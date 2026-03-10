# Fahrplan – Durchlauf 191 (Slot-Count-SSOT-Nachzug Maintainer-Ops)

## Kontext

Nach Durchlauf 190 ist der v7-Save-Vertrag konsistent, es bleibt jedoch ein
kleiner Doku-Unsync im Maintainer-Memo: dort steht noch „20 Wissensmodule“
(inkl. 19 Runtime-Module), obwohl der aktuelle Default-Load-Kanon auf
**19 Gesamt-Slots** (Spieler-Handbuch + 18 Runtime-Module) normiert ist.

## Ziel

- Slot-Zählung im Maintainer-Memo auf die kanonische 19er-Defaultstruktur
  ziehen.
- Anschlussdokumentation (Hard-Final-Review-Übersicht + Known-Issues) um den
  Nachzug ergänzen, damit der nächste Lauf ohne Kontextverlust anknüpfen kann.

## Arbeitspakete

1. `docs/maintainer-ops.md`
   - Runtime-Modulzahl und Slot-Kontrollsatz auf 19-Gesamtlogik korrigieren.
2. `internal/qa/process/hard-final-review-next-steps.md`
   - Durchlauf 191 als abgeschlossenen Anschlusspunkt ergänzen.
3. `internal/qa/process/known-issues.md`
   - ZR-021-Notiz um den Slot-Count-Nachzug aus Durchlauf 191 erweitern.
4. Pflichtcheck `bash scripts/smoke.sh` ausführen.

## Abnahme

- Maintainer-Ops enthält keine 20er-Defaultslot-Angabe mehr.
- Hard-Final-Review-Anschlussseite und Known-Issues spiegeln Durchlauf 191.
- Pflicht-Smoke läuft vollständig grün.
