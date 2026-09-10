'use strict';

const assert = require('assert');
const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync, spawnSync } = require('child_process');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');
const { getDocText } = createDocTextLoader({
  root,
  scopeLabel: 'Player Feedback Watchguard',
});
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'zeitriss-pack-'));
try {
  execFileSync('python3', [path.join(root, 'scripts/setup.py'), '--export', '--out', tmp], { cwd: root });
  const dirs = fs.readdirSync(tmp).filter(n => fs.statSync(path.join(tmp, n)).isDirectory());
  assert.strictEqual(dirs.length, 1, 'genau ein Exportverzeichnis');
  const pack = path.join(tmp, dirs[0]);
  const manifest = JSON.parse(fs.readFileSync(path.join(pack, 'BUILD-MANIFEST.json'), 'utf8'));
  assert.strictEqual(manifest.project_version, '4.2.6');
  assert.match(manifest.source_commit, /^[0-9a-f]{40}$/);
  assert.strictEqual(manifest.knowledge_slots, 19);
  const knowledge = manifest.files.filter(f => f.path.startsWith('knowledge/'));
  assert.strictEqual(knowledge.length, 19);
  for (const item of manifest.files) {
    const bytes = fs.readFileSync(path.join(pack, item.path));
    assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'), item.sha256);
    if (item.source) assert.deepStrictEqual(bytes, fs.readFileSync(path.join(root, item.source)));
  }
  const { getDocText: getPackDocText } = createDocTextLoader({
    root: pack,
    scopeLabel: 'Erzeugtes Spielerfeedback-Paket',
  });
  assert.strictEqual(getPackDocText('system/SYSTEM_PROMPT_ONLY.md'),
    getDocText('meta/masterprompt_v6.md'));
  assert.strictEqual(getPackDocText('system/PROJECT_BOOTSTRAP_INSTRUCTIONS.md'),
    getDocText('meta/project_bootstrap_instructions.md'));
  assert(fs.existsSync(`${pack}.zip`), 'ZIP fehlt');
  const zipList = execFileSync('python3', ['-c',
    'import sys,zipfile; print("\\n".join(zipfile.ZipFile(sys.argv[1]).namelist()))', `${pack}.zip`],
    { encoding: 'utf8' });
  assert(zipList.includes('BUILD-MANIFEST.json'));
  assert(!/(^|\/)(\.env|runtime\.js|internal\/|docs\/|AGENTS\.md)/m.test(zipList));

  const broken = path.join(tmp, 'broken');
  execFileSync('cp', ['-a', root, broken]);
  fs.unlinkSync(path.join(broken, 'meta/project_bootstrap_instructions.md'));
  const failed = spawnSync('python3', ['scripts/setup.py', '--export', '--out', path.join(tmp, 'negative')],
    { cwd: broken, encoding: 'utf8' });
  assert.notStrictEqual(failed.status, 0, 'fehlender Pflicht-Bootstrap muss fehlschlagen');
  assert.match(failed.stdout + failed.stderr, /Project bootstrap not found/);
  console.log('player-feedback-watchguard-ok');
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
