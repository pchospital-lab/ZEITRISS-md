# QA-Log – Durchlauf 206 (Chronopolis Dev-Blueprint Contract Sync)

## Ausgangslage

Durchlauf 203–205 hat den Chronopolis-Play-Contract in Runtime-SSOT,
Kapitelstruktur und SL-Referenz auf „freier Infiltrationslauf“ gehärtet.
Im Dev-Blueprint stand am Abschluss noch die Altlesart „Endgame-Hub“ und
führte damit eine unnötige Terminologie-Drift fort.

## Umsetzung

- `docs/dev/chronopolis-map-blueprint.md`
  - Schlussabsatz von „Endgame-Hub Chronopolis“ auf
    „Chronopolis-Spielmodus als freier Infiltrationslauf“ umgestellt.
- Prozessspiegel aktualisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021)

## Ergebnis

Die Chronopolis-Benennung ist jetzt auch in der Dev-Dokumentation mit dem
gehärteten Runtime-Contract synchron. Dadurch sinkt die Lesedrift zwischen
Design-/Blueprint-Texten und dem aktiven Spielmodus.

## Checks

- `bash scripts/smoke.sh` → bestanden.
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → bestanden.
- `rg -n 'Endgame-Hub|freier Infiltrationslauf|Durchlauf 206' docs/dev/chronopolis-map-blueprint.md internal/qa/process/known-issues.md internal/qa/process/hard-final-review-next-steps.md` → erwartete Treffer.
