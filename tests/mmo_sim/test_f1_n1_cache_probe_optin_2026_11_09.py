#!/usr/bin/env python3
"""tests/mmo_sim/test_f1_n1_cache_probe_optin_2026_11_09.py — Zero-POST-Nachweis
für ZR-MINT-SPIELSTART-FEINSCHLIFF F1-N1 WP2 (PF2).

Vorher führte `scripts/setup.py:run_install_litellm` nach dem Healthcheck
BEDINGUNGSLOS einen 2-Call-Cache-Test aus: zwei echte, kostenpflichtige
`POST /v1/chat/completions` gegen OpenRouter. Aufruf im Normalpfad über
`launcher.py:action_install` (Menü [1]), ohne dass der Nutzer das irgendwo
explizit bestätigt. Fix: der Test läuft jetzt nur noch hinter einer
expliziten, kostenbenannten Wahl (`opts["cache_probe"]` / CLI `--cache-probe`
/ `ZEITRISS_LITELLM_CACHE_PROBE=1`), Default AUS.

Dieser Test treibt `run_install_litellm` komplett End-to-End (über einen
Transport-Spy auf `urllib.request.urlopen` + einen `subprocess.run`-Double
für Docker), gegen eine isolierte Fake-Repo-Struktur in einem Tempverzeichnis
(NICHT das echte `scripts/litellm/.env` — keine Gefahr für echte Secrets),
und zählt die tatsächlich ausgelösten `POST /v1/chat/completions`-Aufrufe:

  1. Default (kein `opts`, keine Env) → 0 POSTs.
  2. `opts={"cache_probe": True}` → ≥1 POST.
  3. `ZEITRISS_LITELLM_CACHE_PROBE=1` (ohne `opts`-Flag) → ≥1 POST.

Double-Grenze (A4, offen gelegt): `subprocess.run` (Docker) und
`urllib.request.urlopen` (HTTP) sind vollständig gedoubelt — kein echter
Docker-Daemon, kein echtes Netzwerk, kein echter OpenRouter-Call. Der
OpenWebUI-Auto-Wire-Zweig (Schritt 8+9) bleibt unausgeführt, weil
`OPENWEBUI_API_KEY` bewusst leer gehalten wird (und `_auto_load_owui_env`
gedoubelt ist) — dieser Test beweist NUR das Cache-Probe-Gating, nicht den
Auto-Wire-Pfad (den deckt WP1c/WP1d ab).

Pure Python, nur `assert`, echter Exitcode, kein Docker/Netzwerk."""
from __future__ import annotations

import importlib.util
import os
import shutil
import tempfile
import traceback
import types
import unittest.mock as mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SETUP_PY = _REPO_ROOT / "scripts" / "setup.py"

_spec = importlib.util.spec_from_file_location(
    "f1_n1_cache_probe_setup_under_test", _SETUP_PY,
)
setup_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_module)


def _make_fake_repo() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="f1-n1-cache-probe-"))
    lite_dir = tmp / "scripts" / "litellm"
    lite_dir.mkdir(parents=True)
    (lite_dir / "docker-compose.litellm.yml").write_text("services: {}\n", encoding="utf-8")
    (lite_dir / ".env.example").write_text("OPENROUTER_API_KEY=sk-or-v1-REPLACE\n", encoding="utf-8")
    return tmp


def _fake_subprocess_run(cmd, *a, **kw):
    # Docker ist komplett gedoubelt: "docker compose version" (check=True)
    # und "docker compose ... up -d" liefern beide einen Erfolg zurück,
    # ohne je `docker` auf dem Host anzufassen.
    return types.SimpleNamespace(returncode=0, stdout="", stderr="")


class _FakeResp:
    def __init__(self, status=200, body=b"{}"):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


def _make_urlopen_spy(post_calls: list):
    def _urlopen(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        method = req.get_method() if hasattr(req, "get_method") else "GET"
        if method == "POST" and "/v1/chat/completions" in url:
            post_calls.append(url)
            body = (
                b'{"usage": {"prompt_tokens_details": {"cached_tokens": 5}}}'
            )
            return _FakeResp(200, body)
        # Health-Check (GET .../health/liveness) -- sofort gesund, kein
        # Retry-Loop nötig.
        return _FakeResp(200, b'{"status":"healthy"}')
    return _urlopen


def _run_install_litellm_isolated(opts):
    """Führt `run_install_litellm` gegen eine Fake-Repo-Struktur, zählt
    POSTs zu /v1/chat/completions. Gibt (post_count, tmp_repo) zurück."""
    tmp_repo = _make_fake_repo()
    cfg = {"project": "f1n1test"}
    post_calls: list = []

    saved_or = os.environ.get("OPENROUTER_API_KEY")
    saved_owui = os.environ.get("OPENWEBUI_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-fake-test-key-not-real"
    os.environ.pop("OPENWEBUI_API_KEY", None)

    try:
        with mock.patch.object(setup_module.subprocess, "run", side_effect=_fake_subprocess_run), \
             mock.patch.object(setup_module.urllib.request, "urlopen", side_effect=_make_urlopen_spy(post_calls)), \
             mock.patch.object(setup_module.time, "sleep", return_value=None), \
             mock.patch.object(setup_module, "_auto_load_owui_env", return_value=False):
            setup_module.run_install_litellm(tmp_repo, cfg, opts=opts)
    finally:
        if saved_or is None:
            os.environ.pop("OPENROUTER_API_KEY", None)
        else:
            os.environ["OPENROUTER_API_KEY"] = saved_or
        if saved_owui is None:
            os.environ.pop("OPENWEBUI_API_KEY", None)
        else:
            os.environ["OPENWEBUI_API_KEY"] = saved_owui
        shutil.rmtree(tmp_repo, ignore_errors=True)

    return len(post_calls)


def test_default_path_sends_zero_chat_completion_posts():
    count = _run_install_litellm_isolated(opts=None)
    assert count == 0, f"Default-Pfad haette 0 POST /v1/chat/completions erzeugen duerfen, waren {count}"


def test_cache_probe_opt_sends_at_least_one_post():
    count = _run_install_litellm_isolated(opts={"cache_probe": True})
    assert count >= 1, f"opts['cache_probe']=True haette mindestens einen POST ausloesen muessen, waren {count}"


def test_cache_probe_env_var_sends_at_least_one_post():
    saved_env = os.environ.get("ZEITRISS_LITELLM_CACHE_PROBE")
    os.environ["ZEITRISS_LITELLM_CACHE_PROBE"] = "1"
    try:
        count = _run_install_litellm_isolated(opts=None)
    finally:
        if saved_env is None:
            os.environ.pop("ZEITRISS_LITELLM_CACHE_PROBE", None)
        else:
            os.environ["ZEITRISS_LITELLM_CACHE_PROBE"] = saved_env
    assert count >= 1, f"ZEITRISS_LITELLM_CACHE_PROBE=1 haette mindestens einen POST ausloesen muessen, waren {count}"


def test_cache_probe_requested_helper_precedence():
    """Direkter Unit-Test des Gating-Helpers: opts-Flag UND Env schalten ein,
    beides fehlend -> aus."""
    assert setup_module._cache_probe_requested({}) is False
    assert setup_module._cache_probe_requested({"cache_probe": True}) is True
    assert setup_module._cache_probe_requested({"cache_probe": False}) is False
    saved = os.environ.get("ZEITRISS_LITELLM_CACHE_PROBE")
    try:
        os.environ["ZEITRISS_LITELLM_CACHE_PROBE"] = "1"
        assert setup_module._cache_probe_requested({}) is True
        os.environ["ZEITRISS_LITELLM_CACHE_PROBE"] = "0"
        assert setup_module._cache_probe_requested({}) is False
    finally:
        if saved is None:
            os.environ.pop("ZEITRISS_LITELLM_CACHE_PROBE", None)
        else:
            os.environ["ZEITRISS_LITELLM_CACHE_PROBE"] = saved


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
