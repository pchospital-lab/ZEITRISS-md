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

from . import save_validation as save_validation_lib
from . import saves as save_lib

COMPLETION_MARKER = "SECTION-ABSCHLUSS-BESTAETIGT"

SAVE_COMMANDS = frozenset({"!save", "!speichern"})
"""OPTION2-CMD (FIX-SPEC-OPTION2-CMD.md, 2026-10-22): die dokumentierten
Save-Kommandos (`meta/project_bootstrap_instructions.md` §"`!save` und
`!speichern`"). `!bogen` ist NUR Ansicht und zaehlt NICHT als Save-Trigger."""


def is_save_command(text: str | None) -> bool:
    """True, wenn `text` (getrimmt, case-insensitiv) GENAU einem der
    `SAVE_COMMANDS` entspricht -- der Leader-Input dieses Turns, NICHT die
    GM-Antwort (s. `build_save_command_completion_fallback`)."""
    return (text or "").strip().casefold() in {c.casefold() for c in SAVE_COMMANDS}


def build_save_command_completion_fallback(table, harvest_extractor=save_lib.harvest_from_debrief):
    """OPTION2-CMD: baut das injizierbare `Callable[[str, str | None], bool]`-
    Fallback-Praedikat fuer `core.runtime.SectionRuntime(completion_fallback=
    ...)` (Runtime bleibt domaenen-neutral -- sie kennt nur das Ergebnis,
    nicht diese Kommando-/Bindungsregel). `table` wird PER CLOSURE gebunden
    (nicht erst beim Aufruf uebergeben), weil `core/app_service.py`/
    `core/lobby_flow.py`/`ui/tui.py` den Tisch bereits zur Konstruktionszeit
    kennen -- derselbe Wiring-Punkt wie `marker`/`harvest_validator`/
    `harvest_extractor`.

    Ersetzt die PHRASEN-basierte Variante (FIX-SPEC-OPTION2.md, verworfen):
    der live gehostete GM formuliert die Save-Bestaetigung FREI
    ("Deepsave wird ausgegeben"/"ausgegeben"/"exportiert") -- Prosa-Matching
    ist tot (live3). Der Trigger haengt jetzt an SEINEM `!save`-Kommando
    (`is_save_command`) + den tatsaechlichen Save-Bloecken, NICHT an
    GM-Worten: zusaetzlich zum Kommando muss `harvest_extractor` (Default
    `saves.harvest_from_debrief`) auf dem GM-Text mindestens einen Save
    liefern, der sich an einen AKTUELLEN Tisch-Chrononauten (`table.
    chrononaut_id_to_persona()`) binden laesst -- das schuetzt gegen ein
    blosses `!save` ohne echten Save (SaveGuard-Verweigerung ausserhalb HQ)
    UND gegen einen fremden/historischen Block, den `harvest_extractor`
    nicht an die aktuelle Bindung knuepfen kann (FIX-SPEC-OPTION2-CMD.md
    §Zielverhalten)."""

    def _fallback(gm_text: str, leader_input: str | None) -> bool:
        if not is_save_command(leader_input):
            return False
        cid_to_pk = table.chrononaut_id_to_persona()
        harvested = harvest_extractor(gm_text, cid_to_pk) if gm_text else {}
        return bool(harvested)

    return _fallback


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
    """v7-Save-Semantik (genau 1 Figur pro Block, passende char_id, UND --
    R12-Savegate, 01_AUFTRAG_SAVEGATE.md §A/§B -- volle lokale Schema-
    Validierung gegen BEIDE unveraenderten v7-Schemas) — reine ZEITRISS-
    Regel. `core/store.py` ruft nur `validate_block`/`validate_identity` auf
    und kennt den Inhalt dieser Pruefung nicht (A1/A27).

    R12-Fix (SC01 "Milder Harvest darf den Vollschemafehler nicht
    uebersteuern"): vorher pruefte diese Methode nur v7/Ein-Figur/char_id
    (milde Pruefung) -- ein Save, der diese drei Bedingungen erfuellt, aber
    strukturell gegen die v7-Schemas verstoesst (z.B. `economy.wallets.
    <id>` als blanke Zahl statt `{"balance": ...}`-Objekt), wurde bisher
    trotzdem als `completed`/Harvest-faehig akzeptiert. Jetzt delegiert
    diese Methode die volle Pruefung an `save_validation.validate_save_
    block` (Schema BEIDER Dateien + Bindung) -- `accepted` ist nur dann
    wahr, wenn WEDER die milde Pruefung NOCH die volle Schemapruefung einen
    Fehler findet. Dieser EINE Aufrufpunkt gilt fuer ALLE Nutzer dieser
    Klasse gleich: menschliche Erschaffung (`ui/tui.py`), Persona-
    Erst-/Zusatzfigur (`domain/zeitriss/community_creation.py`,
    `core/creation_service.py`), Import/Zusatzfigur-Uebernahme (`ui/tui.py`)
    UND der Fuenfer-Gruppenharvest vor Abschnittsabschluss
    (`core/lobby_flow.py` -> `core/app_service.py` -> `core/runtime.py` ->
    `core/store.py:_validate_harvest`/`complete_section`) -- `core/store.py`
    selbst bleibt dabei UNVERAENDERT (dieselben zwei generischen Protokoll-
    Methoden, A1/A27)."""

    def validate_block(self, block: dict | None, expected_chrononaut_id: str) -> bool:
        if block is None:
            return False
        if block.get("v") != 7:
            return False
        if save_lib.single_character_count(block) != 1:
            return False
        cid = save_lib.block_char_id(block)
        if cid != expected_chrononaut_id:
            return False
        return save_validation_lib.validate_save_block(block, expected_chrononaut_id).accepted

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
