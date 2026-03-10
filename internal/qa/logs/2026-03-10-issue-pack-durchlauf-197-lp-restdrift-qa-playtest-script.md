# QA-Log – Durchlauf 197 (LP-Restdrift im QA-Playtest-Skript)

## Ausgangslage

Nach den LP-Bereinigungsdurchläufen 192–195 war in den SSOT- und
Runtime-nahen Dokumenten kein spieler-sichtbares „HP/Hitpoints“ mehr
vorgesehen. Ein einzelner Alttext im QA-Skript
`internal/qa/playtest-2026-02-22-deep.sh` nutzte jedoch noch „HP 12“ in einer
statischen Assistant-Nachricht.

## Umsetzung

- `internal/qa/playtest-2026-02-22-deep.sh` angepasst:
  - In der Seed-Nachricht für den Cross-Load-Test wurde `HP 12` auf `LP 12`
    korrigiert.
- Prozessspiegel ergänzt:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021-Nachtrag)

## Ergebnis

- Auch der verbliebene QA-Evidenzpfad verwendet nun konsistent LP.
- Terminologie-Drift ist für diesen Strang vollständig geschlossen.

## Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → alle Links validiert.
- `rg -n "\\bHP\\b|Hitpoints" internal/qa/playtest-2026-02-22-deep.sh` → keine Treffer.
