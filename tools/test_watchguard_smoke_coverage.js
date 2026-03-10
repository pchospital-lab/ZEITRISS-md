const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TOOLS_DIR = path.join(ROOT, 'tools');
const SMOKE_FILE = path.join(ROOT, 'scripts', 'smoke.sh');

function listWatchguardTests() {
  return fs
    .readdirSync(TOOLS_DIR)
    .filter((file) => /^test_.*watchguard(?:_.*)?\.js$/.test(file))
    .sort();
}

function listWatchguardsFromSmoke(text) {
  const matches = [...text.matchAll(/node\s+tools\/(test_[a-z0-9_]*watchguard(?:_[a-z0-9_]+)?\.js)\b/g)];
  return matches.map((m) => m[1]);
}

const smokeText = fs.readFileSync(SMOKE_FILE, 'utf8');
const watchguardFiles = listWatchguardTests();
const smokeWatchguards = listWatchguardsFromSmoke(smokeText);

const smokeSet = new Set(smokeWatchguards);
const watchguardSet = new Set(watchguardFiles);

const missingInSmoke = watchguardFiles.filter((file) => !smokeSet.has(file));
const staleInSmoke = smokeWatchguards.filter((file) => !watchguardSet.has(file));
const duplicates = smokeWatchguards.filter((file, idx) => smokeWatchguards.indexOf(file) !== idx);

const violations = [];

if (missingInSmoke.length > 0) {
  violations.push(
    `Fehlende Smoke-Einbindung für Watchguards: ${missingInSmoke.join(', ')}`,
  );
}

if (staleInSmoke.length > 0) {
  violations.push(
    `Smoke referenziert nicht existente Watchguards: ${[...new Set(staleInSmoke)].join(', ')}`,
  );
}

if (duplicates.length > 0) {
  violations.push(
    `Smoke führt Watchguards mehrfach aus: ${[...new Set(duplicates)].join(', ')}`,
  );
}

if (violations.length > 0) {
  console.error('watchguard-smoke-coverage-fail');
  for (const v of violations) {
    console.error(`- ${v}`);
  }
  process.exit(1);
}

console.log('watchguard-smoke-coverage-ok');
