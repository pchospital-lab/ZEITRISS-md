# QA-Log – Durchlauf 195 (Sozialkonflikte: erst ausspielen, dann Wurf)

## Ausgangslage

Nach den letzten Nachzügen war die Mechanik sauber, aber das gewünschte
Pen-&-Paper-Gefühl („erst das gespielte Wort wirken lassen“) war nicht explizit
als Reihenfolge formuliert.

## Umsetzung

- `gameplay/fahrzeuge-konflikte.md` präzisiert:
  - Soziale Duelle bleiben CHA-basiert,
  - Würfelwürfe erfolgen erst bei unklarem/risikoreichem/aktiv umkämpftem
    Ausgang,
  - klare Szene = direkte KI-SL-Entscheidung ohne Pflichtwurf,
  - Named-Widerstand = Oppositionswurf.
- Beispiel „Rededuell“ angepasst:
  - Runde 1 ohne Wurf entschieden (starke Ansprache),
  - bei aktivem Gegenzug anschließend Oppositionswurf,
  - finaler Bonuswurf nach Menschenkenntnis.
- Prozessspiegel ergänzt:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md` (ZR-021-Nachtrag)

## Ergebnis

- Die KI-SL kann das textuelle Spielgefühl stärker nutzen, ohne den
  bestehenden Wurfkern aufzuweichen.
- Regelklarheit: Keine Pflichtwürfe bei bereits klarer Lage, aber klare
  Würfelanbindung bei Unsicherheit oder Widerstand.

## Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
- `rg -n "Erst würfeln|ohne Pflichtwurf|unklarem Ausgang|aktiv umkämpft" gameplay/fahrzeuge-konflikte.md` → erwartete Treffer vorhanden.
