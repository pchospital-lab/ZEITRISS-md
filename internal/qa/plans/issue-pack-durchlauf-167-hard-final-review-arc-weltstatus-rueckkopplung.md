# Fahrplan – Durchlauf 167 (Hard-Final-Review Arc-Weltstatus-Rückkopplung)

## Kontext

Nach Durchlauf 166 war die SSOT-Drift weitgehend geschlossen. Als offener
Anschlusspunkt blieb die Frage, ob Makro-Weltkontinuität aus
`arc.factions/questions/hooks` als gleich harter Runtime-Vertrag verankert
werden soll wie Relevanzsatz und ITI-Bulletin.

## Ziel

- Regie-Layer in den Runtime-SSOT-Dokumenten um eine verpflichtende
  Weltstatus-Rückkopplung pro Missionszyklus ergänzen.
- Die Formulierung auf Masterprompt, Toolkit, SL-Referenz und
  Kampagnenstruktur konsistent ziehen.
- Einen Smoke-aktiven Watchguard erweitern, damit die neue Pflicht künftig
  regressionssicher bleibt.

## Arbeitspakete

1. Regie-Layer-Contract in `meta/masterprompt_v6.md` ergänzen.
2. Parallele Contract-Updates in `systems/toolkit-gpt-spielleiter.md`,
   `core/sl-referenz.md` und `gameplay/kampagnenstruktur.md` durchführen.
3. `tools/test_director_layer_watchguard.js` auf den neuen Pflichtanker
   erweitern.
4. Pflicht-Smoke ausführen und Ergebnis im QA-Log dokumentieren.

## Abnahme

- `bash scripts/smoke.sh` ist vollständig grün.
- In allen vier Runtime-Referenzen gilt: genau eine kompakte Weltstatus-Zeile
  pro Missionszyklus aus `arc.factions/questions/hooks` (vor Briefing oder nach
  Heimkehr) mit klarer Folgewirkung.
