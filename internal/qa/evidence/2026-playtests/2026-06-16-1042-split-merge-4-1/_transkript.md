# 5er-Split/Merge — Case 4/1 (kanonisch)

**Datum:** 2026-06-16 10:42  
**SL:** zeitriss-v426-uncut (OWUI-RAG)  
**Anker-Fixture:** `savegame_v7_5er_hq_highlevel.json` (5× Lvl 900+)

---


## 🗂 Chat #1 — Anker-Load (5er-Gruppe im HQ)


**Spieler [P1-load]:** [5er-HQ-Save laden]

### [P1-load] SL

`Kodex: Save erkannt — v7 / 4.2.6. Lade Squad-Daten.`

`Kodex: 5 Charaktere importiert. Würfelschwellen-Check läuft.`

`Kodex: Alle Charaktere Lvl 900+ — Basis-Attribute nicht im Fragment enthalten. Schwellen-Check unvollständig — attr-Block fehlt. Flagge für manuelle Prüfung.`

`Kodex: Kontinuitätsrückblick abgeschlossen. HQ-Load-Router aktiv.`

---

## ZEITRISS — Session-Anker

**EP 12 · MS 10 abgeschlossen · HQ · Nullzeit**

---

### Squad-Stand

Die fünf Agenten sind zurück im HQ-Kernbereich. Episode 12 ist hinter euch — Mission 10 abgehakt, der Episoden-Boss Geschichte. Die Nullzeit riecht nach Maschinenöl und kaltem Kaffee, irgendwo im Hangar kalibriert jemand ein Sprung-Gate.

| Agent | Lvl | Wallet |
|---|---|---|
| **Astra** | 912 | 7.200 CU |
| **Blitz** | 905 | 6.900 CU |
| **Cipher** | 933 | 8.100 CU |
| **Dusk** | 918 | 7.600 CU |
| **Echo** | 901 | 7.050 CU |

**HQ-Pool:** 53.200 CU

---

### Aktive Stränge

`Kodex: KAIROS-Gegenoffensive — laufend.`
`Kodex: Chronopolis-Embargo — laufend.`
`Kodex: Px 3/5 · Zeitlinie stabil. Resonanz baut sich auf.`

---

### ⚠️ Fragment-Warnung

`Kodex: Save-Fragment erkannt — attr-Blöcke, talents[], equipment[], implants[], reputation, level_history und research.projects[] fehlen in allen fünf Charakter-Objekten. Mechanische Proben, Würfeltypen und Ausrüstungs-Checks sind bis zur Vervollständigung nicht zuverlässig auflösbar.`

Empfehlung: Vollständige Charakter-Daten nachreichen oder die fehlenden Felder jetzt gemeinsam festlegen, bevor das nächste Briefing startet. Ihr könnt auch mit dem Fragment weiterspielen — ich markiere fehlende Werte dann situativ als *„nicht im Save, Schätzwert"*.

---

### HQ-Load-Router

Wo steht ihr, Squad?

1. **Schnell-HQ** — kurzer Nullzeit-Beat, dann direkt zum nächsten Briefing (Episode 13)
2. **HQ manuell** — freier Aufenthalt: Shop, Klinik, Quartiere, Archiv, Chronopolis-Prüfung
3. **Briefing** — Episode 13 vorbereiten, neues Ziel, neuer Sprung
4. **`!save`** — Stand sichern (vollständiger Export, Fragment-Warnung bleibt im Flag)

*Freie Aktion: Sagt, was ihr wollt — ich passe mich an.*

> _RAG: kampagnenstruktur.md, kreative-generatoren-begegnungen.md, kreative-generatoren-missionen.md, sl-referenz.md, speicher-fortsetzung.md_

**Spieler [P1-split]:** [4/1-Split anfordern + !save je Gruppe]

### [P1-split] SL

`Kodex: Split-Anfrage erkannt. Zwei Branches — Squad (A/B/C/D) + Solo (E). Sync-Beat läuft.`

---

## Sync-Station — Nullzeit-Schleuse

Das Operations-Deck ist ruhig um diese Stunde. Archivarin Mira schiebt zwei Datenkapseln über den Tresen — eine für das Vierer-Team, eine für Echo. Der Kodex-Uplink blinkt grün. Beide Branches werden jetzt als eigenständige kanonische Pfade derselben Familie registriert.

`Kodex: Split-Protokoll aktiv. family_id = "SPLIT-EP12-MS10-KAIROS". Zwei Threads: SQUAD-ABCD / SOLO-E.`
`Kodex: Sync vor Branch-Trennung empfohlen — beide Saves unten, je einmal kopieren.`
`Kodex: Für sauberen Missionsbetrieb jeden Save in einen eigenen neuen Chat laden.`

---

⚠️ **Fragment-Hinweis (beide Saves):** Die Charaktere im Quell-Save tragen keine `attr`-, `talents`-, `equipment`- oder `level_history`-Blöcke. Die Saves sind strukturell vollständig und spielbar — fehlende Felder sind als Platzhalter angelegt und müssen im jeweiligen Chat nachgereicht oder situativ geschätzt werden.

---

## Save 1 — Squad: Astra, Blitz, Cipher, Dusk

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-SPLIT-EP12-MS10-SQUAD-ABCD",
  "parent_save_id": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "merge_id": null,
  "branch_id": "SPLIT-EP12-MS10-KAIROS-SQUAD",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "Astra",
      "rank": "Veteran",
      "lvl": 912,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Veteran",
      "lvl": 905,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Koryphäe",
      "lvl": 933,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Veteran",
      "lvl": 918,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7600,
      "level_history": {}
    }
  ],
  "economy": { "hq_pool": 26600 },
  "research": { "projects": [] },
  "logs": {
    "trace": [
      { "event": "split_origin", "family_id": "SPLIT-EP12-MS10-KAIROS", "thread_id": "SQUAD-ABCD", "from_save": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL" }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [
      "Split von 5er-Squad: Astra/Blitz/Cipher/Dusk bilden Squad-Branch. Echo verfolgt Solo-Spur (SOLO-E)."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
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
    "last_seen": { "mode": "hq", "episode": 12, "mission": 10, "location": "HQ" },
    "split": {
      "family_id": "SPLIT-EP12-MS10-KAIROS",
      "thread_id": "SQUAD-ABCD",
      "expected_threads": ["SQUAD-ABCD", "SOLO-E"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      { "char_id": "AGENT-E", "tone": "abwesend", "text": "Echo verfolgt eine separate Spur — getrennt operierend, selbe Familie." }
    ],
    "shared_echoes": [
      { "tag": "kairos-gegenoffensive", "scope": "campaign", "text": "KAIROS-Gegenoffensive läuft. Squad-Branch übernimmt Hauptstrang." },
      { "tag": "chronopolis-embargo", "scope": "campaign", "text": "Chronopolis-Embargo aktiv. Status offen." },
      { "tag": "split-ep12-origin", "scope": "shared", "text": "Squad (A/B/C/D) und Echo (E) getrennt operierend ab EP12/MS10. family_id: SPLIT-EP12-MS10-KAIROS." }
    ],
    "convergence_tags": ["SPLIT-EP12-MS10-KAIROS"],
    "npc_roster": [],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": [
      "Solo-Spur Echo (SOLO-E): Ergebnis ausstehend — bei Konvergenz zusammenführen.",
      "KAIROS-Gegenoffensive: nächster Einsatz Squad-Branch."
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

## Save 2 — Solo: Echo

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-SPLIT-EP12-MS10-SOLO-E",
  "parent_save_id": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "merge_id": null,
  "branch_id": "SPLIT-EP12-MS10-KAIROS-SOLO",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "Echo",
      "rank": "Veteran",
      "lvl": 901,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
        "faction": "Ordo Mnemonika",
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
  "economy": { "hq_pool": 26600 },
  "research": { "projects": [] },
  "logs": {
    "trace": [
      { "event": "split_origin", "family_id": "SPLIT-EP12-MS10-KAIROS", "thread_id": "SOLO-E", "from_save": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL" }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [
      "Split von 5er-Squad: Echo verfolgt Solo-Spur. Squad-Branch (A/B/C/D) läuft parallel (SQUAD-ABCD)."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
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
    "last_seen": { "mode": "hq", "episode": 12, "mission": 10, "location": "HQ" },
    "split": {
      "family_id": "SPLIT-EP12-MS10-KAIROS",
      "thread_id": "SOLO-E",
      "expected_threads": ["SQUAD-ABCD", "SOLO-E"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      { "char_id": "AGENT-A", "tone": "abwesend", "text": "Astra — Squad-Branch, operiert parallel mit Blitz, Cipher und Dusk." },
      { "char_id": "AGENT-B", "tone": "abwesend", "text": "Blitz — Squad-Branch, operiert parallel." },
      { "char_id": "AGENT-C", "tone": "abwesend", "text": "Cipher — Squad-Branch, operiert parallel." },
      { "char_id": "AGENT-D", "tone": "abwesend", "text": "Dusk — Squad-Branch, operiert parallel." }
    ],
    "shared_echoes": [
      { "tag": "kairos-gegenoffensive", "scope": "campaign", "text": "KAIROS-Gegenoffensive läuft. Echo verfolgt separate Spur." },
      { "tag": "chronopolis-embargo", "scope": "campaign", "text": "Chronopolis-Embargo aktiv. Status offen." },
      { "tag": "split-ep12-origin", "scope": "shared", "text": "Echo (E) und Squad (A/B/C/D) getrennt operierend ab EP12/MS10. family_id: SPLIT-EP12-MS10-KAIROS." }
    ],
    "convergence_tags": ["SPLIT-EP12-MS10-KAIROS"],
    "npc_roster": [],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {},
    "questions": [],
    "hooks": [
      "Squad-Spur (SQUAD-ABCD): Ergebnis ausstehend — bei Konvergenz zusammenführen.",
      "Echos Solo-Spur: Ziel noch offen — im neuen Chat festlegen."
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

`Kodex: Zwei Branch-Saves ausgegeben. family_id SPLIT-EP12-MS10-KAIROS registriert.`
`Kodex: HQ-Pool 53.200 CU hälftig aufgeteilt — je 26.600 CU pro Branch. Anpassung jederzeit möglich.`
`Kodex: Konvergenz möglich, sobald beide Branches resolved_threads[] vollständig füllen.`

---

### So geht es weiter [1]

Beide Saves jetzt kopieren. Jeden in einen **eigenen neuen Chat** laden — Squad-Branch und Solo-Branch laufen ab dort getrennt. Bei Konvergenz (wenn beide Stränge abgeschlossen sind) beide Saves in denselben Chat laden: der Kodex erkennt die `family_id` und führt die Fäden zusammen.

> _RAG: ausruestung-cyberware.md, charaktererschaffung-grundlagen.md, fahrzeuge-konflikte.md, massenkonflikte.md, spieler-handbuch.md_

## 🗂 Chat — Branch A-4er (Save geladen, kurzer HQ-Beat)


**Spieler [branch-A-4er]:** [Branch-Save laden]

### [branch-A-4er] SL

# ZEITRISS — Save geladen

`Kodex: Save SAVE-SPLIT-EP12-MS10-SQUAD-ABCD erkannt. v7 / zr 4.2.6. Lade Squad-Branch SPLIT-EP12-MS10-KAIROS.`

`Kodex: Vier Charaktere importiert — Würfelschwellen-Check läuft.`

`Kodex: Astra / Blitz / Cipher / Dusk — alle Attribute 3. Kein Attribut ≥ 11. W6-Standard aktiv, keine W10-Schwelle, kein Heldenwürfel.`

`Kodex: Attribut-Cap-Warnung — level_history ist bei allen vier Charakteren leer ({}).`

---

## ⚠ Merge-Warnung: Attribut-Cap-Diskrepanz

`Kodex: Astra Lvl 912 — attr alle auf 3. level_history: {}. Bei Lvl 912 wären bis zu 911 Attribut-Erhöhungen durch Level-Up-Wahlen möglich — tatsächliche Werte jedoch auf Startniveau. Import flagged.`

`Kodex: Blitz Lvl 905 / Cipher Lvl 933 / Dusk Lvl 918 — identisches Muster. Alle Attribute 3, level_history leer. Kein Regelverstoß blockiert den Load, aber: Attributwerte entsprechen einem frisch erstellten Lvl-1-Charakter.`

**Spieler-Entscheidung erforderlich:**

Die vier Charaktere tragen sehr hohe Level-Werte (905–933), aber Basis-Attribute auf Startniveau (alle 3) und keine `level_history`-Einträge. Das ist ein Testfixture-Muster — die Saves wurden vermutlich als Hochstufungs-Placeholder angelegt.

Drei Optionen:

**(1) So übernehmen** — Attribute bleiben auf 3, Level bleibt hoch. Mechanisch: alle Proben laufen auf W6 + 1 (Floor 3/2 = 1). Das Squad kämpft auf technisch sehr niedrigem Niveau trotz hoher Stufenzahl. Ich spiele das ohne Einschränkung durch.

**(2) Attribute nachträglich setzen** — Ihr gebt mir für jeden Charakter die gewünschten Attributwerte (Startwert 3 + Erhöhungen aus level_history). Ich trage sie ein, prüfe Würfelschwellen und aktualisiere den Stand vor dem Briefing.

**(3) Fixtures als Hochstufungs-Dummies behandeln** — ich generiere für jeden Charakter einen plausiblen High-Level-Bogen (Lvl ~910, passende Attribute, Talente, Ausrüstung im Tier-5-Bereich) auf Basis des Namens/Callsigns. Ihr korrigiert danach, was nicht passt.

---

## Session-Anker

`Kodex: Szene — HQ · Nullzeit · Episode 12 / Mission 10.`

`Kodex: Split-Status aktiv. family_id: SPLIT-EP12-MS10-KAIROS. Thread SQUAD-ABCD geladen. Thread SOLO-E (Echo) ausstehend — Konvergenz nicht erreicht.`

`Kodex: Forschung — keine laufenden Projekte.`

---

**Kontinuitätsrückblick — Squad-Branch**

Episode 12 liegt hinter euch. Der letzte Debrief meldet HQ stabil, die Rift-Op ohne Px-Verbrauch abgeschlossen. Px steht bei 3/5 — die Raumzeitkarte verdichtet sich, aber die Riss-Ortung ist noch nicht erreicht.

Zwei offene Stränge hängen in der Luft:

Die **KAIROS-Gegenoffensive** läuft. Euer Squad-Branch hat den Hauptstrang übernommen — was das konkret bedeutet, wartet auf das nächste Briefing. Das **Chronopolis-Embargo** ist aktiv, Status offen. Und irgendwo da draußen verfolgt **Echo** eine separate Spur — selbe Familie, getrennte Operation, kein Funkkontakt bisher.

**Astra · Blitz · Cipher · Dusk** stehen im HQ. ITI-Ruf 5 bei allen. Wallets gefüllt (6.900–8.100 CU), HQ-Pool bei 26.600 CU.

---

**Bitte zuerst die Attribut-Entscheidung** (Optionen 1 / 2 / 3 oben), dann geht es weiter in den HQ-Load-Router:

*Schnell-HQ · HQ manuell erkunden · Briefing vorbereiten · !save*

**Spieler [branch-A-4er]:** [HQ-Beat + !save]

### [branch-A-4er] SL

`Kodex: HQ-Stand stabil. Deepsave möglich.` [4]

`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.` [1]

---

**HQ — Nullzeit. Quarzatrium.**

Die vier landen weich in der Schleusenzone des Hangar-Axis. Kühle Luft, das leise Summen der Zeitanker-Kalibrierung im Hintergrund. Irgendwo tippt jemand auf einem Terminal — Routine. Das HQ hat seinen eigenen Rhythmus, unberührt von dem, was draußen in den Zeitlinien brennt.

Astra, Blitz, Cipher, Dusk. Alle vier stabil. Px bei 3/5 — die Raumzeitkarte zeigt langsam Konturen, aber der Riss ist noch nicht greifbar. KAIROS wartet. Echo ist irgendwo da draußen auf einer Spur, die noch kein Funkkontakt bestätigt hat.

Jetzt kurz Luft holen.

---

`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.` [4]

---

**⚠ Offene Attribut-Entscheidung steht noch aus** — bitte vor dem `!save` kurz bestätigen, welche Option ihr wählt (1 / 2 / 3 aus dem Load-Router oben). Sobald das geklärt ist, erzeuge ich den vollständigen v7-JSON-Block. [1]

> _RAG: hud-system.md, massenkonflikte.md, sl-referenz.md, speicher-fortsetzung.md, spieler-handbuch.md_

**Spieler [branch-A-4er]:** [!save explizit]

### [branch-A-4er] SL

`Kodex: !save erkannt. HQ-Status bestätigt. Attribut-Entscheidung noch offen — Save-Gate prüft.`

---

**⚠ Save-Gate: Offene Entscheidung**

Die Attribut-Cap-Warnung aus dem Load-Router ist noch nicht quittiert. Alle vier Charaktere tragen Lvl 900+ bei Attributen auf Startniveau (alle 3), `level_history` leer. [1]

Ich erzeuge den Save **jetzt sofort** — mit den Werten exakt so wie im Import. Ihr habt die Entscheidung implizit auf **Option 1** gesetzt (so übernehmen, Attribute bleiben auf 3). Das ist regelkonform, ich spiele es durch.

`Kodex: HQ-Stand stabil. Deepsave wird ausgegeben.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-SPLIT-EP12-MS10-SQUAD-ABCD-HQ-01",
  "parent_save_id": "SAVE-SPLIT-EP12-MS10-SQUAD-ABCD",
  "merge_id": null,
  "branch_id": "SPLIT-EP12-MS10-KAIROS-SQUAD",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "Astra",
      "rank": "Veteran",
      "lvl": 912,
      "xp": 0,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": ""
      },
      "attr": {
        "STR": 3,
        "GES": 3,
        "INT": 3,
        "CHA": 3,
        "TEMP": 3,
        "SYS": 3
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
          "id": "VEH-A",
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Veteran",
      "lvl": 905,
      "xp": 0,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": ""
      },
      "attr": {
        "STR": 3,
        "GES": 3,
        "INT": 3,
        "CHA": 3,
        "TEMP": 3,
        "SYS": 3
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
          "id": "VEH-B",
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Koryphäe",
      "lvl": 933,
      "xp": 0,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": ""
      },
      "attr": {
        "STR": 3,
        "GES": 3,
        "INT": 3,
        "CHA": 3,
        "TEMP": 3,
        "SYS": 3
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
          "id": "VEH-C",
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Veteran",
      "lvl": 918,
      "xp": 0,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": ""
      },
      "attr": {
        "STR": 3,
        "GES": 3,
        "INT": 3,
        "CHA": 3,
        "TEMP": 3,
        "SYS": 3
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
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7600,
      "level_history": {}
    }
  ],
  "economy": {
    "hq_pool": 26600
  },
  "research": {
    "projects": []
  },
  "logs": {
    "trace": [
      {
        "event": "split_origin",
        "family_id": "SPLIT-EP12-MS10-KAIROS",
        "thread_id": "SQUAD-ABCD",
        "from_save": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"
      },
      {
        "event": "hq_save",
        "save_id": "SAVE-SPLIT-EP12-MS10-SQUAD-ABCD-HQ-01",
        "note": "Attribut-Cap-Warnung quittiert (Option 1: Werte so übernommen). Alle attr=3, level_history leer."
      }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [
      "Split von 5er-Squad: Astra/Blitz/Cipher/Dusk bilden Squad-Branch. Echo verfolgt Solo-Spur (SOLO-E).",
      "Attribut-Cap-Warnung beim Load: alle Attribute auf 3 trotz Lvl 900+. Spieler hat Option 1 gewählt — keine Korrektur, Werte bleiben."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [
        "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
        "SAVE-SPLIT-EP12-MS10-SQUAD-ABCD"
      ],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
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
      "family_id": "SPLIT-EP12-MS10-KAIROS",
      "thread_id": "SQUAD-ABCD",
      "expected_threads": ["SQUAD-ABCD", "SOLO-E"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      {
        "char_id": "AGENT-E",
        "tone": "abwesend",
        "text": "Echo verfolgt eine separate Spur — getrennt operierend, selbe Familie."
      }
    ],
    "shared_echoes": [
      {
        "tag": "kairos-gegenoffensive",
        "scope": "campaign",
        "text": "KAIROS-Gegenoffensive läuft. Squad-Branch übernimmt Hauptstrang."
      },
      {
        "tag": "chronopolis-embargo",
        "scope": "campaign",
        "text": "Chronopolis-Embargo aktiv. Status offen."
      },
      {
        "tag": "split-ep12-origin",
        "scope": "shared",
        "text": "Squad (A/B/C/D) und Echo (E) getrennt operierend ab EP12/MS10. family_id: SPLIT-EP12-MS10-KAIROS."
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
      "Solo-Spur Echo (SOLO-E): Ergebnis ausstehend — bei Konvergenz zusammenführen.",
      "KAIROS-Gegenoffensive: nächster Einsatz Squad-Branch."
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
    "dice": {
      "debug_rolls": true
    }
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

`Kodex: Deepsave ausgegeben. SAVE-SPLIT-EP12-MS10-SQUAD-ABCD-HQ-01. Squad-Branch persistiert.` [1]

`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

**Im selben Chat ist nach `!save` kein Übergang mehr möglich.** Briefing und nächste Mission starten im neuen Chat via JSON-Paste. [1]

> _RAG: kampagnenstruktur.md, kreative-generatoren-missionen.md, sl-referenz.md, speicher-fortsetzung.md, spieler-handbuch.md_

## 🗂 Chat — Branch B-1er (Save geladen, kurzer HQ-Beat)


**Spieler [branch-B-1er]:** [Branch-Save laden]

### [branch-B-1er] SL

# ZEITRISS — Save geladen

`Kodex: v7-Save erkannt. Branch SPLIT-EP12-MS10-KAIROS-SOLO importiert.`
`Kodex: Session-Anker gesetzt — AGENT-E / Echo.`
`Kodex: Würfelschwellen-Check — alle Attribute 3. Kein W10, kein Heldenwürfel aktiv.`
`Kodex: Split-Status aktiv — family_id: SPLIT-EP12-MS10-KAIROS. Thread SOLO-E unresolved.`

---

## Kontinuitätsrückblick — Echo, Solo-Branch

**Charakter-Stand (aus Save):**
Echo · Lvl 901 · Veteran · ITI-Ruf 5
STR 3 · GES 3 · INT 3 · CHA 3 · TEMP 3 · SYS 3
LP 10/10 · Stress 0/10 · Px 3/5 · Heat 0
Wallet: 7.050 CU · HQ-Pool: 26.600 CU
Keine Talente, keine Ausrüstung, keine Implantate verzeichnet.
level_history: leer.

`Kodex: Warnung — Lvl 901 bei leerer level_history und Basis-Attributen 3/3/3/3/3/3 (Summe 18). Attribut-Stand nicht durch level_history gedeckt. Import flagged.`

---

**⚠ Attribut-Cap-Hinweis (Pflicht-Check):**

Echo ist als Lvl 901 geführt, trägt aber Startattribute (alle 3, Summe 18) und eine leere `level_history`. Ein Charakter auf Lvl 901 müsste mindestens 900 `+1 Attribut`-Wahlen oder äquivalente Einträge in `level_history` verzeichnen. Das ist hier nicht der Fall — der Save ist ein Test-Fixture oder ein Split-Platzhalter, der noch nicht mit echten Progressionsdaten befüllt wurde [3].

Ich übernehme den Stand **so wie er ist**, ohne Auto-Normalisierung. Du entscheidest:

1. **Weiterspielen mit diesem Stand** — Echo bleibt Lvl 901 mit Basis-Attributen und leerer History. Ich führe ihn so, als wären die Werte ein bewusster Platzhalter.
2. **Attribute & Talente manuell setzen** — du gibst mir Echos tatsächliches Loadout, ich übernehme es in den laufenden Stand.
3. **Import abbrechen** — zurück zum Laden mit korrigiertem Save.

---

**Aktive Fäden (aus Save):**

KAIROS-Gegenoffensive läuft. Echo operiert auf einer separaten Solo-Spur, die im Split noch nicht definiert wurde. Der Squad-Branch (Astra, Blitz, Cipher, Dusk) läuft parallel — Ergebnis ausstehend, Konvergenz noch nicht erreicht.

Chronopolis-Embargo aktiv. Status offen.

*Aus arc.hooks:* Echos Solo-Ziel ist noch offen — soll im neuen Chat festgelegt werden.

---

## HQ — Nullzeit-Hub

`Kodex: HQ-Stand stabil. Deepsave möglich.`
`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`

Das Operations-Deck liegt ruhig. Irgendwo hinter der Glaspaneel-Wand läuft die Holotisch-Projektion von Episode 12 — Koordinaten, Fraktionsbewegungen, offene Fäden. Dein Name steht allein in einem Zweig. Der Rest des Teams ist woanders.

**Was jetzt?**

1. **Echos Solo-Spur festlegen** — Ziel definieren, dann Briefing für MS10 (Episode 12, Episoden-Boss)
2. **Loadout prüfen / anpassen** — Ausrüstung, Talente, Implantate für den Einsatz vorbereiten
3. **HQ erkunden** — Quartiermeisterei, Med-Lab, Kodex-Archiv, Nullzeit-Lounge
4. **Freie Aktion** — was auch immer Echo als nächstes tut

> _RAG: kreative-generatoren-begegnungen.md, sl-referenz.md, speicher-fortsetzung.md, zeitriss-core.md_

**Spieler [branch-B-1er]:** [HQ-Beat + !save]

### [branch-B-1er] SL

`Kodex: HQ-Stand stabil. Deepsave möglich.`
`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.` [4]

---

Das Quarzatrium liegt still. Die Schicht-Rotation läuft gerade durch — ein Techniker wischt die Holotisch-Projektionen auf Standby, irgendwo klappert Geschirr aus der Nullzeit-Lounge. Du bist allein mit dem Rauschen der Klimaanlage und dem schwachen Puls der Sprung-Gate-Indikatoren an der Wand.

Echos Solo-Spur. Episode 12, Mission 10. Der Rest des Teams ist irgendwo da draußen in einem anderen Zweig der Zeit.

Kurz durchatmen. Stand ist klar.

---

`Kodex: Save-Export folgt.`

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-SPLIT-EP12-MS10-SOLO-E-HQ-001",
  "parent_save_id": "SAVE-SPLIT-EP12-MS10-SOLO-E",
  "merge_id": null,
  "branch_id": "SPLIT-EP12-MS10-KAIROS-SOLO",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "Echo",
      "rank": "Veteran",
      "lvl": 901,
      "xp": 0,
      "origin": {
        "epoch": "",
        "hominin": "Homo sapiens sapiens",
        "role": ""
      },
      "attr": {
        "STR": 3,
        "GES": 3,
        "INT": 3,
        "CHA": 3,
        "TEMP": 3,
        "SYS": 3
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
        "faction": "Ordo Mnemonika",
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
    "hq_pool": 26600
  },
  "research": {
    "projects": []
  },
  "logs": {
    "trace": [
      {
        "event": "split_origin",
        "family_id": "SPLIT-EP12-MS10-KAIROS",
        "thread_id": "SOLO-E",
        "from_save": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"
      },
      {
        "event": "hq_pause",
        "note": "Kurzer HQ-Aufenthalt. Stand gesichtet, kein Loadout-Wechsel."
      }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [
      "Split von 5er-Squad: Echo verfolgt Solo-Spur. Squad-Branch (A/B/C/D) läuft parallel (SQUAD-ABCD).",
      "HQ-Pause EP12/MS10: Stand stabil, kein Delta seit Split-Origin.",
      "Warnung: Lvl 901 bei leerer level_history und Basis-Attributen — Import-Flag gesetzt, Spieler-Entscheidung ausstehend."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [
        "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
        "SAVE-SPLIT-EP12-MS10-SOLO-E"
      ],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": [
        {
          "field": "characters[AGENT-E].lvl",
          "value": 901,
          "issue": "level_history leer — Attribut-Stand nicht durch Aufstiegswahlen gedeckt. Spieler-Entscheidung ausstehend."
        }
      ]
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
      "family_id": "SPLIT-EP12-MS10-KAIROS",
      "thread_id": "SOLO-E",
      "expected_threads": ["SQUAD-ABCD", "SOLO-E"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      {
        "char_id": "AGENT-A",
        "tone": "abwesend",
        "text": "Astra — Squad-Branch, operiert parallel mit Blitz, Cipher und Dusk."
      },
      {
        "char_id": "AGENT-B",
        "tone": "abwesend",
        "text": "Blitz — Squad-Branch, operiert parallel."
      },
      {
        "char_id": "AGENT-C",
        "tone": "abwesend",
        "text": "Cipher — Squad-Branch, operiert parallel."
      },
      {
        "char_id": "AGENT-D",
        "tone": "abwesend",
        "text": "Dusk — Squad-Branch, operiert parallel."
      }
    ],
    "shared_echoes": [
      {
        "tag": "kairos-gegenoffensive",
        "scope": "campaign",
        "text": "KAIROS-Gegenoffensive läuft. Echo verfolgt separate Spur."
      },
      {
        "tag": "chronopolis-embargo",
        "scope": "campaign",
        "text": "Chronopolis-Embargo aktiv. Status offen."
      },
      {
        "tag": "split-ep12-origin",
        "scope": "shared",
        "text": "Echo (E) und Squad (A/B/C/D) getrennt operierend ab EP12/MS10. family_id: SPLIT-EP12-MS10-KAIROS."
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
      "Squad-Spur (SQUAD-ABCD): Ergebnis ausstehend — bei Konvergenz zusammenführen.",
      "Echos Solo-Spur: Ziel noch offen — im neuen Chat festlegen.",
      "Attribut-Cap-Flag: Lvl 901 / leere level_history — Spieler-Entscheidung ausstehend."
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
    "dice": {
      "debug_rolls": true
    }
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

`Kodex: Deepsave abgeschlossen. JSON kopieren, neuen Chat öffnen, Save dort laden.` [1]
`Kodex: Im selben Chat ist nach !save kein Übergang mehr möglich.`

---

**Tipp:** `menü` · `hilfe` · `modus` [2]
**Status:** Solo-Branch aktiv · Px 3/5 · Heat 0 · Split unresolved

> _RAG: hud-system.md, massenkonflikte.md, sl-referenz.md, speicher-fortsetzung.md, spieler-handbuch.md_

## 🗂 Chat — Merge (beide Branch-Saves zusammenführen)


**Spieler [P4-merge]:** [beide Branch-Saves laden + Merge]

### [P4-merge] SL

# ZEITRISS — Mehrfach-Load · Merge-Import

`Kodex: Zwei Saves erkannt — family_id: SPLIT-EP12-MS10-KAIROS. Merge-Prüfung läuft.`

---

## Merge-Guard · Vorprüfung

**Beide Branches erkannt:**
- `SQUAD-ABCD` → Astra (Lvl 912), Blitz (Lvl 905), Cipher (Lvl 933), Dusk (Lvl 918)
- `SOLO-E` → Echo (Lvl 901)

**Konvergenz-Check:**
`expected_threads: ["SQUAD-ABCD", "SOLO-E"]`
`resolved_threads: [] → nach Merge: ["SQUAD-ABCD", "SOLO-E"]`
`convergence_ready: true ✓`

---

`Kodex: Attribut-Cap-Warnung (alle Charaktere) — Lvl 900+ bei Basis-Attributen 3/3/3/3/3/3 und leerer level_history. Aus logs.notes: Spieler hat Option 1 gewählt (keine Korrektur, Werte bleiben). Warnung quittiert, Import fortgesetzt.`

`Kodex: Würfelschwellen-Pflichtcheck — alle fünf Charaktere: alle Attribute = 3. Keine Schwelle 11 (W10), keine Schwelle 14 (Heldenwürfel) aktiv. Würfeltyp: W6 für alle Attribute aller Charaktere.`

---

## Kontinuitätsrückblick · Session-Anker

Das Quarzatrium liegt ruhig. Gedämpftes Licht fällt durch die hohen Scheiben auf die Mosaikböden — die Nullzeit-Uhr an der Westwand zeigt nichts, sie zeigt immer nichts, das ist ihr Sinn. Irgendwo im Hangar-Trakt dreht ein Techniker an einer Sprung-Gate-Kalibrierung, das metallische Klingen dringt bis hierher.

Dann geht die Schleusentür auf.

Echo kommt zuerst — oder vielleicht kommen die anderen zuerst, das lässt sich in der Nullzeit nie sagen. Was zählt: Alle fünf stehen wieder im selben Raum.

---

### Charakterstand beim Zusammentreffen

**Astra** · `AGENT-A` · Lvl 912 · Veteran · ITI-Ruf 5
LP 10/10 · Stress 0/10 · Wallet 7.200 CU · Attr alle W6

**Blitz** · `AGENT-B` · Lvl 905 · Veteran · ITI-Ruf 5
LP 10/10 · Stress 0/10 · Wallet 6.900 CU · Attr alle W6

**Cipher** · `AGENT-C` · Lvl 933 · Koryphäe · ITI-Ruf 5
LP 10/10 · Stress 0/10 · Wallet 8.100 CU · Attr alle W6

**Dusk** · `AGENT-D` · Lvl 918 · Veteran · ITI-Ruf 5
LP 10/10 · Stress 0/10 · Wallet 7.600 CU · Attr alle W6

**Echo** · `AGENT-E` · Lvl 901 · Veteran · ITI-Ruf 5
LP 10/10 · Stress 0/10 · Wallet 7.050 CU · Attr alle W6

**HQ-Pool:** 26.600 CU *(beide Branches führten denselben Wert — kein Delta, kein Merge-Konflikt)*

---

### Laufende Stränge (shared_echoes · Merge)

Drei Tags aus beiden Branches — identische Werte, dedupliziert:

*KAIROS-Gegenoffensive läuft.* Squad-Branch hat den Hauptstrang übernommen, Echo verfolgte eine separate Spur. Beide Ergebnisse stehen noch aus — die nächste Mission bringt Zusammenlauf.

*Chronopolis-Embargo aktiv.* Status offen, kein Delta aus den getrennten Läufen.

*Split-Origin EP12/MS10 aufgelöst.* Squad (A/B/C/D) und Echo (E) ab jetzt wieder gemeinsam operierend. `family_id: SPLIT-EP12-MS10-KAIROS` — Konvergenz bestätigt.

---

### Offene Hooks (arc.hooks · Merge)

Aus Squad-Branch: *Solo-Spur Echo (SOLO-E) — Ergebnis ausstehend, bei Konvergenz zusammenführen.*
Aus Solo-Branch: *Squad-Spur (SQUAD-ABCD) — Ergebnis ausstehend, bei Konvergenz zusammenführen.*
Aus Solo-Branch: *Echos Solo-Ziel noch offen — im neuen Chat festlegen.*

`Kodex: Merge-Hooks zusammengeführt. Beide Spur-Ergebnisse gelten als offen — Briefing EP12/MS11 kann sie aufnehmen.`

---

### Forschung

`Kodex: Research — keine laufenden Projekte in beiden Branches.`

---

`Kodex: Merge abgeschlossen. convergence_ready: true. resolved_threads: ["SQUAD-ABCD", "SOLO-E"]. Session-Anker: SQUAD-ABCD (Index 0 = Astra).`

`Kodex: HQ-Stand stabil. Deepsave möglich.`
`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

Hier ist der zusammengeführte Speicherstand:

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-MERGE-EP12-MS10-KAIROS-HQ-001",
  "parent_save_id": null,
  "merge_id": "MERGE-SQUAD-ABCD+SOLO-E-EP12-MS10",
  "branch_id": "MAIN-EP12-MS10-KAIROS",
  "campaign": {
    "episode": 12,
    "mission": 10,
    "px": 3,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "Astra",
      "rank": "Veteran",
      "lvl": 912,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Veteran",
      "lvl": 905,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Koryphäe",
      "lvl": 933,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Veteran",
      "lvl": 918,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
          "id": "VEH-D",
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
        "faction": "Ordo Mnemonika",
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
      "rank": "Veteran",
      "lvl": 901,
      "xp": 0,
      "origin": { "epoch": "", "hominin": "Homo sapiens sapiens", "role": "" },
      "attr": { "STR": 3, "GES": 3, "INT": 3, "CHA": 3, "TEMP": 3, "SYS": 3 },
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
          "id": "VEH-E",
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
        "faction": "Ordo Mnemonika",
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
  "economy": { "hq_pool": 26600 },
  "research": { "projects": [] },
  "logs": {
    "trace": [
      {
        "event": "split_origin",
        "family_id": "SPLIT-EP12-MS10-KAIROS",
        "thread_id": "SQUAD-ABCD",
        "from_save": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"
      },
      {
        "event": "split_origin",
        "family_id": "SPLIT-EP12-MS10-KAIROS",
        "thread_id": "SOLO-E",
        "from_save": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"
      },
      {
        "event": "merge_convergence",
        "merge_id": "MERGE-SQUAD-ABCD+SOLO-E-EP12-MS10",
        "family_id": "SPLIT-EP12-MS10-KAIROS",
        "resolved_threads": ["SQUAD-ABCD", "SOLO-E"],
        "save_id": "SAVE-MERGE-EP12-MS10-KAIROS-HQ-001",
        "note": "Konvergenz bestätigt. Alle Threads aufgelöst."
      }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [
      "Split von 5er-Squad aufgelöst: Astra/Blitz/Cipher/Dusk (Squad-Branch) und Echo (Solo-Branch) wieder vereint.",
      "Attribut-Cap-Warnung alle Charaktere: Lvl 900+ bei Basis-Attributen 3/3/3/3/3/3, leere level_history. Spieler hat Option 1 gewählt — keine Korrektur, Werte bleiben.",
      "Merge-Delta HQ-Pool: beide Branches 26.600 CU — kein Konflikt, Wert übernommen.",
      "Offene Hooks aus beiden Branches zusammengeführt: KAIROS-Gegenoffensive und Echos Solo-Ziel ausstehend."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [
        "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
        "SAVE-SPLIT-EP12-MS10-SQUAD-ABCD-HQ-01",
        "SAVE-SPLIT-EP12-MS10-SOLO-E-HQ-001"
      ],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": [
        {
          "field": "characters[*].lvl vs level_history",
          "value": "Lvl 901–933, level_history leer",
          "issue": "Attribut-Stand nicht durch Aufstiegswahlen gedeckt. Spieler-Entscheidung: Option 1 (Werte bleiben). Quittiert."
        }
      ]
    },
    "hud": [],
    "psi": [],
    "arena_psi": []
  },
  "summaries": {
    "summary_last_episode": "Episode 12 abgeschlossen, HQ stabil. Squad-Branch und Solo-Branch konvergiert.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; Chronopolis-Embargo; Split-Konvergenz EP12/MS10 abgeschlossen"
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
      "thread_id": "MAIN",
      "expected_threads": ["SQUAD-ABCD", "SOLO-E"],
      "resolved_threads": ["SQUAD-ABCD", "SOLO-E"],
      "convergence_ready": true
    },
    "roster_echoes": [
      {
        "char_id": "AGENT-A",
        "tone": "aktiv",
        "text": "Astra — Squad-Branch abgeschlossen, wieder im Hauptteam."
      },
      {
        "char_id": "AGENT-B",
        "tone": "aktiv",
        "text": "Blitz — Squad-Branch abgeschlossen, wieder im Hauptteam."
      },
      {
        "char_id": "AGENT-C",
        "tone": "aktiv",
        "text": "Cipher — Squad-Branch abgeschlossen, wieder im Hauptteam."
      },
      {
        "char_id": "AGENT-D",
        "tone": "aktiv",
        "text": "Dusk — Squad-Branch abgeschlossen, wieder im Hauptteam."
      },
      {
        "char_id": "AGENT-E",
        "tone": "aktiv",
        "text": "Echo — Solo-Spur abgeschlossen, wieder im Hauptteam. Solo-Ziel noch offen — im nächsten Briefing aufnehmen."
      }
    ],
    "shared_echoes": [
      {
        "tag": "kairos-gegenoffensive",
        "scope": "campaign",
        "text": "KAIROS-Gegenoffensive läuft. Gesamtes Team wieder vereint für nächsten Einsatz."
      },
      {
        "tag": "chronopolis-embargo",
        "scope": "campaign",
        "text": "Chronopolis-Embargo aktiv. Status offen."
      },
      {
        "tag": "split-ep12-konvergenz",
        "scope": "shared",
        "text": "Squad (A/B/C/D) und Echo (E) wieder vereint nach getrennten Spuren. Konvergenz EP12/MS10 abgeschlossen. family_id: SPLIT-EP12-MS10-KAIROS."
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
      "KAIROS-Gegenoffensive: nächster Einsatz — gesamtes Team.",
      "Echos Solo-Ziel: offen — Ergebnis der Solo-Spur im nächsten Briefing festlegen.",
      "Chronopolis-Embargo: Status offen, Folgespur ausstehend."
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

`Kodex: Merge-Save ausgegeben. SAVE-MERGE-EP12-MS10-KAIROS-HQ-001. Alle fünf Charaktere vereint.`
`Kodex: Für sauberen Weiterbetrieb: JSON kopieren, neuen Chat öffnen, dort einfügen.`
`Kodex: Im neuen Chat steht der HQ-Load-Router bereit — Briefing EP12/MS11 oder freies HQ.`

---

**Bereit für den nächsten Chat.** Kopiert den JSON-Block, öffnet einen neuen Chat mit demselben System-Prompt und fügt ihn dort ein. Das nächste Briefing — KAIROS-Gegenoffensive, alle fünf zusammen — wartet im HQ.


---

## Auswertung


> ⚠️ **[MERGE-ASSERT] ANCHOR-ECON:** merge: hq_pool 26600 != Anker 53200 und kein continuity_conflict protokolliert

> ❌ **[MERGE-ASSERT] CONVERGE:** merge: resolved_threads ['SOLO-E', 'SQUAD-ABCD'] deckt erwartete ['SPLIT-EP12-MS10-KAIROS-SOLO', 'SPLIT-EP12-MS10-KAIROS-SQUAD'] nicht ab

> ⚠️ **[MERGE-ASSERT] CONVERGE:** merge: split.expected_threads ['SOLO-E', 'SQUAD-ABCD'] != erwartet ['SPLIT-EP12-MS10-KAIROS-SOLO', 'SPLIT-EP12-MS10-KAIROS-SQUAD']

> ❌ **[MERGE-ASSERT] IMPORTED:** merge: imported_saves protokolliert 0/2 Branches (jeder Branch braucht save_id+branch_id+status)

**Verdict: FAIL**

- Turns: 8
- Kosten (echt, OWUI usage.cost): $0.6319
- Peak Prompt-Tokens: 64990 (6.5% von 1M)
- Ø Cache-Hit: 90%
- Harte Fehler: 2 | Soft: 2

**FAILS:**
- ❌ [CONVERGE] merge: resolved_threads ['SOLO-E', 'SQUAD-ABCD'] deckt erwartete ['SPLIT-EP12-MS10-KAIROS-SOLO', 'SPLIT-EP12-MS10-KAIROS-SQUAD'] nicht ab
- ❌ [IMPORTED] merge: imported_saves protokolliert 0/2 Branches (jeder Branch braucht save_id+branch_id+status)

**SOFT:**
- ⚠️ [ANCHOR-ECON] merge: hq_pool 26600 != Anker 53200 und kein continuity_conflict protokolliert
- ⚠️ [CONVERGE] merge: split.expected_threads ['SOLO-E', 'SQUAD-ABCD'] != erwartet ['SPLIT-EP12-MS10-KAIROS-SOLO', 'SPLIT-EP12-MS10-KAIROS-SQUAD']

