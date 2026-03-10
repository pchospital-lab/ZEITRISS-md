# QA-Log – Durchlauf 177 (Hard-Final-Review Watchguard Loader-Consistency-Guard)

## Ausgangslage

Nach Durchlauf 176 liefen alle relevanten Guards bereits auf dem zentralen
`watchguard_doc_loader`. Es gab jedoch noch keinen automatisierten Meta-Check,
der zukünftige Einführungen lokaler Resolver-Helfer direkt im Smoke stoppt.

## Umsetzung

- Neuer Guard `tools/test_watchguard_loader_consistency.js` hinzugefügt.
- Guard scannt alle `tools/test_*watchguard.js` (außer sich selbst) und prüft:
  - kein direkter Import von `watchguard_file_resolver`
  - kein direkter Aufruf von `resolveUniqueMarkdownTarget(...)`
  - verpflichtende Nutzung von `createDocTextLoader`
  - kein direkter `readFileSync(... .md ...)`-Zugriff in Watchguard-Tests
- `scripts/smoke.sh` erweitert um den Pflichtlauf des neuen Guards:
  - `node tools/test_watchguard_loader_consistency.js`
  - `grep "watchguard-loader-consistency-ok" ...`
- Beim Erstlauf meldete der neue Guard einen False-Positive auf
  `test_onboarding_start_save_watchguard.js` (generisches Muster für
  `readFileSync` + `.md` in derselben Datei).
- Prüfmuster im neuen Guard auf echten Direktlese-Aufruf
  `readFileSync(... .md ...)` präzisiert; danach finaler Smoke-Lauf grün.

## Ergebnis

- Der Loader-Standard ist jetzt durch einen eigenen Watchguard dauerhaft im
  Pflicht-Smoke verankert.
- Neue/angepasste Watchguards, die wieder lokale Resolver-Duplikate einführen,
  fallen künftig sofort auf.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
