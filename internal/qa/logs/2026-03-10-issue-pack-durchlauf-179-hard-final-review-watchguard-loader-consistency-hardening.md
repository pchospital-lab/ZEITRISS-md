# QA-Log – Durchlauf 179 (Hard-Final-Review Watchguard-Loader-Consistency Hardening)

## Ausgangslage

Der neue Meta-Guard aus Durchlauf 177 erzwingt den zentralen
`watchguard_doc_loader`-Standard für alle `test_*watchguard.js`.
Beim gezielten Nachschärfen zeigte sich, dass der bestehende Regex für direkte
`.md`-Direktlese nicht alle multiline-Varianten gleich robust abdeckt.
Außerdem sollte die Guard-Regel klarstellen, dass die Loader-API auch real
verwendet wird (nicht nur der Import von `createDocTextLoader`).

## Umsetzung

- `tools/test_watchguard_loader_consistency.js` gehärtet:
  - neuen Helper `hasDirectMarkdownReadFileSync(text)` ergänzt,
  - multiline-sichere Erkennung für direkte `readFileSync(... .md ...)`
    implementiert,
  - zusätzliche Regel eingeführt: Watchguards müssen mindestens eine
    zentrale Loader-Lese-API nutzen (`readMarkdown(...)` oder
    `getDocText(...)`).
- Guard unmittelbar verifiziert:
  - Erstlauf deckte erwartungsgemäß eine zu strenge Zwischenregel auf
    (`test_onboarding_start_save_watchguard.js` nutzt legitimerweise
    `getDocText` statt `readMarkdown`),
  - Regel auf „`readMarkdown` **oder** `getDocText`“ korrigiert.

## Ergebnis

- `node tools/test_watchguard_loader_consistency.js` läuft grün
  (`watchguard-loader-consistency-ok`).
- Pflicht-Smoke grün:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
- Prozessspur auf Durchlauf-179-Stand aktualisiert (`known-issues.md` und
  `hard-final-review-next-steps.md`).
