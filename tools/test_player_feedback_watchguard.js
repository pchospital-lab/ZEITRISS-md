'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync, spawnSync } = require('child_process');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');
const setup = JSON.parse(fs.readFileSync(path.join(root, 'setup.json')));
const index = JSON.parse(fs.readFileSync(path.join(root, 'master-index.json')));
const slotSources = [...new Set(index.modules.filter((m) => m.slot === true)
  .map((m) => m.path.split('#')[0]))];
assert.strictEqual(slotSources.length, 19, 'master-index.json muss 19 eindeutige Slot-Quellen liefern');
const { getDocText: getRepoDocText } = createDocTextLoader({ root, scopeLabel: 'Player Feedback Watchguard' });
const psi = getRepoDocText('systems/kp-kraefte-psi.md');
const pyro = psi
  .split('### Pyrokinese')[1].split('\n### ')[0];
for (const contract of [
  /\| Psioniker 1, TEMP 3 \| Low \| 1 \| 0 \|/, /Medium \| 2 \| 1 frei \|/, /High \| 3 \| 2 frei \|/,
  /kraftspezifische Mindest-Fokuslast/, /allgemeine 0-SYS-Impulsregel hebt diese\s+Mindest-Fokuslast nicht auf/,
  /keine zweite Ausweichprobe/, /Anti-Psi-Gitter erhöht den SG um \+2/, /SYS wird frei, PP,/,
  /kritischer Patzer kann weiterhin die bestehende\s+Backlash-Tabelle/, /kein Brand/, /selbstständig weiter/,
  /⌊TEMP 5\/2⌋=2/, /SYS-Belegung wieder 1\/4/,
]) assert.match(pyro, contract, `Pyrokinese-Vertrag fehlt: ${contract}`);

const generalCosts = psi.slice(0, psi.indexOf('### Pyrokinese'));
assert.strictEqual((generalCosts.match(/\[Pyrokinese\]\(#pyrokinese\)/g) || []).length, 2,
  'beide allgemeinen Kosten-Kurzstellen müssen die Pyrokinese-Ausnahme verlinken');
assert.match(generalCosts, /Effekt unter 1 Sekunde kostet 0 SYS; ausgenommen[^\n]*\n[^\n]*Mindest-Fokuslast/);
assert.match(generalCosts, /Kurze Effekte \(<1 Sekunde\) kosten 0 SYS;[^\n]*Mindest-Fokuslast/);
const sysShortRule = psi.split('### Psi-SYS-Kurzregel')[1].split('\n### ')[0];
assert.match(sysShortRule, /Impuls unter 1 Sekunde[^\n]*\[Pyrokinese\]\(#pyrokinese\)/,
  'die allgemeine Impuls-Tabelle muss die Pyrokinese-Ausnahme nennen');
assert.match(psi, /Der Stoß ist <1 Sekunde, daher \*\*0 SYS\*\*/,
  'der telekinetische Impuls muss unverändert 0 SYS belegen');

// Redaktionelle Zustandsrechnung, keine Kampfengine und kein Modell-Playtest.
const pyroActivation = ({ pp, freeSys, ppCost, sysLoad }) => ({
  possible: pp >= ppCost && freeSys >= sysLoad,
  duringActivation: pp >= ppCost && freeSys >= sysLoad ? sysLoad : 0,
  afterActivation: 0,
});
assert.deepStrictEqual(pyroActivation({ pp: 2, freeSys: 1, ppCost: 2, sysLoad: 1 }),
  { possible: true, duringActivation: 1, afterActivation: 0 });
assert.strictEqual(pyroActivation({ pp: 2, freeSys: 0, ppCost: 2, sysLoad: 1 }).possible, false,
  'Medium bleibt bei 0 freien SYS gesperrt, obwohl der Impuls unter 1 Sekunde dauert');
assert.strictEqual(pyroActivation({ pp: 3, freeSys: 1, ppCost: 3, sysLoad: 2 }).possible, false,
  'High bleibt bei nur 1 freier SYS gesperrt');

function expectedFiles(flat) {
  const expected = new Map();
  slotSources.forEach((source, i) => expected.set(flat
    ? `knowledge/${String(i + 1).padStart(2, '0')}-${path.basename(source)}`
    : `knowledge/${source}`, source));
  expected.set('system/SYSTEM_PROMPT_ONLY.md', setup.masterprompt);
  expected.set('system/PROJECT_BOOTSTRAP_INSTRUCTIONS.md', setup.project_bootstrap_instructions);
  expected.set('system/CREATOR_BOOTSTRAP_INSTRUCTIONS.md', setup.creator_bootstrap_instructions);
  expected.set('SETUP-ANLEITUNG.md', null); // von run_export() erzeugt
  expected.set('LICENSE', 'LICENSE');
  return expected;
}

function verifyZip(zip, expectedRoot = root, requireConfirmed = false) {
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
  assert.strictEqual(manifest.project_version, setup.version);
  assert.strictEqual(manifest.knowledge_slots, 19);
  const flat = manifest.files.some((f) => /^knowledge\/01-/.test(f.path));
  const expected = expectedFiles(flat);
  const actual = new Map(manifest.files.map((f) => [f.path, f]));
  assert.strictEqual(actual.size, manifest.files.length, 'Manifestpfade müssen eindeutig sein');
  assert.deepStrictEqual([...actual.keys()].sort(), [...expected.keys()].sort(),
    'Manifest entspricht nicht der unabhängigen Soll-Liste');
  for (const [target, source] of expected) {
    const item = actual.get(target);
    if (source === null) assert.strictEqual(item.source, null, `${target}: generierte Anleitung ohne Quellkopie`);
    else assert.strictEqual(item.source, source, `${target}: falsche oder fehlende Quellzuordnung`);
  }
  assert.deepStrictEqual(names.slice().sort(), ['BUILD-MANIFEST.json', ...manifest.files.map((f) => f.path)]
    .map((name) => prefix + name).sort(), 'Manifest-Dateiliste stimmt nicht mit ZIP überein');
  assert(names.includes(prefix + 'LICENSE'), 'Lizenzhinweis fehlt');
  assert(!names.some((n) => /(^|\/)(\.env|runtime\.js|internal|docs|AGENTS\.md)(\/|$)/.test(n)));
  assert(['confirmed-git', 'unconfirmed'].includes(manifest.source_provenance));
  assert.strictEqual(manifest.source_confirmed, manifest.source_provenance === 'confirmed-git');
  if (manifest.source_provenance === 'confirmed-git') {
    assert.strictEqual(typeof manifest.source_dirty, 'boolean');
    assert.match(manifest.source_commit, /^[0-9a-f]{40}$/);
    if (expectedRoot && fs.existsSync(path.join(expectedRoot, '.git'))) {
      assert.strictEqual(manifest.source_commit, execFileSync('git', ['rev-parse', 'HEAD'], { cwd: expectedRoot, encoding: 'utf8' }).trim());
    }
  } else {
    assert.strictEqual(manifest.source_commit, null);
    assert.strictEqual(manifest.source_dirty, null);
  }
  if (requireConfirmed) {
    assert.strictEqual(manifest.source_provenance, 'confirmed-git', 'strenger Build braucht bestätigte Herkunft');
    assert.strictEqual(manifest.source_dirty, false, 'strenger Build muss sauber sein');
  }
  return manifest;
}

// Im Workflow wird genau das hochzuladende Artefakt geprüft, nicht ein zweiter Export.
if (process.env.PACK_ZIP) {
  verifyZip(path.resolve(process.env.PACK_ZIP), root, true);
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
    const manifest = verifyZip(`${pack}.zip`, root);
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
  verifyZip(`${noGitPack}.zip`, sourceZip);

  const goodZip = `${path.join(tmp, dirs[0])}.zip`;
  const mutateZip = (name, script) => {
    const output = path.join(tmp, `${name}.zip`);
    execFileSync('python3', ['-c', [
      'import io,json,sys,zipfile',
      'src,dst,mode=sys.argv[1:]',
      'with zipfile.ZipFile(src) as zin:',
      ' files={n:zin.read(n) for n in zin.namelist() if not n.endswith("/")}',
      'prefix=next(iter(files)).split("/")[0]+"/"',
      'manifest=json.loads(files[prefix+"BUILD-MANIFEST.json"])',
      script,
      'files[prefix+"BUILD-MANIFEST.json"]=(json.dumps(manifest)+"\\n").encode()',
      'with zipfile.ZipFile(dst,"w",zipfile.ZIP_DEFLATED) as zout:',
      ' for n,data in files.items(): zout.writestr(n,data)',
    ].join('\n'), goodZip, output, name]);
    assert.throws(() => verifyZip(output, root), `${name} muss durch dieselbe verifyZip-Funktion scheitern`);
  };
  mutateZip('missing-masterprompt', 'item=next(x for x in manifest["files"] if x["path"]=="system/SYSTEM_PROMPT_ONLY.md")\nmanifest["files"].remove(item)\ndel files[prefix+item["path"]]');
  mutateZip('replaced-slot', 'item=next(x for x in manifest["files"] if x["path"].startswith("knowledge/"))\ndata=files.pop(prefix+item["path"])\nitem["path"]="knowledge/ersatz.md"\nfiles[prefix+item["path"]]=data');
  mutateZip('missing-source', 'next(x for x in manifest["files"] if x["path"]=="LICENSE").pop("source",None)');
  mutateZip('damaged-content', 'item=next(x for x in manifest["files"] if x["path"].startswith("knowledge/"))\nfiles[prefix+item["path"]]+=b"\\nBESCHAEDIGT"');

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
