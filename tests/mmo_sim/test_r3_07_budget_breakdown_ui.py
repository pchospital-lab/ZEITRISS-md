#!/usr/bin/env python3
"""
tests/mmo_sim/test_r3_07_budget_breakdown_ui.py — R3-07 Code-Teil
(ZR-ALTAIR-UPDATER-SPIELTEST-NACHZUG-20261118-r3): Sicherheitsreservierung/
geschaetzter+tatsaechlicher Verbrauch/unbekannte Werte muessen in der
normalen Oberflaeche ('einstellungen budget') SICHTBAR GETRENNT werden,
nicht nur als additiver `usd_spent`-Gesamtbetrag. Zusaetzlich muss ein
Betreiber eine bestehende, zu konservative Grenze ueber die normale
Oberflaeche ANHEBEN koennen ('einstellungen budget erhoehen'), ohne
`lab.status.json` von Hand zu editieren und ohne heimliches Hochsetzen
(jeder neue Wert muss explizit bestaetigt werden).

Treibt den echten Aufrufer `TuiSession._cmd_settings(args)` an.
Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.core.admission import _status_path, grant_operator_budget  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402


def _scripted_input(answers):
    it = iter(answers)

    def read(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError()

    return read


def _session(root: Path, *, input_fn=None):
    run_dir = root / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    printed: list[str] = []
    session = TuiSession(
        onboarding_dir=root / "onboarding", catalog_dir=root / "catalog", participant_id="p1",
        input_fn=input_fn, print_fn=printed.append, run_dir=run_dir,
    )
    return session, run_dir, printed


def test_breakdown_separates_reservation_spent_limit_and_unknown_turns():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        grant_operator_budget(run_dir, max_turns=10, max_seconds=600.0, max_usd=5.0)
        data = json.loads(_status_path(run_dir).read_text(encoding="utf-8"))
        data["usd_spent"] = 1.2345
        data["turns_used"] = 3
        data["usd_unknown_turns"] = 2
        from mmo_sim.core.admission import _atomic_write_json
        _atomic_write_json(_status_path(run_dir), data)

        printed: list[str] = []
        session = TuiSession(
            onboarding_dir=root / "onboarding", catalog_dir=root / "catalog", participant_id="p1",
            print_fn=printed.append, run_dir=run_dir,
        )
        session._cmd_settings(["budget"])

        joined = "\n".join(printed)
        assert "1.2345" in joined and "5.0000" in joined, printed
        assert "2 Anfrage(n) mit NICHT vom Provider gemeldeten" in joined, printed
        assert "3" in joined and "10" in joined, printed  # turns_used/max_turns sichtbar


def test_no_authorization_yet_is_stated_plainly_not_as_zero_usage():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session, run_dir, printed = _session(root)
        session._cmd_settings(["budget"])
        assert any("noch keine vorhanden" in p for p in printed), printed
        assert not any("usd_spent" in p.lower() or "0.0000" in p for p in printed), printed


def test_operator_can_raise_an_existing_limit_through_the_normal_ui():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        grant_operator_budget(run_dir, max_turns=5, max_seconds=60.0, max_usd=1.0)

        session, _run_dir, printed = _session(
            root, input_fn=_scripted_input(["20", "", "", "j"]),  # neue Turns, Rest behalten, bestaetigen
        )
        session._cmd_settings(["budget", "erhoehen"])

        data = json.loads(_status_path(run_dir).read_text(encoding="utf-8"))
        assert data["max_turns"] == 20
        assert data["max_seconds"] == 60.0  # leer gelassen -> unveraendert
        assert data["max_usd"] == 1.0
        assert any("aktualisiert" in p for p in printed), printed


def test_declining_the_confirmation_leaves_the_limit_unchanged():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        run_dir = root / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        grant_operator_budget(run_dir, max_turns=5, max_seconds=60.0, max_usd=1.0)

        session, _run_dir, printed = _session(
            root, input_fn=_scripted_input(["999", "999", "999", "n"]),
        )
        session._cmd_settings(["budget", "erhoehen"])

        data = json.loads(_status_path(run_dir).read_text(encoding="utf-8"))
        assert data["max_turns"] == 5, "keine stille Uebernahme ohne Bestaetigung"


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
            import traceback
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
