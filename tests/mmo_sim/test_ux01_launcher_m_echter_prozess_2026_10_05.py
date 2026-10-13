#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux01_launcher_m_echter_prozess_2026_10_05.py — W15/
C4-MUSS#1: echter Launcher-`[M]`-Prozessbeleg (UX01, bisher
`NOT_INDEPENDENTLY_COMPLETED`, s. `runs/C4/report/CRITIC-URTEIL-C4.md`
MUSS #1).

Startet den ECHTEN `scripts/launcher.py` als FRISCHEN, eigenstaendigen
Python-Subprozess (kein In-Prozess-Import, kein Mock/Stub des Launcher-
oder Hook-Codes), waehlt am Launcher-Hauptmenue `[M]` (lokale Terminal-
Route) und belegt, dass dieser Pfad real bis in das `mmo_sim`-Terminal-
Hauptmenue fuehrt -- OHNE technischen Produktwechsel (derselbe Prozess,
derselbe Python-Interpreter, kein Exec in ein anderes Programm) und OHNE
die Browserroute ([3]/`action_play`) umzubiegen (`[M]` dispatcht laut
`scripts/launcher.py:main()` direkt auf `project_hook.launch()`, NIE auf
`action_play()` -- code-gelesen, s. Docstring unten).

Importwurzel+SHA-Bindung (Fehlbindung=INVALID_TEST): dieser Test bindet
sich beim Start an die VIER realen Quelldateien, die den `[M]`-Pfad
bilden (`scripts/launcher.py`, `scripts/mmo_sim_launcher_hook.py`,
`scripts/mmo_sim.py`, `mmo_sim/ui/tui.py`) UNTER DIESEM Testbaum
(`Path(__file__).resolve().parents[1]`). Fehlen sie, bricht der Test
SOFORT mit `InvalidTestBindingError` (eigener Exitcode 2, siehe `main()`)
ab -- niemals als normale Testassertion (FAIL) getarnt. Weil der echte
`[M]`-Hook (`mmo_sim_launcher_hook.launch()`) `scripts/mmo_sim.py` IMMER
mit dem PRODUKT-Default-Datenverzeichnis (`<Repo-Root>/internal/
mmo_sim_data`, hartkodiert, kein CLI-/Env-Override im echten Hook-Pfad)
startet, laeuft der Subprozess gegen eine EXKLUSIVE, temporaere Kopie
dieses gesamten Quellbaums (nicht gegen den ausgelieferten `workdir`
selbst) -- sonst wuerde dieser Testlauf das Lieferverzeichnis mit
generierten Laufzeitdateien verschmutzen, obwohl dieser W-Lauf laut
Auftrag NUR MUSS#1+MUSS#4 beruehren darf. Nach dem Kopieren wird JEDE der
vier gebundenen Dateien erneut per SHA256 gegen das Original verglichen
(zweite Fehlbindungspruefung) -- die Kopie ist bytegleich zur echten
Importwurzel, kein Stub/keine Patchversion.

Testumgebung: frisches leeres `HOME`/`XDG_*` (kein echtes Nutzer-HOME,
keine echten Keys), eine knappe Env-Allowlist (kein Vererben von Dev-
Session-/Token-/Proxy-Variablen), `PATH` auf ein garantiert leeres
Verzeichnis gesetzt (`shutil.which("docker")`/`shutil.which("xdg-open")`
liefern im Kind zuverlaessig `None` -- belegt den Child-Lock: der echte
Statusblock faellt dadurch control­liert auf "nicht installiert" zurueck,
STATT einen echten `docker ps`-Kindprozess zu starten) und
`OPENWEBUI_URL` auf einen garantiert geschlossenen lokalen Port (127.0.0.1:1)
gesetzt (belegt den Netz-Lock: der Status-Check schlaegt schnell und
lokal fehl, kein echter Netzwerkzugriff). Die Eingabesequenz waehlt NUR
`[M]` dann sofort `x`/`x` (Spiel-TUI verlassen, Launcher verlassen) --
KEIN Zug, KEIN GM-/Persona-Call, reine Routenpruefung bis ins
Hauptmenue (kein Live-Modellcall, exakt wie vom Auftrag verlangt).

Ehrliche Grenze (im W-REPORT.md ausgewiesen, hier nur referenziert):
dieser Test kann NICHT beweisen, dass auf einem echten Desktop tatsaechlich
ein Browserfenster erscheint ODER ausbleibt (`webbrowser.open`/`xdg-open`
sind OS-/Display-abhaengig und in einer Offline-/Headless-Sandbox nicht
pruefbar) -- er beweist stattdessen STRUKTURELL + schwarzkistig, dass die
`[M]`-Auswahl NIE den Browser-Code-Pfad (`action_play`/`_open_browser`)
durchlaeuft (Code gelesen: `main()`s `elif choice == "m"`-Zweig ruft
ausschliesslich `project_hook.launch()`) und dass in der tatsaechlichen
Prozessausgabe keine Browser-Oeffnen-Zeile erscheint."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import _h02_vollreise_support as _h02sup  # noqa: E402 -- Sichtbarkeitsmuster wiederverwendet (copy_dependency_visibility)

_LAUNCHER = _REPO_ROOT / "scripts" / "launcher.py"
_HOOK = _REPO_ROOT / "scripts" / "mmo_sim_launcher_hook.py"
_MMO_SIM_ENTRY = _REPO_ROOT / "scripts" / "mmo_sim.py"
_TUI = _REPO_ROOT / "mmo_sim" / "ui" / "tui.py"
_SETUP_JSON = _REPO_ROOT / "setup.json"
_BOUND_FILES = (_LAUNCHER, _HOOK, _MMO_SIM_ENTRY, _TUI, _SETUP_JSON)

# Knappe, dokumentierte Allowlist (analog `_h02_vollreise_support.
# _INHERITED_ENV_ALLOWLIST`) -- kein unbesehenes `dict(os.environ)`.
_INHERITED_ENV_ALLOWLIST = ("LANG", "LC_ALL", "TERM")

_IGNORE_DIRS = {"__pycache__", "out", "internal"}


class InvalidTestBindingError(RuntimeError):
    """Fehlbindung ans Importwurzel/SHA-Paar -- NIE eine normale
    Testassertion. Eigener Exitcode (s. `main()`), damit ein fehlendes/
    verschobenes Produktmodul nicht wie ein echter Produktfehler aussieht."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bind_import_root() -> dict[str, str]:
    """Bindet diesen Test an die vier realen `[M]`-Quelldateien unter der
    EIGENEN Importwurzel (`_REPO_ROOT`). Fehlt eine, ist das eine
    Fehlbindung (falscher Testbaum/verschobene Datei), kein PASS/FAIL."""
    missing = [str(p) for p in _BOUND_FILES if not p.is_file()]
    if missing:
        raise InvalidTestBindingError(
            "Importwurzel-Fehlbindung: folgende gebundene Dateien fehlen unter "
            f"{_REPO_ROOT}: {missing}"
        )
    return {str(p.relative_to(_REPO_ROOT)): _sha256(p) for p in _BOUND_FILES}


def _copy_source_tree(dest: Path) -> None:
    """Exklusive Scratch-Kopie des GESAMTEN Quellbaums (ohne `internal/`,
    `__pycache__`, `out/`) -- der echte `[M]`-Hook kennt keinen Daten-
    verzeichnis-Override, daher muss die gesamte Importwurzel verschoben
    werden, nicht nur `scripts/`+`mmo_sim/`. `internal/qa` (Fixtures) wird
    bewusst NICHT mitkopiert: fehlt `internal/qa/fixtures/persona-state.
    schema.json`, setzt `scripts/mmo_sim.py:main()` `schema_path=None`
    (code gelesen, `if schema_path.is_file() else None`) -- reiner
    Lesecheck, kein Fehler, fuer das Erreichen des Hauptmenues irrelevant."""
    def _ignore(dirpath: str, names: list[str]) -> set[str]:
        return {n for n in names if n in _IGNORE_DIRS}

    shutil.copytree(_REPO_ROOT, dest, ignore=_ignore, dirs_exist_ok=True)


def _verify_copy_matches_bound_sha(dest: Path, bound: dict[str, str]) -> None:
    for rel, sha in bound.items():
        copied = dest / rel
        if not copied.is_file() or _sha256(copied) != sha:
            raise InvalidTestBindingError(
                f"Scratch-Kopie weicht von der Importwurzel ab: {rel} "
                f"(erwartet sha256={sha})"
            )


def _build_isolated_env(tmp_root: Path) -> dict[str, str]:
    """Frisches HOME/XDG, knappe Allowlist, `PATH` garantiert leer (Child-
    Lock-Beleg: kein `docker`/`xdg-open` im Kind auffindbar),
    `OPENWEBUI_URL` auf einen garantiert geschlossenen lokalen Port
    (Netz-Lock-Beleg: Status-Check schlaegt schnell+lokal fehl, kein
    echter Netzzugriff).

    `PYTHONPATH` bindet zusaetzlich eine kuratierte, exklusive
    Sichtbarkeitskopie von `jsonschema`+`referencing` (samt deren reinen
    Pure-Python-Laufzeitabhaengigkeiten `jsonschema_specifications`,
    `attr(s)`, `rpds`) aus dem REALEN `site.getusersitepackages()` dieses
    Hosts ins isolierte Kind -- Muster identisch zu `_h02_vollreise_support.
    copy_dependency_visibility`/`H02_REAL_USER_SITE_PACKAGES` (bereits an
    anderer Stelle geprueft). KEINE Installation, KEIN Durchreichen des
    echten HOME/PATH/geerbter Secrets -- nur diese eine kuratierte
    Scratchkopie wird sichtbar gemacht, weil `mmo_sim/domain/zeitriss/
    save_validation.py` `jsonschema`/`referencing` OHNE optionalen
    Fallback importiert und das frische, leere `HOME` oben
    `site.getusersitepackages()` im Kind sonst unsichtbar macht."""
    home_dir = tmp_root / "home"
    home_dir.mkdir(parents=True, exist_ok=True)
    empty_bin = tmp_root / "empty_bin"
    empty_bin.mkdir(parents=True, exist_ok=True)
    env = {k: os.environ[k] for k in _INHERITED_ENV_ALLOWLIST if k in os.environ}
    env["HOME"] = str(home_dir)
    env["XDG_CONFIG_HOME"] = str(home_dir / ".config")
    env["XDG_DATA_HOME"] = str(home_dir / ".local" / "share")
    env["XDG_CACHE_HOME"] = str(home_dir / ".cache")
    env["PATH"] = str(empty_bin)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["NO_COLOR"] = "1"
    # Garantiert geschlossener lokaler Port (privilegiert, kein echter
    # Dienst) -- der Statuscheck schlaegt schnell+lokal fehl, kein echter
    # Netzwerkzugriff noetig/versucht.
    env["OPENWEBUI_URL"] = "http://127.0.0.1:1"
    vis_dir, manifest = _h02sup.copy_dependency_visibility(tmp_root / "dependency-visibility")
    if vis_dir is not None and manifest:
        env["PYTHONPATH"] = str(vis_dir)
    return env


def _run_launcher(tmp_repo: Path, env: dict[str, str], stdin_text: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(tmp_repo / "scripts" / "launcher.py")]
    return subprocess.run(
        cmd, input=stdin_text, capture_output=True, text=True,
        env=env, cwd=str(tmp_repo), timeout=60,
    )


def test_m_route_reaches_real_mmo_sim_hauptmenue() -> None:
    bound = _bind_import_root()
    with tempfile.TemporaryDirectory(prefix="w15_ux01_launcher_m_") as td:
        tmp_root = Path(td)
        tmp_repo = tmp_root / "repo"
        _copy_source_tree(tmp_repo)
        _verify_copy_matches_bound_sha(tmp_repo, bound)
        env = _build_isolated_env(tmp_root)

        # [M] waehlen -> im echten mmo_sim-Hauptmenue sofort 'x' (Spiel-TUI
        # verlassen) -> zurueck im Launcher-Hauptmenue sofort 'x' (Launcher
        # verlassen). Kein Zug, kein GM-/Persona-Call.
        proc = _run_launcher(tmp_repo, env, "m\nx\nx\n")

        assert proc.returncode == 0, (
            f"Launcher-Prozess (echter Subprozess) endete mit rc={proc.returncode}\n"
            f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
        )
        assert "Traceback" not in proc.stderr, f"Unerwartete Exception im Kind:\n{proc.stderr}"

        out = proc.stdout
        assert "[M]  ZEITRISS MMO-Sim (Terminal, kein Browser)" in out, (
            f"Echter [M]-Menuepunkt wurde nicht angezeigt -- kein echter Routendurchlauf:\n{out}"
        )
        # Der ECHTE mmo_sim-TUI-Hauptmenue-Banner (render_boot_menu in
        # mmo_sim/ui/tui.py) -- kein Attrappentext, kommt NUR, wenn
        # TuiSession.run() tatsaechlich real durchlief.
        assert "ZEITRISS MMO-Sim" in out and "Hauptmenue:" in out, (
            f"Echtes mmo_sim-Terminal-Hauptmenue wurde nicht erreicht:\n{out}"
        )
        assert "[spielen] Spielen" in out, f"mmo_sim-Hauptmenue unvollstaendig/nicht echt:\n{out}"

        # Browserroute NICHT umgebogen: 'm' dispatcht laut Code
        # ausschliesslich auf project_hook.launch(), nie auf action_play().
        assert "Öffne Browser" not in out, (
            f"[M] hat unerwartet die Browserroute ausgeloest:\n{out}"
        )

        # Child-Lock-Beleg: PATH war leer -> Docker-Check findet 'docker'
        # nicht, startet KEINEN echten 'docker ps'-Kindprozess.
        assert "Docker nicht installiert" in out, (
            f"Docker-Statuscheck hat trotz leerem PATH einen echten Kindprozess erwartet:\n{out}"
        )
        # Netz-Lock-Beleg: OPENWEBUI_URL zeigte auf einen garantiert
        # geschlossenen lokalen Port -- Status-Check meldet "nicht
        # erreichbar", kein echter Netzkontakt zustande gekommen.
        assert "nicht erreichbar" in out, (
            f"OpenWebUI-Statuscheck hat trotz geschlossenem Port keinen Fehlschlag gemeldet:\n{out}"
        )

        # Realer Produkt-Seiteneffekt des echten Default-Datenpfads (kein
        # Mock): der [M]-Hook hat tatsaechlich `scripts/mmo_sim.py` mit dem
        # Produkt-Default-Datenverzeichnis ausgefuehrt.
        data_dir = tmp_repo / "internal" / "mmo_sim_data"
        marker = data_dir / "last_participant.json"
        assert marker.is_file(), (
            f"Echter [M]-Lauf haette den Produkt-Default-Datenpfad ({data_dir}) real "
            "anlegen muessen -- Hinweis auf einen nicht-echten/umgeleiteten Lauf."
        )
        participant_id = json.loads(marker.read_text(encoding="utf-8"))["participant_id"]
        assert participant_id, "last_participant.json ohne participant_id -- kein echter Teilnehmerlauf"


def test_without_m_choice_no_mmo_sim_menu_appears() -> None:
    """Negativkontrolle: OHNE `[M]`-Auswahl (nur sofort `x` am Launcher-
    Hauptmenue) darf das echte mmo_sim-Terminal-Hauptmenue NICHT erscheinen
    -- belegt, dass der positive Befund oben tatsaechlich an die `[M]`-
    Auswahl gebunden ist, nicht an einen immer gleichen Textblock."""
    bound = _bind_import_root()
    with tempfile.TemporaryDirectory(prefix="w15_ux01_launcher_control_") as td:
        tmp_root = Path(td)
        tmp_repo = tmp_root / "repo"
        _copy_source_tree(tmp_repo)
        _verify_copy_matches_bound_sha(tmp_repo, bound)
        env = _build_isolated_env(tmp_root)

        proc = _run_launcher(tmp_repo, env, "x\n")
        assert proc.returncode == 0, (
            f"Launcher-Kontrolllauf (nur 'x') endete mit rc={proc.returncode}\n{proc.stderr}"
        )
        assert "Hauptmenue:" not in proc.stdout, (
            f"mmo_sim-Hauptmenue erschien OHNE [M]-Auswahl -- Befund oben waere nicht aussagekraeftig:\n{proc.stdout}"
        )
        data_dir = tmp_repo / "internal" / "mmo_sim_data"
        assert not data_dir.exists(), (
            f"Ohne [M]-Auswahl haette der Produkt-Default-Datenpfad nicht angelegt werden duerfen: {data_dir}"
        )


def main() -> int:
    tests = (test_m_route_reaches_real_mmo_sim_hauptmenue, test_without_m_choice_no_mmo_sim_menu_appears)
    for t in tests:
        t()
        print(f"OK: {t.__name__}")
    print("=== UX01 echter Launcher-[M]-Prozessbeleg: PASS (offline-beweisbarer Teil) ===")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except InvalidTestBindingError as exc:
        print(f"INVALID_TEST: {exc}", file=sys.stderr)
        rc = 2
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        rc = 1
    except Exception:
        import traceback
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
