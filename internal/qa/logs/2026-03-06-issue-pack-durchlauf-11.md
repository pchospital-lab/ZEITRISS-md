---
title: "QA-Log – Issue-Pack Durchlauf 11"
date: 2026-03-06
scope: "Psi-Rahmen für KI-SL: Zeitreisenden-Fokus + Epochen-Ausnahmen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Maintainer-Feedback: Psi soll von der KI-SL genau als beabsichtigt gelesen
  werden – primär bei Chrononauten und zentralen Gegnerfraktionen, mit
  seltenen Epochen-Ausnahmen (kulturell anders benannt).

## Umsetzung in diesem Durchlauf

1. **SSOT-Schärfung im Psi-Modul**
   - `systems/kp-kraefte-psi.md` präzisiert den Rahmen:
     - Psi als Weltstandard im Einsatzraum,
     - primärer Trägerkreis = Zeitreisende/Chrononauten + Hauptgegner,
     - seltene Epochen-Ausnahmen als gleiche Mechanik mit anderer
       kultureller Deutung.

2. **Kampagnenübersicht synchronisiert**
   - `gameplay/kampagnenuebersicht.md` nutzt denselben Fokus und nennt
     explizit seltene Epochenfiguren als Ausnahmefall.

3. **QA-Nachführung**
   - Durchlauf 11 als Plan/Log ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Verweise auf
     Durchlauf 11 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
