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

function section(text, start, end) {
  const from = text.search(start);
  assert.notStrictEqual(from, -1, `Abschnitt fehlt: ${start}`);
  const rest = text.slice(from);
  const to = end ? rest.slice(1).search(end) : -1;
  return to === -1 ? rest : rest.slice(0, to + 1);
}

const missions = read('gameplay/kreative-generatoren-missionen.md', /Rift-Seed Catalogue/);
const catalogue = section(missions, /^### Rift-Seed Catalogue/m, /^### Rift-Casefile Builder/m);
const butcher = section(catalogue, /RIFT-BUTCHER/, /RIFT-JDEV/);
const bridge = section(catalogue, /RIFT-BRIDGE/, /RIFT-ORCHID/);
const lunar = section(catalogue, /RIFT-LUNAR/, /```/);
const builder = section(missions, /^### Rift-Casefile Builder/m, /^### Drei Variationsmuster/m);
const kestrel = section(missions, /langen Schritte von Kestrel Hollow/, /Diese Muster/);

assert.match(catalogue, /TEMP-Probe gegen SG 12[\s\S]{0,220}has_psi=false/);
assert.match(catalogue, /SG 12 ist der Zielwert, kein\s+Attributsmindestwert/);
assert.match(catalogue, /Aktive Psi-Kräfte[\s\S]{0,180}has_psi[\s\S]{0,180}PP- und SYS-Kosten/);
assert.match(butcher, /TEMP-Wahrnehmung gegen SG 12[\s\S]{0,180}INT\/Tech gegen SG 11/);
assert.match(butcher, /Ermittlungsbilder|Überwachungsbilder|Überwachung/);
assert.doesNotMatch(butcher, /Psi-Scan|Psi-Impuls|Psi Mind 12/);
assert.match(bridge, /TEMP-Widerstandsprobe gegen SG 12 für alle Chrononauten[\s\S]{0,100}Misserfolg Stress \+1/);
assert.doesNotMatch(bridge, /Psi-Save/);
assert.match(lunar, /Druckschotts[\s\S]{0,160}Atemmembran/);
assert.doesNotMatch(lunar, /Psi-Signatur|Mind 13/);
assert.match(builder, /VISUAL HOOK[\s\S]{0,100}Fallanker \+ konkrete beobachtbare Spur/);
assert.match(builder, /VISUAL HOOK: <Fallanker \+ konkrete beobachtbare Spur>/);
assert.doesNotMatch(builder, /Anchor \+ Marker, der sofort im HUD auftaucht|VISUAL HOOK: <Anchor \+ Marker>/);
assert.match(kestrel, /einmal im gesamten Encounter[\s\S]{0,100}zweiten Bossphase/);
assert.doesNotMatch(kestrel, /einmal pro Phase/);

const encounters = read('gameplay/kreative-generatoren-begegnungen.md', /Kreaturen- & Gestalten-Generator/);
const creaturesIntro = section(encounters, /^## Kreaturen- & Gestalten-Generator/m, /^### Para-Schwereklassen/m);
const paraDoc = read('gameplay/kreative-generatoren-begegnungen.md', /Para-Creature-Generator: Rift Casefile Edition/);
const para = section(paraDoc, /^## Para-Creature-Generator: Rift Casefile Edition/m, /^# Rift Urban-Myth-Generator/m);
assert.match(creaturesIntro, /Zukunftsmissionen[\s\S]{0,160}ohne aktive Zeitfähigkeit/);
assert.doesNotMatch(creaturesIntro, /Zukunftsmissionen werfen[\s\S]{0,100}reine Zeitkonstrukte/);
assert.match(para, /Der Fallanker[\s\S]{0,600}entfernt nicht automatisch Gegner[\s\S]{0,100}überspringt keine\s+Bossphase/);
assert.doesNotMatch(para, /Wird der Anchor befreit\/zerstört, löst sich die Anomalie/);
assert.match(para, /TEMP und Psi trennen[\s\S]{0,260}has_psi=false/);
assert.doesNotMatch(para, /Psi Mind 12|Psi-Signatur Mind 13/);
assert.match(para, /Epoche\/Setting[\s\S]{0,100}Epochen-\/Setting-Rahmen/);
assert.doesNotMatch(para, /Epoche \(W6\)[\s\S]{0,50}identisch zur Rift-Edition/);

const campaign = read('gameplay/kampagnenstruktur.md', /Level-Hinweise & Rift-Tier-System/);
const tiers = section(campaign, /^#### Level-Hinweise & Rift-Tier-System/m, /^##### Tier-Übergangs-Regeln/m);
assert.match(tiers, /keine permanenten Pflichtmodifikatoren/);
assert.match(tiers, /gemeinsamen Fallkern-\/Effektbudgets/);
assert.doesNotMatch(tiers, /Zeitregen, Schwerkraft-Flimmern\) als permanente Szenen-Modifier/);
assert.doesNotMatch(tiers, /Bosse nutzen eingeschränkte Chrono-Tricks/);

const master = read('meta/masterprompt_v6.md', /Rift-Horror-Pflichtgate/);
assert.match(master, /Zeitursache ≠ Zeit-Skill/);
assert.match(master, /TEMP-Wahrnehmungs-\/Widerstandsproben[\s\S]{0,180}has_psi=false/);
assert.match(master, /Aktive Psi-Kräfte verlangen weiterhin[\s\S]{0,120}PP-\/SYS-Kosten/);

console.log('rift-action-horror-watchguard-ok');
