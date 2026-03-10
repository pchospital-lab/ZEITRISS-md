# QA-Log – Durchlauf 189 (Hard-Final-Review Watchguard-Smoke-Coverage-Namensvarianten)

## Ausgangslage

`tools/test_watchguard_smoke_coverage.js` verwendete für den Scan von
Watchguard-Dateien das Pattern `^test_.*watchguard\.js$`. Damit wurden
Meta-Watchguards mit Zusatzsuffix (z. B. `test_watchguard_loader_consistency.js`
und `test_watchguard_smoke_coverage.js`) nicht als Watchguard-Dateien erfasst.

## Umsetzung

- Dateimuster in `tools/test_watchguard_smoke_coverage.js` erweitert auf
  `^test_.*watchguard(?:_.*)?\.js$`.
- Dadurch berücksichtigt der Coverage-Scan nun beide Varianten:
  - klassische Guards (`test_*watchguard.js`)
  - Guards mit Suffix (`test_*watchguard_*.js`)
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md` ergänzt um Durchlauf-189-Vermerk,
  - `internal/qa/process/hard-final-review-next-steps.md` ergänzt um den
    neuen Härtungspunkt zur Namensvarianten-Erkennung.

## Ergebnis

- Die strukturelle Smoke-Abdeckungsprüfung ist jetzt robuster gegen
  Dateinamenerweiterungen innerhalb der Watchguard-Familie.
- Meta-Watchguards mit Suffix werden künftig nicht mehr still aus der
  Coverage-Betrachtung ausgeschlossen.
- Pflicht-Smoke lief vollständig grün.

## Pflicht-Checks

- `node tools/test_watchguard_smoke_coverage.js` → `watchguard-smoke-coverage-ok`
- `bash scripts/smoke.sh` → `All smoke checks passed.`
