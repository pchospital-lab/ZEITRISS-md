---
title: "Issue-Pack Fahrplan – Durchlauf 48"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 48

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 7: Dedupe + Merge-Lineage).

## Ziel

Split/Merge-Importe gegen Doppel-Saves und doppelte Charaktere härten, ohne den
bestehenden kanonischen Host-SSOT-Pfad aufzubrechen.

## Scope dieses Durchlaufs

- `meta/masterprompt_v6.md`: v7-JSON-Template um Lineage-Felder ergänzen
  (`save_id`, `parent_save_id`, `merge_id`, `branch_id`) und Dedupe-Regeln
  explizit machen.
- `systems/gameflow/speicher-fortsetzung.md`: Kompakt-Profil und Merge-Abschnitt
  um Import-Lineage, `imported_saves[]` und Konfliktflags ergänzen.
- `core/sl-referenz.md`: operative KI-SL-Regeln für Dedupe/Lineage spiegeln.
- `README.md`: kurzer Hinweis für Maintainer auf Merge-Dedupe-Grenzen.
- `internal/qa/process/known-issues.md`: ZR-017-Notiz auf Durchlauf 48 erweitern.
- Pflicht-Smoke ausführen.

## Exit-Kriterium

- V7-Dokumente nennen dieselben Lineage-Schlüssel (`save_id`,
  `parent_save_id`, `merge_id`, `branch_id`).
- Duplicate-Save und Duplicate-Character sind als sichtbare Konfliktfälle
  dokumentiert (`duplicate_branch_detected`, `duplicate_character_detected`,
  `imported_saves[]`).
- Pflicht-Smoke bleibt grün.
