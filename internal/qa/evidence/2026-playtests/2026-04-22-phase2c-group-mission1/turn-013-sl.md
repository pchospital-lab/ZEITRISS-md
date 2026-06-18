# Turn 13 — SL

`EP 01 · MS 00 · SC 03/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/10 · Px 0/5 · Stress 0/10`

---

## Kurze Antworten zuerst

**Kim — Deepsave:** Du musst nichts anklicken. Du kopierst den JSON-Block den ich gleich ausgebe, und wenn du das nächste Mal weiterspielst, fügst du ihn einfach in den Chat ein. Das ist dein Spielstand [5]. Kein Knopf, kein System — nur Text der deine Figur enthält.

**Jonas — Kodex-Archiv:** HQ-Erkunden ist eine eigene Szene, aber eine kurze. Wenn du nach dem Save ins Archiv willst, sagst du einfach "Erkunden" und wir spielen es durch. Kein Zeitdruck, kein Aufwand [1].

**Sarah — Briefing:** Kommt nach dem Save. Ich halte die Reihenfolge ein: erst speichern, dann Briefing [7].

---

## `!save` — Drei Charakterbögen

Alle drei Saves folgen. Jede/r kopiert den eigenen Block.

---

### SAVE — RASK (Jonas)

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP01-MS00-RASK-CHARGEN",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 0,
    "px": 0,
    "px_state": "stable",
    "mode": "mixed",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-RASK-01",
      "name": "Rask",
      "callsign": "RASK",
      "rank": "Rekrut",
      "lvl": 1,
      "xp": 0,
      "origin": { "epoch": "Nah-Zukunft (2040er)", "hominin": "Homo sapiens sapiens", "role": "Enforcer" },
      "attr": { "STR": 6, "GES": 4, "INT": 2, "CHA": 2, "TEMP": 2, "SYS": 2 },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        { "name": "Waffenloser Kampf", "tier": "Basis", "effect": "+2 auf STR-Proben bei Faustkampf/Ringen" }
      ],
      "equipment": [
        { "name": "Schlagring", "type": "weapon", "tier": 1 },
        { "name": "Taktisches Messer", "type": "weapon", "tier": 1 },
        { "name": "Leichte Kampfweste", "type": "armor", "tier": 1 },
        { "name": "Comlink", "type": "gadget", "tier": 1 },
        { "name": "Verbandskit", "type": "consumable", "tier": 0 },
        { "name": "Verbandskit", "type": "consumable", "tier": 0 }
      ],
      "implants": [],
      "history": {
        "background": "Sicherheitskontraktor, 2041. Arbeitete für Konzerne die keine Fragen stellten. Das ITI rekrutierte ihn nach einem Einsatz der offiziell nie stattfand.",
        "milestones": []
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": { "id": "VEH-RASK-01", "name": "Kontrakt-Kurier (2040er)", "type": "vehicle", "tier": 1, "upgrades": [] },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 0,
        "faction": "Ordo Mnemonika",
        "factions": { "ordo_mnemonika": 0, "chrono_symmetriker": 0, "kausalklingen": 0, "zerbrechliche_ewigkeit": 0 }
      },
      "wallet": 100
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [],
    "market": [],
    "artifact_log": [],
    "notes": ["Nullzeit-Einweisung abgeschlossen. Archivarin Mira. Vier externe Fraktionen erwähnt."],
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
    "summary_active_arcs": "Ep01 gestartet. Rekrutierung abgeschlossen. Briefing steht aus."
  },
  "continuity": {
    "last_seen": { "mode": "core", "episode": 1, "mission": 0, "location": "HQ-Quartiere" },
    "split": { "family_id": null, "thread_id": null, "expected_threads": [], "resolved_threads": [], "convergence_ready": false },
    "roster_echoes": [],
    "shared_echoes": [],
    "convergence_tags": [],
    "npc_roster": [
      { "id": "NPC-MIRA-01", "name": "Mira", "callsign": "Archivarin", "role": "ITI-Kernpersonal", "scope": "HQ", "status": "aktiv" }
    ],
    "active_npc_ids": []
  },
  "arc": { "factions": { "ordo_mnemonika": "unbekannt", "chrono_symmetriker": "unbekannt", "kausalklingen": "unbekannt", "zerbrechliche_ewigkeit": "unbekannt" }, "questions": ["Was stand in den bereinigten Akten?", "Welche Fraktionen lesen Rekrutierungsmuster?"], "hooks": [] },
  "ui": { "gm_style": "verbose", "suggest_mode": false, "contrast": "standard", "badge_density": "standard", "output_pace": "normal", "voice_profile": "gm_second_person" }
}
```

---

### SAVE — KIM (Kim)

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP01-MS00-KIM-CHARGEN",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 0,
    "px": 0,
    "px_state": "stable",
    "mode": "mixed",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-KIM-01",
      "name": "Kimberley Vane",
      "callsign": "KIM",
      "rank": "Rekrut",
      "lvl": 1,
      "xp": 0,
      "origin": { "epoch": "1920er Chicago", "hominin": "Homo sapiens sapiens", "role": "Smooth Operator" },
      "attr": { "STR": 1, "GES": 3, "INT": 4, "CHA": 6, "TEMP": 2, "SYS": 2 },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        { "name": "Silberzunge", "tier": "Basis", "effect": "+2 auf CHA-Proben bei Überredung & Täuschung" }
      ],
      "equipment": [
        { "name": "Derringer .22", "type": "weapon", "tier": 0 },
        { "name": "Elegante Zeitkleidung (1920er)", "type": "armor", "tier": 0 },
        { "name": "Gefälschte Papiere", "type": "gadget", "tier": 1 },
        { "name": "Comlink (verborgen)", "type": "gadget", "tier": 1 },
        { "name": "Verbandskit", "type": "consumable", "tier": 0 },
        { "name": "Notizblock & Stift", "type": "gadget", "tier": 0 }
      ],
      "implants": [],
      "history": {
        "background": "Journalistin, Chicago 1924. Wusste zu viel, redete zu gut. Das ITI fand sie bevor die falschen Leute es taten.",
        "milestones": []
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": { "id": "VEH-KIM-01", "name": "Stadtauto (1920er)", "type": "vehicle", "tier": 1, "upgrades": [] },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 0,
        "faction": "Ordo Mnemonika",
        "factions": { "ordo_mnemonika": 0, "chrono_symmetriker": 0, "kausalklingen": 0, "zerbrechliche_ewigkeit": 0 }
      },
      "wallet": 100
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [],
    "market": [],
    "artifact_log": [],
    "notes": ["Nullzeit-Einweisung abgeschlossen. Archivarin Mira. Vier externe Fraktionen erwähnt."],
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
    "summary_active_arcs": "Ep01 gestartet. Rekrutierung abgeschlossen. Briefing steht aus."
  },
  "continuity": {
    "last_seen": { "mode": "core", "episode": 1, "mission": 0, "location": "HQ-Quartiere" },
    "split": { "family_id": null, "thread_id": null, "expected_threads": [], "resolved_threads": [], "convergence_ready": false },
    "roster_echoes": [],
    "shared_echoes": [],
    "convergence_tags": [],
    "npc_roster": [
      { "id": "NPC-MIRA-01", "name": "Mira", "callsign": "Archivarin", "role": "ITI-Kernpersonal", "scope": "HQ", "status": "aktiv" }
    ],
    "active_npc_ids": []
  },
  "arc": { "factions": { "ordo_mnemonika": "unbekannt", "chrono_symmetriker": "unbekannt", "kausalklingen": "unbekannt", "zerbrechliche_ewigkeit": "unbekannt" }, "questions": ["Was stand in den bereinigten Akten?", "Welche Fraktionen lesen Rekrutierungsmuster?"], "hooks": [] },
  "ui": { "gm_style": "verbose", "suggest_mode": false, "contrast": "standard", "badge_density": "standard", "output_pace": "normal", "voice_profile": "gm_second_person" }
}
```

---

### SAVE — SPLINTER (Sarah)

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP01-MS00-SPLINTER-CHARGEN",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 0,
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
      "xp": 0,
      "origin": { "epoch": "unbekannt", "hominin": "Homo sapiens sapiens", "role": "Infiltration & Intel" },
      "attr": { "STR": 2, "GES": 5, "INT": 5, "CHA": 2, "TEMP": 2, "SYS": 2 },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        { "name": "Tatortanalyse", "tier": "Basis", "effect": "+2 auf INT-Proben bei Spurensicherung & Analyse (Echo aus früherem Leben)" }
      ],
      "equipment": [
        { "name": "Dienstpistole", "type": "weapon", "tier": 1 },
        { "name": "Kevlarweste", "type": "armor", "tier": 1 },
        { "name": "Handscanner", "type": "gadget", "tier": 1 },
        { "name": "Multitool", "type": "gadget", "tier": 1 },
        { "name": "Comlink", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 }
      ],
      "implants": [],
      "history": {
        "background": "Herkunft offen. Tatortanalyse als Echo aus früherem Leben — liest Szenen bevor sie etwas anfasst.",
        "milestones": []
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": { "id": "VEH-SPLINTER-01", "name": "Feldfahrzeug (Standard)", "type": "vehicle", "tier": 1, "upgrades": [] },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 0,
        "faction": "Ordo Mnemonika",
        "factions": { "ordo_mnemonika": 0, "chrono_symmetriker": 0, "kausalklingen": 0, "zerbrechliche_ewigkeit": 0 }
      },
      "wallet": 100
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [],
    "market": [],
    "artifact_log": [],
    "notes": ["Nullzeit-Einweisung abgeschlossen. Archivarin Mira. Vier externe Fraktionen erwähnt. Akten-Bereinigung: vor Rekrutierung, Standardprotokoll."],
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
    "summary_active_arcs": "Ep01 gestartet. Rekrutierung abgeschlossen. Briefing steht aus."
  },
  "continuity": {
    "last_seen": { "mode": "core", "episode": 1, "mission": 0, "location": "HQ-Quartiere" },
    "split": { "family_id": null, "thread_id": null, "expected_threads": [], "resolved_threads": [], "convergence_ready": false },
    "roster_echoes": [],
    "shared_echoes": [],
    "convergence_tags": [],
    "npc_roster": [
      { "id": "NPC-MIRA-01", "name": "Mira", "callsign": "Archivarin", "role": "ITI-Kernpersonal", "scope": "HQ", "status": "aktiv" }
    ],
    "active_npc_ids": []
  },
  "arc": { "factions": { "ordo_mnemonika": "unbekannt", "chrono_symmetriker": "unbekannt", "kausalklingen": "unbekannt", "zerbrechliche_ewigkeit": "unbekannt" }, "questions": ["Was stand in den bereinigten Akten?", "Welche Fraktionen lesen Rekrutierungsmuster?", "Wann wurden Voss' Akten bereinigt — und warum war das Timing präzise?"], "hooks": [] },
  "ui": { "gm_style": "verbose", "suggest_mode": false, "contrast": "standard", "badge_density": "standard", "output_pace": "normal", "voice_profile": "gm_second_person" }
}
```

---

`Kodex: Drei Deepsaves ausgegeben. Blöcke kopieren, sicher ablegen.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

**Wie geht's weiter?**

1. **Erkunden** — Kodex-Archiv, Zero Time Lounge, Hangar, andere HQ-Orte
2. **Direkt ins Briefing** — Mission 1, Episode 1
3. **Neuer Chat** — Saves laden, frisch starten *(empfohlen vor langen Sessionen)*
4. **Freie Aktion**
