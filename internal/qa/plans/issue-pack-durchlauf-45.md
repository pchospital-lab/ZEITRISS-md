---
title: "Issue-Pack Fahrplan – Durchlauf 45"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 45

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 5: Arena-Savegrenze `completed` vs `idle`).

## Ziel

Die Arena-Savegrenze auf eine belastbare Wahrheit festziehen, damit der
kritische PvP→HQ-Savepunkt eindeutig dokumentiert und mit der Runtime synchron
bleibt.

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`: Save-Regeltext von
  missverständlicher `idle`-Lesart auf Runtime-konsistente Freigabe
  (`idle|completed` bei inaktiver Arena) umstellen.
- `core/sl-referenz.md`: dieselbe Regel als SL-Betriebsstandard spiegeln.
- Pflicht-Smoke als Regression-Gate ausführen.

## Exit-Kriterium

- Eine konsistente Arena-Save-Regel bleibt übrig (keine konkurrierenden
  Aussagen `idle only` vs `idle|completed`).
- PvP-Ausstieg ist als dokumentierter HQ-Savepunkt klar verständlich.
- Pflicht-Smoke bleibt grün.
