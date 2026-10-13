#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_binding_lifecycle_format_fix_after_conflict.py —
R12-W77: F02-LIFECYCLE-Fix, 01_BINDUNGSERHALT.md §A, CASES.json
L01-KNOWN-CONFLICT (positiv): "clean format-only response => accepted
within Max3."

Gegenstueck zu `test_r12_binding_lifecycle_conflict_preserves_binding.py`:
derselbe Ablauf (konkret gebundener, wallet-fehlerhafter Originalentwurf +
echte mehrdeutige SL-Zwischenantwort), aber die DRITTE Antwort behebt NUR
den tatsaechlich gemeldeten Schemafehler (Wallet-Struktur) OHNE Identitaet/
Name/Callsign/Wallet-WERT zu aendern. 01_BINDUNGSERHALT.md §A verlangt
ausdruecklich, dass dieser Fall WEITERHIN annehmbar bleibt -- "KEINE
pauschale terminale Sperre jeder Mehrdeutigkeit als Billigfix". Belegt, dass
der R01-LIFECYCLE-Fix (Erhalt der Vergleichsbasis nach Konflikt) NICHT zu
einer Ueberreaktion fuehrt, die JEDE Mehrdeutigkeit terminal haelt.

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
from _r12_provenance_close_fixture import ScriptedGm, wallet_as_number  # noqa: E402
from _r12_window_hold_fixture import open_window  # noqa: E402

import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402


def _ambiguous_text(char_id: str) -> str:
    block_a = full_v7_save(char_id, name="Konflikt A")
    block_b = full_v7_save(char_id, name="Konflikt B")
    return (
        "```json\n" + json.dumps(block_a) + "\n```\n"
        "```json\n" + json.dumps(block_b) + "\n```"
    )


# ---------------------------------------------------------------------------
# L01-KNOWN-CONFLICT (positiv): Konflikt + echte Formatkorrektur -> accepted.
# ---------------------------------------------------------------------------

def test_ambiguous_conflict_then_same_identity_format_fix_is_accepted():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w77_conflict_fmt", "CHR-77-CONFLICT-FMT"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id, name="Original Testfigur")
        # Dieselbe Identitaet/Name/Wallet-WERT -- NUR die Wallet-STRUKTUR
        # wird korrigiert (genau der zuvor gemeldete Schemafehler).
        format_fixed = full_v7_save(char_id, name="Original Testfigur")
        gm = ScriptedGm([
            _ambiguous_text(char_id),
            "```json\n" + json.dumps(format_fixed) + "\n```",
        ])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=original_draft, gm_transport=gm,
        )
        assert outcome.status == "accepted" and outcome.block == format_fixed, (
            f"R12-W77: eine echte Formatkorrektur (gleiche Identitaet/Name/Wallet-Wert, nur Struktur "
            f"korrigiert) NACH einer Konfliktantwort bleibt annehmbar -- KEINE pauschale terminale "
            f"Sperre jeder Mehrdeutigkeit -- {outcome}"
        )
        assert len(gm.calls) == 2, gm.calls
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "adopted" and record["attempts_used"] == 2, record


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
