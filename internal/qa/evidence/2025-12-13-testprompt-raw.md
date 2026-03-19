---
title: "Testprompt Voll-Lauf 2025-12-13 – Rohtext"
version: 1.0.0
tags: [qa, raw]
---

# Testprompt Voll-Lauf 2025-12-13 – Rohtext

Dieser Rohtext spiegelt die unveränderte Ausgabe des Testprompts inklusive
Speicherabgleich. Er dient als Referenz für den QA-Fahrplan und nachgelagerte
Maßnahmen. Bei der Bearbeitung der offenen Punkte immer gegen diesen Block
querprüfen.

## Issues und Befunde (Originaltext)

### ISSUE #1

- Beobachtung: Es existiert kein eigenständiges, als „Test-Save (JSON)“
  gekennzeichnetes v6-Referenz-Save im Datensatz; die Beispiele in Modul 12
  decken nicht alle geforderten Felder (insb. `logs.psi`, Arena-Trace,
  Cross-Mode-Felder) in einem konsolidierten Block ab.
- Diagnose: Der Speicherleitfaden zeigt mehrere Beispielstände (Ghost, Agent
  Nova, Accessibility-Preset), aber keinen einzigen, der alle Pflichtfelder und
  die Cross-Mode-Pfadfelder (`economy.wallets{}`, `logs.psi[]`,
  `arc_dashboard.offene_seeds`, `arena.phase_strike_tax`) in einem vollständigen
  `saveGame`-Fixture vereint. Für Cross-Mode-Tests (Solo → Koop → Arena) musste
  ein Synthese-Save manuell konstruiert werden.
- Evidenz: Acceptance-SMoke Prüfpunkte: 4 (HQ-Save-Guard), 10 (Cross-Mode-Saves).
  Nachfolgend ein vollständig ausgefüllter Teststand in kanonischer Struktur:

Test-Save (JSON)

```json
{
  "save_version": 6,
  "zr_version": "4.2.2",
  "location": "HQ",
  "phase": "core",
  "campaign": {
    "episode": 1,
    "mission": 5,
    "mission_in_episode": 5,
    "scene": 0,
    "type": "core",
    "mode": "preserve",
    "px": 3,
    "seed_source": "preserve_pool",
    "seed_id": "P-0002",
    "objective": "Stabilisiere Reaktor Brunsbüttel, verhindere Kühlverlust.",
    "hq_moments_used": ["BASTION"],
    "hq_moment_last": "BASTION",
    "rift_seeds": ["RIFT-011", "RIFT-015"],
    "exfil": {
      "active": false,
      "armed": false,
      "hot": false,
      "ttl": 0,
      "sweeps": 0,
      "stress": 0,
      "anchor": null,
      "alt_anchor": null
    }
  },
  "character": {
    "id": "AGENT-TEST",
    "name": "Vektor",
    "rank": "Operator I",
    "level": 3,
    "xp": 240,
    "origin": {
      "epoch": "ITI-Nullzeit",
      "hominin": "Homo sapiens sapiens",
      "role": "Infiltrator"
    },
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "attributes": {
      "STR": 4,
      "GES": 6,
      "INT": 4,
      "CHA": 3,
      "TEMP": 2,
      "SYS_max": 4,
      "SYS_used": 4,
      "hp": 11,
      "hp_max": 11
    },
    "modes": ["mission_focus"],
    "self_reflection": false,
    "has_psi": false,
    "psi_buffer": true,
    "talents": ["Schleichprofi", "Pistolenschütze"],
    "skills": ["Infiltration", "Taktische Analyse"],
    "implants": [
      {
        "name": "Retina-HUD-Kontaktlinse",
        "sys_cost": 0,
        "effect": "Standard-HUD, Paradoxon-Anzeige"
      },
      {
        "name": "Taktisches Ohrimplantat Mk I",
        "sys_cost": 1,
        "effect": "+1 Gehör, Comlink-Boost"
      },
      {
        "name": "Reflex-Boost Microline",
        "sys_cost": 1,
        "effect": "+1 Initiative"
      }
    ],
    "inventory": {
      "weapons": ["CQB-Kampfpistole (SD)", "Tactical Fighting Knife"],
      "armor": ["Kevlar-Weste Stufe II"],
      "gadgets": [
        "Multi-Tool Wraith",
        "Faseroptik-Kabelkamera",
        "Rauchgranate Mk I",
        "Micro-Breacher"
      ],
      "consumables": ["Med-Patch"],
      "special": ["Notfall-Transponder"]
    },
    "quarters": {
      "id": "QTR-T01",
      "preset": "custom",
      "layout_tags": ["stealth", "urban_ghost"],
      "deck": "HQ-A",
      "notes": "Kleines Einzelquartier mit schallgedämmter Tür."
    },
    "stats": {
      "missions_completed": 4,
      "deaths": 0,
      "rifts_closed": 0,
      "shots_fired": 27
    }
  },
  "team": {
    "members": [
      {
        "id": "AGENT-TEST",
        "callsign": "Vektor"
      }
    ]
  },
  "party": {
    "characters": [
      {
        "id": "AGENT-TEST",
        "callsign": "Vektor",
        "psi_buffer": true,
        "has_psi": false
      }
    ]
  },
  "loadout": {
    "AGENT-TEST": {
      "primary": "CQB-Kampfpistole (SD)",
      "secondary": "Tactical Fighting Knife",
      "armor": "Kevlar-Weste Stufe II",
      "gear": [
        "Multi-Tool Wraith",
        "Faseroptik-Kabelkamera",
        "Rauchgranate Mk I",
        "Micro-Breacher",
        "Ersatzmagazin"
      ]
    }
  },
  "economy": {
    "cu": 2100,
    "credits": 2100,
    "wallets": {
      "AGENT-TEST": {
        "name": "Vektor",
        "balance": 2100
      }
    }
  },
  "logs": {
    "artifact_log": [
      {
        "id": "A01",
        "name": "Mothman-Auge",
        "mission_ref": "EP01-MS03",
        "seed_id": "RIFT-011",
        "status": "archived",
        "note": "NightVision30m; Perception+1"
      }
    ],
    "market": [
      {
        "ts": "2025-11-26T18:45:00Z",
        "item": "Kevlar-Weste Stufe II",
        "cost_cu": 150,
        "px_clause": "neutral"
      }
    ],
    "offline": [
      {
        "ts": "2025-11-26T19:12:00Z",
        "trigger": "!offline",
        "device": "Comlink",
        "range_m": 2500,
        "jammer": true,
        "relay": false,
        "scene": "MS03:SC06"
      }
    ],
    "kodex": [
      {
        "ts": "2025-11-26T20:30:00Z",
        "message": "Paradoxon-Index 3/5 – ClusterCreate wahrscheinlich bei nächster stabiler Phase."
      }
    ],
    "alias_trace": [
      {
        "ts": "2000-09-15T20:00:00Z",
        "persona": "Dr. Lehmann",
        "cover": "Sicherheitsinspekteur",
        "status": "aktiv",
        "mission": "Brunsbüttel Blockage"
      }
    ],
    "squad_radio": [
      {
        "ts": "2000-09-15T20:12:00Z",
        "speaker": "Vektor",
        "channel": "Ops",
        "message": "Primärventil unter Kontrolle. Bereite Kühlrückfluss vor.",
        "status": "ok"
      }
    ],
    "hud": [
      "EP 01 · MS 04 · SC 12/12 · MODE CORE · Px ██░░░ (2/5) · FS 4/4 · GATE 2/2",
      "SF-OFF (M5 prep)",
      "Kodex: Foreshadow-Gate M5 erfüllt – Boss freigegeben."
    ],
    "psi": [
      {
        "ts": "2025-11-26T21:55:00Z",
        "ability": "phase_strike",
        "base_cost": 2,
        "tax": 1,
        "total_cost": 3,
        "mode": "pvp",
        "arena_active": true,
        "location": "ARENA",
        "gm_style": "verbose",
        "reason": "Arena-Smoke-Test"
      }
    ],
    "foreshadow": [
      {
        "token": "manual:mini-boss-signatur-gadget",
        "tag": "Foreshadow",
        "text": "Mini-Boss trägt Prototyp-EMP-Mine am Gürtel.",
        "scene": "EP01-MS04-SC09",
        "first_seen": "2025-11-26T20:15:00Z",
        "last_seen": "2025-11-26T20:15:00Z"
      },
      {
        "token": "manual:mini-boss-fluchtweg",
        "tag": "Foreshadow",
        "text": "Dachluke über der Probebühne ist ungesichert.",
        "scene": "EP01-MS04-SC10",
        "first_seen": "2025-11-26T20:20:00Z",
        "last_seen": "2025-11-26T20:20:00Z"
      }
    ],
    "fr_interventions": [
      {
        "ts": "2000-09-15T20:05:00Z",
        "result": "Beobachter",
        "faction": "Zeitkartell",
        "mission": "EP01-MS04",
        "scene": "SC04",
        "observer": true,
        "escalated": false,
        "impact": "Aufklärungsdrohne über Kühlbecken – keine direkte Einmischung."
      }
    ],
    "flags": {
      "runtime_version": "4.2.2",
      "compliance_shown_today": true,
      "chronopolis_warn_seen": false,
      "offline_help_count": 1,
      "offline_help_last_scene": "MS03:SC06",
      "self_reflection": false,
      "self_reflection_off": true,
      "self_reflection_auto_reset_at": null,
      "self_reflection_auto_reset_reason": null,
      "foreshadow_gate_m5_seen": true,
      "foreshadow_gate_m10_seen": false,
      "last_mission_end_reason": "completed",
      "hq_moment_last": "BASTION"
    }
  },
  "arc_dashboard": {
    "offene_seeds": [
      {
        "id": "RIFT-011",
        "epoch": "1983",
        "label": "Oko False Alarm – Schattenkontakt",
        "status": "open"
      },
      {
        "id": "RIFT-015",
        "epoch": "1977",
        "label": "Dam Safety Drill – Schattenriss im Wehr",
        "status": "open"
      }
    ],
    "fraktionen": {
      "ITI": 1,
      "Zeitkartell": -1
    },
    "timeline": [
      {
        "id": "TL-OLYMPICS-2000",
        "epoch": "2000",
        "label": "Milzbrand-Nano-Anschlag bei Olympia 2000 verhindert",
        "stability": 4
      },
      {
        "id": "TL-APOLLO15",
        "epoch": "1971",
        "label": "Apollo 15 Guidance stabilisiert",
        "stability": 2
      }
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": true,
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal"
  },
  "arena": {
    "active": false,
    "phase": "completed",
    "mode": "squad",
    "previous_mode": "preserve",
    "wins_player": 1,
    "wins_opponent": 1,
    "tier": 2,
    "proc_budget": 0,
    "artifact_limit": 1,
    "loadout_budget": 500,
    "phase_strike_tax": 1,
    "damage_dampener": true,
    "team_size": 4,
    "fee": 200,
    "scenario": "Scrimmage Montauk",
    "started_episode": 1,
    "last_reward_episode": 1,
    "policy_players": ["AGENT-TEST"],
    "audit": [
      {
        "ts": "2025-11-26T21:30:00Z",
        "event": "arenaStart",
        "fee": 200
      },
      {
        "ts": "2025-11-26T21:50:00Z",
        "event": "arenaEnd",
        "reward_cu": 300
      }
    ]
  }
}
```

Lösungsvorschlag

- Ansatz: Diesen Block als offizielles Fixture unter
  `internal/qa/fixtures/savegame_v6_test.json` oder analog dokumentieren und im
  Speicher-Modul explizit als Referenz verlinken. Zusätzlich im README unter
  „HQ-JSON-Save“ auf das Fixture verweisen.
- Risiken: Bei späteren Schemaänderungen muss das Fixture synchron angepasst
  werden; andernfalls droht es selbst zu veralten.

To-do

- Codex: Fixture in die Wissensbasis aufnehmen und im Speicher-Modul als
  „Test-Save (JSON)“ markieren.
- QA: Acceptance-SMoke Prüfpunkte 4 und 10 mit genau diesem Save als Input
  wiederholen (Solo, Solo→Koop, Koop→Arena), um Serializer- und Cross-Mode-Flows
  gegenzutesten.

Nächste Schritte

- Maintainer: Fixture ins Repo einchecken und in `master-index.json` unter
  einem eigenen Eintrag referenzieren.
- Notizen: Der Block bildet auch eine gute Basis für automatisierte
  Serializer-Tests und für künftige Tool-Integrationen.

---

### ISSUE #2

- Beobachtung: Self-Reflection-Status und Mission-5-Auto-Reset sind im
  Speicher-Modul widersprüchlich dokumentiert; das JSON-Beispiel zeigt
  `character.self_reflection = true`, aber `logs.flags.self_reflection = false`
  und `self_reflection_off = true`, während der Text fordert, dass Runtime und
  HUD ausschließlich `character.self_reflection` lesen und Auto-Reset beide
  Werte synchron setzt.

- Diagnose: Das Beispiel „Mission 5 Auto-Reset (Self-Reflection-Beispiel)“
  spiegelt offenbar einen Zwischenstand vor der finalen Helper-Logik. Die Flags
  repräsentieren den Status „SF-OFF während Mission 5“, der Charakterwert bereits
  den zurückgesetzten Zustand nach Missionende. Das kollidiert mit der
  Prioritätsbeschreibung (`set_self_reflection` synchronisiert Charakterwert und
  Flags) und erschwert die QA des Mission-5-Badge-Checks.

- Evidenz: Acceptance-SMoke Prüfpunkte: 3, 8, 11.
  - Mission-5-Badge-Check (Solo, Midgame Preserve) aus dem Test-Save:
    - Start im HQ mit `foreshadow_gate_m5_seen = true`, HUD-Log
      `["EP 01 · MS 04 · … · FS 4/4 · GATE 2/2", "SF-OFF (M5 prep)", …]` (Gate 2/2,
      SF-OFF).
    - Beim Start von Mission 5 erwartet das Toolkit laut Modul 16
      `scene_overlay()` mit `FS 0/4` und Gate-Badge `GATE 2/2`, Self-Reflection-
      Badge `SF-OFF`.
      - Simulierter HUD-Header (Szene 1):
        - `EP 01 · MS 05 · SC 01/12 · MODE CORE · Px ███░░ (3/5) · FS 0/4 · GATE 2/2 · SF-OFF`

    - Nach Missionsabbruch oder -abschluss soll der Auto-Reset laut Text **immer**
      Self-Reflection auf ON setzen und das HUD-Badge sowie Flag-Felder
      entsprechend aktualisieren.
    - Das Beispiel-JSON in Modul 12 zeigt dagegen:
      - `logs.flags.self_reflection = false`, `self_reflection_off = true`,
        HUD-Log nur `"SF-OFF (Mission 5)", "GATE 2/2"`, aber
        `character.self_reflection = true`.

    - Für den Badge-Check Mission 5 (Gate 2/2 → Missionstart → Toast & Zähler
      `FS 0/4` → Reset auf `SF-ON`) existiert somit keine eindeutige
      Referenzstruktur.

Lösungsvorschlag

- Ansatz: Beispielblock in Modul 12 anpassen:
  - Flags nach Auto-Reset auf `self_reflection = true`, `self_reflection_off =
false` setzen.
  - HUD-Log um einen expliziten Eintrag `SF-ON (post-M5 reset)` ergänzen, so dass
    klar wird: SF-OFF ist Missions-Log, SF-ON der aktuelle Zustand nach Rückkehr
    ins HQ.
  - Mission-5-Badge-Check im QA-Fahrplan mit dieser Zielstruktur verknüpfen
    (Gate 2/2, FS 0/4 beim Start, SF-ON nach Debrief).

- Risiken: Legacy-Saves, die alte Flag-Kombination gespeichert haben, müssten
  beim Laden entweder toleriert oder migriert werden (Normalizer, der
  `character.self_reflection` über Flags stellt).

To-do

- Codex: Helper `set_self_reflection()`-Beschreibung um eine kurze
  JSON-Zielstruktur erweitern; klarstellen, dass Flags stets den **aktuellen**
  Zustand spiegeln und nicht den Missionsverlauf.
- QA: Mission-5-Badge-Check mit zwei Läufen wiederholen (Abbruch und Abschluss):
  - Prüfen, ob HUD `SF-OFF` zu Beginn und `SF-ON (post-M5 reset)` nach Debrief
    loggt.
  - Sicherstellen, dass `character.self_reflection`, `logs.flags.self_reflection`
    und `logs.flags.self_reflection_off` konsistent sind.

Nächste Schritte

- Maintainer: Beispiel-JSON in Modul 12 aktualisieren, QA-Dokumentation
  zum Badge-Check auf neuen Zielzustand synchronisieren.
- Notizen: Der Mission-5-Auto-Reset ist ein zentraler Kontrollpunkt; eine
  eindeutige Referenzstruktur reduziert Supportfragen für Self-Reflection
  deutlich.

---

### ISSUE #3

- Beobachtung: Modul 12 trägt im Frontmatter die Version „4.2.3“, im Titelblock
  jedoch „ZEITRISS 4.2.2 – Modul 12“, während README und Master-Index Modul 12
  konsistent als Teil von 4.2.2 listen.

- Diagnose: Patch-Level des Speicher-Moduls wurde offenbar angehoben, die
  Überschrift und die übrige Runtime-Dokumentation aber nicht vollständig
  nachgezogen. Da die Semver-Regel explizit `major.minor` als
  Kompatibilitätskriterium nutzt, ist dies technisch unkritisch, aber für
  Dispatcher und Tool-Integrationen verwirrend.

- Evidenz: Acceptance-SMoke Prüfpunkte: 1, 2.
  - Modul-Header: `title: "ZEITRISS 4.2.3 – Modul 12..."`, darunter Überschrift
    `# ZEITRISS 4.2.2 – Modul 12 ...`.
  - README und `master-index.json` listen das Modul unter Version 4.2.2, ohne
    Hinweis auf das abweichende Patch-Level.

Lösungsvorschlag

- Ansatz: Versionierung bereinigen: Entweder Modul 12 offiziell auf 4.2.3
  anheben und README / Master-Index anpassen oder Titelblock zurück auf 4.2.2
  setzen. Zusätzlich im Speicher-Modul einen kurzen Hinweis zum Patch-Change
  (Changelog-Abschnitt) hinterlegen.
- Risiken: Bei Mischständen (Teile der Runtime noch 4.2.2, Speicher 4.2.3) können
  externe Tools verwirrt sein, wenn sie Versionsstrings als harte
  Kompatibilitätsprüfung nutzen.

To-do

- Codex: Semver-Abschnitt im Speicher-Modul um ein Beispiel ergänzen, das zeigt,
  wie `zr_version` und Modul-Version zusammenhängen.
- QA: Einen `!load`-Test mit einem Save `zr_version: "4.2.2"` gegen den
  4.2.3-Speicherleitfaden dokumentieren (Kompatibilitätsmeldung, ggf.
  Warntext).

Nächste Schritte

- Maintainer: Versionstrings vereinheitlichen, Changelog aktualisieren und
  bei Bedarf Tag/Release im Repo anpassen.
- Notizen: Saubere Versionsangaben helfen insbesondere bei zukünftigen
  4.3-Migrationen und automatisierten Schema-Validatoren.

---

### ISSUE #4

- Beobachtung: Offene Rifts werden gleichzeitig als `campaign.rift_seeds` (im
  Laufzeittext) und als `arc_dashboard.offene_seeds[]` (im Save-Beispiel)
  geführt; es gibt keinen klar definierten „Single Source of Truth“.

- Diagnose: Kampagnenstruktur und Toolkit beschreiben `ClusterCreate()` als
  Mechanik, die bei Px 5 neue Rift-Seeds erzeugt und im Save ablegt. An mehreren
  Stellen wird `campaign.rift_seeds` genannt, während das Deepsave-Beispiel die
  Seeds nur im `arc_dashboard.offene_seeds`-Block zeigt. Das lädt dazu ein,
  Seeds doppelt zu pflegen oder bei Cross-Mode-Imports (Solo → Koop, Koop →
  Arena) zu vergessen, beide Strukturen zu aktualisieren.

- Evidenz: Acceptance-SMoke Prüfpunkte: 6, 13.
  - Kampagnenstruktur: `ClusterCreate()` erzeugt 1–2 Seeds und „speichert sie im
    Saveblock, setzt Px auf 0“; später wird explizit `campaign.rift_seeds` als
    Speicherort erwähnt.
  - Speicher-Modul: Voller HQ-Deepsave nutzt `arc_dashboard.offene_seeds` zur
    Darstellung offener Seeds, ohne `campaign.rift_seeds` zu zeigen.
  - Toolkit: Rift-Spawn-Ansage referenziert `campaign.rift_seeds` und
    `ClusterDashboard`, ohne klarzustellen, ob das Dashboard aus
    `campaign.rift_seeds` generiert oder separat geführt wird.
  - In den simulierten Solo-, Koop- und PvP-Läufen mussten Seeds manuell sowohl
    in `campaign.rift_seeds` (für Kodex-Ansagen / HUD-Badges) als auch in
    `arc_dashboard.offene_seeds` gepflegt werden, um `!dashboard status` und
    Paradoxon-Prognosen konsistent zu halten.

Lösungsvorschlag

- Ansatz: `campaign.rift_seeds` als kanonische Datenquelle definieren und
  `arc_dashboard.offene_seeds` nur als abgeleitete Darstellung, die beim
  Laden/Schreiben automatisch synchronisiert wird (`normalize_save_v6()`-Pfad).
  Im Speicher-Modul explizit dokumentieren, dass Spielleitungen Seeds nur an
  einer Stelle anfassen.
- Risiken: Bestehende Saves, die Seeds nur im Dashboard führen, müssen bei der
  Migration einmalig gemappt werden.

To-do

- Codex: Abschnitt „Cluster-Erzeugung“ in Kampagnenstruktur und Speicher-Modul
  um eine kurze Strukturdefinition für `campaign.rift_seeds[]` erweitern, inkl.
  Feldnamen (`id`, `epoch`, `label`, `status`).
- QA: Regressionstest mit Px → 5 in Solo (Frühphase), Koop (Midgame) und Rift-
  Endgame: prüfen, ob `ClusterCreate()` Seeds konsistent in `campaign.rift_seeds`
  anlegt und `!dashboard status` sie korrekt aus dem Dashboard spiegelt.

Nächste Schritte

- Maintainer: Serializer / Normalizer aktualisieren, so dass beim Laden
  beide Strukturen zusammengeführt werden; Dokumentation im Toolkit ergänzen.
- Notizen: Eine klare Seed-Quelle erleichtert spätere Features wie automatisierte
  Rift-Side-Ops oder UI-Filter für „kritische“ Seeds.

---

### ISSUE #5

- Beobachtung: Arena-Start setzt `campaign.mode` auf `pvp`, es ist aber nicht
  dokumentiert, wann und wie `campaign.mode` nach Ende der Arena-Session wieder
  auf `preserve` oder `trigger` zurückgestellt wird.

- Diagnose: Das Toolkit beschreibt, dass `arenaStart()` die Arena aktiviert,
  `phase_strike_tax` setzt, SaveGuards blockiert **und** `state.campaign.mode =
'pvp'` markiert. Zugleich legt die Preserve-vs-Trigger-Logik fest, dass eine
  Kampagne genau einen Modus (Preserve oder Trigger) fährt; Arena wird als
  separates Endgame-Modul beschrieben, das Seeds deaktiviert.
  In den simulierten Cross-Mode-Läufen (Solo → Koop → Arena → HQ-Save) blieb
  `campaign.mode = 'pvp'` im Test-Save bestehen, obwohl die Kampagne anschließend
  wieder im Preserve-Core weiterlief. Das kann den Seed-Pool und den
  `seed_source`-Schalter beeinflussen.

- Evidenz: Acceptance-SMoke Prüfpunkte: 5, 10, 14.
  - Toolkit-Beschreibung `arenaStart(options)`: setzt `state.campaign.mode =
'pvp'` und meldet, dass Seeds deaktiviert sind; der Rückweg (Reset auf
    Preserve/Trigger) wird nicht im selben Modul beschrieben.
  - Preserve vs. Trigger: Kampagnenmodus wird einmalig gewählt, gemischte Pools
    seien ausgeschlossen; Mode-Feld in `campaign` dient als globaler Schalter.

Lösungsvorschlag

- Ansatz: `arenaStart()` und der Arena-Exit-Pfad sollten `campaign.previous_mode`
  konsequent nutzen:
  - Beim Start: `previous_mode = campaign.mode`, `campaign.mode = 'pvp'`.
  - Beim Exit: `campaign.mode = previous_mode`, `previous_mode = null`.
    Dies explizit im Speicher-Modul dokumentieren und im Arena-Deepsave-Beispiel
    widerspiegeln.

- Risiken: Bereits bestehende Saves mit `campaign.mode = 'pvp'` und leerem
  `previous_mode` benötigen einen manuellen oder heuristischen Reset (z. B.
  Standard auf `preserve`).

To-do

- Codex: Arena-Sektion im Toolkit um eine kurze State-Machine für
  `campaign.mode` ergänzen; klar markieren, dass Arena kein dauerhaft eigener
  Kampagnenmodus ist.
- QA: PvP-Smoke mit Fokus auf Mode-Reset:
  - HQ-Save vor Arena (Preserve),
  - Arena-Match,
  - HQ-Rückkehr,
  - `!save` und Kontrolle von `campaign.mode` sowie `seed_source`.

Nächste Schritte

- Maintainer: Arena-Runtime-Stub und Dokumentation aktualisieren; ggf.
  Migrationshinweis für ältere Saves ergänzen.
- Notizen: Ein sauberer Mode-Reset verhindert, dass PvP-Sessions unbeabsichtigt
  Core-Ops seeds und Preserve/Trigger-Pools blockieren.

---

### ISSUE #6

- Beobachtung: Der Gruppenschnellstart mit mehreren geposteten Saves
  (`Spiel starten (gruppe schnell)` mit 2 HQ-Saves + 1 neuer Rolle) ist im README
  skizziert, aber es fehlt eine explizite Regel, welcher Save als „Host“ für
  `campaign`, `economy` und globale Logs gilt.

- Diagnose: `load_deep()` ist klar auf einen HQ-Deepsave ausgelegt; für laufende
  Einsätze wird ein „Mid-Session-Merge“ beschrieben, der `party.characters[]` und
  Wallets auffüllt, ohne `state.location` zu ändern.
  Der Gruppenschnellstart im README demonstriert aber das gleichzeitige Posten
  mehrerer Saves vor einem neuen Briefing. Ohne definierte Priorität (z. B.
  „erster Save ist Host, weitere Saves liefern nur Charakterdaten“) ist unklar,
  wie Widersprüche bei `campaign.episode`, `px`, `economy.cu` oder Fraktionsständen
  aufgelöst werden sollen.

- Evidenz: Acceptance-SMoke Prüfpunkte: 2, 9.
  - README-Snippet „Gruppe – Schnelleinstieg (gemischt, 2 Saves + 1 Rolle)“:
    Synchronisierung von A und B wird beschrieben, aber nicht, auf welcher
    Kampagnen-Zeitleiste das Team landet.
  - Speicher-Modul: `Mid-Session-Merge` erwähnt explizit, dass dieser Pfad für
    neue Agenten in laufende Einsätze gedacht ist, nicht für mehrere HQ-
    Saves vor einem Einsatz.

Lösungsvorschlag

- Ansatz: Klare Host-Regel definieren, z. B.:
  - Erst geposteter Save bestimmt `campaign`, `economy`, `px`, `logs`.
  - Weitere Saves liefern nur `party.characters[]`, `loadout` und individuelle
    Stats; Kampagnenfelder werden ignoriert oder in einem separaten QA-Log
    (Konfliktwarnung) festgehalten.
    Diese Regel im README und im Speicher-Modul an derselben Stelle
    dokumentieren.

- Risiken: Gruppen, die bisher „Save mit höchstem Level“ oder ähnliche
  Heuristiken verwenden, müssen ihr Vorgehen anpassen.

To-do

- Codex: Abschnitt „Spiel laden“ um einen Unterpunkt „Multi-Save-Import (Gruppe)“
  erweitern, inkl. Pseudocode für Host-Auswahl und Konfliktlog.
- QA: Gruppenschnellstart mit zwei divergenten Saves (verschiedene Episoden und
  CU-Stände) durchspielen und prüfen, ob das System konsistent den Host benennt
  und Abweichungen klar im Kodex-Log dokumentiert.

Nächste Schritte

- Maintainer: Dispatcher-Logik (`Spiel starten (gruppe schnell)`) an die
  Host-Regel anpassen, falls erforderlich.
- Notizen: Eine definierte Host-Semantik verhindert subtile Paradoxon-Fehler
  durch „Zeitleisten-Mischungen“ beim Gruppeneinstieg.

---

### ISSUE #7

- Beobachtung: Die CU-Ökonomie nutzt mehrere überlagerte Formeln (Risiko-Basis ×
  Multiplikator, Solo/Buddy-Hazard-Pay, 10×Spielerlevel, Szenen-Skalierung), ohne
  klaren Vorrang oder Kombinationsregel.

- Diagnose: Modul 8A beschreibt die Missionsprämie als `Basiswert × Multiplikator`,
  ergänzt um Hazard-Pay +50 % für Solo/Buddy und optionale Boni. Modul 15 führt
  zusätzlich eine Empfehlung „Standardmissionen rechnen mit 10×Spielerlevel CU“
  sowie eine szenenbasierte Formel `Belohnung = Basiswert × Multiplikator ×
(abgeschlossene Szenen / 12)` ein.
  In den simulierten Solo-Early-Game-Runs (Lvl 1, R1) und Koop-Midgame-Runs
  (Lvl 5, R2) ergeben sich stark divergierende Belohnungen, je nachdem, ob nur
  eine oder alle Formeln kumulativ angewendet werden.

- Evidenz: Acceptance-SMoke Prüfpunkte: 7, 12.
  - Beispiel: Solo-Core-Mission (Lvl 1, Mid-Risiko, Erfolg, 12 Szenen)
    - Variante A (nur Basis + Multiplikator + Hazard-Pay): 500 CU × 1,0 × 1,5
      = 750 CU.
    - Variante B (zusätzlich Szenenskalierung): 500 × 1,0 × (12/12) × 1,5 =
      750 CU (identisch).
    - Variante C (zusätzlich 10×Level additiv interpretiert): 750 + 10 = 760 CU.
    - Variante D (10×Level als separate Basis): 10×Level (10) statt 500 →
      deutliche Unterzahlung im Vergleich zur Risiko-Tabelle.

  - Modultexte lassen offen, ob die 10×Level-Regel eine alternative
    Budget-Daumenregel oder ein zusätzlicher Aufschlag sein soll.

Lösungsvorschlag

- Ansatz: Eine einzige, verbindliche Formel im Economy-Modul festlegen (z. B.
  Basiswert nach Risiko × Multiplikator × Szenenfaktor, Hazard-Pay als klar
  definierter Bonus) und die 10×Level-Angabe explizit als „Budget-Faustregel für
  Kampagnenplanung, nicht für Ingame-Payout“ deklarieren.
- Risiken: Anpassungen können bestehende Balancen in laufenden Kampagnen
  verschieben; Gruppen, die bereits auf alten Werten basieren, müssen einmalig
  geglättet werden.

To-do

- Codex: Modul 15 um eine Beispielrechnung mit Solo- und Koop-Mission ergänzen,
  inkl. Klartext „Diese Formel ersetzt die ältere Kurzformel in Modul 8A“ oder
  umgekehrt.
- QA: Vergleichsrechnungen mit denselben Missionen (Frühphase Solo, Midgame
  Koop, Endgame Rift-Boss) unter alter und neuer Formel dokumentieren, um den
  Effekt auf Progression und Shoppreise zu bewerten.

Nächste Schritte

- Maintainer: Economy-Texte in Modul 8A und 15 synchronisieren, ggf. alte
  Formulierungen als „legacy“ kennzeichnen.
- Notizen: Eine konsistente CU-Formel erleichtert auch das Balancing von
  Chronopolis-Preisen und Arena-Gebühren.

---

### ISSUE #8

- Beobachtung: Die automatische Boss-Schadensreduktion (Mini-Boss DR 2, Arc-/
  Rift-Boss DR 3) ist für kleine Teams (Solo, Duo) sehr hart und streckt
  Gefechte deutlich, ohne dass eine Teamgrößen-Skalierung vorgesehen ist.

- Diagnose: Kampagnenstruktur definiert DR 2 für Mini-Bosse und DR 3 für Episoden-
  und Rift-Bosse als Pflicht-Deckel, um Exploding-Burst zu zähmen. Das Toolkit
  übernimmt dies als festen HUD-Toast („Boss-DR aktiviert – −X Schaden pro
  Treffer“).
  In den simulierten Solo-/NPC-Squad-Runs (Frühphase Mini-Boss M5, Endgame Rift-
  Boss) führt DR bei Standardwaffen (Handfeuerwaffe, 1–2 Exploding-Würfe) oft
  dazu, dass einzelne Treffer vollständig „wegreduziert“ werden. Das fühlt sich
  für Solo-Operatoren zäh an und kann Endgame-Fights unnötig in die Länge
  ziehen.

- Evidenz: Acceptance-SMoke Prüfpunkte: 3, 6, 15.
  - Core-Mini-Boss (Mission 5, Solo + 1 NPC):
    - Typische Trefferlage: 5–7 Schaden pro Schuss; DR 2 reduziert effektiv
      ~30–40 % der Output-Spitze.

  - Rift-Boss (Szene 10, Koop-Team 4P):
    - DR 3 funktioniert wie vorgesehen als Burst-Limiter, weil mehrere Quellen
      Schaden beitragen.

  - Für Solo-Runs, die bereits Hazard-Pay erhalten, gibt es keinen Ausgleich für
    verlängerte TTK.

Lösungsvorschlag

- Ansatz: DR an Teamgröße koppeln, z. B.:
  - Teamgröße 1–2: Mini-Boss DR 1, Boss DR 2.
  - Teamgröße 3–4: aktueller Wert (2/3).
  - Teamgröße 5–6: +1 DR optional als Hard-Mode.
    Die HUD-Ausgabe („Boss-DR aktiviert – −X Schaden“) bleibt, aber X wird
    dynamisch aus Teamgröße berechnet.

- Risiken: Änderungen am DR-Modell beeinflussen alle bestehenden Encounter-
  Designs; die Balance muss in Solo- und Gruppen-Szenarien neu verifiziert
  werden.

To-do

- Codex: Boss-Sektion in Kampagnenstruktur und Toolkit um eine DR-Tabelle nach
  Teamgröße ergänzen.
- QA: Drei Vergleichs-Runs pro Phase: Solo, Duo, Viererteam gegen denselben
  Boss; TTK und gefühlte Gefährlichkeit dokumentieren, bevor DR-Werte endgültig
  festgelegt werden.

Nächste Schritte

- Maintainer: `generate_boss()`-Spiegel im Toolkit entsprechend anpassen
  und die HUD-Texte auf variable DR-Werte ausrichten.
- Notizen: Eine teamgrößen-sensitive DR hält den „harten Thriller“-Ton, ohne
  Solo-Play unangemessen zu bestrafen.

---

### ISSUE #9

- Beobachtung: Die detaillierte „Acceptance-SMoke-Checkliste“ (15 Schritte) wird
  im README referenziert, liegt aber in einem externen QA-Dokument, das nicht
  Teil der Runtime-Wissensbasis ist; produktive KI-Leitungen sehen nur die
  Kurzfassung.

- Diagnose: README verweist auf
  `docs/qa/tester-playtest-briefing.md#acceptance-smoke-checkliste` für die
  vollständige 15-Punkte-Liste und bietet im Runtime-Bereich nur eine komprimierte
  „Kurzablauf“-Version (Solo-Start, !load, !helper boss, !save, !arena,
  Accessibility, Offline, etc.).
  Da `tester-playtest-briefing` nicht in den 20 Runtime-Modulen des Master-Index
  enthalten ist, steht diese Detail-Checkliste der Ingame-Kodex-Instanz (KI-Spielleitung /
  Custom-AI) nicht zur Verfügung. Für Prüfnummern 1–15 müssen QA-Flows derzeit
  auf externe Repo-Kenntnis zurückgreifen.

- Evidenz: Acceptance-SMoke Prüfpunkte: alle (1–15) – Nummern mussten in dieser
  Auswertung aus der Kurzfassung hergeleitet werden.
  - Master-Index listet ausschließlich die Runtime-Module (`core`, `characters`,
    `gameplay`, `systems`), nicht aber `docs/qa/tester-playtest-briefing.md`.
  - README markiert die ausführliche Checkliste als Teil des Dispatcher-
    Briefings und verweist nur über Link; im Runtime-Text werden lediglich die
    wichtigsten Pfade beschrieben (`Spiel starten (solo)`, `!load`, `!helper
boss`, `!arena status`, `!accessibility`).

Lösungsvorschlag

- Ansatz: Die 15 Acceptance-Schritte in ein Runtime-Modul spiegeln (z. B.
  Anhang im Toolkit oder im Speicher-Modul) oder direkt in README unterhalb des
  Kurzablaufs auflisten. Alternativ: ein kompaktes „QA-Overlay“ mit nummerierten
  Prüfungen, auf das der Kodex aktiv referenzieren kann.
- Risiken: Doppelte Pflege von QA-Checklisten (Repo-Dokument + Runtime-Spiegel)
  erfordert Disziplin; Abweichungen müssen vermieden werden.

To-do

- Codex: Eine nummerierte „Acceptance-SMoke“-Liste in das Toolkit aufnehmen, so
  dass KI-Instanzen die Prüfpunkte 1–15 intern referenzieren können, ohne
  externe Dateien zu benötigen.
- QA: Abgleich zwischen Dispatcher-Dokument und Runtime-Spiegel erstellen
  (Matrix 1–15), um sicherzustellen, dass keine Prüfpunkte fehlen oder anders
  benannt sind.

Nächste Schritte

- Maintainer: Entweder `tester-playtest-briefing` als weiteres
  Wissensmodul zulassen oder seine Kerninhalte in ein bestehendes Runtime-Modul
  migrieren.
- Notizen: Eine direkt im Kodex verfügbare Checkliste erleichtert automatisierte
  Smoke-Runs (z. B. `!smoke status`) und verringert die Gefahr, dass einzelne
  Acceptance-Pfade ungetestet bleiben.

---

## Speicher-Abgleich (Originaltext)

"Verstanden — du hast einen **vollständigen HQ-Deepsave** gepostet.
Da du **keinen Befehl gestellt hast** (z. B. „Spiel laden“, „Weiter“, „Briefing
starten“, „Mission fortsetzen“ etc.), befinde ich mich noch **außerhalb der In-
World-Erzählung**.

Ich sage dir kurz, **was der Save bedeutet** und **was du jetzt tun kannst**.

---

# ✅ Dein Save (Kurzüberblick)

Ich erkenne:

- **Ort:** HQ (also speicherbar, kein Exfil aktiv)
- **Episode 1 · Mission 5** → das ist **Mini-Boss-Mission** gemäß Rhythmus
- **Px 3/5**
- **Seed P-0002 – Brunsbüttel Blockage** (Preserve-Pool)
- **Foreshadow-Gate M5 ist offen (2/2)** – der Boss ist also freigegeben
- **Self-Reflection OFF** durch Mission-5-Reset
- **SYS_used = SYS_max = 4** → HQ-Save gültig
- **Arena nicht aktiv**
- **Charakter „Vektor“**, Lvl 3, Infiltrator, kein Psi

Alles konsistent.
Ready für Rückblende + Briefing **sobald du den Startbefehl gibst**.

---

# ❓ Wie möchtest du fortfahren?

Bitte wähle eine der Optionen:

### **1️⃣ Spiel laden und weiterspielen**

Ich führe sofort das **Kodex-Recap**, HUD-Overlay und anschließend das **Briefing
zu Mission 5** aus.
👉 **Sag: „Spiel laden“**

---

### **2️⃣ Direkt ins Mission-5-Briefing ohne Recap**

Falls du das Recap überspringen willst.
👉 **Sag: „Briefing starten“**

---

### **3️⃣ Status anzeigen**

Arc-Dashboard, Seeds, Fraktionen, Px, HUD-Modus usw.
👉 **Sag: „Status“** oder **„Dashboard“**

---

### **4️⃣ HQ-Phase spielen / Ausrüstung ändern**

Training, Shop, Cyberware, Buffs („HQ-Moments“) etc.
👉 **Sag: „HQ-Phase“**

---

### **5️⃣ Etwas anderes tun**

Beliebige Frage stellen oder konkreten Wunsch formulieren.

---

Sobald du eine der Optionen wählst, schalte ich in den **filmischen Agenten-
Thriller** um."
