# Follow-up Fahrplan – Regelupdate Terminologie/Chronopolis/Save (2026-02-23)

## Kontext
Dieses Follow-up protokolliert offene QA-Befunde aus dem Regelupdate-Lauf
(EP→XP-Terminologie, Chronopolis-Tod, Save-Taktung, Gruppen-Todesentscheid).

## Offene Punkte aus Pflichtprüfungen
- ✅ Erledigt: Legacy-Dokument archiviert unter
  `meta/archive/speicher-fortsetzung.legacy.md` (nicht mehr im Runtime-Pfad).
- ✅ Erledigt: `migrate_save` ist wieder explizit im Save-Modul dokumentiert,
  `tools/lint_runtime.py` und `GM_STYLE=verbose tools/lint_runtime.py` laufen
  grün.
- ✅ Erledigt: `make lint`, `bash scripts/smoke.sh`,
  `python3 scripts/lint_doc_links.py` und `python3 scripts/lint_umlauts.py`
  laufen vollständig durch.
- ⚠️ Offen: `make test` scheitert weiterhin in `tools/test_economy_merge.js`
  mit dem vorbestehenden Schema-Fehler
  `saveGame.ui.action_mode erwartet Wert uncut` beim Laden des Test-Saves.

## Nächster Durchlauf
1. Testfixture bzw. Testpfad in `tools/test_economy_merge.js` gegen das
   aktuelle Save-Schema prüfen (`ui.action_mode='uncut'` als verbindlicher Wert).
2. Danach `make test` erneut laufen lassen und das Ergebnis hier ergänzen.
