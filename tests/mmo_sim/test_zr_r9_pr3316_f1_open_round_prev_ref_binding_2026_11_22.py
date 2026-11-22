#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r9_pr3316_f1_open_round_prev_ref_binding_2026_11_22.py —
ZR-R9-PR3316-PREMERGE-NACHZUG-20261122, Befund F1 (GROUP-REVIEW.md §F1,
01_REVIEW.txt Abschnitt 2): der markerbasierte Resume einer offenen
Gruppenkorrekturrunde (`core/runtime.py:has_open_group_round`,
`save_correction.pursue_group_save_correction`s `open_round is not None`-
Zweig) band bislang KEINEN Original-Snapshot in den `_group_rounds/*.open.
json`-Marker -- ein Resume reichte `prev_ref_override=None` durch, sodass
`store.complete_section` beim finalen Plan-Pin den dann FRISCH gelesenen
(ggf. bereits gedrifteten) Current als `expected_prev_ref` uebernahm, statt
den beim Rundenbeginn gueltigen Original-Stand zu pinnen (AR06-Bruch,
belegt durch `repro_open_round_snapshot.py` im Supportpaket).

Nachzug (`mmo_sim/core/save_correction.py`): `_write_open_round`/`load_or_
init_record` binden additiv `expected_prev_ref_by_member` (alle Tisch-
mitglieder) GENAU beim allerersten Betreten des rundenoeffnenden Zweigs;
`pursue_group_save_correction` liest diese Bindung bei JEDEM Resume
(markerbasiert ODER ueber ein bereits vorhandenes Mitgliedsrecord) zurueck
und reicht sie als `prev_ref_override` an alle eigenen `store.complete_
section`-Aufrufe weiter. Ein Marker OHNE diese Bindung (Legacy) haelt
kontrolliert (HOLD), statt den fehlenden Wert zu erraten.

Echter Leader-plus-zwei-Gaeste-Caller (`pursue_group_save_correction` ist
die reale Produktfunktion, `store.complete_section`/`send_correction_turn`
unveraendert, exakt das bereits etablierte Testmuster aus
`test_w49_group_round_restart_2026_10_08.py` -- Direktaufruf der realen
Korrekturfunktion mit realen Store-/Ledger-Abhaengigkeiten gilt in dieser
Suite als echter Caller, kein isolierter Helper-Test):

  F1-A -- normale Wiederaufnahme (kein Drift): die offene Runde bindet den
          Original-Snapshot (seq=1 fuer alle drei Mitglieder); Resume OHNE
          jeden Drift pinnt denselben Snapshot und schliesst erfolgreich ab.
  F1-B -- Current-Drift waehrend der Unterbrechung: Marek driftet nach dem
          Rundenbeginn auf seq=2 (neuere, bereits veroeffentlichte
          Generation). Resume MUSS den ORIGINAL-Snapshot (seq=1) pinnen und
          die Drift erkennen (`_resume_and_harvest` haelt den Abschluss,
          "Recovery abgelehnt") -- NICHT den gedrifteten Stand stillschweigend
          ueberschreiben.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (kein pytest-Fixture-Zwang)."""
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

_MEMBERS = ("leader_pk", "marek_pk", "dronov_pk")
_CHAR_IDS = {"leader_pk": "chrono-leader", "marek_pk": "chrono-marek", "dronov_pk": "chrono-dronov"}
_CID_TO_PK = {v: k for k, v in _CHAR_IDS.items()}


def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


def _build_three_member_table(run_dir: Path, states_dir: Path, table_id: str) -> tuple:
    states_dir.mkdir(parents=True, exist_ok=True)
    schema_path = run_dir.parent / "schema.json"
    schema_path.write_text(_DUMMY_PERSONA_SCHEMA, encoding="utf-8")
    ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
    for pk in _MEMBERS:
        _seed_persona_state(ps_store, states_dir, pk, _CHAR_IDS[pk])
    write_test_profile(run_dir)

    lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
    for pk in _MEMBERS:
        lobby.join(pk)
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["marek_pk", "dronov_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "marek_pk", "accept": True},
            {"type": "consent", "offer_id": "o1", "from": "dronov_pk", "accept": True},
        ],
        chrononaut_ids=dict(_CHAR_IDS),
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store


class _CountingGm:
    """Liefert der Reihe nach vorgegebene Antworten; zaehlt Aufrufe."""

    def __init__(self, contents: list[str]):
        self._contents = list(contents)
        self.calls: list[tuple[int, str]] = []

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls.append((turn_idx, user_text))
        if not self._contents:
            raise AssertionError(f"_CountingGm: unerwarteter zusaetzlicher Transport-Call (turn_idx={turn_idx}).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _open_round_for_missing_marek(run_dir, table, section_id, original_snapshot, original_block=None):
    """Simuliert eine fruehere, dann unterbrochene Prozessinstanz, die die
    Gruppenkorrekturrunde fuer den fehlenden `marek_pk` bereits eroeffnet hat
    -- GENAU die realen Funktionen, die `pursue_group_save_correction` selbst
    beim Rundeneroeffnen durchlaeuft (identisches Setup-Muster zu
    `test_w49_group_round_restart_2026_10_08.py`)."""
    repair_key = save_correction_domain.group_repair_key(table.table_id, section_id, "chrono-marek")
    save_correction.load_or_init_record(
        run_dir, repair_key, persona_key="marek_pk", char_id="chrono-marek",
        operation_key=save_correction_domain.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        expected_prev_ref_by_member=original_snapshot,
    )
    save_correction.begin_attempt(run_dir, repair_key)
    round_no = save_correction._next_round_no(run_dir, table.table_id, section_id)
    save_correction._write_open_round(run_dir, table.table_id, section_id, round_no, [
        {"persona_key": "marek_pk", "char_id": "chrono-marek", "original_block": original_block},
    ], expected_prev_ref_by_member=original_snapshot)
    return repair_key, round_no


def _setup_until_open_round(run_dir: Path, states_dir: Path, table_id: str, section_id: str):
    lobby, table, ps_store = _build_three_member_table(run_dir, states_dir, table_id)
    for pk in _MEMBERS:
        store.publish_current_save(
            run_dir, pk, full_v7_save(_CHAR_IDS[pk], name="Seed"), ps_store, states_dir=states_dir,
        )
    original_snapshot = store.current_save_ref_snapshot(table, ps_store, states_dir)
    assert all(ref is not None and ref["seq"] == 1 for ref in original_snapshot.values()), original_snapshot

    leader_valid = full_v7_save("chrono-leader", name="Leader")
    dronov_valid = full_v7_save("chrono-dronov", name="Dronov")
    harvested = {"leader_pk": leader_valid, "dronov_pk": dronov_valid}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, states_dir, "2026-11-22", ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and harvest_completion.missing == ["marek_pk"], harvest_completion

    repair_key, round_no = _open_round_for_missing_marek(run_dir, table, section_id, original_snapshot)
    return lobby, table, ps_store, harvested, harvest_completion, original_snapshot, repair_key, round_no


# ---------------------------------------------------------------------------
# F1-A -- normale Wiederaufnahme (kein Drift): die offene Runde bindet den
# Original-Snapshot; Resume OHNE Drift pinnt denselben Snapshot.
# ---------------------------------------------------------------------------

def test_f1a_open_round_resume_without_drift_pins_bound_original_snapshot():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        section_id = "section-f1a"
        (lobby, table, ps_store, harvested, harvest_completion,
         original_snapshot, repair_key, round_no) = _setup_until_open_round(
            run_dir, states_dir, f"t-{section_id}", section_id,
        )

        marek_valid = full_v7_save("chrono-marek", name="Marek")
        gm = _CountingGm([f"```json\n{json.dumps(marek_valid)}\n```"])

        # "Neustart": frischer Aufruf der realen Korrekturfunktion OHNE
        # jeden vom Aufrufer mitgegebenen `prev_ref_override` -- genau das,
        # was `core/runtime.py:has_open_group_round` -> `finalize("",
        # resume_section_id=section_id)` liefert.
        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-11-22",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            prev_ref_override=None,
        )
        assert completion_after.success, completion_after.reason
        assert len(gm.calls) == 1, f"genau EIN realer Transport-Call fuer die bereits offene Runde -- {gm.calls}"

        plan_path = store._completion_plan_path(run_dir, section_id)
        assert plan_path.exists(), "die Runde muss einen Abschluss-Auftrag gepinnt haben"
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        for pk in _MEMBERS:
            assert plan_data["members"][pk]["expected_prev_ref"] == original_snapshot[pk], (
                pk, plan_data["members"][pk]
            )
        assert not save_correction._open_round_path(run_dir, table.table_id, section_id).exists()


# ---------------------------------------------------------------------------
# F1-B -- Current-Drift waehrend der Unterbrechung: Resume MUSS den
# ORIGINAL-Snapshot pinnen und die Drift erkennen, NICHT stillschweigend
# ueberschreiben.
# ---------------------------------------------------------------------------

def test_f1b_open_round_resume_with_current_drift_holds_instead_of_overwriting():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir, states_dir = root / "run", root / "states"
        section_id = "section-f1b"
        (lobby, table, ps_store, harvested, harvest_completion,
         original_snapshot, repair_key, round_no) = _setup_until_open_round(
            run_dir, states_dir, f"t-{section_id}", section_id,
        )

        # DRIFT: WAEHREND der (simulierten) Unterbrechung wird fuer
        # marek_pk eine NEUERE Currentgeneration veroeffentlicht -- der
        # beim Rundenbeginn gebundene `original_snapshot["marek_pk"]`
        # (seq=1) ist jetzt veraltet (exakt das AR06-Szenario, s.
        # `repro_open_round_snapshot.py`).
        drifted_marek_save = full_v7_save("chrono-marek", name="Marek-Drift")
        store.publish_current_save(run_dir, "marek_pk", drifted_marek_save, ps_store, states_dir=states_dir)
        drifted_ref = store.current_save_ref_snapshot(table, ps_store, states_dir)["marek_pk"]
        assert drifted_ref != original_snapshot["marek_pk"], "die Drift-Probe braucht einen echten Referenzwechsel."

        # Die Korrekturantwort liefert den urspruenglich angeforderten
        # (gueltigen) Export fuer marek_pk -- UNBEWUSST vom zwischenzeitlich
        # bereits gedrifteten Current.
        marek_correction = full_v7_save("chrono-marek", name="Marek-Korrektur")
        gm = _CountingGm([f"```json\n{json.dumps(marek_correction)}\n```"])

        harvested_after, completion_after = save_correction.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=states_dir, today="2026-11-22",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store, gm_transport=gm,
            cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
            prev_ref_override=None,
        )
        assert len(gm.calls) == 1, f"genau EIN realer Transport-Call -- {gm.calls}"

        # DAS ist der eigentliche Beleg (F1): der Abschluss haelt, weil der
        # gepinnte `expected_prev_ref` der ORIGINAL-Snapshot (seq=1) bleibt
        # UND dieser vom tatsaechlich veroeffentlichten gedrifteten Stand
        # (seq=2) abweicht -- `_resume_and_harvest` erkennt die Drift.
        # F1-Regression (VOR diesem Fix): `prev_ref_override` blieb `None`,
        # `complete_section` pinnte den beim Pin-Moment FRISCH gelesenen
        # (= bereits gedrifteten) Stand, die Drift wurde NIE erkannt, der
        # Abschluss gelang stillschweigend und ueberschrieb die neuere
        # Generation.
        assert not completion_after.success, (
            "der Abschluss haette die Marek-Drift erkennen und HALTEN muessen -- ein stilles "
            f"success=True hier ist GENAU der F1/AR06-Bruch: {completion_after}"
        )
        assert "Recovery abgelehnt" in (completion_after.reason or ""), completion_after.reason

        # Der waehrend der Unterbrechung gedriftete Stand bleibt
        # unveraendert veroeffentlicht -- die Korrekturantwort wurde NICHT
        # stillschweigend darueber geschrieben.
        still_published = store.load_current_save(run_dir, "marek_pk", ps_store, states_dir=states_dir)
        assert still_published == drifted_marek_save, (
            "die waehrend der Unterbrechung veroeffentlichte Generation wurde ueberschrieben -- "
            f"genau der F1/AR06-Bruch: {still_published}"
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
