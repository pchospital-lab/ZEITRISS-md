---
title: "Issue-Pack Fahrplan – Durchlauf 22"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 22

Quelle: `uploads/ZEITRISS_codex_issue_pack.md` (Issue 7/12: essayistische Runtime-Reste und Meta-Leaks entfernen).

## Ziel
Verbleibende Meta-/Editorial-Hinweise im Runtime-Modul
`systems/gameflow/cinematic-start.md` weiter zurückbauen und als in-world,
betriebsnahe Spielleitungs-Leitplanken konsolidieren.

## Scope dieses Durchlaufs

- Runtime-Textkorrektur:
  - `systems/gameflow/cinematic-start.md`
- Drift-Guard im Tooling:
  - `tools/lint_runtime.py`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-22.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Änderungen an Save-Schema, Ökonomie, Boss-Timing oder Szenenanzahl.
- Umbau der Pacing-Mechanik (`output_pace`) oder Missions-Templates.

## Exit-Kriterium für Durchlauf 22

- Abschnitt zu optionalen Debrief-Rückblicken ist ohne externe Tool-/Modellnamen
  formuliert.
- Lint erkennt Rückfälle auf Sora/ChatGPT/Video-KI/„Film ab!" im
  `cinematic-start.md`.
- `bash scripts/smoke.sh` ist grün.
