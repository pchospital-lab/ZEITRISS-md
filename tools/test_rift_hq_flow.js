'use strict';
const assert = require('assert');
const rt = require('../runtime');
const { openSession, projectPersonalSaves, leaderRiftBoard, assignRiftPayoff } = require('./lib/personal_save_projection');
const { save: completeSave, valid, validPersonalContent, errors } = require('./test_v7_personal_export');
const seed = (id, status = 'open') => ({ id, label: id, status, epoch: 1984 });
const save = (id, count, px = 0) => {
  const out = completeSave(id, {A:4,B:2,C:7,D:1,E:6}[id] || 1);
  out.save_id = `SAVE-${id}`; out.branch_id = `BRANCH-${id}`;
  out.campaign.px = px; out.campaign.px_state = 'stable';
  out.campaign.rift_seeds = Array.from({length: count}, (_, i) => seed(`${id}-R${i+1}`));
  valid(out, `Input ${id}`); validPersonalContent(out, `Input ${id}`);
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
const payoff = assignRiftPayoff(session, { debriefId: 'DB-1', completionId: 'CORE-EP1-MS4-END', seeds: [seed('CASE-X-1'), seed('CASE-X-2')], participants: ['A','B','C','D','E'], random: () => rolls.shift() });
assert.deepStrictEqual(payoff.assigned, [{seed_id:'CASE-X-1',owner_id:'B'}, {seed_id:'CASE-X-2',owner_id:'C'}]);
assert.deepStrictEqual(session.order.map(id => session.byCharacter.get(id).save.campaign.rift_seeds.length), [2,1,12,12,12]);
assert.equal(session.byCharacter.get('A').save.campaign.px, 0);
assert.equal(session.byCharacter.get('B').save.campaign.px, 2);
assert.equal(assignRiftPayoff(session, { debriefId: 'DB-1', completionId: 'CORE-EP1-MS4-END', seeds: [seed('NOPE')], participants: session.order }).repeated, true);
const staleCampaign = {...save('A', 2, 5).campaign, mission: 4};
const personalExports = projectPersonalSaves(session, { hq: true, anchorRoots: {campaign: staleCampaign} });
assert.equal(personalExports.length, 5); assert.ok(personalExports.every(out => out.characters.length === 1));
personalExports.forEach((out, i) => { valid(out, `Payoff-Export ${session.order[i]}`); validPersonalContent(out, `Payoff-Export ${session.order[i]}`); });
assert.equal(personalExports[0].campaign.px, 0); assert.equal(personalExports[0].campaign.rift_seeds.length, 2);
// Echter Roundtrip: serialisieren, alte Session verwerfen und neu öffnen.
session = openSession(JSON.parse(JSON.stringify(personalExports)));
assert.equal(assignRiftPayoff(session, { debriefId: 'DB-1', completionId: 'CORE-EP1-MS4-END', seeds: [seed('NOPE')], participants: session.order }).repeated, true);
assert.deepStrictEqual(session.order.map(id => session.byCharacter.get(id).save.campaign.rift_seeds.length), [2,1,12,12,12]);
// Regulärer Folgeabschluss: consumed endet, +1 bleibt über Export und Load.
const nextCampaign = JSON.parse(JSON.stringify(session.byCharacter.get('A').save.campaign));
nextCampaign.px = 1; nextCampaign.px_state = 'stable';
let nextExports = projectPersonalSaves(session, { hq: true, anchorRoots: { campaign: nextCampaign } });
assert.equal(nextExports[0].campaign.px, 1); session = openSession(JSON.parse(JSON.stringify(nextExports)));
assert.equal(session.byCharacter.get('A').save.campaign.px, 1);
session.byCharacter.get('A').save.campaign.px = 5; session.byCharacter.get('A').save.campaign.px_state = 'stable';
assert.equal(assignRiftPayoff(session, { debriefId: 'DB-2', completionId: 'CORE-EP1-MS5-END', seeds: [seed('NEXT-CYCLE')], participants: ['A'], random: () => 0 }).repeated, false);

// Alle voll: ITI übernimmt, Bestand bleibt, Payoff endet.
const full = openSession(['A','B','C','D','E'].map(id => save(id, 12, id === 'A' ? 5 : 2)));
const overflow = assignRiftPayoff(full, { debriefId: 'DB-FULL', completionId: 'CORE-FULL-END', seeds: [seed('OVER')], participants: full.order });
assert.deepStrictEqual(overflow.handedToIti, ['OVER']); assert.equal(full.byCharacter.get('A').save.campaign.px, 0);
assert.ok(full.order.every(id => full.byCharacter.get(id).save.campaign.rift_seeds.length === 12));

// Ungültige Vergaben bleiben atomar unverändert.
const invalid = openSession([save('A', 2, 4)]); const invalidBefore = JSON.stringify(invalid.byCharacter.get('A').save);
assert.throws(() => assignRiftPayoff(invalid, {debriefId:'BAD',completionId:'CORE-BAD-END',seeds:[seed('BAD')],participants:['A']}), /Px 5/);
assert.equal(JSON.stringify(invalid.byCharacter.get('A').save), invalidBefore);

// Runtime: Mid-Episode-Start, stabiler Modifier-Snapshot und kostenfreie, idempotente Abgabe.
// Nach Export/Load wählen B/C tatsächlich B als Leader und starten dessen
// gerade zugewiesene Instanz über den öffentlichen Runtime-Pfad.
const bc = openSession([personalExports[1], personalExports[2]]);
assert.equal(bc.anchorId, 'B');
assert.deepStrictEqual(leaderRiftBoard(bc).seeds.map((s) => s.id), ['CASE-X-1']);
rt.state.location = 'HQ'; rt.state.phase = 'hq'; rt.state.arena = { active: false, queue_state: 'idle' };
rt.state.character = { id: 'B', name: 'B', stress: 0, psi_heat: 0, cooldowns: {}, attributes: { SYS_max: 3, SYS_used: 0 } };
rt.state.campaign = { episode: 1, mission: 2, mission_in_episode: 2, episode_completed: false, px: 2,
  paradoxon_index: 2, rift_seeds: JSON.parse(JSON.stringify(personalExports[1].campaign.rift_seeds)) };
rt.state.team = { members: [] }; rt.state.party = { characters: [] }; rt.state.logs = { flags: {}, trace: [] }; rt.state.mission = {};
assert.equal(rt.launch_rift('CASE-X-1'), 'mission-launched');
assert.equal(rt.state.campaign.active_seed_id, 'CASE-X-1');
assert.match(rt.debrief({cu_reward:50,completed:true,temp:3}), /Chrono Units \+60 CU/);

rt.state.location = 'HQ'; rt.state.phase = 'hq'; rt.state.arena = { active: false, queue_state: 'idle' };
rt.state.character = { id: 'A', name: 'A', stress: 0, psi_heat: 0, cooldowns: {}, attributes: { SYS_max: 3, SYS_used: 0 } };
rt.state.campaign = { episode: 1, mission: 4, mission_in_episode: 3, episode_completed: false, px: 0, paradoxon_index: 0, rift_seeds: [seed('A-R1'), seed('A-R2')] };
rt.state.team = { members: [] }; rt.state.party = { characters: [] }; rt.state.logs = { flags: {}, trace: [] }; rt.state.mission = {};
assert.equal(rt.can_launch_rift('A-R1').ok, true);
assert.equal(rt.can_launch_rift('UNKNOWN').ok, false);
rt.state.phase = 'briefing'; assert.equal(rt.can_launch_rift('A-R1').ok, false); rt.state.phase = 'hq';
assert.equal(rt.launch_rift('A-R1'), 'mission-launched');
assert.equal(rt.state.campaign.active_seed_id, 'A-R1');
const snap = {...rt.state.mission.rift_mods};
rt.state.campaign.rift_seeds[0].status = 'closed';
assert.deepStrictEqual(rt.state.mission.rift_mods, snap); assert.deepStrictEqual(snap, {open_rifts:2,sg_bonus:2,cu_multi:1.4});
const payoutText = rt.debrief({cu_reward:100, completed:true, temp:3});
assert.match(payoutText, /Chrono Units \+140 CU/);
rt.state.phase = 'hq'; assert.deepStrictEqual(rt.snapshot_rift_modifiers(), {open_rifts:1,sg_bonus:1,cu_multi:1.2});
rt.state.phase = 'hq'; const before = JSON.stringify({character:rt.state.character,campaign:{...rt.state.campaign,rift_seeds:undefined}});
assert.deepStrictEqual(rt.resolve_rifts(['A-R2']), ['A-R2']); assert.deepStrictEqual(rt.resolve_rifts(['A-R2']), []);
assert.equal(JSON.stringify({character:rt.state.character,campaign:{...rt.state.campaign,rift_seeds:undefined}}), before);

rt.state.personal_saves = { B: { campaign: { rift_seeds: [seed('B-OWN'), seed('B-ACTIVE')] } } };
assert.deepStrictEqual(rt.resolve_rifts(['B-OWN'], 'B'), ['B-OWN']);
assert.equal(rt.state.personal_saves.B.campaign.rift_seeds.find(s => s.id === 'B-OWN').status, 'closed');

// Die frühere QA-Datei bleibt ausdrücklich ein Fragment und kein Vollsave.
const fragment = require('../internal/qa/fixtures/savegame_v7_personal_export_from_group.json');
assert.ok(errors(fragment).length > 0, 'Fragment muss vom strikten v7-Schema abgelehnt werden');

// P1/P2: historische Leader- oder reine Gast-Nachweise sperren aktuelle Px-Werte nicht.
const historical = save('A', 1, 0); historical.logs.trace.push({event:'rift_payoff',payoff_id:'A:0:ALT',debrief_id:'ALT'});
let projected = projectPersonalSaves(openSession([historical]), {hq:true, anchorRoots:{campaign:{...historical.campaign,px:1,px_state:'stable'}}});
assert.equal(projected[0].campaign.px, 1);
const cleanLeader = save('A', 1, 2); const historicalGuest = save('B', 0, 0);
historicalGuest.logs.trace.push({event:'rift_payoff',payoff_id:'B:0:DB-1',debrief_id:'DB-1'});
projected = projectPersonalSaves(openSession([cleanLeader,historicalGuest]), {hq:true, anchorRoots:{campaign:{...cleanLeader.campaign,px:3}}});
assert.equal(projected[0].campaign.px, 3);

// P3/P4: aktueller Abschluss schließt R1 und neue Logs bleiben neben Nachweisen erhalten.
const closing = save('A', 1, 0); closing.logs.trace.push({event:'rift_payoff',payoff_id:'A:0:OLD',debrief_id:'OLD'});
const closingCampaign = JSON.parse(JSON.stringify(closing.campaign)); closingCampaign.rift_seeds[0].status = 'closed';
projected = projectPersonalSaves(openSession([closing]), {hq:true, anchorRoots:{campaign:closingCampaign,logs:{...closing.logs,trace:[{event:'mission_end',debrief_id:'NOW'}]}}});
assert.equal(projected[0].campaign.rift_seeds[0].status, 'closed');
assert.deepStrictEqual(projected[0].logs.trace.map(e=>e.event).sort(), ['mission_end','rift_payoff']);

// P5: veralteter Gast-Abschlussblock darf die gerade zugewiesene Instanz nicht entfernen.
let guestProjection = openSession([save('A',0,5),save('B',0,0)]); const staleGuestCampaign = JSON.parse(JSON.stringify(guestProjection.byCharacter.get('B').save.campaign));
assignRiftPayoff(guestProjection,{debriefId:'GUEST-ASSIGN',completionId:'CORE-GUEST-END',seeds:[seed('B-NEW')],participants:['B'],random:()=>0});
projected = projectPersonalSaves(guestProjection,{hq:true,personal:{B:{roots:{campaign:staleGuestCampaign}}}});
assert.ok(projected[1].campaign.rift_seeds.some(s=>s.id==='B-NEW'));

// Das Trace-Budget behält den jüngsten benötigten Nachweis.
const budget = save('A',0,0); budget.logs.trace = Array.from({length:205},(_,i)=>({event:'note',debrief_id:`N-${i}`}));
budget.logs.trace.push({event:'rift_payoff',payoff_id:'A:0:KEEP',debrief_id:'KEEP'});
projected = projectPersonalSaves(openSession([budget]),{hq:true,anchorRoots:{logs:{...budget.logs,trace:[]}}});
assert.equal(projected[0].logs.trace.length,200); assert.ok(projected[0].logs.trace.some(e=>e.payoff_id==='A:0:KEEP'));

// Erst vollständig konsolidieren, dann kürzen: 200 neue Ereignisse verdrängen
// 200 alte auch beim zweiten Basis-Merge und bleiben in ihrer Reihenfolge.
const ordered = save('A',0,0);
ordered.logs.trace = Array.from({length:200},(_,i)=>({event:'old',debrief_id:`OLD-${i}`}));
const newerTrace = Array.from({length:200},(_,i)=>({event:'new',debrief_id:`NEW-${i}`}));
projected = projectPersonalSaves(openSession([ordered]),{hq:true,anchorRoots:{logs:{...ordered.logs,trace:newerTrace}}});
assert.deepStrictEqual(projected[0].logs.trace, newerTrace);

// Der jüngste Payoff bleibt trotz Kürzung über den kleinen Flag-Marker stabil.
const edge = save('A',0,5);
edge.logs.trace = [{event:'rift_payoff',payoff_id:'A:CORE-OLD',debrief_id:'OLD'},
  ...Array.from({length:199},(_,i)=>({event:'note',debrief_id:`EDGE-${i}`}))];
let edgeSession = openSession([edge]);
assignRiftPayoff(edgeSession,{debriefId:'DB-1',completionId:'CORE-NEW',seeds:[seed('EDGE-RIFT')],participants:['A'],random:()=>0});
const edgeExport = projectPersonalSaves(edgeSession,{hq:true})[0];
assert.equal(edgeExport.logs.trace.length,200);
assert.equal(edgeExport.logs.flags.last_rift_payoff_id,'A:CORE-NEW');
edgeSession = openSession(JSON.parse(JSON.stringify([edgeExport])));
assert.equal(assignRiftPayoff(edgeSession,{debriefId:'DB-1',completionId:'CORE-NEW',seeds:[seed('DUPLICATE')],participants:['A']}).repeated,true);
const otherLeader = openSession([save('B',0,5)]);
assert.equal(assignRiftPayoff(otherLeader,{debriefId:'DB-1',completionId:'CORE-NEW',seeds:[seed('B-UNIQUE')],participants:['B'],random:()=>0}).repeated,false);

// Legacy-Sperrstatus wird beim Normalisieren offen; Überbestand wird nicht gekürzt.
rt.state.campaign.rift_seeds = [seed('LEGACY','locked_until_episode_end'), ...Array.from({length:12},(_,i)=>seed(`OLD-${i}`))];
assert.equal(rt.ensure_rift_seeds().length, 13); assert.ok(rt.state.campaign.rift_seeds.every(s => s.status === 'open'));
console.log('rift-hq-flow-ok');
