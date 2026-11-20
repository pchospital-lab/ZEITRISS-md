#!/usr/bin/env python3
"""
tests/mmo_sim/test_j3_entry_recovery_20261120.py — ZR-R8-LIVESYNC-
PALIMPSEST-20261119-R1, Stage J, Lauf 3 (Entry-Recovery-Fix 20261120).

Belegter Restfehler (vom General bestaetigt, s. Integrator-Briefing):
das Lauf-2-Gate (`runtime.py`, `ongoing_round > 0 and (...)`) sitzt HINTER
`ongoing_round > 0`. Bei einem FRISCHEN Einstieg wird die while-Schleife
erst mit `ongoing_round == 0` betreten -- das Gate wird uebersprungen,
`act(leader, debrief_ctx)` feuert EINEN GM-Zug, bevor die Recovery greift.
Zusaetzlich feuert bei frischem Prozess der Leader-Anker. Das erfuellt den
beauftragten MODELLFREIEN Resume NICHT.

Fix (eng, additiv, member-bound): ein DRITTES Entry-Gate direkt nach dem
bestehenden `has_open_group_round`-Gate und VOR jedem Anker-/Import-/
Spielzug (`runtime.py run_full_section`), das denselben rein lesenden
`has_resumable_group_hold`-Vertrag nutzt -- jetzt zusaetzlich an die
AKTUELLEN Tischmitglieder gebunden (`group_member_repair_keys`, reuse
`save_correction_domain.group_repair_key`, kein Mirror-Drift).

Treibt den ECHTEN Caller (`core.app_service.run_play_session` ->
`core.runtime.SectionRuntime.run_full_section`) -- EIN direkter
Helfer-Test allein genuegt NICHT (Flo-Vorgabe). Der GM-/Korrektur-
Transport-Stub (`ExplodingGmTransport`) raist bei JEDEM unerwarteten
`.turn()`-Aufruf; die Pflicht-Reflexion wird UEBER DENSELBEN
Entscheidungskanal (`ReflectionOnlyDriver`) separat, EHRLICH gezaehlt --
NICHT abgeschaltet, um einen Null-Call-Test zu erzwingen.

Geldfrei per Konstruktion: ausschliesslich In-Process-Fakes (kein echter
Transport, keine echten HTTP-Requests). Pure Python, nur `assert`, echter
Exitcode -- gleiches Muster wie die bestehende Suite."""
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
from _r12_window_hold_fixture import open_window  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    ExplodingGmTransport, ReflectionOnlyDriver, ScriptedGmTransport,
    build_two_member_table, make_env, make_ps_store, seed_persona_state,
)

import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core import app_service  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER,
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
    build_save_command_completion_fallback,
    is_save_command,
    is_saveguard_rejection,
)

_LEADER_CID = "chrono-leader"
_GUEST_CID = "chrono-guest"
_CID_TO_PK_SOLO = {_LEADER_CID: "leader_pk"}
_CID_TO_PK_DUO = {_LEADER_CID: "leader_pk", _GUEST_CID: "guest_pk"}
_TODAY = "2026-11-20"


def _fenced_json(block: dict) -> str:
    return f"```json\n{json.dumps(block)}\n```"


def _overcap_only(cid: str, name: str = "Leader") -> dict:
    """Reine Cap-Ueberlauf-Form (3 `maxItems`-Fehler, KEINE Bindungs-/Typ-/
    Identitaetsfehler) -- analog zur echten M8-`best_candidate_block`-Form."""
    block = full_v7_save(cid, name=name)
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}", "scope": "campaign", "text": f"erinnerung-{i}"} for i in range(8)
    ]
    block["arc"]["hooks"] = [{"text": f"hook-{i}"} for i in range(8)]
    block["arc"]["questions"] = [f"frage-{i}" for i in range(9)]
    return block


def _build_solo_table(root: Path, table_id: str):
    env = make_env(root)
    schema_path = env.run_dir.parent / "schema.json"
    ps_store = make_ps_store(schema_path)
    seed_persona_state(ps_store, env.states_dir, "leader_pk", _LEADER_CID)

    lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[{"type": "offer", "id": "o1", "from": "leader_pk", "wants": []}],
        chrononaut_ids={"leader_pk": _LEADER_CID},
    )
    assert table is not None, f"Solo-Tisch haette entstehen muessen: {derivation}"
    write_test_profile(env.run_dir)
    open_window(env.run_dir)
    return env, lobby, table, ps_store


def _drive_leader_into_entry_hold_drift(env, lobby, table, ps_store, section_id: str):
    """Reproduziert den realen `__11`-Fall: ein terminaler Entry-HOLD mit
    `last_reason="unjustified_semantic_drift"`, `adopted_block=None`, einem
    rein cap-ueberlangen `best_candidate_block`, KEINEM `.open.json`-Marker,
    KEINEM gepinnten Plan -- ueber den ECHTEN Aufrufer
    `pursue_group_save_correction`."""
    leader_old = _overcap_only(_LEADER_CID)
    harvested = {"leader_pk": leader_old}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, _TODAY,
        ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and harvest_completion.missing == ["leader_pk"], harvest_completion

    drifted = _overcap_only(_LEADER_CID)
    drifted["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}-neu", "scope": "campaign", "text": f"erinnerung-{i}-neu"} for i in range(6)
    ]
    drifted["arc"]["hooks"][0]["text"] = "ausserhalb-des-korrekturauftrags-umformuliert"
    gm = ScriptedGmTransport(scripted_contents=[_fenced_json(drifted)])
    harvested_out, completion_out = sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=env.states_dir, today=_TODAY,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=gm, cid_to_pk=_CID_TO_PK_SOLO, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    assert not completion_out.success, completion_out

    repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
    record = sc.load_record(env.run_dir, repair_key)
    assert record["state"] == "hold" and record["last_reason"] == "unjustified_semantic_drift", record
    assert record.get("adopted_block") is None, record
    assert record.get("best_candidate_block") == leader_old, record
    assert sc.has_residual_structural_cap_overflow(record["best_candidate_block"], _LEADER_CID), (
        "Vorbedingung: der gebundene Originalentwurf darf NUR noch den Cap-Ueberlauf tragen."
    )
    assert not sc._open_round_path(env.run_dir, table.table_id, section_id).exists()
    assert store.open_completion_order_for_table(env.run_dir, table.table_id) is None
    return leader_old, repair_key


def _run_section(lobby, table, ps_store, gm, controller, section_id, states_dir, ts, max_turns=1):
    return app_service.run_play_session(
        lobby, table, gm, controller, section_id,
        {"leader_pk": {"user": "ctx-leader_pk"}, "guest_pk": {"user": "ctx-guest_pk"}},
        states_dir, _TODAY, ts, COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, max_turns=max_turns,
        completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
        explicit_completion_attempt=is_save_command,
        save_guard_rejection_detector=is_saveguard_rejection,
    )


# ---------------------------------------------------------------------------
# (1) Echter FRISCHER Einstieg (kein Leader-Anker, kein Import erledigt):
#     die Entry-Recovery greift VOR jedem GM-Zug, braucht KEINEN
#     vorbereitenden Erzaehlzug, ist mit NUR EINEM verfuegbaren Spielturn
#     erreichbar. GM-Stub raist bei jedem unerwarteten Aufruf. Reflexions-
#     Role wird separat, ehrlich gezaehlt (NICHT erzwungen).
# ---------------------------------------------------------------------------

def test_j3_fresh_entry_recovers_before_any_gm_or_story_turn():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j3-case1")
        section_id = "section-j3-case1"
        leader_old, repair_key = _drive_leader_into_entry_hold_drift(env, lobby, table, ps_store, section_id)
        record_before_resume = sc.load_record(env.run_dir, repair_key)
        requests_dir = env.run_dir / "requests"
        requests_before = sorted(p.name for p in requests_dir.glob("*.json")) if requests_dir.is_dir() else []

        # ECHTER frischer Prozess: KEIN Leader-Anker-Origin im sl_log, KEIN
        # Import erledigt -- genau der Zustand, den das L2-Gate NICHT mehr
        # modellfrei abgefangen hat (Leader-Anker UND der erste GM-Zug
        # feuern vor dem alten, hinter `ongoing_round > 0` sitzenden Gate).
        table2 = store.Table.load(env.run_dir, table.table_id)

        gm_stub = ExplodingGmTransport()
        reflection_driver = ReflectionOnlyDriver(reflection_text="Kurzer Rueckblick.")
        controller2 = TableController(leader_key="leader_pk", drivers={"leader_pk": reflection_driver})

        # max_turns=1: die Recovery muss auch mit nur einem verfuegbaren
        # Spielturn erreichbar sein (Entry-Gate feuert VOR der Turn-Schleife).
        outcome = _run_section(
            lobby, table2, ps_store, gm_stub, controller2, section_id, env.states_dir, "2026-11-20T09:30:00",
            max_turns=1,
        )

        assert outcome.completion.success, (
            f"die Entry-Recovery haette den Drift-HOLD best-effort abschliessen muessen: {outcome.completion}"
        )
        record_after = sc.load_record(env.run_dir, repair_key)
        assert record_after["state"] == "adopted" and record_after.get("best_effort") is True, record_after
        assert record_after["adopted_block"] == leader_old, record_after
        assert record_after["attempts_used"] == record_before_resume["attempts_used"], (
            "best-effort-Adopt darf den Versuchszaehler NICHT veraendern (kein neuer Send)."
        )

        # Null neue GM-/Korrektur-Modellaufrufe: der Stub ist so konstruiert,
        # dass JEDER .turn()-Aufruf eine AssertionError wirft -- die Recovery
        # ist oben bereits OHNE Exception durchgelaufen, also GENAU NULL Calls.
        assert gm_stub.calls == 0, f"kein GM-/Korrektur-Call erwartet: {gm_stub.calls}"

        # Reflexions-Role EHRLICH ausgewiesen (separater Role, NICHT
        # abgeschaltet): die Pflichtreflexion fuer leader_pk ist fuer DIESEN
        # Abschnitt noch nicht committet -- genau EIN Reflexionsaufruf.
        assert reflection_driver.calls == 1, (
            f"Reflexions-Role-Call-Zaehler (separat von GM/Korrektur): {reflection_driver.calls}"
        )
        reflections_path = env.run_dir / "reflections.jsonl"
        reflection_entries = [
            json.loads(line) for line in reflections_path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        committed = [e for e in reflection_entries if e.get("kind") == "ai_required_reflection"]
        assert len(committed) == 1 and committed[0]["persona_key"] == "leader_pk", reflection_entries

        # Keine neue save_correction_group-Request (role==ROLE_GROUP).
        requests_after = sorted(p.name for p in requests_dir.glob("*.json")) if requests_dir.is_dir() else []
        new_request_names = sorted(set(requests_after) - set(requests_before))
        new_correction_requests = [
            name for name in new_request_names
            if json.loads((requests_dir / name).read_text(encoding="utf-8")).get("role") == sc.ROLE_GROUP
        ]
        assert new_correction_requests == [], (
            f"keine neue save_correction_group-Request erwartet: {new_correction_requests} "
            f"(alle neuen Requests: {new_request_names})"
        )

        final_path = env.run_dir / "completion" / f"{section_id}__final.json"
        assert final_path.exists(), "PHASE 2 (Reflexion/Finalize) haette den best-effort-Abschluss abschliessen muessen."
        final_data = json.loads(final_path.read_text(encoding="utf-8"))
        assert final_data.get("best_effort") is True, final_data
        assert final_data.get("best_effort_members") == ["leader_pk"], final_data


# ---------------------------------------------------------------------------
# (2) Zweiter vollstaendiger Einstieg/Neustart: idempotent, keine erneute
#     Adoption, kein unnoetiger Call, Record bytegleich.
# ---------------------------------------------------------------------------

def test_j3_second_fresh_entry_after_restart_is_idempotent():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j3-case2")
        section_id = "section-j3-case2"
        leader_old, repair_key = _drive_leader_into_entry_hold_drift(env, lobby, table, ps_store, section_id)

        table2 = store.Table.load(env.run_dir, table.table_id)
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver(reflection_text="Rueckblick eins."),
        })
        outcome1 = _run_section(
            lobby, table2, ps_store, ExplodingGmTransport(), controller2, section_id, env.states_dir,
            "2026-11-20T09:30:00", max_turns=1,
        )
        assert outcome1.completion.success, outcome1.completion
        record_after_first = sc.load_record(env.run_dir, repair_key)
        assert record_after_first["state"] == "adopted"

        assert not sc.has_resumable_group_hold(
            env.run_dir, table.table_id, section_id,
            member_repair_keys=sc.group_member_repair_keys(table2, section_id),
        ), "nach erfolgreicher Adoption darf das Praedikat NICHT mehr True liefern."

        # Zweiter vollstaendiger Einstieg/Neustart: DIREKT ueber denselben
        # idempotenten `complete_section`-Weg wie der bestehende L2-Sibling-
        # Test (`test_j2_real_caller_...`) -- ein zweiter `run_full_section`-
        # Durchlauf auf einem BEREITS `status=closed`-Tisch ist ein eigener,
        # von diesem engen Entry-Recovery-Fix UNABHAENGIGER Codepfad (kein
        # Entry-Gate dieser Stage deckt "schon finalisiert, aber Tisch/
        # Runtime erneut angetreten" -- das ist kein Teil des beauftragten
        # Restfehlers). Der hier gepruefte Vertrag ("kein unnoetiger Call,
        # Idempotenz, Record bytegleich") gilt fuer den Korrekturdatensatz
        # selbst, nicht fuer eine zweite volle Runtime-Session.
        idempotent_completion = store.complete_section(
            lobby, table2, section_id, {}, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert idempotent_completion.success and idempotent_completion.already_completed, idempotent_completion
        record_after_second = sc.load_record(env.run_dir, repair_key)
        assert record_after_second == record_after_first, (
            "ein idempotenter Re-Poll nach Finalisierung darf den Korrekturdatensatz NICHT veraendern."
        )


# ---------------------------------------------------------------------------
# (3) Negative Faelle am Aufrufer sichtbar: falsche Bindung, Bindungsfehler,
#     bereits adoptiert, Member-Bindung (fremder Record).
# ---------------------------------------------------------------------------

def test_j3_entry_gate_predicate_negative_cases_visible_at_caller():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j3-case3")
        section_id = "section-j3-case3"
        _drive_leader_into_entry_hold_drift(env, lobby, table, ps_store, section_id)
        own_keys = sc.group_member_repair_keys(table, section_id)
        assert own_keys == {domain.group_repair_key(table.table_id, section_id, _LEADER_CID)}

        # falsche char/table/section-Bindung -> Entry-Gate feuert NICHT.
        assert not sc.has_resumable_group_hold(
            env.run_dir, table.table_id, "section-FREMD", member_repair_keys=own_keys,
        )
        assert not sc.has_resumable_group_hold(
            env.run_dir, "t-FREMDER-TISCH", section_id, member_repair_keys=own_keys,
        )

        # Member-Bindung: ein HOLD-Record, dessen repair_key NICHT zu einem
        # aktuellen Tischmitglied gehoert (fremde/abgegangene Figur), darf
        # das Entry-Gate NICHT ausloesen -- auch wenn table_id/section_id
        # exakt passen.
        foreign_keys = {domain.group_repair_key(table.table_id, section_id, "chrono-FREMD-ABGEGANGEN")}
        assert not sc.has_resumable_group_hold(
            env.run_dir, table.table_id, section_id, member_repair_keys=foreign_keys,
        ), "ein Record einer fremden/abgegangenen Figur darf das Entry-Gate NICHT ausloesen."
        # Ohne das kwarg (Rueckwaertskompatibilitaet) bleibt das Praedikat
        # unveraendert True fuer den echten Record.
        assert sc.has_resumable_group_hold(env.run_dir, table.table_id, section_id)
        assert sc.has_resumable_group_hold(
            env.run_dir, table.table_id, section_id, member_repair_keys=own_keys,
        )

        # Kandidat mit Bindungsfehler (nicht nur Cap-Overflow) -> False.
        section_id2 = "section-j3-case3b"
        repair_key2 = domain.group_repair_key(table.table_id, section_id2, _LEADER_CID)
        sc.load_or_init_record(
            env.run_dir, repair_key2, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id2,
        )
        mis_bound = _overcap_only("chrono-FREMD")
        sc.update_best_candidate(env.run_dir, repair_key2, block=mis_bound, error_count=99)
        sc.mark_hold(env.run_dir, repair_key2, reason="unjustified_semantic_drift")
        assert not sc.has_residual_structural_cap_overflow(mis_bound, _LEADER_CID)
        own_keys2 = sc.group_member_repair_keys(table, section_id2)
        assert not sc.has_resumable_group_hold(
            env.run_dir, table.table_id, section_id2, member_repair_keys=own_keys2,
        ), "ein Kandidat mit Bindungsfehler darf NICHT best-effort-faehig gemeldet werden."

        # adopted_block bereits gesetzt -> False.
        section_id3 = "section-j3-case3c"
        repair_key3 = domain.group_repair_key(table.table_id, section_id3, _LEADER_CID)
        sc.load_or_init_record(
            env.run_dir, repair_key3, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id3,
        )
        candidate = _overcap_only(_LEADER_CID)
        sc.update_best_candidate(env.run_dir, repair_key3, block=candidate, error_count=3)
        sc.mark_hold(env.run_dir, repair_key3, reason="unjustified_semantic_drift")
        sc.mark_adopted(env.run_dir, repair_key3, adopted_block=candidate, best_effort=True)
        own_keys3 = sc.group_member_repair_keys(table, section_id3)
        assert not sc.has_resumable_group_hold(
            env.run_dir, table.table_id, section_id3, member_repair_keys=own_keys3,
        ), "ein bereits adoptierter Datensatz darf NIE erneut als resumable gemeldet werden."


# ---------------------------------------------------------------------------
# (4) Bestehende Transport-Recovery bleibt erhalten -- member-bound, ueber
#     den echten Entry-Gate-Caller.
# ---------------------------------------------------------------------------

class _RaisingGmTransportOnce:
    """Liefert fuer den ERSTEN `.turn()`-Aufruf einen Transport-Timeout
    (M7-Originalfallform) -- jeder WEITERE Aufruf (sollte es ihn geben)
    ist ein Testversagen, s. `ExplodingGmTransport`."""

    def __init__(self):
        self.calls = 0
        self.output_limit_tokens = None

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls += 1
        raise TimeoutError("timed out")


def test_j3_entry_gate_recognizes_transport_error_hold_member_bound():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j3-case4")
        section_id = "section-j3-case4"
        leader_old = _overcap_only(_LEADER_CID)
        harvested = {"leader_pk": leader_old}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["leader_pk"]
        sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=_TODAY,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=_RaisingGmTransportOnce(), cid_to_pk=_CID_TO_PK_SOLO,
            harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        record = sc.load_record(env.run_dir, repair_key)
        assert record["state"] == "hold" and record["last_reason"].startswith("transport_error:"), record

        table2 = store.Table.load(env.run_dir, table.table_id)
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver(reflection_text="Rueckblick."),
        })
        gm_stub = ExplodingGmTransport()
        outcome = _run_section(
            lobby, table2, ps_store, gm_stub, controller2, section_id, env.states_dir,
            "2026-11-20T09:30:00", max_turns=1,
        )
        assert outcome.completion.success, outcome.completion
        assert gm_stub.calls == 0, f"kein GM-Call erwartet: {gm_stub.calls}"
        record_after = sc.load_record(env.run_dir, repair_key)
        assert record_after["state"] == "adopted" and record_after.get("best_effort") is True, record_after


# ---------------------------------------------------------------------------
# (5) MISCHGRUPPE (Pflicht, J4-ROOTFIX behoben): A (adoptierbarer HOLD) + B
#     (bereits gueltig persistierter Export). Leerer Entry-Re-Entry adoptiert
#     A genau einmal UND laesst B vollstaendig unangetastet.
#
#     EHEMALIGER BLOCKER (Lauf 3, s. Integrator-Report J3): `finalize("",
#     resume_section_id=section_id)` leitet `harvested = {}` aus dem leeren
#     Text ab. `store.complete_section` listete DADURCH -- unabhaengig vom
#     tatsaechlichen Validitaetsstand -- ALLE Mitglieder als `missing`
#     (`_validate_harvest`, `store.py` ~Z.1699 `blk = harvest.get(pk); if
#     blk is None: missing.append(pk)`), weil B's vorheriger gueltiger Block
#     NIE durabel gepinnt wurde (`complete_section` pinnt `__plan.json` erst
#     NACH einer vollstaendig validen Runde ALLER Mitglieder -- bei A
#     `missing` wurde nie gepinnt, B's valider Block existierte nur im RAM
#     des ERSTEN Prozesses). `pursue_group_save_correction` behandelte B
#     DESHALB wie ein NEUES Korrekturmitglied -- ein echter, bezahlter GM-/
#     Korrektur-Call fuer ein Mitglied, dessen eigener Save NIE fehlerhaft
#     war.
#
#     J4-ROOTFIX (`store.py`, `_load_pending_valid_block`/`_store_pending_
#     valid_block`/`_clear_pending_valid_block`, additiver Seiten-Cache):
#     JEDER NICHT-`missing` Block wird, sobald die Gesamtrunde (wegen eines
#     ANDEREN Mitglieds) scheitert, durabel gecacht und beim naechsten
#     `complete_section`-Aufruf NUR fuer tatsaechlich LEERE
#     `harvested_saves[pk]`-Eintraege zurueckgespielt -- NIE ein
#     Ueberschreiben eines tatsaechlich frisch gelieferten (auch
#     ungueltigen) Blocks. Dadurch meldet `complete_section` beim leeren
#     Entry-Re-Entry JETZT korrekt NUR noch A als `missing` -- B validiert
#     erneut (dieselbe `validate_identity`-Pruefung wie immer) und wird
#     NIEMALS `pursue_group_save_correction` uebergeben: kein Kandidat, kein
#     `begin_attempt`, kein `send_correction_turn`, kein neuer `save_
#     corrections/`-Record fuer B. Dieser Test beweist das jetzt EMPIRISCH
#     (`gm_stub.calls == 0`, `guest_record_after is None`) -- GENAU die
#     Realitaet, die der ehemalige Blocker-Test widerlegt hatte.
# ---------------------------------------------------------------------------

def test_j3_mixed_group_a_hold_b_valid_export_entry_reentry_leaves_b_untouched():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-j3-case5")
        write_test_profile(env.run_dir)
        open_window(env.run_dir)
        section_id = "section-j3-case5"

        leader_old = _overcap_only(_LEADER_CID, name="Leader")
        guest_good = full_v7_save(_GUEST_CID, name="Guest")
        harvested = {"leader_pk": leader_old, "guest_pk": guest_good}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        # B (guest) ist bereits gueltig -- NUR A (leader) fehlt.
        assert not harvest_completion.success and harvest_completion.missing == ["leader_pk"], harvest_completion

        drifted = _overcap_only(_LEADER_CID, name="Leader")
        drifted["continuity"]["shared_echoes"] = [
            {"tag": f"echo-{i}-neu", "scope": "campaign", "text": f"erinnerung-{i}-neu"} for i in range(6)
        ]
        drifted["arc"]["hooks"][0]["text"] = "ausserhalb-des-korrekturauftrags-umformuliert"
        gm_drift = ScriptedGmTransport(scripted_contents=[_fenced_json(drifted)])
        harvested_out, completion_out = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=_TODAY,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm_drift, cid_to_pk=_CID_TO_PK_DUO, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert not completion_out.success, completion_out
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        leader_record = sc.load_record(env.run_dir, leader_repair_key)
        assert leader_record["state"] == "hold" and leader_record["last_reason"] == "unjustified_semantic_drift"
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        assert sc.load_record(env.run_dir, guest_repair_key) is None, (
            "B (guest) hat NIE eine Korrekturrunde durchlaufen -- es existiert "
            "bewusst KEIN save_correction-Record fuer B."
        )

        # Fresh entry (simulierter Neustart, kein Anker/Import erledigt):
        table2 = store.Table.load(env.run_dir, table.table_id)
        gm_stub = ExplodingGmTransport()
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver(reflection_text="Leader-Rueckblick."),
            "guest_pk": ReflectionOnlyDriver(reflection_text="Guest-Rueckblick."),
        })
        # `ExplodingGmTransport.turn()` wirft bei JEDEM Aufruf eine
        # `AssertionError` -- der Test lief ohne jede Exception durch, der
        # Transport wurde also fuer B (und fuer A) NICHT erreicht.
        outcome = _run_section(
            lobby, table2, ps_store, gm_stub, controller2, section_id, env.states_dir,
            "2026-11-20T09:30:00", max_turns=1,
        )
        assert outcome.completion.success, (
            f"die Entry-Recovery haette A best-effort adoptieren und die Gesamtrunde "
            f"(B unveraendert valide) abschliessen muessen: {outcome.completion}"
        )
        assert gm_stub.calls == 0, f"kein GM-/Korrektur-Call erwartet (weder fuer A noch fuer B): {gm_stub.calls}"

        guest_repair_key_check = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        guest_record_after = sc.load_record(env.run_dir, guest_repair_key_check)
        assert guest_record_after is None, (
            "B darf auch nach dem Mischgruppen-Resume KEINEN save_correction-Record bekommen "
            f"haben (reiner nie-fehlerhafter Export): {guest_record_after}"
        )
        assert store.load_current_save(env.run_dir, "guest_pk", ps_store, states_dir=env.states_dir) == guest_good, (
            "B's bereits gueltiger Save muss byteidentisch veroeffentlicht werden -- nicht verloren, "
            "nicht veraendert."
        )
        leader_record_after = sc.load_record(env.run_dir, leader_repair_key)
        assert leader_record_after["state"] == "adopted" and leader_record_after.get("best_effort") is True, (
            "A wird weiterhin korrekt genau einmal best-effort adoptiert."
        )


def _run_all() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"OK   {fn.__name__}")
            passed += 1
        except AssertionError:
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
        except Exception:
            print(f"ERROR {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} passed")
    return 0 if passed == len(fns) else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
