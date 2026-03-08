---
title: "Issue-Pack Durchlauf 84 – Continuity-Fixtures + Guard-Härtung"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-83-continuity-beats-echo-followup.md"
---

# Ziel

Die Session-Anker-/Continuity-Regeln aus den Durchläufen 81–83 auch in den
v7-Fixtures, im Schema-Guard und in den Fixture-Tests konsistent verankern,
sodass der QA-Pfad nicht mehr auf alten Parallel-Core-Refusal-Stand zurückfällt.

1. `continuity`-Block im v7-Schema als dokumentierter Exportpfad ergänzen.
2. Alle v7-Fixtures um `continuity`-Kapsel (inkl. Budgets) ergänzen.
3. `tools/test_v7_schema_consistency.js` auf Pflicht-/Budgetchecks für
   `continuity` erweitern.
4. `tools/test_v7_issue_pack.js` + `v7_parallel_core_refusal.json` auf
   kanonischen Core-Split-Stand (`family_id` + Konvergenz) umstellen.
5. Pflicht-Smoke + Linklint ausführen.

# Checkliste

- [x] `systems/gameflow/saveGame.v7.schema.json` enthält `continuity`-Block.
- [x] Alle `internal/qa/fixtures/savegame_v7_*.json` enthalten `continuity`.
- [x] `tools/test_v7_schema_consistency.js` prüft Presence + Budgetgrenzen.
- [x] `tools/test_v7_issue_pack.js` validiert Split-Konvergenz statt Refusal.
- [x] `internal/qa/fixtures/v7_parallel_core_refusal.json` auf Support-True angepasst.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 84 schließt den QA-Drift zwischen Regeltext und Test-/Fixture-Layer:
Kontinuitätskapsel ist jetzt nicht nur in SSOT-Dokumenten beschrieben, sondern
auch im Schema und in den Regression-Guards explizit abgesichert.
