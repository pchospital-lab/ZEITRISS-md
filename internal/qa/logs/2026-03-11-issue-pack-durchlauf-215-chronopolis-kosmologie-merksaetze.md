# QA-Log – Durchlauf 215 (Chronopolis Kosmologie-Merksätze)

## Ausgangslage

Nach den Chronopolis-Härtungen 209–214 war der Runtime-Contract stabil, aber
im Lore-Fluss fehlte noch eine kurze, wiederholbare Klammer für
Langzeitspielende. Außerdem klang ein Satz in der SL-Referenz noch so, als
würde Kodex Chronopolis frei "erschaffen".

## Umsetzung

- `core/spieler-handbuch.md`
  - Zeitriss-Definition als **Kausalwunde** ergänzt.
  - Brückensatz ergänzt: **Absolut / Nullzeit / Zeitriss** als drei Zustände
    derselben Grenzphysik.
- `core/sl-referenz.md`
  - Kodex-Lore umgestellt auf **Bruchmöglichkeit ankoppeln und stabilisieren**
    statt "Parallelrealität erschaffen".
  - Chronopolis-Merksatz ergänzt (weder Simulation noch Prophezeiung).
  - ITI-Kurzsatz ergänzt: `ABSOLUT-7 liest keine Zukunft. Es macht Bruchlinien lesbar.`
- Prozessspiegel fortgeführt:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md`

## Ergebnis

Die zentralen Begriffe (Absolut, Nullzeit, Zeitriss, Kodex, Chronopolis)
sind jetzt in den Spieler- und SL-Kerntexten als ein einziges Modell lesbar,
ohne den Eindruck eines beliebig-göttlichen Kodex.

## Checks

- `bash scripts/smoke.sh` → bestanden.
