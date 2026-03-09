const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.join(__dirname, '..');

function readText(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
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
  const text = readText(check.relPath);
  for (const rx of check.mustHave) {
    assert.ok(rx.test(text), `${check.relPath}: Pflichtanker fehlt (${rx}).`);
  }
  for (const rx of check.mustNotHave) {
    assert.ok(!rx.test(text), `${check.relPath}: Verbotenes Driftmuster gefunden (${rx}).`);
  }
}

console.log('physicality-watchguard-ok');
