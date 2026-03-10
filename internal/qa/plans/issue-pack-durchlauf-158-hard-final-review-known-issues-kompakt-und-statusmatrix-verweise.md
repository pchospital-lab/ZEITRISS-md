---
title: "Issue-Pack Durchlauf 158 – Hard-Final-Review Prozesspflege (Known-Issues kompakt + Statusmatrix-Verweise)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Meta/Prozess
issue: ZR-021
---

# Ziel

Die operative Prozessseite `internal/qa/process/known-issues.md` soll als
Triage-Einstieg kurz und robust bleiben. Lange Durchlaufprosa wird nicht mehr
in Tabellenzellen geführt, sondern konsequent über Statusmatrizen und Archiv
referenziert.

# Arbeitspaket

1. `known-issues.md` in der Tabelle auf kompakte Notizen normalisieren.
2. Verweise auf bestehende Detailquellen (Statusmatrizen/Archive) je Track
   explizit setzen.
3. `hard-final-review-next-steps.md` auf den neuen Entrümpelungsstand
   synchronisieren.
4. Pflicht-Smoke laufen lassen.

# Abnahmekriterien

- `known-issues.md` bleibt lesbar und enthält nur kompakte Triage-Notizen.
- Detailstände sind über Statusmatrizen/Archive auffindbar.
- `hard-final-review-next-steps.md` enthält den Durchlauf-158-Stand.
- `bash scripts/smoke.sh` ist grün.
