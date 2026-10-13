#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_provenance_close_group_identity.py — R12-W75:
F02-SHAPE Gruppenpfad, `_open_round`-Marker UND Memberrecords GEMEINSAM auf
die aktuelle Gruppenidentitaet pruefen
(`mmo_sim/core/save_correction.py:pursue_group_save_correction`).

Abdeckung (W75-BRIEF.md PFLICHT-ABLAUF Punkt 3(f)):
  `_open_round_path(run_dir, table_id, section_id)` findet den Marker allein
  ueber die Dateiposition (`safe = f"{table_id}__{section_id}".replace("/",
  "_")`) -- das beweist NICHT, dass der INHALT (Marker selbst ODER ein
  einzelnes Mitglieds-Korrekturdatensatz) zur aktuellen Gruppenidentitaet
  passt. Ein Widerspruch in GENAU EINEM der beiden (Marker ODER
  Memberrecord) muss trotzdem zu kontrolliertem HOLD fuehren -- Marker,
  Mitgliederset UND `round_no` bleiben BYTEGLEICH ERHALTEN (kein
  `_clear_open_round`, kein Member-Write, keine neue Runde wird erfunden).

Pure Python, nur `assert`, echter Exitcode -- gleiches Aufbaumuster wie
`test_r12_window_hold_group.py`."""
from __future__ import annotations

import json
import shutil
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
        lobby, "t-r12-provenance-close",
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
        raise AssertionError("kein Transport-Call erwartet -- Marker/Memberrecord-Identitaetsmismatch.")


def _open_pending_round(section_id: str):
    """Baut einen Tisch, oeffnet (via echtem Deadline-Pre-Send-Block, exakt
    wie `test_r12_window_hold_group.py`) eine Runde fuer das fehlende
    Mitglied `guest_pk` und liefert `(run_dir, lobby, table, ps_store,
    states_dir, harvested, harvest_completion)` fuer den naechsten Aufruf."""
    root = Path(tempfile.mkdtemp())
    run_dir, states_dir = root / "run", root / "states"
    lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

    guest_invalid = _wallet_as_number("chrono-guest")
    leader_valid = full_v7_save("chrono-leader", name="Leader")
    harvested = {"leader_pk": leader_valid, "guest_pk": guest_invalid}

    close_window(run_dir, deadline=1.0)
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, states_dir, "2026-10-10", ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

    harvested_blocked, completion_blocked = save_correction.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=_ExplodingGm(), cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    assert not completion_blocked.success and completion_blocked.missing == ["guest_pk"], completion_blocked
    open_round_path = save_correction._open_round_path(run_dir, table.table_id, section_id)
    assert open_round_path.exists(), "Invariante 6: der Marker muss bei einem Deadline-Block ERHALTEN bleiben."
    return root, run_dir, lobby, table, ps_store, states_dir, harvested, harvest_completion, open_round_path


def _resume_and_expect_identity_mismatch_hold(
    run_dir, lobby, table, ps_store, states_dir, harvested, harvest_completion, section_id, open_round_path,
):
    open_window(run_dir)
    marker_before = open_round_path.read_text(encoding="utf-8")
    group_repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-guest")
    member_before = save_correction.load_record(run_dir, group_repair_key)
    ledger_before = len(request_ledger._all_records(run_dir))

    harvested_after, completion_after = save_correction.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-10",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=_ExplodingGm(), cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    assert not completion_after.success and completion_after.missing == ["guest_pk"], completion_after
    assert open_round_path.exists(), "Marker MUSS bei einem Identitaetsmismatch ERHALTEN bleiben."
    assert open_round_path.read_text(encoding="utf-8") == marker_before, "Marker muss BYTEGLEICH bleiben."
    member_after = save_correction.load_record(run_dir, group_repair_key)
    assert member_after == member_before, (
        f"Memberrecord darf bei einem Identitaetsmismatch NICHT geschrieben werden -- "
        f"before={member_before} after={member_after}"
    )
    assert len(request_ledger._all_records(run_dir)) == ledger_before, "0 neue Requestdatensaetze."


# ---------------------------------------------------------------------------
# fremder Abschnitt IM MARKER (Dateiposition passt zufaellig/unveraendert,
# der gespeicherte Markerinhalt selbst traegt eine ANDERE section_id).
# ---------------------------------------------------------------------------

def test_foreign_section_in_marker_content_holds_marker_preserved():
    section_id = "section-g1"
    root, run_dir, lobby, table, ps_store, states_dir, harvested, harvest_completion, open_round_path = (
        _open_pending_round(section_id)
    )
    try:
        marker = json.loads(open_round_path.read_text(encoding="utf-8"))
        marker["section_id"] = "section-FOREIGN"
        save_correction._atomic_write_json(open_round_path, marker)

        _resume_and_expect_identity_mismatch_hold(
            run_dir, lobby, table, ps_store, states_dir, harvested, harvest_completion, section_id, open_round_path,
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# fremder Abschnitt IM MEMBERRECORD (der Marker selbst bleibt korrekt, ein
# einzelnes Mitglieds-Korrekturdatensatz traegt eine ANDERE section_id --
# z.B. durch eine nebenlaeufige/korrupte Schreiboperation).
# ---------------------------------------------------------------------------

def test_foreign_section_in_member_record_holds_marker_preserved():
    section_id = "section-g2"
    root, run_dir, lobby, table, ps_store, states_dir, harvested, harvest_completion, open_round_path = (
        _open_pending_round(section_id)
    )
    try:
        group_repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-guest")
        member_record = save_correction.load_record(run_dir, group_repair_key)
        tampered = dict(member_record)
        tampered["section_id"] = "section-FOREIGN"
        save_correction._write_record(run_dir, group_repair_key, tampered)

        _resume_and_expect_identity_mismatch_hold(
            run_dir, lobby, table, ps_store, states_dir, harvested, harvest_completion, section_id, open_round_path,
        )
    finally:
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
