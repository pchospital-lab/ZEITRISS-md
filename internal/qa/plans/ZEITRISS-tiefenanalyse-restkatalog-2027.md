---
title: "Tiefenanalyse – Restkatalog 2027"
version: 0.3.10
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
   - Status: _abgeschlossen_ (Durchlauf 5 Konfliktprüfung/Closure abgeschlossen,
     2027-03-20)

### Durchlaufplan 2027-03-15 (für die nächsten QA-Sessions bindend)

**Leitprinzip:** `core/sl-referenz.md` und `core/spieler-handbuch.md` sind die
kanonischen Quickformate. README und spätere Regelmodule spiegeln diese
Definitionen, nicht umgekehrt.

1. **Kanon-Extraktion (Session 1)**
   - Quelle: `core/sl-referenz.md`, `core/spieler-handbuch.md`.
   - Ergebnis: Mini-Glossar für Rift-Risiko, Belohnung, optionale Module,
     Muss/Soll/Kann-Semantik.
   - Status: _abgeschlossen_ (Kanon-Mini-Glossar extrahiert, 2027-03-16)
2. **Anker-Sync README/Core (Session 1–2)**
  - Ziel: README-Abschnitte auf den Kanon aus den Core-Quickformaten
    harmonisieren.
  - Gate: keine abweichende Begriffs- oder Prioritätslogik zwischen README
    und den beiden Core-Dateien.
  - Status: _abgeschlossen_ (Belohnungslogik + Optionalitätssemantik im README
    auf den Core-Kanon harmonisiert, 2027-03-17)
3. **Gameplay-Pass (Session 2–3)**
   - Zielmodule: `gameplay/kampagnenuebersicht.md`,
     `gameplay/kampagnenstruktur.md`.
   - Fokus: Rift-Risiko/Belohnung, optionale Module, Gate-Wording.
   - Status: _abgeschlossen_ (Gameplay-Module auf SSOT-Anker harmonisiert,
     2027-03-18; Artefakt-Hausregel entfernt, Boss-only-Drop fixiert)
4. **Systems-Pass (Session 3–4)**
   - Zielmodule: `systems/currency/cu-waehrungssystem.md`,
     `systems/gameflow/speicher-fortsetzung.md`,
     `systems/toolkit-gpt-spielleiter.md`.
   - Fokus: Economy-/Scaling-Aussagen und Pflicht-/Optional-Markierung gegen
     Core-Kanon prüfen.
   - Status: _abgeschlossen_ (Systems-Module mit SSOT-Anker MUSS/SOLL/KANN
     harmonisiert, 2027-03-19)
5. **Konfliktprüfung & Closure (Session 4)**
   - Suchanker: `optional`, `Pflicht`, `empfohlen`, `Rift`, `Belohnung`, `CU`,
     `Scaling`.
   - Status: _abgeschlossen_ (Suchanker-Prüfung durchgeführt; verbliebene
     Startwurf-Referenzen in `core/sl-referenz.md` und
     `systems/toolkit-gpt-spielleiter.md` auf Boss-only harmonisiert,
     2027-03-20).

### Kanon-Mini-Glossar (Ergebnis Session 1 am 2027-03-16)

Extraktionsquelle ist ausschließlich `core/sl-referenz.md` plus
`core/spieler-handbuch.md`. Dieses Glossar dient als verbindlicher Anker für
die nachfolgenden Sync-Pässe (README/Gameplay/Systems).

- **Rift-Risiko:** Rift-Seeds sind Bonus-Missionen mit höherer Gefahrenlage
  (Paramonster, höhere Einsatzlast), aber ohne Änderung am Boss-Timing der
  Core-Episoden.
- **Belohnung (kanonisch):** Px ist ein Belohnungssystem. Bei Px 5 löst
  `ClusterCreate()` 1-2 Rift-Seeds aus; die CU-Formel bleibt in Core und Rift
  identisch (`Basiswert × Ergebnis × Seed-Multi × Hazard-Pay`).
- **Optionale Module:** Optional heißt nur „zusätzlicher Zugriffspfad" (z. B.
  Schnellstart/Film-Modus), nicht „abweichende Grundregel". Kernabläufe
  (Debrief, HQ, SaveGuard, Boss-Rhythmus) bleiben unberührt.
- **Muss/Soll/Kann-Semantik (für Folgemodule):**
  - **MUSS:** invariant und bindend (Boss-Timing, SaveGuard HQ-only,
    Px-5-ClusterCreate, einheitliche CU-Formel).
  - **SOLL:** empfohlener Standardpfad ohne harte Sperre (klassischer Start,
    neuer Chat pro Mission).
  - **KANN:** optionale Komfort-/Darstellungsvariante ohne Regeländerung
    (Film-Modus, zusätzliche Metadatenfelder, manuelle statt Script-Setup).

### Ergebnis Session 4 (Konfliktprüfung & Closure am 2027-03-20)

### Nachtrag 2027-03-20b (Closure-Nachschärfung Runtime-Fokus)

- Meta-/Setup-Wording aus `core/sl-referenz.md` (Struktur-Abschnitt) entfernt,
  damit die laufende Spielleitung keine Repo-/Wissensspeicher-Operatorik als
  Runtime-Regel interpretiert.
- Wartungshinweis aus `core/spieler-handbuch.md` gestrichen; der Schnellzugriff
  bleibt rein spielleitungsorientiert.
- Ergebnis: Wissensmodule bleiben auf Laufzeitregeln fokussiert;
  Setup-/Bestückungsanweisungen liegen ausschließlich in README/Setup-Dokumenten.


- Repo-weite Suchanker-Prüfung abgeschlossen (`optional`, `Pflicht`,
  `empfohlen`, `Rift`, `Belohnung`, `CU`, `Scaling`).
- Konfliktfund bereinigt: optionale Startwurf-Hausregel für Artefakt-Drops aus
  Core-Quickref und Toolkit-Aufruftext entfernt; Boss-only-Anker (Szene 10)
  bleibt in Core, Gameplay und Systems deckungsgleich.
- Closure-Gate erfüllt: Fahrplan, Audit und QA-Log sind synchronisiert;
  Pflichttestpaket ist dokumentiert und grün.

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
