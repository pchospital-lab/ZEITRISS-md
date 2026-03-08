---
title: "ZR-019 Statusmatrix – Kontinuitäts-Redesign (Session-Anker)"
version: 0.1.0
tags: [qa, process, continuity]
---

# ZR-019 Statusmatrix – Kontinuitäts-Redesign

Diese Matrix bündelt den Umsetzungsstand des Upload-Pakets
`uploads/ZEITRISS_continuity_save_redesign.md` für schnelle Anschlussläufe.

## Legende

- **abgeschlossen:** Umsetzung + Pflicht-Smoke dokumentiert.
- **verifiziert:** zusätzlich per Guard/Fixture/Follow-up gegen Drift abgesichert.
- **watchpoint:** kein akuter Defekt, aber bei Folgeänderungen gezielt mitprüfen.

## Issue-Status (Upload-Issues 1–8)

| Issue | Kurzinhalt | Status | Evidenz-Durchläufe | Primäre Evidenz |
| --- | --- | --- | --- | --- |
| 1 | Host-SSOT → Session-Anker-Semantik | verifiziert | 81, 82, 86, 88, 91, 92 | `internal/qa/logs/2026-03-08-issue-pack-durchlauf-81-continuity-redesign.md` |
| 2 | `continuity`-Block + Budgets | verifiziert | 81, 84 | `internal/qa/logs/2026-03-08-issue-pack-durchlauf-84-continuity-fixtures-guards.md` |
| 3 | Multi-Load-Pipeline (Anchor + Character Authority + Fabric) | verifiziert | 81, 87, 90 | `internal/qa/logs/2026-03-08-issue-pack-durchlauf-87-continuity-conflict-structure.md` |
| 4 | Kanonisches Core-Split-Protokoll (`family_id`) | verifiziert | 81, 84, 89 | `internal/qa/logs/2026-03-08-issue-pack-durchlauf-89-continuity-output-contract-guard.md` |
| 5 | `convergence_tags[]` als Branch-Auswirkung | verifiziert | 81, 84, 89 | `internal/qa/fixtures/continuity_output_contract_multi_load.json` |
| 6 | Duplicate Character Rejoin statt Hard-Block | verifiziert | 81, 87 | `internal/qa/logs/2026-03-08-issue-pack-durchlauf-87-continuity-conflict-structure.md` |
| 7 | Pflicht-Recap `Kontinuitätsrückblick` | verifiziert | 81, 83, 89 | `tools/test_continuity_output_contract.js` |
| 8 | Pflichtbeats (Split/Rejoin/Echo-Follow-up) | verifiziert | 83, 89 | `internal/qa/logs/2026-03-08-issue-pack-durchlauf-83-continuity-beats-echo-followup.md` |

## Aktuelle Watchpoints

1. **Playtest-Prompts driftarm halten:** operative QA-Skripte sollten
   Session-Anker-Wording nutzen, damit neue Evidenz keine Altbegriffe erneut
   einführt.
2. **Bei Runtime-Merge-Änderungen immer drei Ebenen prüfen:**
   `runtime.js` + SSOT-Texte (`meta/masterprompt_v6.md`,
   `systems/gameflow/speicher-fortsetzung.md`) + Guards/Fixtures.
3. **Kontinuitäts-Output-Contract bleibt Pflicht:**
   `tools/test_continuity_output_contract.js` muss im Smoke aktiv bleiben.
