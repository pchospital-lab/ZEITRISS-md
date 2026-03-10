---
title: "Issue-Pack Durchlauf 142 - Spielerhandbuch-Startpfad priorisieren + Watchguard"
version: 1.0.0
tags: [qa, plan, onboarding, mmo]
---

# Ziel

Restdrift im spieler-sichtigen Startvertrag schließen: Im Mini-Einsatzhandbuch
soll `klassisch + generate/custom generate/manuell` klar als Standard vor
`schnell` stehen, ohne den optionalen Fast-Lane-Pfad zu verlieren.

## Scope

- `core/spieler-handbuch.md`
- `tools/test_onboarding_start_save_watchguard.js`
- `internal/qa/process/known-issues.md`
- QA-Log für Durchlauf 142

## Checkliste

1. Startpfad im Mini-Einsatzhandbuch auf Standardpfad zuerst umformulieren.
2. `solo schnell`/`npc-team ... schnell` explizit als optionale Fast-Lane markieren.
3. Watchguard um einen Positiv-Check erweitern, der diese Priorisierung im
   Spieler-Handbuch absichert.
4. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
5. Link-Lint für geänderte Doku-/QA-Dateien ausführen.
6. Prozessspur in `known-issues.md` ergänzen.

## Abschlusskriterien

- Startvertrag ist im Spieler-Handbuch sichtbar kampagnenorientiert priorisiert.
- Neuer Watchguard-Check verhindert Regression in Folgeläufen.
- Smoke und Link-Lint sind grün.
