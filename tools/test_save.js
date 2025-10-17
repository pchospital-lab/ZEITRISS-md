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
  logs: {
    foreshadow: [{
      token: 'manual:signal',
      tag: 'Foreshadow',
      message: 'Signal im Tunnel',
      scene: 7,
      first_seen: '2025-06-01T00:00:00.000Z',
      last_seen: '2025-06-01T00:00:00.000Z'
    }],
    artifact_log: [],
    kodex: [],
    hud: [],
    flags: {}
  },
  ui: { gm_style: 'verbose', intro_seen: true },
  arc_dashboard: {
    offene_seeds: [{ id: 'Seed-77', ort: 'Alexandria' }],
    fraktionen: {
      KAIROS: { status: 'Feindlich', letzten_hook: 'Sabotage im Archiv' }
    },
    fragen: ['Wer hat den Psi-Sturm ausgelöst?']
  }
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
assert.ok(Array.isArray(data.logs.foreshadow));
assert.equal(data.logs.foreshadow.length, 1);
assert.equal(data.logs.foreshadow[0].token, 'manual:signal');
assert.equal(typeof data.logs.flags, 'object');
assert.equal(data.logs.flags.runtime_version, rt.ZR_VERSION);
assert.equal(data.logs.flags.chronopolis_warn_seen, false);
assert.equal(typeof data.economy.cu, 'number');
assert.ok(Array.isArray(data.arc_dashboard.offene_seeds));
assert.ok(Array.isArray(data.arc_dashboard.fragen));
assert.equal(typeof data.arc_dashboard.fraktionen, 'object');
assert.deepStrictEqual(data.arc_dashboard.offene_seeds[0].id, 'Seed-77');
assert.deepStrictEqual(data.arc_dashboard.fraktionen.KAIROS.status, 'Feindlich');

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
assert.ok(Array.isArray(minimalData.logs.foreshadow));
assert.equal(minimalData.logs.flags.runtime_version, rt.ZR_VERSION);
assert.equal(minimalData.logs.flags.chronopolis_warn_seen, false);
assert.ok(Array.isArray(minimalData.arc_dashboard.offene_seeds));
assert.equal(minimalData.arc_dashboard.offene_seeds.length, 0);
assert.ok(Array.isArray(minimalData.arc_dashboard.fragen));
assert.equal(typeof minimalData.arc_dashboard.fraktionen, 'object');

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
assert.equal(migrated.logs.flags.runtime_version, rt.ZR_VERSION);

const loadInput = {
  ...data,
  logs: {
    hud: [],
    artifact_log: [],
    kodex: [],
    foreshadow: [{
      token: 'manual:signal',
      tag: 'Foreshadow',
      message: 'Signal im Tunnel',
      scene: 9,
      first_seen: '2025-06-02T00:00:00.000Z'
    }],
    flags: { runtime_version: rt.ZR_VERSION, compliance_shown_today: false }
  },
  campaign: {
    ...data.campaign,
    compliance_shown_today: false
  },
  ui: { gm_style: 'verbose', intro_seen: true }
};

rt.load_deep(JSON.stringify(loadInput));
assert.equal(rt.state.logs.flags.compliance_shown_today, true);
assert.equal(rt.state.campaign.compliance_shown_today, true);
assert.equal(rt.state.logs.flags.chronopolis_warn_seen, false);
assert.equal(rt.state.scene.foreshadows, 1);
assert(rt.on_command('!boss status').includes('Mission FS 1/4'));
// Hinweis (#4 Load-Flows): Toolkit-Makros spiegeln das Flag jetzt mit,
// damit MyGPT-Läufe ohne runtime.js denselben Persistenzstatus liefern.

// Wallet-Split: Verhältnis 1:2 verteilt CU gewichtet
rt.state.character = { id: 'ghost', callsign: 'Ghost' };
rt.state.party = { characters: [
  { id: 'ghost', callsign: 'Ghost' },
  { id: 'nova', callsign: 'Nova' }
] };
rt.state.team = { members: [], stress: 0, psi_heat: 0 };
rt.state.economy = { cu: 0, wallets: {} };
const splitResult = rt.apply_wallet_split({
  economy: {
    split: [
      { id: 'ghost', ratio: 1 },
      { id: 'nova', ratio: 2 }
    ]
  }
}, 300);
assert.equal(rt.state.economy.wallets.ghost.balance, 100);
assert.equal(rt.state.economy.wallets.nova.balance, 200);
assert.equal(splitResult.payout, 300);
assert.equal(splitResult.leftover, 0);

// Psi-Puffer wird beim Missionsstart standardmäßig gesetzt
rt.state.team = {
  members: [
    { id: 'ally-1', callsign: 'Ally One' },
    { id: 'ally-2', callsign: 'Ally Two' }
  ],
  stress: 0,
  psi_heat: 0
};
rt.state.party = {
  characters: [
    { id: 'ghost', callsign: 'Ghost' },
    { id: 'nova', callsign: 'Nova' }
  ]
};
rt.StartMission();
assert.equal(rt.state.character.psi_buffer, true);
assert.equal(rt.state.team.psi_buffer, true);
rt.state.team.members.forEach((member) => {
  assert.equal(member.psi_buffer, true);
});
rt.state.party.characters.forEach((member) => {
  assert.equal(member.psi_buffer, true);
});

console.log('save-ok');
