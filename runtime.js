const { version: ZR_VERSION = '4.2.2' } = require('./package.json');

let hudSequence = 0;

const state = {
  location: 'HQ',
  phase: 'core', // mission phase: core, transfer, rift
  campaign: {},
  character: {},
  team: {},
  loadout: {},
  economy: {},
  logs: {},
  ui: { gm_style: 'verbose' },
  exfil: null,
  fr_intervention: null,
  scene: { index: 0, foreshadows: 0, total: 12 },
  comms: { jammed: false, relays: 0, rangeMod: 1.0 }
};

function ensure_logs(){
  state.logs ||= {};
  if (!Array.isArray(state.logs.hud)){
    state.logs.hud = [];
  }
  return state.logs.hud;
}

function ensure_character(){
  state.character ||= {};
  if (state.character.self_reflection === undefined){
    state.character.self_reflection = true;
  }
  return state.character;
}

function self_reflection_enabled(){
  const character = ensure_character();
  return character.self_reflection !== false;
}

function set_self_reflection(on){
  const enabled = !!on;
  const character = ensure_character();
  character.self_reflection = enabled;
  const statusTag = enabled ? 'SF-ON' : 'SF-OFF';
  const message = enabled
    ? 'Self-Reflection aktiv – introspektive Sequenzen frei.'
    : 'Self-Reflection deaktiviert – Fokus bleibt extern.';
  hud_toast(message, statusTag);
  return { status: statusTag, message };
}

function hud_toast(message, tag = 'HUD'){
  const log = ensure_logs();
  hudSequence = (hudSequence + 1) % 10000;
  const entry = { id: `hud-${hudSequence.toString().padStart(4, '0')}`, tag, message };
  log.push(entry);
  if (log.length > 32){
    log.splice(0, log.length - 32);
  }
  writeLine(`[${tag}] ${message}`);
  return entry;
}

function ensure_exfil(){
  if (!state.exfil){
    state.exfil = {};
  }
  const exfil = state.exfil;
  if (!Number.isFinite(exfil.sweeps)) exfil.sweeps = 0;
  if (!Number.isFinite(exfil.stress)) exfil.stress = 0;
  if (!Number.isFinite(exfil.ttl_min)) exfil.ttl_min = 8;
  if (!Number.isFinite(exfil.ttl_sec)) exfil.ttl_sec = 0;
  exfil.active = !!exfil.active;
  exfil.armed = !!exfil.armed;
  if (typeof exfil.anchor !== 'string') exfil.anchor = null;
  if (typeof exfil.alt_anchor !== 'string') exfil.alt_anchor = null;
  return exfil;
}

function normalize_anchor(raw){
  if (!raw) return null;
  const trimmed = raw.trim();
  return trimmed.length ? trimmed.toUpperCase() : null;
}

function exfil_arm(anchor){
  const exfil = ensure_exfil();
  exfil.active = true;
  exfil.armed = true;
  const resolved = normalize_anchor(anchor) ?? exfil.anchor ?? '?';
  exfil.anchor = normalize_anchor(resolved) ?? '?';
  const parts = ['Exfil armiert'];
  if (exfil.anchor && exfil.anchor !== '?'){
    parts.push(`ANCR ${exfil.anchor}`);
  } else {
    parts.push('ANCR ?');
  }
  const message = parts.join(' · ');
  hud_toast(message);
  return message;
}

function exfil_set_alt(anchor){
  const exfil = ensure_exfil();
  const resolved = normalize_anchor(anchor);
  exfil.alt_anchor = resolved;
  const message = resolved ? `Exfil Alt-Anchor → ${resolved}` : 'Exfil Alt-Anchor entfernt';
  hud_toast(message);
  return message;
}

function parse_rw_token(token){
  const trimmed = (token || '').trim();
  if (!trimmed) throw new Error('RW-Angabe fehlt (mm:ss).');
  const match = trimmed.match(/^(-?\d+)(?::(\d{1,2}))?$/);
  if (!match) throw new Error('RW-Format ungültig. Erwartet mm:ss.');
  const min = parseInt(match[1], 10);
  const sec = match[2] !== undefined ? parseInt(match[2], 10) : 0;
  if (!Number.isFinite(min) || !Number.isFinite(sec) || sec < 0 || sec >= 60){
    throw new Error('RW-Format ungültig. Minuten/Sekunden prüfen.');
  }
  return { min: Math.max(0, min), sec: Math.max(0, sec) };
}

function exfil_tick(token){
  const exfil = ensure_exfil();
  const { min, sec } = parse_rw_token(token);
  exfil.ttl_min = min;
  exfil.ttl_sec = sec;
  const ttl = ttl_fmt(min, sec);
  const message = `Exfil Tick · RW ${ttl}`;
  hud_toast(message);
  return ttl;
}

function ensure_campaign(){
  state.campaign ||= {};
  if (typeof state.campaign.paradoxon_index !== 'number'){
    const raw = Number(state.campaign.paradoxon_index);
    state.campaign.paradoxon_index = Number.isFinite(raw) ? raw : 0;
  }
  if (typeof state.campaign.missions_since_px !== 'number'){
    state.campaign.missions_since_px = 0;
  }
  if (!Array.isArray(state.campaign.rift_seeds)){
    state.campaign.rift_seeds = [];
  }
  if (!Array.isArray(state.campaign.rift_blueprints)){
    state.campaign.rift_blueprints = [];
  }
}

function mission_temp(){
  return state.character?.attributes?.TEMP ?? 0;
}

function missions_required(temp){
  const t = Number.isFinite(temp) ? temp : 0;
  if (t <= 3) return 5;
  if (t <= 7) return 4;
  if (t <= 10) return 3;
  if (t <= 13) return 2;
  return 1;
}

function incrementParadoxon(delta = 1){
  ensure_campaign();
  const current = clamp(state.campaign.paradoxon_index ?? 0, 0, 5);
  const next = clamp(current + delta, 0, 5);
  state.campaign.paradoxon_index = next;
  return next;
}

function ClusterCreate(){
  ensure_campaign();
  if ((state.campaign.paradoxon_index ?? 0) < 5) return state.campaign.paradoxon_index;
  const count = 1 + Math.floor(Math.random() * 2);
  const seeds = [];
  for (let i = 0; i < count; i++){
    const id = `R-${Math.random().toString(36).slice(2, 6).toUpperCase()}`;
    seeds.push({
      id,
      name: 'Uncharted Rift',
      severity: 1 + Math.floor(Math.random() * 3),
      status: 'open'
    });
  }
  state.campaign.rift_seeds = [...state.campaign.rift_seeds, ...seeds];
  state.campaign.paradoxon_index = 0;
  state.campaign.missions_since_px = 0;
  writeLine(`ClusterCreate() aktiv – ${count} Rift-Seeds sichtbar.`);
  return state.campaign.paradoxon_index;
}

function completeMission(summary = {}){
  ensure_campaign();
  const events = [];
  const temp = typeof summary.temp === 'number' ? summary.temp : mission_temp();
  const required = missions_required(temp);
  const stabilized = summary.stabilized || summary.success || summary.completed === 'stabilized';
  if (stabilized){
    state.campaign.missions_since_px = (state.campaign.missions_since_px ?? 0) + 1;
    const progress = state.campaign.missions_since_px;
    events.push(`Codex: Mission stabilisiert (${progress}/${required} für Px+1).`);
    if (progress >= required){
      state.campaign.missions_since_px = 0;
      const after = incrementParadoxon(1);
      events.push(`Codex: Paradoxon-Index steigt auf ${after}/5.`);
      if (after >= 5){
        ClusterCreate();
        events.push('Codex: ClusterCreate() aktiv – neue Rift-Seeds verfügbar.');
      }
    }
  }
  return {
    events,
    required,
    missions_since_px: state.campaign.missions_since_px ?? 0,
    paradoxon_index: state.campaign.paradoxon_index ?? 0
  };
}

function reset_mission_state(){
  state.exfil = null;
  state.fr_intervention = null;
  state.scene = { index: 0, foreshadows: 0, total: 12 };
  state.comms = { jammed: false, relays: 0, rangeMod: 1.0 };
  state.start = null;
  hudSequence = 0;
}

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
  ensure_campaign();
  const n = clamp(state.campaign?.paradoxon_index ?? 0, 0, 5);
  const t = temp ?? mission_temp();
  const required = missions_required(t);
  const progress = clamp(state.campaign?.missions_since_px ?? 0, 0, required);
  const remaining = Math.max(0, required - progress);
  const eta = `${remaining} Mission${remaining === 1 ? '' : 'en'}`;
  return `Px ${px_bar(n)} (${n}/5) · TEMP ${t} · ETA +1 in ${eta}`;
}

const px_tracker = render_px_tracker;

function render_rewards(){
  return 'Rewards rendered';
}

function render_shop_tiers(level=1, faction_rep=0, rift_blueprints=[]){
  const t1 = level >= 1;
  const t2 = level >= 6;
  const count = Array.isArray(rift_blueprints) ? rift_blueprints.length : (rift_blueprints ? 1 : 0);
  const hasBlueprint = count > 0;
  const t3 = level >= 11 && faction_rep >= 3 && hasBlueprint;
  const bp = count;
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
  state.phase = 'core';
  state.comms = { jammed: false, relays: 0, rangeMod: 1.0 };
  state.exfil = { sweeps: 0, stress: 0, ttl_min: 8, ttl_sec: 0, active: false, armed: false, anchor: null, alt_anchor: null };
  const hudLog = ensure_logs();
  hudLog.length = 0;
  ensure_character();
  state.fr_intervention = roll_fr(state.campaign?.fr_bias || 'normal');
  state.scene = { index: 0, foreshadows: 0, total: 12 };
}

function scene_overlay(scene){
  const s = scene || state.scene;
  const ep = state.campaign?.episode ?? 0;
  const ms = state.campaign?.mission ?? 0;
  const sc = s.index ?? 0;
  const total = state.scene?.total ?? 12;
  const mode = state.ui.gm_style;
  const obj = state.campaign?.objective ?? '?';
  let h = `EP ${ep} · MS ${ms} · SC ${sc}/${total} · MODE ${mode} · Objective: ${obj}`;
  if (state.exfil){
    state.exfil.ttl_min = Math.max(0, state.exfil.ttl_min);
    state.exfil.ttl_sec = Math.max(0, state.exfil.ttl_sec);
    const ttl = ttl_fmt(state.exfil.ttl_min, state.exfil.ttl_sec);
    const ancr = state.exfil.anchor || '?';
    h += ` · ANCR ${ancr} · RW ${ttl}`;
    if (state.exfil.alt_anchor) h += ` · ALT ${state.exfil.alt_anchor}`;
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
    if (!self_reflection_enabled()){
      h += ' · SF-OFF';
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
  // phase may be 'core', 'transfer', 'rift', ...
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
    save_version: 5,
    zr_version: ZR_VERSION,
    location: s.location,
    phase: s.phase,
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
  if ((c.psi_heat ?? 0) !== 0) throw new Error('SaveGuard: Psi-Heat > 0.');
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
  if (data.save_version === 3){
    data.phase ||= 'core';
    data.save_version = 4;
  }
  if (data.save_version === 4){
    const character = data.character ||= {};
    const carryHeat = character.psi_heat ?? character.heat ?? 0;
    if (typeof carryHeat !== 'number' || !Number.isFinite(carryHeat)){
      character.psi_heat = 0;
    } else {
      character.psi_heat = carryHeat;
    }
    if (character.psi_heat_max === undefined && character.heat_max !== undefined){
      character.psi_heat_max = character.heat_max;
    }
    delete character.heat;
    delete character.heat_max;
    data.save_version = 5;
  }
  return data;
}

function hydrate_state(data){
  state.location = data.location || 'HQ';
  state.phase = data.phase || 'core';
  state.campaign = data.campaign || {};
  state.character = data.character || {};
  ensure_character();
  const legacyHeat = state.character.psi_heat ?? state.character.heat ?? 0;
  state.character.psi_heat = Number.isFinite(legacyHeat) ? legacyHeat : 0;
  delete state.character.heat;
  if (state.character.psi_heat_max === undefined && state.character.heat_max !== undefined){
    state.character.psi_heat_max = state.character.heat_max;
  }
  delete state.character.heat_max;
  state.team = data.team || {};
  state.loadout = data.loadout || {};
  state.economy = data.economy || {};
  state.logs = data.logs || {};
  state.ui = { gm_style: data.ui?.gm_style || 'verbose' };
  reset_mission_state();
  ensure_campaign();
}

function load_deep(raw){
  const data = typeof raw === 'string' ? JSON.parse(raw) : raw;
  const migrated = migrate_save(data);
  migrated.location = 'HQ';
  hydrate_state(migrated);
  const hud = scene_overlay();
  writeLine(hud);
  return { status: 'ok', state, hud };
}

function startSolo(mode='klassisch'){
  state.start = { type: 'solo', mode };
  state.location = 'HQ';
  state.character = {
    id: 'CHR-NEW',
    stress: 0,
    psi_heat: 0,
    self_reflection: true,
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_used: 1 }
  };
  ensure_campaign();
  return `solo-${mode}`;
}

function setupNpcTeam(size=0){
  state.team = { size };
}

function startGroup(mode='klassisch'){
  state.start = { type: 'gruppe', mode };
  state.location = 'HQ';
  state.team = { size: 0 };
  ensure_campaign();
  return `gruppe-${mode}`;
}

function launch_mission(){
  state.phase = 'transfer';
  StartMission();
  return 'mission-launched';
}

function debrief(st){
  const outcome = st || {};
  const result = completeMission(outcome);
  const lines = [render_rewards(), render_px_tracker(outcome.temp || mission_temp())];
  if (result.events.length){
    lines.push(result.events.join('\n'));
  }
  return lines.join('\n');
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
    if (cmd === '!help start' || cmd === '/help start'){
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
    if (cmd === '!help urban' || cmd === '/help urban'){
        return [
          'Urban Quick-Card:',
          'Deckung: Offen 0 · Teildeckung +1 SG · Volldeckung +2 SG (Peek kostet 1 Aktion).',
          'Mobile Deckung (Schild/Drohne) +1 SG, zerfällt nach 2 Treffern oder 1 Krit.',
          'Verfolgungsjagd: Distanzstufen 0–3. Erfolg +1, Stunt (SG +2) → +2 oder Komplikation für Gegner.',
          'Speed-Delta π = Fahrstufen-Differenz × 2 m pro Szene; Doppel-Fail → Crashbeat & Distanz −2.',
          'HUD-Tags: COVER · PURSUIT · MOVE – Toasts maximal 6 Wörter, haltet sie filmisch.'
        ].join('\n');
      }
    if (cmd === '!help sg' || cmd === '/help sg'){
        return [
          'SG & Exploding Quick-Card:',
          'Attribute 1–10 → W6 · ab 11 W10 · Heldenwürfel ab 14 (1× Reroll).',
          'Exploding: jede 6/10 explodiert einmal; Arena/Boss halbieren Overflow automatisch.',
          'SG-Richtwerte: Leicht 5 · Mittel 8–9 · Schwer 12 · Extrem 15+.',
          'Phasen-Fokus: Aufklärung 8 · Zugriff 12 · Exfiltration 10 – callt eure Ziele laut.',
          'Explosionsketten ansagen: z.B. 6→6→3 = 15, damit das HUD den Peak loggt.'
        ].join('\n');
      }
    if (cmd === 'begin mission'){
      return launch_mission();
    }
    if (cmd === '!gear shop'){
      ensure_campaign();
      const lvl = state.character?.lvl ?? 1;
      const rep = state.campaign?.faction_rep ?? 0;
      const bp = state.campaign?.rift_blueprints ?? [];
      return render_shop_tiers(lvl, rep, bp);
    }
  if (cmd === '!px'){
    return render_px_tracker();
  }
  if ((m = cmd.match(/^!exfil\s+arm(?:\s+(.+))?/))){
    return exfil_arm(m[1]);
  }
  if ((m = cmd.match(/^!exfil\s+alt(?:\s+(.+))?/))){
    return exfil_set_alt(m[1]);
  }
  if ((m = cmd.match(/^!exfil\s+(?:tick|rw)\s+(.+)/))){
    const ttl = exfil_tick(m[1]);
    return `RW ${ttl}`;
  }
  if (cmd === '!exfil status'){
    const exfil = ensure_exfil();
    const ttl = ttl_fmt(exfil.ttl_min, exfil.ttl_sec);
    const armed = exfil.armed ? 'armiert' : 'inaktiv';
    const alt = exfil.alt_anchor ? ` · ALT ${exfil.alt_anchor}` : '';
    return `Exfil ${armed} · ANCR ${exfil.anchor || '?'} · RW ${ttl}${alt}`;
  }
  if (cmd === '!sf off' || cmd === 'sf off' || cmd === 'self reflection off' || cmd === 'self-reflection off'){
    const result = set_self_reflection(false);
    return `${result.status} – introspektive Sequenzen gesperrt.`;
  }
  if (cmd === '!sf on' || cmd === 'sf on' || cmd === 'self reflection on' || cmd === 'self-reflection on'){
    const result = set_self_reflection(true);
    return `${result.status} – introspektive Sequenzen freigegeben.`;
  }
  if (cmd === '!sf' || cmd === '!sf status' || cmd === 'sf status'){
    return self_reflection_enabled()
      ? 'SF-ON – introspektive Sequenzen erlaubt.'
      : 'SF-OFF – Fokus bleibt extern.';
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
  completeMission,
  incrementParadoxon,
  ClusterCreate,
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
