#!/usr/bin/env python3
"""
tests/mmo_sim/test_section_completion_resume_ar2_contract_binding.py — AR2
Teil A (01_ABSCHLUSSVERTRAG.md, review-evidence/CONTRACT-OBSERVATIONS.json):
positive Request-/Antwortbindung VOR jeder automatischen Ernte/Reflexion/
Finalisierung.

Jeder Fall pausiert (StopAfterResponseGmTransport, dieselbe Technik wie die
bestehenden AR02/AR06/AR09-Tests) GENAU nach der durabel empfangenen
Markerantwort -- der zugehoerige GM-Request ist zu diesem Zeitpunkt bereits
`state=accounted`, `error=None`, `result_text` gesetzt (R12-AUTORECOVERY
Teil A: `core/runtime.py:SectionRuntime.submit` bindet den tatsaechlich
empfangenen Antworttext additiv ueber den bereits bestehenden
`result_text`-Parameter von `request_ledger.finish_received`). Danach wird
GENAU EIN Aspekt der Bindung (Request-Datensatz ODER persistierter sl_log-
Eintrag) gezielt verfaelscht/entfernt -- exakt wie review-evidence/
probe_contract.py, hier aber als reine `assert`-Regression statt eines
Beobachtungsskripts. `control` bleibt die positive Gegenprobe (unveraendert
-> normale automatische Recovery, 0 neue GM-/Spielzuganfragen).

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _section_completion_resume_fixtures import (  # noqa: E402
    COMPLETION_MARKER, ExplodingDriver, ExplodingGmTransport, ReflectionOnlyDriver,
    ScriptedDriver, StopAfterResponseGmTransport, build_two_member_table, clear_lab_stop,
    debrief_with_marker, harvest_extractor, make_env, save_block,
)

import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def _pause_right_after_marker_response(env, lobby, table, ps_store, section_id: str):
    """Baut denselben Anker->Gast-Import->Debrief-mit-Marker-Ablauf wie die
    bestehenden AR02/AR06-Tests und pausiert (lab.stop) GENAU nach dem
    durabel empfangenen Debrief -- VOR Markerpruefung/Plan. Gibt den
    `table_id`/`run_dir`-Pfad zum persistierten Tisch zurueck, damit der
    Aufrufer GENAU EINEN Aspekt der Bindung gezielt verfaelschen kann."""
    leader_save = save_block("chrono-leader")
    guest_save = save_block("chrono-guest")
    debrief = debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save})
    gm = StopAfterResponseGmTransport(
        ["SL-Antwort Anker.", "SL-Antwort Gast-Import.", debrief], run_dir=env.run_dir,
        reason="AR2-contract-binding: Pause nach Markerantwort.",
    )
    leader_driver = ScriptedDriver([
        ParticipantDecision(text="Anker.", save_payload=leader_save, origin_source="fake:leader"),
        ParticipantDecision(text="Debrief-Anfrage.", origin_source="fake:leader-debrief"),
    ])
    guest_driver = ScriptedDriver([
        ParticipantDecision(text="Gast-Import.", save_payload=guest_save, origin_source="fake:guest"),
    ])
    controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})
    runtime = SectionRuntime(
        lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=harvest_extractor,
    )
    outcome = runtime.run_full_section(
        controller, section_id,
        contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
        states_dir=env.states_dir, today="2026-10-13", ts="2026-10-13T07:00:00",
    )
    assert not outcome.completion.success
    assert "Admission-Gate blockiert" in outcome.completion.reason, outcome.completion.reason
    return leader_save, guest_save, debrief


def _gm_request_path_for_turn(run_dir: Path, turn_idx: int) -> Path:
    """Anker-, Gast-Import- UND Debrief-Turn senden JE EINEN eigenen
    `role=gm_turn`-Request (je ein `SectionRuntime.submit()`-Aufruf) --
    GENAU der Request mit `turn_idx == turn_idx` gehoert zu dem sl_log-
    Eintrag, der die Markerantwort traegt (s. `request_ledger.
    _operation_identity`: `turn_idx` ist Teil der Operationsidentitaet)."""
    candidates = [
        p for p in (run_dir / "requests").glob("*.json")
        if (lambda d: d.get("role") == "gm_turn" and d.get("turn_idx") == turn_idx)(
            json.loads(p.read_text(encoding="utf-8"))
        )
    ]
    assert len(candidates) == 1, (turn_idx, candidates)
    return candidates[0]


def main() -> int:
    tests = []
    failed = 0

    def _case(case_name: str):
        with tempfile.TemporaryDirectory() as td:
            env = make_env(Path(td))
            lobby, table, ps_store = build_two_member_table(env, table_id=f"t-ar2-contract-{case_name}")
            write_test_profile(env.run_dir)
            section_id = f"section-ar2-contract-{case_name}"
            leader_save, guest_save, debrief = _pause_right_after_marker_response(
                env, lobby, table, ps_store, section_id,
            )
            table_path = env.run_dir / "tables" / f"{table.table_id}.json"
            table_data = json.loads(table_path.read_text(encoding="utf-8"))
            assert len(table_data["sl_log"]) == 3, table_data["sl_log"]
            marker_turn_idx = table_data["sl_log"][-1]["turn_idx"]
            gm_request_path = _gm_request_path_for_turn(env.run_dir, marker_turn_idx)
            req = json.loads(gm_request_path.read_text(encoding="utf-8"))
            assert req["state"] == "accounted" and req.get("error") is None
            assert req.get("result_text") == table_data["sl_log"][-1]["content"], (
                "Vorbedingung: Original-Antworttext muss bereits durabel im Requestledger "
                "gebunden sein (AR2 Teil A, finish_received(result_text=...))."
            )

            if case_name == "changed_response":
                altered = json.loads(json.dumps({"chrono-leader": leader_save, "chrono-guest": guest_save}))
                altered["chrono-leader"]["characters"][0]["name"] = "Changed AR2 Figure"
                table_data["sl_log"][-1]["content"] = debrief_with_marker(altered)
            elif case_name == "foreign_persona":
                table_data["sl_log"][-1]["origin_persona_key"] = "foreign-persona"
            elif case_name == "request_error":
                req["error"] = "synthetic contradictory terminal error"
            elif case_name == "request_sent":
                req["state"] = "sent"
                req["settled_ts"] = None
                req["usd_reconciled"] = False
            elif case_name == "missing_request":
                gm_request_path.unlink()
            elif case_name == "missing_snapshot":
                table_data["sl_log"][-1].pop("expected_prev_ref_by_member")
            elif case_name == "empty_snapshot":
                table_data["sl_log"][-1]["expected_prev_ref_by_member"] = {}
            elif case_name != "control":
                raise AssertionError(f"unbekannter Fall: {case_name}")

            table_path.write_text(json.dumps(table_data, ensure_ascii=False), encoding="utf-8")
            if gm_request_path.exists():
                gm_request_path.write_text(json.dumps(req, ensure_ascii=False), encoding="utf-8")

            clear_lab_stop(env.run_dir)
            reloaded = store.Table.load(env.run_dir, table.table_id)
            if case_name == "control":
                controller2 = TableController(leader_key="leader_pk", drivers={
                    "leader_pk": ReflectionOnlyDriver("Reflexion Leader.", "fake:leader-reflect"),
                    "guest_pk": ReflectionOnlyDriver("Reflexion Gast.", "fake:guest-reflect"),
                })
            else:
                controller2 = TableController(leader_key="leader_pk", drivers={
                    "leader_pk": ExplodingDriver(f"leader-{case_name}"),
                    "guest_pk": ExplodingDriver(f"guest-{case_name}"),
                })
            runtime2 = SectionRuntime(
                lobby=lobby, table=reloaded, gm_transport=ExplodingGmTransport(),
                marker=COMPLETION_MARKER, harvest_validator=ZeitrissHarvestValidator(),
                persona_state_store=ps_store, harvest_extractor=harvest_extractor,
            )
            outcome2 = runtime2.run_full_section(
                controller2, section_id,
                contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
                states_dir=env.states_dir, today="2026-10-13", ts="2026-10-13T07:05:00",
            )
            if case_name == "control":
                assert outcome2.completion.success, outcome2.completion.reason
                assert set(outcome2.completion.members_completed) == {"leader_pk", "guest_pk"}
            else:
                assert not outcome2.completion.success, (
                    f"AR2 Teil A: Fall {case_name!r} MUSS kontrolliert HOLDen (kein Ernte/"
                    f"Finalisierung trotz manipulierter Bindung) -- reason={outcome2.completion.reason!r}"
                )
                assert store.open_completion_order_for_table(env.run_dir, table.table_id) is None, (
                    f"Fall {case_name!r}: HOLD darf keinen Completion-Plan pinnen."
                )

    for name in (
        "control", "changed_response", "foreign_persona", "request_error",
        "request_sent", "missing_request", "missing_snapshot", "empty_snapshot",
    ):
        try:
            _case(name)
            print(f"OK   case_{name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL case_{name}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR case_{name}:")
            traceback.print_exc()
    total = 8
    print(f"\n{total - failed}/{total} Faelle bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
