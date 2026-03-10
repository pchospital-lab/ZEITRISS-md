# QA-Log – Durchlauf 191 (Slot-Count-SSOT-Nachzug Maintainer-Ops)

## Ausgangslage

Der harte Save-/Watchguard-Stand ist stabil, aber `docs/maintainer-ops.md`
führte weiterhin eine veraltete Slotzählung („20 Wissensmodule“ bzw.
„19 Runtime-Module“). Das widerspricht der etablierten Defaultstruktur mit
19 Gesamt-Slots.

## Umsetzung

- `docs/maintainer-ops.md` auf den kanonischen Zählstand korrigiert:
  - Runtime-Module von 19 auf 18 gestellt.
  - Slot-Kontrolle von 20 auf 19 Wissensmodule angepasst.
- Anschlussdokumentation aktualisiert:
  - `internal/qa/process/hard-final-review-next-steps.md` um den Abschluss von
    Durchlauf 191 ergänzt.
  - `internal/qa/process/known-issues.md` (ZR-021) um den Slot-Count-Nachzug
    ergänzt.

## Ergebnis

- Der Slot-Kanon ist jetzt auch im Maintainer-Memo konsistent auf
  „19 Gesamt-Slots im Default-Ladepfad“.
- Der Durchlauf ist in Fahrplan/Log/Prozessdokus als Anschlusskontext
  dokumentiert.

## Pflicht-Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
