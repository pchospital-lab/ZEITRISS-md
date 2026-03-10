# QA-Log – Durchlauf 201 (Slot-Count-Restdrift im QA-Audit)

## Ausgangslage

Der kanonische Setup-Standard ist auf 19 Wissensmodule festgelegt
(Spieler-Handbuch + 18 Runtime-Module). In einem aktiven QA-Auditabschnitt
stand noch die alte 20er-Formulierung, die nicht mehr dem SSOT entspricht.

## Umsetzung

- `internal/qa/audits/ZEITRISS-qa-audit-2025.md` korrigiert:
  - „alle 20 Wissensspeicher-Module“ ersetzt durch
    „alle 19 Wissensspeicher-Module (Spieler-Handbuch + 18 Runtime-Module)“.
- Prozessspiegel ergänzt:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021-Nachtrag)
- Neuer Plan/Log für Durchlauf 201 angelegt.

## Ergebnis

- Die letzte aktive Slot-Count-Restdrift im QA-Auditpfad ist bereinigt.
- Maintainer- und QA-Referenzen verwenden konsistent den 19er-Defaultpfad.

## Checks

- `bash scripts/smoke.sh` → erwartet: `All smoke checks passed.`
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → erwartet: alle Links validiert.
