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
assert.equal(rt.state.campaign.px, 0);
assert.equal(rt.ZR_VERSION, pkg.version);
console.log('load-ok');

const legacy = {
  save_version: 5,
  location: 'HQ',
  phase: 'core',
  campaign: { px: 2, paradoxon_index: 2 },
  character: {
    id: 'CHR-1',
    stress: 0,
    heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_used: 1 }
  },
  team: {
    members: [
      { id: 'ALLY-1', name: 'Alfa' }
    ],
    roster: [
      { id: 'ALLY-1', name: 'Alfa' },
      { id: 'ALLY-2', name: 'Bravo' }
    ]
  },
  party: {
    members: [
      { id: 'ALLY-2', name: 'Bravo' },
      { id: 'ALLY-3', callsign: 'Charlie' }
    ]
  },
  group: {
    characters: [
      { name: 'Echo' }
    ]
  },
  npc_team: [
    { id: 'ALLY-4', name: 'Delta' }
  ],
  loadout: {},
  economy: { cu: 4 },
  logs: { artifact_log: [], kodex: [] },
  ui: { gm_style: 'precision', intro_seen: true }
};

const legacyRes = rt.load_deep(legacy);
assert.equal(legacyRes.status, 'ok');
const partyRoster = rt.state.party.characters.map(entry => entry.id || entry.callsign || entry.name);
assert.deepStrictEqual(partyRoster, ['ALLY-1', 'ALLY-2', 'ALLY-3', 'Echo', 'ALLY-4']);
const teamRoster = rt.state.team.members.map(entry => entry.id || entry.callsign || entry.name);
assert.deepStrictEqual(teamRoster, partyRoster);
console.log('legacy-normalized');
