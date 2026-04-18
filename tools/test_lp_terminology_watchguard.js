const path = require('path');
const { execSync } = require('child_process');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.resolve(__dirname, '..');
const { readText } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'LpTerminologyWatchguard'
});

const TARGET_PREFIXES = [
  'gameplay/',
  'systems/',
  'docs/',
  'internal/runtime/',
  'internal/qa/playtest-',
  'meta/masterprompt_v6.md'
];

const EXCLUDE_PREFIXES = [
  'internal/qa/evidence/',
  'meta/archive/',
  'uploads/',
  'internal/qa/logs/',
  'internal/qa/plans/'
];

const EXCLUDE_FILES = new Set([
  'AGENTS.md',
  'CONTRIBUTING.md'
]);

// Nur Prosa-/Regeldateien prüfen. Binärdateien (PNG, JPG, PDF …) würden sonst
// zufällige Byte-Sequenzen als "HP"-Match liefern und den Watchguard rot färben.
const TEXT_EXTENSIONS = new Set([
  '.md',
  '.mdx',
  '.txt',
  '.json',
  '.yml',
  '.yaml',
  '.csv',
  '.tsv',
  '.html',
  '.htm'
]);

function listTrackedFiles() {
  return execSync('git ls-files', { cwd: ROOT, encoding: 'utf8' })
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
}

function hasTextExtension(relPath) {
  const dot = relPath.lastIndexOf('.');
  if (dot < 0) return false;
  return TEXT_EXTENSIONS.has(relPath.slice(dot).toLowerCase());
}

function isTargetFile(relPath) {
  if (EXCLUDE_FILES.has(relPath)) return false;
  if (EXCLUDE_PREFIXES.some((prefix) => relPath.startsWith(prefix))) return false;
  if (!hasTextExtension(relPath)) return false;
  return TARGET_PREFIXES.some((prefix) => relPath.startsWith(prefix) || relPath === prefix);
}

// Safety-Net: falls eine Textdatei doch Binärdaten enthält (z.B. embedded Base64
// ohne Zeilenumbrüche), überspringen wir sie. Ein Null-Byte ist ein guter Indikator.
function looksBinary(text) {
  return text.indexOf('\u0000') !== -1;
}

const linePattern = /\bHP\b|Hitpoints/;
const filePattern = /\bHP\b|Hitpoints/g;
const violations = [];

for (const relPath of listTrackedFiles().filter(isTargetFile)) {
  const text = readText(relPath);
  if (looksBinary(text)) continue;
  const matches = [...text.matchAll(filePattern)];
  if (matches.length === 0) continue;

  const lines = text.split(/\r?\n/);
  for (let idx = 0; idx < lines.length; idx += 1) {
    if (!linePattern.test(lines[idx])) continue;
    violations.push(`${relPath}:${idx + 1}:${lines[idx].trim()}`);
  }
}

if (violations.length > 0) {
  console.error('lp-terminology-watchguard-fail');
  for (const line of violations) {
    console.error(`- ${line}`);
  }
  process.exit(1);
}

console.log('lp-terminology-watchguard-ok');
