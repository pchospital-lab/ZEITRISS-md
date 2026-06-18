# Turn 30 — SL

Kurze Korrektur — die Reihenfolge stimmt noch nicht ganz [1][2]:

`Kodex: Save ausstehend. JSON-Export zuerst, dann Briefing.`

---

Der Save-Block kommt jetzt. Kopiere ihn, dann empfehle ich einen neuen Chat für Mission 2 — sauberer Missionsbetrieb [1].

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-MS1-DEBRIEF-SPLINTER",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 1,
    "px": 0,
    "px_state": "stable",
    "mode": "mixed",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-SPLINTER-01",
      "name": "Mara Voss",
      "callsign": "SPLINTER",
      "rank": "Rekrut",
      "lvl": 1,
      "xp": 1,
      "origin": {
        "epoch": "2031",
        "hominin": "Homo sapiens sapiens",
        "role": "Forensik-Spezialistin"
      },
      "attr": {
        "STR": 1,
        "GES": 6,
        "INT": 5,
        "CHA": 2,
        "TEMP": 4,
        "SYS": 1
      },
      "hp": 12,
      "hp_max": 12,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Tatortanalyse",
          "tier": "Basis",
          "effect": "+2 auf INT-Proben zur Spurensicherung und Beweisanalyse. Triviale Tatortlesungen: Auto-Erfolg."
        }
      ],
      "equipment": [
        { "name": "Dienstpistole", "type": "weapon", "tier": 1 },
        { "name": "Walther PPK", "type": "weapon", "tier": 1 },
        { "name": "Kevlarweste", "type": "armor", "tier": 1 },
        { "name": "Handscanner", "type": "gadget", "tier": 1 },
        { "name": "Multitool", "type": "gadget", "tier": 1 },
        { "name": "Comlink", "type": "gadget", "tier": 1 }
      ],
      "implants": [],
      "history": {
        "background": "Forensik-Spezialistin, rekrutiert nach einem Rift-Kontakt-Vorfall 2031.",
        "milestones": [
          "MS1 Wien 1938 — Mikrofilm und Identitätsdokumente für 7 Widerstandskontakte gesichert. LINDEN stabilisiert. Kaul (Chrono-Symmetriker) gedeckt. Lorian-Flag aktiv."
        ]
      },
      "carry": [
        { "name": "Walther PPK", "type": "weapon", "tier": 1 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1, "count": 1 }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-SPLINTER-01",
          "name": "Epochenfahrzeug — ausstehend",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 3,
          "next_ready_in": 2
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 1,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 480
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [
      "MS1 Wien 12.03.1938 — Übergabe vollständig. Kaul-Kontakt. Lorian-Flag gesetzt."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Kaul (Symmetriker) hat Lorian-Auftrag intern suspendiert — meldet Vernichtung. Einmaliger Riss oder Muster?",
      "Lorian hat Anfrage über SPLINTER ins Archiv gestellt. Mira hat nicht weitergeleitet — noch nicht.",
      "LINDEN: stabil bei Brenner, Wien. ITI-Bergungsteam ETA 6h nach Sprung."
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
    "summary_active_arcs": "Lorian (Chrono-Symmetriker) hat Akte über SPLINTER eröffnet. Kaul als Kontakt offen. Sieben Widerstandskontakte Wien 1938 gerettet — Zeitlinie stabil."
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
    "shared_echoes": [],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-LINDEN-01",
        "name": "LINDEN",
        "callsign": "LINDEN",
        "role": "ITI-Voragent",
        "scope": "episode",
        "status": "stabil, Wien 1938, bei Brenner"
      },
      {
        "id": "NPC-KAUL-01",
        "name": "Kaul",
        "callsign": "Kaul",
        "role": "Chrono-Symmetriker, Feldagent",
        "scope": "arc",
        "status": "aktiv, Lorian-Auftrag suspendiert, Bericht gefälscht"
      },
      {
        "id": "NPC-BRENNER-01",
        "name": "Brenner",
        "callsign": "Brenner",
        "role": "Buchhändler, Widerstandskontakt",
        "scope": "episode",
        "status": "aktiv, Wien 1938, deckt LINDEN"
      }
    ],
    "active_npc_ids": ["NPC-KAUL-01"]
  },
  "arc": {
    "factions": {
      "chrono_symmetriker": "Lorian hat Akte SPLINTER eröffnet. Kaul: interner Riss sichtbar."
    },
    "questions": [
      "Was macht Lorian mit der Akte über SPLINTER?",
      "Ist Kauls Loyalitätsriss einmalig oder Muster?",
      "Was war im zweiten Fach des Kästchens ursprünglich — und wer hatte es vor LINDEN?"
    ],
    "hooks": [
      "Pater Lorian — Symmetriker, Präzedenzfall Wien 1935, sieben Tote",
      "Kaul — möglicher stiller Verbündeter, unzuverlässig",
      "Archivarin Mira — hält Lorians Anfrage zurück"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  },
  "level_history": {
    "1": {
      "choice": "+1 Attribut",
      "detail": "GES 5→6",
      "mission": "MS1"
    }
  }
}
```

---

`Kodex: Save vollständig. Wallet 480 CU, GES 6, ITI-Ruf 1, XP 1/10 persistiert.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.` [1]

---

**Nächster Schritt:**

JSON kopieren → neuen Chat öffnen → Save einfügen → Mission 2 läuft sauber an.
