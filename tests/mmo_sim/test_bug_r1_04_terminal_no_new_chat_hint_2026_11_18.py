#!/usr/bin/env python3
"""
tests/mmo_sim/test_bug_r1_04_terminal_no_new_chat_hint_2026_11_18.py —
BUG-R1-04 (ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261118-r3): die KI-SL-
Anweisung "neuen Chat oeffnen, Save laden" (Chargen-Save-Gate/Abschnitts-
wechsel, core/spieler-handbuch.md) ist fuer das Chat-basierte OpenWebUI-
Produkt richtig, verwirrt aber im Terminalspiel (kein "Chat"-Konzept dort).

Fix: `TuiSession._print_section_completion_card` (die echte, produkt-
autoritative Abschlusskarte NACH jedem Abschnittsende, s. ui/tui.py) zeigt
jetzt deterministisch einen klarstellenden Terminal-Hinweis -- OHNE den
Masterprompt/die WS-Regel selbst zu aendern und OHNE das freie KI-SL-
Narrativ per fragiler Textmustersuche umzuschreiben.

Treibt den echten Aufrufer (`_print_section_completion_card`, Muster
test_r4_u3_completion_card_and_stop_retry_2026_11_07.py) an.
Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
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

_HINT = "musst du dafuer KEINEN neuen Chat oeffnen"


def _register_private_figure(onboarding_dir, catalog_dir, participant_id, char_id):
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=1)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


def test_completion_card_shows_terminal_clarification_after_real_save():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        host_id, char_id = "host_r1_04", "CHR-R1-04-HOST"
        _register_private_figure(onboarding_dir, catalog_dir, host_id, char_id)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=host_id,
            print_fn=printed.append, host_capable=True,
        )
        session._input = lambda prompt="": "2"  # "Zurueck", keine Folgeaktion noetig
        session._print_section_completion_card(session, host_id, saved_now=True)

        out = "\n".join(printed)
        assert _HINT in out, (
            "BUG-R1-04: die Terminal-Klarstellung muss nach einem echten Abschnittsabschluss "
            f"erscheinen. Gedruckt war:\n{out}"
        )


def test_hint_appears_regardless_of_whether_a_new_save_happened_this_round():
    """Die Klarstellung ist keine Erfolgsbehauptung -- sie gilt fuer JEDE
    Abschlusskarte (auch ohne neuen Save in dieser Runde), weil sie sich
    auf den naechsten Abschnittswechsel bezieht, nicht auf diesen Zug."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        host_id, char_id = "host_r1_04b", "CHR-R1-04B-HOST"
        _register_private_figure(onboarding_dir, catalog_dir, host_id, char_id)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=host_id,
            print_fn=printed.append, host_capable=True,
        )
        session._input = lambda prompt="": "2"
        session._print_section_completion_card(session, host_id, saved_now=False)

        out = "\n".join(printed)
        assert _HINT in out, out


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
            import traceback
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
