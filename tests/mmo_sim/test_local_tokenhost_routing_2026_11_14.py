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
`APIClient.test_model` wird als Fallenstelle instrumentiert (muss 0 bleiben).

G4 (O3-C.C1, Nachzug 2026-11-16): `LocalTokenhostNegativeCallerTests` ergaenzt
die bestellte negative Caller-Batterie (401/403/404/501/Timeout/leerer
Body/falscher Body-falsche Modellliste/fehlendes Modell) an den WIRKLICHEN
lokalen Aufrufern `scripts/setup.py::run_setup` (`/openai/verify`) und
`scripts/launcher.py::_finish_installed_connection` (Connection+Rewire) --
nicht nur am direkt gerufenen Helper `_verify_owui_connection_route`."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
import unittest.mock as mock
import urllib.error
import urllib.parse
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
_SETUP_PY = _SCRIPTS_DIR / "setup.py"
_LAUNCHER_PY = _SCRIPTS_DIR / "launcher.py"
_LOCAL_PROFILE_PY = _SCRIPTS_DIR / "local_model_profile.py"
_SL_CLIENT_PY = _REPO_ROOT / "internal" / "qa" / "harness" / "agent_mp" / "sl_client.py"
_SUPPORT_SCRIPT = _HERE / "_local_tokenhost_support_2026_11_14.py"

# N4-N1: Fruehschutz MUSS installiert sein, BEVOR irgendein Produktmodul
# geladen wird -- hier insbesondere VOR dem `from mmo_sim.adapters...`-
# Import unten (identische frueh installierte Offlinehuelle wie in
# test_local_tokenhost_profile_2026_11_14.py, 04_OFFLINE_ABNAHME.md "C1").
# `bootstrap_isolation` ist prozessweit idempotent (EIN Audithook, EINE
# geteilte Allowlist) -- siehe Support-Moduldocstring.
import importlib.util as _importlib_util_bootstrap  # noqa: E402

_support_spec = _importlib_util_bootstrap.spec_from_file_location(
    "o2_local_tokenhost_support", _SUPPORT_SCRIPT
)
_support_mod = _importlib_util_bootstrap.module_from_spec(_support_spec)
sys.modules["o2_local_tokenhost_support"] = _support_mod
_support_spec.loader.exec_module(_support_mod)
# Weg 3 (Flo 2026-11-15): Prozessbruecke. Im geteilten unittest-Elternprozess
# bleibt der Import seiteneffektfrei (kein Guard, kein Produktimport, kein
# globaler Patch) und stellt nur die Bruecke bereit; der echte geschuetzte
# Koerper laeuft im frischen Interpreter (Standalone/run_all/Bundle/Kind).
_REAL_BODY = (__name__ == "__main__") or _support_mod.is_real_body_env()

if not _REAL_BODY:
    # Platzhalter fuer Produktsymbole, die in Klassenkoerpern ZUR IMPORTZEIT
    # ausgewertet werden (hier `factories_mod._LOCAL_TOKENHOST_RESOLVED_MARKER`
    # im Klassenattribut `_PERSONA_ENV_KEYS`). Im Elternprozess laufen diese
    # Klassen nie (die Bruecke delegiert an frische Kinder) -- das inerte
    # Double verhindert nur den NameError bei der Klassendefinition.
    factories_mod = lmp = setup_mod = launcher_mod = _support_mod.parent_mode_product_stub()
    load_tests = _support_mod.make_delegating_load_tests(
        __file__, "routing", min_domain_tests=35)

if _REAL_BODY:
    # Manche CPython-Builds suchen dieses unveraenderte oeffentliche CA-
    # Verzeichnis per Python-stat. Explizit dieselbe Trust-Quelle benennen
    # vermeidet den Fallback-Probe, ohne TLS oder IO-Rechte abzusenken.
    import ssl
    if hasattr(ssl.SSLContext, "_FALLBACK_CERT_DIR"):
        os.environ.setdefault("SSL_CERT_DIR", ssl.SSLContext._FALLBACK_CERT_DIR)
    EARLY_GUARD = _support_mod.self_bootstrap_isolation()

# Immer (nicht nur bei Abwesenheit) an Position 0 setzen: ein anderes, in
# derselben `unittest discover`-Session VORHER geladenes Testmodul kann
# `scripts/` bereits vor den Repo-Root geschoben haben (`setup.py` fuegt
# sich selbst via `sys.path.insert(0, ...)` ein, s. dortiger Kommentar) --
# dann wuerde ein simples "falls nicht enthalten" den Repo-Root an seiner
# alten (hinteren) Position belassen und `import mmo_sim` faelschlich auf
# das gleichnamige `scripts/mmo_sim.py`-Shim statt des echten Pakets treffen.
if _REAL_BODY:
    sys.path.insert(0, str(_REPO_ROOT))

# WICHTIG: `mmo_sim` (das Paket an REPO_ROOT) muss VOR jedem Laden von
# `setup.py` importiert/gecacht werden -- `setup.py` fuegt sich selbst
# `scripts/` an sys.path[0] an (fuer `import local_model_profile`), was
# einen SPAETEREN frischen `import mmo_sim` sonst auf das gleichnamige
# Launcher-Shim `scripts/mmo_sim.py` statt des echten Pakets treffen liesse
# ("mmo_sim is not a package"). Einmal in sys.modules gecacht, ist die
# spaetere sys.path-Reihenfolge fuer diese Importe irrelevant.
if _REAL_BODY:
    from mmo_sim.adapters.persona_api import (  # noqa: E402
        PersonaApiConfig, PersonaApiDriver, _validate_persona_max_tokens,
    )
    from mmo_sim.adapters.gm_owui import GmOwuiTransport  # noqa: E402
    from mmo_sim.adapters.base import ProviderAuthError, ProviderQuotaError, ProviderUnavailableError  # noqa: E402
    from mmo_sim.adapters import factories as factories_mod  # noqa: E402


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


if _REAL_BODY:
    lmp = _load("o2_local_model_profile_under_test", _LOCAL_PROFILE_PY)
    setup_mod = _load("o2_setup_under_test", _SETUP_PY)
    launcher_mod = _load("o2_launcher_under_test", _LAUNCHER_PY)

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


class _RawBytes:
    """G4 (O3-C.C1, 01_GENERALREVIEW.md §5): enger Rohbytes-Zweig fuer den
    vorhandenen 'leerer Body'-Fall -- `(200, None)` liefert bisher
    `json.dumps(None)` == `b"null"` (kein echtes Leerbyte). `(200,
    _RawBytes(b""))` liefert am selben Connection-GET tatsaechlich `b""`
    an `_FakeResponse.read()`, ohne den JSON-Serialisierungsschritt zu
    durchlaufen. Der bisherige `null`-Fall bleibt als zusaetzlicher
    gueltiger malformed/no-object-Beleg unveraendert erhalten."""

    def __init__(self, data: bytes):
        self.data = bytes(data)


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
        if isinstance(payload, _RawBytes):
            response_body = payload.data
        else:
            response_body = json.dumps(payload).encode("utf-8")
        return _FakeResponse(status, response_body)


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

    # ─── I1/I5: Guardintegration -- Export, keine unerwarteten Blocks ────

    def test_guard_export_status_has_no_secrets_and_zero_unexpected_blocks(self):
        """I1.4/I5.1: der in diesem Prozess VOR jedem Produktimport
        installierte Fruehschutz bleibt waehrend des normalen
        Testbetriebs dieser Datei frei von unerwarteten Blocks und
        exportiert ausschliesslich Pfadklassen/Zaehler, nie Secretwerte
        (02_N4N1_ARBEITSAUFTRAG.md B/04_OFFLINE_ABNAHME.md)."""
        status = EARLY_GUARD.export_status()
        self.assertEqual(status["counters"]["unexpected_blocked"], 0)
        dump = json.dumps(status)
        self.assertNotIn(FAKE_LOCAL_TOKEN, dump)
        self.assertNotIn(FAKE_OWUI_KEY, dump)
        export_path = self._tmp_dir("guard-export") / "guard-state.json"
        exported = EARLY_GUARD.export_guard_state(export_path)
        self.assertEqual(exported["counters"]["unexpected_blocked"], 0)
        self.assertTrue(export_path.is_file())
        self.assertNotIn(FAKE_LOCAL_TOKEN, export_path.read_text(encoding="utf-8"))

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
                   "OPENAI_API_CONFIGS": {"0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL]}},
                   "ENABLE_OPENAI_API": True}),
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

    def test_ensure_local_connection_foreign_connection_byte_identical_before_after(self):
        """O3-B.B3: eine ZUSAETZLICHE fremde Connection (andere URL,
        eigener Key/Pin/Tags) bleibt VOR/NACH dem Schreiben der eigenen
        lokalen Connection bytegleich -- nur die bewusst eigene Verbindung
        wird geaendert, kein Beruehren/Normalisieren fremder Eintraege."""
        foreign_cfg = {
            "enable": True, "model_ids": ["foreign-model-untouched"], "tags": ["foreign", "custom"],
            "prefix_id": "foreign-prefix-", "connection_type": "external", "auth_type": "bearer",
            "some_foreign_extra_field": "must-survive-untouched",
        }
        foreign_url = "http://127.0.0.1:19777/v1"
        foreign_key = "foreign-key-not-secret"
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [foreign_url], "OPENAI_API_KEYS": [foreign_key],
                   "OPENAI_API_CONFIGS": {"0": dict(foreign_cfg)}}),
            (200, {}),
            (200, {"OPENAI_API_BASE_URLS": [foreign_url, FAKE_LOCAL_BASE],
                   "OPENAI_API_KEYS": [foreign_key, FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": {
                       "0": dict(foreign_cfg),
                       "1": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL]},
                   },
                   "ENABLE_OPENAI_API": True}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertTrue(ok, msg)
        post_body = script.calls[1]["body"]
        self.assertEqual(post_body["OPENAI_API_BASE_URLS"][0], foreign_url, "fremde URL bytegleich.")
        self.assertEqual(post_body["OPENAI_API_KEYS"][0], foreign_key, "fremder Key bytegleich.")
        self.assertEqual(
            post_body["OPENAI_API_CONFIGS"]["0"], foreign_cfg,
            "fremder Connection-Eintrag (inkl. unbekanntem Feld) bytegleich im gesendeten Payload.",
        )
        reread_call = script.calls[2]
        self.assertEqual(reread_call["method"], "GET")

    def test_ensure_local_connection_idempotent_no_rewrite_when_matching(self):
        existing_cfg = {
            "0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL], "tags": ["local"],
                  "prefix_id": "", "connection_type": "external", "auth_type": "bearer"}
        }
        script = _UrlopenScript([
            # O3-B.B1: ein wirklich identischer Zustand schliesst den
            # GLOBALEN Schalter ein -- ohne `ENABLE_OPENAI_API: True` hier
            # waere dies kein echtes Idempotenzbeispiel mehr (s. Testfall
            # unten fuer den global deaktivierten Gegenfall).
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": existing_cfg, "ENABLE_OPENAI_API": True}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertTrue(ok, msg)
        self.assertEqual(len(script.calls), 1, "bereits identischer Zustand darf keinen POST ausloesen (Idempotenz).")

    def test_ensure_local_connection_globally_disabled_is_not_confirmed_as_idempotent(self):
        """O3-B.B1 (RELEASE-CASES.json): eine ansonsten exakt passende
        bestehende Connection (Key/Pin/per-Connection-enable stimmen) darf
        bei global deaktiviertem `ENABLE_OPENAI_API` NICHT als "bereits
        korrekt, kein Update noetig" bestaetigt werden -- vorher pruefte die
        Idempotenzkurzschluss-Pruefung NUR die eigene Connection, nie den
        globalen Schalter des GET-Koerpers. Hier bleibt der Schalter auch
        NACH dem erzwungenen Re-Enable-Versuch (POST setzt ihn zwar, aber
        das Readback zeigt einen Server, der ihn weiterhin global
        zurueckgesetzt zeigt) aus -- die Funktion muss sichtbar NICHT
        bestaetigen (False), nicht den alten Fast-Pfad nehmen."""
        existing_cfg = {
            "0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL], "tags": ["local"],
                  "prefix_id": "", "connection_type": "external", "auth_type": "bearer"}
        }
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": existing_cfg, "ENABLE_OPENAI_API": False}),
            (200, {}),  # POST-Antwort (Inhalt hier irrelevant, nur Status 200 zaehlt)
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": existing_cfg, "ENABLE_OPENAI_API": False}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertFalse(ok, "global deaktiviertes ENABLE_OPENAI_API darf nie als korrekt bestaetigt werden.")
        self.assertIn("ENABLE_OPENAI_API", msg)
        self.assertEqual(len(script.calls), 3, "needs_write=True muss GET->POST->Readback-GET ausloesen, kein Fast-Pfad.")
        self.assertEqual(script.calls[1]["method"], "POST")
        self.assertTrue(script.calls[1]["body"]["ENABLE_OPENAI_API"], "POST muss den globalen Schalter explizit setzen.")

    def test_ensure_local_connection_globally_disabled_then_re_enabled_confirms(self):
        """Positiv-Gegenprobe zum vorigen Fall: dieselbe Ausgangslage (global
        deaktiviert), aber das Readback NACH dem erzwungenen Update zeigt den
        Schalter jetzt korrekt aktiv -- die Funktion bestaetigt dann True,
        weil tatsaechlich ein Schreibversuch samt Readback-Bestaetigung
        stattgefunden hat (kein blinder POST-Erfolg ohne Readback-Beleg)."""
        existing_cfg = {
            "0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL], "tags": ["local"],
                  "prefix_id": "", "connection_type": "external", "auth_type": "bearer"}
        }
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": existing_cfg, "ENABLE_OPENAI_API": False}),
            (200, {}),
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": existing_cfg, "ENABLE_OPENAI_API": True}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertTrue(ok, msg)
        self.assertEqual(len(script.calls), 3)

    def test_ensure_local_connection_never_touches_docker_network_helpers(self):
        """02: KEIN Aufruf der Docker-Netz-Mutation im lokalen Zweig."""
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [], "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {}}),
            (200, {}),
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": {"0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL]}},
                   "ENABLE_OPENAI_API": True}),
        ])
        with mock.patch("urllib.request.urlopen", script), \
             mock.patch.object(setup_mod, "_ensure_owui_on_litellm_network",
                                side_effect=AssertionError("Docker-Netz-Mutation darf im lokalen Zweig nicht laufen")), \
             mock.patch.object(setup_mod, "_owui_container_network_mode",
                                side_effect=AssertionError("Netzwerkkontext-Ermittlung gehoert zum Cloud/LiteLLM-Pfad")):
            ok, _msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertTrue(ok)

    def test_rewire_preset_base_model_local_rejects_invalid_existing_max_tokens_falls_back_to_profile_default(self):
        """O5-B.B2 (RELEASE-CASES.json): `_rewire_preset_base_model_local`s
        eigene "nur eine echte positive endliche Ganzzahl gilt als
        vorhandene strengere Grenze"-Pruefung (setup.py:2386-2394, R8-Fix)
        -- fuer JEDEN ungueltigen bestehenden `params.max_tokens`-Wert
        (0/negativ/bool/Bruch/NaN) muss der gesendete Payload auf den
        lokalen Profil-Startwert (`local_payload_overrides(profile,
        role='gm')['max_tokens']`) zurueckfallen, NICHT den ungueltigen Wert
        fortschreiben. Treibt die reale Funktion ueber den echten
        `urllib.request.urlopen`-Transportrand (`APIClient` selbst laeuft
        echt), kein `APIClient`-Mock."""
        cfg = {
            "variants": {
                "default": {"preset_id": FAKE_PRESET_ID, "preset_name": "Proj", "cache": True},
            },
        }
        profile = _profile()
        for bad_existing in (0, -5, True, 50.5, float("nan")):
            existing_preset = {
                "id": FAKE_PRESET_ID, "base_model_id": "openrouter/old-cloud-model",
                "meta": {"capabilities": {"vision": True}},
                "params": {"max_tokens": bad_existing, "system": "Du bist die SL."},
            }
            updated_preset = {
                "id": FAKE_PRESET_ID, "base_model_id": FAKE_LOCAL_MODEL,
                "meta": {"capabilities": setup_mod.LOCAL_TEXT_ONLY_CAPABILITIES},
                # A4-Fix: das Readback prueft jetzt die VOLLEN gesendeten
                # `desired_params` (local_payload_overrides + system), nicht
                # nur max_tokens -- der simulierte Backend-Zustand nach
                # erfolgreichem Update muss deshalb alle Felder enthalten.
                "params": {
                    "max_tokens": profile.gm_max_tokens, "temperature": 0.7, "stream": False,
                    "system": "Du bist die SL.",
                },
            }
            script = _UrlopenScript([
                (200, existing_preset),              # 1) get_model (initial read)
                (200, {"data": [{"id": FAKE_PRESET_ID}]}),  # 2) list_models (upsert_model exists-check)
                (200, {"id": FAKE_PRESET_ID}),        # 3) POST models/model/update
                (200, updated_preset),                # 4) get_model (post-update verify)
            ])
            with mock.patch("urllib.request.urlopen", script):
                ok, msg = setup_mod._rewire_preset_base_model_local(
                    _REPO_ROOT, cfg, FAKE_OWUI_URL, FAKE_OWUI_KEY, profile,
                )
            self.assertTrue(ok, f"bad_existing={bad_existing!r}: {msg}")
            update_call = script.calls[2]
            self.assertEqual(update_call["method"], "POST")
            sent_max_tokens = update_call["body"]["params"]["max_tokens"]
            self.assertEqual(
                sent_max_tokens, profile.gm_max_tokens,
                f"bad_existing={bad_existing!r}: ungueltige 'strengere' Grenze darf NICHT "
                f"fortgeschrieben werden -- gesendet wurde {sent_max_tokens!r}, erwartet "
                f"der lokale Profil-Startwert {profile.gm_max_tokens!r}.",
            )

    def test_rewire_preset_base_model_local_preserves_valid_stricter_existing_max_tokens(self):
        """Gegenprobe zu obigem Test: eine ECHTE positive endliche
        Ganzzahl, die STRENGER (kleiner) als der lokale Profil-Startwert
        ist, bleibt bewusst erhalten (B.5-Vertrag "bewusst strengere
        Grenzen erhalten") -- NICHT vom lokalen GM-Startwert ueberschrieben."""
        cfg = {"variants": {"default": {"preset_id": FAKE_PRESET_ID, "preset_name": "Proj", "cache": True}}}
        profile = _profile()
        stricter = 128
        self.assertLess(stricter, profile.gm_max_tokens)
        existing_preset = {
            "id": FAKE_PRESET_ID, "base_model_id": "openrouter/old-cloud-model",
            "meta": {"capabilities": {"vision": True}},
            "params": {"max_tokens": stricter, "system": "Du bist die SL."},
        }
        updated_preset = {
            "id": FAKE_PRESET_ID, "base_model_id": FAKE_LOCAL_MODEL,
            "meta": {"capabilities": setup_mod.LOCAL_TEXT_ONLY_CAPABILITIES},
            # A4-Fix: s. Kommentar im Gegenfall oben -- volle desired_params.
            "params": {"max_tokens": stricter, "temperature": 0.7, "stream": False, "system": "Du bist die SL."},
        }
        script = _UrlopenScript([
            (200, existing_preset),
            (200, {"data": [{"id": FAKE_PRESET_ID}]}),
            (200, {"id": FAKE_PRESET_ID}),
            (200, updated_preset),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._rewire_preset_base_model_local(
                _REPO_ROOT, cfg, FAKE_OWUI_URL, FAKE_OWUI_KEY, profile,
            )
        self.assertTrue(ok, msg)
        update_call = script.calls[2]
        self.assertEqual(update_call["body"]["params"]["max_tokens"], stricter)

    def test_rewire_preset_base_model_local_rejects_readback_showing_stale_upstream(self):
        """O2-A.A3 (RELEASE-CASES.json): "Rewire-Readback prüft alle
        geänderten Felder; keine Erfolgsmeldung bei altem ... Upstreamstand."
        `_rewire_preset_base_model_local`s Re-GET NACH dem Update
        (setup.py:2417-2421) ist der einzige Schutz gegen ein Backend, das
        den POST mit 200 bestätigt, aber beim sofortigen Re-GET noch den
        ALTEN (nicht umgeschriebenen) `base_model_id` zeigt (Replikations-
        verzoegerung/Race) -- KEINE Erfolgsmeldung in diesem Fall, trotz
        HTTP-200-POST."""
        cfg = {"variants": {"default": {"preset_id": FAKE_PRESET_ID, "preset_name": "Proj", "cache": True}}}
        profile = _profile()
        existing_preset = {
            "id": FAKE_PRESET_ID, "base_model_id": "openrouter/old-cloud-model",
            "meta": {"capabilities": {"vision": True}},
            "params": {"max_tokens": 64000, "system": "Du bist die SL."},
        }
        stale_readback_preset = dict(existing_preset)  # Re-GET zeigt weiterhin den ALTEN Upstream.
        script = _UrlopenScript([
            (200, existing_preset),
            (200, {"data": [{"id": FAKE_PRESET_ID}]}),
            (200, {"id": FAKE_PRESET_ID}),
            (200, stale_readback_preset),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._rewire_preset_base_model_local(
                _REPO_ROOT, cfg, FAKE_OWUI_URL, FAKE_OWUI_KEY, profile,
            )
        self.assertFalse(ok, "ein Readback mit altem Upstream darf NICHT als Erfolg gemeldet werden.")
        self.assertIn("Re-GET zeigt", msg)
        self.assertIn("openrouter/old-cloud-model", msg)

    def test_rewire_preset_base_model_local_rejects_readback_showing_stale_params_or_capabilities(self):
        """A4-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md A4, O2-A.A3):
        Gegenfall zum vorigen Test -- hier zeigt das Readback die GEWUENSCHTE
        `base_model_id` (das Backend hat den Upstream-Teil des POST korrekt
        uebernommen), aber Params/Capabilities sind (noch) die ALTEN
        Cloud-Werte (z.B. ein Backend, das `base_model_id` sofort, den Rest
        des Form-Payloads aber verzoegert/asynchron uebernimmt). Vor dem
        A4-Fix pruefte das Readback NUR `base_model_id` -- das waere hier
        faelschlich als Erfolg gemeldet worden, obwohl Params/Capabilities
        nie tatsaechlich auf dem lokalen Stand sind."""
        cfg = {"variants": {"default": {"preset_id": FAKE_PRESET_ID, "preset_name": "Proj", "cache": True}}}
        profile = _profile()
        existing_preset = {
            "id": FAKE_PRESET_ID, "base_model_id": "openrouter/old-cloud-model",
            "meta": {"capabilities": {"vision": True}},
            "params": {"max_tokens": 64000, "system": "Du bist die SL."},
        }
        # Readback: base_model_id korrekt umgebogen, aber Params/Capabilities
        # sind UNVERAENDERT die alten Cloud-Werte stehengeblieben.
        stale_fields_readback = {
            "id": FAKE_PRESET_ID, "base_model_id": FAKE_LOCAL_MODEL,
            "meta": {"capabilities": {"vision": True}},
            "params": {"max_tokens": 64000, "system": "Du bist die SL."},
        }
        script = _UrlopenScript([
            (200, existing_preset),
            (200, {"data": [{"id": FAKE_PRESET_ID}]}),
            (200, {"id": FAKE_PRESET_ID}),
            (200, stale_fields_readback),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._rewire_preset_base_model_local(
                _REPO_ROOT, cfg, FAKE_OWUI_URL, FAKE_OWUI_KEY, profile,
            )
        self.assertFalse(
            ok,
            "korrekter base_model_id BEI gleichzeitig alten Params/Capabilities darf NICHT als "
            "Erfolg gemeldet werden -- das Readback muss alle tatsaechlich geaenderten Felder pruefen.",
        )
        self.assertIn("veraltete Params/Capabilities", msg)

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

    def test_hold_on_existing_connection_with_foreign_auth_type_or_prefix(self):
        """O3-B.B2: eine bestehende Connection an GENAU der Ziel-URL mit
        einer vom erwarteten Vertrag (`auth_type='bearer'`, `prefix_id=''`)
        ABWEICHENDEN Konfiguration haelt VOR jeder Mutation -- der
        Produktcode haelt diesen Fall bereits ab (setup.py:2237-2244,
        "B2-Fix ... O3-B"), aber er war bisher UNGETESTET: alle
        existierenden Fixtures in dieser Datei setzen bereits passende
        Werte (auth_type='bearer', prefix_id='')."""
        for bad_cfg in (
            {"enable": True, "model_ids": [FAKE_LOCAL_MODEL], "tags": ["local"],
             "auth_type": "custom", "prefix_id": ""},
            {"enable": True, "model_ids": [FAKE_LOCAL_MODEL], "tags": ["local"],
             "auth_type": "bearer", "prefix_id": "zr-"},
        ):
            existing_cfg = {"0": bad_cfg}
            script = _UrlopenScript([
                (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                       "OPENAI_API_CONFIGS": existing_cfg, "ENABLE_OPENAI_API": True}),
            ])
            with mock.patch("urllib.request.urlopen", script):
                ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
            self.assertFalse(ok, f"abweichender auth_type/prefix_id muss halten, cfg={bad_cfg!r}")
            self.assertIn("ehrdeutig", msg)
            self.assertEqual(len(script.calls), 1, "Halt VOR jeder Mutation -- nur der eine GET.")

    def test_hold_on_ambiguous_connection_appearing_only_in_post_mutation_readback(self):
        """A4-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md A4, O3-B.B2):
        Gegenfall zu den drei `test_hold_on_*`-Faellen oben -- dort war die
        Ziel-URL bereits VOR der Mutation mehrdeutig (ein GET, Halt ohne
        POST). Hier ist der Ausgangszustand (erster GET) SAUBER eindeutig
        (Connection existiert noch nicht -> POST laeuft durch), aber das
        Readback NACH dem Update (zweiter GET) zeigt die Ziel-URL
        ZWEIFACH -- z.B. ein fremder Prozess legte waehrend unseres POST
        gleichzeitig einen zweiten Eintrag an derselben URL an. Vor dem
        A4-Fix verwendete das Readback `.index(target_url)` (ersten
        Treffer) und haette das als Erfolg gemeldet; die vormutative
        Eindeutigkeitspruefung lief nie erneut."""
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [], "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {}}),
            (200, {}),
            # Readback zeigt die Ziel-URL ZWEIFACH -- waehrend des eigenen
            # POST ist (simuliert) ein zweiter, fremder Eintrag entstanden.
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE, FAKE_LOCAL_BASE],
                   "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN, "concurrent-foreign-key"],
                   "OPENAI_API_CONFIGS": {
                       "0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL],
                             "auth_type": "bearer", "prefix_id": ""},
                       "1": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL],
                             "auth_type": "bearer", "prefix_id": ""},
                   },
                   "ENABLE_OPENAI_API": True}),
        ])
        with mock.patch("urllib.request.urlopen", script):
            ok, msg = setup_mod._ensure_owui_local_connection(FAKE_OWUI_URL, FAKE_OWUI_KEY, _profile())
        self.assertFalse(
            ok,
            "eine erst im POST-Readback mehrdeutig gewordene Ziel-URL darf NICHT als Erfolg "
            "gemeldet werden -- dieselbe Eindeutigkeitspruefung muss auch nach der Mutation gelten.",
        )
        self.assertIn("ehrdeutig", msg)
        self.assertEqual(len(script.calls), 3, "POST laeuft durch (sauberer Ausgangszustand) -- Halt erst beim Readback.")

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
                   "OPENAI_API_CONFIGS": {"0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL]}},
                   "ENABLE_OPENAI_API": True}),
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

    def test_persona_output_limit_validator_blocks_invalid_limits_before_physical_send(self):
        """O5-B.B1 (RELEASE-CASES.json): Persona-Pendant zum FROZEN
        `gm_owui._validate_gm_output_limit_tokens` (dort bereits per
        `test_m1_gm_owui.py` belegt, unveraendert) -- `persona_api.
        _validate_persona_max_tokens` existiert bereits (02 Block D, R8-Fix,
        "Identisches Muster ... nur ohne dessen None-'unbegrenzt'-Fall") und
        wird hier GETESTET, NICHT geaendert. Prueft den Validator direkt UND
        bestaetigt, dass er bei JEDER `PersonaApiDriver`-Konstruktion
        greift -- ein ungueltiges Limit blockiert also schon vor jedem
        physischen Request, nicht erst beim Versand."""
        self.assertEqual(_validate_persona_max_tokens(50), 50)
        self.assertIsInstance(_validate_persona_max_tokens(50), int)
        self.assertEqual(_validate_persona_max_tokens(50.0), 50)

        for bad in (0, -5, True, 50.5, float("inf"), float("-inf"), float("nan")):
            with self.assertRaises(ValueError, msg=f"value={bad!r} muss abgelehnt werden"):
                _validate_persona_max_tokens(bad)

        for bad in (0, -5, True, 50.5, float("nan")):
            config = PersonaApiConfig(base_url=FAKE_LOCAL_BASE, api_key=FAKE_LOCAL_TOKEN,
                                       model=FAKE_LOCAL_MODEL, max_tokens=bad)
            with self.assertRaises(ValueError, msg=f"max_tokens={bad!r} muss die Konstruktion blockieren"):
                PersonaApiDriver(config, "persona_bad_limit")

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

    # ─── O1-D (A5): Secret-Redaktion an den beiden bestellten Fehlerecho-
    # Grenzen -- Persona (persona_api.py) und GM (sl_client.py:SLSession.
    # turn). Ein (ggf. absichtlich fehlerhaft antwortendes) Double kann den
    # gesendeten Dummy-Token/-Key im Fehlerbody echoen; Fehlertyp/HTTP-
    # Status/Quota-Erkennung muessen trotzdem erhalten bleiben.

    def test_persona_api_driver_error_redacts_dummy_token_401_403_429_formfalsch(self):
        config = PersonaApiConfig(base_url=FAKE_LOCAL_BASE, api_key=FAKE_LOCAL_TOKEN, model=FAKE_LOCAL_MODEL)

        def _echoing_http_error(code: str, reason: str):
            exc = urllib.error.HTTPError(
                FAKE_LOCAL_BASE + "/chat/completions", code, reason, {}, None,
            )
            exc.read = lambda: json.dumps(
                {"error": reason, "echo_headers": {"Authorization": f"Bearer {FAKE_LOCAL_TOKEN}"}}
            ).encode("utf-8")
            return exc

        cases = [
            (401, "unauthorized", ProviderAuthError),
            (403, "forbidden", ProviderAuthError),
            (402, "payment required", ProviderUnavailableError),
            (429, "rate limited", ProviderQuotaError),
        ]
        for code, reason, expected_exc in cases:
            driver = PersonaApiDriver(config, f"persona_redact_{code}")
            script = _UrlopenScript([_echoing_http_error(code, reason)])
            with mock.patch("urllib.request.urlopen", script):
                with self.assertRaises(expected_exc) as ctx:
                    driver.decide({"system": "s", "user": "u"})
            message = str(ctx.exception)
            self.assertNotIn(FAKE_LOCAL_TOKEN, message, f"HTTP {code}: Token-Echo darf nicht uebernommen werden.")
            self.assertIn(str(code), message, f"HTTP-Status {code} muss trotz Redaktion erhalten bleiben.")

        # formfalscher Body (keine choices[0].message.content) -- ebenfalls redigiert.
        driver = PersonaApiDriver(config, "persona_redact_malformed")
        malformed = {"echo_headers": {"Authorization": f"Bearer {FAKE_LOCAL_TOKEN}"}}
        script = _UrlopenScript([(200, malformed)])
        with mock.patch("urllib.request.urlopen", script):
            with self.assertRaises(ProviderUnavailableError) as ctx:
                driver.decide({"system": "s", "user": "u"})
        self.assertNotIn(FAKE_LOCAL_TOKEN, str(ctx.exception))

    def test_gm_owui_transport_error_redacts_dummy_owui_key_echo_at_sl_client_boundary(self):
        run_dir = self._tmp_dir("gm-redact-run")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        auth_exc = urllib.error.HTTPError(FAKE_OWUI_URL + "/api/chat/completions", 401, "unauthorized", {}, None)
        auth_exc.read = lambda: json.dumps(
            {"error": "unauthorized", "echo_headers": {"Authorization": f"Bearer {FAKE_OWUI_KEY}"}}
        ).encode("utf-8")
        script = _UrlopenScript([auth_exc])
        with mock.patch("urllib.request.urlopen", script):
            transport = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="tisch-redact",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID, is_dollar_billed=False,
            )
            with self.assertRaises(Exception) as ctx:
                transport.turn(1, "Text")
        message = str(ctx.exception)
        self.assertNotIn(FAKE_OWUI_KEY, message, "OWUI-Key darf im GM-Fehlerecho nicht uebernommen werden.")
        self.assertIn("401", message, "HTTP-Status muss trotz Redaktion erhalten bleiben.")

    def test_gm_owui_transport_error_redacts_dummy_owui_key_echo_402_429_formfalsch(self):
        """O1-D.D3/D4-Nachzug (RELEASE-CASES.json): GM-Seite war bisher nur
        fuer 401/403 belegt (routing.py:534-553,471-489) -- diese Faelle
        schliessen die restliche D3-Aufzaehlung ("401/403/402/429, ...
        nicht parsebares JSON und falsche Antwortform") fuer GM:
        402 (Payment Required, ProviderUnavailableError-Aequivalent auf der
        Persona-Seite, hier derselbe OWUIError-Pfad), 429 (Rate-Limit) und
        eine formfalsche 200-Antwort (kein `choices[0].message.content`,
        `owui_client.py:116` `OWUIError('Unerwartete Response-Struktur: ...')`).
        `transport_max_retries=1` haelt in JEDEM Fall bei genau EINEM
        physischen POST-Versuch (`owui_client.py:_post`s Retryschleife mit
        `max_retries=1` -- selbst ein 'retrybarer' Code wie 402/429 loest
        hier KEINEN automatischen Zweitversand aus)."""
        def _echoing_http_error(code: int, reason: str) -> urllib.error.HTTPError:
            exc = urllib.error.HTTPError(FAKE_OWUI_URL + "/api/chat/completions", code, reason, {}, None)
            exc.read = lambda: json.dumps(
                {"error": reason, "echo_headers": {"Authorization": f"Bearer {FAKE_OWUI_KEY}"}}
            ).encode("utf-8")
            return exc

        for code, reason in ((402, "payment required"), (429, "rate limited")):
            run_dir = self._tmp_dir(f"gm-redact-{code}-run")
            os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
            os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
            script = _UrlopenScript([_echoing_http_error(code, reason)])
            with mock.patch("urllib.request.urlopen", script):
                transport = GmOwuiTransport(
                    _SL_CLIENT_PY, run_dir, table_id=f"tisch-redact-{code}",
                    sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
                    transport_max_retries=1, is_dollar_billed=False,
                )
                with self.assertRaises(Exception) as ctx:
                    transport.turn(1, "Text")
            message = str(ctx.exception)
            self.assertNotIn(FAKE_OWUI_KEY, message, f"HTTP {code}: OWUI-Key-Echo darf nicht uebernommen werden.")
            self.assertIn(str(code), message, f"HTTP-Status {code} muss trotz Redaktion erhalten bleiben.")
            self.assertEqual(len(script.calls), 1, f"HTTP {code}: transport_max_retries=1 erlaubt genau 1 physischen Versuch.")

        # formfalsche 200-Antwort (kein choices[0].message.content).
        run_dir = self._tmp_dir("gm-redact-malformed-run")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        malformed = {"echo_headers": {"Authorization": f"Bearer {FAKE_OWUI_KEY}"}, "unexpected": "shape"}
        script = _UrlopenScript([(200, malformed)])
        with mock.patch("urllib.request.urlopen", script):
            transport = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="tisch-redact-malformed",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
                transport_max_retries=1, is_dollar_billed=False,
            )
            with self.assertRaises(Exception) as ctx:
                transport.turn(1, "Text")
        message = str(ctx.exception)
        self.assertNotIn(FAKE_OWUI_KEY, message, "formfalsche Antwort: OWUI-Key darf nicht uebernommen werden.")
        self.assertIn("Unerwartete Response-Struktur", message)

    def test_gm_owui_transport_truncates_long_echo_at_owui_sub_layer_before_redaction(self):
        """O1-D.D3/D4-Nachzug: "an 300/400-Zeichengrenzen, auch bereits im
        OWUI-Unterbau gekuerzt" -- Defense-in-Depth unabhaengig von
        `sl_client._redact_secret_text`s Regex. `owui_client.py:_post`
        (HTTPError-Zweig) schneidet den rohen Serverbody VOR jeder
        Exceptionkonstruktion auf 400 Zeichen (`e.read().decode()[:400]`);
        `OWUIChat.say`s formfalscher-Response-Zweig schneidet den
        json-gedumpten Koerper auf 300 Zeichen (`json.dumps(resp)[:300]`).
        Platziert den Dummy-Key JEWEILS HINTER dieser Schnittstelle (also
        bereits vom OWUI-Unterbau selbst entfernt, nicht erst durch die
        sl_client-Redaktion) -- bestaetigt, dass die Kuerzung selbst schon
        greift, nicht nur die nachgeschaltete Regex."""
        # (a) HTTPError-Zweig, 400-Zeichen-Schnitt: Fuellmaterial VOR dem
        # Key haelt den Key sicher hinter Index 400 -- selbst wenn die
        # Redaktionsregex in sl_client NIE liefe, duerfte der Key schon
        # wegen owui_client.py's eigenem Schnitt nicht in der finalen
        # Meldung stehen.
        run_dir = self._tmp_dir("gm-truncate-http-run")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        padding = "x" * 450
        exc = urllib.error.HTTPError(
            FAKE_OWUI_URL + "/api/chat/completions", 500, "server error", {}, None,
        )
        exc.read = lambda: json.dumps(
            {"detail": padding, "echo_headers": {"Authorization": f"Bearer {FAKE_OWUI_KEY}"}}
        ).encode("utf-8")
        script = _UrlopenScript([exc])
        with mock.patch("urllib.request.urlopen", script):
            transport = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="tisch-truncate-http",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
                transport_max_retries=1, is_dollar_billed=False,
            )
            with self.assertRaises(Exception) as ctx:
                transport.turn(1, "Text")
        message = str(ctx.exception)
        self.assertNotIn(FAKE_OWUI_KEY, message, (
            "der Key liegt im rohen Body HINTER der 400-Zeichen-Schnittstelle von "
            "owui_client.py -- die Kuerzung selbst muss ihn schon entfernt haben."
        ))
        self.assertIn("500", message, "HTTP-Status muss trotz Kuerzung erhalten bleiben.")

        # (b) formfalsche-Antwort-Zweig, 300-Zeichen-Schnitt: derselbe
        # Aufbau fuer OWUIChat.say()s json.dumps(resp)[:300]-Pfad.
        run_dir = self._tmp_dir("gm-truncate-malformed-run")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        malformed = {"unexpected": "x" * 350, "echo_headers": {"Authorization": f"Bearer {FAKE_OWUI_KEY}"}}
        script = _UrlopenScript([(200, malformed)])
        with mock.patch("urllib.request.urlopen", script):
            transport = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="tisch-truncate-malformed",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
                transport_max_retries=1, is_dollar_billed=False,
            )
            with self.assertRaises(Exception) as ctx:
                transport.turn(1, "Text")
        message = str(ctx.exception)
        self.assertNotIn(FAKE_OWUI_KEY, message, (
            "der Key liegt im json-gedumpten Body HINTER der 300-Zeichen-Schnittstelle "
            "von owui_client.py:OWUIChat.say -- die Kuerzung selbst muss ihn schon entfernt haben."
        ))
        self.assertIn("Unerwartete Response-Struktur", message)

    def test_gm_owui_transport_redacts_key_fragment_crossing_truncation_boundary(self):
        """A1 (evidence/INDEPENDENT-GENERAL-REVIEW.md A1, O1-D.D3/D4): Gegenfall
        zum Test oben -- hier liegt der Dummy-Key NICHT vollstaendig hinter der
        300/400-Zeichen-Schnittkante von owui_client.py, sondern KREUZT sie, in
        einem gewoehnlichen JSON-Feld OHNE 'Bearer'-Praefix. Vor dem A1-Fix blieb
        in diesem Fall ein Praefix des Keys stehen -- weder vollstaendiger Key
        noch Bearer-Treffer, also von sl_client._redact_secret_text's Replace/
        Regex nicht erfasst. Nach dem Fix redigiert owui_client.py:OWUIChat
        den konfigurierten Key bereits VOR der Kuerzung -- kein zusammenhaengendes
        Fragment von mindestens 8 Key-Zeichen darf in der finalen Meldung
        auftauchen, unabhaengig davon, wo genau die Schnittkante faellt."""
        key_fragments = [FAKE_OWUI_KEY[i:i + 8] for i in range(0, len(FAKE_OWUI_KEY) - 8 + 1)]

        # (a) HTTPError-Zweig: Key beginnt bei Index 388 und kreuzt damit die
        # 400-Zeichen-Schnittkante von owui_client.py (e.read().decode()[:400]);
        # die Kuerzung alleine liesse "owui-fake-ke" (erste 12 Zeichen) stehen.
        run_dir = self._tmp_dir("gm-redact-cross-http-run")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        body_text = json.dumps({"detail": "x" * 376 + FAKE_OWUI_KEY + "y" * 50})
        exc = urllib.error.HTTPError(
            FAKE_OWUI_URL + "/api/chat/completions", 500, "server error", {}, None,
        )
        exc.read = lambda: body_text.encode("utf-8")
        script = _UrlopenScript([exc])
        with mock.patch("urllib.request.urlopen", script):
            transport = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="tisch-redact-cross-http",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
                transport_max_retries=1, is_dollar_billed=False,
            )
            with self.assertRaises(Exception) as ctx:
                transport.turn(1, "Text")
        message = str(ctx.exception)
        self.assertNotIn(FAKE_OWUI_KEY, message)
        for frag in key_fragments:
            self.assertNotIn(frag, message, (
                f"Key-Fragment {frag!r} darf nicht stehenbleiben -- der Key kreuzte "
                "die 400-Zeichen-Schnittkante, Redaktion muss vor der Kuerzung laufen."
            ))
        self.assertIn("500", message, "HTTP-Status muss trotz Redaktion erhalten bleiben.")

        # (b) formfalsche-Antwort-Zweig: Key beginnt bei Index 288 und kreuzt
        # damit die 300-Zeichen-Schnittkante (json.dumps(resp)[:300]).
        run_dir = self._tmp_dir("gm-redact-cross-malformed-run")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        malformed = {"unexpected": "x" * 272 + FAKE_OWUI_KEY + "z" * 50}
        script = _UrlopenScript([(200, malformed)])
        with mock.patch("urllib.request.urlopen", script):
            transport = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="tisch-redact-cross-malformed",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
                transport_max_retries=1, is_dollar_billed=False,
            )
            with self.assertRaises(Exception) as ctx:
                transport.turn(1, "Text")
        message = str(ctx.exception)
        self.assertNotIn(FAKE_OWUI_KEY, message)
        for frag in key_fragments:
            self.assertNotIn(frag, message, (
                f"Key-Fragment {frag!r} darf nicht stehenbleiben -- der Key kreuzte "
                "die 300-Zeichen-Schnittkante, Redaktion muss vor der Kuerzung laufen."
            ))
        self.assertIn("Unerwartete Response-Struktur", message)


class LocalTokenhostPersonaEnvReentryTests(unittest.TestCase):
    """O6-B (02_NACHARBEIT.md Gruppe C, G2/G3-Fix): `mmo_sim.adapters.
    factories._maybe_default_local_tokenhost_persona_env` -- Herkunft von
    Prozessoverride vs. selbst gesetztem Wert vs. abgeleitetem Default
    zuverlaessig unterscheiden. VOR dem Fix erkannte die Funktion ihre
    EIGENEN vorherigen Schreibzugriffe nicht wieder: eine zweite/erneute
    Personakonstruktion im selben Prozess sah die selbst gesetzten
    MMO_SIM_PERSONA_API_*-Werte als widersprechenden externen Override an
    und stoppte sichtbar mit RuntimeError."""

    _PERSONA_ENV_KEYS = (
        "MMO_SIM_PERSONA_CLI", "MMO_SIM_PERSONA_API_BASE_URL", "MMO_SIM_PERSONA_API_KEY",
        "MMO_SIM_PERSONA_API_MODEL", "MMO_SIM_PERSONA_API_MAX_TOKENS", "MMO_SIM_PERSONA_API_DOLLAR_BILLED",
        factories_mod._LOCAL_TOKENHOST_RESOLVED_MARKER,
    )

    def setUp(self):
        self._tmp_dirs: list[Path] = []
        self._env_backup = dict(os.environ)
        for key in self._PERSONA_ENV_KEYS:
            os.environ.pop(key, None)

    def tearDown(self):
        for d in self._tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        os.environ.clear()
        os.environ.update(self._env_backup)

    def _tmp_home_with_local_profile(self) -> Path:
        tmp_home = Path(tempfile.mkdtemp(prefix="o6b-persona-reentry-"))
        self._tmp_dirs.append(tmp_home)
        env_path = tmp_home / ".openwebui_env"
        updates = lmp.build_local_profile_updates(base_url=FAKE_LOCAL_BASE, model=FAKE_LOCAL_MODEL, api_key=FAKE_LOCAL_TOKEN)
        self.assertTrue(setup_mod._update_env_file_preserving(env_path, updates))
        return tmp_home

    def _actual_persona(self, key="rest-persona"):
        data = Path(tempfile.mkdtemp(prefix="rest-persona-data-"))
        self._tmp_dirs.append(data)
        return factories_mod.default_persona_driver_factory(data)(key)

    def _assert_api_wire(self, driver, *, model, token, limit, billed):
        self.assertIsInstance(driver, PersonaApiDriver)
        self.assertEqual(driver.is_dollar_billed, billed)
        script = _UrlopenScript([(200, {
            "choices": [{"message": {"content": "synthetische Antwort"}}],
            "usage": {"prompt_tokens": 19, "completion_tokens": 7},
        })])
        with mock.patch("urllib.request.urlopen", script):
            self.assertEqual(driver.decide({"user": "synthetischer Zug"}).text,
                             "synthetische Antwort")
        self.assertEqual(len(script.calls), 1)
        call = script.calls[0]
        self.assertEqual(call["url"], FAKE_LOCAL_BASE + "/chat/completions")
        self.assertEqual(call["headers"]["Authorization"], "Bearer " + token)
        self.assertEqual(call["body"]["model"], model)
        self.assertEqual(call["body"]["max_tokens"], limit)

    def test_same_url_file_api_gm_autoload_local_cloud_actual_new_persona(self):
        """R1a: URL-Gleichheit allein darf den eigenen Vollsnapshot nicht entwerten."""
        home = self._tmp_home_with_local_profile()
        path = home / ".openwebui_env"
        updates = dict(lmp.build_local_profile_updates(
            base_url=FAKE_LOCAL_BASE, model=FAKE_LOCAL_MODEL, api_key=FAKE_LOCAL_TOKEN,
            persona_max_tokens=111,
        ))
        updates.update({
            "MMO_SIM_PERSONA_API_BASE_URL": FAKE_LOCAL_BASE,
            "MMO_SIM_PERSONA_API_KEY": "synthetic-old-cloud-token",
            "MMO_SIM_PERSONA_API_MODEL": "synthetic-old-cloud-model",
            "MMO_SIM_PERSONA_API_MAX_TOKENS": "677",
            "MMO_SIM_PERSONA_API_DOLLAR_BILLED": "1",
        })
        self.assertTrue(setup_mod._update_env_file_preserving(path, updates))
        with mock.patch.object(Path, "home", return_value=home):
            # Derselbe Autoload wie beim GM, vor der Persona-Konstruktion.
            setup_mod._auto_load_owui_env()
            local = self._actual_persona("local-first")
            self._assert_api_wire(local, model=FAKE_LOCAL_MODEL, token=FAKE_LOCAL_TOKEN,
                                  limit=111, billed=False)
            self.assertTrue(setup_mod._update_env_file_preserving(path, dict(lmp.cloud_provider_updates())))
            cloud = self._actual_persona("cloud-after-rekey")
            self.assertIsNot(local, cloud)
            self._assert_api_wire(cloud, model="synthetic-old-cloud-model",
                                  token="synthetic-old-cloud-token", limit=677, billed=True)
            # Eine neue Instanz aendert die alte lokale Instanz nicht global.
            self.assertFalse(local.is_dollar_billed)

    def test_file_only_cli_then_local_choice_constructs_actual_api_driver(self):
        """R1b: der nur dateiabgeleitete CLI-Altwert darf nicht erneut gewinnen."""
        home = self._tmp_home_with_local_profile()
        self.assertTrue(setup_mod._update_env_file_preserving(
            home / ".openwebui_env", {"MMO_SIM_PERSONA_CLI": "synthetic-old-cli"}))
        with mock.patch.object(Path, "home", return_value=home):
            setup_mod._auto_load_owui_env()
            self._assert_api_wire(self._actual_persona(), model=FAKE_LOCAL_MODEL,
                                  token=FAKE_LOCAL_TOKEN, limit=400, billed=False)
            # Auch wiederholter Autoload darf die echte Adapterwahl nicht kippen.
            self.assertIsInstance(self._actual_persona("local-again"), PersonaApiDriver)

    def test_explicit_cli_before_and_after_local_default_is_actual_cli(self):
        from mmo_sim.adapters.persona_claude_code import PersonaClaudeCodeDriver
        home = self._tmp_home_with_local_profile()
        with mock.patch.object(Path, "home", return_value=home):
            os.environ["MMO_SIM_PERSONA_CLI"] = "synthetic-explicit-cli-before"
            first = self._actual_persona()
            self.assertIsInstance(first, PersonaClaudeCodeDriver)
            self.assertEqual(first.config.binary, "synthetic-explicit-cli-before")
            os.environ.pop("MMO_SIM_PERSONA_CLI")
            self.assertIsInstance(self._actual_persona(), PersonaApiDriver)
            os.environ["MMO_SIM_PERSONA_CLI"] = "synthetic-explicit-cli-after"
            after = self._actual_persona()
            self.assertIsInstance(after, PersonaClaudeCodeDriver)
            self.assertEqual(after.config.binary, "synthetic-explicit-cli-after")
            os.environ["MMO_SIM_PERSONA_TIMEOUT_SECONDS"] = "invalid-timeout"
            with self.assertRaisesRegex(ValueError, "MMO_SIM_PERSONA_TIMEOUT_SECONDS"):
                self._actual_persona("invalid-cli-no-api-fallback")

    def test_explicit_api_beats_file_only_cli_at_actual_selection(self):
        home = self._tmp_home_with_local_profile()
        self.assertTrue(setup_mod._update_env_file_preserving(
            home / ".openwebui_env", {"MMO_SIM_PERSONA_CLI": "synthetic-file-cli"}))
        with mock.patch.object(Path, "home", return_value=home):
            setup_mod._auto_load_owui_env()
            os.environ.update({
                "MMO_SIM_PERSONA_API_BASE_URL": FAKE_LOCAL_BASE,
                "MMO_SIM_PERSONA_API_KEY": "synthetic-explicit-api",
                "MMO_SIM_PERSONA_API_MODEL": "explicit-model",
            })
            self._assert_api_wire(self._actual_persona(), model="explicit-model",
                                  token="synthetic-explicit-api", limit=400, billed=True)

    def test_incomplete_explicit_api_holds_without_local_default(self):
        home = self._tmp_home_with_local_profile()
        with mock.patch.object(Path, "home", return_value=home):
            for missing in self._PERSONA_ENV_KEYS[1:4]:
                with self.subTest(missing=missing):
                    for key in self._PERSONA_ENV_KEYS:
                        os.environ.pop(key, None)
                    os.environ.update({
                        "MMO_SIM_PERSONA_API_BASE_URL": FAKE_LOCAL_BASE,
                        "MMO_SIM_PERSONA_API_KEY": "synthetic-incomplete-override",
                        "MMO_SIM_PERSONA_API_MODEL": "incomplete-override-model",
                    })
                    os.environ.pop(missing)
                    with self.assertRaises(RuntimeError):
                        self._actual_persona("must-hold")
                    self.assertNotEqual(os.environ.get("MMO_SIM_PERSONA_API_MODEL"), FAKE_LOCAL_MODEL)

    def test_explicit_same_url_api_before_and_after_local_default_is_actual_api(self):
        home = self._tmp_home_with_local_profile()
        with mock.patch.object(Path, "home", return_value=home):
            for phase in ("before", "after"):
                if phase == "after":
                    for key in self._PERSONA_ENV_KEYS:
                        os.environ.pop(key, None)
                    self.assertIsInstance(self._actual_persona(), PersonaApiDriver)
                os.environ.update({
                    "MMO_SIM_PERSONA_API_BASE_URL": FAKE_LOCAL_BASE,
                    "MMO_SIM_PERSONA_API_KEY": "synthetic-explicit-api-" + phase,
                    "MMO_SIM_PERSONA_API_MODEL": "explicit-model-" + phase,
                    "MMO_SIM_PERSONA_API_MAX_TOKENS": "263",
                    "MMO_SIM_PERSONA_API_DOLLAR_BILLED": "1",
                })
                self._assert_api_wire(self._actual_persona(), model="explicit-model-" + phase,
                                      token="synthetic-explicit-api-" + phase, limit=263, billed=True)

    def test_second_persona_construction_in_same_process_does_not_raise(self):
        tmp_home = self._tmp_home_with_local_profile()
        with mock.patch.object(Path, "home", return_value=tmp_home):
            first = factories_mod._maybe_default_local_tokenhost_persona_env()
            self.assertTrue(first, "erste Aufloesung muss die lokale Wahl erkennen.")
            self.assertEqual(os.environ.get("MMO_SIM_PERSONA_API_MODEL"), FAKE_LOCAL_MODEL)
            # Zweiter Aufruf im SELBEN Prozess (zweite Persona/dieselbe Persona
            # erneut) -- darf NICHT als widersprechender externer Override
            # gelesen werden und NICHT crashen.
            second = factories_mod._maybe_default_local_tokenhost_persona_env()
            self.assertTrue(second, "zweiter Aufruf muss die eigene vorherige Aufloesung idempotent fortsetzen.")
            self.assertEqual(os.environ.get("MMO_SIM_PERSONA_API_MODEL"), FAKE_LOCAL_MODEL)
            # Dritter Aufruf (z.B. "nach Rekey" im selben Testlauf noch ohne
            # Aenderung) bleibt ebenfalls stabil.
            third = factories_mod._maybe_default_local_tokenhost_persona_env()
            self.assertTrue(third)

    def test_rekey_to_cloud_clears_stale_local_persona_env_in_same_process(self):
        """G3-Fix: nach einem Rueckwechsel auf cloud/legacy duerfen die vom
        Resolver SELBST gesetzten lokalen API-/Dollarmarker-Werte nicht als
        stiller Prozessoverride fuer die naechste (jetzt wieder Cloud-)
        Personakonstruktion im Environment stehen bleiben."""
        tmp_home = self._tmp_home_with_local_profile()
        with mock.patch.object(Path, "home", return_value=tmp_home):
            self.assertTrue(factories_mod._maybe_default_local_tokenhost_persona_env())
            self.assertEqual(os.environ.get("MMO_SIM_PERSONA_API_DOLLAR_BILLED"), "0")

            # Bewusster Rueckwechsel auf cloud (wie action_rekeys) -- lokale
            # Felder bleiben in der Datei stehen, nur der Provider wechselt.
            env_path = tmp_home / ".openwebui_env"
            self.assertTrue(setup_mod._update_env_file_preserving(env_path, dict(lmp.cloud_provider_updates())))

            result = factories_mod._maybe_default_local_tokenhost_persona_env()
            self.assertFalse(result, "nach Rueckwechsel auf cloud liefert der lokale Resolver False.")
            for key in (
                "MMO_SIM_PERSONA_API_BASE_URL", "MMO_SIM_PERSONA_API_KEY",
                "MMO_SIM_PERSONA_API_MODEL", "MMO_SIM_PERSONA_API_MAX_TOKENS",
                "MMO_SIM_PERSONA_API_DOLLAR_BILLED",
            ):
                self.assertIsNone(
                    os.environ.get(key),
                    f"{key} muss nach Rueckwechsel auf cloud nicht mehr als stiller lokaler "
                    "Prozessoverride im Environment stehen.",
                )

    def test_gm_autoloaded_file_values_are_not_treated_as_deliberate_persona_override(self):
        """A3-Fix Teil 1 (evidence/INDEPENDENT-GENERAL-REVIEW.md A3, Fall
        "GM-vorab-autoloaded Dateialtwerte"): `default_gm_transport_factory`
        ruft `setup._auto_load_owui_env()` BEREITS VOR der ersten
        Personaaufloesung auf (gleicher Prozess, gemeinsames os.environ).
        Liegt in `~/.openwebui_env` noch ein STEHENGEBLIEBENER alter Cloud-
        Persona-Wert (frueherer Lauf, nie aufgeraeumt), laedt dieser GM-
        Autoload ihn in `MMO_SIM_PERSONA_API_*` -- OHNE den A3-Fix erkannte
        `_maybe_default_local_tokenhost_persona_env` diesen Wert faelschlich
        als bewusst VOR dem Aufruf gesetzten Prozessoverride (Fall (a)) und
        verwendete den ALTEN Cloudwert statt der aktuellen lokalen Wahl."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o6b-gm-autoload-stale-"))
        self._tmp_dirs.append(tmp_home)
        env_path = tmp_home / ".openwebui_env"
        updates = dict(lmp.build_local_profile_updates(
            base_url=FAKE_LOCAL_BASE, model=FAKE_LOCAL_MODEL, api_key=FAKE_LOCAL_TOKEN,
        ))
        stale_model = "stale-cloud-persona-model-from-old-run"
        updates["MMO_SIM_PERSONA_API_BASE_URL"] = "https://old-cloud-api.example/v1"
        updates["MMO_SIM_PERSONA_API_KEY"] = "stale-cloud-key-not-secret"
        updates["MMO_SIM_PERSONA_API_MODEL"] = stale_model
        self.assertTrue(setup_mod._update_env_file_preserving(env_path, updates))

        with mock.patch.object(Path, "home", return_value=tmp_home):
            # Simuliert den GM-Transportbau: `_auto_load_owui_env()` laeuft
            # VOR jeder Personaaufloesung und laedt die stehengebliebenen
            # Altwerte, weil sie im Prozess-Env noch fehlen.
            setup_mod._auto_load_owui_env()
            self.assertEqual(os.environ.get("MMO_SIM_PERSONA_API_MODEL"), stale_model)

            result = factories_mod._maybe_default_local_tokenhost_persona_env()
            self.assertTrue(
                result,
                "der nur vom GM-Autoload nachgeladene Datei-Altwert ist KEIN bewusster "
                "Prozessoverride -- die aktuelle lokale Wahl muss ihn ueberschreiben.",
            )
            self.assertEqual(
                os.environ.get("MMO_SIM_PERSONA_API_MODEL"), FAKE_LOCAL_MODEL,
                "die aktuelle lokale Wahl muss den stehengebliebenen Datei-Altwert ersetzen.",
            )

    def test_foreign_override_written_after_self_resolution_is_not_silently_overwritten(self):
        """O6-B.B2 (RELEASE-CASES.json) "nach lokalem Default": nachdem bereits
        ein lokaler Default aufgeloest wurde, schreibt ein FREMDER Aufrufer
        (Lab/CLI/Testsetup) einen EIGENEN, bewusst gesetzten, GUELTIGEN Override
        (`MMO_SIM_PERSONA_API_*`). Dieser gueltige explizite Override behaelt
        Vorrang und wird TATSAECHLICH verwendet -- er wird weder stillschweigend
        von der lokalen Wahl ueberschrieben noch fuehrt er nur zu einem Halt
        (frueher: RuntimeError OHNE Verwendung = der in GAPS.md benannte Origin-
        Prioritaetsfehler). Der Fingerabdruck-Vergleich erkennt den Override
        (Abweichung vom zuletzt SELBST gesetzten Snapshot), die Originprioritaet
        in `_maybe_default_local_tokenhost_persona_env` tritt zurueck (False),
        und `default_persona_driver_factory` konstruiert den Adapter aus dem
        Override. Treibt die ECHTE Folgefunktion, nicht nur den Resolver."""
        # A3-Fix: eigener, von PersonaApiConfigs Klassendefault (400)
        # UNTERSCHEIDBARER lokaler persona_max_tokens-Wert -- sonst wuerde
        # ein stehengebliebener lokaler Marker zufaellig mit dem Default
        # zusammenfallen und die untere MAX_TOKENS-Pruefung waere blind.
        tmp_home = Path(tempfile.mkdtemp(prefix="o6b-persona-reentry-distinct-"))
        self._tmp_dirs.append(tmp_home)
        env_path = tmp_home / ".openwebui_env"
        updates = lmp.build_local_profile_updates(
            base_url=FAKE_LOCAL_BASE, model=FAKE_LOCAL_MODEL, api_key=FAKE_LOCAL_TOKEN,
            persona_max_tokens=111,
        )
        self.assertTrue(setup_mod._update_env_file_preserving(env_path, updates))
        override_url = "http://127.0.0.1:29999/v1"
        override_key = "foreign-override-key-not-secret"
        override_model = "foreign-override-model"
        with mock.patch.object(Path, "home", return_value=tmp_home):
            self.assertTrue(factories_mod._maybe_default_local_tokenhost_persona_env())
            self.assertEqual(os.environ.get("MMO_SIM_PERSONA_API_MODEL"), FAKE_LOCAL_MODEL)
            self.assertEqual(os.environ.get("MMO_SIM_PERSONA_API_MAX_TOKENS"), "111")

            # Ein FREMDER Aufrufer schreibt jetzt einen EIGENEN, von unserer
            # Aufloesung abweichenden, GUELTIGEN Override -- der (veraltete)
            # Marker aus dem ersten Aufruf steht dabei noch.
            os.environ["MMO_SIM_PERSONA_API_BASE_URL"] = override_url
            os.environ["MMO_SIM_PERSONA_API_KEY"] = override_key
            os.environ["MMO_SIM_PERSONA_API_MODEL"] = override_model

            # Originprioritaet: der gueltige Override gewinnt -> Resolver tritt
            # zurueck (False), KEIN Halt, KEIN stilles Ueberschreiben.
            result = factories_mod._maybe_default_local_tokenhost_persona_env()
            self.assertFalse(
                result,
                "nach lokalem Default tritt der Resolver fuer einen gueltigen expliziten "
                "Override zurueck (Originprioritaet), statt zu halten oder zu ueberschreiben.",
            )
            # Der fremde Wert bleibt erhalten (nicht stillschweigend ersetzt) ...
            self.assertEqual(os.environ.get("MMO_SIM_PERSONA_API_BASE_URL"), override_url)

            data_dir = Path(tempfile.mkdtemp(prefix="o6b-after-default-data-"))
            self._tmp_dirs.append(data_dir)
            factory = factories_mod.default_persona_driver_factory(data_dir)
            driver = factory("persona_override_after_local_default")
        # ... und wird vom echten Factory-/Adapterweg TATSAECHLICH verwendet.
        self.assertEqual(
            driver.config.base_url, override_url,
            "der nach dem lokalen Default gesetzte gueltige Override muss tatsaechlich "
            "verwendet werden -- nicht nur unveraendert im Environment uebrig bleiben.",
        )
        self.assertEqual(driver.config.model, override_model)
        self.assertEqual(driver.config.api_key, override_key)
        # A3-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md A3, O6-B.B2): der
        # Override aendert hier nur die DREI Verbindungsfelder (URL/Key/
        # Model), NICHT MAX_TOKENS/DOLLAR_BILLED -- vor dem Fix blieb die
        # vom ERSTEN lokalen Default selbst gesetzte `MMO_SIM_PERSONA_API_
        # DOLLAR_BILLED=0` im Environment stehen und wurde faelschlich fuer
        # diesen Override uebernommen (local_unpriced statt des regulaeren
        # fremden Clouddefaults `dollar_billed=True`). Die vorherigen drei
        # Asserts pruefen nur URL/Modell/Key -- genau die vom General
        # benannte Luecke ("falsche Billingherkunft bleibt unsichtbar").
        self.assertTrue(
            driver.is_dollar_billed,
            "ein gueltiger Cloud/API-Override ohne eigenen Billingmarker muss den "
            "regulaeren fremden Clouddefault (dollar_billed=True) tragen, nicht die "
            "stehengebliebene lokale Billingmarkierung der vorherigen Aufloesung.",
        )
        self.assertEqual(
            driver.config.max_tokens, 400,
            "der Override setzt kein eigenes MAX_TOKENS -- PersonaApiConfig muss dann "
            "seinen eigenen Klassendefault (400) tragen, NICHT das stehengebliebene "
            "lokale Limit (111) der vorherigen Aufloesung.",
        )

    def test_pre_existing_api_override_before_first_resolution_takes_precedence(self):
        """O6-B.B2 (RELEASE-CASES.json): "gueltige explizite CLI/API-
        Alternativen VOR erster Aufloesung ... behalten Vorrang" -- OHNE
        lokales Profil (frischer `Path.home()`, kein `.openwebui_env`,
        `resolve_model_provider` liefert 'legacy') ist ein bereits VOR dem
        ersten Aufruf gesetzter `MMO_SIM_PERSONA_API_BASE_URL` KEIN Konflikt
        mit einer lokalen Wahl (es gibt keine) -- `_maybe_default_local_
        tokenhost_persona_env` muss `False` liefern (branch (a), Zeilen
        ~230-252), OHNE den Override zu beruehren. Treibt zusaetzlich die
        ECHTE Folgefunktion (`default_persona_driver_factory`), um zu
        bestaetigen, dass der Override auch tatsaechlich VERWENDET wird
        (nicht nur unveraendert im Environment steht)."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o6b-no-local-profile-"))
        self._tmp_dirs.append(tmp_home)
        override_url = "http://127.0.0.1:29998/v1"
        os.environ["MMO_SIM_PERSONA_API_BASE_URL"] = override_url
        os.environ["MMO_SIM_PERSONA_API_KEY"] = "override-key-not-secret"
        os.environ["MMO_SIM_PERSONA_API_MODEL"] = "override-model"
        with mock.patch.object(Path, "home", return_value=tmp_home):
            result = factories_mod._maybe_default_local_tokenhost_persona_env()
            self.assertFalse(result, "ohne lokale Wahl darf die Funktion nichts setzen/ueberschreiben.")
            self.assertEqual(
                os.environ.get("MMO_SIM_PERSONA_API_BASE_URL"), override_url,
                "der bereits gesetzte explizite Override darf NICHT veraendert werden.",
            )

            data_dir = Path(tempfile.mkdtemp(prefix="o6b-data-dir-"))
            self._tmp_dirs.append(data_dir)
            factory = factories_mod.default_persona_driver_factory(data_dir)
            driver = factory("persona_override_precedence")
        self.assertEqual(
            driver.config.base_url, override_url,
            "der VOR der ersten Aufloesung gesetzte explizite Override muss tatsaechlich "
            "verwendet werden -- nicht nur unveraendert im Environment uebrig bleiben.",
        )
        self.assertTrue(driver.is_dollar_billed, "ohne lokale Wahl bleibt der Cloud-Billingdefault.")

    def test_invalid_explicit_persona_max_tokens_holds_without_provider_switch(self):
        """O6-B.B3 (RELEASE-CASES.json): "ungueltige explizite Alternativen
        halten ohne Providerwechsel" -- `MMO_SIM_PERSONA_API_MAX_TOKENS` auf
        einen nicht lesbaren Wert gesetzt (factories.py:407-414) wirft einen
        spezifischen `ValueError` ("fail-closed, kein stiller Fallback auf
        den Default") -- NICHT den generischen 'nicht konfiguriert'-
        `RuntimeError`, der einen stillen Providerwechsel (z.B. auf
        'nicht konfiguriert'/einen anderen Zweig) bedeuten wuerde. Die
        explizite API-Wahl (`use_api`) bleibt dabei die ganze Zeit aktiv --
        kein Wechsel auf CLI/kein Wechsel auf 'nicht konfiguriert'."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o6b-invalid-max-tokens-"))
        self._tmp_dirs.append(tmp_home)
        os.environ["MMO_SIM_PERSONA_API_BASE_URL"] = FAKE_LOCAL_BASE
        os.environ["MMO_SIM_PERSONA_API_KEY"] = FAKE_LOCAL_TOKEN
        os.environ["MMO_SIM_PERSONA_API_MODEL"] = FAKE_LOCAL_MODEL
        os.environ["MMO_SIM_PERSONA_API_MAX_TOKENS"] = "not-a-number"
        data_dir = Path(tempfile.mkdtemp(prefix="o6b-data-dir-invalid-"))
        self._tmp_dirs.append(data_dir)
        with mock.patch.object(Path, "home", return_value=tmp_home):
            factory = factories_mod.default_persona_driver_factory(data_dir)
            with self.assertRaises(ValueError) as ctx:
                factory("persona_invalid_limit")
        self.assertIn("MMO_SIM_PERSONA_API_MAX_TOKENS", str(ctx.exception))
        self.assertNotIsInstance(
            ctx.exception, RuntimeError,
            "ein ungueltiger expliziter Wert haelt am spezifischen ValueError, kein "
            "generischer 'nicht konfiguriert'-Providerwechsel.",
        )

    def test_invalid_explicit_persona_override_leaves_no_global_billing_state_for_next_construction(self):
        """O6-B.B3-Nachzug: "keine globale Billingumschaltung" -- nach dem
        obigen gehaltenen `ValueError` (EINE Persona-Instanz) darf eine
        ANSCHLIESSEND konstruierte, unabhaengige zweite Persona mit
        gueltiger Konfiguration und `MMO_SIM_PERSONA_API_DOLLAR_BILLED=0`
        trotzdem korrekt lokal/unpriced konstruiert werden -- kein
        globaler Zustand aus dem gescheiterten ersten Versuch blutet durch."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o6b-billing-leak-"))
        self._tmp_dirs.append(tmp_home)
        data_dir = Path(tempfile.mkdtemp(prefix="o6b-data-dir-leak-"))
        self._tmp_dirs.append(data_dir)
        with mock.patch.object(Path, "home", return_value=tmp_home):
            os.environ["MMO_SIM_PERSONA_API_BASE_URL"] = FAKE_LOCAL_BASE
            os.environ["MMO_SIM_PERSONA_API_KEY"] = FAKE_LOCAL_TOKEN
            os.environ["MMO_SIM_PERSONA_API_MODEL"] = FAKE_LOCAL_MODEL
            os.environ["MMO_SIM_PERSONA_API_MAX_TOKENS"] = "not-a-number"
            os.environ["MMO_SIM_PERSONA_API_DOLLAR_BILLED"] = "0"
            factory = factories_mod.default_persona_driver_factory(data_dir)
            with self.assertRaises(ValueError):
                factory("persona_first_failed")

            os.environ["MMO_SIM_PERSONA_API_MAX_TOKENS"] = "250"
            driver = factory("persona_second_valid")
        self.assertFalse(driver.is_dollar_billed, "die zweite, gueltige Konstruktion bleibt instanzgebunden lokal/unpriced.")
        self.assertEqual(driver.config.max_tokens, 250)
        self.assertEqual(driver.config.model, FAKE_LOCAL_MODEL)


# ─── O2-A (RELEASE-CASES.json): zustandsbehaftetes In-Memory-OWUI-Double,
# ALLE 5 echten Aufrufer (run_setup, _finish_installed_connection [beide
# Aufrufstellen], complete_orphaned_kb_install, run_sync) GEGEN DENSELBEN
# ueber alle Aufrufe hinweg ERHALTENEN Zustand. REINER Loopback-Fake (kein
# echter Netz-/OWUI-Kontakt) an derselben `urllib.request.urlopen`-
# Transportgrenze wie die bereits bestehenden Doubles in dieser Datei --
# deckt zusaetzlich Connection-/Knowledge-/File-/Model-CRUD ab.

def _o2a_extract_upload_filename(body: bytes) -> str:
    m = re.search(rb'filename="([^"]+)"', body or b"")
    return m.group(1).decode("utf-8") if m else ""


def _o2a_extract_upload_content(body: bytes, content_type: str) -> bytes:
    m = re.search(r"boundary=([^\s;]+)", content_type or "")
    if not m:
        return b""
    marker = b"--" + m.group(1).encode()
    parts = (body or b"").split(marker)
    if len(parts) < 2:
        return b""
    idx = parts[1].find(b"\r\n\r\n")
    if idx == -1:
        return b""
    content = parts[1][idx + 4:]
    return content[:-2] if content.endswith(b"\r\n") else content


class _O2AResponse:
    def __init__(self, status: int, body):
        self.status = status
        self._body = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False


class _StatefulOwuiDouble:
    """O2-A: zustandsbehaftetes In-Memory-OWUI-Double -- `__call__` ist
    direkt als `urllib.request.urlopen`-Ersatz patchbar (identisches
    Muster zu `_o6a_router` in `test_local_tokenhost_profile_2026_11_14.py`
    und dem O2-B.B1-Kettentest), deckt aber zusaetzlich die GESAMTE lokale
    OWUI-Oberflaeche ab, die `run_setup`/`complete_orphaned_kb_install`/
    `run_sync`/`_ensure_owui_local_connection`/`_rewire_preset_base_model_
    local` tatsaechlich beruehren: Connection-Config (`/openai/config`,
    `/openai/config/update`), Verify (`/openai/verify`), Model-Presets
    (`/api/v1/models/*`, `/api/models`), Knowledge Bases (`/api/v1/
    knowledge/*`) und Files (`/api/v1/files/*`), content-hash-basiertes
    Duplicate-Verhalten wie `test_f1_n5_1b_unclear_file_list_halts_2026_
    11_10.py:_ContentHttpDouble`. Da `urlopen` GLOBAL gepatcht wird
    (nicht nur `APIClient._request`), laeuft JEDER echte Aufrufer --
    egal ob er ueber eine eigene `APIClient`-Instanz (auch aus einer
    ANDEREN per-Pfad geladenen `setup.py`-Modulkopie, z.B. `launcher_
    mod.setup_module`) oder ueber die rohe `_ensure_owui_local_
    connection`-`_api()`-Hilfsfunktion geht -- gegen DENSELBEN Zustand."""

    def __init__(self, owui_url: str):
        self.owui_url = owui_url.rstrip("/")
        self.connection = {
            "ENABLE_OPENAI_API": True, "OPENAI_API_BASE_URLS": [],
            "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {},
        }
        self.models: dict = {}
        self.knowledge: dict = {}  # kb_id -> {"name":.., "description":..}
        self.files: dict = {}      # file_id -> content bytes
        self.filenames: dict = {}  # file_id -> filename
        self.collection_of: dict = {}  # file_id -> kb_id | None
        self.linked: set = set()
        self._next_file_id = 100
        self._next_kb_id = 100
        self.calls: list = []
        self._stale_readback_for: set = set()
        self._stale_before_update: dict = {}
        self.verify_models: list = []

    @staticmethod
    def _hash(content: bytes) -> str:
        return hashlib.sha256(content or b"").hexdigest()

    def set_stale_readback(self, preset_id: str) -> None:
        """A3-Gegenprobe-Unterstuetzung: der naechste Re-GET fuer
        `preset_id` NACH einem Update liefert weiterhin den VOR diesem
        Update gueltigen Snapshot (Replikationsverzoegerung/Race)."""
        self._stale_readback_for.add(preset_id)

    def __call__(self, req, timeout=None, context=None):
        full = req.full_url
        if not full.startswith(self.owui_url):
            raise AssertionError(f"O2A-Double: unerwartete Fremd-URL (kein echtes Netz erwartet): {full}")
        path = full[len(self.owui_url):]
        method = req.get_method()
        raw = req.data
        if raw is None:
            data = None
        else:
            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
                data = raw  # multipart/form-data -- bleibt roh fuer den Upload-Zweig.
        content_type = req.get_header("Content-type", "application/json") or "application/json"
        self.calls.append((method, path))
        status, body = self._dispatch(method, path, data, content_type)
        return _O2AResponse(status, body)

    def _dispatch(self, method: str, path: str, data, content_type: str):
        # ── health/auth passthroughs ────────────────────────────────────
        if method == "GET" and path == "/api/config":
            return 200, b"{}"
        if method == "GET" and path == "/api/v1/files/":
            return 200, {"items": [], "total": 0}
        if method == "GET" and path == "/api/models":
            return 200, {"data": [{"id": pid} for pid in self.models]}
        if method == "POST" and path == "/api/chat/completions":
            return 200, {"choices": [{"message": {"content": "ok"}}]}

        # ── Connection-Config (roh von _ensure_owui_local_connection) ───
        if method == "GET" and path == "/openai/config":
            return 200, dict(self.connection)
        if method == "POST" and path == "/openai/config/update":
            payload = data if isinstance(data, dict) else {}
            self.connection = {
                "ENABLE_OPENAI_API": payload.get("ENABLE_OPENAI_API", True),
                "OPENAI_API_BASE_URLS": list(payload.get("OPENAI_API_BASE_URLS") or []),
                "OPENAI_API_KEYS": list(payload.get("OPENAI_API_KEYS") or []),
                "OPENAI_API_CONFIGS": dict(payload.get("OPENAI_API_CONFIGS") or {}),
            }
            return 200, {}
        if method == "POST" and path == "/openai/verify":
            return 200, {"data": [{"id": m} for m in self.verify_models]}

        # ── Models/Presets ──────────────────────────────────────────────
        if method == "GET" and path.startswith("/api/v1/models/model?id="):
            pid = urllib.parse.unquote(path.split("=", 1)[1])
            if pid in self._stale_readback_for:
                self._stale_readback_for.discard(pid)
                stale = self._stale_before_update.get(pid)
                if stale is not None:
                    return 200, dict(stale)
            preset = self.models.get(pid)
            if preset is None:
                return 404, {"detail": "not found"}
            return 200, dict(preset)
        if method == "POST" and path == "/api/v1/models/create":
            pid = data["id"]
            self.models[pid] = dict(data)
            return 200, {"id": pid}
        if method == "POST" and path == "/api/v1/models/model/update":
            pid = data["id"]
            if pid in self._stale_readback_for:
                if not hasattr(self, "_stale_before_update"):
                    self._stale_before_update = {}
                self._stale_before_update[pid] = dict(self.models.get(pid) or {})
            self.models[pid] = dict(data)
            return 200, {"id": pid}

        # ── Knowledge Bases ──────────────────────────────────────────────
        if method == "GET" and path == "/api/v1/knowledge/":
            items = [{"id": kid, "name": kb["name"]} for kid, kb in self.knowledge.items()]
            return 200, {"items": items, "total": len(items)}
        if method == "POST" and path == "/api/v1/knowledge/create":
            self._next_kb_id += 1
            kb_id = f"kb-o2a-{self._next_kb_id}"
            self.knowledge[kb_id] = {"name": data.get("name"), "description": data.get("description")}
            return 200, {"id": kb_id}
        if method == "POST" and path.startswith("/api/v1/knowledge/") and path.endswith("/file/add"):
            kb_id = path.split("/")[-3]
            fid = (data or {}).get("file_id")
            content = self.files.get(fid, b"")
            h = self._hash(content)
            colliding = [
                f for f in self.linked
                if f != fid and self.collection_of.get(f) == kb_id and self._hash(self.files.get(f, b"")) == h
            ]
            if colliding:
                return 400, {"detail": "400: Duplicate content detected"}
            self.linked.add(fid)
            self.collection_of[fid] = kb_id
            return 200, {}
        if method == "POST" and path.startswith("/api/v1/knowledge/") and path.endswith("/file/remove"):
            kb_id = path.split("/")[-3]
            fid = (data or {}).get("file_id")
            self.linked.discard(fid)
            if self.collection_of.get(fid) == kb_id:
                self.collection_of[fid] = None
            return 200, {}
        if method == "GET" and path.startswith("/api/v1/knowledge/"):
            kb_id = urllib.parse.unquote(path.rsplit("/", 1)[-1])
            if kb_id not in self.knowledge:
                return 404, {"detail": "not found"}
            member_files = [{"id": fid} for fid in self.files if self.collection_of.get(fid) == kb_id]
            return 200, {"files": member_files}

        # ── Files ─────────────────────────────────────────────────────
        if method == "GET" and path.startswith("/api/v1/files/?page="):
            page = int(path.rsplit("=", 1)[1])
            if page > 1:
                return 200, {"items": [], "total": 0}
            items = [
                {"id": fid, "filename": self.filenames[fid],
                 "meta": {"collection_name": self.collection_of.get(fid), "file_hash": self._hash(self.files[fid])}}
                for fid in self.files
            ]
            return 200, {"items": items, "total": len(items)}
        if method == "POST" and path == "/api/v1/files/":
            fname = _o2a_extract_upload_filename(data if isinstance(data, bytes) else b"")
            content = _o2a_extract_upload_content(data if isinstance(data, bytes) else b"", content_type)
            self._next_file_id += 1
            fid = f"file-o2a-{self._next_file_id}"
            self.files[fid] = content
            self.filenames[fid] = fname
            self.collection_of.setdefault(fid, None)
            return 200, {"id": fid}
        if method == "DELETE" and path.startswith("/api/v1/files/"):
            fid = path.rsplit("/", 1)[1]
            if fid not in self.files:
                return 400, {"detail": "Not found"}
            del self.files[fid]
            self.filenames.pop(fid, None)
            self.collection_of.pop(fid, None)
            self.linked.discard(fid)
            return 200, {}
        # UPD-1: `wait_for_file_ready` fragt vor jedem Link-Versuch
        # `GET /api/v1/files/{id}` ab (kein `?page=`) -- bereits in `self.
        # files` liegender Inhalt gilt sofort als fertig extrahiert (dieser
        # Double modelliert keine Verarbeitungsverzögerung).
        if method == "GET" and path.startswith("/api/v1/files/") and "?" not in path and path != "/api/v1/files/":
            fid = path.rsplit("/", 1)[-1]
            if fid in self.files:
                return 200, {"id": fid, "data": {"content": "ready"}}
            return 404, {"detail": "not found"}
        return 404, {"detail": f"O2A-Double: unbehandelt {method} {path}"}


def _o2a_build_repo(tmp: Path, *, filenames=("a.md",)) -> None:
    (tmp / "kb").mkdir()
    for i, name in enumerate(filenames):
        (tmp / "kb" / name).write_text(f"Wissensinhalt {i}", encoding="utf-8")
    (tmp / "meta").mkdir()
    (tmp / "meta" / "masterprompt.md").write_text("Du bist die SL (O2-A).", encoding="utf-8")


class O2AStatefulDoubleAllFiveCallersTests(unittest.TestCase):
    """O2-A (RELEASE-CASES.json): ALLE 5 echten Aufrufer (Fresh/create=
    `run_setup`, Installed+Auth-Recheck=`launcher._finish_installed_
    connection` [beide Aufrufstellen dispatchen auf dieselbe Funktion],
    Orphan=`complete_orphaned_kb_install`, Sync=`run_sync`) GEGEN
    DENSELBEN zustandsbehafteten OWUI-Double, EIN zusammenhaengender
    Ablauf (kein Helper-only-Stub je Aufrufer)."""

    def setUp(self):
        self._tmp_dirs: list[Path] = []
        self._env_backup = dict(os.environ)

    def tearDown(self):
        for d in self._tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        os.environ.clear()
        os.environ.update(self._env_backup)

    def _tmp_dir(self, prefix: str) -> Path:
        d = Path(tempfile.mkdtemp(prefix=f"o2a-{prefix}-"))
        self._tmp_dirs.append(d)
        return d

    def test_all_five_real_callers_same_double_own_preset_foreign_bestand_unchanged(self):
        owui_url = "http://127.0.0.1:19090"
        owui_key = "owui-o2a-key-not-secret"
        preset_id = "zeitriss-o2a-preset"
        os.environ["OPENWEBUI_URL"] = owui_url
        os.environ["OPENWEBUI_API_KEY"] = owui_key

        repo = self._tmp_dir("repo")
        _o2a_build_repo(repo, filenames=("a.md", "b.md"))
        cfg = {
            "project": "O2AProj", "kb_name": "O2AProj Wissensspeicher",
            "masterprompt": "meta/masterprompt.md", "params": {}, "suggestions": ["Start"],
            "default_variant": "default",
            "variants": {"default": {
                "preset_id": preset_id, "preset_name": "O2AProj", "cache": False,
                "model": "openrouter/deepseek/deepseek-v3.2",
            }},
        }
        profile = lmp.LocalModelProfile(
            base_url=FAKE_LOCAL_BASE, model=FAKE_LOCAL_MODEL, api_key=FAKE_LOCAL_TOKEN,
            owui_base_url=None, gm_max_tokens=512, persona_max_tokens=120,
        )
        tmp_home = self._tmp_dir("home")
        env_path = tmp_home / ".openwebui_env"
        self.assertTrue(setup_mod._update_env_file_preserving(
            env_path, lmp.build_local_profile_updates(
                base_url=profile.base_url, model=profile.model, api_key=profile.api_key,
                gm_max_tokens=profile.gm_max_tokens, persona_max_tokens=profile.persona_max_tokens,
            ),
        ))

        double = _StatefulOwuiDouble(owui_url)
        # Fremder Bestand (andere KB/Preset/Datei) -- muss den GESAMTEN
        # Ablauf unten byte-identisch ueberstehen (A2 "fremder Bestand
        # unveraendert").
        double.knowledge["kb-foreign-1"] = {"name": "Fremdes Projekt KB", "description": "nicht unsere"}
        double.files["file-foreign-1"] = b"FREMDER INHALT"
        double.filenames["file-foreign-1"] = "fremd.md"
        double.collection_of["file-foreign-1"] = "kb-foreign-1"
        double.linked.add("file-foreign-1")
        double.models["fremdes-preset"] = {
            "id": "fremdes-preset", "name": "Fremdes Preset", "base_model_id": "openrouter/foreign-model",
            "meta": {"capabilities": {"vision": True}, "knowledge": [{"id": "kb-foreign-1"}]},
            "params": {"system": "Fremd.", "max_tokens": 64000},
        }
        foreign_snapshot = (
            json.dumps(double.models["fremdes-preset"], sort_keys=True),
            dict(double.knowledge["kb-foreign-1"]), double.files["file-foreign-1"],
        )
        # `_verify_owui_connection_route` fragt OWUIs eigenes `/openai/
        # verify` (POST {url,key}) -- die Antwort muss das lokal gewaehlte
        # Modell als erreichbar zeigen, damit der nichtgenerative Verify
        # (echter Produktpfad in run_setup) bestaetigt.
        double.verify_models = [profile.model]

        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch("urllib.request.urlopen", double):
            # ── Caller 1: Fresh/create -- run_setup ─────────────────────
            setup_mod.run_setup(repo, cfg, {"assume_yes": True})

            self.assertIn(preset_id, double.models, "run_setup muss das eigene Preset real anlegen.")
            own_preset = double.models[preset_id]
            self.assertEqual(own_preset["base_model_id"], profile.model, "bewusster lokaler Upstream.")
            self.assertEqual(own_preset["params"]["system"], "Du bist die SL (O2-A).", "aktueller Masterprompt.")
            self.assertEqual(own_preset["params"]["max_tokens"], profile.gm_max_tokens, "strengeres lokales Textlimit.")
            self.assertEqual(own_preset["meta"]["capabilities"], setup_mod.LOCAL_TEXT_ONLY_CAPABILITIES)
            own_kb_ids = {k["id"] for k in own_preset["meta"]["knowledge"]}
            self.assertEqual(len(own_kb_ids), 1)
            own_kb_id = next(iter(own_kb_ids))
            self.assertIn(own_kb_id, double.knowledge, "eigenes, aktuelles KB.")
            own_files = {fid for fid in double.files if self.collection_of_matches(double, fid, own_kb_id)}
            self.assertEqual(len(own_files), 2, "beide lokalen Wissensdateien real hochgeladen+verlinkt.")

            # ── Caller 2/3: Installed + Auth-Recheck -- _finish_installed_
            # connection (dieselbe Funktion, BEIDE echten Aufrufstellen in
            # launcher.py dispatchen hierauf) -- erhaltend, kein Neuaufbau.
            printed: list[str] = []
            with mock.patch.object(launcher_mod, "resolve_model_provider_choice",
                                    return_value=("local", profile, None)), \
                 mock.patch.object(launcher_mod, "print", side_effect=lambda *a, **k: printed.append(" ".join(map(str, a)))):
                launcher_mod._finish_installed_connection(cfg)   # Installed-Aufrufstelle
                launcher_mod._finish_installed_connection(cfg)   # Auth-Recheck-Aufrufstelle
            self.assertFalse(
                any("nicht bestätigt" in p or "unvollständig" in p for p in printed),
                f"beide Aufrufstellen muessen erhaltend bestaetigen, nicht halten: {printed}",
            )
            self.assertEqual(
                double.models[preset_id]["base_model_id"], profile.model,
                "Installed/Auth-Recheck duerfen den bereits korrekten Upstream nicht verlieren.",
            )

            # ── Caller 4: Orphan -- complete_orphaned_kb_install auf der
            # EIGENEN, bereits von run_setup befuellten KB (bereits
            # synchron -- bestaetigt per Content-Hash, kein Re-Upload).
            uploaded_before = len(double.files)
            ok = setup_mod.complete_orphaned_kb_install(repo, cfg, own_kb_id)
            self.assertTrue(ok, "Orphan-Ergaenzung auf bereits synchroner KB muss abschliessen.")
            self.assertEqual(len(double.files), uploaded_before, "kein unnoetiger Re-Upload bei bereits synchronem Bestand.")

            # ── Caller 5: Sync -- run_sync auf demselben Preset/derselben KB.
            sync_cfg = dict(cfg, default_variant="default")
            buf_calls_before = len(double.calls)
            setup_mod.run_sync(repo, sync_cfg, {"no_verify": True, "assume_yes": True})
            self.assertGreater(len(double.calls), buf_calls_before, "run_sync muss real gegen den Double laufen.")
            self.assertEqual(
                double.models[preset_id]["base_model_id"], profile.model,
                "run_sync darf den lokalen Upstream nicht veraendern.",
            )

        # Fremder Bestand byte-identisch VOR/NACH dem gesamten Ablauf.
        self.assertEqual(json.dumps(double.models["fremdes-preset"], sort_keys=True), foreign_snapshot[0])
        self.assertEqual(double.knowledge["kb-foreign-1"], foreign_snapshot[1])
        self.assertEqual(double.files["file-foreign-1"], foreign_snapshot[2])
        self.assertNotIn("file-foreign-1", json.dumps([c for c in double.calls]))

        # Secrets nie im Aufrufprotokoll.
        self.assertNotIn(FAKE_LOCAL_TOKEN, json.dumps(double.calls))

    @staticmethod
    def collection_of_matches(double: "_StatefulOwuiDouble", fid: str, kb_id: str) -> bool:
        return double.collection_of.get(fid) == kb_id


# ─── G4 (O3-C.C1): echte negative Caller-Batterie ───────────────────────
# Die Helper-Batterie oben (547-592) belegt NUR den direkt gerufenen Helper
# `_verify_owui_connection_route`. Hier laufen dieselben acht Fehlerklassen
# (401, 403, 404, 501, Timeout, leerer Body, falscher Body/falsche
# Modellliste, fehlendes Modell) je an EINEM der zwei wirklichen lokalen
# Setup-/Fortsetzungsaufrufer -- enge Zuordnung, keine 2x8-Matrix:
#   - `run_setup` -> `/openai/verify` (Route-Verify, setup.py ~5220):
#     401, 403, Timeout, falscher Body/falsche Modellliste.
#   - `_finish_installed_connection` -> Connection (`_ensure_owui_local_
#     connection`, `/openai/config`, launcher.py:709): 404, leerer Body.
#   - `_finish_installed_connection` -> Rewire (`_rewire_preset_base_
#     model_local`, Model-GET/Update, launcher.py:713): fehlendes Modell,
#     501.
# Produktive Connection-/Verify-/Rewirelogik und Rueckgabebehandlung laufen
# REAL; nur der HTTP-Transportrand (`urllib.request.urlopen`) ist gedoubelt.
# Die Providerwahl selbst (`resolve_model_provider`/`resolve_model_provider_
# choice`) wird auf ('local', profile, None) fixiert -- derselbe bereits
# etablierte Mockpunkt wie im positiven Mehrcallertest oben fuer den
# launcher-Aufrufer (`O2AStatefulDoubleAllFiveCallersTests`); das ist die
# Providerwahl, nicht die hier geprüfte Verify-/Connection-/Rewirelogik.


class LocalTokenhostNegativeCallerTests(unittest.TestCase):
    """01_NATIVER_AUFTRAG.md §F / 02_ABNAHME_UND_RUECKGABE.md §3 (G4): jede
    geforderte Fehlerklasse am wirklichen lokalen Caller, tatsaechlicher
    Fehlerpunkt, sichtbarer HOLD/Stopp und KEINE Erfolgs-/Probeweiter-
    leitung -- ein direktes False/None des Verifyhelpers allein (s. oben,
    547-592) reicht dafuer nicht."""

    def setUp(self):
        self._tmp_dirs: list[Path] = []
        self._env_backup = dict(os.environ)

    def tearDown(self):
        for d in self._tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        os.environ.clear()
        os.environ.update(self._env_backup)

    def _tmp_dir(self, prefix: str) -> Path:
        d = Path(tempfile.mkdtemp(prefix=f"o3c-{prefix}-"))
        self._tmp_dirs.append(d)
        return d

    # ── Caller 1: run_setup -> /openai/verify ─────────────────────────

    def _g4_run_setup_script(self, verify_final):
        """Die ersten fuenf Antworten sind die erfolgreichen Vorgaenger
        (Health, Auth, Connection GET/POST/Readback-GET) -- identisch zum
        Erfolgspfad in `test_ensure_local_connection_creates_with_separate_
        local_token` oben. Erst die SECHSTE (`/openai/verify`) traegt die
        injizierte Fehlerklasse -- der Fehler darf nicht unbemerkt schon
        vorher (Healthcheck/Auth/Connection) auftreten."""
        return _UrlopenScript([
            (200, {}),                                                 # 1) GET /api/config (check_health)
            (200, {}),                                                 # 2) GET /api/v1/files/ (check_auth)
            (200, {"OPENAI_API_BASE_URLS": [], "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {}}),  # 3) Connection GET
            (200, {}),                                                 # 4) Connection POST update
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": {"0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL]}},
                   "ENABLE_OPENAI_API": True}),                         # 5) Connection Readback GET
            verify_final,                                              # 6) POST /openai/verify -- injizierte Klasse
        ])

    def _g4_run_setup_with(self, verify_final):
        """Treibt `run_setup` real bis exakt zum `/openai/verify`-Aufruf;
        liefert (SystemExit-Code, zusammengefuehrter stdout+stderr-Text,
        Script)."""
        repo = self._tmp_dir("repo")
        _o2a_build_repo(repo)
        cfg = {
            "project": "G4Proj", "kb_name": "G4Proj Wissensspeicher",
            "masterprompt": "meta/masterprompt.md", "params": {}, "suggestions": ["Start"],
            "default_variant": "default",
            "variants": {"default": {"preset_id": FAKE_PRESET_ID, "preset_name": "G4Proj", "cache": False}},
        }
        tmp_home = self._tmp_dir("home")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        script = self._g4_run_setup_script(verify_final)
        buf = io.StringIO()
        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch.object(setup_mod, "resolve_model_provider", return_value=("local", _profile(), None)), \
             mock.patch.object(setup_mod, "_auto_load_owui_env", return_value=False), \
             mock.patch("urllib.request.urlopen", script):
            with redirect_stdout(buf), redirect_stderr(buf):
                with self.assertRaises(SystemExit) as ctx:
                    setup_mod.run_setup(repo, cfg, {"assume_yes": True})
            exit_code = ctx.exception.code
        return exit_code, buf.getvalue(), script

    def _assert_run_setup_halted_at_verify(self, exit_code, out, script):
        self.assertEqual(exit_code, 1, "run_setup muss bei nicht bestaetigtem Verify mit Exitcode 1 halten.")
        self.assertIn(
            "kein Fallback, kein Completion-Versuch", out,
            "die reale run_setup-Fehlermeldung am Verify-Halt muss erscheinen (nicht nur ein generischer Halt).",
        )
        self.assertNotIn("Setup abgeschlossen", out, "kein Erfolgsschild nach einem nicht bestaetigten Verify.")
        self.assertEqual(
            len(script.calls), 6,
            "Fehler darf nicht unbemerkt schon beim Healthcheck/Auth/Connection auftreten -- "
            "muss genau am sechsten (Verify-)Aufruf landen, nicht frueher.",
        )
        last = script.calls[-1]
        self.assertEqual(last["method"], "POST")
        self.assertTrue(last["url"].endswith("/openai/verify"), last["url"])
        self.assertNotIn(
            "/chat/completions", json.dumps(script.calls),
            "keine Probe-/Completion-Weiterleitung nach nicht bestaetigtem Verify.",
        )

    def test_run_setup_local_verify_401_403_halts_no_fallback_no_completion(self):
        for code in (401, 403):
            exc = urllib.error.HTTPError(f"{FAKE_OWUI_URL}/openai/verify", code, "err", {}, None)
            exc.read = lambda: b"{}"
            exit_code, out, script = self._g4_run_setup_with(exc)
            self._assert_run_setup_halted_at_verify(exit_code, out, script)

    def test_run_setup_local_verify_timeout_halts_no_fallback_no_completion(self):
        exit_code, out, script = self._g4_run_setup_with(urllib.error.URLError("timed out"))
        self._assert_run_setup_halted_at_verify(exit_code, out, script)

    def test_run_setup_local_verify_malformed_model_list_halts_no_fallback_no_completion(self):
        """'falscher Body bzw. falsche Modellliste': `/openai/verify`
        antwortet 200 mit einem lesbaren, aber NICHT modellistenfoermigen
        Koerper -- derselbe Fall wie im Helpertest `test_verify_local_
        route_none_on_timeout_and_malformed_body` oben, hier aber ueber den
        echten `run_setup`-Aufrufer statt per Direktaufruf des Helpers."""
        exit_code, out, script = self._g4_run_setup_with((200, {"unexpected_shape": True}))
        self._assert_run_setup_halted_at_verify(exit_code, out, script)

    # ── Caller 2: _finish_installed_connection -> Connection/Rewire ───

    def _g4_finish_installed_with(self, config_get_final):
        profile = _profile()
        tmp_home = self._tmp_dir("home")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        cfg = {"variants": {}}
        script = _UrlopenScript([config_get_final])
        printed: list[str] = []
        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch.object(launcher_mod, "resolve_model_provider_choice",
                                return_value=("local", profile, None)), \
             mock.patch("urllib.request.urlopen", script), \
             mock.patch.object(launcher_mod, "print",
                                side_effect=lambda *a, **k: printed.append(" ".join(map(str, a)))):
            launcher_mod._finish_installed_connection(cfg)
        return printed, script

    def _g4_finish_installed_rewire_with(self, rewire_responses):
        profile = _profile()
        tmp_home = self._tmp_dir("home")
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY
        cfg = {"variants": {"default": {"preset_id": FAKE_PRESET_ID, "preset_name": "Proj", "cache": True}}}
        script = _UrlopenScript([
            (200, {"OPENAI_API_BASE_URLS": [], "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {}}),  # Connection GET
            (200, {}),                                                                              # Connection POST
            (200, {"OPENAI_API_BASE_URLS": [FAKE_LOCAL_BASE], "OPENAI_API_KEYS": [FAKE_LOCAL_TOKEN],
                   "OPENAI_API_CONFIGS": {"0": {"enable": True, "model_ids": [FAKE_LOCAL_MODEL]}},
                   "ENABLE_OPENAI_API": True}),                                                      # Connection Readback
            *rewire_responses,
        ])
        printed: list[str] = []
        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch.object(launcher_mod, "resolve_model_provider_choice",
                                return_value=("local", profile, None)), \
             mock.patch("urllib.request.urlopen", script), \
             mock.patch.object(launcher_mod, "print",
                                side_effect=lambda *a, **k: printed.append(" ".join(map(str, a)))):
            launcher_mod._finish_installed_connection(cfg)
        return printed, script

    def _assert_finish_installed_not_confirmed(self, printed, script):
        joined = " ".join(printed)
        self.assertNotIn(
            "aktiv und bestätigt", joined,
            "ohne bestaetigte Connection/Rewire darf _finish_installed_connection NIE "
            "'aktiv und bestätigt' melden.",
        )
        self.assertNotIn("/chat/completions", json.dumps(script.calls), "keine Probe-/Completion-Weiterleitung.")

    def test_finish_installed_connection_owui_config_404_holds_no_active_confirmation(self):
        """404 an Connection: `GET /openai/config` (launcher.py:709 ->
        setup.py:2193) scheitert mit HTTP 404 -- `_ensure_owui_local_
        connection` haelt VOR jeder Mutation (kein POST), `_finish_
        installed_connection` kehrt OHNE 'aktiv und bestätigt' zurueck."""
        exc = urllib.error.HTTPError(f"{FAKE_OWUI_URL}/openai/config", 404, "err", {}, None)
        exc.read = lambda: b"{}"
        printed, script = self._g4_finish_installed_with(exc)
        self._assert_finish_installed_not_confirmed(printed, script)
        joined = " ".join(printed)
        self.assertIn("nicht bestätigt werden", joined)
        self.assertEqual(len(script.calls), 1, "Halt am ersten (GET /openai/config) Aufruf -- kein POST.")
        self.assertEqual(script.calls[0]["method"], "GET")

    def test_finish_installed_connection_owui_config_empty_body_holds_no_active_confirmation(self):
        """'leerer Body' an Connection: `/openai/config` antwortet 200,
        aber der Koerper ist kein brauchbares Config-Objekt (JSON `null`
        statt eines dicts) -- `_ensure_owui_local_connection`s eigene
        `isinstance(data, dict)`-Pruefung (setup.py:2194) muss das wie
        einen unerreichbaren Endpoint behandeln, NICHT wie eine leere,
        aber gueltige Connection-Liste (die mit `{}` bereits an anderer
        Stelle in dieser Datei als Erfolgsfall gilt, s. Fresh-Case oben)."""
        printed, script = self._g4_finish_installed_with((200, None))
        self._assert_finish_installed_not_confirmed(printed, script)
        joined = " ".join(printed)
        self.assertIn("nicht bestätigt werden", joined)
        self.assertEqual(len(script.calls), 1)

    def test_finish_installed_connection_owui_config_raw_empty_bytes_holds_no_active_confirmation(self):
        """G4-Praezisierung (01_GENERALREVIEW.md §5/03_ABNAHME_UND_RUECKGABE.md
        §2 O3-C.C1): derselbe Connection-GET-Fall wie direkt oben, aber mit
        TATSAECHLICH leeren Responsebytes (`b""`) statt der JSON-serialisierten
        `null`-Fiktion -- belegt, dass `_ensure_owui_local_connection`s
        `json.loads(raw)`-Fehlerpfad (setup.py ~2180: `except
        json.JSONDecodeError: return resp.status, raw.decode(...)`) echte
        Leerbytes auf dieselbe `isinstance(data, dict)`-Ablehnung (setup.py:2193)
        und denselben sichtbaren Nicht-dict-HOLD fuehrt wie der `null`-Fall --
        kein neuer Produktfehlerclaim, keine neue Callermatrix."""
        printed, script = self._g4_finish_installed_with((200, _RawBytes(b"")))
        self._assert_finish_installed_not_confirmed(printed, script)
        joined = " ".join(printed)
        self.assertIn("nicht bestätigt werden", joined)
        self.assertEqual(len(script.calls), 1)

    def test_finish_installed_connection_rewire_missing_model_holds_no_active_confirmation(self):
        """'fehlendes Modell' an Rewire: Connection ist bestaetigt, aber
        das Preset selbst ist am Rewire-Ziel nicht (mehr) vorhanden
        (`client.get_model(preset_id)` -> HTTP 404, setup.py:2391f) --
        `_rewire_preset_base_model_local` meldet 'nicht gefunden — Setup
        zuerst.' statt einer Erfolgsmeldung; `_finish_installed_
        connection` kehrt OHNE 'aktiv und bestätigt' zurueck."""
        exc = urllib.error.HTTPError(f"{FAKE_OWUI_URL}/api/v1/models/model", 404, "err", {}, None)
        exc.read = lambda: b"{}"
        printed, script = self._g4_finish_installed_rewire_with([exc])
        self._assert_finish_installed_not_confirmed(printed, script)
        joined = " ".join(printed)
        self.assertIn("unvollständig", joined)
        self.assertIn("nicht gefunden", joined)

    def test_finish_installed_connection_rewire_update_501_holds_no_active_confirmation(self):
        """501 an Rewire: Connection ist bestaetigt, das Preset existiert
        (`get_model` 200), aber der eigentliche Update-Request (`POST
        /api/v1/models/model/update`, setup.py:2437/821-831) scheitert mit
        HTTP 501 -- `upsert_model` meldet `ok=False`, Rewire bleibt
        unvollstaendig; `_finish_installed_connection` kehrt OHNE 'aktiv
        und bestätigt' zurueck."""
        existing_preset = {
            "id": FAKE_PRESET_ID, "base_model_id": "openrouter/old-cloud-model",
            "meta": {"capabilities": {"vision": True}},
            "params": {"max_tokens": 64000, "system": "Du bist die SL."},
        }
        exc = urllib.error.HTTPError(f"{FAKE_OWUI_URL}/api/v1/models/model/update", 501, "err", {}, None)
        exc.read = lambda: b"{}"
        printed, script = self._g4_finish_installed_rewire_with([
            (200, existing_preset),                      # 1) get_model (initial read)
            (200, {"data": [{"id": FAKE_PRESET_ID}]}),    # 2) list_models (exists-check)
            exc,                                          # 3) POST update -> 501
        ])
        self._assert_finish_installed_not_confirmed(printed, script)
        joined = " ".join(printed)
        self.assertIn("unvollständig", joined)
        self.assertIn("Update fehlgeschlagen", joined)


if __name__ == "__main__":
    # Von der Prozessbruecke gestarteter frischer Kindinterpreter: echten
    # Koerper ausfuehren und Ergebnis als Marker auf STDOUT zurueckgeben.
    # Standalone/run_all.py (ohne Kindmarke) laufen unveraendert nativ.
    if os.environ.get(_support_mod._UNITTEST_CHILD_ENV) == "1":
        raise SystemExit(_support_mod.run_module_as_child(sys.modules[__name__]))
    unittest.main()
