# Fahrplan – Durchlauf 203 (Chronopolis Play-Contract Härtung)

## Kontext

Chronopolis ist bereits als gescheiterte Episodenzeitlinie mit klaren
Risiken verankert, wirkt im Play-Contract aber noch zu diffus. Für
Spielende und KI-SL soll klarer lesbar werden: Chronopolis ist ein freier
Infiltrationslauf mit reaktiver Stadtlogik und seltener Apex-Bedrohung,
nicht ein entspannter Stadt-Hub.

## Ziel

- Spielerseitigen Merksatz für Chronopolis als Infiltrationsmodus ergänzen.
- Regie-Contract im Masterprompt auf Modus + Reaktionslogik schärfen.
- Runtime-Leitplanken in Modul 6 um klare Reaktions- und Apex-Regeln erweitern.
- Anschlussfähigkeit über QA-Log und Prozessseiten dokumentieren.

## Arbeitspakete

1. WS-Änderungen:
   - `core/spieler-handbuch.md`
   - `meta/masterprompt_v6.md`
   - `gameplay/kampagnenstruktur.md`
2. QA/Prozess-Spiegel:
   - Neuer Log unter `internal/qa/logs/`
   - Ergänzungen in
     `internal/qa/process/hard-final-review-next-steps.md` und
     `internal/qa/process/known-issues.md` (ZR-021)
3. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- Chronopolis ist als freier Infiltrationslauf in allen drei Runtime-SSOT-
  Ebenen eindeutig lesbar (Spieler-Handbuch, Masterprompt, Kampagnenstruktur).
- Reaktionslogik „genau ein Beat pro bedeutsamer Aktion“ ist als Regie-Default
  explizit dokumentiert.
- Apex-Bedrohung ist als selten/optional und bevorzugt am Exit-Rückweg
  verankert.
- Pflicht-Smoke und Link-Lint laufen ohne Fehler.
