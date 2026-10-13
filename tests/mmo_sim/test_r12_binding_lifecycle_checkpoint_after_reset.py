#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_binding_lifecycle_checkpoint_after_reset.py —
R12-W77: F02-LIFECYCLE-Fix, 01_BINDUNGSERHALT.md §A, CASES.json
L03-CHECKPOINT.

"Crash nach persistiertem Reset / vor naechstem Versuch: Resume nutzt
dauerhaftes Original, nicht Calleraustausch; keine Doppelzaehlung."

Simuliert einen Prozessabsturz GENAU zwischen einem persistierten
Konflikt-Reset (`_reset_for_next_attempt`, Zustand kehrt auf `validating`
zurueck, `bound_block` bleibt der durabel gebundene Originalentwurf) und dem
naechsten `begin_attempt` -- OHNE den vollen Retry-Loop in EINEM
Funktionsaufruf zu durchlaufen (der wuerde sofort selbst weiterlaufen). Der
naechste `pursue_single_figure_correction`-Aufruf (die "neue Prozessinstanz")
erhaelt dabei bewusst einen ANDEREN `candidate_block`-Parameter als den
durabel gebundenen -- sie DARF diesen NICHT uebernehmen.

VOR diesem Fix (R12-W77 CHANGE 1, `pursue_single_figure_correction` Zeilen
~613ff): ein Resume in einem neuen Aufruf setzte `current_block` bedingungs-
los auf den frisch uebergebenen `candidate_block`-Parameter, sobald der
Datensatz NICHT HOLD/WINDOW_PAUSED/ADOPTED war (hier: `validating`,
`attempts_used=1`) -- der durabel gebundene Originalentwurf ging verloren.

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

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

ROLE_CREATION = save_correction_domain.ROLE_CREATION


def test_resume_after_persisted_conflict_reset_uses_durable_original_not_caller_substitution():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w77_checkpoint", "CHR-77-CHECKPOINT"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id, name="Original Testfigur")

        # "Prozess 1": der erste Versuch wurde begonnen (begin_attempt) UND
        # erhielt bereits eine mehrdeutige Konfliktantwort, die via
        # `_reset_for_next_attempt` persistiert wurde (state zurueck auf
        # "validating", `bound_block` bleibt `original_draft`) -- GENAU HIER
        # (vor dem naechsten `begin_attempt`) wird der Absturz simuliert.
        save_correction.load_or_init_record(
            run_dir, repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, errors=["economy.wallets.*"], original_block=original_draft,
        )
        save_correction.begin_attempt(run_dir, repair_key, original_block=original_draft)
        save_correction._reset_for_next_attempt(
            run_dir, repair_key, errors=["mehrdeutige SL-Antwort"], original_block=original_draft,
        )
        pre_crash_record = save_correction.load_record(run_dir, repair_key)
        assert pre_crash_record["state"] == "validating" and pre_crash_record["attempts_used"] == 1
        assert pre_crash_record["bound_block"] == original_draft
        before_ledger = len(request_ledger._all_records(run_dir))

        # "Prozess 2" (neue Instanz, z.B. nach Neustart): der Aufrufer bringt
        # einen VOELLIG ANDEREN (ebenfalls strukturell ungueltigen, damit der
        # fruehe accepted-Kurzschluss nicht greift) `candidate_block` mit --
        # der durabel gebundene `original_draft` MUSS trotzdem die
        # Vergleichsbasis bleiben, NICHT dieser frische Parameter. Die SL-
        # Antwort ist eine ECHTE Formatkorrektur DER URSPRUENGLICHEN Figur
        # (gleicher Name "Original Testfigur", nur Wallet-Struktur behoben)
        # -- das unterscheidet scharf zwischen "Vergleichsbasis =
        # original_draft" (KEINE Drift, da Name identisch -> accepted) und
        # "Vergleichsbasis = swapped_caller_draft" (Name-Drift gegen
        # 'Swapped Caller Draft' -> faelschlich hold). Eine rein umbenannte
        # Antwort waere gegen BEIDE moeglichen Basen Drift und koennte die
        # beiden Faelle nicht unterscheiden.
        swapped_caller_draft = wallet_as_number(char_id, name="Swapped Caller Draft")
        format_fixed_original = full_v7_save(char_id, name="Original Testfigur")
        gm = ScriptedGm([
            "```json\n" + json.dumps(format_fixed_original) + "\n```",
        ])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=swapped_caller_draft, gm_transport=gm,
        )
        assert outcome.status == "accepted" and outcome.block == format_fixed_original, (
            f"R12-W77 L03-CHECKPOINT: der Resume MUSS den durabel gebundenen Originalentwurf "
            f"('Original Testfigur') als Vergleichsbasis nutzen, NICHT den frisch uebergebenen "
            f"Caller-Parameter ('Swapped Caller Draft') -- eine reine Formatkorrektur der "
            f"URSPRUENGLICHEN Figur muss deshalb 'accepted' sein -- tatsaechlich: {outcome}"
        )
        assert len(gm.calls) == 1, (
            f"genau EIN neuer Transport-Call fuer den fortgesetzten Slot -- keine Doppelzaehlung -- {gm.calls}"
        )
        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 2, (
            f"der Zaehler wird GENAU EINMAL weitergezaehlt (Slot2), nicht dupliziert -- {record}"
        )
        assert len(request_ledger._all_records(run_dir)) == before_ledger + 1, (
            "genau EIN neuer Requestdatensatz -- kein Doppelversand fuer denselben Slot."
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
