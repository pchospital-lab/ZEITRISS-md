#!/usr/bin/env python3
"""
tests/mmo_sim/test_restnachzug_k_20261124_r3.py - enger Gegenfall des PR-#3317-
Restnachzugs r3 (STATUS_WRITER_REVIEW.md / RECOVERY_REVIEW.md Abschnitt 2:
"normaler Runner-Statuswrite verliert reservation_booked_usd").

Self-contained: unveraenderte echte `admission`-/`request_ledger`-/
`LabRunner`-Funktionen in einem frischen synthetischen Tempverzeichnis. Einzige
Fehlerinduktion ist ein OSError am child-sent-Write (wie `repro/
status_writer_witness.py`). Kein nativer Daten-/Netzwerk-/Modellzugriff.

Lauf: `python3 -m pytest tests/mmo_sim/test_restnachzug_k_20261124_r3.py -q`
oder `python3 -m unittest tests.mmo_sim.test_restnachzug_k_20261124_r3 -v`.
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
from mmo_sim.lab.runner import LabBudget, LabRunner, read_status  # noqa: E402


class TestReservationBookedUsdSurvivesNormalRunnerWrite(unittest.TestCase):
    """STATUS_WRITER_REVIEW.md Gegenfall: Original .001, autorisierter Child
    .01, Topup .02 (jeweils Crash vor dem sent-Write), dann ein echter
    `LabRunner.start()/release()`-Zyklus zwischen Topup-Crash und Retry.
    Vorher riss dieser Zyklus `reservation_booked_usd` auf {} zurueck, sodass
    der abschliessende Retry+Settlement .041 statt .031 ergab. Nach dem
    Nachzug muss der Runner-Zyklus die Map unveraendert durchreichen."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.run_dir = Path(self._td.name) / "run"
        write_test_profile(self.run_dir, max_turns=100, max_usd=10.0)

    def tearDown(self):
        self._td.cleanup()

    def _status(self):
        return json.loads((self.run_dir / "lab.status.json").read_text(encoding="utf-8"))

    def _crash_before_sent(self, child_id, amount):
        writer = request_ledger._write_request

        def fail(run_dir, request_id, data):
            if request_id == child_id and data.get("state") == "sent":
                raise OSError("synthetic sent marker interruption")
            return writer(run_dir, request_id, data)

        request_ledger._write_request = fail
        try:
            with self.assertRaises(OSError):
                request_ledger.commit_authorized_retry(
                    self.run_dir, child_id, content="bound synthetic context", reserved_usd=amount,
                )
        finally:
            request_ledger._write_request = writer

    def test_runner_start_release_preserves_booked_usd_map_031_not_041(self):
        original_id = request_ledger.begin(
            self.run_dir, role="persona_decision", content="original", reserved_usd=0.001,
            table_id="table", section_id="section", turn_idx=45, participant="persona",
        )
        original_bytes = (self.run_dir / "requests" / f"{original_id}.json").read_bytes()
        request_ledger.dispose_open_orphan(self.run_dir, original_id, reason="synthetic deliberate retry")
        child_id = request_ledger.authorize_bound_retry(self.run_dir, original_id)

        # Erstbuchung .01, Topup .02 -- jeweils vor dem sent-Write unterbrochen.
        self._crash_before_sent(child_id, 0.01)
        self._crash_before_sent(child_id, 0.02)

        before = self._status()
        self.assertAlmostEqual(before["usd_spent"], 0.021, places=6)
        self.assertAlmostEqual(before["reservation_booked_usd"][child_id], 0.02, places=6)
        self.assertEqual(request_ledger.load_request(self.run_dir, child_id)["reserved_usd"], 0.01)
        map_before_runner = dict(before["reservation_booked_usd"])
        dedup_ids_before_runner = list(before["booked_reservation_request_ids"])

        # Echter LabRunner.start()/release()-Zyklus zwischen Topup-Crash und
        # Retry -- genau der im Review bezeichnete Writer-Pfad.
        runner = LabRunner(self.run_dir, LabBudget(max_turns=100, max_seconds=100, max_usd=10.0))
        try:
            runner.start()
            after_writer = self._status()
        finally:
            runner.release()

        print(f"[K-r3-raw] after_writer.reservation_booked_usd={after_writer.get('reservation_booked_usd')!r} "
              f"after_writer.booked_reservation_request_ids={after_writer.get('booked_reservation_request_ids')!r}")

        # K-FIX: der normale Runner-Statuswrite darf die Map NICHT auf {}
        # zuruecksetzen -- sie muss bytegleich zum Stand vor dem Runnerwrite
        # bleiben (analog zu den bereits erhaltenen Dedup-IDs).
        self.assertEqual(
            after_writer["reservation_booked_usd"], map_before_runner,
            msg="K-FIX: reservation_booked_usd darf Runnerwrite nicht als {} ueberleben lassen",
        )
        self.assertEqual(
            after_writer["booked_reservation_request_ids"], dedup_ids_before_runner,
            msg="K: bestehende Dedup-IDs bleiben wie zuvor erhalten",
        )

        # Frischer Caller .03: rechnet gegen die crashfeste Basis .02 im
        # Status -> bucht nur die fehlende Differenz .01 -> Gesamt .031.
        request_ledger.commit_authorized_retry(self.run_dir, child_id, content="bound synthetic context", reserved_usd=0.03)
        request_ledger.finish_received(self.run_dir, child_id, usage={"usd": 0.03}, seconds=1.0, result_text="synthetic received")

        final = self._status()
        print(f"[K-r3-final-raw] usd_spent={final['usd_spent']!r} turns_used={final['turns_used']!r}")
        self.assertAlmostEqual(final["usd_spent"], 0.031, places=6, msg="K-FIX: .031 nach echtem Runnerwrite, NICHT .041")
        self.assertEqual(final["turns_used"], 2)
        self.assertEqual(
            (self.run_dir / "requests" / f"{original_id}.json").read_bytes(), original_bytes,
            msg="K: Originalbytes bleiben unveraendert",
        )

    def test_old_status_without_field_stays_readable_default_empty(self):
        """Altstatus OHNE `reservation_booked_usd` (Rueckwaertskompat) darf
        beim Lesen nicht crashen; der Reader liefert den Dataclass-Default
        {} statt eines TypeError."""
        status_path = self.run_dir / "lab.status.json"
        raw = json.loads(status_path.read_text(encoding="utf-8"))
        raw.pop("reservation_booked_usd", None)
        status_path.write_text(json.dumps(raw), encoding="utf-8")

        loaded = read_status(self.run_dir)
        self.assertEqual(loaded.reservation_booked_usd, {})

        runner = LabRunner(self.run_dir, LabBudget(max_turns=100, max_seconds=100, max_usd=10.0))
        try:
            runner.start()
        finally:
            runner.release()
        after = json.loads(status_path.read_text(encoding="utf-8"))
        self.assertEqual(after["reservation_booked_usd"], {})


if __name__ == "__main__":
    unittest.main()
