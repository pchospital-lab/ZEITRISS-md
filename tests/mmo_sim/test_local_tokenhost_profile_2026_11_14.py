#!/usr/bin/env python3
"""tests/mmo_sim/test_local_tokenhost_profile_2026_11_14.py — ZR-LOCAL-TOKENHOST-L1,
Offline-Abnahme O1 (Auswahl, Persistenz, Wiederaufnahme) + N4-N2 (API-CONTRACT-
N4N2.md §3: vollstaendige Guard-Gegenproben, Post-Mock-Matrix, Verbrauchs-/
Replay-Pruefung, Validator-Seam-Tests, zwei Kinder mit eigenem env/Kontext und
7-Feld-Reader-Vergleich).

Belegt gegen die echten Produktfunktionen des Worktrees:
  - `scripts/local_model_profile.py` (neuer Daten-/Validierungsresolver)
  - `scripts/setup.py:_read_env_file` / `_update_env_file_preserving`
    (bestehender erhaltender Schreibhelfer, wiederverwendet statt verdoppelt)
  - `scripts/setup.py:resolve_model_provider` / `_home_env_path`
  - `scripts/launcher.py:resolve_model_provider_choice` / `action_rekeys`

IO ausschliesslich an Grenzen kontrolliert: private Tempdateien statt
`~/.openwebui_env`, `getpass.getpass`/`_prompt` monkeygepatcht. Die echte
Nutzerdatei wird in KEINEM Testfall geoeffnet -- `Path.home` wird nur fuer
den einen End-to-End-Test auf ein Tempverzeichnis umgelenkt, alle anderen
Tests uebergeben einen expliziten `env_path`.

unittest.TestCase, `python3 -m unittest discover` faehig; kein Netzwerk-/
Docker-/Modellzugriff."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pwd
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import unittest
import unittest.mock as mock
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
_SETUP_PY = _SCRIPTS_DIR / "setup.py"
_LAUNCHER_PY = _SCRIPTS_DIR / "launcher.py"
_LOCAL_PROFILE_PY = _SCRIPTS_DIR / "local_model_profile.py"
_SL_CLIENT_PY = _REPO_ROOT / "internal" / "qa" / "harness" / "agent_mp" / "sl_client.py"
_SUPPORT_SCRIPT = _HERE / "_local_tokenhost_support_2026_11_14.py"

# N4-N2 (API-CONTRACT-N4N2.md §1.1): Fruehschutz MUSS installiert sein,
# BEVOR irgendein Produktmodul (setup/launcher/local_model_profile) unten
# geladen wird. Diese Datei ist NICHT eingefroren, ruft `bootstrap_isolation`
# aber trotzdem im selben Legacy-Stil wie die eingefrorenen routing/F1-
# Dateien auf (symmetrisch, keine eigene Sonderregel): EINE echte
# Primaerinstallation geschieht AUSSCHLIESSLICH ueber `bootstrap_isolation
# (context=...)` aus Mains `bootstrap_entry.py`, VOR dem Dispatch dieser
# pytest-Datei. Dieser Aufruf hier RUFT NUR DEN BEREITS INSTALLIERTEN
# Primaerguard AB (kein Platzhalterguard, keine Neukonfiguration) -- fehlt
# die vorherige Primaerinstallation, scheitert dieser Aufruf sichtbar mit
# `IsolationBootstrapError` (kein fall-open-Autoload).
import importlib.util as _importlib_util_bootstrap  # noqa: E402

_support_spec = _importlib_util_bootstrap.spec_from_file_location(
    "o1_local_tokenhost_support", _SUPPORT_SCRIPT
)
_support_mod = _importlib_util_bootstrap.module_from_spec(_support_spec)
sys.modules["o1_local_tokenhost_support"] = _support_mod
_support_spec.loader.exec_module(_support_mod)
# Weg 3 (Flo 2026-11-15): Prozessbruecke fuer die gemeinsame unittest-
# Discovery. NUR im echten Koerper-Modus (Standalone/run_all.py als
# `__main__`, Bundle-/Runner-Einstieg, oder von der Bruecke gestarteter
# frischer Kindinterpreter) werden Guard, sys.path-Anpassung UND Produkt-
# importe ausgefuehrt. Im geteilten Elternprozess (`python3 -m unittest -q`)
# bleibt der Import seiteneffektfrei -- kein Guard, kein globaler Patch,
# kein Produktimport -- und stellt nur die schlanke `load_tests`-Bruecke
# bereit, die den echten Koerper im frischen Interpreter ausfuehrt.
_REAL_BODY = (__name__ == "__main__") or _support_mod.is_real_body_env()

if _REAL_BODY:
    # EINE echte Primaerinstallation erfolgt im Bundle ueber
    # `bootstrap_isolation(context=...)` VOR diesem Import; hier wird sie nur
    # wiederverwendet. Ohne Runner (Standalone/run_all/Kind) baut der
    # Self-Bootstrap einen vollstaendigen, validierten PRIVATEN Kontext.
    EARLY_GUARD = _support_mod.self_bootstrap_isolation()

    if str(_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS_DIR))

    # O6-A (RELEASE-CASES.json): `mmo_sim` (das Paket an REPO_ROOT) muss VOR
    # jedem Laden von `setup.py` importiert/gecacht werden -- `setup.py` fuegt
    # sich selbst `scripts/` an sys.path[0] an, was einen SPAETEREN frischen
    # `import mmo_sim` sonst auf das gleichnamige Launcher-Shim
    # `scripts/mmo_sim.py` statt des echten Pakets treffen liesse (identisches
    # Muster zu `test_local_tokenhost_routing_2026_11_14.py`/`_runtime_.../
    # _creation_...`). `_REPO_ROOT` ist hier (anders als in jenen Dateien)
    # bisher NIE auf sys.path gelandet -- ohne diese Zeile waere "mmo_sim"
    # ueberhaupt nicht importierbar.
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from mmo_sim.adapters.gm_owui import GmOwuiTransport  # noqa: E402
    from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver  # noqa: E402
    # G2 (O6-A.A1/A2): die beiden ECHTEN gemeinsamen Default-Factories --
    # kein Hand-Bau von GmOwuiTransport/PersonaApiDriver mit erwartetem
    # `is_dollar_billed` mehr, das Billing MUSS aus der echten Route/
    # Factory-Ableitung stammen (s. `_o6a_run_cycle` unten).
    from mmo_sim.adapters.factories import (  # noqa: E402
        default_gm_transport_factory, default_persona_driver_factory,
    )
    from mmo_sim.adapters import factories as o6a_factories_mod  # noqa: E402

    def _load(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod  # dataclasses-Introspektion braucht den Modulnamen im Registry
        spec.loader.exec_module(mod)
        return mod

    def _o6a_load_mmo_sim_module():
        """G2: laedt `scripts/mmo_sim.py` (den TUI-Shim, NICHT das
        gleichnamige Paket `mmo_sim/`) per explizitem Dateipfad, identische
        Technik wie `test_f1_gm_route_threading_2026_11_09.py:_load_mmo_sim_
        entrypoint` -- `sys.prefix` wird kurz auf das erwartete `.venv`
        gelegt, damit der venv-Bootstrap des Moduls (`ensure_running_in_
        project_venv`) beim Laden als No-Op durchlaeuft statt real `os.execv`/
        `pip install` auszuloesen."""
        spec = importlib.util.spec_from_file_location(
            "o6a_mmo_sim_entrypoint_under_test", _REPO_ROOT / "scripts" / "mmo_sim.py",
        )
        mod = importlib.util.module_from_spec(spec)
        with mock.patch.object(sys, "prefix", str(_REPO_ROOT / ".venv")):
            spec.loader.exec_module(mod)
        return mod

    # B1-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md B1): diese drei `_load`-
    # Aufrufe standen vorher AUSSERHALB dieses Real-Body-Zweigs -- jeder
    # Import dieser Testdatei (auch im geteilten Discovery-Elternprozess,
    # `python3 -m unittest -q`) fuehrte `setup.py`/`launcher.py`/
    # `local_model_profile.py` dadurch real aus (inkl. `setup.py`s
    # sys.path-Mutation und `launcher.py`s stdout/stderr-Konfiguration) --
    # genau der vom General benannte Bruch des Vertrags "kein Produktimport/
    # keine globalen Produktwirkungen im gemeinsamen Elternprozess".
    lmp = _load("o1_local_model_profile_under_test", _LOCAL_PROFILE_PY)
    setup_mod = _load("o1_setup_under_test", _SETUP_PY)
    launcher_mod = _load("o1_launcher_under_test", _LAUNCHER_PY)

    # G3 (01_GENERALREVIEW.md §4 "O6-A-stdout/stderr liegt ... in einem
    # durch tearDown geloeschten Fixtureverzeichnis"): ein BLEIBENDES
    # Evidenzziel innerhalb des bereits vom Guard erlaubten privaten
    # Schreibbereichs dieses Prozesses (`EARLY_GUARD.private_write_roots`)
    # -- NICHT ueber `self._tmp_dir(...)` registriert, also von `tearDown`s
    # `shutil.rmtree`-Schleife unberuehrt. Main/Integrator kopieren diesen
    # Ordner NACH dem Lauf (ausserhalb des Guards) an das dauerhafte
    # Evidenzziel `.../run/evidence/g2/`. Kein neues Repo-File, keine neue
    # Guard-Architektur -- reine Pfadwahl innerhalb der bestehenden Wurzel.
    _G2_EVIDENCE_DIR = Path(EARLY_GUARD.private_write_roots[0]) / "g2-raw-evidence"
    _G2_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    def _persist_g2_raw_channel(label: str, *, stdout: str, stderr: str, meta: dict) -> None:
        """Sichert Rohkanaele + Kontextfelder (context/pid/ppid/argv/cwd/
        env/start/end/exit) EINES tatsaechlichen Kindes zusaetzlich an das
        bleibende Evidenzziel oben -- additiv, ersetzt keine bestehende
        Assertion/Export im ephemeren `exports_dir`."""
        safe = label.replace("/", "_")
        (_G2_EVIDENCE_DIR / f"{safe}.stdout").write_text(stdout or "", encoding="utf-8")
        (_G2_EVIDENCE_DIR / f"{safe}.stderr").write_text(stderr or "", encoding="utf-8")
        (_G2_EVIDENCE_DIR / f"{safe}.meta.json").write_text(
            json.dumps(meta, indent=2, sort_keys=True, default=str), encoding="utf-8",
        )
else:
    # Geteilter Discovery-Elternprozess: nur die Bruecke, kein Koerper.
    load_tests = _support_mod.make_delegating_load_tests(
        __file__, "profile", min_domain_tests=38)
    # B1-Fix: inerte Platzhalter statt echter Produktmodule -- identisches
    # Muster zu `test_local_tokenhost_routing_2026_11_14.py` (dort bereits
    # so gefixt). Klassenkoerper, die `lmp`/`setup_mod`/`launcher_mod` zur
    # Importzeit auswerten, crashen so nicht; echtes Produktverhalten/
    # -import findet im Elternprozess trotzdem nicht statt.
    lmp = setup_mod = launcher_mod = _support_mod.parent_mode_product_stub()

FAKE_BASE_URL = "http://127.0.0.1:18001/v1"
FAKE_MODEL = "nemotron-3-super"
FAKE_TOKEN = "test-local-token-not-secret"  # noqa: S105 -- erkennbar unecht, s. 04


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class _O6AFakeResponse:
    """O6-A: minimale `urllib.request.urlopen`-Antwort (status/read()/
    Context-Manager) -- identische Form zu den `_FakeResponse`-Doubles in
    den anderen tokenhost-Testdateien."""

    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False


class _O6AStatefulOwuiDouble:
    """G2 (O6-A.A1/A2): zustandsbehaftetes In-Memory-OWUI-Double fuer den
    echten Cloud->Local->Cloud-Setup-/Connection-/Rewire-Zyklus -- identisches
    Muster zu `_StatefulOwuiDouble` in
    `test_local_tokenhost_routing_2026_11_14.py` (dort fuer O2-A), hier auf
    GENAU die Raender beschraenkt, die `_ensure_owui_local_connection`/
    `_ensure_owui_litellm_connection`/`_rewire_preset_base_model_local`/
    `_rewire_preset_base_model`/`_verify_owui_connection_route`/
    `_verify_owui_connection_unique_and_enabled`/`APIClient.upsert_model`
    tatsaechlich beruehren. JEDE Zustandsaenderung entsteht ausschliesslich
    aus einem echten `__call__` (also einem echten `urllib.request.urlopen`-
    Request eines produktiven Aufrufers) -- kein Feld wird von aussen direkt
    gesetzt."""

    def __init__(self, owui_url: str):
        self.owui_url = owui_url.rstrip("/")
        self.connection: dict = {
            "ENABLE_OPENAI_API": True, "OPENAI_API_BASE_URLS": [],
            "OPENAI_API_KEYS": [], "OPENAI_API_CONFIGS": {},
        }
        self.models: dict = {}
        self.calls: list[tuple] = []
        # G2 (01_GENERALREVIEW.md §3 "Requestbelege"): zusaetzliche
        # reichhaltige Aufzeichnung je tatsaechlichem Request (Methode/Pfad/
        # Bodymodell/Response/Phase/Rolle, redigiert exportiert) --
        # `self.calls` bleibt fuer die bestehenden Tupel-Assertions
        # unveraendert. `current_phase` wird vom Zyklustreiber
        # (`_o6a_run_cycle`) je Leg gesetzt, NICHT von aussen auf Werte
        # gesetzt, die den Request selbst beeinflussen.
        self.requests: list[dict] = []
        self.current_phase: str | None = None

    def seed_preset(self, preset_id: str, *, base_model_id: str, kb_id: str,
                     system: str = "", max_tokens: int = 64000) -> None:
        """Anfangsfixture (01_NATIVER_AUFTRAG.md §D: "bestehendes eigenes
        Preset mit cache=True, aktueller KB, unveraenderte Preset-ID") --
        NUR der Startzustand, keine Laufzeitmutation."""
        self.models[preset_id] = {
            "id": preset_id, "name": preset_id, "base_model_id": base_model_id,
            "is_active": True,
            "meta": {"capabilities": {"vision": True}, "knowledge": [{"id": kb_id}]},
            "params": {"system": system, "max_tokens": max_tokens},
        }

    def seed_connection(self, *, url: str, key: str, model_ids: list[str],
                         tags: list[str]) -> None:
        """Anfangsfixture fuer einen bereits bestehenden Cloud-/LiteLLM-
        Anschluss ("vorhandener Cloudanschluss/Autowire") -- NUR Startzustand."""
        idx = str(len(self.connection["OPENAI_API_BASE_URLS"]))
        self.connection["OPENAI_API_BASE_URLS"].append(url)
        self.connection["OPENAI_API_KEYS"].append(key)
        self.connection["OPENAI_API_CONFIGS"][idx] = {
            "enable": True, "tags": list(tags), "prefix_id": "",
            "connection_type": "external", "auth_type": "bearer",
            "model_ids": list(model_ids),
        }

    def _pinned_model_ids(self) -> set:
        ids: set = set()
        for cfg in self.connection["OPENAI_API_CONFIGS"].values():
            if cfg.get("enable"):
                ids.update(cfg.get("model_ids") or [])
        return ids

    def __call__(self, req, timeout=None, context=None):
        full = req.full_url
        if not full.startswith(self.owui_url):
            raise AssertionError(f"O6A-Double: unerwartete Fremd-URL (kein echtes Netz erwartet): {full}")
        path = full[len(self.owui_url):]
        method = req.get_method()
        raw = req.data
        if raw is None:
            data = None
        else:
            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
                data = raw
        self.calls.append((method, path))
        status, body = self._dispatch(method, path, data)
        body_bytes = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.requests.append({
            "phase": self.current_phase, "role": "gm", "caller": "owui",
            "method": method, "path": path, "request_body": data,
            "response_status": status, "response_body": body,
            "auth": req.headers.get("Authorization"),
        })
        return _O6AFakeResponse(status, body_bytes)

    def _dispatch(self, method: str, path: str, data):
        # ── Connection-Config (roh von _ensure_owui_local_connection /
        # _ensure_owui_litellm_connection) ──────────────────────────────
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
            # `_verify_owui_connection_route`: nichtgenerativer Check GENAU
            # der per `url`+`key` adressierten Connection -- die zurueck-
            # gegebene "Modell-Liste" sind deren real gepinnte model_ids
            # (aus einer echten vorherigen /openai/config/update-Mutation),
            # kein separat gesetztes Feld.
            payload = data if isinstance(data, dict) else {}
            target_url, target_key = payload.get("url"), payload.get("key")
            urls = self.connection["OPENAI_API_BASE_URLS"]
            keys = self.connection["OPENAI_API_KEYS"]
            matches = [i for i, u in enumerate(urls) if u == target_url]
            if len(matches) != 1:
                return 200, {"data": []}
            idx = matches[0]
            if idx >= len(keys) or keys[idx] != target_key:
                return 200, {"data": []}
            cfg = dict(self.connection["OPENAI_API_CONFIGS"].get(str(idx)) or {})
            if not cfg.get("enable"):
                return 200, {"data": []}
            return 200, {"data": [{"id": m} for m in (cfg.get("model_ids") or [])]}
        # ── aggregiertes Listing (APIClient.upsert_model()s exists-Check
        # UND _wait_for_owui_model_visible): echte Presets UND real
        # gepinnte Backend-Modelle, identisch zu OWUIs eigener Aggregation.
        if method == "GET" and path == "/api/models":
            ids = set(self.models.keys()) | self._pinned_model_ids()
            return 200, {"data": [{"id": m} for m in ids]}
        # ── Models/Presets ──────────────────────────────────────────────
        if method == "GET" and path.startswith("/api/v1/models/model?id="):
            pid = urllib.parse.unquote(path.split("=", 1)[1])
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
            self.models[pid] = dict(data)
            return 200, {"id": pid}
        # ── GM-Chat (sl_client.py/owui_client.py:_post) ──────────────────
        if method == "POST" and path == "/api/chat/completions":
            return 200, {
                "choices": [{"message": {"content": "GM-Antwort (O6-A)."}}],
                "usage": {"prompt_tokens": 7, "completion_tokens": 3},
            }
        return 404, {"detail": f"O6A-Double: unbehandelt {method} {path}"}


class LocalTokenhostProfileTests(unittest.TestCase):
    def setUp(self):
        self._tmp_dirs: list[Path] = []

    def tearDown(self):
        for d in self._tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)

    def _tmp_env_path(self, prefix: str) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix=f"o1-{prefix}-"))
        self._tmp_dirs.append(tmp)
        return tmp / ".fake_openwebui_env"

    def _tmp_dir(self, prefix: str) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix=f"o1-{prefix}-"))
        self._tmp_dirs.append(tmp)
        return tmp

    # ─── B1-Fix: Negativprobe im geteilten Discovery-Elternprozess ──────

    def test_shared_discovery_parent_import_has_no_product_side_effects(self):
        """B1-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md B1): vorher standen
        die drei `_load`-Produktimporte (setup/launcher/local_model_profile)
        AUSSERHALB des `if _REAL_BODY:`-Zweigs -- jeder Import dieser
        Testdatei im geteilten Elternprozess fuehrte sie real aus. Der vom
        General zitierte fruehere Critic-Check ('mmo_sim' in sys.modules)
        deckte das NICHT ab -- diese drei Aliasnamen sind andere Strings.
        Dieser Test importiert die Testdatei frisch in einem SAUBEREN
        Subprozess OHNE jede LTH_*-Bruecken-Variable (also im geteilten-
        Elternprozess-/Stub-Zweig) und prueft direkt:
          (a) keiner der drei Alias-Modulnamen landet in sys.modules,
          (b) sys.path waechst nicht (setup.py/das `if _REAL_BODY:`-
              sys.path.insert fuer scripts/ und REPO_ROOT laufen nicht),
          (c) `sys.stdout`/`sys.stderr` werden nicht umkonfiguriert
              (launcher.py 49-53)."""
        probe_script = (
            "import sys, json\n"
            "aliases = ('o1_local_model_profile_under_test', 'o1_setup_under_test', 'o1_launcher_under_test')\n"
            "path_before = list(sys.path)\n"
            "reconfigure_calls = {'n': 0}\n"
            "_orig_out, _orig_err = sys.stdout.reconfigure, sys.stderr.reconfigure\n"
            "def _spy(*a, **k):\n"
            "    reconfigure_calls['n'] += 1\n"
            "sys.stdout.reconfigure = _spy\n"
            "sys.stderr.reconfigure = _spy\n"
            "import importlib.util\n"
            f"spec = importlib.util.spec_from_file_location('profile_negative_probe_mod', {str(_HERE / 'test_local_tokenhost_profile_2026_11_14.py')!r})\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            "result = {\n"
            "    'real_body': mod._REAL_BODY,\n"
            "    'leaked_aliases': [n for n in aliases if n in sys.modules],\n"
            "    'path_grew': sys.path != path_before,\n"
            "    'reconfigure_calls': reconfigure_calls['n'],\n"
            "}\n"
            "print(json.dumps(result))\n"
        )
        clean_env = {k: v for k, v in os.environ.items() if not k.startswith("LTH_")}
        probe_argv = [sys.executable, "-c", probe_script]
        # N4-N2-Guard: jeder echte `subprocess.Popen`-Aufruf braucht eine
        # vorherige exakte argv-Registrierung (s. `authorize_and_consume`);
        # ohne env/cwd-Bindung bei der Registrierung bleiben env/cwd hier frei.
        EARLY_GUARD.register_child(
            role="b1-negative-probe", argv=probe_argv, fixture_paths=[],
            export_id="b1-negative-probe-export", count=1,
        )
        proc = subprocess.run(
            probe_argv, cwd=str(_HERE), env=clean_env, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(proc.returncode, 0, f"Probe-Subprozess ist gecrasht:\n{proc.stdout}\n{proc.stderr}")
        result = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertFalse(result["real_body"], "Probe muss selbst im geteilten-Elternprozess-Zweig laufen.")
        self.assertEqual(
            result["leaked_aliases"], [],
            "keiner der drei Produktmodul-Aliase darf im geteilten Elternprozess in sys.modules landen.",
        )
        self.assertFalse(
            result["path_grew"],
            "sys.path darf im geteilten Elternprozess nicht durch Produktimporte wachsen "
            "(setup.py/launcher.py-Pfadmutationen duerfen hier nicht laufen).",
        )
        self.assertEqual(
            result["reconfigure_calls"], 0,
            "launcher.py darf stdout/stderr im geteilten Elternprozess NICHT umkonfigurieren.",
        )

    def test_bridge_parent_fails_when_child_reports_skipped_tests(self):
        """B2-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md B2): eine Kind-
        Suite, die (auch nur teilweise) uebersprungene Tests meldet, darf
        NICHT als erfolgreicher echter Testkoerper durchgehen -- `testsRun`
        zaehlt Skips mit, `wasSuccessful()` bleibt bei Skips `True`. Baut
        eine winzige TEMPORAERE Fixture-Datei (kein neues Repo-File, landet
        in einem `tempfile.mkdtemp()`) mit einem echten `unittest.TestCase`,
        das GENAU EINEN von zwei Tests per `skipTest` uebergeht, und laesst
        den ECHTEN Bruecken-Elternvertreter (`_DelegatingChildBase.test_
        protected_body_runs_in_fresh_interpreter`) direkt dagegen laufen."""
        fixture_dir = self._tmp_dir("bridge-skip-fixture")
        fixture_path = fixture_dir / "_bridge_skip_fixture.py"
        fixture_path.write_text(
            "import sys, unittest\n"
            f"sys.path.insert(0, {str(_HERE)!r})\n"
            "import _local_tokenhost_support_2026_11_14 as support_mod\n"
            "class _T(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n"
            "    def test_skipped(self):\n"
            "        self.skipTest('synthetic B2 counter-case')\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(support_mod.run_module_as_child(sys.modules[__name__]))\n",
            encoding="utf-8",
        )
        probe_argv = [sys.executable, str(fixture_path)]
        EARLY_GUARD.register_child(
            role="b2-skip-fixture", argv=probe_argv, fixture_paths=[],
            export_id="b2-skip-fixture-export", count=1,
        )
        cls = type(
            "BridgeSkipFixtureChild", (_support_mod._DelegatingChildBase,),
            {"_module_file": str(fixture_path), "_module_label": "bridge-skip-fixture",
             "_min_domain_tests": 1, "_timeout_s": 60},
        )
        case = cls("test_protected_body_runs_in_fresh_interpreter")
        with self.assertRaises(AssertionError) as ctx:
            case.test_protected_body_runs_in_fresh_interpreter()
        self.assertIn("uebersprungene", str(ctx.exception))

    def test_self_bootstrap_rejects_empty_or_null_explicit_context_but_absent_context_works(self):
        """B3-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md B3): ein EXPLIZIT
        gesetztes, aber leeres `LTH_CONTEXT_JSON` ODER ein explizit
        gesetztes `LTH_CONTEXT_JSON=null` muessen SICHTBAR scheitern -- vor
        dem Fix fielen beide Faelle (`if env_ctx:` ist fuer "" falsy;
        `if ctx is not None:` ist fuer das aus 'null' geparste `None`
        ebenfalls falsch) still auf den normalen Self-Bootstrap zurueck,
        identisch zu einem GANZ ABWESENDEN Kontext. Ein tatsaechlich
        ABWESENDER Kontext muss weiterhin normal funktionieren (Positiv-
        kontrolle). `self_bootstrap_isolation()` selbst braucht einen
        FRISCHEN Interpreter (ein bereits in DIESEM Prozess installierter
        Primaerguard wuerde sofort wiederverwendet, Fall 1, und die neue
        Validierung nie erreichen) -- daher drei gezielte Subprozess-Proben."""
        probe_tmpl = (
            "import sys, json\n"
            f"sys.path.insert(0, {str(_HERE)!r})\n"
            "import _local_tokenhost_support_2026_11_14 as support_mod\n"
            "ok = False\n"
            "msg = ''\n"
            "try:\n"
            "    support_mod.self_bootstrap_isolation()\n"
            "    ok = {expect_raise!r} is False\n"
            "except support_mod.IsolationBootstrapError as exc:\n"
            "    ok = {expect_raise!r} is True\n"
            "    msg = str(exc)\n"
            "print(json.dumps({{'ok': ok, 'msg': msg}}))\n"
        )
        for case_name, env_value, expect_raise in (
            ("empty", "", True),
            ("null", "null", True),
            ("absent", None, False),
        ):
            # eindeutiges argv je Fall -- sonst waeren "empty" und "null"
            # (beide expect_raise=True) textidentische Skripte und die
            # zweite Registrierung/Verbrauch desselben argv wuerde als
            # Replay abgelehnt.
            script = f"# case={case_name}\n" + probe_tmpl.format(expect_raise=expect_raise)
            clean_env = {k: v for k, v in os.environ.items() if not k.startswith("LTH_")}
            if env_value is not None:
                clean_env["LTH_CONTEXT_JSON"] = env_value
            probe_argv = [sys.executable, "-c", script]
            EARLY_GUARD.register_child(
                role=f"b3-context-probe-{case_name}", argv=probe_argv, fixture_paths=[],
                export_id=f"b3-context-probe-{case_name}-export", count=1,
            )
            proc = subprocess.run(
                probe_argv, cwd=str(_HERE), env=clean_env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(
                proc.returncode, 0,
                f"[{case_name}] Probe-Subprozess ist gecrasht:\n{proc.stdout}\n{proc.stderr}",
            )
            result = json.loads(proc.stdout.strip().splitlines()[-1])
            self.assertTrue(
                result["ok"],
                f"[{case_name}] LTH_CONTEXT_JSON={env_value!r}: erwartetes "
                f"Verhalten (expect_raise={expect_raise}) trat nicht ein. msg={result['msg']!r}",
            )

    # ─── 1. Resolver pur: Validierung/Haltegruende ──────────────────────

    def test_resolve_provider_legacy_cloud_local_hold(self):
        # N1-03: fehlender Schluessel (Datei erwaehnt den Provider nie) ist
        # 'legacy'; ein ausdruecklich LEERER Schluessel (`KEY=`) ist KEIN
        # Legacyzustand mehr, sondern ein sichtbarer HOLD (vorher beide
        # faelschlich gleich behandelt).
        self.assertEqual(lmp.resolve_provider({}), "legacy")
        self.assertEqual(lmp.resolve_provider({"ZEITRISS_MODEL_PROVIDER": ""}), "hold")
        self.assertEqual(lmp.resolve_provider({"ZEITRISS_MODEL_PROVIDER": "cloud"}), "cloud")
        self.assertEqual(lmp.resolve_provider({"ZEITRISS_MODEL_PROVIDER": "LOCAL"}), "local")
        self.assertEqual(lmp.resolve_provider({"ZEITRISS_MODEL_PROVIDER": "weird-value"}), "hold")

    def test_resolve_local_profile_valid_defaults(self):
        env = {
            lmp.ENV_KEY_PROVIDER: "local",
            lmp.ENV_KEY_BASE_URL: FAKE_BASE_URL,
            lmp.ENV_KEY_MODEL: FAKE_MODEL,
            lmp.ENV_KEY_API_KEY: FAKE_TOKEN,
        }
        profile = lmp.resolve_local_profile(env)
        self.assertEqual(profile.base_url, FAKE_BASE_URL)
        self.assertEqual(profile.model, FAKE_MODEL)
        self.assertEqual(profile.api_key, FAKE_TOKEN)
        self.assertIsNone(profile.owui_base_url)
        self.assertEqual(profile.gm_max_tokens, lmp.DEFAULT_GM_MAX_TOKENS)
        self.assertEqual(profile.gm_max_tokens, 4096)
        self.assertEqual(profile.persona_max_tokens, lmp.DEFAULT_PERSONA_MAX_TOKENS)
        self.assertEqual(profile.persona_max_tokens, 400)

    def test_resolve_local_profile_negative_cases_hold_not_raise_generic(self):
        base = {
            lmp.ENV_KEY_BASE_URL: FAKE_BASE_URL,
            lmp.ENV_KEY_MODEL: FAKE_MODEL,
            lmp.ENV_KEY_API_KEY: FAKE_TOKEN,
        }

        def _expect_hold(overrides: dict, note: str):
            env = dict(base)
            env.update(overrides)
            with self.assertRaises(lmp.ProfileHold, msg=note):
                lmp.resolve_local_profile(env)

        _expect_hold({lmp.ENV_KEY_BASE_URL: ""}, "leere URL")
        _expect_hold({lmp.ENV_KEY_BASE_URL: "ftp://127.0.0.1:1/v1"}, "falsches Schema")
        _expect_hold({lmp.ENV_KEY_BASE_URL: "http://user:pw@127.0.0.1:1/v1"}, "eingebettetes Credential")
        _expect_hold({lmp.ENV_KEY_BASE_URL: "http://127.0.0.1:1/v1?token=x"}, "Query-Secret")
        _expect_hold({lmp.ENV_KEY_BASE_URL: "http://127.0.0.1:999999/v1"}, "ungueltiger Port")
        _expect_hold({lmp.ENV_KEY_MODEL: ""}, "leeres Modell")
        _expect_hold({lmp.ENV_KEY_MODEL: "a\r\nb"}, "CRLF im Modell")
        _expect_hold({lmp.ENV_KEY_API_KEY: ""}, "leerer Token")
        _expect_hold({lmp.ENV_KEY_API_KEY: "tok\x00en"}, "NUL im Token")
        _expect_hold({lmp.ENV_KEY_GM_MAX_TOKENS: "0"}, "GM-Limit 0")
        _expect_hold({lmp.ENV_KEY_GM_MAX_TOKENS: "-5"}, "GM-Limit negativ")
        _expect_hold({lmp.ENV_KEY_GM_MAX_TOKENS: "abc"}, "GM-Limit unlesbar")
        _expect_hold({lmp.ENV_KEY_PERSONA_MAX_TOKENS: "0"}, "Persona-Limit 0")
        _expect_hold({lmp.ENV_KEY_OWUI_BASE_URL: "not-a-url"}, "ungueltige OWUI-Basis")
        # A3-Fix (02_NACHARBEIT.md Gruppe A.3): "URLs lehnen ALLE Steuerzeichen
        # ab, nicht nur CR/LF/NUL" -- Tab und ein beliebiges anderes ASCII-
        # Steuerzeichen (hier \x01) im Pfadanteil muessen ebenfalls halten.
        _expect_hold({lmp.ENV_KEY_BASE_URL: "http://127.0.0.1:1/v1/\tpath"}, "Tab in der URL")
        _expect_hold({lmp.ENV_KEY_BASE_URL: "http://127.0.0.1:1/v1/\x01path"}, "sonstiges Steuerzeichen (\\x01) in der URL")

    def test_negative_messages_never_contain_secret_value(self):
        env = {
            lmp.ENV_KEY_BASE_URL: FAKE_BASE_URL,
            lmp.ENV_KEY_MODEL: FAKE_MODEL,
            lmp.ENV_KEY_API_KEY: "",
        }
        with self.assertRaises(lmp.ProfileHold) as ctx:
            lmp.resolve_local_profile(env)
        self.assertNotIn(FAKE_TOKEN, str(ctx.exception))
        self.assertIn("ZEITRISS_LOCAL_API_KEY", str(ctx.exception))

    # ─── 2. Realer Schreib-/Readback-Pfad (setup.py-Helfer, keine Verdopplung) ──

    def test_write_readback_roundtrip_protected_0600_and_values_exact(self):
        env_path = self._tmp_env_path("roundtrip")
        updates = lmp.build_local_profile_updates(
            base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN,
            gm_max_tokens=4096, persona_max_tokens=400,
        )
        ok = setup_mod._update_env_file_preserving(env_path, updates)
        self.assertTrue(ok)
        mode = stat.S_IMODE(env_path.stat().st_mode)
        self.assertEqual(mode, 0o600, f"erwartete 0600, bekam {oct(mode)}")

        # Frischer Reread -- kein In-Memory-Zustand des Schreibvorgangs wird
        # wiederverwendet.
        reread = setup_mod._read_env_file(env_path)
        profile = lmp.resolve_local_profile(reread)
        self.assertEqual(profile.base_url, FAKE_BASE_URL)
        self.assertEqual(profile.model, FAKE_MODEL)
        self.assertEqual(profile.api_key, FAKE_TOKEN)
        self.assertEqual(profile.gm_max_tokens, 4096)
        self.assertEqual(profile.persona_max_tokens, 400)
        self.assertEqual(reread[lmp.ENV_KEY_PROVIDER], "local")

        provider, profile2, reason = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "local")
        self.assertIsNone(reason)
        # setup_mod importiert sein EIGENES `local_model_profile` (echter
        # sys.path-Import) -- andere Klassenidentitaet als das hier per
        # spec_from_file_location geladene `lmp`, daher Feldvergleich statt
        # Dataclass-`__eq__` (das `other.__class__ is self.__class__` prueft).
        self.assertEqual(profile2.base_url, profile.base_url)
        self.assertEqual(profile2.model, profile.model)
        self.assertEqual(profile2.api_key, profile.api_key)
        self.assertEqual(profile2.gm_max_tokens, profile.gm_max_tokens)
        self.assertEqual(profile2.persona_max_tokens, profile.persona_max_tokens)

    def test_preserves_foreign_fields_comments_and_cloud_values_on_local_write(self):
        env_path = self._tmp_env_path("preserve")
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(
            "# ein fremder Kommentar\n"
            "OPENWEBUI_URL=http://localhost:8080\n"
            "OPENWEBUI_API_KEY=owui-fake-key-abc\n"
            "OPENROUTER_API_KEY=sk-or-fake-old-key\n"
            "SOME_UNKNOWN_CUSTOM_VAR=bleibt-unberuehrt\n",
            encoding="utf-8",
        )
        updates = lmp.build_local_profile_updates(
            base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN,
        )
        ok = setup_mod._update_env_file_preserving(env_path, updates)
        self.assertTrue(ok)
        content = env_path.read_text(encoding="utf-8")
        self.assertIn("# ein fremder Kommentar", content)
        self.assertIn("SOME_UNKNOWN_CUSTOM_VAR=bleibt-unberuehrt", content)
        self.assertIn("OPENWEBUI_API_KEY=owui-fake-key-abc", content)
        self.assertIn(
            "OPENROUTER_API_KEY=sk-or-fake-old-key", content,
            "OpenRouter-Key muss erhalten bleiben -- Local-Wahl loescht keine "
            "Cloud-Altwerte (02: alte Legacy-Personafelder bleiben erhalten).",
        )
        self.assertIn(FAKE_TOKEN, content)
        self.assertIn("ZEITRISS_LOCAL_API_KEY=", content)

    def test_reuse_enter_keeps_existing_local_profile_via_action_rekeys(self):
        """O1: 'Rekey mit Enter erhaelt die Auswahl' -- echter `action_rekeys`-
        Lauf, zweiter Aufruf mit nur Enter behaelt Token/URL/Modell unveraendert."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o1-rekey-home-"))
        self._tmp_dirs.append(tmp_home)
        stdout_lines: list[str] = []

        def _capture_print(*args, **_kwargs):
            stdout_lines.append(" ".join(str(a) for a in args))

        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch.object(launcher_mod, "_pause", return_value=None), \
             mock.patch("builtins.print", side_effect=_capture_print):
            prompts_1 = iter([
                "http://localhost:8080",  # OpenWebUI-URL (zuerst, unveraenderte Reihenfolge)
                "local",                  # Modell-Provider
                FAKE_BASE_URL,
                FAKE_MODEL,
                "",
            ])
            with mock.patch.object(launcher_mod, "_prompt", side_effect=lambda *_a, **_k: next(prompts_1)), \
                 mock.patch("getpass.getpass", side_effect=["owui-fake-key", FAKE_TOKEN]):
                launcher_mod.action_rekeys()

            env_path = tmp_home / ".openwebui_env"
            self.assertTrue(env_path.is_file())
            first_body = setup_mod._read_env_file(env_path)
            self.assertEqual(first_body[lmp.ENV_KEY_MODEL], FAKE_MODEL)
            self.assertEqual(first_body[lmp.ENV_KEY_API_KEY], FAKE_TOKEN)

            prompts_2 = iter(["", "", "", "", ""])
            with mock.patch.object(launcher_mod, "_prompt", side_effect=lambda *_a, **_k: next(prompts_2)), \
                 mock.patch("getpass.getpass", side_effect=["", ""]):
                launcher_mod.action_rekeys()

            second_body = setup_mod._read_env_file(env_path)
            self.assertEqual(second_body[lmp.ENV_KEY_MODEL], FAKE_MODEL)
            self.assertEqual(second_body[lmp.ENV_KEY_API_KEY], FAKE_TOKEN)
            self.assertEqual(second_body[lmp.ENV_KEY_PROVIDER], "local")

        joined_stdout = "\n".join(stdout_lines)
        self.assertNotIn(FAKE_TOKEN, joined_stdout, "Token darf nie in Terminalausgabe erscheinen.")

    def test_cloud_to_local_to_cloud_switch_fresh_reread_each_time(self):
        """O1/O6-Unterstuetzung: bewusster Rueckwechsel, jeweils FRISCH von der
        Platte gelesen (kein In-Memory-Rest eines frueheren Aufrufs)."""
        env_path = self._tmp_env_path("switch")
        cloud_updates = {"OPENWEBUI_URL": "http://localhost:8080", "OPENROUTER_API_KEY": "sk-or-fake-cloud"}
        self.assertTrue(setup_mod._update_env_file_preserving(env_path, cloud_updates))
        provider, _p, _r = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "legacy")

        local_updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        self.assertTrue(setup_mod._update_env_file_preserving(env_path, local_updates))
        provider, profile, _r = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "local")
        self.assertEqual(profile.model, FAKE_MODEL)

        self.assertTrue(setup_mod._update_env_file_preserving(env_path, lmp.cloud_provider_updates()))
        provider, profile, _r = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "cloud")
        self.assertIsNone(profile)
        reread = setup_mod._read_env_file(env_path)
        self.assertEqual(reread.get("OPENROUTER_API_KEY"), "sk-or-fake-cloud")
        self.assertEqual(
            reread.get(lmp.ENV_KEY_MODEL), FAKE_MODEL,
            "Lokale Felder bleiben in der Datei stehen -- ein spaeterer Rueckwechsel auf "
            "local braucht keine Neueingabe (cloud_provider_updates()-Vertrag).",
        )

        self.assertTrue(setup_mod._update_env_file_preserving(env_path, {lmp.ENV_KEY_PROVIDER: "local"}))
        provider, profile, _r = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "local")
        self.assertEqual(profile.model, FAKE_MODEL)
        self.assertEqual(profile.api_key, FAKE_TOKEN)

    def test_unreadable_existing_file_not_replaced_write_fails_closed(self):
        env_path = self._tmp_env_path("unreadable")
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text("OPENWEBUI_URL=http://localhost:8080\n", encoding="utf-8")
        env_path.chmod(0o000)
        try:
            ok = setup_mod._update_env_file_preserving(
                env_path,
                lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN),
            )
            self.assertFalse(ok, "unlesbare Bestandsdatei darf NICHT neu gebaut werden.")
        finally:
            env_path.chmod(0o600)
        content = env_path.read_text(encoding="utf-8")
        self.assertEqual(content, "OPENWEBUI_URL=http://localhost:8080\n", "Datei muss bytegleich unangetastet bleiben.")

    def test_read_env_file_recognizes_export_prefix_and_quotes(self):
        """A3-Fix (02_NACHARBEIT.md Gruppe A.3): alle beteiligten Leser muessen
        denselben KEY=VALUE-/export-/Quote-Vertrag verstehen. VOR dem Fix
        erkannte `_read_env_file` (von `resolve_model_provider` genutzt)
        WEDER `export `-Praefix NOCH Quotes -- eine so gespeicherte lokale
        Wahl waere faelschlich als 'legacy' gelesen worden."""
        env_path = self._tmp_env_path("export-quotes")
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(
            'export ZEITRISS_MODEL_PROVIDER=local\n'
            f'ZEITRISS_LOCAL_BASE_URL="{FAKE_BASE_URL}"\n'
            f"export ZEITRISS_LOCAL_MODEL='{FAKE_MODEL}'\n"
            f"ZEITRISS_LOCAL_API_KEY={FAKE_TOKEN}\n",
            encoding="utf-8",
        )
        reread = setup_mod._read_env_file(env_path)
        self.assertEqual(reread[lmp.ENV_KEY_PROVIDER], "local")
        self.assertEqual(reread[lmp.ENV_KEY_BASE_URL], FAKE_BASE_URL)
        self.assertEqual(reread[lmp.ENV_KEY_MODEL], FAKE_MODEL)
        self.assertEqual(reread[lmp.ENV_KEY_API_KEY], FAKE_TOKEN)

        provider, profile, reason = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "local", reason)
        self.assertEqual(profile.model, FAKE_MODEL)

    def test_hold_blocks_launcher_choice_no_silent_cloud_fallback(self):
        env_path = self._tmp_env_path("hold")
        setup_mod._update_env_file_preserving(env_path, {"ZEITRISS_MODEL_PROVIDER": "quantum-local-ish"})
        provider, profile, reason = launcher_mod.resolve_model_provider_choice(env_path)
        self.assertEqual(provider, "hold")
        self.assertIsNone(profile)
        self.assertIsNone(reason)

        env_path2 = self._tmp_env_path("hold-incomplete")
        setup_mod._update_env_file_preserving(
            env_path2, {"ZEITRISS_MODEL_PROVIDER": "local", lmp.ENV_KEY_MODEL: FAKE_MODEL}
        )
        provider2, profile2, reason2 = launcher_mod.resolve_model_provider_choice(env_path2)
        self.assertEqual(provider2, "hold")
        self.assertIsNone(profile2)
        self.assertTrue(reason2 and lmp.ENV_KEY_BASE_URL in reason2)

    def test_cloud_litellm_traps_never_triggered_by_profile_resolution(self):
        """O1-Belegpflicht: Aufrufzaehler fuer Cloud-/LiteLLM-Fallen = 0 -- reine
        Profilaufloesung darf NIE `run_install_litellm`/`ensure_litellm_autowire`/
        `APIClient.test_model` beruehren."""
        calls = {"litellm_install": 0, "litellm_autowire": 0, "test_model": 0}

        def _trap_install(*_a, **_k):
            calls["litellm_install"] += 1
            raise AssertionError("run_install_litellm darf hier nicht aufgerufen werden")

        def _trap_autowire(*_a, **_k):
            calls["litellm_autowire"] += 1
            raise AssertionError("ensure_litellm_autowire darf hier nicht aufgerufen werden")

        def _trap_test_model(self_, *_a, **_k):
            calls["test_model"] += 1
            raise AssertionError("APIClient.test_model darf hier nicht aufgerufen werden")

        env_path = self._tmp_env_path("traps")
        updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        with mock.patch.object(setup_mod, "run_install_litellm", _trap_install), \
             mock.patch.object(setup_mod, "ensure_litellm_autowire", _trap_autowire), \
             mock.patch.object(setup_mod.APIClient, "test_model", _trap_test_model):
            self.assertTrue(setup_mod._update_env_file_preserving(env_path, updates))
            provider, profile, reason = setup_mod.resolve_model_provider(env_path)
            self.assertEqual(provider, "local")
            self.assertEqual(profile.model, FAKE_MODEL)

        self.assertEqual(calls, {"litellm_install": 0, "litellm_autowire": 0, "test_model": 0})

    # ─── O1-A (A1): echter frischer action_install-Weg fragt Erstwahl ──────

    def test_fresh_action_install_asks_cloud_local_erstwahl_local_choice_no_cloudkey(self):
        """G1-Fix (02_NACHARBEIT.md Gruppe A.1): VOR dem Fix loeste
        `action_install` bei 'legacy' (noch nie gewaehlt) NUR eine bereits
        gespeicherte Wahl auf und fiel dadurch still auf den alten Cloudweg
        zurueck, OHNE je zu fragen. Dieser Test faehrt den tatsaechlichen
        frischen `action_install`-Weg (keine gespeicherte Wahl) und waehlt
        'local' -- KEIN Cloudkey-/LiteLLM-Zwang danach, dieselbe Validierung/
        Persistenz wie `action_rekeys` (`_rekeys_choose_local_fields`)."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o1-erstwahl-home-"))
        self._tmp_dirs.append(tmp_home)
        saved_env = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "owui-fake-key-not-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        try:
            prompts = iter(["l", FAKE_BASE_URL, FAKE_MODEL, ""])
            with mock.patch.object(Path, "home", return_value=tmp_home), \
                 mock.patch.object(launcher_mod, "_detect_install_state", side_effect=["fresh", "fresh"]), \
                 mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
                 mock.patch.object(launcher_mod, "_prompt", side_effect=lambda *_a, **_k: next(prompts)), \
                 mock.patch("getpass.getpass", side_effect=["test-local-token-not-secret"]), \
                 mock.patch.object(launcher_mod, "_pause"), \
                 mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
                 mock.patch.object(launcher_mod.setup_module, "run_install_litellm") as install_litellm_mock, \
                 mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock, \
                 mock.patch.object(launcher_mod, "_litellm_ok", return_value=(False, "nicht geprueft")):
                launcher_mod.action_install()

            self.assertEqual(run_setup_mock.call_count, 1, "lokale Erstwahl ueberspringt run_setup NICHT.")
            self.assertEqual(install_litellm_mock.call_count, 0, "lokale Wahl: kein LiteLLM-Zwang danach.")
            self.assertEqual(autowire_mock.call_count, 0, "lokale Wahl: kein LiteLLM-Autowire danach.")

            env_path = tmp_home / ".openwebui_env"
            self.assertTrue(env_path.is_file(), "Erstwahl 'local' muss persistiert werden.")
            reread = setup_mod._read_env_file(env_path)
            self.assertEqual(reread[lmp.ENV_KEY_PROVIDER], "local")
            profile = lmp.resolve_local_profile(reread)
            self.assertEqual(profile.base_url, FAKE_BASE_URL)
            self.assertEqual(profile.model, FAKE_MODEL)
            self.assertEqual(profile.api_key, "test-local-token-not-secret")

            provider, _p, _r = launcher_mod.resolve_model_provider_choice(env_path)
            self.assertEqual(provider, "local", "Erstwahl muss fuer DIESEN Lauf uebernommen werden (kein Cloudzwang).")
        finally:
            os.environ.clear()
            os.environ.update(saved_env)

    def test_fresh_action_install_erstwahl_cloud_choice_persists_provider_cloud(self):
        """Gegenprobe: Erstwahl 'cloud' (Enter/Default) persistiert
        `ZEITRISS_MODEL_PROVIDER=cloud` und laeuft unveraendert den alten
        Cloud-/LiteLLM-Weg (alte Pflichten bleiben erhalten)."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o1-erstwahl-cloud-home-"))
        self._tmp_dirs.append(tmp_home)
        saved_env = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "owui-fake-key-not-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        os.environ["OPENROUTER_API_KEY"] = "sk-or-fake-not-secret"
        try:
            with mock.patch.object(Path, "home", return_value=tmp_home), \
                 mock.patch.object(launcher_mod, "_detect_install_state", side_effect=["fresh", "fresh"]), \
                 mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
                 mock.patch.object(launcher_mod, "_openrouter_key_status", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_prompt", return_value=""), \
                 mock.patch.object(launcher_mod, "_pause"), \
                 mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
                 mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock:
                launcher_mod.action_install()
            self.assertEqual(run_setup_mock.call_count, 1)
            self.assertEqual(autowire_mock.call_count, 1, "Cloud-Erstwahl laeuft weiter den alten LiteLLM-Weg.")
            env_path = tmp_home / ".openwebui_env"
            reread = setup_mod._read_env_file(env_path)
            self.assertEqual(reread.get(lmp.ENV_KEY_PROVIDER), "cloud")
        finally:
            os.environ.clear()
            os.environ.update(saved_env)

    def test_fresh_action_install_cloud_choice_write_failure_halts_visibly_no_autowire(self):
        """P5-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md, O1-C.C1): Gegenprobe
        zum vorigen Test -- der Cloud-Erstwahlzweig ignorierte vorher den
        False-Rueckgabewert des geschuetzten Writers und lief trotzdem bis
        `run_setup`/`ensure_litellm_autowire` weiter, obwohl die Wahl NIE
        persistiert wurde. Jetzt muss ein Schreibfehler sichtbar halten --
        kein automatischer Fortsetzungsversuch mit unpersistierter Wahl."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o1-erstwahl-cloud-writefail-"))
        self._tmp_dirs.append(tmp_home)
        saved_env = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "owui-fake-key-not-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        os.environ["OPENROUTER_API_KEY"] = "sk-or-fake-not-secret"
        try:
            with mock.patch.object(Path, "home", return_value=tmp_home), \
                 mock.patch.object(launcher_mod, "_detect_install_state", side_effect=["fresh", "fresh"]), \
                 mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
                 mock.patch.object(launcher_mod, "_openrouter_key_status", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_prompt", return_value=""), \
                 mock.patch.object(launcher_mod, "_pause") as pause_mock, \
                 mock.patch.object(launcher_mod.setup_module, "_update_env_file_preserving", return_value=False), \
                 mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
                 mock.patch.object(launcher_mod, "_litellm_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock:
                launcher_mod.action_install()
            self.assertEqual(
                run_setup_mock.call_count, 0,
                "ein ignorierter Schreibfehler duerfte NICHT bis run_setup weiterlaufen.",
            )
            self.assertEqual(autowire_mock.call_count, 0)
            self.assertGreaterEqual(pause_mock.call_count, 1, "muss sichtbar halten (Pause), nicht einfach weiterlaufen.")
            env_path = tmp_home / ".openwebui_env"
            self.assertFalse(
                env_path.is_file(),
                "bei einem gehaltenen Schreibfehler darf keine (auch keine ungeschuetzte Vorab-) "
                "Datei zurueckbleiben.",
            )
        finally:
            os.environ.clear()
            os.environ.update(saved_env)

    def test_action_install_erstwahl_local_halts_on_wrong_but_valid_readback_mismatch(self):
        """O1-C.C2/C3 (RELEASE-CASES.json): "falscher, aber gueltiger
        Readback in Erstwahl UND Rekey haelt" -- der bestehende zentrale
        Helpertest (`test_protected_publish_wrong_but_valid_readback_holds_
        no_false_success`) treibt NUR `_update_env_file_preserving` direkt,
        nie den echten `action_install`-Erstwahlweg. Hier liefert das
        Pflicht-Readback INNERHALB des Writers ein strukturell gueltiges,
        aber vom gewaehlten Profil ABWEICHENDES Modell zurueck (z.B. eine
        Race/ein fremder gleichzeitiger Schreibzugriff) -- der echte
        Aufrufer muss sichtbar halten, NICHT mit der falschen Auswahl
        weiterlaufen."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o1-erstwahl-local-readback-mismatch-"))
        self._tmp_dirs.append(tmp_home)
        saved_env = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "owui-fake-key-not-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        try:
            prompts = iter(["l", FAKE_BASE_URL, FAKE_MODEL, ""])
            wrong_but_valid = {
                lmp.ENV_KEY_PROVIDER: "local", lmp.ENV_KEY_BASE_URL: FAKE_BASE_URL,
                lmp.ENV_KEY_MODEL: "a-different-but-otherwise-valid-model", lmp.ENV_KEY_API_KEY: FAKE_TOKEN,
            }
            with mock.patch.object(Path, "home", return_value=tmp_home), \
                 mock.patch.object(launcher_mod, "_detect_install_state", side_effect=["fresh", "fresh"]), \
                 mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
                 mock.patch.object(launcher_mod, "_prompt", side_effect=lambda *_a, **_k: next(prompts)), \
                 mock.patch("getpass.getpass", side_effect=["test-local-token-not-secret"]), \
                 mock.patch.object(launcher_mod, "_pause") as pause_mock, \
                 mock.patch.object(launcher_mod.setup_module, "_read_env_file", return_value=wrong_but_valid), \
                 mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
                 mock.patch.object(launcher_mod.setup_module, "run_install_litellm") as install_litellm_mock, \
                 mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock:
                launcher_mod.action_install()
            self.assertEqual(
                run_setup_mock.call_count, 0,
                "ein falscher-aber-gueltiger Readback-Mismatch darf NICHT bis run_setup weiterlaufen.",
            )
            self.assertEqual(install_litellm_mock.call_count, 0)
            self.assertEqual(autowire_mock.call_count, 0)
            self.assertGreaterEqual(pause_mock.call_count, 1, "muss sichtbar halten, nicht einfach weiterlaufen.")
        finally:
            os.environ.clear()
            os.environ.update(saved_env)

    def test_action_rekeys_local_halts_on_wrong_but_valid_readback_mismatch(self):
        """O1-C.C2/C3 (RELEASE-CASES.json): Gegenstueck zum vorigen Test fuer
        den echten Rekey-Aufrufer (`action_rekeys`, lokaler Zweig) -- derselbe
        falsche-aber-gueltige Readback-Mismatch muss auch hier sichtbar
        halten, nicht nur am zentralen Helper oder am (positiven)
        `test_rekey_enter_preserves_strict_512_120_limits...`-Test."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o1-rekey-local-readback-mismatch-"))
        self._tmp_dirs.append(tmp_home)
        wrong_but_valid = {
            lmp.ENV_KEY_PROVIDER: "local", lmp.ENV_KEY_BASE_URL: FAKE_BASE_URL,
            lmp.ENV_KEY_MODEL: "a-different-but-otherwise-valid-model", lmp.ENV_KEY_API_KEY: FAKE_TOKEN,
        }
        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch.object(launcher_mod, "_pause") as pause_mock:
            prompts = iter(["http://localhost:8080", "local", FAKE_BASE_URL, FAKE_MODEL, ""])
            with mock.patch.object(launcher_mod, "_prompt", side_effect=lambda *_a, **_k: next(prompts)), \
                 mock.patch("getpass.getpass", side_effect=["owui-fake-key", FAKE_TOKEN]), \
                 mock.patch.object(launcher_mod.setup_module, "_read_env_file", return_value=wrong_but_valid):
                launcher_mod.action_rekeys()
        self.assertGreaterEqual(pause_mock.call_count, 1, "muss sichtbar halten, nicht einfach weiterlaufen.")
        env_path = tmp_home / ".openwebui_env"
        marker = setup_mod._pending_marker_path(env_path)
        self.assertTrue(
            marker.exists(),
            "bei einem Readback-Mismatch muss der Pending-Marker aktiv bleiben (HOLD) -- "
            "die Bytes stehen zwar schon auf Platte, aber unbestaetigt.",
        )
        provider, _p, hold_reason = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(
            provider, "hold",
            f"ein aktiver Pending-Marker muss resolve_model_provider sichtbar halten lassen, war {provider!r} ({hold_reason!r}).",
        )

    def test_action_install_reuses_valid_saved_local_choice_without_erstwahl_prompt(self):
        """O1-A (A1, dritte Teilbedingung): "gueltige gespeicherte Wahl
        wiederverwenden" -- liegt VOR dem Lauf schon eine gueltige
        persistierte 'local'-Wahl vor (z.B. aus einem frueheren Lauf), muss
        der echte `action_install`-Weg diese OHNE jede erneute Cloud/local-
        Erstwahlfrage uebernehmen. `_prompt` wird in diesem Test komplett
        gesperrt (wirft bei JEDEM Aufruf) -- die beiden anderen Teile von
        A1 (frischer Cloud-Weg, frischer Local-Weg mit eigener Erstwahl)
        sind bereits durch die zwei Tests direkt oberhalb belegt; dieser
        Test schliesst GENAU die bisher fehlende dritte Teilbedingung."""
        tmp_home = Path(tempfile.mkdtemp(prefix="o1-erstwahl-reuse-home-"))
        self._tmp_dirs.append(tmp_home)
        saved_env = dict(os.environ)
        os.environ["OPENWEBUI_API_KEY"] = "owui-fake-key-not-secret"
        os.environ["OPENWEBUI_URL"] = "http://127.0.0.1:8080"
        try:
            env_path = tmp_home / ".openwebui_env"
            saved_updates = lmp.build_local_profile_updates(
                base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN,
            )
            self.assertTrue(setup_mod._update_env_file_preserving(env_path, saved_updates))

            def _forbidden_prompt(*args, **_kwargs):
                raise AssertionError(
                    f"_prompt darf bei einer bereits gueltigen gespeicherten Wahl NICHT "
                    f"aufgerufen werden (Argumente: {args!r})."
                )

            with mock.patch.object(Path, "home", return_value=tmp_home), \
                 mock.patch.object(launcher_mod, "_detect_install_state", side_effect=["fresh", "fresh"]), \
                 mock.patch.object(launcher_mod, "_docker_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_openwebui_ok", return_value=(True, "ok")), \
                 mock.patch.object(launcher_mod, "_ensure_owui_env", return_value=True), \
                 mock.patch.object(launcher_mod, "_prompt", side_effect=_forbidden_prompt), \
                 mock.patch.object(launcher_mod, "_pause"), \
                 mock.patch.object(launcher_mod.setup_module, "run_setup") as run_setup_mock, \
                 mock.patch.object(launcher_mod.setup_module, "run_install_litellm") as install_litellm_mock, \
                 mock.patch.object(launcher_mod.setup_module, "ensure_litellm_autowire") as autowire_mock:
                launcher_mod.action_install()

            self.assertEqual(run_setup_mock.call_count, 1, "gespeicherte lokale Wahl ueberspringt run_setup NICHT.")
            self.assertEqual(install_litellm_mock.call_count, 0, "wiederverwendete lokale Wahl: kein LiteLLM-Zwang.")
            self.assertEqual(autowire_mock.call_count, 0, "wiederverwendete lokale Wahl: kein LiteLLM-Autowire.")

            # Die gespeicherte Wahl bleibt unveraendert dieselbe (kein stiller
            # Neuaufbau/Ueberschreiben durch einen trotzdem versteckt
            # gelaufenen Erstwahl-Pfad).
            reread = setup_mod._read_env_file(env_path)
            self.assertEqual(reread[lmp.ENV_KEY_PROVIDER], "local")
            self.assertEqual(reread[lmp.ENV_KEY_MODEL], FAKE_MODEL)
            self.assertEqual(reread[lmp.ENV_KEY_API_KEY], FAKE_TOKEN)
        finally:
            os.environ.clear()
            os.environ.update(saved_env)

    # ─── I4: zwei frische Kinder, eigener Kontext/env, 7-Feld-Vergleich ──

    def test_two_fresh_children_cover_success_and_pending_persisted_states(self):
        """I4 (API-CONTRACT-N4N2.md §3/§5.3, 04_OFFLINE_ABNAHME.md/OFFLINE-CASES.json):
        GENAU ZWEI vorab exakt registrierte, verbrauchbare Kindprozesse, kein
        geteilter Modul-/Prozessstatus:

        - Schreiberkind (`write-matrix`): ECHTER Writer erzeugt A (echter
          Erfolg) UND B (derselbe Writer, synthetischer Fehler NUR am
          verpflichtenden Readback-IO-Seam `setup._read_env_file` ->
          tatsaechliches `False`, Pending-Marker bleibt belegt). Token/
          URL/Modell/Limits stehen NUR in einer privaten JSON-Fixturedatei,
          NIE in argv.
        - Leserkind (`read-matrix`): startet als VOELLIG NEUER Interpreter
          und vergleicht INTERN alle sieben I4.2-Felder (provider, base_url,
          model, api_key, owui_base_url, gm_max_tokens, persona_max_tokens)
          bei BEIDEN echten Resolvern gegen die Fixture -- druckt NUR
          boolesche Ergebnisse.

        Kinderstart exakt nach API-CONTRACT-N4N2.md §5.3: Ist
        `LTH_BOOTSTRAP_ENTRY` gesetzt (Runner-Lauf), laufen beide Kinder
        ueber Mains kontrollierten Einstieg (`[python -I -S -B
        <bootstrap_entry> "child-writer"/"child-reader" env_a env_b
        fixture]`) mit einem von `os.environ["LTH_CONTEXT_JSON"]`
        (selbst ein Dateipfad, kein Inline-JSON) geerbten Elternkontext
        (`real_home_class`/`repo_root`/`private_write_roots`/
        `dep_read_roots`). Fehlt `LTH_BOOTSTRAP_ENTRY` (Solo-Lauf), startet
        der Test den Support direkt (ebenfalls `-I -S -B`, `--context
        <kind_ctx>`), Exporte dann test-lokal. Beide Kinder bekommen ein
        EIGENES minimales `env=` (PATH/LANG/LC_ALL/LC_CTYPE + LTH_CONTEXT_JSON
        + LTH_SUPPORT_PATH, keine Tokens/kein PYTHONPATH) und einen EIGENEN
        gebundenen LTH-Kontext (eigene IDs/Exportpfade). stdout/stderr werden
        VOR den Assertions als Rohdateien gesichert (auch leer). Child
        start/end (echte UTC/PID/PPID/rc) werden sowohl am Guard als auch
        append-only in `child_events.jsonl` protokolliert."""
        self.assertTrue(_SUPPORT_SCRIPT.is_file())
        support_path = str(_SUPPORT_SCRIPT)

        # API-CONTRACT-N4N2.md §5.3: Runner-Lauf erkennt sich an
        # `LTH_BOOTSTRAP_ENTRY`; nur dann existieren die weiteren LTH_*-
        # Variablen verbindlich (sonst Solo-Fallback mit test-lokalen IDs/
        # Exporten unten).
        bootstrap_entry = os.environ.get("LTH_BOOTSTRAP_ENTRY")
        if bootstrap_entry:
            # N4-N3 Fix (01_GENERALREVIEW.md §3 "Profil und Runner benutzen
            # unterschiedliche Kontext- und Kinderprozessmodelle"): EIN
            # tatsaechlich verwendeter Plan steuert die gesamte Kette.
            # Mains run_bundle.py hat bereits VOR diesem Lauf ein
            # vollstaendiges, wertfreies `child_plan.json` geschrieben
            # (argv/minimal_env/cwd/Kontextpfad/private Wurzel/Exportpfade
            # je Kind, dieselbe `fixture.json`). Dieser Test baut KEINEN
            # eigenen, zweiten, abweichenden Plan mehr -- er liest und
            # verwendet exakt Mains Plan.
            exports_dir = Path(os.environ["LTH_CHILD_PHASE_DIR"])  # eigener privater Bereich (capture/)
            child_plan = json.loads(Path(os.environ["LTH_CHILD_PLAN"]).read_text(encoding="utf-8"))
            writer_plan, reader_plan = child_plan["writer"], child_plan["reader"]
            writer_id, reader_id = writer_plan["process_id"], reader_plan["process_id"]
            env_path_a = Path(writer_plan["env_a_path"])
            env_path_b = Path(writer_plan["env_b_path"])
            fixture_path = Path(writer_plan["fixture_path"])
            self.assertTrue(fixture_path.is_file(), "Main muss die Fixture vor dem Bundle anlegen.")
            writer_argv, reader_argv = writer_plan["argv"], reader_plan["argv"]
            writer_env, reader_env = writer_plan["minimal_env"], reader_plan["minimal_env"]
            writer_cwd, reader_cwd = writer_plan["cwd"], reader_plan["cwd"]
            writer_context_path = writer_plan["context_path"]
            reader_context_path = reader_plan["context_path"]
            writer_private_root = writer_plan["private_write_root"]
            reader_private_root = reader_plan["private_write_root"]
            writer_fixture_paths = writer_plan["fixture_paths"]
            reader_fixture_paths = reader_plan["fixture_paths"]
            writer_ctx_sha = writer_plan.get("guard_context_sha256")
            reader_ctx_sha = reader_plan.get("guard_context_sha256")
            # Mains bereits geschriebene Kind-Exportpfade (I1.4/I5.1) --
            # liegen je im EIGENEN privaten Bereich des Kindes, fuer DIESEN
            # (Eltern-)Prozess nur ueber `artifact_read_paths` lesbar.
            writer_before_path, writer_after_path = writer_plan["export_before_path"], writer_plan["export_after_path"]
            reader_before_path, reader_after_path = reader_plan["export_before_path"], reader_plan["export_after_path"]
        else:
            # Solo-Fallback (kein Main-Runner): baut lokal denselben
            # Umschlag, den `bootstrap_isolation` sonst vom Runner erhaelt.
            # In der Praxis unerreichbar, seit der Modulimport oben
            # zwingend einen bereits installierten Primaerguard verlangt
            # (kein stiller Platzhalterguard) -- bleibt als Entwicklungspfad
            # erhalten, ohne ihn weiter auszubauen.
            shared = self._tmp_dir("i4-shared-fixture")
            env_path_a = shared / ".fake_openwebui_env_a"
            env_path_b = shared / ".fake_openwebui_env_b"
            fixture_path = shared / "fixture.json"
            fixture_path.write_text(
                json.dumps({
                    "base_url": FAKE_BASE_URL, "model": FAKE_MODEL, "api_key": FAKE_TOKEN,
                    "owui_base_url": None, "gm_max_tokens": 512, "persona_max_tokens": 120,
                }),
                encoding="utf-8",
            )
            contexts_dir = self._tmp_dir("i4-contexts")
            exports_dir = self._tmp_dir("i4-exports")
            bundle_id = EARLY_GUARD.bundle_id
            writer_id, reader_id = "i4-writer", "i4-reader"
            writer_private_root = str(self._tmp_dir(f"i4-{writer_id}-private"))
            reader_private_root = str(self._tmp_dir(f"i4-{reader_id}-private"))

            def _child_context(role: str, child_id: str, own_private_root: str) -> str:
                before_path = str(exports_dir / f"{child_id}.before.json")
                after_path = str(exports_dir / f"{child_id}.after.json")
                ctx = {
                    "bundle_id": bundle_id, "process_id": child_id, "role": role,
                    "real_home_class": EARLY_GUARD.real_home_class,
                    "repo_root": str(_REPO_ROOT),
                    "source_read_roots": [str(_SCRIPTS_DIR)], "dep_read_roots": [],
                    "private_write_roots": [own_private_root], "shared_fixture_root": str(shared),
                    "export_before_path": before_path, "export_after_path": after_path,
                    "credential_block_roots": [], "artifact_read_paths": [],
                }
                path = contexts_dir / f"{child_id}-context.json"
                path.write_text(json.dumps(ctx), encoding="utf-8")
                return str(path), before_path, after_path

            writer_context_path, writer_before_path, writer_after_path = _child_context(
                "child-writer", writer_id, writer_private_root)
            reader_context_path, reader_before_path, reader_after_path = _child_context(
                "child-reader", reader_id, reader_private_root)
            writer_ctx_sha = hashlib.sha256(Path(writer_context_path).read_bytes()).hexdigest()
            reader_ctx_sha = hashlib.sha256(Path(reader_context_path).read_bytes()).hexdigest()
            writer_argv = [
                sys.executable, "-I", "-S", "-B", support_path, "write-matrix",
                str(env_path_a), str(env_path_b), str(fixture_path),
                "--context", writer_context_path,
            ]
            reader_argv = [
                sys.executable, "-I", "-S", "-B", support_path, "read-matrix",
                str(env_path_a), str(env_path_b), str(fixture_path),
                "--context", reader_context_path,
            ]
            base_child_env = {}
            for key in ("PATH", "LANG", "LC_ALL", "LC_CTYPE"):
                if os.environ.get(key):
                    base_child_env[key] = os.environ[key]
            writer_env = dict(base_child_env)
            writer_env["LTH_CONTEXT_JSON"] = writer_context_path
            writer_env["LTH_SUPPORT_PATH"] = support_path
            reader_env = dict(base_child_env)
            reader_env["LTH_CONTEXT_JSON"] = reader_context_path
            reader_env["LTH_SUPPORT_PATH"] = support_path
            writer_cwd = reader_cwd = None
            writer_fixture_paths = reader_fixture_paths = [fixture_path]

        # I2.2/I4.1: exakt nach Modus/Fixturepfad/Kontext/Anzahl binden --
        # kein breites `python3`-Praefix, keine klassenweite Menge. Genau
        # EIN Writer und EIN Reader, je einmal verbrauchbar. N4-N3 Fix
        # (01_GENERALREVIEW.md §3 "Kinderberechtigung ueberschreibbar;
        # env/cwd nicht verbindlich gebunden"): zusaetzlich env/cwd/
        # Kontext/privaten Bereich bindend mitregistrieren -- `cwd=` ist
        # jetzt derselbe Wert, der unten tatsaechlich an `Popen` gereicht
        # wird (Runner-Modus: Mains WORKTREE; Solo: unverandert None).
        EARLY_GUARD.register_child(
            role="child-writer", argv=writer_argv, fixture_paths=writer_fixture_paths,
            export_id="i4-writer-export", count=1,
            context_path=writer_context_path, context_sha256=writer_ctx_sha,
            minimal_env=writer_env, cwd=writer_cwd, private_root=writer_private_root,
        )
        EARLY_GUARD.register_child(
            role="child-reader", argv=reader_argv, fixture_paths=reader_fixture_paths,
            export_id="i4-reader-export", count=1,
            context_path=reader_context_path, context_sha256=reader_ctx_sha,
            minimal_env=reader_env, cwd=reader_cwd, private_root=reader_private_root,
        )

        # API-CONTRACT §5.3.6: Child start/end zusaetzlich append-only in
        # einer eigenen JSONL unter LTH_CHILD_PHASE_DIR (bzw. test-lokal im
        # Solo-Fallback) -- unabhaengig von den Guard-internen
        # child_starts/child_ends-Listen (die nur in den before/after-Export
        # DIESES Prozesses landen, nicht in einer eigenen Datei).
        events_path = exports_dir / "child_events.jsonl"

        def _append_child_event(**fields) -> None:
            fields.setdefault("utc", _utcnow_iso())
            with open(events_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(fields, sort_keys=True) + "\n")

        def _run_child(role: str, child_id: str, argv: list, child_env: dict,
                       child_cwd=None) -> subprocess.CompletedProcess:
            # API-CONTRACT §5.3.6 beschreibt `subprocess.run(..., capture_
            # output=True, text=True, timeout=...)`; dasselbe Verhalten wird
            # hier ueber Popen+communicate erreicht, weil `record_child_start`
            # die ECHTE PID braucht, BEVOR der Kindprozess beendet ist --
            # `subprocess.run`s `CompletedProcess` liefert keine PID.
            # N4-N3 Fix (01_GENERALREVIEW.md §3 "cwd/env nicht verbindlich
            # gebunden"): `cwd` wird HIER EXPLIZIT an Popen gereicht --
            # derselbe Wert, der oben an `register_child` gebunden wurde --
            # statt sich auf den (nicht in jedem Fall identischen) geerbten
            # Prozess-cwd zu verlassen.
            start_utc = _utcnow_iso()
            proc = subprocess.Popen(
                argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=child_env, cwd=child_cwd,
            )
            EARLY_GUARD.record_child_start(role=role, pid=proc.pid, ppid=os.getpid(), argv=argv, utc=start_utc)
            _append_child_event(event="child_start", role=role, process_id=child_id,
                                 pid=proc.pid, ppid=os.getpid(), utc=start_utc)

            # N4-N3 Fix (01_GENERALREVIEW.md §5 "Timeout/Startausnahme kann
            # Kindkanaele/Ereignisse verlieren"): bei Timeout ODER jeder
            # anderen Ausnahme waehrend `communicate` wird das Kind trotzdem
            # terminiert/gereapt, ein echtes Endereignis registriert und
            # JEDER gestartete Kanal als Rohdatei gesichert (auch leer) --
            # NIE erst nach einer Assertion. Der ORIGINALE Fehler wird
            # danach weitergereicht (kein stilles Verschlucken).
            try:
                stdout, stderr = proc.communicate(timeout=30)
            except Exception:
                proc.kill()
                stdout, stderr = proc.communicate()
                rc = proc.returncode if proc.returncode is not None else -1
                end_utc = _utcnow_iso()
                EARLY_GUARD.record_child_end(role=role, pid=proc.pid, rc=rc, utc=end_utc)
                _append_child_event(event="child_end", role=role, process_id=child_id,
                                     pid=proc.pid, rc=rc, utc=end_utc)
                (exports_dir / f"{child_id}.stdout").write_text(stdout or "", encoding="utf-8")
                (exports_dir / f"{child_id}.stderr").write_text(stderr or "", encoding="utf-8")
                _persist_g2_raw_channel(
                    child_id, stdout=stdout, stderr=stderr,
                    meta={"role": role, "process_id": child_id, "pid": proc.pid,
                          "ppid": os.getpid(), "argv": list(argv), "cwd": child_cwd,
                          "env": dict(child_env), "start_utc": start_utc,
                          "end_utc": end_utc, "rc": rc},
                )
                raise

            rc = proc.returncode
            end_utc = _utcnow_iso()
            EARLY_GUARD.record_child_end(role=role, pid=proc.pid, rc=rc, utc=end_utc)
            _append_child_event(event="child_end", role=role, process_id=child_id,
                                 pid=proc.pid, rc=rc, utc=end_utc)
            # I4.3: stdout UND stderr je Kind VOR den Assertions als
            # Rohdatei sichern -- auch leere Streams als 0-Byte-Datei.
            (exports_dir / f"{child_id}.stdout").write_text(stdout or "", encoding="utf-8")
            (exports_dir / f"{child_id}.stderr").write_text(stderr or "", encoding="utf-8")
            # G3 (01_GENERALREVIEW.md §4): zusaetzliche bleibende Kopie
            # samt vollstaendigem context/pid/ppid/argv/cwd/env/start/end/
            # exit -- `exports_dir` selbst wird in `tearDown` geloescht.
            _persist_g2_raw_channel(
                child_id, stdout=stdout, stderr=stderr,
                meta={"role": role, "process_id": child_id, "pid": proc.pid,
                      "ppid": os.getpid(), "argv": list(argv), "cwd": child_cwd,
                      "env": dict(child_env), "start_utc": start_utc,
                      "end_utc": end_utc, "rc": rc},
            )
            return subprocess.CompletedProcess(argv, rc, stdout, stderr)

        write_proc = _run_child("child-writer", writer_id, writer_argv, writer_env, writer_cwd)
        self.assertEqual(write_proc.returncode, 0, write_proc.stderr)
        self.assertIn("WROTE_A:True", write_proc.stdout)
        self.assertIn("WROTE_B:False:True", write_proc.stdout, write_proc.stdout)
        self.assertNotIn(FAKE_TOKEN, write_proc.stderr, "Token darf nie in Prozess-Stderr erscheinen.")
        self.assertNotIn(FAKE_TOKEN, write_proc.stdout, "Token darf nie in Prozess-Stdout erscheinen.")

        marker_b = setup_mod._pending_marker_path(env_path_b)
        self.assertTrue(marker_b.exists(), "B-Pending-Marker muss nach dem Schreiberkind belegt bleiben.")

        read_proc = _run_child("child-reader", reader_id, reader_argv, reader_env, reader_cwd)
        self.assertEqual(read_proc.returncode, 0, read_proc.stderr)
        for resolver_name in ("setup", "launcher"):
            self.assertIn(f"ALL_MATCH_A_{resolver_name}:True", read_proc.stdout, read_proc.stdout)
            self.assertIn(f"HOLD_B_{resolver_name}:True", read_proc.stdout, read_proc.stdout)
        self.assertNotIn(FAKE_TOKEN, read_proc.stdout, "Token darf nie in Prozess-Stdout erscheinen.")
        self.assertNotIn(FAKE_TOKEN, read_proc.stderr, "Token darf nie in Prozess-Stderr erscheinen.")
        self.assertTrue(marker_b.exists(), "Pending bleibt nach dem Leserkind unveraendert bestehen.")

        # I1.4/I5.1: eigener before/after-Export je Kind, Elterndateien NICHT
        # ueberschrieben. N4-N3 Fix (01_GENERALREVIEW.md §3 "Profil- und
        # Runner-Kinderwurzeln"): diese Pfade liegen im EIGENEN privaten
        # Bereich jedes Kindes (Mains Plan), fuer DIESEN Elternprozess nur
        # ueber `artifact_read_paths` lesbar -- NICHT mehr im
        # Eltern-Capture-Ordner `exports_dir`.
        for child_id, before_path, after_path in (
            (writer_id, writer_before_path, writer_after_path),
            (reader_id, reader_before_path, reader_after_path),
        ):
            before = json.loads(Path(before_path).read_text(encoding="utf-8"))
            after = json.loads(Path(after_path).read_text(encoding="utf-8"))
            self.assertEqual(before["phase"], "before")
            self.assertEqual(after["phase"], "after")
            self.assertEqual(after["completion_status"], "completed")
            self.assertEqual(after["counters"]["unexpected_blocked"], 0)
            self.assertEqual(_support_mod.validate_export_schema(before), [])
            self.assertEqual(_support_mod.validate_export_schema(after), [])
            self.assertNotIn(FAKE_TOKEN, json.dumps(before))
            self.assertNotIn(FAKE_TOKEN, json.dumps(after))

            # R2 (01_GENERALREVIEW.md §3 "Writer-/Readerphasen ... gehen im
            # Cleanup verloren -- die neue dauerhafte Metadaten-/Rohstrom-
            # kopie enthaelt diese eigenen Phasen und Kontexte nicht"):
            # dieselben tatsaechlich gelesenen/geprueften Phasen-/Kontext-
            # originale zusaetzlich dauerhaft sichern -- NOCH im Testkoerper,
            # vor jedem spaeteren Fixturecleanup (`exports_dir`/`contexts_dir`
            # liegen im Solo-Fallback unter `self._tmp_dir(...)`, werden also
            # in `tearDown` entfernt; im Runner-Lauf liegen sie in je einer
            # eigenen Kindwurzel, die dieser Parent sonst nie einsammelt).
            # Ein gescheitertes Pflicht-Copy verhindert den Abschluss.
            own_context_path = writer_context_path if child_id == writer_id else reader_context_path
            persisted_dir = _G2_EVIDENCE_DIR / f"i4-{child_id}"
            persisted_dir.mkdir(parents=True, exist_ok=True)
            try:
                (persisted_dir / "before.json").write_text(
                    json.dumps(before, indent=2, sort_keys=True), encoding="utf-8",
                )
                (persisted_dir / "after.json").write_text(
                    json.dumps(after, indent=2, sort_keys=True), encoding="utf-8",
                )
                if own_context_path and Path(own_context_path).is_file():
                    shutil.copy2(own_context_path, persisted_dir / "context.json")
                if events_path.is_file():
                    shutil.copy2(events_path, persisted_dir / "child_events.jsonl")
            except OSError as exc:
                self.fail(
                    f"{child_id}: Pflicht-Copy der eigenen Writer-/Reader-Phasen-/Kontextoriginale "
                    f"ist gescheitert ({exc.__class__.__name__}: {exc}) -- Abschluss verhindert."
                )

        # ─── O6-A (RELEASE-CASES.json, G2): echter Cloud->Local->Cloud-
        # Setup-/Rewire-/Factory-Zusammenhang -- im SELBEN Parentprozess
        # UND in zwei vorab geplanten FRISCHEN O6-A-Testkindprozessen
        # (Vertragsanforderung, s. `_o6a_run_cycle`/`_o6a_run_in_two_fresh_
        # children`). Die obigen Schreib-/Lesekinder bleiben unveraendert
        # erhalten -- das hier ist eine eng ergaenzte, GETRENNTE Kinderpaar-
        # Anforderung fuer den Setup-/Rewire-/Factoryzyklus selbst.
        self._o6a_run_cycle("parent")
        self._o6a_run_in_two_fresh_children()

    def _o6a_run_cycle(self, tag: str) -> None:
        """G2 (O6-A.A1/A2, 01_NATIVER_AUFTRAG.md §D): EIN bestehendes
        eigenes Preset (cache=True, aktuelle KB, unveraenderte Preset-ID)
        durchlaeuft Cloud->Local->Cloud. Die Wahl wird je Phase ueber die
        ECHTEN Bedienwege `launcher_mod.action_rekeys()` (persistiert) und
        `launcher_mod._finish_installed_connection(cfg)` (Localzweig:
        `_ensure_owui_local_connection` + `_rewire_preset_base_model_local`;
        Cloudzweig: vorhandener Cloudanschluss + `ensure_litellm_autowire`)
        angewandt -- JEDE Double-Zustandsaenderung (Connection-Pins,
        Preset-`base_model_id`) entsteht dadurch AUSSCHLIESSLICH aus
        echten HTTP-Mutationsrequests dieser produktiven Aufrufer, nie aus
        einem direkt gesetzten Feld. Nach jeder Phase lesen die ECHTE
        `scripts/mmo_sim.py:_resolve_active_gm_route` UND BEIDE
        `mmo_sim/adapters/factories.py`-Default-Factories den dann
        gueltigen Zustand und bauen die ECHTEN Adapter (`GmOwuiTransport`/
        `PersonaApiDriver`) -- deren `is_dollar_billed` ist eine abgeleitete
        Folge, nie ein Konstruktorargument dieses Tests."""
        owui_url = "http://127.0.0.1:19080"
        owui_key = f"owui-o6a-{tag}-key-not-secret"
        preset_id = f"zeitriss-o6a-{tag}-preset"
        kb_id = f"kb-o6a-{tag}"
        cloud_persona_base = "https://openrouter.example/api/v1"
        cloud_persona_model = f"anthropic/claude-o6a-{tag}-cloud"
        cloud_persona_key = f"sk-or-o6a-{tag}-cloud-not-secret"
        cloud_upstream_model = f"openrouter/o6a-{tag}-cloud-upstream"
        local_base_url = FAKE_BASE_URL
        local_model = FAKE_MODEL
        local_token = FAKE_TOKEN
        litellm_master_key = f"sk-litellm-o6a-{tag}-not-secret"
        litellm_url = "http://127.0.0.1:4000/v1"

        double = _O6AStatefulOwuiDouble(owui_url)
        double.seed_preset(
            preset_id, base_model_id=cloud_upstream_model, kb_id=kb_id,
            system=f"Du bist die SL (O6-A {tag}).",
        )
        # "vorhandener Cloudanschluss/Autowire" (02_ABNAHME_UND_RUECKGABE.md
        # §3 G2-Zeile): die LiteLLM-Connection ist bereits idempotent
        # etabliert, BEVOR Leg 1 beginnt -- Anfangsfixture, keine Mutation.
        double.seed_connection(
            url=litellm_url, key=litellm_master_key,
            model_ids=[cloud_upstream_model], tags=["cached"],
        )

        cfg = {
            "project": f"O6AProj-{tag}", "default_variant": "default",
            "variants": {"default": {
                "preset_id": preset_id, "preset_name": f"O6AProj-{tag}", "cache": True,
                "model": cloud_upstream_model, "litellm_routing": cloud_upstream_model,
            }},
            "litellm": {"routing_model": cloud_upstream_model, "port": 4000},
        }

        tmp_route_repo = self._tmp_dir(f"o6a-{tag}-route-repo")
        (tmp_route_repo / "setup.json").write_text(json.dumps(cfg), encoding="utf-8")
        tmp_home = self._tmp_dir(f"o6a-{tag}-home")
        tmp_litellm_repo = self._tmp_dir(f"o6a-{tag}-litellm-repo")
        (tmp_litellm_repo / "scripts" / "litellm").mkdir(parents=True)
        (tmp_litellm_repo / "scripts" / "litellm" / ".env").write_text(
            f"LITELLM_MASTER_KEY={litellm_master_key}\n", encoding="utf-8",
        )
        data_dir = self._tmp_dir(f"o6a-{tag}-gm-data")

        # G2 (01_GENERALREVIEW.md §3 "Persona-Kausalitaet" / 01_NATIVER_
        # RESTAUFTRAG.md §D "Persona-Rueckweg"): EINMALIGES Fixture-Setup
        # VOR dem Zyklus (ausdruecklich zulaessig) -- eine gueltige
        # GESPEICHERTE Cloud-Ausgangskonfiguration in genau der Datei, die
        # `setup._auto_load_owui_env()`/`resolve_model_provider()` ueber
        # das unten gemockte `Path.home()` tatsaechlich lesen. Dadurch
        # entsteht die Cloud-Persona-Route in JEDER Phase aus dem
        # tatsaechlichen Provider-/Autoload-/Factoryweg -- die drei Legs
        # setzen/entfernen die drei Persona-API-Felder NICHT mehr von Hand
        # (vorheriger Defekt: das trieb den bewussten Explicit-Override-
        # Zweig statt des normalen `self_resolved`-Rueckwegs). Der gueltige
        # Override-Vorrang samt Billingcleanup bleibt als SEPARATER,
        # korrekt benannter Gegenbeleg erhalten
        # (`test_o6a_persona_explicit_override_keeps_priority_over_local_with_billing_cleanup`).
        (tmp_home / ".openwebui_env").write_text(
            "# synthetische gespeicherte Cloud-Ausgangskonfiguration (Testfixture)\n"
            f"MMO_SIM_PERSONA_API_BASE_URL={cloud_persona_base}\n"
            f"MMO_SIM_PERSONA_API_KEY={cloud_persona_key}\n"
            f"MMO_SIM_PERSONA_API_MODEL={cloud_persona_model}\n",
            encoding="utf-8",
        )

        mmo_sim_module = _o6a_load_mmo_sim_module()
        persona_calls: list[dict] = []

        def _decode_body(raw):
            if raw is None:
                return None
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
                return raw if isinstance(raw, str) else raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw

        def _router(req, timeout=None, context=None):
            url = req.full_url
            if url.startswith(owui_url):
                return double(req, timeout=timeout, context=context)
            if url == f"{cloud_persona_base}/chat/completions":
                persona_calls.append({
                    "phase": double.current_phase, "role": "persona", "which": "cloud",
                    "url": url, "model": cloud_persona_model,
                    "request_body": _decode_body(req.data),
                    "auth": req.headers.get("Authorization"),
                })
                return _O6AFakeResponse(200, json.dumps({
                    "choices": [{"message": {"content": "Cloud-Persona-Antwort (O6-A)."}}],
                    "usage": {"prompt_tokens": 6, "completion_tokens": 2},
                }).encode("utf-8"))
            if url == f"{local_base_url}/chat/completions":
                persona_calls.append({
                    "phase": double.current_phase, "role": "persona", "which": "local",
                    "url": url, "model": local_model,
                    "request_body": _decode_body(req.data),
                    "auth": req.headers.get("Authorization"),
                })
                return _O6AFakeResponse(200, json.dumps({
                    "choices": [{"message": {"content": "Local-Persona-Antwort (O6-A)."}}],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 2},
                }).encode("utf-8"))
            raise AssertionError(f"unerwarteter Request im O6-A-Zyklus ({tag}): {req.get_method()} {url}")

        saved_env = dict(os.environ)
        for key in (
            "OPENWEBUI_URL", "OPENWEBUI_API_KEY", "OPENROUTER_API_KEY",
            "MMO_SIM_PERSONA_CLI", "MMO_SIM_PERSONA_API_BASE_URL", "MMO_SIM_PERSONA_API_KEY",
            "MMO_SIM_PERSONA_API_MODEL", "MMO_SIM_PERSONA_API_MAX_TOKENS",
            "MMO_SIM_PERSONA_API_DOLLAR_BILLED", "MMO_SIM_GM_TRANSPORT_DOUBLE",
            o6a_factories_mod._LOCAL_TOKENHOST_RESOLVED_MARKER,
        ):
            os.environ.pop(key, None)
        try:
            with mock.patch.object(Path, "home", return_value=tmp_home), \
                 mock.patch.object(launcher_mod, "REPO", tmp_litellm_repo), \
                 mock.patch("urllib.request.urlopen", _router), \
                 mock.patch.object(setup_mod, "_owui_container_network_mode", return_value=None), \
                 mock.patch.object(launcher_mod.setup_module, "_owui_container_network_mode", return_value=None):
                # B/G3 (01_GENERALREVIEW.md §4, 02_NATIVER_RESTAUFTRAG.md §B):
                # `_owui_container_network_mode()` ist der aeussere
                # Hoststatusrand, den `_ensure_owui_litellm_connection`
                # (ueber `ensure_litellm_autowire`, Cloudzweig) im echten
                # LiteLLM-Autowire erreicht -- real ein `subprocess.run(
                # ["docker","inspect",...])`. Der Guard faengt diesen echten
                # `subprocess.Popen`-Versuch unautorisiert ab (exportiert als
                # `unexpected_blocked subprocess_popen`, 6 im r1-Profilparent-
                # after). Dieser Rand wird HIER synthetisch kontrolliert
                # (liefert `None`, dieselbe "nicht ermittelbar"-Antwort, die
                # die Funktion auch bei fehlendem Docker real liefert) --
                # BEVOR ein realer Subprozessversuch entsteht. Die produktive
                # Auswahl/Connection-/Presetmutation/Re-GET/Fehlerweitergabe
                # und beide Factories bleiben vollstaendig real; nur dieser
                # eine aeussere Blattknoten ist kontrolliert, kein Mocken
                # des gesamten Autowire-/Rewirepfads. `launcher_mod.
                # setup_module` ist eine EIGENE, ueber `launcher.py`s
                # eigenes `import setup as setup_module` real importierte
                # Modulinstanz (sys.modules["setup"]) -- NICHT identisch mit
                # `setup_mod` (der hier unter dem Namen "o1_setup_under_test"
                # separat per Dateipfad geladenen Instanz). `_finish_
                # installed_connection` -> `ensure_litellm_autowire` ruft
                # tatsaechlich IN DIESER dritten Instanz auf, deshalb werden
                # beide Modulobjekte gepatcht.
                client = setup_mod.APIClient(owui_url, owui_key)

                def _assert_upstream(expected_model: str, msg: str) -> None:
                    preset = client.get_model(preset_id)
                    self.assertIsNotNone(preset, msg)
                    self.assertEqual(preset["base_model_id"], expected_model, msg)
                    self.assertEqual(
                        preset["id"], preset_id,
                        "Preset-ID bleibt ueber alle drei Legs unveraendert (Preset != Upstreammodell).",
                    )
                    kb_ids = {e.get("id") for e in (preset.get("meta") or {}).get("knowledge") or []}
                    self.assertIn(kb_id, kb_ids, "dieselbe aktuelle KB bleibt am Preset gebunden.")

                def _persist_and_finish(leg_label, provider, prompts, getpass_answers):
                    double.current_phase = leg_label
                    prompts_iter = iter(prompts)
                    with mock.patch.object(launcher_mod, "_prompt",
                                            side_effect=lambda *_a, **_k: next(prompts_iter)), \
                         mock.patch("getpass.getpass", side_effect=iter(getpass_answers)), \
                         mock.patch.object(launcher_mod, "_pause", return_value=None):
                        launcher_mod.action_rekeys()
                    reread = setup_mod._read_env_file(tmp_home / ".openwebui_env")
                    self.assertEqual(
                        reread.get(lmp.ENV_KEY_PROVIDER), provider,
                        f"{leg_label}: Providerwahl muss ueber die echte action_rekeys persistiert sein.",
                    )
                    launcher_mod._finish_installed_connection(cfg)

                def _run_gm_and_persona(leg_label, expect_billed, table_id, persona_key, persona_text):
                    double.current_phase = leg_label
                    sl_model, resolved_kb_id = mmo_sim_module._resolve_active_gm_route(tmp_route_repo)
                    self.assertEqual(sl_model, preset_id, leg_label)
                    self.assertEqual(resolved_kb_id, kb_id, leg_label)
                    gm_factory = default_gm_transport_factory(
                        data_dir, _REPO_ROOT, sl_model=sl_model, kb_id=resolved_kb_id,
                    )
                    gm_transport = gm_factory(table_id)
                    self.assertEqual(
                        gm_transport.is_dollar_billed, expect_billed,
                        f"{leg_label}: GM-Billing muss aus der echten Route/Factory-Ableitung stammen.",
                    )
                    gm_result = gm_transport.turn(
                        1, f"Runde ({leg_label}).", output_limit_tokens=gm_transport.output_limit_tokens,
                    )
                    self.assertEqual(gm_result["content"], "GM-Antwort (O6-A).")

                    # R1 (01_GENERALREVIEW.md §3 "tatsaechliche Chatrequests
                    # vor Redaktion pruefen", 02_NATIVER_RESTAUFTRAG.md §C):
                    # die tatsaechlich am Double EINGEGANGENE GM-Request --
                    # VOR jeder Redaktion/jedem Export -- muss rollen-/
                    # phasengebunden stimmen. Der GM-Chatzweig des Doubles
                    # liefert sonst unabhaengig vom empfangenen Body
                    # denselben Erfolg; eine Fehlzuordnung MUSS diesen Test
                    # scheitern lassen. `double.requests[-1]` ist der echte,
                    # noch unredigierte Eintrag genau DIESES Aufrufs.
                    gm_req = double.requests[-1]
                    self.assertEqual(
                        gm_req["phase"], leg_label,
                        f"{leg_label}: GM-Request falscher Phase zugeordnet: {gm_req}",
                    )
                    self.assertEqual(
                        gm_req["request_body"]["model"], preset_id,
                        f"{leg_label}: GM-Request-Body traegt nicht dieselbe eigene Preset-ID: {gm_req}",
                    )
                    gm_kb_ids = {
                        f.get("id") for f in (gm_req["request_body"].get("files") or [])
                        if isinstance(f, dict)
                    }
                    self.assertIn(
                        kb_id, gm_kb_ids,
                        f"{leg_label}: GM-Request-Body bindet nicht die aktuelle KB: {gm_req}",
                    )
                    self.assertEqual(
                        gm_req["auth"], f"Bearer {owui_key}",
                        f"{leg_label}: tatsaechlich verwendete OWUI-Authorization != erwarteter "
                        f"OWUI-Key der Phase (vor Redaktion geprueft): {gm_req!r}",
                    )
                    # Cloud-GM ohne Request-max_tokens ist KEIN Fehler
                    # (01_GENERALREVIEW.md §3) -- nur korrekt zuordnen,
                    # WELCHER Fall vorliegt, aus dem tatsaechlichen Request-/
                    # Presetbezug (`gm_transport.output_limit_tokens`), keine
                    # erfundene feste Zahl (Rueckkehr zu 4096 verlangt NICHT
                    # die Wiederherstellung von 64000).
                    if gm_transport.output_limit_tokens:
                        self.assertEqual(
                            gm_req["request_body"].get("max_tokens"), gm_transport.output_limit_tokens,
                            f"{leg_label}: GM-Request-Limit != tatsaechlichem Request-/Presetbezug: {gm_req}",
                        )
                    else:
                        self.assertNotIn(
                            "max_tokens", gm_req["request_body"],
                            f"{leg_label}: unerwarteter max_tokens-Key ohne konfiguriertes Limit: {gm_req}",
                        )

                    persona_factory = default_persona_driver_factory(data_dir)
                    persona_driver = persona_factory(persona_key)
                    self.assertEqual(
                        persona_driver.is_dollar_billed, expect_billed,
                        f"{leg_label}: Persona-Billing muss aus der echten Factory-Ableitung stammen.",
                    )
                    decision = persona_driver.decide({"system": "s", "user": "u"})
                    self.assertEqual(decision.text, persona_text)

                    # R1: der Persona-Chatzweig behandelt die empfangene
                    # Authorization bisher NICHT als Erfolgsbedingung --
                    # tatsaechliche served-ID/Route UND eigener Rollenkey
                    # (VOR Redaktion) muessen zur Phase passen. Das
                    # Metafeld "model" (von `_router` gesetzt) ersetzt
                    # `request_body["model"]` NICHT -- beide werden
                    # unabhaengig gegen die bei Phasenkonstruktion bekannten
                    # erwarteten Literale (nicht gegen `persona_driver.
                    # config`, um keinen zirkulaeren Vergleich zu bauen)
                    # gebunden.
                    persona_req = persona_calls[-1]
                    expected_persona_model = cloud_persona_model if expect_billed else local_model
                    expected_persona_key = cloud_persona_key if expect_billed else local_token
                    self.assertEqual(
                        persona_req["phase"], leg_label,
                        f"{leg_label}: Persona-Request falscher Phase zugeordnet: {persona_req}",
                    )
                    self.assertEqual(
                        persona_req["model"], expected_persona_model,
                        f"{leg_label}: Persona-Metafeld 'model' != erwartete served-ID der Phase.",
                    )
                    self.assertEqual(
                        persona_req["request_body"]["model"], expected_persona_model,
                        f"{leg_label}: Persona-Request-Body['model'] != erwartete served-ID/Route "
                        f"(Metafeld allein ersetzt request_body.model nicht): {persona_req}",
                    )
                    self.assertEqual(
                        persona_req["auth"], f"Bearer {expected_persona_key}",
                        f"{leg_label}: tatsaechlicher Persona-Rollenkey != erwarteter Persona-Key "
                        f"der Phase (vor Redaktion geprueft): {persona_req!r}",
                    )
                    self.assertEqual(
                        persona_req["request_body"].get("max_tokens"), persona_driver.config.max_tokens,
                        f"{leg_label}: Persona-Request-Limit != effektivem Rollenlimit: {persona_req}",
                    )

                # ── Leg 1: Cloud (vor dem lokalen Abschnitt) ─────────────
                # G2-Fix (01_GENERALREVIEW.md §3 "Persona-Kausalitaet"):
                # KEIN manuelles Setzen der drei Persona-API-Felder mehr --
                # die Cloud-Persona-Route entsteht aus der oben VOR dem
                # Zyklus persistierten gespeicherten Cloud-Ausgangskonfig
                # ueber den echten `setup._auto_load_owui_env()`/
                # `_maybe_default_local_tokenhost_persona_env()`-Autoloadweg
                # (normaler `self_resolved`-Rueckweg, kein bewusster
                # Explicit-Override-Zweig).
                _persist_and_finish(
                    f"{tag}-leg1-cloud", lmp.PROVIDER_CLOUD,
                    prompts=[owui_url, "cloud"],
                    getpass_answers=[owui_key, cloud_persona_key],
                )
                _assert_upstream(cloud_upstream_model, f"{tag}-leg1: Preset zeigt auf den Cloud-Upstream.")
                _run_gm_and_persona(
                    f"{tag}-leg1-cloud", True,
                    f"o6a-{tag}-cloud-1", f"o6a-{tag}-persona-cloud-1",
                    "Cloud-Persona-Antwort (O6-A).",
                )

                # ── Leg 2: Local -- kein manuelles Env-Popping mehr noetig
                # (nichts wurde manuell gesetzt): der normale Rueckweg in
                # `_maybe_default_local_tokenhost_persona_env()` erkennt den
                # jetzt per `action_rekeys` persistierten `provider=local`
                # selbst und ersetzt die zuvor file-autoloadeten
                # Cloud-Persona-Werte durch die echten lokalen Profilwerte.
                _persist_and_finish(
                    f"{tag}-leg2-local", lmp.PROVIDER_LOCAL,
                    prompts=[owui_url, "local", local_base_url, local_model, ""],
                    getpass_answers=[owui_key, local_token],
                )
                _assert_upstream(
                    local_model, f"{tag}-leg2: Preset zeigt nach dem echten Rewire auf den lokalen Upstream.",
                )
                _run_gm_and_persona(
                    f"{tag}-leg2-local", False,
                    f"o6a-{tag}-local", f"o6a-{tag}-persona-local",
                    "Local-Persona-Antwort (O6-A).",
                )

                # ── Leg 3: Cloud (nach dem lokalen Abschnitt) -- derselbe
                # Preset muss durch den echten Autowire-Rueckwechsel wieder
                # auf den Cloud-Upstream zeigen. G2-Fix: KEIN manuelles
                # Wiedersetzen der drei Persona-Felder mehr. Der echte
                # Rueckweg in `_maybe_default_local_tokenhost_persona_env()`
                # sieht `provider=cloud` (von `action_rekeys` persistiert),
                # erkennt die noch stehenden LOKALEN Werte als `self_
                # resolved` und entfernt sie SELBST (produktive Bereinigung,
                # kein Testeingriff) -- der nachfolgende Factory-Fallback
                # laedt daraufhin ueber `_auto_load_owui_env()` wieder genau
                # die vor dem Zyklus gespeicherte Cloud-Ausgangskonfiguration
                # aus `~/.openwebui_env`. Das ist der tatsaechlich
                # beobachtete normale Rueckweg, nicht nur behauptet.
                _persist_and_finish(
                    f"{tag}-leg3-cloud", lmp.PROVIDER_CLOUD,
                    prompts=[owui_url, "cloud"],
                    getpass_answers=[owui_key, cloud_persona_key],
                )
                _assert_upstream(
                    cloud_upstream_model, f"{tag}-leg3: echter Autowire-Ruecklauf auf den Cloud-Upstream.",
                )
                _run_gm_and_persona(
                    f"{tag}-leg3-cloud", True,
                    f"o6a-{tag}-cloud-2", f"o6a-{tag}-persona-cloud-2",
                    "Cloud-Persona-Antwort (O6-A).",
                )
        finally:
            os.environ.clear()
            os.environ.update(saved_env)

        # Dasselbe Preset (dieselbe Preset-ID im Request-Body/-Pfad) in
        # ALLEN drei GM-Beinen -- "am selben Preset", kein neues Preset
        # pro Leg.
        gm_chat_calls = [c for c in double.calls if c == ("POST", "/api/chat/completions")]
        self.assertEqual(len(gm_chat_calls), 3, f"{tag}: genau ein echter GM-Request je Leg (Cloud/Local/Cloud).")
        model_update_calls = [c for c in double.calls if c == ("POST", "/api/v1/models/model/update")]
        self.assertEqual(
            len(model_update_calls), 2,
            f"{tag}: genau zwei reale Upstream-Mutationen (Local-Rewire in Leg 2 + Cloud-Ruecklauf "
            f"in Leg 3; Leg 1 ist idempotent, keine Mutation noetig): {double.calls}",
        )
        cloud_persona_calls = [c for c in persona_calls if c["which"] == "cloud"]
        local_persona_calls = [c for c in persona_calls if c["which"] == "local"]
        self.assertEqual(len(cloud_persona_calls), 2, f"{tag}: Cloud-Persona-Requests nur in Leg 1+3.")
        self.assertEqual(len(local_persona_calls), 1, f"{tag}: Local-Persona-Request nur in Leg 2.")
        # Jeder aufgezeichnete Persona-Request ist tatsaechlich einer realen
        # Zyklusphase zugeordnet (kein Request ohne Phase -- `current_phase`
        # wurde vom Zyklustreiber je Leg gesetzt, nicht konstant).
        for c in persona_calls:
            self.assertIsNotNone(c["phase"], f"{tag}: Persona-Request ohne Phasenzuordnung: {c}")
        for r in double.requests:
            self.assertIsNotNone(r["phase"], f"{tag}: GM/OWUI-Request ohne Phasenzuordnung: {r}")

        # Secrets der jeweils ANDEREN Rolle/Leg (und generell) duerfen
        # nirgends im LEGACY-Callprotokoll (Methode+Pfad, nie Bodywerte)
        # auftauchen -- unveraendert erhalten.
        all_calls_text = json.dumps(double.calls)
        for leaked in (local_token, cloud_persona_key, owui_key, litellm_master_key):
            self.assertNotIn(leaked, all_calls_text, f"{tag}: Geheimniswert darf nie im Callprotokoll stehen.")

        # G2 (01_GENERALREVIEW.md §3 "Requestbelege"): tatsaechlich
        # empfangene Request-Bodies pro Prozess/Phase/Rolle, VOR dem Export
        # redigiert (keine echten/unredigierten Tokenwerte). Schreibt in das
        # bleibende Evidenzziel (nicht ueber `self._tmp_dir`, also von
        # `tearDown` unberuehrt). `double.requests`/`persona_calls` ENTHALTEN
        # bewusst die echten Werte (Rolleninhalt/Authzuordnung intern
        # pruefbar) -- nur der dauerhafte EXPORT wird redigiert.
        secrets_to_redact = [
            s for s in (local_token, cloud_persona_key, owui_key, litellm_master_key) if s
        ]

        def _redact(obj):
            if isinstance(obj, dict):
                return {k: _redact(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_redact(v) for v in obj]
            if isinstance(obj, str):
                red = obj
                for s in secrets_to_redact:
                    if s in red:
                        red = red.replace(s, "<REDACTED>")
                return red
            return obj

        evidence_payload = {
            "tag": tag, "process_id": os.getpid(),
            "gm_owui_requests": _redact(double.requests),
            "persona_requests": _redact(persona_calls),
        }
        evidence_text = json.dumps(evidence_payload, indent=2, sort_keys=True, default=str)
        for leaked in secrets_to_redact:
            self.assertNotIn(
                leaked, evidence_text,
                f"{tag}: Geheimniswert nach Redaktion weiterhin im exportierten Evidenztext.",
            )
        (_G2_EVIDENCE_DIR / f"o6a-request-bodies-{tag}-{os.getpid()}.json").write_text(
            evidence_text, encoding="utf-8",
        )

    def _o6a_run_in_two_fresh_children(self) -> None:
        """G2 (01_NATIVER_AUFTRAG.md §D / 02_ABNAHME_UND_RUECKGABE.md §3
        G2-Zeile): derselbe echte Setup-/Rewire-/Factory-Zusammenhang wie
        `_o6a_run_cycle` laeuft zusaetzlich in ZWEI vorab geplanten
        FRISCHEN Testkindprozessen -- eine konkrete Vertragsanforderung,
        keine wiederbelebte globale Laufquote. Jedes Kind startet DIESE
        Testdatei direkt (derselbe `__main__`-Zweig, der auch Standalone-
        Laeufe trägt) mit einem EXPLIZITEN Testnamen -- `unittest.main()`
        waehlt darueber GENAU die eine `o6a_child_*_cycle`-Methode aus,
        baut dabei frisch den Primaerguard (Solo-Self-Bootstrap) und importiert
        die Produktmodule frisch -- kein geteilter Zustand mit dem
        Elternprozess oder dem anderen Kind."""
        exports_dir = self._tmp_dir("o6a-children-capture")
        this_file = str(_HERE / "test_local_tokenhost_profile_2026_11_14.py")
        base_env: dict = {"HOME": pwd.getpwuid(os.getuid()).pw_dir}
        for key in ("PATH", "LANG", "LC_ALL", "LC_CTYPE"):
            if os.environ.get(key):
                base_env[key] = os.environ[key]

        for idx, method_name in enumerate((
            "LocalTokenhostProfileTests.o6a_child_one_cycle",
            "LocalTokenhostProfileTests.o6a_child_two_cycle",
        ), start=1):
            child_id = f"o6a-child-{idx}"
            # I2.2 (anders als die write/read-Kinder oben): KEIN `-I`/`-S`
            # -- dieses Kind laedt `mmo_sim`/`scripts/mmo_sim.py` real
            # (ueber `_o6a_load_mmo_sim_module`), dessen Importkette echte
            # Drittpakete (`jsonschema`) aus dem normalen Site-/User-Site-
            # Pfad braucht; `-I` schliesst genau den User-Site-Pfad aus, in
            # dem dieses Paket hier tatsaechlich installiert ist. `-B`
            # bleibt (kein Bytecode-Schreiben ausserhalb privater Wurzeln).
            argv = [sys.executable, "-B", this_file, method_name]
            child_env = dict(base_env)
            EARLY_GUARD.register_child(
                role=child_id, argv=argv, fixture_paths=[],
                export_id=f"{child_id}-export", count=1,
                minimal_env=child_env, cwd=None,
            )
            start_utc = _utcnow_iso()
            proc = subprocess.Popen(
                argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=child_env,
            )
            EARLY_GUARD.record_child_start(role=child_id, pid=proc.pid, ppid=os.getpid(), argv=argv, utc=start_utc)
            try:
                stdout, stderr = proc.communicate(timeout=120)
            except Exception:
                proc.kill()
                stdout, stderr = proc.communicate()
                rc = proc.returncode if proc.returncode is not None else -1
                end_utc = _utcnow_iso()
                EARLY_GUARD.record_child_end(role=child_id, pid=proc.pid, rc=rc, utc=end_utc)
                (exports_dir / f"{child_id}.stdout").write_text(stdout or "", encoding="utf-8")
                (exports_dir / f"{child_id}.stderr").write_text(stderr or "", encoding="utf-8")
                _persist_g2_raw_channel(
                    child_id, stdout=stdout, stderr=stderr,
                    meta={"role": child_id, "process_id": child_id, "pid": proc.pid,
                          "ppid": os.getpid(), "argv": list(argv), "cwd": None,
                          "env": dict(child_env), "start_utc": start_utc,
                          "end_utc": end_utc, "rc": rc, "method_name": method_name},
                )
                raise
            rc = proc.returncode
            end_utc = _utcnow_iso()
            EARLY_GUARD.record_child_end(role=child_id, pid=proc.pid, rc=rc, utc=end_utc)
            (exports_dir / f"{child_id}.stdout").write_text(stdout or "", encoding="utf-8")
            (exports_dir / f"{child_id}.stderr").write_text(stderr or "", encoding="utf-8")
            # G3 (01_GENERALREVIEW.md §4 "O6-A-stdout/stderr liegt ... in
            # einem durch tearDown geloeschten Fixtureverzeichnis"):
            # bleibende Zusatzkopie samt vollstaendigem Kontext.
            _persist_g2_raw_channel(
                child_id, stdout=stdout, stderr=stderr,
                meta={"role": child_id, "process_id": child_id, "pid": proc.pid,
                      "ppid": os.getpid(), "argv": list(argv), "cwd": None,
                      "env": dict(child_env), "start_utc": start_utc,
                      "end_utc": end_utc, "rc": rc, "method_name": method_name},
            )
            self.assertEqual(
                rc, 0,
                f"{child_id} ({method_name}) muss den echten O6-A-Setup-/Rewire-/Factoryzyklus "
                f"in einem frischen Interpreter fehlerfrei durchlaufen:\n{stderr}",
            )
            combined = (stdout or "") + (stderr or "")
            self.assertNotIn(FAKE_TOKEN, combined, f"{child_id}: Token darf nie im Kindkanal erscheinen.")

            # R2 (01_GENERALREVIEW.md §3 "die zwei realen O6-A-Kinder haben
            # keine eigenen before/after/context und keine eigenen Request-
            # dateien -- liegen in separaten Kindwurzeln; ein Parent-
            # verzeichnis-Copy erfasst diese separaten Kindwurzeln nicht"):
            # den vom Kind selbst gedruckten Marker lesen (das Kind hat
            # seine eigenen Exportinhalte bereits SELBST aus seiner eigenen
            # Wurzel gelesen, s. `_o6a_run_cycle_as_own_child`) und dauerhaft
            # in das bleibende Evidenzziel schreiben -- der Parent liest nie
            # selbst aus der fremden Kindwurzel (eigener Guard kennt sie
            # nicht als erlaubten Lesebereich). Ein fehlender Marker oder
            # ein gescheitertes Pflicht-Schreiben verhindert den Abschluss.
            own_export_marker = None
            for line in (stdout or "").splitlines():
                if line.startswith("O6A_CHILD_OWN_EXPORT:"):
                    own_export_marker = line[len("O6A_CHILD_OWN_EXPORT:"):]
            self.assertIsNotNone(
                own_export_marker,
                f"{child_id}: kein O6A_CHILD_OWN_EXPORT-Marker im Kindoutput -- eigene "
                f"before/after/Requestdaten des Kindes nicht auffindbar.\n{stdout}",
            )
            own_export = json.loads(own_export_marker)
            own_before, own_after = own_export["before"], own_export["after"]
            self.assertEqual(_support_mod.validate_export_schema(own_before), [])
            self.assertEqual(_support_mod.validate_export_schema(own_after), [])
            self.assertEqual(own_after["completion_status"], "completed")
            self.assertIsNotNone(
                own_export.get("request_body_text"),
                f"{child_id}: eigene O6-A-Requestdatei (Inhalt) fehlt im Marker.",
            )
            persisted_child_root = _G2_EVIDENCE_DIR / f"{child_id}-own-root"
            try:
                persisted_child_root.mkdir(parents=True, exist_ok=True)
                (persisted_child_root / "before.json").write_text(
                    json.dumps(own_before, indent=2, sort_keys=True), encoding="utf-8",
                )
                (persisted_child_root / "after.json").write_text(
                    json.dumps(own_after, indent=2, sort_keys=True), encoding="utf-8",
                )
                (persisted_child_root / "request-bodies.json").write_text(
                    own_export["request_body_text"], encoding="utf-8",
                )
            except OSError as exc:
                self.fail(
                    f"{child_id}: Pflicht-Schreiben der eigenen Kind-Exportoriginale ist "
                    f"gescheitert ({exc.__class__.__name__}: {exc}) -- Abschluss verhindert."
                )
            # Laufmanifest (01_GENERALREVIEW.md §3 R2: Quelle/Rolle/PID/
            # PPID/argv/cwd/minimale Umgebung/Start-Ende/Exit + Vorher-/
            # Nachherquellenbindung) -- additiv zum bereits bestehenden
            # `_persist_g2_raw_channel`-Meta oben, an derselben bleibenden
            # Evidenzwurzel.
            (_G2_EVIDENCE_DIR / f"{child_id}.manifest.json").write_text(
                json.dumps({
                    "role": child_id, "source": "o6a-fresh-child", "method_name": method_name,
                    "pid": proc.pid, "ppid": os.getpid(), "argv": list(argv),
                    "cwd": None, "minimal_env": dict(child_env),
                    "start_utc": start_utc, "end_utc": end_utc, "exit_code": rc,
                    "own_before_path": str(persisted_child_root / "before.json"),
                    "own_after_path": str(persisted_child_root / "after.json"),
                    "own_request_body_path": str(persisted_child_root / "request-bodies.json"),
                }, indent=2, sort_keys=True, default=str),
                encoding="utf-8",
            )

    # ─── G2-Kindeinstiege (KEIN `test_`-Praefix -- normale Discovery
    # fuehrt sie dadurch NICHT zusaetzlich aus; `unittest.main()` im frisch
    # gestarteten Kindinterpreter waehlt sie ueber den expliziten Namen in
    # `sys.argv` trotzdem gezielt aus, s. `_o6a_run_in_two_fresh_children`). ──

    def o6a_child_one_cycle(self) -> None:
        self._o6a_run_cycle_as_own_child("child1")

    def o6a_child_two_cycle(self) -> None:
        self._o6a_run_cycle_as_own_child("child2")

    def _o6a_run_cycle_as_own_child(self, tag: str) -> None:
        """R2 (01_GENERALREVIEW.md §3 "die zwei realen O6-A-Kinder ... haben
        keine eigenen before/after/context und keine eigenen Requestdateien
        im Paket -- liegen in separaten Kindwurzeln"): dieses EINE O6-A-Kind
        exportiert jetzt SELBST before/after unter seiner eigenen (bereits
        im Modulimport self-bootstrapped) privaten Wurzel. Der Parent kennt
        diese fremde Kindwurzel NICHT als eigenen erlaubten Lese-/Schreib-
        raum -- ein Crossroot-`shutil.copytree` aus dem Elternprozess waere
        selbst eine erwartete `IsolationViolation` (kein Guardabbau/keine
        neue Ausnahme dafuer). Stattdessen liest DIESES Kind seine EIGENEN
        Exportdateien + seine eigene Requestdatei SELBST (innerhalb der
        eigenen Wurzel ausdruecklich erlaubt) und reicht ihren vollen Inhalt
        ueber den bereits vom Parent abgefangenen stdout-Kanal weiter --
        der Parent schreibt sie danach in SEINEN EIGENEN erlaubten
        Schreibraum, ohne je selbst aus der fremden Kindwurzel zu lesen."""
        own_root = Path(EARLY_GUARD.private_write_roots[0])
        before_path = own_root / "o6a-child-own.before.json"
        after_path = own_root / "o6a-child-own.after.json"
        EARLY_GUARD.export_phase(
            "before", before_path, completion_status="running",
            evidence={"test_or_fixture_id": f"o6a-{tag}"},
        )
        status = "failed"
        try:
            self._o6a_run_cycle(tag)
            status = "completed"
        finally:
            EARLY_GUARD.export_phase(
                "after", after_path, completion_status=status,
                evidence={"test_or_fixture_id": f"o6a-{tag}"},
            )
            request_body_path = _G2_EVIDENCE_DIR / f"o6a-request-bodies-{tag}-{os.getpid()}.json"
            payload = {
                "tag": tag, "pid": os.getpid(),
                "before": json.loads(before_path.read_text(encoding="utf-8")),
                "after": json.loads(after_path.read_text(encoding="utf-8")),
                "request_body_text": (
                    request_body_path.read_text(encoding="utf-8")
                    if request_body_path.is_file() else None
                ),
            }
            print("O6A_CHILD_OWN_EXPORT:" + json.dumps(payload, sort_keys=True))

    # ─── G2-Gegenbeleg: gueltiger Explicit-Override + Billingcleanup ─────

    def test_o6a_persona_explicit_override_keeps_priority_over_local_with_billing_cleanup(self):
        """G2 (01_GENERALREVIEW.md §3 "Persona-Kausalitaet" / 01_NATIVER_
        RESTAUFTRAG.md §D "Persona-Rueckweg"): der oben in `_o6a_run_cycle`
        geprueften normalen `self_resolved`-Rueckwegbranche (KEIN manuelles
        Env-Setzen mehr) wird HIER -- separat und korrekt benannt -- der
        GUELTIGE Gegenfall gegenuebergestellt: ein ECHTER, bewusst VOR dem
        Resolveraufruf gesetzter Prozessoverride (Fall a/d in
        `_maybe_default_local_tokenhost_persona_env`s Docstring) behaelt
        Vorrang vor einer gleichzeitig gespeicherten lokalen Profilwahl, UND
        die vom lokalen Resolver zuvor SELBST gesetzten MAX_TOKENS/DOLLAR_
        BILLED-Marker werden bereinigt, wenn sie noch exakt dem eigenen alten
        Fingerabdruck entsprechen (factories.py ~Zeile 316-325). Dies wird
        NICHT als "normaler Rueckweg" ausgegeben -- das ist der bewusste
        Explicit-Override-Zweig."""
        tmp_home = self._tmp_dir("o6a-override-home")
        home_env = tmp_home / ".openwebui_env"
        home_env.write_text(
            "# synthetisches gespeichertes lokales Profil (Testfixture)\n"
            f"{lmp.ENV_KEY_PROVIDER}=local\n"
            "ZEITRISS_LOCAL_BASE_URL=http://127.0.0.1:18001/v1\n"
            "ZEITRISS_LOCAL_MODEL=nemotron-3-super\n"
            "ZEITRISS_LOCAL_API_KEY=test-local-token-not-secret\n"
            "OPENWEBUI_URL=http://127.0.0.1:19080\n"
            "OPENWEBUI_API_KEY=owui-override-key-not-secret\n",
            encoding="utf-8",
        )
        saved_env = dict(os.environ)
        for key in (
            "MMO_SIM_PERSONA_CLI", "MMO_SIM_PERSONA_API_BASE_URL", "MMO_SIM_PERSONA_API_KEY",
            "MMO_SIM_PERSONA_API_MODEL", "MMO_SIM_PERSONA_API_MAX_TOKENS",
            "MMO_SIM_PERSONA_API_DOLLAR_BILLED", o6a_factories_mod._LOCAL_TOKENHOST_RESOLVED_MARKER,
        ):
            os.environ.pop(key, None)
        try:
            with mock.patch.object(Path, "home", return_value=tmp_home):
                # Erst die lokale Wahl real ueber den normalen Rueckweg
                # aufloesen (self_resolved=True, KEIN manueller Override).
                resolved_first = o6a_factories_mod._maybe_default_local_tokenhost_persona_env()
                self.assertTrue(resolved_first, "lokales Profil muss beim ersten Aufruf real aufgeloest werden.")
                self.assertEqual(os.environ.get("MMO_SIM_PERSONA_API_MAX_TOKENS"), "400")
                self.assertEqual(os.environ.get("MMO_SIM_PERSONA_API_DOLLAR_BILLED"), "0")

                # Jetzt ein ECHTER bewusster Override VOR dem naechsten
                # Aufruf -- URL/Key/Modell geaendert, MAX_TOKENS/DOLLAR_
                # BILLED NICHT mitgesetzt (bleiben noch exakt unser alter
                # Fingerabdruck -> muessen bereinigt werden).
                os.environ["MMO_SIM_PERSONA_API_BASE_URL"] = "https://openrouter.example/api/v1"
                os.environ["MMO_SIM_PERSONA_API_KEY"] = "sk-or-override-not-secret"
                os.environ["MMO_SIM_PERSONA_API_MODEL"] = "anthropic/claude-override"

                resolved_second = o6a_factories_mod._maybe_default_local_tokenhost_persona_env()
                self.assertFalse(
                    resolved_second,
                    "ein echter bewusster Override wird NICHT als eigene lokale Aufloesung gemeldet.",
                )
                self.assertEqual(os.environ["MMO_SIM_PERSONA_API_BASE_URL"], "https://openrouter.example/api/v1")
                self.assertEqual(os.environ["MMO_SIM_PERSONA_API_KEY"], "sk-or-override-not-secret")
                self.assertEqual(os.environ["MMO_SIM_PERSONA_API_MODEL"], "anthropic/claude-override")
                # Billingcleanup: die EIGENEN alten MAX_TOKENS/DOLLAR_BILLED-
                # Marker (noch exakt unser Fingerabdruck) wurden entfernt --
                # der Override erbt sie NICHT mehr als lokale Restwerte.
                self.assertNotIn("MMO_SIM_PERSONA_API_MAX_TOKENS", os.environ)
                self.assertNotIn("MMO_SIM_PERSONA_API_DOLLAR_BILLED", os.environ)
        finally:
            os.environ.clear()
            os.environ.update(saved_env)

    # ─── I1/I5: Guardexport -- keine Secrets, keine unerwarteten Blocks ──

    def test_guard_export_status_has_no_secrets_and_zero_unexpected_blocks(self):
        """I1.4/I5.1: Guarddaten sind exportierbar und enthalten weder
        Tokenwerte noch echte Nutzerkonfiguration; normaler Testbetrieb
        in diesem Prozess darf keinen einzigen UNERWARTETEN Block
        ausloesen (Export allein ist kein Wirksamkeitsnachweis, aber eine
        notwendige Teilbedingung)."""
        status = EARLY_GUARD.export_status()
        self.assertEqual(status["counters"]["unexpected_blocked"], 0)
        dump = json.dumps(status)
        self.assertNotIn(FAKE_TOKEN, dump)
        export_path = self._tmp_env_path("guard-export").with_suffix(".json")
        exported = EARLY_GUARD.export_phase("before", export_path)
        self.assertEqual(exported["counters"]["unexpected_blocked"], 0)
        self.assertIn("context_sha256_without_secrets", exported)
        self.assertIn("enforced_read_roots", exported)
        self.assertIn("enforced_write_roots", exported)
        self.assertIn("artifact_read_paths", exported)
        self.assertIn("metadata_ancestor_paths", exported)
        self.assertEqual(exported["phase"], "before")
        self.assertEqual(_support_mod.validate_export_schema(exported), [])
        self.assertTrue(export_path.is_file())
        self.assertNotIn(FAKE_TOKEN, export_path.read_text(encoding="utf-8"))

    # ─── N4-N2: vollstaendige Selbstprobenmatrix (ersetzt die alte einzelne
    # open('w')-Probe, API-CONTRACT-N4N2.md §3 / 02_N4N2_ARBEITSAUFTRAG.md C) ──

    def _assert_guard_blocks(self, op_desc: str, fn) -> None:
        """N4-N3 Fix (01_GENERALREVIEW.md §3 "Negative Netz-/Prozessproben
        koennen bei defektem Guard durchgreifen" / "Die behauptete untere
        IO-Falle ist weiterhin keine solche Falle"): ruft die ECHTE
        oeffentliche API auf -- der installierte Guard-Wrapper bleibt
        aktiv, kein Wegmocken -- und verlangt `IsolationViolation`. Die
        Aufrufer unten binden darunter zusaetzlich eine KONTROLLIERTE
        untere IO-Falle (synthetisches AF_UNIX-Ziel bzw. getrapptes
        `os.posix_spawn`/`os.fork`), sodass ein Guard-Durchgriff NIE einen
        echten Netzversuch oder Prozess erzeugt. Ein Normalerfolg ODER ein
        ANDERER Ausnahmetyp (beide deuten auf einen durchgreifenden Guard
        hin) werden hier wertfrei erfasst und fuehren zu einem EXPLIZITEN,
        klar benannten Testabbruch statt eines stillen/verrauschten
        Fehlschlags."""
        try:
            fn()
        except _support_mod.IsolationViolation:
            return
        except Exception as exc:
            self.fail(
                f"Guard-Bruch bei {op_desc}: erwartete IsolationViolation, echte IO-Falle "
                f"registrierte statt dessen {type(exc).__name__} -- Guardentscheidung hat "
                "nicht VOR der echten Operation gegriffen."
            )
        else:
            self.fail(
                f"Guard-Bruch bei {op_desc}: echte Operation lief ohne IsolationViolation "
                "durch (Breakthrough wertfrei erfasst, Test sofort abgebrochen)."
            )

    def _run_self_probe_matrix(self, work_dir: Path) -> None:
        """Tatsaechliche Aufrufe (keine Direktpruefung der Auditfunktion,
        kein blosses export_status) gegen EIN rein SYNTHETISCHES, innerhalb
        dieser privaten Testfixture registriertes Sperrziel -- NIE eine
        echte Credentialdatei. Positivkontrolle: private erlaubte IO
        funktioniert unveraendert."""
        guard = EARLY_GUARD
        target = work_dir / "synthetic_blocked_target.txt"
        target.write_text("synthetic fixture content, not a real credential", encoding="utf-8")
        guard.register_self_probe_block(target)

        before_underlying = dict(guard._underlying_io_calls)

        guard.begin_self_probe()
        try:
            with self.assertRaises(_support_mod.IsolationViolation):
                with open(target, "w", encoding="utf-8") as fh:
                    fh.write("should never happen")
            with self.assertRaises(_support_mod.IsolationViolation):
                with open(target, "r", encoding="utf-8") as fh:
                    fh.read()
            with self.assertRaises(_support_mod.IsolationViolation):
                os.rename(target, work_dir / "renamed.txt")
            with self.assertRaises(_support_mod.IsolationViolation):
                os.stat(target)
            with self.assertRaises(_support_mod.IsolationViolation):
                os.lstat(target)
            with self.assertRaises(_support_mod.IsolationViolation):
                os.path.exists(target)
            with self.assertRaises(_support_mod.IsolationViolation):
                os.path.isfile(target)
            with self.assertRaises(_support_mod.IsolationViolation):
                target.stat()
            with self.assertRaises(_support_mod.IsolationViolation):
                target.exists()
            with self.assertRaises(_support_mod.IsolationViolation):
                target.is_file()
            # Direkter Aliasweg (rel./normpath-betrachtete Variante DESSELBEN
            # Ziels -- "./"-Segment, keine echte Home-Datei/kein ~-Alias).
            alias_path = str(work_dir) + os.sep + "." + os.sep + target.name
            with self.assertRaises(_support_mod.IsolationViolation):
                with open(alias_path, "r", encoding="utf-8") as fh:
                    fh.read()
            # N4-N3 Fix (01_GENERALREVIEW.md §3 "Die behauptete untere
            # IO-Falle ist weiterhin keine solche Falle"): die echte
            # oeffentliche `socket.connect`-API bleibt der Testaufruf (der
            # Guard-Audithook muss VOR der echten Implementierung
            # greifen), aber das Ziel ist jetzt ein SYNTHETISCHES Linux-
            # Abstract-Namespace-AF_UNIX-Ziel (fuehrendes NUL-Byte -- KEIN
            # Dateisystempfad, daher auch kein `sun_path`-Laengenlimit
            # unter einem tief verschachtelten privaten Tempverzeichnis)
            # statt einer echten externen (wenn auch nicht routbaren)
            # IPv4-Adresse. Selbst bei einem hypothetischen Guard-
            # Durchgriff verlaesst dabei NIE ein Byte die Maschine (rein
            # kernelinternes ECONNREFUSED, kein Dateisystem-, kein
            # Netzversuch) -- ein kurzes Timeout und die verwendete
            # Testadresse allein waren kein Ersatz fuer diese kontrollierte
            # untere Grenze.
            unix_target = b"\x00zr_lth_synthetic_unreachable_socket"
            probe_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                self._assert_guard_blocks("socket.connect", lambda: probe_sock.connect(unix_target))
            finally:
                probe_sock.close()
            # Subprozess: kontrollierte untere Falle DIREKT UNTER dem
            # echten `subprocess.Popen`-Aufruf. CPython ruft intern
            # `os.posix_spawn`/`os.fork` auf, um den Prozess tatsaechlich
            # zu erzeugen (abhaengig vom Pfad) -- NACH dem
            # `subprocess.Popen`-Audit-Event, aber VOR jedem echten
            # fork/exec. Beide werden fuer die Dauer dieses EINEN Aufrufs
            # auf eine wertfreie Falle umgelenkt, die NIEMALS einen echten
            # Prozess erzeugt. Greift der Guard korrekt, wird keine der
            # beiden Fallen je erreicht (die Ausnahme kommt bereits aus
            # dem Audit-Hook selbst, vor jedem Spawn-Versuch) -- nur ein
            # tatsaechlicher Guard-Durchgriff loest die Falle aus.
            real_posix_spawn = getattr(os, "posix_spawn", None)
            real_fork = getattr(os, "fork", None)

            def _spawn_trap(*_a, **_kw):
                raise AssertionError("GUARD_BREAKTHROUGH_TRAPPED_BEFORE_REAL_SPAWN")

            if real_posix_spawn is not None:
                os.posix_spawn = _spawn_trap
            if real_fork is not None:
                os.fork = _spawn_trap
            try:
                self._assert_guard_blocks(
                    "subprocess.Popen", lambda: subprocess.Popen([sys.executable, "-c", "pass"])
                )
            finally:
                if real_posix_spawn is not None:
                    os.posix_spawn = real_posix_spawn
                if real_fork is not None:
                    os.fork = real_fork
        finally:
            guard.end_self_probe()
            guard.clear_self_probe_blocks()

        after_underlying = dict(guard._underlying_io_calls)
        for op, before_count in before_underlying.items():
            self.assertEqual(
                after_underlying.get(op, 0), before_count,
                f"underlying_io_calls fuer {op} darf durch geblockte Selbstproben nicht steigen "
                "(der echte Metadatenaufruf darf bei Block nie ausgefuehrt worden sein).",
            )
        self.assertEqual(guard.export_status()["counters"]["unexpected_blocked"], 0)

        # Positivkontrolle: erlaubte private read/write/metadata-IO
        # funktioniert unveraendert (derselbe Arbeitsbereich, anderes Ziel).
        positive = work_dir / "allowed_positive.txt"
        positive.write_text("private allowed content", encoding="utf-8")
        self.assertTrue(positive.exists())
        self.assertTrue(positive.is_file())
        self.assertTrue(os.path.exists(positive))
        self.assertTrue(os.path.isfile(positive))
        self.assertIsNotNone(positive.stat())
        self.assertIsNotNone(os.stat(positive))
        self.assertEqual(positive.read_text(encoding="utf-8"), "private allowed content")

    def test_self_probe_matrix_blocks_all_synthetic_operations_and_allows_private_io(self):
        """N4-N2 (ersetzt das N4-01-Generalreview-Gegenbeispiel §2: ein
        blosses `fake_cred.exists() == False` ist KEIN Beleg -- der neue
        Guard muss `IsolationViolation` werfen, NICHT leise `False`
        liefern)."""
        work_dir = self._tmp_dir("selfprobe-primary")
        self._run_self_probe_matrix(work_dir)

    def test_self_probe_matrix_survives_temporary_home_and_io_mock_context(self):
        """02_N4N2_ARBEITSAUFTRAG.md C: dieselbe entscheidende Matrix NACH
        temporaeren Home-/expanduser-/IO-Mockkontexten erneut ausfuehren --
        `mock.patch` stellt beim Verlassen des `with`-Blocks IMMER die
        Fassung wieder her, die beim Patchbeginn aktuell war. Da unser
        Metadaten-Wrapper schon VOR diesem Test (beim Primaerinstall)
        gesetzt wurde, ist das die wiederhergestellte Fassung -- NICHT das
        unpatchte CPython-Original."""
        wrapped_exists_before_mock = Path.exists
        # N4-N3 Fix (01_GENERALREVIEW.md §5 "Fehlerhafte Bound-Method-
        # Identitaetsassertion"): `Path.home` ist ein `classmethod` --
        # JEDER Attributzugriff auf `Path.home` erzeugt ueber den
        # Deskriptorprotokoll-`__get__` ein NEUES Bound-Method-Objekt,
        # auch wenn die darunterliegende Funktion unveraendert dieselbe
        # ist. `assertIs(Path.home, <frueher gelesenes Path.home>)` kann
        # deshalb fehlschlagen, OBWOHL `mock.patch` korrekt wiederherstellt
        # -- das pruefbare, stabile Objekt ist `Path.home.__func__`
        # (die zugrunde liegende Funktion), nicht die Bound-Method-Huelle.
        wrapped_home_func_before_mock = Path.home.__func__

        fake_home = self._tmp_dir("selfprobe-fake-home")
        with mock.patch.object(Path, "home", return_value=fake_home), \
             mock.patch.object(Path, "exists", return_value=True):
            # Waehrend des Mocks ist Path.exists absichtlich NICHT unser
            # Wrapper -- das ist der Zweck dieses Zwischenschritts.
            self.assertTrue(Path("/irrelevant/for/this/probe").exists())

        self.assertIs(
            Path.exists, wrapped_exists_before_mock,
            "mock.patch muss unseren Guard-Wrapper wiederherstellen, nicht das CPython-Original.",
        )
        self.assertIs(
            Path.home.__func__, wrapped_home_func_before_mock,
            "mock.patch muss unsere gepatchte Path.home-Funktion wiederherstellen -- "
            "Vergleich auf Verhalten/__func__, NICHT auf eine instabile, bei jedem "
            "Attributzugriff neu erzeugte Bound-Method-Objektidentitaet.",
        )

        work_dir = self._tmp_dir("selfprobe-after-mock")
        self._run_self_probe_matrix(work_dir)

    # ─── N4-N2: Verbrauchslogik synthetisch (Replay/geaendertes argv/dritte
    # Berechtigung), OHNE dritten Interpreter, OHNE die 2 realen Erlaubnisse ──

    def test_child_grant_consumption_replay_and_third_grant_rejected_without_extra_process(self):
        probe_argv = [sys.executable, "-c", "pass", "--selfprobe-consumption-marker"]
        EARLY_GUARD.register_child(
            role="selfprobe-consumption", argv=probe_argv,
            fixture_paths=[], export_id="selfprobe-consumption-export", count=1,
        )
        EARLY_GUARD.begin_self_probe()
        try:
            EARLY_GUARD.authorize_and_consume(probe_argv)  # 1. echter Verbrauch -> OK, kein Prozess gestartet
            with self.assertRaises(_support_mod.IsolationViolation):
                EARLY_GUARD.authorize_and_consume(probe_argv)  # Replay nach Verbrauch
            changed_argv = probe_argv + ["--extra-flag"]
            with self.assertRaises(_support_mod.IsolationViolation):
                EARLY_GUARD.authorize_and_consume(changed_argv)  # geaendertes argv, nie registriert

            # N4-N3 Fix (01_GENERALREVIEW.md §5 "Kinderberechtigung
            # ueberschreibbar; env/cwd nicht verbindlich gebunden"): eine
            # erneute Registrierung DESSELBEN bereits verbrauchten argv
            # darf den Grant NICHT erneuern -- vorher wurde das
            # stillschweigend erlaubt (genau der gemeldete Fehler).
            with self.assertRaises(_support_mod.IsolationViolation):
                EARLY_GUARD.register_child(
                    role="selfprobe-consumption-renew", argv=probe_argv,
                    fixture_paths=[], export_id="selfprobe-consumption-export-renew", count=2,
                )

            # Ein NEUES, bisher unregistriertes argv kann weiterhin normal
            # mit count=2 registriert und zweifach verbraucht werden; eine
            # dritte Berechtigung bleibt abgelehnt (Anzahl erschoepft).
            second_probe_argv = [sys.executable, "-c", "pass", "--selfprobe-consumption-marker-2"]
            EARLY_GUARD.register_child(
                role="selfprobe-consumption-2", argv=second_probe_argv,
                fixture_paths=[], export_id="selfprobe-consumption-export-2", count=2,
            )
            EARLY_GUARD.authorize_and_consume(second_probe_argv)
            EARLY_GUARD.authorize_and_consume(second_probe_argv)
            with self.assertRaises(_support_mod.IsolationViolation):
                EARLY_GUARD.authorize_and_consume(second_probe_argv)  # dritte Berechtigung, Anzahl erschoepft

            # Eine abweichende Bindung (anderer export_id) fuer denselben,
            # noch NICHT verbrauchten argv-Schluessel wird ebenfalls
            # abgelehnt (`child_grant_decision`: "changed_binding").
            third_probe_argv = [sys.executable, "-c", "pass", "--selfprobe-consumption-marker-3"]
            EARLY_GUARD.register_child(
                role="selfprobe-consumption-3", argv=third_probe_argv,
                fixture_paths=[], export_id="selfprobe-consumption-export-3", count=1,
            )
            with self.assertRaises(_support_mod.IsolationViolation):
                EARLY_GUARD.register_child(
                    role="selfprobe-consumption-3", argv=third_probe_argv,
                    fixture_paths=[], export_id="selfprobe-consumption-export-3-changed", count=1,
                )
        finally:
            EARLY_GUARD.end_self_probe()
        self.assertEqual(EARLY_GUARD.export_status()["counters"]["unexpected_blocked"], 0)

    def test_child_grant_decision_pure_seam_matches_registration_behavior(self):
        """N4-N3 (MAIN-SEAM-SPEC.md geteilter Seam 4): dieselbe reine
        Funktion direkt gegen ein GETRENNTES synthetisches Lager pruefen
        -- ohne Beruehrung des echten Primaerlagers/EARLY_GUARD. Die
        "exakt zwei Rollen"-Obergrenze bindet NUR die kanonischen
        Primaerrollen (`child-writer`/`child-reader`) -- ein beliebiger
        synthetischer Rollenname (hier `synthetic-role`) unterliegt ihr
        bewusst NICHT, sonst wuerde die GETEILTE EARLY_GUARD-Instanz
        Selbstproben-Rollennamen quer ueber Testmethoden hinweg
        faelschlich gegen die echte child-writer/child-reader-Grenze
        anrechnen (N4-N3-Korrektur gegenueber einer frueheren, zu
        generischen Fassung dieser Pruefung)."""
        store: dict = {}
        argv = ["synthetic", "--probe"]
        decision, _reason = _support_mod.child_grant_decision(
            store, "synthetic-role", argv, [], None, None, None, None, None, "synthetic-export",
        )
        self.assertEqual(decision, "GRANT")
        store[tuple(argv)] = {
            "role": "synthetic-role", "fixture_paths": [], "export_id": "synthetic-export",
            "remaining": 1, "consumed": False,
            "binding": _support_mod._child_binding(
                "synthetic-role", argv, [], None, None, None, None, None, "synthetic-export",
            ),
        }
        same_decision, _ = _support_mod.child_grant_decision(
            store, "synthetic-role", argv, [], None, None, None, None, None, "synthetic-export",
        )
        self.assertEqual(same_decision, "GRANT", "identische Bindung bleibt idempotent GRANT.")
        changed_decision, changed_reason = _support_mod.child_grant_decision(
            store, "synthetic-role", argv, [], None, None, None, None, None, "a-different-export-id",
        )
        self.assertEqual(changed_decision, "REJECT")
        self.assertEqual(changed_reason, "changed_binding_for_existing_argv")
        store[tuple(argv)]["consumed"] = True
        consumed_decision, consumed_reason = _support_mod.child_grant_decision(
            store, "synthetic-role", argv, [], None, None, None, None, None, "synthetic-export",
        )
        self.assertEqual(consumed_decision, "REJECT")
        self.assertEqual(consumed_reason, "replay_of_consumed_grant_argv")

        # Primaerrollen-Obergrenze: eigenes, FRISCHES synthetisches Lager
        # mit den ECHTEN kanonischen Rollennamen.
        primary_store: dict = {}
        writer_decision, _ = _support_mod.child_grant_decision(
            primary_store, "child-writer", ["writer-argv"], [], None, None, None, None, None, "writer-export",
        )
        self.assertEqual(writer_decision, "GRANT")
        primary_store[("writer-argv",)] = {
            "role": "child-writer", "consumed": False,
            "binding": _support_mod._child_binding(
                "child-writer", ["writer-argv"], [], None, None, None, None, None, "writer-export",
            ),
        }
        reader_decision, _ = _support_mod.child_grant_decision(
            primary_store, "child-reader", ["reader-argv"], [], None, None, None, None, None, "reader-export",
        )
        self.assertEqual(reader_decision, "GRANT")
        primary_store[("reader-argv",)] = {
            "role": "child-reader", "consumed": False,
            "binding": _support_mod._child_binding(
                "child-reader", ["reader-argv"], [], None, None, None, None, None, "reader-export",
            ),
        }
        # Ein DRITTER, noch unregistrierter argv-Schluessel fuer eine
        # bereits lebende Primaerrolle (child-writer) wird abgelehnt --
        # das Primaerlager darf nie zwei gleichzeitig lebende Grants fuer
        # dieselbe Rolle haben.
        duplicate_decision, duplicate_reason = _support_mod.child_grant_decision(
            primary_store, "child-writer", ["writer-argv-second-attempt"], [], None, None, None, None, None,
            "writer-export-second",
        )
        self.assertEqual(duplicate_decision, "REJECT")
        self.assertEqual(duplicate_reason, "duplicate_live_grant_for_role")

    # ─── N4-N2: Bootstrap-/Export-Validator-Seam (kontrollierte Funktionen
    # im vorhandenen Profilprozess, kein dritter Prozess) ─────────────────

    def test_bootstrap_validator_seam_rejects_missing_or_invalid_context(self):
        with self.assertRaises(_support_mod.IsolationBootstrapError):
            _support_mod._validate_context(None)
        with self.assertRaises(_support_mod.IsolationBootstrapError):
            _support_mod._validate_context({})
        incomplete = {k: "x" for k in _support_mod._REQUIRED_CONTEXT_KEYS if k != "export_after_path"}
        with self.assertRaises(_support_mod.IsolationBootstrapError):
            _support_mod._validate_context(incomplete)
        empty_export = {k: "x" for k in _support_mod._REQUIRED_CONTEXT_KEYS}
        empty_export["export_after_path"] = ""
        with self.assertRaises(_support_mod.IsolationBootstrapError):
            _support_mod._validate_context(empty_export)

        # Dispatcher-Seam: OHNE Primaerguard (hier durch kurzzeitiges,
        # garantiert wiederhergestelltes Entfernen des Singleton-Attributs
        # simuliert) darf bootstrap_isolation NIE einen Platzhalter
        # installieren -- weder bei fehlendem `context=` noch bei einem
        # absichtlich unvollstaendigen `context=`.
        saved_guard = getattr(sys, _support_mod._GUARD_SINGLETON_ATTR, None)
        self.assertIsNotNone(saved_guard, "Vorbedingung: Primaerguard muss in diesem Prozess bereits installiert sein.")
        try:
            delattr(sys, _support_mod._GUARD_SINGLETON_ATTR)
            with self.assertRaises(_support_mod.IsolationBootstrapError):
                _support_mod.bootstrap_isolation(
                    private_home="x", private_root="x", real_home="x", repo_root="x",
                )
            with self.assertRaises(_support_mod.IsolationBootstrapError):
                _support_mod.bootstrap_isolation(context={"bundle_id": "x"})
            self.assertIsNone(
                getattr(sys, _support_mod._GUARD_SINGLETON_ATTR, None),
                "Ein fehlgeschlagener Bootstrapversuch darf KEINEN Platzhalterguard hinterlassen.",
            )
        finally:
            setattr(sys, _support_mod._GUARD_SINGLETON_ATTR, saved_guard)
        self.assertIs(getattr(sys, _support_mod._GUARD_SINGLETON_ATTR), EARLY_GUARD)

    def test_export_schema_validator_detects_missing_and_invalid_fields(self):
        export_path = self._tmp_env_path("export-schema-valid").with_suffix(".json")
        valid = EARLY_GUARD.export_phase("before", export_path, completion_status="running")
        self.assertEqual(_support_mod.validate_export_schema(valid), [])

        broken = dict(valid)
        broken.pop("unexpected_counts_by_operation")
        broken["phase"] = "sideways"
        missing = _support_mod.validate_export_schema(broken)
        self.assertIn("unexpected_counts_by_operation", missing)
        self.assertIn("phase_invalid", missing)
        self.assertEqual(_support_mod.validate_export_schema("not-a-dict"), ["not_a_dict"])

    def test_export_schema_validator_checks_values_not_only_key_presence(self):
        """N4-N3 (01_GENERALREVIEW.md §5 "Validator prueft Schluessel
        statt entscheidende Werte"): ein Feld, das PRAESENT aber vom
        falschen Typ/Wert ist, muss ebenso erkannt werden wie ein
        komplett FEHLENDES Feld -- reine Schluesselanwesenheit reicht
        nicht."""
        export_path = self._tmp_env_path("export-schema-values").with_suffix(".json")
        valid = EARLY_GUARD.export_phase("before", export_path, completion_status="running")
        self.assertEqual(_support_mod.validate_export_schema(valid), [])

        bad_pid = dict(valid)
        bad_pid["pid"] = -1
        self.assertIn("not_a_positive_int:pid", _support_mod.validate_export_schema(bad_pid))

        bad_hash = dict(valid)
        bad_hash["support_sha256"] = "not-a-real-hash"
        self.assertIn("invalid_or_empty_hash:support_sha256", _support_mod.validate_export_schema(bad_hash))

        bad_optional_hash = dict(valid)
        bad_optional_hash["runner_sha256"] = "too-short"
        self.assertIn("invalid_hash:runner_sha256", _support_mod.validate_export_schema(bad_optional_hash))
        # None bleibt fuer die Provenienzfelder gueltig (Main fuellt sie extern).
        none_optional_hash = dict(valid)
        none_optional_hash["runner_sha256"] = None
        self.assertEqual(_support_mod.validate_export_schema(none_optional_hash), [])

        bad_counts = dict(valid)
        bad_counts["unexpected_counts_by_operation"] = {"open": -1}
        self.assertIn(
            "not_a_nonnegative_count_dict:unexpected_counts_by_operation",
            _support_mod.validate_export_schema(bad_counts),
        )

        bad_status = dict(valid)
        bad_status["completion_status"] = "not-a-real-status"
        self.assertIn("invalid_completion_status", _support_mod.validate_export_schema(bad_status))

    def test_export_guard_state_one_arg_writes_own_snapshot_without_touching_phase_files(self):
        """01_GENERALREVIEW.md §5 "Eingefrorene Routing-API gebrochen":
        `export_guard_state(path)` bleibt EIN Argument (wie von den
        eingefrorenen routing/F1-Aufrufern erwartet), schreibt einen
        EIGENEN Snapshot und ueberschreibt KEINE offizielle before/after-
        Datei."""
        before_path = self._tmp_env_path("guard-state-before").with_suffix(".json")
        before = EARLY_GUARD.export_phase("before", before_path, completion_status="running")

        snapshot_path = self._tmp_env_path("guard-state-snapshot").with_suffix(".json")
        snapshot = EARLY_GUARD.export_guard_state(snapshot_path)
        self.assertEqual(snapshot["counters"]["unexpected_blocked"], 0)
        self.assertTrue(snapshot_path.is_file())
        self.assertNotIn(FAKE_TOKEN, snapshot_path.read_text(encoding="utf-8"))

        before_after_snapshot = json.loads(before_path.read_text(encoding="utf-8"))
        self.assertEqual(before_after_snapshot, before, "export_guard_state darf die before-Datei nie ueberschreiben.")

    def test_phase_value_validation_checks_plan_and_child_counts_not_just_schema(self):
        """N4-N3 (MAIN-SEAM-SPEC.md geteilter Seam 2): reine Funktion,
        kein Prozess -- synthetischer Plan/Phasensatz/Ereignisliste.

        N4-N3 Fix (01_GENERALREVIEW.md §3 "Ein neu hinzugefuegter Test ist
        logisch unerfuellbar"): die positive Aussage (keine Kinder erwartet,
        keine vorhanden -> leer) und die negative Aussage (Kinder erwartet,
        aber keine vorhanden -> Fehler) brauchen GETRENNTE `expected_plan`-
        Eingaben (`expects_children` False bzw. True) -- dieselben drei
        unveraenderten Eingaben (`expected_plan`, `phase_record`, `events`)
        koennen nicht gleichzeitig `[]` und einen Fehler liefern, ohne eine
        fachliche Assertion abzuschalten."""
        export_path = self._tmp_env_path("phase-value-validation").with_suffix(".json")
        phase_record = EARLY_GUARD.export_phase(
            "after", export_path, evidence={"test_or_fixture_id": "synthetic-test"},
            completion_status="completed",
        )
        # Positiv: dieser synthetische Prozess plant KEINE Kinder (wie die
        # 13 uebrigen aeusseren Tests und beide Kinder selbst) -- leer.
        # N4-N3 Fix (01_GENERALREVIEW.md §3 "... kommt hinzu, dass
        # forbidden_underlying_io_ops=('stat',) alle bereits aufsummierten
        # normalen Metadatenaufrufe desselben [prozessweiten Singleton-]
        # Guards als verboten behandelt"): `EARLY_GUARD` ist DERSELBE
        # Prozesssingleton, den ALLE anderen Testmethoden in dieser Datei
        # bereits benutzt haben -- sein `stat`-Zaehler ist zu diesem
        # Zeitpunkt praktisch immer schon > 0 durch ganz normale private
        # IO vorheriger Tests, unabhaengig von der Ausfuehrungsreihenfolge.
        # "stat" als Beispiel-Forbidden-Op markiert also keine synthetische
        # Negativbedingung, sondern realen Nebeneffektzustand. Ein
        # garantiert nie real auftretender Operationsname testet die reine
        # Pruefregel, ohne vom geteilten Guard-Zustand abzuhaengen.
        expected_plan = {
            "test_or_fixture_id": "synthetic-test",
            "forbidden_underlying_io_ops": ("synthetic_never_called_op",),
            "expects_children": False,
        }
        events = [{"pid": phase_record["pid"]}]
        self.assertEqual(_support_mod.phase_value_validation(expected_plan, phase_record, events), [])

        # Negativ (getrennter Datensatz, reine Funktion -- kein echter
        # Guard-Zustand): derselbe "forbidden_underlying_io_ops"-Name MUSS
        # erkannt werden, wenn der Phasensatz tatsaechlich einen nichtnull
        # Zaehler dafuer zeigt.
        forbidden_io_record = dict(phase_record)
        forbidden_io_record["underlying_io_calls_by_operation"] = dict(
            phase_record["underlying_io_calls_by_operation"], synthetic_never_called_op=3,
        )
        self.assertIn(
            "forbidden_underlying_io_nonzero:synthetic_never_called_op",
            _support_mod.phase_value_validation(expected_plan, forbidden_io_record, events),
        )

        mismatched_plan = dict(expected_plan)
        mismatched_plan["test_or_fixture_id"] = "a-different-test"
        self.assertIn(
            "mismatch:test_or_fixture_id",
            _support_mod.phase_value_validation(mismatched_plan, phase_record, events),
        )

        no_cross_match_events = [{"pid": phase_record["pid"] + 1}]
        self.assertIn(
            "pid_not_cross_matched_with_events",
            _support_mod.phase_value_validation(expected_plan, phase_record, no_cross_match_events),
        )

        # Negativ: GETRENNTER Plan, der Kinder verlangt (wie der
        # Profilparent) -- derselbe kinderlose `phase_record` muss dagegen
        # durchfallen, weil genau 1 Writer+1 Reader je Start/Verbrauch/Ende
        # fehlen.
        children_expected_plan = dict(expected_plan)
        children_expected_plan["expects_children"] = True
        problems = _support_mod.phase_value_validation(children_expected_plan, phase_record, events)
        self.assertIn("after_success_child_counts_not_exactly_one_writer_one_reader", problems)

        self.assertEqual(_support_mod.phase_value_validation("not-a-dict", phase_record, events), ["expected_plan_not_a_dict"])
        self.assertEqual(_support_mod.phase_value_validation(expected_plan, "not-a-dict", events), ["phase_record_not_a_dict"])

    def test_bootstrap_pre_dispatch_validation_and_recording_dispatcher_reject_invalid_contexts(self):
        """N4-N3 (MAIN-SEAM-SPEC.md geteilter Seam 3): DIESELBE Funktion,
        die `bootstrap_entry` vor jedem Dispatch laeuft -- hier mit
        privaten ungueltigen Eingaben + einem protokollierenden
        Dispatcher gefuettert, OHNE einen zusaetzlichen Prozess zu
        starten."""
        valid_root = self._tmp_dir("predispatch-root")
        valid_before = str(valid_root / "before.json")
        valid_after = str(valid_root / "after.json")
        valid_context = {
            "bundle_id": "predispatch-bundle", "process_id": "predispatch-proc", "role": "outer-test",
            "real_home_class": str(valid_root), "repo_root": str(_REPO_ROOT),
            "source_read_roots": [str(_SCRIPTS_DIR)], "dep_read_roots": [],
            "private_write_roots": [str(valid_root)], "shared_fixture_root": None,
            "export_before_path": valid_before, "export_after_path": valid_after,
            "credential_block_roots": [], "artifact_read_paths": [],
        }

        def _controlled_dispatch(context):
            problems = _support_mod.bootstrap_pre_dispatch_validation(context)
            dispatched = {"called": False}
            if not problems:
                dispatched["called"] = True
            return problems, dispatched

        problems, dispatched = _controlled_dispatch(valid_context)
        self.assertEqual(problems, [])
        self.assertTrue(dispatched["called"])

        missing_key = dict(valid_context)
        missing_key.pop("artifact_read_paths")
        problems, dispatched = _controlled_dispatch(missing_key)
        self.assertIn("artifact_read_paths", problems)
        self.assertFalse(dispatched["called"])

        relative_path = dict(valid_context)
        relative_path["repo_root"] = "relative/not/absolute"
        problems, dispatched = _controlled_dispatch(relative_path)
        self.assertIn("not_an_absolute_path:repo_root", problems)
        self.assertFalse(dispatched["called"])

        export_outside_own_root = dict(valid_context)
        export_outside_own_root["export_before_path"] = str(self._tmp_dir("predispatch-elsewhere") / "before.json")
        problems, dispatched = _controlled_dispatch(export_outside_own_root)
        self.assertIn("export_path_outside_own_private_root", problems)
        self.assertFalse(dispatched["called"])

        self.assertEqual(_support_mod.bootstrap_pre_dispatch_validation("not-a-dict"), ["context_not_a_dict"])

    # ─── N4-02: gemeinsamer Parser -- Konflikte, Roundtrip, fehlendes Modul ──

    def test_parse_env_text_identical_duplicate_is_not_a_conflict(self):
        values, conflicts = lmp.parse_env_text(
            f"{lmp.ENV_KEY_PROVIDER}=local\n{lmp.ENV_KEY_PROVIDER}=local\n"
        )
        self.assertEqual(values[lmp.ENV_KEY_PROVIDER], "local")
        self.assertNotIn(lmp.ENV_KEY_PROVIDER, conflicts)

    def test_conflicting_duplicate_provider_key_holds_no_last_wins(self):
        text = f"{lmp.ENV_KEY_PROVIDER}=cloud\n{lmp.ENV_KEY_PROVIDER}=local\n"
        values, conflicts = lmp.parse_env_text(text)
        self.assertIn(lmp.ENV_KEY_PROVIDER, conflicts)
        self.assertEqual(lmp.resolve_provider(values, conflicts), "hold")

        env_path = self._tmp_env_path("provider-conflict")
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(text, encoding="utf-8")
        provider, profile, _reason = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "hold")
        self.assertIsNone(profile)
        # Realer Launcherresolver (jetzt dieselbe Delegation) haelt identisch.
        provider2, profile2, _reason2 = launcher_mod.resolve_model_provider_choice(env_path)
        self.assertEqual(provider2, "hold")
        self.assertIsNone(profile2)

    def test_conflicting_duplicate_local_field_holds_no_last_wins(self):
        text = (
            f"{lmp.ENV_KEY_PROVIDER}=local\n"
            f"{lmp.ENV_KEY_BASE_URL}={FAKE_BASE_URL}\n"
            f"{lmp.ENV_KEY_BASE_URL}=http://127.0.0.1:9999/v1\n"
            f"{lmp.ENV_KEY_MODEL}={FAKE_MODEL}\n"
            f"{lmp.ENV_KEY_API_KEY}={FAKE_TOKEN}\n"
        )
        values, conflicts = lmp.parse_env_text(text)
        self.assertIn(lmp.ENV_KEY_BASE_URL, conflicts)
        with self.assertRaises(lmp.ProfileHold):
            lmp.resolve_local_profile(values, conflicts)

    def test_build_local_profile_updates_rejects_non_roundtripping_token_value_free(self):
        for bad_token in (" leading-space", "trailing-space ", '"quoted"', "'quoted'"):
            with self.assertRaises(lmp.ProfileHold) as ctx:
                lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=bad_token)
            self.assertNotIn(bad_token, str(ctx.exception), "Token selbst darf nie in der Meldung stehen.")
        # ein exakt roundtrippender Token bleibt weiterhin gueltig.
        updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        self.assertEqual(updates[lmp.ENV_KEY_API_KEY], FAKE_TOKEN)

    def test_missing_resolver_module_with_existing_profile_holds_not_legacy(self):
        env_path = self._tmp_env_path("missing-module-present")
        self.assertTrue(setup_mod._update_env_file_preserving(env_path, {lmp.ENV_KEY_PROVIDER: "local"}))
        with mock.patch.object(setup_mod, "local_model_profile", None):
            provider, profile, reason = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "hold", "fehlendes Resolvermodul bei vorhandenem Profil darf keine Cloudroute sein.")
        self.assertIsNone(profile)
        self.assertIsNotNone(reason)

        # Gegenprobe: der Schluessel fehlt in der Datei wirklich komplett
        # (nie geschrieben) -- das bleibt 'legacy', auch ohne Modul.
        env_path2 = self._tmp_env_path("missing-module-absent")
        with mock.patch.object(setup_mod, "local_model_profile", None):
            provider2, profile2, reason2 = setup_mod.resolve_model_provider(env_path2)
        self.assertEqual(provider2, "legacy")
        self.assertIsNone(profile2)
        self.assertIsNone(reason2)

    # ─── N4-03: geschuetzte Profiltransaktion -- Pending/Readback/Fehler ──

    def test_protected_publish_pending_marker_lifecycle_and_read_gate(self):
        env_path = self._tmp_env_path("pending-lifecycle")
        updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        marker = setup_mod._pending_marker_path(env_path)
        self.assertFalse(marker.exists())

        ok = setup_mod._update_env_file_preserving(env_path, updates)
        self.assertTrue(ok)
        self.assertFalse(marker.exists(), "Marker muss nach bestaetigtem Erfolg wieder entfernt sein.")
        provider, _profile, _r = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "local")

        # Marker SYNTHETISCH stehen lassen (simuliert einen abgebrochenen
        # vorherigen Versuch) -- normale Leser MUESSEN sichtbar halten.
        marker.touch()
        provider2, profile2, reason2 = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider2, "hold")
        self.assertIsNone(profile2)
        self.assertIsNotNone(reason2)
        provider3, profile3, _r3 = launcher_mod.resolve_model_provider_choice(env_path)
        self.assertEqual(provider3, "hold")
        self.assertIsNone(profile3)

        # Ein ausdruecklich neuer vollstaendiger Speicherversuch darf unter
        # bestehendem HOLD die Transaktion neu verifizieren und abschliessen.
        ok2 = setup_mod._update_env_file_preserving(env_path, updates)
        self.assertTrue(ok2)
        self.assertFalse(marker.exists())
        provider4, profile4, _r4 = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider4, "local")
        self.assertEqual(profile4.model, FAKE_MODEL)

    def test_protected_publish_unreadable_marker_also_holds(self):
        """'seine Abwesenheit nicht zuverlaessig pruefbar' ist GENAUSO ein
        Haltegrund wie 'Marker vorhanden' -- ein `stat()`-Fehler, der NICHT
        FileNotFoundError ist, darf nicht optimistisch als 'kein Marker'
        gelesen werden."""
        env_path = self._tmp_env_path("pending-unprobable")
        updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        self.assertTrue(setup_mod._update_env_file_preserving(env_path, updates))
        marker = setup_mod._pending_marker_path(env_path)

        real_stat = Path.stat

        def _unprobable(self_path, *a, **k):
            if self_path == marker:
                raise PermissionError("synthetic: Marker-Status nicht pruefbar")
            return real_stat(self_path, *a, **k)

        with mock.patch.object(Path, "stat", _unprobable):
            provider, profile, reason = setup_mod.resolve_model_provider(env_path)
        self.assertEqual(provider, "hold")
        self.assertIsNone(profile)
        self.assertIsNotNone(reason)

    def test_protected_publish_wrong_but_valid_readback_holds_no_false_success(self):
        """N4-03: ein 'falsches, aber gueltiges Profil' beim Pflicht-
        Readback darf NIE als Erfolg durchgehen -- 'irgendein gueltiges
        Profil' genuegt nicht, es muss die GEWAEHLTE Auswahl sein."""
        env_path = self._tmp_env_path("wrong-but-valid-readback")
        updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        marker = setup_mod._pending_marker_path(env_path)
        wrong_but_valid = dict(updates)
        wrong_but_valid[lmp.ENV_KEY_MODEL] = "a-different-but-otherwise-valid-model"
        with mock.patch.object(setup_mod, "_read_env_file", return_value=wrong_but_valid):
            ok = setup_mod._update_env_file_preserving(env_path, updates)
        self.assertFalse(ok, "Readback-Mismatch (falsches-aber-gueltiges Profil) darf nie Erfolg melden.")
        self.assertTrue(marker.exists(), "Pending muss bei Mismatch aktiv bleiben (HOLD).")

    def test_protected_publish_readback_io_error_holds_no_false_success(self):
        env_path = self._tmp_env_path("readback-ioerror")
        updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        marker = setup_mod._pending_marker_path(env_path)
        with mock.patch.object(setup_mod, "_read_env_file", side_effect=OSError("synthetic readback failure")):
            ok = setup_mod._update_env_file_preserving(env_path, updates)
        self.assertFalse(ok)
        self.assertTrue(marker.exists())

    def test_protected_publish_marker_removal_failure_holds_without_masking_primary_success(self):
        """Primaererfolg (Veroeffentlichung + Readback bestaetigt) wird
        durch einen Markerabbaufehler NICHT verdeckt/als Erfolg behauptet
        -- die Funktion bleibt bei `False`, die neuen Bytes stehen aber
        bereits korrekt auf der Platte."""
        env_path = self._tmp_env_path("marker-unlink-fail")
        updates = lmp.build_local_profile_updates(base_url=FAKE_BASE_URL, model=FAKE_MODEL, api_key=FAKE_TOKEN)
        marker = setup_mod._pending_marker_path(env_path)
        real_unlink = Path.unlink

        def _boom(self_path, *a, **k):
            if self_path == marker:
                raise OSError("synthetic marker-unlink failure")
            return real_unlink(self_path, *a, **k)

        with mock.patch.object(Path, "unlink", _boom):
            ok = setup_mod._update_env_file_preserving(env_path, updates)
        self.assertFalse(ok)
        self.assertTrue(marker.exists(), "Marker muss bei fehlgeschlagenem Abbau aktiv bleiben (HOLD).")
        reread = setup_mod._read_env_file(env_path)
        self.assertEqual(reread[lmp.ENV_KEY_MODEL], FAKE_MODEL, "Inhalt wurde trotzdem korrekt veroeffentlicht.")

    # ─── N4-04: echte Rekey-Bedienwege -- strenge 512/120-Limits + '-' ──

    def test_rekey_enter_preserves_strict_512_120_limits_and_dash_removes_owui_address(self):
        tmp_home = Path(tempfile.mkdtemp(prefix="o1-rekey-strict-limits-"))
        self._tmp_dirs.append(tmp_home)
        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch.object(launcher_mod, "_pause", return_value=None):
            prompts_1 = iter([
                "http://localhost:8080", "local", FAKE_BASE_URL, FAKE_MODEL,
                "http://127.0.0.1:19999",  # abweichende OWUI-Backendadresse setzen
            ])
            with mock.patch.object(launcher_mod, "_prompt", side_effect=lambda *_a, **_k: next(prompts_1)), \
                 mock.patch("getpass.getpass", side_effect=["owui-fake-key", FAKE_TOKEN]):
                launcher_mod.action_rekeys()

            env_path = tmp_home / ".openwebui_env"
            # Bewusst strengere 512/120-Limits vorbelegen (wie ein frueherer
            # bewusster Rekey sie gesetzt haette) -- `_rekeys_choose_local_
            # fields` fragt Limits selbst nicht ab, sondern erhaelt nur den
            # vorhandenen Wert.
            self.assertTrue(setup_mod._update_env_file_preserving(env_path, {
                lmp.ENV_KEY_GM_MAX_TOKENS: "512", lmp.ENV_KEY_PERSONA_MAX_TOKENS: "120",
            }))
            before = setup_mod._read_env_file(env_path)
            self.assertEqual(before[lmp.ENV_KEY_OWUI_BASE_URL], "http://127.0.0.1:19999")

            prompts_2 = iter(["", "", "", "", "-"])
            with mock.patch.object(launcher_mod, "_prompt", side_effect=lambda *_a, **_k: next(prompts_2)), \
                 mock.patch("getpass.getpass", side_effect=["", ""]):
                launcher_mod.action_rekeys()

            after = setup_mod._read_env_file(env_path)
            self.assertEqual(after[lmp.ENV_KEY_MODEL], FAKE_MODEL)
            self.assertEqual(after[lmp.ENV_KEY_API_KEY], FAKE_TOKEN)
            self.assertEqual(after[lmp.ENV_KEY_GM_MAX_TOKENS], "512", "strengere GM-Grenze muss Enter ueberleben.")
            self.assertEqual(
                after[lmp.ENV_KEY_PERSONA_MAX_TOKENS], "120", "strengere Persona-Grenze muss Enter ueberleben."
            )
            self.assertNotIn(
                lmp.ENV_KEY_OWUI_BASE_URL, after,
                "'-' muss die OWUI-Adresse tatsaechlich entfernen, kein alter Datei-/Envrest.",
            )

            provider, profile, _r = setup_mod.resolve_model_provider(env_path)
            self.assertEqual(provider, "local")
            self.assertEqual(profile.gm_max_tokens, 512)
            self.assertEqual(profile.persona_max_tokens, 120)
            self.assertIsNone(profile.owui_base_url)


if __name__ == "__main__":
    # Von der Prozessbruecke gestarteter frischer Kindinterpreter: echten
    # Koerper ausfuehren und Ergebnis als Marker auf STDOUT zuruueckgeben.
    # Standalone/run_all.py (ohne Kindmarke) laufen unveraendert nativ.
    if os.environ.get(_support_mod._UNITTEST_CHILD_ENV) == "1":
        raise SystemExit(_support_mod.run_module_as_child(sys.modules[__name__]))
    unittest.main()
