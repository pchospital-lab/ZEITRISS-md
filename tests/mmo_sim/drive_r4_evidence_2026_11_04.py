#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r4_evidence_2026_11_04.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261104-R4 (02_NACHWEISE_UND_RUECKGABE.md §2): vier
Beweisfamilien T1-T4, die -- anders als `drive_r3_g5_evidence_2026_11_04.py`
(R3-N1-Luecke: Sessions direkt konstruiert statt den echten Launcher zu
nutzen) -- T1/T3/T4 AUSSCHLIESSLICH ueber den ECHTEN Launcher-Subprozess
(`scripts/mmo_sim.py`, literal `--operator-control-fifo`/`--guest-terminal`/
`--no-host-capable`/getrennte Wurzeln) fahren. Der Anbieter-GM ist eine
Grenzinjektion ueber FIX5 (`MMO_SIM_GM_TRANSPORT_DOUBLE`,
`mmo_sim/adapters/factories.py`) -- NIE ein Live-Modelllauf, in jeder
Laufspur als solche ausgewiesen (s. `tests/mmo_sim/_r4_gm_double.py`).

LITERAL ARGV (R3-§6-Luecke): KEIN `-c`-Platzhalter. Jeder Subprozess ist
entweder der woertliche `scripts/mmo_sim.py`-Einstiegspunkt ODER eine
gebundene Skriptdatei (`_r4_launcher_hardexit_*.py`), die `scripts.mmo_sim`
importiert (nicht nachbaut) und `sys.argv[1:]` UNVERAENDERT an
`launcher.main()` durchreicht.

GEFIXTER PRODUKTDEFEKT, R4 FIX6 (ZR-BETREIBER-GASTERSCHAFFUNG-20261104-R4):
`guest_session.run()` (FIX1, eigener Thread je `--guest-terminal`) und die
`_HumanDriver`-Rundenantwort (ueber `register_guest_terminal`, laeuft im
BETREIBER-Thread) lesen DIESELBE `in_fifo`-Datei. Ohne Koordination
konkurrierten beide Leser frueher um die naechste FIFO-Zeile -- eine direkt
gesendete Rundenantwort konnte als 'Unbekannte Auswahl' im Top-Menue-
Dispatch landen (empirisch verifiziert VOR FIX6). FIX6 (`mmo_sim/ui/
tui.py:TuiSession._host_terminal_claimed`/`_readline_guest_menu`,
`_HumanDriver.decide`) macht den Menue-Loop zum Einzelleser-Koordinator:
waehrend ein host-getriebener Round-/Dialog-Read fuer dieses Gast-Terminal
aktiv ist (Claim gesetzt), parkt der Menue-Loop GETIMED statt zu
konsumieren. Dieser Treiber sendet jede echte Rundenantwort/Reflexion
DIREKT (`_deliver_guest_turn_answer()`, KEINE Leerzeile/kein Drain-
Workaround mehr) -- die nachfolgenden `_wait_for_marker`/`_wait_for_path`-
Aufrufe UND die expliziten "Unbekannte Auswahl"-Abwesenheitschecks an den
Aufrufstellen sind der echte Beleg, dass FIX6 wirkt.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import select
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.core.table_admission as table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import creation_service as creation_grants  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_RESULTS_ROOT = Path("/home/altair/zr-betreiber-gast-20261103/run/r4/results")
_LAUNCHER = _REPO_ROOT / "scripts" / "mmo_sim.py"
_HARDEXIT_BEFORE_REFLECTION = _HERE / "_r4_launcher_hardexit_before_reflection.py"
_HARDEXIT_BETWEEN_PUBLICATION = _HERE / "_r4_launcher_hardexit_between_publication.py"
_J4_TOLERATED_FIXTURE = _HERE / "fixtures" / "j4_tolerant_import" / "p01_latch.json"
_GM_DOUBLE_SPEC = "tests.mmo_sim._r4_gm_double:build"

_MANIFEST: dict = {"files": [], "runs": []}


# ───────────────────────── gemeinsame Helfer (wie R3) ─────────────────────

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _export_file(szene: str, src: Path, rel: str) -> None:
    dest = _RESULTS_ROOT / szene / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    _MANIFEST["files"].append({
        "path": str(dest.relative_to(_RESULTS_ROOT)), "sha256": _sha256(dest), "bytes": dest.stat().st_size,
    })


def _export_tree(szene: str, src_root: Path, rel_root: str) -> None:
    if not src_root.exists():
        return
    for p in sorted(src_root.rglob("*")):
        if p.is_file():
            rel = str(Path(rel_root) / p.relative_to(src_root))
            _export_file(szene, p, rel)


def _write_export_json(szene: str, rel: str, data: object) -> None:
    dest = _RESULTS_ROOT / szene / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    _MANIFEST["files"].append({
        "path": str(dest.relative_to(_RESULTS_ROOT)), "sha256": _sha256(dest), "bytes": dest.stat().st_size,
    })


def _clean_env(extra: dict | None = None) -> dict:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    # KEIN NETZ: jede echte SL-/Persona-Anbindung bleibt deaktiviert; der
    # einzige GM-Weg ist FIX5s Double (MMO_SIM_GM_TRANSPORT_DOUBLE unten).
    env.pop("OPENWEBUI_API_KEY", None)
    env.pop("MMO_SIM_PERSONA_CLI", None)
    env.pop("MMO_SIM_PERSONA_API_BASE_URL", None)
    if extra:
        env.update(extra)
    return env


def _run_real_subprocess(szene: str, label: str, argv: list[str], **kw) -> subprocess.CompletedProcess:
    cwd = kw.pop("cwd", None)
    timeout = kw.pop("timeout", 60)
    utc_start = _utc(time.time())
    result = subprocess.run(argv, capture_output=True, text=True, cwd=cwd, timeout=timeout, **kw)
    utc_end = _utc(time.time())
    out_dir = _RESULTS_ROOT / szene
    out_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = out_dir / f"{label}.stdout.txt"
    stderr_path = out_dir / f"{label}.stderr.txt"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    for p in (stdout_path, stderr_path):
        _MANIFEST["files"].append({
            "path": str(p.relative_to(_RESULTS_ROOT)), "sha256": _sha256(p), "bytes": p.stat().st_size,
        })
    _MANIFEST["runs"].append({
        "szene": szene, "label": label, "argv": argv, "cwd": str(cwd) if cwd else None,
        "utc_start": utc_start, "utc_end": utc_end, "exit": result.returncode,
        "stdout_path": str(stdout_path.relative_to(_RESULTS_ROOT)),
        "stderr_path": str(stderr_path.relative_to(_RESULTS_ROOT)),
    })
    return result


def _record_background_run(
    szene: str, label: str, argv: list[str], cwd, utc_start: str, utc_end: str,
    exit_code: int, stdout_text: str, stderr_text: str,
) -> None:
    out_dir = _RESULTS_ROOT / szene
    out_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = out_dir / f"{label}.stdout.txt"
    stderr_path = out_dir / f"{label}.stderr.txt"
    stdout_path.write_text(stdout_text, encoding="utf-8")
    stderr_path.write_text(stderr_text, encoding="utf-8")
    for p in (stdout_path, stderr_path):
        _MANIFEST["files"].append({
            "path": str(p.relative_to(_RESULTS_ROOT)), "sha256": _sha256(p), "bytes": p.stat().st_size,
        })
    _MANIFEST["runs"].append({
        "szene": szene, "label": label, "argv": argv, "cwd": str(cwd) if cwd else None,
        "utc_start": utc_start, "utc_end": utc_end, "exit": exit_code,
        "stdout_path": str(stdout_path.relative_to(_RESULTS_ROOT)),
        "stderr_path": str(stderr_path.relative_to(_RESULTS_ROOT)),
    })


# ───────────────────────── FIFO-/Prozessinteraktions-Helfer ────────────────

class _LineReader:
    """Liest Zeilen aus einem rohen FIFO-Dateideskriptor OHNE versteckte
    `TextIOWrapper`-Pufferung.

    GEFUNDENE TREIBER-EIGENSCHAFT (eigener Testharness-Bug, empirisch per
    `strace`/Timestamp-Log verifiziert, KEIN Produktfehler): `os.fdopen(fd,
    "r")` + `select.select([f], ...)` + `f.readline()` liest gelegentlich
    einen GROSSEN Schub bereits verfuegbarer Bytes (mehrere Zeilen) in EINEM
    internen `BufferedReader`-Lesevorgang, gibt aber nur die ERSTE Zeile
    zurueck -- die RESTLICHEN Zeilen liegen danach NUR NOCH im PRIVATEN
    Python-Puffer dieses `TextIOWrapper`-Objekts, NICHT mehr im Kernel-
    Pipe-Puffer. `select.select` prueft aber den rohen Kernel-Deskriptor --
    es meldet 'nicht bereit', obwohl `readline()` trotzdem sofort eine
    weitere Zeile liefern wuerde. Das fuehrte zu einem echten Haenger (die
    Restzeilen kamen NIE an, obwohl der Subprozess sie laengst geschrieben
    hatte und sauber beendete). Diese Klasse umgeht das: `os.read(fd, N)`
    OHNE jede Python-Pufferung, eigenes Zeilen-Splitting -- `pop_line()`
    liefert zuerst alles, was bereits im EIGENEN (jetzt transparenten)
    Puffer liegt, BEVOR ueberhaupt erneut `select`/`os.read` bemueht wird."""

    def __init__(self, fd: int):
        self.fd = fd
        self._buf = ""
        self.eof = False

    def fileno(self) -> int:
        return self.fd

    def pop_line(self) -> str | None:
        idx = self._buf.find("\n")
        if idx == -1:
            return None
        line = self._buf[: idx + 1]
        self._buf = self._buf[idx + 1:]
        return line

    def pump(self, max_bytes: int = 65536) -> bool:
        """EIN `os.read()` -- Aufrufer MUSS vorher per `select.select`
        echte Lesebereitschaft bestaetigt haben. `False` bei EOF."""
        chunk = os.read(self.fd, max_bytes)
        if chunk == b"":
            self.eof = True
            return False
        self._buf += chunk.decode("utf-8", errors="replace")
        return True

    def close(self) -> None:
        os.close(self.fd)


def _drain(reader: "_LineReader", settle: float = 0.4, overall: float = 10.0) -> list[str]:
    """Liest alle gerade verfuegbaren Zeilen, bis `settle` Sekunden lang
    nichts Neues mehr ankommt (oder Timeout) -- wie R3s `_drain_lines`."""
    lines: list[str] = []
    deadline = time.time() + overall
    last_data_at = None
    while time.time() < deadline:
        line = reader.pop_line()
        if line is not None:
            lines.append(line)
            last_data_at = time.time()
            continue
        ready, _, _ = select.select([reader], [], [], 0.1)
        if ready:
            if not reader.pump():
                break
        elif last_data_at is not None and time.time() - last_data_at > settle:
            break
    return lines


def _wait_for_marker(reader: "_LineReader", marker: str, overall: float = 20.0) -> list[str]:
    collected: list[str] = []
    deadline = time.time() + overall
    while time.time() < deadline:
        line = reader.pop_line()
        if line is not None:
            collected.append(line)
            if marker in line:
                return collected
            continue
        ready, _, _ = select.select([reader], [], [], 0.1)
        if ready:
            if not reader.pump():
                raise AssertionError(
                    f"Marker {marker!r} nicht gesehen (EOF); gesammelt={collected}"
                )
    raise AssertionError(f"Marker {marker!r} nicht gesehen; gesammelt={collected}")


def _wait_for_path(path: Path, overall: float = 20.0) -> None:
    deadline = time.time() + overall
    while time.time() < deadline:
        if path.exists():
            return
        time.sleep(0.02)
    raise AssertionError(f"Pfad {path} ist nicht rechtzeitig entstanden.")


def _open_guest_fifo_pair(in_fifo: Path, out_fifo: Path):
    """`O_NONBLOCK` NUR fuer den `open()`-Syscall selbst (verhindert
    Blockieren, falls der Subprozess seine Schreibseite noch nicht
    geoeffnet hat) -- danach den Nonblocking-Modus per `fcntl` WIEDER
    entfernen (die rohen `os.read()`-Aufrufe in `_LineReader.pump()` laufen
    IMMER erst nach einem positiven `select`, ein bleibend nonblocking FD
    ist hier ohne Nutzen)."""
    _wait_for_path(in_fifo)
    _wait_for_path(out_fifo)
    out_fd = os.open(str(out_fifo), os.O_RDONLY | os.O_NONBLOCK)
    flags = fcntl.fcntl(out_fd, fcntl.F_GETFL)
    fcntl.fcntl(out_fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
    out_reader = _LineReader(out_fd)
    in_fd = os.open(str(in_fifo), os.O_WRONLY)
    in_f = os.fdopen(in_fd, "w")
    return in_f, out_reader


def _send_op(proc: subprocess.Popen, line: str) -> None:
    proc.stdin.write(line + "\n")
    proc.stdin.flush()


def _send_guest(in_f, line: str) -> None:
    in_f.write(line + "\n")
    in_f.flush()


def _deliver_guest_turn_answer(in_f, out_f, answer: str) -> None:
    """R4 FIX6 (s. Moduldocstring): sendet die ECHTE Rundenantwort/
    Reflexion DIREKT -- KEIN Leerzeilen-/Drain-Workaround mehr (FIX6 im
    Produkt macht den Menue-Loop zum Einzelleser-Koordinator, s. `mmo_sim/
    ui/tui.py:TuiSession._readline_guest_menu`/`_host_terminal_claimed`).
    `out_f` bleibt Parameter fuer Aufrufstellen-Symmetrie (ungenutzt hier --
    der Nachweis, dass die Antwort den Round-Reader statt des Menue-
    Dispatchs erreicht, liegt bei den `_wait_for_marker`/`_wait_for_path`-
    Aufrufen UND den expliziten "Unbekannte Auswahl"-Checks an den
    Aufrufstellen). Caller MUSS vorher per `_wait_for_marker` den
    Rundenprompt bestaetigt haben."""
    _send_guest(in_f, answer)


def _write_gm_double_config(
    path: Path, *, responses: list[str], calls_log: Path, stop: dict | None = None,
) -> None:
    cfg = {"responses": list(responses), "calls_log": str(calls_log), "stop": stop}
    path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")


def _gm_double_env(config_path: Path, extra: dict | None = None) -> dict:
    return _clean_env({
        "MMO_SIM_GM_TRANSPORT_DOUBLE": _GM_DOUBLE_SPEC,
        "MMO_SIM_R4_GMDOUBLE_CONFIG": str(config_path),
        **(extra or {}),
    })


def _seed_guest_figure(onboarding_dir: Path, catalog_dir: Path, guest_id: str, char_id: str, save_id: str) -> dict:
    start_save = full_v7_save(char_id, name=f"Gast-{guest_id}", save_id=save_id)
    onboarding.start_or_resume(onboarding_dir, guest_id)
    onboarding.complete_with_save(onboarding_dir, guest_id, start_save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=guest_id, chrononaut_id=char_id, persona_key=guest_id,
    ))
    catalog.store_figure_save(catalog_dir, guest_id, char_id, start_save)
    return start_save


# ───────────────────────── Familie T1 ─────────────────────────
# G1/G5, O1-O3/O6 (02 §2 T1): normaler Betreibertisch (Betreiber OHNE
# Figur, Gast MIT persoenlicher Originaldatei) ueber den ECHTEN
# Launcher-Subprozess; Stop gewinnt vor der dauerhaften Planannahme.

def run_family_t1() -> None:
    szene = "t1"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo = fifo_dir / "guest_in.fifo"
        out_fifo = fifo_dir / "guest_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)

        # Echte persoenliche Gast-Originaldatei -- unter der vom LAUNCHER
        # selbst verwendeten Konvention (`--data-dir`/guests/<id>/...),
        # NICHT einer treiber-erfundenen Sonderwurzel.
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        char_id = "chrono-t1-guest"
        _seed_guest_figure(guest_onboarding, guest_catalog, "guest1", char_id, "fixture-t1-guest-001")
        guest_figure_path = guest_catalog / "figures" / f"guest1__{char_id}.json"
        # T1-Messgrenze (R3-N1-Fix): Originaldatei VOR dem ersten Request
        # gesichert -- NICHT nach dem Abbruch gemessen.
        sha_guest_original_before_request = _sha256(guest_figure_path)

        _write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker."], calls_log=calls_log,
            stop={
                "after_call": 1, "kind": "table",
                "control_fifo": str(ctrl_fifo), "control_line": "/stop",
                "run_dir": str(run_dir), "table_id": "local-guest1",
            },
        )
        env = _gm_double_env(cfg_path)

        argv = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = _utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = _open_guest_fifo_pair(in_fifo, out_fifo)
        _wait_for_path(ctrl_fifo)

        initial_guest = _drain(out_f, settle=0.6, overall=10.0)
        assert initial_guest, "T1: Gast-Terminal hat keinen Startbanner gesendet."

        # ── Begrenzte Probe an der neuen Abbruchgrenze (02 §2 T1, letzter
        # Absatz): eine bereits legitim tolerierte Fassung (WIEDERVERWENDET
        # aus dem bestehenden J4-Toleranzpfad, `import_export.preview_
        # import_tolerant`, s. test_j4_tolerant_import_2026_11_02.py) --
        # echte Warnung sichtbar, dann OHNE Bestaetigung abgebrochen (kein
        # Write) -- keine neue tolerierte Reisekampagne, nur die Probe,
        # dass der bestehende Toleranzpfad auch an diesem Gast-Terminal
        # real erreichbar ist UND die Originalbytes dabei unberuehrt
        # bleiben.
        _send_guest(in_f, "i")
        _wait_for_marker(out_f, "JSON-Datei-Pfad", overall=20.0)
        _send_guest(in_f, str(_J4_TOLERATED_FIXTURE))
        _send_guest(in_f, "ENDE")
        tolerated_probe_out = _wait_for_marker(out_f, "Teilnehmer-ID eintippen", overall=20.0)
        joined_tolerated = "".join(tolerated_probe_out)
        assert "WARNUNG -- TOLERIERTER FREMDIMPORT" in joined_tolerated, joined_tolerated
        assert "maxItems" in joined_tolerated, joined_tolerated
        _send_guest(in_f, "nein-kein-import")
        tolerated_abort_out = _drain(out_f, settle=0.6, overall=10.0)
        joined_abort = "".join(tolerated_abort_out)
        assert "Import abgebrochen (kein Write)" in joined_abort, joined_abort
        sha_guest_after_tolerated_probe = _sha256(guest_figure_path)
        assert sha_guest_after_tolerated_probe == sha_guest_original_before_request, (
            "T1: die tolerierte Importprobe haette die Originaldatei NICHT veraendern duerfen."
        )

        # ── Normaler Produktweg: anbieten/anfragen/annehmen/starten.
        _send_op(proc, "tisch-anbieten mesaT1")
        time.sleep(0.6)
        _send_guest(in_f, "tisch-anfragen mesaT1")
        after_request = _drain(out_f, settle=0.6, overall=10.0)
        assert any("Anfrage an Tisch 'mesaT1' gestellt" in l for l in after_request), after_request
        _send_op(proc, "tisch-annehmen mesaT1 guest1")
        time.sleep(0.6)
        _send_op(proc, "tisch-start mesaT1")

        # Echter Kontroll-FIFO-Stop WAEHREND des offenen GM-Aufrufs (Double
        # blockiert bis zur durablen Bestaetigung, s. _r4_gm_double.py).
        _wait_for_marker(out_f, "Empfaenger: Spielleitung (SL)", overall=25.0)
        _deliver_guest_turn_answer(in_f, out_f, "Ich erkunde die Gegend.")
        post_answer = _drain(out_f, settle=0.6, overall=10.0)
        # R4 FIX6-Beleg: die echte Antwort (OHNE Leerzeilen-Workaround)
        # darf NICHT im Top-Menue-Dispatch als 'Unbekannte Auswahl' landen.
        assert "Unbekannte Auswahl" not in "".join(post_answer), (
            f"T1/FIX6: Rundenantwort wurde fehlgeleitet: {post_answer}"
        )

        # ── Spaeterer Annahmeversuch verliert am gemeinsamen Entscheid
        # (echter Dispatch-Versuch, NICHT nur Abwesenheit einer Plandatei).
        _send_op(proc, "tisch-start mesaT1")
        time.sleep(0.6)
        _send_op(proc, "tisch-anbieten mesaT1-retry")
        time.sleep(0.6)
        utc_end_cmd = _utc(time.time())
        _send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = _utc(time.time())
        in_f.close()
        out_f.close()
        _record_background_run(
            szene, "t1_operator_guest_round_stop_race", argv, str(_REPO_ROOT),
            utc_start, utc_end, proc.returncode, stdout_text, stderr_text,
        )
        assert proc.returncode == 0, f"T1: echter Launcher-Lauf ist unerwartet fehlgeschlagen: {stderr_text}"
        assert "[Zuschauer][SL] SL-Antwort auf Anker." in stdout_text, stdout_text
        assert "Tischstart abgelehnt: Tisch 'mesaT1' ist geschlossen" in stdout_text, (
            "T1: ein echter spaeterer Annahme-/Startversuch muss am gemeinsamen Entscheid "
            f"erkennbar scheitern: {stdout_text}"
        )
        assert "Tisch 'mesaT1-retry' offen" in stdout_text, stdout_text

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 1, f"T1: genau EIN GM-Turn (Anker) erwartet, Stop haette den zweiten verhindert: {calls}"
        assert calls[0]["content_returned"] == "SL-Antwort auf Anker."
        assert "Ich erkunde die Gegend." in calls[0]["user_text_excerpt"], calls[0]

        table_id = "local-guest1"
        stopped, stop_reason = admission.read_table_stop(run_dir, table_id)
        assert stopped is True, (stopped, stop_reason)
        decision = admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        record = table_admission.load_record(run_dir, "mesaT1")
        assert record is not None and record["state"] == table_admission.STATE_CLOSED, record
        section = store.Table.load(run_dir, table_id)
        assert section.status == "closed", f"T1: kein aktiver Core-Tisch als abgeschlossener Abbruch erwartet: {section.status}"
        completion_section_id = f"{table_id}-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        assert not plan_path.exists(), "T1: kein __plan.json -- die Planannahme hat den Stop verloren."
        assert not final_path.exists(), "T1: kein __final.json."

        # Direkter Nachweis "spaeterer Annahmeversuch verliert am
        # gemeinsamen Entscheid" UEBER DENSELBEN atomaren Slot (zusaetzlich
        # zum bereits oben bewiesenen Dispatch-Level-Scheitern).
        won_later, later_decision = admission.try_commit_table_decision(
            run_dir, table_id, "plan_committed", table_key="mesaT1", operator_id="operator1",
        )
        assert won_later is False and later_decision.get("decision") == "stopped", later_decision

        # Enge Probe (G5/O6): derselbe table_id-adressierte Gate-Check
        # blockt auch einen offenen Personaaufruf (persona-route,
        # dollar_billed=False) -- keine zweite Autoritaet fuer Personas.
        persona_blocked, persona_reason = admission.read_admission_block(
            run_dir, reserved_usd=0.01, output_bound_known=True, route="persona-route",
            dollar_billed=False, table_id=table_id,
        )
        assert persona_blocked is True, persona_reason

        guest_current_path = run_dir / "current_saves" / "guest1.json"
        assert guest_current_path.exists(), "guest1 haette bei Annahme hostseitig uebernommen werden muessen."
        sha_guest_current = _sha256(guest_current_path)
        active_binding = store.chrononaut_active_binding(run_dir, char_id)
        assert active_binding is False, f"T1: Figurenbindung haette freigegeben werden muessen: {active_binding}"

        after_guest_original_sha = _sha256(guest_figure_path)
        assert after_guest_original_sha == sha_guest_original_before_request, (
            "T1: die persoenliche Gast-Originaldatei wurde trotz Stop veraendert."
        )

        # ── Fortsetzbarkeit: ECHTER frischer Prozess (literaler CLI-
        # Einstiegspunkt, --no-host-capable) auf der Gastwurzel liest die
        # Figur + erreicht eine neue Tischanfrage.
        fresh_data_dir = op_data / "guests" / "guest1"
        fresh_argv = [
            sys.executable, "-B", str(_LAUNCHER), "--no-host-capable",
            "--participant", "guest1", "--data-dir", str(fresh_data_dir),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
        ]
        fresh = _run_real_subprocess(
            szene, "t1_fresh_guest_process_reads_and_requests", fresh_argv,
            cwd=str(_REPO_ROOT), input="s\ntisch-suchen\ntisch-anfragen mesaT1-retry\nbeenden\n",
            env=_clean_env(),
        )
        assert fresh.returncode == 0, f"T1: frischer Gastprozess ist unerwartet fehlgeschlagen: {fresh.stderr}"
        assert "Katalog-Eintraege: 1" in fresh.stdout, fresh.stdout
        assert "'mesaT1-retry'" in fresh.stdout, fresh.stdout
        assert "Anfrage an Tisch 'mesaT1-retry' gestellt" in fresh.stdout, fresh.stdout

        after_fresh_sha = _sha256(guest_figure_path)
        assert after_fresh_sha == sha_guest_original_before_request, (
            "T1: der frische Leseprozess hat die Originaldatei veraendert."
        )

        # ── Export VOR Tempverzeichnis-Bereinigung.
        _export_tree(szene, run_dir, "run")
        _export_tree(szene, states_dir, "states")
        _export_tree(szene, guest_onboarding, "guest_onboarding")
        _export_tree(szene, guest_catalog, "guest_catalog")
        _export_file(szene, calls_log, "gm_calls.jsonl")
        _write_export_json(szene, "io_transcript.json", {
            "tolerated_probe_warning": joined_tolerated, "tolerated_probe_abort": joined_abort,
            "after_request": after_request, "post_answer": post_answer,
        })
        _write_export_json(szene, "inventory.json", {
            "before": {
                "guest_original_sha256": sha_guest_original_before_request,
                "plan_exists": False, "final_exists": False,
            },
            "after": {
                "guest_original_sha256": after_fresh_sha, "guest_current_sha256": sha_guest_current,
                "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
                "chrononaut_active_binding": active_binding, "table_state": record["state"],
            },
            "notes": [
                "GM-Anbieter ist eine Grenzinjektion (FIX5, MMO_SIM_GM_TRANSPORT_DOUBLE) -- s. "
                "gm_calls.jsonl, kein Live-Modelllauf.",
                "Originaldatei VOR dem ersten Request gesichert (sha_guest_original_before_request), "
                "NICHT nachtraeglich nach dem Abbruch gemessen.",
                "Tolerierte Anfangsfassung wiederverwendet aus dem bestehenden J4-Toleranzpfad "
                "(fixtures/j4_tolerant_import/p01_latch.json) -- echte Warnung sichtbar, dann ohne "
                "Bestaetigung abgebrochen (kein Write), keine neue tolerierte Reisekampagne.",
                "Spaeterer Annahmeversuch verliert NACHWEISLICH am gemeinsamen Entscheid -- sowohl am "
                "echten Dispatch ('Tischstart abgelehnt: ... ist geschlossen') als auch am atomaren "
                "Entscheid-Slot selbst (try_commit_table_decision liefert won=False).",
            ],
        })


# ───────────────────────── Familie T2 ─────────────────────────
# G2/G5, O4 (02 §2 T2): DIESELBE angenommene Tisch-/Abschnittsentscheidung
# durchgehend -- Planannahme, Teilpublikation, Betreiberstop (haelt, blockt
# NICHT den Restabschluss des bereits gebundenen Abschnitts, F3b), dann
# echter neuer Prozess bedient Fortsetzen-Weg inkl. '/abbrechen' an der
# freiwilligen Notiz (bleibt offen, EndOfInput) und danach die regulaer
# erreichbare Fertigstellung (echte Notiz) + privater Rueckkanal.

def run_family_t2() -> None:
    szene = "t2"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        ctrl_fifo = fifo_dir / "ctrl.fifo"
        in_fifo_1 = fifo_dir / "guest_in_1.fifo"
        out_fifo_1 = fifo_dir / "guest_out_1.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        char_id = "chrono-t2-guest"
        _seed_guest_figure(guest_onboarding, guest_catalog, "guest1", char_id, "fixture-t2-guest-001")
        guest_current_path = run_dir / "current_saves" / "guest1.json"

        debrief_save = full_v7_save(char_id, name="Gast-guest1", save_id="fixture-t2-guest-002", level=2)
        debrief_text = (
            "Abschnitt beendet.\n```json\n" + json.dumps(debrief_save) + "\n```\nSECTION-ABSCHLUSS-BESTAETIGT"
        )
        _write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker.", debrief_text], calls_log=calls_log,
        )
        env = _gm_double_env(cfg_path)

        # ── Prozess 1 (gebundene Skriptdatei, ECHTER launcher.main()
        # importiert, Klassen-Monkeypatch GENAU an der Abbruch-Grenze):
        # echter Rundenverlauf bis Plan-Pin + Primaersave (Phase 1), dann
        # os._exit(94) VOR jeder Reflexion (Phase 2).
        argv1 = [
            sys.executable, "-B", str(_HARDEXIT_BEFORE_REFLECTION),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_1}:{out_fifo_1}",
        ]
        utc_start = _utc(time.time())
        proc1 = subprocess.Popen(
            argv1, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f1, out_f1 = _open_guest_fifo_pair(in_fifo_1, out_fifo_1)
        _drain(out_f1, settle=0.6, overall=10.0)

        _send_op(proc1, "tisch-anbieten mesaT2")
        time.sleep(0.6)
        _send_guest(in_f1, "tisch-anfragen mesaT2")
        after_request = _drain(out_f1, settle=0.6, overall=10.0)
        assert any("Anfrage an Tisch 'mesaT2' gestellt" in l for l in after_request), after_request
        _send_op(proc1, "tisch-annehmen mesaT2 guest1")
        time.sleep(0.6)
        _send_op(proc1, "tisch-start mesaT2")

        _wait_for_marker(out_f1, "Empfaenger: Spielleitung (SL)", overall=25.0)
        _deliver_guest_turn_answer(in_f1, out_f1, "Ich erkunde die Gegend.")
        # Zweiter echter Zug (Debrief-Antwort mit COMPLETION_MARKER). Der
        # Rundenprompt erscheint erneut NUR, wenn die erste Antwort den
        # Round-Reader (nicht den Menue-Dispatch) erreicht hat -- ohne
        # FIX6 waere diese Marker-Wartung durch Timeout gescheitert
        # (AssertionError), WEIL die erste Antwort sonst im Top-Menue
        # 'Unbekannte Auswahl' quittiert worden waere und der Round-Reader
        # unbegrenzt auf die echte Antwort weiterwartet haette.
        second_turn_lines = _wait_for_marker(out_f1, "Empfaenger: Spielleitung (SL)", overall=25.0)
        assert "Unbekannte Auswahl" not in "".join(second_turn_lines), (
            f"T2/FIX6: erste Rundenantwort wurde fehlgeleitet: {second_turn_lines}"
        )
        _deliver_guest_turn_answer(in_f1, out_f1, "Ich gehe weiter.")

        stdout1, stderr1 = proc1.communicate(timeout=30)
        utc_end = _utc(time.time())
        in_f1.close()
        out_f1.close()
        _record_background_run(
            szene, "t2_proc1_plan_pin_primary_save_hard_exit", argv1, str(_REPO_ROOT),
            utc_start, utc_end, proc1.returncode, stdout1, stderr1,
        )
        assert proc1.returncode == 94, (
            f"T2: Prozess 1 muss ueber os._exit(94) enden (NACH Plan-Pin/Primaersave, VOR Reflexion) -- "
            f"rc={proc1.returncode} stderr={stderr1!r}"
        )

        table_id = "local-guest1"
        completion_section_id = f"{table_id}-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        assert plan_path.exists(), "T2: Prozess 1 haette den Plan real pinnen muessen (Phase 1)."
        assert guest_current_path.exists(), "T2: Prozess 1 haette den Primaersave real schreiben muessen."
        assert not final_path.exists(), "T2: Phase 2 (__final.json) darf von Prozess 1 NICHT erreicht worden sein."
        sha_guest_phase1 = _sha256(guest_current_path)
        decision = admission.read_table_decision(run_dir, table_id)
        assert decision is not None and decision.get("decision") == "plan_committed", decision
        before_inventory = {
            "plan_exists": True, "final_exists": False, "guest_current_sha256": sha_guest_phase1,
            "decision": decision.get("decision"),
        }

        # ── Prozess 2 (literaler Launcher, ECHTER Fortsetzen-/Retryweg
        # 'tisch-start' -- FIX2 G2-Nachweis: KEIN 'KI-Leader'-Abbruch mehr
        # fuer den ueber --guest-terminal admittierten menschlichen
        # Leader). Betreiberstop WAEHREND der offenen Reflexion (F3b: der
        # Abschluss hat den Slot schon gewonnen -> Stop haelt NUR neue
        # Spielzuege; NICHT den Restabschluss dieses Abschnitts). '/abbrechen'
        # an der freiwilligen Notiz -- bleibt ehrlich offen (EndOfInput).
        in_fifo_2 = fifo_dir / "guest_in_2.fifo"
        out_fifo_2 = fifo_dir / "guest_out_2.fifo"
        argv2 = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--operator-control-fifo", str(ctrl_fifo),
            "--guest-terminal", f"guest1:{in_fifo_2}:{out_fifo_2}",
        ]
        utc_start2 = _utc(time.time())
        proc2 = subprocess.Popen(
            argv2, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f2, out_f2 = _open_guest_fifo_pair(in_fifo_2, out_fifo_2)
        _wait_for_path(ctrl_fifo)
        _drain(out_f2, settle=0.6, overall=10.0)
        _send_op(proc2, "tisch-start mesaT2")
        resume_lines = _wait_for_marker(out_f2, "eigene lokale Notiz", overall=25.0)
        joined_resume = "".join(resume_lines)
        assert "KI-Leader" not in joined_resume, (
            f"T2/FIX2: der admittierte menschliche Leader darf NICHT mehr als KI-Leader "
            f"abgelehnt werden: {joined_resume}"
        )

        # Echter Betreiberstop ueber die Kontroll-FIFO (dasselbe `/stop`
        # wie T1) WAEHREND die Reflexion offen ist -- der gemeinsame
        # Entscheid ist bereits 'plan_committed' (Prozess 1), der Stop
        # gewinnt daher NICHT, haelt aber die durable Betreiberabsicht
        # (keine neuen Spielzuege) fest.
        fd = os.open(str(ctrl_fifo), os.O_WRONLY)
        with os.fdopen(fd, "w") as f:
            f.write("/stop\n")
        _deadline = time.time() + 15
        while time.time() < _deadline:
            stopped_mid, _r = admission.read_table_stop(run_dir, table_id)
            if stopped_mid:
                break
            time.sleep(0.05)
        assert stopped_mid is True, "T2: der echte Kontroll-FIFO-Stop wurde nicht durabel bestaetigt."
        decision_after_stop_attempt = admission.read_table_decision(run_dir, table_id)
        assert decision_after_stop_attempt.get("decision") == "plan_committed", (
            "T2/F3b: der Stop-Versuch darf eine bereits gewonnene Planannahme NICHT ueberschreiben: "
            f"{decision_after_stop_attempt}"
        )

        _deliver_guest_turn_answer(in_f2, out_f2, "/abbrechen")
        abbrechen_out = _wait_for_marker(out_f2, "wird regulaer fertiggestellt", overall=15.0)
        joined_abbrechen = "".join(abbrechen_out)
        assert "Spielstand uebernommen" in joined_abbrechen, joined_abbrechen
        assert "KEIN Verwurf" in joined_abbrechen, joined_abbrechen
        # R4 FIX6-Beleg: '/abbrechen' (ohne Leerzeilen-Workaround gesendet)
        # muss den Round-Reader erreichen (der o.g. '/abbrechen'-Zweig in
        # `decide()`), NICHT im Top-Menue-Dispatch landen.
        assert "Unbekannte Auswahl" not in joined_abbrechen, (
            f"T2/FIX6: '/abbrechen' wurde fehlgeleitet: {abbrechen_out}"
        )

        stdout2, stderr2 = proc2.communicate(timeout=30)
        utc_end2 = _utc(time.time())
        in_f2.close()
        out_f2.close()
        _record_background_run(
            szene, "t2_proc2_resume_stop_abbrechen_leaves_open", argv2, str(_REPO_ROOT),
            utc_start2, utc_end2, proc2.returncode, stdout2, stderr2,
        )
        assert proc2.returncode == 0, f"T2: Prozess 2 ist unerwartet gescheitert: {stderr2}"
        assert not final_path.exists(), "T2: '/abbrechen' an der Notiz darf NICHT finalisieren (bleibt offen)."
        assert _sha256(guest_current_path) == sha_guest_phase1, (
            "T2: '/abbrechen' an der Notiz darf den Primaersave NICHT veraendern."
        )
        held_state = {
            "plan_exists": plan_path.exists(), "final_exists": final_path.exists(),
            "table_stop": admission.read_table_stop(run_dir, table_id),
            "decision": admission.read_table_decision(run_dir, table_id),
            "guest_current_sha256": _sha256(guest_current_path),
        }

        # ── Prozess 3 (literaler Launcher, echter NEUER Prozess): derselbe
        # Fortsetzen-Weg erreicht die REGULAERE Fertigstellung -- diesmal
        # eine echte freiwillige Notiz statt '/abbrechen'.
        in_fifo_3 = fifo_dir / "guest_in_3.fifo"
        out_fifo_3 = fifo_dir / "guest_out_3.fifo"
        argv3 = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_3}:{out_fifo_3}",
        ]
        proc3 = subprocess.Popen(
            argv3, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        utc_start3 = _utc(time.time())
        in_f3, out_f3 = _open_guest_fifo_pair(in_fifo_3, out_fifo_3)
        _drain(out_f3, settle=0.6, overall=10.0)
        _send_op(proc3, "tisch-start mesaT2")
        _wait_for_marker(out_f3, "eigene lokale Notiz", overall=25.0)
        _deliver_guest_turn_answer(in_f3, out_f3, "Echte freiwillige Abschlussnotiz: alles gut gelaufen.")
        # KEIN Promptzeilen-Marker: `_fifo_input_fn` schreibt den
        # `prompt`-Text (z.B. "Auswahl: ") NIE in die Ausgabe-FIFO -- der
        # echte, robuste Abschlussnachweis ist die tatsaechlich entstandene
        # `__final.json` auf Platte.
        _wait_for_path(final_path, overall=25.0)
        finish_out = _drain(out_f3, settle=0.6, overall=10.0)
        # R4 FIX6-Beleg: die freiwillige Notiz (ohne Leerzeilen-Workaround)
        # muss den Reflexions-Round-Reader erreicht haben -- `final_path`
        # (oben bereits abgewartet) kann NUR entstehen, wenn
        # `_collect_reflections`/`decide()` die Antwort real erhalten hat;
        # zusaetzlich darf keine spaete 'Unbekannte Auswahl'-Fehlzustellung
        # im Nachlauf sichtbar werden.
        assert "Unbekannte Auswahl" not in "".join(finish_out), (
            f"T2/FIX6: freiwillige Notiz wurde fehlgeleitet: {finish_out}"
        )
        _send_op(proc3, "beenden")
        stdout3, stderr3 = proc3.communicate(timeout=30)
        utc_end3 = _utc(time.time())
        in_f3.close()
        out_f3.close()
        _record_background_run(
            szene, "t2_proc3_real_finish_via_voluntary_note", argv3, str(_REPO_ROOT),
            utc_start3, utc_end3, proc3.returncode, stdout3, stderr3,
        )
        assert proc3.returncode == 0, f"T2: Prozess 3 ist unerwartet gescheitert: {stderr3}"
        assert final_path.exists(), "T2: der echte Fortsetzen-Prozess haette __final.json real schreiben muessen."
        sha_final = _sha256(final_path)
        sha_guest_after_finish = _sha256(guest_current_path)

        # Privater Rueckkanal (`_writeback_registered_guest_saves`): die
        # abgeschlossene Fassung landet in der EIGENEN privaten Gastablage
        # (NICHT nur im Hostbestand).
        guest_private_state = onboarding.peek(guest_onboarding, "guest1")
        assert guest_private_state is not None and guest_private_state.final_save is not None, (
            "T2: die abgeschlossene Fassung haette ueber den normalen Rueckkanal in die private "
            "Gastablage geschrieben werden muessen."
        )

        # ── Prozess 4 (literaler Launcher, identischer Retry): keine
        # weitere Wirkung.
        in_fifo_4 = fifo_dir / "guest_in_4.fifo"
        out_fifo_4 = fifo_dir / "guest_out_4.fifo"
        argv4 = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo_4}:{out_fifo_4}",
        ]
        result4 = _run_real_subprocess(
            szene, "t2_proc4_identical_retry_no_double_effect", argv4,
            cwd=str(_REPO_ROOT), env=env, input="tisch-start mesaT2\nbeenden\n",
        )
        assert result4.returncode == 0, f"T2: identischer Retry-Prozess ist unerwartet gescheitert: {result4.stderr}"
        assert "Tischstart abgelehnt: Tisch 'mesaT2' ist geschlossen" in result4.stdout, result4.stdout
        assert _sha256(final_path) == sha_final, "T2: identischer Retry hat __final.json erneut geschrieben."
        assert _sha256(guest_current_path) == sha_guest_after_finish, (
            "T2: identischer Retry hat den Gast-Save veraendert."
        )

        # ── Export VOR Tempverzeichnis-Bereinigung.
        _export_tree(szene, run_dir, "run")
        _export_tree(szene, states_dir, "states")
        _export_tree(szene, guest_onboarding, "guest_onboarding")
        _export_tree(szene, guest_catalog, "guest_catalog")
        _export_file(szene, calls_log, "gm_calls.jsonl")
        _write_export_json(szene, "io_transcript.json", {
            "proc2_resume": joined_resume, "proc2_abbrechen": joined_abbrechen,
            "proc3_finish_tail": "".join(finish_out),
        })
        _write_export_json(szene, "inventory.json", {
            "before": before_inventory, "held_after_stop_and_abbrechen": held_state,
            "after_real_finish": {
                "final_exists": True, "final_sha256": sha_final,
                "guest_current_sha256": sha_guest_after_finish,
                "guest_private_final_save_present": guest_private_state.final_save is not None,
            },
            "notes": [
                "GM-Anbieter ist eine Grenzinjektion (FIX5) -- genau 2 GM-Calls (Anker+Debrief), s. "
                "gm_calls.jsonl; Prozess 2/3/4 brauchen GAR KEINEN GM-Call mehr (reine Reflexion/"
                "Finalisierung).",
                "FIX2 real nachgewiesen: Prozess 2's 'tisch-start' resumiert den ueber --guest-terminal "
                "admittierten menschlichen Leader OHNE 'KI-Leader erfordert Persona-Anbindung'-Abbruch.",
                "F3b real nachgewiesen: der Betreiberstop (Prozess 2, echte Kontroll-FIFO) gewinnt NICHT "
                "gegen die bereits gewonnene Planannahme (decision bleibt 'plan_committed'), blockt aber "
                "durabel neue Spielzuege (table_stop gesetzt).",
                "'/abbrechen' an der freiwilligen Notiz laesst den Restabschluss ehrlich OFFEN "
                "(EndOfInput, kein Verwurf, kein Final) -- die anschliessend erreichbare REGULAERE "
                "Fertigstellung wird in Prozess 3 (echte Notiz) tatsaechlich gezeigt.",
                "Die abgeschlossene Fassung kommt ueber den normalen Rueckkanal "
                "(`_writeback_registered_guest_saves`) in der PRIVATEN Gastablage an (onboarding.peek "
                "auf guest_onboarding, NICHT nur im Hostbestand).",
            ],
        })


# ───────────────────────── Familie T3 ─────────────────────────
# G3/G5, O5/O6 (02 §2 T3): hostloser Gast (ohne Figur/Providerconfig/
# Hostfaehigkeit) ueber den ECHTEN ausgelieferten Launcher-Anschluss
# (--guest-terminal, FIX1) -- Anbieter-GM stellt Fragen, der Gast antwortet
# ueber sein EIGENES Terminal, erst danach wird die fertige Fassung
# angenommen.

def run_family_t3() -> None:
    szene = "t3"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        op_data = root / "op_data"
        run_dir = root / "run"
        states_dir = root / "states"
        fifo_dir = root / "fifos"
        fifo_dir.mkdir(parents=True)
        in_fifo = fifo_dir / "guest_in.fifo"
        out_fifo = fifo_dir / "guest_out.fifo"
        calls_log = root / "gm_calls.jsonl"
        cfg_path = root / "gmdouble_cfg.json"

        write_test_profile(run_dir, max_turns=200)
        guest_onboarding = op_data / "guests" / "guest1" / "onboarding"
        guest_catalog = op_data / "guests" / "guest1" / "catalog"
        char_id = "CHR-T3-GAST"
        final_block = full_v7_save(char_id, name="GastT3", save_id="fixture-t3-guest-001")
        q1 = "Wie nennt sich dein Chrononaut?"
        q2 = "Was ist ihr praegender Ursprung?"
        final_content = "```json\n" + json.dumps(final_block, ensure_ascii=False) + "\n```"
        _write_gm_double_config(cfg_path, responses=[q1, q2, final_content], calls_log=calls_log)
        env = _gm_double_env(cfg_path)

        argv = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
            "--guest-terminal", f"guest1:{in_fifo}:{out_fifo}",
        ]
        utc_start = _utc(time.time())
        proc = subprocess.Popen(
            argv, cwd=str(_REPO_ROOT), env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f, out_f = _open_guest_fifo_pair(in_fifo, out_fifo)
        _drain(out_f, settle=0.6, overall=10.0)

        # §O6 Negativfall (a): KEINE Freigabe -- 0 GM-Aufrufe, 0 Writes.
        # ("gast-erschaffung-dialog" ist eine EIGENE, synchron im Gast-
        # Thread abgearbeitete Top-Level-Anweisung -- kein konkurrierender
        # Zweitleser wie bei einer Tischrunde, s. Moduldocstring.)
        _send_guest(in_f, "gast-erschaffung-dialog operator1")
        no_grant_out = _drain(out_f, settle=0.6, overall=10.0)
        joined_no_grant = "".join(no_grant_out)
        assert "kein gueltiger Betreiber-Grant" in joined_no_grant, joined_no_grant

        # §O6 Negativfall (b): Gast stellt die Anfrage; EIN FREMDER
        # Betreiber ('mallory') kann sie NICHT entscheiden (direkter
        # Aufruf der echten Autoritaetsfunktion, dieselbe Pruefung, die
        # `_cmd_gast_erschaffung_annehmen` intern verwendet).
        _send_guest(in_f, "gast-erschaffung-anfragen operator1")
        request_out = _drain(out_f, settle=0.6, overall=10.0)
        assert "Erschaffungsanfrage an Betreiber 'operator1' gestellt" in "".join(request_out), request_out
        try:
            creation_grants.decide_creation_request(
                run_dir, operator_id="mallory", guest_id="guest1", approve=True,
            )
            raise AssertionError("T3: ein fremder Betreiber ('mallory') haette abgelehnt werden muessen.")
        except creation_grants.CreationGrantError:
            pass
        grant_after_foreign = creation_grants.grant_status(run_dir, "guest1")
        assert grant_after_foreign["status"] == "requested", grant_after_foreign

        # Echte Betreiberfreigabe (TATSAECHLICHER Betreiber, operator1).
        _send_op(proc, "gast-erschaffung-annehmen guest1")
        time.sleep(0.6)
        grant_after_approve = creation_grants.grant_status(run_dir, "guest1")
        assert grant_after_approve["status"] == "approved" and grant_after_approve["generation"] == 1, grant_after_approve

        # Mehrschrittiger echter Dialog: Anbieter-GM stellt zwei echte
        # Fragen, der Gast antwortet ueber sein EIGENES Terminal (FIFO),
        # ERST danach wird die fertige Fassung angenommen.
        _send_guest(in_f, "gast-erschaffung-dialog operator1")
        _wait_for_marker(out_f, f"[SL] {q1}", overall=15.0)
        _send_guest(in_f, "Elena")
        _wait_for_marker(out_f, f"[SL] {q2}", overall=15.0)
        _send_guest(in_f, "Eine verlorene Chronoflotte.")
        dialog_tail = _drain(out_f, settle=0.8, overall=15.0)

        calls = [json.loads(l) for l in calls_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(calls) == 3, f"T3: zwei Fragen + ein finaler Save erwartet, calls={calls}"
        assert calls[0]["content_returned"] == q1
        assert calls[1]["content_returned"] == q2
        assert "Elena" in calls[1]["user_text_excerpt"], calls[1]
        assert "Eine verlorene Chronoflotte." in calls[2]["user_text_excerpt"], calls[2]

        onboarding_key = creation_grants.guest_onboarding_key("guest1", 1)
        state = onboarding.peek(guest_onboarding, onboarding_key)
        assert state is not None and state.status == "completed", state
        assert state.final_save == final_block, "persoenlicher Save muss real ueber complete_with_save gelandet sein."

        entries = catalog.list_for_participant(guest_catalog, "guest1")
        assert any(e.chrononaut_id == char_id for e in entries), entries
        assert catalog.load_figure_save(guest_catalog, "guest1", char_id) == final_block
        current_save_path = run_dir / "current_saves" / "guest1.json"
        assert current_save_path.exists(), "T3: Current-Save haette real veroeffentlicht werden muessen."
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        published = store.load_current_save_or_raise(run_dir, "guest1", ps_store, states_dir=states_dir)
        assert published == final_block, published

        # Strukturelle Garantie (FIX1, `scripts/mmo_sim.py`-Quelle): ein
        # `--guest-terminal`-Gast bekommt NIE eine eigene
        # `gm_transport_factory`/`persona_driver_factory` uebergeben --
        # STRUKTURELL unerreichbar, nicht nur ungenutzt. Die einzige
        # SL-Anbindung ist die ANBIETER-Autoritaet (register_guest_terminal,
        # G3). Die 3 Aufrufe oben liefen alle gegen operator1s Double.
        #
        # R4 FIX6-Nachzug: `input_fn=_fifo_input_fn(in_fifo_path)` wurde
        # durch den geteilten `_FifoInputReader` (`read_line`/`ready`, s.
        # `scripts/mmo_sim.py`-Docstring an dieser Stelle) ersetzt, UM
        # Einzelleser-Koordination (FIX6, `_readline_guest_menu`) zu
        # ermoeglichen -- die hier geprueften strukturellen Garantien
        # (KEINE `gm_transport_factory`/`persona_driver_factory`-Zeile im
        # Block) bleiben unveraendert, nur der literale Text wird
        # nachgezogen.
        guest_terminal_source = _LAUNCHER.read_text(encoding="utf-8")
        assert (
            'onboarding_dir=data_dir / "guests" / guest_id / "onboarding",\n'
            '            catalog_dir=data_dir / "guests" / guest_id / "catalog",\n'
            '            participant_id=guest_id,\n'
            "            input_fn=in_fifo_reader.read_line,\n"
            "            print_fn=_fifo_print_fn(out_fifo_path),\n"
            "            run_dir=run_dir,\n"
            "            states_dir=states_dir,\n"
            "            schema_path=schema_path if schema_path.is_file() else None,\n"
            "            host_capable=False,\n"
            "            input_ready_fn=in_fifo_reader.ready,\n"
            "        )" in guest_terminal_source
        ), "T3: der echte Launcher-Quellcode haette KEINE gm_transport_factory fuer --guest-terminal uebergeben duerfen."

        # Fortsetzbarkeit: Betreiber bietet einen Tisch an, damit der
        # FRISCHE Prozess unten eine echte Tischanfrage erreichen kann.
        _send_op(proc, "tisch-anbieten mesaT3")
        time.sleep(0.6)

        sha_guest_current_before = _sha256(current_save_path)
        guest_figure_path = guest_catalog / "figures" / f"guest1__{char_id}.json"
        sha_guest_figure_before = _sha256(guest_figure_path)

        utc_cmd_end = _utc(time.time())
        _send_op(proc, "beenden")
        stdout_text, stderr_text = proc.communicate(timeout=30)
        utc_end = _utc(time.time())
        in_f.close()
        out_f.close()
        _record_background_run(
            szene, "t3_operator_provider_and_guest_dialog", argv, str(_REPO_ROOT),
            utc_start, utc_end, proc.returncode, stdout_text, stderr_text,
        )
        assert proc.returncode == 0, f"T3: echter Launcher-Lauf ist unerwartet fehlgeschlagen: {stderr_text}"
        assert "Tisch 'mesaT3' offen" in stdout_text, stdout_text

        # ── Frischer Prozess (literaler CLI-Einstiegspunkt,
        # --no-host-capable) auf der Gastwurzel liest die Figur + erreicht
        # eine echte Tischanfrage.
        fresh_data_dir = op_data / "guests" / "guest1"
        fresh_argv = [
            sys.executable, "-B", str(_LAUNCHER), "--no-host-capable",
            "--participant", "guest1", "--data-dir", str(fresh_data_dir),
            "--run-dir", str(run_dir), "--states-dir", str(states_dir),
        ]
        fresh = _run_real_subprocess(
            szene, "t3_fresh_guest_process_reads_and_requests", fresh_argv,
            cwd=str(_REPO_ROOT), input="s\ntisch-suchen\ntisch-anfragen mesaT3\nbeenden\n",
            env=_clean_env(),
        )
        assert fresh.returncode == 0, f"T3: frischer Gastprozess ist unerwartet fehlgeschlagen: {fresh.stderr}"
        assert "Katalog-Eintraege: 1" in fresh.stdout, fresh.stdout
        assert "'mesaT3'" in fresh.stdout, fresh.stdout
        assert "Anfrage an Tisch 'mesaT3' gestellt" in fresh.stdout, fresh.stdout

        assert _sha256(current_save_path) == sha_guest_current_before, (
            "T3: der frische Leseprozess hat den Current-Save veraendert."
        )
        assert _sha256(guest_figure_path) == sha_guest_figure_before, (
            "T3: der frische Leseprozess hat die private Gastfigur veraendert."
        )

        # ── Export VOR Tempverzeichnis-Bereinigung.
        _export_tree(szene, run_dir, "run")
        _export_tree(szene, states_dir, "states")
        _export_tree(szene, guest_onboarding, "guest_onboarding")
        _export_tree(szene, guest_catalog, "guest_catalog")
        _export_file(szene, calls_log, "gm_calls.jsonl")
        _write_export_json(szene, "io_transcript.json", {
            "no_grant_probe": joined_no_grant, "dialog_tail": "".join(dialog_tail),
        })
        _write_export_json(szene, "inventory.json", {
            "before": {"guest_current_sha256": None, "guest_figure_sha256": None, "grant_status": None},
            "after": {
                "guest_current_sha256": sha_guest_current_before, "guest_figure_sha256": sha_guest_figure_before,
                "grant_status": creation_grants.grant_status(run_dir, "guest1"),
            },
            "notes": [
                "GM-Anbieter ist eine Grenzinjektion (FIX5) -- genau 3 Aufrufe (2 Fragen + 1 "
                "finaler Save), s. gm_calls.jsonl. Vor jeder Freigabe erreichte KEIN Aufruf den "
                "Double (0 calls bis zur Freigabe).",
                "Vor der Freigabe/Anfrage existierte weder ein Grant-Record noch ein persoenlicher "
                "Gastsave (echtes Vorher = vollstaendig fehlend) -- bewusst kein Fake-Leer-Record.",
                "Der hostlose Gast (--guest-terminal, FIX1) bekommt laut echtem Launcher-Quellcode "
                "STRUKTURELL keine eigene gm_transport_factory/persona_driver_factory -- die einzige "
                "SL-Anbindung ist die Anbieter-Autoritaet (register_guest_terminal, G3).",
                "Ein fremder Betreiber ('mallory') wurde ueber die ECHTE Autoritaetsfunktion "
                "(creation_grants.decide_creation_request) abgelehnt -- derselbe Pruefpfad, den "
                "'gast-erschaffung-annehmen' intern verwendet.",
            ],
        })


# ───────────────────────── Familie T4 ─────────────────────────
# G4/G5, O2/O5/O6 (02 §2 T4): dieselbe Erschaffungsautoritaet VOR und NACH
# Annahme stoppen -- nutzt denselben T3-Anschluss (--guest-terminal,
# Anbieter-GM-Double).

def run_family_t4() -> None:
    szene = "t4"
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # ========== T4-A: Stop VOR Annahme (waehrend offenem Request) ====
        op_data_a = root / "opA_data"
        run_dir_a = root / "runA"
        states_dir_a = root / "statesA"
        fifo_dir_a = root / "fifosA"
        fifo_dir_a.mkdir(parents=True)
        in_fifo_a = fifo_dir_a / "guest_in.fifo"
        out_fifo_a = fifo_dir_a / "guest_out.fifo"
        calls_log_a = root / "gm_calls_a.jsonl"
        cfg_path_a = root / "gmdouble_cfg_a.json"
        signal_path_a = root / "stop_signal_a.json"

        write_test_profile(run_dir_a, max_turns=200)
        char_id_a = "CHR-T4A-GAST"
        final_block_a = full_v7_save(char_id_a, name="GastT4A", save_id="fixture-t4a-guest-001")
        q1_a, q2_a = "Wie nennt sich dein Chrononaut?", "Was ist ihr praegender Ursprung?"
        final_content_a = "```json\n" + json.dumps(final_block_a, ensure_ascii=False) + "\n```"
        _write_gm_double_config(
            cfg_path_a, responses=[q1_a, q2_a, final_content_a], calls_log=calls_log_a,
            stop={
                "after_call": 2, "kind": "creation", "signal_file": str(signal_path_a),
                "run_dir": str(run_dir_a), "operator_id": "operator1", "guest_id": "guest1", "generation": 1,
            },
        )
        env_a = _gm_double_env(cfg_path_a)
        argv_a = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data_a),
            "--run-dir", str(run_dir_a), "--states-dir", str(states_dir_a),
            "--guest-terminal", f"guest1:{in_fifo_a}:{out_fifo_a}",
        ]
        utc_start_a = _utc(time.time())
        proc_a = subprocess.Popen(
            argv_a, cwd=str(_REPO_ROOT), env=env_a, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f_a, out_f_a = _open_guest_fifo_pair(in_fifo_a, out_fifo_a)
        _drain(out_f_a, settle=0.6, overall=10.0)

        _send_guest(in_f_a, "gast-erschaffung-anfragen operator1")
        _drain(out_f_a, settle=0.6, overall=10.0)
        _send_op(proc_a, "gast-erschaffung-annehmen guest1")
        time.sleep(0.6)
        grant_a_before = creation_grants.grant_status(run_dir_a, "guest1")
        assert grant_a_before["status"] == "approved" and grant_a_before["generation"] == 1, grant_a_before

        _send_guest(in_f_a, "gast-erschaffung-dialog operator1")
        _wait_for_marker(out_f_a, f"[SL] {q1_a}", overall=15.0)
        _send_guest(in_f_a, "Elena")

        # Der Double blockiert JETZT innerhalb des Q2-Aufrufs (echter
        # offener Anbieterrequest) und beruehrt die Signaldatei -- der
        # Betreiber tippt den ECHTEN Top-Level-Befehl 'gast-erschaffung-
        # stop guest1' ueber sein EIGENES regulaeres stdin ein, SOBALD
        # die Signaldatei erscheint (der Double selbst ruft NIE eine
        # interne Kommandomethode auf, s. _r4_gm_double.py).
        _wait_for_path(signal_path_a, overall=15.0)
        _send_op(proc_a, "gast-erschaffung-stop guest1")
        # Spaete Antwort (Q2) wird nach der durablen Stop-Bestaetigung
        # trotzdem zugestellt -- korrekt verbucht, aber danach terminal.
        _wait_for_marker(out_f_a, f"[SL] {q2_a}", overall=15.0)
        _send_guest(in_f_a, "Eine verlorene Chronoflotte.")
        final_tail = _drain(out_f_a, settle=0.8, overall=15.0)
        joined_final_tail = "".join(final_tail)
        assert "Betreiber-Stop beendet (terminal)" in joined_final_tail and "kein Katalog-/Current-Write" in joined_final_tail, (
            joined_final_tail
        )

        decision_a = admission.read_table_decision(
            run_dir_a, creation_grants._creation_decision_id("operator1", "guest1", 1),
        )
        assert decision_a is not None and decision_a.get("decision") == "stopped", decision_a
        assert not (run_dir_a / "current_saves" / "guest1.json").exists(), (
            "T4A: kein Current-Write nach gewonnenem Stop erwartet."
        )

        # Frischer Prozess respektiert denselben terminalen Abbruch -- kein
        # neuer Dialogeintritt, keine Publikation. R4 FIX7: der Retry MUSS
        # ECHT ueber die verdrahtete GAST-FIFO (laeuft als guest1) getrieben
        # werden, NICHT ueber das Operator-stdin -- sonst bindet
        # `ensure_valid_grant` faelschlich guest_id=self.participant_id=
        # 'operator1' (fuer diese ID existiert NIE ein Grant-Record), was
        # die triviale Ablehnung "keine Erschaffungsanfrage/-freigabe fuer
        # guest_id='operator1'" ausloest -- BEVOR der echte Stop-Pfad
        # (`ensure_valid_grant`s gewonnener-Stop-Zweig) je erreicht wird.
        in_fifo_a2 = fifo_dir_a / "guest_in_2.fifo"
        out_fifo_a2 = fifo_dir_a / "guest_out_2.fifo"
        argv_a2 = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator1", "--data-dir", str(op_data_a),
            "--run-dir", str(run_dir_a), "--states-dir", str(states_dir_a),
            "--guest-terminal", f"guest1:{in_fifo_a2}:{out_fifo_a2}",
        ]
        utc_start_a2 = _utc(time.time())
        proc_a2 = subprocess.Popen(
            argv_a2, cwd=str(_REPO_ROOT), env=env_a, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f_a2, out_f_a2 = _open_guest_fifo_pair(in_fifo_a2, out_fifo_a2)
        _drain(out_f_a2, settle=0.6, overall=10.0)
        _send_guest(in_f_a2, "gast-erschaffung-dialog operator1")
        retry_a2_out = _drain(out_f_a2, settle=0.8, overall=15.0)
        joined_retry_a2 = "".join(retry_a2_out)
        assert "durch einen adressierten Betreiber-Stop beendet (terminal)" in joined_retry_a2, joined_retry_a2
        assert "keine Erschaffungsanfrage/-freigabe fuer guest_id='operator1'" not in joined_retry_a2, (
            joined_retry_a2
        )
        assert not (run_dir_a / "current_saves" / "guest1.json").exists(), (
            "T4A: frischer Retry ueber die echte Gast-FIFO (guest1) darf keinen Current-Write erzeugen."
        )
        _send_op(proc_a2, "beenden")
        stdout_a2, stderr_a2 = proc_a2.communicate(timeout=30)
        utc_end_a2 = _utc(time.time())
        in_f_a2.close()
        out_f_a2.close()
        _record_background_run(
            szene, "t4a_fresh_process_retry_respects_stop", argv_a2, str(_REPO_ROOT),
            utc_start_a2, utc_end_a2, proc_a2.returncode, stdout_a2, stderr_a2,
        )
        assert proc_a2.returncode == 0, f"T4A: frischer Retry-Prozess ist unerwartet gescheitert: {stderr_a2}"

        utc_end_a = _utc(time.time())
        _send_op(proc_a, "beenden")
        stdout_a, stderr_a = proc_a.communicate(timeout=30)
        in_f_a.close()
        out_f_a.close()
        _record_background_run(
            szene, "t4a_operator_and_guest_dialog_stopped_mid_request", argv_a, str(_REPO_ROOT),
            utc_start_a, utc_end_a, proc_a.returncode, stdout_a, stderr_a,
        )
        assert proc_a.returncode == 0, f"T4A: echter Launcher-Lauf ist unerwartet fehlgeschlagen: {stderr_a}"

        _export_tree(szene, run_dir_a, "t4a_run")
        _export_file(szene, calls_log_a, "t4a_gm_calls.jsonl")
        _write_export_json(szene, "t4a_io_transcript.json", {"final_tail": joined_final_tail})

        # ========== T4-B: Stop NACH Annahme (idempotente Fertigstellung,
        # Versionsbestand bleibt bei 1) ================================
        op_data_b = root / "opB_data"
        run_dir_b = root / "runB"
        states_dir_b = root / "statesB"
        fifo_dir_b = root / "fifosB"
        fifo_dir_b.mkdir(parents=True)
        in_fifo_b1 = fifo_dir_b / "guest_in_1.fifo"
        out_fifo_b1 = fifo_dir_b / "guest_out_1.fifo"
        calls_log_b = root / "gm_calls_b.jsonl"
        cfg_path_b = root / "gmdouble_cfg_b.json"

        write_test_profile(run_dir_b, max_turns=200)
        char_id_b = "CHR-T4B-GAST"
        final_block_b = full_v7_save(char_id_b, name="GastT4B", save_id="fixture-t4b-guest-001")
        q1_b, q2_b = "Wie nennt sich dein Chrononaut?", "Was ist ihr Ursprung?"
        final_content_b = "```json\n" + json.dumps(final_block_b, ensure_ascii=False) + "\n```"
        _write_gm_double_config(cfg_path_b, responses=[q1_b, q2_b, final_content_b], calls_log=calls_log_b)
        env_b = _gm_double_env(cfg_path_b)

        # Prozess 1 (gebundene Skriptdatei, Klassen-Monkeypatch GENAU
        # ZWISCHEN den beiden Publikationsschritten): echter mehrschrittiger
        # Dialog bis zur ECHTEN Annahme (onboarding.complete_with_save real
        # erfolgt), dann os._exit(94) VOR Katalog-/Current-Veroeffentlichung.
        argv_b1 = [
            sys.executable, "-B", str(_HARDEXIT_BETWEEN_PUBLICATION),
            "--participant", "operator2", "--data-dir", str(op_data_b),
            "--run-dir", str(run_dir_b), "--states-dir", str(states_dir_b),
            "--guest-terminal", f"guest2:{in_fifo_b1}:{out_fifo_b1}",
        ]
        utc_start_b1 = _utc(time.time())
        proc_b1 = subprocess.Popen(
            argv_b1, cwd=str(_REPO_ROOT), env=env_b, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f_b1, out_f_b1 = _open_guest_fifo_pair(in_fifo_b1, out_fifo_b1)
        _drain(out_f_b1, settle=0.6, overall=10.0)
        _send_guest(in_f_b1, "gast-erschaffung-anfragen operator2")
        _drain(out_f_b1, settle=0.6, overall=10.0)
        _send_op(proc_b1, "gast-erschaffung-annehmen guest2")
        time.sleep(0.6)
        grant_b_before = creation_grants.grant_status(run_dir_b, "guest2")
        assert grant_b_before["status"] == "approved" and grant_b_before["generation"] == 1, grant_b_before

        _send_guest(in_f_b1, "gast-erschaffung-dialog operator2")
        _wait_for_marker(out_f_b1, f"[SL] {q1_b}", overall=15.0)
        _send_guest(in_f_b1, "Mira")
        _wait_for_marker(out_f_b1, f"[SL] {q2_b}", overall=15.0)
        _send_guest(in_f_b1, "Ein Forscherteam.")

        stdout_b1, stderr_b1 = proc_b1.communicate(timeout=30)
        utc_end_b1 = _utc(time.time())
        in_f_b1.close()
        out_f_b1.close()
        _record_background_run(
            szene, "t4b_proc1_dialog_completed_hard_exit_before_finish", argv_b1, str(_REPO_ROOT),
            utc_start_b1, utc_end_b1, proc_b1.returncode, stdout_b1, stderr_b1,
        )
        assert proc_b1.returncode == 94, (
            f"T4B: Prozess 1 muss ueber os._exit(94) enden (NACH onboarding.complete_with_save, VOR "
            f"_finish_granted_guest_creation) -- rc={proc_b1.returncode} stderr={stderr_b1!r}"
        )

        guest_onboarding_b = op_data_b / "guests" / "guest2" / "onboarding"
        guest_catalog_b = op_data_b / "guests" / "guest2" / "catalog"
        onboarding_key_b = creation_grants.guest_onboarding_key("guest2", 1)
        state_b1 = onboarding.peek(guest_onboarding_b, onboarding_key_b)
        assert state_b1 is not None and state_b1.status == "completed", state_b1
        assert state_b1.final_save == final_block_b, "T4B: der angenommene Save muss real uebernommen sein (Phase 1)."
        assert catalog.list_for_participant(guest_catalog_b, "guest2") == [], (
            "T4B: Phase 2 (Publikation) darf NICHT erreicht worden sein."
        )
        guestB_current_path = run_dir_b / "current_saves" / "guest2.json"
        assert not guestB_current_path.exists()
        before_inventory_b = {
            "onboarding_status": state_b1.status, "final_save_present": True,
            "catalog_entries": 0, "current_save_exists": False,
        }

        # Prozess 2 (frisch, literaler Launcher): G4/B3b -- 'gast-
        # erschaffung-abbrechen' darf die bereits angenommene Figur NICHT
        # mehr verwerfen; idempotente Fertigstellung (0 neue GM-Calls).
        in_fifo_b2 = fifo_dir_b / "guest_in_2.fifo"
        out_fifo_b2 = fifo_dir_b / "guest_out_2.fifo"
        argv_b2 = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator2", "--data-dir", str(op_data_b),
            "--run-dir", str(run_dir_b), "--states-dir", str(states_dir_b),
            "--guest-terminal", f"guest2:{in_fifo_b2}:{out_fifo_b2}",
        ]
        proc_b2 = subprocess.Popen(
            argv_b2, cwd=str(_REPO_ROOT), env=env_b, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        utc_start_b2 = _utc(time.time())
        in_f_b2, out_f_b2 = _open_guest_fifo_pair(in_fifo_b2, out_fifo_b2)
        _drain(out_f_b2, settle=0.6, overall=10.0)
        _send_guest(in_f_b2, "gast-erschaffung-abbrechen operator2")
        abbrechen_b_out = _drain(out_f_b2, settle=0.6, overall=10.0)
        joined_abbrechen_b = "".join(abbrechen_b_out)
        assert "nicht abbrechbar" in joined_abbrechen_b and "bereits angenommen" in joined_abbrechen_b, (
            joined_abbrechen_b
        )
        state_b2 = onboarding.peek(guest_onboarding_b, onboarding_key_b)
        assert state_b2.status == "completed", "T4B: G4/B3b -- der Abbruchversuch darf die Annahme NICHT verwerfen."

        calls_b_before_finish = len(calls_log_b.read_text(encoding="utf-8").splitlines()) if calls_log_b.exists() else 0
        _send_guest(in_f_b2, "gast-erschaffung-dialog operator2")
        finish_b_out = _drain(out_f_b2, settle=0.8, overall=15.0)
        calls_b_after_finish = len(calls_log_b.read_text(encoding="utf-8").splitlines()) if calls_log_b.exists() else 0
        assert calls_b_after_finish == calls_b_before_finish, (
            "T4B: idempotente Fertigstellung braucht keinen neuen GM-Turn."
        )

        _send_op(proc_b2, "beenden")
        stdout_b2, stderr_b2 = proc_b2.communicate(timeout=30)
        utc_end_b2 = _utc(time.time())
        in_f_b2.close()
        out_f_b2.close()
        _record_background_run(
            szene, "t4b_proc2_abbrechen_denied_then_real_finish", argv_b2, str(_REPO_ROOT),
            utc_start_b2, utc_end_b2, proc_b2.returncode, stdout_b2, stderr_b2,
        )
        assert proc_b2.returncode == 0, f"T4B: Prozess 2 ist unerwartet gescheitert: {stderr_b2}"
        assert guestB_current_path.exists(), "T4B: der echte Finish-Prozess haette den Current real veroeffentlichen muessen."
        guestB_figure_path = guest_catalog_b / "figures" / f"guest2__{char_id_b}.json"
        assert guestB_figure_path.exists()
        assert catalog.list_for_participant(guest_catalog_b, "guest2") != [], joined_abbrechen_b
        catalog_entries_b1 = len(catalog.list_for_participant(guest_catalog_b, "guest2"))
        assert catalog_entries_b1 == 1, catalog_entries_b1
        published_b = store.load_current_save_or_raise(
            run_dir_b, "guest2", PersonaStateStore(schema_path=_SCHEMA_PATH), states_dir=states_dir_b,
        )
        assert published_b == final_block_b, published_b
        versions_dir_b = run_dir_b / "current_saves" / "guest2__versions"
        version_files_b1 = sorted(versions_dir_b.glob("*.json")) if versions_dir_b.exists() else []
        assert len(version_files_b1) == 1, (
            f"T4B/FIX4: nach der ERSTEN echten Fertigstellung wird GENAU 1 Version erwartet: {version_files_b1}"
        )
        sha_current_b1 = _sha256(guestB_current_path)
        sha_figure_b1 = _sha256(guestB_figure_path)

        # Prozess 3 (frisch, literaler Launcher): weiterer identischer
        # Retry -- B3/FIX4-Nachweis: Versionsbestand bleibt EXAKT 1 (NICHT
        # 2), Current-Verweis unveraendert. R4 FIX7: der Retry MUSS ECHT
        # ueber die verdrahtete GAST-FIFO (laeuft als guest2) getrieben
        # werden, NICHT ueber das Operator-stdin -- sonst bindet
        # `ensure_valid_grant` faelschlich guest_id=self.participant_id=
        # 'operator2' (kein Grant-Record je fuer diese ID), lehnt VOR dem
        # FIX4-Guard ab, und der beobachtete Versionsbestand==1 waere
        # trivial (kein echter zweiter Finish-Durchlauf).
        in_fifo_b3 = fifo_dir_b / "guest_in_3.fifo"
        out_fifo_b3 = fifo_dir_b / "guest_out_3.fifo"
        argv_b3 = [
            sys.executable, "-B", str(_LAUNCHER),
            "--participant", "operator2", "--data-dir", str(op_data_b),
            "--run-dir", str(run_dir_b), "--states-dir", str(states_dir_b),
            "--guest-terminal", f"guest2:{in_fifo_b3}:{out_fifo_b3}",
        ]
        utc_start_b3 = _utc(time.time())
        proc_b3 = subprocess.Popen(
            argv_b3, cwd=str(_REPO_ROOT), env=env_b, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        in_f_b3, out_f_b3 = _open_guest_fifo_pair(in_fifo_b3, out_fifo_b3)
        _drain(out_f_b3, settle=0.6, overall=10.0)
        calls_b_before_retry = len(calls_log_b.read_text(encoding="utf-8").splitlines()) if calls_log_b.exists() else 0
        _send_guest(in_f_b3, "gast-erschaffung-dialog operator2")
        retry_b3_out = _drain(out_f_b3, settle=0.8, overall=15.0)
        joined_retry_b3 = "".join(retry_b3_out)
        calls_b_after_retry = len(calls_log_b.read_text(encoding="utf-8").splitlines()) if calls_log_b.exists() else 0
        assert calls_b_after_retry == calls_b_before_retry, (
            "T4B/B3: identischer Retry (echter zweiter Finish-Durchlauf) braucht keinen neuen GM-Turn."
        )
        assert "kein gueltiger Betreiber-Grant" not in joined_retry_b3, joined_retry_b3
        assert "Gast-Erschaffung abgeschlossen" in joined_retry_b3, joined_retry_b3
        _send_op(proc_b3, "beenden")
        stdout_b3, stderr_b3 = proc_b3.communicate(timeout=30)
        utc_end_b3 = _utc(time.time())
        in_f_b3.close()
        out_f_b3.close()
        _record_background_run(
            szene, "t4b_proc3_identical_retry_version_count_stays_1", argv_b3, str(_REPO_ROOT),
            utc_start_b3, utc_end_b3, proc_b3.returncode, stdout_b3, stderr_b3,
        )
        assert proc_b3.returncode == 0, f"T4B: Prozess 3 ist unerwartet gescheitert: {stderr_b3}"
        version_files_b2 = sorted(versions_dir_b.glob("*.json")) if versions_dir_b.exists() else []
        assert len(version_files_b2) == 1, (
            f"T4B/B3/FIX4: identischer Retry darf KEINE zweite Version erzeugen (erwartet 1, "
            f"tatsaechlich {len(version_files_b2)}): {version_files_b2}"
        )
        assert [p.name for p in version_files_b2] == [p.name for p in version_files_b1], (
            "T4B: Current-Verweis (dieselbe Versionsdatei) muss nach identischem Retry unveraendert bleiben."
        )
        assert _sha256(guestB_current_path) == sha_current_b1, "T4B: identischer Retry hat den Current erneut geschrieben."
        assert _sha256(guestB_figure_path) == sha_figure_b1, "T4B: identischer Retry hat die Figur erneut geschrieben."
        catalog_entries_b2 = len(catalog.list_for_participant(guest_catalog_b, "guest2"))
        assert catalog_entries_b2 == 1, "T4B: weiterhin GENAU EINE Figur, kein Ersatz-/Zweiteintrag."

        # ── Export VOR Tempverzeichnis-Bereinigung.
        _export_tree(szene, run_dir_b, "t4b_run")
        _export_tree(szene, guest_onboarding_b, "t4b_guest_onboarding")
        _export_tree(szene, guest_catalog_b, "t4b_guest_catalog")
        _export_file(szene, calls_log_b, "t4b_gm_calls.jsonl")
        _write_export_json(szene, "t4b_io_transcript.json", {
            "abbrechen": joined_abbrechen_b, "finish_tail": "".join(finish_b_out),
            "proc3_retry_tail": joined_retry_b3,
        })
        _write_export_json(szene, "inventory.json", {
            "t4a_decision": decision_a, "t4a_final_tail": joined_final_tail,
            "t4a_proc2_retry_tail": joined_retry_a2,
            "t4b_before": before_inventory_b,
            "t4b_after_first_finish": {
                "catalog_entries": catalog_entries_b1, "version_files": [p.name for p in version_files_b1],
                "current_sha256": sha_current_b1, "figure_sha256": sha_figure_b1,
            },
            "t4b_after_identical_retry": {
                "catalog_entries": catalog_entries_b2, "version_files": [p.name for p in version_files_b2],
            },
            "notes": [
                "T4A: GM-Anbieter ist eine Grenzinjektion (FIX5); der Stop (echter Top-Level-Befehl "
                "'gast-erschaffung-stop guest1' ueber das reale Betreiber-stdin) wurde WAEHREND des "
                "offenen Q2-Aufrufs zugestellt (Double blockiert bis zur durablen Bestaetigung) -- "
                "s. _r4_gm_double.py '_run_stop_race'. Die spaete Q2-Antwort UND der finale Save "
                "wurden korrekt verbucht, aber NICHT publiziert ('Betreiber-Stop beendet (terminal) "
                "... kein Katalog-/Current-Write').",
                "T4A/proc2 (R4 FIX7): der frische Retry-Prozess wird ECHT ueber die verdrahtete "
                "Gast-FIFO getrieben (laeuft als guest1, NICHT ueber das Operator-stdin) -- "
                "`ensure_valid_grant` findet den echten Grant-Record (operator1/guest1), sieht den "
                "bereits gewonnenen Stop-Entscheid und lehnt mit der STOP-terminal-Meldung ab ('... "
                "durch einen adressierten Betreiber-Stop beendet (terminal) ...'), NICHT mit der "
                "trivialen 'keine Erschaffungsanfrage/-freigabe'-Meldung.",
                "T4B: Prozess 1 endet real ueber os._exit(94) (Klassen-Monkeypatch auf "
                "TuiSession._finish_granted_guest_creation, GENAU an der Abbruch-Grenze zwischen den "
                "beiden Publikationsschritten) -- kein veraenderter Produktpfad.",
                "G4/B3b real belegt: 'gast-erschaffung-abbrechen' auf einer bereits angenommenen "
                "(status=='completed') Figur verwirft NICHT mehr; die idempotente Fertigstellung "
                "(SELBER frischer Prozess) vollzieht das Publizieren real nach, mit 0 neuen GM-Calls.",
                "B3/FIX4 (R4 FIX7): Prozess 3 wird ECHT ueber die verdrahtete Gast-FIFO getrieben "
                "(laeuft als guest2) -- der Dialog resuemiert den 'completed'-Stand und erreicht "
                "`_finish_granted_guest_creation` WIRKLICH (0 neue GM-Calls, stdout zeigt den "
                "idempotenten 'Gast-Erschaffung abgeschlossen'-Pfad, NICHT die Grant-Ablehnung). Der "
                "FIX4-Lesevergleich (bereits publizierter Current == save_block) ueberspringt danach "
                "den Write real -- Versionsbestand (current_saves/guest2__versions/) zaehlt deshalb "
                "ECHT weiterhin EXAKT 1 Datei (nicht 2), Current-/Figur-SHA unveraendert.",
            ],
        })


def main() -> int:
    if _RESULTS_ROOT.exists():
        shutil.rmtree(_RESULTS_ROOT)
    _RESULTS_ROOT.mkdir(parents=True)

    scenes = [("t1", run_family_t1), ("t2", run_family_t2), ("t3", run_family_t3), ("t4", run_family_t4)]
    failed = 0
    for name, fn in scenes:
        try:
            fn()
            print(f"OK   familie_{name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL familie_{name}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR familie_{name}:")
            traceback.print_exc()

    manifest_path = _RESULTS_ROOT / "MANIFEST.json"
    manifest_path.write_text(json.dumps(_MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(scenes) - failed}/{len(scenes)} Familien bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
