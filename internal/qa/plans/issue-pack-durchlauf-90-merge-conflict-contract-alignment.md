---
title: "Issue-Pack Durchlauf 90 – Merge-Conflict-Contract Alignment"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-89-continuity-output-contract-guard.md"
---

# Ziel

Restdrift zwischen dokumentiertem Cross-Mode-`merge_conflicts[]`-Payload und
Runtime-Verhalten beheben, damit SSOT-Beispielstruktur (`source|target|mode`)
mit `runtime.js`-Sanitizer, Smoke-Guards und bestehenden Fixtures konsistent
bleibt.

1. Merge-Conflict-Beispiel im SSOT auf den tatsächlichen Runtime-Contract mappen.
2. Pflichtchecks erneut ausführen.
3. Anschlusslauf in QA-Plan/Log + Known-Issues dokumentieren.

# Checkliste

- [x] `systems/gameflow/speicher-fortsetzung.md` nutzt im Cross-Mode-Beispiel jetzt `source`, `target`, `mode`.
- [x] Widersprüchliche `resolution`-Enum-Referenz im `merge_conflicts[]`-Beispiel entfernt.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 90 harmonisiert die Dokumentationsschnittstelle für
`logs.flags.merge_conflicts[]` mit der Runtime-Implementierung. Damit sind
Cross-Mode-Konfliktbeispiele wieder maschinen- und reviewerfest und vermeiden
Fehlinterpretationen mit dem separaten `continuity_conflicts[]`-Pfad.
