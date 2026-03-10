# QA-Log – Durchlauf 200 (LP-Terminologie-Watchguard für aktive Pfade)

## Ausgangslage

Die Terminologie-Drift `HP/Hitpoints` wurde in den letzten Durchläufen
inhaltlich bereinigt. Um Rückfälle bei späteren Änderungen zu verhindern,
fehlte noch ein dedizierter, automatischer Smoke-Guard für aktive
Runtime-/QA-Pfade.

## Umsetzung

- Neuer Watchguard angelegt: `tools/test_lp_terminology_watchguard.js`
  - nutzt den standardisierten Loader (`createDocTextLoader`),
  - scannt aktive Zielpfade per `git ls-files`,
  - meldet harte Violations bei `\bHP\b|Hitpoints`,
  - schließt Evidenz-/Archiv-/Uploadpfade sowie Prozesshistorien aus.
- Pflicht-Smoke erweitert: `scripts/smoke.sh`
  - Ausführung des neuen Guards,
  - Grep auf Ergebnis-Token `lp-terminology-watchguard-ok`.
- Prozessspiegel synchronisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021-Nachtrag)

## Ergebnis

- LP-Terminologie ist nicht mehr nur per manueller Einmalprüfung abgesichert,
  sondern als dauerhafter CI-/Smoke-Watchguard verankert.
- Künftige HP-Restdrift in aktiven Zielpfaden wird sofort fail-fast erkannt.

## Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → alle Links validiert.
