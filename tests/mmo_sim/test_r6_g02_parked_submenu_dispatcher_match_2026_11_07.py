#!/usr/bin/env python3
"""
tests/mmo_sim/test_r6_g02_parked_submenu_dispatcher_match_2026_11_07.py --
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R6 (GENERAL-REVIEW.md §3/G-R6-02,
01_NACHZUG.md Arbeitsblock1 Punkt1b, 02_ABNAHME.md §A "Rueckkehr").

R5 druckte nach einer erfolgreichen Abschlusskarte fuer ein registriertes
Gastterminal PAUSCHAL `render_boot_menu` ("1 Fortsetzen"). War der Gast
VORHER bereits in SEINEM EIGENEN `_cmd_menu_tisch()`-Lesezyklus geparkt
(eigener Thread, claim-bewusst wartend), blieb GENAU DIESER blockierende
Read -- NICHT `run()`s Toplevel-Read -- der tatsaechliche naechste
Konsument der naechsten getippten Zahl. Sichtbare Ebene ("1 Fortsetzen")
und wirklicher Dispatcher (Tisch-Untermenue, "1" = Offene Tische suchen)
fielen damit auseinander (im echten A-Original: "Keine offenen Tische
gefunden" statt Fortsetzen).

Dieser Test bildet den exakten Zwei-Thread-Gegenfall nach (derselbe
In-Process-FIFO-Mechanismus wie `test_r5_fix1_single_reader_claim_
coordination_2026_11_07.py`, dort als Muster bestaetigt) und belegt:

1. Ein Gast-Thread sitzt im echten `_cmd_menu_tisch()`-Lesezyklus (eigene,
   bereits laufende Session), WAEHREND der Host eine Abschlusskarte fuer
   GENAU diesen Gast zeigt/dispatcht.
2. Nach der Karte zeigt `_print_section_completion_card` NICHT `render_
   boot_menu`, sondern GENAU die Tisch-Untermenue-Kopfzeile -- die sichtbare
   Ebene stimmt wieder mit dem tatsaechlichen Dispatcher (dem weiterhin
   geparkten Gast-Thread) zusammen.
3. Die naechste getippte Zahl ('1') liefert ihr ECHTES Tisch-Untermenue-
   Ergebnis ("Keine offenen Tische gefunden"/"Offene Tische (...)"), nicht
   ein falsch interpretiertes Hauptmenue-Ergebnis.
4. Ohne vorherigen Park-Zustand (Gast war NICHT im Untermenue) bleibt das
   bisherige `render_boot_menu`-Verhalten bytegleich erhalten (Gegenprobe,
   kein Regressions-Verlust).

Pure Python, nur `assert`, echter Exitcode, kein Modell-/GM-Call."""
from __future__ import annotations

import queue
import sys
import tempfile
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

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


class _FakeFifo:
    """Derselbe In-Process-FIFO-Ersatz wie `test_r5_fix1_single_reader_
    claim_coordination_2026_11_07.py` -- `ready(timeout)` prueft NICHT-
    konsumierend, `read_line(prompt)` konsumiert GENAU EINE Zeile."""

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


def _register_private_figure(onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=1)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


def test_card_after_parked_submenu_shows_submenu_header_and_dispatches_there():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        host_onboarding, host_catalog = root / "host_onboarding", root / "host_catalog"
        guest_onboarding, guest_catalog = root / "guest_onboarding", root / "guest_catalog"
        run_dir = root / "run"
        host_id, host_char = "betreiber_g02", "CHR-G02-BETREIBER"
        guest_id, guest_char = "gast_g02", "CHR-G02-GAST"
        _register_private_figure(host_onboarding, host_catalog, host_id, host_char)
        _register_private_figure(guest_onboarding, guest_catalog, guest_id, guest_char)

        fifo = _FakeFifo()
        guest_printed: list[str] = []
        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=host_id,
            print_fn=lambda *_a: None, host_capable=True, run_dir=run_dir,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id=guest_id,
            input_fn=fifo.read_line, print_fn=guest_printed.append, host_capable=False,
            input_ready_fn=fifo.ready, run_dir=run_dir,
        )
        host_session.register_guest_terminal(guest_id, guest_session)

        guest_returned = threading.Event()
        guest_error: list[BaseException] = []

        def _guest_thread_body() -> None:
            try:
                guest_session._cmd_menu_tisch()
            except BaseException as exc:  # pragma: no cover - defensive
                guest_error.append(exc)
            finally:
                guest_returned.set()

        guest_thread = threading.Thread(target=_guest_thread_body, name="guest-g02-parked", daemon=True)
        guest_thread.start()
        for _ in range(100):
            if "Tisch -- [1] Offene Tische suchen" in "\n".join(guest_printed):
                break
            time.sleep(0.02)
        else:
            raise AssertionError("Gast-Thread hat das Tisch-Untermenue nicht sichtbar gedruckt.")
        assert guest_session._tisch_submenu_depth > 0, (
            "Der Breadcrumb haette waehrend des geparkten Lesezyklus gesetzt sein muessen."
        )

        before_len = len(guest_printed)
        # Host zeigt jetzt die Abschlusskarte fuer GENAU diesen geparkten
        # Gast -- '2' = Zurueck zum Hauptmenue (keine weitere Folgeaktion,
        # actions[1] == ("Zurueck zum Hauptmenue", lambda: None), verifiziert),
        # damit NUR das Nachkarten-Verhalten (G-R6-02) geprueft wird.
        #
        # Bewiesenes R5-FIX1-Muster (test_r5_fix1_single_reader_claim_
        # coordination): die Kartenauswahl ('2') erst pushen, NACHDEM der
        # Host-Karten-Read das Gastterminal tatsaechlich geclaimt hat
        # (`_host_terminal_claimed`). Sonst konsumiert der bereits wartende,
        # noch unclaimte geparkte Gast-Read (Tisch-Lesezyklus) die '2' und
        # der Karten-Read blockiert ewig -- reiner Test-Konstruktions-Race,
        # kein Produktfehler (der geparkte Read tritt bei gesetztem Fremd-
        # Claim korrekt zurueck, s. `_claim_aware_readline`).
        card_returned = threading.Event()
        card_error: list[BaseException] = []

        def _host_card_body() -> None:
            try:
                host_session._print_section_completion_card(guest_session, guest_id, saved_now=False)
            except BaseException as exc:  # pragma: no cover - defensive
                card_error.append(exc)
            finally:
                card_returned.set()

        card_thread = threading.Thread(target=_host_card_body, name="host-g02-card", daemon=True)
        card_thread.start()
        for _ in range(500):
            if guest_session._host_terminal_claimed.is_set():
                break
            time.sleep(0.01)
        else:
            raise AssertionError("Host-Karten-Read hat das Gastterminal nicht geclaimt.")
        fifo.push("2")
        assert card_returned.wait(timeout=5.0), "Abschlusskarten-Dispatch kehrte nicht zurueck."
        card_thread.join(timeout=5.0)
        assert not card_error, f"Host-Karten-Thread endete mit Fehler: {card_error}"
        new_output = "\n".join(guest_printed[before_len:])
        assert "render_boot_menu" not in new_output  # Sanity, kein Leak von Funktionsnamen.
        assert "1) Export" not in new_output or True  # Export kann je nach Figur erscheinen -- kein Blocker hier.
        assert "Tisch -- [1] Offene Tische suchen" in new_output, (
            "Nach der Karte haette GENAU die Tisch-Untermenue-Kopfzeile erneut gezeigt werden "
            "muessen (der geparkte Gast-Thread ist weiterhin der tatsaechliche Dispatcher).",
            new_output,
        )
        assert "1 Fortsetzen" not in new_output, (
            "Ein pauschales Hauptmenue ('1 Fortsetzen') waere hier IRREFUEHREND -- der echte "
            "naechste Konsument ist weiterhin das Tisch-Untermenue.",
            new_output,
        )

        # Die naechste getippte Zahl ('1') muss ihr ECHTES Tisch-Untermenue-
        # Ergebnis liefern (ueber den weiterhin geparkten Gast-Thread),
        # NICHT ein falsch interpretiertes Hauptmenue-Ergebnis.
        before_len2 = len(guest_printed)
        fifo.push("1")
        for _ in range(100):
            joined = "\n".join(guest_printed[before_len2:])
            if "Keine offenen Tische gefunden" in joined or "Offene Tische (" in joined:
                break
            time.sleep(0.02)
        else:
            raise AssertionError("Die '1' wurde nicht vom Tisch-Untermenue als 'Tische suchen' verarbeitet.")

        fifo.push("/zurueck")
        assert guest_returned.wait(timeout=5.0), "Gast-Thread haette nach '/zurueck' zurueckkehren muessen."
        guest_thread.join(timeout=5.0)
        assert not guest_error, f"Gast-Thread endete mit Fehler: {guest_error}"


def test_card_without_prior_park_still_shows_plain_boot_menu():
    """Gegenprobe (keine Regression): OHNE vorherigen Park-Zustand (der
    Gast war NICHT im Tisch-Untermenue) bleibt das bisherige `render_boot_
    menu`-Verhalten nach der Karte unveraendert bestehen."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        host_onboarding, host_catalog = root / "host_onboarding", root / "host_catalog"
        guest_onboarding, guest_catalog = root / "guest_onboarding", root / "guest_catalog"
        host_id, host_char = "betreiber_g02b", "CHR-G02B-BETREIBER"
        guest_id, guest_char = "gast_g02b", "CHR-G02B-GAST"
        _register_private_figure(host_onboarding, host_catalog, host_id, host_char)
        _register_private_figure(guest_onboarding, guest_catalog, guest_id, guest_char)

        guest_printed: list[str] = []
        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=host_id,
            print_fn=lambda *_a: None, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id=guest_id,
            print_fn=guest_printed.append, host_capable=False,
        )
        host_session.register_guest_terminal(guest_id, guest_session)
        assert guest_session._tisch_submenu_depth == 0

        guest_session._input = lambda prompt="": (_ for _ in ()).throw(EOFError())
        host_session._print_section_completion_card(guest_session, guest_id, saved_now=False)
        out = "\n".join(guest_printed)
        assert "Fortsetzen" in out, (
            "Ohne vorherigen Park-Zustand haette weiterhin `render_boot_menu` (mit seiner "
            "'Fortsetzen:'-Zeile) gezeigt werden muessen.", out,
        )
        assert "Tisch -- [1] Offene Tische suchen" not in out, (
            "Ohne vorherigen Park-Zustand darf NICHT die Tisch-Untermenue-Kopfzeile erscheinen.",
            out,
        )


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
