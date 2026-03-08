---
title: "QA-Log – Issue-Pack Durchlauf 58 (Ruf/Alien Follow-up)"
date: 2026-03-08
scope: "SSOT-Feinschliff Spieler-Handbuch (Ruf/Tier)"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Ursprungsreview: `uploads/ZEITRISS_ruf_alien_review.md`.
- Vorlauf: `internal/qa/logs/2026-03-08-issue-pack-durchlauf-57-ruf-alien.md`.
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-58-ruf-alien-followup.md`.

## Umsetzung in diesem Durchlauf

1. **Debrief-Benennung präzisiert**
   - `core/spieler-handbuch.md` (Schnellstart Schritt 6):
     `Ruf + Lizenz-Tier` auf `ITI-Ruf + Lizenz-Tier` umgestellt.

2. **Tier-V-Drift im Cheatsheet behoben**
   - `core/spieler-handbuch.md` (Tier-Lizenzen): Tier V von
     `Questbelohnung` auf `5.000 CU` korrigiert.
   - Ergänzt: Klartext, dass ab Ruf +5 reguläre ITI-Lizenzpfade kaufbar sind
     und Sonderfälle objektbezogen statt über globale Tier-V-Sperre laufen.

3. **QA-Prozess fortgeschrieben**
   - Statusmatrix (`internal/qa/process/ruf-alien-statusmatrix.md`) um
     Follow-up-Hinweis für Durchlauf 58 erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen; der verbliebene Onboarding-Drift im
  Spieler-Handbuch ist geschlossen.
- Folge-Durchläufe prüfen weiter nur die Watchpoints (Debrief-Label,
  Rangnamen, Tier-V-Rückfall, Onboarding-Ton).
