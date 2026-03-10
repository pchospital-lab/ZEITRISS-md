# Fahrplan – Durchlauf 201 (Slot-Count-Restdrift im QA-Audit)

## Kontext

Der 19er-Defaultpfad (Spieler-Handbuch + 18 Runtime-Module) ist in den
kanonischen Setup-/Runtime-Dokumenten bereits synchronisiert. Im aktiven
QA-Auditpfad stand jedoch noch ein veralteter Verweis auf
„20 Wissensspeicher-Module“, der bei Übergaben unnötige Unsicherheit erzeugt.

## Ziel

- Verbleibende aktive Slot-Count-Drift (20 → 19) im QA-Audit schließen.
- Die Korrektur in Fahrplan/Log/Prozessspiegel dokumentieren, damit nächste
  Anschlussläufe ohne Kontextverlust fortsetzen können.

## Arbeitspakete

1. Audit-Korrektur:
   - `internal/qa/audits/ZEITRISS-qa-audit-2025.md` auf den kanonischen
     19er-Defaultpfad umstellen (Spieler-Handbuch + 18 Runtime-Module).
2. Prozess-/QA-Nachzug:
   - Neuer Durchlauf-Plan unter `internal/qa/plans/`.
   - Neuer Durchlauf-Log unter `internal/qa/logs/`.
   - Nachträge in
     `internal/qa/process/hard-final-review-next-steps.md` und
     `internal/qa/process/known-issues.md`.
3. Pflichtchecks:
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

## Abnahme

- Keine aktive 20er-Formulierung mehr im Zielpfad des QA-Audits.
- Pflicht-Smoke vollständig grün.
- Links in Plan/Log/Prozessseiten validiert.
