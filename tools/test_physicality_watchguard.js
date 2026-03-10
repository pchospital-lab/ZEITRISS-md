const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Physicality-Watchguard'
});

function readText(relPath, anchorRegex) {
  const { file, text } = readMarkdown(
    relPath,
    anchorRegex ? [anchorRegex] : [/./s],
    `Physicality-Watchguard (${relPath})`
  );
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
