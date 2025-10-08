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
  logs: { artifact_log: [], kodex: [], hud: [], flags: {} },
  ui: { gm_style: 'verbose', intro_seen: true }
};

const json = rt.save_deep(base);
const data = JSON.parse(json);
assert.equal(data.save_version, 6);
assert.equal(data.phase, 'core');
assert.equal(data.zr_version, rt.ZR_VERSION);
assert.equal(rt.ZR_VERSION, pkg.version);
assert.equal(data.ui.intro_seen, true);
assert.equal(data.campaign.px, 0);
assert.ok(Array.isArray(data.logs.artifact_log));
assert.ok(Array.isArray(data.logs.kodex));
assert.ok(Array.isArray(data.logs.hud));
assert.equal(typeof data.logs.flags, 'object');
assert.equal(typeof data.economy.cu, 'number');

assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, stress: 1 } }));
assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, psi_heat: 1 } }));
assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, attributes: { SYS_max: 1, SYS_used: 2 } } }));

const minimal = {
  location: 'HQ',
  phase: 'core',
  campaign: {},
  character: {
    id: 'CHR-2',
    stress: 0,
    psi_heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_used: 1 }
  }
};

const minimalJson = rt.save_deep(minimal);
const minimalData = JSON.parse(minimalJson);
assert.equal(minimalData.campaign.px, 0);
assert.equal(minimalData.campaign.paradoxon_index, 0);
assert.equal(minimalData.ui.gm_style, 'verbose');
assert.equal(minimalData.ui.intro_seen, false);
assert.equal(minimalData.economy.cu, 0);
assert.ok(Array.isArray(minimalData.logs.artifact_log));
assert.ok(Array.isArray(minimalData.logs.kodex));
assert.ok(Array.isArray(minimalData.logs.hud));
assert.deepEqual(minimalData.logs.flags, {});

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
