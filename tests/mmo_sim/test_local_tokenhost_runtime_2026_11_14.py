#!/usr/bin/env python3
"""tests/mmo_sim/test_local_tokenhost_runtime_2026_11_14.py — ZR-LOCAL-TOKENHOST-L1,
Offline-Abnahmen O4 (serielle normale Runde + bestehender Abschluss) und
O5 (ehrliche Abrechnung + weiterhin wirksame Grenzen). O6s gerichteter
Wechseltest liegt in `test_local_tokenhost_profile_2026_11_14.py`
(`test_cloud_to_local_to_cloud_switch_fresh_reread_each_time`).

Treibt eine echte normale Runde (Leader [human] + Persona-Gast + GM) ueber
die TATSAECHLICHEN Produktbausteine:
  - `mmo_sim.core.runtime.SectionRuntime` / `mmo_sim.core.controller.
    TableController` / `mmo_sim.core.store` / `mmo_sim.core.admission` /
    `mmo_sim.core.request_ledger` (alle UNVERAENDERT, read-only)
  - `mmo_sim.adapters.gm_owui.GmOwuiTransport` -> `agent_mp/sl_client.py`
    -> `owui_client.OWUIChat` (echter HTTP-Code, nur `urllib.request.
    urlopen` als Transportgrenze gefaked)
  - `mmo_sim.adapters.persona_api.PersonaApiDriver` (echter HTTP-Code,
    dieselbe Transportgrenze)

Kein echtes Netz/Docker/Modell. Fixtureadressen/Keys erkennbar unecht."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
import unittest.mock as mock
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
# Immer an Position 0 (nicht nur bei Abwesenheit) -- s. ausfuehrlicher
# Kommentar in `test_local_tokenhost_routing_2026_11_14.py`: ein vorher in
# derselben Discover-Session geladenes Testmodul kann `scripts/` bereits
# vor den Repo-Root geschoben haben.
sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# Dieselbe fruehe Offlinehuelle und Prozessbruecke wie die Routingtests.
# Im Discover-Elternprozess keine Produktimporte und kein globaler Guard.
_spec = importlib.util.spec_from_file_location(
    "runtime_local_tokenhost_support", _HERE / "_local_tokenhost_support_2026_11_14.py")
_support_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _support_mod
_spec.loader.exec_module(_support_mod)
_REAL_BODY = (__name__ == "__main__") or _support_mod.is_real_body_env()
if _REAL_BODY:
    import ssl
    if hasattr(ssl.SSLContext, "_FALLBACK_CERT_DIR"):
        os.environ.setdefault("SSL_CERT_DIR", ssl.SSLContext._FALLBACK_CERT_DIR)
    EARLY_GUARD = _support_mod.self_bootstrap_isolation()
    from _full_v7_fixture import full_v7_save  # noqa: E402

    import mmo_sim.core.store as store  # noqa: E402
    from mmo_sim.adapters import factories as factories_mod  # noqa: E402
    from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
    from mmo_sim.adapters.gm_owui import GmOwuiTransport  # noqa: E402
    from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver  # noqa: E402
    from mmo_sim.core.admission import write_test_profile  # noqa: E402
    from mmo_sim.core.controller import TableController  # noqa: E402
    from mmo_sim.core.events import EventLog  # noqa: E402
    from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
    from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
    from mmo_sim.core import request_ledger  # noqa: E402
    from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
    from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402
else:
    load_tests = _support_mod.make_delegating_load_tests(
        __file__, "local-tokenhost-runtime", min_domain_tests=10)

_SL_CLIENT_PY = _REPO_ROOT / "internal" / "qa" / "harness" / "agent_mp" / "sl_client.py"

COMPLETION_MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"
_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)

FAKE_OWUI_URL = "http://127.0.0.1:18080"
FAKE_OWUI_KEY = "owui-fake-key-not-secret"
FAKE_LOCAL_BASE = "http://127.0.0.1:18001/v1"
FAKE_LOCAL_MODEL = "nemotron-3-super"
FAKE_LOCAL_TOKEN = "test-local-token-not-secret"
FAKE_PRESET_ID = "zeitriss-sonnet"
FAKE_KB_ID = "9ad88aff-aaaa-bbbb-cccc-fakekbid0001"


def _harvest_extractor(debrief_text: str, cid_to_pk: dict) -> dict:
    out: dict = {}
    for blk in zeitriss_saves.extract_all_saves(debrief_text):
        cid = zeitriss_saves.block_char_id(blk)
        pk = cid_to_pk.get(cid) if cid else None
        if pk is not None and zeitriss_saves.single_character_count(blk) == 1 and pk not in out:
            out[pk] = blk
    return out


@dataclass
class Env:
    run_dir: Path
    states_dir: Path


def _make_env(root: Path) -> Env:
    env = Env(run_dir=root / "run", states_dir=root / "states")
    env.states_dir.mkdir(parents=True)
    return env


def _save_block(char_id: str) -> dict:
    return full_v7_save(char_id, name="Test")


def _seed_persona_state(ps_store, states_dir, pk, char_id):
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


class ScriptedDriver:
    """Wie `test_m1_runtime_section.py` -- geskripteter Fake-Teilnehmer,
    implementiert exakt `ParticipantDriver`."""

    def __init__(self, script, *, is_human_driver=False, is_dollar_billed=True):
        self._script = list(script)
        self.calls = 0
        self.is_human_driver = is_human_driver
        self.is_dollar_billed = is_dollar_billed

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        if not self._script:
            raise RuntimeError("ScriptedDriver: Skript erschoepft")
        return self._script.pop(0)


class _SerialTrackingUrlopen:
    """Routet `urllib.request.urlopen` nach Pfad-Endung auf getrennte
    GM-/Persona-Antwortwarteschlangen UND zeichnet enter/exit-Ereignisse
    MONOTON auf -- Beleg fuer `max(active_requests)=1` (02/04: echte
    Serialitaet, kein paralleler Versand)."""

    def __init__(self, gm_responses, persona_responses):
        self._gm = list(gm_responses)
        self._persona = list(persona_responses)
        self.events: list[tuple] = []  # (kind, role, seq)
        self._active = 0
        self._seq = 0

    def __call__(self, req, timeout=None, context=None):
        url = req.full_url
        role = "gm" if url.endswith("/api/chat/completions") else "persona"
        self._seq += 1
        seq = self._seq
        self._active += 1
        self.events.append(("enter", role, seq))
        # O4-C.C1-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md Tabelle C):
        # vorher dekrementierte bereits das `finally` HIER, direkt nach dem
        # Konstruieren der Response -- das misst nur, wie lange `__call__`
        # selbst braucht, NICHT die tatsaechliche Response-Lebensdauer
        # (read/close). `_FakeResponse.__exit__` (unten) haelt die
        # Aktivitaet jetzt bis zum echten Schluss des `with`-Blocks, exakt
        # wie ein echter `urllib`-Response-Kontextmanager es tun wuerde --
        # ein bestellter vollstaendiger open/read/close-Nachweis, nicht nur
        # ein urlopen-Aufrufnachweis.
        if self._active > 1:
            self._active -= 1
            self.events.append(("exit", role, seq))
            raise AssertionError(f"active_requests={self._active + 1} > 1 -- Parallelversand erkannt")
        queue = self._gm if role == "gm" else self._persona
        if not queue:
            self._active -= 1
            self.events.append(("exit", role, seq))
            raise AssertionError(f"_SerialTrackingUrlopen: keine weitere {role}-Antwort")
        status, payload = queue.pop(0)
        return _FakeResponse(status, json.dumps(payload).encode("utf-8"), release=lambda: self._release(role, seq))

    def _release(self, role, seq):
        self._active -= 1
        self.events.append(("exit", role, seq))

    def max_active(self) -> int:
        active = 0
        peak = 0
        for kind, _role, _seq in self.events:
            active += 1 if kind == "enter" else -1
            peak = max(peak, active)
        return peak

    def every_exit_before_next_enter(self) -> bool:
        """Bei striktem seriellem Betrieb folgt auf jedes 'enter' sofort
        das passende 'exit', bevor ein neues 'enter' folgt (kein
        ueberlappendes Paar)."""
        depth = 0
        for kind, _role, _seq in self.events:
            depth += 1 if kind == "enter" else -1
            if depth > 1:
                return False
        return True


class _FactoryAwareSerialTrackingUrlopen(_SerialTrackingUrlopen):
    """O4-A.A1-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md, Tabelle C):
    beantwortet zusaetzlich die EINMALIGEN Setup-Anfragen, die
    `default_gm_transport_factory`s lokaler Zweig beim Transportbau
    ausloest (Preset-Read, nichtgenerativer Verify, Connection-
    Eindeutigkeitscheck) -- diese sind KEINE GM-/Persona-Completion und
    duerfen die Serial-/Active-Zaehlung der Basisklasse nicht beruehren.
    Danach bleibt das Verhalten (GM-/Persona-Queues, Aktivitaetstracking)
    bytegleich zur Basisklasse."""

    def __init__(self, gm_responses, persona_responses, *, owui_url, preset_id, local_model, kb_id,
                 local_base_url, local_token):
        super().__init__(gm_responses, persona_responses)
        self._owui_url = owui_url
        self._preset_id = preset_id
        self._local_model = local_model
        self._kb_id = kb_id
        self._local_base_url = local_base_url
        self._local_token = local_token
        self.setup_calls: list[str] = []

    def __call__(self, req, timeout=None, context=None):
        import urllib.parse
        url = req.full_url
        model_url = f"{self._owui_url}/api/v1/models/model?id={urllib.parse.quote(self._preset_id, safe='')}"
        if url == model_url:
            self.setup_calls.append(url)
            body = {
                "id": self._preset_id, "base_model_id": self._local_model,
                "meta": {"knowledge": [{"id": self._kb_id}]},
            }
            return _FakeResponse(200, json.dumps(body).encode("utf-8"))
        if url == f"{self._owui_url}/openai/verify":
            self.setup_calls.append(url)
            return _FakeResponse(200, json.dumps({"data": [{"id": self._local_model}]}).encode("utf-8"))
        if req.get_method() == "GET" and url == f"{self._owui_url}/openai/config":
            self.setup_calls.append(url)
            cfg = {
                "ENABLE_OPENAI_API": True,
                "OPENAI_API_BASE_URLS": [self._local_base_url],
                "OPENAI_API_KEYS": [self._local_token],
                "OPENAI_API_CONFIGS": {
                    "0": {"enable": True, "model_ids": [self._local_model],
                          "auth_type": "bearer", "prefix_id": ""},
                },
            }
            return _FakeResponse(200, json.dumps(cfg).encode("utf-8"))
        return super().__call__(req, timeout=timeout, context=context)


class _FakeResponse:
    def __init__(self, status, body, release=None):
        self.status = status
        self._body = body
        # O4-C.C1-Fix: `release` (falls gesetzt) wird ERST in `__exit__`
        # aufgerufen -- nicht beim Konstruieren/Zurueckgeben der Response.
        # `read()` haelt die Aktivitaet weiterhin (ruft `release` nicht auf),
        # exakt wie ein echter Response-Kontextmanager.
        self._release = release

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def close(self):
        if self._release is not None:
            release, self._release = self._release, None
            release()

    def __exit__(self, *a):
        self.close()
        return False


def _gm_response(text: str, ptok=20, ctok=10):
    return (200, {"choices": [{"message": {"content": text}}],
                  "usage": {"prompt_tokens": ptok, "completion_tokens": ctok}})


def _persona_response(text: str, ptok=15, ctok=8):
    return (200, {"choices": [{"message": {"content": text}}],
                  "usage": {"prompt_tokens": ptok, "completion_tokens": ctok}})


def _ledger_records(run_dir: Path) -> list[dict]:
    requests_dir = run_dir / "requests"
    if not requests_dir.is_dir():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(requests_dir.glob("*.json"))]


class LocalTokenhostRuntimeTests(unittest.TestCase):
    def setUp(self):
        self._tmp_dirs: list[Path] = []
        self._env_backup = dict(os.environ)
        os.environ["OPENWEBUI_URL"] = FAKE_OWUI_URL
        os.environ["OPENWEBUI_API_KEY"] = FAKE_OWUI_KEY

    def tearDown(self):
        for d in self._tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        os.environ.clear()
        os.environ.update(self._env_backup)

    def _tmp_root(self, prefix: str) -> Path:
        d = Path(tempfile.mkdtemp(prefix=f"o4o5-{prefix}-"))
        self._tmp_dirs.append(d)
        return d

    def _build_round(self, root: Path, *, gm_dollar_billed: bool):
        env = _make_env(root)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
        ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
        _seed_persona_state(ps_store, env.states_dir, "leader_pk", "chrono-leader")
        _seed_persona_state(ps_store, env.states_dir, "guest_pk", "chrono-guest")

        lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("leader_pk")
        lobby.join("guest_pk")
        table, derivation = store.create_table_from_offer_log(
            lobby, "t-local",
            offer_log_events=[{"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
                               {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True}],
            chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
        )
        self.assertIsNotNone(table, derivation)

        gm = GmOwuiTransport(
            _SL_CLIENT_PY, env.run_dir, table_id="t-local",
            sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
            gm_output_limit_tokens=4096, is_dollar_billed=gm_dollar_billed,
        )
        # Lokales Profil bedient GM UND Persona gleich -- beide tragen
        # denselben Billingmarker wie der GM-Transport dieses Laufs.
        persona_config = PersonaApiConfig(
            base_url=FAKE_LOCAL_BASE, api_key=FAKE_LOCAL_TOKEN, model=FAKE_LOCAL_MODEL,
            max_tokens=400, is_dollar_billed=gm_dollar_billed,
        )
        guest_driver = PersonaApiDriver(persona_config, "guest_pk")

        debrief_content = (
            "Abschnitt beendet.\n"
            f"```json\n{json.dumps(_save_block('chrono-leader'))}\n```\n"
            f"```json\n{json.dumps(_save_block('chrono-guest'))}\n```\n"
            f"{COMPLETION_MARKER}"
        )
        leader_driver = ScriptedDriver([
            ParticipantDecision(text="Anker-Text vom Leader.", save_payload=_save_block("chrono-leader"), origin_source="fake:leader"),
            ParticipantDecision(text="Debrief-Anfrage vom Leader.", origin_source="fake:leader-debrief"),
            ParticipantDecision(text="Reflexion: zufrieden.", origin_source="fake:leader-reflect"),
        ], is_human_driver=True)

        controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})
        event_log = EventLog(env.run_dir)
        write_test_profile(env.run_dir, max_usd=0.0)

        runtime = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=_harvest_extractor, event_log=event_log,
        )
        return env, runtime, controller, ps_store, gm, guest_driver, leader_driver, debrief_content

    def test_serial_activity_lasts_through_read_and_idempotent_close(self):
        transport = _SerialTrackingUrlopen([_gm_response("synthetic")], [])
        import urllib.request
        response = transport(urllib.request.Request(FAKE_OWUI_URL + "/api/chat/completions"))
        with response:
            response.read()
            self.assertEqual(transport._active, 1)
            response.close()
            self.assertEqual(transport._active, 0)
            response.close()
        self.assertEqual(transport.events, [("enter", "gm", 1), ("exit", "gm", 1)])

    def test_local_round_max_usd_zero_completes_serial_unpriced(self):
        """O4+O5-Pflichtkombination: voller lokaler Ablauf (Leader[human] +
        Persona-Gast + GM + Reflexion/Abschluss) mit max_usd=0 -- muss bis
        zum bestehenden Abschluss gehen, seriell (max 1 aktiver Request),
        Billing local_unpriced/dollar_billed=False, Tokenusage erhalten."""
        root = self._tmp_root("local-complete")
        env, runtime, controller, ps_store, gm, guest_driver, leader_driver, debrief = self._build_round(
            root, gm_dollar_billed=False,
        )
        urlopen = _SerialTrackingUrlopen(
            gm_responses=[_gm_response("SL-Antwort auf Anker."), _gm_response("SL-Antwort auf Gast."), _gm_response(debrief)],
            persona_responses=[
                _persona_response("Gast-Text vom echten Persona-Driver."),
                _persona_response("Reflexion: hat Spass gemacht."),
            ],
        )
        with mock.patch("urllib.request.urlopen", urlopen):
            outcome = runtime.run_full_section(
                controller, "section-local",
                contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"system": "Du spielst eine Figur.", "user": "ctx-guest"}},
                states_dir=env.states_dir, today="2026-11-14", ts="2026-11-14T12:00:00",
            )
        self.assertTrue(outcome.completion.success, outcome.completion.reason)
        self.assertEqual(set(outcome.completion.members_completed), {"leader_pk", "guest_pk"})

        self.assertEqual(urlopen.max_active(), 1, "max(active_requests) muss 1 sein -- kein Parallelversand.")
        self.assertTrue(urlopen.every_exit_before_next_enter())

        records = _ledger_records(env.run_dir)
        self.assertTrue(records, "Ledger muss Requestdatensaetze enthalten.")
        gm_records = [r for r in records if r["role"] == "gm_turn"]
        persona_records = [r for r in records if r["role"] == "persona_decision"]
        self.assertTrue(gm_records, "mindestens ein gm_turn-Ledgereintrag erwartet.")
        self.assertTrue(persona_records, "mindestens ein persona_decision-Ledgereintrag erwartet.")
        for rec in gm_records + persona_records:
            # `reserved_usd` bleibt eine Vorab-SCHAETZUNG (fuer Audit) --
            # `dollar_billed=False` ist der massgebliche Marker, der
            # `booked_usd=0.0` in `request_ledger.begin` erzwingt (statt
            # `reserved_usd`); echte Tokenusage bleibt in `usage` erhalten.
            self.assertFalse(rec["dollar_billed"], rec)
            self.assertIn("prompt_tokens", rec["usage"])
            self.assertGreater(rec["usage"]["prompt_tokens"], 0)

        status_path = env.run_dir / "lab.status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        self.assertEqual(status["usd_spent"], 0.0, "lokale Requests buchen nie einen Dollarbetrag (booked_usd=0.0 bei dollar_billed=False).")

        jsonl_path = env.run_dir / "gm_sessions" / "t-local" / "sl_history.jsonl"
        gm_lines = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertTrue(all(not l["dollar_billed"] for l in gm_lines))
        # N1-04: lokal/unpriced ist ein unbekannter Preis (JSON-null), KEINE
        # gemessene Nullkostenrechnung -- vorher faelschlich `0.0`.
        self.assertTrue(all(l["cost_usd"] is None for l in gm_lines))
        self.assertTrue(any(l["prompt_tokens"] > 0 for l in gm_lines), "echte Tokenusage bleibt erhalten.")

    def test_local_round_ledger_trace_carries_role_route_model_billing_limits_secrets_redacted_before_durable_write(self):
        """R3: reale Reservierungs-ID am Wire binden; Originale ueber Cleanup retten."""
        root = self._tmp_root("ledger-trace")
        env, runtime, controller, ps_store, gm, guest_driver, leader_driver, debrief = self._build_round(
            root, gm_dollar_billed=False,
        )
        pending = {}
        reservation_ids = []
        real_begin = request_ledger.begin

        def traced_begin(*args, **kwargs):
            # Kein Ledgerdouble: erst den unveraenderten produktiven Write
            # ausfuehren, dann dessen tatsaechliche ID fuer den Wire beobachten.
            request_id = real_begin(*args, **kwargs)
            pending["id"] = request_id
            reservation_ids.append(request_id)
            return request_id

        case = self

        class TracingUrlopen(_SerialTrackingUrlopen):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.wire_calls = []

            def __call__(self, req, timeout=None, context=None):
                request_id = pending.pop("id")
                record = request_ledger.load_request(env.run_dir, request_id)
                case.assertEqual(record["state"], "sent")
                body = json.loads(req.data)
                response = super().__call__(req, timeout=timeout, context=context)
                reply = json.loads(response._body)
                self.wire_calls.append({
                    "request_id": request_id, "sequence": self._seq,
                    "url": req.full_url, "headers": dict(req.headers), "body": body,
                    "response": reply,
                })
                return response

        urlopen = TracingUrlopen(
            gm_responses=[
                _gm_response("SL-Anker-Antwort-101.", ptok=101, ctok=11),
                _gm_response("SL-Gast-Antwort-202.", ptok=202, ctok=22),
                _gm_response(debrief, ptok=303, ctok=33),
            ],
            persona_responses=[
                _persona_response("Gast-Entscheidung-404.", ptok=404, ctok=44),
                _persona_response("Gast-Reflexion-505.", ptok=505, ctok=55),
            ],
        )
        with mock.patch.object(request_ledger, "begin", side_effect=traced_begin), \
             mock.patch("urllib.request.urlopen", urlopen):
            outcome = runtime.run_full_section(
                controller, "section-ledger-trace",
                contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"system": "Du spielst eine Figur.", "user": "ctx-guest"}},
                states_dir=env.states_dir, today="2026-11-14", ts="2026-11-14T12:00:00",
            )
        self.assertTrue(outcome.completion.success, outcome.completion.reason)
        self.assertEqual(urlopen.max_active(), 1)
        self.assertEqual(urlopen._active, 0)
        self.assertTrue(urlopen.every_exit_before_next_enter())
        self.assertEqual(pending, {})
        self.assertEqual([c["request_id"] for c in urlopen.wire_calls], reservation_ids)
        self.assertEqual([c["sequence"] for c in urlopen.wire_calls], list(range(1, 6)))

        # Bewusst andere Dateireihenfolge: weder UUID-Sortierung noch zip
        # duerfen eine Nutzrequest-Zuordnung begruenden.
        records = list(reversed(_ledger_records(env.run_dir)))
        by_id = {r["id"]: r for r in records}
        self.assertEqual(len(records), 5)
        self.assertEqual(set(by_id), set(reservation_ids))

        def entry(call, rec):
            self.assertEqual(call["request_id"], rec["id"])
            is_gm = rec["role"] == "gm_turn"
            self.assertIn(rec["role"], ("gm_turn", "persona_decision", "reflection"))
            self.assertEqual(rec["route"], FAKE_OWUI_URL if is_gm else FAKE_LOCAL_BASE)
            self.assertEqual(call["url"], rec["route"] + ("/api/chat/completions" if is_gm else "/chat/completions"))
            self.assertEqual(call["body"]["model"], FAKE_PRESET_ID if is_gm else FAKE_LOCAL_MODEL)
            self.assertEqual(call["body"]["max_tokens"], 4096 if is_gm else 400)
            self.assertEqual(rec["output_limit_tokens"], call["body"]["max_tokens"])
            self.assertFalse(rec["dollar_billed"])
            for key in ("prompt_tokens", "completion_tokens"):
                self.assertEqual(rec["usage"][key], call["response"]["usage"][key])
            if is_gm:
                self.assertEqual(rec["result_text"], call["response"]["choices"][0]["message"]["content"])
            return dict(
                request_id=rec["id"], sequence=call["sequence"], role=rec["role"],
                route=rec["route"], endpoint=call["url"], model=call["body"]["model"],
                max_tokens=call["body"]["max_tokens"], dollar_billed=rec["dollar_billed"],
                usage=rec["usage"], wire=call,
            )

        trace = [entry(c, by_id[c["request_id"]]) for c in urlopen.wire_calls]
        self.assertEqual({e["role"] for e in trace}, {"gm_turn", "persona_decision", "reflection"})
        self.assertEqual(len({e["usage"]["prompt_tokens"] for e in trace}), 5)
        # Negative Kontrollen: gleiche Rolle/Anzahl reicht nicht; sowohl
        # fremde IDs als auch falsch zugeordnete Usage muessen auffallen.
        gm_calls = [c for c in urlopen.wire_calls if by_id[c["request_id"]]["role"] == "gm_turn"]
        first, other = (by_id[c["request_id"]] for c in gm_calls[:2])
        with self.assertRaises(AssertionError):
            entry(gm_calls[0], other)
        with self.assertRaises(AssertionError):
            entry(gm_calls[0], dict(first, usage=other["usage"]))

        def redacted(raw):
            return raw.replace(FAKE_OWUI_KEY.encode(), b"[REDACTED]").replace(
                FAKE_LOCAL_TOKEN.encode(), b"[REDACTED]")

        # Ausgabe liegt in der EXISTIERENDEN privaten Guardwurzel, aber
        # ausserhalb aller tearDown-Fixtures. Keine neue Schreibfreigabe.
        durable = Path(tempfile.mkdtemp(prefix="runtime-artifacts-", dir=EARLY_GUARD.private_write_roots[0]))
        exported = []
        for source in sorted(root.rglob("*")):
            if not source.is_file():
                continue
            raw = source.read_bytes()
            # Bereits produktiv geschriebene Ledgeroriginale sind secretfrei.
            if source.parent == env.run_dir / "requests":
                self.assertNotIn(FAKE_OWUI_KEY.encode(), raw)
                self.assertNotIn(FAKE_LOCAL_TOKEN.encode(), raw)
            clean = redacted(raw)
            relative = source.relative_to(root)
            target = durable / "originals" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(clean)  # Redaktion VOR dauerhaftem Schreiben.
            exported.append({
                "path": str(Path("originals") / relative),
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                "redacted_sha256": hashlib.sha256(clean).hexdigest(),
            })
        self.assertTrue(any("current_saves" in e["path"] for e in exported), "Saveoriginale muessen mitgeliefert sein")
        trace_path = durable / "raw_trace_export.json"
        trace_path.write_bytes(redacted(json.dumps(trace, indent=2, sort_keys=True).encode()))
        EARLY_GUARD.export_guard_state(durable / "guard.json")
        self.assertEqual(EARLY_GUARD.export_status()["counters"]["unexpected_blocked"], 0)
        (durable / "manifest.json").write_text(json.dumps(exported, indent=2, sort_keys=True), encoding="utf-8")

        # Cleanup wirklich ausfuehren: der Export muss anschliessend noch
        # unveraendert lesbar sein, nicht nur vor tearDown kurz existieren.
        shutil.rmtree(root)
        self.assertFalse(root.exists())
        self.assertEqual(len(json.loads(trace_path.read_text())), 5)
        for item in exported:
            self.assertEqual(hashlib.sha256((durable / item["path"]).read_bytes()).hexdigest(), item["redacted_sha256"])
        for path in durable.rglob("*"):
            if path.is_file():
                raw = path.read_bytes()
                self.assertNotIn(FAKE_OWUI_KEY.encode(), raw)
                self.assertNotIn(FAKE_LOCAL_TOKEN.encode(), raw)
        print("LTH_RUNTIME_ARTIFACTS:" + str(durable), flush=True)

    def test_cloud_counterpart_max_usd_zero_stops_before_gm_completion(self):
        """O5: Cloudgegenfall mit max_usd=0 stoppt an DERSELBEN GM-Stelle --
        kein Abschluss, keine echte GM-Completion."""
        root = self._tmp_root("cloud-stop")
        env, runtime, controller, ps_store, gm, guest_driver, leader_driver, debrief = self._build_round(
            root, gm_dollar_billed=True,
        )
        urlopen = _SerialTrackingUrlopen(
            gm_responses=[_gm_response("SL-Antwort auf Anker."), _gm_response("SL-Antwort auf Gast."), _gm_response(debrief)],
            persona_responses=[_persona_response("Gast-Text vom echten Persona-Driver.")],
        )
        with mock.patch("urllib.request.urlopen", urlopen):
            outcome = runtime.run_full_section(
                controller, "section-cloud",
                contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"system": "Du spielst eine Figur.", "user": "ctx-guest"}},
                states_dir=env.states_dir, today="2026-11-14", ts="2026-11-14T12:00:00",
            )
        self.assertFalse(outcome.completion.success, "Cloud mit max_usd=0 darf NICHT abschliessen.")
        gm_calls = [e for e in urlopen.events if e[1] == "gm" and e[0] == "enter"]
        self.assertEqual(len(gm_calls), 0, "kein einziger echter GM-HTTP-Call -- das Gate stoppt VOR dem Versand.")

    def test_stop_requested_blocks_local_round_despite_max_usd_zero(self):
        """O5-Gegenfall: Stopflag muss den lokalen (dollar_billed=False)
        Ablauf weiterhin zuverlaessig stoppen -- Q07/Dollar-Skip betrifft
        NUR die Budgetpruefung, nicht Stop/Turns/Zeit/Deadline."""
        root = self._tmp_root("local-stop")
        env, runtime, controller, ps_store, gm, guest_driver, leader_driver, debrief = self._build_round(
            root, gm_dollar_billed=False,
        )
        status_path = env.run_dir / "lab.status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["stop_requested"] = True
        status_path.write_text(json.dumps(status), encoding="utf-8")

        urlopen = _SerialTrackingUrlopen(
            gm_responses=[_gm_response("SL-Antwort auf Anker."), _gm_response("SL-Antwort auf Gast."), _gm_response(debrief)],
            persona_responses=[_persona_response("Gast-Text.")],
        )
        with mock.patch("urllib.request.urlopen", urlopen):
            outcome = runtime.run_full_section(
                controller, "section-stop",
                contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"system": "s", "user": "ctx-guest"}},
                states_dir=env.states_dir, today="2026-11-14", ts="2026-11-14T12:00:00",
            )
        self.assertFalse(outcome.completion.success, "Stop-Flag muss den lokalen Ablauf trotz max_usd=0 anhalten.")
        gm_calls = [e for e in urlopen.events if e[1] == "gm" and e[0] == "enter"]
        self.assertEqual(len(gm_calls), 0)

    def test_turncap_blocks_local_round_between_requests_despite_max_usd_zero(self):
        """O5-B.B3 (RELEASE-CASES.json): "Stop ... UND ZWISCHEN Requests,
        Turncap, Zeitlimit, Deadline trotz lokaler Dollarbefreiung;
        erlaubte Vorrunden-Calls separat von verbotenem Folgesend zaehlen."
        `max_turns` gated UNVERAENDERT fuer JEDE Rolle (admission.py:492-493,
        "gaten UNVERAENDERT fuer JEDE Rolle") -- `dollar_billed=False`
        (Q07/Dollar-Skip) befreit NUR vom `max_usd`-Check, NICHT von
        `max_turns`. `max_turns=1` erlaubt GENAU EINEN echten Request
        (Vorrunden-Call), der ZWEITE (Folgesend) wird ZWISCHEN den Requests
        blockiert -- der Ablauf darf trotzdem nicht abschliessen."""
        root = self._tmp_root("local-turncap")
        env, runtime, controller, ps_store, gm, guest_driver, leader_driver, debrief = self._build_round(
            root, gm_dollar_billed=False,
        )
        # Additiv zum bereits von _build_round gesetzten max_usd=0.0 --
        # write_test_profile ueberschreibt turns_used/usd_spent NICHT
        # (setdefault), nur max_turns wird neu gesetzt.
        write_test_profile(env.run_dir, max_turns=1)

        urlopen = _SerialTrackingUrlopen(
            gm_responses=[_gm_response("SL-Antwort auf Anker."), _gm_response("SL-Antwort auf Gast."), _gm_response(debrief)],
            persona_responses=[_persona_response("Gast-Text vom echten Persona-Driver."), _persona_response("Reflexion.")],
        )
        with mock.patch("urllib.request.urlopen", urlopen):
            outcome = runtime.run_full_section(
                controller, "section-turncap",
                contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"system": "s", "user": "ctx-guest"}},
                states_dir=env.states_dir, today="2026-11-14", ts="2026-11-14T12:00:00",
            )
        self.assertFalse(outcome.completion.success, "max_turns=1 muss den lokalen Ablauf trotz max_usd=0 anhalten.")
        real_calls = [e for e in urlopen.events if e[0] == "enter"]
        self.assertEqual(
            len(real_calls), 1,
            "GENAU EIN erlaubter Vorrunden-Call, der verbotene Folgesend muss VOR dem "
            "physischen Transport blockiert werden, nicht erst danach gezaehlt werden.",
        )
        status = json.loads((env.run_dir / "lab.status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["turns_used"], 1, "genau der eine erlaubte Request wurde angerechnet.")

    def test_wall_deadline_blocks_local_round_before_any_request_despite_max_usd_zero(self):
        """O5-B.B3-Nachzug: ein bereits abgelaufenes `wall_deadline` haelt
        den lokalen (dollar_billed=False) Ablauf GENAUSO an wie Stop/
        Turncap -- unabhaengig von max_usd=0."""
        root = self._tmp_root("local-deadline")
        env, runtime, controller, ps_store, gm, guest_driver, leader_driver, debrief = self._build_round(
            root, gm_dollar_billed=False,
        )
        status_path = env.run_dir / "lab.status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["wall_deadline"] = time.time() - 10.0
        status_path.write_text(json.dumps(status), encoding="utf-8")

        urlopen = _SerialTrackingUrlopen(
            gm_responses=[_gm_response("SL-Antwort auf Anker."), _gm_response("SL-Antwort auf Gast."), _gm_response(debrief)],
            persona_responses=[_persona_response("Gast-Text.")],
        )
        with mock.patch("urllib.request.urlopen", urlopen):
            outcome = runtime.run_full_section(
                controller, "section-deadline",
                contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"system": "s", "user": "ctx-guest"}},
                states_dir=env.states_dir, today="2026-11-14", ts="2026-11-14T12:00:00",
            )
        self.assertFalse(outcome.completion.success, "abgelaufenes wall_deadline muss trotz max_usd=0 anhalten.")
        real_calls = [e for e in urlopen.events if e[0] == "enter"]
        self.assertEqual(len(real_calls), 0, "ein bereits abgelaufenes Deadline-Fenster blockiert VOR jedem Request.")

    def test_resume_from_history_local_profile_does_not_inherit_cloud_cum_cost(self):
        """O5: New UND fortgesetzte SLSession (from_history) behandeln das
        Profil gleich -- eine Cloud-History darf nicht als lokale aktuelle
        Rechnung erscheinen."""
        run_dir = self._tmp_root("resume")
        urlopen_cloud = _SerialTrackingUrlopen(gm_responses=[_gm_response("Cloud-Antwort.", ptok=100, ctok=50)], persona_responses=[])
        with mock.patch("urllib.request.urlopen", urlopen_cloud):
            cloud_transport = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="resume-tisch",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID, is_dollar_billed=True,
            )
            cloud_transport.turn(1, "Erster Cloud-Turn.")
        cloud_summary = cloud_transport.usage_summary()
        self.assertTrue(cloud_summary["cum_cost_est_usd"] > 0.0, "Cloud-Kosten muessen vor dem Wechsel real > 0 sein.")

        urlopen_local = _SerialTrackingUrlopen(gm_responses=[_gm_response("Lokaler Resume-Turn.", ptok=30, ctok=15)], persona_responses=[])
        with mock.patch("urllib.request.urlopen", urlopen_local):
            local_resumed = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="resume-tisch",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID, is_dollar_billed=False,
            )
            local_summary_before_turn = local_resumed.usage_summary()
            # N1-04: lokal/unpriced ist ab Resume-Start ausdruecklich UNKNOWN
            # (`None`/JSON-null), NICHT `0.0` -- `0.0` wuerde eine echte
            # Nullkosten-Messung behaupten, die fuer einen ungepreisten
            # lokalen Tokenhost nicht existiert.
            self.assertIsNone(
                local_summary_before_turn["cum_cost_est_usd"],
                "Resume mit dollar_billed=False darf die alte Cloud-Dollarsumme NICHT als "
                "aktuelle lokale Messung uebernehmen (und auch keine erfundene 0.0-Rechnung).",
            )
            local_resumed.turn(2, "Zweiter Turn, jetzt lokal.")
        self.assertIsNone(local_resumed.usage_summary()["cum_cost_est_usd"])
        jsonl_path = run_dir / "gm_sessions" / "resume-tisch" / "sl_history.jsonl"
        lines = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertEqual(lines[0]["pricing"], "sonnet_usd")
        self.assertEqual(lines[1]["pricing"], "local_unpriced")
        self.assertIsNone(lines[1]["cost_usd"])
        self.assertEqual(lines[1]["completion_tokens"], 15, "echte Tokenusage des lokalen Turns bleibt erhalten.")

    def test_local_round_two_real_persona_constructions_max_usd_zero_completes(self):
        """O4-A.A1 (RELEASE-CASES.json): dieselbe normale lokale Runde wie
        oben, aber mit Leader(human) + ZWEI echten Persona-Konstruktionen
        (zwei eigene `PersonaApiDriver`-Instanzen, zwei eigene Gaeste) statt
        nur einer -- der Mensch zaehlt dabei NICHT als zweite Persona. Pass-
        1-Gap: der einzige existierende O4-A-Test hatte genau EINEN
        Gast/EINE Personakonstruktion."""
        root = self._tmp_root("local-two-persona")
        env = _make_env(root)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
        ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
        _seed_persona_state(ps_store, env.states_dir, "leader_pk", "chrono-leader-2p")
        _seed_persona_state(ps_store, env.states_dir, "guest_a_pk", "chrono-guest-a")
        _seed_persona_state(ps_store, env.states_dir, "guest_b_pk", "chrono-guest-b")

        lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("leader_pk")
        lobby.join("guest_a_pk")
        lobby.join("guest_b_pk")
        table, derivation = store.create_table_from_offer_log(
            lobby, "t-local-2p",
            offer_log_events=[
                {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_a_pk", "guest_b_pk"]},
                {"type": "consent", "offer_id": "o1", "from": "guest_a_pk", "accept": True},
                {"type": "consent", "offer_id": "o1", "from": "guest_b_pk", "accept": True},
            ],
            chrononaut_ids={
                "leader_pk": "chrono-leader-2p", "guest_a_pk": "chrono-guest-a", "guest_b_pk": "chrono-guest-b",
            },
        )
        self.assertIsNotNone(table, derivation)

        # O4-A.A1-Fix (evidence/INDEPENDENT-GENERAL-REVIEW.md, Tabelle C):
        # GM und Personas werden jetzt ueber die ECHTEN gemeinsamen Factories
        # (`mmo_sim.adapters.factories.default_gm_transport_factory`/
        # `default_persona_driver_factory`) aufgebaut -- vorher wurden
        # `GmOwuiTransport`/`PersonaApiDriver` hier direkt konstruiert,
        # getrennt von der separat belegten Factorykette (A2/O2-B/O2-C).
        # Dafuer braucht es ein echtes persistiertes lokales Profil
        # (`~/.openwebui_env`) UND die drei einmaligen Setup-Anfragen, die
        # der lokale GM-Zweig vor dem Transportbau stellt (Preset-Read,
        # Verify, Connection-Eindeutigkeit) -- `_FactoryAwareSerialTracking
        # Urlopen` beantwortet sie, ohne die Serial-/Active-Zaehlung zu
        # beruehren.
        tmp_home = Path(tempfile.mkdtemp(prefix="o4a-two-persona-home-"))
        self._tmp_dirs.append(tmp_home)
        scripts_dir = _REPO_ROOT / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        import local_model_profile as real_lmp  # noqa: E402
        import setup as real_setup  # noqa: E402
        env_path = tmp_home / ".openwebui_env"
        local_updates = dict(real_lmp.build_local_profile_updates(
            base_url=FAKE_LOCAL_BASE, model=FAKE_LOCAL_MODEL, api_key=FAKE_LOCAL_TOKEN,
        ))
        self.assertTrue(real_setup._update_env_file_preserving(env_path, local_updates))

        debrief_content = (
            "Abschnitt beendet.\n"
            f"```json\n{json.dumps(_save_block('chrono-leader-2p'))}\n```\n"
            f"```json\n{json.dumps(_save_block('chrono-guest-a'))}\n```\n"
            f"```json\n{json.dumps(_save_block('chrono-guest-b'))}\n```\n"
            f"{COMPLETION_MARKER}"
        )
        leader_driver = ScriptedDriver([
            ParticipantDecision(text="Anker-Text vom Leader.", save_payload=_save_block("chrono-leader-2p"), origin_source="fake:leader"),
            ParticipantDecision(text="Debrief-Anfrage vom Leader.", origin_source="fake:leader-debrief"),
            ParticipantDecision(text="Reflexion: zufrieden.", origin_source="fake:leader-reflect"),
        ], is_human_driver=True)

        event_log = EventLog(env.run_dir)
        write_test_profile(env.run_dir, max_usd=0.0)

        urlopen = _FactoryAwareSerialTrackingUrlopen(
            # Leader-Anker + Import je Gast (2x) + Debrief = 4 GM-Antworten.
            gm_responses=[
                _gm_response("SL-Antwort auf Anker."),
                _gm_response("SL-Antwort auf Gast A."),
                _gm_response("SL-Antwort auf Gast B."),
                _gm_response(debrief_content),
            ],
            # Import je Gast (2x) + Pflicht-Reflexion je Gast (2x) = 4
            # Persona-Antworten (jeder Gast reflektiert ueber seinen EIGENEN
            # Driver, nicht nur der Leader).
            persona_responses=[
                _persona_response("Gast-A-Text vom echten Persona-Driver."),
                _persona_response("Gast-B-Text vom echten Persona-Driver."),
                _persona_response("Gast-A-Reflexion: hat Spass gemacht."),
                _persona_response("Gast-B-Reflexion: hat Spass gemacht."),
            ],
            owui_url=FAKE_OWUI_URL, preset_id=FAKE_PRESET_ID, local_model=FAKE_LOCAL_MODEL,
            kb_id=FAKE_KB_ID, local_base_url=FAKE_LOCAL_BASE, local_token=FAKE_LOCAL_TOKEN,
        )
        with mock.patch.object(Path, "home", return_value=tmp_home), \
             mock.patch("urllib.request.urlopen", urlopen):
            gm_factory = factories_mod.default_gm_transport_factory(
                env.run_dir, _REPO_ROOT, sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID,
            )
            gm = gm_factory("t-local-2p")
            self.assertFalse(gm.is_dollar_billed, "echte lokale Route muss dollar_billed=False bestaetigen.")

            # ZWEI eigene, tatsaechlich konstruierte PersonaApiDriver-
            # Instanzen ueber dieselbe echte Factory -- dies ist die
            # "mindestens zwei Persona-Konstruktionen"-Teilbedingung.
            persona_factory = factories_mod.default_persona_driver_factory(env.run_dir)
            guest_a_driver = persona_factory("guest_a_pk")
            guest_b_driver = persona_factory("guest_b_pk")
            self.assertIsNot(guest_a_driver, guest_b_driver, "zwei eigenstaendige Konstruktionen, keine Wiederverwendung.")

            controller = TableController(
                leader_key="leader_pk",
                drivers={"leader_pk": leader_driver, "guest_a_pk": guest_a_driver, "guest_b_pk": guest_b_driver},
            )
            runtime = SectionRuntime(
                lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
                harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
                harvest_extractor=_harvest_extractor, event_log=event_log,
            )
            outcome = runtime.run_full_section(
                controller, "section-local-2p",
                contexts_by_persona={
                    "leader_pk": {"user": "ctx-leader"},
                    "guest_a_pk": {"system": "Du spielst Figur A.", "user": "ctx-guest-a"},
                    "guest_b_pk": {"system": "Du spielst Figur B.", "user": "ctx-guest-b"},
                },
                states_dir=env.states_dir, today="2026-11-14", ts="2026-11-14T12:00:00",
            )
        self.assertGreaterEqual(len(urlopen.setup_calls), 3, "die drei einmaligen GM-Setup-Anfragen muessen gelaufen sein.")
        self.assertTrue(outcome.completion.success, outcome.completion.reason)
        self.assertEqual(set(outcome.completion.members_completed), {"leader_pk", "guest_a_pk", "guest_b_pk"})
        self.assertEqual(urlopen.max_active(), 1, "auch mit zwei Personas bleibt der Versand seriell.")
        self.assertTrue(urlopen.every_exit_before_next_enter())
        self.assertGreater(guest_a_driver.request_count, 0, "Gast A muss real .decide() aufgerufen haben.")
        self.assertGreater(guest_b_driver.request_count, 0, "Gast B muss real .decide() aufgerufen haben.")

        records = _ledger_records(env.run_dir)
        persona_records = [r for r in records if r["role"] == "persona_decision"]
        self.assertGreaterEqual(
            len(persona_records), 2, "beide Persona-Konstruktionen muessen eigene Ledgereintraege erzeugen.",
        )
        for rec in persona_records:
            self.assertFalse(rec["dollar_billed"], rec)

    def test_cloud_resume_after_legacy_local_unpriced_numeric_zero_line_keeps_real_cloud_sum(self):
        """O5-D/G9-Fix (02_NACHARBEIT.md Gruppe E): eine AELTERE, VOR dem
        N1-04-Fix geschriebene lokale Zeile konnte `cum_cost_usd` noch als
        numerische `0.0` statt `null` tragen (`dollar_billed=False`). Ohne
        die zusaetzliche `dollar_billed`-Pruefung in `SLSession.from_history`
        wuerde eine SPAETERE echte Cloud-Summe durch diese alte lokale
        Nullzeile wieder geloescht -- genau das G9-Risiko (01_GENERALREVIEW.md)."""
        run_dir = self._tmp_root("g9-legacy-zero")
        effective_dir = run_dir / "gm_sessions" / "g9-tisch"
        effective_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = effective_dir / "sl_history.jsonl"
        jsonl_path.write_text(
            json.dumps({
                "turn": 1, "leader_post": "Cloud-Anfrage.", "sl_content": "Cloud-Antwort.",
                "prompt_tokens": 100, "completion_tokens": 50, "cost_usd": 5.0,
                "cum_cost_usd": 5.0, "dollar_billed": True, "pricing": "sonnet_usd",
                "rag_sources": [], "latency_s": 0.1, "chat_id": "g9-chat", "ts": "2026-11-01T00:00:00",
            }, ensure_ascii=False) + "\n"
            + json.dumps({
                # Legacy-Zeile VOR dem N1-04-Fix: lokal/unpriced, aber
                # `cum_cost_usd` noch als numerische 0.0 statt `null`.
                "turn": 2, "leader_post": "Lokale Anfrage.", "sl_content": "Lokale Antwort.",
                "prompt_tokens": 10, "completion_tokens": 5, "cost_usd": 0.0,
                "cum_cost_usd": 0.0, "dollar_billed": False, "pricing": "local_unpriced",
                "rag_sources": [], "latency_s": 0.1, "chat_id": "g9-chat", "ts": "2026-11-02T00:00:00",
            }, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        urlopen_cloud_resume = _SerialTrackingUrlopen(
            gm_responses=[_gm_response("Cloud-Resume-Antwort.", ptok=20, ctok=10)], persona_responses=[],
        )
        with mock.patch("urllib.request.urlopen", urlopen_cloud_resume):
            cloud_resumed = GmOwuiTransport(
                _SL_CLIENT_PY, run_dir, table_id="g9-tisch",
                sl_model=FAKE_PRESET_ID, kb_id=FAKE_KB_ID, is_dollar_billed=True,
            )
            summary_before_turn = cloud_resumed.usage_summary()
            self.assertEqual(
                summary_before_turn["cum_cost_est_usd"], 5.0,
                "Cloud-Resume darf die alte lokale 0.0-Zeile NICHT als aktuelle Summe uebernehmen "
                "-- die echte vorherige Cloudsumme (5.0) muss erhalten bleiben (G9).",
            )
            cloud_resumed.turn(3, "Dritter Turn, wieder Cloud.")
        self.assertGreater(cloud_resumed.usage_summary()["cum_cost_est_usd"], 5.0)


if __name__ == "__main__":
    raise SystemExit(_support_mod.run_module_as_child(sys.modules[__name__]))
