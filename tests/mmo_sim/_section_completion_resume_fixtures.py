#!/usr/bin/env python3
"""
tests/mmo_sim/_section_completion_resume_fixtures.py — gemeinsamer Testhelper
fuer die R12-AUTORECOVERY-Regressionstests (AR01-AR12,
01_AUFTRAG_AUTORECOVERY.md/CASES.json aus dem Closeout-Paket). Reiner
Testcode, keine Produktabhaengigkeit hierauf.

Baut denselben minimalen, aber ECHTEN Lauf wie `tests/mmo_sim/
test_m1_runtime_section.py` (ScriptedDriver, Fake-GM-Transport,
`write_test_profile`, `_full_v7_fixture.full_v7_save`) -- hier zusaetzlich
mit Helfern, um GENAU das engste Crash-/Pause-Fenster zwischen durabler
SL-Antwort und Markerbehandlung/Completion-Plan zu reproduzieren, sowohl
innerhalb desselben Prozesses (Admission-Pause) als auch ueber einen echten
zweiten Betriebssystemprozess (hartes Prozessende via `os._exit`
unmittelbar NACH `store.submit_to_sl`s Persist, VOR jeder weiteren
Python-Zeile)."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _full_v7_fixture import full_v7_save  # noqa: E402

COMPLETION_MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"

_DUMMY_SCHEMA = (
    '{"type":"object","required":["v","persona_key","rounds_played"],'
    '"properties":{"v":{"const":2}}}'
)


@dataclass
class Env:
    run_dir: Path
    states_dir: Path


def make_env(root: Path) -> Env:
    env = Env(run_dir=root / "run", states_dir=root / "states")
    env.states_dir.mkdir(parents=True)
    return env


def save_block(char_id: str, **overrides) -> dict:
    return full_v7_save(char_id, name="Testfigur", **overrides)


def debrief_with_marker(saves_by_char_id: dict[str, dict], prose: str = "Abschnitt beendet.") -> str:
    """Baut einen gueltigen SL-Debrief-Text mit genau den uebergebenen
    v7-Save-Bloecken PLUS Abschluss-Marker -- derselbe Fenced-Block-Aufbau,
    den `domain.zeitriss.saves.extract_all_saves` erwartet (s. test_m1)."""
    parts = [prose]
    for blk in saves_by_char_id.values():
        parts.append(f"```json\n{json.dumps(blk)}\n```")
    parts.append(COMPLETION_MARKER)
    return "\n".join(parts)


def seed_persona_state(ps_store, states_dir: Path, pk: str, char_id: str, rounds_played: int = 0) -> None:
    ps_store.save_state(pk, {
        "v": 2, "persona_key": pk, "rounds_played": rounds_played,
        "plays_char": {"character_id": char_id, "name": "Testfigur"},
    }, states_dir=states_dir)


def make_ps_store(schema_path: Path):
    from mmo_sim.core.persona_state import PersonaStateStore
    schema_path.write_text(_DUMMY_SCHEMA, encoding="utf-8")
    return PersonaStateStore(schema_path=schema_path, default_states_dir=None)


def harvest_extractor(debrief_text: str, cid_to_pk: dict[str, str]) -> dict[str, dict]:
    from mmo_sim.domain.zeitriss import saves as zeitriss_saves
    out: dict[str, dict] = {}
    for blk in zeitriss_saves.extract_all_saves(debrief_text):
        cid = zeitriss_saves.block_char_id(blk)
        pk = cid_to_pk.get(cid) if cid else None
        if pk is not None and zeitriss_saves.single_character_count(blk) == 1 and pk not in out:
            out[pk] = blk
    return out


class ScriptedDriver:
    """Identisch zu test_m1_runtime_section.ScriptedDriver -- hier dupliziert
    (kein Produktimport, reiner Testcode), damit dieses Fixture-Modul
    eigenstaendig bleibt."""

    def __init__(self, script):
        self._script = list(script)
        self.calls = 0

    def decide(self, context: dict):
        self.calls += 1
        if not self._script:
            raise RuntimeError("ScriptedDriver: Skript erschoepft")
        return self._script.pop(0)


class ExplodingDriver:
    """AR05-Helfer: ein Treiber, der NIEMALS haette gefragt werden duerfen
    (z.B. nach erfolgreichem Auto-Recovery). Jeder Aufruf ist ein
    Testversagen, kein stiller Fallback."""

    def __init__(self, label: str = "exploding"):
        self.label = label
        self.calls = 0

    def decide(self, context: dict):
        self.calls += 1
        raise AssertionError(
            f"{self.label}: keine neue Persona-Entscheidung erwartet -- "
            "Auto-Recovery haette die bereits durabel empfangene Antwort ernten muessen."
        )


class ReflectionOnlyDriver:
    """AR02/AR07-Helfer: antwortet NUR auf den bestehenden privaten
    Pflicht-Reflexionsturn (`core/runtime.py:_collect_reflections`s
    `system == 'PRIVATE_REFLECTION_SENTINEL'`-Kontext) -- jede ANDERE
    Entscheidungsanfrage (ein neuer Spiel-/GM-Turn) ist ein Testversagen:
    nach erfolgreichem Auto-Recovery darf GENAU NULL neue Spielzug-
    Entscheidung noetig sein, die Pflicht-KI-Reflexion bleibt aber
    weiterhin faellig (nicht uebersprungen/gefaelscht)."""

    def __init__(self, reflection_text: str, origin_source: str = "fake:reflect"):
        self._reflection_text = reflection_text
        self._origin_source = origin_source
        self.calls = 0

    def decide(self, context: dict):
        from mmo_sim.adapters.base import ParticipantDecision
        self.calls += 1
        if context.get("system") != "PRIVATE_REFLECTION_SENTINEL":
            raise AssertionError(
                "ReflectionOnlyDriver: unerwartete Nicht-Reflexions-Anfrage -- "
                f"Auto-Recovery haette keinen neuen Spielzug ausloesen duerfen (context={context!r})."
            )
        return ParticipantDecision(text=self._reflection_text, origin_source=self._origin_source)


class ScriptedGmTransport:
    """Fake-GM-Transport -- liefert der Reihe nach vorgegebene Inhalte."""

    def __init__(self, scripted_contents):
        self._contents = list(scripted_contents)
        self.calls: list[dict] = []

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls.append({"turn_idx": turn_idx, "user_text": user_text})
        content = self._contents.pop(0) if self._contents else ""
        return {"content": content, "usage": {}, "sources": [], "latency_s": 0.0, "chat_id": f"chat-{turn_idx}"}


class StopAfterResponseGmTransport(ScriptedGmTransport):
    """AR02-Helfer: liefert die Antwort GANZ NORMAL (der Rohbeleg wird von
    `store.submit_to_sl` unveraendert durabel persistiert), setzt aber
    DANACH -- noch VOR der Rueckkehr an den Aufrufer -- den bestehenden
    `lab.stop`-Flag (admission.py). Reproduziert AR02 ('Fake-Uhr
    ueberschreitet die Startfrist GENAU nach einer erfolgreichen Antwort')
    OHNE jeden Produktcode anzufassen -- der naechste `self._check_gate()`
    in `run_full_section` (F3, 'vor Publish/Reflexion') sieht den Stop und
    blockt, GENAU wie eine echte Betreiber-Stopanforderung."""

    def __init__(self, scripted_contents, run_dir: Path, reason: str):
        super().__init__(scripted_contents)
        self._run_dir = run_dir
        self._reason = reason

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        result = super().turn(turn_idx, user_text, **kwargs)
        if not self._contents:
            # NUR nach dem LETZTEN gescripteten Turn (der Markerantwort) --
            # fruehere Turns (Anker/Gast-Import) sollen ganz normal
            # durchlaufen, exakt wie im Normalfall.
            write_lab_stop(self._run_dir, self._reason)
        return result


class ExplodingGmTransport:
    """AR03/AR04-Helfer: ein GM-Transport, der NIE erreicht werden duerfen
    sollte (kein neuer GM-Turn nach erfolgreichem Auto-Recovery)."""

    def __init__(self):
        self.calls = 0

    def turn(self, turn_idx: int, user_text: str, **kwargs) -> dict:
        self.calls += 1
        raise AssertionError(
            "ExplodingGmTransport: kein neuer GM-Turn erwartet -- Auto-Recovery "
            "haette die bereits durabel empfangene Antwort ernten muessen."
        )


def write_lab_stop(run_dir: Path, reason: str) -> None:
    """Setzt den bestehenden `lab.stop`-Flag (admission.py, UNVERAENDERT,
    nur gelesen) -- `read_admission_block` blockt dann JEDE weitere
    Anfrage/jeden weiteren Gate-Check, exakt wie eine echte Betreiber-
    Stopanforderung oder eine ueberschrittene Startfrist."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "lab.stop").write_text(json.dumps({"reason": reason}), encoding="utf-8")


def clear_lab_stop(run_dir: Path) -> None:
    p = run_dir / "lab.stop"
    if p.exists():
        p.unlink()


def build_two_member_table(env: Env, table_id: str = "t-autorecovery"):
    """Baut Lobby+Tisch mit Leader+Gast, zwei neutralen Testfiguren,
    `ZeitrissHarvestValidator`/`ZeitrissTableSizePolicy` (echter Schema-/
    Validierungsweg, A08) -- gibt `(lobby, table, ps_store)` zurueck."""
    import mmo_sim.core.store as store
    from mmo_sim.domain.zeitriss.policy import ZeitrissTableSizePolicy

    schema_path = env.run_dir.parent / "schema.json"
    ps_store = make_ps_store(schema_path)
    seed_persona_state(ps_store, env.states_dir, "leader_pk", "chrono-leader")
    seed_persona_state(ps_store, env.states_dir, "guest_pk", "chrono-guest")

    lobby = store.Lobby(env.run_dir, table_size_policy=ZeitrissTableSizePolicy())
    lobby.join("leader_pk")
    lobby.join("guest_pk")
    table, derivation = store.create_table_from_offer_log(
        lobby, table_id,
        offer_log_events=[
            {"type": "offer", "id": "o1", "from": "leader_pk", "wants": ["guest_pk"]},
            {"type": "consent", "offer_id": "o1", "from": "guest_pk", "accept": True},
        ],
        chrononaut_ids={"leader_pk": "chrono-leader", "guest_pk": "chrono-guest"},
    )
    assert table is not None, f"Tisch haette entstehen muessen: {derivation}"
    return lobby, table, ps_store
