#!/usr/bin/env python3
"""tests/mmo_sim/test_local_tokenhost_routing_2026_11_14.py — ZR-LOCAL-TOKENHOST-L1,
Offline-Abnahmen O2 (echte Transportfelder) + O3 (Host-/Backendkontext,
Fehler, Eindeutigkeit).

Belegt gegen echte Produktfunktionen:
  - `scripts/setup.py:_ensure_owui_local_connection` / `_verify_owui_connection_route`
    (letztere ist der BESTEHENDE nichtgenerative Verify-Vertrag, hier fuer den
    lokalen Pfad wiederverwendet statt verdoppelt) / `local_payload_overrides`
  - `mmo_sim/adapters/persona_api.py:PersonaApiDriver` (realer HTTP-Request)
  - `mmo_sim/adapters/gm_owui.py:GmOwuiTransport` + `agent_mp/sl_client.py`
    (realer HTTP-Request ueber `owui_client.OWUIChat`)

IO ausschliesslich an der urllib-Transportgrenze kontrolliert (`urllib.
request.urlopen` monkeygepatcht) -- kein echtes Netzwerk, kein Docker, keine
echte Modellantwort. Fixtureadressen/Keys sind erkennbar unecht (04).
`APIClient.test_model` wird als Fallenstelle instrumentiert (muss 0 bleiben)."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
import unittest.mock as mock
import urllib.error
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
_SETUP_PY = _SCRIPTS_DIR / "setup.py"
_LOCAL_PROFILE_PY = _SCRIPTS_DIR / "local_model_profile.py"
_SL_CLIENT_PY = _REPO_ROOT / "internal" / "qa" / "harness" / "agent_mp" / "sl_client.py"

# Immer (nicht nur bei Abwesenheit) an Position 0 setzen: ein anderes, in
# derselben `unittest discover`-Session VORHER geladenes Testmodul kann
# `scripts/` bereits vor den Repo-Root geschoben haben (`setup.py` fuegt
# sich selbst via `sys.path.insert(0, ...)` ein, s. dortiger Kommentar) --
# dann wuerde ein simples "falls nicht enthalten" den Repo-Root an seiner
# alten (hinteren) Position belassen und `import mmo_sim` faelschlich auf
# das gleichnamige `scripts/mmo_sim.py`-Shim statt des echten Pakets treffen.
sys.path.insert(0, str(_REPO_ROOT))

# WICHTIG: `mmo_sim` (das Paket an REPO_ROOT) muss VOR jedem Laden von
# `setup.py` importiert/gecacht werden -- `setup.py` fuegt sich selbst
# `scripts/` an sys.path[0] an (fuer `import local_model_profile`), was
# einen SPAETEREN frischen `import mmo_sim` sonst auf das gleichnamige
# Launcher-Shim `scripts/mmo_sim.py` statt des echten Pakets treffen liesse
# ("mmo_sim is not a package"). Einmal in sys.modules gecacht, ist die
# spaetere sys.path-Reihenfolge fuer diese Importe irrelevant.
from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver  # noqa: E402
from mmo_sim.adapters.gm_owui import GmOwuiTransport  # noqa: E402
from mmo_sim.adapters.base import ProviderAuthError, ProviderQuotaError, ProviderUnavailableError  # noqa: E402


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


lmp = _load("o2_local_model_profile_under_test", _LOCAL_PROFILE_PY)
setup_mod = _load("o2_setup_under_test", _SETUP_PY)

FAKE_OWUI_URL = "http://127.0.0.1:18080"
FAKE_OWUI_KEY = "owui-fake-key-not-secret"
FAKE_LOCAL_BASE = "http://127.0.0.1:18001/v1"
FAKE_LOCAL_MODEL = "nemotron-3-super"
FAKE_LOCAL_TOKEN = "test-local-token-not-secret"
FAKE_PRESET_ID = "zeitriss-sonnet"
FAKE_KB_ID = "9ad88aff-aaaa-bbbb-cccc-fakekbid0001"


def _profile(**overrides) -> "lmp.LocalModelProfile":
    base = dict(
        base_url=FAKE_LOCAL_BASE, model=FAKE_LOCAL_MODEL, api_key=FAKE_LOCAL_TOKEN,
        owui_base_url=None, gm_max_tokens=4096, persona_max_tokens=400,
    )
    base.update(overrides)
    return lmp.LocalModelProfile(**base)


class _FakeResponse:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _UrlopenScript:
    """Skriptierbarer `urllib.request.urlopen`-Double: liefert pro Aufruf
    die naechste vorbereitete Antwort/Exception, zeichnet jeden Request
    (url/method/headers/body) auf."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def __call__(self, req, timeout=None, context=None):
        body = req.data
        try:
            parsed_body = json.loads(body) if body else None
        except (json.JSONDecodeError, TypeError):
            parsed_body = body
        self.calls.append({
            "url": req.full_url, "method": req.get_method(),
            "headers": dict(req.headers), "body": parsed_body,
        })
        if not self._responses:
            raise AssertionError(f"_UrlopenScript: keine weitere Antwort fuer Aufruf #{len(self.calls)} ({req.full_url})")
        nxt = self._responses.pop(0)
        if isinstance(nxt, Exception):
            raise nxt
        status, payload = nxt
        return _FakeResponse(status, json.dumps(payload).encode("utf-8"))


class LocalTokenhostRoutingTests(unittest.TestCase):
    def setUp(self):
        self._tmp_dirs: list[Path] = []
        self._env_backup = dict(os.environ)

    def tearDown(self):
        for d in self._tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        os.environ.clear()
        os.environ.update(self._env_backup)

    def _tmp_dir(self, prefix: str) -> Path:
        d = Path(tempfile.mkdtemp(prefix=f"o2-{prefix}-"))
        self._tmp_dirs.append(d)
        return d

    # ─── local_payload_overrides: keine Cloudvererbung ──────────────────

    def test_local_payload_overrides_gm_and_persona_no_cloud_inheritance(self):
        profile = _profile()
        gm = setup_mod.local_payload_overrides(profile, role="gm")
        persona = setup_mod.local_payload_overrides(profile, role="persona")
        self.assertEqual(gm["max_tokens"], 4096)
        self.assertEqual(persona["max_tokens"], 400)
        for payload in (gm, persona):
            self.assertNotIn("reasoning_effort", payload)
            self.assertNotIn("vision", payload)
            self.assertNotIn(64000, payload.values())
            self.assertNotIn(16000, payload.values())

    # ─── O2: _ensure_owui_local_connection -- reale Mutationsfelder ──────

    def test_ensure_local_connection_creates_with_separate_local_token(self):
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [], "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {}}),
            (200, {}),
            # N1-03: Readback NACH dem Update -- bestaetigt exakt URL+Token+Modell,
            # statt dem POST-Echo blind zu vertrauen.
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": {"0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL]}}}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertTrue(ok, msg)
        self.assertEqual(len(script.calls), 3)
        get_call, post_call, reread_call = script.calls
        self.assertEqual(get_call["url"], f"{FAKE_OWUI_URL}/openai/config")
        self.assertEqual(reread_call["url"], f"{FAKE_OWUI_URL}/openai/config")
        self.assertEqual(reread_call["method"], "GET")
        self.assertEqual(get_call["headers"]["Authorization"], f"Bearer {FAKE_OWUI_KEY}")
        post_body = post_call["body"]
        self.assertIn(FAKE_LOCAL_BASE, post_body["OPENAI_API_BASE_URLS"])
        idx = post_body["OPENAI_API_BASE_URLS"].index(FAKE_LOCAL_BASE)
        self.assertEqual(post_body["OPENAI_API_KEYS"][idx], FAKE_LOCAL_TOKEN)
        self.assertNotEqual(post_body["OPENAI_API_KEYS"][idx], FAKE_OWUI_KEY)
        self.assertIn(FAKE_LOCAL_MODEL, post_body["OPENAI_API_CONFIGS"][str(idx)]["model_ids"])

    def test_ensure_local_connection_idempotent_no_rewrite_when_matching(self):
        existing_cfg = {
            "0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL], "tags": ["local"],
                  "prefix_id": "", "connection_type": "external", "auth_type": "bearer"}
        }
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": existing_cfg}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertTrue(ok, msg)
        self.assertEqual(len(script.calls), 1, "bereits identischer Zustand darf keinen POST ausloesen (Idempotenz).")

    def test_ensure_local_connection_never_touches_docker_network_helpers(self):
        """02: KEIN Aufruf der Docker-Netz-Mutation im lokalen Zweig."""
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [], "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {}}),
            (200, {}),
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": {"0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL]}}}),
        ])
        with mock.patch("urllib.request.urlopen", script), \
             mock.patch.object(setup_mod, "_ensure_owui_on_litellm_network",
                                side_effect=AssertionError("Docker-Netz-Mutation darf im lokalen Zweig nicht laufen")), \
             mock.patch.object(setup_mod, "_owui_container_network_mode",
                                side_effect=AssertionError("Netzwerkkontext-Ermittlung gehoert zum Cloud/LiteLLM-Pfad")):
            ok, _msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertTrue(ok)

    # ─── O3: nichtgenerativer Verify -- True/False/None, 401/403/404/501/Timeout ──

    def test_verify_local_route_true_when_model_present(self):
        script = _UrlopenScript([(200, {"data": [{"id": FAKE_LOCAL_MODEL}, {"id": "other-model"}]})])
        with mock.patch("urllib.request.urlopen", script):
            result = setup_mod._verify_owui_connection_route(
                FAKE_OWUI_URL, FAKE_OWUI_KEY, FAKE_LOCAL_BASE, FAKE_LOCAL_TOKEN, FAKE_LOCAL_MODEL,
            )
        self.assertIs(result, True)
        verify_call = script.calls[0]
        self.assertEqual(verify_call["url"], f"{FAKE_OWUI_URL}/openai/verify")
        self.assertEqual(verify_call["body"]["url"], FAKE_LOCAL_BASE)
        self.assertEqual(verify_call["body"]["key"], FAKE_LOCAL_TOKEN)

    def test_verify_local_route_false_when_model_missing_or_empty_list(self):
        for payload in ({"data": [{"id": "some-other-model"}]}, {"data": []}, []):
            script = _UrlopenScript([(200, payload)])
            with mock.patch("urllib.request.urlopen", script):
                result = setup_mod._verify_owui_connection_route(
                    FAKE_OWUI_URL, FAKE_OWUI_KEY, FAKE_LOCAL_BASE, FAKE_LOCAL_TOKEN, FAKE_LOCAL_MODEL,
                )
            self.assertIs(result, False, f"payload={payload!r}")

    def test_verify_local_route_false_on_401_403_404_501(self):
        for code in (401, 403, 404, 501):
            exc = urllib.error.HTTPError(f"{FAKE_OWUI_URL}/openai/verify", code, "err", {}, None)
            exc.read = lambda: b"{}"
            script = _UrlopenScript([exc])
            with mock.patch("urllib.request.urlopen", script):
                result = setup_mod._verify_owui_connection_route(
                    FAKE_OWUI_URL, FAKE_OWUI_KEY, FAKE_LOCAL_BASE, FAKE_LOCAL_TOKEN, FAKE_LOCAL_MODEL,
                )
            self.assertIs(result, False, f"HTTP {code} sollte bestaetigt negativ sein")

    def test_verify_local_route_none_on_timeout_and_malformed_body(self):
        timeout_script = _UrlopenScript([urllib.error.URLError("timed out")])
        with mock.patch("urllib.request.urlopen", timeout_script):
            result = setup_mod._verify_owui_connection_route(
                FAKE_OWUI_URL, FAKE_OWUI_KEY, FAKE_LOCAL_BASE, FAKE_LOCAL_TOKEN, FAKE_LOCAL_MODEL,
            )
        self.assertIsNone(result, "Timeout ist 'nicht pruefbar', NICHT 'bestaetigt nicht verbunden'.")

        malformed_script = _UrlopenScript([(200, {"unexpected_shape": True})])
        with mock.patch("urllib.request.urlopen", malformed_script):
            result2 = setup_mod._verify_owui_connection_route(
                FAKE_OWUI_URL, FAKE_OWUI_KEY, FAKE_LOCAL_BASE, FAKE_LOCAL_TOKEN, FAKE_LOCAL_MODEL,
            )
        self.assertIsNone(result2)

    def test_hold_on_ambiguous_duplicate_connection_same_base_url_different_key(self):
        """O3/N1-03: mehrdeutige/gleichnamige Connections halten -- zwei
        Eintraege mit DERSELBEN Ziel-URL aber unterschiedlichem Key sind
        nicht sicher eindeutig zuordenbar. `_ensure_owui_local_connection`
        MUSS das echt erkennen und VOR jeder Mutation halten -- vorher pruefte
        dieser Test nur die rohe JSON-Antwort (2 Eintraege), nie den
        tatsaechlichen Entscheidungsweg."""
        dup_cfg = {
            "0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL], "tags": ["local"]},
            "1": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL], "tags": ["local"]},
        }
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE, FAKE_LOCAL_BASE],
                   "OPENAI_API_KEYS": ["old-key-a", "old-key-b"], "OPENAI_API_CONFIGS": dup_cfg}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertFalse(ok, "doppelte Ziel-URL mit widersprechenden Keys muss halten, nicht den ersten Treffer nehmen.")
        self.assertIn("ehrdeutig", msg)
        # Kein POST -- der Halt geschieht VOR jeder Mutation (nur der eine GET).
        self.assertEqual(len(script.calls), 1)
        self.assertEqual(script.calls[0]["method"], "GET")

    def test_hold_on_ambiguous_same_model_pinned_at_other_connection(self):
        """N1-03: dieselbe served-model-ID bereits an einer ANDEREN wirksamen
        Connection (andere URL) gepinnt -- muss ebenfalls halten statt das
        Modell blind an eine zweite Connection zu haengen."""
        other_cfg = {
            "0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL], "tags": ["local"]},
        }
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": ["http://127.0.0.1:19999/v1"],
                   "OPENAI_API_KEYS": ["other-key"], "OPENAI_API_CONFIGS": other_cfg}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertFalse(ok, "gleiche Modell-ID an anderer wirksamer Connection muss halten.")
        self.assertIn("ehrdeutig", msg)
        self.assertEqual(len(script.calls), 1)

    # ─── O2: completion-counter=0 bei Setup/Connectioncheck ─────────────

    def test_no_hidden_completion_during_connection_and_verify(self):
        calls = {"test_model": 0}

        def _trap(self_, *_a, **_k):
            calls["test_model"] += 1
            raise AssertionError("APIClient.test_model darf im lokalen Setup-/Anschlussweg nicht laufen")

        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [], "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {}}),
            (200, {}),
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": {"0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL]}}}),
            (200, {"data": [{"id": FAKE_LOCAL_MODEL}]}),
        ])
        with mock.patch("urllib.request.urlopen", script), \
             mock.patch.object(setup_mod.APIClient, "test_model", _trap):
            ok, _msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
            self.assertTrue(ok)
            verified = setup_mod._verify_owui_connection_route(
                FAKE_OWUI_URL, FAKE_OWUI_KEY, FAKE_LOCAL_BASE, FAKE_LOCAL_TOKEN, FAKE_LOCAL_MODEL,
            )
        self.assertIs(verified, True)
        self.assertEqual(calls["test_model"], 0)
        for call in script.calls:
            self.assertNotIn("/chat/completions", call["url"], "kein verstecktes Completion-POST.")

    # ─── O2: Persona -- realer Request auf lokaler Basis+served-model-ID ──

    def test_persona_api_driver_real_request_fields_local_profile(self):
        script = _UrlopenScript([
            (200, {"choices": [{"message": {"content": "ok"}}], "usage": {"prompt_tokens": 7, "completion_tokens": 3}}),
        ])
        config = PersonaApiConfig(
            base_url=FAKE_LOCAL_BASE, api_key=FAKE_LOCAL_TOKEN, model=FAKE_LOCAL_MODEL,
            max_tokens=400, is_dollar_billed=False,
        )
        driver = PersonaApiDriver(config, "persona_test")
        self.assertFalse(driver.is_dollar_billed)
        with mock.patch("urllib.request.urlopen", script):
            decision = driver.decide({"system": "Du bist eine Figur.", "user": "Hallo"})
        self.assertEqual(decision.text, "ok")
        self.assertEqual(len(script.calls), 1)
        call = script.calls[0]
        self.assertEqual(call["url"], f"{FAKE_LOCAL_BASE}/chat/completions")
        self.assertEqual(call["headers"]["Authorization"], f"Bearer {FAKE_LOCAL_TOKEN}")
        self.assertEqual(call["body"]["model"], FAKE_LOCAL_MODEL)
        self.assertEqual(call["body"]["max_tokens"], 400)
        self.assertNotIn("reasoning_effort", call["body"])
        self.assertNotIn("files", call["body"], "Persona bekommt keinen GM-KB-Kontext.")

    def test_persona_api_driver_auth_and_timeout_errors_no_second_send_no_cloud_fallback(self):
        auth_exc = urllib.error.HTTPError(FAKE_LOCAL_BASE + "/chat/completions", 401, "unauthorized", {}, None)
        auth_exc.read = lambda: b"{}"
        config = PersonaApiConfig(base_url=FAKE_LOCAL_BASE, api_key=FAKE_LOCAL_TOKEN, model=FAKE_LOCAL_MODEL)
        driver = PersonaApiDriver(config, "persona_auth")
        script = _UrlopenScript([auth_exc])
        with mock.patch("urllib.request.urlopen", script):
            with self.assertRaises(ProviderAuthError):
                driver.decide({"system": "s", "user": "u"})
        self.assertEqual(len(script.calls), 1, "genau EIN Versand -- kein automatischer Zweitversand.")

        timeout_exc = TimeoutError("timed out")
        driver2 = PersonaApiDriver(config, "persona_timeout")
        script2 = _UrlopenScript([timeout_exc])
        with mock.patch("urllib.request.urlopen", script2):
            with self.assertRaises(ProviderUnavailableError):
                driver2.decide({"system": "s", "user": "u"})
        self.assertEqual(len(script2.calls), 1)

    # ─── O2: GM -- realer Request auf Preset-ID + KB, getrennter Upstream ──

    def test_gm_owui_transport_real_request_fields_local_billing(self):
        run_dir = self._tmp_dir("gm-run")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        script = _UrlopenScript([
            (200, {"choices": [{"message": {"content": "Der Raum ist still."}}],
                   "usage": {"prompt_tokens": 20, "completion_tokens": 10}}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            transport = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="tisch-1",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
                gm_output_limit_tokens=4096, is_dollar_billed=False,
            )
            self.assertFalse(transport.is_dollar_billed)
            # Produktpfad (runtime.py:submit): `output_limit_tokens` wird
            # vom AUFRUFER aus `getattr(gm_transport, 'output_limit_tokens')`
            # gelesen und explizit in `.turn()` durchgereicht -- nicht
            # implizit innerhalb von `GmOwuiTransport` angewendet.
            self.assertEqual(transport.output_limit_tokens, 4096)
            result = transport.turn(1, "Die Gruppe betritt den Raum.", output_limit_tokens=transport.output_limit_tokens)
        self.assertEqual(result["content"], "Der Raum ist still.")
        self.assertEqual(len(script.calls), 1)
        call = script.calls[0]
        self.assertEqual(call["url"], f"{FAKE_OWUI_URL}/api/chat/completions")
        self.assertEqual(call["headers"]["Authorization"], f"Bearer {FAKE_OWUI_KEY}")
        self.assertEqual(call["body"]["model"], FAKE_PRESET_ID, "GM-Request.model bleibt die Preset-ID.")
        self.assertEqual(call["body"]["files"], [{"type": "collection", "id": FAKE_KB_ID}])
        self.assertEqual(call["body"]["max_tokens"], 4096)

        summary = transport.usage_summary()
        self.assertFalse(summary["dollar_billed"])
        self.assertEqual(summary["pricing"], "local_unpriced")
        # N1-04: lokal/unpriced ist ausdruecklich UNKNOWN (`None`/JSON-null),
        # KEINE gemessene Nullkostenrechnung -- vorher faelschlich `0.0`.
        self.assertIsNone(summary["cum_cost_est_usd"])

        jsonl_path = run_dir / "gm_sessions" / "tisch-1" / "sl_history.jsonl"
        self.assertTrue(jsonl_path.is_file())
        record = json.loads(jsonl_path.read_text(encoding="utf-8").splitlines()[-1])
        self.assertIsNone(record["cost_usd"])
        self.assertEqual(record["pricing"], "local_unpriced")
        self.assertFalse(record["dollar_billed"])
        self.assertEqual(record["prompt_tokens"], 20)
        self.assertEqual(record["completion_tokens"], 10, "echte Tokenusage bleibt erhalten.")

    def test_gm_owui_transport_auth_error_no_cloud_fallback(self):
        run_dir = self._tmp_dir("gm-auth-run")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        auth_exc = urllib.error.HTTPError(FAKE_OWUI_URL + "/api/chat/completions", 403, "forbidden", {}, None)
        auth_exc.read = lambda: b"{}"
        script = _UrlopenScript([auth_exc, auth_exc, auth_exc])  # OWUIChat retried intern, max_retries steuerbar
        with mock.patch("urllib.request.urlopen", script):
            transport = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="tisch-auth",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
                gm_output_limit_tokens=4096, transport_max_retries=1,
                is_dollar_billed=False,
            )
            with self.assertRaises(Exception):
                transport.turn(1, "Text")
        # transport_max_retries=1: genau EIN physischer POST-Versuch (kein
        # automatischer Zweitversand durch den neuen Profilcode).
        self.assertEqual(len(script.calls), 1)


if __name__ == "__main__":
    unittest.main()
