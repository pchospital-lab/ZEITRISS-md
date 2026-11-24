#!/usr/bin/env python3
"""
tests/mmo_sim/test_restnachzug_rk_20261124_r2.py — enge Gegenfaelle des
PR-#3317-Restnachzugs r2 (RECOVERY_REVIEW.md §3 K "feste Topup-ID verliert die
zweite geaenderte Buchungsbasis; monetaere Korrektur zaehlt einen weiteren
Turn" + §2 R5 "denselben vollstaendigen Bindungsentscheid vor jeder Grant-
Ausnahme").

Self-contained wie test_restnachzug_rk_20261124_r1: kein Mock AUF den
geprueften Pfaden, nur direkte `request_ledger`-/`admission`-Aufrufe + ein
synthetisch nachgestellter Crash (verlorener Record-Write) ueber einen
bewussten `_write_request` auf den Vorzustand. Alle Betraege synthetisch.

Lauf: `python3 -m pytest tests/mmo_sim/test_restnachzug_rk_20261124_r2.py -q`
oder `python3 -m unittest tests.mmo_sim.test_restnachzug_rk_20261124_r2 -v`.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core.admission as admission  # noqa: E402
import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402


class _KBase(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.run_dir = Path(self._td.name) / "run"
        write_test_profile(self.run_dir, max_turns=10, max_usd=10.0)

    def tearDown(self):
        self._td.cleanup()

    def _status(self):
        return json.loads((self.run_dir / "lab.status.json").read_text(encoding="utf-8"))

    def _usd(self):
        return self._status().get("usd_spent", 0.0)

    def _turns(self):
        return self._status().get("turns_used", 0)

    def _make_granted_follower(self, *, original_reserved):
        original_id = request_ledger.begin(
            self.run_dir, role="persona_decision", content="original-wire", reserved_usd=original_reserved,
            table_id="t-k", section_id="sec-k", turn_idx=0, participant="vanguard", dollar_billed=True,
        )
        request_ledger.dispose_open_orphan(self.run_dir, original_id, reason="K-Restnachzug-r2-Test")
        child_id = request_ledger.authorize_bound_retry(self.run_dir, original_id)
        return original_id, child_id

    def _simulate_crash_before_sent(self, request_id, *, reserved_usd=None):
        """Der im Review bezeichnete Zwischenzustand: Buchung in `lab.status.
        json` ist erfolgt, aber der abschliessende `sent`-/Record-Write wurde
        unterbrochen -- der Record bleibt `reserved`. Optional faellt die
        gespeicherte `reserved_usd` auf einen frueheren Stand zurueck (der
        verlorene Record-Write der Topup-Runde)."""
        rec = request_ledger.load_request(self.run_dir, request_id)
        rec["state"] = "reserved"
        rec["sent_ts"] = None
        if reserved_usd is not None:
            rec["reserved_usd"] = reserved_usd
        request_ledger._write_request(self.run_dir, request_id, rec)


class TestKSecondCrashAfterTopupBeforeRecord(_KBase):
    """RECOVERY_REVIEW.md §3: Original .001; Child-Erstbuchung .01; Topup auf
    .02; zweiter Crash NACH der Topup-Buchung / VOR dem Record-/sent-Write
    (gespeicherte Childbasis bleibt .01); frischer Caller .03. Vorher blockierte
    die feste `:rebook-topup`-ID jede weitere Differenz -> Gesamt .021 statt
    .031, Record behauptete trotzdem .03. Jetzt rechnet die Nachbuchung gegen
    den crashfesten `reservation_booked_usd`-Stand im Status."""

    def test_second_crash_books_only_missing_delta_total_031_not_021(self):
        original_id, child_id = self._make_granted_follower(original_reserved=0.001)
        # Original .001 ist gebucht (begin): usd=.001, 1 Turn.
        self.assertAlmostEqual(self._usd(), 0.001, places=6)
        self.assertEqual(self._turns(), 1)

        # 1) Erstbuchung Child .01 (Branch B): bucht .01 -> Gesamt .011, 2 Turns.
        #    Danach "Crash vor sent" (Review-Schritt 1): Record bleibt reserved.
        request_ledger.commit_authorized_retry(self.run_dir, child_id, content="v1", reserved_usd=0.01)
        self.assertAlmostEqual(self._usd(), 0.011, places=6)
        self.assertEqual(self._turns(), 2)
        self.assertAlmostEqual(admission.booked_reservation_amount(self.run_dir, child_id), 0.01, places=6)
        turns_after_first = self._turns()
        self._simulate_crash_before_sent(child_id)

        # 2) Topup auf .02 (Branch A, Record reserved): bucht Differenz .01 ->
        #    Gesamt .021. Reine Geldkorrektur zaehlt KEINEN neuen Turn.
        #    Danach "zweiter Crash nach Topup/vor Record" (Review-Schritt 2):
        #    Record-Write verloren -> gespeicherte Childbasis faellt auf .01
        #    zurueck, der Statusbetrag bleibt crashfest .02.
        request_ledger.commit_authorized_retry(self.run_dir, child_id, content="v2", reserved_usd=0.02)
        self.assertAlmostEqual(self._usd(), 0.021, places=6)
        self.assertEqual(self._turns(), turns_after_first, "K: reine Geldnachbuchung zaehlt keinen Turn")
        self.assertAlmostEqual(admission.booked_reservation_amount(self.run_dir, child_id), 0.02, places=6)
        self._simulate_crash_before_sent(child_id, reserved_usd=0.01)
        self.assertAlmostEqual(request_ledger.load_request(self.run_dir, child_id)["reserved_usd"], 0.01, places=6)

        # 3) Frischer Caller .03 (Branch A): rechnet gegen den crashfesten Stand
        #    .02 -> bucht NUR die fehlende Differenz .01 -> Gesamt .031 (NICHT
        #    .021, wie es die alte feste Topup-ID produzierte).
        request_ledger.commit_authorized_retry(self.run_dir, child_id, content="v3", reserved_usd=0.03)
        status = self._status()
        print(f"[K-second-crash-raw] usd_spent={status['usd_spent']!r} turns_used={status['turns_used']!r} "
              f"reservation_booked_usd={status.get('reservation_booked_usd')!r} "
              f"record_reserved_usd={request_ledger.load_request(self.run_dir, child_id)['reserved_usd']!r}")
        self.assertAlmostEqual(self._usd(), 0.031, places=6, msg="K-FIX: Gesamt .031 statt .021")
        self.assertEqual(self._turns(), 2, "K-FIX: ein Original + ein Child bleiben zwei Turns")
        self.assertAlmostEqual(admission.booked_reservation_amount(self.run_dir, child_id), 0.03, places=6)
        # Record behauptet GENAU die gebuchte Basis (.03), keine ungebookte Basis.
        self.assertAlmostEqual(request_ledger.load_request(self.run_dir, child_id)["reserved_usd"], 0.03, places=6)
        self.assertEqual(request_ledger.load_request(self.run_dir, child_id)["state"], "sent")

    def test_repeat_commit_same_base_is_idempotent(self):
        _original_id, child_id = self._make_granted_follower(original_reserved=0.001)
        request_ledger.commit_authorized_retry(self.run_dir, child_id, content="v1", reserved_usd=0.02)
        usd_once, turns_once = self._usd(), self._turns()
        # "Crash vor sent" -> Record reserved; wiederholter Commit DERSELBEN
        # Basis (Branch A) -> keine zweite Buchung, kein Turn.
        self._simulate_crash_before_sent(child_id)
        request_ledger.commit_authorized_retry(self.run_dir, child_id, content="v1", reserved_usd=0.02)
        print(f"[K-idempotent-raw] usd_before={usd_once!r} usd_after={self._usd()!r} turns={self._turns()!r}")
        self.assertAlmostEqual(self._usd(), usd_once, places=6, msg="K: Wiederholung bucht nicht doppelt")
        self.assertEqual(self._turns(), turns_once, "K: Wiederholung zaehlt keinen weiteren Turn")

    def test_lower_or_equal_base_stays_frozen_no_down_booking(self):
        _original_id, child_id = self._make_granted_follower(original_reserved=0.001)
        request_ledger.commit_authorized_retry(self.run_dir, child_id, content="v1", reserved_usd=0.02)
        usd_high = self._usd()
        # "Crash vor sent" -> Record reserved; eine NIEDRIGERE neue Basis (Branch
        # A) bucht nichts ab; die gebuchte Verpflichtung (.02) bleibt
        # eingefroren, der Record behauptet weiterhin .02.
        self._simulate_crash_before_sent(child_id, reserved_usd=0.005)
        request_ledger.commit_authorized_retry(self.run_dir, child_id, content="v-small", reserved_usd=0.005)
        print(f"[K-frozen-raw] usd_high={usd_high!r} usd_after={self._usd()!r} "
              f"record_reserved={request_ledger.load_request(self.run_dir, child_id)['reserved_usd']!r}")
        self.assertAlmostEqual(self._usd(), usd_high, places=6, msg="K: keine Abbuchung bei niedrigerer Basis")
        self.assertAlmostEqual(
            request_ledger.load_request(self.run_dir, child_id)["reserved_usd"], 0.02, places=6,
            msg="K: eingefrorene Verpflichtung bleibt die Record-Basis",
        )


if __name__ == "__main__":
    unittest.main()
