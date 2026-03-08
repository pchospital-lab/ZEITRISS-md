---
title: "QA-Log – Issue-Pack Durchlauf 51"
date: 2026-03-08
scope: "Issue 9 + Issue 10: Economy-Bänder und v7-Fixture-Strecke"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 9, Issue 10).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-51.md`.

## Umsetzung in diesem Durchlauf

1. **Economy-Bänder vereinheitlicht**
   - `systems/currency/cu-waehrungssystem.md` nutzt im High-Level-Block jetzt
     durchgehend die Bänder `120/512/900+`.
   - `core/sl-referenz.md` referenziert denselben Band-Standard, statt
     der alten `100/400/1000`-Formulierung.

2. **v7-Fixture-Strecke aufgebaut (Issue 10)**
   - Neue QA-Fixtures angelegt:
     - `internal/qa/fixtures/savegame_v7_5er_hq_highlevel.json`
     - `internal/qa/fixtures/savegame_v7_split_3_2_merge.json`
     - `internal/qa/fixtures/savegame_v7_merge_rift_pvp.json`
     - `internal/qa/fixtures/savegame_v7_chronopolis_roundtrip.json`
     - `internal/qa/fixtures/savegame_v7_abort_resume.json`
     - `internal/qa/fixtures/savegame_v7_chat_load.json`
     - `internal/qa/fixtures/v7_parallel_core_refusal.json`
   - Die Fixtures decken die im Issue-Pack geforderten Pfade inkl.
     Refusal für parallele Core-Branches ab.

3. **Automatisierter Check ergänzt**
   - `tools/test_v7_issue_pack.js` prüft die neuen Fixture-Pfade auf
     v7-Grundstruktur, HQ-Save-Grenzen, Merge-Lineage-Marker und
     OpenWebUI-Load-Hinweis.
   - `scripts/smoke.sh` führt den neuen Check als Pflichtteil aus.

4. **QA-Prozess synchronisiert**
   - `internal/qa/process/known-issues.md` um den Durchlauf-51-Stand ergänzt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- Issue 9 (Economy-Band-Drift) ist auf den relevanten Runtime-Modulen
  geschlossen.
- Issue 10 hat jetzt eine konkrete, automatisiert geprüfte v7-Fixture-Strecke
  für die kritischen 5er-/Split-/Merge-Pfade.
- Offener Rest unter ZR-017: formales Mixed-Split-Protokoll (Rift+PvP+Chronopolis+Abort
  als einheitlicher Präzedenzgraph) bleibt als nächster Ausbaupunkt.
