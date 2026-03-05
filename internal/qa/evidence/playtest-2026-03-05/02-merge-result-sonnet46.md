# Merge-Test Ergebnis

# ZEITRISS — Team-Merge: Save A + Save B

## Merge-Protokoll

**Kodex:** Zwei Gruppen-Saves erkannt. Starte Konsolidierung.

---

### Merge-Regeln (transparent):

| Feld | Entscheidung |
|---|---|
| `campaign.episode` | 1 → beide gleich ✓ |
| `campaign.mission` | 0 → beide gleich ✓ |
| `campaign.px` | Max-Wert: **2** (Save B höher) |
| `campaign.rift_seeds` | Union: RS-001 + RS-002 |
| `characters[]` | CHR-0001 bis CHR-0005, Host = CHR-0001 (Index 0) |
| `economy.hq_pool` | Summiert: 3500 + 3200 = **6700 CU** |
| `logs.trace` | Beide Events gemergt |
| `logs.artifact_log` | ART-001 + ART-002 |
| `logs.notes` | Beide Notes gemergt |
| `arc.factions` | Union, Konflikte: Kausalklingen doppelt → behalten (gleich), Zerbrechliche Ewigkeit aus B übernommen |
| `arc.questions` | Beide gemergt |
| `arc.hooks` | Alle 3 Hooks gemergt |
| `flags.chronopolis_unlocked` | true (beide) |
| `ui` | Save A (Host) |
| `campaign.mode` | mixed (beide gleich) |

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "campaign": {
    "episode": 2,
    "mission": 0,
    "px": 2,
    "mode": "mixed",
    "rift_seeds": [
      {
        "id": "RS-001",
        "epoch": "1347",
        "label": "Pestlabor-Anomalie",
        "status": "closed",
        "tier": "early"
      },
      {
        "id": "RS-002",
        "epoch": "2089",
        "label": "Orbital-Datenleck",
        "status": "closed",
        "tier": "early"
      }
    ]
  },
  "characters": [
    {
      "id": "CHR-0001",
      "name": "Viktor Kowalski",
      "callsign": "Hammer",
      "rank": "Operator I",
      "lvl": 11,
      "xp": 12,
      "origin": {
        "epoch": "1988",
        "hominin": "Homo sapiens sapiens",
        "role": "Breacher"
      },
      "attr": {
        "STR": 9,
        "GES": 5,
        "INT": 3,
        "CHA": 3,
        "TEMP": 3,
        "SYS": 3
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 3,
      "talents": [
        { "name": "CQB-Spezialist II", "tag": "melee", "bonus": 2 },
        { "name": "Sprengmeister", "tag": "demolition", "bonus": 2 }
      ],
      "equipment": [
        { "name": "Kampfschrotflinte", "type": "weapon", "tier": 2 },
        { "name": "Breaching-Charges x3", "type": "gadget", "tier": 2 },
        { "name": "Schwere Kevlar-Weste", "type": "armor", "tier": 2, "dr": 3 },
        { "name": "Pest-Antiserum x2", "type": "consumable" }
      ],
      "implants": [
        { "name": "Muskel-Servos", "sys_cost": 2, "effect": "+1 STR-Proben" },
        { "name": "Sub-Derm Kevlar", "sys_cost": 1, "effect": "DR +1" }
      ],
      "artifact": {
        "name": "Rift-Skorpion-Stachel",
        "tier": "Legendary",
        "effect": "+2 DMG Nahkampf, Doppelschlag 20%"
      },
      "reputation": {
        "iti": 2,
        "faction": "Chrono-Symmetriker",
        "factions": {
          "ordo_mnemonika": 1,
          "chrono_symmetriker": 2,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": -1
        }
      },
      "wallet": 1800
    },
    {
      "id": "CHR-0002",
      "name": "Yuki Tanaka",
      "callsign": "Phantom",
      "rank": "Operator I",
      "lvl": 11,
      "xp": 12,
      "origin": {
        "epoch": "2031",
        "hominin": "Homo sapiens sapiens",
        "role": "Ghost"
      },
      "attr": {
        "STR": 3,
        "GES": 9,
        "INT": 4,
        "CHA": 3,
        "TEMP": 3,
        "SYS": 3
      },
      "hp": 8,
      "hp_max": 10,
      "stress": 2,
      "has_psi": false,
      "sys_installed": 2,
      "talents": [
        { "name": "Schleichprofi II", "tag": "stealth", "bonus": 2 },
        { "name": "Schlösser III", "tag": "lockpick", "bonus": 3 }
      ],
      "equipment": [
        { "name": "Schalldämpfer-Pistole Mk II", "type": "weapon", "tier": 2 },
        { "name": "Stealth-Suit", "type": "armor", "tier": 2, "dr": 1 },
        { "name": "Dietrich-Set Pro", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Stealth-Skin", "sys_cost": 1, "effect": "+1 Schleichen" },
        { "name": "Reflexboost", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "reputation": {
        "iti": 2,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 2,
          "chrono_symmetriker": 1,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 1100
    },
    {
      "id": "CHR-0003",
      "name": "Elias Voss",
      "callsign": "Cipher",
      "rank": "Operator I",
      "lvl": 11,
      "xp": 12,
      "origin": {
        "epoch": "2045",
        "hominin": "Homo sapiens sapiens",
        "role": "Analyst"
      },
      "attr": {
        "STR": 3,
        "GES": 3,
        "INT": 9,
        "CHA": 3,
        "TEMP": 3,
        "SYS": 4
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 3,
      "talents": [
        { "name": "Techno-Mancer III", "tag": "tech", "bonus": 3 },
        { "name": "Hacking II", "tag": "hack", "bonus": 2 }
      ],
      "equipment": [
        { "name": "Hacking-Terminal Mk II", "type": "gadget", "tier": 2 },
        { "name": "Pistole", "type": "weapon", "tier": 1 },
        { "name": "Nano-Weave Anzug", "type": "armor", "tier": 2, "dr": 2 }
      ],
      "implants": [
        { "name": "Neuro-Link", "sys_cost": 1, "effect": "Kabellose Gerätesteuerung" },
        { "name": "Datenjack", "sys_cost": 1, "effect": "+1 Hacking" },
        { "name": "Kognitiv-Boost", "sys_cost": 1, "effect": "+1 INT-Proben" }
      ],
      "reputation": {
        "iti": 1,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 1,
          "chrono_symmetriker": 1,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 1000
    },
    {
      "id": "CHR-0004",
      "name": "Isabella Montoya",
      "callsign": "Silk",
      "rank": "Operator II",
      "lvl": 11,
      "xp": 12,
      "origin": {
        "epoch": "1962",
        "hominin": "Homo sapiens sapiens",
        "role": "Fixer"
      },
      "attr": {
        "STR": 3,
        "GES": 4,
        "INT": 3,
        "CHA": 9,
        "TEMP": 3,
        "SYS": 3
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 2,
      "talents": [
        { "name": "Menschenkenntnis III", "tag": "social", "bonus": 3 },
        { "name": "Diplomatisches Geschick II", "tag": "negotiation", "bonus": 2 }
      ],
      "equipment": [
        { "name": "Versteckte Derringer", "type": "weapon", "tier": 1 },
        { "name": "Eleganter Mantel (gepanzert)", "type": "armor", "tier": 2, "dr": 1 },
        { "name": "Bestechungsgeld 500 CU", "type": "gadget", "tier": 2 },
        { "name": "Orbital-Zugangskarte", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Pheromon-Drüse", "sys_cost": 1, "effect": "+1 CHA-Proben" },
        { "name": "Neuro-Translator", "sys_cost": 1, "effect": "Auto-Übersetzung" }
      ],
      "reputation": {
        "iti": 3,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 3,
          "chrono_symmetriker": 1,
          "kausalklingen": 1,
          "zerbrechliche_ewigkeit": -1
        }
      },
      "wallet": 2200
    },
    {
      "id": "CHR-0005",
      "name": "Kael Ashford",
      "callsign": "Drift",
      "rank": "Operator I",
      "lvl": 11,
      "xp": 12,
      "origin": {
        "epoch": "2200",
        "hominin": "Homo sapiens sapiens",
        "role": "Rifter"
      },
      "attr": {
        "STR": 3,
        "GES": 3,
        "INT": 3,
        "CHA": 3,
        "TEMP": 7,
        "SYS": 3
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": true,
      "psi_heat": 0,
      "pp": 7,
      "psi_abilities": [
        { "name": "Echostep", "cost": 1, "cooldown": 1, "effect": "Mini-Teleport 3m" },
        { "name": "Zeitsinn", "cost": 1, "cooldown": 0, "effect": "Anomalie-Warnung" },
        { "name": "Psi-Schild", "cost": 2, "cooldown": 2, "effect": "DR +2 für 1 Runde" }
      ],
      "sys_installed": 2,
      "talents": [
        { "name": "Psi-Fokus II", "tag": "psi", "bonus": 2 },
        { "name": "Temporal-Logiker", "tag": "temporal", "bonus": 1 }
      ],
      "equipment": [
        { "name": "Psi-Stab", "type": "weapon", "tier": 2 },
        { "name": "Leichte Rüstung", "type": "armor", "tier": 1, "dr": 1 },
        { "name": "Paradoxon-Scanner", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Psi-Amplifier", "sys_cost": 1, "effect": "+1 Psi-Proben" },
        { "name": "Chrono-Resonator", "sys_cost": 1, "effect": "Psi-Heat -1 nach Kampf" }
      ],
      "artifact": {
        "name": "Krakenherz-Fragment",
        "tier": "Legendary",
        "effect": "Bioscan 30m durch Wände"
      },
      "reputation": {
        "iti": 2,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 2,
          "chrono_symmetriker": 1,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": -1
        }
      },
      "wallet": 1400
    }
  ],
  "economy": {
    "hq_pool": 6700
  },
  "logs": {
    "trace": [
      { "event": "rift_complete", "seed_id": "RS-001", "result": "success" },
      { "event": "rift_complete", "seed_id": "RS-002", "result": "success" },
      { "event": "team_merge", "saves": ["Save-A-3er", "Save-B-2er"], "result": "success", "episode_transition": "EP1→EP2" }
    ],
    "market": [],
    "artifact_log": [
      { "id": "ART-001", "name": "Rift-Skorpion-Stachel", "found_at": "RS-001", "holder": "CHR-0001" },
      { "id": "ART-002", "name": "Krakenherz-Fragment", "found_at": "RS-002", "holder": "CHR-0005" }
    ],
    "notes": [
      { "agent": "CHR-0003", "text": "Pestlabor war Deckmantel für Chronowaffen-Forschung" },
      { "agent": "CHR-0004", "text": "Orbital-Datenleck führt zu Zerbrechlicher Ewigkeit" }
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": true
    }
  },
  "arc": {
    "factions": {
      "Kausalklingen": { "stance": "misstrauisch" },
      "Zerbrechliche Ewigkeit": { "stance": "feindlich" }
    },
    "questions": [
      "Wer finanziert die Chronowaffen-Forschung?",
      "Was will die Zerbrechliche Ewigkeit mit den Orbitaldaten?"
    ],
    "hooks": [
      "Cipher hat Daten über illegale Zeitexperimente gefunden",
      "Silk hat einen Kontakt bei den Kausalklingen",
      "Drift spürt eine Psi-Resonanz vom Orbital"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_third_person"
  }
}
```

---

## Merge-Notizen

**Kodex:** Merge abgeschlossen. 5 Charaktere registriert. Drei offene Punkte zur Klärung beim nächsten Sessionstart:

> **① Px-Stand:** Save A hatte Px 1, Save B Px 2. Gemergt auf **Px 2** (Maxwert). Alternativ könnte die Gruppe auf **Px 3** (Summe geteilt durch Gruppen-Merge-Bonus) hochgesetzt werden — Entscheidung liegt beim Tisch.
>
> **② Episode:** Beide Saves standen auf EP1/MS0. Da beide Rift-Ops abgeschlossen sind, wurde auf **EP2/MS0** hochgezählt. Wenn noch EP1-Missionen ausstehen, manuell zurücksetzen.
>
> **③ HQ-Pool:** 3500 + 3200 = **6700 CU** summiert. Falls die Teams getrennte Kassen führen wollen, bitte beim nächsten Session-Start ansagen.