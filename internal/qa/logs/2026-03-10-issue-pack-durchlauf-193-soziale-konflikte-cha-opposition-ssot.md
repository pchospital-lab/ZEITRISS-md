# QA-Log – Durchlauf 193 (Soziale Konflikte: CHA/Opposition SSOT)

## Ausgangslage

Im Abschnitt „Soziale Konflikte & Einfluss“ (`gameplay/fahrzeuge-konflikte.md`)
war ein freischwebendes Leistenmodell so formuliert, dass es wie eine
Primärmechanik wirken konnte. Das steht quer zum Kernmodell (reguläre Proben,
bei Named-NPCs Oppositionswurf).

## Umsetzung

- Mechanikabschnitt auf SSOT zurückgeführt:
  - soziale Duelle = CHA-basierte Proben,
  - normale NSCs/Mengen = SG-Probe,
  - benannte Gegenspieler = Oppositionswurf gegen relevanten Gegenwert.
- Wortgefecht/Fortschrittspunkte als **optional** und explizit nur als
  Erzähl-Overlay markiert.
- Beispiel-Rededuell auf echte Probeabfolge umgestellt (SG + Oppositionswurf +
  situativer Bonus), ohne Überzeugungspunkt-Leisten als Kernlogik.
- Langzeit-Einfluss bereinigt: keine Formulierungen mehr zu Auto-/Gratis-Erfolg,
  stattdessen Bonuswürfel/SG-Erleichterung/situativer Vorteil auf Proben.
- Prozessspiegel ergänzt:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021 Nachtrag)

## Ergebnis

- Modul 7 ist bei sozialen Konflikten wieder eindeutig auf Wurfmechanik geankert.
- Keine Regeländerung am Systemkern, sondern SSOT-Rückführung einer
  missverständlichen Formulierung.

## Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
- `rg -n "Überzeugungspunkte|Willenskraft-Leiste|automatische Erfolge|Gratis-Erfolg" gameplay --glob '!meta/archive/**'` → keine Treffer.
