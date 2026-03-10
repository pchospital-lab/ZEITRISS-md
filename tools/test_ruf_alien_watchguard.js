const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Ruf/Alien-Watchguard'
});

function resolveText(preferredRelPath, contentPredicates) {
  const { file, text } = readMarkdown(
    preferredRelPath,
    contentPredicates && contentPredicates.length ? contentPredicates : [/./s],
    `Ruf/Alien-Watchguard (${preferredRelPath})`
  );
  return { relPath: path.relative(ROOT, file), text };
}

function expectIncludes(relPath, needle, message) {
  const { relPath: resolvedRelPath, text } = resolveText(relPath, [new RegExp(needle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i')]);
  assert.ok(text.includes(needle), `${resolvedRelPath}: ${message}`);
}

function expectNotMatch(relPath, pattern, message) {
  const { relPath: resolvedRelPath, text } = resolveText(relPath, []);
  assert.ok(!pattern.test(text), `${resolvedRelPath}: ${message}`);
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

expectIncludes(
  'core/spieler-handbuch.md',
  'Rang Feldagent · ITI-Ruf +2 · Lizenz Tier II',
  'Spieler-Handbuch soll das kanonische Debrief-Format mit ITI-Ruf führen.'
);

// Mystery-Kern regressionssicher halten: kein harter Alien-Fakt, aber klarer Reveal-Pfad.
expectIncludes(
  'core/zeitriss-core.md',
  'es gibt keine Aliens, nur',
  'Core-Modul soll den Reveal-Pfad "keine Aliens, nur Zukunft" explizit führen.'
);

expectIncludes(
  'gameplay/kreative-generatoren-begegnungen.md',
  'Greys - posthumane Fernzukunfts-Menschen',
  'Generator-Eintrag soll Greys als posthumane Fernzukunfts-Lesart führen.'
);

// Gating-Wording-Drift verhindern: kein Mischbegriff und kein Level-Tier-Header.

expectNotMatch(
  'gameplay/kampagnenuebersicht.md',
  /ITI-Rang\s*\/\s*ITI-Ruf/i,
  'Formale Freigaben sollen nicht als Mischbegriff "ITI-Rang/ITI-Ruf" auftauchen.'
);

expectNotMatch(
  'characters/charaktererschaffung-grundlagen.md',
  /Dienstgrad\s*\/\s*Ruf/i,
  'Formale Freigaben sollen nicht als Mischbegriff "Dienstgrad/Ruf" auftauchen.'
);

expectNotMatch(
  'characters/ausruestung-cyberware.md',
  /\*\*Tier\s*[1-5IVX]+\s*\(Lv[^\n]*\):/i,
  'Shop-Tier-Header dürfen nicht auf levelbasiertes Freigabe-Gating zurückfallen.'
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
