---
title: "Log – Durchlauf 160 (Hard-Final-Review / Watchguard-Resolver-Standardisierung)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA + Meta/Prozess
issue: ZR-021
---

## Kontext

In der Anschlussübersicht war als priorisierter Folgeschritt festgehalten, die
robuste Watchguard-Fundlogik als Standard zu etablieren. Nach der Härtung im
Chronopolis-Guard (Durchlauf 159) wurde dafür nun eine gemeinsame Utility
extrahiert.

## Umsetzung

- Neue Utility `tools/watchguard_file_resolver.js` ergänzt:
  - bevorzugte Zielpfade (`preferredRelPaths`) werden zuerst geprüft;
  - fallback auf Markdown-Scan über `candidatePathRegex`;
  - `contentPredicates` erzwingen funktionale Fingerprints;
  - deterministischer Fail bei 0 oder >1 Treffern.
- `tools/test_chronopolis_gate_watchguard.js` auf die Utility umgestellt und
  den Output um den Auflösungsweg (`preferred`/`fallback-scan`) ergänzt.
- Prozessseiten synchronisiert:
  - `internal/qa/process/hard-final-review-next-steps.md`
  - `internal/qa/process/known-issues.md`

## Ergebnis

- Die robuste Zielpfad-Fundlogik liegt nicht mehr als Guard-Einzelfall vor,
  sondern als wiederverwendbarer Baustein für weitere Watchguards.
- Anschlussläufe können neue Guards mit geringerem Pflegeaufwand aufsetzen.

## Checks

- `node tools/test_chronopolis_gate_watchguard.js` erfolgreich.
- `bash scripts/smoke.sh` erfolgreich.

