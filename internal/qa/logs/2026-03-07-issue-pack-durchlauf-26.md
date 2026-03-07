---
title: "QA-Log – Issue-Pack Durchlauf 26"
date: 2026-03-07
scope: "Save-v7-Kurzschema festziehen und Drift-Guard ergänzen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- ZR-016 (externer Codex-Issue-Pack), Schwerpunkt Save-Schema-SSOT.
- Restdrift im Runtime-Save-Modul: v7-Überschrift bei zugleich v6-Feldern im
  Kurzschema.

## Umsetzung in diesem Durchlauf

1. **Save-Kurzschema auf v7 gezogen (`systems/gameflow/speicher-fortsetzung.md`)**
   - Abschnitt "Kanonisches DeepSave-Schema (Kurzfassung, v7)" ersetzt.
   - Modell auf `v: 7`, `characters[]`, `wallet`, `economy.hq_pool`, `arc`
     konsolidiert.
   - Begleittext auf "Legacy-Importpfade" umgestellt, um Legacy-Felder als
     Import-Bridge statt Runtime-Standard zu markieren.

2. **Lint-Guard ergänzt (`tools/lint_runtime.py`)**
   - Neuer Check `check_save_v7_short_schema_block()` prüft den v7-Kurzschema-
     Block auf Zielpfade.
   - Derselbe Check schlägt fehl, wenn Legacy-Strukturen im v7-Kurzschema
     auftauchen (`save_version`, `character`, `party`, `team`, `cu`,
     `wallets`, `arc_dashboard`).
   - Bestehende Save-Modul-Prüfung von `save_version` auf `v: 7` als
     Zielversion angehoben.

3. **QA-Nachführung**
   - Neuer Fahrplan/Log für Durchlauf 26 angelegt.
   - `internal/qa/process/known-issues.md` um Durchlauf 26 ergänzt.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
