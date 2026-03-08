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
  assert.ok(save.continuity && typeof save.continuity === 'object', `${label}: continuity fehlt.`);

  const continuity = save.continuity;
  assert.ok(continuity.last_seen && typeof continuity.last_seen === 'object', `${label}: continuity.last_seen fehlt.`);
  assert.ok(continuity.split && typeof continuity.split === 'object', `${label}: continuity.split fehlt.`);
  assert.ok(Array.isArray(continuity.roster_echoes), `${label}: continuity.roster_echoes[] fehlt.`);
  assert.ok(Array.isArray(continuity.shared_echoes), `${label}: continuity.shared_echoes[] fehlt.`);
  assert.ok(Array.isArray(continuity.convergence_tags), `${label}: continuity.convergence_tags[] fehlt.`);
  assert.ok(save.logs && save.logs.flags && Array.isArray(save.logs.flags.continuity_conflicts), `${label}: logs.flags.continuity_conflicts[] fehlt.`);
  assert.ok(continuity.roster_echoes.length <= 5, `${label}: continuity.roster_echoes überschreitet Budget (max 5).`);
  assert.ok(continuity.shared_echoes.length <= 6, `${label}: continuity.shared_echoes überschreitet Budget (max 6).`);
  assert.ok(continuity.convergence_tags.length <= 4, `${label}: continuity.convergence_tags überschreitet Budget (max 4).`);

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
