const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.join(__dirname, '..');

function readJson(relPath){
  return JSON.parse(fs.readFileSync(path.join(ROOT, relPath), 'utf8'));
}

const fixtures = [
  'internal/qa/fixtures/savegame_v7_5er_hq_highlevel.json',
  'internal/qa/fixtures/savegame_v7_split_3_2_merge.json',
  'internal/qa/fixtures/savegame_v7_merge_rift_pvp.json',
  'internal/qa/fixtures/savegame_v7_chronopolis_roundtrip.json',
  'internal/qa/fixtures/savegame_v7_abort_resume.json',
  'internal/qa/fixtures/savegame_v7_chat_load.json'
];

const forbiddenRoot = ['save_version', 'zr_version', 'character', 'party', 'team', 'arc_dashboard'];
const forbiddenCampaign = ['mission_in_episode'];
const forbiddenCharacter = ['attributes'];
const forbiddenArc = ['open_seeds', 'open_questions', 'timeline', 'offene_seeds', 'fragen'];

function checkFixture(relPath){
  const save = readJson(relPath);
  const label = path.basename(relPath);

  assert.strictEqual(save.v, 7, `${label}: v muss 7 sein.`);
  assert.strictEqual(typeof save.zr, 'string', `${label}: zr fehlt.`);
  assert.ok(Array.isArray(save.characters) && save.characters.length > 0, `${label}: characters[] fehlt.`);
  assert.ok(save.campaign && typeof save.campaign === 'object', `${label}: campaign fehlt.`);

  forbiddenRoot.forEach((key) => {
    assert.ok(!(key in save), `${label}: Legacy-Rootfeld '${key}' darf im v7-Export nicht gesetzt sein.`);
  });

  forbiddenCampaign.forEach((key) => {
    assert.ok(!(key in save.campaign), `${label}: Legacy-Campaignfeld '${key}' entdeckt.`);
  });

  save.characters.forEach((character, index) => {
    forbiddenCharacter.forEach((key) => {
      assert.ok(!(key in character), `${label}: characters[${index}] enthält Legacyfeld '${key}'.`);
    });
  });

  if (save.arc && typeof save.arc === 'object') {
    forbiddenArc.forEach((key) => {
      assert.ok(!(key in save.arc), `${label}: arc enthält Legacyfeld '${key}'.`);
    });
  }
}

readJson('systems/gameflow/saveGame.v7.schema.json');
fixtures.forEach(checkFixture);

console.log('v7-schema-consistency-ok');
