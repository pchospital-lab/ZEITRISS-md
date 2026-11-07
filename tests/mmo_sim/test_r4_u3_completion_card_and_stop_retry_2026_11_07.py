#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_u3_completion_card_and_stop_retry_2026_11_07.py
ZR-VOLLENDUNG-OHNE-LAN-NACHZUG-20261107-R4 (U3, PLAYER-UX-REVIEW.md F3,
01_NACHZUG.md U3 Punkt 3/5, 02_ABNAHME.md B "Ein Print mit Nummern beweist
keine Nummernauswahl").

Vorher DRUCKTEN `_print_section_completion_card`/`_print_operator_table_
completion_card` nur `1) Export`/`2) Zurueck`/`3) Weiterspielen`, lasen
aber nie eine Auswahl -- der Aufrufer rief ausschliesslich die
Druckfunktion. Dieser Test beweist am echten `TuiSession`-Code, dass die
Nummern jetzt WIRKLICH ausgefuehrt werden:

* `1` (Export) erzeugt tatsaechlich eine Exportdatei mit dem echten
  aktuellen Stand (`_cmd_export`, bestehende Autoritaet).
* `2` (Zurueck) fuehrt KEINE weitere Aktion aus.
* `3` beim figurlosen/ungebundenen Host ruft tatsaechlich den bestehenden
  Current-Resolver (`_cmd_menu_fortsetzen`) auf (echter Funktionsaufruf,
  kein Spy, erkennbar an dessen EIGENEM, nur dort erzeugten Text).
* `3` beim Gast ruft tatsaechlich `_cmd_menu_tisch` auf (zulaessige
  Tischsuche/-beitritt), NICHT das fuer Gaeste gesperrte 'spielen'.

Zusaetzlich (Stop-Retry, F3 "Ein erneuter Start eines gestoppten Abschnitts
sagt weiterhin 'bereits abgeschlossen'"): ein erneuter `tisch-start` auf
denselben, per '/abbrechen' ECHT VERWORFENEN `table_key` nennt den
Abschnitt jetzt NICHT mehr 'bereits abgeschlossen' (Erfolg), sondern
ENDGUELTIG VERWORFEN -- derselbe Fixture-Aufbau wie
`test_zr_betreiber_r2_f3a_abbruch_lifecycle_2026_11_04.py`.

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs,
0 echte GM-/Modellcalls (der Stop-Retry-Host-Pfad nutzt einen Spy, der bei
JEDEM GM-Aufruf sofort AssertionError wirft -- derselbe Beleg wie im
F3a-Treiber)."""
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

from mmo_sim.core import admission as core_admission  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


def _scripted_input(values):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if q:
            return q.pop(0)
        raise EOFError()

    return _fn


def _register_private_figure(onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str) -> dict:
    """Figur OHNE `run_dir`/Current-Veroeffentlichung -- reicht
    `_build_resume_card`/`_cmd_export` als ehrlicher Onboarding-Fallback.
    `bind_for_section` (zusaetzlich zu `register`, Muster aus
    `test_ux1_q04_round_setup_connects_new_person_2026_10_05.py`) setzt
    `last_selected_chrononaut_id` -- OHNE diesen Aufruf liefert `catalog.
    last_selected` weiterhin `None` und `_build_resume_card` haette KEINE
    Figur gefunden."""
    save = full_v7_save(char_id, name=participant_id, save_id=f"fixture-{participant_id}-001", level=1)
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    return save


def test_card_number_1_really_exports_and_number_2_does_nothing():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        host_id, char_id = "host_u3", "CHR-U3-HOST"
        save = _register_private_figure(onboarding_dir, catalog_dir, host_id, char_id)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=host_id,
            print_fn=printed.append, host_capable=True,
        )

        # Nummer 1: echter Export -- eine tatsaechliche Datei entsteht mit
        # dem echten aktuellen Stand.
        session._input = _scripted_input(["1"])
        session._print_section_completion_card(session, host_id, saved_now=True)
        export_path = session.exports_dir / f"{host_id}.json"
        assert export_path.exists(), "Nummer 1 haette eine Exportdatei erzeugen muessen."
        exported = json.loads(export_path.read_text(encoding="utf-8"))
        assert exported.get("characters", [{}])[0].get("id") == char_id, exported

        # Nummer 2: Zurueck -- KEINE weitere Aktion, insbesondere kein
        # erneuter Export-/Fortsetzen-/Tischtext.
        printed.clear()
        session._input = _scripted_input(["2"])
        session._print_section_completion_card(session, host_id, saved_now=False)
        out = "\n".join(printed)
        assert "Zusaetzlich als Datei gespeichert" not in out, out
        assert "Fortsetzen:" not in out, out
        assert save["characters"][0]["id"] == char_id


def test_card_number_3_dispatches_real_fortsetzen_for_unbound_host():
    """`3` bei einem HOST-FAEHIGEN Teilnehmer OHNE bekannten Stand ruft
    tatsaechlich `_cmd_menu_fortsetzen()` auf -- erkennbar an dessen
    EIGENEM Text ('kein tatsaechlich fortsetzbarer Stand gefunden'), der
    NUR von dieser Methode stammt, kein Zufallstreffer."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="unbound_host_u3",
            print_fn=printed.append, host_capable=True,
        )
        # Ohne Figur zeigt die Karte keine Export-Option -- '2' ist dann
        # bereits die (einzige) Folgeaktion 'Solo-Fortsetzen'.
        session._input = _scripted_input(["2"])
        session._print_section_completion_card(session, "unbound_host_u3", saved_now=False)
        out = "\n".join(printed)
        assert "Solo-Fortsetzen" in out, out
        assert "kein tatsaechlich fortsetzbarer Stand gefunden" in out, (
            "Nummer 3/2 haette echt `_cmd_menu_fortsetzen()` aufgerufen haben muessen", out,
        )


def test_card_number_3_dispatches_real_tisch_menu_for_guest_not_locked_spielen():
    """`3` bei einem GAST ruft `_cmd_menu_tisch()` auf (zulaessige
    Tischsuche/-beitritt) -- NICHT das fuer Gaeste gesperrte 'spielen'."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
        guest_id, char_id = "guest_u3", "CHR-U3-GUEST"
        _register_private_figure(onboarding_dir, catalog_dir, guest_id, char_id)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=guest_id,
            print_fn=printed.append, host_capable=False,
        )
        # '3' = Folgeaktion (nach [1] Export/[2] Zurueck); '/zurueck'
        # verlaesst das echte Tisch-Untermenue sofort wieder kontrolliert.
        session._input = _scripted_input(["3", "/zurueck"])
        session._print_section_completion_card(session, guest_id, saved_now=False)
        out = "\n".join(printed)
        assert "Tisch -- [1] Offene Tische suchen" in out, (
            "Nummer 3 haette echt `_cmd_menu_tisch()` aufgerufen haben muessen", out,
        )
        assert "spielen" not in out.lower() or "gesperrt" not in out.lower()


class _SpyGm:
    def turn(self, *a, **kw):
        raise AssertionError("GM-Transport wurde aufgerufen -- unerwartet fuer diesen Stop-Retry-Beleg.")


def test_restart_of_discarded_section_no_longer_claims_success():
    """F3 ("erneuter Start eines gestoppten Abschnitts sagt weiterhin
    'bereits abgeschlossen'"): nach einem echten, bestaetigten '/abbrechen'
    VOR jeder Entscheidung (derselbe Fixture-Aufbau wie
    test_zr_betreiber_r2_f3a_abbruch_lifecycle_2026_11_04.py) nennt ein
    erneuter `tisch-start` auf DIESELBE table_key den Abschnitt jetzt
    ENDGUELTIG VERWORFEN, NICHT 'bereits abgeschlossen' (Erfolg)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        host_onboarding, host_catalog = root / "host_onboarding", root / "host_catalog"
        guest_onboarding, guest_catalog = root / "guest_onboarding", root / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)

        operator_id, guest_id, char_id = "betreiber_u3stop", "gast_u3stop", "CHR-U3STOP"
        table_key = "mesaU3Stop"

        _register_private_figure(guest_onboarding, guest_catalog, guest_id, char_id)

        guest_printed: list[str] = []
        guest_session = TuiSession(
            onboarding_dir=guest_onboarding, catalog_dir=guest_catalog, participant_id=guest_id,
            input_fn=_scripted_input(["/abbrechen"]), print_fn=guest_printed.append,
            run_dir=run_dir, host_capable=False,
        )

        host_session = TuiSession(
            onboarding_dir=host_onboarding, catalog_dir=host_catalog, participant_id=operator_id,
            print_fn=lambda *_a: None,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
            gm_transport_factory=lambda: _SpyGm(),
            host_capable=True,
        )

        host_session._cmd_table_offer([table_key])
        guest_session._cmd_table_request_join([table_key])
        host_session._cmd_table_accept([table_key, guest_id])
        host_session.register_guest_terminal(guest_id, guest_session)

        try:
            host_session._cmd_table_start([table_key])
            raise AssertionError("ein echter Verwurf VOR dem ersten Zug muss ueber EndOfInput zurueckkehren.")
        except EndOfInput:
            pass

        record = table_admission.load_record(run_dir, table_key)
        section_id = record["section_id"]
        decision = core_admission.read_table_decision(run_dir, section_id)
        assert decision is not None and decision.get("decision") == "stopped", decision
        table = core_store.Table.load(run_dir, section_id)
        assert table.status == "closed", table.status

        # Erneuter Start auf DIESELBE table_key -- jetzt der eigentliche
        # Belegpunkt dieses Tests.
        retry_printed: list[str] = []
        host_session._print = retry_printed.append
        host_session._cmd_table_start([table_key])
        retry_out = "\n".join(retry_printed)
        assert "Tischstart abgelehnt" in retry_out and "geschlossen" in retry_out, retry_out
        assert "ENDGUELTIG VERWORFEN" in retry_out, (
            "der Retry haette den dauerhaften Verwurf-Entscheid lesen und benennen muessen", retry_out,
        )
        assert "bereits abgeschlossen" not in retry_out, (
            "ein verworfener Abschnitt darf beim Retry NICHT als 'bereits abgeschlossen' (Erfolg) "
            "bezeichnet werden", retry_out,
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
