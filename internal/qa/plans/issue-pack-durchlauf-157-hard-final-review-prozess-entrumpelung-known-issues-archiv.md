---
title: "Issue-Pack Durchlauf 157 – Hard-Final-Review Prozess-Entrümpelung (Known-Issues-Archiv)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Meta/Prozess
issue: ZR-021
---

# Ziel

Die Prozessseite `internal/qa/process/known-issues.md` soll als operativer Einstieg kompakt bleiben.
Dafür wird die ausführliche historische Durchlaufchronik (73–156) in eine Archivdatei ausgelagert,
ohne die Nachvollziehbarkeit der Hard-Final-Review-Historie zu verlieren.

# Arbeitspaket

1. Historische Durchlaufnotizen aus `known-issues.md` in eine Archivdatei unter
   `internal/qa/process/archive/` verschieben.
2. In `known-issues.md` einen klaren Verweis auf das Archiv ergänzen.
3. `internal/qa/process/hard-final-review-next-steps.md` auf den neuen Stand synchronisieren
   (Task 1 teilweise/konkret umgesetzt).
4. Pflicht-Smoke laufen lassen.

# Abnahmekriterien

- `known-issues.md` bleibt als kompakte Triage-Seite lesbar.
- Archivdatei enthält die ausgelagerte Historie 73–156.
- `hard-final-review-next-steps.md` referenziert den erreichten Entrümpelungsstand.
- `bash scripts/smoke.sh` ist grün.
