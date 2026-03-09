---
title: "Issue-Pack Durchlauf 96 – Cinematic-Physicality-Restdrift"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-95-hologramm-physicality-harmonisierung.md"
---

# Ziel

Nach der Physicality-Nuancierung (Durchlauf 95) verbleibende Mischbegriffe im
Cinematic-Start entfernen, damit HQ-Projektionen und Linsen-HUD sauber getrennt
bleiben und kein semantischer Rückfall in unklare Hologramm-Defaults entsteht.

1. Solo-Begleiter-Wording auf klare Gerätepfade reduzieren (Linse/HUD vs. HQ-
   Briefingflächen).
2. Kulturkollisions-Beispiel in `cinematic-start.md` auf HQ-gebundene
   Lichtbilder schärfen.
3. Pflicht-Smoke ausführen und Anschlusslauf dokumentieren.

# Checkliste

- [x] `systems/gameflow/cinematic-start.md` Wording in den Restdrift-Stellen präzisiert.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 96 ergänzt.
- [x] Pflicht-Smoke ausgeführt.

# Abschluss

Durchlauf 96 entfernt die verbliebenen Mischformulierungen zwischen HUD und
HQ-Projektion im Startmodul. Damit bleibt der Physicality-Gate-Guard aus
Durchlauf 95 erhalten und sprachlich konsistent.
