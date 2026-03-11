# Fahrplan – Durchlauf 205 (Chronopolis SL-Referenz Contract Sync)

## Kontext

Die Chronopolis-Härtung aus Durchlauf 203/204 ist in Spieler-Handbuch,
Masterprompt und Kampagnenstruktur sauber verankert. In
`core/sl-referenz.md` stand jedoch weiterhin die ältere Lesart
„ohne Missionsdruck“, die Chronopolis eher wie einen lockeren Stadthub als
reaktiven Infiltrationslauf rahmt.

## Ziel

- Chronopolis-Wording in `core/sl-referenz.md` auf den gehärteten
  Play-Contract synchronisieren (freier Infiltrationslauf statt Freizeit-Hub).
- Anschlussfähigkeit im QA-Prozess mit neuem Fahrplan/Log und
  Prozessspiegel nachziehen.

## Arbeitspakete

1. Runtime-SSOT-Wording:
   - `core/sl-referenz.md` (Chronopolis-Stimmungswechsel/Funktion)
2. QA/Prozess-Spiegel:
   - Neuer Log unter `internal/qa/logs/`
   - Ergänzungen in
     `internal/qa/process/hard-final-review-next-steps.md` und
     `internal/qa/process/known-issues.md` (ZR-021)
3. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- `core/sl-referenz.md` nutzt im Chronopolis-Block den gleichen Contract wie
  die bereits gehärteten SSOT-Module (Infiltrationslauf + Reaktionsdruck).
- Prozessdokumente enthalten den Durchlauf 205 als Anschlussstand.
- Pflicht-Smoke und Link-Lint laufen ohne Fehler.
