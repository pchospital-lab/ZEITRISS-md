#!/usr/bin/env python3
"""
tests/mmo_sim/test_r5_fix2_shared_screen_card_owner_binding_2026_11_07.py --
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R5 (Arbeitsblock 1 Punkt 1/4, F2/
UX-R4-02, 02_ABNAHME.md §B "derselbe Bildschirm, unterschiedliche
Menschen").

Vorher war fuer einen Menschen OHNE eigenes registriertes Gastterminal
`io = self` (die AEUSSERE Session) -- die Abschlusskarte las zwar explizit
den angesprochenen `pid`, aber Export (`io._cmd_export()`) und die
Rollenentscheidung fuer die Folgeaktion (`io._host_capable`) bezogen sich
IMMER auf die aeussere Person/Session, nicht auf `pid`. Am geteilten
Terminal (zwei verschiedene Menschen an EINER aeusseren `TuiSession`) hiess
das: die Karte des ZWEITEN Menschen exportierte/entschied ueber den Stand
der ERSTEN (aeusseren) Person.

Dieser Test bildet GENAU diesen gemeinsamen Bildschirm ab (EINE aeussere
`TuiSession`, zwei verschiedene registrierte Figuren/Personen OHNE eigenes
Gastterminal) und belegt am echten `TuiSession`-Code:

1. Die Karte fuer den ZWEITEN Menschen (`pid != session.participant_id`)
   exportiert ECHT dessen eigenen Stand unter dessen eigenem Dateinamen --
   NICHT den der aeusseren Person.
2. Die aeussere (erste) Person bekommt dabei KEINEN fremden Export (keine
   Datei unter ihrem eigenen Namen entsteht aus dieser Aktion).
3. Die Folgeaktion fuer den zweiten Menschen ist 'Tisch suchen/beitreten'
   (Gast-Rolle), NICHT 'Solo-Fortsetzen' -- selbst wenn die AEUSSERE Session
   `host_capable=True` ist (figurfreier Betreiber-Fall).
4. Die figurfreie Betreiber-eigene Tisch-Abschlusskarte
   (`_print_operator_table_completion_card`) bietet strukturell weder
   Export noch Solo-Fortsetzen an (bleibt figurfrei, kein fremder Export/
   kein fremdes Solo).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs, 0
echte GM-/Modellcalls."""
from __future__ import annotations

import json
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

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _scripted_input(values):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return _fn


def _register_private_figure(onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str) -> dict:
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=1)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


def test_shared_screen_card_for_second_person_exports_their_own_save_not_the_outer_one():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        outer_id, outer_char = "betreiber_fix2", "CHR-FIX2-BETREIBER"
        second_id, second_char = "gast_fix2", "CHR-FIX2-GAST"

        # BEIDE Personen teilen sich dieselbe aeussere Session/denselben
        # Onboarding-/Katalog-Root -- genau der "geteilte Bildschirm ohne
        # eigenes Gastterminal"-Fall aus 02_ABNAHME.md §B.
        _register_private_figure(onboarding_dir, catalog_dir, outer_id, outer_char)
        _register_private_figure(onboarding_dir, catalog_dir, second_id, second_char)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=outer_id,
            print_fn=printed.append, host_capable=True,
        )

        # Karte fuer den ZWEITEN Menschen (`pid=second_id != session.
        # participant_id`) -- `io=session` (kein eigenes Gastterminal).
        session._input = _scripted_input(["1"])  # [1] = Export.
        session._print_section_completion_card(session, second_id, saved_now=True)

        second_export = session.exports_dir / f"{second_id}.json"
        outer_export = session.exports_dir / f"{outer_id}.json"
        assert second_export.exists(), (
            "Die Karte des ZWEITEN Menschen haette dessen EIGENEN Stand exportieren muessen.", printed,
        )
        exported = json.loads(second_export.read_text(encoding="utf-8"))
        assert exported.get("characters", [{}])[0].get("id") == second_char, exported
        assert not outer_export.exists(), (
            "Die Karte des ZWEITEN Menschen darf KEINEN Export der AEUSSEREN Person erzeugen "
            "(falscher Besitzer waere ein Datenverlust/-leck fuer die aeussere Person)."
        )


def test_shared_screen_card_for_second_person_offers_guest_follow_up_not_outer_solo():
    """Die Folgeaktion fuer den ZWEITEN Menschen muss 'Tisch suchen/
    beitreten' sein (Gast-Rolle) -- NICHT 'Solo-Fortsetzen', obwohl die
    AEUSSERE Session `host_capable=True` ist (sonst wuerde der zweite
    Mensch die Host-Solo-Rolle der aeusseren Person erben koennen)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        outer_id, outer_char = "betreiber_fix2b", "CHR-FIX2B-BETREIBER"
        second_id, second_char = "gast_fix2b", "CHR-FIX2B-GAST"
        _register_private_figure(onboarding_dir, catalog_dir, outer_id, outer_char)
        _register_private_figure(onboarding_dir, catalog_dir, second_id, second_char)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=outer_id,
            print_fn=printed.append, host_capable=True,
        )
        # '3' = Folgeaktion (nach [1] Export/[2] Zurueck); '/zurueck'
        # verlaesst ein echt aufgerufenes Tisch-Untermenue sofort wieder
        # kontrolliert.
        session._input = _scripted_input(["3", "/zurueck"])
        session._print_section_completion_card(session, second_id, saved_now=False)
        out = "\n".join(printed)
        assert "Tisch suchen/beitreten" in out, (
            "Der zweite Mensch (pid != aeussere participant_id) haette die Gast-Folgeaktion "
            "angeboten bekommen muessen.", out,
        )
        assert "Solo-Fortsetzen" not in out, (
            "Der zweite Mensch darf NICHT die Solo-Fortsetzen-Rolle der aeusseren (host-faehigen) "
            "Person erben.", out,
        )
        assert "Tisch -- [1] Offene Tische suchen" in out, (
            "Die Folgeaktion haette echt `_cmd_menu_tisch()` ausgefuehrt haben muessen.", out,
        )


def test_operator_table_card_stays_figureless_no_export_no_solo():
    """Die figurfreie Betreiber-Tischkarte (`_print_operator_table_
    completion_card`) bietet strukturell weder Export noch Solo-Fortsetzen
    an -- kein fremder Export/kein fremdes Solo fuer den figurfreien
    Betreiber."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        operator_id = "betreiber_fix2c"

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=operator_id,
            print_fn=printed.append, host_capable=True,
        )

        class _FakeTable:
            table_id = "local-fix2c-table"

        session._input = _scripted_input(["3"])  # 3 = Beenden (letzte Nummer).
        session._print_operator_table_completion_card(_FakeTable(), operator_table_key=None)
        out = "\n".join(printed)
        assert "Export" not in out, out
        assert "Solo-Fortsetzen" not in out, out
        assert not (session.exports_dir / f"{operator_id}.json").exists(), (
            "Die figurfreie Betreiberkarte darf NIE einen Export ausloesen."
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
