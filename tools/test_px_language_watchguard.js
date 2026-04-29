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
const forbidden = [/Paradoxon\s*>?=\s*2/i, /Paradoxon\s*≥\s*2/i, /Px\s*-\s*1/i, /Px-1/i, /\|\s*Paradoxon\s*\|/i, /-1\s*\(Px\)/i, /\+\d+\s*bei\s+Psi-Einsatz/i, /\+\d+\s*bei\s+Verzögerung/i, /Paradoxon\s+0/i, /RIFT OPS.*Paradoxon/i];

for (const rel of targets){
  const { text } = readMarkdown(rel, [], `Px-Language-Watchguard (${rel})`);
  for (const rx of forbidden){
    assert.ok(!rx.test(text), `${rel}: Verbotene Px/Paradoxon-Altformel gefunden (${rx}).`);
  }
}

const { text: campaignText } = readMarkdown('gameplay/kampagnenstruktur.md', [], 'Px-Language-Watchguard (Encounter-Tabellen)');
const encounterSliceMatch = campaignText.match(/#### 2 CORE OPS-Pool \(1W12\)[\s\S]*?#### 4 FIELD DOWNTIME-Pool \(1W8\)/i);
assert.ok(encounterSliceMatch, 'gameplay/kampagnenstruktur.md: Encounter-Tabellenbereich nicht gefunden.');
const encounterSlice = encounterSliceMatch[0];
const forbiddenEncounterShorthand = [/\|\s*0-1\s*\|/i, /\|\s*\+1-2\s*\|/i, /\|\s*\+1\s*\|/i, /\|\s*\+2\s*\|/i];
for (const rx of forbiddenEncounterShorthand) {
  assert.ok(!rx.test(encounterSlice), `gameplay/kampagnenstruktur.md: Unbeschriftete Encounter-Folge gefunden (${rx}).`);
}

console.log('px-language-watchguard-ok');
