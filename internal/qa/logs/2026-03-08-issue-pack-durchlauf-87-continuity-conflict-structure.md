---
title: "QA-Log 2026-03-08 – Durchlauf 87 (Continuity-Conflict Struktur + Lineage-Restdrift)"
status: "abgeschlossen"
run_id: "zr-018-d87"
---

# Kontext

Nach den Durchläufen 81–86 war die Session-Anker-Semantik inhaltlich stabil,
aber der Konfliktpfad bei doppelten `characters[].id` blieb textlich teilweise
als singuläres `continuity_conflict` formuliert. Für robuste QA und klare
Auswertung wurde ein strukturierter Save-Pfad benötigt.

# Umgesetzte Änderungen

1. **Schema-Härtung für Konfliktprotokoll**
   - `systems/gameflow/saveGame.v7.schema.json`
   - `logs.flags.continuity_conflicts[]` als strukturierter Array-Pfad ergänzt
     (`char_id`, `anchor_save_id`, `incoming_save_id`, `resolution`, `note`).

2. **SSOT-/Runtime-Texte nachgezogen**
   - `meta/masterprompt_v6.md`
   - `systems/gameflow/speicher-fortsetzung.md`
   - `core/sl-referenz.md`
   - Singuläre `continuity_conflict`-Nennungen auf
     `logs.flags.continuity_conflicts[]` harmonisiert; Beispiel-Lineage von
     `HOST-main` auf `ANCHOR-main` umgestellt.

3. **Fixtures + Guards synchronisiert**
   - `internal/qa/fixtures/savegame_v7_*.json`
   - `tools/test_v7_schema_consistency.js`
   - `tools/test_v7_issue_pack.js`
   - Alle v7-Fixtures führen jetzt `logs.flags.continuity_conflicts: []`; beide
     Guard-Skripte prüfen das Feld als Pflichtbestandteil.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core systems meta/masterprompt_v6.md README.md internal/qa/plans internal/qa/logs`
   - Ergebnis: **grün**

# Bewertung

Das Continuity-Redesign ist nun auch auf Save-/Fixture-/Guard-Ebene konsistent:
Dedupe-Divergenzen sind strukturiert auswertbar, dokumentiert und testbar,
ohne die Session-Anker-Mechanik oder bestehende Invarianten zu verändern.
