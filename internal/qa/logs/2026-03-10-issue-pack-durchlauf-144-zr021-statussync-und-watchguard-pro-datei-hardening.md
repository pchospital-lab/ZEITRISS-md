---
title: "QA-Log Durchlauf 144 - ZR-021 Status-Sync und Onboarding-Watchguard pro Datei"
version: 1.0.0
tags: [qa, log, onboarding, mmo]
---

# Kontext

Nach Durchlauf 143 war der Onboarding-Track inhaltlich weitgehend stabil, aber
es blieben zwei Prozess-/Qualitätslücken:

1. `ZR-021` stand in der Prozessmatrix weiterhin auf `in Umsetzung`, obwohl die
   Anschlussläufe 140-143 bereits umgesetzt und dokumentiert waren.
2. Der Onboarding-Watchguard arbeitete im Start-/HQ-Bereich teilweise über
   Mindesttreffer und konnte damit Datei-spezifische Driftfälle verdecken.

## Umgesetzte Änderungen

1. `tools/test_onboarding_start_save_watchguard.js`
   - Pro-Datei-Helper `assertPerDocRule(...)` ergänzt.
   - Startvertrag zusätzlich zu `minHits` mit dateispezifischen Pflichtchecks
     gehärtet (`natürliche Sprache`, `klassisch als Standard`,
     `generate/custom generate/manuell`).
   - HQ-Flow um eine explizite Rule-Matrix erweitert:
     - `Deepsave möglich` in Toolkit/SL-Referenz/Speichermodul,
     - `kein Auto-Briefing` in Toolkit/SL-Referenz/Speichermodul,
     - `neuer Chat empfohlen` in allen HQ-Referenzdokumenten.
2. `internal/qa/process/known-issues.md`
   - ZR-021 auf konsistenten Stand 140-144 nachgezogen und als
     Deepsearch-Übergabepunkt markiert.

## Verifikation

- Pflicht-Smoke erfolgreich.
- Link-Lint auf geänderten Doku-/QA-Dateien erfolgreich.

## Ergebnis

Der Onboarding-Track ist wieder in einer sauberen Spur: dokumentierter
Abschluss-/Übergabestand in der Prozessmatrix plus präziserer Watchguard, der
auch dateiweise Drift früh sichtbar macht.
