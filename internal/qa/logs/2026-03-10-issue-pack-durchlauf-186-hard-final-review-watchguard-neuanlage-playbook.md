# QA-Log – Durchlauf 186 (Hard-Final-Review Watchguard-Neuanlage-Playbook)

## Ausgangslage

Die technische Durchsetzung des Loader-Standards ist per Meta-Guard vorhanden,
aber die Neuanlage neuer Watchguards hatte keinen eigenen, knappen
Maintainer-Einstieg mit Template + Checkliste.

## Umsetzung

- Neues Starttemplate ergänzt:
  - `tools/templates/watchguard.template.js`
  - enthält `createDocTextLoader(...)` mit `scopeLabel`, Loader-basierte
    Markdown-Lese-API und `...-ok`-Ausgabetoken.
- Neue Prozess-Checkliste ergänzt:
  - `internal/qa/process/watchguard-neuanlage-checkliste.md`
  - dokumentiert Pflichtschritte für neue Guards inkl. Smoke-/Prozesssync.
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md` um Durchlauf-186-Hinweis ergänzt,
  - `internal/qa/process/hard-final-review-next-steps.md` um den neuen
    Playbook-Schritt erweitert.

## Ergebnis

- Watchguard-Neuanlage ist im Repo nun als wiederholbarer, knapper Ablauf
  dokumentiert.
- Loader-/Label-Standards sind nicht nur implizit im Meta-Guard, sondern auch
  explizit im Neuanlage-Playbook verankert.
- Pflicht-Smoke lief vollständig grün.

## Pflicht-Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
