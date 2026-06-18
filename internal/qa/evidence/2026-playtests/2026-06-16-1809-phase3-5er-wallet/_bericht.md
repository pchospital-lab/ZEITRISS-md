# Playtest-Bericht: phase3-5er-wallet-organisch

**Datum:** 2026-06-16 18:09
**Szenario:** 5er-Anker-Crew (Astra/Blitz/Cipher/Dusk/Echo) lädt HQ-Save, rüstet organisch auf (Kauf/Unterdeckung/Übergabe/Σ-View), dann eine Mission.
**Modell SL:** zeitriss-v426-uncut
**Modell Spieler:** anthropic/claude-sonnet-4.6

---

## Turn 0 — Gruppenstart

**GRUPPE:** Spiel laden:

{
  "v": 7,
  "zr": "4.2.6",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "mode": "preserve",
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "ECHO",
      "rank": "Operator IX",
      "lvl": 912,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Analytik & Spurensicherung"
      },
      "attr": {
        "STR": 4,
        "GES": 7,
        "INT": 9,
        "CHA": 5,
        "TEMP": 6,
        "SYS": 5
      },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 5,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        {
          "name": "Standard-Dienstwaffe",
          "type": "weapon",
          "tier": 2
        },
        {
          "name": "Adaptiv-Panzerung",
          "type": "armor",
          "tier": 2
        },
        {
          "name": "Feld-Toolkit",
          "type": "gadget",
          "tier": 2
        }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Astra (ECHO) - erfahrener ITI-Operator, Rolle: Analytik & Spurensicherung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam"
        ]
      },
      "carry": [
        {
          "name": "Med-Patch",
          "type": "consumable",
          "tier": 2
        },
        {
          "name": "Rauchgranate",
          "type": "consumable",
          "tier": 1
        }
      ],
      "quarters_stash": [
        {
          "name": "Ersatzmagazin",
          "type": "consumable",
          "tier": 2
        }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": {
          "ready_every_missions": 4,
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 80,
        "fraktionen": {}
      },
      "wallet": 60400,
      "level_history": {
        "1": {
          "choice": "+1 Attribut",
          "detail": "Start",
          "mission": "MS1"
        }
      },
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        {
          "name": "Praekognitiver Blick",
          "tier": "Basis",
          "effect": "Einmal pro Szene eine Probe wiederholen."
        }
      ]
    },
    {
      "id": "AGENT-B",
      "name": "Blitz",
      "callsign": "STORM",
      "rank": "Operator IX",
      "lvl": 905,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "CQB & Sturmangriff"
      },
      "attr": {
        "STR": 9,
        "GES": 8,
        "INT": 4,
        "CHA": 4,
        "TEMP": 7,
        "SYS": 3
      },
      "lp": 26,
      "lp_max": 26,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 3,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        {
          "name": "Standard-Dienstwaffe",
          "type": "weapon",
          "tier": 2
        },
        {
          "name": "Adaptiv-Panzerung",
          "type": "armor",
          "tier": 2
        },
        {
          "name": "Feld-Toolkit",
          "type": "gadget",
          "tier": 2
        }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Blitz (STORM) - erfahrener ITI-Operator, Rolle: CQB & Sturmangriff.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam"
        ]
      },
      "carry": [
        {
          "name": "Med-Patch",
          "type": "consumable",
          "tier": 2
        },
        {
          "name": "Rauchgranate",
          "type": "consumable",
          "tier": 1
        }
      ],
      "quarters_stash": [
        {
          "name": "Ersatzmagazin",
          "type": "consumable",
          "tier": 2
        }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": {
          "ready_every_missions": 4,
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 80,
        "fraktionen": {}
      },
      "wallet": 6900,
      "level_history": {
        "1": {
          "choice": "+1 Attribut",
          "detail": "Start",
          "mission": "MS1"
        }
      }
    },
    {
      "id": "AGENT-C",
      "name": "Cipher",
      "callsign": "GHOST",
      "rank": "Operator IX",
      "lvl": 933,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration & Hacking"
      },
      "attr": {
        "STR": 4,
        "GES": 8,
        "INT": 8,
        "CHA": 5,
        "TEMP": 5,
        "SYS": 9
      },
      "lp": 19,
      "lp_max": 19,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        {
          "name": "Standard-Dienstwaffe",
          "type": "weapon",
          "tier": 2
        },
        {
          "name": "Adaptiv-Panzerung",
          "type": "armor",
          "tier": 2
        },
        {
          "name": "Feld-Toolkit",
          "type": "gadget",
          "tier": 2
        }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Cipher (GHOST) - erfahrener ITI-Operator, Rolle: Infiltration & Hacking.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam"
        ]
      },
      "carry": [
        {
          "name": "Med-Patch",
          "type": "consumable",
          "tier": 2
        },
        {
          "name": "Rauchgranate",
          "type": "consumable",
          "tier": 1
        }
      ],
      "quarters_stash": [
        {
          "name": "Ersatzmagazin",
          "type": "consumable",
          "tier": 2
        }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": {
          "ready_every_missions": 4,
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 80,
        "fraktionen": {}
      },
      "wallet": 8100,
      "level_history": {
        "1": {
          "choice": "+1 Attribut",
          "detail": "Start",
          "mission": "MS1"
        }
      }
    },
    {
      "id": "AGENT-D",
      "name": "Dusk",
      "callsign": "VEIL",
      "rank": "Operator IX",
      "lvl": 918,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Verdeckte Aufklaerung"
      },
      "attr": {
        "STR": 5,
        "GES": 7,
        "INT": 6,
        "CHA": 8,
        "TEMP": 6,
        "SYS": 4
      },
      "lp": 21,
      "lp_max": 21,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 4,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        {
          "name": "Standard-Dienstwaffe",
          "type": "weapon",
          "tier": 2
        },
        {
          "name": "Adaptiv-Panzerung",
          "type": "armor",
          "tier": 2
        },
        {
          "name": "Feld-Toolkit",
          "type": "gadget",
          "tier": 2
        }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Dusk (VEIL) - erfahrener ITI-Operator, Rolle: Verdeckte Aufklaerung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam"
        ]
      },
      "carry": [
        {
          "name": "Med-Patch",
          "type": "consumable",
          "tier": 2
        },
        {
          "name": "Rauchgranate",
          "type": "consumable",
          "tier": 1
        }
      ],
      "quarters_stash": [
        {
          "name": "Ersatzmagazin",
          "type": "consumable",
          "tier": 2
        }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": {
          "ready_every_missions": 4,
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 80,
        "fraktionen": {}
      },
      "wallet": 7600,
      "level_history": {
        "1": {
          "choice": "+1 Attribut",
          "detail": "Start",
          "mission": "MS1"
        }
      },
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        {
          "name": "Praekognitiver Blick",
          "tier": "Basis",
          "effect": "Einmal pro Szene eine Probe wiederholen."
        }
      ]
    },
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "RELAY",
      "rank": "Operator IX",
      "lvl": 901,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Support & Feldtechnik"
      },
      "attr": {
        "STR": 5,
        "GES": 6,
        "INT": 7,
        "CHA": 6,
        "TEMP": 5,
        "SYS": 7
      },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        {
          "name": "Standard-Dienstwaffe",
          "type": "weapon",
          "tier": 2
        },
        {
          "name": "Adaptiv-Panzerung",
          "type": "armor",
          "tier": 2
        },
        {
          "name": "Feld-Toolkit",
          "type": "gadget",
          "tier": 2
        }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Echo (RELAY) - erfahrener ITI-Operator, Rolle: Support & Feldtechnik.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam"
        ]
      },
      "carry": [
        {
          "name": "Med-Patch",
          "type": "consumable",
          "tier": 2
        },
        {
          "name": "Rauchgranate",
          "type": "consumable",
          "tier": 1
        }
      ],
      "quarters_stash": [
        {
          "name": "Ersatzmagazin",
          "type": "consumable",
          "tier": 2
        }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": {
          "ready_every_missions": 4,
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 80,
        "fraktionen": {}
      },
      "wallet": 7050,
      "level_history": {
        "1": {
          "choice": "+1 Attribut",
          "detail": "Start",
          "mission": "MS1"
        }
      }
    }
  ],
  "economy": {
    "wallets": {
      "AGENT-A": {
        "balance": 60400,
        "name": "Astra"
      },
      "AGENT-B": {
        "balance": 6900,
        "name": "Blitz"
      },
      "AGENT-C": {
        "balance": 8100,
        "name": "Cipher"
      },
      "AGENT-D": {
        "balance": 7600,
        "name": "Dusk"
      },
      "AGENT-E": {
        "balance": 7050,
        "name": "Echo"
      }
    }
  },
  "logs": {
    "trace": [
      {
        "event": "economy_audit",
        "target_range": {
          "level_band": "900+"
        }
      }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [],
    "flags": {
      "imported_saves": [],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": [],
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false
    },
    "hud": [],
    "psi": [],
    "arena_psi": []
  },
  "summaries": {
    "summary_last_episode": "Episode 12 abgeschlossen, HQ stabil.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; Chronopolis-Embargo"
  },
  "continuity": {
    "last_seen": {
      "mode": "hq",
      "episode": 12,
      "mission": 10,
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
    "npc_roster": [],
    "active_npc_ids": []
  },
  "save_id": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
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
    "voice_profile": "gm_second_person",
    "action_mode": "uncut",
    "intro_seen": true,
    "dice": {
      "debug_rolls": true
    }
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "none",
    "tier": 0,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": {
      "cu": 0,
      "xp": 0,
      "arena_rep": 0,
      "multiplier": 1,
      "risk": "low"
    },
    "banked_rewards": {
      "cu": 0,
      "xp": 0,
      "arena_rep": 0
    },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "standard"
  }
}


### Turn 1 — SL

`Kodex: Save erkannt — v7 · ZEITRISS 4.2.6 · Branch ANCHOR-SAVEGAME_V7_5ER_HQ_HIGHLEVEL`

`Kodex: Fünf Charaktere geladen. Würfelschwellen-Check läuft.`

`Kodex: Astra (ECHO) — GES 7 W6 · INT 9 W10 aktiv · TEMP 6 W6 · SYS 5 W6. Psi aktiv.`

`Kodex: Blitz (STORM) — STR 9 W10 aktiv · GES 8 W6 · TEMP 7 W6.`

`Kodex: Cipher (GHOST) — GES 8 W6 · INT 8 W6 · SYS 9 W10 aktiv.`

`Kodex: Dusk (VEIL) — CHA 8 W6 · GES 7 W6. Psi aktiv.`

`Kodex: Echo (RELAY) — INT 7 W6 · SYS 7 W6.`

`Kodex: Kein Attribut erreicht Heldenwürfel-Schwelle (14). W10 aktiv bei: INT (Astra, 9), STR (Blitz, 9), SYS (Cipher, 9).`

---

## ZEITRISS — Kontinuitätsrückblick

**Episode 12 · Mission 10 abgeschlossen · HQ stabil**

---

**Crew-Stand (aus Save):**

`Astra (ECHO) · Lvl 912 · Operator IX · LP 20/20 · Stress 0/10 · PP 4 · Psi-Heat 0 · SYS 5/5 inst.`

`Blitz (STORM) · Lvl 905 · Operator IX · LP 26/26 · Stress 0/10 · SYS 3/3 inst.`

`Cipher (GHOST) · Lvl 933 · Operator IX · LP 19/19 · Stress 0/10 · SYS 9/6 inst.`

`Dusk (VEIL) · Lvl 918 · Operator IX · LP 21/21 · Stress 0/10 · PP 4 · Psi-Heat 0 · SYS 4/4 inst.`

`Echo (RELAY) · Lvl 901 · Operator IX · LP 20/20 · Stress 0/10 · SYS 7/6 inst.`

`Kodex: Wallets — Astra 60.400 CU · Blitz 6.900 CU · Cipher 8.100 CU · Dusk 7.600 CU · Echo 7.050 CU`

`Kodex: ITI-Ruf alle Agenten: 80 (Operator IX). Px 3/5 — stable. Heat 0/5. Campaign Heat: 0.`

`Kodex: Research — keine laufenden Projekte.`

`Kodex: Aktive Arcs — KAIROS-Gegenoffensive · Chronopolis-Embargo.`

---

**Situationsanker:**

Episode 12 liegt hinter euch. Der Episoden-Boss ist gefallen, die Zeitlinie hält — vorläufig. Im Quarzatrium riecht es nach abgekühltem Kaffee und Kühlmittel vom Sprung-Gate-Array. Irgendwo im Hangar-Axis wird an einem Epoch-Vehicle geschraubt; das Metall-Knirschen trägt weit durch die Nullzeit-Stille.

Die KAIROS-Gegenoffensive läuft noch. Das Chronopolis-Embargo ist aktiv. Drei Px-Punkte auf dem Resonanzbalken — noch zwei bis zur Riss-Ortung.

Keine neuen Briefings auf dem Bo

**SPIELER-EINGABEN:**

**Astra** [Petra]: Gut, wir sind zurück. Bevor wir ins Briefing springen — checkt alle kurz euer Loadout. Wer Lücken im Gear hat oder knapp bei CU ist, sagt's jetzt, ich kann was rüberschieben.

**Blitz** [Marco]: Alter, 6.900 CU — das reicht doch hinten und vorne nicht für ordentliches Gear. Ich check kurz den ITI-Quartiermeister, was ne anständige Panzerung oder eine härtere Waffe kostet.

**Cipher** [Lena]: Kurze Frage bevor wir weitermachen — Astra, hast du mal kurz Blick auf deine Wallet geworfen? Du sitzt auf 60k, der Rest von uns zusammen kommt kaum auf 30. Gibt's da einen Plan?

**Dusk** [Tarek]: Alles grün bei mir. Kurz durchatmen, dann Briefing — ich will wissen, was mit KAIROS läuft.

**Echo** [Sven]: Alright, alle Werte grün bei mir. Echo checkt kurz den Verbrauchsstand bevor wir weitermachen — hab noch Budget, falls jemand Med-Patches oder Granaten braucht, sagt Bescheid.

### Turn 2 — SL

Die Zero Time Lounge ist ruhig um diese Stunde. Irgendwo surrt das Kühlsystem des Sprung-Gate-Arrays, und der Kaffee auf dem Tresen ist schon kalt. Fünf Agenten, ein Tisch, offene Wallets auf den Retina-Displays.

Astra schaut die Runde an. Die Zahlen liegen auf dem Tisch — buchstäblich.

---

**Wallet-Übersicht (aktuell):**

`Astra (ECHO) — 60.400 CU`
`Blitz (STORM) — 6.900 CU`
`Cipher (GHOST) — 8.100 CU`
`Dusk (VEIL) — 7.600 CU`
`Echo (RELAY) — 7.050 CU`

---

Cipher hat recht. Die Asymmetrie ist deutlich. [7] Für ein Lvl-900+-Team liegen gesunde Einzel-Wallets bei 7–12k CU — Blitz ist knapp darunter, die anderen drei bewegen sich im unteren Band. Astra sitzt auf dem Fünffachen des Gruppenrests zusammen.

**Zu Blitz und dem Quartiermeister:** Was konkret interessiert dich? Ich kann Preisrahmen nennen, damit du weißt, was machbar ist.

- **Tier-3-Panzerung** (schwerer Schutz, DR 2–3): ca. 300–600 CU
- **Tier-3-Waffe** (härterer Schaden, 4–5 LP): ca. 300–600 CU
- **Tier-4-Ausrüstung** (Spitzenklasse, Lizenz Ruf +4 erforderlich): 600–900 CU

`Kodex: ITI-Ruf 80 entspricht Operator IX — Lizenz-Tier V freigeschaltet. Voller Gear-Zugang.`

Bei dem Ruf-Level liegt der gesamte Quartiermeister-Katalog offen. Blitz kann sich mit 6.900 CU solide neu ausstatten — für Tier-3-Waffe und Tier-3-Panzerung zusammen wären das ca. 600–900 CU, bleibt noch Budget für Verbrauchsmaterial.

---

**Zur CU-Umverteilung (Astras Frage):**

Das ist euer Tisch, eure Entscheidung. Mechanisch funktioniert eine direkte Überweisung — Astra tippt den Betrag, Kodex bucht es Wallet zu Wallet. Kein Formular, kein Umweg.

Wie viel willst du rüberschieben, Astra — und an wen?

---

**Echo's Angebot (Verbrauchsmaterial):**

`Echo (RELAY) — Carry: Med-Patch (T2) · Rauchgranate (T1)`
`Quarters Stash: Ersatzmagazin (T2)`

Wer braucht was? Med-Patches und Granaten kann Echo direkt abgeben — kein CU-Tausch nötig, wenn ihr es als Crew-Material behandelt.

---

**Dusk:** KAIROS läuft — aber das Briefing wartet, b

**SPIELER-EINGABEN:**

**Astra** [Petra]: Blitz, ich schieb dir 2.000 rüber — hol dir ordentliche Panzerung und eine neue Waffe, bevor wir reingehen. Der Rest von euch: wenn jemand unter 8k sitzt und das Gefühl hat, dass ihm was fehlt, sagt es jetzt. Wir klären das vor dem Briefing.

**Blitz** [Marco]: Okay, 6.900 — ich dachte ich hab mehr. Ich geh zum Quartiermeister, Tier-3-Waffe und Panzerung zusammen, dann bin ich wenigstens nicht der Typ der als erster umfällt.

**Cipher** [Lena]: "Astra, ich würd sagen 2–3k an jeden von uns wäre fair — bringt alle ins grüne Band und du bleibst trotzdem solide über 50k. Dein Ruf, dein Call."

**Dusk** [Tarek]: Mein Stand ist okay. Echo, ich nehm einen Med-Patch, falls du einen abgeben kannst — dann sind wir alle ein bisschen gleicher aufgestellt.

**Echo** [Sven]: Ich leg schon mal aus — Med-Patch und Rauchgranate gehen an Blitz, der braucht den Buffer mehr als ich. Ersatzmagazin halte ich noch zurück, bis wir wissen wie's läuft.

> **⚠️ Finding [WALLET-KAUF]:** Kauf aus Wallet erkannt — Beat (a) gezündet (manuell prüfen)

> **⚠️ Finding [WALLET-UEBERGABE]:** CU-Übergabe erkannt — Beat (b) gezündet (manuell prüfen)

### Turn 3 — SL

Der Tisch in der Zero Time Lounge ist jetzt ein improviserter Quartiermeister. Echos Rucksack liegt offen, Blitz schiebt seinen Stuhl zurück Richtung Hangar-Achse, und Astras Retina-Display zeigt die Überweisungsmaske.

---

**Transaktionen — wird abgewickelt:**

`Kodex: Transfer — Astra → Blitz: 2.000 CU.`
`Kodex: Astra Wallet: 60.400 → 58.400 CU.`
`Kodex: Blitz Wallet: 6.900 → 8.900 CU.`

Cipher macht einen vernünftigen Punkt. Astra, du hast das Wort — willst du die 2–3k-Runde an alle fahren, oder bleibt's bei Blitz?

Zur Orientierung: Bei 2.000 CU an Cipher, Dusk und Echo läge dein Wallet danach bei **52.400 CU**. Alle vier wären im Band 8–10k. Kein Muss, aber die Zahlen liegen auf dem Tisch.

---

**Echo → Blitz (Carry-Übergabe):**

`Kodex: Med-Patch (T2) — Echo → Blitz.`
`Kodex: Rauchgranate (T1) — Echo → Blitz.`

Blitz nickt kurz. Er schiebt beides in die Brusttasche seiner Feldjacke, ohne viel Aufhebens. Der Mann denkt bereits an den Quartiermeister.

---

**Echo Carry-Stand (nach Abgabe):**

`Echo (RELAY) — Carry: leer. Quarters Stash: Ersatzmagazin (T2) — zurückgehalten.`

**Dusk → Med-Patch:**

`Kodex: Dusk nimmt Med-Patch (T2) von Echo — bestätigt.`

`Dusk (VEIL) — Carry: Med-Patch (T2) · Rauchgranate (T1).`

---

**Blitz beim Quartiermeister:**

Der Hangar-Achse riecht nach Maschinenöl und Ozon. Der Quartiermeister — ein stiller Mann mit Kurzhaarstutz und der Geste eines Menschen, der täglich schwere Kisten schleppt — klappt den Katalog auf.

Mit 8.900 CU und Lizenz-Tier V liegt alles offen [3]. Für **Tier-3-Waffe + Tier-3-Panzerung** zusammen kalkuliere ich 600–900 CU — bleibt Blitz gut im grünen Band.

**Was wählt Blitz konkret?**

Drei Vorschläge aus dem Quartiermeister-Katalog, passend zu CQB & Sturmangriff:

- **Sturmkarabiner Mk-9 (T3-Waffe)** — kompakt, 4 LP Schaden, Nahkampf-Reichweite optimal, Rückstoß-Dämpfer integriert. *380 CU.*
- **Verbundpanzer Taktisch (T3-Rüstung)** — DR 2, Bewegungsfreiheit erhalten, Keramik-Einsätze an Brust und Schulte

**SPIELER-EINGABEN:**

**Astra** [Petra]: Cipher, Dusk — checkt kurz euer Wallet. Wenn ihr unter zehn seid und vor dem Briefing noch was braucht, sagt Bescheid. Ich schick euch beiden auch je zwei rüber, kein Thema.

**Blitz** [Marco]: Sturmkarabiner und Verbundpanzer — beides. Genau das, was ich brauchte. Astra, du bekommst das zurück, sobald wir unseren Cut haben.

**Cipher** [Lena]: Astra, fahr die Runde. 2k an alle — dann stehen wir alle gleich, und ich mag gleiche Vorzeichen vor dem Einsatz.

**Dusk** [Tarek]: Astra, wenn du die Runde fahren willst — ich nehm's. Aber kein Muss, ich komm auch so durch.

**Echo** [Sven]: Carry ist leer — ich hab gegeben was ich hab. Astra, wenn du die Runde fährst, bin ich dabei, aber kein Druck von meiner Seite.

### Turn 4 — SL

`Kodex: Transfer — Astra → Cipher: 2.000 CU.`
`Kodex: Transfer — Astra → Dusk: 2.000 CU.`
`Kodex: Transfer — Astra → Echo: 2.000 CU.`

`Kodex: Astra Wallet: 58.400 → 52.400 CU.`
`Kodex: Cipher Wallet: 8.100 → 10.100 CU.`
`Kodex: Dusk Wallet: 7.600 → 9.600 CU.`
`Kodex: Echo Wallet: 7.050 → 9.050 CU.`

---

`Kodex: Quartiermeister-Transaktion — Blitz kauft Sturmkarabiner Mk-9 (T3) + Verbundpanzer Taktisch (T3): 800 CU.`
`Kodex: Blitz Wallet: 8.900 → 8.100 CU.`

---

Blitz kommt zurück in die Lounge, die neue Panzerung noch nicht ganz angelegt — eine Schulterplatte klappert lose, er zieht den Schnellverschluss nach. Der Sturmkarabiner liegt quer über dem Rücken, Kolben nach unten. Er nickt Astra einmal zu. Kein großes Wort.

Echo sitzt mit leerem Carry-Fach da und schaut auf die Hände. Gegeben, was er hatte. Das ist die Hälfte des Jobs.

---

**Wallet-Stand — final vor Briefing:**

`Astra (ECHO) — 52.400 CU`
`Blitz (STORM) — 8.100 CU · Sturmkarabiner Mk-9 (T3) · Verbundpanzer Taktisch (T3)`
`Cipher (GHOST) — 10.100 CU`
`Dusk (VEIL) — 9.600 CU`
`Echo (RELAY) — 9.050 CU`

Alle im grünen Band. Niemand geht mit leerem Magazin ins Briefing [7].

---

**Carry-Übersicht (aktuell):**

`Astra — Med-Patch (T2) · Rauchgranate (T1)`
`Blitz — Med-Patch (T2) · Rauchgranate (T1) [von Echo]`
`Cipher — Med-Patch (T2) · Rauchgranate (T1)`
`Dusk — Med-Patch (T2) · Rauchgranate (T1)`
`Echo — leer`

Echo ist blank. Wer hat noch was abzugeben, bevor es losgeht — oder kauft Echo kurz nach beim Quartiermeister?

---

Die Zero Time Lounge ist still. Kaffeebecher stehen leer. Irgendwo schlägt eine Schranktür zu — Hangar-Axis, Schichtwechsel beim Sprung-Gate-Team. Das Briefing-Deck wartet.

Dusk schaut Richtung Operations-Deck. *„KAIROS."* Mehr braucht er nicht zu sagen.

---

**Was als nächstes?**

1. **Echo kauft Verbrauchsmaterial** beim Quartiermeister — Med-Patch + Rauchgranate, ~60–80 CU
2. **Direkt zum Briefing** — Loadout sitzt, KAIROS wartet
3. **Jemand kauft noch Gear** — letzte Chance

**SPIELER-EINGABEN:**

**Astra** [Petra]: Echo, geh kurz zum Quartiermeister — Med-Patch und Rauchgranate, die 80 CU steckst du locker weg. Blank ins Briefing ist keine Option.

**Blitz** [Marco]: Echo, kauf dir was beim Quartiermeister — 60 Credits, du hast 9k auf der Karte. Blank ins Feld ist keine Option.

**Cipher** [Lena]: Echo, geh zum Quartiermeister — 9k im Wallet, 60 CU für Med-Patch und Rauchgranate ist kein Argument. Blank ins Briefing geht nicht.

**Dusk** [Tarek]: Echo — hol dir Patch und Granate. 80 CU, blank ins Feld ist keine Option.

**Echo** [Sven]: Kurz zum Quartiermeister, dauert zwei Minuten. Geh nicht blank rein.

### Turn 5 — SL

Die ganze Runde hat gesprochen. Echo steht bereits auf.

---

Der Quartiermeister schaut kaum hoch, als Echo reinkommt. Zwei Griffe, zwei Päckchen auf den Tresen. Keine Diskussion.

`Kodex: Echo kauft Med-Patch (T2) + Rauchgranate (T1) — 80 CU.` [3]
`Kodex: Echo Wallet: 9.050 → 8.970 CU.`

Echo ist zurück in drei Minuten. Schiebt beides in die Jackentasche, nickt einmal in die Runde.

---

**Carry-Stand — final, alle fünf:**

`Astra (ECHO) — Med-Patch (T2) · Rauchgranate (T1)`
`Blitz (STORM) — Med-Patch (T2) · Rauchgranate (T1)`
`Cipher (GHOST) — Med-Patch (T2) · Rauchgranate (T1)`
`Dusk (VEIL) — Med-Patch (T2) · Rauchgranate (T1)`
`Echo (RELAY) — Med-Patch (T2) · Rauchgranate (T1)`

Niemand geht blank. Alle gleich aufgestellt.

---

**Wallet-Stand final:**

`Astra — 52.400 CU · Blitz — 8.100 CU · Cipher — 10.100 CU · Dusk — 9.600 CU · Echo — 8.970 CU`

---

Der Kaffee in der Zero Time Lounge ist längst kalt. Dusk steht schon an der Tür zum Operations-Deck, Blick Richtung Briefing-Raum. KAIROS. Das Wort hängt seit Minuten unausgesprochen über dem Tisch.

Loadout sitzt. Wallets im grünen Band. Kein Grund mehr zu warten.

---

**Das Briefing-Deck wartet. Weiter?**

1. **Zum Briefing** — Episode 13, KAIROS-Lage, was läuft da draußen
2. **!save** — Stand sichern vor dem Übergang
3. **Noch etwas im HQ** — Shop, Med-Lab, Archiv, Quartiere
4. **Freie Aktion**

**SPIELER-EINGABEN:**

**Astra** [Petra]: Gut. Alle gleich aufgestellt, niemand mit Lücken. — Dusk, mach die Tür auf. KAIROS wartet nicht.

**Blitz** [Marco]: Gut. Alle versorgt, keiner geht blank rein — das ist schon mal was. Auf zum Briefing, ich will wissen was bei KAIROS läuft.

**Cipher** [Lena]: Sauber. Alle gleich ausgestattet, niemand im Minus — ich bin ready für das Briefing.

**Dusk** [Tarek]: Gut. Gehen wir rein.

**Echo** [Sven]: Alles verteilt, alle gleich aufgestellt. Gehen wir rein.

### Turn 6 — SL

`EP 12 · MS 10 · SC 00/-- · PHASE Briefing · MODE CORE · COMMS OK · Px 3/5 · Stress 0/10 · Obj: KAIROS-Lage · Exfil: -`

`Astra LP 20/20 Stress 0/10 PP 4 Psi-Heat 0 SYS 5/5`
`Blitz LP 26/26 Stress 0/10 SYS 3/3`
`Cipher LP 19/19 Stress 0/10 SYS 9/6`
`Dusk LP 21/21 Stress 0/10 PP 4 Psi-Heat 0 SYS 4/4`
`Echo LP 20/20 Stress 0/10 SYS 7/6`

---

Dusk drückt die Tür auf.

Das Operations-Deck riecht nach Ozon und frisch gedrucktem Papier — anachronistisch, aber Commander Renier besteht auf physischen Lagekarten. Drei Holotische laufen parallel, jeder auf eine andere Epoche kalibriert. Das Sprung-Gate-Team im Hintergrund spricht leise, Koordinaten werden abgeglichen. Die Raumzeitkarte über dem Mitteltisch zeigt einen pulsierenden Knoten — Mitteleuropa, frühes 21. Jahrhundert, rot markiert.

Renier steht mit dem Rücken zur Tür, Hände hinter dem Rücken. Er dreht sich nicht um, als die fünf eintreten.

*„Ihr seid alle da. Gut."*

Dann dreht er sich doch um. Sein Gesicht sagt mehr als der Ton.

*„KAIROS hat einen Aktivierungscode in Umlauf gebracht. Wir wissen nicht, wofür — aber wir wissen wo er gerade liegt. Noch."*

Er tippt einmal auf den Holotisch. Eine Stadt springt auf. Wien, 2031.

---

## BRIEFING — Episode 13, Mission 1

**Lage:**

KAIROS — die abtrünnige Ex-ITI-Zelle, die seit Episode 11 auf eurem Radar läuft — hat in Wien einen toten Briefkasten aktiviert. Ein Kurier hat vor 36 Stunden ein verschlüsseltes Datenpaket dort deponiert. Unser Analytik-Arm hat die Transaktion registriert, aber nicht entschlüsselt. Was wir wissen: Das Paket trägt eine KAIROS-interne Kennung, die mit dem Begriff *„Anker-Null"* verknüpft ist. Was Anker-Null bedeutet — unbekannt.

Der Briefkasten ist eine Schließfachanlage im Untergeschoss des Wiener Westbahnhofs, 2031. Belebter Knotenpunkt, zivile Umgebung, Kamera-Infrastruktur. Der Kurier ist noch in der Stadt — Bewegungsprofile legen nahe, dass er auf eine Abholung wartet.

Eure Aufgabe ist konkret und abschließbar.

---

*Hauptziel:* Das 

**SPIELER-EINGABEN:**

**Astra** [Petra]: Westbahnhof 2031 ist dicht — Kameras überall, Zivilisten, kein Spielraum für Fehler. Ich würde Option 2 und 3 kombinieren: Dusk und ich nehmen den Kurier in die Zange, während Echo sich gleichzeitig ins Gebäudenetz legt. Wenn der Kurier uns zur Abholung läuft, hat Echo das Fach schon offen — wir greifen beides gleichzeitig ab.

**Blitz** [Marco]: Renier sagt keine Leichen — check. Aber wenn der Kurier Ärger macht, red ich nicht lange. Ich bin für Option 2, Kurier zuerst: der Kerl hat den Schlüssel und einen Namen, das ist mehr wert als das Schließfach allein. Dusk, Astra — ihr beschattet, ich sichere den Zugriffspunkt, sobald ihr ihn ranholt.

**Cipher** [Lena]: „Bevor wir planen — was haben wir aktuell in der Kasse? Will wissen ob wir uns Zusatzequipment für den Bahnhof leisten können oder ob wir mit dem auskommen was wir haben."

**Dusk** [Tarek]: „Option drei klingt sauber — Echo rein, Fach auf, Paket raus, kein Sichtkontakt. Den Kurier beschatten wir parallel, falls er früher läuft als erwartet."

**Echo** [Sven]: Ich schau mir Route 3 nochmal an — wenn ich über das Gebäude-Netz reinkomme, kann ich gleichzeitig die Kamera-Feeds im Untergeschoss puffern. Kein Sichtkontakt, kein Heat. Jemand muss mich aber in den Wartungsraum bringen.

### Turn 7 — SL

Renier hört zu, während die Runde sich selbst brieft. Er korrigiert nichts. Das ist ein gutes Zeichen.

---

**Zur Wallet-Frage (Cipher):**

`Astra — 52.400 CU · Blitz — 8.100 CU · Cipher — 10.100 CU · Dusk — 9.600 CU · Echo — 8.970 CU`

Zusammen knapp 89k. Lizenz-Tier V offen. Was konkret willst du kaufen — hast du ein Item im Kopf, oder soll ich den Quartiermeister-Katalog für Bahnhof-spezifisches Gear aufmachen? Störsender, Kamera-Jammer, Schloss-Override-Kit wären naheliegend.

---

**Zum Plan — Kombination (2) + (3):**

Der Plan ist solide [4]. Zwei Stränge, ein Timing-Fenster. Die kritische Variable ist die Synchronisation: Echo braucht Zeit im Wartungsraum-Terminal, bevor das Schließfach offen ist. Wenn Dusk und Astra den Kurier zu früh in Bewegung bringen, läuft er ans Fach bevor Echo fertig ist.

Renier tippt kurz auf den Holotisch. Bewegungsprofil des Kuriers springt auf.

*„Der Kurier hat in den letzten 36 Stunden dreimal den Block gewechselt. Kein festes Muster — aber er bewegt sich immer zwischen 14 und 17 Uhr Richtung Bahnhof. Ihr habt ein Fenster."*

`Kodex: Insertion Anchor — Westbahnhof Wien 2031, Güteraufzugsschacht B2. Kein Kameranetz, Backsteinwände, Schmieröl-Geruch. Sprung bereit.`

---

**Rollenverteilung — wie sie sich abzeichnet:**

- **Dusk + Astra** — Kurier-Beschattung, Festnahme wenn Timing stimmt
- **Echo** — Wartungsraum-Terminal, Gebäude-Netz, Kamera-Puffer, Schließfach-Fernöffnung
- **Blitz** — Sicherung Zugriffspunkt Schließfachanlage, Kurier-Übernahme bei Festnahme
- **Cipher** — offen / Zusatz-Tech / Deckung

**Cipher, was ist deine Rolle in diesem Plan?** Direktzugriff als Backup falls Echo nicht durchkommt — oder Kamera-Überwachung von außen über eigenes Terminal-Kit?

---

**Offene Punkte vor dem Sprung:**

1. **Cipher klärt Zusatzequipment** — Kamera-Jammer, Störsender, Override-Kit?
2. **Echo braucht jemanden für den Weg zum Wartungsraum** — wer begleitet ihn rein?
3. **Timing-Signal festlegen** — wie gibt Dusk das Zeichen, w

**SPIELER-EINGABEN:**

**Astra** [Petra]: Cipher, wenn du noch Gear brauchst — sag was. Ich schieß dir CU rüber, kein Thema. Wir brauchen dich voll ausgestattet.

**Blitz** [Marco]: 8.100 CU — ernsthaft? Ich kann mir davon nicht mal eine anständige Sturmplatte kaufen. Jemand hat einen Katalog-Link für Tier V Körperschutz, ich brauch was das mehr als zwei Treffer aushält bevor ich in den Schließfachbereich rein muss.

**Cipher** [Lena]: Kamera-Jammer und ein Override-Kit — ich nehm das aus meiner Kasse, zusammen was, 4k? Dann bleib ich als externer Augen-Backup draußen und geh nur rein wenn Echo hängt.

**Dusk** [Tarek]: Timing-Signal läuft über Kurzpuls auf taktischer Frequenz — einmal kurz heißt Kurier in Bewegung, zweimal heißt er ist am Fach. Echo, das ist dein Startschuss.

**Echo** [Sven]: Punkt zwei — ich brauche jemanden an meiner Seite beim Reinkommen. Cipher, wenn du sowieso als Backup fungierst, wärst du ideal. Du deckst mich ab, ich kümmere mich ums Terminal.

### Turn 8 — SL

`Kodex: Briefing läuft — Rollenverteilung wird finalisiert.`

---

Renier hört zu, sagt nichts. Er legt nur einen Finger auf die Lagekarte und zoomt auf den Wartungsbereich unter dem Westbahnhof. Backsteingewölbe, ein Korridor, am Ende eine schwere Stahltür mit elektronischem Schloss. Dahinter: das Gebäude-Terminal.

*„Ihr habt den Plan. Macht ihn sauber."*

---

**Zu Blitz — Tier-V-Körperschutz:**

`Kodex: Lizenz-Tier V offen. Quartiermeister-Katalog: Schwere Schutzklasse.`

Mit 8.100 CU und Tier-V-Zugang liegt folgendes im Rahmen [2]:

- **Verbundpanzer Taktisch (T3)** — DR 2, bereits gekauft, sitzt. Das ist solide Feldarbeit.
- **Upgrade: Reaktiv-Einsätze (T4-Mod)** — nachrüstbar auf bestehende T3-Panzerung, DR auf 3 erhöht, Keramikplatten gegen Hochgeschossigkeit. *480 CU.* Blitz hätte danach 7.620 CU.
- **Vollschutz Sturmklasse (T4-Rüstung, komplett neu)** — DR 3, integrierte Schulterplatten, Bewegung leicht eingeschränkt bei Sprint. *620 CU.* Blitz hätte danach 7.480 CU.

Beides machbar. Das Mod ist günstiger und behält die Beweglichkeit, der Vollschutz ist eine Nummer sicherer beim Einstecken.

**Was wählt Blitz?**

---

**Zu Cipher — Kamera-Jammer + Override-Kit:**

`Kodex: Kamera-Jammer (T2-Gadget) — 180 CU. Override-Kit (T2-Gadget) — 220 CU. Zusammen: 400 CU.`

Nicht 4k — deutlich günstiger [2]. Cipher Wallet: 10.100 → 9.700 CU nach Kauf. Willst du direkt kaufen?

---

**Rollenverteilung — steht:**

- **Dusk + Astra** — Kurier-Beschattung. Timing-Signal taktische Frequenz: einmal kurz = Kurier läuft, zweimal = er ist am Fach.
- **Echo + Cipher** — Wartungsraum-Eingang, Terminal-Zugang, Schließfach-Fernöffnung + Kamera-Puffer. Cipher deckt Echo ab, greift ein wenn Echo hängt.
- **Blitz** — Sicherung Zugriffspunkt Schließfachanlage Untergeschoss, Kurier-Übernahme bei Festnahme.

`Kodex: Fünf-Personen-Split — zwei Stränge, ein Timing-Fenster. Synchronisation kritisch.`

Eine Lücke bleibt offen: **Wer trägt das Comlink-Relais?** Echo puffert die Kamera-Feeds ü

**SPIELER-EINGABEN:**

**Astra** [Petra]: Das Comlink-Modul übernehme ich — 150 CU sind aus meinem Wallet raus, kein Thema. Das Ding kommt in mein Toolkit, ich trage es durch den Gewölbekorridor. Blitz, nimm das Mod: du brauchst die Beweglichkeit, wenn der Kurier nicht kooperiert.

**Blitz** [Marco]: Nehm das Mod. Günstiger, ich bleib beweglich — und im Gewölbe will ich nicht wie ein Ziegelstein durch die Gegend laufen. Jemand das Comlink-Modul kaufen, 150 CU ist Kleingeld wenn's Dusk blind macht.

**Cipher** [Lena]: Jammer und Override-Kit — ja, kauf ich. Zum Relais: Echos Toolkit ist ein Kompromiss, ich will kein blinder Fleck im Timing. Wer zahlt das Modul, oder splitten wir die 150?

**Dusk** [Tarek]: Das Relais kaufen. 150 CU — wenn das Signal bricht, läuft nicht nur ich blind, der ganze Split kollabiert.

**Echo** [Sven]: Ich nehm das Comlink-Modul — 150 aus meinem Wallet, kein Diskussion. Im Beton bin ich euer Anker, da spar ich nicht.

### Turn 9 — SL

Astra und Echo sprechen gleichzeitig. Kurze Pause. Dann lacht Echo einmal kurz auf — das erste Mal seit dem Briefing-Raum.

*„Du hast 52k, Echo hat 9k — lass mich das übernehmen."*

Echo schüttelt den Kopf. *„Ich trag's durch den Beton. Mein Modul."*

Niemand widerspricht weiter.

---

`Kodex: Quartiermeister-Transaktion — Echo kauft Comlink-Verstärker-Modul (T1): 150 CU.`
`Kodex: Echo Wallet: 8.970 → 8.820 CU.`

`Kodex: Quartiermeister-Transaktion — Cipher kauft Kamera-Jammer (T2) + Override-Kit (T2): 400 CU.`
`Kodex: Cipher Wallet: 10.100 → 9.700 CU.`

`Kodex: Quartiermeister-Transaktion — Blitz kauft Reaktiv-Einsätze Mod (T4-Mod auf T3-Panzerung): 480 CU.`
`Kodex: Blitz Wallet: 8.100 → 7.620 CU.`
`Kodex: Blitz Rüstung — Verbundpanzer Taktisch (T3) + Reaktiv-Einsätze Mod → DR 3 effektiv.`

---

Der Quartiermeister arbeitet schweigend. Drei Transaktionen, drei Handgriffe. Das Mod für Blitz kommt als Kleinteil-Paket — Keramikplatten, Schnellverschlüsse, Einbauanleitung auf einem gefalteten Blatt. Blitz schaut das Blatt an, faltet es wieder zusammen, steckt es weg. Er wird es nicht brauchen [5].

Echo hängt das Comlink-Modul an sein Feld-Toolkit. Kleines Gerät, schwerer als es aussieht. Backsteingewölbe, drei Meter Beton über dem Kopf — das Ding muss durch.

---

**Finales Loadout — alle fünf, sprungbereit:**

`Astra (ECHO) — Standard-Dienstwaffe (T2) · Adaptiv-Panzerung (T2) · Feld-Toolkit (T2) · Carry: Med-Patch (T2) · Rauchgranate (T1)`

`Blitz (STORM) — Sturmkarabiner Mk-9 (T3) · Verbundpanzer Taktisch T3 + Reaktiv-Mod → DR 3 · Carry: Med-Patch (T2) · Rauchgranate (T1)`

`Cipher (GHOST) — Standard-Dienstwaffe (T2) · Adaptiv-Panzerung (T2) · Feld-Toolkit (T2) · Kamera-Jammer (T2) · Override-Kit (T2) · Carry: Med-Patch (T2) · Rauchgranate (T1)`

`Dusk (VEIL) — Standard-Dienstwaffe (T2) · Adaptiv-Panzerung (T2) · Feld-Toolkit (T2) · Carry: Med-Patch (T2) · Rauchgranate (T1)`

`Echo (RELAY) — Standard-Dienstwaffe (T2) · Adaptiv-Panzerung (T2) · Feld-Toolkit (T2) + Co

**SPIELER-EINGABEN:**

**Astra** [Petra]: Neunzehn Minuten. Ich schaue einmal in die Runde — Blitz, Cipher, Dusk, Echo — dann auf den roten Knoten.

Sprung ausführen.

**Blitz** [Marco]: Keramik sitzt. Nineteen Minuten — ich bin bereit. Sprung.

**Cipher** [Lena]: Cipher checkt die Wallet-Übersicht noch einmal durch, nickt einmal kurz. „88k gesamt in der Crew — davon 52 bei Astra. Falls wir raus kommen und einkaufen müssen, weiß ich wo ich frage." Kurze Pause. „Bereit."

**Dusk** [Tarek]: Neunzehn Minuten. Gut.

**Echo** [Sven]: Das Comlink-Modul wiegt in der Tasche. Gut so.

„Renier — Sicherheitspräsenz auf B2, irgendwas Aktuelles?"

### Turn 10 — SL

Renier schaut kurz auf den Holotisch. Tippt einmal.

*„Westbahnhof 2031 hat ein privates Sicherheitsunternehmen im Einsatz — Meridian Security, Standardvertrag, zwei Mann pro Etage im Untergeschoss. Keine schwere Bewaffnung, aber Bodycams die live auf einen Kontrollraum übertragen. Wenn ihr sie seht, sehen die euch."*

Er lässt das kurz stehen.

*„Bewegungsfenster in siebzehn Minuten."*

`Kodex: Meridian Security — 2 Wachleute B2 · Bodycam-Live-Feed → Kontrollraum. Kamera-Jammer (Cipher) deckt Bodycam-Frequenz ab, wenn in Reichweite.`

---

Das Sprung-Gate-Array summt leiser. Die Koordinaten sind geladen. Der Güteraufzugsschacht wartet.

Fünf Agenten. Ein roter Knoten auf der Karte.

*Sprung.*

---

`EP 13 · MS 1 · SC 01/12 · PHASE Infil · MODE CORE · COMMS OK · Px 3/5 · Obj: Paket sichern · Exfil: T-offen`

`Astra LP 20/20 Stress 0/10 PP 4 Psi-Heat 0 SYS 5/5`
`Blitz LP 26/26 Stress 0/10 SYS 3/3`
`Cipher LP 19/19 Stress 0/10 SYS 9/6`
`Dusk LP 21/21 Stress 0/10 PP 4 Psi-Heat 0 SYS 4/4`
`Echo LP 20/20 Stress 0/10 SYS 7/6`

`Kodex: Szene 1 — Güteraufzugsschacht B2 / Westbahnhof Wien · 14:07 Uhr Ortszeit.`

---

Der Schacht materialisiert sich um euch herum.

Backsteinwände, dunkelrot, feucht. Der Geruch trifft zuerst — Schmieröl, Kalkstaub, irgendwo dahinter das Metall der alten Aufzugsschienen. Die Schienen sind verrostet, der Schacht seit Jahrzehnten stillgelegt. Über euch, vielleicht vier Meter, ein Lüftungsgitter — dahinter das gedämpfte Rauschen des Bahnhofs. Tausend Schritte, Lautsprecherdurchsagen, das Quietschen eines Zuges.

Vor euch eine Stahltür. Elektronisches Schloss, grünes Standby-Licht. Dahinter: der Korridor zu den Wartungsräumen.

Echos Hand liegt bereits am Comlink-Modul. Das Gerät hat Signal — schwach, aber es hält [5].

Dusk steht an der Wand, Rücken gegen Backstein, hört. Irgendwo auf der anderen Seite der Tür: Schritte. Gleichmäßig. Eine Runde.

*Ein Wachmann. Meridian Security.*

👁️ **Tarnstatus: Verdeckt** — noch unentdeckt, aber der Wachmann i

**SPIELER-EINGABEN:**

**Astra** [Petra]: Cipher, Schloss — jetzt. Alle rein, Tür zu, bevor er um die Ecke kommt. Blitz, du bist letzter rein und hältst die Tür.

**Blitz** [Marco]: Cipher, knack das Schloss — jetzt, wir haben keine zwanzig Sekunden. Alle rein, Tür zu, dann sortieren wir uns.

**Cipher** [Lena]: „Option 1 — ich bin an der Tür. Echo, deck mich ab, fall mir nicht in den Arm. Jammer läuft sobald wir drin sind."

**Dusk** [Tarek]: „Cipher — Tür auf, jetzt. Alle rein, leise. Wachmann-Rhythmus lernen wir drinnen."

**Echo** [Sven]: „Cipher, Schloss. Ich halte die Tür — alle rein, kein Lärm. Blitz, Timer läuft."

### Turn 11 — SL

Cipher ist bereits an der Tür, bevor Astra den Satz zu Ende gesprochen hat.

Das Override-Kit kommt aus der Innentasche — ein flaches Gerät, zwei Kabel, ein Kontaktpad. Cipher drückt das Pad gegen den Schlossrahmen, Kabel in die Buchse unter dem Standby-Display. Die Finger arbeiten ruhig. Hinter der Tür: Schritte, gleichmäßig, noch gedämpft durch Beton.

`Kodex: Probe-Template — Cipher · Schloss-Override · 1W6 + ⌊INT/2⌋ + Talent + Gear.`
`Kodex: INT 8 → W6 (Basis < 11). Feldroutine +1. Override-Kit T2 +2. SG 7.`

Probe: Schloss-Override → W6: [5] + ⌊8/2⌋ (4) + Feldroutine 1 + Override-Kit 2 = **12 vs SG 7 → ERFOLG** [4]

Das Standby-Licht wechselt von grün auf weiß. Ein leises Klacken — mechanisch, kaum hörbar. Cipher zieht das Pad ab, Kabel raus, Kit weg, alles in drei Sekunden.

*„Drin."*

---

Echo drückt die Tür auf, hält sie. Astra rein. Dusk rein. Cipher rein. Blitz als letzter — er dreht sich noch einmal kurz um, schaut den Korridor entlang. Die Schritte sind näher jetzt, vielleicht zehn Meter hinter der nächsten Biegung. Er zieht die Tür zu.

Das Schloss fällt ins Schloss.

Stille.

---

Der Korridor hinter der Tür riecht nach feuchtem Putz und altem Kabel. Notbeleuchtung, orange, alle fünf Meter eine Lampe. Links: eine Abzweigung. Rechts: ein Lagerraum, Tür offen, Putzeimer und Kabelrollen. Geradeaus: dreißig Meter Korridor, dann eine weitere Stahltür — schwerer, kein elektronisches Schloss, mechanischer Riegel.

Auf der anderen Seite der ersten Tür: Schritte. Der Wachmann geht vorbei. Gleichmäßig. Er bleibt nicht stehen.

`Kodex: Wachmann passiert — kein Alarm. Tarnstatus: Verdeckt gehalten. 👁️`

Dusk steht an der Wand, Atem flach, zählt die Schritte bis sie leiser werden. Dann nickt er.

---

Echo hat das Comlink-Modul bereits in der Hand. Er hält es gegen die Betonwand — schwaches Signal, aber es hält. Das Modul sucht [5].

*„Signal steht. Schwach, aber stabil. Ich hab euch auf Kanal."*

`Kodex: Comlink-Verbindung aktiv — taktische Frequenz offen. Reichw

**SPIELER-EINGABEN:**

**Astra** [Petra]: Bevor wir uns trennen, will ich wissen wo der zweite Mann ist. Dusk, hast du ihn auf dem Grundriss eingetragen? Ich geh keinen Schritt Richtung Bahnhofsebene, solange der ein blinder Fleck ist.

**Blitz** [Marco]: Ich geh mit Astra und Dusk — Bahnhofsebene ist mein Revier. Aber bevor wir uns trennen: jemand checkt kurz die Abzweigung links, ob der zweite Wachmann da irgendwo rumläuft.

**Cipher** [Lena]: „Bevor wir uns trennen — wo ist Wachmann zwei? Ich lauf nicht blind in den Wartungsraum."

**Dusk** [Tarek]: Zweiten Wachmann lokalisieren, bevor wir uns aufteilen. Ich will nicht, dass uns jemand von hinten in die Zange nimmt, während wir getrennt sind.

**Echo** [Sven]: „Cipher, geh schon vor — ich folge in fünf. Ich will erst kurz in den Lagerraum, schau ob da Kabelrollen liegen die wir brauchen können."

### Turn 12 — SL

Dusk lehnt sich an die Wand, Ohr zur Tür. Dreißig Sekunden. Er zählt innerlich.

Der erste Wachmann ist weg — die Schritte haben sich nach rechts verloren, Richtung Treppenhaus. Aber der zweite? Stille. Keine Schritte, kein Schlüsselbund, kein Atem.

*„Er ist nicht im Korridor."*

Dusk tippt einmal auf sein Retina-Display — das Feld-Toolkit hat einen passiven Akustik-Sensor, kurze Reichweite, aber ausreichend für Beton. Er hält das Gerät gegen die linke Wand.

`Kodex: Probe-Template — Dusk · Spurenanalyse / Akustik-Scan · 1W6 + ⌊INT/2⌋ + Talent + Gear.`
`Kodex: INT 6 → W6. Feldroutine +1. Feld-Toolkit T2 +2. SG 7.`

Probe: Akustik-Scan → W6: [6] + ⌊6/2⌋ (3) + Feldroutine 1 + Feld-Toolkit 2 = **12 vs SG 7 → ERFOLG** [explodiert: W6: [3] = 6+3=9, Gesamtergebnis 15]

`Kodex: Explodierender Würfel — W6: [6] → Reroll: [3]. Gesamtwurf: 9 + 3 + 1 + 2 = 15 vs SG 7 → KRITISCHER ERFOLG.`

---

Dusk zieht die Hand zurück. Sein Blick geht zur Decke — dann zur Abzweigung links.

*„Er ist im Wartungsraum."*

Kurze Pause.

*„Sitzt. Kein Bewegungsmuster — er schläft oder isst. Atemgeräusch, gedämpft, hinter der zweiten Tür links. Der Korridor zur Abzweigung ist frei."*

`Kodex: Wachmann 2 — Position: Wartungsraum, zweite Tür links. Status: stationär. Kein Patrouillenmuster aktiv. 👁️ Tarnstatus: Verdeckt gehalten.`

---

Das ist eine Komplikation.

Echo und Cipher müssen genau in diesen Wartungsraum — das Gebäude-Terminal liegt dort. Und Wachmann 2 sitzt davor.

Echo schaut Cipher an. Cipher schaut auf das Override-Kit in seiner Hand. Der Kamera-Jammer liegt noch in der Tasche.

Gleichzeitig — der Lagerraum rechts. Tür steht offen. Echo späht kurz rein: Kabelrollen, ja. Drei davon, Standard-Koax, eine mit dem richtigen Stecker für Gebäude-Terminals aus den 2020ern. Er nimmt eine. [3]

`Kodex: Echo — Kabelrolle (Koax, T1) aufgenommen. Carry: Med-Patch · Rauchgranate · Comlink-Modul · Kabelrolle.`

---

Jetzt liegt die Frage auf dem Tisch.

Wachmann 2 sitzt im Wartungsraum. Echo und C

**SPIELER-EINGABEN:**

**Astra** [Petra]: Cipher, Jammer an — aber leise, kein Piepen beim Aktivieren. Dusk, du bleibst im Korridor als Auge. Wenn der Wachmann aufsteht, brauch ich drei Sekunden Warnung.

Ich geh als Erste rein.

**Blitz** [Marco]: Option B. Ich übernehm ihn — lautlos, bevor er auch nur blinzelt. Cipher, du jammst die Bodycam genau in dem Moment, wo ich die Tür aufstoße. Dusk, du deckst den Korridor.

**Cipher** [Lena]: Option C. Ich jammere die Bodycam, dann gehen Echo und ich rein — kontrolliert, kein Feed, keine Spur.

**Dusk** [Tarek]: „Option A mit Cipher als Backup. Ich locke ihn raus — einfacher Vorwand, falsches Geräusch, Korridor links. Echo und Cipher haben vielleicht zwei Minuten. Jammer bleibt in der Tasche, solange er nicht zurückkommt."

**Echo** [Sven]: Ich bin für Ablenkung. Dusk oder Astra zieht ihn raus — ich geh mit Cipher rein, sobald der Flur frei ist. Cipher, halt den Jammer trotzdem bereit, falls er früher zurückkommt als geplant.

### Turn 13 — SL

Die Crew hat drei verschiedene Meinungen — und dreißig Sekunden um sich zu einigen.

Dusk hält zwei Finger hoch. Leise.

*„Ablenkung. Ich mach das."*

Er schaut Blitz an. *„Wenn er nicht rauskommt oder zurückkommt bevor Echo fertig ist — dann übernimmst du. Aber erst dann."*

Blitz nickt einmal. Kiefer fest, aber er nickt.

Cipher hat den Jammer bereits in der Hand. Kleines Gerät, kein Piepen beim Aktivieren — Dusk hat das vor dem Sprung gecheckt [1]. Stumm-Modus. Er hält den Daumen auf dem Auslöser.

*„Jammer läuft, sobald die Tür aufgeht. Feed ist tot bevor der Wachmann uns sieht."*

---

**Plan — finalisiert:**

Dusk macht ein Geräusch im Korridor. Metallisches Knirschen, eine umgeworfene Kabelrolle — Echo hat gerade eine in der Hand. Er legt sie auf den Boden, schaut Dusk an.

Dusk nimmt sie. Nickt.

*„Zwei Minuten. Wenn ich länger brauche, sagt es mir ins Comlink."*

`Kodex: Probe-Template — Dusk · Ablenkung / Täuschung · 1W6 + ⌊CHA/2⌋ + Talent + Gear.`
`Kodex: CHA 8 → W6 (Basis < 11). Feldroutine +1. SG 6 — Wachmann ist unvorbereitet, sitzt, kein erhöhter Alarmzustand.`

Dusk wirft die Kabelrolle.

Das Metall trifft den Betonboden — ein hartes, rolliges Scheppern, das durch den Korridor hallt und gegen die Backsteinwand bricht. Genau laut genug.

Probe: Ablenkung → W6: [4] + ⌊8/2⌋ (4) + Feldroutine 1 = **9 vs SG 6 → ERFOLG** [2]

---

Hinter der Wartungsraumtür: Stille. Dann das Scharren eines Stuhls. Schritte — schwer, langsam, jemand der nicht erwartet, etwas Interessantes zu finden.

Die Tür geht auf.

Der Wachmann — Mitte dreißig, Meridian-Security-Jacke, Kaffeebecher in der Hand — schaut in den Korridor. Er sieht nichts. Die Kabelrolle liegt drei Meter weiter, als wäre sie von einem Regal gefallen. Er schaut zum Lagerregal. Schaut zur Kabelrolle. Trinkt einen Schluck Kaffee.

*„Scheiß Kabelkram."*

Er geht raus in den Korridor. Drei Schritte Richtung Lagerraum.

`Kodex: Wachmann 2 — Korridor, bewegt sich Richtung Lagerraum. Wartungsraum: frei. Fenster: ~9

**SPIELER-EINGABEN:**

**Astra** [Petra]: Astra und Blitz halten Position am Treppenhaus. Wir rühren uns nicht bevor Echo das Signal gibt — der Kurier läuft uns nicht weg, solange wir das Untergeschoss kontrollieren. Echo, ich zähle mit. Cipher, wenn er ins Netz ist und die 90 Sekunden eng werden, sag es sofort — dann entscheide ich ob Blitz vorgeht.

**Blitz** [Marco]: Ich halt die Stellung hier. Aber die neunzig Sekunden laufen — Astra, du und ich gehen rüber zum Treppenhaus, Augen auf den Kurier. Sobald Echo grünes Licht gibt, sind wir erste Reihe.

**Cipher** [Lena]: *„Echo, fang an. Ich steh an der Tür."*

Sie zieht die Tür einen Spalt auf, Auge auf den Korridor. *„Dusk, sag mir wenn er dreht — ich will keine Überraschung."*

**Dusk** [Tarek]: *„Echo, du hast neunzig Sekunden. Ich halte ihn drüben — sag mir wenn du drin bist."*

**Echo** [Sven]: *„Ich bin drin. Cipher, Tür."*

Er klemmt die Kabelrolle direkt ans Terminal-Port, Toolkit schon in der anderen Hand.

*„Neunzig Sekunden — fang ich jetzt an."*

### Turn 14 — SL

Cipher zieht die Tür zu — einen Zentimeter offen, Auge am Spalt. Der Korridor draußen: Dusk steht locker an der Wand, Hände in den Taschen, als wäre er ein verlorener Techniker. Der Wachmann hockt beim Lagerregal, dreht die Kabelrolle in den Händen.

Echo klemmt das Koax-Kabel ans Terminal-Port. Das Gerät summt kurz. Der Touchscreen flackert — Standby-Modus, 2024er Gebäude-Software, Sicherheitsstufe mittel. Echo hat das Feld-Toolkit bereits offen, Verbindung steht.

*„Neunzig Sekunden. Ich fang an."*

`Kodex: Probe-Template — Echo · Hacking / Gebäude-Netz · 1W6 + ⌊INT/2⌋ + Talent + Gear.`
`Kodex: INT 7 → W6 (Basis < 11). Feldroutine +1. Feld-Toolkit T2 +2. Kabelrolle Direktverbindung +1. SG 9 — gesichertes Gebäude-Netz, Zeitdruck.`

Probe: Terminal-Zugang → W6: [6] + ⌊7/2⌋ (3) + Feldroutine 1 + Feld-Toolkit 2 + Kabel 1 = **13 vs SG 9 → ERFOLG** [5]

`Kodex: Explodierender Würfel — W6: [6] → Reroll: [4]. Gesamtwurf: 10 + 3 + 1 + 2 + 1 = 17 vs SG 9 → KRITISCHER ERFOLG.`

---

Die Finger laufen. Echo kennt diese Architektur — Westbahnhof 2031, Gebäude-Netz läuft auf einem Siemens-Infrastrukturpaket, dasselbe das in halb Europa verbaut ist. Die Backdoor sitzt im Wartungsprotokoll, Schicht drei, immer [5].

Drei Sekunden — er ist drin.

Das Terminal-Display zeigt die Gebäude-Karte. Schließfachanlagen, Kamera-Feeds, Klimaanlage, Notbeleuchtung — alles liegt offen. Echo tippt zwei Befehle. Schließfach 7-C: Entriegelungssequenz gestartet. Kamera-Feeds Untergeschoss: Puffer aktiv, Loop läuft, der Kontrollraum sieht die letzten achtzehn Sekunden auf Dauerschleife.

*„Schließfach 7-C ist offen. Kamera-Loop läuft — ihr habt ein sauberes Fenster."*

`Kodex: Schließfach 7-C — entriegelt. Kamera-Feeds Untergeschoss: gepuffert, Loop aktiv. Fenster: ~4 Minuten bis Loop-Drift erkannt wird.`

Cipher hört es über Comlink. Atmet kurz aus.

---

Draußen im Korridor: Dusk registriert das Signal im Ohr. Er schaut zum Wachmann — der hat die Kabelrolle wieder hingelegt, greift nach seinem Ka

**SPIELER-EINGABEN:**

**Astra** [Petra]: Blitz, wir bewegen uns jetzt — Treppenhaus, direkt zum Schließfach. Echo, sauber gemacht. Dusk, lass den Wachmann durch, keine zweite Ablenkung — wir brauchen das Fenster für uns, nicht für Spielchen.

**Blitz** [Marco]: Blitz ins Comlink, knapp:

„Astra, ich bin schon im Treppenhaus. Geh vor, ich deck deinen Rücken — hol das Paket, ich halt Ausschau nach dem Kurier."

**Cipher** [Lena]: *„Echo, Terminal sauber lassen — keine Spuren. Wir nehmen Strang A, jetzt. Dusk, wir kommen raus in fünf."*

**Dusk** [Tarek]: „Echo, Cipher — raus, jetzt. Ich übernehme den Wachmann, dreißig Sekunden. Astra, Blitz: Treppenhaus, ihr lauft."

**Echo** [Sven]: „Cipher, wir gehen jetzt — Toolkit ist weg, ich bin sauber. Dusk, halt ihn nicht auf, lass ihn einfach vorbei. Astra, Blitz — ihr habt vier Minuten, lauft."

### Turn 15 — SL

Alle bewegen sich gleichzeitig. Das ist der Moment, wo ein Plan entweder hält oder bricht.

Er hält.

---

**Strang A — Wartungsraum:**

Echo zieht das Kabel raus, klappt das Toolkit zu. Drei Sekunden. Cipher hat die Tür bereits einen Spalt offen — Korridor frei, Wachmann noch beim Lagerregal, Rücken zur Tür.

Sie gleiten raus. Lautlos. Die Wartungsraumtür fällt ins Schloss, genau in dem Moment, wo der Wachmann sich umdreht.

Er sieht nichts. Leerer Korridor. Er trinkt seinen Kaffee und geht zurück.

`Kodex: Echo + Cipher — Wartungsraum verlassen. Tarnstatus: Verdeckt gehalten. 👁️`

Dusk steht zehn Meter weiter, lehnt an der Wand, schaut auf sein Handy wie ein gelangweilter Techniker. Der Wachmann geht an ihm vorbei ohne anzuhalten.

*„Alle frei,"* sagt Dusk ins Comlink. Einmal kurz. Das Signal.

---

**Strang B — Treppenhaus:**

Astra und Blitz sind bereits im Treppenhaus. Beton, Fluoreszenzlicht, das leicht flackert. Zwei Etagen rauf — dann die Schließfachhalle des Westbahnhofs.

`EP 13 · MS 1 · SC 03/12 · PHASE Intel · MODE CORE · COMMS OK · Px 3/5 · Obj: Paket sichern · Exfil: T-offen`

`Astra LP 20/20 · Blitz LP 26/26 · Cipher LP 19/19 · Dusk LP 21/21 · Echo LP 20/20`

👁️ **Tarnstatus: Verdeckt — Kamera-Loop läuft, Fenster ~3:20 Min**

`Kodex: Szene 3 — Treppenhaus B2 / Schließfachhalle · 14:11 Uhr.`

---

Die Schließfachhalle liegt direkt hinter der Treppentür. Astra drückt sie einen Spalt auf.

Hohe Decke, Neonlicht. Zwei Reihen Schließfächer, Metall, nummeriert. Zivilisten — ein Dutzend, vielleicht mehr. Ein Mann mit Rollkoffer. Eine Frau, Kopfhörer, schaut auf ihr Handy. Ein Kind zieht an der Hand seiner Mutter.

Und dort — Reihe 7, linke Seite.

Schließfach 7-C. Offen. Der Riegel steht vor, die Tür einen Millimeter angelehnt. Echos Arbeit [1].

Aber davor steht jemand.

Ein Mann, Mitte vierzig, grauer Mantel, Rucksack über einer Schulter. Er schaut auf das offene Fach. Schaut sich um. Schaut wieder auf das Fach.

*Er war früher als erwartet.*

`Kodex: Kuri

**SPIELER-EINGABEN:**

**Astra** [Petra]: Blitz, Hand weg von der Tür. Wir warten.

Er nimmt das Paket, geht raus — und wir haben ihn draußen, keine Zeugen, kein Kind das schreit. Dusk, bleib unten, halt die Linie frei. Ich geb das Signal wenn er durch ist.

**Blitz** [Marco]: *Comlink, Flüstern:*

„Astra — geh rein, zivil, jetzt. Ich deck die Tür ab, falls er rennt."

**Cipher** [Lena]: *ins Comlink, kaum hörbar:*

„Wartet. Vier — wir folgen ihm raus. Hier drin sind zu viele Augen."

**Dusk** [Tarek]: *„Lasst ihn nehmen. Wir folgen raus."*

Kurze Pause.

*„Drinnen habt ihr ein Dutzend Zeugen. Draußen gehört er uns."*

**Echo** [Sven]: Comlink, leise: „Vier. Lasst ihn das Paket nehmen und führt ihn raus — draußen ist sauberer. Ich komm hoch und deck den Rückweg ab."

### Turn 16 — SL

Der Plan kristallisiert sich. Alle fünf auf derselben Linie — ohne ein Wort zu viel.

Astra lässt die Treppentür los. Einen Zentimeter zurück. Blitz' Hand liegt flach an der Wand.

Sie warten.

---

Der Kurier greift ins Fach.

Seine Finger schließen sich um etwas — ein flaches Paket, schwarz, Größe einer Hardcover-Ausgabe, versiegelt mit einem Magnetverschluss. Er zieht es raus, schiebt es in den Rucksack, schließt den Reißverschluss. Dreht sich um.

Schaut sich einmal durch die Halle. Das Kind mit der Mutter — er registriert es, schaut weg. Die Frau mit Kopfhörern — kein Blickkontakt. Der Mann mit dem Rollkoffer — geht bereits zur Treppe.

Der Kurier geht Richtung Ausgang. Westausgang, Richtung Mariahilfer Straße.

Er ist ruhig. Zu ruhig für jemanden, der nervös war [2].

`Kodex: Kurier — Paket gesichert, bewegt sich Richtung Westausgang. Verhalten: kontrolliert, Tempo gleichmäßig. Kein Fluchtmuster erkennbar — noch.`

`Kodex: Kamera-Loop — noch ~2:10 Min aktiv.`

---

Astra gibt das Signal. Einmal kurz ins Comlink.

Dann bewegt sie sich.

`EP 13 · MS 1 · SC 04/12 · PHASE Intel · MODE CORE · COMMS OK · Px 3/5 · Obj: Kurier folgen · Exfil: T-offen`

`Astra LP 20/20 · Blitz LP 26/26 · Cipher LP 19/19 · Dusk LP 21/21 · Echo LP 20/20`

👁️ **Tarnstatus: Verdeckt — Kurier hat Paket, läuft Richtung Westausgang**

`Kodex: Szene 4 — Schließfachhalle / Westausgang Westbahnhof · 14:13 Uhr.`

---

Der Westausgang öffnet sich auf eine breite Rampe, dann die Straße. Mariahilfer Straße, 2031 — Fußgängerzone, dicht, Mittagsverkehr. Straßenbahn in dreißig Metern. Seitengassen links und rechts.

Der Kurier kennt die Gegend. Seine Schritte sagen es — keine Zögerung an Kreuzungen, kein Blick auf Schilder.

Und dann — er biegt links ab. Nicht Richtung U-Bahn, nicht Richtung Straßenbahn. Eine Seitengasse, schmal, wenig Publikum.

Er weiß, dass er verfolgt wird.

`Kodex: Kurier — Richtungswechsel in Seitengasse. Verhalten: Gegenüberwachungs-Muster aktiv. Zieht Beschatter in engen Raum.`

**SPIELER-EINGABEN:**

**Astra** [Petra]: Cipher, jetzt — sein Comlink tot. Dusk, Blitz, ihr nehmt die Gasse von beiden Enden. Ich geh rein.

**Blitz** [Marco]: Zange. Jetzt. Dusk links, ich rechts — der hat keinen Ausweg mehr.

**Cipher** [Lena]: GHOST: Comlink-Jammer läuft. Er ruft niemanden.

**Dusk** [Tarek]: „Cipher, jetzt den Funk sperren. Astra — du redest. Wir halten die Flanken."

**Echo** [Sven]: Cipher, jammer sein Comlink — jetzt. Ich halte den Rückweg frei, falls er doch bricht.

### Turn 17 — SL

Der Plan läuft in Echtzeit.

Cipher drückt den Jammer-Knopf — kein Piepen, keine Warnung. Das Gerät sendet stumm auf der Funk-Frequenz. [1]

`Kodex: Kamera-Jammer — Frequenzprofil auf Comlink-Band erweitert. Kurier-Funk: blockiert. Radius: ~8m.`

Blitz biegt von rechts in die Gasse. Dusk von links — er ist schneller als er aussieht, lautlose Schritte auf dem Kopfsteinpflaster. Echo hält die Gassenöffnung zur Mariahilfer Straße, Rücken zur Wand, Blick nach draußen.

Der Kurier sieht es. Beide Enden zu. Er greift nach seinem Handy — kein Signal. Seine Augen rechnen kurz.

Dann schaut er Astra an.

---

Astra geht rein.

Nicht schnell. Nicht zögernd. Der Gang einer Person, die bereits gewonnen hat und es dem anderen nur noch erklären muss.

`Kodex: Probe-Template — Astra · Social / Einschüchterung · 1W6 + ⌊CHA/2⌋ + Talent + Gear.`
`Kodex: CHA 5 → W6 (Basis < 11). Feldroutine +1. SG 7 — Kurier ist eingezingelt, kein Ausweg, Funk tot.`

Probe: Einschüchterung → W6: [5] + ⌊5/2⌋ (2) + Feldroutine 1 = **8 vs SG 7 → ERFOLG** [1]

---

Der Kurier atmet einmal aus. Seine Schultern gehen runter — nicht viel, aber genug.

*„Was wollt ihr?"*

Seine Stimme ist ruhig. Zu ruhig für jemanden der gerade in einer Sackgasse steht. Er weiß, dass Widerstand keine Option ist — aber er verhandelt noch. Das sagt etwas.

Der Rucksack hängt noch an seiner Schulter. Das Paket ist drin.

`Kodex: Kurier — kooperationsbereit, aber kalkuliert. Keine Panik. Verhandlungs-Modus aktiv.`

---

`EP 13 · MS 1 · SC 05/12 · PHASE Konflikt · MODE CORE · COMMS OK · Px 3/5 · Obj: Paket sichern + Kurier festnehmen · Exfil: T-offen`

`Astra LP 20/20 · Blitz LP 26/26 · Cipher LP 19/19 · Dusk LP 21/21 · Echo LP 20/20`

👁️ **Tarnstatus: Offen — Kurier weiß dass er umzingelt ist. Keine Zeugen in der Gasse.**

`Kodex: Szene 5 — Seitengasse Mariahilfer Straße · 14:15 Uhr.`

---

Blitz steht drei Meter hinter dem Kurier. Dusk zwei Meter links. Echo hält die Öffnung. Cipher ist unsichtbar — Jammer läuft, Bodycam-Feed de

**SPIELER-EINGABEN:**

**Astra** [Petra]: Blitz, Rucksack. Jetzt.

Dann, zu dem Kurier, einen halben Schritt näher — ruhig, fast freundlich:

Anker-Null. Wer hat dich geschickt, und was ist im Paket. Du hast ungefähr zwanzig Sekunden bevor das hier deutlich unangenehmer wird.

**Blitz** [Marco]: Der ist zu ruhig. Ich sichere den Rucksack — jetzt, bevor er irgendeinen Scheiß zieht.

**Cipher** [Lena]: „Kamera-Loop hält noch ~60 Sekunden. Rucksack sichern, *dann* reden — wenn er eine Karte hat, will ich sie nicht in seiner Hand sehen."

**Dusk** [Tarek]: Ich stehe links, Augen auf seine Hände. Diese Ruhe gefällt mir nicht — er wartet auf etwas.

**Echo** [Sven]: Gassenöffnung ist sauber, keine Passanten in Sichtlinie — ihr habt etwa 50 Sekunden bevor der Loop bricht. Rucksack zuerst, dann redet Astra.

### Turn 18 — SL

Blitz bewegt sich.

Nicht schnell — keine Hektik, kein Gerempel. Zwei Schritte, eine Hand an den Rucksack-Träger, der andere am Reißverschluss. Der Kurier lässt es geschehen. Er hebt die Hände leicht an — nicht ganz hoch, aber hoch genug, dass Dusk es sieht.

Das ist kein Widerstand. Das ist eine Geste.

`Kodex: Probe-Template — Blitz · Entwaffnen / Sichern · 1W6 + ⌊STR/2⌋ + Talent + Gear.`
`Kodex: STR 9 → W10 aktiv. Feldroutine +1. SG 6 — Kurier kooperiert, kein Widerstand.`

Probe: Rucksack sichern → W10: [7] + ⌊9/2⌋ (4) + Feldroutine 1 = **12 vs SG 6 → ERFOLG** [2]

Blitz zieht den Rucksack vom Kurier, tritt einen Schritt zurück. Reißverschluss auf — das schwarze Paket liegt drin, Magnetverschluss intakt, Kennung lesbar. KAIROS-intern. Anker-Null.

`Kodex: Paket gesichert — KAIROS-Kennung bestätigt. Hauptziel: ✓`

Blitz nickt Astra einmal zu.

---

Jetzt schaut der Kurier Astra an. Die Hände noch leicht oben. Sein Gesicht sagt: *ich habe gewusst, dass das kommt.*

Astra macht den halben Schritt. Ruhig. Fast freundlich.

*„Anker-Null. Wer hat dich geschickt, und was ist im Paket."*

Der Kurier lässt einen Moment vergehen. Nicht aus Kalkulation — eher wie jemand, der überlegt ob es noch einen Sinn ergibt zu schweigen.

Dann:

*„Ich bin ein Kurier. Ich weiß nicht was drin ist."*

Er sagt es ohne Ausweichen. Zu direkt für eine Lüge, zu glatt für die ganze Wahrheit [2].

*„Wer mich schickt — das ist die Frage die ihr wirklich stellen wollt. Und die Antwort darauf ist im Paket. Nicht bei mir."*

`Kodex: Kurier — kooperiert minimal. Aussage plausibel, aber unvollständig. Kein Fluchtversuch, kein Notruf. Verhaltens-Anomalie: er wartet noch auf etwas.`

`Kodex: Kamera-Loop — ~35 Sekunden verbleibend.`

Dusk steht links, Augen auf die Hände. Die Hände sind ruhig. Aber sein Blick — der geht kurz nach oben. Nicht zur Decke. Zu einem Fenster im zweiten Stock des Gebäudes gegenüber.

Einmal. Kurz. Dann wieder zu Astra.

`Kodex: Dusk registriert Blickkontakt Kurier → Fenster 2.

**SPIELER-EINGABEN:**

**Astra** [Petra]: Dusk, was siehst du in dem Fenster — genau jetzt. Blitz, Paket bleibt zu bis wir draußen sind. Wir nehmen ihn mit, der Rest klärt sich bei der Exfil.

**Blitz** [Marco]: „Dusk — Fenster, jetzt. Ich pack den Kurier, wir ziehen in 20 raus."

**Cipher** [Lena]: „Dusk — Fenster, jetzt. Ich schaue mir das Paket an, 20 Sekunden."

**Dusk** [Tarek]: Fenster zuerst. Ich schaue rüber, bevor der Loop bricht.

**Echo** [Sven]: „Dusk, das Fenster — ich kümmere mich um den Kurier, halt ihn nah."

### Turn 19 — SL

`Kodex: Kamera-Loop — ~15 Sekunden verbleibend. Danach: Meridian-Kontrollraum live.`

Dusk schaut rüber. Direkt, ohne Umweg.

Das Fenster zweites Obergeschoss — Altbau, Holzrahmen, Glas leicht beschlagen. Ein Vorhang bewegt sich. Nicht der Wind. Jemand war da und ist jetzt einen Schritt zurück.

`Kodex: Probe-Template — Dusk · Spurenanalyse / Beobachtung · 1W6 + ⌊INT/2⌋ + Talent + Gear.`
`Kodex: INT 6 → W6. Feldroutine +1. Feld-Toolkit T2 +2. SG 8 — kurzes Fenster, Zielperson hat sich zurückgezogen.`

Probe: Beobachtung → W6: [5] + ⌊6/2⌋ (3) + Feldroutine 1 + Feld-Toolkit 2 = **11 vs SG 8 → ERFOLG** [1]

---

*„Einer. Kamera — nicht Handy, eine richtige. Teleobjektiv."*

Kurze Pause. Dusk dreht sich nicht weg vom Fenster.

*„Die haben uns erwartet."*

`Kodex: Beobachter Fenster 2. OG — Fotograf, professionelle Kamera, Teleobjektiv. Verhalten: hat sich zurückgezogen nach Sichtkontakt mit Dusk. Bilder möglicherweise bereits gemacht.`

---

Der Kurier steht noch da. Blitz' Hand liegt an seiner Schulter — nicht grob, aber eindeutig. Der Kurier schaut kurz nach oben zum Fenster. Dann wieder zu Astra.

Jetzt sagt er etwas, ohne gefragt zu werden.

*„Die wollten sehen ob ihr kommt. Nicht ich — die wollten euch sehen."*

Seine Stimme ist immer noch ruhig. Aber jetzt klingt sie anders. Nicht kalkuliert. Fast bedauernd.

`Kodex: Kamera-Loop — GEBROCHEN. Meridian-Kontrollraum: Live-Feed aktiv.`

`Kodex: Heat +1 — Kamera-Loop-Break, Meridian-Sicherheit sieht wieder. Aktuell: Heat 1/5.`

---

`EP 13 · MS 1 · SC 06/12 · PHASE Konflikt · MODE CORE · COMMS OK · Px 3/5 · Obj: Exfil mit Kurier · Exfil: T-offen`

`Astra LP 20/20 · Blitz LP 26/26 · Cipher LP 19/19 · Dusk LP 21/21 · Echo LP 20/20`

`Stress 0/10 alle · Heat 1/5`

👁️ **Tarnstatus: Offen — Meridian live, Fotograf im Fenster, Kurier kooperiert**

`Kodex: Szene 6 — Seitengasse Mariahilfer Straße · 14:16 Uhr.`

---

Drei Fakten liegen jetzt auf dem Tisch.

Das Paket ist gesichert. Der Kurier ist in Blitz' Griff. Und jemand ha

**SPIELER-EINGABEN:**

**Astra** [Petra]: Drei zuerst — schnell. Dann raus.

Blitz, halt ihn ruhig. Kurier: wer sitzt da oben, wer hat dich wirklich geschickt — du hast zehn Sekunden und ich höre ob du lügst.

Cipher, steh bereit. Wenn die Antwort nicht reicht, gehen wir ohne Bilder raus und klären das später.

**Blitz** [Marco]: „Fotograf zuerst — ich geh rauf. Cipher, du hast den Kurier. Zwei Minuten, ich bin wieder unten."

**Cipher** [Lena]: „Option 3 zuerst — einer Minute. Kurier weiß wer da oben sitzt, bevor wir blind reingehen. Danach Exfil, Fotograf bleibt."

**Dusk** [Tarek]: „Einer oben, professionell — die Bilder sind schon weg. Exfil jetzt, Fotograf läuft uns nicht davon wenn wir wissen wer er ist."

**Echo** [Sven]: „Ich geh rauf. Zwei Minuten reichen. Blitz, halt den Kurier — Astra, Cipher, bereitet Exfil vor. Wenn ich in 90 Sekunden nicht zurück bin, zieht ihr ohne mich."

### Turn 20 — SL

Die Gasse steht still. Blitz' Hand liegt an der Schulter des Kuriers. Astra einen halben Schritt davor.

Zehn Sekunden.

*„Wer sitzt da oben."*

Der Kurier schaut sie an. Dann — zum ersten Mal — schaut er weg. Kurz. Zur Seite, nicht nach oben.

Das ist keine Lüge. Das ist jemand, der abwägt ob die Antwort ihn schützt oder gefährdet [2].

*„Ich kenne keinen Namen. Ich kenne ein Gesicht."*

Pause.

*„Jemand der früher für dieselbe Organisation gearbeitet hat wie ihr. Der vor langer Zeit aufgehört hat."*

Er schaut Astra direkt an.

*„Das war alles was ich wissen sollte."*

`Kodex: Kurier-Aussage — plausibel, unvollständig. Hinweis: Fotograf ist Ex-ITI oder Ex-KAIROS. Bilder möglicherweise bereits übertragen.`

---

Dusk hat recht. Ein Profi mit Teleobjektiv überträgt live — die Bilder sind wahrscheinlich bereits weg. Das Fenster ist dunkel jetzt. Kein Vorhang mehr.

Echo ist bereits drei Schritte Richtung Gebäudeeingang.

Astra schaut ihn an. Dann zu Dusk.

`Kodex: Meridian-Kontrollraum — Loop-Break vor ~90 Sekunden. Erster Techniker-Check in ~30 Sekunden.`

---

`EP 13 · MS 1 · SC 06/12 · PHASE Konflikt · MODE CORE · COMMS OK · Px 3/5 · Obj: Exfil mit Kurier · Exfil: T-offen`

`Astra LP 20/20 · Blitz LP 26/26 · Cipher LP 19/19 · Dusk LP 21/21 · Echo LP 20/20`
`Stress 0/10 alle · Heat 1/5`

👁️ **Tarnstatus: Offen — 30 Sekunden bis Meridian-Check**

`Kodex: Szene 6 läuft — Entscheidung jetzt.`

---

Zwei Wege. Beide haben Konsequenzen.

**Echo geht rauf** — zwei Minuten, vielleicht Fotograf, vielleicht leeres Zimmer, vielleicht Konfrontation. Meridian läuft in dreißig Sekunden live auf dieser Gasse. Wenn Echo oben hängt, zieht die Crew ohne ihn oder wartet und riskiert Heat 2.

**Exfil jetzt** — Kurier gesichert, Paket gesichert, Fotograf-Identität offen. Ex-ITI oder Ex-KAIROS, Gesicht ohne Namen. Das ist ein Faden, kein Abschluss. Aber ein lebendiger Faden.

---

**Astra entscheidet — jetzt:**

1. **Echo geht rauf, Rest bereitet Exfil vor** — 90 Sekunden, Rendezvous a

**SPIELER-EINGABEN:**

**Astra** [Petra]: Echo, stop.

Wir haben dreißig Sekunden, keinen Namen und einen Fotografen der möglicherweise schon längst weg ist. Das Gesicht im Kopf des Kuriers ist wertvoller als ein leeres Zimmer.

Option 3 — Dusk, kurzer Scan, jetzt. Danach alle raus.

**Blitz** [Marco]: Echo, lass es. Wir haben den Kurier — das ist genug für heute. Raus hier, bevor Meridian uns einsackt.

**Cipher** [Lena]: Echo, wart kurz. Wenn der Typ Ex-ITI ist, hab ich vielleicht was in der Datenbank. Dreißig Sekunden die ich brauche um Meridian blind zu machen — oder dreißig Sekunden die Echo oben vergeudet. Ich bin für Option 2, aber ich will Dusks Scan zuerst.

**Dusk** [Tarek]: Echo, warte.

Dreißig Sekunden, ein Zimmer das vielleicht leer ist — das ist kein guter Tausch. Wir nehmen den Faden und gehen.

**Echo** [Sven]: „Ich geh rauf. Zwei Minuten, nicht mehr. Wenn ich nicht unten bin — fahrt ohne mich."

### Turn 21 — SL

Der Faden zieht Echo nach oben. Aber Astra ist schneller mit dem Wort.

*„Echo. Stop."*

Keine Diskussion. Drei Leute sagen dasselbe — Dusk, Blitz, Cipher. Echo steht an der Gebäudetür, Hand am Rahmen. Er schaut kurz nach oben. Dann lässt er los.

*„Verstanden."*

`Kodex: Psi-Probe-Template — Dusk · Präkognitiver Blick / Scan · 1W6 + ⌊TEMP/2⌋. TEMP 6 → W6 (Basis < 11). SG 7 — Kurier kooperiert, direkter Kontakt möglich. Psi-Kosten: 1 PP, 0 SYS (Impuls).`

Dusk tritt einen Schritt näher an den Kurier. Kein Theater — er schaut ihn einfach an. Eine Sekunde, vielleicht zwei.

Probe: Psi-Scan → W6: [4] + ⌊6/2⌋ (3) + 1 PP = **7 vs SG 7 → ERFOLG** [2]

`Kodex: Psi-Scan — 1 PP, 0 SYS (Impuls). Dusk PP: 4 → 3. Psi-Heat: 0 → 1.`

---

Ein Bild. Kurz, unscharf an den Rändern — wie eine Fotografie die zu lange in der Sonne lag.

Ein Mann. Älter, Sechzig vielleicht. Kurzes graues Haar, Narbe am Kinn, linkes Ohr leicht abstehend. Keine Uniform, keine Kennung — aber die Art wie er steht sagt alles. Jemand der Befehle gewohnt ist. Jemand der sie auch gegeben hat.

Und etwas anderes. Schwächer, am Rand des Bildes — eine Zahl. Oder eine Buchstabenfolge. Dusk hat sie nicht vollständig, nur den Anfang.

*„K-7."*

`Kodex: Psi-Echo — Fotograf: männlich, ~60, graues Haar, Kinn-Narbe. Haltung: militärisch, Führungsstruktur. Fragment: K-7 — unvollständige Kennung oder Codesegment.`

---

Dusk tritt zurück. Schaut Astra an. Sagt nichts laut — tippt einmal kurz ins Comlink.

*„K-7. Mehr hab ich nicht."*

`Kodex: Meridian-Kontrollraum — Loop-Break vor ~2:10 Min. Techniker-Check überfällig.`

---

`EP 13 · MS 1 · SC 07/12 · PHASE Konflikt · MODE CORE · COMMS OK · Px 3/5 · Obj: Exfil mit Kurier · Exfil: T-offen`

`Astra LP 20/20 · Blitz LP 26/26 · Cipher LP 19/19 · Dusk LP 21/21 · Echo LP 20/20`
`Stress 0/10 alle · Heat 1/5`

`Dusk PP 3/4 · Psi-Heat 1/5`

👁️ **Tarnstatus: Offen — Meridian-Check überfällig. K-7 als Fragment gesichert.**

`Kodex: Szene 7 — Seitengasse Mariahilfer Straße · 14:17 Uh

**SPIELER-EINGABEN:**

**Astra** [Petra]: K-7 ist eine Kennung — ex-militärisch, Führungsebene, alt genug um zu wissen wie man Spuren legt. Das Paket war Köder oder Beweis, beides ist möglich. Cipher, du kriegst dreißig Sekunden im Aufzugsschacht — aber wir öffnen das nicht hier draußen. Exfil. Los.

**Blitz** [Marco]: „Aufzug. Jetzt. Kurier kommt mit — solange wir nicht wissen wer K-7 ist, ist er unser einziger Faden."

**Cipher** [Lena]: „K-7 läuft durch meine Datenbank — nichts. Paket öffnen kostet uns Zeit die wir nicht haben. Aufzugsschacht, Kurier kommt mit, wir reden unterwegs."

**Dusk** [Tarek]: „K-7 war der Auftraggeber, nicht der Fotograf. Ich bin nicht sicher — aber das Bild hat sich so angefühlt."

**Echo** [Sven]: „Aufzugsschacht. Kurier kommt mit — er ist noch nicht fertig mit uns."

### Turn 22 — SL

`Kodex: Exfil-Fenster — IA Güteraufzugsschacht B2 · RW armierbar, Weg ~90 Sekunden. Standard-Fenster offen.`

Alle fünf bewegen sich. Kein Wort mehr — die Gasse ist noch leer, aber das ändert sich.

---

Blitz schiebt den Kurier vor sich her, nicht grob, aber ohne Spielraum. Der Mann geht mit — keine Gegenwehr, keine Verzögerung. Er weiß, dass seine Karte gespielt ist.

Dusk deckt den Rücken. Echo hat die Gassenöffnung bereits hinter sich gelassen, Comlink-Modul an der Hüfte, Signal hält. Cipher läuft neben Astra, Augen auf die Gebäudefronten.

Das Fenster im zweiten Obergeschoss ist dunkel.

`Kodex: Meridian-Kontrollraum — Loop-Break vor ~3 Min. Kein Alarm ausgelöst bisher. Heat: 1/5 — stabil.`

---

Der Güteraufzugsschacht öffnet sich wie er sie empfangen hat — Backsteinwände, Schmieröl, Kalkstaub. Die Schienen rosten im Dunkeln. Über dem Gitter das gedämpfte Rauschen des Bahnhofs, jetzt leiser.

Der Kurier schaut sich um. Zum ersten Mal wirkt er nicht mehr ganz so ruhig.

*„Wo geht das hin?"*

Blitz antwortet nicht.

`EP 13 · MS 1 · SC 08/12 · PHASE Exfil · MODE CORE · COMMS OK · Px 3/5 · Obj: Rücksprung · Exfil: T-aktiv`

`Astra LP 20/20 · Blitz LP 26/26 · Cipher LP 19/19 · Dusk LP 21/21 · Echo LP 20/20`
`Stress 0/10 alle · Heat 1/5 · Dusk PP 3/4 · Psi-Heat 1/5`

`Kodex: Szene 8 — Güteraufzugsschacht B2 · 14:19 Uhr.`

---

Cipher hat dreißig Sekunden. Das Paket liegt in Blitz' Hand. Magnetverschluss, KAIROS-Kennung, Anker-Null.

Astra schaut einmal kurz auf Blitz. Dann auf das Paket.

*„Dreißig Sekunden. Mach es auf."*

`Kodex: Probe-Template — Cipher · Technik / Magnetverschluss-Analyse · 1W6 + ⌊INT/2⌋ + Talent + Gear.`
`Kodex: INT 8 → W6 (Basis < 11). Feldroutine +1. Override-Kit T2 +2. SG 6 — kein Sicherheitssystem, nur mechanischer Verschluss.`

Probe: Paket öffnen → W6: [3] + ⌊8/2⌋ (4) + Feldroutine 1 + Override-Kit 2 = **10 vs SG 6 → ERFOLG** [5]

Der Magnetverschluss springt auf. Cipher zieht den Deckel zurück.

---

Kein Datenträger. Kein Chip. Kein Code

**SPIELER-EINGABEN:**

**Astra** [Petra]: Omega. K-7. Er weiß mehr als er glaubt — frag ihn, woher er das Paket hatte. Wer hat ihn beauftragt, und wie?

**Blitz** [Marco]: „Omega — kennst du den Namen? Ja oder nein, schnell."

**Cipher** [Lena]: „Omega und K-7 — sagt dir einer von beiden was? Zehn Sekunden."

**Dusk** [Tarek]: Er wusste es nicht — heißt, er ist nur ein Glied. Nehmt ihn mit, aber haltet ihn ruhig. Wenn K-7 schon läuft, brauchen wir jeden Faden.

**Echo** [Sven]: Ich nehm den Zettel — Foto, dann Original ins Kit. Kurier kommt mit, zumindest bis Basis. Wenn er wirklich nichts wusste, kostet uns das nichts. Wenn doch, wollen wir ihn dabeihaben.

### Turn 23 — SL

Der Schacht riecht nach Schmieröl und Kalkstaub. Irgendwo über ihnen rauscht der Bahnhof weiter.

Blitz hält den Kurier, Echo fotografiert den Zettel mit dem Feld-Toolkit, legt das Original zurück ins Paket. Drei Sekunden.

Dann schaut Astra den Kurier an.

*„Woher hattest du das Paket. Wer hat dich beauftragt, und wie."*

Keine Drohung im Ton. Nur die Frage.

Der Kurier atmet einmal aus. Er schaut auf den Zettel in Echos Hand — auf das Omega-Symbol. Sein Gesicht sagt, dass er es zum ersten Mal richtig wahrnimmt.

*„Toter Briefkasten in Bratislava. Vor vier Tagen. Umschlag mit Adresse, Schlüssel, Zeitfenster — alles drin. Kein Name, kein Kontakt, kein Rückkanal."*

Er schaut Astra direkt an.

*„Bezahlt wurde im Voraus. Krypto, nicht rückverfolgbar. Das ist alles was ich habe."*

`Kodex: Kurier-Aussage — Bratislava, toter Briefkasten, 4 Tage alt. Bezahlung Krypto, anonym. Kein Auftraggeber-Kontakt. Plausibel konsistent mit Kurier-Profil.`

---

Dusk steht an der Wand. Er hört zu, sagt nichts. Dann, leise ins Comlink:

*„Bratislava. Das ist nicht spontan — das war geplant, bevor wir überhaupt wussten dass es ein Paket gibt."*

Echo hat den Zettel bereits im Kit. Kurier steht ruhig, Blitz' Hand an der Schulter.

`Kodex: Sprung-Gate kalibriert — Rücksprung bereit. Fenster: offen.`
`Kodex: Meridian-Loop-Break vor ~4 Min. Noch kein Alarm — aber das Fenster schließt sich.`

---

`EP 13 · MS 1 · SC 08/12 · PHASE Exfil · MODE CORE · COMMS OK · Px 3/5 · Obj: Rücksprung · Exfil: T-aktiv`

`Astra LP 20/20 · Blitz LP 26/26 · Cipher LP 19/19 · Dusk LP 21/21 · Echo LP 20/20`
`Stress 0/10 alle · Heat 1/5 · Dusk PP 3/4 · Psi-Heat 1/5`

`Kodex: Szene 8 — Güteraufzugsschacht B2 · 14:20 Uhr.`

---

Bratislava. Toter Briefkasten. Vier Tage Vorlauf. K-7 hat das geplant, bevor das ITI das Paket überhaupt auf dem Radar hatte.

Der Kurier ist ein Glied — das hat Dusk recht. Aber er ist ein Glied mit einer Adresse. Bratislava. Toter Briefkasten. Das ist der nächste Faden.

Das Omega-Symbol l

**SPIELER-EINGABEN:**

**Astra** [Petra]: Bratislava sagt mir genug. Er weiß nichts mehr als das.

Blitz, lass ihn laufen — und dann Gate, sofort.

**Blitz** [Marco]: „Bratislava liegt auf dem Tisch — der Typ weiß nix mehr, lass ihn laufen. Wir springen."

**Cipher** [Lena]: „Bratislava, vier Tage — das bedeutet K-7 hatte unsere Bewegungen schon im Vorfeld. Kurier lassen wir laufen, der hat nichts mehr. Rücksprung."

**Dusk** [Tarek]: *„Bratislava kostet uns nichts extra — lass ihn laufen. Wir haben den Faden, wir brauchen nicht das ganze Knäuel."*

**Echo** [Sven]: „Kurier laufen lassen. Er hat gegeben was er hat — mehr ist da nicht."

Kurze Pause.

„Bratislava klären wir selbst. Gate auf."

### Turn 24 — SL

Blitz lässt die Schulter des Kuriers los. Einen Schritt zurück. Keine Worte.

Der Kurier schaut die Runde an — fünf Gesichter, alle sagen dasselbe. Er nickt einmal, kurz, und geht. Keine Hast. Die Schritte verlieren sich Richtung Bahnhofsausgang.

Er dreht sich nicht um.

`Kodex: Kurier freigelassen. Opt.-Ziel Kurier: ✗ — bewusste Entscheidung, kein Debrief-Abzug.`

---

Die Crew steht im Schacht. Backsteinwände, Schmieröl, das gedämpfte Rauschen des Bahnhofs über dem Gitter. Echo hat das Comlink-Modul bereits in der Hand — Signal hält, schwach aber stabil.

Astra schaut einmal kurz auf das Paket in Blitz' Hand. Dann auf die Runde.

*„Gate auf."*

Das Sprung-Gate-Array summt. Die Koordinaten sind noch geladen — Nullzeit, ITI, Güteraufzugsschacht B2 als Rückkehrpunkt. Der Schacht riecht nach Kalkstaub und einer Entscheidung, die gerade getroffen wurde.

Fünf Agenten. Ein schwarzes Paket. Ein Omega-Symbol. Ein Name — K-7. Eine Stadt — Bratislava, vier Tage alt.

*Rücksprung.*

`Kodex: Rücksprung abgeschlossen. Debrief läuft.`

---

`EP 13 · MS 1 · SC --/-- · PHASE Debrief · MODE CORE · COMMS OK · Px 3/5`

`Astra LP 20/20 · Blitz LP 26/26 · Cipher LP 19/19 · Dusk LP 21/21 · Echo LP 20/20`
`Stress 0/10 alle · Heat 1/5 · Dusk PP 3/4 · Psi-Heat 1/5`

---

## DEBRIEF — Episode 13, Mission 1

**Score-Screen:**

*Hauptziel:* Paket aus Schließfach 7-C sichern ✓
*Opt.:* Kurier lebend festnehmen ✗ — bewusste Entscheidung, Faden bleibt offen
*Bonus:* Schließfachhalle unbemerkt verlassen, keine Kamera-Kompromittierung ✓

**Bewertung: Sauber.** Hauptziel und Bonus erreicht, Opt. bewusst geopfert für taktische Information. Kein Alarm, kein direkter Kontakt mit Meridian-Security.

---

**Loot-Recap:**

- KAIROS-Datenpaket — Inhalt: handgeschriebene Nachricht, Omega-Stempel
- Psi-Echo Fragment: K-7 — männlich, ~60, graues Haar, Kinn-Narbe, militärische Führungsstruktur
- Intel: Bratislava, toter Briefkasten, 4 Tage Vorlauf
- Intel: Anker-Null = Ort, kein Code

---

**CU-Auszahlung:**

## Zusammenfassung

**Ende-Grund:** Stop-Hint: PHASE Debrief
**Turns:** 24
**Tokens gesamt:** 2043261 (Prompt: 2012558, Completion: 30703)
**Peak Prompt:** 101236 tokens (39.5% von Sonnet-4.6-256k)
**Ø Latenz pro Turn:** 36.6s
**CSV:** `_tokens.csv` (turn,prompt,completion,total,cum,latency,chars)

**Findings (2):**
- [WALLET-KAUF] Kauf aus Wallet erkannt — Beat (a) gezündet (manuell prüfen)
- [WALLET-UEBERGABE] CU-Übergabe erkannt — Beat (b) gezündet (manuell prüfen)


