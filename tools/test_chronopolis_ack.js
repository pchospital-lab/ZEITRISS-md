const assert = require('assert');
const rt = require('../runtime');

function setupState(){
  rt.state.location = 'HQ';
  rt.state.phase = 'core';
  rt.state.campaign = { paradoxon_index: 0 };
  rt.state.character = {
    id: 'CHR-CHRONO',
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

assert.strictEqual(rt.state.logs.flags.chronopolis_warn_seen || false, false);
const msg = rt.on_command('!chronopolis ack');
assert.strictEqual(msg, 'Chronopolis-Warnung quittiert.');
assert.strictEqual(rt.state.logs.flags.chronopolis_warn_seen, true);
assert.strictEqual(rt.state.campaign.chronopolis_warn_seen, true);

const savedJson = rt.save_deep(rt.state);
const saved = JSON.parse(savedJson);
assert.strictEqual(saved.logs.flags.chronopolis_warn_seen, true);
assert.strictEqual(saved.campaign.chronopolis_warn_seen, true);

rt.load_deep(savedJson);
assert.strictEqual(rt.state.logs.flags.chronopolis_warn_seen, true);
assert.strictEqual(rt.state.campaign.chronopolis_warn_seen, true);

console.log('chronopolis-ack-ok');
