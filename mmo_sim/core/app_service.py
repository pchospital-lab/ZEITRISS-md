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

from typing import Callable

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
    status_fn: Callable[[str], None] | None = None,
    completion_fallback: Callable[[str, str | None], bool] | None = None,
    harvest_conflict_detector: Callable[[str, dict[str, str]], list[str]] | None = None,
    explicit_completion_attempt: Callable[[str | None], bool] | None = None,
    save_guard_rejection_detector: Callable[[str], bool] | None = None,
) -> SectionOutcome:
    """EIN gemeinsamer Einstiegspunkt fuer "einen Abschnitt an einem Tisch
    spielen". Baut die `SectionRuntime` und delegiert an
    `run_full_section` — TUI und Lab rufen NUR diese Funktion auf, nicht
    `SectionRuntime` je eigenstaendig (I1/A4).

    W51 (01_RESTAUFTRAG.md §3): `status_fn`, additiv und OPTIONAL (Default
    `None`), reicht nur die menschlich lesbaren Korrektur-Statuszeilen des
    bestehenden `save_correction.pursue_group_save_correction`-`emit`-Hooks
    an den Aufrufer durch (s. `SectionRuntime`-Docstring) -- `lab/runner.py`
    (headless, Persona-only) uebergibt es nicht und bleibt dadurch
    unveraendert stumm; `ui/tui.py` reicht `self._print`.

    OPTION2-CMD (FIX-SPEC-OPTION2-CMD.md): `completion_fallback`, additiv
    und OPTIONAL (Default `None` -> unveraendertes Marker-only-Verhalten),
    wird 1:1 an `SectionRuntime` durchgereicht -- reiner Durchreicher, diese
    Funktion kennt den Inhalt des Praedikats nicht (A1-Konsistenz)."""
    runtime = SectionRuntime(
        lobby, table, gm_transport, marker, harvest_validator,
        persona_state_store, harvest_extractor, event_log=event_log, status_fn=status_fn,
        completion_fallback=completion_fallback,
        harvest_conflict_detector=harvest_conflict_detector,
        explicit_completion_attempt=explicit_completion_attempt,
        save_guard_rejection_detector=save_guard_rejection_detector,
    )
    return runtime.run_full_section(
        controller, section_id, contexts_by_persona, states_dir, today, ts, max_turns=max_turns,
    )
