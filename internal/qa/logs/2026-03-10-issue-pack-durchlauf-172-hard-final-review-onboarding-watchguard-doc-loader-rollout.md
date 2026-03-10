# QA-Log – Durchlauf 172 (Hard-Final-Review Onboarding-Watchguard Doc-Loader-Rollout)

## Ausgangslage

Der neue zentrale `watchguard_doc_loader` war eingeführt, aber
`tools/test_onboarding_start_save_watchguard.js` führte weiterhin lokale
Hilfslogik für Markdown-Auflösung und Caching. Das war funktional korrekt,
erhöhte aber Wartungsaufwand und Drift-Risiko bei künftigen Resolver-Änderungen.

## Umsetzung

- `tools/test_onboarding_start_save_watchguard.js` auf
  `createDocTextLoader` umgestellt.
- Lokale Helfer für resolver-basiertes Markdown-Lesen und lokales Cache-Mapping
  entfernt.
- Bestehende Guard-Regeln und Assertions unverändert belassen;
  nur die Dokument-Ladeebene wurde standardisiert.
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md`
  - `internal/qa/process/hard-final-review-next-steps.md`

## Ergebnis

- Der Onboarding-Start-Save-Watchguard verwendet nun den gleichen Loader-Standard
  wie bereits umgestellte Hard-Final-Review-Guards.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
