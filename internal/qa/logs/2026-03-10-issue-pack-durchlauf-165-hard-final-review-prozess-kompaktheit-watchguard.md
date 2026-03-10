# QA-Log – Durchlauf 165 (Hard-Final-Review Prozess-Kompaktheit)

## Ausgangslage

Die Hard-Final-Review-Anschlussübersicht führte weiterhin den offenen
Prozess-Task „Prozessseiten weiter schlank halten“. Es fehlte noch eine
automatisierte Smoke-Absicherung, damit die Kompaktheit der Triage-Seiten nicht
wieder regressiert.

## Umsetzung

- Neuer Guard `tools/test_process_compactness_watchguard.js` ergänzt.
  - Auflösung der Zieldateien über `resolveUniqueMarkdownTarget`
    (preferred + fallback-scan).
  - Prüft Pflichtanker in `known-issues.md` und
    `hard-final-review-next-steps.md`.
  - Enthält Zeilenbudget-Checks für beide Prozessseiten, damit operative
    Kompaktheit maschinenlesbar bleibt.
- `scripts/smoke.sh` um den Pflichtcheck ergänzt:
  - Ausgabe-Token `process-compactness-watchguard-ok`.
- Prozessseiten synchronisiert:
  - `internal/qa/process/hard-final-review-next-steps.md` um Durchlauf-165-Stand
    ergänzt.
  - `internal/qa/process/known-issues.md` (ZR-021-Notiz) um Durchlauf-165-Hinweis
    ergänzt.

## Ergebnis

- Einzeltest erfolgreich: `process-compactness-watchguard-ok`.
- Pflicht-Smoke erfolgreich: `bash scripts/smoke.sh` meldet
  „All smoke checks passed.“
- Anschlussläufe haben nun einen verbindlichen Smoke-Guard gegen
  Prozessseiten-Aufblähung.
