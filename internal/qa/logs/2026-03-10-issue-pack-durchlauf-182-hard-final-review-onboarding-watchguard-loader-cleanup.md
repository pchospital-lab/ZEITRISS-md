# QA-Log – Durchlauf 182 (Hard-Final-Review Onboarding-Watchguard Loader-Cleanup)

## Ausgangslage

Der Onboarding-Watchguard war bereits auf `createDocTextLoader(...)`
angebunden, enthielt jedoch noch lokale Wrapper (`getDocText`) und eine eigene
Dateilese-Funktion für JSON (`readText` via `fs.readFileSync`).

## Umsetzung

- `tools/test_onboarding_start_save_watchguard.js` bereinigt:
  - lokale `fs`-Abhängigkeit entfernt,
  - lokale Helfer `readText(...)` und Wrapper `getDocText(...)` entfernt,
  - direkte Nutzung von `readText` und `getDocText` aus
    `createDocTextLoader(...)` eingeführt.
- Prozess-/Anschlussdokumentation synchronisiert:
  - `internal/qa/process/known-issues.md` auf Durchlauf-182-Stand referenziert,
  - `internal/qa/process/hard-final-review-next-steps.md` um den 182er
    Cleanup-Schritt ergänzt.

## Ergebnis

- Onboarding-Watchguard folgt jetzt ohne lokale Duplikat-Helfer dem zentralen
  Loader-Standard.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
