---
title: "Issue-Pack Durchlauf 98 – SL-Referenz NPC-Schema-Alignment"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-97-npc-squad-persistence-alignment.md"
---

# Ziel

Die technische Save-v7-Kurzreferenz in `core/sl-referenz.md` an den bereits
kanonisierten NPC-Kontinuitätsvertrag angleichen, damit KI-SL und Review-Läufe
beim Schema nicht auf einen veralteten, unvollständigen Block zurückfallen.

1. `continuity`-Block mit `npc_roster[]` + `active_npc_ids[]` in der
   Save-Kurzreferenz ergänzen.
2. Kontinuitäts-Budgets sowie Scope-/Status-Enums der NPC-Chrononauten im
   Referenztext festschreiben.
3. Slotregel (Mensch-vor-NPC) und NPC-Lagebild im Kontinuitätsrückblick als
   Runtime-Hinweis ergänzen.

# Checkliste

- [x] `core/sl-referenz.md` auf den v7-NPC-Kontinuitätsvertrag harmonisiert.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 98 ergänzt.
- [x] Pflicht-Smoke ausgeführt.

# Abschluss

Durchlauf 98 schließt eine SSOT-Lücke in der SL-Referenz: Das technische
Save-v7-Schema listet nun dieselben NPC-Kontinuitätsfelder und Guards wie
Masterprompt, Speichermodul und Toolkit, wodurch Anschlussarbeit konsistenter
reviewbar bleibt.
