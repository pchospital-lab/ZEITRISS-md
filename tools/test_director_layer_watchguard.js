const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Director-Layer-Watchguard'
});

const fullDirectorLayerDocs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md'
];

const worldstatusDocs = [
  ...fullDirectorLayerDocs,
  'gameplay/kampagnenstruktur.md'
];

for (const relPath of fullDirectorLayerDocs) {
  const { text, file } = readMarkdown(
    relPath,
    [/Briefing/i, /Relevanzsatz/i, /ITI-Bulletin/i, /Weltstatus|arc\.(?:factions|questions|hooks)/i],
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


  assert.ok(
    ((/pro[\s\S]{0,120}missionszyklus/i.test(text) &&
      /genau[\s\S]{0,120}ein(?:e)?[\s\S]{0,120}weltstatus/i.test(text)) ||
      (/weltstatus[\s\S]{0,120}pro[\s\S]{0,60}missionszyklus/i.test(text) &&
        /genau[\s\S]{0,120}ein(?:e)?/i.test(text))) &&
      /arc\.(?:factions|questions|hooks)/i.test(text) &&
      /folge(?:wirkung)?/i.test(text),
    `Regie-Layer-Drift in ${resolvedRelPath}: Pflichtanker 'genau eine Weltstatus-Zeile aus arc.factions/questions/hooks pro Missionszyklus' fehlt.`
  );
}

for (const relPath of worldstatusDocs) {
  const { text, file } = readMarkdown(
    relPath,
    [/Weltstatus|arc\.(?:factions|questions|hooks)/i],
    `Director-Layer-Watchguard (Worldstatus ${relPath})`
  );

  const resolvedRelPath = path.relative(ROOT, file);

  assert.ok(
    ((/pro[\s\S]{0,120}missionszyklus/i.test(text) &&
      /genau[\s\S]{0,120}ein(?:e)?[\s\S]{0,120}weltstatus/i.test(text)) ||
      (/weltstatus[\s\S]{0,120}pro[\s\S]{0,60}missionszyklus/i.test(text) &&
        /genau[\s\S]{0,120}ein(?:e)?/i.test(text))) &&
      /arc\.(?:factions|questions|hooks)/i.test(text) &&
      /folge(?:wirkung)?/i.test(text),
    `Weltstatus-Drift in ${resolvedRelPath}: Pflichtanker 'genau eine Weltstatus-Zeile aus arc.factions/questions/hooks pro Missionszyklus mit Folgewirkung' fehlt.`
  );
}

console.log('director-layer-watchguard-ok');
