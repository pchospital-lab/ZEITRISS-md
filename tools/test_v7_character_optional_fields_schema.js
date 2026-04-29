const fs = require('fs');
const path = require('path');

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const schemaPath = path.resolve(__dirname, '..', 'systems/gameflow/saveGame.v7.export.schema.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
const characterProps = schema?.properties?.characters?.items?.properties || {};

for (const key of ['psi_heat', 'pp', 'psi_abilities', 'artifact']) {
  assert(Object.prototype.hasOwnProperty.call(characterProps, key), `v7-character-schema-watchguard: Feld fehlt: ${key}`);
}

console.log('v7-character-schema-watchguard-ok');
