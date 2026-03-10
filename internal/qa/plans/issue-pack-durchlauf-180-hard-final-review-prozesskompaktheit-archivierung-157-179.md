# Fahrplan – Durchlauf 180 (Hard-Final-Review Prozesskompaktheit + Archivierung 157–179)

## Kontext

Die Anschlussübersicht `internal/qa/process/hard-final-review-next-steps.md`
enthielt weiterhin die vollständige Detailchronik 157–179. Inhaltlich korrekt,
aber für den operativen Einstieg zu lang und redundant gegenüber bereits
etabliertem Archivierungsprinzip.

## Ziel

- Anschlussübersicht weiter verdichten, ohne Verlust der Nachvollziehbarkeit.
- Detailhistorie 157–179 in ein dediziertes Archiv auslagern.
- Prozessreferenzen (`known-issues.md` + Anschlussübersicht) synchron halten.

## Arbeitspakete

1. Neues Archivdokument für Hard-Final-Review-Historie 157–179 anlegen.
2. `hard-final-review-next-steps.md` auf Kurzfassung umstellen und auf das neue
   Archiv verweisen.
3. `known-issues.md` auf den neuen Archivpfad und Durchlauf-180-Stand
   synchronisieren.
4. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
5. QA-Log für Durchlauf 180 dokumentieren.

## Abnahme

- `hard-final-review-next-steps.md` bleibt operativ kompakt und enthält Verweis
  auf das neue Archiv 157–179.
- `known-issues.md` referenziert die Archivierung konsistent.
- `bash scripts/smoke.sh` läuft vollständig grün.
