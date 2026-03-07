---
title: "QA-Log – Issue-Pack Durchlauf 19"
date: 2026-03-07
scope: "Korrektur nach Feedback: Core stabil halten, Rift-Casefiles schärfen"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Maintainer-Feedback auf Durchlauf 18: kein 3-Ebenen-Modell; Core nicht
  umlenken; Rift als eigenständige mystische Casefile-Operationen schärfen.

## Umsetzung in diesem Durchlauf

1. **Roll-back Ton-Bibel-Ebenenmodell**
   - `core/spieler-handbuch.md`: Abschnitt "Ton-Kanon (SSOT)" (Core/Rift/Mythic)
     entfernt.
   - `gameplay/kampagnenuebersicht.md`: Abschnitt "Ton-Bibel (Core/Rift/Mythic)"
     entfernt; Intro wieder auf bisherigen Wortlaut zurückgeführt.
   - `gameplay/kreative-generatoren-missionen.md`: Block "Ton-Gewichtung
     (verbindlich)" entfernt.

2. **Rift-Identität präzisiert (ohne Core-Flow-Änderung)**
   - `core/spieler-handbuch.md`: Rift-Ops explizit als eigenständige Fallfilme
     verankert, ohne Pflichtbezug zu laufender Core-Mission/Episode/Arc.
   - `gameplay/kreative-generatoren-missionen.md`: Rift-Casefiles als
     abgeschlossene Sonderfälle dokumentiert.

3. **Kampf-/PvP-Leitplanke ergänzt**
   - `core/spieler-handbuch.md`: neuer Block "Einsatzgewalt & Endzustände
     (Filmstandard)" ergänzt (harte Ausschaltung in Core, dramatische
     Todesentscheidungen nur in Schlüsselmomenten, Rift-Kreaturen dürfen
     getötet werden, PvP/Arena nicht-tödlich).
   - `gameplay/kampagnenuebersicht.md`: Arena-Policy um nicht-tödliche
     PvP-Auflösung ergänzt.

4. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 19 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 19 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
