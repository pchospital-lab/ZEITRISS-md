---
title: "QA-Log – Issue-Pack Durchlauf 66 (Gating-Restdrift + Watchguard-Nachschärfung)"
date: 2026-03-08
scope: "ZR-018 Anschlusslauf für Gating-Wording und Drift-Guard"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Ursprungsreview: `uploads/ZEITRISS_ruf_alien_review.md`.
- Vorlauf:
  - `internal/qa/logs/2026-03-08-issue-pack-durchlauf-65-ruf-alien-watchguard.md`
- Fahrplan:
  - `internal/qa/plans/issue-pack-durchlauf-66-ruf-alien-gating-restdrift.md`

## Umsetzung in diesem Durchlauf

1. **Charaktermodul nachgeschärft (`characters/charaktererschaffung-grundlagen.md`)**
   - Fraktionsübertritt-Abschnitt auf explizite **ITI-Rufpunkte** vereinheitlicht.
   - Ausrüstungszugangstext von unscharfem "Dienstgrad/Ruf" auf formales
     **ITI-Ruf + Lizenz-Tier** umgestellt.

2. **Shop-Gating konsolidiert (`characters/ausruestung-cyberware.md`)**
   - Restabschnitt "Shop-Tiers & Gating" von levelbasierten Tier-Bändern auf
     SSOT-Lesart umgestellt.
   - Klartext ergänzt: Formale Freigaben über `reputation.iti` + Lizenz-Tier,
     Level nur Build-Fortschritt, Fraktionsruf nur politisch/narrativ.

3. **Watchguard erweitert (`tools/test_ruf_alien_watchguard.js`)**
   - Neuer Rückfallblocker gegen altes Misch-Wording `Dienstgrad/Ruf`.
   - Neuer Rückfallblocker gegen levelbasierte Tier-Header (`Tier X (Lv ...)`).

4. **Prozessanschluss aktualisiert**
   - `internal/qa/process/ruf-alien-statusmatrix.md` um Durchlauf-66-Vermerk
     erweitert.
   - `internal/qa/process/known-issues.md` (ZR-018) um Durchlauf-66-Hinweis
     ergänzt.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- ZR-018 bleibt abgeschlossen.
- Watchguard deckt jetzt zusätzlich die zuletzt gefundenen
  Gating-Wording-Rückfälle ab und liefert für Folge-Durchläufe schnellere
  Regressionserkennung.
