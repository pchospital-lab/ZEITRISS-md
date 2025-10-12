const fs = require('fs');
const path = require('path');
const { version: ZR_VERSION = '4.2.2' } = require('./package.json');

const RANK_ORDER = ['Recruit', 'Operator I', 'Operator II', 'Lead', 'Specialist', 'Chief'];
const COMPLIANCE_NOTICE = 'Compliance-Hinweis: ZEITRISS ist ein Science-Fiction-Rollenspiel. Alle Ereignisse sind fiktiv.';

const CHRONO_CATEGORY_LIMITS = {
  'Temporal Ships': 1,
  'Never-Was Gadgets': 3,
  'Era-Skins': 4
};

const OFFLINE_HELP_TOAST = 'Kodex-Uplink getrennt – Mission läuft weiter mit HUD-Lokaldaten.';
const OFFLINE_HELP_GUIDE = [
  'Kodex Offline-FAQ (ITI↔Kodex-Uplink im Einsatz gekappt):',
  '- Terminal oder Hardline suchen, Relay koppeln, Jammer-Override prüfen – Kodex bleibt bis dahin stumm.',
  '- Mission normal fortsetzen: HUD liefert lokale Logs, neue Saves gibt es weiterhin erst zurück im HQ.',
  '- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ markieren und Bestätigung abwarten.'
];
const OFFLINE_HELP_MIN_INTERVAL_MS = 60 * 1000;
const MARKET_LOG_LIMIT = 24;
const OFFLINE_LOG_LIMIT = 12;
const FR_INTERVENTION_LOG_LIMIT = 16;
const PSI_LOG_LIMIT = 16;
const ALIAS_TRACE_LIMIT = 24;
const SQUAD_RADIO_LOG_LIMIT = 24;

const CHRONO_CATALOG = [
  { id: 'ship_chronoglider_mk2', name: 'Chronoglider MK II', category: 'Temporal Ships', price: 5000, minRank: 'Lead', minResearch: 2 },
  { id: 'ship_aurora_skiff', name: 'Aurora-Skiff „Helio“', category: 'Temporal Ships', price: 5400, minRank: 'Specialist', minResearch: 3 },
  { id: 'ship_timesloop_schooner', name: 'Timesloop-Schooner', category: 'Temporal Ships', price: 5200, minRank: 'Lead', minResearch: 3 },
  { id: 'gadget_quantum_flashbang', name: 'Quantum-Flashbang', category: 'Never-Was Gadgets', price: 500, minRank: 'Operator II', minResearch: 1 },
  { id: 'gadget_nullgrav_tether', name: 'Null-Grav-Tether', category: 'Never-Was Gadgets', price: 450, minRank: 'Operator I', minResearch: 1 },
  { id: 'gadget_phase_jump_capsule', name: 'Phase-Jump-Kapsel', category: 'Never-Was Gadgets', price: 750, minRank: 'Lead', minResearch: 2 },
  { id: 'gadget_echo_distortion_field', name: 'Echo-Distortion-Field', category: 'Never-Was Gadgets', price: 900, minRank: 'Specialist', minResearch: 3 },
  { id: 'skin_aeon_nomad', name: 'Era-Skin: Æon-Nomadenmantel', category: 'Era-Skins', price: 200, minRank: 'Recruit', minResearch: 0 },
  { id: 'skin_krakatoa_1883', name: 'Era-Skin: Krakatoa 1883 Survivor', category: 'Era-Skins', price: 200, minRank: 'Operator I', minResearch: 0 },
  { id: 'skin_neon_cathedral', name: 'Era-Skin: Neon-Cathedral Glimmer', category: 'Era-Skins', price: 220, minRank: 'Lead', minResearch: 1 },
  { id: 'skin_sable_parallax', name: 'Era-Skin: Sable-Parallax Cloak', category: 'Era-Skins', price: 240, minRank: 'Specialist', minResearch: 2 }
];

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

const RUNTIME_TMP_DIR = path.join(__dirname, '.runtime-cache');
const SUSPEND_DIR = path.join(RUNTIME_TMP_DIR, 'suspend');
const SUSPEND_VERSION = 1;
const SUSPEND_TTL_MS = 24 * 60 * 60 * 1000;

let hudSequence = 0;

function pickString(...candidates){
  for (const candidate of candidates){
    if (typeof candidate !== 'string') continue;
    const trimmed = candidate.trim();
    if (trimmed){
      return trimmed;
    }
  }
  return '';
}

function pickNumber(...candidates){
  for (const candidate of candidates){
    const value = asNumber(candidate);
    if (value !== null){
      return value;
    }
  }
  return null;
}

function isoTimestamp(value){
  if (value instanceof Date && !Number.isNaN(value.getTime())){
    return value.toISOString();
  }
  if (typeof value === 'string'){
    const trimmed = value.trim();
    if (trimmed){
      const parsed = new Date(trimmed);
      if (!Number.isNaN(parsed.getTime())){
        return parsed.toISOString();
      }
    }
  }
  return null;
}

function normalize_market_entry(entry, fallbackTimestamp){
  if (!entry || typeof entry !== 'object') return null;
  const timestamp = isoTimestamp(entry.timestamp) || fallbackTimestamp || new Date().toISOString();
  const item = pickString(entry.item, entry.name, entry.label) || 'Unbekannter Artikel';
  const cost = pickNumber(entry.cost_cu, entry.cost, entry.price, entry.amount, entry.value, entry.cu, entry.credits);
  const quantity = pickNumber(entry.quantity, entry.qty, entry.count);
  const pxDelta = pickNumber(entry.px_delta, entry.delta_px, entry.pxDelta, entry.px);
  const pxClause = pickString(entry.px_clause, entry.pxClause, entry.px_note, entry.pxNote);
  const source = pickString(entry.source, entry.location, entry.channel);
  const note = pickString(entry.note, entry.details, entry.comment);
  const normalized = {
    timestamp,
    item,
    cost_cu: cost !== null ? Math.max(0, Math.round(cost)) : 0
  };
  if (source){
    normalized.source = source;
  }
  if (quantity !== null && quantity > 0){
    normalized.quantity = Math.max(1, Math.floor(quantity));
  }
  if (pxDelta !== null){
    const rounded = Number.isInteger(pxDelta) ? pxDelta : Math.round(pxDelta * 100) / 100;
    normalized.px_delta = rounded;
    if (!pxClause && rounded !== 0){
      const sign = rounded > 0 ? '+' : '';
      normalized.px_clause = `Px ${sign}${rounded}`;
    }
  }
  if (pxClause){
    normalized.px_clause = pxClause;
  }
  if (note){
    normalized.note = note;
  }
  const id = pickString(entry.id, entry.entry_id);
  if (id){
    normalized.id = id;
  }
  return normalized;
}

function sanitize_market_entries(entries, fallbackTimestamp){
  if (!Array.isArray(entries)) return [];
  const timestamp = fallbackTimestamp || new Date().toISOString();
  const sanitized = [];
  entries.forEach((entry) => {
    const normalized = normalize_market_entry(entry, timestamp);
    if (normalized){
      sanitized.push(normalized);
    }
  });
  if (sanitized.length > MARKET_LOG_LIMIT){
    return sanitized.slice(sanitized.length - MARKET_LOG_LIMIT);
  }
  return sanitized;
}

function normalize_offline_entry(entry, fallbackTimestamp){
  if (!entry || typeof entry !== 'object') return null;
  const timestamp = isoTimestamp(entry.timestamp) || fallbackTimestamp || new Date().toISOString();
  const reason = pickString(entry.reason, entry.cause, entry.trigger) || 'fallback';
  const status = pickString(entry.status, entry.state) || 'offline';
  const device = pickString(entry.device, entry.channel, entry.link);
  let jammed = null;
  if (typeof entry.jammed === 'boolean'){
    jammed = entry.jammed;
  } else if (typeof entry.jammed === 'string'){
    const trimmed = entry.jammed.trim().toLowerCase();
    if (['true', '1', 'yes', 'aktiv'].includes(trimmed)){
      jammed = true;
    } else if (['false', '0', 'no', 'frei'].includes(trimmed)){
      jammed = false;
    }
  } else if (entry.jammed != null){
    jammed = !!entry.jammed;
  }
  const range = pickNumber(entry.range_m, entry.range, entry.distance);
  const relays = pickNumber(entry.relays, entry.relay_count, entry.relays_count);
  const note = pickString(entry.note, entry.details, entry.message, entry.info);
  const count = pickNumber(entry.count, entry.sequence, entry.counter, entry.total);
  const sceneIndex = pickNumber(entry.scene_index, entry.sceneIndex, entry.scene);
  const sceneTotal = pickNumber(entry.scene_total, entry.sceneTotal, entry.totalScenes);
  const episode = pickNumber(entry.episode, entry.ep);
  const mission = pickNumber(entry.mission, entry.ms);
  const location = pickString(entry.location, entry.loc);
  const phase = pickString(entry.phase);
  const gmStyle = pickString(entry.gm_style, entry.gmStyle);
  const normalized = {
    timestamp,
    reason,
    status
  };
  if (device){
    normalized.device = device;
  }
  if (jammed !== null){
    normalized.jammed = !!jammed;
  }
  if (Number.isFinite(range) && range >= 0){
    normalized.range_m = Math.max(0, Math.round(range));
  }
  if (Number.isFinite(relays) && relays >= 0){
    normalized.relays = Math.max(0, Math.floor(relays));
  }
  if (note){
    normalized.note = note;
  }
  if (Number.isFinite(count) && count > 0){
    normalized.count = Math.max(1, Math.floor(count));
  }
  if (Number.isFinite(sceneIndex) && sceneIndex >= 0){
    normalized.scene_index = Math.max(0, Math.floor(sceneIndex));
  }
  if (Number.isFinite(sceneTotal) && sceneTotal > 0){
    normalized.scene_total = Math.max(1, Math.floor(sceneTotal));
  }
  if (Number.isFinite(episode) && episode >= 0){
    normalized.episode = Math.max(0, Math.floor(episode));
  }
  if (Number.isFinite(mission) && mission >= 0){
    normalized.mission = Math.max(0, Math.floor(mission));
  }
  if (location){
    normalized.location = location;
  }
  if (phase){
    normalized.phase = phase;
  }
  if (gmStyle){
    normalized.gm_style = gmStyle;
  }
  return normalized;
}

function sanitize_offline_entries(entries, fallbackTimestamp){
  if (!Array.isArray(entries)) return [];
  const timestamp = fallbackTimestamp || new Date().toISOString();
  const sanitized = [];
  entries.forEach((entry) => {
    const normalized = normalize_offline_entry(entry, timestamp);
    if (normalized){
      sanitized.push(normalized);
    }
  });
  if (sanitized.length > OFFLINE_LOG_LIMIT){
    return sanitized.slice(sanitized.length - OFFLINE_LOG_LIMIT);
  }
  return sanitized;
}

function normalize_intervention_entry(entry, fallbackTimestamp, options = {}){
  if (entry === undefined || entry === null) return null;
  const fillDefaults = options.fillDefaults !== false;
  let payload;
  if (typeof entry === 'string'){
    payload = { result: entry };
  } else if (typeof entry === 'object'){
    payload = { ...entry };
  } else {
    return null;
  }
  const timestamp = isoTimestamp(payload.timestamp) || fallbackTimestamp || new Date().toISOString();
  const result = pickString(payload.result, payload.status, payload.outcome, payload.message, payload.note);
  if (!result){
    return null;
  }
  let faction = pickString(payload.faction, payload.faction_id, payload.faction_name, payload.faction_tag, payload.name);
  if (!faction && fillDefaults && typeof state.campaign?.faction === 'string'){
    faction = state.campaign.faction;
  }
  let impact = pickString(payload.impact, payload.effect, payload.delta, payload.summary);
  const note = pickString(payload.note, payload.details, payload.comment, payload.description);
  let location = pickString(payload.location, payload.place);
  if (!location && fillDefaults && typeof state.location === 'string'){
    location = state.location;
  }
  let phase = pickString(payload.phase);
  if (!phase && fillDefaults && typeof state.phase === 'string'){
    phase = state.phase;
  }
  let gmStyle = pickString(payload.gm_style);
  if (!gmStyle && fillDefaults){
    gmStyle = ensure_ui().gm_style;
  }
  let mission = Number.isFinite(payload.mission) ? Math.max(0, Math.floor(payload.mission)) : null;
  if (mission === null && fillDefaults && Number.isFinite(state.campaign?.mission)){
    mission = Math.max(0, Math.floor(state.campaign.mission));
  }
  let episode = Number.isFinite(payload.episode) ? Math.max(0, Math.floor(payload.episode)) : null;
  if (episode === null && fillDefaults && Number.isFinite(state.campaign?.episode)){
    episode = Math.max(0, Math.floor(state.campaign.episode));
  }
  const sceneIndex = Number.isFinite(payload.scene_index)
    ? Math.max(0, Math.floor(payload.scene_index))
    : (fillDefaults && Number.isFinite(state.scene?.index))
    ? Math.max(0, Math.floor(state.scene.index))
    : null;
  const sceneTotal = Number.isFinite(payload.scene_total)
    ? Math.max(1, Math.floor(payload.scene_total))
    : (fillDefaults && Number.isFinite(state.scene?.total))
    ? Math.max(1, Math.floor(state.scene.total))
    : null;
  const observer = typeof payload.observer === 'boolean'
    ? payload.observer
    : (payload.is_observer === true || payload.observer === 'true');
  const escalated = typeof payload.escalated === 'boolean'
    ? payload.escalated
    : (payload.escalation === true || payload.escalated === 'true');
  const severity = pickString(payload.severity, payload.tier);
  const arc = pickString(payload.arc, payload.arc_id, payload.story_arc);
  const normalized = { timestamp, result: result.trim() };
  if (faction){
    normalized.faction = faction;
  }
  if (impact){
    normalized.impact = impact;
  }
  if (note){
    normalized.note = note;
  }
  if (location){
    normalized.location = location;
  }
  if (phase){
    normalized.phase = phase;
  }
  if (gmStyle){
    normalized.gm_style = gmStyle;
  }
  if (mission !== null){
    normalized.mission = mission;
  }
  if (episode !== null){
    normalized.episode = episode;
  }
  if (sceneIndex !== null){
    normalized.scene_index = sceneIndex;
  }
  if (sceneTotal !== null){
    normalized.scene_total = sceneTotal;
  }
  if (arc){
    normalized.arc = arc;
  }
  if (severity){
    normalized.severity = severity;
  }
  if (observer !== undefined){
    normalized.observer = !!observer;
  }
  if (escalated !== undefined){
    normalized.escalated = !!escalated;
  }
  return normalized;
}

function sanitize_intervention_entries(entries){
  if (!Array.isArray(entries)) return [];
  const fallback = new Date().toISOString();
  const sanitized = [];
  entries.forEach((entry) => {
    const normalized = normalize_intervention_entry(entry, fallback, { fillDefaults: false });
    if (normalized){
      sanitized.push(normalized);
    }
  });
  if (sanitized.length > FR_INTERVENTION_LOG_LIMIT){
    return sanitized.slice(sanitized.length - FR_INTERVENTION_LOG_LIMIT);
  }
  return sanitized;
}

function sanitize_psi_entries(entries){
  if (!Array.isArray(entries)) return [];
  const fallback = new Date().toISOString();
  const sanitized = [];
  entries.forEach((entry) => {
    if (!entry || typeof entry !== 'object') return;
    const ability = pickString(entry.ability, entry.power, entry.name) || 'phase_strike';
    const timestamp = isoTimestamp(entry.timestamp) || fallback;
    const baseCost = pickNumber(entry.base_cost, entry.base, entry.base_cost_sys, entry.baseCost);
    const tax = pickNumber(entry.tax, entry.tax_sys, entry.delta, entry.addition);
    const total = pickNumber(entry.total_cost, entry.total, entry.cost_total, entry.cost);
    const mode = pickString(entry.mode) || campaign_mode();
    const location = pickString(entry.location) || state.location || null;
    const arenaActive = entry.arena_active !== undefined ? !!entry.arena_active : !!state.arena?.active;
    const gmStyle = pickString(entry.gm_style, entry.gmStyle);
    const reason = pickString(entry.reason, entry.note);
    const record = {
      ability,
      timestamp,
      base_cost: Number.isFinite(baseCost) ? baseCost : 0,
      tax: Number.isFinite(tax) ? tax : 0,
      total_cost: Number.isFinite(total)
        ? total
        : ((Number.isFinite(baseCost) ? baseCost : 0) + (Number.isFinite(tax) ? tax : 0)),
      mode,
      arena_active: arenaActive
    };
    if (location){
      record.location = location;
    }
    if (gmStyle){
      record.gm_style = gmStyle;
    }
    if (reason){
      record.reason = reason;
    }
    sanitized.push(record);
  });
  if (sanitized.length > PSI_LOG_LIMIT){
    return sanitized.slice(sanitized.length - PSI_LOG_LIMIT);
  }
  return sanitized;
}

function normalize_alias_entry(entry, fallbackTimestamp){
  if (!entry || typeof entry !== 'object') return null;
  const timestamp = isoTimestamp(entry.timestamp) || fallbackTimestamp || new Date().toISOString();
  const persona = pickString(entry.persona, entry.identity, entry.agent, entry.profile);
  const cover = pickString(entry.cover, entry.alias, entry.mask, entry.role, entry.legend);
  const status = pickString(entry.status, entry.state, entry.result);
  const mission = pickString(entry.mission, entry.job, entry.op, entry.operation);
  const location = pickString(entry.location, entry.site, entry.zone);
  const note = pickString(entry.note, entry.notes, entry.detail, entry.details, entry.comment);
  const window = pickString(entry.window, entry.stage);
  const sceneIndex = pickNumber(entry.scene_index, entry.scene, entry.sceneIndex);
  const sceneTotal = pickNumber(entry.scene_total, entry.scenes, entry.sceneTotal);
  if (!persona && !cover && !note){
    return null;
  }
  const normalized = { timestamp };
  if (persona){
    normalized.persona = persona;
  }
  if (cover){
    normalized.cover = cover;
  }
  if (status){
    normalized.status = status;
  }
  if (mission){
    normalized.mission = mission;
  }
  if (location){
    normalized.location = location;
  }
  if (window){
    normalized.window = window;
  }
  if (note){
    normalized.note = note;
  }
  if (Number.isFinite(sceneIndex)){
    normalized.scene_index = Math.max(0, Math.floor(sceneIndex));
  }
  if (Number.isFinite(sceneTotal)){
    normalized.scene_total = Math.max(0, Math.floor(sceneTotal));
  }
  return normalized;
}

function sanitize_alias_entries(entries){
  if (!Array.isArray(entries)) return [];
  const fallback = new Date().toISOString();
  const sanitized = [];
  entries.forEach((entry) => {
    const normalized = normalize_alias_entry(entry, fallback);
    if (normalized){
      sanitized.push(normalized);
    }
  });
  if (sanitized.length > ALIAS_TRACE_LIMIT){
    return sanitized.slice(sanitized.length - ALIAS_TRACE_LIMIT);
  }
  return sanitized;
}

function normalize_radio_entry(entry, fallbackTimestamp){
  if (!entry || typeof entry !== 'object') return null;
  const timestamp = isoTimestamp(entry.timestamp) || fallbackTimestamp || new Date().toISOString();
  const message = pickString(entry.message, entry.text, entry.content, entry.call);
  if (!message){
    return null;
  }
  const speaker = pickString(entry.speaker, entry.from, entry.agent, entry.voice, entry.callsign);
  const channel = pickString(entry.channel, entry.band, entry.freq, entry.frequency);
  const status = pickString(entry.status, entry.state, entry.tag);
  const severity = pickString(entry.severity, entry.priority, entry.level);
  const note = pickString(entry.note, entry.notes, entry.detail, entry.details, entry.comment);
  const location = pickString(entry.location, entry.zone, entry.site);
  const sceneIndex = pickNumber(entry.scene_index, entry.scene, entry.sceneIndex);
  const normalized = { timestamp, message };
  if (speaker){
    normalized.speaker = speaker;
  }
  if (channel){
    normalized.channel = channel;
  }
  if (status){
    normalized.status = status;
  }
  if (severity){
    normalized.severity = severity;
  }
  if (note){
    normalized.note = note;
  }
  if (location){
    normalized.location = location;
  }
  if (Number.isFinite(sceneIndex)){
    normalized.scene_index = Math.max(0, Math.floor(sceneIndex));
  }
  return normalized;
}

function sanitize_radio_entries(entries){
  if (!Array.isArray(entries)) return [];
  const fallback = new Date().toISOString();
  const sanitized = [];
  entries.forEach((entry) => {
    const normalized = normalize_radio_entry(entry, fallback);
    if (normalized){
      sanitized.push(normalized);
    }
  });
  if (sanitized.length > SQUAD_RADIO_LOG_LIMIT){
    return sanitized.slice(sanitized.length - SQUAD_RADIO_LOG_LIMIT);
  }
  return sanitized;
}

const HQ_INTRO_LINES = [
  'HQ-Kurzintro – Nullzeit-Puffer flutet Euch zurück in Eure Körper.',
  'Sensorhallen öffnen sich, Soras Stimmennetz gleitet wie Regenlicht über die Decks.',
  'Commander Renier: „Briefingraum in drei Minuten. Rollen wählen, Fokus halten.“'
];

const state = {
  location: 'HQ',
  phase: 'core', // mission phase: core, transfer, rift
  campaign: {},
  character: {},
  team: { members: [] },
  party: { characters: [] },
  loadout: {},
  economy: {},
  logs: {},
  ui: { gm_style: 'verbose', intro_seen: false, suggest_mode: false },
  arc_dashboard: { offene_seeds: [], fraktionen: {}, fragen: [] },
  initiative: { order: [], active_id: null },
  hud: { timers: [] },
  exfil: null,
  fr_intervention: null,
  scene: { index: 0, foreshadows: 0, total: 12 },
  comms: { jammed: false, relays: 0, rangeMod: 1.0 },
  mission: { id: null, objective: null, clock: {}, timers: [] },
  flags: { runtime: {} },
  roll: { open: false },
  suspend_snapshot: null,
  arena: {
    active: false,
    wins_player: 0,
    wins_opponent: 0,
    last_reward_episode: null,
    tier: 1,
    proc_budget: 0,
    artifact_limit: 0,
    loadout_budget: 0,
    audit: [],
    fee: 0,
    scenario: null,
    damage_dampener: true,
    team_size: 1,
    mode: 'single',
    phase_strike_tax: 0
  }
};

function ensure_logs(){
  state.logs ||= {};
  if (!Array.isArray(state.logs.hud)){
    state.logs.hud = [];
  }
  if (!Array.isArray(state.logs.foreshadow)){
    state.logs.foreshadow = [];
  } else {
    const deduped = [];
    const byToken = new Map();
    for (const entry of state.logs.foreshadow){
      if (!entry || typeof entry !== 'object' || typeof entry.token !== 'string') continue;
      const rawToken = entry.token.trim();
      if (!rawToken) continue;
      const token = rawToken.toLowerCase();
      const tag = typeof entry.tag === 'string' && entry.tag.trim() ? entry.tag.trim() : 'Foreshadow';
      const message = typeof entry.message === 'string' ? entry.message.trim() : '';
      const sceneIndex = Number(entry.scene);
      const scene = Number.isFinite(sceneIndex) ? sceneIndex : null;
      const firstSeen = typeof entry.first_seen === 'string' ? entry.first_seen : null;
      const lastSeen = typeof entry.last_seen === 'string' ? entry.last_seen : null;
      if (byToken.has(token)){
        const existing = byToken.get(token);
        if (!existing.message && message){
          existing.message = message;
        }
        if (!existing.tag && tag){
          existing.tag = tag;
        }
        if (!Number.isFinite(existing.scene) && Number.isFinite(scene)){
          existing.scene = scene;
        }
        if (!existing.last_seen && lastSeen){
          existing.last_seen = lastSeen;
        }
        continue;
      }
      const record = {
        token,
        tag,
        message,
        scene,
        first_seen: firstSeen,
        last_seen: lastSeen || firstSeen
      };
      deduped.push(record);
      byToken.set(token, record);
    }
    state.logs.foreshadow = deduped;
  }
  if (!Array.isArray(state.logs.artifact_log)){
    state.logs.artifact_log = [];
  }
  if (!Array.isArray(state.logs.kodex)){
    state.logs.kodex = [];
  }
  if (!Array.isArray(state.logs.market)){
    state.logs.market = [];
  } else {
    state.logs.market = sanitize_market_entries(state.logs.market);
  }
  if (!Array.isArray(state.logs.offline)){
    state.logs.offline = [];
  } else {
    state.logs.offline = sanitize_offline_entries(state.logs.offline);
  }
  if (!Array.isArray(state.logs.fr_interventions)){
    state.logs.fr_interventions = [];
  } else {
    state.logs.fr_interventions = sanitize_intervention_entries(state.logs.fr_interventions);
  }
  if (!Array.isArray(state.logs.psi)){
    state.logs.psi = [];
  } else {
    state.logs.psi = sanitize_psi_entries(state.logs.psi);
  }
  if (!Array.isArray(state.logs.alias_trace)){
    state.logs.alias_trace = [];
  } else {
    state.logs.alias_trace = sanitize_alias_entries(state.logs.alias_trace);
  }
  if (!Array.isArray(state.logs.squad_radio)){
    state.logs.squad_radio = [];
  } else {
    state.logs.squad_radio = sanitize_radio_entries(state.logs.squad_radio);
  }
  if (!state.logs.flags || typeof state.logs.flags !== 'object'){
    state.logs.flags = {};
  }
  const flags = state.logs.flags;
  if (!flags.runtime_version){
    flags.runtime_version = ZR_VERSION;
  }
  if (typeof flags.compliance_shown_today !== 'boolean'){
    flags.compliance_shown_today = !!state.campaign?.compliance_shown_today;
  } else {
    flags.compliance_shown_today = !!flags.compliance_shown_today;
  }
  if (typeof flags.chronopolis_warn_seen !== 'boolean'){
    flags.chronopolis_warn_seen = false;
  } else {
    flags.chronopolis_warn_seen = !!flags.chronopolis_warn_seen;
  }
  if (typeof flags.offline_help_last !== 'string'){
    flags.offline_help_last = null;
  }
  if (!Number.isFinite(flags.offline_help_count)){
    flags.offline_help_count = 0;
  } else {
    flags.offline_help_count = Math.max(0, Math.floor(flags.offline_help_count));
  }
  if (state.campaign && typeof state.campaign === 'object' && typeof state.campaign.compliance_shown_today !== 'boolean'){
    state.campaign.compliance_shown_today = flags.compliance_shown_today;
  }
  return state.logs.hud;
}

function ensure_market_log(){
  ensure_logs();
  if (!Array.isArray(state.logs.market)){
    state.logs.market = [];
  }
  state.logs.market = sanitize_market_entries(state.logs.market);
  return state.logs.market;
}

function ensure_offline_log(){
  ensure_logs();
  if (!Array.isArray(state.logs.offline)){
    state.logs.offline = [];
  }
  state.logs.offline = sanitize_offline_entries(state.logs.offline);
  return state.logs.offline;
}

function ensure_intervention_log(){
  ensure_logs();
  if (!Array.isArray(state.logs.fr_interventions)){
    state.logs.fr_interventions = [];
  }
  state.logs.fr_interventions = sanitize_intervention_entries(state.logs.fr_interventions);
  return state.logs.fr_interventions;
}

function ensure_psi_log(){
  ensure_logs();
  if (!Array.isArray(state.logs.psi)){
    state.logs.psi = [];
  }
  state.logs.psi = sanitize_psi_entries(state.logs.psi);
  return state.logs.psi;
}

function ensure_alias_trace(){
  ensure_logs();
  if (!Array.isArray(state.logs.alias_trace)){
    state.logs.alias_trace = [];
  }
  state.logs.alias_trace = sanitize_alias_entries(state.logs.alias_trace);
  return state.logs.alias_trace;
}

function ensure_squad_radio_log(){
  ensure_logs();
  if (!Array.isArray(state.logs.squad_radio)){
    state.logs.squad_radio = [];
  }
  state.logs.squad_radio = sanitize_radio_entries(state.logs.squad_radio);
  return state.logs.squad_radio;
}

function log_market_purchase(item, cost, options = {}){
  const payload = {
    ...options,
    item,
    cost_cu: cost
  };
  if (options.timestamp){
    const iso = isoTimestamp(options.timestamp);
    if (iso){
      payload.timestamp = iso;
    }
  }
  const marketLog = ensure_market_log();
  const normalized = normalize_market_entry(payload, new Date().toISOString());
  if (!normalized){
    throw new Error('MarketLog: Ungültiger Eintrag.');
  }
  marketLog.push(normalized);
  if (marketLog.length > MARKET_LOG_LIMIT){
    marketLog.splice(0, marketLog.length - MARKET_LOG_LIMIT);
  }
  return normalized;
}

function log_phase_strike_event(ctx = state, details = {}){
  const psiLog = ensure_psi_log();
  const now = new Date().toISOString();
  const base = Number.isFinite(details.base) ? Number(details.base) : 0;
  const tax = Number.isFinite(details.tax) ? Number(details.tax) : 0;
  const total = Number.isFinite(details.total) ? Number(details.total) : base + tax;
  const mode = campaign_mode(ctx);
  const arenaActive = !!(ctx?.arena?.active);
  const entry = {
    ability: 'phase_strike',
    timestamp: now,
    base_cost: base,
    tax,
    total_cost: total,
    mode,
    arena_active: arenaActive
  };
  const location = typeof ctx?.location === 'string' && ctx.location.trim()
    ? ctx.location.trim()
    : (typeof state.location === 'string' && state.location.trim() ? state.location.trim() : null);
  if (location){
    entry.location = location;
  }
  const ui = ensure_ui();
  const gmStyle = typeof ui?.gm_style === 'string' ? ui.gm_style.trim() : '';
  if (gmStyle){
    entry.gm_style = gmStyle;
  }
  if (typeof details.reason === 'string' && details.reason.trim()){
    entry.reason = details.reason.trim();
  }
  psiLog.push(entry);
  if (psiLog.length > PSI_LOG_LIMIT){
    psiLog.splice(0, psiLog.length - PSI_LOG_LIMIT);
  }
  return entry;
}

function log_alias_event(details = {}){
  const trace = ensure_alias_trace();
  const fallback = new Date().toISOString();
  const payload = { ...details };
  if (!payload.timestamp){
    payload.timestamp = fallback;
  }
  const normalized = normalize_alias_entry(payload, fallback);
  if (!normalized){
    throw new Error('AliasTrace: Alias oder Persona fehlen.');
  }
  trace.push(normalized);
  if (trace.length > ALIAS_TRACE_LIMIT){
    trace.splice(0, trace.length - ALIAS_TRACE_LIMIT);
  }
  return normalized;
}

function log_squad_radio(details = {}){
  const radioLog = ensure_squad_radio_log();
  const fallback = new Date().toISOString();
  const payload = { ...details };
  if (!payload.timestamp){
    payload.timestamp = fallback;
  }
  const normalized = normalize_radio_entry(payload, fallback);
  if (!normalized){
    throw new Error('SquadRadio: Nachricht fehlt.');
  }
  radioLog.push(normalized);
  if (radioLog.length > SQUAD_RADIO_LOG_LIMIT){
    radioLog.splice(0, radioLog.length - SQUAD_RADIO_LOG_LIMIT);
  }
  return normalized;
}

function format_alias_trace_entry(entry){
  if (!entry) return '';
  const parts = [];
  let label = '';
  if (entry.persona && entry.cover){
    label = `${entry.persona} → ${entry.cover}`;
  } else if (entry.cover){
    label = entry.cover;
  } else if (entry.persona){
    label = entry.persona;
  }
  if (entry.status){
    label = label ? `${label} (${entry.status})` : entry.status;
  }
  if (label){
    parts.push(label);
  }
  const meta = [];
  if (Number.isFinite(entry.scene_index) && Number.isFinite(entry.scene_total)){
    meta.push(`Sz ${entry.scene_index}/${entry.scene_total}`);
  } else if (Number.isFinite(entry.scene_index)){
    meta.push(`Sz ${entry.scene_index}`);
  }
  if (entry.mission){
    meta.push(entry.mission);
  }
  if (entry.location){
    meta.push(entry.location);
  }
  if (entry.window){
    meta.push(entry.window);
  }
  if (meta.length){
    parts.push(meta.join(' · '));
  }
  if (entry.note){
    parts.push(entry.note);
  }
  return parts.length ? parts.join(' – ') : '';
}

function render_alias_trace_summary(limit = 4){
  const entries = ensure_alias_trace();
  if (!entries.length) return '';
  const recent = entries.slice(Math.max(0, entries.length - limit));
  const lines = [`Alias-Trace (${entries.length}×):`];
  recent.forEach((entry) => {
    const line = format_alias_trace_entry(entry);
    if (line){
      lines.push(`- ${line}`);
    }
  });
  return lines.join('\n');
}

function format_squad_radio_entry(entry){
  if (!entry) return '';
  const segments = [];
  const headerParts = [];
  if (entry.speaker){
    headerParts.push(entry.speaker);
  }
  if (entry.channel){
    headerParts.push(`#${entry.channel}`);
  }
  if (entry.status){
    headerParts.push(entry.status);
  }
  if (entry.severity){
    headerParts.push(entry.severity);
  }
  if (headerParts.length){
    segments.push(headerParts.join(' · '));
  }
  if (entry.message){
    segments.push(entry.message);
  }
  const meta = [];
  if (Number.isFinite(entry.scene_index)){
    meta.push(`Sz ${entry.scene_index}`);
  }
  if (entry.location){
    meta.push(entry.location);
  }
  if (entry.note){
    meta.push(entry.note);
  }
  if (meta.length){
    segments.push(meta.join(' · '));
  }
  return segments.length ? segments.join(' – ') : '';
}

function render_squad_radio_summary(limit = 5){
  const entries = ensure_squad_radio_log();
  if (!entries.length) return '';
  const recent = entries.slice(Math.max(0, entries.length - limit));
  const lines = [`Squad-Radio (${entries.length}×):`];
  recent.forEach((entry) => {
    const line = format_squad_radio_entry(entry);
    if (line){
      lines.push(`- ${line}`);
    }
  });
  return lines.join('\n');
}

function strip_quotes(value){
  if (typeof value !== 'string') return value;
  const trimmed = value.trim();
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || (trimmed.startsWith("'") && trimmed.endsWith("'"))){
    return trimmed.slice(1, -1).trim();
  }
  return trimmed;
}

function split_pipe_segments(text){
  if (typeof text !== 'string') return [];
  return text.split('|').map(segment => strip_quotes(segment));
}

function parse_alias_payload(text){
  const segments = split_pipe_segments(text);
  const payload = {};
  let index = 0;
  segments.forEach((segment) => {
    if (!segment) return;
    const eq = segment.indexOf('=');
    if (eq > -1){
      const key = segment.slice(0, eq).trim().toLowerCase();
      const value = segment.slice(eq + 1).trim();
      switch (key){
        case 'persona':
        case 'identity':
        case 'agent':
        case 'profile':
          payload.persona = value;
          break;
        case 'alias':
        case 'cover':
        case 'legend':
        case 'role':
          payload.cover = value;
          break;
        case 'status':
        case 'state':
        case 'result':
          payload.status = value;
          break;
        case 'mission':
        case 'op':
        case 'job':
        case 'operation':
          payload.mission = value;
          break;
        case 'note':
        case 'details':
        case 'comment':
          payload.note = value;
          break;
        case 'location':
        case 'site':
        case 'zone':
          payload.location = value;
          break;
        case 'scene':
        case 'scene_index':
          payload.scene_index = Number.parseInt(value, 10);
          break;
        case 'scene_total':
        case 'scenes':
          payload.scene_total = Number.parseInt(value, 10);
          break;
        case 'window':
        case 'phase':
          payload.window = value;
          break;
        default:
          break;
      }
      return;
    }
    switch (index){
      case 0:
        if (!payload.persona){
          payload.persona = segment;
        }
        break;
      case 1:
        if (!payload.cover){
          payload.cover = segment;
        }
        break;
      case 2:
        if (!payload.status){
          payload.status = segment;
        }
        break;
      default:
        payload.note = payload.note ? `${payload.note}; ${segment}` : segment;
        break;
    }
    index += 1;
  });
  return payload;
}

function parse_radio_payload(text){
  const segments = split_pipe_segments(text);
  const payload = {};
  let index = 0;
  segments.forEach((segment) => {
    if (!segment) return;
    const eq = segment.indexOf('=');
    if (eq > -1){
      const key = segment.slice(0, eq).trim().toLowerCase();
      const value = segment.slice(eq + 1).trim();
      switch (key){
        case 'speaker':
        case 'from':
        case 'agent':
        case 'voice':
          payload.speaker = value;
          break;
        case 'channel':
        case 'band':
        case 'freq':
        case 'frequency':
          payload.channel = value;
          break;
        case 'message':
        case 'text':
        case 'content':
          payload.message = value;
          break;
        case 'status':
        case 'state':
        case 'tag':
          payload.status = value;
          break;
        case 'severity':
        case 'priority':
        case 'level':
          payload.severity = value;
          break;
        case 'note':
        case 'comment':
        case 'details':
          payload.note = value;
          break;
        case 'location':
        case 'zone':
        case 'site':
          payload.location = value;
          break;
        case 'scene':
        case 'scene_index':
          payload.scene_index = Number.parseInt(value, 10);
          break;
        default:
          break;
      }
      return;
    }
    switch (index){
      case 0:
        if (!payload.speaker){
          payload.speaker = segment;
        }
        break;
      case 1:
        if (!payload.channel){
          payload.channel = segment;
        }
        break;
      case 2:
        if (!payload.message){
          payload.message = segment;
        }
        break;
      case 3:
        if (!payload.status){
          payload.status = segment;
        }
        break;
      default:
        payload.note = payload.note ? `${payload.note}; ${segment}` : segment;
        break;
    }
    index += 1;
  });
  return payload;
}

function handleAliasCommand(raw){
  const cmd = raw.trim();
  if (cmd === '!alias' || cmd === '!alias status'){
    const summary = render_alias_trace_summary();
    return summary || 'Alias-Trace leer.';
  }
  if (cmd === '!alias clear'){
    const trace = ensure_alias_trace();
    trace.length = 0;
    return 'Alias-Trace geleert.';
  }
  if (cmd === '!alias help'){
    return 'Alias-Trace: `!alias log Persona|Cover|Status|Notiz` oder Felder via `key=value` setzen. `!alias status` zeigt die Übersicht.';
  }
  const m = cmd.match(/^!alias\s+log\s+(.+)/);
  if (m){
    try {
      const entry = log_alias_event(parse_alias_payload(m[1]));
      const line = format_alias_trace_entry(entry) || 'Alias-Eintrag gespeichert.';
      return `Alias-Trace aktualisiert (${ensure_alias_trace().length}×): ${line}`;
    } catch (err){
      return err.message;
    }
  }
  return 'Alias-Befehl unbekannt. Nutzt `!alias help`.';
}

function handleRadioCommand(raw){
  const cmd = raw.trim();
  if (cmd === '!radio' || cmd === '!radio status'){
    const summary = render_squad_radio_summary();
    return summary || 'Squad-Radio-Log leer.';
  }
  if (cmd === '!radio clear'){
    const log = ensure_squad_radio_log();
    log.length = 0;
    return 'Squad-Radio-Log geleert.';
  }
  if (cmd === '!radio help'){
    return 'Squad-Radio: `!radio log Sprecher|Channel|Meldung|Status` oder Felder via `key=value`. `!radio status` zeigt die letzten Einträge.';
  }
  const m = cmd.match(/^!radio\s+log\s+(.+)/);
  if (m){
    try {
      const entry = log_squad_radio(parse_radio_payload(m[1]));
      const line = format_squad_radio_entry(entry) || 'Funk-Log gespeichert.';
      return `Squad-Radio aktualisiert (${ensure_squad_radio_log().length}×): ${line}`;
    } catch (err){
      return err.message;
    }
  }
  return 'Radio-Befehl unbekannt. Nutzt `!radio help`.';
}

function foreshadow_entries(){
  return Array.isArray(state.logs?.foreshadow) ? state.logs.foreshadow : [];
}

function foreshadow_count(){
  return foreshadow_entries().length;
}

function foreshadow_requirement(ctx = state){
  const campaign = ctx?.campaign || {};
  const rawType = typeof campaign.type === 'string' ? campaign.type.trim().toLowerCase() : '';
  const phase = typeof ctx?.phase === 'string' ? ctx.phase.trim().toLowerCase() : '';
  if (rawType === 'rift' || (!rawType && phase === 'rift')){
    return 2;
  }
  if (rawType === 'core' || rawType === 'preserve' || rawType === 'story' || (!rawType && phase === 'core')){
    if (campaign.boss_allowed === false) return 0;
    return 4;
  }
  return 0;
}

function foreshadow_status(ctx = state){
  const count = foreshadow_count();
  const required = foreshadow_requirement(ctx);
  return required > 0 ? `Foreshadow ${count}/${required}` : `Foreshadow ${count}`;
}

function sync_foreshadow_progress(){
  state.scene ||= { index: 0, foreshadows: 0, total: 12 };
  state.scene.foreshadows = foreshadow_count();
  return state.scene.foreshadows;
}

function register_foreshadow(token, details = {}){
  ensure_logs();
  const entries = foreshadow_entries();
  const normalized = typeof token === 'string' ? token.trim().toLowerCase() : '';
  if (!normalized) return null;
  const now = new Date().toISOString();
  let entry = entries.find(item => item.token === normalized);
  const message = typeof details.message === 'string' ? details.message.trim() : '';
  const tag = typeof details.tag === 'string' && details.tag.trim() ? details.tag.trim() : 'Foreshadow';
  const sceneIndex = Number.isFinite(details.scene)
    ? Number(details.scene)
    : Number.isFinite(state.scene?.index)
    ? state.scene.index
    : null;
  if (!entry){
    entry = {
      token: normalized,
      tag,
      message,
      scene: sceneIndex,
      first_seen: now,
      last_seen: now
    };
    entries.push(entry);
  } else {
    entry.last_seen = now;
    if (message && !entry.message){
      entry.message = message;
    }
    if (tag && entry.tag !== tag){
      entry.tag = tag;
    }
    if (Number.isFinite(sceneIndex) && !Number.isFinite(entry.scene)){
      entry.scene = sceneIndex;
    }
  }
  sync_foreshadow_progress();
  return entry;
}

function ensure_ui(){
  if (!state.ui || typeof state.ui !== 'object'){
    state.ui = { gm_style: 'verbose', intro_seen: false, suggest_mode: false };
  }
  if (typeof state.ui.gm_style !== 'string'){
    state.ui.gm_style = 'verbose';
  }
  state.ui.intro_seen = !!state.ui.intro_seen;
  if (typeof state.ui.suggest_mode !== 'boolean'){
    state.ui.suggest_mode = false;
  }
  return state.ui;
}

function ensure_economy(){
  if (!state.economy || typeof state.economy !== 'object'){
    state.economy = {};
  }
  const economy = state.economy;
  economy.cu = Number.isFinite(economy.cu) ? Math.round(economy.cu) : 0;
  ensure_wallets();
  return economy;
}

function normalize_wallet_id(raw){
  if (typeof raw !== 'string') return null;
  const trimmed = raw.trim();
  return trimmed || null;
}

function normalize_wallet_record(entry){
  if (entry === null || entry === undefined) return null;
  if (typeof entry === 'number'){
    const balance = Math.max(0, Math.round(entry));
    return { balance, name: null };
  }
  if (typeof entry !== 'object' || Array.isArray(entry)){
    return null;
  }
  const amount = asNumber(entry.balance ?? entry.amount ?? entry.cu ?? entry.value ?? entry.delta);
  if (amount === null){
    return null;
  }
  const balance = Math.max(0, Math.round(amount));
  const name = typeof entry.name === 'string' && entry.name.trim() ? entry.name.trim() : null;
  return { balance, name };
}

function ensure_wallets(){
  const economy = state.economy || (state.economy = {});
  const wallets = economy.wallets;
  const normalized = {};
  if (wallets && typeof wallets === 'object' && !Array.isArray(wallets)){
    for (const [key, value] of Object.entries(wallets)){
      const id = normalize_wallet_id(key);
      if (!id) continue;
      const record = normalize_wallet_record(value);
      if (!record) continue;
      normalized[id] = {
        balance: record.balance,
        name: record.name
      };
    }
  }
  economy.wallets = normalized;
  return normalized;
}

function wallet_lookup(){
  ensure_wallets();
  const economy = state.economy;
  return economy.wallets;
}

function get_wallet_record(id, label){
  if (!id) return null;
  const wallets = wallet_lookup();
  let record = wallets[id];
  if (!record){
    record = { balance: 0, name: label || null };
    wallets[id] = record;
  } else if (!record.name && label){
    record.name = label;
  }
  return record;
}

function ensure_character(){
  state.character ||= {};
  if (state.character.self_reflection === undefined){
    state.character.self_reflection = true;
  }
  if (!state.character.rank){
    state.character.rank = 'Recruit';
  }
  if (!state.character.cooldowns || typeof state.character.cooldowns !== 'object'){
    state.character.cooldowns = {};
  }
  return state.character;
}

function ensure_team(){
  state.team ||= {};
  const team = state.team;
  team.stress = Number.isFinite(team.stress) ? team.stress : 0;
  team.psi_heat = Number.isFinite(team.psi_heat) ? team.psi_heat : 0;
  if (typeof team.status !== 'string'){ team.status = 'ready'; }
  if (!team.cooldowns || typeof team.cooldowns !== 'object'){ team.cooldowns = {}; }
  if (!Array.isArray(team.members)){
    team.members = [];
  }
  return team;
}

function ensure_party(){
  state.party ||= {};
  const party = state.party;
  if (!Array.isArray(party.characters)){
    party.characters = [];
  } else {
    party.characters = party.characters.filter(entry => entry && typeof entry === 'object');
  }
  return party;
}

function ensure_arc_dashboard(){
  state.arc_dashboard ||= {};
  const dash = state.arc_dashboard;
  if (!Array.isArray(dash.offene_seeds)){
    dash.offene_seeds = [];
  } else {
    dash.offene_seeds = dash.offene_seeds
      .filter(entry => entry && typeof entry === 'object')
      .map(entry => clone_plain_object(entry));
  }
  if (!dash.fraktionen || typeof dash.fraktionen !== 'object' || Array.isArray(dash.fraktionen)){
    dash.fraktionen = {};
  } else {
    const normalized = {};
    for (const [key, value] of Object.entries(dash.fraktionen)){
      const record = value && typeof value === 'object' ? clone_plain_object(value) : {};
      if (Array.isArray(record.interventions)){
        record.interventions = sanitize_intervention_entries(record.interventions).map(entry => ({ ...entry }));
      } else {
        record.interventions = [];
      }
      if (record.last_intervention){
        const last = normalize_intervention_entry(record.last_intervention, record.last_intervention?.timestamp, { fillDefaults: false });
        record.last_intervention = last || null;
      } else {
        record.last_intervention = null;
      }
      normalized[key] = record;
    }
    dash.fraktionen = normalized;
  }
  if (!Array.isArray(dash.fragen)){
    dash.fragen = [];
  } else {
    dash.fragen = dash.fragen.map(entry => (
      entry && typeof entry === 'object'
        ? clone_plain_object(entry)
        : entry
    ));
  }
  return dash;
}

function update_arc_dashboard_intervention(entry){
  const dash = ensure_arc_dashboard();
  dash.fraktionen ||= {};
  const factionKey = typeof entry.faction === 'string' && entry.faction.trim()
    ? entry.faction.trim()
    : 'unbekannt';
  const mapKey = factionKey.toLowerCase();
  const record = dash.fraktionen[mapKey] && typeof dash.fraktionen[mapKey] === 'object'
    ? dash.fraktionen[mapKey]
    : {};
  if (!record.id){
    record.id = mapKey;
  }
  if (factionKey && !record.name){
    record.name = factionKey;
  }
  const history = Array.isArray(record.interventions) ? record.interventions.slice() : [];
  const snapshot = { timestamp: entry.timestamp, result: entry.result };
  if (entry.impact){
    snapshot.impact = entry.impact;
  }
  if (entry.note){
    snapshot.note = entry.note;
  }
  if (entry.phase){
    snapshot.phase = entry.phase;
  }
  if (entry.location){
    snapshot.location = entry.location;
  }
  if (Number.isFinite(entry.scene_index)){
    snapshot.scene_index = entry.scene_index;
  }
  if (Number.isFinite(entry.scene_total)){
    snapshot.scene_total = entry.scene_total;
  }
  if (Number.isFinite(entry.mission)){
    snapshot.mission = entry.mission;
  }
  if (Number.isFinite(entry.episode)){
    snapshot.episode = entry.episode;
  }
  if (entry.arc){
    snapshot.arc = entry.arc;
  }
  if (entry.severity){
    snapshot.severity = entry.severity;
  }
  if (entry.observer !== undefined){
    snapshot.observer = !!entry.observer;
  }
  if (entry.escalated !== undefined){
    snapshot.escalated = !!entry.escalated;
  }
  history.push(snapshot);
  if (history.length > 6){
    history.splice(0, history.length - 6);
  }
  record.interventions = history;
  record.last_intervention = snapshot;
  record.last_result = entry.result;
  record.last_updated = entry.timestamp;
  dash.fraktionen[mapKey] = record;
  return record;
}

function ensure_initiative(){
  if (!state.initiative || typeof state.initiative !== 'object'){
    state.initiative = {};
  }
  const initiative = state.initiative;
  if (!Array.isArray(initiative.order)){
    initiative.order = [];
  } else {
    initiative.order = initiative.order
      .filter(entry => entry !== undefined && entry !== null)
      .map(entry => (typeof entry === 'object' ? clone_plain_object(entry) : entry));
  }
  if (typeof initiative.active_id === 'string'){
    const trimmed = initiative.active_id.trim();
    initiative.active_id = trimmed.length ? trimmed : null;
  } else {
    initiative.active_id = null;
  }
  return initiative;
}

function normalize_hud_timer(entry){
  if (entry === undefined || entry === null) return null;
  if (typeof entry === 'string'){
    const label = entry.trim();
    return label ? { label } : null;
  }
  if (typeof entry !== 'object') return null;
  const normalized = clone_plain_object(entry);
  if (typeof normalized.id === 'string'){
    const trimmed = normalized.id.trim();
    normalized.id = trimmed.length ? trimmed : undefined;
  }
  if (typeof normalized.label === 'string'){
    const trimmed = normalized.label.trim();
    normalized.label = trimmed.length ? trimmed : undefined;
  }
  if (typeof normalized.tag === 'string'){
    const trimmed = normalized.tag.trim();
    normalized.tag = trimmed.length ? trimmed : undefined;
  }
  if (!Number.isFinite(normalized.remaining)) delete normalized.remaining;
  if (!Number.isFinite(normalized.total)) delete normalized.total;
  if (normalized.paused !== true) delete normalized.paused;
  if (normalized.critical !== true) delete normalized.critical;
  if (typeof normalized.style === 'string'){
    const trimmed = normalized.style.trim();
    normalized.style = trimmed.length ? trimmed : undefined;
  }
  if (typeof normalized.notes === 'string'){
    const trimmed = normalized.notes.trim();
    normalized.notes = trimmed.length ? trimmed : undefined;
  }
  Object.keys(normalized).forEach(key => {
    if (normalized[key] === undefined) delete normalized[key];
  });
  return Object.keys(normalized).length ? normalized : {};
}

function ensure_hud_state(){
  if (!state.hud || typeof state.hud !== 'object'){
    state.hud = {};
  }
  const hud = state.hud;
  if (!Array.isArray(hud.timers)){
    hud.timers = [];
  } else {
    hud.timers = hud.timers
      .map(normalize_hud_timer)
      .filter(entry => entry !== null);
  }
  return hud;
}

function ensure_mission(){
  state.mission ||= {};
  const mission = state.mission;
  if (typeof mission.id !== 'string'){ mission.id = mission.id ?? null; }
  if (typeof mission.objective !== 'string'){ mission.objective = mission.objective ?? null; }
  if (!mission.clock || typeof mission.clock !== 'object'){ mission.clock = {}; }
  if (!Array.isArray(mission.timers)){ mission.timers = []; }
  return mission;
}

function ensure_runtime_flags(){
  state.flags ||= {};
  if (!state.flags.runtime || typeof state.flags.runtime !== 'object'){ state.flags.runtime = {}; }
  const runtimeFlags = state.flags.runtime;
  if (typeof runtimeFlags.skip_entry_choice !== 'boolean'){
    runtimeFlags.skip_entry_choice = false;
  } else {
    runtimeFlags.skip_entry_choice = !!runtimeFlags.skip_entry_choice;
  }
  return runtimeFlags;
}

function ensure_cooldowns(){
  const character = ensure_character();
  return character.cooldowns;
}

function set_cooldown(name, rounds){
  const pool = ensure_cooldowns();
  if (!Number.isFinite(rounds) || rounds <= 0){
    delete pool[name];
    return 0;
  }
  pool[name] = rounds;
  return rounds;
}

function get_cooldown(name){
  const pool = ensure_cooldowns();
  return pool[name] ?? 0;
}

function activate_tk_melee_cooldown(rounds = 1){
  const applied = set_cooldown('tk_melee', rounds);
  const msg = applied > 0
    ? `TK-Nahkampf kühlt ab – ${applied} Runde Sperre.`
    : 'TK-Nahkampf bereit.';
  hud_toast(msg, '🌀');
  return applied;
}

function clear_tk_melee_cooldown(){
  const wasActive = get_cooldown('tk_melee') > 0;
  set_cooldown('tk_melee', 0);
  if (wasActive){
    hud_toast('TK-Nahkampf wieder frei – Fokus stabil.', '🌀');
  }
  return wasActive;
}

function self_reflection_enabled(){
  const character = ensure_character();
  return character.self_reflection !== false;
}

function set_self_reflection(on){
  const enabled = !!on;
  const character = ensure_character();
  character.self_reflection = enabled;
  const statusTag = enabled ? 'SF-ON' : 'SF-OFF';
  const message = enabled
    ? 'Self-Reflection aktiv – introspektive Sequenzen frei.'
    : 'Self-Reflection deaktiviert – Fokus bleibt extern.';
  hud_toast(message, statusTag);
  return { status: statusTag, message };
}

function suggest_mode_enabled(){
  const ui = ensure_ui();
  return !!ui.suggest_mode;
}

function set_suggest_mode(on){
  const ui = ensure_ui();
  const enabled = !!on;
  ui.suggest_mode = enabled;
  const statusTag = enabled ? 'SUG-ON' : 'SUG-OFF';
  const message = enabled
    ? 'Suggest-Modus aktiv – Kodex liefert auf Anfrage kurze Vorschläge.'
    : 'Ask-Modus aktiv – Kodex reagiert nur auf direkte Fragen.';
  hud_toast(message, statusTag);
  return { status: statusTag, message };
}

function hud_toast(message, tag = 'HUD'){
  const log = ensure_logs();
  hudSequence = (hudSequence + 1) % 10000;
  const entry = { id: `hud-${hudSequence.toString().padStart(4, '0')}`, tag, message };
  log.push(entry);
  if (log.length > 32){
    log.splice(0, log.length - 32);
  }
  writeLine(`[${tag}] ${message}`);
  return entry;
}

function ForeshadowHint(text, tag = 'Foreshadow'){
  const cleaned = (text ?? '').toString().trim();
  if (!cleaned){
    throw new Error('ForeshadowHint: text fehlt.');
  }
  const normalizedTag = typeof tag === 'string' && tag.trim() ? tag.trim() : 'Foreshadow';
  const tokenBase = cleaned
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
  const token = tokenBase ? `manual:${tokenBase}` : `manual:${Date.now()}`;
  register_foreshadow(token, { message: cleaned, tag: normalizedTag });
  return hud_toast(`${normalizedTag}: ${cleaned}`, normalizedTag);
}

function show_compliance_once(force = false){
  ensure_logs();
  const flags = state.logs.flags;
  const alreadyShown = !!flags.compliance_shown_today;
  if (alreadyShown && !force){
    return false;
  }
  writeLine(COMPLIANCE_NOTICE);
  flags.compliance_shown_today = true;
  if (state.campaign && typeof state.campaign === 'object'){
    state.campaign.compliance_shown_today = true;
  }
  return !alreadyShown || force;
}

function play_hq_intro(force = false){
  const ui = ensure_ui();
  show_compliance_once();
  if (ui.intro_seen && !force) return false;
  writeLine(HQ_INTRO_LINES.join('\n'));
  ui.intro_seen = true;
  return true;
}

function ensure_exfil(){
  if (!state.exfil){
    state.exfil = {};
  }
  const exfil = state.exfil;
  if (!Number.isFinite(exfil.sweeps)) exfil.sweeps = 0;
  if (!Number.isFinite(exfil.stress)) exfil.stress = 0;
  if (!Number.isFinite(exfil.ttl_min)) exfil.ttl_min = 8;
  if (!Number.isFinite(exfil.ttl_sec)) exfil.ttl_sec = 0;
  exfil.active = !!exfil.active;
  exfil.armed = !!exfil.armed;
  if (typeof exfil.anchor !== 'string') exfil.anchor = null;
  if (typeof exfil.alt_anchor !== 'string') exfil.alt_anchor = null;
  return exfil;
}

function normalize_anchor(raw){
  if (!raw) return null;
  const trimmed = raw.trim();
  return trimmed.length ? trimmed.toUpperCase() : null;
}

function exfil_arm(anchor){
  const exfil = ensure_exfil();
  exfil.active = true;
  exfil.armed = true;
  const resolved = normalize_anchor(anchor) ?? exfil.anchor ?? '?';
  exfil.anchor = normalize_anchor(resolved) ?? '?';
  const parts = ['Exfil armiert'];
  if (exfil.anchor && exfil.anchor !== '?'){
    parts.push(`ANCR ${exfil.anchor}`);
  } else {
    parts.push('ANCR ?');
  }
  const message = parts.join(' · ');
  hud_toast(message);
  return message;
}

function exfil_set_alt(anchor){
  const exfil = ensure_exfil();
  const resolved = normalize_anchor(anchor);
  exfil.alt_anchor = resolved;
  const message = resolved ? `Exfil Alt-Anchor → ${resolved}` : 'Exfil Alt-Anchor entfernt';
  hud_toast(message);
  return message;
}

function parse_rw_token(token){
  const trimmed = (token || '').trim();
  if (!trimmed) throw new Error('RW-Angabe fehlt (mm:ss).');
  const match = trimmed.match(/^(-?\d+)(?::(\d{1,2}))?$/);
  if (!match) throw new Error('RW-Format ungültig. Erwartet mm:ss.');
  const min = parseInt(match[1], 10);
  const sec = match[2] !== undefined ? parseInt(match[2], 10) : 0;
  if (!Number.isFinite(min) || !Number.isFinite(sec) || sec < 0 || sec >= 60){
    throw new Error('RW-Format ungültig. Minuten/Sekunden prüfen.');
  }
  return { min: Math.max(0, min), sec: Math.max(0, sec) };
}

function exfil_tick(token){
  const exfil = ensure_exfil();
  const { min, sec } = parse_rw_token(token);
  exfil.ttl_min = min;
  exfil.ttl_sec = sec;
  const ttl = ttl_fmt(min, sec);
  const message = `Exfil Tick · RW ${ttl}`;
  hud_toast(message);
  return ttl;
}

function ensure_campaign(){
  state.campaign ||= {};
  if (typeof state.campaign.paradoxon_index !== 'number'){
    const raw = Number(state.campaign.paradoxon_index);
    state.campaign.paradoxon_index = Number.isFinite(raw) ? raw : 0;
  }
  if (!Number.isFinite(state.campaign.px)){
    const px = Number(state.campaign.px ?? state.campaign.paradoxon_index);
    state.campaign.px = Number.isFinite(px) ? px : state.campaign.paradoxon_index ?? 0;
  }
  if (!Number.isFinite(state.campaign.paradoxon_index)){
    state.campaign.paradoxon_index = state.campaign.px ?? 0;
  }
  if (typeof state.campaign.missions_since_px !== 'number'){
    state.campaign.missions_since_px = 0;
  }
  if (!Array.isArray(state.campaign.rift_seeds)){
    state.campaign.rift_seeds = [];
  }
  if (!Array.isArray(state.campaign.rift_blueprints)){
    state.campaign.rift_blueprints = [];
  }
  if (typeof state.campaign.research_level !== 'number'){
    state.campaign.research_level = 0;
  }
  if (typeof state.campaign.chronopolis_missions_since_reset !== 'number'){
    state.campaign.chronopolis_missions_since_reset = 0;
  }
  if (typeof state.campaign.chronopolis_tick_modulo !== 'number'){
    state.campaign.chronopolis_tick_modulo = 3;
  }
  if (typeof state.campaign.episode !== 'number'){
    const episode = Number(state.campaign.episode);
    state.campaign.episode = Number.isFinite(episode) ? episode : 0;
  }
  if (typeof state.campaign.scene !== 'number'){
    const scene = Number(state.campaign.scene);
    state.campaign.scene = Number.isFinite(scene) ? scene : state.scene?.index ?? 0;
  }
  if (typeof state.campaign.phase !== 'string'){
    state.campaign.phase = state.phase || 'core';
  }
  if (typeof state.campaign.id !== 'string' || !state.campaign.id.trim()){
    const base = state.character?.id || 'campaign';
    state.campaign.id = String(base).trim() || 'campaign';
  }
  if (typeof state.campaign.mode !== 'string' || !state.campaign.mode.trim()){
    state.campaign.mode = 'preserve';
  }
  const complianceFlag = !!(state.logs?.flags?.compliance_shown_today);
  if (typeof state.campaign.compliance_shown_today !== 'boolean'){
    state.campaign.compliance_shown_today = complianceFlag;
  } else {
    state.campaign.compliance_shown_today = !!state.campaign.compliance_shown_today;
  }
}

function campaign_mode(ctx = state){
  const fallback = state.campaign?.mode;
  const raw = ctx?.campaign?.mode ?? fallback;
  if (typeof raw !== 'string' || !raw.trim()){
    return 'preserve';
  }
  const normalized = raw.trim().toLowerCase();
  if (['pvp', 'arena', 'sparring'].includes(normalized)){
    return 'pvp';
  }
  return normalized;
}

function is_pvp(ctx = state){
  if (campaign_mode(ctx) === 'pvp'){
    return true;
  }
  const arenaState = ctx?.arena ?? state.arena;
  return !!(arenaState && typeof arenaState === 'object' && arenaState.active);
}

function phase_strike_tax(ctx = state){
  return is_pvp(ctx) ? 1 : 0;
}

function phase_strike_cost(ctx = state, baseOrOptions = 2, maybeOptions = {}){
  let base = 2;
  let options = {};
  if (Number.isFinite(baseOrOptions)){
    base = Number(baseOrOptions);
    if (maybeOptions && typeof maybeOptions === 'object'){
      options = maybeOptions;
    }
  } else if (baseOrOptions && typeof baseOrOptions === 'object'){
    options = baseOrOptions;
    if (Number.isFinite(options.base)){
      base = Number(options.base);
    }
  }
  const tax = phase_strike_tax(ctx);
  const total = base + tax;
  const feedback = options.feedback !== false;
  const logEnabled = options.log !== false;
  if (feedback && tax > 0){
    const customMessage = typeof options.toast_message === 'string' ? options.toast_message.trim() : '';
    const toast = customMessage || `Arena: Phase-Strike belastet +${tax} SYS (Kosten ${total})`;
    hud_toast(toast, 'ARENA');
  }
  if (logEnabled && tax > 0){
    log_phase_strike_event(ctx, { base, tax, total, reason: options.reason });
  }
  return total;
}

function mission_temp(){
  return state.character?.attributes?.TEMP ?? 0;
}

function missions_required(temp){
  const t = Number.isFinite(temp) ? temp : 0;
  if (t <= 3) return 5;
  if (t <= 7) return 4;
  if (t <= 10) return 3;
  if (t <= 13) return 2;
  return 1;
}

function incrementParadoxon(delta = 1){
  ensure_campaign();
  const current = clamp(state.campaign.paradoxon_index ?? 0, 0, 5);
  const next = clamp(current + delta, 0, 5);
  state.campaign.paradoxon_index = next;
  state.campaign.px = next;
  return next;
}

function ClusterCreate(){
  ensure_campaign();
  if ((state.campaign.paradoxon_index ?? 0) < 5) return state.campaign.paradoxon_index;
  const count = 1 + Math.floor(Math.random() * 2);
  const seeds = [];
  for (let i = 0; i < count; i++){
    const id = `R-${Math.random().toString(36).slice(2, 6).toUpperCase()}`;
    seeds.push({
      id,
      name: 'Uncharted Rift',
      severity: 1 + Math.floor(Math.random() * 3),
      status: 'open'
    });
  }
  state.campaign.rift_seeds = [...state.campaign.rift_seeds, ...seeds];
  state.campaign.paradoxon_index = 0;
  state.campaign.missions_since_px = 0;
  state.campaign.px = 0;
  writeLine(`ClusterCreate() aktiv – ${count} Rift-Seeds sichtbar.`);
  return state.campaign.paradoxon_index;
}

function completeMission(summary = {}){
  ensure_campaign();
  const events = [];
  const temp = typeof summary.temp === 'number' ? summary.temp : mission_temp();
  const required = missions_required(temp);
  const stabilized = summary.stabilized || summary.success || summary.completed === 'stabilized';
  if (stabilized){
    state.campaign.missions_since_px = (state.campaign.missions_since_px ?? 0) + 1;
    const progress = state.campaign.missions_since_px;
    events.push(`Kodex: Mission stabilisiert (${progress}/${required} für Px+1).`);
    if (progress >= required){
      state.campaign.missions_since_px = 0;
      const after = incrementParadoxon(1);
      events.push(`Kodex: Paradoxon-Index steigt auf ${after}/5.`);
      if (after >= 5){
        ClusterCreate();
        events.push('Kodex: ClusterCreate() aktiv – neue Rift-Seeds verfügbar.');
      }
    }
  }
  const chronoReset = chronopolisProgressAfterMission(summary);
  if (chronoReset === 'episode'){
    events.push('Kodex: Chronopolis-Angebote neu instanziiert – Episode abgeschlossen.');
  } else if (chronoReset === 'mission-cycle'){
    events.push('Kodex: Chronopolis-Angebote rotiert – HQ-Zyklus erreicht.');
  }
  return {
    events,
    required,
    missions_since_px: state.campaign.missions_since_px ?? 0,
    paradoxon_index: state.campaign.paradoxon_index ?? 0
  };
}

function reset_mission_state(){
  state.exfil = null;
  state.fr_intervention = null;
  state.scene = { index: 0, foreshadows: 0, total: 12 };
  state.comms = { jammed: false, relays: 0, rangeMod: 1.0 };
  state.start = null;
  hudSequence = 0;
  state.mission = { id: null, objective: null, clock: {}, timers: [] };
  const initiative = ensure_initiative();
  initiative.order = [];
  initiative.active_id = null;
  const hud = ensure_hud_state();
  hud.timers = [];
  ensure_team();
  ensure_party();
}

function clamp(n, min, max){
  return Math.min(max, Math.max(min, n));
}

function writeLine(msg){
  console.log(msg);
}

function px_bar(n){
  const total = 5;
  return '█'.repeat(n) + '░'.repeat(total - n);
}

function render_px_tracker(temp){
  ensure_campaign();
  const n = clamp(state.campaign?.paradoxon_index ?? 0, 0, 5);
  const t = temp ?? mission_temp();
  const required = missions_required(t);
  const progress = clamp(state.campaign?.missions_since_px ?? 0, 0, required);
  const remaining = Math.max(0, required - progress);
  const eta = `${remaining} Mission${remaining === 1 ? '' : 'en'}`;
  return `Px ${px_bar(n)} (${n}/5) · TEMP ${t} · ETA +1 in ${eta}`;
}

const px_tracker = render_px_tracker;

function offline_log_entries(){
  return Array.isArray(state.logs?.offline) ? state.logs.offline : [];
}

function offline_audit(trigger='auto', context = {}){
  ensure_logs();
  const flags = state.logs.flags || {};
  const entry = {
    timestamp: context.timestamp,
    reason: trigger,
    status: context.status || 'offline',
    device: context.device ?? state.comms?.device,
    jammed: context.jammed ?? state.comms?.jammed,
    range_m: context.range_m ?? state.comms?.range_m,
    relays: context.relays ?? state.comms?.relays,
    note: context.note,
    count: context.count ?? flags.offline_help_count,
    scene_index: context.scene_index ?? state.scene?.index,
    scene_total: context.scene_total ?? state.scene?.total,
    episode: context.episode ?? state.campaign?.episode,
    mission: context.mission ?? state.campaign?.mission,
    location: context.location ?? state.location,
    phase: context.phase ?? state.phase,
    gm_style: context.gm_style ?? ensure_ui().gm_style
  };
  const offlineLog = ensure_offline_log();
  const normalized = normalize_offline_entry(entry, new Date().toISOString());
  if (!normalized){
    return null;
  }
  offlineLog.push(normalized);
  if (offlineLog.length > OFFLINE_LOG_LIMIT){
    offlineLog.splice(0, offlineLog.length - OFFLINE_LOG_LIMIT);
  }
  return normalized;
}

function log_intervention(result, context = {}){
  const base = {};
  const nowIso = new Date().toISOString();
  if (context && typeof context === 'object'){
    Object.assign(base, context);
  }
  if (result && typeof result === 'object' && !Array.isArray(result)){
    Object.assign(base, result);
  } else if (result !== undefined){
    base.result = result;
  }
  if (!base.timestamp){
    base.timestamp = nowIso;
  }
  if (base.scene_index === undefined && Number.isFinite(state.scene?.index)){
    base.scene_index = state.scene.index;
  }
  if (base.scene_total === undefined && Number.isFinite(state.scene?.total)){
    base.scene_total = state.scene.total;
  }
  if (base.phase === undefined && typeof state.phase === 'string'){
    base.phase = state.phase;
  }
  if (base.location === undefined && typeof state.location === 'string'){
    base.location = state.location;
  }
  if (base.mission === undefined && Number.isFinite(state.campaign?.mission)){
    base.mission = state.campaign.mission;
  }
  if (base.episode === undefined && Number.isFinite(state.campaign?.episode)){
    base.episode = state.campaign.episode;
  }
  if (base.gm_style === undefined){
    base.gm_style = ensure_ui().gm_style;
  }
  const normalized = normalize_intervention_entry(base, nowIso, { fillDefaults: true });
  if (!normalized){
    throw new Error('log_intervention: Ergebnis fehlt.');
  }
  const log = ensure_intervention_log();
  log.push(normalized);
  if (log.length > FR_INTERVENTION_LOG_LIMIT){
    log.splice(0, log.length - FR_INTERVENTION_LOG_LIMIT);
  }
  update_arc_dashboard_intervention(normalized);
  const shouldToast = base.toast !== false;
  const toastTag = typeof base.toast_tag === 'string' && base.toast_tag.trim() ? base.toast_tag.trim() : 'FR-INTRV';
  if (shouldToast){
    hud_toast(`FR-INTRV: ${normalized.result}`, toastTag);
  }
  return normalized;
}

function get_intervention_log(filter = {}){
  const entries = ensure_intervention_log();
  const factions = Array.isArray(filter.faction)
    ? filter.faction.filter(f => typeof f === 'string' && f.trim()).map(f => f.trim().toLowerCase())
    : (typeof filter.faction === 'string' && filter.faction.trim())
    ? [filter.faction.trim().toLowerCase()]
    : [];
  const resultFilter = typeof filter.result === 'string' && filter.result.trim()
    ? filter.result.trim().toLowerCase()
    : null;
  const observerFilter = typeof filter.observer === 'boolean' ? filter.observer : null;
  const escalatedFilter = typeof filter.escalated === 'boolean' ? filter.escalated : null;
  const sinceMs = filter.since ? Date.parse(filter.since) : null;
  const untilMs = filter.until ? Date.parse(filter.until) : null;
  return entries
    .filter((entry) => {
      if (factions.length){
        const factionKey = typeof entry.faction === 'string' ? entry.faction.trim().toLowerCase() : '';
        if (!factions.includes(factionKey)){
          return false;
        }
      }
      if (resultFilter && (!entry.result || entry.result.trim().toLowerCase() !== resultFilter)){
        return false;
      }
      if (observerFilter !== null && !!entry.observer !== observerFilter){
        return false;
      }
      if (escalatedFilter !== null && !!entry.escalated !== escalatedFilter){
        return false;
      }
      if (sinceMs !== null){
        const ts = Date.parse(entry.timestamp);
        if (Number.isFinite(ts) && ts < sinceMs){
          return false;
        }
      }
      if (untilMs !== null){
        const ts = Date.parse(entry.timestamp);
        if (Number.isFinite(ts) && ts > untilMs){
          return false;
        }
      }
      return true;
    })
    .map(entry => clone_plain_object(entry));
}

function describe_arc_seed(entry){
  if (entry === undefined || entry === null){
    return null;
  }
  if (typeof entry === 'string'){
    const trimmed = entry.trim();
    return trimmed.length ? trimmed : null;
  }
  if (typeof entry !== 'object'){
    return String(entry);
  }
  const id = typeof entry.id === 'string' && entry.id.trim() ? entry.id.trim() : null;
  const key = typeof entry.key === 'string' && entry.key.trim() ? entry.key.trim() : null;
  const title = typeof entry.title === 'string' && entry.title.trim() ? entry.title.trim() : null;
  const hook = typeof entry.hook === 'string' && entry.hook.trim() ? entry.hook.trim() : null;
  const epoch = typeof entry.epoch === 'string' && entry.epoch.trim() ? entry.epoch.trim() : null;
  const status = typeof entry.status === 'string' && entry.status.trim() ? entry.status.trim() : null;
  const severity = entry.severity !== undefined && entry.severity !== null
    ? entry.severity
    : (entry.level !== undefined ? entry.level : null);
  const deadline = typeof entry.deadline === 'string' && entry.deadline.trim()
    ? entry.deadline.trim()
    : (typeof entry.until === 'string' && entry.until.trim() ? entry.until.trim() : null);
  const labelParts = [];
  if (id){
    labelParts.push(`#${id}`);
  } else if (key){
    labelParts.push(`#${key}`);
  }
  if (title){
    labelParts.push(title);
  } else if (hook){
    labelParts.push(hook);
  }
  if (!labelParts.length && epoch){
    labelParts.push(epoch);
  }
  if (!labelParts.length){
    labelParts.push('Seed');
  }
  const tagParts = [];
  if (epoch){
    tagParts.push(epoch);
  }
  if (status){
    tagParts.push(status);
  }
  if (Number.isFinite(severity)){
    tagParts.push(`Stufe ${severity}`);
  } else if (typeof severity === 'string' && severity.trim()){
    tagParts.push(severity.trim());
  }
  if (deadline){
    tagParts.push(`bis ${deadline}`);
  }
  if (typeof entry.priority === 'string' && entry.priority.trim()){
    tagParts.push(entry.priority.trim());
  }
  const label = labelParts.join(' · ');
  return tagParts.length ? `${label} · ${tagParts.join(' · ')}` : label;
}

function describe_arc_question(entry){
  if (entry === undefined || entry === null){
    return null;
  }
  if (typeof entry === 'string'){
    const trimmed = entry.trim();
    return trimmed.length ? trimmed : null;
  }
  if (typeof entry !== 'object'){
    return String(entry);
  }
  const title = ['title', 'question', 'prompt', 'summary', 'text']
    .map((key) => typeof entry[key] === 'string' && entry[key].trim() ? entry[key].trim() : null)
    .find(Boolean);
  const identifier = ['id', 'key', 'ref']
    .map((key) => typeof entry[key] === 'string' && entry[key].trim() ? entry[key].trim() : null)
    .find(Boolean);
  const status = typeof entry.status === 'string' && entry.status.trim() ? entry.status.trim() : null;
  const owner = typeof entry.owner === 'string' && entry.owner.trim()
    ? entry.owner.trim()
    : (typeof entry.assignee === 'string' && entry.assignee.trim() ? entry.assignee.trim() : null);
  const episode = Number.isFinite(entry.episode) ? `E${entry.episode}` : null;
  const mission = Number.isFinite(entry.mission) ? `M${entry.mission}` : null;
  const labelParts = [];
  if (identifier){
    labelParts.push(identifier);
  }
  if (title){
    labelParts.push(title);
  }
  if (!labelParts.length){
    labelParts.push('Frage');
  }
  const tagParts = [status, owner, episode, mission].filter(Boolean);
  return tagParts.length ? `${labelParts.join(' · ')} · ${tagParts.join(' · ')}` : labelParts.join(' · ');
}

function render_arc_dashboard_status(){
  const dash = ensure_arc_dashboard();
  const lines = [];
  lines.push('Arc-Dashboard Status');
  const seeds = Array.isArray(dash.offene_seeds) ? dash.offene_seeds : [];
  const seedLines = seeds
    .map(describe_arc_seed)
    .filter((line) => typeof line === 'string' && line.trim());
  if (seedLines.length){
    lines.push('Seeds:');
    seedLines.forEach((line) => {
      lines.push(`• ${line}`);
    });
  } else {
    lines.push('Seeds: keine offenen Seeds.');
  }

  const factions = dash.fraktionen && typeof dash.fraktionen === 'object' && !Array.isArray(dash.fraktionen)
    ? Object.values(dash.fraktionen)
    : [];
  const factionRecords = factions
    .filter((record) => record && typeof record === 'object')
    .map((record) => ({ ...record }));
  if (factionRecords.length){
    lines.push('Fraktionen:');
    factionRecords
      .sort((a, b) => {
        const nameA = (a.name || a.id || '').toLowerCase();
        const nameB = (b.name || b.id || '').toLowerCase();
        return nameA.localeCompare(nameB);
      })
      .forEach((record) => {
        const name = record.name || record.id || 'Fraktion';
        const last = record.last_intervention && typeof record.last_intervention === 'object'
          ? record.last_intervention
          : null;
        const result = typeof (last?.result || record.last_result) === 'string'
          ? (last?.result || record.last_result)
          : 'keine Aktivität';
        const tags = [];
        if (Number.isFinite(last?.episode)){
          tags.push(`E${last.episode}`);
        }
        if (Number.isFinite(last?.mission)){
          tags.push(`M${last.mission}`);
        }
        if (typeof last?.phase === 'string' && last.phase.trim()){
          tags.push(last.phase.trim());
        }
        if (Number.isFinite(last?.scene_index)){
          const index = Math.max(0, last.scene_index);
          const sceneNumber = index + 1;
          if (Number.isFinite(last?.scene_total)){
            tags.push(`Sz ${sceneNumber}/${last.scene_total}`);
          } else {
            tags.push(`Sz ${sceneNumber}`);
          }
        }
        if (typeof last?.location === 'string' && last.location.trim()){
          tags.push(last.location.trim());
        }
        if (last?.escalated){
          tags.push('Escal');
        }
        if (last?.observer){
          tags.push('Beobachter');
        }
        if (typeof record.interventions?.length === 'number' && record.interventions.length > 1){
          tags.push(`Verlauf ${record.interventions.length}×`);
        }
        const suffix = tags.length ? ` (${tags.join(' · ')})` : '';
        const timestamp = typeof last?.timestamp === 'string' && last.timestamp.trim()
          ? ` @ ${last.timestamp.trim()}`
          : '';
        lines.push(`• ${name}: ${result}${suffix}${timestamp}`);
        if (typeof last?.impact === 'string' && last.impact.trim()){
          lines.push(`  Impact: ${last.impact.trim()}`);
        }
        if (typeof last?.note === 'string' && last.note.trim()){
          lines.push(`  Notiz: ${last.note.trim()}`);
        }
      });
  } else {
    lines.push('Fraktionen: keine Interventionen protokolliert.');
  }

  const questions = Array.isArray(dash.fragen) ? dash.fragen : [];
  const questionLines = questions
    .map(describe_arc_question)
    .filter((line) => typeof line === 'string' && line.trim());
  if (questionLines.length){
    lines.push('Fragen:');
    questionLines.forEach((line) => {
      lines.push(`• ${line}`);
    });
  } else {
    lines.push('Fragen: keine offenen Rückfragen.');
  }

  return lines.join('\n');
}

function format_offline_report(entry, totalCount){
  if (!entry) return null;
  const segments = [];
  const reason = typeof entry.reason === 'string' ? entry.reason.trim() : '';
  if (reason){
    if (reason === 'command'){
      segments.push('manueller Abruf');
    } else if (reason === 'auto'){
      segments.push('Fallback');
    } else {
      segments.push(reason);
    }
  }
  if (entry.device){
    segments.push(`Gerät ${entry.device}`);
  }
  if (typeof entry.jammed === 'boolean'){
    segments.push(entry.jammed ? 'Jammer aktiv' : 'Jammer frei');
  }
  if (Number.isFinite(entry.range_m)){
    const range = Math.max(0, Math.round(entry.range_m));
    segments.push(`Reichweite ${range}m`);
  }
  if (Number.isFinite(entry.relays)){
    const relays = Math.max(0, Math.floor(entry.relays));
    segments.push(`Relais ${relays}`);
  }
  if (Number.isFinite(entry.scene_index) && Number.isFinite(entry.scene_total)){
    segments.push(`Szene ${entry.scene_index}/${entry.scene_total}`);
  } else if (Number.isFinite(entry.scene_index)){
    segments.push(`Szene ${entry.scene_index}`);
  }
  if (Number.isFinite(entry.episode)){
    segments.push(`EP ${entry.episode}`);
  }
  if (Number.isFinite(entry.mission)){
    segments.push(`MS ${entry.mission}`);
  }
  if (entry.note){
    segments.push(entry.note);
  }
  const total = Math.max(1, Number(totalCount) || 1);
  const header = `Offline-Protokoll (${total}×)`;
  if (!segments.length){
    return `${header}: Fallback aktiv.`;
  }
  return `${header}: ${segments.join(' · ')}`;
}

function render_offline_protocol(){
  const entries = offline_log_entries();
  if (!entries.length) return null;
  const latest = entries[entries.length - 1];
  const total = state.logs?.flags?.offline_help_count || entries.length;
  return format_offline_report(latest, total);
}

function format_market_entry(entry){
  if (!entry || typeof entry !== 'object') return '';
  const segments = [];
  if (typeof entry.timestamp === 'string' && entry.timestamp.trim()){
    segments.push(entry.timestamp.trim());
  }
  if (typeof entry.item === 'string' && entry.item.trim()){
    segments.push(entry.item.trim());
  }
  if (Number.isFinite(entry.quantity) && entry.quantity > 1){
    segments.push(`x${Math.max(1, Math.floor(entry.quantity))}`);
  }
  const cost = Number(entry.cost_cu);
  if (Number.isFinite(cost)){
    segments.push(`${Math.max(0, Math.round(cost))} CU`);
  }
  if (typeof entry.px_clause === 'string' && entry.px_clause.trim()){
    segments.push(entry.px_clause.trim());
  }
  if (typeof entry.note === 'string' && entry.note.trim()){
    segments.push(entry.note.trim());
  }
  if (typeof entry.source === 'string' && entry.source.trim()){
    segments.push(`Quelle ${entry.source.trim()}`);
  }
  return segments.join(' · ');
}

function render_market_trace(limit = 2){
  const log = ensure_market_log();
  if (!log.length) return null;
  const slice = log.slice(Math.max(0, log.length - Math.max(1, limit)));
  const entries = slice.map(format_market_entry).filter(Boolean);
  if (!entries.length) return null;
  if (log.length > slice.length){
    entries.unshift('…');
  }
  return `Chronopolis-Trace (${log.length}×): ${entries.join(' | ')}`;
}

function render_foreshadow_report(limit = 3){
  const entries = foreshadow_entries();
  if (!entries.length) return null;
  const slice = entries.slice(Math.max(0, entries.length - Math.max(1, limit)));
  const summaries = slice.map((entry) => {
    if (!entry || typeof entry !== 'object') return '';
    const parts = [];
    const tag = typeof entry.tag === 'string' && entry.tag.trim() ? entry.tag.trim() : 'Foreshadow';
    parts.push(tag);
    if (Number.isFinite(entry.scene)){
      parts.push(`Szene ${entry.scene}`);
    }
    if (typeof entry.message === 'string' && entry.message.trim()){
      parts.push(entry.message.trim());
    }
    return parts.join(' – ');
  }).filter(Boolean);
  if (!summaries.length) return null;
  if (entries.length > slice.length){
    summaries.unshift('…');
  }
  return `Foreshadow-Log (${entries.length}×): ${summaries.join(' | ')}`;
}

function render_runtime_flags_summary(){
  ensure_logs();
  const flags = state.logs?.flags || {};
  const parts = [];
  if (typeof flags.runtime_version === 'string' && flags.runtime_version.trim()){
    parts.push(`Runtime ${flags.runtime_version.trim()}`);
  }
  parts.push(flags.compliance_shown_today ? 'Compliance gezeigt' : 'Compliance offen');
  parts.push(flags.chronopolis_warn_seen ? 'Chronopolis-Warnung quittiert' : 'Chronopolis-Warnung offen');
  if (Number.isFinite(flags.offline_help_count) && flags.offline_help_count > 0){
    parts.push(`Offline-Hilfe ${Math.max(0, Math.floor(flags.offline_help_count))}×`);
  }
  if (typeof flags.offline_help_last === 'string' && flags.offline_help_last.trim()){
    parts.push(`Offline zuletzt ${flags.offline_help_last.trim()}`);
  }
  if (!parts.length) return null;
  return `Runtime-Flags: ${parts.join(' · ')}`;
}

function asNumber(value){
  if (value === null || value === undefined) return null;
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function normalize_cu(value){
  const num = asNumber(value);
  if (num === null) return null;
  return Math.max(0, Math.round(num));
}

function sumCuFromArray(entries){
  if (!Array.isArray(entries)) return null;
  let total = 0;
  let found = false;
  entries.forEach((entry) => {
    if (entry === null || entry === undefined) return;
    if (typeof entry === 'number'){
      total += entry;
      found = true;
      return;
    }
    if (typeof entry !== 'object') return;
    const label = [entry.currency, entry.type, entry.kind, entry.key]
      .find((token) => typeof token === 'string' && /cu/i.test(token));
    if (!label) return;
    const amount = asNumber(entry.amount ?? entry.value ?? entry.cu ?? entry.credits);
    if (amount !== null){
      total += amount;
      found = true;
    }
  });
  return found ? total : null;
}

function extractCuReward(outcome){
  const sources = [
    outcome,
    outcome?.reward,
    outcome?.rewards,
    outcome?.rewards?.primary,
    outcome?.currency,
    outcome?.payout,
    outcome?.economy,
    outcome?.economy?.delta,
    outcome?.economy?.change
  ];
  const keys = ['cu_reward', 'chrono_units', 'chronounits', 'chronounit', 'cu', 'credits', 'payout', 'amount', 'value'];
  for (const source of sources){
    if (!source) continue;
    if (Array.isArray(source)){
      const summed = sumCuFromArray(source);
      if (summed !== null) return summed;
      continue;
    }
    for (const key of keys){
      const value = asNumber(source[key]);
      if (value !== null) return value;
    }
    if (typeof source === 'object'){
      for (const [key, value] of Object.entries(source)){
        if (typeof value === 'object'){
          const nested = extractCuReward(value);
          if (nested !== null) return nested;
        }
        if (typeof key === 'string' && /cu/i.test(key)){
          const asNum = asNumber(value);
          if (asNum !== null) return asNum;
        }
      }
    }
  }
  const fallback = asNumber(state.campaign?.cu_payout);
  return fallback !== null && fallback > 0 ? fallback : null;
}

function resolveLevelInfo(outcome){
  const candidatePairs = [
    [outcome?.level_before, outcome?.level_after],
    [outcome?.prev_level, outcome?.new_level],
    [outcome?.level?.before, outcome?.level?.after],
    [outcome?.lvl_before, outcome?.lvl_after],
    [outcome?.level_start, outcome?.level_end]
  ];
  let before = null;
  let after = null;
  for (const [b, a] of candidatePairs){
    const nb = asNumber(b);
    const na = asNumber(a);
    if (nb !== null && na !== null){
      before = nb;
      after = na;
      break;
    }
  }
  if (after === null){
    const charLevel = asNumber(state.character?.lvl ?? state.character?.level);
    if (charLevel !== null){
      after = charLevel;
    }
  }
  if (before === null && after !== null){
    const delta = asNumber(outcome?.level_delta ?? outcome?.lvl_delta);
    if (delta !== null){
      before = after - delta;
    }
  }
  const leveledUp = (() => {
    if (before !== null && after !== null) return after > before;
    if (outcome?.level_up === true) return true;
    const delta = asNumber(outcome?.level_delta ?? outcome?.lvl_delta);
    return delta !== null && delta > 0;
  })();
  return { before, after, leveledUp };
}

function render_rewards(outcome = {}, missionResult = {}){
  ensure_campaign();
  ensure_character();
  ensure_economy();

  const segments = [];
  const cuReward = extractCuReward(outcome);
  if (cuReward !== null){
    segments.push(`Chrono Units +${cuReward} CU`);
  } else {
    segments.push('Chrono Units n/a');
  }

  const { before: lvlBefore, after: lvlAfter, leveledUp } = resolveLevelInfo(outcome);
  if (leveledUp && lvlBefore !== null && lvlAfter !== null){
    segments.push(`Level-Up ${lvlBefore}→${lvlAfter}`);
  } else if (lvlAfter !== null){
    segments.push(`Level ${lvlAfter}`);
  }

  const px = clamp(asNumber(missionResult?.paradoxon_index) ?? asNumber(state.campaign?.paradoxon_index) ?? 0, 0, 5);
  const progress = Math.max(0, asNumber(missionResult?.missions_since_px) ?? asNumber(state.campaign?.missions_since_px) ?? 0);
  const required = Math.max(1, asNumber(missionResult?.required) ?? missions_required(asNumber(outcome?.temp) ?? mission_temp()));
  const remaining = Math.max(0, required - progress);
  segments.push(`Resonanz Px ${px}/5 (${remaining}/${required} bis Px+1)`);

  const rank = state.character?.rank || state.character?.callsign;
  if (rank){
    segments.push(`Rang ${rank}`);
  }

  return `Belohnungen · ${segments.join(' · ')}`;
}

function build_wallet_roster(){
  const roster = [];
  const indexById = new Map();
  const register = (candidate = {}, fallbackLabel) => {
    const rawId = typeof candidate.id === 'string' && candidate.id.trim() ? candidate.id.trim() : null;
    const labels = [candidate.callsign, candidate.name, candidate.alias, candidate.handle, fallbackLabel]
      .filter((value) => typeof value === 'string' && value.trim());
    const label = labels.length ? labels[0].trim() : null;
    let id = rawId;
    if (!id && label){
      id = label.toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '');
    }
    if (!id){
      id = `agent-${roster.length + 1}`;
    }
    if (indexById.has(id)){
      const existing = roster[indexById.get(id)];
      if (!existing.label && label){
        existing.label = label;
      }
      return existing;
    }
    const entry = { id, label: label || id };
    roster.push(entry);
    indexById.set(id, roster.length - 1);
    return entry;
  };

  const character = ensure_character();
  register(character, 'Operator');

  const party = ensure_party();
  if (Array.isArray(party.characters)){
    party.characters.forEach((member) => {
      if (member && typeof member === 'object'){
        register(member, 'Agent');
      }
    });
  }

  const team = ensure_team();
  if (Array.isArray(team.members)){
    team.members.forEach((member) => {
      if (member && typeof member === 'object'){
        register(member, 'Agent');
      }
    });
  }

  if (!roster.length){
    register({ id: 'agent-1', callsign: 'Agent' }, 'Agent');
  }

  return { roster, indexById };
}

function normalize_wallet_instruction(entry, fallbackMember, rosterInfo){
  if (entry === null || entry === undefined) return null;
  let payload = entry;
  if (typeof entry === 'number'){
    payload = { amount: entry };
  } else if (typeof entry === 'string'){
    const parts = entry.split(':');
    if (parts.length === 2){
      payload = { id: parts[0], amount: parts[1] };
    } else {
      return null;
    }
  }
  if (typeof payload !== 'object' || Array.isArray(payload)){
    return null;
  }
  let id = typeof payload.id === 'string' && payload.id.trim() ? payload.id.trim() : null;
  let label = typeof payload.label === 'string' && payload.label.trim() ? payload.label.trim() : null;
  if (!label && typeof payload.name === 'string' && payload.name.trim()){
    label = payload.name.trim();
  }
  if (!id && fallbackMember){
    id = fallbackMember.id;
    label = label || fallbackMember.label;
  }
  if (!id){
    return null;
  }
  if (!label && rosterInfo.indexById.has(id)){
    label = rosterInfo.roster[rosterInfo.indexById.get(id)].label;
  }
  const amount = normalize_cu(payload.amount ?? payload.share ?? payload.value ?? payload.cu ?? payload.payout ?? payload.delta ?? payload.balance);
  let ratio = asNumber(payload.ratio ?? payload.percent ?? payload.weight ?? payload.share_ratio ?? payload.portion ?? payload.percent_share);
  if (ratio !== null){
    ratio = Math.max(0, ratio > 1 ? (ratio > 100 ? ratio / 100 : ratio / 100) : ratio);
  }
  const result = {
    id,
    label,
    amount: amount !== null ? Math.max(0, amount) : null,
    ratio: ratio !== null ? Math.max(0, ratio) : null
  };
  if (result.amount === null && result.ratio === null){
    return null;
  }
  return result;
}

function gather_wallet_instructions(outcome, rosterInfo){
  const instructions = [];
  const fallbackQueue = rosterInfo.roster.slice();
  const nextFallback = () => (fallbackQueue.length ? fallbackQueue.shift() : null);
  const pushEntry = (entry) => {
    const normalized = normalize_wallet_instruction(entry, nextFallback(), rosterInfo);
    if (normalized){
      instructions.push(normalized);
    }
  };
  const consider = (source) => {
    if (!source) return;
    if (Array.isArray(source)){
      source.forEach((item) => pushEntry(item));
      return;
    }
    if (typeof source === 'object'){
      for (const [key, value] of Object.entries(source)){
        if (value && typeof value === 'object' && !Array.isArray(value)){
          pushEntry({ id: key, ...value });
        } else {
          pushEntry({ id: key, amount: value });
        }
      }
    }
  };

  consider(outcome?.economy?.split);
  consider(outcome?.economy?.wallet_split);
  consider(outcome?.economy?.wallets);
  consider(outcome?.wallet_split);
  consider(outcome?.wallets);
  consider(outcome?.cu_split);
  if (outcome?.split && typeof outcome.split === 'object' && !Array.isArray(outcome.split)){
    consider(outcome.split.wallets ?? outcome.split.members ?? outcome.split);
  }
  return instructions;
}

function compute_wallet_allocations(totalCu, rosterInfo, instructions){
  const aggregated = new Map();
  instructions.forEach((instruction) => {
    const { id } = instruction;
    if (!id) return;
    const base = aggregated.get(id) || {
      id,
      label: instruction.label || (rosterInfo.indexById.has(id) ? rosterInfo.roster[rosterInfo.indexById.get(id)].label : id),
      amount: 0,
      ratio: 0
    };
    if (instruction.amount !== null){
      base.amount = Math.max(0, base.amount + instruction.amount);
    }
    if (instruction.ratio !== null){
      base.ratio = Math.max(0, base.ratio + instruction.ratio);
    }
    if (!base.label && instruction.label){
      base.label = instruction.label;
    }
    aggregated.set(id, base);
  });

  let available = Math.max(0, Math.round(totalCu));
  const allocations = [];
  const addAllocation = (id, label, amount) => {
    const value = Math.max(0, Math.round(amount));
    if (value <= 0) return 0;
    let record = allocations.find((entry) => entry.id === id);
    if (!record){
      record = { id, label: label || (rosterInfo.indexById.has(id) ? rosterInfo.roster[rosterInfo.indexById.get(id)].label : id), amount: 0 };
      allocations.push(record);
    } else if (!record.label && label){
      record.label = label;
    }
    record.amount += value;
    return value;
  };

  aggregated.forEach((entry) => {
    if (available <= 0) return;
    if (entry.amount > 0){
      const assigned = addAllocation(entry.id, entry.label, Math.min(available, Math.round(entry.amount)));
      available -= assigned;
    }
  });

  if (available > 0){
    const ratioEntries = Array.from(aggregated.values()).filter((entry) => entry.ratio > 0);
    if (ratioEntries.length){
      const totalRatio = ratioEntries.reduce((sum, entry) => sum + entry.ratio, 0);
      if (totalRatio > 0){
        let distributed = 0;
        ratioEntries.forEach((entry, index) => {
          if (available - distributed <= 0) return;
          let share = available * (entry.ratio / totalRatio);
          if (index === ratioEntries.length - 1){
            share = available - distributed;
          } else {
            share = Math.round(share);
          }
          share = Math.max(0, Math.min(share, available - distributed));
          if (share > 0){
            addAllocation(entry.id, entry.label, share);
            distributed += share;
          }
        });
        available = Math.max(0, available - distributed);
      }
    }
  }

  if (available > 0 && instructions.length === 0){
    const recipients = rosterInfo.roster.length ? rosterInfo.roster : [{ id: 'agent-1', label: 'Agent' }];
    const baseShare = Math.floor(available / recipients.length);
    let remainder = available - baseShare * recipients.length;
    recipients.forEach((member) => {
      let share = baseShare;
      if (remainder > 0){
        share += 1;
        remainder -= 1;
      }
      if (share > 0){
        addAllocation(member.id, member.label, share);
      }
    });
    available = 0;
  }

  const totalAssigned = allocations.reduce((sum, entry) => sum + entry.amount, 0);
  return { allocations, totalAssigned, leftover: Math.max(0, Math.round(totalCu) - totalAssigned) };
}

function apply_wallet_split(outcome, cuReward){
  const reward = normalize_cu(cuReward);
  if (reward === null || reward <= 0){
    return { lines: [], payout: 0 };
  }
  const rosterInfo = build_wallet_roster();
  const instructions = gather_wallet_instructions(outcome, rosterInfo);
  const { allocations, totalAssigned, leftover } = compute_wallet_allocations(reward, rosterInfo, instructions);
  const economy = ensure_economy();
  economy.cu = Math.max(0, Math.round(economy.cu) + reward);
  allocations.forEach((entry) => {
    const record = get_wallet_record(entry.id, entry.label);
    if (!record) return;
    record.balance = Math.max(0, Math.round(record.balance || 0) + entry.amount);
    if (!record.name && entry.label){
      record.name = entry.label;
    }
  });
  if (totalAssigned > 0){
    economy.cu = Math.max(0, Math.round(economy.cu) - totalAssigned);
  }
  const lines = [];
  if (allocations.length){
    const summary = allocations.map((entry) => `${entry.label || entry.id} +${entry.amount} CU`).join(' | ');
    lines.push(`Wallet-Split (${allocations.length}×): ${summary}`);
  }
  const hqBalance = Math.max(0, Math.round(economy.cu));
  const remainderText = leftover > 0 ? ` (Rest ${leftover} CU im HQ-Pool)` : '';
  lines.push(`HQ-Pool: ${hqBalance} CU verfügbar${remainderText}.`);
  return { lines, payout: totalAssigned, leftover };
}

function ensure_economy(){
  if (!state.economy || typeof state.economy !== 'object'){
    state.economy = {};
  }
  const economy = state.economy;
  economy.cu = Number.isFinite(economy.cu) ? Math.round(economy.cu) : 0;
  ensure_wallets();
  return economy;
}

function ensure_arena(){
  state.arena ||= {};
  const arena = state.arena;
  arena.active = !!arena.active;
  arena.wins_player = Number.isFinite(arena.wins_player) ? arena.wins_player : 0;
  arena.wins_opponent = Number.isFinite(arena.wins_opponent) ? arena.wins_opponent : 0;
  arena.last_reward_episode = arena.last_reward_episode ?? null;
  arena.tier = Number.isFinite(arena.tier) ? arena.tier : 1;
  arena.proc_budget = Number.isFinite(arena.proc_budget) ? arena.proc_budget : 0;
  arena.artifact_limit = Number.isFinite(arena.artifact_limit) ? arena.artifact_limit : 0;
  arena.loadout_budget = Number.isFinite(arena.loadout_budget) ? arena.loadout_budget : 0;
  arena.audit = Array.isArray(arena.audit) ? arena.audit : [];
  arena.fee = Number.isFinite(arena.fee) ? arena.fee : 0;
  arena.scenario = arena.scenario ?? null;
  arena.damage_dampener = arena.damage_dampener !== false;
  arena.team_size = Number.isFinite(arena.team_size) ? arena.team_size : 1;
  arena.mode = typeof arena.mode === 'string' ? arena.mode : 'single';
  arena.phase_strike_tax = Number.isFinite(arena.phase_strike_tax) ? arena.phase_strike_tax : 0;
  arena.previous_mode = typeof arena.previous_mode === 'string' ? arena.previous_mode : null;
  arena.policy_players = Array.isArray(arena.policy_players)
    ? arena.policy_players.map(entry => (entry && typeof entry === 'object' ? clone_plain_object(entry) : null)).filter(Boolean)
    : undefined;
  apply_arena_rules(state);
  return arena;
}

function apply_arena_rules(ctx = state){
  if (!ctx || typeof ctx !== 'object'){ return null; }
  const arena = ctx.arena;
  if (!arena || typeof arena !== 'object'){ return null; }
  const active = !!arena.active;
  arena.damage_dampener = active && arena.damage_dampener !== false;
  arena.phase_strike_tax = active ? phase_strike_tax(ctx) : 0;
  if (!active){
    return arena;
  }
  const markBuffer = target => {
    if (!target || typeof target !== 'object'){ return; }
    target.psi_buffer = true;
  };
  markBuffer(ensure_character());
  const team = ensure_team();
  markBuffer(team);
  if (Array.isArray(team.members)){
    team.members.forEach(member => markBuffer(member));
  }
  const party = ensure_party();
  if (Array.isArray(party.characters)){
    party.characters.forEach(member => markBuffer(member));
  }
  return arena;
}

function ensure_chronopolis(){
  const economy = ensure_economy();
  economy.chronopolis ||= {};
  const chrono = economy.chronopolis;
  if (!Array.isArray(chrono.stock)) chrono.stock = [];
  if (typeof chrono.reset_serial !== 'number') chrono.reset_serial = 0;
  return chrono;
}

function ensureSuspendStorage(){
  fs.mkdirSync(SUSPEND_DIR, { recursive: true });
  return SUSPEND_DIR;
}

function majorMinor(version){
  if (!version) return null;
  const parts = String(version).split('.');
  return parts.slice(0, 2).join('.');
}

function safeCampaignId(){
  ensure_campaign();
  const raw = state.campaign?.id || state.character?.id || 'campaign';
  const normalized = String(raw).toLowerCase().replace(/[^a-z0-9_-]+/g, '-');
  const trimmed = normalized.replace(/^-+|-+$/g, '').replace(/-+/g, '-');
  return trimmed || 'campaign';
}

function suspendFilePath(){
  const dir = ensureSuspendStorage();
  const file = `${safeCampaignId()}.json`;
  return path.join(dir, file);
}

function sanitizeSnapshotClock(clock){
  if (!clock || typeof clock !== 'object') return {};
  return JSON.parse(JSON.stringify(clock));
}

function sanitizeSnapshotTimers(timers){
  if (!Array.isArray(timers)) return [];
  return JSON.parse(JSON.stringify(timers));
}

function sanitizeSnapshotFlags(flags){
  if (!flags || typeof flags !== 'object') return {};
  const out = { ...flags };
  return out;
}

function sanitizeSnapshotTeam(team){
  const base = ensure_team();
  return {
    stress: Number.isFinite(team?.stress) ? team.stress : base.stress,
    psi_heat: Number.isFinite(team?.psi_heat) ? team.psi_heat : base.psi_heat,
    status: typeof team?.status === 'string' ? team.status : base.status,
    cooldowns: { ...base.cooldowns, ...(team?.cooldowns || {}) }
  };
}

function sanitizeSnapshotInitiative(raw){
  const source = raw && typeof raw === 'object' ? raw : {};
  const order = Array.isArray(source.order)
    ? source.order
        .filter(entry => entry !== undefined && entry !== null)
        .map(entry => (typeof entry === 'object' ? clone_plain_object(entry) : entry))
    : [];
  const activeId = typeof source.active_id === 'string' && source.active_id.trim()
    ? source.active_id.trim()
    : null;
  return { order, active_id: activeId };
}

function sanitizeSnapshotHud(raw){
  const source = raw && typeof raw === 'object' ? raw : {};
  const timers = Array.isArray(source.timers)
    ? source.timers
        .map(normalize_hud_timer)
        .filter(entry => entry !== null)
        .map(entry => (typeof entry === 'object' ? clone_plain_object(entry) : entry))
    : [];
  return { timers };
}

function sanitizeSnapshotExfil(exfil){
  if (!exfil || typeof exfil !== 'object') return null;
  return {
    active: !!exfil.active,
    armed: !!exfil.armed,
    sweeps: Number.isFinite(exfil.sweeps) ? exfil.sweeps : 0,
    stress: Number.isFinite(exfil.stress) ? exfil.stress : 0,
    ttl_min: Number.isFinite(exfil.ttl_min) ? exfil.ttl_min : 0,
    ttl_sec: Number.isFinite(exfil.ttl_sec) ? exfil.ttl_sec : 0,
    anchor: exfil.anchor || null,
    alt_anchor: exfil.alt_anchor || null
  };
}

function suspend_snapshot(){
  ensure_campaign();
  ensure_mission();
  const team = ensure_team();
  const runtimeFlags = ensure_runtime_flags();
  const initiative = ensure_initiative();
  const hud = ensure_hud_state();
  if (state.arena?.active){
    throw new Error('Suspend blockiert während Arena-Lauf.');
  }
  if (state.exfil?.active){
    throw new Error('Suspend blockiert während laufender Exfiltration.');
  }
  if (state.roll?.open){
    throw new Error('Suspend nur zwischen Szenen oder nach einem Wurf-Ergebnis.');
  }
  const now = Date.now();
  const expiresAt = now + SUSPEND_TTL_MS;
  const file = suspendFilePath();
  const snapshot = {
    suspend_version: SUSPEND_VERSION,
    zr_version: ZR_VERSION,
    created_at: new Date(now).toISOString(),
    expires_at: new Date(expiresAt).toISOString(),
    volatile: true,
    campaign: {
      episode: state.campaign.episode,
      scene: state.scene?.index ?? state.campaign.scene,
      phase: state.campaign.phase,
      scene_total: state.scene?.total ?? 12
    },
    mission: {
      id: state.mission?.id ?? null,
      objective: state.mission?.objective ?? null,
      clock: sanitizeSnapshotClock(state.mission?.clock),
      timers: sanitizeSnapshotTimers(state.mission?.timers)
    },
    team: sanitizeSnapshotTeam(team),
    exfil: sanitizeSnapshotExfil(state.exfil),
    flags: sanitizeSnapshotFlags(runtimeFlags),
    initiative: sanitizeSnapshotInitiative(initiative),
    hud: sanitizeSnapshotHud(hud)
  };
  ensureSuspendStorage();
  fs.writeFileSync(file, JSON.stringify(snapshot, null, 2), 'utf8');
  runtimeFlags.suspend_active = true;
  state.suspend_snapshot = { created_at: now, expires_at: expiresAt, path: file };
  hud_toast('Session eingefroren · Ablauf <24h', 'HUD');
  return 'Suspend-Snapshot aktiv. Nutzt !resume, bevor 24h vergehen.';
}

function resume_snapshot(){
  ensure_campaign();
  ensure_mission();
  const runtimeFlags = ensure_runtime_flags();
  const file = suspendFilePath();
  if (!fs.existsSync(file)){
    runtimeFlags.suspend_active = false;
    state.suspend_snapshot = null;
    throw new Error('Kein Suspend-Snapshot gefunden. Bitte HQ-Save laden.');
  }
  const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
  const now = Date.now();
  const expiresAt = raw.expires_at ? Date.parse(raw.expires_at) : null;
  if (expiresAt && Number.isFinite(expiresAt) && now > expiresAt){
    fs.unlinkSync(file);
    runtimeFlags.suspend_active = false;
    state.suspend_snapshot = null;
    hud_toast('Suspend verworfen · HQ-Save nötig', 'HUD');
    throw new Error('Suspend-Fenster verstrichen. Bitte HQ-Save laden.');
  }
  const snapshotVersion = majorMinor(raw.zr_version);
  if (snapshotVersion && snapshotVersion !== majorMinor(ZR_VERSION)){
    throw new Error(`Suspend-Version inkompatibel (${raw.zr_version} ≠ ${ZR_VERSION}).`);
  }
  state.campaign.episode = raw.campaign?.episode ?? state.campaign.episode;
  state.campaign.phase = raw.campaign?.phase ?? state.campaign.phase;
  const sceneIndex = raw.campaign?.scene ?? state.scene?.index ?? state.campaign.scene;
  const sceneTotal = raw.campaign?.scene_total ?? state.scene?.total ?? 12;
  state.campaign.scene = sceneIndex;
  state.scene = { index: sceneIndex, foreshadows: state.scene?.foreshadows ?? 0, total: sceneTotal };
  const mission = ensure_mission();
  if (raw.mission){
    mission.id = raw.mission.id ?? mission.id ?? null;
    mission.objective = raw.mission.objective ?? mission.objective ?? null;
    mission.clock = sanitizeSnapshotClock(raw.mission.clock);
    mission.timers = sanitizeSnapshotTimers(raw.mission.timers);
  }
  if (raw.exfil){
    state.exfil = sanitizeSnapshotExfil(raw.exfil);
  }
  const team = ensure_team();
  if (raw.team){
    team.stress = Number.isFinite(raw.team.stress) ? raw.team.stress : team.stress;
    team.psi_heat = Number.isFinite(raw.team.psi_heat) ? raw.team.psi_heat : team.psi_heat;
    team.status = typeof raw.team.status === 'string' ? raw.team.status : team.status;
    team.cooldowns = { ...team.cooldowns, ...(raw.team.cooldowns || {}) };
  }
  const initiativeState = ensure_initiative();
  const restoredInitiative = sanitizeSnapshotInitiative(raw.initiative);
  initiativeState.order = restoredInitiative.order;
  initiativeState.active_id = restoredInitiative.active_id;
  const hudState = ensure_hud_state();
  const restoredHud = sanitizeSnapshotHud(raw.hud);
  hudState.timers = restoredHud.timers;
  const mergedFlags = sanitizeSnapshotFlags(raw.flags);
  Object.assign(runtimeFlags, mergedFlags);
  runtimeFlags.suspend_active = false;
  state.suspend_snapshot = null;
  fs.unlinkSync(file);
  state.roll = { open: false };
  const message = `Session fortgesetzt · Szene ${sceneIndex}/${sceneTotal}`;
  hud_toast(message, 'HUD');
  return `Suspend-Snapshot geladen. Szene ${sceneIndex}/${sceneTotal}.`;
}

function resolveSuspendPath(){
  return suspendFilePath();
}

function ensureArray(value){
  if (Array.isArray(value)) return value.filter(item => item !== undefined && item !== null && item !== '');
  if (value === undefined || value === null || value === '') return [];
  return [value];
}

function cloneLoadout(loadout){
  if (!loadout || typeof loadout !== 'object') return {};
  return JSON.parse(JSON.stringify(loadout));
}

function enforceProcBudget(loadout, limit, auditLog, label){
  if (!Number.isFinite(limit) || limit < 0) return loadout;
  let remaining = limit;
  for (const key of ARENA_PROC_KEYS){
    const items = ensureArray(loadout[key]);
    if (items.length === 0){
      loadout[key] = [];
      continue;
    }
    const kept = [];
    for (const item of items){
      if (remaining > 0){
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

function extractArtifactEntries(loadout){
  const entries = [];
  for (const key of ARENA_ARTIFACT_KEYS){
    const value = loadout[key];
    if (Array.isArray(value)){
      value.forEach((entry, index) => {
        if (entry){
          entries.push({ key, index, value: entry });
        }
      });
    } else if (value){
      entries.push({ key, index: null, value });
    }
  }
  for (const key of ARENA_PROC_KEYS){
    const arr = ensureArray(loadout[key]);
    arr.forEach((entry, index) => {
      if (typeof entry === 'string' && /artefakt|artifact/i.test(entry)){
        entries.push({ key, index, value: entry, derived: true });
      }
    });
  }
  return entries;
}

function enforceArtifactLimit(loadout, limit, auditLog, label){
  if (!Number.isFinite(limit) || limit < 0) limit = 0;
  const entries = extractArtifactEntries(loadout);
  let kept = 0;
  for (const entry of entries){
    if (kept < limit){
      kept += 1;
      continue;
    }
    auditLog.push(`${label}: Artefakt-Limit erreicht – '${entry.value}' entfernt`);
    if (entry.index === null){
      if (Array.isArray(loadout[entry.key])){
        loadout[entry.key] = [];
      } else {
        loadout[entry.key] = null;
      }
    } else if (Array.isArray(loadout[entry.key])){
      const arr = loadout[entry.key];
      if (entry.index >= 0 && entry.index < arr.length){
        arr.splice(entry.index, 1);
      }
    }
  }
  return loadout;
}

function enforceLoadoutBudget(loadout, limit, auditLog, label){
  if (!Number.isFinite(limit) || limit <= 0) return loadout;
  let remaining = limit;
  for (const key of ARENA_LOADOUT_KEYS){
    const items = ensureArray(loadout[key]);
    if (items.length === 0){
      loadout[key] = [];
      continue;
    }
    if (items.length <= remaining){
      loadout[key] = items;
      remaining -= items.length;
      continue;
    }
    const kept = items.slice(0, remaining);
    const removed = items.slice(remaining);
    removed.forEach(item => auditLog.push(`${label}: Loadout-Budget erreicht – '${item}' aus ${key} entfernt`));
    loadout[key] = kept;
    remaining = 0;
  }
  return loadout;
}

function resolveArenaTier(players = []){
  const highestLevel = players.reduce((lvl, entry) => {
    const raw = entry?.level ?? entry?.character?.level ?? 1;
    const level = Number(raw);
    return Math.max(lvl, Number.isFinite(level) ? level : 1);
  }, 1);
  return ARENA_TIER_RULES.find(rule => highestLevel >= rule.minLevel && highestLevel <= rule.maxLevel) || ARENA_TIER_RULES[0];
}

function applyArenaTierPolicy(players, tierRule){
  const audit = [];
  const sanitisedPlayers = players.map(entry => {
    const label = entry?.name || entry?.callsign || 'Agent';
    const clone = { ...entry };
    const loadout = cloneLoadout(entry?.loadout);
    enforceArtifactLimit(loadout, tierRule.artifactLimit, audit, label);
    enforceProcBudget(loadout, tierRule.procBudget, audit, label);
    enforceLoadoutBudget(loadout, tierRule.loadoutBudget, audit, label);
    clone.loadout = loadout;
    return clone;
  });
  return { tierRule, players: sanitisedPlayers, audit };
}

function nextArenaScenario(){
  const idx = arenaScenarioSerial % ARENA_SCENARIOS.length;
  const description = ARENA_SCENARIOS[idx];
  arenaScenarioSerial = (arenaScenarioSerial + 1) % ARENA_SCENARIOS.length;
  return { description };
}

function gatherArenaPlayers(){
  const character = ensure_character();
  const players = [];
  const baseFaction = character.faction || state.team?.faction || 'Projekt Phoenix';
  players.push({
    name: character.name || character.callsign || character.id || 'Agent',
    level: Number.isFinite(character.lvl) ? character.lvl : Number(character.level) || 1,
    faction: baseFaction,
    loadout: cloneLoadout(state.loadout || {})
  });
  const members = Array.isArray(state.team?.members) ? state.team.members : [];
  members.forEach((member, index) => {
    if (!member) return;
    const lvl = Number(member.lvl ?? member.level ?? character.lvl ?? 1);
    players.push({
      name: member.name || member.callsign || `Team-${index + 1}`,
      level: Number.isFinite(lvl) ? lvl : 1,
      faction: member.faction || baseFaction,
      loadout: cloneLoadout(member.loadout || {})
    });
  });
  return players;
}

function readArenaCurrency(){
  const economy = ensure_economy();
  const keys = ['credits', 'cu', 'balance', 'assets'];
  for (const key of keys){
    const value = Number(economy[key]);
    if (Number.isFinite(value)){
      return { key, value: Math.max(0, value) };
    }
  }
  if (!Number.isFinite(Number(economy.credits))){
    economy.credits = 0;
  }
  return { key: 'credits', value: 0 };
}

function writeArenaCurrency(key, value){
  const economy = ensure_economy();
  economy[key] = value;
  if (key !== 'credits' && economy.credits === undefined){
    economy.credits = value;
  }
}

function getArenaFee(currency = 0){
  let remaining = Math.max(0, currency);
  let fee = ARENA_BASE_FEE;
  for (const bracket of ARENA_FEE_BRACKETS){
    if (remaining <= 0) break;
    const taxable = Math.min(remaining, bracket.limit);
    fee += taxable * bracket.rate;
    remaining -= taxable;
  }
  return Math.floor(fee);
}

function arenaStart(options = {}){
  ensure_campaign();
  const arena = ensure_arena();
  if (arena.active){
    throw new Error('Arena bereits aktiv – beendet zuerst die laufende Serie.');
  }
  const { key, value } = readArenaCurrency();
  const fee = getArenaFee(value);
  if (value < fee){
    throw new Error('Arena-Gebühr kann nicht bezahlt werden. Credits prüfen.');
  }
  const players = gatherArenaPlayers();
  const tierRule = resolveArenaTier(players);
  const { players: sanitisedPlayers, audit } = applyArenaTierPolicy(players, tierRule);
  const parsedSize = Number.isFinite(options.teamSize) ? Math.floor(options.teamSize) : NaN;
  const teamSize = Number.isFinite(parsedSize) && parsedSize > 0 ? Math.min(Math.max(parsedSize, 1), 6) : 1;
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
  const pxLocked = arena.last_reward_episode !== null && arena.last_reward_episode === currentEpisode;
  const pxNote = pxLocked ? 'Px-Bonus dieser Episode bereits verbraucht' : 'Px-Bonus verfügbar';
  const baseMessage = `Arena initiiert · Tier ${tierRule.tier} · Gebühr ${fee} CU`;
  hud_toast(`${baseMessage} · ${pxNote}`, 'ARENA');
  if (audit.length){
    hud_toast(`Arena-Loadout angepasst: ${audit.length} Eingriffe.`, 'ARENA');
  }
  return `${baseMessage} · ${scenario.description} · ${pxNote}`;
}

function arenaScore(){
  const arena = ensure_arena();
  const pxLocked = arena.last_reward_episode !== null && arena.last_reward_episode === (state.campaign?.episode ?? null);
  const pxNote = pxLocked ? 'Px-Bonus bereits vergeben' : 'Px-Bonus offen';
  const scenario = arena.scenario?.description || 'n/a';
  return `Arena-Score ${arena.wins_player}:${arena.wins_opponent} · Tier ${arena.tier} · Team ${arena.team_size} · ${pxNote} · Szenario ${scenario}`;
}

function arenaExit(){
  const arena = ensure_arena();
  if (!arena.active){
    return 'Arena ist nicht aktiv.';
  }
  const episode = state.campaign?.episode ?? null;
  let pxGranted = false;
  if (arena.wins_player >= 2 && arena.wins_player > arena.wins_opponent){
    if (episode !== null && arena.last_reward_episode !== episode){
      incrementParadoxon(1);
      arena.last_reward_episode = episode;
      pxGranted = true;
    }
  }
  const messageParts = [`Arena Ende · Score ${arena.wins_player}:${arena.wins_opponent}`];
  if (arena.wins_player < 2 || arena.wins_player <= arena.wins_opponent){
    messageParts.push('Keine Px-Belohnung (Serie verloren)');
  } else if (pxGranted){
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
  if (typeof restoreMode === 'string' && restoreMode.trim()){
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

function arenaRegisterResult(outcome){
  const arena = ensure_arena();
  if (!arena.active){
    throw new Error('Arena ist nicht aktiv. Nutzt !arena start.');
  }
  const normalized = (outcome || '').toString().toLowerCase();
  if (normalized === 'win' || normalized === 'victory'){
    arena.wins_player += 1;
  } else if (['loss', 'lose', 'defeat'].includes(normalized)){
    arena.wins_opponent += 1;
  } else {
    throw new Error('Unbekanntes Arena-Ergebnis. Nutzt win oder loss.');
  }
  const status = `Arena-Serie ${arena.wins_player}:${arena.wins_opponent}`;
  let hint = '';
  if (arena.wins_player >= 2){
    hint = 'Serie gewonnen – nutzt !arena exit für den Abschluss.';
  } else if (arena.wins_opponent >= 2){
    hint = 'Serie verloren – ihr könnt die Arena mit !arena exit verlassen.';
  }
  const message = hint ? `${status} · ${hint}` : status;
  hud_toast(message, 'ARENA');
  return message;
}

function parseArenaStartArgs(tokens){
  let teamSize;
  let mode;
  for (let i = 0; i < tokens.length; i += 1){
    const token = tokens[i];
    if (token === 'team' && Number.isFinite(Number(tokens[i + 1]))){
      teamSize = parseInt(tokens[i + 1], 10);
      i += 1;
      continue;
    }
    if (token === 'mode' && typeof tokens[i + 1] === 'string'){
      mode = tokens[i + 1];
      i += 1;
    }
  }
  return { teamSize, mode };
}

function handleArenaCommand(cmd){
  const tokens = cmd.split(/\s+/).map(t => t.trim()).filter(Boolean);
  const sub = tokens[1] || 'status';
  if (sub === 'start'){
    const options = parseArenaStartArgs(tokens.slice(2));
    return arenaStart(options);
  }
  if (sub === 'score' || sub === 'status'){
    return arenaScore();
  }
  if (sub === 'exit' || sub === 'leave'){
    return arenaExit();
  }
  if (sub === 'result' && tokens[2]){
    return arenaRegisterResult(tokens[2]);
  }
  if (sub === 'win'){
    return arenaRegisterResult('win');
  }
  if (sub === 'loss' || sub === 'lose'){
    return arenaRegisterResult('loss');
  }
  return 'Arena-Befehle: !arena start [team <n>] [mode <name>] · !arena result win|loss · !arena score · !arena exit';
}

function rankIndex(rank){
  const idx = RANK_ORDER.indexOf(rank);
  return idx === -1 ? 0 : idx;
}

function chrono_research_level(){
  ensure_campaign();
  const char = ensure_character();
  const charResearch = Number.isFinite(char.research_level) ? char.research_level : 0;
  const campaignResearch = Number.isFinite(state.campaign.research_level) ? state.campaign.research_level : 0;
  return Math.max(charResearch, campaignResearch);
}

function hashString(input){
  let h = 0;
  for (let i = 0; i < input.length; i += 1){
    h = Math.imul(31, h) + input.charCodeAt(i) | 0;
  }
  return h >>> 0;
}

function seededRandom(seed){
  let x = seed | 0;
  return function rng(){
    x = (x + 0x6D2B79F5) | 0;
    let t = Math.imul(x ^ x >>> 15, 1 | x);
    t ^= t + Math.imul(t ^ t >>> 7, 61 | t);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

function shuffleWithRng(items, rng){
  const arr = [...items];
  for (let i = arr.length - 1; i > 0; i -= 1){
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function chronopolis_reset(reason){
  const chrono = ensure_chronopolis();
  chrono.stock = [];
  chrono.day = null;
  chrono.cache_key = null;
  chrono.reset_serial = (chrono.reset_serial || 0) + 1;
  chrono.last_reset_reason = reason;
  chrono.last_reset_at = new Date().toISOString();
}

function rollChronopolisStock(){
  const chrono = ensure_chronopolis();
  const dayStamp = new Date().toISOString().slice(0, 10);
  const cacheKey = `${dayStamp}#${chrono.reset_serial || 0}`;
  if (chrono.cache_key === cacheKey && chrono.stock.length){
    return chrono;
  }
  const rng = seededRandom(hashString(cacheKey));
  const categories = Object.keys(CHRONO_CATEGORY_LIMITS);
  const picked = [];
  categories.forEach((category) => {
    const options = CHRONO_CATALOG.filter((item) => item.category === category);
    const limit = CHRONO_CATEGORY_LIMITS[category] || options.length;
    const pool = shuffleWithRng(options, rng).slice(0, Math.min(limit, options.length));
    picked.push(...pool);
  });
  chrono.stock = picked;
  chrono.day = dayStamp;
  chrono.cache_key = cacheKey;
  return chrono;
}

function chronopolisStockReport(){
  const chrono = rollChronopolisStock();
  const char = ensure_character();
  const research = chrono_research_level();
  const rankIdx = rankIndex(char.rank || 'Recruit');
  const lines = [];
  lines.push(`Chronopolis · Tagesangebot ${chrono.day}`);
  const grouped = chrono.stock.reduce((acc, item) => {
    acc[item.category] ||= [];
    acc[item.category].push(item);
    return acc;
  }, {});
  Object.keys(grouped).sort().forEach((category) => {
    lines.push(`— ${category} —`);
    grouped[category].forEach((item) => {
      const needRank = rankIndex(item.minRank || 'Recruit');
      const needResearch = Number.isFinite(item.minResearch) ? item.minResearch : 0;
      const rankOk = rankIdx >= needRank;
      const researchOk = research >= needResearch;
      const locks = [];
      if (!rankOk) locks.push(`Rank ${item.minRank}`);
      if (!researchOk) locks.push(`Research ${needResearch}`);
      if (locks.length){
        lines.push(`🔒 ${item.name} · ${item.price} CU (${locks.join(' · ')})`);
      } else {
        lines.push(`${item.name} · ${item.price} CU`);
      }
    });
  });
  return lines.join('\n');
}

function chronopolisTickStatus(){
  ensure_campaign();
  const chrono = ensure_chronopolis();
  const modulo = state.campaign.chronopolis_tick_modulo;
  const progress = state.campaign.chronopolis_missions_since_reset;
  const reason = chrono.last_reset_reason || 'init';
  const when = chrono.last_reset_at || '–';
  const missionInfo = modulo > 0 ? `alle ${modulo} Missionen` : 'deaktiviert';
  return `Chronopolis-Tick · Episoden → immer · Missionen → ${missionInfo} · Fortschritt ${progress}/${modulo || '–'} · Letzter Reset ${reason} @ ${when}`;
}

function chronopolisSetTickModulo(modulo){
  ensure_campaign();
  const value = Math.max(0, Math.floor(modulo));
  state.campaign.chronopolis_tick_modulo = value;
  state.campaign.chronopolis_missions_since_reset = 0;
  return value
    ? `Chronopolis-Tick nach ${value} Missionen aktiviert. Fortschritt zurückgesetzt.`
    : 'Chronopolis-Tick (Missionen) deaktiviert. Fortschritt zurückgesetzt.';
}

function chronopolisProgressAfterMission(summary){
  ensure_campaign();
  const reason = summary && summary.episode_completed ? 'episode' : null;
  if (reason){
    state.campaign.chronopolis_missions_since_reset = 0;
    chronopolis_reset('episode');
    return reason;
  }
  const modulo = state.campaign.chronopolis_tick_modulo;
  if (modulo > 0){
    state.campaign.chronopolis_missions_since_reset = (state.campaign.chronopolis_missions_since_reset || 0) + 1;
    if (state.campaign.chronopolis_missions_since_reset >= modulo){
      state.campaign.chronopolis_missions_since_reset = 0;
      chronopolis_reset('mission-cycle');
      return 'mission-cycle';
    }
  }
  return null;
}

function render_shop_tiers(level=1, faction_rep=0, rift_blueprints=[]){
  const t1 = level >= 1;
  const t2 = level >= 6;
  const count = Array.isArray(rift_blueprints) ? rift_blueprints.length : (rift_blueprints ? 1 : 0);
  const hasBlueprint = count > 0;
  const t3 = level >= 11 && faction_rep >= 3 && hasBlueprint;
  const bp = count;
  return `Shop-Tiers: T1:${t1 ? 'true' : 'false'} T2:${t2 ? 'true' : 'false'} T3:${t3 ? 'true' : 'false'} · BP:${bp}`;
}

function ttl_fmt(min=0, sec=0){
  const mm = String(Math.max(0, min)).padStart(2, '0');
  const ss = String(Math.max(0, sec)).padStart(2, '0');
  return `${mm}:${ss}`;
}

function seeded(seed){
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

function roll_fr(bias = 'normal', seed = null){
  const r = seed != null ? seeded(seed) : Math.random();
  let pR = 0.60, pB = 0.25;
  if (bias === 'hard'){ pR = 0.45; pB = 0.30; }
  if (bias === 'easy'){ pR = 0.75; pB = 0.20; }
  return r < pR ? 'ruhig' : (r < pR + pB ? 'beobachter' : 'aktiv');
}

function jam_now(on = true){
  state.comms.jammed = !!on;
}

function StartMission(){
  state.phase = 'core';
  state.comms = { jammed: false, relays: 0, rangeMod: 1.0 };
  state.exfil = { sweeps: 0, stress: 0, ttl_min: 8, ttl_sec: 0, active: false, armed: false, anchor: null, alt_anchor: null };
  const hudLog = ensure_logs();
  hudLog.length = 0;
  const foreshadowLog = foreshadow_entries();
  foreshadowLog.length = 0;
  ensure_character();
  ensure_team();
  const mission = ensure_mission();
  mission.clock = mission.clock && typeof mission.clock === 'object' ? mission.clock : {};
  mission.timers = Array.isArray(mission.timers) ? mission.timers : [];
  state.fr_intervention = roll_fr(state.campaign?.fr_bias || 'normal');
  state.scene = { index: 0, foreshadows: 0, total: 12 };
}

function scene_overlay(scene){
  const s = scene || state.scene;
  const ep = state.campaign?.episode ?? 0;
  const ms = state.campaign?.mission ?? 0;
  const sc = s.index ?? 0;
  const total = state.scene?.total ?? 12;
  const ui = ensure_ui();
  const mode = ui.gm_style;
  const obj = state.campaign?.objective ?? '?';
  let h = `EP ${ep} · MS ${ms} · SC ${sc}/${total} · MODE ${mode}`;
  if (suggest_mode_enabled()){
    h += ' · SUG';
  }
  h += ` · Objective: ${obj}`;
  if (state.exfil){
    state.exfil.ttl_min = Math.max(0, state.exfil.ttl_min);
    state.exfil.ttl_sec = Math.max(0, state.exfil.ttl_sec);
    const ttl = ttl_fmt(state.exfil.ttl_min, state.exfil.ttl_sec);
    const ancr = state.exfil.anchor || '?';
    h += ` · ANCR ${ancr} · RW ${ttl}`;
    if (state.exfil.alt_anchor) h += ` · ALT ${state.exfil.alt_anchor}`;
    if (state.exfil.sweeps) h += ` · Sweeps:${state.exfil.sweeps}`;
    if (state.exfil.stress) h += ` · Stress ${state.exfil.stress}`;
  }
  const fsCount = sync_foreshadow_progress();
  const fsRequired = foreshadow_requirement();
  if (fsRequired > 0){
    h += ` · FS ${fsCount}/${fsRequired}`;
  } else {
    h += ` · FS ${fsCount}`;
  }
    const px = state.campaign?.px ?? state.campaign?.paradoxon_index ?? 0;
    const sys = state.character?.attributes?.SYS_max ?? 0;
    const lvl = state.character?.lvl ?? '-';
    h += ` · Px ${px} · SYS ${sys} · Lvl ${lvl}`;
    if (s.index === 0 && state.fr_intervention){
      h += ` · FR:${state.fr_intervention}`;
    }
    if (!self_reflection_enabled()){
      h += ' · SF-OFF';
    }
    const tkCooldown = get_cooldown('tk_melee');
    if (tkCooldown > 0){
      h += ` · TK🌀 ${tkCooldown}`;
    }
  return h;
}

function comms_check(device, range){
  const okDev = ['comlink', 'cable', 'relay', 'jammer_override'].includes(device);
  const jam = !!state.comms?.jammed;
  const okRng = (range * (state.comms?.rangeMod ?? 1)) > 0;
  const ok = okDev && okRng && (
    !jam || device === 'cable' || device === 'jammer_override' || device === 'relay'
  );
  return ok;
}

function kodex_link_state(ctx){
  const c = ctx || state;
  // phase may be 'core', 'transfer', 'rift', ...
  if (c.location === 'HQ' || c.phase === 'transfer') return 'uplink';
  const dev = c.comms?.device;
  const rng = c.comms?.range_m;
  const jam = c.comms?.jammed;
  const inBubble = dev === 'comlink' && typeof rng === 'number' && rng <= 2000 && !jam;
  return inBubble ? 'field_online' : 'field_offline';
}

function offline_help(trigger='auto'){
  ensure_logs();
  const flags = state.logs.flags;
  const now = Date.now();
  const last = typeof flags.offline_help_last === 'string' ? Date.parse(flags.offline_help_last) : NaN;
  const shouldToast = !Number.isFinite(last) || (now - last) > OFFLINE_HELP_MIN_INTERVAL_MS;
  if (shouldToast){
    hud_toast(OFFLINE_HELP_TOAST, 'OFFLINE');
  }
  flags.offline_help_last = new Date(now).toISOString();
  flags.offline_help_count = (flags.offline_help_count || 0) + 1;
  const entry = offline_audit(trigger, { count: flags.offline_help_count });
  const summary = format_offline_report(entry, flags.offline_help_count);
  const guide = OFFLINE_HELP_GUIDE.join('\n');
  return summary ? `${guide}\n\n${summary}` : guide;
}

function require_uplink(ctx, action){
  const st = kodex_link_state(ctx);
  if (st === 'uplink' || st === 'field_online') return true;
  offline_help('auto');
  throw new Error(
    'Kodex-Uplink getrennt – Mission läuft weiter mit HUD-Lokaldaten. !offline zeigt das Feldprotokoll bis zum HQ-Re-Sync.'
  );
}

function must_comms(o){
  if (!comms_check(o.device, o.range)){
    throw new Error(
      'CommsCheck failed: require valid device/range or relay/jammer override. ' +
      'Tipp: Terminal suchen / Comlink koppeln / Kabel/Relay nutzen / Jammer-Override aktivieren; Reichweite anpassen. ' +
      'Mission läuft weiter mit HUD-Lokaldaten – !offline listet das Feldprotokoll.'
    );
  }
}

function radio_tx(o){
  const ctx = { ...state, comms: { ...state.comms, device: o.device, range_m: o.range } };
  require_uplink(ctx, 'radio_tx');
  must_comms(o);
  return 'tx';
}

function radio_rx(o){
  const ctx = { ...state, comms: { ...state.comms, device: o.device, range_m: o.range } };
  require_uplink(ctx, 'radio_rx');
  must_comms(o);
  return 'rx';
}

function assert_foreshadow(n=2){
  const ui = ensure_ui();
  if (ui.gm_style !== 'precision') return;
  const c = state.scene.foreshadows || 0;
  if (c < n) console.log(`Foreshadow low: ${c}/${n}`);
}

function clone_plain_object(obj){
  if (!obj || typeof obj !== 'object') return {};
  return JSON.parse(JSON.stringify(obj));
}

function prepare_save_campaign(campaign){
  const base = clone_plain_object(campaign);
  if (!Number.isFinite(base.paradoxon_index)){
    const px = Number(base.paradoxon_index);
    base.paradoxon_index = Number.isFinite(px) ? px : 0;
  }
  const pxValue = Number.isFinite(base.px)
    ? base.px
    : Number.isFinite(base.paradoxon_index)
    ? base.paradoxon_index
    : 0;
  base.px = Number.isFinite(pxValue) ? pxValue : 0;
  base.compliance_shown_today = !!base.compliance_shown_today;
  return base;
}

function prepare_save_economy(economy){
  const base = clone_plain_object(economy);
  if (!Number.isFinite(base.cu)){
    base.cu = 0;
  }
  base.cu = Math.round(base.cu);
  const wallets = {};
  if (base.wallets && typeof base.wallets === 'object' && !Array.isArray(base.wallets)){
    for (const [key, value] of Object.entries(base.wallets)){
      const id = normalize_wallet_id(key);
      if (!id) continue;
      const record = normalize_wallet_record(value);
      if (!record) continue;
      wallets[id] = {
        balance: record.balance,
        ...(record.name ? { name: record.name } : {})
      };
    }
  }
  base.wallets = wallets;
  return base;
}

function prepare_save_logs(logs){
  const base = clone_plain_object(logs);
  if (!Array.isArray(base.hud)){
    base.hud = [];
  }
  if (Array.isArray(base.foreshadow)){
    const deduped = [];
    const byToken = new Map();
    for (const entry of base.foreshadow){
      if (!entry || typeof entry !== 'object' || typeof entry.token !== 'string') continue;
      const rawToken = entry.token.trim();
      if (!rawToken) continue;
      const token = rawToken.toLowerCase();
      const tag = typeof entry.tag === 'string' && entry.tag.trim() ? entry.tag.trim() : 'Foreshadow';
      const message = typeof entry.message === 'string' ? entry.message.trim() : '';
      const sceneIndex = Number(entry.scene);
      const scene = Number.isFinite(sceneIndex) ? sceneIndex : null;
      const firstSeen = typeof entry.first_seen === 'string' ? entry.first_seen : null;
      const lastSeen = typeof entry.last_seen === 'string' ? entry.last_seen : null;
      if (byToken.has(token)){
        const existing = byToken.get(token);
        if (!existing.message && message){
          existing.message = message;
        }
        if (!existing.tag && tag){
          existing.tag = tag;
        }
        if (!Number.isFinite(existing.scene) && Number.isFinite(scene)){
          existing.scene = scene;
        }
        if (!existing.last_seen && lastSeen){
          existing.last_seen = lastSeen;
        }
        continue;
      }
      const record = {
        token,
        tag,
        message,
        scene,
        first_seen: firstSeen,
        last_seen: lastSeen || firstSeen
      };
      deduped.push(record);
      byToken.set(token, record);
    }
    base.foreshadow = deduped;
  } else {
    base.foreshadow = [];
  }
  if (!Array.isArray(base.artifact_log)){
    base.artifact_log = [];
  }
  if (!Array.isArray(base.kodex)){
    base.kodex = [];
  }
  if (Array.isArray(base.market)){
    base.market = sanitize_market_entries(base.market);
  } else {
    base.market = [];
  }
  if (Array.isArray(base.offline)){
    base.offline = sanitize_offline_entries(base.offline);
  } else {
    base.offline = [];
  }
  if (Array.isArray(base.fr_interventions)){
    base.fr_interventions = sanitize_intervention_entries(base.fr_interventions).map(entry => ({ ...entry }));
  } else {
    base.fr_interventions = [];
  }
  if (Array.isArray(base.alias_trace)){
    base.alias_trace = sanitize_alias_entries(base.alias_trace);
  } else {
    base.alias_trace = [];
  }
  if (Array.isArray(base.squad_radio)){
    base.squad_radio = sanitize_radio_entries(base.squad_radio);
  } else {
    base.squad_radio = [];
  }
  if (!base.flags || typeof base.flags !== 'object'){
    base.flags = {};
  }
  if (!base.flags.runtime_version){
    base.flags.runtime_version = ZR_VERSION;
  }
  base.flags.compliance_shown_today = !!base.flags.compliance_shown_today;
  base.flags.chronopolis_warn_seen = !!base.flags.chronopolis_warn_seen;
  if (typeof base.flags.offline_help_last !== 'string'){
    base.flags.offline_help_last = null;
  }
  const offlineCount = Number(base.flags.offline_help_count);
  base.flags.offline_help_count = Number.isFinite(offlineCount) && offlineCount > 0
    ? Math.floor(offlineCount)
    : 0;
  return base;
}

function prepare_save_arc_dashboard(dashboard){
  const base = dashboard && typeof dashboard === 'object' && !Array.isArray(dashboard)
    ? clone_plain_object(dashboard)
    : {};
  base.offene_seeds = Array.isArray(base.offene_seeds)
    ? base.offene_seeds.map(entry => clone_plain_object(entry))
    : [];
  if (!base.fraktionen || typeof base.fraktionen !== 'object' || Array.isArray(base.fraktionen)){
    base.fraktionen = {};
  } else {
    const normalized = {};
    for (const [key, value] of Object.entries(base.fraktionen)){
      const record = value && typeof value === 'object' ? clone_plain_object(value) : {};
      if (Array.isArray(record.interventions)){
        record.interventions = sanitize_intervention_entries(record.interventions).map(entry => ({ ...entry }));
      } else {
        record.interventions = [];
      }
      if (record.last_intervention){
        const last = normalize_intervention_entry(record.last_intervention, record.last_intervention?.timestamp, { fillDefaults: false });
        record.last_intervention = last || null;
      } else {
        record.last_intervention = null;
      }
      normalized[key] = record;
    }
    base.fraktionen = normalized;
  }
  base.fragen = Array.isArray(base.fragen)
    ? base.fragen.map(entry => (
        entry && typeof entry === 'object' ? clone_plain_object(entry) : entry
      ))
    : [];
  return base;
}

function prepare_save_ui(ui){
  const base = clone_plain_object(ui);
  base.gm_style = typeof base.gm_style === 'string' ? base.gm_style : 'verbose';
  base.intro_seen = !!base.intro_seen;
  base.suggest_mode = !!base.suggest_mode;
  return base;
}

function prepare_save_character(character){
  const base = clone_plain_object(character);
  if (!base || typeof base !== 'object'){
    throw new Error('SaveGuard: Charakterdaten fehlen.');
  }
  if (!base.id){
    throw new Error('SaveGuard: Feld character.id fehlt.');
  }
  base.stress = Number.isFinite(base.stress) ? base.stress : 0;
  base.psi_heat = Number.isFinite(base.psi_heat) ? base.psi_heat : 0;
  if (!base.cooldowns || typeof base.cooldowns !== 'object'){
    base.cooldowns = {};
  }
  const attrs = clone_plain_object(base.attributes);
  if (!Number.isFinite(attrs.SYS_max)){
    const sysMax = Number(attrs.SYS_max);
    attrs.SYS_max = Number.isFinite(sysMax) ? sysMax : 0;
  }
  if (!Number.isFinite(attrs.SYS_used)){
    const sysUsed = Number(attrs.SYS_used);
    attrs.SYS_used = Number.isFinite(sysUsed) ? sysUsed : attrs.SYS_max;
  }
  base.attributes = attrs;
  return base;
}

function prepare_save_team(team){
  const base = clone_plain_object(team);
  if (Array.isArray(team?.members)){
    base.members = team.members.map(member => clone_plain_object(member));
  } else if (!Array.isArray(base.members)){
    base.members = [];
  }
  return base;
}

function prepare_save_loadout(loadout){
  return clone_plain_object(loadout);
}

function prepare_save_party(party, team){
  const sourceParty = party && typeof party === 'object' ? party : {};
  const base = clone_plain_object(sourceParty);
  const fallback = Array.isArray(base.characters) && base.characters.length
    ? base.characters
    : Array.isArray(team?.members)
    ? team.members
    : [];
  base.characters = fallback.map(member => clone_plain_object(member));
  return base;
}

function assert_save_field(payload, path){
  let current = payload;
  for (const segment of path){
    if (current == null || !(segment in current)){
      throw new Error(`SaveGuard: Feld ${path.join('.')} fehlt.`);
    }
    current = current[segment];
  }
  if (current === undefined || current === null){
    throw new Error(`SaveGuard: Feld ${path.join('.')} fehlt.`);
  }
  return current;
}

const SAVE_REQUIRED_PATHS = [
  ['character', 'id'],
  ['character', 'cooldowns'],
  ['character', 'attributes', 'SYS_max'],
  ['character', 'attributes', 'SYS_used'],
  ['character', 'stress'],
  ['character', 'psi_heat'],
  ['campaign', 'px'],
  ['economy'],
  ['logs'],
  ['logs', 'artifact_log'],
  ['logs', 'market'],
  ['logs', 'offline'],
  ['logs', 'kodex'],
  ['logs', 'alias_trace'],
  ['logs', 'squad_radio'],
  ['ui']
];

function enforce_required_save_fields(payload){
  for (const path of SAVE_REQUIRED_PATHS){
    assert_save_field(payload, path);
  }
}

function select_state_for_save(s){
  const payload = {
    save_version: 6,
    zr_version: ZR_VERSION,
    location: s.location,
    phase: s.phase,
    campaign: prepare_save_campaign(s.campaign),
    character: prepare_save_character(s.character),
    team: prepare_save_team(s.team),
    party: prepare_save_party(s.party, s.team),
    loadout: prepare_save_loadout(s.loadout),
    economy: prepare_save_economy(s.economy),
    logs: prepare_save_logs(s.logs),
    ui: prepare_save_ui(s.ui),
    arc_dashboard: prepare_save_arc_dashboard(s.arc_dashboard)
  };
  enforce_required_save_fields(payload);
  return payload;
}

function save_deep(s=state){
  if (s?.arena?.active){
    throw new Error('SaveGuard: Arena aktiv – HQ-Save gesperrt.');
  }
  if (s.location !== 'HQ') throw new Error('Save denied: HQ-only.');
  const c = s.character || {};
  const a = c.attributes || {};
  if (c.stress !== 0) throw new Error('SaveGuard: stress > 0.');
  if ((c.psi_heat ?? 0) !== 0) throw new Error('SaveGuard: Psi-Heat > 0.');
  if (a.SYS_used > a.SYS_max) throw new Error('SaveGuard: SYS overflow.');
  const payload = select_state_for_save(s);
  return JSON.stringify(payload);
}

function roster_entry_key(entry, fallbackIndex){
  const candidates = [
    entry?.id,
    entry?.character?.id,
    entry?.callsign,
    entry?.character?.callsign,
    entry?.name,
    entry?.character?.name
  ];
  for (const candidate of candidates){
    if (candidate === undefined || candidate === null) continue;
    const value = String(candidate).trim();
    if (value){
      return value.toLowerCase();
    }
  }
  return `idx:${fallbackIndex}`;
}

function normalize_party_roster(data){
  if (!data || typeof data !== 'object') return;
  const team = data.team && typeof data.team === 'object' ? data.team : (data.team = {});
  const party = data.party && typeof data.party === 'object' ? data.party : (data.party = {});
  const group = data.group && typeof data.group === 'object' ? data.group : undefined;
  const candidateArrays = [];
  const pushArray = arr => {
    if (Array.isArray(arr) && arr.length){
      candidateArrays.push(arr);
    }
  };
  pushArray(party.characters);
  pushArray(team.members);
  pushArray(team.roster);
  pushArray(team.characters);
  pushArray(party.members);
  if (group){
    pushArray(group.characters);
    pushArray(group.members);
  }
  pushArray(data.npc_team);
  pushArray(data.npcs);
  pushArray(data.roster);
  const seen = new Set();
  const canonical = [];
  let fallbackIndex = 0;
  const addEntry = (entry) => {
    if (!entry || typeof entry !== 'object') return;
    const clone = clone_plain_object(entry);
    const key = roster_entry_key(clone, fallbackIndex);
    fallbackIndex += 1;
    if (seen.has(key)) return;
    seen.add(key);
    canonical.push(clone);
  };
  candidateArrays.forEach(arr => arr.forEach(addEntry));
  party.characters = canonical.map(entry => clone_plain_object(entry));
  data.party = { ...party, characters: party.characters };
  team.members = party.characters.map(entry => clone_plain_object(entry));
  if (Array.isArray(team.roster)){
    team.roster = team.members.map(entry => clone_plain_object(entry));
  }
  if (Array.isArray(team.characters)){
    team.characters = team.members.map(entry => clone_plain_object(entry));
  }
  if (group){
    group.characters = party.characters.map(entry => clone_plain_object(entry));
    if (Array.isArray(group.members)){
      group.members = party.characters.map(entry => clone_plain_object(entry));
    }
  }
}

function migrate_save(data){
  if (!data.save_version) data.save_version = 1;
  if (data.save_version === 1){
    data.campaign ||= {};
    data.save_version = 2;
  }
  if (data.save_version === 2){
    data.ui ||= { gm_style: 'verbose' };
    data.save_version = 3;
  }
  if (data.save_version === 3){
    data.phase ||= 'core';
    data.save_version = 4;
  }
  if (data.save_version === 4){
    const character = data.character ||= {};
    const carryHeat = character.psi_heat ?? character.heat ?? 0;
    if (typeof carryHeat !== 'number' || !Number.isFinite(carryHeat)){
      character.psi_heat = 0;
    } else {
      character.psi_heat = carryHeat;
    }
    if (character.psi_heat_max === undefined && character.heat_max !== undefined){
      character.psi_heat_max = character.heat_max;
    }
    delete character.heat;
    delete character.heat_max;
    data.save_version = 5;
  }
  if (data.save_version === 5){
    data.ui ||= { gm_style: 'verbose' };
    data.ui.intro_seen = !!data.ui.intro_seen;
    data.save_version = 6;
  }
  normalize_party_roster(data);
  data.campaign = prepare_save_campaign(data.campaign);
  data.economy = prepare_save_economy(data.economy);
  data.logs = prepare_save_logs(data.logs);
  data.arc_dashboard = prepare_save_arc_dashboard(data.arc_dashboard);
  data.initiative = sanitizeSnapshotInitiative(data.initiative);
  data.hud = sanitizeSnapshotHud(data.hud);
  if (data.campaign && typeof data.campaign === 'object'){
    const shown = !!data.logs?.flags?.compliance_shown_today;
    data.campaign.compliance_shown_today = shown || !!data.campaign.compliance_shown_today;
  }
  if (data.logs && data.logs.flags){
    data.logs.flags.compliance_shown_today = !!data.logs.flags.compliance_shown_today;
    if (typeof data.logs.flags.chronopolis_warn_seen !== 'boolean'){
      data.logs.flags.chronopolis_warn_seen = false;
    } else {
      data.logs.flags.chronopolis_warn_seen = !!data.logs.flags.chronopolis_warn_seen;
    }
  }
  data.ui = prepare_save_ui(data.ui);
  return data;
}

function hydrate_state(data){
  state.location = data.location || 'HQ';
  state.phase = data.phase || 'core';
  state.campaign = data.campaign || {};
  state.character = data.character || {};
  ensure_character();
  const legacyHeat = state.character.psi_heat ?? state.character.heat ?? 0;
  state.character.psi_heat = Number.isFinite(legacyHeat) ? legacyHeat : 0;
  delete state.character.heat;
  if (state.character.psi_heat_max === undefined && state.character.heat_max !== undefined){
    state.character.psi_heat_max = state.character.heat_max;
  }
  delete state.character.heat_max;
  state.team = data.team || {};
  state.loadout = data.loadout || {};
  state.economy = data.economy || {};
  state.logs = data.logs || {};
  state.arc_dashboard = data.arc_dashboard || {};
  state.initiative = data.initiative && typeof data.initiative === 'object'
    ? JSON.parse(JSON.stringify(data.initiative))
    : {};
  state.hud = data.hud && typeof data.hud === 'object'
    ? JSON.parse(JSON.stringify(data.hud))
    : {};
  ensure_economy();
  ensure_logs();
  sync_foreshadow_progress();
  ensure_arc_dashboard();
  ensure_initiative();
  ensure_hud_state();
  state.flags = data.flags && typeof data.flags === 'object' ? JSON.parse(JSON.stringify(data.flags)) : { runtime: {} };
  ensure_runtime_flags();
  state.roll = { open: false };
  state.arena = data.arena && typeof data.arena === 'object' ? { ...data.arena } : {};
  ensure_arena();
  state.ui = {
    gm_style: data.ui?.gm_style || 'verbose',
    intro_seen: !!(data.ui?.intro_seen),
    suggest_mode: !!(data.ui?.suggest_mode)
  };
  ensure_ui();
  state.party = data.party && typeof data.party === 'object' ? JSON.parse(JSON.stringify(data.party)) : {};
  const party = ensure_party();
  const roster = Array.isArray(party.characters) ? party.characters.map(entry => clone_plain_object(entry)) : [];
  const team = ensure_team();
  team.members = roster.map(entry => clone_plain_object(entry));
  if (Array.isArray(team.roster)){
    team.roster = roster.map(entry => clone_plain_object(entry));
  }
  reset_mission_state();
  ensure_campaign();
  state.suspend_snapshot = null;
}

function normalize_save_v6(data){
  if (!data || typeof data !== 'object') return data;
  const normalized = data;
  const ensureObject = (value) => (value && typeof value === 'object' && !Array.isArray(value) ? value : {});
  normalized.character = ensureObject(normalized.character);
  const character = normalized.character;
  const assignString = (targetKey, ...sourceKeys) => {
    if (typeof character[targetKey] === 'string' && character[targetKey].trim()){
      sourceKeys.forEach((key) => {
        if (key in normalized) delete normalized[key];
      });
      return;
    }
    const candidates = sourceKeys.map((key) => normalized[key]);
    candidates.push(character[targetKey]);
    const value = pickString(...candidates);
    if (value){
      character[targetKey] = value;
    }
    sourceKeys.forEach((key) => {
      if (key in normalized) delete normalized[key];
    });
  };
  const assignNumber = (targetKey, ...sourceKeys) => {
    if (Number.isFinite(character[targetKey])){
      sourceKeys.forEach((key) => {
        if (key in normalized) delete normalized[key];
      });
      return;
    }
    for (const key of sourceKeys){
      if (!(key in normalized)) continue;
      const candidate = asNumber(normalized[key]);
      if (candidate !== null){
        character[targetKey] = candidate;
        break;
      }
    }
    sourceKeys.forEach((key) => {
      if (key in normalized) delete normalized[key];
    });
  };
  assignString('id', 'id', 'character_id');
  assignString('name', 'name');
  assignString('callsign', 'callsign');
  assignString('rank', 'rank');
  assignNumber('lvl', 'lvl', 'level');
  assignNumber('xp', 'xp');
  assignNumber('stress', 'stress');
  assignNumber('psi_heat', 'psi_heat');
  assignNumber('psi_heat_max', 'psi_heat_max', 'psi_heat_cap');
  if (typeof character.self_reflection !== 'boolean' && 'self_reflection' in normalized){
    character.self_reflection = !!normalized.self_reflection;
    delete normalized.self_reflection;
  }
  const ensurePlainObject = (value) => (value && typeof value === 'object' && !Array.isArray(value) ? value : {});
  if (!character.cooldowns || typeof character.cooldowns !== 'object' || Array.isArray(character.cooldowns)){
    character.cooldowns = ensurePlainObject(normalized.cooldowns);
    if (!character.cooldowns || typeof character.cooldowns !== 'object' || Array.isArray(character.cooldowns)){
      character.cooldowns = {};
    }
  } else if (normalized.cooldowns && typeof normalized.cooldowns === 'object' && !Array.isArray(normalized.cooldowns)){
    const source = normalized.cooldowns;
    for (const [key, value] of Object.entries(source)){
      if (!(key in character.cooldowns)){
        character.cooldowns[key] = value;
      }
    }
  }
  if ('cooldowns' in normalized){
    delete normalized.cooldowns;
  }
  const attributes = ensurePlainObject(character.attributes);
  const assignAttributeNumber = (targetKey, ...sourceKeys) => {
    if (Number.isFinite(attributes[targetKey])){
      sourceKeys.forEach((key) => {
        if (key in normalized) delete normalized[key];
      });
      return;
    }
    for (const key of sourceKeys){
      if (!(key in normalized)) continue;
      const candidate = asNumber(normalized[key]);
      if (candidate !== null){
        attributes[targetKey] = candidate;
        break;
      }
    }
    sourceKeys.forEach((key) => {
      if (key in normalized) delete normalized[key];
    });
  };
  if (normalized.attributes && typeof normalized.attributes === 'object' && !Array.isArray(normalized.attributes)){
    for (const [key, value] of Object.entries(normalized.attributes)){
      if (!(key in attributes)){
        attributes[key] = value;
      }
    }
    delete normalized.attributes;
  }
  assignAttributeNumber('SYS_max', 'sys', 'sys_max');
  assignAttributeNumber('SYS_used', 'sys_used');
  if (character.attributes && typeof character.attributes === 'object' && !Array.isArray(character.attributes)){
    for (const [key, value] of Object.entries(character.attributes)){
      if (!(key in attributes)){
        attributes[key] = value;
      }
    }
  }
  character.attributes = attributes;
  if (!Array.isArray(character.modes) && Array.isArray(normalized.modes) && character.modes === undefined){
    character.modes = normalized.modes.slice();
    delete normalized.modes;
  }
  return normalized;
}

function load_deep(raw){
  const source = typeof raw === 'string' ? JSON.parse(raw) : clone_plain_object(raw);
  const normalized = normalize_save_v6(source);
  const migrated = migrate_save(normalized);
  const runtimeSemver = majorMinor(ZR_VERSION);
  const saveSemver = majorMinor(migrated.zr_version || migrated.ZR_VERSION);
  if (saveSemver && saveSemver !== runtimeSemver){
    throw new Error(`Kodex-Archiv: Datensatz v${saveSemver} nicht kompatibel mit v${runtimeSemver}. Bitte HQ-Migration veranlassen.`);
  }
  migrated.zr_version = migrated.zr_version || ZR_VERSION;
  migrated.logs ||= {};
  if (Array.isArray(migrated.logs.offline)){
    migrated.logs.offline = sanitize_offline_entries(migrated.logs.offline);
  } else {
    migrated.logs.offline = [];
  }
  if (Array.isArray(migrated.logs.foreshadow)){
    const deduped = [];
    const byToken = new Map();
    for (const entry of migrated.logs.foreshadow){
      if (!entry || typeof entry !== 'object' || typeof entry.token !== 'string') continue;
      const rawToken = entry.token.trim();
      if (!rawToken) continue;
      const token = rawToken.toLowerCase();
      const tag = typeof entry.tag === 'string' && entry.tag.trim() ? entry.tag.trim() : 'Foreshadow';
      const message = typeof entry.message === 'string' ? entry.message.trim() : '';
      const sceneIndex = Number(entry.scene);
      const scene = Number.isFinite(sceneIndex) ? sceneIndex : null;
      const firstSeen = typeof entry.first_seen === 'string' ? entry.first_seen : null;
      const lastSeen = typeof entry.last_seen === 'string' ? entry.last_seen : null;
      if (byToken.has(token)){
        const existing = byToken.get(token);
        if (!existing.message && message){
          existing.message = message;
        }
        if (!existing.tag && tag){
          existing.tag = tag;
        }
        if (!Number.isFinite(existing.scene) && Number.isFinite(scene)){
          existing.scene = scene;
        }
        if (!existing.last_seen && lastSeen){
          existing.last_seen = lastSeen;
        }
        continue;
      }
      const record = {
        token,
        tag,
        message,
        scene,
        first_seen: firstSeen,
        last_seen: lastSeen || firstSeen
      };
      deduped.push(record);
      byToken.set(token, record);
    }
    migrated.logs.foreshadow = deduped;
  } else {
    migrated.logs.foreshadow = [];
  }
  if (!migrated.logs.flags || typeof migrated.logs.flags !== 'object'){
    migrated.logs.flags = {};
  }
  if (!migrated.logs.flags.runtime_version){
    migrated.logs.flags.runtime_version = migrated.zr_version || ZR_VERSION;
  }
  migrated.arc_dashboard = prepare_save_arc_dashboard(migrated.arc_dashboard);
  if (typeof migrated.logs.flags.compliance_shown_today !== 'boolean'){
    const fallback = !!migrated.campaign?.compliance_shown_today;
    migrated.logs.flags.compliance_shown_today = fallback;
  }
  if (typeof migrated.logs.flags.chronopolis_warn_seen !== 'boolean'){
    migrated.logs.flags.chronopolis_warn_seen = false;
  } else {
    migrated.logs.flags.chronopolis_warn_seen = !!migrated.logs.flags.chronopolis_warn_seen;
  }
  if (typeof migrated.logs.flags.offline_help_last !== 'string'){
    migrated.logs.flags.offline_help_last = null;
  }
  const migratedOfflineCount = Number(migrated.logs.flags.offline_help_count);
  migrated.logs.flags.offline_help_count = Number.isFinite(migratedOfflineCount) && migratedOfflineCount > 0
    ? Math.floor(migratedOfflineCount)
    : 0;
  if (migrated.campaign && typeof migrated.campaign === 'object' && typeof migrated.campaign.compliance_shown_today !== 'boolean'){
    migrated.campaign.compliance_shown_today = !!migrated.logs.flags.compliance_shown_today;
  }
  migrated.location = 'HQ';
  hydrate_state(migrated);
  ensure_runtime_flags().skip_entry_choice = true;
  show_compliance_once();
  const hud = scene_overlay();
  writeLine(hud);
  return { status: 'ok', state, hud };
}

function startSolo(mode='klassisch'){
  ensure_ui();
  state.start = { type: 'solo', mode };
  state.location = 'HQ';
  state.character = {
    id: 'CHR-NEW',
    stress: 0,
    psi_heat: 0,
    self_reflection: true,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_used: 1 }
  };
  ensure_logs();
  state.logs.flags.compliance_shown_today = false;
  state.logs.flags.chronopolis_warn_seen = false;
  ensure_campaign();
  state.campaign.compliance_shown_today = false;
  ensure_runtime_flags().skip_entry_choice = false;
  play_hq_intro();
  return `solo-${mode}`;
}

function setupNpcTeam(size=0){
  state.team = { size };
}

function startGroup(mode='klassisch'){
  ensure_ui();
  state.start = { type: 'gruppe', mode };
  state.location = 'HQ';
  state.team = { size: 0 };
  ensure_logs();
  state.logs.flags.compliance_shown_today = false;
  state.logs.flags.chronopolis_warn_seen = false;
  ensure_campaign();
  state.campaign.compliance_shown_today = false;
  ensure_runtime_flags().skip_entry_choice = false;
  play_hq_intro();
  return `gruppe-${mode}`;
}

function launch_mission(){
  state.phase = 'transfer';
  StartMission();
  return 'mission-launched';
}

function debrief(st){
  const outcome = st || {};
  const cuReward = extractCuReward(outcome);
  const result = completeMission(outcome);
  const lines = [];
  lines.push(render_rewards(outcome, result));
  if (cuReward !== null && cuReward > 0){
    const split = apply_wallet_split(outcome, cuReward);
    if (split.lines.length){
      lines.push(...split.lines);
    }
  }
  lines.push(render_px_tracker(outcome.temp || mission_temp()));
  const marketTrace = render_market_trace();
  if (marketTrace){
    lines.push(marketTrace);
  }
  const foreshadowSummary = render_foreshadow_report();
  if (foreshadowSummary){
    lines.push(foreshadowSummary);
  }
  const offlineSummary = render_offline_protocol();
  if (offlineSummary){
    lines.push(offlineSummary);
  }
  const aliasSummary = render_alias_trace_summary();
  if (aliasSummary){
    lines.push(aliasSummary);
  }
  const radioSummary = render_squad_radio_summary();
  if (radioSummary){
    lines.push(radioSummary);
  }
  const flagSummary = render_runtime_flags_summary();
  if (flagSummary){
    lines.push(flagSummary);
  }
  if (result.events.length){
    lines.push(result.events.join('\n'));
  }
  return lines.join('\n');
}

function on_command(command){
    let cmd = command.toLowerCase().trim();
    if (cmd.startsWith('!load ')){
      const json = command.slice(6).trim();
      return load_deep(json);
    }
    if (cmd === '!load' || cmd === 'spiel laden' || cmd === 'spielstand laden'){
      return 'Kodex: Poste Speicherstand als JSON.';
    }
    if (cmd === '!suspend'){
      try {
        return suspend_snapshot();
      } catch (err){
        return err.message;
      }
    }
    if (cmd === '!resume'){
      try {
        return resume_snapshot();
      } catch (err){
        return err.message;
      }
    }
    if (cmd.startsWith('!arena')){
      try {
        return handleArenaCommand(cmd);
      } catch (err){
        return err.message;
      }
    }
    let m;
    if ((m = cmd.match(/^spiel starten \(solo\)(?:\s+(schnell|fast|klassisch|classic))?/))){
      const mode = (cmd.includes('schnell') || cmd.includes('fast')) ? 'schnell' : 'klassisch';
      return startSolo(mode);
    }
    if ((m = cmd.match(/^spiel starten\s*\(npc-team\)(?:\s+([0-4]))?(?:\s+(schnell|fast|klassisch|classic))?$/))){
      const mode = (cmd.includes('schnell') || cmd.includes('fast')) ? 'schnell' : 'klassisch';
      startSolo(mode);
      const size = m[1] ? parseInt(m[1], 10) : 0;
      setupNpcTeam(size);
      state.start.type = 'npc-team';
      return `npc-team-${mode}`;
    }
    if ((m = cmd.match(/^spiel starten\s*\(gruppe\)(?:\s+(schnell|fast|klassisch|classic))?$/))){
      const mode = (cmd.includes('schnell') || cmd.includes('fast')) ? 'schnell' : 'klassisch';
      return startGroup(mode);
    }
    if (cmd === '!help start' || cmd === '/help start'){
        return [
          'Startbefehle:',
          '- Spiel starten (solo) [klassisch|schnell]',
          '- Spiel starten (npc-team [0–4]) [klassisch|schnell]',
          '- Spiel starten (gruppe) [klassisch|schnell]',
          '- Spiel laden',
          'Klammern sind Pflicht. Rollen-Kurzformen: infil/tech/face/cqb/psi.',
          'Speichern nur im HQ. Px 5 ⇒ ClusterCreate() (Rift-Seeds nach Episodenende).'
        ].join('\n');
      }
    if (cmd === '!offline' || cmd === '!help offline' || cmd === '/help offline' || cmd === 'offline hilfe'){
        return offline_help('command');
      }
    if (cmd === '!help urban' || cmd === '/help urban'){
        return [
          'Urban Quick-Card:',
          'Deckung: Offen 0 · Teildeckung +1 SG · Volldeckung +2 SG (Peek kostet 1 Aktion).',
          'Mobile Deckung (Schild/Drohne) +1 SG, zerfällt nach 2 Treffern oder 1 Krit.',
          'Verfolgungsjagd: Distanzstufen 0–3. Erfolg +1, Stunt (SG +2) → +2 oder Komplikation für Gegner.',
          'Speed-Delta π = Fahrstufen-Differenz × 2 m pro Szene; Doppel-Fail → Crashbeat & Distanz −2.',
          'HUD-Tags: COVER · PURSUIT · MOVE – Toasts maximal 6 Wörter, haltet sie filmisch.'
        ].join('\n');
      }
    if (cmd === '!help sg' || cmd === '/help sg'){
        return [
          'SG & Exploding Quick-Card:',
          'Attribute 1–10 → W6 · ab 11 W10 · Heldenwürfel ab 14 (1× Reroll).',
          'Exploding: jede 6/10 explodiert einmal; Arena/Boss halbieren Overflow automatisch.',
          'SG-Richtwerte: Leicht 5 · Mittel 8–9 · Schwer 12 · Extrem 15+.',
          'Phasen-Fokus: Aufklärung 8 · Zugriff 12 · Exfiltration 10 – callt eure Ziele laut.',
          'Explosionsketten ansagen: z.B. 6→6→3 = 15, damit das HUD den Peak loggt.'
        ].join('\n');
      }
    if (cmd === 'begin mission'){
      return launch_mission();
    }
    if (cmd === '!gear shop'){
      ensure_campaign();
      const lvl = state.character?.lvl ?? 1;
      const rep = state.campaign?.faction_rep ?? 0;
      const bp = state.campaign?.rift_blueprints ?? [];
      return render_shop_tiers(lvl, rep, bp);
    }
    if (cmd === '!chrono stock'){
      return chronopolisStockReport();
    }
    if (cmd === '!chrono tick'){
      return chronopolisTickStatus();
    }
    if ((m = cmd.match(/^!chrono\s+tick\s+(off|0|[1-9]\d*)$/))){
      const token = m[1];
      const value = token === 'off' ? 0 : parseInt(token, 10);
      return chronopolisSetTickModulo(value);
    }
    if (cmd === '!chrono reset'){
      chronopolis_reset('manual');
      state.campaign.chronopolis_missions_since_reset = 0;
      return 'Chronopolis-Reset durchgeführt. Tagesangebot wird bei nächstem Abruf neu geladen.';
    }
    if (cmd === '!alias' || cmd.startsWith('!alias ')){
      return handleAliasCommand(command.trim());
    }
    if (cmd === '!radio' || cmd.startsWith('!radio ')){
      return handleRadioCommand(command.trim());
    }
    if (cmd === '!dashboard' || cmd === '!dashboard status'){
      return render_arc_dashboard_status();
    }
    if (cmd === '!help dashboard'){
      return 'Arc-Dashboard: !dashboard status fasst Seeds, Fraktionsmeldungen und offene Fragen als Text zusammen.';
    }
    if (cmd === '!px'){
      return render_px_tracker();
    }
  if ((m = cmd.match(/^!exfil\s+arm(?:\s+(.+))?/))){
    return exfil_arm(m[1]);
  }
  if ((m = cmd.match(/^!exfil\s+alt(?:\s+(.+))?/))){
    return exfil_set_alt(m[1]);
  }
  if ((m = cmd.match(/^!exfil\s+(?:tick|rw)\s+(.+)/))){
    const ttl = exfil_tick(m[1]);
    return `RW ${ttl}`;
  }
  if (cmd === '!exfil status'){
    const exfil = ensure_exfil();
    const ttl = ttl_fmt(exfil.ttl_min, exfil.ttl_sec);
    const armed = exfil.armed ? 'armiert' : 'inaktiv';
    const alt = exfil.alt_anchor ? ` · ALT ${exfil.alt_anchor}` : '';
    return `Exfil ${armed} · ANCR ${exfil.anchor || '?'} · RW ${ttl}${alt}`;
  }
  if (cmd === 'modus suggest'){
    const result = set_suggest_mode(true);
    return `${result.status} – Kodex liefert auf Anfrage Vorschläge.`;
  }
  if (cmd === 'modus ask'){
    const result = set_suggest_mode(false);
    return `${result.status} – Kodex wartet auf direkte Fragen.`;
  }
  if (cmd === '!sf off' || cmd === 'sf off' || cmd === 'self reflection off' || cmd === 'self-reflection off'){
    const result = set_self_reflection(false);
    return `${result.status} – introspektive Sequenzen gesperrt.`;
  }
  if (cmd === '!sf on' || cmd === 'sf on' || cmd === 'self reflection on' || cmd === 'self-reflection on'){
    const result = set_self_reflection(true);
    return `${result.status} – introspektive Sequenzen freigegeben.`;
  }
  if (cmd === '!sf' || cmd === '!sf status' || cmd === 'sf status'){
    return self_reflection_enabled()
      ? 'SF-ON – introspektive Sequenzen erlaubt.'
      : 'SF-OFF – Fokus bleibt extern.';
  }
  if (cmd === '!tk melee' || cmd === 'tk melee'){
    const remaining = activate_tk_melee_cooldown(1);
    return remaining > 0
      ? `TK🌀 Cooldown ${remaining} Runde aktiv.`
      : 'TK🌀 bereit.';
  }
  if (cmd === '!tk ready' || cmd === 'tk ready'){
    return clear_tk_melee_cooldown()
      ? 'TK🌀 wieder einsatzbereit.'
      : 'TK🌀 war nicht blockiert.';
  }
  if (cmd === 'modus precision'){
    ensure_ui().gm_style = 'precision';
    return 'GM_STYLE → precision (persistiert)';
  }
  if (cmd === 'modus verbose'){
    ensure_ui().gm_style = 'verbose';
    return 'GM_STYLE → verbose (persistiert)';
  }
  if (cmd === '!fr help'){
    return 'FR-Status:\nruhig · beobachter · aktiv';
  }
  if (cmd === '!boss status'){
    return foreshadow_status();
  }
  return '';
}

module.exports = {
  ZR_VERSION,
  state,
  on_command,
  debrief,
  render_shop_tiers,
  render_px_tracker,
  px_tracker,
  StartMission,
  scene_overlay,
  completeMission,
  incrementParadoxon,
  ClusterCreate,
  radio_tx,
  radio_rx,
  kodex_link_state,
  require_uplink,
  assert_foreshadow,
  ForeshadowHint,
  save_deep,
  migrate_save,
  load_deep,
  startSolo,
  setupNpcTeam,
  startGroup,
  jam_now,
  launch_mission,
  chronopolisStockReport,
  chronopolisTickStatus,
  suspend_snapshot,
  resume_snapshot,
  resolveSuspendPath,
  campaign_mode,
  is_pvp,
  phase_strike_tax,
  phase_strike_cost,
  apply_arena_rules,
  getArenaFee,
  arenaStart,
  arenaScore,
  arenaExit,
  arenaRegisterResult,
  handleArenaCommand,
  offline_help,
  offline_audit,
  render_offline_protocol,
  log_intervention,
  get_intervention_log,
  set_suggest_mode,
  suggest_mode_enabled,
  log_market_purchase,
  log_alias_event,
  log_squad_radio,
  render_alias_trace_summary,
  render_squad_radio_summary,
  render_arc_dashboard_status
};
