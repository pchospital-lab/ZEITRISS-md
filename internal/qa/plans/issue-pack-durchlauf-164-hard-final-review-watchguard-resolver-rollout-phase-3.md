---
title: "Issue-Pack Durchlauf 164 – Hard-Final-Review Watchguard-Resolver-Rollout (Phase 3)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

# Ziel

Weitere zentrale Hard-Final-Review-Watchguards sollen auf die gemeinsame
Resolver-Utility umgestellt werden, damit Zielpfad-Auflösung auch bei
Dateiverschiebungen robust bleibt und Einzellösungen in `tools/` reduziert
werden.

# Arbeitspaket

1. `tools/test_ruf_alien_watchguard.js` auf `resolveUniqueMarkdownTarget`
   umstellen.
2. `tools/test_physicality_watchguard.js` auf
   `resolveUniqueMarkdownTarget` umstellen.
3. `tools/test_kausalabfang_watchguard.js` auf
   `resolveUniqueMarkdownTarget` umstellen.
4. Prozessspur synchronisieren (`known-issues.md`,
   `hard-final-review-next-steps.md`, Durchlauf-Log).
5. Pflicht-Smoke ausführen.

# Abnahmekriterien

- Alle drei Guards nutzen die gemeinsame Resolver-Utility für Markdown-Ziele.
- Fehlermeldungen referenzieren aufgelöste relative Zielpfade.
- Prozessseiten sind auf Durchlauf 164 synchronisiert.
- `bash scripts/smoke.sh` ist grün.
