---
title: "ZEITRISS 4.2.2 – Runtime Stub & Routing Layer (Text-Edition)"
version: 4.2.2
tags: [system]
---

# ZEITRISS 4.2.2 – Runtime Stub & Routing Layer (Text-Edition)

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

## 3 | PERSISTENZ – Paradoxon- & Seed-Stats

```jsonc
// Spielzustand (JSON) – wird nach jeder Aktion aktualisiert
{
  "paradoxon_index": 3,
  "paradoxon_points": 11,
  "open_seeds": [
    { "id":"LND‑1851‑SW", "epoch":"Victorian", "status":"open" }
  ],
  "campaign": { "episode": 3, "mission_in_episode": 7, "mode": "preserve" },
  "arena": {
    "active": false,
    "winsA": 0,
    "winsB": 0,
    "last_reward_episode": 2,
    "phase_strike_tax": 0
  },
  "player": {
    "hp": 18,
    "stress": 4,
    "rank": 37,
    "inventory": [...]
  },
  "current_room": "Operations-Deck"
}
```

`campaign.episode` spiegelt die aktuelle Missions-Staffel, `campaign.mode`
markiert den aktiven Ablauf (z. B. `preserve`, `trigger`, `pvp`). Der Block
`arena` merkt sich, ob der Px-Bonus bereits vergeben wurde –
`last_reward_episode` bewahrt den Episodenstempel, damit kein Team denselben
Bonus farmen kann. `phase_strike_tax` notiert den aktuellen SYS-Aufschlag für
Phase-Strike (0 außerhalb der Arena, +1 im PvP-Sparring).

_Getter-Helpers (pseudo JS):_

```javascript
export const getParadoxon = () => state.paradoxon_index;
export const getOpenSeeds = () => state.open_seeds.length;
export const incrementParadoxon = (pp = 1) => {
  state.paradoxon_index += pp;
  ParadoxonPing();
  autoSave();
};
export const closeSeed = (id) => { ... };
export function ClusterCreate() {
  if (state.paradoxon_index < 5) return;
  const count = 1 + Math.floor(Math.random() * 2);
  for (let i = 0; i < count; i++) {
    state.open_seeds.push({
      id: `R-${Math.random().toString(36).slice(2,6).toUpperCase()}`,
      name: "Uncharted Rift",
      severity: 1 + Math.floor(Math.random() * 3),
      deadline: Date.now() + 72 * 3600 * 1000,
    });
  }
  state.paradoxon_index = 0;
  writeLine(`ClusterCreate spawned ${count} Rift-Seeds.`);
  autoSave();
}

export const campaignMode = (ctx = state) => {
  const raw = ctx?.campaign?.mode ?? state.campaign?.mode ?? 'preserve';
  const normalized = raw.toString().trim().toLowerCase();
  if (!normalized) return 'preserve';
  if (['pvp', 'arena', 'sparring'].includes(normalized)) return 'pvp';
  return normalized;
};

export const isPvP = (ctx = state) => {
  if (campaignMode(ctx) === 'pvp') return true;
  const arenaState = ctx?.arena ?? state.arena;
  return !!(arenaState && arenaState.active);
};

export const phaseStrikeTax = (ctx = state) => (isPvP(ctx) ? 1 : 0);
export const phaseStrikeCost = (ctx = state, base = 2) => base + phaseStrikeTax(ctx);
```

---

## 4 | `Operations-Deck` – Stat-Ausgabe Snippet

```typescript
function renderOperationsDeck() {
  const lvl = getParadoxon();
  const open = getOpenSeeds();
  writeLine(`Rift-Seeds: ${open}  |  Paradoxon-Index: ${lvl}`);
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
  writeLine("Seed sealed. Paradoxon pressure eased.");
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
const ARENA_FEE_BRACKETS = [
  { limit: 1000, rate: 0.01 }, // 1 % auf die ersten 1.000 CU
  { limit: 4000, rate: 0.02 }, // 2 % auf die nächsten 4.000 CU
  { limit: Infinity, rate: 0.03 }, // 3 % ab 5.000 CU
];

function getArenaFee(currency = state.currency || 0) {
  let remaining = Math.max(0, currency);
  let fee = ARENA_BASE_FEE;
  for (const bracket of ARENA_FEE_BRACKETS) {
    if (remaining <= 0) break;
    const taxable = Math.min(remaining, bracket.limit);
    fee += taxable * bracket.rate;
    remaining -= taxable;
  }
  return Math.floor(fee);
}

const ARENA_TIER_RULES = [
  { tier: 1, minLevel: 1, maxLevel: 5, artifactLimit: 0, procBudget: 3, loadoutBudget: 5 },
  { tier: 2, minLevel: 6, maxLevel: 10, artifactLimit: 1, procBudget: 4, loadoutBudget: 6 },
  { tier: 3, minLevel: 11, maxLevel: Infinity, artifactLimit: 1, procBudget: 5, loadoutBudget: 7 },
];

function resolveArenaTier(players = []) {
  const highestLevel = players.reduce((lvl, entry) => {
    const raw = entry?.level ?? entry?.character?.level ?? 1;
    const level = Number(raw);
    return Math.max(lvl, Number.isFinite(level) ? level : 1);
  }, 1);
  return (
    ARENA_TIER_RULES.find(
      (rule) => highestLevel >= rule.minLevel && highestLevel <= rule.maxLevel,
    ) || ARENA_TIER_RULES[0]
  );
}

function cloneLoadout(loadout) {
  if (!loadout || typeof loadout !== "object") return {};
  return JSON.parse(JSON.stringify(loadout));
}

function ensureArray(value) {
  if (Array.isArray(value)) return value.filter(Boolean);
  if (value === undefined || value === null || value === "") return [];
  return [value];
}

const ARENA_PROC_KEYS = ["support", "tools", "mods", "devices", "gizmos"];

function enforceProcBudget(loadout, limit, auditLog, label) {
  if (!Number.isFinite(limit) || limit < 0) return loadout;
  let remaining = limit;
  for (const key of ARENA_PROC_KEYS) {
    const items = ensureArray(loadout[key]);
    if (items.length === 0) continue;
    const kept = [];
    for (const item of items) {
      if (remaining > 0) {
        kept.push(item);
        remaining -= 1;
      } else {
        auditLog.push(
          `${label}: Proc-Budget erreicht – '${item}' aus ${key} deaktiviert`,
        );
      }
    }
    loadout[key] = kept;
  }
  return loadout;
}

const ARENA_ARTIFACT_KEYS = ["artifacts", "artifact", "legendary", "trophies"];

function extractArtifactEntries(loadout) {
  const entries = [];
  for (const key of ARENA_ARTIFACT_KEYS) {
    const value = loadout[key];
    if (Array.isArray(value)) {
      value.forEach((entry, index) => {
        if (entry) entries.push({ key, index, value: entry });
      });
    } else if (value) {
      entries.push({ key, index: null, value });
    }
  }
  // Zusatzcheck: Support-/Tool-Slots, falls Artefakt erwähnt wird
  for (const key of ARENA_PROC_KEYS) {
    const arr = ensureArray(loadout[key]);
    arr.forEach((entry, index) => {
      if (typeof entry === "string" && /artefakt|artifact/i.test(entry)) {
        entries.push({ key, index, value: entry, derived: true });
      }
    });
  }
  return entries;
}

function enforceArtifactLimit(loadout, limit, auditLog, label) {
  if (!Number.isFinite(limit) || limit < 0) limit = 0;
  const entries = extractArtifactEntries(loadout);
  let kept = 0;
  for (const entry of entries) {
    if (kept < limit) {
      kept += 1;
      continue;
    }
    auditLog.push(
      `${label}: Artefakt-Limit erreicht – '${entry.value}' entfernt`,
    );
    if (entry.index === null) {
      loadout[entry.key] = Array.isArray(loadout[entry.key]) ? [] : null;
    } else if (Array.isArray(loadout[entry.key])) {
      const arr = loadout[entry.key];
      const idx = arr.indexOf(entry.value);
      if (idx !== -1) {
        arr.splice(idx, 1);
      }
    }
  }
  return loadout;
}

function applyArenaTierPolicy(players, tierRule) {
  const audit = [];
  const sanitisedPlayers = players.map((entry) => {
    const label = entry?.name || entry?.callsign || "Agent";
    const clone = { ...entry };
    const loadout = cloneLoadout(entry?.loadout);
    enforceArtifactLimit(loadout, tierRule.artifactLimit, audit, label);
    enforceProcBudget(loadout, tierRule.procBudget, audit, label);
    clone.loadout = loadout;
    return clone;
  });
  return { tierRule, players: sanitisedPlayers, audit };
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
  const tierRule = resolveArenaTier(players);
  const { players: sanitisedPlayers, audit } = applyArenaTierPolicy(
    players,
    tierRule,
  );
  const fee = getArenaFee();
  const numericCurrency = Number(state.currency);
  state.currency = Number.isFinite(numericCurrency) ? numericCurrency : 0;
  if (state.currency < fee) {
    return writeLine("Not enough CU for Arena match.");
  }
  state.currency -= fee;
  const scenario = generateArenaScenario();
  const teamA = createTeam(teamSize, sanitisedPlayers, mode); // füllt mit Fraktionsmitgliedern
  const teamB = createOpposingTeam(teamSize); // GPT generiert Gegenteam
  const lastReward = state.arena?.last_reward_episode ?? null;
  const previousMode = typeof state.campaign?.mode === "string" ? state.campaign.mode : null;
  state.arena = {
    active: true,
    teamA,
    teamB,
    scenario,
    winsA: 0,
    winsB: 0,
    last_reward_episode: lastReward,
    tier: tierRule.tier,
    budget_limit: tierRule.loadoutBudget,
    proc_budget: tierRule.procBudget,
    artifact_limit: tierRule.artifactLimit,
    audit,
    policy_players: sanitisedPlayers,
    previous_mode: previousMode,
    phase_strike_tax: 0,
  };
  state.campaign.mode = "pvp";
  state.arena.phase_strike_tax = phaseStrikeTax();
  autoSave();
  writeLine(
    `PvP showdown started: ${scenario.description} · Tier ${tierRule.tier} (Budget ${tierRule.loadoutBudget}, Proc ${tierRule.procBudget}, Artefakte ${tierRule.artifactLimit})`,
  );
  if (audit.length > 0) {
    writeLine(`Arena-Loadout angepasst: ${audit.length} Eingriffe.`);
  }
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
    const episode = state.campaign?.episode ?? "freeplay";
    const alreadyRewarded =
      state.arena.last_reward_episode !== null &&
      state.arena.last_reward_episode === episode;
    if (!alreadyRewarded) {
      state.paradoxon_index += 1; // Px-Bonus nur einmal pro Episode
      state.arena.last_reward_episode = episode;
    }
  }
  const stamp = state.arena.last_reward_episode ?? null;
  const restoreMode = state.arena.previous_mode;
  state.arena = {
    active: false,
    teamA: [],
    teamB: [],
    winsA: 0,
    winsB: 0,
    last_reward_episode: stamp,
    phase_strike_tax: 0,
  };
  state.arena.previous_mode = null;
  state.campaign.mode = restoreMode && restoreMode.trim() ? restoreMode : "preserve";
  autoSave();
  writeLine("Arena match ended.");
}
```

## 8 | MULTIPLAYER-RESET – Gruppenmodus starten

```typescript
function startGroupMode(players = []) {
  // Wird nach dem Einlesen mehrerer Savegames aufgerufen.
  // Schwierigkeitsgrad angleichen: Paradoxon-Index und offene Rifts zurücksetzen
  state.paradoxon_index = 0;
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

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
