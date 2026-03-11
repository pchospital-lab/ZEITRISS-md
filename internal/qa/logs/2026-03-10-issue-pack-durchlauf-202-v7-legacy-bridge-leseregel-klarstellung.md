# QA-Log – Durchlauf 202 (Legacy-Bridge Leseregel-Klarstellung)

## Ausgangslage

Im Abschnitt „Voller HQ-Deepsave (Solo/Gruppe)“ in
`systems/gameflow/speicher-fortsetzung.md` existiert ein großer
Legacy-Bridge-Block. Obwohl dieser bereits als Legacy markiert ist, kann die
Kombination aus umfangreichem Beispiel und `v: 7` beim Überfliegen als
konkurrierender Neu-Exportpfad missverstanden werden.

## Umsetzung

- `systems/gameflow/speicher-fortsetzung.md` ergänzt:
  - Explizite Leseregel direkt vor dem Legacy-Bridge-HQ-Beispiel hinzugefügt:
    `v: 7` in diesem Block ist Import-/Migrations-Bridge und kein
    kanonischer Neu-Export.
- Prozessspiegel fortgeschrieben:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021)
- Neuer Plan/Log für Durchlauf 202 angelegt.

## Ergebnis

- Der Legacy-Bridge-Abschnitt ist klarer gegen Fehlinterpretation abgesichert,
  ohne den bestehenden v7-Smoke-Guard-Vertrag zu verletzen.
- Lesefluss für Maintainer/Spielleitung bleibt robust: Kanonischer Neu-Export
  bleibt ausschließlich im Abschnitt „Kanonisches Save-Exportformat“ verankert.

## Checks

- `bash scripts/smoke.sh` → erwartet: `All smoke checks passed.`
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → erwartet: alle Links validiert.
- `rg -n 'Leseregel für dieses Legacy-Muster|Kanonisches Save-Exportformat' systems/gameflow/speicher-fortsetzung.md` → erwartete Trefferlage.
