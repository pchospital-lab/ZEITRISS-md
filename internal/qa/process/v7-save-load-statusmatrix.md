---
title: "ZR-017 Statusmatrix – Save/Load v7 Issue-Pack"
version: 0.1.0
tags: [qa, process]
---

# ZR-017 Statusmatrix – Save/Load v7 Issue-Pack

Ziel: Der Stand aus den Durchläufen 39–55 wird pro Upload-Issue (1–10)
kompakt sichtbar gemacht, damit Folge-Durchläufe ohne Kontextverlust anschließen.

## Legende

- **abgeschlossen:** dokumentiert + Pflicht-Smoke grün.
- **abgeschlossen (revalidiert):** abgeschlossen und in späteren Durchläufen
  erneut per Doku-/Fixture-/Guard-Checks bestätigt.

## Status je Upload-Issue

| Upload-Issue | Kurzname | Status | Kernentscheidung | Evidenzläufe |
| --- | --- | --- | --- | --- |
| 1 | Save-v7-SSOT vereinheitlichen | abgeschlossen (revalidiert) | Exportkanon auf `v`+`zr`, `campaign.mission`, `characters[].attr`, `arc.{factions,questions,hooks}`, `summaries.*`; Legacy nur Import-Bridge. | 39, 48, 53, 54, 55 |
| 2 | OpenWebUI vs Runtime-Komfort trennen | abgeschlossen (revalidiert) | Chat-only Standard ist `!save` im HQ + JSON-Paste (optional `Spiel laden`); Runtime-Komfort nicht kanonisch. | 39, 46, 47 |
| 3 | Parallel-Core-Branches regeln/verbieten | abgeschlossen | Kanonischer Standard bleibt: Split/Merge erst nach Episodenende für Rift-Ops; Mid-Episode-Core-Branches non-canonical. | 41, 42, 44, 52 |
| 4 | Mixed Split/Merge formalisieren | abgeschlossen (revalidiert) | 6-stufiges Präzedenzmodell + Allowlist + Importreason `non_canonical_branch`. | 52, 53 |
| 5 | Arena-Savegrenze vereinheitlichen | abgeschlossen | Save nach PvP erlaubt bei normalisiertem Zustand (`arena.active=false`, Queue auf `idle|completed`). | 45 |
| 6 | Save-Größenbudget für Highend | abgeschlossen | Rolling-Caps für Logs/Arc/History + persistente `summaries.*`-Verdichtung. | 49 |
| 7 | Character-Dedupe + Lineage | abgeschlossen | Pflichtfelder `save_id/parent_save_id/merge_id/branch_id`; Dedupe über `imported_saves[]` und Duplicate-Flags. | 48, 52 |
| 8 | Px bei Split/Merge stabilisieren | abgeschlossen | Zustandsautomat `campaign.px_state` (`stable|pending_reset|consumed`) mit Merge-Priorität gegen Reanimation. | 50 |
| 9 | Economy-Bänder vereinheitlichen | abgeschlossen | Kanonische Highlevel-Bänder auf `120/512/900+` harmonisiert. | 51 |
| 10 | Vollständige v7-Teststrecke | abgeschlossen (revalidiert) | 5er-v7-Fixtures + Refusal-Fall + Smoke-Integration (`test_v7_issue_pack`, `test_v7_schema_consistency`). | 51, 52, 54 |

## Watchpoints für Folge-Durchläufe

1. **SSOT-Drift verhindern:** Bei jeder Save-Textänderung immer gleichzeitig
   Masterprompt, Save-Doku, SL-Referenz und Fixture-Guards querprüfen.
2. **Legacy strikt einhegen:** Legacy-Felder nur als Import-Bridge erwähnen,
   nie wieder als Exportbeispiel.
3. **OpenWebUI-Betriebsklarheit halten:** Chat-only Standard (`!save` +
   JSON-Paste) nicht durch Runtime-Komfortbegriffe verwässern.
4. **Merge-Risikoabsicherung:** Bei neuen Branch-Features immer Dedupe/Lineage,
   Allowlist und `imported_saves[]`-Transparenz mitdenken.

## Verknüpfung

- Fahrplan: `internal/qa/plans/issue-pack-durchlauf-56.md`
- Log: `internal/qa/logs/2026-03-08-issue-pack-durchlauf-56.md`
- Prozessanker: `internal/qa/process/known-issues.md` (ZR-017)
