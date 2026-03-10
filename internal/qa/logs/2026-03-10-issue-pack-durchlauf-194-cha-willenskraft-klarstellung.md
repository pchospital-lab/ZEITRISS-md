# QA-Log – Durchlauf 194 (CHA/Willenskraft-Klarstellung)

## Ausgangslage

Im Sozialkonflikt-Abschnitt von Modul 7 stand noch die Kurzform
`CHA/Willenskraft`. Diese Schreibweise kann fälschlich ein separates
Willenskraft-Attribut suggerieren.

## Umsetzung

- `gameplay/fahrzeuge-konflikte.md` präzisiert:
  - Oppositionswurf gegen den Gegenwert des Ziels,
  - Standardfall ausdrücklich als **CHA (Charisma) als Attribut für
    Überzeugung und Willenskraft** formuliert.
- Prozessspiegel ergänzt:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021-Nachtrag)

## Ergebnis

- Regeltext ist jetzt eindeutig: kein separates Willenskraft-Attribut,
  sondern CHA als kanonischer Träger.

## Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
- `rg -n "CHA/Willenskraft|separates Willenskraft-Attribut" gameplay/fahrzeuge-konflikte.md` → keine Treffer.
