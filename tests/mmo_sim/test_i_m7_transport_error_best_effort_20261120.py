#!/usr/bin/env python3
"""
tests/mmo_sim/test_i_m7_transport_error_best_effort_20261120.py --
ZR-R8-LIVESYNC-PALIMPSEST-20261119-R1, Stage I (M7-Save-Fix + Recovery).

Reproduziert am ECHTEN Aufrufer (`core.save_correction.
pursue_group_save_correction` -> `send_correction_turn`) genau die
M7-Originalfallform (belegt gegen `run/preserve/H-m7-recovery/section10/
save_corrections_group__10.json` + `request_05573_retry.json`): der GM-
Transport wirft fuer EINEN Gruppen-Korrekturversand eine Ausnahme (echter
Transport-Timeout, `TIMEOUT_SL=420 x 3 Versuche` ohne gesetztes
`MMO_SIM_GM_TRANSPORT_TIMEOUT`, s. I-A-Report), OHNE dass das Modell je
geantwortet hat -- `send_correction_turn`s generischer
`except Exception`-Zweig faengt das als `reason=f"transport_error:{exc}"`,
`request_ledger.finish_error` bucht den Request terminal mit `error`
gesetzt und `result_text=None` (fuer IMMER unsichtbar fuer `find_durable_
result`). Die Gruppe bleibt `state=hold`, `last_reason` beginnt mit
`transport_error:` -- mit einem bereits VOR dem fehlgeschlagenen Versand
registrierten `best_candidate_block` (dem urspruenglichen, bereits
empfangenen Harvest-Entwurf, hier bewusst NUR mit Cap-Ueberlauf-Fehlern
praepariert, analog zur echten M7-Form: 3 `maxItems`-Fehler, keine
Bindungsfehler).

Testet den NEUEN, in dieser Stage ergaenzten Wiederaufnahmepfad
(`resume_hold_via_transport_error_best_effort` + dessen Verdrahtung in
`pursue_group_save_correction`) -- GENAU analog zum bereits bestehenden
Drift-Pendant (`resume_hold_via_structural_best_effort`, s.
`test_r7_01_drift_guard_and_m2_recovery_2026_11_19.py`):

  (1) transport_error-HOLD + best_candidate_block-Registrierung entsteht
      exakt wie erwartet (ohne Fix wuerde die Gruppe hier fuer IMMER HOLD
      bleiben -- es gibt vor diesem Fix KEINEN Resume-Pfad fuer diesen
      `last_reason`).
  (2) Falsche Provenienz (char_id/table_id/section_id) -> KEIN Resume,
      Datensatz unveraendert.
  (3) Gueltige Provenienz -> regulaerer Wiederaufnahmeversuch am normalen
      Gruppenabschlussweg, OHNE jeden neuen GM-Call (`ExplodingGmTransport`
      beweist das) -- entspricht der realen 'kostenloser Resume'-Anforderung.
  (4) Wiederholter Resume nach (simuliertem) Neustart -> idempotent, KEINE
      doppelte Adoption/Buchung.
  (5) Saubere Trennung von der bestehenden Drift-Variante: ein
      `unjustified_semantic_drift`-HOLD wird vom NEUEN Pfad NICHT resumed
      (und umgekehrt) -- keine stille Verbreiterung der jeweils anderen
      Fallklasse.

Geldfrei per Konstruktion: ausschliesslich In-Process-Fakes (kein echter
Transport, keine echten HTTP-Requests).

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (`test_r7_01_drift_guard_and_m2_recovery_2026_11_19.py`)."""
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
    ExplodingGmTransport, build_two_member_table, make_env,
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


class RaisingGmTransport:
    """M7-Originalfallform: jeder `.turn()`-Aufruf wirft dieselbe Ausnahme
    wie ein echter client-seitiger Transport-Timeout (`OWUIChat._post`
    nach 3 Versuchen à 420s, s. I-A-Report) -- OHNE je eine Antwort
    zurueckzugeben. `send_correction_turn`s generischer `except Exception`-
    Zweig faengt das identisch zu einem echten Timeout."""

    def __init__(self):
        self.calls: list[dict] = []
        self.output_limit_tokens = None

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        raise TimeoutError("timed out")


def _overcap_only(cid: str, name: str = "Guest") -> dict:
    """Reine Cap-Ueberlauf-Form (3 `maxItems`-Fehler, KEINE Bindungs-/Typ-/
    Identitaetsfehler) -- analog zur echten M7-`best_candidate_block`-Form
    (bestaetigt gegen `save_corrections_group__10.json`: `total_error_
    count=3`, alle `check=maxItems`, `binding_errors=[]`)."""
    block = full_v7_save(cid, name=name)
    block["continuity"]["shared_echoes"] = [
        {"tag": f"echo-{i}", "scope": "campaign", "text": f"erinnerung-{i}"} for i in range(8)
    ]
    block["arc"]["hooks"] = [{"text": f"hook-{i}"} for i in range(8)]
    block["arc"]["questions"] = [f"frage-{i}" for i in range(9)]
    return block


def _build(root: Path, table_id: str):
    env = make_env(root)
    lobby, table, ps_store = build_two_member_table(env, table_id=table_id)
    write_test_profile(env.run_dir)
    return env, lobby, table, ps_store


def _run_guest_only_correction_with_transport_error(env, lobby, table, ps_store, section_id: str, leader_save: dict):
    guest_old = _overcap_only(_GUEST_CID, name="Guest")
    harvested = {"leader_pk": leader_save, "guest_pk": guest_old}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, "2026-11-19",
        ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion
    gm = RaisingGmTransport()
    harvested_out, completion_out = sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-11-19",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    return env, guest_old, gm, harvested_out, completion_out


# ---------------------------------------------------------------------------
# (1) Transportfehler beim Gruppen-Korrekturversand -> terminal HOLD mit
#     last_reason="transport_error:..." + best_candidate_block registriert.
# ---------------------------------------------------------------------------

def test_i_transport_error_during_group_correction_yields_hold_with_best_candidate():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-i-case1")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        _env, guest_old, gm, harvested_out, completion_out = _run_guest_only_correction_with_transport_error(
            env, lobby, table, ps_store, "section-i-case1", leader_save,
        )
        assert not completion_out.success and completion_out.missing == ["guest_pk"], completion_out
        assert len(gm.calls) == 1, gm.calls
        assert harvested_out["guest_pk"] == guest_old, (
            "ein transportfehlgeschlagener Versand darf den alten Stand NICHT veraendern."
        )
        guest_repair_key = domain.group_repair_key(table.table_id, "section-i-case1", _GUEST_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record["state"] == "hold", guest_record
        assert guest_record["last_reason"].startswith("transport_error:"), guest_record
        assert "timed out" in guest_record["last_reason"], guest_record
        assert guest_record.get("adopted_block") is None
        # P2-Registrierung (dieselbe wie im Drift-Fall, unveraendert): der
        # VOR dem fehlgeschlagenen Versand bereits beobachtete Originalentwurf
        # ist bereits als best_candidate_block gebunden.
        assert guest_record.get("best_candidate_block") == guest_old, guest_record
        assert sc.has_residual_structural_cap_overflow(guest_record["best_candidate_block"], _GUEST_CID), (
            "Vorbedingung: der gebundene Originalentwurf darf NUR noch den Cap-Ueberlauf tragen."
        )
        return env, table, guest_record


# ---------------------------------------------------------------------------
# (2) Falsche Provenienz -> KEIN Resume, Datensatz unveraendert.
# ---------------------------------------------------------------------------

def test_i_resume_rejects_wrong_provenance():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-i-case2")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        _env, guest_old, gm, harvested_out, completion_out = _run_guest_only_correction_with_transport_error(
            env, lobby, table, ps_store, "section-i-case2", leader_save,
        )
        section_id = "section-i-case2"
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        guest_record_before = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record_before["state"] == "hold"

        invalid_attempts = [
            dict(char_id="CHR-FREMDE-FIGUR", table_id=table.table_id, section_id=section_id),
            dict(char_id=_GUEST_CID, table_id="t-FREMDER-TISCH", section_id=section_id),
            dict(char_id=_GUEST_CID, table_id=table.table_id, section_id="section-FREMD"),
        ]
        for kwargs in invalid_attempts:
            resumed_invalid = sc.resume_hold_via_transport_error_best_effort(env.run_dir, guest_repair_key, **kwargs)
            assert resumed_invalid is None, (
                f"Resume mit ungueltiger Provenienz {kwargs} darf NICHT greifen: {resumed_invalid}"
            )
        guest_record_still_hold = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record_still_hold == guest_record_before, (
            "ein fehlgeschlagener Resume-Versuch darf den Datensatz NICHT veraendern (kein Teil-Write)."
        )


# ---------------------------------------------------------------------------
# (3) Gueltige Provenienz -> regulaerer Wiederaufnahmeversuch am normalen
#     Gruppenabschlussweg, OHNE jeden neuen GM-Call ("kostenloser Resume").
# ---------------------------------------------------------------------------

def test_i_resume_hold_via_transport_error_best_effort_adopts_without_new_gm_call():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-i-case3")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        _env, guest_old, gm, harvested_out, completion_out = _run_guest_only_correction_with_transport_error(
            env, lobby, table, ps_store, "section-i-case3", leader_save,
        )
        section_id = "section-i-case3"
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        guest_record_before = sc.load_record(env.run_dir, guest_repair_key)

        never_called_gm = ExplodingGmTransport()
        harvested2 = {"leader_pk": leader_save, "guest_pk": guest_old}
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
            f"beobachteten Originalentwurf: calls={never_called_gm.calls}"
        )
        assert completion_out2.success, completion_out2
        assert harvested_out2["guest_pk"] == guest_old, (
            "Recovery adoptiert den UNVERAENDERTEN Originalentwurf."
        )
        guest_record_after = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record_after["state"] == "adopted" and guest_record_after.get("best_effort") is True, (
            guest_record_after
        )
        assert guest_record_after["adopted_block"] == guest_old
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
# (4) Wiederholter Resume nach (simuliertem) Neustart -> idempotent, KEINE
#     doppelte Adoption/Buchung.
# ---------------------------------------------------------------------------

def test_i_repeated_resume_after_restart_is_idempotent_no_double_adoption():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-i-case4")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        _env, guest_old, gm, harvested_out, completion_out = _run_guest_only_correction_with_transport_error(
            env, lobby, table, ps_store, "section-i-case4", leader_save,
        )
        section_id = "section-i-case4"
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        assert sc.load_record(env.run_dir, guest_repair_key)["state"] == "hold"

        resumed_first = sc.resume_hold_via_transport_error_best_effort(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed_first is not None and resumed_first["state"] == "adopted"
        record_after_first = sc.load_record(env.run_dir, guest_repair_key)

        resumed_second = sc.resume_hold_via_transport_error_best_effort(
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


# ---------------------------------------------------------------------------
# (5) Saubere Trennung: Drift-HOLD wird NICHT vom neuen Transport-Pfad
#     resumed, Transport-HOLD wird NICHT vom bestehenden Drift-Pfad resumed.
# ---------------------------------------------------------------------------

def test_i_transport_error_and_drift_resume_paths_stay_disjoint():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-i-case5")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")

        # Transport-HOLD darf NICHT ueber den Drift-Pfad resumed werden.
        _env, guest_old_t, _gm_t, _ho_t, _co_t = _run_guest_only_correction_with_transport_error(
            env, lobby, table, ps_store, "section-i-case5-transport", leader_save,
        )
        repair_key_t = domain.group_repair_key(table.table_id, "section-i-case5-transport", _GUEST_CID)
        assert sc.load_record(env.run_dir, repair_key_t)["state"] == "hold"
        resumed_via_drift_path = sc.resume_hold_via_structural_best_effort(
            env.run_dir, repair_key_t, char_id=_GUEST_CID, table_id=table.table_id,
            section_id="section-i-case5-transport",
        )
        assert resumed_via_drift_path is None, (
            f"ein transport_error-HOLD darf NICHT ueber den Drift-Resume-Pfad greifen: {resumed_via_drift_path}"
        )
        assert sc.load_record(env.run_dir, repair_key_t)["state"] == "hold"

        # Drift-HOLD darf NICHT ueber den neuen Transport-Pfad resumed werden.
        from _section_completion_resume_fixtures import ScriptedGmTransport

        def _fenced_json(block: dict) -> str:
            import json
            return f"```json\n{json.dumps(block)}\n```"

        drifted = _overcap_only(_GUEST_CID, name="Guest")
        drifted["continuity"]["shared_echoes"] = [
            {"tag": f"echo-{i}-neu", "scope": "campaign", "text": f"erinnerung-{i}-neu"} for i in range(6)
        ]
        drifted["arc"]["hooks"][0]["text"] = "ausserhalb-des-korrekturauftrags-umformuliert"
        guest_old_d = _overcap_only(_GUEST_CID, name="Guest")
        harvested_d = {"leader_pk": leader_save, "guest_pk": guest_old_d}
        section_id_d = "section-i-case5-drift"
        harvest_completion_d = store.complete_section(
            lobby, table, section_id_d, harvested_d, env.states_dir, "2026-11-19",
            ZeitrissHarvestValidator(), ps_store,
        )
        gm_d = ScriptedGmTransport(scripted_contents=[_fenced_json(drifted)])
        sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id_d, harvested=dict(harvested_d),
            harvest_completion=harvest_completion_d, states_dir=env.states_dir, today="2026-11-19",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm_d, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        repair_key_d = domain.group_repair_key(table.table_id, section_id_d, _GUEST_CID)
        guest_record_d = sc.load_record(env.run_dir, repair_key_d)
        assert guest_record_d["state"] == "hold" and guest_record_d["last_reason"] == "unjustified_semantic_drift", (
            guest_record_d
        )
        resumed_via_transport_path = sc.resume_hold_via_transport_error_best_effort(
            env.run_dir, repair_key_d, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id_d,
        )
        assert resumed_via_transport_path is None, (
            f"ein unjustified_semantic_drift-HOLD darf NICHT ueber den neuen Transport-Resume-Pfad "
            f"greifen: {resumed_via_transport_path}"
        )
        assert sc.load_record(env.run_dir, repair_key_d)["state"] == "hold"


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
