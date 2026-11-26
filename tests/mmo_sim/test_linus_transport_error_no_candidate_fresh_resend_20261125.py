#!/usr/bin/env python3
"""
tests/mmo_sim/test_linus_transport_error_no_candidate_fresh_resend_20261125.py --
ZR-PLAYTEST-ANSCHLUSS-20261125 (Linus-Fix).

Belegter Originalfall (`/home/altair/zr-updater-spieltest-nachzug-20261119-r7/
run/live/install/internal/mmo_sim_data`): eine Gruppen-Save-Correction-
Request (`role=save_correction_group`) lief in einen VERBUCHTEN Transport-
Timeout (`state=accounted`, `error="timed out"`, `result_text=None`,
`dollar_billed=True`) -- die betroffenen Mitglieder (hier reproduziert als
zwei abwesende Tischmitglieder, analog CHR-RUSH-001/CHR-DRONOV-001) landen
in `state=hold`, `attempts_used=1` (von `MAX_ADDITIONAL_REQUESTS=3`),
`last_reason` beginnt mit `transport_error:`, OHNE `best_candidate_block`
(das Mitglied fehlte bereits im allerersten Harvest komplett -- der
`original_block is not None`-Zweig in `pursue_group_save_correction`, der
`update_best_candidate` fuettert, wird dadurch NIE erreicht) UND mit
gesetztem `bound_prev_ref_by_member` (unveraenderter Vorzustand gebunden).

Deckt ab:
  (1) Baseline (unveraendertes Verhalten): die beiden bestehenden Best-
      effort-Resume-Pfade (`resume_hold_via_transport_error_best_effort`/
      `resume_hold_via_structural_best_effort`) greifen NICHT (kein
      Kandidat) -- UND ein regulaerer Folgeaufruf von `pursue_group_save_
      correction` (z.B. die naechste normale Tischrunde) laesst den HOLD
      unveraendert OHNE jeden neuen GM-Call (keine automatische
      Wiederaufnahme ohne erfuellte Guards). Das ist der Zustand, der ohne
      diesen Fix fuer IMMER bestehen bleibt (Baseline-rot fuer "ein
      bewusster Re-Send ist moeglich").
  (2) Der neue, NUR vom Betreiber erreichbare Pfad (`authorize_transport_
      error_fresh_resend`) lehnt falsche Provenienz/einen Nicht-Transport-
      HOLD-Grund/einen bereits vorhandenen Kandidaten/ein bereits
      erschoepftes Budget ab -- Datensatz bleibt dabei UNVERAENDERT.
  (3) Gueltige Freigabe -> `state` wechselt GENAU auf `validating`,
      `attempts_used`/`bound_prev_ref_by_member` bleiben unveraendert,
      KEIN GM-Call in der Freigabe selbst.
  (4) Nach Freigabe sendet der naechste reguläre `pursue_group_save_
      correction`-Aufruf tatsaechlich NEU (ueber denselben echten Aufrufer,
      `begin_attempt`/Attempt-Budget wird dabei regulaer verbraucht) --
      wird die Antwort diesmal akzeptiert, schliesst die Gruppe erfolgreich
      ab.
  (5) Idempotenz: ein zweiter Freigabeversuch NACH der ersten Freigabe
      (Zustand nicht mehr `hold`) liefert `None`, OHNE einen zweiten Versand
      auszuloesen (kein doppelter `begin_attempt`/keine doppelte Zaehlung).
  (6) Ein anderes, bereits `adopted` Mitglied (Palimpsest-Analogon) bleibt
      von der gesamten Operation unberuehrt.

Geldfrei per Konstruktion: ausschliesslich In-Process-Fakes (kein echter
Transport, keine echten HTTP-Requests). Pure Python, nur `assert`, echter
Exitcode -- gleiches Muster wie `test_i_m7_transport_error_best_effort_
20261120.py`."""
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


class RaisingGmTransport:
    """Identische Fallform zu `test_i_m7_transport_error_best_effort_
    20261120.RaisingGmTransport`: jeder `.turn()`-Aufruf wirft dieselbe
    Ausnahme wie ein echter client-seitiger Transport-Timeout, OHNE je eine
    Antwort zurueckzugeben."""

    def __init__(self):
        self.calls: list[dict] = []
        self.output_limit_tokens = None

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        raise TimeoutError("timed out")


def _build(root: Path, table_id: str):
    env = make_env(root)
    lobby, table, ps_store = build_two_member_table(env, table_id=table_id)
    write_test_profile(env.run_dir)
    return env, lobby, table, ps_store


def _run_guest_entirely_missing_with_transport_error(env, lobby, table, ps_store, section_id: str, leader_save: dict):
    """Guest fehlt bereits im ALLERERSTEN Harvest komplett (kein `guest_pk`-
    Schluessel in `harvested`) -- GENAU der belegte Originalfall: das
    Mitglied liefert nie einen Entwurf, `update_best_candidate` wird daher
    NIE erreicht (`original_block is not None`-Zweig in `pursue_group_
    save_correction` greift nicht). Der anschliessende Gruppen-Korrektur-
    versand scheitert am Transport."""
    harvested = {"leader_pk": leader_save}
    harvest_completion = store.complete_section(
        lobby, table, section_id, harvested, env.states_dir, "2026-11-25",
        ZeitrissHarvestValidator(), ps_store,
    )
    assert not harvest_completion.success and harvest_completion.missing == ["guest_pk"], harvest_completion
    gm = RaisingGmTransport()
    harvested_out, completion_out = sc.pursue_group_save_correction(
        lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested),
        harvest_completion=harvest_completion, states_dir=env.states_dir, today="2026-11-25",
        harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
        gm_transport=gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
    )
    return gm, harvested_out, completion_out


# ---------------------------------------------------------------------------
# (1) Belegter Ausgangszustand + Baseline: KEIN bewusster Re-Send heute
#     moeglich, KEINE automatische Wiederaufnahme ohne Guards.
# ---------------------------------------------------------------------------


def test_1_hold_without_candidate_is_terminal_and_unresumable_via_existing_best_effort_paths():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-linus-case1")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        section_id = "section-linus-case1"
        gm, harvested_out, completion_out = _run_guest_entirely_missing_with_transport_error(
            env, lobby, table, ps_store, section_id, leader_save,
        )
        assert not completion_out.success and completion_out.missing == ["guest_pk"], completion_out
        assert len(gm.calls) == 1, gm.calls

        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        guest_record = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record["state"] == "hold", guest_record
        assert guest_record["last_reason"].startswith("transport_error:"), guest_record
        assert "timed out" in guest_record["last_reason"], guest_record
        assert guest_record["attempts_used"] == 1, guest_record
        assert guest_record.get("adopted_block") is None
        assert guest_record.get("best_candidate_block") is None, (
            "belegte Vorbedingung: KEIN Kandidat, weil das Mitglied im Erstharvest komplett abwesend war."
        )
        assert guest_record.get("bound_prev_ref_by_member") is not None, (
            "belegte Vorbedingung: der Originalvorgang ist gebunden."
        )

        # Die beiden bestehenden Best-effort-Pfade greifen NICHT (kein Kandidat).
        resumed_transport = sc.resume_hold_via_transport_error_best_effort(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed_transport is None
        resumed_structural = sc.resume_hold_via_structural_best_effort(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed_structural is None
        assert sc.load_record(env.run_dir, guest_repair_key) == guest_record, (
            "fehlgeschlagene Resume-Versuche duerfen den Datensatz NICHT veraendern."
        )

        # KEINE automatische Wiederaufnahme: ein regulaerer Folgeaufruf (naechste
        # normale Tischrunde) loest KEINEN neuen GM-Call aus und laesst den HOLD
        # unveraendert bestehen -- Baseline fuer "heute kein bewusster Re-Send".
        never_called_gm = ExplodingGmTransport()
        harvested_retry = {"leader_pk": leader_save}
        harvest_completion_retry = store.complete_section(
            lobby, table, section_id, harvested_retry, env.states_dir, "2026-11-25",
            ZeitrissHarvestValidator(), ps_store,
        )
        harvested_out2, completion_out2 = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested_retry),
            harvest_completion=harvest_completion_retry, states_dir=env.states_dir, today="2026-11-25",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=never_called_gm, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert never_called_gm.calls == 0, (
            "ein gewoehnlicher Folgeaufruf darf OHNE Betreiber-Freigabe KEINEN neuen Versand ausloesen."
        )
        assert not completion_out2.success and completion_out2.missing == ["guest_pk"], completion_out2
        guest_record_unchanged = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record_unchanged == guest_record, (
            "ohne Betreiber-Freigabe darf der HOLD-Datensatz unveraendert bleiben -- kein automatisches Freischalten."
        )


# ---------------------------------------------------------------------------
# (2) Guard-Ablehnungen des neuen Pfads -- Datensatz bleibt dabei UNVERAENDERT.
# ---------------------------------------------------------------------------


def test_2_fresh_resend_rejects_wrong_provenance_and_non_transport_reason_and_existing_candidate_and_exhausted_budget():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-linus-case2")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        section_id = "section-linus-case2"
        _gm, _ho, _co = _run_guest_entirely_missing_with_transport_error(
            env, lobby, table, ps_store, section_id, leader_save,
        )
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        guest_record_before = sc.load_record(env.run_dir, guest_repair_key)

        # Falsche Provenienz.
        for kwargs in (
            dict(char_id="CHR-FREMDE-FIGUR", table_id=table.table_id, section_id=section_id),
            dict(char_id=_GUEST_CID, table_id="t-FREMDER-TISCH", section_id=section_id),
            dict(char_id=_GUEST_CID, table_id=table.table_id, section_id="section-FREMD"),
        ):
            assert sc.authorize_transport_error_fresh_resend(env.run_dir, guest_repair_key, **kwargs) is None

        # Nicht-transport_error-HOLD-Grund (synthetisch ueberschrieben) -> kein Resend.
        drift_record = dict(guest_record_before)
        drift_record["last_reason"] = "unjustified_semantic_drift"
        sc._write_record(env.run_dir, guest_repair_key, drift_record)
        assert sc.authorize_transport_error_fresh_resend(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        ) is None
        assert sc.load_record(env.run_dir, guest_repair_key) == drift_record

        # Bereits vorhandener Kandidat -> der bestehende Best-effort-Pfad ist zustaendig, nicht dieser hier.
        with_candidate = dict(guest_record_before)
        with_candidate["best_candidate_block"] = full_v7_save(_GUEST_CID, name="Guest")
        sc._write_record(env.run_dir, guest_repair_key, with_candidate)
        assert sc.authorize_transport_error_fresh_resend(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        ) is None
        assert sc.load_record(env.run_dir, guest_repair_key) == with_candidate

        # Budget bereits erschoepft -> kein weiterer Versand, das ist der SAVECOMPAT-/Best-effort-Abschlussweg.
        exhausted = dict(guest_record_before)
        exhausted["attempts_used"] = sc.MAX_ADDITIONAL_REQUESTS
        sc._write_record(env.run_dir, guest_repair_key, exhausted)
        assert sc.authorize_transport_error_fresh_resend(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        ) is None
        assert sc.load_record(env.run_dir, guest_repair_key) == exhausted

        # Bereits adoptiert -> keine Freigabe mehr noetig/zulaessig.
        adopted = dict(guest_record_before)
        adopted["state"] = "adopted"
        adopted["adopted_block"] = full_v7_save(_GUEST_CID, name="Guest")
        sc._write_record(env.run_dir, guest_repair_key, adopted)
        assert sc.authorize_transport_error_fresh_resend(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        ) is None
        assert sc.load_record(env.run_dir, guest_repair_key) == adopted


# ---------------------------------------------------------------------------
# (3)+(4) Gueltige Freigabe -> state=validating, KEIN GM-Call in der
#         Freigabe selbst; der naechste reguläre Aufruf sendet dann
#         TATSAECHLICH neu und schliesst bei akzeptierter Antwort ab.
# ---------------------------------------------------------------------------


def test_3_4_valid_authorization_flips_to_validating_then_next_regular_call_actually_resends_and_completes():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-linus-case3")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        section_id = "section-linus-case3"
        _gm, _ho, _co = _run_guest_entirely_missing_with_transport_error(
            env, lobby, table, ps_store, section_id, leader_save,
        )
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)
        guest_record_before = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record_before["state"] == "hold"

        resumed = sc.authorize_transport_error_fresh_resend(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed is not None and resumed["state"] == "validating", resumed
        # Attempt-Budget/Bindung bleiben unveraendert -- der eigentliche Versand
        # (begin_attempt) ist NICHT Teil der Freigabe selbst.
        assert resumed["attempts_used"] == guest_record_before["attempts_used"] == 1
        assert resumed["bound_prev_ref_by_member"] == guest_record_before["bound_prev_ref_by_member"]
        assert resumed.get("adopted_block") is None and resumed.get("best_candidate_block") is None

        # Jetzt antwortet der GM beim naechsten regulaeren Aufruf gueltig --
        # derselbe echte Aufrufer (`pursue_group_save_correction`), KEIN
        # Sonder-Codepfad.
        from _section_completion_resume_fixtures import debrief_with_marker

        guest_new = full_v7_save(_GUEST_CID, name="Guest")
        gm2 = ScriptedGmTransport([debrief_with_marker({"guest": guest_new})])
        harvested2 = {"leader_pk": leader_save}
        harvest_completion2 = store.complete_section(
            lobby, table, section_id, harvested2, env.states_dir, "2026-11-25",
            ZeitrissHarvestValidator(), ps_store,
        )
        harvested_out2, completion_out2 = sc.pursue_group_save_correction(
            lobby=lobby, table=table, section_id=section_id, harvested=dict(harvested2),
            harvest_completion=harvest_completion2, states_dir=env.states_dir, today="2026-11-25",
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            gm_transport=gm2, cid_to_pk=_CID_TO_PK, harvest_extractor=zeitriss_saves.harvest_from_debrief,
        )
        assert len(gm2.calls) == 1, (
            f"der freigegebene Datensatz muss GENAU EINEN neuen Versand bei der naechsten regulaeren "
            f"Fortsetzung ausloesen: calls={gm2.calls}"
        )
        assert completion_out2.success, completion_out2
        assert harvested_out2["guest_pk"] == guest_new

        guest_record_after = sc.load_record(env.run_dir, guest_repair_key)
        assert guest_record_after["state"] == "adopted", guest_record_after
        assert guest_record_after["attempts_used"] == 2, (
            "der frische Resend muss das Attempt-Budget regulaer ueber begin_attempt verbrauchen."
        )


# ---------------------------------------------------------------------------
# (5) Idempotenz: zweite Freigabe NACH der ersten (Zustand nicht mehr hold)
#     -> None, kein zweiter Versand/keine doppelte Zaehlung.
# ---------------------------------------------------------------------------


def test_5_second_authorization_after_first_is_a_no_op_no_double_dispatch():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-linus-case4")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        section_id = "section-linus-case4"
        _gm, _ho, _co = _run_guest_entirely_missing_with_transport_error(
            env, lobby, table, ps_store, section_id, leader_save,
        )
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)

        resumed_first = sc.authorize_transport_error_fresh_resend(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed_first is not None and resumed_first["state"] == "validating"
        record_after_first = sc.load_record(env.run_dir, guest_repair_key)

        # Zweites "Bestaetigen" (z.B. erneutes Oeffnen desselben TUI-Menues) --
        # state ist nicht mehr "hold", der Guard greift, KEINE zweite Mutation.
        resumed_second = sc.authorize_transport_error_fresh_resend(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        assert resumed_second is None, (
            f"ein bereits freigegebener (nicht mehr hold) Datensatz darf NICHT erneut freigegeben werden: {resumed_second}"
        )
        record_after_second_attempt = sc.load_record(env.run_dir, guest_repair_key)
        assert record_after_second_attempt == record_after_first, (
            "ein No-op-Freigabeversuch darf den Datensatz NICHT veraendern (kein zweiter Write)."
        )
        assert record_after_second_attempt["attempts_used"] == 1, (
            "KEIN begin_attempt durch die Freigabe selbst -- das Budget wird erst beim tatsaechlichen Versand verbraucht."
        )


# ---------------------------------------------------------------------------
# (6) Ein anderes, bereits adoptiertes Mitglied (Palimpsest-Analogon) bleibt
#     von der gesamten Operation unberuehrt.
# ---------------------------------------------------------------------------


def test_6_other_already_adopted_member_untouched():
    with tempfile.TemporaryDirectory() as td:
        env, lobby, table, ps_store = _build(Path(td), "t-linus-case5")
        leader_save = full_v7_save(_LEADER_CID, name="Leader")
        section_id = "section-linus-case5"
        _gm, _ho, _co = _run_guest_entirely_missing_with_transport_error(
            env, lobby, table, ps_store, section_id, leader_save,
        )
        guest_repair_key = domain.group_repair_key(table.table_id, section_id, _GUEST_CID)

        # Leader-Analogon zum "adopted" Palimpsest-Mitglied: eigener, FREMDER
        # Korrekturdatensatz, der NICHT Teil dieser Operation ist.
        leader_repair_key = domain.group_repair_key(table.table_id, section_id, _LEADER_CID)
        leader_record = sc.load_or_init_record(
            env.run_dir, leader_repair_key, persona_key="leader_pk", char_id=_LEADER_CID,
            operation_key=sc.ROLE_GROUP, table_id=table.table_id, section_id=section_id,
        )
        leader_adopted = sc.mark_adopted(env.run_dir, leader_repair_key, adopted_block=leader_save)
        assert leader_adopted["state"] == "adopted"

        sc.authorize_transport_error_fresh_resend(
            env.run_dir, guest_repair_key, char_id=_GUEST_CID, table_id=table.table_id, section_id=section_id,
        )
        leader_record_after = sc.load_record(env.run_dir, leader_repair_key)
        assert leader_record_after == leader_adopted, (
            "die Freigabe fuer das Gast-Mitglied darf den FREMDEN, bereits adoptierten Leader-Datensatz NICHT anfassen."
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
