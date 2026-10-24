#!/usr/bin/env python3
"""
tests/mmo_sim/test_n2r5_timeoutfix_persona_timeout_2026_10_20.py —
N2R5-TIMEOUTFIX (ZR-N2R-ANSCHLUSS-20261019-R4, worker/BRIEF-timeoutfix-rerun.md).

Reproduziert den realen live1-Befund (`worker/driftfix1/work4`-Re-Run):
EIN echter `claude -p ...`-Call > 120s -> `subprocess.TimeoutExpired` ->
`ProviderUnavailableError` -> terminaler `lab-Subprozess rc=1` (`Provider-
UnavailableError` wird in `mmo_sim/` NIRGENDS gefangen, s. FIX.diff/REPORT.md
Diagnose). Zwei Hebel, beide additiv/optional (Default unveraendert):

1. `ClaudeCodeConfig.process_timeout_seconds` wird jetzt tatsaechlich von
   `factories.default_persona_driver_factory` aus `MMO_SIM_PERSONA_TIMEOUT_
   SECONDS` gelesen (vorher: LAUNCH-SPEC `timing.persona_timeout_seconds`
   erreichte diesen Konstruktionsort NIE, blieb am hartverdrahteten 120s-
   Default -- Test 1/2 unten).
2. `ClaudeCodeConfig.max_timeout_retries` erlaubt einen bounded Re-Dispatch
   NUR nach `subprocess.TimeoutExpired` (NICHT nach rc!=0/anderen
   Exceptions) -- Test 3 (Retry rettet den Call) / Test 4 (Budget bleibt
   hart, kein unendlicher Retry) / Test 5 (rc!=0 wird NICHT maskiert).

Pure Python, nur `assert`, echter Exitcode -- gleiches Muster wie
`test_n2r5_driftfix_creation_core_identity_2026_10_20.py`."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ProviderUnavailableError  # noqa: E402
from mmo_sim.adapters.persona_claude_code import ClaudeCodeConfig, PersonaClaudeCodeDriver  # noqa: E402


class _FakeRunner:
    """Lokaler Test-Doppelgaenger fuer `process_runner` (injizierbar, s.
    `PersonaClaudeCodeDriver.__init__`-Docstring) -- liefert der Reihe nach
    konfigurierte Ergebnisse, wobei ein Ergebnis entweder ein
    `(rc, stdout, stderr)`-Tupel ODER eine Exception-Instanz sein kann
    (wird dann bei genau diesem Aufruf geworfen)."""

    def __init__(self, results: list):
        self._results = list(results)
        self.calls = 0

    def run(self, argv, stdin="", env=None, cwd=None):
        self.calls += 1
        if not self._results:
            raise RuntimeError("_FakeRunner: keine weiteren gecannten Ergebnisse.")
        item = self._results.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


_ISOLATED_CALL_ARGS = {"isolation_already_checked": True}


def _make_driver(runner: _FakeRunner, *, max_timeout_retries: int = 0) -> PersonaClaudeCodeDriver:
    config = ClaudeCodeConfig(
        binary="claude", isolated_workdir="/tmp", extra_isolation_flags=[],
        max_timeout_retries=max_timeout_retries,
    )
    driver = PersonaClaudeCodeDriver(config, "p_timeoutfix_test", process_runner=runner)
    driver._isolation_checked = True  # Isolation ist hier nicht der Testgegenstand.
    return driver


_OK_JSON = '{"type": "result", "subtype": "success", "result": "ok", "usage": {}, "is_error": false}'


def test_default_retries_zero_still_raises_after_single_timeout():
    """Byte-identisches Verhalten zu vorher: ohne explizit gesetztes
    `max_timeout_retries` (Default 0) killt EIN Timeout den Call sofort --
    kein bestehender Aufrufer aendert durch den Fix sein Verhalten."""
    timeout_exc = subprocess.TimeoutExpired(cmd=["claude"], timeout=120)
    runner = _FakeRunner([timeout_exc])
    driver = _make_driver(runner, max_timeout_retries=0)
    try:
        driver.decide({"system": "", "turn": 1})
        raise AssertionError("haette ProviderUnavailableError werfen muessen.")
    except ProviderUnavailableError as e:
        assert "Zeitueberschreitung" in str(e)
    assert runner.calls == 1, f"genau EIN Versuch bei max_timeout_retries=0, war {runner.calls}"


def test_single_timeout_then_success_is_retried_not_fatal():
    """Der reale live1-Fall: EIN langsamer Call > Timeout, danach waere ein
    zweiter Versuch erfolgreich -- mit `max_timeout_retries=1` killt das
    NICHT mehr die ganze Section (kein `ProviderUnavailableError`,
    `decide()` liefert die echte Antwort des zweiten Versuchs)."""
    timeout_exc = subprocess.TimeoutExpired(cmd=["claude"], timeout=240)
    runner = _FakeRunner([timeout_exc, (0, _OK_JSON, "")])
    driver = _make_driver(runner, max_timeout_retries=1)
    decision = driver.decide({"system": "", "turn": 1})
    assert decision.text == "ok"
    assert runner.calls == 2, f"genau EIN Re-Dispatch nach dem Timeout, war {runner.calls} Aufrufe"


def test_timeout_retry_budget_is_bounded_not_infinite():
    """`max_timeout_retries=1` erlaubt GENAU einen zusaetzlichen Versuch --
    ein ZWEITER Timeout in Folge bleibt weiterhin ein ehrlicher
    `ProviderUnavailableError` (kein unbegrenzter Re-Dispatch, kein stilles
    Haengenbleiben)."""
    timeout_exc_1 = subprocess.TimeoutExpired(cmd=["claude"], timeout=240)
    timeout_exc_2 = subprocess.TimeoutExpired(cmd=["claude"], timeout=240)
    runner = _FakeRunner([timeout_exc_1, timeout_exc_2])
    driver = _make_driver(runner, max_timeout_retries=1)
    try:
        driver.decide({"system": "", "turn": 1})
        raise AssertionError("haette nach Erschoepfung des Retry-Budgets werfen muessen.")
    except ProviderUnavailableError as e:
        assert "Zeitueberschreitung" in str(e)
    assert runner.calls == 2, f"genau 1 Initial + 1 Retry, dann Abbruch, war {runner.calls}"


def test_non_timeout_failure_is_never_retried_even_with_budget():
    """`max_timeout_retries` gilt NUR fuer `subprocess.TimeoutExpired` -- ein
    echter rc!=0 (z.B. CLI-interner Fehler) bleibt sofort ein ehrlicher
    Fehler, selbst wenn ein Retry-Budget konfiguriert ist (keine stille
    Fehlermaskierung eines nicht-transienten Defekts, s. FIX.diff)."""
    runner = _FakeRunner([(1, "", "echter CLI-Fehler, kein Timeout")])
    driver = _make_driver(runner, max_timeout_retries=3)
    try:
        driver.decide({"system": "", "turn": 1})
        raise AssertionError("haette bei rc=1 sofort werfen muessen.")
    except ProviderUnavailableError as e:
        assert "Prozess rc=1" in str(e)
    assert runner.calls == 1, f"rc!=0 wird NICHT retried, war {runner.calls} Aufrufe"


def test_factory_wires_launch_spec_persona_timeout_into_claude_code_config():
    """Der eigentliche Wurzelfund (s. REPORT.md Diagnose): LAUNCH-SPEC
    `timing.persona_timeout_seconds` erreichte vorher NIE `ClaudeCodeConfig.
    process_timeout_seconds` -- der reale Subprozess-Timeout blieb immer am
    hartverdrahteten 120s-Default. `default_persona_driver_factory` muss den
    additiven, optionalen `MMO_SIM_PERSONA_TIMEOUT_SECONDS`-Wert jetzt real
    binden (Default bleibt 120, wenn das Env NICHT gesetzt ist).

    Pure Python (kein pytest-Fixture-Zwang, s. Moduldocstring) -- Env wird
    manuell gesichert/wiederhergestellt, `tempfile.mkdtemp()` statt
    `tmp_path`."""
    import os
    import shutil
    import tempfile

    from mmo_sim.adapters import factories

    saved = {
        k: os.environ.get(k)
        for k in (
            "MMO_SIM_PERSONA_CLI", "MMO_SIM_PERSONA_API_BASE_URL", "MMO_SIM_PERSONA_ISOLATION_FLAGS",
            "MMO_SIM_PERSONA_TIMEOUT_SECONDS", "MMO_SIM_PERSONA_TIMEOUT_RETRIES",
        )
    }
    workdir = Path(tempfile.mkdtemp(prefix="n2r5_timeoutfix_factory_test_"))
    try:
        os.environ["MMO_SIM_PERSONA_CLI"] = "claude"
        os.environ.pop("MMO_SIM_PERSONA_API_BASE_URL", None)
        os.environ.pop("MMO_SIM_PERSONA_ISOLATION_FLAGS", None)

        # Ohne das Env bleibt der Default unveraendert (kein bestehender
        # Aufrufer aendert sein Verhalten).
        os.environ.pop("MMO_SIM_PERSONA_TIMEOUT_SECONDS", None)
        os.environ.pop("MMO_SIM_PERSONA_TIMEOUT_RETRIES", None)
        factory_default = factories.default_persona_driver_factory(workdir, profile="hybrid")
        driver_default = factory_default("p_test")
        assert driver_default.config.process_timeout_seconds == 120
        assert driver_default.config.max_timeout_retries == 0

        # Mit gesetztem Env (wie es der Treiber jetzt aus LAUNCH-SPEC timing.
        # persona_timeout_seconds setzt, s. driver.integrated.py FIX.diff)
        # wird der reale Wert gebunden.
        os.environ["MMO_SIM_PERSONA_TIMEOUT_SECONDS"] = "240"
        os.environ["MMO_SIM_PERSONA_TIMEOUT_RETRIES"] = "1"
        factory_configured = factories.default_persona_driver_factory(workdir, profile="hybrid")
        driver_configured = factory_configured("p_test")
        assert driver_configured.config.process_timeout_seconds == 240, (
            f"LAUNCH-SPEC persona_timeout_seconds muss real bis ClaudeCodeConfig "
            f"durchreichen, war {driver_configured.config.process_timeout_seconds}"
        )
        assert driver_configured.config.max_timeout_retries == 1
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    failures = []
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {name}")
            except AssertionError as exc:
                failures.append(name)
                print(f"FAIL {name}: {exc}")
            except Exception as exc:  # noqa: BLE001 -- echter Exitcode, volle Diagnose
                failures.append(name)
                import traceback
                print(f"ERROR {name}: {exc}")
                traceback.print_exc()
    total = len([n for n in globals() if n.startswith("test_")])
    print(f"\n{total - len(failures)}/{total} Tests bestanden.")
    raise SystemExit(0 if not failures else 1)
