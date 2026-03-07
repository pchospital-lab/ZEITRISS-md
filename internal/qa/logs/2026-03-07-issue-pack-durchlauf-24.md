---
title: "QA-Log – Issue-Pack Durchlauf 24"
date: 2026-03-07
scope: "Save-SSOT/Cross-Mode-Konsolidierung im Save-Modul"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- ZR-016 (externer Codex-Issue-Pack), fortlaufende SSOT-Konsolidierung.
- Sichtbarer Drift im Save-Modul: aktive Beispiel-/Transfertexte nutzten noch
  Legacy-Pfade als impliziten Standard.

## Umsetzung in diesem Durchlauf

1. **Pflichtfeld-/Standardblock auf v7 gezogen (`systems/gameflow/speicher-fortsetzung.md`)**
   - Standardpfade auf `v`, `economy.hq_pool`, `characters[]` und `arc`
     konsolidiert.
   - Import-Aliase (`party.characters[]`, `team.members[]`) klar als
     Legacy-Bridge formuliert, nicht als Exportstandard.

2. **Cross-Mode-Abschnitt präzisiert (`systems/gameflow/speicher-fortsetzung.md`)**
   - Ablauf auf `normalize_roster_to_characters()` + `sync_hq_pool()` und
     Host-Priorität bei `campaign`/`economy.hq_pool` geschärft.
   - Transfermatrix sprachlich auf Wallet-in-`characters[]` und
     HQ-Pool-Verantwortung umgestellt.

3. **Accessibility-Beispiel modernisiert (`systems/gameflow/speicher-fortsetzung.md`)**
   - Beispielsave von Legacy-Layout auf v7-Schema umgestellt (`v: 7`,
     `characters[]`, `economy.hq_pool`, `arc`).
   - UI-Persistenzteil beibehalten, aber an den aktualisierten Save-Körper
     gekoppelt.

4. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 24 hinzugefügt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 24 ergänzt.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
