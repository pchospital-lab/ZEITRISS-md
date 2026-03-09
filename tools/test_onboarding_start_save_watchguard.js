const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.join(__dirname, '..');

function readText(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

const startDocs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md',
  'core/spieler-handbuch.md'
];

const startContractRules = [
  {
    label: 'natürliche-sprache-anker',
    regex: /natürliche(?:r|n)?\s+sprache/i,
    minHits: 4
  },
  {
    label: 'klassisch-als-standard',
    regex: /klassisch[^\n]{0,140}(?:als\s+standard|standardpfad)/i,
    minHits: 3
  },
  {
    label: 'generate-custom-manuell',
    regex: /generate[^\n]*custom\s+generate[^\n]*(?:manuell|selbst\s+bauen)/i,
    minHits: 3
  }
];

for (const rule of startContractRules) {
  let hits = 0;
  for (const relPath of startDocs) {
    const text = readText(relPath);
    if (rule.regex.test(text)) hits += 1;
  }
  assert.ok(
    hits >= rule.minHits,
    `Startvertrag-Drift: Regel '${rule.label}' nur in ${hits}/${startDocs.length} Dokumenten gefunden (mind. ${rule.minHits}).`
  );
}

const hqDocs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md',
  'systems/gameflow/speicher-fortsetzung.md'
];

let saveHintHits = 0;
let noAutoBriefingHits = 0;
let newChatHintHits = 0;

for (const relPath of hqDocs) {
  const text = readText(relPath);
  if (/deepsave\s+möglich/i.test(text)) saveHintHits += 1;
  if (/(?:kein\s+automatisches?[^\n.]*briefing|kein\s+auto-weiterleitungsdruck[^\n.]*briefing|nicht\s+automatisch[^\n.]*briefing)/i.test(text)) {
    noAutoBriefingHits += 1;
  }
  if (/(?:neuen\s+chat[^\n.]*empfohlen|neuer\s+chat[^\n.]*empfohlen)/i.test(text)) {
    newChatHintHits += 1;
  }
}

assert.ok(saveHintHits >= 2, `HQ-Save-Hinweisdrift: 'Deepsave möglich' nur ${saveHintHits}/4 Treffer.`);
assert.ok(noAutoBriefingHits >= 2, `HQ-Flow-Drift: 'kein Auto-Briefing' nur ${noAutoBriefingHits}/4 Treffer.`);
assert.ok(newChatHintHits >= 2, `Chatwechsel-Hinweisdrift: 'neuer Chat empfohlen' nur ${newChatHintHits}/4 Treffer.`);

console.log('onboarding-start-save-watchguard-ok');
