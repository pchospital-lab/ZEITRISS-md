#!/usr/bin/env python3
"""
tests/mmo_sim/test_m12_save_correction_reachability_fix_2026_11_21.py —
ZR-R8-M12 Save-Correction-Reachability-Fix (2026-11-21).

Belegter native Bug (M12, Section `local-pe14d9b7bc5c84709__15`): die SL
gibt auf eine normale freie Aktion einen bindbaren eigenen HQ-Export aus,
dessen EINZIGER Fehler ein struktureller Cap-Ueberlauf ist (`continuity.
npc_roster` 7 Eintraege > `maxItems: 6`, `characters[0].history.milestones`
21 Eintraege > `maxItems: 20` -- per statischer Analyse der nativen
`gm_sessions/local-pe14d9b7bc5c84709__15/sl_history.jsonl` UND Live-Lauf von
`mmo_sim.domain.zeitriss.save_correction.evaluate`/`mmo_sim.core.
save_correction.has_residual_structural_cap_overflow` gegen GENAU diesen
Kandidaten bestaetigt, s. Report). Der Leader tippt `!save` -> `core.
runtime.py`s PRE-SEND-Pfad (`act()` -> `finalize(..., pre_send=True)`)
uebernimmt den Kandidaten OHNE neuen GM-Call, `store.complete_section`
lehnt ihn wegen des Cap-Ueberlaufs als `missing` ab -- VOR diesem Fix hielt
`runtime.py`s `and not pre_send`-Gate (Z.935 am Ausgangsstand 2ed250f1) den
GESAMTEN Korrekturweg fuer PRE-SEND zu, OBWOHL der bereits bestehende
Best-effort-Strukturvertrag (`has_residual_structural_cap_overflow` +
`mark_adopted(best_effort=True)`, bereits produktiv fuer den
reaktiven/erschoepften-Budget-Pfad) diesen EXAKTEN Fall mit NULL
GM-/Correction-Calls haette abschliessen koennen -- dauerhafte `!save`-
Sackgasse (Boot-Hauptmenue -> Fortsetzen -> derselbe offene Abschnitt).

Testet am ECHTEN Verzweigungsort (`TuiSession._cmd_local_round` ->
`core.app_service` -> `core.runtime.SectionRuntime.run_full_section`,
derselbe Call-Pfad wie `test_zr_r8_pending_save_commitfix_2026_11_20.py`),
KEIN isolierter Nachbau der Gate-/Korrektur-Logik. Das gescriptete GM-Fake
wirft bei jedem UEBERZAEHLIGEN Aufruf -- der direkte Beleg fuer "0
zusaetzliche GM-/Correction-Calls" (Order §2/03_FIXAUFTRAG.md §4/§5 gelten
unveraendert auch fuer den Best-effort-Reachability-Fall).

Pure Python, nur `assert`, echter Exitcode, synthetische Daten/Temp-Dirs."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    build_two_member_table, make_env, seed_persona_state,
)

from mmo_sim.core import save_correction  # noqa: E402
from mmo_sim.core import store as core_store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import catalog, onboarding  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as save_correction_domain  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402
from mmo_sim.ui.tui import EndOfInput, TuiSession  # noqa: E402

_SCHEMA = _REPO_ROOT / "internal" / "qa" / "fixtures" / "persona-state.schema.json"
_CHAR_ID = "CHR-SNIPER-001"
#: `build_two_member_table` (`_section_completion_resume_fixtures.py`) bindet
#: `leader_pk` fest an diese Chrononaut-Id -- NUR fuer die beiden direkten
#: Guard-Tests unten gebraucht (TuiSession-Ende-zu-Ende-Test oben bindet
#: ueber `_make_ready`/`_CHAR_ID` unabhaengig davon).
_LEADER_CID = "chrono-leader"


def _queued_input(values: list[str]):
    q = list(values)

    def _fn(prompt: str = "") -> str:
        if not q:
            raise EOFError()
        return q.pop(0)
    return _fn


def _cap_overflow_candidate_block_for_char(char_id: str, save_id: str, level: int = 5) -> dict:
    """GENAU der native HQ-03-Fehlerklasse (7 NPCs/21 Milestones, NUR
    `maxItems`, KEINE Bindungsfehler, sofern `char_id` dem Aufrufer-
    erwarteten Chrononauten entspricht) -- s. Moduldocstring, Report."""
    block = full_v7_save(
        char_id, name="Yael", callsign="SNIPER", level=level, save_id=save_id,
        history={"milestones": [{"id": f"MS-{i}", "text": f"milestone {i}"} for i in range(21)]},
    )
    block["continuity"]["npc_roster"] = [{"id": f"NPC-{i}", "name": f"npc{i}"} for i in range(7)]
    return block


def _cap_overflow_candidate_block(save_id: str, level: int = 5) -> dict:
    return _cap_overflow_candidate_block_for_char(_CHAR_ID, save_id, level=level)


def _cap_overflow_candidate_text(save_id: str, level: int = 5) -> str:
    block = _cap_overflow_candidate_block(save_id, level=level)
    return "```json\n" + json.dumps(block, ensure_ascii=False) + "\n```"


class _ScriptedTableGm:
    """Wirft bei einem ueberzaehligen Call -- der direkte Beleg, dass die
    Best-effort-Uebernahme KEINEN zusaetzlichen GM-/Correction-Call
    ausloest (03_FIXAUFTRAG.md §4/§5, hier auf den Reachability-Fall
    angewandt)."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[str] = []

    def turn(self, idx, text, output_limit_tokens=None):
        self.calls.append(text)
        if not self._contents:
            raise AssertionError(
                f"_ScriptedTableGm: unerwarteter {len(self.calls)}. GM-Call (Skript erschoepft) "
                f"mit text={text!r} -- die Best-effort-Strukturvertrag-Uebernahme darf KEINEN "
                "zusaetzlichen GM-/Correction-Call ausloesen."
            )
        content = self._contents.pop(0)
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "table"}


def _env(root: Path):
    states_dir, run_dir = root / "states", root / "run"
    onboarding_dir, catalog_dir = root / "onboarding", root / "catalog"
    states_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    return states_dir, run_dir, onboarding_dir, catalog_dir


def _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, persona_key: str) -> dict:
    """Minimal gueltiger HQ-02-artiger Ausgangsstand (bewusst OHNE Cap-
    Ueberlauf) -- derselbe Aufbau wie `test_zr_r8_pending_save_commitfix_
    2026_11_20.py`s `_make_ready`, nur mit `full_v7_save` statt eines
    externen Fixture-Files (kein Bedarf an einer gebundenen Sniper-Fixture
    hier, das narrow-Save-Upgrade entfaellt dadurch)."""
    save = full_v7_save(_CHAR_ID, name="Yael", callsign="SNIPER", level=1, save_id="hq02-baseline")
    ps_store = PersonaStateStore(schema_path=_SCHEMA)
    chrono_id = _CHAR_ID
    onboarding.start_or_resume(onboarding_dir, persona_key)
    onboarding.complete_with_save(onboarding_dir, persona_key, save, ZeitrissHarvestValidator(), chrono_id)
    onboarding.ensure_participant_persona_state(ps_store, states_dir, persona_key, chrono_id, save)
    core_store.publish_current_save(run_dir, persona_key, save, ps_store, states_dir)
    catalog.register(catalog_dir, catalog.CatalogEntry(
        participant_id=persona_key, chrononaut_id=chrono_id, persona_key=persona_key,
    ))
    catalog.bind_for_section(catalog_dir, persona_key, chrono_id, has_open_section=False)
    return save


def _assert_calls(calls: list[str], expected_texts: list[str]) -> None:
    assert len(calls) == len(expected_texts), (calls, expected_texts)
    for actual, expected in zip(calls, expected_texts):
        assert actual == expected or actual.startswith(expected + "\n"), (actual, expected)


def test_m12_pre_send_structural_cap_overflow_candidate_reaches_best_effort_zero_gm_calls():
    """Kernregression (M12 Save-Correction-Reachability-Fix): der reale
    7/21-Fall. VOR dem Fix (Ausgangsstand 2ed250f1) blieb dieser Lauf
    dauerhaft `success=False`/HOLD (der bereits bestehende Best-effort-
    Strukturvertrag war fuer PRE-SEND unerreichbar) -- NACH dem Fix schliesst
    derselbe Kandidat GENAU EINMAL best-effort ab, OHNE jeden zusaetzlichen
    GM-/Correction-Call fuer den `!save`-Turn selbst."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        states_dir, run_dir, onboarding_dir, catalog_dir = _env(root)
        write_test_profile(run_dir)
        _make_ready(onboarding_dir, states_dir, run_dir, catalog_dir, "sniper")

        gm = _ScriptedTableGm([
            _cap_overflow_candidate_text("m12-hq03-overflow-001", level=5),  # normale Aktion -> Export.
            # KEIN zweiter Eintrag -- der '!save'-Turn darf den GM NIE erreichen.
        ])
        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=onboarding_dir, catalog_dir=catalog_dir, participant_id="sniper",
            input_fn=_queued_input([
                "Ich frage Halvorsen nach dem offenen Rift.",  # normale Aktion, SL liefert Export.
                "!save",  # PRE-SEND-Uebernahme -- muss 0 GM-Calls ausloesen.
                "",  # Pflicht-Abschlussnotiz -- leer = ueberspringen.
            ]),
            print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=_SCHEMA,
            gm_transport_factory=lambda *_a, **_kw: gm,
        )
        try:
            session._cmd_local_round()
        except EndOfInput:
            pass  # nach Abschluss endet die Runde regulaer.

        # 0 zusaetzliche GM-/Correction-Calls fuer den '!save'-Turn selbst --
        # NUR die eine normale Aktion wurde tatsaechlich an den GM gesendet.
        _assert_calls(gm.calls, ["Ich frage Halvorsen nach dem offenen Rift."])

        assert any("Abschnitt abgeschlossen" in p for p in printed), (
            "PASS-AFTER erwartet: der strukturell ueberlaufende, aber sonst "
            "vollstaendig gebundene Kandidat muss best-effort abschliessen, "
            f"statt in der alten HOLD-Sackgasse zu bleiben: {printed}"
        )
        ps_store = PersonaStateStore(schema_path=_SCHEMA)
        current_after = core_store.load_current_save(run_dir, "sniper", ps_store, states_dir=states_dir)
        assert current_after is not None and current_after.get("save_id") == "m12-hq03-overflow-001", (
            f"Current muss den best-effort uebernommenen Kandidaten tragen: {current_after}"
        )
        assert current_after["characters"][0].get("lvl") == 5, current_after
        assert len(current_after["continuity"]["npc_roster"]) == 7, (
            "der adoptierte Block bleibt der TATSAECHLICH beobachtete Kandidat "
            "(kein Hand-Prune durch diesen Fix -- die SL prunt beim naechsten "
            f"Laden/Speichern selbst): {current_after['continuity']['npc_roster']}"
        )

        # Erhaltene Guards: der angelegte Korrekturdatensatz ist EHRLICH als
        # best_effort geflaggt, mit 0 tatsaechlichen Zusatzversuchen (kein
        # Fake-DONE, keine versteckte Nachforderung) -- Scan ueber das
        # bestehende `save_corrections/`-Verzeichnis statt Rekonstruktion
        # des internen `repair_key`-Formats (Implementierungsdetail).
        records_dir = run_dir / "save_corrections"
        record_files = sorted(records_dir.glob("*.json")) if records_dir.is_dir() else []
        assert record_files, (
            "der bestehende Best-effort-Strukturvertrag muss GENAU EINEN "
            f"Korrekturdatensatz angelegt haben: {records_dir}"
        )
        matching = [
            json.loads(p.read_text(encoding="utf-8")) for p in record_files
            if json.loads(p.read_text(encoding="utf-8")).get("char_id") == _CHAR_ID
        ]
        assert matching, (record_files, _CHAR_ID)
        record = matching[0]
        assert record.get("best_effort") is True, record
        assert record.get("attempts_used") == 0, (
            "0 Zusatzversuche -- die Uebernahme darf KEINEN Korrekturversuch "
            f"gezaehlt haben: {record}"
        )
        assert record.get("state") == save_correction.STATE_ADOPTED, record


def test_m12_pre_send_binding_error_candidate_still_holds_no_regression():
    """Guard-Erhalt (KEINE Aufweichung), DIREKTER Aufruf der neuen Funktion
    `save_correction.pursue_pre_send_structural_best_effort` (derselbe
    Direktaufruf-Stil wie `test_r4_startfresh_group_best_effort_2026_10_29.
    py` fuer `pursue_group_save_correction`, echter `store.Lobby`/`Table`,
    echte `store.complete_section`): ein `missing`-Mitglied, dessen Block
    GLEICHZEITIG ueberlang UND falsch gebunden ist (falsche `char_id` fuer
    den von der Tabelle erwarteten Chrononauten), bleibt UNVERAENDERT
    `missing`/HOLD -- `has_residual_structural_cap_overflow`s bestehende
    Haertung (`acceptance.binding_errors` nicht leer -> `False`, UNVERAENDERT,
    dieser Fix ruft NUR die bestehende Funktion auf, aendert sie NICHT)
    verhindert, dass dieser Fix einen falsch gebundenen Envelope faelschlich
    best-effort durchwinkt.

    PR3314-Nachzug (Testfixture-Korrektur, General-Review §5): der Gast
    liefert jetzt einen VOLLSTAENDIG geeigneten, korrekt an `chrono-guest`
    gebundenen, schema-validen Block OHNE Cap-Ueberlauf -- der erste
    `complete_section`-Aufruf liefert dadurch `missing=={leader_pk}` (der
    Gast besteht `_validate_harvest` bereits). VORHER lieferte der Tisch gar
    keinen Gast-Block, `missing` war `{leader_pk, guest_pk}` -- selbst ein
    (hypothetisch) durchlaessiger Leader-Guard waere am fehlenden Gast
    GRUEN geblieben, OHNE dass der Leader-Guard selbst je geprueft wurde.
    Jetzt ist die falsche Leader-Bindung der EINZIGE moegliche Blocker."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-bindingerror")
        write_test_profile(env.run_dir)
        section_id = "section-m12-bindingerror"
        today = "2026-11-21"
        validator = ZeitrissHarvestValidator()

        wrong_block = _cap_overflow_candidate_block_for_char("CHR-WRONG-999", "m12-wrongbind-001")
        guest_block = full_v7_save("chrono-guest", name="Gast", callsign="GAST", level=1, save_id="m12-wrongbind-guest-001")
        harvested = {"leader_pk": wrong_block, "guest_pk": guest_block}
        harvest_completion = core_store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, today, validator, ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk"}, (
            harvest_completion
        )

        harvested_out, completion_out = save_correction.pursue_pre_send_structural_best_effort(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=today,
            harvest_validator=validator, persona_state_store=ps_store,
        )
        assert completion_out is harvest_completion and not completion_out.success, (
            f"ein falsch gebundener Kandidat darf NIE best-effort durchgehen: {completion_out}"
        )
        assert set(completion_out.missing) == {"leader_pk"}, completion_out
        assert list(
            (env.run_dir / "save_corrections").glob("*.json"),
        ) == [], "kein Korrekturdatensatz darf fuer einen abgelehnten Bindungsfehler-Kandidaten entstehen"


def test_m12_pre_send_all_or_nothing_one_genuinely_missing_member_blocks_whole_round():
    """Guard-Erhalt (All-oder-nichts, wie der bestehende erschoepfter-
    Budget-Zweig in `pursue_group_save_correction`): zwei `missing`-
    Mitglieder, EINES mit einem reinen Cap-Ueberlauf-Kandidaten, das ANDERE
    OHNE jeden Kandidaten (echt fehlender Gast) -- die GESAMTE Runde bleibt
    UNVERAENDERT `missing`/HOLD, KEIN Teil-Write fuer das eigentlich
    adoptable Mitglied (kein 'halb best-effort')."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-allornothing")
        write_test_profile(env.run_dir)
        section_id = "section-m12-allornothing"
        today = "2026-11-21"
        validator = ZeitrissHarvestValidator()

        overflow_block = _cap_overflow_candidate_block_for_char(_LEADER_CID, "m12-partial-001")
        harvested = {"leader_pk": overflow_block}  # guest_pk liefert GAR KEINEN Block.
        harvest_completion = core_store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, today, validator, ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}, (
            harvest_completion
        )

        harvested_out, completion_out = save_correction.pursue_pre_send_structural_best_effort(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=today,
            harvest_validator=validator, persona_state_store=ps_store,
        )
        assert completion_out is harvest_completion and not completion_out.success, (
            f"ein echt fehlendes Mitglied darf die Best-effort-Uebernahme des ANDEREN "
            f"Mitglieds NICHT ausloesen (kein Teil-Write): {completion_out}"
        )
        assert set(completion_out.missing) == {"leader_pk", "guest_pk"}, completion_out
        assert list((env.run_dir / "save_corrections").glob("*.json")) == [], (
            "All-oder-nichts: kein Korrekturdatensatz fuer IRGENDEIN Mitglied, solange "
            "nicht ALLE fehlenden Mitglieder einen adoptablen Kandidaten tragen"
        )


def test_m12_pre_send_stale_open_correction_record_stays_hold_no_silent_adopt():
    """Nachzug-Guard (Vera-Mangel 1, 2026-11-21): ein Mitglied traegt bereits
    einen Korrekturdatensatz in einem der drei OFFENEN Zwischenzustaende
    (`STATE_CORRECTION_PENDING`, hier via `load_or_init_record` +
    `begin_attempt` -- ein nach Crash/Admission-Pause mitten in
    `pursue_group_save_correction` stehengebliebener, bereits GEZAEHLTER
    Versuch). Der schnelle PRE-SEND-Best-effort-Pfad darf diesen laufenden
    Versuch NIE stillschweigend auf `adopted` umbiegen (und damit den
    gezaehlten Versuch verstecken bzw. einen womoeglich besseren, noch
    offenen SL-Kandidaten ueberschreiben), sondern muss die GESAMTE Runde
    UNVERAENDERT `missing`/HOLD lassen -- der regulaere Resume-/`pursue_
    group_save_correction`-Pfad uebernimmt. Beide Mitglieder tragen sonst
    adoptable Kandidaten, der Stale-Record ist also der EINZIGE Blocker (kein
    All-oder-nichts/Bindungs-/Identitaets-Confound). VOR dem Nachzug-Fix
    (nur die 4 TERMINALEN States geprueft, Z.588-590 am Zwischenstand) haette
    der offene State den Abbruch NICHT ausgeloest und `mark_adopted` haette
    den laufenden Versuch ueberschrieben."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-staleopen")
        write_test_profile(env.run_dir)
        section_id = "section-m12-staleopen"
        today = "2026-11-21"
        validator = ZeitrissHarvestValidator()

        harvested = {
            "leader_pk": _cap_overflow_candidate_block_for_char(_LEADER_CID, "m12-staleopen-leader"),
            "guest_pk": _cap_overflow_candidate_block_for_char("chrono-guest", "m12-staleopen-guest"),
        }
        harvest_completion = core_store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, today, validator, ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}, (
            harvest_completion
        )

        # Stale OFFENER Korrekturdatensatz NUR fuer den Leader: ein mitten in
        # der Gruppenkorrektur stehengebliebener, bereits GEZAEHLTER Versuch.
        repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        save_correction.load_or_init_record(
            env.run_dir, repair_key, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=save_correction.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        save_correction.begin_attempt(env.run_dir, repair_key)
        pre = save_correction.load_record(env.run_dir, repair_key)
        assert pre["state"] == save_correction.STATE_CORRECTION_PENDING and pre["attempts_used"] == 1, pre

        harvested_out, completion_out = save_correction.pursue_pre_send_structural_best_effort(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=today,
            harvest_validator=validator, persona_state_store=ps_store,
        )
        assert completion_out is harvest_completion and not completion_out.success, (
            f"ein offener (nicht-terminaler) Korrekturdatensatz muss den schnellen "
            f"PRE-SEND-Pfad abbrechen (kein stilles 'adopt'): {completion_out}"
        )
        assert set(completion_out.missing) == {"leader_pk", "guest_pk"}, completion_out

        post = save_correction.load_record(env.run_dir, repair_key)
        assert post["state"] == save_correction.STATE_CORRECTION_PENDING, (
            f"der laufende Versuch darf NICHT auf 'adopted' umgebogen werden: {post}"
        )
        assert post["attempts_used"] == 1, (
            f"der bereits gezaehlte Versuch darf nicht versteckt/zurueckgesetzt werden: {post}"
        )
        record_files = list((env.run_dir / "save_corrections").glob("*.json"))
        assert len(record_files) == 1, (
            "nur der eine vorbestehende Leader-Record darf existieren, es darf KEIN "
            f"neuer Gast-Record entstehen (All-oder-nichts-Abbruch vor dem Write): {record_files}"
        )


def test_m12_pre_send_identity_drift_leaves_no_falsely_adopted_record():
    """Nachzug-Guard (Vera-Mangel 2, 2026-11-21): ein Mitglied liefert einen
    korrekt GEBUNDENEN, nur cap-ueberlaufenden Kandidaten (besteht
    `has_residual_structural_cap_overflow`), aber sein PERSISTIERTER
    Persona-State ist identitaets-gedriftet (`plays_char.character_id` !=
    vom Tisch erwarteter Chrononaut). `store._validate_harvest` prueft
    Identitaet ERST NACH `validate_block` (store.py:1792-1804) -- auf dem
    ERSTEN (nicht-best_effort) `complete_section` wurde der Block schon wegen
    Cap-Ueberlauf verworfen, die Identitaetspruefung lief dort also nie. Ohne
    die Identitaets-VORABpruefung liefe `mark_adopted` zuerst und der
    best_effort-`complete_section` scheiterte DANACH erst an der Identitaet --
    der Korrekturdatensatz bliebe dauerhaft faelschlich `adopted` (neuer,
    schlimmerer Dead-End). Erwartung NACH Fix: All-oder-nichts-Abbruch VOR
    jedem Write -- Runde bleibt UNVERAENDERT `missing`/HOLD, und es entsteht
    KEIN (schon gar kein faelschlich adoptierter) Korrekturdatensatz."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-identitydrift")
        write_test_profile(env.run_dir)
        section_id = "section-m12-identitydrift"
        today = "2026-11-21"
        validator = ZeitrissHarvestValidator()

        # Leader-Block korrekt an chrono-leader gebunden (besteht has_residual),
        # aber der persistierte Persona-State driftet weg (anderer character_id).
        seed_persona_state(ps_store, env.states_dir, "leader_pk", "chrono-leader-DRIFT")

        harvested = {
            "leader_pk": _cap_overflow_candidate_block_for_char(_LEADER_CID, "m12-drift-leader"),
            "guest_pk": _cap_overflow_candidate_block_for_char("chrono-guest", "m12-drift-guest"),
        }
        harvest_completion = core_store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, today, validator, ps_store,
        )
        assert not harvest_completion.success and "leader_pk" in harvest_completion.missing, harvest_completion

        harvested_out, completion_out = save_correction.pursue_pre_send_structural_best_effort(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=today,
            harvest_validator=validator, persona_state_store=ps_store,
        )
        assert completion_out is harvest_completion and not completion_out.success, (
            f"ein identitaets-gedriftetes Mitglied muss die Best-effort-Uebernahme VORAB "
            f"(vor jedem Write) abbrechen: {completion_out}"
        )
        assert list((env.run_dir / "save_corrections").glob("*.json")) == [], (
            "KEIN (schon gar kein faelschlich 'adopted') Korrekturdatensatz darf entstehen, "
            "wenn die Identitaet vorab scheitert -- sonst neuer Dead-End"
        )


def test_m12_pre_send_prev_ref_override_pins_original_snapshot_not_fresh_current():
    """F1a (ZR-R8-PR3314-Nachzug, 2026-11-21): ein best-effort-Abschluss MIT
    gesetztem `prev_ref_override` muss `expected_prev_ref` im gepinnten Plan
    aus dem ORIGINAL-Snapshot binden, NICHT aus dem beim Abschluss frisch
    gelesenen Current (hier fuer beide frischen Mitglieder `None`). Das ist
    GENAU der F1-Fehler: der zweite `store.complete_section`-Aufruf im alten
    Code setzte `best_effort=True`, aber NIE `prev_ref_override` -- `store.
    py:2274-2275` nahm dann den frisch gelesenen Current statt der
    durabel gebundenen Erwartung.

    Fail-before (Revert auf 1e8e5ec5, s. Verifikationslauf im Report): die
    Vorgaengerfassung von `pursue_pre_send_structural_best_effort` besitzt
    GAR KEINEN `prev_ref_override`-Parameter -- der Aufruf mit diesem
    Keyword schlaegt dort mit `TypeError` fehl, der alte zweite `complete_
    section`-Aufruf uebergibt structural NIE einen Override."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-f1a")
        write_test_profile(env.run_dir)
        section_id = "section-m12-f1a"
        today = "2026-11-21"
        validator = ZeitrissHarvestValidator()

        harvested = {
            "leader_pk": _cap_overflow_candidate_block_for_char(_LEADER_CID, "m12-f1a-leader"),
            "guest_pk": _cap_overflow_candidate_block_for_char("chrono-guest", "m12-f1a-guest"),
        }
        harvest_completion = core_store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, today, validator, ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}, (
            harvest_completion
        )

        frozen_snapshot = {
            "leader_pk": {"run_id": "frozen-run", "seq": 7},
            "guest_pk": {"run_id": "frozen-run", "seq": 3},
        }
        save_correction.pursue_pre_send_structural_best_effort(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=today,
            harvest_validator=validator, persona_state_store=ps_store,
            prev_ref_override=frozen_snapshot,
        )

        plan_path = core_store._completion_plan_path(env.run_dir, section_id)
        assert plan_path.exists(), "ein Abschluss-Auftrag muss trotz Vorgaenger-Mismatch gepinnt worden sein"
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        for pk, expected in frozen_snapshot.items():
            assert plan_data["members"][pk]["expected_prev_ref"] == expected, (
                f"expected_prev_ref fuer {pk} muss der ORIGINAL-Snapshot sein, NICHT der frisch "
                f"gelesene (hier: None) Current-Stand: {plan_data['members'][pk]}"
            )


def test_m12_pre_send_prev_ref_override_form_hold_leaves_no_record():
    """F1b (ZR-R8-PR3314-Nachzug, 2026-11-21): ein unvollstaendiger
    `prev_ref_override` (hier: fehlender `guest_pk`-Schluessel) muss den
    gesamten Abschluss VORAB (vor jedem Write) mit HOLD abbrechen und darf
    KEINEN Korrekturdatensatz/keinen Abschluss-Auftrag hinterlassen --
    `store._prev_ref_override_hold_reason` wird hier VOR dem `mark_adopted`-
    Write aufgerufen, nicht erst (zu spaet) im zweiten `complete_section`.

    Fail-before (Revert auf 1e8e5ec5): kein `prev_ref_override`-Parameter
    vorhanden -- `TypeError` bei diesem Aufruf."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-f1b")
        write_test_profile(env.run_dir)
        section_id = "section-m12-f1b"
        today = "2026-11-21"
        validator = ZeitrissHarvestValidator()

        harvested = {
            "leader_pk": _cap_overflow_candidate_block_for_char(_LEADER_CID, "m12-f1b-leader"),
            "guest_pk": _cap_overflow_candidate_block_for_char("chrono-guest", "m12-f1b-guest"),
        }
        harvest_completion = core_store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, today, validator, ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}, (
            harvest_completion
        )

        incomplete_override = {"leader_pk": {"run_id": "frozen-run", "seq": 7}}  # guest_pk fehlt.

        harvested_out, completion_out = save_correction.pursue_pre_send_structural_best_effort(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=today,
            harvest_validator=validator, persona_state_store=ps_store,
            prev_ref_override=incomplete_override,
        )
        assert completion_out is harvest_completion and not completion_out.success, (
            f"ein unvollstaendiger Override muss die gesamte Uebernahme VORAB abbrechen: {completion_out}"
        )
        assert list((env.run_dir / "save_corrections").glob("*.json")) == [], (
            "KEIN Korrekturdatensatz darf bei Form-HOLD entstehen -- sonst irrefuehrend vorab adoptiert"
        )
        assert not core_store._completion_plan_path(env.run_dir, section_id).exists(), (
            "kein Abschluss-Auftrag darf bei Form-HOLD gepinnt werden"
        )


def test_m12_pre_send_resume_after_own_adopted_interruption_completes_idempotently():
    """F2a (ZR-R8-PR3314-Nachzug, 2026-11-21): ein eigener, originalgebundener
    `adopted`/`attempts_used=0`/`best_effort=True`-Zwischenstand (Abbruch
    NACH `mark_adopted`, VOR dem zweiten `store.complete_section`-Aufruf --
    derselbe Kandidat wie beim fruehen Aufruf) darf einen frischen Reentry
    NICHT dauerhaft sperren: idempotenter Abschluss, 0 neue GM-/Correction-
    Calls (reiner Direktaufruf, kein Transport beteiligt), `attempts_used`
    bleibt `0`, genau EINE Save-Version je Mitglied.

    Fail-before (Revert auf 1e8e5ec5, pauschaler `if existing_record is not
    None: return`-Guard ohne Unterscheidung): bleibt HOLD, `missing`
    unveraendert, keine neue Version."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-f2a")
        write_test_profile(env.run_dir)
        section_id = "section-m12-f2a"
        today = "2026-11-21"
        validator = ZeitrissHarvestValidator()

        leader_block = _cap_overflow_candidate_block_for_char(_LEADER_CID, "m12-f2a-leader")
        guest_block = _cap_overflow_candidate_block_for_char("chrono-guest", "m12-f2a-guest")
        harvested = {"leader_pk": leader_block, "guest_pk": guest_block}
        harvest_completion = core_store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, today, validator, ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}, (
            harvest_completion
        )

        # Simuliert eine fruehere, unterbrochene Ausfuehrung dieser Funktion:
        # BEIDE Mitglieder bereits adopted/best_effort mit attempts_used=0,
        # originalgebunden an GENAU diese Kandidaten.
        members = [("leader_pk", _LEADER_CID, leader_block), ("guest_pk", "chrono-guest", guest_block)]
        for pk, char_id, block in members:
            repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
            save_correction.load_or_init_record(
                env.run_dir, repair_key, persona_key=pk, char_id=char_id,
                operation_key=save_correction.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
                original_block=block,
            )
            save_correction.mark_adopted(env.run_dir, repair_key, adopted_block=block, best_effort=True)

        harvested_out, completion_out = save_correction.pursue_pre_send_structural_best_effort(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=today,
            harvest_validator=validator, persona_state_store=ps_store,
        )
        assert completion_out.success, (
            f"ein frischer Reentry auf den eigenen adopted/0-Zwischenstand muss idempotent "
            f"abschliessen, statt dauerhaft HOLD zu bleiben: {completion_out}"
        )
        for pk, char_id, _block in members:
            repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
            record = save_correction.load_record(env.run_dir, repair_key)
            assert record["attempts_used"] == 0, (
                f"0 Zusatzversuche -- ein Resume darf KEINEN Versuch zaehlen: {record}"
            )
            assert record["state"] == save_correction.STATE_ADOPTED and record.get("best_effort") is True, record
            versions = list((env.run_dir / "current_saves" / f"{pk}__versions").glob("*.json"))
            assert len(versions) == 1, (
                f"genau EINE Save-Version je Mitglied -- kein Doppelspiel durch den Resume: {versions}"
            )


def test_m12_pre_send_resume_after_own_validating_interruption_completes_idempotently():
    """F2b (ZR-R8-PR3314-Nachzug, 2026-11-21): analog zu F2a, aber fuer den
    noch frueheren Abbruch -- NUR `load_or_init_record` lief (originalgebunden
    via `bound_block`), `mark_adopted` wurde NIE erreicht (`validating`/
    `attempts_used=0`). Ein frischer Reentry mit demselben Kandidaten muss
    trotzdem idempotent abschliessen -- die bestehende Write-Schleife
    (`load_or_init_record` gibt den vorhandenen Record unveraendert zurueck,
    `mark_adopted` setzt `adopted` jetzt erstmalig) ist dafuer bereits
    ausreichend.

    Fail-before (Revert auf 1e8e5ec5): bleibt HOLD, GENAUSO wie F2a."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-f2b")
        write_test_profile(env.run_dir)
        section_id = "section-m12-f2b"
        today = "2026-11-21"
        validator = ZeitrissHarvestValidator()

        leader_block = _cap_overflow_candidate_block_for_char(_LEADER_CID, "m12-f2b-leader")
        guest_block = _cap_overflow_candidate_block_for_char("chrono-guest", "m12-f2b-guest")
        harvested = {"leader_pk": leader_block, "guest_pk": guest_block}
        harvest_completion = core_store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, today, validator, ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}, (
            harvest_completion
        )

        # Simuliert den noch frueheren Abbruch: nur load_or_init_record lief.
        members = [("leader_pk", _LEADER_CID, leader_block), ("guest_pk", "chrono-guest", guest_block)]
        for pk, char_id, block in members:
            repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
            save_correction.load_or_init_record(
                env.run_dir, repair_key, persona_key=pk, char_id=char_id,
                operation_key=save_correction.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
                original_block=block,
            )
            pre = save_correction.load_record(env.run_dir, repair_key)
            assert pre["state"] == save_correction.STATE_VALIDATING and pre["attempts_used"] == 0, pre

        harvested_out, completion_out = save_correction.pursue_pre_send_structural_best_effort(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=today,
            harvest_validator=validator, persona_state_store=ps_store,
        )
        assert completion_out.success, (
            f"ein frischer Reentry auf den eigenen validating/0-Zwischenstand muss idempotent "
            f"abschliessen, statt dauerhaft HOLD zu bleiben: {completion_out}"
        )
        for pk, char_id, _block in members:
            repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
            record = save_correction.load_record(env.run_dir, repair_key)
            assert record["attempts_used"] == 0, record
            assert record["state"] == save_correction.STATE_ADOPTED and record.get("best_effort") is True, record
            versions = list((env.run_dir / "current_saves" / f"{pk}__versions").glob("*.json"))
            assert len(versions) == 1, versions


def test_m12_pre_send_foreign_adopted_without_best_effort_record_stays_protected():
    """F2c (ZR-R8-PR3314-Nachzug, 2026-11-21): ein fremder, bereits
    `adopted`-Record OHNE `best_effort`-Flag (z.B. ein regulaer -- NICHT ueber
    diesen Schnellpfad -- angenommener Kandidat eines anderen Laufs) ist KEIN
    eigener resumierbarer Zwischenstand (`_pre_send_resumable_own_record`
    verlangt bei `adopted` zwingend `best_effort is True`) -- bleibt
    dauerhaft HOLD, GENAUSO vor wie nach diesem Fix (Guard-Erhalt, keine
    Aufweichung auf JEDEN `adopted`-Record)."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-m12-f2c")
        write_test_profile(env.run_dir)
        section_id = "section-m12-f2c"
        today = "2026-11-21"
        validator = ZeitrissHarvestValidator()

        leader_block = _cap_overflow_candidate_block_for_char(_LEADER_CID, "m12-f2c-leader")
        guest_block = _cap_overflow_candidate_block_for_char("chrono-guest", "m12-f2c-guest")
        harvested = {"leader_pk": leader_block, "guest_pk": guest_block}
        harvest_completion = core_store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, today, validator, ps_store,
        )
        assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}, (
            harvest_completion
        )

        # Fremder Record NUR fuer den Leader: bereits 'adopted', aber OHNE
        # best_effort (regulaer angenommener Kandidat eines ANDEREN Pfads).
        repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        save_correction.load_or_init_record(
            env.run_dir, repair_key, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=save_correction.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        save_correction.mark_adopted(env.run_dir, repair_key, adopted_block=leader_block)
        pre = save_correction.load_record(env.run_dir, repair_key)
        assert pre["state"] == save_correction.STATE_ADOPTED and not pre.get("best_effort"), pre

        harvested_out, completion_out = save_correction.pursue_pre_send_structural_best_effort(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested,
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=today,
            harvest_validator=validator, persona_state_store=ps_store,
        )
        assert completion_out is harvest_completion and not completion_out.success, (
            f"ein fremder adopted-Record OHNE best_effort darf NIE als eigener Zwischenstand "
            f"durchgehen: {completion_out}"
        )
        post = save_correction.load_record(env.run_dir, repair_key)
        assert post == pre, f"der fremde Record darf UNVERAENDERT bleiben: {post} vs {pre}"
        record_files = list((env.run_dir / "save_corrections").glob("*.json"))
        assert len(record_files) == 1, (
            f"kein neuer Gast-Record darf entstehen, solange der fremde Leader-Record blockt: {record_files}"
        )


if __name__ == "__main__":
    import traceback

    tests = [
        test_m12_pre_send_structural_cap_overflow_candidate_reaches_best_effort_zero_gm_calls,
        test_m12_pre_send_binding_error_candidate_still_holds_no_regression,
        test_m12_pre_send_all_or_nothing_one_genuinely_missing_member_blocks_whole_round,
        test_m12_pre_send_stale_open_correction_record_stays_hold_no_silent_adopt,
        test_m12_pre_send_identity_drift_leaves_no_falsely_adopted_record,
        test_m12_pre_send_prev_ref_override_pins_original_snapshot_not_fresh_current,
        test_m12_pre_send_prev_ref_override_form_hold_leaves_no_record,
        test_m12_pre_send_resume_after_own_adopted_interruption_completes_idempotently,
        test_m12_pre_send_resume_after_own_validating_interruption_completes_idempotently,
        test_m12_pre_send_foreign_adopted_without_best_effort_record_stays_protected,
    ]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except Exception:
            failures += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    if failures:
        sys.exit(1)
    print(f"{len(tests)} Tests gruen.")
