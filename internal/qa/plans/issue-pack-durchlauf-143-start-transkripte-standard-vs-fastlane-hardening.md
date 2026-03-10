---
title: "Issue-Pack Durchlauf 143 - Start-Transkripte auf Standardpfad/Fast-Lane-Hierarchie härten"
version: 1.0.0
tags: [qa, plan, onboarding, mmo]
---

# Ziel

Anschlusslauf zu ZR-021: Die Start-Transkripte im Spieler-Handbuch sollen die
bereits harmonisierte Onboarding-Hierarchie sichtbar widerspiegeln
(Standardpfad `klassisch + generate` zuerst; `schnell` nur als optionale
Fast-Lane), inklusive Regression-Guard im Pflicht-Smoke.

## Scope

- `core/spieler-handbuch.md`
- `tools/test_onboarding_start_save_watchguard.js`
- `internal/qa/process/known-issues.md`
- QA-Log für Durchlauf 143

## Checkliste

1. Start-Transkriptblock um einen expliziten klassischen Kampagnenstart ergänzen.
2. Schnelleinstieg-Transkripte in Überschrift/Wording als Fast-Lane (optional)
   markieren.
3. Onboarding-Watchguard um Positiv-Checks auf diese Transcript-Hierarchie
   erweitern.
4. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
5. Link-Lint für geänderte Doku-/QA-Dateien ausführen.
6. Prozessspur in `known-issues.md` ergänzen.

## Abschlusskriterien

- Start-Transkripte spiegeln den kanonischen Standardpfad sichtbar wider.
- Fast-Lane bleibt als optionale Kurzrunde dokumentiert, aber klar sekundär.
- Neue Guard-Checks verhindern Rückfall in gleichwertige Darstellung.
