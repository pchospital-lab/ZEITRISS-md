#!/usr/bin/env python3
"""
tests/mmo_sim/test_h10_lease_ownership_matrix_2026_09_27.py — dauerhafte
H10-Besitzer-/Statusmatrix fuer den F2-Leaseabschluss (Bau-GO 2026-09-27,
ANSCHLUSSPLAN-HEADLESS.md ERGAENZUNG 4, REVIEW-LEASEABSCHLUSS.md §4-§6).

Die alte Rename-/Rollback-Reklamation (`os.rename(lock_path, stale_marker)`)
machte den kanonischen `lab.lock.json`-Pfad zeitweise LEER -- ein dritter
Start oder ein gewoehnlicher Rueckstellungsfehler konnte dieses Fenster als
freie Ablage lesen (REVIEW-LEASEABSCHLUSS.md §4/§5). Ersetzt durch EINE
echte, ununterbrochene Exklusivitaetsgrenze: eine stabile Lock-fd mit
`fcntl.flock(LOCK_EX|LOCK_NB)` als massgebliche Autoritaet (PID-JSON bleibt
rein informativ) -- s. `mmo_sim/lab/runner.py:LabRunner._acquire_lock`.

Benannte Matrix (ERGAENZUNG 4 §"H10-Matrix"), je Fall real geprueft, wer
erwerben durfte, wer lebt, canonical owner/Status, Betraege/Dedup, Verhalten
des naechsten regulaeren Starts:
(a) frischer exklusiver Erwerb
(b) Einzel-Reclaim toter Owner
(c) verzoegerter Nachfolger + dritter Start
(d) Fehler/Unterbrechung an der massgeblichen Besitzuebertragung
(e) fehlgeschlagener initialer Statuswrite
(f) alter Release gegen Nachfolger vor/nach Statuspublikation
(g) frueh gelesener Verbrauch + spaeterer Erwerb

(b)/(c)/(d) verwenden echte eigene Kindprozesse mit echten PIDs (kein
Netz/Modell, keine PID-Erfindung, kein manueller Lock-Dateiaustausch als
angeblicher natuerlicher Start). (a)/(e)/(g) sind einprozessige, deterministische
Regressionen derselben Produktinvarianten -- ihre mehrprozessige, mit echten
Barrieren synchronisierte Auspraegung von (c)/(d) UND von (f) (alter Release
vs. Nachfolger vor/nach Statuspublikation) lebt zusaetzlich in
`out/leaseabschluss-2026-09-27/worker/seam-adaptations/
review_lease_reclaim_windows.ADAPTED.py` (Faelle 02-06, 6/6 PASS) -- diese
Datei hier ist die dauerhafte, im Produktrepo verbleibende Absicherung, jene
das einmalige Review-Reproduktionsartefakt. Beide pruefen dieselbe Invariante
mit unterschiedlichem Aufwand.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import select
import tempfile
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.lab import runner as lab_runner  # noqa: E402
from mmo_sim.lab.runner import LabBudget, LabRunner, read_status  # noqa: E402


def _wait(fd, timeout=15):
    assert select.select([fd], [], [], timeout)[0], "Kindprozess-Barriere nicht erreicht"
    return os.read(fd, 1)


# --- (a) frischer exklusiver Erwerb ----------------------------------------

def test_h10_a_fresh_exclusive_acquire():
    """Erstbesitz eines vollkommen neuen `run_dir`: Erwerb gelingt, Status
    traegt die eigene PID, kein Fremdbesitz sichtbar."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        assert not (run_dir / "lab.lock.json").exists()
        lab = LabRunner(run_dir, LabBudget(10, 60, 5))
        lab.start()
        try:
            status = read_status(run_dir)
            assert status.pid == lab.pid and status.running is True
            lock = json.loads((run_dir / "lab.lock.json").read_text())
            assert lock["pid"] == lab.pid
        finally:
            lab.release()
        assert not (run_dir / "lab.lock.json").exists()
        assert read_status(run_dir).running is False


# --- (b) Einzel-Reclaim toter Owner -----------------------------------------

def test_h10_b_single_dead_owner_reclaim_full_state():
    """Ein einzelner nachweislich toter Owner wird erfolgreich reklamiert --
    ZUSAETZLICH zu `test_f2_single_dead_owner_reclaim_still_works`
    (test_f1_f2_fortsetzung_2026_09_27.py) hier: sowohl Lock ALS AUCH Status
    tragen danach ausschliesslich den neuen Owner, die alte tote PID ist
    nirgends mehr sichtbar."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        seed = subprocess.run(
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
        assert seed.returncode == 0, seed.stderr
        dead_pid = json.loads(seed.stdout)["pid"]
        try:
            os.kill(dead_pid, 0)
        except ProcessLookupError:
            pass
        else:
            raise AssertionError("Seed-Owner muss nachweislich beendet sein")

        lab = LabRunner(run_dir, LabBudget(10, 60, 5))
        lab.start()
        try:
            status = read_status(run_dir)
            lock = json.loads((run_dir / "lab.lock.json").read_text())
            assert status.pid == lab.pid != dead_pid
            assert lock["pid"] == lab.pid != dead_pid
        finally:
            lab.release()


# --- (c) verzoegerter Nachfolger + dritter Start ----------------------------

def test_h10_c_delayed_reclaimer_does_not_hide_live_owner_from_third_start():
    """Ein verzoegerter Reklamationsversuch gegen eine bereits WIEDER lebende
    Lease darf einen dritten, unabhaengigen Startversuch nicht durchlassen --
    kein Fenster, in dem der lebende Owner als frei erscheint. `slow`
    pausiert ECHT direkt vor seinem eigenen `flock(LOCK_EX|LOCK_NB)`-Versuch
    (Trefferbeleg: das Event kommt nur aus dem realen Patch-Wrapper)."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        seed = subprocess.run(
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
        assert seed.returncode == 0, seed.stderr

        # `fast` reklamiert die tote Lease vollstaendig und bleibt lebend.
        rr, rw = os.pipe(); gr, gw = os.pipe()
        fast = subprocess.Popen(
            [sys.executable, "-c", (
                "import os,sys,json\n"
                "sys.path.insert(0, %r)\n"
                "from mmo_sim.lab import runner\n"
                "lab = runner.LabRunner(%r, runner.LabBudget(10, 60, 5))\n"
                "lab.start()\n"
                "os.write(%d, b'A')\n"
                "os.read(%d, 1)\n"
                "lab.release()\n"
            ) % (str(_REPO_ROOT), str(run_dir), rw, gr)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, pass_fds=(rw, gr),
        )
        os.close(rw); os.close(gr)
        try:
            _wait(rr)  # fast acquired and holds

            # `slow` pausiert echt vor seinem eigenen flock-Reklamationsversuch.
            sr, sw = os.pipe(); sgr, sgw = os.pipe(); dr, dw = os.pipe(); fr, fw = os.pipe()
            slow = subprocess.Popen(
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
                    "        os.write(%d, b'B')\n"
                    "        os.read(%d, 1)\n"
                    "    return orig(fd, op, *a, **kw)\n"
                    "try:\n"
                    "    with patch.object(runner.fcntl, 'flock', seam):\n"
                    "        lab.start()\n"
                    "    os.write(%d, b'A')\n"
                    "except Exception as e:\n"
                    "    os.write(%d, b'X')\n"
                    "    print(type(e).__name__, str(e), file=sys.stderr)\n"
                    "os.read(%d, 1)\n"
                ) % (str(_REPO_ROOT), str(run_dir), sw, sgr, dw, dw, fr)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                pass_fds=(sw, sgr, dw, fr),
            )
            for fd in (sw, sgr, dw, fr):
                os.close(fd)
            try:
                _wait(sr)  # slow reached the real flock seam, still paused

                # dritter, unabhaengiger Startversuch WAEHREND slow pausiert.
                third = subprocess.run(
                    [sys.executable, "-c", (
                        "import os,sys,json\n"
                        "sys.path.insert(0, %r)\n"
                        "from mmo_sim.lab import runner\n"
                        "lab = runner.LabRunner(%r, runner.LabBudget(10, 60, 5))\n"
                        "try:\n"
                        "    lab.start()\n"
                        "    print(json.dumps({'acquired': True}))\n"
                        "except runner.SingletonViolationError:\n"
                        "    print(json.dumps({'acquired': False}))\n"
                    ) % (str(_REPO_ROOT), str(run_dir))],
                    capture_output=True, text=True, timeout=15,
                )
                assert third.returncode == 0, third.stderr
                third_acquired = json.loads(third.stdout)["acquired"]
                assert not third_acquired, (
                    "Ein dritter Start darf einen lebenden Owner nicht als frei sehen, "
                    "waehrend ein verzoegerter Reklamationsversuch mitten in der Ausfuehrung ist"
                )

                os.write(sgw, b"G")  # slow's real flock attempt now runs (must fail, fast holds it)
                _wait(dr)
            finally:
                try:
                    os.write(fw, b"F")
                except OSError:
                    pass
                try:
                    slow.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    slow.kill(); slow.communicate()
                for fd in (sr, sgw, dr, fw):
                    os.close(fd)

            assert json.loads((run_dir / "lab.lock.json").read_text())["pid"] == fast.pid, (
                "Die urspruengliche lebende Lease muss weiterhin massgeblich sein"
            )
        finally:
            try:
                os.write(gw, b"G")
            except OSError:
                pass
            try:
                fast.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                fast.kill(); fast.communicate()
            for fd in (rr, gw):
                os.close(fd)


# --- (d) Fehler/Unterbrechung an der massgeblichen Besitzuebertragung ------

def test_h10_d_ordinary_fault_at_commit_write_leaves_no_second_authority():
    """Ein einmaliger echter `OSError` am tatsaechlichen neuen Commit-Write
    (`os.pwrite`, NACH erfolgreichem `flock`-Erwerb einer echten toten Lease)
    darf keine zweite lebende Autoritaet eroeffnen UND den Lock nicht
    dauerhaft blockieren -- ein Folgestart muss weiterhin gelingen."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        seed = subprocess.run(
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
        assert seed.returncode == 0, seed.stderr
        before = (run_dir / "lab.lock.json").read_bytes()

        faulty = subprocess.run(
            [sys.executable, "-c", (
                "import os,sys,json\n"
                "from unittest.mock import patch\n"
                "sys.path.insert(0, %r)\n"
                "from mmo_sim.lab import runner\n"
                "lab = runner.LabRunner(%r, runner.LabBudget(10, 60, 5))\n"
                "orig = runner.os.pwrite; hits=[0]\n"
                "def faulty_pwrite(fd,data,offset,*a,**kw):\n"
                "    if not hits[0]:\n"
                "        hits[0]+=1\n"
                "        raise OSError('REVIEW_ONLY_ONE_COMMIT_WRITE_FAILURE')\n"
                "    return orig(fd,data,offset,*a,**kw)\n"
                "try:\n"
                "    with patch.object(runner.os,'pwrite',faulty_pwrite):\n"
                "        lab.start()\n"
                "    print(json.dumps({'acquired': True, 'injected': hits[0]}))\n"
                "except OSError as e:\n"
                "    print(json.dumps({'acquired': False, 'injected': hits[0], 'error': str(e)}))\n"
            ) % (str(_REPO_ROOT), str(run_dir))],
            capture_output=True, text=True, timeout=15,
        )
        assert faulty.returncode == 0, faulty.stderr
        result = json.loads(faulty.stdout)
        assert result["injected"] == 1, "Fault must reach the actual new commit write (os.pwrite)"
        assert not result["acquired"], result
        # Der ORIGINALE tote Owner-Eintrag muss unveraendert erhalten geblieben
        # sein (WRITE-vor-TRUNCATE-Reihenfolge, s. runner.py) -- kein leeres/
        # kaputtes File als Nebenwirkung des fehlgeschlagenen Commits.
        assert (run_dir / "lab.lock.json").read_bytes() == before

        third = LabRunner(run_dir, LabBudget(10, 60, 5))
        third.start()
        try:
            assert read_status(run_dir).pid == third.pid, (
                "Ein Folgestart muss nach dem injizierten Commit-Fehler weiterhin gelingen "
                "-- kein dauerhaft blockierter Lock"
            )
        finally:
            third.release()


# --- (e) fehlgeschlagener initialer Statuswrite -----------------------------

def test_h10_e_failed_initial_status_write_releases_lock_and_propagates():
    """Ein Fehler am initialen `_write_status()`-Aufruf (NACH bereits
    erfolgreichem Lock-Erwerb) muss propagieren, statt als abgeschlossener
    Besitzwechsel zu gelten -- UND darf den OS-Lock nicht dauerhaft haengen
    lassen, obwohl der Aufrufer (der `start()` als fehlgeschlagen behandelt)
    typischerweise KEIN `release()` mehr aufruft."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        lab = LabRunner(run_dir, LabBudget(10, 60, 5))
        original_write = lab_runner._atomic_write_json
        with patch.object(lab_runner, "_atomic_write_json", side_effect=OSError("INJECT initial status write")):
            try:
                lab.start()
                raise AssertionError("start() haette den injizierten Fehler propagieren muessen")
            except OSError as exc:
                assert "INJECT" in str(exc)
        assert lab._lock_fd is None, "Der OS-Lock darf nach dem Fehler nicht mehr offen sein"
        assert not (run_dir / "lab.lock.json").exists(), (
            "Die Lock-Datei darf nach einem fehlgeschlagenen initialen Statuswrite "
            "nicht zurueckbleiben (kein Fremdbesitz vorgetaeuscht)"
        )
        assert not (run_dir / "lab.status.json").exists(), "kein Status fuer einen nie abgeschlossenen Erwerb"

        # Ein Folgestart (ohne den Patch) muss trotzdem gelingen -- kein
        # dauerhaft blockierter Lock durch den fehlgeschlagenen Versuch.
        retry = LabRunner(run_dir, LabBudget(10, 60, 5))
        retry.start()
        try:
            assert read_status(run_dir).pid == retry.pid
        finally:
            retry.release()
        assert original_write is lab_runner._atomic_write_json


# --- (f) alter Release gegen Nachfolger vor/nach Statuspublikation --------

def test_h10_f_release_status_write_is_bound_to_still_held_lock():
    """`release()`s finaler Statuswrite passiert WAEHREND der OS-Lock noch
    gehalten wird -- ein Nachfolger kann strukturell nicht dazwischenfunken
    (kein Fenster, s. `LabRunner.release()`-Docstring). Regression: ein
    gewoehnlicher eigener Release+Folgestart-Zyklus liefert konsistente
    Besitzer-/Statuswerte, ohne dass der alte Owner je den neuen Status
    ueberschreibt."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        owner = LabRunner(run_dir, LabBudget(10, 60, 5))
        owner.start()
        owner.record_turn(seconds=3, usd=0.1)
        owner.release()
        after_release = read_status(run_dir)
        assert after_release.running is False and after_release.pid == owner.pid
        assert not (run_dir / "lab.lock.json").exists()

        successor = LabRunner(run_dir, LabBudget(10, 60, 5))
        successor.start()
        try:
            status = read_status(run_dir)
            assert status.running is True and status.pid == successor.pid
            # L3: der Nachfolger sieht den vom alten Owner tatsaechlich
            # gebuchten Verbrauch frisch, nicht 0/0.
            assert status.turns_used == 1
            assert abs(status.usd_spent - 0.1) < 1e-9
        finally:
            successor.release()
        final = read_status(run_dir)
        assert final.pid == successor.pid and final.running is False, (
            "Der alte Owner darf den finalen Nachfolgerstatus nie ueberschreiben"
        )


# --- (g) frueh gelesener Verbrauch + spaeterer Erwerb -----------------------

def test_h10_g_stale_constructor_snapshot_refreshed_on_later_start():
    """Ein VOR jeder Buchung konstruiertes `LabRunner`-Objekt darf nach
    seinem SPAETEREN tatsaechlichen Erwerb keine inzwischen neueren Zahlen
    ueberschreiben (L3, Fall 06) -- Konstruktion != frischer Erwerbszustand."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        early = LabRunner(run_dir, LabBudget(10, 60, 5))
        assert early._turns_used == 0 and early._usd_spent == 0.0

        owner = LabRunner(run_dir, LabBudget(10, 60, 5))
        owner.start()
        owner.record_turn(seconds=2, usd=0.05)
        owner.release()

        early.start()
        try:
            status = read_status(run_dir)
            assert status.turns_used == 1, "Fruehe Konstruktorwerte duerfen den spaeteren Erwerb nicht ueberschreiben"
            assert abs(status.usd_spent - 0.05) < 1e-9
            assert status.pid == early.pid
        finally:
            early.release()


if __name__ == "__main__":
    import traceback

    tests = [
        test_h10_a_fresh_exclusive_acquire,
        test_h10_b_single_dead_owner_reclaim_full_state,
        test_h10_c_delayed_reclaimer_does_not_hide_live_owner_from_third_start,
        test_h10_d_ordinary_fault_at_commit_write_leaves_no_second_authority,
        test_h10_e_failed_initial_status_write_releases_lock_and_propagates,
        test_h10_f_release_status_write_is_bound_to_still_held_lock,
        test_h10_g_stale_constructor_snapshot_refreshed_on_later_start,
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
