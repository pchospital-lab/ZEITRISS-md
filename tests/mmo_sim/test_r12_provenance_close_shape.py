#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_provenance_close_shape.py — R12-W75: F02-SHAPE,
echte Kontrollwerte VOR jedem Transport/jeder Adoption pruefen
(`mmo_sim/core/save_correction.py:pursue_single_figure_correction`).

Abdeckung (W75-BRIEF.md PFLICHT-ABLAUF Punkt 3(c)/(d)):
  (c) ein resumierbarer HOLD/WINDOW_PAUSED-Datensatz mit `attempts_used`
      ausserhalb des gueltigen offenen Slotbereichs (1..max_attempts) ODER
      falsch typisiert (`bool` statt `int`) erreicht KEINEN synthetischen
      Transport -- `status="hold"`, `reason="invalid_resume_slot_shape"`,
      0 neue Requestdatensaetze (W74-Bug: ein solcher Wert erreichte
      bisher den Versand, erst der Ledger wies den Typ spaeter ab und
      hinterliess einen `sent`-Record).
  (d) ein Caller/Record-`section_id`-Mismatch bleibt terminal HOLD, KEIN
      Versand unter der neuen Calleridentitaet (Regressionsbeleg -- bereits
      durch `test_r12_window_resume_boundary_f02.py::test_d` abgedeckt,
      hier zusaetzlich mit einem ECHTEN Legacy-Record OHNE `bound_block`,
      um zu belegen, dass die Identitaetspruefung VOR der neuen
      Provenienzpruefung greift).

Pure Python, nur `assert`, echter Exitcode."""
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

from _r12_provenance_close_fixture import ExplodingGm, wallet_as_number, write_legacy_hold_record  # noqa: E402
from _r12_window_hold_fixture import deadline_reason, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

ROLE_CREATION = save_correction_domain.ROLE_CREATION


# ---------------------------------------------------------------------------
# (c) attempts_used ausserhalb des gueltigen Slotbereichs/falsch typisiert.
# ---------------------------------------------------------------------------

def test_c_invalid_resume_slot_shape_holds_before_any_transport():
    # "too_high" (4 > max_attempts=3) passiert `_window.is_resumable_pre_send_
    # pause`s eigenen (nur unteren) Bereichscheck und erreicht damit
    # `pursue_single_figure_correction`s NEUEN SHAPE-Check -- exakte
    # `reason="invalid_resume_slot_shape"` erwartet. "boolean_true"/
    # "wrong_type_string" werden bereits VOR diesem Punkt von `_window.
    # is_resumable_pre_send_pause`s eigenem Typcheck abgewiesen (R12-W75-
    # Nachzug dort -- sonst ein ungefangener `TypeError` bei `< 1`) und
    # bleiben ueber den ALLGEMEINEN Identitaets-/Resumierbarkeits-Terminalweg
    # HOLD (`reason` = der urspruengliche gespeicherte Deadline-Grund) --
    # fuer BEIDE Wege gilt dieselbe Kerninvariante: HOLD VOR jedem Transport,
    # 0 neue Requestdatensaetze, kein `sent`-Record.
    cases = [
        ("too_high", 4, "invalid_resume_slot_shape"),
        ("boolean_true", True, None),
        ("wrong_type_string", "2", None),
    ]
    for label, bad_attempts_used, expected_reason in cases:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            open_window(run_dir)
            participant_id, char_id = f"p75_shape_{label}", f"CHR-75-SHAPE-{label}"
            repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
            reason = deadline_reason(1700000000.0)
            legacy = write_legacy_hold_record(
                run_dir, repair_key=repair_key, persona_key=participant_id, char_id=char_id,
                operation_key=ROLE_CREATION, attempts_used=bad_attempts_used, last_reason=reason,
            )
            assert legacy["attempts_used"] == bad_attempts_used

            before = len(request_ledger._all_records(run_dir))
            gm = ExplodingGm()
            outcome = save_correction.pursue_single_figure_correction(
                run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
                candidate_block=wallet_as_number(char_id), gm_transport=gm,
            )
            assert outcome.status == "hold", f"Fall {label!r}: erwartet kontrollierten HOLD -- {outcome}"
            if expected_reason is not None:
                assert outcome.reason == expected_reason, f"Fall {label!r}: {outcome}"
            assert gm.calls == [], (
                f"Fall {label!r}: KEIN synthetischer Transport-Call fuer attempts_used={bad_attempts_used!r} -- "
                f"{gm.calls}"
            )
            after = len(request_ledger._all_records(run_dir))
            assert after == before, (
                f"Fall {label!r}: 0 neue Requestdatensaetze (kein `sent`-Record vor der Typablehnung) -- "
                f"before={before} after={after}"
            )
            record = save_correction.load_record(run_dir, repair_key)
            assert record["state"] == "hold", record
            if expected_reason is not None:
                assert record["last_reason"] == expected_reason, record


# ---------------------------------------------------------------------------
# (d) Caller/Record-section_id-Mismatch bleibt terminal HOLD -- auch fuer
#     einen ECHTEN Legacy-Record ohne bound_block (Identitaetspruefung
#     greift VOR der neuen Provenienzpruefung).
# ---------------------------------------------------------------------------

def test_d_single_figure_section_mismatch_on_legacy_record_stays_hold():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "p75_shape_section_mismatch", "CHR-75-SHAPE-SECTION"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        reason = deadline_reason(1700000000.0)
        legacy = write_legacy_hold_record(
            run_dir, repair_key=repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, table_id="community-A", section_id="section-A",
            attempts_used=1, last_reason=reason,
        )
        assert "bound_block" not in legacy

        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=wallet_as_number(char_id), gm_transport=gm,
            table_id="community-A", section_id="section-B",  # ANDERER Abschnitt als der Record.
        )
        assert outcome.status == "hold", f"Mismatch MUSS terminal bleiben -- {outcome}"
        assert gm.calls == [], "KEIN Versand unter der neuen Calleridentitaet."
        assert len(request_ledger._all_records(run_dir)) == before
        record = save_correction.load_record(run_dir, repair_key)
        assert record["section_id"] == "section-A", "der gespeicherte Record bleibt an seine ORIGINAL-Identitaet gebunden."
        assert record["state"] == "hold"


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
