---
title: "Issue-Pack Fahrplan – Durchlauf 68 (Rang-Mapping Handbuch + Guard)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 68 (Rang-Mapping Handbuch + Guard)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` mit Fokus auf
Rangnamen-Konsistenz in der Spieler-Onboarding-Schicht.

## Ziel

1. Kanonisches ITI-Rang-Mapping (Ruf 0–5) im Spieler-Handbuch explizit führen.
2. Debrief-Format im Spielerpfad mit `ITI-Ruf` fixieren.
3. Watchguard um einen Positiv-Check auf das Debrief-Format im Handbuch erweitern.

## Scope dieses Durchlaufs

- Runtime-Module:
  - `core/spieler-handbuch.md`
- Guard/Smoke:
  - `tools/test_ruf_alien_watchguard.js`
- QA-Anschluss:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-68-ruf-alien-rangmapping-handbuch.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- `bash scripts/smoke.sh` bleibt grün inkl. Watchguard.
- Spieler-Handbuch enthält das SSOT-Rang-Mapping 0–5 samt Debrief-Format.
- Durchlauf 68 ist in Statusmatrix + Known-Issues-ZR-018 referenziert.
