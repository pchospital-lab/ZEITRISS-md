---
title: "QA-Log – Issue-Pack Durchlauf 21"
date: 2026-03-07
scope: "Issue 7: Runtime-Kanon im Cinematic-Start ent-essayisieren"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Externes Issue-Pack (`uploads/ZEITRISS_codex_issue_pack.md`), Issue 7:
  Runtime-Kanon von Autorenessay trennen.
- Maintainer-Auftrag: iterativ weiterarbeiten mit Plan/QA-Anschlussfähigkeit.

## Umsetzung in diesem Durchlauf

1. **Cinematic-Start bereinigt (`systems/gameflow/cinematic-start.md`)**
   - Explizite Playlist-/Soundtrack-Hinweise durch In-World-Akustikleitplanken
     ersetzt (Comms-Pings, Sirenen, Hall, Maschinenlärm).
   - Regie-/Set-Metaphern entschärft (`Regie` → `Leitfaden`, Set-Formulierungen
     auf Einsatzsprache gezogen).
   - Marken-/Referenzsprache nachgeschärft (`Akte X` → generische
     Mystery-Fallserien-Formulierung).

2. **Drift-Guard ergänzt (`tools/lint_runtime.py`)**
   - Neuer Check `check_forbidden_editorial_aids()` prüft
     `systems/gameflow/cinematic-start.md` auf verbotene Editorial-Helferbegriffe:
     `Playlist`, `Soundtrack`, `Akte X`, `am Set`.
   - Check in `main()` eingebunden, damit der Guard im Pflicht-Smoke automatisch
     läuft.

3. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 21 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 21 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
