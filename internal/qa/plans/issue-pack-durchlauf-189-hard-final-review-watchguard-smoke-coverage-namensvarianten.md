# Fahrplan – Durchlauf 189 (Hard-Final-Review Watchguard-Smoke-Coverage-Namensvarianten)

## Kontext

Der Coverage-Guard `tools/test_watchguard_smoke_coverage.js` prüft die
Smoke-Einbindung von Watchguards, erkannte bisher aber nur Dateinamen mit
Suffix `...watchguard.js`. Meta-Watchguards mit erweitertem Suffix
(`...watchguard_*.js`) fielen aus dem Scan.

## Ziel

- Dateinamen-Pattern im Coverage-Guard so erweitern, dass auch
  `test_*watchguard_*.js` erfasst werden.
- Sicherstellen, dass die Smoke-Abdeckungsprüfung weiterhin eindeutig und
  regressionssicher bleibt.
- Prozess-/QA-Spur auf Durchlauf 189 fortführen.

## Arbeitspakete

1. `tools/test_watchguard_smoke_coverage.js` auf erweitertes
   Watchguard-Dateinamenmuster anpassen.
2. Guard direkt ausführen und auf Erfolgstoken prüfen.
3. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
4. Prozessseiten (`known-issues.md`, `hard-final-review-next-steps.md`)
   auf Durchlauf 189 synchronisieren.

## Abnahme

- Coverage-Guard erkennt sowohl `test_*watchguard.js` als auch
  `test_*watchguard_*.js`.
- `node tools/test_watchguard_smoke_coverage.js` meldet
  `watchguard-smoke-coverage-ok`.
- `bash scripts/smoke.sh` läuft vollständig grün.
