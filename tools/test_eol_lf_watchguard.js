const assert = require('assert');
const path = require('path');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.resolve(__dirname, '..');
const { readText } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'EolLfWatchguard'
});

function checkLfOnly(relPath, minLf) {
  const raw = readText(relPath);
  const crCount = (raw.match(/\r/g) || []).length;
  const lfCount = (raw.match(/\n/g) || []).length;

  assert.strictEqual(crCount, 0, `${relPath}: CR-Zeichen gefunden (${crCount}).`);
  assert.ok(lfCount >= minLf, `${relPath}: zu wenige LF-Zeilen (${lfCount} < ${minLf}).`);
}

checkLfOnly('scripts/smoke.sh', 80);
checkLfOnly('.gitattributes', 6);

console.log('eol-lf-watchguard-ok');
