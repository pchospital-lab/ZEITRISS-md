---
title: "Issue-Pack Fahrplan – Durchlauf 12"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 12

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Issue 12 aus dem externen Pack umsetzen: Meta-/Modellbegriffe in geladenen
Runtime-Modulen entfernen und per Lint gegen Regression absichern.

## Scope dieses Durchlaufs

- Terminologie-Sweep in geladenen Runtime-Modulen:
  - `GPT` / `MyGPT` -> `KI-SL`
  - `Director` / `Directors` -> `Spielleitung` / `Spielleitungen`
  - `LLM` -> `KI-SL`
- Drift-Guard erweitern (`tools/lint_runtime.py`):
  - neuer Check auf verbotene Meta-Begriffe in `core/`, `characters/`,
    `gameplay/`, `systems/`.
- QA-Nachführung (`known-issues`, Plan/Log).

## Nicht im Scope (bewusst verschoben)

- Dateiumbenennung von `systems/toolkit-gpt-spielleiter.md`
  (separater Migrationsschritt, da potenziell Referenz-/Index-Folgen).
- Stilistische Vollredaktion jenseits der Terminologie.

## Exit-Kriterium für Durchlauf 12

- In geladenen Runtime-Modulen keine Treffer mehr für
  `GPT`, `MyGPT`, `LLM`, `Director`, `Directors`.
- `bash scripts/smoke.sh` ist grün und enthält den neuen Drift-Guard.
