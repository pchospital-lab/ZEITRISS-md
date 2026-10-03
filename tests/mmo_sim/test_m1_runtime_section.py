#!/usr/bin/env python3
"""
tests/mmo_sim/test_m1_runtime_section.py — A01/A06/A09 auf `core/runtime.py`:
derselbe Runtime-/Store-/Eventcode treibt einen vollen Abschnitt mit ECHTEN
(hier: gescripteten Fake-)Teilnehmerentscheidungen statt P1-Fixturetexten —
Beweis fuer M1 "Fixture->echte Eingabe" (PLAN.md §3 Antwort 4).

Pure Python, nur `assert`, echter Exitcode."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mmo_sim.core.store as store  # noqa: E402
from mmo_sim.adapters.base import ParticipantDecision  # noqa: E402
from mmo_sim.core.admission import write_test_profile  # noqa: E402
from mmo_sim.core.controller import TableController  # noqa: E402
from mmo_sim.core.events import EventLog  # noqa: E402
from mmo_sim.core.persona_state import PersonaStateStore  # noqa: E402
from mmo_sim.core.runtime import SectionRuntime  # noqa: E402
from mmo_sim.domain.zeitriss.policy import ZeitrissHarvestValidator, ZeitrissTableSizePolicy  # noqa: E402
from mmo_sim.domain.zeitriss import saves as zeitriss_saves  # noqa: E402

COMPLETION_MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


class ScriptedDriver:
    """Geskripteter Fake-Teilnehmer (Mensch- ODER Persona-Ersatz) —
    implementiert exakt `ParticipantDriver`. Liefert der Reihe nach die
    vorgegebenen Texte/Save-Payloads, PROTOKOLLIERT aber, dass dies eine
    reale Entscheidungs-Anfrage war (kein Fixture-Lookup durch die Runtime
    selbst)."""

    def __init__(self, script: list[ParticipantDecision]):
        self._script = list(script)
        self.calls = 0

    def decide(self, context: dict) -> ParticipantDecision:
        self.calls += 1
        if not self._script:
            raise RuntimeError("ScriptedDriver: Skript erschoepft")
        return self._script.pop(0)


def _harvest_extractor(debrief_text: str, cid_to_pk: dict[str, str]) -> dict[str, dict]:
    """ZEITRISS-Domaenenimplementierung des HarvestExtractor-Protokolls
    (core/runtime.py kennt diese Funktion nicht, nur ihr Ergebnis)."""
    out: dict[str, dict] = {}
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
    return {"v": 7, "characters": [{"char_id": char_id, "name": "Test"}]}


def _seed_persona_state(ps_store: PersonaStateStore, states_dir: Path, pk: str, char_id: str) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": 0,
        "plays_char": {"character_id": char_id, "name": "Test"},
    }, states_dir=states_dir)


class _FakeGmTransport:
    """Fake-GM-Transport an der Runtime-Grenze (kein Netz) — protokolliert
    jeden Turn, liefert den Debrief-Turn mit echtem Marker."""

    def __init__(self, scripted_contents: list[str]):
        self._contents = list(scripted_contents)
        self.calls: list[dict] = []

    def turn(self, turn_idx: int, user_text: str) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        content = self._contents.pop(0) if self._contents else ""
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": "fake-chat"}


def test_full_section_with_real_decisions_completes_and_publishes():
    """P2-Fertigstellung (I1, alt->neu dokumentiert): nach erfolgreichem
    Abschluss sammelt `run_full_section` jetzt eine FREIWILLIGE private
    Reflexion je Mitglied (Plan §1 Punkt 6, Plan §4: keine optionale
    Reportauswertung, echter Teil von I1) -- deshalb bekommen beide
    ScriptedDriver-Skripte hier je einen zusaetzlichen Eintrag, und
    `leader_driver.calls`/`guest_driver.calls` steigen um je 1 (Anker+Debrief
    +Reflexion=3 fuer den Leader; Turn+Reflexion=2 fuer den Gast)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
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
            lobby, "t-runtime",
            offer_log_events=[{"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
                               {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True}],
            chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
        )
        assert table is not None, f"Tisch haette entstehen muessen: {derivation}"

        debrief_content = (
            "Abschnitt beendet.\n"
            f"```json\n{json.dumps(_save_block('chrono-leader'))}\n```\n"
            f"```json\n{json.dumps(_save_block('chrono-guest'))}\n```\n"
            f"{COMPLETION_MARKER}"
        )
        gm = _FakeGmTransport(scripted_contents=[
            "SL-Antwort auf Anker-Turn.",
            "SL-Antwort auf Gast-Turn.",
            debrief_content,
        ])
        leader_driver = ScriptedDriver([
            ParticipantDecision(text="Anker-Text vom echten Leader-Driver.", save_payload=_save_block("chrono-leader"), origin_source="fake:leader"),
            ParticipantDecision(text="Debrief-Anfrage vom Leader-Driver.", origin_source="fake:leader-debrief"),
            ParticipantDecision(text="Reflexion: bin zufrieden mit dem Abschnitt.", origin_source="fake:leader-reflect"),
        ])
        guest_driver = ScriptedDriver([
            ParticipantDecision(text="Gast-Text vom echten Guest-Driver.", save_payload=_save_block("chrono-guest"), origin_source="fake:guest"),
            ParticipantDecision(text="Reflexion: hat mir Spass gemacht.", origin_source="fake:guest-reflect"),
        ])
        controller = TableController(leader_key="leader_pk", drivers={"leader_pk": leader_driver, "guest_pk": guest_driver})
        event_log = EventLog(env.run_dir)
        # I2/A1 (MAIN-ENTSCHEIDUNG A1, fail-closed): explizites, sichtbares
        # Testprofil-Setup -- ohne Autorisierung blockiert das Admission-Gate
        # jetzt JEDE Entscheidung (auch menschliche/gescriptete Leader).
        write_test_profile(env.run_dir)

        runtime = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=_harvest_extractor, event_log=event_log,
        )
        outcome = runtime.run_full_section(
            controller, "section-runtime-01",
            contexts_by_persona={"leader_pk": {"user": "ctx-leader"}, "guest_pk": {"user": "ctx-guest"}},
            states_dir=env.states_dir, today="2026-09-22", ts="2026-09-22T15:30:00",
        )

        assert outcome.completion.success, outcome.completion.reason
        assert set(outcome.completion.members_completed) == {"leader_pk", "guest_pk"}
        assert leader_driver.calls == 3, "Leader wird fuer Anker, Debrief UND Reflexion real gefragt"
        assert guest_driver.calls == 2, "Gast wird fuer seinen Turn UND seine Reflexion real gefragt"
        assert len(gm.calls) == 3, "3 echte GM-Turns (Anker, Gast, Debrief) -- Reflexion geht NICHT an die SL"

        # Publikation ueber denselben Store lesbar (A01: kein Fixture-Sonderkern).
        published = store.load_current_save(env.run_dir, "leader_pk", ps_store, states_dir=env.states_dir)
        assert published == _save_block("chrono-leader")

        # Private Reflexion wurde lokal abgelegt, NICHT an die SL gesendet (Plan §1 Punkt 6).
        reflections_path = env.run_dir / "reflections.jsonl"
        assert reflections_path.exists(), "Reflexion nach erfolgreichem Abschluss haette geschrieben werden muessen"
        reflection_lines = [json.loads(l) for l in reflections_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert {r["persona_key"] for r in reflection_lines} == {"leader_pk", "guest_pk"}
        assert all("zufrieden" in r["text"] or "Spass" in r["text"] for r in reflection_lines)

        events = event_log.read_all()
        types = [e["event_type"] for e in events]
        assert "section_completed" in types
        assert types.count("sl_turn") == 3


def test_missing_marker_does_not_complete_and_no_publish():
    """P2-Fertigstellung (I1/A2, alt->neu dokumentiert, PLAN-CRITIC.md
    BLOCKER): `run_full_section` ist jetzt eine ECHTE Mehrfach-Turn-Schleife
    (nicht mehr Anker->EIN Debrief-Turn) -- nach jedem GM-Turn wird SOFORT
    der Marker geprueft, bei Fehlen laeuft die Szene weiter (bis Marker/
    Admission-Block/`max_turns`). Der `ScriptedDriver` wirft bei
    Skripterschoepfung bewusst `RuntimeError` (Test-Sentinel fuer "mehr
    Decision-Calls als das Fixture vorsieht"). Diese Testfixture uebergibt
    deshalb explizit `max_turns=2`, um GENAU die urspruenglich vorgesehenen
    zwei Turns (Anker + ein weiterer Spielturn ohne Marker) zu pruefen, ohne
    das Skript zu verlaengern -- die inhaltliche Kernaussage bleibt
    unveraendert: ohne Marker gibt es keinen Abschluss und keine
    Publikation."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        env = _make_env(root)
        schema_path = root / "schema.json"
        schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
        ps_store = PersonaStateStore(schema_path=schema_path, default_states_dir=None)
        _seed_persona_state(ps_store, env.states_dir, "solo_pk", "chrono-solo")

        lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
        lobby.join("solo_pk")
        table, _ = store.create_table_from_offer_log(
            lobby, "t-solo",
            offer_log_events=[{"type": "offer", "id": "o1", "from": "solo_pk", "wants": []}],
            chrononaut_ids={"solo_pk": "chrono-solo"},
        )
        gm = _FakeGmTransport(scripted_contents=["Normale SL-Antwort ohne jeden Marker."])
        driver = ScriptedDriver([
            ParticipantDecision(text="Anker.", save_payload=_save_block("chrono-solo")),
            ParticipantDecision(text="Debrief ohne Erfolg."),
        ])
        controller = TableController(leader_key="solo_pk", drivers={"solo_pk": driver})
        # I2/A1: explizites Testprofil-Setup -- ohne Autorisierung wuerde
        # das Admission-Gate bereits den ERSTEN Turn blockieren und damit
        # die eigentliche Testaussage (Mehrfach-Turn ohne Marker -> kein
        # Abschluss) verdecken statt sie zu pruefen.
        write_test_profile(env.run_dir)
        runtime = SectionRuntime(
            lobby=lobby, table=table, gm_transport=gm, marker=COMPLETION_MARKER,
            harvest_validator=ZeitrissHarvestValidator(), persona_state_store=ps_store,
            harvest_extractor=_harvest_extractor,
        )
        outcome = runtime.run_full_section(
            controller, "section-no-marker",
            contexts_by_persona={"solo_pk": {"user": "ctx"}},
            states_dir=env.states_dir, today="2026-09-22", ts="2026-09-22T15:30:00",
            max_turns=2,
        )
        assert not outcome.completion.success
        assert store.load_current_save(env.run_dir, "solo_pk", ps_store, states_dir=env.states_dir) is None


def main() -> int:
    tests = [test_full_section_with_real_decisions_completes_and_publishes, test_missing_marker_does_not_complete_and_no_publish]
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
