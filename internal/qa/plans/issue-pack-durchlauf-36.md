---
title: "Issue-Pack Fahrplan – Durchlauf 36"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 36

Quelle: Fortsetzung ZR-016 mit Fokus auf Issue 1 (Save-Schema v7 als einzige
Runtime-Wahrheit) und dem Maintainer-Feedback zur HQ-Save-Struktur.

## Ziel

Den HQ-Deepsave als **spielrelevanten Charakterbogen** schärfen: so wenig wie
möglich, so viel wie nötig — mit klarer Trennung zwischen aktivem
Einsatz-Snapshot (`character`) und persistenter Roster-Quelle (`characters[]`).

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`
- QA-Nachführung: Log + Known-Issues-Update

## Nicht im Scope

- Umbau der Runtime-Import-/Save-Engine in `runtime.js`.
- Umbenennung historischer Artefakte (`masterprompt_v6.md`).
- Neue Systemregeln außerhalb des Save-/Merge-Contracts.

## Exit-Kriterium für Durchlauf 36

- Der Abschnitt „Voller HQ-Deepsave (Solo/Gruppe)“ nutzt ein konsistentes
  v7-Bild, das mit dem kanonischen Exportformat kompatibel ist.
- Das Beispiel trennt klar:
  - `character` = aktiver Snapshot für den laufenden Einstieg,
  - `characters[]` = vollständiger persistenter Charakterbogen für Solo/Koop,
    Split/Merge und Langzeitfortschritt.
- Keine aktiven Legacy-Felder oder Compliance-Reste im HQ-Deepsave-Block.
- `bash scripts/smoke.sh` läuft vollständig grün.
