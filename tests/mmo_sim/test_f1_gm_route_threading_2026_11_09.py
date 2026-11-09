#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_gm_route_threading_2026_11_09.py — Delta-Test für
F1-3 (03_F1_AUFTRAG.md §F1-3: "gespeicherte Werte müssen bei den
tatsächlich verwendeten GM-/Persona-Factories ankommen").

Vorher reichte `mmo_sim/adapters/factories.py:default_gm_transport_factory`
NIE ein `sl_model`/`kb_id` an `GmOwuiTransport` durch (obwohl dessen
Konstruktor beide Parameter bereits akzeptierte) — und
`scripts/mmo_sim.py:main()` ermittelte diese Werte gar nicht erst. Jede
frische `setup.py`-Installation legt aber eine NEUE Knowledge-Base mit
neuer ID an; ohne diesen Fix griffe das Terminalspiel immer auf die in
`agent_mp/sl_client.py` hartkodierte KB-ID einer alten Installation zurück.

Deckt zwei getrennte Stellen:
  (A) `factories.default_gm_transport_factory(..., sl_model=, kb_id=)`
      reicht beide Werte tatsächlich an den konstruierten Transport durch.
  (B) `scripts/mmo_sim.py:_resolve_active_gm_route()` ermittelt Preset-ID
      (aus `setup.json`) und KB-ID (live über den vorhandenen
      `setup.APIClient`) korrekt und bleibt fail-soft ohne Konfiguration.

Double-Grenzen (A4, offen gelegt):
  (A) `mmo_sim.adapters.gm_owui.GmOwuiTransport` wird durch ein Fake
      ersetzt, das nur die übergebenen Konstruktor-Kwargs aufzeichnet —
      kein echter `sl_client`-Import, kein HTTP, keine OWUI-Verbindung.
  (B) `setup` (scripts/setup.py) wird durch ein Fake-Modul in `sys.modules`
      ersetzt (eigenes `APIClient`, eigenes `_auto_load_owui_env`) — keine
      echte Netzwerk-/OWUI-Anbindung, reine Entscheidungslogik-Prüfung.

Pure Python, nur `assert`, echter Exitcode, temporäre Verzeichnisse."""
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

from mmo_sim.adapters.factories import default_gm_transport_factory  # noqa: E402
import mmo_sim.adapters.gm_owui as gm_owui_mod  # noqa: E402


def test_factory_forwards_sl_model_and_kb_id_to_transport():
    captured: dict = {}

    class _FakeTransport:
        def __init__(self, sl_client_path, run_dir, table_id=None,
                     sl_model=None, kb_id=None, **kw):
            captured["sl_model"] = sl_model
            captured["kb_id"] = kb_id
            captured["table_id"] = table_id

    real_transport = gm_owui_mod.GmOwuiTransport
    gm_owui_mod.GmOwuiTransport = _FakeTransport
    tmp = Path(tempfile.mkdtemp(prefix="f1-gm-route-"))
    try:
        factory = default_gm_transport_factory(
            tmp, _REPO_ROOT, sl_model="zeitriss-v426-uncut", kb_id="kb-fresh-123",
        )
        factory("table-1")
        assert captured["sl_model"] == "zeitriss-v426-uncut", captured
        assert captured["kb_id"] == "kb-fresh-123", captured
        assert captured["table_id"] == "table-1", captured
    finally:
        gm_owui_mod.GmOwuiTransport = real_transport
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_factory_without_sl_model_kb_id_keeps_old_default_none_behavior():
    """Regressionsschutz: ohne die neuen Kwargs (jeder bestehende Aufrufer,
    z.B. `mmo_sim/lab/cli.py`) bleiben beide Werte `None` -- `GmOwuiTransport`
    faellt dann weiterhin auf die `sl_client.py`-Altdefaults zurueck."""
    captured: dict = {"called": False}

    class _FakeTransport:
        def __init__(self, sl_client_path, run_dir, table_id=None,
                     sl_model=None, kb_id=None, **kw):
            captured["called"] = True
            captured["sl_model"] = sl_model
            captured["kb_id"] = kb_id

    real_transport = gm_owui_mod.GmOwuiTransport
    gm_owui_mod.GmOwuiTransport = _FakeTransport
    tmp = Path(tempfile.mkdtemp(prefix="f1-gm-route-"))
    try:
        factory = default_gm_transport_factory(tmp, _REPO_ROOT)  # alte 2-Arg-Form
        factory("table-1")
        assert captured["called"]
        assert captured["sl_model"] is None
        assert captured["kb_id"] is None
    finally:
        gm_owui_mod.GmOwuiTransport = real_transport
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def _load_mmo_sim_entrypoint():
    """Laedt `scripts/mmo_sim.py` per explizitem Dateipfad (identische
    Technik wie `scripts/mmo_sim_launcher_hook.py:launch()`) -- ein
    plattes `import mmo_sim` wuerde an das Paket `mmo_sim/` binden, nicht an
    den Shim, s. dessen eigener Kollisions-Docstring."""
    spec = importlib.util.spec_from_file_location(
        "f1_mmo_sim_entrypoint_under_test", _REPO_ROOT / "scripts" / "mmo_sim.py",
    )
    module = importlib.util.module_from_spec(spec)
    # F1-Critic-Fix: scripts/mmo_sim.py ruft beim Laden seinen venv-Bootstrap
    # (`ensure_running_in_project_venv`) auf -- ohne diesen Mock feuert der ein
    # echtes `os.execv`/`pip install` mitten im Test (per strace belegt), was
    # den Testprozess still neu startet (doppelte "OK"-Zeilen) und auf einem
    # frischen CI-Runner ohne `.venv` einen unentdeckten Netzwerkaufruf
    # ausloest. `sys.prefix` auf das erwartete `.venv` zeigen lassen ->
    # `already_in_venv()` == True -> Bootstrap ist No-Op (identische Technik
    # wie test_f1_venv_bootstrap_2026_11_09.py).
    with mock.patch.object(sys, "prefix", str(_REPO_ROOT / ".venv")):
        spec.loader.exec_module(module)
    return module


def _install_fake_setup_module(get_model_result):
    fake_setup = types.ModuleType("setup")
    fake_setup._auto_load_owui_env_calls = []

    def _auto_load_owui_env():
        fake_setup._auto_load_owui_env_calls.append(True)

    class _FakeAPIClient:
        def __init__(self, url, key):
            self.url = url
            self.key = key

        def get_model(self, model_id):
            return get_model_result

    fake_setup._auto_load_owui_env = _auto_load_owui_env
    fake_setup.APIClient = _FakeAPIClient
    sys.modules["setup"] = fake_setup
    return fake_setup


def test_resolve_active_gm_route_no_setup_json_is_fail_soft():
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-"))
    try:
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model is None and kb_id is None
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_active_gm_route_without_owui_key_returns_only_sl_model():
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-"))
    saved_setup = sys.modules.get("setup")
    saved_env = module.os.environ.pop("OPENWEBUI_API_KEY", None)
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "zeitriss-v426-uncut"}},
        }), encoding="utf-8")
        _install_fake_setup_module(get_model_result=None)
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "zeitriss-v426-uncut", sl_model
        assert kb_id is None, kb_id
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        if saved_env is not None:
            module.os.environ["OPENWEBUI_API_KEY"] = saved_env
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_active_gm_route_invalid_auth_is_fail_soft():
    """A4 (ungueltige-Auth/Route-Check): ein (simuliert) abgelaufener/
    falscher OWUI-Key fuehrt bei `APIClient.get_model` zu einem Fehler --
    `_resolve_active_gm_route` darf dabei NICHT crashen, sondern faellt auf
    `(sl_model, None)` zurueck (GmOwuiTransport nutzt dann die
    sl_client.py-Altdefaults statt eines abgebrochenen Terminalstarts)."""
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-auth-"))
    saved_setup = sys.modules.get("setup")
    saved_env = dict(module.os.environ)
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "zeitriss-v426-uncut"}},
        }), encoding="utf-8")
        module.os.environ["OPENWEBUI_API_KEY"] = "invalid-expired-key-not-a-secret"
        module.os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"

        fake_setup = types.ModuleType("setup")

        def _auto_load_owui_env():
            pass

        class _UnauthorizedAPIClient:
            def __init__(self, url, key):
                pass

            def get_model(self, model_id):
                raise RuntimeError("HTTP 401: invalid API key")

        fake_setup._auto_load_owui_env = _auto_load_owui_env
        fake_setup.APIClient = _UnauthorizedAPIClient
        sys.modules["setup"] = fake_setup

        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "zeitriss-v426-uncut", sl_model
        assert kb_id is None, kb_id
    finally:
        if saved_setup is not None:
            sys.modules["setup"] = saved_setup
        else:
            sys.modules.pop("setup", None)
        module.os.environ.clear()
        module.os.environ.update(saved_env)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_active_gm_route_with_owui_key_resolves_live_kb_id():
    module = _load_mmo_sim_entrypoint()
    tmp = Path(tempfile.mkdtemp(prefix="f1-resolve-route-"))
    saved_setup = sys.modules.get("setup")
    saved_env = dict(module.os.environ)
    try:
        (tmp / "setup.json").write_text(json.dumps({
            "default_variant": "sonnet",
            "variants": {"sonnet": {"preset_id": "zeitriss-v426-uncut"}},
        }), encoding="utf-8")
        module.os.environ["OPENWEBUI_API_KEY"] = "test-key-not-a-secret"
        module.os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        fake_preset = {"meta": {"knowledge": [{"id": "kb-fresh-456", "name": "x"}]}}
        _install_fake_setup_module(get_model_result=fake_preset)
        sl_model, kb_id = module._resolve_active_gm_route(tmp)
        assert sl_model == "zeitriss-v426-uncut", sl_model
        assert kb_id == "kb-fresh-456", kb_id
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
