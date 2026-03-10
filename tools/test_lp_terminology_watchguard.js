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

function listTrackedFiles() {
  return execSync('git ls-files', { cwd: ROOT, encoding: 'utf8' })
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
}

function isTargetFile(relPath) {
  if (EXCLUDE_FILES.has(relPath)) return false;
  if (EXCLUDE_PREFIXES.some((prefix) => relPath.startsWith(prefix))) return false;
  return TARGET_PREFIXES.some((prefix) => relPath.startsWith(prefix) || relPath === prefix);
}

const linePattern = /\bHP\b|Hitpoints/;
const filePattern = /\bHP\b|Hitpoints/g;
const violations = [];

for (const relPath of listTrackedFiles().filter(isTargetFile)) {
  const text = readText(relPath);
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
