const rt = require('../runtime');
const assert = require('assert');

rt.on_command('spiel starten (solo) fast');
assert.equal(rt.state.start.type, 'solo');
assert.equal(rt.state.start.mode, 'schnell');
assert.equal(rt.state.exfil, null);

rt.on_command('Spiel starten (npc-team) 3 classic');
assert.equal(rt.state.start.type, 'npc-team');
assert.equal(rt.state.team.size, 3);
assert.equal(rt.state.start.mode, 'klassisch');
assert.equal(rt.state.exfil, null);

rt.on_command('spiel starten (GRUPPE) fast');
assert.equal(rt.state.start.type, 'gruppe');
assert.equal(rt.state.start.mode, 'schnell');
assert.equal(rt.state.exfil, null);

rt.on_command('spiel starten (gruppe) 3');
assert.equal(rt.state.start.type, 'gruppe');
assert.equal(rt.state.team.size, 0);

rt.on_command('spiel starten (npc-team) 9');
assert.equal(rt.state.start.type, 'gruppe');
assert.equal(rt.state.team.size, 0);

const help = rt.on_command('!help start');
assert(help.includes('Spiel starten (solo)'));

rt.on_command('begin mission');
assert.notEqual(rt.state.exfil, null);

console.log('start-ok');
