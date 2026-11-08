#!/usr/bin/env python3
"""
tests/mmo_sim/test_r9_1_operator_card_back_label_2026_11_08.py --
ZR-VOLLENDUNG-LINUX-MINT-NACHZUG-20261108-R9 (R9-1, GENERAL-REVIEW.md §3
UX-R8-B1 "figurfreie Betreiber-Abschlusskarte luegt pauschal 'Hauptmenue'").

Muster wie `test_r7_a3_card_return_label_and_submenu_dialog_2026_11_08.py`
(dort fuer die PERSOENLICHE Abschlusskarte, hier fuer die FIGURFREIE
Betreiber-Tischkarte `_print_operator_table_completion_card`): Zeile 9397
beschriftete die No-op-Rueckkehr-Option pauschal "Beenden (zurueck zum
Hauptmenue)", obwohl der Karten-Readprompt (9154) ueber
`_completion_card_back_label(self)` bereits korrekt den tatsaechlichen
Kontext nennt. Im normalen Tischmenueweg (figurfreier Betreiber ruft diese
Karte aus seinem EIGENEN `_cmd_menu_tisch()`-Lesezyklus, s. echte Reise in
`drive_r7_c_komfortkopie_zeitpunkt_evidence_2026_11_08.py`-Nutzung) ist der
wahre Rueckweg das Tisch-Untermenue, nicht das Hauptmenue.

Dieser Test deckt die Beschriftungs-/Prompt-Konsistenz an GENAU `self`
(`io is self`, die figurfreie Betreiberkarte dispatcht immer auf sich
selbst, kein separates Gastterminal/kein Thread noetig) in zwei Faellen ab:

1. Hauptmenue-Gegenfall (kontrollierter enger Testrand): frische
   `TuiSession`, `_tisch_submenu_depth == 0` (Default, unveraendert) -->
   Option-3-Label UND Karten-Readprompt nennen "Hauptmenue"; eine leere
   Eingabe kehrt ohne Aktion zurueck (No-op, kein Handler ausgefuehrt).

2. Tischmenue-Kontext (Label-Ehrlichkeit): `session._tisch_submenu_depth`
   direkt > 0 gesetzt (NUR fuer diese enge Beschriftungs-/Prompt-Pruefung
   -- liefert laut Auftrag NICHT den alleinigen Normalweg-Nachweis, das
   leistet die echte Terminalreise in Aufgabe 3) --> Option-3-Label UND
   Readprompt nennen "Tisch-Untermenue", nicht "Hauptmenue".

Beide Faelle pruefen zusaetzlich: Option-Label und Readprompt benutzen
DENSELBEN Ruecktext (Konsistenz-Check, dieselbe Textautoritaet
`_completion_card_back_label(self)`).

Pure Python, nur `assert`, echter Exitcode, kein Modell-/GM-Call."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.ui.tui import TuiSession  # noqa: E402


class _FakeFifo:
    """Enges In-Process-Doppel fuer `session._input` -- zeichnet JEDEN
    tatsaechlich uebergebenen `prompt` in `prompts_seen` auf (derselbe
    Zweck wie `_FakeFifo.read_line` in `test_r7_a3_card_return_label_and_
    submenu_dialog_2026_11_08.py`) und liefert nacheinander die
    vorgegebenen Antworten. `io is self` bei der figurfreien Betreiberkarte
    braucht keinen Thread/keine FIFO-Queue -- ein direkter, synchroner
    Aufruf genuegt."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.prompts_seen: list[str] = []

    def read_line(self, prompt: str = "") -> str:
        self.prompts_seen.append(prompt)
        if self._responses:
            return self._responses.pop(0)
        raise EOFError()


class _FakeOperatorTable:
    table_id = "local-r91-table"


def _new_operator_session(root: Path, operator_id: str, fifo: _FakeFifo) -> TuiSession:
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    return TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=operator_id,
        input_fn=fifo.read_line, print_fn=lambda *_a: None, host_capable=True,
    )


def _show_card_and_collect(session: TuiSession, printed: list[str]) -> None:
    session._print = printed.append
    session._print_operator_table_completion_card(_FakeOperatorTable(), operator_table_key=None)


def test_main_menu_counter_case_labels_and_returns_as_noop():
    """Hauptmenue-Gegenfall: `_tisch_submenu_depth == 0` (unveraendertes
    Default einer frischen Session) -- Option UND Readprompt nennen
    "Hauptmenue", leere Auswahl kehrt ohne Aktion zurueck."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        fifo = _FakeFifo([""])  # leer = No-op-Rueckkehr (kein Handler).
        session = _new_operator_session(root, "betreiber_r91a", fifo)
        assert session._tisch_submenu_depth == 0, (
            "Testrand setzt diesen Fall bewusst NICHT -- muss das unveraenderte Default sein."
        )

        offer_calls: list[object] = []
        zuschauer_calls: list[object] = []
        session._cmd_table_offer = lambda *a, **kw: offer_calls.append((a, kw))
        session._cmd_table_zuschauer = lambda *a, **kw: zuschauer_calls.append((a, kw))

        printed: list[str] = []
        _show_card_and_collect(session, printed)

        out = "\n".join(printed)
        assert "3) Beenden (zurueck zum Hauptmenue)" in out, out
        assert "Tisch-Untermenue" not in out, out

        assert fifo.prompts_seen, "Kein Karten-Readprompt wurde abgefragt."
        card_prompt = fifo.prompts_seen[0]
        assert "zum Hauptmenue" in card_prompt, card_prompt
        assert "Tisch-Untermenue" not in card_prompt, card_prompt

        assert not offer_calls and not zuschauer_calls, (
            "Leere Auswahl haette OHNE Aktion zurueckkehren muessen (No-op), kein Handler darf "
            "gelaufen sein.",
        )

        back_label = session._completion_card_back_label(session)
        assert back_label == "zum Hauptmenue", back_label
        assert f"zurueck {back_label}" in out, (out, back_label)
        assert f"fuehrt {back_label}" in card_prompt, (card_prompt, back_label)


def test_table_submenu_context_labels_as_tisch_untermenue_not_hauptmenue():
    """Tischmenue-Kontext: `_tisch_submenu_depth` direkt > 0 gesetzt (NUR
    fuer diese Beschriftungs-/Prompt-Pruefung, kein alleiniger Normalweg-
    Nachweis) -- Option UND Readprompt nennen "Tisch-Untermenue"."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        fifo = _FakeFifo(["/zurueck"])  # Kontrolltoken = ebenfalls No-op.
        session = _new_operator_session(root, "betreiber_r91b", fifo)
        session._tisch_submenu_depth = 2
        assert session._tisch_submenu_table_query_depth == 0, (
            "Dieser Fall prueft die ALLGEMEINE Untermenue-Tiefe, nicht den tieferen "
            "'Welcher Tisch?'-Read."
        )

        offer_calls: list[object] = []
        zuschauer_calls: list[object] = []
        session._cmd_table_offer = lambda *a, **kw: offer_calls.append((a, kw))
        session._cmd_table_zuschauer = lambda *a, **kw: zuschauer_calls.append((a, kw))

        printed: list[str] = []
        _show_card_and_collect(session, printed)

        out = "\n".join(printed)
        assert "3) Beenden (zurueck zum Tisch-Untermenue)" in out, out
        assert ") Beenden (zurueck zum Hauptmenue)" not in out, out

        assert fifo.prompts_seen, "Kein Karten-Readprompt wurde abgefragt."
        card_prompt = fifo.prompts_seen[0]
        assert "zum Tisch-Untermenue" in card_prompt, card_prompt
        assert "Hauptmenue" not in card_prompt, card_prompt

        assert not offer_calls and not zuschauer_calls, (
            "'/zurueck' haette OHNE Aktion zurueckkehren muessen (No-op), kein Handler darf "
            "gelaufen sein.",
        )

        back_label = session._completion_card_back_label(session)
        assert back_label == "zum Tisch-Untermenue", back_label
        assert f"zurueck {back_label}" in out, (out, back_label)
        assert f"fuehrt {back_label}" in card_prompt, (card_prompt, back_label)


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
