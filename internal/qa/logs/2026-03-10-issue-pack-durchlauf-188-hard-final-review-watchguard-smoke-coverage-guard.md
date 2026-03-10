# QA-Log – Durchlauf 188 (Hard-Final-Review Watchguard-Smoke-Coverage-Guard)

## Ausgangslage

Der bestehende Meta-Guard `test_watchguard_loader_consistency.js` erzwingt
Loader-/Label-/Token-Standards innerhalb einzelner Watchguard-Dateien. Nicht
abgesichert war bisher, ob jede Watchguard-Datei auch tatsächlich in
`scripts/smoke.sh` als Pflichtcheck ausgeführt wird.

## Umsetzung

- Neuer Meta-Guard `tools/test_watchguard_smoke_coverage.js` ergänzt:
  - liest alle `tools/test_*watchguard.js`,
  - extrahiert die in `scripts/smoke.sh` ausgeführten Watchguards,
  - meldet Violations für fehlende, stale oder doppelte Smoke-Referenzen.
- `scripts/smoke.sh` erweitert:
  - neuer Pflichtschritt `node tools/test_watchguard_smoke_coverage.js`,
  - Grep-Anker auf `watchguard-smoke-coverage-ok`.
- `internal/qa/process/watchguard-neuanlage-checkliste.md` geschärft:
  - Smoke-Aufnahme ist weiterhin Pflicht,
  - Hinweis ergänzt, dass die Coverage automatisch vom Meta-Guard geprüft wird.
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md` um Durchlauf-188-Hinweis ergänzt,
  - `internal/qa/process/hard-final-review-next-steps.md` um den neuen
    Coverage-Härtungspunkt erweitert.

## Ergebnis

- Watchguard-Neuanlagen sind jetzt nicht nur über Konventionen,
  sondern auch über einen strukturellen Smoke-Coverage-Check abgesichert.
- Fehlende oder veraltete Watchguard-Einbindungen in `scripts/smoke.sh`
  werden frühzeitig und eindeutig sichtbar.
- Pflicht-Smoke lief vollständig grün.

## Pflicht-Checks

- `node tools/test_watchguard_smoke_coverage.js` → `watchguard-smoke-coverage-ok`
- `bash scripts/smoke.sh` → `All smoke checks passed.`
