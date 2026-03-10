---
title: "Log – Durchlauf 161 (Hard-Final-Review / Watchguard-Resolver-Rollout)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

## Kontext

Nach Durchlauf 160 lag die Resolver-Utility bereits produktiv im
Chronopolis-Guard. Als Anschlussaufgabe blieb, weitere Hard-Final-Review-
relevante Watchguards auf dieselbe Auflösung zu standardisieren.

## Umsetzung

- `tools/test_default_slot_dependency_watchguard.js` auf
  `resolveUniqueMarkdownTarget` umgestellt:
  - bevorzugter Zielpfad bleibt `characters/charaktererschaffung-grundlagen.md`;
  - Fallback-Scan über Dateinamen + Inhaltsanker (`Ordo Mnemonika`,
    `Retina-Linse`) ergänzt;
  - Drift-Fehlermeldung zeigt den aufgelösten relativen Zielpfad.
- `tools/test_hard_final_review_watchguard.js` auf Resolver-Utility
  standardisiert:
  - Save-, Cinematic- und Kampagnenziel jeweils mit preferred+fallback
    aufgelöst;
  - bestehende SSOT-Assertions inhaltlich unverändert beibehalten.
- Prozessseiten synchronisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md`

## Ergebnis

- Der Resolver-Rollout ist über den Chronopolis-Guard hinaus auf weitere
  Hard-Final-Review-Guards ausgeweitet.
- Zielpfad-Auflösung bleibt bei künftigen Datei-Umzügen robuster und
  wartungsärmer.

## Checks

- `node tools/test_default_slot_dependency_watchguard.js` erfolgreich.
- `node tools/test_hard_final_review_watchguard.js` erfolgreich.
- `bash scripts/smoke.sh` erfolgreich.
