const fs = require('fs');
const path = require('path');
const assert = require('assert');

const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'internal/qa/fixtures/savegame_v7_arena_round_checkpoint.json'), 'utf8'));
const arena = fixture.arena || {};

assert.strictEqual(arena.active, false, 'Arena-Checkpoint darf nicht aktiv sein.');
assert.ok(['idle', 'completed'].includes(arena.queue_state), 'queue_state muss idle|completed sein.');
assert.ok(['idle', 'completed'].includes(arena.phase), 'phase muss idle|completed sein.');
assert.ok(arena.pending_rewards && arena.pending_rewards.cu > 0, 'pending_rewards müssen für Push-Checkpoint persistierbar sein.');
assert.strictEqual(typeof arena.first_wins, 'object', 'first_wins muss Objekt sein.');
assert.ok(!Number.isInteger(arena.first_wins), 'first_wins darf kein Integer sein.');
assert.strictEqual(fixture.campaign.px, 2, 'Arena-Checkpoint darf campaign.px nicht mutieren.');

console.log('arena-round-checkpoint-ok');
