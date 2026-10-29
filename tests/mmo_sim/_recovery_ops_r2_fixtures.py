#!/usr/bin/env python3
"""
tests/mmo_sim/_recovery_ops_r2_fixtures.py — gemeinsamer Testhelper fuer
`test_recovery_ops_r2.py` (ZR-RECOVERY-OFFLINE-R2-20261015-R1). FIXTURE_ONLY,
reiner Testcode -- Produktcode kennt diese Datei nicht.

Baut auf den bestehenden R1-Fixtures (`_recovery_ops_r1_fixtures.py`) auf,
statt sie zu duplizieren -- nur die zusaetzlichen R2-spezifischen Helfer
(GATE-Statusmanipulation, Run-Identitaet, Symlink-/Sonderdateiaufbau) leben
hier."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from mmo_sim.core.admission import _atomic_write_json, _status_path

_HERE = Path(__file__).resolve().parent
import sys  # noqa: E402

if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from _recovery_ops_r1_fixtures import (  # noqa: E402,F401
    ScriptedGm, apply_p3_audit, apply_p5_grant, make_p3_unknown_request, make_p5_drift_hold,
    make_synthetic_run, never_called_gm, snapshot_tree,
)


def write_run_id(run_dir: Path, run_id: str) -> None:
    (Path(run_dir) / "run_id.json").write_text(json.dumps({"run_id": run_id}), encoding="utf-8")


def set_wall_deadline(run_dir: Path, *, seconds_from_now: float) -> None:
    """Setzt `wall_deadline` in `lab.status.json` direkt (dieselbe Datei, die
    `write_test_profile` bereits mit `provider_free=True` angelegt hat) --
    ein negativer `seconds_from_now` erzeugt ein bereits ABGELAUFENES Fenster."""
    path = _status_path(Path(run_dir))
    data = json.loads(path.read_text(encoding="utf-8"))
    data["wall_deadline"] = time.time() + seconds_from_now
    _atomic_write_json(path, data)


def set_budget_exhausted(run_dir: Path, *, max_usd: float = 0.01) -> None:
    """Setzt `max_usd`/`usd_spent` so, dass `usd_spent >= max_usd` bereits
    VOR jedem weiteren Request gilt (bekannt unzureichendes Budget)."""
    path = _status_path(Path(run_dir))
    data = json.loads(path.read_text(encoding="utf-8"))
    data["max_usd"] = max_usd
    data["usd_spent"] = max_usd
    _atomic_write_json(path, data)


def make_fifo(path: Path) -> None:
    os.mkfifo(path)


# ═══════════════ R2-N1 echter kausaler Writerbeleg (GENERALREVIEW.md §5) ═════
#
# Transparent adaptiert aus General's `review/reproduction/
# probe_actual_writer_handover.py` (ausdrueckliche Referenz, KEINE
# unveraenderliche Produkt-API, s. 05_QUELLEN_UND_REPRO.md) -- echte
# `LabRunner`/`recovery_ops`-Methoden in ZWEI echten Prozessen, an echten
# I/O-Grenzen synchron angehalten (stdin/stdout-Handshake), KEINE
# Mikrosekunden-/Zufallsannahme. `_atomic_write_json`/`Path.unlink` werden
# NUR im Kindprozess temporaer gewrapped, um GENAU an der Stelle zu pausieren,
# an der das echte Produkt ohnehin schreibt/unlinkt -- keine Produkt-
# entscheidung wird dadurch ersetzt oder monkeygepatcht, nur die Beobachtung
# synchronisiert (ersetzt die alte Mikrosekunden-/50ms-Annahme durch einen
# echten Haltepunkt). Die EINZIGE absichtliche Abweichung ist die eigene
# `sensitivity_late_write`-Phase: ein VORSAETZLICH FALSCH rekonstruierter
# Referenzablauf (alter Statuswrite NACH dem Unlink) als reine
# Sensitivitaetskontrolle -- kein Produktbug, kein Produktpatch.

WRITER_PROOF_PHASES = (
    "before_status", "before_unlink", "after_unlink", "failed_start_after_unlink", "sensitivity_late_write",
)


def _writer_proof_child_main(phase: str, run_dir_str: str) -> int:
    """Kindprozess-Rolle. Faehrt ECHTE `LabRunner.start()`/`release()`
    (bzw. den echten `_release_lock_after_failed_start()`-Cleanuppfad fuer
    `failed_start_after_unlink`) und pausiert an einer ECHTEN I/O-Grenze,
    BEVOR der jeweilige Schritt tatsaechlich passiert (`before_status`/
    `before_unlink`) bzw. UNMITTELBAR danach (`after_unlink`/
    `failed_start_after_unlink`/`sensitivity_late_write`) -- Druck auf stdout
    (`{"event": "PAUSED", ...}`) + Blockieren auf `stdin` bis `CONTINUE`."""
    import fcntl
    from mmo_sim.lab import runner as lr

    run_dir = Path(run_dir_str)
    budget = lr.LabBudget(max_turns=100, max_seconds=300, max_usd=10)
    r = lr.LabRunner(run_dir, budget)
    trace: list[dict] = []
    orig_write = lr._atomic_write_json
    orig_unlink = Path.unlink
    state = {"active": False, "paused": False}

    def pause() -> None:
        if state["paused"]:
            return
        state["paused"] = True
        st = os.fstat(r._lock_fd)
        print(json.dumps({
            "event": "PAUSED", "phase": phase, "pid": os.getpid(),
            "old_inode": st.st_ino, "old_nlink": st.st_nlink,
        }), flush=True)
        if sys.stdin.readline().strip() != "CONTINUE":
            raise RuntimeError("missing CONTINUE handshake from parent")

    def write(path, data):
        if state["active"] and path == run_dir / "lab.status.json":
            if phase == "before_status":
                pause()
            trace.append({"event": "status_write", "pid_value": data.get("pid"), "running": data.get("running")})
        return orig_write(path, data)

    def unlink(path_self, *args, **kwargs):
        target = state["active"] and path_self == run_dir / "lab.lock.json"
        if target and phase == "before_unlink":
            pause()
        out = orig_unlink(path_self, *args, **kwargs)
        if target:
            trace.append({"event": "lock_unlinked"})
            if phase in ("after_unlink", "failed_start_after_unlink", "sensitivity_late_write"):
                pause()
        return out

    lr._atomic_write_json = write
    Path.unlink = unlink
    try:
        if phase == "sensitivity_late_write":
            # Absichtlich FALSCH rekonstruierter Referenzablauf, NUR als
            # Sensitivitaetskontrolle (s. Modulkommentar oben) -- der alte
            # Statuswrite wird bewusst HINTER den Unlink verschoben (anders
            # als die echte `LabRunner.release()`, die zuerst schreibt).
            r.start()
            state["active"] = True
            fd = r._lock_fd
            data = json.loads((run_dir / "lab.status.json").read_text(encoding="utf-8"))
            data["running"] = False
            try:
                (run_dir / "lab.lock.json").unlink()
                write(run_dir / "lab.status.json", data)  # bewusst FALSCH: spaeter alter Write NACH Unlink
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
                r._lock_fd = None
        elif phase == "failed_start_after_unlink":
            # Echter `start()`-Erwerb gelingt; ein SPAETERER Schritt
            # (`_write_status()`) schlaegt fehl -- `start()`s eigener
            # `except BaseException: self._release_lock_after_failed_
            # start(); raise` (H10 Fall e, s. `runner.py`) ist der ECHTE
            # Produkt-Cleanup-Pfad dafuer; NUR dieser eine Instanzaufruf
            # wird durch `fail()` ausgeloest, keine Klassenaenderung.
            original_write_status = r._write_status

            def fail():
                original_write_status()
                raise OSError(5, "synthetic failure after initial status write")

            r._write_status = fail
            state["active"] = True
            try:
                r.start()
            except OSError:
                trace.append({"event": "expected_failed_start"})
        else:
            r.start()
            state["active"] = True
            r.release()
        assert state["paused"] and r._lock_fd is None, (state["paused"], r._lock_fd)
        print(json.dumps({"event": "DONE", "trace": trace, "lock_fd_closed": r._lock_fd is None}), flush=True)
    finally:
        lr._atomic_write_json = orig_write
        Path.unlink = orig_unlink
        if r._lock_fd is not None:
            r.release()
    return 0


def run_actual_writer_proof(*, log_dir: Path) -> dict:
    """Treibt den echten Zweiprozess-Writerbeleg fuer alle 5 Phasen
    (`WRITER_PROOF_PHASES`). Fuer jede Phase: eigener Kindprozess (dieses
    Modul, `--writer-proof-child <phase> --run <run_dir>`), Handshake bis
    zur echten Pausen-Grenze, dann versucht der Elternprozess `apply_p3` auf
    DEMSELBEN Lock -- erwartet Verweigerung (`before_status`/`before_unlink`)
    oder Erfolg (`after_unlink`/`failed_start_after_unlink`/
    `sensitivity_late_write`). Bei Erfolg startet der Elternprozess einen
    NACHFOLGER-`LabRunner` VOR dem `CONTINUE`-Handshake und vergleicht
    dessen Lease-/Statusbytes vor/nach Fortsetzung des alten Kindprozesses
    -- GENAU das ist der kausale Nachweis (Datenautoritaet, nicht bloss
    fd-Ueberlappung). Gibt `{phase: {status, expectation, observation,
    script, log}}` zurueck; echte Rohlogs unter `log_dir`."""
    import hashlib as _hashlib
    import select
    import shutil as _shutil
    import subprocess
    import sys as _sys
    import tempfile

    import mmo_sim.core.recovery_ops as recovery_ops
    from mmo_sim.lab.runner import LabBudget, LabRunner

    script_path = str(Path(__file__).resolve())
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    results: dict = {}
    expectations = {
        "before_status": "Recovery-apply wird VERWEIGERT (RecoveryExclusivityUnavailableError), solange der alte LabRunner seinen letzten Statuswrite noch nicht geschrieben hat.",
        "before_unlink": "Recovery-apply wird VERWEIGERT, solange der alte LabRunner seinen Lock noch nicht unlinkt hat.",
        "after_unlink": "Nach Unlink darf Recovery/ein neuer LabRunner beginnen; dessen Lease/Status bleiben vom alten (noch offenen) fd UNVERAENDERT.",
        "failed_start_after_unlink": "Derselbe nach-Unlink-Schutz gilt auch fuer den echten Failed-Start-Cleanuppfad (`_release_lock_after_failed_start`).",
        "sensitivity_late_write": "Sensitivitaetskontrolle: ein ABSICHTLICH FALSCH rekonstruierter Referenzablauf (alter Statuswrite NACH Unlink) MUSS von derselben Probe als Nachfolgerueberschreibung erkannt werden.",
    }
    for phase in WRITER_PROOF_PHASES:
        log_path = log_dir / f"writer_proof_{phase}.log"
        log_lines = [f"=== writer proof phase={phase} ==="]
        status = "FAIL"
        observation = ""
        with tempfile.TemporaryDirectory(prefix="SYNTHETIC-WRITER-") as td:
            run_dir = make_synthetic_run(Path(td))
            rid = make_p3_unknown_request(run_dir)
            ident = dict(
                table_id="table-1", section_id="section-1", role="gm_turn", turn_idx=1,
                participant="alice", request_id=rid,
            )
            plan = recovery_ops.plan_p3(run_dir, **ident)
            original_request_bytes = (run_dir / "requests" / f"{rid}.json").read_bytes()
            repo_root = _HERE.parents[1]
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            existing_pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = os.pathsep.join(
                p for p in (str(repo_root), str(_HERE), existing_pythonpath) if p
            )
            proc = subprocess.Popen(
                [_sys.executable, "-B", script_path, "--writer-proof-child", phase, "--run", str(run_dir)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
            )
            successor = None
            try:
                try:
                    if not select.select([proc.stdout], [], [], 15)[0]:
                        raise AssertionError(f"{phase}: Kindprozess erreichte die echte Pausen-Grenze nicht (Timeout).")
                    marker_line = proc.stdout.readline()
                    log_lines.append(f"CHILD>{marker_line.strip()}")
                    marker = json.loads(marker_line)
                    assert marker["event"] == "PAUSED", marker
                    time.sleep(0.08)
                    denied = False
                    result = None
                    try:
                        result = recovery_ops.apply_p3(
                            run_dir, **ident, operator_decision="synthetic-writer-proof",
                            reason="actual-writer-ordered-proof", evidence_ref="RC-R2N1-A", plan=plan,
                        )
                    except recovery_ops.RecoveryExclusivityUnavailableError:
                        denied = True
                    expected_deny = phase in ("before_status", "before_unlink")
                    assert denied == expected_deny, (phase, denied)
                    successor_before = None
                    if not denied:
                        assert result["status"] == "applied", result
                        successor = LabRunner(run_dir, LabBudget(max_turns=10, max_seconds=30, max_usd=1))
                        successor.start()
                        successor_before = {
                            p.name: _hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (run_dir / "lab.lock.json", run_dir / "lab.status.json")
                        }
                        assert marker["old_nlink"] == 0, marker
                    proc.stdin.write("CONTINUE\n")
                    proc.stdin.flush()
                    out, err = proc.communicate(timeout=15)
                    log_lines.append(f"CHILD-STDOUT>{out.strip()}")
                    if err.strip():
                        log_lines.append(f"CHILD-STDERR>{err.strip()}")
                    assert proc.returncode == 0, (phase, out, err)
                    done = json.loads(out.strip().splitlines()[-1])
                    assert done["event"] == "DONE", done
                    unchanged = True
                    if successor is not None:
                        after = {
                            p.name: _hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (run_dir / "lab.lock.json", run_dir / "lab.status.json")
                        }
                        unchanged = after == successor_before
                        expected_unchanged = phase != "sensitivity_late_write"
                        assert unchanged == expected_unchanged, (phase, unchanged, expected_unchanged)
                        assert successor._fd_still_matches_path(successor._lock_fd, run_dir / "lab.lock.json")
                    assert original_request_bytes == (run_dir / "requests" / f"{rid}.json").read_bytes()
                    observation = (
                        f"recovery_denied={denied}; successor_started={successor is not None}; "
                        f"successor_lease_and_status_preserved={unchanged}; "
                        f"old_nlink_at_pause={marker['old_nlink']}; trace={done.get('trace')}"
                    )
                    status = "PASS"
                finally:
                    if proc.poll() is None:
                        proc.kill()
                        proc.communicate()
                    if successor is not None:
                        successor.release()
            except Exception as exc:  # noqa: BLE001 -- echte Rohausnahme im Log, kein PASS verschleiern
                observation = f"EXCEPTION: {exc!r}"
                log_lines.append(observation)
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        results[phase] = {
            "status": status, "expectation": expectations[phase], "observation": observation,
            "script": script_path, "log": str(log_path),
        }
    return results


if __name__ == "__main__":
    # Kindprozess-Re-Exec-Einstieg fuer `run_actual_writer_proof` (s. oben) --
    # dieses Modul wird normalerweise importiert (FIXTURE_ONLY); dieser Block
    # macht KEIN automatisches Verhalten beim normalen `import`.
    if "--writer-proof-child" in sys.argv:
        _phase = sys.argv[sys.argv.index("--writer-proof-child") + 1]
        _run = sys.argv[sys.argv.index("--run") + 1]
        raise SystemExit(_writer_proof_child_main(_phase, _run))
    raise SystemExit(f"usage: {sys.argv[0]} --writer-proof-child <phase> --run <run_dir>")
