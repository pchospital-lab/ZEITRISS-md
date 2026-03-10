# QA-Log – Durchlauf 171 (Hard-Final-Review Watchguard-Doc-Loader-Standardisierung)

## Ausgangslage

Nach den Resolver-Rollout-Durchläufen (bis 170) war die Fachlogik stabil,
aber die technische Umsetzung der Markdown-Lesehelfer in mehreren Guards
noch redundant. Das erhöhte Pflegeaufwand und Patch-Risiko bei kleinen
Anpassungen am Resolver-Verhalten.

## Umsetzung

- Neues Utility `tools/watchguard_doc_loader.js` eingeführt:
  - `createDocTextLoader({ root, scopeLabel })`
  - `readText(relPath)` für Direktlese (Nicht-Markdown)
  - `readMarkdown(...)` mit `resolveUniqueMarkdownTarget`
  - `getDocText(...)` mit Cache für `.md`
- Umstellung auf das Utility:
  - `tools/test_iti_hardcanon_watchguard.js`
  - `tools/test_npc_continuity_consistency.js`
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md`
  - `internal/qa/process/hard-final-review-next-steps.md`

## Ergebnis

- Die betroffenen Hard-Final-Review-Guards verwenden jetzt denselben
  zentralen Loader-Standard statt kopierter Helferblöcke.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
