#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_window_hold_group.py — R12-W73: D-HOLD Pre-Send-
Window-Resume, Gruppenpfad
(`mmo_sim/core/save_correction.py:pursue_group_save_correction`).

Abdeckung (W73-BRIEF.md Invariante 6, PFLICHT-ABLAUF Punkt 3(f)):
  (f) ein Deadline-Pre-Send-Block WAEHREND einer Gruppenrunde erhaelt den
      `_open_round`-Marker (Rundenidentitaet `round_no` + Mitgliederset)
      -- NICHT `_clear_open_round`, NICHT terminal `mark_hold`. Der
      naechste Aufruf (Fenster wieder offen) nimmt DENSELBEN `round_no`
      und dasselbe Mitgliederset wieder auf, OHNE `begin_attempt` ein
      zweites Mal aufzurufen (kein Doppelzaehlen) -- genau EIN
      Ledger-Datensatz fuer die gesamte Runde.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie
`test_w53_save_correction_adopted_replay_2026_10_08.py`."""
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
from _r12_window_hold_fixture import close_window, deadline_reason, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

ROLE_GROUP = save_correction_domain.ROLE_GROUP
_CID_TO_PK = {"chrono-leader": "leader_pk", "chrono-guest": "guest_pk"}
_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _wallet_as_number(char_id: str, name: str = "Flo") -> dict:
    block = full_v7_save(char_id, name=name)
    block["economy"] = {"wallets": {char_id: 500}}
    return block


def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _build_two_member_table(run_dir: Path, states_dir: Path) -> tuple:
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
        lobby, "t-r12-window-hold",
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


class _ExplodingGm:
    def turn(self, *a, **k):
        raise AssertionError("f: kein Transport-Call erwartet -- die Runde muss admission-blockiert bleiben.")


class _CountingGm:
    def __init__(self, contents):
        self._contents = list(contents)
        self.calls = []

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(f"unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _ledger_group_records(run_dir: Path) -> list[dict]:
    return [r for r in request_ledger._all_records(run_dir) if r.get("role") == ROLE_GROUP]


def test_f_group_deadline_pause_preserves_round_marker_and_resumes_without_double_count():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        guest_invalid = _wallet_as_number("chrono-guest")
        leader_valid = full_v7_save("chrono-leader", name="Leader")
        harvested = {"leader_pk": leader_valid, "guest_pk": guest_invalid}

        reason = close_window(run_dir, deadline=1.0)
        harvest_completion = store.complete_section(
            lobby, table, "section-f", harvested, states_dir, "2026-10-08", ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

        group_repair_key = save_correction_domain.group_repair_key(table.table_id, "section-f", "chrono-guest")

        # --- (1) Deadline-vor-Versand-Block WAEHREND der Gruppenrunde: der
        # `_open_round`-Marker UND der Mitglieds-Korrekturdatensatz muessen
        # ERHALTEN bleiben (NICHT terminal `mark_hold`, NICHT `_clear_open_
        # round`).
        harvested_blocked, completion_blocked = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-f", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=_ExplodingGm(), cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert not completion_blocked.success and completion_blocked.missing == ["guest_pk"], completion_blocked

        open_round_path = save_correction._open_round_path(run_dir, table.table_id, "section-f")
        assert open_round_path.exists(), "Invariante 6: der _open_round-Marker muss bei einem Deadline-Block ERHALTEN bleiben."
        open_round = json.loads(open_round_path.read_text(encoding="utf-8"))
        assert open_round["round"] == 1
        assert open_round["members"] == [
            {"persona_key": "guest_pk", "char_id": "chrono-guest", "original_block": guest_invalid},
        ], open_round

        member_record = save_correction.load_record(run_dir, group_repair_key)
        assert member_record["state"] == "window_paused", member_record
        assert member_record["attempts_used"] == 1 and member_record["last_reason"] == reason
        assert member_record["last_request_id"] is None

        ledger_blocked = _ledger_group_records(run_dir)
        assert ledger_blocked == [], f"0 neue Requestdatensaetze bei einem Deadline-vor-Versand-Block -- {ledger_blocked}"

        # --- (2) Fenster wieder offen: derselbe round_no + dasselbe
        # Mitgliederset werden regulaer fortgesetzt, OHNE erneutes
        # begin_attempt (kein Doppelzaehlen), genau EIN Ledger-Datensatz
        # fuer die gesamte Runde.
        open_window(run_dir)
        guest_valid = full_v7_save("chrono-guest", name="Flo")
        gm = _CountingGm([f"```json\n{json.dumps(guest_valid)}\n```"])
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-f", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_after.success, f"Resume MUSS die Section abschliessen -- {completion_after}"
        assert harvested_after["guest_pk"] == guest_valid

        assert len(gm.calls) == 1, f"genau EIN Transport-Call fuer die fortgesetzte Runde -- {gm.calls}"
        assert gm.calls[0][0] == 1, f"turn_idx muss derselbe round_no (1) bleiben -- {gm.calls}"

        member_after = save_correction.load_record(run_dir, group_repair_key)
        assert member_after["attempts_used"] == 1, (
            f"KEIN Doppelzaehlen -- attempts_used bleibt bei 1, tatsaechlich {member_after['attempts_used']}"
        )
        assert member_after["state"] == "adopted"

        assert not open_round_path.exists(), "Marker wird NACH vollstaendiger Verarbeitung der Runde geloescht."

        ledger_after = _ledger_group_records(run_dir)
        assert len(ledger_after) == 1, f"genau EIN Ledger-Datensatz fuer die GESAMTE Runde -- {ledger_after}"
        assert ledger_after[0]["turn_idx"] == 1 and ledger_after[0]["participant"] == table.leader


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
