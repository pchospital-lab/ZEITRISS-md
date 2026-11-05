#!/usr/bin/env python3
"""
tests/mmo_sim/drive_r5_t2_evidence_2026_11_05.py -- ZR-BETREIBER-
GASTERSCHAFFUNG-20261105-R5, Phase t1t2, T2 (STOP-BOUNDARY.md §4.2/§4.3/
§7.3, briefing/t2.md): ersetzt die T2-Nachweislücke aus R4s
`drive_r4_evidence_2026_11_04.py:run_family_t2` -- NICHT durch Patchen
dieser alten Datei (fremde Schreibzuständigkeit, Worker T1 ist parallel
daran), sondern durch einen eigenen, vollständig neuen Treiber, der dieselbe
G2-Implementierung (echter Launcher-Subprozess, FIX2/FIX6, Kontroll-FIFO,
Gast-Terminal-FIFOs) wiederverwendet.

T2 ist laut STOP-BOUNDARY.md §7-Urteil eine NACHWEIS-/Evidenzlücke, KEIN
Produktdefekt -- dieser Treiber ändert keine Zeile unter `mmo_sim/`.

Materieller Kern (§4.2): Prozess 1 wird NICHT (wie R4) an
`SectionRuntime._collect_reflections` (runtime.py:924, NACH ALLEN
Primärsaves) hart beendet, sondern über den NEUEN Helper
`_r5_t2_launcher_hardexit_in_primary_publication.py` ECHT INNERHALB
`store.complete_section`s (`store.py:1986`) Primär-Schreibsequenz
(`_resume_and_harvest`, `store.py:1719-1836`): Primärsave (`:1807`) ->
Version (`:1808`) -> Fortschrittszustand (`:1812-1818`) -> os._exit(94) --
VOR dem Completed-Guard (`:1820-1829`). Der geschriebene Primärteil UND der
ausstehende Rest werden UNMITTELBAR danach (vor jedem weiteren
Schreibschritt/Prozessstart) als Zwischenkörper exportiert.

Danach (§7.3) dieselbe Tisch-/Abschnittsentscheidung durchgehend über die
volle Normalwegkette: adressierter Stop, neuer normaler Resume, '/abbrechen'
an der freiwilligen Notiz, gehaltene Bindungen (Locks/Core-Tisch/Admission/
Guards/Versionen/Fortschritt) VOR Final als Zwischenkörper, regulärer
Abschluss + private Rückgabe, abschließender wirkungsloser identischer
Retry MIT vollem Vor-/Nach-Vergleich (Versionen/Fortschritt/Reflexionen/
privat, nicht nur Final-/Current-Hash -- die von §4.3 benannte R4-Lücke).

GM-Anbieter ist eine Grenzinjektion (FIX5, `MMO_SIM_GM_TRANSPORT_DOUBLE`) --
NIE ein Live-Modelllauf, in jeder Laufspur als solche ausgewiesen (s.
`tests/mmo_sim/_r4_gm_double.py`, wiederverwendet, nicht verändert).

LITERAL ARGV: KEIN `-c`-Platzhalter. Jeder Subprozess ist entweder der
wörtliche `scripts/mmo_sim.py`-Einstiegspunkt ODER der neue gebundene
Helper, der `scripts.mmo_sim` importiert und `sys.argv[1:]` unverändert an
`launcher.main()` durchreicht.

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import hashlib
import json
import os
import select
import shutil
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
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

_RESULTS_ROOT = Path("/home/altair/zr-betreiber-gast-20261105/r5/t1t2/t2/evidence")
_LAUNCHER = _REPO_ROOT / "scripts" / "mmo_sim.py"
_HARDEXIT_IN_PRIMARY_PUBLICATION = _HERE / "_r5_t2_launcher_hardexit_in_primary_publication.py"
_GM_DOUBLE_SPEC = "tests.mmo_sim._r4_gm_double:build"

_MANIFEST: dict = {"files": [], "runs": []}


# ───────────────────────── gemeinsame Helfer (Muster wie R4) ───────────────

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


# ───────────────────────── FIFO-/Prozessinteraktions-Helfer (Muster wie R4) ─

class _LineReader:
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
        chunk = os.read(self.fd, max_bytes)
        if chunk == b"":
            self.eof = True
            return False
        self._buf += chunk.decode("utf-8", errors="replace")
        return True

    def close(self) -> None:
        os.close(self.fd)


def _drain(reader: "_LineReader", settle: float = 0.4, overall: float = 10.0) -> list[str]:
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
    import fcntl
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


def _snapshot_held_bindings(
    run_dir: Path, states_dir: Path, table_id: str, char_id: str, completion_section_id: str,
    guard_path: Path, versions_dir: Path, progress_state_path: Path,
) -> dict:
    """Gehaltene Bindungen eines noch nicht final abgeschlossenen Abschnitts
    -- Locks, Core-Tisch, Admission(-Stop/-Entscheid), Guards, Versionen,
    Fortschritt -- ALS tatsaechliche Dateikoerper (nicht nur Existenz-Bools),
    s. STOP-BOUNDARY.md §4.3: R4 sicherte hier nur Plan/Final/Current-Hash."""
    locks_path = run_dir / "locks.json"
    table_record = table_admission.load_record(run_dir, "mesaT2")
    section = store.Table.load(run_dir, table_id)
    version_files = sorted(versions_dir.glob("*.json"))
    return {
        "locks_json": {
            "exists": locks_path.exists(),
            "sha256": _sha256(locks_path) if locks_path.exists() else None,
            "bytes": locks_path.stat().st_size if locks_path.exists() else None,
            "content": json.loads(locks_path.read_text(encoding="utf-8")) if locks_path.exists() else None,
        },
        "core_table": {
            "table_id": section.table_id, "status": section.status, "members": list(section.members),
        },
        "table_admission_record": {
            "state": table_record["state"] if table_record else None,
        },
        "admission_stop": admission.read_table_stop(run_dir, table_id),
        "admission_decision": admission.read_table_decision(run_dir, table_id),
        "chrononaut_active_binding": store.chrononaut_active_binding(run_dir, char_id),
        "completed_guard": {
            "exists": guard_path.exists(),
            "sha256": _sha256(guard_path) if guard_path.exists() else None,
            "content": json.loads(guard_path.read_text(encoding="utf-8")) if guard_path.exists() else None,
        },
        "current_save_versions": [
            {"name": p.name, "sha256": _sha256(p), "bytes": p.stat().st_size} for p in version_files
        ],
        "progress_state": {
            "exists": progress_state_path.exists(),
            "sha256": _sha256(progress_state_path) if progress_state_path.exists() else None,
            "content": json.loads(progress_state_path.read_text(encoding="utf-8")) if progress_state_path.exists() else None,
        },
    }


# ───────────────────────── Familie T2 ─────────────────────────
# STOP-BOUNDARY.md §4.2 (korrekte Innen-Grenze) + §4.3 (gehaltene Bindungen
# als echte Zwischenkoerper) + §7.3 (volle Kette inkl. vollstaendigem
# Retry-Vergleich). G2-Implementierung (FIX2/FIX6, echter Launcher-
# Subprozess, Kontroll-/Gast-FIFOs) wiederverwendet, IDs identisch zu R4s
# T2-Familie (mesaT2 / local-guest1 / local-guest1-section / guest1 /
# chrono-t2-guest).

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
        versions_dir = run_dir / "current_saves" / "guest1__versions"
        progress_state_path = states_dir / "guest1.json"

        table_id = "local-guest1"
        completion_section_id = f"{table_id}-section"
        plan_path = run_dir / "completion" / f"{completion_section_id}__plan.json"
        final_path = run_dir / "completion" / f"{completion_section_id}__final.json"
        guard_path = store._completion_guard_path(run_dir, char_id, completion_section_id)

        debrief_save = full_v7_save(char_id, name="Gast-guest1", save_id="fixture-t2-guest-002", level=2)
        debrief_text = (
            "Abschnitt beendet.\n```json\n" + json.dumps(debrief_save) + "\n```\nSECTION-ABSCHLUSS-BESTAETIGT"
        )
        _write_gm_double_config(
            cfg_path, responses=["SL-Antwort auf Anker.", debrief_text], calls_log=calls_log,
        )
        env = _gm_double_env(cfg_path)

        # ── Prozess 1 (gebundene Skriptdatei, ECHTER launcher.main()
        # importiert, Monkeypatch GENAU an der NEUEN Innen-Grenze, s.
        # `_r5_t2_launcher_hardexit_in_primary_publication.py`): echter
        # Rundenverlauf bis Plan-Pin + Primaersave + Version +
        # Fortschrittszustand -- os._exit(94) VOR dem Completed-Guard.
        argv1 = [
            sys.executable, "-B", str(_HARDEXIT_IN_PRIMARY_PUBLICATION),
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
        assert guest_current_path.exists(), "T2/R5: tisch-annehmen haette den Startsave (v0001) publizieren muessen."
        sha_guest_accept = _sha256(guest_current_path)
        version_files_accept = sorted(versions_dir.glob("*.json"))
        assert len(version_files_accept) == 1, (
            f"T2/R5: nach Annahme wird GENAU EINE Startversion erwartet: {version_files_accept}"
        )

        _send_op(proc1, "tisch-start mesaT2")
        _wait_for_marker(out_f1, "Empfaenger: Spielleitung (SL)", overall=25.0)
        _deliver_guest_turn_answer(in_f1, out_f1, "Ich erkunde die Gegend.")
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
            szene, "t2_proc1_hardexit_in_primary_publication", argv1, str(_REPO_ROOT),
            utc_start, utc_end, proc1.returncode, stdout1, stderr1,
        )
        assert proc1.returncode == 94, (
            f"T2/R5: Prozess 1 muss ueber os._exit(94) ECHT INNERHALB der Primaerpublikation enden "
            f"(nach Primaersave/Version/Fortschritt, vor dem Completed-Guard) -- "
            f"rc={proc1.returncode} stderr={stderr1!r}"
        )

        # ── SOFORTIGE Sicherung der Innen-Grenze (§4.2/Evidenz-Disziplin):
        # geschriebener Primaerteil + ausstehender Rest, GENAU an diesem
        # Zeitpunkt -- VOR jedem weiteren Schreibschritt/Prozessstart.
        assert plan_path.exists(), "T2/R5: Prozess 1 haette den Plan real pinnen muessen (vor dem Primaerschritt)."
        assert not final_path.exists(), "T2/R5: Phase 2 (__final.json) darf von Prozess 1 NICHT erreicht worden sein."
        assert not guard_path.exists(), (
            "T2/R5: der Completed-Guard darf an dieser Innen-Grenze NOCH NICHT existieren -- "
            "sonst waere die Primaerpublikation bereits VOLLSTAENDIG (wie beim R4-Boundary)."
        )
        version_files_mid = sorted(versions_dir.glob("*.json"))
        assert len(version_files_mid) == 2, (
            f"T2/R5: nach dem Debrief-Primaersave werden GENAU 2 Versionen erwartet "
            f"(Startsave + Debrief), tatsaechlich: {version_files_mid}"
        )
        direct_content_mid = json.loads(guest_current_path.read_text(encoding="utf-8"))
        assert direct_content_mid == debrief_save, (
            "T2/R5: der Primaersave (direct) muss beim Exit bereits den Debrief-Save enthalten."
        )
        assert json.loads(version_files_mid[-1].read_text(encoding="utf-8")) == debrief_save, (
            "T2/R5: die neueste Versionsdatei muss beim Exit bereits den Debrief-Save enthalten."
        )
        sha_guest_primary_mid = _sha256(guest_current_path)
        sha_version_debrief_mid = _sha256(version_files_mid[-1])
        assert progress_state_path.exists(), "T2/R5: der Fortschrittszustand muss beim Exit bereits real geschrieben sein."
        progress_state_mid = json.loads(progress_state_path.read_text(encoding="utf-8"))
        assert progress_state_mid.get("rounds_played") == 1, (
            f"T2/R5: der Fortschrittszustand muss beim Exit bereits rounds_played=1 zeigen: {progress_state_mid}"
        )
        assert progress_state_mid.get("current_save_version", {}).get("seq") == 2, (
            f"T2/R5: der Fortschrittszustand muss beim Exit bereits auf die Debrief-Version (seq=2) zeigen: "
            f"{progress_state_mid}"
        )
        kernereignis_mid = progress_state_mid.get("round_history", {}).get("1", {}).get("kernereignis", "")
        assert kernereignis_mid == f"Abschnitt {completion_section_id} am Tisch {table_id} abgeschlossen.", (
            f"T2/R5: das Erkennungsmerkmal des Helpers muss im geschriebenen Fortschritt stehen: {kernereignis_mid!r}"
        )
        decision_mid = admission.read_table_decision(run_dir, table_id)
        assert decision_mid is not None and decision_mid.get("decision") == "plan_committed", decision_mid
        sha_progress_state_mid = _sha256(progress_state_path)

        before_inventory = {
            "plan_exists": True, "final_exists": False, "guard_exists": False,
            "decision": decision_mid.get("decision"),
            "guest_current_sha256_at_accept": sha_guest_accept,
            "guest_current_sha256_after_primary_publication": sha_guest_primary_mid,
            "version_files_at_mid_boundary": [p.name for p in version_files_mid],
            "version_debrief_sha256": sha_version_debrief_mid,
            "progress_state_sha256_at_mid_boundary": sha_progress_state_mid,
            "progress_state_rounds_played": progress_state_mid.get("rounds_played"),
        }

        # Export der Zwischenkoerper AN DIESER GRENZE, vor Prozess 2.
        _export_tree(szene, run_dir, "mid_boundary_run")
        _export_tree(szene, states_dir, "mid_boundary_states")
        _write_export_json(szene, "mid_boundary_inventory.json", {
            "before_inventory": before_inventory,
            "outstanding_at_exit": [
                "Completed-Guard (store.py:_resume_and_harvest, unmittelbar nach dem Fortschritt-Write)",
                "store.return_to_lobby (runtime.py:923)",
                "SectionRuntime._collect_reflections (runtime.py:924) -- Pflicht-/freiwillige Reflexion",
                "finalize_section_after_reflection (__final.json, Lock-Release, Tisch 'closed')",
            ],
            "notes": [
                "Primaersave (direct) UND Version (0002) UND Fortschrittszustand (rounds_played=1, "
                "current_save_version.seq=2) sind beim Exit bereits real auf Platte -- der Completed-Guard "
                "fehlt noch, store._resume_and_harvest/complete_section kehrt daher NIE erfolgreich zurueck.",
            ],
        })

        # ── Prozess 2 (literaler Launcher, echter NEUER Prozess, G2-
        # Implementierung): resumiert denselben gebundenen Tisch -- der
        # offene Plan wird idempotent zu Ende geharvested (Guard wird jetzt
        # geschrieben, OHNE zweite Version/Publikation, s. Assertion unten),
        # danach die Pflicht-/freiwillige Reflexion erreicht. Betreiberstop
        # waehrend der offenen Reflexion; '/abbrechen' an der freiwilligen
        # Notiz -- bleibt ehrlich offen (EndOfInput).
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

        # An dieser Stelle muss der Resume den offenen Primaerrest idempotent
        # abgeschlossen haben: Guard jetzt vorhanden, aber KEINE dritte
        # Version/neue Publikation (der bereits real geschriebene Debrief-
        # Stand wird uebernommen, nicht neu erzeugt).
        assert guard_path.exists(), (
            "T2/R5: der echte Resume (Prozess 2) haette den ausstehenden Completed-Guard idempotent "
            "nachschreiben muessen."
        )
        version_files_after_resume = sorted(versions_dir.glob("*.json"))
        assert [p.name for p in version_files_after_resume] == [p.name for p in version_files_mid], (
            f"T2/R5: der idempotente Resume darf KEINE zusaetzliche Version erzeugen: "
            f"vorher={[p.name for p in version_files_mid]} nachher={[p.name for p in version_files_after_resume]}"
        )
        assert _sha256(guest_current_path) == sha_guest_primary_mid, (
            "T2/R5: der idempotente Resume darf den Primaersave NICHT veraendern."
        )

        # Echter Betreiberstop ueber die Kontroll-FIFO, adressiert auf
        # denselben table_id -- der gemeinsame Entscheid ist bereits
        # 'plan_committed', der Stop gewinnt daher NICHT, haelt aber die
        # durable Betreiberabsicht (keine neuen Spielzuege) fest (F3b).
        fd = os.open(str(ctrl_fifo), os.O_WRONLY)
        with os.fdopen(fd, "w") as f:
            f.write("/stop\n")
        _deadline = time.time() + 15
        stopped_mid = False
        while time.time() < _deadline:
            stopped_mid, _r = admission.read_table_stop(run_dir, table_id)
            if stopped_mid:
                break
            time.sleep(0.05)
        assert stopped_mid is True, "T2/R5: der adressierte Kontroll-FIFO-Stop wurde nicht durabel bestaetigt."
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
        assert proc2.returncode == 0, f"T2/R5: Prozess 2 ist unerwartet gescheitert: {stderr2}"
        assert not final_path.exists(), "T2/R5: '/abbrechen' an der Notiz darf NICHT finalisieren (bleibt offen)."
        assert _sha256(guest_current_path) == sha_guest_primary_mid, (
            "T2/R5: '/abbrechen' an der Notiz darf den Primaersave NICHT veraendern."
        )

        # ── §4.3: gehaltene Bindungen VOR Final als ECHTE Zwischenkoerper
        # (Locks/Core-Tisch/Admission/Guards/Versionen/Fortschritt) -- nicht
        # nur Plan/Final/Current-Hash wie bei R4.
        held_bindings = _snapshot_held_bindings(
            run_dir, states_dir, table_id, char_id, completion_section_id,
            guard_path, versions_dir, progress_state_path,
        )
        _export_tree(szene, run_dir, "held_bindings_run")
        _export_tree(szene, states_dir, "held_bindings_states")
        _write_export_json(szene, "held_bindings_before_final.json", held_bindings)

        # ── Prozess 3 (literaler Launcher, echter NEUER Prozess, G2-
        # Implementierung): derselbe Fortsetzen-Weg erreicht die REGULAERE
        # Fertigstellung -- echte freiwillige Notiz statt '/abbrechen'.
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
        _wait_for_path(final_path, overall=25.0)
        finish_out = _drain(out_f3, settle=0.6, overall=10.0)
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
        assert proc3.returncode == 0, f"T2/R5: Prozess 3 ist unerwartet gescheitert: {stderr3}"
        assert final_path.exists(), "T2/R5: der echte Fortsetzen-Prozess haette __final.json real schreiben muessen."
        sha_final = _sha256(final_path)
        sha_guest_after_finish = _sha256(guest_current_path)
        version_files_after_finish = sorted(versions_dir.glob("*.json"))

        guest_private_state = onboarding.peek(guest_onboarding, "guest1")
        assert guest_private_state is not None and guest_private_state.final_save is not None, (
            "T2/R5: die abgeschlossene Fassung haette ueber den normalen Rueckkanal in die private "
            "Gastablage geschrieben werden muessen."
        )
        reflections_path = run_dir / "reflections.jsonl"
        sha_reflections_after_finish = _sha256(reflections_path) if reflections_path.exists() else None
        progress_state_after_finish = json.loads(progress_state_path.read_text(encoding="utf-8"))
        sha_progress_state_after_finish = _sha256(progress_state_path)
        private_final_json_after_finish = json.dumps(guest_private_state.final_save, sort_keys=True)

        before_retry = {
            "final_sha256": sha_final,
            "guest_current_sha256": sha_guest_after_finish,
            "version_files": [p.name for p in version_files_after_finish],
            "version_shas": {p.name: _sha256(p) for p in version_files_after_finish},
            "progress_state_sha256": sha_progress_state_after_finish,
            "progress_state_rounds_played": progress_state_after_finish.get("rounds_played"),
            "reflections_jsonl_sha256": sha_reflections_after_finish,
            "reflections_jsonl_bytes": reflections_path.stat().st_size if reflections_path.exists() else None,
            "private_final_save_json": private_final_json_after_finish,
            "private_final_save_sha256": hashlib.sha256(private_final_json_after_finish.encode("utf-8")).hexdigest(),
        }

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
        assert result4.returncode == 0, f"T2/R5: identischer Retry-Prozess ist unerwartet gescheitert: {result4.stderr}"
        assert "Tischstart abgelehnt: Tisch 'mesaT2' ist geschlossen" in result4.stdout, result4.stdout

        # ── Voller Vor-/Nach-Vergleich ueber den letzten identischen Retry
        # (§4.3/§7.3-Luecke: nicht nur Final-/Current-Hash).
        version_files_after_retry = sorted(versions_dir.glob("*.json"))
        progress_state_after_retry = json.loads(progress_state_path.read_text(encoding="utf-8"))
        guest_private_state_after_retry = onboarding.peek(guest_onboarding, "guest1")
        private_final_json_after_retry = json.dumps(guest_private_state_after_retry.final_save, sort_keys=True)
        after_retry = {
            "final_sha256": _sha256(final_path),
            "guest_current_sha256": _sha256(guest_current_path),
            "version_files": [p.name for p in version_files_after_retry],
            "version_shas": {p.name: _sha256(p) for p in version_files_after_retry},
            "progress_state_sha256": _sha256(progress_state_path),
            "progress_state_rounds_played": progress_state_after_retry.get("rounds_played"),
            "reflections_jsonl_sha256": _sha256(reflections_path) if reflections_path.exists() else None,
            "reflections_jsonl_bytes": reflections_path.stat().st_size if reflections_path.exists() else None,
            "private_final_save_json": private_final_json_after_retry,
            "private_final_save_sha256": hashlib.sha256(private_final_json_after_retry.encode("utf-8")).hexdigest(),
        }

        assert after_retry["final_sha256"] == before_retry["final_sha256"], "T2/R5: identischer Retry hat __final.json veraendert."
        assert after_retry["guest_current_sha256"] == before_retry["guest_current_sha256"], (
            "T2/R5: identischer Retry hat den Primaersave veraendert."
        )
        assert after_retry["version_files"] == before_retry["version_files"], (
            f"T2/R5: identischer Retry hat die Versionsliste veraendert: "
            f"vorher={before_retry['version_files']} nachher={after_retry['version_files']}"
        )
        assert after_retry["version_shas"] == before_retry["version_shas"], (
            "T2/R5: identischer Retry hat mindestens eine Versionsdatei inhaltlich veraendert."
        )
        assert after_retry["progress_state_sha256"] == before_retry["progress_state_sha256"], (
            "T2/R5: identischer Retry hat den Fortschrittszustand veraendert (erwartet bytegleich)."
        )
        assert after_retry["progress_state_rounds_played"] == before_retry["progress_state_rounds_played"], (
            "T2/R5: identischer Retry hat rounds_played veraendert -- zweites Rundenereignis waere ein Doppelspiel."
        )
        assert after_retry["reflections_jsonl_sha256"] == before_retry["reflections_jsonl_sha256"], (
            "T2/R5: identischer Retry hat reflections.jsonl veraendert."
        )
        assert after_retry["private_final_save_sha256"] == before_retry["private_final_save_sha256"], (
            "T2/R5: identischer Retry hat die private Gastfassung veraendert."
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
        _write_export_json(szene, "full_retry_comparison.json", {
            "before_retry": before_retry, "after_retry": after_retry,
            "identical": {
                k: (before_retry[k] == after_retry[k]) for k in before_retry
            },
        })
        _write_export_json(szene, "inventory.json", {
            "mid_boundary_before_inventory": before_inventory,
            "held_bindings_before_final": held_bindings,
            "after_real_finish": {
                "final_exists": True, "final_sha256": sha_final,
                "guest_current_sha256": sha_guest_after_finish,
                "guest_private_final_save_present": guest_private_state.final_save is not None,
            },
            "notes": [
                "GM-Anbieter ist eine Grenzinjektion (FIX5); genau 2 GM-Calls (Anker+Debrief) -- s. "
                "gm_calls.jsonl. Prozess 2/3/4 brauchen GAR KEINEN GM-Call mehr.",
                "NEUE Innen-Grenze (§4.2): Prozess 1 endet ECHT INNERHALB store.complete_section's "
                "Primaer-Schreibsequenz (nach Primaersave/Version/Fortschritt, vor dem Completed-Guard) -- "
                "s. mid_boundary_inventory.json.",
                "Prozess 2's Resume schliesst den offenen Primaerrest idempotent ab (Guard wird "
                "nachgeschrieben, KEINE zusaetzliche Version) -- danach F3b/FIX2 wie in R4.",
                "§4.3-Nachzug: gehaltene Bindungen (Locks/Core-Tisch/Admission/Guards/Versionen/"
                "Fortschritt) wurden VOR Final als echte Dateikoerper gesichert, s. "
                "held_bindings_before_final.json.",
                "§7.3-Nachzug: der letzte identische Retry wird VOLLSTAENDIG verglichen (Versionen/"
                "Fortschritt/Reflexionen/private Fassung), nicht nur Final-/Current-Hash -- s. "
                "full_retry_comparison.json.",
            ],
        })


def main() -> int:
    if _RESULTS_ROOT.exists():
        shutil.rmtree(_RESULTS_ROOT)
    _RESULTS_ROOT.mkdir(parents=True)

    scenes = [("t2", run_family_t2)]
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
