#!/usr/bin/env python3
"""
tests/mmo_sim/test_h10_fresh_vs_reclaim_race_2026_09_27.py — dauerhafte
Regression fuer den End-Critic-Befund CRITIC-REPORT.md §2
(taskName leaseabschluss_end_critic, 2026-09-27): eine vom Worker-Matrix
(test_h10_lease_ownership_matrix_2026_09_27.py, Faelle a-g) NICHT abgedeckte
Race zwischen dem Frischerwerbszweig UND dem Reklamationszweig derselben
`LabRunner._acquire_lock`.

Befund (vor der Nacharbeit): der Frischerwerbszweig macht ZWEI getrennte
Syscalls ohne gemeinsame Atomaritaet -- `os.open(O_CREAT|O_EXCL)` (Datei
existiert danach, aber NIEMAND haelt noch einen `flock` darauf), dann erst
der EIGENE `fcntl.flock(fd, LOCK_EX)`-Aufruf (ohne LOCK_NB, kann blockieren).
Ein GLEICHZEITIGER Reklamationsversuch eines ANDEREN Prozesses sieht die
Datei bereits existieren, faellt regulaer in den Reklamationszweig
(`os.open(..., O_RDWR)` + `fcntl.flock(fd, LOCK_EX|LOCK_NB)`) und kann diesen
NICHT-blockierenden `flock` GEWINNEN, weil der Frischerwerber seinen eigenen
(blockierenden) `flock` noch nicht aufgerufen hat. Gibt der Reklamierer
danach regulaer frei (unlinkt die Datei), entsperrt sich der urspruengliche
Frischerwerber zwar erfolgreich, haelt danach aber nur noch eine
"geisterhafte" fd (der Verzeichniseintrag zeigt inzwischen auf eine ANDERE
oder GAR KEINE Inode mehr) -- ein DRITTER, ganz normaler Start kann den
(wieder leeren) kanonischen Pfad parallel ebenfalls frisch erwerben: zwei
gleichzeitig erfolgreiche Owner, exakt die von L1 verbotene Situation.

Fix (Nacharbeit nach CRITIC-REPORT.md §2): nach JEDEM `flock`-Erwerb (beide
Zweige) verifiziert `LabRunner._fd_still_matches_path()` per `st_dev`/
`st_ino`-Abgleich, dass die eigene fd noch dem AKTUELLEN Pfadeintrag
entspricht. Bei Abweichung wird die fd verworfen und der GESAMTE Erwerb
(`while True`-Schleife in `_acquire_lock`) neu versucht, statt blind mit
einer potenziell veralteten fd fortzufahren.

Dieser Test haelt den Frischerwerber-Prozess A ECHT an genau der kritischen
Stelle an (Pipe-Barriere direkt VOR seinem eigenen `fcntl.flock(fd,
LOCK_EX)`-Aufruf im Frischerwerbszweig, per `unittest.mock.patch.object` auf
`runner.fcntl.flock` -- identische Technik wie die uebrigen H10-Faelle (c)/
(d) in `test_h10_lease_ownership_matrix_2026_09_27.py`, nur auf den ANDEREN
Zweig angewendet), damit die tatsaechliche Kernel-Race deterministisch
beobachtbar wird, statt auf zufaellige Scheduler-Praeemption zu hoffen. Alle
Locks/Writes/Opens sind ECHT, kein Mock von `flock`s Rueckgabewert.

Erwartungshaltung MIT dem Fix: B gewinnt weiterhin (das ist unvermeidlich --
die Race-Luecke selbst kann nicht geschlossen werden, nur ihre Konsequenz);
A erkennt nach seinem verspaeteten `flock`-Erwerb die geisterhafte fd,
verwirft sie und versucht den GESAMTEN Erwerb neu (jetzt ohne erneute Pause,
der Seam feuert nur beim ersten Treffer) -- A schliesst dadurch selbst
erfolgreich einen FRISCHEN Erwerb ab. Ein DANACH gestarteter dritter Prozess
C darf den jetzt von A lebend gehaltenen Lock NICHT mehr als frei sehen.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

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


def _wait(fd, timeout=15):
    r, _, _ = select.select([fd], [], [], timeout)
    assert r, "Kindprozess-Barriere nicht rechtzeitig erreicht (Timeout)"
    data = os.read(fd, 1)
    assert data, "Kindprozess-Pipe unerwartet geschlossen (Prozess vermutlich abgestuerzt)"
    return data


def test_h10_fresh_vs_reclaim_race_closed_by_inode_retry():
    """CRITIC-REPORT.md §2: kein doppelter lebender Owner mehr, wenn ein
    Reklamierer einen pausierten Frischerwerber ueberholt und wieder
    freigibt, bevor dessen eigener `flock`-Aufruf zurueckkehrt."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"

        # --- Prozess A: Frischerwerb, pausiert ECHT vor seinem eigenen
        # flock(LOCK_EX) OHNE LOCK_NB (Frischerwerbszweig) -----------------
        a_ready_r, a_ready_w = os.pipe()
        a_go_r, a_go_w = os.pipe()
        a_done_r, a_done_w = os.pipe()
        a_fin_r, a_fin_w = os.pipe()
        proc_a = subprocess.Popen(
            [sys.executable, "-c", (
                "import fcntl,os,sys,json\n"
                "from unittest.mock import patch\n"
                "sys.path.insert(0, %r)\n"
                "from mmo_sim.lab import runner\n"
                "lab = runner.LabRunner(%r, runner.LabBudget(10, 60, 5))\n"
                "orig = runner.fcntl.flock; hits = [0]\n"
                "def seam(fd, op, *a, **kw):\n"
                "    if not (op & fcntl.LOCK_NB) and hits[0] == 0:\n"
                "        hits[0] += 1\n"
                "        os.write(%d, b'R')\n"
                "        os.read(%d, 1)\n"
                "    return orig(fd, op, *a, **kw)\n"
                "try:\n"
                "    with patch.object(runner.fcntl, 'flock', seam):\n"
                "        lab.start()\n"
                "    os.write(%d, json.dumps({'acquired': True, 'pid': os.getpid()}).encode())\n"
                "except Exception as e:\n"
                "    os.write(%d, json.dumps({'acquired': False, 'error': type(e).__name__}).encode())\n"
                "os.read(%d, 1)\n"
            ) % (str(_REPO_ROOT), str(run_dir), a_ready_w, a_go_r, a_done_w, a_done_w, a_fin_r)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            pass_fds=(a_ready_w, a_go_r, a_done_w, a_fin_r),
        )
        os.close(a_ready_w); os.close(a_go_r); os.close(a_done_w); os.close(a_fin_r)

        try:
            _wait(a_ready_r)  # A hat Datei erstellt (O_CREAT|O_EXCL), pausiert VOR eigenem flock
            assert (run_dir / "lab.lock.json").exists()

            # --- Prozess B: normaler (ungepatchter) Reklamationsversuch,
            # WAEHREND A pausiert ------------------------------------------
            proc_b = subprocess.run(
                [sys.executable, "-c", (
                    "import os,sys,json\n"
                    "sys.path.insert(0, %r)\n"
                    "from mmo_sim.lab import runner\n"
                    "lab = runner.LabRunner(%r, runner.LabBudget(10, 60, 5))\n"
                    "try:\n"
                    "    lab.start()\n"
                    "    print(json.dumps({'acquired': True, 'pid': os.getpid()}))\n"
                    "    lab.release()\n"
                    "except runner.SingletonViolationError as e:\n"
                    "    print(json.dumps({'acquired': False, 'error': str(e)}))\n"
                ) % (str(_REPO_ROOT), str(run_dir))],
                capture_output=True, text=True, timeout=15,
            )
            assert proc_b.returncode == 0, f"B crashed: {proc_b.stderr}"
            b_result = json.loads(proc_b.stdout)
            assert b_result["acquired"] is True, (
                "B muss den unbelegten flock gewinnen, waehrend A vor seinem "
                "eigenen Aufruf pausiert -- das ist die Race-Luecke selbst, "
                "die dieser Test bewusst ausnutzt, um die FOLGE zu pruefen"
            )
            assert not (run_dir / "lab.lock.json").exists(), (
                "B muss regulaer freigeben+unlinken, bevor A fortgesetzt wird"
            )

            # --- A freigeben: sein blockierter flock(LOCK_EX)-Aufruf darf
            # jetzt (nach B's release) durchlaufen -------------------------
            os.write(a_go_w, b"G")
            a_msg = _wait(a_done_r, timeout=15)
            more = b""
            while select.select([a_done_r], [], [], 0.2)[0]:
                chunk = os.read(a_done_r, 4096)
                if not chunk:
                    break
                more += chunk
            a_result = json.loads((a_msg + more).decode())
            assert a_result["acquired"] is True, (
                "Mit dem Fix muss A nach Erkennen der geisterhaften fd "
                f"selbst einen frischen Retry-Erwerb abschliessen: {a_result}"
            )
            assert (run_dir / "lab.lock.json").exists()
            lock_after_a = json.loads((run_dir / "lab.lock.json").read_text())
            assert lock_after_a["pid"] == a_result["pid"], (
                "Der Lock nach A's Retry-Erwerb muss A's eigene (neue) PID tragen"
            )

            # --- Dritter Prozess C: regulaerer Startversuch NACH A's
            # (jetzt echtem, frischem) Erwerb --------------------------------
            proc_c = subprocess.run(
                [sys.executable, "-c", (
                    "import os,sys,json\n"
                    "sys.path.insert(0, %r)\n"
                    "from mmo_sim.lab import runner\n"
                    "lab = runner.LabRunner(%r, runner.LabBudget(10, 60, 5))\n"
                    "try:\n"
                    "    lab.start()\n"
                    "    print(json.dumps({'acquired': True, 'pid': os.getpid()}))\n"
                    "except runner.SingletonViolationError as e:\n"
                    "    print(json.dumps({'acquired': False, 'error': str(e)}))\n"
                ) % (str(_REPO_ROOT), str(run_dir))],
                capture_output=True, text=True, timeout=15,
            )
            assert proc_c.returncode == 0, f"C crashed: {proc_c.stderr}"
            c_result = json.loads(proc_c.stdout)
            assert c_result["acquired"] is False, (
                "Ein dritter Start darf A's frischen Retry-Erwerb NICHT als "
                f"frei sehen -- kein doppelter lebender Owner: {c_result}"
            )
            assert not (bool(a_result["acquired"]) and bool(c_result["acquired"])), (
                "Kern-Invariante (L1): niemals zwei gleichzeitig erfolgreiche Owner"
            )
        finally:
            try:
                os.write(a_fin_w, b"F")
            except OSError:
                pass
            try:
                proc_a.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                proc_a.kill(); proc_a.communicate()
            for fd in (a_ready_r, a_go_w, a_done_r, a_fin_w):
                try:
                    os.close(fd)
                except OSError:
                    pass


if __name__ == "__main__":
    import traceback

    tests = [
        test_h10_fresh_vs_reclaim_race_closed_by_inode_retry,
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
