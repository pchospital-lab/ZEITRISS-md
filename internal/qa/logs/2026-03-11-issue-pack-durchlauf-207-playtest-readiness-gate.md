# QA-Log – Durchlauf 207 (Playtest-Readiness-Gate)

## Ausgangslage

Nach den inhaltlichen Anschlussläufen bis 206 sind die großen Drift-Themen
abgeräumt. Für den nächsten praktischen Playtest fehlte jedoch ein kurzer,
verbindlicher Go/No-Go-Gate, der bestehende Anforderungen aus Setup,
Pflicht-Smoke und Dokumentation kompakt zusammenführt.

## Umsetzung

- Neues Prozessdokument angelegt:
  - `internal/qa/process/playtest-readiness-gate.md`
- Prozessspiegel fortgeschrieben:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021 ergänzt um Durchlauf 207)

## Ergebnis

Vor neuen Testrunden steht jetzt ein klarer Vorstart-Gate bereit:
Setup prüfen, Pflicht-Smoke erzwingen, Invarianten kurz querchecken,
Evidence-Pfad vorbereiten und erst dann mit GO starten.

## Checks

- `bash scripts/smoke.sh` → bestanden.
- `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` → bestanden.
- `rg -n 'Playtest-Readiness-Gate|Durchlauf 207|playtest-readiness-gate.md' internal/qa/process/hard-final-review-next-steps.md internal/qa/process/known-issues.md internal/qa/process/playtest-readiness-gate.md internal/qa/plans/issue-pack-durchlauf-207-playtest-readiness-gate.md internal/qa/logs/2026-03-11-issue-pack-durchlauf-207-playtest-readiness-gate.md` → erwartete Treffer.
