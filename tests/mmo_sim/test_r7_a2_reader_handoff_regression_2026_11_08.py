#!/usr/bin/env python3
"""
tests/mmo_sim/test_r7_a2_reader_handoff_regression_2026_11_08.py --
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261108-R7 (01_NACHZUG.md A2, GENERAL-
REVIEW.md §3 "ausbleibender Aktions-/Notizprompt", 02_ABNAHME.md §A "Fuer die
vier in R6 berichteten Prompt-Timeouts ist eine belegte Ursache ... oder ein
gezielter unterscheidender Gegenfall erforderlich").

`_claim_aware_readline` (tui.py) prueft `ready = self._input_ready_fn(0.2)`
AUSSERHALB des `_terminal_read_lock` (Zeile ~1292). Danach nimmt es den Lock
und prueft NUR den Claim erneut (Zeile ~1309-1310), NICHT aber die
Eingabebereitschaft -- obwohl zwischen dem ersten Check und der
Lockuebernahme GENAU das Interleaving passieren kann, das GENERAL-REVIEW.md
§3 als "interessante statische Fehlerfolge" benennt: der privilegierte,
host-getriebene Read (`_HumanDriver.decide`, setzt seinen Claim UNTER
demselben Lock) konsumiert die urspruenglich bereite Zeile UND gibt seinen
Claim wieder frei, BEVOR dieser Thread den Lock bekommt. Der alte Code rief
dann blind `self._readline("")` -- das blockiert auf eine NEUE, noch nicht
getippte Zeile, WAEHREND der Lock gehalten bleibt (`with`-Block endet erst
bei Rueckkehr). Der naechste host-getriebene Read kann seinen eigenen Claim
dann nicht mehr setzen (derselbe Lock) und sein Aktions-/Notizprompt
erscheint nie -- genau der in `repeat-proof.txt` beobachtete Fehlerzustand.

Dieser Test bildet den kleinsten ECHTEN unterscheidenden Gegenfall nach, am
echten `TuiSession`/`_claim_aware_readline`-Code (kein Mock des Mechanismus
selbst), mit kontrollierter Thread-Orchestrierung ueber `threading.Event`
(KEIN Blind-Sleep/Timing-Raten -- jeder Zustand wird explizit synchronisiert,
Sleeps sind nur kurze Polling-Intervalle gegen bereits deterministisch
gesetzte Bedingungen, s. `_RaceFifo.ready()`):

1. Ein Menue-Thread ruft `_claim_aware_readline` auf; sein `ready()`-Aufruf
   liefert `True`, haelt dabei aber (testdoppel-kontrolliert) INNEHALB der
   Ready-Pruefung an, BEVOR er zurueckkehrt.
2. WAEHREND er dort pausiert, laeuft ein echter host-getriebener Claim-Setz-
   und -Konsum-Zyklus (derselbe Lock, dieselbe `bypass_claim=True`-Lese-
   methode wie `_HumanDriver.decide`/der Rundenleser) vollstaendig durch:
   Claim setzen, GENAU die urspruenglich bereite Zeile konsumieren, Claim
   wieder freigeben.
3. Erst DANACH liefert `ready()` sein (jetzt veraltetes) `True` an den
   Menue-Thread zurueck -- exakt das im Review beschriebene Fenster.
4. Ein ZWEITER, unabhaengiger "naechster Hostleser" versucht sofort danach,
   DENSELBEN Lock fuer sein eigenes Claim-Setzen zu bekommen (dieselbe
   Stelle wie `_HumanDriver.decide`/9459ff). OHNE den Fix haelt der
   Menue-Thread den Lock waehrend eines blockierenden Reads auf eine noch
   nicht getippte Zeile -- der zweite Hostleser wartet lange/unbegrenzt.
   MIT dem Fix erkennt der Menue-Thread die veraltete Bereitschaft (erneuter
   Poll unter dem Lock) und gibt den Lock sofort wieder frei.
5. Funktionale Kontrollprobe: sobald die ECHTE naechste Zeile eintrifft,
   liefert der Menue-Thread GENAU diese (kein Datenverlust, kein falsches
   Ergebnis, keine Dauerblockade).

Pure Python, nur `assert`, echter Exitcode, kein Modell-/GM-Call, keine
echten Betriebssystem-FIFOs/-Prozesse (reiner In-Process-Thread-Test, selbes
Vertragsmuster wie `test_r5_fix1_single_reader_claim_coordination_2026_11_07.
py`s `_FakeFifo`)."""
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


class _RaceFifo:
    """Wie `test_r5_fix1_...`s `_FakeFifo` (nicht-konsumierender `ready()` +
    konsumierender `read_line()`), ZUSAETZLICH mit einem einmaligen,
    kontrollierten Innehalten INNERHALB des ERSTEN erfolgreichen
    `ready()`-Aufrufs: der Aufrufer bekommt sein `ready=True` erst
    ausgeliefert, NACHDEM der Test-Hauptthread den `host_consumed`-Event
    gesetzt hat -- das bildet exakt das im Review beschriebene Fenster
    zwischen Bereitschafts-Check und Lockuebernahme nach, OHNE Zeiten zu
    raten (echte Event-Synchronisation, kein Blind-Sleep)."""

    def __init__(self) -> None:
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._lock = threading.Lock()
        self._peeked: str | None = None
        self._race_armed = True
        self.menu_checked_ready = threading.Event()
        self.host_consumed = threading.Event()

    def push(self, line: str) -> None:
        self._queue.put(line)

    def ready(self, timeout: float) -> bool:
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
            # Das Fenster: ready() hat die Zeile bereits gesehen/gepeekt,
            # liefert ihr Ergebnis aber erst NACH dem vollstaendigen
            # Host-Konsumzyklus zurueck.
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


def test_stale_readiness_does_not_hold_lock_and_block_next_host_claim():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guest_printed: list[str] = []
        fifo = _RaceFifo()

        guest_session = TuiSession(
            onboarding_dir=root / "guest_onboarding", catalog_dir=root / "guest_catalog",
            participant_id="gast_a2", input_fn=fifo.read_line, print_fn=guest_printed.append,
            host_capable=False, input_ready_fn=fifo.ready,
        )
        guest_session._is_registered_guest_terminal = True

        menu_result: list[str] = []
        menu_error: list[BaseException] = []
        menu_done = threading.Event()

        def _menu_thread_body() -> None:
            try:
                menu_result.append(guest_session._claim_aware_readline("Menue: "))
            except BaseException as exc:  # pragma: no cover - defensive
                menu_error.append(exc)
            finally:
                menu_done.set()

        menu_thread = threading.Thread(target=_menu_thread_body, name="a2-menu", daemon=True)
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
            "Host-Aktionsprompt: ", context="Spielzug", speaker_pid="host_a2", bypass_claim=True,
        )
        guest_session._host_terminal_claimed.clear()
        guest_session._host_terminal_claim_owner = None
        assert consumed_text == "L1_fuer_host", (
            "Der host-getriebene Read haette die urspruenglich bereite Zeile bekommen muessen.",
            consumed_text,
        )
        # Jetzt erst darf der pausierte `ready()`-Aufruf im Menue-Thread sein
        # (veraltetes) True zurueckgeben.
        fifo.host_consumed.set()

        # Der naechste Hostleser (z.B. der Notizprompt der naechsten Runde)
        # versucht sofort, DENSELBEN Lock fuer sein eigenes Claim-Setzen zu
        # bekommen -- das ist exakt die Stelle 9459ff im Produktcode.
        next_host_claimed = threading.Event()
        lock_wait_seconds: list[float] = []

        def _next_host_body() -> None:
            t0 = time.monotonic()
            with guest_session._terminal_read_lock:
                lock_wait_seconds.append(time.monotonic() - t0)
                guest_session._host_terminal_claimed.set()
                guest_session._host_terminal_claim_owner = threading.current_thread()
            next_host_claimed.set()

        next_host_thread = threading.Thread(target=_next_host_body, name="a2-next-host", daemon=True)
        next_host_thread.start()

        got_claim = next_host_claimed.wait(timeout=1.0)
        next_host_thread.join(timeout=2.0)
        assert got_claim, (
            "Der naechste Hostleser konnte seinen eigenen Claim nicht zuegig setzen -- der "
            "Menue-Thread haelt den Lock offenbar waehrend eines blockierenden Reads auf eine "
            "bereits anderweitig konsumierte Zeile (genau der beschriebene ausbleibende "
            "Aktions-/Notizprompt)."
        )
        assert lock_wait_seconds and lock_wait_seconds[0] < 0.5, lock_wait_seconds

        # Aufraeumen + funktionale Kontrollprobe: der Menue-Thread muss nach
        # Freigabe des zweiten Claims korrekt die ECHTE naechste Zeile
        # konsumieren, kein Haengenbleiben, kein falsches Ergebnis.
        guest_session._host_terminal_claimed.clear()
        guest_session._host_terminal_claim_owner = None
        fifo.push("L2_echte_naechste_menueeingabe")
        assert menu_done.wait(timeout=5.0), "Menue-Thread ist nach dem Fix nicht zurueckgekehrt."
        menu_thread.join(timeout=5.0)
        assert not menu_error, f"Menue-Thread endete mit Fehler: {menu_error}"
        assert menu_result == ["L2_echte_naechste_menueeingabe"], (
            "Der Menue-Read haette NACH der veralteten Zeile korrekt die naechste echte Zeile "
            "konsumieren muessen, nicht blind blockieren oder falsche Daten liefern.", menu_result,
        )


def test_normal_single_reader_consume_without_race_still_works():
    """Gegenprobe/normaler C-Weg (keine Regression): OHNE jedes
    Host-Interleaving liefert `_claim_aware_readline` weiterhin sofort die
    tatsaechlich bereite Zeile -- der zusaetzliche Readiness-Recheck unter
    dem Lock kostet im unbelasteten Normalfall keine Funktionalitaet."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guest_printed: list[str] = []
        fifo = _RaceFifo()
        fifo._race_armed = False  # kein Interleaving-Fenster in diesem Test

        guest_session = TuiSession(
            onboarding_dir=root / "guest_onboarding", catalog_dir=root / "guest_catalog",
            participant_id="gast_a2b", input_fn=fifo.read_line, print_fn=guest_printed.append,
            host_capable=False, input_ready_fn=fifo.ready,
        )
        guest_session._is_registered_guest_terminal = True

        fifo.push("normale_zeile")
        result = guest_session._claim_aware_readline("Menue: ")
        assert result == "normale_zeile", result


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
