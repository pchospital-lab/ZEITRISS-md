---
title: "Issue-Pack Fahrplan – Durchlauf 58 (Ruf/Alien Follow-up)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 58 (Ruf/Alien Follow-up)

Quelle: Follow-up auf `uploads/ZEITRISS_ruf_alien_review.md` nach Abschluss von
Durchlauf 57.

## Ziel

1. Letzten SSOT-Drift im Spieler-Onboarding entfernen (Tier-V-Lizenzkosten im
   Cheatsheet).
2. Debrief-Wording im Schnellstart auf konsistente ITI-Ruf-Benennung ziehen.
3. Anschluss-QA dokumentieren, damit Folgedurchläufe den Restzustand klar sehen.

## Scope dieses Durchlaufs

- Inhaltliche Korrekturen in:
  - `core/spieler-handbuch.md`
- QA-Anschluss:
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-58-ruf-alien-followup.md`

## Exit-Kriterien

- Cheatsheet führt Tier V als kaufbare Lizenz (`Ruf +5`, `5.000 CU`).
- Debrief im Schnellstart nennt explizit `ITI-Ruf` statt generischem `Ruf`.
- Pflicht-Smoke (`bash scripts/smoke.sh`) bleibt grün.
