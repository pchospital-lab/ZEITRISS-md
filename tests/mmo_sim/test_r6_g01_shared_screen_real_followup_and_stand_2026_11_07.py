#!/usr/bin/env python3
"""
tests/mmo_sim/test_r6_g01_shared_screen_real_followup_and_stand_2026_11_07.py
-- ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R6 (GENERAL-REVIEW.md §2/G-R6-01,
01_NACHZUG.md Arbeitsblock1 Punkt1a, 02_ABNAHME.md §B).

R5 band den Export der Abschlusskarte korrekt an `pid` (`_cmd_export(
participant_id=pid)`), aber die Gastfolge selbst blieb `io._cmd_menu_
tisch()` OHNE Identitaet -- bei `io is self` (geteilter Bildschirm, ZWEITER
Mensch OHNE eigenes registriertes Gastterminal) lief diese Folge auf
`self.participant_id` (der AEUSSEREN Person): die Betreiberzeile [5]-[9]
erschien, obwohl die aeussere Person selbst gar nicht handelte, und eine
echte Tischanfrage waere unter der FALSCHEN `guest_id` gelandet. Der
vorherige R5-Test (`test_r5_fix2_shared_screen_card_owner_binding_2026_
11_07.py`) druckt zwar das Gastmenue, fuehrt aber NIE eine echte Anfrage aus
und sofort '/zurueck' -- genau die in GENERAL-REVIEW.md §2 benannte Luecke
("Warum gruene Tests das uebersehen").

Dieser Test belegt am echten `TuiSession`-Code:

1. Die Betreiberzeile [5]-[9] erscheint NICHT, wenn die Kartenperson
   (`pid`) NICHT die aeussere, host-faehige Person ist -- selbst wenn die
   AEUSSERE Session `host_capable=True` ist.
2. Eine aus der Gastfolge heraus TATSAECHLICH ausgefuehrte neue Tisch-
   Anfrage (Menuepunkt 2) landet unter der `guest_id` der KARTENPERSON
   (`pid`), NICHT unter `self.participant_id` (der aeusseren Person).
3. `self.participant_id` der aeusseren Session bleibt dabei unveraendert
   (kein globales Umschreiben).
4. Ein an GENAU diesem Kartenread eingegebenes '/stand' zeigt den Stand der
   KARTENPERSON (eigene Figur-ID), nicht den der aeusseren Person.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs, 0
echte GM-/Modellcalls."""
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

from _full_v7_fixture import full_v7_save  # noqa: E402

from mmo_sim.core import table_admission  # noqa: E402
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


def test_shared_screen_followup_hides_host_line_for_non_host_card_person():
    """Betreiberzeile [5]-[9] darf NICHT erscheinen, solange die Karten-
    person (`pid`) nicht selbst die aeussere, host-faehige Person ist --
    selbst wenn die aeussere Session `host_capable=True` ist (sonst koennte
    der zweite Mensch Betreiberaktionen der ersten Person uebernehmen)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        outer_id, outer_char = "betreiber_g01", "CHR-G01-BETREIBER"
        second_id, second_char = "gast_g01", "CHR-G01-GAST"
        _register_private_figure(onboarding_dir, catalog_dir, outer_id, outer_char)
        _register_private_figure(onboarding_dir, catalog_dir, second_id, second_char)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=outer_id,
            print_fn=printed.append, host_capable=True, run_dir=run_dir,
        )
        # '3' = Gastfolge -> `_cmd_menu_tisch(acting_pid=second_id)`;
        # '/zurueck' verlaesst das echt aufgerufene Untermenue sofort.
        session._input = _scripted_input(["3", "/zurueck"])
        session._print_section_completion_card(session, second_id, saved_now=False)
        out = "\n".join(printed)
        assert "Betreiber/Host -- [5]" not in out, (
            "Die Betreiberzeile darf fuer eine NICHT-host-faehige Kartenperson am geteilten "
            "Bildschirm nicht erscheinen, selbst wenn die aeussere Session host_capable=True ist.",
            out,
        )
        assert session.participant_id == outer_id, (
            "Die aeussere Session darf durch die Gastfolge NICHT umgeschrieben werden."
        )


def test_shared_screen_followup_real_request_binds_to_card_person_not_outer():
    """Eine aus der Gastfolge heraus TATSAECHLICH ausgefuehrte neue
    Tisch-Anfrage muss unter `pid`s eigener `guest_id` landen -- NICHT unter
    `self.participant_id` (der aeusseren Person). Dies ist die in
    GENERAL-REVIEW.md §2 ausdruecklich geforderte Gegenprobe (eine echte
    Anfrage, nicht nur ein Menuelabel/ein sofortiges '/zurueck')."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        outer_id, outer_char = "betreiber_g01b", "CHR-G01B-BETREIBER"
        second_id, second_char = "gast_g01b", "CHR-G01B-GAST"
        _register_private_figure(onboarding_dir, catalog_dir, outer_id, outer_char)
        _register_private_figure(onboarding_dir, catalog_dir, second_id, second_char)

        # Ein offener Tisch eines DRITTEN Hosts -- weder `outer_id` noch
        # `second_id` ist selbst Host dieses Tisches, damit eine Anfrage
        # eindeutig einer `guest_id` zuzuordnen ist.
        table_key = "tisch-g01b"
        table_admission.offer_table(run_dir, host_id="dritter_host_g01b", table_key=table_key)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=outer_id,
            print_fn=printed.append, host_capable=True, run_dir=run_dir,
        )
        # '3' = Gastfolge; im echten Tisch-Untermenue: '2' = Tisch anfragen,
        # dann der table_key, dann '/zurueck' zum Verlassen.
        session._input = _scripted_input(["3", "2", table_key, "/zurueck"])
        session._print_section_completion_card(session, second_id, saved_now=False)

        record = table_admission.load_record(run_dir, table_key)
        assert record is not None
        assert second_id in record["requests"], (
            "Die ECHTE Tisch-Anfrage haette unter der guest_id der KARTENPERSON (second_id) "
            "landen muessen.", record,
        )
        assert outer_id not in record["requests"], (
            "Die aeussere Person (outer_id) darf durch die Gastfolge der Kartenperson KEINE "
            "eigene Anfrage bekommen.", record,
        )

        # Die eigene Figur der Kartenperson (second_char) wurde angeboten,
        # NICHT die der aeusseren Person (outer_char) -- `table_guest_
        # offers` ist derselbe Sidecar wie `_cmd_table_request_join`.
        offer_dir = run_dir / "table_guest_offers"
        offer_files = list(offer_dir.glob(f"{table_key}__*.json")) if offer_dir.exists() else []
        offer_names = [p.name for p in offer_files]
        assert any(second_id in name for name in offer_names), (
            "Es haette ein Gastangebot unter second_id entstehen muessen.", offer_names,
        )
        assert not any(outer_id in name for name in offer_names), (
            "Es haette KEIN Gastangebot unter outer_id entstehen duerfen.", offer_names,
        )


def test_shared_screen_card_read_stand_shows_card_person_not_outer():
    """'/stand', eingegeben GENAU an der Abschlusskarten-Auswahlzeile
    (`_dispatch_completion_card_choice`s eigener Read, `context=
    "Abschlusskarte"`), muss den Stand der KARTENPERSON zeigen -- nicht
    pauschal `io.participant_id` (die aeussere Person). Vorher fehlte der
    `speaker_pid` an diesem Read vollstaendig (GENERAL-REVIEW.md §2:
    "Der Karten-Read reicht zudem keinen speaker_pid ... weiter")."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        outer_id, outer_char = "betreiber_g01c", "CHR-G01C-BETREIBER"
        second_id, second_char = "gast_g01c", "CHR-G01C-GAST"
        _register_private_figure(onboarding_dir, catalog_dir, outer_id, outer_char)
        _register_private_figure(onboarding_dir, catalog_dir, second_id, second_char)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=outer_id,
            print_fn=printed.append, host_capable=True,
        )
        # '/stand' am Kartenread selbst, dann '2' (Zurueck zum Hauptmenue,
        # keine weitere Aktion).
        session._input = _scripted_input(["/stand", "2"])
        session._print_section_completion_card(session, second_id, saved_now=False)
        out = "\n".join(printed)
        stand_lines = [ln for ln in out.splitlines() if ln.strip().startswith("Fortsetzen:")]
        assert stand_lines, ("Es haette eine 'Fortsetzen:'-Zeile fuer '/stand' geben muessen.", out)
        assert any(second_id in ln and second_char in ln for ln in stand_lines), (
            "'/stand' an der Karte der Kartenperson haette deren EIGENEN Stand "
            "(second_id/second_char) zeigen muessen.", stand_lines,
        )
        assert not any(outer_id in ln or outer_char in ln for ln in stand_lines), (
            "'/stand' haette NICHT den Stand der aeusseren Person (outer_id/outer_char) zeigen "
            "duerfen.", stand_lines,
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
