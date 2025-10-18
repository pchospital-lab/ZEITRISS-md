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
