---
title: "Issue-Pack Durchlauf 83 – Kontinuitäts-Redesign Follow-up (Split/Rejoin-Beats + Echo-Fortwirkung)"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-82-session-anchor-restdrift.md"
---

# Ziel

Offene Erzählausgabe-Pflichten aus dem Kontinuitäts-Redesign explizit in den
SSOT-Kernstellen verankern, damit Multi-Load/Split/Rejoin nicht nur als
Datenmerge, sondern als verpflichtende Inworld-Inszenierung geführt wird.

1. Split-Beat und Rejoin-HQ-Beat als Pflicht in Masterprompt und Runtime-Referenz ergänzen.
2. Echo-Fortwirkungspflicht (innerhalb der nächsten 2 Sitzungsblöcke) in SSOT-Regeln schärfen.
3. Save/Load-SSOT (`speicher-fortsetzung.md`) mit denselben Pflichtbeats harmonisieren.
4. Pflicht-Smoke und Linklint für geänderte Kernstellen ausführen.

# Checkliste

- [x] `meta/masterprompt_v6.md` um Split-/Rejoin-Szenenpflicht + Echo-Fortwirkung ergänzt.
- [x] `systems/gameflow/speicher-fortsetzung.md` Pflichtbeats im Kontinuitätsmodell ergänzt.
- [x] `core/sl-referenz.md` Split/Merge-Kanon um Szenen-/Echo-Pflicht ergänzt.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint für betroffene Dokumente ausgeführt.

# Abschluss

Durchlauf 83 schließt den Output-Contract-Teil des Kontinuitäts-Redesigns:
Multi-Load bleibt deterministisch im Wertebereich, wird aber mit verbindlichen
Szenenbeats (Split/Rejoin) und Echo-Rückkopplung in den nächsten Sitzungsblöcken
erzählerisch belastbar gemacht.
