const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const smoke = path.join(ROOT, 'scripts', 'smoke.sh');
const text = fs.readFileSync(smoke, 'utf8');
const lines = text.split(/\r?\n/);

assert.strictEqual(lines[0], '#!/usr/bin/env bash', 'smoke.sh: Shebang muss allein in Zeile 1 stehen.');
assert.ok(lines.length >= 80, `smoke.sh: zu wenige physische Zeilen (${lines.length}) — vermutlich kollabiert.`);
assert.ok(!/^#!\/usr\/bin\/env bash\s+export\s+LANG/.test(lines[0]), 'smoke.sh: Shebang enthält Kommandos.');
assert.ok(!text.includes('verankerte HQ-Projektion) node'), 'smoke.sh: Kommentar/Text und node-Befehl sind kollabiert.');
assert.ok(text.includes('set -euo pipefail'), 'smoke.sh: set -euo pipefail fehlt.');
assert.ok(lines.every((line) => line.length < 500), 'smoke.sh: mindestens eine Monsterzeile >500 Zeichen.');
assert.ok(!/#[^\n]{120,}\b(node|python3|grep)\b/.test(text), 'smoke.sh: Kommentarzeile kollabiert mit ausführbarem Kommando.');

execFileSync('bash', ['-n', smoke], { stdio: 'pipe' });

console.log('smoke-script-sanity-ok');
