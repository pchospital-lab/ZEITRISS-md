#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_origin_finish_null_binding.py — R12-W76: F02 §A R01
null-Binding ist keine freie Inhaltsfreigabe
(`mmo_sim/core/save_correction.py:pursue_single_figure_correction`).

Bug (VOR diesem Fix, s. W76-BRIEF.md R01): `if "bound_block" in record:
current_block = record.get("bound_block")` -- bei vorhandenem Schluessel MIT
Wert `None` wurde `current_block=None`, `current_acceptance` fiel auf die
`acceptance` des AKTUELLEN `candidate_block` zurueck -> die Driftpruefung
gegen den gebundenen Originalentwurf wurde uebersprungen, obwohl der
Aufrufer (via `original_request_id`/`original_evidence`) tatsaechlich eine
historische Antwort behauptete -- eine umbenannte Figur waere durchgerutscht.

Abdeckung (CASES.json):
  R01-KNOWN-DICT     (a) konkreter `dict`-`bound_block` bleibt UNVERAENDERT
                      die Drift-Baseline -- Regressionskontrolle.
  R01-NULL-EXISTING  (b) `bound_block=None` + Aufrufer behauptet eine
                      Herkunft (`original_request_id`/`original_evidence`):
                        (b-positiv) verifiziert sich -> wird zur Drift-
                          Baseline, eine umbenannte Antwort wird GEHALTEN
                          (NICHT mehr blind akzeptiert -- der eigentliche
                          Fix).
                        (b-negativ) verifiziert sich NICHT -> HOLD VOR
                          Transport, KEIN Drift-Skip.
  R01-FIRST-MISSING  (d) `bound_block=None` OHNE jede Herkunftsbehauptung
                      (beide `None`) -- unveraendert ueber den bestehenden
                      Weg korrigierbar (keine Regression fuer die
                      bestehenden `test_r12_window_hold_single_figure.py`-
                      Faelle (b)/(d), die genauso aufgebaut sind).
  R01-FIRST-AMBIGUOUS (e) `forced_conflicts`-Resume (candidate_block=None,
                      KEINE Herkunftsbehauptung, exakt wie
                      `creation_service._attempt_correction(None, ...)`)
                      bleibt UNBERUEHRT korrigierbar -- kein
                      `legacy_provenance_unverified`-HOLD, Transport wird
                      regulaer versucht.

Pure Python, nur `assert`, echter Exitcode."""
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
from _r12_provenance_close_fixture import (  # noqa: E402
    ExplodingGm, ScriptedGm, seed_original_request, wallet_as_number,
)
from _r12_window_hold_fixture import close_window, deadline_reason, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

ROLE_CREATION = save_correction_domain.ROLE_CREATION
_ORIGINAL_ROLE = "creation_dialog"
_ORIGINAL_TURN_IDX = 0


def _build_null_bound_hold_record(run_dir, repair_key, participant_id, char_id):
    """Exakt dasselbe Testmuster wie `test_r12_window_hold_single_figure.py`
    Faelle (b)/(d) -- `load_or_init_record` OHNE `original_block`-Kwarg
    (Default `None`), direkter `state="hold"` -- `bound_block` ist dabei
    IMMER `None` (Schluessel vorhanden, s. `load_or_init_record`), NIE
    abwesend."""
    save_correction.load_or_init_record(
        run_dir, repair_key, persona_key=participant_id, char_id=char_id,
        operation_key=ROLE_CREATION, errors=["economy.wallets.*"],
    )
    save_correction.begin_attempt(run_dir, repair_key)
    reason = deadline_reason(1700000000.0)
    legacy = save_correction.mark_hold(run_dir, repair_key, reason=reason)
    assert "bound_block" in legacy and legacy["bound_block"] is None, (
        f"Testvoraussetzung verletzt -- Schluessel muss PRAESENT und None sein: {legacy}"
    )
    return reason


# ---------------------------------------------------------------------------
# (a) R01-KNOWN-DICT -- konkreter dict-bound_block bleibt Drift-Baseline.
# ---------------------------------------------------------------------------

def test_a_known_dict_bound_block_rejects_renamed_figure_as_drift():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_r01_dict", "CHR-76-R01-DICT"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id, name="Original Testfigur")
        save_correction.load_or_init_record(
            run_dir, repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, errors=["economy.wallets.*"], original_block=original_draft,
        )
        save_correction.begin_attempt(run_dir, repair_key)
        reason = deadline_reason(1700000000.0)
        save_correction.mark_hold(run_dir, repair_key, reason=reason)

        renamed = full_v7_save(char_id, name="Changed Testfigur")
        gm = ScriptedGm(["```json\n" + json.dumps(renamed) + "\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=wallet_as_number(char_id), gm_transport=gm,
        )
        assert outcome.status == "hold" and outcome.reason == "unjustified_semantic_drift", outcome
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "hold", record


# ---------------------------------------------------------------------------
# (b-positiv) R01-NULL-EXISTING -- bound_block=None, verifizierte Herkunft
#             wird zur Drift-Baseline, eine umbenannte Antwort wird GEHALTEN.
# ---------------------------------------------------------------------------

def test_b_pos_null_binding_with_verified_origin_rejects_renamed_figure():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_r01_null_pos", "CHR-76-R01-NULLPOS"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id, name="Original Testfigur")
        original_request_id = seed_original_request(
            run_dir, participant=participant_id, table_id=None, section_id=None,
            role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX, evidence_block=original_draft,
        )
        _build_null_bound_hold_record(run_dir, repair_key, participant_id, char_id)

        renamed = full_v7_save(char_id, name="Changed Testfigur")
        gm = ScriptedGm(["```json\n" + json.dumps(renamed) + "\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=wallet_as_number(char_id), gm_transport=gm,
            original_request_id=original_request_id, original_evidence=original_draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
        )
        assert outcome.status == "hold" and outcome.reason == "unjustified_semantic_drift", (
            f"R01-NULL-EXISTING: die verifizierte Herkunft MUSS die Drift-Baseline sein -- "
            f"VOR dem Fix waere diese umbenannte Antwort faelschlich 'accepted' gewesen. "
            f"tatsaechlich: {outcome}"
        )
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "hold", record
        assert len(gm.calls) == 1, "genau EIN Transport-Call -- die Pruefung erfolgt NACH der Antwort."


# ---------------------------------------------------------------------------
# (b-negativ) R01-NULL-EXISTING -- bound_block=None, NICHT verifizierbare
#             Herkunftsbehauptung -> HOLD VOR Transport, kein Drift-Skip.
# ---------------------------------------------------------------------------

def test_b_neg_null_binding_with_rejected_origin_holds_before_transport():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_r01_null_neg", "CHR-76-R01-NULLNEG"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        actually_stored = wallet_as_number(char_id, name="Original Testfigur")
        original_request_id = seed_original_request(
            run_dir, participant=participant_id, table_id=None, section_id=None,
            role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX, evidence_block=actually_stored,
        )
        swapped_evidence = wallet_as_number(char_id, name="Changed Testfigur")
        _build_null_bound_hold_record(run_dir, repair_key, participant_id, char_id)

        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=swapped_evidence, gm_transport=gm,
            original_request_id=original_request_id, original_evidence=swapped_evidence,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
        )
        assert outcome.status == "hold" and outcome.reason == "legacy_provenance_unverified", outcome
        assert gm.calls == [], f"KEIN Transport-Call vor unverifizierter Null-Binding-Herkunft -- {gm.calls}"
        assert len(request_ledger._all_records(run_dir)) == before, "0 neue Requestdatensaetze."
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "hold" and record["last_reason"] == "legacy_provenance_unverified", record


# ---------------------------------------------------------------------------
# (d) R01-FIRST-MISSING -- bound_block=None, KEINE Herkunftsbehauptung ->
#     unveraendert korrigierbar (Regressionsbeleg fuer die bestehenden
#     test_r12_window_hold_single_figure.py-Faelle).
# ---------------------------------------------------------------------------

def test_d_null_binding_without_any_origin_claim_stays_correctable():
    """R12-W77 (Testkorrektur, 01_BINDUNGSERHALT.md §D): W76 nannte hier
    einen bestehenden, lediglich wallet-fehlerhaften Entwurf (`candidate_
    block=wallet_as_number(char_id)`, ein tatsaechlicher dict) einen
    'fehlenden Erstkandidaten' -- ein echter R01-FIRST-MISSING-Fall braucht
    aber `candidate_block=None` (WIRKLICH kein Entwurf vorhanden), nicht
    bloss einen vorhandenen, nur strukturell ungueltigen Entwurf so zu
    nennen. Fix: derselbe Legacy-HOLD-Aufbau wie (b)/(d) OHNE
    `_build_null_bound_hold_record` (dessen `errors=["economy.wallets.*"]`
    einen tatsaechlich evaluierten, nur wallet-fehlerhaften Entwurf
    unterstellt), sondern mit `errors` passend zu einem wirklich fehlenden
    Erstkandidaten UND `candidate_block=None` im eigentlichen Aufruf."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_r01_first_missing", "CHR-76-R01-FIRSTMISS"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        # R12-W77: echter fehlender Erstkandidat -- `load_or_init_record`
        # OHNE `original_block` (Default None) UND mit `errors`, die KEINEN
        # tatsaechlich vorhandenen (nur fehlerhaften) Entwurf unterstellen.
        save_correction.load_or_init_record(
            run_dir, repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, errors=["no_candidate_block_provided"],
        )
        save_correction.begin_attempt(run_dir, repair_key)
        reason = deadline_reason(1700000000.0)
        legacy = save_correction.mark_hold(run_dir, repair_key, reason=reason)
        assert "bound_block" in legacy and legacy["bound_block"] is None, (
            f"Testvoraussetzung verletzt -- Schluessel muss PRAESENT und None sein: {legacy}"
        )

        valid_block = full_v7_save(char_id, name="Flo")
        gm = ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            # R12-W77: WIRKLICH kein Erstkandidat -- candidate_block=None
            # (vorher: ein tatsaechlich vorhandener, wallet-fehlerhafter dict).
            candidate_block=None, gm_transport=gm,
        )
        assert outcome.status == "accepted" and outcome.block == valid_block, (
            f"R01-FIRST-MISSING: ein wirklich fehlender Erstkandidat (candidate_block=None, keine "
            f"Herkunftsbehauptung) bleibt ueber den bestehenden Weg unveraendert korrigierbar -- "
            f"tatsaechlich: {outcome}"
        )
        assert len(gm.calls) == 1 and gm.calls[0][0] == 1, gm.calls


# ---------------------------------------------------------------------------
# (e) R01-FIRST-AMBIGUOUS -- forced_conflicts-Resume (candidate_block=None,
#     keine Herkunftsbehauptung) bleibt unberuehrt korrigierbar.
# ---------------------------------------------------------------------------

def test_e_ambiguous_forced_conflicts_resume_stays_correctable_no_provenance_hold():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        close_reason = close_window(run_dir, deadline=1.0)
        participant_id, char_id = "w76_r01_ambiguous", "CHR-76-R01-AMBIG"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        # echte BindingError-Konflikte, exakt wie `creation_service`s eigener
        # G02/SC06-Mehrdeutigkeitsweg sie via `find_duplicate_save_ids`
        # erzeugt -- ZWEI Rohbloecke derselben char_id mit ABWEICHENDEM Inhalt.
        conflicts = save_correction_domain.find_duplicate_save_ids([
            full_v7_save(char_id, name="Rohblock A"), full_v7_save(char_id, name="Rohblock B"),
        ])
        assert conflicts, "Testvoraussetzung: echte Mehrdeutigkeitskonflikte."
        gm1 = ExplodingGm()
        outcome1 = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=None, gm_transport=gm1, forced_conflicts=conflicts,
        )
        assert outcome1.status == "hold" and outcome1.reason == close_reason, outcome1
        record1 = save_correction.load_record(run_dir, repair_key)
        assert "bound_block" in record1 and record1["bound_block"] is None, record1
        assert record1["state"] == "window_paused", record1

        open_window(run_dir)
        valid_block = full_v7_save(char_id, name="Flo")
        gm2 = ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome2 = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=None, gm_transport=gm2, forced_conflicts=conflicts,
        )
        assert outcome2.status == "accepted" and outcome2.block == valid_block, (
            f"R01-FIRST-AMBIGUOUS: KEIN 'legacy_provenance_unverified'-HOLD erwartet, "
            f"Transport MUSS regulaer versucht werden -- tatsaechlich: {outcome2}"
        )
        assert len(gm2.calls) == 1, gm2.calls


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
