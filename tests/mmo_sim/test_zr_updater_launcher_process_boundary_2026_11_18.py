#!/usr/bin/env python3
"""tests/mmo_sim/test_zr_updater_launcher_process_boundary_2026_11_18.py —
ZR-ALTAIR-UPDATER-SPIELTEST-20261118-r2, Abnahme-Matrix-Zeile "Git-Update"
und "Neustart/Abbruch" aus 02_UPDATE_VERHALTEN_UND_ABNAHME.md.

Standalone Assert-Skript (python3 -m unittest -q findet die Modulfunktionen
NICHT, s. unten) -- analog zur bestehenden Konvention der datierten
tests/mmo_sim/test_*_2026_*.py-Dateien (z.B. test_f1_venv_bootstrap_
2026_11_09.py), additiv in scripts/smoke.sh verankert.

Treibt den TATSÄCHLICHEN normalen Starter `scripts/zeitriss.py` als echten
Kindprozess, piped stdin/stdout -- NICHT nur die isolierten `launcher_
update`-Helfer (die hat scripts/tests/test_launcher_update.py bereits
voll abgedeckt). Das beweist hier zusätzlich:
  - Menüintegration: `[4] Nach Updates suchen` ist im echten Menü des
    echten Launcher-Prozesses erreichbar und löst den echten Ablauf aus.
  - Ein echter lokaler Git-Remote-Fixture (Dateisystem-Transport, kein
    Netz) wird per `git fetch`/`git merge --ff-only` wirklich gezogen.
  - Echter Neustart (U6): `os.execv` ersetzt den Prozess durch den echten
    `scripts/zeitriss.py`-Einstieg -- das BEWEIST sich dadurch, dass die
    zweite Banner-Zeile die NEUE `setup.json`-Version zeigt, obwohl
    derselbe Kindprozess (dieselben stdio-Pipes) weiterläuft.
  - U5: nach dem Neustart bleibt der Sync-Status "offen" sichtbar (kein
    OpenWebUI-Key in der isolierten Testumgebung) -- ein erneuter Check
    zeigt das weiterhin, statt es durch "Aktuell" zu verdecken.

Die Fixture-"Produktdateien" sind eine Kopie des ECHTEN `scripts/`-Baums
dieses Checkouts (inkl. der hier neu hinzugefügten `launcher_update.py`)
plus der echten `setup.json` -- der getestete Mechanismus ist also der
reale Code dieses Diffs, nur der Trigger-Commit (ein Versions-Marker in
`setup.json`) ist eine Testfixture, kein echtes Upstream-Repo. Kein echtes
Netz, kein echtes OpenWebUI-/Modell-Backend (fehlender API-Key ist hier
Testabsicht, nicht ein Fehler)."""
from __future__ import annotations

import json
import os
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_REAL_SCRIPTS = _REPO_ROOT / "scripts"
_REAL_SETUP_JSON = _REPO_ROOT / "setup.json"


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=check)


def _build_fixture_tree(dest: Path) -> None:
    shutil.copytree(_REAL_SCRIPTS, dest / "scripts", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy2(_REAL_SETUP_JSON, dest / "setup.json")


def _init_repo(path: Path) -> None:
    _git(path, "init", "-q", "-b", "main")
    _git(path, "config", "user.email", "test@example.invalid")
    _git(path, "config", "user.name", "Test")


def _commit_all(path: Path, message: str) -> str:
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", message)
    return _git(path, "rev-parse", "HEAD").stdout.strip()


class _InteractiveDriver:
    """Treibt eine interaktive stdin/stdout-CLI SCHRITTWEISE: schickt eine
    Eingabezeile erst, NACHDEM die erwartete Prompt-Teilzeichenkette (mit
    gewünschter Mindest-Vorkommenszahl) tatsächlich im bisher gelesenen
    Output erschienen ist.

    Notwendig, weil `os.execv` (echter Neustart, U6) den Prozess MITTEN im
    Lauf ersetzt: ein naives `subprocess.run(input=kompletter_text)` schreibt
    ALLE Zeilen sofort in die Pipe — Pythons stdin-Puffer im ALTEN Prozess
    liest dabei oft mehr als eine Zeile auf einmal voraus (readahead); die
    noch ungelesenen, bereits gepufferten Bytes gehen beim `execv`-Wechsel
    verloren (der neue Prozess startet mit einem frischen, leeren Puffer,
    aber die Pipe-Leseposition ist schon vorgerückt). Schrittweises Senden
    nach bestätigtem Prompt stellt sicher, dass im Moment des Neustarts
    NICHTS Ungelesenes mehr in der Pipe liegt."""

    def __init__(self, proc: subprocess.Popen, overall_timeout: float = 45.0):
        self.proc = proc
        self.output = ""
        self.overall_timeout = overall_timeout
        self.sel = selectors.DefaultSelector()
        self.sel.register(proc.stdout, selectors.EVENT_READ)
        self._start = time.monotonic()

    def _pump(self) -> bool:
        """Liest, was gerade verfügbar ist. True, wenn etwas gelesen wurde."""
        events = self.sel.select(timeout=0.5)
        if not events:
            return False
        chunk = os.read(self.proc.stdout.fileno(), 65536)
        if not chunk:
            return False
        self.output += chunk.decode("utf-8", errors="replace")
        return True

    def wait_for(self, substring: str, count: int = 1) -> None:
        while self.output.count(substring) < count:
            if time.monotonic() - self._start > self.overall_timeout:
                raise TimeoutError(f"Timeout wartend auf {substring!r} (x{count}). Bisher:\n{self.output}")
            if not self._pump():
                if self.proc.poll() is not None:
                    raise RuntimeError(
                        f"Prozess endete vorzeitig (exit {self.proc.returncode}) vor {substring!r}. "
                        f"Bisher:\n{self.output}"
                    )

    def send(self, line: str) -> None:
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def drain_until_exit(self, timeout: float = 15.0) -> int:
        deadline = time.monotonic() + timeout
        while self.proc.poll() is None and time.monotonic() < deadline:
            self._pump()
        # letzte Reste nach Prozessende noch abholen.
        try:
            while self._pump():
                pass
        except OSError:
            pass
        return self.proc.wait(timeout=5)


def _spawn_launcher(install_dir: Path, isolated_home: Path) -> subprocess.Popen:
    env = dict(os.environ)
    env["HOME"] = str(isolated_home)
    env["ZEITRISS_SKIP_VENV_BOOTSTRAP"] = "1"
    env["NO_COLOR"] = "1"
    env["LANG"] = "C.UTF-8"
    env["LC_ALL"] = "C.UTF-8"
    # Keine echten Keys in der isolierten Testumgebung -- bewusst, s. Docstring.
    env.pop("OPENWEBUI_API_KEY", None)
    env.pop("OPENROUTER_API_KEY", None)
    return subprocess.Popen(
        [sys.executable, str(install_dir / "scripts" / "zeitriss.py")],
        cwd=str(install_dir), env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
    )


def test_real_git_update_restart_and_sync_pending_survives_check() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="zr-updater-process-boundary-"))
    try:
        fixture_repo = tmp / "fixture_repo"
        install_dir = tmp / "install"
        isolated_home = tmp / "home"
        isolated_home.mkdir()

        _build_fixture_tree(fixture_repo)
        _init_repo(fixture_repo)
        old_cfg = json.loads(_REAL_SETUP_JSON.read_text("utf-8"))
        old_version = old_cfg["version"]
        base_rev = _commit_all(fixture_repo, "base (candidate code snapshot)")

        # Clone VOR dem Marker-Fortschritt -- install_dir bleibt auf `base_rev`
        # stehen, waehrend `fixture_repo` (der "Remote") danach weiterzieht.
        _git(tmp, "clone", "-q", str(fixture_repo), str(install_dir))
        _git(install_dir, "config", "user.email", "test@example.invalid")
        _git(install_dir, "config", "user.name", "Test")

        new_version = old_version + "+fixturetest-new"
        cfg_path = fixture_repo / "setup.json"
        cfg = json.loads(cfg_path.read_text("utf-8"))
        cfg["version"] = new_version
        cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        new_rev = _commit_all(fixture_repo, "advance (upstream has a new commit)")
        assert new_rev != base_rev

        assert _git(install_dir, "rev-parse", "HEAD").stdout.strip() == base_rev

        # Gesteuerte Eingabesequenz -- JEDE Zeile wird erst geschickt, nachdem
        # der jeweils vorherige Prompt tatsaechlich im Output erschienen ist
        # (s. `_InteractiveDriver`-Docstring fuer den execv-Grund):
        #   [Auswahl 1x]            -> 4   (Menue [4] Nach Updates suchen, 1. Prozess)
        #   [Jetzt installieren?]   -> j   (Update verfuegbar)
        #   [Jetzt neu starten?]    -> j   (-> os.execv -> 2. Prozess)
        #   [Auswahl 2x]            -> 4   (Menue [4] erneut, NACH echtem Neustart)
        #   [Jetzt synchronisieren?]-> n   (ablehnen -- Key fehlt eh)
        #   [Weiter mit Enter]      -> ''  (Pause bestaetigen)
        #   [Auswahl 3x]            -> x   (Beenden)
        proc = _spawn_launcher(install_dir, isolated_home)
        driver = _InteractiveDriver(proc)
        try:
            driver.wait_for("Auswahl:", 1)
            driver.send("4")
            driver.wait_for("Jetzt installieren?")
            driver.send("j")
            driver.wait_for("Jetzt neu starten?")
            driver.send("j")
            driver.wait_for("Auswahl:", 2)
            driver.send("4")
            driver.wait_for("Jetzt synchronisieren?")
            driver.send("n")
            driver.wait_for("Weiter mit Enter")
            driver.send("")
            driver.wait_for("Auswahl:", 3)
            driver.send("x")
            returncode = driver.drain_until_exit()
        except (TimeoutError, RuntimeError):
            proc.kill()
            sys.stderr.write(driver.output)
            raise

        out = driver.output
        if returncode != 0:
            sys.stderr.write(out)
        assert returncode == 0, f"Launcher-Prozess endete mit Exitcode {returncode}"

        banner_count = out.count("Launcher (Setup + Betrieb)")
        assert banner_count >= 2, f"Erwarte mindestens 2 Banner-Renderings (vor/nach Neustart), sah {banner_count}"

        first_banner_end = out.index("Launcher (Setup + Betrieb)")
        assert f"Version {old_version}" in out[:first_banner_end + 2000], (
            "Erster Banner zeigt nicht den ALTEN Versionsstand"
        )

        assert "Update verfügbar" in out, "Update-Check hat kein 'Update verfügbar' gemeldet"
        assert "Repo auf die geprüfte Zielrevision aktualisiert." in out, (
            "Echter git fast-forward (perform_git_update) ist nicht sichtbar gelaufen"
        )
        assert "OPENWEBUI_API_KEY fehlt — Sync übersprungen." in out, (
            "Sync-Schritt sollte wegen fehlendem Key sichtbar ausgelassen worden sein"
        )
        assert "Update installiert. Bitte den Launcher neu starten." in out

        second_banner_start = out.index("Launcher (Setup + Betrieb)", first_banner_end + 1)
        tail_after_restart = out[second_banner_start:]
        assert f"Version {new_version}" in tail_after_restart[:2000], (
            "Zweiter Banner (nach echtem Neustart) zeigt nicht den NEUEN Versionsstand -- "
            "kein echter Prozesswechsel nachweisbar"
        )

        # U5: Sync blieb offen (kein Key) -- ein erneuter Check nach dem
        # Neustart darf das NICHT als blankes 'Aktuell' verdecken.
        assert "die Synchronisierung mit OpenWebUI ist aber" in tail_after_restart
        assert "noch offen" in tail_after_restart
        assert "Übersprungen — bleibt offen, ein erneuter Check verdeckt das nicht als 'Aktuell'." in tail_after_restart

        # Farewell am echten Ende -- belegt den normalen, kontrollierten Ausstieg.
        assert "Bis bald, Chrononaut." in tail_after_restart

        # Dateisystem-Wahrheit, unabhaengig vom stdout-Text:
        final_head = _git(install_dir, "rev-parse", "HEAD").stdout.strip()
        assert final_head == new_rev, f"install_dir sollte auf {new_rev} stehen, ist aber {final_head}"
        on_disk_version = json.loads((install_dir / "setup.json").read_text("utf-8"))["version"]
        assert on_disk_version == new_version

        state = json.loads((install_dir / ".zeitriss-update-state.json").read_text("utf-8"))
        assert state["method"] == "git"
        assert state["installed_rev"] == new_rev
        assert state["sync_status"] in ("pending", "failed"), (
            "Sync-Status sollte sichtbar offen/gescheitert sein (kein Key), nicht 'ok'"
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
