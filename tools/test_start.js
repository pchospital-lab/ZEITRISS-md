const rt = require('../runtime');
const assert = require('assert');

let response = rt.on_command('spiel starten (solo trigger schnell)');
assert.strictEqual(response, 'solo-trigger-schnell');
assert.strictEqual(rt.state.start.type, 'solo');
assert.strictEqual(rt.state.start.mode, 'schnell');
assert.strictEqual(rt.state.start.seed_mode, 'trigger');
assert.strictEqual(rt.state.campaign.mode, 'trigger');
assert.strictEqual(rt.state.campaign.seed_source, 'trigger');
assert.strictEqual(rt.state.flags.runtime.skip_entry_choice, false);
assert.strictEqual(rt.state.logs.flags.chronopolis_warn_seen, false);

response = rt.on_command('Spiel starten (npc-team 3 trigger classic)');
assert.strictEqual(response, 'npc-team-trigger-klassisch');
assert.strictEqual(rt.state.start.type, 'npc-team');
assert.strictEqual(rt.state.start.mode, 'klassisch');
assert.strictEqual(rt.state.start.seed_mode, 'trigger');
assert.strictEqual(rt.state.campaign.mode, 'trigger');
assert.strictEqual(rt.state.campaign.seed_source, 'trigger');
assert.strictEqual(rt.state.team.size, 3);

let error = rt.on_command('spiel starten (npc-team 5)');
assert.strictEqual(error, 'Teamgröße erlaubt: 0–4. Bitte erneut eingeben (z. B. `npc-team 3`).');
assert.strictEqual(rt.state.start.type, 'npc-team');
assert.strictEqual(rt.state.team.size, 3);

error = rt.on_command('spiel starten (gruppe 3)');
assert.strictEqual(error, 'Bei *gruppe* keine Zahl angeben. (klassisch/schnell sind erlaubt)');
assert.strictEqual(rt.state.start.type, 'npc-team');

response = rt.on_command('spiel starten (gruppe trigger fast)');
assert.strictEqual(response, 'gruppe-trigger-schnell');
assert.strictEqual(rt.state.start.type, 'gruppe');
assert.strictEqual(rt.state.start.mode, 'schnell');
assert.strictEqual(rt.state.start.seed_mode, 'trigger');
assert.strictEqual(rt.state.campaign.mode, 'trigger');
assert.strictEqual(rt.state.campaign.seed_source, 'trigger');

const help = rt.on_command('!help start');
assert(help.includes('[preserve|trigger]'));

rt.on_command('begin mission');
assert.notEqual(rt.state.exfil, null);

console.log('start-ok');
