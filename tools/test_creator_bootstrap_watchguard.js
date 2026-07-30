const path = require('path');
const assert = require('assert');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const ROOT = path.join(__dirname, '..');
const { readText, getDocText } = createDocTextLoader({
  root: ROOT,
  scopeLabel: 'Creator Bootstrap Watchguard'
});

const setup = JSON.parse(readText('setup.json'));
const creatorPath = setup.creator_bootstrap_instructions;
const playPath = setup.project_bootstrap_instructions;

assert.strictEqual(
  creatorPath,
  'meta/creator_bootstrap_instructions.md',
  'setup.json muss den aktiven Creator-Bootstrap referenzieren.'
);
assert.strictEqual(
  playPath,
  'meta/project_bootstrap_instructions.md',
  'setup.json muss den Spiel-Bootstrap weiterhin separat referenzieren.'
);

const creator = getDocText(creatorPath);
const play = getDocText(playPath);
const setupPy = readText('scripts/setup.py');
const guide = getDocText('docs/creator-mode.md');
const setupGuide = getDocText('docs/setup-guide.md');
const readme = getDocText('README.md');
const importSchema = JSON.parse(readText('systems/gameflow/saveGame.v7.schema.json'));
const exportSchema = JSON.parse(readText('systems/gameflow/saveGame.v7.export.schema.json'));

const charCount = Array.from(creator).length;
const byteCount = Buffer.byteLength(creator, 'utf8');

assert.ok(
  charCount <= 8000,
  `Creator-Bootstrap überschreitet 8000 Unicode-Zeichen: ${charCount}.`
);
assert.ok(
  byteCount <= 8000,
  `Creator-Bootstrap überschreitet 8000 UTF-8-Bytes: ${byteCount}.`
);

const requiredAnchors = [
  ['creator-role', /ZEITRISS® Creator Studio/i],
  ['mode-boundary', /Im Creator-Modus wird \*\*nicht gespielt\*\*/i],
  ['play-redirect', /separates Projekt[\s\S]{0,100}PROJECT_BOOTSTRAP_INSTRUCTIONS\.md/i],
  ['source-save', /v7-Save-JSON\(s\)[\s\S]{0,100}Quellenkorpus/i],
  ['creator-board', /Creator Board[\s\S]{0,260}Hero Asset[\s\S]{0,260}Story Cut[\s\S]{0,260}Growth Asset/i],
  ['canon-ledger', /\*\*KANON\*\*[\s\S]{0,180}\*\*ADAPTIERT\*\*[\s\S]{0,180}\*\*KONZEPT\*\*/i],
  ['no-fake-quotes', /Keine „Originalzitate“ ohne Transkript/i],
  ['visual-identity', /characters\[\]\.visual_identity/i],
  ['visual-shape', /appearance:\{apparent_age:[\s\S]{0,300}performance:\{voice:[\s\S]{0,220}locks:\[\],avoid:\[\]/i],
  ['look-lock', /Bei \*\*Look Lock\*\*[\s\S]{0,300}keine Gameplay-Werte ändern/i],
  ['metadata-revision', /reine Metadatenrevision[\s\S]{0,240}parent_save_id[\s\S]{0,240}-VIS-R/i],
  ['sidecar', /Binärdateien nie in Saves einbetten/i],
  ['continuity-qa', /Continuity QA[\s\S]{0,220}`PASS`[\s\S]{0,120}`DRIFT`/i],
  ['media-fallback', /fehlt das Medium[\s\S]{0,100}Prompt-\/Storyboard-Paket/i],
  ['comic', /\*\*Comic Cut:\*\*/i],
  ['motion', /\*\*Motion Cut:\*\*/i],
  ['creator-kit', /\*\*Creator Kit:\*\*/i],
  ['merch', /\*\*Merch Forge:\*\*/i],
  ['creator-pack', /`Creator Pack` liefert/i],
  ['campaign-pack', /`Campaign Pack` verdichtet/i],
  ['physicality', /nicht generisches Neon-Cyberpunk/i],
  ['attribution', /ZEITRISS® – © pchospital/i],
  ['repo-url', /https:\/\/github\.com\/pchospital-lab\/ZEITRISS-md/i],
  ['license-check', /private Konzeptstudie mit `LICENSE CHECK`/i],
  ['license-contact', /chrononaut@zeitriss\.org/i],
  ['official-gate', /„Offiziell“ nur nach ausdrücklicher Bestätigung/i]
];

for (const [label, regex] of requiredAnchors) {
  assert.ok(regex.test(creator), `Creator-Bootstrap-Drift: '${label}' fehlt.`);
}

const forbiddenPatterns = [
  ['game-start', /Spiel starten \(solo klassisch\)/i],
  ['game-progression', /XP\/CU\/Px\/Heat[\s\S]{0,80}(?:erhöhen|vergeben|fortschreiben)/i],
  ['merch-free-pass', /Merch[\s\S]{0,160}(?:frei erlaubt|ohne Genehmigung)/i],
  ['pixel-guarantee', /pixelidentisch(?:e|er)? Ausgabe garantier/i],
  ['creator-autosave', /(?:nutze|tippe|erzeuge)[^\n]{0,80}`!save`/i]
];

for (const [label, regex] of forbiddenPatterns) {
  assert.ok(
    !regex.test(creator),
    `Creator-Bootstrap-Drift: verbotenes Muster '${label}' gefunden.`
  );
}

assert.ok(
  /Spielbetrieb ist \*\*reiner Text\*\*/i.test(play),
  'Spiel-Bootstrap-Drift: reiner Textmodus fehlt.'
);
assert.ok(
  /Bilder, Videos[\s\S]{0,180}nichttextlichen Medien/i.test(play),
  'Spiel-Bootstrap-Drift: Mediengenerierung ist nicht mehr gesperrt.'
);

for (const [label, schema] of [['Import', importSchema], ['Export', exportSchema]]) {
  const character = schema?.properties?.characters?.items || {};
  const props = character.properties || {};
  assert.ok(props.visual_identity, `${label}: Visual-Identity-Foundation fehlt.`);
  assert.ok(!(character.required || []).includes('visual_identity'), `${label}: visual_identity darf nicht required sein.`);
}

assert.ok(
  setupPy.includes('creator_bootstrap_instructions'),
  'Export-Drift: setup.py liest creator_bootstrap_instructions nicht.'
);
assert.ok(
  setupPy.includes('CREATOR_BOOTSTRAP_INSTRUCTIONS.md'),
  'Export-Drift: Creator-Bootstrap wird nicht exportiert.'
);

for (const [name, text] of [
  ['docs/creator-mode.md', guide],
  ['docs/setup-guide.md', setupGuide],
  ['README.md', readme]
]) {
  assert.ok(/Creator Studio/i.test(text), `${name}: Creator Studio fehlt.`);
}

assert.ok(
  /Spiel und Creator Studio niemals im selben Projekt mischen/i.test(guide),
  'Creator-Guide muss die Modustrennung ausdrücklich nennen.'
);
assert.ok(
  /CREATOR_BOOTSTRAP_INSTRUCTIONS\.md/i.test(setupGuide),
  'Setup-Guide muss den Creator-Bootstrap benennen.'
);
assert.ok(
  /Spiel- und Creator-Bootstrap niemals kombinieren;\s+das Creator Studio ist ein separates Projekt\./i.test(setupGuide),
  'Setup-Guide muss die verbindliche Modustrennung enthalten.'
);

console.log('creator-bootstrap-watchguard-ok');
