---
title: "QA-Log – Issue-Pack Durchlauf 67 (Chronopolis-Rufklarheit + Guard)"
date: 2026-03-08
scope: "ZR-018 Anschlusslauf für Chronopolis-Gating-Wording"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Ursprungsreview: `uploads/ZEITRISS_ruf_alien_review.md`.
- Vorlauf:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-66-ruf-alien-gating-restdrift.md`
- Fahrplan:
  - `internal/qa/plans/issue-pack-durchlauf-67-ruf-alien-chronopolis-rufklarheit.md`

## Umsetzung in diesem Durchlauf

1. **Chronopolis-Wording vereinheitlicht (`gameplay/kampagnenuebersicht.md`)**
   - Mischformulierung `ITI-Rang/ITI-Ruf` entfernt.
   - Formales Gating explizit auf **ITI-Ruf** (`reputation.iti`) gesetzt.
   - Klartext ergänzt: sichtbarer ITI-Rang ist eine abgeleitete Anzeige, kein
     separater Freigabeschlüssel.
   - Kernbereichs-Zugang auf **höheren ITI-Ruf** statt Dienstgrad-Wording
     präzisiert.

2. **Watchguard nachgeschärft (`tools/test_ruf_alien_watchguard.js`)**
   - Neuer Rückfallblocker gegen `ITI-Rang/ITI-Ruf` im Chronopolis-Modul.

3. **Prozessanschluss aktualisiert**
   - `internal/qa/process/ruf-alien-statusmatrix.md` um Durchlauf-67-Vermerk
     erweitert.
   - `internal/qa/process/known-issues.md` (ZR-018) um Durchlauf-67-Hinweis
     ergänzt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen.
- Chronopolis-Gating verwendet nun konsistent den formalen
  `reputation.iti`-Pfad ohne Mischbegriff; der Smoke blockiert entsprechende
  Regressionen im Folge-Lauf.
