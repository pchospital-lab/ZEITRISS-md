#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_origin_finish_generation.py — R12-W76: F02 §B/R03
Generation nur dort als Pflichtwert, wo Operation/Caller/Record tatsaechlich
einen Wert tragen (`mmo_sim/core/save_correction.py:_verify_legacy_
provenance`).

KEIN Produktfix in dieser Datei -- `_verify_legacy_provenance` vergleicht
`generation` bereits NUR, wenn SOWOHL `original_generation` ALS AUCH der
gespeicherte Korrekturdatensatz selbst (`record.get("generation")`)
tatsaechlich einen Wert tragen (s. Zeilen ~483-487 dort). Diese Suite belegt
diese bereits korrekte Abgrenzung mit echten Kontrollen ueber die neue
R12-W76-R01-(b)-Route (`bound_block=None` + Herkunftsbehauptung, s.
`test_r12_origin_finish_null_binding.py`), weil DIESE Route
`_verify_legacy_provenance` tatsaechlich erreicht -- der reale
`creation_service`-Call kennt laut W75-Quelle KEINE Generation und bleibt
deshalb unveraendert (s. W76-REPORT.md "nicht geaendert").

Abdeckung (CASES.json GENERATION):
  (pos)  `record.generation` UND `original_generation` gesetzt UND gleich
         -> KEINE zusaetzliche Ablehnung, Herkunft verifiziert sich.
  (neg)  beide gesetzt, ABER verschieden (Widerspruch) -> HOLD.
  (type) beide gesetzt, verschiedener Typ UND verschiedener Wert
         (Typwiderspruch) -> HOLD (derselbe `!=`-Vergleich, kein
         Typzwang).
  (miss-caller) `original_generation=None` (Aufrufer liefert KEINEN Wert),
         `record.generation` gesetzt -> Vergleich entfaellt, Herkunft
         verifiziert sich trotzdem (kein erfundener Pflichtwert).
  (miss-record) `record.generation=None` (nie gesetzt), `original_
         generation` gesetzt -> Vergleich entfaellt genauso.

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
from _r12_provenance_close_fixture import ExplodingGm, ScriptedGm, seed_original_request, wallet_as_number  # noqa: E402
from _r12_window_hold_fixture import deadline_reason, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

ROLE_CREATION = save_correction_domain.ROLE_CREATION
_ORIGINAL_ROLE = "creation_dialog"
_ORIGINAL_TURN_IDX = 0


def _build_null_bound_hold_record_with_generation(run_dir, repair_key, participant_id, char_id, generation):
    save_correction.load_or_init_record(
        run_dir, repair_key, persona_key=participant_id, char_id=char_id,
        operation_key=ROLE_CREATION, generation=generation, errors=["economy.wallets.*"],
    )
    save_correction.begin_attempt(run_dir, repair_key)
    reason = deadline_reason(1700000000.0)
    legacy = save_correction.mark_hold(run_dir, repair_key, reason=reason)
    assert legacy["generation"] == generation and legacy["bound_block"] is None, legacy


def _seed_matching_origin(run_dir, participant_id, char_id, draft):
    return seed_original_request(
        run_dir, participant=participant_id, table_id=None, section_id=None,
        role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX, evidence_block=draft,
    )


# ---------------------------------------------------------------------------
# (pos) beide gesetzt UND gleich -> verifiziert sich, accepted.
# ---------------------------------------------------------------------------

def test_pos_consistent_generation_on_both_sides_is_accepted():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_gen_pos", "CHR-76-GEN-POS"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        draft = wallet_as_number(char_id)
        request_id = _seed_matching_origin(run_dir, participant_id, char_id, draft)
        _build_null_bound_hold_record_with_generation(run_dir, repair_key, participant_id, char_id, 5)

        valid_block = full_v7_save(char_id, name="Flo")
        # F-WALLET-LOSS: wertgleicher Betrag (500) wie `draft`.
        valid_block["economy"] = {"wallets": {char_id: {"balance": 500}}}
        gm = ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=draft, gm_transport=gm,
            original_request_id=request_id, original_evidence=draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX, original_generation=5,
        )
        assert outcome.status == "accepted" and outcome.block == valid_block, outcome


# ---------------------------------------------------------------------------
# (neg) beide gesetzt, verschieden -> HOLD.
# ---------------------------------------------------------------------------

def test_neg_contradictory_generation_holds_before_transport():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_gen_neg", "CHR-76-GEN-NEG"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        draft = wallet_as_number(char_id)
        request_id = _seed_matching_origin(run_dir, participant_id, char_id, draft)
        _build_null_bound_hold_record_with_generation(run_dir, repair_key, participant_id, char_id, 5)

        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=draft, gm_transport=gm,
            original_request_id=request_id, original_evidence=draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX, original_generation=99,
        )
        assert outcome.status == "hold" and outcome.reason == "legacy_provenance_unverified", outcome
        assert gm.calls == [], gm.calls
        assert len(request_ledger._all_records(run_dir)) == before


# ---------------------------------------------------------------------------
# (type) beide gesetzt, verschiedener Typ -> HOLD (derselbe !=-Vergleich).
# ---------------------------------------------------------------------------

def test_type_contradiction_generation_holds_before_transport():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_gen_type", "CHR-76-GEN-TYPE"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        draft = wallet_as_number(char_id)
        request_id = _seed_matching_origin(run_dir, participant_id, char_id, draft)
        # bewusst ein falsch typisierter Bestandswert (String statt int) --
        # derselbe `!=`-Vergleich faengt das ohne jede Typkonvertierung.
        _build_null_bound_hold_record_with_generation(run_dir, repair_key, participant_id, char_id, "5")

        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=draft, gm_transport=gm,
            original_request_id=request_id, original_evidence=draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX, original_generation=5,
        )
        assert outcome.status == "hold" and outcome.reason == "legacy_provenance_unverified", outcome
        assert gm.calls == [], gm.calls
        assert len(request_ledger._all_records(run_dir)) == before


# ---------------------------------------------------------------------------
# (miss-caller) original_generation=None -> Vergleich entfaellt, accepted.
# ---------------------------------------------------------------------------

def test_missing_caller_generation_is_not_required_and_is_accepted():
    """R12-W77 (F02-GENERATION-Fix, 01_BINDUNGSERHALT.md §C): W76 liess hier
    EINSEITIG eine Caller-Generation fehlen UND record.generation=5 gesetzt
    durchgehen -- genau der Bug (GENERALREVIEW.md §5: "ein einseitig
    vorhandener Wert schaltet seine Pruefung NICHT automatisch ab"). Dieser
    Testname beschreibt den tatsaechlich weiterhin korrekten Fall: generation
    ist auf BEIDEN Seiten (Caller UND Record) NICHT gesetzt -- echte
    Generationslosigkeit (None/None) bleibt unveraendert akzeptiert, kein
    erfundener Pflichtwert. Der vormals hier getestete einseitige Fall (eine
    Seite gesetzt, die andere fehlt) MUSS jetzt HOLD liefern und wandert in
    tests/mmo_sim/test_r12_binding_lifecycle_generation_counterpart.py."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_gen_misscaller", "CHR-76-GEN-MISSCALLER"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        draft = wallet_as_number(char_id)
        request_id = _seed_matching_origin(run_dir, participant_id, char_id, draft)
        # R12-W77: record.generation ist jetzt EBENFALLS None -- echte
        # Generationslosigkeit auf BEIDEN Seiten (vorher: 5, einseitig).
        _build_null_bound_hold_record_with_generation(run_dir, repair_key, participant_id, char_id, None)

        valid_block = full_v7_save(char_id, name="Flo")
        # F-WALLET-LOSS: wertgleicher Betrag (500) wie `draft`.
        valid_block["economy"] = {"wallets": {char_id: {"balance": 500}}}
        gm = ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=draft, gm_transport=gm,
            original_request_id=request_id, original_evidence=draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
            # original_generation bewusst NICHT uebergeben (Default None) --
            # UND record.generation=None (s.o.): echte Generationslosigkeit.
        )
        assert outcome.status == "accepted" and outcome.block == valid_block, (
            f"echte Generationslosigkeit (beide Seiten None) darf KEIN erfundener Pflichtwert sein -- {outcome}"
        )


# ---------------------------------------------------------------------------
# (miss-record) record.generation=None -> Vergleich entfaellt, accepted.
# ---------------------------------------------------------------------------

def test_missing_record_generation_is_not_required_and_is_accepted():
    """R12-W77 (F02-GENERATION-Fix, 01_BINDUNGSERHALT.md §C): dieselbe
    Korrektur wie beim Caller-Fall oben -- record.generation=None (wie
    bisher) UND original_generation jetzt EBENFALLS NICHT uebergeben (vorher
    7, einseitig). Echte Generationslosigkeit auf BEIDEN Seiten bleibt
    unveraendert akzeptiert. Der vormals hier getestete einseitige Fall
    wandert in test_r12_binding_lifecycle_generation_counterpart.py."""
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_gen_missrecord", "CHR-76-GEN-MISSRECORD"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        draft = wallet_as_number(char_id)
        request_id = _seed_matching_origin(run_dir, participant_id, char_id, draft)
        _build_null_bound_hold_record_with_generation(run_dir, repair_key, participant_id, char_id, None)

        valid_block = full_v7_save(char_id, name="Flo")
        # F-WALLET-LOSS: wertgleicher Betrag (500) wie `draft`.
        valid_block["economy"] = {"wallets": {char_id: {"balance": 500}}}
        gm = ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=draft, gm_transport=gm,
            original_request_id=request_id, original_evidence=draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
            # original_generation bewusst NICHT uebergeben (Default None, vorher 7) --
            # record.generation ist ebenfalls None: echte Generationslosigkeit.
        )
        assert outcome.status == "accepted" and outcome.block == valid_block, (
            f"echte Generationslosigkeit (beide Seiten None) darf KEIN erfundener Pflichtwert sein -- {outcome}"
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
