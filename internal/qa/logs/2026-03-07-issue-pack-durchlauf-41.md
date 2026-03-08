---
title: "QA-Log – Issue-Pack Durchlauf 41"
date: 2026-03-07
scope: "Issue 3 aus v7 Save/Load Pack: kanonischer Split/Merge-Standard und Branch-Grenzen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 3)
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-41.md`

## Umsetzung in diesem Durchlauf

1. **Kanonische Branch-Grenze im Spielpfad geschärft**
   - `README.md`: Multiplayer-Abschnitt klar auf kanonischen Rift-Split nach Episodenende begrenzt;
     Core-Parallel-Branches und Misch-Splits ohne Protokoll als nicht-kanonische Hausregel markiert.

2. **Masterprompt auf denselben Standard gehoben**
   - `meta/masterprompt_v6.md`: Split/Merge nur für Rift nach Episodenende als Standard ergänzt;
     Core-Parallelpfade ohne Branch-Protokoll explizit als nicht-kanonisch gekennzeichnet.

3. **Runtime-/SL-Doku synchronisiert**
   - `systems/gameflow/speicher-fortsetzung.md`: Abschnitt „Team-Split & Team-Merge“ in
     „Kanonischer Split-Standard“ + „Kanonischer Merge (Rift-only)“ umgestellt;
     zusätzlicher Hinweistext für nicht-kanonische Branch-Imports aufgenommen.
   - `core/sl-referenz.md`: Chat-Kurzbefehlsumfeld um klare Kanon-Grenze ergänzt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
