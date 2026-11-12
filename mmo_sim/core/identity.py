#!/usr/bin/env python3
"""
mmo_sim/core/identity.py — Identitaetsbegriffe (PLAN.md §3 Antwort 2).

Reine, domaenenneutrale Typen/Erzeuger. Kennt keine ZEITRISS-Regel:
`chrononaut_id` ist hier nur ein String-Alias (die v7-Char-ID-Bedeutung liefert
`domain/zeitriss`), `participant_id` ist STABIL und NICHT identisch mit einer
Char-ID (11 §6/§9 — ein Teilnehmer kann mehrere Chrononauten besitzen).
"""
from __future__ import annotations

import re
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

# Fix C (ZR-SPIEL-S1, LINUS-SPEC §Fix C): Spiegel der persona_key-Schemaregel
# aus `internal/qa/fixtures/persona-state.schema.json` Zeile 25
# (`^[a-z][a-z0-9_]*$`) -- EINE Quelle fuer den participant_id-Vertrag, nicht
# aufweichen. `new_participant_id()` erfuellt diese Regel bereits.
PARTICIPANT_ID_PATTERN = r"^[a-z][a-z0-9_]*$"
_PARTICIPANT_ID_RE = re.compile(PARTICIPANT_ID_PATTERN)


def is_valid_participant_id(pid: object) -> bool:
    """True nur fuer einen `str`, der `PARTICIPANT_ID_PATTERN` erfuellt."""
    return isinstance(pid, str) and bool(_PARTICIPANT_ID_RE.match(pid))


class InvalidParticipantId(ValueError):
    """Eine participant_id verletzt `PARTICIPANT_ID_PATTERN`."""


def validate_participant_id(pid: object, *, source: str) -> None:
    """Wirft `InvalidParticipantId` mit einer verstaendlichen deutschen
    Meldung, wenn `pid` den Vertrag `PARTICIPANT_ID_PATTERN` verletzt.
    Nennt die ID, die Quelle (z.B. "explizit --participant" oder
    "gespeicherte last_participant.json") und den Vertrag -- und weist
    darauf hin, dass KEINE automatische Ersetzung erfolgt und der
    Bestand erhalten bleibt.

    R3-Nachzug (02_ENGER_NACHZUG.md R3, LINUS-SPEC-N1.md): die Abschluss-
    zeile ist QUELLBEWUSST -- fuer einen ungueltigen MARKER (`last_
    participant.json`) ist "ohne --participant starten" KEINE Heilung
    (`_resolve_participant_id` liest ohne `--participant`-Override genau
    denselben ungueltigen Marker erneut und wirft wieder), anders als beim
    explizit uebergebenen `--participant`. Vertrag/Regex bleiben unveraendert
    -- nur die Handlungsempfehlung unterscheidet sich je Quelle."""
    if is_valid_participant_id(pid):
        return
    if "last_participant.json" in source:
        guidance = (
            "Keine automatische Ersetzung -- der vorhandene Bestand bleibt "
            "erhalten. Bitte den Marker mit einer gueltigen ID korrigieren "
            "oder entfernen (ein blosses Weglassen von --participant liest "
            "denselben ungueltigen Marker erneut und heilt ihn NICHT "
            "automatisch)."
        )
    else:
        guidance = (
            "Keine automatische Ersetzung -- der vorhandene Bestand bleibt "
            "erhalten. Bitte eine gueltige ID angeben oder ohne "
            "--participant starten, um eine neue gueltige ID erzeugen zu "
            "lassen."
        )
    raise InvalidParticipantId(
        f"Ungueltige Teilnehmer-ID {pid!r} ({source}): entspricht nicht dem "
        f"Vertrag '{PARTICIPANT_ID_PATTERN}' (klein beginnend, nur "
        f"a-z/0-9/_). {guidance}"
    )


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
