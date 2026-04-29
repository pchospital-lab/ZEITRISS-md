const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Save-Budget-Watchguard'
});

const { text } = readMarkdown(
  'systems/gameflow/speicher-fortsetzung.md',
  [],
  'Save-Budget-Watchguard (systems/gameflow/speicher-fortsetzung.md)'
);

assert.ok(/Save-Größenbudget/.test(text), 'Save-Budget-Abschnitt fehlt in speicher-fortsetzung.md.');
assert.ok(/logs\.trace`?\s*max\s*\*\*64\*\*/i.test(text), 'Budget-Cap für logs.trace (max 64) fehlt.');
assert.ok(/logs\.market`?\s*max\s*\*\*24\*\*/i.test(text), 'Budget-Cap für logs.market (max 24) fehlt.');
assert.ok(/arc\.hooks`?\s*max\s*\*\*18\*\*/i.test(text), 'Budget-Cap für arc.hooks (max 18) fehlt.');
assert.ok(/roster_echoes[\s\S]{0,40}max\s*5/i.test(text), 'Budget-Cap für continuity.roster_echoes[] (max 5) fehlt.');
assert.ok(/shared_echoes[\s\S]{0,40}max\s*6/i.test(text), 'Budget-Cap für continuity.shared_echoes[] (max 6) fehlt.');

console.log('save-budget-watchguard-ok');
