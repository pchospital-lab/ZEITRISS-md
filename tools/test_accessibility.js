const assert = require('assert');
const rt = require('../runtime');

function setupState(){
  rt.state.location = 'HQ';
  rt.state.phase = 'core';
  rt.state.campaign = { paradoxon_index: 0 };
  rt.state.character = {
    id: 'CHR-ACCESS',
    stress: 0,
    psi_heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_used: 1 }
  };
  rt.state.team = {};
  rt.state.party = { characters: [] };
  rt.state.loadout = {};
  rt.state.economy = { cu: 0, wallets: {} };
  rt.state.logs = {
    hud: [],
    foreshadow: [],
    artifact_log: [],
    kodex: [],
    offline: [],
    market: [],
    squad_radio: [],
    alias_trace: [],
    fr_interventions: [],
    flags: {}
  };
  rt.state.arena = { active: false };
  rt.state.flags = { runtime: {} };
}

setupState();
let status = rt.on_command('!accessibility');
assert(status.includes('Accessibility-Panel'));

rt.on_command('!accessibility contrast high');
rt.on_command('!accessibility badges compact');
rt.on_command('!accessibility pace slow');

assert.strictEqual(rt.state.ui.contrast, 'high');
assert.strictEqual(rt.state.ui.badge_density, 'compact');
assert.strictEqual(rt.state.ui.output_pace, 'slow');

const savedJson = rt.save_deep(rt.state);
const saved = JSON.parse(savedJson);
assert.strictEqual(saved.ui.contrast, 'high');
assert.strictEqual(saved.ui.badge_density, 'compact');
assert.strictEqual(saved.ui.output_pace, 'slow');

rt.load_deep(savedJson);
assert.strictEqual(rt.state.ui.contrast, 'high');
assert.strictEqual(rt.state.ui.badge_density, 'compact');
assert.strictEqual(rt.state.ui.output_pace, 'slow');

console.log('accessibility-ok');
