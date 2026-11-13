#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_k2_kausalabfang_final_save_2026_11_13.py —
ZR-KERN-FEINSCHLIFF-K2-20261113 (Schoepferentscheidung Spieler-Chrononaut-
Tod): Offline-Regression fuer den neuen gemeinsamen Notfallabschluss.

Deckt NUR den engen Terminal-/Schema-Anschluss ab (Produkttext/Regelwerk
ist nicht automatisiert pruefbar):
- `characters[0].status=="deceased"` ist ein reiner, expliziter Marker
  (KEINE LP-Heuristik) -- `zeitriss_saves.is_final_deceased`.
- Beide v7-Schemas (tolerant + strikt/Export) akzeptieren GENAU diesen
  optionalen Marker; ein falscher Wert oder ein Root-Duplikat bleiben
  ausserhalb des kanonischen Exports.
- Ein gemeinsamer Abschluss (ein Final-Save + lebende Mitspieler) harvestet
  ALLE vollstaendigen persoenlichen Saves mit echten Current-/Versionsbytes;
  `CompletionResult` traegt strukturell keinen Missionssieg/Px-Wert.
- Status/Export/Teilnehmerbindung: Wiederaufnahme-/Bogen-/Exportansicht
  benennt das Finale eindeutig, bleibt aber vollstaendig lesbar/exportierbar;
  andere Gruppenmitglieder bleiben unabhaengig spielbar.
- Neue Spielaufnahme (Solo-Start UND Gast-Einladung) mit einer verstorbenen
  Figur wird VOR jedem neuen GM-/SL-Zug gehalten (`TuiSession.
  _final_deceased_hold`, verdrahtet in `_cmd_local_round`/
  `_resume_bound_table`) -- echte Bindung, kein ausgeblendetes Menuelabel.
- Echte Restfertigstellung: ein bereits gepinnter, noch nicht finalisierter
  Abschlussauftrag (`core_store.complete_section` ohne nachfolgendes
  `finalize_section_after_reflection`, d.h. ein echter offener
  `chrononaut_open_completion_order`) haelt NICHT -- eine BELIEBIGE andere
  offene Tischdatei ohne diese konkrete Abschlussautoritaet haelt dagegen
  weiterhin.
- Bewusster Figurenwechsel: `TuiSession._switch_active_figure` wechselt weg
  von der verstorbenen Figur zu einer neuen, ohne die archivierte
  Final-Figur zu veraendern oder automatisch wiederzubeleben.

ZR-KERN-FEINSCHLIFF-K3-20261113-Nachzug (02_BEFUNDE_UND_ZIELVERTRAG.md §C,
04_NACHWEISE_UND_RUECKGABE.md §2 -- schliesst die von K2-VERA-REPORT N-1
benannte Luecke UND die uebrige offene Verhaltensmatrix):
- Echter Gastrequest (`_cmd_table_request_join`), eigene Persona-Anfrage
  (`_cmd_table_request_persona`), Annahme eines bereits vorliegenden
  Final-Angebots (`_cmd_table_accept`) UND frischer Tischstart
  (`_cmd_table_start`) halten VOR jeder Admission-/Figur-Wirkung -- Host-
  UND Gast-/Nicht-Host-Perspektive.
- Der interaktive `b`-Lobby-Eingang (`core.lobby_flow.run_lobby_window`,
  ECHTE Resolver/Guards, kein Attrappen-`_resolve_member`/`_final_
  deceased_hold`) haelt eine verstorbene Figur schon an der
  Rosterauflösung (keine neue Persona-Anbahnung) UND an `play_bound_table`
  (keine neue Tischbindung), waehrend ein anderes Mitglied unabhaengig
  normal spielbereit bleibt.
- Echte Restfertigstellung ueber genau diesen Lobby-Weg: ein real
  gepinnter, noch unfinalisierter Abschlussauftrag mit einer verstorbenen
  Figur wird bis `__final.json`/`status=="closed"`/Lockfreigabe zu Ende
  gefuehrt (KEIN neuer GM-Turn, KEINE doppelte Reflexionsabfrage); ein
  zweiter Lobby-Durchlauf danach bleibt idempotent (kein Crash, keine
  zweite Publikation).

Fakes NUR am GM-Transportrand (`_ExplodingGmTransport`/`_SpyFactory`/
`l01._TableGM`/`_FlexDriver`) -- Produktpersistenz (onboarding/catalog/
core_store/Schemas) laeuft echt, exakt wie in `test_r3_f2_resume_admission_
reconcile.py`/`test_a27_neutral_core.py`/`test_r4_open_plan_resume_
priority_2026_10_23.py`. Pure Python, nur `assert`, echter Exitcode."""
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

import test_l01_l10_lobby_initiative as l01  # noqa: E402
from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    build_two_member_table, clear_lab_stop, make_env, write_lab_stop,
)

from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import lobby_flow  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core import table_admission  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss import save_validation  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import TuiSession, _write_table_guest_offer  # noqa: E402

_SCHEMA_PATH = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"


class _SpyFactory:
    """Reiner Gate-Spy -- JEDER Aufruf ist ein Testversagen (kein neuer
    Modell-/GM-Call erwartet). Muster aus
    `test_r3_f2_resume_admission_reconcile.py:_SpyFactory`."""

    def __init__(self, label: str):
        self.label = label
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError(f"Spy-Factory '{self.label}' wurde aufgerufen (Hold haette VOR jedem Call greifen muessen).")


class _ExplodingGmTransport:
    """AR03/AR04-Muster (`_section_completion_resume_fixtures.
    ExplodingGmTransport`), hier lokal dupliziert (reiner Testcode, keine
    neue Produktabhaengigkeit): KEIN neuer GM-Turn darf fuer eine
    gehaltene verstorbene Figur ausgeloest werden."""

    def __init__(self):
        self.calls = 0

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls += 1
        raise AssertionError("ExplodingGmTransport: kein neuer GM-Turn erwartet -- der Hold haette greifen muessen.")


def _register_own_figure(
    onboarding_dir: Path, catalog_dir: Path, participant_id: str, char_id: str,
    *, run_dir: Path, states_dir: Path, **character_overrides,
) -> dict:
    """Registriert+veroeffentlicht EINE Figur als tatsaechlichen Current-
    Save -- dieselbe Komposition bereits bestehender Produktfunktionen wie
    `test_r3_f2_resume_admission_reconcile.py:_register_own_figure`, hier
    zusaetzlich mit `**character_overrides` (z.B. `status="deceased"`,
    `lp=0`), die `full_v7_save` 1:1 in die EINE Figur mergt."""
    save = full_v7_save(
        char_id, name=participant_id, save_id=f"fixture-{participant_id}-{char_id}",
        **character_overrides,
    )
    onboarding.start_or_resume(onboarding_dir, participant_id)
    onboarding.complete_with_save(onboarding_dir, participant_id, save, ZeitrissHarvestValidator(), char_id)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=participant_id, chrononaut_id=char_id, persona_key=participant_id,
    ))
    catalog.bind_for_section(catalog_dir, participant_id, char_id, has_open_section=False)
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, participant_id, char_id, save)
    core_store.publish_current_save(run_dir, participant_id, save, ps_store, states_dir)
    return save


def _session(onboarding_dir, catalog_dir, participant_id, run_dir, states_dir, *, gm_transport_factory, host_capable=True):
    return TuiSession(
        onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id=participant_id,
        input_fn=lambda *_a, **_kw: "", print_fn=lambda *_a, **_kw: None,
        run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA_PATH,
        gm_transport_factory=gm_transport_factory, persona_driver_factory=_SpyFactory("persona_driver"),
        host_capable=host_capable,
    )


def test_living_oldsave_and_lp0_without_marker_no_auto_death():
    """Fall 1 (Briefing §6): ein bestehender gueltiger Save OHNE Marker
    bleibt angenommen, auch bei `lp=0` -- KEIN automatisch abgeleiteter Tod,
    normale Aufnahme unveraendert. Reine LP-Werte duerfen NIEMALS den
    Marker ersetzen (Harte Grenze §1)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        save = _register_own_figure(
            onboarding_dir, catalog_dir, "p1", "CHR-L1",
            run_dir=run_dir, states_dir=states_dir, lp=0,
        )
        assert "status" not in save["characters"][0], save["characters"][0]
        assert zeitriss_saves.is_final_deceased(save) is False

        session = _session(onboarding_dir, catalog_dir, "p1", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))
        resolved = session._resolve_member("p1")
        assert resolved is not None, "Ein gueltiger Altstand ohne Marker haette resolvbar bleiben muessen."
        active_save, chrono_id = resolved
        assert chrono_id == "CHR-L1"
        assert session._final_deceased_hold(chrono_id, active_save) is None, (
            "LP=0 ohne expliziten Marker darf KEINEN Hold ausloesen (keine LP-Heuristik)."
        )


def test_strict_personal_final_save_passes_structure_wrong_value_and_root_duplicate_fail():
    """Fall 2 (Briefing §6/§4): `characters[0].status='deceased'` passiert
    die volle Struktur-/Schemapruefung (beide unveraenderten v7-Schemas,
    `save_validation.validate_structure`, derselbe Annahmepunkt wie
    `ZeitrissHarvestValidator.validate_block`). Ein falscher Markerwert
    UND ein Root-Duplikat bleiben ausserhalb des kanonischen Exports."""
    good = full_v7_save("CHR-S1", name="S1", status="deceased")
    report_good = save_validation.validate_structure(good)
    assert report_good.valid is True, [e.message for e in report_good.errors]
    assert zeitriss_saves.is_final_deceased(good) is True

    wrong_value = full_v7_save("CHR-S1", name="S1", status="alive")
    report_wrong = save_validation.validate_structure(wrong_value)
    assert report_wrong.valid is False, "status='alive' ist kein deklarierter Enum-Wert -- muss scheitern."

    root_duplicate = full_v7_save("CHR-S1", name="S1", status="deceased")
    root_duplicate["status"] = "deceased"
    report_root = save_validation.validate_structure(root_duplicate)
    assert report_root.valid is False, (
        "Ein Root-Status-Duplikat muss am strikten Export-Schema "
        "(additionalProperties:false auf Root-Ebene) scheitern."
    )

    validator = ZeitrissHarvestValidator()
    assert validator.validate_block(good, "CHR-S1") is True
    assert validator.validate_block(wrong_value, "CHR-S1") is False
    assert validator.validate_block(root_duplicate, "CHR-S1") is False


def test_shared_group_completion_harvests_all_members_without_mission_win_flag():
    """Fall 3 (Briefing §6): kleine synthetische Gruppe (ein bewusster
    Finalstand + lebende Mitspieler) -- alle vollstaendigen persoenlichen
    Saves ueber den normalen Harvest (`core_store.complete_section` ->
    `finalize_section_after_reflection`), echte Current-/Versionsbytes,
    technischer Abschluss wird NICHT als Missionssieg/Px ausgegeben
    (`CompletionResult` hat strukturell kein solches Feld)."""
    import dataclasses

    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        write_test_profile(env.run_dir, max_turns=200)
        lobby, table, ps_store = build_two_member_table(env, table_id="t-shared-abschluss")

        leader_final = full_v7_save("chrono-leader", name="Leader", status="deceased")
        guest_alive = full_v7_save("chrono-guest", name="Guest", lp=8)
        harvested = {"leader_pk": leader_final, "guest_pk": guest_alive}

        result = core_store.complete_section(
            lobby, table, "sec-shared-abschluss", harvested_saves=harvested,
            states_dir=env.states_dir, today="2026-11-13",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        )
        assert result.success, result.reason
        assert not result.missing, result.missing
        assert set(result.members_completed) == {"leader_pk", "guest_pk"}
        completion_fields = {f.name for f in dataclasses.fields(result)}
        assert not (completion_fields & {"px", "mission_success", "mission_win", "cu", "reward"}), (
            f"CompletionResult darf keinen Missionssieg-/Px-/Belohnungswert tragen: {completion_fields}"
        )

        final_result = core_store.finalize_section_after_reflection(lobby, table, "sec-shared-abschluss")
        assert final_result.success, final_result.reason
        assert core_store.Table.load(env.run_dir, table.table_id).status == "closed"

        # ZR-KERN-FEINSCHLIFF-K3-N1 (02 §C-Publikation): `complete_section`
        # (Phase 1, oben) hat die Current-Saves bereits REAL ueber den
        # eigentlichen Produktweg veroeffentlicht (`_write_current_save_
        # version` + Zustandsreferenz) -- diese Pruefung liest GENAU diese
        # bereits vom Produkt geschriebene Publikation. Ein erneutes
        # explizites `publish_current_save` HIER im Test waere eine vom
        # Test selbst erzeugte, selbstbestaetigende Schreibung (kein
        # unabhaengiger Beleg einer eigenstaendigen Produktpublikation) --
        # deshalb bewusst NICHT mehr aufgerufen. Der vollstaendige, ueber
        # den echten GM-/Harvest-Weg erzeugte Publikationsbeleg (inkl.
        # stabilem Versionsbestand bei einem idempotenten zweiten
        # Durchlauf) steht in Test 12
        # (`test_lobby_b_entry_real_resume_completes_open_plan_to_closed_
        # idempotent_second_pass`).
        published_leader = core_store.load_current_save_or_raise(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir)
        published_guest = core_store.load_current_save_or_raise(env.run_dir, "guest_pk", ps_store, states_dir=env.states_dir)
        assert published_leader == leader_final, (
            "Die vom Produkt (complete_section) geschriebene Current-Publikation muss byte-"
            "identisch zum geernteten Final-Save sein."
        )
        assert published_guest == guest_alive, (
            "Die vom Produkt (complete_section) geschriebene Current-Publikation muss byte-"
            "identisch zum geernteten lebenden Save sein."
        )
        assert zeitriss_saves.is_final_deceased(published_leader) is True
        assert zeitriss_saves.is_final_deceased(published_guest) is False


def test_resume_card_bogen_export_name_the_finale_other_member_stays_playable():
    """Fall 4 (Briefing §6): Wiederaufnahme-/Abschlussansicht benennt das
    Finale eindeutig; eigener Export bleibt komplett und gehoert der
    richtigen Person (auch an einem geteilten Terminal); andere
    Gruppenmitglieder bleiben unabhaengig spielbar."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        deceased_save = _register_own_figure(
            onboarding_dir, catalog_dir, "p4", "CHR-E1",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        _register_own_figure(
            onboarding_dir, catalog_dir, "p4b", "CHR-E2",
            run_dir=run_dir, states_dir=states_dir,
        )

        session = _session(onboarding_dir, catalog_dir, "p4", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))

        card = session._build_resume_card(participant_id="p4")
        assert card is not None and card.last_valid_save_summary is not None
        assert "deceased" in card.last_valid_save_summary or "Legendenabschied" in card.last_valid_save_summary, (
            card.last_valid_save_summary
        )
        assert "andere/neue Figur" in card.last_valid_save_summary

        printed: list[str] = []
        session._print = printed.append
        session._cmd_export(participant_id="p4")
        joined = "\n".join(printed)
        assert "deceased" in joined, "Der Export muss den Final-Marker sichtbar enthalten."
        export_path = session.exports_dir / "p4.json"
        assert export_path.exists(), "Export-Datei haette geschrieben werden muessen."
        import json as _json
        assert _json.loads(export_path.read_text(encoding="utf-8")) == deceased_save

        printed.clear()
        # T5 (03_NACHWEISE): NUR die aeussere Fenster-/Desktopoeffnungs-
        # grenze (`sheet_view.try_open_in_external_terminal`) wird
        # gestubbt, damit der Test offline/CI-sicher bleibt (kein echtes
        # Terminalfenster/Browser) -- der echte Produkt-Bogenpfad
        # (`_cmd_show_bogen` selbst, der reale Current-Leser, der
        # Renderer `sheet_view.render_character_sheet`) bleibt
        # UNVERAENDERT und wird real durchlaufen. Danach wird der
        # Originalzustand zurueckgesetzt -- ein realer Fensterstart ist
        # KEIN zulaessiger Offline-Nachweis, aber auch kein verlangtes
        # Verbot des Zweigs selbst.
        from mmo_sim.ui import sheet_view as _sheet_view_module
        _original_try_open_in_external_terminal = _sheet_view_module.try_open_in_external_terminal
        _sheet_view_module.try_open_in_external_terminal = lambda *_a, **_kw: True
        try:
            session._cmd_show_bogen(speaker_pid="p4")
        finally:
            _sheet_view_module.try_open_in_external_terminal = _original_try_open_in_external_terminal
        # Read-only, darf nicht crashen -- der (gestubbte) externe-
        # Terminal-Zweig greift hier deterministisch, kein lokaler Druck
        # noetig/erwartet.

        other_resolved = session._resolve_member("p4b")
        assert other_resolved is not None
        other_save, other_chrono = other_resolved
        assert session._final_deceased_hold(other_chrono, other_save) is None, (
            "Ein anderes Gruppenmitglied ohne eigenen Final-Save darf NICHT gehalten werden."
        )


def test_new_solo_start_and_guest_invite_hold_with_deceased_figure_no_new_gm_turn():
    """Fall 5 (Briefing §6): direkter Solo-Start UND ein neues Gastangebot
    mit der finalen Figur erzeugen KEINEN neuen GM-Spielzug und KEINE neue
    zulaessige Spielbindung -- echte Bindung haelt, nicht nur ausgeblendete
    Menuelabels. Prueft ALLE aufgenommenen Mitglieder, nicht nur den Host."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            onboarding_dir, catalog_dir, "p5host", "CHR-H5",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        gm = _ExplodingGmTransport()
        host_session = _session(
            onboarding_dir, catalog_dir, "p5host", run_dir, states_dir,
            gm_transport_factory=lambda: gm,
        )
        printed: list[str] = []
        host_session._print = printed.append
        host_session._cmd_local_round([])
        joined = "\n".join(printed)
        assert "Legendenabschied" in joined and "andere/neue Figur" in joined, joined
        assert gm.calls == 0, "Solo-Start mit verstorbener Figur haette KEINEN GM-Turn ausloesen duerfen."

        # Gast-Einladung: Host lebt, der eingeladene Gast ist die
        # verstorbene Figur -- der Hold muss GENAU fuer den Gast greifen
        # (nicht nur fuer den Host gepruefte Bindung).
        _register_own_figure(
            onboarding_dir, catalog_dir, "p5host2", "CHR-H5B",
            run_dir=run_dir, states_dir=states_dir,
        )
        from mmo_sim.registry.participants import Participant, ParticipantRegistry
        registry = ParticipantRegistry(onboarding_dir.parent / "registry")
        registry._save(Participant(participant_id="p5guest", kind="human", display_name="p5guest"))
        _register_own_figure(
            onboarding_dir, catalog_dir, "p5guest", "CHR-G5",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        gm2 = _ExplodingGmTransport()
        host2_session = _session(
            onboarding_dir, catalog_dir, "p5host2", run_dir, states_dir,
            gm_transport_factory=lambda: gm2,
        )
        printed2: list[str] = []
        host2_session._print = printed2.append
        host2_session._cmd_local_round(["p5guest"])
        joined2 = "\n".join(printed2)
        assert "p5guest" in joined2 and "Legendenabschied" in joined2, joined2
        assert gm2.calls == 0, "Eine Gasteinladung mit verstorbener Figur haette KEINEN GM-Turn ausloesen duerfen."


def test_genuine_open_completion_order_holds_exception_arbitrary_table_file_does_not():
    """Fall 6 (Briefing §6/§5): ein tatsaechlich bereits angefangener
    Abschlussauftrag mit geerntetem Final-Current (`complete_section` ohne
    nachfolgendes `finalize_section_after_reflection`, also ein echter
    offener `chrononaut_open_completion_order`) haelt NICHT -- die
    Restfertigstellung bleibt erreichbar. Eine BELIEBIGE andere, nicht an
    DIESE Figur gebundene offene Tischdatei ist dagegen KEINE Ausnahme."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        write_test_profile(env.run_dir, max_turns=200)
        lobby, table, ps_store = build_two_member_table(env, table_id="t-restfertigstellung")

        leader_final = full_v7_save("chrono-leader", name="Leader", status="deceased")
        guest_alive = full_v7_save("chrono-guest", name="Guest", lp=6)
        result = core_store.complete_section(
            lobby, table, "sec-restfertigstellung",
            harvested_saves={"leader_pk": leader_final, "guest_pk": guest_alive},
            states_dir=env.states_dir, today="2026-11-13",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        )
        assert result.success, result.reason
        # KEIN finalize_section_after_reflection hier -- der Plan bleibt
        # gepinnt, aber unfinalisiert (genau der offene Abschlussauftrag).
        assert core_store.chrononaut_open_completion_order(env.run_dir, "chrono-leader") is True, (
            "Testvoraussetzung: der Plan muss real offen (gepinnt, ohne __final.json) sein."
        )

        onboarding_dir, catalog_dir = env.run_dir.parent / "onboarding", env.run_dir.parent / "catalog"
        core_store.publish_current_save(env.run_dir, "leader_pk", leader_final, ps_store, env.states_dir)
        onboarding.start_or_resume(onboarding_dir, "leader_pk")
        onboarding.complete_with_save(onboarding_dir, "leader_pk", leader_final, ZeitrissHarvestValidator(), "chrono-leader")

        session = _session(onboarding_dir, catalog_dir, "leader_pk", env.run_dir, env.states_dir, gm_transport_factory=_SpyFactory("gm"))
        resolved = session._resolve_member("leader_pk")
        assert resolved is not None
        active_save, chrono_id = resolved
        assert chrono_id == "chrono-leader"
        # K3 (02 §C Z.37/43): die Ausnahme ist jetzt TISCHGEBUNDEN -- fuer
        # GENAU den gebundenen Tisch mit echtem offenem Abschluss hebt sie
        # den Hold auf. Der Aufrufer uebergibt dafuer `completing_table_id`
        # (an jeder echten Resume-Stelle die Figur ohnehin aus der
        # Tisch-Roster aufgeloest).
        assert session._final_deceased_hold(
            chrono_id, active_save, completing_table_id="t-restfertigstellung",
        ) is None, (
            "Ein echter offener Abschlussauftrag fuer GENAU diesen gebundenen Tisch "
            "(open_completion_order_for_table) muss den Hold aufheben."
        )
        # K3 D-1 (Kreuztisch-Negativfall, 02 §C Z.43 'derselbe Chrononaut mit
        # einem anderen neuen Angebot genuegt nicht'): dieselbe reale Figur
        # mit offenem Abschluss fuer Tisch A, aber eine Aktion fuer einen
        # ANDEREN Tisch B (kein eigener offener Abschluss dort) bleibt
        # gehalten -- der offene Abschluss fuer A ist KEINE Pauschal-Erlaubnis.
        assert session._final_deceased_hold(
            chrono_id, active_save, completing_table_id="t-ein-ganz-anderer-tisch",
        ) is not None, (
            "Ein offener Abschluss fuer Tisch A darf eine neue Aktion an Tisch B "
            "NICHT durchlassen (02 §C Zeile 37/43)."
        )
        # Und ganz ohne Tischkontext (jeder Neustart/jedes neue Angebot) gibt
        # es keine Ausnahme.
        assert session._final_deceased_hold(chrono_id, active_save) is not None, (
            "Ohne `completing_table_id` (neuer Start/neues Angebot) bleibt der Hold bestehen."
        )

        # Gegenprobe: eine voellig unbeteiligte verstorbene Figur, OHNE
        # jeden eigenen offenen Abschlussauftrag in DIESEM run_dir, bleibt
        # trotz der oben existierenden Tischdatei gehalten -- "eine
        # beliebige offene Tischdatei genuegt nicht".
        assert core_store.chrononaut_open_completion_order(env.run_dir, "chrono-unrelated-elsewhere") is False
        unrelated_save = full_v7_save("chrono-unrelated-elsewhere", name="Unrelated", status="deceased")
        assert session._final_deceased_hold("chrono-unrelated-elsewhere", unrelated_save) is not None, (
            "Eine beliebige offene Tischdatei fuer eine ANDERE Figur darf den Hold nicht aufheben."
        )


def test_conscious_character_switch_preserves_archived_final_no_auto_revival():
    """Fall 7 (Briefing §6): nach dem Abschluss waehlt die Person bewusst
    eine andere/neue Figur (`TuiSession._switch_active_figure`, bestehender
    Wechselweg) -- die vorhandene ausgehende Archivierung bewahrt den
    exakten finalen Stand unveraendert, kein Fallback auf eine fruehere
    lebende Generation, keine automatische Wiederbelebung/Ersatzfigur."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        deceased_save = _register_own_figure(
            onboarding_dir, catalog_dir, "p7", "CHR-D7",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        new_save = full_v7_save("CHR-N7", name="p7", save_id="fixture-p7-CHR-N7")
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id="p7", chrononaut_id="CHR-N7", persona_key="p7",
        ))
        catalog.store_figure_save(catalog_dir, "p7", "CHR-N7", new_save)

        session = _session(onboarding_dir, catalog_dir, "p7", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))
        entries = catalog.list_for_participant(catalog_dir, "p7")
        printed: list[str] = []
        session._print = printed.append
        session._switch_active_figure("CHR-N7", entries)
        assert any("CHR-N7" in p for p in printed), printed

        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        published = core_store.load_current_save_or_raise(run_dir, "p7", ps_store, states_dir=states_dir)
        assert zeitriss_saves.block_char_id(published) == "CHR-N7", (
            "Nach dem bewussten Wechsel muss die NEUE Figur der aktive Current sein."
        )
        assert zeitriss_saves.is_final_deceased(published) is False

        archived = catalog.load_figure_save(catalog_dir, "p7", "CHR-D7")
        assert archived == deceased_save, (
            "Die archivierte verstorbene Figur darf durch den Wechsel NICHT veraendert worden sein "
            "(kein Fallback, keine automatische Wiederbelebung)."
        )

        resolved_new = session._resolve_member("p7")
        assert resolved_new is not None
        new_active_save, new_chrono_id = resolved_new
        assert new_chrono_id == "CHR-N7"
        assert session._final_deceased_hold(new_chrono_id, new_active_save) is None, (
            "Die neue, lebende aktive Figur darf keinen Hold mehr ausloesen."
        )


def test_table_request_join_and_persona_request_hold_with_final_figure_host_and_guest():
    """Fall 8 (K3, 02 §C / 04 §2 'Neue Aufnahme ohne Ausnahme'): ein echter
    Gastrequest (`_cmd_table_request_join`, Nicht-Host-Perspektive) UND
    eine eigene Persona-Anfrage (`_cmd_table_request_persona`, Host-
    Perspektive) mit GENAU der finalen Figur halten VOR jeder Admission-
    Wirkung -- kein Request-Write, kein Gastangebot-Sidecar."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            onboarding_dir, catalog_dir, "p8host", "CHR-H8",
            run_dir=run_dir, states_dir=states_dir,
        )
        _register_own_figure(
            onboarding_dir, catalog_dir, "p8guest", "CHR-G8",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )

        host = _session(onboarding_dir, catalog_dir, "p8host", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm-host"))
        host._cmd_table_offer(["t8"])

        guest = _session(
            onboarding_dir, catalog_dir, "p8guest", run_dir, states_dir,
            gm_transport_factory=_SpyFactory("gm-guest"), host_capable=False,
        )
        printed: list[str] = []
        guest._print = printed.append
        guest._cmd_table_request_join(["t8"])
        joined = "\n".join(printed)
        assert "Legendenabschied" in joined, joined

        record = table_admission.load_record(run_dir, "t8")
        assert record["requests"] == [], f"Ein gehaltener Request darf die Admission nicht mutieren: {record}"
        from mmo_sim.ui.tui import _read_table_guest_offer
        assert _read_table_guest_offer(run_dir, "t8", "p8guest") is None, (
            "Ein gehaltener Request darf KEIN Gastangebot-Sidecar schreiben."
        )

        # Host-Perspektive: eigene Persona-Anfrage mit einer eigenen,
        # bereits abgeschlossenen finalen Figur haelt ebenso, VOR jedem
        # `table_admission`-Write (`_known_ai_overview` hier gezielt
        # ersetzt -- reine Bestandsermittlung, NICHT der tatsaechlich
        # geprueften `_resolve_member`/`_final_deceased_hold`-Autoritaet).
        _register_own_figure(
            onboarding_dir, catalog_dir, "p8persona", "CHR-P8",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        host._known_ai_overview = lambda: [("p8persona", "Testpersona (Simuliert)")]
        printed2: list[str] = []
        host._print = printed2.append
        host._cmd_table_request_persona(["t8", "p8persona"])
        joined2 = "\n".join(printed2)
        assert "Legendenabschied" in joined2, joined2
        record2 = table_admission.load_record(run_dir, "t8")
        assert record2["requests"] == [], f"Eine gehaltene Persona-Anfrage darf die Admission nicht mutieren: {record2}"


def test_table_accept_holds_pending_guest_offer_with_final_figure_no_roster_write():
    """Fall 9 (K3, 02 §C 'schon vorhandene Gastangebote ... Endstatus ...
    pruefen'): `_cmd_table_accept` haelt ein bereits vorliegendes
    Gastangebot-Sidecar mit einer endgueltig abgeschlossenen Figur VOR
    `accept_request`/Figurenuebernahme -- kein Roster-Write, Sidecar UND
    offene Anfrage bleiben unveraendert erhalten (retry-faehig nach einer
    bewussten anderen Figurenwahl)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            onboarding_dir, catalog_dir, "p9host", "CHR-H9",
            run_dir=run_dir, states_dir=states_dir,
        )
        host = _session(onboarding_dir, catalog_dir, "p9host", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))
        host._cmd_table_offer(["t9"])
        table_admission.request_join(run_dir, table_key="t9", guest_id="p9guest")

        deceased_offer_save = full_v7_save("CHR-G9", name="p9guest", status="deceased")
        _write_table_guest_offer(run_dir, "t9", "p9guest", chrononaut_id="CHR-G9", save=deceased_offer_save)

        printed: list[str] = []
        host._print = printed.append
        host._cmd_table_accept(["t9", "p9guest"])
        joined = "\n".join(printed)
        assert "Legendenabschied" in joined, joined

        record = table_admission.load_record(run_dir, "t9")
        assert "p9guest" not in record["roster"], record
        assert "p9guest" in record["requests"], "Die offene Anfrage bleibt bestehen -- kein stiller Abbruch."
        from mmo_sim.ui.tui import _read_table_guest_offer
        assert _read_table_guest_offer(run_dir, "t9", "p9guest") is not None, (
            "Das Gastangebot-Sidecar muss erhalten bleiben (retry-faehig)."
        )


def test_table_accept_holds_without_sidecar_when_own_current_deceased_no_roster_write():
    """Fall 9a (02 §A2, Belegte Luecke 'ohne Sidecar gibt es GAR KEINEN
    Hold'): eine reine ID-Anfrage OHNE Gastangebot-Sidecar haelt trotzdem,
    wenn die EIGENE, inzwischen final gewordene Current-Figur des Gasts
    betroffen ist -- VOR `accept_request`. Echte VORHER/NACHHER-Byte-
    vergleiche (Roster-Record, Current-Save-Versionsverzeichnis, Katalog)
    beweisen 0 Writes statt einer blossen Textassertion."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            onboarding_dir, catalog_dir, "p9ahost", "CHR-H9A",
            run_dir=run_dir, states_dir=states_dir,
        )
        _register_own_figure(
            onboarding_dir, catalog_dir, "p9aguest", "CHR-G9A",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        host = _session(onboarding_dir, catalog_dir, "p9ahost", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))
        host._cmd_table_offer(["t9a"])
        table_admission.request_join(run_dir, table_key="t9a", guest_id="p9aguest")
        from mmo_sim.ui.tui import _read_table_guest_offer
        assert _read_table_guest_offer(run_dir, "t9a", "p9aguest") is None, (
            "Testvoraussetzung: reine ID-Anfrage OHNE Sidecar."
        )

        record_path = run_dir / "table_admission" / "t9a.json"
        versions_dir = run_dir / "current_saves" / "p9aguest__versions"
        catalog_path = catalog_dir / "catalog__p9aguest.json"
        before = (
            record_path.read_bytes(),
            sorted((p.name, p.read_bytes()) for p in versions_dir.glob("*.json")),
            catalog_path.read_bytes() if catalog_path.exists() else None,
        )

        printed: list[str] = []
        host._print = printed.append
        host._cmd_table_accept(["t9a", "p9aguest"])
        joined = "\n".join(printed)
        assert "Legendenabschied" in joined, joined

        after = (
            record_path.read_bytes(),
            sorted((p.name, p.read_bytes()) for p in versions_dir.glob("*.json")),
            catalog_path.read_bytes() if catalog_path.exists() else None,
        )
        assert before == after, "Ohne Sidecar darf eine final gewordene eigene Figur trotzdem 0 Writes verursachen."

        record = table_admission.load_record(run_dir, "t9a")
        assert "p9aguest" not in record["roster"], record
        assert "p9aguest" in record["requests"], "Die offene Anfrage bleibt bestehen -- kein stiller Abbruch."


def test_table_accept_holds_sidecar_living_same_figure_when_current_already_final():
    """Fall 9b (02 §A3, Belegte Luecke 'aelterer lebender Sidecar ... die
    massgebliche finale Autoritaet derselben Figur wird nicht geprueft --
    auch nicht nach a/k'): der Sidecar traegt eine AELTERE, noch lebende
    Fassung GENAU der Figur, deren massgeblicher (Current-)Stand
    inzwischen final geworden ist -- der Hold muss VOR jeder a/k-
    Konfliktwahl greifen, NICHT erst danach (weder 'a' noch 'k'
    erreichbar)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            onboarding_dir, catalog_dir, "p9bhost", "CHR-H9B",
            run_dir=run_dir, states_dir=states_dir,
        )
        guest_alive_save = _register_own_figure(
            onboarding_dir, catalog_dir, "p9bguest", "CHR-G9B",
            run_dir=run_dir, states_dir=states_dir,
        )
        assert zeitriss_saves.is_final_deceased(guest_alive_save) is False
        # Die Figur stirbt NACH der urspruenglichen Registrierung -- derselbe
        # Current wird erneut mit status=deceased veroeffentlicht (Muster
        # Fall 10). Der Sidecar unten bleibt bewusst die AELTERE, noch
        # lebende Fassung (z.B. vor dem Tod aufgezeichnet).
        guest_deceased_save = full_v7_save("CHR-G9B", name="p9bguest", status="deceased")
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        core_store.publish_current_save(run_dir, "p9bguest", guest_deceased_save, ps_store, states_dir)

        host = _session(onboarding_dir, catalog_dir, "p9bhost", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))
        host._cmd_table_offer(["t9b"])
        table_admission.request_join(run_dir, table_key="t9b", guest_id="p9bguest")
        from mmo_sim.ui.tui import _write_table_guest_offer, _read_table_guest_offer
        _write_table_guest_offer(run_dir, "t9b", "p9bguest", chrononaut_id="CHR-G9B", save=guest_alive_save)

        record_path = run_dir / "table_admission" / "t9b.json"
        sidecar_path = run_dir / "table_guest_offers" / "t9b__p9bguest.json"
        versions_dir = run_dir / "current_saves" / "p9bguest__versions"
        before = (
            record_path.read_bytes(), sidecar_path.read_bytes(),
            sorted((p.name, p.read_bytes()) for p in versions_dir.glob("*.json")),
        )

        printed: list[str] = []
        host._print = printed.append
        host._cmd_table_accept(["t9b", "p9bguest"])
        joined = "\n".join(printed)
        assert "Legendenabschied" in joined, joined
        assert "Konfliktwahl" not in joined, (
            f"Der Hold muss VOR jedem a/k-Konfliktdialog greifen, nicht erst danach: {joined}"
        )

        after = (
            record_path.read_bytes(), sidecar_path.read_bytes(),
            sorted((p.name, p.read_bytes()) for p in versions_dir.glob("*.json")),
        )
        assert before == after, "0 Writes trotz aelterem lebenden Sidecar derselben, inzwischen finalen Figur."

        record = table_admission.load_record(run_dir, "t9b")
        assert "p9bguest" not in record["roster"], record
        assert _read_table_guest_offer(run_dir, "t9b", "p9bguest") is not None, (
            "Das Gastangebot-Sidecar muss erhalten bleiben (retry-faehig)."
        )


def test_table_accept_holds_missing_host_onboarding_projection_with_shared_final_current():
    """Fall 9c (02 §A, Belegte Luecke 'fehlende Host-Onboarding-Projektion
    bei real vorhandenem gemeinsamen Current'): der Gast hat seine eigene,
    SEPARATE Onboarding-/Katalogwurzel (realer Launcher, scripts/
    mmo_sim.py), aber einen mit dem Host GETEILTEN run_dir/states_dir --
    die Figur ist dort bereits final (deceased) veroeffentlicht UND das
    Sidecar-Angebot traegt BYTEIDENTISCH genau diesen Stand. Der Host hat
    fuer diesen Gast noch KEINE eigene Onboarding-Projektion -- der Hold
    muss GENAU VOR dem `noop_identical`-Host-projektions-Write greifen,
    der sonst (R6 B) diese fehlende Projektion automatisch nachtragen
    wuerde."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        host_onboarding_dir, host_catalog_dir = d / "host_onboarding", d / "host_catalog"
        guest_onboarding_dir, guest_catalog_dir = d / "guest_onboarding", d / "guest_catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            host_onboarding_dir, host_catalog_dir, "p9chost", "CHR-H9C",
            run_dir=run_dir, states_dir=states_dir,
        )
        guest_save = _register_own_figure(
            guest_onboarding_dir, guest_catalog_dir, "p9cguest", "CHR-G9C",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        assert onboarding.peek(host_onboarding_dir, "p9cguest") is None, (
            "Testvoraussetzung: der Host hat fuer den Gast noch KEINE eigene Onboarding-Projektion."
        )

        host = _session(
            host_onboarding_dir, host_catalog_dir, "p9chost", run_dir, states_dir,
            gm_transport_factory=_SpyFactory("gm"),
        )
        host._cmd_table_offer(["t9c"])
        table_admission.request_join(run_dir, table_key="t9c", guest_id="p9cguest")
        from mmo_sim.ui.tui import _write_table_guest_offer, _read_table_guest_offer
        _write_table_guest_offer(run_dir, "t9c", "p9cguest", chrononaut_id="CHR-G9C", save=guest_save)

        # T4 (03_NACHWEISE, 'fehlende-Hostprojektion-Fall'): die
        # tatsaechlich beruehrbaren Artefakte VOR dem gehaltenen Accept
        # binden -- der Host-Onboarding-Slot und der Host-Katalogeintrag
        # fuer den Gast existieren noch NICHT (das ist genau die Luecke,
        # die `noop_identical` sonst nachtragen wuerde); Sidecar/Request/
        # Record UND der geteilte Current-Versionsbestand des Gasts
        # muessen danach unveraendert bleiben.
        record_path = run_dir / "table_admission" / "t9c.json"
        sidecar_path = run_dir / "table_guest_offers" / "t9c__p9cguest.json"
        host_catalog_path = host_catalog_dir / "catalog__p9cguest.json"
        guest_versions_dir = run_dir / "current_saves" / "p9cguest__versions"
        before = (
            record_path.read_bytes(), sidecar_path.read_bytes(),
            host_catalog_path.exists(),
            sorted((p.name, p.read_bytes()) for p in guest_versions_dir.glob("*.json")),
        )

        printed: list[str] = []
        host._print = printed.append
        host._cmd_table_accept(["t9c", "p9cguest"])
        joined = "\n".join(printed)
        assert "Legendenabschied" in joined, joined

        after = (
            record_path.read_bytes(), sidecar_path.read_bytes(),
            host_catalog_path.exists(),
            sorted((p.name, p.read_bytes()) for p in guest_versions_dir.glob("*.json")),
        )
        assert before == after, (
            "Der Hold muss ALLE tatsaechlich beruehrbaren Artefakte unveraendert lassen "
            "(Record/Sidecar/Host-Katalogdatei/geteilter Current-Versionsbestand)."
        )

        record = table_admission.load_record(run_dir, "t9c")
        assert "p9cguest" not in record["roster"], record
        assert onboarding.peek(host_onboarding_dir, "p9cguest") is None, (
            "Der Hold muss die sonst vom noop_identical-Zweig nachgetragene Host-Onboarding-"
            "Projektion verhindern -- 0 Writes, auch keine Host-Projektion."
        )
        assert catalog.list_for_participant(host_catalog_dir, "p9cguest") == [], (
            "Kein Host-Katalogeintrag fuer den Gast -- 0 Writes."
        )
        assert _read_table_guest_offer(run_dir, "t9c", "p9cguest") is not None, (
            "Das Gastangebot-Sidecar muss erhalten bleiben (retry-faehig)."
        )


def test_table_accept_holds_archived_offered_figure_with_final_archive_state():
    """Fall 9d (02 §A1, dritte Autoritaetsstufe Archiv): die angebotene
    eigene Figur hat KEINEN veroeffentlichten Current und KEINEN
    Onboarding-Slot fuer DIESE Figur, aber einen bekannten, finalen Stand
    im GETRENNTEN Katalog-/Archivspeicher (`catalog.load_figure_save`) --
    die dritte Autoritaetsstufe von `_authoritative_final_save_for` muss
    den Hold GENAUSO VOR jeder a/k-Konfliktwahl ausloesen."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            onboarding_dir, catalog_dir, "p9dhost", "CHR-H9D",
            run_dir=run_dir, states_dir=states_dir,
        )
        # Der Gast hat NIE eine eigene Figur ueber onboarding/Current
        # veroeffentlicht -- NUR ein getrennter Archiveintrag (z.B. aus
        # einem frueheren Import/Export) mit finalem Stand liegt vor.
        archived_final_save = full_v7_save("CHR-G9D", name="p9dguest", status="deceased")
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id="p9dguest", chrononaut_id="CHR-G9D", persona_key="p9dguest",
        ))
        catalog.store_figure_save(catalog_dir, "p9dguest", "CHR-G9D", archived_final_save)

        host = _session(onboarding_dir, catalog_dir, "p9dhost", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))
        host._cmd_table_offer(["t9d"])
        table_admission.request_join(run_dir, table_key="t9d", guest_id="p9dguest")
        # Sidecar-Angebot: eine ANDERE (z.B. frisch importierte, lebende)
        # Byte-Fassung GENAU dieser char_id -- der reine Sidecar-Hold
        # (`guest_offer["save"]`) greift bewusst NICHT, nur die Archiv-
        # Autoritaet ueber `_authoritative_final_save_for`.
        offered_living_save = full_v7_save("CHR-G9D", name="p9dguest", lp=4)
        assert zeitriss_saves.is_final_deceased(offered_living_save) is False
        from mmo_sim.ui.tui import _write_table_guest_offer, _read_table_guest_offer
        _write_table_guest_offer(run_dir, "t9d", "p9dguest", chrononaut_id="CHR-G9D", save=offered_living_save)

        record_path = run_dir / "table_admission" / "t9d.json"
        sidecar_path = run_dir / "table_guest_offers" / "t9d__p9dguest.json"
        # T4 (03_NACHWEISE): `catalog__p9dguest.json` ist NUR der
        # Katalog-Metadaten-Eintrag (Entry-Liste/Bindung) -- die
        # Archiv-AUTORITAET selbst (`_authoritative_final_save_for`s
        # dritte Stufe liest `catalog.load_figure_save`) liegt in den
        # echten Figurenbytes unter `figures/pid__char.json`. Beide Pfade
        # werden hier getrennt vor/nach gebunden, damit "0 Writes" sich
        # tatsaechlich auf die massgebliche Archivquelle bezieht, nicht
        # nur auf die Metadatendatei.
        archive_meta_path = catalog_dir / "catalog__p9dguest.json"
        archive_figure_path = catalog_dir / "figures" / "p9dguest__CHR-G9D.json"
        assert archive_figure_path.exists(), "Testvoraussetzung: echte Figurenbytes muessen bereits vorliegen."
        assert catalog.load_figure_save(catalog_dir, "p9dguest", "CHR-G9D") == archived_final_save
        before = (
            record_path.read_bytes(), sidecar_path.read_bytes(),
            archive_meta_path.read_bytes(), archive_figure_path.read_bytes(),
        )

        printed: list[str] = []
        host._print = printed.append
        host._cmd_table_accept(["t9d", "p9dguest"])
        joined = "\n".join(printed)
        assert "Legendenabschied" in joined, joined
        assert "Konfliktwahl" not in joined, joined

        after = (
            record_path.read_bytes(), sidecar_path.read_bytes(),
            archive_meta_path.read_bytes(), archive_figure_path.read_bytes(),
        )
        assert before == after, (
            "0 Writes trotz Archiv-Autoritaet ueber die dritte Stufe (Katalog-Metadaten UND "
            "echte Figurenbytes unter figures/pid__char.json)."
        )
        assert catalog.load_figure_save(catalog_dir, "p9dguest", "CHR-G9D") == archived_final_save, (
            "Die archivierte finale Figur darf durch den gehaltenen Accept nicht veraendert werden."
        )

        record = table_admission.load_record(run_dir, "t9d")
        assert "p9dguest" not in record["roster"], record
        assert _read_table_guest_offer(run_dir, "t9d", "p9dguest") is not None


def test_table_accept_positive_counterexamples_remain_admitted():
    """Gegenproben (02 §A, Invariante 'eine bewusst gewaehlte ANDERE
    lebende Figur derselben Person bleibt zulaessig'): drei Faelle, die
    trotz der neuen Holds WEITERHIN normal angenommen werden muessen --
    eine gueltige lebende Figur, eine reine ID-Anfrage ohne eigene Figur,
    und eine bewusst ANDERE lebende Figur derselben Person, waehrend eine
    FRUEHERE eigene Figur bereits final/archiviert ist (char-gebundener
    Hold, keine Pauschalsperre der Person)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            onboarding_dir, catalog_dir, "p9host", "CHR-H9POS",
            run_dir=run_dir, states_dir=states_dir,
        )
        host = _session(onboarding_dir, catalog_dir, "p9host", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))
        host._cmd_table_offer(["t9pos"])
        from mmo_sim.ui.tui import _write_table_guest_offer

        # (1) gueltige lebende Figur -- normale Annahme, Figur wird
        # uebernommen.
        guest_living_save = _register_own_figure(
            onboarding_dir, catalog_dir, "p9guest1", "CHR-G9POS1",
            run_dir=run_dir, states_dir=states_dir,
        )
        table_admission.request_join(run_dir, table_key="t9pos", guest_id="p9guest1")
        _write_table_guest_offer(run_dir, "t9pos", "p9guest1", chrononaut_id="CHR-G9POS1", save=guest_living_save)
        host._cmd_table_accept(["t9pos", "p9guest1"])
        record1 = table_admission.load_record(run_dir, "t9pos")
        assert "p9guest1" in record1["roster"], record1

        # (2) reine ID-Anfrage ohne jede eigene Figur -- KEIN Sidecar, KEIN
        # eigener Current -- bleibt weiterhin zulaessig (`own is None` ist
        # KEIN pauschaler Personen-/Hostrollen-Hold).
        table_admission.request_join(run_dir, table_key="t9pos", guest_id="p9guest2")
        host._cmd_table_accept(["t9pos", "p9guest2"])
        record2 = table_admission.load_record(run_dir, "t9pos")
        assert "p9guest2" in record2["roster"], record2

        # (3) bewusst ANDERE lebende Figur derselben Person, waehrend eine
        # FRUEHERE eigene Figur bereits final/archiviert ist -- der Hold
        # ist char-gebunden, keine Pauschalsperre der Person.
        old_final_save = full_v7_save("CHR-G9POS3-OLD", name="p9guest3", status="deceased")
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id="p9guest3", chrononaut_id="CHR-G9POS3-OLD", persona_key="p9guest3",
        ))
        catalog.store_figure_save(catalog_dir, "p9guest3", "CHR-G9POS3-OLD", old_final_save)
        new_living_save = _register_own_figure(
            onboarding_dir, catalog_dir, "p9guest3", "CHR-G9POS3-NEW",
            run_dir=run_dir, states_dir=states_dir,
        )
        table_admission.request_join(run_dir, table_key="t9pos", guest_id="p9guest3")
        _write_table_guest_offer(run_dir, "t9pos", "p9guest3", chrononaut_id="CHR-G9POS3-NEW", save=new_living_save)
        host._cmd_table_accept(["t9pos", "p9guest3"])
        record3 = table_admission.load_record(run_dir, "t9pos")
        assert "p9guest3" in record3["roster"], record3
        # Die aeltere, archivierte finale Figur bleibt unberuehrt (kein
        # Fallback, keine automatische Wiederbelebung).
        archived_old = catalog.load_figure_save(catalog_dir, "p9guest3", "CHR-G9POS3-OLD")
        assert archived_old == old_final_save


def test_table_accept_holds_sidecarless_when_own_current_unreadable_no_roster_write():
    """T3 (ZR-KERN-FEINSCHLIFF-K3-N2 02 §N2-C/03_NACHWEISE T3): eine reine
    ID-Anfrage OHNE Gastangebot-Sidecar haelt kontrolliert, wenn die
    BEKANNTE eigene Current-Referenz des Gasts GERADE nicht lesbar ist --
    die tatsaechlich referenzierte Current-Versionsdatei wird im
    isolierten Temp-Testverzeichnis real ungueltig gemacht (KEINE
    Leser-/Guard-Attrappe), sodass `load_current_save_or_raise` ein
    echtes `CurrentSaveUnavailableError` liefert. Der echte
    `_cmd_table_accept`-Aufruf haelt VOR jeder Schreibwirkung: Anfrage/
    Roster, Current-Referenz, Versions- und Archivbestand bleiben
    byteidentisch unveraendert. Daneben bleibt eine positive reine
    ID-Anfrage OHNE jede eigene Fassung weiterhin zulaessig (kein
    pauschaler Personen-/Betreiber-Hold)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            onboarding_dir, catalog_dir, "p_t3host", "CHR-T3H",
            run_dir=run_dir, states_dir=states_dir,
        )
        _register_own_figure(
            onboarding_dir, catalog_dir, "p_t3guest", "CHR-T3G",
            run_dir=run_dir, states_dir=states_dir,
        )
        host = _session(onboarding_dir, catalog_dir, "p_t3host", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))
        host._cmd_table_offer(["t3"])
        table_admission.request_join(run_dir, table_key="t3", guest_id="p_t3guest")
        from mmo_sim.ui.tui import _read_table_guest_offer
        assert _read_table_guest_offer(run_dir, "t3", "p_t3guest") is None, (
            "Testvoraussetzung: reine ID-Anfrage OHNE Sidecar."
        )

        # Fehlzustand VOR dem Vorher-Snapshot herstellen: die TATSAECHLICH
        # referenzierte Current-Versionsdatei des Gasts wird real
        # unlesbar/ungueltig gemacht (reale Datei im isolierten
        # Temp-Testverzeichnis, kein Leser-/Guard-Attrappe).
        versions_dir = run_dir / "current_saves" / "p_t3guest__versions"
        version_files = sorted(versions_dir.glob("*.json"))
        assert len(version_files) == 1, version_files
        version_path = version_files[0]
        version_path.write_text("{dies ist kein gueltiges JSON", encoding="utf-8")

        record_path = run_dir / "table_admission" / "t3.json"
        catalog_path = catalog_dir / "catalog__p_t3guest.json"
        before = (
            record_path.read_bytes(),
            sorted((p.name, p.read_bytes()) for p in versions_dir.glob("*.json")),
            catalog_path.read_bytes() if catalog_path.exists() else None,
        )

        printed: list[str] = []
        host._print = printed.append
        host._cmd_table_accept(["t3", "p_t3guest"])
        joined = "\n".join(printed)
        assert "nicht lesbar" in joined, joined
        assert "Legendenabschied" not in joined, (
            f"CurrentSaveUnavailableError darf NICHT als Finalhold ausgegeben/umgedeutet werden: {joined}"
        )

        after = (
            record_path.read_bytes(),
            sorted((p.name, p.read_bytes()) for p in versions_dir.glob("*.json")),
            catalog_path.read_bytes() if catalog_path.exists() else None,
        )
        assert before == after, "Ein bekannter, gerade unlesbarer Current darf 0 Writes verursachen."

        record = table_admission.load_record(run_dir, "t3")
        assert "p_t3guest" not in record["roster"], record
        assert "p_t3guest" in record["requests"], "Die offene Anfrage bleibt bestehen -- kein stiller Abbruch."

        # Daneben bleibt eine positive reine ID-Anfrage OHNE jede eigene
        # Fassung weiterhin zulaessig (kein pauschaler Personen-/
        # Betreiber-Hold).
        table_admission.request_join(run_dir, table_key="t3", guest_id="p_t3guest2")
        host._cmd_table_accept(["t3", "p_t3guest2"])
        record2 = table_admission.load_record(run_dir, "t3")
        assert "p_t3guest2" in record2["roster"], record2


def test_shared_terminal_completion_card_export_selects_own_bytes_not_session_owner():
    """C-Gast-Export (02 §C-Gast-Export) + ZR-KERN-FEINSCHLIFF-K3-N2 (02
    §N2-A/T1): am geteilten Terminal durchlaeuft die ECHTE
    `_print_section_completion_card` + ihr echter Auswahl-Dispatcher
    (`_dispatch_completion_card_choice`) -- NICHT ein direkter
    `_cmd_export`-Aufruf. Nur die AEUSSERE IO-Grenze
    (`_readline_with_controls`) liefert die Auswahl-Eingabe; Kartenbauer,
    Dispatcher, Resolver und `_cmd_export` selbst bleiben ungemockt.

    Belege: eine FINALE Hostfigur UND eine FINALE Gastfigur am geteilten
    Terminal bekommen KEINE als zulaessig angebotene neue Solo-/
    Beitrittsaufnahme (Aktionsliste bleibt bei Export+Rueckkehr, keine
    dritte Nummer); die reale Auswahl exportiert tatsaechlich die EIGENEN
    Bytes der jeweiligen Kartenperson (Gast != Host, fremder Export wird
    nicht ueberschrieben); eine LEBENDE Figur behaelt ihren bestehenden
    zulaessigen Folgeweg (Solo-Fortsetzen bleibt angeboten)."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        host_save = _register_own_figure(
            onboarding_dir, catalog_dir, "p_shared_host", "CHR-SHOST",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        guest_save = _register_own_figure(
            onboarding_dir, catalog_dir, "p_shared_guest", "CHR-SGUEST",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        assert host_save != guest_save

        # EINE Sitzung (geteiltes Terminal, `io is self`) mit
        # `self.participant_id` == Host -- die Karte wird aber EXPLIZIT
        # fuer die tatsaechliche Kartenperson gelesen (`pid`), exakt wie
        # am geteilten Terminal ("andere aeussere Sitzungsperson" = andere
        # Kartenperson an derselben physischen Session, s. bestehender
        # Docstring von `_print_section_completion_card`).
        session = _session(
            onboarding_dir, catalog_dir, "p_shared_host", run_dir, states_dir,
            gm_transport_factory=_SpyFactory("gm"),
        )
        import json as _json

        # (1) Finale HOSTFIGUR: `pid == io.participant_id and io._host_capable`
        # -- ohne den Fix wuerde dies "Solo-Fortsetzen" anbieten. Auswahl
        # "1" (Export ist Aktion 1, da `has_character` True) ueber die
        # aeussere IO-Grenze.
        printed_host: list[str] = []
        session._print = printed_host.append
        session._readline_with_controls = lambda *a, **kw: ("1", None)
        session._print_section_completion_card(session, "p_shared_host", False)
        joined_host = "\n".join(printed_host)
        assert "Solo-Fortsetzen" not in joined_host, joined_host
        assert "Tisch suchen/beitreten" not in joined_host, joined_host
        assert "  3)" not in joined_host, (
            f"Eine finale Kartenfigur darf keine dritte (Folgeaktions-)Nummer bekommen: {joined_host}"
        )
        assert "Legendenabschied abgeschlossen" in joined_host, joined_host
        host_export_path = session.exports_dir / "p_shared_host.json"
        assert host_export_path.exists(), "Die reale Auswahl '1' haette den echten Export ausloesen muessen."
        host_export_bytes_after_host = host_export_path.read_bytes()
        assert _json.loads(host_export_bytes_after_host) == host_save

        # (2) Finale GASTFIGUR an derselben physischen Session (`io is
        # self`), aber ANDERE Kartenperson (`pid="p_shared_guest"` !=
        # `io.participant_id`) -- `is_guest_follow_up` waere ohne Fix
        # "Tisch suchen/beitreten". Auswahl "1" exportiert wieder die
        # Kartenperson, NICHT die aeussere Session (R5 FIX2-Bindung).
        printed_guest: list[str] = []
        session._print = printed_guest.append
        session._readline_with_controls = lambda *a, **kw: ("1", None)
        session._print_section_completion_card(session, "p_shared_guest", False)
        joined_guest = "\n".join(printed_guest)
        assert "Tisch suchen/beitreten" not in joined_guest, joined_guest
        assert "Solo-Fortsetzen" not in joined_guest, joined_guest
        assert "  3)" not in joined_guest, joined_guest
        assert "Legendenabschied abgeschlossen" in joined_guest, joined_guest
        guest_export_path = session.exports_dir / "p_shared_guest.json"
        assert guest_export_path.exists()
        assert _json.loads(guest_export_path.read_text(encoding="utf-8")) == guest_save
        assert _json.loads(guest_export_path.read_text(encoding="utf-8")) != host_save
        # Fremder Export wird nicht ueberschrieben: der Hostexport bleibt
        # byteidentisch zu VOR dem Gastexport.
        assert host_export_path.read_bytes() == host_export_bytes_after_host, (
            "Der Gastexport darf die bereits geschriebene Hostexportdatei nicht ueberschreiben."
        )

        # (3) Gegenprobe: eine LEBENDE Figur behaelt ihren bestehenden
        # zulaessigen Folgeweg (Solo-Fortsetzen bleibt als Aktion 3
        # angeboten) -- leere Eingabe ('/zurueck'-Aequivalent) loest hier
        # bewusst KEINE Aktion aus, nur die gedruckte Aktionsliste wird
        # geprueft.
        _register_own_figure(
            onboarding_dir, catalog_dir, "p_shared_host", "CHR-SHOST",
            run_dir=run_dir, states_dir=states_dir,
        )
        printed_living: list[str] = []
        session._print = printed_living.append
        session._readline_with_controls = lambda *a, **kw: ("", None)
        session._print_section_completion_card(session, "p_shared_host", False)
        joined_living = "\n".join(printed_living)
        assert "Solo-Fortsetzen" in joined_living, (
            f"Eine lebende Kartenfigur muss ihren bestehenden Folgeweg behalten: {joined_living}"
        )


def test_table_start_pre_check_holds_fresh_start_before_admission_effect_with_final_roster_member():
    """Fall 10 (K3, 02 §C `_cmd_table_start`): ein frischer Start haelt VOR
    `start_table` (roster/requests-Einfrieren ist bereits eine echte
    Wirkung), wenn ein bereits angenommenes Rostermitglied inzwischen eine
    endgueltig abgeschlossene Figur hat -- die bestehende Wiederoeffnung
    nach gescheitertem Start ist dafuer KEIN Ersatz: der Zustand bleibt
    schon VORHER unveraendert 'offen', kein GM-Turn."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        _register_own_figure(
            onboarding_dir, catalog_dir, "p10host", "CHR-H10",
            run_dir=run_dir, states_dir=states_dir,
        )
        guest_save = _register_own_figure(
            onboarding_dir, catalog_dir, "p10guest", "CHR-G10",
            run_dir=run_dir, states_dir=states_dir,
        )

        host = _session(onboarding_dir, catalog_dir, "p10host", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm-host"))
        host._cmd_table_offer(["t10"])
        guest = _session(
            onboarding_dir, catalog_dir, "p10guest", run_dir, states_dir,
            gm_transport_factory=_SpyFactory("gm-guest"), host_capable=False,
        )
        guest._cmd_table_request_join(["t10"])
        host._cmd_table_accept(["t10", "p10guest"])
        record_before = table_admission.load_record(run_dir, "t10")
        assert "p10guest" in record_before["roster"], record_before

        # Die Figur stirbt (Legendenabschied) NACH der Annahme, VOR dem
        # Tischstart -- derselbe Current wird erneut mit status=deceased
        # veroeffentlicht (dieselbe Produktfunktion wie jeder echte
        # Legendenabschied-Final-Save).
        guest_save["characters"][0]["status"] = "deceased"
        ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
        core_store.publish_current_save(run_dir, "p10guest", guest_save, ps_store, states_dir)

        gm_host = _ExplodingGmTransport()
        host2 = _session(onboarding_dir, catalog_dir, "p10host", run_dir, states_dir, gm_transport_factory=lambda: gm_host)
        printed: list[str] = []
        host2._print = printed.append
        host2._cmd_table_start(["t10"])
        joined = "\n".join(printed)
        assert "Legendenabschied" in joined, joined
        assert gm_host.calls == 0, "Ein gehaltener Tischstart darf KEINEN GM-Turn ausloesen."

        record_after = table_admission.load_record(run_dir, "t10")
        assert record_after["state"] == table_admission.STATE_OPEN, (
            f"Ein gehaltener Tischstart darf 'start_table' NICHT erreichen: {record_after}"
        )


def _make_ready_with_status(onboarding_dir, states_dir, run_dir, persona_key: str, *, status: str | None = None) -> dict:
    """K3-Variante von `test_l01_l10_lobby_initiative.py:_make_ready` --
    identische Produktschritte, zusaetzlich mit optionalem `status`-
    Override auf der EINEN Figur (z.B. `"deceased"`), damit eine
    Community-Persona ueber den echten `b`-Lobby-Weg mit einem bereits
    abgeschlossenen Legendenabschied antritt."""
    save = l01._load_fixture_save(persona_key)
    if status is not None:
        save["characters"][0]["status"] = status
    chrono_id = save["characters"][0]["id"]
    ps_store = PersonaStateStore(schema_path=_SCHEMA_PATH)
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    return save


class _MiniFlexDriver:
    """Lokale, minimale Variante von `test_r4_open_plan_resume_priority_
    2026_10_23.py:_FlexDriver` (reiner Testcode, nur das hier Benoetigte:
    EIN optionaler Tischvorschlag, Konsens-Zusage, Pflicht-Reflexion mit
    optionalem Seiteneffekt, sonst normaler Spielzug)."""

    def __init__(self, pk: str, propose: dict | None = None, on_reflection=None):
        self.pk = pk
        self._propose = propose
        self._proposed = False
        self._on_reflection = on_reflection
        self.calls: list[dict] = []

    def decide(self, ctx: dict) -> ParticipantDecision:
        import json as _json
        self.calls.append(ctx)
        if ctx.get("system") == "PRIVATE_REFLECTION_SENTINEL":
            if self._on_reflection is not None:
                self._on_reflection()
            return ParticipantDecision(text=f"Reflexion von {self.pk}.", origin_source=f"fake:{self.pk}")
        if "decision_contract" in ctx:
            c = ctx["decision_contract"]
            return ParticipantDecision(
                text=f"ENTSCHEIDUNG offer_id={c['offer_id']} participant_id={self.pk} decision=accept",
                origin_source=f"fake:{self.pk}",
            )
        if "begrenztes eigenes Lobby-Initiativfenster" in ctx.get("user", ""):
            if self._propose is not None and not self._proposed:
                self._proposed = True
                return ParticipantDecision(
                    text=_json.dumps({"action": "propose", **self._propose}), origin_source=f"fake:{self.pk}",
                )
            return ParticipantDecision(text='{"action": "pause"}', origin_source=f"fake:{self.pk}")
        return ParticipantDecision(text=f"'{self.pk}' spielt weiter.", origin_source=f"fake:{self.pk}")


def test_lobby_b_entry_roster_resolution_excludes_lone_deceased_member_no_persona_call():
    """Fall 11 (K3, 02 §C Rosterauflösung): eine Spielgemeinschaft aus
    GENAU einer bereits final abgeschlossenen Figur (ohne eigenen offenen
    Abschlussauftrag) wird am echten `b`-Weg (`core.lobby_flow.
    run_lobby_window`, ECHTE Resolver/Guards) schon an der
    Rosterauflösung gehalten -- `persona_driver_factory` wird dafuer KEIN
    einziges Mal aufgerufen (keine neue Persona-Anbahnung), die
    Sichtbarkeit bleibt dabei ehrlich (die Figur erscheint weiterhin in
    der Statuszeile -- jetzt in der eigenen `legendenabschied`-Kategorie,
    NICHT mehr als "frei/spielbereit", 02 §B1)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, "community-op", ["sniper"],
        )
        write_test_profile(run_dir)
        _make_ready_with_status(onboarding_dir, states_dir, run_dir, "sniper", status="deceased")

        printed: list[str] = []
        session = l01._session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=_SpyFactory("gm"),
            persona_driver_factory=_SpyFactory("persona_driver"),
            printed=printed,
        )
        out = lobby_flow.run_lobby_window(session, ai_personas=None)
        joined = "\n".join(printed)
        assert "frei/spielbereit=[]" in joined, joined
        assert "legendenabschied=['sniper']" in joined, (
            "Die gehaltene Finalfigur muss in der eigenen legendenabschied-Kategorie sichtbar "
            f"bleiben, NICHT als frei/spielbereit: {joined}"
        )
        assert out.kind == lobby_flow.LobbyOutcomeKind.NO_CONSENSUS, out


def test_lobby_b_entry_real_resume_completes_open_plan_to_closed_idempotent_second_pass():
    """Fall 12 (K3, 02 §C play_bound_table/Resumeauflösung; 04 §2 'Echte
    Restfertigstellung' + 'Ausnahme ist eng'): die Figur lebt beim
    Tischstart noch (realer Flow: der Legendenabschied entsteht erst als
    ERGEBNIS dieser Sitzung, nicht vorher) und wird erst durch den
    echten Harvest (`core_store.complete_section` -> `_write_current_
    save_version`, ausgeloest ueber den normalen GM-Marker-Turn) zu ihrem
    eigenen Final-Current. Ein real gepinnter, noch unfinalisierter
    Abschlussauftrag GENAU dieser jetzt verstorbenen Figur wird ueber den
    echten `b`-Lobby-Weg (R4-Muster: `write_lab_stop` NACH der letzten
    Reflexion reproduziert 'Wall-Clock-Fenster endet') bis `__final.json`/
    `status=='closed'`/Lockfreigabe zu Ende gefuehrt -- KEIN neuer
    GM-Turn, KEINE doppelte Reflexionsabfrage; ein dritter Lobbydurchlauf
    danach bleibt idempotent (kein Crash, kein neuer Call)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        keys = ["sniper", "tech"]
        schema_path, states_dir, run_dir, onboarding_dir, catalog_dir = l01._bootstrap_community(
            root, "community-op", keys,
        )
        write_test_profile(run_dir)

        # Beide Figuren starten LEBEND (Produkt-Normalfall) -- `_make_ready`
        # ohne Status-Override, identisch zu `test_l01_l10_lobby_initiative`.
        l01._make_ready(onboarding_dir, states_dir, run_dir, "sniper")
        l01._make_ready(onboarding_dir, states_dir, run_dir, "tech")
        sniper_chrono_id = l01._load_fixture_save("sniper")["characters"][0]["id"]
        tech_chrono_id = l01._load_fixture_save("tech")["characters"][0]["id"]

        # Der GM liefert am Markerturn den geernteten Final-Current --
        # NUR sniper's Block traegt den Legendenabschied-Marker (das
        # Ergebnis DIESER Sitzung, nicht ein vorbestehender Zustand).
        deceased_harvest_save = l01._load_fixture_save("sniper")
        deceased_harvest_save["characters"][0]["status"] = "deceased"
        tech_harvest_save = l01._load_fixture_save("tech")

        table_id = "lobby-sniper-tech"
        gm = l01._TableGM(
            table_id, f"{table_id}-section",
            {"sniper": deceased_harvest_save, "tech": tech_harvest_save}, turns_before_marker=1,
        )
        stop_state = {"armed": False}

        def _arm_stop():
            # "sniper" < "tech" alphabetisch -- table.members ist sortiert
            # ["sniper", "tech"], "tech" ist damit die LETZTE Reflexion in
            # der Schleife (dasselbe R4-Muster: der Stop wirkt erst auf den
            # naechsten Gate-Check NACH allen drei -- hier beiden --
            # bereits vollstaendig committeten Reflexionen).
            stop_state["armed"] = True
            write_lab_stop(run_dir, "K3-Test: Wall-Clock-Fenster endet nach letzter Reflexion.")

        drivers = {
            "sniper": _MiniFlexDriver("sniper", propose={"wants": ["tech"]}),
            "tech": _MiniFlexDriver("tech", on_reflection=_arm_stop),
        }
        printed: list[str] = []
        session = l01._session(
            "op", onboarding_dir, catalog_dir, run_dir, states_dir, schema_path,
            gm_transport_factory=lambda *_a, **_kw: gm,
            persona_driver_factory=lambda pk: drivers[pk],
            printed=printed,
        )

        # Fenster 1: Tisch bildet sich, spielt bis zur Ernte+Reflexion --
        # die dritte Gate-Pruefung NACH der letzten Reflexion wird durch
        # den Wall-Clock-Stop blockiert, BEVOR sie finalisiert.
        out1 = lobby_flow.run_lobby_window(session, ai_personas=None)
        assert out1.table_id == table_id, out1
        assert stop_state["armed"], "tech's Reflexion haette den Stop-Seiteneffekt ausloesen muessen"
        table_after_w1 = core_store.Table.load(run_dir, table_id)
        assert table_after_w1.status == "active", table_after_w1
        completion_dir = run_dir / "completion"
        assert list(completion_dir.glob(f"{table_id}-section__plan.json")), (
            "Ein gepinnter, unfertiger Abschlussauftrag wird erwartet."
        )
        assert not list(completion_dir.glob(f"{table_id}-section__final.json")), "Noch kein __final.json erwartet."
        gm_calls_after_w1 = len(gm.calls)
        assert gm_calls_after_w1 == 1, gm.calls
        reflection_calls_before = {pk: len(drivers[pk].calls) for pk in keys}

        # ZR-KERN-FEINSCHLIFF-K3-N1 (02 §C-Resume): der tatsaechlich
        # geerntete Final-Current wird VOR dem Resume DIREKT gelesen --
        # beweist, dass der Harvest in Fenster 1 bereits real (ueber den
        # normalen GM-Marker-Turn -> `complete_section`) vorliegt, NICHT
        # erst eine Testannahme ist. Dieser Lesebeleg ersetzt gleichzeitig
        # die vorher in Test 3 selbst erzeugte, redundante Publikation
        # (02 §C-Publikation).
        resume_ps_store = PersonaStateStore(schema_path=schema_path)
        pre_resume_sniper_current = core_store.load_current_save_or_raise(
            run_dir, "sniper", resume_ps_store, states_dir=states_dir,
        )
        assert pre_resume_sniper_current == deceased_harvest_save, (
            "Der real geerntete Final-Current muss VOR dem Resume bereits identisch vorliegen."
        )
        assert zeitriss_saves.is_final_deceased(pre_resume_sniper_current) is True
        # T4 (03_NACHWEISE, Test 12): AUCH das zweite Gruppenmitglied
        # ("tech", lebend) vor der Restfinalisierung real lesen --
        # Figurenidentitaet + (Nicht-)Finalmarker fuer BEIDE Mitglieder
        # binden, nicht nur fuer die finale Figur.
        pre_resume_tech_current = core_store.load_current_save_or_raise(
            run_dir, "tech", resume_ps_store, states_dir=states_dir,
        )
        assert pre_resume_tech_current == tech_harvest_save, (
            "Der real geerntete lebende Current fuer 'tech' muss VOR dem Resume bereits identisch vorliegen."
        )
        assert zeitriss_saves.block_char_id(pre_resume_tech_current) == tech_chrono_id
        assert zeitriss_saves.is_final_deceased(pre_resume_tech_current) is False
        sniper_versions_dir = run_dir / "current_saves" / "sniper__versions"
        tech_versions_dir = run_dir / "current_saves" / "tech__versions"
        # Tatsaechlichen VersionsBESTAND (Dateinamen UND Bytes, nicht nur
        # die Anzahl) vor der Restfinalisierung binden -- eine gleiche
        # Dateianzahl allein beweist keine gleichen Bytes.
        sniper_versions_before_resume = sorted((p.name, p.read_bytes()) for p in sniper_versions_dir.glob("*.json"))
        tech_versions_before_resume = sorted((p.name, p.read_bytes()) for p in tech_versions_dir.glob("*.json"))
        sniper_version_count_before_resume = len(sniper_versions_before_resume)

        clear_lab_stop(run_dir)

        # Fenster 2 (DER PRUEFGEGENSTAND): derselbe real gepinnte
        # Abschlussauftrag wird ueber `find_bound_active_open_plan_table`
        # -> `_resume_bound_table` vorrangig zu Ende gefuehrt --
        # `_final_deceased_hold` laesst 'sniper' NUR deshalb durch, weil
        # fuer GENAU diesen Tisch ein echter offener Abschlussauftrag
        # vorliegt (dieselbe Store-Leser-Autoritaet wie Fall 6 oben).
        out2 = lobby_flow.run_lobby_window(session, ai_personas=None)
        assert out2.table_id == table_id, out2
        assert out2.kind == lobby_flow.LobbyOutcomeKind.SECTION_COMPLETED, out2
        table_after_w2 = core_store.Table.load(run_dir, table_id)
        assert table_after_w2.status == "closed", f"Echte Restfertigstellung muss bis 'closed' fuehren: {table_after_w2}"
        assert list(completion_dir.glob(f"{table_id}-section__final.json")), (
            "Nach Restfertigstellung wird __final.json erwartet."
        )
        assert len(gm.calls) == gm_calls_after_w1, "Fenster 2 darf KEINEN neuen GM-Turn ausloesen."
        for pk in keys:
            assert len(drivers[pk].calls) == reflection_calls_before[pk], (
                f"'{pk}' durfte in Fenster 2 NICHT erneut befragt werden: {drivers[pk].calls}"
            )

        # 02 §C-Resume: die Restfertigstellung (Fenster 2, nur Reflexion +
        # Finalisierung) darf KEINE zweite Version/keinen zweiten
        # Fortschritt fuer die bereits in Fenster 1 geernteten Bytes
        # erzeugen -- der TATSAECHLICHE Versionsbestand (Namen+Bytes, nicht
        # nur die Anzahl) bleibt fuer BEIDE Mitglieder unveraendert.
        sniper_versions_after_resume = sorted((p.name, p.read_bytes()) for p in sniper_versions_dir.glob("*.json"))
        tech_versions_after_resume = sorted((p.name, p.read_bytes()) for p in tech_versions_dir.glob("*.json"))
        assert sniper_versions_after_resume == sniper_versions_before_resume, (
            "Die Restfertigstellung darf den Sniper-Versionsbestand (Bytes) nicht veraendern -- "
            "gleiche Dateianzahl beweist keine gleichen Bytes."
        )
        assert tech_versions_after_resume == tech_versions_before_resume, (
            "Die Restfertigstellung darf den Tech-Versionsbestand (Bytes) ebenfalls nicht veraendern."
        )
        sniper_version_count_after_resume = len(sniper_versions_after_resume)
        assert sniper_version_count_after_resume == sniper_version_count_before_resume, (
            f"Die Restfertigstellung darf keine zweite Current-Version erzeugen: "
            f"{sniper_version_count_before_resume} -> {sniper_version_count_after_resume}."
        )

        # Beide persoenlichen Currents NACH der Restfinalisierung erneut
        # real lesen -- Figurenidentitaet/Finalmarker bleiben fuer BEIDE
        # Mitglieder konsistent (sniper final, tech weiterhin lebend;
        # keine Vermischung/kein Ueberschreiben der falschen Person).
        post_resume_sniper_current = core_store.load_current_save_or_raise(
            run_dir, "sniper", resume_ps_store, states_dir=states_dir,
        )
        assert zeitriss_saves.block_char_id(post_resume_sniper_current) == sniper_chrono_id
        assert zeitriss_saves.is_final_deceased(post_resume_sniper_current) is True
        post_resume_tech_current = core_store.load_current_save_or_raise(
            run_dir, "tech", resume_ps_store, states_dir=states_dir,
        )
        assert zeitriss_saves.block_char_id(post_resume_tech_current) == tech_chrono_id
        assert zeitriss_saves.is_final_deceased(post_resume_tech_current) is False

        # Lockfreigabe: beide Chrononauten sind nach dem echten Abschluss
        # NICHT mehr an diesen (jetzt geschlossenen) Tisch gebunden.
        from mmo_sim.domain.zeitriss.policy import ZeitrissTableSizePolicy
        lock_lobby = core_store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        assert not lock_lobby.is_locked(sniper_chrono_id), "sniper's Figur muss nach Abschluss entsperrt sein."
        assert not lock_lobby.is_locked(tech_chrono_id), "tech's Figur muss nach Abschluss entsperrt sein."

        # Idempotenter zweiter Resume: ein dritter Lobbydurchlauf (ohne
        # jede Personabefragung, `ai_personas=frozenset()`) darf weder
        # abstuerzen noch einen neuen GM-/Persona-Call ausloesen -- der
        # Abschlussauftrag ist bereits real finalisiert.
        out3 = lobby_flow.run_lobby_window(session, ai_personas=frozenset())
        assert out3 is not None
        assert len(gm.calls) == gm_calls_after_w1, "Ein dritter Lobbydurchlauf darf keinen neuen GM-Turn ausloesen."
        for pk in keys:
            assert len(drivers[pk].calls) == reflection_calls_before[pk], (
                f"Ein dritter Lobbydurchlauf darf '{pk}' nicht erneut befragen: {drivers[pk].calls}"
            )
        # Ein zweiter Durchlauf DESSELBEN bereits abgeschlossenen Vorgangs
        # darf KEINEN zweiten Fortschritt erzeugen -- der TATSAECHLICHE
        # Versionsbestand (Namen+Bytes) bleibt fuer BEIDE Mitglieder
        # unveraendert, nicht nur die Dateianzahl (02 §C-Resume).
        sniper_versions_after_idempotent_pass = sorted(
            (p.name, p.read_bytes()) for p in sniper_versions_dir.glob("*.json")
        )
        tech_versions_after_idempotent_pass = sorted(
            (p.name, p.read_bytes()) for p in tech_versions_dir.glob("*.json")
        )
        assert sniper_versions_after_idempotent_pass == sniper_versions_before_resume, (
            "Ein zweiter Durchlauf desselben abgeschlossenen Vorgangs darf den Sniper-"
            "Versionsbestand (Bytes) NICHT veraendern."
        )
        assert tech_versions_after_idempotent_pass == tech_versions_before_resume, (
            "Ein zweiter Durchlauf desselben abgeschlossenen Vorgangs darf den Tech-"
            "Versionsbestand (Bytes) ebenfalls NICHT veraendern."
        )
        sniper_version_count_after_idempotent_pass = len(sniper_versions_after_idempotent_pass)
        assert sniper_version_count_after_idempotent_pass == sniper_version_count_before_resume, (
            "Ein zweiter Durchlauf desselben abgeschlossenen Vorgangs darf KEINEN zweiten "
            "Fortschritt erzeugen (Versionszahl unveraendert)."
        )


def test_resume_card_shows_abschluss_ausstehend_for_real_open_completion_order_then_abgeschlossen():
    """C-Pending/Completed (02 §B2): ein tatsaechlich noch offener
    Abschlussauftrag (gepinnt, ohne `__final.json`) fuer den GEBUNDENEN
    Tisch der finalen Figur darf NICHT 'Legendenabschied abgeschlossen'
    heissen -- 'Abschluss ausstehend' ist Pflicht, solange der Abschluss
    real offen ist; NACH echter Finalisierung zeigt dieselbe Karte wieder
    den bisherigen Wortlaut."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        write_test_profile(env.run_dir, max_turns=200)
        lobby, table, ps_store = build_two_member_table(env, table_id="t-resume-card-pending")

        leader_final = full_v7_save("chrono-leader", name="Leader", status="deceased")
        guest_alive = full_v7_save("chrono-guest", name="Guest", lp=5)
        result = core_store.complete_section(
            lobby, table, "sec-resume-card-pending",
            harvested_saves={"leader_pk": leader_final, "guest_pk": guest_alive},
            states_dir=env.states_dir, today="2026-11-13",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        )
        assert result.success, result.reason
        # KEIN finalize_section_after_reflection hier -- der Abschluss
        # bleibt real offen (gepinnt, ohne __final.json).

        onboarding_dir, catalog_dir = env.run_dir.parent / "onboarding", env.run_dir.parent / "catalog"
        onboarding.start_or_resume(onboarding_dir, "leader_pk")
        onboarding.complete_with_save(onboarding_dir, "leader_pk", leader_final, ZeitrissHarvestValidator(), "chrono-leader")
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id="leader_pk", chrononaut_id="chrono-leader", persona_key="leader_pk",
        ))
        catalog.bind_for_section(catalog_dir, "leader_pk", "chrono-leader", has_open_section=False)

        session = _session(onboarding_dir, catalog_dir, "leader_pk", env.run_dir, env.states_dir, gm_transport_factory=_SpyFactory("gm"))
        card = session._build_resume_card(participant_id="leader_pk")
        assert card is not None and card.last_valid_save_summary is not None
        assert "Abschluss ausstehend" in card.last_valid_save_summary, card.last_valid_save_summary
        assert "Legendenabschied abgeschlossen" not in card.last_valid_save_summary, card.last_valid_save_summary
        assert "Solo-/Beitrittsaufnahme" in card.last_valid_save_summary, (
            "Die Karte darf auch im 'ausstehend'-Zustand keine sofort zulaessige neue "
            f"Aufnahme behaupten: {card.last_valid_save_summary}"
        )

        final_result = core_store.finalize_section_after_reflection(lobby, table, "sec-resume-card-pending")
        assert final_result.success, final_result.reason
        card_after = session._build_resume_card(participant_id="leader_pk")
        assert card_after is not None and card_after.last_valid_save_summary is not None
        assert "Legendenabschied abgeschlossen" in card_after.last_valid_save_summary, card_after.last_valid_save_summary
        assert "Abschluss ausstehend" not in card_after.last_valid_save_summary, card_after.last_valid_save_summary


def test_character_listing_marks_active_from_current_others_from_archive():
    """C-Pending/Completed + Figurenquelle (02 §B4) + ZR-KERN-FEINSCHLIFF-
    K3-N2 (02 §N2-B/T2): im vorhandenen Figurenwahl-Listing
    (`_cmd_new_or_switch_character`) wird die AKTIVE Figur aus dem
    TATSAECHLICHEN Current, jede andere aus ihren getrennten, tatsaechlich
    vorhandenen Archivbytes gekennzeichnet -- reine Anzeige, keine
    erfundenen Statusmetadaten im Katalog, kein Figurenwechsel/neuer
    Erschaffungszug allein durch Anzeige.

    Belege: eine AKTIVE finale Figur (echter Current, status=deceased)
    bekommt ein eigenes Finallabel; eine ANDERE finale Archivfigur
    (echte Figurenbytes, status=deceased) ebenso -- eine normale
    lebende Archivfigur bleibt unterscheidbar von beiden; ein bewusst
    abweichender ALTER Onboardingstand (ohne eigenen Katalogeintrag)
    wird NICHT statt des Current massgeblich. Katalog-ID/blosses
    "Archiv" allein ist KEIN Finalnachweis -- Labels werden hier an den
    tatsaechlich gelesenen Status gebunden."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        run_dir, states_dir = d / "run", d / "states"
        onboarding_dir, catalog_dir = d / "onboarding", d / "catalog"
        write_test_profile(run_dir, max_turns=200)

        # AKTIVE Figur: TATSAECHLICHER Current, final (status=deceased).
        active_final_save = _register_own_figure(
            onboarding_dir, catalog_dir, "p_b4", "CHR-B4-ACTIVE",
            run_dir=run_dir, states_dir=states_dir, status="deceased",
        )
        assert zeitriss_saves.is_final_deceased(active_final_save) is True

        # Andere Figur #1: getrennte Archivbytes, final (status=deceased),
        # OHNE eigenen Current/Onboarding-Slot fuer DIESE char_id.
        other_final_save = full_v7_save("CHR-B4-OTHERFINAL", name="p_b4", status="deceased")
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id="p_b4", chrononaut_id="CHR-B4-OTHERFINAL", persona_key="p_b4",
        ))
        catalog.store_figure_save(catalog_dir, "p_b4", "CHR-B4-OTHERFINAL", other_final_save)

        # Andere Figur #2: getrennte Archivbytes, LEBEND -- muss von
        # beiden finalen Figuren unterscheidbar bleiben.
        other_living_save = full_v7_save("CHR-B4-OTHERLIVE", name="p_b4", lp=7)
        assert zeitriss_saves.is_final_deceased(other_living_save) is False
        catalog.register(catalog_dir, catalog.CatalogEntry(
            participant_id="p_b4", chrononaut_id="CHR-B4-OTHERLIVE", persona_key="p_b4",
        ))
        catalog.store_figure_save(catalog_dir, "p_b4", "CHR-B4-OTHERLIVE", other_living_save)

        # Bewusst abweichender ALTER Onboardingstand derselben Person --
        # traegt KEINEN deceased-Marker und ist strukturell NICHT die
        # aktive char_id; darf den tatsaechlichen (finalen) Current NICHT
        # ersetzen. `onboarding.peek` liest den zuletzt geschriebenen
        # `final_save`-Slot -- `_register_own_figure` (aktive Figur oben)
        # hat diesen Slot bereits mit `active_final_save` belegt; wir
        # ueberschreiben ihn hier bewusst NUR mit einem abweichenden,
        # NICHT-finalen Stand, um zu beweisen, dass das Listing dennoch
        # den echten (finalen) Current bindet, nicht diesen Onboarding-Slot.
        stale_onboarding_save = full_v7_save("CHR-B4-ACTIVE", name="p_b4", lp=3)
        onboarding.complete_with_save(
            onboarding_dir, "p_b4", stale_onboarding_save, ZeitrissHarvestValidator(), "CHR-B4-ACTIVE",
        )
        stale_peek = onboarding.peek(onboarding_dir, "p_b4")
        assert stale_peek is not None and stale_peek.final_save == stale_onboarding_save, (
            "Testvoraussetzung: der Onboarding-Slot weicht jetzt bewusst vom echten Current ab."
        )

        session = _session(onboarding_dir, catalog_dir, "p_b4", run_dir, states_dir, gm_transport_factory=_SpyFactory("gm"))
        printed: list[str] = []
        session._print = printed.append
        # Die Figurenliste wird VOR dem Auswahl-Prompt gedruckt -- ein
        # simuliertes '/zurueck' an GENAU diesem Prompt beendet die
        # Methode sofort danach, OHNE einen neuen Erschaffungsdialog
        # (GM-Call) auszuloesen (reiner Anzeigetest, 02 §B4).
        session._readline_with_controls = lambda *a, **kw: ("", "zurueck")
        session._cmd_new_or_switch_character()
        joined = "\n".join(printed)
        assert "CHR-B4-ACTIVE" in joined, joined

        active_line = next(line for line in printed if "CHR-B4-ACTIVE" in line)
        other_final_line = next(line for line in printed if "CHR-B4-OTHERFINAL" in line)
        other_living_line = next(line for line in printed if "CHR-B4-OTHERLIVE" in line)

        assert "aktiv, Legendenabschied abgeschlossen" in active_line, active_line
        assert "aus aktuellem Spielstand" not in active_line, (
            f"Der echte finale Current darf NICHT als normal 'aus aktuellem Spielstand' erscheinen: {active_line}"
        )

        assert "Archiv, Legendenabschied abgeschlossen" in other_final_line, other_final_line

        assert "Archiv" in other_living_line and "Legendenabschied" not in other_living_line, other_living_line

        # Katalog-ID/blosses "Archiv" allein ist KEIN Finalnachweis -- die
        # beiden Archivfiguren muessen sich im Label unterscheiden, obwohl
        # beide "Archiv" tragen.
        assert other_final_line != other_living_line
        assert "Legendenabschied" in other_final_line and "Legendenabschied" not in other_living_line

        # Kein Figurenwechsel/neuer Erschaffungszug allein durch die
        # Anzeige, keine Katalog-/Archivwrites durch das Listing selbst.
        assert catalog.load_figure_save(catalog_dir, "p_b4", "CHR-B4-OTHERFINAL") == other_final_save
        assert catalog.load_figure_save(catalog_dir, "p_b4", "CHR-B4-OTHERLIVE") == other_living_save


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
