#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_resume_card_community.py — UX11 (ZEITRISS Terminal
UX-1, 06_ABNAHME_UND_TESTS.md): `_build_resume_card()` lieferte `community_id`
vorher fest `None` -- die Fortsetzen-Zeile in `render_boot_menu()` war ueber
den normalen Startweg STRUKTURELL NIE erreichbar (OFFENE_BEDIENBEFUNDE.md
Punkt 1, General-Befund G01). Dieser Test beweist den realen, ueber den
tatsaechlichen `c`-Produktionsweg (`TuiSession._cmd_community`, keine
isolierte Domaenenfunktion) erzeugten Fix -- UND dass ein Teilnehmer ohne
jede Community weiterhin `None` bekommt (kein falsches Positiv).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.ui.tui import EndOfInput, TuiSession, render_boot_menu  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _eof_input(prompt: str = "") -> str:
    raise EOFError()


def test_resume_card_none_without_any_community_or_figure():
    """UX11/UX12 Vorbedingung: ohne jede Community/Figur bleibt die Karte
    `None` wie vorher -- kein falsch-positives 'Fortsetzen'."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="fresh-p",
            input_fn=_eof_input, print_fn=lambda *_a: None,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
        )
        card = session._build_resume_card()
        assert card is None, card
        text = render_boot_menu(card)
        assert "Fortsetzen" not in text, text


def test_resume_card_shows_real_community_id_after_real_c_command():
    """UX11 Kernfall: nach dem tatsaechlichen `c`-Produktionsweg
    (`_cmd_community`, OHNE gm_transport_factory/persona_driver_factory --
    reiner Demo-Pool-Zweig, 0 Modellaufrufe) muss `_build_resume_card()`
    `community_id='community-<participant_id>'` liefern, NICHT mehr
    hartcodiert `None` (der eigentliche Fehler, OFFENE_BEDIENBEFUNDE.md
    Punkt 1)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_eof_input, print_fn=printed.append,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
        )
        session._cmd_community()
        assert any("Bootstrap" in p for p in printed), printed

        card = session._build_resume_card()
        assert card is not None
        assert card.community_id == "community-p1", card
        assert card.participant_id == "p1"

        text = render_boot_menu(card)
        assert "Fortsetzen: community-p1 · p1" in text, text
        assert "[fortsetzen] Fortsetzen" in text, text


def test_resume_card_different_participant_without_own_community_stays_none():
    """UX11/UX21-Erhaltung: eine fremde `participant_id` unter DEMSELBEN
    `run_dir` bekommt KEINE fremde Community zugeordnet (kein geteilter
    Zeiger ueber Teilnehmergrenzen hinweg)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        owner_session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="owner",
            input_fn=_eof_input, print_fn=lambda *_a: None,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
        )
        owner_session._cmd_community()

        other_session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="someone-else",
            input_fn=_eof_input, print_fn=lambda *_a: None,
            run_dir=d / "run", states_dir=d / "states", schema_path=_SCHEMA_PATH,
        )
        card = other_session._build_resume_card()
        assert card is None, card


def test_resume_card_without_run_dir_stays_none_no_regression():
    """Ohne konfigurierte Laufumgebung (viele bestehende Tests/Aufrufe ohne
    `run_dir`) bleibt die Community-Erkennung ausgeschaltet -- kein neuer
    Crash/Importversuch, identisch zum alten Verhalten fuer diesen Fall."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        session = TuiSession(
            onboarding_dir=d / "onboarding", catalog_dir=d / "catalog", participant_id="p1",
            input_fn=_eof_input, print_fn=lambda *_a: None,
        )
        card = session._build_resume_card()
        assert card is None, card


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
