const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.join(__dirname, '..');

function readText(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

const mustHaveRegex = [
  /0\s*-?LP/i,
  /Loot\s+sichern\s*→\s*optional(?:er)?\s+Kausalabfang\s*→\s*Cleanup\/Exfil/i,
  /kein\s+Kampf(?:-?Gadget|werkzeug|zug)|nicht\s+als\s+Kampf(?:-?Gadget|werkzeug|zug)|nie\s+als\s+Kampf(?:aktion|zug)?/i,
  /Nahdistanz|Nahbereich/i,
  /Identitätsfassung|Identitätslock/i,
  /Kodex\s*-?Uplink|Uplink/i,
  /Sekunden\s+bis\s+wenige\s+Minuten|wenige\s+Minuten/i,
  /Chrononauten/i,
  /Squadmates/i,
  /Boss[^\n]{0,20}Mini-?Boss/i,
  /Zivilisten/i,
  /Para\s*-?Wesen/i,
  /Arena\s*\/\s*PvP/i,
  /Chronopolis/i
];

const hardeningRegex = [
  /Named-Target-Echo|maximal\s+einen\s+Nachhall/i,
  /Kodex:\s*Identitätslock\s+bestätigt/i,
  /Kodex:\s*Kausalabfang\s+freigegeben/i,
  /Kodex:\s*Lokale\s+Erinnerung\s+driftet\.\s*Archivanker\s+aktiv/i,
  /Unbenannte\s+Hostiles[\s\S]{0,220}automatisch[\s\S]{0,220}benannten[\s\S]{0,220}nachfragen/i
];

const checks = [
  'core/spieler-handbuch.md',
  'core/sl-referenz.md',
  'systems/toolkit-gpt-spielleiter.md',
  'meta/masterprompt_v6.md',
  'characters/ausruestung-cyberware.md'
];

for (const relPath of checks) {
  const text = readText(relPath);
  assert.ok(/Kausalabfang|Never happened/i.test(text), `${relPath}: Kausalabfang/Never-happened-Anker fehlt.`);

  for (const rx of mustHaveRegex) {
    assert.ok(rx.test(text), `${relPath}: Pflichtanker fehlt (${rx}).`);
  }

  assert.ok(!/universell(?:es|er)?\s+Retcon/i.test(text), `${relPath}: driftiges Retcon-Wording gefunden.`);
}

const infraChecks = [
  'core/sl-referenz.md',
  'characters/ausruestung-cyberware.md'
];

for (const relPath of infraChecks) {
  const text = readText(relPath);
  assert.ok(/nicht\s+shopbar|kein\s+Kaufgegenstand/i.test(text), `${relPath}: Shop-Sperre für Marker fehlt.`);
  assert.ok(/nicht\s+als\s+Pflicht-Inventar|kein\s+Inventar-Ballast|nicht\s+als\s+eigenes\s+Inventarstück/i.test(text), `${relPath}: Inventar-Guard für Marker fehlt.`);
}

const strictChecks = [
  'systems/toolkit-gpt-spielleiter.md',
  'meta/masterprompt_v6.md'
];

for (const relPath of strictChecks) {
  const text = readText(relPath);
  for (const rx of hardeningRegex) {
    assert.ok(rx.test(text), `${relPath}: Echo-/Kodex-Hardening fehlt (${rx}).`);
  }
}

console.log('kausalabfang-watchguard-ok');
