---
title: "Issue-Pack Durchlauf 161 – Hard-Final-Review Watchguard-Resolver-Rollout"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

# Ziel

Weitere Hard-Final-Review-Watchguards sollen auf die gemeinsame Resolver-
Utility standardisiert werden, damit Zielpfad-Auflösung bei Datei-
Umstrukturierungen robust bleibt und keine Guard-Insellösungen fortbestehen.

# Arbeitspaket

1. `tools/test_default_slot_dependency_watchguard.js` auf
   `tools/watchguard_file_resolver.js` umstellen.
2. `tools/test_hard_final_review_watchguard.js` auf die gleiche Utility
   umstellen (je Teilziel mit Preferred-Pfad + Fallback-Scan).
3. Prozessspur synchronisieren (`internal/qa/process/hard-final-review-next-steps.md`,
   `internal/qa/process/known-issues.md`, Durchlauf-Log).
4. Pflicht-Smoke ausführen.

# Abnahmekriterien

- Beide Watchguards nutzen `resolveUniqueMarkdownTarget` produktiv.
- Bestehende Guard-Checks bleiben inhaltlich unverändert wirksam.
- Prozessseiten enthalten den Durchlauf-161-Stand.
- `bash scripts/smoke.sh` ist grün.
