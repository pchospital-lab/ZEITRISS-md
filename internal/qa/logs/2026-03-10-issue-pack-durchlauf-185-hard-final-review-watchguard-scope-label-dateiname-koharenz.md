# QA-Log – Durchlauf 185 (Hard-Final-Review Scope-Label-Dateiname-Kohärenz)

## Ausgangslage

Die bestehenden Meta-Guard-Regeln deckten syntaktische Labelqualität gut ab
(`scopeLabel` vorhanden, Suffix `Watchguard`, keine Slashes), jedoch nicht die
semantische Zuordnung zum jeweiligen Guard-Dateinamen.

## Umsetzung

- `tools/test_watchguard_loader_consistency.js` erweitert:
  - `normalizeLabelToken(...)` ergänzt (vereinheitlicht Vergleichswerte),
  - `expectedScopeLabelTokenFromFilename(...)` ergänzt,
  - neue Verstoßregel: normalisiertes `scopeLabel` muss dem normalisierten
    Dateinamen-Token entsprechen.
- Befund aus Erstlauf behoben:
  - `tools/test_chronopolis_gate_watchguard.js` Label von
    `Chronopolis-Watchguard` auf `Chronopolis-Gate-Watchguard` angehoben,
    inklusive Label-String beim Markdown-Read.
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md` auf Durchlauf-185-Stand ergänzt,
  - `internal/qa/process/hard-final-review-next-steps.md` um den 185er
    Kohärenzschritt erweitert.

## Ergebnis

- Der neue Meta-Guard erkennt Label-Dateiname-Drift reproduzierbar.
- Nach Label-Angleichung lief der Pflicht-Smoke vollständig grün.
- Diagnose in Smoke-/CI-Logs ist konsistenter, weil Guard-Name und
  `scopeLabel` jetzt denselben semantischen Anker tragen.

## Pflicht-Checks

- `node tools/test_watchguard_loader_consistency.js` →
  `watchguard-loader-consistency-ok`
- `bash scripts/smoke.sh` → `All smoke checks passed.`
