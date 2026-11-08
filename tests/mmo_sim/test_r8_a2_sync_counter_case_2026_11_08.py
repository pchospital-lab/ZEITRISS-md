#!/usr/bin/env python3
"""
tests/mmo_sim/test_r8_a2_sync_counter_case_2026_11_08.py --
ZR-VOLLENDUNG-LINUX-MINT-NACHZUG-20261108-R8 (01_NACHZUG.md R8-1a,
02_ABNAHME.md R8-1a: "Ein zeitabhaengig moeglicher gruener Altcodeablauf,
ein Reportzitat 'rot/gruen' ... genuegt nicht").

`test_r7_a2_reader_handoff_regression_2026_11_08.py` startet den
`next_host`-Konkurrenzversuch SOFORT nach `fifo.host_consumed.set()`, OHNE
zu erzwingen, dass der Menue-/Leserthread den `_terminal_read_lock` bereits
GENOMMEN und seine Claim-Recheck-Stelle PASSIERT hat (01_NACHZUG.md R8-1,
GENERAL-REVIEW.md §3: "nach host_consumed.set() ist die Reihenfolge
'Menuethread nimmt Lock + trifft Entscheidung' vs. 'next_host contendet'
NICHT erzwungen"): gewinnt `next_host` den (zu diesem Zeitpunkt noch
freien) Lock rein durch Scheduling-Zufall VOR dem Menue-Thread, setzt+loest
er seinen Claim, BEVOR der Menue-Thread dort ueberhaupt ankommt -- dann hat
NIE echte Lock-Konkurrenz stattgefunden, und der ALTE Mechanismus (ohne
Readiness-Recheck) kann genauso "gruen" wirken wie der FIXIERTE. Ein
einmal roter/gruener Lauf des bestehenden Tests beweist die Unterscheidung
deshalb NICHT (02_ABNAHME.md R8-1a).

Dieser Test schliesst GENAU diese Luecke: ein zusaetzliches, deterministisch
gesetztes Event ("der Menue-/Leserthread haelt JETZT den `_terminal_read_
lock` und hat seinen Claim-Recheck -- tui.py:1376/1377 -- passiert") wird
vom Testhauptthread ABGEWARTET, BEVOR `next_host_thread` ueberhaupt
gestartet wird. Erst danach ist die Lock-Kontention real und ausschliesslich
durch den weiteren Mechanismus entschieden (Readiness-Recheck tui.py:
1403-1408 vorhanden oder nicht) -- kein Scheduling-Zufall mehr.

Zwei Szenarien auf demselben synchronisierten Aufbau (enger isolierter
Vergleich, 02_ABNAHME.md: "Ein enger isolierter Vergleich ist erlaubt"):

  - ALT: faithful lokale Kopie von `_claim_aware_readline` (tui.py:1273-
    1411) OHNE den Readiness-Recheck 1403-1408 -- sonst identisch: Prompt,
    Claim-Loop, Claim-Recheck unter Lock, dann `self._readline("")`. Muss
    an der Lock-Grenze SICHTBAR scheitern: `next_host` bekommt seinen
    Claim NICHT innerhalb einer kurzen Frist. Das ist KEINE Zeitwette --
    die alte Kopie haelt den Lock waehrend eines blockierenden Reads auf
    eine noch nicht getippte Zeile; es gibt KEINEN Codepfad, auf dem
    `next_host` durchkommen koennte, solange L2 nicht gepusht ist (beweisbare
    Unmoeglichkeit, kein Blind-Sleep-Timing-Raten).
  - FIXIERT: der ECHTE `TuiSession._claim_aware_readline` (unveraenderter
    Produktcode) -- `next_host` bekommt seinen Claim zuegig (< Schwelle);
    danach funktionale Kontrollprobe: die echte naechste Zeile L2 wird
    korrekt konsumiert (kein Datenverlust, kein falsches Ergebnis, keine
    Dauerblockade).

Pure Python, nur `assert`, echter Exitcode, kein Modell-/GM-Call, keine
echten Betriebssystem-FIFOs/-Prozesse (reiner In-Process-Thread-Test,
dasselbe Vertragsmuster wie `test_r7_a2_reader_handoff_regression_2026_11_
08.py`s `_RaceFifo`). Der bestehende R7-Normalweg-Gegentest
`test_normal_single_reader_consume_without_race_still_works` in jener Datei
bleibt unveraendert und gruen (hier nicht beruehrt)."""
from __future__ import annotations

import queue
import sys
import threading
import time
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import tempfile  # noqa: E402

from mmo_sim.ui.tui import TuiSession  # noqa: E402


class _SyncFifo:
    """Wie `test_r7_a2_...`s `_RaceFifo` (nicht-konsumierender `ready()` +
    konsumierender `read_line()`, einmaliges kontrolliertes Innehalten im
    ERSTEN `ready()`-Aufruf ueber `host_consumed`), ZUSAETZLICH mit einem
    `recheck_probe`-Event: wird GENAU dann gesetzt, wenn `ready()` mit
    `timeout == 0` aufgerufen wird. Beim ECHTEN `_claim_aware_readline` ist
    das AUSSCHLIESSLICH der Readiness-Recheck tui.py:1404
    (`still_ready = self._input_ready_fn(0)`), der NUR innerhalb des
    bereits genommenen `_terminal_read_lock`, NACH dem bestandenen
    Claim-Recheck (1376/1377), ausgefuehrt wird -- das Event ist damit ein
    echter Beweis ('dieser Thread haelt JETZT den Lock'), kein
    Zeit-Raten."""

    def __init__(self) -> None:
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._lock = threading.Lock()
        self._peeked: str | None = None
        self._race_armed = True
        self.menu_checked_ready = threading.Event()
        self.host_consumed = threading.Event()
        self.recheck_probe = threading.Event()

    def push(self, line: str) -> None:
        self._queue.put(line)

    def ready(self, timeout: float) -> bool:
        if timeout == 0:
            # Siehe Klassendocstring: nur der Lock-interne Recheck ruft mit
            # timeout==0 auf -- an dieser Stelle haelt der Aufrufer bereits
            # den `_terminal_read_lock` und hat seinen Claim-Recheck
            # bestanden.
            self.recheck_probe.set()
        with self._lock:
            if self._peeked is not None:
                return True
        try:
            item = self._queue.get(timeout=timeout)
        except queue.Empty:
            return False
        with self._lock:
            self._peeked = item
        if self._race_armed:
            self._race_armed = False
            self.menu_checked_ready.set()
            # Dasselbe Fenster wie in `_RaceFifo`: ready() hat die Zeile
            # bereits gepeekt, liefert ihr Ergebnis aber erst NACH dem
            # vollstaendigen Host-Konsumzyklus zurueck.
            self.host_consumed.wait(timeout=5.0)
        return True

    def read_line(self, prompt: str = "") -> str:
        while True:
            with self._lock:
                if self._peeked is not None:
                    item = self._peeked
                    self._peeked = None
                    return item
            try:
                return self._queue.get(timeout=0.05)
            except queue.Empty:
                continue


def _old_mechanism_readline(session: TuiSession, prompt: str, lock_entered: threading.Event) -> str:
    """Faithful lokale Kopie des VOR-R7-Mechanismus (R6-Stand) von
    `_claim_aware_readline` (tui.py:1273-1411) -- identisch in Prompt,
    Claim-Loop und Claim-Recheck unter Lock (tui.py:1345-1377), aber OHNE
    den R7-Readiness-Recheck tui.py:1403-1408 (`still_ready =
    self._input_ready_fn(0)` / `if not still_ready: continue`). Direkt
    NACH dem bestandenen Claim-Recheck wird `lock_entered` gesetzt --
    derselbe Beweispunkt wie `_SyncFifo.recheck_probe` fuer den fixierten
    Pfad, NUR dass hier (wie im echten R6-Code) sofort blockierend
    gelesen wird, statt erneut auf Bereitschaft zu pruefen -- das ist
    GENAU der in 01_NACHZUG.md R8-1/GENERAL-REVIEW.md §3 benannte
    statische Fehler (Lock bleibt waehrend eines blockierenden Reads auf
    eine noch nicht getippte Zeile gehalten)."""
    if not session._is_registered_guest_terminal or session._input_ready_fn is None:
        return session._readline(prompt)
    if prompt:
        session._print(prompt)
    while True:
        if session._host_terminal_claimed.is_set():
            if session._host_terminal_claim_owner is threading.current_thread():
                return session._readline("")
            time.sleep(0.05)
            continue
        try:
            ready = session._input_ready_fn(0.2)
        except (OSError, ValueError):
            ready = False
        if not ready:
            continue
        with session._terminal_read_lock:
            if session._host_terminal_claimed.is_set():
                continue
            lock_entered.set()
            # R6-Stand: KEIN Readiness-Recheck -- direkt blockierend lesen,
            # WAEHREND der Lock gehalten bleibt (identisch zu tui.py VOR
            # R7, bytegleich zur echten Vorgaengerfassung von Zeile 1411).
            return session._readline("")


def _run_scenario(*, use_fixed: bool) -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guest_printed: list[str] = []
        fifo = _SyncFifo()

        guest_session = TuiSession(
            onboarding_dir=root / "guest_onboarding", catalog_dir=root / "guest_catalog",
            participant_id="gast_r8a2", input_fn=fifo.read_line, print_fn=guest_printed.append,
            host_capable=False, input_ready_fn=fifo.ready,
        )
        guest_session._is_registered_guest_terminal = True

        lock_entered = threading.Event()
        menu_result: list[str] = []
        menu_error: list[BaseException] = []
        menu_done = threading.Event()

        def _menu_thread_body() -> None:
            try:
                if use_fixed:
                    menu_result.append(guest_session._claim_aware_readline("Menue: "))
                else:
                    menu_result.append(_old_mechanism_readline(guest_session, "Menue: ", lock_entered))
            except BaseException as exc:  # pragma: no cover - defensive
                menu_error.append(exc)
            finally:
                menu_done.set()

        menu_thread = threading.Thread(target=_menu_thread_body, name="r8a2-menu", daemon=True)
        menu_thread.start()

        # Die urspruenglich bereite Zeile -- fuer den Host bestimmt, der
        # Menue-Thread hat sie nur "gesehen" (peek), noch nicht konsumiert.
        fifo.push("L1_fuer_host")
        assert fifo.menu_checked_ready.wait(timeout=5.0), (
            "Menue-Thread hat 'ready' nicht geprueft -- Testaufbau defekt."
        )

        # Echter host-getriebener Claim-Setz-/Konsum-Zyklus, GENAU wie
        # `_HumanDriver.decide`/der Rundenleser (Claim unter demselben Lock
        # setzen, ausserhalb des Locks konsumieren, danach freigeben).
        with guest_session._terminal_read_lock:
            guest_session._host_terminal_claimed.set()
            guest_session._host_terminal_claim_owner = threading.current_thread()
        consumed_text, _control = guest_session._readline_with_controls(
            "Host-Aktionsprompt: ", context="Spielzug", speaker_pid="host_r8a2", bypass_claim=True,
        )
        guest_session._host_terminal_claimed.clear()
        guest_session._host_terminal_claim_owner = None
        assert consumed_text == "L1_fuer_host", (
            "Der host-getriebene Read haette die urspruenglich bereite Zeile bekommen muessen.",
            consumed_text,
        )
        # Jetzt erst darf der pausierte `ready()`-Aufruf im Menue-Thread
        # sein (veraltetes) True zurueckgeben.
        fifo.host_consumed.set()

        # DIE Luecke, die dieser Test schliesst (01_NACHZUG.md R8-1a):
        # next_host darf ERST kontendieren, NACHDEM der Menue-/Leserthread
        # den Lock TATSAECHLICH genommen und seinen Claim-Recheck passiert
        # hat -- sonst ist die Reihenfolge Scheduling-Zufall, und beide
        # Mechanismen wirken ununterscheidbar "gruen".
        entered_event = fifo.recheck_probe if use_fixed else lock_entered
        assert entered_event.wait(timeout=5.0), (
            "Menue-Thread hat den Lock-/Claim-Recheck-Punkt nicht erreicht -- Testaufbau defekt."
        )

        next_host_claimed = threading.Event()
        lock_wait_seconds: list[float] = []

        def _next_host_body() -> None:
            t0 = time.monotonic()
            with guest_session._terminal_read_lock:
                lock_wait_seconds.append(time.monotonic() - t0)
                guest_session._host_terminal_claimed.set()
                guest_session._host_terminal_claim_owner = threading.current_thread()
            next_host_claimed.set()

        next_host_thread = threading.Thread(target=_next_host_body, name="r8a2-next-host", daemon=True)
        next_host_thread.start()

        got_claim_quickly = next_host_claimed.wait(timeout=0.5)

        if use_fixed:
            assert got_claim_quickly, (
                "FIXIERT: naechster Hostleser haette seinen Claim zuegig setzen muessen -- der "
                "Menue-Thread haelt den Lock nach dem bestandenen Readiness-Recheck NICHT mehr."
            )
            next_host_thread.join(timeout=2.0)
            assert lock_wait_seconds and lock_wait_seconds[0] < 0.5, lock_wait_seconds
        else:
            assert not got_claim_quickly, (
                "ALT: naechster Hostleser haette NICHT zuegig durchkommen duerfen -- der "
                "Menue-Thread haelt den Lock waehrend des blockierenden Reads auf eine noch "
                "nicht getippte Zeile (keine L2 vorhanden, kein Codepfad fuer einen schnellen "
                "Claim moeglich). Ein sofortiger Claim hier wuerde bedeuten, dass gar keine "
                "echte Lock-Konkurrenz stattgefunden hat -- genau die R8-1a-Luecke."
            )
            assert not next_host_claimed.is_set(), "ALT: next_host darf vor L2 nicht durchkommen."

        # Aufraeumen (fuer FIXIERT bereits durch next_host gesetzt, fuer ALT
        # ein No-op) + funktionale Kontrollprobe: der Menue-Thread muss
        # nach Freigabe des zweiten Claims korrekt die ECHTE naechste
        # Zeile konsumieren, kein Haengenbleiben, kein falsches Ergebnis.
        guest_session._host_terminal_claimed.clear()
        guest_session._host_terminal_claim_owner = None
        fifo.push("L2_echte_naechste_menueeingabe")

        assert menu_done.wait(timeout=5.0), "Menue-Thread ist nicht zurueckgekehrt."
        menu_thread.join(timeout=5.0)
        assert not menu_error, f"Menue-Thread endete mit Fehler: {menu_error}"
        assert menu_result == ["L2_echte_naechste_menueeingabe"], (
            "Der Menue-Read haette die echte naechste Zeile korrekt konsumieren muessen, kein "
            "Datenverlust, kein falsches Ergebnis.", menu_result,
        )

        # ALT: next_host war bis hierhin blockiert (Lock erst jetzt frei,
        # da der blockierende Read des Menue-Threads erst jetzt zurueck-
        # kehrt) -- bestaetigt, dass es sich nicht um einen Dauerblock
        # handelte, sondern GENAU um die beschriebene Verzoegerung bis zur
        # naechsten echten Eingabe.
        assert next_host_claimed.wait(timeout=5.0), (
            "next_host haette spaetestens nach Lockfreigabe seinen Claim bekommen muessen."
        )
        next_host_thread.join(timeout=2.0)


def test_old_mechanism_blocks_next_host_at_lock_boundary():
    """ALT (R6, ohne Readiness-Recheck tui.py:1403-1408): next_host wird
    waehrend des blockierenden Reads am Lock aufgehalten -- genau die in
    GENERAL-REVIEW.md §3 benannte ausbleibende Aktions-/Notizprompt-Grenze."""
    _run_scenario(use_fixed=False)


def test_fixed_mechanism_releases_lock_for_next_host():
    """FIXIERT (echter Produktcode `TuiSession._claim_aware_readline`):
    next_host bekommt seinen Claim zuegig; danach korrekte Kontrollprobe
    fuer die echte naechste Zeile."""
    _run_scenario(use_fixed=True)


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
