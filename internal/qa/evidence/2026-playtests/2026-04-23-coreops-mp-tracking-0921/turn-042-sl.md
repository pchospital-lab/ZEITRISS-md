# Turn 42 — SL

## Klärungen + Level-Up + Save

---

### Jonas — Paradoxon-Index

Gute Nachricht: **Px 5 ist das Ziel, nicht das Problem.**

> Px steigt = gut. Bei Px 5 löst das ITI ein **ClusterCreate** aus — das System erkennt 1-2 instabile Zeitkoordinaten auf der Raumzeitkarte und markiert sie als **Rift-Ops**. Dort warten Paramonstern, Artefakte, besondere Beute.

Das ist ein Belohnungssystem. Die Crew *will* Px 5 erreichen. Kein SR-Astralüberlauf, keine Strafe — ein Jackpot-Moment.

`Kodex: Px 1/5. Nächster Anstieg: abhängig von TEMP-Durchschnitt und Missionsverlauf.`

---

### Kim — TEMP

**TEMP = Temporale Affinität.** Je höher, desto besser reagiert ein Agent auf Zeitphänomene, Psi-Kräfte und Zeitverwerfungen. Außerdem:
- Beeinflusst wie schnell Px steigt
- Bestimmt wie oft dein Epochenfahrzeug verfügbar ist
- Wird für Initiative mitgenutzt (max GES/TEMP)

Delacroix hat TEMP 1 — das bedeutet langsamer Px-Aufbau, seltenes Fahrzeug. Aber CHA 6 und GES 5 machen das mehr als wett.

---

### Voss — Tatortanalyse Fortgeschritten

`Kodex: Tatortanalyse Basis → Fortgeschritten. +3 auf INT-Proben Spurenanalyse. Reroll 1×/Mission verfügbar.`

**Level-Up abgeschlossen.**

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP1-MS2-HQ-POST",
  "parent_save_id": "SAVE-2026-EP1-MS1-HQ-POST",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 2,
    "px": 1,
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
      "lvl": 3,
      "xp": 0,
      "origin": { "epoch": "unbekannt", "hominin": "Homo sapiens sapiens", "role": "Analystin" },
      "attr": { "STR": 3, "GES": 6, "INT": 6, "CHA": 3, "TEMP": 4, "SYS": 2 },
      "hp": 13,
      "hp_max": 13,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Tatortanalyse",
          "tier": "Fortgeschritten",
          "effect": "+3 auf INT-Proben Spurenanalyse & Beweissicherung; Reroll 1×/Mission"
        }
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
        "background": "Feldagentin, Spezialisierung Spurenanalyse und Tatortlesung.",
        "milestones": [
          "EP1-MS1: Tempocom-Bauteil gesichert, Washington D.C. 1962.",
          "EP1-MS2: Vadim verhört, Georgetown. Auge-über-Anker-Symbol identifiziert. Bauteil = Kopie bestätigt."
        ]
      },
      "carry": [
        { "name": "Kompaktpistole Brixon-4", "type": "weapon", "tier": 1 },
        { "name": "Verstärktes Einsatzjackett", "type": "armor", "tier": 1 },
        { "name": "Handscanner Kodex-Link", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 0 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 0 },
        { "name": "Streichholzheftchen Auge-über-Anker", "type": "gadget", "tier": 0 }
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
        "availability": { "ready_every_missions": 3, "next_ready_in": 1 },
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
      "wallet": 550
    },
    {
      "id": "CHR-KASPAR-01",
      "name": "Ren Kaspar",
      "callsign": "RAMPART",
      "rank": "Feldagent",
      "lvl": 2,
      "xp": 1,
      "origin": { "epoch": "unbekannt", "hominin": "Homo sapiens sapiens", "role": "Sicherheitsoffizier" },
      "attr": { "STR": 6, "GES": 4, "INT": 3, "CHA": 2, "TEMP": 4, "SYS": 2 },
      "hp": 16,
      "hp_max": 16,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Nahkampf-Taktik",
          "tier": "Basis",
          "effect": "+2 STR Nahkampf; routinemäßige Entwaffnung ohne Probe gegen ungepanzerte Gegner"
        }
      ],
      "equipment": [
        { "name": "Stun-Schlagstock verstärkt", "type": "weapon", "tier": 1 },
        { "name": "Dienstpistole P-7", "type": "weapon", "tier": 1 },
        { "name": "Taktikweste", "type": "armor", "tier": 1 },
        { "name": "Verstärkter Kampfhandschuh", "type": "weapon", "tier": 1 },
        { "name": "Handfessel-Kit", "type": "gadget", "tier": 0 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 },
        { "name": "Erste-Hilfe-Injektor", "type": "consumable", "tier": 0 }
      ],
      "implants": [],
      "history": {
        "background": "Ehemaliger Sicherheitsoffizier, ITI-Außenagent.",
        "milestones": [
          "EP1-MS1: Georgetown-Adresse durch Kurier-Befragung gesichert.",
          "EP1-MS2: Vadim eingekesselt, verhört. Versprechen gegeben — Vadim und unbekannte Frau bleiben aus Bericht."
        ]
      },
      "carry": [
        { "name": "Stun-Schlagstock verstärkt", "type": "weapon", "tier": 1 },
        { "name": "Dienstpistole P-7", "type": "weapon", "tier": 1 },
        { "name": "Taktikweste", "type": "armor", "tier": 1 },
        { "name": "Verstärkter Kampfhandschuh", "type": "weapon", "tier": 1 },
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
        "availability": { "ready_every_missions": 3, "next_ready_in": 1 },
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
      "wallet": 310
    },
    {
      "id": "CHR-DELACROIX-01",
      "name": "Ines Delacroix",
      "callsign": "MOTH",
      "rank": "Feldagentin",
      "lvl": 2,
      "xp": 1,
      "origin": { "epoch": "unbekannt", "hominin": "Homo sapiens sapiens", "role": "Infiltratorin" },
      "attr": { "STR": 2, "GES": 5, "INT": 5, "CHA": 6, "TEMP": 1, "SYS": 2 },
      "hp": 12,
      "hp_max": 12,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 1,
      "talents": [
        {
          "name": "Verdeckte Identität",
          "tier": "Basis",
          "effect": "+2 CHA Täuschung/Rollenspiel; Alias-Aufbau ohne Probe in kontrollierten Umgebungen"
        }
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
        "background": "Verhandlungsführerin und Infiltratorin.",
        "milestones": [
          "EP1-MS1: Tempocom-Bauteil durch Tischablenkung gesichert. Tarnung kompromittiert.",
          "EP1-MS2: Großen (Vadim) am Fenster gestoppt, Verhör ermöglicht."
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
        "availability": { "ready_every_missions": 4, "next_ready_in": 3 },
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
      "wallet": 365
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [
      "EP1-MS1: Tempocom-Bauteil gesichert, Washington D.C. 14.10.1962.",
      "EP1-MS1: Georgetown-Adresse Volta Street 2800er Block gesichert.",
      "EP1-MS1: Verfolger-Aussage: 'Leute die nicht vergessen'.",
      "EP1-MS1: Größerer hat visuelle ID auf MOTH, möglicherweise SPLINTER/RAMPART.",
      "EP1-MS2: Haus Georgetown infiltriert. Notizbuch + Karte gescannt.",
      "EP1-MS2: ITI-Standort auf Gegenseiten-Karte markiert — kompromittiert.",
      "EP1-MS2: Vadim verhört. Name: Vadim, Nachname unbekannt.",
      "EP1-MS2: Bauteil = Kopie. Original unbekannt.",
      "EP1-MS2: Dritte Partei: Auge über Anker. Zwei Jahre aktiv, kein Gesicht.",
      "EP1-MS2: Union Station Schließfach 114 — Kontaktpunkt dritte Partei.",
      "EP1-MS2: Versprechen an Vadim: er und unbekannte Frau bleiben aus Bericht."
    ],
    "market": [
      "EP1-MS1: Kaspar — Verstärkter Kampfhandschuh Tier 1, 80 CU.",
      "EP1-MS1: Delacroix — Adrenalin-Regulator Tier 1, 85 CU."
    ],
    "artifact_log": [],
    "notes": [
      "Streichholzheftchen Auge-über-Anker bei SPLINTER.",
      "Notizbuch-Scan (14 Seiten kyrillisch) im Handscanner — Upload ausstehend.",
      "Union Station Schließfach 114 — ITI-Archivar prüft.",
      "Vadim — Standort bekannt, läuft vorerst frei.",
      "Finch passiver Marker aktiv."
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
    "summary_active_arcs": "EP1: Bauteil = Kopie, Original unbekannt. Dritte Partei 'Auge über Anker' seit 2 Jahren aktiv. Union Station Schließfach 114 als Kontaktpunkt. ITI-Standort auf Gegenseiten-Karte. Vadim läuft frei, Versprechen aktiv."
  },
  "continuity": {
    "last_seen": { "mode": "core", "episode": 1, "mission": 2, "location": "HQ" },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      "EP1-MS1: Verfolger — osteuropäisch, professionell, Organisations-Botschafter.",
      "EP1-MS1: Kleinerer — Empfänger, nervös, südstaatlicher Akzent.",
      "EP1-MS1: Kurier — jung, Motorrad, U Street Diner.",
      "EP1-MS2: Vadim — Koordinator, Instrument der dritten Partei, Georgetown. Versprechen aktiv.",
      "EP1-MS2: Unbekannte Frau — Vadims Kontakt, nicht Teil der Operation, sauber laut Archivarin."
    ],
    "shared_echoes": [
      "Tempocom-Bauteil: Kopie. Original unbekannt.",
      "Auge über Anker: Symbol dritte Partei, zwei Jahre aktiv.",
      "Union Station Schließfach 114: Kontaktpunkt.",
      "ITI-Standort kompromittiert — auf Gegenseiten-Karte markiert.",
      "Versprechen an Vadim: er und Frau bleiben aus Bericht."
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
      },
      {
        "id": "NPC-VADIM-01",
        "name": "Vadim",
        "callsign": null,
        "role": "Koordinator, Instrument der dritten Partei",
        "scope": "EP1",
        "status": "active_free",
        "notes": "Versprechen aktiv. Läuft frei. Weiß ZEITRISS-Namen."
      }
    ],
    "active_npc_ids": ["NPC-MIRA-01", "NPC-OSEI-01", "NPC-VADIM-01"]
  },
  "arc": {
    "factions": {
      "auge_ueber_anker": {
        "name": "Auge über Anker",
        "status": "aktiv, feindlich, unbekannte Führung",
        "known": "Symbol, zwei Jahre aktiv, tote Briefkästen, Union Station Schließfach 114, Bauteil-Herkunft unbekannt"
      },
      "vadims_organisation": {
        "name": "Vadims Organisation (Leute die nicht vergessen)",
        "status": "operativ, feindlich, Instrument der dritten Partei",
        "known": "Osteuropäische Verbindung, Georgetown-Basis, Vadim als Koordinator"
      }
    },
    "questions": [
      "Wo ist das Original-Bauteil?",
      "Wer oder was ist Auge über Anker?",
      "Was steht im Notizbuch (kyrillisch)?",
      "Was ist in Union Station Schließfach 114?",
      "Woher stammt das Bauteil — welche Epoche?"
    ],
    "hooks": [
      "Union Station Schließfach 114 — ITI-Archivar prüft",
      "Notizbuch-Upload ausstehend — Übersetzung nötig",
      "Vadim läuft frei — könnte wieder auftauchen",
      "ITI-Standort kompromittiert — Konsequenzen?"
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

`Kodex: Deepsave abgeschlossen. SAVE-2026-EP1-MS2-HQ-POST.`
`Kodex: Neuen Chat für Mission 3 empfohlen.`

---

**HQ-Menü:**

1. **Erkunden** — Zero Time Lounge, Klinik, Quartiermeisterei, Kodex-Archiv
2. **Schnell-HQ** — direkt zu Mission 3 Briefing
3. **Freie Aktion** — eigener Wunsch
4. **Neuer Chat** — Save kopieren, frischen Start für Mission 3
