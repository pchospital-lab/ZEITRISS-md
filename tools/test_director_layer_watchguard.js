const path = require('path');
const assert = require('assert');
const { resolveUniqueMarkdownTarget } = require('./watchguard_file_resolver');

const ROOT = path.join(__dirname, '..');

function resolveDocTarget(preferredRelPath, anchorRegexes, label) {
  return resolveUniqueMarkdownTarget({
    root: ROOT,
    preferredRelPaths: [preferredRelPath],
    candidatePathRegex: new RegExp(`${path.basename(preferredRelPath).replace('.', '\\.')}$`, 'i'),
    contentPredicates: anchorRegexes,
    label
  });
}

const docs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md'
];

for (const relPath of docs) {
  const { text, file } = resolveDocTarget(
    relPath,
    [/Briefing/i, /Relevanzsatz/i, /ITI-Bulletin/i],
    `Director-Layer-Watchguard (${relPath})`
  );

  const resolvedRelPath = path.relative(ROOT, file);

  assert.ok(
    /vor[\s\S]{0,120}briefing/i.test(text) &&
      /genau[\s\S]{0,16}ein(?:en|e)?[\s\S]{0,120}relevanzsatz/i.test(text),
    `Regie-Layer-Drift in ${resolvedRelPath}: Pflichtanker 'genau ein Relevanzsatz vor Briefing' fehlt.`
  );

  assert.ok(
    /nach[\s\S]{0,140}(?:heimkehr|debrief)/i.test(text) &&
      /genau[\s\S]{0,16}ein(?:e)?[\s\S]{0,140}iti-bulletin/i.test(text),
    `Regie-Layer-Drift in ${resolvedRelPath}: Pflichtanker 'genau eine ITI-Bulletin-Mikronachricht nach Heimkehr' fehlt.`
  );
}

console.log('director-layer-watchguard-ok');
