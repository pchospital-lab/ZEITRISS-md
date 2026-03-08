---
title: "Issue-Pack Durchlauf 87 – Continuity-Conflict Struktur + Lineage-Restdrift"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-86-ws-session-anchor-restdrift.md"
---

# Ziel

Den Continuity-Redesign-Stand für Dedupe-Konflikte formal härten: statt
nur singulärer `continuity_conflict`-Hinweise wird ein strukturiertes
Konfliktarray in `logs.flags` verankert. Zusätzlich verbleibende
Lineage-Terminologie im SSOT-Beispiel (`HOST-main`) auf Session-Anker
harmonisieren.

1. Strukturfeld `logs.flags.continuity_conflicts[]` in Schema + Templates verankern.
2. SSOT-/Referenztexte von singulärem Konflikthinweis auf strukturierten Flags-Pfad umstellen.
3. v7-Fixtures + Guard-Tests auf das neue Pflichtfeld nachziehen.
4. Pflichtchecks erneut laufen lassen und Anschlusslauf dokumentieren.

# Checkliste

- [x] `systems/gameflow/saveGame.v7.schema.json` um `logs.flags.continuity_conflicts[]` ergänzt.
- [x] `meta/masterprompt_v6.md`, `systems/gameflow/speicher-fortsetzung.md`, `core/sl-referenz.md` auf strukturierten Konfliktpfad harmonisiert.
- [x] Alle `internal/qa/fixtures/savegame_v7_*.json` enthalten `logs.flags.continuity_conflicts`.
- [x] `tools/test_v7_schema_consistency.js` und `tools/test_v7_issue_pack.js` prüfen das neue Pflichtfeld.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 87 schließt den Restspalt zwischen Narrativregel und Save-Struktur:
Divergente Charakter-Doppelstände werden jetzt konsistent als strukturierte
Konfliktliste (`logs.flags.continuity_conflicts[]`) dokumentiert und getestet.
