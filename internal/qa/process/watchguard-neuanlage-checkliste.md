---
title: "Watchguard-Neuanlage – Checkliste"
date: 2026-03-10
status: aktiv
owner: codex
scope: Meta/Prozess + Tooling
---

# Zweck

Diese Checkliste standardisiert die Neuanlage von `tools/test_*watchguard.js`,
damit Loader-Nutzung, Label-Diagnostik und Smoke-Integration konsistent
bleiben.

## Pflichtschritte bei neuen Watchguards

1. Datei aus `tools/templates/watchguard.template.js` ableiten.
2. `createDocTextLoader({ root, scopeLabel })` verwenden.
3. `scopeLabel`-Konvention einhalten:
   - endet auf `Watchguard`,
   - enthält keine Slash-Zeichen,
   - passt semantisch zum Dateinamen.
4. Markdown ausschließlich über Loader lesen (`readMarkdown` / `getDocText`),
   keine `.md`-Direktlese via `fs.readFileSync`.
5. Ergebnis-Token mit `...-ok` ausgeben und semantisch am Dateinamen ausrichten (z. B. `test_mein_guard_watchguard.js` → `mein-guard-watchguard-ok`).
6. Neuen Guard in `scripts/smoke.sh` aufnehmen (Pflichtcheck, falls
   Hard-Final-Review-relevant).

## Mindeststruktur (Kurzreferenz)

- Imports: `path`, `createDocTextLoader`
- `ROOT = path.resolve(__dirname, '..')`
- Loader-Destructuring aus `createDocTextLoader(...)`
- Inhalt lesen via `readMarkdown(...)`
- Assertions ausführen
- `console.log('<guard-name>-ok')`

## Prozesspflichten pro Durchlauf

- Plan unter `internal/qa/plans/` anlegen
- Log unter `internal/qa/logs/` anlegen
- `internal/qa/process/known-issues.md` synchronisieren
- `internal/qa/process/hard-final-review-next-steps.md` synchronisieren
- Pflicht-Smoke ausführen: `bash scripts/smoke.sh`
