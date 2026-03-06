---
title: "QA-Log – Issue-Pack Durchlauf 14"
date: 2026-03-06
scope: "Issue 10: ITI-Überbegriff vs. HQ-Kern und Chronopolis-Ring konsolidieren"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Externer Pack `uploads/ZEITRISS_codex_issue_pack.md`, Issue 10
  (Chronopolis-Regeln/Instanzlogik präzisieren).
- Maintainer-Feedback nach Durchlauf 13:
  ITI als Gesamtanlage klarer fassen (HQ-Kern + Chronopolis-Ring),
  ohne Save-/Service-Regeln zu verwässern.

## Umsetzung in diesem Durchlauf

1. **Masterprompt-SSOT geschärft**
   - ITI explizit als Gesamtanlage definiert.
   - Klare Trennung ergänzt: HQ-Kern (safe + Save/Services) vs. Chronopolis
     (`CITY`, Gefahrenzone, kein Save).

2. **Spieler- und Kampagnenmodule angeglichen**
   - `core/spieler-handbuch.md`: HQ-Abschnitt als ITI-Überbegriff + HQ-Kern
     formuliert; Chronopolis-Flavor als variabler Episoden-Fehlschlagraum
     präzisiert.
   - `gameplay/kampagnenuebersicht.md`: ITI-Überbegriff und SSOT-Block zur
     Instanz-/Persistenzlogik konsistent auf HQ-Kern vs. `CITY` gezogen.

3. **SL-/Save-Referenzen nachgezogen**
   - `core/sl-referenz.md`: ITI-Überbegriff + HQ-Definition für Save/Service
     konkretisiert.
   - `systems/gameflow/speicher-fortsetzung.md`: SaveGuard-Definition sprachlich
     auf ITI-Überbegriff bei gleichzeitigem HQ-Kern-Scope geschärft.

4. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 14 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 14 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
