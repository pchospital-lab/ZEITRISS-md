const fs = require('fs');
const path = require('path');

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const loadSchema = (name) => JSON.parse(fs.readFileSync(
  path.resolve(__dirname, '..', `systems/gameflow/${name}`),
  'utf8'
));
const schemas = [
  ['Import', loadSchema('saveGame.v7.schema.json')],
  ['Export', loadSchema('saveGame.v7.export.schema.json')]
];

for (const [label, schema] of schemas) {
  const character = schema?.properties?.characters?.items || {};
  const characterProps = character.properties || {};
  assert(characterProps.visual_identity, `${label}: visual_identity fehlt`);
  assert(!(character.required || []).includes('visual_identity'), `${label}: visual_identity darf nicht required sein`);

  const visual = characterProps.visual_identity;
  const required = ['v', 'status', 'revision', 'appearance', 'performance', 'locks', 'avoid'];
  assert(required.every((key) => visual.required.includes(key)), `${label}: Required-Felder unvollständig`);
  assert(visual.properties.v.const === 1, `${label}: Vertragsversion muss const 1 sein`);
  assert(JSON.stringify(visual.properties.status.enum) === JSON.stringify(['draft', 'locked']), `${label}: Status-Enum driftet`);
  assert(visual.properties.revision.minimum === 1, `${label}: Revision-Minimum driftet`);
  const appearanceRequired = ['apparent_age', 'stature', 'face', 'eyes', 'hair', 'skin', 'distinctive', 'visible_implants'];
  assert(appearanceRequired.every((key) => visual.properties.appearance.required.includes(key)), `${label}: Appearance-Requireds unvollständig`);
  assert(['voice', 'movement'].every((key) => visual.properties.performance.required.includes(key)), `${label}: Performance-Requireds unvollständig`);
  assert(visual.properties.appearance.properties.distinctive.maxItems === 8, `${label}: distinctive-Cap driftet`);
  assert(visual.properties.appearance.properties.visible_implants.maxItems === 8, `${label}: visible_implants-Cap driftet`);
  assert(visual.properties.locks.maxItems === 12, `${label}: locks-Cap driftet`);
  assert(visual.properties.avoid.maxItems === 12, `${label}: avoid-Cap driftet`);
  assert(visual.properties.reference.required.includes('asset_id'), `${label}: reference.asset_id muss required sein`);
  assert(visual.properties.reference.properties.sha256.pattern === '^[A-Fa-f0-9]{64}$', `${label}: SHA-Pattern driftet`);
}

const exportCharacterProps = schemas[1][1].properties.characters.items.properties;
for (const key of ['psi_heat', 'pp', 'psi_abilities', 'artifact']) {
  assert(Object.prototype.hasOwnProperty.call(exportCharacterProps, key), `Export: altes optionales Feld fehlt: ${key}`);
}

const strictVisual = exportCharacterProps.visual_identity;
assert(strictVisual.additionalProperties === false, 'Export: visual_identity muss strikt sein');
assert(strictVisual.properties.appearance.additionalProperties === false, 'Export: appearance muss strikt sein');
assert(strictVisual.properties.performance.additionalProperties === false, 'Export: performance muss strikt sein');
assert(strictVisual.properties.reference.additionalProperties === false, 'Export: reference muss strikt sein');

console.log('v7-character-schema-watchguard-ok');
