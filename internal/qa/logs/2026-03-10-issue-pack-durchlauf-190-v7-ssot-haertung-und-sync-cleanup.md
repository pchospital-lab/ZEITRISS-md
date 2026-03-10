# QA-Log – Durchlauf 190 (v7-SSOT-Härtung & Sync-Cleanup)

## Ausgangslage

Nach den Hard-Final-Review-Läufen blieb eine Restdrift im Save-v7-Vertrag:
Doku, Schema, Fixtures und Guard-Tests zeigten unterschiedliche Härtegrade
(inkl. Root-`location`/`phase` und uneinheitlicher Lineage-/Summary-Form).
Zusätzlich waren zwei kleine Text-Unsyncs offen (Auto-Briefing-Satz,
19-vs-20-WS-Module).

## Umsetzung

- Save-Doku präzisiert:
  - `systems/gameflow/speicher-fortsetzung.md` benennt im Kompakt-Profil
    jetzt explizit, dass `economy/logs/summaries/continuity/arc/ui/arena`
    Root-Blöcke sind und nicht unter `characters[]` hängen.
- Schema gehärtet:
  - `systems/gameflow/saveGame.v7.schema.json` entfernt Root-`location`,
    verlangt verpflichtend Lineage (`save_id`, `parent_save_id`, `merge_id`,
    `branch_id`) und verpflichtet die Root-Blöcke
    `summaries/continuity/arc/ui`.
  - `summaries.summary_active_arcs` ist als String fixiert.
  - `continuity.npc_roster[]` und `continuity.active_npc_ids[]` sind als
    Pflichtanker enthalten.
- V7-Fixtures synchronisiert:
  - `internal/qa/fixtures/savegame_v7_*.json` ohne Root-`location`/`phase`,
    mit vollständiger Lineage und Root-Blöcken (`summaries`, `continuity`,
    `arc`, `ui`) vereinheitlicht.
- Guard-/Issue-Pack-Tests nachgezogen:
  - `tools/test_v7_schema_consistency.js` und
    `tools/test_v7_issue_pack.js` prüfen jetzt den gehärteten Vertrag
    (Lineage-Pflicht, String-Typ für `summary_active_arcs`, kein
    `location`/`phase` im Export).
- Kleine Sync-Fixes:
  - `gameplay/kampagnenstruktur.md`: Auto-HQ-Satz korrigiert auf
    **kein** automatischer Briefing-Sprung nach Save.
  - `docs/qa/tester-playtest-briefing.md`: Setup-Text von
    „20 WS-Module“ auf „19 WS-Module“ korrigiert.

## Ergebnis

- Der Save-v7-Vertrag ist über Doku, Schema, Fixtures und Guard-Checks wieder
  deckungsgleich auf einen schlanken, autoritativen HQ-Export ausgerichtet.
- Die beiden dokumentarischen Flow-Unsyncs sind bereinigt.
- Pflicht-Smoke lief vollständig grün.

## Pflicht-Checks

- `bash scripts/smoke.sh` → `All smoke checks passed.`
