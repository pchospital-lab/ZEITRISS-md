---
title: "Issue-Pack Durchlauf 100 – Masterprompt NPC-Beat-Guard vervollständigen"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-99-npc-continuity-cross-pollination-guard.md"
---

# Ziel

Den letzten SSOT-Restdrift im NPC/MMO-Strang schließen: Die Pflichtbeats
`NPC-Departure` und `NPC-Recognition` standen bereits im Speichermodul und
Toolkit, waren aber im Masterprompt-Regelblock noch nicht als expliziter Guard
formuliert.

1. Masterprompt um klaren Departure/Recognition-Guard ergänzen.
2. Fahrplan- und Prozessdoku auf Durchlauf 100 erweitern.
3. Pflichtchecks erneut ausführen und als Evidenzlauf dokumentieren.

# Checkliste

- [x] `meta/masterprompt_v6.md` um NPC-Departure/Recognition-Guard ergänzt.
- [x] `internal/qa/process/known-issues.md` um Durchlauf-100-Evidenz ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 100 erweitert.
- [x] Neues QA-Log für Durchlauf 100 angelegt.
- [x] Pflicht-Smoke ausgeführt.

# Abschluss

Durchlauf 100 schließt die Guard-Triangulation: Masterprompt,
Speichermodul, Toolkit und SL-Referenz führen nun dieselben NPC-Pflichtbeats
für Abgang und Wiedererkennung, wodurch Folgeänderungen weniger driftanfällig
werden.
