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


## NPC/MMO-Follow-up (Upload 2026-03-09)

Quelle: `uploads/ZEITRISS_npc_mmo_immersion_review.md`

| Schwerpunkt | Status | Evidenz-Durchlauf | Primäre Evidenz |
| --- | --- | --- | --- |
| Toolkit: temporären Solo-NPC-Pfad + Reset-Makro entfernen | verifiziert | 94 | `systems/toolkit-gpt-spielleiter.md` |
| Save v7: `continuity.npc_roster[]` + `active_npc_ids[]` | verifiziert | 94 | `meta/masterprompt_v6.md` |
| Mischgruppen-Slotlogik Mensch-vor-NPC + NPC-Lagebild beim Rejoin | verifiziert | 94 | `systems/gameflow/speicher-fortsetzung.md` |
| Physicality-Wording (Hologramm ↔ Linse/Comlink/HQ-Projektion) | verifiziert | 94, 95, 96 | `systems/gameflow/cinematic-start.md` |
| Kampagnenstruktur: Solo-/NPC-Squad-Wording auf Persistenzkanon | verifiziert | 97 | `gameplay/kampagnenstruktur.md` |
| SL-Referenz: Save-v7-Kurzschema um NPC-Kontinuitätsblock ergänzt | verifiziert | 98 | `core/sl-referenz.md` |

**Neue Watchpoints:**
1. Bei künftigen Save-v7-Änderungen immer `continuity.npc_roster[]`/`active_npc_ids[]` gegen Masterprompt und Speichermodul parallel prüfen.
2. Bei Start-/Merge-Pseudocode keine stillen Resets von `campaign.px`, `campaign.rift_seeds` oder `arc.open_seeds` einführen.
3. Mehrfach-Load-Rückblick darf das NPC-Lagebild nicht verlieren (5-Block-Ausgabe bleibt Pflicht).
4. Cinematic-Start-Wording muss Linse-HUD und HQ-Projektionsflächen semantisch trennen (keine hybriden Default-Begriffe).
5. `gameplay/kampagnenstruktur.md` bei Solo-/NPC-Textänderungen gegen den Persistenzkanon halten (`npc-team` als regulärer Startpfad, Drohne nur Fallback).
