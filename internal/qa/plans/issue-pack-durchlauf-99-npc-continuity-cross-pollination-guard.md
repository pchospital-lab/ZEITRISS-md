---
title: "Issue-Pack Durchlauf 99 – NPC-Kontinuität Cross-Pollination-Guard"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-98-sl-referenz-npc-schema-alignment.md"
---

# Ziel

Die letzten Unterdefinitionen aus dem NPC/MMO-Review schließen, damit die
NPC-Kontinuitätsregeln in den SSOT-nahen Kerntexten nicht nur Datenfelder,
sondern auch klare Join/Leave- und Offscreen-Fortwirkungsguards enthalten.

1. Join/Leave-Guard (`personal|session|iti`) im Masterprompt explizit
   verankern.
2. Offscreen-Cross-Pollination (kompakter Hook bei Rückkehr) in den
   Kontinuitätsregeln festziehen.
3. Speichermodul + SL-Kurzreferenz auf dieselben Guard-Aussagen harmonisieren.

# Checkliste

- [x] `meta/masterprompt_v6.md` um Join/Leave- und Cross-Pollination-Guard ergänzt.
- [x] `systems/gameflow/speicher-fortsetzung.md` um NPC-Cross-Pollination-Beat ergänzt.
- [x] `core/sl-referenz.md` um Join/Leave-Guard + Offscreen-Rückkehrregel ergänzt.
- [x] `internal/qa/process/known-issues.md` und
      `internal/qa/process/continuity-redesign-statusmatrix.md` um Durchlauf 99 ergänzt.
- [x] Pflicht-Smoke ausgeführt.

# Abschluss

Durchlauf 99 schließt die inhaltliche Restlücke zwischen „Schema vorhanden“
und „Verhalten klar geregelt“: NPCs sind jetzt auch in den kompakten
Referenztexten als persistente Akteure mit eindeutigen Übergangsregeln und
begrenzter Offscreen-Fortwirkung beschrieben.
