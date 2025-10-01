const assert = require('assert');
const rt = require('../runtime');

rt.StartMission();
let overlay = rt.scene_overlay({ index: 0 });
assert(!overlay.includes('TK🌀'), 'Cooldown-Icon darf nicht gesetzt sein.');
console.log(overlay);

rt.state.exfil.sweeps = 1;
rt.state.exfil.stress = 2;
overlay = rt.scene_overlay({ index: 0 });
assert(overlay.includes('Sweeps:1') && overlay.includes('Stress 2'), 'Exfil-Werte fehlen.');
console.log(overlay);

const originalLog = console.log;
console.log = () => {};
rt.on_command('!tk melee');
console.log = originalLog;
let tkOverlay = rt.scene_overlay({ index: 0 });
assert(tkOverlay.includes('TK🌀 1'), 'TK-Cooldown wird nicht angezeigt.');

console.log = () => {};
rt.on_command('!tk ready');
console.log = originalLog;
tkOverlay = rt.scene_overlay({ index: 0 });
assert(!tkOverlay.includes('TK🌀'), 'TK-Cooldown wurde nicht entfernt.');
