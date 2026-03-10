# Fahrplan – Durchlauf 200 (LP-Terminologie-Watchguard für aktive Pfade)

## Kontext

Die LP/HP-Bereinigungen der Durchläufe 192 sowie 197–199 haben die aktive
Terminologie konsolidiert. Der Schutz war bislang aber primär prozedural
(manuale `rg`-Checks in Logs), nicht als dauerhafter CI-Watchguard in
`scripts/smoke.sh` verankert.

## Ziel

- LP-Terminologie (`LP`, nicht `HP/Hitpoints`) in aktiven Runtime-/QA-Pfaden
  dauerhaft gegen Regression absichern.
- Den Check als festen Bestandteil des Pflicht-Smokes verankern.
- Anschlussfähigkeit über Plan/Log/Prozessspiegel dokumentieren.

## Arbeitspakete

1. Neuer Guard in `tools/`:
   - `tools/test_lp_terminology_watchguard.js` anlegen.
   - Zielpfade scannen (`gameplay/`, `systems/`, `docs/`,
     `internal/runtime/`, `internal/qa/playtest-*.sh`, `meta/masterprompt_v6.md`).
   - Nicht-kanonische Evidenz-/Archivpfade explizit ausschließen.
2. Smoke-Integration:
   - Guard in `scripts/smoke.sh` aufnehmen und auf
     `lp-terminology-watchguard-ok` prüfen.
3. Prozess-/QA-Nachzug:
   - Neuer QA-Log unter `internal/qa/logs/`.
   - Nachtrag in
     `internal/qa/process/hard-final-review-next-steps.md` und
     `internal/qa/process/known-issues.md`.
4. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- Smoke enthält den LP-Watchguard und läuft vollständig grün.
- Guard meldet `lp-terminology-watchguard-ok`.
- Durchlauf 200 ist in Plan/Log/Prozessseiten referenziert.
