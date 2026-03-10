# Fahrplan – Durchlauf 177 (Hard-Final-Review Watchguard Loader-Consistency-Guard)

## Kontext

Die Resolver-/Loader-Umstellung der Hard-Final-Review-Watchguards ist bis
Durchlauf 176 fachlich abgeschlossen. Um künftige Regressionen bei neuen Guards
zu verhindern, fehlte noch ein eigener Meta-Guard, der den Standard dauerhaft
im Smoke erzwingt.

## Ziel

- Einen zentralen Konsistenz-Guard ergänzen, der alle `test_*watchguard.js`
  auf den Loader-Standard überprüft.
- Direkte Resolver-Aufrufe (`watchguard_file_resolver` /
  `resolveUniqueMarkdownTarget`) in Watchguards künftig automatisch blockieren.
- Guard als Pflichtteil in `scripts/smoke.sh` verankern.
- QA-/Prozessspur auf Durchlauf-177-Stand synchronisieren.

## Arbeitspakete

1. Neuen Test `tools/test_watchguard_loader_consistency.js` erstellen.
2. Prüflogik auf alle Watchguard-Tests anwenden (mit Selbst-Ausschluss des
   neuen Guards).
3. Neuen Guard in `scripts/smoke.sh` aufnehmen.
4. Pflicht-Smoke laufen lassen.
5. Plan/Log/Prozessseiten aktualisieren.

## Abnahme

- `node tools/test_watchguard_loader_consistency.js` meldet
  `watchguard-loader-consistency-ok`.
- `bash scripts/smoke.sh` vollständig grün.
- Prozessseiten dokumentieren den neuen Watchguard als Regressionsanker.
