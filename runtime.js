const fs = require('fs');
const path = require('path');
const { version: ZR_VERSION = '4.2.3' } = require('./package.json');

const RANK_ORDER = ['Recruit', 'Operator I', 'Operator II', 'Lead', 'Specialist', 'Chief'];
const COMPLIANCE_NOTICE =
  'Compliance-Hinweis: ZEITRISS ist ein Science-Fiction-Rollenspiel. Alle Ereignisse sind fiktiv.';

const CHRONO_CATEGORY_LIMITS = {
  'Temporal Ships': 1,
  'Never-Was Gadgets': 3,
  'Era-Skins': 4
};

const OFFLINE_HELP_TOAST = 'Kodex-Uplink getrennt – Mission läuft weiter mit HUD-Lokaldaten.';
const OFFLINE_HELP_GUIDE = [
  'Kodex Offline-FAQ (ITI↔Kodex-Uplink im Einsatz gekappt):',
  '- Terminal oder Hardline suchen, Relay koppeln, Jammer-Override prüfen – Kodex bleibt bis dahin stumm.',
  '- Mission normal fortsetzen: HUD liefert lokale Logs; HQ-Deepsaves/Cloud-Sync laufen erst nach der',
  '  Rückkehr ins HQ (HQ-only, keine Save-Sperre).',
  '- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ markieren und Bestätigung abwarten.'
];

function helper_delay_text(){
  return "DelayConflict(th=4, allow=[]): Konflikte ab Szene th. Setze allow='ambush|vehicle_chase' für Ausnahmen.";
}

function helper_comms_text(){
  return [
    'comms_check(device,range_m,range_km?): Pflicht vor radio_tx/rx.',
    'Akzeptiert `comlink|cable|relay|jammer_override` (Groß-/Kleinschreibung egal)',
    'und Meterwerte; optional wandelt der Guard Kilometer in Meter um.',
    'Tipp: Terminal suchen / Comlink koppeln / Kabel/Relais nutzen / Jammer-Override aktivieren;',
    'Reichweite anpassen. `!offline` zeigt das Feldprotokoll, während die Mission mit HUD-Lokaldaten weiterläuft.'
  ].join('\n');
}

function helper_boss_text(){
  return [
    'Boss-Foreshadow: Core – M4 und M9 je zwei Hinweise, Rift – Szene 9 zwei Hinweise.',
    'Nutze `ForeshadowHint()` oder automatische Seeds, damit `state.logs.foreshadow`',
    'und `scene.foreshadows` den Fortschritt persistieren.',
    'Gate 2/2 steht ab Missionsstart; Szene 10 öffnet nur bei FS 4/4 (Core) oder 2/2 (Rift).',
    'Gate-Toast zeigt fehlende Foreshadows: `Gate blockiert – FS x/y (Gate 2/2 bleibt)`.'
  ].join('\n');
}

const OFFLINE_HELP_MIN_INTERVAL_MS = 60 * 1000;
const MARKET_LOG_LIMIT = 24;
const OFFLINE_LOG_LIMIT = 12;
const FR_INTERVENTION_LOG_LIMIT = 16;
const FORESHADOW_GATE_REQUIRED = 2;
const PSI_LOG_LIMIT = 16;
const ALIAS_TRACE_LIMIT = 24;
const SQUAD_RADIO_LOG_LIMIT = 24;

const CHRONO_CATALOG = [
  {
    id: 'ship_chronoglider_mk2',
    name: 'Chronoglider MK II',
    category: 'Temporal Ships',
    price: 5000,
    minRank: 'Lead',
    minResearch: 2
  },
  {
    id: 'ship_aurora_skiff',
    name: 'Aurora-Skiff „Helio“',
    category: 'Temporal Ships',
    price: 5400,
    minRank: 'Specialist',
    minResearch: 3
  },
  {
    id: 'ship_timesloop_schooner',
    name: 'Timesloop-Schooner',
    category: 'Temporal Ships',
    price: 5200,
    minRank: 'Lead',
    minResearch: 3
  },
  {
    id: 'gadget_quantum_flashbang',
    name: 'Quantum-Flashbang',
    category: 'Never-Was Gadgets',
    price: 500,
    minRank: 'Operator II',
    minResearch: 1
  },
  {
    id: 'gadget_nullgrav_tether',
    name: 'Null-Grav-Tether',
    category: 'Never-Was Gadgets',
    price: 450,
    minRank: 'Operator I',
    minResearch: 1
  },
  {
    id: 'gadget_phase_jump_capsule',
    name: 'Phase-Jump-Kapsel',
    category: 'Never-Was Gadgets',
    price: 750,
    minRank: 'Lead',
    minResearch: 2
  },
  {
    id: 'gadget_echo_distortion_field',
    name: 'Echo-Distortion-Field',
    category: 'Never-Was Gadgets',
    price: 900,
    minRank: 'Specialist',
    minResearch: 3
  },
  {
    id: 'skin_aeon_nomad',
    name: 'Era-Skin: Æon-Nomadenmantel',
    category: 'Era-Skins',
    price: 200,
    minRank: 'Recruit',
    minResearch: 0
  },
  {
    id: 'skin_krakatoa_1883',
    name: 'Era-Skin: Krakatoa 1883 Survivor',
    category: 'Era-Skins',
    price: 200,
    minRank: 'Operator I',
    minResearch: 0
  },
  {
    id: 'skin_neon_cathedral',
    name: 'Era-Skin: Neon-Cathedral Glimmer',
    category: 'Era-Skins',
    price: 220,
    minRank: 'Lead',
    minResearch: 1
  },
  {
    id: 'skin_sable_parallax',
    name: 'Era-Skin: Sable-Parallax Cloak',
    category: 'Era-Skins',
    price: 240,
    minRank: 'Specialist',
    minResearch: 2
  }
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
const GEAR_ALIAS_MAP = {
  multitoolarmband: 'Multi-Tool-Handschuh'
};
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
  const phase = normalize_phase_value(pickString(entry.phase));
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
  let faction = pickString(
    payload.faction,
    payload.faction_id,
    payload.faction_name,
    payload.faction_tag,
    payload.name
  );
  if (!faction && fillDefaults && typeof state.campaign?.faction === 'string'){
    faction = state.campaign.faction;
  }
  let impact = pickString(payload.impact, payload.effect, payload.delta, payload.summary);
  const note = pickString(payload.note, payload.details, payload.comment, payload.description);
  let location = pickString(payload.location, payload.place);
  if (!location && fillDefaults && typeof state.location === 'string'){
    location = state.location;
  }
  let phase = normalize_phase_value(pickString(payload.phase));
  if (!phase && fillDefaults && typeof state.phase === 'string'){
    phase = normalize_phase_value(state.phase);
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

function sanitize_arena_psi_entries(entries){
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
    const category = pickString(entry.category) || 'arena_phase_strike';
    const record = {
      ability,
      timestamp,
      base_cost: Number.isFinite(baseCost) ? baseCost : 0,
      tax: Number.isFinite(tax) ? tax : 0,
      total_cost: Number.isFinite(total)
        ? total
        : ((Number.isFinite(baseCost) ? baseCost : 0) + (Number.isFinite(tax) ? tax : 0)),
      mode,
      arena_active: arenaActive,
      category
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

function sanitize_merge_conflicts(entries){
  if (!Array.isArray(entries)) return [];
  const sanitized = [];
  const limit = 50;
  entries.forEach((entry) => {
    if (!entry || typeof entry !== 'object') return;
    const field = pickString(entry.field, entry.key, entry.path);
    const source = pickString(entry.source, entry.source_value, entry.incoming);
    const target = pickString(entry.target, entry.target_value, entry.existing);
    const mode = pickString(entry.mode, entry.context);
    const note = pickString(entry.note, entry.reason, entry.description);
    const timestamp = isoTimestamp(entry.timestamp);
    const resolved = entry.resolved === true;
    if (!field) return;
    const record = { field };
    if (source){
      record.source = source;
    }
    if (target){
      record.target = target;
    }
    if (mode){
      record.mode = mode;
    }
    if (timestamp){
      record.timestamp = timestamp;
    }
    if (note){
      record.note = note;
    }
    record.resolved = resolved;
    sanitized.push(record);
  });
  if (sanitized.length > limit){
    return sanitized.slice(sanitized.length - limit);
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
  if (!Array.isArray(state.logs.trace)){
    state.logs.trace = [];
  } else if (state.logs.trace.length > 64){
    state.logs.trace = state.logs.trace.slice(-64);
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
  if (!Array.isArray(state.logs.arena_psi)){
    state.logs.arena_psi = [];
  } else {
    state.logs.arena_psi = sanitize_arena_psi_entries(state.logs.arena_psi);
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
  const legacyOfflineLast = typeof flags.offline_help_last === 'string'
    ? flags.offline_help_last
    : null;
  const offlineScene = typeof flags.offline_help_last_scene === 'string'
    ? flags.offline_help_last_scene
    : null;
  const normalizedOfflineScene = offlineScene || legacyOfflineLast;
  flags.offline_help_last_scene = normalizedOfflineScene || null;
  flags.offline_help_last = normalizedOfflineScene || null;
  if (!Number.isFinite(flags.offline_help_count)){
    flags.offline_help_count = 0;
  } else {
    flags.offline_help_count = Math.max(0, Math.floor(flags.offline_help_count));
  }
  if (!Array.isArray(flags.merge_conflicts)){
    flags.merge_conflicts = [];
  } else {
    flags.merge_conflicts = sanitize_merge_conflicts(flags.merge_conflicts);
  }
  const charSelfReflection =
    state.character && typeof state.character.self_reflection === 'boolean'
      ? state.character.self_reflection
      : null;
  if (charSelfReflection !== null){
    flags.self_reflection = !!charSelfReflection;
  } else if (typeof flags.self_reflection !== 'boolean'){
    flags.self_reflection = true;
  } else {
    flags.self_reflection = !!flags.self_reflection;
  }
  const gateProgress = Number(flags.foreshadow_gate_progress);
  flags.foreshadow_gate_progress = Number.isFinite(gateProgress) && gateProgress > 0
    ? Math.min(FORESHADOW_GATE_REQUIRED, Math.max(0, Math.floor(gateProgress)))
    : 0;
  const gateSnapshot = Number(flags.foreshadow_gate_snapshot);
  flags.foreshadow_gate_snapshot = Number.isFinite(gateSnapshot) && gateSnapshot > 0
    ? Math.min(FORESHADOW_GATE_REQUIRED, Math.max(0, Math.floor(gateSnapshot)))
    : 0;
  flags.foreshadow_gate_expected = !!flags.foreshadow_gate_expected
    || flags.foreshadow_gate_progress > 0
    || flags.foreshadow_gate_snapshot > 0;
  flags.foreshadow_gate_m5_seen = !!flags.foreshadow_gate_m5_seen;
  flags.foreshadow_gate_m10_seen = !!flags.foreshadow_gate_m10_seen;
  flags.self_reflection_off = (!flags.self_reflection && flags.self_reflection_off !== false)
    || (flags.self_reflection_off === true && !flags.self_reflection);
  if (typeof flags.self_reflection_changed_at !== 'string'){
    flags.self_reflection_changed_at = null;
  }
  if (typeof flags.self_reflection_last_change_reason !== 'string'){
    flags.self_reflection_last_change_reason = null;
  } else {
    const trimmed = flags.self_reflection_last_change_reason.trim();
    flags.self_reflection_last_change_reason = trimmed ? trimmed : null;
  }
  if (typeof flags.self_reflection_auto_reset_at !== 'string'){
    flags.self_reflection_auto_reset_at = null;
  }
  if (typeof flags.self_reflection_auto_reset_reason !== 'string'){
    flags.self_reflection_auto_reset_reason = null;
  } else {
    const resetReason = flags.self_reflection_auto_reset_reason.trim();
    flags.self_reflection_auto_reset_reason = resetReason ? resetReason : null;
  }
  if (typeof flags.last_mission_end_reason !== 'string'){
    flags.last_mission_end_reason = null;
  } else {
    const lastReason = flags.last_mission_end_reason.trim();
    flags.last_mission_end_reason = lastReason ? lastReason : null;
  }
    if (
      state.campaign &&
      typeof state.campaign === 'object' &&
      typeof state.campaign.compliance_shown_today !== 'boolean'
    ){
    state.campaign.compliance_shown_today = flags.compliance_shown_today;
  }
  if (state.character && typeof state.character === 'object'){
    state.character.self_reflection = flags.self_reflection;
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

function ensure_arena_psi_log(){
  ensure_logs();
  if (!Array.isArray(state.logs.arena_psi)){
    state.logs.arena_psi = [];
  }
  state.logs.arena_psi = sanitize_arena_psi_entries(state.logs.arena_psi);
  return state.logs.arena_psi;
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
  const arenaPsiLog = ensure_arena_psi_log();
  const now = new Date().toISOString();
  const base = Number.isFinite(details.base) ? Number(details.base) : 0;
  const tax = Number.isFinite(details.tax) ? Number(details.tax) : 0;
  const total = Number.isFinite(details.total) ? Number(details.total) : base + tax;
  const mode = campaign_mode(ctx);
  const arenaActive = !!(ctx?.arena?.active);
  const previousMode = typeof ctx?.arena?.previous_mode === 'string' && ctx.arena.previous_mode.trim()
    ? ctx.arena.previous_mode.trim()
    : null;
  const entry = {
    ability: 'phase_strike',
    timestamp: now,
    base_cost: base,
    tax,
    total_cost: total,
    mode,
    arena_active: arenaActive,
    category: 'arena_phase_strike'
  };
  if (previousMode){
    entry.mode_previous = previousMode;
  }
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
  arenaPsiLog.push(entry);
  if (arenaPsiLog.length > PSI_LOG_LIMIT){
    arenaPsiLog.splice(0, arenaPsiLog.length - PSI_LOG_LIMIT);
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

function record_npc_autoradio(size, mode){
  const normalizedSize = Number.isFinite(size) ? Math.max(0, Math.floor(size)) : 0;
  const presetParts = [`NPC-Autoradio aktiv (${normalizedSize}× Squad)`];
  const normalizedMode = typeof mode === 'string' ? mode.trim().toLowerCase() : 'preserve';
  if (normalizedMode === 'trigger'){
    presetParts.push('Trigger-Seeds bereit');
  }
  log_squad_radio({
    speaker: 'Kodex',
    channel: 'npc-team',
    message: presetParts.join(' · '),
    status: 'preset'
  });
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
  const normalized = cmd.toLowerCase();
  if (normalized === '!alias' || normalized === '!alias status'){
    const summary = render_alias_trace_summary();
    return summary || 'Alias-Trace leer.';
  }
  if (normalized === '!alias clear'){
    const trace = ensure_alias_trace();
    trace.length = 0;
    return 'Alias-Trace geleert.';
  }
  if (normalized === '!alias help'){
    return (
      'Alias-Trace: `!alias log Persona|Cover|Status|Notiz` oder Felder via `key=value` setzen. '
      + '`!alias status` zeigt die Übersicht.'
    );
  }
  const m = cmd.match(/^!alias\s+log\s+(.+)/i);
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
  const normalized = cmd.toLowerCase();
  if (normalized === '!radio' || normalized === '!radio status'){
    const summary = render_squad_radio_summary();
    return summary || 'Squad-Radio-Log leer.';
  }
  if (normalized === '!radio clear'){
    const log = ensure_squad_radio_log();
    log.length = 0;
    return 'Squad-Radio-Log geleert.';
  }
  if (normalized === '!radio help'){
    return (
      'Squad-Radio: `!radio log Sprecher|Channel|Meldung|Status` oder Felder via `key=value`. '
      + '`!radio status` zeigt die letzten Einträge.'
    );
  }
  const m = cmd.match(/^!radio\s+log\s+(.+)/i);
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

function gate_progress_info(ctx = state){
  const flags = ctx?.logs?.flags || {};
  const snapshot = Number(flags.foreshadow_gate_snapshot);
  const live = Number(flags.foreshadow_gate_progress);
  const value = Number.isFinite(snapshot) && snapshot > 0
    ? Math.min(FORESHADOW_GATE_REQUIRED, Math.max(0, Math.floor(snapshot)))
    : Number.isFinite(live)
    ? Math.min(FORESHADOW_GATE_REQUIRED, Math.max(0, Math.floor(live)))
    : 0;
  return {
    value,
    expected: !!flags.foreshadow_gate_expected
  };
}

function foreshadow_status(ctx = state){
  const count = foreshadow_count();
  const required = foreshadow_requirement(ctx);
  const gate = gate_progress_info(ctx);
  const missionText = required > 0 ? `Mission FS ${count}/${required}` : `Foreshadow ${count}`;
  if (gate.expected || gate.value > 0){
    return `Gate ${gate.value}/${FORESHADOW_GATE_REQUIRED} · ${missionText}`;
  }
  return missionText;
}

function sync_foreshadow_progress(){
  const missionType = resolve_mission_type();
  const sceneTotal = resolve_scene_total(missionType);
  if (!state.scene){
    state.scene = { index: 0, foreshadows: 0, total: sceneTotal };
  } else if (!Number.isFinite(state.scene.total) || state.scene.total <= 0){
    state.scene.total = sceneTotal;
  }
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

function normalize_badge_density(value, fallback = 'standard'){
  const normalized = typeof value === 'string' ? value.trim().toLowerCase() : '';
  if (['standard', 'dense', 'compact'].includes(normalized)){
    return normalized;
  }
  if (normalized === 'full') return 'standard';
  if (normalized === 'minimal') return 'compact';
  return fallback;
}

function normalize_phase_value(value, fallback = ''){
  const normalized = typeof value === 'string' ? value.trim().toLowerCase() : '';
  return normalized || fallback;
}

function ensure_ui(){
  if (!state.ui || typeof state.ui !== 'object'){
    state.ui = {
      gm_style: 'verbose',
      intro_seen: false,
      suggest_mode: false,
      contrast: 'standard',
      badge_density: 'standard',
      output_pace: 'normal'
    };
  }
  if (typeof state.ui.gm_style !== 'string'){
    state.ui.gm_style = 'verbose';
  }
  state.ui.intro_seen = !!state.ui.intro_seen;
  if (typeof state.ui.suggest_mode !== 'boolean'){
    state.ui.suggest_mode = false;
  }
  const contrast = typeof state.ui.contrast === 'string' ? state.ui.contrast.trim().toLowerCase() : '';
  if (!['standard', 'high'].includes(contrast)){
    state.ui.contrast = 'standard';
  } else {
    state.ui.contrast = contrast;
  }
  state.ui.badge_density = normalize_badge_density(state.ui.badge_density);
  const pace = typeof state.ui.output_pace === 'string' ? state.ui.output_pace.trim().toLowerCase() : '';
  if (!['normal', 'slow', 'fast'].includes(pace)){
    state.ui.output_pace = 'normal';
  } else {
    state.ui.output_pace = pace;
  }
  return state.ui;
}

function accessibility_status(){
  const ui = ensure_ui();
  const parts = [];
  parts.push(`Kontrast: ${ui.contrast === 'high' ? 'hoch' : 'standard'}`);
  const badgeMap = { standard: 'standard', dense: 'dicht', compact: 'kompakt' };
  parts.push(`HUD-Badges: ${badgeMap[ui.badge_density] || 'voll'}`);
  const paceMap = { slow: 'langsam', normal: 'normal', fast: 'schnell' };
  parts.push(`Output-Takt: ${paceMap[ui.output_pace] || 'normal'}`);
  return [
    'Accessibility-Panel – verfügbare Optionen:',
    '- `!accessibility contrast [standard|high]`',
    '- `!accessibility badges [standard|dense|compact]`',
    '- `!accessibility pace [slow|normal|fast]`',
    '',
    `Aktueller Status: ${parts.join(' · ')}`
  ].join('\n');
}

function set_accessibility_option(option, value){
  const ui = ensure_ui();
  const normalizedOption = option.trim().toLowerCase();
  const normalizedValue = value.trim().toLowerCase();
  switch (normalizedOption){
    case 'contrast':
      if (!['standard', 'high'].includes(normalizedValue)){
        throw new Error('Kontrastoption unbekannt – nutze `standard` oder `high`.');
      }
      ui.contrast = normalizedValue;
      hud_toast(normalizedValue === 'high' ? 'HUD-Kontrast erhöht.' : 'HUD-Kontrast normal.', 'ACCESS');
      break;
    case 'badges':
    case 'badge':
      ui.badge_density = normalize_badge_density(normalizedValue, null);
      if (!ui.badge_density){
        throw new Error('Badge-Dichte unbekannt – wähle `standard`, `dense` oder `compact`.');
      }
      hud_toast(`HUD-Badges → ${ui.badge_density}`, 'ACCESS');
      break;
    case 'pace':
      if (!['slow', 'normal', 'fast'].includes(normalizedValue)){
        throw new Error('Tempo unbekannt – `slow`, `normal` oder `fast` sind erlaubt.');
      }
      ui.output_pace = normalizedValue;
      hud_toast(`Output-Takt → ${normalizedValue}`, 'ACCESS');
      break;
    default:
      throw new Error('Unbekannte Accessibility-Option.');
  }
  return accessibility_status();
}

const ECONOMY_PRIMARY_KEYS = ['credits', 'cu', 'balance', 'assets'];

function normalize_primary_currency(value){
  const numeric = asNumber(value);
  if (numeric === null) return null;
  const rounded = Math.round(numeric);
  return rounded < 0 ? 0 : rounded;
}

function resolve_primary_currency(economy){
  if (!economy || typeof economy !== 'object'){
    return 0;
  }
  for (const key of ECONOMY_PRIMARY_KEYS){
    if (!(key in economy)) continue;
    const normalized = normalize_primary_currency(economy[key]);
    if (normalized !== null){
      return normalized;
    }
  }
  return 0;
}

function sync_primary_currency(economy, override){
  if (!economy || typeof economy !== 'object'){
    return 0;
  }
  let amount = null;
  if (override !== undefined){
    amount = normalize_primary_currency(override);
  }
  if (amount === null){
    amount = resolve_primary_currency(economy);
  }
  if (amount === null){
    amount = 0;
  }
  economy.cu = amount;
  economy.credits = amount;
  return amount;
}

function ensure_economy(){
  if (!state.economy || typeof state.economy !== 'object'){
    state.economy = {};
  }
  const economy = state.economy;
  sync_primary_currency(economy);
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

function ensure_psi_buffer_flag(target){
  if (!target || typeof target !== 'object'){
    return target;
  }
  if (target.psi_buffer === undefined){
    target.psi_buffer = true;
  }
  return target;
}

function ensure_character(){
  state.character ||= {};
  const character = state.character;
  if (character.self_reflection === undefined){
    const persisted = state.logs?.flags?.self_reflection;
    character.self_reflection = persisted === false ? false : true;
  } else if (state.logs?.flags && typeof state.logs.flags.self_reflection === 'boolean'){
    character.self_reflection = state.logs.flags.self_reflection;
  }
  if (!character.rank){
    character.rank = 'Recruit';
  }
  if (!character.cooldowns || typeof character.cooldowns !== 'object'){
    character.cooldowns = {};
  }
  ensure_psi_buffer_flag(character);
  return character;
}

function ensure_team(){
  state.team ||= {};
  const team = state.team;
  team.stress = Number.isFinite(team.stress) ? team.stress : 0;
  team.psi_heat = Number.isFinite(team.psi_heat) ? team.psi_heat : 0;
  if (typeof team.status !== 'string'){ team.status = 'ready'; }
  if (!team.cooldowns || typeof team.cooldowns !== 'object'){ team.cooldowns = {}; }
  ensure_psi_buffer_flag(team);
  if (!Array.isArray(team.members)){
    team.members = [];
  }
  team.members.forEach((member) => {
    ensure_psi_buffer_flag(member);
  });
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
  party.characters.forEach((member) => {
    ensure_psi_buffer_flag(member);
  });
  return party;
}

function resolve_team_size(ctx = state){
  const campaignSize = asNumber(ctx?.campaign?.team_size);
  if (campaignSize !== null && campaignSize > 0){
    return Math.min(4, Math.max(1, Math.floor(campaignSize)));
  }
  const partySize = Array.isArray(ctx?.party?.characters) ? ctx.party.characters.length : null;
  if (Number.isFinite(partySize) && partySize > 0){
    return Math.min(4, Math.max(1, Math.floor(partySize)));
  }
  const teamSize = Array.isArray(ctx?.team?.members) ? ctx.team.members.length : null;
  if (Number.isFinite(teamSize) && teamSize > 0){
    return Math.min(4, Math.max(1, Math.floor(teamSize)));
  }
  return 1;
}

function ensure_arc_dashboard(){
  state.arc_dashboard ||= {};
  const dash = state.arc_dashboard;
  if (!Array.isArray(dash.offene_seeds)){
    dash.offene_seeds = [];
  } else {
    dash.offene_seeds = dash.offene_seeds
      .map((entry) => {
        if (entry && typeof entry === 'object'){
          return clone_plain_object(entry);
        }
        if (typeof entry === 'string'){
          const trimmed = entry.trim();
          return trimmed ? trimmed : null;
        }
        return null;
      })
      .filter(entry => entry !== null);
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
          const last = normalize_intervention_entry(
            record.last_intervention,
            record.last_intervention?.timestamp,
            { fillDefaults: false }
          );
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
  ensure_logs();
  const flags = state.logs.flags;
  if (typeof flags.self_reflection === 'boolean'){
    return flags.self_reflection;
  }
  const character = ensure_character();
  return character.self_reflection !== false;
}

function set_self_reflection(on, opts = {}){
  const options = opts && typeof opts === 'object' ? opts : {};
  const enabled = !!on;
  const character = ensure_character();
  character.self_reflection = enabled;
  ensure_logs();
  const flags = state.logs.flags || (state.logs.flags = {});
  const statusTag = options.tag || (enabled ? 'SF-ON' : 'SF-OFF');
  const defaultMessage = enabled
    ? 'Self-Reflection aktiv – introspektive Sequenzen frei.'
    : 'Self-Reflection deaktiviert – Fokus bleibt extern.';
  const message = options.message || defaultMessage;
  const timestamp = new Date().toISOString();
  flags.self_reflection = enabled;
  flags.self_reflection_off = !enabled;
  flags.self_reflection_changed_at = timestamp;
  flags.self_reflection_last_change_reason = options.reason || null;
  if (!options.silent){
    hud_toast(message, statusTag);
  }
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

function record_trace(event, details = {}){
  ensure_logs();
  if (!Array.isArray(state.logs.trace)){
    state.logs.trace = [];
  }
  const eventName = typeof event === 'string' && event.trim() ? event.trim() : 'event';
  const nowIso = new Date().toISOString();
  const sceneIndex = Number.isFinite(state.scene?.index) ? state.scene.index : null;
  const sceneTotal = Number.isFinite(state.scene?.total) ? state.scene.total : null;
  const episode = Number.isFinite(state.campaign?.episode) ? state.campaign.episode : null;
  const mission = Number.isFinite(state.campaign?.mission) ? state.campaign.mission : null;
  const missionType = resolve_mission_type();
  const campaignMode = typeof state.campaign?.mode === 'string' ? state.campaign.mode : null;
  const channel = typeof details.channel === 'string' && details.channel.trim()
    ? details.channel.trim()
    : null;
  const overlay = typeof details.hud === 'string' && details.hud.trim()
    ? details.hud.trim()
    : null;
  const foreshadowRequired = foreshadow_requirement();
  const foreshadowProgress = Number.isFinite(state.logs?.flags?.foreshadow_gate_progress)
    ? state.logs.flags.foreshadow_gate_progress
    : 0;
  const trace = {
    event: eventName,
    at: nowIso,
    location: state.location || null,
    phase: state.phase || state.campaign?.phase || null,
    mission_type: missionType,
    campaign_mode: campaignMode,
    scene: {
      episode,
      mission,
      index: sceneIndex,
      total: sceneTotal
    },
    hud: overlay,
    channel,
    foreshadow: {
      progress: foreshadowProgress,
      required: foreshadowRequired,
      tokens: Array.isArray(state.logs?.foreshadow) ? state.logs.foreshadow.length : 0,
      expected: !!state.logs?.flags?.foreshadow_gate_expected
    },
    radio_count: Array.isArray(state.logs?.squad_radio) ? state.logs.squad_radio.length : 0,
    kodex_count: Array.isArray(state.logs?.kodex) ? state.logs.kodex.length : 0,
    alias_count: Array.isArray(state.logs?.alias_trace) ? state.logs.alias_trace.length : 0,
    economy: {
      cu: Number.isFinite(state.economy?.cu) ? state.economy.cu : null,
      wallets: state.economy?.wallets ? Object.keys(state.economy.wallets).length : 0
    },
    fr_bias: state.campaign?.fr_bias || null,
    intervention: state.fr_intervention || null,
    note: typeof details.note === 'string' && details.note.trim() ? details.note.trim() : null
  };
  if (details.arena && typeof details.arena === 'object'){
    trace.arena = {
      scenario: details.arena.scenario || null,
      tier: details.arena.tier ?? null,
      team_size: details.arena.team_size ?? resolve_team_size()
    };
  }
  if (details.seed && typeof details.seed === 'object'){
    trace.seed = {
      id: details.seed.id || state.campaign?.active_seed_id || null,
      tier: details.seed.tier || state.campaign?.active_seed_tier || null,
      label: details.seed.label || state.campaign?.active_seed_label || null,
      status: details.seed.status || null
    };
  }
  state.logs.trace.push(trace);
  if (state.logs.trace.length > 64){
    state.logs.trace.splice(0, state.logs.trace.length - 64);
  }
  return trace;
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
  ensure_logs();
  const flags = state.logs.flags;
  const missionNumber = Number(state.campaign?.mission);
  const gateFixed = Number.isFinite(missionNumber) && (missionNumber === 5 || missionNumber === 10);
  if (!gateFixed){
    const current = Number.isFinite(flags.foreshadow_gate_progress)
      ? Math.max(0, Math.floor(flags.foreshadow_gate_progress))
      : 0;
    const next = Math.min(FORESHADOW_GATE_REQUIRED, current + 1);
    flags.foreshadow_gate_progress = next;
    if (next > 0){
      flags.foreshadow_gate_expected = true;
    }
    if (Number.isFinite(missionNumber)){
      if (missionNumber === 5 && next >= FORESHADOW_GATE_REQUIRED){
        flags.foreshadow_gate_m5_seen = true;
      }
      if (missionNumber === 10 && next >= FORESHADOW_GATE_REQUIRED){
        flags.foreshadow_gate_m10_seen = true;
      }
    }
  } else {
    flags.foreshadow_gate_expected = true;
    flags.foreshadow_gate_snapshot = FORESHADOW_GATE_REQUIRED;
    flags.foreshadow_gate_progress = 0;
    if (missionNumber === 5){
      flags.foreshadow_gate_m5_seen = true;
    }
    if (missionNumber === 10){
      flags.foreshadow_gate_m10_seen = true;
    }
  }
  return hud_toast(`${normalizedTag}: ${cleaned}`, normalizedTag);
}

function sync_compliance_flags(){
  ensure_logs();
  ensure_campaign();
  const flags = state.logs.flags;
  const combined = !!(flags.compliance_shown_today || state.campaign?.compliance_shown_today);
  flags.compliance_shown_today = combined;
  state.campaign.compliance_shown_today = combined;
  return combined;
}

function show_compliance_once(options = {}){
  const normalized = typeof options === 'boolean'
    ? { force: options, qa_mode: false }
    : (options || {});
  const force = !!normalized.force;
  const channel = typeof normalized.channel === 'string'
    ? normalized.channel.toLowerCase()
    : normalized.channel;
  const qaMode = !!normalized.qa_mode || channel === 'hud';
  ensure_logs();
  const flags = state.logs.flags;
  const alreadyShown = !!flags.compliance_shown_today;
  if (alreadyShown && !force){
    return false;
  }
  const toastOnly = qaMode;
  if (!toastOnly){
    writeLine(COMPLIANCE_NOTICE);
  }
  if (qaMode){
    hud_toast(COMPLIANCE_NOTICE, 'HUD');
  }
  flags.compliance_shown_today = true;
  sync_compliance_flags();
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
  sync_campaign_exfil(exfil);
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
  sync_campaign_exfil(exfil);
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
  sync_campaign_exfil(exfil);
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
  sync_campaign_exfil(exfil);
  const ttl = ttl_fmt(min, sec);
  const message = `Exfil Tick · RW ${ttl}`;
  hud_toast(message);
  return ttl;
}

function ensure_campaign(){
  state.campaign ||= {};
  const missionRaw = Number(state.campaign.mission);
  state.campaign.mission = Number.isFinite(missionRaw)
    ? Math.max(1, Math.floor(missionRaw))
    : 1;
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
  const missionInEpisodeRaw = Number(state.campaign.mission_in_episode);
  const missionInEpisode = Number.isFinite(missionInEpisodeRaw)
    ? Math.max(1, Math.floor(missionInEpisodeRaw))
    : ((state.campaign.mission - 1) % 10) + 1;
  state.campaign.mission_in_episode = missionInEpisode;
  if (typeof state.campaign.episode !== 'number'){
    const episode = Number(state.campaign.episode);
    state.campaign.episode = Number.isFinite(episode)
      ? Math.max(1, Math.floor(episode))
      : Math.max(1, Math.floor((state.campaign.mission - 1) / 10) + 1);
  } else {
    state.campaign.episode = Math.max(1, Math.floor(state.campaign.episode));
  }
  if (typeof state.campaign.episode_completed !== 'boolean'){
    state.campaign.episode_completed = missionInEpisode >= 10;
  } else {
    state.campaign.episode_completed = !!state.campaign.episode_completed;
  }
  if (typeof state.campaign.scene !== 'number'){
    const scene = Number(state.campaign.scene);
    state.campaign.scene = Number.isFinite(scene) ? scene : state.scene?.index ?? 0;
  }
  state.campaign.phase = normalize_phase_value(state.campaign.phase, state.phase || 'core');
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
  ensure_campaign_exfil();
  return state.campaign;
}

function normalize_rift_seed_entry(entry){
  if (!entry) return null;
  if (typeof entry === 'string'){
    const id = entry.trim();
    if (!id) return null;
    return { id, label: id, status: 'open' };
  }
  if (typeof entry !== 'object' || Array.isArray(entry)) return null;
  const id = pickString(entry.id, entry.seed_id, entry.label, entry.name);
  if (!id) return null;
  const statusRaw = pickString(entry.status, entry.state) || 'open';
  const status = statusRaw.toLowerCase() === 'closed' ? 'closed' : 'open';
  const seedTierRaw = pickString(entry.seed_tier);
  const seedTier = seedTierRaw ? seedTierRaw.toLowerCase() : null;
  const clusterHint = pickString(entry.cluster_hint);
  const levelHint = pickString(entry.level_hint);
  const epoch = Number(entry.epoch);
  const normalized = {
    id: id.trim(),
    label: pickString(entry.label, entry.name, id) || id.trim(),
    status,
  };
  if (seedTier && ['early', 'mid', 'late'].includes(seedTier)){
    normalized.seed_tier = seedTier;
  }
  if (clusterHint){
    normalized.cluster_hint = clusterHint;
  }
  if (levelHint){
    normalized.level_hint = levelHint;
  }
  if (Number.isFinite(epoch)){
    normalized.epoch = epoch;
  }
  return normalized;
}

function ensure_rift_seeds(){
  ensure_campaign();
  const seeds = Array.isArray(state.campaign.rift_seeds)
    ? state.campaign.rift_seeds
    : [];
  const normalized = seeds
    .map((entry) => normalize_rift_seed_entry(entry))
    .filter(Boolean);
  state.campaign.rift_seeds = normalized;
  return state.campaign.rift_seeds;
}

function ensure_campaign_exfil(){
  state.campaign ||= {};
  const campaign = state.campaign;
  if (!campaign.exfil || typeof campaign.exfil !== 'object'){
    campaign.exfil = {};
  }
  const exfil = campaign.exfil;
  exfil.active = !!exfil.active;
  exfil.armed = !!exfil.armed;
  exfil.hot = !!exfil.hot;
  exfil.sweeps = Number.isFinite(exfil.sweeps) ? Math.max(0, Math.floor(exfil.sweeps)) : 0;
  exfil.stress = Number.isFinite(exfil.stress) ? Math.max(0, Math.floor(exfil.stress)) : 0;
  exfil.anchor = typeof exfil.anchor === 'string' && exfil.anchor.trim() ? exfil.anchor.trim() : null;
  exfil.alt_anchor = typeof exfil.alt_anchor === 'string' && exfil.alt_anchor.trim() ? exfil.alt_anchor.trim() : null;
  exfil.ttl = Number.isFinite(exfil.ttl) ? Math.max(0, Number(exfil.ttl)) : 0;
  if (state.location === 'HQ'){
    exfil.active = false;
    exfil.armed = false;
    exfil.hot = false;
    exfil.ttl = 0;
    exfil.sweeps = 0;
    exfil.stress = 0;
    exfil.anchor = null;
    exfil.alt_anchor = null;
  } else if (state.phase === 'transfer'){
    exfil.active = false;
    exfil.armed = false;
  }
  return exfil;
}

function sync_campaign_exfil(source = state.exfil){
  ensure_campaign();
  const exfil = ensure_campaign_exfil();
  if (!source || typeof source !== 'object'){
    exfil.active = false;
    exfil.armed = false;
    exfil.hot = false;
    exfil.ttl = 0;
    exfil.sweeps = 0;
    exfil.stress = 0;
    exfil.anchor = null;
    exfil.alt_anchor = null;
    return exfil;
  }
  exfil.active = !!source.active;
  exfil.armed = !!source.armed;
  exfil.hot = !!source.hot;
  exfil.sweeps = Number.isFinite(source.sweeps) ? Math.max(0, Math.floor(source.sweeps)) : 0;
  exfil.stress = Number.isFinite(source.stress) ? Math.max(0, Math.floor(source.stress)) : 0;
  exfil.anchor =
    typeof source.anchor === 'string' && source.anchor.trim()
      ? source.anchor.trim()
      : null;
  exfil.alt_anchor =
    typeof source.alt_anchor === 'string' && source.alt_anchor.trim()
      ? source.alt_anchor.trim()
      : null;
  const ttlMinutes = Math.max(0, (Number(source.ttl_min) || 0) + (Number(source.ttl_sec) || 0) / 60);
  exfil.ttl = ttlMinutes;
  return exfil;
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
  const persist = options.persist !== false;
  if (feedback && tax > 0){
    const customMessage = typeof options.toast_message === 'string' ? options.toast_message.trim() : '';
    const toast = customMessage || `Arena: Phase-Strike belastet +${tax} SYS (Kosten ${total})`;
    hud_toast(toast, 'ARENA');
  }
  if (persist && tax > 0){
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
  state.campaign.px_reset_pending = true;
  state.campaign.px_reset_scheduled_at = new Date().toISOString();
  writeLine(`ClusterCreate() aktiv – ${count} Rift-Seeds sichtbar.`);
  return state.campaign.paradoxon_index;
}

function completeMission(summary = {}){
  ensure_campaign();
  const events = [];
  const temp = typeof summary.temp === 'number' ? summary.temp : mission_temp();
  const required = missions_required(temp);
  const missionNumber = Number(state.campaign?.mission);
  const missionInEpisode = Number.isFinite(state.campaign?.mission_in_episode)
    ? Math.max(1, Math.floor(state.campaign.mission_in_episode))
    : Number.isFinite(missionNumber)
      ? ((Math.max(1, Math.floor(missionNumber)) - 1) % 10) + 1
      : null;
  const reasonCandidate = pickString(summary.reason, summary.completed, summary.outcome, summary.status);
  const normalizedReason = typeof reasonCandidate === 'string' ? reasonCandidate.trim().toLowerCase() : '';
  const abortedToken =
    typeof summary.aborted === 'string' ? summary.aborted.trim().toLowerCase() : '';
  const abortedFlag = asBoolean(summary.aborted) === true || abortedToken === 'aborted' || abortedToken === 'abort';
  const stabilizedFlag = asBoolean(summary.stabilized);
  const successFlag = asBoolean(summary.success);
  const completedFlag = asBoolean(summary.completed);
  const patzerFlag = normalizedReason === 'patzer' || normalizedReason === 'kritischer patzer';
  let missionEndReason = 'completed';
  if (abortedFlag || normalizedReason === 'aborted'){
    missionEndReason = 'aborted';
  } else if (successFlag === false || normalizedReason === 'failed'){
    missionEndReason = 'failed';
  } else if (normalizedReason === 'stabilized' || normalizedReason === 'completed'){
    missionEndReason = 'completed';
  }
  const stabilized =
    stabilizedFlag === true ||
    successFlag === true ||
    completedFlag === true ||
    normalizedReason === 'stabilized' ||
    normalizedReason === 'completed';
  if (!stabilized && (missionEndReason === 'failed' || patzerFlag)){
    const before = clamp(state.campaign.paradoxon_index ?? 0, 0, 5);
    const after = incrementParadoxon(-1);
    state.campaign.missions_since_px = 0;
    const note = patzerFlag ? 'Patzer' : 'Mission fehlgeschlagen';
    events.push(`Kodex: ${note} – Px sinkt auf ${after}/5 (vorher ${before}/5).`);
  }
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
        events.push('Kodex: ClusterCreate() aktiv – neue Rift-Seeds verfügbar. Px-Reset folgt nach Missionsende.');
      }
    }
  }
  const chronoReset = chronopolisProgressAfterMission(summary);
  if (chronoReset === 'episode'){
    events.push('Kodex: Chronopolis-Angebote neu instanziiert – Episode abgeschlossen.');
  } else if (chronoReset === 'mission-cycle'){
    events.push('Kodex: Chronopolis-Angebote rotiert – HQ-Zyklus erreicht.');
  }
  if (missionInEpisode !== null){
    state.campaign.mission_in_episode = missionInEpisode;
    state.campaign.episode_completed = missionInEpisode >= 10;
  }
  const nowIso = new Date().toISOString();
  if (state.logs?.flags){
    const flags = state.logs.flags;
    flags.foreshadow_gate_snapshot = 0;
    flags.foreshadow_gate_progress = 0;
    flags.foreshadow_gate_expected = false;
    flags.last_mission_end_reason = missionEndReason;
    if (
      Number.isFinite(missionNumber) &&
      missionNumber === 5 &&
      (missionEndReason === 'completed' || missionEndReason === 'aborted')
    ){
      set_self_reflection(true, {
        message: 'SF-ON (post-M5 reset)',
        tag: 'SF-ON',
        reason: missionEndReason
      });
      flags.self_reflection_auto_reset_at = nowIso;
      flags.self_reflection_auto_reset_reason = missionEndReason;
    }
  }
  state.campaign.last_mission_end_reason = missionEndReason;
  sync_campaign_exfil(null);
  if (state.campaign.px_reset_pending){
    state.campaign.paradoxon_index = 0;
    state.campaign.px = 0;
    state.campaign.missions_since_px = 0;
    state.campaign.px_reset_pending = false;
    state.campaign.px_reset_confirm = true;
    state.campaign.px_reset_scheduled_at = state.campaign.px_reset_scheduled_at || new Date().toISOString();
    events.push('Kodex: Paradoxon-Index zurückgesetzt – Reset beim nächsten Briefing bestätigen.');
  }
  return {
    events,
    required,
    missions_since_px: state.campaign.missions_since_px ?? 0,
    paradoxon_index: state.campaign.paradoxon_index ?? 0
  };
}

function reset_mission_state(){
  const missionType = resolve_mission_type();
  const missionPhase = missionType === 'rift' ? 'rift' : 'core';
  const sceneTotal = resolve_scene_total(missionType);
  state.exfil = null;
  state.fr_intervention = null;
  state.scene = { index: 0, foreshadows: 0, total: sceneTotal };
  state.phase = missionPhase;
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
  state.campaign ||= {};
  state.campaign.phase = missionPhase;
  state.campaign.scene_total = sceneTotal;
  state.campaign.scene = state.scene.index;
  sync_campaign_exfil(null);
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
  return `Px ${px_bar(n)} (${n}/5) · TEMP ${t} · ETA (Heuristik) +1 in ${eta}`;
}

const px_tracker = render_px_tracker;

function offline_log_entries(){
  return ensure_offline_log();
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
  const offlineLast = typeof flags.offline_help_last_scene === 'string'
    ? flags.offline_help_last_scene.trim()
    : (typeof flags.offline_help_last === 'string' ? flags.offline_help_last.trim() : '');
  if (offlineLast){
    parts.push(`Offline zuletzt ${offlineLast}`);
  }
  if (!parts.length) return null;
  return `Runtime-Flags: ${parts.join(' · ')}`;
}

function asNumber(value){
  if (value === null || value === undefined) return null;
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

const BOOLEAN_TRUE_TOKENS = new Set([
  'true',
  '1',
  'yes',
  'y',
  'ja',
  'j',
  'ok',
  'okay',
  'success',
  'successful',
  'succeeded',
  'stabilized',
  'stabilised',
  'stabilise',
  'completed',
  'complete',
  'done'
]);

const BOOLEAN_FALSE_TOKENS = new Set([
  'false',
  '0',
  'no',
  'n',
  'nein',
  'not',
  'fail',
  'failed',
  'failure',
  'unstable',
  'unstabilized',
  'unstabilised',
  'aborted',
  'abort',
  'cancel',
  'cancelled',
  'canceled'
]);

function asBoolean(value){
  if (value === null || value === undefined) return null;
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number'){
    if (Number.isNaN(value)) return null;
    return value !== 0;
  }
  if (typeof value === 'string'){
    const normalized = value.trim().toLowerCase();
    if (!normalized) return null;
    if (BOOLEAN_TRUE_TOKENS.has(normalized)) return true;
    if (BOOLEAN_FALSE_TOKENS.has(normalized)) return false;
    return null;
  }
  return null;
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

function normalize_risk_level(raw){
  if (typeof raw === 'string'){
    const value = raw.trim().toLowerCase();
    if (!value) return null;
    if (value.includes('low') || value.includes('niedrig')) return 'low';
    if (value.includes('high') || value.includes('hoch')) return 'high';
    if (value.includes('mid') || value.includes('medium') || value.includes('mittel')) return 'mid';
  }
  if (Number.isFinite(raw)){
    if (raw <= 1) return 'low';
    if (raw >= 3) return 'high';
    return 'mid';
  }
  return null;
}

function resolve_risk_level(outcome = {}){
  const candidates = [
    outcome?.risk,
    outcome?.risk_level,
    outcome?.riskLevel,
    outcome?.difficulty,
    outcome?.mission_risk,
    outcome?.mission?.risk,
    state.campaign?.risk,
    state.campaign?.risk_level
  ];
  for (const candidate of candidates){
    const normalized = normalize_risk_level(candidate);
    if (normalized) return normalized;
  }
  return 'mid';
}

function resolve_completion_tier(outcome = {}){
  const boolBonus = outcome?.bonus === true || outcome?.bonus_objectives === true || outcome?.bonusAchieved === true;
  const boolPartial = outcome?.partial === true || outcome?.teil_erfolg === true;
  const boolFail = outcome?.failed === true || outcome?.aborted === true || outcome?.failure === true;
  const candidates = [
    outcome?.result,
    outcome?.status,
    outcome?.outcome,
    outcome?.summary,
    outcome?.mission_result,
    outcome?.mission?.result
  ].map((value) => (typeof value === 'string' ? value.trim().toLowerCase() : ''));
  if (boolBonus || candidates.some((value) => value.includes('bonus') || value.includes('perfect') || value.includes('voll'))){
    return 'bonus';
  }
  if (boolFail || candidates.some((value) => value.includes('fail') || value.includes('aborted') || value.includes('scheiter'))){
    return 'fail';
  }
  if (boolPartial || candidates.some((value) => value.includes('teil') || value.includes('partial'))){
    return 'partial';
  }
  return 'success';
}

function compute_default_cu_reward(outcome = {}){
  const risk = resolve_risk_level(outcome);
  const tier = resolve_completion_tier(outcome);
  const baseMap = { low: 400, mid: 500, high: 600 };
  const base = baseMap[risk] ?? 500;
  const multiplierMap = { partial: 0.6, success: 1.0, bonus: 1.2, fail: 0.3 };
  const multiplier = multiplierMap[tier] ?? 1.0;
  let reward = base * multiplier;
  const teamSize = asNumber(outcome?.team_size ?? outcome?.team?.size ?? state.team?.size ?? state.team?.members?.length);
  if (teamSize !== null && teamSize > 0 && teamSize < 3){
    reward *= 1.5;
  }
  reward = Math.round(reward);
  return reward > 0 ? reward : null;
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
  const computed = compute_default_cu_reward(outcome);
  if (computed !== null) return computed;
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
    const progress = Math.max(
      0,
      asNumber(missionResult?.missions_since_px) ??
        asNumber(state.campaign?.missions_since_px) ??
        0
    );
    const required = Math.max(
      1,
      asNumber(missionResult?.required) ??
        missions_required(asNumber(outcome?.temp) ?? mission_temp())
    );
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
    const amount = normalize_cu(
      payload.amount ??
        payload.share ??
        payload.value ??
        payload.cu ??
        payload.payout ??
        payload.delta ??
        payload.balance
    );
  const weightSource = asNumber(payload.ratio ?? payload.weight ?? payload.share_ratio ?? payload.portion);
  let ratio = null;
  if (weightSource !== null){
    ratio = Math.max(0, weightSource);
  } else {
    const percentSource = asNumber(payload.percent ?? payload.percent_share);
    if (percentSource !== null){
      const normalizedPercent = percentSource > 1 ? percentSource / 100 : percentSource;
      ratio = Math.max(0, normalizedPercent);
    }
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
        label:
          instruction.label ||
          (rosterInfo.indexById.has(id)
            ? rosterInfo.roster[rosterInfo.indexById.get(id)].label
            : id),
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
      record = {
        id,
        label:
          label ||
          (rosterInfo.indexById.has(id)
            ? rosterInfo.roster[rosterInfo.indexById.get(id)].label
            : id),
        amount: 0
      };
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
  const economy = ensure_economy();
  const hazardSource = outcome?.economy?.hazard_pay ?? outcome?.hazard_pay ?? outcome?.economy?.hazard;
  const hazardPay = normalize_cu(hazardSource);
  const lines = [];
  if (hazardPay !== null && hazardPay > 0){
    economy.cu = Math.max(0, Math.round(economy.cu) + hazardPay);
    lines.push(`Hazard-Pay: ${hazardPay} CU priorisiert (HQ-Pool).`);
  }
  const reward = normalize_cu(cuReward);
  if (reward === null || reward <= 0){
    const hqBalance = Math.max(0, Math.round(economy.cu));
    lines.push(`HQ-Pool: ${hqBalance} CU verfügbar.`);
    return { lines, payout: 0, leftover: 0 };
  }
  const rosterInfo = build_wallet_roster();
  const instructions = gather_wallet_instructions(outcome, rosterInfo);
  const { allocations, totalAssigned, leftover } = compute_wallet_allocations(reward, rosterInfo, instructions);
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
  if (allocations.length){
    const summary = allocations.map((entry) => `${entry.label || entry.id} +${entry.amount} CU`).join(' | ');
    lines.push(`Wallet-Split (${allocations.length}×): ${summary}`);
  }
  sync_primary_currency(economy, economy.cu);
  const hqBalance = Math.max(0, Math.round(economy.cu));
  const remainderText = leftover > 0 ? ` (Rest ${leftover} CU im HQ-Pool)` : '';
  lines.push(`HQ-Pool: ${hqBalance} CU verfügbar${remainderText}.`);
  return { lines, payout: totalAssigned, leftover };
}

function initialize_wallets_from_roster(){
  ensure_economy();
  const wallets = wallet_lookup();
  const { roster } = build_wallet_roster();
  let created = 0;
  roster.forEach((entry) => {
    if (!entry || !entry.id) return;
    if (!wallets[entry.id]){
      wallets[entry.id] = { balance: 0, name: entry.label || null };
      created += 1;
    } else if (!wallets[entry.id].name && entry.label){
      wallets[entry.id].name = entry.label;
    }
  });
  if (created > 0){
    hud_toast(`Wallets initialisiert (${created}×)`, 'HQ');
  }
  return created;
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
  arena.phase = typeof arena.phase === 'string' ? arena.phase : (arena.active ? 'active' : 'idle');
  arena.policy_players = Array.isArray(arena.policy_players)
    ? arena.policy_players
        .map((entry) =>
          entry && typeof entry === 'object' ? clone_plain_object(entry) : null
        )
        .filter(Boolean)
    : undefined;
  if (!arena.resume_token || typeof arena.resume_token !== 'object' || Array.isArray(arena.resume_token)){
    arena.resume_token = null;
  }
  apply_arena_rules(state);
  return arena;
}

function build_arena_resume_token(arena){
  if (!arena) return null;
  const scenario =
    arena.scenario && typeof arena.scenario === 'object'
      ? {
          description:
            pickString(arena.scenario.description, arena.scenario.name, arena.scenario.id) || null,
        }
      : null;
  const policyPlayers = Array.isArray(arena.policy_players)
    ? arena.policy_players
        .map((entry) => {
          if (!entry || typeof entry !== 'object') return null;
          const id = pickString(entry.id, entry.player_id);
          if (!id) return null;
          return {
            id: String(id).trim(),
            name: pickString(entry.name, entry.label, entry.callsign) || null,
          };
        })
        .filter(Boolean)
    : [];
  return {
    created_at: new Date().toISOString(),
    scenario,
    team_size:
      Number.isFinite(arena.team_size) && arena.team_size > 0
        ? Math.min(4, Math.floor(arena.team_size))
        : 1,
    mode: typeof arena.mode === 'string' ? arena.mode : 'single',
    previous_mode: typeof arena.previous_mode === 'string' ? arena.previous_mode : null,
    tier:
      Number.isFinite(arena.tier) && arena.tier > 0
        ? Math.min(3, Math.floor(arena.tier))
        : 1,
    fee_paid: Number.isFinite(arena.fee) ? Math.max(0, Math.floor(arena.fee)) : 0,
    audit: Array.isArray(arena.audit) ? arena.audit.slice() : [],
    started_episode: Number.isFinite(arena.started_episode) ? Math.floor(arena.started_episode) : null,
    policy_players: policyPlayers.length ? policyPlayers : undefined,
  };
}

function reset_arena_after_load(){
  const arena = ensure_arena();
  const hadCompleted = arena.phase === 'completed';
  const wasActive =
    !!arena.active || (arena.phase && arena.phase !== 'idle' && arena.phase !== 'completed');
  if (wasActive && !arena.previous_mode){
    arena.previous_mode = typeof arena.mode === 'string' ? arena.mode : null;
  }
  let resume_token = null;
  if (wasActive){
    resume_token = build_arena_resume_token(arena);
    arena.resume_token = resume_token;
  }
  arena.active = false;
  arena.phase = hadCompleted || wasActive ? 'completed' : 'idle';
  arena.phase_strike_tax = 0;
  return { wasActive, resume_token };
}

function apply_arena_rules(ctx = state){
  if (!ctx || typeof ctx !== 'object'){ return null; }
  const arena = ctx.arena;
  if (!arena || typeof arena !== 'object'){ return null; }
  const active = !!arena.active;
  if (!active && arena.phase !== 'completed'){
    arena.phase = 'idle';
  } else if (active){
    arena.phase = arena.phase === 'completed' ? 'completed' : 'active';
  }
  arena.damage_dampener = active && arena.damage_dampener !== false;
  arena.phase_strike_tax = active ? phase_strike_tax(ctx) : 0;
  const markBuffer = target => {
    ensure_psi_buffer_flag(target);
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
  if (!active){
    return arena;
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
      scene_total: Number.isFinite(state.scene?.total) ? state.scene.total : resolve_scene_total()
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
  state.campaign.phase = normalize_phase_value(raw.campaign?.phase, state.campaign.phase);
  const sceneIndex = raw.campaign?.scene ?? state.scene?.index ?? state.campaign.scene;
  const fallbackTotal = Number.isFinite(state.scene?.total) ? state.scene.total : resolve_scene_total();
  const sceneTotalSource = raw.campaign?.scene_total;
  const sceneTotal = Number.isFinite(sceneTotalSource)
    ? Math.max(1, Math.floor(sceneTotalSource))
    : fallbackTotal;
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

function normalize_gear_alias(value){
  if (typeof value !== 'string') return value;
  const normalized = value
    .toLowerCase()
    .replace(/ä/g, 'ae')
    .replace(/ö/g, 'oe')
    .replace(/ü/g, 'ue')
    .replace(/ß/g, 'ss')
    .replace(/[^a-z0-9]+/g, '');
  const mapped = GEAR_ALIAS_MAP[normalized];
  return mapped || value;
}

function normalize_loadout_aliases(loadout){
  const base = loadout && typeof loadout === 'object' ? clone_plain_object(loadout) : {};
  for (const [key, value] of Object.entries(base)){
    if (Array.isArray(value)){
      base[key] = value
        .map(entry => normalize_gear_alias(entry))
        .filter(entry => entry !== undefined && entry !== null && entry !== '');
    } else if (value && typeof value === 'object'){
      base[key] = normalize_loadout_aliases(value);
    } else {
      base[key] = normalize_gear_alias(value);
    }
  }
  return base;
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
  return (
    ARENA_TIER_RULES.find(
      (rule) => highestLevel >= rule.minLevel && highestLevel <= rule.maxLevel
    ) || ARENA_TIER_RULES[0]
  );
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
  for (const key of ECONOMY_PRIMARY_KEYS){
    if (!(key in economy)) continue;
    const normalized = normalize_primary_currency(economy[key]);
    if (normalized !== null){
      return { key, value: normalized };
    }
  }
  const synced = sync_primary_currency(economy);
  return { key: 'credits', value: synced };
}

function writeArenaCurrency(key, value){
  const economy = ensure_economy();
  const normalized = normalize_primary_currency(value);
  const amount = normalized === null ? 0 : normalized;
  economy[key] = amount;
  sync_primary_currency(economy, amount);
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

function arenaResume(){
  ensure_campaign();
  const arena = ensure_arena();
  if (arena.active){
    return 'Arena läuft bereits.';
  }
  const token = arena.resume_token;
  if (!token || typeof token !== 'object'){
    return 'Kein Arena-Resume-Token vorhanden.';
  }
  const teamSize =
    Number.isFinite(token.team_size) && token.team_size > 0
      ? Math.min(Math.floor(token.team_size), 6)
      : 1;
  const mode = typeof token.mode === 'string' ? token.mode : 'single';
  const tier =
    Number.isFinite(token.tier) && token.tier > 0 ? Math.min(Math.floor(token.tier), 3) : 1;
  const policyPlayers = Array.isArray(token.policy_players)
    ? token.policy_players
        .map((entry) => (entry && typeof entry === 'object' ? clone_plain_object(entry) : null))
        .filter(Boolean)
    : arena.policy_players || [];
  const scenario =
    token.scenario && typeof token.scenario === 'object'
      ? {
          description:
            pickString(token.scenario.description, token.scenario.name, token.scenario.id) ||
            'Arena-Szenario',
        }
      : nextArenaScenario();
  const audit = Array.isArray(token.audit) ? token.audit.slice() : [];
  const previousMode =
    typeof token.previous_mode === 'string'
      ? token.previous_mode
      : typeof state.campaign?.mode === 'string'
      ? state.campaign.mode
      : null;
  const currentEpisode = state.campaign?.episode ?? token.started_episode ?? null;
  arena.active = true;
  arena.phase = 'active';
  arena.wins_player = 0;
  arena.wins_opponent = 0;
  arena.tier = tier;
  arena.proc_budget = Number.isFinite(arena.proc_budget) ? arena.proc_budget : 0;
  arena.artifact_limit = Number.isFinite(arena.artifact_limit) ? arena.artifact_limit : 0;
  arena.loadout_budget = Number.isFinite(arena.loadout_budget) ? arena.loadout_budget : 0;
  arena.audit = audit;
  arena.fee = Number.isFinite(token.fee_paid) ? Math.max(0, Math.floor(token.fee_paid)) : 0;
  arena.scenario = scenario;
  arena.damage_dampener = true;
  arena.team_size = teamSize;
  arena.mode = mode;
  arena.previous_mode = previousMode;
  arena.policy_players = policyPlayers;
  arena.started_episode = currentEpisode;
  delete arena.resume_token;
  state.campaign.mode = 'pvp';
  apply_arena_rules();
  ensure_runtime_flags().arena_active = true;
  state.location = 'ARENA';
  const pxLocked =
    arena.last_reward_episode !== null && arena.last_reward_episode === currentEpisode;
  const pxNote = pxLocked ? 'Px-Bonus dieser Episode bereits verbraucht' : 'Px-Bonus verfügbar';
  const baseMessage = `Arena Resume · Tier ${arena.tier}`;
  hud_toast(`${baseMessage} · ${pxNote}`, 'ARENA');
  if (audit.length){
    hud_toast(`Arena-Audit reaktiviert: ${audit.length} Hinweise.`, 'ARENA');
  }
  return `${baseMessage} · ${scenario.description} · ${pxNote}`;
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
  const teamSize = Number.isFinite(parsedSize) && parsedSize > 0 ? Math.min(Math.max(parsedSize, 1), 4) : 1;
  const mode = typeof options.mode === 'string' ? options.mode.toLowerCase() : 'single';
  const scenario = nextArenaScenario();
  writeArenaCurrency(key, value - fee);
  const currentEpisode = state.campaign?.episode ?? null;
  const previousMode = typeof state.campaign?.mode === 'string' ? state.campaign.mode : null;
  arena.active = true;
  arena.phase = 'active';
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
    arena.last_reward_episode !== null && arena.last_reward_episode === currentEpisode;
  const pxNote = pxLocked ? 'Px-Bonus dieser Episode bereits verbraucht' : 'Px-Bonus verfügbar';
  const baseMessage = `Arena initiiert · Tier ${tierRule.tier} · Gebühr ${fee} CU`;
  hud_toast(`${baseMessage} · ${pxNote}`, 'ARENA');
  if (audit.length){
    hud_toast(`Arena-Loadout angepasst: ${audit.length} Eingriffe.`, 'ARENA');
  }
  record_trace('arena_start', {
    hud: baseMessage,
    channel: 'ARENA',
    arena: { scenario: scenario?.description || null, tier: tierRule.tier, team_size: teamSize },
    note: pxNote
  });
  return `${baseMessage} · ${scenario.description} · ${pxNote}`;
}

function arenaScore(){
  const arena = ensure_arena();
  const pxLocked =
    arena.last_reward_episode !== null &&
    arena.last_reward_episode === (state.campaign?.episode ?? null);
  const pxNote = pxLocked ? 'Px-Bonus bereits vergeben' : 'Px-Bonus offen';
  const scenario = arena.scenario?.description || 'n/a';
  const summary =
    `Arena-Score ${arena.wins_player}:${arena.wins_opponent} · Tier ${arena.tier} · ` +
    `Team ${arena.team_size} · ${pxNote}`;
  return `${summary} · Szenario ${scenario}`;
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
  arena.phase = 'completed';
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
  if (sub === 'resume'){
    return arenaResume();
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
  const help = [
    '!arena start [team <n>] [mode <name>]',
    '!arena resume',
    '!arena result win|loss',
    '!arena score',
    '!arena exit'
  ].join(' · ');
  return `Arena-Befehle: ${help}`;
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
  return (
    `Chronopolis-Tick · Episoden → immer · Missionen → ${missionInfo} · Fortschritt ` +
    `${progress}/${modulo || '–'} · Letzter Reset ${reason} @ ${when}`
  );
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

function acknowledge_chronopolis_warning(){
  ensure_logs();
  state.logs.flags.chronopolis_warn_seen = true;
  ensure_campaign();
  state.campaign.chronopolis_warn_seen = true;
  hud_toast('Chronopolis-Warnung quittiert – Stadtbriefing aktiv.', 'CITY');
  return 'Chronopolis-Warnung quittiert.';
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

function resolve_mission_type(){
  const campaignType = typeof state.campaign?.type === 'string'
    ? state.campaign.type.trim().toLowerCase()
    : '';
  if (campaignType === 'rift' || campaignType === 'core'){
    return campaignType;
  }
  const campaignPhase = typeof state.campaign?.phase === 'string'
    ? state.campaign.phase.trim().toLowerCase()
    : '';
  if (campaignPhase === 'rift' || campaignPhase === 'core'){
    return campaignPhase;
  }
  const currentPhase = typeof state.phase === 'string' ? state.phase.trim().toLowerCase() : '';
  if (currentPhase === 'rift' || currentPhase === 'core'){
    return currentPhase;
  }
  return 'core';
}

function find_open_rift_seed(seedId = null){
  const seeds = ensure_rift_seeds();
  if (!seeds.length) return null;
  if (seedId && typeof seedId === 'string'){
    const target = seedId.trim().toLowerCase();
    const match = seeds.find((seed) =>
      seed?.id && seed.id.toLowerCase() === target && seed.status !== 'closed'
    );
    if (match) return match;
  }
  return seeds.find((seed) => seed && seed.status !== 'closed') || null;
}

function can_launch_rift(seedId = null){
  const location = typeof state.location === 'string' ? state.location.trim().toUpperCase() : 'HQ';
  if (location !== 'HQ'){
    return { ok: false, reason: 'Rift-Start nur im HQ erlaubt.' };
  }
  const arenaActive = !!state.arena?.active;
  if (arenaActive){
    return { ok: false, reason: 'Arena aktiv – Rift-Start blockiert.' };
  }
  const episodeDone = state.campaign?.episode_completed === true;
  const missionInEpisode = Number(state.campaign?.mission_in_episode);
  const episodeReady = episodeDone || (Number.isFinite(missionInEpisode) && missionInEpisode >= 10);
  if (!episodeReady){
    return { ok: false, reason: 'Rift-Start blockiert – erst nach Episodenende im HQ.' };
  }
  const seed = find_open_rift_seed(seedId);
  if (!seed){
    return { ok: false, reason: 'Keine offenen Rift-Seeds verfügbar.' };
  }
  return { ok: true, seed };
}

function resolve_scene_total(missionType = resolve_mission_type()){
  const storedTotal = Number(state.campaign?.scene_total);
  if (Number.isFinite(storedTotal) && storedTotal > 0){
    return Math.max(1, Math.floor(storedTotal));
  }
  const sceneTotal = Number(state.scene?.total);
  if (Number.isFinite(sceneTotal) && sceneTotal > 0){
    return Math.max(1, Math.floor(sceneTotal));
  }
  return missionType === 'rift' ? 14 : 12;
}

function resolve_boss_dr(teamSize, bossTier){
  const size = Number.isFinite(teamSize) ? Math.min(4, Math.max(1, Math.floor(teamSize))) : 1;
  const tier = bossTier === 'mini' ? 'mini' : 'arc';
  if (size <= 2){
    return tier === 'mini' ? 1 : 2;
  }
  if (size <= 4){
    return tier === 'mini' ? 2 : 3;
  }
  return tier === 'mini' ? 3 : 4;
}

function StartMission(){
  ensure_campaign();
  const missionType = resolve_mission_type();
  const missionPhase = missionType === 'rift' ? 'rift' : 'core';
  const sceneTotal = resolve_scene_total(missionType);
  state.phase = missionPhase;
  state.campaign ||= {};
  state.campaign.phase = missionPhase;
  state.campaign.scene_total = sceneTotal;
  state.comms = { jammed: false, relays: 0, rangeMod: 1.0 };
  state.exfil = {
    sweeps: 0,
    stress: 0,
    ttl_min: 8,
    ttl_sec: 0,
    active: false,
    armed: false,
    anchor: null,
    alt_anchor: null
  };
  sync_campaign_exfil(state.exfil);
  const hudLog = ensure_logs();
  hudLog.length = 0;
  const foreshadowLog = foreshadow_entries();
  foreshadowLog.length = 0;
  ensure_character();
  ensure_team();
  ensure_party();
  const flags = state.logs.flags;
  const teamSize = resolve_team_size();
  const missionNumber = Number(state.campaign?.mission);
  const missionInEpisode = Number(state.campaign?.mission_in_episode);
  state.campaign.team_size = teamSize;
  const gateProgress = Number.isFinite(flags.foreshadow_gate_progress)
    ? Math.max(0, Math.floor(flags.foreshadow_gate_progress))
    : 0;
  const m5Or10 = Number.isFinite(missionNumber) && (missionNumber === 5 || missionNumber === 10);
  const gateStartValue = m5Or10
    ? FORESHADOW_GATE_REQUIRED
    : gateProgress;
  flags.foreshadow_gate_snapshot = Math.min(FORESHADOW_GATE_REQUIRED, gateStartValue);
  flags.foreshadow_gate_progress = 0;
  const mission = ensure_mission();
  mission.clock = mission.clock && typeof mission.clock === 'object' ? mission.clock : {};
  mission.timers = Array.isArray(mission.timers) ? mission.timers : [];
  state.fr_intervention = roll_fr(state.campaign?.fr_bias || 'normal');
  state.scene = { index: 0, foreshadows: 0, total: sceneTotal };
  state.campaign.scene = state.scene.index;
  const runtimeFlags = ensure_runtime_flags();
  if (runtimeFlags.skip_entry_choice !== true){
    runtimeFlags.skip_entry_choice = false;
  }
  if (state.campaign?.px_reset_confirm){
    hud_toast('Paradoxon-Reset abgeschlossen – Px 0/5.', 'PX');
    delete state.campaign.px_reset_confirm;
    delete state.campaign.px_reset_scheduled_at;
  }
  if (Number.isFinite(missionNumber) && (missionNumber === 5 || missionNumber === 10)){
    state.logs.flags.foreshadow_gate_expected = true;
    if (missionNumber === 5){
      state.logs.flags.foreshadow_gate_m5_seen = true;
    }
    if (missionNumber === 10){
      state.logs.flags.foreshadow_gate_m10_seen = true;
    }
    const fsRequired = foreshadow_requirement();
    const gateBadge = `GATE ${FORESHADOW_GATE_REQUIRED}/${FORESHADOW_GATE_REQUIRED}`;
    const fsBadge = `FS 0/${fsRequired}`;
    hud_tag(gateBadge);
    hud_toast(`${gateBadge} · ${fsBadge}`, 'BOSS');
  }
  if (Number.isFinite(missionInEpisode) && missionInEpisode <= 1){
    state.campaign.episode_completed = false;
  }
  if (Number.isFinite(missionNumber) && missionNumber >= 6 && !self_reflection_enabled()){
    set_self_reflection(true);
    state.logs.flags.self_reflection_auto_reset_at = new Date().toISOString();
  }
  let bossToast = null;
  let bossDrToast = null;
  let bossDrValue = null;
  if (Number.isFinite(missionNumber) && missionNumber >= 5){
    if (missionNumber % 10 === 0){
      bossToast = 'Boss-Finale in Szene 10 – DR aktiv.';
      bossDrValue = resolve_boss_dr(teamSize, 'arc');
    } else if (missionNumber % 5 === 0){
      bossToast = 'Mini-Boss in Szene 10 – Overflow halbiert.';
      bossDrValue = resolve_boss_dr(teamSize, 'mini');
    }
  }
  if (bossDrValue !== null){
    state.campaign.boss_dr = bossDrValue;
    bossDrToast = `Boss-DR aktiviert – −${bossDrValue} Schaden pro Treffer`;
  } else if (state.campaign && 'boss_dr' in state.campaign){
    delete state.campaign.boss_dr;
  }
  const overlay = scene_overlay();
  writeLine(overlay);
  if (bossToast){
    hud_toast(bossToast, 'BOSS');
  }
  if (bossDrToast){
    hud_toast(bossDrToast, 'BOSS');
  }
  record_trace('mission_start', {
    hud: overlay,
    channel: 'HUD',
    note: bossDrToast || bossToast || null,
    seed: {
      id: state.campaign?.active_seed_id || state.campaign?.seed_id || null,
      tier: state.campaign?.active_seed_tier || null,
      label: state.campaign?.active_seed_label || null,
      status: state.campaign?.type === 'rift' ? 'open' : null
    }
  });
  return overlay;
}

function scene_overlay(scene){
  const s = scene || state.scene;
  const ep = state.campaign?.episode ?? 0;
  const ms = state.campaign?.mission ?? 0;
  const sc = s.index ?? 0;
  const total = Number.isFinite(s.total) ? s.total : resolve_scene_total();
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
  const gateInfo = gate_progress_info(state);
  if (gateInfo.expected || gateInfo.value > 0){
    h += ` · GATE ${gateInfo.value}/${FORESHADOW_GATE_REQUIRED}`;
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

function normalize_comms_payload(input){
  const source = input && typeof input === 'object' ? input : {};
  const normalized = { ...source };
  const rawDevice = pickString(
    source.device,
    source.Device,
    source.DEVICE
  );
  let device = rawDevice ? rawDevice.toString().trim() : '';
  if (device){
    const canonical = device.toLowerCase().replace(/\s+/g, '_');
    const map = {
      comlink: 'comlink',
      commlink: 'comlink',
      'com-link': 'comlink',
      kabel: 'cable',
      cable: 'cable',
      relay: 'relay',
      relais: 'relay',
      jammer: 'jammer_override',
      jammeroverride: 'jammer_override',
      'jammer-override': 'jammer_override',
      jammer_override: 'jammer_override'
    };
    device = map[canonical] || canonical;
  } else {
    device = null;
  }
  const rangeCandidates = [
    source.range_m,
    source.rangeM,
    source.range,
    source.rangeMeters,
    source.range_meters,
    source.distance
  ];
  let range = pickNumber(...rangeCandidates);
  if (range === null){
    const km = pickNumber(
      source.range_km,
      source.rangeKm,
      source.rangeKilometers,
      source.range_kilometers
    );
    if (km !== null){
      range = km * 1000;
    }
  }
  if (range !== null){
    range = Number(range);
    if (!Number.isFinite(range)){
      range = null;
    }
  }
  const relaysCandidate = pickNumber(source.relays, source.relay_count);
  const jammerCandidate = source.jammer ?? source.jammed ?? null;
  normalized.device = device;
  normalized.range_m = range;
  if (normalized.range === undefined && range !== null){
    normalized.range = range;
  }
  normalized.relays = relaysCandidate !== null ? Math.max(0, relaysCandidate) : (source.relays === true ? 1 : 0);
  if (jammerCandidate !== null){
    normalized.jammer = !!jammerCandidate;
  }
  return normalized;
}

function comms_check(deviceOrOptions, maybeRange){
  const normalized = typeof deviceOrOptions === 'object' && deviceOrOptions !== null
    ? normalize_comms_payload(deviceOrOptions)
    : normalize_comms_payload({ device: deviceOrOptions, range_m: maybeRange });
  const device = normalized.device;
  const range = normalized.range_m;
  const okDev = ['comlink', 'cable', 'relay', 'jammer_override'].includes(device);
  const rangeFactor = state.comms?.rangeMod ?? 1;
  const okRng = Number.isFinite(range) && (range * rangeFactor) > 0;
  const jammed = normalized.jammer ?? !!state.comms?.jammed;
  const hasRelay = device === 'relay' || (Number.isFinite(normalized.relays) && normalized.relays > 0);
  const ok = okDev && okRng && (
    !jammed || device === 'cable' || device === 'jammer_override' || hasRelay
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

function offline_scene_marker(){
  const location = state.location || null;
  const sceneIndex = Number.isFinite(state.scene?.index) ? state.scene.index : null;
  const sceneTotal = Number.isFinite(state.scene?.total) ? state.scene.total : null;
  const episode = Number.isFinite(state.campaign?.episode) ? state.campaign.episode : null;
  const mission = Number.isFinite(state.campaign?.mission_in_episode)
    ? state.campaign.mission_in_episode
    : Number.isFinite(state.campaign?.mission)
      ? state.campaign.mission
      : null;
  const parts = [];
  if (location) parts.push(location);
  if (episode !== null && mission !== null){
    parts.push(`EP${episode}-MS${mission}`);
  } else if (sceneIndex !== null && sceneTotal !== null){
    parts.push(`SC${sceneIndex}/${sceneTotal}`);
  } else if (sceneIndex !== null){
    parts.push(`SC${sceneIndex}`);
  }
  return parts.join(':') || null;
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
  const nowIso = new Date(now).toISOString();
  flags.offline_help_last = nowIso;
  flags.offline_help_last_scene = offline_scene_marker() || nowIso;
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
    'Kodex-Uplink getrennt – Mission läuft weiter mit HUD-Lokaldaten. ' +
      '!offline zeigt das Feldprotokoll bis zum HQ-Re-Sync.'
  );
}

function must_comms(o){
  const normalized = normalize_comms_payload(o);
  if (!comms_check(normalized)){
    throw new Error(
      'CommsCheck failed: require valid device/range or relay/jammer override. ' +
      'Tipp: Terminal suchen / Comlink koppeln / Kabel/Relay nutzen / ' +
      'Jammer-Override aktivieren; Reichweite anpassen. ' +
      'Mission läuft weiter mit HUD-Lokaldaten – !offline listet das Feldprotokoll.'
    );
  }
  return normalized;
}

function radio_tx(o){
  const normalized = must_comms(o);
  const ctx = { ...state, comms: { ...state.comms, device: normalized.device, range_m: normalized.range_m } };
  require_uplink(ctx, 'radio_tx');
  return 'tx';
}

function radio_rx(o){
  const normalized = must_comms(o);
  const ctx = { ...state, comms: { ...state.comms, device: normalized.device, range_m: normalized.range_m } };
  require_uplink(ctx, 'radio_rx');
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
  const campaignTeamSize = asNumber(base.team_size);
  base.team_size = Number.isFinite(campaignTeamSize)
    ? Math.min(4, Math.max(1, Math.floor(campaignTeamSize)))
    : null;
  const bossDr = Number(base.boss_dr);
  base.boss_dr = Number.isFinite(bossDr) && bossDr > 0 ? Math.floor(bossDr) : 0;
  base.px_reset_pending = !!base.px_reset_pending;
  base.px_reset_confirm = !!base.px_reset_confirm;
  if (typeof base.px_reset_scheduled_at !== 'string'){
    base.px_reset_scheduled_at = null;
  }
  base.compliance_shown_today = !!base.compliance_shown_today;
  const exfilSource = base.exfil && typeof base.exfil === 'object' ? base.exfil : {};
  base.exfil = {
    active: !!exfilSource.active,
    armed: !!exfilSource.armed,
    hot: !!exfilSource.hot,
    sweeps: Number.isFinite(exfilSource.sweeps) ? Math.max(0, Math.floor(exfilSource.sweeps)) : 0,
    stress: Number.isFinite(exfilSource.stress) ? Math.max(0, Math.floor(exfilSource.stress)) : 0,
    anchor:
      typeof exfilSource.anchor === 'string' && exfilSource.anchor.trim()
        ? exfilSource.anchor.trim()
        : null,
    alt_anchor:
      typeof exfilSource.alt_anchor === 'string' && exfilSource.alt_anchor.trim()
        ? exfilSource.alt_anchor.trim()
        : null,
    ttl: Number.isFinite(exfilSource.ttl) ? Math.max(0, Number(exfilSource.ttl)) : 0
  };
  return base;
}

function prepare_save_arena(arena){
  const source = clone_plain_object(arena);
  const active = !!source.active;
  const normalized = {
    active,
    phase: typeof source.phase === 'string' && source.phase.trim()
      ? source.phase.trim()
      : active
      ? 'active'
      : 'idle',
    mode: typeof source.mode === 'string' && source.mode.trim() ? source.mode.trim() : 'single',
    previous_mode: typeof source.previous_mode === 'string' && source.previous_mode.trim()
      ? source.previous_mode.trim()
      : null,
    team_size: Number.isFinite(source.team_size) ? Math.max(1, Math.min(4, Math.floor(source.team_size))) : 1,
    tier: Number.isFinite(source.tier) ? Math.max(1, Math.floor(source.tier)) : 1,
    proc_budget: Number.isFinite(source.proc_budget) ? Math.max(0, Math.floor(source.proc_budget)) : 0,
    artifact_limit: Number.isFinite(source.artifact_limit) ? Math.max(0, Math.floor(source.artifact_limit)) : 0,
    loadout_budget: Number.isFinite(source.loadout_budget) ? Math.max(0, Math.floor(source.loadout_budget)) : 0,
    wins_player: Number.isFinite(source.wins_player) ? Math.max(0, Math.floor(source.wins_player)) : 0,
    wins_opponent: Number.isFinite(source.wins_opponent) ? Math.max(0, Math.floor(source.wins_opponent)) : 0,
    fee: Number.isFinite(source.fee) ? Math.max(0, Math.floor(source.fee)) : 0,
    phase_strike_tax: Number.isFinite(source.phase_strike_tax) ? Math.max(0, Math.floor(source.phase_strike_tax)) : 0,
    damage_dampener: source.damage_dampener !== false,
    started_episode: Number.isFinite(source.started_episode) ? Math.floor(source.started_episode) : null,
    last_reward_episode: Number.isFinite(source.last_reward_episode)
      ? Math.floor(source.last_reward_episode)
      : null,
    scenario: source.scenario && typeof source.scenario === 'object'
      ? clone_plain_object(source.scenario)
      : (typeof source.scenario === 'string' ? source.scenario : null),
    audit: Array.isArray(source.audit)
      ? source.audit
          .map((entry) =>
            entry && typeof entry === 'object' ? clone_plain_object(entry) : entry
          )
          .filter(Boolean)
      : [],
    policy_players: Array.isArray(source.policy_players)
      ? source.policy_players
          .map((entry) =>
            entry && typeof entry === 'object' ? clone_plain_object(entry) : entry
          )
          .filter(Boolean)
      : []
  };
  return normalized;
}

function prepare_save_economy(economy){
  const base = clone_plain_object(economy);
  const primary = sync_primary_currency(base);
  base.cu = primary;
  base.credits = primary;
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
  if (!Array.isArray(base.foreshadow)){
    base.foreshadow = [];
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
  if (Array.isArray(base.psi)){
    base.psi = sanitize_psi_entries(base.psi);
  } else {
    base.psi = [];
  }
  if (Array.isArray(base.arena_psi)){
    base.arena_psi = sanitize_arena_psi_entries(base.arena_psi);
  } else {
    base.arena_psi = [];
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
  if (Array.isArray(base.field_notes)){
    base.field_notes = base.field_notes
      .map((entry) => {
        if (!entry) return null;
        if (typeof entry === 'string'){
          const note = entry.trim();
          return note ? { note } : null;
        }
        if (typeof entry !== 'object' || Array.isArray(entry)) return null;
        const record = clone_plain_object(entry);
        const agentId = typeof record.agent_id === 'string' && record.agent_id.trim()
          ? record.agent_id.trim()
          : null;
        const mission = typeof record.mission === 'string' && record.mission.trim()
          ? record.mission.trim()
          : null;
        const timestamp = typeof record.timestamp === 'string' && record.timestamp.trim()
          ? record.timestamp.trim()
          : null;
        const note = typeof record.note === 'string' && record.note.trim()
          ? record.note.trim()
          : (typeof record.text === 'string' ? record.text.trim() : null);
        if (!note && !mission && !agentId && !timestamp) return null;
        const normalized = {};
        if (agentId) normalized.agent_id = agentId;
        if (mission) normalized.mission = mission;
        if (timestamp) normalized.timestamp = timestamp;
        if (note) normalized.note = note;
        return normalized;
      })
      .filter(Boolean);
  } else {
    base.field_notes = [];
  }
  if (!base.flags || typeof base.flags !== 'object'){
    base.flags = {};
  }
  if (!base.flags.runtime_version){
    base.flags.runtime_version = ZR_VERSION;
  }
  base.flags.compliance_shown_today = !!base.flags.compliance_shown_today;
  base.flags.chronopolis_warn_seen = !!base.flags.chronopolis_warn_seen;
  const offlineLastScene = typeof base.flags.offline_help_last_scene === 'string'
    ? base.flags.offline_help_last_scene.trim()
    : null;
  const offlineLast = typeof base.flags.offline_help_last === 'string'
    ? base.flags.offline_help_last.trim()
    : null;
  base.flags.offline_help_last_scene = offlineLastScene || offlineLast || null;
  base.flags.offline_help_last = base.flags.offline_help_last_scene;
  const offlineCount = Number(base.flags.offline_help_count);
  base.flags.offline_help_count = Number.isFinite(offlineCount) && offlineCount > 0
    ? Math.floor(offlineCount)
    : 0;
  base.flags.merge_conflicts = sanitize_merge_conflicts(base.flags.merge_conflicts);
  base.flags.self_reflection = base.flags.self_reflection !== false;
  base.flags.self_reflection_off = !!base.flags.self_reflection_off;
  base.flags.self_reflection_changed_at = typeof base.flags.self_reflection_changed_at === 'string'
    ? base.flags.self_reflection_changed_at
    : null;
  base.flags.self_reflection_last_change_reason = typeof base.flags.self_reflection_last_change_reason === 'string'
    ? base.flags.self_reflection_last_change_reason.trim() || null
    : null;
  base.flags.self_reflection_auto_reset_at = typeof base.flags.self_reflection_auto_reset_at === 'string'
    ? base.flags.self_reflection_auto_reset_at
    : null;
  base.flags.self_reflection_auto_reset_reason = typeof base.flags.self_reflection_auto_reset_reason === 'string'
    ? base.flags.self_reflection_auto_reset_reason.trim() || null
    : null;
  base.flags.last_mission_end_reason = typeof base.flags.last_mission_end_reason === 'string'
    ? base.flags.last_mission_end_reason.trim() || null
    : null;
  const gateProgress = Number(base.flags.foreshadow_gate_progress);
  base.flags.foreshadow_gate_progress = Number.isFinite(gateProgress) && gateProgress > 0
    ? Math.min(FORESHADOW_GATE_REQUIRED, Math.max(0, Math.floor(gateProgress)))
    : 0;
  const gateSnapshot = Number(base.flags.foreshadow_gate_snapshot);
  base.flags.foreshadow_gate_snapshot = Number.isFinite(gateSnapshot) && gateSnapshot > 0
    ? Math.min(FORESHADOW_GATE_REQUIRED, Math.max(0, Math.floor(gateSnapshot)))
    : 0;
  base.flags.foreshadow_gate_expected = !!base.flags.foreshadow_gate_expected
    || base.flags.foreshadow_gate_progress > 0
    || base.flags.foreshadow_gate_snapshot > 0;
  base.flags.foreshadow_gate_m5_seen = !!base.flags.foreshadow_gate_m5_seen;
  base.flags.foreshadow_gate_m10_seen = !!base.flags.foreshadow_gate_m10_seen;
  return base;
}

function prepare_save_arc_dashboard(dashboard){
  const base = dashboard && typeof dashboard === 'object' && !Array.isArray(dashboard)
    ? clone_plain_object(dashboard)
    : {};
  base.offene_seeds = Array.isArray(base.offene_seeds)
    ? base.offene_seeds
        .map((entry) => {
          if (entry && typeof entry === 'object'){
            return clone_plain_object(entry);
          }
          if (typeof entry === 'string'){
            const trimmed = entry.trim();
            return trimmed ? trimmed : null;
          }
          return null;
        })
        .filter(entry => entry !== null)
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
        const last = normalize_intervention_entry(
          record.last_intervention,
          record.last_intervention?.timestamp,
          { fillDefaults: false }
        );
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
  if (Array.isArray(base.timeline)){
    base.timeline = base.timeline
      .map((entry) => {
        if (!entry || typeof entry !== 'object' || Array.isArray(entry)) return null;
        const record = clone_plain_object(entry);
        const id = typeof record.id === 'string' && record.id.trim() ? record.id.trim() : null;
        const epoch = typeof record.epoch === 'string' && record.epoch.trim()
          ? record.epoch.trim()
          : null;
        const label = typeof record.label === 'string' && record.label.trim()
          ? record.label.trim()
          : null;
        if (!id && !epoch && !label) return null;
        const normalized = {};
        if (id) normalized.id = id;
        if (epoch) normalized.epoch = epoch;
        if (label) normalized.label = label;
        return normalized;
      })
      .filter(Boolean);
  } else {
    base.timeline = [];
  }
  return base;
}

function prepare_save_ui(ui){
  const base = clone_plain_object(ui);
  base.gm_style = typeof base.gm_style === 'string' ? base.gm_style : 'verbose';
  base.intro_seen = !!base.intro_seen;
  base.suggest_mode = !!base.suggest_mode;
  const contrast = typeof base.contrast === 'string' ? base.contrast.trim().toLowerCase() : '';
  base.contrast = ['standard', 'high'].includes(contrast) ? contrast : 'standard';
  base.badge_density = normalize_badge_density(base.badge_density);
  const pace = typeof base.output_pace === 'string' ? base.output_pace.trim().toLowerCase() : '';
  base.output_pace = ['slow', 'normal', 'fast'].includes(pace) ? pace : 'normal';
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
  const sysMaxRaw = Number(attrs.SYS_max);
  const sysMax = Number.isFinite(sysMaxRaw) ? sysMaxRaw : 0;
  const sysInstalledRaw = Number(
    Number.isFinite(attrs.SYS_installed) ? attrs.SYS_installed : attrs.SYS_used
  );
  const sysInstalled = Number.isFinite(sysInstalledRaw) ? sysInstalledRaw : sysMax;
  const sysRuntimeRaw = Number(
    Number.isFinite(attrs.SYS_runtime) ? attrs.SYS_runtime : sysInstalled
  );
  const sysRuntime = Number.isFinite(sysRuntimeRaw) ? sysRuntimeRaw : sysInstalled;
  attrs.SYS_max = sysMax;
  attrs.SYS_installed = clamp(sysInstalled, 0, sysMax);
  attrs.SYS_runtime = clamp(sysRuntime, 0, attrs.SYS_installed);
  attrs.SYS_used = attrs.SYS_installed;
  base.attributes = attrs;
  if (base.quarters && typeof base.quarters === 'object' && !Array.isArray(base.quarters)){
    const quarters = clone_plain_object(base.quarters);
    quarters.id = typeof quarters.id === 'string' && quarters.id.trim() ? quarters.id.trim() : null;
    const preset = typeof quarters.preset === 'string' ? quarters.preset.trim() : '';
    quarters.preset = preset || 'custom';
    quarters.deck = typeof quarters.deck === 'string' && quarters.deck.trim()
      ? quarters.deck.trim()
      : null;
    quarters.notes = typeof quarters.notes === 'string' && quarters.notes.trim()
      ? quarters.notes.trim()
      : null;
    quarters.layout_tags = Array.isArray(quarters.layout_tags)
      ? quarters.layout_tags
          .map((tag) => (typeof tag === 'string' ? tag.trim() : null))
          .filter(Boolean)
      : [];
    base.quarters = quarters;
  }
  return base;
}

function prepare_save_team(team){
  const base = clone_plain_object(team);
  if (Array.isArray(team?.members)){
    base.members = team.members.map(member => {
      const clone = clone_plain_object(member);
      if (clone.loadout){
        clone.loadout = normalize_loadout_aliases(clone.loadout);
      }
      return clone;
    });
  } else if (!Array.isArray(base.members)){
    base.members = [];
  }
  return base;
}

function prepare_save_loadout(loadout){
  return normalize_loadout_aliases(loadout);
}

function prepare_save_party(party, team){
  const sourceParty = party && typeof party === 'object' ? party : {};
  const base = clone_plain_object(sourceParty);
  const fallback = Array.isArray(base.characters) && base.characters.length
    ? base.characters
    : Array.isArray(team?.members)
    ? team.members
    : [];
  base.characters = fallback.map(member => {
    const clone = clone_plain_object(member);
    if (clone.loadout){
      clone.loadout = normalize_loadout_aliases(clone.loadout);
    }
    return clone;
  });
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

function enforce_required_save_fields(payload){
  for (const path of SAVE_REQUIRED_PATHS){
    assert_save_field(payload, path);
  }
}

function toast_save_block(reason){
  const trimmed = typeof reason === 'string' ? reason.trim() : '';
  return trimmed
    ? `SaveGuard: ${trimmed} – HQ-Save gesperrt.`
    : 'SaveGuard: HQ-Save gesperrt.';
}

function select_state_for_save(s){
  const ui = prepare_save_ui({ ...ensure_ui(), ...clone_plain_object(s.ui) });
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
    ui,
    arena: prepare_save_arena(s.arena),
    arc_dashboard: prepare_save_arc_dashboard(s.arc_dashboard)
  };
  enforce_required_save_fields(payload);
  return payload;
}

function save_deep(s=state){
  const arenaState = s?.arena;
  if (arenaState?.active || (arenaState && arenaState.phase && arenaState.phase !== 'idle' && arenaState.phase !== 'completed')){
    throw new Error(toast_save_block('Arena aktiv'));
  }
  if (s.location !== 'HQ') throw new Error(toast_save_block('HQ-only'));
  if (s?.exfil?.active || s?.campaign?.exfil?.active){
    throw new Error(toast_save_block('Exfil aktiv'));
  }
  const c = s.character || {};
  const a = c.attributes || {};
  const sysMax = Number.isFinite(a.SYS_max) ? Number(a.SYS_max) : 0;
  const sysInstalled = Number.isFinite(a.SYS_installed)
    ? Number(a.SYS_installed)
    : Number.isFinite(a.SYS_used)
      ? Number(a.SYS_used)
      : sysMax;
  const sysRuntime = Number.isFinite(a.SYS_runtime)
    ? Number(a.SYS_runtime)
    : sysInstalled;
  if (c.stress !== 0) throw new Error('SaveGuard: stress > 0.');
  if ((c.psi_heat ?? 0) !== 0) throw new Error('SaveGuard: Psi-Heat > 0.');
  if (sysInstalled > sysMax) throw new Error('SaveGuard: SYS overflow.');
  if (sysRuntime > sysInstalled) throw new Error('SaveGuard: SYS runtime overflow.');
  if (sysInstalled !== sysMax){
    throw new Error('SaveGuard: SYS nicht voll installiert.');
  }
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
    data.phase = normalize_phase_value(data.phase, 'core');
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
  data.phase = normalize_phase_value(data.phase, 'core');
  if (data.campaign && typeof data.campaign === 'object'){
    data.campaign.phase = normalize_phase_value(data.campaign.phase, data.phase);
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
  data.arena = prepare_save_arena(data.arena);
  return data;
}

function hydrate_state(data){
  state.location = data.location || 'HQ';
  state.phase = normalize_phase_value(data.phase, 'core');
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
  state.loadout = normalize_loadout_aliases(data.loadout);
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
  sync_compliance_flags();
  sync_foreshadow_progress();
  ensure_arc_dashboard();
  ensure_initiative();
  ensure_hud_state();
  state.flags = data.flags && typeof data.flags === 'object' ? JSON.parse(JSON.stringify(data.flags)) : { runtime: {} };
  ensure_runtime_flags();
  state.roll = { open: false };
  state.arena = data.arena && typeof data.arena === 'object' ? { ...data.arena } : {};
  ensure_arena();
  state.ui = prepare_save_ui(data.ui);
  ensure_ui();
  state.party = data.party && typeof data.party === 'object' ? JSON.parse(JSON.stringify(data.party)) : {};
  const party = ensure_party();
  const roster = Array.isArray(party.characters) ? party.characters.map(entry => clone_plain_object(entry)) : [];
  const normalizedRoster = roster.map(entry => {
    const clone = clone_plain_object(entry);
    if (clone.loadout){
      clone.loadout = normalize_loadout_aliases(clone.loadout);
    }
    return clone;
  });
  party.characters = normalizedRoster.map(entry => clone_plain_object(entry));
  const team = ensure_team();
  team.members = normalizedRoster.map(entry => clone_plain_object(entry));
  if (Array.isArray(team.roster)){
    team.roster = normalizedRoster.map(entry => clone_plain_object(entry));
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
  assignAttributeNumber('SYS_installed', 'sys_installed');
  assignAttributeNumber('SYS_runtime', 'sys_runtime');
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
    throw new Error(
      `Kodex-Archiv: Datensatz v${saveSemver} nicht kompatibel mit v${runtimeSemver}. ` +
        'Bitte HQ-Migration veranlassen.'
    );
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
  const migratedOfflineLastScene = typeof migrated.logs.flags.offline_help_last_scene === 'string'
    ? migrated.logs.flags.offline_help_last_scene.trim()
    : null;
  const migratedOfflineLast = typeof migrated.logs.flags.offline_help_last === 'string'
    ? migrated.logs.flags.offline_help_last.trim()
    : null;
  migrated.logs.flags.offline_help_last_scene = migratedOfflineLastScene || migratedOfflineLast || null;
  migrated.logs.flags.offline_help_last = migrated.logs.flags.offline_help_last_scene;
  const migratedOfflineCount = Number(migrated.logs.flags.offline_help_count);
  migrated.logs.flags.offline_help_count = Number.isFinite(migratedOfflineCount) && migratedOfflineCount > 0
    ? Math.floor(migratedOfflineCount)
    : 0;
  if (
    migrated.campaign &&
    typeof migrated.campaign === 'object' &&
    typeof migrated.campaign.compliance_shown_today !== 'boolean'
  ){
    migrated.campaign.compliance_shown_today = !!migrated.logs.flags.compliance_shown_today;
  }
  migrated.location = 'HQ';
  hydrate_state(migrated);
  ensure_rift_seeds();
  const arenaReset = reset_arena_after_load();
  initialize_wallets_from_roster();
  ensure_runtime_flags().skip_entry_choice = true;
  show_compliance_once();
  const hud = scene_overlay();
  writeLine(hud);
  if (arenaReset.wasActive){
    writeLine('Arena-Zustand auf HQ zurückgesetzt.');
    if (arenaReset.resume_token){
      writeLine('Arena-Resume-Token gesichert: Serie kann aus dem HQ fortgesetzt werden.');
    }
  }
  return { status: 'ok', state, hud };
}

function startSolo(mode='klassisch'){
  ensure_ui();
  ensure_campaign();
  const normalizedSeed = campaign_mode();
  state.start = { type: 'solo', mode, seed_mode: normalizedSeed };
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
  state.logs.flags.self_reflection = true;
  state.logs.flags.foreshadow_gate_progress = 0;
  state.logs.flags.foreshadow_gate_snapshot = 0;
  state.logs.flags.foreshadow_gate_expected = false;
  state.campaign.compliance_shown_today = false;
  state.campaign.mode = normalizedSeed;
  state.campaign.seed_source = normalizedSeed;
  ensure_runtime_flags().skip_entry_choice = false;
  sync_compliance_flags();
  play_hq_intro();
  return normalizedSeed === 'preserve' ? `solo-${mode}` : `solo-${normalizedSeed}-${mode}`;
}

function setupNpcTeam(size=0){
  state.team = { size };
  initialize_wallets_from_roster();
  record_npc_autoradio(size, state.campaign?.mode || 'preserve');
}

function startGroup(mode='klassisch'){
  ensure_ui();
  ensure_campaign();
  const normalizedSeed = campaign_mode();
  state.start = { type: 'gruppe', mode, seed_mode: normalizedSeed };
  state.location = 'HQ';
  state.team = { size: 0 };
  ensure_logs();
  state.logs.flags.compliance_shown_today = false;
  state.logs.flags.chronopolis_warn_seen = false;
  state.logs.flags.self_reflection = true;
  state.logs.flags.foreshadow_gate_progress = 0;
  state.logs.flags.foreshadow_gate_snapshot = 0;
  state.logs.flags.foreshadow_gate_expected = false;
  state.campaign.compliance_shown_today = false;
  state.campaign.mode = normalizedSeed;
  state.campaign.seed_source = normalizedSeed;
  ensure_runtime_flags().skip_entry_choice = false;
  sync_compliance_flags();
  initialize_wallets_from_roster();
  play_hq_intro();
  return normalizedSeed === 'preserve' ? `gruppe-${mode}` : `gruppe-${normalizedSeed}-${mode}`;
}

function set_campaign_mode_command(raw){
  const normalized = typeof raw === 'string' ? raw.trim().toLowerCase() : '';
  if (!['preserve', 'trigger'].includes(normalized)){
    return 'Kampagnenmodus setzen: `!kampagnenmodus preserve|trigger`.';
  }
  ensure_campaign();
  state.campaign.mode = normalized;
  state.campaign.seed_source = normalized;
  return `Kampagnenmodus gesetzt: ${normalized.toUpperCase()} (persistiert im HQ-Save).`;
}

function launch_mission(){
  state.phase = 'transfer';
  StartMission();
  return 'mission-launched';
}

function launch_rift(seedId = null){
  const check = can_launch_rift(seedId);
  if (!check.ok){
    throw new Error(check.reason);
  }
  const seed = check.seed;
  ensure_campaign();
  state.campaign.type = 'rift';
  state.campaign.phase = 'rift';
  state.phase = 'transfer';
  state.campaign.seed_source = 'rift';
  state.campaign.active_seed_id = seed?.id ?? null;
  state.campaign.active_seed_label = seed?.label ?? null;
  if (seed?.seed_tier){
    state.campaign.active_seed_tier = seed.seed_tier;
  }
  if (Number.isFinite(seed?.epoch)){
    state.campaign.epoch = seed.epoch;
  }
  record_trace('rift_launch', {
    channel: 'RIFT',
    hud: seed?.label ? `Rift ${seed.id}: ${seed.label}` : null,
    seed: {
      id: seed?.id || null,
      label: seed?.label || null,
      tier: seed?.seed_tier || null,
      status: seed?.status || 'open'
    }
  });
  return launch_mission();
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
    if ((m = cmd.match(/^spiel starten\s*\(npc-team\s+([0-9]+)/))){
      const size = parseInt(m[1], 10);
      if (Number.isFinite(size) && size > 4){
        return 'Teamgrößen: 0–4. Bitte erneut eingeben (z. B. npc-team 3).';
      }
    }
    if (cmd.match(/^spiel starten\s*\(gruppe\s+\d/)){
      return 'Bei gruppe keine Zahl angeben. (klassisch/schnell sind erlaubt)';
    }
    if ((m = cmd.match(/^spiel starten\s*\(solo([^)]*)\)$/))){
      const options = m[1] ? m[1].trim().split(/\s+/).filter(Boolean) : [];
      let mode = 'klassisch';
      let legacySeed = null;
      options.forEach((token) => {
        if (token === 'schnell' || token === 'fast') mode = 'schnell';
        if (token === 'klassisch' || token === 'classic') mode = 'klassisch';
        if (token === 'trigger' || token === 'preserve') legacySeed = token;
      });
      if (legacySeed){
        return 'Startsyntax aktualisiert: Kampagnenmodus im HQ setzen (z. B. `!kampagnenmodus trigger`). ' +
          'In den Start-Klammern nur `klassisch` oder `schnell` nutzen.';
      }
      return startSolo(mode);
    }
    if ((m = cmd.match(/^spiel starten\s*\(npc-team([^)]*)\)$/))){
      const options = m[1] ? m[1].trim().split(/\s+/).filter(Boolean) : [];
      let size = 0;
      let mode = 'klassisch';
      let legacySeed = null;
      options.forEach((token) => {
        if (/^[0-9]+$/.test(token)){
          const parsed = parseInt(token, 10);
          if (Number.isFinite(parsed)){
            size = parsed;
          }
        } else if (token === 'schnell' || token === 'fast'){
          mode = 'schnell';
        } else if (token === 'klassisch' || token === 'classic'){
          mode = 'klassisch';
        } else if (token === 'trigger' || token === 'preserve'){
          legacySeed = token;
        }
      });
      if (legacySeed){
        return 'Kampagnenmodus wird nicht mehr im Startbefehl gesetzt. Nutze `!kampagnenmodus preserve|trigger` ' +
          'im HQ und wiederhole den Start mit `klassisch` oder `schnell`.';
      }
      if (size > 4){
        return 'Teamgrößen: 0–4. Bitte erneut eingeben (z. B. npc-team 3).';
      }
      startSolo(mode);
      setupNpcTeam(size);
      state.start.type = 'npc-team';
      state.start.seed_mode = campaign_mode();
      return `npc-team-${mode}`;
    }
    if ((m = cmd.match(/^spiel starten\s*\(gruppe([^)]*)\)$/))){
      const options = m[1] ? m[1].trim().split(/\s+/).filter(Boolean) : [];
      let mode = 'klassisch';
      let legacySeed = null;
      options.forEach((token) => {
        if (token === 'schnell' || token === 'fast') mode = 'schnell';
        if (token === 'klassisch' || token === 'classic') mode = 'klassisch';
        if (token === 'trigger' || token === 'preserve') legacySeed = token;
      });
      if (legacySeed){
        return 'Kampagnenmodus separat setzen: `!kampagnenmodus preserve|trigger`. ' +
          'Start-Klammern verwenden nur `klassisch` oder `schnell`.';
      }
      return startGroup(mode);
    }
    if (cmd === '!kampagnenmodus' || cmd.startsWith('!kampagnenmodus ') || cmd === '!campaign-mode'){
      const tokens = command.trim().split(/\s+/);
      const choice = tokens[1];
      return set_campaign_mode_command(choice);
    }
    if (cmd === '!helper delay'){
      return helper_delay_text();
    }
    if (cmd === '!helper comms'){
      return helper_comms_text();
    }
    if (cmd === '!helper boss'){
      return helper_boss_text();
    }
    if (cmd === '!help start' || cmd === '/help start'){
        return [
          'Startbefehle:',
          '- Vor jedem Einsatz: !radio clear und !alias clear ausführen, damit Funk- und Alias-Logs frisch sind.',
          '- Spiel starten (solo [klassisch|schnell])',
          '- Spiel starten (npc-team [0–4] [klassisch|schnell])',
          '- Spiel starten (gruppe [klassisch|schnell])',
          '- Spiel laden',
          'Kampagnenmodus separat setzen: !kampagnenmodus preserve|trigger (persistiert im Save).',
          'Klammern sind Pflicht. Rollen-Kurzformen: infil/tech/face/cqb/psi.',
          'Speichern nur im HQ. Px 5 ⇒ ClusterCreate() (Rift-Seeds nach Episodenende).'
        ].join('\n');
      }
    if (cmd === '!offline' || cmd === '!help offline' || cmd === '/help offline' || cmd === 'offline hilfe'){
        return offline_help('command');
      }
    if (cmd === '!accessibility' || cmd === '!accessibility status' || cmd === '/help accessibility'){
      return accessibility_status();
    }
    if (cmd.startsWith('!accessibility ')){
      const parts = cmd.split(/\s+/);
      if (parts.length < 3){
        return 'Syntax: `!accessibility <contrast|badges|pace> <wert>`';
      }
      try {
        return set_accessibility_option(parts[1], parts[2]);
      } catch (err){
        return err.message;
      }
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
    if (cmd === '!chronopolis ack' || cmd === '!chronopolis warn ack'){
      return acknowledge_chronopolis_warning();
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
  record_trace,
  ensure_rift_seeds,
  can_launch_rift,
  startSolo,
  setupNpcTeam,
  startGroup,
  jam_now,
  launch_mission,
  launch_rift,
  chronopolisStockReport,
  chronopolisTickStatus,
  acknowledge_chronopolis_warning,
  suspend_snapshot,
  resume_snapshot,
  resolveSuspendPath,
  campaign_mode,
  is_pvp,
  phase_strike_tax,
  phase_strike_cost,
  apply_arena_rules,
  apply_wallet_split,
  getArenaFee,
  arenaResume,
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
