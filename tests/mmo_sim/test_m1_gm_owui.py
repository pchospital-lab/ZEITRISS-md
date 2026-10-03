#!/usr/bin/env python3
"""
tests/mmo_sim/test_m1_gm_owui.py — `gm_owui`-Adapter: laedt den ECHTEN
`agent_mp/sl_client.py` per Pfad und prueft den Preflight-Fail-Fast-Pfad
(fehlender OPENWEBUI_API_KEY -> RuntimeError, KEIN stiller Fallback, KEIN
echter Netzwerkaufruf). Ein vollstaendiger HTTP-Payload-Test wie bei
persona_api ist hier NICHT enthalten (sl_client nutzt owui_client.OWUIChat
mit eigenem Retry/Backoff auf Modulebene) — als LUECKE im Report vermerkt."""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.gm_owui import GmOwuiTransport, _validate_gm_output_limit_tokens  # noqa: E402

_SL_CLIENT_PATH = _REPO_ROOT / "internal" / "qa" / "harness" / "agent_mp" / "sl_client.py"


def test_gm_owui_loads_real_module_by_explicit_path():
    assert _SL_CLIENT_PATH.exists(), "sl_client.py muss am dokumentierten Ort existieren"


def test_gm_owui_fails_fast_without_api_key_no_network_call():
    old = os.environ.pop("OPENWEBUI_API_KEY", None)
    try:
        try:
            GmOwuiTransport(_SL_CLIENT_PATH, run_dir="/tmp/gm-owui-test-run")
            assert False, "haette RuntimeError werfen muessen (kein API-Key)"
        except RuntimeError as e:
            assert "OPENWEBUI_API_KEY" in str(e)
    finally:
        if old is not None:
            os.environ["OPENWEBUI_API_KEY"] = old


# ---------------------------------------------------------------- B2 (MAIN-KORREKTUR I2-Nacharbeit 2026-09-24): Wertegueltigkeit
def test_gm_output_limit_none_stays_unconfigured():
    """Legacy-P1: kein Wert -- bleibt `None`, keine P2-Budgetfreigabe daraus."""
    assert _validate_gm_output_limit_tokens(None) is None


def test_gm_output_limit_valid_positive_int_normalized():
    assert _validate_gm_output_limit_tokens(50) == 50
    assert isinstance(_validate_gm_output_limit_tokens(50), int)


def test_gm_output_limit_valid_whole_float_normalized_to_int():
    """`50.0` (aus Env-Var-Parsing via `float(...)`) ist real eine Ganzzahl --
    muss auf einen echten `int` normalisiert werden (JSON-Body-Anforderung,
    kein `50.0` im HTTP-Body)."""
    value = _validate_gm_output_limit_tokens(50.0)
    assert value == 50
    assert isinstance(value, int)


def test_gm_output_limit_rejects_zero():
    """B2 0-Edge (REVIEW-I2.md §4): `0` ist keine durchsetzbare Grenze --
    darf NICHT stillschweigend als bekannt/unbegrenzt durchgehen."""
    try:
        _validate_gm_output_limit_tokens(0)
        assert False, "haette ValueError werfen muessen (0 ist keine positive Grenze)"
    except ValueError:
        pass


def test_gm_output_limit_rejects_negative():
    try:
        _validate_gm_output_limit_tokens(-5)
        assert False, "haette ValueError werfen muessen (negativ)"
    except ValueError:
        pass


def test_gm_output_limit_rejects_bool():
    """`bool` ist technisch eine `int`-Unterklasse -- `True`/`False` sind
    KEINE sinnvollen Tokengrenzen."""
    try:
        _validate_gm_output_limit_tokens(True)
        assert False, "haette ValueError werfen muessen (bool)"
    except ValueError:
        pass


def test_gm_output_limit_rejects_fraction():
    try:
        _validate_gm_output_limit_tokens(50.5)
        assert False, "haette ValueError werfen muessen (Bruch)"
    except ValueError:
        pass


def test_gm_output_limit_rejects_non_finite():
    for bad in (float("inf"), float("-inf"), float("nan")):
        try:
            _validate_gm_output_limit_tokens(bad)
            assert False, f"haette ValueError werfen muessen (nicht endlich: {bad})"
        except ValueError:
            pass


def test_gm_owui_transport_rejects_invalid_limit_before_any_side_effect():
    """`GmOwuiTransport.__init__` validiert VOR jedem Seiteneffekt (Modul-
    laden/Verzeichnisanlage/Session-Aufbau) -- ein ungueltiger Wert wirft
    `ValueError`, OHNE dass `OPENWEBUI_API_KEY`/Netzwerk ueberhaupt relevant
    wird."""
    old = os.environ.pop("OPENWEBUI_API_KEY", None)
    try:
        try:
            GmOwuiTransport(_SL_CLIENT_PATH, run_dir="/tmp/gm-owui-test-run-invalid-limit", gm_output_limit_tokens=0)
            assert False, "haette ValueError werfen muessen (0 ist keine positive Grenze)"
        except ValueError as e:
            assert "gm_output_limit_tokens" in str(e)
    finally:
        if old is not None:
            os.environ["OPENWEBUI_API_KEY"] = old


def main() -> int:
    tests = [
        test_gm_owui_loads_real_module_by_explicit_path,
        test_gm_owui_fails_fast_without_api_key_no_network_call,
        test_gm_output_limit_none_stays_unconfigured,
        test_gm_output_limit_valid_positive_int_normalized,
        test_gm_output_limit_valid_whole_float_normalized_to_int,
        test_gm_output_limit_rejects_zero,
        test_gm_output_limit_rejects_negative,
        test_gm_output_limit_rejects_bool,
        test_gm_output_limit_rejects_fraction,
        test_gm_output_limit_rejects_non_finite,
        test_gm_owui_transport_rejects_invalid_limit_before_any_side_effect,
    ]
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
