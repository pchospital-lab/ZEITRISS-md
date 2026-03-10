# QA-Log – Durchlauf 181 (Hard-Final-Review Watchguard Scope-Label Guard)

## Ausgangslage

Die Loader-Konsistenz war bereits gut abgesichert (kein lokaler Resolver,
keine `.md`-Direktlese, Pflichtnutzung von `readMarkdown/getDocText`). Der
`scopeLabel` als Debug-/Kontextanker im Loader war jedoch noch nicht als harte
Pflicht im Meta-Guard verankert.

## Umsetzung

- `tools/test_watchguard_loader_consistency.js` erweitert:
  - neuer Helper `hasScopeLabelOnLoader(text)` ergänzt,
  - neue Pflichtregel hinzugefügt: jedes `test_*watchguard.js` muss im
    `createDocTextLoader(...)` einen nichtleeren `scopeLabel` setzen.
- Prozess-/Anschlussdokumentation synchronisiert:
  - `internal/qa/process/known-issues.md` auf Durchlauf-181-Stand referenziert,
  - `internal/qa/process/hard-final-review-next-steps.md` um den 181er
    Stabilisierungsschritt ergänzt.

## Ergebnis

- Loader-Standard ist regressionssicher um den `scopeLabel`-Anker erweitert.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
