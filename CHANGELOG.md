---
title: "Changelog"
version: 4.2.2
tags: [meta]
---

# Changelog

## [Unveröffentlicht]

- `AGENTS.md` fokussiert den Repo-Agenten auf Rollen, Übergaben und verweist auf den
  Beitragsleitfaden.
- `CONTRIBUTING.md` bündelt die Qualitäts-, Link- und Compliance-Checkliste sowie den vollständigen
  Pflicht-Testkatalog.
- README-Dokumenten-Landkarte reflektiert die neue Aufgabenverteilung zwischen `AGENTS.md` und
  `CONTRIBUTING.md`.

## 4.2.2 – Arena-Episodenstempel

QA-Nachweis: [QA-Log 2025-03-19 – Acceptance-Smoke-Abgleich][qa-log-2025-03-19].
- PvP-Arena vergibt den Px-Bonus nur einmal pro Episode; `arena_episode_stamp` ist in
  Kampagnenstruktur und Runtime-Stubs dokumentiert.
- Makefile ergänzt `lint`- und `test`-Targets, damit Standard-Checks direkt über `make` anlaufen.
- `tech_solution()` staffelt `tech_heat` nach Teamgröße und erzwingt für Solo- und Duo-Teams einen
  Gerätezwang über `confirm_device_slot()`.
- `AGENTS.md` und `CONTRIBUTING.md` präzisieren den Ablauf für Beta-GPT- und KI-Review-Reports.
- QA-Standardprompt simuliert komplette Läufe autonom und liefert strukturierte `ISSUE`-,
  `Lösungsvorschlag`-, `To-do`- und `Nächste Schritte`-Blöcke; Dokumentation in README, Maintainer-Ops,
  QA-Fahrplan, QA-Audit, QA-Log und Tester-Briefing angepasst.

## 4.0.1

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Rewrapped long lines in `README.md`, `meta/masterprompt_v6.md` and `core/wuerfelmechanik.md`.
- Added this changelog file.

## 4.0.2

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Removed redundant lines in README for clarity.

## 4.0.3

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Added historical anomaly table and puzzle sets in `gameplay/kreative-generatoren-missionen.md` and
  `gameplay/kreative-generatoren-begegnungen.md`.
- Introduced contextual `historical_faction` pool in `master-index.json`.

## 4.0.4

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Converted historical anomalies section to YAML blocks.
- Kürzere Rätsel-Set-Texte und klarere Missionstrennung in README.

## 4.0.5

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Erweiterte Speicherhinweise und manuelle Backup-Option im README.
- Diverse Korrekturen an Savegame-Beispielen und Missionstabellen.

## 4.0.6

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Ergänzt Psi-Sektion "Phase-Strike" mit Anker und Referenz.
- Kleinere Textpflege in `psi-talente.md`.

## 4.1.0

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Reworked Dice Mechanics to additive model.
- W10 explodes on 10; removed SG+4 and W8 step.
- Heldenwürfel erst ab 14, einmaliger Reroll.
- Aktualisierte Beispiele, HUD-Hinweise und Vehicle-Note.

## 4.1.1

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Item Tier pass-balance (Scout Communicator jetzt Kodex-Relay-Knoten, T2 Perks, heavy gear +1 SYS).
- Med-Auto-Kit Preis 200 CU, Nahkampf-Mod Kritbonus +2 DMG.
- Versionstexte auf 4.1.1 aktualisiert.

## 4.1.2

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Neues SceneCounter-System mit HUD-Anzeige.
- Core-Ops bestehen jetzt aus **12 Szenen**, Rift-Ops aus **14 Szenen**.
- Erfahrung: 1 Mission = 1 Level (bis Stufe 10).
- Überarbeitetes Rift-Op-Template im Kampagnenmodul.
- HUD zeigt `PAR n/5 · SC x/50 · Time t` an.

## 4.1.3 – ItemForge Tier-Generator

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Neues Macro `itemforge()` im Toolkit.
- Loot-Tabellen tragen eindeutige `id:`-Felder.
- HUD meldet `HEAVY LOCK` bei fehlender Lizenz für Heavy-Gear.

## 4.1.4 – Era-Pulse Patch

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Historische Missionsziele mit Preserve- und Trigger-Formulierungen.
- Rift-Seeds enthalten verdeckte Ursachen.
- Loot besitzt `altSkin` für epochegerechte Varianten.
- Neues Macro `ParadoxPing()` und Befehl `!seed` dokumentiert.

## 4.1.5 – Scene Template Update

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Standard-Format auf **12 Szenen** (Core) bzw. **14 Szenen** (Rift) festgelegt.
- Demo-Mission "Feuerkette 1410" an neues Format angepasst.
- Toolkit enthält `StartScene` und `EndScene` Macros.

## 4.1.6 – Readme Clarifications

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Seed-Beispiel zeigt nun Preserve- und Trigger-Varianten.
- Standardmodus betont fortlaufende Core-Ops als Arc.

## 4.1.7 – HUD Readability Fix

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- `StartScene`-Macro bricht HUD-Zeile jetzt um, um Scrollen zu vermeiden.

## 4.1.8 – Terminology Revert

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Reverted "Interventionsformen" back to "Missionstypen" und integrierte die Begriffszuordnung im
  README.
- Klarstellung: Mission-Fokus richtet sich gegen Fremdfraktionen, kein PvP im Standardmodus.
- Updated Toolkit und Generatoren entsprechend.

## 4.1.9 – Manual Roll Mode

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Neuer `/roll manual` Schalter für analoges Würfeln.
- Exploding-Regel greift weiterhin bei 6 bzw. 10.

## 4.2.0 – Paradoxon Rework

QA-Nachweis: Legacy-Abnahme (vor 2025, intern archiviert).
- Paradoxon-Index fungiert jetzt als Resonanzanzeige.
- `ClusterCreate()` enthüllt bei Stufe 5 neue Rift-Seeds.
- Dokumentation an mehreren Stellen angepasst.
- Resonanzpunkte verleihen kleine Boni (−1 Stress, Heilung usw.) bei jedem Anstieg.
- RiftSeed-Tabelle überarbeitet: neue Cryptid-Seeds ergänzt.
- Neuer Erzählmodus **Verbose** ergänzt; **Precision** weiter verfügbar.
- HUD-Befehl `regelcheck` lädt Regelmodule auf Anfrage neu.
- PvP-Arena: Best-of-Three-Sieger erhalten +1 Px statt Paradoxon-Reset.
- Arena-Regeln präzisiert: Szenario-Pool, balanciertes Matchmaking und HUD-Scoreboard.
- Optionales 1v1-Duell und Balance-Hinweise zu Psi-Kräften und Artefakten.
- Legendary Artefakt-Pool v3 mit 14 Parawesen-Trophies; Makro `roll_legendary()` und JSON-Lookup.
- `NextScene` ersetzt manuelle `StartScene`/`EndScene`-Aufrufe, ergänzt `Objective`- und
  `Seed`-Zeilen, Boss- und Artefaktmeldungen sowie `EndMission`-Kodex-Logs.

- Save-Befehl nur noch im HQ; `cmdSave` verhindert Speichern unterwegs.
- `maintain_cooldowns` räumt Nullwerte auf, HQ-Szenen löschen Rest-Cooldowns und setzen `sys_used`
  zurück.
- Psi-Kräfte erhöhen `sys_used`; Artefakt-Makros loggen Funde in `artifact_log` und
  `kodex_log_artifact`.
- Boss-Generator nutzt bei Rifts die Missionsnummer und meldet Szene 10 klar im HUD.

- Verankerte Funksignale an reale Hardware in Masterprompt und Toolkit.
- `signal_space`-Stilfilter eingeführt; StartMission betont physische Umgebung.
- Missions- und Begegnungstabellen nennen konkrete Geräte statt abstrakter Signale.
- `Kodex-Relay-Knoten` beschreibt Reichweite und Störquellen.
- Kodex-Verbindung zum Nullzeit-HQ-Archiv als reale Funkstrecke klargestellt.
- `hud_vocab` enthält zusätzliche Noir-Phrasen; Macro `noir_soft()` gibt sie als HUD-Code aus.
- Neues Macro `TK_Melee()` prüft SR ≥ 2 und erhöht die SG entsprechend.
- `tech_solution()` triggert `inject_complication()` einmalig nach dem vierten Tech-Schritt.

- Modulanzahl im README auf 25 und Slug-Liste bereinigt.
- HUD-Modul in Kategorie "Characters" geführt.
- Masterprompt nicht mehr im `master-index.json`.
- Tests im Runtime-Stub als Pflichtschritt klargestellt.

## 4.2.1 – Docs & Flow Hardening

QA-Nachweis: [QA-Log 2025-03-17 – Beta GPT – Build 4.2.2][qa-log-2025-03-17].
- LLM-Dispatcher dokumentiert und HQ-only Save gehärtet.
- Paradoxon/Rift-Terminologie vereinheitlicht, Gear-Alias-Map ergänzt.

## 4.2.2 – DPMA Trademark

QA-Nachweis: [QA-Log 2025-03-17 – Beta GPT – Build 4.2.2][qa-log-2025-03-17].
- Lizenz auf eingetragene Marke aktualisiert.
- README und neue Dokumentation zur DPMA-Urkunde.

## 4.2.2 – Masterprompt Hardening

QA-Nachweis: Maintainer-Sync 2025-03-19 – Prompt Hardening (intern).
- Masterprompt 4.2.2 geschärft: direkte Modulverweise, straffere Sicherheits- und
  Generatorleitplanken, Selbstbegegnungen standardmäßig deaktiviert.
- DeepSave-Pflicht nach jeder Sitzung mit kanonischem JSON-Block im Prompt verankert und YAML-Header
  entfernt.
- Maintainer-Guides (`AGENTS.md`, `CONTRIBUTING.md`) dokumentieren die 8 k-Grenze und die YAML-
  Ausnahme des Masterprompts.

[qa-log-2025-03-19]:
  internal/qa/logs/2025-beta-qa-log.md#2025-03-19--beta-gpt--build-422-acceptance-smoke-abgleich
[qa-log-2025-03-17]:
  internal/qa/logs/2025-beta-qa-log.md#2025-03-17--beta-gpt--build-422

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
