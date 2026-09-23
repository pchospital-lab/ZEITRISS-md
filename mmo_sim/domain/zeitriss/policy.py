#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/policy.py — ZEITRISS-Domaenenregeln als injizierbare
Policy-Objekte fuer den neutralen `mmo_sim.core.store` (A1, PLAN-CRITIC.md
BLOCKER).

`core/store.py` kennt weder "5" (Tischgrenze) noch "v7"/"char_id"
(Save-Semantik) — diese Regeln leben ausschliesslich hier. Ein anderer
Bausatz (ACCILOG/ARXION, spaeter) wuerde eine eigene Policy unter
`domain/<projekt>/policy.py` implementieren, ohne `core/store.py` anzufassen.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import saves as save_lib

COMPLETION_MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"


@dataclass
class ZeitrissTableSizePolicy:
    """Fuenfer-Tischgrenze (02 §4 / 11 §8): 1-5 Spieler insgesamt, Leader
    eingeschlossen, Mensch+KI zusammen."""

    min_size: int = 1
    max_size: int = 5

    def validate_size(self, size: int) -> bool:
        return self.min_size <= size <= self.max_size


@dataclass
class ZeitrissHarvestValidator:
    """v7-Save-Semantik (genau 1 Figur pro Block, passende char_id) — reine
    ZEITRISS-Regel. `core/store.py` ruft nur `validate_block`/`validate_identity`
    auf und kennt den Inhalt dieser Pruefung nicht (A1/A27)."""

    def validate_block(self, block: dict | None, expected_chrononaut_id: str) -> bool:
        if block is None:
            return False
        if block.get("v") != 7:
            return False
        if save_lib.single_character_count(block) != 1:
            return False
        cid = save_lib.block_char_id(block)
        return cid == expected_chrononaut_id

    def validate_identity(self, state: dict, persona_key: str, expected_chrononaut_id: str) -> bool:
        return (
            state.get("persona_key") == persona_key
            and state.get("plays_char", {}).get("character_id") == expected_chrononaut_id
        )


class NullHarvestValidator:
    """A27-Referenzimplementierung fuer einen NEUTRALEN Dummy-Bausatz ohne
    Char-ID-Konzept: akzeptiert jeden nicht-leeren Block und jede Identitaet,
    die nur den `persona_key` matcht. Beweist, dass `core/store.py` keine
    ZEITRISS-Regel erzwingt — ein Dummyfall OHNE Char-ID scheitert hier NICHT
    an einer generischen Spielklassenpflicht."""

    def validate_block(self, block: dict | None, expected_id: str) -> bool:
        return bool(block)

    def validate_identity(self, state: dict, persona_key: str, expected_id: str) -> bool:
        return state.get("persona_key") == persona_key
