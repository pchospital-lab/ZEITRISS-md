# Fahrplan – Durchlauf 206 (Chronopolis Dev-Blueprint Contract Sync)

## Kontext

Die Chronopolis-Contract-Härtung ist in den Runtime-SSOTs und der SL-Referenz
bereits konsistent. In der Dev-Dokumentation `docs/dev/chronopolis-map-blueprint.md`
blieb jedoch im Schlussabsatz noch die ältere Benennung „Endgame-Hub“ stehen.
Das erzeugt Lesedrift zwischen Dev-Referenz und gehärtetem Spielmodus.

## Ziel

- Dev-Blueprint-Wording auf den gehärteten Chronopolis-Contract synchronisieren
  (freier Infiltrationslauf statt Endgame-Hub).
- Anschlussfähigkeit im QA-Prozess mit Fahrplan/Log und Prozessspiegel sichern.

## Arbeitspakete

1. Dev-Dokumentation synchronisieren:
   - `docs/dev/chronopolis-map-blueprint.md`
2. QA/Prozess-Spiegel aktualisieren:
   - Neuer Log unter `internal/qa/logs/`
   - Ergänzungen in
     `internal/qa/process/hard-final-review-next-steps.md` und
     `internal/qa/process/known-issues.md` (ZR-021)
3. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- `docs/dev/chronopolis-map-blueprint.md` nutzt keine Endgame-Hub-Lesart mehr,
  sondern verweist auf den Chronopolis-Spielmodus als freien
  Infiltrationslauf.
- Prozessdokumente enthalten Durchlauf 206 als Anschlussstand.
- Pflicht-Smoke und Link-Lint laufen ohne Fehler.
