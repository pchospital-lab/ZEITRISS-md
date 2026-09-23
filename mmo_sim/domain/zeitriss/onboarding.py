#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/onboarding.py — geführter, fortsetzbarer
Einzel-Erschaffungsabschnitt (11 §3, M2/A17).

"Ohne Save bietet die UI 'Neuen Chrononauten erschaffen' an. Sie legt
zunaechst NUR die menschliche Teilnehmeridentitaet und einen technischen,
fortsetzbaren Erschaffungsauftrag an." Abbruch vor erstem gueltigem Save:
Erschaffung bleibt unvollstaendig, KEINE Spielrunde zaehlt, KEIN leerer
v7-Save wird als fertig veroeffentlicht. Fortsetzen nimmt DIESELBE
Erschaffung wieder auf (kein unbemerktes Duplikat).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ...core.store import HarvestValidator


@dataclass
class OnboardingState:
    participant_id: str
    status: str  # "in_progress" | "completed" | "abandoned"
    steps: list[dict] = field(default_factory=list)
    final_save: dict | None = None


def _path(onboarding_dir: Path, participant_id: str) -> Path:
    safe = participant_id.replace("/", "_")
    return onboarding_dir / f"onboarding__{safe}.json"


def _load(path: Path) -> OnboardingState | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return OnboardingState(**data)


def _write(path: Path, state: OnboardingState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def peek(onboarding_dir: str | Path, participant_id: str) -> OnboardingState | None:
    """Reine Lesefunktion OHNE Seiteneffekt (I3-Fertigstellung): liefert den
    vorhandenen Auftrag oder `None` -- im Gegensatz zu `start_or_resume`
    legt `peek` NIEMALS einen neuen leeren Auftrag an. Fuer Stellen wie
    `ui/tui.py`s Fortsetzen-Karte, die nur PRUEFEN wollen, ob bereits
    Fortschritt existiert, ohne beim blossen Anzeigen des Menues bereits
    einen Erschaffungsauftrag zu erzeugen."""
    return _load(_path(Path(onboarding_dir), participant_id))


def start_or_resume(onboarding_dir: str | Path, participant_id: str, *, force_new: bool = False) -> OnboardingState:
    """Ein fehlender Charakter ist ein zulaessiger Onboardingzustand (11 §3)
    — legt bei erstem Aufruf einen leeren `in_progress`-Auftrag an, bei
    Wiederaufruf wird DERSELBE Auftrag zurueckgegeben (kein Duplikat).

    W4-Ergaenzung (F4, "zweite Erschaffung möglich", `ui/tui.py:_cmd_new_
    or_switch_character`): `force_new=True` startet BEWUSST einen frischen
    Erschaffungsauftrag, selbst wenn bereits ein `completed`-Auftrag
    vorliegt -- fuer eine EXPLIZIT gewaehlte weitere Figur. Dieser Auftrag
    bleibt (wie zuvor) ein reines fortsetzbares SCRATCH-Objekt fuer den
    GERADE laufenden Erschaffungsdialog ("Onboarding ≠ Mehrfigurenarchiv",
    WEGKARTE W4) -- die durable Mehrfigurenarchivierung uebernimmt
    `catalog.store_figure_save` (bereits abgeschlossene Figuren verlieren
    dabei NICHTS, ihre Bytes liegen dort bereits getrennt)."""
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    existing = _load(path)
    if not force_new:
        if existing is not None and existing.status == "in_progress":
            return existing
        if existing is not None and existing.status == "completed":
            return existing
    state = OnboardingState(participant_id=participant_id, status="in_progress")
    _write(path, state)
    return state


def record_step(onboarding_dir: str | Path, participant_id: str, question: str, answer: str) -> OnboardingState:
    """Jeder Schritt wird SOFORT persistiert (Crash-Sicherheit) — ein Abbruch
    zwischen zwei Fragen verliert nur die noch nicht beantwortete Frage,
    nicht den bisherigen Fortschritt."""
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    state = _load(path)
    if state is None or state.status != "in_progress":
        raise ValueError(f"kein offener Erschaffungsauftrag fuer {participant_id!r}")
    state.steps.append({"question": question, "answer": answer})
    _write(path, state)
    return state


def complete_with_save(
    onboarding_dir: str | Path, participant_id: str, save_block: dict,
    harvest_validator: HarvestValidator, expected_chrononaut_id: str,
) -> OnboardingState:
    """Markiert die Erschaffung erst dann als `completed`, wenn ein
    gueltiger (v7/Ein-Figur/passende char_id, geprueft ueber die injizierte
    Domaenen-Policy) Save vorliegt — vorher KEIN Dummy-v7, kein fingierter
    Fortschritt (11 §3)."""
    if not harvest_validator.validate_block(save_block, expected_chrononaut_id):
        raise ValueError(
            f"Save-Block fuer {participant_id!r} ist ungueltig oder passt nicht zur erwarteten "
            f"Chrononaut-ID {expected_chrononaut_id!r} — Erschaffung bleibt unvollstaendig."
        )
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    state = _load(path)
    if state is None:
        raise ValueError(f"kein Erschaffungsauftrag fuer {participant_id!r} — start_or_resume() zuerst aufrufen")
    state.status = "completed"
    state.final_save = save_block
    _write(path, state)
    return state


def ensure_participant_persona_state(
    persona_state_store, states_dir: str | Path, participant_id: str,
    chrononaut_id: str, save_block: dict,
) -> dict:
    """D1/A2 (PLAN-CRITIC-ABSCHLUSS.md BLOCKER): gemeinsamer Import-/
    Figurenservice -- stellt sicher, dass fuer `participant_id` ein
    gueltiger Persona-State existiert, den `ZeitrissHarvestValidator.
    validate_identity` akzeptiert (`persona_key`==participant_id,
    `plays_char.character_id`==chrononaut_id).

    Existiert bereits ein State (z.B. aus einer vorherigen Spielrunde),
    werden NUR die Identitaetsfelder (`persona_key`/`plays_char`) an den
    importierten Save angeglichen -- `rounds_played`/`learnings`/... bleiben
    unangetastet (Import zaehlt NICHT als gespielte Runde).

    Existiert noch KEIN State (frischer externer Import ohne vorherige
    Persona-Historie), wird ein neuer State mit KLAR TECHNISCH MARKIERTEN
    Platzhaltern fuer `real_name`/`archetype`/`play_style`/`charwunsch`
    angelegt -- NIE erfundene Charakterzuege (Grenzen §5/A22)."""
    chars = save_block.get("characters")
    char0 = chars[0] if isinstance(chars, list) and chars and isinstance(chars[0], dict) else {}
    plays_char = {
        "save_file": f"{participant_id}.json",
        "character_id": chrononaut_id,
        "name": char0.get("name", "?"),
        "callsign": char0.get("callsign", "?"),
    }
    try:
        state = persona_state_store.load_state(participant_id, states_dir=states_dir)
        state["persona_key"] = participant_id
        state["plays_char"] = plays_char
    except FileNotFoundError:
        state = {
            "v": 2,
            "persona_key": participant_id,
            "real_name": participant_id,
            "archetype": (
                "TECHNISCHER PLATZHALTER -- extern importierter Save, kein "
                "erspielter Archetyp/keine erfundene Charaktereigenschaft."
            ),
            "play_style": (
                "TECHNISCHER PLATZHALTER -- extern importierter Save, kein "
                "erspielter Spielstil."
            ),
            "charwunsch": (
                "TECHNISCHER PLATZHALTER -- kein Erschaffungsdialog "
                "durchlaufen (externer Import)."
            ),
            "plays_char": plays_char,
            "rounds_played": 0,
        }
    persona_state_store.save_state(participant_id, state, states_dir=states_dir)
    return state


def abandon(onboarding_dir: str | Path, participant_id: str) -> OnboardingState:
    """Bewusster Neustart (11 §3: 'ein Neustart ist bewusst zu waehlen') —
    erzeugt KEIN unbemerktes Duplikat, sondern markiert den alten Auftrag
    explizit als abgebrochen, bevor ein neuer begonnen wird."""
    onboarding_dir = Path(onboarding_dir)
    path = _path(onboarding_dir, participant_id)
    state = _load(path)
    if state is None:
        raise ValueError(f"kein Erschaffungsauftrag fuer {participant_id!r}")
    state.status = "abandoned"
    _write(path, state)
    return state
