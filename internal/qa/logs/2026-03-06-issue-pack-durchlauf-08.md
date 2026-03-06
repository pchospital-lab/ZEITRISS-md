---
title: "QA-Log – Issue-Pack Durchlauf 08"
date: 2026-03-06
scope: "Rollback Durchlauf 07 / Pacing-Änderung verworfen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Maintainer-Feedback auf Durchlauf 07: aktueller Spiel-Flow soll unverändert bleiben,
  keine zweite Pacing-Logik neben den etablierten Modi.

## Entscheidung
- Der in Durchlauf 07 eingeführte `output_pace`-Preset-Block
  (`compact|normal|cinematic`) wird **verworfen**.
- Begründung: Risiko eines grundlegenden Flow-Drifts trotz gut eingespieltem
  Missions-/Kodex-Verhalten.

## Umgesetzter Scope

1. **Runtime-Rollback**
   - `meta/masterprompt_v6.md` wieder auf den vorherigen Ausgabevertrag
     (mind. 3 Absätze, Konflikt 4-6) zurückgeführt.
   - Save-Regel zu erlaubten `ui.output_pace`-Werten entfernt.
   - `core/spieler-handbuch.md` um die Durchlauf-07-Pacing-Ergänzungen bereinigt.

2. **QA-Nachführung**
   - Durchlauf 08 als Rückbau-/Verwerfungsdurchlauf dokumentiert.
   - ZR-016 um Durchlauf 08 (Plan + Log) erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
