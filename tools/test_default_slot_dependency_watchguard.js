const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Default-Slot-Dependency-Watchguard'
});

const { file: targetFile, text } = readMarkdown(
  'characters/charaktererschaffung-grundlagen.md',
  [/Ordo\s+Mnemonika/i, /Retina-Linse/i],
  'Default-Slot-Dependency-Watchguard'
);

assert.ok(
  !/charaktererschaffung-optionen\.md/i.test(text),
  `Default-Slot-Drift: ${path.relative(ROOT, targetFile)} referenziert das optionale Modul charaktererschaffung-optionen.md.`
);

console.log('default-slot-dependency-watchguard-ok');
