const { version: ZR_VERSION = '4.2.2' } = require('./package.json');

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
  scene: { index: 0, foreshadows: 0 },
  comms: { jammed: false, relays: 0, rangeMod: 1.0 }
};

function clamp(n, min, max){
  return Math.min(max, Math.max(min, n));
}

function writeLine(msg){
  console.log(msg);
}

function px_bar(n){
  const total = 5;
  return '█'.repeat(n) + '░'.repeat(total - n);
}

function render_px_tracker(temp){
  const n = clamp(state.campaign?.paradoxon_index ?? 0, 0, 5);
  const t = temp ?? (state.character?.attributes?.TEMP ?? 0);
  const eta = t <= 0 ? 'n/a' : `${Math.max(1, 6 - t)} ops`;
  return `Px ${px_bar(n)} (${n}/5) · TEMP ${t} · NEXT +1 in ${eta}`;
}

const px_tracker = render_px_tracker;

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

function seeded(seed){
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

function roll_fr(bias = 'normal', seed = null){
  const r = seed != null ? seeded(seed) : Math.random();
  let pR = 0.60, pB = 0.25;
  if (bias === 'hard'){ pR = 0.45; pB = 0.30; }
  if (bias === 'easy'){ pR = 0.75; pB = 0.20; }
  return r < pR ? 'ruhig' : (r < pR + pB ? 'beobachter' : 'aktiv');
}

function jam_now(on = true){
  state.comms.jammed = !!on;
}

function StartMission(){
  state.comms = { jammed: false, relays: 0, rangeMod: 1.0 };
  state.exfil = { sweeps: 0, stress: 0, ttl_min: 8, ttl_sec: 0 };
  state.fr_intervention = roll_fr(state.campaign?.fr_bias || 'normal');
  state.scene = { index: 0, foreshadows: 0 };
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
    const ancr = state.exfil.anchor || '?';
    h += ` · ANCR ${ancr} · RW ${ttl}`;
    if (state.exfil.sweeps) h += ` · Sweeps:${state.exfil.sweeps}`;
    if (state.exfil.stress) h += ` · Stress ${state.exfil.stress}`;
  }
    const px = state.campaign?.px ?? state.campaign?.paradoxon_index ?? 0;
    const sys = state.character?.attributes?.SYS_max ?? 0;
    const lvl = state.character?.lvl ?? '-';
    h += ` · Px ${px} · SYS ${sys} · Lvl ${lvl}`;
    if (s.index === 0 && state.fr_intervention){
      h += ` · FR:${state.fr_intervention}`;
    }
  return h;
}

function comms_check(device, range){
  const okDev = ['comlink', 'cable', 'relay', 'jammer_override'].includes(device);
  const jam = !!state.comms?.jammed;
  const okRng = (range * (state.comms?.rangeMod ?? 1)) > 0;
  const ok = okDev && okRng && (
    !jam || device === 'cable' || device === 'jammer_override' || device === 'relay'
  );
  return ok;
}

function codex_link_state(ctx){
  const c = ctx || state;
  if (c.location === 'HQ' || c.phase === 'transfer') return 'uplink';
  const dev = c.comms?.device;
  const rng = c.comms?.range_m;
  const jam = c.comms?.jammed;
  const inBubble = dev === 'comlink' && typeof rng === 'number' && rng <= 2000 && !jam;
  return inBubble ? 'field_online' : 'field_offline';
}

function require_uplink(ctx, action){
  const st = codex_link_state(ctx);
  if (st === 'uplink' || st === 'field_online') return true;
  throw new Error(
    'Codex offline – Relais setzen · Hardline/Terminal nutzen · Comlink koppeln.'
  );
}

function must_comms(o){
  if (!comms_check(o.device, o.range)){
    throw new Error(
      'CommsCheck failed: require valid device/range or relay/jammer override. ' +
      'Tipp: Terminal suchen / Comlink koppeln / Kabel/Relay nutzen / Jammer-Override aktivieren; Reichweite anpassen.'
    );
  }
}

function radio_tx(o){
  const ctx = { ...state, comms: { ...state.comms, device: o.device, range_m: o.range } };
  require_uplink(ctx, 'radio_tx');
  must_comms(o);
  return 'tx';
}

function radio_rx(o){
  const ctx = { ...state, comms: { ...state.comms, device: o.device, range_m: o.range } };
  require_uplink(ctx, 'radio_rx');
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
    zr_version: ZR_VERSION,
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
  const c = s.character || {};
  const a = c.attributes || {};
  if (c.stress !== 0) throw new Error('SaveGuard: stress > 0.');
  if (c.heat !== 0) throw new Error('SaveGuard: heat > 0.');
  if (a.SYS_used > a.SYS_max) throw new Error('SaveGuard: SYS overflow.');
  const required = [
    c.id,
    c.cooldowns,
    s.campaign?.paradoxon_index,
    s.economy,
    s.logs,
    s.ui
  ];
  if (required.some(v => v === undefined)){
    throw new Error('SaveGuard: missing fields.');
  }
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

function hydrate_state(data){
  state.location = data.location || 'HQ';
  state.campaign = data.campaign || {};
  state.character = data.character || {};
  state.team = data.team || {};
  state.loadout = data.loadout || {};
  state.economy = data.economy || {};
  state.logs = data.logs || {};
  state.ui = { gm_style: data.ui?.gm_style || 'verbose' };
}

function load_deep(raw){
  const data = typeof raw === 'string' ? JSON.parse(raw) : raw;
    const migrated = migrate_save(data);
    migrated.location = 'HQ';
    hydrate_state(migrated);
    const ep = state.campaign?.episode ?? 0;
    const ms = state.campaign?.mission ?? 0;
    const sc = state.scene?.index ?? 0;
    const total = state.scene?.total ?? 12;
    const px = state.campaign?.px ?? state.campaign?.paradoxon_index ?? 0;
    const sys = state.character?.attributes?.SYS_max ?? 0;
    const hud = `EP ${ep} · MS ${ms} · SC ${sc}/${total} · Px ${px} · SYS ${sys}`;
    writeLine(hud);
    return { status: 'ok', state, hud };
  }

function startSolo(mode='klassisch'){
  state.start = { type: 'solo', mode };
  state.location = 'HQ';
  state.character = {
    id: 'CHR-NEW',
    stress: 0,
    heat: 0,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_used: 1 }
  };
    return `solo-${mode}`;
}

function setupNpcTeam(size=0){
  state.team = { size };
}

function startGroup(mode='klassisch'){
  state.start = { type: 'gruppe', mode };
  state.location = 'HQ';
  state.team = { size: 0 };
  return `gruppe-${mode}`;
}

function launch_mission(){
  StartMission();
  return 'mission-launched';
}

function debrief(st){
  return `${render_rewards()}\n${render_px_tracker(st.temp || 0)}`;
}

function on_command(command){
    let cmd = command.toLowerCase().trim();
    if (cmd.startsWith('!load ')){
      const json = command.slice(6).trim();
      return load_deep(json);
    }
    if (cmd === '!load' || cmd === 'spiel laden' || cmd === 'spielstand laden'){
      return 'Codex: Poste Speicherstand als JSON.';
    }
    let m;
    if ((m = cmd.match(/^spiel starten \(solo\)(?:\s+(schnell|fast|klassisch|classic))?/))){
      const mode = (cmd.includes('schnell') || cmd.includes('fast')) ? 'schnell' : 'klassisch';
      return startSolo(mode);
    }
    if ((m = cmd.match(/^spiel starten\s*\(npc-team\)(?:\s+([0-4]))?(?:\s+(schnell|fast|klassisch|classic))?$/))){
      const mode = (cmd.includes('schnell') || cmd.includes('fast')) ? 'schnell' : 'klassisch';
      startSolo(mode);
      const size = m[1] ? parseInt(m[1], 10) : 0;
      setupNpcTeam(size);
      state.start.type = 'npc-team';
      return `npc-team-${mode}`;
    }
    if ((m = cmd.match(/^spiel starten\s*\(gruppe\)(?:\s+(schnell|fast|klassisch|classic))?$/))){
      const mode = (cmd.includes('schnell') || cmd.includes('fast')) ? 'schnell' : 'klassisch';
      return startGroup(mode);
    }
      if (cmd === '!help start'){
        return [
          'Startbefehle:',
          '- Spiel starten (solo) [klassisch|schnell]',
          '- Spiel starten (npc-team [0–4]) [klassisch|schnell]',
          '- Spiel starten (gruppe) [klassisch|schnell]',
          '- Spiel laden',
          'Klammern sind Pflicht. Rollen-Kurzformen: infil/tech/face/cqb/psi.',
          'Speichern nur im HQ. Px 5 ⇒ ClusterCreate() (Rift-Seeds nach Episodenende).'
        ].join('\n');
      }
    if (cmd === 'begin mission'){
      return launch_mission();
    }
    if (cmd === '!gear shop'){
      return render_shop_tiers(1, 0, []);
    }
  if (cmd === '!px'){
    return render_px_tracker(0);
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
  ZR_VERSION,
  state,
  on_command,
  debrief,
  render_shop_tiers,
  render_px_tracker,
  px_tracker,
  StartMission,
  scene_overlay,
  radio_tx,
  radio_rx,
  codex_link_state,
  require_uplink,
  assert_foreshadow,
  save_deep,
  migrate_save,
  load_deep,
  startSolo,
  setupNpcTeam,
  startGroup,
  jam_now,
  launch_mission
};
