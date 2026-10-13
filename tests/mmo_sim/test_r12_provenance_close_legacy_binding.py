#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_provenance_close_legacy_binding.py — R12-W75:
F02-PROVENANCE, positive Herkunftsbindung fuer einen ECHTEN, VOR diesem Fix
geschriebenen Legacy-Korrekturdatensatz OHNE `"bound_block"`-Schluessel
(`mmo_sim/core/save_correction.py:pursue_single_figure_correction` +
`_verify_legacy_provenance`).

Abdeckung (W75-BRIEF.md PFLICHT-ABLAUF Punkt 3(a)/(b)):
  (a) VOLLSTAENDIG positiv gebundener Originalrequest+Entwurf (Teilnehmer/
      Tisch/Abschnitt/Rolle/Turn passen, die tatsaechlich gespeicherte
      Antwort des aufgeloesten Requests extrahiert BYTEGLEICH zum
      uebergebenen `original_evidence`) -> Resume im selben Slot1, reine
      Formatkorrektur, `status="accepted"`.
  (b1) `original_request_id`/`original_evidence` fehlen (beide `None`) ->
       HOLD VOR Transport.
  (b2) `original_request_id` loest NICHT auf (kein Requestledger-Datensatz
       mit dieser ID) -> HOLD VOR Transport.
  (b3) der aufgeloeste Request gehoert zu einer ANDEREN Operation (fremder
       `participant`) -> HOLD VOR Transport (Ledger-Abwesenheit fuer die
       ALTE Identitaet darf keinen Versand legitimieren).
  (b4) `original_evidence` ist GETAUSCHT -- der aufgeloeste Request ist
       zwar echt und identitaetsmaessig passend, aber seine tatsaechlich
       gespeicherte Antwort unterscheidet sich vom uebergebenen
       `original_evidence` -> HOLD VOR Transport.

Jede (b)-Variante: KEIN Transport-Call, 0 neue Ledger-Requestdatensaetze,
`status="hold"` mit `reason="legacy_provenance_unverified"`.

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
    ExplodingGm, ScriptedGm, seed_original_request, wallet_as_number, write_legacy_hold_record,
)
from _r12_window_hold_fixture import deadline_reason, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

ROLE_CREATION = save_correction_domain.ROLE_CREATION
_ORIGINAL_ROLE = "creation_dialog"
_ORIGINAL_TURN_IDX = 0


# ---------------------------------------------------------------------------
# (a) vollstaendig positiv gebunden -> Resume im selben Slot1, accepted.
# ---------------------------------------------------------------------------

def test_a_fully_bound_legacy_record_resumes_same_slot_and_is_accepted():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "p75_prov_pos", "CHR-75-PROV-POS"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        original_draft = wallet_as_number(char_id)
        original_request_id = seed_original_request(
            run_dir, participant=participant_id, table_id=None, section_id=None,
            role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX, evidence_block=original_draft,
        )
        reason = deadline_reason(1700000000.0)
        legacy = write_legacy_hold_record(
            run_dir, repair_key=repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, attempts_used=1, last_reason=reason,
            errors=["economy.wallets.*"],
        )
        assert "bound_block" not in legacy, "Testvoraussetzung: ECHTER Legacy-Record ohne den Schluessel."
        before_requests = len(request_ledger._all_records(run_dir))

        valid_block = full_v7_save(char_id, name="Flo")  # reine Formatkorrektur, gleiche Identitaet/Name
        gm = ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=original_draft, gm_transport=gm,
            original_request_id=original_request_id, original_evidence=original_draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
        )
        assert outcome.status == "accepted" and outcome.block == valid_block, outcome
        assert len(gm.calls) == 1 and gm.calls[0][0] == 1, (
            f"genau EIN Transport-Call, derselbe Slot1 (turn_idx=attempts_used=1) -- {gm.calls}"
        )
        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 1, "Zaehler bleibt unangetastet -- derselbe Slot, kein 2. Versuch."
        assert record["state"] == "adopted"
        # genau EIN neuer Ledger-Record fuer den tatsaechlichen Korrektur-Versand (Slot1).
        assert len(request_ledger._all_records(run_dir)) == before_requests + 1


# ---------------------------------------------------------------------------
# (b) HOLD vor Transport bei fehlender/nichtauflösbarer/fremder/
#     getauschter Herkunft.
# ---------------------------------------------------------------------------

def _assert_hold_before_transport(run_dir, repair_key, outcome, gm):
    assert outcome.status == "hold" and outcome.reason == "legacy_provenance_unverified", outcome
    assert gm.calls == [], f"KEIN Transport-Call vor einer unverifizierten Legacy-Herkunft -- {gm.calls}"
    record = save_correction.load_record(run_dir, repair_key)
    assert record["state"] == "hold", record
    assert record["last_reason"] == "legacy_provenance_unverified", record


def test_b1_missing_original_request_id_and_evidence_holds_before_transport():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "p75_prov_missing", "CHR-75-PROV-MISSING"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        reason = deadline_reason(1700000000.0)
        write_legacy_hold_record(
            run_dir, repair_key=repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, attempts_used=1, last_reason=reason,
        )
        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=wallet_as_number(char_id), gm_transport=gm,
        )
        _assert_hold_before_transport(run_dir, repair_key, outcome, gm)
        assert len(request_ledger._all_records(run_dir)) == before, "0 neue Requestdatensaetze."


def test_b2_unresolvable_original_request_id_holds_before_transport():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "p75_prov_unresolvable", "CHR-75-PROV-UNRESOLVABLE"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        reason = deadline_reason(1700000000.0)
        write_legacy_hold_record(
            run_dir, repair_key=repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, attempts_used=1, last_reason=reason,
        )
        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=wallet_as_number(char_id), gm_transport=gm,
            original_request_id="does-not-exist-in-ledger", original_evidence=wallet_as_number(char_id),
        )
        _assert_hold_before_transport(run_dir, repair_key, outcome, gm)
        assert len(request_ledger._all_records(run_dir)) == before, "0 neue Requestdatensaetze."


def test_b3_foreign_participant_original_request_holds_before_transport():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "p75_prov_foreign", "CHR-75-PROV-FOREIGN"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        foreign_draft = wallet_as_number(char_id)
        foreign_request_id = seed_original_request(
            run_dir, participant="SOMEONE-ELSE", table_id=None, section_id=None,
            role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX, evidence_block=foreign_draft,
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
            candidate_block=foreign_draft, gm_transport=gm,
            original_request_id=foreign_request_id, original_evidence=foreign_draft,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
        )
        _assert_hold_before_transport(run_dir, repair_key, outcome, gm)
        assert len(request_ledger._all_records(run_dir)) == before, (
            "Ledger-Abwesenheit fuer die ALTE Recordidentitaet darf KEINEN Versand unter einer "
            "fremden, lediglich zufaellig auflösbaren Requestidentitaet legitimieren."
        )


def test_b4_swapped_original_evidence_holds_before_transport():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)
        participant_id, char_id = "p75_prov_swapped", "CHR-75-PROV-SWAPPED"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        actually_stored_draft = wallet_as_number(char_id, name="Original Testfigur")
        original_request_id = seed_original_request(
            run_dir, participant=participant_id, table_id=None, section_id=None,
            role=_ORIGINAL_ROLE, turn_idx=_ORIGINAL_TURN_IDX, evidence_block=actually_stored_draft,
        )
        swapped_evidence = wallet_as_number(char_id, name="Changed Testfigur")
        assert swapped_evidence != actually_stored_draft, "Testvoraussetzung: tatsaechlich ausgetauscht."

        reason = deadline_reason(1700000000.0)
        write_legacy_hold_record(
            run_dir, repair_key=repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, attempts_used=1, last_reason=reason,
        )
        before = len(request_ledger._all_records(run_dir))
        gm = ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=swapped_evidence, gm_transport=gm,
            original_request_id=original_request_id, original_evidence=swapped_evidence,
            original_role=_ORIGINAL_ROLE, original_turn_idx=_ORIGINAL_TURN_IDX,
        )
        _assert_hold_before_transport(run_dir, repair_key, outcome, gm)
        assert len(request_ledger._all_records(run_dir)) == before, (
            "getauschtes original_evidence darf NICHT als Drift-Baseline akzeptiert werden."
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
