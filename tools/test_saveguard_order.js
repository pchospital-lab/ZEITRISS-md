const assert = require('assert');

function freshRuntime(){
  delete require.cache[require.resolve('../runtime')];
  return require('../runtime');
}

function expectSaveBlocked(rt){
  const before = rt.state.logs.trace.length;
  let error;
  try {
    rt.save_deep();
  } catch (err){
    error = err;
  }
  assert(error instanceof Error, 'SaveGuard sollte einen Fehler werfen');
  const added = rt.state.logs.trace.slice(before);
  assert.strictEqual(added.length, 1, 'Trace sollte genau einen Save-Block enthalten');
  const entry = added[0];
  assert.strictEqual(entry.event, 'save_blocked', 'Save-Block-Event fehlt');
  return { error, entry };
}

const offlineRt = freshRuntime();
offlineRt.startSolo('klassisch');
offlineRt.StartMission();
offlineRt.state.location = 'FIELD';
offlineRt.state.phase = 'core';
offlineRt.state.comms = { device: 'comlink', range_m: 0, jammed: true };
let { error: offlineError, entry: offlineEntry } = expectSaveBlocked(offlineRt);
assert.ok(
  offlineError.message.includes('Offline – HQ-Deepsave erst nach Re-Sync'),
  'Offline-Guard liefert keinen Offline-Hinweis'
);
assert.strictEqual(offlineEntry.reason, 'offline');
assert.strictEqual(offlineEntry.location, 'FIELD');
assert.strictEqual(offlineEntry.phase, 'core');
assert.strictEqual(offlineEntry.link_state, 'field_offline');

const arenaRt = freshRuntime();
arenaRt.startSolo('klassisch');
arenaRt.state.location = 'FIELD';
arenaRt.state.phase = 'transfer';
arenaRt.state.arena = {
  active: true,
  phase: 'combat',
  queue_state: 'engaged',
  zone: 'alpha'
};
let { error: arenaError, entry: arenaEntry } = expectSaveBlocked(arenaRt);
assert.ok(arenaError.message.includes('Arena aktiv'), 'Arena-Guard liefert keinen Arena-Toast');
assert.strictEqual(arenaEntry.reason, 'arena_active');
assert.strictEqual(arenaEntry.arena.active, true, 'Arena-Trace fehlt Aktiv-Flag');
assert.strictEqual(arenaEntry.arena.queue_state, 'active', 'Arena-Queue-State fehlt');
assert.strictEqual(arenaEntry.arena.phase, 'combat', 'Arena-Phase fehlt');
assert.strictEqual(arenaEntry.arena.zone, 'alpha', 'Arena-Zone fehlt');
assert.strictEqual(arenaEntry.location, 'FIELD');
assert.strictEqual(arenaEntry.phase, 'transfer');

let locationError, locationEntry;

const locationRt = freshRuntime();
locationRt.startSolo('klassisch');
locationRt.state.location = 'CITY';
locationRt.state.phase = 'transfer';
({ error: locationError, entry: locationEntry } = expectSaveBlocked(locationRt));
assert.ok(
  locationError.message.includes('Chronopolis ist kein HQ-Savepunkt'),
  'Chronopolis-Guard meldet kein HQ-Only'
);
assert.strictEqual(locationEntry.reason, 'chronopolis');
assert.strictEqual(locationEntry.location, 'CITY');
assert.strictEqual(locationEntry.phase, 'transfer');

const hqOnlyRt = freshRuntime();
hqOnlyRt.startSolo('klassisch');
hqOnlyRt.state.location = 'FIELD';
hqOnlyRt.state.phase = 'transfer';
({ error: locationError, entry: locationEntry } = expectSaveBlocked(hqOnlyRt));
assert.ok(
  locationError.message.includes('Speichern nur im HQ'),
  'HQ-Only-Guard liefert keinen HQ-Toast'
);
assert.strictEqual(locationEntry.reason, 'hq_only');
assert.strictEqual(locationEntry.location, 'FIELD');
assert.strictEqual(locationEntry.phase, 'transfer');

console.log('saveguard-order-ok');
