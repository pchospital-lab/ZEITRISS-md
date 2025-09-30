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
    psi_heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_used: 1 }
  },
  team: {},
  loadout: {},
  economy: {},
  logs: { artifact_log: [], codex: [] },
  ui: { gm_style: 'verbose', intro_seen: true }
};

const json = rt.save_deep(base);
const data = JSON.parse(json);
assert.equal(data.save_version, 6);
assert.equal(data.phase, 'core');
assert.equal(data.zr_version, rt.ZR_VERSION);
assert.equal(rt.ZR_VERSION, pkg.version);
assert.equal(data.ui.intro_seen, true);

assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, stress: 1 } }));
assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, psi_heat: 1 } }));
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
assert.equal(migrated.save_version, 6);
assert.equal(migrated.phase, 'core');
assert.equal(migrated.ui.gm_style, 'verbose');
assert.equal(migrated.ui.intro_seen, false);
console.log('save-ok');
