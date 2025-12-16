---
title: "ZEITRISS 4.2.3 – Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)"
version: 4.2.3
tags: [system]
---

# ZEITRISS 4.2.3 – Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)

## HQ-JSON-Save {#json-schluesselfelder}
> **Guard:** Speichern nur in der HQ-Phase; Pflichtwerte sind deterministisch.
> Chat-Befehle: `!save`, `!load`, optional `!autosave hq`, `!suspend`, `!resume`.
> Einziger Save-Typ: Deepsave (HQ-only).

**SaveGuard (Pseudocode)**
{# LINT:HQ_ONLY_SAVE #}
```pseudo
assert state.location == "HQ", "Speichern nur im HQ. Missionszustände sind flüchtig und werden nicht persistiert."
assert state.character.attributes.SYS_installed == state.character.attributes.SYS_max
assert state.character.attributes.SYS_runtime <= state.character.attributes.SYS_installed
assert state.character.stress == 0 und state.character.psi_heat == 0
assert not state.get('timer') und not state.get('exfil_active') und not campaign.exfil.active
required = [
  "character.id",
  "character.attributes.SYS_max",
  "character.attributes.SYS_installed",
  "character.attributes.SYS_runtime",
  "character.attributes.SYS_used",
  "character.stress",
  "character.psi_heat",
  "character.cooldowns",
  "campaign.px",
  "economy",
  "economy.wallets",
  "logs",
  "logs.hud",
  "logs.trace",
  "logs.artifact_log",
  "logs.market",
  "logs.offline",
  "logs.kodex",
  "logs.alias_trace",
  "logs.squad_radio",
  "logs.foreshadow",
  "logs.fr_interventions",
  "logs.psi",
  "logs.arena_psi",
  "logs.flags.merge_conflicts",
  "logs.flags",
  "ui",
  "arena"
]
assert serializer_bereit(required)
```

Speichern ist ausschließlich in der HQ-Phase zulässig. Alle Ressourcen sind
dort deterministisch gesetzt:

Referenz-Fixtures `internal/qa/fixtures/savegame_v6_test.json`,
`savegame_v6_highlevel.json` und `savegame_v6_full.json` führen alle
Pflichtcontainer (u. a. `logs.arena_psi[]`, `logs.flags.merge_conflicts[]`) als
minimale bis schema-vollständige Beispiele und dienen als Abgleich für
Smoke-/Acceptance-Läufe. Das versionierte JSON-Schema liegt unter
`systems/gameflow/saveGame.v6.schema.json`; `load_deep()` validiert Saves gegen
dieses Schema und bricht mit einem `Save-Schema (saveGame.v6)`-Fehler ab, wenn
Pflichtcontainer fehlen oder die Typen nicht passen.

Offline-Fallbacks sperren den HQ-Save bis zum Kodex-Re-Sync: `save_deep()`
bricht mit „SaveGuard: Offline – HQ-Re-Sync erforderlich.“ ab, schreibt
gleichzeitig ein `logs.trace[]`-Event `save_blocked` (`reason: offline`) und
führt keine weiteren Save-Guards aus. Der Befehl `!offline` ist auf 60 s
getaktet; Rate-Limit-Meldungen zählen weder den Offline-Counter hoch noch
füllen sie das Protokoll.

### Kompakt-Profil für GPT (Save v6)
Das Schema ist zusätzlich als Klartext-Profil für MyGPT gespiegelt, damit es
ohne Artefakt-Anhang in den Wissensspeicher passt. Orientiere dich an
SaveGuard + folgendem Pfadbaum:

- `save_version`, `zr_version`, `location`, `phase`
- `character.{id,name,rank,stress,psi_heat,cooldowns,attributes.SYS_max|installed|runtime|used}`
- `campaign.{episode,scene,px,rift_seeds[]}`
- `team.members[]`, `party.characters[]`, `loadout`, `economy.{cu,wallets}`
- `logs.{artifact_log,market,offline,kodex,alias_trace,squad_radio,hud,psi,arena_psi,foreshadow,fr_interventions,flags{runtime_version,compliance_shown_today,chronopolis_warn_seen,chronopolis_unlock_level,chronopolis_unlocked},flags.merge_conflicts[]}`
- `arc_dashboard{offene_seeds[],fraktionen{}}`, `ui` (vollständiger UI-Block), `arena` (Status inkl. `queue_state=idle|searching|matched|staging|active|completed`, `zone=safe|combat`, `team_size` hart 0–4)

Die JSON-Schema-Datei bleibt für Validierungs-/QA-Läufe bestehen; GPT nutzt
das Klartext-Profil als maßgebliche Struktur.

`campaign.exfil{active, armed, hot, ttl, sweeps, stress, anchor, alt_anchor}`
spiegelt den Zustand des Exfil-Fensters. Solange `campaign.exfil.active`
oder `state.exfil.active` wahr ist, blockiert der Serializer den HQ-Save mit
„SaveGuard: Exfil aktiv – HQ-Save gesperrt.“. Arena- und HQ-Blocker nutzen
denselben Text via `toast_save_block(reason)`. Sobald die Crew ins HQ
zurückkehrt, setzt die Runtime alle Exfil-Felder automatisch zurück.

In-Mission-Ausstieg ist erlaubt, aber es erfolgt kein Save; Ausrüstung darf
übergeben werden, nächster Save erst im HQ. HQ-Saves verlangen vollständige
Installation (`SYS_installed == SYS_max`) und eine Runtime-Last innerhalb des
installierten Rahmens (`SYS_runtime ≤ SYS_installed`).

```json
{
  "save_version": 6,
  "zr_version": "4.2.3",
  "location": "HQ",
  "phase": "core",
  "character": {
    "id": "CHR-1234",
    "name": "Ghost",
    "rank": "Operator I",
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "attributes": {
      "SYS_max": 5,
      "SYS_installed": 5,
      "SYS_runtime": 5,
      "SYS_used": 5
    }
  },
  "campaign": {"episode": 4, "scene": 0, "px": 0},
  "team": {"members": []},
  "party": {"characters": []},
  "loadout": {},
  "economy": {"cu": 0, "wallets": {}},
  "logs": {
    "artifact_log": [],
    "market": [],
    "offline": [],
    "kodex": [],
    "alias_trace": [],
    "squad_radio": [],
    "hud": [],
    "psi": [],
    "arena_psi": [],
    "foreshadow": [],
    "fr_interventions": [],
    "flags": {
      "runtime_version": "4.2.3",
      "compliance_shown_today": false,
      "chronopolis_warn_seen": false
    }
  },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {}
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": false,
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
    "previous_mode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "tier": 1,
    "proc_budget": 0,
    "artifact_limit": 0,
    "loadout_budget": 0,
    "phase_strike_tax": 0,
    "damage_dampener": true,
    "team_size": 1,
    "queue_state": "idle",
    "zone": "safe",
    "fee": 0,
    "scenario": null,
    "started_episode": null,
    "last_reward_episode": null,
    "policy_players": [],
    "audit": []
  }
}
```

`campaign.rift_seeds[]` ist die **kanonische Quelle** für offene Seeds. Jede
Struktur enthält mindestens `id`, `epoch`, `label` und `status` (open/closed)
und kann optional `seed_tier: early|mid|late` sowie Metadaten `cluster_hint`
(1-25/80-150/400-1000) und freies `level_hint` tragen (reine QA-/Balance-
Hinweise, keine Gating-Logik). Der Normalizer hebt Legacy-Strings oder
uneinheitliche Felder auf Objektform und setzt unbekannte Status auf
`open`. Launch-Guards erwarten `location='HQ'` und lehnen Starts mit
aktiver Arena oder fehlenden Seeds ab. `logs.arena_psi[]` spiegelt
Phase-Strike-Events separat vom regulären `logs.psi[]`.
`arc_dashboard.offene_seeds[]` bildet diese Liste nur ab; der Normalizer
führt beide Blöcke beim Laden zusammen und schreibt sie gemeinsam zurück.
Toolkit-Generatoren tragen Seeds ausschließlich in `campaign.rift_seeds[]`
ein, damit Dispatcher, Arc-Dashboard und Debrief dieselbe Quelle nutzen.

**Single Source „Save v6“:** Modul 12 führt das _einzige_ kanonische Schema für
HQ-Deepsaves. README, Toolkit und QA-Notizen zitieren lediglich Auszüge, ohne
abweichende Felder zu definieren. Legacy-Schlüssel (Root-Felder oder
`team.members[]`) sind reine Import-Aliase; neue Saves entstehen ausschließlich
im v6-Format mit `party.characters[]`. Divergierende Doppelstrukturen gelten als
Fehler und werden beim Laden zusammengeführt.

### E2E-Trace-Schema {#e2e-trace}

`logs.trace[]` hält ein kompaktes E2E-Protokoll pro Modus/Szene. Jede Zeile
enthält mindestens `event`, `at` (ISO), `location`, `phase`,
`mission_type`/`campaign_mode`, `scene{episode,mission,index,total}` sowie
`foreshadow{progress,required,tokens,expected}`. Optionale Felder fassen HUD-
Overlay, Radio-/Alias-/Kodex-Zähler, Ökonomie (`economy{cu,wallets}`), FR-Bias
und Arena- oder Seed-Metadaten zusammen. Die Runtime ruft `record_trace()` bei
`StartMission()`, `launch_rift()` und `arenaStart()` auf, begrenzt die Liste auf
64 Einträge und spiegelt die Snapshots im HQ-Save (Fixtures enthalten
Beispiele). Das Trace ergänzt `logs.hud[]` und ersetzt keine Toasts.

**Phase-Feld:** HQ-Saves bleiben `phase: core`. Während der Mission setzt die
Runtime `state.phase`/`campaign.phase` automatisch auf `core|transfer|rift`
(immer Kleinbuchstaben) gemäß Missionstyp und Szenenzahl. Seeds geben nur den
Typ vor und überlassen das `phase`-Feld der Laufzeit; Uppercase-Werte gelten
als ungültig und werden beim Laden auf lowercase normalisiert.

**Accessibility-Felder:** Der Serializer schreibt stets `ui.gm_style` und
`ui.suggest_mode`. Felder für `contrast`, `badge_density` und `output_pace` sind
empfohlen; fehlen sie, setzt die Runtime Defaults (`standard`/`standard`/
`normal`) und loggt den Schritt im Accessibility-Toast. Saves dürfen diese
Felder weglassen, ohne dass Persistenz verloren geht; Smokes mit fehlenden
Feldern gelten als bestanden, wenn die Defaults greifen.

**Vollständiges Test-Save:** `internal/qa/fixtures/savegame_v6_test.json`
enthält den vollständig ausgefüllten v6-HQ-Save mit offenen Rift-Seeds,
Arena-Audit, Wallet-Split-Logs und Self-Reflection-Status. Er dient als
Referenz für Acceptance- und Load-Flows.

**High-Level-Progression:** `internal/qa/fixtures/savegame_v6_highlevel.json`
zeigt drei Stände (Lvl 8/120/520) mit Seed-Pools und optionaler
`seed_tier`-Kennzeichnung. Nutzung: Regression für Rifts und Endgame-Scaling;
die Datei liegt nur lokal als QA-Bezugspunkt und ist nicht Teil des
produktiven Wissensspeichers.

**Schema-voller QA-Save:** `internal/qa/fixtures/savegame_v6_full.json`
vereint Level 7/120/512 mit offenen und geschlossenen Seeds, vollständigem
UI-Block, Wallet-Splits, Arena-/PvP-/Psi-Logs sowie Merge-Conflict-Einträgen.
Der Datensatz belegt alle Pflichtcontainer des Save-Schemas und eignet sich
für Roundtrip-Tests und Loader-Dedupe.

### Voller HQ-Deepsave (Solo/Gruppe) {#full-save}

> Referenz-HQ-Block mit Quartier, Timeline, Squad und Feldnotizen. Alle
> Pflichtfelder bleiben erhalten; optionale Blöcke sind knapp, aber vollständig
> ausgefüllt, damit jede Spielleitung sofort den gesamten Charakterbogen
> nachvollziehen kann.

```json
{
  "save_version": 6,
  "zr_version": "4.2.3",
  "location": "HQ",
  "phase": "core",
  "campaign": {
    "episode": 1,
    "mission": 2,
    "mission_in_episode": 2,
    "scene": 0,
    "px": 2,
    "mode": "preserve",
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
    "id": "AGENT-01",
    "name": "Agent Nova",
    "rank": "Operator I",
    "level": 2,
    "xp": 120,
    "origin": {
      "epoch": "ITI-Nullzeit",
      "hominin": "Homo sapiens sapiens",
      "role": "CQB-Operator"
    },
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "attributes": {
      "STR": 3,
      "GES": 6,
      "INT": 4,
      "CHA": 2,
      "TEMP": 1,
      "SYS_max": 2,
      "SYS_installed": 2,
      "SYS_runtime": 2,
      "SYS_used": 2,
      "hp": 10,
      "hp_max": 10
    },
    "modes": ["mission_focus"],
    "self_reflection": true,
    "talents": ["Schleichprofi", "Pistolenschütze", "Reaktionsschnell"],
    "skills": ["CQB", "Taktische Analyse"],
    "implants": [
      {"name": "Reflex-Boost Microline", "sys_cost": 1, "effect": "+1 Initiative"},
      {"name": "Taktisches Ohrimplantat Mk I", "sys_cost": 1, "effect": "+1 Gehör"}
    ],
    "inventory": {
      "weapons": ["CQB-Kampfpistole (SD)", "Tactical Fighting Knife"],
      "armor": ["Kevlar-Weste Stufe II"],
      "gadgets": ["Multi-Tool Wraith", "Faseroptik-Kabelkamera", "Rauchgranate Mk I", "Micro-Breacher"],
      "consumables": ["Med-Patch"],
      "special": ["Notfall-Transponder"]
    },
    "quarters": {
      "id": "QTR-A17",
      "preset": "custom",
      "layout_tags": ["cqb_ready", "urban_ghost", "analyst_cell"],
      "deck": "HQ-A",
      "notes": "Schallgedämmte CQB-Zelle mit Analysten-Setup"
    },
    "stats": {
      "missions_completed": 2,
      "deaths": 1,
      "rifts_closed": 0,
      "shots_fired": 2
    }
  },
  "team": {"members": [{"id": "AGENT-01", "callsign": "Nova"}]},
  "party": {"characters": [{"id": "AGENT-01", "callsign": "Nova"}]},
  "loadout": {
    "AGENT-01": {
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
    "cu": 1650,
    "wallets": {
      "AGENT-01": {"name": "Agent Nova", "balance": 1650}
    }
  },
  "logs": {
    "artifact_log": [],
    "market": [],
    "offline": [],
    "kodex": [],
    "alias_trace": [],
    "squad_radio": [],
    "hud": [],
    "psi": [],
    "foreshadow": [],
    "fr_interventions": [],
    "flags": {
      "runtime_version": "4.2.3",
      "compliance_shown_today": true,
      "chronopolis_warn_seen": false
    },
    "field_notes": [
      {
        "agent_id": "AGENT-01",
        "mission": "Sydney 2000 – Maskottchen-Bio-Plot",
        "timestamp": "2000-09-15T20:30:00Z",
        "note": "Nano-Kapsel in der Logistik gesichert; Zelle neutralisiert."
      },
      {
        "agent_id": "AGENT-01",
        "mission": "Apollo 15 Abort Call",
        "timestamp": "1971-07-30T03:15:00Z",
        "note": "Saboteur in Tunnel S-03 gefesselt, Guidance-Daten korrigiert."
      }
    ]
  },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {
      "ITI": 0,
      "Ordo Mnemonika": 0,
      "Kausalklingen": 0
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
    "phase": "idle",
    "mode": "single",
    "previous_mode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "tier": 1,
    "proc_budget": 0,
    "artifact_limit": 0,
    "loadout_budget": 0,
    "phase_strike_tax": 0,
    "damage_dampener": true,
    "team_size": 1,
    "fee": 0,
    "scenario": null,
    "started_episode": null,
    "last_reward_episode": null,
    "policy_players": [],
    "audit": []
  }
}
```

**Optionale strukturierte Talente:** Wer statt reiner Strings klarere Tool-
Hooks benötigt, kann Talente auch als Objekte speichern. Die einfache Liste
bleibt unterstützt; beide Formen können gemischt werden.

```json
"talents": [
  "Schleichprofi",
  {"name": "Pistolenschütze", "tag": "ranged", "bonus": 2},
  {"name": "Menschenkenntnis", "tag": "interrogation", "bonus": 2}
]
```

Die Felder `tag` und `bonus` sind optional, helfen aber beim automatischen
Routen zu passenden Proben.

**Timeline-Notizen:** `arc_dashboard.timeline[]` speichert bedeutende Einsätze
mit optionalen Angaben zu ID, Epoche und Label; die Liste ist unabhängig von
`campaign.px`.

**Mission 5 Auto-Reset (Self-Reflection-Beispiel)**

```json
{
  "logs": {
    "hud": ["SF-OFF (Mission 5)", "GATE 2/2", "SF-ON (post-M5 reset)"],
    "self_reflection_history": [
      {"mission_ref": "EP04-MS05", "reason": "mission5_end", "ts": "2025-11-26T22:10:00Z"}
    ],
    "flags": {
      "foreshadow_gate_m5_seen": true,
      "self_reflection": true,
      "self_reflection_off": false,
      "self_reflection_auto_reset_at": "2025-11-26T22:10:00Z",
      "self_reflection_auto_reset_reason": "mission5_end",
      "self_reflection_last_change_reason": "mission5_end",
      "last_mission_end_reason": "aborted"
    }
  },
  "character": {"self_reflection": true},
  "ui": {"suggest_mode": false}
}
```

Das Beispiel zeigt den automatischen Reset nach Mission 5: HUD-Badge `SF-OFF`
bleibt bis zur Rückkehr sichtbar, `self_reflection_auto_reset_*` dokumentiert
den Zeitpunkt und den Missionsausgang (`completed` oder `aborted`), die optionale
`self_reflection_history[]` hält jeden Reset chronologisch fest. Nach dem
Debrief ist der Charakterwert maßgeblich (`self_reflection=true`), Log-Flags
spiegeln diesen Zustand und weisen keine `self_reflection_off`-Reste mehr auf.

**Self-Reflection-Priorität & Helper**
- Runtime und HUD lesen ausschließlich `character.self_reflection`; Log-Flags
  spiegeln den Charakterwert, ersetzen ihn aber nie.
- `set_self_reflection(enabled:boolean, reason?: string)` setzt
  `character.self_reflection` und `logs.flags.self_reflection` synchron, legt
  `self_reflection_changed_at/_reason` an, plant den Auto-Reset nach
  Mission 5 (`self_reflection_auto_reset_*`) und hängt auf Wunsch einen Eintrag
  an `logs.self_reflection_history[]` an, damit Wiederholungen nachvollziehbar
  bleiben.
- Auto-Reset feuert nach Mission 5 immer, egal ob Abschluss oder Abbruch, und
  setzt sowohl HUD-Badge als auch Charakterwert auf `SF-ON` zurück.

- Pflichtfelder: `character.id`, `character.attributes.SYS_max`,
  `character.attributes.SYS_installed`, `character.attributes.SYS_runtime`,
  `character.attributes.SYS_used`, `character.stress`, `character.psi_heat`,
  `character.cooldowns`, `campaign.px`, `economy` (inklusive `wallets{}`),
  `logs` (inklusive `hud`, `artifact_log`, `market`, `offline`, `kodex`,
  `alias_trace`, `squad_radio`, `foreshadow`, `fr_interventions`, `psi`,
  `flags`), `ui` und `arena`. Der Market-Trace hält maximal 24 Einträge und
  schneidet ältere automatisch ab.
- **Paradoxon-Index:** `campaign.px` ist die einzige Quelle für Px-Stand und
  Progression. Rifts erzeugen kein separates `rift_px`; Importpfade verwerfen
  abweichende Felder und mappen Legacy-Keys zurück auf `campaign.px`.
- Optionales Feld: `modes` – Liste aktivierter Erzählmodi.
- Im HQ sind `character.attributes.SYS_installed` und
  `character.attributes.SYS_max` deckungsgleich, `SYS_runtime` liegt höchstens
  bei der installierten Last, `stress = 0`, `psi_heat = 0`. Das Speichern
  erfasst diese Werte, damit GPT den Basiszustand prüfen kann. Die JSON-
  Beispiele in diesem Modul zeigen weiterhin volle SYS-Werte (5/5 bzw. 6/6)
  und erfüllen damit den Guard.
- GPT darf keine dieser Angaben ableiten oder weglassen. Der Serializer setzt
  fehlende Pflichtblöcke automatisch auf sichere Defaults (`economy.cu = 0`,
  leere Logs mit `logs.flags`, `ui.gm_style = "verbose"`).
- `party.characters[]` ist die kanonische Gruppenstruktur. Legacy-Saves mit
  `Charaktere` (DE) oder reinen Arrays werden beim Import auf diese Form
  normalisiert; Exporte und Debriefs verwenden ausschließlich die EN-Schreibweise.
- Array-only-Gruppensaves (ohne Objektfelder) werden beim Laden auf
  `party.characters[]` gehoben; anschließend legt
  `initialize_wallets_from_roster()` automatisch Wallets für alle IDs an und
  meldet den Schritt im HUD („Wallets initialisiert …“). `team.members[]`
  bleibt ausschließlich Migration und erscheint nicht in neuen Beispielblöcken.

### Cross-Mode Import – Solo → Koop/Arena {#cross-mode-import}

Cross-Mode-Sequenz (Solo → Koop → Arena → Debrief):
`load_save()` → `initialize_wallets_from_roster()` → `sync_primary_currency()` →
Arena-Gebühr über `arenaStart()` → Debrief `apply_wallet_split()`.

1. **Solo-Save laden.** `economy.wallets{}` ist zunächst leer; `party.characters[]`
   enthält nur den Protagonisten. Nach dem Laden läuft
   `initialize_wallets_from_roster()` automatisch und legt leere Wallets für alle
   aktiven Agent:innen an. Die Person, die den Save bereitstellt, ist der Host:
   Ihr Kampagnenblock (`episode`, `mission`, `mode`, `seed_source`,
   `rift_seeds[]`) gewinnt bei Konflikten den Vorrang; zusätzliche Crew-Saves
   dürfen nur Charaktere, Loadouts und Wallets beisteuern.
2. **Koop- oder Gruppeneinsatz starten.** Im Debrief erzeugt `apply_wallet_split()`
   für jedes Teammitglied eine Auszahlung und protokolliert den Vorgang als
   `Wallet-Split` in den HUD-Logs. `logs.arena_psi[]` dokumentiert parallel den
   zuvor aktiven Modus (`mode_previous`) für die Cross-Mode-Evidenz. Wallet-Werte
   stammen immer aus `economy.cu`/`wallets{}` – Credits nie per Hand direkt
   setzen.
3. **Arena aktivieren.** `arenaStart()` setzt `arena.policy_players[]`,
   `arena.previous_mode` und `arena.phase='active'`, markiert `location='ARENA'`
   und blockiert Save-Versuche bis zum Arena-Exit. Während der Serie blockiert
   der HQ-Save-Guard (`SaveGuard: Arena aktiv`). Beim Start zieht die Routine die
   Gebühr aus dem primären Economy-Feld und spiegelt sie via
   `sync_primary_currency()` auf `economy.cu` und `economy.credits`. Der
   Kampagnenmodus wird temporär auf `pvp` gesetzt, `campaign.previous_mode`
   sichert den alten Wert (`preserve`/`trigger`). Beim Exit schreibt die Runtime
   `arena.phase='completed'`, synchronisiert Px (+1 bei Sieg), stellt
   `campaign.mode = previous_mode` wieder her, leert `previous_mode` und erlaubt
   erneut HQ-Saves. `reset_arena_after_load()` bewahrt den letzten Modus über
   `arena.previous_mode`, falls mitten in einer Serie geladen wird, damit der
   Exit konsistent auf den Ursprungsmodus zurückspringt.

**Host-Regel für Mehrfach-Import:** Sobald mehrere Saves zusammengeführt
werden, bleibt der Kampagnenblock des Hosts maßgeblich. Fremdsaves dürfen weder
`campaign.mode` noch `campaign.rift_seeds[]` oder Episoden-/Missionszähler
überschreiben. Der Merge-Pfad zieht lediglich Charaktere, Loadouts und Wallets
heran und protokolliert abweichende Seeds im HUD/Debrief. Jeder abweichende
Wert (Seeds, Episoden-/Missions-/Szenenzähler, Seed-Quelle, UI-Optionen,
Arena- oder Non-HQ-States) landet zusätzlich in `logs.flags.merge_conflicts[]`
und wird als Host-Wert beibehalten; `load_deep()` schreibt ergänzend ein
`logs.trace[]`-Event `merge_conflicts` mit Arena-Phase/Queue-State/Zone,
Reset-/Resume-Markern, `conflict_fields`, `conflicts_added` und Gesamtzähler.
Unmittelbar nach dem Hydratisieren synchronisiert `ensure_economy()` den
HQ-Pool (`economy.cu`) mit dem Credits-Fallback, bevor Wallets geöffnet oder
Arena-Guards scharfgeschaltet werden.

### Accessibility-Preset (zweites Muster) {#accessibility-save}

```json
{
  "save_version": 6,
  "zr_version": "4.2.3",
  "location": "HQ",
  "phase": "core",
  "character": {
    "id": "CHR-7777",
    "name": "Jade",
    "rank": "Specialist",
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "attributes": {"SYS_max": 6, "SYS_installed": 6, "SYS_runtime": 6, "SYS_used": 6}
  },
  "campaign": {"episode": 12, "scene": 0, "px": 2},
  "team": {"members": []},
  "party": {"characters": []},
  "loadout": {},
  "economy": {"cu": 1200, "wallets": {"jade": {"balance": 1200, "name": "Jade"}}},
  "logs": {
    "artifact_log": [],
    "market": [],
    "offline": [],
    "kodex": [],
    "alias_trace": [],
    "squad_radio": [],
    "hud": [],
    "psi": [],
    "foreshadow": [],
    "fr_interventions": [],
    "flags": {
      "runtime_version": "4.2.3",
      "compliance_shown_today": true,
      "chronopolis_warn_seen": true,
      "offline_help_count": 1,
      "offline_help_last_scene": "HQ:4",
      "offline_help_last": "HQ:4"
    }
  },
  "arc_dashboard": {"offene_seeds": [], "fraktionen": {}},
  "ui": {
    "gm_style": "verbose",
    "intro_seen": true,
    "suggest_mode": false,
    "contrast": "high",
    "badge_density": "compact",
    "output_pace": "slow"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
    "previous_mode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "tier": 1,
    "proc_budget": 0,
    "artifact_limit": 0,
    "loadout_budget": 0,
    "phase_strike_tax": 0,
    "damage_dampener": true,
    "team_size": 1,
    "fee": 0,
    "scenario": null,
    "started_episode": null,
    "last_reward_episode": null,
    "policy_players": [],
    "audit": []
  }
}
```

Das Preset illustriert, wie ein `!accessibility`-Dialog persistiert wird: Der
Kontrast steht auf `high`, Badges nutzen das kompakte Layout und der Output
läuft im `slow`-Takt. Diese Werte bleiben erhalten, bis Nutzer:innen sie im HQ
zurücksetzen. HQ-Deepsaves erzwingen den kompletten UI-Block
(`gm_style`/`intro_seen`/`suggest_mode` plus `contrast`/`badge_density`/
`output_pace`); fehlt ein Feld, stoppt der SaveGuard und die Migration füllt
es auf `standard|normal` auf. Der Serializer mappt die Optionen 1:1 auf JSON:

- **Kontrast:** `contrast = standard|high`
- **Badge-Dichte:** `badge_density = standard|dense|compact`
- **Ausgabetempo:** `output_pace = normal|fast|slow`

Jede Bestätigung erzeugt den Toast „Accessibility aktualisiert …“ und schreibt
die Auswahl in `ui{}`. Legacy-Werte `full|minimal` werden beim Laden auf
`standard|compact` gemappt; `rapid|quick` landen auf `fast`,
`default|steady` auf `normal`. Saves ohne Badge-Feld setzen automatisch auf
`standard`.

## Laden & HQ-Rückkehr {#load-flow}

### Ablauf nach `!load`

 1. **Save posten.** `!load` erwartet den HQ-Deepsave als JSON und quittiert die
   Eingabe mit „Kodex: Poste Speicherstand als JSON.“
 2. **Deserializer starten.** Das hier dokumentierte `load_deep()`-Schema
   migriert Legacy-Felder in die v6-Struktur, prüft Pflichtblöcke und setzt
   `state.location='HQ'`. Die lokale `runtime.js` im Test-Container spiegelt
   diesen Pfad, gehört aber **nicht** zum Wissensspeicher.
3. **Rückblende & HUD.** `scene_overlay()` rendert nach dem Laden den HUD-Block
   „EP·MS·SC/Total·Px·SYS“. Die Runde springt ohne Nachfrage direkt zum HQ-
   beziehungsweise Briefing-Einstieg.
4. **Compliance-Spiegel.** `show_compliance_once()` ruft das Toolkit-Makro
   `ShowComplianceOnce()` (Alias `StoreCompliance()`) auf und synchronisiert
   `campaign.compliance_shown_today` mit `logs.flags.compliance_shown_today`.

{# LINT:FS_RESET_OK #}

> **Laufzeitabgleich:** Dieses Modul ist maßgeblich für GPT-basierte
> Spielleitungen. Die beigelegte `runtime.js` dient nur als Test-Spiegel für
> lokale Runs und wird nicht in produktive Wissensspeicher geladen.

**Mid-Session-Merge:** Für laufende Einsätze nutzt GPT statt `load_deep()` einen
leichten Merge-Pfad: Die Save-Blöcke werden ohne Location-Reset nach
`party.characters[]` kopiert, Wallets normalisiert und HUD/Timer beibehalten.
So können neue Agent:innen aufschlagen, während `state.location` auf Mission
steht; gespeichert wird trotzdem erst wieder im HQ.

### Kompatibilität & Guards

- Semver-Toleranz: Lädt, wenn `major.minor` der gespeicherten `zr_version` dem
  aktuellen `ZR_VERSION` entspricht; Patch-Level sind egal.
- Version-Mismatch liefert `Kodex-Archiv: Datensatz vX.Y nicht kompatibel mit
  vA.B. Bitte HQ-Migration veranlassen.`
- `campaign.exfil.active` oder `state.exfil.active` blockieren den HQ-Save mit
  „SaveGuard: Exfil aktiv – HQ-Save gesperrt.“
- Pflichtblöcke dürfen nicht geschätzt werden; der Serializer ersetzt fehlende
  Strukturen mit sicheren Defaults (Wallets `{}`, Logs als leere Arrays,
  `ui.gm_style="verbose"`).
- Story-Beispiel für den HQ-Guard: Abbruch kurz vor Mission 5-Boss → HUD meldet
  `BOSS`+`GATE 2/2`, Debrief schreibt `last_mission_end_reason=aborted`,
  Self-Reflection springt automatisch auf `SF-ON` und der Save bleibt bis zur
  Rückkehr ins HQ gesperrt.

### Persistente Debrief-Spiegel

- **Runtime-Flags.** `logs.flags.runtime_version` hält die erzeugende Version
  fest. Der Debrief bündelt sie unter `Runtime-Flags: …` inklusive
  Compliance-Status, Chronopolis-Warnung sowie Offline-Hilfe-Zähler plus
  Szene-Marker (`offline_help_last_scene`). Legacy-Felder
  `offline_help_last` werden beim Laden auf `offline_help_last_scene`
  gespiegelt.
- **Chronopolis & Markt.** `log_market_purchase()` schreibt Einkäufe nach
  `logs.market[]` (ISO-Timestamp, Artikel, Kosten, Px-Klausel).
  `render_market_trace()` erzeugt `Chronopolis-Trace (n×): …`.
  `chronopolis_warn_seen` bleibt beim Laden gesetzt und sorgt dafür, dass die
  City-Warnblende nur einmal auftaucht – auch nach Pre-City-Warncuts. Der
  Chronopolis-Schlüssel schaltet ab Level 10 frei: Der Serializer hält das
  erwartete Level unter `logs.flags.chronopolis_unlock_level=10`, markiert den
  Übergang mit `chronopolis_unlocked=true` und schreibt beim ersten Erreichen
  ein Trace-Event `chronopolis_unlock` (Quelle + Level). Der HUD-Toast
  „Chronopolis-Schlüssel aktiv – Level 10+ erreicht.“ dient als sichtbarer
  Beleg in der Acceptance-Checkliste.
- **Offline & Foreshadow.** `sanitize_offline_entries()` begrenzt
  `logs.offline[]` auf zwölf Einträge (Trigger, Gerät, Jammer, Reichweite,
  Relais, Szene/Episode). `render_offline_protocol()` fasst sie als
  `Offline-Protokoll (n×): …` zusammen. `normalize_save_v6()` dedupliziert
  `logs.foreshadow[]` (Tag, Kurztext, Szene, First/Last-Seen);
  Debriefs spiegeln `Foreshadow-Log (n×): …`.
- **Fraktionen & Funk.** `log_intervention()` protokolliert bis zu 16
  `logs.fr_interventions[]` (Ergebnis, Fraktion, Szene, Mission, Zusatzfelder)
  und spiegelt sie ins Arc-Dashboard; `render_alias_trace_summary()` fasst
  `logs.alias_trace[]` zu `Alias-Trace (n×): …` zusammen. Funkmeldungen landen
  via `log_squad_radio()` in `logs.squad_radio[]`; der Debrief liefert
  `Squad-Radio (n×): …`.
- **HQ-Rituale.** `campaign.hq_moments_used: string[]` dokumentiert Buffs
  (FOCUS/BASTION/SPARK/CALM/PULSE). Fehlt das Feld, setzt der Serializer `[]`;
  Debriefs nennen „HQ-Moments (n×)“ entsprechend. HUD-Logs übernehmen das
  jeweils gültige `hud_tag` (z. B. `HQ:CALM · Psi +1 (Mission)` bei CALM) und
  spiegeln so den aktiven Effekt.
- **Arena & Psi.** `ensure_arena()` konserviert PvP-Status, Phasen,
  Serienstände, Budget-Limits sowie `phase_strike_tax`. Sobald
  `phase_strike_cost()` greift, ruft die Runtime `log_phase_strike_event()`
  auf und legt in `logs.arena_psi[]` strukturierte Einträge mit
  `ability='phase_strike'`, `base_cost`, `tax`, `total_cost`, `mode`,
  `arena_active` und `category='arena_phase_strike'` an; optional ergänzt der
  Logger `mode_previous`, `location`, `gm_style` und `reason`.
  `prepare_save_logs()`/`sanitize_arena_psi_entries()` halten dieses Schema
  stabil und entkoppeln Arena-Psi-Logs von `logs.psi[]` (Psi-Heat/Story).
- **Arena-Reset nach Load.** `load_deep()` setzt `location='HQ'`,
  deaktiviert aktive Arena-Flags und kippt die Phase auf `completed` (falls ein
  Run lief) oder `idle`. Der Reset wird explizit genannt („Arena-Zustand auf HQ
  zurückgesetzt.“); die letzte Runde bleibt über `arena.previous_mode`
  nachvollziehbar. Lief die Serie noch, erzeugt die Runtime ein
  `arena.resume_token` (Tier, Teamgröße, Modus, Szenario, Audit,
  `previous_mode`), das `!arena resume` im HQ ohne erneute Gebühr reaktiviert.
- **Wallets.** `initialize_wallets_from_roster()` erzeugt fehlende Einträge in
  `economy.wallets{}` (Toast „Wallets initialisiert (n×)“). Saves führen immer
  ein Objekt – ggf. `{}`.
- **Self-Reflection.** `logs.flags` ergänzt Gate- und Reset-Felder
  (`foreshadow_gate_m5_seen`, `self_reflection_auto_reset_at`,
  `self_reflection_last_change_reason` usw.) für nachvollziehbare Debrief-Logs.

## Koop-Debrief & Wallet-Split {#koop-wallet-split}

Nach jeder Mission folgt auf den Belohnungsblock automatisch der Koop-Abschnitt.
`apply_wallet_split()` spiegelt das Ergebnis in `economy.wallets{}` und erzeugt
die Debrief-Zeilen.

### Hazard-Pay & HQ-Pool

- Enthält `outcome` ein `hazard_pay`-Feld (oder `economy.hazard_pay`), bucht die
  Runtime den Betrag zuerst auf `economy.cu` und loggt `Hazard-Pay: … CU
  priorisiert`.
- Anschließend meldet `apply_wallet_split()` den HQ-Stand als
  `HQ-Pool: <Betrag> CU verfügbar`. Restbeträge erscheinen in Klammern
  (`Rest 150 CU im HQ-Pool`).
- Reihenfolge und Restsummen bleiben deterministisch: Die Debrief-Zeile
  `Wallet-Split (n×)` listet IDs in Roster-Reihenfolge, verteilt Rundungsreste
  gleichmäßig von oben nach unten und schließt mit einem einzigen Hinweis auf
  den verbleibenden HQ-Pool (`Rest … CU im HQ-Pool`).

### Standard- und Sonderaufteilungen

1. **Standardaufteilung.** Ohne Vorgaben verteilt der GPT die Auszahlung
   gleichmäßig (`Wallet-Split (n×): Ghost +200 CU | …`).
2. **Solo→Koop.** Beim Moduswechsel initialisiert
   `initialize_wallets_from_roster()` leere Wallets für alle `party.characters[]`
   und verschiebt Solo-Guthaben in den HQ-Pool.
3. **Spezialschemata.** Sonderregeln kommen über `economy.split`/`wallet_split`.
   Prozentwerte (`percent`, `percent_share`) nutzt GPT als 0–1 bzw. 0–100 %.
   Verhältnisangaben (`ratio`, `weight`, `share_ratio`, `portion`) bleiben
   relative Anteile. Nicht zugewiesene CU verbleiben im HQ-Pool.
4. **Dialogführung.** Kodex nennt Standard und Alternativen (_„Standardaufteilung
   je 200 CU …“_) und dokumentiert Entscheidungen in Debrief oder
   Einsatzprotokoll.

### Persistenz & IDs

- `economy.wallets{}` speichert Balances anhand der IDs aus
  `party.characters[]`. Fehlt eine ID, erzeugt GPT einen Slug (`agent-nova`).
- Änderungen an Callsigns aktualisieren nur den Anzeigenamen; das Guthaben bleibt
  über die ID erhalten.
- Ohne lokale Runtime müssen GPT-Leitungen dieselben Schritte manuell
  beschreiben und die Werte in den Saveblock übertragen, damit Koop-Teams ihre
  CU-Historie nachvollziehen können.

**Legacy-Normalisierung (ohne runtime.js)**

- Encounter mit Alt-Saves laufen vollständig im LLM – es gibt keine
  JavaScript-Hooks im Produktivbetrieb. Deshalb erstellt die Spielleitung bei
  Legacy-Daten den `character{}`-Block manuell, bevor irgendetwas geladen oder
  geprüft wird:
  1. Alle vorhandenen Stammdaten (`id`, `name`, `rank`, `callsign`, `lvl`, `xp`)
     aus Root-Feldern in `character{}` kopieren und anschließend die
     Wurzelkopien löschen.
  2. `stress`, `psi_heat`, `psi_heat_max` und `cooldowns{}` ebenso in den
     `character`-Block übernehmen; `cooldowns{}` immer als Objekt führen.
  3. `character.attributes{SYS_max,SYS_installed,SYS_runtime,SYS_used}` aus
     `sys`/`sys_max`, `sys_installed`, `sys_runtime` bzw. `sys_used` bilden und
     dabei bestehende Werte aus `attributes{}` nur ergänzen – niemals
     überschreiben. Fehlt `SYS_installed`, setze es auf `SYS_used` oder den
     Maximalwert; `SYS_runtime` darf höchstens die installierte Last tragen.
  4. Wenn ein Legacy-Save `modes[]` oder `self_reflection` direkt an der
     Wurzel notiert hatte, landen sie jetzt ebenfalls in `character{}`.
- Abschließend kontrollierst du die Standard-Flags: **Psi-Puffer** gehören bei allen Agent:innen zur Grundausstattung. Fehlt `psi_buffer` in `character{}`, `team{}` oder `party.characters[]`, ergänze `true`.
- Danach verhält sich der Save wie ein natives v6-Dokument. Guards wie der
  HQ-Serializer, Log-Sanitizer und das Semver-Gate operieren erst auf dieser
  bereinigten Struktur.

Beim Laden liest die Spielleitung `modes` aus und ruft für jeden
Eintrag `modus <name>` auf. So bleiben etwa Mission-Fokus oder
Transparenz-Modus nach einem Neustart erhalten.

**Save-Beispiel mit `modes` inkl. `suggest`**

```json
{
  "ui": {"suggest_mode": true, "gm_style": "verbose"},
  "character": {"modes": ["mission_focus", "suggest"]},
  "logs": {"hud": ["· SUG", "Mission-Fokus"]}
}
```

Der Save hält sowohl die aktivierten Erzählmodi (`modes[]`) als auch den UI-Flag
`suggest_mode`. Beim Laden setzt GPT `modus suggest` und spiegelt das HUD-Tag
`· SUG` samt Mission-Fokus-Badge.

## Session-Suspend (Temporärer Snapshot) {#session-suspend}

> **Ziel:** Ihr könnt eine laufende Sitzung pausieren, ohne den HQ-Deepsave zu verletzen.
> `!suspend` schreibt einen flüchtigen Snapshot, `!resume` setzt ihn exakt einmal fort.

Der Suspend-Snapshot friert den laufenden Einsatz für eine Pause ein.
Er lebt außerhalb der regulären Save-Pipeline und verfällt nach 24 Stunden.
Der Deepsave im HQ bleibt weiterhin Pflicht, sobald Ihr die Episode wirklich abschließt.

**SuspendGuard (Pseudocode)**
```pseudo
assert not state.get('open_roll'), "Suspend nur zwischen Szenen oder nach einem Wurf-Ergebnis."
assert not state.get('exfil_active'), "Suspend blockiert während laufender Exfiltration."
snapshot = {
  "suspend_version": 1,
  "zr_version": state.get('zr_version'),
  "created_at": now(),
  "expires_at": now() + 24h,
  "volatile": true,
  "campaign": {
    "episode": state.campaign.episode,
    "scene": state.campaign.scene,
    "phase": state.campaign.phase
  },
  "mission": {
    "id": state.mission.id,
    "objective": state.mission.objective,
    "clock": state.mission.clock,
    "timers": state.mission.timers
  },
  "team": {
    "stress": state.team.stress,
    "psi_heat": state.team.psi_heat,
    "status": state.team.status,
    "cooldowns": state.team.cooldowns
  },
  "initiative": {
    "order": state.initiative.order,
    "active_id": state.initiative.active_id
  },
  "hud": {
    "timers": state.hud.timers
  },
  "flags": state.flags.runtime
}
write_tmp("suspend/" + state.campaign.id + ".json", snapshot)
toast("Suspend-Snapshot aktiv. Nutzt !resume, bevor 24h vergehen.")
state.flags.runtime["suspend_active"] = true
```

Der Snapshot speichert nur die taktisch relevanten Werte einer Szene.
Inventar, Shop-Angebote und Episoden-Belohnungen bleiben Teil des HQ-Deepsaves.
`volatile: true` stellt klar, dass der Snapshot nicht als vollwertiger Save gilt.

**ResumeFlow (Pseudocode)**
```pseudo
snapshot = read_tmp("suspend/" + state.campaign.id + ".json")
assert snapshot, "Kein Suspend-Snapshot gefunden."
assert now() < snapshot.expires_at, "Suspend-Snapshot abgelaufen. Bitte letzten HQ-Save laden."
assert snapshot.zr_version.major_minor == state.zr_version.major_minor,
       "Suspend-Version inkompatibel."
apply(state.campaign.scene = snapshot.campaign.scene)
apply(state.campaign.phase = snapshot.campaign.phase)
apply(state.mission.clock = snapshot.mission.clock)
apply(state.mission.timers = snapshot.mission.timers)
apply(state.team.stress = snapshot.team.stress)
apply(state.team.psi_heat = snapshot.team.psi_heat)
apply(state.team.status = snapshot.team.status)
apply(state.team.cooldowns = snapshot.team.cooldowns)
apply(state.initiative.order = snapshot.initiative.order)
apply(state.initiative.active_id = snapshot.initiative.active_id)
apply(state.hud.timers = snapshot.hud.timers)
state.flags.runtime.update(snapshot.flags)
delete_tmp("suspend/" + state.campaign.id + ".json")
toast("Suspend-Snapshot geladen. Fahrt an Szene " + state.campaign.scene + " fort.")
```

- `!resume` ist nur einmal pro Snapshot erlaubt; der Datensatz wird nach dem Laden gelöscht.
- Nach der Rückkehr ins HQ erwartet Euch weiterhin `!save`, damit Episoden-Belohnungen gesichert bleiben.
- Bei Ablauf des Snapshots informiert das HUD: „Suspend-Fenster verstrichen. Bitte HQ-Deepsave laden.“
- Der Snapshot konserviert Initiative-Reihenfolge und HUD-Timer, damit Konfliktszenen nach `!resume`
  lückenlos weiterlaufen.

**HUD-Feedback**

- Nach `!suspend`: Toast `HUD → Session eingefroren · Ablauf <24h`.
- Nach `!resume`: Overlay `Session fortgesetzt · Szene X/Y`.
- Nach Ablauf: Benachrichtigung `Suspend verworfen · HQ-Save nötig`.

**Best Practices**

- Nutzt `!suspend`, wenn Ihr mitten im Konflikt aufhören müsst, aber den Flow bewahren wollt.
- Legt direkt vor einer Pause eine Mini-Rekap an, damit `!resume` den Einstieg filmisch anschließen kann.
- Verlasst Euch nicht dauerhaft darauf: Der Snapshot ersetzt keinen Story-Fortschritts-Save im HQ.
## Makros im Überblick {#makros-im-ueberblick}

- `StartMission(total=12|14, type="core"|"rift")` – initiiert den Missionsfluss nach dem Load.
- `DelayConflict(4)` – verschiebt Konfliktszenen bis zur vierten Szene.
- `ShowComplianceOnce()` – blendet den täglichen Compliance-Hinweis ein und soll
  `logs.flags.compliance_shown_today=true` setzen. `SkipEntryChoice()` markiert
  parallel `flags.runtime.skip_entry_choice=true`; die Runtime übernimmt das
  Flag unverändert in den Einsatz.
- `Chronopolis-Warnung` – `start_chronopolis()` blendet das einmalige Warn-Popup
  ein und setzt `logs.flags.chronopolis_warn_seen=true`, damit die Sequenz nach
  dem ersten Besuch stumm bleibt.
- `ClusterCreate()` – legt bei Paradoxon 5 neue Rift-Seeds an.
- `ClusterDashboard()` – zeigt aktive Seeds mit Schweregrad und optionaler Deadline.
- `launch_rift(id)` – startet eine Rift-Mission aus einem Seed (nur nach Episodenende).
- `resolve_rifts(ids)` – markiert Seeds als geschlossen und passt Belohnungen an.
- `seed_to_hook(id)` – liefert drei Kurz-Hooks als Einsprungpunkte für die nächste Sitzung.

### Paradoxon-Index & Rift-Seeds (Kernlogik) {#paradoxon-index}

- Der Paradoxon-Index misst die Resonanz der Zelle mit dem Zeitstrom.
- Bei Stufe 5 löst `ClusterCreate()` 1–2 neue Rift-Seeds aus und markiert den
  Px-Reset als „anhängig“ (`px_reset_pending=true`, `px_reset_confirm=false`).
- Rift-Seeds sind erst nach Episodenende spielbar.
- Nach der Rift-Phase setzt der Debrief im HQ den Index auf 0, schreibt ein
  `logs.trace[]`-Event (`px_reset`) und bestätigt den Reset via
  `px_reset_confirm=true` und HUD-Toast, sobald die Crew im HQ ankommt.

**Single-Source-Paradoxon-Effekte:**

| Px-Stand | Wirkung (Runtime/HUD/Doku) |
| -------- | -------------------------- |
| 0–4      | Keine Maluswerte oder Sonderregeln. HUD zeigt den aktuellen Balken und nutzt `campaign.px` als einzige Quelle. Die optionale Px-Verlust-Regel greift nur, wenn sie bewusst aktiviert wurde (z. B. misslungene Hot-Exfil). |
| 5        | `ClusterCreate()` erzeugt 1–2 Seeds, markiert den Reset als ausstehend und verhindert weitere Px-Anstiege. HUD/Debrief notieren „Paradoxon-Index 5 erreicht – neue Rifts sichtbar“. Nach der Rift-Op springt der Wert auf 0 und der Reset-Toast bestätigt dies. |

Jeder weitere Px‑5‑Treffer **stapelt** Seeds im Pool – ein Limit existiert nicht.
`apply_rift_mods_next_episode()` liest ausschließlich **offene** Seeds aus und
setzt `sg_bonus` sowie `cu_multi = 1 + 0,2 × offene Seeds`, damit der Pool
gezielt als Schwellen- oder Loot-Hebel genutzt werden kann.

Die Px-Boni wirken ausschließlich im Debrief/HQ: Analyse‑ und Loot‑Boosts
werden dort aus `campaign.px` berechnet und beeinflussen die nächste
Operation; während der Mission existieren keine separaten Mid-Scene-Buffs
mehr, damit Seed-Stacking und Px-Anzeige dieselbe Quelle teilen.

Toolkit, Runtime und README referenzieren ausschließlich diese Tabelle; Legacy-
Varianten (Arc-spezifische Px, zusätzliche Stresswürfe) gelten als verworfen
und werden beim Laden ignoriert.

### Legacy-Kompatibilität (Gear-Alias)

> Hinweis für die Spielleitung: Beim Laden interpretiert ihr alte oder abweichende Gear-Bezeichnungen still
> auf die neuen Namen. Speichern nutzt stets die kanonischen Begriffe.

**Alias-Beispiele (erweiterbar):**
- "Kodex-Armbandverstärker" → **Comlink-Boostermodul (Ear-Clip)**
- "Multi-Tool-Armband" → **Multi-Tool-Handschuh**

### Immersiver Ladevorgang (In-World-Protokoll) {#immersives-laden}

- Kollektive Ansprache im Gruppenmodus („Rückkehrprotokoll für Agententeam …“).
- Synchronisierungs-Hinweis („Kodex synchronisiert Einsatzdaten aller Teammitglieder …“).
- Kurze Rückblende der letzten Ereignisse aus Sicht der Beteiligten.
- Individuelle Logbucheinträge sind erlaubt (ein Satz pro Char).

> **Kodex-Archiv** – Rückkehrprotokoll aktiviert.
> Synchronisiere Einsatzdaten: **Alex** (Lvl 3), **Mia** (Lvl 2).
> Letzte Einsätze konsolidiert. Paradoxon-Index: █░░░░ (1/5).
> Willkommen im HQ. Befehle? (Briefing, Shop, Training, Speichern)

### Abweichende oder fehlerhafte Stände (In-World-Behandlung)

- Leichte Formatfehler: als Kodex-Anomalie melden und in-world nachfragen.
- Inkonsistenzen: als Anomalie melden und einen Vorschlag zur Bereinigung anbieten.
- Unbekannte oder veraltete Felder: still ignorieren oder als Archivnotiz kennzeichnen.
- Semver-Mismatch: „Kodex-Archiv: Datensatz vX.Y nicht kompatibel mit vA.B. Bitte HQ-Migration veranlassen.“
- Ambige Saves: „Kodex-Archiv: Profilpluralität erkannt. Sollen *Einzelprofil* oder *Teamprofil* geladen werden?“

### Kanonisches DeepSave-Schema (Kurzfassung)

```json
{
  "zr_version": "4.2.3",
  "save_version": 6,
  "location": "HQ",
  "phase": "core",
  "campaign": {
    "episode": 1,
    "mission_in_episode": 2,
    "scene": 0,
    "px": 1,
    "paradoxon_index": 0,
    "fr_bias": "normal"
  },
  "character": {
    "id": "CHR-XXXX",
    "name": "Agent Name",
    "level": 3,
    "attributes": { "STR": 5, "GES": 10, "INT": 4, "CHA": 4, "TEMP": 2, "SYS_max": 4, "SYS_installed": 4, "SYS_runtime": 4, "SYS_used": 4 },
    "talents": ["Scharfschütze II", "Soldat I"],
    "bioware": ["Reflexverstärkung", "Muskelstärkung", "Stealth-Skin", "Adrenalin-Drüse"],
    "synergy": "Adaptive Ligament",
    "equipment": {
      "primary": "Resonanz-Sniper (SD)",
      "secondary": "Sidearm (SD)",
      "armor": ["Kevlar", "Helm 360°"],
      "gadgets": ["Medikit", "Nano-Bindepflaster"]
    },
    "ammo": 10,
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {}
  },
  "team": { "name": "NPC-Zelle", "members": [] },
  "party": { "characters": [] },
  "loadout": {
    "primary": "Resonanz-Sniper (SD)",
    "secondary": "Sidearm (SD)",
    "cqb": null,
    "armor": ["Kevlar", "Helm 360°"],
    "tools": ["Medikit", "Nano-Bindepflaster"],
    "support": []
  },
  "economy": { "cu": 0, "wallets": {} },
  "logs": {
    "artifact_log": [],
    "market": [],
    "offline": [],
    "kodex": [],
    "alias_trace": [],
    "squad_radio": [],
    "hud": [],
    "foreshadow": [],
    "fr_interventions": [],
    "arena_psi": [],
    "psi": [],
    "flags": {
      "runtime_version": "4.2.3",
      "chronopolis_warn_seen": false,
      "compliance_shown_today": false
    }
  },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {},
    "fragen": []
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": false,
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
    "previous_mode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "tier": 1,
    "proc_budget": 0,
    "artifact_limit": 0,
    "loadout_budget": 0,
    "phase_strike_tax": 0,
    "team_size": 1,
    "fee": 0,
    "scenario": null,
    "started_episode": null,
    "last_reward_episode": null,
    "policy_players": [],
    "audit": []
  }
}
```

> Gruppen-Save analog mit `party.characters[]`. Kein zweites Schema mit anderen Feldnamen.

#### Arc-Dashboard-Objekt

`arc_dashboard` sammelt alle Story-Hub-Einträge aus dem HQ-Dashboard. Das Feld ist optional, wird
aber vom Serializer automatisch nachgezogen und strukturiert:

- **`offene_seeds[]`** – Liste aktiver Missionsansätze. Einträge können Strings (Freitext-Notizen)
  oder Objekte (z. B. mit `id`, `titel`, `status`, `deadline`) sein. Optionales
  Feld `seed_tier` dient als Balancing-Hinweis (`early|mid|late`) ohne Freischalt-
  oder Sperrwirkung; alle Seeds bleiben ab Level 1 spielbar.
- **`fraktionen{}`** – Wörterbuch mit Fraktionsschlüsseln; Werte sind Objekte für Ruf, Haltung oder
  letzte Aktionen. Die Runtime ergänzt `last_intervention`, `last_result`, `last_updated` sowie
  `interventions[]` (max. sechs Snapshots aus `logs.fr_interventions[]` inklusive Wirkung/Notiz),
  sodass HQ-Dashboard, Kampagnenlog und Runtime denselben Stand anzeigen.
- **`fragen[]`** – Offene Forschungs- oder Storyfragen als kurze Strings oder Objekte.

Beim Laden normalisiert `load_deep()` das Objekt, entfernt Nullwerte und stellt sicher, dass alle
Listen echte Arrays sind. Unbekannte Zusatzfelder bleiben erhalten.

### Legacy-Aliase & Normalisierung

- `party.characters[]` ist die verbindliche Quelle für Gruppenroster. Laufzeit und Serializer lesen
  ausschließlich daraus.
- Historische Felder (`team.members[]`, `team.roster[]`, `group.characters[]`, `party.members[]`,
  `npc_team[]`) werden beim Laden automatisch nach `party.characters[]` gespiegelt. Doppelte Einträge
  erkennt `load_deep()` anhand von IDs, Callsigns oder Namen und entfernt sie.
- Beim Speichern repliziert der Serializer den bereinigten Cast zusätzlich nach `team.members[]`, um
  Kompatibilität mit älteren Tools zu bewahren – ohne voneinander abweichende Arrays. `team.members[]`
  ist somit immer eine 1:1-Kopie des kanonischen `party.characters[]`. GPT ergänzt neue Koop-Mitglieder
  ausschließlich im `party`-Block; `team.members[]` wird nur vom Serializer gespiegelt, damit Saves
  aus Solo- und Koop-Läufen keine widersprüchlichen Listen mehr besitzen.

- Einführung und Zielsetzung
- Einzelspieler-Speicherstände – Bewährte Logik beibehalten
- Gruppen-Spielstände – Neue Unterstützung für Teams
- Zeitlinien-Tracker und Paradoxon-Index
- Immersiver Ladevorgang: Rückblenden und Anschluss in der Erzählung
- Umgang mit fehlerhaften oder abweichenden Speicherständen
- Spielleitung bleibt in-world (Immersion der Spielleitung)
- Praxis-Beispiele für Speicherblöcke (Solo & Gruppe)
- Fazit

## Einführung und Zielsetzung

Das Speicherstand- und Fortsetzungssystem von **ZEITRISS 4.2.3** wird in Modul 12 vollständig
überarbeitet. Ziel ist es, eine klare, GPT-kompatible Speicher- und Fortsetzungsmechanik zu
gewährleisten, die langfristiges Spielen mit einer hohen Spielerzahl unterstützt – **ohne die
Immersion zu beeinträchtigen**. Die grundlegende **Save/Load-Logik** bleibt erhalten, wird aber
durch neue Funktionen erweitert. Entwickler:innen erhalten damit ein robustes, transparentes und
flexibles Speichersystem für Einzel- und Gruppenspiele mit GPT als Spielleitung.

**Wichtige Schwerpunkte der Überarbeitung sind unter anderem:**

- **Integration eines Zeitlinien-Trackers & Paradoxon-Index:** Jede Stabilisierung eines
  historischen Ereignisses wird im Speicher protokolliert (ID, Epoche,
  Kurzbeschreibung und ein Stabilitätswert von 3 bis 0). Erreicht ein Eintrag den
  Wert 3, steigt der Paradoxon-Index um +1.
- **Trennung von Einzelspieler- und Gruppen-Spielständen:** Klare Definition, wie Einzelcharakter-
  Speicherstände vs. Gruppenspielstände aufgebaut und gehandhabt werden.
- **Standardisiertes, maschinenlesbares Format (JSON) mit narrativer Einbettung:** Einführung eines
  einheitlichen Formats mit allen notwendigen Feldern (Name, Attribute, EP, Talente, Inventar, Kodex-
  Wissen etc.), damit der KI-Spielleiter (GPT) die Daten fehlerfrei einlesen kann. Das Format wird
  **In-World** präsentiert (etwa als Kodex-Archiv), sodass die Technik für Spieler unsichtbar bleibt.
- **Integration des Gruppen-Spielsystems:** Mechaniken zum Import vorhandener Einzelcharaktere in
  eine Gruppe, Export einzelner Gruppenmitglieder sowie nahtloses Hinzufügen oder Entfernen von
  Spielern aus laufenden Gruppen.
- **Fortsetzungs-Logik für GPT:** Formatregeln sorgen dafür, dass GPT den Speicherblock bei jedem
  Laden sicher erkennt, korrekt interpretiert und die Geschichte konsistent fortsetzt.
- **Automatische Rückblenden & Anschluss an vorherige Mission:** Ingame-Mechanismen (Logbuch, Déjà-
  vu, Kodex-Archiv) ermöglichen eine kurze Zusammenfassung der letzten Ereignisse – jetzt auch aus
  Sicht aller Gruppenmitglieder – beim Laden eines Spielstands, um den Übergang in die neue Mission
  atmosphärisch zu gestalten.
- **Umgang mit fehlerhaften Speicherständen:** Richtlinien dafür, wie die KI-Spielleitung auf
  abweichende oder beschädigte Savegames reagieren kann (etwa durch korrigierende Vorschläge oder
  Ingame-Nachfragen) – ohne die Immersion zu brechen.
- **In-World-Spielleitung:** Die Spielleitung durch GPT bleibt vollständig in der Spielwelt
  verankert. Sämtliche Erklärungen zum Laden/Speichern erfolgen durch Ingame-Elemente (z.B. den Kodex,
  NSCs oder ein „Nullzeit-Log“) und nicht als außenstehende Systemkommentare.
- **Beispiel-Speicherblöcke:** Bereitstellung von kommentierten Beispielen für typische
  Speicherstände (sowohl Solo- als auch Gruppen-Spielstände) im standardisierten Format, die als
  Vorlage dienen können.
- **Token-Lite-Modus:** Missionslog mit max. 15 Einträgen. Archivierte Rifts lassen sich auslagern, um Token zu sparen.
- **Archiv-ZIP:** Erledigte Missions-JSON lassen sich gebündelt zippen, um Langzeitkampagnen schlank zu halten.

Im Folgenden werden diese Punkte im Detail ausgeführt und das neue System erläutert.
Um Speicherplatz zu sparen, darf die SL erledigte Missionslogs gebündelt als ZIP-Archiv auslagern.
Beim Laden ladet ihr zuerst euren aktuellen Speicherstand.
Danach folgt, falls nötig, die ZIP-Datei. GPT erkennt so den bisherigen Missionsverlauf.
- Nach dem Laden zwingend `StartMission()` ausführen; Details siehe Abschnitt „Load-Pipeline“.

Speichern ist ausschließlich im **HQ** erlaubt. `cmdSave()` setzt dabei das
Exfil-Fenster zurück, leert Stress und schreibt Level, Rank, Würfelmodus,
offene Seeds sowie den ☆-Bonus in den JSON-Block.

### Deep Save {#deep-save}

`speichern` gibt stets einen vollständigen JSON-Block mit allen relevanten
Feldern aus. Wird das Kontextlimit überschritten, teile den Block in mehrere
Codefelder und sende sie nacheinander.

**DeepSave(state)**

1. Wandle den gesamten Zustand in einen JSON-Snapshot um.
2. Gib diesen Snapshot vollständig aus und ersetze damit jeden vorherigen Stand.

Incrementelle oder partielle Saves sind nicht vorgesehen; jeder Speichervorgang
überschreibt den gesamten vorherigen Zustand.

```javascript
function select_state_for_save(state) {
  return {
    zr_version: "4.2.3",
    save_version: 6,
    location: state.location,
    phase: state.phase,
    campaign: state.campaign,
    character: state.character,
    team: state.team,
    party: {
      characters: state.party?.characters ?? state.team?.members ?? []
    },
    loadout: state.loadout,
    economy: state.economy,
    logs: state.logs,
    ui: {
      gm_style: state.ui?.gm_style ?? "verbose",
      suggest_mode: !!state.ui?.suggest_mode
    },
    arena: state.arena,
    arc_dashboard: state.arc_dashboard
  };
}

function save_deep(state) {
  if (state.location !== "HQ") {
    throw new Error(toast_save_block("HQ-only"));
  }
  const payload = select_state_for_save(state);
  payload.checksum = sha256(JSON.stringify(payload)); // optional
  return JSON.stringify(payload);
}

function load_deep(json) {
  const data = JSON.parse(json);
  return hydrate_state(migrate_save(data));
}

function migrate_save(data) {
  if (!data.save_version) data.save_version = 1;
  if (data.save_version === 1) {
    data.campaign ||= {};
    data.save_version = 2;
  }
  if (data.save_version === 2) {
    data.ui ||= { gm_style: "verbose" };
    data.save_version = 3;
  }
  if (data.save_version === 3) {
    data.phase ||= "core";
    data.save_version = 4;
  }
  if (data.save_version === 4) {
    const character = data.character ||= {};
    const carryHeat = character.psi_heat ?? character.heat ?? 0;
    character.psi_heat = Number.isFinite(carryHeat) ? carryHeat : 0;
    if (character.psi_heat_max === undefined && character.heat_max !== undefined) {
      character.psi_heat_max = character.heat_max;
    }
    delete character.heat;
    delete character.heat_max;
    data.save_version = 5;
  }
  if (data.save_version === 5) {
    data.ui ||= { gm_style: "verbose" };
    data.ui.intro_seen = !!data.ui.intro_seen;
    data.save_version = 6;
  }
  return data;
}
```

`sha256()` dient lediglich der Entwicklungsprüfung; im regulären Spielbetrieb darf die Checksumme entfallen.

## Einzelspieler-Speicherstände – Bewährte Logik beibehalten

Für **Einzelspieler-Runden** (ein Chrononaut als Spielercharakter) bleibt die bisherige
Speichermechanik im Kern bestehen. Am Ende jeder Mission erzeugt das Spiel einen maschinell lesbaren
**Speicherblock** – idealerweise als strukturierten JSON-Code im Chat (z.B. in einem Code-Feld).
Entscheidend ist, dass das Format einheitlich und klar lesbar ist, sowohl für
Menschen als auch für das KI-Modell. Dadurch erkennt GPT zuverlässig, dass es sich um einen
Spielstand handelt, und kann alle relevanten Daten übernehmen, sobald der Speicherstand in eine neue
Spielsitzung geladen wird.

**Struktur und Inhalt eines Einzel-Speicherstands:** Der Speicherstand wird als zusammenhängender
Datenblock (z.B. in einem Code-Feld) dargestellt. Er enthält die wichtigsten Charakterdaten in
**beschreibender, narrativ eingebetteter Form**, aber **keine versteckten Befehle** oder unklare
Formulierungen. Alles ist neutral in der dritten Person gehalten, damit GPT es problemlos
interpretieren kann. Typische Felder eines Speicherstands sind unter anderem:

- **Grunddaten:** Name des Charakters, Herkunftsepoche (Zeit/Hintergrund), Level und
  Erfahrungspunkte (EP) bzw. Fortschritt.
- **Attribute:** Werte für Stärke, Geschicklichkeit, Intelligenz, Charisma etc. (inklusive
  Spezialattribute wie _Temporale Affinität_ oder _Systemlast_ für Chrononauten).
- **Fähigkeiten und Talente:** Eine Liste besonderer Talente, Fertigkeiten oder Ausbildungen der
  Figur.
- **Ausrüstung:** Inventarlisten, ggf. inklusive besonderer Gegenstände, Implantate, psionischer
  Fähigkeiten etc.
- **Charakterprofil:** Besondere Merkmale wie moralische Ausrichtung, Ruf oder Zugehörigkeiten (z.B.
  _„altruistisch“_, Rang im ITI, Beziehungen zu Fraktionen).
- **Errungenschaften:** Wichtige Erfolge aus vergangenen Missionen.
- **Kodex-Wissen:** Relevantes Wissen, das der Charakter im Kodex gespeichert hat – z.B.
  Erkenntnisse aus vergangenen Missionen, enthüllte Geheimnisse, bekannte NPCs oder historische
  Fakten, an die er sich erinnert.
- **Statistiken (optional):** Dinge wie absolvierte Missionen, gelöste Rätsel, besiegte Gegner usw.,
  falls für den Spielfortschritt von Belang.
- **Zeitlinien-Veränderungen (optional):** Wichtige Abweichungen im historischen Verlauf, die durch
  die Aktionen des Charakters verursacht wurden, inklusive Angabe eines Stabilitätsgrads der Änderung
  (siehe _Zeitlinien-Tracker_ weiter unten).

Nicht im Speicherstand enthalten sind in der Regel detailreiche Situationsbeschreibungen oder
komplette Dialogverläufe vergangener Missionen. Der Speicherstand soll **kompakt** bleiben –
ausreichend, um den Charakter konsistent weiterzuspielen, aber ohne den neuen Missionskontext mit
irrelevanten Altlasten zu überfrachten. Jede neue Mission beginnt erzählerisch „frisch“, und der
Spielstand liefert nur die nötigsten Zusammenfassungen der Vorgeschichte. So bleibt der Chat-Kontext
schlank, und GPT kann die Fortsetzung konsistent gestalten, ohne durch Rauschen alter Dialoge
verwirrt zu werden.

**Beispiel: JSON-Speicherstand für einen einzelnen Charakter.** Angenommen, Agent Alex hat Mission 1
abgeschlossen. Sein Speicherstand könnte folgendermaßen aussehen:

_{
  "Name": "Alex",
  "Epoche": "Gegenwart (2025)",
  "Level": 2,
  "Erfahrung": 15,
  "zr_version": "4.1.5",
  "version_hash": "4.1",
  "arc_dashboard": {"offene_seeds": [], "fraktionen": {}, "fragen": []},  # optional
  "Attribute": {"Stärke": 4, "Geschicklichkeit": 5, "Intelligenz": 5, "Charisma": 3},
  "Talente": ["Pistolenschütze", "Kryptographie"],
  "Inventar": ["Dietrich-Set", "Heiltrank", "Zeitscanner-Tablet"],
  "Kodex": ["Schlacht von Aquitanien 1356", "Chronomant Moros"],
  "Errungenschaften": ["Retter von Aquitanien"]
_}

_Erläuterung:_ In diesem Speicherblock sind alle zentralen Daten von Alex nach seiner ersten Mission enthalten.
Zum Beispiel hat er das Talent _Kryptographie_, besitzt ein Neuro-Link-Implantat,
ein Inventar mit

Gegenständen (Dietrich-Set, Heiltrank, Zeitscanner-Tablet)
und im **Kodex** stehen Einträge, die an
seine Erlebnisse aus einer Anfangsmission erinnern (Schlacht von Aquitanien 1356 etc.). Diese Informationen
reichen aus, um Alex in einer zukünftigen Mission konsistent weiterzuspielen. GPT kann daraus
entnehmen, **wer Alex ist, was er kann und was er erlebt hat**, ohne dass jedes Detail der ersten
Mission erneut im Prompt geladen werden muss.

```json
"field_notes": [
  {
    "agent_id": "ZE-A12",
    "mission": "Operation Cold Swap",
    "timestamp": "1958-06-02T14:07Z",
    "note": "Funkraum mit Ventil-Schalter entdeckt. PZ-2.5 aktiv."
  }
]
```

_Beispiel:_ Dieses optionale Feld sammelt kurze Einsatzmemos und hat keinerlei
Regelwirkung. Der Serializer legt ein leeres Array an, wenn keine Notizen
vorliegen; Validatoren akzeptieren auch Saves ohne `field_notes[]`.

Bestehende Einzelspieler-Spielstände aus früheren Versionen behalten dieses Format bei und
funktionieren weiterhin unverändert. Wer also bisher Solo-Abenteuer mit ZEITRISS gespielt hat, muss
nichts an alten Savegames ändern – sie können in ZEITRISS 4.2.3 direkt weitergenutzt werden.

## Gruppen-Spielstände – Neue Unterstützung für Teams

**Neu** im aktualisierten System ist die offizielle Unterstützung von **Gruppen-Spielständen**. Ein
einzelner Speicherblock kann nun mehrere Spielercharaktere umfassen. Dadurch lassen sich Gruppen von
Chrononauten gemeinsam speichern und laden, ohne die etablierte Einzelspieler-Mechanik zu stören.
Die bereits bekannte Datenstruktur eines Charakter-Datensatzes bleibt dabei erhalten und wird
lediglich erweitert: Statt eines einzelnen Charakter-Objekts können nun mehrere solcher Objekte im
Speicher vorhanden sein.

### Struktur eines Gruppen-Speicherstands

Um mehrere Charaktere in einem Savegame abzubilden, gibt es zwei naheliegende Ansätze im JSON-
Format:

- **Array von Charakterobjekten:** Der Speicherblock besteht aus einer Liste _\[...\]_, in der jedes
  Element ein vollständiges Charakter-Datenobjekt (wie oben beschrieben) ist.
- **Wrapper-Objekt mit Charakterliste:** Der Speicherblock ist ein JSON-Objekt mit einem Feld (z.B.
  _"Charaktere"_ oder _"Gruppe"_), das eine Liste aller Charakterobjekte enthält. Optional kann dieses
  Objekt zusätzliche gruppenweite Felder wie einen Gruppennamen enthalten.

Beide Varianten sind technisch handhabbar. Wichtig ist vor allem, dass GPT zuverlässig erkennt, dass
mehrere Charaktere vorliegen. Aus Gründen der Klarheit verwenden wir im Folgenden einen Wrapper-
Ansatz: ein JSON-Objekt mit dem Feld _"Charaktere"_, das eine Liste von Charakteren enthält, sowie
optional ein Feld für den **Gruppennamen**.

**Beispiel: JSON-Gruppenspielstand mit zwei Charakteren.** Angenommen, zwei Spieler (oder ein
Spieler mit zwei aktiven Charakteren) möchten ihre Figuren Alex und Mia gemeinsam als Team
speichern. Ein Gruppen-Spielstand im JSON-Format könnte so aussehen:

_{_

{
  "Gruppe": "Team Chronos",
  "zr_version": "4.1.5",
  "version_hash": "4.1",
  "arc_dashboard": {"offene_seeds": [], "fraktionen": {}, "fragen": []},  # optional
  "Charaktere": [
    { "Name": "Alex", "Epoche": "Gegenwart (2025)", "Level": 2 },
    { "Name": "Mia", "Epoche": "Victorianisches Zeitalter (1888)", "Level": 1 }
  ]
}

Hier besteht das Agenten-Team **“Team Chronos”** aus zwei Mitgliedern: Alex und Mia. Jeder Charakter
wird als separates Objekt mit all seinen Datenfeldern aufgeführt (der Übersicht halber sind oben
nicht alle Felder ausgeschrieben, aber in einem echten Save würden analog zu Alex auch Mias
Attribute, Talente, Inventar etc. vollständig aufgeführt sein). Das optionale Feld _"Gruppe"_ dient
als Teamname oder Identifikator der Gruppe. Es ist _nicht zwingend erforderlich_ – die Präsenz
mehrerer Objekte in _"Charaktere"_ signalisiert GPT bereits, dass es sich um einen Gruppen-
Spielstand handelt. Dennoch kann ein Gruppenname atmosphärisch hilfreich sein und vom Spielleiter in
Dialogen verwendet werden (z.B. _„Agententeam Chronos...“_).

Entscheidend ist: Die **Struktur pro Charakter bleibt identisch** zu einem Einzelspieler-
Speicherstand. Es gehen also keine Datenfelder verloren und es werden keine neuen speziellen Formate
pro Charakter erfunden – wir haben lediglich eine zusätzliche Ebene drumherum gesetzt, um mehrere
Datensätze zusammenzuhalten. Somit ist auch die **Abwärtskompatibilität** gegeben: Ein Einzel-
Charakter-Save sieht für GPT praktisch genauso aus wie ein Gruppen-Save, nur ohne die äußere Liste.

### Erkennung von Einzel- vs. Gruppen-Spielständen

Der KI-Spielleiter (GPT) muss sofort erkennen können, ob ein geladener Speicherblock einen einzelnen
Charakter enthält oder eine Gruppe. Diese Unterscheidung erfolgt **allein durch die JSON-Struktur**:

- **Einzelspieler-Speicherstand:** Besteht typischerweise aus **einem einzigen JSON-Objekt** mit
  Charakterdaten – kein äußerer Array und kein _"Charaktere"_-Feld. Auf oberster Ebene steht z.B.
  direkt _"Name": "Alex"_. GPT liest diese Struktur und sieht nur einen Charaktereintrag – damit ist
  klar, dass es sich um einen Solo-Spielstand handelt. _Beispiel:_ _{ "Name": "Alex", "Level": 2, ...
  }_ – kein Array, keine weiteren Objekte auf Top-Level außer diesem einen Charakter →
  **Einzelcharakter-Save**.
- **Gruppen-Speicherstand:** Erkennbar an **mehreren Charakterdatensätzen** in einem Container. Das
  kann eine JSON-Liste _\[ {...}, {...} \]_ sein oder ein Objekt mit einem Feld _"Charaktere"_ (bzw.
  analog), welches ein Array enthält. Sobald GPT mehr als ein Charakterobjekt findet, ist klar: Dieser
  Spielstand umfasst mehrere Figuren. Ein optionales Feld _"Gruppe"_/_"Team"_ kann die Gruppennatur
  untermauern, wird aber zur reinen Erkennung nicht benötigt. _Beispiel:_ _{ "Charaktere": \[
  {Char1-Daten}, {Char2-Daten} \] }_ – mehrere Objekte im Array → **Gruppen-Save**.

Im Klartext prüft GPT beim Laden eines Spielstands einfach die oberste Struktur: Ein einzelnes
Datenobjekt bedeutet Solo-Spiel; eine Liste oder ein _"Charaktere"_-Feld mit mehreren Objekten
bedeutet Gruppe. Diese Prüfung ist trivial und benötigt keine extra Kennzeichnung, solange wir das
Format konsequent einhalten.

### Eindeutige Identifikation von Charakteren (Metadaten)

Wenn mehrere Charaktere in einem Savegame enthalten sind, kann es hilfreich sein, jeden Eintrag mit
einer eindeutigen **ID** oder ähnlichen Metadaten zu versehen. Dies dient der robusten
Identifikation, insbesondere falls Charaktere ähnliche Namen haben oder sich über die Zeit ändern.
Ein optionales Feld wie _"ID"_ pro Charakter kann z.B. eine eindeutige Kennung (UUID oder ein
anderer einmaliger Code) enthalten.

_Beispiel eines Charakters mit ID:_

_{_

_"Name": "Alex",_

_"ID": "CHR-7f3a9b2e",_

_"Epoche": "Gegenwart (2025)",_

_..._

_}_

In einem Gruppenstand hätte dann jeder Charaktereintrag seine eigene ID. **Wozu das?** Bei der
Zusammenführung mehrerer Speicherstände oder dem späteren Aktualisieren einzelner Charaktere
innerhalb einer Gruppe kann GPT anhand der ID erkennen, ob ein Charakter bereits existiert oder neu
hinzukommt. So werden Duplikate vermieden:

- **Mit ID:** Lädt man einen neuen Speicherstand von Alex in eine bestehende Gruppe, in der Alex mit
  gleicher ID schon existiert, weiß das System, dass es **denselben Charakter** updaten soll (anstatt
  einen zweiten „Alex“ hinzuzufügen). Gleiches gilt beim erneuten Laden eines fortgeschrittenen
  Savegames: Die ID signalisiert GPT, welcher bestehende Gruppencharakter aktualisiert werden muss.
- **Ohne ID:** Versucht GPT, Charaktere anhand von Name + Epoche o. ä. zu unterscheiden. Das kann in
  vielen Fällen funktionieren, ist aber fehleranfälliger (z.B. könnten zwei Spieler zufällig beide
einen Charakter namens „Alex“ spielen, oder ein Charakter ändert seinen Decknamen zwischenzeitlich).

#### Konfliktfall ohne ID

Treffen zwei Einträge ohne ID aufeinander und stimmen **Name** sowie
**Epoche** überein, fragt das System nach. Entweder wird eine neue ID vergeben
oder der vorhandene Datensatz bewusst überschrieben. Auf diese Weise lassen sich
Duplikate vermeiden, ohne dass IDs zwingend erforderlich sind.

Eine technische UUID als ID ist daher **empfehlenswert** für langfristige, große Kampagnen, aber das
Feld bleibt optional. Das System funktioniert auch ohne – es verlässt sich dann ganz auf die
eindeutigen Namen oder Konstellationen. (In unseren obigen Beispielen haben wir der Einfachheit
halber keine IDs angegeben, um die Darstellung nicht zu verkomplizieren; in der Praxis könnte man
sie jedoch hinzufügen, um maximale Eindeutigkeit zu erzielen.)

### Laden und Zusammenführen von Speicherständen

Speichern bleibt strikt HQ-only. **Gruppen-Merges** dürfen aber auch mitten in einer laufenden Mission
passieren: Spielende posten ihre letzten HQ-Saves in den Chat, GPT liest die Charakterblöcke ein und
fügt sie ohne Timer- oder Szenen-Reset in die aktive Gruppe ein. Der laufende Einsatz bleibt
eingefroren, bis die neuen Agent:innen eingegliedert sind. **Je nach Situation passiert Folgendes:**

- **Solo-Spielstand laden (ein Charakter):** Wird ein einzelner Charakter-Speicherstand im HQ geladen
  (Format wie Alex im Beispiel oben), verfährt die Spielleitung wie gewohnt: GPT liest die
  Charakterdaten ein und setzt die Geschichte nahtlos mit **diesem einen Chrononauten** fort. Für den
  Spieler fühlt es sich an, als würde er genau dort weitermachen, wo er mit seinem Charakter aufgehört
  hat. Alle Werte, Inventargegenstände und Kodex-Einträge aus dem Save stehen zur Verfügung, und die
  neue Mission kann mit dem bekannten Helden beginnen. _(Dieser Ablauf entspricht dem bisherigen
  Fortsetzungsprozess in ZEITRISS.)_
- **Von Solo zu Gruppe (Charaktere hinzufügen):** Wer aus einem Solo-Spiel eine Gruppe bilden möchte,
  erledigt das spätestens im Briefing: Zuerst wird wie üblich der Solo-Charakter A geladen, anschließend
  folgt der Speicherblock von Charakter B. GPT erkennt die getrennten Datensätze und erzeugt daraus einen
  **Gruppen-Spielstand**. Charakter B wird als neues Gruppenmitglied ergänzt, ohne Charakter A zu
  überschreiben. Der Eintritt kann beim Briefing oder – falls die Mission schon läuft – als filmischer
  Drop-in in der aktuellen Szene passieren (z. B. Ankunft per Gate oder Funk-Handshake). Die Mission
  selbst wird dabei **nicht** zurückgesetzt.
- **Gruppenstart (mehrere Charaktere gemeinsam laden):** Mehrere Speicherstände können zum Session-
  Start hintereinander (oder gesammelt) ins HQ gepostet werden, wenn mehrere Spieler ihre Soloruns zu
  einem Team bündeln wollen. GPT konsolidiert diese Informationen zu **einem einzigen Gruppenstand**:
  Alle Charakterdaten bleiben separat erhalten, bilden aber nun ein gemeinsames Team. Kein Charakter
  überschreibt einen anderen; doppelte Saves derselben ID erkennt GPT und aktualisiert nur. Die
  Reihenfolge der Blöcke ist egal. Nach dem Zusammenführen setzt GPT Paradoxon-Index und offene Rifts
  auf **0**, damit der neue Run sauber im HQ beginnt. Das Toolkit zeigt den Reset-Pseudocode in
  `systems/toolkit-gpt-spielleiter.md` (Snippet `StartGroupMode()`); interne Dev-Stubs sind dafür
  nicht erforderlich.

> **Mid-Session-Beitritt:** Ein Missionsteam darf jederzeit neue HQ-Saves einwerfen. GPT friert die
> Szene kurz ein, mapt die neuen Charaktere auf `party.characters[]`, normalisiert Wallets und fährt
> dann mit unveränderten Timern/Clocks fort. Speichern bleibt dennoch HQ-only; ein Ausstieg mitten in
> der Mission erzeugt **keinen** neuen Save, sondern verweist auf den letzten HQ-Save oder einen
> temporären `!suspend`-Snapshot.

**Zusammengefasst:** Ein einzelner Savegame-Block ergibt einen einzelnen Charakter; mehrere
Savegame-Blöcke (gleichzeitig oder sukzessive) ergeben die Bildung bzw. Erweiterung einer Gruppe.
GPT erkennt das automatisch anhand der Formatstruktur und passt sein Vorgehen entsprechend an –
**ohne** dass der Spielleiter außerhalb der Welt eingreifen muss.

### Hinzufügen, Aktualisieren und Entfernen von Gruppenmitgliedern

Sobald ein Spiel im Gruppenmodus läuft, gelten einfache **Regeln für den Umgang mit Gruppen-
Spielständen**, damit GPT als Spielleiter nichts durcheinanderbringt:

- **Neuen Charakter hinzufügen:** Jeder zusätzliche Charakter-Datensatz, der in der aktuellen Gruppe
  noch nicht vorhanden war, wird als neues Gruppenmitglied ergänzt. GPT erzeugt intern einen neuen
  Charaktereintrag und übernimmt alle Werte aus dessen Savegame. _Beispiel:_ Die Gruppe bestand bisher
  nur aus Alex. Nun wird Mias Speicherstand hinzugefügt. Mia (neuer Name/ID) wird von GPT als neues
  Mitglied erkannt. Ergebnis: Gruppe = \[Alex, Mia\]. Beide stehen mit ihren vollen Daten zur
  Verfügung.
- **Bestehenden Charakter aktualisieren:** Wird ein Speicherstand geladen, der zu einem Charakter
  gehört, der bereits in der Gruppe existiert, so werden dessen Daten **aktualisiert**, nicht
  dupliziert. Hier kommt das Metadaten-Feld (ID) ins Spiel: GPT vergleicht die IDs (falls vorhanden)
  oder ersatzweise Name/Epoche. Stimmen diese überein, nimmt es an, dass es derselbe Charakter ist.
  _Beispiel:_ In einer laufenden Gruppe aus Alex und Mia werden zu Beginn der nächsten Mission beide
  aktualisierten Savegames neu geladen. GPT erkennt an Alex’ ID oder Namen, dass Alex schon Teil der
  Gruppe ist – also wird **kein zweiter Alex** hinzugefügt, sondern Alex’ bestehender Eintrag mit den
  aktuellen Werten versehen (die ohnehin dem Save entsprechen). Genauso für Mia. Die Gruppe \[Alex,
  Mia\] bleibt bestehen, nur dass nun beide auf dem neuesten Stand sind.
- **Keine Konflikte durch unterschiedliche Felder:** Charaktere können unterschiedliche Felder oder
  Listen in ihren Daten haben, ohne Probleme zu verursachen. Hat Charakter A z.B. ein Feld _"Psionik":
  \[\]_ (weil er keine psionischen Fähigkeiten hat) und Charakter B gar kein Feld _"Psionik"_ (weil es
  für sie nie relevant war), führt das zu keinerlei Konflikt. GPT interpretiert einfach jeden
  Charakterblock für sich. Fehlt ein Feld bei einer Figur, bedeutet das nur, dass diese Figur dazu
  keine Angaben hat – es ist kein globales Problem. Es gibt also keine Fehlermeldung oder Störung,
  sondern jeder Charakterdatensatz wird individuell vollständig gelesen.
- **Optionale gemeinsame Elemente:** Das System ist primär so ausgelegt, dass jede Figur **getrennte
  Daten** hat. Falls gewünscht, kann man aber auch gruppenweite Felder definieren – etwa ein
  gemeinsames _"Gruppeninventar"_ oder einen aktuellen _"Missionsstatus"_, die außerhalb der einzelnen
  Charakterobjekte im JSON stehen. Solche Felder gelten dann für die **gesamte Gruppe**. GPT würde sie
  als von allen geteilt interpretieren. _Beispiel:_ Man könnte dem Gruppen-JSON ein Feld _"Mission":
  "Paris 1943 – Einsatzbeginn"_ auf oberster Ebene hinzufügen. GPT weiß dann, dass alle Charaktere
  sich zu Beginn von Mission X (hier Paris 1943) befinden. Solche globalen Felder sind optional und
  sollten sparsam verwendet werden, um die Trennung der Charakterdaten klar zu halten.
- **Charaktere entfernen:** Wenn ein Charakter die Gruppe dauerhaft verlassen soll, kann dies
  einfach dadurch geschehen, dass sein Datenblock im nächsten Speicherstand **weggelassen** wird. GPT
  wird beim Laden merken, dass ein zuvor vorhandener Charaktereintrag nicht mehr vorhanden ist. Die
  Konsequenz in der Spielwelt wäre, dass diese Figur nicht mehr Teil der aktiven Gruppe ist.
  Idealerweise wird dies narrativ untermauert – etwa indem zuvor in der Geschichte erklärt wird,
  **warum** der Charakter die Gruppe verlässt (Ruhestand, eigene Mission, Tod etc.). Beim nächsten
  Laden fehlen seine Daten; GPT interpretiert das so, dass nur die verbleibenden Charaktere
  weitermachen. _(Hinweis: Der letzte gespeicherte Stand des entfernten Charakters kann
  selbstverständlich als Einzel-Save separat archiviert werden, falls er später wiederkommt oder solo
  weiterspielt – die Formatkompatibilität macht’s möglich.)_

Durch diese Regeln können Gruppen dynamisch **wachsen oder schrumpfen**, ohne Chaos im Speicherstand
zu verursachen.

**Beispiel – Zusammenführung Schritt für Schritt:** Spieler 1 und Spieler 2 haben jeweils einen
Chrononauten (Charakter A und B) in Solo-Missionen gespielt und Savegames erstellt. Für ein
gemeinsames Abenteuer laden sie beide Speicherblöcke in den neuen Chat. GPT sieht Charakter A und
Charakter B – unterschiedliche Namen/IDs, keine Überschneidungen – und formt intern ein Team
**\[A, B\]**. Anschließend begrüßt der Spielleiter diese neue Gruppe im Spiel (dazu mehr im
Abschnitt _Immersiver Ladevorgang_). Kommt später Spieler 3 mit Charakter C dazu, fügt man einfach
dessen Speicherstand hinzu: GPT erkennt C als neu → Gruppe wächst zu **\[A, B, C\]**. Falls hingegen
Spieler 2 vor der nächsten Mission seinen **aktualisierten** B-Speicher einfügt (z.B. nach einem
Level-Up), erkennt GPT an B’s ID/Name, dass dieser schon in \[A, B, C\] existiert, und
**aktualisiert nur B’s Werte**, anstatt einen zweiten B hinzuzufügen. Die Gruppe bleibt konsistent,
niemand wird dupliziert.

## Load-Pipeline (Autoload, Multi-JSON, Gruppen-Merge)

**Ziel:** Saves laden (Solo oder Gruppe), migrieren, im **HQ** fortsetzen und
`StartMission()` automatisch initialisieren.

### Autoload & Intents
- Erkennt *automatisch* gepostete JSON-Saves (Heuristik: `zr_version` plus Felder wie
  `character`, `Charaktere`, `team` oder `campaign`).
- Befehle: `!load`, „Spiel laden“, „Spielstand laden“, „Load“. Ohne JSON → Prompt:
  `Kodex: Load-Modus aktiv. Poste 1–N Speicherstände (Solo oder Gruppe). "Fertig" startet den Merge.`

### Multi-JSON Collector
- Akzeptiert mehrere JSON-Blöcke in **einer** oder **mehreren** Nachrichten.
- Sammelphase endet auf **„Fertig“** – oder bei Autoload sofort, wenn genau **ein** Save erkannt
  wurde.

### Validierung & Migration
- Wende `migrate_save()` auf jeden Block an (`save_version` hochsetzen, Defaults ergänzen).
- **Fortsetzung** erzwingen: `location = "HQ"` (Load-Guard; Speichern bleibt HQ-only).

### Merge-Regeln (Gruppe)
- Primärschlüssel: `character.id` → Update statt Duplikat.
- Fallback: `(name, epoche)` → Kollision: `Kodex: Doppelter Agent erkannt. Überschreiben [Ja/Nein]?`
- **CU**-Konten bleiben **pro Agent** separat; die Summe darf im Recap erscheinen.
- Team-NSCs werden additiv zusammengeführt (Duplikate pro Name max. 1×).
- Merge-Konflikte (z. B. Wallet-Delta, Modus-Wechsel, offene Seeds) landen
  **verpflichtend** in `logs.flags.merge_conflicts[]` mit `{field, source, target,
  mode?, note?, resolved:false}`. Seeds, Kampagnenzähler (Mission, Episode,
  Szene, Seed-Quelle), UI-Präferenzen (`gm_style`, `contrast`,
  `badge_density`, `output_pace`) und Arena-/HQ-Kontexte werden immer mit
  Host-Vorrang geloggt und behalten die Host-Werte. Bei Arena-Ladevorgängen
  erscheint zusätzlich ein HUD-Toast („Merge-Konflikt: Arena-Status
  verworfen“), das den Reset auf HQ dokumentiert.

### Recap & Start
- **StartMission()** direkt nach dem Load auslösen (Transfer ggf. temporär unterdrücken).
- **Compliance-Hinweis:** `ShowComplianceOnce()` vor dem Rückblick anzeigen; erscheint pro Tag nur
  1×. Der gesetzte Status liegt in `logs.flags.compliance_shown_today`; `SkipEntryChoice()`
  setzt parallel `flags.runtime.skip_entry_choice=true`, damit der übersprungene Einstieg
  dokumentiert bleibt – `StartMission()` respektiert ein bereits gesetztes Flag.
- **Kurzrückblick**: letzte Missionslogs, Paradoxon, offene Seeds, CU pro Agent und Summe,
  aktive Modi.
- **Einstieg** gemäß README: _„klassischer Einstieg“_ oder _„Schnelleinstieg“_.
  - HQ-Interlude nur als Text; kein `NextScene("HQ")`.
  - Danach Transfer-HUD einblenden und direkt `NextScene(loc=<Ziel>, role="Ankunft")`.

```mermaid
flowchart TD
  A[JSON erkannt ODER !load] -->|Multi-JSON| B[Migration]
  B --> C[Merge (ID, sonst Name+Epoche)]
  C --> D[Fortsetzung im HQ]
  D --> E[StartMission() (Transfer-Defer)]
  E --> F[ShowComplianceOnce() + Recap]
  F --> G{Einstieg wählen}
  G -->|Klassisch| H[Transfer-HUD → NextScene]
  G -->|Schnell| I[Transfer-HUD → NextScene]

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
