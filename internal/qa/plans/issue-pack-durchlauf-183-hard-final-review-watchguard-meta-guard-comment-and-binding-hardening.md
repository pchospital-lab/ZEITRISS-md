# Fahrplan – Durchlauf 183 (Hard-Final-Review Watchguard Meta-Guard Härtung)

## Kontext

Der Meta-Guard `tools/test_watchguard_loader_consistency.js` prüft den
Loader-Standard bereits breit. Zwei Restschwächen blieben jedoch offen:

- reine Kommentar-Treffer konnten einzelne Regex-Regeln fälschlich erfüllen,
- die API-Pflicht prüfte bisher nur Aufrufe (`readMarkdown/getDocText`), aber
  nicht, ob diese APIs auch direkt aus `createDocTextLoader(...)` gebunden sind.

## Ziel

- Kommentar-Drift aus der Meta-Guard-Erkennung ausschließen.
- Loader-API-Bindung (Destructuring aus `createDocTextLoader(...)`) als
  explizite Pflicht ergänzen.
- Prozess- und QA-Spur auf Durchlauf-183-Stand fortführen.

## Arbeitspakete

1. `tools/test_watchguard_loader_consistency.js` um Comment-Stripping für die
   statischen Prüfungen ergänzen.
2. Zusätzliche Pflichtregel einführen: jede Guard-Datei bindet mindestens eine
   Loader-Lese-API (`readMarkdown/getDocText/readText`) direkt aus
   `createDocTextLoader(...)`.
3. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
4. QA-Log für Durchlauf 183 dokumentieren.
5. Prozessübersichten (`known-issues.md` + Anschlussübersicht) synchron
   aktualisieren.

## Abnahme

- Meta-Guard ignoriert Kommentare bei Pattern-Prüfungen.
- Meta-Guard schlägt fehl, wenn Loader-Lese-APIs nicht direkt aus
  `createDocTextLoader(...)` gebunden sind.
- `bash scripts/smoke.sh` läuft vollständig grün.
- Plan/Log/Prozessseiten sind auf Durchlauf-183-Stand anschlussfähig.
