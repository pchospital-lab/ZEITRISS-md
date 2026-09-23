#!/usr/bin/env python3
"""
mmo_sim/domain/zeitriss/community_bootstrap.py — Crash-sichere
Community-/Generation-Initialisierung (A3, PLAN-CRITIC.md WICHTIG; 04 §A10).

Folgt EXAKT demselben Journal-Muster wie `core/store.complete_section`:
  1. Persistenter Bootstrap-Plan (`bootstrap__plan.json`) mit der VOLLEN
     Ziel-Persona-Liste — EINMALIG gepinnt, ein Retry nutzt ihn unveraendert
     wieder (kein Neuwuerfeln bei Crash-Recovery).
  2. Pro-Persona-Guard-Dateien (`bootstrap__<pk>.guard.json`) — eine bereits
     geschriebene Persona wird bei Resume NICHT erneut geschrieben.
  3. EIN `bootstrap__final.json`-Marker als EINZIGER "Community vollstaendig
     initialisiert"-Nachweis — existiert er, ist jeder weitere Aufruf ein
     No-op (`already_completed=True`).

Keine "Datei existiert?"-Kurzschluss-Pruefung (PLAN-CRITIC.md A3 Kritik) —
Resume iteriert wieder ALLE Personas des gepinnten Plans und ueberspringt nur
die mit vorhandenem Guard.

Modellgenerierte Motivations-/Stil-Vorgaben (`target_personas`-Payload) werden
in diesem Bauauftrag NICHT per echtem Modellaufruf erzeugt — der Aufrufer
uebergibt vorbereitete/gemockte Payloads (03 §7: keine echten Modellaufrufe in
diesem Block). Ein spaeterer Live-Adapter fuer "Start-Personas erzeugen"
bleibt ein separater, budgetierter Schritt.

P2-Fertigstellung (I4, PLAN-CRITIC.md A6-HINWEIS): NUR die Payload-
Persistenztreue wird repariert (vollstaendige Felduebernahme aus
`target_personas[pk]` inkl. `archetype`/`play_style`/`charwunsch`, kein
Verwerfen) — NICHT die Erzeugung dieser Felder fuer brandneue Communities
ohne vorgegebenes Fixture (bleibt separater, budgetierter Live-Schritt, s.
oben). `target_personas[pk]` darf entweder ein bereits vollstaendiger
Persona-State (reales Schema, z.B. ein Fixture) ODER ein minimaler
Test-/Dummy-Payload (nur die vom jeweils aktiven Schema geforderten Felder)
sein — dieser Kern validiert nur gegen das injizierte Schema, erfindet
selbst keine Felder."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ...core.persona_state import PersonaStateStore


@dataclass
class BootstrapResult:
    community_id: str
    generation: int
    personas_written: list[str]
    already_completed: bool
    reason: str


def _plan_path(community_dir: Path) -> Path:
    return community_dir / "bootstrap__plan.json"


def _guard_path(community_dir: Path, persona_key: str) -> Path:
    safe = persona_key.replace("/", "_")
    return community_dir / f"bootstrap__{safe}.guard.json"


def _final_path(community_dir: Path) -> Path:
    return community_dir / "bootstrap__final.json"


def bootstrap_community(
    community_dir: str | Path, community_id: str, generation: int,
    target_personas: dict[str, dict], persona_state_store: PersonaStateStore,
    states_dir: str | Path, today: str,
) -> BootstrapResult:
    """`target_personas`: persona_key -> {"real_name": ..., "plays_char": {...}}.
    `today` OHNE Default (A5-Konsistenz): Aufrufer MUSS das reale Datum
    uebergeben."""
    community_dir = Path(community_dir)
    community_dir.mkdir(parents=True, exist_ok=True)
    final_path = _final_path(community_dir)
    plan_path = _plan_path(community_dir)

    if final_path.exists():
        final_data = json.loads(final_path.read_text(encoding="utf-8"))
        if final_data.get("community_id") != community_id:
            return BootstrapResult(
                community_id=community_id, generation=generation, personas_written=[],
                already_completed=False,
                reason=(
                    f"Bootstrap-Abschluss gehoert bereits community_id="
                    f"{final_data.get('community_id')!r} — keine Neuanlage unter fremder ID."
                ),
            )
        return BootstrapResult(
            community_id=community_id, generation=generation,
            personas_written=list(final_data.get("personas") or []),
            already_completed=True, reason="Community bereits vollstaendig initialisiert — kein zweiter Bootstrap.",
        )

    if plan_path.exists():
        plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
        if plan_data.get("community_id") != community_id:
            return BootstrapResult(
                community_id=community_id, generation=generation, personas_written=[],
                already_completed=False,
                reason=(
                    f"Bootstrap-Plan gehoert bereits community_id={plan_data.get('community_id')!r} "
                    f"— Kollision, kein Ueberschreiben eines fremden Plans."
                ),
            )
    else:
        # EINMALIG pinnen: die volle Ziel-Persona-Liste UND ihre Payloads —
        # ein spaeterer Retry darf NIE eine abweichende Liste verwenden.
        plan_data = {
            "community_id": community_id, "generation": generation,
            "personas": target_personas,
        }
        plan_path.write_text(json.dumps(plan_data, ensure_ascii=False, indent=2), encoding="utf-8")

    written: list[str] = []
    for pk, payload in plan_data["personas"].items():
        guard_path = _guard_path(community_dir, pk)
        if guard_path.exists():
            # Bereits in einem frueheren (abgebrochenen) Versuch geschrieben —
            # kein zweiter State-Write (Anti-Doppel-Roster, A10).
            written.append(pk)
            continue
        # I4-Fix (A6): VOLLE Felduebernahme aus dem gepinnten Payload (z.B.
        # `archetype`/`play_style`/`charwunsch`, vom realen Schema
        # verlangt) statt einer festen Teilmenge -- nur die vom Bootstrap
        # selbst kontrollierten Felder werden ueberschrieben/ergaenzt.
        state = dict(payload)
        state["v"] = 2
        state["persona_key"] = pk
        state.setdefault("real_name", pk)
        state.setdefault("plays_char", {})
        state["rounds_played"] = 0
        state["last_updated"] = today
        persona_state_store.save_state(pk, state, states_dir=states_dir)
        guard_path.write_text(
            json.dumps({"persona_key": pk, "status": "written", "community_id": community_id}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        written.append(pk)

    final_path.write_text(
        json.dumps({"community_id": community_id, "generation": generation, "personas": written},
                    ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return BootstrapResult(
        community_id=community_id, generation=generation, personas_written=written,
        already_completed=False, reason="Community-Bootstrap vollstaendig abgeschlossen.",
    )
