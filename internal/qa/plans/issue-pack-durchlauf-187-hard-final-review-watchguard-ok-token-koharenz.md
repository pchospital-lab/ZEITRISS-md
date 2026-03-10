# Fahrplan – Durchlauf 187 (Hard-Final-Review Watchguard-OK-Token-Kohärenz)

## Kontext

Der zentrale Loader-/Label-Meta-Guard ist etabliert, aber das erwartete
`...-ok`-Ergebnis-Token war bisher nur als Prozessregel dokumentiert und nicht
als technische Pflichtprüfung im Meta-Guard verankert.

## Ziel

- Smoke-/Grep-Kohärenz für alle `test_*watchguard.js` technisch absichern.
- Sicherstellen, dass jeder Watchguard genau das erwartete `...-ok`-Token
  passend zum Dateinamen ausgibt.
- QA-/Prozessspur auf Durchlauf-187-Stand fortführen.

## Arbeitspakete

1. `tools/test_watchguard_loader_consistency.js` um eine Regel erweitern, die
   pro Guard das erwartete `...-ok`-Token aus dem Dateinamen ableitet und gegen
   `console.log(...)` prüft.
2. `internal/qa/process/watchguard-neuanlage-checkliste.md` um die
   Dateiname→Token-Regel konkretisieren.
3. Prozessseiten (`known-issues.md`, `hard-final-review-next-steps.md`) auf
   Durchlauf 187 synchronisieren.
4. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).

## Abnahme

- Meta-Guard meldet bei Token-Drift einen Verstoß.
- Checkliste enthält die explizite Dateiname→Token-Regel.
- Prozessseiten verweisen auf Durchlauf 187.
- `bash scripts/smoke.sh` läuft vollständig grün.
