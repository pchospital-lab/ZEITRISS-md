---
title: "Issue-Pack Durchlauf 85 – Continuity-Fixture-Wording auf Session-Anker"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-84-continuity-fixtures-guards.md"
---

# Ziel

Restdrift in QA-Fixtures nach dem Kontinuitäts-Redesign entfernen, damit auch
Beispieltexte und Branch-IDs konsistent Session-Anker statt Host-Semantik
verwenden.

1. v7-Fixture-Branch-IDs (`HOST-HQ-*`) auf Session-Anker-Wording harmonisieren.
2. Hinweistexte in Mixed-/Abort-Imports von "Host-geführt" auf
   "Session-Anker-geführt" umstellen.
3. Pflichtchecks erneut laufen lassen und den Anschlusslauf dokumentieren.

# Checkliste

- [x] `internal/qa/fixtures/savegame_v7_split_3_2_merge.json` Branch-ID harmonisiert.
- [x] `internal/qa/fixtures/savegame_v7_merge_rift_pvp.json` Hinweistext auf Session-Anker angepasst.
- [x] `internal/qa/fixtures/savegame_v7_abort_resume.json` Hinweistext auf Session-Anker angepasst.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 85 schließt die verbleibende Terminologie-Drift in der Fixture-Schicht:
Regeltexte, Tests und Beispiel-JSON sprechen nun durchgehend die gleiche
Session-Anker-Sprache.
