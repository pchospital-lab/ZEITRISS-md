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


def _participant_struct_valid(data: dict) -> bool:
    """Q08 (REVIEW.md R04, 05.10.2026, UX21): der vorhandene `isinstance(
    dict)`-Schutz (G05/P08, s. unten) faengt nur Nicht-Objekt-JSON (`[]`/
    `null`/Zahl/String) ab -- ein strukturell unvollstaendiges OBJEKT
    (z.B. passender `display_name`, aber FEHLENDES `participant_id`)
    bleibt `isinstance(dict)`-True und wirft weiterhin `KeyError` beim
    direkten `data["participant_id"]`-Zugriff. Prueft genau die fuer
    `Participant` zwingend noetigen Felder (dieselben drei Pflichtfelder,
    die `_save` immer schreibt) -- rein lesend, keine Reparatur/
    Ueberschreibung der defekten Datei."""
    return all(isinstance(data.get(f), str) and data.get(f) for f in ("participant_id", "kind", "display_name"))


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

    def find_by_display_name(self, display_name: str) -> list[Participant]:
        """R6 (ZEITRISS Terminal UX-1, Korrekturzyklus 1, T-Befund 3,
        UX02/UX07) -- bedingter Core-Edit, s. `worker/SCOPE-MAP-2.md`:
        REINE Lesefunktion (kein Write, keine Autoritaets-/Ownership-
        Aenderung) -- scannt die bereits bestehenden Teilnehmerdateien in
        `registry_dir` und liefert ALLE Teilnehmer mit exakt diesem
        `display_name` (case-insensitiv getrimmt). Ohne diese Lesefunktion
        hatte `ui/tui.py:_cmd_register_new_person` keine Moeglichkeit,
        eine Namensgleichheit zu erkennen -- jede erneute Registrierung
        mit demselben Anzeigenamen (z.B. nach Ctrl-C + Neustart) erzeugte
        dadurch stillschweigend eine zweite, komplett neue ID (02 §D.1:
        'Altbestand nicht neu anlegen', 'keine still neue Anlage')."""
        needle = display_name.strip().lower()
        matches: list[Participant] = []
        for path in sorted(self.registry_dir.glob("participant__*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            # G05/P08 (ZEITRISS Terminal UX-1, Korrekturzyklus 2): ein
            # strukturell gueltiges JSON, das aber kein Objekt ist (z.B. ein
            # defekter/fremder Datensatz mit Inhalt `[]`), darf diesen rein
            # lesenden Scan NICHT mit einem `AttributeError` abbrechen (vorher
            # `data.get(...)` auf einer `list`). Ehrlich als unlesbarer
            # Einzeldatensatz uebersprungen -- wie ein JSON-Parserfehler oben:
            # kein Crash, keine Reparatur/Ueberschreibung, kein stilles neues
            # gleichnamiges Profil.
            if not isinstance(data, dict):
                continue
            if str(data.get("display_name", "")).strip().lower() == needle:
                # Q08: ein Treffer mit passendem `display_name`, aber ohne
                # (oder mit falsch typisiertem) `participant_id`/`kind`,
                # ist kein auflösbarer Teilnehmer -- ehrlich als unlesbaren
                # Einzeldatensatz überspringen (derselbe Vertrag wie der
                # JSON-Parserfehler/Nicht-Objekt-Fall oben), statt mit
                # `KeyError` den GESAMTEN Scan abzubrechen.
                if not _participant_struct_valid(data):
                    continue
                matches.append(Participant(
                    participant_id=data["participant_id"], kind=data["kind"],
                    display_name=data["display_name"],
                    record_refs=[ApplicationRecordRef(**r) for r in data.get("record_refs", [])],
                ))
        return matches

    def load_participant(self, participant_id: str) -> Participant | None:
        path = self._path(participant_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        # Q08: derselbe Strukturschutz wie `find_by_display_name` -- eine
        # einzelne, ueber ihre eigene ID direkt angesprochene Datei ohne
        # Alternative wird kontrolliert gemeldet (klare Ausnahme mit
        # Ursache) statt mit einem rohen `KeyError` auf ein fehlendes Feld.
        # Kein automatischer Reparatur-/Ueberschreibwrite.
        if not isinstance(data, dict) or not _participant_struct_valid(data):
            raise ValueError(
                f"Teilnehmerdatensatz {participant_id!r} strukturell unvollstaendig/ungueltig "
                "(fehlende Pflichtfelder participant_id/kind/display_name) -- lesend gemeldet, "
                "kein automatischer Reparaturwrite."
            )
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
