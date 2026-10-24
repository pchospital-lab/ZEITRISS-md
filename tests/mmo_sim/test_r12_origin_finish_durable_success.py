#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_origin_finish_durable_success.py — R12-W76: F02 R02
erfolgreiche Originalantwort verlangen
(`mmo_sim/core/save_correction.py:_verify_legacy_provenance`).

Bug (VOR diesem Fix, s. W76-BRIEF.md R02): die Funktion las
`original_request.get("result_text")` direkt und prufte Identitaet/
Bytegleichheit der Evidenz, aber NICHT den Erfolgs-/Fehlerzustand des
aufgeloesten Requests -- ein passender `result_text` MIT gesetztem `error`
(oder ein noch offener/unklarer Zustand) wurde faelschlich als Herkunft
akzeptiert.

Fix: der aufgeloeste `original_request` muss dasselbe Durable-Erfolgs-
praedikat erfuellen wie `request_ledger.find_durable_result`/
`request_ledger.py:439-441` (`state in ("received", "accounted")` UND
`error is None` UND `result_text is not None`). Sonst
`_LEGACY_PROVENANCE_REJECTED`.

Abdeckung (CASES.json):
  R02-GOOD-ORIGIN   passender erfolgreicher Originalrequest -> positive
                     Kontrolle, `status="accepted"`.
  R02-ERROR-ORIGIN  passender Text/Identitaet, ABER `error` gesetzt -> HOLD
                     VOR Transport, KEIN Originalwrite.
  R02-STATE-TEXT    unzulaessiger/unklarer Zustand (nie beantwortet, kein
                     `result_text`) -> kontrollierter HOLD.

Alle (negativen) Faelle: KEIN Transport-Call, 0 neue Requestdatensaetze,
`status="hold"` mit `reason="legacy_provenance_unverified"` -- gleiches
Beleg-/Aufbaumuster wie `test_r12_provenance_close_legacy_binding.py`.

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
from _r12_origin_finish_fixture import (  # noqa: E402
    seed_error_origin_request, seed_unresolved_origin_request,
)
from _r12_provenance_close_fixture import (  # noqa: E402
    ExplodingGm, ScriptedGm, seed_original_request, wallet_as_number, write_legacy_hold_record,
)
from _r12_window_hold_fixture import deadline_reason, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

ROLE_CREATION = save_correction_domain.ROLE_CREATION
_ORIGINAL_ROLE = "creation_dialog"
_ORIGINAL_TURN_IDX = 0


def _assert_hold_before_transport(run_dir, repair_key, outcome, gm, before):
    assert outcome.status == "hold" and outcome.reason == "legacy_provenance_unverified", outcome
    assert gm.calls == [], f"KEIN Transport-Call vor einer unverifizierten Herkunft -- {gm.calls}"
    assert len(request_ledger._all_records(run_dir)) == before, "0 neue Requestdatensaetze."
    record = save_correction.load_record(run_dir, repair_key)
    assert record["state"] == "hold" and record["last_reason"] == "legacy_provenance_unverified", record


# ---------------------------------------------------------------------------
# R02-GOOD-ORIGIN -- positive Kontrolle (bereits strukturell durch
# test_r12_provenance_close_legacy_binding.py::test_a abgedeckt, hier
# nochmal fokussiert als direkte Gegenprobe zu den beiden neuen (b)/(c)
# Faellen unten -- derselbe Requestaufbau, nur das Erfolgspraedikat variiert).
# ---------------------------------------------------------------------------

def test_good_origin_is_accepted_as_positive_control():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_r02_good", "CHR-76-R02-GOOD"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id)
        original_request_id = seed_original_request(
            run_dir, participant=participant_id, table_id=None, section_id=None,
            role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX, evidence_block=original_draft,
        )
        reason = deadline_reason(1700000000.0)
        write_legacy_hold_record(
            run_dir, repair_key=repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, attempts_used=1, last_reason=reason,
            errors=["economy.wallets.*"],
        )

        valid_block = full_v7_save(char_id, name="Flo")
        # F-WALLET-LOSS: wertgleicher Betrag (500) wie `original_draft`.
        valid_block["economy"] = {"wallets": {char_id: {"balance": 500}}}
        gm = ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=original_draft, gm_transport=gm,
            original_request_id=original_request_id, original_evidence=original_draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
        )
        assert outcome.status == "accepted" and outcome.block == valid_block, outcome


# ---------------------------------------------------------------------------
# R02-ERROR-ORIGIN -- passender Text/Identitaet, ABER error gesetzt.
# ---------------------------------------------------------------------------

def test_error_set_on_matching_origin_holds_before_transport():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_r02_error", "CHR-76-R02-ERROR"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id)
        original_request_id = seed_error_origin_request(
            run_dir, participant=participant_id, table_id=None, section_id=None,
            role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX, evidence_block=original_draft,
        )
        seeded = request_ledger.load_request(run_dir, original_request_id)
        assert seeded["error"] is not None and seeded["result_text"] is not None, (
            f"Testvoraussetzung: passender Text UND gesetzter error -- {seeded}"
        )
        reason = deadline_reason(1700000000.0)
        write_legacy_hold_record(
            run_dir, repair_key=repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, attempts_used=1, last_reason=reason,
        )

        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=original_draft, gm_transport=gm,
            original_request_id=original_request_id, original_evidence=original_draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
        )
        _assert_hold_before_transport(run_dir, repair_key, outcome, gm, before)


# ---------------------------------------------------------------------------
# R02-STATE-TEXT -- nie beantworteter/offener Zustand (kein result_text).
# ---------------------------------------------------------------------------

def test_unresolved_state_without_result_text_holds_before_transport():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "w76_r02_unresolved", "CHR-76-R02-UNRESOLVED"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id)
        original_request_id = seed_unresolved_origin_request(
            run_dir, participant=participant_id, table_id=None, section_id=None,
            role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX,
        )
        seeded = request_ledger.load_request(run_dir, original_request_id)
        assert seeded["state"] not in ("received", "accounted") and seeded["result_text"] is None, (
            f"Testvoraussetzung: nie beantworteter Requestdatensatz -- {seeded}"
        )
        reason = deadline_reason(1700000000.0)
        write_legacy_hold_record(
            run_dir, repair_key=repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, attempts_used=1, last_reason=reason,
        )

        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=original_draft, gm_transport=gm,
            original_request_id=original_request_id, original_evidence=original_draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
        )
        _assert_hold_before_transport(run_dir, repair_key, outcome, gm, before)


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
