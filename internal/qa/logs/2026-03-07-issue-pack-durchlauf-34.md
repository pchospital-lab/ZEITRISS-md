---
title: "QA-Log – Issue-Pack Durchlauf 34"
date: 2026-03-07
scope: "Save-v7-SSOT ohne eingebettete v6-JSON-Beispiele + Drift-Guard"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), Restpunkt aus Issue 1/6:
  Im geladenen Save-Modul war weiterhin ein großer eingebetteter v6-JSON-Block
  enthalten, der trotz Migrationshinweis SSOT-Kontextbudget belegt und
  Schema-Drift signalisiert.

## Umsetzung in diesem Durchlauf

1. **Save-Modul bereinigt (`systems/gameflow/speicher-fortsetzung.md`)**
   - Den eingebetteten v6-JSON-Beispielblock (`save_version: 6`, `economy.cu`,
     `arc_dashboard`) entfernt.
   - Stattdessen einen kompakten Migrationshinweis eingefügt: historische
     v6-Beispiele liegen in internen/archivierten Dev-Artefakten; im geladenen
     Runtime-Kanon gilt ausschließlich das v7-Exportformat.

2. **Drift-Guard ergänzt (`tools/lint_runtime.py`)**
   - Neue Prüfung `check_no_embedded_v6_json_examples_in_save_module()` hinzugefügt.
   - Der Guard prüft `systems/gameflow/speicher-fortsetzung.md` auf eingebettete
     v6-JSON-Signaturen (`"save_version": 6`, `"arc_dashboard": {`,
     `"economy": { "cu": ... }`) und lässt CI bei Rückfällen fehlschlagen.
   - Check ist in `main()` eingebunden und läuft automatisch im Pflicht-Smoke.

3. **Prozessnachführung (`internal/qa/process/known-issues.md`)**
   - ZR-016 um Durchlauf 34 (Plan + QA-Log) erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
