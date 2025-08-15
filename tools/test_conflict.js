const assert = require('assert');

function can_open_conflict(sceneIndex, type, gate) {
  const g = gate || { threshold: 4, allow: [] };
  if ((sceneIndex + 1) >= g.threshold) return true;
  return g.allow.includes(type);
}

const sceneIndex = 1; // scene 2
const gate = { threshold: 4, allow: ['ambush', 'vehicle_chase'] };
assert.strictEqual(can_open_conflict(sceneIndex, 'firefight', gate), false);
console.log('conflict-gate-ok');
