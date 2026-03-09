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

| ZR-020 | ITI/MMO-Hauskanon (Ortsatlas, Kernpersonal, Heimkehr-Beat, Ausbau-Drift) als Runtime-SSOT stabilisieren | `uploads/ZEITRISS_ITI_mmo_konsistenz_review.md` | P0 | Runtime/QA | abgeschlossen | Durchlauf 122 harmonisiert den ITI-Atlas (8 Hauptorte), verankert Kernpersonal (Renier/Mira/Liaisons), ersetzt HQ-Ausbau durch Zugangs-/Lizenzlogik und zieht den Pflicht-Heimkehr-Beat parallel in Toolkit, Masterprompt und Kernmodule nach. Durchlauf 123 ergänzt den Kontinuitäts-Feinschliff mit festen ITI-ID-Ankern (`ITI-RENIER`, `ITI-MIRA`, `ITI-LORIAN`, `ITI-VARGAS`, `ITI-NARELLA`) und Echo-Kurzform `ITI-ID :: Status/Hook` in Speichermodul + Toolkit (`internal/qa/plans/issue-pack-durchlauf-123-iti-kernrollen-id-echo-konvention.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-123-iti-kernrollen-id-echo-konvention.md`). Durchlauf 124 entfernt den letzten aktiven `HQ-Ausbau`-Reststring im Runtime-Slot Currency zugunsten von `HQ-Zugangsfreigaben/Lizenzen` (`internal/qa/plans/issue-pack-durchlauf-124-iti-hq-ausbau-restdrift-currency.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-124-iti-hq-ausbau-restdrift-currency.md`). Durchlauf 125 bereinigt zusätzlich den verbleibenden Ausbau-/Stufenrest im Core-Slot (`core/zeitriss-core.md`) auf Freigaben-/Lizenzlogik (`internal/qa/plans/issue-pack-durchlauf-125-iti-hq-ausbau-restdrift-core.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-125-iti-hq-ausbau-restdrift-core.md`). Durchlauf 126 entfernt den verbliebenen Optionalpfad `Direkt weiterspringen (ohne HQ-Stop)` im Core-Loop und verankert den HQ-Beat explizit als verpflichtenden Heimkehrschritt (`internal/qa/plans/issue-pack-durchlauf-126-iti-hq-pflichtbeat-restdrift-core.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-126-iti-hq-pflichtbeat-restdrift-core.md`). Durchlauf 127 härtet zusätzlich SL-Referenz und Kampagnenübersicht: Pflicht-Heimkehr-Beat inkl. ITI-Lage-Zeile sowie Atlas/Kernpersonal als sichtbarer Runtime-SSOT-Anker (`internal/qa/plans/issue-pack-durchlauf-127-iti-ssot-verankerung-referenz-uebersicht.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-127-iti-ssot-verankerung-referenz-uebersicht.md`). Durchlauf 128 zieht die gleiche Atlas-/Alias-Logik in den internen Runtime-Stub nach und ersetzt dort Alt-Hauptorte durch kanonische Raum-IDs plus Alias-Bridge (`internal/qa/plans/issue-pack-durchlauf-128-iti-alias-drift-runtime-stub.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-128-iti-alias-drift-runtime-stub.md`). Durchlauf 129 ergänzt einen verpflichtenden ITI-Hardcanon-Watchguard im Smoke (`tools/test_iti_hardcanon_watchguard.js` + `scripts/smoke.sh`) und automatisiert damit Atlas/Kernpersonal/Driftbegriff-Checks (`internal/qa/plans/issue-pack-durchlauf-129-iti-hardcanon-watchguard-automation.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-129-iti-hardcanon-watchguard-automation.md`). Durchlauf 130 führt den Abschluss-/Übergabelauf vor dem nächsten DeepScan aus (Pflicht-Smoke + Linklint revalidiert, Tracking synchronisiert) (`internal/qa/plans/issue-pack-durchlauf-130-abschluss-vor-deepscan.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-130-abschluss-vor-deepscan.md`). Durchlauf 131 setzt anschließend die Start/MMO-Onboarding-Entschlackung um: natürliche Sprache als player-facing Einstieg, `klassisch + generate/custom generate/manuell` als Standardhierarchie, HQ-Save-Hinweis ohne Auto-Weiterleitung ins Briefing, Archetypen als Inspirationsmaterial sowie README/Setup-Harmonisierung (`internal/qa/plans/issue-pack-durchlauf-131-start-mmo-onboarding-entschlackung.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-131-start-mmo-onboarding-entschlackung.md`). Durchlauf 132 schärft den Praxisfall für Gruppen-Lobbys nach: JSON-first-Load ohne Pflichtkommando, `first JSON sets session_anchor` in Chatreihenfolge und ein explizites Split-Angebot nach Debrief+HQ (`internal/qa/plans/issue-pack-durchlauf-132-host-anchor-json-first-split-offer.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-132-host-anchor-json-first-split-offer.md`). Durchlauf 133 schließt den verbliebenen HQ-Menü-Restdrift in `core/sl-referenz.md`: Option 3 endet jetzt als `Auto-HQ -> Save anbieten` ohne automatisches Briefing und mit explizitem `!save`-/Chatwechsel-Hinweis (`internal/qa/plans/issue-pack-durchlauf-133-hq-menu-autobriefing-restfix.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-133-hq-menu-autobriefing-restfix.md`). Durchlauf 134 harmonisiert den verbliebenen Abschlussblock im Masterprompt (`## BEREIT`) auf denselben Startvertrag: natürliche Sprache als Einstieg, `solo klassisch` als Standard, `generate/custom generate/manuell` als primäre Charakterwahl und `solo schnell` nur noch als optionale Fast-Lane (`internal/qa/plans/issue-pack-durchlauf-134-masterprompt-bereit-startvertrag-restfix.md`, `internal/qa/logs/2026-03-09-issue-pack-durchlauf-134-masterprompt-bereit-startvertrag-restfix.md`). |
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

