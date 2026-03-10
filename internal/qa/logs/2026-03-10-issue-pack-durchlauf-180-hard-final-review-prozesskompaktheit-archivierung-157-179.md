# QA-Log – Durchlauf 180 (Hard-Final-Review Prozesskompaktheit + Archivierung 157–179)

## Ausgangslage

Die Anschlussübersicht führte die komplette Durchlaufprosa 157–179 noch direkt
im operativen Dokument. Das erhöhte Leselast bei neuen Durchläufen, obwohl der
Prozess bereits auf kompakte Einstiegsseiten + Archive ausgelegt ist.

## Umsetzung

- Neues Archiv angelegt:
  - `internal/qa/process/archive/hard-final-review-durchlaufhistorie-157-179.md`
    mit der vollständigen Detailchronik der Durchläufe 157–179.
- Operatives Dokument entschlackt:
  - `internal/qa/process/hard-final-review-next-steps.md` auf kompakte
    Kurzfassung umgestellt,
  - zentrale Smoke-Guard-Anker und offene Anschluss-Tasks beibehalten,
  - Referenzen auf beide Archivpfade (73–156 und 157–179) ergänzt.
- Prozessstatus synchronisiert:
  - `internal/qa/process/known-issues.md` aktualisiert (ZR-021-Notiz +
    Archivabschnitt mit Verweis auf das neue 157–179-Archiv).

## Ergebnis

- Prozessdokumente bleiben anschlussfähig und konsistent (Kurzfassung operativ,
  Detailhistorie archiviert).
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
