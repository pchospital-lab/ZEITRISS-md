const rt = require('../runtime');
const assert = require('assert');

// Start-Mission: Atmosphere-Contract greift und HUD-Usage wird zurückgesetzt.
rt.state.logs = { flags: { hud_scene_usage: { 2: { count: 3, tags: { HUD: 3 } } } } };
rt.state.ui = {
  gm_style: 'verbose',
  intro_seen: true,
  suggest_mode: false,
  contrast: 'standard',
  badge_density: 'standard',
  output_pace: 'normal',
  voice_profile: 'second_person'
};
rt.state.character = { modes: ['legacy_mode'] };
rt.state.campaign = {};

rt.on_command('spiel starten (solo schnell)');
rt.on_command('begin mission');

assert.deepStrictEqual(rt.state.logs.flags.hud_scene_usage, {
  0: { count: 1, tags: { ENTRY: 1 }, limit: 2 }
});
const startContract = rt.state.logs.flags.atmosphere_contract;
assert.strictEqual(startContract.voice_profile, 'gm_third_person');
assert.deepStrictEqual(startContract.default_modes, ['mission_focus', 'covert_ops_technoir']);
assert.ok(startContract.banned_terms.includes('holodeck'));
console.log('atmosphere-contract-start-ok');

// Load-Pfad: Voice-Lock und Mode-Preset werden normalisiert.
const legacySave = {
  save_version: 6,
  location: 'HQ',
  phase: 'core',
  campaign: { px: 0 },
  character: {
    id: 'LEG-1',
    stress: 0,
    psi_heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_installed: 1, SYS_runtime: 1, SYS_used: 1 },
    modes: ['stealth']
  },
  loadout: {},
  economy: { wallets: {} },
  logs: {
    hud: [],
    trace: [],
    foreshadow: [],
    artifact_log: [],
    market: [],
    offline: [],
    kodex: [],
    alias_trace: [],
    squad_radio: [],
    fr_interventions: [],
    arena_psi: [],
    psi: [],
    flags: { hud_scene_usage: { 1: { count: 1, tags: { HUD: 1 } } } }
  },
  ui: {
    gm_style: 'precision',
    intro_seen: true,
    suggest_mode: false,
    contrast: 'standard',
    badge_density: 'standard',
    output_pace: 'normal'
  },
  hud: {},
  arena: {}
};

const loadResult = rt.load_deep(legacySave);
assert.strictEqual(loadResult.status, 'ok');
assert.strictEqual(rt.state.ui.voice_profile, 'gm_third_person');
assert.deepStrictEqual(rt.state.character.modes, ['mission_focus', 'covert_ops_technoir', 'stealth']);
assert.deepStrictEqual(rt.state.logs.flags.hud_scene_usage, {});
const loadContract = rt.state.logs.flags.atmosphere_contract;
assert.strictEqual(loadContract.voice_profile, 'gm_third_person');
assert.deepStrictEqual(loadContract.default_modes, rt.state.character.modes);
assert.ok(loadContract.banned_terms.includes('matrix'));
console.log('atmosphere-contract-load-ok');
