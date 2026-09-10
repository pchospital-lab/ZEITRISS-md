'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync, spawnSync } = require('child_process');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');

function verifyZip(zip, expectedRoot = root) {
  const checked = JSON.parse(execFileSync('python3', ['-c', [
    'import hashlib,json,pathlib,sys,zipfile',
    'with zipfile.ZipFile(sys.argv[1]) as z:',
    ' names=[n for n in z.namelist() if not n.endswith("/")]',
    ' prefix=names[0].split("/")[0]+"/"',
    ' manifest=json.loads(z.read(prefix+"BUILD-MANIFEST.json"))',
    ' for item in manifest["files"]:',
    '  data=z.read(prefix+item["path"])',
    '  assert len(data)==item["bytes"] and hashlib.sha256(data).hexdigest()==item["sha256"]',
    '  if item.get("source") and len(sys.argv)>2: assert data==(pathlib.Path(sys.argv[2])/item["source"]).read_bytes()',
    ' print(json.dumps({"names":names,"prefix":prefix,"manifest":manifest}))',
  ].join('\n'), zip, ...(expectedRoot ? [expectedRoot] : [])], { encoding: 'utf8' }));
  const { names, prefix, manifest } = checked;
  assert(names.length > 0, 'ZIP ist leer oder beschädigt');
  assert(names.every((name) => name.startsWith(prefix)), 'uneinheitliches ZIP-Wurzelverzeichnis');
  assert.strictEqual(manifest.project_version, '4.2.6');
  assert.strictEqual(manifest.knowledge_slots, 19);
  assert.strictEqual(manifest.files.filter((f) => f.path.startsWith('knowledge/')).length, 19);
  assert.deepStrictEqual(names.slice().sort(), ['BUILD-MANIFEST.json', ...manifest.files.map((f) => f.path)]
    .map((name) => prefix + name).sort(), 'Manifest-Dateiliste stimmt nicht mit ZIP überein');
  assert(names.includes(prefix + 'LICENSE'), 'Lizenzhinweis fehlt');
  assert(!names.some((n) => /(^|\/)(\.env|runtime\.js|internal|docs|AGENTS\.md)(\/|$)/.test(n)));
  return manifest;
}

// Im Workflow wird genau das hochzuladende Artefakt geprüft, nicht ein zweiter Export.
if (process.env.PACK_ZIP) {
  verifyZip(path.resolve(process.env.PACK_ZIP));
  console.log('player-feedback-pack-zip-ok');
  process.exit(0);
}

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'zeitriss-pack-'));
try {
  for (const flat of [false, true]) {
    const args = ['scripts/setup.py', '--export', '--out', tmp];
    if (flat) args.push('--flat');
    execFileSync('python3', args, { cwd: root });
  }
  const dirs = fs.readdirSync(tmp).filter((n) => fs.statSync(path.join(tmp, n)).isDirectory());
  assert.strictEqual(dirs.length, 2, 'structured und flat brauchen getrennte Verzeichnisse');
  assert(dirs.some((n) => n.includes('-structured-')) && dirs.some((n) => n.includes('-flat-')));
  for (const name of dirs) {
    const pack = path.join(tmp, name);
    const manifest = verifyZip(`${pack}.zip`);
    assert.strictEqual(manifest.source_provenance, 'confirmed-git');
    assert.match(manifest.source_commit, /^[0-9a-f]{40}$/);
    const { getDocText } = createDocTextLoader({ root: pack, scopeLabel: 'Player Feedback Watchguard' });
    const guide = getDocText('SETUP-ANLEITUNG.md');
    assert.match(guide, /PROJECT_BOOTSTRAP_INSTRUCTIONS\.md/);
    assert.match(guide, /SYSTEM_PROMPT_ONLY\.md/);
    assert.match(guide, /persönlichen JSON-Save/);
    assert.match(guide, /Creator Studio – separates Projekt/);
    if (name.includes('-flat-')) assert(manifest.files.some((f) => f.path === 'knowledge/01-spieler-handbuch.md'));
  }

  const sourceZip = path.join(tmp, 'source-without-git');
  execFileSync('cp', ['-a', root, sourceZip]);
  fs.rmSync(path.join(sourceZip, '.git'), { recursive: true, force: true });
  const zipOut = path.join(tmp, 'nogit-out');
  execFileSync('python3', ['scripts/setup.py', '--export', '--out', zipOut], { cwd: sourceZip });
  const noGitPack = path.join(zipOut, fs.readdirSync(zipOut).find((n) => fs.statSync(path.join(zipOut, n)).isDirectory()));
  const noGitManifest = JSON.parse(fs.readFileSync(path.join(noGitPack, 'BUILD-MANIFEST.json')));
  assert.strictEqual(noGitManifest.source_provenance, 'unconfirmed');
  assert.strictEqual(noGitManifest.source_commit, null);
  assert.notStrictEqual(spawnSync('python3', ['scripts/setup.py', '--export', '--require-clean', '--out', path.join(tmp, 'reject')], { cwd: sourceZip }).status, 0);

  for (const [missing, message] of [
    ['meta/project_bootstrap_instructions.md', /Project bootstrap not found/],
    ['meta/masterprompt_v6.md', /Masterprompt not found/],
    ['core/spieler-handbuch.md', /Required slot file missing/],
  ]) {
    const broken = path.join(tmp, `broken-${path.basename(missing)}`);
    execFileSync('cp', ['-a', sourceZip, broken]);
    fs.unlinkSync(path.join(broken, missing));
    const failed = spawnSync('python3', ['scripts/setup.py', '--export', '--out', path.join(tmp, 'negative')], { cwd: broken, encoding: 'utf8' });
    assert.notStrictEqual(failed.status, 0, `${missing} muss fehlschlagen`);
    assert.match(failed.stdout + failed.stderr, message);
  }

  const damaged = path.join(tmp, 'damaged.zip');
  fs.writeFileSync(damaged, 'kein zip');
  const damagedCheck = spawnSync('python3', ['-c', 'import sys,zipfile; zipfile.ZipFile(sys.argv[1]).testzip()', damaged]);
  assert.notStrictEqual(damagedCheck.status, 0, 'beschädigtes ZIP muss zurückgewiesen werden');
  const launcher = fs.readFileSync(path.join(root, 'scripts/launcher.py'), 'utf8');
  const exportAction = launcher.slice(launcher.indexOf('def action_export()'), launcher.indexOf('def _open_folder'));
  assert.match(exportAction, /except SystemExit as exc:[\s\S]*?_pause\(\)\s*return/, 'Exportfehler muss vor Erfolgshinweisen zurückkehren');
  console.log('player-feedback-watchguard-ok');
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
