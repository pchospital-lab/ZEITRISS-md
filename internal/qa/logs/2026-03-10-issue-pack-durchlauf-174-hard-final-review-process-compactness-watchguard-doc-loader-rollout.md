# QA-Log – Durchlauf 174 (Hard-Final-Review Process-Compactness-Watchguard Doc-Loader-Rollout)

## Ausgangslage

Nach den Rollouts 171–173 war der `tools/test_process_compactness_watchguard.js`
noch auf direkte Resolver-Aufrufe (`resolveUniqueMarkdownTarget`) aufgebaut.
Fachlich war der Guard korrekt, aber der Loader-Standard war nicht vollständig
vereinheitlicht.

## Umsetzung

- `tools/test_process_compactness_watchguard.js` auf
  `createDocTextLoader` aus `tools/watchguard_doc_loader.js` umgestellt.
- Direkte Resolver-Aufrufe entfernt; stattdessen
  `readMarkdown(relPath, anchors, label)` aus dem zentralen Loader genutzt.
- Guard-Regeln/Assertions unverändert gelassen (Zeilenbudget,
  Archiv-/Prozessverweise, Pflicht-Smoke-Anker).
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md`
  - `internal/qa/process/hard-final-review-next-steps.md`

## Ergebnis

- Der `process-compactness-watchguard` folgt jetzt ebenfalls dem zentralen
  Resolver-/Loader-Standard.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
