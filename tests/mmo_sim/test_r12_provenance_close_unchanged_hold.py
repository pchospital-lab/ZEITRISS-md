#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_provenance_close_unchanged_hold.py — R12-W75:
F02-UNCHANGED-HOLD, ein geschlossenes Admissionfenster migriert einen
bereits HOLD/WINDOW_PAUSED-Datensatz NICHT allein deshalb, weil der neu
berechnete Deadline-Grund einen ANDEREN Deadlinewert traegt
(`mmo_sim/core/save_correction.py:mark_window_paused`).

Abdeckung (W75-BRIEF.md PFLICHT-ABLAUF Punkt 3(e)):
  ein bereits VOR diesem Fix geschriebener Legacy-`STATE_HOLD` (OHNE
  `window_paused`-Vorlauf) bleibt bei einem erneuten Resume-Versuch
  BYTEGLEICH (PRE==POST), SOLANGE die Admission NACHWEISLICH weiterhin
  geschlossen ist -- SOWOHL bei exakt demselben abgelaufenen Deadlinewert
  (idempotent, bereits W74-Verhalten) ALS AUCH bei einem ANDEREN, aber
  ebenfalls abgelaufenen Deadlinewert (W74-Bug: `mark_window_paused`s
  Idempotenz pruefte bisher NUR Textgleichheit und migrierte deshalb
  faelschlich `hold` -> `window_paused` samt Ueberschreiben von
  `last_reason`). Oeffnet sich das Fenster danach TATSAECHLICH, bleibt der
  Datensatz regulaer fortsetzbar (`status="accepted"`, derselbe Slot1).

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
from _r12_provenance_close_fixture import ExplodingGm, ScriptedGm, wallet_as_number  # noqa: E402
from _r12_window_hold_fixture import close_window, deadline_reason, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

ROLE_CREATION = save_correction_domain.ROLE_CREATION


def _snapshot(run_dir: Path) -> dict:
    return {
        str(p.relative_to(run_dir)): p.read_bytes()
        for p in run_dir.rglob("*") if p.is_file()
    }


def _seed_legacy_hold(run_dir, participant_id, char_id, reason):
    repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
    save_correction.load_or_init_record(
        run_dir, repair_key, persona_key=participant_id, char_id=char_id,
        operation_key=ROLE_CREATION, errors=["economy.wallets.*"],
    )
    save_correction.begin_attempt(run_dir, repair_key)
    legacy = save_correction.mark_hold(run_dir, repair_key, reason=reason)
    assert legacy["state"] == "hold" and legacy["attempts_used"] == 1
    return repair_key


# ---------------------------------------------------------------------------
# (e1) derselbe abgelaufene Deadlinewert -- bereits W74-Verhalten, Regression.
# ---------------------------------------------------------------------------

def test_e1_same_expired_deadline_value_stays_byte_identical():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        participant_id, char_id = "p75_unchanged_same", "CHR-75-UNCHANGED-SAME"
        reason = close_window(run_dir, deadline=1700000000.0)
        repair_key = _seed_legacy_hold(run_dir, participant_id, char_id, reason)

        pre = _snapshot(run_dir)
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=wallet_as_number(char_id), gm_transport=gm,
        )
        post = _snapshot(run_dir)
        assert outcome.status == "hold" and outcome.reason == reason, outcome
        assert gm.calls == [], "KEIN Transport-Call -- Fenster weiterhin geschlossen."
        assert pre == post, (
            f"PRE==POST verletzt bei IDENTISCHEM Deadlinewert -- "
            f"{sorted(set(pre) ^ set(post)) or [k for k in pre if pre[k] != post.get(k)]}"
        )
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "hold", record


# ---------------------------------------------------------------------------
# (e2) ANDERER abgelaufener Deadlinewert -- der eigentliche W75-Fix.
# ---------------------------------------------------------------------------

def test_e2_different_expired_deadline_value_still_stays_byte_identical():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        participant_id, char_id = "p75_unchanged_diff", "CHR-75-UNCHANGED-DIFF"
        original_reason = close_window(run_dir, deadline=1700000000.0)
        repair_key = _seed_legacy_hold(run_dir, participant_id, char_id, original_reason)

        # Ein ANDERER Deadlinewert -- Admission bleibt WEITERHIN geschlossen,
        # der `reason`-TEXT ist aber textuell verschieden von `original_reason`.
        new_reason = close_window(run_dir, deadline=1750000000.0)
        assert new_reason != original_reason, "Testvoraussetzung: tatsaechlich ein ANDERER Deadlinewert/Text."

        pre = _snapshot(run_dir)
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=wallet_as_number(char_id), gm_transport=gm,
        )
        post = _snapshot(run_dir)
        assert outcome.status == "hold", outcome
        assert gm.calls == [], "KEIN Transport-Call -- Fenster bleibt geschlossen (nur mit ANDEREM Deadlinewert)."
        assert pre == post, (
            f"PRE==POST verletzt bei ANDEREM, aber weiterhin abgelaufenem Deadlinewert (W75-Bug) -- "
            f"{sorted(set(pre) ^ set(post)) or [k for k in pre if pre[k] != post.get(k)]}"
        )
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "hold", (
            f"KEIN Label-Wechsel hold->window_paused allein wegen eines anderen Deadlinewerts -- {record}"
        )
        assert record["last_reason"] == original_reason, (
            f"last_reason darf NICHT durch den neuen Deadlinewert ueberschrieben werden -- {record}"
        )

        # --- danach oeffnet sich das Fenster TATSAECHLICH -- derselbe
        # Slot1 bleibt regulaer fortsetzbar (Invariante 1/3/4 unveraendert).
        open_window(run_dir)
        valid_block = full_v7_save(char_id, name="Flo")
        gm2 = ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome2 = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=wallet_as_number(char_id), gm_transport=gm2,
        )
        assert outcome2.status == "accepted" and outcome2.block == valid_block, outcome2
        assert len(gm2.calls) == 1 and gm2.calls[0][0] == 1, (
            f"genau EIN Transport-Call, derselbe Slot1 (turn_idx=attempts_used=1) -- {gm2.calls}"
        )
        record2 = save_correction.load_record(run_dir, repair_key)
        assert record2["attempts_used"] == 1, "Zaehler bleibt unangetastet -- derselbe Slot, kein 2. Versuch."
        assert record2["state"] == "adopted"


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
