# Turn 26 — SL

## Kurze Antworten + Save

---

### Kim — Stress-Max 14

Genau richtig gerechnet:

> Stress-Max = 8 + CHA (6) = **14** + Adrenalin-Regulator (+2, bereits eingerechnet beim Kauf) = **14**

Warte — kurze Korrektur. Der Adrenalin-Regulator gibt +2 auf Stress-Max, das steht im Item. Ich hatte das bereits beim Kauf eingerechnet (daher 13 vor Level-Up). Nach CHA 5→6:

> 8 + CHA 6 = 14, Adrenalin-Regulator +2 = **16**

`Kodex: Delacroix — Stress-Maximum korrigiert: 14 → 16. Adrenalin-Regulator +2 addiert.`

Entschuldigung für den Fehler im Bogen oben — Delacroix hat **Stress 0/16**.

---

### Jonas — Quartiermeisterei

Kurzer Abstecher, fünf Minuten. Osei zeigt Kaspar was verfügbar ist:

| Item | Tier | Preis | Effekt |
|---|---|---|---|
| Verstärkter Kampfhandschuh | 1 | 80 CU | +1 LP im Nahkampf, kein Waffen-Slot |
| Knieschützer taktisch | 1 | 60 CU | DR +1 gegen Beinschüsse/Tritte |
| Erste-Hilfe-Injektor | 0 | 30 CU | +3 HP, Einmalnutzung |
| Signalstörer-Patch | 1 | 60 CU | +1 Schleichen vs. Elektronik, 1× |

190 CU — Kaspar kann sich eines leisten und hätte noch Reserve. **Jonas, kaufst du etwas?**

---

### !save

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP1-MS1-HQ-POST",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 1,
    "px": 0,
    "px_state": "stable",
    "mode": "core",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-VOSS-01",
      "name": "Mara Voss",
      "callsign": "SPLINTER",
      "rank": "Feldagentin",
      "lvl": 2,
      "xp": 1,
      "origin": { "epoch": "unbekannt", "hominin": "Homo sapiens sapiens", "role": "Analystin" },
      "attr": { "STR": 3, "GES": 6, "INT": 6, "CHA": 3, "TEMP": 4, "SYS": 2 },
      "hp": 13,
      "hp_max": 13,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        { "name": "Tatortanalyse", "tier": "Basis", "effect": "+2 INT Spurenanalyse; triviale Tatortlesungen ohne Probe" }
      ],
      "equipment": [
        { "name": "Kompaktpistole Brixon-4", "type": "weapon", "tier": 1 },
        { "name": "Verstärktes Einsatzjackett", "type": "armor", "tier": 1 },
        { "name": "Handscanner Kodex-Link", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 0 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 0 }
      ],
      "implants": [],
      "history": {
        "background": "Feldagentin, eine Mission absolviert. Spezialisierung Spurenanalyse.",
        "milestones": [
          "EP1-MS1: Tempocom-Bauteil gesichert, Washington D.C. 1962. Größerer hat Gesicht von SPLINTER gesehen."
        ]
      },
      "carry": [
        { "name": "Kompaktpistole Brixon-4", "type": "weapon", "tier": 1 },
        { "name": "Verstärktes Einsatzjackett", "type": "armor", "tier": 1 },
        { "name": "Handscanner Kodex-Link", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 0 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 0 }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-VOSS-01",
          "name": "ITI-Standardtransport",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": { "ready_every_missions": 3, "next_ready_in": 2 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 330
    },
    {
      "id": "CHR-KASPAR-01",
      "name": "Ren Kaspar",
      "callsign": "RAMPART",
      "rank": "Feldagent",
      "lvl": 2,
      "xp": 0,
      "origin": { "epoch": "unbekannt", "hominin": "Homo sapiens sapiens", "role": "Sicherheitsoffizier" },
      "attr": { "STR": 6, "GES": 4, "INT": 3, "CHA": 2, "TEMP": 4, "SYS": 2 },
      "hp": 16,
      "hp_max": 16,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        { "name": "Nahkampf-Taktik", "tier": "Basis", "effect": "+2 STR Nahkampf; routinemäßige Entwaffnung ohne Probe gegen ungepanzerte Gegner" }
      ],
      "equipment": [
        { "name": "Stun-Schlagstock verstärkt", "type": "weapon", "tier": 1 },
        { "name": "Dienstpistole P-7", "type": "weapon", "tier": 1 },
        { "name": "Taktikweste", "type": "armor", "tier": 1 },
        { "name": "Handfessel-Kit", "type": "gadget", "tier": 0 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 }
      ],
      "implants": [],
      "history": {
        "background": "Ehemaliger Sicherheitsoffizier, jetzt ITI-Außenagent. Erster Einsatz abgeschlossen.",
        "milestones": [
          "EP1-MS1: Verfolger in Seitengasse konfrontiert. Georgetown-Adresse durch Kurier-Befragung gesichert."
        ]
      },
      "carry": [
        { "name": "Stun-Schlagstock verstärkt", "type": "weapon", "tier": 1 },
        { "name": "Dienstpistole P-7", "type": "weapon", "tier": 1 },
        { "name": "Taktikweste", "type": "armor", "tier": 1 },
        { "name": "Handfessel-Kit", "type": "gadget", "tier": 0 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-KASPAR-01",
          "name": "ITI-Standardtransport",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": { "ready_every_missions": 3, "next_ready_in": 2 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 190
    },
    {
      "id": "CHR-DELACROIX-01",
      "name": "Ines Delacroix",
      "callsign": "MOTH",
      "rank": "Feldagentin",
      "lvl": 2,
      "xp": 0,
      "origin": { "epoch": "unbekannt", "hominin": "Homo sapiens sapiens", "role": "Infiltratorin" },
      "attr": { "STR": 2, "GES": 5, "INT": 5, "CHA": 6, "TEMP": 1, "SYS": 2 },
      "hp": 12,
      "hp_max": 12,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 1,
      "talents": [
        { "name": "Verdeckte Identität", "tier": "Basis", "effect": "+2 CHA Täuschung/Rollenspiel; Alias-Aufbau ohne Probe in kontrollierten Umgebungen" }
      ],
      "equipment": [
        { "name": "Kompaktpistole mit Schalldämpfer", "type": "weapon", "tier": 1 },
        { "name": "Verstärkte Zivilkleidung", "type": "armor", "tier": 1 },
        { "name": "Falscher Ausweis-Kit", "type": "gadget", "tier": 1 },
        { "name": "Falscher Ausweis-Kit", "type": "gadget", "tier": 1 },
        { "name": "Falscher Ausweis-Kit", "type": "gadget", "tier": 1 },
        { "name": "Micro-Jammer", "type": "gadget", "tier": 1 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 }
      ],
      "implants": [
        { "name": "Adrenalin-Regulator", "tier": 1, "slot_cost": 1, "effect": "Stress-Max +2" }
      ],
      "history": {
        "background": "Verhandlungsführerin und Infiltratorin. Erster Einsatz abgeschlossen.",
        "milestones": [
          "EP1-MS1: Tempocom-Bauteil durch Tischablenkung gesichert, The Argyle Bar D.C. 1962. Größerer hat Gesicht von MOTH gesehen. Tarnung kompromittiert."
        ]
      },
      "carry": [
        { "name": "Kompaktpistole mit Schalldämpfer", "type": "weapon", "tier": 1 },
        { "name": "Verstärkte Zivilkleidung", "type": "armor", "tier": 1 },
        { "name": "Falscher Ausweis-Kit", "type": "gadget", "tier": 1 },
        { "name": "Falscher Ausweis-Kit", "type": "gadget", "tier": 1 },
        { "name": "Falscher Ausweis-Kit", "type": "gadget", "tier": 1 },
        { "name": "Micro-Jammer", "type": "gadget", "tier": 1 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-DELACROIX-01",
          "name": "ITI-Standardtransport",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": { "ready_every_missions": 3, "next_ready_in": 2 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 165
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [
      "EP1-MS1: Tempocom-Bauteil gesichert, Washington D.C. 14.10.1962.",
      "EP1-MS1: Georgetown-Adresse Volta Street 2800er Block gesichert.",
      "EP1-MS1: Verfolger-Aussage: 'Leute die nicht vergessen' — Organisations-Idiom.",
      "EP1-MS1: Größerer hat visuelle ID auf MOTH, möglicherweise SPLINTER und RAMPART.",
      "EP1-MS1: Auftraggeber-Profil: männlich, Mitte 40, grauer Anzug, nördlicher Akzent, Brille."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Volta Street Georgetown — Briefkasten überwacht durch ITI.",
      "Finch passiver Marker gesetzt — historisch unberührt.",
      "Bauteil in ITI-Labor zur Analyse."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": "EP1: Tempocom-Bauteil gesichert. Fraktion 'Leute die nicht vergessen' aktiv. Georgetown-Verbindung offen. Bauteil-Analyse ausstehend."
  },
  "continuity": {
    "last_seen": { "mode": "core", "episode": 1, "mission": 1, "location": "HQ" },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      "EP1-MS1: Verfolger — osteuropäischer Akzent, professionell, Organisations-Botschafter.",
      "EP1-MS1: Größerer — Koordinator, Volta Street Verbindung, hat Gesichter gesehen.",
      "EP1-MS1: Kleinerer — Empfänger, nervös, südstaatlicher Akzent.",
      "EP1-MS1: Kurier — jung, Lederjacke, Motorrad, angeheuert U Street Diner."
    ],
    "shared_echoes": [
      "Tempocom-Bauteil: Signalverstärker mit Zeitstempel-Modul, nicht aus 1962.",
      "Organisations-Idiom: 'Leute die nicht vergessen'.",
      "Georgetown Volta Street 2800er Block — grüner Briefkasten."
    ],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-MIRA-01",
        "name": "Archivarin Mira",
        "callsign": null,
        "role": "ITI Operations, Briefing/Debrief",
        "scope": "HQ",
        "status": "active"
      },
      {
        "id": "NPC-OSEI-01",
        "name": "Osei, T.",
        "callsign": null,
        "role": "Duty-Desk ITI",
        "scope": "HQ",
        "status": "active"
      },
      {
        "id": "NPC-FINCH-01",
        "name": "Harold Finch",
        "callsign": null,
        "role": "Pentagon-Techniker, historisch geschützt",
        "scope": "EP1",
        "status": "passive_marker"
      }
    ],
    "active_npc_ids": ["NPC-MIRA-01", "NPC-OSEI-01"]
  },
  "arc": {
    "factions": {
      "leute_die_nicht_vergessen": {
        "name": "Leute die nicht vergessen",
        "status": "aktiv, feindlich",
        "known": "Organisations-Idiom, Georgetown-Verbindung, koordinierte Feldstruktur"
      }
    },
    "questions": [
      "Woher stammt das Tempocom-Bauteil?",
      "Wer ist der Auftraggeber (Mitte 40, grauer Anzug, Brille)?",
      "Was sollte das Bauteil dokumentieren — und für wen?",
      "Was passiert an der Volta Street?"
    ],
    "hooks": [
      "Bauteil-Analyse ITI-Labor — Ergebnis ausstehend",
      "Volta Street Georgetown — überwacht, ungeprüft",
      "Finch passiver Marker — falls sich etwas bewegt"
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

`Kodex: Deepsave abgeschlossen. SAVE-2026-EP1-MS1-HQ-POST.`
`Kodex: Neuen Chat für Mission 2 empfohlen.`

---

**Jonas — Quartiermeisterei noch offen.** Kaufst du etwas vor Mission 2? Dann Briefing.
