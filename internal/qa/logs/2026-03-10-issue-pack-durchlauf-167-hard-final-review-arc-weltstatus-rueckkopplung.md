# QA-Log – Durchlauf 167 (Hard-Final-Review Arc-Weltstatus-Rückkopplung)

## Ausgangslage

Die persönliche und Gruppen-Kontinuität war bereits mit harten Beats abgesichert
(Relevanzsatz vor Briefing, ITI-Bulletin nach Heimkehr). Offen blieb die
gleich harte Rückkopplung der persistierten Makro-Weltdaten aus
`arc.factions`, `arc.questions` und `arc.hooks`.

## Umsetzung

- Runtime-Contract um Pflicht-Weltstatus ergänzt:
  - `meta/masterprompt_v6.md`
  - `systems/toolkit-gpt-spielleiter.md`
  - `core/sl-referenz.md`
  - `gameplay/kampagnenstruktur.md`
- Vereinheitlichter Contract:
  - pro Missionszyklus **genau eine** kompakte Weltstatus-Zeile
  - Platzierung **vor Briefing oder nach Heimkehr**
  - Quelle: `arc.factions/questions/hooks`
  - immer mit konkreter Folgewirkung für den nächsten Einsatzrahmen
- QA-Härtung:
  - `tools/test_director_layer_watchguard.js` prüft jetzt zusätzlich den neuen
    Weltstatus-Pflichtanker neben Relevanzsatz und ITI-Bulletin.

## Ergebnis

- Erster Smoke-Lauf schlug gezielt im erweiterten `director-layer-watchguard`
  fehl (Regex zu eng für die Masterprompt-Formulierung des Weltstatus-Satzes).
- Watchguard-Regel wurde auf robuste Wortreihenfolgevarianten gehärtet; danach
  zweiter Pflicht-Smoke-Lauf vollständig grün:
  `bash scripts/smoke.sh` → „All smoke checks passed.“
- Die Arc-Makrokontinuität ist damit nicht nur persistiert, sondern als
  verpflichtender Regie-Output im Runtime-SSOT und im Smoke-Gate verankert.
