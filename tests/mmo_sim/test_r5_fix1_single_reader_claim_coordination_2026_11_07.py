#!/usr/bin/env python3
"""
tests/mmo_sim/test_r5_fix1_single_reader_claim_coordination_2026_11_07.py --
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R5 (Arbeitsblock 1 Punkt 2/3, F1/
UX-R4-01: "Der Gastkanal hat im Tischuntermenue und an der Abschlusskarte
konkurrierende Leser").

Vorher las `_cmd_menu_tisch()` (Tisch-Untermenue) und der Abschlusskarten-
Dispatcher (`_dispatch_completion_card_choice`) IMMER direkt (`self.
_readline(prompt)`), OHNE die bestehende Claim-/Lock-Koordination
(`_host_terminal_claimed`, `_terminal_read_lock`) zu pruefen oder zu setzen
-- ein gleichzeitig lebender Gast-Menue-Loop-Thread (derselbe FIFO-
Eingabekanal) konnte deshalb genau die Zeile konsumieren, die eigentlich fuer
den host-getriebenen Karten-/Untermenue-Read bestimmt war (R4-RETURN-CODE-
EVIDENCE-REVIEW.md F1, PLAYER-UX-REVIEW.md UX-R4-01).

Dieser Test belegt am ECHTEN `TuiSession`-Code (kein Mock des Claim-
Mechanismus selbst), mit einer EINFACHEN In-Process-FIFO-Simulation
(threadsicherer, nicht-konsumierender `ready()`-Check + konsumierender
`read_line()`, dasselbe Vertragsmuster wie `scripts/mmo_sim.py`s
`_FifoInputReader` fuer den echten Produktionscode -- hier ohne echte
Betriebssystem-FIFO, um den Test schnell/portabel zu halten):

1. Ein Gast-Thread sitzt bereits im normal erreichbaren Tisch-Untermenue
   (`_cmd_menu_tisch()`, claimbewusster Read) und wartet auf eine Zeile.
2. WAEHREND er wartet, claimt der Host-Thread das Terminal und liest ueber
   den Abschlusskarten-Dispatcher (`_dispatch_completion_card_choice`,
   `bypass_claim=True`) GENAU EINE Zeile -- diese Zeile MUSS beim Karten-
   Dispatcher ankommen, NICHT beim parallel wartenden Gast-Menue-Loop.
3. Nach Karte+Folgeaktion (hier: derselbe `io._cmd_menu_tisch()`-Aufruf als
   Folgeaktion, verschachtelt unter demselben gehaltenen Claim) gibt der
   Host den Claim wieder frei -- der urspruengliche, die ganze Zeit
   geparkte Gast-Thread konsumiert DANACH kontrolliert seine eigene naechste
   Zeile ('/zurueck') und kehrt geordnet zurueck (Fokus-Ruckgabe).

Pure Python, nur `assert`, echter Exitcode, kein Modell-/GM-Call, keine
echten Betriebssystem-FIFOs/-Prozesse (reiner In-Process-Thread-Test)."""
from __future__ import annotations

import queue
import sys
import threading
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


class _FakeFifo:
    """Minimaler In-Process-Ersatz fuer `scripts/mmo_sim.py`s echte
    `_FifoInputReader`: `ready(timeout)` prueft NICHT-konsumierend (wie der
    echte select-basierte Check), `read_line(prompt)` konsumiert GENAU EINE
    Zeile. Dasselbe Vertragsmuster, nur ohne echte OS-FIFO -- der Claim-
    Mechanismus selbst (den dieser Test prueft) ist UNVERAENDERT der echte
    Produktionscode aus `mmo_sim/ui/tui.py`."""

    def __init__(self) -> None:
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._lock = threading.Lock()
        self._peeked: str | None = None

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
        return True

    def read_line(self, prompt: str = "") -> str:
        # Pollt mit kurzen Timeouts statt EINES unbegrenzten `get()` --
        # sonst koennte ein gleichzeitiger `ready()`-Aufruf (anderer Thread)
        # den Weckruf der zugrundeliegenden `queue.Queue` "stehlen" (nur
        # EIN Consumer wird je `put()` geweckt) und dieser Aufruf wuerde
        # dann fuer immer blockieren, obwohl die Zeile bereits (im `_peeked`-
        # Puffer des anderen Aufrufs) angekommen ist. Reiner Testdoppel-
        # Kunstgriff -- der echte Produktionscode (`_claim_aware_readline`)
        # hat dieses Problem nicht (er ruft `ready()` IMMER vor dem
        # konsumierenden `_input`-Aufruf, nie parallel von zwei Stellen).
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


def test_card_reader_and_live_guest_submenu_reader_do_not_race_same_channel():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        host_printed: list[str] = []
        guest_printed: list[str] = []
        fifo = _FakeFifo()

        host_session = TuiSession(
            onboarding_dir=root / "host_onboarding", catalog_dir=root / "host_catalog",
            participant_id="betreiber_fix1", print_fn=host_printed.append, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=root / "guest_onboarding", catalog_dir=root / "guest_catalog",
            participant_id="gast_fix1", input_fn=fifo.read_line, print_fn=guest_printed.append,
            host_capable=False, input_ready_fn=fifo.ready,
        )
        host_session.register_guest_terminal("gast_fix1", guest_session)

        guest_entered_submenu = threading.Event()
        guest_returned = threading.Event()
        guest_error: list[BaseException] = []

        def _guest_thread_body() -> None:
            try:
                guest_entered_submenu.set()
                guest_session._cmd_menu_tisch()
            except BaseException as exc:  # pragma: no cover - defensive
                guest_error.append(exc)
            finally:
                guest_returned.set()

        guest_thread = threading.Thread(target=_guest_thread_body, name="guest-fix1-test", daemon=True)
        guest_thread.start()
        # Der Gast-Thread muss WIRKLICH im Untermenue-Read parken, bevor der
        # Host claimt -- sonst waere das kein echter Beleg der Koordination.
        assert guest_entered_submenu.wait(timeout=5.0), "Gast-Thread ist nicht gestartet."
        import time as _time
        for _ in range(50):
            if "Tisch -- [1] Offene Tische suchen" in "\n".join(guest_printed):
                break
            _time.sleep(0.02)
        else:
            raise AssertionError("Gast-Thread hat das Tisch-Untermenue nicht sichtbar gedruckt.")

        handler_calls: list[str] = []
        actions: list[tuple[str, object]] = [
            ("Testaktion (host-geklaimt)", lambda: handler_calls.append("handled")),
        ]

        # Host claimt UND liest -- die FIFO ist zu diesem Zeitpunkt noch
        # LEER; erst JETZT (nach dem Claim-Setzen) kommt die Zeile an. Ohne
        # den R5-FIX1-Claim wuerde der bereits wartende Gast-Thread diese
        # Zeile ebenso gut haben koennen (echte Rennbedingung vor dem Fix).
        push_thread = threading.Timer(0.1, fifo.push, args=("1",))
        push_thread.start()
        host_session._dispatch_completion_card_choice(guest_session, actions)
        push_thread.join()

        assert handler_calls == ["handled"], (
            "Der host-geklaimte Kartenread haette die Zeile '1' konsumieren und den Handler "
            "ausloesen muessen -- stattdessen", handler_calls,
        )
        assert not guest_returned.is_set(), (
            "Der parallel wartende Gast-Menue-Loop haette die fuer den Host bestimmte Zeile NICHT "
            "konsumieren/zurueckkehren duerfen (Claim haette ihn parken muessen)."
        )

        # Fokus-Ruckgabe (01_NACHZUG.md Arbeitsblock 1 Punkt 2): nach Karte
        # (keine weitere Folgeaktion in `actions` hier) ist der Claim wieder
        # frei -- der urspruenglich parkende Gast-Thread konsumiert jetzt
        # KONTROLLIERT seine eigene naechste Zeile und kehrt geordnet zurueck.
        fifo.push("/zurueck")
        assert guest_returned.wait(timeout=5.0), (
            "Der Gast-Menue-Loop haette nach Freigabe des Claims seine eigene Zeile konsumieren "
            "und zurueckkehren muessen (Fokus-Ruckgabe)."
        )
        guest_thread.join(timeout=5.0)
        assert not guest_error, f"Gast-Thread endete mit Fehler: {guest_error}"


def test_card_follow_up_action_under_held_claim_does_not_race_live_guest_loop():
    """R5 FIX1: die Folgeaktion EINER Karte (hier `io._cmd_menu_tisch()`,
    dieselbe Methode wie die Kartenauswahl selbst, echt verschachtelt unter
    demselben gehaltenen Claim, s. `_dispatch_completion_card_choice`)
    verschachtelt einen WEITEREN Read auf `io`. Ohne die Thread-Owner-
    Erkennung in `_claim_aware_readline` (R5 FIX1) wuerde dieser
    verschachtelte Read auf den eigenen, gerade gehaltenen Claim warten
    (Deadlock); mit ihr laeuft er sofort durch, WAEHREND der urspruengliche
    Gast-Thread weiterhin zuverlaessig geparkt bleibt."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        guest_printed: list[str] = []
        fifo = _FakeFifo()

        host_session = TuiSession(
            onboarding_dir=root / "host_onboarding", catalog_dir=root / "host_catalog",
            participant_id="betreiber_fix1b", print_fn=lambda *_a: None, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=root / "guest_onboarding", catalog_dir=root / "guest_catalog",
            participant_id="gast_fix1b", input_fn=fifo.read_line, print_fn=guest_printed.append,
            host_capable=False, input_ready_fn=fifo.ready,
        )
        host_session.register_guest_terminal("gast_fix1b", guest_session)

        guest_returned = threading.Event()
        guest_error: list[BaseException] = []

        def _guest_thread_body() -> None:
            try:
                guest_session._cmd_menu_tisch()
            except BaseException as exc:  # pragma: no cover - defensive
                guest_error.append(exc)
            finally:
                guest_returned.set()

        guest_thread = threading.Thread(target=_guest_thread_body, name="guest-fix1b-test", daemon=True)
        guest_thread.start()
        import time as _time
        for _ in range(50):
            if "Tisch -- [1] Offene Tische suchen" in "\n".join(guest_printed):
                break
            _time.sleep(0.02)
        else:
            raise AssertionError("Gast-Thread hat das Tisch-Untermenue nicht sichtbar gedruckt.")

        # Folgeaktion = ein ZWEITER `_cmd_menu_tisch()`-Aufruf auf DEMSELBEN
        # `io` (verschachtelter Read unter dem gehaltenen Claim, derselbe
        # Form wie eine echte Kartenfolgeaktion). Er muss den Claim seines
        # EIGENEN Threads erkennen (bypass) und darf nicht deadlocken.
        actions: list[tuple[str, object]] = [
            ("Tisch-Folgeaktion", lambda: guest_session._cmd_menu_tisch()),
        ]

        done = threading.Event()

        def _host_dispatch() -> None:
            host_session._dispatch_completion_card_choice(guest_session, actions)
            done.set()

        host_thread = threading.Thread(target=_host_dispatch, name="host-fix1b-dispatch", daemon=True)
        host_thread.start()
        # WICHTIG: beide Zeilen erst NACHDEM der Claim steht pushen -- sonst
        # koennte der bereits laenger wartende (unclaimte) urspruengliche
        # Gast-Thread sie vorher stehlen (reine Testablauf-Reihenfolge,
        # nicht der zu belegende Mechanismus selbst).
        for _ in range(100):
            if guest_session._host_terminal_claimed.is_set():
                break
            _time.sleep(0.01)
        else:
            raise AssertionError("Host-Dispatch hat den Claim nicht sichtbar gesetzt.")
        fifo.push("1")  # Kartenauswahl: loest die Folgeaktion aus.
        fifo.push("/zurueck")  # wird von der VERSCHACHTELTEN Folgeaktion konsumiert.
        assert done.wait(timeout=5.0), (
            "Der Host-Dispatch (Karte + verschachtelte Folgeaktion) haette ohne Deadlock "
            "durchlaufen muessen."
        )
        host_thread.join(timeout=5.0)

        assert not guest_returned.is_set(), (
            "Der urspruenglich wartende Gast-Thread haette WAEHREND Karte+Folgeaktion NICHT "
            "konsumieren/zurueckkehren duerfen."
        )

        # Erst JETZT (Claim wieder frei) bekommt der urspruengliche Gast-
        # Thread seine eigene Zeile.
        fifo.push("/zurueck")
        assert guest_returned.wait(timeout=5.0), (
            "Der urspruengliche Gast-Thread haette nach Freigabe des Claims kontrolliert "
            "zurueckkehren muessen (Fokus-Ruckgabe nach Karte+Folge)."
        )
        guest_thread.join(timeout=5.0)
        assert not guest_error, f"Gast-Thread endete mit Fehler: {guest_error}"


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
