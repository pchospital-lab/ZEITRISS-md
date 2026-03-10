const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.join(__dirname, '..');

function readText(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

const docs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md'
];

for (const relPath of docs) {
  const text = readText(relPath);

  assert.ok(
    /vor[\s\S]{0,120}briefing/i.test(text) &&
      /genau[\s\S]{0,16}ein(?:en|e)?[\s\S]{0,120}relevanzsatz/i.test(text),
    `Regie-Layer-Drift in ${relPath}: Pflichtanker 'genau ein Relevanzsatz vor Briefing' fehlt.`
  );

  assert.ok(
    /nach[\s\S]{0,140}(?:heimkehr|debrief)/i.test(text) &&
      /genau[\s\S]{0,16}ein(?:e)?[\s\S]{0,140}iti-bulletin/i.test(text),
    `Regie-Layer-Drift in ${relPath}: Pflichtanker 'genau eine ITI-Bulletin-Mikronachricht nach Heimkehr' fehlt.`
  );
}

console.log('director-layer-watchguard-ok');
