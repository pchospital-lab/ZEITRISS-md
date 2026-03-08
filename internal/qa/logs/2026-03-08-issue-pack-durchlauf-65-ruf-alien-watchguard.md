---
title: "QA-Log – Issue-Pack Durchlauf 65 (Watchguard + Prozess-Aufräumlauf)"
date: 2026-03-08
scope: "ZR-018 Watchpoint-Absicherung per Smoke-Guard und Prozessanschluss"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Ursprungsreview: `uploads/ZEITRISS_ruf_alien_review.md`.
- Vorlauf:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-64-ruf-alien-chronopolis-schlauchlevel.md`
- Fahrplan:
  - `internal/qa/plans/issue-pack-durchlauf-65-ruf-alien-watchguard.md`

## Umsetzung in diesem Durchlauf

1. **Smoke-Watchguard ergänzt (`tools/test_ruf_alien_watchguard.js`)**
   - Guard prüft Debrief-Disziplin auf explizites `ITI-Ruf-Update`.
   - Guard verhindert Tier-V-Rückfall auf globales `Questbelohnung`-Wording.
   - Guard verhindert frühe harte Alien-Faktbehauptungen in Onboarding-
     Schlüsselstellen.

2. **Pflicht-Smoke erweitert (`scripts/smoke.sh`)**
   - Neuer Schritt `test_ruf_alien_watchguard.js` in den Smoke-Ablauf aufgenommen.
   - Marker-Check `ruf-alien-watchguard-ok` als klare Pass-Bedingung ergänzt.

3. **Prozessanschluss aktualisiert**
   - `internal/qa/process/ruf-alien-statusmatrix.md` um Durchlauf-65-Hinweis,
     Guard-Notiz und Verknüpfung ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-018) um Durchlauf-65-
     Referenz ergänzt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen.
- Die bisher manuell getragenen Watchpoints sind jetzt als leichter
  Smoke-Guard verstetigt und geben für Durchlauf 66+ einen direkten
  Regression-Alarm.
