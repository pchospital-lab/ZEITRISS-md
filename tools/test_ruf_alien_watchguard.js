const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.join(__dirname, '..');

function read(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

function expectIncludes(relPath, needle, message) {
  const text = read(relPath);
  assert.ok(text.includes(needle), `${relPath}: ${message}`);
}

function expectNotMatch(relPath, pattern, message) {
  const text = read(relPath);
  assert.ok(!pattern.test(text), `${relPath}: ${message}`);
}

// Debrief-/Ruf-Disziplin: zentraler Ablauf muss explizit ITI-Ruf führen.
expectIncludes(
  'meta/masterprompt_v6.md',
  'Bewertung → Loot-Recap → CU-Auszahlung → XP/Level-Up → ITI-Ruf-Update → Lizenz-Tier.',
  'Debrief-Flow muss ITI-Ruf-Update explizit enthalten.'
);

expectIncludes(
  'gameplay/kampagnenstruktur.md',
  'ITI-Ruf-Update',
  'Kampagnenablauf soll ITI-Ruf-Update explizit benennen.'
);

// Tier-V-Rückfall verhindern: kein globales Quest-only-Wording mehr.
expectNotMatch(
  'characters/ausruestung-cyberware.md',
  /Tier\s*V[^\n]{0,120}Questbelohnung/i,
  'Tier V darf nicht wieder als globale Questbelohnung formuliert werden.'
);

// Onboarding-Ton halten: frühe Spielertexte ohne harten Alien-Fakt.
expectNotMatch(
  'core/spieler-handbuch.md',
  /galaktische\s+F[öo]deration\s+fortgeschrittener\s+Alien-Spezies/i,
  'Frühes Onboarding darf keine bestätigte Alien-Föderation behaupten.'
);

expectNotMatch(
  'gameplay/kampagnenuebersicht.md',
  /Galaktische\s+F[öo]deration\s+mit\s+56\s+Spezies/i,
  'Kampagnenübersicht soll keine harte Föderationszahl als Fakt führen.'
);

console.log('ruf-alien-watchguard-ok');
