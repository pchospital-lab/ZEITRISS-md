const path = require('path');
const assert = require('assert');
const { resolveUniqueMarkdownTarget } = require('./watchguard_file_resolver');

const ROOT = path.join(__dirname, '..');

function readText(relPath, anchorRegex) {
  const { file, text } = resolveUniqueMarkdownTarget({
    root: ROOT,
    preferredRelPaths: [relPath],
    candidatePathRegex: new RegExp(`${relPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`, 'i'),
    contentPredicates: anchorRegex ? [anchorRegex] : [],
    label: 'Physicality-Watchguard'
  });
  return { relPath: path.relative(ROOT, file), text };
}

const checks = [
  {
    relPath: 'systems/toolkit-gpt-spielleiter.md',
    mustHave: [/Retina-HUD/i, /Handgelenk-Projektor/i, /Inworld-/i],
    mustNotHave: [
      /schwebende\s+holografische\s+Displays/i,
      /Hologramm-Begleiter/i,
      /nur\s+f[üu]r\s+diese\s+Mission/i
    ]
  },
  {
    relPath: 'systems/gameflow/cinematic-start.md',
    mustHave: [/linsengebundene\s+HUD-Lichtbilder/i, /Briefingfl[äa]chen/i],
    mustNotHave: [
      /Hologramm-Begleiter/i,
      /schwebende\s+holografische\s+Displays/i,
      /holografische\s+Anzeigen\s+erscheinen\s+in\s+deinem\s+Sichtfeld/i
    ]
  },
  {
    relPath: 'core/zeitriss-core.md',
    mustHave: [/Holosuite/i, /Retina-HUD/i, /Handgelenk-HUDs/i],
    mustNotHave: [
      /freischwebende\s+Hologramm-UI/i,
      /Handgelenk-Projektor-UI\s+als\s+Default/i
    ]
  }
];

for (const check of checks) {
  const { relPath, text } = readText(check.relPath, check.mustHave[0]);
  for (const rx of check.mustHave) {
    assert.ok(rx.test(text), `${relPath}: Pflichtanker fehlt (${rx}).`);
  }
  for (const rx of check.mustNotHave) {
    assert.ok(!rx.test(text), `${relPath}: Verbotenes Driftmuster gefunden (${rx}).`);
  }
}

console.log('physicality-watchguard-ok');
