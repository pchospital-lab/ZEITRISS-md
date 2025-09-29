const assert = require('assert');
const rt = require('../runtime');

rt.StartMission();

assert.ok(Array.isArray(rt.state.logs.hud), 'HUD-Log initialisiert');
assert.strictEqual(rt.state.logs.hud.length, 0, 'HUD-Log geleert');

const arm = rt.on_command('!exfil arm NEON-1');
assert.ok(arm.includes('NEON-1'), 'Anchor gesetzt');
assert.strictEqual(rt.state.exfil.anchor, 'NEON-1');
assert.strictEqual(rt.state.exfil.armed, true);

const alt = rt.on_command('!exfil alt LUMEN-2');
assert.ok(alt.includes('LUMEN-2'), 'Alt-Anchor gemeldet');
assert.strictEqual(rt.state.exfil.alt_anchor, 'LUMEN-2');

const tick = rt.on_command('!exfil tick 07:45');
assert.strictEqual(tick, 'RW 07:45');
assert.strictEqual(rt.state.exfil.ttl_min, 7);
assert.strictEqual(rt.state.exfil.ttl_sec, 45);

const status = rt.on_command('!exfil status');
assert.ok(status.includes('armiert'), 'Status meldet Armierung');

const hudLog = rt.state.logs.hud;
assert.strictEqual(hudLog.length, 3, 'Drei HUD-Einträge erwartet');
assert.ok(hudLog[0].message.includes('Exfil armiert'));
assert.ok(hudLog[1].message.includes('Alt-Anchor'));
assert.ok(hudLog[2].message.includes('RW 07:45'));

console.log('HUD-Exfil-Test erfolgreich.');
