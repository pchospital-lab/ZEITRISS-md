# QA-Log – Durchlauf 173 (Hard-Final-Review Director-Watchguard Doc-Loader-Rollout)

## Ausgangslage

Nach den Rollouts der Durchläufe 171 und 172 blieb der
`tools/test_director_layer_watchguard.js` als Restbestand mit einer lokalen
Resolver-Funktion (`resolveDocTarget`) zurück. Fachlich war der Guard korrekt,
aber der Loader-Standard war noch nicht vollständig konsistent.

## Umsetzung

- `tools/test_director_layer_watchguard.js` auf
  `createDocTextLoader` aus `tools/watchguard_doc_loader.js` umgestellt.
- Lokale Resolver-Helferfunktion entfernt; stattdessen
  `readMarkdown(relPath, anchors, label)` aus dem zentralen Loader genutzt.
- Guard-Regeln/Assertions unverändert gelassen (Relevanzsatz,
  ITI-Bulletin, Weltstatus-Zeile aus `arc.factions/questions/hooks`).
- Prozessseiten synchronisiert:
  - `internal/qa/process/known-issues.md`
  - `internal/qa/process/hard-final-review-next-steps.md`

## Ergebnis

- Der `director-layer-watchguard` folgt jetzt ebenfalls dem zentralen
  Resolver-/Loader-Standard.
- Pflicht-Smoke erfolgreich:
  - `bash scripts/smoke.sh` → „All smoke checks passed.“
