'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const rt = require('../runtime');
const { openSession, projectPersonalSaves, leaderRiftBoard, assignRiftPayoff } = require('./lib/personal_save_projection');
const seed = (id, status = 'open') => ({ id, label: id, status, epoch: 1984 });
const base = JSON.parse(fs.readFileSync(path.join(__dirname, '../internal/qa/fixtures/savegame_v7_personal_export_from_group.json')));
delete base.fixture_kind;
const save = (id, count, px = 0) => {
  const out = JSON.parse(JSON.stringify(base));
  const oldId = out.characters[0].id;
  out.save_id = `SAVE-${id}`; out.parent_save_id = null; out.branch_id = `BRANCH-${id}`;
  out.characters[0].id = id; out.characters[0].name = `Agent ${id}`; out.characters[0].wallet = 100 + id.charCodeAt(0);
  out.campaign.px = px; out.campaign.px_state = 'stable';
  out.campaign.rift_seeds = Array.from({length: count}, (_, i) => seed(`${id}-R${i+1}`));
  out.economy.wallets = { [id]: { balance: out.characters[0].wallet, name: out.characters[0].name } };
  for (const npc of out.continuity.npc_roster || []) if (npc.owner_id === oldId) npc.owner_id = id;
  return out;
};

// Leader ist stets der erste Save; Gastbestände ändern Board und Boni nicht.
let session = openSession([save('A', 0), save('B', 12)]);
assert.deepStrictEqual(leaderRiftBoard(session), { leader_id: 'A', seeds: [], sg_bonus: 0, cu_multi: 1 });
session = openSession([save('A', 2), save('B', 12), save('C', 4)]);
assert.deepStrictEqual(leaderRiftBoard(session).seeds.map(s => s.id), ['A-R1', 'A-R2']);
assert.equal(leaderRiftBoard(session).sg_bonus, 2); assert.equal(leaderRiftBoard(session).cu_multi, 1.4);

// Kontrollierter Zufall: zunächst B, nach erneuter Kapazitätsprüfung C.
session = openSession([save('A', 2, 5), save('B', 0, 2), save('C', 11, 3), save('D', 12, 4), save('E', 12, 1)]);
const rolls = [0.34, 0.99];
const payoff = assignRiftPayoff(session, { debriefId: 'DB-1', seeds: [seed('CASE-X-1'), seed('CASE-X-2')], participants: ['A','B','C','D','E'], random: () => rolls.shift() });
assert.deepStrictEqual(payoff.assigned, [{seed_id:'CASE-X-1',owner_id:'B'}, {seed_id:'CASE-X-2',owner_id:'C'}]);
assert.deepStrictEqual(session.order.map(id => session.byCharacter.get(id).save.campaign.rift_seeds.length), [2,1,12,12,12]);
assert.equal(session.byCharacter.get('A').save.campaign.px, 0);
assert.equal(session.byCharacter.get('B').save.campaign.px, 2);
assert.equal(assignRiftPayoff(session, { debriefId: 'DB-1', seeds: [seed('NOPE')], participants: session.order }).repeated, true);
const staleCampaign = {...save('A', 2, 5).campaign, mission: 4};
const personalExports = projectPersonalSaves(session, { hq: true, anchorRoots: {campaign: staleCampaign} });
assert.equal(personalExports.length, 5); assert.ok(personalExports.every(out => out.characters.length === 1));
assert.equal(personalExports[0].campaign.px, 0); assert.equal(personalExports[0].campaign.rift_seeds.length, 2);
// Echter Roundtrip: serialisieren, alte Session verwerfen und neu öffnen.
session = openSession(JSON.parse(JSON.stringify(personalExports)));
assert.equal(assignRiftPayoff(session, { debriefId: 'DB-1', seeds: [seed('NOPE')], participants: session.order }).repeated, true);
assert.deepStrictEqual(session.order.map(id => session.byCharacter.get(id).save.campaign.rift_seeds.length), [2,1,12,12,12]);
session.byCharacter.get('A').save.campaign.px = 5;
assert.equal(assignRiftPayoff(session, { debriefId: 'DB-2', seeds: [seed('NEXT-CYCLE')], participants: ['A'], random: () => 0 }).repeated, false);

// Alle voll: ITI übernimmt, Bestand bleibt, Payoff endet.
const full = openSession(['A','B','C','D','E'].map(id => save(id, 12, id === 'A' ? 5 : 2)));
const overflow = assignRiftPayoff(full, { debriefId: 'DB-FULL', seeds: [seed('OVER')], participants: full.order });
assert.deepStrictEqual(overflow.handedToIti, ['OVER']); assert.equal(full.byCharacter.get('A').save.campaign.px, 0);
assert.ok(full.order.every(id => full.byCharacter.get(id).save.campaign.rift_seeds.length === 12));

// Ungültige Vergaben bleiben atomar unverändert.
const invalid = openSession([save('A', 2, 4)]); const invalidBefore = JSON.stringify(invalid.byCharacter.get('A').save);
assert.throws(() => assignRiftPayoff(invalid, {debriefId:'BAD',seeds:[seed('BAD')],participants:['A']}), /Px 5/);
assert.equal(JSON.stringify(invalid.byCharacter.get('A').save), invalidBefore);

// Runtime: Mid-Episode-Start, stabiler Modifier-Snapshot und kostenfreie, idempotente Abgabe.
rt.state.location = 'HQ'; rt.state.phase = 'hq'; rt.state.arena = { active: false, queue_state: 'idle' };
rt.state.character = { id: 'A', name: 'A', stress: 0, psi_heat: 0, cooldowns: {}, attributes: { SYS_max: 3, SYS_used: 0 } };
rt.state.campaign = { episode: 1, mission: 4, mission_in_episode: 3, episode_completed: false, px: 0, paradoxon_index: 0, rift_seeds: [seed('A-R1'), seed('A-R2')] };
rt.state.team = { members: [] }; rt.state.party = { characters: [] }; rt.state.logs = { flags: {}, trace: [] }; rt.state.mission = {};
assert.equal(rt.can_launch_rift('A-R1').ok, true);
assert.equal(rt.can_launch_rift('UNKNOWN').ok, false);
rt.state.phase = 'briefing'; assert.equal(rt.can_launch_rift('A-R1').ok, false); rt.state.phase = 'hq';
rt.snapshot_rift_modifiers(); const snap = {...rt.state.mission.rift_mods};
rt.state.campaign.rift_seeds[0].status = 'closed';
assert.deepStrictEqual(rt.state.mission.rift_mods, snap); assert.deepStrictEqual(snap, {open_rifts:2,sg_bonus:2,cu_multi:1.4});
const payoutText = rt.debrief({cu_reward:100, completed:false, temp:3});
assert.match(payoutText, /Chrono Units \+140 CU/);
rt.state.phase = 'hq'; assert.deepStrictEqual(rt.snapshot_rift_modifiers(), {open_rifts:1,sg_bonus:1,cu_multi:1.2});
rt.state.phase = 'hq'; const before = JSON.stringify({character:rt.state.character,campaign:{...rt.state.campaign,rift_seeds:undefined}});
assert.deepStrictEqual(rt.resolve_rifts(['A-R2']), ['A-R2']); assert.deepStrictEqual(rt.resolve_rifts(['A-R2']), []);
assert.equal(JSON.stringify({character:rt.state.character,campaign:{...rt.state.campaign,rift_seeds:undefined}}), before);

rt.state.personal_saves = { B: { campaign: { rift_seeds: [seed('B-OWN'), seed('B-ACTIVE')] } } };
assert.deepStrictEqual(rt.resolve_rifts(['B-OWN'], 'B'), ['B-OWN']);
assert.equal(rt.state.personal_saves.B.campaign.rift_seeds.find(s => s.id === 'B-OWN').status, 'closed');

// Legacy-Sperrstatus wird beim Normalisieren offen; Überbestand wird nicht gekürzt.
rt.state.campaign.rift_seeds = [seed('LEGACY','locked_until_episode_end'), ...Array.from({length:12},(_,i)=>seed(`OLD-${i}`))];
assert.equal(rt.ensure_rift_seeds().length, 13); assert.ok(rt.state.campaign.rift_seeds.every(s => s.status === 'open'));
console.log('rift-hq-flow-ok');
