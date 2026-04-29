const fs = require('fs');
const path = require('path');
const assert = require('assert');

const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'internal/qa/fixtures/savegame_v7_split_3_2_merge.json'), 'utf8'));

assert.strictEqual(fixture.characters.length, 5, 'Merge muss 5 Spieler tragen.');
assert.ok(fixture.merge_id, 'merge_id fehlt.');
assert.strictEqual(fixture.continuity?.split?.convergence_ready, true, 'Split muss als convergence_ready markiert sein.');
assert.ok((fixture.continuity?.split?.resolved_threads || []).length >= 2, 'resolved_threads muss beide Branches enthalten.');
assert.ok((fixture.continuity?.shared_echoes || []).length >= 1, 'shared_echoes braucht mindestens ein Konvergenz-Echo.');
assert.ok(Array.isArray(fixture.continuity?.roster_echoes), 'roster_echoes fehlt.');
assert.ok((fixture.logs?.flags?.imported_saves || []).length >= 2, 'imported_saves muss beide Imports protokollieren.');
assert.ok(Array.isArray(fixture.logs?.flags?.continuity_conflicts), 'continuity_conflicts muss existieren (auch leer).');
assert.strictEqual(fixture.continuity?.last_seen?.mode, 'hq', 'Mehrfach-Load-Anker muss HQ sein.');

console.log('v7-smart-merge-3-2-ok');
