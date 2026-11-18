#!/usr/bin/env python3
"""
tests/mmo_sim/test_r3_06_operator_budget_setup.py — R3-06 (ZR-ALTAIR-
UPDATER-SPIELTEST-NACHZUG-20261118-r3): der normale Solo-Start darf keine
internen Operator-Dateieingriffe (Handedit von `lab.status.json`) mehr
verlangen. `core.admission.grant_operator_budget` ist der neue, normal
bedienbare Weg, eine Betreiber-Live-/Budgetfreigabe herzustellen -- ohne
`provider_free` (das bleibt ausschliesslich fuer kontrollierte Test-
Doubles reserviert) und ohne die Singleton-Lock-Semantik von
`lab.runner.LabRunner` zu uebernehmen.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core import admission  # noqa: E402


def test_grant_establishes_recognized_authorization_without_provider_free():
    with tempfile.TemporaryDirectory() as run_dir:
        blocked_before, _ = admission.read_admission_block(run_dir)
        assert blocked_before, "vor der Freigabe muss die Erschaffung blockiert bleiben (fail-closed)"

        admission.grant_operator_budget(run_dir, max_turns=50, max_seconds=3600.0, max_usd=5.0)

        blocked_after, reason = admission.read_admission_block(run_dir)
        assert not blocked_after, f"nach normaler Betreiberfreigabe sollte kein Block mehr gelten: {reason}"

        import json
        data = json.loads((Path(run_dir) / "lab.status.json").read_text(encoding="utf-8"))
        assert data.get("provider_free") is not True, (
            "eine echte Betreiberfreigabe darf NIE provider_free=True setzen -- "
            "das waere eine falsche Kennzeichnung einer echten Cloudroute als Testdouble"
        )
        assert data["max_turns"] == 50
        assert data["max_usd"] == 5.0


def test_grant_does_not_reset_existing_usage_counters():
    with tempfile.TemporaryDirectory() as run_dir:
        admission.grant_operator_budget(run_dir, max_turns=10, max_seconds=600.0, max_usd=1.0)
        admission.record_turn_usage(run_dir, 12.0, 0.2)

        # Erneuter Grant-Versuch ohne allow_overwrite darf NICHT geschehen
        # (bereits eine Grenze gesetzt) -- Verbrauch bleibt unberuehrt.
        raised = False
        try:
            admission.grant_operator_budget(run_dir, max_turns=999, max_seconds=999.0)
        except admission.OperatorBudgetAlreadyGrantedError:
            raised = True
        assert raised, "ein zweiter Grant ohne allow_overwrite darf eine bestehende Grenze nicht stillschweigend aendern"

        import json
        data = json.loads((Path(run_dir) / "lab.status.json").read_text(encoding="utf-8"))
        assert data["max_turns"] == 10, "unveraendert -- kein heimliches Hochsetzen"
        assert data["usd_spent"] == 0.2, "Verbrauch bleibt erhalten (Resume-vertraeglich)"


def test_explicit_allow_overwrite_can_raise_an_existing_limit():
    with tempfile.TemporaryDirectory() as run_dir:
        admission.grant_operator_budget(run_dir, max_turns=10, max_seconds=600.0)
        admission.grant_operator_budget(run_dir, max_turns=20, max_seconds=1200.0, allow_overwrite=True)
        import json
        data = json.loads((Path(run_dir) / "lab.status.json").read_text(encoding="utf-8"))
        assert data["max_turns"] == 20


def test_guest_cannot_derive_operator_rights_from_grant_alone():
    """R3-06-Abnahme: 'Gast erhaelt daraus keine Betreiberrechte' -- die
    Freigabe ist eine reine Datei-Autorisierung fuer `read_admission_block`,
    kein Identitaets-/Rollenwechsel. `grant_operator_budget` selbst kennt
    gar keinen Teilnehmerbegriff (Host-Gate bleibt Aufgabe der TUI, s.
    `_require_host`) -- dieser Test belegt nur, dass die Funktion keine
    rollenbezogenen Felder schreibt."""
    with tempfile.TemporaryDirectory() as run_dir:
        admission.grant_operator_budget(run_dir, max_turns=5, max_seconds=60.0)
        import json
        data = json.loads((Path(run_dir) / "lab.status.json").read_text(encoding="utf-8"))
        assert "host" not in data and "role" not in data and "guest" not in data


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
