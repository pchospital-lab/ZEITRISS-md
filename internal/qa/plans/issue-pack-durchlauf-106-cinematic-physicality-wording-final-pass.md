---
title: "Issue-Pack Durchlauf 106 – Cinematic-Start Physicality Final Pass"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-105-spielerhandbuch-npc-kontinuitaet-clarification.md"
---

# Ziel

Verbleibende Physicality-Drift in `systems/gameflow/cinematic-start.md`
schließen, damit der Text keine freischwebenden Hologramm-Defaults mehr
transportiert und klar zwischen Linsen-HUD und sichtbarer HQ-Infrastruktur
trennt.

1. Reststellen mit „holografisch“ im HQ-Einstieg und den Cine-Tipps auf
   Physicality-konforme Formulierungen umstellen.
2. Prozessdoku um Evidenzlauf 106 ergänzen.
3. Pflicht-Smoke und Linkprüfung für betroffene Bereiche ausführen.

# Checkliste

- [x] `systems/gameflow/cinematic-start.md` an Reststellen auf
      Linse/HUD bzw. sichtbare Briefingflächen harmonisiert.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 106 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 106 ergänzt.
- [x] QA-Log für Durchlauf 106 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py systems/gameflow/cinematic-start.md internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 106 schließt die letzten sichtbaren Hologramm-Restformulierungen im
Cinematic-Start und hält den Physicality-Guard konsistent mit Toolkit,
Lore-Core und den NPC/MMO-Follow-up-Regeln.
