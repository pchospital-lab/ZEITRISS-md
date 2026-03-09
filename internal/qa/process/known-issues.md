---
title: "Known Issues & Triage-Prozess"
version: 1.0.0
tags: [meta, qa]
---

# Known Issues & Triage-Prozess

Diese Seite bündelt den Prozess für offene QA-Funde, die nicht direkt im
Runtime-Content gelöst werden (z. B. Tooling-, Workflow- oder Plattformfragen).

## Ziel

- Einheitlicher Ort für Triagestatus (`neu`, `geprüft`, `geplant`,
  `in Umsetzung`, `abgeschlossen`, `verworfen`).
- Klare Verlinkung zwischen Eingangsquelle, Fahrplan, Log und Umsetzung.
- Saubere Trennung zwischen Runtime-Änderungen und Meta-Prozessarbeit.

## Prozess (leichtgewichtig)

1. **Erfassen**
   - Issue im QA-Log benennen und mit Quelle verlinken (Upload, Playtest,
     Audit, Maintainer-Report).
2. **Triagieren**
   - Priorität (`P0`–`P3`), Scope (Runtime/Meta/Tooling) und Besitzer:in
     festlegen.
3. **Planen**
   - Falls umsetzungsrelevant: Ticket in den Fahrplan (`internal/qa/plans/`)
     aufnehmen.
4. **Umsetzen**
   - Änderungen im Repo durchführen, Pflichtprüfungen laufen lassen,
     Commit/PR mit Referenz auf den QA-Eintrag versehen.
5. **Abschließen**
   - Status in dieser Liste, im QA-Log und im Fahrplan synchron auf
     `abgeschlossen` oder `verworfen` setzen.

## Aktuelle Known Issues

| ID | Titel | Quelle | Priorität | Scope | Status | Notiz |
| --- | --- | --- | --- | --- | --- | --- |
| ZR-015 | Interne QA-Known-Issues in GitHub-Issue-Triage spiegeln | `uploads/deep-research-report(4).md` | P3 | Meta/Prozess | abgeschlossen | Diese Prozessseite ist der kanonische Startpunkt; operative Arbeit läuft weiterhin über Fahrplan + QA-Log. |
| ZR-016 | Externer Codex-Issue-Pack in iterative Fahrplan-Cluster überführen | `uploads/ZEITRISS_codex_issue_pack.md` | P0 | Runtime/QA | abgeschlossen | Primärindex für den Gesamtstand: `internal/qa/process/issue-pack-statusmatrix.md`. Abschluss dokumentiert bis Durchlauf 38 (`internal/qa/plans/issue-pack-durchlauf-01.md` bis `internal/qa/plans/issue-pack-durchlauf-38.md` plus zugehörige QA-Logs `internal/qa/logs/*issue-pack-durchlauf-*.md`). Folgearbeit wird als neue Known-Issue-ID angelegt. |
| ZR-017 | Save/Load v7 und OpenWebUI-Standardpfad aus dem neuen Issue-Pack nachziehen | `uploads/ZEITRISS_v7_save_load_issue_pack.md` | P0 | Runtime/QA | abgeschlossen | Durchläufe 39-47 umgesetzt (`internal/qa/plans/issue-pack-durchlauf-39.md` bis `internal/qa/plans/issue-pack-durchlauf-47.md` + Logs): Chat-Load-Standard (`!save` + JSON-Paste, `Spiel laden` optional), `!bogen`-Lesesicht, kanonische Split/Merge-Grenze, Mid-Episode-Klarfall 5er→3/2, OpenWebUI-Hopper/Leaver-Betrieb und Arena-Savegrenze (`idle|completed` bei inaktiver Arena) sind dokumentiert; obsolet gewordene Runtime-Komfortbefehle (`load/suspend/resume/autosave hq`) wurden aus dem Spielerpfad entfernt. Leseführung bleibt auf "Kanon pro aktivem Host-Chat" (Merge weiter host-priorisiert). Dedupe/Lineage-Standard wurde in Durchlauf 48 dokumentarisch verankert; Save-Größenbudget inkl. `summaries.*`-Prune-Standard wurde in Durchlauf 49 ergänzt; der Px-Zustandsautomat (`campaign.px_state` + Merge-Priorität `consumed > pending_reset > stable`) wurde in Durchlauf 50 vereinheitlicht; in Durchlauf 51 wurden die Economy-Bänder auf `120/512/900+` harmonisiert und eine v7-Fixture-/Smoke-Strecke für 5er-Highlevel, Split/Merge, Chronopolis, Abort und chat-nativen JSON-Load ergänzt; in Durchlauf 52 wurde das formale Mixed-Split-Präzedenzmodell (Rift/PvP/Chronopolis/Abort) inklusive Allowlist-Importregeln und Fixture-Checks abgeschlossen. Durchlauf 53 führte eine SSOT-Revalidierung nach: konkurrierender Alt-v7-Exportblock in `speicher-fortsetzung.md` auf den kanonischen `zr`/`campaign.mission`/`attr`/`arc.questions+hooks`-Pfad harmonisiert; Legacy-Feldnamen bleiben nur Import-Bridge. Durchlauf 54 ergänzt einen dauerhaften Driftguard (`tools/test_v7_schema_consistency.js`) plus kanonische v7-Schemareferenz (`systems/gameflow/saveGame.v7.schema.json`) im Pflicht-Smoke. Durchlauf 55 schärft die WS-/Repo-Trennung nach: Save-Kanon in WS-Texten explizit ohne Repo-Pfad-Abhängigkeit für KI-SL/OpenWebUI; externe Schemas bleiben reine Tooling-/Runtime-Hilfe. Durchlauf 56 ergänzt eine zentrale Statusmatrix über Upload-Issues 1–10 (`internal/qa/process/v7-save-load-statusmatrix.md`) inklusive Watchpoints für Anschluss-QA und revalidiert den Stand erneut via Pflicht-Smoke. |

| ZR-018 | Ruf/Tier-Progress und Alien/Mystery-Onboarding als SSOT nachziehen | `uploads/ZEITRISS_ruf_alien_review.md` | P0 | Runtime/QA | abgeschlossen | Durchlauf 57 abgeschlossen: Trennung `reputation.iti` vs. `reputation.factions.*`, bossbasierte ITI-Rufprogression (M1/M5/M10/M15/M20), Tier-V-Lizenz als kaufbarer Pfad, Rang-Mapping 0–5, Level-10-vs.-Lizenz-Klarstellung sowie Mystery-Contract/Graue-Deckname in Spieler-Onboarding und Kampagnenübersicht. Durchlauf 58 schließt den Restdrift im Spieler-Handbuch (Debrief-Label `ITI-Ruf`, Tier-V-Cheatsheet `5.000 CU`). Durchlauf 59 härtet Referenz-/Kerntext-Watchpoints (Rufbegriffe in Kampagnenübersicht/SL-Referenz, Mystery-Tonlage im Core-Text ohne harten Alien-Fakt). Durchlauf 60 schließt eine Restdrift im Missionsbeispielpfad (`scheinbar "Alien"-Raptoren` als Feldread in `gameplay/kampagnenstruktur.md`) und hält den Onboarding-Ton damit auch in Episodenbeispielen konsistent. Durchlauf 61 zieht verbleibende Watchpoint-Wordingstellen nach (`characters/ausruestung-cyberware.md`: formaler `ITI-Ruf`/`Lizenz-Tier`-Pfad; `gameplay/kreative-generatoren-begegnungen.md`: `Greys` als `ITI-Deckname`). Durchlauf 62 korrigiert diese Überverengung gemäß Reviewer-Feedback: `Greys` als posthumane Fernzukunfts-Herkunft (jenseits T-/N-Stufe) mit möglichem Bezug zu externen Zeitmanipulator-Fraktionen; Gegnerklarheit in der Kampagnenübersicht entsprechend nachgezogen. Durchlauf 63 schließt verbliebene Debrief-/HQ-Wording-Drift in `gameplay/kampagnenstruktur.md` (`ITI-Ruf-Update` und formaler `reputation.iti`-Pfad) und dokumentiert den Anschlusslauf in QA-Plan/Log. Durchlauf 64 härtet ergänzend die Chronopolis-Wegführung als Schlauchlevel (`Eingangsschleuse -> Ringlauf -> gegenüberliegende Ausgangsschleuse`) in Core/Referenz/Kampagnenmodul sowie die Level-10-Klarstellung ohne Shop-Drift. Durchlauf 65 verstetigt die Watchpoints per leichtem Smoke-Guard (`tools/test_ruf_alien_watchguard.js` in `scripts/smoke.sh`) für Debrief-Disziplin, Tier-V-Rückfallblocker und Onboarding-Ton. Durchlauf 66 schließt verbleibende Gating-Wording-Drift (`ITI-Rufpunkte`, kein `Dienstgrad/Ruf`, Shop-Tiers ohne levelbasierten Freigabe-Header) in den Charakter-/Ausrüstungsmodulen und erweitert den Watchguard um diese Rückfallmuster. Durchlauf 67 schließt Restdrift im Chronopolis-Gating (`ITI-Rang/ITI-Ruf`) in `gameplay/kampagnenuebersicht.md`, präzisiert formales Gating auf `reputation.iti` und erweitert den Watchguard um dieses Rückfallmuster. Durchlauf 68 ergänzt im `core/spieler-handbuch.md` das kanonische ITI-Rang-Mapping (0–5) plus Debrief-Format und erweitert den Watchguard um einen Positiv-Check für dieses Handbuch-Format. Durchlauf 69 ergänzt den Monitoring-Rhythmus für Anschlussläufe und erweitert den Watchguard um zusätzliche Positiv-Checks auf Mystery-Kern (`core/zeitriss-core.md`) und Greys-Generatorpfad (`gameplay/kreative-generatoren-begegnungen.md`). Durchlauf 70 führt den allgemeinen Abschlusscheck durch (Pflicht-Smoke + v7-Guards grün, WS-Linkgrenzen auf WS+Masterprompt gehärtet, fehlerhaften relativen Modul-Link korrigiert) und dokumentiert den Auditpfad in Plan/Log. Durchlauf 71 zieht ein direktes V6→V7-Migrationsbeispiel in den Wissensspeicher nach und verlinkt die SL-Referenz auf diesen internen WS-Anker, damit KI-SL-Legacy-Migration ohne externe Dev-Artefakte möglich bleibt. Durchlauf 72 ergänzt den allgemeinen Abschlusscheck um Format-/Zeilenlängenbefund, bestätigt erneut v7-/Watchguard-Integrität sowie den internen WS-Linkscope ohne Außenverweise. Primärindex: `internal/qa/process/ruf-alien-statusmatrix.md`. |

## Pflegehinweis

Neue Meta-Issues werden zuerst hier erfasst und danach in Fahrplan/Log
verknüpft. Runtime-Issues bleiben primär im Fahrplan, werden aber bei
prozessualem Bedarf mit Referenz in dieser Datei gespiegelt.


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
