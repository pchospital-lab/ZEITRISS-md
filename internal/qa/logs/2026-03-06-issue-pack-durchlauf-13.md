---
title: "QA-Log – Issue-Pack Durchlauf 13"
date: 2026-03-06
scope: "Issue 10: Chronopolis-Instanzlogik und HQ-Persistenz klarziehen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Externer Pack `uploads/ZEITRISS_codex_issue_pack.md`, Issue 10
  (Chronopolis ontologisch/persistenzseitig schärfen).

## Umsetzung in diesem Durchlauf

1. **Chronopolis-Instanzlogik in der Kampagnenübersicht präzisiert**
   - Neuer SSOT-Abschnitt definiert, was instanzlokal in `CITY` verbleibt
     (Kampfzustände, lokale Ereignisse, Händlerrotationen, Gerüchte).
   - Persistenzpfad explizit auf lebenden Rücktransfer + Debrief im HQ
     festgelegt.

2. **HQ-Kernprozesse klar abgegrenzt**
   - Shop-Freischaltungen, Klinik/Heilung, Lizenzfortschritt und Speichern
     als HQ-exklusiv benannt.
   - Damit bleibt Chronopolis als instanzierte Gefahrenzone konsistent, ohne
     HQ-Funktionen semantisch zu vermischen.

3. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 13 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 13 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
