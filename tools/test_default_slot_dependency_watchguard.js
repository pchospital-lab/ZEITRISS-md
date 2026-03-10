const path = require('path');
const assert = require('assert');
const { resolveUniqueMarkdownTarget } = require('./watchguard_file_resolver');

const ROOT = path.join(__dirname, '..');

const { file: targetFile, text } = resolveUniqueMarkdownTarget({
  root: ROOT,
  preferredRelPaths: ['characters/charaktererschaffung-grundlagen.md'],
  candidatePathRegex: /charaktererschaffung-grundlagen\.md$/i,
  contentPredicates: [/Ordo\s+Mnemonika/i, /Retina-Linse/i],
  label: 'Default-Slot-Dependency-Watchguard'
});

assert.ok(
  !/charaktererschaffung-optionen\.md/i.test(text),
  `Default-Slot-Drift: ${path.relative(ROOT, targetFile)} referenziert das optionale Modul charaktererschaffung-optionen.md.`
);

console.log('default-slot-dependency-watchguard-ok');
