const rt = require('../runtime');
const assert = require('assert');
const pkg = require('../package.json');

const base = {
  location: 'HQ',
  phase: 'core',
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
assert.equal(data.save_version, 4);
assert.equal(data.phase, 'core');
assert.equal(data.zr_version, rt.ZR_VERSION);
assert.equal(rt.ZR_VERSION, pkg.version);

assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, stress: 1 } }));
assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, attributes: { SYS_max: 1, SYS_used: 2 } } }));
assert.throws(() => rt.save_deep({ ...base, economy: undefined }));
assert.throws(() => rt.save_deep({ ...base, logs: undefined }));
assert.throws(() => rt.save_deep({ ...base, ui: undefined }));

try {
  rt.save_deep({ ...base, location: 'CITY' });
} catch (e) {
  console.log(e.message);
}

const migrated = rt.migrate_save({});
assert.equal(migrated.save_version, 4);
assert.equal(migrated.phase, 'core');
console.log('save-ok');
