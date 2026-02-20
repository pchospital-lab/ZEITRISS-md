---
title: "Tiefenanalyse – Restkatalog 2027"
version: 0.2.0
tags: [meta, qa]
---

# Tiefenanalyse – Restkatalog 2027

## Zweck

Dieser Katalog überführt die noch offenen Punkte aus
`uploads/tiefenanalyse-regelwerk-und-onboarding.md` in eine operative QA-Form,
damit Upload-Artefakte keine aktive To-do-Liste mehr sind.

## Quelle

- Upload-Artefakt: `uploads/tiefenanalyse-regelwerk-und-onboarding.md`
- Kanonischer Arbeitsstand:
  - `internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md`
  - `internal/qa/logs/2025-beta-qa-log.md`

## Offene Maßnahmen (ab 2027-03-13)

1. **Single-Source-of-Truth-Pass (Restpunkte)**
   - Ziel: Verbleibende Doppelbeschreibungen für Rift-Risiko/Belohnung und
     optionale Module auflösen.
   - Artefakte: README, Spieler-Handbuch, Kampagnen-/Economy-Module.
   - Status: _offen_

2. **KI-First-Onboardingpfad finalisieren**
   - Ziel: Eine durchgehende Einstiegsstrecke (Quickstart → Session-Ablauf →
     Toolkit-Nutzung) für KI-geleitetes Spiel explizit und konsistent machen.
   - Artefakte: README, `docs/setup-guide.md`,
     `systems/toolkit-gpt-spielleiter.md`.
   - Status: _offen_

3. **Economy-/Scaling-Sicherungen als QA-Checkliste bündeln**
   - Ziel: Risiko von Drift zwischen Regeltext und Runtime-Parametern senken
     (CU, Seed-Multiplikatoren, Gate-/Foreshadow-Regeln).
   - Artefakte: QA-Plan, QA-Audit, gezielte Testfälle in `tools/`.
   - Status: _offen_

4. **Stil- und Sprachkonsistenz (Feinschliff)**
   - Ziel: Vereinheitlichung von Begriffswahl und Tonlage in
     spielerorientierten Kernmodulen.
   - Artefakte: README, `core/spieler-handbuch.md`, `gameplay/*`.
   - Status: _offen_

## Pflegehinweis

- Fortschritt wird zuerst in `internal/qa/logs/2025-beta-qa-log.md`
  dokumentiert.
- Beim Abschluss einzelner Punkte folgt der Statusabgleich im
  `ZEITRISS-qa-fahrplan-2025.md`.
