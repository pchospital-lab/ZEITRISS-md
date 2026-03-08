---
title: "Issue-Pack Fahrplan – Durchlauf 64 (Chronopolis-Schlauchlevel + Level-10-Klarzug)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 64 (Chronopolis-Schlauchlevel + Level-10-Klarzug)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` plus
Maintainer-Hinweis zur Chronopolis-Wegführung als Schlauchlevel.

## Ziel

1. Chronopolis-Wegführung als **feste Schlauchroute** SSOT-klarziehen
   (Eingangsschleuse → Ringlauf → gegenüberliegende Ausgangsschleuse).
2. Level-10-Textstellen ohne impliziten Shop-Freigabe-Drift halten
   (Vertrauen/Chronopolis-Schlüssel vs. formale ITI-Ruf-/Lizenzpfade).
3. Anschlussfähigkeit im QA-Prozess sichern (Plan, Log, Statusmatrix,
   Known-Issues-Referenz).

## Scope dieses Durchlaufs

- Inhaltliche Korrekturen in:
  - `core/zeitriss-core.md`
  - `core/sl-referenz.md`
  - `gameplay/kampagnenstruktur.md`
- QA-Anschluss:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-64-ruf-alien-chronopolis-schlauchlevel.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- Chronopolis ist in Referenz- und Kampagnenmodul explizit als
  **Schlauchlevel** beschrieben.
- Level-10-Formulierungen bleiben kompatibel mit SSOT:
  - Chronopolis-Zugang/Verantwortung über Level,
  - formale Ausrüstungslizenzen über `reputation.iti` + Tier.
- ZR-018 bleibt `abgeschlossen`; Durchlauf 64 ist im Prozessindex
  verlinkt.
- Pflicht-Smoke (`bash scripts/smoke.sh`) bleibt grün.
