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
- ✅ Erledigt: `tools/test_economy_merge.js` nutzt im Merge-Test jetzt ein
  schema-konformes `incomingSave.ui.action_mode="uncut"`; `make test` läuft
  wieder grün.

## Abschlussstand
Der Follow-up-Block ist abgeschlossen; es bestehen aktuell keine offenen
Pflichtprüfungs-Punkte mehr aus dem Regelupdate-Lauf vom 2026-02-23.
