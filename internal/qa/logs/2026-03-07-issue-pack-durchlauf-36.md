---
title: "QA-Log – Issue-Pack Durchlauf 36"
date: 2026-03-07
scope: "HQ-Deepsave als konsistenter Charakterbogen (v7)"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), Maintainer-Feedback:
  Save-Struktur wirkte uneinheitlich und zu runtime-lastig; unklar, was im
  HQ-Save wirklich spielrelevant persistiert werden muss.

## Umsetzung in diesem Durchlauf

1. **HQ-Deepsave-Beispiel geschärft (`systems/gameflow/speicher-fortsetzung.md`)**
   - Den Block auf ein konsistentes v7-Bild überführt: klarer
     Characterbogen-Fokus statt gemischter Runtime-/Legacy-Signale.
   - `character` als **aktiven Snapshot** belassen (für den direkten
     Wiedereinstieg nach `!load`).
   - `characters[]` als **einzige persistente Roster-Quelle** für Solo/Koop,
     Split/Merge und Langzeitprogression ausgestaltet (Wallet, History, Carry,
     Quartier-Stash, Fahrzeuge, Equipment im `{name,type,tier}`-Format).
   - Legacy-/Compliance-Reste bleiben entfernt.

2. **Pflichtfeld-Text präzisiert (`systems/gameflow/speicher-fortsetzung.md`)**
   - Die Pflichtfeldliste trennt jetzt explizit Snapshot (`character`) und
     persistenten Roster-Charakterbogen (`characters[]`).
   - Solo-Regel `character.id = characters[0].id` und Gruppenregel
     `characters[]` als Roster-SSOT klar benannt.

3. **Prozessnachführung (`internal/qa/process/known-issues.md`)**
   - ZR-016 um Durchlauf 36 (Plan + QA-Log) erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
