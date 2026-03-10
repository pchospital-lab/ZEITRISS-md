# QA-Log – Durchlauf 175 (Hard-Final-Review Watchguard-Doc-Loader-Rollout Restguards)

## Ausgangslage

Der zentrale `watchguard_doc_loader` war bereits in mehreren Guards produktiv,
aber einzelne Hard-Final-Review-Watchguards nutzten weiterhin direkte
Resolver-Aufrufe. Dadurch blieb unnötige Duplikatlogik in den Tests.

## Umsetzung

- Auf `createDocTextLoader(...).readMarkdown(...)` umgestellt:
  - `tools/test_chronopolis_gate_watchguard.js`
  - `tools/test_default_slot_dependency_watchguard.js`
  - `tools/test_hard_final_review_watchguard.js`
  - `tools/test_kausalabfang_watchguard.js`
  - `tools/test_physicality_watchguard.js`
  - `tools/test_ruf_alien_watchguard.js`
  - `tools/test_upload_snapshot_watchguard.js`
- Fachliche Assertions und Driftmuster-Prüfungen in allen Guards unverändert
  belassen.
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md`
  - `internal/qa/process/hard-final-review-next-steps.md`

## Ergebnis

- Die verbleibenden Hard-Final-Review-Restguards folgen jetzt ebenfalls dem
  zentralen Loader-Standard.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
