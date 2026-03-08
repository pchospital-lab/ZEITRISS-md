---
title: "Issue-Pack Fahrplan – Durchlauf 54"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 54

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 1 Dauerabsicherung: v7-SSOT gegen Legacy-Regressionen).

## Ziel

1. Kanonisches v7-Schema als eigene Referenzdatei im Repo führen.
2. Drift-Guard ergänzen, der Legacy-Key-Regressionen in v7-Fixtures früh erkennt.
3. Save-Doku und SL-Referenz auf denselben Schema-Stand (v7 Export, v6 nur Import-Bridge) synchronisieren.

## Scope dieses Durchlaufs

- `systems/gameflow/saveGame.v7.schema.json`
  - Neue Schema-Referenz für kanonischen v7-Exportpfad (`v`, `zr`, `campaign.mission`, `characters[].attr`, `arc`, `summaries`).
- `tools/test_v7_schema_consistency.js`
  - Node-Driftguard für v7-Fixtures: Pflichtpfade vorhanden, Legacy-Felder verboten.
- `scripts/smoke.sh`
  - Driftguard in den Pflicht-Smoke aufnehmen.
- `systems/gameflow/speicher-fortsetzung.md`
  - Schema-Passage auf „v7 Export + v6 Legacy-Import-Bridge“ präzisieren.
- `core/sl-referenz.md`
  - Spiegelnde Präzisierung derselben Schema- und Bridge-Aussage.
- `internal/qa/process/known-issues.md`
  - ZR-017 um Durchlauf-54-Revalidierung ergänzen.

## Exit-Kriterium

- v7-Schema liegt als dedizierte Referenz im Repo vor.
- Pflicht-Smoke enthält einen automatischen Legacy-Key-Driftguard und läuft grün.
- Save-Doku und SL-Referenz beschreiben denselben Schema-Stand ohne widersprüchlichen Eindruck.
