---
title: "QA-Log – Issue-Pack Durchlauf 09"
date: 2026-03-06
scope: "Psi-Gating: Baseline vs. Aktivmodus"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Externer Pack `uploads/ZEITRISS_codex_issue_pack.md`, Issue 9
  ("Psi-Gating bereinigen: optionales Modul oder baseline Weltannahme").

## Umsetzung in diesem Durchlauf

1. **Psi-Modul als SSOT geschärft**
   - In `systems/kp-kraefte-psi.md` wurde ein klarer Baseline-Schalter ergänzt:
     `has_psi=false` = Standardmodus, `has_psi=true` = Psi-Aktiv-Modus.
   - Zusätzlich festgezogen: keine Plot-Hürde darf ausschließlich über Psi
     lösbar sein.

2. **Ausrüstungsmodul entkoppelt**
   - `characters/ausruestung-cyberware.md` nutzt im Kernanzug-Abschnitt jetzt
     "Anomalie-Puffer" statt impliziter Dauer-Psi-Infrastruktur.
   - Mechanische Psi-Boni bleiben erhalten, aber explizit nur für
     `has_psi=true`.

3. **Kampagnenübersicht kalibriert**
   - `gameplay/kampagnenuebersicht.md` beschreibt Psionik jetzt als optionale,
     seltene Zusatzebene statt allgemeiner Weltgrundannahme.
   - Terminologie-Drift bereinigt: "Spielleiter (MyGPT)" →
     "Spielleitung (KI-SL)".

4. **QA-Nachführung**
   - Durchlauf 09 in Fahrplan/Log ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Verweise auf
     Durchlauf 09 erweitert.

## Offene Restpunkte für Folge-Durchlauf
- Modul 3B (N-/T-Stufen) auf Psi-Tonalität gegenprüfen.
- Generatoren/Encounter-Texte auf implizite Psi-Alltäglichkeit prüfen.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
