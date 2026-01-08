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
  ui: { gm_style: 'verbose' },
  arc_dashboard: {
    offene_seeds: ['Kontakt: Beta-Sondierung', { id: 'Seed-01', status: 'offen' }],
    fraktionen: { ITI: { status: 'Verbündet' } },
    fragen: ['Wie sichern wir den Chronosplit?']
  }
};

const res = rt.load_deep(save);
assert.equal(res.status, 'ok');
assert.equal(rt.state.exfil, null);
assert.equal(rt.state.phase, 'core');
assert.equal(rt.state.character.psi_heat, 0);
assert.ok(rt.state.character.heat === undefined);
assert.equal(rt.state.campaign.px, 0);
assert.equal(rt.ZR_VERSION, pkg.version);
assert.ok(Array.isArray(rt.state.arc_dashboard.offene_seeds));
assert.equal(rt.state.arc_dashboard.offene_seeds[0], 'Kontakt: Beta-Sondierung');
assert.equal(rt.state.arc_dashboard.offene_seeds[1].id, 'Seed-01');
assert.equal(rt.state.arc_dashboard.fragen[0], 'Wie sichern wir den Chronosplit?');
assert.equal(rt.state.arc_dashboard.fraktionen.ITI.status, 'Verbündet');
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
  ui: { gm_style: 'precision', intro_seen: true },
  arc_dashboard: {
    offene_seeds: [
      { id: 'Seed-02', status: 'kritisch' },
      { id: 'Seed-03', status: 'archiviert' }
    ],
    fraktionen: {
      KAIROS: { status: 'Feindlich' }
    },
    fragen: []
  }
};

const legacyRes = rt.load_deep(legacy);
assert.equal(legacyRes.status, 'ok');
const partyRoster = rt.state.party.characters.map(entry => entry.id || entry.callsign || entry.name);
assert.deepStrictEqual(partyRoster, ['ALLY-1', 'ALLY-2', 'ALLY-3', 'Echo', 'ALLY-4']);
const teamRoster = rt.state.team.members.map(entry => entry.id || entry.callsign || entry.name);
assert.deepStrictEqual(teamRoster, partyRoster);
assert.equal(rt.state.arc_dashboard.offene_seeds.length, 2);
assert.equal(rt.state.arc_dashboard.fraktionen.KAIROS.status, 'Feindlich');
console.log('legacy-normalized');

const incompatible = {
  ...legacy,
  zr_version: '3.9.0'
};

assert.throws(() => rt.load_deep(incompatible), /Kodex-Archiv: Datensatz v3.9 nicht kompatibel mit v4.2/);
console.log('version-guard');

const hostSeeds = Array.from({ length: 10 }, (_, idx) => ({ id: `R-H-${idx + 1}` }));
const incomingSeeds = Array.from({ length: 6 }, (_, idx) => ({ id: `R-I-${idx + 1}` }));
rt.state.location = 'HQ';
rt.state.campaign = { rift_seeds: hostSeeds, mode: 'preserve', seed_source: 'preserve' };
rt.state.character = {
  id: 'HOST',
  stress: 0,
  psi_heat: 0,
  cooldowns: {},
  attributes: { SYS_max: 1, SYS_used: 1 }
};
rt.state.team = { members: [] };
rt.state.party = { characters: [] };
rt.state.loadout = {};
rt.state.economy = {};
rt.state.arc_dashboard = { offene_seeds: [], fraktionen: {}, fragen: [] };
rt.state.logs = { flags: {} };
const mergeSave = {
  save_version: 6,
  location: 'HQ',
  phase: 'core',
  campaign: { rift_seeds: incomingSeeds, px: 0, paradoxon_index: 0 },
  character: {
    id: 'IMPORT',
    stress: 0,
    psi_heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_used: 1 }
  },
  team: { members: [] },
  party: { characters: [] },
  loadout: {},
  economy: {},
  logs: { flags: {} },
  ui: { gm_style: 'verbose' },
  arc_dashboard: { offene_seeds: [] }
};

const mergeRes = rt.load_deep(mergeSave);
assert.equal(mergeRes.status, 'ok');
assert.equal(rt.state.campaign.rift_seeds.length, 12);
const keptIds = rt.state.campaign.rift_seeds.map((seed) => seed.id);
assert.deepStrictEqual(keptIds, [
  'R-H-1', 'R-H-2', 'R-H-3', 'R-H-4', 'R-H-5', 'R-H-6', 'R-H-7', 'R-H-8', 'R-H-9',
  'R-H-10', 'R-I-1', 'R-I-2'
]);
const conflict = rt.state.logs.flags.merge_conflicts.find((entry) => entry.field === 'rift_merge');
assert.ok(conflict, 'Rift-Seed-Merge-Konflikt fehlt.');
assert.ok(
  rt.state.logs.trace.some((entry) => entry.event === 'rift_seed_merge_cap_applied'),
  'Trace rift_seed_merge_cap_applied fehlt.'
);
console.log('rift-merge-cap');
