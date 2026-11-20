#!/usr/bin/env python3
"""
tests/mmo_sim/test_j4_mixedgroup_rootfix_siblings_20261120.py — ZR-R8-
LIVESYNC-PALIMPSEST-20261119-R1, Stage J, Lauf 4 (Mischgruppen-
Korrektheitsfehler an der Wurzel behoben, 20261120).

Briefing-Pflicht ("Geschwister-Fehler aktiv suchen"): deckt die Wurzel
(`store.py` `_validate_harvest`/`complete_section`, leerer Entry-Re-Entry-
Harvest listet unbepinnte, aber bereits gueltige Mitglieder faelschlich als
`missing`) in JEDER Konstellation ab, nicht nur im Zweier-Fall aus Lauf 3:

1. 3er-Tisch: A=HOLD (Drift), B+C je gueltig -- weder B noch C duerfen
   bezahlt nachgefordert werden.
2. Transport-Error-HOLD bei A + gueltiges B (Zweier-Tisch) -- derselbe
   Resume-Pfad wie der Drift-Fall aus Lauf 3, hier mit der ANDEREN
   bestehenden Resume-Bruecke (`resume_hold_via_transport_error_best_
   effort`).
3. Zwei HOLD-Mitglieder (A, B) + ein gueltiges Mitglied (C) -- BEIDE HOLDs
   adoptieren best-effort, C bleibt unangetastet.
4. Solo-HOLD (der belegte Live-M8-Fall) bleibt weiterhin modellfrei
   adoptierbar -- der J4-Cache-Mechanismus (`store.py` `_pending_valid_
   cache`) darf den bereits in Lauf 3 verifizierten Solo-Pfad NICHT
   veraendern (fuer einen Solo-Tisch gibt es per Konstruktion NIE ein
   zweites, nicht-missing Mitglied -- der Cache bleibt in diesem Fall
   immer leer, s. Test 4 unten).

Treibt in JEDEM Fall den ECHTEN Caller (`core.app_service.run_play_session`
-> `core.runtime.SectionRuntime.run_full_section`). `ExplodingGmTransport`
raist bei JEDEM unerwarteten `.turn()`-Aufruf -- jeder unerwartete
Transport-Aufruf ist ein sofortiger Testfehlschlag. Geldfrei per
Konstruktion: ausschliesslich In-Process-Fakes."""
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
from test_j3_entry_recovery_20261120 import (  # noqa: E402
    _CID_TO_PK_DUO, _TODAY, _fenced_json, _overcap_only, _run_section,
)

import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    ZeitrissHarvestValidator, ZeitrissTableSizePolicy,
)

_LEADER_CID = "chrono-leader"
_GUEST_CID = "chrono-guest"
_THIRD_CID = "chrono-third"


def _build_three_member_table(env, table_id: str):
    """3er-Tisch (Leader + 2 Gaeste) -- analog zu `_section_completion_
    resume_fixtures.build_two_member_table`, hier zusaetzlich additiv fuer
    den Briefing-Pflichtfall '3er-Tisch'. Rein Testcode, kein Produkt-
    import."""
    schema_path = env.run_dir.parent / "schema.json"
    ps_store = make_ps_store(schema_path)
    seed_persona_state(ps_store, env.states_dir, "leader_pk", _LEADER_CID)
    seed_persona_state(ps_store, env.states_dir, "guest_pk", _GUEST_CID)
    seed_persona_state(ps_store, env.states_dir, "third_pk", _THIRD_CID)

    lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    lobby.join("third_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk", "third_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
            {"type": "consent", "offer_id": "o1", "from": "third_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": _LEADER_CID, "guest_pk": _GUEST_CID, "third_pk": _THIRD_CID},
    )
    assert table is not None, f"3er-Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


_CID_TO_PK_TRIO = {_LEADER_CID: "leader_pk", _GUEST_CID: "guest_pk", _THIRD_CID: "third_pk"}


# ---------------------------------------------------------------------------
# (1) 3er-Tisch: A=HOLD (Drift), B+C je gueltig.
# ---------------------------------------------------------------------------

def test_j4_trio_a_hold_b_and_c_valid_entry_reentry_leaves_b_and_c_untouched():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = _build_three_member_table(env, table_id="t-j4-trio1")
        write_test_profile(env.run_dir)
        open_window(env.run_dir)
        section_id = "section-j4-trio1"

        leader_old = _overcap_only(_LEADER_CID, name="Leader")
        guest_good = full_v7_save(_GUEST_CID, name="Guest")
        third_good = full_v7_save(_THIRD_CID, name="Third")
        harvested = {"leader_pk": leader_old, "guest_pk": guest_good, "third_pk": third_good}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["leader_pk"], harvest_completion

        drifted = _overcap_only(_LEADER_CID, name="Leader")
        drifted["continuity"]["shared_echoes"] = [
            {"tag": f"echo-{i}-neu", "scope": "campaign", "text": f"erinnerung-{i}-neu"} for i in range(6)
        ]
        drifted["arc"]["hooks"][0]["text"] = "ausserhalb-des-korrekturauftrags-umformuliert"
        gm_drift = ScriptedGmTransport(scripted_contents=[_fenced_json(drifted)])
        _harvested_out, completion_out = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=_TODAY,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm_drift, cid_to_pk=_CID_TO_PK_TRIO, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert not completion_out.success, completion_out
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        leader_record = sc.load_record(env.run_dir, leader_repair_key)
        assert leader_record["state"] == "hold" and leader_record["last_reason"] == "unjustified_semantic_drift"
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        third_repair_key = domain.group_repair_key(table.table_id, section_id, _THIRD_CID)
        assert sc.load_record(env.run_dir, guest_repair_key) is None
        assert sc.load_record(env.run_dir, third_repair_key) is None

        table2 = store.Table.load(env.run_dir, table.table_id)
        gm_stub = ExplodingGmTransport()
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver(reflection_text="Leader-Rueckblick."),
            "guest_pk": ReflectionOnlyDriver(reflection_text="Guest-Rueckblick."),
            "third_pk": ReflectionOnlyDriver(reflection_text="Third-Rueckblick."),
        })
        outcome = app_service_run_play_session_trio(
            lobby, table2, ps_store, gm_stub, controller2, section_id, env.states_dir,
        )
        assert outcome.completion.success, outcome.completion
        assert gm_stub.calls == 0, f"kein GM-/Korrektur-Call erwartet (A/B/C): {gm_stub.calls}"

        assert sc.load_record(env.run_dir, guest_repair_key) is None, (
            "B darf auch nach dem Trio-Resume KEINEN save_correction-Record bekommen haben."
        )
        assert sc.load_record(env.run_dir, third_repair_key) is None, (
            "C darf auch nach dem Trio-Resume KEINEN save_correction-Record bekommen haben."
        )
        assert store.load_current_save(env.run_dir, "guest_pk", ps_store, states_dir=env.states_dir) == guest_good
        assert store.load_current_save(env.run_dir, "third_pk", ps_store, states_dir=env.states_dir) == third_good
        leader_record_after = sc.load_record(env.run_dir, leader_repair_key)
        assert leader_record_after["state"] == "adopted" and leader_record_after.get("best_effort") is True


def app_service_run_play_session_trio(lobby, table, ps_store, gm, controller, section_id, states_dir, max_turns=1):
    from mmo_sim.core import app_service
    from mmo_sim.domain.zeitriss.policy import (
        COMPLETION_MARKER, build_save_command_completion_fallback, is_save_command, is_saveguard_rejection,
    )
    return app_service.run_play_session(
        lobby, table, gm, controller, section_id,
        {
            "leader_pk": {"user": "ctx-leader_pk"},
            "guest_pk": {"user": "ctx-guest_pk"},
            "third_pk": {"user": "ctx-third_pk"},
        },
        states_dir, _TODAY, "2026-11-20T09:30:00", COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, max_turns=max_turns,
        completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
        explicit_completion_attempt=is_save_command,
        save_guard_rejection_detector=is_saveguard_rejection,
    )


# ---------------------------------------------------------------------------
# (2) Transport-Error-HOLD bei A + gueltiges B (Zweier-Tisch).
# ---------------------------------------------------------------------------

class _RaisingGmTransportOnce:
    def __init__(self):
        self.calls = 0
        self.output_limit_tokens = None

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls += 1
        raise TimeoutError("timed out")


def test_j4_duo_a_transport_error_hold_b_valid_entry_reentry_leaves_b_untouched():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-j4-duo-transport")
        write_test_profile(env.run_dir)
        open_window(env.run_dir)
        section_id = "section-j4-duo-transport"

        leader_old = _overcap_only(_LEADER_CID, name="Leader")
        guest_good = full_v7_save(_GUEST_CID, name="Guest")
        harvested = {"leader_pk": leader_old, "guest_pk": guest_good}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["leader_pk"], harvest_completion

        sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=_TODAY,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=_RaisingGmTransportOnce(), cid_to_pk=_CID_TO_PK_DUO,
            harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        leader_record = sc.load_record(env.run_dir, leader_repair_key)
        assert leader_record["state"] == "hold" and leader_record["last_reason"].startswith("transport_error:")
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        assert sc.load_record(env.run_dir, guest_repair_key) is None

        table2 = store.Table.load(env.run_dir, table.table_id)
        gm_stub = ExplodingGmTransport()
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver(reflection_text="Leader-Rueckblick."),
            "guest_pk": ReflectionOnlyDriver(reflection_text="Guest-Rueckblick."),
        })
        outcome = _run_section(
            lobby, table2, ps_store, gm_stub, controller2, section_id, env.states_dir,
            "2026-11-20T09:30:00", max_turns=1,
        )
        assert outcome.completion.success, outcome.completion
        assert gm_stub.calls == 0, f"kein GM-/Korrektur-Call erwartet (A/B): {gm_stub.calls}"
        assert sc.load_record(env.run_dir, guest_repair_key) is None, (
            "B darf auch nach dem Transport-Error-Resume KEINEN save_correction-Record bekommen haben."
        )
        assert store.load_current_save(env.run_dir, "guest_pk", ps_store, states_dir=env.states_dir) == guest_good
        leader_record_after = sc.load_record(env.run_dir, leader_repair_key)
        assert leader_record_after["state"] == "adopted" and leader_record_after.get("best_effort") is True


# ---------------------------------------------------------------------------
# (3) Zwei HOLD-Mitglieder (A, B) + ein gueltiges Mitglied (C).
# ---------------------------------------------------------------------------

def test_j4_trio_a_and_b_hold_c_valid_entry_reentry_adopts_both_holds_leaves_c_untouched():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = _build_three_member_table(env, table_id="t-j4-trio2")
        write_test_profile(env.run_dir)
        open_window(env.run_dir)
        section_id = "section-j4-trio2"

        leader_old = _overcap_only(_LEADER_CID, name="Leader")
        guest_old = _overcap_only(_GUEST_CID, name="Guest")
        third_good = full_v7_save(_THIRD_CID, name="Third")
        harvested = {"leader_pk": leader_old, "guest_pk": guest_old, "third_pk": third_good}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and sorted(harvest_completion.missing) == ["guest_pk", "leader_pk"], (
            harvest_completion
        )

        drifted_leader = _overcap_only(_LEADER_CID, name="Leader")
        drifted_leader["continuity"]["shared_echoes"] = [
            {"tag": f"echo-{i}-neu", "scope": "campaign", "text": f"erinnerung-{i}-neu"} for i in range(6)
        ]
        drifted_leader["arc"]["hooks"][0]["text"] = "ausserhalb-des-korrekturauftrags-umformuliert-leader"
        drifted_guest = _overcap_only(_GUEST_CID, name="Guest")
        drifted_guest["continuity"]["shared_echoes"] = [
            {"tag": f"echo-{i}-neu", "scope": "campaign", "text": f"erinnerung-{i}-neu"} for i in range(6)
        ]
        drifted_guest["arc"]["hooks"][0]["text"] = "ausserhalb-des-korrekturauftrags-umformuliert-guest"
        gm_drift = ScriptedGmTransport(scripted_contents=[_fenced_json(drifted_leader), _fenced_json(drifted_guest)])
        _harvested_out, completion_out = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=_TODAY,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm_drift, cid_to_pk=_CID_TO_PK_TRIO, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert not completion_out.success, completion_out
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        third_repair_key = domain.group_repair_key(table.table_id, section_id, _THIRD_CID)
        leader_record = sc.load_record(env.run_dir, leader_repair_key)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert leader_record["state"] == "hold" and leader_record["last_reason"] == "unjustified_semantic_drift"
        assert guest_record["state"] == "hold" and guest_record["last_reason"] == "unjustified_semantic_drift"
        assert sc.load_record(env.run_dir, third_repair_key) is None

        table2 = store.Table.load(env.run_dir, table.table_id)
        gm_stub = ExplodingGmTransport()
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver(reflection_text="Leader-Rueckblick."),
            "guest_pk": ReflectionOnlyDriver(reflection_text="Guest-Rueckblick."),
            "third_pk": ReflectionOnlyDriver(reflection_text="Third-Rueckblick."),
        })
        outcome = app_service_run_play_session_trio(
            lobby, table2, ps_store, gm_stub, controller2, section_id, env.states_dir,
        )
        assert outcome.completion.success, outcome.completion
        assert gm_stub.calls == 0, f"kein GM-/Korrektur-Call erwartet (A/B/C): {gm_stub.calls}"

        assert sc.load_record(env.run_dir, third_repair_key) is None, (
            "C darf auch nach dem Trio-Resume mit ZWEI HOLDs KEINEN save_correction-Record bekommen haben."
        )
        assert store.load_current_save(env.run_dir, "third_pk", ps_store, states_dir=env.states_dir) == third_good
        leader_record_after = sc.load_record(env.run_dir, leader_repair_key)
        guest_record_after = sc.load_record(env.run_dir, guest_repair_key)
        assert leader_record_after["state"] == "adopted" and leader_record_after.get("best_effort") is True
        assert guest_record_after["state"] == "adopted" and guest_record_after.get("best_effort") is True


# ---------------------------------------------------------------------------
# (4) Solo-HOLD (Live-M8-Fall) bleibt modellfrei adoptierbar -- der J4-Cache
#     bleibt fuer einen Solo-Tisch strukturell immer leer (kein zweites
#     Mitglied, das je `missing` UND `nicht-missing` gleichzeitig sein
#     koennte).
# ---------------------------------------------------------------------------

def test_j4_solo_hold_entry_reentry_stays_model_free_cache_stays_empty():
    with tempfile.TemporaryDirectory() as td:
        from test_j3_entry_recovery_20261120 import _build_solo_table, _drive_leader_into_entry_hold_drift

        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j4-solo")
        section_id = "section-j4-solo"
        leader_old, repair_key = _drive_leader_into_entry_hold_drift(env, lobby, table, ps_store, section_id)

        cache_dir = env.run_dir / "save_corrections" / "_pending_valid_cache"
        assert not cache_dir.exists() or list(cache_dir.glob("*.json")) == [], (
            "ein Solo-Tisch hat strukturell nie ein zweites, nicht-missing Mitglied -- "
            f"der J4-Cache muss leer bleiben: {list(cache_dir.glob('*.json')) if cache_dir.exists() else []}"
        )

        table2 = store.Table.load(env.run_dir, table.table_id)
        gm_stub = ExplodingGmTransport()
        reflection_driver = ReflectionOnlyDriver(reflection_text="Kurzer Rueckblick.")
        controller2 = TableController(leader_key="leader_pk", drivers={"leader_pk": reflection_driver})
        outcome = _run_section(
            lobby, table2, ps_store, gm_stub, controller2, section_id, env.states_dir, "2026-11-20T09:30:00",
            max_turns=1,
        )
        assert outcome.completion.success, outcome.completion
        assert gm_stub.calls == 0, f"kein GM-/Korrektur-Call erwartet: {gm_stub.calls}"
        record_after = sc.load_record(env.run_dir, repair_key)
        assert record_after["state"] == "adopted" and record_after.get("best_effort") is True, record_after
        assert record_after["adopted_block"] == leader_old
        assert not cache_dir.exists() or list(cache_dir.glob("*.json")) == [], (
            "der J4-Cache bleibt ueber den gesamten Solo-Lauf hinweg leer."
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
