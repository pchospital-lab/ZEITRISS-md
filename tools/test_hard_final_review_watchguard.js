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
const macroOverview = saveText.split('## Makros im Überblick')[1].split('\n### ')[0];
const launchRiftShortRef = macroOverview.split('`launch_rift(id)`')[1].split('`resolve_rifts(ids)`')[0];
assert.ok(/eigene offene Leader-Rift[\s\S]{0,120}freien HQ/i.test(launchRiftShortRef),
  'launch_rift-Kurzverweis muss eigenen offenen Leader-Rift und freies HQ nennen.');
assert.ok(!/continuity\.split|family_id/i.test(launchRiftShortRef),
  'launch_rift-Kurzverweis darf keinen Split-Family-Zwang setzen.');
assert.ok(/historische[\s\S]{0,100}continuity\.split\.family_id/i.test(saveText),
  'Historische Split-Importfelder müssen weiterhin zulässig bleiben.');
assert.ok(/rift_payoff[\s\S]{0,180}debrief_id/i.test(saveText), 'Persistenter Payoff-Beleg fehlt.');
assert.ok(/payoff_id[\s\S]{0,220}Leader-ID[\s\S]{0,220}Abschluss-\/Trace-ID/i.test(saveText),
  'Stabile, einsatzgebundene Payoff-Identität fehlt.');
assert.ok(/px=0[\s\S]{0,40}px_state=consumed/i.test(saveText), 'Payoff-Lebenszyklus driftet.');
assert.ok(/Projektionsreihenfolge[\s\S]{0,500}Rift-Zuweisungen[\s\S]{0,300}Px-Reset/i.test(saveText),
  'Persönliche Projektionsreihenfolge ist nicht geladen erklärt.');
assert.ok(!/HQ-Merge\/Group-Import ein Cap von 12/i.test(saveText), 'Alte Merge-Deckelung ist wieder aktiv.');

const { text: masterText } = readMarkdown(
  'meta/masterprompt_v6.md',
  [/Legacy-Split-\/Konvergenzdaten/i, /Legacy-Px-Konfliktimport/i],
  'Hard-Final-Review-Watchguard (Masterprompt)'
);
const masterImportRules = masterText
  .split('- **NPC-Kontinuität (Kurzregel):**')[1]
  .split('- Arena ist immer vorhanden:')[0];
assert.ok(
  /ausschließlich beim historischen Import[\s\S]{0,220}gewöhnlicher Gruppenwechsel[\s\S]{0,100}ohne Split-Protokoll/i
    .test(masterImportRules),
  'Masterprompt-Schemaabschnitt muss Split-/Konvergenzdaten auf Legacy-Import begrenzen.'
);
assert.ok(
  !/Core-Split-Kanon|Mixed-Split ohne Branch-Protokoll|Konvergenz entsteht/i.test(masterImportRules),
  'Masterprompt-Schemaabschnitt enthält wieder aktive Split-/Konvergenzregeln.'
);
const masterBriefingRules = masterText
  .split('- **Gruppen- und Split-Verhalten (Multiplayer/MMO):**')[1]
  .split('- **Verb-SSOT und Pflicht-Output-Format gelten unverändert**')[0];
assert.ok(
  /Historische Core-Split-Daten[\s\S]{0,350}weder neue Thread-Briefings noch erneute Zielabrechnungen/i
    .test(masterBriefingRules),
  'Masterprompt-Briefingabschnitt muss alte Core-Splits rein historisch behandeln.'
);
assert.ok(
  !/Core-Splits mit `continuity\.split\.family_id`|Konvergenz .* löst den Merge/i.test(masterBriefingRules),
  'Masterprompt-Briefingabschnitt enthält wieder ein aktives Split-Family-Protokoll.'
);
const pxConflictRules = masterText
  .split('- **Legacy-Px-Konfliktimport:**')[1]
  .split('- Keine Laufzeit-Daten')[0];
assert.ok(
  /keine Pool-Zusammenführung verschiedener Spieler[\s\S]{0,180}Gast-Px[\s\S]{0,180}späteren regulären Fortschritt nicht zurück/i
    .test(pxConflictRules),
  'Legacy-Px-Präzedenz muss persönliche Pools und späteren Fortschritt schützen.'
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
assert.ok(/Ein Episodenabschluss ist nicht nötig/i.test(campaignText), 'Rift-Start hängt wieder am Episodenende.');
const campaignRiftIntro = campaignText
  .split('### Cinematic Arc')[1]
  .split('#### Grundablauf')[0];
assert.ok(
  /Px-5-Payoff erzeugt Rift-Koordinaten/i.test(campaignRiftIntro)
    && /zugehörigen Debrief[\s\S]{0,180}nächsten[\s\S]{0,80}freien HQ-Chat/i.test(campaignRiftIntro)
    && /auch innerhalb der laufenden Core-Episode/i.test(campaignRiftIntro),
  'Kampagnen-Kurzstelle muss die persönliche Rift-Freigabe ab dem nächsten freien HQ-Chat nennen.'
);
assert.ok(
  !/Rifts spawnen separat zwischen den Episoden|beeinflussen die folgende Episode/i.test(campaignRiftIntro),
  'Kampagnen-Kurzstelle enthält wieder die alte Episodenfreigabe.'
);
assert.ok(/Neuerwerbslimit/i.test(campaignText) && /Altbestand/i.test(campaignText), 'Persönliche Kapazitätsregel fehlt.');
assert.ok(/Multi-Zeit-Sicht-Split[\s\S]{0,300}selben Chat/i.test(campaignText), 'Multi-Zeit-Sicht verlangt wieder getrennte Chats.');
assert.ok(
  !/Weiterentwicklung eines gemeinsamen Hauptquartiers/i.test(campaignText),
  'HQ-Kanon-Drift: kampagnenstruktur.md enthält wieder die Formulierung "Weiterentwicklung eines gemeinsamen Hauptquartiers".'
);
assert.ok(
  /feste[nr]? HQ-Kernbereich/i.test(campaignText),
  'HQ-Kanon driftet: der feste HQ-Kernbereich ist nicht mehr klar verankert.'
);

console.log('hard-final-review-watchguard-ok');
