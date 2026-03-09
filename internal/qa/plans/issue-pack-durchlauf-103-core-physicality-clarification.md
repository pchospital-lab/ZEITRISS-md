---
title: "Issue-Pack Durchlauf 103 – Core-Physicality-Klarstellung"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-102-core-physicality-terminology-alignment.md"
---

# Ziel

Die semantische Absicht des Physicality-Gates in `core/zeitriss-core.md`
präzisieren: Hologramme sind erlaubt, sofern sie an sichtbare Inworld-
Infrastruktur gebunden sind; der verbotene Default bleibt das mobile
Handgelenk-HUD.

1. Core-Passagen von "Hologramm komplett vermeiden" auf "Hologramm ja,
   aber verankert" justieren.
2. QA-Prozessdoku um Evidenzlauf 103 ergänzen.
3. Pflicht-Smoke erneut ausführen.

# Checkliste

- [x] `core/zeitriss-core.md` mit expliziter Verankerungsregel (Holosuite/Briefingglas/Tischprojektor) aktualisiert.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 103 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 103 ergänzt.
- [x] QA-Log für Durchlauf 103 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.

# Abschluss

Durchlauf 103 stellt die gemeinsame Intention wieder eindeutig her:
Mixed-Retina-HUD bleibt linsengebunden, Hologramm-Projektionen bleiben erlaubt,
aber nur als sichtbare, inworld verankerte Geräteflächen.
