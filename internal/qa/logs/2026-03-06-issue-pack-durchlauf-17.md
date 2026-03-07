---
title: "QA-Log – Issue-Pack Durchlauf 17"
date: 2026-03-06
scope: "Item-Regeln nach Feedback: generativ offen, Save strikt"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Maintainer-Feedback auf Durchlauf 16: ZEITRISS soll als generatives
  Pen-&-Paper-System offen bleiben (freie Item-Anfragen/Angebote), ohne starre
  Katalogwirkung.

## Umsetzung in diesem Durchlauf

1. **Ausrüstungsmodul korrigiert (`characters/ausruestung-cyberware.md`)**
   - Registry-/ID-Fokus entfernt.
   - Stattdessen generative Item-Leitplanken verankert:
     freie, plausible Erstellung + Lizenz-/Balance-Leitlinien.
   - Save-Kompatibilität explizit auf `equipment[{name,type,tier}]` fixiert.

2. **Masterprompt präzisiert (`meta/masterprompt_v6.md`)**
   - Equipment-Regel wieder auf das kanonische Minimalformat zurückgeführt.
   - Ergänzt, dass Namen frei/generativ sein dürfen, solange Wirkung/Tier
     plausibel bleiben.

3. **SL-Referenz rückgeführt (`core/sl-referenz.md`)**
   - Save-v7-Kompaktschema wieder konsistent auf
     `equipment:[{name,type,tier}]` gesetzt.

4. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 17 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 17 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
