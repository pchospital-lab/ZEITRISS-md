---
title: "Issue-Pack Durchlauf 162 – Hard-Final-Review Watchguard-Resolver-Rollout (Phase 2)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

# Ziel

Die verbleibenden zentralen Hard-Final-Review-Watchguards sollen ebenfalls auf
`tools/watchguard_file_resolver.js` standardisiert werden, damit die
Zielpfad-Auflösung bei Datei-Umbenennungen oder -Verschiebungen konsistent
robust bleibt.

# Arbeitspaket

1. `tools/test_director_layer_watchguard.js` auf Resolver-Utility umstellen.
2. `tools/test_onboarding_start_save_watchguard.js` auf Resolver-Utility
   standardisieren (für Markdown-Ziele; Shell/JSON unverändert direkt lesen).
3. `tools/test_iti_hardcanon_watchguard.js` auf Resolver-Utility umstellen
   (Atlas-/Personal-SSOT-Ziele).
4. Prozessspur synchronisieren (`internal/qa/process/hard-final-review-next-steps.md`,
   `internal/qa/process/known-issues.md`, Durchlauf-Log).
5. Pflicht-Smoke ausführen.

# Abnahmekriterien

- Die drei Watchguards nutzen `resolveUniqueMarkdownTarget` produktiv.
- Assertions bleiben inhaltlich gleichwertig wirksam.
- Prozessseiten enthalten den Durchlauf-162-Stand.
- `bash scripts/smoke.sh` ist grün.
