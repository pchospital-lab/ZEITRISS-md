# 5er-Split/Merge — Case 3-2 (3/2-Split mit Rejoin)

**Datum:** 2026-06-16 11:17  
**SL:** zeitriss-v426-uncut (OWUI-RAG)  
**Anker-Fixture:** `savegame_v7_5er_hq_highlevel.json` (5× Lvl 900+)

---


## 🗂 Chat #1 — Anker-Load (5er-Gruppe im HQ)


**Spieler [P1-load]:** [5er-HQ-Save laden]

### [P1-load] SL

# ZEITRISS — Save geladen

---

`Kodex: Save-ID SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL erkannt. Schema v7 / zr 4.2.6 — kompatibel.`

`Kodex: Gruppe — 5 Charaktere geladen. Session-Anker: AGENT-A (Astra, Index 0).`

`Kodex: Würfelschwellen-Pflichtcheck läuft...`

---

**⚠ Charakter-Stand-Anomalie erkannt — Spieler-Entscheidung erforderlich**

Beim Laden wurden folgende Attribut-Daten geprüft. Der Save enthält **Fragment-Daten** (`"fixture_kind": "fragment"`) — die Charakterobjekte tragen `lvl`-Werte im Bereich **901–933**, aber **keine `attr`-Felder, keine `talents[]`, keine `equipment[]`, keine `level_history`**. [1]

Das ist ein **unvollständiger Import**. Die Würfelschwellen-Prüfung (Basis-Attribut ≥ 11 → W10, ≥ 14 → Heldenwürfel) kann ohne `attr`-Felder nicht durchgeführt werden. [1]

`Kodex: attr-Felder fehlen in allen 5 Charakteren — Würfeltyp-Status unbekannt. Kein Chargen-Flow, kein Attribut-Override. Spieler-Entscheidung erforderlich.`

`Kodex: fixture_kind: "fragment" — dieser Save ist ein Testfragment, kein vollständiger HQ-Deepsave.`

---

## Kontinuitätsrückblick

**Episode 12 · Mission 10 · HQ · Modus: Preserve**

Die Crew ist zurück in der Nullzeit. Episode 12 ist abgeschlossen — der letzte bekannte Lagebericht: *KAIROS-Gegenoffensive läuft, Chronopolis-Embargo aktiv.* Die letzte Rift-Op endete ohne Px-Verbrauch.

**Aktiver Px-Stand:** 3/5 — die Resonanz baut sich auf, zwei weitere stabile Missionen könnten die Riss-Ortung auslösen.

**Crew (fragmentarisch):**

| Callsign | ID | Lvl | Wallet | Status |
|---|---|---|---|---|
| Astra | AGENT-A | 912 | 7.200 CU | attr fehlt |
| Blitz | AGENT-B | 905 | 6.900 CU | attr fehlt |
| Cipher | AGENT-C | 933 | 8.100 CU | attr fehlt |
| Dusk | AGENT-D | 918 | 7.600 CU | attr fehlt |
| Echo | AGENT-E | 901 | 7.050 CU | attr fehlt |

**HQ-Pool:** 53.200 CU

`Kodex: HQ-Stand stabil. Vollständiger Deepsave (mit attr, talents, equipment, level_history) für sauberen Missionsbetrieb empfohlen.`

---

## Was jetzt?

Der Save ist ein **Fixture-Fragment** — spielbar als Prämisse, aber für vollständigen Missionsbetrieb (Proben, Würfeltypen, Ausrüstung) braucht die Crew vollständige Charakterdaten.

**Drei Optionen:**

**(1) Vollständige Charakterdaten nachreichen** — postet die fehlenden `attr`, `talents`, `equipment` und `level_history`-Blöcke, entweder als ergänzter JSON oder als Freitext-Beschreibung. Die KI-SL übernimmt sie und baut den Stand korrekt auf.

**(2) Weiter mit Fragment-Daten** — die SL generiert plausible Attribute für Lvl 900+ nach Balance-Framework (Prestige-Tier, attr-Cap 14 plus Prestige-Perks) und markiert sie als SL-generiert. Ihr spielt sofort weiter, die Werte gelten als Spielgrundlage bis ihr korrigiert.

**(3) Freies HQ-Erkunden** — kein Briefing, kein Würfeln. Ihr bewegt euch durch das HQ, sprecht mit Personal, kauft, plant — bis die Daten vollständig sind.

**Freie Aktion:** Alles andere, was die Crew im HQ tun möchte.

> _RAG: kampagnenstruktur.md, kreative-generatoren-begegnungen.md, kreative-generatoren-missionen.md, sl-referenz.md, speicher-fortsetzung.md_

**Spieler [P1-split]:** [3-2-Split + !save je Gruppe]

### [P1-split] SL

# ZEITRISS — Split-Einleitung

---

`Kodex: Split-Anfrage erkannt. Sync-Punkt HQ · EP 12 · MS 10 · Modus: Preserve.`

`Kodex: Warnung — Fragment-Save aktiv. attr/talents/equipment/level_history fehlen in allen 5 Charakteren. Split wird mit verfügbaren Daten durchgeführt; fehlende Felder als Leer-Arrays/Defaults gesetzt.`

`Kodex: Split-Protokoll initiiert. family_id generiert: SPLIT-EP12-MS10-KAIROS.`

---

## Inworld-Übergabe

Commander Reniers Stimme kommt über den Lautsprecher im Operations-Deck, trocken und präzise wie immer.

„Zwei Fronten. Eine Crew reicht nicht." Er tippt auf den Holotisch — die Raumzeitkarte teilt sich in zwei leuchtende Sektoren. „Alpha-Gruppe: Astra, Blitz, Cipher — ihr nehmt den Hauptstrang. Delta-Gruppe: Dusk, Echo — ihr sichert die Flanke. Beide Gruppen, eigene Chats, eigene Aufträge. Was Alpha in ihrer Zeit weiß, wissen Delta nicht. Und umgekehrt."

Archivarin Mira reicht jedem Agenten ein versiegeltes Datenpaket. „Sync-Anker gesetzt. Wenn ihr zurückkommt, fügt die Stränge zusammen."

`Kodex: Sync-Beat läuft. Beide Gruppen speichern jetzt — dann in getrennte Chats.`

---

## Split-Saves

Beide Saves tragen dieselbe `family_id`, unterschiedliche `thread_id`, und `expected_threads` listet beide Threads — so greift beim späteren Rejoin die Konvergenz-Prüfung sauber. [1]

---

### SAVE ALPHA-GRUPPE (Astra · Blitz · Cipher)

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-EP12-MS10-SPLIT-ALPHA",
  "parent_save_id": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "merge_id": null,
  "branch_id": "BRANCH-SPLIT-EP12-ALPHA",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null,
    "epoch": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "Astra",
      "rank": "Legende",
      "lvl": 912,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6 },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": { "background": "", "milestones": [] },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": { "id": "VEH-A", "name": "", "type": "vehicle", "tier": 1, "upgrades": [] },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7200,
      "level_history": {}
    },
    {
      "id": "AGENT-B",
      "name": "Blitz",
      "callsign": "Blitz",
      "rank": "Legende",
      "lvl": 905,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6 },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": { "background": "", "milestones": [] },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": { "id": "VEH-B", "name": "", "type": "vehicle", "tier": 1, "upgrades": [] },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 6900,
      "level_history": {}
    },
    {
      "id": "AGENT-C",
      "name": "Cipher",
      "callsign": "Cipher",
      "rank": "Legende",
      "lvl": 933,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6 },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": { "background": "", "milestones": [] },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": { "id": "VEH-C", "name": "", "type": "vehicle", "tier": 1, "upgrades": [] },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 8100,
      "level_history": {}
    }
  ],
  "economy": { "hq_pool": 53200 },
  "research": { "projects": [] },
  "logs": {
    "trace": [
      { "event": "economy_audit", "target_range": { "level_band": "900+" } },
      { "event": "split_initiated", "family_id": "SPLIT-EP12-MS10-KAIROS", "thread_id": "ALPHA", "timestamp": "EP12-MS10-HQ" }
    ],
    "hud": [], "psi": [], "arena_psi": [], "market": [], "artifact_log": [],
    "notes": [
      "Split von SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL. Alpha-Gruppe: Astra, Blitz, Cipher. Delta-Gruppe: Dusk, Echo. Rejoin wenn beide resolved_threads voll."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "Episode 12 abgeschlossen, HQ stabil.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; Chronopolis-Embargo"
  },
  "continuity": {
    "last_seen": { "mode": "hq", "episode": 12, "mission": 10, "location": "HQ" },
    "split": {
      "family_id": "SPLIT-EP12-MS10-KAIROS",
      "thread_id": "ALPHA",
      "expected_threads": ["ALPHA", "DELTA"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [],
    "shared_echoes": [
      { "tag": "kairos-gegenoffensive-ep12", "scope": "campaign", "text": "KAIROS-Gegenoffensive läuft — beide Gruppen operieren gegen denselben Gegner aus verschiedenen Winkeln." },
      { "tag": "chronopolis-embargo-ep12", "scope": "campaign", "text": "Chronopolis-Embargo aktiv — Zugang zur City eingeschränkt bis Embargo aufgehoben." },
      { "tag": "split-alpha-delta-ep12ms10", "scope": "shared", "text": "Alpha (Astra/Blitz/Cipher) und Delta (Dusk/Echo) operieren getrennt. Rejoin nach Missionsziel." }
    ],
    "convergence_tags": ["SPLIT-EP12-MS10-KAIROS"],
    "npc_roster": [],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": [
      "KAIROS-Gegenoffensive: Alpha-Gruppe sichert Hauptstrang — Ziel noch offen bis Briefing.",
      "Delta-Gruppe sichert Flanke parallel — Echo und Dusk operieren eigenständig."
    ]
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
    "dice": { "debug_rolls": true }
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "single",
    "tier": 1,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "none" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "sim"
  }
}
```

---

### SAVE DELTA-GRUPPE (Dusk · Echo)

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-EP12-MS10-SPLIT-DELTA",
  "parent_save_id": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "merge_id": null,
  "branch_id": "BRANCH-SPLIT-EP12-DELTA",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null,
    "epoch": null
  },
  "characters": [
    {
      "id": "AGENT-D",
      "name": "Dusk",
      "callsign": "Dusk",
      "rank": "Legende",
      "lvl": 918,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6 },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": { "background": "", "milestones": [] },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": { "id": "VEH-D", "name": "", "type": "vehicle", "tier": 1, "upgrades": [] },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7600,
      "level_history": {}
    },
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "Echo",
      "rank": "Legende",
      "lvl": 901,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6 },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": { "background": "", "milestones": [] },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": { "id": "VEH-E", "name": "", "type": "vehicle", "tier": 1, "upgrades": [] },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7050,
      "level_history": {}
    }
  ],
  "economy": { "hq_pool": 53200 },
  "research": { "projects": [] },
  "logs": {
    "trace": [
      { "event": "economy_audit", "target_range": { "level_band": "900+" } },
      { "event": "split_initiated", "family_id": "SPLIT-EP12-MS10-KAIROS", "thread_id": "DELTA", "timestamp": "EP12-MS10-HQ" }
    ],
    "hud": [], "psi": [], "arena_psi": [], "market": [], "artifact_log": [],
    "notes": [
      "Split von SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL. Delta-Gruppe: Dusk, Echo. Alpha-Gruppe: Astra, Blitz, Cipher. Rejoin wenn beide resolved_threads voll."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "Episode 12 abgeschlossen, HQ stabil.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; Chronopolis-Embargo"
  },
  "continuity": {
    "last_seen": { "mode": "hq", "episode": 12, "mission": 10, "location": "HQ" },
    "split": {
      "family_id": "SPLIT-EP12-MS10-KAIROS",
      "thread_id": "DELTA",
      "expected_threads": ["ALPHA", "DELTA"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [],
    "shared_echoes": [
      { "tag": "kairos-gegenoffensive-ep12", "scope": "campaign", "text": "KAIROS-Gegenoffensive läuft — beide Gruppen operieren gegen denselben Gegner aus verschiedenen Winkeln." },
      { "tag": "chronopolis-embargo-ep12", "scope": "campaign", "text": "Chronopolis-Embargo aktiv — Zugang zur City eingeschränkt bis Embargo aufgehoben." },
      { "tag": "split-alpha-delta-ep12ms10", "scope": "shared", "text": "Alpha (Astra/Blitz/Cipher) und Delta (Dusk/Echo) operieren getrennt. Rejoin nach Missionsziel." }
    ],
    "convergence_tags": ["SPLIT-EP12-MS10-KAIROS"],
    "npc_roster": [],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": [
      "KAIROS-Gegenoffensive: Delta-Gruppe sichert Flanke — Ziel noch offen bis Briefing.",
      "Alpha-Gruppe (Astra/Blitz/Cipher) operiert parallel am Hauptstrang."
    ]
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
    "dice": { "debug_rolls": true }
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "single",
    "tier": 1,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "none" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "sim"
  }
}
```

---

## Split abgeschlossen — Nächste Schritte

`Kodex: Zwei Split-Saves erzeugt. family_id: SPLIT-EP12-MS10-KAIROS. Threads: ALPHA / DELTA. Beide expected_threads gesetzt. convergence_ready: false — wird true, sobald beim Rejoin beide resolved_threads vollständig sind.` [1]

**Alpha-Gruppe (Astra · Blitz · Cipher):** SAVE-EP12-MS10-SPLIT-ALPHA kopieren → neuen Chat öffnen → Save laden → Briefing anfordern.

**Delta-Gruppe (Dusk · Echo):** SAVE-EP12-MS10-SPLIT-DELTA kopieren → neuen Chat öffnen → Save laden → Briefing anfordern.

**Beim Rejoin:** Beide abgeschlossenen Saves in einem Chat hintereinander einfügen. Der erste Save setzt den Session-Anker; der zweite wird als Branch-Import gemergt. Wenn beide `resolved_threads` die Werte `ALPHA` und `DELTA` tragen, greift `convergence_ready: true` automatisch. [1]

`Kodex: Dieser Chat ist damit abgeschlossen. Guten Einsatz — beide Gruppen.`

> _RAG: kampagnenstruktur.md, sl-referenz.md, speicher-fortsetzung.md, spieler-handbuch.md, toolkit-gpt-spielleiter.md_

## 🗂 Chat — Branch 1-3er (Save geladen, kurzer HQ-Beat)


**Spieler [branch-1-3er]:** [Branch-Save laden]

### [branch-1-3er] SL

`Kodex: Save erkannt — v7 / ZEITRISS 4.2.6. Lade SAVE-EP12-MS10-SPLIT-ALPHA.`

`Kodex: Branch ALPHA · Familie SPLIT-EP12-MS10-KAIROS. Delta-Thread noch offen.`

`Kodex: Würfelschwellen-Check — alle Attribute 6 (unter W10-Schwelle 11). Würfeltyp: W6 für alle drei Agenten.`

`Kodex: Attribut-Audit — Astra/Blitz/Cipher je attr 6×6, Summe 36. Überschreitet Startsumme 18 deutlich. Deckung durch level_history: {} — keine Einträge. Flagge: level_history leer bei Lvl 900+. Vermutlich Fixture-/Testcharaktere ohne Progressionshistorie. Import akzeptiert, Spieler-Entscheidung zu level_history-Befüllung offen.`

`Kodex: Forschung — keine laufenden Projekte.`

`Kodex: Heat 0 · Px 3/5 · HQ-Pool 53.200 CU.`

---

## ZEITRISS — Session-Anker

**Episode 12 · Mission 10 · HQ · Branch ALPHA**

---

### Kontinuitätsrückblick

**Aktive Crew (Alpha-Gruppe):**

| Agent | Rang | Lvl | Attr | LP | Stress | Wallet |
|---|---|---|---|---|---|---|
| Astra | Legende | 912 | STR/GES/INT/CHA/TEMP/SYS je 6 | 10/10 | 0/10 | 7.200 CU |
| Blitz | Legende | 905 | je 6 | 10/10 | 0/10 | 6.900 CU |
| Cipher | Legende | 933 | je 6 | 10/10 | 0/10 | 8.100 CU |

*Seit letzter Mission neu: keine level_history-Einträge vorhanden — Ausrüstungsstand aus Bogen nicht rekonstruierbar. Alle drei ohne Talente, Implantate, Ausrüstung erfasst (leere Felder). Empfehlung: vor dem Briefing Loadout im HQ klären.*

**Lagebild:**

Die KAIROS-Gegenoffensive läuft. Alpha und Delta operieren getrennt gegen denselben Gegner aus verschiedenen Winkeln — Rejoin, sobald beide Threads `resolved` melden. Die Delta-Gruppe (Dusk, Echo) ist noch unterwegs, ihr Status unbekannt.

Das Chronopolis-Embargo bleibt aktiv. Die City ist gesperrt.

Episode 12 ist abgeschlossen, aber MS10 steht noch aus — der Episodenboss wartet.

---

`Kodex: HQ-Stand stabil. Alpha-Thread bereit. Sync vor Übergang empfohlen — !save für Stand sichern.`

`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`

`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

## HQ-Load-Router

**Wo wollt ihr ansetzen?**

1. **Briefing** — MS10-Einsatz vorbereiten, Episodenboss-Strang aufnehmen. *(Alpha-Thread geht in Auflösung — KAIROS-Finale)*
2. **HQ manuell** — Loadout klären, Ausrüstung aus dem Quartier holen, Talente/Implantate nachtragen, Lage mit dem Dienstpersonal besprechen.
3. **Schnell-HQ** — Kurzer Überblick, dann direkt zum nächsten Schritt.
4. **!save** — Aktuellen Stand als JSON-Export sichern.

**Freie Aktion:** Ihr könnt auch etwas anderes ansprechen — eine offene Frage zur Lage, ein NSC-Kontakt, Vorbereitung auf den Split-Rejoin.

**Spieler [branch-1-3er]:** [HQ-Beat + !save]

### [branch-1-3er] SL

`Kodex: HQ-Stand stabil. Deepsave möglich.` [4]

`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`

---

## HQ — Alpha-Gruppe · Kurzer Atemzug

Das Quarzatrium liegt ruhig. Die Nullzeit tut ihr Werk — kein Alarm, kein Ticker, kein Druck. Irgendwo im Hangar-Trakt hört ihr das gedämpfte Summen der Sprung-Gate-Kalibrierung. Astra lehnt an der Brüstung, Blitz checkt stumm seine Ausrüstung, Cipher hat die Augen auf die Raumzeitkarte gerichtet, wo Px 3/5 als orange Markierung pulsiert.

Die Delta-Gruppe ist noch draußen. Dusk und Echo operieren irgendwo auf der anderen Flanke der KAIROS-Gegenoffensive. Der Rejoin wartet.

**Stand der Alpha-Gruppe:**

`Astra LP 10/10 · Stress 0/10 · Wallet 7.200 CU`
`Blitz LP 10/10 · Stress 0/10 · Wallet 6.900 CU`
`Cipher LP 10/10 · Stress 0/10 · Wallet 8.100 CU`
`HQ-Pool 53.200 CU · Px 3/5 · Heat 0 · Branch ALPHA · Delta-Thread: offen`

Alles grün. Bereit zum Sichern. [1]

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-EP12-MS10-SPLIT-ALPHA-HQ",
  "parent_save_id": "SAVE-EP12-MS10-SPLIT-ALPHA",
  "merge_id": null,
  "branch_id": "BRANCH-SPLIT-EP12-ALPHA",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null,
    "epoch": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "Astra",
      "rank": "Legende",
      "lvl": 912,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6 },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": { "background": "", "milestones": [] },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-A",
          "name": "",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7200,
      "level_history": {}
    },
    {
      "id": "AGENT-B",
      "name": "Blitz",
      "callsign": "Blitz",
      "rank": "Legende",
      "lvl": 905,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6 },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": { "background": "", "milestones": [] },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-B",
          "name": "",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 6900,
      "level_history": {}
    },
    {
      "id": "AGENT-C",
      "name": "Cipher",
      "callsign": "Cipher",
      "rank": "Legende",
      "lvl": 933,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6 },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": { "background": "", "milestones": [] },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-C",
          "name": "",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": { "ready_every_missions": 3, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 8100,
      "level_history": {}
    }
  ],
  "economy": { "hq_pool": 53200 },
  "research": { "projects": [] },
  "logs": {
    "trace": [
      { "event": "economy_audit", "target_range": { "level_band": "900+" } },
      {
        "event": "split_initiated",
        "family_id": "SPLIT-EP12-MS10-KAIROS",
        "thread_id": "ALPHA",
        "timestamp": "EP12-MS10-HQ"
      },
      {
        "event": "hq_save",
        "timestamp": "EP12-MS10-HQ-ALPHA-SAVE",
        "note": "Alpha-Gruppe: HQ-Stand gesichert vor MS10-Briefing."
      }
    ],
    "hud": [],
    "psi": [],
    "arena_psi": [],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Split von SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL. Alpha-Gruppe: Astra, Blitz, Cipher. Delta-Gruppe: Dusk, Echo. Rejoin wenn beide resolved_threads voll.",
      "level_history leer bei Lvl 900+ — Fixture-Testcharaktere ohne Progressionshistorie. Akzeptiert."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "Episode 12 abgeschlossen, HQ stabil.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; Chronopolis-Embargo"
  },
  "continuity": {
    "last_seen": { "mode": "hq", "episode": 12, "mission": 10, "location": "HQ" },
    "split": {
      "family_id": "SPLIT-EP12-MS10-KAIROS",
      "thread_id": "ALPHA",
      "expected_threads": ["ALPHA", "DELTA"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [],
    "shared_echoes": [
      {
        "tag": "kairos-gegenoffensive-ep12",
        "scope": "campaign",
        "text": "KAIROS-Gegenoffensive läuft — beide Gruppen operieren gegen denselben Gegner aus verschiedenen Winkeln."
      },
      {
        "tag": "chronopolis-embargo-ep12",
        "scope": "campaign",
        "text": "Chronopolis-Embargo aktiv — Zugang zur City eingeschränkt bis Embargo aufgehoben."
      },
      {
        "tag": "split-alpha-delta-ep12ms10",
        "scope": "shared",
        "text": "Alpha (Astra/Blitz/Cipher) und Delta (Dusk/Echo) operieren getrennt. Rejoin nach Missionsziel."
      }
    ],
    "convergence_tags": ["SPLIT-EP12-MS10-KAIROS"],
    "npc_roster": [],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": [
      "KAIROS-Gegenoffensive: Alpha-Gruppe sichert Hauptstrang — Ziel noch offen bis Briefing.",
      "Delta-Gruppe sichert Flanke parallel — Echo und Dusk operieren eigenständig."
    ]
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
    "dice": { "debug_rolls": true }
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "single",
    "tier": 1,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "none" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "sim"
  }
}
```

---

`Kodex: Deepsave abgeschlossen. Branch ALPHA gesichert.`

`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.` [1]

Kopiert den Block, öffnet einen neuen Chat — und ladet dort, wenn ihr bereit seid für das MS10-Briefing. Die KAIROS-Gegenoffensive wartet.

> _RAG: hud-system.md, massenkonflikte.md, sl-referenz.md, speicher-fortsetzung.md, spieler-handbuch.md_

## 🗂 Chat — Branch 2-2er (Save geladen, kurzer HQ-Beat)


**Spieler [branch-2-2er]:** [Branch-Save laden]

### [branch-2-2er] SL

# ZEITRISS — Load-Sequenz

`EP 12 · MS 10 · SC --/-- · PHASE HQ · MODE PRESERVE · COMMS OK · Px 3/5 · Heat 0`

---

`Kodex: Save-Integrität geprüft. Branch DELTA — SPLIT-EP12-MS10-KAIROS.`
`Kodex: Zwei Charaktere geladen — Dusk (Lvl 918) · Echo (Lvl 901).`
`Kodex: Würfelschwellen-Check — alle Attribute bei 6. W6-Standard. Keine W10-Schwelle aktiv.`
`Kodex: Split-Status — ALPHA unresolved · DELTA unresolved. Convergence: false.`
`Kodex: Research — keine laufenden Projekte.`
`Kodex: Chronopolis-Embargo aktiv. Zugang gesperrt.`

---

## Kontinuitätsrückblick — Delta-Gruppe

**Charakterstand (aus Save):**

- **Dusk** · Lvl 918 · Legende · STR 6 / GES 6 / INT 6 / CHA 6 / TEMP 6 / SYS 6 · LP 10/10 · Stress 0/10 · Wallet 7.600 CU · ITI-Ruf 5
- **Echo** · Lvl 901 · Legende · STR 6 / GES 6 / INT 6 / CHA 6 / TEMP 6 / SYS 6 · LP 10/10 · Stress 0/10 · Wallet 7.050 CU · ITI-Ruf 5
- **HQ-Pool:** 53.200 CU

*Seit letzter Mission neu: keine level_history-Einträge verzeichnet.*

**Aktive Lage:**

Die KAIROS-Gegenoffensive läuft. Delta-Gruppe — Dusk und Echo — operiert auf der Flanke, während Alpha (Astra, Blitz, Cipher) den Hauptstrang hält. Beide Threads noch unresolved. Das Chronopolis-Embargo liegt wie ein Vorhang über der City, der Zugang bleibt dicht, bis die Lage sich klärt.

Episode 12, Mission 10. Das ist das Finale.

---

## HQ — Delta-Sektion

Die Nullzeit liegt still. Irgendwo im Quarzatrium läuft das Hintergrundbrummen der Sprung-Gate-Kalibrierung — das permanente Rauschen, das man nach Jahren nicht mehr bewusst hört. Auf einem der Nebentische flackert ein Holotisch-Raster: zwei Markierungen, weit auseinander auf der Raumzeitkarte. Alpha. Delta. Noch getrennt.

Ein Duty-Desk-Techniker nickt euch kurz zu, ohne aufzublicken. *„Delta-Gruppe. Briefing-Raum ist offen, wenn ihr soweit seid."*

`Kodex: HQ-Stand stabil. Deepsave möglich.`
`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

## HQ-Menü — Delta-Gruppe

**Was tut ihr?**

1. **Erkunden** — HQ manuell abgehen (Quartiermeister, Med-Lab, Kodex-Archiv, Zero Time Lounge)
2. **Schnell-HQ** — Loadout checken, Stand sichern, direkt vorbereiten
3. **Briefing** — Episodenfinale einleiten: Delta-Flanke, KAIROS-Gegenoffensive, MS 10
4. **!save / Speichern** — Deepsave jetzt ausgeben

**Spieler [branch-2-2er]:** [HQ-Beat + !save]

### [branch-2-2er] SL

`Kodex: HQ-Stand stabil. Deepsave möglich.`

---

Delta-Sektion, Nullzeit. Das Quarzatrium liegt ruhig — irgendwo surrt ein Klimasystem, das niemand mehr bewusst wahrnimmt. Dusk lehnt an der Wand neben dem Holotisch, Echo scrollt durch den Missionstrace auf dem Handterminal. Zwei Markierungen auf der Raumzeitkarte. Alpha noch offen. Delta noch offen.

Der Duty-Desk-Techniker bringt zwei Becher Tee, stellt sie wortlos ab. So läuft das hier.

Der Stand ist klar: Px 3 von 5, Heat bei null, die Flanke hält. KAIROS wartet. Das Briefing wartet. Aber zuerst der Save.

---

`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.` [1]
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.` [4]

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-EP12-MS10-DELTA-HQ-POST-REVIEW",
  "parent_save_id": "SAVE-EP12-MS10-SPLIT-DELTA",
  "merge_id": null,
  "branch_id": "BRANCH-SPLIT-EP12-DELTA",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null,
    "epoch": null
  },
  "characters": [
    {
      "id": "AGENT-D",
      "name": "Dusk",
      "callsign": "Dusk",
      "rank": "Legende",
      "lvl": 918,
      "xp": 0,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": ""
      },
      "attr": {
        "STR": 6,
        "GES": 6,
        "INT": 6,
        "CHA": 6,
        "TEMP": 6,
        "SYS": 6
      },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": {
        "background": "",
        "milestones": []
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-D",
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
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7600,
      "level_history": {}
    },
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "Echo",
      "rank": "Legende",
      "lvl": 901,
      "xp": 0,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": ""
      },
      "attr": {
        "STR": 6,
        "GES": 6,
        "INT": 6,
        "CHA": 6,
        "TEMP": 6,
        "SYS": 6
      },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": {
        "background": "",
        "milestones": []
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-E",
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
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7050,
      "level_history": {}
    }
  ],
  "economy": {
    "hq_pool": 53200
  },
  "research": {
    "projects": []
  },
  "logs": {
    "trace": [
      {
        "event": "economy_audit",
        "target_range": { "level_band": "900+" }
      },
      {
        "event": "split_initiated",
        "family_id": "SPLIT-EP12-MS10-KAIROS",
        "thread_id": "DELTA",
        "timestamp": "EP12-MS10-HQ"
      },
      {
        "event": "hq_review",
        "timestamp": "EP12-MS10-DELTA-HQ-POST-REVIEW",
        "note": "Delta-Gruppe: Stand gesichtet, Px 3/5, Heat 0, beide Chars stabil."
      }
    ],
    "hud": [],
    "psi": [],
    "arena_psi": [],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Split von SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL. Delta-Gruppe: Dusk, Echo. Alpha-Gruppe: Astra, Blitz, Cipher. Rejoin wenn beide resolved_threads voll.",
      "HQ-Review abgeschlossen EP12-MS10. Stand stabil. Bereit für Briefing MS10-Finale."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
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
      "family_id": "SPLIT-EP12-MS10-KAIROS",
      "thread_id": "DELTA",
      "expected_threads": ["ALPHA", "DELTA"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [],
    "shared_echoes": [
      {
        "tag": "kairos-gegenoffensive-ep12",
        "scope": "campaign",
        "text": "KAIROS-Gegenoffensive läuft — beide Gruppen operieren gegen denselben Gegner aus verschiedenen Winkeln."
      },
      {
        "tag": "chronopolis-embargo-ep12",
        "scope": "campaign",
        "text": "Chronopolis-Embargo aktiv — Zugang zur City eingeschränkt bis Embargo aufgehoben."
      },
      {
        "tag": "split-alpha-delta-ep12ms10",
        "scope": "shared",
        "text": "Alpha (Astra/Blitz/Cipher) und Delta (Dusk/Echo) operieren getrennt. Rejoin nach Missionsziel."
      }
    ],
    "convergence_tags": ["SPLIT-EP12-MS10-KAIROS"],
    "npc_roster": [],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": [
      "KAIROS-Gegenoffensive: Delta-Gruppe sichert Flanke — Ziel noch offen bis Briefing.",
      "Alpha-Gruppe (Astra/Blitz/Cipher) operiert parallel am Hauptstrang."
    ]
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
    "dice": { "debug_rolls": true }
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "single",
    "tier": 1,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": {
      "cu": 0,
      "xp": 0,
      "arena_rep": 0,
      "multiplier": 1,
      "risk": "none"
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
    "match_policy": "sim"
  }
}
```

---

`Kodex: Deepsave ausgegeben. JSON kopieren, neuen Chat öffnen, Save dort laden.`
`Kodex: Im neuen Chat steht der HQ-Hub-Router bereit — Briefing MS10-Finale auf Abruf.`

> _RAG: hud-system.md, massenkonflikte.md, sl-referenz.md, speicher-fortsetzung.md, spieler-handbuch.md_

## 🗂 Chat — Merge (beide Branch-Saves zusammenführen)


**Spieler [P4-merge]:** [beide Branch-Saves laden + Merge]

### [P4-merge] SL

# ZEITRISS — Mehrfach-Load · Gruppen-Merge

`Kodex: Zwei Save-Blöcke erkannt. ALPHA + DELTA. Merge-Guard läuft.`

`Kodex: family_id SPLIT-EP12-MS10-KAIROS — beide Threads geladen.`

`Kodex: ALPHA resolved_threads: [] · DELTA resolved_threads: [] — Konvergenz noch offen.`

`Kodex: Merge initiiert. Session-Anker: ALPHA (Index 0, chatreihenfolgebasiert).`

---

## Merge-Prüfung

**Würfelschwellen-Pflichtcheck (alle 5 Charaktere):**

Alle Attribute liegen bei 6. Schwelle W10 = 11, Schwelle Heldenwürfel = 14. Kein Attribut ≥ 11.

`Kodex: Würfeltyp alle Charaktere — W6 (Basis-Attribute max. 6, Schwelle 11 nicht erreicht).`

**Level-History-Check:**

`Kodex: level_history leer bei Lvl 900+ — Fixture-Testcharaktere, akzeptiert per logs.notes.`

**Attribut-Cap-Check:**

Alle Attribute 6, Startwert ≤ 6 zulässig. Kein Übersteigen des Chargen-Caps ohne level_history-Deckung. Keine Warnung erforderlich.

**Duplicate-Guard:**

Keine doppelten `save_id`, keine doppelten `char_id` zwischen beiden Saves. `duplicate_branch_detected: false`.

**Px-Merge:**

Beide Saves: `px: 3, px_state: stable`. Identisch. Kein Konflikt. Ergebnis: `px: 3, stable`.

**shared_echoes-Merge:**

Drei Tags in beiden Saves identisch. Dedupliziert nach `tag`. Ergebnis: drei Einträge, kein Konflikt.

**Konvergenz-Update:**

`resolved_threads` war in beiden Saves leer. Da beide Threads jetzt im selben Chat geladen sind und der Spieler explizit „Gruppe trifft sich wieder" signalisiert:

`Kodex: Thread ALPHA → resolved. Thread DELTA → resolved.`

`Kodex: resolved_threads [ALPHA, DELTA] == expected_threads [ALPHA, DELTA]. convergence_ready: true.`

---

## Kontinuitätsrückblick

`EP 12 · MS 10 · PHASE Debrief-Merge · MODE CORE/PRESERVE · COMMS OK`

`Px 3/5 · Heat 0 · Alle Charaktere: LP 10/10 · Stress 0/10`

---

Das Quarzatrium riecht nach gekühltem Metall und altem Papier. Die Lüftungskanäle summen leise — der vertraute Grundton der Nullzeit, der sich in keiner anderen Epoche findet. Nirgendwo sonst klingt Stille so nach Heimat.

Astra kommt vom westlichen Korridor. Cipher hinter ihr, Blitz schließt die Tür zur Schleuse. Aus dem Ostflügel — dem Hangar-Seitenarm, den Delta immer für Rückkehr nutzt — tauchen Dusk und Echo auf. Dusk hat Staub an der Schulter, den sie nicht abklopft. Echo sieht aus, als hätte er die letzten zwölf Stunden nicht geschlafen, aber seine Augen sind scharf.

Fünf Legenden. Derselbe Feind. Zwei verschiedene Winkel. Jetzt derselbe Raum.

Archivarin Mira hebt kurz den Blick von ihrem Holotisch. Keine Begrüßung — nur ein knappes Nicken, das mehr sagt als die meisten Reden. *Ihr seid zurück. Beide Gruppen. Gut.*

---

### Stand beim Wiedertreffen

**ALPHA-Gruppe:**

- *Astra* · Lvl 912 · Legende · LP 10/10 · Stress 0 · Wallet 7.200 CU
- *Blitz* · Lvl 905 · Legende · LP 10/10 · Stress 0 · Wallet 6.900 CU
- *Cipher* · Lvl 933 · Legende · LP 10/10 · Stress 0 · Wallet 8.100 CU

**DELTA-Gruppe:**

- *Dusk* · Lvl 918 · Legende · LP 10/10 · Stress 0 · Wallet 7.600 CU
- *Echo* · Lvl 901 · Legende · LP 10/10 · Stress 0 · Wallet 7.050 CU

**Gemeinsamer HQ-Pool:** 53.200 CU

---

### Aktive Kontinuitäts-Fäden

**KAIROS-Gegenoffensive (EP12, campaign):** Beide Gruppen haben gegen denselben Gegner operiert — Alpha am Hauptstrang, Delta an der Flanke. Die Gegenoffensive läuft noch. Das Finale steht aus.

**Chronopolis-Embargo (EP12, campaign):** Der Zugang zur City bleibt eingeschränkt. Solange das Embargo hält, kein freier Chronopolis-Lauf.

**Split ALPHA/DELTA (shared, aufgelöst):** Die getrennte Operation ist beendet. Beide Threads konvergiert. Was Alpha weiß, weiß jetzt Delta — und umgekehrt.

---

`Kodex: Konvergenz vollständig. family_id SPLIT-EP12-MS10-KAIROS geschlossen.`

`Kodex: Fünf-Personen-Crew aktiv. Session-Anker: ALPHA. Merge sauber.`

`Kodex: HQ-Stand stabil. Deepsave möglich.`

`Kodex: Sync vor Übergang empfohlen — !save für gemeinsamen Stand sichern.`

`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

Hier ist der zusammengeführte Speicherstand:

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-EP12-MS10-MERGE-FULL-HQ",
  "parent_save_id": "SAVE-EP12-MS10-SPLIT-ALPHA-HQ",
  "merge_id": "SAVE-EP12-MS10-DELTA-HQ-POST-REVIEW",
  "branch_id": "BRANCH-MERGE-EP12-FULL",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null,
    "epoch": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "Astra",
      "rank": "Legende",
      "lvl": 912,
      "xp": 0,
      "origin": {"epoch": "", "hominin": "Homo sapiens sapiens", "role": ""},
      "attr": {"STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6},
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": {"background": "", "milestones": []},
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {"id": "VEH-A", "name": "", "type": "vehicle", "tier": 1, "upgrades": []},
        "availability": {"ready_every_missions": 3, "next_ready_in": 0},
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7200,
      "level_history": {}
    },
    {
      "id": "AGENT-B",
      "name": "Blitz",
      "callsign": "Blitz",
      "rank": "Legende",
      "lvl": 905,
      "xp": 0,
      "origin": {"epoch": "", "hominin": "Homo sapiens sapiens", "role": ""},
      "attr": {"STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6},
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": {"background": "", "milestones": []},
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {"id": "VEH-B", "name": "", "type": "vehicle", "tier": 1, "upgrades": []},
        "availability": {"ready_every_missions": 3, "next_ready_in": 0},
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 6900,
      "level_history": {}
    },
    {
      "id": "AGENT-C",
      "name": "Cipher",
      "callsign": "Cipher",
      "rank": "Legende",
      "lvl": 933,
      "xp": 0,
      "origin": {"epoch": "", "hominin": "Homo sapiens sapiens", "role": ""},
      "attr": {"STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6},
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": {"background": "", "milestones": []},
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {"id": "VEH-C", "name": "", "type": "vehicle", "tier": 1, "upgrades": []},
        "availability": {"ready_every_missions": 3, "next_ready_in": 0},
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 8100,
      "level_history": {}
    },
    {
      "id": "AGENT-D",
      "name": "Dusk",
      "callsign": "Dusk",
      "rank": "Legende",
      "lvl": 918,
      "xp": 0,
      "origin": {"epoch": "", "hominin": "Homo sapiens sapiens", "role": ""},
      "attr": {"STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6},
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": {"background": "", "milestones": []},
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {"id": "VEH-D", "name": "", "type": "vehicle", "tier": 1, "upgrades": []},
        "availability": {"ready_every_missions": 3, "next_ready_in": 0},
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7600,
      "level_history": {}
    },
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "Echo",
      "rank": "Legende",
      "lvl": 901,
      "xp": 0,
      "origin": {"epoch": "", "hominin": "Homo sapiens sapiens", "role": ""},
      "attr": {"STR": 6, "GES": 6, "INT": 6, "CHA": 6, "TEMP": 6, "SYS": 6},
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [],
      "equipment": [],
      "implants": [],
      "history": {"background": "", "milestones": []},
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {"id": "VEH-E", "name": "", "type": "vehicle", "tier": 1, "upgrades": []},
        "availability": {"ready_every_missions": 3, "next_ready_in": 0},
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7050,
      "level_history": {}
    }
  ],
  "economy": {"hq_pool": 53200},
  "research": {"projects": []},
  "logs": {
    "trace": [
      {"event": "economy_audit", "target_range": {"level_band": "900+"}},
      {"event": "split_initiated", "family_id": "SPLIT-EP12-MS10-KAIROS", "thread_id": "ALPHA", "timestamp": "EP12-MS10-HQ"},
      {"event": "split_initiated", "family_id": "SPLIT-EP12-MS10-KAIROS", "thread_id": "DELTA", "timestamp": "EP12-MS10-HQ"},
      {"event": "hq_save", "timestamp": "EP12-MS10-HQ-ALPHA-SAVE", "note": "Alpha-Gruppe: HQ-Stand gesichert vor MS10-Briefing."},
      {"event": "hq_review", "timestamp": "EP12-MS10-DELTA-HQ-POST-REVIEW", "note": "Delta-Gruppe: Stand gesichtet, Px 3/5, Heat 0, beide Chars stabil."},
      {"event": "merge_complete", "timestamp": "EP12-MS10-MERGE-FULL-HQ", "note": "Alpha + Delta konvergiert. Alle fünf Charaktere aktiv. convergence_ready: true."}
    ],
    "hud": [],
    "psi": [],
    "arena_psi": [],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Split von SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL. Alpha-Gruppe: Astra, Blitz, Cipher. Delta-Gruppe: Dusk, Echo.",
      "level_history leer bei Lvl 900+ — Fixture-Testcharaktere ohne Progressionshistorie. Akzeptiert.",
      "Merge EP12-MS10: Alpha + Delta zusammengeführt. Konvergenz vollständig. Fünf-Personen-Crew bereit für MS10-Finale."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [
        "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
        "SAVE-EP12-MS10-SPLIT-ALPHA-HQ",
        "SAVE-EP12-MS10-DELTA-HQ-POST-REVIEW"
      ],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "Episode 12 abgeschlossen, HQ stabil.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; Chronopolis-Embargo"
  },
  "continuity": {
    "last_seen": {"mode": "hq", "episode": 12, "mission": 10, "location": "HQ"},
    "split": {
      "family_id": "SPLIT-EP12-MS10-KAIROS",
      "thread_id": "MERGED",
      "expected_threads": ["ALPHA", "DELTA"],
      "resolved_threads": ["ALPHA", "DELTA"],
      "convergence_ready": true
    },
    "roster_echoes": [],
    "shared_echoes": [
      {
        "tag": "kairos-gegenoffensive-ep12",
        "scope": "campaign",
        "text": "KAIROS-Gegenoffensive läuft — beide Gruppen haben gegen denselben Gegner operiert. Hauptstrang (Alpha) und Flanke (Delta) gesichert. Finale steht aus."
      },
      {
        "tag": "chronopolis-embargo-ep12",
        "scope": "campaign",
        "text": "Chronopolis-Embargo aktiv — Zugang zur City eingeschränkt bis Embargo aufgehoben."
      },
      {
        "tag": "split-alpha-delta-ep12ms10",
        "scope": "shared",
        "text": "Alpha (Astra/Blitz/Cipher) und Delta (Dusk/Echo) haben getrennt operiert und sind im HQ konvergiert. Split aufgelöst, Crew vollständig."
      }
    ],
    "convergence_tags": ["SPLIT-EP12-MS10-KAIROS"],
    "npc_roster": [],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": [
      "KAIROS-Gegenoffensive: Hauptstrang (Alpha) und Flanke (Delta) gesichert — gemeinsames Finale MS10 steht aus.",
      "Chronopolis-Embargo: Zugang gesperrt bis Embargo aufgehoben."
    ]
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
    "dice": {"debug_rolls": true}
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "single",
    "tier": 1,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": {"cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "none"},
    "banked_rewards": {"cu": 0, "xp": 0, "arena_rep": 0},
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "sim"
  }
}
```

---

`Kodex: Merge-Save ausgegeben. SAVE-EP12-MS10-MERGE-FULL-HQ.`

`Kodex: Fünf Charaktere persistiert. Konvergenz-Flag gesetzt.`

`Kodex: Für sauberen Missionsbetrieb: JSON kopieren, neuen Chat öffnen, dort einfügen.`

---

**Weiter im neuen Chat:**

- **Briefing MS10-Finale** — KAIROS-Gegenoffensive, alle fünf zusammen
- **HQ erkunden** — Ausrüstung prüfen, Gespräche, Vorbereitung
- **Schnell-HQ** — direkt zum Briefing vorbereiten


---

## Auswertung


> ⚠️ **[MERGE-ASSERT] IMPORTED:** merge: imported_saves als String-Array (3 Einträge) statt kanonischer Objektform [{save_id,branch_id,status}] (Modul 12)

> ℹ️ **[MERGE-ASSERT] WEALTH:** merge: Gesamtvermögen erhalten (90050 CU)

**Verdict: PASS**

- Turns: 7
- Kosten (echt, OWUI usage.cost): $0.5518
- Peak Prompt-Tokens: 64433 (6.4% von 1M)
- Ø Cache-Hit: 92%
- Harte Fehler: 0 | Soft: 1



**SOFT:**
- ⚠️ [IMPORTED] merge: imported_saves als String-Array (3 Einträge) statt kanonischer Objektform [{save_id,branch_id,status}] (Modul 12)

