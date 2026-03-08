---
title: "Issue-Pack Fahrplan – Durchlauf 66 (Gating-Restdrift + Watchguard-Nachschärfung)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 66 (Gating-Restdrift + Watchguard-Nachschärfung)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` mit Fokus auf
verbliebene Wording-Drift in Ausrüstungszugang und Shop-Gating.

## Ziel

1. Verbleibende Mischbegriffe im Charakter-/Ausrüstungsmodul eliminieren
   ("Rufpunkte", "Dienstgrad/Ruf", levelbasiertes Tier-Gating).
2. Shop-Tier-Abschnitt auf SSOT vereinheitlichen:
   - formales Gating nur über `reputation.iti` + Lizenz-Tier,
   - Level als Build-Fortschritt, nicht als formaler Freigabeschlüssel,
   - Fraktionsruf nur politisch/narrativ.
3. Watchguard um Muster erweitern, damit genau diese Drift künftig im
   Pflicht-Smoke blockiert wird.

## Scope dieses Durchlaufs

- Runtime-Module:
  - `characters/charaktererschaffung-grundlagen.md`
  - `characters/ausruestung-cyberware.md`
- Guard/Smoke:
  - `tools/test_ruf_alien_watchguard.js`
- QA-Anschluss:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-66-ruf-alien-gating-restdrift.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- `bash scripts/smoke.sh` bleibt grün inkl. erweitertem Watchguard.
- Keine verbliebenen Formulierungen mehr, die formale Freigaben an
  "Dienstgrad/Ruf" oder Level-Bänder koppeln.
- Durchlauf 66 ist in Statusmatrix + Known-Issues-ZR-018 als Anschlusslauf
  referenziert.
