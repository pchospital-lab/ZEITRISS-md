---
title: "Known-Issues Durchlaufhistorie (73–156)"
date: 2026-03-10
status: archiv
source: internal/qa/process/known-issues.md
---

# Zweck

Archiv der aus `known-issues.md` ausgelagerten Detailchronik für die Durchläufe 73–156.
Die operative Triage bleibt in `internal/qa/process/known-issues.md`.

## Historische Durchlaufnotizen (ausgelagert)

- **Durchlauf 73 (2026-03-08):** Round-4-Review-Cluster abgearbeitet
  (Voice-SSOT, Save-v7-Persistenzklarheit, Px-Determinismus,
  Toolkit-Ruf/Tier-Korrektur, Absolut-Rahmensatz und Bonusmodule
  Signaturtell/Forensik-Dreieck). Dokumentiert in
  `internal/qa/plans/issue-pack-durchlauf-73-round4-ssot-harmonisierung.md`
  und `internal/qa/logs/2026-03-08-issue-pack-durchlauf-73-round4-ssot-harmonisierung.md`.

- **Durchlauf 74 (2026-03-08):** Round-4-Abschluss-Restdrift nachgezogen: v7-Beispiel in `core/zeitriss-core.md` auf `ui.voice_profile = gm_second_person` harmonisiert und Dispatcher-Semver-Hinweis in `systems/toolkit-gpt-spielleiter.md` auf kanonisches `zr` (mit Legacy-Normalisierung von `zr_version`) umgestellt; Pflicht-Smoke und Linklint erneut grün.

- **Durchlauf 75 (2026-03-08):** Round-4-Restklarheit nachgezogen: `core/sl-referenz.md` Persistenz-Bullet auf kanonische `characters[]`-Felder geschärft (Legacy-`character{}` nur als Import-Normalisierung), `systems/gameflow/speicher-fortsetzung.md` Legacy-HQ-Block explizit als nicht-kanonischen Neu-Export markiert und `gameplay/kampagnenstruktur.md` beim Chronopolis-Entry auf einmaligen In-World-Warnhinweis statt Warn-Cutscene harmonisiert; Pflicht-Smoke und Linklint erneut grün. Dokumentiert in `internal/qa/plans/issue-pack-durchlauf-75-round4-restklarheit-save-chronopolis.md` und `internal/qa/logs/2026-03-08-issue-pack-durchlauf-75-round4-restklarheit-save-chronopolis.md`.

- **Durchlauf 76 (2026-03-08):** HQ-Save/Reset-Klarstellung über die drei SSOT-Orte gezogen: `meta/masterprompt_v6.md`, `core/sl-referenz.md` und `systems/gameflow/speicher-fortsetzung.md` benennen jetzt explizit die Invariante „Speichern nur im HQ; Debrief-Reset von `stress`/`psi_heat`/`SYS` vor Save“, inklusive Begründung, warum `stress`/`psi_heat` trotz Reset im v7-Schema verbleiben (expliziter HQ-Status + stabile Legacy-/Import-Normalisierung). Pflicht-Smoke erneut grün. Dokumentiert in `internal/qa/plans/issue-pack-durchlauf-76-hq-save-reset-clarity.md` und `internal/qa/logs/2026-03-08-issue-pack-durchlauf-76-hq-save-reset-clarity.md`.

- **Durchlauf 77 (2026-03-08):** Round-4-Anschlusslauf in `systems/gameflow/speicher-fortsetzung.md`: Chronopolis-Makrotext auf einmaligen In-World-Warnhinweis (statt Warn-Popup) harmonisiert und SaveGuard-Pseudocode explizit als Runtime-/Legacy-Bridge vor v7-Normalisierung gekennzeichnet (kein kanonischer Neu-Export). Pflicht-Smoke + Linklint erneut grün. Dokumentiert in `internal/qa/plans/issue-pack-durchlauf-77-round4-anschluss-chronopolis-bridge.md` und `internal/qa/logs/2026-03-08-issue-pack-durchlauf-77-round4-anschluss-chronopolis-bridge.md`.

- **Durchlauf 78 (2026-03-08):** Round-4-Anschlusslauf zur Mystery-Tonverdichtung abgeschlossen: `gameplay/kampagnenuebersicht.md` im Abschnitt "Mystery-Contract von ZEITRISS" um den Signatursatz ergänzt ("Was im ersten Zugriff wie Fremdheit wirkt ... menschliche Zukunft"), um die gewünschte Erstlesart (Alien/Fremdheit) mit dem kanonischen Reveal (posthumane Fernzukunft) explizit zu bündeln; Pflicht-Smoke + Linklint erneut grün. Dokumentiert in `internal/qa/plans/issue-pack-durchlauf-78-round4-signatursatz-mystery-bridge.md` und `internal/qa/logs/2026-03-08-issue-pack-durchlauf-78-round4-signatursatz-mystery-bridge.md`.


- **Durchlauf 79 (2026-03-08):** Round-4-Anschlusslauf für SSOT-Feldnamen abgeschlossen: `systems/toolkit-gpt-spielleiter.md` setzt im Gruppenreset jetzt kanonisch `state.campaign.rift_seeds = []` (inkl. Legacy-/Dashboard-Spiegel `state.arc.open_seeds = []`), und `gameplay/kampagnenstruktur.md` nutzt in der Dev-Checkliste konsistent `len(campaign.rift_seeds)` statt ungebundener `open_seeds`-Kurzform; Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Round4 SSOT-Feldnamen-Restdrift): `internal/qa/plans/issue-pack-durchlauf-79-round4-ssot-feldnamen-restdrift.md`
- Log (Round4 SSOT-Feldnamen-Restdrift): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-79-round4-ssot-feldnamen-restdrift.md`


- **Durchlauf 80 (2026-03-08):** Round-4-Anschlusslauf zur Formatpflege abgeschlossen: Im Abschnitt „Para-Creature-Generator: Rift Casefile Edition" in `gameplay/kreative-generatoren-begegnungen.md` wurden Long-Line-Hotspots in mehrzeilige Listen/Bullets überführt (reine Lesbarkeitsverbesserung ohne Regel- oder SSOT-Änderung); Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Round4 Formatpflege Long-Lines): `internal/qa/plans/issue-pack-durchlauf-80-round4-formatpflege-long-lines.md`
- Log (Round4 Formatpflege Long-Lines): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-80-round4-formatpflege-long-lines.md`

- **Durchlauf 81 (2026-03-08):** Kontinuitäts-Redesign aus dem Upload-Paket in die SSOT-Kernstellen gezogen: `README.md`, `meta/masterprompt_v6.md`, `systems/gameflow/speicher-fortsetzung.md` und `core/sl-referenz.md` nutzen jetzt Session-Anker-Semantik, `continuity`-Kapsel (inkl. `split.family_id`) sowie Pflicht-`Kontinuitätsrückblick` für Mehrfach-Loads; Duplicate-Character-Fälle laufen als Rejoin-/`continuity_conflict` statt reiner Hard-Block. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kontinuitäts-Redesign): `internal/qa/plans/issue-pack-durchlauf-81-continuity-redesign.md`
- Log (Kontinuitäts-Redesign): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-81-continuity-redesign.md`

- **Durchlauf 82 (2026-03-08):** Session-Anker-Restdrift nach Durchlauf 81 abgeschlossen: `systems/gameflow/speicher-fortsetzung.md`, `meta/masterprompt_v6.md` und `core/sl-referenz.md` verwenden in Roster-/Merge-/Audit-Beschreibungen nun durchgehend Session-Anker-Semantik (u. a. `Session-Anker-Charakter = Index 0`, `session_anchor_level`, `anchor_value|anchor_wins`, `session_anchor_id`). Inhaltliche Regeln bleiben unverändert; Fokus war Terminologie-/SSOT-Konsistenz. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Session-Anker Restdrift): `internal/qa/plans/issue-pack-durchlauf-82-session-anchor-restdrift.md`
- Log (Session-Anker Restdrift): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-82-session-anchor-restdrift.md`

- **Durchlauf 83 (2026-03-08):** Follow-up zum Kontinuitäts-Redesign abgeschlossen: `meta/masterprompt_v6.md`, `systems/gameflow/speicher-fortsetzung.md` und `core/sl-referenz.md` verankern jetzt explizit die Szenenpflicht für Split-Beat/Rejoin-HQ-Beat sowie die Echo-Fortwirkungspflicht (mindestens ein importierter Echo-Eintrag innerhalb der nächsten zwei Sitzungsblöcke). Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kontinuitäts-Beats + Echo-Fortwirkung): `internal/qa/plans/issue-pack-durchlauf-83-continuity-beats-echo-followup.md`
- Log (Kontinuitäts-Beats + Echo-Fortwirkung): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-83-continuity-beats-echo-followup.md`


- **Durchlauf 84 (2026-03-08):** QA-/Fixture-Layer auf Kontinuitäts-Redesign nachgezogen: `systems/gameflow/saveGame.v7.schema.json` dokumentiert jetzt den `continuity`-Rootblock (`last_seen`, `split`, `roster_echoes`, `shared_echoes`, `convergence_tags` inkl. Budgetgrenzen), alle `internal/qa/fixtures/savegame_v7_*.json` enthalten die Kontinuitätskapsel, und die Regression-Guards (`tools/test_v7_schema_consistency.js`, `tools/test_v7_issue_pack.js`) prüfen Presence/Budget sowie kanonische Core-Split-Konvergenz statt Parallel-Core-Refusal. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Continuity-Fixtures + Guard-Härtung): `internal/qa/plans/issue-pack-durchlauf-84-continuity-fixtures-guards.md`
- Log (Continuity-Fixtures + Guard-Härtung): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-84-continuity-fixtures-guards.md`


- **Durchlauf 85 (2026-03-08):** Anschlusslauf zur Terminologie-Drift in der QA-Fixture-Schicht abgeschlossen: `internal/qa/fixtures/savegame_v7_split_3_2_merge.json` nutzt nun `ANCHOR-HQ-ALPHA` statt `HOST-HQ-ALPHA`; die Hinweistexte in `internal/qa/fixtures/savegame_v7_merge_rift_pvp.json` und `internal/qa/fixtures/savegame_v7_abort_resume.json` wurden auf Session-Anker-/Allowlist-Semantik harmonisiert. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Continuity-Fixture-Wording Session-Anker): `internal/qa/plans/issue-pack-durchlauf-85-continuity-fixture-wording-anchor.md`
- Log (Continuity-Fixture-Wording Session-Anker): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-85-continuity-fixture-wording-anchor.md`

- **Durchlauf 86 (2026-03-08):** Anschlusslauf zur WS-Restdrift nach dem Kontinuitäts-Redesign abgeschlossen: `core/spieler-handbuch.md` und `core/zeitriss-core.md` nutzen jetzt in Gruppen-/Save-Abschnitten konsistent Session-Anker-Semantik statt Host-SSOT-Wording (u. a. Gruppen-Px, Seed-Epoche, `characters[]` Index-0-Erklärung, Multi-Load-Regeltext). Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (WS-Session-Anker-Restdrift): `internal/qa/plans/issue-pack-durchlauf-86-ws-session-anchor-restdrift.md`
- Log (WS-Session-Anker-Restdrift): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-86-ws-session-anchor-restdrift.md`


- **Durchlauf 87 (2026-03-08):** Anschlusslauf zur Strukturhärtung des Continuity-Dedupe-Pfads abgeschlossen: `systems/gameflow/saveGame.v7.schema.json` führt jetzt `logs.flags.continuity_conflicts[]` als strukturiertes Konfliktarray; `meta/masterprompt_v6.md`, `systems/gameflow/speicher-fortsetzung.md` und `core/sl-referenz.md` referenzieren denselben Pfad konsistent (inkl. Lineage-Beispiel `ANCHOR-main`), und alle `internal/qa/fixtures/savegame_v7_*.json` plus Guards (`tools/test_v7_schema_consistency.js`, `tools/test_v7_issue_pack.js`) prüfen das Pflichtfeld. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Continuity-Conflict Struktur + Lineage-Restdrift): `internal/qa/plans/issue-pack-durchlauf-87-continuity-conflict-structure.md`
- Log (Continuity-Conflict Struktur + Lineage-Restdrift): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-87-continuity-conflict-structure.md`


- **Durchlauf 88 (2026-03-08):** Anschlusslauf zur Template-/Toolkit-Restdrift abgeschlossen: `meta/masterprompt_v6.md` und `systems/gameflow/speicher-fortsetzung.md` nutzen in den kanonischen v7-Beispielen jetzt `branch_id: ANCHOR-main` statt `HOST-main`; `systems/toolkit-gpt-spielleiter.md` wurde in Merge-/Dispatcher-Formulierungen auf Session-Anker-Wording harmonisiert (`Session-Anker-HQ-Pool`, `Session-Anker-Wallets`, `Session-Anker-Save + weitere`). Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Anchor-Template + Toolkit-Restdrift): `internal/qa/plans/issue-pack-durchlauf-88-anchor-template-toolkit-restdrift.md`
- Log (Anchor-Template + Toolkit-Restdrift): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-88-anchor-template-toolkit-restdrift.md`

- **Durchlauf 89 (2026-03-08):** Anschlusslauf zur Guard-Härtung der erzählerischen Kontinuitäts-Pflichten abgeschlossen: Neue QA-Fixture `internal/qa/fixtures/continuity_output_contract_multi_load.json` deckt den Multi-Load-Output-Contract (Kontinuitätsrückblick mit 4 Pflichtblöcken, Split-Beat, Rejoin-HQ-Beat, Echo-Fortwirkung ≤ 2 Sitzungsblöcke) ab; neuer Guard `tools/test_continuity_output_contract.js` validiert diese Pflichten maschinenlesbar und ist im Pflicht-Smoke (`scripts/smoke.sh`) integriert. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Continuity-Output-Contract Guard): `internal/qa/plans/issue-pack-durchlauf-89-continuity-output-contract-guard.md`
- Log (Continuity-Output-Contract Guard): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-89-continuity-output-contract-guard.md`


- **Durchlauf 90 (2026-03-08):** Anschlusslauf zur Contract-Konsolidierung im Cross-Mode-Konfliktpfad abgeschlossen: `systems/gameflow/speicher-fortsetzung.md` nutzt im `merge_conflicts[]`-Minimalbeispiel jetzt den Runtime-konformen Payload (`field`, `source`, `target`, `mode`) statt eines veralteten `anchor_value|guest_value|resolution`-Schemas. Damit bleibt die Trennung zu `logs.flags.continuity_conflicts[]` eindeutig und Follow-up-QA kann deterministisch gegen denselben Datenvertrag prüfen. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Merge-Conflict-Contract Alignment): `internal/qa/plans/issue-pack-durchlauf-90-merge-conflict-contract-alignment.md`
- Log (Merge-Conflict-Contract Alignment): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-90-merge-conflict-contract-alignment.md`

- **Durchlauf 91 (2026-03-08):** Anschlusslauf zur Runtime-Terminologie-Drift nach dem Kontinuitäts-Redesign abgeschlossen: `runtime.js` nutzt jetzt Session-Anker-Wording in Merge-Notizen (`Session-Anker-Vorrang`, `HQ-Pool (economy.cu): Session-Anker-Vorrang`) und protokolliert UI-Overrides als `ui_session_anchor_override`; außerdem wurde der Economy-Audit-Bandgrund auf `session_anchor_level` harmonisiert. `core/sl-referenz.md` und `tools/test_economy_merge.js` wurden entsprechend nachgezogen. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Runtime-Trace Anchor-Terminologie): `internal/qa/plans/issue-pack-durchlauf-91-runtime-trace-anchor-terminology.md`
- Log (Runtime-Trace Anchor-Terminologie): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-91-runtime-trace-anchor-terminology.md`

- **Durchlauf 92 (2026-03-08):** Anschlusslauf zur Restdrift in Runtime-Konfliktnotizen abgeschlossen: `runtime.js` nutzt in Wallet-/Campaign-/Rift-Merge-Notizen nun durchgehend Session-Anker-Wording (`Session-Anker-Werte bevorzugt`, `Session-Anker-Kampagnenzähler/-modus behalten`, `Session-Anker-Seeds priorisiert`); `tools/test_economy_merge.js` wurde beim Wallet-Label auf `Session-Anker` harmonisiert. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Runtime-Note-Wording Cleanup): `internal/qa/plans/issue-pack-durchlauf-92-runtime-note-wording-cleanup.md`
- Log (Runtime-Note-Wording Cleanup): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-92-runtime-note-wording-cleanup.md`


- **Durchlauf 93 (2026-03-08):** Abschluss-/Aufräumlauf für den Kontinuitäts-Strang: neue Statusmatrix `internal/qa/process/continuity-redesign-statusmatrix.md` bündelt Upload-Issues 1–8 (Status + Primärevidenz + Watchpoints) für schnelle Anschlussfähigkeit; zusätzlich wurden operative Playtest-Prompts in `internal/qa/playtest-2026-02-22.sh`, `internal/qa/playtest-2026-02-22-round2.sh` und `internal/qa/playtest-2026-02-22-deep.sh` auf Session-Anker-Wording harmonisiert. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Continuity Closure + QA-Aufräumen): `internal/qa/plans/issue-pack-durchlauf-93-continuity-closure-matrix-cleanup.md`
- Log (Continuity Closure + QA-Aufräumen): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-93-continuity-closure-matrix-cleanup.md`

- **Durchlauf 94 (2026-03-09):** NPC/MMO-Anschlusslauf abgeschlossen: `systems/toolkit-gpt-spielleiter.md` ersetzt den Altblock „Solo-Modus mit temporärem NPC-Team“ durch persistente NPC-Chrononauten (Scope/Status, Join/Leave-Regeln, Offscreen-Fortschreibung) und entfernt den Progress-Reset-Pseudopfad zugunsten von `StartGroupContinuity(...)` ohne Px-/Seed-Reset. `meta/masterprompt_v6.md` und `systems/gameflow/speicher-fortsetzung.md` wurden auf denselben v7-Vertrag erweitert (`continuity.npc_roster[]`, `active_npc_ids[]`, Mensch-vor-NPC-Slotregel, 5-Block-Kontinuitätsrückblick inkl. NPC-Lagebild). `systems/gameflow/cinematic-start.md` harmonisiert Solo-Begleiter-Wording auf Physicality-konforme Begriffe (Linsen-Lichtbild/Comlink statt Hologramm). `internal/qa/process/continuity-redesign-statusmatrix.md` dokumentiert den NPC/MMO-Follow-up-Block und neue Watchpoints. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (NPC-Kontinuität & MMO-Immersion-Hardening): `internal/qa/plans/issue-pack-durchlauf-94-npc-continuity-mmo-hardening.md`
- Log (NPC-Kontinuität & MMO-Immersion-Hardening): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-94-npc-continuity-mmo-hardening.md`

- **Durchlauf 95 (2026-03-09):** Anschlusslauf zur Hologramm-/Physicality-Nuancierung abgeschlossen: `systems/toolkit-gpt-spielleiter.md` erlaubt feste Inworld-Projektionen im HQ (Wand/Tisch/Briefing-Glas) bei expliziter Gerätebenennung, hält aber den Guard gegen losgelöste VR-Räume und Handgelenk-Projektor-Defaults aufrecht. `core/sl-referenz.md` harmonisiert das Hardwareprinzip entsprechend; `systems/gameflow/cinematic-start.md` nutzt wieder technoir-kompatibles Wording (`Lichtbilder/HUD-Hologramme`, `Hologramm-Projektionen`) ohne den Linse/Comlink-Kern zu verlieren. Pflicht-Smoke erneut grün.

- Fahrplan (Hologramm/Physicality-Harmonisierung): `internal/qa/plans/issue-pack-durchlauf-95-hologramm-physicality-harmonisierung.md`
- Log (Hologramm/Physicality-Harmonisierung): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-95-hologramm-physicality-harmonisierung.md`

- **Durchlauf 96 (2026-03-09):** Restdrift-Fix im Startmodul abgeschlossen: `systems/gameflow/cinematic-start.md` trennt verbliebene Hybrid-Begriffe jetzt klar in linsegebundenes HUD-Wording („Linsen-Lichtbilder im HUD“) und HQ-gebundene Inworld-Flächen („Lichtbilder auf den HQ-Briefingflächen“). Damit bleibt die in Durchlauf 95 etablierte Physicality-Nuance stabil, ohne neue Default-Implikationen für Hologramm-HUDs zu öffnen. Pflicht-Smoke erneut grün.

- Fahrplan (Cinematic-Physicality-Restdrift): `internal/qa/plans/issue-pack-durchlauf-96-cinematic-physicality-restdrift.md`
- Log (Cinematic-Physicality-Restdrift): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-96-cinematic-physicality-restdrift.md`

- **Durchlauf 97 (2026-03-09):** Restdrift im Kampagnenstruktur-Modul abgeschlossen: `gameplay/kampagnenstruktur.md` spiegelt den Solo-Start wieder auf `npc-team 0-4` (Drohne nur Fallback ohne Feld-NPC) und hebt den NPC-Squad-Kodex von „temporären Verbündeten“ auf wiederkehrende Kontinuitätsakteure mit HQ-/Offscreen-Fortbestand. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (NPC-Squad-Persistenzabgleich): `internal/qa/plans/issue-pack-durchlauf-97-npc-squad-persistence-alignment.md`
- Log (NPC-Squad-Persistenzabgleich): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-97-npc-squad-persistence-alignment.md`

- **Durchlauf 98 (2026-03-09):** SSOT-Anschlusslauf zur technischen SL-Referenz abgeschlossen: `core/sl-referenz.md` führt im Save-v7-Block jetzt explizit den `continuity`-Abschnitt mit `npc_roster[]`/`active_npc_ids[]`, ergänzt Kontinuitäts-Budgets sowie NPC-Scope/Status-Enums und verankert die Mensch-vor-NPC-Slotregel inkl. NPC-Lagebild-Pflicht im Mehrfach-Load-Rückblick. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (SL-Referenz NPC-Schema-Alignment): `internal/qa/plans/issue-pack-durchlauf-98-sl-referenz-npc-schema-alignment.md`
- Log (SL-Referenz NPC-Schema-Alignment): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-98-sl-referenz-npc-schema-alignment.md`


- **Durchlauf 99 (2026-03-09):** Anschlusslauf zur Verhaltensschicht des NPC-Kontinuitätsmodells abgeschlossen: `meta/masterprompt_v6.md` enthält jetzt explizit die Join/Leave-Guard-Regel (`personal` folgt `owner_id`, `session` bleibt beim Session-Anker, `iti` Hintergrundstatus; Scope-Wechsel nur als sichtbarer Transfer-Beat) plus Cross-Pollination-Hinweis für kompakte Offscreen-Rückkehr. `systems/gameflow/speicher-fortsetzung.md` ergänzt den Pflichtbeat `NPC-Cross-Pollination` (max. 1 Hook), `core/sl-referenz.md` zieht denselben Guard im Save-v7-Hinweisblock nach. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (NPC-Kontinuität Cross-Pollination-Guard): `internal/qa/plans/issue-pack-durchlauf-99-npc-continuity-cross-pollination-guard.md`
- Log (NPC-Kontinuität Cross-Pollination-Guard): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-99-npc-continuity-cross-pollination-guard.md`

- **Durchlauf 100 (2026-03-09):** SSOT-Feinschliff im Masterprompt abgeschlossen: `meta/masterprompt_v6.md` ergänzt jetzt explizit den `NPC-Departure/Recognition-Guard` (Abgang nie stumm, Wiederauftauchen mit konkretem Wiedererkennungsanker). Damit sind die NPC-Pflichtbeats zwischen Masterprompt, Speichermodul, Toolkit und SL-Referenz vollständig synchron. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Masterprompt NPC-Beat-Guard): `internal/qa/plans/issue-pack-durchlauf-100-masterprompt-npc-beat-guard.md`
- Log (Masterprompt NPC-Beat-Guard): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-100-masterprompt-npc-beat-guard.md`

- **Durchlauf 101 (2026-03-09):** Toolkit-Restdrift zur Physicality-Formulierung abgeschlossen: `systems/toolkit-gpt-spielleiter.md` präzisiert im HUD-Stilabschnitt den linsengebundenen Default (Retina-Linse im Sichtfeld) und erlaubt freie Projektionen nur noch als explizit benannte Inworld-Fläche/Geräteschnittstelle (z. B. HQ-Briefingglas). Damit bleibt der in 94–100 etablierte Guard auch in den KI-Erzählhinweisen stabil. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Toolkit Physicality-Wording-Guard): `internal/qa/plans/issue-pack-durchlauf-101-toolkit-physicality-wording-guard.md`
- Log (Toolkit Physicality-Wording-Guard): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-101-toolkit-physicality-wording-guard.md`


- **Durchlauf 102 (2026-03-09):** Core-Restdrift zur Physicality-Terminologie abgeschlossen: `core/zeitriss-core.md` ersetzt verbliebene Altbegriffe (`holografische Anzeigen`, `Hologramm-Module`, `Holosuites`) in HQ-/Trainingspassagen durch Physicality-konsistente Formulierungen (`Lichtbild-Anzeigen auf den Briefingflächen`, `Simulationsräume`, `Simulationsmodule mit fest verbauten Lichtbildflächen`). Damit bleibt der in den Durchläufen 94–101 etablierte Guard auch im Lore-Core stabil. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Core Physicality-Terminologieabgleich): `internal/qa/plans/issue-pack-durchlauf-102-core-physicality-terminology-alignment.md`
- Log (Core Physicality-Terminologieabgleich): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-102-core-physicality-terminology-alignment.md`

- **Durchlauf 103 (2026-03-09):** Präzisierungslauf nach Feedback: `core/zeitriss-core.md` wurde semantisch auf den etablierten Physicality-Kanon zurückgeführt. Hologramm-/Lichtbild-Begriffe bleiben zulässig, sofern an sichtbare Inworld-Infrastruktur gebunden (Holosuite/Briefingglas/Tischprojektor); ausgeschlossen bleibt nur das mobile Handgelenk-HUD als Default. Damit ist die Trennung aus 94–101 (`Retina-HUD` vs. verankerte Projektion) auch im Core wieder eindeutig. Pflicht-Smoke erneut grün.

- Fahrplan (Core Physicality-Klarstellung): `internal/qa/plans/issue-pack-durchlauf-103-core-physicality-clarification.md`
- Log (Core Physicality-Klarstellung): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-103-core-physicality-clarification.md`

- **Durchlauf 104 (2026-03-09):** Guard-Automation für den NPC-Kontinuitätsstrang abgeschlossen: `tools/test_npc_continuity_consistency.js` prüft jetzt als Pflicht-Smoke die SSOT-Anker in `meta/masterprompt_v6.md`, `systems/gameflow/speicher-fortsetzung.md` und `core/sl-referenz.md` (inkl. `continuity.npc_roster[]`, `active_npc_ids[]`, Scope-Guard `personal|session|iti`, Mensch-vor-NPC-Slotregel) und validiert das neue Fixture `internal/qa/fixtures/npc_continuity_output_contract.json` (Budgets/Status/Leave/Cross-Pollination). `scripts/smoke.sh` enthält den Check fest; Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (NPC-Continuity-Guard-Automation): `internal/qa/plans/issue-pack-durchlauf-104-npc-continuity-guard-automation.md`
- Log (NPC-Continuity-Guard-Automation): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-104-npc-continuity-guard-automation.md`

- **Durchlauf 105 (2026-03-09):** Spielerpfad-Klarstellung im NPC/MMO-Strang abgeschlossen: `core/spieler-handbuch.md` ergänzt im Mini-Einsatzhandbuch eine explizite Notiz zur NPC-Kontinuität (`npc-team` als persistenter Pfad, Menschen-vor-NPC-Slotregel, HQ/Funk/Offscreen-Fortbestand, kompakte Offscreen-Fortschreibung). Damit ist der bereits in 94–104 verankerte SSOT-Kern auch im spieler-sichtigen Startpfad direkt sichtbar. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Spielerhandbuch NPC-Kontinuitätsklarstellung): `internal/qa/plans/issue-pack-durchlauf-105-spielerhandbuch-npc-kontinuitaet-clarification.md`
- Log (Spielerhandbuch NPC-Kontinuitätsklarstellung): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-105-spielerhandbuch-npc-kontinuitaet-clarification.md`

- **Durchlauf 106 (2026-03-09):** Finaler Restdrift-Fix im Startmodul abgeschlossen: `systems/gameflow/cinematic-start.md` ersetzt verbleibende Hologramm-Defaults im HQ-Einstieg und in den Cine-Tipps durch Physicality-konforme Formulierungen (`linsengebundene HUD-Lichtbilder` im Sichtfeld, sichtbare Briefingflächen/Lichtbild-Anzeigen für Inworld-Projektionen). Damit bleibt die Trennung Linse-HUD vs. verankerte HQ-Projektionen in allen Starttexten stabil. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Cinematic-Start Physicality Final Pass): `internal/qa/plans/issue-pack-durchlauf-106-cinematic-physicality-wording-final-pass.md`
- Log (Cinematic-Start Physicality Final Pass): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-106-cinematic-physicality-wording-final-pass.md`

- **Durchlauf 107 (2026-03-09):** Physicality-Guard-Automation abgeschlossen: `tools/test_physicality_watchguard.js` prüft jetzt in `systems/toolkit-gpt-spielleiter.md`, `systems/gameflow/cinematic-start.md` und `core/zeitriss-core.md` die Pflichtanker der Linse/HUD-vs.-Inworld-Projektions-Trennung und blockt bekannte Driftmuster (`Hologramm-Begleiter`, alte freischwebende Display-Defaults). `scripts/smoke.sh` enthält den Check fest mit Erfolgstoken `physicality-watchguard-ok`. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Physicality-Watchguard-Automation): `internal/qa/plans/issue-pack-durchlauf-107-physicality-watchguard-automation.md`
- Log (Physicality-Watchguard-Automation): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-107-physicality-watchguard-automation.md`

- **Durchlauf 108 (2026-03-09):** Upload-Paket `ZEITRISS_never_happened_gadget_pack.md` integriert: `core/spieler-handbuch.md`, `core/sl-referenz.md`, `systems/toolkit-gpt-spielleiter.md`, `meta/masterprompt_v6.md` und `characters/ausruestung-cyberware.md` verankern nun konsistent den Kausalabfang-Marker ("Never happened") als strikt begrenztes ITI-Cleanup-Protokoll **nach 0 LP**. Reihenfolge und Guard sind harmonisiert (`Loot sichern → optional Kausalabfang → Cleanup/Exfil`), inklusive Sperren für Boss-/Mini-Boss-Ziele, Chrononauten/Squadmates, Zivilisten, Para-Wesen, Arena/PvP und Chronopolis. Prozessdoku + QA-Artefakte für Lauf 108 ergänzt. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang-Integration): `internal/qa/plans/issue-pack-durchlauf-108-never-happened-kausalabfang-integration.md`
- Log (Kausalabfang-Integration): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-108-never-happened-kausalabfang-integration.md`


- **Durchlauf 109 (2026-03-09):** Kausalabfang-Guard-Automation abgeschlossen: `tools/test_kausalabfang_watchguard.js` prüft als Pflicht-Smoke über `core/spieler-handbuch.md`, `core/sl-referenz.md`, `systems/toolkit-gpt-spielleiter.md`, `meta/masterprompt_v6.md` und `characters/ausruestung-cyberware.md` die 0-LP-Grenze, die Reihenfolge `Loot sichern → optional(er) Kausalabfang → Cleanup/Exfil` sowie die Verbotsmatrix (Chrononauten, Boss/Mini-Boss, Zivilisten, Para-Wesen, Arena/PvP, Chronopolis). `scripts/smoke.sh` enthält den Check fest mit Erfolgstoken `kausalabfang-watchguard-ok`. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang-Watchguard-Automation): `internal/qa/plans/issue-pack-durchlauf-109-kausalabfang-watchguard-automation.md`
- Log (Kausalabfang-Watchguard-Automation): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-109-kausalabfang-watchguard-automation.md`

- **Durchlauf 110 (2026-03-09):** Anschluss-Hardening zum Kausalabfang abgeschlossen: `systems/toolkit-gpt-spielleiter.md` und `meta/masterprompt_v6.md` enthalten jetzt zusätzlich den **Named-Target-Echo** (maximal ein späterer Nachhall bei benannten Zielen) sowie den trockenen **Kodex-Satzbau** für Vollzug/Blockfälle (`Identitätslock bestätigt`, `Kausalabfang freigegeben`, `ITI-Abfangfenster`, Uplink-/Zulässigkeitsblock). `tools/test_kausalabfang_watchguard.js` wurde um diese Anker erweitert, damit nicht nur 0-LP-Gate/Reihenfolge/Sperren, sondern auch Echo-/Kommunikationskonsistenz im Pflicht-Smoke stabil bleibt. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang Echo-/Kodex-Hardening): `internal/qa/plans/issue-pack-durchlauf-110-kausalabfang-echo-kodex-hardening.md`
- Log (Kausalabfang Echo-/Kodex-Hardening): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-110-kausalabfang-echo-kodex-hardening.md`


- **Durchlauf 111 (2026-03-09):** Kausalabfang-Guard um Infra-Hardening erweitert: `tools/test_kausalabfang_watchguard.js` prüft jetzt zusätzlich über alle Kernmodule die Anker **kein Kampfwerkzeug**, **Nahdistanz/Nahbereich**, **Identitätsfassung/Identitätslock** und **Kodex-Uplink/Uplink**. Zusätzlich sichern dateispezifische Checks in `core/sl-referenz.md` und `characters/ausruestung-cyberware.md`, dass der Marker **nicht shopbar/kein Kaufgegenstand** und **kein Pflicht-Inventarstück** bleibt. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang Watchguard Hardening / Infra): `internal/qa/plans/issue-pack-durchlauf-111-kausalabfang-watchguard-hardening-infra.md`
- Log (Kausalabfang Watchguard Hardening / Infra): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-111-kausalabfang-watchguard-hardening-infra.md`


- **Durchlauf 112 (2026-03-09):** Kausalabfang-Abfangfenster als zusätzlicher SSOT-Guard verankert: `core/spieler-handbuch.md`, `systems/toolkit-gpt-spielleiter.md` und `meta/masterprompt_v6.md` führen jetzt explizit das enge ITI-Zeitfenster (**Sekunden bis wenige Minuten** vor Einsatzkontakt). `tools/test_kausalabfang_watchguard.js` prüft diesen Anker im Pflicht-Smoke mit, damit die Regel nicht in ein weites Retcon-Fenster driftet. Pflicht-Smoke + Linklint erneut grün.
- **Durchlauf 113 (2026-03-09):** Kodex-Archivanker für Kausalabfang gehärtet: `systems/toolkit-gpt-spielleiter.md` und `meta/masterprompt_v6.md` führen nun parallel den trockenen Drift-Satz `Kodex: Lokale Erinnerung driftet. Archivanker aktiv.`; `tools/test_kausalabfang_watchguard.js` prüft ihn als Pflichtanker in den strikten Checks. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang Abfangfenster-Hardening): `internal/qa/plans/issue-pack-durchlauf-112-kausalabfang-abfangfenster-hardening.md`
- Log (Kausalabfang Abfangfenster-Hardening): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-112-kausalabfang-abfangfenster-hardening.md`

- **Durchlauf 114 (2026-03-09):** Kausalabfang-Watchguard um verbleibende Ablauf-/Sperrenanker ergänzt: `tools/test_kausalabfang_watchguard.js` prüft jetzt `Squadmates` als expliziten Pflichtanker über alle Kernmodule und erzwingt in den strikten Dateien (`systems/toolkit-gpt-spielleiter.md`, `meta/masterprompt_v6.md`) zusätzlich die KI-Regel **unbenannte Hostiles automatisch, benannte Ziele nachfragen**. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang Squadmates/Auto-Nachfrage-Watchguard): `internal/qa/plans/issue-pack-durchlauf-114-kausalabfang-squadmates-auto-nachfrage-watchguard.md`
- Log (Kausalabfang Squadmates/Auto-Nachfrage-Watchguard): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-114-kausalabfang-squadmates-auto-nachfrage-watchguard.md`

- **Durchlauf 115 (2026-03-09):** Kausalabfang um den verbleibenden TEMP-Flavor-Anker gehärtet: `systems/toolkit-gpt-spielleiter.md` und `meta/masterprompt_v6.md` führen nun parallel den knappen **TEMP-Recall-Blur** (TEMP 1–2 kurzer Blur, 3–5 Déjà-vu, 6+ fast stabil) ausdrücklich ohne Zusatzwürfe/Strafmechanik. `tools/test_kausalabfang_watchguard.js` prüft diese Staffelung als strikten Hardening-Regex in Toolkit + Masterprompt mit. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang TEMP-Recall-Blur-Hardening): `internal/qa/plans/issue-pack-durchlauf-115-kausalabfang-temp-recall-blur-hardening.md`
- Log (Kausalabfang TEMP-Recall-Blur-Hardening): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-115-kausalabfang-temp-recall-blur-hardening.md`

- **Durchlauf 116 (2026-03-09):** Kausalabfang-Named-Target-Echo um den fehlenden `roster_echoes`-Anker ergänzt: `systems/toolkit-gpt-spielleiter.md` und `meta/masterprompt_v6.md` schreiben den Nachhall benannter Ziele jetzt konsistent in `logs.trace[]`/`logs.notes[]` oder `continuity.roster_echoes[]` / `continuity.shared_echoes[]`. `tools/test_kausalabfang_watchguard.js` erzwingt diesen Storage-Anker per zusätzlichem Strict-Regex in Toolkit + Masterprompt. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang Roster-Echo-Anker-Hardening): `internal/qa/plans/issue-pack-durchlauf-116-kausalabfang-roster-echo-anchor-hardening.md`
- Log (Kausalabfang Roster-Echo-Anker-Hardening): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-116-kausalabfang-roster-echo-anchor-hardening.md`

- **Durchlauf 117 (2026-03-09):** Kausalabfang-Anti-Retcon-Wording explizit gehärtet: `core/spieler-handbuch.md`, `core/sl-referenz.md`, `systems/toolkit-gpt-spielleiter.md`, `meta/masterprompt_v6.md` und `characters/ausruestung-cyberware.md` führen jetzt konsistent den Anker **kein universelles Retcon-Werkzeug**. `tools/test_kausalabfang_watchguard.js` prüft dies als positiven Pflichtregex über alle Kernmodule (statt reinem Negativcheck). Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang Anti-Retcon-Wording-Hardening): `internal/qa/plans/issue-pack-durchlauf-117-kausalabfang-anti-retcon-wording-hardening.md`
- Log (Kausalabfang Anti-Retcon-Wording-Hardening): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-117-kausalabfang-anti-retcon-wording-hardening.md`

- **Durchlauf 118 (2026-03-09):** Kausalabfang-Motiv-/Lagefenster explizit gehärtet: `core/spieler-handbuch.md`, `core/sl-referenz.md`, `systems/toolkit-gpt-spielleiter.md`, `meta/masterprompt_v6.md` und `characters/ausruestung-cyberware.md` verankern nun parallel, dass Abfang nur gilt, solange **Tatmotivation und Einsatzlage** des Ziels erkennbar gleich bleiben. `tools/test_kausalabfang_watchguard.js` prüft den neuen Doppelanker (`Tatmotivation` + `Einsatzlage`) als Pflichtregex über alle Kernmodule. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang Motiv-/Lagefenster-Hardening): `internal/qa/plans/issue-pack-durchlauf-118-kausalabfang-motivlage-window-hardening.md`
- Log (Kausalabfang Motiv-/Lagefenster-Hardening): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-118-kausalabfang-motivlage-window-hardening.md`

- **Durchlauf 119 (2026-03-09):** Prozess-Housekeeping vor dem nächsten Deepsearch-Lauf abgeschlossen: `internal/qa/process/continuity-redesign-statusmatrix.md` wurde um eine explizite **Anschluss-Checkliste vor dem nächsten Deepsearch-Lauf** ergänzt (Pflicht-Smoke, optionaler Linklint für Prozessdateien, SSOT-Parallellauf und Synchronpflicht für Plan/Log/known-issues/Statusmatrix). Zusätzlich wurde die Watchpoint-Liste im Follow-up-Bereich auf fortlaufende Nummerierung ohne Leerlaufblöcke bereinigt, damit Anschlussläufe reproduzierbar bleiben.

- Fahrplan (Housekeeping vor Deepsearch): `internal/qa/plans/issue-pack-durchlauf-119-housekeeping-vor-deepsearch.md`
- Log (Housekeeping vor Deepsearch): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-119-housekeeping-vor-deepsearch.md`


- **Durchlauf 120 (2026-03-09):** Kausalabfang-Leitmotiv **Festnahme statt Löschung** als expliziten Positivanker SSOT-weit gehärtet: `core/spieler-handbuch.md`, `core/sl-referenz.md`, `systems/toolkit-gpt-spielleiter.md`, `meta/masterprompt_v6.md` und `characters/ausruestung-cyberware.md` enthalten nun parallel diese Leitformulierung. `tools/test_kausalabfang_watchguard.js` prüft den Anker als zusätzlichen Pflichtregex über alle Kernmodule. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang Festnahme-statt-Löschung Hardening): `internal/qa/plans/issue-pack-durchlauf-120-kausalabfang-festnahme-statt-loeschung-hardening.md`
- Log (Kausalabfang Festnahme-statt-Löschung Hardening): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-120-kausalabfang-festnahme-statt-loeschung-hardening.md`


- **Durchlauf 121 (2026-03-09):** Kodex-Blocksatz beim Kausalabfang vollständig harmonisiert: `meta/masterprompt_v6.md` nutzt nun parallel zum Toolkit die volle Sperr-Meldung `Kodex: Ziel nicht zulässig. Boss-/ITI-/Zivilstatus blockiert.`. `tools/test_kausalabfang_watchguard.js` wurde in den strikten Checks um zusätzliche Kodex-Pflichtregex erweitert (`ITI-Abfangfenster steht`, `Ziel nicht zulässig ...`, `Uplink fehlt ... Marker bleibt ohne Vollzug`), damit dieser Satzbau nicht mehr still driften kann. Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Kausalabfang Kodex-Blocksatz Watchguard-Hardening): `internal/qa/plans/issue-pack-durchlauf-121-kausalabfang-kodex-blocksatz-watchguard-hardening.md`
- Log (Kausalabfang Kodex-Blocksatz Watchguard-Hardening): `internal/qa/logs/2026-03-09-issue-pack-durchlauf-121-kausalabfang-kodex-blocksatz-watchguard-hardening.md`


- **Durchlauf 151 (2026-03-10):** Hard-Final-Review-Anschluss zur Runtime-Rest-Entdevifizierung abgeschlossen: `systems/gameflow/speicher-fortsetzung.md`, `systems/toolkit-gpt-spielleiter.md` und `gameplay/kampagnenstruktur.md` wurden an verbleibenden QA-/Testrun-Formulierungen neutralisiert, ohne Regelkern zu verändern (u. a. UI-/Cross-Mode-Überschriften, Load-Hinweise, HUD-/SUG-Hinweistext, Seed-Lock-Label). Pflicht-Smoke erneut grün.

- Fahrplan (Hard Final Review Runtime-Rest-Entdevifizierung): `internal/qa/plans/issue-pack-durchlauf-151-hard-final-review-runtime-rest-entdevifizierung.md`
- Log (Hard Final Review Runtime-Rest-Entdevifizierung): `internal/qa/logs/2026-03-10-issue-pack-durchlauf-151-hard-final-review-runtime-rest-entdevifizierung.md`

- **Durchlauf 152 (2026-03-10):** Hard-Final-Review-Anschluss zur Split-/Merge-Klarstellung abgeschlossen: `systems/gameflow/speicher-fortsetzung.md` beseitigt den letzten semantischen Restdrift zwischen Überschrift und Kanontext. Der Abschnitt heißt nun `Branch-Importe ohne Split-Protokoll`; gleichzeitig bleibt explizit festgehalten, dass Core-Parallelpfade mit identischer `continuity.split.family_id` kanonisch sind und nur gemischte Pfade ohne Split-Protokoll als Branch-Import laufen. Pflicht-Smoke erneut grün.

- Fahrplan (Hard Final Review Split-/Branch-Import-Klarstellung): `internal/qa/plans/issue-pack-durchlauf-152-hard-final-review-split-branch-import-klarstellung.md`
- Log (Hard Final Review Split-/Branch-Import-Klarstellung): `internal/qa/logs/2026-03-10-issue-pack-durchlauf-152-hard-final-review-split-branch-import-klarstellung.md`

- **Durchlauf 153 (2026-03-10):** Hard-Final-Review-Anschluss als Pipeline-Guard abgesichert: `tools/test_default_slot_dependency_watchguard.js` prüft nun verpflichtend, dass `characters/charaktererschaffung-grundlagen.md` keine implizite Runtime-Abhängigkeit auf das optionale Modul `charaktererschaffung-optionen.md` enthält. Der Check ist in `scripts/smoke.sh` integriert und läuft im Pflicht-Smoke mit. Pflicht-Smoke erneut grün.

- Fahrplan (Hard Final Review Default-Slot-Watchguard & Statusaudit): `internal/qa/plans/issue-pack-durchlauf-153-hard-final-review-default-slot-watchguard-und-statusaudit.md`
- Log (Hard Final Review Default-Slot-Watchguard & Statusaudit): `internal/qa/logs/2026-03-10-issue-pack-durchlauf-153-hard-final-review-default-slot-watchguard-und-statusaudit.md`

- **Durchlauf 154 (2026-03-10):** Hard-Final-Review-Regressionspaket als Pflicht-Watchguard ergänzt: `tools/test_hard_final_review_watchguard.js` sichert jetzt gemeinsam Split-/Merge-Kanon (Core-Parallelpfade + separate Rift-Ops, Pflichtanker `continuity.split.family_id`, ohne Legacy-Rift-only-Satz), Einstiegskanon-Altspur in `cinematic-start.md` sowie HQ-Kernbereichs-Wording in `kampagnenstruktur.md`. Der Guard ist in `scripts/smoke.sh` integriert und liefert `hard-final-review-watchguard-ok`. Pflicht-Smoke erneut grün.

- Fahrplan (Hard Final Review Regression-Watchguard-Pack): `internal/qa/plans/issue-pack-durchlauf-154-hard-final-review-regression-watchguard-pack.md`
- Log (Hard Final Review Regression-Watchguard-Pack): `internal/qa/logs/2026-03-10-issue-pack-durchlauf-154-hard-final-review-regression-watchguard-pack.md`

- **Durchlauf 155 (2026-03-10):** Prozess-Housekeeping für bessere Anschlussfähigkeit ergänzt: neue kompakte Übersicht `internal/qa/process/hard-final-review-next-steps.md` als Arbeitsfahrplan nach Abschluss der Hard-Final-Review-Runde; zusätzlich wurde `uploads/hard-final-review.md` als historischer Snapshot gekennzeichnet und auf den aktuellen Prozessstand (`known-issues.md` + neue Anschlussübersicht) verwiesen. Pflicht-Smoke erneut grün.

- Fahrplan (Hard Final Review Übersicht & Anschlusspfad): `internal/qa/plans/issue-pack-durchlauf-155-hard-final-review-uebersicht-und-anschlusspfad.md`
- Log (Hard Final Review Übersicht & Anschlusspfad): `internal/qa/logs/2026-03-10-issue-pack-durchlauf-155-hard-final-review-uebersicht-und-anschlusspfad.md`

- **Durchlauf 156 (2026-03-10):** Der offene Manual-Rest aus der Anschlussübersicht ist automatisiert: `tools/test_chronopolis_gate_watchguard.js` prüft jetzt Lvl10-Key-Grant/HQ-Hook, `fr_contact` HQ-only, Rift-Launch-Gate (`HQ` + `episode_completed`), den Epoch-Fallback (`chrono.epoch` → `campaign.epoch`) sowie den CITY-vs-HQ-Anker. `scripts/smoke.sh` führt den Guard verpflichtend aus (`chronopolis-gate-watchguard-ok`) und der manuelle Chronopolis-Gate-Block wurde entfernt. Pflicht-Smoke erneut grün.

- Fahrplan (Hard Final Review Chronopolis-Gate-Watchguard-Automation): `internal/qa/plans/issue-pack-durchlauf-156-hard-final-review-chronopolis-gate-watchguard-automation.md`
- Log (Hard Final Review Chronopolis-Gate-Watchguard-Automation): `internal/qa/logs/2026-03-10-issue-pack-durchlauf-156-hard-final-review-chronopolis-gate-watchguard-automation.md`

