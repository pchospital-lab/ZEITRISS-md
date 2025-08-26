const rt = require('../runtime');
const assert = require('assert');

rt.on_command('spiel starten (solo) schnell');
assert.equal(rt.state.start.type, 'solo');
assert.equal(rt.state.start.mode, 'schnell');

rt.on_command('spiel starten (npc-team)');
assert.equal(rt.state.start.type, 'npc-team');

rt.on_command('spiel starten (gruppe) klassisch');
assert.equal(rt.state.start.type, 'gruppe');
console.log('start-ok');
