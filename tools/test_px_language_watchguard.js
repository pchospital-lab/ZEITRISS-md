const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Px-Language-Watchguard'
});

const targets = [
  'gameplay/kampagnenstruktur.md',
  'meta/masterprompt_v6.md',
  'systems/gameflow/speicher-fortsetzung.md'
];
const forbidden = [/Paradoxon\s*>?=\s*2/i, /Paradoxon\s*≥\s*2/i, /Px\s*-\s*1/i, /Px-1/i];

for (const rel of targets){
  const { text } = readMarkdown(rel, [], `Px-Language-Watchguard (${rel})`);
  for (const rx of forbidden){
    assert.ok(!rx.test(text), `${rel}: Verbotene Px/Paradoxon-Altformel gefunden (${rx}).`);
  }
}

console.log('px-language-watchguard-ok');
