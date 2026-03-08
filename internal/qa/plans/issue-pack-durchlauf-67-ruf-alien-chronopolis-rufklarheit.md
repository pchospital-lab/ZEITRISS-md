---
title: "Issue-Pack Fahrplan – Durchlauf 67 (Chronopolis-Rufklarheit + Guard)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 67 (Chronopolis-Rufklarheit + Guard)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` mit Fokus auf
Restdrift im Chronopolis-Zugangs-/Shop-Wording (`ITI-Rang/ITI-Ruf`).

## Ziel

1. Mischbegriff im Chronopolis-Text entfernen und formales Gating eindeutig auf
   `reputation.iti` ziehen.
2. Sichtbaren ITI-Rang als abgeleitete Anzeige definieren (nicht separater
   Freigabeschlüssel).
3. Watchguard um Rückfallmuster für `ITI-Rang/ITI-Ruf` ergänzen.

## Scope dieses Durchlaufs

- Runtime-Module:
  - `gameplay/kampagnenuebersicht.md`
- Guard/Smoke:
  - `tools/test_ruf_alien_watchguard.js`
- QA-Anschluss:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-67-ruf-alien-chronopolis-rufklarheit.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- `bash scripts/smoke.sh` bleibt grün inkl. Watchguard.
- Chronopolis nutzt kein `ITI-Rang/ITI-Ruf`-Mischgating mehr.
- Durchlauf 67 ist in Statusmatrix + Known-Issues-ZR-018 referenziert.
