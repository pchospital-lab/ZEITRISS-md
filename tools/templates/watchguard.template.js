const path = require('path');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.resolve(__dirname, '..');
const {
  readMarkdown,
} = createDocTextLoader({ root: ROOT, scopeLabel: 'Beispiel-Watchguard' });

function assertHasPattern(text, pattern, message) {
  if (!pattern.test(text)) {
    throw new Error(message);
  }
}

const doc = readMarkdown(
  'core/spieler-handbuch.md',
  ['# Spieler-Handbuch'],
  'Spieler-Handbuch (Beispiel-Watchguard)',
);

assertHasPattern(
  doc,
  /KI-SL|Spielleitung/i,
  'Pflichtanker fehlt: KI-SL/Spielleitung muss referenziert sein.',
);

console.log('beispiel-watchguard-ok');
