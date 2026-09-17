#!/usr/bin/env python3
"""
Persona-State v2 — Laden/Rendern/Fortschreiben/Speichern (2026-09-17).

Reine Funktionsbibliothek, keine SL-/Netz-Calls. Implementiert die in
personas/PERSONA-STATE.md dokumentierte v2-Mechanik 1:1:

  - Anti-Stacking-Gate ueber `rounds_played` (nicht Key-Lookup, siehe
    PERSONA-STATE.md "Warum das Gate ueber rounds_played laeuft").
  - Keyed-Append fuer `round_history` (Key = Rundennummer als String).
  - Cap+Prune fuer `round_history` (Detail-Fenster 6) und `learnings` (Cap 10),
    Verdichtung des Herausfallenden in `summary.rounds_summary` /
    `summary.learnings_summary` statt Datenverlust.
  - `relationships`: Merge/Overwrite pro Key. `goals`: Append + Cap 8, aeltestes
    faellt ersatzlos weg (kein Verdichtungsfeld, siehe Schema-Doku).

Kein Date.now()-Aequivalent: `now`/`datum` werden immer als Parameter
uebergeben (Reproduzierbarkeit, siehe state_roundtrip_demo.py).
"""
from __future__ import annotations
import json
import os
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover - jsonschema ist auf dieser VM vorhanden
    jsonschema = None

_HERE = Path(__file__).resolve().parent
_PERSONAS_DIR = _HERE.parent / "personas"
_SCHEMA_PATH = _PERSONAS_DIR / "persona-state.schema.json"
_DEFAULT_STATES_DIR = _PERSONAS_DIR / "state-2026-09-16"

ROUND_HISTORY_CAP = 6
LEARNINGS_CAP = 10
GOALS_CAP = 8

_SCHEMA_CACHE: dict | None = None


def _load_schema() -> dict:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is None:
        _SCHEMA_CACHE = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    return _SCHEMA_CACHE


def validate_state(state: dict) -> None:
    """Wirft bei Verstoss gegen persona-state.schema.json. Kein Rueckgabewert."""
    schema = _load_schema()
    if jsonschema is not None:
        jsonschema.validate(instance=state, schema=schema)
        return
    # Fallback ohne jsonschema-Lib: nur die Kernfelder pruefen.
    for req in schema.get("required", []):
        if req not in state:
            raise ValueError(f"persona state fehlt Pflichtfeld: {req}")
    if state.get("v") != 2:
        raise ValueError("persona state 'v' muss 2 sein")


def load_state(pk: str, states_dir: str | Path | None = None) -> dict:
    d = Path(states_dir) if states_dir else _DEFAULT_STATES_DIR
    with open(d / f"{pk}.json", encoding="utf-8") as f:
        return json.load(f)


def render_for_prompt(state: dict) -> str:
    """Kompakter Text-Block zum Injizieren in den Persona-Turn-Prompt."""
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
    bereits verarbeitet, keine Doppel-Buchung. Es wird eine flache Kopie
    zurueckgegeben (idempotent bzgl. round_history/rounds_played), andere
    Felder (relationships/goals/tactics_notes) werden in diesem Fall NICHT
    zusaetzlich fortgeschrieben, da sie an dieselbe Rundenverarbeitung
    gekoppelt sind wie der Rundeneintrag selbst.
    """
    st = json.loads(json.dumps(state))  # deep copy, keine Mutation des Inputs
    rounds_played = st.get("rounds_played", 0)

    if round_no <= rounds_played:
        # Anti-Stacking-Gate: Runde bereits verarbeitet, unveraendert zurueckgeben.
        return st

    # ── round_history: keyed-Append + rounds_played fortschreiben ──────────
    round_history = st.setdefault("round_history", {})
    entry = {"datum": datum or now, "kernereignis": kernereignis}
    if mission:
        entry["mission"] = mission
    round_history[str(round_no)] = entry
    st["rounds_played"] = round_no

    # ── round_history Cap+Prune (Detail-Fenster 6) ──────────────────────────
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

    # ── learnings: Append + Cap+Prune ───────────────────────────────────────
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

    # ── relationships: Merge/Overwrite pro Key ──────────────────────────────
    relationships = st.setdefault("relationships", {})
    for k, v in (relationship_updates or {}).items():
        relationships[k] = v

    # ── goals: Append + Cap (aeltestes faellt ersatzlos weg) ────────────────
    goals = st.setdefault("goals", [])
    for g in new_goals or []:
        goals.append(g)
    while len(goals) > GOALS_CAP:
        goals.pop(0)

    if tactics_notes is not None:
        st["tactics_notes"] = tactics_notes

    st["last_updated"] = now or datum

    return st


def save_state(pk: str, state: dict, states_dir: str | Path | None = None) -> Path:
    """Validiert gegen das Schema, schreibt dann atomar (temp+rename)."""
    validate_state(state)
    d = Path(states_dir) if states_dir else _DEFAULT_STATES_DIR
    d.mkdir(parents=True, exist_ok=True)
    target = d / f"{pk}.json"
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, target)
    return target
