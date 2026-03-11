# QA-Log – Durchlauf 204 (Chronopolis Heading/Contract Sync)

## Ausgangslage

Die inhaltliche Schärfung aus Durchlauf 203 ist umgesetzt, aber in
`gameplay/kampagnenstruktur.md` blieb die Kapitelbenennung noch bei
„Endgame-Hub“. Das widerspricht nicht den Regeln, erzeugt aber einen
Lesebruch gegenüber dem neuen Spielmodus-Contract.

## Umsetzung

- `gameplay/kampagnenstruktur.md`
  - Gameplay-Index von „Chronopolis - Endgame-Hub“ auf
    „Chronopolis - Freier Infiltrationslauf“ umgestellt.
  - Kapitelüberschrift entsprechend auf
    „## Chronopolis - Freier Infiltrationslauf“ synchronisiert.
- Prozessspiegel aktualisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021)

## Ergebnis

Der Chronopolis-Play-Contract ist jetzt nicht nur in den Leitplanken, sondern
auch in der sichtbaren Kapitelstruktur konsistent lesbar.

## Checks

- `bash scripts/smoke.sh` → bestanden.
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → bestanden.
- `rg -n 'Chronopolis - Freier Infiltrationslauf|Chronopolis - Endgame-Hub|Durchlauf 204' gameplay/kampagnenstruktur.md internal/qa/process/known-issues.md internal/qa/process/hard-final-review-next-steps.md` → erwartete Treffer.
