const state = {
  location: 'HQ',
  campaign: {},
  character: {},
  team: {},
  loadout: {},
  economy: {},
  logs: {},
  ui: { gm_style: 'verbose' },
  exfil: null,
  fr_intervention: null,
  scene: { index: 0, foreshadows: 0 }
};

function px_bar(px){
  return '▓'.repeat(px) + '░'.repeat(5 - px);
}

function px_tracker(temp){
  const paradox = 0;
  const remaining = 5 - paradox;
  return `Px ${px_bar(paradox)} (${paradox}/5) · TEMP ${temp} · +1 nach ${remaining} Missionen`;
}

function render_rewards(){
  return 'Rewards rendered';
}

function render_shop_tiers(level=1, faction_rep=0, rift_blueprints=[]){
  const t1 = level >= 1;
  const t2 = level >= 6;
  const t3 = level >= 11 && faction_rep >= 3;
  const bp = rift_blueprints.length;
  return `Shop-Tiers: T1:${t1 ? 'true' : 'false'} T2:${t2 ? 'true' : 'false'} T3:${t3 ? 'true' : 'false'} · BP:${bp}`;
}

function ttl_fmt(min=0, sec=0){
  const mm = String(Math.max(0, min)).padStart(2, '0');
  const ss = String(Math.max(0, sec)).padStart(2, '0');
  return `${mm}:${ss}`;
}

function roll_fr(){
  return 'ruhig';
}

function StartMission(){
  state.exfil = { sweeps: 0, stress: 0, ttl_min: 8, ttl_sec: 0 };
  state.fr_intervention = roll_fr();
}

function scene_overlay(scene){
  const s = scene || state.scene;
  const ep = 0, ms = 0, sc = 0;
  const mode = state.ui.gm_style;
  const obj = '?';
  let h = `EP ${ep} · MS ${ms} · SC ${sc}/12 · MODE ${mode} · Objective: ${obj}`;
  if (state.exfil){
    state.exfil.ttl_min = Math.max(0, state.exfil.ttl_min);
    state.exfil.ttl_sec = Math.max(0, state.exfil.ttl_sec);
    const ttl = ttl_fmt(state.exfil.ttl_min, state.exfil.ttl_sec);
    h += ` · TTL ${ttl}`;
    if (state.exfil.sweeps) h += ` · Sweeps:${state.exfil.sweeps}`;
    if (state.exfil.stress) h += ` · Stress ${state.exfil.stress}`;
  }
  if (s.index === 0 && state.fr_intervention){
    h += ` · FR:${state.fr_intervention}`;
  }
  return h;
}

function comms_check(device, range){
  const okDev = ['comlink', 'cable', 'relay', 'jammer_override'].includes(device);
  const okRng = range > 0 && !state.jammed;
  return okDev && okRng;
}

function must_comms(o){
  if (!comms_check(o.device, o.range)){
    throw new Error(
      'CommsCheck failed: require valid device/range or relay/jammer override. ' +
      'Tipp: Gerät=Comlink/Kabel/Relay oder Jammer-Override; Reichweite anpassen.'
    );
  }
}

function radio_tx(o){
  must_comms(o);
  return 'tx';
}

function radio_rx(o){
  must_comms(o);
  return 'rx';
}

function assert_foreshadow(n=2){
  if (state.ui.gm_style !== 'precision') return;
  const c = state.scene.foreshadows || 0;
  if (c < n) console.log(`Foreshadow low: ${c}/${n}`);
}

function select_state_for_save(s){
  return {
    save_version: 3,
    zr_version: '4.2.0',
    location: s.location,
    campaign: s.campaign,
    character: s.character,
    team: s.team,
    loadout: s.loadout,
    economy: s.economy,
    logs: s.logs,
    ui: { gm_style: s.ui?.gm_style ?? 'verbose' }
  };
}

function save_deep(s=state){
  if (s.location !== 'HQ') throw new Error('Save denied: HQ-only.');
  return JSON.stringify(select_state_for_save(s));
}

function migrate_save(data){
  if (!data.save_version) data.save_version = 1;
  if (data.save_version === 1){
    data.campaign ||= {};
    data.save_version = 2;
  }
  if (data.save_version === 2){
    data.ui ||= { gm_style: 'verbose' };
    data.save_version = 3;
  }
  return data;
}

function debrief(st){
  return `${render_rewards()}\n${px_tracker(st.temp || 0)}`;
}

function on_command(cmd){
  if (cmd === '!gear shop'){
    return render_shop_tiers(1, 0, []);
  }
  if (cmd === '!px'){
    return px_tracker(0);
  }
  if (cmd === 'modus precision'){
    state.ui.gm_style = 'precision';
    return 'GM_STYLE → precision (persistiert)';
  }
  if (cmd === 'modus verbose'){
    state.ui.gm_style = 'verbose';
    return 'GM_STYLE → verbose (persistiert)';
  }
  if (cmd === '!fr help'){
    return 'FR-Status:\nruhig · beobachter · aktiv';
  }
  if (cmd === '!boss status'){
    return `Foreshadow ${state.scene.foreshadows}`;
  }
  return '';
}

module.exports = {
  state,
  on_command,
  debrief,
  render_shop_tiers,
  px_tracker,
  StartMission,
  scene_overlay,
  radio_tx,
  radio_rx,
  assert_foreshadow,
  save_deep,
  migrate_save
};
