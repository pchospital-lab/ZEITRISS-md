#!/usr/bin/env python3
"""
tests/mmo_sim/test_section_completion_resume_provenance.py — R12-AUTORECOVERY:
CASES.json AR05 (Herkunft/Leader-Input ist KEINE SL-Antwort), AR06
(Current-/Generation-Drift wird weiterhin erkannt, kein Ueberschreiben), AR11
(unzureichend gebundene/legacy Rohantwort wird NICHT automatisch adoptiert --
kontrollierter Stopp statt erfundener Provenienz).

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
    ScriptedDriver, ScriptedGmTransport, build_two_member_table, debrief_with_marker,
    harvest_extractor, make_env, save_block,
)

import mmo_sim.core._section_completion_recovery as recovery  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.completion_marker import completion_marker_matches  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def test_ar05_leader_message_with_marker_text_is_not_mistaken_for_sl_answer():
    """AR05: der Marker im LEADER-Text (an die SL gesendet, `leader_message`)
    ist KEINE SL-Antwort -- nur `content` (das tatsaechliche SL-Feld) zaehlt.
    `store.submit_to_sl` persistiert beides getrennt; `find_recoverable_entry`
    darf aus einem `leader_message`-Treffer OHNE `content`-Treffer NICHTS
    ableiten."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-ar05")
        gm = ScriptedGmTransport(["Normale SL-Antwort ohne jeden Marker."])
        # Der Leader-Text selbst zitiert den Marker-String (z.B. aus einer
        # frueheren Beispielantwort kopiert) -- die SL antwortet aber ganz
        # normal, OHNE eigenen Marker.
        result = store.submit_to_sl(
            table, "leader_pk", gm, 0, f"Ich zitiere den Marker: {COMPLETION_MARKER} nur als Beispiel.",
            section_id="section-ar05",
            expected_prev_ref_by_member=store.current_save_ref_snapshot(table, ps_store, env.states_dir),
        )
        assert COMPLETION_MARKER not in result["content"]

        reloaded = store.Table.load(env.run_dir, table.table_id)
        entry = reloaded.sl_log[-1]
        assert COMPLETION_MARKER in entry["leader_message"], "Testaufbau: Marker steckt im Leader-Text."
        assert COMPLETION_MARKER not in entry["content"], "Testaufbau: SL-Antwort selbst traegt keinen Marker."

        found, hold_reason = recovery.find_recoverable_entry(
            reloaded.sl_log, "section-ar05", table.table_id, COMPLETION_MARKER, completion_marker_matches,
        )
        assert found is None, "Leader-/Zitat-Text mit Marker darf NIE als empfangene SL-Antwort gelten."
        assert hold_reason is None, (
            "Kein Marker-Treffer im content heisst 'kein Abschlussbeleg', nicht HOLD -- "
            f"der Spielweg muss normal weiterlaufen: {hold_reason!r}"
        )


def test_ar06_generation_drift_between_crash_and_resume_is_still_rejected():
    """AR06: zwischen der durabel gebundenen Original-Erwartung (VOR der
    Markerpruefung erhoben) und der tatsaechlichen Wiederaufnahme wurde eine
    NEUERE Currentversion fuer dasselbe Mitglied veroeffentlicht (hier
    simuliert: ein unabhaengiger `publish_current_save`-Schreibzugriff
    zwischen Prozess 1 und Prozess 2). Automatische Ernte darf diese neuere
    Generation NICHT ueberschreiben -- `_resume_and_harvest`s bestehende
    Drift-Pruefung muss GENAU DESHALB noch feuern, weil der durabel VOR dem
    Crash gebundene Schnappschuss (nicht ein beim Recovery frisch erfundener)
    als `expected_prev_ref` verwendet wird."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-ar06")
        write_test_profile(env.run_dir)

        # Abschnitt 1 (regulaer, unveraendert) -- etabliert eine erste
        # veroeffentlichte Generation (seq=1) fuer leader_pk/guest_pk.
        leader_save_s1 = save_block("chrono-leader", wallet=10.0)
        guest_save_s1 = save_block("chrono-guest", wallet=10.0)
        gm1 = ScriptedGmTransport([
            "SL-Antwort Anker S1.", "SL-Antwort Gast-Import S1.", debrief_with_marker({"chrono-leader": leader_save_s1, "chrono-guest": guest_save_s1}),
        ])
        leader_driver1 = ScriptedDriver([
            ParticipantDecision(text="Anker S1.", save_payload=leader_save_s1, origin_source="fake:leader"),
            ParticipantDecision(text="Debrief S1.", origin_source="fake:leader-debrief"),
            ParticipantDecision(text="Reflexion S1 Leader.", origin_source="fake:leader-reflect"),
        ])
        guest_driver1 = ScriptedDriver([
            ParticipantDecision(text="Gast-Import S1.", save_payload=guest_save_s1, origin_source="fake:guest"),
            ParticipantDecision(text="Reflexion S1 Gast.", origin_source="fake:guest-reflect"),
        ])
        controller1 = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver1, "guest_pk": guest_driver1})
        runtime1 = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm1, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=harvest_extractor,
        )
        outcome1 = runtime1.run_full_section(
            controller1, "section-ar06-s1",
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T09:00:00",
        )
        assert outcome1.completion.success, outcome1.completion.reason

        # Zweiter Tisch (neue Generation, A6/D5-Mechanik: derselbe Tisch-
        # Namensraum nach Abschluss erzeugt automatisch "__2") fuer denselben
        # Mitgliederkreis, zweiter Abschnitt.
        table2, derivation2 = store.create_table_from_offer_log(
            lobby, "t-ar06",
            offer_log_events=[
                {"type": "offer", "id": "o2", "from": "leader_pk", "wants": ["guest_pk"]},
                {"type": "consent", "offer_id": "o2", "from": "guest_pk", "accept": True},
            ],
            chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
        )
        assert table2 is not None and table2.table_id == "t-ar06__2", derivation2

        leader_save_s2 = save_block("chrono-leader", wallet=20.0)
        guest_save_s2 = save_block("chrono-guest", wallet=20.0)
        gm2 = ScriptedGmTransport([debrief_with_marker({"chrono-leader": leader_save_s2, "chrono-guest": guest_save_s2})])
        leader_driver2 = ScriptedDriver([
            ParticipantDecision(text="Anker S2.", save_payload=leader_save_s2, origin_source="fake:leader"),
        ])
        guest_driver2 = ScriptedDriver([
            ParticipantDecision(text="Gast-Import S2.", save_payload=guest_save_s2, origin_source="fake:guest"),
        ])
        controller2 = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver2, "guest_pk": guest_driver2})
        runtime2 = SectionRuntime(
            lobby=lobby, table=table2, gm_transport=gm2, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=harvest_extractor,
        )
        # Der ERSTE Turn (Leader-Anker) ist attach_import_save -- die SL
        # antwortet aber bereits hier (ein Mitglied-Tisch-Ablauf mit
        # sofortigem Debrief ist nicht vorgesehen); wir simulieren den
        # Crash NACH dem Gast-Import-Turn (der bereits die Markerantwort
        # durabel bindet), indem wir `max_turns` so waehlen, dass der Lauf
        # GENAU nach dem Gast-Import (mit Marker) zurueckkehrt -- das ist
        # bereits der reale `finalize`-Call im ununterbrochenen Normalfall.
        # Fuer AR06 wollen wir aber die DRIFT-Situation: die Rohantwort muss
        # durabel sein, OHNE dass `finalize` in DIESEM Prozess schon laeuft.
        # Dazu ersetzen wir `store.complete_section` kurzzeitig durch einen
        # Stub, der NUR beim ersten Aufruf (fuer section-ar06-s2) sofort
        # `_GateBlocked`-artig abbricht, indem wir statt eines echten Crashs
        # den vorhandenen Lab-Stop-Mechanismus nutzen (konsistent mit AR02).
        from _section_completion_resume_fixtures import write_lab_stop
        gm2.turn_orig = gm2.turn

        def _turn_then_stop(turn_idx, user_text, **kwargs):
            res = gm2.turn_orig(turn_idx, user_text, **kwargs)
            write_lab_stop(env.run_dir, "AR06: Pause nach Antwort, um Drift simulieren zu koennen.")
            return res

        gm2.turn = _turn_then_stop

        outcome_paused = runtime2.run_full_section(
            controller2, "section-ar06-s2",
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T09:30:00",
            max_turns=1,
        )
        assert not outcome_paused.completion.success
        assert "Admission-Gate blockiert" in outcome_paused.completion.reason, outcome_paused.completion.reason
        assert store.open_completion_order_for_table(env.run_dir, "t-ar06__2") is None, (
            "VOR der Drift darf noch kein Completion-Plan fuer section-ar06-s2 existieren."
        )

        # DRIFT: ein unabhaengiger Schreibzugriff (z.B. ein spaeter Import)
        # veroeffentlicht fuer leader_pk eine NEUERE Generation, WAEHREND der
        # Prozess pausiert ist -- die durabel VOR dem Crash gebundene
        # Erwartung (seq=1, aus Abschnitt S1) ist jetzt veraltet.
        drifted_block = save_block("chrono-leader", wallet=999.0)
        store.publish_current_save(env.run_dir, "leader_pk", drifted_block, ps_store, states_dir=env.states_dir)

        # Fresh resume: STOP entfernt, Ernte muesste automatisch versucht
        # werden -- MUSS aber wegen der Drift kontrolliert ablehnen, NICHT
        # ueberschreiben.
        from _section_completion_resume_fixtures import clear_lab_stop
        clear_lab_stop(env.run_dir)
        runtime3 = SectionRuntime(
            lobby=lobby, table=store.Table.load(env.run_dir, "t-ar06__2"), gm_transport=ExplodingGmTransport(),
            marker=COMPLETION_MARKER, harvest_validator=ZeitrissHarvestValidator(),
            persona_state_store=ps_store, harvest_extractor=harvest_extractor,
        )
        outcome_resume = runtime3.run_full_section(
            TableController(leader_key="leader_pk", drivers={
                "leader_pk": ExplodingDriver("leader-drift"), "guest_pk": ExplodingDriver("guest-drift"),
            }),
            "section-ar06-s2",
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-10-12", ts="2026-10-12T09:45:00",
        )
        assert not outcome_resume.completion.success, (
            "AR06: Drift MUSS erkannt werden -- kein automatisches Ueberschreiben einer neueren Generation."
        )
        assert "neuere" in outcome_resume.completion.reason or "Vorgaenger" in outcome_resume.completion.reason, (
            outcome_resume.completion.reason
        )
        still_published = store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir)
        assert still_published == drifted_block, "die zwischenzeitlich veroeffentlichte neuere Generation darf NICHT ueberschrieben worden sein."


def test_ar11_legacy_entry_without_durable_snapshot_is_not_auto_adopted():
    """AR11: ein sl_log-Eintrag OHNE den additiven `expected_prev_ref_by_
    member`-Schnappschuss (z.B. aus einer Zeit vor dieser Aenderung, oder
    ein Aufrufer, der die neuen Keyword-Parameter nicht setzt) ist eine
    unzureichend gebundene Rohantwort -- `find_recoverable_entry` liefert
    kontrolliert `None`, KEINE erfundene Provenienz/automatische Adoption."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-ar11")
        gm = ScriptedGmTransport([debrief_with_marker({"chrono-leader": save_block("chrono-leader")})])
        # Alt-Aufrufer-Simulation: `section_id`/`expected_prev_ref_by_member`
        # werden bewusst NICHT gesetzt (Default `None` -- exakt wie ein
        # Aufrufer, der die neuen Keyword-Parameter nicht kennt).
        store.submit_to_sl(table, "leader_pk", gm, 0, "Anker (Legacy-Aufrufer ohne Checkpoint).")
        reloaded = store.Table.load(env.run_dir, table.table_id)
        entry = reloaded.sl_log[-1]
        assert entry.get("expected_prev_ref_by_member") is None
        assert entry.get("section_id") is None, "Legacy-Aufrufer setzt section_id erst gar nicht."

        # Selbst wenn man `section_id` nachtraeglich (synthetisch) auf die
        # gesuchte Section setzen wuerde, bleibt der fehlende Schnappschuss
        # allein ausschlaggebend.
        entry["section_id"] = "section-ar11"
        found, hold_reason = recovery.find_recoverable_entry(
            [entry], "section-ar11", table.table_id, COMPLETION_MARKER, completion_marker_matches,
        )
        assert found is None, "Ohne durablen Original-Schnappschuss darf NICHTS automatisch adoptiert werden."
        # AR2 (Teil A/C): ein BEKANNTER Marker-/Abschlussbeleg mit fehlender
        # Bindung ist ein kontrollierter HOLD, kein blosses "kein Beleg" --
        # `find_recoverable_entry` liefert jetzt explizit einen Grund statt
        # eines reinen `None`-Freibriefs (vorher nicht unterscheidbar vom
        # "gar kein Eintrag"-Fall).
        assert hold_reason is not None, "Fehlender Schnappschuss muss als expliziter HOLD-Grund zurueckkommen."
        assert "Schnappschuss" in hold_reason or "snapshot" in hold_reason.lower(), hold_reason


def main() -> int:
    tests = [
        test_ar05_leader_message_with_marker_text_is_not_mistaken_for_sl_answer,
        test_ar06_generation_drift_between_crash_and_resume_is_still_rejected,
        test_ar11_legacy_entry_without_durable_snapshot_is_not_auto_adopted,
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
