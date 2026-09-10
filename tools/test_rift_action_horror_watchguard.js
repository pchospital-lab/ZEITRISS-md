const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Rift-Action-Horror-Watchguard'
});

function read(relPath, anchor) {
  return readMarkdown(relPath, [anchor], `Rift-Action-Horror (${relPath})`).text;
}

const missions = read('gameplay/kreative-generatoren-missionen.md', /Rift-Casefile Builder/);
assert.match(missions, /keine oder höchstens eine[\s\S]{0,160}Zeit-Signaturfähigkeit/i);
assert.match(missions, /temporale Analyse ist nicht verpflichtend/i);
assert.match(missions, /Stille auf Station Nadir/);
assert.match(missions, /Unter den Glocken von Rabensteg/);
assert.match(missions, /langen Schritte von Kestrel Hollow/);
assert.doesNotMatch(missions, /Identify Time Marker/);

const creatures = read('gameplay/kreative-generatoren-begegnungen.md', /Para-Creature-Generator/);
assert.match(creatures, /Boss, Brut\/Rudel,[\s\S]{0,180}keine zusätzlichen Anomalien/i);
assert.match(creatures, /Psi[\s\S]{0,100}nie ungefragt einzige Lösung/i);
assert.doesNotMatch(creatures, /Fähigkeitspalette um den Zeitmarker/);

const campaign = read('gameplay/kampagnenstruktur.md', /Rift-Op Interface Contract/);
assert.match(campaign, /Bio \+ Material[\s\S]{0,100}Temporal ist keine Builder-Pflicht/i);
assert.doesNotMatch(campaign, /Rift-Boss: voller Chrono-Suite/);

const master = read('meta/masterprompt_v6.md', /Rift-Horror-Pflichtgate/);
assert.match(master, /Zeitursache ≠ Zeit-Skill/);
assert.match(master, /keine aktive Zeitmanipulation oder höchstens einen/);

console.log('rift-action-horror-watchguard-ok');
