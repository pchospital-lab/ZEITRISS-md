# QA-Log – Durchlauf 199 (LP-Restdrift im QA-Round2-Playtestskript)

## Ausgangslage

Die LP-Terminologie ist in aktiven Gameplay- und QA-Pfaden weitgehend
konsolidiert. In `internal/qa/playtest-2026-02-22-round2.sh` verblieb noch ein
statischer Alt-Token (`HP 12/12`) in der Gladiator-Startnachricht.

## Umsetzung

- `internal/qa/playtest-2026-02-22-round2.sh` angepasst:
  - In der Test-3-Seed-Nachricht (`MSGS_GLAD`) `HP 12/12` auf `LP 12/12`
    umgestellt.
- Prozessspiegel ergänzt:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021-Nachtrag)

## Ergebnis

- Aktive QA-Playtestskripte sind terminologisch konsistent (`LP` statt `HP`).
- Die Anschlussdokumentation für den nächsten Durchlauf ist vollständig
  synchronisiert.

## Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → alle Links validiert.
- `rg -n "\\bHP\\b|Hitpoints" internal/qa/*.sh internal/runtime docs gameplay systems meta/masterprompt_v6.md --glob '!internal/qa/evidence/**' --glob '!meta/archive/**'` → keine aktiven Drift-Treffer.
