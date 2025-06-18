---
title: "ZEITRISS 4.0 – Modul 18: Cronopoli Living-Instance Guide"
version: 4.0
tags: [gameplay]
---

# ZEITRISS 4.0 – Cronopoli "Living-Instance" Guide

*Implementations-Package für Code, Art & Content*

## 1 | High-Level-Pitch

> **Cronopoli** ist ein **statische Megastruktur** aus einer *möglichen Zukunft, die nie eintreten wird*.
> Architektur & Straßenzüge bleiben unverändert.
> **Bewohner, Händler und Begegnungen werden bei jedem Betreten vollständig neu instanziiert** – so wirkt die Stadt stets frisch,
> ohne dass wir mehr als **eine** Map modellieren müssen.
> Die ringförmige Stadt schmiegt sich wie ein Wurm um das zentrale ITI-Hauptquartier.

## 2 | Freischalt-Logik

| Flag            | Wert                                                              |
| --------------- | ----------------------------------------------------------------- |
| **Rank-Gate**   | `PLAYER_RANK ≥ 50` *(änderbar in Config)*                         |
| **Key-Item**    | `itm_quant_key` (Erhalt beim Rang-Up 50)                          |
| **Entry-Event** | `evt_enter_cronopoli()` *(wie zuvor, Rank-Check auf 50 anpassen)* |

## 3 | Instanzierungs-Pipeline

```mermaid
graph TD
A[Player betreten Zone] --> B[Load static city geometry]
B --> C[Seed RNG = UTC-Timestamp]
C --> D[GPT-Stub: getCronopoliPopulation(seed)]
D --> E[NPC / Vendor Pool in RAM]
```

### 3.1 GPT-Stub-Signature

```json
POST /gpt/getCronopoliPopulation
{
  "seed": 1696851200,
  "player_rank": 52,
  "flags": ["temporal_ship_unlocked"]
}
```

**Response** – Beispiel

```json
{
  "vendors": [
    {
      "id": "vend_neoark",
      "type": "Temporal Shipwright",
      "inventory": ["timesloop_schooner", "chronoglider_mk2"],
      "greeting": "Sturm der Äonen, Captain?"
    },
    ...
  ],
  "npcs": [
    {"id":"npc_oracle", "role":"Rumormonger", "hook":"Seed about 1883 Krakatoa Rift"},
    ...
  ]
}
```

*→ Engine erstellt Instanz; Cache gilt bis Spieler Zone verlässt.*

## 4 | Content-Richtlinien für dynamische Bevölkerung

| Kategorie          | Mindest-Pool | Beispiele                             | Regel-Notizen           |
| ------------------ | ------------ | ------------------------------- | --------------------------- |
| **Händler**        | 6            | Temp. Shipwright, Antikythera Arch., Dieselpunk Shop | 3–5 Items, 1 Prototyp |
| **Quest-Giver**    | 3            | Rift Cartographer, Lost-Era Agent, Flux-Smuggler | Seeds, Gerüchte oder Side-Ops |
| **Atmosphäre NPC** | 10           | Sprawl-Pilger, Android Poet, Retro-Cyber Monk | Kein Handel; nur Flavor |
| **Event-NPC**      | 1            | Random Duelist, Street-Race Announcer | 10 % Spawn-Chance; Mini-Game |

## 5 | Item- & Service-Matrix in Cronopoli

| Kategorie             | Nutzen                                   | Preis    | Paradox-Risiko             |
| --------------------- | ---------------------------------------- | -------- | -------------------------- |
| **Temporal Ships**    | Inter-Epoch Travel / Schnell-Exfil       | 5 000 CU | +1 PP bei Erstflug         |
| **Never-Was Gadgets** | Einmal-Buffs (z. B. "Quantum Flashbang") | 500 CU   | +1 PP bei öffentl. Nutzung |
| **Era-Skins**         | Kosmetisch                               | 200 CU   | 0                          |
| **Shard Exchange**    | 5 Shards → 500 CU                        | —        | 0                          |

*PP = Paradox-Punkte. Tabelle direkt in `cu_waehrungssystem.md` referenzieren.*

## 6 | No-Go-Zonen (Style-Compliance)

* **Keine Meta-Reveals** über Realität / Bewusstsein.
* **Keine Variablen Stadtgeometrie** – Gebäude bleiben identisch, nur Personen wechseln.
* **Keine Auto-Paradox-Explosion** beim Betreten; Cronopoli ist *zeitverankert*.

## 7 | Cutscene & UI-Flow

1. **Warn-Popup (einmalig)**
   „Cronopoli entzieht sich jeder bekannten Zeitlinie. Nur wer die Konsequenzen akzeptiert, tritt ein.“
   Buttons: *Abbrechen* / *Eintreten*
2. **5-s Establishing Shot** über ringförmige Skyline → Fade to Player Spawn-Point „Paradox Plaza“.
3. **UI-Banner**: „Bewohner wechseln mit jedem Besuch – halte Ausschau nach seltenen Händlern!“

*(Assets: Skyline-Mat, Plaza Spawn-Statue, 2x Ambient Loop.)*

## 8 | Dev-Task-Board

| Task                          | Owner     | ETA    |
| ----------------------------- | --------- | ------ |
| Static City Map Greybox       | Level Art | 7 Tage |
| GPT-Stub & RNG-Seed           | Backend   | 5 Tage |
| Vendor / NPC Scriptables      | Gameplay  | 6 Tage |
| UI Warn-Popup & Banner        | UX        | 4 Tage |
| Cutscene Camera Path          | Animator  | 5 Tage |
| QA Pass (Rank 50 unlock flow) | QA        | 3 Tage |

## 9 | Beispiel-Run (Spieler Rank 53)

1. Spieler klickt „Cronopoli betreten“.
2. Engine ruft GPT-Stub mit Seed `2025-06-18-T19:15:00Z`.
3. Stadt lädt, 8 Händler & 15 NPC erscheinen.
4. Händler „Temporal Shipwright Novara“ bietet **Chronoglider MK II** an.
5. Spieler kauft Item → +1 Paradox-Punkt erst beim ersten Einsatz außerhalb Cronopoli.
6. Verlassen → Instanz-Cache gelöscht. Nächster Eintritt ⇒ komplette Neu-Population.

**Ready for hand-off – alles zur Implementierung steht hier.**
