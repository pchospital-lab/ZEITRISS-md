---
title: "Issue-Pack Fahrplan – Durchlauf 21"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 21

Quelle: `uploads/ZEITRISS_codex_issue_pack.md` (Issue 7: Runtime-Kanon von Autorenessay trennen).

## Ziel
Essayistische Editorial-Hinweise im Runtime-Modul `cinematic-start.md` abbauen,
ohne den Spielstil zu verwässern: Fokus auf in-world Signale, klare
Spielleitungs-Leitplanken und stabile Runtime-Texte für die KI-SL.

## Scope dieses Durchlaufs

- Runtime-Textkorrektur:
  - `systems/gameflow/cinematic-start.md`
- Drift-Guard im Tooling:
  - `tools/lint_runtime.py`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-21.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Änderungen an Save-Schema, Ökonomie, Boss-Timing, Szenenanzahl oder Px-Formel.
- Umbau der Missionsideen, Kampfregeln oder Chronopolis/HQ-Logik.

## Exit-Kriterium für Durchlauf 21

- Externe Audio-/Regiemetaphern in den bearbeiteten Textstellen sind entfernt
  oder in In-World-Leitplanken überführt.
- Das Lint erkennt Rückfälle auf die verbotenen Editorial-Helferbegriffe in
  `systems/gameflow/cinematic-start.md`.
- `bash scripts/smoke.sh` ist grün.
