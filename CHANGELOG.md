---
title: "Changelog"
version: 1.0
tags: [meta]
---

# Changelog

## 4.0.1
- Rewrapped long lines in `README.md`, `meta/masterprompt_v6.md` and `core/wuerfelmechanik.md`.
- Added this changelog file.

## 4.0.2
- Removed redundant lines in README for clarity.

## 4.0.3
- Added historical anomaly table and puzzle sets in
  `gameplay/kreative-generatoren-missionen.md` and
  `gameplay/kreative-generatoren-begegnungen.md`.
- Introduced contextual `historical_faction` pool in `master-index.json`.

## 4.0.4
- Converted historical anomalies section to YAML blocks.
- Kürzere Rätsel-Set-Texte und klarere Missionstrennung in README.

## 4.0.5
- Erweiterte Speicherhinweise und manuelle Backup-Option im README.
- Diverse Korrekturen an Savegame-Beispielen und Missionstabellen.

## 4.0.6
- Ergänzt Psi-Sektion "Phase-Strike" mit Anker und Referenz.
- Kleinere Textpflege in `psi-talente.md`.

## 4.1.0
- Reworked Dice Mechanics to additive model.
- W10 explodes on 10; removed SG+4 and W8 step.
- Heldenwürfel erst ab 14, einmaliger Reroll.
- Aktualisierte Beispiele, HUD-Hinweise und Vehicle-Note.

## 4.1.1
- Item Tier pass-balance (Scout Communicator jetzt Codex-Relay-Knoten, T2 Perks, heavy gear +1 SYS).
- Med-Auto-Kit Preis 200 CU, Nahkampf-Mod Kritbonus +2 DMG.
- Versionstexte auf 4.1.1 aktualisiert.

## 4.1.2
- Neues SceneCounter-System mit HUD-Anzeige.
- Core-Ops bestehen jetzt aus **12 Szenen**, Rift-Ops aus **14 Szenen**.
- Erfahrung: 1 Mission = 1 Level (bis Stufe 10).
- Überarbeitetes Rift-Op-Template im Kampagnenmodul.
- HUD zeigt `[PAR n/5 | SC x/50 | Time t]` an.

## 4.1.3 – ItemForge Tier-Generator
- Neues Macro `itemforge()` im Toolkit.
- Loot-Tabellen tragen eindeutige `id:`-Felder.
- HUD meldet `[HEAVY LOCK]` bei fehlender Lizenz für Heavy-Gear.

## 4.1.4 – Era-Pulse Patch
- Historische Missionsziele mit Preserve- und Trigger-Formulierungen.
- Rift-Seeds enthalten verdeckte Ursachen.
- Loot besitzt `altSkin` für epochegerechte Varianten.
- Neues Macro `ParadoxPing()` und Befehl `!seed` dokumentiert.

## 4.1.5 – Scene Template Update
- Standard-Format auf **12 Szenen** (Core) bzw. **14 Szenen** (Rift) festgelegt.
- Demo-Mission "Feuerkette 1410" an neues Format angepasst.
- Toolkit enthält `StartScene` und `EndScene` Macros.

## 4.1.6 – Readme Clarifications
- Seed-Beispiel zeigt nun Preserve- und Trigger-Varianten.
- Standardmodus betont fortlaufende Core-Ops als Arc.

## 4.1.7 – HUD Readability Fix
- `StartScene`-Macro bricht HUD-Zeile jetzt um, um Scrollen zu vermeiden.

## 4.1.8 – Terminology Revert
- Reverted "Interventionsformen" back to "Missionstypen" und integrierte die Begriffszuordnung im README.
- Klarstellung: Mission-Fokus richtet sich gegen Fremdfraktionen, kein PvP im Standardmodus.
- Updated Toolkit und Generatoren entsprechend.

## 4.1.9 – Manual Roll Mode
- Neuer `/roll manual` Schalter für analoges Würfeln.
- Exploding-Regel greift weiterhin bei 6 bzw. 10.

## 4.2.0 – Paradoxon Rework
- Paradoxon-Index fungiert jetzt als Resonanzanzeige.
- `ClusterCreate()` enthüllt bei Stufe 5 neue Rift-Seeds.
- Dokumentation an mehreren Stellen angepasst.
- Resonanzpunkte verleihen kleine Boni (−1 Stress, Heilung usw.) bei jedem Anstieg.
