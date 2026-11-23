#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r8_c_resume_prev_ref_override_preserved_2026_11_22.py —
ZR-R8-CHARGEN-GRUPPENABSCHLUSS-20261122 Ziel C, Stage3-Zusatzfund (Vera-
Report `vera-stage3-report.md`, Befund 1, Severity "sollte"): der
NICHT-pre_send-Resume-Pfad (`core/runtime.py:run_full_section` findet ueber
`_section_completion_recovery.find_recoverable_entry` einen bereits durabel
empfangenen `!save`-Debrief wieder und ruft `finalize(recoverable["content"],
resume_section_id=section_id, prev_ref_override=recoverable.get(
"expected_prev_ref_by_member"))`, `runtime.py:~1779-1782`, OHNE `pre_send`).
Bleiben nach diesem Resume noch Mitglieder `missing`, reicht `finalize`
(`runtime.py:~973`) seit diesem Fix `prev_ref_override` NEU an
`save_correction.pursue_group_save_correction` durch — vorher fehlte das
dort vollstaendig (Vera-Report). Ohne diese Weiterleitung liest
`store.complete_section` beim finalen Plan-Pin NICHT den durabel VOR der
Pause gebundenen ORIGINAL-Schnappschuss, sondern den beim Abschluss FRISCH
gelesenen (ggf. bereits gedrifteten) Current-Stand — derselbe AR06-Bruch,
den `pursue_pre_send_structural_best_effort`s eigener Vorlaeufer-Fix bereits
fuer den Best-effort-Pfad schloss. Dieser Test belegt das end-to-end fuer
GENAU den hier noch offenen `not pre_send`-Resume+Correction-Fall (bisher
von keinem bestehenden Test dediziert abgedeckt, s. Vera-Report "Eigener
Zusatzfund").

Szenario: Zweier-Tisch, beide Mitglieder mit Erstgeneration (seq=1)
seed-veroeffentlicht (`store.publish_current_save`). Ein `!save`-Debrief
bindet NUR den Leader vollstaendig (der Gast fehlt bewusst im
Debriefinhalt) und wird — ueber den bestehenden
`StopAfterResponseGmTransport`-Helfer, genau wie in
`test_section_completion_resume_ar2_generation_override.py` — unmittelbar
NACH dem durablen `store.submit_to_sl`-Persist, aber VOR `finalize`, durch
einen Admission-Stop unterbrochen. WAEHREND der Pause driftet der GAST auf
eine NEUERE Currentgeneration. Ein neuer Prozess (neue `Table`-Instanz,
neue `SectionRuntime`) findet den unterbrochenen Debrief ueber
`find_recoverable_entry` wieder, uebernimmt dessen
`expected_prev_ref_by_member` (= der ORIGINAL-Schnappschuss VOR der Drift)
und ruft `finalize(...)`. Da der Gast im Debriefinhalt weiterhin fehlt,
greift GENAU der `not pre_send`-Correction-Zweig
(`pursue_group_save_correction`); eine einzige geskriptete Korrekturantwort
liefert einen gueltigen Gast-Export, die Korrektur gelingt, der
Abschluss-Auftrag (`__plan.json`) wird gepinnt.

Assertion: `__plan.json["members"]["guest_pk"]["expected_prev_ref"]` ist
exakt der ORIGINAL-Schnappschuss (identisch zu
`expected_prev_ref_by_member["guest_pk"]`), NICHT die gedriftete
Currentreferenz — UND als direkte Folge erkennt `store._resume_and_harvest`
den Unterschied zur tatsaechlich veroeffentlichten (gedrifteten)
Gastgeneration und HAELT den Abschluss (`success=False`, Grund nennt
"Recovery abgelehnt"), STATT ihn mit der gedrifteten Basis
stillschweigend durchzuwinken. Faellt die Weiterleitung weg (Fail-before,
s. `linus-stage3b-report.md`): `complete_section` liest beim Pin-Moment den
GAST-Eintrag FRISCH (= bereits gedriftet), `expected_prev_ref` entspricht
dann der Drift, `_resume_and_harvest` findet KEINEN Unterschied und laesst
den Abschluss faelschlich `success=True` durchlaufen, OHNE die Drift je zu
pruefen — genau das soll dieser Test rot machen.

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
    COMPLETION_MARKER, ReflectionOnlyDriver, ScriptedDriver, ScriptedGmTransport,
    StopAfterResponseGmTransport, build_two_member_table, clear_lab_stop,
    debrief_with_marker, harvest_extractor, make_env, save_block,
)

import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402


def _fenced_json(block: dict) -> str:
    return f"```json\n{json.dumps(block)}\n```"


def test_resume_not_pre_send_correction_pins_original_prev_ref_not_drifted_current():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-c-resume-override")
        write_test_profile(env.run_dir)
        section_id = "section-c-resume-override"

        # Erstgeneration (seq=1) fuer BEIDE Mitglieder bereits VOR diesem
        # Abschnitt veroeffentlicht (genau wie
        # test_section_completion_resume_ar2_generation_override.py).
        seed_leader = save_block("chrono-leader", wallet=1.0)
        seed_guest = save_block("chrono-guest", wallet=1.0)
        store.publish_current_save(env.run_dir, "leader_pk", seed_leader, ps_store, states_dir=env.states_dir)
        store.publish_current_save(env.run_dir, "guest_pk", seed_guest, ps_store, states_dir=env.states_dir)

        # Debrief bindet NUR den Leader -- der Gast fehlt bewusst im
        # Debriefinhalt, damit der Resume anschliessend GENAU den
        # `not pre_send`-Correction-Zweig (runtime.py:~967-974) erreicht.
        leader_save = save_block("chrono-leader", wallet=2.0)
        debrief = debrief_with_marker({"chrono-leader": leader_save})
        gm1 = StopAfterResponseGmTransport(
            ["SL-Antwort Anker.", "SL-Antwort Gast-Import.", debrief], run_dir=env.run_dir,
            reason="C-Resume-Override: Pause nach Markerantwort (Gast fehlt bewusst im Debrief).",
        )
        leader_driver1 = ScriptedDriver([
            ParticipantDecision(text="Anker.", save_payload=leader_save, origin_source="fake:leader"),
            ParticipantDecision(text="Debrief-Anfrage.", origin_source="fake:leader-debrief"),
        ])
        guest_driver1 = ScriptedDriver([
            ParticipantDecision(text="Gast-Import.", save_payload=seed_guest, origin_source="fake:guest"),
        ])
        controller1 = TableController(
            leader_key="leader_pk", drivers={"leader_pk": leader_driver1, "guest_pk": guest_driver1},
        )
        runtime1 = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm1, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=harvest_extractor,
        )
        outcome1 = runtime1.run_full_section(
            controller1, section_id,
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-11-22", ts="2026-11-22T10:00:00",
        )
        assert not outcome1.completion.success, outcome1.completion
        assert "Admission-Gate blockiert" in (outcome1.completion.reason or ""), outcome1.completion.reason
        assert not store._completion_plan_path(env.run_dir, section_id).exists(), (
            "VOR dem Resume darf noch KEIN Abschluss-Auftrag gepinnt sein -- die Pause muss GENAU "
            "vor finalize() getroffen haben."
        )

        # Der durabel VOR der Pause/Drift gebundene ORIGINAL-Schnappschuss --
        # direkt aus dem persistierten sl_log-Eintrag gelesen, kein eigener
        # Nachbau.
        reloaded_before_drift = store.Table.load(env.run_dir, table.table_id)
        original_snapshot = reloaded_before_drift.sl_log[-1]["expected_prev_ref_by_member"]
        assert original_snapshot is not None and set(original_snapshot.keys()) == {"leader_pk", "guest_pk"}, (
            original_snapshot
        )

        # DRIFT: waehrend der Pause wird fuer guest_pk eine NEUERE
        # Currentgeneration veroeffentlicht -- der durabel VOR dem
        # Pause-Fenster gebundene `expected_prev_ref_by_member` ist jetzt
        # veraltet (exakt das AR06-Szenario).
        drifted_guest_save = save_block("chrono-guest", wallet=999.0)
        store.publish_current_save(env.run_dir, "guest_pk", drifted_guest_save, ps_store, states_dir=env.states_dir)

        clear_lab_stop(env.run_dir)
        table2 = store.Table.load(env.run_dir, table.table_id)

        # Einzige Korrekturantwort: liefert den fehlenden Gast-Export.
        guest_export = save_block("chrono-guest", wallet=2.0)
        gm2 = ScriptedGmTransport(scripted_contents=[
            "Korrekturantwort fuer den fehlenden Gast.\n" + _fenced_json(guest_export),
        ])
        # Der Resume-Zweig (`recoverable is not None`) kehrt SOFORT ueber
        # `finalize(...)` zurueck, OHNE je einen neuen Anker-/Import-/
        # Spielzug-Treiberaufruf -- ReflectionOnlyDriver explodiert bei
        # jeder Nicht-Reflexionsanfrage und deckt damit beide moeglichen
        # Ausgaenge ab (Reflexion wird nur bei vollem Erfolg erreicht).
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ReflectionOnlyDriver("Reflexion Leader (gut gelaufen).", "fake:leader-reflect"),
            "guest_pk": ReflectionOnlyDriver("Reflexion Gast (gut gelaufen).", "fake:guest-reflect"),
        })
        runtime2 = SectionRuntime(
            lobby=lobby, table=table2, gm_transport=gm2, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=harvest_extractor,
        )
        outcome2 = runtime2.run_full_section(
            controller2, section_id,
            contexts_by_persona={"leader_pk": {"user": "ctx"}, "guest_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-11-22", ts="2026-11-22T10:05:00",
        )

        # Genau EIN Korrekturversand fuer den einen fehlenden Gast (kein
        # Anker-/Import-/Weiterspiel-Call -- der Resume hat beide
        # uebersprungen).
        assert len(gm2.calls) == 1, gm2.calls

        plan_path = store._completion_plan_path(env.run_dir, section_id)
        assert plan_path.exists(), "die Korrektur muss einen Abschluss-Auftrag gepinnt haben"
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))

        # DAS ist der eigentliche Beleg: der GEPINNTE `expected_prev_ref`
        # ist fuer BEIDE Mitglieder exakt der ORIGINAL-Schnappschuss --
        # insbesondere fuer guest_pk NICHT die waehrend der Pause
        # gedriftete Currentreferenz (F1/AR06). Ohne die Weiterleitung in
        # runtime.py:~973 wuerde `store.complete_section` hier stattdessen
        # den beim Pin-Moment FRISCH (= bereits gedriftet) gelesenen Stand
        # einsetzen.
        assert plan_data["members"]["leader_pk"]["expected_prev_ref"] == original_snapshot["leader_pk"], (
            plan_data["members"]["leader_pk"]
        )
        assert plan_data["members"]["guest_pk"]["expected_prev_ref"] == original_snapshot["guest_pk"], (
            plan_data["members"]["guest_pk"]
        )
        assert plan_data["members"]["guest_pk"]["expected_prev_ref"] != store.current_save_ref_snapshot(
            table2, ps_store, env.states_dir,
        )["guest_pk"], (
            "der gepinnte Schnappschuss darf NICHT zufaellig mit der gedrifteten Currentreferenz "
            "uebereinstimmen -- sonst waere diese Probe nicht aussagekraeftig."
        )

        # Direkte Folge des korrekt erhaltenen ORIGINAL-Schnappschusses:
        # `_resume_and_harvest` erkennt die Drift des Gasts (gepinntes
        # `expected_prev_ref` != tatsaechlich veroeffentlichter Stand) und
        # HAELT den Abschluss, STATT ihn mit der gedrifteten Basis
        # stillschweigend durchzuwinken.
        assert not outcome2.completion.success, (
            "der Abschluss haette die Gast-Drift erkennen und HALTEN muessen -- ein stilles "
            f"success=True hier ist GENAU der AR06-Bruch: {outcome2.completion}"
        )
        assert "Recovery abgelehnt" in (outcome2.completion.reason or ""), outcome2.completion.reason

        # Der waehrend der Pause gedriftete Gast-Stand bleibt unveraendert
        # veroeffentlicht -- die (schema-gueltige) Korrekturantwort wurde
        # NICHT stillschweigend ueber ihn geschrieben.
        still_published_guest = store.load_current_save(env.run_dir, "guest_pk", ps_store, states_dir=env.states_dir)
        assert still_published_guest == drifted_guest_save, (
            "die waehrend der Pause veroeffentlichte Gastgeneration wurde ueberschrieben -- "
            f"genau der AR06-Bruch: {still_published_guest}"
        )


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
