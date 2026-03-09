---
title: "Issue-Pack Durchlauf 104 – NPC-Continuity-Guard-Automation"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-103-core-physicality-clarification.md"
---

# Ziel

Die offenen Drift-Risiken aus dem NPC/MMO-Strang auf einen automatisierten
Guard heben, damit Save-v7-NPC-Felder und Verhaltenskontrakt nicht mehr nur
textuell, sondern als Pflichtcheck in `scripts/smoke.sh` abgesichert sind.

1. Neuen Guard für SSOT-Feldanker (`npc_roster`, `active_npc_ids`,
   Scope/Slotregel) über Masterprompt/Speichermodul/SL-Referenz ergänzen.
2. Fixture für Join/Leave- und Cross-Pollination-Kontrakt hinzufügen.
3. Prozessdoku um Evidenzlauf 104 ergänzen.
4. Pflicht-Smoke und Linkprüfung erneut ausführen.

# Checkliste

- [x] `tools/test_npc_continuity_consistency.js` angelegt.
- [x] `internal/qa/fixtures/npc_continuity_output_contract.json` angelegt.
- [x] `scripts/smoke.sh` um den neuen NPC-Guard erweitert.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 104 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 104 ergänzt.
- [x] QA-Log für Durchlauf 104 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 104 macht den NPC-Kontinuitätsstrang anschlussfest: künftige
Drifts bei v7-NPC-Feldern, Join/Leave-Zuordnung, Slotregel und
Cross-Pollination werden als Pflicht-Smoke automatisch erkannt.
