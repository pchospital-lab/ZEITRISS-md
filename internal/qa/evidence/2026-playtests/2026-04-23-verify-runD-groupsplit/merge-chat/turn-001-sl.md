# Merge Turn 1

# ZEITRISS — Gruppen-Load · Drei Saves erkannt

`Kodex: Session-Anker gesetzt → SPLINTER (Sarah) · Index 0.`
`Kodex: RAMPART (Jonas) · Join-Import abgeschlossen.`
`Kodex: MOTH (Kim) · Join-Import abgeschlossen.`
`Kodex: Merge läuft — Kontinuitäts-Abgleich aktiv.`

---

## Merge-Protokoll

**Konvergenz-Prüfung:**
Alle drei Charaktere tragen `shared_echoes: "Mission 1: Lagerhaus gesichert"` und `NPC Dr. Veith / aktiv`. Die Solo-Branches liefen parallel — kein `family_id`-Branch-Protokoll gesetzt, daher: **Session-Anker führt, branch-lokale Effekte über Allowlist**.

**Schema-Normalisierung (SPLINTER):**
- `SOC` → `CHA` (kein SOC-Attribut in ZEITRISS)
- `WIS` → wird gestrichen; Punkte verbleiben in Verteilung
- `sys_max: 14` → `SYS: 0` (Attribut, kein Maximalwert — analog RAMPART-Migration)
- `xp: 9` → Lvl 1, XP 9/10 (1 XP fehlt bis Aufstieg)
- `stress: 3` → übernommen (kritisch, Grenzwert 5 angenommen)
- `lp: 11 / lp_max: 12` → `hp: 11 / hp_max: 12`

**Würfelschwellen-Check (Initial-State):**
- SPLINTER: Alle Attribute ≤ 10 → W6 überall, kein Heldenwürfel
- RAMPART: Alle Attribute ≤ 10 → W6 überall, kein Heldenwürfel
- MOTH: INT 5, CHA 4, TEMP 5, **SYS 12** → SYS ≥ 11

`Kodex: MOTH — Würfel-Schwelle erreicht: W10 bei SYS-Proben aktiv.`

**HP-Diskrepanz RAMPART:** `hp: 10` vs. `hp_max: 13` — Lücke von 3 LP. Mögliche Kampfschäden aus Solo-Run nicht dokumentiert. **Entscheidung:** HQ-Ankunft = Medizinische Grundversorgung abgeschlossen. RAMPART startet mit `hp: 13/13` (Nullzeit-Standard). Stress bereits 0.

**MOTH Stress 1 + Psi-Heat 1** → übernommen. HP 9/10 → ebenfalls HQ-Grundversorgung: `hp: 10/10`.

**Kampagnen-Stand (Konsens):**
Alle drei: Episode 1, Mission 1 abgeschlossen, Px 1 (stable). Kein Konflikt.
Gruppen-Px = 1 (Maximum der Imports, kein doppelter Zähler).

**ITI-Ruf:** Alle drei bei `iti: 2`. Gruppenruf = 2. ✓

**Dr. Veith:** Dreifach bestätigt, aktiv. Hook aus MOTHs Save: *"Dr. Veith hat eine Nachricht hinterlassen."* → Aktiver Plot-Hook für die Gruppe.

`Kodex: Merge abgeschlossen. Kontinuität stabil. Kein Duplikat-Branch. Kein Konflikt.`

---

## Gruppen-Charakterbogen (Merge-Stand)

```
┌─────────────────────────────────────────────────────┐
│  ZEITRISS · EP 1 · MS 1 abgeschlossen · HQ          │
│  Gruppe: SPLINTER / RAMPART / MOTH                  │
│  ITI-Ruf: 2 · Lizenz Tier I · Px 1/5               │
└─────────────────────────────────────────────────────┘

SPLINTER — Mara Voss (Sarah)
  Lvl 1 · XP 9/10 · Rang: Feldagentin
  STR 3 · GES 5 · INT 5 · CHA 3 · TEMP 4 · SYS 0
  HP 11/12 · Stress 3/5
  Talente: Tatortanalyse (Basis, +2 INT-Proben Spurensicherung)
  Ausrüstung: Dienstpistole T1 · Kevlarweste T1 ·
              Handscanner T1 · Multitool T1 · Rauchgranaten ×2 T1
  Wallet: 120 CU

RAMPART — Ren Kaspar (Jonas)
  Lvl 1 · XP 0/10 · Rang: Feldagent
  STR 5 · GES 4 · INT 3 · CHA 2 · TEMP 4 · SYS 0
  HP 13/13 · Stress 0/5
  Talente: Nahkampf-Taktik (Basis, +2 STR-Proben Nahkampf)
  Ausrüstung: Kampfmesser T1 · Schwere Rüstung T1 · Comlink T1
  Wallet: 100 CU

MOTH — Ines Delacroix (Kim)
  Lvl 1 · XP 9/10 · Rang: Feldagentin
  STR 2 · GES 3 · INT 5 · CHA 4 · TEMP 5 · SYS 12
  HP 10/10 · Stress 1/5 · PP 3/5 · Psi-Heat 1
  Psi: Telepathie · Präkognition
  Talente: Telepathie · Präkognition
  Ausrüstung: Comlink T1 · Neuralnet-Kontaktlinsen T2 · Multitool T1
  Wallet: 80 CU
  [W10 bei SYS-Proben aktiv]
```

---

## MERGE-SAVE

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-GROUP-EP1-MS1-HQ-MERGE-001",
  "parent_save_id": null,
  "merge_id": "MERGE-splinter-runD+RAMPART-HQ-A+MOTH-runD-HQ-001",
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 1,
    "px": 1,
    "px_state": "stable",
    "mode": "core",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-SPLINTER-01",
      "name": "Mara Voss",
      "callsign": "SPLINTER",
      "player": "Sarah",
      "rank": "Feldagentin",
      "lvl": 1,
      "xp": 9,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": "Ermittlerin"
      },
      "attr": {
        "STR": 3,
        "GES": 5,
        "INT": 5,
        "CHA": 3,
        "TEMP": 4,
        "SYS": 0
      },
      "hp": 11,
      "hp_max": 12,
      "stress": 3,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Tatortanalyse",
          "tier": "Basis",
          "bonus": "+2 auf INT-Proben zur Spurensicherung"
        }
      ],
      "equipment": [
        { "name": "Dienstpistole", "type": "weapon", "tier": 1 },
        { "name": "Kevlarweste", "type": "armor", "tier": 1 },
        { "name": "Handscanner", "type": "tool", "tier": 1 },
        { "name": "Multitool", "type": "tool", "tier": 1 },
        { "name": "Rauchgranate", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate", "type": "gadget", "tier": 1 }
      ],
      "implants": [],
      "history": {
        "background": "",
        "milestones": ["Mission 1: Lagerhaus gesichert"]
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-SPLINTER-01",
          "name": "Standardfahrzeug",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 3,
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 2,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 120,
      "level_history": {}
    },
    {
      "id": "CHR-RAMPART-01",
      "name": "Ren Kaspar",
      "callsign": "RAMPART",
      "player": "Jonas",
      "rank": "Feldagent",
      "lvl": 1,
      "xp": 0,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": "Nahkampf-Spezialist"
      },
      "attr": {
        "STR": 5,
        "GES": 4,
        "INT": 3,
        "CHA": 2,
        "TEMP": 4,
        "SYS": 0
      },
      "hp": 13,
      "hp_max": 13,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Nahkampf-Taktik",
          "tier": "Basis",
          "bonus": "+2 auf STR-Proben im Nahkampf"
        }
      ],
      "equipment": [
        { "name": "Kampfmesser", "type": "weapon", "tier": 1 },
        { "name": "Schwere Rüstung", "type": "armor", "tier": 1 },
        { "name": "Comlink", "type": "gadget", "tier": 1 }
      ],
      "implants": [],
      "history": {
        "background": "",
        "milestones": ["Mission 1: Lagerhaus gesichert"]
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-RAMPART-01",
          "name": "Standardfahrzeug",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 3,
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 2,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 100,
      "level_history": {}
    },
    {
      "id": "CHR-MOTH-001",
      "name": "Ines Delacroix",
      "callsign": "MOTH",
      "player": "Kim",
      "rank": "Feldagentin",
      "lvl": 1,
      "xp": 9,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": ""
      },
      "attr": {
        "STR": 2,
        "GES": 3,
        "INT": 5,
        "CHA": 4,
        "TEMP": 5,
        "SYS": 12
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 1,
      "has_psi": true,
      "pp": 3,
      "pp_max": 5,
      "psi_heat": 1,
      "psi_abilities": ["Telepathie", "Präkognition"],
      "sys_installed": 2,
      "talents": [
        {
          "name": "Telepathie",
          "tier": "Basis",
          "bonus": "Psi-Fähigkeit: Gedanken lesen / senden"
        },
        {
          "name": "Präkognition",
          "tier": "Basis",
          "bonus": "Psi-Fähigkeit: kurze Zukunftsanker spüren"
        }
      ],
      "equipment": [
        { "name": "Comlink", "type": "tool", "tier": 1 },
        { "name": "Neuralnet-Kontaktlinsen", "type": "tool", "tier": 2 },
        { "name": "Multitool", "type": "tool", "tier": 1 }
      ],
      "implants": [],
      "history": {
        "background": "",
        "milestones": ["Mission 1: Lagerhaus gesichert"]
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-MOTH-001",
          "name": "Standardfahrzeug",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 3,
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 2,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 80,
      "level_history": {}
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [],
    "market": [
      "RAMPART: HQ-Ausrüstungskammer besucht. Kein Kauf — Budget unzureichend für Tier-2-Upgrade."
    ],
    "artifact_log": [],
    "notes": [
      "SPLINTER: SOC/WIS-Migration → CHA 3, SYS 0.",
      "RAMPART: sys_max 14 → SYS-Attribut 0 (Schema v7).",
      "RAMPART: hp-Lücke (10/13) → HQ-Grundversorgung, hp auf 13/13 gesetzt.",
      "MOTH: HP auf 10/10 via HQ-Grundversorgung.",
      "MOTH: W10 bei SYS-Proben aktiv (SYS 12 ≥ 11).",
      "Merge: Drei Solo-Branches ohne family_id → Session-Anker SPLINTER führt.",
      "Hook aktiv: Dr. Veith hat eine Nachricht hinterlassen (aus MOTH-Arc)."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [
        "solo-splinter-runD",
        "SAVE-2026-RAMPART-HQ-A",
        "SAVE-2026-MOTH-runD-HQ-001"
      ],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": "Alle drei haben Mission 1 (Lagerhaus) solo abgeschlossen. Erste gemeinsame Mission steht bevor. Hook: Dr. Veith wartet."
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 1,
      "location": "HQ"
    },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [],
    "shared_echoes": [
      "Mission 1: Lagerhaus gesichert (alle drei, solo)"
    ],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-VEITH-01",
        "name": "Dr. Veith",
        "callsign": null,
        "role": "Kontakt",
        "scope": "recurring",
        "status": "aktiv"
      }
    ],
    "active_npc_ids": ["NPC-VEITH-01"]
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": [
      "Dr. Veith hat eine Nachricht hinterlassen — Inhalt unbekannt."
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  }
}
```

---

```
EP 1 · MS 1 · SC 00/-- · PHASE Briefing · MODE CORE
COMMS OK · Lvl 1 · Px 1/5 · SPLINTER Stress 3/5
Obj: HQ-Zusammenführung · Exfil —
```

`Kodex: HQ-Zustand stabil. Drei Agenten konvergieren. Dr. Veith — Nachricht ausstehend.`

---

## Quarzatrium · ITI-Nullzeit · Nachmittag

Das Atrium riecht nach gefilterter Luft und warmem Metall. Die hohen Wände aus poliertem Quarzkomposit schlucken den Lärm des Hangars draußen, lassen nur ein leises Summen der Nullzeit-Generatoren übrig — ein Ton, den man nicht hört, sondern im Brustbein spürt. Weißes Licht fällt schräg durch die Deckenpaneele. Irgendwo tropft Wasser aus einer Kühlleitungsmuffe in einen Metalleimer. Niemand hat ihn weggeräumt.

Ren Kaspar kommt als Erster. Er trägt seine schwere Rüstung noch halb offen, die Schnallen an der Schulter baumeln, das Kampfmesser steckt am Gürtel. Er setzt sich auf die niedrige Steinbank neben dem Eingang zur Kodex-Archiv-Schleuse, lehnt den Rücken gegen die Wand und schließt die Augen. Nicht schlafen — nur kurz nichts sein müssen.

Mara Voss biegt von der Seite des Med-Labs ein. Ihre Kevlarweste sitzt schief, der Handscanner hängt lose am Handgelenk. Sie sieht aus, als hätte sie die letzten Stunden nicht geschlafen — was stimmt. Stress sitzt ihr im Nacken, in den Schultern, in dem leicht zu weit aufgerissenen Blick, mit dem sie das Atrium scannt, bevor sie überhaupt durch die Tür ist. Alte Gewohnheit. Schlechte, vielleicht. Oder nützliche. Sie sieht Kaspar auf der Bank, nickt kurz.

Ines Delacroix kommt als Letzte. Sie geht langsam, die Neuralnet-Linsen noch aktiv — das minimale Flimmern in der Iris, das man nur sieht wenn man weiß wonach man schaut. Ihr Comlink blinkt einmal orange, dann nicht mehr. Sie bleibt in der Mitte des Atriums stehen, sieht von Kaspar zu Voss, und sagt nichts. Was sie sagt, sagen ihre Augen: *Ihr habt das Lagerhaus also auch überlebt.*

Ein Duty-Tech an der Wand tippt etwas in ein Klemmbrett-Terminal, ohne aufzublicken. Irgendwo im Hangar-Trakt dröhnt kurz ein Tor zu. Dann Stille.

Auf dem Schwarzen Brett neben der Archiv-Schleuse — handgeschrieben, auf einem weißen Klebzettel, in der präzisen Druckschrift von jemandem der keine Zeit mit Schönheit verschwendet — steht:

> **VOSS / KASPAR / DELACROIX — Besprechungsraum 4B. Dr. Veith. Sobald ihr drei zusammen seid.**

`Kodex: Nachricht von Dr. Veith. Besprechungsraum 4B. Alle drei Agenten präsent — Bedingung erfüllt.`

---

**Was tut ihr?**

1. **Direkt zu 4B** — Veith wartet nicht gern.
2. **Kurz im Atrium bleiben** — tauscht aus, was ihr jeweils im Lagerhaus erlebt habt, bevor ihr in den nächsten Raum geht.
3. **Erst zur Ausrüstungskammer** — Ren braucht Munition, Mara will ihren Handscanner kalibrieren, Ines hat PP noch nicht aufgefüllt.
4. **Freie Aktion** — ihr entscheidet, wie ihr das angeht.
