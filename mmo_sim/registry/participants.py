#!/usr/bin/env python3
"""
mmo_sim/registry/participants.py — neutraler Teilnehmer-/Anwendungsdatensatz-
Hook (11 §9, PLAN.md §3 Antwort 11).

Minimal: stabile Teilnehmer-ID, getrennt referenzierter Anwendungsdatensatz
samt Schema-/Versions-/Herkunftsbezug, rollenbezogene Bindung. KEINE
"eine Persona = ein Datensatz fuer immer"-Regel — ein Teilnehmer kann mehrere
Datensaetze referenzieren (`domain/zeitriss/catalog.py` baut ZEITRISS-
spezifisch darauf auf, mit der zusaetzlichen EXKLUSIVEN Chrononaut-Bindung,
die eine konkrete ZEITRISS-Regel ist, keine universelle Registry-Regel).

Ein kleiner neutraler Dummy-Datensatz (`register_application_record` mit
`schema="dummy-v1"`) demonstriert die Trennung im Offline-Test — kein echter
Bausatz-Integrationstest fuer ACCILOG/ARXION (11 §9, ausdruecklich nicht
beauftragt).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..core import identity


@dataclass
class ApplicationRecordRef:
    record_id: str
    schema: str
    version: str
    owner_participant_id: str
    source: str = "local"  # z.B. "local" | "extern importiert"


@dataclass
class Participant:
    participant_id: str
    kind: str  # "human" | "persona"
    display_name: str
    record_refs: list[ApplicationRecordRef] = field(default_factory=list)


class ParticipantRegistry:
    """Datei-gestuetztes, domaenenneutrales Register. Kennt weder "Char-ID"
    noch "v7" — nur generische `record_id`/`schema`/`version`."""

    def __init__(self, registry_dir: str | Path):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, participant_id: str) -> Path:
        safe = participant_id.replace("/", "_")
        return self.registry_dir / f"participant__{safe}.json"

    def register_participant(self, kind: str, display_name: str) -> Participant:
        pid = identity.new_participant_id()
        p = Participant(participant_id=pid, kind=kind, display_name=display_name)
        self._save(p)
        return p

    def load_participant(self, participant_id: str) -> Participant | None:
        path = self._path(participant_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Participant(
            participant_id=data["participant_id"], kind=data["kind"], display_name=data["display_name"],
            record_refs=[ApplicationRecordRef(**r) for r in data.get("record_refs", [])],
        )

    def _save(self, p: Participant) -> None:
        path = self._path(p.participant_id)
        tmp = path.with_suffix(path.suffix + ".tmp")
        payload = {
            "participant_id": p.participant_id, "kind": p.kind, "display_name": p.display_name,
            "record_refs": [r.__dict__ for r in p.record_refs],
        }
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)

    def add_record_ref(self, participant_id: str, ref: ApplicationRecordRef) -> Participant:
        p = self.load_participant(participant_id)
        if p is None:
            raise KeyError(f"Teilnehmer {participant_id!r} nicht registriert.")
        if not any(r.record_id == ref.record_id for r in p.record_refs):
            p.record_refs.append(ref)
        self._save(p)
        return p
