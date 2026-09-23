#!/usr/bin/env python3
"""
mmo_sim/core/persona_state.py — generische Persona-State v2 Engine.

Extrahiert aus `internal/qa/harness/persona_state.py` (P1). Reine
Funktionsbibliothek, keine SL-/Netz-Calls. Implementiert dieselbe v2-Mechanik
(Anti-Stacking-Gate ueber rounds_played, Keyed-Append fuer round_history,
Cap+Prune, relationships-Merge, goals-Cap) 1:1 — inhaltlich unveraendert
uebernommen.

Auflage A2/A6 (PLAN-CRITIC.md): der Schema-Pfad ist HIER kein `__file__`-
relativer Default mehr, sondern ein PFLICHT-Konstruktorparameter von
`PersonaStateStore`. Ein neutraler Kern darf kein ZEITRISS-Schema hart
verdrahten — die Domaene (`domain/zeitriss/policy.py` bzw. die QA-Fassade)
uebergibt den tatsaechlichen Schema-Pfad explizit.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

ROUND_HISTORY_CAP = 6
LEARNINGS_CAP = 10
GOALS_CAP = 8


def render_for_prompt(state: dict) -> str:
    """Kompakter Text-Block zum Injizieren in den Persona-Turn-Prompt.

    Domaenenneutral: liest nur generische State-Felder (real_name, plays_char,
    rounds_played, learnings, relationships, goals, tactics_notes,
    round_history, summary) — keine ZEITRISS-Regelentscheidung."""
    lines = []
    lines.append(
        f"[BISHERIGER STAND — {state.get('real_name', '?')} spielt "
        f"{state.get('plays_char', {}).get('name', '?')} "
        f"\"{state.get('plays_char', {}).get('callsign', '?')}\", "
        f"{state.get('rounds_played', 0)} Runde(n) gespielt]"
    )

    learnings = state.get("learnings") or []
    if learnings:
        lines.append("Bisherige Erkenntnisse:")
        lines.extend(f"- {x}" for x in learnings)
    learnings_summary = (state.get("summary") or {}).get("learnings_summary") or ""
    if learnings_summary:
        lines.append(f"Aeltere Erkenntnisse (verdichtet): {learnings_summary}")

    relationships = state.get("relationships") or {}
    if relationships:
        lines.append("Einschaetzung der anderen:")
        lines.extend(f"- {k}: {v}" for k, v in relationships.items())

    goals = state.get("goals") or []
    if goals:
        lines.append("Offene Vorhaben:")
        lines.extend(f"- {g}" for g in goals)

    tactics_notes = state.get("tactics_notes") or ""
    if tactics_notes:
        lines.append(f"Taktischer Merksatz: {tactics_notes}")

    round_history = state.get("round_history") or {}
    if round_history:
        last_keys = sorted(round_history.keys(), key=lambda k: int(k))[-3:]
        lines.append("Letzte Runden:")
        for k in last_keys:
            entry = round_history[k]
            mission = f" ({entry['mission']})" if entry.get("mission") else ""
            lines.append(f"- Runde {k}{mission}: {entry.get('kernereignis', '')}")
    rounds_summary = (state.get("summary") or {}).get("rounds_summary") or ""
    if rounds_summary:
        lines.append(f"Aeltere Runden (verdichtet): {rounds_summary}")

    return "\n".join(lines)


def update_state(
    state: dict,
    round_no: int,
    kernereignis: str,
    new_learnings: list[str] | None = None,
    relationship_updates: dict[str, str] | None = None,
    new_goals: list[str] | None = None,
    now: str = "",
    datum: str = "",
    mission: str | None = None,
    tactics_notes: str | None = None,
) -> dict:
    """Gibt einen NEUEN, aktualisierten State zurueck (Input bleibt unangetastet).

    Anti-Stacking-Gate: `round_no <= state['rounds_played']` -> Runde wurde
    bereits verarbeitet, keine Doppel-Buchung."""
    st = json.loads(json.dumps(state))  # deep copy, keine Mutation des Inputs
    rounds_played = st.get("rounds_played", 0)

    if round_no <= rounds_played:
        return st

    round_history = st.setdefault("round_history", {})
    entry = {"datum": datum or now, "kernereignis": kernereignis}
    if mission:
        entry["mission"] = mission
    round_history[str(round_no)] = entry
    st["rounds_played"] = round_no

    summary = st.setdefault("summary", {"rounds_summary": "", "learnings_summary": ""})
    summary.setdefault("rounds_summary", "")
    summary.setdefault("learnings_summary", "")
    while len(round_history) > ROUND_HISTORY_CAP:
        oldest_key = min(round_history.keys(), key=lambda k: int(k))
        oldest = round_history.pop(oldest_key)
        addition = f"R{oldest_key}: {oldest.get('kernereignis', '')}"
        summary["rounds_summary"] = (
            f"{summary['rounds_summary']} {addition}".strip()
            if summary["rounds_summary"]
            else addition
        )

    learnings = st.setdefault("learnings", [])
    for l in new_learnings or []:
        learnings.append(l)
    while len(learnings) > LEARNINGS_CAP:
        oldest = learnings.pop(0)
        summary["learnings_summary"] = (
            f"{summary['learnings_summary']} {oldest}".strip()
            if summary["learnings_summary"]
            else oldest
        )

    relationships = st.setdefault("relationships", {})
    for k, v in (relationship_updates or {}).items():
        relationships[k] = v

    goals = st.setdefault("goals", [])
    for g in new_goals or []:
        goals.append(g)
    while len(goals) > GOALS_CAP:
        goals.pop(0)

    if tactics_notes is not None:
        st["tactics_notes"] = tactics_notes

    st["last_updated"] = now or datum

    return st


class PersonaStateStore:
    """Buendelt Schema-Pfad + optionalen Default-States-Ordner.

    A2/A6 (bindend): `schema_path` ist PFLICHT, kein `__file__`-relativer
    Default. `default_states_dir` ist optional — wird bei jedem Aufruf ein
    expliziter `states_dir` mitgegeben (wie es die gesamte mmo_sim-Runtime
    tut), wird der Default nie gebraucht."""

    def __init__(self, schema_path: str | Path, default_states_dir: str | Path | None = None):
        self.schema_path = Path(schema_path)
        self.default_states_dir = Path(default_states_dir) if default_states_dir else None
        self._schema_cache: dict | None = None

    def _load_schema(self) -> dict:
        if self._schema_cache is None:
            self._schema_cache = json.loads(self.schema_path.read_text(encoding="utf-8"))
        return self._schema_cache

    def validate_state(self, state: dict) -> None:
        schema = self._load_schema()
        if jsonschema is not None:
            jsonschema.validate(instance=state, schema=schema)
            return
        for req in schema.get("required", []):
            if req not in state:
                raise ValueError(f"persona state fehlt Pflichtfeld: {req}")
        if state.get("v") != 2:
            raise ValueError("persona state 'v' muss 2 sein")

    def _resolve_dir(self, states_dir: str | Path | None) -> Path:
        d = Path(states_dir) if states_dir else self.default_states_dir
        if d is None:
            raise ValueError(
                "states_dir muss angegeben werden (kein default_states_dir konfiguriert)."
            )
        return d

    def load_state(self, pk: str, states_dir: str | Path | None = None) -> dict:
        d = self._resolve_dir(states_dir)
        with open(d / f"{pk}.json", encoding="utf-8") as f:
            return json.load(f)

    def save_state(self, pk: str, state: dict, states_dir: str | Path | None = None) -> Path:
        """Validiert gegen das Schema, schreibt dann atomar (temp+rename)."""
        self.validate_state(state)
        d = self._resolve_dir(states_dir)
        d.mkdir(parents=True, exist_ok=True)
        target = d / f"{pk}.json"
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, target)
        return target

    # Domaenenneutrale Funktionen bleiben zusaetzlich als Methoden erreichbar,
    # damit ein Aufrufer nur EIN Objekt (die Store-Instanz) braucht.
    render_for_prompt = staticmethod(render_for_prompt)
    update_state = staticmethod(update_state)
