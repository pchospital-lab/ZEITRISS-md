# Fahrplan – Durchlauf 197 (LP-Restdrift im QA-Playtest-Skript)

## Kontext

Die LP-Terminologie wurde in den spielnahen SSOT-Dokumenten bereits
vereinheitlicht. Ein verbliebener Alttext stand noch in
`internal/qa/playtest-2026-02-22-deep.sh` als eingebettete Assistant-Nachricht
mit „HP 12“.

## Ziel

- Letzte Restdrift „HP“ → „LP“ im aktiven QA-Playtest-Skript entfernen.
- Sicherstellen, dass auch Test-/Evidenzskripte die Spielerterminologie
  konsistent spiegeln.
- Anschlussfähigkeit über Plan/Log/Prozessseiten erhalten.

## Arbeitspakete

1. `internal/qa/playtest-2026-02-22-deep.sh`
   - In der statischen Assistant-Message `HP 12` auf `LP 12` korrigieren.
2. Prozessspiegel fortschreiben:
   - `internal/qa/process/hard-final-review-next-steps.md`
   - `internal/qa/process/known-issues.md`
3. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- Kein verbleibendes `HP` in der betroffenen QA-Playtest-Nachricht.
- Prozess- und QA-Dokumentation ist um Durchlauf 197 ergänzt.
- Pflicht-Smoke und Linklint laufen erfolgreich.
