# Fahrplan – Durchlauf 179 (Hard-Final-Review Watchguard-Loader-Consistency Hardening)

## Kontext

Durchlauf 177 hat den Meta-Guard `watchguard-loader-consistency` als Pflichtanker
in den Smoke gebracht. In der Praxis zeigte sich dabei ein Robustheitsgap:
Der Guard prüfte direkte `.md`-Direktlese, aber noch nicht robust genug für
multiline-`readFileSync(...)`-Fälle. Zusätzlich sollte die API-Nutzung des
zentralen Loaders klarer erzwungen werden.

## Ziel

- Loader-Konsistenz-Guard auf multiline-sichere Erkennung direkter
  `.md`-Direktlese härten.
- Sicherstellen, dass Watchguards nicht nur `createDocTextLoader` importieren,
  sondern auch eine zentrale Loader-Lese-API (`readMarkdown` oder `getDocText`)
  tatsächlich nutzen.
- QA-/Prozessspur auf Durchlauf-179-Stand fortschreiben.

## Arbeitspakete

1. `tools/test_watchguard_loader_consistency.js` erweitern:
   - Helper für multiline-sichere `.md`-Direktlese-Erkennung,
   - zusätzliche Assertion für reale Loader-API-Nutzung
     (`readMarkdown(...)` oder `getDocText(...)`).
2. Meta-Guard einzeln ausführen (`node tools/test_watchguard_loader_consistency.js`).
3. Pflicht-Smoke ausführen (`bash scripts/smoke.sh`).
4. QA-Log für Durchlauf 179 ergänzen.
5. `known-issues.md` und `hard-final-review-next-steps.md` synchronisieren.

## Abnahme

- `node tools/test_watchguard_loader_consistency.js` meldet
  `watchguard-loader-consistency-ok`.
- `bash scripts/smoke.sh` vollständig grün.
- Prozessübersichten dokumentieren Durchlauf 179 als Hardening des
  Loader-Konsistenz-Regressionankers.
