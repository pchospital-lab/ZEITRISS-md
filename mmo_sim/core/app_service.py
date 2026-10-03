#!/usr/bin/env python3
"""
mmo_sim/core/app_service.py — gemeinsamer Application-Service-Einstieg (I1,
PLAN-CRITIC.md A4 WICHTIG).

REVIEW-P2.md §I1: "`SectionRuntime` wird nicht von TUI oder LabRunner
aufgerufen, obwohl Docstrings diese Verbindung behaupten." `run_play_session`
ist GENAU DIE EINE Funktion, die `ui/tui.py` (TUI, `l`-Kommando) UND
`lab/runner.LabRunner.run_section` (headless) aufrufen, um einen Abschnitt zu
spielen — kein zweiter, paralleler Spiel-Loop. `tests/mmo_sim/
test_a04_shared_app_service.py` (A4, neuer eigener Test) belegt per Spy, dass
beide Wege ueber DIESE Funktion laufen."""
from __future__ import annotations

from .events import EventLog
from .persona_state import PersonaStateStore
from .runtime import SectionOutcome, SectionRuntime
from .store import HarvestValidator, Lobby, Table


def run_play_session(
    lobby: Lobby,
    table: Table,
    gm_transport,
    controller,
    section_id: str,
    contexts_by_persona: dict[str, dict],
    states_dir,
    today: str,
    ts: str,
    marker: str,
    harvest_validator: HarvestValidator,
    persona_state_store: PersonaStateStore,
    harvest_extractor,
    event_log: EventLog | None = None,
    max_turns: int | None = None,
) -> SectionOutcome:
    """EIN gemeinsamer Einstiegspunkt fuer "einen Abschnitt an einem Tisch
    spielen". Baut die `SectionRuntime` und delegiert an
    `run_full_section` — TUI und Lab rufen NUR diese Funktion auf, nicht
    `SectionRuntime` je eigenstaendig (I1/A4)."""
    runtime = SectionRuntime(
        lobby, table, gm_transport, marker, harvest_validator,
        persona_state_store, harvest_extractor, event_log=event_log,
    )
    return runtime.run_full_section(
        controller, section_id, contexts_by_persona, states_dir, today, ts, max_turns=max_turns,
    )
