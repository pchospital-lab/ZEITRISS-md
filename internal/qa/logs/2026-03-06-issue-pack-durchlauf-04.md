---
title: "QA-Log – Issue-Pack Durchlauf 04"
version: 0.1.0
tags: [qa, log]
---

# QA-Log – Issue-Pack Durchlauf 04

## Kontext
- Input: `uploads/ZEITRISS_codex_issue_pack.md`
- Fokus: Issue 1/2 (Save/Wallet-SSOT, Teil 2) + Issue 6 (Drift-Tests, Teil 1).

## Umgesetzter Scope

1. **Save-v7-Block in der SL-Referenz konsolidiert**
   - Der Abschnitt „Save v7 – Pflichtfelder & Kompatibilität“ wurde auf das
     v7-Zielmodell ausgerichtet: `v: 7`, `characters[].wallet`,
     `economy.hq_pool`, `arc.timeline`.
   - Legacy-Elemente (`save_version: 6`, `party.characters[]`,
     `team.members[]`, `economy.cu`) werden im Abschnitt nur noch als
     Import-/Migrationspfad beschrieben.

2. **Drift-Guard im Runtime-Lint ergänzt**
   - `tools/lint_runtime.py` prüft jetzt den Save-v7-Abschnitt der
     `core/sl-referenz.md` gezielt.
   - Der Check erzwingt Zielpfade und markiert ausgewählte
     Legacy-Standardformulierungen im Save-v7-Abschnitt als CI-Fehler.

## QA-Checks
- Pflichtcheck: `bash scripts/smoke.sh`.

## Offene Restpunkte (nächster Durchlauf)
1. Save-SSOT in `meta/masterprompt_v6.md` final gegen die gleiche Feldsprache
   gegenlesen (v7-Export vs. Legacy-Hinweise).
2. Optional: Drift-Guards auf weitere Runtime-Abschnitte erweitern
   (z. B. `meta/masterprompt_v6.md`, `systems/gameflow/speicher-fortsetzung.md`).

## Status
- Durchlauf 04: **abgeschlossen**.
