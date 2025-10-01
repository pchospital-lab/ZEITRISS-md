const rt = require('../runtime');
const assert = require('assert');
const pkg = require('../package.json');

const save = {
  save_version: 4,
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
  logs: { artifact_log: [], kodex: [] },
  ui: { gm_style: 'verbose' }
};

const res = rt.load_deep(save);
assert.equal(res.status, 'ok');
assert.equal(rt.state.exfil, null);
assert.equal(rt.state.phase, 'core');
assert.equal(rt.state.character.psi_heat, 0);
assert.ok(rt.state.character.heat === undefined);
assert.equal(rt.ZR_VERSION, pkg.version);
console.log('load-ok');
