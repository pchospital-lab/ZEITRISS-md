---
title: "QA-Log – Issue-Pack Durchlauf 12"
date: 2026-03-06
scope: "Issue 12: Meta-/Modellbegriffe aus Runtime-Modulen entfernen + Drift-Guard"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Externer Pack `uploads/ZEITRISS_codex_issue_pack.md`, Issue 12
  (Terminologie-Sweep für Runtime-Module).

## Umsetzung in diesem Durchlauf

1. **Terminologie in Runtime-Modulen bereinigt**
   - Betroffene Module in `core/`, `gameplay/`, `systems/` wurden auf
     KI-Sprache vereinheitlicht (`KI-SL`/`Spielleitung`).
   - Modell-/Meta-Terme (`GPT`, `MyGPT`, `LLM`, `Director`, `Directors`) in
     den geladenen Modulen ersetzt.

2. **Automatischen Regressionstest ergänzt**
   - `tools/lint_runtime.py` um
     `check_forbidden_meta_terms_in_runtime()` erweitert.
   - Der Check läuft über alle Runtime-Markdown-Dateien und schlägt bei
     verbotenen Meta-Begriffen fehl.

3. **QA-Nachführung**
   - Durchlauf 12 als Plan/Log ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Verweise auf
     Durchlauf 12 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
