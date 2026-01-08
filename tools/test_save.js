const rt = require('../runtime');
const assert = require('assert');
const pkg = require('../package.json');
const saveFixture = require('../internal/qa/fixtures/savegame_v6_test.json');

const base = {
  location: 'HQ',
  phase: 'core',
  campaign: { paradoxon_index: 0 },
  character: {
    id: 'CHR-1',
    stress: 0,
    psi_heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_installed: 1, SYS_runtime: 1, SYS_used: 1 },
    quarters: {
      id: 'QTR-A17',
      preset: ' custom ',
      layout_tags: ['cqb_ready', '  analyst_cell '],
      deck: 'HQ-A',
      notes: 'Testquartier'
    }
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
    flags: {},
    field_notes: [
      '   Quick Memo   ',
      {
        agent_id: 'CHR-1',
        mission: 'Testmission',
        timestamp: '2025-07-01T10:00:00Z',
        note: 'Notiz mit Trim'
      },
      {},
      []
    ]
  },
  ui: { gm_style: 'verbose', intro_seen: true },
  arc_dashboard: {
    offene_seeds: ['Freitext: Anomalie aufspüren', { id: 'Seed-77', ort: 'Alexandria' }],
    fraktionen: {
      KAIROS: { status: 'Feindlich', letzten_hook: 'Sabotage im Archiv' }
    },
    fragen: ['Wer hat den Psi-Sturm ausgelöst?'],
    timeline: [
      { id: 'TL-1', epoch: '1971', label: 'Apollo' },
      { label: 'Leer' },
      'invalid'
    ]
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
assert.deepStrictEqual(data.arc_dashboard.offene_seeds[0], 'Freitext: Anomalie aufspüren');
assert.deepStrictEqual(data.arc_dashboard.offene_seeds[1].id, 'Seed-77');
assert.deepStrictEqual(data.arc_dashboard.fraktionen.KAIROS.status, 'Feindlich');
assert.ok(Array.isArray(data.arc_dashboard.timeline));
assert.equal(data.arc_dashboard.timeline[0].epoch, '1971');
assert.equal(data.arc_dashboard.timeline[0].id, 'TL-1');
assert.equal(data.arc_dashboard.timeline.length, 2);
assert.equal(data.logs.field_notes.length, 2);
assert.equal(data.logs.field_notes[0].note, 'Quick Memo');
assert.equal(data.logs.field_notes[1].mission, 'Testmission');
assert.equal(data.character.quarters.preset, 'custom');
assert.equal(data.character.quarters.layout_tags[1], 'analyst_cell');

assert.throws(
  () => {
    try {
      rt.save_deep({ ...base, arena: { queue_state: 'searching' } });
    } catch (err){
      console.log(err.message);
      throw err;
    }
  },
  /SaveGuard: Arena aktiv/
);

assert.doesNotThrow(
  () => rt.save_deep({ ...base, arena: { queue_state: 'completed' } })
);

const completedArena = JSON.parse(rt.save_deep({ ...base, arena: { phase: 'completed', queue_state: 'idle' } }));
assert.equal(completedArena.arena.queue_state, 'idle');
assert.equal(completedArena.arena.phase, 'completed');
assert.equal(completedArena.arena.active, false);

assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, stress: 1 } }));
assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, psi_heat: 1 } }));
assert.throws(() => rt.save_deep({ ...base, character: { ...base.character, attributes: { SYS_max: 1, SYS_installed: 2, SYS_runtime: 2, SYS_used: 2 } } }));
assert.throws(
  () => rt.save_deep({ ...base, character: { ...base.character, attributes: { SYS_max: 3, SYS_installed: 2, SYS_runtime: 2, SYS_used: 2 } } }),
  /SaveGuard: SYS nicht voll installiert/
);
assert.throws(
  () => rt.save_deep({ ...base, character: { ...base.character, attributes: { SYS_max: 3, SYS_installed: 3, SYS_runtime: 4, SYS_used: 3 } } }),
  /SaveGuard: SYS runtime overflow/
);

const minimal = {
  location: 'HQ',
  phase: 'core',
  campaign: {},
  character: {
    id: 'CHR-2',
    stress: 0,
    psi_heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_installed: 1, SYS_runtime: 1, SYS_used: 1 }
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

const missingTrace = JSON.parse(rt.save_deep({ ...base, logs: { ...base.logs, trace: [] } }));
delete missingTrace.logs.trace;
assert.throws(
  () => rt.enforce_required_save_fields(missingTrace),
  /SaveGuard: Feld logs\.trace fehlt\./
);

const missingArenaPsi = JSON.parse(rt.save_deep({ ...base, logs: { ...base.logs, arena_psi: [] } }));
delete missingArenaPsi.logs.arena_psi;
assert.throws(
  () => rt.enforce_required_save_fields(missingArenaPsi),
  /SaveGuard: Feld logs\.arena_psi fehlt\./
);

try {
  rt.save_deep({ ...base, location: 'CITY', phase: 'transfer' });
} catch (e) {
  assert(/Chronopolis ist kein HQ-Savepunkt/.test(e.message));
}

const migrated = rt.migrate_save({});
assert.equal(migrated.save_version, 6);
assert.equal(migrated.phase, 'core');
assert.equal(migrated.ui.gm_style, 'verbose');
assert.equal(migrated.ui.intro_seen, false);
assert.equal(migrated.logs.flags.runtime_version, rt.ZR_VERSION);

const wrapperRosterSource = {
  ...data,
  party: {},
  team: {},
  Charaktere: [
    { id: 'alpha', callsign: 'Alpha' },
    { id: 'beta', callsign: 'Beta' }
  ]
};
const wrapperNormalized = rt.migrate_save(wrapperRosterSource);
assert.deepStrictEqual(
  wrapperNormalized.party.characters.map(entry => entry.id),
  ['alpha', 'beta']
);
assert.deepStrictEqual(
  wrapperNormalized.team.members.map(entry => entry.id),
  ['alpha', 'beta']
);
const wrapperSaved = JSON.parse(rt.save_deep(wrapperNormalized));
assert.deepStrictEqual(
  wrapperSaved.party.characters.map(entry => entry.id),
  ['alpha', 'beta']
);
assert.equal(Object.prototype.hasOwnProperty.call(wrapperSaved, 'Charaktere'), false);

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

loadInput.arc_dashboard.offene_seeds = ['  Kontakt: Altes Archiv  ', { id: 'Seed-88', status: 'aktiv' }];

rt.load_deep(JSON.stringify(loadInput));
assert.equal(rt.state.logs.flags.compliance_shown_today, true);
assert.equal(rt.state.campaign.compliance_shown_today, true);
assert.equal(rt.state.logs.flags.chronopolis_warn_seen, false);
assert.equal(rt.state.scene.foreshadows, 1);
assert(rt.on_command('!boss status').includes('Mission FS 1/4'));
assert.equal(rt.state.arc_dashboard.offene_seeds[0], 'Kontakt: Altes Archiv');
assert.equal(rt.state.arc_dashboard.offene_seeds[1].id, 'Seed-88');
const roundtrip = JSON.parse(rt.save_deep(rt.state));
assert.equal(roundtrip.arc_dashboard.offene_seeds[0], 'Kontakt: Altes Archiv');
assert.equal(roundtrip.arc_dashboard.offene_seeds[1].id, 'Seed-88');
const arenaLoad = {
  ...roundtrip,
  location: 'ARENA',
  campaign: { ...roundtrip.campaign, mode: 'pvp' },
  arena: {
    active: true,
    phase: 'active',
    mode: 'single',
    previous_mode: 'mixed',
    queue_state: 'active',
    phase_strike_tax: 5,
    zone: 'combat'
  }
};
rt.load_deep(JSON.stringify(arenaLoad));
assert.equal(rt.state.campaign.mode, 'mixed');
assert.equal(rt.state.arena.phase, 'completed');
assert.equal(rt.state.arena.phase_strike_tax, 0);
assert.equal(rt.state.arena.resume_token.previous_mode, 'mixed');
const mergeConflicts = Array.isArray(rt.state.logs.flags.merge_conflicts)
  ? rt.state.logs.flags.merge_conflicts
  : [];
assert(mergeConflicts.some((entry) => entry.field === 'arena.state'));
const roundtripAfterArena = JSON.parse(rt.save_deep(rt.state));
assert.equal(roundtripAfterArena.arc_dashboard.offene_seeds[0], 'Kontakt: Altes Archiv');
assert.equal(roundtripAfterArena.arc_dashboard.offene_seeds[1].id, 'Seed-88');
const chronoLoad = {
  ...roundtrip,
  character: { ...roundtrip.character, lvl: 12 },
  logs: {
    ...roundtrip.logs,
    flags: { ...roundtrip.logs.flags, chronopolis_unlocked: false }
  }
};
rt.load_deep(JSON.stringify(chronoLoad));
assert.equal(rt.state.logs.flags.chronopolis_unlocked, true);
assert.equal(rt.state.logs.flags.chronopolis_unlock_logged, true);
const chronoToast = rt.state.logs.hud.find((entry) => {
  if (typeof entry === 'string') return entry.includes('Chronopolis-Schlüssel aktiv');
  return typeof entry?.message === 'string' && entry.message.includes('Chronopolis-Schlüssel aktiv');
});
assert(chronoToast);
const roundtripAfterChrono = JSON.parse(rt.save_deep(rt.state));
assert.equal(roundtripAfterChrono.arc_dashboard.offene_seeds[0], 'Kontakt: Altes Archiv');
assert.equal(roundtripAfterChrono.arc_dashboard.offene_seeds[1].id, 'Seed-88');
// Hinweis (#4 Load-Flows): Toolkit-Makros spiegeln das Flag jetzt mit,
// damit MyGPT-Läufe ohne runtime.js denselben Persistenzstatus liefern.

const saveFixtureClone = JSON.parse(JSON.stringify(saveFixture));
rt.load_deep(JSON.stringify(saveFixtureClone));
const savedFixture = JSON.parse(rt.save_deep());
assert.equal(savedFixture.logs.flags.last_save_at, saveFixtureClone.logs.flags.last_save_at);
const fixtureAudit = savedFixture.logs.trace.find(entry => entry.event === 'economy_audit');
assert(fixtureAudit);
assert.equal(fixtureAudit.at, saveFixtureClone.logs.flags.last_save_at);
const fixtureChrono = savedFixture.logs.trace.find(entry => entry.event === 'chronopolis_unlock');
assert(fixtureChrono && fixtureChrono.at);
const hudAutofill = savedFixture.logs.hud.find(
  (entry) => (
    entry.event === 'vehicle_clash'
      && typeof entry.at === 'string'
      && entry.at.startsWith(saveFixtureClone.logs.flags.last_save_at.slice(0, 19))
  )
);
assert(hudAutofill);
assert.equal(savedFixture.arc_dashboard.fragen[0], saveFixtureClone.arc_dashboard.fragen[0]);
assert.equal(
  savedFixture.logs.flags.atmosphere_contract_capture.rift.banned_terms.status,
  'PASS'
);
assert(savedFixture.logs.flags.hud_scene_usage);

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

function resetMissionTestState(){
  rt.state.location = 'MISSION';
  rt.state.phase = 'core';
  rt.state.logs = { flags: {} };
  rt.state.exfil = {};
  rt.state.campaign = {
    paradoxon_index: 0,
    missions_since_px: 0,
    px: 0,
    mission: 1,
    rift_seeds: [],
    rift_blueprints: [],
    chronopolis_tick_modulo: 0,
    chronopolis_missions_since_reset: 0
  };
}

resetMissionTestState();
const failedMission = rt.completeMission({
  temp: 1,
  stabilized: 'false',
  success: 'no',
  completed: 'failed',
  reason: 'failed'
});
assert.equal(rt.state.campaign.missions_since_px, 0);
assert.equal(
  failedMission.events.some((line) => /Mission stabilisiert/.test(line)),
  false
);
assert.equal(rt.state.campaign.last_mission_end_reason, 'failed');

resetMissionTestState();
rt.completeMission({ temp: 1, stabilized: 'YES' });
assert.equal(rt.state.campaign.missions_since_px, 1);
assert.equal(rt.state.campaign.last_mission_end_reason, 'completed');

resetMissionTestState();
rt.completeMission({ temp: 1, success: 'true' });
assert.equal(rt.state.campaign.missions_since_px, 1);
assert.equal(rt.state.campaign.last_mission_end_reason, 'completed');

resetMissionTestState();
rt.completeMission({ temp: 1, completed: 'Stabilized' });
assert.equal(rt.state.campaign.missions_since_px, 1);
assert.equal(rt.state.campaign.last_mission_end_reason, 'completed');

rt.state.economy = { cu: '1500', wallets: {} };
const hqPoolStatus = rt.apply_wallet_split({}, 0);
assert.equal(rt.state.economy.cu, 1500);
assert.ok(Array.isArray(hqPoolStatus.lines));

const economyMirrorSource = JSON.parse(JSON.stringify(base));
economyMirrorSource.economy = {
  cu: '1750',
  wallets: {
    ghost: { balance: '50', name: 'Ghost' },
    nova: { balance: '125' }
  }
};
const economyMirrorJson = rt.save_deep(economyMirrorSource);
const economyMirrorData = JSON.parse(economyMirrorJson);
assert.equal(economyMirrorData.economy.cu, 1750);
assert.equal(economyMirrorData.economy.wallets.ghost.balance, 50);
assert.equal(economyMirrorData.economy.wallets.ghost.name, 'Ghost');
assert.equal(economyMirrorData.economy.wallets.nova.balance, 125);

console.log('save-ok');
