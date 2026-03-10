# Fahrplan – Durchlauf 169 (Hard-Final-Review ITI-Watchguard Markdown-Resolver-Rollout)

## Kontext

Die vorherigen Durchläufe haben den Resolver-Standard breit ausgerollt. Im
`iti-hardcanon-watchguard` wurden einige Prüfpfade weiterhin direkt per
Dateipfad gelesen (`fs.readFileSync`), wodurch Umzüge/Varianten im
Markdown-Zielpfad weniger robust abgesichert waren als in den übrigen
Watchguards.

## Ziel

- `iti-hardcanon-watchguard` auf denselben Resolver-Standard bringen wie die
  übrigen Hard-Final-Review-Guards.
- Alle Slot-Textprüfungen über eine konsolidierte Markdown-Zielauflösung führen,
  damit Drift-Checks bei Datei-Umzügen robust bleiben.
- Anschlussfähigkeit über Plan/Log/Prozessseiten für Folge-Durchläufe sichern.

## Arbeitspakete

1. `tools/test_iti_hardcanon_watchguard.js` um Resolver-gestützte
   `getDocText`-Logik mit Cache ergänzen.
2. Direktlese-Pfade für slot-basierte Markdown-Prüfungen auf die neue
   Resolver-Logik umstellen.
3. Pflicht-Smoke (`bash scripts/smoke.sh`) ausführen und Ergebnis loggen.
4. `known-issues.md` und Anschlussübersicht auf Durchlauf-169-Stand nachziehen.

## Abnahme

- `bash scripts/smoke.sh` vollständig grün.
- `iti-hardcanon-watchguard` liest Markdown-Dateien im Slot-Durchlauf über die
  Resolver-Logik statt über direkte Dateipfade.
