const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TOOLS_DIR = path.join(ROOT, 'tools');

function listWatchguardTests() {
  return fs
    .readdirSync(TOOLS_DIR)
    .filter((file) => /^test_.*watchguard\.js$/.test(file))
    .filter((file) => file !== 'test_watchguard_loader_consistency.js')
    .sort();
}

function readFile(relPath) {
  return fs.readFileSync(path.join(TOOLS_DIR, relPath), 'utf8');
}

function hasDirectMarkdownReadFileSync(text) {
  return /readFileSync\s*\([\s\S]{0,220}\.md(?:["'`]|\s*[,)])/m.test(text);
}

function hasScopeLabelOnLoader(text) {
  return /createDocTextLoader\s*\(\s*\{[\s\S]{0,260}scopeLabel\s*:\s*['"`][^'"`]+['"`]/m.test(text);
}

const violations = [];

for (const file of listWatchguardTests()) {
  const text = readFile(file);

  if (/watchguard_file_resolver/.test(text)) {
    violations.push(`${file}: nutzt weiterhin watchguard_file_resolver direkt.`);
  }

  if (/resolveUniqueMarkdownTarget\s*\(/.test(text)) {
    violations.push(`${file}: ruft resolveUniqueMarkdownTarget(...) direkt auf.`);
  }

  if (/createDocTextLoader/.test(text) === false) {
    violations.push(`${file}: bindet createDocTextLoader nicht ein.`);
  }

  if (/readMarkdown\s*\(/.test(text) === false && /getDocText\s*\(/.test(text) === false) {
    violations.push(`${file}: nutzt weder readMarkdown(...) noch getDocText(...) aus dem zentralen Loader.`);
  }

  if (hasScopeLabelOnLoader(text) === false) {
    violations.push(`${file}: setzt keinen scopeLabel beim createDocTextLoader(...) (Pflicht für nachvollziehbare Fehlermeldungen).`);
  }

  if (hasDirectMarkdownReadFileSync(text)) {
    violations.push(`${file}: liest .md-Dateien direkt per readFileSync statt Loader.`);
  }
}

if (violations.length > 0) {
  console.error('watchguard-loader-consistency-fail');
  for (const line of violations) {
    console.error(`- ${line}`);
  }
  process.exit(1);
}

console.log('watchguard-loader-consistency-ok');
