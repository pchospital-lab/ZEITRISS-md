#!/usr/bin/env python3
"""
tests/mmo_sim/test_r7_01_drift_guard_and_m2_recovery_2026_11_19.py --
ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261119-R7, §02 (R7-01) Parts B/C/E.

Reproduziert am ECHTEN Aufrufer (`core.save_correction.
pursue_group_save_correction` -> `domain.zeitriss.save_correction.
detect_unjustified_drift`) genau die Fallform aus dem r6-M2-Originalbeleg
(`evidence/save-correction-readback.json`, request_id
51b0660fa39b4983a8993bd3462ed4e8): die KI-SL kuerzt `continuity.
shared_echoes` von 8 auf 6 Eintraege (gemeldeter Fehler: `maxItems`, limit
6) UND aendert dabei zusaetzlich `arc.hooks`/`arc.questions` -- Felder, die
NICHT Teil des gemeldeten Fehlerpfads sind.

Part B (Drift-Guard eng korrigieren): eine Antwort, die NUR die gemeldete
Liste kuerzt/reorganisiert, darf NICHT mehr als Drift gelten (Nachfahren
eines `maxItems`/`minItems`-Fehlerpfads sind keine Drift) -- dieselbe
Antwort PLUS eine arc-Aenderung bleibt weiterhin Drift (arc ist KEIN
Nachfahre des gemeldeten shared_echoes-Fehlerpfads).

Part C (M2-HOLD-Wiederaufnahme): ein bereits terminal `STATE_HOLD`
(`unjustified_semantic_drift`) Datensatz mit einem driftfrei beobachteten
`best_candidate_block` (dem urspruenglichen, NIE gedrifteten Entwurf), der
NUR noch den Cap-Ueberlauf traegt, wird ueber den bereits bestehenden
Best-effort-Strukturvertrag (`resume_hold_via_structural_best_effort`)
regulaer wiederaufgenommen -- die tatsaechlich archivierte gedriftete
Antwort selbst wird dabei NIE fuer gueltig erklaert.

Leader ist in allen Szenarien von Anfang an ein bereits gueltiger,
unveraenderter Save (nicht Teil der Korrektur) -- NUR der Gast durchlaeuft
das M2-aehnliche Szenario (gleiches Muster wie `test_r4_startfresh_group_
best_effort_2026_10_29.py`s Szenario (c)).

Geldfrei per Konstruktion: ausschliesslich In-Process-Fakes
(`ScriptedGmTransport`/`build_two_member_table`), kein echter Transport.

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite."""
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
from _section_completion_resume_fixtures import (  # noqa: E402
    ExplodingGmTransport, ScriptedGmTransport, build_two_member_table, make_env,
)

import mmo_sim.core.save_correction as sc  # noqa: E402
import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.domain.zeitriss import save_correction as domain  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator  # noqa: E402

_LEADER_CID = "chrono-leader"
_GUEST_CID = "chrono-guest"
_CID_TO_PK = {_LEADER_CID: "leader_pk", _GUEST_CID: "guest_pk"}


def _fenced_json(block: dict) -> str:
    import json
    return f"```json\n{json.dumps(block)}\n```"


def _m2_like_overcap(cid: str, name: str = "Guest") -> dict:
    """Nachbildung der realen M2-Originalform (`evidence/save-correction-
    readback.json`): 8 `continuity.shared_echoes` (maxItems 6 -- schema-
    ungueltig), 8 `arc.hooks`, 9 `arc.questions`."""
    block = full_v7_save(cid, name=name)
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}", "scope": "campaign", "text": f"erinnerung-{i}"} for i in range(8)
    ]
    block["arc"]["hooks"] = [{"text": f"hook-{i}"} for i in range(8)]
    block["arc"]["questions"] = [f"frage-{i}" for i in range(9)]
    return block


def _m2_like_pure_repair(cid: str, name: str = "Guest") -> dict:
    """NUR die gemeldete Liste gekuerzt/reorganisiert (8 -> 6), `arc`
    UNVERAENDERT -- die wirklich minimale, semantisch vertraegliche
    Strukturkorrektur (02_NACHZUG_AUFTRAG.md §02 A)."""
    block = _m2_like_overcap(cid, name=name)
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}-neu", "scope": "campaign", "text": f"erinnerung-{i}-neu"} for i in range(6)
    ]
    return block


def _m2_like_drifted_correction(cid: str, name: str = "Guest") -> dict:
    """Dieselbe zulaessige shared_echoes-Kuerzung PLUS zusaetzliche
    Aenderungen an `arc.hooks`/`arc.questions` -- GENAU die r6-Fallform:
    unbestellte Aenderungen AUSSERHALB des diagnostizierten Feldes."""
    block = _m2_like_pure_repair(cid, name=name)
    block["arc"]["hooks"][0]["text"] = "ausserhalb-des-korrekturauftrags-umformuliert"
    block["arc"]["hooks"][2]["text"] = "auch-hier-unbestellt-geaendert"
    block["arc"]["questions"][2] = "unbestellt-umformulierte-frage"
    return block


def _build(root: Path, table_id: str):
    env = make_env(root)
    lobby, table, ps_store = build_two_member_table(env, table_id=table_id)
    write_test_profile(env.run_dir)
    return env, lobby, table, ps_store


def _run_guest_only_correction(env, lobby, table, ps_store, section_id: str, leader_save: dict, scripted_contents):
    guest_old_invalid = _m2_like_overcap(_GUEST_CID, name="Guest")
    harvested = {"leader_pk": leader_save, "guest_pk": guest_old_invalid}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, "2026-11-19",
        ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion
    gm = ScriptedGmTransport(scripted_contents=scripted_contents)
    harvested_out, completion_out = sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-11-19",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    return env, guest_old_invalid, gm, harvested_out, completion_out


# ---------------------------------------------------------------------------
# (1) r6-Fall exakt: shared_echoes 8->6 + arc-Aenderungen -> bleibt Drift/HOLD.
# ---------------------------------------------------------------------------

def test_r7_m2_exact_case_shared_echoes_repair_plus_arc_changes_stays_drift_hold():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-r7-case1")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        drifted = _m2_like_drifted_correction(_GUEST_CID, name="Guest")
        _env, guest_old_invalid, gm, harvested_out, completion_out = _run_guest_only_correction(
            env, lobby, table, ps_store, "section-r7-case1", leader_save, [_fenced_json(drifted)],
        )

        assert not completion_out.success, completion_out
        assert completion_out.missing == ["guest_pk"], completion_out
        assert len(gm.calls) == 1, gm.calls
        assert harvested_out["guest_pk"] == guest_old_invalid, (
            "die gedriftete Antwort darf NICHT uebernommen werden -- der alte Stand bleibt."
        )
        guest_repair_key = domain.group_repair_key(table.table_id, "section-r7-case1", _GUEST_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record["state"] == "hold" and guest_record["last_reason"] == "unjustified_semantic_drift", (
            guest_record
        )
        # P2-Registrierung: der NIE gedriftete Originalentwurf ist bereits als
        # best_candidate_block gebunden (Vorbedingung fuer Part C/Test 5).
        assert guest_record.get("best_candidate_block") == guest_old_invalid, guest_record


# ---------------------------------------------------------------------------
# (2) Reine zulaessige Listenreparatur (nur shared_echoes->6) -> akzeptiert,
#     KEINE Drift.
# ---------------------------------------------------------------------------

def test_r7_pure_shared_echoes_repair_without_arc_changes_is_accepted_no_drift():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-r7-case2")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        repaired = _m2_like_pure_repair(_GUEST_CID, name="Guest")
        _env, guest_old_invalid, gm, harvested_out, completion_out = _run_guest_only_correction(
            env, lobby, table, ps_store, "section-r7-case2", leader_save, [_fenced_json(repaired)],
        )

        assert completion_out.success, completion_out
        assert harvested_out["guest_pk"] == repaired
        guest_repair_key = domain.group_repair_key(table.table_id, "section-r7-case2", _GUEST_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record["state"] == "adopted" and not guest_record.get("best_effort"), (
            "Part B: eine reine Listenkuerzung muss jetzt OHNE Best-effort-Flagge voll akzeptiert "
            f"werden (kein Rest-Strukturfehler, kein Drift-Hold): {guest_record}"
        )
        assert guest_record["adopted_block"] == repaired


# ---------------------------------------------------------------------------
# (3) Dieselbe Reparatur + zusaetzliche arc-Aenderung -> bleibt Drift.
# ---------------------------------------------------------------------------

def test_r7_pure_repair_plus_single_additional_arc_change_stays_drift():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-r7-case3")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        repaired_plus_one_arc_change = _m2_like_pure_repair(_GUEST_CID, name="Guest")
        repaired_plus_one_arc_change["arc"]["hooks"][0]["text"] = "einzelne-unbestellte-aenderung"
        _env, guest_old_invalid, gm, harvested_out, completion_out = _run_guest_only_correction(
            env, lobby, table, ps_store, "section-r7-case3", leader_save,
            [_fenced_json(repaired_plus_one_arc_change)],
        )

        assert not completion_out.success, completion_out
        guest_repair_key = domain.group_repair_key(table.table_id, "section-r7-case3", _GUEST_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record["state"] == "hold" and guest_record["last_reason"] == "unjustified_semantic_drift", (
            f"schon EINE unbestellte arc-Aenderung ausserhalb der shared_echoes-Kuerzung muss weiterhin "
            f"Drift bleiben: {guest_record}"
        )


# ---------------------------------------------------------------------------
# (4) Geschuetzte Identitaets-/Wallet-/Fortschrittsaenderung bleibt Drift,
#     auch wenn GLEICHZEITIG eine zulaessige Cap-Reparatur vorliegt.
# ---------------------------------------------------------------------------

def test_r7_protected_identity_wallet_change_alongside_valid_cap_repair_stays_drift():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-r7-case4")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        repaired_plus_identity_drift = _m2_like_pure_repair(_GUEST_CID, name="Guest")
        # Level- UND Walletaenderung -- beides AUSSERHALB von error_paths
        # und AUSSERHALB jedes structural_cap_paths-Nachfahren.
        repaired_plus_identity_drift["characters"][0]["lvl"] = 99
        repaired_plus_identity_drift["economy"] = {"wallets": {_GUEST_CID: {"balance": 999999}}}
        _env, guest_old_invalid, gm, harvested_out, completion_out = _run_guest_only_correction(
            env, lobby, table, ps_store, "section-r7-case4", leader_save,
            [_fenced_json(repaired_plus_identity_drift)],
        )

        assert not completion_out.success, completion_out
        guest_repair_key = domain.group_repair_key(table.table_id, "section-r7-case4", _GUEST_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record["state"] == "hold" and guest_record["last_reason"] == "unjustified_semantic_drift", (
            f"Level-/Walletaenderung muss Drift bleiben, selbst neben einer sonst zulaessigen "
            f"Cap-Reparatur: {guest_record}"
        )

        # Praezisionsergaenzung auf Helper-Ebene (Part B, Wallet-Vorrang):
        # selbst wenn ein Walletpfad NOMINELL ein Nachfahre eines gemeldeten
        # Cap-Fehlerpfads waere, bleibt er -- GENAU wie vor diesem Fix --
        # ueber `_is_wallet_amount_path` geschuetzt (Pruefreihenfolge im
        # Code: "... and not _is_wallet_amount_path(path)").
        old_block = {"economy": {"wallets": {_GUEST_CID: 500}}}
        new_block = {"economy": {"wallets": {_GUEST_CID: 300}}}
        error_paths = {"/economy/wallets"}
        structural_cap_paths = frozenset({"/economy/wallets"})
        drift = domain.detect_unjustified_drift(
            old_block, new_block, error_paths, structural_cap_paths=structural_cap_paths,
        )
        assert any(d[0] == "/economy/wallets/" + _GUEST_CID for d in drift), (
            f"ein ECHTER Walletbetragswechsel darf NIE durch die neue Cap-Nachfahren-Ausnahme "
            f"verschluckt werden, selbst wenn der Elternpfad nominell als Cap-Fehler gemeldet ist: {drift}"
        )


# ---------------------------------------------------------------------------
# (5) Vorhandenes terminales M2-HOLD: gueltige Provenienz -> Recovery
#     moeglich; ungueltige Provenienz -> bleibt HOLD.
# ---------------------------------------------------------------------------

def test_r7_terminal_m2_hold_resumes_via_best_effort_with_valid_provenance_only():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-r7-case5")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        drifted = _m2_like_drifted_correction(_GUEST_CID, name="Guest")
        _env, guest_old_invalid, gm, harvested_out, completion_out = _run_guest_only_correction(
            env, lobby, table, ps_store, "section-r7-case5", leader_save, [_fenced_json(drifted)],
        )
        assert not completion_out.success and completion_out.missing == ["guest_pk"], completion_out
        section_id = "section-r7-case5"
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        guest_record_before = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record_before["state"] == "hold", guest_record_before
        assert sc.has_residual_structural_cap_overflow(guest_record_before["best_candidate_block"], _GUEST_CID), (
            "Vorbedingung: der gebundene Originalentwurf darf NUR noch den Cap-Ueberlauf tragen."
        )

        # Ungueltige Provenienz zuerst (direkter Funktionsaufruf -- derselbe
        # Datensatz, aber mit einem FALSCHEN char_id/table_id/section_id, wie
        # es bei einer missbraeuchlichen Wiederaufnahme unter fremder
        # Bindung vorlaege): KEINE Resume, Datensatz bleibt unveraendert HOLD.
        invalid_attempts = [
            dict(char_id="CHR-FREMDE-FIGUR", table_id=table.table_id, section_id=section_id),
            dict(char_id=_GUEST_CID, table_id="t-FREMDER-TISCH", section_id=section_id),
            dict(char_id=_GUEST_CID, table_id=table.table_id, section_id="section-FREMD"),
        ]
        for kwargs in invalid_attempts:
            resumed_invalid = sc.resume_hold_via_structural_best_effort(env.run_dir, guest_repair_key, **kwargs)
            assert resumed_invalid is None, (
                f"Resume mit ungueltiger Provenienz {kwargs} darf NICHT greifen: {resumed_invalid}"
            )
        guest_record_still_hold = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record_still_hold == guest_record_before, (
            "ein fehlgeschlagener Resume-Versuch darf den Datensatz NICHT veraendern (kein Teil-Write)."
        )

        # Gueltige Provenienz -- regulaerer Wiederaufnahmeversuch am normalen
        # Gruppenabschlussweg: ein erneuter Aufruf von
        # `pursue_group_save_correction` (z.B. nach normaler erneuter
        # UI-Bestaetigung) OHNE jeden neuen GM-Call.
        never_called_gm = ExplodingGmTransport()
        harvested2 = {"leader_pk": leader_save, "guest_pk": guest_old_invalid}
        harvest_completion2 = store.complete_section(
            lobby, table, section_id, harvested2, env.states_dir, "2026-11-19",
            ZeitrissHarvestValidator(), ps_store,
        )
        assert not harvest_completion2.success and harvest_completion2.missing == ["guest_pk"]
        harvested_out2, completion_out2 = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=harvested2,
            harvest_completion=harvest_completion2, states_dir=env.states_dir, today="2026-11-19",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=never_called_gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert never_called_gm.calls == 0, (
            "Die Wiederaufnahme darf KEINEN neuen GM-Call ausloesen -- sie nutzt den bereits "
            f"beobachteten, driftfreien Originalentwurf: calls={never_called_gm.calls}"
        )
        assert completion_out2.success, completion_out2
        assert harvested_out2["guest_pk"] == guest_old_invalid, (
            "Recovery adoptiert den UNVERAENDERTEN Originalentwurf -- NIE die archivierte gedriftete "
            "Antwort."
        )
        guest_record_after = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record_after["state"] == "adopted" and guest_record_after.get("best_effort") is True, (
            guest_record_after
        )
        assert guest_record_after["adopted_block"] == guest_old_invalid
        # Keine Doppelmission/-belohnung/-buchung: derselbe Versuchszaehler,
        # keine neue Request-/Budgetbuchung (kein GM-Call oben bewiesen).
        assert guest_record_after["attempts_used"] == guest_record_before["attempts_used"]
        plan_path = store._completion_plan_path(env.run_dir, section_id)
        assert plan_path.exists()
        import json
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        assert plan_data.get("best_effort") is True
        assert plan_data["members"]["guest_pk"].get("best_effort") is True


# ---------------------------------------------------------------------------
# (6) Unterbrechung/Neustart + wiederholtes Fortsetzen -> keine Doppel-
#     Adoption/-Buchung.
# ---------------------------------------------------------------------------

def test_r7_repeated_resume_after_restart_is_idempotent_no_double_adoption():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-r7-case6")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        drifted = _m2_like_drifted_correction(_GUEST_CID, name="Guest")
        _env, guest_old_invalid, gm, harvested_out, completion_out = _run_guest_only_correction(
            env, lobby, table, ps_store, "section-r7-case6", leader_save, [_fenced_json(drifted)],
        )
        section_id = "section-r7-case6"
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        assert sc.load_record(env.run_dir, guest_repair_key)["state"] == "hold"

        # Erster Resume -- erfolgreich (wie Test 5).
        resumed_first = sc.resume_hold_via_structural_best_effort(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed_first is not None and resumed_first["state"] == "adopted"
        record_after_first = sc.load_record(env.run_dir, guest_repair_key)

        # Simulierter Prozessneustart: ein erneuter Aufruf (z.B. weil ein
        # frueherer Prozess GENAU zwischen Resume und der naechsten
        # `complete_section`-Pruefung abgestuerzt ist) darf KEINE zweite
        # Adoption/Buchung erzeugen -- `adopted_block` ist bereits gesetzt,
        # die Guard-Bedingung in `resume_hold_via_structural_best_effort`
        # greift und liefert `None`, der Datensatz bleibt UNVERAENDERT.
        resumed_second = sc.resume_hold_via_structural_best_effort(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed_second is None, (
            f"ein bereits adoptierter Datensatz darf NICHT erneut resumed werden: {resumed_second}"
        )
        record_after_second_attempt = sc.load_record(env.run_dir, guest_repair_key)
        assert record_after_second_attempt == record_after_first, (
            "ein No-op-Resume-Versuch (bereits adoptiert) darf den Datensatz NICHT veraendern "
            "(kein zweiter Write, keine Doppelbuchung)."
        )
        assert record_after_second_attempt["attempts_used"] == record_after_first["attempts_used"]


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
