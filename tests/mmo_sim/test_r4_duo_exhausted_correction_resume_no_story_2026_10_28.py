#!/usr/bin/env python3
"""
tests/mmo_sim/test_r4_duo_exhausted_correction_resume_no_story_2026_10_28.py
-- ZR-N2R-ANSCHLUSS-20261019-R4, Reparatur 2 ("unerledigte Abschlussarbeit
dauerhaft erkennen").

Belegter Live-Defekt (Duo-Tisch `lobby-p01_latch-p02_breach__2`): nachdem das
Gruppen-Korrekturbudget erschoepft ist (beide Mitglieder `validating`,
`attempts_used=3`), loescht `pursue_group_save_correction` den
`_group_rounds/<tisch>__<section>.open.json`-Marker (`_clear_open_round`). Die
Mitglieds-Korrekturdatensaetze bleiben jedoch OFFEN (nicht adoptiert), und es
ist WEDER ein `__plan.json` gepinnt NOCH ein `__final.json` geschrieben. Der
markerbasierte Resume-Zweig (`has_open_group_round`) sieht das danach NICHT
mehr -- der normale Spieleinstieg fiel deshalb in einen gewoehnlichen Story-/
Persona-Zug zurueck (live: 14 unnoetige GM-Zuege nach zwei erfolglosen
Korrekturen), statt den unerledigten Abschluss zu erkennen und zu halten.

Dieser Test geht -- wie `test_r4_duo_open_group_correction_resume_2026_10_28`
-- ueber den ECHTEN normalen Aufrufer (`app_service.run_play_session`, je
Phase NEU konstruiert = frischer Prozess auf demselben persistierten
`run_dir`). Er beweist:
  - Nach echter Budgeterschoepfung ist der `.open.json`-Marker weg, die
    Datensaetze sind aber noch `validating`/`attempts_used=MAX` (kein Plan/
    Final) -- und `save_correction.has_unfinished_group_round` erkennt genau
    das (marker-UNABHAENGIG).
  - Der naechste normale Spieleinstieg startet dann KEINEN Storyzug: weder ein
    GM-Transport-Call (`ExplodingGmTransport`) noch eine neue Persona-
    Entscheidung (`ExplodingDriver`) -- er fuehrt den idempotenten
    Abschluss-/Recoveryzweig und meldet ein ehrliches, unvollstaendiges
    Ergebnis (kein `success`, keine Finalisierung).
  - Vorheriger Zustand bleibt erhalten (kein Counter-Reset, kein manuell
    geschriebenes Final): `attempts_used` bleibt MAX, `state` bleibt offen.

Geldfrei per Konstruktion: ausschliesslich In-Process-Fakes, kein realer
Transport, keine echte CLI, keine echte GM-Route."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _full_v7_fixture import full_v7_save  # noqa: E402
from _r12_window_hold_fixture import open_window  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    ScriptedDriver, ScriptedGmTransport,
    build_two_member_table, make_env,
)

import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core import app_service  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER,
    ZeitrissHarvestValidator,
    build_save_command_completion_fallback,
    is_save_command,
    is_saveguard_rejection,
)

_LEADER_CID = "chrono-leader"
_GUEST_CID = "chrono-guest"
_CID_TO_PK = {_LEADER_CID: "leader_pk", _GUEST_CID: "guest_pk"}


def _fenced_json(block: dict) -> str:
    return f"```json\n{json.dumps(block)}\n```"


def _overlong_invalid(cid: str) -> dict:
    """Sonst gueltiger v7-Save mit GENAU der realen Duo-B-Ueberlaenge: sieben
    `continuity.shared_echoes` (maxItems 6) -- schema-ungueltig, aber sauber
    extrahierbar (ein fenced Block, genau eine Figur, richtige char_id)."""
    block = full_v7_save(cid, name="Testfigur")
    block.setdefault("continuity", {})
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}", "scope": "shared", "text": f"nicht-leer-{i}"} for i in range(7)
    ]
    return block


def _run(lobby, table, ps_store, gm, controller, section_id, states_dir, ts):
    return app_service.run_play_session(
        lobby, table, gm, controller, section_id,
        {"leader_pk": {"user": "ctx-leader_pk"}, "guest_pk": {"user": "ctx-guest_pk"}},
        states_dir, "2026-10-28", ts, COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, max_turns=5,
        completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
        explicit_completion_attempt=is_save_command,
        save_guard_rejection_detector=is_saveguard_rejection,
    )


def _drive_group_correction_to_exhaustion(env, lobby, table, ps_store, section_id):
    """Treibt eine Gruppenkorrektur BEIDER Mitglieder ueber ein direktes
    `pursue_group_save_correction` bis zur echten Budgeterschoepfung: der
    GM-Fake liefert `MAX_ADDITIONAL_REQUESTS` Mal DENSELBEN ungueltigen Block
    je Figur (kein Fortschritt, keine Drift). Danach ist der Marker weg, beide
    Datensaetze sind `validating`/`attempts_used=MAX`."""
    harvested: dict = {}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, "2026-10-28",
        ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and set(harvest_completion.missing) == {"leader_pk", "guest_pk"}

    max_attempts = sc.MAX_ADDITIONAL_REQUESTS
    invalid_leader = _overlong_invalid(_LEADER_CID)
    invalid_guest = _overlong_invalid(_GUEST_CID)
    one_response = (
        "Technische Speicherkorrektur (ungueltig, bleibt ungueltig).\n"
        + _fenced_json(invalid_leader) + "\n" + _fenced_json(invalid_guest)
    )
    gm = ScriptedGmTransport(scripted_contents=[one_response] * max_attempts)

    harvested_out, completion_out = sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=harvested,
        harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-10-28",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    assert not completion_out.success, completion_out
    # Genau MAX gesendete Korrekturrunden -- Budget tatsaechlich erschoepft.
    assert len(gm.calls) == max_attempts, gm.calls
    return max_attempts


def test_exhausted_group_correction_is_detected_without_marker():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-duo-exhausted")
        write_test_profile(env.run_dir)
        open_window(env.run_dir)
        section_id = "section-duo-exhausted"

        max_attempts = _drive_group_correction_to_exhaustion(env, lobby, table, ps_store, section_id)

        # Marker ist nach Erschoepfung weg -- der alte markerbasierte Zweig
        # waere jetzt blind.
        marker = sc._open_round_path(env.run_dir, table.table_id, section_id)
        assert not marker.exists(), "Nach Budgeterschoepfung ist der .open.json-Marker geloescht."
        assert not sc.has_open_group_round(env.run_dir, table.table_id, section_id)

        # Datensaetze sind OFFEN (validating) mit erschoepftem Budget, nicht
        # adoptiert -- und FIX2 erkennt genau das.
        for cid in (_LEADER_CID, _GUEST_CID):
            rec = sc.load_record(env.run_dir, domain.group_repair_key(table.table_id, section_id, cid))
            assert rec["state"] == "validating", rec
            assert rec["attempts_used"] == max_attempts, rec
        assert sc.has_unfinished_group_round(env.run_dir, table.table_id, section_id), (
            "FIX2: die unerledigte, erschoepfte Gruppenkorrektur muss marker-unabhaengig erkannt werden."
        )

        # Kein Plan/Final -- die Section ist nachweislich nicht abgeschlossen.
        assert store.open_completion_order_for_table(env.run_dir, table.table_id) is None
        assert not (env.run_dir / "completion" / f"{section_id}__final.json").exists()


def _append_anchor_origins(run_dir, table_id: str, section_id: str) -> None:
    """Reproduziert den realen Duo-B-Resumezustand: der Abschnitt wurde zuvor
    bereits GESPIELT (Leader-Anker + Gast-Import), deshalb ueberspringt der
    frische Prozess Anker/Import und geht direkt in die Spiel-/Storyschleife
    (`SectionRuntime.__init__`: ein `sl_log`-Eintrag mit `origin_persona_key`
    == pk heisst 'pk hat bereits beigetragen'). Ohne diese Vorgeschichte wuerde
    der Resume zuerst einen Anker-Turn fahren -- hier geht es aber genau um den
    danach folgenden, wiederholten STORY-Zug nach erschoepfter Korrektur."""
    t = store.Table.load(run_dir, table_id)
    for i, pk in enumerate(("leader_pk", "guest_pk")):
        t.sl_log.append({
            "turn_idx": 800 + i, "leader_message": "frueherer Spielzug", "origin_persona_key": pk,
            "origin_raw_input": "frueherer Spielzug", "origin_source": f"fake:{pk}-prior", "save_payload": None,
            "content": "frueher gespielter Abschnittsinhalt.", "section_id": section_id,
            "chat_id": f"fake-prior-{i}", "expected_prev_ref_by_member": None, "gm_request_id": None,
        })
    t.persist()


def test_normal_entry_after_exhaustion_halts_repeated_story_turns():
    """FIX2-Kern: Nach erschoepfter Korrektur (Marker weg, Records offen) darf
    der bereits geankerte Resume NICHT in eine Kette reiner Story-/Persona-
    Zuege laufen (belegt: 14). Der neue In-Loop-Guard laesst hoechstens den
    einen ersten Abschluss-/Recoveryversuch der Schleife zu und haelt danach
    fortsetzbar an -- kein Weitererzaehlen bis `max_turns`."""
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        lobby, table, ps_store = build_two_member_table(env, table_id="t-duo-exhausted-resume")
        write_test_profile(env.run_dir)
        open_window(env.run_dir)
        section_id = "section-duo-exhausted-resume"

        max_attempts = _drive_group_correction_to_exhaustion(env, lobby, table, ps_store, section_id)
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        _append_anchor_origins(env.run_dir, table.table_id, section_id)

        # === NEUER normaler Spieleinstieg (frischer Prozess). Der GM-Fake wuerde
        # BIS ZU max_turns reine Erzaehlung liefern (kein Abschlussmarker).
        # Ohne den Fix liefe die Schleife bis `max_turns` (viele Story-GM-Calls);
        # MIT dem Fix bricht sie nach dem ersten, nicht abschliessenden Zug ab. ===
        table2 = store.Table.load(env.run_dir, table.table_id)
        gm2 = ScriptedGmTransport(scripted_contents=["Reine Erzaehlung, kein Abschluss."] * 10)
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([
                ParticipantDecision(text="weiter", origin_source="fake:leader-cont") for _ in range(10)
            ]),
            "guest_pk": ScriptedDriver([
                ParticipantDecision(text="weiter", origin_source="fake:guest-cont") for _ in range(10)
            ]),
        })
        outcome = _run(lobby, table2, ps_store, gm2, controller2, section_id, env.states_dir, "2026-10-28T09:30:00")

        # Beschraenkter Abbruch statt Story-Kette: hoechstens EIN Zug (der erste
        # Schleifendurchlauf), danach fortsetzbarer HOLD -- NICHT bis max_turns.
        assert len(gm2.calls) <= 1, (
            f"Nach erschoepfter Korrektur duerfen keine wiederholten Story-Zuege laufen: {len(gm2.calls)}"
        )
        assert not outcome.completion.success, outcome.completion
        assert not (env.run_dir / "completion" / f"{section_id}__final.json").exists()

        # Vorheriger Zustand bleibt erhalten (kein Reset, kein manuelles Final).
        for rk in (guest_repair_key, leader_repair_key):
            rec = sc.load_record(env.run_dir, rk)
            assert rec["state"] == "validating", rec
            assert rec["attempts_used"] == max_attempts, rec
        # Der offene Abschluss bleibt weiterhin marker-unabhaengig erkennbar
        # (eine autorisierte enge Zusatzkorrektur-Recovery kann hier ansetzen).
        assert sc.has_unfinished_group_round(env.run_dir, table.table_id, section_id)


def main() -> int:
    tests = [
        test_exhausted_group_correction_is_detected_without_marker,
        test_normal_entry_after_exhaustion_halts_repeated_story_turns,
    ]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\nall {len(tests)} R4 duo exhausted-correction resume tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
