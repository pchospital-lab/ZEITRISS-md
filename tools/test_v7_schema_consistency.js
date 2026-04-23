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
  'internal/qa/fixtures/savegame_v7_chat_load.json',
  'internal/qa/fixtures/savegame_v7_level_history.json'
];

const forbiddenRoot = ['save_version', 'zr_version', 'character', 'party', 'team', 'arc_dashboard', 'location', 'phase'];
const forbiddenCampaign = ['mission_in_episode'];
const forbiddenCharacter = ['attributes'];
const forbiddenArc = ['open_seeds', 'open_questions', 'timeline', 'offene_seeds', 'fragen'];

function checkFixture(relPath){
  const save = readJson(relPath);
  const label = path.basename(relPath);

  assert.strictEqual(save.v, 7, `${label}: v muss 7 sein.`);
  assert.strictEqual(typeof save.zr, 'string', `${label}: zr fehlt.`);
  assert.strictEqual(typeof save.save_id, 'string', `${label}: save_id fehlt.`);
  assert.ok(Object.prototype.hasOwnProperty.call(save, 'parent_save_id'), `${label}: parent_save_id fehlt.`);
  assert.ok(Object.prototype.hasOwnProperty.call(save, 'merge_id'), `${label}: merge_id fehlt.`);
  assert.strictEqual(typeof save.branch_id, 'string', `${label}: branch_id fehlt.`);
  assert.ok(Array.isArray(save.characters) && save.characters.length > 0, `${label}: characters[] fehlt.`);
  assert.ok(save.campaign && typeof save.campaign === 'object', `${label}: campaign fehlt.`);
  assert.ok(save.continuity && typeof save.continuity === 'object', `${label}: continuity fehlt.`);
  assert.ok(save.summaries && typeof save.summaries === 'object', `${label}: summaries fehlt.`);
  assert.ok(save.arc && typeof save.arc === 'object', `${label}: arc fehlt.`);
  assert.ok(save.ui && typeof save.ui === 'object', `${label}: ui fehlt.`);

  const continuity = save.continuity;
  assert.ok(continuity.last_seen && typeof continuity.last_seen === 'object', `${label}: continuity.last_seen fehlt.`);
  assert.ok(continuity.split && typeof continuity.split === 'object', `${label}: continuity.split fehlt.`);
  assert.ok(Array.isArray(continuity.roster_echoes), `${label}: continuity.roster_echoes[] fehlt.`);
  assert.ok(Array.isArray(continuity.shared_echoes), `${label}: continuity.shared_echoes[] fehlt.`);
  assert.ok(Array.isArray(continuity.convergence_tags), `${label}: continuity.convergence_tags[] fehlt.`);
  assert.ok(Array.isArray(continuity.npc_roster), `${label}: continuity.npc_roster[] fehlt.`);
  assert.ok(Array.isArray(continuity.active_npc_ids), `${label}: continuity.active_npc_ids[] fehlt.`);
  assert.ok(save.logs && save.logs.flags && Array.isArray(save.logs.flags.continuity_conflicts), `${label}: logs.flags.continuity_conflicts[] fehlt.`);
  assert.ok(continuity.roster_echoes.length <= 5, `${label}: continuity.roster_echoes überschreitet Budget (max 5).`);
  assert.ok(continuity.shared_echoes.length <= 6, `${label}: continuity.shared_echoes überschreitet Budget (max 6).`);
  assert.ok(continuity.convergence_tags.length <= 4, `${label}: continuity.convergence_tags überschreitet Budget (max 4).`);

  // Pflichtformat-Check: shared_echoes[] und roster_echoes[] Items müssen Objekt mit 'tag' sein
  // (Schema-Invariante seit 2026-04-23 nach Run-D-Merge-Analyse)
  continuity.shared_echoes.forEach((item, i) => {
    assert.strictEqual(typeof item, 'object', `${label}: continuity.shared_echoes[${i}] muss Objekt sein (kein String oder Primitive).`);
    assert.ok(item !== null && !Array.isArray(item), `${label}: continuity.shared_echoes[${i}] muss Objekt sein (nicht null/array).`);
    assert.ok(typeof item.tag === 'string' && item.tag.length > 0, `${label}: continuity.shared_echoes[${i}] braucht 'tag' als non-leeren String (Fremdkeys wie {echo:...} sind verboten).`);
  });
  continuity.roster_echoes.forEach((item, i) => {
    assert.strictEqual(typeof item, 'object', `${label}: continuity.roster_echoes[${i}] muss Objekt sein.`);
    assert.ok(item !== null && !Array.isArray(item), `${label}: continuity.roster_echoes[${i}] muss Objekt sein (nicht null/array).`);
    assert.ok(typeof item.tag === 'string' && item.tag.length > 0, `${label}: continuity.roster_echoes[${i}] braucht 'tag' als non-leeren String.`);
  });

  // level_history-Platzierung: NUR pro Character, NIEMALS auf Root (seit 2026-04-23)
  assert.ok(!('level_history' in save), `${label}: Root-Level 'level_history' verboten — gilt pro Character (siehe Masterprompt §F Level-Up-Exklusivitäts-Pflichtgate).`);

  assert.strictEqual(typeof save.summaries.summary_last_episode, 'string', `${label}: summary_last_episode muss String sein.`);
  assert.strictEqual(typeof save.summaries.summary_last_rift, 'string', `${label}: summary_last_rift muss String sein.`);
  assert.strictEqual(typeof save.summaries.summary_active_arcs, 'string', `${label}: summary_active_arcs muss String sein.`);

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
    // level_history (optional) muss Objekt sein, Keys = Level-Nummer als String, Values = Wahl-Objekt mit 'choice'
    if ('level_history' in character) {
      const lh = character.level_history;
      assert.strictEqual(typeof lh, 'object', `${label}: characters[${index}].level_history muss Objekt sein.`);
      assert.ok(lh !== null && !Array.isArray(lh), `${label}: characters[${index}].level_history muss Objekt (Map) sein, nicht Array/null.`);
      Object.entries(lh).forEach(([lvl, choice]) => {
        assert.ok(/^\d+$/.test(lvl), `${label}: characters[${index}].level_history Key '${lvl}' muss numerischer Level-String sein.`);
        assert.strictEqual(typeof choice, 'object', `${label}: characters[${index}].level_history['${lvl}'] muss Objekt sein.`);
        assert.ok(typeof choice.choice === 'string' && ['+1 Attribut', 'Talent/Upgrade', '+1 SYS'].includes(choice.choice),
          `${label}: characters[${index}].level_history['${lvl}'].choice muss einer der Werte sein: '+1 Attribut', 'Talent/Upgrade', '+1 SYS'.`);
      });
    }
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
