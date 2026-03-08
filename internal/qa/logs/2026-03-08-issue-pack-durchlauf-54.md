---
title: "QA-Log – Issue-Pack Durchlauf 54"
date: 2026-03-08
scope: "Issue 1 Dauerabsicherung: v7-SSOT Driftguard"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- Upload-Issue-Pack: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 1).
- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-54.md`.

## Umsetzung in diesem Durchlauf

1. **Kanonisches v7-Schema als Referenz ergänzt**
   - Neue Datei `systems/gameflow/saveGame.v7.schema.json` angelegt.
   - Enthält den exportseitigen Pflichtbaum inkl. `v`, `zr`, Lineage-Felder,
     `campaign.mission`, `characters[].attr`, `arc` und `summaries`.

2. **Automatischer SSOT-Driftguard eingeführt**
   - Neues Prüfskript `tools/test_v7_schema_consistency.js` prüft alle
     v7-Fixtures gegen den kanonischen Feldpfad und blockiert Legacy-Keys
     (`save_version`, `zr_version`, `mission_in_episode`, `attributes`,
     `arc_dashboard`, `arc.open_*`) im v7-Export.

3. **Pflicht-Smoke erweitert**
   - `scripts/smoke.sh` führt den neuen Driftguard aus
     (`node tools/test_v7_schema_consistency.js` → `v7-schema-consistency-ok`).

4. **Doku-/SL-Synchronisierung nachgezogen**
   - `systems/gameflow/speicher-fortsetzung.md` und `core/sl-referenz.md`
     unterscheiden jetzt klar: v7-Schema ist Export-Referenz, v6-Schema bleibt
     Legacy-Import-Bridge für Runtime/Loader-Fehlertexte.

5. **Known-Issues fortgeschrieben**
   - `internal/qa/process/known-issues.md` enthält den Verweis auf
     Durchlauf 54 als Revalidierung ohne Kanonwechsel.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.

## Ergebnis / Anschluss

- V7-Export-Schema und CI-Driftguard sind jetzt als wiederholbare
  Qualitätsschranke dokumentiert.
- Folge-Durchläufe können auf dem neuen Guard aufsetzen und gezielt
  inhaltliche Regeln statt Feldnamens-Drift auditieren.
