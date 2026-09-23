#!/usr/bin/env python3
"""
tests/mmo_sim/test_a03_billing_var_check.py — A3 (PLAN-CRITIC.md WICHTIG):
eigener, neuer Test fuer den Billing-Var-Check (I2). `review_p2_integration.
py` Test 04 assertiert die `synthetic_*_key`-Beobachtungen NICHT (nur
`note(...)`) und koppelt Isolation nicht mehr hart an leere
`extra_isolation_flags` (s. `adapters/persona_claude_code.check_isolation`)
-- ein fehlender Billing-Check bliebe sonst trotz 14/14 gruen unentdeckt.
Dieser Test belegt DIREKT: Billing-Risk-Vars in der geerbten Umgebung
blockieren einen Request VOR jeder Inferenz, unabhaengig vom Isolationsstatus.

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import os
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ProviderUnavailableError  # noqa: E402
from mmo_sim.adapters.fakes import FakeCLIProcess  # noqa: E402
from mmo_sim.adapters.persona_claude_code import (  # noqa: E402
    BILLING_RISK_ENV_VARS, ClaudeCodeConfig, PersonaClaudeCodeDriver,
)


def _clean_env() -> dict:
    return {k: v for k, v in os.environ.items() if k not in BILLING_RISK_ENV_VARS}


def test_billing_risk_var_blocks_request_before_inference():
    with tempfile.TemporaryDirectory() as workdir:
        fake = FakeCLIProcess([
            (0, "claude-code 1.2.3", ""), (0, "usage: ... [--strict-mcp-config]", ""),
            (0, "sollte nie aufgerufen werden", ""),
        ])
        driver = PersonaClaudeCodeDriver(
            ClaudeCodeConfig(binary="claude", isolated_workdir=workdir,
                              extra_isolation_flags=["--strict-mcp-config"]),
            "p1", process_runner=fake,
        )
        env = _clean_env()
        env["ANTHROPIC_API_KEY"] = "SYNTHETIC_BILLING_SENTINEL"
        rejected = False
        with patch.dict(os.environ, env, clear=True):
            try:
                driver.decide({"user": "u"})
            except ProviderUnavailableError:
                rejected = True
        assert rejected, "Billing-Risk-Var haette den Request VOR Inferenz blockieren muessen"
        inference_calls = [c for c in fake.calls if "-p" in c.argv]
        assert not inference_calls, "kein Inferenzaufruf trotz Billing-Risk-Var erwartet"


def test_each_billing_risk_var_individually_blocks():
    for var in BILLING_RISK_ENV_VARS:
        with tempfile.TemporaryDirectory() as workdir:
            fake = FakeCLIProcess([
                (0, "claude-code 1.2.3", ""), (0, "usage: ... [--strict-mcp-config]", ""),
                (0, "sollte nie aufgerufen werden", ""),
            ])
            driver = PersonaClaudeCodeDriver(
                ClaudeCodeConfig(binary="claude", isolated_workdir=workdir,
                                  extra_isolation_flags=["--strict-mcp-config"]),
                "p1", process_runner=fake,
            )
            env = _clean_env()
            env[var] = "SYNTHETIC_SENTINEL"
            rejected = False
            with patch.dict(os.environ, env, clear=True):
                try:
                    driver.decide({"user": "u"})
                except ProviderUnavailableError:
                    rejected = True
            assert rejected, f"{var} haette blockieren muessen"
            inference_calls = [c for c in fake.calls if "-p" in c.argv]
            assert not inference_calls, f"kein Inferenzaufruf trotz {var} erwartet"


def test_clean_environment_does_not_block_on_billing_check():
    """Positivkontrolle: OHNE Billing-Risk-Vars laesst der Check den Request
    durch (isoliert die Wirkung des Billing-Checks von der Isolationslogik --
    Isolation ist hier durch `extra_isolation_flags` regulaer belegt)."""
    with tempfile.TemporaryDirectory() as workdir:
        fake = FakeCLIProcess([
            (0, "claude-code 1.2.3", ""), (0, "usage: ... [--strict-mcp-config]", ""),
            (0, "echte Antwort", ""),
        ])
        driver = PersonaClaudeCodeDriver(
            ClaudeCodeConfig(binary="claude", isolated_workdir=workdir,
                              extra_isolation_flags=["--strict-mcp-config"]),
            "p1", process_runner=fake,
        )
        with patch.dict(os.environ, _clean_env(), clear=True):
            decision = driver.decide({"user": "u"})
        assert decision.text == "echte Antwort"


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
