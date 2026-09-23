#!/usr/bin/env python3
"""
mmo_sim/core/controller.py — EIN lokaler Controller (Human+Persona-Input,
PLAN.md §3 Antwort 1).

Nimmt validierte Entscheidungen von `ParticipantDriver`-Instanzen entgegen.
Human-Driver (Terminal/geskriptet) und Persona-Driver (API/CLI/Fake)
implementieren dasselbe Protokoll — der Controller selbst unterscheidet nicht,
WOHER eine Entscheidung kommt, nur WER Leader ist (Leader-only-Send bleibt
Aufgabe von `core/store.submit_to_sl`, hier nur die Vorbereitung/Kontext-Bau).

M2/Auftrag: "Aufrufinhalt kommt aus Human-/Persona-Entscheidungen. Technische
Serialisierung eines freigegebenen Textes plus aktuellem persoenlichen Save
ist zulaessig." — `TableController` fragt jeden Treiber einzeln, formt daraus
den an `submit_to_sl` uebergebenen Text/Payload, formuliert aber selbst KEINE
Persona-Entscheidung.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..adapters.base import ParticipantDecision, ParticipantDriver


@dataclass
class TurnRecord:
    persona_key: str
    decision: ParticipantDecision


class TableController:
    """Ein Controller pro Tisch. `drivers` bildet persona_key -> Driver ab;
    `leader_key` bestimmt, wessen serialisierte Nachricht tatsaechlich an
    `submit_to_sl` geht (nur der Leader sendet, COORDINATION-MODEL-FROZEN
    Punkt 3 — unveraendert)."""

    def __init__(self, leader_key: str, drivers: dict[str, ParticipantDriver]):
        if leader_key not in drivers:
            raise ValueError(f"leader_key {leader_key!r} nicht in drivers vorhanden")
        self.leader_key = leader_key
        self.drivers = drivers

    def collect_decision(self, persona_key: str, context: dict) -> TurnRecord:
        """Fragt GENAU EINEN Treiber nach seiner Entscheidung. Wirft
        `KeyError`, wenn `persona_key` nicht Teil dieses Tisches ist —
        kein Rateversuch, welcher Treiber gemeint sein koennte."""
        driver = self.drivers[persona_key]
        decision = driver.decide(context)
        return TurnRecord(persona_key=persona_key, decision=decision)

    def leader_decision(self, context: dict) -> TurnRecord:
        return self.collect_decision(self.leader_key, context)
