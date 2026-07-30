const fs = require('fs');
const os = require('os');
const path = require('path');
const assert = require('assert');
const { execFileSync } = require('child_process');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readText, getDocText } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Creator Export Watchguard'
});

const setup = JSON.parse(readText('setup.json'));
const index = JSON.parse(readText('master-index.json'));
const creatorSource = getDocText(setup.creator_bootstrap_instructions);
const playSource = getDocText(setup.project_bootstrap_instructions);
const masterSource = getDocText(setup.masterprompt);
const expectedKnowledgePaths = (index.modules || [])
  .filter((entry) => entry.slot === true)
  .map((entry) => String(entry.path || '').split('#')[0].replace(/\\/g, '/'))
  .filter(Boolean)
  .sort();
const expectedKnowledgeCount = expectedKnowledgePaths.length;
const setupPy = readText('scripts/setup.py');

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'zeitriss-creator-export-'));
const requestedDest = path.join(tempRoot, 'pack');
const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');

assert.ok(
  /cfg\.get\(["']creator_bootstrap_instructions["']\)/.test(setupPy),
  'Creator-Export: Creator-Key muss optional per cfg.get(...) gelesen werden.'
);
assert.ok(
  /has_creator_bootstrap:\s*bool\s*=\s*False/.test(setupPy),
  'Creator-Export: has_creator_bootstrap braucht Default False.'
);
assert.ok(
  /f["']3\. Die \{file_count\} Wissensmodule plus/.test(setupPy),
  'Creator-Export: Setup-Anleitung muss die dynamische Modulzahl verwenden.'
);

try {
  execFileSync(
    python,
    [path.join(ROOT, 'scripts', 'setup.py'), '--export', '-o', requestedDest],
    {
      cwd: ROOT,
      env: { ...process.env, NO_COLOR: '1' },
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe']
    }
  );

  const exportedFiles = walk(tempRoot);
  const setupGuides = exportedFiles.filter((file) => path.basename(file) === 'SETUP-ANLEITUNG.md');
  assert.strictEqual(setupGuides.length, 1, 'Creator-Export: genau eine SETUP-ANLEITUNG.md erwartet.');

  const packRoot = path.dirname(setupGuides[0]);
  const systemDir = path.join(packRoot, 'system');
  const knowledgeDir = path.join(packRoot, 'knowledge');
  const exportedMaster = path.join(systemDir, 'SYSTEM_PROMPT_ONLY.md');
  const exportedPlay = path.join(systemDir, 'PROJECT_BOOTSTRAP_INSTRUCTIONS.md');
  const exportedCreator = path.join(systemDir, 'CREATOR_BOOTSTRAP_INSTRUCTIONS.md');

  for (const file of [exportedMaster, exportedPlay, exportedCreator]) {
    assert.ok(
      fs.existsSync(file) && fs.statSync(file).isFile(),
      `Creator-Export: Datei fehlt: ${path.relative(packRoot, file)}`
    );
  }
  assert.ok(
    fs.existsSync(knowledgeDir) && fs.statSync(knowledgeDir).isDirectory(),
    'Creator-Export: knowledge/ fehlt.'
  );

  assert.strictEqual(fs.readFileSync(exportedMaster, 'utf8'), masterSource, 'Creator-Export: Masterprompt wurde verändert.');
  assert.strictEqual(fs.readFileSync(exportedPlay, 'utf8'), playSource, 'Creator-Export: Spiel-Bootstrap wurde verändert.');
  assert.strictEqual(fs.readFileSync(exportedCreator, 'utf8'), creatorSource, 'Creator-Export: Creator-Bootstrap wurde verändert.');

  const knowledgeFiles = walk(knowledgeDir).filter((file) => fs.statSync(file).isFile());
  const actualKnowledgePaths = knowledgeFiles
    .map((file) => path.relative(knowledgeDir, file).split(path.sep).join('/'))
    .sort();
  assert.deepStrictEqual(
    actualKnowledgePaths,
    expectedKnowledgePaths,
    'Creator-Export: exportierte Wissensmodule weichen von den slot:true-Pfaden ab.'
  );
  assert.strictEqual(
    knowledgeFiles.length,
    expectedKnowledgeCount,
    `Creator-Export: ${knowledgeFiles.length}/${expectedKnowledgeCount} Wissensmodule exportiert.`
  );

  const setupText = fs.readFileSync(setupGuides[0], 'utf8');
  assert.ok(/Creator Studio/i.test(setupText), 'Creator-Export: Creator-Studio-Weg fehlt in der Setup-Anleitung.');
  assert.ok(/CREATOR_BOOTSTRAP_INSTRUCTIONS\.md/i.test(setupText), 'Creator-Export: Creator-Dateiname fehlt in der Setup-Anleitung.');
  assert.ok(/PROJECT_BOOTSTRAP_INSTRUCTIONS\.md/i.test(setupText), 'Creator-Export: Spiel-Bootstrap fehlt in der Setup-Anleitung.');
  assert.ok(
    setupText.includes(`Die ${expectedKnowledgeCount} Wissensmodule plus`),
    'Creator-Export: dynamische Modulzahl fehlt im Creator-Setup.'
  );
  assert.ok(
    /Spiel- und Creator-Bootstrap niemals kombinieren;\s+das Creator Studio ist ein separates Projekt\./i.test(setupText),
    'Creator-Export: Modustrennung fehlt in der Setup-Anleitung.'
  );
} finally {
  fs.rmSync(tempRoot, { recursive: true, force: true });
}

assert.ok(!fs.existsSync(tempRoot), 'Creator-Export: temporäres Exportverzeichnis wurde nicht entfernt.');
console.log('creator-export-watchguard-ok');
