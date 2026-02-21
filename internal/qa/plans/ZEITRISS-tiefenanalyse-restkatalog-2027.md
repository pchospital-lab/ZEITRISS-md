---
title: "Tiefenanalyse – Restkatalog 2027"
version: 0.3.3
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
   - Artefakte: `core/sl-referenz.md`, `core/spieler-handbuch.md`, README,
     Kampagnen-/Economy-Module.
   - Status: _in Umsetzung_ (modulsequenzieller Durchlaufplan angelegt,
     2027-03-15)

### Durchlaufplan 2027-03-15 (für die nächsten QA-Sessions bindend)

**Leitprinzip:** `core/sl-referenz.md` und `core/spieler-handbuch.md` sind die
kanonischen Quickformate. README und spätere Regelmodule spiegeln diese
Definitionen, nicht umgekehrt.

1. **Kanon-Extraktion (Session 1)**
   - Quelle: `core/sl-referenz.md`, `core/spieler-handbuch.md`.
   - Ergebnis: Mini-Glossar für Rift-Risiko, Belohnung, optionale Module,
     Muss/Soll/Kann-Semantik.
2. **Anker-Sync README/Core (Session 1–2)**
   - Ziel: README-Abschnitte auf den Kanon aus den Core-Quickformaten
     harmonisieren.
   - Gate: keine abweichende Begriffs- oder Prioritätslogik zwischen README
     und den beiden Core-Dateien.
3. **Gameplay-Pass (Session 2–3)**
   - Zielmodule: `gameplay/kampagnenuebersicht.md`,
     `gameplay/kampagnenstruktur.md`.
   - Fokus: Rift-Risiko/Belohnung, optionale Module, Gate-Wording.
4. **Systems-Pass (Session 3–4)**
   - Zielmodule: `systems/currency/cu-waehrungssystem.md`,
     `systems/gameflow/speicher-fortsetzung.md`,
     `systems/toolkit-gpt-spielleiter.md`.
   - Fokus: Economy-/Scaling-Aussagen und Pflicht-/Optional-Markierung gegen
     Core-Kanon prüfen.
5. **Konfliktprüfung & Closure (Session 4)**
   - Suchanker: `optional`, `Pflicht`, `empfohlen`, `Rift`, `Belohnung`, `CU`,
     `Scaling`.
   - Abschluss: Statuswechsel auf _abgeschlossen_ erst nach Fahrplan-/Audit- und
     QA-Log-Synchronisierung inkl. Pflichttestpaket.

2. **KI-First-Onboardingpfad finalisieren**
   - Ziel: Eine durchgehende Einstiegsstrecke (Quickstart → Session-Ablauf →
     Sessionstart) für KI-geleitetes Spiel explizit und konsistent machen.
   - Artefakte: README, `docs/setup-guide.md`.
   - Status: _abgeschlossen_ (Onboardingroute als Referenzfluss in README/
     Setup verankert, 2027-03-14; Toolkit bleibt bewusst onboardingfrei)

3. **Economy-/Scaling-Sicherungen als QA-Checkliste bündeln**
   - Ziel: Risiko von Drift zwischen Regeltext und Runtime-Parametern senken
     (CU, Seed-Multiplikatoren, Gate-/Foreshadow-Regeln).
   - Artefakte: QA-Plan, QA-Audit, gezielte Testfälle in `tools/`.
   - Status: _in Umsetzung_ (Checkliste im QA-Plan/Audit ergänzt, 2027-03-14)

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
