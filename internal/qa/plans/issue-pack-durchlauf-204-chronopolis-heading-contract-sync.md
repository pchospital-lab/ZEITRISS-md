# Fahrplan – Durchlauf 204 (Chronopolis Heading/Contract Sync)

## Kontext

Durchlauf 203 hat den Chronopolis-Play-Contract inhaltlich klar auf
„freier Infiltrationslauf“ gehärtet. In Modul 6 blieb jedoch die
Abschnittsüberschrift noch auf „Endgame-Hub“, was die neue Lesart unnötig
verwässert.

## Ziel

- Chronopolis in `gameplay/kampagnenstruktur.md` auch in
  Index/Abschnittsüberschrift explizit als „Freier Infiltrationslauf“ führen.
- Anschlussfähigkeit im QA-Prozess mit Fahrplan, Log und Prozessseiten
  nachziehen.

## Arbeitspakete

1. Runtime-SSOT-Wording:
   - `gameplay/kampagnenstruktur.md` (Gameplay-Index + Chronopolis-H2)
2. QA/Prozess-Spiegel:
   - Neuer Log unter `internal/qa/logs/`
   - Ergänzungen in
     `internal/qa/process/hard-final-review-next-steps.md` und
     `internal/qa/process/known-issues.md` (ZR-021)
3. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- Modul 6 führt Chronopolis konsistent als „Freier Infiltrationslauf“ statt
  „Endgame-Hub“.
- Prozessdokumente enthalten den Durchlauf 204 als Anschlussstand.
- Pflicht-Smoke und Link-Lint laufen ohne Fehler.
