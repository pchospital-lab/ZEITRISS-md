---
title: "QA-Log – Issue-Pack Durchlauf 35"
date: 2026-03-07
scope: "HQ-Deepsave v7-SSOT + dedizierter Drift-Guard"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), Restpunkt aus Issue 1/6:
  Der Abschnitt „Voller HQ-Deepsave“ im Save-Modul enthielt weiter aktive
  Legacy-Strukturen (`save_version`, `team`, `party`, `economy.cu`,
  `economy.wallets`, `arc_dashboard`) und einen alten Compliance-Flag.

## Umsetzung in diesem Durchlauf

1. **HQ-Deepsave auf v7-SSOT gezogen (`systems/gameflow/speicher-fortsetzung.md`)**
   - JSON-Beispiel auf `"v": 7` umgestellt.
   - Aktive Legacy-Strukturen entfernt und durch v7-Kernpfade ersetzt:
     `characters[]` mit `wallet`, `economy.hq_pool` und `arc`.
   - Alten Compliance-Rest (`compliance_shown_today`) aus dem Beispielblock
     entfernt.

2. **Neuer Guard für den HQ-Deepsave-Block (`tools/lint_runtime.py`)**
   - Funktion `check_full_hq_deepsave_block_uses_v7_ssot()` ergänzt.
   - Der Check extrahiert den JSON-Block aus dem Abschnitt
     „Voller HQ-Deepsave (Solo/Gruppe)“ und validiert:
     - erforderliche v7-Signaturen (`v`, `characters[]`, `wallet`, `hq_pool`,
       `arc`),
     - Verbot von Legacy-/Rückfallmustern (`save_version`, `party`, `team`,
       `cu`, `wallets`, `arc_dashboard`, `compliance_shown_today`).
   - Check in `main()` eingebunden, damit er im Pflicht-Smoke automatisch läuft.

3. **Prozessnachführung (`internal/qa/process/known-issues.md`)**
   - ZR-016 um Durchlauf 35 (Plan + QA-Log) erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
