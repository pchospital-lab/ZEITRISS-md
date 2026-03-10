const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Hard-Final-Review-Watchguard'
});

const { text: saveText } = readMarkdown(
  'systems/gameflow/speicher-fortsetzung.md',
  [/Split\/Merge ist kanonisch/i, /continuity\.split\.family_id/i],
  'Hard-Final-Review-Watchguard (Save)'
);
assert.ok(
  /Split\/Merge ist kanonisch[\s\S]{0,220}Core-Parallelpfade[\s\S]{0,220}separate Rift-Ops/i.test(saveText),
  'Split-/Merge-Kanon fehlt oder driftet: Core-Parallelpfade + separate Rift-Ops müssen explizit kanonisch sein.'
);
assert.ok(
  /Core-Parallelpfaden[\s\S]{0,120}continuity\.split\.family_id[\s\S]{0,120}Pflicht/i.test(saveText),
  'Split-/Merge-Kanon driftet: continuity.split.family_id muss bei Core-Parallelpfaden als Pflicht verankert sein.'
);
assert.ok(
  !/standardmäßig[\s\S]{0,80}nur[\s\S]{0,80}nach Episodenende[\s\S]{0,80}Rift-Ops[\s\S]{0,80}kanonisch/i.test(saveText),
  'Legacy-Drift: alter Rift-only-Standardsatz zum Split-/Merge-Kanon ist wieder aufgetaucht.'
);

const { text: cinematicText } = readMarkdown(
  'systems/gameflow/cinematic-start.md',
  [/Kanonischer Produkt-Startpfad/i],
  'Hard-Final-Review-Watchguard (Cinematic)'
);
assert.ok(
  !/Sobald die Fraktionswahl steht/i.test(cinematicText),
  'Einstiegskanon-Drift: cinematic-start.md enthält wieder den Altanker "Sobald die Fraktionswahl steht".'
);

const { text: campaignText } = readMarkdown(
  'gameplay/kampagnenstruktur.md',
  [/HQ-Kernbereich/i],
  'Hard-Final-Review-Watchguard (Campaign)'
);
assert.ok(
  !/Weiterentwicklung eines gemeinsamen Hauptquartiers/i.test(campaignText),
  'HQ-Kanon-Drift: kampagnenstruktur.md enthält wieder die Formulierung "Weiterentwicklung eines gemeinsamen Hauptquartiers".'
);
assert.ok(
  /feste[nr]? HQ-Kernbereich/i.test(campaignText),
  'HQ-Kanon driftet: der feste HQ-Kernbereich ist nicht mehr klar verankert.'
);

console.log('hard-final-review-watchguard-ok');
