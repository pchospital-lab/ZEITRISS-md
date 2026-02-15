# Security Policy

## Supported Versions

Aktiver Support erfolgt für den jeweils aktuellen Stand auf `main`.

## Vulnerability Reporting

Bitte melde sicherheitsrelevante Funde **nicht öffentlich** im normalen
Issue-Tracker, wenn eine unmittelbare Ausnutzung möglich ist.

- Kontakt: `chrononaut@zeitriss.org`
- Betreff-Vorschlag: `SECURITY: <kurze Beschreibung>`
- Erwünschte Angaben: betroffene Datei/Funktion, Reproduktionsschritte,
  erwartetes vs. tatsächliches Verhalten, potenzieller Impact.

## Disclosure

- Eingänge werden so schnell wie möglich triagiert.
- Nach Bestätigung wird ein Fix priorisiert und im Changelog/Release-Hinweis
  transparent dokumentiert.
- Bitte gib angemessen Zeit für Behebung, bevor technische Details öffentlich
  geteilt werden.


## Key-Notfallpfad

Wenn ein API-Key versehentlich im Repo oder in einem öffentlichen Paste landet:

1. Key sofort beim Provider rotieren oder widerrufen.
2. Betroffene Datei/Commit bereinigen.
3. Falls bereits gepusht: History-Cleanup durchführen und den Vorfall intern
   dokumentieren.
4. Danach Secret-Scanning und Push-Protection im Ziel-Repo prüfen.

Siehe ergänzend: `docs/setup-guide.md` (Abschnitt
"Key-Notfallpfad (wenn versehentlich committed)").
