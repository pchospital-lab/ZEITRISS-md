# QA-Log – Durchlauf 187 (Hard-Final-Review Watchguard-OK-Token-Kohärenz)

## Ausgangslage

Die Neuanlage-Checkliste verlangte bereits ein `...-ok`-Token, jedoch ohne
harte technische Durchsetzung gegen Dateiname-Drift. Damit blieb ein kleiner,
aber relevanter Raum für inkonsistente Smoke-Grep-Ausgaben.

## Umsetzung

- `tools/test_watchguard_loader_consistency.js` erweitert:
  - `expectedOkTokenFromFilename(...)` ergänzt,
  - `hasExpectedOkToken(...)` ergänzt,
  - neue Violation eingeführt, wenn das erwartete Ergebnis-Token nicht per
    `console.log(...)` ausgegeben wird.
- `internal/qa/process/watchguard-neuanlage-checkliste.md` geschärft:
  - Pflichtschritt zum `...-ok`-Token jetzt mit explizitem
    Dateiname→Token-Beispiel.
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md` um Durchlauf-187-Hinweis ergänzt,
  - `internal/qa/process/hard-final-review-next-steps.md` um den neuen
    Meta-Guard-Härtungspunkt erweitert.

## Ergebnis

- Der Meta-Guard deckt nun auch Ergebnis-Token-Drift ab und härtet damit die
  Smoke-Kohärenz über alle Watchguards hinweg.
- Maintainer haben in der Neuanlage-Checkliste eine eindeutigere
  Formulierungs- und Benennungsregel.
- Pflicht-Smoke lief vollständig grün.

## Pflicht-Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
