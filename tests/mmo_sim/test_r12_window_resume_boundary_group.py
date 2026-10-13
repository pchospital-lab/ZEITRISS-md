#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_window_resume_boundary_group.py — R12-W74: F01b auf
dem Gruppenpfad ("Gruppen-Crash",
`mmo_sim/core/save_correction.py:pursue_group_save_correction`), als
ECHTER Zweiprozess-Fall. `store.create_table_from_offer_log` ist bewusst
resume-sicher designed (laedt einen bereits persistierten OFFENEN Tisch
unter `table_id` zurueck statt ihn neu anzulegen, s. dessen Docstring) --
ein zweiter, komplett frischer Prozess kann denselben Tisch deshalb ueber
dieselbe deterministische Konstruktion GEGEN DENSELBEN `run_dir`
zurueckerhalten, exakt wie ein echter Neustart des Aufrufers.

Abdeckung (g):
  Prozess A eroeffnet Runde 1 fuer das fehlende Mitglied `guest_pk`
  (`begin_attempt`, `_open_round`-Marker persistiert), der Versand schlaegt
  TRANSPORTSEITIG fehl (`finish_error` -> `state=accounted`, `error`
  gesetzt) -- GENAU DANACH, aber VOR `mark_hold`/`_clear_open_round`,
  crasht der Prozess (injizierter `SystemExit`). Der `_open_round`-Marker
  UND der korrekturdatensatz des Mitglieds bleiben dadurch unveraendert
  liegen. Prozess B (komplett frisch) ruft erneut auf: der bereits
  `accounted`e Requestdatensatz MIT `error` fuer GENAU diese
  Rundenidentitaet (`table_id`/`section_id`/`ROLE_GROUP`/`turn_idx=
  round_no`/`participant=table.leader`) ist fuer `find_durable_result`/
  `find_answered_without_text` BEIDE unsichtbar und faellt NIE in
  `open_requests` -- OHNE die F01b-Erweiterung wuerde das Resume dies als
  "nie versandt" werten und einen ZWEITEN POST fuer dieselbe Runde
  ausloesen. Die Runde MUSS stattdessen terminal werden: KEIN zweiter
  Transport-Call, GENAU EIN Ledger-Datensatz fuer diese Rundenidentitaet,
  der Korrekturdatensatz des Mitglieds endet `state="hold"`, der
  `_open_round`-Marker wird geloescht.

Pure Python, nur `assert`, echter Prozess-Exitcode."""
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

from _r12_window_resume_boundary_fixture import last_json, run_phase  # noqa: E402

_COMMON_SETUP = """
import json
from pathlib import Path
from _full_v7_fixture import full_v7_save
from mmo_sim.core import save_correction as sc, request_ledger as ledger, store
from mmo_sim.core.admission import write_test_profile
from mmo_sim.core.persona_state import PersonaStateStore
from mmo_sim.domain.zeitriss import save_correction as domain
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy

run_dir = Path({run_dir!r})
states_dir = Path({states_dir!r})
write_test_profile(run_dir)
ROLE_GROUP = domain.ROLE_GROUP
_CID_TO_PK = {{"chrono-leader": "leader_pk", "chrono-guest": "guest_pk"}}
_SCHEMA = (
    '{{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{{"v":{{"const":2}}}}}}'
)

def _wallet_as_number(char_id, name="Flo"):
    block = full_v7_save(char_id, name=name)
    block["economy"] = {{"wallets": {{char_id: 500}}}}
    return block

def _seed(ps_store, pk, char_id):
    ps_store.save_state(pk, {{
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {{"character_id": char_id, "name": "Test"}},
    }}, states_dir=states_dir)

def build_table():
    states_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir.parent / "schema.json"
    if not schema_path.exists():
        schema_path.write_text(_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    _seed(ps_store, "leader_pk", "chrono-leader")
    _seed(ps_store, "guest_pk", "chrono-guest")
    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, "t-r12-window-resume-boundary-group",
        offer_log_events=[
            {{"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]}},
            {{"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True}},
        ],
        chrononaut_ids={{"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"}},
    )
    assert table is not None, derivation
    return lobby, table, ps_store

lobby, table, ps_store = build_table()
guest_invalid = _wallet_as_number("chrono-guest")
leader_valid = full_v7_save("chrono-leader", name="Leader")
harvested = {{"leader_pk": leader_valid, "guest_pk": guest_invalid}}
harvest_completion = store.complete_section(
    lobby, table, "section-g", harvested, states_dir, "2026-10-10",
    ZeitrissHarvestValidator(), ps_store,
)
group_repair_key = domain.group_repair_key(table.table_id, "section-g", "chrono-guest")
"""


def test_g_group_accounted_error_member_stays_terminal_no_second_post():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        base = _COMMON_SETUP.format(run_dir=str(run_dir), states_dir=str(states_dir))

        phase1 = base + """
assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

class Gm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        raise TimeoutError("SYNTHETIC_GROUP_TRANSPORT_FAILURE")

def _crash(*a, **kw):
    raise SystemExit(73)
sc.mark_hold = _crash

g = Gm()
try:
    sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id="section-g", harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=g, cid_to_pk=_CID_TO_PK, harvest_extractor=None,
    )
    raise AssertionError("crash point not reached")
except SystemExit as exc:
    assert exc.code == 73

open_round_path = sc._open_round_path(run_dir, table.table_id, "section-g")
member_record = sc.load_record(run_dir, group_repair_key)
group_records = [r for r in ledger._all_records(run_dir) if r.get("role") == ROLE_GROUP]
print(json.dumps({
    "phase": 1, "calls": g.calls, "open_round_marker_present": open_round_path.exists(),
    "member_state": member_record["state"], "group_record_count": len(group_records),
    "group_record_states": [(r["state"], r["error"]) for r in group_records],
}))
"""
        proc1 = run_phase(phase1)
        assert proc1.returncode == 0, f"Phase 1 (Gruppen-Crash-Setup) failed: {proc1.stderr}"
        j1 = last_json(proc1)
        assert j1["calls"] == [1], j1
        assert j1["open_round_marker_present"] is True, (
            f"der Marker darf vom injizierten Crash NICHT erreicht/geloescht worden sein -- {j1}"
        )
        assert j1["member_state"] == "correction_pending", j1
        assert j1["group_record_count"] == 1, j1
        assert j1["group_record_states"] == [["accounted", "SYNTHETIC_GROUP_TRANSPORT_FAILURE"]], j1

        phase2 = base + """
class ExplodingGm:
    def __init__(self):
        self.calls = []
    def turn(self, turn_idx, text, **kw):
        self.calls.append(turn_idx)
        raise AssertionError("kein zweiter Transport-Call erwartet -- die Runde ist terminal.")

before = len([r for r in ledger._all_records(run_dir) if r.get("role") == ROLE_GROUP])
g = ExplodingGm()
harvested_after, completion_after = sc.pursue_group_save_correction(
    lobby=lobby, table=table, section_id="section-g", harvested=dict(harvested),
    harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
    harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
    gm_transport=g, cid_to_pk=_CID_TO_PK, harvest_extractor=None,
)
after = len([r for r in ledger._all_records(run_dir) if r.get("role") == ROLE_GROUP])
open_round_path = sc._open_round_path(run_dir, table.table_id, "section-g")
member_record = sc.load_record(run_dir, group_repair_key)
print(json.dumps({
    "phase": 2, "calls": g.calls, "completion_success": completion_after.success,
    "completion_missing": completion_after.missing,
    "before_group_records": before, "after_group_records": after,
    "member_state": member_record["state"], "member_reason": member_record["last_reason"],
    "open_round_marker_present": open_round_path.exists(),
}))
"""
        proc2 = run_phase(phase2)
        assert proc2.returncode == 0, f"Phase 2 (Resume) failed: {proc2.stderr}"
        j2 = last_json(proc2)
        assert j2["calls"] == [], f"F01b Gruppenpfad: KEIN zweiter POST fuer dieselbe Runde -- {j2}"
        assert j2["before_group_records"] == 1 and j2["after_group_records"] == 1, (
            f"weiterhin GENAU EIN Ledger-Datensatz fuer diese Rundenidentitaet -- {j2}"
        )
        assert not j2["completion_success"] and j2["completion_missing"] == ["guest_pk"], j2
        assert j2["member_state"] == "hold", f"Mitglied muss terminal werden -- {j2}"
        assert j2["open_round_marker_present"] is False, (
            f"der Marker muss nach der terminalen Entscheidung geloescht werden -- {j2}"
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
