const assert = require('assert');
const { openSession, projectPersonalSaves } = require('./lib/personal_save_projection');

const missions = [4, 2, 7, 1, 6];
const ids = ['A', 'B', 'C', 'D', 'E'];
const requiredRoots = ['v', 'zr', 'save_id', 'parent_save_id', 'merge_id', 'branch_id', 'campaign',
  'characters', 'economy', 'logs', 'summaries', 'continuity', 'research', 'arc', 'ui', 'arena'];

function save(id, mission) {
  return {
    v: 7, zr: '4.2.6', save_id: `SAVE-${id}-0`, parent_save_id: null, merge_id: null,
    branch_id: `BRANCH-${id}`, campaign: { id: `CAMPAIGN-${id}`, episode: 1, mission, px: 0,
      px_state: 'stable', mode: 'mixed', rift_seeds: [] },
    characters: [{ id, name: `Agent ${id}`, xp: mission * 10, wallet: mission * 100,
      carry: [], history: { background: `Geschichte ${id}`, milestones: [] } }],
    economy: { wallets: { [id]: { balance: mission * 100, name: `Agent ${id}` } } },
    logs: { trace: [], flags: { continuity_conflicts: [] } },
    summaries: { summary_last_episode: `Episode ${id}`, summary_last_rift: '', summary_active_arcs: `Faden ${id}` },
    continuity: { last_seen: { mode: 'hq', location: 'HQ' }, split: {}, roster_echoes: [], shared_echoes: [],
      convergence_tags: [], npc_roster: [{ id: `NPC-${id}`, name: `Begleiter ${id}`, scope: 'personal', owner_id: id,
        status: 'hq', offscreen: '', hook: '' }], active_npc_ids: [] },
    research: { projects: [{ id: `RESEARCH-${id}`, scope: 'campaign', missions_done: mission }] },
    arc: { factions: {}, questions: [`Frage ${id}`], hooks: [`Hook ${id}`] },
    ui: { gm_style: 'verbose', intro_seen: true }, arena: { active: false, phase: 'idle', queue_state: 'idle' }
  };
}

const originals = ids.map((id, i) => save(id, missions[i]));
const session = openSession(originals);
const completion = { hq: true, memory: 'Gemeinsamer Einsatz in Kampagne A.',
  anchorCampaign: { ...originals[0].campaign, mission: 5 },
  personal: Object.fromEntries(ids.map((id, i) => [id, { xp: 5 + i, cu: 10 + i,
    items: i === 2 ? [{ id: 'UNIQUE-C', name: 'Singulärer Schlüssel', type: 'gadget', tier: 1 }] : [] }])) };
const exportsA = projectPersonalSaves(session, completion);

assert.strictEqual(exportsA.length, 5);
exportsA.forEach((out, i) => {
  requiredRoots.forEach((root) => assert.ok(Object.hasOwn(out, root), `${ids[i]}: Root ${root} fehlt`));
  assert.deepStrictEqual(out.characters.map((c) => c.id), [ids[i]]);
  assert.strictEqual(out.campaign.id, `CAMPAIGN-${ids[i]}`);
  assert.strictEqual(out.campaign.mission, i === 0 ? 5 : missions[i]);
  assert.strictEqual(out.characters[0].xp, missions[i] * 10 + 5 + i);
  assert.strictEqual(out.characters[0].wallet, missions[i] * 100 + 10 + i);
  assert.strictEqual(out.continuity.npc_roster[0].owner_id, ids[i]);
  assert.ok(out.characters[0].history.milestones.includes(completion.memory));
});
assert.strictEqual(exportsA.flatMap((s) => s.characters[0].carry).filter((x) => x.id === 'UNIQUE-C').length, 1);

// Jeder Export ist allein ladbar; der erste Save eines neuen Chats setzt neu den Anker.
exportsA.forEach((out) => assert.strictEqual(openSession([out]).anchorId, out.characters[0].id));
assert.strictEqual(openSession(exportsA.slice(0, 3)).byCharacter.get('A').save.campaign.mission, 5);
assert.strictEqual(openSession(exportsA.slice(3)).anchorId, 'D');
const de = projectPersonalSaves(openSession(exportsA.slice(3)), { hq: true,
  anchorCampaign: { ...exportsA[3].campaign, mission: 2 }, personal: { D: { xp: 2 }, E: { xp: 3 } } });
assert.deepStrictEqual(de.map((s) => s.campaign.mission), [2, 6]);
assert.strictEqual(openSession([exportsA[1], exportsA[0]]).anchorId, 'B');

// Identischer Import dedupliziert, Legacy-Sammelsave wird pro Figur projiziert, Solo/Duo stimmen.
assert.strictEqual(openSession([exportsA[0], exportsA[0]]).order.length, 1);
const legacy = save('L1', 3); legacy.save_id = 'LEGACY-GROUP'; legacy.characters.push(save('L2', 8).characters[0]);
legacy.economy.wallets.L2 = { balance: 800, name: 'Agent L2' };
assert.strictEqual(projectPersonalSaves(openSession([legacy]), { hq: true }).length, 2);
assert.strictEqual(projectPersonalSaves(openSession([exportsA[0]]), { hq: true }).length, 1);
assert.strictEqual(projectPersonalSaves(openSession(exportsA.slice(0, 2)), { hq: true }).length, 2);
assert.throws(() => projectPersonalSaves(session, { hq: false }), /SaveGuard/);
assert.throws(() => openSession([save('X', 1), { ...save('X', 2), save_id: 'OTHER-X' }]), /Widerspruechlicher/);

console.log('v7-personal-campaign-export-ok');
