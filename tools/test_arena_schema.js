const assert = require('assert');
const rt = require('../runtime');

function setupState(){
  rt.state.location = 'HQ';
  rt.state.phase = 'core';
  rt.state.campaign = { paradoxon_index: 0 };
  rt.state.character = {
    id: 'CHR-ARENA-SCHEMA',
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
rt.state.arena = {
  active: false,
  phase: 'completed',
  queue_state: 'idle',
  mode: 'team',
  match_policy: 'lore',
  previous_mode: 'single',
  team_size: 4,
  tier: 3,
  proc_budget: 2,
  artifact_limit: 1,
  loadout_budget: 3,
  wins_player: 2,
  wins_opponent: 1,
  fee: 450,
  phase_strike_tax: 1,
  damage_dampener: true,
  started_episode: 7,
  last_reward_episode: 6,
  scenario: { id: 'phase-strike', map: 'Spire' },
  audit: [{ id: 'AUD-1', result: 'win' }],
  policy_players: [
    { id: 'ghost', role: 'lead' },
    { id: 'nova', role: 'scout' }
  ]
};

const savedJson = rt.save_deep(rt.state);
const saved = JSON.parse(savedJson);
const arena = saved.arena;
assert.strictEqual(arena.active, false);
assert.strictEqual(arena.phase, 'completed');
assert.strictEqual(arena.mode, 'team');
assert.strictEqual(arena.match_policy, 'lore');
assert.strictEqual(arena.previous_mode, 'single');
assert.strictEqual(arena.team_size, 4);
assert.strictEqual(arena.policy_players.length, 2);
assert.strictEqual(arena.audit[0].id, 'AUD-1');

rt.load_deep(savedJson);
assert.strictEqual(rt.state.arena.active, false);
assert.strictEqual(rt.state.arena.phase, 'completed');
assert.strictEqual(rt.state.arena.match_policy, 'lore');
assert.strictEqual(rt.state.arena.previous_mode, 'single');
assert.strictEqual(Array.isArray(rt.state.arena.policy_players), true);
assert.strictEqual(rt.state.arena.policy_players.length, 2);

console.log('arena-schema-ok');
