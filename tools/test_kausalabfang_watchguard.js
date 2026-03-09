const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.join(__dirname, '..');

function readText(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

const mustHaveRegex = [
  /0\s*-?LP/i,
  /Loot\s+sichern\s*→\s*optional(?:er)?\s+Kausalabfang\s*→\s*Cleanup\/Exfil/i,
  /Chrononauten/i,
  /Boss[^\n]{0,20}Mini-?Boss/i,
  /Zivilisten/i,
  /Para\s*-?Wesen/i,
  /Arena\s*\/\s*PvP/i,
  /Chronopolis/i
];

const checks = [
  'core/spieler-handbuch.md',
  'core/sl-referenz.md',
  'systems/toolkit-gpt-spielleiter.md',
  'meta/masterprompt_v6.md',
  'characters/ausruestung-cyberware.md'
];

for (const relPath of checks) {
  const text = readText(relPath);
  assert.ok(/Kausalabfang|Never happened/i.test(text), `${relPath}: Kausalabfang/Never-happened-Anker fehlt.`);

  for (const rx of mustHaveRegex) {
    assert.ok(rx.test(text), `${relPath}: Pflichtanker fehlt (${rx}).`);
  }

  assert.ok(!/universell(?:es|er)?\s+Retcon/i.test(text), `${relPath}: driftiges Retcon-Wording gefunden.`);
}

console.log('kausalabfang-watchguard-ok');
