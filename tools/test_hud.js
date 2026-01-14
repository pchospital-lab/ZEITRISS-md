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

// HUD-Toast-Budget: Critical-Tags (z. B. OFFLINE) werden nicht unterdrückt.
rt.state.logs = {
  hud: [],
  trace: [],
  flags: { qa_mode: true, hud_scene_usage: { 0: { count: 2, tags: { HUD: 2 }, limit: 2 } } }
};
rt.state.scene = { index: 0, total: 12 };
rt.state.campaign = { episode: 1, mission: 1 };
const offlineGuide = rt.offline_help('command');
assert(offlineGuide.includes('Terminal'), 'Offline-Guide wurde nicht geliefert.');
assert.strictEqual(rt.state.logs.hud.length, 1, 'Critical-Toast muss im HUD-Log landen.');
assert.ok(!rt.state.logs.hud[0].suppressed, 'Critical-Toast darf nicht suppressed werden.');
const lastTrace = rt.state.logs.trace[rt.state.logs.trace.length - 1];
assert.ok(!lastTrace || lastTrace.event !== 'toast_suppressed', 'Suppression-Trace ist unerwartet.');
console.log('hud-toast-critical-ok');

// HUD-Toast-Budget: Unterdrückungen schreiben auch außerhalb des QA-Modes einen Trace.
rt.state.logs = { hud: [], trace: [], flags: { hud_scene_usage: {} } };
rt.state.scene = { index: 2, total: 8 };
rt.state.campaign = { episode: 1, mission: 2 };
const toastResults = [];
for (let i = 0; i < 5; i += 1){
  toastResults.push(rt.hud_toast(`Low-Priority-${i + 1}`, 'HUD'));
}
const visibleToasts = toastResults.filter((entry) => !entry.suppressed);
assert.strictEqual(visibleToasts.length, 2, 'Nur zwei Toasts dürfen sichtbar sein.');
assert.strictEqual(rt.state.logs.hud.length, 5, 'HUD-Log soll Suppressions mitführen.');
const suppressedHud = rt.state.logs.hud.filter((entry) => entry.suppressed);
assert.strictEqual(suppressedHud.length, 3, 'Suppressed-HUD-Einträge fehlen.');
suppressedHud.forEach((entry) => {
  assert.strictEqual(entry.reason, 'budget', 'Suppression-Reason fehlt im HUD-Log.');
});
const suppression = rt.state.logs.trace.filter((entry) => entry.event === 'toast_suppressed');
assert.strictEqual(suppression.length, 3, 'Drei Suppression-Traces erwartet.');
suppression.forEach((entry) => {
  assert.strictEqual(entry.qa_mode, false, 'Suppression-Trace muss QA-Flag spiegeln.');
  assert.ok(entry.hud_scene_usage, 'HUD-Usage-Snapshot fehlt.');
  assert.strictEqual(entry.hud_scene_usage.count, 2, 'Usage-Count muss das Cap spiegeln.');
});
console.log('hud-toast-budget-outside-qa-ok');

// HUD-Events: strukturierte Einträge validieren, numerische Felder normalisieren und fehlende Timestamps ergänzen.
console.log = () => {};
rt.StartMission();
console.log = originalLog;
rt.state.logs.hud = [
  { event: 'mass_conflict', chaos: '2', stress: '1' }
];
rt.state.logs.flags = { hud_scene_usage: {} };
rt.state.scene = { index: 1, total: 12 };
const beforeHudLength = rt.state.logs.hud.length;
const clash = rt.hud_event('vehicle_clash', { tempo: '120.5', stress: 3, damage: '2' });
assert.ok(clash, 'HUD-Event wurde verworfen.');
assert.strictEqual(clash.event, 'vehicle_clash');
assert.strictEqual(clash.damage, 2, 'Schaden nicht numerisch normalisiert.');
assert.strictEqual(clash.tempo, 120.5, 'Tempo nicht numerisch normalisiert.');
const conflict = rt.state.logs.hud.find((entry) => entry.event === 'mass_conflict');
assert.ok(conflict, 'Mass-Conflict-Event fehlt.');
assert.ok(typeof conflict.at === 'string' && conflict.at.includes('T'), 'Timestamp nicht ergänzt.');
assert.strictEqual(conflict.chaos, 2, 'Chaos nicht numerisch normalisiert.');
const invalid = rt.hud_event('unknown_event', { chaos: 1 });
assert.ok(invalid, 'Unbekanntes Event muss als Fallback übernommen werden.');
assert.strictEqual(invalid.event, 'unknown_event');
assert.strictEqual(invalid.tag, 'HUD');
const fallback = rt.state.logs.hud.find((entry) => entry.event === 'unknown_event');
assert.ok(fallback, 'Fallback-HUD-Event fehlt.');
assert.strictEqual(rt.state.logs.hud.length, beforeHudLength + 2, 'HUD-Events sollten Fallbacks anhängen.');
console.log('hud-events-ok');
