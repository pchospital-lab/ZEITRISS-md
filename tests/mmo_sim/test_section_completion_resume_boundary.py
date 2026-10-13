#!/usr/bin/env python3
"""
tests/mmo_sim/test_section_completion_resume_boundary.py — R12-AUTORECOVERY:
CASES.json AR01 (Kontrollreise), AR02 (Frist/Admission-Pause NACH erfolgreicher
Antwort), AR04 (aktiver STOP verhindert automatische Ernte, saubere Pause +
spaetere frische Autorisierung setzt DIESELBE Operation fort).

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
    ScriptedDriver, ScriptedGmTransport, StopAfterResponseGmTransport,
    build_two_member_table, clear_lab_stop, debrief_with_marker, harvest_extractor,
    make_env, write_lab_stop,
)

import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def test_ar01_uninterrupted_control_journey_unaffected_by_auto_recovery():
    """AR01: ein ganz normaler, ununterbrochener Ablauf (Anker, Gast-Import,
    Debrief mit Marker) darf durch die neue Auto-Recovery-Pruefung KEINE
    zusaetzliche GM-/Persona-Anfrage bekommen -- `find_recoverable_entry`
    muss beim allerersten Aufruf (leeres `sl_log`) sofort `None` liefern und
    den bestehenden Pfad unveraendert laufen lassen."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env)
        write_test_profile(env.run_dir)

        from _full_v7_fixture import full_v7_save
        leader_save = full_v7_save("chrono-leader", name="Testfigur")
        guest_save = full_v7_save("chrono-guest", name="Testfigur")
        debrief = debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save})

        gm = ScriptedGmTransport(["SL-Antwort auf Anker.", "SL-Antwort auf Gast-Import.", debrief])
        leader_driver = ScriptedDriver([
            ParticipantDecision(text="Anker-Text.", save_payload=leader_save, origin_source="fake:leader"),
            ParticipantDecision(text="Debrief-Anfrage.", origin_source="fake:leader-debrief"),
            ParticipantDecision(text="Reflexion Leader.", origin_source="fake:leader-reflect"),
        ])
        guest_driver = ScriptedDriver([
            ParticipantDecision(text="Gast-Import.", save_payload=guest_save, origin_source="fake:guest"),
            ParticipantDecision(text="Reflexion Gast.", origin_source="fake:guest-reflect"),
        ])
        controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})

        runtime = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=harvest_extractor,
        )
        outcome = runtime.run_full_section(
            controller, "section-ar01",
            contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"user": "ctx-guest"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T10:00:00",
        )
        assert outcome.completion.success, outcome.completion.reason
        assert set(outcome.completion.members_completed) == {"leader_pk", "guest_pk"}
        assert len(gm.calls) == 3, "genau Anker+Gast-Import+Debrief -- keine zusaetzliche Auto-Recovery-Anfrage"
        assert leader_driver.calls == 3 and guest_driver.calls == 2


def test_ar02_ar04_admission_pause_after_durable_response_then_fresh_resume_harvests_without_new_turn():
    """AR02: eine Startfrist/ein STOP greift GENAU NACH der durabel
    empfangenen Markerantwort (noch vor Markerpruefung/Plan) -- der laufende
    Prozess pausiert (`blocked_outcome`), KEIN heimlicher Abschluss an der
    Sperre vorbei. AR04: solange der STOP aktiv bleibt, bleibt JEDER weitere
    Versuch blockiert (keine automatische Ernte an bestehenden Schutz-
    bedingungen vorbei) -- erst eine SAUBERE, spaetere frische Autorisierung
    (STOP entfernt) fuehrt DIESELBE Operation fort: automatische Ernte der
    ORIGINAL empfangenen Antwort, null neue GM-/Persona-Spielzug-
    Entscheidungen, nur die weiterhin faellige Pflicht-KI-Reflexion."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-ar02")
        write_test_profile(env.run_dir)

        from _full_v7_fixture import full_v7_save
        leader_save = full_v7_save("chrono-leader", name="Testfigur")
        guest_save = full_v7_save("chrono-guest", name="Testfigur")
        debrief = debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save})

        gm1 = StopAfterResponseGmTransport(
            ["SL-Antwort auf Anker.", "SL-Antwort auf Gast-Import.", debrief], run_dir=env.run_dir,
            reason="AR02: Startfrist nach erfolgreicher Antwort ueberschritten (Testfixture).",
        )
        leader_driver1 = ScriptedDriver([
            ParticipantDecision(text="Anker-Text.", save_payload=leader_save, origin_source="fake:leader"),
            ParticipantDecision(text="Debrief-Anfrage.", origin_source="fake:leader-debrief"),
        ])
        guest_driver1 = ScriptedDriver([
            ParticipantDecision(text="Gast-Import.", save_payload=guest_save, origin_source="fake:guest"),
        ])
        controller1 = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver1, "guest_pk": guest_driver1})
        runtime1 = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm1, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=harvest_extractor,
        )
        outcome1 = runtime1.run_full_section(
            controller1, "section-ar02",
            contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"user": "ctx-guest"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T10:00:00",
        )
        assert not outcome1.completion.success
        assert "Admission-Gate blockiert" in outcome1.completion.reason, outcome1.completion.reason
        assert len(gm1.calls) == 3, "Anker+Gast-Import+Debrief wurden bereits durabel versandt/empfangen"
        # Die Antwort ist durabel im sl_log -- aber NOCH kein Completion-Plan.
        reloaded = store.Table.load(env.run_dir, table.table_id)
        assert reloaded.sl_log[-1]["content"] == debrief
        assert store.open_completion_order_for_table(env.run_dir, table.table_id) is None

        # AR04: STOP bleibt aktiv -- ein weiterer Versuch (neuer Prozess/neue
        # Runtime-Instanz, EXPLODING-Treiber/-Transport als Beweis, dass bei
        # aktivem STOP NICHTS automatisch geerntet/gesendet werden darf) muss
        # GENAUSO blockiert bleiben.
        controller_blocked = TableController(
            leader_key="leader_pk",
            drivers={"leader_pk": ExplodingDriver("leader-still-stopped"), "guest_pk": ExplodingDriver("guest-still-stopped")},
        )
        runtime_blocked = SectionRuntime(
            lobby=lobby, table=store.Table.load(env.run_dir, table.table_id), gm_transport=ExplodingGmTransport(),
            marker=COMPLETION_MARKER, harvest_validator=ZeitrissHarvestValidator(),
            persona_state_store=ps_store, harvest_extractor=harvest_extractor,
        )
        outcome_still_blocked = runtime_blocked.run_full_section(
            controller_blocked, "section-ar02",
            contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"user": "ctx-guest"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T10:05:00",
        )
        assert not outcome_still_blocked.completion.success
        assert "Admission-Gate blockiert" in outcome_still_blocked.completion.reason

        # Saubere Pause vorbei, frische Autorisierung (STOP entfernt) --
        # DIESELBE Operation wird fortgesetzt: automatische Ernte, KEIN neuer
        # Spiel-/GM-Turn (ExplodingGmTransport/-Driver wuerden sonst feuern),
        # nur die weiterhin faellige Pflicht-Reflexion (ReflectionOnlyDriver).
        clear_lab_stop(env.run_dir)
        controller2 = TableController(
            leader_key="leader_pk",
            drivers={
                "leader_pk": ReflectionOnlyDriver("Reflexion Leader nach Recovery.", "fake:leader-reflect"),
                "guest_pk": ReflectionOnlyDriver("Reflexion Gast nach Recovery.", "fake:guest-reflect"),
            },
        )
        runtime2 = SectionRuntime(
            lobby=lobby, table=store.Table.load(env.run_dir, table.table_id), gm_transport=ExplodingGmTransport(),
            marker=COMPLETION_MARKER, harvest_validator=ZeitrissHarvestValidator(),
            persona_state_store=ps_store, harvest_extractor=harvest_extractor,
        )
        outcome2 = runtime2.run_full_section(
            controller2, "section-ar02",
            contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"user": "ctx-guest"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T10:10:00",
        )
        assert outcome2.completion.success, outcome2.completion.reason
        assert set(outcome2.completion.members_completed) == {"leader_pk", "guest_pk"}
        published = store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir)
        assert published == leader_save, "die ORIGINAL empfangene Antwort wurde geerntet, nichts Neues erfunden"


def main() -> int:
    tests = [
        test_ar01_uninterrupted_control_journey_unaffected_by_auto_recovery,
        test_ar02_ar04_admission_pause_after_durable_response_then_fresh_resume_harvests_without_new_turn,
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
