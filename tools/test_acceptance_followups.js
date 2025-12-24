const assert = require('assert');
const mission5Fixture = require('../internal/qa/fixtures/mission5_badge_snapshots.json');

if (typeof global.hud_tag !== 'function'){
  global.hud_tag = () => {};
}

function freshRuntime(){
  delete require.cache[require.resolve('../runtime')];
  const rt = require('../runtime');
  return rt;
}

function runForeshadowGateCheck(){
  const rt = freshRuntime();
  rt.startSolo('klassisch');
  rt.state.campaign.episode = 2;
  rt.state.campaign.mission = 5;
  rt.state.campaign.type = 'rift';
  rt.state.campaign.objective = 'Mission 5 Gate QA';
  rt.state.scene = { index: 0, foreshadows: 0, total: 12 };

  const beforeHud = rt.state.logs.hud.length;
  rt.ForeshadowHint('Boss-Encounter in Szene 10', 'Foreshadow');
  rt.ForeshadowHint('Rift-Anomalie → Stabilisationsfenster', 'Foreshadow');
  assert.strictEqual(rt.state.logs.hud.length, beforeHud + 2, 'Foreshadow toasts fehlen');
  const bossStatus = rt.on_command('!boss status');
  assert.ok(/FS\s+2\/2/.test(bossStatus), 'Foreshadow-Zähler meldet nicht 2/2');
  const overlayBefore = rt.scene_overlay();
  assert.strictEqual(overlayBefore, null, 'Scene-Overlay sollte im HQ leer sein');

  rt.StartMission();
  const hudAfterStart = rt.state.logs.hud.map(({ tag, message }) => ({ tag, message }));
  assert.strictEqual(
    hudAfterStart[0]?.tag,
    'CASE',
    'Case-Stage-Overlay sollte als erstes HUD-Element erscheinen'
  );
  assert.ok(
    hudAfterStart.some(entry => entry.tag === 'BOSS' && entry.message === 'GATE 2/2 · FS 0/2'),
    'Gate-Toast nach Reset fehlt'
  );
  assert.ok(
    hudAfterStart.some(entry => entry.tag === 'ENTRY'),
    'EntryChoice-Toast fehlt nach Missionsstart'
  );
  const foreignTags = hudAfterStart.filter(entry => !['BOSS', 'CASE', 'ENTRY', 'SF'].includes(entry.tag));
  assert.strictEqual(foreignTags.length, 0, 'HUD-Log enthält Rest-Einträge');
  const bossAfter = rt.on_command('!boss status');
  assert.ok(/FS\s+0\/2/.test(bossAfter), 'Foreshadow-Zähler wurde nicht zurückgesetzt');
  const overlayAfter = rt.scene_overlay();
  assert.ok(overlayAfter.includes('FS 0/2'), 'Scene-Overlay meldet nach Reset nicht 0/2');

  return {
    overlayBefore,
    overlayAfter,
    bossStatus,
    bossAfter
  };
}

function runSuggestToggleCheck(){
  const rt = freshRuntime();
  rt.startSolo('klassisch');
  rt.StartMission();
  const overlayBase = rt.scene_overlay();
  assert.ok(!overlayBase.includes('· SUG'), 'Suggest-Markierung sollte deaktiviert sein');

  const onResult = rt.set_suggest_mode(true);
  assert.strictEqual(onResult.status, 'SUG-ON', 'Suggest-Modus meldet kein SUG-ON');
  const overlaySuggest = rt.scene_overlay();
  assert.ok(overlaySuggest.includes('· SUG'), 'Scene-Overlay zeigt Suggest-Markierung nicht');

  const offResult = rt.set_suggest_mode(false);
  assert.strictEqual(offResult.status, 'SUG-OFF', 'Suggest-Modus meldet kein SUG-OFF');
  const overlayAsk = rt.scene_overlay();
  assert.ok(!overlayAsk.includes('· SUG'), 'Scene-Overlay sollte nach Ask kein SUG zeigen');

  const hudTags = rt.state.logs.hud.map(entry => `[${entry.tag}] ${entry.message}`);
  return { overlayBase, overlaySuggest, overlayAsk, hudTags };
}

function runPhaseStrikeArenaCheck(){
  const rt = freshRuntime();
  rt.startGroup('klassisch');
  rt.state.campaign.episode = 4;
  rt.state.campaign.mode = 'core';
  rt.state.economy = { credits: 1500 };
  rt.state.team = {
    size: 3,
    members: [
      { name: 'Beta', lvl: 8 },
      { name: 'Gamma', lvl: 7 }
    ]
  };

  const taxBefore = rt.phase_strike_tax();
  assert.strictEqual(taxBefore, 0, 'Phase-Strike-Steuer sollte außerhalb der Arena 0 sein');
  const arenaMsg = rt.arenaStart({ teamSize: 3, mode: 'squad' });
  assert.ok(/Arena initiiert/.test(arenaMsg), 'Arena-Startmeldung fehlt');
  assert.strictEqual(rt.state.campaign.mode, 'pvp', 'Kampagnenmodus wurde nicht auf PvP gesetzt');
  assert.strictEqual(rt.state.arena.phase_strike_tax, 1, 'Arena setzt Phase-Strike-Steuer nicht auf 1');

  const cost = rt.phase_strike_cost(rt.state, { feedback: true });
  assert.strictEqual(cost, 3, 'Phase-Strike-Kosten ohne Feedback stimmen nicht');
  const toast = rt.state.logs.hud.find(entry => entry.tag === 'ARENA' && /Phase-Strike/.test(entry.message));
  assert.ok(toast, 'Phase-Strike-Toast wurde nicht protokolliert');

  const exitMsg = rt.arenaExit();
  assert.ok(/Arena Ende/.test(exitMsg), 'Arena-Ende wurde nicht gemeldet');

  return { arenaMsg, toast: toast.message, exitMsg };
}

function runPsiHeatTraceCheck(){
  const rt = freshRuntime();
  rt.startSolo('klassisch');
  rt.state.campaign.episode = 1;
  rt.state.campaign.mission = 2;
  rt.state.scene = { index: 0, foreshadows: 0, total: 12 };

  rt.log_psi_event({ category: 'psi_heat_inc', delta: 1, trigger: 'conflict:alpha' });
  rt.log_psi_event({ category: 'psi_heat_inc', delta: 2, trigger: 'conflict:alpha' });
  const flushed = rt.log_psi_event({ category: 'psi_heat_inc', delta: 1, trigger: 'conflict:beta', scene_index: 1, flush: true });
  assert.ok(flushed && flushed.category === 'psi_heat_inc', 'Psi-Heat-Inkrement wurde nicht geschrieben');

  const reset = rt.reset_psi_heat('hq_transfer');
  const psiLog = rt.state.logs.psi.slice(-3);
  const categories = psiLog.map(({ category }) => category);
  assert.ok(categories.includes('psi_heat_inc') && categories.includes('psi_heat_reset'), 'Psi-Heat-Trace fehlt Inkrement oder Reset');
  const aggEntry = psiLog.find((entry) => entry.category === 'psi_heat_inc' && entry.delta === 3);
  assert.ok(aggEntry, 'Psi-Heat sollte pro Konflikt aggregiert werden (Delta 3 erwartet)');
  assert.ok(Array.isArray(aggEntry.triggers) && aggEntry.triggers.includes('conflict:alpha'), 'Trigger-Liste wurde nicht übernommen');
  assert.ok(reset && reset.category === 'psi_heat_reset', 'Psi-Heat-Reset wurde nicht protokolliert');
  assert.strictEqual(rt.state.character.psi_heat, 0, 'Psi-Heat wurde nach Reset nicht geleert');

  return { aggEntry, reset };
}

function runAccessibilityRoundtripCheck(){
  const rt = freshRuntime();
  rt.startSolo('klassisch');
  rt.set_accessibility_option('contrast', 'high');
  rt.set_accessibility_option('badges', 'compact');
  rt.set_accessibility_option('pace', 'slow');
  const saved = rt.save_deep();

  const reloaded = freshRuntime();
  reloaded.load_deep(saved);
  assert.deepStrictEqual(
    {
      contrast: 'high',
      badge_density: 'compact',
      output_pace: 'slow'
    },
    {
      contrast: reloaded.state.ui.contrast,
      badge_density: reloaded.state.ui.badge_density,
      output_pace: reloaded.state.ui.output_pace
    },
    'Accessibility-Werte sind nach dem Laden nicht identisch'
  );

  const legacy = JSON.parse(JSON.stringify(require('../internal/qa/fixtures/savegame_v6_full.json').saves[0]));
  legacy.ui = undefined;
  legacy.contrast = 'high';
  legacy.badge_density = 'dense';
  legacy.output_pace = 'fast';

  const legacyRuntime = freshRuntime();
  legacyRuntime.load_deep(legacy);
  assert.deepStrictEqual(
    {
      contrast: 'high',
      badge_density: 'dense',
      output_pace: 'fast'
    },
    {
      contrast: legacyRuntime.state.ui.contrast,
      badge_density: legacyRuntime.state.ui.badge_density,
      output_pace: legacyRuntime.state.ui.output_pace
    },
    'Legacy-Accessibility-Felder werden nicht korrekt gemappt'
  );

  return {
    roundtrip: reloaded.state.ui,
    legacy: legacyRuntime.state.ui
  };
}

function runMissionFiveBadgeCheck(){
  const rt = freshRuntime();
  const originalRandom = Math.random;
  Math.random = () => 0.12;
  try {
    rt.startSolo('klassisch');
    rt.state.campaign.episode = 2;
    rt.state.campaign.mission = 5;
    rt.state.campaign.type = 'core';
    rt.state.campaign.objective = 'Mission 5 Badge QA';
    rt.state.scene = { index: 0, foreshadows: 0, total: 12 };
    rt.state.logs.flags.foreshadow_gate_snapshot = 2;
    rt.state.logs.flags.foreshadow_gate_expected = true;

    const hqOverlay = rt.scene_overlay();
    assert.strictEqual(hqOverlay, mission5Fixture.hq_overlay, 'HQ-Overlay für Mission 5 weicht von der Referenz ab');

    const sfOff = rt.on_command('!sf off');
    assert.strictEqual(sfOff, mission5Fixture.sf_off, 'SF-OFF-Toast fehlt oder ist verändert');

    const startOverlay = rt.StartMission();
    assert.strictEqual(startOverlay, mission5Fixture.mission_overlay, 'Mission-Start-Overlay stimmt nicht mit dem Snapshot überein');

    const hudMission = rt.state.logs.hud.map(({ tag, message }) => ({ tag, message }));
    assert.deepStrictEqual(hudMission, mission5Fixture.hud_mission, 'HUD-Toast-Log beim Start entspricht nicht dem Golden File');

    const bossStatus = rt.on_command('!boss status');
    assert.strictEqual(bossStatus, mission5Fixture.boss_status, 'Boss-Status liefert nicht Gate 2/2 · FS 0/4');

    rt.state.scene.index = 10;
    rt.completeMission({ reason: 'completed' });
    const hudAfter = rt.state.logs.hud.map(({ tag, message }) => ({ tag, message }));
    assert.deepStrictEqual(hudAfter, mission5Fixture.hud_after, 'SF-Reset/HUD-Log nach Mission 5 stimmt nicht');

    const flags = rt.state.logs.flags;
    Object.entries(mission5Fixture.flag_checks).forEach(([key, expected]) => {
      assert.strictEqual(flags[key], expected, `Flag ${key} entspricht nicht dem Snapshot`);
    });
    assert.ok(
      typeof flags.self_reflection_auto_reset_at === 'string' && flags.self_reflection_auto_reset_at.trim(),
      'Flag self_reflection_auto_reset_at fehlt nach Mission 5'
    );

    rt.state.location = 'HQ';
    rt.state.phase = 'core';
    rt.state.exfil = { active: false };
    rt.state.campaign.exfil = { active: false };
    const saved = rt.save_deep();
    const reloaded = freshRuntime();
    reloaded.load_deep(saved);
    const loadHud = reloaded.state.logs.hud.map(({ tag, message }) => ({ tag, message }));
    assert.deepStrictEqual(
      loadHud.slice(0, mission5Fixture.hud_after.length),
      mission5Fixture.hud_after,
      'HUD-Log nach Load (Mission 5) stimmt im Kern nicht'
    );
    const loadFlags = reloaded.state.logs.flags;
    Object.entries(mission5Fixture.flag_checks).forEach(([key, expected]) => {
      assert.strictEqual(loadFlags[key], expected, `Load-Flag ${key} entspricht nicht dem Snapshot`);
    });
    assert.ok(
      typeof loadFlags.self_reflection_auto_reset_at === 'string' && loadFlags.self_reflection_auto_reset_at.trim(),
      'Flag self_reflection_auto_reset_at fehlt nach Load'
    );

    return { hqOverlay, sfOff, startOverlay, hudMission, bossStatus, hudAfter };
  } finally {
    Math.random = originalRandom;
  }
}

function main(){
  const foreshadow = runForeshadowGateCheck();
  const suggest = runSuggestToggleCheck();
  const arena = runPhaseStrikeArenaCheck();
  const mission5 = runMissionFiveBadgeCheck();
  const psiHeat = runPsiHeatTraceCheck();
  const accessibility = runAccessibilityRoundtripCheck();

  console.log('Foreshadow overlay (vorher):', foreshadow.overlayBefore);
  console.log('Foreshadow overlay (nachher):', foreshadow.overlayAfter);
  console.log('Boss-Status vor Reset:', foreshadow.bossStatus);
  console.log('Boss-Status nach Reset:', foreshadow.bossAfter);
  console.log('Suggest Overlay Verlauf:', suggest.overlayBase, '→', suggest.overlaySuggest, '→', suggest.overlayAsk);
  console.log('Suggest HUD-Tags:', suggest.hudTags.join(' | '));
  console.log('Arena Start:', arena.arenaMsg);
  console.log('Arena Phase-Strike Toast:', arena.toast);
  console.log('Arena Exit:', arena.exitMsg);
  console.log('Mission 5 HQ Overlay:', mission5.hqOverlay);
  console.log('Mission 5 Start Overlay:', mission5.startOverlay);
  console.log('Mission 5 HUD Start:', mission5.hudMission.map(({ tag, message }) => `[${tag}] ${message}`).join(' | '));
  console.log('Mission 5 HUD Reset:', mission5.hudAfter.map(({ tag, message }) => `[${tag}] ${message}`).join(' | '));
  console.log('Psi-Heat Trace:', psiHeat.aggEntry, psiHeat.reset);
  console.log('Accessibility Roundtrip:', accessibility.roundtrip, accessibility.legacy);
}

if (require.main === module){
  main();
}
