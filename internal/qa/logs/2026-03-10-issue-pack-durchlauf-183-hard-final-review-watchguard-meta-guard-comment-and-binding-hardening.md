# QA-Log – Durchlauf 183 (Hard-Final-Review Watchguard Meta-Guard Härtung)

## Ausgangslage

Der zentrale Loader-Standard war bereits etabliert, aber der Meta-Guard ließ
noch zwei Lücken zu:

1. Kommentierte Textfragmente konnten Regex-Regeln theoretisch „schein-erfüllen“.
2. Es wurde nicht explizit erzwungen, dass `readMarkdown/getDocText/readText`
   direkt aus `createDocTextLoader(...)` gebunden sind.

## Umsetzung

- `tools/test_watchguard_loader_consistency.js` gehärtet:
  - neuer Helper `stripJsComments(text)` entfernt Block- und Zeilenkommentare
    vor den statischen Pattern-Prüfungen,
  - neue Regel `hasLoaderApiBinding(text)` ergänzt und als Pflicht aktiviert,
  - bestehende API-Nutzungsregel auf `readMarkdown/getDocText/readText`
    erweitert,
  - Prüfungen auf Resolver-/Loader-Drift laufen jetzt gegen den bereinigten
    Code-Text statt gegen Rohtext.
- Prozess-/Anschlussdokumentation synchronisiert:
  - `internal/qa/process/known-issues.md` auf Durchlauf-183-Stand referenziert,
  - `internal/qa/process/hard-final-review-next-steps.md` um den 183er
    Härtungsschritt ergänzt.

## Ergebnis

- Meta-Guard ist robuster gegen Kommentar-bedingte False-Positives.
- Direkte Loader-API-Bindung aus `createDocTextLoader(...)` ist als
  regressionssichere Pflicht verankert.
- Pflicht-Checks erfolgreich:
  - `node tools/test_watchguard_loader_consistency.js`
    → `watchguard-loader-consistency-ok`
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
