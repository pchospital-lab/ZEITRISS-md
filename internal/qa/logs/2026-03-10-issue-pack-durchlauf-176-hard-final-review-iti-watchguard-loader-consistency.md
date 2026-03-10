# QA-Log – Durchlauf 176 (Hard-Final-Review ITI-Watchguard Loader-Consistency)

## Ausgangslage

Der zentrale `watchguard_doc_loader` war bereits eingeführt, jedoch nutzte der
`iti-hardcanon-watchguard` in Teilen weiterhin einen lokalen Resolver-Helfer.
Dadurch blieb vermeidbare Duplikatlogik im Guard bestehen.

## Umsetzung

- `tools/test_iti_hardcanon_watchguard.js` konsolidiert:
  - Loader-API auf `readText`, `getDocText` und `readMarkdown` erweitert.
  - Lokalen Resolver-Import (`watchguard_file_resolver`) entfernt.
  - Lokale Funktion `resolveMarkdownTarget(...)` entfernt.
  - SSOT-Scans (Atlas + Kernpersonal) auf `readMarkdown(...)` umgestellt.
- Fachliche Assertions (ITI-Atlasanker, Kernpersonal, Drift-/Alias-Verbote)
  unverändert belassen.
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md`
  - `internal/qa/process/hard-final-review-next-steps.md`

## Ergebnis

- Der `iti-hardcanon-watchguard` folgt jetzt ohne Rest-Duplikatlogik dem
  zentralen Loader-Standard.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
