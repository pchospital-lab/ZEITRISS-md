#!/usr/bin/env python3
"""
mmo_sim/core/scheduler.py — fairer Turn-Scheduler (PLAN.md §3 Antwort 6/8).

"Ein fairer Scheduler ermoeglicht Beteiligung, entscheidet aber nicht fuer
die Personas" (02 §8). Verwaltet begrenzte Initiativfenster/Einladungen —
NICHT, wer eine Einladung annimmt oder was jemand sagt. Round-Robin ueber
angemeldete Teilnehmer, mit optionalem Ausschluss bereits gebundener/
pausierter Teilnehmer."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InitiativeWindow:
    persona_key: str
    opened_ts: str
    expires_after_turns: int = 1


class FairScheduler:
    """Reine Reihenfolge-/Fairness-Buchhaltung, KEINE Persona-Entscheidung."""

    def __init__(self, participants: list[str]):
        self._order = list(participants)
        self._cursor = 0
        self._paused: set[str] = set()
        self._open_windows: dict[str, InitiativeWindow] = {}

    def pause(self, persona_key: str) -> None:
        self._paused.add(persona_key)

    def resume(self, persona_key: str) -> None:
        self._paused.discard(persona_key)

    def active_participants(self) -> list[str]:
        return [p for p in self._order if p not in self._paused]

    def next_initiative(self) -> str | None:
        """Round-Robin ueber aktive Teilnehmer. `None`, wenn niemand aktiv ist
        (z.B. alle pausiert — normaler `play`-Betrieb pausiert dann ebenfalls,
        s. lab/runner.py)."""
        active = self.active_participants()
        if not active:
            return None
        for _ in range(len(self._order)):
            candidate = self._order[self._cursor % len(self._order)]
            self._cursor += 1
            if candidate in active:
                return candidate
        return None

    def open_window(self, persona_key: str, ts: str, expires_after_turns: int = 1) -> InitiativeWindow:
        window = InitiativeWindow(persona_key=persona_key, opened_ts=ts, expires_after_turns=expires_after_turns)
        self._open_windows[persona_key] = window
        return window

    def close_window(self, persona_key: str) -> None:
        self._open_windows.pop(persona_key, None)

    def open_windows(self) -> list[InitiativeWindow]:
        return list(self._open_windows.values())
