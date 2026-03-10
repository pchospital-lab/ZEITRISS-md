# QA-Log – Durchlauf 198 (LP-Restdrift in Massenkonflikte-Pseudocode)

## Ausgangslage

Die LP-Terminologie ist in den aktiven Gameplay- und Prozessdokumenten weitgehend
bereinigt. In `gameplay/massenkonflikte.md` verblieb jedoch eine einzelne
Altbezeichnung im Pseudocode (`effektive_HP = HP_Pool × ...`).

## Umsetzung

- `gameplay/massenkonflikte.md` angepasst:
  - Teamgrößen-Skalierung im Pseudocode von
    `effektive_HP = HP_Pool × ceil(team_size / 2)` auf
    `effektive_LP = LP_Pool × ceil(team_size / 2)` umgestellt.
- Prozessspiegel ergänzt:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021-Nachtrag)

## Ergebnis

- In aktivem Gameplay-Regeltext ist kein HP-Token mehr vorhanden.
- Die LP-Nomenklatur ist nun auch im letzten technischen Pseudocode konsistent.

## Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → alle Links validiert.
- `rg -n "\\bHP\\b|Hitpoints" gameplay -S` → keine Treffer.
