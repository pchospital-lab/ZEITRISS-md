# Fahrplan – Durchlauf 190 (v7-SSOT-Härtung & Sync-Cleanup)

## Kontext

Der aktuelle Hard-Review-Stand ist spielbereit, hat aber noch letzte
Formdrifts im Save-Contract (Doku vs. Schema/Fixtures/Guards) und zwei kleine
Text-Unsyncs im HQ-/Setup-Flow.

## Ziel

- Save-v7 als **eine Wahrheit** auf den schlanken Exportpfad ziehen.
- Strukturdrift in der Save-Doku entfernen (Root vs. Character-Scope).
- Schema/Fixtures/Tests auf denselben verpflichtenden v7-Contract schärfen.
- Kleine Flow-Unsyncs in Kampagnen-/Playtest-Doku bereinigen.

## Arbeitspakete

1. `systems/gameflow/speicher-fortsetzung.md`
   - Kompakt-Profil explizit als Root-Struktur schärfen.
2. `systems/gameflow/saveGame.v7.schema.json`
   - `location` aus Root entfernen (Runtime-only),
   - Lineage + Root-Blöcke (`summaries`, `continuity`, `arc`, `ui`) verpflichten,
   - `summaries.summary_active_arcs` als String vereinheitlichen.
3. `internal/qa/fixtures/savegame_v7_*.json`
   - auf denselben Exportcontract normieren (ohne `location`/`phase`, mit
     Pflicht-Lineage + Root-Blöcken).
4. `tools/test_v7_schema_consistency.js` und `tools/test_v7_issue_pack.js`
   - Prüfungen auf den gehärteten Vertrag synchronisieren.
5. `gameplay/kampagnenstruktur.md`, `docs/qa/tester-playtest-briefing.md`
   - Auto-Briefing-Satz und 19-vs-20-Module-Unsync beheben.
6. Pflichtcheck `bash scripts/smoke.sh` ausführen.

## Abnahme

- Pflicht-Smoke läuft vollständig grün.
- V7-Schema/Fixures/Guards erzwingen denselben Root-/Lineage-Vertrag.
- Kein Widerspruch mehr bei HQ-Save-Flow und WS-Modulzahl in den
  relevanten Dokus.
