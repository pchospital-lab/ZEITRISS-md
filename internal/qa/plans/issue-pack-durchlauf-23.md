---
title: "Issue-Pack Fahrplan – Durchlauf 23"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 23

Quelle: Maintainer-Feedback auf Durchlauf 22 (Wortlaut/Datensatz-Klarheit).

## Ziel
Gender-Syntax aus dem betroffenen Runtime-Modul entfernen und den Stil auf
klare, einfache Pluralformen ziehen; zusätzlich Drift-Guard ergänzen, damit die
unerwünschte Syntax nicht wieder in Runtime-Dateien einläuft.

## Scope dieses Durchlaufs

- Runtime-Textkorrektur:
  - `systems/gameflow/cinematic-start.md`
- Drift-Guard im Tooling:
  - `tools/lint_runtime.py`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-23.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Änderungen an Save-Schema, Ökonomie, Boss-Timing oder Szenenanzahl.
- Umbauten anderer Runtime-Module außerhalb des direkt beanstandeten Bereichs.

## Exit-Kriterium für Durchlauf 23

- In `systems/gameflow/cinematic-start.md` sind keine Formen wie `*innen`,
  `:innen`, `der/die`, `jede/r` mehr enthalten.
- Debrief-Recap nutzt keinen HQ-fremden PP-Zustandsbezug.
- `bash scripts/smoke.sh` ist grün.
