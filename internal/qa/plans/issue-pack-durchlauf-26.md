---
title: "Issue-Pack Fahrplan – Durchlauf 26"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 26

Quelle: Fortsetzung ZR-016 (Save-SSOT-Drift im Runtime-Modul `speicher-fortsetzung.md`).

## Ziel
Das kanonische Kurzschema im Save-Modul auf das v7-Zielmodell festziehen und
per Lint-Guard absichern, damit Legacy-Strukturen nicht als aktiver Standard
zurückkehren.

## Scope dieses Durchlaufs

- Save-Modul-Konsolidierung:
  - `systems/gameflow/speicher-fortsetzung.md` (Kurzschema-Block auf v7)
- Tooling-Guardrail:
  - `tools/lint_runtime.py` (neuer Check für v7-Kurzschema)
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-26.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Umbau der Runtime-Engine in `runtime.js`.
- Vollständige Entfernung aller Legacy-Migrationshinweise aus der Save-Doku.
- Änderungen an Missions-/Tonregeln.

## Exit-Kriterium für Durchlauf 26

- Der Block "Kanonisches DeepSave-Schema (Kurzfassung, v7)" nutzt nur noch
  `v`, `characters[]`, `characters[].wallet`, `economy.hq_pool`, `arc.*`.
- Im v7-Kurzschema erscheinen keine Legacy-Strukturen (`save_version`,
  `character`, `party`, `team`, `economy.cu`, `economy.wallets`,
  `arc_dashboard`).
- `bash scripts/smoke.sh` ist grün.
