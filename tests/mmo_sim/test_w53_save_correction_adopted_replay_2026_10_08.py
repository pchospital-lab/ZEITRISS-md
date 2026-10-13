#!/usr/bin/env python3
"""
tests/mmo_sim/test_w53_save_correction_adopted_replay_2026_10_08.py --
R12-Savegate, W53-Slice: schliesst das in W49-REPORT.md §7 (CARRY-FORWARD
W49-SS7) offen gemeldete, enge Crashfenster im Gruppenpfad
(`mmo_sim/core/save_correction.py:pursue_group_save_correction`) zwischen
`_clear_open_round(...)` und dem unmittelbar folgenden
`store.complete_section(...)`-Aufruf.

Befund (W53-MAIN-COUNTERPROOF.md): ein Kandidat kann bereits vollstaendig
akzeptiert sein (`mark_adopted`, Marker geloescht) -- crasht der Prozess
GENAU in diesem Fenster, bevor `store.complete_section` den korrigierten
Block je gesehen hat, fand ein Neustart (frisches `harvested` ohne den
korrigierten Block, `open_round is None`, Fresh-Zweig) den Datensatz
bereits `state=="adopted"` vor und ueberging ihn per blindem `continue` --
der bereits akzeptierte Block war dadurch DAUERHAFT verloren (nie neu
angefragt, nie publiziert).

W53-Fix (NUR `mmo_sim/core/save_correction.py`):
  1. `mark_adopted(..., adopted_block=...)` persistiert die adoptierten
     Blockbytes ATOMAR zusammen mit `state="adopted"` als neues internes
     Corrector-Metadatum.
  2. Im Fresh-Zweig wird bei `state==STATE_ADOPTED` und weiterhin
     fehlendem `pk` der persistierte Block in `harvested[pk]`
     zurueckgespielt (statt blindem Verwerfen) -- UND, falls dadurch kein
     neuer Versandkandidat mehr uebrig bleibt, wird `store.complete_
     section` (unveraendert, idempotent) genau einmal erneut aufgerufen,
     BEVOR die While-Schleife terminiert, damit der wiederhergestellte
     Stand tatsaechlich publiziert wird.

Abdeckung:
  W53-E -- Crash NACH `_clear_open_round`, VOR `store.complete_section`:
           genau EIN bereits adoptierter Kandidat (einziges fehlendes
           Mitglied). Restart MUSS den adoptierten Block publizieren --
           kein Verlust, 0 zusaetzliche Transport-Calls, `attempts_used`
           unveraendert, genau 1 Ledger-Datensatz.
  W53-F -- Dieselbe Crash-Situation, aber GEMISCHT mit einem ZWEITEN,
           noch nicht einmal angefragten Mitglied derselben Section
           (unabhaengiger `repair_key`/eigene Runde) -- belegt, dass die
           Wiederherstellung des adoptierten Kandidaten die normale
           Neueroeffnung einer Runde fuer ein echtes, noch offenes
           Mitglied nicht stoert (beide werden am Ende korrekt publiziert).

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie
`test_w49_group_round_restart_2026_10_08.py`. Kein Netz, kein Livecall --
ausschliesslich kontrollierte, lokal geskriptete Fake-SL-Antworten."""
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

from _full_v7_fixture import full_v7_save  # noqa: E402 (Fixturehelper, FIXTURE_ONLY)

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402

_DUMMY_PERSONA_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _wallet_as_number(char_id: str, name: str = "Flo") -> dict:
    """Mild-pass, aber strukturell schema-ungueltig (identisches Muster zu
    `test_w49_group_round_restart_2026_10_08.py`'s `_wallet_as_number`)."""
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
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, "t-w53",
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


class _ExplodingGm:
    """Wirft bei JEDEM Call -- Beleg, dass fuer einen bereits adoptierten/
    erfolgreich abgeschlossenen Kandidaten KEIN zusaetzlicher realer
    Transport-/SL-Turn ausgeloest wird."""

    def turn(self, *a, **k):
        raise AssertionError("W53: kein zusaetzlicher realer SL-Turn fuer einen bereits adoptierten Kandidaten.")


class _CountingGm:
    """Liefert der Reihe nach vorgegebene Antworten; zaehlt Aufrufe (fuer
    `store.submit_to_sl`-Aufrufe aus dem Gruppenpfad)."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(f"_CountingGm: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _ledger_group_records(run_dir: Path) -> list[dict]:
    return [r for r in request_ledger._all_records(run_dir) if r.get("role") == save_correction_domain.ROLE_GROUP]


_CID_TO_PK = {"chrono-leader": "leader_pk", "chrono-guest": "guest_pk"}


def _simulate_adopted_then_crash_before_complete_section(
    run_dir: Path, table, section_id: str, pk: str, char_id: str, invalid_block: dict, valid_block: dict,
) -> tuple[str, int]:
    """Durchlaeuft EXAKT die Schritte, die `pursue_group_save_correction`
    selbst fuer eine erfolgreich akzeptierte Runde durchlaeuft -- bis UND
    EINSCHLIESSLICH `_clear_open_round` -- und bricht DANACH ab (simulierter
    Prozessabsturz), OHNE `store.complete_section` aufzurufen. Nutzt
    ausschliesslich oeffentliche/bereits-vorhandene Funktionen (identisches
    Muster zu `refs/w49-negative-control-reproduction-script.py`). Gibt
    `(repair_key, round_no)` zurueck."""
    repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, char_id)
    save_correction.load_or_init_record(
        run_dir, repair_key, persona_key=pk, char_id=char_id,
        operation_key=save_correction_domain.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
    )
    save_correction.begin_attempt(run_dir, repair_key)
    round_no = save_correction._next_round_no(run_dir, table.table_id, section_id)
    save_correction._write_open_round(run_dir, table.table_id, section_id, round_no, [
        {"persona_key": pk, "char_id": char_id, "original_block": invalid_block},
    ])

    real_gm = _CountingGm([f"```json\n{json.dumps(valid_block)}\n```"])
    message = save_correction_domain.build_group_correction_message(
        table_id=table.table_id, section_id=section_id, requests=[{
            "persona_key": pk, "char_id": char_id,
            "acceptance": save_correction_domain.evaluate(invalid_block, char_id),
            "original_block": invalid_block, "attempt_no": 1,
        }],
    )
    sent = save_correction.send_correction_turn(
        run_dir, role=save_correction_domain.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        participant=table.leader, turn_idx=round_no, outgoing_text=message, gm_transport=real_gm, table=table,
    )
    assert sent.blocked is False and len(real_gm.calls) == 1

    save_correction.record_correction_received(run_dir, repair_key, request_id=sent.request_id)
    # `harvested[pk] = valid_block` (nur in-memory, so wie Z.627 im
    # Produktcode) -- wird absichtlich NICHT an den Aufrufer zurueckgegeben,
    # weil genau DAS beim echten Absturz verloren geht.
    save_correction.mark_adopted(run_dir, repair_key, adopted_block=valid_block)
    save_correction._clear_open_round(run_dir, table.table_id, section_id)
    # *** SIMULIERTER CRASH HIER *** -- exakt zwischen `_clear_open_round`
    # (Z.601 im Produktcode) und `store.complete_section` (Z.603): der
    # Marker ist weg, `harvested[pk]` existiert nur noch in der (jetzt
    # verlorenen) RAM-Kopie des abgestuerzten Prozesses, `complete_section`
    # wurde fuer diesen korrigierten Block NIE aufgerufen.
    assert not save_correction._open_round_path(run_dir, table.table_id, section_id).exists()
    return repair_key, round_no


# ---------------------------------------------------------------------------
# W53-E -- genau EIN bereits adoptierter Kandidat, einziges fehlendes
# Mitglied der Section -- Restart MUSS den Block publizieren, kein Verlust.
# ---------------------------------------------------------------------------

def test_w53e_crash_after_clear_open_round_before_complete_section_replays_adopted_block():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        guest_invalid = _wallet_as_number("chrono-guest")
        leader_valid = full_v7_save("chrono-leader", name="Leader")
        harvested = {"leader_pk": leader_valid, "guest_pk": guest_invalid}
        harvest_completion = store.complete_section(
            lobby, table, "section-w53e", harvested, states_dir, "2026-10-08",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion

        guest_valid = full_v7_save("chrono-guest", name="Flo")
        repair_key, round_no = _simulate_adopted_then_crash_before_complete_section(
            run_dir, table, "section-w53e", "guest_pk", "chrono-guest", guest_invalid, guest_valid,
        )
        before = save_correction.load_record(run_dir, repair_key)
        assert before["attempts_used"] == 1 and before["state"] == "adopted"
        assert before.get("adopted_block") == guest_valid, "adoptierter Block muss persistiert sein (W53-Fix 1)."

        ledger_before = _ledger_group_records(run_dir)
        assert len(ledger_before) == 1

        # "Neustart": frisch rekonstruiertes `harvested` (wie ein echter
        # Prozessneustart es liefern wuerde -- die RAM-Kopie mit dem
        # korrigierten Block ist verloren, NUR der urspruengliche ungueltige
        # Stand ist bekannt) UND derselbe `harvest_completion`-Stand
        # (`missing=["guest_pk"]`), wie der Aufrufer ihn nach dem Absturz per
        # erneutem `store.complete_section`-Aufruf (unveraendert) bekommen
        # wuerde. Transport wuerde bei einem (verbotenen) Zweitversand werfen.
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-w53e", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=_ExplodingGm(),
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        assert completion_after.success, (
            f"der bereits adoptierte Block MUSS nach Restart publiziert werden, kein Verlust -- {completion_after}"
        )
        assert harvested_after["guest_pk"] == guest_valid, "adoptierter Block darf NICHT verloren gehen."

        after = save_correction.load_record(run_dir, repair_key)
        assert after["attempts_used"] == 1, (
            f"attempts_used darf durch die Wiederherstellung NICHT veraendert werden -- {after['attempts_used']}"
        )
        assert after["state"] == "adopted"

        ledger_after = _ledger_group_records(run_dir)
        assert len(ledger_after) == 1, f"genau EIN Ledger-Datensatz, kein neuer Versand -- {ledger_after}"
        assert ledger_after == ledger_before, "kein zusaetzlicher/veraenderter Ledger-Datensatz durch den Restart."

        assert not save_correction._open_round_path(run_dir, table.table_id, "section-w53e").exists()
        assert store.open_completion_order_for_table(run_dir, table.table_id) == "section-w53e", (
            "PHASE 1 (Ernte) muss nach der Wiederherstellung gepinnt sein -- echte Publikation hat stattgefunden."
        )

        # W49-No-Replay bleibt erhalten: ein weiterer Aufruf loest keinen
        # zusaetzlichen Transport-Call/Ledger-Datensatz aus.
        harvested_again, completion_again = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-w53e", harvested=dict(harvested_after),
            harvest_completion=completion_after, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=_ExplodingGm(),
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert completion_again is completion_after
        assert len(_ledger_group_records(run_dir)) == 1


# ---------------------------------------------------------------------------
# W53-F -- derselbe Crash-Fall, GEMISCHT mit einem zweiten, noch nie
# angefragten Mitglied derselben Section -- die Wiederherstellung des
# adoptierten Kandidaten darf die normale Neueroeffnung einer Runde fuer das
# echte, noch offene Mitglied nicht stoeren.
# ---------------------------------------------------------------------------

def test_w53f_mixed_adopted_replay_and_fresh_round_for_other_member():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        lobby, table, ps_store = _build_two_member_table(run_dir, states_dir)

        guest_invalid = _wallet_as_number("chrono-guest")
        leader_invalid = _wallet_as_number("chrono-leader", name="Leader")
        harvested = {"leader_pk": leader_invalid, "guest_pk": guest_invalid}
        harvest_completion = store.complete_section(
            lobby, table, "section-w53f", harvested, states_dir, "2026-10-08",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success
        assert set(harvest_completion.missing) == {"leader_pk", "guest_pk"}

        # NUR der Guest-Kandidat wird in der simulierten (dann gecrashten)
        # Vorrunde adoptiert -- der Leader-Kandidat wurde in dieser Vorrunde
        # NIE angefragt (eigener `repair_key`, eigene Rundenidentitaet).
        guest_valid = full_v7_save("chrono-guest", name="Flo")
        repair_key_guest, _ = _simulate_adopted_then_crash_before_complete_section(
            run_dir, table, "section-w53f", "guest_pk", "chrono-guest", guest_invalid, guest_valid,
        )

        leader_valid = full_v7_save("chrono-leader", name="Leader")
        gm = _CountingGm([f"```json\n{json.dumps(leader_valid)}\n```"])
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id="section-w53f", harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-10-08",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        assert completion_after.success, completion_after.reason
        assert harvested_after["guest_pk"] == guest_valid, "adoptierter Guest-Block darf nicht verloren gehen."
        assert harvested_after["leader_pk"] == leader_valid, "Leader muss ganz normal EINE neue Runde erhalten."
        assert len(gm.calls) == 1, f"genau EIN realer Transport-Call (nur fuer den Leader) -- {gm.calls}"

        guest_record = save_correction.load_record(run_dir, repair_key_guest)
        assert guest_record["attempts_used"] == 1, "Guest-Budget darf durch die Wiederherstellung nicht steigen."
        leader_repair_key = save_correction_domain.group_repair_key(table.table_id, "section-w53f", "chrono-leader")
        leader_record = save_correction.load_record(run_dir, leader_repair_key)
        assert leader_record["attempts_used"] == 1 and leader_record["state"] == "adopted"

        ledger_records = _ledger_group_records(run_dir)
        # 1 Datensatz aus der simulierten Guest-Vorrunde + 1 neuer fuer die
        # echte Leader-Runde = 2, KEIN dritter (kein Zweitversand fuer Guest).
        assert len(ledger_records) == 2, f"Guest-Vorrunde (1) + neue Leader-Runde (1), kein Zweitversand -- {ledger_records}"
        assert not save_correction._open_round_path(run_dir, table.table_id, "section-w53f").exists()


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
