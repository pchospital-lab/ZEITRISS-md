---
title: "Issue-Pack Fahrplan – Durchlauf 34"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 34

Quelle: Fortsetzung ZR-016 mit Fokus auf Issue 1 (Save-v7 als einzige
Runtime-Wahrheit) und Issue 6 (Drift-Guard) aus
`uploads/ZEITRISS_codex_issue_pack.md`.

## Ziel

Den letzten aktiven v6-Beispielblock aus dem geladenen Save-Modul entfernen,
damit das Runtime-Kontextfenster ausschließlich das kanonische v7-Exportmodell
zeigt. Parallel einen Guard ergänzen, der eingebettete v6-JSON-Rückfälle im
Save-Modul im Pflicht-Smoke erkennt.

## Scope dieses Durchlaufs

- `systems/gameflow/speicher-fortsetzung.md`
- `tools/lint_runtime.py`
- QA-Nachführung: Log + Known-Issues-Update

## Nicht im Scope

- Umbenennung von Legacy-Dateien (z. B. `masterprompt_v6.md`).
- Änderungen an Runtime-Importlogik für historische v6-Saves.
- Neue Save-Felder oder Änderungen am v7-Zielschema.

## Exit-Kriterium für Durchlauf 34

- Kein eingebettetes v6-JSON-Beispiel (`save_version: 6`, `economy.cu`,
  `arc_dashboard`) mehr im geladenen Save-Modul.
- Save-Modul enthält stattdessen einen klaren Migrationshinweis auf externe
  Dev-/Archiv-Referenzen bei gleichzeitigem v7-SSOT.
- Lint enthält einen Guard gegen eingebettete v6-JSON-Rückfälle in
  `systems/gameflow/speicher-fortsetzung.md`.
- `bash scripts/smoke.sh` läuft vollständig grün.
