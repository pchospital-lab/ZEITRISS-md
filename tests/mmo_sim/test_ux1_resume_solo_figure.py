#!/usr/bin/env python3
"""
tests/mmo_sim/test_ux1_resume_solo_figure.py — R2 (Korrekturzyklus 1, C-M2,
UX11), ZEITRISS Terminal UX-1.

Vorher gateten `render_boot_menu()`s `has_resume` UND `_cmd_menu_
fortsetzen()`s Guard EXKLUSIV auf `card.community_id` -- ein Teilnehmer mit
einer echten, abgeschlossenen Figur-Save, der aber NIE 'c' (Meine
KI-Spielgemeinschaft) genutzt hat (der weitaus haeufigste Einstiegspfad:
[n] Figur erschaffen -> solo spielen), sah "Fortsetzen" nie -- obwohl
`_resolve_member()`/`_cmd_local_round([])` fuer genau diesen Fall voll
funktionsfaehig sind und nichts mit `community_id` zu tun haben. Die
gedruckte Fehlermeldung behauptete zudem faelschlich, auch die Figur-Save
geprueft zu haben.

Dieser Test beweist: eine Solo-Figur OHNE Community macht "Fortsetzen"
jetzt sichtbar UND tatsaechlich funktionsfaehig (ruft den echten
`_cmd_local_round([])`-Weg auf, keine zweite, schwaechere Anzeige-Logik).

Erhaltungsprobe: der echte Negativfall (weder Community noch Figur) bleibt
unveraendert "kein fortsetzbarer Stand" (s. bereits bestehender Test
`test_ux1_resume_card_community.py::test_resume_card_none_without_any_
community_or_figure`, hier nicht dupliziert).

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
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mmo_sim.ui.tui import TuiSession, render_boot_menu  # noqa: E402
import _a24_local_support as sup  # noqa: E402


def _eof_input(prompt: str = "") -> str:
    raise EOFError()


def _build_solo_figure_without_community(d: Path):
    run_dir, states_dir, onboarding_dir, catalog_dir, registry_dir = (
        d / "run", d / "states", d / "onboarding", d / "catalog", d / "registry",
    )
    solo = sup.register_human(registry_dir, "Solo")
    pid = solo.participant_id
    onb = sup.onboard_human_figure(
        registry_dir, pid, onboarding_dir, states_dir, run_dir, "CHR-SOLO", "Solo", "SOLOOPS",
    )
    from mmo_sim.domain.zeitriss import catalog as catalog_mod
    catalog_mod.register(catalog_dir, catalog_mod.CatalogEntry(
        participant_id=pid, chrononaut_id=onb["char_id"], persona_key=pid, display_name="Solo",
    ))
    catalog_mod.bind_for_section(catalog_dir, pid, onb["char_id"], has_open_section=False)
    return pid, run_dir, states_dir, onboarding_dir, catalog_dir


def test_resume_card_solo_figure_without_community_has_chrononaut_id():
    """`_build_resume_card()` liefert fuer die Solo-Figur `chrononaut_id`
    gesetzt UND `community_id` korrekt `None` (kein falsches Positiv auf
    der Community-Seite)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid, run_dir, states_dir, onboarding_dir, catalog_dir = _build_solo_figure_without_community(d)
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=pid,
            input_fn=_eof_input, print_fn=lambda *_a: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
        )
        card = session._build_resume_card()
        assert card is not None
        assert card.chrononaut_id == "CHR-SOLO", card
        assert card.community_id is None, card


def test_fortsetzen_visible_and_functional_for_solo_figure_without_community():
    """R2 Kernassertion: Solo-Figur ohne Community macht 'Fortsetzen' im
    Menue SICHTBAR und `_cmd_menu_fortsetzen()` ruft tatsaechlich den
    echten `_cmd_local_round([])`-Weg auf (kein zweiter, nur kosmetischer
    Guard-Text mehr)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        pid, run_dir, states_dir, onboarding_dir, catalog_dir = _build_solo_figure_without_community(d)
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=pid,
            input_fn=_eof_input, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=sup.SCHEMA,
        )
        card = session._build_resume_card()
        menu_text = render_boot_menu(card)
        assert "[fortsetzen] Fortsetzen" in menu_text, menu_text
        assert "None" not in menu_text, menu_text

        session._cmd_menu_fortsetzen()
        # Der alte, irrefuehrende Blockertext darf NICHT mehr erscheinen.
        assert not any("kein tatsaechlich fortsetzbarer Stand gefunden" in p for p in printed), printed
        assert any(p.startswith("Fortsetzen:") for p in printed), printed
        # Keine rohe Python-'None' in der tatsaechlich gedruckten Fortsetzen-Zeile.
        assert not any("None" in p for p in printed), printed
        # `_cmd_local_round([])` wurde real erreicht -- es versucht, eine
        # lokale Runde zu starten (echter Weiterspielweg, keine reine
        # Anzeige-Attrappe). Ohne konfigurierte SL-Anbindung endet das
        # ehrlich mit der bestehenden, unveraenderten Statusmeldung.
        assert any(
            "Lokale Runde" in p or "Abschnitt" in p for p in printed
        ), printed


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
