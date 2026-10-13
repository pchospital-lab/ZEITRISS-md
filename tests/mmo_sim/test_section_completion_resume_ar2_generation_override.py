#!/usr/bin/env python3
"""
tests/mmo_sim/test_section_completion_resume_ar2_generation_override.py —
AR2 Teil B (01_ABSCHLUSSVERTRAG.md, review-evidence/GENERATION-OBSERVATIONS.json):
vollstaendige Originalgeneration ODER HOLD -- ein `prev_ref_override`, der
nicht ALLE damaligen Mitglieder bindet (fehlender Memberkey ODER eine leere
Map bei tatsaechlich vorhandenen Mitgliedern), darf NIE durch den beim
Recovery frisch gelesenen aktuellen Stand ersetzt werden (`core/store.py:
complete_section`). Reproduziert exakt die drei Faelle aus
GENERATION-OBSERVATIONS.json (`intact_drift_control`, `missing_leader_ref`,
`empty_all_refs`) -- die ersten zwei sind bereits durch den bestehenden
`test_section_completion_resume_resume_provenance.py:test_ar06_...`
abgedeckt (intakte Map, Drift korrekt erkannt); hier zusaetzlich die beiden
REGRESSIONSFAELLE, in denen das Original ueberschrieb (Teilmap/leere Map).

Pure Python, nur `assert`, echter Exitcode, kein pytest."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _section_completion_resume_fixtures import (  # noqa: E402
    COMPLETION_MARKER, ExplodingDriver, ExplodingGmTransport, ScriptedDriver,
    StopAfterResponseGmTransport, build_two_member_table, clear_lab_stop,
    debrief_with_marker, harvest_extractor, make_env, save_block,
)

import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def _case(case_name: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id=f"t-ar2-gen-{case_name}")
        write_test_profile(env.run_dir)
        section_id = f"section-ar2-gen-{case_name}"

        # Erste Generation (seq=1) fuer BEIDE Mitglieder bereits VOR diesem
        # Abschnitt veroeffentlicht -- genau wie review-evidence/
        # probe_generation.py's Vorbereitung.
        seed_leader = save_block("chrono-leader", wallet=1.0)
        seed_guest = save_block("chrono-guest", wallet=1.0)
        store.publish_current_save(env.run_dir, "leader_pk", seed_leader, ps_store, states_dir=env.states_dir)
        store.publish_current_save(env.run_dir, "guest_pk", seed_guest, ps_store, states_dir=env.states_dir)

        leader_save = save_block("chrono-leader", wallet=2.0)
        guest_save = save_block("chrono-guest", wallet=2.0)
        debrief = debrief_with_marker({"chrono-leader": leader_save, "chrono-guest": guest_save})
        gm = StopAfterResponseGmTransport(
            ["SL-Antwort Anker.", "SL-Antwort Gast-Import.", debrief], run_dir=env.run_dir,
            reason="AR2-generation-override: Pause nach Markerantwort.",
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
        outcome1 = runtime.run_full_section(
            controller, section_id,
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-10-13", ts="2026-10-13T07:00:00",
        )
        assert not outcome1.completion.success
        assert "Admission-Gate blockiert" in outcome1.completion.reason, outcome1.completion.reason

        # DRIFT: waehrend der Pause wird fuer leader_pk eine NEUERE
        # Currentgeneration veroeffentlicht -- das durabel VOR dem Pause-
        # Fenster gebundene expected_prev_ref_by_member (seq=1) ist jetzt
        # veraltet. Automatische Ernte darf diese neuere Fassung NIE
        # ueberschreiben, egal wie der Checkpoint-Override aussieht.
        drifted_leader_save = save_block("chrono-leader", wallet=999.0)
        store.publish_current_save(env.run_dir, "leader_pk", drifted_leader_save, ps_store, states_dir=env.states_dir)

        if case_name in ("missing_leader_ref", "empty_all_refs"):
            import json
            table_path = env.run_dir / "tables" / f"{table.table_id}.json"
            table_data = json.loads(table_path.read_text(encoding="utf-8"))
            assert len(table_data["sl_log"]) == 3
            ref_map = table_data["sl_log"][-1]["expected_prev_ref_by_member"]
            assert set(ref_map.keys()) == {"leader_pk", "guest_pk"}
            if case_name == "missing_leader_ref":
                ref_map.pop("leader_pk")
            else:
                table_data["sl_log"][-1]["expected_prev_ref_by_member"] = {}
            table_path.write_text(json.dumps(table_data, ensure_ascii=False), encoding="utf-8")
        elif case_name != "intact_drift_control":
            raise AssertionError(f"unbekannter Fall: {case_name}")

        clear_lab_stop(env.run_dir)
        reloaded = store.Table.load(env.run_dir, table.table_id)
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
        assert not outcome2.completion.success, (
            f"AR2 Teil B: Fall {case_name!r} MUSS die Drift erkennen und HOLDen, NIEMALS "
            f"mit der aelteren Antwort ueberschreiben -- reason={outcome2.completion.reason!r}"
        )
        still_published = store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir)
        assert still_published == drifted_leader_save, (
            f"Fall {case_name!r}: die waehrend der Pause veroeffentlichte NEUERE Generation "
            "wurde ueberschrieben -- genau der AR06-Bruch aus GENERATION-OBSERVATIONS.json."
        )
        if case_name in ("missing_leader_ref", "empty_all_refs"):
            # AR2 Teil B: ein UNVOLLSTAENDIGER/defekter Override wird VOR
            # jeder Plan-Pinnung abgelehnt -- anders als `intact_drift_
            # control` (vollstaendiger Override, Drift zeigt sich erst in
            # `_resume_and_harvest`, ein Plan ist dort bereits laut
            # bestehendem, unveraendertem Vertrag eine committete
            # Entscheidung, s. `test_ar06_...`).
            assert store.open_completion_order_for_table(env.run_dir, table.table_id) is None, (
                f"Fall {case_name!r}: ein unvollstaendiger Checkpoint-Override darf NIE einen "
                "Completion-Plan pinnen."
            )


def main() -> int:
    cases = ["intact_drift_control", "missing_leader_ref", "empty_all_refs"]
    failed = 0
    for name in cases:
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
    print(f"\n{len(cases) - failed}/{len(cases)} Faelle bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
