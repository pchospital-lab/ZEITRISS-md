const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.join(__dirname, '..');
const target = 'characters/charaktererschaffung-grundlagen.md';
const text = fs.readFileSync(path.join(ROOT, target), 'utf8');

assert.ok(
  !/charaktererschaffung-optionen\.md/i.test(text),
  'Default-Slot-Drift: charaktererschaffung-grundlagen.md referenziert das optionale Modul charaktererschaffung-optionen.md.'
);

console.log('default-slot-dependency-watchguard-ok');
