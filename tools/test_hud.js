const assert = require('assert');
const rt = require('../runtime');

const originalLog = console.log;

console.log = () => {};
rt.StartMission();
console.log = originalLog;

let overlay = rt.scene_overlay({ index: 0 });
assert(!overlay.includes('TK🌀'), 'Cooldown-Icon darf nicht gesetzt sein.');
console.log(overlay);

rt.state.exfil.sweeps = 1;
rt.state.exfil.stress = 2;
overlay = rt.scene_overlay({ index: 0 });
assert(overlay.includes('Sweeps:1') && overlay.includes('Stress 2'), 'Exfil-Werte fehlen.');
console.log(overlay);

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

console.log = () => {};
rt.ForeshadowHint('Seltsames Flimmern am Horizont');
console.log = originalLog;
const fsOverlay = rt.scene_overlay();
assert(fsOverlay.includes('FS 1'), 'Foreshadow-Badge fehlt im Overlay.');

rt.state.campaign.type = 'rift';
rt.state.campaign.scene_total = 14;
console.log = () => {};
const riftOverlay = rt.StartMission();
console.log = originalLog;
assert(riftOverlay.includes('SC 0/14'), 'Rift-Overlay zeigt nicht 14 Szenen.');
assert.strictEqual(rt.state.phase, 'rift', 'Rift-Phase in state.phase fehlt.');
assert.strictEqual(rt.state.campaign.phase, 'rift', 'Rift-Phase in campaign.phase fehlt.');
assert.strictEqual(rt.state.scene.total, 14, 'Rift-Szenenanzahl nicht übernommen.');

// HUD-Toast-Budget: Low-Priority-Toasts werden im QA-Mode unterdrückt und protokolliert.
rt.state.logs = {
  hud: [],
  trace: [],
  flags: { qa_mode: true, hud_scene_usage: { 0: { count: 2, tags: { HUD: 2 }, limit: 2 } } }
};
rt.state.scene = { index: 0, total: 12 };
rt.state.campaign = { episode: 1, mission: 1 };
const offlineGuide = rt.offline_help('command');
assert(offlineGuide.includes('Terminal'), 'Offline-Guide wurde nicht geliefert.');
assert.strictEqual(rt.state.logs.hud.length, 0, 'Toast hätte wegen Cap nicht erscheinen dürfen.');
const lastTrace = rt.state.logs.trace[rt.state.logs.trace.length - 1];
assert.strictEqual(lastTrace.event, 'toast_suppressed', 'Suppression-Trace fehlt.');
assert.strictEqual(lastTrace.hud_scene_usage.count, 2, 'HUD-Usage-Snapshot fehlt im Trace.');
console.log('hud-toast-budget-ok');
