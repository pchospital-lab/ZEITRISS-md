# Fahrplan – Durchlauf 199 (LP-Restdrift im QA-Round2-Playtestskript)

## Kontext

Nach den bisherigen LP-Bereinigungen blieb in einem aktiven QA-Playtestskript
noch ein einzelner Alt-Token (`HP 12/12`) bestehen:
`internal/qa/playtest-2026-02-22-round2.sh`.

## Ziel

- Letzten verbliebenen `HP`-Token in aktiven QA-Playtest-Skripten auf `LP`
  ziehen.
- Terminologie-Kohärenz in allen aktiven Regel-/QA-Pfaden sicherstellen.
- Anschlussfähigkeit über Plan/Log/Prozessspiegel dokumentieren.

## Arbeitspakete

1. `internal/qa/playtest-2026-02-22-round2.sh`
   - Statische Assistant-Startnachricht von `HP 12/12` auf `LP 12/12`
     korrigieren.
2. QA-Dokumentation ergänzen:
   - neuer Log unter `internal/qa/logs/`
   - Prozessspiegel in
     `internal/qa/process/hard-final-review-next-steps.md` und
     `internal/qa/process/known-issues.md` nachziehen.
3. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - `rg -n "\\bHP\\b|Hitpoints" internal/qa/*.sh internal/runtime docs gameplay systems meta/masterprompt_v6.md --glob '!internal/qa/evidence/**' --glob '!meta/archive/**'`

## Abnahme

- Kein Treffer für `\bHP\b|Hitpoints` mehr im aktiven QA-Skriptpfad.
- Pflicht-Smoke und Link-Lint laufen erfolgreich.
- Durchlauf 199 ist in Plan/Log/Prozessseiten referenziert.
