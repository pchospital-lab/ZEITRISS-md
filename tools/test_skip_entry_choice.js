const assert = require('assert');
const rt = require('../runtime');

// Ausgangslage: Skip-Einstieg wurde bereits dokumentiert (z. B. nach SkipEntryChoice()).
rt.state.flags.runtime.skip_entry_choice = true;

rt.StartMission();

assert.strictEqual(rt.state.flags.runtime.skip_entry_choice, true);

console.log('skip-entry-choice-ok');
