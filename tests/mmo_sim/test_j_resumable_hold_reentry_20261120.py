#!/usr/bin/env python3
"""
tests/mmo_sim/test_j_resumable_hold_reentry_20261120.py — ZR-R8-LIVESYNC-
PALIMPSEST-20261119-R1, Stage J, Lauf 2 (Re-Entry-Fix 20261120).

Belegter Live-Defekt (s. `run/ledger.md` Stage J Nachtrag "PRAEZISE
URSACHE"): der vorhandene Best-effort-Adopt (`resume_hold_via_structural_
best_effort`/`resume_hold_via_transport_error_best_effort`,
`save_correction.py:2049ff`) ist fuer einen TERMINALEN Entry-HOLD-
Gruppenrecord mit adoptierbarem `best_candidate_block` erreichbar, SOBALD
`pursue_group_save_correction` erneut aufgerufen wird -- aber der
Runtime-Re-Entry (`core/runtime.py:1405-1408`) zuendet NUR bei
`save_correction.has_unfinished_group_round(...)` (matcht ausschliesslich
die drei OFFENEN Zwischenzustaende, Docstring: "terminale Zustaende
zaehlen NICHT als offen"). Ein reiner Terminal-HOLD wird deshalb vom
normalen Fortsetzen NIE erneut in `pursue` getragen -- der Adopt bleibt
unerreichbar, der Save bleibt faelschlich HOLD.

Fix (additiv, guard-erhaltend): ein neues, rein lesendes drittes Praedikat
`save_correction.has_resumable_group_hold(...)` bildet EXAKT dieselben
Guards der beiden bestehenden Adopt-Funktionen 1:1 nach (KEINE
Faktorisierung, 0 Deletions an den bestehenden, unveraendert getesteten
Adopt-Funktionen) und erweitert das Runtime-Gate additiv (`... or
has_resumable_group_hold(...)`).

Treibt den ECHTEN Caller (`core.runtime.SectionRuntime.run_full_section`
ueber `core.app_service.run_play_session`, derselbe 1405-Re-Entry) --
EIN direkter Helfer-Test allein genuegt NICHT (Flo-Vorgabe). Setup ist
ein SOLO-Tisch (1 Mitglied) -- entspricht GENAU der realen M8-Form
(`run/preserve/.../__11`-Record, `missing=[pk]` singular, dieselbe Figur
ist Leader UND das einzige Gruppenmitglied).

Fail-before-Beleg: `git stash` (nur der additive Fix-Diff dieser Stage,
NICHT diese Testdatei) VOR einem Lauf dieser Datei macht
`test_j2_real_caller_reenters_and_adopts_without_new_requests`
fehlschlagen (der echte Caller erreicht den Adopt nicht, Record bleibt
`hold`, `adopted_block` bleibt `None`) -- s. Integrator-Report fuer den
belegten Stash-Lauf-Output.

Geldfrei per Konstruktion: ausschliesslich In-Process-Fakes (kein echter
Transport, keine echten HTTP-Requests). Pure Python, nur `assert`, echter
Exitcode -- gleiches Muster wie die bestehende Suite."""
from __future__ import annotations

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
from _r12_window_hold_fixture import open_window  # noqa: E402
from _section_completion_resume_fixtures import (  # noqa: E402
    ExplodingGmTransport, ScriptedDriver, ScriptedGmTransport,
    make_env, make_ps_store, seed_persona_state,
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
    ZeitrissTableSizePolicy,
    build_save_command_completion_fallback,
    is_save_command,
    is_saveguard_rejection,
)

_LEADER_CID = "chrono-leader"
_CID_TO_PK = {_LEADER_CID: "leader_pk"}
_TODAY = "2026-11-20"


def _fenced_json(block: dict) -> str:
    import json
    return f"```json\n{json.dumps(block)}\n```"


def _overcap_only(cid: str, name: str = "Leader") -> dict:
    """Reine Cap-Ueberlauf-Form (3 `maxItems`-Fehler, KEINE Bindungs-/Typ-/
    Identitaetsfehler) -- analog zur echten M8-`best_candidate_block`-Form
    (s. `test_i_m7_transport_error_best_effort_20261120.py`s identischer
    Helfer)."""
    block = full_v7_save(cid, name=name)
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}", "scope": "campaign", "text": f"erinnerung-{i}"} for i in range(8)
    ]
    block["arc"]["hooks"] = [{"text": f"hook-{i}"} for i in range(8)]
    block["arc"]["questions"] = [f"frage-{i}" for i in range(9)]
    return block


def _build_solo_table(root: Path, table_id: str):
    """Ein-Mitglied-Tisch -- entspricht GENAU der realen M8-Form (derselbe
    Chrononaut ist Leader UND das einzige Gruppenmitglied, `missing=[pk]`
    singular, s. `run/ledger.md` Stage J Nachtrag)."""
    env = make_env(root)
    schema_path = env.run_dir.parent / "schema.json"
    ps_store = make_ps_store(schema_path)
    seed_persona_state(ps_store, env.states_dir, "leader_pk", _LEADER_CID)

    lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[{"type": "offer", "id": "o1", "from": "leader_pk", "wants": []}],
        chrononaut_ids={"leader_pk": _LEADER_CID},
    )
    assert table is not None, f"Solo-Tisch haette entstehen muessen: {derivation}"
    write_test_profile(env.run_dir)
    open_window(env.run_dir)
    return env, lobby, table, ps_store


def _drive_leader_into_entry_hold_drift(env, lobby, table, ps_store, section_id: str):
    """Reproduziert den realen `__11`-Fall: ein terminaler Entry-HOLD mit
    `last_reason="unjustified_semantic_drift"`, `adopted_block=None`, einem
    rein cap-ueberlangen `best_candidate_block` (dem Originalentwurf VOR
    der gedrifteten Korrekturantwort, P2-FIX-Registrierung), KEINEM
    `.open.json`-Marker, KEINEM gepinnten Plan -- ueber den ECHTEN Aufrufer
    `pursue_group_save_correction` (kein manuelles Datensatz-Seeding)."""
    leader_old = _overcap_only(_LEADER_CID)
    harvested = {"leader_pk": leader_old}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, _TODAY,
        ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and harvest_completion.missing == ["leader_pk"], harvest_completion

    drifted = _overcap_only(_LEADER_CID)
    drifted["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}-neu", "scope": "campaign", "text": f"erinnerung-{i}-neu"} for i in range(6)
    ]
    drifted["arc"]["hooks"][0]["text"] = "ausserhalb-des-korrekturauftrags-umformuliert"
    gm = ScriptedGmTransport(scripted_contents=[_fenced_json(drifted)])
    harvested_out, completion_out = sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=env.states_dir, today=_TODAY,
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    assert not completion_out.success, completion_out

    repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
    record = sc.load_record(env.run_dir, repair_key)
    assert record["state"] == "hold" and record["last_reason"] == "unjustified_semantic_drift", record
    assert record.get("adopted_block") is None, record
    assert record.get("best_candidate_block") == leader_old, record
    assert sc.has_residual_structural_cap_overflow(record["best_candidate_block"], _LEADER_CID), (
        "Vorbedingung: der gebundene Originalentwurf darf NUR noch den Cap-Ueberlauf tragen."
    )
    # Pflicht-Setup (Briefing): KEIN .open.json, KEIN gepinnter Plan.
    assert not sc._open_round_path(env.run_dir, table.table_id, section_id).exists()
    assert store.open_completion_order_for_table(env.run_dir, table.table_id) is None
    return leader_old, repair_key


def _append_leader_anchor_origin(run_dir, table_id: str, section_id: str) -> None:
    """Reproduziert den realen Resumezustand: der Leader hat den Abschnitt
    bereits geankert (frueherer Prozess) -- der frische Prozess ueberspringt
    Anker/Import und geht direkt in die Spiel-/Storyschleife (dieselbe
    `_leader_anchored`-Ableitung wie der bestehende R4-Sibling-Test, s.
    `test_r4_duo_exhausted_correction_resume_no_story_2026_10_28.py`s
    `_append_anchor_origins`)."""
    t = store.Table.load(run_dir, table_id)
    t.sl_log.append({
        "turn_idx": 800, "leader_message": "frueherer Spielzug", "origin_persona_key": "leader_pk",
        "origin_raw_input": "frueherer Spielzug", "origin_source": "fake:leader-prior", "save_payload": None,
        "content": "frueher gespielter Abschnittsinhalt.", "section_id": section_id,
        "chat_id": "fake-prior-0", "expected_prev_ref_by_member": None, "gm_request_id": None,
    })
    t.persist()


def _run_section(lobby, table, ps_store, gm, controller, section_id, states_dir, ts, max_turns=3):
    return app_service.run_play_session(
        lobby, table, gm, controller, section_id,
        {"leader_pk": {"user": "ctx-leader_pk"}},
        states_dir, _TODAY, ts, COMPLETION_MARKER, ZeitrissHarvestValidator(),
        ps_store, zeitriss_saves.harvest_from_debrief, max_turns=max_turns,
        completion_fallback=build_save_command_completion_fallback(table, zeitriss_saves.harvest_from_debrief),
        explicit_completion_attempt=is_save_command,
        save_guard_rejection_detector=is_saveguard_rejection,
    )


# ---------------------------------------------------------------------------
# (1) Praedikat erkennt den adoptierbaren Drift-HOLD (direkter Cross-Check
#     gegen die tatsaechliche Adoption -- kein Spiegel-Drift).
# ---------------------------------------------------------------------------

def test_j2_predicate_true_for_adoptable_drift_hold_and_cross_checks_real_adopt():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j2-case1")
        section_id = "section-j2-case1"
        leader_old, repair_key = _drive_leader_into_entry_hold_drift(env, lobby, table, ps_store, section_id)

        assert sc.has_resumable_group_hold(env.run_dir, table.table_id, section_id), (
            "ein terminaler Drift-HOLD mit adoptierbarem best_candidate_block muss True liefern."
        )
        # Rein lesend -- Datensatz bleibt UNVERAENDERT nach dem Praedikat-Check.
        assert sc.load_record(env.run_dir, repair_key)["state"] == "hold"

        # Cross-Check: GENAU das Praedikat-Ergebnis muss der tatsaechlichen
        # Adoption entsprechen (dieselben Guards, kein Spiegel-Drift).
        resumed = sc.resume_hold_via_structural_best_effort(
            env.run_dir, repair_key, char_id=_LEADER_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed is not None and resumed["state"] == "adopted" and resumed.get("best_effort") is True
        assert resumed["adopted_block"] == leader_old

        # Nach der Adoption muss das Praedikat jetzt False liefern (Gegenfall c).
        assert not sc.has_resumable_group_hold(env.run_dir, table.table_id, section_id), (
            "ein bereits adoptierter Datensatz darf NICHT erneut als resumable gemeldet werden."
        )


# ---------------------------------------------------------------------------
# (2) Praedikat erkennt auch den Stage-I-transport_error-Fall (zweiter
#     anerkannter Recovery-Fall, GLEICHE Guard-Wiederverwendung).
# ---------------------------------------------------------------------------

class _RaisingGmTransport:
    """M7-Originalfallform (s. `test_i_m7_transport_error_best_effort_
    20261120.py`s identischer Helfer): jeder `.turn()`-Aufruf wirft
    dieselbe Ausnahme wie ein echter client-seitiger Transport-Timeout."""

    def __init__(self):
        self.calls: list[dict] = []
        self.output_limit_tokens = None

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        raise TimeoutError("timed out")


def test_j2_predicate_recognizes_transport_error_hold_too():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j2-case2")
        section_id = "section-j2-case2"
        leader_old = _overcap_only(_LEADER_CID)
        harvested = {"leader_pk": leader_old}
        harvest_completion = store.complete_section(
            lobby, table, section_id, harvested, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion.success and harvest_completion.missing == ["leader_pk"]
        gm = _RaisingGmTransport()
        sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=_TODAY,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        record = sc.load_record(env.run_dir, repair_key)
        assert record["state"] == "hold" and record["last_reason"].startswith("transport_error:"), record

        assert sc.has_resumable_group_hold(env.run_dir, table.table_id, section_id), (
            "ein transport_error-HOLD mit adoptierbarem best_candidate_block muss ebenfalls True liefern."
        )
        resumed = sc.resume_hold_via_transport_error_best_effort(
            env.run_dir, repair_key, char_id=_LEADER_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed is not None and resumed["state"] == "adopted"


# ---------------------------------------------------------------------------
# (3) Gegenfaelle bleiben gesperrt: falsche Bindung, kein Kandidat,
#     Bindungsfehler statt reinem Cap-Ueberlauf.
# ---------------------------------------------------------------------------

def test_j2_predicate_rejects_wrong_table_or_section_binding():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j2-case3")
        section_id = "section-j2-case3"
        _drive_leader_into_entry_hold_drift(env, lobby, table, ps_store, section_id)

        assert not sc.has_resumable_group_hold(env.run_dir, table.table_id, "section-FREMD"), (
            "falsche section_id darf NICHT den Record einer anderen Section matchen."
        )
        assert not sc.has_resumable_group_hold(env.run_dir, "t-FREMDER-TISCH", section_id), (
            "falsche table_id darf NICHT den Record eines anderen Tisches matchen."
        )
        # Der echte Record bleibt davon unberuehrt weiterhin resumable.
        assert sc.has_resumable_group_hold(env.run_dir, table.table_id, section_id)


def test_j2_predicate_rejects_hold_without_best_candidate():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j2-case4")
        section_id = "section-j2-case4"
        repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        sc.load_or_init_record(
            env.run_dir, repair_key, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        sc.mark_hold(env.run_dir, repair_key, reason="unjustified_semantic_drift")
        record = sc.load_record(env.run_dir, repair_key)
        assert record["state"] == "hold" and record.get("best_candidate_block") is None

        assert not sc.has_resumable_group_hold(env.run_dir, table.table_id, section_id), (
            "ein terminaler HOLD OHNE best_candidate_block darf NIE als resumable gemeldet werden."
        )


def test_j2_predicate_rejects_candidate_with_binding_error_not_just_cap_overflow():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j2-case5")
        section_id = "section-j2-case5"
        repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        sc.load_or_init_record(
            env.run_dir, repair_key, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        # Cap-Ueberlauf PLUS eine falsche char_id-Bindung (fremde Figur) --
        # has_residual_structural_cap_overflow haertet darauf ab (binding_
        # errors), s. dessen Docstring "HAERTUNG".
        mis_bound = _overcap_only("chrono-FREMD")
        sc.update_best_candidate(env.run_dir, repair_key, block=mis_bound, error_count=99)
        sc.mark_hold(env.run_dir, repair_key, reason="unjustified_semantic_drift")

        assert not sc.has_residual_structural_cap_overflow(mis_bound, _LEADER_CID), (
            "Vorbedingung: ein falsch gebundener Kandidat darf die Cap-Ueberlauf-Pruefung nicht bestehen."
        )
        assert not sc.has_resumable_group_hold(env.run_dir, table.table_id, section_id), (
            "ein Kandidat mit Bindungsfehler darf NICHT best-effort-faehig gemeldet werden, "
            "selbst wenn er GLEICHZEITIG cap-ueberlang ist."
        )


def test_j2_predicate_rejects_already_adopted_record():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j2-case6")
        section_id = "section-j2-case6"
        repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        sc.load_or_init_record(
            env.run_dir, repair_key, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        candidate = _overcap_only(_LEADER_CID)
        sc.update_best_candidate(env.run_dir, repair_key, block=candidate, error_count=3)
        sc.mark_hold(env.run_dir, repair_key, reason="unjustified_semantic_drift")
        sc.mark_adopted(env.run_dir, repair_key, adopted_block=candidate, best_effort=True)

        assert not sc.has_resumable_group_hold(env.run_dir, table.table_id, section_id), (
            "ein bereits adoptierter Datensatz (state=adopted) darf NIE erneut als resumable gemeldet werden "
            "-- KEINE Doppel-Adoption/-Buchung."
        )


# ---------------------------------------------------------------------------
# (4) Der ECHTE Caller: run_full_section/der 1405-Re-Entry adoptiert den
#     Drift-HOLD OHNE neuen GM-/Korrektur-Request. Fail-before (git stash
#     des Fix-Diffs): dieser Test schlaegt fehl -- der echte Caller
#     erreicht den Adopt NICHT, Record bleibt hold, adopted_block bleibt
#     None (s. Integrator-Report fuer den belegten Stash-Lauf-Output).
# ---------------------------------------------------------------------------

def test_j2_real_caller_reenters_and_adopts_without_new_requests():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build_solo_table(Path(td), "t-j2-case7")
        section_id = "section-j2-case7"
        leader_old, repair_key = _drive_leader_into_entry_hold_drift(env, lobby, table, ps_store, section_id)
        record_before_resume = sc.load_record(env.run_dir, repair_key)
        requests_dir = env.run_dir / "requests"
        requests_before = sorted(p.name for p in requests_dir.glob("*.json")) if requests_dir.is_dir() else []

        _append_leader_anchor_origin(env.run_dir, table.table_id, section_id)
        table2 = store.Table.load(env.run_dir, table.table_id)

        gm_resume = ScriptedGmTransport(scripted_contents=["Reine Erzaehlung, kein Abschluss."])
        controller2 = TableController(leader_key="leader_pk", drivers={
            "leader_pk": ScriptedDriver([
                ParticipantDecision(text="weiter", origin_source="fake:leader-cont") for _ in range(4)
            ]),
        })
        outcome = _run_section(
            lobby, table2, ps_store, gm_resume, controller2, section_id, env.states_dir, "2026-11-20T09:30:00",
            max_turns=3,
        )

        # Der echte 1405-Re-Entry hat den Adopt erreicht -- Record ist jetzt
        # adoptiert, der best-effort-Replay war erfolgreich.
        assert outcome.completion.success, (
            f"der echte Re-Entry haette den Drift-HOLD best-effort abschliessen muessen: {outcome.completion}"
        )
        record_after = sc.load_record(env.run_dir, repair_key)
        assert record_after["state"] == "adopted" and record_after.get("best_effort") is True, record_after
        assert record_after["adopted_block"] == leader_old, record_after

        # Lauf 3 (Entry-Recovery-Fix 20261120): das dritte Entry-Gate (s.
        # `runtime.py run_full_section`, VOR dem Leader-Anker) adoptiert den
        # member-bound resumable HOLD JETZT bereits VOR jedem Erzaehlzug --
        # GENAU NULL GM-/Korrektur-Calls (nicht mehr der eine legitime
        # Fortsetzungszug aus Lauf 2, der hier nie mehr erreicht wird). Die
        # Wiederaufnahme SELBST sendet nichts (HOLD-Mitglied wird im
        # else-Zweig IMMER geskippt, kein begin_attempt/Send).
        assert len(gm_resume.calls) == 0, (
            f"die Lauf-3-Entry-Recovery darf GAR KEINEN GM-/Korrektur-Call ausloesen: {gm_resume.calls}"
        )
        assert record_after["attempts_used"] == record_before_resume["attempts_used"], (
            "best-effort-Adopt darf den Versuchszaehler NICHT veraendern (kein neuer Send)."
        )
        # Neue Request-Dateien DUERFEN entstehen (der eine legitime
        # Fortsetzungsturn + die Pflicht-Reflexion reservieren je einen
        # eigenen Request, s. oben) -- aber KEINE davon darf eine neue
        # `save_correction_group`-Korrektursendung sein (role==ROLE_GROUP,
        # s. `pursue_group_save_correction`s `send_correction_turn`-Weg).
        import json as _json
        requests_after = sorted(p.name for p in requests_dir.glob("*.json")) if requests_dir.is_dir() else []
        new_request_names = sorted(set(requests_after) - set(requests_before))
        new_correction_requests = [
            name for name in new_request_names
            if _json.loads((requests_dir / name).read_text(encoding="utf-8")).get("role") == sc.ROLE_GROUP
        ]
        assert new_correction_requests == [], (
            f"keine neue save_correction_group-Request erwartet: {new_correction_requests} "
            f"(alle neuen Requests: {new_request_names})"
        )

        final_path = env.run_dir / "completion" / f"{section_id}__final.json"
        assert final_path.exists(), "PHASE 2 (Reflexion/Finalize) haette den best-effort-Abschluss abschliessen muessen."
        import json
        final_data = json.loads(final_path.read_text(encoding="utf-8"))
        assert final_data.get("best_effort") is True, final_data
        assert final_data.get("best_effort_members") == ["leader_pk"], final_data

        # --- Idempotenz / kein Doppelspiel: ein zweiter Re-Entry (simulierter
        # Neustart) adoptiert nicht erneut und bucht nichts doppelt. ---
        assert not sc.has_resumable_group_hold(env.run_dir, table.table_id, section_id), (
            "nach erfolgreicher Adoption darf das Praedikat NICHT mehr True liefern."
        )
        second_resume_attempt = sc.resume_hold_via_structural_best_effort(
            env.run_dir, repair_key, char_id=_LEADER_CID, table_id=table.table_id, section_id=section_id,
        )
        assert second_resume_attempt is None, (
            f"ein bereits adoptierter Datensatz darf NICHT erneut resumed werden: {second_resume_attempt}"
        )
        record_after_second_attempt = sc.load_record(env.run_dir, repair_key)
        assert record_after_second_attempt == record_after, (
            "ein No-op-Resume-Versuch (bereits adoptiert) darf den Datensatz NICHT veraendern "
            "(kein zweiter Write, keine Doppelbuchung)."
        )
        # Ein erneuter, schon abgeschlossener complete_section-Aufruf (zweiter
        # Prozess/Poll derselben Section) ist idempotent erfolgreich, OHNE
        # jeden neuen Korrektur-Versuch (pursue wird dafuer gar nicht mehr
        # erreicht -- `final_path.exists()` greift bereits in `complete_
        # section` selbst).
        idempotent_completion = store.complete_section(
            lobby, table2, section_id, {}, env.states_dir, _TODAY,
            ZeitrissHarvestValidator(), ps_store,
        )
        assert idempotent_completion.success and idempotent_completion.already_completed, idempotent_completion
        assert sc.load_record(env.run_dir, repair_key) == record_after, (
            "ein idempotenter Re-Poll nach Finalisierung darf den Korrekturdatensatz NICHT veraendern."
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
