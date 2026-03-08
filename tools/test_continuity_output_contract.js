const fs = require('fs');
const path = require('path');
const assert = require('assert');

function readJson(relPath){
  const abs = path.join(__dirname, '..', relPath);
  return JSON.parse(fs.readFileSync(abs, 'utf8'));
}

const fixture = readJson('internal/qa/fixtures/continuity_output_contract_multi_load.json');

assert.strictEqual(typeof fixture.scenario_id, 'string', 'scenario_id fehlt.');
assert.ok(fixture.session_anchor && typeof fixture.session_anchor.save_id === 'string', 'session_anchor.save_id fehlt.');
assert.ok(Array.isArray(fixture.imports) && fixture.imports.length >= 1, 'imports[] fehlt oder ist leer.');

const recap = fixture.output_contract?.continuity_recap;
assert.ok(recap, 'output_contract.continuity_recap fehlt.');
assert.strictEqual(typeof recap.session_anchor, 'string', 'Recap-Block 1 (session_anchor) fehlt.');
assert.ok(Array.isArray(recap.returnees) && recap.returnees.length >= 1, 'Recap-Block 2 (returnees) fehlt.');
assert.ok(Array.isArray(recap.shared_aftermath) && recap.shared_aftermath.length >= 2, 'Recap-Block 3 (shared_aftermath) fehlt.');
assert.strictEqual(typeof recap.convergence_consequence, 'string', 'Recap-Block 4 (convergence_consequence) fehlt.');

const beats = fixture.output_contract?.beats;
assert.strictEqual(beats?.split_beat?.played, true, 'Split-Beat fehlt (played=true erwartet).');
assert.strictEqual(beats?.rejoin_hq_beat?.played, true, 'Rejoin-HQ-Beat fehlt (played=true erwartet).');

const followup = fixture.output_contract?.echo_followup;
assert.ok(followup, 'echo_followup fehlt.');
assert.strictEqual(followup.window_session_blocks, 2, 'Echo-Fenster muss 2 Sitzungsblöcke sein.');
assert.ok(Number.isInteger(followup.manifested_in_block), 'manifested_in_block muss integer sein.');
assert.ok(followup.manifested_in_block <= followup.window_session_blocks, 'Echo-Fortwirkung liegt außerhalb des 2-Block-Fensters.');

const importedEchoRef = followup.imported_echo_ref;
assert.strictEqual(typeof importedEchoRef, 'string', 'imported_echo_ref fehlt.');
const [scope, tag] = importedEchoRef.split(':');
assert.ok(scope === 'shared' || scope === 'roster', 'imported_echo_ref muss shared:<tag> oder roster:<char_id> sein.');
if (scope === 'shared') {
  const shared = fixture.continuity?.shared_echoes || [];
  assert.ok(shared.some((entry) => entry.tag === tag), 'echo_followup referenziert keinen vorhandenen shared_echo.');
} else {
  const roster = fixture.continuity?.roster_echoes || [];
  assert.ok(roster.some((entry) => entry.char_id === tag), 'echo_followup referenziert keinen vorhandenen roster_echo.');
}

const manifestation = followup.manifested_as;
assert.ok(['boss_tell', 'alt_route', 'npc_reaction', 'briefing_hook'].includes(manifestation), 'manifested_as nutzt keinen erlaubten Echo-Typ.');

console.log('continuity-output-contract-ok');
