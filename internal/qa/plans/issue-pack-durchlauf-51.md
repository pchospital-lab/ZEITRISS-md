---
title: "Issue-Pack Fahrplan – Durchlauf 51"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 51

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 9 + Issue 10).

## Ziel

1. Die High-Level-Ökonomie-Bänder in allen relevanten Quellen auf eine
   eindeutige Referenz bringen (`120/512/900+`).
2. Eine dokumentierte v7-Fixture-Strecke für 5er-Highlevel- und
   Split/Merge-Pfade ergänzen, inklusive Refusal-Fall für parallele
   Core-Missions-Branches ohne Branch-Protokoll.

## Scope dieses Durchlaufs

- `systems/currency/cu-waehrungssystem.md`
  - High-Level-Band-Tabelle von `100/400/1000` auf `120/512/900+` umstellen.
- `core/sl-referenz.md`
  - Economy-Verweistext auf dieselben Bänder synchronisieren.
- `internal/qa/fixtures/*.json`
  - Neue v7-Fixtures für 5er-HQ-Highlevel, Split 3/2 + Merge,
    Rift+PvP-Merge, Chronopolis-Roundtrip, Abort/Resume-Weiterlauf,
    chat-nativen JSON-Load.
  - Refusal-Fixture für nicht-kanonische parallele Core-Branches.
- `tools/test_v7_issue_pack.js`
  - Fixture-Checks für die oben genannten Golden Paths.
- `scripts/smoke.sh`
  - Neuen Fixture-Check in den Pflicht-Smoke aufnehmen.
- `internal/qa/process/known-issues.md`
  - Fortschritt für ZR-017 auf Durchlauf 51 erweitern.

## Exit-Kriterium

- High-Level-Bänder sind in Save-Doku, SL-Referenz und Währungsmodul
  konsistent (`120/512/900+`).
- v7-Fixtures + Testskript laufen im Pflicht-Smoke grün.
- Refusal-Fall für parallele Core-Branches ist als Testartefakt hinterlegt.
