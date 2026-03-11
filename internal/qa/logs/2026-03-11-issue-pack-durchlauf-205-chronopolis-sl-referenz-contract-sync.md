# QA-Log – Durchlauf 205 (Chronopolis SL-Referenz Contract Sync)

## Ausgangslage

Chronopolis ist seit Durchlauf 203/204 als freier Infiltrationslauf sauber
in mehreren SSOT-Dateien verankert. In `core/sl-referenz.md` blieb im
Chronopolis-Block jedoch noch die ältere Formulierung „ohne Missionsdruck“
stehen und verwässerte die gewünschte Spielmodus-Lesart.

## Umsetzung

- `core/sl-referenz.md`
  - Stimmungswechsel-Passage von „ohne Missionsdruck eintauchen“ auf
    Infiltrationslauf-Contract umgestellt (unauffällig rein, Chancen nutzen,
    Spuren klein halten, lebend raus).
  - Funktionssatz von lockerer Hub-Lesart auf
    „freier Infiltrationslauf mit Reaktionsdruck statt Freizeit-Hub“
    synchronisiert.
- Prozessspiegel aktualisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021)

## Ergebnis

Die Chronopolis-Lesart ist jetzt auch in der SL-Referenz konsistent mit dem
gehärteten Runtime-Contract: frei spielbar, aber nicht harmlos und nicht als
Missionsersatz-Hub.

## Checks

- `bash scripts/smoke.sh` → bestanden.
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → bestanden.
- `rg -n 'ohne Missionsdruck|freier Infiltrationslauf mit Reaktionsdruck|Durchlauf 205' core/sl-referenz.md internal/qa/process/known-issues.md internal/qa/process/hard-final-review-next-steps.md` → erwartete Treffer.
