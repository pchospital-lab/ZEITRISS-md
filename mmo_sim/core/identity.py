#!/usr/bin/env python3
"""
mmo_sim/core/identity.py — Identitaetsbegriffe (PLAN.md §3 Antwort 2).

Reine, domaenenneutrale Typen/Erzeuger. Kennt keine ZEITRISS-Regel:
`chrononaut_id` ist hier nur ein String-Alias (die v7-Char-ID-Bedeutung liefert
`domain/zeitriss`), `participant_id` ist STABIL und NICHT identisch mit einer
Char-ID (11 §6/§9 — ein Teilnehmer kann mehrere Chrononauten besitzen).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

ParticipantId = str
PersonaKey = str
ChrononautId = str
CommunityId = str
TableId = str
SectionId = str
RequestId = str
MessageId = str


def new_participant_id() -> ParticipantId:
    # A8/D1 (WEGKARTE §8, Plan-Critic A8, Test 02): direkt schema-konform
    # erzeugen (`^[a-z][a-z0-9_]*$`, s. persona-state.schema.json) -- die
    # participant_id wird an mehreren Stellen (`domain/zeitriss/onboarding.
    # py:ensure_participant_persona_state`) 1:1 als `persona_key`
    # uebernommen. Kein Bindestrich, kein Aufweichen der Schema-Validierung.
    return f"p{uuid.uuid4().hex[:16]}"


def new_community_id() -> CommunityId:
    return f"community-{uuid.uuid4().hex[:12]}"


def new_request_id() -> RequestId:
    return f"req-{uuid.uuid4().hex[:12]}"


def new_message_id() -> MessageId:
    return f"msg-{uuid.uuid4().hex[:12]}"


def new_table_id() -> TableId:
    return f"table-{uuid.uuid4().hex[:8]}"


@dataclass(frozen=True)
class ParticipantRef:
    """Stabile Teilnehmer-Identitaet — Mensch ODER Persona, unabhaengig von
    der Anzahl gebundener Anwendungsdatensaetze (Chrononauten)."""

    participant_id: ParticipantId
    kind: str  # "human" | "persona"
    display_name: str


@dataclass(frozen=True)
class CommunityRef:
    community_id: CommunityId
    generation: int = 1
