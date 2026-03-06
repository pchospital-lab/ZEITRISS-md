---
title: "QA-Log – Issue-Pack Durchlauf 10"
date: 2026-03-06
scope: "Korrektur Psi-Standard (Issue 9)"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Maintainer-Feedback auf Durchlauf 09: Psi soll im Spiel **Standard** sein,
  aktive Nutzung aber charakterabhängig bleiben; Discoverability im laufenden
  Spiel ist ausdrücklich gewünscht.

## Umsetzung in diesem Durchlauf

1. **SSOT-Korrektur im Psi-Modul**
   - `systems/kp-kraefte-psi.md` benennt Psi jetzt wieder als
     Weltstandard.
   - `has_psi` bleibt als Charakter-Gating für aktive Psi-Nutzung gesetzt.
   - Nicht-psionische Lösungswege für Schlüsselszenen bleiben als
     Spielfluss-Sicherheitsregel bestehen.

2. **Kampagnenübersicht nachgezogen**
   - `gameplay/kampagnenuebersicht.md` beschreibt Psionik als festen
     Weltbestandteil (NPCs/Gegner/Fraktionen), kombiniert mit
     charakterabhängiger Freischaltung/Nutzung.
   - Discoverability im Spielverlauf (späteres Erlernen) wurde explizit
     festgehalten.

3. **Bestehende gute Änderung beibehalten**
   - `characters/ausruestung-cyberware.md` bleibt beim neutralen
     Anomalie-Puffer.

4. **QA-Nachführung**
   - Durchlauf 10 in Fahrplan/Log ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Verweise auf
     Durchlauf 10 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
