---
title: "ZEITRISS 4.2.0 – Runtime Stub & Routing Layer (Text-Edition)"
version: 4.2.0
tags: [system]
---

# ZEITRISS 4.2.0 – Runtime Stub & Routing Layer (Text-Edition)

_Plug-and-play Vorlagen für eure Entwickler – copy-pastable Pseudocode / JSON-Schemas._

---

## 1 | TEXT-ROUTER – Raum-IDs & Befehls-Alias-Map

```json
{
  "Gatehall": {
    "aliases": ["gate", "atrium", "hub"],
    "sub": {
      "briefing": "Mission-Briefing-Pod"
    }
  },
  "Mission-Briefing-Pod": {
    "aliases": ["briefing", "pod"],
    "parent": "Gatehall"
  },
  "Research-Wing": {
    "aliases": ["research", "labs"],
    "sub": {
      "lab-alpha": "Lab-Alpha",
      "workshop": "Workshop-Beta"
    }
  },
  "Lab-Alpha": { "aliases": ["alpha"], "parent": "Research-Wing" },
  "Workshop-Beta": { "aliases": ["beta"], "parent": "Research-Wing" },

  "Operations-Deck": {
    "aliases": ["ops", "operations"],
    "sub": {
      "vault": "Time-Shard-Vault",
      "scanner": "Seed-Scanner"
    }
  },
  "Time-Shard-Vault": { "aliases": ["vault"], "parent": "Operations-Deck" },
  "Seed-Scanner": { "aliases": ["scanner"], "parent": "Operations-Deck" },

  "Crew-Quarters": {
    "aliases": ["crew", "quarters"],
    "sub": {
      "common": "Common-Room",
      "sleep": "Sleep-Capsules"
    }
  },
  "Common-Room": { "aliases": ["common"], "parent": "Crew-Quarters" },
  "Sleep-Capsules": { "aliases": ["sleep"], "parent": "Crew-Quarters" },

  "Hangar-Axis": {
    "aliases": ["hangar"],
    "sub": {
      "jump": "Jump-Pads",
      "maint": "Maintenance-Bay"
    }
  },
  "Jump-Pads": { "aliases": ["jump"], "parent": "Hangar-Axis" },
  "Maintenance-Bay": { "aliases": ["maint"], "parent": "Hangar-Axis" }
}
```

> **Router-Call (pseudo)** > `resolveCommand("> go research") ➜ "Research-Wing"`

---

## 2 | GPT-SOCKET-API – `getRoomPopulation`

```typescript
interface PopulationRequest {
  seed: number; // epoch-secs or cryptographic RNG
  room_id: string; // canonical (e.g. "Research-Wing")
  player_rank: number;
  flags?: string[]; // optional campaign flags
}

interface NPC {
  id: string;
  role: string;
  quirk?: string;
  hook?: string;
}

interface RoomEvent {
  id: string;
  trigger: string; // "on_enter" | "on_command"
  skill_gate?: { attr: string; dc: number };
  on_success?: string; // plain-text description / effect token
  on_fail?: string;
}

interface PopulationResponse {
  npcs: NPC[]; // length ≤ slot spec
  events: RoomEvent[]; // length ≤ slot spec
}
```

_HTTP-like stub_

```http
POST /gpt/getRoomPopulation
Content-Type: application/json
{ …PopulationRequest }

200 OK
{ …PopulationResponse }
```

> **Call-Site**: bei Raum-Wechsel. Cache Response bis Spieler den Raum verlässt.

---

## 3 | PERSISTENZ – Paradox- & Seed-Stats

```jsonc
// Spielzustand (JSON) – wird nach jeder Aktion aktualisiert
{
  "paradox_level": 3,
  "paradox_points": 11,
  "open_seeds": [
    { "id":"LND‑1851‑SW", "epoch":"Victorian", "status":"open" }
  ],
  "player": {
    "hp": 18,
    "stress": 4,
    "rank": 37,
    "inventory": [...]
  },
  "current_room": "Operations-Deck"
}
```

_Getter-Helpers (pseudo JS):_

```javascript
export const getParadox = () => state.paradox_level;
export const getOpenSeeds = () => state.open_seeds.length;
export const incrementParadox = (pp = 1) => {
  state.paradox_level += pp;
  ParadoxPing();
  autoSave();
};
export const closeSeed = (id) => { ... };
export function ClusterCreate() {
  if (state.paradox_level < 5) return;
  const count = 1 + Math.floor(Math.random() * 2);
  for (let i = 0; i < count; i++) {
    state.open_seeds.push({
      id: `R-${Math.random().toString(36).slice(2,6).toUpperCase()}`,
      name: "Uncharted Rift",
      severity: 1 + Math.floor(Math.random() * 3),
      deadline: Date.now() + 72 * 3600 * 1000,
    });
  }
  state.paradox_level = 0;
  writeLine(`ClusterCreate spawned ${count} Rift-Seeds.`);
  autoSave();
}
```

---

## 4 | `Operations-Deck` – Stat-Ausgabe Snippet

```typescript
function renderOperationsDeck() {
  const lvl = getParadox();
  const open = getOpenSeeds();
  writeLine(`Open Rifts: ${open}  |  Paradoxon-Index: ${lvl}`);
  writeLine("> use scanner | > go vault | > go gate");
}
```

---

## 5 | SIDE-OP-STARTER – `jump rift-id`

```typescript
function loadParaCreatureEncounter(seed) {
  const enc = gpull(
    "gameplay/kreative-generatoren-begegnungen.md#para-creature-generator",
    seed.id,
  );
  state.encounter = { creature: enc.creature, loot: enc.loot };
  writeLine(`Rift spawns ${enc.creature.name}.`);
  if (enc.loot) {
    generate_para_artifact(enc.creature);
  }
}

function cmdJump(arg) {
  // arg = "LND‑1851‑SW"
  if (!state.arc_complete) {
    return writeLine("Rift access locked until der Arc abgeschlossen ist.");
  }
  const seed = state.open_seeds.find((s) => s.id === arg);
  if (!seed) return writeLine("Unknown Rift-ID.");
  loadParaCreatureEncounter(seed); // → uses Para-Creature generator
  // After victory:
  closeSeed(seed.id);
  writeLine("Seed sealed. Paradox pressure eased.");
  autoSave();
}
```

`loadParaCreatureEncounter` ruft den Para-Creature-Generator aus
`gameplay/kreative-generatoren-begegnungen.md#para-creature-generator`.

## 6 | REST-FUNKTION – Crew-Quarters

```typescript
function cmdRest() {
  if (state.current_room !== "Crew-Quarters") {
    return writeLine("You need to be in Crew-Quarters to rest.");
  }
  state.player.hp = MAX_HP;
  state.player.stress = 0;
  autoSave(); // JSON dump to disk / DB
  writeLine("You feel refreshed. HP & Stress reset.");
}
```

## 7 | SAVE-BEFEHL – HQ-Lock

```typescript
function cmdSave() {
  if (state.current_room !== "HQ") {
    return writeLine("Speichern nur im HQ möglich.");
  }
  autoSave();
  writeLine("Game saved.");
}
```

## 8 | PVP-ARENA – Matchmaking-Stub

```typescript
const ARENA_BASE_FEE = 250; // fixer Grundbetrag
function getArenaFee() {
  // 1 % des aktuellen Vermögens als Zusatzgebühr
  return Math.floor(ARENA_BASE_FEE + state.currency * 0.01);
}

function generateArenaScenario() {
  const mission = gpull("gameplay/kreative-generatoren-missionen.md#missions-generator");
  const epoch = gpull("gameplay/kreative-generatoren-missionen.md#epochen-generator");
  return { description: `${mission} @ ${epoch}` };
}

function majorityFaction(players) {
  if (players.length === 0) return "";
  const tally = {};
  for (const p of players) {
    tally[p.faction] = (tally[p.faction] || 0) + 1;
  }
  return Object.entries(tally).sort((a, b) => b[1] - a[1])[0][0];
}

function createFactionAllies(factionId, count) {
  const allies = [];
  for (let i = 0; i < count; i++) {
    const npc = gpull(
      "gameplay/kreative-generatoren-begegnungen.md#nsc-generator",
      { faction: factionId },
    );
    allies.push(npc);
  }
  return allies;
}

function createOpposingTeam(size) {
  const foes = [];
  for (let i = 0; i < size; i++) {
    const npc = gpull(
      "gameplay/kreative-generatoren-begegnungen.md#nsc-generator",
    );
    foes.push(npc);
  }
  return foes;
}

function createTeam(size, players, mode = "single") {
  if (players.length === 0) return [];
  const team = players.slice(0, size);
  const missing = size - team.length;
  if (missing > 0) {
    const fac =
      mode === "single" ? players[0].faction : majorityFaction(players);
    team.push(...createFactionAllies(fac, missing)); // NPC-Generator
  }
  return team;
}

function startPvPArena(teamSize = 1, players = [], mode = "single") {
  const fee = getArenaFee();
  if (state.currency < fee) {
    return writeLine("Not enough CU for Arena match.");
  }
  state.currency -= fee;
  const scenario = generateArenaScenario();
  const teamA = createTeam(teamSize, players, mode); // füllt mit Fraktionsmitgliedern
  const teamB = createOpposingTeam(teamSize); // GPT generiert Gegenteam
  state.arena = { active: true, teamA, teamB, scenario, winsA: 0, winsB: 0 };
  autoSave();
  writeLine(`PvP showdown started: ${scenario.description}`);
}

function arenaMatchWon(playerTeamWon = true) {
  if (!state.arena?.active) return;
  if (playerTeamWon) {
    state.arena.winsA++;
  } else {
    state.arena.winsB++;
  }
  if (state.arena.winsA >= 2 || state.arena.winsB >= 2) {
    exitPvPArena();
  }
}

function exitPvPArena() {
  if (!state.arena?.active) return;
  if (state.arena.winsA > state.arena.winsB) {
    state.paradox_level += 1; // Paradoxon-Bonus +1 Px nach gewonnener Best-of-Three-Serie
  }
  state.arena = { active: false, teamA: [], teamB: [], winsA: 0, winsB: 0 };
  autoSave();
  writeLine("Arena match ended.");
}
```

## 8 | MULTIPLAYER-RESET – Gruppenmodus starten

```typescript
function startGroupMode(players = []) {
  // Wird nach dem Einlesen mehrerer Savegames aufgerufen.
  // Schwierigkeitsgrad angleichen: Paradoxon-Index und offene Rifts zurücksetzen
  state.paradox_level = 0;
  state.open_seeds = [];
  deepSave();
  writeLine(
    `Group mode initiated for ${players.length} players. Paradoxon-Index reset.`,
  );
}
```

---

## 9 | DEEP SAVE HELPER

```typescript
function deepSave() {
  updateCharacterData(state); // vollständiger Spielzustand gespeichert
}

function generateId(prefix = "CHR") {
  const num = Math.floor(Math.random() * 10000)
    .toString()
    .padStart(4, "0");
  return `${prefix}-${num}`;
}
// Beim Erstellen eines neuen Charakters ruft das System `generateId()` auf und
// speichert die ID im Spielstand.
// `deepSave()` wird nach jeder Phase aufgerufen – so bleibt der Spielstand selbst bei Abstürzen aktuell.
```

---

### Zusammenfassung der To-Dos für Dev-Integrierung

1. **`router.json`** in euren Command-Parser laden.
2. **Endpoint / Stub** `getRoomPopulation` implementieren; Aufruf bei Raum-Wechsel.
3. **State-Objekt** & _deepSave()_ global verfügbar machen.
4. **Commands**

    - `go <alias>` (Navigation)
    - `look` (Raum-Refresh)
    - `jump <rift-id>` (Side-Op)
    - `rest` (Nur in Crew-Quarters)
    - `regelreset` (Spieler: Regelmodule neu laden, Warnhinweis)

    ```typescript
    if (cmd === "regelreset") {
      const ok = await confirm("Regelreset lädt alle Module neu. Fortfahren?");
      if (ok) {
        loadAllRuleModules();
        notify("Regeln neu geladen.");
      }
    }
    ```

5. **Para-Creature-Generator** bereits vorhanden – einfach aus `cmdJump` callen.
6. Nach jeder Phase `deepSave()` aufrufen; es gibt keine Delta-Saves.
7. Offene Backend-Hooks: `history_ok_preserve()` und `history_ok_trigger()` sind noch zu
   implementieren.
8. **QA-Tests:**
   - `scene_count`: Mission plant mindestens **12** Szenen.
   - `no_macro_leak`: Keine Ausgaben enthalten `<!--`.
   - `meta_filter`: Kein Seed setzt das Flag `meta_introspection`.

---
*© 2025 pchospital – private use only. See LICENSE.
