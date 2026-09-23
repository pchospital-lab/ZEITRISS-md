#!/usr/bin/env python3
"""
tests/mmo_sim/test_p2_offline_player_journey.py — Durchgehende Offline-
Spielerreise (INTEGRATIONSPLAN.md §3) UND systematische Fehlerfaelle, die
NICHT bereits durch review_p2_integration.py (14) oder die bestehenden
P1-/P2-Suiten abgedeckt sind:

- Headless (Lab) UND TUI durchlaufen denselben `core.app_service.
  run_play_session`-Pfad ueber MEHRERE Turns bis zu einem echten,
  erfolgreichen Abschluss (Save-Ernte, Reflexion, Rueckkehr in die Lobby),
  danach Export in eine Datei und ein "Neustart" (neue Session, gleicher
  Teilnehmer/gleicher run_dir).
- Ein waehrend eines laufenden Mehrfach-Turn-Abschnitts (nicht nur VOR dem
  ersten Request) gesetzter Lab-Stop blockiert die naechste Anfrage sofort
  (A1, ueber test_12 hinaus, der nur den Vor-Start-Fall prueft).
- Menschlicher Treiber faellt WAEHREND eines laufenden Turns durch EOF aus
  -> derselbe "sicher pausiert"-Pfad wie im Boot-Menue (A5), kein
  Weiterspielen mit Ersatzentscheidung.
- API-Adapter: echter Verbindungsfehler (geschlossener Port) -> `Provider
  UnavailableError`, kein stiller Fallback (Fehlerfall "Quota/Auth/Timeout").

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mmo_sim.adapters.base import ParticipantDecision, ProviderUnavailableError  # noqa: E402
from mmo_sim.adapters.persona_api import PersonaApiConfig, PersonaApiDriver  # noqa: E402
from mmo_sim.core import app_service, store  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.domain.zeitriss import onboarding, saves as zeitriss_saves  # noqa: E402
from mmo_sim.domain.zeitriss.policy import (  # noqa: E402
    COMPLETION_MARKER, ZeitrissHarvestValidator, ZeitrissTableSizePolicy,
)
from mmo_sim.lab.runner import LabBudget, LabRunner  # noqa: E402
from mmo_sim.ui.tui import TuiSession  # noqa: E402

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


def _save_block(char_id: str) -> dict:
    return {"v": 7, "characters": [{"char_id": char_id, "name": "Journey"}]}


class _MultiTurnGm:
    """Mehrere Nicht-Marker-Turns, dann ein Turn mit Marker + Save-Block."""

    def __init__(self, non_marker_turns: int, char_id: str):
        self._remaining = non_marker_turns
        self._char_id = char_id
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls += 1
        if self._remaining > 0:
            self._remaining -= 1
            return {"content": f"Szene laeuft weiter (Turn {self.calls}).", "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}
        content = f"Abschnitt beendet.\n```json\n{json.dumps(_save_block(self._char_id))}\n```\n{COMPLETION_MARKER}"
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake"}


class _ScriptedPersonaDriver:
    def __init__(self, texts):
        self._texts = list(texts)
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        text = self._texts.pop(0) if self._texts else "Ich warte ab."
        return ParticipantDecision(text=text, origin_source="fake:journey")


def test_headless_multi_turn_journey_completes_reflects_and_publishes():
    """Lab-Pfad: mehrere Spielturns OHNE Marker, dann ein Turn MIT Marker
    -> echter Abschluss, Reflexion lokal abgelegt, Save ueber den
    gemeinsamen Store lesbar (kein Fixture-Sonderkern)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
        states_dir = root / "states"
        states_dir.mkdir()
        run_dir = root / "run"
        ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
        ps_store.save_state("solo_pk", {
            "v": 2, "persona_key": "solo_pk", "rounds_played": 0,
            "plays_char": {"character_id": "chrono-journey"},
        }, states_dir=states_dir)

        lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("solo_pk")
        table, _ = store.create_table_from_offer_log(
            lobby, "t-journey", [{"type": "offer", "id": "o1", "from": "solo_pk", "wants": []}],
            {"solo_pk": "chrono-journey"},
        )
        assert table is not None

        gm = _MultiTurnGm(non_marker_turns=3, char_id="chrono-journey")
        driver = _ScriptedPersonaDriver(["Anker.", "Weiter.", "Noch mehr.", "Letzter Zug.", "War ok, danke."])
        controller = TableController("solo_pk", {"solo_pk": driver})

        lab = LabRunner(run_dir, LabBudget(max_turns=100, max_seconds=1000, max_usd=10.0))
        lab.start()
        outcome = lab.run_section(
            lobby, table, gm, controller, "journey-section",
            {"solo_pk": {"user": "Ich beginne."}}, states_dir, "2026-09-22", "T",
            COMPLETION_MARKER, ZeitrissHarvestValidator(), ps_store, zeitriss_saves.harvest_from_debrief,
        )
        lab.release()

        assert outcome.completion.success, outcome.completion.reason
        assert gm.calls == 4, "3 Nicht-Marker-Turns + 1 Marker-Turn"
        published = store.load_current_save(run_dir, "solo_pk", ps_store, states_dir=states_dir)
        assert published == _save_block("chrono-journey")
        # R08-Restintegrationsfix (WEGKARTE §7 A4): eine erfolgreiche
        # KI-Pflichtreflexion schreibt jetzt ZWEI Archivzeilen -- den
        # empfangenen Rohbeleg (`ai_reflection_received`, sofort nach dem
        # Modellaufruf, VOR dem Statewrite-Versuch) UND den committeten
        # Nachweis (`ai_required_reflection`, NACH erfolgreichem
        # Statewrite) -- statt vorher nur einer Zeile. received != published
        # bleibt dadurch strukturell nachvollziehbar (s. Test 08 in
        # review_p2r_restintegration.py).
        reflections = [
            json.loads(line)
            for line in (run_dir / "reflections.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(reflections) == 2
        assert {r["kind"] for r in reflections} == {"ai_reflection_received", "ai_required_reflection"}
        assert all("danke" in r["text"] for r in reflections)

        # "Neustart": frischer LabRunner fuer DASSELBE run_dir sieht den
        # tatsaechlich verbrauchten Status (I5) -- kein Reset.
        status = LabRunner(run_dir, LabBudget(max_turns=100, max_seconds=1000, max_usd=10.0))
        assert status._turns_used >= 4


def test_tui_journey_export_writes_file_and_restart_reuses_participant():
    """TUI-Pfad: Export schreibt jetzt zusaetzlich eine Datei (I3); ein
    zweiter `scripts.mmo_sim`-Lauf (ueber `_resolve_participant_id`) nutzt
    denselben Teilnehmer wieder (Test 07 direkt am Mechanismus, nicht nur
    ueber den externen Subprozess-Gegentest)."""
    with tempfile.TemporaryDirectory() as td:
        data_dir = Path(td)
        sys.path.insert(0, str(_REPO_ROOT / "scripts"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("mmo_sim_journey_entrypoint", _REPO_ROOT / "scripts" / "mmo_sim.py")
        entry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(entry)

        pid1 = entry._resolve_participant_id(data_dir, None)
        pid2 = entry._resolve_participant_id(data_dir, None)
        assert pid1 == pid2, "wiederholter Aufruf ohne --participant muss denselben Teilnehmer liefern"

        onboarding_dir = data_dir / "onboarding"
        onboarding.start_or_resume(onboarding_dir, pid1)
        onboarding.complete_with_save(
            onboarding_dir, pid1, _save_block("chrono-export"), ZeitrissHarvestValidator(), "chrono-export",
        )
        printed = []
        session = TuiSession(onboarding_dir, data_dir / "catalog", pid1, print_fn=printed.append,
                              exports_dir=data_dir / "exports")
        session._cmd_export()
        export_path = data_dir / "exports" / f"{pid1}.json"
        assert export_path.is_file(), "Export haette eine Datei schreiben muessen (I3)"
        assert json.loads(export_path.read_text(encoding="utf-8"))["characters"][0]["char_id"] == "chrono-export"


def test_lab_stop_during_running_section_blocks_next_request_not_just_before_start():
    """alt->neu (WEGKARTE §6 F3/A1, PLAN-CRITIC-DURCHSTICH.md bestaetigter
    Punkt): urspruenglich erwartete dieser Test `gm.calls == 2` -- ein Stop,
    der WAEHREND der zweiten Persona-Entscheidung gesetzt wird, blockierte
    demnach NICHT mehr den zu dieser Entscheidung gehoerenden GM-Request,
    sondern erst den DARAUFFOLGENDEN. Das widersprach dem P2F-Vertrag
    (review_p2f_paths.py Test 05: 'Zwischen Persona-Request und GM-Request
    fehlt neuer Gatecheck' -- ein Stop WAEHREND der Entscheidung MUSS den
    zugehoerigen GM-Request verhindern) direkt am selben Mechanismus. F3
    verlangt jetzt ein Gate-Check ZWISCHEN jedem Persona-Request und dem
    zugehoerigen GM-Request (`core/runtime.py:act()`) -- diese Fixture ist
    bewusst umgeschrieben (semantisch notwendige Testanpassung, 04 §3):
    `gm.calls` bleibt bei 1 (nur der Anker-Turn, VOR dem Stop), der zweite
    Decision-Call findet weiterhin statt (der Stop wird ja erst WAEHREND
    dieser Entscheidung gesetzt), aber sein GM-Request wird jetzt verhindert
    -- 'die naechste Anfrage' ist ab sofort exakt DIE, die unmittelbar auf
    den Stop folgt, nicht erst die uebernaechste."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
        states_dir = root / "states"
        states_dir.mkdir()
        run_dir = root / "run"
        ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
        ps_store.save_state("solo_pk", {
            "v": 2, "persona_key": "solo_pk", "rounds_played": 0,
            "plays_char": {"character_id": "chrono-stop"},
        }, states_dir=states_dir)
        lobby = store.Lobby(run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("solo_pk")
        table, _ = store.create_table_from_offer_log(
            lobby, "t-stop", [{"type": "offer", "id": "o1", "from": "solo_pk", "wants": []}],
            {"solo_pk": "chrono-stop"},
        )
        assert table is not None
        gm = _MultiTurnGm(non_marker_turns=10, char_id="chrono-stop")

        lab_a = LabRunner(run_dir, LabBudget(max_turns=100, max_seconds=1000, max_usd=10.0))
        lab_a.start()

        class _OperatorStopsAfterFirstTurn:
            def __init__(self):
                self.calls = 0

            def decide(self, context: dict) -> ParticipantDecision:
                self.calls += 1
                if self.calls == 2:
                    # Simuliert einen SEPARATEN Operator-Prozess, der waehrend
                    # des laufenden Abschnitts stoppt (persistiert, A1).
                    lab_b = LabRunner(run_dir, LabBudget(max_turns=100, max_seconds=1000, max_usd=10.0))
                    lab_b.stop("Operator-Stop waehrend laufendem Abschnitt")
                return ParticipantDecision(text=f"Zug {self.calls}.", origin_source="fake:journey")

        driver = _OperatorStopsAfterFirstTurn()
        controller = TableController("solo_pk", {"solo_pk": driver})
        outcome = app_service.run_play_session(
            lobby, table, gm, controller, "stop-mid-section",
            {"solo_pk": {"user": "Start."}}, states_dir, "2026-09-22", "T",
            COMPLETION_MARKER, ZeitrissHarvestValidator(), ps_store, zeitriss_saves.harvest_from_debrief,
        )
        lab_a.release()

        assert not outcome.completion.success
        assert "Admission-Gate" in outcome.completion.reason
        assert driver.calls == 2, "kein dritter Decision-Call NACH dem Stop"
        assert gm.calls == 1, "kein GM-Turn mehr, sobald der Stop (auch waehrend der Entscheidung) gesetzt ist (F3, alt->neu)"


def test_human_driver_eof_mid_turn_pauses_safely_via_full_tui_run():
    """A5: EOF eines menschlichen Treibers WAEHREND eines laufenden Turns
    (nicht nur im Boot-Menue) nutzt denselben 'sicher pausiert'-Pfad --
    ueber `TuiSession.run()` (nicht nur direkten Methodenaufruf), damit der
    reale Propagationsweg EndOfInput -> run()-Handler geprueft ist."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
        states_dir = root / "states"
        states_dir.mkdir()
        run_dir = root / "run"
        onboarding_dir = root / "onboarding"
        catalog_dir = root / "catalog"
        onboarding.start_or_resume(onboarding_dir, "p_eof")
        onboarding.complete_with_save(
            onboarding_dir, "p_eof", _save_block("chrono-eof"), ZeitrissHarvestValidator(), "chrono-eof",
        )

        class _NeverRespondingGm:
            calls = 0

            def turn(self, turn_idx, user_text):
                self.calls += 1
                raise AssertionError("GM haette bei EOF VOR dem Request nie aufgerufen werden duerfen")

        printed = []
        scripted = iter(["l"])  # nur die Menuewahl -- danach EOF WAEHREND des Turns

        def _input_fn(prompt=""):
            try:
                return next(scripted)
            except StopIteration:
                raise EOFError()

        session = TuiSession(
            onboarding_dir, catalog_dir, "p_eof", input_fn=_input_fn, print_fn=printed.append,
            run_dir=run_dir, states_dir=states_dir, schema_path=schema_path,
            gm_transport_factory=lambda: _NeverRespondingGm(),
        )
        rc = session.run()
        assert rc == 0
        assert any("sicher pausiert" in p for p in printed), "EOF waehrend des Turns haette denselben Pause-Pfad wie im Boot-Menue nutzen muessen"


def test_persona_api_connection_refused_maps_to_provider_unavailable():
    """Fehlerfall 'Quota/Auth/Timeout': ein ECHTER Verbindungsfehler
    (geschlossener Loopback-Port, kein Mock der Adapterfunktion) wird auf
    `ProviderUnavailableError` abgebildet -- kein stiller Fallback, kein
    unbehandelter `URLError`."""
    driver = PersonaApiDriver(PersonaApiConfig(base_url="http://127.0.0.1:1", api_key="k", model="m", timeout=2), "p1")
    try:
        driver.decide({"system": "s", "user": "u"})
        assert False, "haette ProviderUnavailableError werfen muessen (Verbindung verweigert)"
    except ProviderUnavailableError:
        pass


def main() -> int:
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
