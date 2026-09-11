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
assert.ok(creator.endsWith('\n'), 'Creator-Bootstrap muss mit finalem Newline enden.');
assert.ok(!creator.includes('\r'), 'Creator-Bootstrap muss LF-only sein.');
assert.ok(!/\n{3,}/.test(creator), 'Creator-Bootstrap enthält unnötige Mehrfach-Leerzeilen.');

const requiredAnchors = [
  ['creator-role', /ZEITRISS® Creator Studio/i],
  ['masterprompt-retrieval', /Vor der ersten quellengebundenen Antwort[\s\S]{0,180}# ZEITRISS - System Prompt/i],
  ['save-continuity-retrieval', /Vor Save-Prüfung[\s\S]{0,180}Save-\/Continuity-Modul/i],
  ['retrieval-fail-closed', /Fehlt eine Pflichtquelle[\s\S]{0,180}(?:keinen|oder) ladbaren Save/i],
  ['mode-boundary', /Im Creator-Modus wird \*\*nicht gespielt\*\*/i],
  ['play-redirect', /separates Projekt[\s\S]{0,100}PROJECT_BOOTSTRAP_INSTRUCTIONS\.md/i],
  ['source-save', /v7-Save-JSON\(s\)[\s\S]{0,100}Quellenkorpus/i],
  ['private-default', /Ohne Angabe arbeite als `privat`[\s\S]{0,220}(?:Veröffentlichung|Monetarisierung)/i],
  ['creator-board', /Creator Board[\s\S]{0,260}Hero Asset[\s\S]{0,260}Story Cut[\s\S]{0,260}Growth Asset/i],
  ['board-nur-offen', /Nur bei offenem Einstieg, Ideensuche oder ausdrücklichem Aufruf[\s\S]{0,180}Creator Board/i],
  ['konkreter-auftrag-vorrang', /konkreter Medienauftrag hat Vorrang/i],
  ['canon-ledger', /\*\*KANON\*\*[\s\S]{0,180}\*\*ADAPTIERT\*\*[\s\S]{0,180}\*\*KONZEPT\*\*/i],
  ['no-fake-quotes', /Keine „Originalzitate“ ohne Transkript/i],
  ['historisches-equipment', /frühere[n]? gespielte[n]? Szene[\s\S]{0,260}damaliges Equipment[\s\S]{0,260}(?:nicht|niemals) automatisch rückwirkend/i],
  ['kein-gruppenmerge', /persönliche Saves sind Quellenkorpus, kein mechanischer Gruppenmerge/i],
  ['visual-identity', /characters\[\]\.visual_identity/i],
  ['visual-shape', /appearance:\{apparent_age:[\s\S]{0,300}performance:\{voice:[\s\S]{0,220}locks:\[\],avoid:\[\]/i],
  ['look-lock', /Bei \*\*Look Lock\*\*[\s\S]{0,260}revision:1[\s\S]{0,120}revision \+1/i],
  ['metadata-revision', /Metadatenrevision[\s\S]{0,260}parent_save_id[\s\S]{0,220}-VIS-R/i],
  ['target-only-revision', /Nur Ziel-`visual_identity`, `save_id`, `parent_save_id` ändern/i],
  ['output-validation', /validiere Visual-Block und Gesamtsave vor Ausgabe/i],
  ['patch-source-contract', /CREATOR_PATCH[\s\S]{0,100}source_save_id[\s\S]{0,80}char_id[\s\S]{0,80}visual_identity/i],
  ['sidecar', /Binärdateien nie in Saves einbetten/i],
  ['continuity-qa', /Continuity QA[\s\S]{0,220}`PASS`[\s\S]{0,120}`DRIFT`/i],
  ['media-fallback', /Fehlt (?:das Medium|die Fähigkeit)[\s\S]{0,140}Prompt-\/Storyboard-Paket/i],
  ['keine-falsche-datei', /Behaupte keine generierte Datei für einen Textentwurf/i],
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
assert.ok(
  /cfg\.get\(["']creator_bootstrap_instructions["']\)/.test(setupPy),
  'Export-Drift: Creator-Key muss optional per cfg.get(...) gelesen werden.'
);
assert.ok(
  /has_creator_bootstrap:\s*bool\s*=\s*False/.test(setupPy),
  'Export-Drift: has_creator_bootstrap muss rückwärtskompatibel False defaulten.'
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
assert.ok(
  /ZEITRISS – Spiel[\s\S]{0,80}ZEITRISS – Creator/i.test(setupGuide),
  'Setup-Guide muss das praktische Zwei-Projekte-Beispiel enthalten.'
);
assert.ok(
  /Projektgedächtnis ersetzt keinen portablen v7-Save/i.test(setupGuide) &&
    /Projektbezogenes Gedächtnis[\s\S]{0,180}ersetzt keinen Save/i.test(setupGuide),
  'Setup-Guide muss Projektgedächtnis als Kontext statt Save-Autorität erklären.'
);
assert.ok(
  /meta\/creator_bootstrap_instructions\.md[\s\S]{0,120}system\/CREATOR_BOOTSTRAP_INSTRUCTIONS\.md/i.test(setupGuide),
  'Setup-Guide muss beide Creator-Bootstrap-Pfade zuordnen.'
);
assert.ok(
  /geteiltes Projekt ist trotzdem kein[\s\S]{0,40}synchroner gemeinsamer Spielchat/i.test(setupGuide),
  'Setup-Guide darf Projektfreigabe nicht als synchronen Spielchat darstellen.'
);

console.log('creator-bootstrap-watchguard-ok');
