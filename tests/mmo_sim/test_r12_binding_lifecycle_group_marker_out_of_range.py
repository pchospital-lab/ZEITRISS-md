#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_binding_lifecycle_group_marker_out_of_range.py —
R12-W77: F02-MARKER-Fix, 01_BINDUNGSERHALT.md §B, CASES.json
L06-GROUP-CONTROL ("corrupt bool/4/identity").

`test_r12_origin_finish_group_shape.py::test_neg_*` (W77-korrigiert) deckt
den `bool`-Fall ab. Diese Suite deckt zusaetzlich den `4` (ausserhalb des
gueltigen offenen Slotbereichs `1..max_attempts`, aber ein ECHTER `int`,
kein Typproblem) -- denselben konkreten Wert, den GENERALREVIEW.md §4
("Meine Probe ... bestaetigt ... True bzw. 4 als unzulaessige Versuche")
und `01_BINDUNGSERHALT.md §B` ausdruecklich nennen -- UND dieselbe
PRE==POST-Byte-/Modus-Erhaltung wie der dort korrigierte Fall.

Pure Python, nur `assert`, echter Exitcode -- gleiches Aufbaumuster wie
`test_r12_origin_finish_group_shape.py`."""
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
from _r12_window_hold_fixture import close_window, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

_CID_TO_PK = {"chrono-leader": "leader_pk", "chrono-guest": "guest_pk"}
_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _wallet_as_number(char_id: str, name: str = "Flo") -> dict:
    block = full_v7_save(char_id, name=name)
    block["economy"] = {"wallets": {char_id: 500}}
    return block


def _seed_persona_state(ps_store, states_dir, pk, char_id):
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _build_two_member_table(run_dir, states_dir):
    states_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir.parent / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed_persona_state(ps_store, states_dir, "leader_pk", "chrono-leader")
    _seed_persona_state(ps_store, states_dir, "guest_pk", "chrono-guest")

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, "t-r77-marker-oor",
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


class _ExplodingGm:
    def __init__(self):
        self.calls = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        raise AssertionError("kein Transport-Call erwartet -- SHAPE-Verletzung muss VOR jedem Versand HOLD halten.")


def test_out_of_range_int_four_member_attempts_holds_whole_round_byte_identical():
    section_id = "section-marker-oor"
    root = Path(tempfile.mkdtemp())
    try:
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        leader_invalid = _wallet_as_number("chrono-leader")
        guest_invalid = _wallet_as_number("chrono-guest")
        harvested = {"leader_pk": leader_invalid, "guest_pk": guest_invalid}

        close_window(run_dir, deadline=1.0)
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, states_dir, "2026-10-10", ZeitrissHarvestValidator(), ps_store,
        )
        gm0 = _ExplodingGm()
        harvested, harvest_completion = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm0, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        open_round_path = save_correction._open_round_path(run_dir, table.table_id, section_id)
        assert open_round_path.exists(), "Marker muss bei Deadline-Block erhalten bleiben."

        # EIN Mitglied auf `4` korrumpieren -- ein ECHTER `int`, aber
        # ausserhalb des gueltigen offenen Slotbereichs `1..max_attempts`
        # (hier max_attempts=3) -- GENAU der in GENERALREVIEW.md §4 genannte
        # konkrete Wert, NICHT der bereits andernorts getestete `bool`-Fall.
        guest_repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-guest")
        tampered = dict(save_correction.load_record(run_dir, guest_repair_key))
        tampered["attempts_used"] = 4
        save_correction._write_record(run_dir, guest_repair_key, tampered)

        leader_repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-leader")
        pre_open_round_bytes = open_round_path.read_bytes()
        pre_guest_bytes = save_correction._record_path(run_dir, guest_repair_key).read_bytes()
        pre_leader_bytes = save_correction._record_path(run_dir, leader_repair_key).read_bytes()
        pre_ledger_records = request_ledger._all_records(run_dir)

        open_window(run_dir)
        gm = _ExplodingGm()
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert gm.calls == [], f"KEIN Transport-Call bei attempts_used=4 (ausserhalb 1..3) -- {gm.calls}"
        assert not completion_after.success and set(completion_after.missing) == {"leader_pk", "guest_pk"}
        assert open_round_path.exists(), "R12-W77: Marker MUSS erhalten bleiben (kein _clear_open_round)."
        assert open_round_path.read_bytes() == pre_open_round_bytes, "Marker-Bytes unveraendert."
        assert save_correction._record_path(run_dir, guest_repair_key).read_bytes() == pre_guest_bytes, (
            "korrumpiertes Member-Record (chrono-guest) muss byte-identisch bleiben."
        )
        assert save_correction._record_path(run_dir, leader_repair_key).read_bytes() == pre_leader_bytes, (
            "unveraendertes Member-Record (chrono-leader) muss byte-identisch bleiben."
        )
        assert request_ledger._all_records(run_dir) == pre_ledger_records, "Requesthistorie unveraendert."

        guest_record = save_correction.load_record(run_dir, guest_repair_key)
        assert guest_record["attempts_used"] == 4, "der korrupte Wert wird NICHT manuell repariert."
        assert guest_record["last_reason"] != "invalid_resume_slot_shape", (
            f"kein Member-Write durch die Ablehnung -- {guest_record}"
        )
    finally:
        import shutil
        shutil.rmtree(root, ignore_errors=True)


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
