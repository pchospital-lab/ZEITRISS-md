#!/usr/bin/env python3
"""
tests/mmo_sim/test_r7_a3_card_return_label_and_submenu_dialog_2026_11_08.py --
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261108-R7 (01_NACHZUG.md A3, GENERAL-
REVIEW.md §4, 02_ABNAHME.md §B "Wahrer Rueckweg nach der Karte").

Zwei getrennte, aber zusammenhaengende Befunde aus GENERAL-REVIEW.md §4:

1. `_print_section_completion_card` beschriftet eine Aktion PAUSCHAL
   "Zurueck zum Hauptmenue" (No-op-Handler), obwohl die TATSAECHLICHE
   Rueckgabe -- sobald `io`s eigener Thread bereits in seinem EIGENEN
   `_cmd_menu_tisch()`-Lesezyklus geparkt ist (`io._tisch_submenu_depth >
   0`) -- das weiterhin geparkte Tisch-Untermenue ist, NICHT das
   Hauptmenue. Der (R6-angenommene) FUNKTIONALE Rueckkehrweg selbst bleibt
   unveraendert (G02-Testoriginal) -- nur das Label muss jetzt ehrlich
   sein.

2. `_tisch_submenu_depth` alleine unterscheidet NICHT den noch tieferen,
   konkret wartenden "Welcher Tisch (Nummer ... oder table_key)?"-Read
   (Zeile ~2168/~2197) von der ALLGEMEINEN Tisch-Untermenue-Auswahl. Wird
   eine Karte gezeigt, WAEHREND `io`s Thread konkret in diesem tieferen
   Dialog wartet, darf NICHT die allgemeine Untermenue-Kopfzeile ("[1]
   Offene Tische suchen ...") erneut gedruckt werden -- die naechste
   getippte Zahl bedeutet dort eine TISCHKENNUNG/-INDEX, keine
   Submenue-Aktion ("sichtbare Ebene != wirklicher Leser").

Dieser Test bildet BEIDE am echten `TuiSession`-Code nach (derselbe
In-Process-FIFO-Mechanismus wie `test_r6_g02_parked_submenu_dispatcher_
match_2026_11_07.py`, dort als Muster bestaetigt):

a) Guest-Thread wird gezielt bis in den TIEFEREN "Welcher Tisch?"-Read
   hinein geparkt (Wahl "2" = anfragen im Tisch-Untermenue).
b) Host zeigt WAEHREND dieser Parkung die Abschlusskarte fuer GENAU
   diesen Gast.
c) Belegt: das Kartenlabel fuer die No-op-Aktion ist jetzt ehrlich
   ("Zurueck zum Tisch-Untermenue", NICHT "Zurueck zum Hauptmenue"); nach
   der Karte erscheint GENAU die noch offene "Welcher Tisch?"-Frage
   erneut (NICHT die allgemeine Untermenue-Kopfzeile).
d) Die naechste getippte Zahl ('1') wird tatsaechlich als TISCHAUSWAHL
   (Index in die zuletzt gezeigte Liste) an `_cmd_table_request_join`
   durchgereicht -- nicht als Submenue-Aktion missinterpretiert.
e) Gegenprobe (keine Regression): dieselbe Karte WAEHREND der
   ALLGEMEINEN Tisch-Untermenue-Auswahl (nicht im tieferen Dialog) zeigt
   weiterhin unveraendert die allgemeine Kopfzeile (G-R6-02-Verhalten).

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
from mmo_sim.ui.tui import _TISCH_WHICH_TABLE_PROMPT, TuiSession  # noqa: E402


class _FakeFifo:
    """Derselbe In-Process-FIFO-Ersatz wie `test_r6_g02_parked_submenu_
    dispatcher_match_2026_11_07.py` -- `ready(timeout)` prueft NICHT-
    konsumierend, `read_line(prompt)` konsumiert GENAU EINE Zeile.

    R8-Nachzug (01_NACHZUG.md R8-2c): `read_line` zeichnet zusaetzlich JEDEN
    tatsaechlich uebergebenen `prompt` in `prompts_seen` auf -- derselbe
    `prompt`, den das reale `scripts/mmo_sim.py::_FifoLineReader.read_line`
    bei nicht-leerem Text wirklich an den Gastbildschirm echot (s. dortiger
    `_echo_fn`-Aufruf). Diese enge Testdoppel druckt den Prompt selbst
    NICHT (unveraendertes bisheriges Verhalten dieser Klasse), erlaubt aber
    zu pruefen, WELCHEN Text `_dispatch_completion_card_choice` fuer den
    Karten-Read tatsaechlich uebergibt -- genau die R8-2c-Luecke
    (`tui.py:9124` versprach dort weiter pauschal 'Hauptmenue')."""

    def __init__(self) -> None:
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._lock = threading.Lock()
        self._peeked: str | None = None
        self.prompts_seen: list[str] = []

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
        self.prompts_seen.append(prompt)
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


def test_card_during_deeper_which_table_dialog_matches_label_and_reminder():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        host_onboarding, host_catalog = root / "host_onboarding", root / "host_catalog"
        guest_onboarding, guest_catalog = root / "guest_onboarding", root / "guest_catalog"
        host_id, guest_id = "betreiber_a3", "gast_a3"
        _register_private_figure(host_onboarding, host_catalog, host_id, "CHR-A3-HOST")
        _register_private_figure(guest_onboarding, guest_catalog, guest_id, "CHR-A3-GUEST")

        fifo = _FakeFifo()
        guest_printed: list[str] = []
        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=host_id,
            print_fn=lambda *_a: None, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id=guest_id,
            input_fn=fifo.read_line, print_fn=guest_printed.append, host_capable=False,
            input_ready_fn=fifo.ready,
        )
        host_session.register_guest_terminal(guest_id, guest_session)

        # Vorher bereits gezeigte Tischliste (In-Memory-Breadcrumb, wie von
        # `_cmd_table_search` real befuellt) -- direkt gesetzt, damit dieser
        # enge Test keine echte Admission-Laufumgebung braucht.
        guest_session._last_table_search_offers = ["mesa-a3-eins"]

        join_calls: list[tuple[tuple, str | None]] = []

        def _fake_request_join(args, *, acting_pid=None):
            join_calls.append((tuple(args), acting_pid))

        guest_session._cmd_table_request_join = _fake_request_join

        guest_returned = threading.Event()
        guest_error: list[BaseException] = []

        def _guest_thread_body() -> None:
            try:
                guest_session._cmd_menu_tisch()
            except BaseException as exc:  # pragma: no cover - defensive
                guest_error.append(exc)
            finally:
                guest_returned.set()

        guest_thread = threading.Thread(target=_guest_thread_body, name="guest-a3", daemon=True)
        guest_thread.start()
        for _ in range(200):
            if "Tisch -- [1] Offene Tische suchen" in "\n".join(guest_printed):
                break
            time.sleep(0.02)
        else:
            raise AssertionError("Gast-Thread hat das Tisch-Untermenue nicht sichtbar gedruckt.")

        # '2' = Tisch anfragen -> fuehrt in den TIEFEREN "Welcher Tisch?"-
        # Read, NICHT direkt in eine Aktion.
        fifo.push("2")
        for _ in range(200):
            if guest_session._tisch_submenu_table_query_depth > 0:
                break
            time.sleep(0.01)
        else:
            raise AssertionError(
                "Gast-Thread ist nicht im tieferen 'Welcher Tisch?'-Read geparkt -- Testaufbau defekt."
            )
        assert guest_session._tisch_submenu_depth > 0, (
            "Der aeussere Breadcrumb haette ebenfalls gesetzt sein muessen."
        )

        before_len = len(guest_printed)
        before_prompts_len = len(fifo.prompts_seen)
        card_returned = threading.Event()
        card_error: list[BaseException] = []

        def _host_card_body() -> None:
            try:
                host_session._print_section_completion_card(guest_session, guest_id, saved_now=False)
            except BaseException as exc:  # pragma: no cover - defensive
                card_error.append(exc)
            finally:
                card_returned.set()

        card_thread = threading.Thread(target=_host_card_body, name="host-a3-card", daemon=True)
        card_thread.start()
        for _ in range(500):
            if guest_session._host_terminal_claimed.is_set():
                break
            time.sleep(0.01)
        else:
            raise AssertionError("Host-Karten-Read hat das Gastterminal nicht geclaimt.")

        # Kartenwahl: Export entfaellt nicht (Figur vorhanden) -> Aktion 2
        # ist die No-op-Rueckkehr (Label wird unten geprueft).
        fifo.push("2")
        assert card_returned.wait(timeout=5.0), "Abschlusskarten-Dispatch kehrte nicht zurueck."
        card_thread.join(timeout=5.0)
        assert not card_error, f"Host-Karten-Thread endete mit Fehler: {card_error}"

        new_output = "\n".join(guest_printed[before_len:])
        assert "Zurueck zum Tisch-Untermenue" in new_output, (
            "Das Rueckkehr-Label haette ehrlich 'Tisch-Untermenue' nennen muessen, nicht "
            "pauschal 'Hauptmenue' (der wirklich wartende Read ist weiterhin das Tisch-"
            "Untermenue).", new_output,
        )
        assert ") Zurueck zum Hauptmenue" not in new_output, new_output
        assert _TISCH_WHICH_TABLE_PROMPT.strip() in new_output, (
            "Nach der Karte haette GENAU die noch offene 'Welcher Tisch?'-Frage erneut gezeigt "
            "werden muessen.", new_output,
        )
        assert "Tisch -- [1] Offene Tische suchen" not in new_output, (
            "Die ALLGEMEINE Untermenue-Kopfzeile waere hier IRREFUEHREND -- der wirklich "
            "wartende Read ist der tiefere 'Welcher Tisch?'-Dialog, keine Submenue-Auswahl.",
            new_output,
        )
        # R8-Nachzug (01_NACHZUG.md R8-2c, tui.py:9124): der GENERISCHE
        # Karten-Read-Prompt selbst (nicht nur das No-op-Aktionslabel oben)
        # muss ebenfalls ehrlich die tiefere "Welcher Tisch?"-Frage nennen,
        # nicht pauschal "Hauptmenue".
        card_prompts = fifo.prompts_seen[before_prompts_len:]
        assert card_prompts and "zur vorherigen 'Welcher Tisch?'-Frage" in card_prompts[0], (
            "Der Karten-Read-Prompt haette ehrlich die tiefere 'Welcher Tisch?'-Frage als "
            "Rueckziel nennen muessen.", card_prompts,
        )
        assert "Hauptmenue" not in card_prompts[0], card_prompts

        # Die naechste getippte Zahl MUSS als Tischauswahl (Index 1 ->
        # 'mesa-a3-eins') ankommen, NICHT als Submenue-Aktion.
        fifo.push("1")
        for _ in range(200):
            if join_calls:
                break
            time.sleep(0.02)
        else:
            raise AssertionError("Die '1' wurde nicht als Tischauswahl im tieferen Dialog verarbeitet.")
        assert join_calls == [(("mesa-a3-eins",), guest_id)], join_calls

        fifo.push("/zurueck")
        assert guest_returned.wait(timeout=5.0), "Gast-Thread haette nach '/zurueck' zurueckkehren muessen."
        guest_thread.join(timeout=5.0)
        assert not guest_error, f"Gast-Thread endete mit Fehler: {guest_error}"


def test_card_during_general_submenu_selection_keeps_existing_header_behaviour():
    """Gegenprobe (keine Regression): die Karte WAEHREND der ALLGEMEINEN
    Tisch-Untermenue-Auswahl (NICHT im tieferen 'Welcher Tisch?'-Dialog)
    zeigt weiterhin unveraendert die allgemeine Kopfzeile (G-R6-02)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        host_onboarding, host_catalog = root / "host_onboarding", root / "host_catalog"
        guest_onboarding, guest_catalog = root / "guest_onboarding", root / "guest_catalog"
        host_id, guest_id = "betreiber_a3b", "gast_a3b"
        _register_private_figure(host_onboarding, host_catalog, host_id, "CHR-A3B-HOST")
        _register_private_figure(guest_onboarding, guest_catalog, guest_id, "CHR-A3B-GUEST")

        fifo = _FakeFifo()
        guest_printed: list[str] = []
        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=host_id,
            print_fn=lambda *_a: None, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id=guest_id,
            input_fn=fifo.read_line, print_fn=guest_printed.append, host_capable=False,
            input_ready_fn=fifo.ready,
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

        guest_thread = threading.Thread(target=_guest_thread_body, name="guest-a3b", daemon=True)
        guest_thread.start()
        for _ in range(200):
            if "Tisch -- [1] Offene Tische suchen" in "\n".join(guest_printed):
                break
            time.sleep(0.02)
        else:
            raise AssertionError("Gast-Thread hat das Tisch-Untermenue nicht sichtbar gedruckt.")
        assert guest_session._tisch_submenu_depth > 0
        assert guest_session._tisch_submenu_table_query_depth == 0, (
            "Im allgemeinen Auswahl-Read darf der tiefere Breadcrumb NICHT gesetzt sein."
        )

        before_len = len(guest_printed)
        before_prompts_len = len(fifo.prompts_seen)
        card_returned = threading.Event()

        def _host_card_body() -> None:
            host_session._print_section_completion_card(guest_session, guest_id, saved_now=False)
            card_returned.set()

        card_thread = threading.Thread(target=_host_card_body, name="host-a3b-card", daemon=True)
        card_thread.start()
        for _ in range(500):
            if guest_session._host_terminal_claimed.is_set():
                break
            time.sleep(0.01)
        else:
            raise AssertionError("Host-Karten-Read hat das Gastterminal nicht geclaimt.")
        fifo.push("2")
        assert card_returned.wait(timeout=5.0)
        card_thread.join(timeout=5.0)

        new_output = "\n".join(guest_printed[before_len:])
        assert "Tisch -- [1] Offene Tische suchen" in new_output, (
            "Im allgemeinen Auswahl-Fall haette weiterhin die Untermenue-Kopfzeile gezeigt "
            "werden muessen (unveraendertes G-R6-02-Verhalten).", new_output,
        )
        assert "Zurueck zum Tisch-Untermenue" in new_output, new_output
        # R8-Nachzug (01_NACHZUG.md R8-2c): auch hier muss der generische
        # Karten-Read-Prompt selbst (tui.py:9124) ehrlich "Tisch-Untermenue"
        # nennen, nicht pauschal "Hauptmenue" -- derselbe wartende Read ist
        # hier die ALLGEMEINE Untermenue-Auswahl, nicht die tiefere Frage.
        card_prompts = fifo.prompts_seen[before_prompts_len:]
        assert card_prompts and "zum Tisch-Untermenue" in card_prompts[0], (
            "Der Karten-Read-Prompt haette ehrlich 'Tisch-Untermenue' als Rueckziel nennen "
            "muessen.", card_prompts,
        )
        assert "Hauptmenue" not in card_prompts[0], card_prompts

        fifo.push("/zurueck")
        assert guest_returned.wait(timeout=5.0)
        guest_thread.join(timeout=5.0)
        assert not guest_error, f"Gast-Thread endete mit Fehler: {guest_error}"


def test_card_retry_exhausted_message_matches_real_back_destination():
    """R8-Nachzug (01_NACHZUG.md R8-2c, GENERAL-REVIEW.md §4 "ebenso der
    Ruecktext bei ausgeschoepften Fehlversuchen um 9138"): nicht nur der
    Karten-Read-Prompt selbst, auch der Rueckfalltext nach den 10
    ungueltigen Versuchen (`_dispatch_completion_card_choice`s
    `max_attempts`-Zweig) muss die tatsaechliche Rueckgabe (hier: das
    weiterhin geparkte Tisch-Untermenue) nennen, nicht pauschal
    'Hauptmenue'."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        host_onboarding, host_catalog = root / "host_onboarding", root / "host_catalog"
        guest_onboarding, guest_catalog = root / "guest_onboarding", root / "guest_catalog"
        host_id, guest_id = "betreiber_a3c", "gast_a3c"
        _register_private_figure(host_onboarding, host_catalog, host_id, "CHR-A3C-HOST")
        _register_private_figure(guest_onboarding, guest_catalog, guest_id, "CHR-A3C-GUEST")

        fifo = _FakeFifo()
        guest_printed: list[str] = []
        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=host_id,
            print_fn=lambda *_a: None, host_capable=True,
        )
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id=guest_id,
            input_fn=fifo.read_line, print_fn=guest_printed.append, host_capable=False,
            input_ready_fn=fifo.ready,
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

        guest_thread = threading.Thread(target=_guest_thread_body, name="guest-a3c", daemon=True)
        guest_thread.start()
        for _ in range(200):
            if "Tisch -- [1] Offene Tische suchen" in "\n".join(guest_printed):
                break
            time.sleep(0.02)
        else:
            raise AssertionError("Gast-Thread hat das Tisch-Untermenue nicht sichtbar gedruckt.")
        assert guest_session._tisch_submenu_depth > 0

        card_returned = threading.Event()
        card_error: list[BaseException] = []

        def _host_card_body() -> None:
            try:
                host_session._print_section_completion_card(guest_session, guest_id, saved_now=False)
            except BaseException as exc:  # pragma: no cover - defensive
                card_error.append(exc)
            finally:
                card_returned.set()

        card_thread = threading.Thread(target=_host_card_body, name="host-a3c-card", daemon=True)
        card_thread.start()
        for _ in range(500):
            if guest_session._host_terminal_claimed.is_set():
                break
            time.sleep(0.01)
        else:
            raise AssertionError("Host-Karten-Read hat das Gastterminal nicht geclaimt.")

        before_len = len(guest_printed)
        # 10 ungueltige Versuche (ausserhalb jeder gueltigen Aktionsnummer)
        # -- erschoepft `max_attempts`, OHNE '/zurueck' zu tippen.
        for _ in range(10):
            fifo.push("99")
        assert card_returned.wait(timeout=5.0), "Abschlusskarten-Dispatch kehrte nicht zurueck."
        card_thread.join(timeout=5.0)
        assert not card_error, f"Host-Karten-Thread endete mit Fehler: {card_error}"

        new_output = "\n".join(guest_printed[before_len:])
        assert "zurueck zum Tisch-Untermenue" in new_output, (
            "Der Rueckfalltext nach ausgeschoepften Fehlversuchen haette ehrlich "
            "'Tisch-Untermenue' nennen muessen, nicht pauschal 'Hauptmenue' (der wirklich "
            "wartende Read ist weiterhin das Tisch-Untermenue).", new_output,
        )
        assert "zurueck zum Hauptmenue" not in new_output, new_output

        fifo.push("/zurueck")
        assert guest_returned.wait(timeout=5.0)
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
