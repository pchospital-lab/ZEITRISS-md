#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_binding_lifecycle_generation_counterpart.py —
R12-W77: F02-GENERATION-Fix, 01_BINDUNGSERHALT.md §C,
CASES.json L08-GENERATION (bool/int/float-Typwiderspruch UND einseitig
fehlende notwendige Gegenseite).

`_verify_legacy_provenance` (`mmo_sim/core/save_correction.py`) verglich
`generation` VOR diesem Fix mit `!=` (Python-Wertgleichheit) -- `1 == True`
UND ein einseitig vorhandener Wert schaltete die Pruefung automatisch ab
(GENERALREVIEW.md §5, FINDINGS.json R03-GENERATION). Diese Suite deckt
GENAU die Faelle ab, die aus den umbenannten W76-Tests
(`test_r12_origin_finish_generation.py::test_missing_caller_*`/
`test_missing_record_*`, jetzt echte Generationslosigkeit auf BEIDEN Seiten)
herausgeloest wurden:

  (a) original_generation gesetzt, record.generation fehlt (einseitig) -> HOLD.
  (b) original_generation fehlt, record.generation gesetzt (einseitig) -> HOLD.
  (c) `(1, True)` -- Bug-Beispiel aus GENERALREVIEW.md §5 woertlich -> HOLD.
  (d) `(True, 1)` -- GENAUSO woertlich aus GENERALREVIEW.md §5 -> HOLD.
  (e) `(7.0, 7)` -- float/int, gleicher numerischer Wert, anderer Typ -> HOLD.
  (f) `(7, "7")` -- int/string -- HOLD (Regressionsbeleg, bereits vorher
      durch den reinen `!=`-Vergleich erkannt, bleibt erhalten).

Gegen `w76-source` liefern (c)/(d) `accepted` statt `hold` -- der Bug
woertlich aus GENERALREVIEW.md §5 reproduziert.

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
from _r12_provenance_close_fixture import ExplodingGm, seed_original_request, wallet_as_number  # noqa: E402
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


def _run_case(label, record_generation, original_generation):
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = f"w77_gen_{label}", f"CHR-77-GEN-{label.upper()}"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        draft = wallet_as_number(char_id)
        request_id = seed_original_request(
            run_dir, participant=participant_id, table_id=None, section_id=None,
            role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX, evidence_block=draft,
        )
        _build_null_bound_hold_record_with_generation(run_dir, repair_key, participant_id, char_id, record_generation)

        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        kwargs = dict(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=draft, gm_transport=gm,
            original_request_id=request_id, original_evidence=draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
        )
        if original_generation is not _MISSING:
            kwargs["original_generation"] = original_generation
        outcome = save_correction.pursue_single_figure_correction(**kwargs)
        assert outcome.status == "hold" and outcome.reason == "legacy_provenance_unverified", (
            f"Fall {label!r} (record.generation={record_generation!r}, "
            f"original_generation={original_generation!r}): erwartet kontrollierten HOLD -- {outcome}"
        )
        assert gm.calls == [], f"Fall {label!r}: KEIN Transport-Call -- {gm.calls}"
        assert len(request_ledger._all_records(run_dir)) == before, f"Fall {label!r}: 0 neue Requestdatensaetze."


_MISSING = object()


# ---------------------------------------------------------------------------
# (a)/(b) einseitig fehlende notwendige Gegenseite -> HOLD.
# ---------------------------------------------------------------------------

def test_a_caller_generation_present_record_generation_missing_holds():
    _run_case("misscaller", record_generation=None, original_generation=5)


def test_b_record_generation_present_caller_generation_missing_holds():
    _run_case("missrecord", record_generation=7, original_generation=_MISSING)


# ---------------------------------------------------------------------------
# (c)/(d) bool/int-Typwiderspruch -- GENERALREVIEW.md §5 woertlich.
# ---------------------------------------------------------------------------

def test_c_int_one_vs_bool_true_is_a_type_contradiction_holds():
    _run_case("onetrue", record_generation=True, original_generation=1)


def test_d_bool_true_vs_int_one_is_a_type_contradiction_holds():
    _run_case("trueone", record_generation=1, original_generation=True)


# ---------------------------------------------------------------------------
# (e) float/int-Typwiderspruch, gleicher numerischer Wert.
# ---------------------------------------------------------------------------

def test_e_float_seven_vs_int_seven_is_a_type_contradiction_holds():
    _run_case("floatint", record_generation=7, original_generation=7.0)


# ---------------------------------------------------------------------------
# (f) int/string-Widerspruch (Regressionsbeleg).
# ---------------------------------------------------------------------------

def test_f_int_seven_vs_string_seven_is_a_type_contradiction_holds():
    _run_case("intstring", record_generation=7, original_generation="7")


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
