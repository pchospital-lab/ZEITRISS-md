const fs = require('fs');
const path = require('path');
const assert = require('assert');

function readJson(relPath){
  const abs = path.join(__dirname, '..', relPath);
  return JSON.parse(fs.readFileSync(abs, 'utf8'));
}

function assertBaseV7(save, label){
  assert.strictEqual(save.v, 7, `${label}: v muss 7 sein.`);
  assert.strictEqual(typeof save.zr, 'string', `${label}: zr fehlt.`);
  assert.strictEqual(save.location, 'HQ', `${label}: nur HQ-Saves sind kanonisch.`);
  assert.ok(Array.isArray(save.characters), `${label}: characters[] fehlt.`);
  assert.ok(save.economy && Number.isFinite(save.economy.hq_pool), `${label}: economy.hq_pool fehlt.`);
  assert.ok(save.campaign && typeof save.campaign.px_state === 'string', `${label}: campaign.px_state fehlt.`);
  assert.ok(save.logs && save.logs.flags && Array.isArray(save.logs.flags.continuity_conflicts), `${label}: logs.flags.continuity_conflicts[] fehlt.`);
}

const highLevel = readJson('internal/qa/fixtures/savegame_v7_5er_hq_highlevel.json');
assertBaseV7(highLevel, '5er-highlevel');
assert.strictEqual(highLevel.characters.length, 5, '5er-highlevel: Es müssen 5 Agenten sein.');
assert.ok(highLevel.characters.every((entry) => entry.lvl >= 900), '5er-highlevel: Alle Agenten brauchen Lvl 900+.');
const auditBand = highLevel.logs.trace.find((entry) => entry.event === 'economy_audit')?.target_range?.level_band;
assert.strictEqual(auditBand, '900+', '5er-highlevel: Economy-Band muss 900+ sein.');

const splitMerge = readJson('internal/qa/fixtures/savegame_v7_split_3_2_merge.json');
assertBaseV7(splitMerge, 'split-3-2');
const importedSplit = splitMerge.logs.flags.imported_saves || [];
assert.strictEqual(importedSplit.length, 2, 'split-3-2: Beide Rift-Branches müssen protokolliert sein.');
assert.ok(importedSplit.every((entry) => entry.status === 'merged'), 'split-3-2: Importstatus muss merged sein.');
assert.ok(importedSplit.every((entry) => typeof entry.save_id === 'string' && typeof entry.branch_id === 'string'), 'split-3-2: imported_saves braucht save_id+branch_id.');
assert.strictEqual(splitMerge.continuity?.split?.family_id, 'EP7-RIFT-FORK-01', 'split-3-2: split.family_id fehlt.');
assert.strictEqual(splitMerge.continuity?.split?.convergence_ready, true, 'split-3-2: convergence_ready muss true sein.');
assert.ok((splitMerge.continuity?.convergence_tags || []).includes('boss_tell:morgenrot'), 'split-3-2: convergence_tag-Nachweis fehlt.');

const riftPvp = readJson('internal/qa/fixtures/savegame_v7_merge_rift_pvp.json');
assertBaseV7(riftPvp, 'rift-pvp');
assert.strictEqual(riftPvp.arena.active, false, 'rift-pvp: Arena muss vor HQ-Save inaktiv sein.');
assert.ok(['idle', 'completed'].includes(riftPvp.arena.queue_state), 'rift-pvp: queue_state muss idle|completed sein.');

const mixedImported = riftPvp.logs.flags.imported_saves || [];
assert.ok(mixedImported.length >= 2, 'rift-pvp: Mixed-Imports müssen protokolliert sein.');
assert.ok(mixedImported.every((entry) => entry.reason === 'non_canonical_branch'), 'rift-pvp: Mixed-Imports brauchen reason=non_canonical_branch.');
assert.ok(mixedImported.every((entry) => Array.isArray(entry.allowed_fields) && entry.allowed_fields.includes('wallet')), 'rift-pvp: Allowlist-Felder fehlen.');
assert.ok((riftPvp.logs.market || []).some((entry) => entry.event === 'chronopolis_log'), 'rift-pvp: Chronopolis-Lognachweis fehlt.');
assert.ok((riftPvp.logs.notes || []).some((note) => /Nicht-kanonischer Branch-Import/i.test(note)), 'rift-pvp: Hinweistext für nicht-kanonischen Import fehlt.');

const chronopolis = readJson('internal/qa/fixtures/savegame_v7_chronopolis_roundtrip.json');
assertBaseV7(chronopolis, 'chronopolis-roundtrip');
const chronoEvents = (chronopolis.logs.trace || []).map((entry) => entry.event);
assert.ok(chronoEvents.includes('chronopolis_enter') && chronoEvents.includes('chronopolis_return_hq'), 'chronopolis-roundtrip: Enter/Return-Ereignisse fehlen.');

const abortResume = readJson('internal/qa/fixtures/savegame_v7_abort_resume.json');
assertBaseV7(abortResume, 'abort-resume');
const abortEvents = (abortResume.logs.trace || []).map((entry) => entry.event);
assert.ok(abortEvents.includes('abort_to_hq') && abortEvents.includes('resume_planned'), 'abort-resume: Abort/Resume-Pfad fehlt.');
const abortImported = abortResume.logs.flags.imported_saves || [];
assert.ok(abortImported.some((entry) => entry.reason === 'non_canonical_branch' && (entry.allowed_fields || []).includes('abort_marker')), 'abort-resume: non-canonical Abort-Import fehlt.');

const chatLoad = readJson('internal/qa/fixtures/savegame_v7_chat_load.json');
assertBaseV7(chatLoad, 'chat-load');
assert.ok((chatLoad.logs.notes || []).some((note) => /JSON-Paste/i.test(note)), 'chat-load: Chat-Load-Hinweis fehlt.');

const refusal = readJson('internal/qa/fixtures/v7_parallel_core_refusal.json');
assert.strictEqual(refusal.supported, true, 'parallel-core-refusal: supported muss true sein.');
assert.ok(/kanonisch.*continuity\.split\.family_id/i.test(refusal.acceptance_text), 'parallel-core-refusal: Acceptance-Text fehlt oder unklar.');

console.log('v7-issue-pack-ok');
