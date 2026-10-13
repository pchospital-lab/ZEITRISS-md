#!/usr/bin/env python3
"""
tests/mmo_sim/test_section_completion_resume_sequence.py — R12-AUTORECOVERY:
CASES.json AR09 (zwei aufeinanderfolgende Abschnitte -- Abschnitt A regulaer
geschlossen, Abschnitt B auf der naechsten Tischgeneration unterbrochen und
automatisch fortgesetzt, A bleibt unangetastet) und AR07 (partieller
Ernte-/Reflexionsfortschritt -- ein bereits erfolgreich reflektiertes
Mitglied wird bei einem weiteren Resume NICHT erneut gefragt).

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _section_completion_resume_fixtures import (  # noqa: E402
    COMPLETION_MARKER, ExplodingDriver, ExplodingGmTransport, ReflectionOnlyDriver,
    ScriptedDriver, ScriptedGmTransport, build_two_member_table, clear_lab_stop,
    debrief_with_marker, harvest_extractor, make_env, save_block, write_lab_stop,
)

import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def _run_section_a(env, lobby, table, ps_store):
    leader_save = save_block("chrono-leader", wallet=1.0)
    guest_save = save_block("chrono-guest", wallet=1.0)
    gm = ScriptedGmTransport([
        "SL-Antwort Anker A.", "SL-Antwort Gast-Import A.",
        debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save}),
    ])
    leader_driver = ScriptedDriver([
        ParticipantDecision(text="Anker A.", save_payload=leader_save, origin_source="fake:leader"),
        ParticipantDecision(text="Debrief A.", origin_source="fake:leader-debrief"),
        ParticipantDecision(text="Reflexion A Leader.", origin_source="fake:leader-reflect"),
    ])
    guest_driver = ScriptedDriver([
        ParticipantDecision(text="Gast-Import A.", save_payload=guest_save, origin_source="fake:guest"),
        ParticipantDecision(text="Reflexion A Gast.", origin_source="fake:guest-reflect"),
    ])
    controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})
    runtime = SectionRuntime(
        lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        harvest_extractor=harvest_extractor,
    )
    outcome = runtime.run_full_section(
        controller, "section-ar09-a",
        contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
        states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T08:00:00",
    )
    assert outcome.completion.success, outcome.completion.reason
    return leader_save, guest_save


def test_ar09_second_section_on_next_table_generation_interrupted_then_auto_resumed():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-ar09")
        write_test_profile(env.run_dir)

        leader_save_a, guest_save_a = _run_section_a(env, lobby, table, ps_store)
        table_a_final = store.Table.load(env.run_dir, "t-ar09")
        assert table_a_final.status == "closed"

        # Abschnitt B: naechste Tischgeneration (A6/D5, __2) fuer dieselben
        # Mitglieder/Figuren -- unterbrochen GENAU nach der Markerantwort
        # (lab.stop, s. AR02-Technik), dann automatisch fortgesetzt.
        table_b, derivation_b = store.create_table_from_offer_log(
            lobby, "t-ar09",
            offer_log_events=[
                {"type": "offer", "id": "o2", "from": "leader_pk", "wants": ["guest_pk"]},
                {"type": "consent", "offer_id": "o2", "from": "guest_pk", "accept": True},
            ],
            chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
        )
        assert table_b is not None and table_b.table_id == "t-ar09__2", derivation_b

        leader_save_b, guest_save_b = save_block("chrono-leader", wallet=2.0), save_block("chrono-guest", wallet=2.0)
        gm_b = ScriptedGmTransport([
            "SL-Antwort Anker B.",
            debrief_with_marker({"chrono-leader": leader_save_b, "chrono-guest": guest_save_b}),
        ])

        def _stop_after_last(turn_idx, user_text, **kwargs):
            res = ScriptedGmTransport.turn(gm_b, turn_idx, user_text, **kwargs)
            if not gm_b._contents:
                write_lab_stop(env.run_dir, "AR09: Pause nach Markerantwort in Abschnitt B.")
            return res

        gm_b.turn = _stop_after_last
        leader_driver_b1 = ScriptedDriver([
            ParticipantDecision(text="Anker B.", save_payload=leader_save_b, origin_source="fake:leader"),
        ])
        guest_driver_b1 = ScriptedDriver([
            ParticipantDecision(text="Gast-Import B.", save_payload=guest_save_b, origin_source="fake:guest"),
        ])
        controller_b1 = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver_b1, "guest_pk": guest_driver_b1})
        runtime_b1 = SectionRuntime(
            lobby=lobby, table=table_b, gm_transport=gm_b, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=harvest_extractor,
        )
        outcome_b1 = runtime_b1.run_full_section(
            controller_b1, "section-ar09-b",
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T08:30:00",
        )
        assert not outcome_b1.completion.success
        assert "Admission-Gate blockiert" in outcome_b1.completion.reason

        # Abschnitt A bleibt WAEHREND der Unterbrechung von B unangetastet.
        table_a_check = store.Table.load(env.run_dir, "t-ar09")
        assert table_a_check.status == "closed"
        assert store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir) == leader_save_a

        clear_lab_stop(env.run_dir)
        controller_b2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver("Reflexion B Leader.", "fake:leader-reflect-b"),
            "guest_pk": ReflectionOnlyDriver("Reflexion B Gast.", "fake:guest-reflect-b"),
        })
        runtime_b2 = SectionRuntime(
            lobby=lobby, table=store.Table.load(env.run_dir, "t-ar09__2"), gm_transport=ExplodingGmTransport(),
            marker=COMPLETION_MARKER, harvest_validator=ZeitrissHarvestValidator(),
            persona_state_store=ps_store, harvest_extractor=harvest_extractor,
        )
        outcome_b2 = runtime_b2.run_full_section(
            controller_b2, "section-ar09-b",
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T08:45:00",
        )
        assert outcome_b2.completion.success, outcome_b2.completion.reason
        assert set(outcome_b2.completion.members_completed) == {"leader_pk", "guest_pk"}

        # Jede Section hat ihre EIGENEN fuenf (hier: zwei) Reflexionen und
        # Endsavegenerationen -- kein Vermischen von A und B.
        assert store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir) == leader_save_b
        reflections = (env.run_dir / "reflections.jsonl").read_text(encoding="utf-8").splitlines()
        import json
        rows = [json.loads(l) for l in reflections if l.strip()]
        sections_seen = {r["section_id"] for r in rows if r.get("kind") == "ai_required_reflection"}
        assert sections_seen == {"section-ar09-a", "section-ar09-b"}, sections_seen
        # A behaelt GENAU ihre zwei Reflexionen, B bekommt GENAU ihre eigenen
        # zwei -- kein Doppel-/Nullzaehlen durch die Auto-Recovery.
        assert sum(1 for r in rows if r.get("section_id") == "section-ar09-a" and r.get("kind") == "ai_required_reflection") == 2
        assert sum(1 for r in rows if r.get("section_id") == "section-ar09-b" and r.get("kind") == "ai_required_reflection") == 2
        table_a_final_check = store.Table.load(env.run_dir, "t-ar09")
        assert table_a_final_check.status == "closed" and len(table_a_final_check.sl_log) == 3


def test_ar07_partial_reflection_progress_continues_idempotently_without_resending_completed_member():
    """AR07: ein Mitglied hat seine Pflichtreflexion bereits erfolgreich
    committet, ein ANDERES wurde durch das (D4/A1 'JE Reflexion'-)Admission-
    Gate noch NICHT gefragt (Stop zwischen den beiden Mitgliedern gesetzt).
    Ein weiterer Resume darf das bereits erfolgreiche Mitglied NICHT erneut
    fragen -- nur das noch offene wird nachgeholt, danach schliesst der
    Abschnitt final. `table.members` ist sortiert (`guest_pk` vor
    `leader_pk`) -- der Gast reflektiert hier zuerst und setzt dabei (als
    Testseiteneffekt) den Stop, der DANACH GENAU den Leader blockt."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-ar07")
        write_test_profile(env.run_dir)

        leader_save = save_block("chrono-leader")
        guest_save = save_block("chrono-guest")
        gm = ScriptedGmTransport([
            "SL-Antwort Anker.", debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save}),
        ])

        class _GuestReflectsThenStops:
            """Beantwortet Import UND Reflexion ganz normal (committet
            erfolgreich), setzt aber NACH der Reflexionsantwort den
            Lab-Stop -- der naechste Gate-Check (fuer den Leader, der laut
            sortierter `table.members`-Reihenfolge ALS ZWEITER reflektiert)
            sieht den Stop VOR seiner eigenen Anfrage."""

            def __init__(self):
                self._script = [
                    ParticipantDecision(text="Gast-Import.", save_payload=guest_save, origin_source="fake:guest"),
                    ParticipantDecision(text="Reflexion Gast (erfolgreich).", origin_source="fake:guest-reflect"),
                ]
                self.calls = 0

            def decide(self, context: dict):
                self.calls += 1
                decision = self._script.pop(0)
                if context.get("system") == "PRIVATE_REFLECTION_SENTINEL":
                    write_lab_stop(env.run_dir, "AR07: Stop nach Gast-Reflexion, vor Leader-Reflexion.")
                return decision

        leader_driver = ScriptedDriver([
            ParticipantDecision(text="Anker.", save_payload=leader_save, origin_source="fake:leader"),
            ParticipantDecision(text="Reflexion Leader (wird in Runde 1 NICHT erreicht).", origin_source="fake:leader-reflect"),
        ])
        guest_driver = _GuestReflectsThenStops()
        controller1 = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})
        runtime1 = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=harvest_extractor,
        )
        outcome1 = runtime1.run_full_section(
            controller1, "section-ar07",
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T08:00:00",
        )
        assert not outcome1.completion.success
        assert "Reflexion" in outcome1.completion.reason, outcome1.completion.reason
        assert guest_driver.calls == 2, "Gast: Import + Reflexion -- beide bereits real angefragt/committet."
        assert leader_driver.calls == 1, "Leader: nur der Anker -- die Reflexion wurde durch den Stop verhindert."

        reflections_raw = (env.run_dir / "reflections.jsonl").read_text(encoding="utf-8").splitlines()
        import json as _json
        committed = {r["persona_key"] for r in (_json.loads(l) for l in reflections_raw if l.strip()) if r.get("kind") == "ai_required_reflection"}
        assert committed == {"guest_pk"}, committed

        # Fresh resume: STOP entfernt. GENAU der bestehende Resume-Pfad
        # (offener Completion-Auftrag -- NICHT unser neuer Auto-Recovery-
        # Zweig, der bereits VORHER in `run_full_section` greift) muss den
        # Gast NICHT erneut fragen (ExplodingDriver deckt das auf) und darf
        # KEINEN neuen GM-Turn ausloesen.
        clear_lab_stop(env.run_dir)
        leader_driver2 = ScriptedDriver([ParticipantDecision(text="Reflexion Leader (jetzt erfolgreich).", origin_source="fake:leader-reflect")])
        controller2 = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver2, "guest_pk": ExplodingDriver("guest-done")})
        runtime2 = SectionRuntime(
            lobby=lobby, table=store.Table.load(env.run_dir, "t-ar07"), gm_transport=ExplodingGmTransport(),
            marker=COMPLETION_MARKER, harvest_validator=ZeitrissHarvestValidator(),
            persona_state_store=ps_store, harvest_extractor=harvest_extractor,
        )
        outcome2 = runtime2.run_full_section(
            controller2, "section-ar07",
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T08:10:00",
        )
        assert outcome2.completion.success, outcome2.completion.reason
        assert leader_driver2.calls == 1, "Leader wird genau EIN weiteres Mal (fuer seine ausstehende Reflexion) gefragt."


def main() -> int:
    tests = [
        test_ar09_second_section_on_next_table_generation_interrupted_then_auto_resumed,
        test_ar07_partial_reflection_progress_continues_idempotently_without_resending_completed_member,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
