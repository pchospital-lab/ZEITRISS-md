#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n2_autowired_visibility_2026_11_09.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N2 WP-N2-1c (P1b-Teil).

Vorher berechnete `scripts/setup.py:run_install_litellm` (jetzt ausgelagert
nach `ensure_litellm_autowire`) `auto_wired = ok_conn and ok_rewire` --
die vorher geprüfte Modellsichtbarkeit (`_wait_for_owui_model_visible`)
floss NUR in eine Warnung, nie in die Abschlusslage. Ein Preset, das auf
ein Modell zeigt, das OWUI noch nicht in seiner Modell-Liste hat, wurde so
fälschlich als "live verkabelt" gemeldet -- eine behauptete externe
Modellantwort, die nie bestätigt wurde.

Deckt:
  (A) Connection + Rewire OK, aber Sichtbarkeit NICHT bestätigt ->
      `ensure_litellm_autowire` liefert `False` (nicht "live verkabelt"),
      und druckt den eigenen Zwischenstand ("konfiguriert, aber nicht
      sichtbar"), nicht eine der beiden anderen Meldungen.
  (B) Connection + Rewire + Sichtbarkeit alle True -> `True` ("live
      verkabelt").

Double-Grenze (A4, offen gelegt): `_ensure_owui_litellm_connection`,
`_rewire_preset_base_model`, `_wait_for_owui_model_visible`,
`_auto_load_owui_env`, `_read_env_file` sind vollständig gedoubelt. Kein
Docker/Netzwerk-Call.

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import io
import traceback
import unittest.mock as mock
from contextlib import redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n2_autowired_visibility_setup_under_test", _SETUP_PY,
)
setup_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_mod)


def _base_mocks(*, ok_conn=True, ok_rewire=True, visible=True):
    return [
        mock.patch.object(setup_mod, "_read_env_file", return_value={"LITELLM_MASTER_KEY": "sk-litellm-test"}),
        mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False),
        mock.patch.object(setup_mod, "_litellm_routing_model_id", return_value="proj-sonnet"),
        mock.patch.object(setup_mod, "_ensure_owui_litellm_connection", return_value=(ok_conn, "conn-msg")),
        mock.patch.object(setup_mod, "_wait_for_owui_model_visible", return_value=visible),
        mock.patch.object(setup_mod, "_rewire_preset_base_model", return_value=(ok_rewire, "rewire-msg")),
    ]


def _run_with_env_key(cfg):
    import os
    saved = dict(os.environ)
    os.environ["OPENWEBUI_API_KEY"] = "owui-test-key"
    os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            result = setup_mod.ensure_litellm_autowire(Path("/tmp/repo-fake"), cfg)
        return result, buf.getvalue()
    finally:
        os.environ.clear()
        os.environ.update(saved)


_CFG = {"project": "Proj", "variants": {"default": {"preset_id": "p1", "cache": True}}}


def test_connected_and_rewired_but_not_visible_is_not_auto_wired():
    mocks = _base_mocks(ok_conn=True, ok_rewire=True, visible=False)
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5]:
        result, out = _run_with_env_key(_CFG)
    assert result is False, "Connection+Rewire OHNE bestaetigte Sichtbarkeit duerfen NICHT als auto_wired=True gelten"
    assert "Cache ist live verkabelt" not in out, out
    assert "noch nicht als sichtbar bestätigt" in out, out


def test_connected_rewired_and_visible_is_auto_wired():
    mocks = _base_mocks(ok_conn=True, ok_rewire=True, visible=True)
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5]:
        result, out = _run_with_env_key(_CFG)
    assert result is True, out
    assert "Cache ist live verkabelt" in out, out


def test_connection_failed_is_not_auto_wired_regardless_of_visibility():
    mocks = _base_mocks(ok_conn=False, ok_rewire=True, visible=True)
    with mocks[0], mocks[1], mocks[2], mocks[3], mocks[4], mocks[5]:
        result, out = _run_with_env_key(_CFG)
    assert result is False, out
    assert "Cache ist live verkabelt" not in out, out


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
            print(f"ERROR {t.__name__}:")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
