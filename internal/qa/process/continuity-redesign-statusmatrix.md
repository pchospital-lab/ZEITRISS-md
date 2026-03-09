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
| Save v7: `continuity.npc_roster[]` + `active_npc_ids[]` | verifiziert | 94, 104 | `tools/test_npc_continuity_consistency.js` |
| Mischgruppen-Slotlogik Mensch-vor-NPC + NPC-Lagebild beim Rejoin | verifiziert | 94 | `systems/gameflow/speicher-fortsetzung.md` |
| Physicality-Wording (Hologramm ↔ Linse/Comlink/HQ-Projektion) | verifiziert | 94, 95, 96, 101, 102, 103, 106, 107 | `tools/test_physicality_watchguard.js` |
| Kampagnenstruktur: Solo-/NPC-Squad-Wording auf Persistenzkanon | verifiziert | 97 | `gameplay/kampagnenstruktur.md` |
| SL-Referenz: Save-v7-Kurzschema um NPC-Kontinuitätsblock ergänzt | verifiziert | 98 | `core/sl-referenz.md` |
| NPC-Verhaltensguard: Join/Leave + Cross-Pollination in SSOT-Kerntexten | verifiziert | 99, 100, 104 | `internal/qa/fixtures/npc_continuity_output_contract.json` |
| Spieler-Handbuch: `npc-team`-Persistenz im Player-Startpfad sichtbar | verifiziert | 105 | `core/spieler-handbuch.md` |
| Kausalabfang ("Never happened") als Cleanup-SSOT über WS-Module | verifiziert | 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 120 | `tools/test_kausalabfang_watchguard.js` |

**Neue Watchpoints:**
1. NPC-v7-Feldanker über Pflicht-Smoke halten: `tools/test_npc_continuity_consistency.js` darf nicht aus `scripts/smoke.sh` entfernt werden.
2. Bei Start-/Merge-Pseudocode keine stillen Resets von `campaign.px`, `campaign.rift_seeds` oder `arc.open_seeds` einführen.
3. Mehrfach-Load-Rückblick darf das NPC-Lagebild nicht verlieren (5-Block-Ausgabe bleibt Pflicht).
4. Cinematic-Start-Wording muss Linse-HUD und HQ-Projektionsflächen semantisch trennen (keine hybriden Default-Begriffe; Evidenzlauf 106).
5. `gameplay/kampagnenstruktur.md` bei Solo-/NPC-Textänderungen gegen den Persistenzkanon halten (`npc-team` als regulärer Startpfad, Drohne nur Fallback).
6. Join/Leave-Logik (`personal|session|iti`) und Offscreen-Cross-Pollination (max. 1 Hook) in Masterprompt, Speichermodul und SL-Referenz parallel halten.
7. NPC-Departure/NPC-Recognition als explizite Pflichtbeats auch im Masterprompt erhalten (Abgang nicht stumm, Wiederkehr mit konkretem Wiedererkennungsanker).
8. Lore-Core (`core/zeitriss-core.md`) bei HQ-/Trainingswörtern gegen den Physicality-Guard mitprüfen (keine freischwebenden Hologramm-Defaults).
9. Spielernahe Startdoku (`core/spieler-handbuch.md`) bei `npc-team`-Textänderungen auf den NPC-Persistenzkanon prüfen (Menschen-vor-NPC, HQ/Offscreen-Fortbestand, kompakte Offscreen-Fortschreibung).
10. Physicality-Guard im Pflicht-Smoke halten: `tools/test_physicality_watchguard.js` darf nicht aus `scripts/smoke.sh` entfernt werden.
11. Kausalabfang-Minimalregel bei Loot/Cleanup-Änderungen mitprüfen: Reihenfolge bleibt `Loot sichern → optional Kausalabfang → Cleanup/Exfil`; Sperren (Boss/Chrononauten/Zivilisten/Para/Arena-PvP/Chronopolis) dürfen nicht aufweichen.
12. Kausalabfang-Watchguard im Pflicht-Smoke halten: `tools/test_kausalabfang_watchguard.js` darf nicht aus `scripts/smoke.sh` entfernt werden.
13. Bei Kausalabfang-Textänderungen Echo-/Kodex-Hardening mitprüfen: `Named-Target-Echo` (max. 1 Nachhall) und kurze Kodex-Phrasen (`Identitätslock bestätigt`, `Kausalabfang freigegeben`) in Toolkit + Masterprompt parallel halten.
14. Kausalabfang als ITI-Infra halten: Anti-Kampfanker (kein Kampfwerkzeug), Nahdistanz/Identitätsfassung/Kodex-Uplink sowie Nicht-Shop-/Nicht-Pflichtinventar-Setzung (`core/sl-referenz.md`, `characters/ausruestung-cyberware.md`) bei Textänderungen mitprüfen.
15. Kausalabfang-Abfangfenster eng halten: Formulierung **Sekunden bis wenige Minuten** (vor Einsatzkontakt) in Spieler-Handbuch, Toolkit und Masterprompt parallel halten; keine Ausweitung auf lange Retcon-Zeiträume.

16. Kodex-Archivanker beim Kausalabfang stabil halten: `Kodex: Lokale Erinnerung driftet. Archivanker aktiv.` in Toolkit + Masterprompt parallel führen (kein Spektakel-Wording).
17. Named-vs.-Unnamed-Cleanup-Flow beim Kausalabfang stabil halten: in Toolkit + Masterprompt muss `unbenannte Hostiles automatisch, benannte Ziele nachfragen` explizit erhalten bleiben (Watchguard-Regex aus Durchlauf 114).
18. TEMP-Recall-Blur beim Kausalabfang als reiner Flavor halten: TEMP-Staffelung (`1–2 Blur`, `3–5 Déjà-vu`, `6+ fast stabil`) in Toolkit + Masterprompt parallel führen, ohne Zusatzwürfe/Strafmechanik (Watchguard-Regex aus Durchlauf 115).
19. Named-Target-Echo-Storage beim Kausalabfang dual halten: In Toolkit + Masterprompt muss der Nachhall benannter Ziele weiter auf `logs.trace[]`/`logs.notes[]` **oder** `continuity.roster_echoes[]` / `continuity.shared_echoes[]` verankert bleiben (Watchguard-Regex aus Durchlauf 116).
20. Kausalabfang explizit anti-retcon halten: in allen fünf Kernmodulen muss der Anker „kein universelles Retcon-Werkzeug“ (oder äquivalentes Wording) erhalten bleiben; Watchguard-Pflichtregex aus Durchlauf 117 nicht auf Negativprüfung zurückbauen.
21. Kausalabfang-Motiv-/Lagefenster stabil halten: in allen fünf Kernmodulen muss der Anker **Tatmotivation und Einsatzlage bleiben gleich** erhalten bleiben; Watchguard-Pflichtregex aus Durchlauf 118 nicht entfernen.

22. Kausalabfang-Leitmotiv sprachlich stabil halten: in allen fünf Kernmodulen muss der Positivanker **Festnahme statt Löschung** erhalten bleiben; Watchguard-Pflichtregex aus Durchlauf 120 nicht entfernen.


## Anschluss-Checkliste vor dem nächsten Deepsearch-Lauf

1. Pflichtcheck ausführen: `bash scripts/smoke.sh` (inkl. Tokens `physicality-watchguard-ok` und `kausalabfang-watchguard-ok`).
2. Nur bei Prozessdateien: `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`.
3. Bei Regeltext-Änderungen immer SSOT-parallel in den fünf Kernmodulen prüfen (Spieler-Handbuch, SL-Referenz, Toolkit, Masterprompt, Ausrüstung).
4. Neue Durchläufe in **Plan + Log + known-issues + Statusmatrix** synchron nachziehen, damit Anschlussläufe ohne Kontextverlust starten können.
