const fs = require('fs');
const path = require('path');
const assert = require('assert');

const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'internal/qa/fixtures/savegame_v7_personal_export_from_group.json'), 'utf8'));

assert.strictEqual(fixture.characters.length, 1, 'Personal-Export darf genau einen Character enthalten.');
assert.strictEqual(fixture.characters[0].id, 'AGENT-03', 'Falscher Charakter exportiert.');
assert.ok((fixture.continuity?.shared_echoes || []).length >= 1, 'Mindestens ein shared_echo muss erhalten bleiben.');
assert.ok((fixture.continuity?.roster_echoes || []).length <= 2, 'roster_echoes im Personal-Export max 2.');
assert.ok((fixture.continuity?.shared_echoes || []).length <= 3, 'shared_echoes im Personal-Export max 3.');
assert.ok((fixture.arc?.hooks || []).length <= 3, 'arc.hooks im Personal-Export max 3.');

const jsonText = JSON.stringify(fixture);
assert.ok(!/AGENT-01|AGENT-02|AGENT-04|AGENT-05/.test(jsonText), 'Andere Spielercharaktere dürfen nicht im Personal-Export auftauchen.');

console.log('v7-personal-export-ok');
