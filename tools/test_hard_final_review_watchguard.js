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
  [/Persönlicher Gruppenwechsel-Standard/i, /keine Teilgruppen-Saves/i],
  'Hard-Final-Review-Watchguard (Save)'
);
assert.ok(
  /Jede Figur erhält ihren vollständigen persönlichen v7-Save/i.test(saveText),
  'Persönliche Saves beim Gruppenwechsel fehlen.'
);
assert.ok(
  /Taktische Teilgruppen[\s\S]{0,220}selben Chat[\s\S]{0,220}keine Teilgruppen-Saves/i.test(saveText),
  'Cross-Chat-Teilmissionssplit muss ausgeschlossen bleiben.'
);
assert.ok(!/Seeds: Union/i.test(saveText), 'Rift-Pool-Union darf nicht wieder aktiv werden.');

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
