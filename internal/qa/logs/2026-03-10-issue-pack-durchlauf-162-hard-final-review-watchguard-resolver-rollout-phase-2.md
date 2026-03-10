---
title: "Log – Durchlauf 162 (Hard-Final-Review / Watchguard-Resolver-Rollout Phase 2)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

## Kontext

Nach den Durchläufen 160/161 war die Resolver-Utility bereits in ausgewählten
Guards aktiv. Als Anschlussaufgabe blieb, die übrigen zentralen Hard-Final-
Review-Guards ebenfalls auf dieselbe robuste Zielpfad-Auflösung zu heben.

## Umsetzung

- `tools/test_director_layer_watchguard.js` auf
  `resolveUniqueMarkdownTarget` umgestellt.
- `tools/test_onboarding_start_save_watchguard.js` auf Resolver-Utility für
  Markdown-Ziele standardisiert; nicht-Markdown (`master-index.json`,
  `scripts/setup-openwebui.sh`) bleiben direkte Datei-Reads.
- `tools/test_iti_hardcanon_watchguard.js` auf Resolver-Utility für die
  Atlas-/Personal-SSOT-Zieldateien umgestellt.
- Prozessseiten synchronisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md`

## Ergebnis

- Die zentralen Hard-Final-Review-Watchguards verwenden nun einheitlich die
  gemeinsame Resolver-Utility.
- Zielpfadauflösung ist damit über weitere Guard-Familien hinweg robuster und
  wartungsärmer.

## Checks

- `node tools/test_director_layer_watchguard.js` erfolgreich.
- `node tools/test_onboarding_start_save_watchguard.js` erfolgreich.
- `node tools/test_iti_hardcanon_watchguard.js` erfolgreich.
- `bash scripts/smoke.sh` erfolgreich.
