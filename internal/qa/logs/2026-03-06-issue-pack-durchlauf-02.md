---
title: "QA-Log – Issue-Pack Durchlauf 02"
version: 0.1.0
tags: [qa, log]
---

# QA-Log – Issue-Pack Durchlauf 02

## Kontext
- Input: `uploads/ZEITRISS_codex_issue_pack.md`
- Fokus: Issue 4 (Px/Arena entkoppeln).

## Umgesetzter Scope

1. **Arena-Belohnung ohne Px in der Kampagnenstruktur verankert**
   - Der Arena-Belohnungsabschnitt nennt nun explizit nur CU/Ruf/Training.
   - Die frühere +1-Px-Regel wurde entfernt.
   - Das Pseudocode-Beispiel schreibt keinen Px-Wert mehr.

2. **Cross-Mode-Matrix im Save-Modul angeglichen**
   - Zeile `PvP → zurück` beschreibt nur Arena-Rewards ohne Px.
   - `campaign.px` bleibt beim Arena-Exit unverändert.

## QA-Checks
- Pflichtcheck: `bash scripts/smoke.sh`.

## Offene Restpunkte (nächster Durchlauf)
1. Save-/Wallet-SSOT durchziehen (`characters[]`, `economy.hq_pool`, `arc`) in
   `speicher-fortsetzung`, `sl-referenz`, `cu-waehrungssystem`, `kampagnenstruktur`.
2. Drift-Guards in `tools/lint_runtime.py` für Legacy-Tokens ergänzen.

## Status
- Durchlauf 02: **abgeschlossen**.
