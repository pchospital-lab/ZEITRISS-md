---
title: "Issue-Pack Fahrplan – Durchlauf 16"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 16

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Issue 13 (Item-Registry-Layer) als kleinen, risikoarmen SSOT-Schritt
vorziehen: Runtime-Texte sollen ein kanonisches Registry-Muster benennen,
ohne das bestehende Save-Pflichtformat `{name,type,tier}` zu brechen.

## Scope dieses Durchlaufs

- Registry-SSOT in Runtime-Modulen verankern:
  - `characters/ausruestung-cyberware.md`
  - `meta/masterprompt_v6.md`
  - `core/sl-referenz.md`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-06-issue-pack-durchlauf-16.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Vollständige Item-Katalog-Migration auf IDs in allen Loot-/Shop-Tabellen.
- Neue Pflichtfelder im Save-Schema v7 (kein Breaking Change).
- Tooling für Registry-Build oder Auto-Validierung einzelner Item-IDs.

## Exit-Kriterium für Durchlauf 16

- Runtime-Kanon benennt ein einheitliches Registry-Muster mit `id`,
  `display_name`, `type`, `tier`, `cost` (optional `tags`, `alt_skin`).
- Save-Export bleibt explizit kompatibel mit `equipment[{name,type,tier}]`.
- Optionale Felder `item_id`/`skin` sind als Zusatzpfad dokumentiert.
- `bash scripts/smoke.sh` ist grün.
