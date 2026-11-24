#!/usr/bin/env python3
"""
tests/mmo_sim/test_restnachzug_r5_20261124_r3.py - enger Gegenfall des PR-
#3317-Restnachzugs r3 (RECOVERY_REVIEW.md Abschnitt 1: "normale Persona-/GM-
Caller reichen StaleDispositionError noch ungefangen weiter").

Self-contained: der echte `mmo_sim.core.runtime.SectionRuntime` (volle Klasse,
kein AST-Teilextrakt) mit duck-typed `lobby`/`table`/`controller`-Platzhaltern
(SimpleNamespace). Unveraenderte echte `request_ledger`-/`admission`-
Funktionen in einem frischen synthetischen Tempverzeichnis. Fehlerinduktion
ist derselbe synthetische Run-ID-Drift wie im `recovery_review_witness.py`
(`run_id.json` nach `authorize_bound_retry` auf eine andere Run-ID setzen).
Kein Netzwerk-/Modellcall (der Treiber/`collect_decision` wirft, falls er
ueberhaupt erreicht wuerde).

Lauf: `python3 -m pytest tests/mmo_sim/test_restnachzug_r5_20261124_r3.py -q`
oder `python3 -m unittest tests.mmo_sim.test_restnachzug_r5_20261124_r3 -v`.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core.request_ledger as request_ledger  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime, _GateBlocked, _RecoveryPause  # noqa: E402


def _make_runtime(run_dir):
    """Dieselbe Konstruktion wie jeder echte Aufrufer (`ui/tui.py`/`lab/
    runner.py` ueber `core.app_service`), nur mit duck-typed Platzhaltern
    fuer `lobby`/`table`/`gm_transport` -- KEIN AST-Teilextrakt, das ist die
    tatsaechliche `SectionRuntime`-Klasse aus `mmo_sim/core/runtime.py`."""
    rt = SectionRuntime(
        lobby=SimpleNamespace(run_dir=run_dir),
        table=SimpleNamespace(table_id="table", members=["vanguard"], leader="vanguard",
                               sl_log=[], table_messages=[]),
        gm_transport=SimpleNamespace(is_dollar_billed=True, output_limit_tokens=None, base_url=None),
        marker="MARKER",
        harvest_validator=None,
        persona_state_store=None,
        harvest_extractor=None,
    )
    rt._current_section_id = "section"
    rt._turn_idx = 45
    return rt


class _R5Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.run_dir = Path(self._td.name) / "run"
        write_test_profile(self.run_dir, max_turns=100, max_usd=10.0)
        (self.run_dir / "run_id.json").write_text('{"run_id":"fixture-run-A"}', encoding="utf-8")

    def tearDown(self):
        self._td.cleanup()

    def _status(self):
        path = self.run_dir / "lab.status.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _setup_bound_drift(self, role):
        """Echtes `begin -> dispose_open_orphan -> authorize_bound_retry`,
        dann der synthetische Run-ID-Drift NACH der Autorisierung (bindet
        `disposition.bound_run_id` auf "fixture-run-A", aktueller Stand wird
        danach auf "fixture-run-B" umgeschrieben -- exakt wie
        `recovery_review_witness.py`)."""
        original_id = request_ledger.begin(
            self.run_dir, role=role, content="synthetic original", reserved_usd=.001,
            table_id="table", section_id="section", turn_idx=45, participant="vanguard",
        )
        original_bytes = (self.run_dir / "requests" / f"{original_id}.json").read_bytes()
        request_ledger.dispose_open_orphan(self.run_dir, original_id, reason="synthetic deliberate recovery")
        child_id = request_ledger.authorize_bound_retry(self.run_dir, original_id)
        (self.run_dir / "run_id.json").write_text('{"run_id":"fixture-run-B"}', encoding="utf-8")
        return original_id, child_id, original_bytes


class TestAdmittedDecisionTranslatesStaleDispositionError(_R5Base):
    def test_persona_decision_drift_raises_recovery_pause_not_raw_stale(self):
        original_id, child_id, original_bytes = self._setup_bound_drift("persona_decision")
        before_child = request_ledger.load_request(self.run_dir, child_id)
        before_status = self._status()

        calls = []

        def collect_decision(*_args, **_kwargs):
            calls.append("unexpected")
            raise AssertionError("kein Modellaufruf darf nach der Bindungsdrift erreicht werden")

        driver = SimpleNamespace(config=SimpleNamespace(max_tokens=100), is_dollar_billed=True)
        controller = SimpleNamespace(drivers={"vanguard": driver}, collect_decision=collect_decision)
        rt = _make_runtime(self.run_dir)

        # Die eigentliche Pruefung: jetzt propagiert _RecoveryPause (bzw.
        # irgendein _GateBlocked), NICHT mehr der rohe StaleDispositionError.
        with self.assertRaises(_GateBlocked) as ctx:
            rt._admitted_decision("persona_decision", controller, "vanguard", {"user": "ctx"})
        exc = ctx.exception
        print(f"[R5-r3-persona-raw] type={type(exc).__name__!r} isinstance_RecoveryPause={isinstance(exc, _RecoveryPause)!r} "
              f"isinstance_GateBlocked={isinstance(exc, _GateBlocked)!r} msg={exc!r}")
        self.assertIsInstance(exc, _RecoveryPause, "R5-FIX: muss als _RecoveryPause propagieren")
        self.assertIsInstance(exc, _GateBlocked, "R5-FIX: _RecoveryPause ist _GateBlocked -> bestehender Catch greift")
        self.assertEqual(calls, [], "R5: 0 Modellaufrufe nach der Bindungsdrift")
        self.assertEqual(self._status(), before_status, "R5: kein Status-/Buchungsseiteneffekt")
        self.assertEqual(request_ledger.load_request(self.run_dir, child_id), before_child, "R5: Child-Record unveraendert")
        self.assertEqual(
            (self.run_dir / "requests" / f"{original_id}.json").read_bytes(), original_bytes,
            msg="R5: Originalbytes unveraendert",
        )


class TestSubmitTranslatesStaleDispositionError(_R5Base):
    def test_gm_turn_drift_raises_recovery_pause_not_raw_stale(self):
        original_id, child_id, original_bytes = self._setup_bound_drift("gm_turn")
        before_child = request_ledger.load_request(self.run_dir, child_id)
        before_status = self._status()

        rt = _make_runtime(self.run_dir)
        controller = SimpleNamespace(drivers={})

        with self.assertRaises(_GateBlocked) as ctx:
            rt.submit(controller, "vanguard", "ctx-text", "fixture-ts",
                      origin_persona_key="vanguard", reserved_usd=.01)
        exc = ctx.exception
        print(f"[R5-r3-gm-raw] type={type(exc).__name__!r} isinstance_RecoveryPause={isinstance(exc, _RecoveryPause)!r} "
              f"isinstance_GateBlocked={isinstance(exc, _GateBlocked)!r} msg={exc!r}")
        self.assertIsInstance(exc, _RecoveryPause, "R5-FIX: muss als _RecoveryPause propagieren")
        self.assertIsInstance(exc, _GateBlocked, "R5-FIX: _RecoveryPause ist _GateBlocked -> bestehender Catch greift")
        self.assertEqual(self._status(), before_status, "R5: kein Status-/Buchungsseiteneffekt")
        self.assertEqual(request_ledger.load_request(self.run_dir, child_id), before_child, "R5: Child-Record unveraendert")
        self.assertEqual(
            (self.run_dir / "requests" / f"{original_id}.json").read_bytes(), original_bytes,
            msg="R5: Originalbytes unveraendert",
        )


class TestRunFullSectionCallerBoundary(unittest.TestCase):
    """Caller-naher Nachweis (Briefing: 'wenn mit vertretbarem Aufwand
    moeglich'): `run_full_section`s aeusserer Catch (Zeilen ~2274-2286)
    faengt AUSSCHLIESSLICH `_GateBlocked` und uebersetzt per `blocked_outcome(
    e.reason, recovery_pause=isinstance(e, _RecoveryPause))`. Dies prueft
    DIESEN Codepfad direkt am Quelltext (keine volle `run_full_section`-
    Ausfuehrung -- deren Aufbau liegt ausserhalb der Dateigrenze dieses
    Nachzugs/ist fuer einen engen Regressionstest unverhaeltnismaessig) und
    bestaetigt per `inspect`, dass eine `_RecoveryPause` (jetzt aus den
    beiden Callern oben per `isinstance` erreichbar) exakt den Pfad nimmt,
    der `recovery_pause=True` erzeugt. Ehrliche Grenze: dies ist ein
    codegelesener Nachweis der Catch-Bindung, kein ausgefuehrter
    `run_full_section`-Lauf."""

    def test_run_full_section_catches_gate_blocked_and_sets_recovery_pause_via_isinstance(self):
        import inspect
        import mmo_sim.core.runtime as runtime_mod

        source = inspect.getsource(runtime_mod.SectionRuntime.run_full_section)
        self.assertIn("except _GateBlocked as e", source)
        self.assertIn("recovery_pause=isinstance(e, _RecoveryPause)", source)
        print("[R5-r3-caller-boundary] run_full_section faengt _GateBlocked und setzt "
              "recovery_pause=isinstance(e, _RecoveryPause) -- codegelesen, kein ausgefuehrter Lauf.")

        # Die beiden Caller oben werfen jetzt _RecoveryPause -- diese
        # isinstance-Pruefung ist exakt das, was der Catch oben auswertet.
        exc = _RecoveryPause("synthetic")
        self.assertTrue(isinstance(exc, _GateBlocked))
        self.assertTrue(isinstance(exc, _RecoveryPause))


if __name__ == "__main__":
    unittest.main()
