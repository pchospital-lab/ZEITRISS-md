#!/usr/bin/env python3
"""
tests/mmo_sim/test_zr_r9_pr3316_f2r_hq_policy_runtime_resume_2026_11_23.py —
ZR-R9-PR3316-HQ-RESUME-NACHZUG-20261123, Befund F2-R (01_REVIEW.txt
Abschnitt 3/5): die aktive PRE-SEND-HQ-Pflicht (`core/runtime.py:
pre_send_active_leader_authority`, `require_hq=True` an `save_correction.
pursue_group_save_correction`) ueberlebt den tatsaechlichen Runtime-Resume
NICHT. Alle drei Resume-Gates in `SectionRuntime.run_full_section`
(gepinnter Plan, `has_open_group_round`, `has_resumable_group_hold`) rufen
`finalize("", resume_section_id=...)` auf, das ueber den normalen `not
pre_send`-Nachforderweg (`runtime.py` ~Z.967) `pursue_group_save_correction`
OHNE `require_hq` aufruft (Default `False`). Ein beim urspruenglichen
PRE-SEND-Auftrag verbotener Nicht-HQ-Gast (schema-/bindungsvalider
mode=core-Block) konnte dadurch nach Unterbrechung + Runtime-Resume
adoptiert und veroeffentlicht werden -- belegt durch
`offline/repro_hq_policy_resume.py`/`ROOT-RESULT.json` im Nachreview-Paket.

Nachzug (additiv, keyword-only, Default `False`/`None`, symmetrisch zum
bereits gemergten F1-Fix `expected_prev_ref_by_member`): `_write_open_round`
und `load_or_init_record` binden additiv `require_hq` durabel in Marker
bzw. Mitgliedsrecord (NUR bei Erstanlage persistiert); `pursue_group_save_
correction`s Eintritt restauriert `require_hq` aus dieser Bindung, BEVOR
die while-Schleife laeuft, wenn der hereingereichte Wert `False` ist.

Treibt den ECHTEN Runtime-Einstieg (`core.app_service.run_play_session` ->
`core.runtime.SectionRuntime.run_full_section` -> `finalize("",
resume_section_id=...)`) fuer den Resume -- EIN direkter Helfer-Aufruf
allein genuegt NICHT (Flo-Vorgabe/Briefing). Der Resume-Pfad uebergibt
`require_hq` NICHT manuell; ein Monkeypatch auf `save_correction.pursue_
group_save_correction` belegt zusaetzlich EMPIRISCH, dass der tatsaechlich
hereingereichte Wert `False` war und erst die Bindung ihn restauriert.

Pflichtfaelle (Briefing):
  1. Kernfall -- Drei-Mitglieder-PRE-SEND-Korrektur (`require_hq=True`,
     Marker+Record gebunden) wird NACH Marker-/Record-Write unterbrochen
     (W49-A-Crash-Muster: Marker+Record bereits durabel, KEIN Versand
     erfolgt); echter Runtime-Resume OHNE manuelles `require_hq`: der
     schema-/bindungsvalide Nicht-HQ-Gast (mode=core) wird NICHT adoptiert,
     kein Plan/keine Veroeffentlichung, Record bleibt retry-faehig (kein
     terminaler Hold).
  2. HQ-Gegenfall -- derselbe Resume, Gast liefert gueltigen HQ-Block:
     Abschluss schliesst, Plan+Veroeffentlichung, F1-Snapshot aller drei
     Mitglieder bleibt korrekt.
  3. Markerlose Wiederaufnahme -- dieselbe Bindung, aber OHNE lebenden
     Marker (`_clear_open_round`), direkt ueber den record-basierten W48-
     Resume-Weg (`pursue_group_save_correction` mit `require_hq=False`,
     exakt der Aufruf, den `finalize()`s normaler Nachforderweg @967
     ausfuehrt): die Bindung muss auch dann aus dem Mitgliedsrecord
     restaurieren.
  4. Rot-vor-Nachweis -- Kernfall gegen den UNGEPATCHTEN Stand (`git
     stash`) laufen lassen: der Gast wird dort adoptiert UND veroeffentlicht
     (genau der belegte Bug). Siehe Report fuer den tatsaechlichen Output
     dieses Laufs.

Pure Python, nur `assert`, `_run_all()`, echter Exitcode (gleiche
Dateikonvention wie die bestehende Suite)."""
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
from _section_completion_resume_fixtures import (  # noqa: E402
    COMPLETION_MARKER, ExplodingDriver, ReflectionOnlyDriver, make_env, make_ps_store, seed_persona_state,
)

import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core import app_service  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    ZeitrissHarvestValidator,
    ZeitrissTableSizePolicy,
    build_save_command_completion_fallback,
    is_save_command,
    is_saveguard_rejection,
)

_TODAY = "2026-11-23"
_TS = "2026-11-23T09:30:00"

_MEMBERS = ("leader_pk", "marek_pk", "dronov_pk")
_CHAR_IDS = {"leader_pk": "chrono-leader", "marek_pk": "chrono-marek", "dronov_pk": "chrono-dronov"}
_CID_TO_PK = {v: k for k, v in _CHAR_IDS.items()}


def _hq_block(char_id: str, name: str) -> dict:
    block = full_v7_save(char_id, name=name)
    block["continuity"]["last_seen"]["mode"] = "hq"
    return block


def _non_hq_block(char_id: str, name: str, mode: str = "core") -> dict:
    block = full_v7_save(char_id, name=name)
    block["continuity"]["last_seen"]["mode"] = mode
    return block


def _fenced_json(block: dict) -> str:
    return f"```json\n{json.dumps(block)}\n```"


def _build_three_member_table(env, table_id: str):
    schema_path = env.run_dir.parent / "schema.json"
    ps_store = make_ps_store(schema_path)
    for pk in _MEMBERS:
        seed_persona_state(ps_store, env.states_dir, pk, _CHAR_IDS[pk])
    write_test_profile(env.run_dir)

    lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
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


class _RepeatingGmTransport:
    """Liefert BEI JEDEM `.turn()`-Aufruf denselben Inhalt -- der Resume-Pfad
    kann (je nach Require-HQ-Zustand) intern mehrfach eine neue Runde oeffnen/
    senden (R4-STARTFRESH-Retry-Schleife); dieselbe Antwort auf jeden Versuch
    haelt das Ergebnis deterministisch (identisch zum unabhaengig verifizierten
    `repro_hq_policy_resume.py`-Verhalten NACH der Crash-Phase)."""

    def __init__(self, content: str):
        self._content = content
        self.calls = 0

    def turn(self, turn_idx, user_text, **kwargs):
        self.calls += 1
        return {"content": self._content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": f"chat-{turn_idx}"}


def _setup_three_member_pre_send_hq_round_crashed_before_send(env, table_id: str, section_id: str):
    """Baut den Drei-Mitglieder-Tisch, laesst Leader+Marek bereits gueltig
    (HQ) harvesten (nur Dronov fehlt), und oeffnet dann GENAU die Runde, die
    `pursue_group_save_correction(require_hq=True, ...)` beim aktiven
    PRE-SEND-Uebernahmepfad selbst oeffnen wuerde (Record + Marker,
    `require_hq=True` gebunden) -- GENAU das W49-A-Crash-Muster (Marker+
    Record bereits durabel, KEIN Versand erfolgt): dieselbe Reihenfolge
    (`load_or_init_record`, `begin_attempt`, `_write_open_round`), die
    `pursue_group_save_correction` VOR jedem `send_correction_turn`-Aufruf
    selbst durchlaeuft."""
    lobby, table, ps_store = _build_three_member_table(env, table_id)
    leader_hq = _hq_block(_CHAR_IDS["leader_pk"], "Leader")
    marek_hq = _hq_block(_CHAR_IDS["marek_pk"], "Marek")
    harvested = {"leader_pk": leader_hq, "marek_pk": marek_hq}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, _TODAY, ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and harvest_completion.missing == ["dronov_pk"], harvest_completion

    prev_ref_snapshot = store.current_save_ref_snapshot(table, ps_store, env.states_dir)
    dronov_repair_key = domain.group_repair_key(table.table_id, section_id, _CHAR_IDS["dronov_pk"])
    sc.load_or_init_record(
        env.run_dir, dronov_repair_key, persona_key="dronov_pk", char_id=_CHAR_IDS["dronov_pk"],
        operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        expected_prev_ref_by_member=prev_ref_snapshot, require_hq=True,
    )
    sc.begin_attempt(env.run_dir, dronov_repair_key)
    round_no = sc._next_round_no(env.run_dir, table.table_id, section_id)
    sc._write_open_round(env.run_dir, table.table_id, section_id, round_no, [
        {"persona_key": "dronov_pk", "char_id": _CHAR_IDS["dronov_pk"], "original_block": None},
    ], expected_prev_ref_by_member=prev_ref_snapshot, require_hq=True)

    record_before = sc.load_record(env.run_dir, dronov_repair_key)
    assert record_before["attempts_used"] == 1 and record_before.get("bound_require_hq") is True, record_before
    open_marker = sc._load_open_round(env.run_dir, table.table_id, section_id)
    assert open_marker is not None and open_marker.get("require_hq") is True, open_marker

    return lobby, table, ps_store, harvested, harvest_completion, dronov_repair_key, prev_ref_snapshot


def _resume_controller(expect_reflections: bool = False) -> TableController:
    # Fuer die Nicht-HQ-/Markerlos-Faelle (erwartet: Abschluss scheitert VOR
    # jeder Pflicht-Reflexion) ist JEDE Persona-Entscheidung ein Testversagen
    # -- ExplodingDriver fuer alle drei Mitglieder. Fuer den HQ-Gegenfall
    # (erwartet: Abschluss gelingt und erreicht PHASE 2) beantwortet
    # `ReflectionOnlyDriver` NUR den bestehenden Pflicht-Reflexionsturn
    # (`PRIVATE_REFLECTION_SENTINEL`) -- jede ANDERE Anfrage (ein neuer
    # Spiel-/GM-Zug) bleibt weiterhin ein Testversagen.
    if expect_reflections:
        return TableController(leader_key="leader_pk", drivers={
            pk: ReflectionOnlyDriver(reflection_text=f"Rueckblick {pk}.") for pk in _MEMBERS
        })
    return TableController(leader_key="leader_pk", drivers={
        "leader_pk": ExplodingDriver("leader_pk"),
        "marek_pk": ExplodingDriver("marek_pk"),
        "dronov_pk": ExplodingDriver("dronov_pk"),
    })


def _resume_contexts() -> dict:
    return {pk: {"user": f"ctx-{pk}"} for pk in _MEMBERS}


def _run_real_runtime_resume(env, lobby, table, ps_store, section_id, gm_transport, expect_reflections: bool = False):
    """Der ECHTE Runtime-Einstieg: `app_service.run_play_session` baut
    `SectionRuntime` und ruft `run_full_section` -- GENAU dieselbe Funktion,
    die TUI/Lab verwenden (I1/A4). Ein frisch geladenes `Table`-Objekt
    (`store.Table.load`) simuliert denselben Prozess-Neueinstieg wie die
    bestehenden `test_j3_*`/`test_j_resumable_*`-Tests. `require_hq` wird
    HIER an KEINER Stelle manuell uebergeben -- einziger Hebel ist die
    durable Bindung aus Marker/Record."""
    table2 = store.Table.load(env.run_dir, table.table_id)
    observed_require_hq: list = []
    real_pursue = sc.pursue_group_save_correction

    def _observing_pursue(**kw):
        observed_require_hq.append(kw.get("require_hq", False))
        return real_pursue(**kw)

    sc.pursue_group_save_correction = _observing_pursue
    try:
        outcome = app_service.run_play_session(
            lobby, table2, gm_transport, _resume_controller(expect_reflections), section_id, _resume_contexts(),
            env.states_dir, _TODAY, _TS, COMPLETION_MARKER, ZeitrissHarvestValidator(), ps_store,
            zeitriss_saves.harvest_from_debrief, max_turns=1,
            completion_fallback=build_save_command_completion_fallback(table2, zeitriss_saves.harvest_from_debrief),
            explicit_completion_attempt=is_save_command,
            save_guard_rejection_detector=is_saveguard_rejection,
        )
    finally:
        sc.pursue_group_save_correction = real_pursue
    return outcome, observed_require_hq


# ---------------------------------------------------------------------------
# 1. Kernfall -- echter Runtime-Resume OHNE manuelles require_hq: der
#    schema-/bindungsvalide Nicht-HQ-Gast (mode=core) wird NICHT adoptiert,
#    kein Plan/keine Veroeffentlichung, Record bleibt retry-faehig.
# ---------------------------------------------------------------------------

def test_f2r_kernfall_real_runtime_resume_blocks_non_hq_guest_without_manual_require_hq():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        section_id = "section-f2r-kernfall"
        lobby, table, ps_store, _harvested, _hc, dronov_repair_key, prev_ref_snapshot = (
            _setup_three_member_pre_send_hq_round_crashed_before_send(env, "t-f2r-kernfall", section_id)
        )

        dronov_non_hq = _non_hq_block(_CHAR_IDS["dronov_pk"], "Dronov", mode="core")
        gm_resume = _RepeatingGmTransport(_fenced_json(dronov_non_hq))
        outcome, observed_require_hq = _run_real_runtime_resume(env, lobby, table, ps_store, section_id, gm_resume)

        assert observed_require_hq == [False], (
            "der Resume-Weg (finalize()'s normaler Nachforderweg) MUSS require_hq=False an "
            f"pursue_group_save_correction uebergeben -- NUR die Bindung restauriert ihn: {observed_require_hq}"
        )
        assert gm_resume.calls >= 1, "der Resume muss den Korrektur-Transport tatsaechlich erreichen."

        assert not outcome.completion.success, (
            f"nach dem F2-R-Fix darf der Nicht-HQ-Gast NICHT adoptiert/veroeffentlicht werden: {outcome.completion}"
        )
        plan_path = env.run_dir / "completion" / f"{section_id}__plan.json"
        assert not plan_path.exists(), "ohne den F2-R-Fix waere hier faelschlich ein Plan gepinnt."
        published_dronov = store.load_current_save(env.run_dir, "dronov_pk", ps_store, states_dir=env.states_dir)
        assert published_dronov is None or "continuity" not in published_dronov, (
            f"der Nicht-HQ-Gast (mode=core) darf NICHT veroeffentlicht werden: {published_dronov}"
        )
        record_after = sc.load_record(env.run_dir, dronov_repair_key)
        assert record_after["state"] not in (sc.STATE_HOLD, sc.STATE_ADOPTED, sc.STATE_ABORTED), (
            f"der Record muss retry-faehig bleiben (kein terminaler Hold, der eine spaetere gueltige "
            f"HQ-Korrektur ausschliessen wuerde): {record_after}"
        )
        assert record_after.get("bound_require_hq") is True, (
            "die Bindung selbst bleibt unveraendert erhalten, unabhaengig vom Ausgang dieses Versuchs."
        )


# ---------------------------------------------------------------------------
# 2. HQ-Gegenfall -- derselbe Resume, Gast liefert gueltigen HQ-Block:
#    Abschluss schliesst, Plan+Veroeffentlichung, F1-Snapshot aller drei
#    Mitglieder bleibt korrekt.
# ---------------------------------------------------------------------------

def test_f2r_hq_gegenfall_real_runtime_resume_accepts_valid_hq_guest_and_publishes():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        section_id = "section-f2r-hq-gegenfall"
        lobby, table, ps_store, _harvested, _hc, dronov_repair_key, prev_ref_snapshot = (
            _setup_three_member_pre_send_hq_round_crashed_before_send(env, "t-f2r-hq-gegenfall", section_id)
        )

        dronov_hq = _hq_block(_CHAR_IDS["dronov_pk"], "Dronov")
        gm_resume = _RepeatingGmTransport(_fenced_json(dronov_hq))
        outcome, observed_require_hq = _run_real_runtime_resume(
            env, lobby, table, ps_store, section_id, gm_resume, expect_reflections=True,
        )

        assert observed_require_hq == [False], observed_require_hq
        assert outcome.completion.success, (
            f"ein gueltiger HQ-Gast muss den Abschluss nach Resume regulaer abschliessen: {outcome.completion}"
        )

        plan_path = env.run_dir / "completion" / f"{section_id}__plan.json"
        assert plan_path.exists(), "nach der gueltigen HQ-Korrektur muss der Plan gepinnt sein."
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        assert set(plan_data["members"].keys()) == set(_MEMBERS)
        for pk in _MEMBERS:
            assert plan_data["members"][pk]["expected_prev_ref"] == prev_ref_snapshot[pk], (
                f"F1-Snapshot (expected_prev_ref_by_member) muss fuer ALLE drei Mitglieder "
                f"ueber den Resume hinweg erhalten bleiben -- {pk}: {plan_data['members'][pk]}"
            )

        published_dronov = store.load_current_save(env.run_dir, "dronov_pk", ps_store, states_dir=env.states_dir)
        assert published_dronov is not None, "der HQ-Gast muss nach erfolgreichem Abschluss veroeffentlicht sein."
        assert published_dronov["continuity"]["last_seen"]["mode"] == "hq", published_dronov

        record_after = sc.load_record(env.run_dir, dronov_repair_key)
        assert record_after["state"] == sc.STATE_ADOPTED, record_after


# ---------------------------------------------------------------------------
# 3. Markerlose Wiederaufnahme -- dieselbe Bindung, aber OHNE lebenden
#    Marker (`_clear_open_round`), direkt ueber den record-basierten W48-
#    Resume-Weg (`pursue_group_save_correction` mit require_hq default
#    False -- EXAKT der Aufruf, den finalize()'s normaler Nachforderweg
#    @967 ausfuehrt): die Bindung muss auch dann aus dem Mitgliedsrecord
#    restaurieren.
# ---------------------------------------------------------------------------

def test_f2r_markerless_resume_restores_require_hq_from_member_record_only():
    with tempfile.TemporaryDirectory() as td:
        env = make_env(Path(td))
        section_id = "section-f2r-markerless"
        lobby, table, ps_store, harvested, harvest_completion, dronov_repair_key, prev_ref_snapshot = (
            _setup_three_member_pre_send_hq_round_crashed_before_send(env, "t-f2r-markerless", section_id)
        )

        # Marker weg (z.B. ein frueherer Prozess hat ihn bereits geloescht) --
        # NUR der Mitgliedsrecord traegt die Bindung noch.
        sc._clear_open_round(env.run_dir, table.table_id, section_id)
        assert sc._load_open_round(env.run_dir, table.table_id, section_id) is None
        assert not sc._open_round_path(env.run_dir, table.table_id, section_id).exists()
        record_before = sc.load_record(env.run_dir, dronov_repair_key)
        assert record_before.get("bound_require_hq") is True and record_before["state"] != sc.STATE_HOLD, (
            "Vorbedingung: NUR der Record (nicht der Marker) traegt die require_hq-Bindung."
        )

        dronov_non_hq = _non_hq_block(_CHAR_IDS["dronov_pk"], "Dronov", mode="core")
        gm_resume = _RepeatingGmTransport(_fenced_json(dronov_non_hq))

        # EXAKT der verwundbare Aufruf (`core/runtime.py` ~Z.967, finalize()'s
        # normaler `not pre_send`-Nachforderweg): KEIN require_hq-kwarg, KEIN
        # prev_ref_override -- die Bindung MUSS vollstaendig aus dem bereits
        # bestehenden Mitgliedsrecord restauriert werden.
        harvested_after, completion_after = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
            harvest_completion=harvest_completion, states_dir=env.states_dir, today=_TODAY,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm_resume, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )

        assert not completion_after.success, (
            f"ohne lebenden Marker MUSS die require_hq-Bindung trotzdem aus dem Record restaurieren -- "
            f"der Nicht-HQ-Gast darf NICHT adoptiert werden: {completion_after}"
        )
        assert "continuity" not in harvested_after.get("dronov_pk", {}) or (
            harvested_after["dronov_pk"].get("continuity", {}).get("last_seen", {}).get("mode") != "core"
        ), harvested_after.get("dronov_pk")
        plan_path = env.run_dir / "completion" / f"{section_id}__plan.json"
        assert not plan_path.exists()
        record_after = sc.load_record(env.run_dir, dronov_repair_key)
        assert record_after["state"] not in (sc.STATE_HOLD, sc.STATE_ADOPTED, sc.STATE_ABORTED), record_after


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
