# Fahrplan – Durchlauf 192 (LP-Terminologie-SSOT-Cleanup)

## Kontext

Nach den v7- und Slot-Count-Nachzügen sind die Save-/Prozessverträge stabil.
Ein kleiner, aber spielerisch sichtbarer Restdrift blieb in der Wortwahl:
vereinzelt stand noch „HP/Hitpoints“ in spielnahen Texten. Laut
Repo-Invariante müssen spieler-sichtige Formulierungen konsistent „LP“ nutzen.

## Ziel

- Terminologie-Drift „HP/Hitpoints“ in spielnahen Texten entfernen.
- Betroffene Stellen in Runtime-Stubs und Gameplay-Dokumenten auf „LP“
  vereinheitlichen, ohne Mechanik oder Datenmodell zu ändern.
- Anschlussfähigkeit über Fahrplan/Log/Prozessseiten dokumentieren.

## Arbeitspakete

1. `gameplay/kreative-generatoren-begegnungen.md`
   - Tabelleneinträge von HP auf LP umstellen.
2. `gameplay/kampagnenstruktur.md`
   - Rift-Statblock von HP auf LP umstellen.
3. `gameplay/fahrzeuge-konflikte.md`
   - Begriff „Hitpoints“ in sozialer Konflikterklärung auf deutschsprachiges
     LP-Wording ziehen.
4. `internal/runtime/runtime-stub-routing-layer.md`
   - Spielernahe Ausgabemeldung („HP & Stress reset“) auf LP korrigieren.
5. Prozessspiegel aktualisieren:
   - `internal/qa/process/hard-final-review-next-steps.md`
   - `internal/qa/process/known-issues.md`
6. Pflichtcheck `bash scripts/smoke.sh` ausführen.

## Abnahme

- In den betroffenen aktiven Pfaden bleiben keine spieler-sichtigen
  HP/Hitpoints-Formulierungen zurück.
- Pflicht-Smoke ist grün.
- Durchlauf 192 ist in Fahrplan/Log/Prozessdokus als Anschlusskontext erfasst.
