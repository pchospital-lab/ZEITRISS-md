const path = require('path');
const assert = require('assert');
const fs = require('fs');
const { resolveUniqueMarkdownTarget } = require('./watchguard_file_resolver');

const ROOT = path.join(__dirname, '..');

function readText(relPath){
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

function readJson(relPath){
  return JSON.parse(readText(relPath));
}

function resolveMarkdownTarget(relPath, anchors, label) {
  return resolveUniqueMarkdownTarget({
    root: ROOT,
    preferredRelPaths: [relPath],
    candidatePathRegex: new RegExp(`${path.basename(relPath).replace('.', '\\.')}$`, 'i'),
    contentPredicates: anchors,
    label
  });
}

const atlas = [
  'Quarzatrium',
  'Kodex-Archiv',
  'Med-Lab',
  'Operations-Deck',
  'Quartiere',
  'Hangar-Axis',
  'Zero Time Lounge',
  'Pre-City-Hub'
];

const ssotAtlasDocs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md',
  'gameplay/kampagnenstruktur.md',
  'gameplay/kampagnenuebersicht.md'
];

for (const relPath of ssotAtlasDocs) {
  const { text, file } = resolveMarkdownTarget(relPath, ['Quarzatrium', 'Pre-City-Hub'].map((x) => new RegExp(x, 'i')), `ITI-Hardcanon-Watchguard (Atlas: ${relPath})`);
  const resolvedRelPath = path.relative(ROOT, file);
  for (const token of atlas) {
    assert.ok(text.includes(token), `${resolvedRelPath}: ITI-Atlasanker '${token}' fehlt.`);
  }
}

const requiredPersonnel = ['Renier', 'Mira', 'Lorian', 'Vargas', 'Narella'];
const personnelDocs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md',
  'characters/charaktererschaffung-grundlagen.md'
];

for (const relPath of personnelDocs) {
  const { text, file } = resolveMarkdownTarget(relPath, [/Renier/i, /Mira/i], `ITI-Hardcanon-Watchguard (Personal: ${relPath})`);
  const resolvedRelPath = path.relative(ROOT, file);
  for (const token of requiredPersonnel) {
    assert.ok(text.includes(token), `${resolvedRelPath}: Kernpersonal-Anker '${token}' fehlt.`);
  }
}

const index = readJson('master-index.json');
const slotPaths = [...new Set(index.modules.filter((m) => m.slot).map((m) => m.path.split('#')[0]))];

const forbiddenRegexes = [
  { regex: /Institut für Temporale Interventionen/gi, label: 'ITI-Name im Plural' },
  { regex: /HQ-Ausbau/gi, label: 'HQ-Ausbau-Begriff' },
  { regex: /HQ-Ausbaustufen/gi, label: 'HQ-Ausbaustufen-Begriff' },
  { regex: /Direkt weiterspringen \(ohne HQ-Stop\)/gi, label: 'HQ-Skip-Option' }
];

for (const relPath of slotPaths) {
  const text = readText(relPath);
  for (const rule of forbiddenRegexes) {
    assert.ok(!rule.regex.test(text), `${relPath}: verbotener Driftbegriff '${rule.label}' gefunden.`);
  }
}

const aliasTerms = ['Gatehall', 'Research-Wing', 'Mission-Briefing-Pod'];
const aliasAllowlist = new Set([
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'gameplay/kampagnenstruktur.md'
]);

for (const relPath of slotPaths) {
  const text = readText(relPath);
  if (aliasAllowlist.has(relPath)) continue;
  for (const alias of aliasTerms) {
    assert.ok(!text.includes(alias), `${relPath}: Legacy-Alias '${alias}' außerhalb der Alias-Bridge gefunden.`);
  }
}

console.log('iti-hardcanon-watchguard-ok');
