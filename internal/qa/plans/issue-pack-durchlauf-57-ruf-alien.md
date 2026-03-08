---
title: "Issue-Pack Fahrplan – Durchlauf 57 (Ruf/Alien)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 57 (Ruf/Alien)

Quelle: `uploads/ZEITRISS_ruf_alien_review.md`.

## Ziel

1. Ruf-/Tier-Progress als SSOT über die Spieler- und Runtime-nahen Module
   vereinheitlichen (`reputation.iti` vs. `reputation.factions.*`).
2. Alien-/Mystery-Onboarding so schärfen, dass frühe Texte keine harten
   Alien-Fakten setzen.
3. Anschluss-QA schaffen (Status je Review-Issue, Watchpoints für Folge-Durchläufe).

## Scope dieses Durchlaufs

- SSOT-Updates in:
  - `characters/charaktererschaffung-grundlagen.md`
  - `characters/ausruestung-cyberware.md`
  - `meta/masterprompt_v6.md`
  - `core/sl-referenz.md`
  - `core/spieler-handbuch.md`
  - `gameplay/kampagnenuebersicht.md`
- QA-Anschluss:
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-57-ruf-alien.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- Alter Ruf-Link (`iti = max(factions.*)`) ist in den betroffenen Modulen entfernt.
- ITI-Ruf-Progression (M1, M5, M10, M15, M20) ist als kanonischer Standard dokumentiert.
- Tier V ist als kaufbare Lizenz bei Ruf +5 geführt.
- Frühe Spielertexte behandeln Alien-Signaturen als Gerücht-/Aktenlage,
  nicht als bestätigte Welt-Tatsache.
- Pflicht-Smoke (`bash scripts/smoke.sh`) bleibt grün.
