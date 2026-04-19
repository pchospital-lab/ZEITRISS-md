const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');

const { readText, getDocText } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Onboarding-Start-Save-Watchguard'
});

const startDocs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md',
  'core/spieler-handbuch.md'
];

function assertPerDocRule(docList, rule) {
  for (const relPath of docList) {
    const text = getDocText(relPath);
    assert.ok(
      rule.regex.test(text),
      `Drift in ${relPath}: Pflichtanker '${rule.label}' fehlt.`
    );
  }
}

const startContractRules = [
  {
    label: 'natürliche-sprache-anker',
    regex: /natürliche(?:r|n)?\s+sprache/i,
    minHits: 4
  },
  {
    label: 'klassisch-als-standard',
    regex: /klassisch[^\n]{0,140}(?:als\s+standard|standardpfad)/i,
    minHits: 3
  },
  {
    label: 'generate-custom-manuell',
    regex: /generate[^\n]*custom\s+generate[^\n]*(?:manuell|selbst\s+bauen)/i,
    minHits: 3
  }
];

for (const rule of startContractRules) {
  let hits = 0;
  for (const relPath of startDocs) {
    const text = getDocText(relPath);
    if (rule.regex.test(text)) hits += 1;
  }
  assert.ok(
    hits >= rule.minHits,
    `Startvertrag-Drift: Regel '${rule.label}' nur in ${hits}/${startDocs.length} Dokumenten gefunden (mind. ${rule.minHits}).`
  );
}

const startPerDocRules = [
  {
    label: 'natürliche-sprache-pro-ssot-datei',
    regex: /natürliche(?:r|n)?\s+sprache/i
  },
  {
    label: 'klassisch-standard-pro-ssot-datei',
    regex: /klassisch[^\n]{0,200}(?:als\s+standard|standardpfad|standard)/i
  },
  {
    label: 'generate-custom-manuell-pro-ssot-datei',
    regex: /generate[\s\S]{0,300}custom\s+generate[\s\S]{0,300}(?:manuell|manuellem\s+bau|manuellen\s+bau|selbst\s+bauen)/i
  }
];

for (const rule of startPerDocRules) {
  assertPerDocRule(startDocs, rule);
}

const hqDocs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md',
  'systems/gameflow/speicher-fortsetzung.md'
];

let saveHintHits = 0;
let noAutoBriefingHits = 0;
let newChatHintHits = 0;

for (const relPath of hqDocs) {
  const text = getDocText(relPath);
  if (/deepsave\s+möglich/i.test(text)) saveHintHits += 1;
  if (/(?:kein\s+automatisches?[^\n.]*briefing|kein\s+auto-weiterleitungsdruck[^\n.]*briefing|nicht\s+automatisch[^\n.]*briefing)/i.test(text)) {
    noAutoBriefingHits += 1;
  }
  if (/(?:neuen\s+chat[^\n.]*empfohlen|neuer\s+chat[^\n.]*empfohlen)/i.test(text)) {
    newChatHintHits += 1;
  }
}

assert.ok(saveHintHits >= 2, `HQ-Save-Hinweisdrift: 'Deepsave möglich' nur ${saveHintHits}/4 Treffer.`);
assert.ok(noAutoBriefingHits >= 2, `HQ-Flow-Drift: 'kein Auto-Briefing' nur ${noAutoBriefingHits}/4 Treffer.`);
assert.ok(newChatHintHits >= 2, `Chatwechsel-Hinweisdrift: 'neuer Chat empfohlen' nur ${newChatHintHits}/4 Treffer.`);

const hqPerDocRuleMatrix = [
  {
    label: 'hq-deepsave-anker',
    regex: /deepsave\s+möglich/i,
    docs: [
      'systems/toolkit-gpt-spielleiter.md',
      'core/sl-referenz.md',
      'systems/gameflow/speicher-fortsetzung.md'
    ]
  },
  {
    label: 'hq-kein-auto-briefing-anker',
    regex: /(?:kein\s+automatisches?[\s\S]{0,140}briefing|kein\s+auto-weiterleitungsdruck[\s\S]{0,140}briefing|nicht\s+automatisch[\s\S]{0,140}briefing|kein[\s\S]{0,140}automatischer[\s\S]{0,140}sprung[\s\S]{0,140}briefing)/i,
    docs: [
      'systems/toolkit-gpt-spielleiter.md',
      'core/sl-referenz.md',
      'systems/gameflow/speicher-fortsetzung.md'
    ]
  },
  {
    label: 'hq-neuer-chat-empfohlen-anker',
    regex: /(?:neuen\s+chat[^\n.]*empfohlen|neuer\s+chat[^\n.]*empfohlen)/i,
    docs: hqDocs
  }
];

for (const rule of hqPerDocRuleMatrix) {
  assertPerDocRule(rule.docs, rule);
}

// ---------------------------------------------------------------------------
// Chargen-Save-Gate-Watchguard
//
// Der Chargen-Save-Gate-Abschnitt muss im klassischen Onboarding-Pfad
// ausdrücklich verankert sein. Entdeckt via automatisiertem Noob-Playtest
// (Sarah-Persona, Lvl 1), in dem die SL nach Chargen ohne Save-Angebot ins
// Briefing gesprungen ist.
//
// Siehe: docs/qa/playtest-befund-chargen-save-gate.md (merged 2026-04-19)
// ---------------------------------------------------------------------------

const chargenGateDocs = [
  'meta/masterprompt_v6.md',
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md',
  'systems/gameflow/speicher-fortsetzung.md',
  'core/spieler-handbuch.md'
];

const chargenGatePerDocRules = [
  {
    label: 'chargen-save-gate-anker',
    regex: /chargen-save-gate/i
  },
  {
    label: 'fast-lane-ausnahme-anker',
    regex: /fast-lane[\s\S]{0,320}(?:direkt\s+(?:in(?:s|\s+den)?)\s+briefing(?:raum)?|kein(?:e|en)?\s+(?:pause|chargen-save-gate)|keine\s+HQ-Heimkehr)/i
  }
];

for (const rule of chargenGatePerDocRules) {
  assertPerDocRule(chargenGateDocs, rule);
}

// Trigger-Liste "Savebare HQ-Zustände" muss in mindestens zwei Kern-SSOT-Dateien
// konsistent auftauchen (Masterprompt ist optional; er verweist auf Toolkit/SL-Ref).
const triggerListDocs = [
  'systems/toolkit-gpt-spielleiter.md',
  'core/sl-referenz.md',
  'systems/gameflow/speicher-fortsetzung.md'
];

let triggerListHits = 0;
for (const relPath of triggerListDocs) {
  const text = getDocText(relPath);
  if (/savebare\s+hq-zustände/i.test(text) || /deepsave-trigger-liste/i.test(text)) {
    triggerListHits += 1;
  }
}
assert.ok(
  triggerListHits >= 2,
  `Trigger-Liste-Drift: 'Savebare HQ-Zustände'/'Deepsave-Trigger-Liste' nur ${triggerListHits}/${triggerListDocs.length} Treffer.`
);

// Chargen-Ende muss in der Trigger-Liste als eigener Fall genannt sein.
let chargenEndHits = 0;
for (const relPath of triggerListDocs) {
  const text = getDocText(relPath);
  if (/chargen-ende/i.test(text)) chargenEndHits += 1;
}
assert.ok(
  chargenEndHits >= 2,
  `Chargen-Trigger-Drift: 'Chargen-Ende' nur ${chargenEndHits}/${triggerListDocs.length} Treffer in Trigger-Listen.`
);

const spielerHandbuchText = getDocText('core/spieler-handbuch.md');
assert.ok(
  /standard\s*\(empfohlen\)[\s\S]{0,220}spiel\s+starten\s*\(solo\s+klassisch\)/i.test(spielerHandbuchText),
  'Spielerhandbuch-Drift: Mini-Einsatzhandbuch muss `solo klassisch` als Standard (empfohlen) ausweisen.'
);
assert.ok(
  /fast-lane\s*\(optional\)[\s\S]{0,220}solo\s+schnell/i.test(spielerHandbuchText),
  'Spielerhandbuch-Drift: Mini-Einsatzhandbuch muss `solo schnell` als optionale Fast-Lane markieren.'
);
assert.ok(
  /kampagnenstart[\s\S]{0,120}standard[\s\S]{0,120}klassisch\s*\+\s*generate/i.test(spielerHandbuchText),
  'Spielerhandbuch-Drift: Start-Transkripte müssen einen klassischen Kampagnenstart als Standard hervorheben.'
);
assert.ok(
  /solo\s*-\s*schnelleinstieg\s*\(fast-lane,\s*optional\)/i.test(spielerHandbuchText),
  'Spielerhandbuch-Drift: Solo-Schnelleinstieg muss als optionale Fast-Lane gekennzeichnet bleiben.'
);

const charsOptionsText = getDocText('characters/charaktererschaffung-optionen.md');
assert.ok(
  /nicht[\s\S]{0,40}bevorzugte?r?\s+runtime-pfad/i.test(charsOptionsText),
  'Archetypen-Drift: chars-options muss Archetypen/Pregens explizit als nicht-bevorzugten Runtime-Pfad markieren.'
);
assert.ok(
  /generate[\s\S]{0,160}custom\s+generate[\s\S]{0,160}(?:manuell|manuellen\s+bau)/i.test(charsOptionsText),
  'Archetypen-Drift: chars-options muss den Kampagnen-Standard generate/custom generate/manuell hervorheben.'
);

const masterIndex = JSON.parse(readText('master-index.json'));
const charsOptionsModule = masterIndex.modules.find((m) => m.slug === 'chars-options');
assert.ok(charsOptionsModule, 'Archetypen-Drift: master-index enthält kein chars-options Modul.');
assert.ok(
  /(inspiration|fallback)/i.test(charsOptionsModule.title || ''),
  'Archetypen-Drift: master-index Titel für chars-options muss Inspirations-/Fallback-Charakter tragen.'
);
assert.strictEqual(
  charsOptionsModule.slot,
  false,
  'Archetypen-Drift: chars-options muss im master-index als optionaler Nicht-Default-Slot (slot:false) geführt werden.'
);

const entryLayerDocs = [
  'README.md',
  'docs/setup-guide.md',
  'scripts/setup-openwebui.sh'
];

const entryRules = [
  {
    label: 'entry-klassisch-default',
    regex: /spiel\s+starten\s*\(solo\s+klassisch\)/i,
    minHits: 3
  },
  {
    label: 'entry-fastlane-optional',
    regex: /solo\s+schnell[^\n]{0,120}(?:fast-lane|optional)/i,
    minHits: 2
  },
  {
    label: 'entry-natuerliche-sprache',
    regex: /natürliche(?:r|n)?\s+sprache|natürlich\w*\s+(?:sagen|formulier\w*|neu\s+starten)/i,
    minHits: 3
  }
];

for (const rule of entryRules) {
  let hits = 0;
  for (const relPath of entryLayerDocs) {
    const text = getDocText(relPath);
    if (rule.regex.test(text)) hits += 1;
  }
  assert.ok(
    hits >= rule.minHits,
    `Entry-Layer-Drift: Regel '${rule.label}' nur in ${hits}/${entryLayerDocs.length} Dokumenten gefunden (mind. ${rule.minHits}).`
  );
}

const readmeText = getDocText('README.md');
const setupGuideText = getDocText('docs/setup-guide.md');

assert.ok(
  /mmo\s+ohne\s+server/i.test(readmeText),
  'Entry-Layer-Drift: README muss das Produktversprechen "MMO ohne Server" sichtbar tragen.'
);
assert.ok(
  /save\s*=\s*charakter/i.test(readmeText),
  'Entry-Layer-Drift: README muss den Anker "Save = Charakter" sichtbar tragen.'
);
assert.ok(
  /müsst[^\n]{0,80}nicht[^\n]{0,80}regelwerk\s+lesen/i.test(readmeText),
  'Entry-Layer-Drift: README muss den Niedrigschwellen-Anker (Regelwerk nicht vorab lesen) enthalten.'
);
assert.ok(
  /19\s+slots\s+im\s+default|19\s+wissensmodule/i.test(readmeText),
  'Entry-Layer-Drift: README muss den Default-Ladepfad (19 Slots/Module) referenzieren.'
);
assert.ok(
  /19\s+default(?:-modulen|-wissensslots)|19\s+wissensmodule/i.test(setupGuideText),
  'Entry-Layer-Drift: Setup-Guide muss den 19-Module-Default klar benennen.'
);
assert.ok(
  /nicht\s+mehr\s+in\s+den\s+default-ladepfad|nicht\s+im\s+default-slotset/i.test(setupGuideText),
  'Entry-Layer-Drift: Setup-Guide muss chars-options als optionales Nicht-Default-Modul markieren.'
);

console.log('onboarding-start-save-watchguard-ok');
