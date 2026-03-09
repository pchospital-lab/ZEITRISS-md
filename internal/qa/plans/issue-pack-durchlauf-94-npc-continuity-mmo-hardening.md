---
title: "Issue-Pack Durchlauf 94 – NPC-Kontinuität & MMO-Immersion-Hardening"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  statusmatrix: "internal/qa/process/continuity-redesign-statusmatrix.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-93-continuity-closure-matrix-cleanup.md"
---

# Ziel

Das NPC/MMO-Review in den aktiven Wissensspeicherpfaden verankern: persistente
NPC-Chrononauten statt temporärer Solo-Begleiter, klare Slot-Regeln für
Mensch/NPC-Mischgruppen, und durchgehende Rejoin-/Offscreen-Logik im v7-
Kontinuitätsmodell.

1. Toolkit-Altlogik (temporäres NPC-Team + Reset-Makro) entfernen und durch
   persistente Kontinuitätsregeln ersetzen.
2. Save-v7-/Kontinuitätstexte um `npc_roster[]`/`active_npc_ids[]` und
   NPC-Lagebild bei Mehrfach-Load ergänzen.
3. Physicality-Wording im Cinematic-Start bei Solo-Begleitern harmonisieren.
4. Anschlussfähigkeit über Statusmatrix + Known-Issues + QA-Log dokumentieren.

# Checkliste

- [x] `systems/toolkit-gpt-spielleiter.md` auf persistente NPC-Kontinuität umgestellt.
- [x] `meta/masterprompt_v6.md` um NPC-Kontinuitätsfelder und Regeln erweitert.
- [x] `systems/gameflow/speicher-fortsetzung.md` mit NPC-Kapsel + Slot-Regel + 5er-Rückblick aktualisiert.
- [x] `systems/gameflow/cinematic-start.md` auf Physicality-konformes Begleiter-Wording harmonisiert.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` mit NPC/MMO-Anschlussblock ergänzt.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 94 fortgeschrieben.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 94 schließt den größten verbleibenden Kontinuitätsbruch für
NPC-Chrononauten in den SSOT-Texten: Keine temporären Solo-Sonderpfade mehr,
kein Progress-Reset im Gruppenjoin-Pseudocode und ein klarer, kompakter
Persistenzpfad für wiederkehrende NPC-Mitagenten.
