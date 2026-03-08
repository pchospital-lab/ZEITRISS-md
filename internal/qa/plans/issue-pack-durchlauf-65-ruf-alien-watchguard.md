---
title: "Issue-Pack Fahrplan – Durchlauf 65 (Watchguard + Prozess-Aufräumlauf)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 65 (Watchguard + Prozess-Aufräumlauf)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` mit Fokus auf
stabile Drift-Prävention für ZR-018.

## Ziel

1. ZR-018-Watchpoints in einen wiederholbaren Folge-Lauf überführen
   (Plan/Log/Index auf Durchlauf 65 erweitern).
2. Leichten Smoke-Watchguard ergänzen, der Rückfälle in drei Kernbereichen
   automatisch meldet:
   - Debrief-Labeling (`ITI-Ruf-Update`),
   - Tier-V-Formulierung (kein globales `Questbelohnung`),
   - frühe Alien-Onboarding-Faktbehauptungen.
3. Prozessdokumente als Anschlussanker für Durchlauf 66+ aufräumen.

## Scope dieses Durchlaufs

- Tooling/Smoke:
  - `tools/test_ruf_alien_watchguard.js`
  - `scripts/smoke.sh`
- QA-Anschluss:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-65-ruf-alien-watchguard.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- `bash scripts/smoke.sh` bleibt grün inkl. neuem Watchguard.
- ZR-018 bleibt `abgeschlossen`; Durchlauf 65 ist in Statusmatrix und
  Known-Issues-Notiz verlinkt.
- Watchpoints sind als dauerhafter Guard für Folge-Durchläufe dokumentiert.
