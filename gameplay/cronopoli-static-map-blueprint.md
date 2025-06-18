---
title: "ZEITRISS 4.0 – Modul 18B: Cronopoli – Static Map Blueprint"
version: 4.0
tags: [gameplay]
---

# ZEITRISS 4.0 – Cronopoli Static Map Blueprint

*Grundplan einer statischen City-Map für das textbasierte GPT-Spiel*

## 1 | Macro-Layout (Top-Down)
```
         ┌──────────────────────────┐
         │   Ω-Ring Transit Line    │
┌────────┤────────┐  ▲  ┌───────────┤────────┐
│ Dock-  │        │  │  │           │ Bazaar │
│ yard Q │  N     │──┼──│  E        │ Q      │
│        │        │  │  │           │        │
└────────┴────────┘  ▼  └───────────┴────────┘
         │   Central Spire (Chronotorium)     │
┌────────┬────────┐     ┌───────────┬────────┐
│ Archive│        │     │           │Sanctuary│
│  Q     │  S     │     │  W        │   Q     │
│        │        │     │           │        │
└────────┴────────┘     └───────────┴────────┘
```
*Maßstab: Durchmesser 600 m, Straßenbreite 12 m, Spire 180 m hoch.*

### Quadranten
| ID  | Name                | Core Function    | Landmark              |
| --- | ------------------- | ---------------- | --------------------- |
| Q-N | **Temporal Dockyard** | Schiff-Spawn    | Neo-Ark Slip #01      |
| Q-E | **Chrono-Bazaar**     | Händlerdrehscheibe | Fractal Canopy Market |
| Q-S | **Eternal Archive**   | Lore & Quests    | Infinite Staircase    |
| Q-W | **Aion Sanctuary**    | Ruhezone         | Glass Wave Cathedral  |

## 2 | Vertikale Ebenen
| Layer        | Höhe   | Zweck                                       | Zugang                  |
| ------------ | ------ | ------------------------------------------- | ----------------------- |
| **Sub-Grid** | -20 m  | Wartungstunnel, optionale Arenen            | Servicelifts, versteckt |
| **Street**   | 0 m    | Hauptwege, Händlerstände                    | Alle Spieler            |
| **Ω-Ring**   | +25 m  | Mag-lev Loop zum Schnellreisen              | Rang ≥ 60               |
| **Sky-Deck** | +130 m | Nur Cutscene (Spitze des Spires)            | Entry-/Exit-Filmsequenz |

## 3 | Style-Bible
| Element          | Beschreibung                                                        |
| ---------------- | ------------------------------------------------------------------ |
| **Architektur**  | Weiße Terrazzoflächen mit titanfarbenen Rippen, Art-Déco trifft Möbius. |
| **Beleuchtung**  | Mischung aus kühlem Türkis und warmen Amber-Akzenten.                |
| **Skybox**       | Statische Nebelwolke mit leichten Zeitpartikeln.                    |
| **Ambient SFX**  | Dockyard: dumpfes Maschinenbrummen; Sanctuary: sanfte Glockenklänge. |
| **Props**        | Holo-Kioske mit Oktagon-Glyphen, Bänke mit integrierter Chrono-Kompass-Rose. |

## 4 | Spawn- und Navigationspunkte
| Tag          | Koordinaten (x,y,z) | Nutzung                                      |
| ------------ | ------------------ | --------------------------------------------- |
| `SPWN_PLAZA` | 0,0,0              | Standard-Einstieg auf der Paradox Plaza.     |
| `SPWN_DOCK`  | -260,180,0         | Tutorial für Schiffs-Upgrades.               |
| `SPWN_BAZ`   | 260,180,0          | Händler-Hotspot mit mindestens drei Verkäufern. |
| `SPWN_ARCH`  | -260,-180,0        | Questgeber-Cluster.                          |
| `SPWN_SANC`  | 260,-180,0         | Ruhiger Bereich zum Durchatmen.              |

## 5 | Vendor- und NPC-Sockets
Jedes 10x10-m-Straßenmodul besitzt zwei Sockets zur Platzierung von Händlern oder NPCs.
```
{
  "socket_id": "baz_12_B",
  "type": ["vendor","npc","event"],
  "level_min": 50,
  "level_max": 999
}
```
Die Engine ersetzt nur Population, keine Geometrie.

## 6 | Key Assets & Mod-Kit
| Kategorie            | File Prefix    | Poly-Budget | Hinweise                               |
| -------------------  | -------------- | ----------- | -------------------------------------- |
| **Building Shells**  | `bld_crono_*`  | 6–9k        | Sechs Wandmodule und drei Dachkappen.  |
| **Street Kit**       | `str_tile_*`   | 2k          | Gebogene und gerade Segmente.          |
| **Props**            | `prp_chrono_*` | 0.5–1.5k    | Bänke, Kioske, Holo-Lampen.            |
| **Spire**            | `ctr_spire`    | 18k         | Ein Hero-Mesh, vereinfachte Kollision. |
| **Ω-Train**          | `veh_maglev_*` | 4k          | Dreiteiliger Zug, splinebasiert.       |

## 7 | Cutscene-Pfad
| Waypoint | Aktion                                                     |
| -------- | ---------------------------------------------------------- |
| `C0`     | Start 100 m über dem Spire, Kamera neigt 15° nach unten.   |
| `C1`     | Abstieg auf 60 m, 20° Roll nach rechts, Ω-Ring wird sichtbar. |
| `C2`     | Kurzer Schwenk über Dockyard-Kräne (2 s).                  |
| `C3`     | Fahrt zur Paradox Plaza, Ausblendung 8 m über Boden.       |
*Gesamtlänge 5 s bei 60 fps.*

## 8 | Performance-Ziele
| Hardware            | FPS-Ziel         | Hinweise                                     |
| ------------------- | ---------------- | -------------------------------------------- |
| Mid-spec PC (2060)  | 90 fps Straße    | Instancing, LOD 0–2 bei 25/55/120 m.        |
| Aktuelle Konsolen   | 60 fps           | 30 % weniger Ω-Ring-Publikum.               |
| Low-end PC          | 45 fps           | Abschalten dynamischer Schatten außerhalb Plaza. |

## 9 | Build-Roadmap (6 Wochen)
| Woche | Meilenstein                                          |
| ----- | ---------------------------------------------------- |
| 1     | Greybox der Map (Street, Ring, Spire).               |
| 2     | Art-Pass Dockyard & Bazaar, Props im Greybox-Stil.   |
| 3     | Ω-Ring-Spline, Mag-lev, LOD-0-Assets.                |
| 4     | Licht & Skybox, Cutscene-Pfad.                       |
| 5     | Ambience, LOD-1/2, Kollisionen.                      |
| 6     | GPT-Socket-Test, QA und Performance-Sweep.           |

**Eine Map, unendliches Replay** – dieser Blueprint bildet die Grundlage für das
Endgame-Hub Cronopoli.
