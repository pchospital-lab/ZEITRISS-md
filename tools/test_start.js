const rt = require('../runtime');
const assert = require('assert');

rt.on_command('spiel starten (solo) schnell');
assert.equal(rt.state.start.type, 'solo');
assert.equal(rt.state.start.mode, 'schnell');
assert.equal(rt.state.exfil, null);

rt.on_command('Spiel starten (npc-team) 3');
assert.equal(rt.state.start.type, 'npc-team');
assert.equal(rt.state.team.size, 3);
assert.equal(rt.state.exfil, null);

rt.on_command('spiel starten (GRUPPE) klassisch');
assert.equal(rt.state.start.type, 'gruppe');
assert.equal(rt.state.exfil, null);

rt.on_command('begin mission');
assert.notEqual(rt.state.exfil, null);

console.log('start-ok');
