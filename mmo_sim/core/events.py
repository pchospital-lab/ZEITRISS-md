#!/usr/bin/env python3
"""
mmo_sim/core/events.py — validierte Event-Typen (gemeinsam TUI+Lab, PLAN.md §2).

Ein Append-only JSONL-Eventlog pro `run_dir`. Dient (a) `reports/report.py`
als alleinige Quelle fuer lokale Berichte (kein Modellcall), (b) der
Fehlerpunktmatrix (04 §4) als nachvollziehbarer Beleg vor/nach jedem Write.

Kein Event ohne bekannten `event_type` (Validierung beim Anhaengen) — verwirft
still-inkonsistente Ereignisse frueh, statt sie unbemerkt im Report auftauchen
zu lassen.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import identity

KNOWN_EVENT_TYPES = {
    "lobby_joined",
    "table_created",
    "table_rejected",
    "message_posted",
    "sl_turn",
    "section_completed",
    "section_completion_rejected",
    "onboarding_started",
    "onboarding_step",
    "onboarding_completed",
    "onboarding_aborted",
    "community_bootstrap_started",
    "community_bootstrap_persona_written",
    "community_bootstrap_completed",
    "import_previewed",
    "import_applied",
    "import_rejected",
    "character_switched",
    "human_joined",
    "human_left",
    "play_paused",
    "play_resumed",
    "lab_started",
    "lab_stopped",
    "provider_error",
    "provider_auth_missing",
}


class UnknownEventTypeError(ValueError):
    pass


@dataclass
class Event:
    event_id: str
    event_type: str
    actor: str | None
    payload: dict
    ts: str  # vom Aufrufer uebergeben (keine implizite Uhrzeit im Kern)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "payload": self.payload,
            "ts": self.ts,
        }


class EventLog:
    """Append-only JSONL unter `<run_dir>/events.jsonl`."""

    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.run_dir / "events.jsonl"

    def append(self, event_type: str, ts: str, actor: str | None = None, payload: dict | None = None) -> Event:
        if event_type not in KNOWN_EVENT_TYPES:
            raise UnknownEventTypeError(f"unbekannter event_type: {event_type!r}")
        ev = Event(
            event_id=identity.new_message_id(), event_type=event_type,
            actor=actor, payload=payload or {}, ts=ts,
        )
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
        return ev

    def read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # korrupte Zeile ueberspringen, kein Absturz des Reports
        return out
