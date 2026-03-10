const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { resolveUniqueMarkdownTarget } = require('./watchguard_file_resolver');

const ROOT = path.join(__dirname, '..');

function readText(relPath){
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

function readMarkdown(relPath, anchors, label) {
  return resolveUniqueMarkdownTarget({
    root: ROOT,
    preferredRelPaths: [relPath],
    candidatePathRegex: new RegExp(`${path.basename(relPath).replace('.', '\\.')}$`, 'i'),
    contentPredicates: anchors,
    label
  });
}

const markdownDocCache = new Map();

function getDocText(relPath, anchors = [/./s], label = `NPC-Continuity-Watchguard (${relPath})`) {
  if (!relPath.endsWith('.md')) return readText(relPath);
  if (!markdownDocCache.has(relPath)) {
    const { text } = readMarkdown(relPath, anchors, label);
    markdownDocCache.set(relPath, text);
  }
  return markdownDocCache.get(relPath);
}

function readJson(relPath){
  return JSON.parse(readText(relPath));
}

const ssotDocs = [
  'meta/masterprompt_v6.md',
  'systems/gameflow/speicher-fortsetzung.md',
  'core/sl-referenz.md'
];

const requiredTokens = [
  'npc_roster',
  'active_npc_ids',
  'personal',
  'session',
  'iti'
];

const slotRuleMatchers = [
  /Menschen\s+belegen\s+Feldpl[aä]tze\s+zuerst/i,
  /mensch\s*-?vor\s*-?npc/i,
  /Menschen\s+z[aä]hlen(?:\s+\w+){0,3}\s+zuerst/i
];

let slotRuleHits = 0;
for (const relPath of ssotDocs) {
  const text = getDocText(relPath);
  for (const token of requiredTokens) {
    assert.ok(text.includes(token), `${relPath}: Pflichtanker '${token}' fehlt.`);
  }
  if (slotRuleMatchers.some((rx) => rx.test(text))) slotRuleHits += 1;
}
assert.ok(slotRuleHits >= 2, 'Slotregel Mensch-vor-NPC muss in mindestens zwei SSOT-Dokumenten explizit verankert sein.');

const fixture = readJson('internal/qa/fixtures/npc_continuity_output_contract.json');

assert.strictEqual(typeof fixture.scenario_id, 'string', 'scenario_id fehlt.');
assert.ok(Array.isArray(fixture.loaded_saves) && fixture.loaded_saves.length >= 2, 'loaded_saves[] fehlt oder ist zu klein.');

const continuity = fixture.continuity;
assert.ok(continuity && typeof continuity === 'object', 'continuity fehlt.');
assert.ok(Array.isArray(continuity.npc_roster), 'continuity.npc_roster[] fehlt.');
assert.ok(Array.isArray(continuity.active_npc_ids), 'continuity.active_npc_ids[] fehlt.');
assert.ok(continuity.npc_roster.length <= 6, 'continuity.npc_roster überschreitet Budget (max 6).');
assert.ok(continuity.active_npc_ids.length <= 4, 'continuity.active_npc_ids überschreitet Budget (max 4).');

const allowedScope = new Set(['personal', 'session', 'iti']);
const allowedStatus = new Set(['attached', 'hq', 'assigned', 'recovering', 'missing', 'rival']);

for (const npc of continuity.npc_roster) {
  assert.strictEqual(typeof npc.id, 'string', 'npc.id fehlt.');
  assert.strictEqual(typeof npc.name, 'string', `NPC ${npc.id}: name fehlt.`);
  assert.strictEqual(typeof npc.scope, 'string', `NPC ${npc.id}: scope fehlt.`);
  assert.ok(allowedScope.has(npc.scope), `NPC ${npc.id}: scope '${npc.scope}' ist ungültig.`);
  assert.strictEqual(typeof npc.status, 'string', `NPC ${npc.id}: status fehlt.`);
  assert.ok(allowedStatus.has(npc.status), `NPC ${npc.id}: status '${npc.status}' ist ungültig.`);
  assert.strictEqual(typeof npc.offscreen, 'string', `NPC ${npc.id}: offscreen fehlt.`);
  assert.ok((npc.offscreen.match(/[.!?]/g) || []).length <= 1, `NPC ${npc.id}: offscreen überschreitet 1-Satz-Regel.`);
  assert.strictEqual(typeof npc.hook, 'string', `NPC ${npc.id}: hook fehlt.`);

  if (npc.scope === 'personal') {
    assert.strictEqual(typeof npc.owner_id, 'string', `NPC ${npc.id}: personal-NPC braucht owner_id.`);
  }
}

const contract = fixture.output_contract;
assert.ok(contract && typeof contract === 'object', 'output_contract fehlt.');

assert.ok(contract.slot_resolution, 'slot_resolution fehlt.');
assert.strictEqual(contract.slot_resolution.team_cap, 5, 'team_cap muss 5 sein.');
assert.ok(contract.slot_resolution.human_slots >= 1, 'human_slots muss >=1 sein.');
assert.strictEqual(
  contract.slot_resolution.npc_slots,
  Math.max(0, 5 - contract.slot_resolution.human_slots),
  'npc_slots verletzt Mensch-vor-NPC-Slotregel.'
);

assert.ok(contract.leave_resolution, 'leave_resolution fehlt.');
assert.ok(Array.isArray(contract.leave_resolution.personal_return_with_owner_ids), 'leave_resolution.personal_return_with_owner_ids fehlt.');
assert.ok(Array.isArray(contract.leave_resolution.session_remain_with_anchor_ids), 'leave_resolution.session_remain_with_anchor_ids fehlt.');

assert.ok(contract.cross_pollination, 'cross_pollination fehlt.');
assert.strictEqual(typeof contract.cross_pollination.beat, 'string', 'cross_pollination.beat fehlt.');
assert.ok((contract.cross_pollination.beat.match(/[.!?]/g) || []).length <= 1, 'cross_pollination.beat muss kompakt (max. 1 Satz) sein.');

console.log('npc-continuity-consistency-ok');
