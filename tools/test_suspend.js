const fs = require('fs');
const assert = require('assert');
const rt = require('../runtime');

function resetBaseline(){
  rt.state.character = {
    id: 'CHR-SUS',
    name: 'Suspend Tester',
    lvl: 5,
    stress: 0,
    psi_heat: 0,
    self_reflection: true,
    cooldowns: { tk: 1 },
    attributes: { SYS_max: 4, SYS_used: 4 }
  };
  rt.state.campaign = {
    id: 'ARC-SUS',
    episode: 4,
    scene: 3,
    phase: 'core',
    paradoxon_index: 0,
    missions_since_px: 0
  };
  rt.state.scene = { index: 3, foreshadows: 1, total: 12 };
  rt.state.mission = {
    id: 'MSN-SUS',
    objective: 'Snapshot prüfen',
    clock: { segments: 6, filled: 2 },
    timers: [{ id: 'bomb', value: 3 }]
  };
  rt.state.team = {
    stress: 2,
    psi_heat: 1,
    status: 'ready',
    cooldowns: { tk: 1 }
  };
  rt.state.exfil = {
    active: false,
    armed: false,
    sweeps: 0,
    stress: 0,
    ttl_min: 7,
    ttl_sec: 15,
    anchor: 'ALPHA',
    alt_anchor: null
  };
  rt.state.roll = { open: false };
  rt.state.flags = { runtime: { some_flag: true } };
  rt.state.arena.active = false;
  rt.state.initiative = {
    order: ['CHR-SUS', { id: 'EN-01', label: 'Sentinel', remaining: 2 }],
    active_id: 'CHR-SUS'
  };
  rt.state.hud = {
    timers: [
      { id: 'bomb', label: 'Sprengsatz', remaining: 3, total: 5 },
      'Fallback Timer'
    ]
  };
}

function cleanupSnapshot(){
  const file = rt.resolveSuspendPath();
  if (fs.existsSync(file)){
    fs.unlinkSync(file);
  }
}

resetBaseline();
cleanupSnapshot();

// 1. Suspend and force expiry
let msg = rt.on_command('!suspend');
assert.ok(/Suspend-Snapshot aktiv/.test(msg));
let path = rt.resolveSuspendPath();
assert.ok(fs.existsSync(path));
let data = JSON.parse(fs.readFileSync(path, 'utf8'));
data.expires_at = new Date(Date.now() - 1).toISOString();
fs.writeFileSync(path, JSON.stringify(data, null, 2));
msg = rt.on_command('!resume');
assert.ok(/Suspend-Fenster verstrichen/.test(msg));
assert.ok(!fs.existsSync(path));

// 2. Suspend again and resume successfully
resetBaseline();
cleanupSnapshot();
msg = rt.on_command('!suspend');
assert.ok(/Suspend-Snapshot aktiv/.test(msg));
path = rt.resolveSuspendPath();
assert.ok(fs.existsSync(path));
const snapshot = JSON.parse(fs.readFileSync(path, 'utf8'));
// Mutate live state to verify restore
rt.state.scene.index = 1;
rt.state.team.stress = 0;
rt.state.mission.clock = {};
rt.state.flags.runtime.some_flag = false;
rt.state.initiative.order = [];
rt.state.initiative.active_id = null;
rt.state.hud.timers = [];
msg = rt.on_command('!resume');
assert.ok(/Suspend-Snapshot geladen/.test(msg));
assert.strictEqual(rt.state.scene.index, snapshot.campaign.scene);
assert.strictEqual(rt.state.team.stress, snapshot.team.stress);
assert.strictEqual(rt.state.flags.runtime.some_flag, true);
assert.deepStrictEqual(rt.state.initiative.order, snapshot.initiative.order);
assert.strictEqual(rt.state.initiative.active_id, snapshot.initiative.active_id);
assert.deepStrictEqual(rt.state.hud.timers, snapshot.hud.timers);
assert.ok(!fs.existsSync(path));

// 3. Double resume fails gracefully
msg = rt.on_command('!resume');
assert.ok(/Kein Suspend-Snapshot/.test(msg));

console.log('suspend-ok');
