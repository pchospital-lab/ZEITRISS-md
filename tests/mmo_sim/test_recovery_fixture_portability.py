#!/usr/bin/env python3
"""
tests/mmo_sim/test_recovery_fixture_portability.py — Portabilitaetsvertrag
der Recovery-Pflichtfixtures (ZR-LIVEWEG-PR-KANDIDAT-20261016-R1,
01_AUFTRAG.md C): ein frischer OEFFENTLICHER Repo-Checkout braucht KEIN
privates Pruefpaket (`ZEITRISS_R1_BUDGET_CALC`/`ZEITRISS_R1_CONTROL_JSON`/
`ZEITRISS_R2_PKG_ROOT`) mehr, um `test_recovery_ops_r1.py`/
`test_recovery_ops_r2.py` vollstaendig zu bestehen -- die drei neutralen
Fixturedateien unter `tests/mmo_sim/fixtures/recovery_contract/` liegen
IMMER im Checkout. Eine ausdruecklich auf eine NICHT vorhandene Datei
zeigende Variable bleibt weiterhin ehrlich BLOCKED_ENV/nonzero (kein
optionaler SKIP fuer einen Pflichtfall).

Pure Python, nur `assert`, echter Exitcode (gleiches Muster wie die
uebrigen `test_*.py` dieses Pakets)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _recovery_public_fixture_paths import (  # noqa: E402
    DEFAULT_BUDGET_CALC, DEFAULT_CONTROL_JSON, resolve_budget_calc, resolve_control_json,
)

_PRIVATE_ENV_NAMES = ("ZEITRISS_R1_BUDGET_CALC", "ZEITRISS_R1_CONTROL_JSON", "ZEITRISS_R2_PKG_ROOT")


def _clean_env() -> dict:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in _PRIVATE_ENV_NAMES:
        env.pop(name, None)
    return env


def test_neutral_defaults_exist_in_repo():
    """Die beiden neutralen Repo-Fixturen liegen IMMER im Checkout -- kein
    Exchange-/Chatpaket, kein Pfad ausserhalb von `tests/mmo_sim/`."""
    assert DEFAULT_BUDGET_CALC.is_file(), DEFAULT_BUDGET_CALC
    assert DEFAULT_CONTROL_JSON.is_file(), DEFAULT_CONTROL_JSON
    for p in (DEFAULT_BUDGET_CALC, DEFAULT_CONTROL_JSON):
        assert _REPO_ROOT in p.parents, f"{p} liegt ausserhalb des Repo-Checkouts."


def test_neutral_control_json_structurally_valid():
    data = json.loads(DEFAULT_CONTROL_JSON.read_text(encoding="utf-8"))
    for key in ("allowed_existing_candidate_paths", "allowed_new_candidate_paths"):
        assert isinstance(data.get(key), list) and data[key], (key, data)


def test_neutral_budget_calc_exposes_required_contract():
    """`test_recovery_ops_r1.py::test_budget_seed_30_independent_cases`
    braucht `physical_cost_usd`/`BudgetBlocked` UND einen `main()`, der
    `{"schema": "general-budget-seed/1", "positive_cases": [...], "negative_cases": [...]}`
    auf stdout druckt, rc=0."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("_neutral_budget_calc_fixture", DEFAULT_BUDGET_CALC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.physical_cost_usd)
    assert issubclass(module.BudgetBlocked, Exception)

    proc = subprocess.run([sys.executable, "-B", str(DEFAULT_BUDGET_CALC)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["schema"] == "general-budget-seed/1"
    assert len(report["positive_cases"]) >= 7 and len(report["negative_cases"]) >= 5


def test_resolver_env_override_still_works():
    """Rueckwaertskompatibilitaet: ist die Env explizit gesetzt, bindet sie
    weiterhin UNVERAENDERT (ein Betreiber kann ein eigenes Referenzpaket
    einhaengen) -- die neutrale Defaultbindung ist additiv, kein Ersatz."""
    with tempfile.TemporaryDirectory() as td:
        custom = Path(td) / "custom_budget_calc.py"
        custom.write_text(DEFAULT_BUDGET_CALC.read_text(encoding="utf-8"), encoding="utf-8")
        old = os.environ.get("ZEITRISS_R1_BUDGET_CALC")
        os.environ["ZEITRISS_R1_BUDGET_CALC"] = str(custom)
        try:
            assert resolve_budget_calc() == custom
        finally:
            if old is None:
                os.environ.pop("ZEITRISS_R1_BUDGET_CALC", None)
            else:
                os.environ["ZEITRISS_R1_BUDGET_CALC"] = old


def test_resolver_without_env_falls_back_to_neutral_default():
    old = os.environ.pop("ZEITRISS_R1_CONTROL_JSON", None)
    try:
        assert resolve_control_json() == DEFAULT_CONTROL_JSON
    finally:
        if old is not None:
            os.environ["ZEITRISS_R1_CONTROL_JSON"] = old


def test_r1_full_regression_without_any_private_env():
    """Der zentrale Portabilitaetsnachweis: `test_recovery_ops_r1.py` mit
    GENAU den drei privaten Variablen entfernt (kein Privatpaket, kein
    Exchange-/Chatpaket) -- alle 22 Faelle real durch, rc=0."""
    proc = subprocess.run(
        [sys.executable, "-B", str(_HERE / "test_recovery_ops_r1.py")],
        capture_output=True, text=True, env=_clean_env(), cwd=str(_HERE),
    )
    assert proc.returncode == 0, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    assert "22/22 bestanden, 0 fehlgeschlagen, 0 BLOCKED_ENV." in proc.stdout, proc.stdout


def test_r2_full_regression_without_any_private_env():
    proc = subprocess.run(
        [sys.executable, "-B", str(_HERE / "test_recovery_ops_r2.py")],
        capture_output=True, text=True, env=_clean_env(), cwd=str(_HERE),
    )
    assert proc.returncode == 0, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    assert "27/27 bestanden, 0 fehlgeschlagen, 0 BLOCKED_ENV, 0 BLOCKED." in proc.stdout, proc.stdout


def test_explicitly_missing_fixture_file_is_nonzero_not_skip():
    """01_AUFTRAG.md C: 'waehlt jetzt ausdruecklich eine nicht vorhandene
    Datei, statt den legalen Repo-Default durch Weglassen einer optionalen
    Env zu verbieten' -- eine Env, die ausdruecklich auf eine NICHT
    existierende Datei zeigt, bleibt BLOCKED_ENV/nonzero. Kein optionaler
    SKIP fuer einen Pflichtfall."""
    env = _clean_env()
    env["ZEITRISS_R1_BUDGET_CALC"] = str(Path(tempfile.mkdtemp()) / "genuinely-missing-budget-calc.py")
    proc = subprocess.run(
        [sys.executable, "-B", str(_HERE / "test_recovery_ops_r1.py")],
        capture_output=True, text=True, env=env, cwd=str(_HERE),
    )
    assert proc.returncode != 0, proc.stdout
    assert "BLOCKED_ENV" in proc.stdout
    assert "22/22" not in proc.stdout


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)]
    passed, failed = 0, 0
    for t in sorted(tests, key=lambda f: f.__name__):
        try:
            t()
            print(f"OK      {t.__name__}")
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"FAIL    {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR   {t.__name__}:")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} bestanden, {failed} fehlgeschlagen.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
