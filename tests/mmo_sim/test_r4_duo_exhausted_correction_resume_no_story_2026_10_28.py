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
`run_dir`).

R4-STARTFRESH-NACHTRAG (Owner-Vertrag, 2026-10-28/29, `mmo_sim/core/save_
correction.py`-Moduldocstring): der urspruengliche FIX2-Befund oben ("WEDER
ein `__plan.json` gepinnt NOCH ein `__final.json` geschrieben") beschrieb
GENAU den General-Drift, den der Owner-Vertrag jetzt ausdruecklich
ueberschreibt ("kein kuenstlicher Erfolg" war KEIN bindender Vertrag,
sondern eine damals ungeprueft uebernommene Annahme). Das hier verwendete
Exhaustionsszenario (beide Mitglieder liefern ueber mehrere Runden denselben
schema-ungueltigen, aber sauber extrahierbaren, NICHT gedrifteten Kandidaten
-- `_overlong_invalid`, 7 `shared_echoes` gegen `maxItems:6`) ist EXAKT der
Fall, fuer den der Owner-Vertrag jetzt einen best-effort-Abschluss verlangt
(`pursue_group_save_correction`s erschoepfter-Budget-Zweig). Die beiden
Tests unten sind deshalb AKTUALISIERT (nicht geloescht -- die eigentliche
FIX2-Kernaussage "kein wiederholter Storyzug nach Erschoepfung" bleibt
unveraendert gueltig und wird weiterhin geprueft):
  - Nach echter Budgeterschoepfung ist der `.open.json`-Marker weg, BEIDE
    Mitglieder sind jetzt `adopted`/`best_effort=True` (NICHT mehr
    `validating`) -- `__plan.json`/`__final.json` sind jetzt gepinnt/
    geschrieben (best-effort, ehrlich geflaggt), `has_unfinished_group_
    round` meldet deshalb korrekt `False` (der Abschnitt ist nicht mehr
    offen).
  - Ein nachfolgender normaler Spieleinstieg sieht den Abschnitt bereits
    final abgeschlossen und startet KEINEN Storyzug (die eigentliche FIX2-
    Garantie bleibt bestehen, nur die Art des Abschlusses hat sich
    geaendert).
  - `attempts_used` bleibt unveraendert MAX (kein Counter-Reset) -- der
    best-effort-Abschluss aendert NICHTS an der Versuchshistorie.

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
    je Figur (kein Fortschritt, keine Drift).

    R4-STARTFRESH (Owner-Vertrag): dieser ungueltige, aber sauber
    extrahierbare, NICHT gedriftete Block ist jetzt GENAU der Fall, den der
    Owner-Vertrag best-effort abschliesst -- `pursue_group_save_correction`
    liefert deshalb `success=True`, BEIDE Mitglieder sind `adopted`/`best_
    effort=True` (NICHT mehr `validating`), `attempts_used` bleibt
    unveraendert MAX."""
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
    # R4-STARTFRESH: best-effort-Abschluss statt ehrlichem HOLD -- der
    # maximal-konforme (hier: der einzige je beobachtete) Kandidat wird
    # adoptiert, PHASE 1 (`store.complete_section`) ist jetzt erfolgreich.
    assert completion_out.success, completion_out
    # Genau MAX gesendete Korrekturrunden -- Budget tatsaechlich erschoepft
    # (der best-effort-Abschluss aendert NICHTS an der Versuchszahl).
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

        # Marker ist nach Erschoepfung weg -- erwartet, UNVERAENDERT (FIX2).
        marker = sc._open_round_path(env.run_dir, table.table_id, section_id)
        assert not marker.exists(), "Nach Budgeterschoepfung ist der .open.json-Marker geloescht."
        assert not sc.has_open_group_round(env.run_dir, table.table_id, section_id)

        # R4-STARTFRESH: Datensaetze sind jetzt `adopted`/`best_effort=True`
        # mit erschoepftem (unveraendertem) Budget -- NICHT mehr offen.
        for cid in (_LEADER_CID, _GUEST_CID):
            rec = sc.load_record(env.run_dir, domain.group_repair_key(table.table_id, section_id, cid))
            assert rec["state"] == "adopted" and rec.get("best_effort") is True, rec
            assert rec["attempts_used"] == max_attempts, rec
        assert not sc.has_unfinished_group_round(env.run_dir, table.table_id, section_id), (
            "R4-STARTFRESH: nach best-effort-Abschluss ist die Gruppenkorrektur NICHT mehr offen."
        )

        # PHASE 1 ist best-effort erfolgreich -- ein Abschluss-Auftrag ist
        # jetzt gepinnt (PHASE 2/Reflexion steht noch aus, bewusst nicht
        # Teil dieses Tests).
        assert store.open_completion_order_for_table(env.run_dir, table.table_id) == section_id
        plan_data = json.loads(
            (env.run_dir / "completion" / f"{section_id}__plan.json").read_text(encoding="utf-8")
        )
        assert plan_data.get("best_effort") is True, plan_data
        assert not (env.run_dir / "completion" / f"{section_id}__final.json").exists(), (
            "PHASE 2 (Reflexion/Finalize) ist bewusst noch nicht gelaufen -- kein Final ohne sie."
        )


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
    """FIX2-Kern (weiterhin gueltig): Nach erschoepfter Korrektur darf der
    bereits geankerte Resume NICHT in eine Kette reiner Story-/Persona-Zuege
    laufen (belegt: 14 unnoetige GM-Zuege). Mit dem urspruenglichen FIX2
    (Marker weg, Records offen) hielt der In-Loop-Guard danach HOLD; mit
    R4-STARTFRESH (Owner-Vertrag, best-effort Gruppenabschluss) ist PHASE 1
    jetzt bereits best-effort erfolgreich -- der normale Resume erkennt den
    bereits gepinnten Abschluss-Auftrag (`open_completion_order_for_table`)
    und fuehrt NUR noch die ausstehende PHASE 2 (Pflicht-Reflexion/Finalize)
    aus, OHNE jeden neuen Story-/GM-Zug. Beide Varianten erfuellen dieselbe
    Kerngarantie ("kein Weitererzaehlen bis `max_turns`"), nur das Resultat
    (HOLD vs. best-effort-Abschluss) hat sich mit dem Owner-Vertrag
    geaendert."""
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
        # BIS ZU max_turns reine Erzaehlung liefern (kein Abschlussmarker) --
        # wenn der Resume faelschlich in einen normalen Story-/Persona-Zug
        # zurueckfiele, wuerde GENAU dieser Fake das aufdecken. ===
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

        # KEIN einziger neuer Story-/GM-Zug -- der Resume ging direkt in
        # PHASE 2 (Reflexion/Finalize) des bereits best-effort gepinnten
        # Abschluss-Auftrags, nicht in eine Story-Kette.
        assert len(gm2.calls) == 0, (
            f"Nach best-effort-Abschluss duerfen keine neuen Story-Zuege laufen: {len(gm2.calls)}"
        )
        # R4-STARTFRESH: PHASE 2 schliesst den bereits best-effort gepinnten
        # Auftrag jetzt ehrlich ab (kein Fake-DONE -- `best_effort` bleibt
        # im Final sichtbar, s. Assertion unten).
        assert outcome.completion.success, outcome.completion
        final_path = env.run_dir / "completion" / f"{section_id}__final.json"
        assert final_path.exists()
        final_data = json.loads(final_path.read_text(encoding="utf-8"))
        assert final_data.get("best_effort") is True, final_data
        assert set(final_data.get("best_effort_members") or []) == {"leader_pk", "guest_pk"}, final_data

        # Kein Counter-Reset -- die volle Versuchshistorie bleibt erhalten,
        # auch nach dem best-effort-Abschluss.
        for rk in (guest_repair_key, leader_repair_key):
            rec = sc.load_record(env.run_dir, rk)
            assert rec["state"] == "adopted" and rec.get("best_effort") is True, rec
            assert rec["attempts_used"] == max_attempts, rec
        # Der Abschluss ist jetzt vollstaendig final -- keine offene
        # Gruppenkorrektur mehr (marker-unabhaengig).
        assert not sc.has_unfinished_group_round(env.run_dir, table.table_id, section_id)


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
