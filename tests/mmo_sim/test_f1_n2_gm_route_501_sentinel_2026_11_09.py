#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n2_gm_route_501_sentinel_2026_11_09.py — Delta-Test
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N2 WP-N2-2a (P2).

Vorher behandelte `scripts/mmo_sim.py:_resolve_active_gm_route` HTTP 501 auf
`GET /api/v1/models/model` als bewusste Produktausnahme (`(sl_model, None)`
statt Sentinel) -- ein HTTP-Status identifiziert aber keinen Testprozess.
Zusätzlich fielen fehlende/unlesbare `setup.json`/fehlende Preset-ID
(`(None, None)`) bei produktiver GM-Nutzung unbemerkt auf die in
`sl_client.py` hartkodierte HISTORISCHE Knowledge-Base zurück.

Deckt (schlanker, eigenständiger Beleg -- Vollabdeckung inkl. 401/403/404/0
und Double-Seam bleibt in `test_f1_gm_route_threading_2026_11_09.py`):
  (A) HTTP 501 -> `GM_ROUTE_KB_UNVERIFIED` (NICHT mehr `None`) -- die
      501-Produktausnahme ist vollständig entfernt.
  (B) Fehlendes `setup.json` -> `(None, GM_ROUTE_KB_UNVERIFIED)` -- der
      produktive Transportbau lehnt sichtbar ab (`default_gm_transport_
      factory` wirft), lokales Menü bleibt unberührt (Factory-KONSTRUKTION
      selbst wirft nicht).
  (C) Fehlende Preset-ID in der Default-Variante -> ebenfalls
      `(None, GM_ROUTE_KB_UNVERIFIED)`.
  (D) Positivpfad (200, gültiger KB-Link) bleibt unverändert grün.

Double-Grenze (A4, offen gelegt): `setup` (scripts/setup.py) wird durch ein
Fake-Modul in `sys.modules` ersetzt (eigenes `APIClient`, eigenes
`_auto_load_owui_env`) -- keine echte Netzwerk-/OWUI-Anbindung, reine
Entscheidungslogik-Prüfung. `scripts/mmo_sim.py` wird per Dateipfad geladen
(venv-Bootstrap gemockt, identische Technik wie die anderen F1-Tests).

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import traceback
import types
from pathlib import Path
from unittest import mock

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.factories import GM_ROUTE_KB_UNVERIFIED, default_gm_transport_factory  # noqa: E402


def _load_mmo_sim_entrypoint():
    spec = importlib.util.spec_from_file_location(
        "f1_n2_gm_route_501_sentinel_entrypoint_under_test", _REPO_ROOT / "scripts" / "mmo_sim.py",
    )
    module = importlib.util.module_from_spec(spec)
    with mock.patch.object(sys, "prefix", str(_REPO_ROOT / ".venv")):
        spec.loader.exec_module(module)
    return module


def _install_fake_setup_module(get_result):
    fake_setup = types.ModuleType("setup")

    def _auto_load_owui_env():
        return False

    class _FakeAPIClient:
        def __init__(self, url, key):
            pass

        def get(self, path, **kw):
            return get_result

    fake_setup._auto_load_owui_env = _auto_load_owui_env
    fake_setup.APIClient = _FakeAPIClient
    sys.modules["setup"] = fake_setup
    return fake_setup


def _with_setup_json(tmp: Path, write=True):
    if write:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "f1n2test-sonnet"}},
        }), encoding="utf-8")


def test_501_is_now_sentinel_not_plain_none():
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-n2-501-"))
    saved_setup = sys.modules.get("setup")
    saved_env = dict(module.os.environ)
    try:
        _with_setup_json(tmp)
        module.os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        module.os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        _install_fake_setup_module(get_result=(501, b""))
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "f1n2test-sonnet", sl_model
        assert kb_id == GM_ROUTE_KB_UNVERIFIED, (
            f"501 haette wie jeder andere Nicht-200-Code den Sentinel liefern muessen, war {kb_id!r}"
        )
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        module.os.environ.clear()
        module.os.environ.update(saved_env)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_missing_setup_json_is_sentinel_and_blocks_productive_transport():
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-n2-noconfig-"))
    try:
        # bewusst KEIN setup.json geschrieben
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model is None, sl_model
        assert kb_id == GM_ROUTE_KB_UNVERIFIED, kb_id

        # Factory-KONSTRUKTION selbst wirft nicht (lokales Menue bleibt
        # bedienbar) -- erst der tatsaechliche Transportbau (factory(...)).
        factory = default_gm_transport_factory(tmp, _REPO_ROOT, sl_model=sl_model, kb_id=kb_id)
        raised = False
        try:
            factory("table-1")
        except RuntimeError as exc:
            raised = True
            assert "nicht verlaesslich aufgeloest" in str(exc), str(exc)
        assert raised, "produktiver Transportbau ohne Konfig haette sichtbar ablehnen muessen"
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_missing_preset_id_is_sentinel():
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-n2-nopreset-"))
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {}},  # keine preset_id
        }), encoding="utf-8")
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model is None, sl_model
        assert kb_id == GM_ROUTE_KB_UNVERIFIED, kb_id
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_positive_path_unchanged():
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-n2-positive-"))
    saved_setup = sys.modules.get("setup")
    saved_env = dict(module.os.environ)
    try:
        _with_setup_json(tmp)
        module.os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        module.os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        fake_preset = {"meta": {"knowledge": [{"id": "kb-fresh-n2", "name": "x"}]}}
        _install_fake_setup_module(get_result=(200, fake_preset))
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "f1n2test-sonnet", sl_model
        assert kb_id == "kb-fresh-n2", kb_id
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        module.os.environ.clear()
        module.os.environ.update(saved_env)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


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
