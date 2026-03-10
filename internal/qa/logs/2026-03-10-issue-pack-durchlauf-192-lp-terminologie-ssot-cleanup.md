# QA-Log – Durchlauf 192 (LP-Terminologie-SSOT-Cleanup)

## Ausgangslage

Die harten Save-/Schema-Themen sind abgeschlossen. Bei einer gezielten
Restprüfung auf spieler-sichtige Terminologie blieb ein kleiner Wording-Drift:
mehrere aktive Stellen verwendeten noch „HP/Hitpoints“ statt „LP“.

## Umsetzung

- `gameplay/kreative-generatoren-begegnungen.md`
  - Gegner-/Trigger-Tabellen auf LP umgestellt.
- `gameplay/kampagnenstruktur.md`
  - Rift-Statblock von „HP: W6×Tier“ auf „LP: W6×Tier“ korrigiert.
- `gameplay/fahrzeuge-konflikte.md`
  - Erklärungstext auf „geistige Lebenspunkte“ umgestellt.
- `internal/runtime/runtime-stub-routing-layer.md`
  - Spielernahe Rest-Ausgabe korrigiert auf „LP & Stress reset.“
- Prozesskontext synchronisiert:
  - `internal/qa/process/hard-final-review-next-steps.md` um Durchlauf 192 ergänzt.
  - `internal/qa/process/known-issues.md` (ZR-021) um Nachtrag zu Durchlauf 192 ergänzt.

## Ergebnis

- Spielernahe Terminologie ist auf LP vereinheitlicht.
- Keine Regel-/Mechanikänderung, nur sprachliche SSOT-Härtung.
- Durchlauf ist dokumentiert und an den Anschlussprozess angebunden.

## Checks

- `rg -n "\bHP\b|Hitpoints" gameplay internal/runtime docs systems meta/masterprompt_v6.md --glob '!meta/archive/**'` → keine Treffer in aktiven Zielpfaden.
- `bash scripts/smoke.sh` → `All smoke checks passed.`
