---
title: "ZEITRISS 4.2.3 – Runtime Stub & Routing Layer (Text-Edition)"
version: 4.2.3
tags: [meta]
---

# ZEITRISS 4.2.3 – Runtime Stub & Routing Layer (Text-Edition)

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
  "location": "HQ",
  "phase": "core",
  "open_seeds": [
    { "id": "LND‑1851‑SW", "epoch": "Victorian", "status": "open" }
  ],
  "campaign": {
    "episode": 3,
    "mission_in_episode": 7,
    "mode": "preserve",
    "px": 3,
    "missions_since_px": 2,
    "compliance_shown_today": false
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
    "previous_mode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "last_reward_episode": null,
    "tier": 1,
    "proc_budget": 0,
    "artifact_limit": 0,
    "loadout_budget": 0,
    "fee": 0,
    "phase_strike_tax": 0,
    "damage_dampener": true,
    "team_size": 1,
    "scenario": null,
    "policy_players": [],
    "audit": []
  },
  "character": {
    "hp": 18,
    "stress": 0,
    "rank": "Operator I",
    "attributes": { "SYS_max": 3, "SYS_installed": 3, "SYS_runtime": 0, "SYS_used": 3 }
  },
  "logs": {
    "hud": [],
    "foreshadow": [],
    "market": [],
    "artifact_log": [],
    "psi": [],
    "offline": [],
    "alias_trace": [],
    "squad_radio": [],
    "kodex": [],
    "flags": {
      "runtime_version": "4.2.3",
      "compliance_shown_today": false,
      "offline_help_last_scene": null,
      "offline_help_last": null,
      "offline_help_count": 0,
      "chronopolis_warn_seen": false
    }
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": false,
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal"
  }
}
```

`campaign.episode` spiegelt die aktuelle Missions-Staffel, `campaign.mode`
markiert den aktiven Ablauf (z. B. `preserve`, `trigger`, `pvp`). Der Block
`arena` notiert Laufzustand, Phase (`idle`/`active`/`completed`), Moduswechsel,
Budget-Limits und Episodenstempel für den Px-Bonus. `logs.psi` speichert die
jüngsten Phase-Strike-Traces (`ability='phase_strike'`, `base_cost`, `tax`,
`total_cost`, `mode`, `arena_active` plus optionale Felder wie
`mode_previous`/`location`/`gm_style`/`reason`), damit QA Cross-Mode-Evidenz
nachverfolgt. `logs.alias_trace`
hält Alias-Läufe (Persona, Cover, Status, Szene/Mission) fest, während
`logs.squad_radio` Funkmeldungen mit Sprecher, Kanal, Status und optionaler
Szene/Ort loggt – beide erscheinen im Debrief als `Alias-Trace (n×)` bzw.
`Squad-Radio (n×)`. `logs.flags` zählt Compliance-Hinweis, Offline-Hilfen sowie
die Runtime-Version – `runtime.js` erwartet diese Felder beim Laden, damit der
GPT dieselbe Persistenz bedient. `ui` hält GM-Stil, Intro-, Suggest- und
Accessibility-Flags (`contrast`, `badge_density`, `output_pace`) synchron mit
den Toolkit-Makros.

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
export const phaseStrikeCost = (ctx = state, baseOrOptions = 2) => {
  const options =
    typeof baseOrOptions === "object" && !Array.isArray(baseOrOptions)
      ? baseOrOptions
      : {};
  const base = Number.isFinite(baseOrOptions)
    ? Number(baseOrOptions)
    : Number.isFinite(options.base)
    ? Number(options.base)
    : 2;
  const tax = phaseStrikeTax(ctx);
  const total = base + tax;
  const feedback = options.feedback !== false;
  const logEnabled = options.log !== false;
  if (feedback && tax > 0) {
    hud.toast(`Arena: Phase-Strike belastet +${tax} SYS (Kosten ${total})`, "ARENA");
  }
  if (logEnabled && tax > 0) {
    logs.psi ||= [];
    logs.psi.push({
      ability: "phase_strike",
      timestamp: new Date().toISOString(),
      base_cost: base,
      tax,
      total_cost: total,
      mode: campaignMode(ctx),
      mode_previous: ctx?.arena?.previous_mode ?? null,
      arena_active: !!(ctx?.arena?.active),
      location: ctx?.location ?? state.location ?? null,
      gm_style: ui.gm_style,
    });
    if (logs.psi.length > 16) {
      logs.psi.splice(0, logs.psi.length - 16);
    }
  }
  return total;
};

export function applyArenaRules(ctx = state) {
  const arena = ctx?.arena;
  if (!arena || typeof arena !== "object") return null;
  const active = !!arena.active;
  arena.damage_dampener = active;
  arena.phase_strike_tax = active ? phaseStrikeTax(ctx) : 0;
  if (!active) return arena;
  const markBuffer = (entry) => {
    if (!entry || typeof entry !== "object") return;
    entry.psi_buffer = true;
  };
  markBuffer(ctx.character);
  if (ctx.team) {
    markBuffer(ctx.team);
    (ctx.team.members || []).forEach(markBuffer);
  }
  if (ctx.party) {
    (ctx.party.characters || []).forEach(markBuffer);
  }
  return arena;
}
```

### 3.1 | HUD- & Foreshadow-Logs

```javascript
const MARKET_LOG_LIMIT = 24;
const OFFLINE_LOG_LIMIT = 12;
const ALIAS_TRACE_LIMIT = 24;
const SQUAD_RADIO_LOG_LIMIT = 24;

function dedupeForeshadow(entries = []) {
  const byToken = new Map();
  const deduped = [];
  for (const entry of entries) {
    if (!entry || typeof entry !== 'object' || typeof entry.token !== 'string') continue;
    const token = entry.token.trim().toLowerCase();
    if (!token) continue;
    if (byToken.has(token)) {
      const existing = byToken.get(token);
      if (!existing.message && entry.message) existing.message = entry.message.trim();
      if (!existing.tag && entry.tag) existing.tag = entry.tag.trim();
      if (!Number.isFinite(existing.scene) && Number.isFinite(entry.scene)) {
        existing.scene = entry.scene;
      }
      if (!existing.last_seen && entry.last_seen) existing.last_seen = entry.last_seen;
      continue;
    }
    const record = {
      token,
      tag: entry.tag?.trim() || 'Foreshadow',
      message: entry.message?.trim() || '',
      scene: Number.isFinite(entry.scene) ? entry.scene : null,
      first_seen: entry.first_seen || entry.last_seen || new Date().toISOString(),
      last_seen: entry.last_seen || entry.first_seen || new Date().toISOString()
    };
    deduped.push(record);
    byToken.set(token, record);
  }
  return deduped;
}

function normalizeAliasEntry(entry = {}, fallback) {
  const timestamp = entry.timestamp || fallback || new Date().toISOString();
  const persona = (entry.persona || entry.identity || entry.agent || '').toString().trim();
  const cover = (entry.cover || entry.alias || entry.role || entry.legend || '').toString().trim();
  const status = (entry.status || entry.state || entry.result || '').toString().trim();
  const mission = (entry.mission || entry.op || '').toString().trim();
  const location = (entry.location || entry.site || entry.zone || '').toString().trim();
  const note = (entry.note || entry.details || entry.comment || '').toString().trim();
  const sceneIndex = Number.isFinite(entry.scene_index) ? entry.scene_index : Number.isFinite(entry.scene) ? entry.scene : null;
  const sceneTotal = Number.isFinite(entry.scene_total) ? entry.scene_total : null;
  if (!persona && !cover && !note) return null;
  const record = { timestamp };
  if (persona) record.persona = persona;
  if (cover) record.cover = cover;
  if (status) record.status = status;
  if (mission) record.mission = mission;
  if (location) record.location = location;
  if (Number.isFinite(sceneIndex)) record.scene_index = Math.max(0, Math.floor(sceneIndex));
  if (Number.isFinite(sceneTotal)) record.scene_total = Math.max(0, Math.floor(sceneTotal));
  if (note) record.note = note;
  return record;
}

function sanitizeAliasEntries(entries = []) {
  const fallback = new Date().toISOString();
  const sanitized = [];
  for (const entry of entries) {
    const normalized = normalizeAliasEntry(entry, fallback);
    if (normalized) {
      sanitized.push(normalized);
    }
  }
  if (sanitized.length > ALIAS_TRACE_LIMIT) {
    sanitized.splice(0, sanitized.length - ALIAS_TRACE_LIMIT);
  }
  return sanitized;
}

function normalizeRadioEntry(entry = {}, fallback) {
  const timestamp = entry.timestamp || fallback || new Date().toISOString();
  const message = (entry.message || entry.text || entry.content || '').toString().trim();
  if (!message) return null;
  const speaker = (entry.speaker || entry.from || entry.agent || entry.voice || '').toString().trim();
  const channel = (entry.channel || entry.band || entry.frequency || '').toString().trim();
  const status = (entry.status || entry.state || entry.tag || '').toString().trim();
  const severity = (entry.severity || entry.priority || entry.level || '').toString().trim();
  const note = (entry.note || entry.details || entry.comment || '').toString().trim();
  const location = (entry.location || entry.zone || '').toString().trim();
  const sceneIndex = Number.isFinite(entry.scene_index) ? entry.scene_index : Number.isFinite(entry.scene) ? entry.scene : null;
  const record = { timestamp, message };
  if (speaker) record.speaker = speaker;
  if (channel) record.channel = channel;
  if (status) record.status = status;
  if (severity) record.severity = severity;
  if (Number.isFinite(sceneIndex)) record.scene_index = Math.max(0, Math.floor(sceneIndex));
  if (location) record.location = location;
  if (note) record.note = note;
  return record;
}

function sanitizeRadioEntries(entries = []) {
  const fallback = new Date().toISOString();
  const sanitized = [];
  for (const entry of entries) {
    const normalized = normalizeRadioEntry(entry, fallback);
    if (normalized) {
      sanitized.push(normalized);
    }
  }
  if (sanitized.length > SQUAD_RADIO_LOG_LIMIT) {
    sanitized.splice(0, sanitized.length - SQUAD_RADIO_LOG_LIMIT);
  }
  return sanitized;
}

function ensureLogs() {
  state.logs ||= {};
  state.logs.hud = Array.isArray(state.logs.hud) ? state.logs.hud : [];
  state.logs.kodex = Array.isArray(state.logs.kodex) ? state.logs.kodex : [];
  state.logs.artifact_log = Array.isArray(state.logs.artifact_log)
    ? state.logs.artifact_log
    : [];
  state.logs.foreshadow = Array.isArray(state.logs.foreshadow)
    ? dedupeForeshadow(state.logs.foreshadow)
    : [];
  state.logs.market = sanitizeMarketEntries(state.logs.market);
  state.logs.offline = Array.isArray(state.logs.offline) ? state.logs.offline : [];
  state.logs.psi = Array.isArray(state.logs.psi) ? state.logs.psi : [];
  state.logs.alias_trace = sanitizeAliasEntries(state.logs.alias_trace);
  state.logs.squad_radio = sanitizeRadioEntries(state.logs.squad_radio);
  state.logs.flags ||= {};
  const flags = state.logs.flags;
  flags.runtime_version ||= ZR_VERSION;
  flags.compliance_shown_today = !!flags.compliance_shown_today;
  flags.chronopolis_warn_seen = !!flags.chronopolis_warn_seen;
  const offlineScene = typeof flags.offline_help_last_scene === 'string'
    ? flags.offline_help_last_scene
    : null;
  const offlineLast = typeof flags.offline_help_last === 'string'
    ? flags.offline_help_last
    : null;
  flags.offline_help_last_scene = offlineScene || offlineLast || null;
  flags.offline_help_last = flags.offline_help_last_scene;
  flags.offline_help_count = Math.max(0, Math.floor(flags.offline_help_count || 0));
  return state.logs;
}

function hud_toast(message, tag = "HUD") {
  const logs = ensureLogs();
  hudSequence = (hudSequence + 1) % 1_000_000;
  const entry = {
    id: hudSequence,
    tag,
    message,
    at: new Date().toISOString()
  };
  const log = logs.hud;
  log.push(entry);
  if (log.length > 32) {
    log.splice(0, log.length - 32);
  }
  writeLine(`[${tag}] ${message}`);
  return entry;
}

function registerForeshadow(token, details = {}) {
  ensureLogs();
  const normalized = (token || "").toString().trim().toLowerCase();
  if (!normalized) return null;
  const now = new Date().toISOString();
  const entries = state.logs.foreshadow;
  let entry = entries.find((item) => item.token === normalized);
  if (!entry) {
    entry = {
      token: normalized,
      tag: details.tag?.trim() || "Foreshadow",
      message: (details.message || "").trim(),
      scene: Number.isFinite(details.scene) ? details.scene : state.scene?.index ?? null,
      first_seen: now,
      last_seen: now
    };
    entries.push(entry);
  } else {
    entry.last_seen = now;
    if (!entry.message && details.message) entry.message = details.message.trim();
    if (!entry.tag && details.tag) entry.tag = details.tag.trim();
    if (!Number.isFinite(entry.scene) && Number.isFinite(details.scene)) {
      entry.scene = details.scene;
    }
  }
  sync_foreshadow_progress();
  return entry;
}

function ForeshadowHint(text, tag = "Foreshadow") {
  const cleaned = (text || "").toString().trim();
  if (!cleaned) throw new Error("ForeshadowHint: text fehlt.");
  const slug = cleaned.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
  registerForeshadow(`manual:${slug || Date.now()}`, { message: cleaned, tag });
  return hud_toast(`${tag}: ${cleaned}`, tag);
}

function log_market_purchase(item, cost, options = {}) {
  ensureLogs();
  const entry = normalize_market_entry({
    ...options,
    item,
    cost_cu: cost
  });
  if (!entry) throw new Error("MarketLog: Ungültiger Eintrag.");
  state.logs.market.push(entry);
  if (state.logs.market.length > MARKET_LOG_LIMIT) {
    state.logs.market.splice(0, state.logs.market.length - MARKET_LOG_LIMIT);
  }
  return entry;
}

function log_alias_event(details = {}) {
  ensureLogs();
  const entry = normalizeAliasEntry({ ...details }, new Date().toISOString());
  if (!entry) throw new Error("AliasTrace: Alias oder Persona fehlen.");
  state.logs.alias_trace.push(entry);
  if (state.logs.alias_trace.length > ALIAS_TRACE_LIMIT) {
    state.logs.alias_trace.splice(0, state.logs.alias_trace.length - ALIAS_TRACE_LIMIT);
  }
  return entry;
}

function log_squad_radio(details = {}) {
  ensureLogs();
  const entry = normalizeRadioEntry({ ...details }, new Date().toISOString());
  if (!entry) throw new Error("SquadRadio: Nachricht fehlt.");
  state.logs.squad_radio.push(entry);
  if (state.logs.squad_radio.length > SQUAD_RADIO_LOG_LIMIT) {
    state.logs.squad_radio.splice(0, state.logs.squad_radio.length - SQUAD_RADIO_LOG_LIMIT);
  }
  return entry;
}

function normalize_offline_entry(entry) {
  const now = entry.timestamp ?? new Date().toISOString();
  const reason = entry.reason ?? 'fallback';
  const status = entry.status ?? 'offline';
  const device = entry.device ?? state.comms?.device ?? null;
  const jammed = typeof entry.jammed === 'boolean' ? entry.jammed : !!entry.jammed;
  const range_m = Number.isFinite(entry.range_m) ? Math.max(0, Math.round(entry.range_m)) : null;
  const relays = Number.isFinite(entry.relays) ? Math.max(0, Math.floor(entry.relays)) : null;
  const scene_index = Number.isFinite(entry.scene_index) ? Math.max(0, Math.floor(entry.scene_index)) : state.scene?.index ?? 0;
  const scene_total = Number.isFinite(entry.scene_total) ? Math.max(1, Math.floor(entry.scene_total)) : state.scene?.total ?? 12;
  return {
    timestamp: now,
    reason,
    status,
    device,
    jammed,
    range_m,
    relays,
    scene_index,
    scene_total,
    episode: entry.episode ?? state.campaign?.episode ?? 0,
    mission: entry.mission ?? state.campaign?.mission ?? 0,
    note: entry.note ?? null,
    count: entry.count ?? 0
  };
}

function offline_audit(trigger = 'auto', context = {}) {
  const logs = ensureLogs();
  logs.offline ||= [];
  const payload = normalize_offline_entry({
    timestamp: new Date().toISOString(),
    reason: trigger,
    status: context.status || 'offline',
    device: context.device,
    jammed: context.jammed,
    range_m: context.range_m,
    relays: context.relays,
    note: context.note,
    count: logs.flags.offline_help_count,
    scene_index: context.scene_index,
    scene_total: context.scene_total,
    episode: context.episode,
    mission: context.mission
  });
  logs.offline.push(payload);
  if (logs.offline.length > OFFLINE_LOG_LIMIT) {
    logs.offline.splice(0, logs.offline.length - OFFLINE_LOG_LIMIT);
  }
  return payload;
}

function format_offline_report(entry, totalCount) {
  const parts = [];
  if (entry.reason === 'command') {
    parts.push('manueller Abruf');
  } else {
    parts.push('Fallback');
  }
  if (entry.device) parts.push(`Gerät ${entry.device}`);
  if (entry.jammed === true) parts.push('Jammer aktiv');
  if (entry.jammed === false) parts.push('Jammer frei');
  if (typeof entry.range_m === 'number') parts.push(`Reichweite ${entry.range_m} m`);
  if (typeof entry.relays === 'number') parts.push(`Relais ${entry.relays}`);
  return `Offline-Protokoll (${Math.max(1, totalCount)}×): ${parts.join(' · ')}`;
}
```

`sync_foreshadow_progress()` setzt `scene.foreshadows` gleich der deduplizierten
Log-Länge; Toolkit-Badges und `!boss status` greifen darauf zu.
`normalize_market_entry()` erzwingt ISO-Timestamps, rundet Kosten und ergänzt
`px_clause`, falls Px-Delta gesetzt ist. Die Runtime beschneidet die Market-
Historie auf die letzten 24 Einträge. `offline_audit()` spiegelt jeden Uplink-
Ausfall in `logs.offline[]` (maximal 12 Einträge) und `format_offline_report()`
liefert die Debrief-Zeile für HUD und Save.

### 3.2 | Offline- & Comms-Gating

```javascript
const OFFLINE_HELP_TOAST = 'Kodex-Uplink getrennt – Mission läuft weiter mit HUD-Lokaldaten.';
const OFFLINE_HELP_MIN_INTERVAL_MS = 60 * 1000;
const OFFLINE_HELP_GUIDE = [
  'Kodex Offline-FAQ (ITI↔Kodex-Uplink im Einsatz gekappt):',
  '- Terminal oder Hardline suchen, Relay koppeln, Jammer-Override prüfen – ' +
    'Kodex bleibt bis dahin stumm.',
  '- Mission normal fortsetzen: HUD liefert lokale Logs; HQ-Deepsaves/Cloud-Sync ' +
    'laufen erst nach der Rückkehr ins HQ (HQ-only, keine Save-Sperre).',
  '- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ markieren und ' +
    'Bestätigung abwarten.'
];

function kodex_link_state(ctx = state) {
  if (ctx.location === 'HQ' || ctx.phase === 'transfer') return 'uplink';
  const dev = ctx.comms?.device;
  const rng = ctx.comms?.range_m;
  const jam = ctx.comms?.jammed;
  const inBubble = dev === 'comlink' && typeof rng === 'number' && rng <= 2000 && !jam;
  return inBubble ? 'field_online' : 'field_offline';
}

function offline_help(trigger = 'auto') {
  const logs = ensureLogs();
  const flags = logs.flags;
  const now = Date.now();
  const last =
    typeof flags.offline_help_last === 'string'
      ? Date.parse(flags.offline_help_last)
      : NaN;
  if (!Number.isFinite(last) || now - last > OFFLINE_HELP_MIN_INTERVAL_MS) {
    hud_toast(OFFLINE_HELP_TOAST, 'OFFLINE');
  }
  const sceneIdx = Number.isFinite(state.scene?.index) ? state.scene.index : null;
  const sceneTotal = Number.isFinite(state.scene?.total) ? state.scene.total : null;
  const markerParts = [];
  if (state.location) markerParts.push(state.location);
  if (sceneIdx !== null && sceneTotal !== null) {
    markerParts.push(`SC${sceneIdx}/${sceneTotal}`);
  } else if (sceneIdx !== null) {
    markerParts.push(`SC${sceneIdx}`);
  }
  const marker = markerParts.join(':');
  const nowIso = new Date(now).toISOString();
  flags.offline_help_last = nowIso;
  flags.offline_help_last_scene = marker || nowIso;
  flags.offline_help_count = (flags.offline_help_count || 0) + 1;
  const entry = offline_audit(trigger, { count: flags.offline_help_count });
  const summary = format_offline_report(entry, flags.offline_help_count);
  return `${OFFLINE_HELP_GUIDE.join('\n')}\n\n${summary}`;
}

function require_uplink(ctx = state, action = 'command') {
  const status = kodex_link_state(ctx);
  if (status === 'uplink' || status === 'field_online') return true;
  offline_help('auto');
  throw new Error(
    'Kodex-Uplink getrennt – Mission läuft weiter mit HUD-Lokaldaten. ' +
      '!offline zeigt das Feldprotokoll bis zum HQ-Re-Sync.',
  );
}

function normalizeCommsOptions(options = {}) {
  const rawDevice = (options.device ?? '').toString().trim().toLowerCase().replace(/\s+/g, '_');
  const deviceMap = {
    comlink: 'comlink',
    commlink: 'comlink',
    'com-link': 'comlink',
    kabel: 'cable',
    cable: 'cable',
    relay: 'relay',
    relais: 'relay',
    jammer: 'jammer_override',
    jammer_override: 'jammer_override',
    'jammer-override': 'jammer_override',
    jammeroverride: 'jammer_override'
  };
  const device = deviceMap[rawDevice] || (rawDevice || null);
  const relays = Number.isFinite(options.relays) ? Math.max(0, options.relays) : (options.relays === true ? 1 : 0);
  const rangeKm = Number.isFinite(options.range_km) ? options.range_km : Number(options.range_km);
  const rawMeters = Number.isFinite(options.range_m) ? options.range_m : Number(options.range_m);
  const meters = Number.isFinite(rawMeters) && rawMeters > 0
    ? rawMeters
    : Number.isFinite(rangeKm) && rangeKm > 0
    ? rangeKm * 1000
    : null;
  const jammer = options.jammer ?? options.jammed ?? undefined;
  return { device, range_m: meters, relays, jammer };
}

function comms_check(options) {
  const normalized = normalizeCommsOptions(options);
  const device = normalized.device;
  const range = normalized.range_m;
  const okDevice = ['comlink', 'cable', 'relay', 'jammer_override'].includes(device);
  const jammed = normalized.jammer ?? !!state.comms?.jammed;
  const okRange = Number.isFinite(range) && (range * (state.comms?.rangeMod ?? 1)) > 0;
  if (!okDevice || !okRange) return false;
  const hasRelay = device === 'relay' || normalized.relays > 0;
  return !jammed || device === 'cable' || device === 'jammer_override' || hasRelay;
}

function radio_tx(options) {
  const normalized = normalizeCommsOptions(options);
  const ctx = {
    ...state,
    comms: {
      ...state.comms,
      device: normalized.device,
      range_m: normalized.range_m,
    },
  };
  require_uplink(ctx, 'radio_tx');
  if (!comms_check(normalized)) {
    throw new Error(
      'CommsCheck failed: require valid device/range or relay/jammer override. ' +
        'Tipp: Terminal suchen / Comlink koppeln / Kabel/Relay nutzen / Jammer-Override aktivieren; Reichweite anpassen. ' +
        'Mission läuft weiter mit HUD-Lokaldaten – !offline listet das Feldprotokoll.',
    );
  }
  return 'tx';
}
```

`radio_rx` spiegelt `radio_tx`. Toolkit-Befehle für `!offline` greifen auf denselben
Zähler zu, sodass QA-Läufe identische Hinweise liefern. `require_uplink()` hängt in
`must_comms()` sowie den Funk-Commands; jeder Abbruch erhöht den Offline-Counter und
triggert das HUD-Toast. `offline_help('command')` liefert neben dem FAQ die aktuelle
Zusammenfassung aus `logs.offline[]`.

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
const SAVE_REQUIRED_PATHS = [
  ['character', 'id'],
  ['character', 'cooldowns'],
  ['character', 'attributes', 'SYS_max'],
  ['character', 'attributes', 'SYS_installed'],
  ['character', 'attributes', 'SYS_runtime'],
  ['character', 'attributes', 'SYS_used'],
  ['character', 'stress'],
  ['character', 'psi_heat'],
  ['campaign', 'px'],
  ['economy'],
  ['economy', 'wallets'],
  ['logs'],
  ['logs', 'hud'],
  ['logs', 'foreshadow'],
  ['logs', 'artifact_log'],
  ['logs', 'market'],
  ['logs', 'offline'],
  ['logs', 'kodex'],
  ['logs', 'alias_trace'],
  ['logs', 'squad_radio'],
  ['logs', 'fr_interventions'],
  ['logs', 'psi'],
  ['logs', 'flags'],
  ['ui'],
  ['ui', 'gm_style'],
  ['ui', 'intro_seen'],
  ['ui', 'suggest_mode'],
  ['ui', 'contrast'],
  ['ui', 'badge_density'],
  ['ui', 'output_pace'],
  ['arena']
];

function enforceRequiredSaveFields(payload) {
  for (const path of SAVE_REQUIRED_PATHS) {
    let node = payload;
    for (const segment of path) {
      if (node == null || !(segment in node)) {
        throw new Error('SaveGuard: Feld ' + path.join('.') + ' fehlt.');
      }
      node = node[segment];
    }
    if (node === undefined || node === null) {
      throw new Error('SaveGuard: Feld ' + path.join('.') + ' fehlt.');
    }
  }
}

const toast_save_block = (reason) =>
  reason ? `SaveGuard: ${reason} – HQ-Save gesperrt.` : 'SaveGuard: HQ-Save gesperrt.';

function save_deep(ctx = state) {
  if (ctx?.arena?.active) throw new Error(toast_save_block('Arena aktiv'));
  if (ctx.location !== 'HQ') throw new Error(toast_save_block('HQ-only'));
  const c = ctx.character || {};
  const attrs = c.attributes || {};
  const sysMax = attrs.SYS_max ?? 0;
  const sysInstalled = attrs.SYS_installed ?? attrs.SYS_used ?? sysMax;
  const sysRuntime = attrs.SYS_runtime ?? sysInstalled;
  if (c.stress !== 0) throw new Error(toast_save_block('Stress aktiv'));
  if ((c.psi_heat ?? 0) !== 0) throw new Error(toast_save_block('Psi-Heat aktiv'));
  if (sysInstalled > sysMax) throw new Error(toast_save_block('SYS overflow'));
  if (sysRuntime > sysInstalled) throw new Error(toast_save_block('SYS runtime overflow'));
  if (sysInstalled !== sysMax) throw new Error(toast_save_block('SYS nicht voll installiert'));
  const payload = select_state_for_save(ctx); // siehe Abschnitt 3 (Persistenz)
  enforceRequiredSaveFields(payload);
  return JSON.stringify(payload);
}

function cmdSave() {
  if (state.location !== 'HQ') {
    return writeLine('Speichern nur im HQ möglich.');
  }
  save_deep(state);
  autoSave(); // Persistiert den JSON-String für QA
  writeLine('Game saved.');
}
```

Rift-Seeds landen konsolidiert in `campaign.rift_seeds[]`; der Loader hebt
Strings auf Objektform (`id`/`label`/`status`, optional `seed_tier` und
Cluster-/Level-Hints) und setzt fehlende Status auf `open`. Rift-Starts sind
HQ-gebunden (`location='HQ'`) und brechen ab, solange die Arena aktiv ist.

## 8 | PVP-ARENA – Matchmaking-Stub

```typescript
const ARENA_BASE_FEE = 250;
const ARENA_FEE_BRACKETS = [
  { limit: 1000, rate: 0.01 },
  { limit: 4000, rate: 0.02 },
  { limit: Infinity, rate: 0.03 }
];

const ARENA_TIER_RULES = [
  { tier: 1, minLevel: 1, maxLevel: 5, artifactLimit: 0, procBudget: 3, loadoutBudget: 5 },
  { tier: 2, minLevel: 6, maxLevel: 10, artifactLimit: 1, procBudget: 4, loadoutBudget: 6 },
  { tier: 3, minLevel: 11, maxLevel: Infinity, artifactLimit: 1, procBudget: 5, loadoutBudget: 7 }
];

const ARENA_PROC_KEYS = ['support', 'tools', 'mods', 'devices', 'gizmos'];
const ARENA_ARTIFACT_KEYS = ['artifacts', 'artifact', 'legendary', 'trophies'];
const ARENA_LOADOUT_KEYS = ['primary', 'secondary', 'gear', 'equipment', 'items'];
const ARENA_SCENARIOS = [
  'Offene Wüstenruine',
  'Labyrinth-Bunker',
  'Dschungel mit dichter Vegetation',
  'Urbanes Trümmerfeld',
  'Symmetrische Trainingsarena'
];
let arenaScenarioSerial = 0;

function ensureArray(value) {
  if (Array.isArray(value)) return value.filter(Boolean);
  if (value === undefined || value === null || value === '') return [];
  return [value];
}

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
        auditLog.push(`${label}: Proc-Budget erreicht – '${item}' aus ${key} deaktiviert`);
      }
    }
    loadout[key] = kept;
  }
  return loadout;
}

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
  for (const key of ARENA_PROC_KEYS) {
    const arr = ensureArray(loadout[key]);
    arr.forEach((entry, index) => {
      if (typeof entry === 'string' && /artefakt|artifact/i.test(entry)) {
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
    auditLog.push(`${label}: Artefakt-Limit erreicht – '${entry.value}' entfernt`);
    if (entry.index === null) {
      loadout[entry.key] = Array.isArray(loadout[entry.key]) ? [] : null;
    } else if (Array.isArray(loadout[entry.key])) {
      const arr = loadout[entry.key];
      if (entry.index >= 0 && entry.index < arr.length) {
        arr.splice(entry.index, 1);
      }
    }
  }
  return loadout;
}

function enforceLoadoutBudget(loadout, limit, auditLog, label) {
  if (!Number.isFinite(limit) || limit <= 0) return loadout;
  let remaining = limit;
  for (const key of ARENA_LOADOUT_KEYS) {
    const items = ensureArray(loadout[key]);
    if (items.length === 0) {
      loadout[key] = [];
      continue;
    }
    if (items.length <= remaining) {
      loadout[key] = items;
      remaining -= items.length;
      continue;
    }
    const kept = items.slice(0, remaining);
    const removed = items.slice(remaining);
    removed.forEach((item) => {
      auditLog.push(
        `${label}: Loadout-Budget erreicht – '${item}' aus ${key} entfernt`,
      );
    });
    loadout[key] = kept;
    remaining = 0;
  }
  return loadout;
}

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

function applyArenaTierPolicy(players, tierRule) {
  const audit = [];
  const sanitisedPlayers = players.map((entry) => {
    const label = entry?.name || entry?.callsign || 'Agent';
    const clone = { ...entry };
    const loadout = JSON.parse(JSON.stringify(entry?.loadout || {}));
    enforceArtifactLimit(loadout, tierRule.artifactLimit, audit, label);
    enforceProcBudget(loadout, tierRule.procBudget, audit, label);
    enforceLoadoutBudget(loadout, tierRule.loadoutBudget, audit, label);
    clone.loadout = loadout;
    return clone;
  });
  return { tierRule, players: sanitisedPlayers, audit };
}

function nextArenaScenario() {
  const idx = arenaScenarioSerial % ARENA_SCENARIOS.length;
  const description = ARENA_SCENARIOS[idx];
  arenaScenarioSerial = (arenaScenarioSerial + 1) % ARENA_SCENARIOS.length;
  return { description };
}

function gatherArenaPlayers() {
  const players = [];
  const character = ensure_character();
  const baseFaction = character.faction || state.team?.faction || 'Projekt Phoenix';
  players.push({
    name: character.name || character.callsign || character.id || 'Agent',
    level: Number(character.lvl ?? character.level ?? 1),
    faction: baseFaction,
    loadout: JSON.parse(JSON.stringify(state.loadout || {}))
  });
  const members = Array.isArray(state.team?.members) ? state.team.members : [];
  members.forEach((member, index) => {
    if (!member) return;
    const lvl = Number(member.lvl ?? member.level ?? character.lvl ?? 1);
    players.push({
      name: member.name || member.callsign || `Team-${index + 1}`,
      level: Number.isFinite(lvl) ? lvl : 1,
      faction: member.faction || baseFaction,
      loadout: JSON.parse(JSON.stringify(member.loadout || {}))
    });
  });
  return players;
}

const ECONOMY_PRIMARY_KEYS = ['credits', 'cu', 'balance', 'assets'];

function normalize_primary_currency(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return null;
  const rounded = Math.round(numeric);
  return rounded < 0 ? 0 : rounded;
}

function resolve_primary_currency(economy) {
  if (!economy || typeof economy !== 'object') return 0;
  for (const key of ECONOMY_PRIMARY_KEYS) {
    if (!(key in economy)) continue;
    const normalized = normalize_primary_currency(economy[key]);
    if (normalized !== null) {
      return normalized;
    }
  }
  return 0;
}

function sync_primary_currency(economy, override) {
  if (!economy || typeof economy !== 'object') return 0;
  let amount = override !== undefined ? normalize_primary_currency(override) : null;
  if (amount === null) {
    amount = resolve_primary_currency(economy);
  }
  if (amount === null) {
    amount = 0;
  }
  economy.cu = amount;
  economy.credits = amount;
  return amount;
}

function readArenaCurrency() {
  const economy = ensure_economy();
  for (const key of ECONOMY_PRIMARY_KEYS) {
    if (!(key in economy)) continue;
    const normalized = normalize_primary_currency(economy[key]);
    if (normalized !== null) {
      return { key, value: normalized };
    }
  }
  const synced = sync_primary_currency(economy);
  return { key: 'credits', value: synced };
}

function writeArenaCurrency(key, value) {
  const economy = ensure_economy();
  const normalized = normalize_primary_currency(value);
  const amount = normalized === null ? 0 : normalized;
  economy[key] = amount;
  sync_primary_currency(economy, amount);
}

function getArenaFee(currency = 0) {
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

function arenaStart(options = {}) {
  ensure_campaign();
  const arena = ensure_arena();
  if (arena.active) throw new Error('Arena bereits aktiv – beendet zuerst die laufende Serie.');
  const { key, value } = readArenaCurrency();
  const fee = getArenaFee(value);
  if (value < fee) throw new Error('Arena-Gebühr kann nicht bezahlt werden. Credits prüfen.');
  const players = gatherArenaPlayers();
  const tierRule = resolveArenaTier(players);
  const { players: sanitisedPlayers, audit } = applyArenaTierPolicy(players, tierRule);
  const parsedSize = Number.isFinite(options.teamSize) ? Math.floor(options.teamSize) : NaN;
  const teamSize =
    Number.isFinite(parsedSize) && parsedSize > 0
      ? Math.min(Math.max(parsedSize, 1), 6)
      : 1;
  const mode = typeof options.mode === 'string' ? options.mode.toLowerCase() : 'single';
  const scenario = nextArenaScenario();
  writeArenaCurrency(key, value - fee);
  const currentEpisode = state.campaign?.episode ?? null;
  const previousMode = typeof state.campaign?.mode === 'string' ? state.campaign.mode : null;
  arena.active = true;
  arena.wins_player = 0;
  arena.wins_opponent = 0;
  arena.tier = tierRule.tier;
  arena.proc_budget = tierRule.procBudget;
  arena.artifact_limit = tierRule.artifactLimit;
  arena.loadout_budget = tierRule.loadoutBudget;
  arena.audit = audit;
  arena.fee = fee;
  arena.scenario = scenario;
  arena.damage_dampener = true;
  arena.team_size = teamSize;
  arena.mode = mode;
  arena.previous_mode = previousMode;
  arena.policy_players = sanitisedPlayers;
  arena.started_episode = currentEpisode;
  state.campaign.mode = 'pvp';
  apply_arena_rules();
  ensure_runtime_flags().arena_active = true;
  state.location = 'ARENA';
  const pxLocked =
    arena.last_reward_episode !== null &&
    arena.last_reward_episode === currentEpisode;
  const pxNote = pxLocked ? 'Px-Bonus bereits vergeben' : 'Px-Bonus verfügbar';
  const baseMessage = `Arena initiiert · Tier ${tierRule.tier} · Gebühr ${fee} CU`;
  hud_toast(`${baseMessage} · ${pxNote}`, 'ARENA');
  if (audit.length) {
    hud_toast(`Arena-Loadout angepasst: ${audit.length} Eingriffe.`, 'ARENA');
  }
  return `${baseMessage} · ${scenario.description} · ${pxNote}`;
}

function arenaScore() {
  const arena = ensure_arena();
  const pxLocked =
    arena.last_reward_episode !== null &&
    arena.last_reward_episode === (state.campaign?.episode ?? null);
  const pxNote = pxLocked ? 'Px-Bonus bereits vergeben' : 'Px-Bonus offen';
  const scenario = arena.scenario?.description || 'n/a';
  return [
    `Arena-Score ${arena.wins_player}:${arena.wins_opponent}`,
    `Tier ${arena.tier}`,
    `Team ${arena.team_size}`,
    pxNote,
    `Szenario ${scenario}`,
  ].join(' · ');
}

function arenaRegisterResult(outcome) {
  const arena = ensure_arena();
  if (!arena.active) throw new Error('Arena ist nicht aktiv. Nutzt !arena start.');
  const normalized = (outcome || '').toString().toLowerCase();
  if (normalized === 'win' || normalized === 'victory') {
    arena.wins_player += 1;
  } else if (['loss', 'lose', 'defeat'].includes(normalized)) {
    arena.wins_opponent += 1;
  } else {
    throw new Error('Unbekanntes Arena-Ergebnis. Nutzt win oder loss.');
  }
  const status = `Arena-Serie ${arena.wins_player}:${arena.wins_opponent}`;
  let hint = '';
  if (arena.wins_player >= 2) {
    hint = 'Serie gewonnen – nutzt !arena exit für den Abschluss.';
  } else if (arena.wins_opponent >= 2) {
    hint = 'Serie verloren – ihr könnt die Arena mit !arena exit verlassen.';
  }
  const message = hint ? `${status} · ${hint}` : status;
  hud_toast(message, 'ARENA');
  return message;
}

function arenaExit() {
  const arena = ensure_arena();
  if (!arena.active) return 'Arena ist nicht aktiv.';
  const episode = state.campaign?.episode ?? null;
  let pxGranted = false;
  if (arena.wins_player >= 2 && arena.wins_player > arena.wins_opponent) {
    if (episode !== null && arena.last_reward_episode !== episode) {
      incrementParadoxon(1);
      arena.last_reward_episode = episode;
      pxGranted = true;
    }
  }
  const messageParts = [`Arena Ende · Score ${arena.wins_player}:${arena.wins_opponent}`];
  if (arena.wins_player < 2 || arena.wins_player <= arena.wins_opponent) {
    messageParts.push('Keine Px-Belohnung (Serie verloren)');
  } else if (pxGranted) {
    messageParts.push(`Px-Bonus +1 (Episode ${episode ?? 'n/a'})`);
  } else {
    messageParts.push('Px-Bonus bereits vergeben');
  }
  arena.active = false;
  arena.wins_player = 0;
  arena.wins_opponent = 0;
  arena.proc_budget = 0;
  arena.artifact_limit = 0;
  arena.loadout_budget = 0;
  arena.audit = [];
  arena.fee = 0;
  arena.scenario = null;
  arena.damage_dampener = false;
  arena.team_size = 1;
  arena.mode = 'single';
  arena.phase_strike_tax = 0;
  delete arena.policy_players;
  delete arena.started_episode;
  const restoreMode = arena.previous_mode;
  if (typeof restoreMode === 'string' && restoreMode.trim()) {
    state.campaign.mode = restoreMode;
  } else {
    delete state.campaign.mode;
    ensure_campaign();
  }
  delete arena.previous_mode;
  ensure_runtime_flags().arena_active = false;
  apply_arena_rules();
  state.location = 'HQ';
  const message = messageParts.join(' · ');
  hud_toast(message, 'ARENA');
  return message;
}

function parseArenaStartArgs(tokens) {
  let teamSize;
  let mode;
  for (let i = 0; i < tokens.length; i += 1) {
    const token = tokens[i];
    if (token === 'team' && Number.isFinite(Number(tokens[i + 1]))) {
      teamSize = parseInt(tokens[i + 1], 10);
      i += 1;
      continue;
    }
    if (token === 'mode' && typeof tokens[i + 1] === 'string') {
      mode = tokens[i + 1];
      i += 1;
    }
  }
  return { teamSize, mode };
}

function handleArenaCommand(cmd) {
  const tokens = cmd.split(/\s+/).map((t) => t.trim()).filter(Boolean);
  const sub = tokens[1] || 'status';
  if (sub === 'start') {
    const options = parseArenaStartArgs(tokens.slice(2));
    return arenaStart(options);
  }
  if (sub === 'score' || sub === 'status') {
    return arenaScore();
  }
  if (sub === 'exit' || sub === 'leave') {
    return arenaExit();
  }
  if (sub === 'result' && tokens[2]) {
    return arenaRegisterResult(tokens[2]);
  }
  if (sub === 'win') {
    return arenaRegisterResult('win');
  }
  if (sub === 'loss' || sub === 'lose') {
    return arenaRegisterResult('loss');
  }
  const help = [
    '!arena start [team <n>] [mode <name>]',
    '!arena result win|loss',
    '!arena score',
    '!arena exit',
  ].join(' · ');
  return `Arena-Befehle: ${help}`;
}
```

Die Runtime belastet die Credits sofort mit der Gebühr, setzt `arena.previous_mode`
für die Rückkehr ins Ursprungs-Gameplay und pflegt `arena.policy_players` als
Audit-Snapshot der bereinigten Loadouts. QA erwartet identische HUD-Toasts
(`ARENA`-Tag) und Px-Bonus-Regeln wie im Toolkit.
`ensure_runtime_flags()` synchronisiert parallel `flags.runtime.arena_active` für
Toolkit-Prüfpfade.

`arenaResume()` reaktiviert eine laufende Serie nach einem HQ-Load, sofern die
Runtime einen `arena.resume_token` (Tier, Teamgröße, Modus, Szenario, Audit,
`previous_mode`) hinterlegt hat; die Gebühr bleibt verbucht, der HUD-Toast
meldet „Arena Resume · Tier …“.


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
// `deepSave()` wird nach jeder Phase aufgerufen – so bleibt der Spielstand
// selbst bei Abstürzen aktuell.
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
