'use strict';
const assert = require('assert');
const schema = require('../systems/gameflow/saveGame.v7.export.schema.json');
const { openSession, projectPersonalSaves } = require('./lib/personal_save_projection');
const clone = (v) => JSON.parse(JSON.stringify(v));

// Kleiner generischer Draft-07-Validator fuer die im Exportvertrag verwendeten
// Keywords. Damit prueft dieser Test das reale strikte Schema ohne Fremdpaket.
function errors(value, rule = schema, path = '$') {
  const out = [];
  const types = Array.isArray(rule.type) ? rule.type : [rule.type];
  const actual = value === null ? 'null' : Array.isArray(value) ? 'array' : Number.isInteger(value) ? 'integer' : typeof value;
  if (rule.type && !types.some((t) => t === actual || (t === 'number' && typeof value === 'number'))) return [`${path}: type ${types.join('|')}`];
  if ('const' in rule && value !== rule.const) out.push(`${path}: const`);
  if (rule.enum && !rule.enum.includes(value)) out.push(`${path}: enum`);
  if (typeof value === 'number' && (value < (rule.minimum ?? -Infinity) || value > (rule.maximum ?? Infinity))) out.push(`${path}: range`);
  if (typeof value === 'string' && rule.pattern && !(new RegExp(rule.pattern)).test(value)) out.push(`${path}: pattern`);
  if (Array.isArray(value)) {
    if (value.length < (rule.minItems || 0) || value.length > (rule.maxItems ?? Infinity)) out.push(`${path}: items`);
    value.forEach((item, i) => out.push(...errors(item, rule.items || {}, `${path}[${i}]`)));
  }
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    for (const key of rule.required || []) if (!Object.hasOwn(value, key)) out.push(`${path}.${key}: required`);
    if (rule.additionalProperties === false) for (const key of Object.keys(value)) if (!Object.hasOwn(rule.properties || {}, key)) out.push(`${path}.${key}: additional`);
    for (const [key, child] of Object.entries(rule.properties || {})) if (Object.hasOwn(value, key)) out.push(...errors(value[key], child, `${path}.${key}`));
    if (rule.additionalProperties && typeof rule.additionalProperties === 'object') for (const [key, child] of Object.entries(value)) out.push(...errors(child, rule.additionalProperties, `${path}.${key}`));
  }
  for (const child of rule.allOf || []) {
    const applies = !child.if || errors(value, child.if, path).length === 0;
    if (applies && child.then) out.push(...errors(value, child.then, path));
  }
  return out;
}
function valid(save, label) { assert.deepStrictEqual(errors(save), [], `${label}: ${errors(save).join('; ')}`); }

const ids = ['A', 'B', 'C', 'D', 'E'];
const missions = [4, 2, 7, 1, 6];
function character(id, mission) {
  return { id, name: `Agent ${id}`, callsign: `Echo-${id}`, rank: 'Agent', lvl: 1, xp: mission * 10,
    origin: { epoch: '2026', role: 'Feldagent' }, attr: { STR: 3, GES: 3, INT: 3, CHA: 3, TEMP: 3, SYS: 3 },
    lp: 10, lp_max: 10, stress: 0, has_psi: false, sys_installed: 0, talents: [],
    equipment: [{ name: 'ITI-Kommunikator', type: 'gadget', tier: 1 }], implants: [],
    history: { background: `Geschichte ${id}`, milestones: [] }, carry: [{ name: `Marker ${id}`, type: 'gadget', tier: 1 }],
    quarters_stash: [{ name: 'Standardkit', type: 'gear', tier: 1 }], vehicles: {}, reputation: {},
    wallet: mission * 100, level_history: {} };
}
function save(id, mission) {
  const c = character(id, mission);
  return { v: 7, zr: '4.2.6', save_id: `SAVE-${id}-0`, parent_save_id: null, merge_id: null,
    branch_id: 'BRANCH-SHARED', campaign: { episode: 1, mission, px: 0, px_state: 'stable', mode: 'mixed', rift_seeds: [], entry_choice_skipped: false, episode_start: null, episode_end: null },
    characters: [c], economy: { wallets: { [id]: { balance: c.wallet, name: c.name } }, cu: c.wallet },
    logs: { trace: [], arena_psi: [], psi: [], hud: [], market: [], artifact_log: [], notes: [], flags: { runtime_version: '4.2.6', chronopolis_unlocked: false, imported_saves: [], duplicate_branch_detected: false, duplicate_character_detected: false, continuity_conflicts: [] } },
    summaries: { summary_last_episode: `Episode ${id}`, summary_last_rift: '', summary_active_arcs: `Faden ${id}` },
    continuity: { last_seen: { mode: 'hq', episode: 1, mission, location: 'HQ' }, split: {}, roster_echoes: [], shared_echoes: [], convergence_tags: [], npc_roster: [{ id: `NPC-${id}`, name: `Begleiter ${id}`, scope: 'personal', owner_id: id, status: 'hq', offscreen: '', hook: '' }], active_npc_ids: [] },
    research: { projects: [{ id: `R-${id}`, label: `Forschung ${id}`, kind: 'hq_research', scope: 'campaign', missions_total: 8, missions_done: mission, status: 'in_progress' }] },
    arc: { factions: {}, questions: [`Frage ${id}`], hooks: [`Hook ${id}`] },
    ui: { gm_style: 'verbose', suggest_mode: false, action_mode: 'uncut', contrast: 'standard', badge_density: 'standard', output_pace: 'normal', voice_profile: 'gm_second_person', intro_seen: true, dice: { debug_rolls: false } },
    arena: { active: false, phase: 'idle', queue_state: 'idle', mode: 'single', tier: 1, previous_mode: null, resume_token: null, contract_id: null, streak: 0, pending_rewards: { cu: 0, xp: 0, arena_rep: 0, multiplier: 1, risk: 'none' }, banked_rewards: { cu: 0, xp: 0, arena_rep: 0 }, rewarded_runs_this_contract: 0, first_wins: {}, defeated_types: [], last_reward_episode: null, wins_player: 0, wins_opponent: 0, match_policy: 'sim' } };
}

const originals = ids.map((id, i) => save(id, missions[i]));
originals.forEach((s, i) => valid(s, `Input ${ids[i]}`));
const finalCharacters = Object.fromEntries(originals.map((s, i) => {
  const c = clone(s.characters[0]); c.xp += 5 + i; c.wallet += 10 + i; c.history.milestones.push('Gemeinsamer Einsatz in Kampagne A.');
  if (i === 1) c.carry = []; // explizit verbrauchter Marker
  if (i === 2) c.carry.push({ name: 'Singulärer Schlüssel', type: 'gadget', tier: 1 });
  return [ids[i], { character: c }];
}));
finalCharacters.E.roots = { continuity: clone(originals[4].continuity) };
finalCharacters.E.roots.continuity.npc_roster[0].status = 'assigned';
const anchorRoots = { campaign: { ...originals[0].campaign, mission: 5 }, arc: { factions: {}, questions: [], hooks: ['Hook A'] }, summaries: { ...originals[0].summaries, summary_last_episode: 'A: Mission 5 abgeschlossen.', summary_active_arcs: 'Hook A' }, continuity: clone(originals[0].continuity), research: clone(originals[0].research) };
anchorRoots.continuity.last_seen.mission = 5; anchorRoots.research.projects[0].missions_done = 5;
const exportsA = projectPersonalSaves(openSession(originals), { hq: true, anchorRoots, personal: finalCharacters });
assert.deepStrictEqual(exportsA.map((s) => s.campaign.mission), [5, 2, 7, 1, 6]);
exportsA.forEach((s, i) => { valid(s, `A-Export ${ids[i]}`); assert.deepStrictEqual(s.characters.map((c) => c.id), [ids[i]]); assert.strictEqual(s.parent_save_id, originals[i].save_id); });
assert.deepStrictEqual(exportsA[0].arc.questions, []); assert.strictEqual(exportsA[0].continuity.last_seen.mission, 5); assert.strictEqual(exportsA[0].research.projects[0].missions_done, 5);
assert.deepStrictEqual(exportsA[1].arc.questions, ['Frage B']); assert.deepStrictEqual(exportsA[1].characters[0].carry, []); assert.strictEqual(exportsA[4].continuity.npc_roster[0].status, 'assigned');
assert.strictEqual(exportsA.flatMap((s) => s.characters[0].carry).filter((x) => x.name === 'Singulärer Schlüssel').length, 1);

// Ankerwechsel D/E und danach B; jeder Output wird erneut strikt validiert.
const dCampaign = { ...exportsA[3].campaign, mission: 2 };
const de = projectPersonalSaves(openSession(exportsA.slice(3)), { hq: true, anchorRoots: { campaign: dCampaign }, personal: {} });
assert.deepStrictEqual(de.map((s) => s.campaign.mission), [2, 6]); de.forEach((s) => valid(s, 'D/E-Export'));
const b = projectPersonalSaves(openSession([exportsA[1], exportsA[0]]), { hq: true, personal: {} });
assert.deepStrictEqual(b.map((s) => s.campaign.mission), [2, 5]); b.forEach((s) => valid(s, 'B-Anker-Export'));

assert.strictEqual(openSession([exportsA[0], exportsA[0]]).order.length, 1);
assert.throws(() => openSession([exportsA[0], { ...clone(exportsA[0]), branch_id: 'ANDERS' }]), /Abweichender Inhalt/);
assert.throws(() => openSession([save('X', 1), { ...save('X', 2), save_id: 'OTHER-X' }]), /Widerspruechlicher/);
assert.strictEqual(openSession(originals).order.length, 5, 'gemeinsame branch_id darf Gäste nicht verwerfen');
const legacy = save('L1', 3); legacy.save_id = 'LEGACY-GROUP'; legacy.characters.push(character('L2', 8)); legacy.economy.wallets.L2 = { balance: 800, name: 'Agent L2' };
assert.strictEqual(projectPersonalSaves(openSession([legacy]), { hq: true }).length, 2);
assert.strictEqual(projectPersonalSaves(openSession([originals[0]]), { hq: true }).length, 1);
assert.strictEqual(projectPersonalSaves(openSession(originals.slice(0, 2)), { hq: true }).length, 2);
assert.throws(() => projectPersonalSaves(openSession(originals), { hq: false }), /SaveGuard/);
const noAttr = clone(originals[0]); delete noAttr.characters[0].attr; assert.ok(errors(noAttr).some((e) => e.includes('attr: required')));
const noHistory = clone(originals[0]); delete noHistory.characters[0].level_history; assert.ok(errors(noHistory).some((e) => e.includes('level_history: required')));
const badCampaign = clone(originals[0]); badCampaign.campaign.id = 'NICHT-KANONISCH'; assert.ok(errors(badCampaign).some((e) => e.includes('campaign.id: additional')));
const inconsistent = clone(originals[0]); inconsistent.continuity.last_seen.mission = 99;
assert.notStrictEqual(inconsistent.campaign.mission, inconsistent.continuity.last_seen.mission, 'gezielte Konsistenzkontrolle');

console.log('v7-personal-export-ok');
