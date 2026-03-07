---
title: "QA-Log – Issue-Pack Durchlauf 22"
date: 2026-03-07
scope: "Issue 7/12: cinematic-start weiter ent-essayisieren (Meta-/Tool-Drift)"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Externes Issue-Pack (`uploads/ZEITRISS_codex_issue_pack.md`), Issue 7 und 12:
  Runtime-Kanon von Autorenessay trennen und Meta-Leaks aus Runtime-Modulen
  entfernen.
- Maintainer-Auftrag: iterativ mit Fahrplan + QA-Log fortsetzen.

## Umsetzung in diesem Durchlauf

1. **Cinematic-Start bereinigt (`systems/gameflow/cinematic-start.md`)**
   - Abschnitt „Optionale Erweiterung" von Sora/„Film ab!"/Video-KI auf
     in-world Debrief-Recap umgestellt.
   - Tool-/Modellbezüge entfernt und auf klaren Kodex-Recap-Fokus reduziert
     (Lage, Belastung, Folgen, nächster Schritt).
   - Übergangsformulierung präzisiert, damit die Szene weiterhin
     spielerzentriert bleibt, ohne Meta-Rahmung.

2. **Drift-Guard erweitert (`tools/lint_runtime.py`)**
   - `check_forbidden_editorial_aids()` ergänzt um Muster für
     `Sora`, `ChatGPT`, `Video-KI`, `Film ab!` in
     `systems/gameflow/cinematic-start.md`.
   - `check_forbidden_meta_terms_in_runtime()` um `ChatGPT` erweitert.

3. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 22 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 22 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
