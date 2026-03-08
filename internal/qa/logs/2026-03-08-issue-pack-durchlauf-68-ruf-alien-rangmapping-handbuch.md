---
title: "QA-Log – Issue-Pack Durchlauf 68 (Rang-Mapping Handbuch + Guard)"
date: 2026-03-08
scope: "ZR-018 Anschlusslauf für Rangnamen-Konsistenz im Spielerpfad"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Ursprungsreview: `uploads/ZEITRISS_ruf_alien_review.md`.
- Vorlauf:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-67-ruf-alien-chronopolis-rufklarheit.md`
- Fahrplan:
  - `internal/qa/plans/issue-pack-durchlauf-68-ruf-alien-rangmapping-handbuch.md`

## Umsetzung in diesem Durchlauf

1. **Spieler-Handbuch ergänzt (`core/spieler-handbuch.md`)**
   - Kanonisches **ITI-Rang-Mapping** (Ruf 0–5) als eigene SSOT-Tabelle ergänzt.
   - Kanonisches Debrief-Format (`Rang … · ITI-Ruf … · Lizenz Tier …`) explizit
     im Handbuch verankert, damit Onboarding und Referenzpfad identisch bleiben.

2. **Watchguard erweitert (`tools/test_ruf_alien_watchguard.js`)**
   - Neuer Positiv-Check auf das kanonische Debrief-Format im
     `core/spieler-handbuch.md` ergänzt.

3. **Prozessanschluss aktualisiert**
   - `internal/qa/process/ruf-alien-statusmatrix.md` um Durchlauf-68-Vermerk
     erweitert.
   - `internal/qa/process/known-issues.md` (ZR-018) um Durchlauf-68-Hinweis
     ergänzt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen.
- Rangnamen-Konsistenz ist nun zusätzlich im Spieler-Handbuch verankert und
  über den Pflicht-Smoke gegen Rückfälle abgesichert.
