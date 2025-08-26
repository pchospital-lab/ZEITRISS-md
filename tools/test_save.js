const rt = require('../runtime');
const assert = require('assert');

const base = {
  location: 'HQ',
  campaign: { paradoxon_index: 0 },
  character: {
    id: 'CHR-1',
    stress: 0,
    heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_used: 1 }
  },
  team: {},
  loadout: {},
  economy: {},
  logs: { artifact_log: [], codex: [] },
  ui: { gm_style: 'verbose' }
};

const json = rt.save_deep(base);
const data = JSON.parse(json);
assert.equal(data.save_version, 3);

assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, stress: 1 } }));
assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, attributes: { SYS_max: 1, SYS_used: 0 } } }));

assert.equal(rt.migrate_save({}).save_version, 3);
console.log('save-ok');
