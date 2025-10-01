const assert = require('assert');
const rt = require('../runtime');

function resetArena(){
  rt.state.character = {
    id: 'CHR-ARENA',
    name: 'Arena Lead',
    lvl: 8,
    rank: 'Lead',
    stress: 0,
    psi_heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 5, SYS_used: 5 }
  };
  rt.state.loadout = {
    support: ['Drohne', 'Medkit'],
    artifacts: ['Relikt-Speer'],
    gear: ['Temporales Schild']
  };
  rt.state.team = { stress: 0, psi_heat: 0, status: 'ready', cooldowns: {} };
  rt.state.campaign = {
    id: 'ARC-ARENA',
    episode: 2,
    scene: 0,
    phase: 'core',
    paradoxon_index: 1,
    missions_since_px: 0
  };
  rt.state.scene = { index: 0, foreshadows: 0, total: 12 };
  rt.state.economy = { credits: 6000 };
  rt.state.arena = { active: false, wins_player: 0, wins_opponent: 0, last_reward_episode: null };
  rt.state.flags = { runtime: {} };
  rt.state.location = 'HQ';
}

resetArena();
const startingCredits = rt.state.economy.credits;
const expectedFee = rt.getArenaFee(startingCredits);
let msg = rt.on_command('!arena start team 2');
assert.ok(/Arena initiiert/.test(msg));
assert.strictEqual(rt.state.arena.active, true);
assert.strictEqual(rt.state.arena.tier, 2);
assert.strictEqual(rt.state.economy.credits, startingCredits - expectedFee);
msg = rt.on_command('!arena score');
assert.ok(/0:0/.test(msg));
rt.on_command('!arena result win');
rt.on_command('!arena result win');
assert.strictEqual(rt.state.arena.wins_player, 2);
const pxBefore = rt.state.campaign.paradoxon_index;
msg = rt.on_command('!arena exit');
assert.ok(/Px-Bonus \+1/.test(msg));
assert.strictEqual(rt.state.campaign.paradoxon_index, pxBefore + 1);
assert.strictEqual(rt.state.arena.active, false);

// Start second run in gleicher Episode
const creditsBeforeSecond = rt.state.economy.credits;
const expectedFeeSecond = rt.getArenaFee(creditsBeforeSecond);
msg = rt.on_command('!arena start team 2');
assert.ok(/Arena initiiert/.test(msg));
rt.on_command('!arena result win');
rt.on_command('!arena result win');
const pxAfterFirst = rt.state.campaign.paradoxon_index;
msg = rt.on_command('!arena exit');
assert.ok(/Px-Bonus bereits vergeben/.test(msg));
assert.strictEqual(rt.state.campaign.paradoxon_index, pxAfterFirst);
assert.strictEqual(rt.state.economy.credits, creditsBeforeSecond - expectedFeeSecond);

console.log('arena-ok');
