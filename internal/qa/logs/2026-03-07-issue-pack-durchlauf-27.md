---
title: "QA-Log – Issue-Pack Durchlauf 27"
date: 2026-03-07
scope: "Save-SSOT-Wording: einziges Exportformat klarstellen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- ZR-016 (externer Codex-Issue-Pack), Folgearbeit nach Maintainer-Feedback zu
  verwirrender Bezeichnung "Kurzfassung" im kanonischen Save-Block.

## Umsetzung in diesem Durchlauf

1. **Save-Abschnitt sprachlich geschärft (`systems/gameflow/speicher-fortsetzung.md`)**
   - Überschrift von "Kanonisches DeepSave-Schema (Kurzfassung, v7)" auf
     "Kanonisches Save-Exportformat (v7, einziges Format)" geändert.
   - Direkt unter der Überschrift explizit klargestellt, dass es nur ein
     kanonisches Exportformat für neue Saves gibt.
   - Legacy-Hinweise ergänzt: v6-Beispiele dienen nur der Migrationserklärung,
     nicht als alternatives Speicherformat.

2. **Lint-Nachzug (`tools/lint_runtime.py`)**
   - Check auf neue Überschrift aktualisiert.
   - Check-Name und Meldungen auf "Exportformat" umgestellt
     (`check_save_v7_canonical_export_block`).

3. **QA-Nachführung**
   - Neuer Fahrplan/Log für Durchlauf 27 angelegt.
   - `internal/qa/process/known-issues.md` um Durchlauf 27 ergänzt.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
