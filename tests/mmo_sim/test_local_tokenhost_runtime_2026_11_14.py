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

from _full_v7_fixture import full_v7_save  # noqa: E402

import mmo_sim.core.store as store  # noqa: E402
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
        self._active += 1
        self.events.append(("enter", role, self._seq))
        try:
            if self._active > 1:
                raise AssertionError(f"active_requests={self._active} > 1 -- Parallelversand erkannt")
            queue = self._gm if role == "gm" else self._persona
            if not queue:
                raise AssertionError(f"_SerialTrackingUrlopen: keine weitere {role}-Antwort")
            status, payload = queue.pop(0)
            return _FakeResponse(status, json.dumps(payload).encode("utf-8"))
        finally:
            self._active -= 1
            self.events.append(("exit", role, self._seq))

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


class _FakeResponse:
    def __init__(self, status, body):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
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


if __name__ == "__main__":
    unittest.main()
