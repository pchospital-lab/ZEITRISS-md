# Merge Request

Gruppenspiel fortsetzen. Alle drei Chars kommen zurück ins HQ und möchten zusammen spielen. Hier die drei individuellen Saves:

**[Sarah — Mara Voss/SPLINTER]:**
```json
{
  "v": 7,
  "save_id": "solo-splinter-runD",
  "session_type": "solo",
  "characters": [
    {
      "name": "Mara Voss",
      "callsign": "SPLINTER",
      "player": "Sarah",
      "level": 1,
      "xp": 9,
      "attributes": {
        "GES": 5,
        "INT": 5,
        "TEMP": 4,
        "SOC": 3,
        "STR": 3,
        "WIS": 3
      },
      "lp": 11,
      "lp_max": 12,
      "stress": 3,
      "pp": 0,
      "pp_max": 0,
      "sys": 0,
      "sys_max": 14,
      "talents": [
        "Tatortanalyse"
      ],
      "equipment": [
        {
          "name": "Dienstpistole",
          "type": "weapon",
          "tier": 1
        },
        {
          "name": "Kevlarweste",
          "type": "armor",
          "tier": 1
        },
        {
          "name": "Handscanner",
          "type": "tool",
          "tier": 1
        },
        {
          "name": "Multitool",
          "type": "tool",
          "tier": 1
        },
        {
          "name": "2x Rauchgranate",
          "type": "gadget",
          "tier": 1
        }
      ],
      "currency": {
        "cu": 120
      },
      "level_history": {},
      "missions_completed": 1,
      "px": 1,
      "deepsave": true
    }
  ],
  "squad": {
    "name": "Mara Voss",
    "tier": 1,
    "wallet": {
      "cu": 120
    },
    "reputation": {
      "ITI": 2,
      "Tempocom": 0,
      "Arcana": 0
    }
  },
  "continuity": {
    "shared_echoes": [
      "Mission 1: Lagerhaus gesichert"
    ],
    "npc_roster": [
      {
        "name": "Dr. Veith",
        "role": "Kontakt",
        "status": "aktiv"
      }
    ]
  },
  "session_meta": {
    "chat_id": "solo-splinter",
    "scene_count": 0,
    "phase": "HQ"
  }
}
```

**[Jonas — Ren Kaspar/RAMPART]:**
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-RAMPART-HQ-A",
  "parent_save_id": "solo-rampart-runD",
  "merge_id": null,
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
      "id": "CHR-RAMPART-01",
      "name": "Ren Kaspar",
      "callsign": "RAMPART",
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
      "hp": 10,
      "hp_max": 13,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Nahkampf-Taktik",
          "tier": "Basis",
          "bonus": "+2 auf Nahkampf-Proben (STR)"
        }
      ],
      "equipment": [
        {
          "name": "Kampfmesser",
          "type": "weapon",
          "tier": 1
        },
        {
          "name": "Schwere Rüstung",
          "type": "armor",
          "tier": 1
        },
        {
          "name": "Comlink",
          "type": "gadget",
          "tier": 1
        }
      ],
      "implants": [],
      "history": {
        "background": "",
        "milestones": [
          "Mission 1: Lagerhaus gesichert"
        ]
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
    }
  ],
  "economy": {
    "hq_pool": 0
  },
  "logs": {
    "trace": [],
    "market": [
      "HQ-Ausrüstungskammer besucht. Kein Kauf — Budget unzureichend für Tier-2-Upgrade."
    ],
    "artifact_log": [],
    "notes": [
      "SYS-Migrationslücke aus Legacy-Save: sys_max 14 nicht übernommen. SYS als Attribut auf 0 gesetzt."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [
        "solo-rampart-runD"
      ],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": ""
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 1,
      "location": "HQ-Ausrüstungskammer"
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
      "Mission 1: Lagerhaus gesichert"
    ],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-VEITH-01",
        "name": "Dr. Veith",
        "callsign": null,
        "role": "Kontakt",
        "scope": "core",
        "status": "aktiv"
      }
    ],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": []
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

**[Kim — Ines Delacroix/MOTH]:**
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-MOTH-runD-HQ-001",
  "parent_save_id": "solo-moth-runD",
  "merge_id": null,
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
      "id": "CHR-MOTH-001",
      "name": "Ines Delacroix",
      "callsign": "MOTH",
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
      "hp": 9,
      "hp_max": 10,
      "stress": 1,
      "has_psi": true,
      "pp": 3,
      "pp_max": 5,
      "psi_heat": 1,
      "psi_abilities": [
        "Telepathie",
        "Präkognition"
      ],
      "sys_installed": 2,
      "talents": [
        "Telepathie",
        "Präkognition"
      ],
      "equipment": [
        {
          "name": "Comlink",
          "type": "tool",
          "tier": 1
        },
        {
          "name": "Neuralnet-Kontaktlinsen",
          "type": "tool",
          "tier": 2
        },
        {
          "name": "Multitool",
          "type": "tool",
          "tier": 1
        }
      ],
      "implants": [],
      "history": {
        "background": "",
        "milestones": [
          "Mission 1: Lagerhaus gesichert"
        ]
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-MOTH-001",
          "name": "",
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
  "economy": {
    "hq_pool": 0
  },
  "logs": {
    "trace": [],
    "market": [],
    "artifact_log": [],
    "notes": [],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [
        "solo-moth-runD"
      ],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": ""
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
      "Mission 1: Lagerhaus gesichert"
    ],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-VEITH-001",
        "name": "Dr. Veith",
        "callsign": "",
        "role": "Kontakt",
        "scope": "recurring",
        "status": "aktiv"
      }
    ],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": [
      "Dr. Veith hat eine Nachricht hinterlassen"
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

Bitte merge alle drei Saves und starte eine gemeinsame Szene wo das Team sich im HQ wiederfindet.
