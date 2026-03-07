---
title: "Issue-Pack Fahrplan – Durchlauf 25"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 25

Quelle: Fortsetzung ZR-016 (Terminologie-/Editorial-Drift in Runtime-Modulen).

## Ziel
Verbleibende Meta-/Editorial-Reste in geladenen Runtime-Modulen entfernen und den
Lint so erweitern, dass Begriffe wie `GPTs` oder `Film ab!` nicht still in den
Kanon zurückrutschen.

## Scope dieses Durchlaufs

- Runtime-Textkonsolidierung:
  - `gameplay/kampagnenstruktur.md`
  - `core/sl-referenz.md`
  - `core/wuerfelmechanik.md`
  - `systems/kp-kraefte-psi.md`
- Tooling-Guardrail:
  - `tools/lint_runtime.py`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-25.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Änderungen am Save-Schema, Economy-Datenmodell oder Chronopolis-Logik.
- Runtime.js-Refactoring.
- Neue Spielmechaniken.

## Exit-Kriterium für Durchlauf 25

- In Runtime-Modulen keine Formulierung mit `GPTs` oder `Film ab!` mehr.
- Lint erkennt künftig auch `GPTs` als verbotenen Meta-Begriff.
- Editorial-Pattern (`Playlist`, `Soundtrack`, `Akte X`, `am Set`, `Sora`,
  `Video-KI`, `Film ab!`) werden runtime-weit geprüft.
- `bash scripts/smoke.sh` ist grün.
