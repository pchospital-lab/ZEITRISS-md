# Follow-up Fahrplan – Regelupdate Terminologie/Chronopolis/Save (2026-02-23)

## Kontext
Dieses Follow-up protokolliert offene QA-Befunde aus dem Regelupdate-Lauf
(EP→XP-Terminologie, Chronopolis-Tod, Save-Taktung, Gruppen-Todesentscheid).

## Offene Punkte aus Pflichtprüfungen
- `python3 tools/lint_runtime.py` meldet weiterhin:
  - `systems/gameflow/speicher-fortsetzung.legacy.md`: YAML-Header fehlt/inkomplett.
  - Lint-Regel `migrate_save vorhanden` schlägt fehl.
- Dieselben beiden Befunde blockieren auch `make lint`, `make test` und
  `bash scripts/smoke.sh`, weil sie `lint_runtime.py` einschließen.

## Nächster Durchlauf
1. `systems/gameflow/speicher-fortsetzung.legacy.md` auf erforderlichen YAML-Header prüfen und korrigieren.
2. `migrate_save`-Referenz in den maßgeblichen Runtime-/Wissensmodulen nachziehen,
   bis `tools/lint_runtime.py` die Regel als erfüllt bewertet.
3. Anschließend Pflichtpaket erneut vollständig ausführen:
   - `make lint`
   - `make test`
   - `bash scripts/smoke.sh`
   - `python3 tools/lint_runtime.py`
   - `GM_STYLE=verbose python3 tools/lint_runtime.py`
   - `python3 scripts/lint_doc_links.py`
   - `python3 scripts/lint_umlauts.py`
