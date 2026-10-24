#!/usr/bin/env python3
"""
tests/mmo_sim/test_r12_window_hold_single_figure.py — R12-W73: D-HOLD
Pre-Send-Window-Resume, Einzelfigur-/Erschaffungspfad
(`mmo_sim/core/save_correction.py:pursue_single_figure_correction` +
`mmo_sim/core/_save_correction_window.py`).

Abdeckung (W73-BRIEF.md PFLICHT-ABLAUF Punkt 3):
  (a) frischer Deadline-Pre-Send-Block -> zweiter Aufruf mit offenem
      Fenster nimmt DENSELBEN Slot (turn_idx/attempts_used unveraendert)
      wieder auf, erreicht "accepted".
  (b) ein bereits VOR diesem Fix als `state="hold"` gespeicherter Legacy-
      Datensatz (kein `window_paused`-Vorlauf) wird ueber dieselbe
      Produktlogik erkannt -- `attempts_used` bleibt 1 beim ersten
      tatsaechlichen Korrekturrequest.
  (c) >=3 Aufrufe bei weiterhin geschlossenem Fenster: 0 neue
      Requestdatensaetze, 0 Zaehleraenderung, idempotent (kein Write nach
      der ersten Migration).
  (d) `last_request_id=null`, ABER ein passender Ledger-Record fuer
      GENAU diese Operationsidentitaet existiert bereits (offene
      Reservierung) -> fail-closed, KEIN Resume, bleibt terminal.
  (e) andere HOLD-Gruende (Attempt-Budget, Lab-Stop, max_usd) bleiben
      terminal -- insbesondere ein ANDERER `admission_blocked:`-Grund OHNE
      den exakten Deadline-Marker wird NICHT resumiert (Invariante 1).

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie die
bestehende Suite (kein pytest-Fixture-Zwang)."""
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
from _r12_window_hold_fixture import close_window, deadline_reason, open_window  # noqa: E402

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
import mmo_sim.core.save_correction as save_correction  # noqa: E402
import mmo_sim.core.save_correction as sc  # noqa: E402,F401 (Alias-Lesbarkeit unten)
import mmo_sim.domain.zeitriss.save_correction as save_correction_domain  # noqa: E402

ROLE_CREATION = save_correction_domain.ROLE_CREATION


def _wallet_as_number(char_id: str) -> dict:
    """Schema-ungueltig (identisches Muster zu test_w48): economy.wallets.*
    als blanke Zahl statt Objekt -- der genaue Defekt spielt fuer diese
    Suite keine Rolle, nur dass die ERSTE Validierung scheitert und damit
    `pursue_single_figure_correction` ueberhaupt einen Korrekturdatensatz
    anlegt."""
    block = full_v7_save(char_id, name="Flo")
    block["economy"] = {"wallets": {char_id: 500}}
    return block


class _ExplodingGm:
    def __init__(self):
        self.calls = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        raise AssertionError("unerwarteter Transport-Call -- dieser Pfad muss admission-blockiert bleiben.")


class _ScriptedGm:
    def __init__(self, contents):
        self._contents = list(contents)
        self.calls = []

    def turn(self, turn_idx, text, **kwargs):
        self.calls.append((turn_idx, text))
        if not self._contents:
            raise AssertionError("unerwarteter zusaetzlicher Transport-Call (keine weitere gescriptete Antwort).")
        return {"content": self._contents.pop(0), "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


def _record_snapshot(run_dir, repair_key):
    r = save_correction.load_record(run_dir, repair_key)
    return dict(r) if r is not None else None


# ---------------------------------------------------------------------------
# (a) frischer Deadline-Pre-Send-Block -> Resume mit offenem Fenster.
# ---------------------------------------------------------------------------

def test_a_fresh_deadline_pre_send_pause_resumes_same_slot_when_window_reopens():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        reason = close_window(run_dir, deadline=1.0)
        participant_id, char_id = "g04_d", "CHR-TRACE-001"

        gm1 = _ExplodingGm()
        outcome1 = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=_wallet_as_number(char_id), gm_transport=gm1,
        )
        assert outcome1.status == "hold" and outcome1.reason == reason, outcome1
        assert gm1.calls == [], "Admission-Gate muss den Transport-Call verhindern, nicht nur nachtragen."

        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)
        record1 = _record_snapshot(run_dir, repair_key)
        assert record1["state"] == "window_paused", record1
        assert record1["attempts_used"] == 1 and record1["last_request_id"] is None

        # Fenster wieder offen (naechster Lab-Zyklus/Prozess) -- GENAU
        # DERSELBE Slot (turn_idx=attempts_used=1) wird regulaer erneut
        # versucht, kein neuer Slot, kein begin_attempt.
        open_window(run_dir)
        valid_block = full_v7_save(char_id, name="Flo")
        # F-WALLET-LOSS: wertgleicher Betrag (500) wie `_wallet_as_number`.
        valid_block["economy"] = {"wallets": {char_id: {"balance": 500}}}
        gm2 = _ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome2 = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=_wallet_as_number(char_id), gm_transport=gm2,
        )
        assert outcome2.status == "accepted" and outcome2.block == valid_block, outcome2
        assert len(gm2.calls) == 1, f"genau EIN Korrektur-Transport-Call, kein Doppelversand -- {gm2.calls}"
        assert gm2.calls[0][0] == 1, f"turn_idx muss derselbe Slot (1) bleiben, nicht neu nummeriert -- {gm2.calls}"

        record2 = save_correction.load_record(run_dir, repair_key)
        assert record2["attempts_used"] == 1, "Zaehler bleibt unangetastet -- derselbe Slot, kein 2. Versuch."
        assert record2["state"] == "adopted"


# ---------------------------------------------------------------------------
# (b) Legacy-D-HOLD (state="hold" OHNE window_paused-Vorlauf des neuen
#     Codes) wird ueber dieselbe generische Produktlogik erkannt.
# ---------------------------------------------------------------------------

def test_b_legacy_hold_record_without_window_paused_history_is_recognized():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)  # Fenster ist JETZT offen -- die Blockade liegt in der Vergangenheit
        participant_id, char_id = "g04_d_legacy", "CHR-TRACE-002"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        # Simuliert einen Datensatz, der VOR diesem Fix durch die alte
        # `mark_hold`-Logik geschrieben wurde -- state="hold" direkt, OHNE
        # jemals `window_paused` gesehen zu haben (Invariante 2: Legacy-D
        # ueber normale Produktlogik, KEINE hardcodierte Figurenliste --
        # dieser Test verwendet bewusst eine ANDERE Identitaet als Test a).
        save_correction.load_or_init_record(
            run_dir, repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, errors=["economy.wallets.*"],
        )
        save_correction.begin_attempt(run_dir, repair_key)
        reason = deadline_reason(1700000000.0)
        legacy = save_correction.mark_hold(run_dir, repair_key, reason=reason)
        assert legacy["state"] == "hold" and legacy["attempts_used"] == 1

        valid_block = full_v7_save(char_id, name="Flo")
        gm = _ScriptedGm(["```json\n" + json.dumps(valid_block) + "\n```"])
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=_wallet_as_number(char_id), gm_transport=gm,
        )
        assert outcome.status == "accepted" and outcome.block == valid_block, outcome
        assert len(gm.calls) == 1 and gm.calls[0][0] == 1, gm.calls

        record = save_correction.load_record(run_dir, repair_key)
        assert record["attempts_used"] == 1, (
            "attempts_used bleibt beim ERSTEN echten Korrekturrequest bei 1 -- "
            f"der Legacy-HOLD-Slot wird fortgesetzt, nicht neu eroeffnet (tatsaechlich: {record['attempts_used']})."
        )


# ---------------------------------------------------------------------------
# (c) >=3 Aufrufe bei weiterhin geschlossenem Fenster: idempotent.
# ---------------------------------------------------------------------------

def test_c_repeated_calls_with_window_still_closed_are_idempotent_no_loop():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        reason = close_window(run_dir, deadline=1.0)
        participant_id, char_id = "g04_d_idem", "CHR-TRACE-003"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        gm = _ExplodingGm()
        outcome1 = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=_wallet_as_number(char_id), gm_transport=gm,
        )
        assert outcome1.status == "hold" and outcome1.reason == reason
        record1 = _record_snapshot(run_dir, repair_key)
        assert record1["state"] == "window_paused"

        for i in range(3):
            outcome_n = save_correction.pursue_single_figure_correction(
                run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
                candidate_block=_wallet_as_number(char_id), gm_transport=gm,
            )
            assert outcome_n.status == "hold" and outcome_n.reason == reason
            record_n = _record_snapshot(run_dir, repair_key)
            assert record_n == record1, (
                f"Aufruf {i + 2}: Datensatz muss bytegleich zu record1 bleiben (kein Write nach der "
                f"ersten Migration) -- record1={record1} record_n={record_n}"
            )

        assert gm.calls == [], "kein einziger Transport-Call bei weiterhin geschlossenem Fenster."
        assert request_ledger.open_requests(run_dir) == [], (
            "0 neue Requestdatensaetze ueber alle wiederholten Aufrufe hinweg."
        )


# ---------------------------------------------------------------------------
# (d) last_request_id=null, ABER ein passender Ledger-Record existiert
#     bereits -> fail-closed, kein Resume.
# ---------------------------------------------------------------------------

def test_d_null_last_request_id_with_matching_open_ledger_record_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "run"
        open_window(run_dir)  # Fenster ist offen -- der Block darf NICHT am Fenster liegen.
        participant_id, char_id = "g04_d_unclear", "CHR-TRACE-004"
        repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

        save_correction.load_or_init_record(
            run_dir, repair_key, persona_key=participant_id, char_id=char_id,
            operation_key=ROLE_CREATION, errors=["economy.wallets.*"],
        )
        save_correction.begin_attempt(run_dir, repair_key)  # attempts_used -> 1
        reason = deadline_reason(1700000000.0)
        save_correction.mark_hold(run_dir, repair_key, reason=reason)

        # Simuliert eine FRUEHERE, zwischen `begin()` und `finish_received`/
        # `finish_error` abgebrochene Prozessinstanz fuer GENAU dieselbe
        # Operationsidentitaet (role, table_id=None, section_id=None,
        # turn_idx=1, participant=participant_id) -- ein offener (state=
        # "sent") Requestdatensatz, den `last_request_id=null` im
        # Korrekturdatensatz NICHT sichtbar macht.
        request_ledger.begin(
            run_dir, role=ROLE_CREATION, content="unklar versandt", reserved_usd=0.001,
            turn_idx=1, participant=participant_id,
        )
        assert save_correction._window.slot_never_sent(
            run_dir, role=ROLE_CREATION, table_id=None, section_id=None,
            turn_idx=1, participant=participant_id,
        ) is False, "Unit-Beleg: slot_never_sent muss den offenen Ledger-Record erkennen."

        gm = _ExplodingGm()
        outcome = save_correction.pursue_single_figure_correction(
            run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
            candidate_block=_wallet_as_number(char_id), gm_transport=gm,
        )
        assert outcome.status == "hold" and outcome.reason == reason, (
            f"fail-closed erwartet (unveraenderter terminaler HOLD), tatsaechlich: {outcome}"
        )
        assert gm.calls == [], "KEIN Transport-Call -- Resume wurde durch die Ledger-Pruefung verhindert."
        record = save_correction.load_record(run_dir, repair_key)
        assert record["state"] == "hold", f"Datensatz darf NICHT nach window_paused migriert werden: {record}"


# ---------------------------------------------------------------------------
# (e) andere HOLD-Gruende bleiben terminal (Invariante 1/7).
# ---------------------------------------------------------------------------

def test_e_other_hold_reasons_stay_terminal_not_resumed():
    cases = [
        ("attempt_budget_exhausted", "attempt_budget_exhausted"),
        ("Lab-Stop aktiv (persistiert)", "Lab-Stop aktiv (persistiert)"),
        (
            "admission_blocked:max_usd erreicht (0.5, frisch von Platte)",
            "admission_blocked:max_usd erreicht (0.5, frisch von Platte)",
        ),
    ]
    for idx, (reason, expected_reason) in enumerate(cases):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            open_window(run_dir)  # Fenster offen -- zeigt, dass NICHT das Fenster der Grund fuer HOLD bleibt.
            participant_id, char_id = f"g04_terminal_{idx}", f"CHR-TRACE-TERM-{idx}"
            repair_key = save_correction_domain.creation_repair_key(participant_id, char_id)

            save_correction.load_or_init_record(
                run_dir, repair_key, persona_key=participant_id, char_id=char_id,
                operation_key=ROLE_CREATION, errors=["economy.wallets.*"],
            )
            save_correction.begin_attempt(run_dir, repair_key)
            save_correction.mark_hold(run_dir, repair_key, reason=reason)

            assert save_correction._window.is_pre_send_deadline_reason(reason) is False, (
                f"Fall {idx}: Vorbedingung verletzt -- {reason!r} darf NICHT als Deadline-Marker gelten."
            )

            gm = _ExplodingGm()
            outcome = save_correction.pursue_single_figure_correction(
                run_dir=run_dir, participant_id=participant_id, expected_chrononaut_id=char_id,
                candidate_block=_wallet_as_number(char_id), gm_transport=gm,
            )
            assert outcome.status == "hold" and outcome.reason == expected_reason, (
                f"Fall {idx} ({reason!r}): muss terminal bleiben, tatsaechlich {outcome}"
            )
            assert gm.calls == [], f"Fall {idx}: KEIN Transport-Call fuer einen terminalen HOLD-Grund."
            record = save_correction.load_record(run_dir, repair_key)
            assert record["state"] == "hold", f"Fall {idx}: Datensatz darf NICHT auf window_paused migrieren."


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
