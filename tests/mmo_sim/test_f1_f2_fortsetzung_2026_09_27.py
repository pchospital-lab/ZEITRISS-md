#!/usr/bin/env python3
"""
tests/mmo_sim/test_f1_f2_fortsetzung_2026_09_27.py — dauerhafte Regressionen
fuer die Fortsetzung am erhaltenen Headless-Teilstand (Bau-GO 2026-09-27,
ANSCHLUSSPLAN-HEADLESS.md ERGAENZUNG 3 / REVIEW-TEILSTAND.md §3+§4), F1+F2:

F1 `scripts/mmo_sim.py:main` schrieb VOR der eigentlichen Kommandosperre
   (den spaeteren `_lab_active_guard`-Aufrufen fuer `n`/`i`/`c`) bereits
   `last_participant.json` -- ein zweiter, unbewachter fruehschreibender
   Einstieg waehrend eines aktiven fremden Lab-Laufs (REVIEW-TEILSTAND.md
   Fall 05). Fix: `_foreign_active_lab_owner(data_dir)` VOR jedem Aufruf von
   `_resolve_participant_id` in `main()`.
F2 `LabRunner._acquire_lock` liess bei einer nachweislich TOTEN Lease zwei
   gleichzeitige Nachfolger BEIDE gewinnen (bedingungslose Ersetzung ist
   kein exklusiver Erwerb) UND behandelte einen strukturell UNGUELTIGEN
   Owner-Eintrag (`pid: "not-a-pid"`) faelschlich als frei ersetzbar statt
   kontrolliert gehalten. Fix: exklusives `os.rename`-basiertes Aufbrechen
   der toten Lease + Inhaltscheck nach dem Rename (kein Fremdprozess wird
   dabei jemals beendet, nur Dateien umbenannt/entfernt) + expliziter Hold
   bei strukturell ungueltigem Owner.

Echte Kindprozesse mit echten PIDs, keine Netzaufrufe, keine erfundenen
PIDs, kein Fremdprozess-Kill. Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import importlib.util
import json
import os
import select
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.lab import runner as lab_runner  # noqa: E402

_ENTRY_PATH = _REPO_ROOT / "scripts" / "mmo_sim.py"


def _load_entry():
    spec = importlib.util.spec_from_file_location("mmo_sim_f1f2_entrypoint", _ENTRY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _wait(fd):
    assert select.select([fd], [], [], 15)[0], "Kindprozess-Barriere nicht erreicht"
    return os.read(fd, 1)


def test_f1_foreign_active_lab_blocks_early_marker_write():
    """Ein ECHTER fremder Kindprozess haelt den Lab-Lock lebend (blockiert
    auf einer Pipe, kein `release()`). `main(["--data-dir", ...])` MUSS
    dann ablehnen, BEVOR `_resolve_participant_id` `last_participant.json`
    schreibt -- weder Datei noch Verzeichnis duerfen dadurch entstehen."""
    entry = _load_entry()
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        run_dir = data_dir / "run"
        gr, gw = os.pipe()
        dr, dw = os.pipe()
        child = subprocess.Popen(
            [sys.executable, "-c", (
                "import os,sys,json\n"
                "sys.path.insert(0, %r)\n"
                "from mmo_sim.lab import runner\n"
                "lab = runner.LabRunner(%r, runner.LabBudget(10, 60, 5))\n"
                "lab.start()\n"
                "os.write(%d, b'R')\n"
                "os.read(%d, 1)\n"
            ) % (str(_REPO_ROOT), str(run_dir), dw, gr)],
            pass_fds=(dw, gr),
        )
        os.close(dw)
        os.close(gr)
        try:
            _wait(dr)
            marker = data_dir / "last_participant.json"
            assert not marker.exists(), "Marker haette VOR dem Lock-Check nicht existieren duerfen"

            foreign_pid = entry._foreign_active_lab_owner(data_dir)
            assert foreign_pid == child.pid, f"erwartet {child.pid}, erhalten {foreign_pid}"

            rc = entry.main(["--data-dir", str(data_dir)])
            assert rc == 1, f"main() haette bei aktivem fremdem Lab ablehnen sollen, exit={rc}"
            assert not marker.exists(), (
                "F1-Regression: main() hat trotz aktivem fremdem Lab-Owner "
                "last_participant.json geschrieben"
            )
        finally:
            os.write(gw, b"G")
            os.close(gw)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
            os.close(dr)


def test_f1_normal_path_without_lab_still_writes_marker():
    """Normalweg OHNE aktiven Lab-Lock bleibt unveraendert (H1): ohne
    fremden Owner schreibt `_resolve_participant_id` wie zuvor."""
    entry = _load_entry()
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        assert entry._foreign_active_lab_owner(data_dir) is None
        pid1 = entry._resolve_participant_id(data_dir, None)
        pid2 = entry._resolve_participant_id(data_dir, None)
        assert pid1 == pid2, "wiederholter Aufruf ohne --participant muss denselben Teilnehmer liefern"
        assert (data_dir / "last_participant.json").is_file()


def _seed_dead_owner(run_dir: Path) -> int:
    """Startet einen ECHTEN Kindprozess, der `LabRunner.start()` real
    ausfuehrt und danach OHNE `release()` beendet (simuliert einen
    abgestuerzten Owner) -- die Lease bleibt bestehen, die PID ist danach
    nachweislich tot. Kein Fremdprozess wird getoetet; der Prozess beendet
    sich selbst regulaer."""
    proc = subprocess.run(
        [sys.executable, "-c", (
            "import os,sys,json\n"
            "sys.path.insert(0, %r)\n"
            "from mmo_sim.lab import runner\n"
            "lab = runner.LabRunner(%r, runner.LabBudget(10, 60, 5))\n"
            "lab.start()\n"
            "print(json.dumps({'pid': os.getpid()}))\n"
        ) % (str(_REPO_ROOT), str(run_dir))],
        capture_output=True, text=True, timeout=15,
    )
    assert proc.returncode == 0, proc.stderr
    old_pid = json.loads(proc.stdout)["pid"]
    try:
        os.kill(old_pid, 0)
    except ProcessLookupError:
        pass
    else:
        raise AssertionError("Seed-Owner muss nachweislich beendet sein, bevor Nachfolger starten")
    assert json.loads((run_dir / "lab.lock.json").read_text())["pid"] == old_pid
    return old_pid


def test_f2_single_dead_owner_reclaim_still_works():
    """Erhalt (G3a positive Kontrolle): ein einzelner nachweislich toter
    Owner wird weiterhin erfolgreich reklamiert."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        _seed_dead_owner(run_dir)
        lab = lab_runner.LabRunner(run_dir, lab_runner.LabBudget(10, 60, 5))
        lab.start()
        try:
            assert lab_runner.read_status(run_dir).pid == lab.pid
        finally:
            lab.release()


def test_f2_two_dead_owner_reclaimers_stay_exclusive():
    """F2-Regression (REVIEW-TEILSTAND.md §4.2), Seamanpassung ERGAENZUNG 4
    (F2-Leaseabschluss, Bau-GO 2026-09-27, REVIEW-LEASEABSCHLUSS.md §4/§5):
    zwei ECHTE Nachfolger derselben nachweislich toten Lease duerfen NICHT
    beide Erwerb melden.

    Original (s. `seam-adaptations/test_f1_f2_fortsetzung_2026_09_27.
    ORIGINAL.py`) patchte `runner.os.rename` -- den damaligen Erwerbsnachweis
    des Rename-/Rollback-Reklamationszweigs. Dieser Zweig existiert nach der
    ERGAENZUNG-4-Haertung nicht mehr (kein `os.rename` mehr in
    `_acquire_lock`, s. dortigen Docstring): ein alter Patch auf `os.rename`
    wuerde NIE mehr treffen (toter Mock, faelschlich gruen). Der ECHTE neue
    Synchronisationspunkt ist jetzt `fcntl.flock(fd, LOCK_EX|LOCK_NB)` auf
    dem Reklamationszweig (unterscheidbar vom blockierenden `LOCK_EX` des
    Frischerwerbs-Zweigs ueber das `LOCK_NB`-Flag) -- DAS ist die Stelle, an
    der echte Konkurrenz um dieselbe tote Lease jetzt tatsaechlich
    entschieden wird. Beide Kinder pausieren dort real (Trefferbeleg: jedes
    Kind schreibt sein 'R' NUR aus dem eigenen Patch-Wrapper heraus, also
    nur wenn der reale Code diesen Aufruf tatsaechlich erreicht hat), werden
    dann gleichzeitig freigegeben und rufen die ECHTE `fcntl.flock`-Syscall
    real-nebenlaeufig auf -- die Kernel-Atomaritaet von `flock`, nicht der
    Test, entscheidet den Gewinner. Erhaltene Invariante identisch zum
    Original: `acquired.count('A') == 1`."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        old_pid = _seed_dead_owner(run_dir)
        children = []
        try:
            for _ in range(2):
                rr, rw = os.pipe()
                gr, gw = os.pipe()
                dr, dw = os.pipe()
                fr, fw = os.pipe()
                child = subprocess.Popen(
                    [sys.executable, "-c", (
                        "import fcntl,os,sys,json\n"
                        "from unittest.mock import patch\n"
                        "sys.path.insert(0, %r)\n"
                        "from mmo_sim.lab import runner\n"
                        "lab = runner.LabRunner(%r, runner.LabBudget(10, 60, 5))\n"
                        "orig = runner.fcntl.flock; hits = [0]\n"
                        "def seam(fd, op, *a, **kw):\n"
                        "    if (op & fcntl.LOCK_NB) and hits[0] == 0:\n"
                        "        hits[0] += 1\n"
                        "        os.write(%d, b'R')\n"
                        "        os.read(%d, 1)\n"
                        "    return orig(fd, op, *a, **kw)\n"
                        "try:\n"
                        "    with patch.object(runner.fcntl, 'flock', seam):\n"
                        "        lab.start()\n"
                        "    os.write(%d, b'A')\n"
                        "    os.read(%d, 1)\n"
                        "except Exception as e:\n"
                        "    os.write(%d, b'X')\n"
                        "    print(type(e).__name__, str(e), file=sys.stderr)\n"
                        "finally:\n"
                        "    try:\n"
                        "        lab.release()\n"
                        "    except Exception:\n"
                        "        pass\n"
                    ) % (str(_REPO_ROOT), str(run_dir), rw, gr, dw, fr, dw)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    pass_fds=(rw, gr, dw, fr),
                )
                for fd in (rw, gr, dw, fr):
                    os.close(fd)
                children.append((child, rr, gw, dr, fw))

            ready = [_wait(c[1]).decode() for c in children]
            assert ready == ["R", "R"], "beide Nachfolger muessen den echten flock-Reklamationsseam erreichen"
            acquired = []
            for child, rr, gw, dr, fw in children:
                os.write(gw, b"G")
                acquired.append(_wait(dr).decode())

            assert acquired.count("A") == 1, (
                f"Reclaim derselben toten Lease darf nicht zwei gleichzeitig lebende Owner "
                f"erzeugen (acquired={acquired})"
            )
            lock = json.loads((run_dir / "lab.lock.json").read_text())
            assert lock["pid"] != old_pid
        finally:
            for child, rr, gw, dr, fw in children:
                try:
                    os.write(fw, b"F")
                except OSError:
                    pass
            for child, rr, gw, dr, fw in children:
                try:
                    child.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.communicate()
                for fd in (rr, gw, dr, fw):
                    os.close(fd)


def test_f2_unassignable_owner_is_held_not_reclaimed():
    """F2-Regression (REVIEW-TEILSTAND.md §4.3): ein strukturell
    UNGUELTIGER Owner-Eintrag (`pid: "not-a-pid"`, kein `int`) ist NICHT
    automatisch 'tot' -- er muss kontrolliert GEHALTEN werden (Exception),
    die Datei bleibt unveraendert, kein `lab.status.json` entsteht."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        run_dir.mkdir(parents=True)
        lock_path = run_dir / "lab.lock.json"
        lock_path.write_text(json.dumps({"pid": "not-a-pid", "evidence": "synthetic-unassignable-owner"}))
        before = lock_path.read_bytes()

        lab = lab_runner.LabRunner(run_dir, lab_runner.LabBudget(10, 60, 5))
        error = None
        try:
            lab.start()
        except Exception as e:
            error = e
        finally:
            try:
                lab.release()
            except Exception:
                pass
        assert isinstance(error, lab_runner.SingletonViolationError), (
            f"erwartet SingletonViolationError, erhalten {error!r}"
        )
        assert lock_path.read_bytes() == before, "unklare Lease darf nicht veraendert werden"
        assert not (run_dir / "lab.status.json").exists(), "kein Status fuer eine nie erworbene Lease"


if __name__ == "__main__":
    import traceback

    tests = [
        test_f1_foreign_active_lab_blocks_early_marker_write,
        test_f1_normal_path_without_lab_still_writes_marker,
        test_f2_single_dead_owner_reclaim_still_works,
        test_f2_two_dead_owner_reclaimers_stay_exclusive,
        test_f2_unassignable_owner_is_held_not_reclaimed,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} Tests bestanden.")
    sys.exit(0 if failed == 0 else 1)
