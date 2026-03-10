# QA-Log – Durchlauf 184 (Hard-Final-Review Scope-Label-Normierung)

## Ausgangslage

Der Watchguard-Meta-Check prüfte bereits auf vorhandenen `scopeLabel`, aber
noch nicht auf einheitliche Form. Dadurch blieb eine kleine Diagnose-Drift
möglich (uneinheitliche Labelnamen in Fehlerausgaben).

## Umsetzung

- `tools/test_watchguard_loader_consistency.js` ergänzt:
  - neuer Helper `getScopeLabelValue(text)` extrahiert den gesetzten
    `scopeLabel` aus `createDocTextLoader(...)`,
  - zusätzliche Pflichtregel: `scopeLabel` muss auf `Watchguard` enden,
  - zusätzliche Pflichtregel: `scopeLabel` darf keine Slash-Zeichen enthalten.
- Prozess-/Anschlussdokumentation synchronisiert:
  - `internal/qa/process/known-issues.md` auf Durchlauf-184-Stand referenziert,
  - `internal/qa/process/hard-final-review-next-steps.md` um den 184er
    Normierungsschritt ergänzt.

## Ergebnis

- Erstlauf von `bash scripts/smoke.sh` schlug erwartbar fehl: der neue
  Meta-Guard meldete im Bestand `Ruf/Alien-Watchguard` (Slash im Label).
- Guard-Datei nachgezogen auf `Ruf-Alien-Watchguard`; danach lief der
  Pflicht-Smoke vollständig grün.
- Die Guard-Diagnostik ist konsistenter, weil alle `scopeLabel`-Werte einem
  gemeinsamen Benennungsmuster folgen.
- Drift durch pfadähnliche oder uneinheitliche Labelnamen wird frühzeitig im
  Meta-Guard abgefangen.
- Pflicht-Check erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
