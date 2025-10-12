const assert = require('assert');

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
  assert.ok(/Foreshadow\s+2\/2/.test(bossStatus), 'Foreshadow-Zähler meldet nicht 2/2');
  const overlayBefore = rt.scene_overlay();
  assert.ok(overlayBefore.includes('FS 2/2'), 'Scene-Overlay zeigt keine Foreshadow 2/2');

  rt.StartMission();
  assert.strictEqual(rt.state.logs.hud.length, 0, 'HUD-Log wurde beim Missionsstart nicht zurückgesetzt');
  const bossAfter = rt.on_command('!boss status');
  assert.ok(/Foreshadow\s+0\/2/.test(bossAfter), 'Foreshadow-Zähler wurde nicht zurückgesetzt');
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

function main(){
  const foreshadow = runForeshadowGateCheck();
  const suggest = runSuggestToggleCheck();
  const arena = runPhaseStrikeArenaCheck();

  console.log('Foreshadow overlay (vorher):', foreshadow.overlayBefore);
  console.log('Foreshadow overlay (nachher):', foreshadow.overlayAfter);
  console.log('Boss-Status vor Reset:', foreshadow.bossStatus);
  console.log('Boss-Status nach Reset:', foreshadow.bossAfter);
  console.log('Suggest Overlay Verlauf:', suggest.overlayBase, '→', suggest.overlaySuggest, '→', suggest.overlayAsk);
  console.log('Suggest HUD-Tags:', suggest.hudTags.join(' | '));
  console.log('Arena Start:', arena.arenaMsg);
  console.log('Arena Phase-Strike Toast:', arena.toast);
  console.log('Arena Exit:', arena.exitMsg);
}

if (require.main === module){
  main();
}
