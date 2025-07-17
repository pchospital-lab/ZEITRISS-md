---
title: "ZEITRISS 4.1.6 – Runtime Stub & Routing Layer (Text-Edition)"
version: 4.1.7
tags: [systems]
---

# ZEITRISS 4.1.6 – Runtime Stub & Routing Layer (Text-Edition)

_Plug-and-play Vorlagen für eure Entwickler – copy-pastable Pseudocode / JSON-Schemas._

---

## 1 | TEXT-ROUTER – Raum-IDs & Befehls-Alias-Map

```jsonc
// router.json
{
  "Gatehall": {
    "aliases": ["gate", "atrium", "hub"],
    "sub": {
      "briefing": "Mission-Briefing-Pod",
    },
  },
  "Mission-Briefing-Pod": {
    "aliases": ["briefing", "pod"],
    "parent": "Gatehall",
  },
  "Research-Wing": {
    "aliases": ["research", "labs"],
    "sub": {
      "lab-alpha": "Lab-Alpha",
      "workshop": "Workshop-Beta",
    },
  },
  "Lab-Alpha": { "aliases": ["alpha"], "parent": "Research-Wing" },
  "Workshop-Beta": { "aliases": ["beta"], "parent": "Research-Wing" },

  "Operations-Deck": {
    "aliases": ["ops", "operations"],
    "sub": {
      "vault": "Time-Shard-Vault",
      "scanner": "Seed-Scanner",
    },
  },
  "Time-Shard-Vault": { "aliases": ["vault"], "parent": "Operations-Deck" },
  "Seed-Scanner": { "aliases": ["scanner"], "parent": "Operations-Deck" },

  "Crew-Quarters": {
    "aliases": ["crew", "quarters"],
    "sub": {
      "common": "Common-Room",
      "sleep": "Sleep-Capsules",
    },
  },
  "Common-Room": { "aliases": ["common"], "parent": "Crew-Quarters" },
  "Sleep-Capsules": { "aliases": ["sleep"], "parent": "Crew-Quarters" },

  "Hangar-Axis": {
    "aliases": ["hangar"],
    "sub": {
      "jump": "Jump-Pads",
      "maint": "Maintenance-Bay",
    },
  },
  "Jump-Pads": { "aliases": ["jump"], "parent": "Hangar-Axis" },
  "Maintenance-Bay": { "aliases": ["maint"], "parent": "Hangar-Axis" },
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
// campaign_state.json   (auto-save nach jeder Aktion)
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
export const incrementParadox = (pp = 1) => { ... };
export const closeSeed = (id) => { ... };
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
function cmdJump(arg) {
  // arg = "LND‑1851‑SW"
  const seed = state.open_seeds.find((s) => s.id === arg);
  if (!seed) return writeLine("Unknown Rift-ID.");
  loadParamonsterEncounter(seed); // → uses Paramonster generator
  // After victory:
  closeSeed(seed.id);
  writeLine("Seed sealed. Paradox pressure eased.");
  autoSave();
}
```

`loadParamonsterEncounter` ruft den Paramonster-Generator aus
`gameplay/kreative-generatoren-begegnungen.md#kreaturen-generator`.

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

## 6a | PVP-ARENA – Matchmaking-Stub

```typescript
const ARENA_BASE_FEE = 250; // fixer Grundbetrag
function getArenaFee() {
  // 1 % des aktuellen Vermögens als Zusatzgebühr
  return Math.floor(ARENA_BASE_FEE + state.currency * 0.01);
}

function generateArenaScenario() {
  // Stub: zieht ein Kurzszenario aus dem Missions-Generator
  const entry = pickRandom(missionPool);
  const place = pickRandom(epochPool);
  return { description: `${entry} @ ${place}` };
}

function majorityFaction(players) {
  const tally = {};
  for (const p of players) {
    tally[p.faction] = (tally[p.faction] || 0) + 1;
  }
  return Object.entries(tally).sort((a, b) => b[1] - a[1])[0][0];
}

function createFactionAllies(factionId, count) {
  // Hook: eigene NPC-Logik einbinden
  // Erwartet die Anzahl der Verbündeten und liefert ein Array entsprechender NPCs
  return [];
}

function createOpposingTeam(size) {
  // Hook: generiert das gegnerische Team nach euren Regeln
  // Erwartet die Teamgröße und gibt ein Array rivalisierender NPCs zurück
  return [];
}

function createTeam(size, players, mode = "single") {
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
    state.paradox_level = 0; // Reset nach gewonnener Best-of-Three-Serie
  }
  state.arena = { active: false, teamA: [], teamB: [], winsA: 0, winsB: 0 };
  autoSave();
  writeLine("Arena match ended.");
}
```

## 6b | MULTIPLAYER-RESET – Gruppenmodus starten

```typescript
function startGroupMode(players = []) {
  // Wird nach dem Einlesen mehrerer Savegames aufgerufen.
  // Schwierigkeitsgrad angleichen: Paradoxon-Index & Rifts zurücksetzen
  state.paradox_level = 0;
  state.open_seeds = [];
  autoSave();
  writeLine(
    `Group mode initiated for ${players.length} players. Paradoxon-Index reset.`,
  );
}
```

---

## 7 | AUTO-SAVE HELPER

```typescript
function autoSave() {
  fs.writeFileSync("campaign_state.json", JSON.stringify(state, null, 2));
}

function deltaSave(prevState, newState) {
  const delta = {};
  for (const k in newState) {
    if (prevState[k] !== newState[k]) delta[k] = newState[k];
  }
  fs.writeFileSync("campaign_state.delta.json", JSON.stringify(delta, null, 2));
}

function generateId(prefix = "CHR") {
  const num = Math.floor(Math.random() * 10000)
    .toString()
    .padStart(4, "0");
  return `${prefix}-${num}`;
}
// Beim Erstellen eines neuen Charakters ruft das System `generateId()` auf und
// speichert die ID im Savegame.
// Wird nach jeder Phase aufgerufen – so bleibt der Spielstand selbst bei Abstürzen aktuell.
```

---

### Zusammenfassung der To-Dos für Dev-Integrierung

1. **`router.json`** in euren Command-Parser laden.
2. **Endpoint / Stub** `getRoomPopulation` implementieren; Aufruf bei Raum-Wechsel.
3. **State-Objekt** & _autoSave()_ global verfügbar machen.
4. **Commands**

   - `go <alias>` (Navigation)
   - `look` (Raum-Refresh)
   - `jump <rift-id>` (Side-Op)
   - `rest` (Nur in Crew-Quarters)

5. **Paramonster-Generator** bereits vorhanden – einfach aus `cmdJump` callen.
6. Wöchentlich einen Full-Snapshot speichern, dazwischen `deltaSave` nutzen.

---
*© 2025 pchospital – private use only. See LICENSE.
