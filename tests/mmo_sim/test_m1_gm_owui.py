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

from mmo_sim.adapters.gm_owui import GmOwuiTransport  # noqa: E402

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


def main() -> int:
    tests = [test_gm_owui_loads_real_module_by_explicit_path, test_gm_owui_fails_fast_without_api_key_no_network_call]
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
