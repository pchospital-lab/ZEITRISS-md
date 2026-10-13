#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_binding_lifecycle_conflict_preserves_binding.py —
R12-W77: F02-LIFECYCLE-Fix, 01_BINDUNGSERHALT.md §A (R01-LIFECYCLE),
CASES.json L01-KNOWN-CONFLICT (negativ).

Reproduziert GENERALREVIEW.md §3 "Eigene direkte Gegenprobe" direkt gegen
`mmo_sim/core/save_correction.py:pursue_single_figure_correction`: ein
konkret gebundener Originalentwurf ("Original Testfigur", nur der Wallet-
Aufbau fehlerhaft) erhaelt zuerst eine echte mehrdeutige SL-Zwischenantwort
(zwei widersprechende Rohbloecke derselben char_id in EINER Antwort), dann
eine strukturell gueltige, aber UMBENANNTE Folgeantwort ("Changed
Testfigur").

VOR diesem Fix (W75/W76, FINDINGS.json R01-LIFECYCLE): der Konflikt setzte
`current_block=None` und persistierte das via `_reset_for_next_attempt` --
die umbenannte Folgeantwort wurde ohne Drift-Pruefung `accepted` (C38
ADV1/ADV2). NACH diesem Fix: die Konfliktantwort darf die belegte
Vergleichsbasis NICHT loeschen -- die umbenannte Antwort bleibt
`unjustified_semantic_drift`-HOLD. Gegen `w76-source` (Baseline) liefert
dieselbe Testlogik `accepted` statt `hold` -- s. W77-REPORT.md fuer den
RC-/Assertion-Beleg beider Seiten.

Pure Python, nur `assert`, echter Exitcode -- gleiches Aufbaumuster wie die
bestehende Suite (z.B. `test_r12_origin_finish_null_binding.py`)."""
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
from _r12_provenance_close_fixture import ScriptedGm, wallet_as_number  # noqa: E402
from _r12_window_hold_fixture import open_window  # noqa: E402

import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402


def _ambiguous_text(char_id: str) -> str:
    """Zwei widersprechende Rohbloecke (ABWEICHENDER Inhalt) derselben
    `char_id` in EINER SL-Antwort -- `extract_checked_single` muss dies als
    echten Konflikt erkennen (`(None, konflikte)`), KEIN 'erster gewinnt'."""
    block_a = full_v7_save(char_id, name="Konflikt A")
    block_b = full_v7_save(char_id, name="Konflikt B")
    return (
        "```json\n" + json.dumps(block_a) + "\n```\n"
        "```json\n" + json.dumps(block_b) + "\n```"
    )


# ---------------------------------------------------------------------------
# L01-KNOWN-CONFLICT (negativ): Konflikt + umbenannte Folgeantwort -> HOLD.
# ---------------------------------------------------------------------------

def test_ambiguous_conflict_then_renamed_answer_stays_drift_hold_not_accepted():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w77_conflict_bind", "CHR-77-CONFLICT-BIND"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id, name="Original Testfigur")
        gm = ScriptedGm([
            _ambiguous_text(char_id),
            "```json\n" + json.dumps(full_v7_save(char_id, name="Changed Testfigur")) + "\n```",
        ])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=original_draft, gm_transport=gm,
        )
        assert outcome.status == "hold" and outcome.reason == "unjustified_semantic_drift", (
            f"R12-W77: eine mehrdeutige Zwischenantwort darf die gebundene Vergleichsbasis NICHT "
            f"loeschen -- eine spaetere UMBENANNTE Antwort bleibt Drift, NICHT 'accepted' -- {outcome}"
        )
        assert len(gm.calls) == 2, (
            f"zwei Korrektur-Transport-Calls erwartet (Konflikt-Slot + umbenannte Antwort) -- {gm.calls}"
        )
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "hold", record
        assert record["attempts_used"] == 2, (
            f"beide Versuche zaehlen (Konflikt-Slot UND die umbenannte Antwort) -- {record}"
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
