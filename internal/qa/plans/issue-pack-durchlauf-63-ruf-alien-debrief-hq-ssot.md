---
title: "Issue-Pack Fahrplan – Durchlauf 63 (Debrief/HQ-SSOT-Klarzug)"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 63 (Debrief/HQ-SSOT-Klarzug)

Quelle: Anschlusslauf auf `uploads/ZEITRISS_ruf_alien_review.md` nach
Durchlauf 62, mit Fokus auf verbliebene Drift im Missionsabschluss- und
HQ-Freigabewording in `gameplay/kampagnenstruktur.md`.

## Ziel

1. Debrief-Pfad in der Kampagnenstruktur auf den SSOT-Begriff
   `ITI-Ruf-Update` vereinheitlichen.
2. HQ-/Lizenz-Freigaben sauber zwischen formaler ITI-Steuerung und
   politischem Fraktionssignal trennen.
3. Anschlussfähigkeit sichern: Durchlauf dokumentieren und in Prozessindex
   verlinken.

## Scope dieses Durchlaufs

- Inhaltliche Korrekturen in:
  - `gameplay/kampagnenstruktur.md`
- QA-Anschluss:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-63-ruf-alien-debrief-hq-ssot.md`
  - `internal/qa/process/ruf-alien-statusmatrix.md`
  - `internal/qa/process/known-issues.md`

## Exit-Kriterien

- Missionsabschluss nennt im Auto-Screen konsistent `ITI-Ruf-Update`
  statt generischem `Ruf`.
- HQ-/Ausrüstungsfreigaben trennen klar:
  - `reputation.iti` für formale ITI-Zugänge und Tier-Lizenzen,
  - `reputation.factions.*` für politische/narrative Modifikatoren.
- ZR-018 bleibt abgeschlossen; Durchlauf 63 ist in den Prozessdokumenten
  referenziert.
- Pflicht-Smoke (`bash scripts/smoke.sh`) bleibt grün.
