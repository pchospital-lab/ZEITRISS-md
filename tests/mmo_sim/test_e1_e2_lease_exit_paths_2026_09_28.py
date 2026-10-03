#!/usr/bin/env python3
"""
tests/mmo_sim/test_e1_e2_lease_exit_paths_2026_09_28.py — dauerhafte
Regression fuer die Lease-Ausgaenge-Nacharbeit E1+E2 (Bau-GO 2026-09-28,
ANSCHLUSSPLAN-HEADLESS.md ERGAENZUNG 5, REVIEW-LEASE-AUSGAENGE.md §4+§5).

Permanente Fassung von `review_lease_exit_paths.py` (Review-Reproduktions-
artefakt, 1 PASS / 3 FAIL vor dem Fix, 4/4 danach) -- diese Datei hier
bleibt dauerhaft im Produktrepo, das Reviewskript ist das einmalige
Belegartefakt.

E1 (`LabRunner.release()` UND `LabRunner._release_lock_after_failed_start()`):
der bedingte `unlink` der Lock-Datei war bisher an eine bereits VERALTETE
PID-Lesung NACH der eigenen `flock`-Freigabe gebunden -- ein Nachfolger
konnte zwischen Freigabe und Unlink bereits erfolgreich erwerben, sodass
der alte Unlink dessen frische Lease entfernte (zwei lebende Owner). Fix:
der Unlink passiert jetzt WAEHREND die eigene `flock`-Autoritaet noch
gehalten wird, `flock(LOCK_UN)`+`close` folgen als letzter Schritt danach.

E2 (`LabRunner._acquire_lock`): ein `OSError` (z.B. EIO) an den Schritten
NACH dem eigenen erfolgreichen `flock`-Erwerb (Inode-Abgleich, `os.pread`)
propagierte bisher UNGEFANGEN nach oben und liess die bereits geoeffnete+
gesperrte fd weder geschlossen noch als `self._lock_fd` uebergeben zurueck
-- eine fuer `release()` unerreichbare, bis zum zufaelligen Prozessende
gehaltene Sperre. Fix: ein gemeinsames `try`/`except BaseException` um
jeden Post-flock-Schritt in beiden Zweigen (frisch/Reklamation), das die
fd auf JEDEM Fehlerpfad zuverlaessig freigibt.

Fall 01 (positiv): beendeter Owner wird reklamiert, ein lebender Besitzer
weist einen gleichzeitigen Contender ab, Release+Folgeerwerb funktioniert.
Fall 02 (E1/release): ein verzoegerter echter Unlink nach normalem Release
darf keine bereits erfolgreich gestartete Nachfolgerlease entfernen.
Fall 03 (E1/failed-start-cleanup): ein echter `OSError` am initialen
Status-Tempwrite loest denselben Cleanup-Unlink-Pfad aus -- der Startfehler
bleibt sichtbar, der verzoegerte Unlink schadet trotzdem keinem Nachfolger.
Fall 04 (E2): je ein einmaliger echter `OSError(EIO)` an `os.stat` (frischer
Erwerb), `os.stat` (Reklamation) und `os.pread` (Reklamation) darf keine
unerreichbare eigene Sperre hinterlassen -- ein gesunder Zweitprozess muss
erwerben koennen, WAEHREND der fehlgeschlagene Aufrufer noch lebt.

Fall 05 (E2-Nacharbeit, Bau-GO 2026-09-28, REVIEW-ERWERBSABBRUCH.md §4,
permanente Fassung von `review_lease_signal_boundary.py`): der Reclaim-
Erstversuch (`os.open(O_RDWR)` -> `fcntl.flock(LOCK_EX|LOCK_NB)`) deckte
bisher NUR `OSError` ab. Ein ECHTES `SIGINT` GENAU an der Rueckkehrgrenze
des tatsaechlich ERFOLGREICHEN `flock` (kein gefaelschtes Kernelresultat)
erzeugt `KeyboardInterrupt` -- das ist kein `OSError` und propagierte bisher
UNGEFANGEN, ohne die soeben erworbene `flock`-Autoritaet freizugeben oder
die fd zu schliessen: eine fuer `release()` unerreichbare Sperre, obwohl der
fehlgeschlagene Aufrufer `KeyboardInterrupt` faengt, oeffentliches
`release()` aufruft und weiterlebt. Fix: eine zusaetzliche `except
BaseException`-Stufe NACH `except OSError` an genau dieser ersten
Rueckkehrgrenze -- gibt eine ggf. bereits gehaltene Autoritaet frei,
schliesst die fd, reicht die Originalausnahme UNVERAENDERT weiter (kein
Umdeuten in `SingletonViolationError`). Die begleitende frische
Erwerbsvariante (bereits vorher durch den gemeinsamen `except BaseException`
um den gesamten Frischerwerb-Block geschuetzt) bleibt als Regressionsschutz
im selben Testpaar erhalten.

Echte Kindprozesse mit echten PIDs, echter `fcntl.flock`-Kernel-Lock (NICHT
gemockt), Pipes ausschliesslich als Zeitbarriere. Kein Loeschen einer
Produktlease durch den Test selbst, keine erfundene PID, kein Fremdprozess-
Kill (nur eigene Kindprozesse im `finally`). Pure Python, nur `assert`,
echter Exitcode."""
from __future__ import annotations

import argparse
import errno
import json
import os
import select
import signal
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _emit(**kw):
    print(json.dumps(kw), flush=True)


def _child_main(args):
    """Kindprozess-Modus (`--child <mode>`): diese Datei fuehrt sich selbst
    als Subprozess erneut aus (wie `review_lease_exit_paths.py`), damit
    jeder Test echte, unabhaengige PIDs und einen echten Kernel-`flock`
    verwendet -- kein Mock von `fcntl.flock` selbst, nur gezielte, real
    getroffene I/O-Seams (`Path.unlink`, `os.stat`, `os.pread`)."""
    from mmo_sim.lab import runner as r

    run = Path(args.run_dir).resolve()
    lab = r.LabRunner(run, r.LabBudget(100, 600, 5))
    lock = run / "lab.lock.json"
    mode = args.child

    if mode in ("owner", "seed"):
        try:
            lab.start()
            _emit(event="result", acquired=True, pid=os.getpid())
        except Exception as e:
            _emit(event="result", acquired=False, pid=os.getpid(),
                  error=type(e).__name__, detail=str(e))
        command = sys.stdin.readline().strip()
        if command == "release":
            lab.release()
        return

    if mode in ("release_unlink", "failed_start_unlink"):
        original_unlink = Path.unlink
        original_write = Path.write_text
        hits = 0
        status_write_hits = 0

        def unlink_seam(path, *a, **kw):
            nonlocal hits
            if Path(path) == lock and hits == 0:
                hits += 1
                _emit(event="before_unlink", pid=os.getpid(), hits=hits,
                      descriptor_owned=lab._lock_fd is not None)
                assert sys.stdin.readline().strip() == "continue", "missing barrier release"
            return original_unlink(path, *a, **kw)

        def status_write_failure(path, *a, **kw):
            nonlocal status_write_hits
            if Path(path).parent == run and Path(path).name.startswith("lab.status.json.tmp-"):
                status_write_hits += 1
                raise OSError(errno.EIO, "SYNTHETIC_INITIAL_STATUS_TEMP_WRITE_IO")
            return original_write(path, *a, **kw)

        if mode == "release_unlink":
            lab.start()
            _emit(event="started", acquired=True, pid=os.getpid())
            assert sys.stdin.readline().strip() == "release"
            with patch.object(Path, "unlink", unlink_seam):
                lab.release()
            _emit(event="complete", pid=os.getpid(), hits=hits)
        else:
            with patch.object(Path, "unlink", unlink_seam), patch.object(Path, "write_text", status_write_failure):
                try:
                    lab.start()
                except OSError as e:
                    _emit(event="complete", pid=os.getpid(), hits=hits,
                          error=type(e).__name__, detail=str(e), status_write_hits=status_write_hits)
                else:
                    _emit(event="unexpected_start", pid=os.getpid())
        sys.stdin.readline()
        return

    if mode in ("stat_failure", "pread_failure"):
        hits = 0
        original_stat, original_pread = r.os.stat, r.os.pread

        def stat_seam(path, *a, **kw):
            nonlocal hits
            if not isinstance(path, int) and Path(path) == lock and hits == 0:
                hits += 1
                raise OSError(errno.EIO, "SYNTHETIC_POST_FLOCK_STAT_IO")
            return original_stat(path, *a, **kw)

        def pread_seam(fd, *a, **kw):
            nonlocal hits
            if hits == 0:
                hits += 1
                raise OSError(errno.EIO, "SYNTHETIC_POST_FLOCK_PREAD_IO")
            return original_pread(fd, *a, **kw)

        selected = (
            patch.object(r.os, "stat", stat_seam)
            if mode == "stat_failure"
            else patch.object(r.os, "pread", pread_seam)
        )
        try:
            with selected:
                lab.start()
        except Exception as e:
            # Ein vernuenftiger Aufrufer versucht auch den oeffentlichen
            # Cleanup; dieser hat aktuell (E2-Fix bereits gegriffen) keine
            # fd mehr zu tun, aber muss gefahrlos aufrufbar bleiben.
            lab.release()
            _emit(event="start_failed", pid=os.getpid(), error=type(e).__name__,
                  detail=str(e), hits=hits, recorded_fd=lab._lock_fd)
        else:
            _emit(event="unexpected_start", pid=os.getpid(), hits=hits)
        sys.stdin.readline()
        return

    if mode == "signal_interrupt":
        # E2-Nacharbeit (Fall 05): echter Kernel-`flock`, echtes `SIGINT` an
        # die eigene PID -- kein gefaelschtes Ergebnis, keine gefaelschte
        # PID. Der Seam ruft ZUERST den echten `fcntl.flock` auf; ERST nach
        # dessen Erfolg (LOCK_EX-Bit gesetzt, erster Treffer) wird das
        # Signal gesendet -- exakt an der Rueckkehrgrenze, die vorher (nur
        # im Reklamationszweig) ungeschuetzt war.
        real_flock = r.fcntl.flock
        hits = 0

        def flock_seam(fd, op):
            nonlocal hits
            value = real_flock(fd, op)
            if op & r.fcntl.LOCK_EX and hits == 0:
                hits += 1
                os.kill(os.getpid(), signal.SIGINT)
            return value

        signal.signal(signal.SIGINT, signal.default_int_handler)
        caught = None
        try:
            with patch.object(r.fcntl, "flock", flock_seam):
                lab.start()
        except BaseException as e:
            caught = type(e).__name__
        lab.release()  # oeffentlicher Cleanup muss genuegen -- kein Testzugriff auf versteckte fd
        _emit(event="signal_result", pid=os.getpid(), error=caught, hits=hits,
              recorded_fd=lab._lock_fd)
        sys.stdin.readline()
        return

    raise ValueError(mode)


class _Peer:
    """Ein echter Kindprozess (Subprozess dieser Datei im `--child`-Modus),
    JSON-Zeilen-IPC ueber stdio."""

    def __init__(self, run, mode):
        self.proc = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--run-dir", str(run), "--child", mode],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
            env={
                **{k: os.environ[k] for k in ("PATH", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH") if k in os.environ},
                "PYTHONDONTWRITEBYTECODE": "1",
            },
        )

    def recv(self, timeout=15):
        if not select.select([self.proc.stdout], [], [], timeout)[0]:
            raise RuntimeError(f"child barrier timeout pid={self.proc.pid}")
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError(f"child exited: {self.proc.stderr.read()}")
        return json.loads(line)

    def send(self, msg):
        self.proc.stdin.write(msg + "\n")
        self.proc.stdin.flush()

    def alive(self):
        return self.proc.poll() is None

    def close(self):
        if self.alive():
            try:
                self.send("exit")
                self.proc.wait(timeout=3)
            except (OSError, subprocess.TimeoutExpired):
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                    self.proc.wait()
        self.proc.stdin.close()
        self.proc.stdout.close()
        self.proc.stderr.close()


def _snapshot(run):
    out = {}
    for name in ("lab.lock.json", "lab.status.json"):
        path = run / name
        if path.exists():
            try:
                out[name] = json.loads(path.read_text())
            except (ValueError, OSError) as e:
                out[name] = {"read_error": str(e)}
        else:
            out[name] = None
    return out


def _seed_dead(run):
    """Ein echter Kindprozess, der erfolgreich erwirbt und dann OHNE
    `release()` beendet wird (nachweislich toter, nicht sauber freigegebener
    Owner -- der Kernel gibt dessen `flock` automatisch beim Prozessende
    frei)."""
    p = _Peer(run, "seed")
    try:
        result = p.recv()
        assert result["acquired"]
        p.send("exit")
        p.proc.wait(timeout=5)
        try:
            os.kill(result["pid"], 0)
        except ProcessLookupError:
            pass
        else:
            raise AssertionError("seed muss nachweislich beendet sein")
        return result
    finally:
        p.close()


# --- Fall 01: beendeter Owner, lebender Besitzer, Contender, Folgeerwerb --

def test_fall01_terminated_owner_reclaim_then_living_owner_rejects_contender():
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "run"
        run.mkdir()
        seed = _seed_dead(run)

        peers = []
        try:
            a = _Peer(run, "owner")
            peers.append(a)
            owner = a.recv()
            assert owner["acquired"] and owner["pid"] != seed["pid"], (
                "Reklamation eines nachweislich beendeten Owners muss gelingen"
            )

            b = _Peer(run, "owner")
            peers.append(b)
            contender = b.recv()
            assert not contender["acquired"], (
                "Ein gleichzeitiger Contender gegen einen lebenden Besitzer muss abgelehnt werden"
            )

            held = _snapshot(run)
            assert held["lab.lock.json"]["pid"] == owner["pid"]
            assert held["lab.status.json"]["pid"] == owner["pid"]

            a.send("release")
            a.proc.wait(timeout=5)
            assert not (run / "lab.lock.json").exists()

            c = _Peer(run, "owner")
            peers.append(c)
            successor = c.recv()
            assert successor["acquired"]
            final = _snapshot(run)
            assert final["lab.status.json"]["pid"] == successor["pid"]
        finally:
            for p in reversed(peers):
                p.close()


# --- Fall 02 (E1/release): verzoegerter Unlink darf Nachfolger nicht entfernen --

def test_fall02_e1_release_late_unlink_must_not_remove_successor_lease():
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "run"
        run.mkdir()
        peers = []
        try:
            a = _Peer(run, "release_unlink")
            peers.append(a)
            started = a.recv()
            assert started["event"] == "started" and started["acquired"]
            a.send("release")
            stage = a.recv()
            assert stage["event"] == "before_unlink", (
                "release() muss die Lock-Datei ueber Path.unlink entfernen -- "
                "dieser Test greift genau an diesem realen Aufruf"
            )
            assert stage["descriptor_owned"] is True, (
                "E1: zum Zeitpunkt des Unlink-Aufrufs muss die eigene flock-Autoritaet "
                "noch bestehen (self._lock_fd noch gesetzt)"
            )

            before_successor = _snapshot(run)
            assert before_successor["lab.lock.json"] is not None

            b = _Peer(run, "owner")
            peers.append(b)
            contender = b.recv()
            assert not contender["acquired"], (
                "E1: solange der alte Owner die eigene flock-Autoritaet waehrend des "
                "verzoegerten Unlink noch haelt, darf ein Contender nicht erwerben"
            )

            a.send("continue")
            complete = a.recv()
            assert complete["event"] == "complete"
            # `a` blockiert danach noch auf einer letzten `sys.stdin.readline()`
            # (Kindprozess-Protokoll) -- kein `proc.wait()` hier, das erledigt
            # `a.close()` im `finally` unten (sendet 'exit', wartet dann).

            after_old = _snapshot(run)
            assert after_old["lab.lock.json"] is None, "der alte Owner muss seine eigene Lease entfernen"

            c = _Peer(run, "owner")
            peers.append(c)
            successor = c.recv()
            assert successor["acquired"], "nach dem alten Release muss ein regulaerer Folgeerwerb gelingen"
            assert not (contender["acquired"] and successor["acquired"] and b.alive() and c.alive()), (
                "kein doppelter lebender Besitz durch den verzoegerten Unlink"
            )
        finally:
            for p in reversed(peers):
                p.close()


# --- Fall 03 (E1/failed-start-cleanup): Cleanup-Unlink darf Nachfolger nicht schaden --

def test_fall03_e1_failed_start_cleanup_unlink_does_not_harm_successor():
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "run"
        run.mkdir()
        peers = []
        try:
            a = _Peer(run, "failed_start_unlink")
            peers.append(a)
            stage = a.recv()
            assert stage["event"] == "before_unlink", (
                "der Fehler-Cleanup (_release_lock_after_failed_start) muss ueber denselben "
                "realen Path.unlink-Aufruf laufen"
            )
            assert stage["descriptor_owned"] is True, (
                "E1: auch im Fehler-Cleanup muss die eigene flock-Autoritaet beim Unlink noch bestehen"
            )

            b = _Peer(run, "owner")
            peers.append(b)
            contender = b.recv()
            assert not contender["acquired"], (
                "waehrend der fehlgeschlagene Aufrufer seine eigene Autoritaet noch haelt, "
                "darf kein Contender erwerben"
            )

            a.send("continue")
            complete = a.recv()
            assert complete["event"] == "complete"
            assert complete["hits"] == 1
            assert complete["status_write_hits"] == 1, "die Injektion muss den echten initialen Statuswrite treffen"
            assert complete["error"] == "OSError"
            # `a` blockiert danach noch auf einer letzten `sys.stdin.readline()`
            # (Kindprozess-Protokoll) -- kein `proc.wait()` hier, das erledigt
            # `a.close()` im `finally` unten (sendet 'exit', wartet dann).

            assert not (run / "lab.lock.json").exists(), "der fehlgeschlagene Erwerb darf keine Lease hinterlassen"
            assert not (run / "lab.status.json").exists(), "kein Status fuer einen nie abgeschlossenen Erwerb"

            c = _Peer(run, "owner")
            peers.append(c)
            successor = c.recv()
            assert successor["acquired"], "ein Folgestart nach dem Fehler-Cleanup muss weiterhin gelingen"
        finally:
            for p in reversed(peers):
                p.close()


# --- Fall 04 (E2): I/O-Fehler nach eigenem flock darf keine unerreichbare Sperre hinterlassen --

def _io_case(run, mode, seeded):
    peers = []
    out = {}
    try:
        if seeded:
            out["seed"] = _seed_dead(run)
        a = _Peer(run, mode)
        peers.append(a)
        out["failed_start"] = a.recv()
        assert out["failed_start"]["event"] == "start_failed" and out["failed_start"]["hits"] == 1, out
        assert out["failed_start"]["recorded_fd"] is None, (
            "E2: nach einem Fehler in _acquire_lock darf self._lock_fd nie gesetzt bleiben"
        )
        b = _Peer(run, "owner")
        peers.append(b)
        out["retry_while_failed_caller_alive"] = b.recv()
        out["failed_caller_alive"] = a.alive()
        assert out["failed_caller_alive"], "der fehlgeschlagene Aufrufer muss weiterleben (kein Fremdprozess-Kill)"
        return out
    finally:
        for p in reversed(peers):
            p.close()


def test_fall04_e2_fresh_stat_io_does_not_leak_unreachable_lock():
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "run"
        run.mkdir()
        out = _io_case(run, "stat_failure", seeded=False)
        assert out["retry_while_failed_caller_alive"]["acquired"], (
            "ein gesunder Zweitprozess muss erwerben koennen, waehrend der an os.stat "
            "(frischer Erwerb) gescheiterte Aufrufer noch lebt -- keine unerreichbare Sperre"
        )


def test_fall04_e2_reclaim_stat_io_does_not_leak_unreachable_lock():
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "run"
        run.mkdir()
        out = _io_case(run, "stat_failure", seeded=True)
        assert out["retry_while_failed_caller_alive"]["acquired"], (
            "ein gesunder Zweitprozess muss erwerben koennen, waehrend der an os.stat "
            "(Reklamation) gescheiterte Aufrufer noch lebt -- keine unerreichbare Sperre"
        )


def test_fall04_e2_reclaim_pread_io_does_not_leak_unreachable_lock():
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "run"
        run.mkdir()
        out = _io_case(run, "pread_failure", seeded=True)
        assert out["retry_while_failed_caller_alive"]["acquired"], (
            "ein gesunder Zweitprozess muss erwerben koennen, waehrend der an os.pread "
            "(Reklamation) gescheiterte Aufrufer noch lebt -- keine unerreichbare Sperre"
        )


# --- Fall 05 (E2-Nacharbeit): echtes SIGINT an der flock-Rueckkehrgrenze --
# darf keine unerreichbare Sperre hinterlassen -- oeffentliches Folge-
# verhalten (nicht nur `_lock_fd is None`): der fehlgeschlagene Aufrufer
# lebt weiter, blockiert danach keinen gesunden Nachfolger, und waehrend
# dieser Nachfolger haelt, wird ein weiterer Contender weiterhin abgelehnt.

def _signal_case(run, seeded):
    peers = []
    out = {}
    try:
        if seeded:
            out["seed"] = _seed_dead(run)
        a = _Peer(run, "signal_interrupt")
        peers.append(a)
        out["failed"] = a.recv()
        assert out["failed"]["event"] == "signal_result"
        assert out["failed"]["hits"] == 1, (
            "das SIGINT muss genau einmal an der echten flock-Rueckkehr greifen"
        )
        assert out["failed"]["error"] == "KeyboardInterrupt", (
            "KeyboardInterrupt muss unveraendert erkennbar bleiben -- kein Umdeuten "
            "in SingletonViolationError oder eine andere Fehlerklasse"
        )
        assert out["failed"]["recorded_fd"] is None, (
            "self._lock_fd darf nach dem Fehlerpfad nicht gesetzt bleiben"
        )

        b = _Peer(run, "owner")
        peers.append(b)
        out["successor"] = b.recv()
        out["failed_caller_alive"] = a.alive()
        assert out["failed_caller_alive"], (
            "der fehlgeschlagene Aufrufer muss weiterleben (kein Fremdprozess-Kill)"
        )
        assert out["successor"]["acquired"], (
            "ein gesunder Nachfolger muss trotz weiterlebendem fehlgeschlagenem Aufrufer "
            "erwerben koennen -- die vom Signal betroffene eigene fd/Sperre darf nach dem "
            "Cleanup keinen gesunden Erwerb unsichtbar blockieren"
        )

        c = _Peer(run, "owner")
        peers.append(c)
        out["contender"] = c.recv()
        assert not out["contender"]["acquired"], (
            "waehrend der gesunde Nachfolger lebt und haelt, muss ein weiterer Contender "
            "weiterhin abgelehnt werden -- die normale Ablehnung eines lebenden Owners bleibt "
            "durch den Fix unveraendert"
        )
        return out
    finally:
        for p in reversed(peers):
            p.close()


def test_fall05_e2_fresh_signal_boundary_regression_unchanged():
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "run"
        run.mkdir()
        _signal_case(run, seeded=False)


def test_fall05_e2_reclaim_signal_boundary_closes_descriptor_and_unblocks_healthy_start():
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "run"
        run.mkdir()
        _signal_case(run, seeded=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir")
    parser.add_argument("--child")
    parsed = parser.parse_args()
    if parsed.child:
        _child_main(parsed)
        raise SystemExit(0)

    tests = [
        test_fall01_terminated_owner_reclaim_then_living_owner_rejects_contender,
        test_fall02_e1_release_late_unlink_must_not_remove_successor_lease,
        test_fall03_e1_failed_start_cleanup_unlink_does_not_harm_successor,
        test_fall04_e2_fresh_stat_io_does_not_leak_unreachable_lock,
        test_fall04_e2_reclaim_stat_io_does_not_leak_unreachable_lock,
        test_fall04_e2_reclaim_pread_io_does_not_leak_unreachable_lock,
        test_fall05_e2_fresh_signal_boundary_regression_unchanged,
        test_fall05_e2_reclaim_signal_boundary_closes_descriptor_and_unblocks_healthy_start,
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
