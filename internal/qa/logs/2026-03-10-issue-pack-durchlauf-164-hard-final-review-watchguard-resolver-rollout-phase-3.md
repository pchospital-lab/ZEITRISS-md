---
title: "Log – Durchlauf 164 (Hard-Final-Review / Watchguard-Resolver-Rollout Phase 3)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

## Kontext

Nach dem Resolver-Rollout in den Durchläufen 160–163 verblieben noch
Hard-Final-Review-nahe Watchguards mit direktem Datei-Lookup für
Markdown-Ziele. Diese Insellösungen sollten für robustere Pfadauflösung auf
die gemeinsame Utility gehärtet werden.

## Umsetzung

- `tools/test_ruf_alien_watchguard.js` auf
  `resolveUniqueMarkdownTarget` portiert.
- `tools/test_physicality_watchguard.js` auf
  `resolveUniqueMarkdownTarget` portiert.
- `tools/test_kausalabfang_watchguard.js` auf
  `resolveUniqueMarkdownTarget` portiert.
- Fehlermeldungen zeigen bei den portierten Guards nun den aufgelösten
  relativen Zielpfad.
- Prozessseiten synchronisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md`

## Ergebnis

Der Resolver-Rollout deckt nun auch Ruf/Alien-, Physicality- und
Kausalabfang-Hardening-Guards ab. Damit sinkt der Pflegeaufwand bei künftigen
Pfadänderungen in den Runtime-Markdown-Zielen.

## Checks

- `node tools/test_ruf_alien_watchguard.js` erfolgreich.
- `node tools/test_physicality_watchguard.js` erfolgreich.
- `node tools/test_kausalabfang_watchguard.js` erfolgreich.
- `bash scripts/smoke.sh` erfolgreich.
