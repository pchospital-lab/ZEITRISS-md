# Fahrplan – Durchlauf 198 (LP-Restdrift in Massenkonflikte-Pseudocode)

## Kontext

Nach den LP-Terminologie-Bereinigungen blieb noch eine einzelne Altbezeichnung
in `gameplay/massenkonflikte.md`: Der Skalierungs-Pseudocode für Teamgröße
nutzte weiterhin `effektive_HP = HP_Pool ...`.

## Ziel

- Letzten verbleibenden HP-Token im aktiven Gameplay-SSOT eliminieren.
- Terminologie in Spieler-/Regeltexten vollständig auf LP vereinheitlichen.
- Anschlussfähigkeit im QA-Prozess durch Plan/Log/Prozessspiegel sichern.

## Arbeitspakete

1. `gameplay/massenkonflikte.md`
   - Pseudocode auf `effektive_LP = LP_Pool × ceil(team_size / 2)` umstellen.
2. QA-Dokumentation ergänzen:
   - neuer Log unter `internal/qa/logs/`
   - Prozessspiegel in
     `internal/qa/process/hard-final-review-next-steps.md` und
     `internal/qa/process/known-issues.md` nachziehen.
3. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- Kein Treffer für `\bHP\b|Hitpoints` mehr in `gameplay/`.
- Pflicht-Smoke und Link-Lint laufen erfolgreich.
- Durchlauf 198 ist in Plan/Log/Prozessseiten referenziert.
