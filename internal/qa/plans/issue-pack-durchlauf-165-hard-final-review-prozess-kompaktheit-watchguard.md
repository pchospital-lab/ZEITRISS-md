# Fahrplan – Durchlauf 165 (Hard-Final-Review Prozess-Kompaktheit)

## Kontext

Die Anschlussübersicht nennt als offenen Task, Prozessseiten dauerhaft schlank zu
halten. Bislang war diese Leitplanke nur dokumentiert, aber nicht als
Pflicht-Guard in der Smoke-Pipeline abgesichert.

## Ziel

- Einen maschinenlesbaren Watchguard ergänzen, der die operative Kompaktheit der
  Triage-Seiten (`known-issues.md`, `hard-final-review-next-steps.md`) absichert.
- Den neuen Guard in `scripts/smoke.sh` als Pflichtcheck verankern.
- Prozessspur für Folge-Durchläufe aktualisieren.

## Arbeitspakete

1. Neuen `tools/test_process_compactness_watchguard.js` implementieren.
2. Guard in `bash scripts/smoke.sh` aufnehmen.
3. Prozessseiten auf Durchlauf-165-Stand synchronisieren.
4. Pflicht-Smoke ausführen und Ergebnis im QA-Log dokumentieren.

## Abnahme

- `node tools/test_process_compactness_watchguard.js` liefert
  `process-compactness-watchguard-ok`.
- `bash scripts/smoke.sh` bleibt vollständig grün.
