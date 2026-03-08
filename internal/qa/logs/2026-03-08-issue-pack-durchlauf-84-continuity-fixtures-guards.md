---
title: "QA-Log 2026-03-08 – Durchlauf 84 (Continuity-Fixtures + Guard-Härtung)"
status: "abgeschlossen"
run_id: "zr-018-d84"
---

# Kontext

Die Regeltexte aus Durchlauf 81–83 waren konsistent, aber Fixture-/Guard-Layer
hatte noch Restdrift:

- v7-Schema kannte `continuity` nicht explizit.
- v7-Fixtures exportierten `continuity` nicht.
- `tools/test_v7_issue_pack.js` erwartete weiterhin einen Parallel-Core-Refusal
  (`supported=false`) statt kanonischem Split-Protokoll.

# Umgesetzte Änderungen

1. **Schema nachgezogen (`systems/gameflow/saveGame.v7.schema.json`)**
   - Root-Property `continuity` ergänzt mit Unterfeldern:
     `last_seen`, `split`, `roster_echoes`, `shared_echoes`,
     `convergence_tags`.
   - Budgetgrenzen über Schema abgesichert (`maxItems` 5/6/4).

2. **Fixtures harmonisiert (`internal/qa/fixtures/savegame_v7_*.json`)**
   - Alle v7-Fixtures um `continuity` ergänzt.
   - Split-/Merge-Fixture mit kanonischem Konvergenzbeispiel ergänzt:
     `split.family_id`, `expected_threads/resolved_threads`,
     `convergence_ready=true`, `convergence_tags`.

3. **Guard-Tests geschärft (`tools/test_v7_schema_consistency.js`)**
   - Presence-Checks für `continuity` und Teilstrukturen ergänzt.
   - Budgetchecks auf `roster_echoes/shared_echoes/convergence_tags`
     ergänzt.

4. **Issue-Pack-Test auf neuen Kanon umgestellt (`tools/test_v7_issue_pack.js`)**
   - Split-/Merge-Checks prüfen jetzt `family_id`, `convergence_ready` und
     Tag-Nachweis.
   - Parallel-Core-Refusal-Fixture auf Support-True + Acceptance-Text
     umgestellt (`internal/qa/fixtures/v7_parallel_core_refusal.json`).

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core systems meta/masterprompt_v6.md README.md internal/qa/plans internal/qa/logs`
   - Ergebnis: **grün**

# Bewertung

- Regeltexte, Schema und Regression-Fixtures sprechen jetzt dieselbe
  Continuity-Sprache.
- Der frühere QA-Rückfall auf „Parallel-Core nicht kanonisch" ist als
  Prüferwartung entfernt.
- HQ-DeepSave-/Determinismus-Invarianten bleiben unverändert.
