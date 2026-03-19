---
title: "ZEITRISS 4.2.6 – Runtime-Makros (Mirror aus Toolkit)"
version: 4.2.6
tags: [meta]
---

# ZEITRISS 4.2.6 – Runtime-Makros (Mirror aus Toolkit)

Dieser Mirror spiegelt den Runtime-Makro-Block aus
`systems/toolkit-runtime-makros.md` als internes Entwicklungsartefakt.
Der Regeltext steht weiterhin im Toolkit (`systems/toolkit-gpt-spielleiter.md`);
die Makros wurden in eine eigene Datei (`systems/toolkit-runtime-makros.md`)
ausgelagert. Runtime-Änderungen werden hier parallel gespiegelt, damit QA und
Reviews technische Diffs getrennt prüfen können.

## Technische Makros & Runtime-Definitionen (KI-Spielleiter-Interna)

> Dieser Abschnitt enthält Jinja2-Template-Code und Pseudocode-Definitionen
> für die KI-Spielleitung zur Laufzeit. Er enthält keine Spielregeln -
> der Regeltext steht oben. Makros laufen intern und dürfen nie als
> Rohtext im Chat erscheinen.

⟨# === Init-Block: Variablen & Defaults === #⟩
⟪ hud_tag(segs|join('')) ⟫
⟨% set campaign = campaign or {} %⟩
⟨# Legacy: Compliance-Hook deaktiviert, bleibt als Fallback #⟩
⟨% if campaign.compliance_shown_today is not defined %⟩
⟨% set campaign.compliance_shown_today = false %⟩
⟨% else %⟩
⟨% set campaign.compliance_shown_today = campaign.compliance_shown_today | bool %⟩
⟨% endif %⟩
⟨% if campaign.boss_dr is not defined %⟩
⟨% set campaign.boss_dr = 0 %⟩
⟨% endif %⟩
⟨% if campaign.research_level is not defined %⟩
⟨% set campaign.research_level = 0 %⟩
⟨% endif %⟩
⟨% set scene_min = 12 %⟩
⟨% set artifact_pool_v3 = load_json('master-index.json')['artifact_pool_v3'] %⟩
⟨% set core_mini_pool = gpull('gameplay/kreative-generatoren-begegnungen.md#core_mini_pool') %⟩
⟨% set core_arc_boss_pool = gpull('gameplay/kreative-generatoren-begegnungen.md#core_arc_boss_pool') %⟩
⟨% set boss_pressure_pool = [
['Timer 90s','Verstärkung in 2min','schwindende Deckung'],
['Timer 90s','Verstärkung in 2min','wanderndes Sichtfenster'],
['Timer 90s','Verstärkung in 2min','Ressourcen-Clamp']
] %⟩
⟨% set boss_pressure_cooldown_length = 2 %⟩
⟨% if campaign.boss_pressure_cooldowns is not defined %⟩
⟨% set campaign.boss_pressure_cooldowns = {} %⟩
⟨% endif %⟩
⟨% set risk_icon_map = {
'R1': '🟢 R1',
'R2': '🟡 R2',
'R3': '🟠 R3',
'R4': '🔴 R4'
} %⟩
⟨% set risk_label_map = {
'R1': 'Niedrig',
'R2': 'Moderat',
'R3': 'Hoch',
'R4': 'Kritisch'
} %⟩
⟨% set exfil = exfil or {
'enabled': true,
'ttl_start_minutes': 8,
'ttl_cost_per_sweep_min': 2,
'stress_gain_per_sweep': 1,
'stress_gain_on_complication': 1,
'hot_exfil_on_ttl_zero': true,
'px_loss_on_hot_fail': false
} %⟩
⟨% if campaign.exfil is not defined %⟩
⟨% set campaign.exfil = {
'active': false,
'ttl': 0,
'hot': false,
'sweeps': 0,
'stress': 0,
'anchor': '?',
'armed': false
} %⟩
⟨% endif %⟩
⟨% if kodex is not defined %⟩
⟨% set kodex = namespace(dev_raw=false) %⟩
⟨% elif kodex.dev_raw is not defined %⟩
⟨% set kodex.dev_raw = false %⟩
⟨% endif %⟩
⟨% if ui is not defined %⟩
⟨% set ui = {
'mode_display': 'label',
'suppress_rank_on_narrow': true,
'dice': {'debug_rolls': true}
} %⟩
⟨% elif ui.dice is not defined %⟩
⟨% set ui = ui | combine({'dice': {'debug_rolls': true⟫, recursive=true) %⟩
⟨% elif ui.dice.debug_rolls is not defined %⟩
⟨% set ui.dice = ui.dice | combine({'debug_rolls': true}, recursive=true) %⟩
⟨% endif %⟩
⟨% set allow_event_icons = true %⟩
⟨% if settings is defined and settings.allow_event_icons is defined %⟩
⟨% set allow_event_icons = settings.allow_event_icons %⟩
⟨% endif %⟩
⟨% if fx is not defined %⟩
⟨% set fx = {
'transfer': {
'on_mission_enter': 'always',
'on_mission_exit': 'always',
'redirect_hours_default': 6,
'show_redirect': true,
'hud_out_template':
'Nullzeit-Puffer · Transfer 3…2…1 · Redirect: +{hours}h (Self-Collision Guard)',
'hud_in_template_core': 'Fenster stabil · {ttl} · Return 3…2…1',
'hud_in_template_rift': 'Resonanzfenster stabil · {ttl} · Return 3…2…1',
'sensory_out':
'Kältezug. Druck auf den Ohren. Farben kippen. Cut - Zielrealität steht scharf.',
'sensory_in_stable':
'Kälte. Leere. Das Umgebungsgeräusch kippt - und reißt ab.',
'sensory_in_hot':
'Instabiles Fenster. Bild zerreißt, Zug reißt euch zurück. Schwarzer Cut.'
}
} %⟩
⟨% endif %⟩
⟨% if mission_fx is not defined %⟩⟨% set mission_fx = {} %⟩⟨% endif %⟩
⟨% if ranks is not defined %⟩
⟨% set ranks = {'order': ['Recruit','Operator I','Operator II','Lead','Specialist','Chief']} %⟩
⟨% endif %⟩
⟨% if env is not defined %⟩⟨% set env = {} %⟩⟨% endif %⟩
⟨% if state is not defined %⟩⟨% set state = {} %⟩⟨% endif %⟩
⟨% set gm_style = env.GM_STYLE
if env.GM_STYLE is defined and env.GM_STYLE
else state.gm_style
if state.gm_style is defined
else 'klassik' %⟩
⟨% set state.gm_style = gm_style %⟩
⟨% if scene is not defined %⟩⟨% set scene = {} %⟩⟨% endif %⟩
⟨% if state.logs is not defined or state.logs is none %⟩
⟨% set state.logs = {} %⟩
⟨% endif %⟩
⟨% if state.logs.foreshadow is not defined or state.logs.foreshadow is none %⟩
⟨% set state.logs.foreshadow = [] %⟩
⟨% endif %⟩
⟨% if state.logs.flags is not defined or state.logs.flags is none %⟩
⟨% set state.logs.flags = {} %⟩
⟨% endif %⟩
⟨% if state.logs.flags.chronopolis_warn_seen is not defined %⟩
⟨% set state.logs.flags.chronopolis_warn_seen = false %⟩
⟨% else %⟩
⟨% set state.logs.flags.chronopolis_warn_seen = state.logs.flags.chronopolis_warn_seen | bool %⟩
⟨% endif %⟩
⟨% if state.logs.flags.compliance_shown_today is not defined %⟩
⟨% set state.logs.flags.compliance_shown_today = campaign.compliance_shown_today | default(false) | bool %⟩
⟨% else %⟩
⟨% set state.logs.flags.compliance_shown_today = state.logs.flags.compliance_shown_today | bool %⟩
⟨% endif %⟩
⟨% if campaign.compliance_shown_today and not state.logs.flags.compliance_shown_today %⟩
⟨% set state.logs.flags.compliance_shown_today = true %⟩
⟨% elif state.logs.flags.compliance_shown_today and not campaign.compliance_shown_today %⟩
⟨% set campaign.compliance_shown_today = true %⟩
⟨% endif %⟩
⟨% if state.logs.flags.offline_help_last_scene is not defined %⟩
⟨% set state.logs.flags.offline_help_last_scene = None %⟩
⟨% endif %⟩
⟨% set state.logs.flags.offline_help_count = state.logs.flags.offline_help_count | default(0) | int %⟩
⟨% if state.flags is not defined or state.flags is none %⟩
⟨% set state.flags = {} %⟩
⟨% endif %⟩
⟨% if state.flags.runtime is not defined or state.flags.runtime is none %⟩
⟨% set state.flags.runtime = {} %⟩
⟨% endif %⟩
⟨% if state.flags.runtime.skip_entry_choice is not defined %⟩
⟨% set state.flags.runtime.skip_entry_choice = false %⟩
⟨% else %⟩
⟨% set state.flags.runtime.skip_entry_choice = state.flags.runtime.skip_entry_choice | bool %⟩
⟨% endif %⟩
⟨# UI-Init: Nur Defaults setzen wenn KEIN Save geladen wurde.
Bei Load hat state.ui bereits die Werte aus dem Save -
suggest_mode darf NICHT auf false zurückgesetzt werden! #⟩
⟨% if state.ui is not defined or state.ui is none %⟩
⟨% set state.ui = {'suggest_mode': false, 'action_mode': 'uncut'} %⟩
⟨% endif %⟩
⟨% if state.ui.suggest_mode is not defined %⟩
⟨% set state.ui.suggest_mode = false %⟩
⟨% else %⟩
⟨# Save-Wert beibehalten - nur zu bool casten, nicht überschreiben #⟩
⟨% set state.ui.suggest_mode = state.ui.suggest_mode | bool %⟩
⟨% endif %⟩
⟨# Nach Load: SUG-Badge reaktivieren wenn suggest_mode true #⟩
⟨% if state.ui.suggest_mode %⟩
⟪ hud_tag('· SUG') ⟫
⟨% endif %⟩
⟨% set state.ui.action_mode = 'uncut' %⟩
⟨% if state.scene is not defined or state.scene is none %⟩
⟨% set state.scene = {} %⟩
⟨% endif %⟩
⟨% if state.scene.foreshadows is not defined or state.scene.foreshadows is none %⟩
⟨% set state.scene.foreshadows = state.logs.foreshadow | length %⟩
⟨% endif %⟩
⟨% if campaign.entry_choice_skipped is not defined %⟩
⟨% set campaign.entry_choice_skipped = false %⟩
⟨% else %⟩
⟨% set campaign.entry_choice_skipped = campaign.entry_choice_skipped | bool %⟩
⟨% endif %⟩

⟨% macro set_mode_display(style) -%⟩
⟨% set ui.mode_display = style %⟩
⟪ hud_tag('Mode-Display: ' ~ style) ⟫
⟨%- endmacro %⟩

⟨# === Campaign-Mode-Logik === #⟩
⟨% set \_campaign_mode_raw = campaign.mode | default('mixed') %⟩
⟨% set \_campaign_mode = \_campaign_mode_raw|string %⟩
⟨% set \_campaign_mode = \_campaign_mode|trim|lower %⟩
⟨% if \_campaign_mode in ['arena', 'sparring'] %⟩
⟨% set \_campaign_mode = 'pvp' %⟩
⟨% endif %⟩
⟨% set campaign.mode = \_campaign_mode or 'mixed' %⟩
⟨% set is_pvp_mode = campaign.mode == 'pvp' or (arena is defined and arena and arena.active) %⟩
⟨% if campaign.mode == 'preserve' %⟩
⟨% set campaign.seed_source = 'preserve' %⟩
⟨% elif campaign.mode == 'trigger' %⟩
⟨% set campaign.seed_source = 'trigger' %⟩
⟪ hud_tag('Briefing: kleineres Übel sichern (Trigger).') ⟫
⟨% elif campaign.mode == 'mixed' %⟩
⟨% set campaign.seed_source = campaign.seed_source or 'preserve' %⟩
⟪ hud_tag('Mixed-Pool aktiv - Seed-Typ pro Mission festlegen.') ⟫
⟨% elif is_pvp_mode %⟩
⟨% set campaign.seed_source = 'preserve' %⟩
⟪ hud_tag('Arena-Sparring aktiv - PvP-Modus gebunden. Seeds bleiben deaktiviert.') ⟫
⟨% else %⟩
⟨% set campaign.seed_source = campaign.seed_source or 'preserve' %⟩
⟪ hud_tag('Modus ' ~ campaign.mode ~ ' aktiv.') ⟫
⟨% endif %⟩

⟨# === Szenen-Init === #⟩
⟨% macro episode_seed_make() -%⟩
⟨% set preserve = gpull('gameplay/kreative-generatoren-missionen.md#preserve_pool') %⟩
⟨% set trigger = gpull('gameplay/kreative-generatoren-missionen.md#trigger_pool') %⟩
⟨% set pool = preserve + trigger %⟩
⟨% set seeds = random.sample(pool, 10) %⟩
⟨% set campaign.episode_plan = seeds %⟩
⟨% set campaign.episode_start = seeds[0].id %⟩
⟨% set campaign.episode_end = seeds[-1].id %⟩
⟨%- endmacro %⟩

⟨# === Missions-, Szenen- und Boss-Makros === #⟩
⟨% set used = campaign.hq_moments_used | default([], true) %⟩
⟨% if 'FOCUS' not in used %⟩
⟪ hud_tag('HQ:FOCUS · +1 Präzision') ⟫
⟨% set campaign.hq_moments_used = used + ['FOCUS'] %⟩
⟨% endif %⟩

````

Die Buffs sind vor allem als **Feld-Downtime** (Safehouse, Nullzeit-Puffer) gedacht. CALM trägt seinen
Psi-Bonus in die nächste Mission und hält ihn bis zur ersten Psi-Probe aufrecht - auch wenn `StartScene('HQ')`
Stress und Psi-Heat bereits auf 0 setzt.

Haltet die Toasts auf **maximal sechs Worte** und gebt sofort an, welcher
mechanische Effekt greift.

⟨% macro fr_intervention_roll() -%⟩
  ⟨% if campaign.fr_intervention is not none %⟩⟨% return %⟩⟨% endif %⟩
  ⟨% set roll = rng_roll(1,6) %⟩
  ⟨% set r = roll[0][0] %⟩
  ⟪ roll_check(roll[1], 0, r, true, roll[0], important=false) ⟫
  ⟨% set status = 'ruhig' if r<=2 else ('Beobachter' if r<=4 else 'aktiver Eingriff') %⟩
  ⟪ hud_tag('FR-INTRV: ' ~ status) ⟫
  ⟨% if status == 'Beobachter' %⟩
    ⟨% set campaign.fr_observer_pending = true %⟩
  ⟨% endif %⟩
  ⟨% set campaign.fr_intervention = status %⟩
⟨%- endmacro %⟩

⟨% macro fr_contact_allowed(loc) -%⟩
  ⟨% if loc != 'HQ' %⟩
    ⟪ hud_tag('Direkter FR-Kontakt nur im HQ erlaubt') ⟫
    ⟨% return %⟩
  ⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro deep_merge(base, override) -%⟩
  ⟪ base | combine(override, recursive=true) ⟫
⟨%- endmacro %⟩

⟨% macro get_transfer_cfg() -%⟩
  ⟨% set base = fx.transfer %⟩
  ⟨% set override = mission_fx.get('transfer', {}) %⟩
  ⟪ deep_merge(base, override) ⟫
⟨%- endmacro %⟩

⟨% macro should_show_transfer_enter(tcfg) -%⟩
  ⟨% set opt = tcfg.on_mission_enter %⟩
  ⟪
    opt == 'always'
    or (opt == 'first_session' and campaign.mission == 1)
    or (opt == 'first_episode' and campaign.mission_in_episode == 1)
  ⟫
⟨%- endmacro %⟩

⟨% macro should_show_transfer_exit(tcfg) -%⟩
  ⟨% set opt = tcfg.on_mission_exit %⟩
  ⟪ opt == 'always' or (opt == 'on_exfil_only' and campaign.exfil.active) ⟫
⟨%- endmacro %⟩

⟨% macro transfer_out_from_hq(ctx, tcfg) -%⟩
  ⟨% set hours = tcfg.get('redirect_hours', tcfg.redirect_hours_default) %⟩
  ⟨% if tcfg.show_redirect %⟩
    ⟪ hud_tag(tcfg.hud_out_template.format(hours=hours)) ⟫
  ⟨% endif %⟩
  ⟪ tcfg.sensory_out ⟫
⟨%- endmacro %⟩

⟨% macro transfer_back_to_hq(state, tcfg, hot=false) -%⟩
  ⟨% if hot %⟩
    ⟪ hud_tag('HOT-Exfil · Fenster instabil') ⟫
    ⟪ tcfg.sensory_in_hot ⟫
  ⟨% else %⟩
    ⟨% set ttl_token = ttl_fmt(campaign.exfil.ttl) if campaign.exfil.active else ttl_fmt(exfil.ttl_start_minutes) %⟩
    ⟨% set tpl = tcfg.hud_in_template_rift if campaign.type == 'rift' else tcfg.hud_in_template_core %⟩
    ⟪ hud_tag(tpl.format(ttl=ttl_token)) ⟫
    ⟪ tcfg.sensory_in_stable ⟫
  ⟨% endif %⟩
  ⟪ cut_to_hq_van() ⟫
⟨%- endmacro %⟩

⟨% macro cut_to_hq_van() -%⟩⟨%- endmacro %⟩

<!-- Macro: StartMission -->
⟨% macro SkipEntryChoice() -%⟩
  ⟨% set state.flags.runtime.skip_entry_choice = true %⟩
  ⟨% set campaign.entry_choice_skipped = true %⟩
⟨%- endmacro %⟩

⟨% macro AllowEntryChoice() -%⟩
  ⟨% set state.flags.runtime.skip_entry_choice = false %⟩
  ⟨% set campaign.entry_choice_skipped = false %⟩
⟨%- endmacro %⟩

⟨% macro StartMission(
  total=12,
  seed_id=None,
  objective=None,
  type="core",
  epoch=None,
  dt_hours=0,
  fx_override=None,
  tags=None
) %⟩
⟨% set mission_fx = fx_override or {} %⟩
⟪ AllowEntryChoice() ⟫
⟨% if campaign.mission is none %⟩
  ⟨% set campaign.mission = 1 %⟩
⟨% else %⟩
  ⟨% set campaign.mission = campaign.mission + 1 %⟩
⟨% endif %⟩
⟨% set campaign.episode = ((campaign.mission - 1) // 10) + 1 %⟩
⟨% set campaign.mission_in_episode = ((campaign.mission - 1) % 10) + 1 %⟩
⟨# Episodebeginn: Seed-Gate wieder schließen #⟩
⟨% if campaign.mission_in_episode == 1 %⟩
  ⟨% set campaign.episode_completed = false %⟩
⟨% endif %⟩
⟨% set campaign.scene = 1 %⟩
⟨% set campaign.seed_id = seed_id %⟩
⟨% set campaign.objective = objective %⟩
⟨% set campaign.type = type %⟩
⟨% set campaign.epoch = epoch %⟩
⟨% set campaign.fr_observer_pending = false %⟩
⟨% set campaign.fr_observer_note = false %⟩
⟨% set campaign.fr_intervention = none %⟩
⟨% set scene = {'index': 0, 'foreshadows': []} %⟩
⟨% set campaign.exfil = campaign.exfil | combine({'sweeps': 0, 'stress': 0}, recursive=true) %⟩
⟨% set campaign.mission_tags = [] %⟩
⟨% set tags_source = tags if tags is not none else mission_fx.get('tags') %⟩
⟨% if tags_source %⟩
  ⟨% if tags_source is string %⟩
    ⟨% set tag_items = tags_source.replace(',', '|').split('|') %⟩
  ⟨% else %⟩
    ⟨% set tag_items = tags_source %⟩
  ⟨% endif %⟩
  ⟨% set normalized = [] %⟩
  ⟨% for tag in tag_items %⟩
    ⟨% set token = tag|trim|lower %⟩
    ⟨% if token %⟩
      ⟨% set normalized = normalized + [token] %⟩
    ⟨% endif %⟩
  ⟨% endfor %⟩
  ⟨% set campaign.mission_tags = normalized %⟩
⟨% endif %⟩
⟪ redirect_same_slot(campaign.epoch, dt_hours) ⟫
⟨% set tcfg = get_transfer_cfg() %⟩
⟨% if should_show_transfer_enter(tcfg) %⟩
  ⟪ transfer_out_from_hq(campaign, tcfg) ⟫
⟨% endif %⟩
⟨% if campaign.kodex_log is none %⟩⟨% set campaign.kodex_log = {} %⟩⟨% endif %⟩
⟨% if campaign.boss_history is none %⟩⟨% set campaign.boss_history = [] %⟩⟨% endif %⟩
⟨% if campaign.boss_pool_usage is none %⟩⟨% set campaign.boss_pool_usage = {} %⟩⟨% endif %⟩
⟨% set campaign.boss_defeated = false %⟩
⟨% set campaign.rift_loot_prompted = false %⟩
⟨% set campaign.last_rift_boss = none %⟩
⟨% set campaign.last_rift_loot_entry = none %⟩
⟨% set campaign.legendary_roll_pending = false %⟩
⟨% if campaign.loot_log is not defined or campaign.loot_log is none %⟩⟨% set campaign.loot_log = [] %⟩⟨% endif %⟩
⟨# Mission-Invarianten #⟩
⟨% if campaign.type == "core" %⟩
  ⟨% set campaign.scene_total = 12 %⟩
  ⟨# LINT:CORE_BOSS_M05_M10 #⟩
  ⟨% set campaign.boss_allowed = (campaign.mission_in_episode in [5,10]) %⟩
  ⟨% set campaign.artifact_allowed = false %⟩
⟨% elif campaign.type == "rift" %⟩
  ⟨% set campaign.scene_total = 14 %⟩
  ⟨% set campaign.boss_required_scene = 10 %⟩
  ⟨% set campaign.artifact_allowed = true %⟩
⟨% endif %⟩
⟨% set existing_bonus = getattr(campaign, 'stars_bonus', 0) %⟩
⟨% set next_episode = getattr(campaign, 'next_episode', None) %⟩
⟨% set queued_bonus = next_episode.get('sg_bonus', 0) if next_episode else 0 %⟩
⟨% if queued_bonus %⟩
  ⟨% set campaign.stars_bonus = queued_bonus %⟩
  ⟨% set campaign.next_episode = next_episode | combine({'sg_bonus': 0}, recursive=true) %⟩
⟨% else %⟩
  ⟨% set campaign.stars_bonus = existing_bonus | int %⟩
⟨% endif %⟩
⟨% if not campaign.stars_bonus %⟩
  ⟨% set campaign.stars_bonus = 0 %⟩
⟨% endif %⟩
⟨% set campaign.stars_overlay_done = false %⟩
⟪ star_bonus_overlay() ⟫
⟨# Fraktionsintervention pro Mission #⟩
⟪ fr_intervention_roll() ⟫
⟪ DelayConflict(4) ⟫
Diese Mission spielt vollständig in der realen Welt.
Funk läuft über Comlinks mit begrenzter Reichweite; jede Störung hat ein
physisches Gerät. Kodex synchronisiert über reale Hardware mit dem
Nullzeit-HQ-Archiv; bei Ausfall bleibt nur der Offline-HUD. Signale,
Objekte und Gegner agieren ausschließlich physisch.

`!dashboard status` liefert das Arc-Dashboard als Text (Seeds, letzte Fraktionsmeldungen, offene Fragen)
und dient als unmittelbarer Evidenz-Snapshot für Beta-Logs.
⟨% endmacro %⟩

Beispielaufruf im Kampagnenstart:

```pseudo
StartMission(total=12, type="core", epoch=target_epoch)
if boss := generate_boss("core", campaign.mission, target_epoch):
    kodex.inject(boss.briefing_block)
````

Das Toolkit löst `generate_boss()` intern aus, sobald eine Core-Mission
Nummer 5 oder 10 erreicht oder eine Rift-Op Szene 10 betritt. Die SL muss den
Makro nicht manuell aufrufen.
In Rift-Ops ruft `NextScene()` bei Szene 10 ebenfalls
`generate_boss("rift", ...)` auf und warnt das Team im HUD.

### finale_guard() Macro

Verhindert das Auslösen eines Finales vor Szene 10.

```pseudo
if campaign.scene < 10:
    forbid("finale")
```

<!-- Macro: DelayConflict -->

⟨% macro DelayConflict(n, allow="") -%⟩
⟨% set base = n %⟩
⟨% set tags = getattr(campaign, 'mission_tags', []) %⟩
⟨% set modifier = 0 %⟩
⟨% for tag in tags %⟩
⟨% if tag in ['heist', 'street'] %⟩
⟨% set modifier = modifier + 1 %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨% set effective = base - modifier %⟩
⟨% if effective < 2 %⟩⟨% set effective = 2 %⟩⟨% endif %⟩
⟨% set campaign.delayConflict_base = base %⟩
⟨% set campaign.delayConflict = effective %⟩
⟨% set allow_tokens = [] %⟩
⟨% if allow is string %⟩
⟨% for item in allow.replace(',', '|').split('|') %⟩
⟨% set token = item|trim %⟩
⟨% if token %⟩
⟨% set allow_tokens = allow_tokens + [token] %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨% elif allow is sequence %⟩
⟨% for item in allow %⟩
⟨% if item is string %⟩
⟨% set token = item|trim %⟩
⟨% if token %⟩
⟨% set allow_tokens = allow_tokens + [token] %⟩
⟨% endif %⟩
⟨% elif item %⟩
⟨% set allow_tokens = allow_tokens + [item] %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨% endif %⟩
⟨% set campaign.delayConflict_allow = allow_tokens %⟩
⟨%- endmacro %⟩
⟨% macro can_open_conflict(kind) -%⟩
⟨% set g = {'threshold': campaign.delayConflict or 4, 'allow': campaign.delayConflict_allow or []} %⟩
⟨% if campaign.scene >= g.threshold %⟩
⟪ true ⟫
⟨% else %⟩
⟪ kind in g.allow ⟫
⟨% endif %⟩
⟨%- endmacro %⟩
Rufe `DelayConflict(4)` direkt nach `StartMission()` auf, ohne den Makroaufruf
anzuzeigen, um Konflikte erst ab Szene 4 zuzulassen. Standardmäßig bleibt
`allow` leer; gib etwa `DelayConflict(4, allow='ambush|vehicle_chase')` (oder
`ambush,vehicle_chase`) an, wenn frühe Überfälle oder Verfolgungen erlaubt sein
sollen. Missions-Tags `heist` oder `street` senken das Limit automatisch um
jeweils eine Szene (Minimum: Szene 2).

<!-- Macro: ShowComplianceOnce -->

⟨% macro ShowComplianceOnce(qa_mode=False, force=False) -%⟩
⟨# Compliance-Hinweis neutralisiert: kein Output, keine Flag-Änderung. #⟩
⟨%- endmacro %⟩

### NextScene Wrapper

Nutze `NextScene` zu Beginn jeder Szene. Die optionale Variable `role` gibt der
KI eine dramaturgische Funktion, etwa _Ankunft_, _Beobachtung_, _Kontakt_,
_Hindernis_ oder _Konflikt_. So bleibt das Pacing nachvollziehbar.
`DelayConflict(n)` setzt ein Mindestlimit, ab welcher Szenennummer ein größerer
Kampf stattfinden darf. Makroaufrufe werden intern ausgeführt und dürfen weder
als Rohtext noch in HTML-Kommentaren erscheinen. `NextScene()` ruft intern
`EndScene()` auf und startet anschließend `StartScene()`, damit der HUD-Header
zuverlässig erscheint. Verwandte Makros arbeiten ohne sichtbare Ausgabe.

<!-- Macro: hud_tag -->

⟨% macro hud_tag(msg) -%⟩
`⟪ msg ⟫`
⟨%- endmacro %⟩

⟨% macro star_bonus_overlay() -%⟩
⟨% set stars = getattr(campaign, 'stars_bonus', 0) | int %⟩
⟨% if stars %⟩
⟨% if not getattr(campaign, 'stars_overlay_done', False) %⟩
⟪ hud_tag('☆-Feedback: ' ~ '☆'\*stars ~ ' · SG +' ~ stars ~ ' aktiv') ⟫
⟨% set campaign.stars_overlay_done = true %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

<!-- Macro: hud_ping -->

⟨% macro hud_ping(msg) -%⟩
`<span style="color:#888">· ⟪ msg ⟫</span>`
⟨%- endmacro %⟩

⟨% macro suggest_actions(options, context=None, caution=None) -%⟩
⟨% set opts = [] %⟩
⟨% if options is string %⟩
⟨% set opts = [options] %⟩
⟨% elif options is iterable %⟩
⟨% set opts = options %⟩
⟨% endif %⟩
⟨% if context %⟩
⟪ hud_tag('Kontext: ' ~ context) ⟫
⟨% endif %⟩
⟨% if not state.ui.suggest_mode %⟩
⟪ hud_ping('Suggest-Modus ist aus - `modus suggest` aktiviert automatische Vorschläge.') ⟫
⟨% endif %⟩
⟨% if opts %⟩
⟨% for option in opts %⟩
⟨% if option %⟩
⟪ hud_tag('Vorschlag: ' ~ option) ⟫
⟨% endif %⟩
⟨% endfor %⟩
⟨% else %⟩
⟪ hud_ping('Keine Vorschläge hinterlegt.') ⟫
⟨% endif %⟩
⟨% if caution %⟩
⟪ hud_ping('Hinweis: ' ~ caution) ⟫
⟨% endif %⟩
⟪ hud_ping('Bitte bestätigt oder korrigiert den Vorschlag, bevor der Kodex fortfährt.') ⟫
⟨%- endmacro %⟩

⟨% macro offline_help(trigger='command') -%⟩
⟨% set scene_marker = (campaign.loc or 'HQ') ~ ':' ~ (campaign.scene or 0) %⟩
⟨% set last_scene = state.logs.flags.offline_help_last_scene %⟩
⟨% set same_scene = last_scene == scene_marker %⟩
⟨% set state.logs.flags.offline_help_last_scene = scene_marker %⟩
⟨% set count = state.logs.flags.offline_help_count + 1 %⟩
⟨% set state.logs.flags.offline_help_count = count %⟩
⟨% set state.logs.offline = state.logs.offline | default([]) %⟩
⟨% if state.logs.offline|length >= 12 %⟩
⟨% set state.logs.offline = state.logs.offline[1:] %⟩
⟨% endif %⟩
⟨% set offline_entry = {
'timestamp': '**AUTO**',
'reason': trigger,
'status': 'offline',
'device': state.comms.device | default(None),
'jammed': state.comms.jammed | default(False),
'range_m': state.comms.range_m | default(0),
'relays': state.comms.relays | default(0),
'scene_index': campaign.scene | default(0),
'scene_total': campaign.scene_total | default(12),
'episode': campaign.episode | default(0),
'mission': campaign.mission | default(0),
'count': count
} %⟩
⟨% set state.logs.offline = state.logs.offline + [offline_entry] %⟩
⟨% if same_scene and trigger != 'init' %⟩
⟪ hud_ping('Offline-Protokoll läuft - Mission weiter, HUD lokal. ' ~
'Terminal koppeln oder Relais suchen. !offline wiederholt die Schritte.') ⟫
⟨% else %⟩
⟪ hud_tag('Kodex-Uplink getrennt - Mission läuft weiter mit HUD-Lokaldaten.') ⟫
⟪ hud_tag('Offline-Protokoll: Terminal koppeln, Hardline suchen, ' ~
'Jammer-Override prüfen; Kodex bleibt stumm bis zum Re-Sync.') ⟫
⟪ hud_tag('HQ bleibt online; Offline gilt nur im Einsatz. HQ-Saves nach Re-Sync.') ⟫
⟪ hud_tag('Ask→Suggest-Fallback: Aktionen als "Vorschlag:" markieren ' ~
'und Bestätigung abholen, bis der Link zurück ist.') ⟫
⟨% endif %⟩
⟨% set device = state.comms.device | default('unbekannt') %⟩
⟨% set jammed = state.comms.jammed | default(False) %⟩
⟨% set range_m = state.comms.range_m | default(0) %⟩
⟨% set relays = state.comms.relays | default(0) %⟩
⟨% set scene_idx = campaign.scene | default(0) %⟩
⟨% set scene_total = campaign.scene_total | default(12) %⟩
⟪ hud_tag('Offline-Protokoll (' ~ count ~ '×): Gerät ' ~ device ~ ' · Jammer ' ~
(jammed and 'aktiv' or 'frei') ~ ' · Reichweite ' ~ range_m ~ 'm · Relais ' ~ relays ~
' · Szene ' ~ scene_idx ~ '/' ~ scene_total) ⟫
⟨%- endmacro %⟩

⟨# PRECISION-Markierungsmakros #⟩
⟨% macro SceneHeader(kamera, target, pressure, env=None) -%⟩
⟨% if gm_style == 'precision' %⟩
Kamera: ⟪ kamera ⟫.
Target: ⟪ target ⟫.
Pressure: ⟪ pressure ⟫.
⟨% set campaign.precision_header_ok = true %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro Decision(text) -%⟩
⟨% if gm_style == 'precision' %⟩
Decision: ⟪ text ⟫?
⟨% set campaign.precision_decision_ok = true %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro kodex_hint_for_scene(loc) -%⟩
Kodex: ⟪ loc ⟫ - Lagecheck aktiv. Infiltrationspfad gemäß Mission-Fokus.
⟨%- endmacro %⟩

<!-- Macro: hud_vocab -->

⟨% macro hud_vocab(key) -%⟩
⟨% set pack = {
"signal_modified": "Δ-Flux!",
"pressure_drop": "Druck fällt - Kern verstummt.",
"line_noise": "Leitung rauscht wie kalter Regen.",
"power_restored": "Sicherung schnappt - Strom kehrt zurück.",
"unauthorized_signal": "Fremdsignal tastet das Netz ab.",
"lock_engaged": "Riegel schlägt zu - Rahmen erzittert.",
"lock_released": "Bolzen gleiten - Öffnung frei.",
"heartbeat_spike": "Puls springt - Adrenalin flutet.",
"system_stable": "System hält - Lage stabil.",
"data_corrupt": "Daten zersplittern - Blöcke unlesbar.",
"kodex_link_lost": "Kodex-Link weg - lokale Protokolle aktiv.",
"signal_jammed": "Signal bricht - Fremdfeld blockiert.",
"lens_damaged": "Linse schrammt - Sicht verwaschen.",
"ear_overload": "Pegel schießt hoch - Trommelfell zittert."
} %⟩
⟪ pack[key] ⟫
⟨%- endmacro %⟩

<!-- Macro: noir_soft -->

⟨% macro noir_soft(key) -%⟩
⟪ hud_tag(hud_vocab(key)) ⟫
⟨%- endmacro %⟩

<!-- Macro: vehicle_overlay -->

⟨% macro vehicle_overlay(env, speed='-', stress='-', dmg='-') -%⟩
⟨% if env == "vehicle" -%⟩
⟨# Runtime: hud_event('vehicle_clash', {tempo: speed, stress: stress, damage: dmg}) #⟩
⟪ hud_tag('Tempo: ' ~ speed ~ ' · Stress: ' ~ stress ~ ' · Schaden: ' ~ dmg) ⟫
⟨%- endif %⟩
⟨%- endmacro %⟩

<!-- Macro: mass_conflict_overlay -->

⟨% macro mass_conflict_overlay(chaos='-', break_sg='-', stress='-') -%⟩
⟨# Runtime: hud_event('mass_conflict', {chaos: chaos, break_sg: break_sg, stress: stress}) #⟩
⟪ hud_tag('Mass Conflict · Chaos: ' ~ chaos ~ ' · Break-SG: ' ~ break_sg ~ ' · Stress: ' ~ stress) ⟫
⟨%- endmacro %⟩

⟨% macro px_bar(px) -%⟩⟪ "█"_px ~ "░"_(5-px) ⟫⟨%- endmacro %⟩

⟨% macro px*tracker(temp) -%⟩
⟨% set px = campaign.px or 0 %⟩
⟨% set temp_val = temp or 0 %⟩
⟨% set eta = px_eta(temp_val) %⟩
⟪ hud_tag('Px ' ~ px_bar(px) ~ ' (' ~ px ~ '/5) · TEMP ' ~ temp_val ~ ' · +' ~ px_gain(temp_val) ~ ' Px/Mission · ETA +1 in ' ~ eta ~ ' Mission') ⟫
⟨%- endmacro %⟩
⟨% macro vehicle_cadence(temp) -%⟩
⟨%- if temp <= 2 -%⟩4⟨%- elif temp <= 5 -%⟩3⟨%- elif temp <= 8 -%⟩2⟨%- else -%⟩1⟨%- endif -%⟩
⟨%- endmacro %⟩
⟨% macro vehicle_window(temp, mission, vehicle_class='standard', source='') -%⟩
⟨# Debrief-Kontext: vehicle_context.* / vehicle.* / top-level (vehicle_class, vehicle_type, source) #⟩
⟨% set klass = vehicle_class|default('standard')|lower %⟩
⟨% set src = source|default('')|lower %⟩
⟨% if mission|default(1)|int > 0 and campaign.type|default('core')|lower == 'rift' and (klass in ['temporal_ship', 'tech_iv_temporal'] or src == 'chronopolis_legendary') %⟩
⟪ hud_tag('Fahrzeugfenster · Rift-Protokoll aktiv · Keine Chrononauten-Fahrzeuge im Rissfenster (inkl. Chronopolis/Tech IV) · Anreise nur via ITI-Riftverfahren.') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% if klass in ['temporal_ship', 'tech_iv_temporal'] or src == 'chronopolis_legendary' %⟩
⟪ hud_tag('Fahrzeugfenster · Ausnahme aktiv · Legendäres temporales Schiff (Chronopolis/Tech IV) nutzt den Zeitriss eigenständig · Fraktions-Asset im Zusatzslot (gemeinsam gepflegt/überwacht) · Standardfahrzeuge bleiben TEMP-gebunden (4/3/2/1).') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% set cadence = vehicle_cadence(temp) | int %⟩
⟨% set mission_safe = mission|default(1)|int %⟩
⟨% if mission_safe < 1 %⟩⟨% set mission_safe = 1 %⟩⟨% endif %⟩
⟨% set slot = ((mission_safe - 1) % cadence) + 1 %⟩
⟨% set ready = slot == cadence %⟩
⟨% set next_in = ready and 0 or (cadence - slot) %⟩
⟪ hud_tag('Fahrzeugfenster · TEMP ' ~ temp ~ ' · Rhythmus ' ~ cadence ~ ' · Slot ' ~ slot ~ '/' ~ cadence ~
' · ' ~ (ready and 'verfügbar' or ('wieder in ' ~ next_in ~ ' Missionen'))) ⟫
⟨%- endmacro %⟩
⟨% macro px_gain(temp) -%⟩
⟨%- if temp<=2 -%⟩0.5⟨%- elif temp<=5 -%⟩1⟨%- elif temp<=8 -%⟩2⟨%- elif temp<=11 -%⟩2⟨%- else -%⟩3⟨%- endif -%⟩
⟨%- endmacro %⟩
⟨% macro px_eta(temp) -%⟩
⟨%- if temp<=2 -%⟩2⟨%- else -%⟩1⟨%- endif -%⟩
⟨%- endmacro %⟩
⟨% macro assert_foreshadow(count_needed=2) -%⟩
⟨% if gm_style == 'precision' %⟩
⟨% set c = scene.foreshadows|length if scene.foreshadows is defined else 0 %⟩
⟨% if c < count_needed %⟩
⟪ hud_tag('Foreshadow low: ' ~ c ~ '/' ~ count_needed) ⟫
⟨% endif %⟩
⟨% endif %⟩
⟨%- endmacro %⟩
⟨% macro register_foreshadow(token) -%⟩
⟨% if scene.foreshadows is not defined %⟩⟨% set scene.foreshadows = [] %⟩⟨% endif %⟩
⟨% if token not in scene.foreshadows %⟩
⟨% do scene.foreshadows.append(token) %⟩
⟨% endif %⟩
⟨%- endmacro %⟩
⟨% macro ForeshadowHint(text, tag='Foreshadow') -%⟩
⟨% set cleaned = text|trim %⟩
⟨% set token = 'manual:' ~ cleaned|lower|replace(' ', '*') %⟩
⟪ register_foreshadow(token) ⟫
⟪ hud_tag(tag ~ ': ' ~ cleaned) ⟫
⟨%- endmacro %⟩

<!-- Macro: scene_overlay -->

⟨% macro ttl_fmt(mins=0, secs=0) -%⟩
⟨% set mm = "%02d"|format(mins|int) %⟩
⟨% set ss = "%02d"|format(secs|int) %⟩
⟪ mm ~ ':' ~ ss ⟫
⟨%- endmacro %⟩

⟨% macro open_exfil_window(ttl=None, anchor='?') -%⟩
⟨% if ttl is none %⟩⟨% set ttl = exfil.ttl_start_minutes %⟩⟨% endif %⟩
⟨% set campaign.exfil = {
'active': true,
'ttl': ttl,
'hot': false,
'sweeps': 0,
'stress': 0,
'anchor': anchor,
'armed': false
} %⟩
⟪ hud_tag('Exfil-Fenster aktiv · ANCR ' ~ anchor ~ ' · RW ' ~ ttl_fmt(campaign.exfil.ttl)) ⟫
⟨%- endmacro %⟩

⟨% macro trigger_hot_exfil() -%⟩
⟨% set campaign.exfil.hot = true %⟩
⟪ hud_tag('Objective: HOT-Exfil') ⟫
⟨%- endmacro %⟩

⟨% macro arm_return_window(loc) -%⟩
⟨% if not campaign.exfil.active %⟩⟪ hud_ping('Kein Exfil aktiv') ⟫
⟨% elif campaign.exfil.armed %⟩⟪ hud_ping('RW bereits armiert') ⟫
⟨% elif loc != campaign.exfil.anchor and loc != campaign.exfil.alt_anchor %⟩
⟪ hud_ping('Falscher Anchor') ⟫
⟨% else %⟩
⟨% set campaign.exfil.armed = true %⟩
⟪ hud_tag('Return Window armiert') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro set_alt_anchor(loc) -%⟩
⟨% if campaign.exfil.active %⟩⟨% set campaign.exfil.alt_anchor = loc %⟩⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro interruption_check(active) -%⟩
⟨% if active %⟩⟪ hud_tag('Interruption-Check') ⟫⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro exfil_complication() -%⟩
⟨% if campaign.exfil.active %⟩
⟨% set char.stress = (char.stress or 0) + exfil.stress_gain_on_complication %⟩
⟪ hud_ping('Stress +' ~ exfil.stress_gain_on_complication ~ ' (Komplikation)') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro scene_overlay(total, pressure=None, env=None) -%⟩
⟨% set ep = campaign.episode %⟩
⟨% set ms = campaign.mission_in_episode %⟩
⟨% set sc = campaign.scene %⟩
⟨% set TYPE = campaign.type|upper %⟩
⟨% set objective = campaign.objective %⟩
⟨% set mode_map = {
'label': {'core': 'MODE CORE', 'rift': 'MODE RIFT'},
'emoji': {'core': '🎯 CORE', 'rift': '✨ RIFT'},
'both': {'core': '🎯 MODE CORE', 'rift': '✨ MODE RIFT'}
} %⟩
⟨% set mode_token = mode_map.get(ui.mode_display or 'label')[campaign.type] %⟩
⟨% set segs = [
"EP " ~ (ep|format("%02d")),
" · MS " ~ (ms|format("%02d")),
" · SC " ~ (sc|format("%02d")) ~ "/" ~ total,
" · " ~ mode_token,
" · Objective: " ~ objective
] %⟩
⟨% if campaign.exfil.active %⟩
⟨% set campaign.exfil.ttl = [campaign.exfil.ttl, 0]|max %⟩
⟨% do segs.append(" · ANCR " ~ (campaign.exfil.anchor or '?') ~ " · RW " ~ ttl_fmt(campaign.exfil.ttl)) %⟩
⟨% if campaign.exfil.sweeps %⟩⟨% do segs.append(" · Sweeps:" ~ campaign.exfil.sweeps) %⟩⟨% endif %⟩
⟨% if campaign.exfil.stress %⟩⟨% do segs.append(" · Stress " ~ campaign.exfil.stress) %⟩⟨% endif %⟩
⟨% endif %⟩
⟨% set px = campaign.px or 0 %⟩
⟨% set sys_free = (char.sys_max or 0) - (char.sys or 0) %⟩
⟨% if char.psi_flag %⟩
⟨% do segs.append(" · PP " ~ char.pp ~ "/" ~ char.pp_max) %⟩
⟨% do segs.append(" · Psi-Heat " ~ (char.psi_heat or 0)) %⟩
⟨% do segs.append(" · SYS " ~ char.sys ~ "/" ~ char.sys_max ~ " (free " ~ sys_free ~ ")") %⟩
⟨% do segs.append(" · Stress " ~ (char.stress or 0)) %⟩
⟨% do segs.append(" · Px " ~ px_bar(px) ~ " (" ~ px ~ "/5)") %⟩
⟨% else %⟩
⟨% if char.ammo is defined %⟩
⟨% do segs.append(" · Ammo " ~ char.ammo) %⟩
⟨% elif char.charges is defined %⟩
⟨% do segs.append(" · Charges " ~ char.charges) %⟩
⟨% endif %⟩
⟨% if char.sys_max %⟩
⟨% do segs.append(" · SYS " ~ char.sys ~ "/" ~ char.sys_max ~ " (free " ~ sys_free ~ ")") %⟩
⟨% endif %⟩
⟨% do segs.append(" · Stress " ~ (char.stress or 0)) %⟩
⟨% do segs.append(" · Px " ~ px_bar(px) ~ " (" ~ px ~ "/5)") %⟩
⟨% endif %⟩
⟨% do segs.append(" · Lvl " ~ (char.lvl or '-')) %⟩
⟨% if campaign.scene == 1 and campaign.fr_intervention %⟩
⟨% do segs.append(" · FR:" ~ campaign.fr_intervention) %⟩
⟨% endif %⟩
⟪ hud_tag(segs|join('')) ⟫
⟨% if pressure %⟩⟪ hud_tag('Pressure: ' ~ pressure) ⟫⟨% endif %⟩
⟪ vehicle_overlay(env) ⟫
⟨%- endmacro %⟩

### StartScene & EndScene Macros ⟨#startscene--endscene-macros}

<!-- Macro: StartScene -->

⟨% macro StartScene(loc, objective=None, seed_id=None, pressure=None,
total=12, role="", env=None) -%⟩
⟨% call maintain_cooldowns() %⟩⟨% endcall %⟩
⟨% set campaign.tech_steps = 0 %⟩
⟨% set campaign.complication_done = false %⟩
⟨% if scene.foreshadows is not defined %⟩⟨% set scene.foreshadows = [] %⟩⟨% endif %⟩
⟨% if seed_id is not none %⟩⟨% set campaign.seed_id = seed_id %⟩⟨% endif %⟩
⟨% if objective is not none %⟩⟨% set campaign.objective = objective %⟩⟨% endif %⟩
⟨% if campaign.objective is defined and 'Optionaler Sweep' in campaign.objective
and '0-2 empfohlen' not in campaign.objective %⟩
⟨% set campaign.objective = campaign.objective ~ ' (0-2 empfohlen)' %⟩
⟨% endif %⟩
⟨% set campaign.sys_prev = char.sys %⟩
⟨% set campaign.pp_prev = char.pp %⟩
⟨% set campaign.psi_heat_prev = char.psi_heat %⟩
⟨% set campaign.psi_logged = false %⟩
⟨% set campaign.precision_header_ok = false %⟩
⟨% set campaign.precision_decision_ok = false %⟩
⟨% if loc == "HQ" %⟩
⟨% do char.cooldowns.clear() %⟩
⟨% set char.sys_used = char.sys %⟩
⟨% set char.stress = 0 %⟩ ⟨# Stress und Psi-Heat werden im HQ komplett abgebaut #⟩
⟨% set char.psi_heat = 0 %⟩
⟨% set campaign.psi_heat_prev = 0 %⟩
⟨% set total = "∞" %⟩
⟨% set campaign.scene_total = None %⟩
⟨% set campaign.exfil = {
'active': false,
'ttl': 0,
'hot': false,
'sweeps': 0,
'stress': 0,
'anchor': '?',
'armed': false
} %⟩
⟨% if campaign.scene == 1 %⟩
⟪ ShowComplianceOnce() ⟫
⟨% endif %⟩
⟨% else %⟩
⟨% if campaign.scene_total is none %⟩
⟨% set campaign.scene_total = total %⟩
⟨% endif %⟩
⟨% set total = campaign.scene_total %⟩
⟨% if campaign.exfil.active and not campaign.exfil.armed %⟩
⟨% if campaign.exfil.ttl <= 0 and exfil.hot_exfil_on_ttl_zero %⟩
⟪ trigger_hot_exfil() ⟫
⟨% else %⟩
⟨% set campaign.exfil.ttl = campaign.exfil.ttl - exfil.ttl_cost_per_sweep_min %⟩
⟨% set campaign.exfil.sweeps = (campaign.exfil.sweeps or 0) + 1 %⟩
⟨% set campaign.exfil.stress = (campaign.exfil.stress or 0) + exfil.stress_gain_per_sweep %⟩
⟨% set char.stress = (char.stress or 0) + exfil.stress_gain_per_sweep %⟩
⟪ hud_ping('Stress +' ~ exfil.stress_gain_per_sweep) ⟫
⟪ interruption_check(pressure) ⟫
⟨% if campaign.exfil.ttl <= 0 and exfil.hot_exfil_on_ttl_zero %⟩
⟪ trigger_hot_exfil() ⟫
⟨% endif %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨% if role == "Finale" and campaign.scene < 10 %⟩
⟪ hud_tag('Finale blockiert - erst ab Szene 10 erlaubt') ⟫
⟨% set role = "Konflikt" %⟩
⟨% endif %⟩
⟪ scene_overlay(total, pressure, env) ⟫
⟨% if loc != "HQ" %⟩
⟪ kodex_hint_for_scene(loc) ⟫
⟨% endif %⟩
⟨% set is_solo = ('solo' in (save.modes or [])) or (campaign.team_size|default(1) <= 1) %⟩
⟨% if is_solo and loc != "HQ" %⟩
Kodex: Solo-Assist aktiv - "Kodex, Details" liefert Zusatzlage in dieser Szene.
⟨% endif %⟩
⟨% set auto_hints = [] %⟩
⟨% if campaign.type == 'core' and campaign.scene == 4 %⟩
⟨% set auto_hints = [
('auto:core:4:a', 'Foreshadow: Kaltes Licht pulst über dem Signatur-Gadget des Bosses.'),
('auto:core:4:b', 'Foreshadow: Wartungsdrohne markiert einen verriegelten Notausgang mit Boss-Siegel.')
] %⟩
⟨% elif campaign.type == 'core' and campaign.scene == 9 %⟩
⟨% set auto_hints = [
('auto:core:9:a', 'Foreshadow: akustischer Click des Metronoms'),
('auto:core:9:b', 'Foreshadow: Glassteg mit Servicelift/Fluchtweg')
] %⟩
⟨% elif campaign.type == 'rift' and campaign.scene == 9 %⟩
⟨% set auto_hints = [
('auto:rift:9:a', 'Foreshadow: akustischer Click des Metronoms'),
('auto:rift:9:b', 'Foreshadow: Glassteg mit Servicelift/Fluchtweg')
] %⟩
⟨% endif %⟩
⟨% for hint in auto_hints %⟩
⟨% set token = hint[0] %⟩
⟨% set text = hint[1] %⟩
⟨% if token not in scene.foreshadows %⟩
⟪ register_foreshadow(token) ⟫
⟨% if text %⟩
⟪ hud_tag(text) ⟫
⟨% endif %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨# Boss-Regel #⟩
⟨% set is_boss_scene = (campaign.type == 'rift' and campaign.scene == 10) or
(campaign.type == 'core' and campaign.scene == 10 and campaign.boss_allowed) %⟩
⟨% if is_boss_scene %⟩
⟨% set trimmed_cooldowns = {} %⟩
⟨% for pressure_id, cd in campaign.boss_pressure_cooldowns.items() %⟩
⟨% if cd > 1 %⟩
⟨% set trimmed_cooldowns = trimmed_cooldowns | combine({pressure_id: cd - 1}) %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨% set campaign.boss_pressure_cooldowns = trimmed_cooldowns %⟩
⟨% set available_pressure = namespace(options=[]) %⟩
⟨% for option in boss_pressure_pool %⟩
⟨% set option_id = option | join('||') %⟩
⟨% if campaign.boss_pressure_cooldowns[option_id]|default(0) == 0 %⟩
⟨% set available_pressure.options = available_pressure.options + [option] %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨% set selectable_pressure = available_pressure.options %⟩
⟨% if selectable_pressure|length == 0 %⟩
⟨% set campaign.boss_pressure_cooldowns = {} %⟩
⟨% set selectable_pressure = boss_pressure_pool %⟩
⟨% endif %⟩
⟨% set pressure_choice = selectable_pressure|random %⟩
⟨% set pressure_id = pressure_choice | join('||') %⟩
⟨% set campaign.boss_pressure_cooldowns = campaign.boss_pressure_cooldowns | combine({
pressure_id: boss_pressure_cooldown_length
}) %⟩
⟨% set campaign.last_boss_pressure = pressure_choice %⟩
⟨% set campaign.boss_scene = {'style': 'VERBOSE','pressure': pressure_choice} %⟩
⟨% if campaign.type == 'rift' %⟩
⟪ generate_boss('rift', campaign.mission, campaign.epoch) ⟫
⟨# LINT:BOSS_SCENE10_RIFT #⟩
⟪ hud_tag('Boss-Encounter in Szene 10') ⟫
⟨% else %⟩
⟪ generate_boss('core', campaign.mission, campaign.epoch) ⟫
⟪ hud_tag('Boss-Encounter in Szene 10 (Core M' ~ campaign.mission_in_episode ~ ')') ⟫
⟨% endif %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

<!-- Macro: maintain_cooldowns (reduziert Cooldowns und entfernt abgelaufene Einträge) -->

⟨% macro maintain_cooldowns() -%⟩
⟨% for skill in char.cooldowns.keys() | list %⟩
⟨% set cd = char.cooldowns[skill] %⟩
⟨% if cd > 1 %⟩
⟨% do char.cooldowns.update({skill: cd - 1}) %⟩
⟨% else %⟩
⟨% do char.cooldowns.pop(skill) %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨%- endmacro %⟩

<!-- Macro: EndScene -->

⟨% macro EndScene() -%⟩
⟨% if gm*style == 'precision' and (not campaign.precision_header_ok or not campaign.precision_decision_ok) %⟩
⟪ hud_tag('PRECISION fehlend: Kamera/Target/Pressure/Decision') ⟫
⟨% endif %⟩
⟨% set campaign.scene = campaign.scene + 1 -%⟩
⟨% if (char.sys != campaign.sys_prev or char.pp != campaign.pp_prev or
char.psi_heat != campaign.psi_heat_prev) and not campaign.psi_logged %⟩
⟪ hud_tag('Psi-Check: nutze psi_activation()') ⟫
⟨% endif %⟩
⟨% set campaign.sys_prev = char.sys %⟩
⟨% set campaign.pp_prev = char.pp %⟩
⟨% set campaign.psi_heat_prev = char.psi_heat %⟩
⟨% set * = scene_budget_enforcer(campaign.scene_total) -%⟩
⟨%- endmacro %⟩

<!-- Macro: NextScene -->

⟨% macro NextScene(loc, objective=None, seed_id=None, pressure=None,
total=None, role="", env=None) -%⟩
⟨% if total is none %⟩⟨% set total = campaign.scene_total %⟩⟨% endif %⟩
⟨% set foreshadows = scene.foreshadows if scene.foreshadows is defined else [] %⟩
⟨% set next_scene = campaign.scene + 1 %⟩
⟨% set core_boss = campaign.type == 'core' and campaign.boss_allowed %⟩
⟨% set rift_boss = campaign.type == 'rift' %⟩
⟨% set gate_target = (core_boss or rift_boss) and next_scene == 10 %⟩
⟨% set required = 0 %⟩
⟨% if gate_target and core_boss %⟩
⟨% set required = 4 %⟩
⟨% elif gate_target and rift_boss %⟩
⟨% set required = 2 %⟩
⟨% endif %⟩
⟨% set have = foreshadows|length %⟩
⟨% set gate_active = gate_target and have < required %⟩
⟨% if gate_active %⟩
⟨% if not campaign.foreshadow_gate_warned %⟩
⟪ hud_tag('Gate blockiert - FS ' ~ have ~ '/' ~ required ~ ' (Gate 2/2 bleibt gesetzt)') ⟫
⟨% set campaign.foreshadow_gate_warned = true %⟩
⟨% endif %⟩
⟨% if campaign.type == 'core' %⟩
⟪ hud_tag('Fehlende Hinweise: Szene 4 und Szene 9 liefern je zwei Foreshadows vor Szene 10.') ⟫
⟨% else %⟩
⟪ hud_tag('Fehlende Hinweise: Szene 9 muss zwei Foreshadows setzen, bevor Szene 10 öffnet.') ⟫
⟨% endif %⟩
⟪ assert_foreshadow(required) ⟫
⟪ hud_tag('Gate aktiv - Szene ' ~ campaign.scene|format("%02d") ~ ' bleibt offen, FS fehlen.') ⟫
⟨% else %⟩
⟨% set campaign.foreshadow_gate_warned = false %⟩
⟨# Konflikte in Szene < delayConflict blocken #⟩
⟨% if campaign.scene < campaign.delayConflict
and role in ["Konflikt","Finale"]
and (role not in campaign.delayConflict_allow) %⟩
⟪ hud_tag('Konflikt zu früh - DelayConflict(' ~ campaign.delayConflict ~ ') aktiv.') ⟫
⟨% set role = "Beobachtung" %⟩
⟨% endif %⟩
⟨% if role == "Finale" and campaign.scene < 10 %⟩
⟪ hud_tag('Finale blockiert - erst ab Szene 10 erlaubt') ⟫
⟨% set role = "Konflikt" %⟩
⟨% endif %⟩
⟪ EndScene() ⟫
⟪ StartScene(loc, objective, seed_id, pressure=pressure,
total=total, role=role, env=env) ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

### Self-Collision Guard & Comms Checks

⟨% macro redirect_same_slot(epoch, dt_hours) -%⟩
⟨% if campaign.last_epoch == epoch and dt_hours|abs < 6 %⟩
⟨% set campaign.start_offset = 6 %⟩
⟪ hud_tag('Redirect: Start +6h (Self-Collision Guard)') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

#### comms_check ⟨#comms-check}

Validiert Funkhardware und Reichweite. Erwartet `device`
(`comlink|cable|relay|jammer_override`, Groß-/Kleinschreibung egal) und eine
Reichweite in **Metern** (`range_m`). Optional akzeptiert der Guard ein
Kilometerfeld (`range_km`) sowie Flags für Jammer- oder Relay-Unterstützung.
`must_comms()` ruft `comms_check()` auf, normalisiert Groß-/Kleinschreibung sowie
km→m und löst bei Fehlern den Offline-Hinweis aus.

⟨% macro comms_check(device, range_m=0, range_km=None, jammer=false, relays=false) -%⟩
⟨% set raw = (device or '')|trim %⟩
⟨% set dev = raw|lower %⟩
⟨% if dev == 'commlink' %⟩⟨% set dev = 'comlink' %⟩⟨% endif %⟩
⟨% if dev in ['jammeroverride','jammer-override'] %⟩⟨% set dev = 'jammer_override' %⟩⟨% endif %⟩
⟨% set meters = range_m|float %⟩
⟨% if (meters <= 0) and (range_km is not none) %⟩
⟨% set meters = (range_km|float) \* 1000 %⟩
⟨% endif %⟩
⟨% set ok_device = dev in ['comlink','cable','relay','jammer_override'] %⟩
⟨% set ok_range = meters > 0 %⟩
⟨% set jam_blocked = jammer and dev not in ['cable','relay','jammer_override'] and not relays %⟩
⟪ ok_device and ok_range and (not jam_blocked) ⟫
⟨%- endmacro %⟩

⟨% macro must_comms(o) -%⟩
⟪ validate_signal((o.device or '') ~ ' ' ~ (o.text or '')) ⟫
⟨% set ok = comms_check(
o.device,
o.range_m|default(0),
o.range_km if o.range_km is defined else none,
o.jammer|default(false),
o.relays|default(false)
) %⟩
⟨% if not ok %⟩
⟪ offline_help('auto') ⟫
⟪ raise('CommsCheck failed: require valid device/range or relay/jammer override. ' ~
'Tipp: benannte Schnittstelle (Port/Buchse/Konsole/Relais) lokalisieren, ' ~
'Terminal suchen / Comlink koppeln / Kabel/Relais nutzen / ' ~
'Jammer-Override aktivieren; Reichweite anpassen. ' ~
'!offline zeigt das Feldprotokoll für den laufenden Einsatz.') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro radio_tx(msg, device='comlink', range_m=0, range_km=None, jammer=false, relays=false) -%⟩
⟪ must_comms({'device':device,'range_m':range_m,'range_km':range_km,'jammer':jammer,'relays':relays,'text':msg}) ⟫
⟪ hud_tag(msg) ⟫
⟨%- endmacro %⟩

⟨% macro radio_rx(msg, device='comlink', range_m=0, range_km=None, jammer=false, relays=false) -%⟩
⟪ must_comms({'device':device,'range_m':range_m,'range_km':range_km,'jammer':jammer,'relays':relays,'text':msg}) ⟫
⟪ hud_tag(msg) ⟫
⟨%- endmacro %⟩

⟨% macro validate_signal(text) -%⟩
⟨% set forbidden = ['Cyberspace','Signalraum','Netzgeist','reiner Signalfluss'] %⟩
⟨% set devices = ['Comlink','Jammer','Terminal','Konsole','Kabel','Antenne','Funkgerät','Relais'] %⟩
⟨% if forbidden|select('in', text)|list and not devices|select('in', text)|list %⟩
⟪
hud_tag(
'Signalaktion blockiert - Gerät + benannte Schnittstelle ' ~
'(Port/Buchse/Konsole/Relais) angeben.'
)
⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro set_mode(arg) -%⟩
⟨% set new_mode = 'precision' if arg == 'precision' else 'verbose' %⟩
⟨% set state.gm_style = new_mode %⟩
⟨% set gm_style = new_mode %⟩
⟪ hud_tag('GM_STYLE → ' ~ new_mode ~ ' (persistiert)') ⟫
⟨%- endmacro %⟩

⟨% macro toggle_suggest(enable=true) -%⟩
⟨% set state.ui.suggest_mode = enable | bool %⟩
⟨% if state.ui.suggest_mode %⟩
⟪ hud_tag('Suggest-Modus aktiv - Kodex liefert auf Anfrage kurze Vorschläge.') ⟫
⟨% else %⟩
⟪ hud_tag('Ask-Modus aktiv - Kodex reagiert nur auf direkte Fragen.') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro set_action_mode(arg) -%⟩
⟨% set raw = arg | string | lower | trim %⟩
⟨% if raw in ['frei', 'free', 'full', 'open', 'uncut', 'gewalt'] %⟩
⟨% set mode = 'frei' %⟩
⟨% else %⟩
⟨% set mode = 'konform' %⟩
⟨% endif %⟩
⟨% set state.ui.action_mode = mode %⟩
⟪ hud_tag('Action-Contract → ' ~ mode|upper ~ ' (persistiert)') ⟫
⟨%- endmacro %⟩

⟨% macro helper_delay() -%⟩
DelayConflict(th=4, allow=[]): Konflikte ab Szene th. Setze allow='ambush|vehicle_chase' für Ausnahmen.
⟨%- endmacro %⟩
⟨% macro helper_comms() -%⟩
comms_check(device,range_m,range_km?): Pflicht vor radio_tx/rx.
Akzeptiert `comlink|cable|relay|jammer_override` (Groß-/Kleinschreibung egal)
und Meterwerte; optional wandelt der Guard Kilometer in Meter um.
Tipp: Terminal suchen / Comlink koppeln / Kabel/Relais nutzen / Jammer-Override aktivieren;
Reichweite anpassen. `!offline` zeigt das Feldprotokoll, während die Mission mit HUD-Lokaldaten weiterläuft.
⟨%- endmacro %⟩
⟨% macro helper_boss() -%⟩
Boss-Foreshadow: Core - Szene 4/9 je zwei Hinweise, Rift - Szene 9 zwei Hinweise.
Gate 2/2 ist ab Missionsstart gesetzt; Szene 10 öffnet nur bei erfülltem Zähler
(FS 4/4 Core, FS 2/2 Rift). Foreshadow-Hinweise erhöhen nur das FS-Badge.
HUD-Badges: `GATE 2/2 · FS x/y` (Foreshadow-Log spiegelt `scene.foreshadows`).
Boss-Trace hält DR + Teamgröße (1-5, geklemmt) fest, DR skaliert nach Boss-Typ.
⟨%- endmacro %⟩
⟨% macro fr_help() -%⟩
FR: ruhig/beobachter/aktiv - wirkt auf Eingriffe in Szene 1.
⟨%- endmacro %⟩
⟨% macro foreshadow_requirement() -%⟩
⟨% set mission_type = (campaign.type or state.phase or '')|lower %⟩
⟨% if mission_type in ['rift'] %⟩
2
⟨% elif mission_type in ['core','preserve','story'] %⟩
⟨% if campaign.boss_allowed is defined and campaign.boss_allowed is not none and campaign.boss_allowed == false %⟩
0
⟨% else %⟩
4
⟨% endif %⟩
⟨% else %⟩
0
⟨% endif %⟩
⟨%- endmacro %⟩
⟨% macro boss_status() -%⟩
⟨% set entries = [] %⟩
⟨% if state.logs is defined and state.logs.foreshadow is defined and state.logs.foreshadow %⟩
⟨% set entries = state.logs.foreshadow %⟩
⟨% endif %⟩
⟨% set count = entries|length %⟩
⟨% set required = foreshadow_requirement() %⟩
Foreshadow ⟪ count ⟫⟨% if required > 0 %⟩/⟪ required ⟫⟨% endif %⟩
⟨%- endmacro %⟩
⟨% macro resolve_temp_for_px() -%⟩
⟨% if game_mode == 'gruppe' and party is defined and party.characters is defined and party.characters %⟩
⟨% set ns = namespace(total=0, count=0) %⟩
⟨% for member in party.characters %⟩
⟨% set member_temp = member.attributes.TEMP|default(member.temp|default(0, true), true) %⟩
⟨% set ns.total = ns.total + member_temp %⟩
⟨% set ns.count = ns.count + 1 %⟩
⟨% endfor %⟩
⟨% if ns.count > 0 %⟩
⟪ ((ns.total + ns.count - 1) // ns.count) ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨% if game_mode == 'gruppe' and campaign.team is defined and campaign.team.members is defined and campaign.team.members %⟩
⟨% set ns = namespace(total=0, count=0) %⟩
⟨% for member in campaign.team.members %⟩
⟨% set member_temp = member.attributes.TEMP|default(member.temp|default(0, true), true) %⟩
⟨% set ns.total = ns.total + member_temp %⟩
⟨% set ns.count = ns.count + 1 %⟩
⟨% endfor %⟩
⟨% if ns.count > 0 %⟩
⟪ ((ns.total + ns.count - 1) // ns.count) ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨% if state.temp is defined and state.temp is not none %⟩
⟪ state.temp ⟫
⟨% elif campaign.temp is defined and campaign.temp is not none %⟩
⟪ campaign.temp ⟫
⟨% else %⟩
⟪ 0 ⟫
⟨% endif %⟩
⟨%- endmacro %⟩
⟨% macro show_px() -%⟩
⟨% set temp_src = resolve_temp_for_px() %⟩
⟪ px_tracker(temp_src) ⟫
⟨%- endmacro %⟩
⟨% macro render_shop_tiers(level, faction_rep, rift_blueprints) -%⟩
⟨% set t1 = level|default(1) >= 1 %⟩
⟨% set t2 = level|default(1) >= 6 %⟩
⟨% set bp = rift_blueprints|default([])|length %⟩
⟨% set has_bp = bp > 0 %⟩
⟨% set t3 = (level|default(1) >= 11) and (faction_rep|default(0) >= 3) and has_bp %⟩
⟪ hud_tag('Shop-Tiers: T1:' ~ (t1 and 'true' or 'false') ~
' T2:' ~ (t2 and 'true' or 'false') ~
' T3:' ~ (t3 and 'true' or 'false') ~
' · BP:' ~ bp) ⟫
⟨%- endmacro %⟩
⟨% macro gear_shop() -%⟩
⟪ render_shop_tiers(state.level, state.faction_rep, state.rift_blueprints) ⟫
⟨%- endmacro %⟩
⟨% macro debrief() -%⟩
⟪ render_rewards() ⟫
⟨% set temp_src = resolve_temp_for_px() %⟩
⟪ px_tracker(temp_src) ⟫
⟨%- endmacro %⟩
⟨% macro on_command(cmd) -%⟩
⟨% set cmd_norm = cmd|lower %⟩
⟨% if cmd == '!helper delay' %⟩
⟪ helper_delay() ⟫
⟨% elif cmd == '!helper comms' %⟩
⟪ helper_comms() ⟫
⟨% elif cmd == '!helper boss' %⟩
⟪ helper_boss() ⟫
⟨% elif cmd == '!px' %⟩
⟪ show_px() ⟫
⟨% elif cmd == '!gear shop' %⟩
⟪ gear_shop() ⟫
⟨% elif cmd == '!fr help' %⟩
⟪ fr_help() ⟫
⟨% elif cmd == '!boss status' %⟩
⟪ boss_status() ⟫
⟨% elif cmd_norm in ['modus action', 'modus gewalt'] %⟩
⟪ hud_tag('Action-Contract → ' ~ state.ui.action_mode|upper ~ ' (persistiert)') ⟫
⟨% elif cmd_norm.startswith('modus action ') %⟩
⟪ set_action_mode(cmd_norm|replace('modus action', '')|trim) ⟫
⟨% elif cmd_norm.startswith('modus gewalt ') %⟩
⟪ set_action_mode(cmd_norm|replace('modus gewalt', '')|trim) ⟫
⟨% elif cmd == 'modus precision' %⟩
⟪ set_mode('precision') ⟫
⟨% elif cmd == 'modus verbose' %⟩
⟪ set_mode('verbose') ⟫
⟨% elif cmd == 'modus suggest' %⟩
⟪ toggle_suggest(true) ⟫
⟨% elif cmd == 'modus ask' %⟩
⟪ toggle_suggest(false) ⟫
⟨% elif cmd_norm in ['!offline','!help offline','/help offline','offline hilfe'] %⟩
⟪ offline_help('command') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro render_psi_option(name, cost_stress) -%⟩
⟨% if char.flags.has_psi %⟩
Psi: ⟪ name ⟫ (Kosten: Stress +⟪ cost_stress ⟫)
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:CHRONO_KEY_GATE #⟩
⟨% macro chrono_has_key() -%⟩
⟪ 'true' if (char.flags.chronokey or 'Chronopolis-Schlüssel' in (char.inv or [])) else 'false' ⟫
⟨%- endmacro %⟩

**HQ-Definition:** Zum HQ zählen ITI-Nullzeit, die ITI-Decks und der Pre-City-Hub.
Chronopolis selbst ist `CITY` und zählt **nicht** als HQ (kein Save, kein
HQ-Overlay).

⟨% macro chrono_grant_key_if_lvl10() -%⟩
⟨% if (char.lvl or 1) >= 10 and not char.flags.chronokey %⟩
⟨% set char.flags.chronokey = true %⟩
⟪ hud_tag('Kodex: Chronopolis-Zugang freigeschaltet (Schlüssel erteilt)') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro chrono_warn_once() -%⟩
⟨% if not state.logs.flags.chronopolis_warn_seen %⟩
⟪ hud_tag('Chronopolis folgt Einsatzregeln: Tod ist endgültig. ' ~
'Vor Schleuseneintritt jetzt HQ-DeepSave anbieten.') ⟫
⟨% set state.logs.flags.chronopolis_warn_seen = true %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:CHRONO_MODULE #⟩
⟨% macro start_chronopolis(district="Agora", ep=None) -%⟩
⟨% if arena and arena.active %⟩
⟪ hud_tag('Chronopolis blockiert - Arena aktiv') ⟫⟨% return %⟩
⟨% endif %⟩
⟨% if chrono_has_key() != 'true' %⟩
⟪ hud_tag('Zugang verweigert - Chronopolis-Schlüssel ab Level 10 erforderlich') ⟫⟨% return %⟩
⟨% endif %⟩
⟪ chrono_warn_once() ⟫
⟪ hud_tag('Vor Chronopolis: HQ-DeepSave bestätigen oder bewusst ohne Save fortfahren') ⟫
⟨% set campaign.loc = 'CITY' %⟩
⟨% set chrono = {
'active': true, 'district': district, 'epoch': ep,
'price_mod': 1.0, 'black_mod': 1.3, 'phase': 'INIT'
} %⟩
⟪ chrono_guards_enable() ⟫
⟪ chrono_hud('INIT') ⟫
⟨%- endmacro %⟩

⟨# LINT:CHRONO_KEY_HQ_HOOK #⟩
⟨% macro hq_entry_hook() -%⟩
⟪ chrono_grant_key_if_lvl10() ⟫
⟨%- endmacro %⟩

⟨% macro exit_chronopolis() -%⟩
⟨% if chrono and chrono.active %⟩
⟨% set chrono.active = false %⟩
⟪ hud_tag('Chronopolis verlassen') ⟫
⟪ chrono_guards_disable() ⟫
⟨% set campaign.loc = 'HQ' %⟩
⟪ hq_entry_hook() ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:CHRONO_ABORT #⟩
⟨% macro chrono_abort() -%⟩
⟨% if chrono and chrono.active %⟩
⟪ hud_tag('Chronopolis abgebrochen - zurück ins ITI-HQ') ⟫
⟨% set chrono.active = false %⟩
⟪ chrono_guards_disable() ⟫
⟨% set campaign.loc = 'HQ' %⟩
⟪ hq_entry_hook() ⟫
⟨% else %⟩
⟪ hud_tag('Chronopolis nicht aktiv - keine Aktion') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:CHRONO_RESUME_GUARD #⟩
⟨% macro chrono_resume_guard() -%⟩
⟨% if campaign.loc == 'CITY' and not (chrono and chrono.active) %⟩
⟪ hud_tag('Session-Resume: CITY ohne aktives Chronopolis - Rückkehr ins HQ') ⟫
⟨% set campaign.loc = 'HQ' %⟩
⟪ hq_entry_hook() ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟪ chrono_resume_guard() ⟫

⟨# LINT:CHRONO_GUARDS #⟩
⟨% macro chrono_guards_enable() -%⟩
⟨# HQ-kritische Systeme aus: Seeds/Paradoxon/Boss/FR #⟩
⟨# LINT:CHRONO_NO_SEEDS #⟩⟨% set campaign.seeds_suppressed = true %⟩
⟨# LINT:CHRONO_NO_PARADOXON #⟩⟨% set campaign.px_frozen = true %⟩
⟨# LINT:CHRONO_NO_BOSS #⟩⟨% set campaign.boss_suppressed = true %⟩
⟨# LINT:CHRONO_NO_FR #⟩⟨% set campaign.intervention_suppressed = true %⟩
⟨%- endmacro %⟩

⟨% macro chrono_guards_disable() -%⟩
⟨% set campaign.seeds_suppressed = false %⟩
⟨% set campaign.px_frozen = false %⟩
⟨% set campaign.boss_suppressed = false %⟩
⟨% set campaign.intervention_suppressed = false %⟩
⟨%- endmacro %⟩

⟨# LINT:HQ_ADMIT_GUARD #⟩
⟨% macro hq_admit(entity) -%⟩
⟨% if not entity.is_agent and not entity.guest_custody %⟩
⟪ hud_tag('HQ-Zutritt verweigert - nur ITI-Agenten / Gäste in Gewahrsam') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:FR_AT_HQ_ONLY #⟩
⟨% macro fr_contact(channel, subject) -%⟩
⟨% if campaign.loc != 'HQ' %⟩
⟪ hud_tag('FR-Kontakt nur im ITI-HQ erlaubt') ⟫⟨% return %⟩
⟨% endif %⟩
⟪ hud_tag('FR-Kanal ' ~ channel ~ ' · Thema: ' ~ subject) ⟫
⟨%- endmacro %⟩

⟨# LINT:CHRONO_RIFT_GATE #⟩
⟨% macro chrono_can_launch_rift() -%⟩
⟪ 'true' if (campaign.loc=='HQ' and campaign.episode_completed) else 'false' ⟫
⟨%- endmacro %⟩

⟨% macro chrono_launch_rift(seed_id) -%⟩
⟨% if chrono_can_launch_rift() != 'true' %⟩
⟪ hud_tag('Rift-Start blockiert - erst im HQ nach Episodenende') ⟫⟨% return %⟩
⟨% endif %⟩
⟨% set ep_use = (chrono and chrono.epoch) or campaign.epoch %⟩
⟪ hud_tag('Rift-Koordinate aktiviert: ' ~ seed_id) ⟫
⟪ StartMission(total=14, type='rift', seed_id=seed_id, epoch=ep_use, objective='Resolve Rift') ⟫
⟨%- endmacro %⟩

⟨# LINT:CHRONO_SERVICES #⟩
⟨% macro chrono_hud(phase="") -%⟩
⟨% set segs = [
"CHRONOPOLIS·", chrono.district,
" · EPOCHE ", (chrono.epoch or "-"),
" · PRC×", chrono.price_mod,
" · BLK×", chrono.black_mod
] %⟩
⟨% if phase %⟩⟨% set segs = segs + [" · PHASE:", phase] %⟩⟨% endif %⟩
`⟪ segs|join('') ⟫`
⟨%- endmacro %⟩

⟨% macro chrono_set_price_mod(base=1.0, black=1.3) -%⟩
⟨% set chrono.price_mod = base %⟩⟨% set chrono.black_mod = black %⟩
⟪ chrono_hud('ECON') ⟫
⟨%- endmacro %⟩

⟨% macro rank_index(rank) -%⟩
⟨% if rank not in ranks.order %⟩
⟪ raise('Unbekannter Rank: ' ~ rank) ⟫
⟨% endif %⟩
⟨% for r in ranks.order %⟩
⟨% if r == rank %⟩⟪ loop.index0 ⟫⟨% endif %⟩
⟨% endfor %⟩
⟨%- endmacro %⟩

⟨% macro validate_catalog_ranks() -%⟩
⟨% for it in catalog.items %⟩
⟨% set mr = getattr(it, 'min_rank', None) %⟩
⟨% if mr and mr not in ranks.order %⟩
⟪ raise('Item ' ~ it.id ~ ' verweist auf unbekannten Rank ' ~ mr) ⟫
⟨% endif %⟩
⟨% endfor %⟩
⟨%- endmacro %⟩

⟨% macro validate_char_rank(char) -%⟩
⟪ rank_index(char.rank) ⟫
⟨%- endmacro %⟩

⟨% macro boot_validate_ranks(roster) -%⟩
⟪ validate_catalog_ranks() ⟫
⟨% for c in roster %⟩
⟪ validate_char_rank(c) ⟫
⟨% endfor %⟩
⟨%- endmacro %⟩

⟨% macro can_purchase(char_rank, item) -%⟩
⟨% set mr = getattr(item, 'min_rank', None) %⟩
⟪ 'true' if not mr or rank_index(char_rank) >= rank_index(mr) else 'false' ⟫
⟨%- endmacro %⟩

⟨% macro list_shop_items(char) -%⟩
⟨% for it in catalog.items %⟩
⟨% if can_purchase(char.rank, it) == 'true' %⟩
⟪ hud_tag(it.name ~ ' · ' ~ it.price ~ ' CU') ⟫
⟨% else %⟩
⟪ hud_tag('🔒 ' ~ it.name ~ ' · ' ~ it.price ~ ' CU (erfordert Rank: ' ~ it.min_rank ~ ')') ⟫
⟨% endif %⟩
⟨% endfor %⟩
⟨%- endmacro %⟩

⟨% macro deny_purchase(item) -%⟩
⟪ hud_tag('Kauf gesperrt: ' ~ item.name ~ ' erfordert Rank ' ~ item.min_rank ~ '.') ⟫
⟪ hud_tag('SFX: ui/deny') ⟫
⟨%- endmacro %⟩

⟨% macro shop_buy(char, item_id) -%⟩
⟨% set it = catalog.get(item_id) %⟩
⟨% if not it %⟩
⟪ hud_tag('Unbekannter Artikel.') ⟫
⟨% elif can_purchase(char.rank, it) == 'false' %⟩
⟪ deny_purchase(it) ⟫
⟨% else %⟩
⟪ hud_tag('Gekauft: ' ~ it.name ~ ' (' ~ it.price ~ ' CU)') ⟫
⟪ inventory_add(char, it) ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro chrono_shop(listing, required_rank=None, required_research=None) -%⟩
⟨% set locks = [] %⟩
⟨% if required_rank and not can_purchase(char.rank, {'min_rank': required_rank}) == 'true' %⟩
⟨% do locks.append('Rank: ' ~ required_rank) %⟩
⟨% endif %⟩
⟨% if required_research is not none and campaign.research_level < required_research %⟩
⟨% do locks.append('Research: ' ~ required_research) %⟩
⟨% endif %⟩
⟨% if locks %⟩
⟪ hud_tag('🔒 ' ~ listing ~ ' (' ~ locks|join(' · ') ~ ')') ⟫
⟨% else %⟩
⟪ hud_tag('Shop: ' ~ listing ~ ' · Preise ×' ~ chrono.price_mod) ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro chrono_black_market(listing) -%⟩
⟪ hud_tag('Black Market: ' ~ listing ~ ' · Preise ×' ~ (chrono.black_mod or 1.3)) ⟫
⟨%- endmacro %⟩

⟨% macro chrono_clinic(service, cost_cu) -%⟩
⟪ hud_tag('Clinic: ' ~ service ~ ' · Kosten ' ~ cost_cu ~ ' CU') ⟫
⟨%- endmacro %⟩

⟨% macro chrono_workshop(action, cost_cu=0) -%⟩
⟪ hud_tag('Workshop: ' ~ action ~ (cost_cu and ' · Kosten ' ~ cost_cu ~ ' CU' or '')) ⟫
⟨%- endmacro %⟩

⟨% macro chrono_board(mode="preserve") -%⟩
⟨% set info = (mode=='trigger' and 'kleineres Übel sichern' or 'Kontinuität wahren') %⟩
⟪ hud_tag('Briefing-Board: Modus ' ~ mode ~ ' · ' ~ info) ⟫
⟨%- endmacro %⟩

⟨% macro chrono_training_open() -%⟩
⟪ hud_tag('Training: PvP-Arena verfügbar') ⟫
⟨%- endmacro %⟩

⟨# LINT:CHRONO_SIGNAL_GUARD #⟩
⟨% macro chrono_terminal(action, device="Terminal", target="") -%⟩
⟨% if device not in ['Terminal','Kabel','Konsole','Comlink'] %⟩
⟪ hud_tag('Aktion blockiert - Gerät angeben (Terminal/Kabel/Konsole/Comlink)') ⟫⟨% return %⟩
⟨% endif %⟩
⟨% if not target %⟩
⟪ hud_tag('Aktion blockiert - Schnittstelle benennen (Port/Buchse/Relais/Konsole)') ⟫⟨% return %⟩
⟨% endif %⟩
⟪ hud_tag('Terminal: ' ~ action ~ ' @ ' ~ target ~ ' (Signalraum aus)') ⟫
⟨%- endmacro %⟩

### kodex_summary() Macro

Fasst Missionsabschlussdaten zusammen und gibt sie im HUD aus.

<!-- Macro: kodex_summary -->

⟨% macro kodex_summary(closed_seed_ids=[], cluster_gain=0, faction_delta=0) -%⟩
⟪ hud_tag('Kodex: Seeds ' ~ closed_seed_ids ~ ' geschlossen') ⟫
⟪ hud_tag('Cluster +' ~ cluster_gain ~ ' · Fraktion +' ~ faction_delta) ⟫
⟨% if campaign.kodex_log %⟩⟪ hud_tag('Kodex-Log: ' ~ campaign.kodex_log) ⟫⟨% endif %⟩
⟨% set campaign.kodex_log = {} %⟩
⟪ hud_tag('Resonanz +1') ⟫
⟨%- endmacro %⟩

### EndMission Macro

Schließt eine Mission ab, setzt Levelaufstieg und protokolliert Abschlussdaten.

<!-- Macro: EndMission -->

⟨% macro EndMission(closed_seed_ids=[], cluster_gain=0, faction_delta=0, intervention_result=None) -%⟩
⟨% set hot = (campaign.exfil.active and campaign.exfil.ttl <= 0) or campaign.exfil.hot %⟩
⟨% set tcfg = get_transfer_cfg() %⟩
⟨% if should_show_transfer_exit(tcfg) %⟩
⟪ transfer_back_to_hq(campaign, tcfg, hot=hot) ⟫
⟨% endif %⟩
⟨% set campaign.loc = 'HQ' %⟩
⟨% set campaign.exfil = {
'active': false,
'ttl': 0,
'hot': false,
'sweeps': 0,
'stress': 0,
'anchor': '?',
'armed': false
} %⟩
⟨% if char.lvl < 10 %⟩
⟪ hud_tag('Level-Up: Wähle +1 Attribut, Talent/Upgrade oder +1 SYS') ⟫
⟨% endif %⟩
⟪ chrono_grant_key_if_lvl10() ⟫
⟪ kodex_summary(closed_seed_ids, cluster_gain, faction_delta) ⟫
⟨% set temp_src = resolve_temp_for_px() %⟩
⟪ px_tracker(temp_src) ⟫
⟨% if intervention_result %⟩⟪ log_intervention(intervention_result) ⟫⟨% endif %⟩
⟨% if campaign.fr_observer_note %⟩⟪ log_intervention('FR-Echo: SG +1 auf einen Check') ⟫⟨% endif %⟩
⟨% if campaign.mission_in_episode == 10 %⟩
⟨% set campaign.episode_completed = true %⟩
⟪ apply_rift_mods_next_episode() ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro dice_for(attr_val) -%⟩
⟪ 'W10*' if attr_val >= 11 else 'W6*' ⟫
⟨%- endmacro %⟩

⟨% macro attribute*budget_status(target=None) -%⟩
⟨% set char_ref = target if target is not none else char %⟩
⟨% if not char_ref %⟩⟨% return %⟩⟨% endif %⟩
⟨% set budget = 18 %⟩
⟨% if char_ref.attr_budget is defined and char_ref.attr_budget is not none %⟩
⟨% set budget = char_ref.attr_budget %⟩
⟨% endif %⟩
⟨% set attrs = char_ref.attributes | default({}, true) %⟩
⟨% set tally = namespace(total=0) %⟩
⟨% set low_attrs = [] %⟩
⟨% for *, val in attrs.items() %⟩
⟨% set tally.total = tally.total + (val or 0) %⟩
⟨% if (val or 0) < 1 %⟩
⟨% do low*attrs.append(* ~ ' ' ~ (val or 0)) %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨% set delta = budget - tally.total %⟩
⟨% if delta > 0 %⟩
⟪ hud_tag('Attributbudget: ' ~ tally.total ~ '/' ~ budget ~ ' · ' ~ delta ~ ' Punkt(e) verfügbar') ⟫
⟨% elif delta < 0 %⟩
⟪ hud_tag('Attributbudget überzogen: ' ~ tally.total ~ '/' ~ budget ~ ' · Bitte ' ~
(-delta) ~ ' Punkt(e) zurücknehmen.') ⟫
⟨% else %⟩
⟪ hud_tag('Attributbudget ausgeglichen: ' ~ tally.total ~ '/' ~ budget ~ ' · Keine Restpunkte') ⟫
⟨% endif %⟩
⟨% if low_attrs %⟩
⟪ hud_tag('Mindestwert prüfen: ' ~ low_attrs|join(', ') ~ ' → Werte auf mindestens 1 anheben') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro on_attribute_change(attr, value) -%⟩
⟨% if value == 11 %⟩
⟪ hud_tag(attr ~ ' 11 → Würfelwechsel: W10 explodierend aktiviert') ⟫
⟨% endif %⟩
⟪ attribute_budget_status() ⟫
⟨%- endmacro %⟩

⟨% macro dice_mode_map(char) -%⟩
⟨% set dm = {} %⟩
⟨% for k, v in char.attributes.items() %⟩
⟨% do dm.update({k: dice_for(v)}) %⟩
⟨% endfor %⟩
⟪ dm ⟫
⟨%- endmacro %⟩

⟨% macro render_roll_overlay(die_text, sg, total, success, parts=[]) -%⟩
⟨% set parts_str = parts|join(' ') %⟩
⟨% set verdict = 'Erfolg' if success else 'Fail' %⟩
⟪ die_text ~ ' ' ~ parts_str ~ ' → ' ~ total ~ ' ≥ SG ' ~ sg ~ ' (' ~ verdict ~ ')' ⟫
⟨%- endmacro %⟩

⟨% macro render_roll_json(die_text, sg, total, success, raw_rolls=[], parts=[]) -%⟩
⟪ {'roll': die_text, 'raw': raw_rolls, 'mods': parts, 'SG': sg, 'total': total, 'success': success} | tojson ⟫
⟨%- endmacro %⟩

⟨% macro roll_check(die_text, sg, total, success, raw_rolls=[], parts=[], local_debug=false, important=true) -%⟩
⟨% if campaign.fr_observer_pending and sg is not none %⟩
⟨% set sg = sg + 1 %⟩
⟨% set campaign.fr_observer_pending = false %⟩
⟨% set campaign.fr_observer_note = true %⟩
⟨% set success = total >= sg %⟩
⟨% endif %⟩
⟪ hud_tag(render_roll_overlay(die_text, sg, total, success, parts)) ⟫
⟨% if important and not success and sg is not none and total == sg - 1 %⟩
⟪ hud_tag('knapp daneben') ⟫
⟨% endif %⟩
⟨% if local_debug or ui.dice.debug_rolls %⟩

```json
⟪ render_roll_json(die_text, sg, total, success, raw_rolls, parts) ⟫
```

⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro label_for(count, sides, exploding=false) -%⟩
⟨% set star = '\*' if exploding else '' %⟩
⟪ (count > 1 and count ~ 'W' ~ sides ~ star) or 'W' ~ sides ~ star ⟫
⟨%- endmacro %⟩

⟨% macro format_raw_list(raw, max_show=6) -%⟩
⟨% if raw|length <= max_show %⟩
⟪ '[' ~ raw|join(',') ~ ']' ⟫
⟨% else %⟩
⟪ '[' ~ raw[:max_show]|join(',') ~ ',…]' ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro rng*roll(num, sides, exploding=false) -%⟩
⟨% set raw = [] %⟩
⟨% for * in range(num) %⟩
⟨% set r = range(1, sides + 1)|random %⟩
⟨% set raw = raw + [r] %⟩
⟨% if exploding and r == sides %⟩
⟨% set extra = range(1, sides + 1)|random %⟩
⟨% set raw = raw + [extra] %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨% set label = label_for(num, sides, exploding) %⟩
⟨% if num > 1 %⟩
⟨% set die_text = label ~ ' ' ~ format_raw_list(raw) %⟩
⟨% else %⟩
⟨% set die_text = label %⟩
⟨% endif %⟩
⟪ [raw, die_text] ⟫
⟨%- endmacro %⟩

⟨% macro die_for_attribute(attr_val) -%⟩
⟪ 'W10*' if attr_val >= 11 else 'W6*' ⟫
⟨%- endmacro %⟩

⟨% macro skill_check(attr, gear, sg, local_debug=false) -%⟩
⟨% set die = die_for_attribute(attr) %⟩
⟨% set roll = rng_roll(1, 10, true) if die == 'W10\*' else rng_roll(1, 6, true) %⟩
⟨% set raw = roll[0] %⟩
⟨% set die_text = roll[1] %⟩
⟨% set overflow = 0 %⟩
⟨% if raw and raw|length > 1 %⟩
⟨% set overflow = raw|sum - raw[0] %⟩
⟨% endif %⟩
⟨% set adjusted_raw_sum = raw|sum %⟩
⟨% set arena_note = none %⟩
⟨% set boss_note = none %⟩
⟨% if overflow > 0 and arena is defined and arena and arena.active and arena.damage_dampener is defined %⟩
⟨% set reduced_overflow = (overflow + 1) // 2 %⟩
⟨% if reduced_overflow < overflow %⟩
⟨% set adjusted_raw_sum = raw[0] + reduced_overflow %⟩
⟨% set arena_note = 'Arena-Dämpfer aktiv - Exploding-Overflow +' ~ overflow ~ ' → +' ~ reduced_overflow %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨% set total = adjusted_raw_sum + attr + gear %⟩
⟨% if campaign.boss_dr %⟩
⟨% set dr = campaign.boss_dr %⟩
⟨% set base_floor = (raw and raw[0] or 0) + attr + gear %⟩
⟨% set after_dr = total - dr %⟩
⟨% if after_dr < base_floor %⟩
⟨% set after_dr = base_floor %⟩
⟨% endif %⟩
⟨% if after_dr < total %⟩
⟨% set total = after_dr %⟩
⟨% set blocked = (adjusted_raw_sum + attr + gear) - total %⟩
⟨% set boss_note = 'Boss-DR -' ~ dr ~ ' → blockt ' ~ blocked %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨% set parts = ['+' ~ attr ~ ' ATTR', '+' ~ gear ~ ' Gear'] %⟩
⟨% if arena_note %⟩
⟨% set parts = parts + [arena_note] %⟩
⟪ hud_tag(arena_note) ⟫
⟨% endif %⟩
⟨% if boss_note %⟩
⟨% set parts = parts + [boss_note] %⟩
⟪ hud_tag(boss_note) ⟫
⟨% endif %⟩
⟨% set success = total >= sg %⟩
⟪ roll_check(die_text, sg, total, success, raw_rolls=raw, parts=parts, local_debug=local_debug) ⟫
⟪ success ⟫
⟨%- endmacro %⟩

⟨% macro vehicle_check(driver_attr, mod, sg, local_debug=false) -%⟩
⟪ skill_check(driver_attr, mod, sg, local_debug=local_debug) ⟫
⟨%- endmacro %⟩

⟨% macro mass_conflict_check(cmd_attr, asset_mod, sg, local_debug=false) -%⟩
⟪ skill_check(cmd_attr, asset_mod, sg, local_debug=local_debug) ⟫
⟨%- endmacro %⟩

⟨% macro enforce_identity_before_stats(char) -%⟩
⟨% set required = ['concept','callsign','name','hull'] %⟩
⟨% for field in required %⟩
⟨% if not getattr(char, field, None) %⟩
⟪ hud_tag('Bitte zuerst Konzept, Callsign, Name und Hülle festlegen.') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟪ attribute_budget_status(char) ⟫
⟨%- endmacro %⟩

⟨% macro on_episode_end(state) -%⟩
⟨% set state.stars_bonus = state.seeds_open %⟩
⟨%- endmacro %⟩

⟨% macro briefing_with_stars(mission) -%⟩
⟪ star_bonus_overlay() ⟫
⟨% if campaign.stars_bonus %⟩
⟪ rule_tag('Schwierigkeitszuschlag: ' ~ '☆'\*campaign.stars_bonus ~ ' (SG +' ~ campaign.stars_bonus ~ ')') ⟫
⟨% set mission.sg = mission.sg + campaign.stars_bonus %⟩
⟨% endif %⟩
⟨%- endmacro %⟩
Rufe `NextScene` am Szenenbeginn auf; es schließt die vorherige Szene über
`EndScene()` ab und startet den neuen Abschnitt.

### roll_antagonist() Macro

Wählt zufällig eine externe Fraktion aus `kampagnenuebersicht.md`, falls ein Seed keinen Gegner vorgibt.

<!-- Macro: roll_antagonist -->

⟨% macro roll_antagonist() %⟩
⟨% set pool = ["Projekt Phoenix", "Die Grauen", "Der Alte Orden", "Schattenkonzerne"] %⟩
⟪ random.choice(pool) ⟫
⟨% endmacro %⟩

```pseudo
if not live_threat and campaign.scene % 3 == 0:
    roll_antagonist()
```

### risk_badge() & format_risk() Macros

Konvertieren Rohdaten (`R1:` … `R4:`) in vereinheitlichte HUD-Badges.

<!-- Macro: risk_badge -->

⟨% macro risk_badge(level) -%⟩
⟨% set code = level|upper %⟩
⟨% set badge = risk_icon_map.get(code, '⚪ ' ~ code) %⟩
⟨% set label = risk_label_map.get(code, 'Unbekannt') %⟩
⟪ badge ~ ' · ' ~ label ⟫
⟨%- endmacro %⟩

<!-- Macro: format_risk -->

⟨% macro format_risk(raw) -%⟩
⟨% set text = raw|trim %⟩
⟨% if text|length > 2 and text[0] == 'R' and text[1] in '1234' and text[2] == ':' %⟩
⟨% set level = text[0:2] %⟩
⟨% set detail = text[3:]|trim %⟩
⟨% if detail %⟩
⟪ risk_badge(level) ~ ' · ' ~ detail ⟫
⟨% else %⟩
⟪ risk_badge(level) ⟫
⟨% endif %⟩
⟨% else %⟩
⟨% if text %⟩
⟪ risk_badge('R2') ~ ' · ' ~ text ⟫
⟨% else %⟩
⟪ risk_badge('R2') ⟫
⟨% endif %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

### artifact_overlay() Macro

Standardisiert die HUD-Ausgabe aktiver Artefakte.

<!-- Macro: artifact_overlay -->

⟨% macro artifact_overlay(name, effect, risk) -%⟩
⟪ hud_tag('Artefakt aktiv · ‹' ~ name ~ '› ▶ ' ~ effect ~ ' · ' ~ format_risk(risk)) ⟫
⟨%- endmacro %⟩

### roll_legendary() Macro

Würfelt legendäres Artefakt aus `artifact_pool_v3`.

<!-- Macro: roll_legendary -->

⟨% macro roll_legendary() -%⟩
⟨# LINT:RIFT_ARTIFACT_11_13_D6 #⟩
⟨% if not campaign.artifact_allowed %⟩⟨% return %⟩⟨% endif %⟩
⟨% if campaign.scene not in [11,12,13] %⟩⟨% return %⟩⟨% endif %⟩
⟨% if not campaign.boss_defeated %⟩⟨% return %⟩⟨% endif %⟩
⟨% if campaign.legendary_roll_pending is not defined %⟩⟨% set campaign.legendary_roll_pending = false %⟩⟨% endif %⟩
⟨% set gate_roll = rng_roll(1,6) %⟩
⟨% set gate = gate_roll[0][0] %⟩
⟪ roll_check(gate_roll[1], 6, gate, gate == 6, gate_roll[0], important=false) ⟫
⟨% set campaign.legendary_roll_pending = false %⟩
⟨% if campaign.last_rift_loot_entry is not none %⟩
⟨% do campaign.last_rift_loot_entry.update({'legendary': gate}) %⟩
⟨% endif %⟩
⟨% if gate != 6 %⟩⟨% return %⟩⟨% endif %⟩
⟨% set pick_roll = rng_roll(1,14) %⟩
⟨% set r = pick_roll[0][0] %⟩
⟨% set art = artifact_pool_v3[r-1] %⟩
⟪ artifact_overlay(art.name, art.effect, art.risk) ⟫
⟨% if char.artifact_log is none %⟩⟨% set char.artifact_log = [] %⟩⟨% endif %⟩
⟨% if art.name not in char.artifact_log %⟩⟨% do char.artifact_log.append(art.name) %⟩⟨% endif %⟩
⟪ kodex_log_artifact(art.name, {'effect': art.effect, 'risk': art.risk}) ⟫
⟨% if campaign.last_rift_loot_entry is not none %⟩
⟨% do campaign.last_rift_loot_entry.update({'legendary_drop': art.name}) %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

### generate_para_artifact() Macro

Erzeugt ein para-spezifisches Artefakt aus Körperteil und Buff-Matrix.

<!-- Macro: generate_para_artifact -->

⟨# Artefakt-Spawn nur in Rift-Op allowed #⟩
⟨% macro generate_para_artifact(creature) -%⟩
⟨% if not campaign.artifact_allowed %⟩⟨% return %⟩⟨% endif %⟩
⟨# Input: creature dict mit .type, .size, .name #⟩
⟨% set part_data = rng_roll(1,6) %⟩
⟨% set part_roll = part_data[0][0] %⟩
⟪ roll_check(part_data[1], 0, part_roll, true, part_data[0], important=false) ⟫
⟨% set side_data = rng_roll(1,6) %⟩
⟨% set side_roll = side_data[0][0] %⟩
⟪ roll_check(side_data[1], 0, side_roll, true, side_data[0], important=false) ⟫
⟨% set part_table = {
1:"Klaue",2:"Zahn",3:"Auge",4:"Drüse",5:"Chitinplatte",6:"Kern"} %⟩
⟨% set base_effect = {
1:"+2 DMG melee",2:"ArmorPierce+1",3:"Perception+1",
4:"1x Special charge",5:"Armor+1",6:"Power burst"} %⟩
⟨% set matrix = {
"Physisch":{"Auge":"Aim+1","Zahn":"+1 DMG","Klaue":"+2 DMG"},
"Psi":{"Auge":"Telepath range×2","Kern":"PP+2"},
"Temporal":{"Kern":"MiniJump ±3s","Drüse":"Action+1"},
"Elementar":{"Chitinplatte":"Element resist","Drüse":"Element bolt+1"},
"Bio-Schwarm":{"Drüse":"Spawn microdrone","Chitinplatte":"Climb 10m"} } %⟩
⟨% set part = part_table[part_roll] %⟩
⟨% set effect = base_effect[part_roll] %⟩
⟨% if matrix[creature.type][part] is defined %⟩
⟨% set effect = matrix[creature.type][part] %⟩
⟨% endif %⟩
⟨% if creature.size == "M" %⟩
⟨% set effect = effect ~ " (2 uses)" %⟩
⟨% elif creature.size == "L" %⟩
⟨% set effect = effect ~ " (passive)" %⟩
⟨% endif %⟩
⟨% set side = [
"Stress+1","Psi-Heat+1","SYS-1","Flashblind",
"Item breaks","Enemy +1 INI"][side_roll-1] %⟩
⟨% set name = part ~ ' von ' ~ creature.name %⟩
⟪ artifact_overlay(name, effect, side) ⟫
⟨% if char.artifact_log is none %⟩⟨% set char.artifact_log = [] %⟩⟨% endif %⟩
⟨% if name not in char.artifact_log %⟩⟨% do char.artifact_log.append(name) %⟩⟨% endif %⟩
⟪ kodex_log_artifact(name, {'effect': effect, 'risk': side}) ⟫
⟨%- endmacro %⟩

Aufruf: `⟨% set artifact = generate_para_artifact(current_creature) %⟩` - ausschließlich direkt
nach dem Rift-Boss (Szene 10). Für Boss-only gilt weiterhin: **max. 1 Artefakt pro Mission**.

### on_rift_boss_down() Macro

Automatisiert den Loot-Reminder nach einem Rift-Boss und markiert den legendären Wurf.

<!-- Macro: on_rift_boss_down -->

⟨% macro on_rift_boss_down() -%⟩
⟨% if campaign.type != 'rift' %⟩
⟪ hud_tag('Rift-Boss-Trigger steht nur in Rift-Ops zur Verfügung.') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% set campaign.boss_defeated = true %⟩
⟨% if campaign.rift_loot_prompted %⟩
⟪ hud_ping('Loot-Protokoll bereits abgewickelt - Legendary-Wurf bei Bedarf direkt nach dem Boss wiederholen.') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% set campaign.rift_loot_prompted = true %⟩
⟨% set boss_data = campaign.last_rift_boss %⟩
⟨% if not boss_data %⟩
⟪ hud_tag('Warnung: Kein gespeicherter Rift-Boss - nutze generate_para_artifact() manuell.') ⟫
⟨% return %⟩
⟨% endif %⟩
⟪ hud_tag('Rift-Boss neutralisiert - Loot-Automation aktiv.') ⟫
⟪ generate_para_artifact(boss_data.creature) ⟫
⟨% if campaign.loot_log is not defined or campaign.loot_log is none %⟩⟨% set campaign.loot_log = [] %⟩⟨% endif %⟩
⟨% set entry = {
'seed': campaign.seed_id,
'boss': boss_data.creature.name,
'scene': campaign.scene,
'artifact_macro': 'generate_para_artifact',
'legendary': 'pending'
} %⟩
⟨% do campaign.loot_log.append(entry) %⟩
⟨% set campaign.last_rift_loot_entry = entry %⟩
⟨% set campaign.legendary_roll_pending = true %⟩
⟪ hud_ping('Legendärer Drop: 1W6, nur bei 6 - roll_legendary() direkt nach dem Boss ausführen.') ⟫
⟨%- endmacro %⟩

### Paradoxon / Rifts (neue Guards)

⟨% macro on_stabilize_history() -%⟩
⟨% set campaign.px = campaign.px + 1 %⟩
⟨% if campaign.px >= 5 %⟩
⟨# LINT:PX5_SEED_GATE #⟩
⟪ hud_tag('Paradoxon-Index 5 erreicht - neue Rift-Koordinaten verfügbar') ⟫
⟪ generate_rift_seeds(1,2) ⟫
⟨% set campaign.px = 0 %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro can_launch_rift(seed_id=None) -%⟩
⟨% set loc = (location or campaign.loc or 'HQ')|upper %⟩
⟨% set seeds = campaign.rift_seeds or [] %⟩
⟨% set mission_in_episode = campaign.mission_in_episode or 0 %⟩
⟨% set episode_done = campaign.episode_completed or mission_in_episode >= 10 %⟩
⟨% set open = false %⟩
⟨% for seed in seeds %⟩
⟨% set status = (seed.status or 'open')|lower %⟩
⟨% if status != 'closed' %⟩
⟨% set sid = (seed.id or seed.seed_id or seed.label or seed)|string %⟩
⟨% if seed_id is none or sid == (seed_id|string) %⟩
⟨% set open = true %⟩⟨% break %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟪ 'true' if (loc == 'HQ' and episode_done and open) else 'false' ⟫
⟨%- endmacro %⟩

⟨% macro apply_rift_mods_next_episode() -%⟩
⟨% set seeds = campaign.rift_seeds or [] %⟩
⟨% set open_seeds = [] %⟩
⟨% for seed in seeds %⟩
⟨% set status = (seed.status or 'open')|lower %⟩
⟨% if status != 'closed' %⟩
⟨% do open_seeds.append(seed) %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨% set n = open_seeds|length %⟩
⟨% set sg_bonus = [n, 3]|min %⟩
⟨% set cu_multi = [1.0 + 0.2*n, 1.6]|min %⟩
⟨% set campaign.next_episode = {'sg_bonus': sg_bonus, 'cu_multi': cu_multi} %⟩
⟨%- endmacro %⟩

### launch_rift Macro (Gate: nur im HQ & nach Episodenende)

⟨% macro launch_rift(id=None) -%⟩
⟨% if can_launch_rift(id) != 'true' %⟩
⟪ hud_tag('Rift-Start blockiert - erst nach Episodenende & im HQ') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% set seeds = campaign.rift_seeds or [] %⟩
⟨% set target = None %⟩
⟨% for seed in seeds %⟩
⟨% set status = (seed.status or 'open')|lower %⟩
⟨% if status != 'closed' %⟩
⟨% set sid = (seed.id or seed.seed_id or seed.label or seed)|string %⟩
⟨% if id is none or sid == (id|string) %⟩⟨% set target = seed %⟩⟨% break %⟩⟨% endif %⟩
⟨% endif %⟩
⟨% endfor %⟩
⟨% set sid = (target and (target.id or target.label)) or (id|string) %⟩
⟪ StartMission(total=14, type='rift', epoch=target and target.epoch or campaign.epoch,
seed_id=sid, objective='Resolve Rift') ⟫
⟨%- endmacro %⟩

### generate_para_creature() Macro

Erzeugt eine Para-Kreatur über `#para-creature-generator`.

<!-- Macro: generate_para_creature -->

⟨% macro generate_para_creature(seed) -%⟩
⟨%- set enc = gpull('gameplay/kreative-generatoren-begegnungen.md#para-creature-generator', seed) -%⟩
⟨%- set hud_core = hud_tag(enc.creature.name ~ ' (' ~ enc.creature.type ~ ')') -%⟩
⟨%- set hud = (allow_event_icons and '👾 ' or '') ~ hud_core -%⟩
⟪ {'creature': enc.creature, 'loot': enc.loot, 'hud': hud} ⟫
⟨%- endmacro %⟩

### itemforge() Macro

Erzeugt automatisches Loot anhand von **CU-Budget** und Missionsart.
Parameter: `core` oder `rift` und optional ein Budget in CU.
Gib zusätzlich ein `year` an, wählt ItemForge historische Skins über `altSkin`.
Die Würfe laufen verdeckt; `!reveal` zeigt sie auf Wunsch.
Heavy-Gear setzt die passende Lizenz voraus; `force=true` ignoriert diese Beschränkung.
Findet das Macro nichts Passendes, meldet Kodex `NONE`.

**Item-DSL:**

```
<NAME> · Typ: Gear/Cyber/Bio/Consumable · Kosten: <CU> · SYS: <0/1/2>
Effekt: <kurz> · Limit: <x/Szene oder x/Mission> · Tradeoff: <klein>
```

**Guardrails:**

- **Gear:** kein SYS, kleine Vorteile, Limit 1×/Szene oder 1×/Mission.
- **Cyber/Bio:** SYS 1-2, moderate permanente Boni/Trigger - keine +2-"Godbuttons".
- **Consumables:** einmalig; +PP/-Psi-Heat nur in kleinen Dosen, oft mit kleinem Stress-Tradeoff.
- **Psi-Heat-Interaktion:** keine globalen "-1 Psi-Heat pro Einsatz"-Auren;
  erlaubt ist 1× pro Konflikt 1 Psi-Heat venten oder eine Psi-Aktion ohne Psi-Heat
  (nicht beides).
- **PP-Boosts:** maximal +1-2 PP, höchstens 2× pro Mission; ggf. +1 Stress.

⟨% macro validate_item(item) -%⟩
⟨% if item.typ == 'Gear' and (item.sys or 0) > 0 %⟩INVALID: Gear ohne SYS⟨% endif %⟩
⟨% if item.typ in ['Cyber','Bio'] and (item.sys or 0) not in [1,2] %⟩INVALID: Cyber/Bio SYS 1-2⟨% endif %⟩
⟨% if item.typ == 'Consumable' and item.limit != '1x' %⟩INVALID: Consumable einmalig⟨% endif %⟩
⟨%- endmacro %⟩

Beispielaufrufe:

```txt
!itemforge core 100cu 1969    # T1-T2, Skin passend zu 1969
!itemforge rift 2120          # T1-T3 inkl. heavy
```

Rift-Missionen generieren mit `itemforge()` regulären Loot wie Core-Einsätze und
gewähren nach dem Sieg über das Paramonster einen zusätzlichen Artefaktwurf
(`1W6`, nur bei `6`).

**Loot-Handling (Outcome-only):** Keycards, Intel und Beute erscheinen als
Ergebnis-Tag oder im Debrief-Recap ("Keycard erhalten", "Intel gesichert").
Keine "Durchsuchen"-Prozeduren, kein Body-Handling; falls nötig, nutze den
Actionfilm-Cut und gib die Konsequenzen (Noise/Stress/Heat/Zeitfenster) aus.

⟨# Boss-DR-Skala nach Teamgröße - Referenztabelle in
gameplay/kampagnenstruktur.md#boss-rhythmus-pro-episode.
Teamgröße → Mini-Boss DR / Arc-/Rift-Boss DR:
1-2 → 1 / 2
3-4 → 2 / 3
5 → 3 / 4
team_size wird aus party.characters/team.members ermittelt und auf 1-5
geklemmt. #⟩
⟨% macro boss_dr_for_team_size(team_size, tier='arc') -%⟩
⟨% set size = [team_size|int, 5]|min %⟩
⟨% if size <= 0 %⟩
⟪ 0 ⟫
⟨% elif size <= 2 %⟩
⟪ 1 if tier == 'mini' else 2 ⟫
⟨% elif size <= 4 %⟩
⟪ 2 if tier == 'mini' else 3 ⟫
⟨% else %⟩
⟪ 3 if tier == 'mini' else 4 ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

### generate_boss() Macro

Wählt gemäß Missionsstand einen Mini-, Arc- oder Rift-Boss aus den Pools des
Boss-Generators. Mini-Bosse erscheinen erst ab Mission 5.
Jeder Datensatz enthält **Schwäche**, **Stil** und **Seed-Bezug**.

<!-- Macro: generate_boss -->

⟨% macro generate_boss(type, mission_number, epoch) %⟩
⟨% if campaign.boss_history is none %⟩⟨% set campaign.boss_history = [] %⟩⟨% endif %⟩
⟨% if campaign.boss_pool_usage is none %⟩⟨% set campaign.boss_pool_usage = {} %⟩⟨% endif %⟩
⟨% set campaign.boss_dr = 0 %⟩
⟨% set team_size = campaign.team_size|default(5) %⟩
⟨% if campaign.team is defined and campaign.team.members is defined %⟩
⟨% set member_count = campaign.team.members|length %⟩
⟨% if member_count > 0 %⟩
⟨% set team_size = member_count %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨% if type == "core" %⟩
⟨% if mission_number % 10 == 0 %⟩
⟨% set pool_name = 'core_arc_boss_pool' %⟩
⟨% set pool_data = core_arc_boss_pool %⟩
⟨% set key = pool_data | list | random %⟩
⟨% set boss = pool_data.pop(key) %⟩
⟨% do campaign.boss_history.append(boss) %⟩
⟨% set used = campaign.boss_pool_usage.get(pool_name, 0) %⟩
⟨% do campaign.boss_pool_usage.update({pool_name: used + 1}) %⟩
⟨% set campaign.boss_dr = boss_dr_for_team_size(team_size, 'arc') %⟩
⟪ (allow_event_icons and '💀 ' or '') ~
hud_tag('ARC-BOSS (T3) → ' ~ boss.name ~
' · Pool: ' ~ pool_name) ⟫
⟪ hud_tag('Boss-DR aktiviert - -' ~ campaign.boss_dr ~ ' Schaden pro Treffer') ⟫
⟨% elif mission_number % 5 == 0 and mission_number >= 5 %⟩
⟨% set pool_name = 'core_mini_pool' %⟩
⟨% set pool_data = core_mini_pool[epoch] %⟩
⟨% set boss = pool_data | random %⟩
⟨% do pool_data.remove(boss) %⟩
⟨% do campaign.boss_history.append(boss) %⟩
⟨% set used = campaign.boss_pool_usage.get(pool_name, 0) %⟩
⟨% do campaign.boss_pool_usage.update({pool_name: used + 1}) %⟩
⟨% set campaign.boss_dr = boss_dr_for_team_size(team_size, 'mini') %⟩
⟪ (allow_event_icons and '💀 ' or '') ~
hud_tag('MINI-BOSS (T3) → ' ~ boss ~
' · Pool: ' ~ pool_name) ⟫
⟪ hud_tag('Boss-DR aktiviert - -' ~ campaign.boss_dr ~ ' Schaden pro Treffer') ⟫
⟨% else %⟩NONE⟨% endif %⟩
⟨% else %⟩
⟨% if mission_number % 10 == 0 %⟩
⟨% set pool_name = 'rift_boss_pool' %⟩
⟨% set boss_data = generate_para_creature(campaign.seed_id) %⟩
⟨% set campaign.last_rift_boss = boss_data %⟩
⟨% set campaign.rift_loot_prompted = false %⟩
⟨% set campaign.boss_defeated = false %⟩
⟨% do campaign.boss_history.append(boss_data.creature.name) %⟩
⟨% set used = campaign.boss_pool_usage.get(pool_name, 0) %⟩
⟨% do campaign.boss_pool_usage.update({pool_name: used + 1}) %⟩
⟨% set campaign.boss_dr = boss_dr_for_team_size(team_size, 'arc') %⟩
⟪ (allow_event_icons and '💀 ' or '') ~
hud_tag('RIFT-BOSS (T3) → ' ~ boss_data.creature.name ~
' · Pool: ' ~ pool_name) ⟫
⟪ hud_tag('Boss-DR aktiviert - -' ~ campaign.boss_dr ~ ' Schaden pro Treffer') ⟫
⟨% else %⟩NONE⟨% endif %⟩
⟨% endif %⟩
⟨% endmacro %⟩

<!-- Macro: psi_activation -->

⟨% macro psi_activation(name, sys_cost, pp_cost, heat_cost) -%⟩
⟨% if char.sys + sys_cost > char.sys_max %⟩
⟪ hud_tag('SYS ' ~ char.sys ~ '/' ~ char.sys_max ~ ' - Kapazität erreicht') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% set campaign.psi_logged = true %⟩
⟨% set char.sys = char.sys + sys_cost %⟩
⟨% set char.sys_used = char.sys_used + sys_cost %⟩
⟨% set char.pp = char.pp - pp_cost %⟩
⟨% set char.psi_heat = (char.psi_heat or 0) + heat_cost %⟩
⟪ hud_tag(
'SYS ' ~ char.sys ~ '/' ~ char.sys_max ~
' · PP ' ~ char.pp ~ '/' ~ char.pp_max ~
' · Ψ-HEAT ' ~ char.psi_heat ~ '/' ~ (char.psi_heat_max or char.heat_max or 6) ~
' - ' ~ name
) ⟫
⟨%- endmacro %⟩

<!-- Macro: log_intervention -->

⟨% macro log_intervention(result, data=None) -%⟩
⟨# LINT:FR_INTERVENTION #⟩
⟨% set entry = result if result is mapping else {'result': result} %⟩
⟨% if data %⟩
⟨% set entry = entry | combine(data, recursive=true) %⟩
⟨% endif %⟩
⟨% set text = entry.result if entry.result is defined else entry.get('result', entry.get('status', '')) %⟩
⟪ hud_tag('FR-INTRV: ' ~ text) ⟫
⟨% if campaign.kodex_log is none %⟩⟨% set campaign.kodex_log = {} %⟩⟨% endif %⟩
⟪ kodex_log_npc('fr_intervention', entry) ⟫
⟨%- endmacro %⟩

> **Runtime-Hinweis:** `log_intervention()` im Node-Runtime-Modul erzeugt parallel zur HUD-Ausgabe einen
> persistierten Eintrag (`logs.fr_interventions[]`) und aktualisiert das Arc-Dashboard (`fraktionen{}` →
> `last_intervention`/`interventions[]`). Die Spielleitung kann den Verlauf bei Bedarf mit
> `get_intervention_log()` gefiltert auslesen. Über den optionalen Parameter `data` gebt ihr
> zusätzliche Felder wie `faction`, `impact`, `observer` oder `escalated` mit; Szene, Mission und
> Episode ergänzt die Runtime automatisch.

<!-- Macro: kodex_log_npc -->

⟨% macro kodex_log_npc(npc_id, data) -%⟩
⟨% if campaign.kodex_log is none %⟩⟨% set campaign.kodex_log = {} %⟩⟨% endif %⟩
⟨% do campaign.kodex_log.update({'npc:' ~ npc_id: data}) %⟩
⟨%- endmacro %⟩

<!-- Macro: kodex_log_artifact -->

⟨% macro kodex_log_artifact(artifact_id, data) -%⟩
⟨% if campaign.kodex_log is none %⟩⟨% set campaign.kodex_log = {} %⟩⟨% endif %⟩
⟨% do campaign.kodex_log.update({'artifact:' ~ artifact_id: data}) %⟩
⟨%- endmacro %⟩

<!-- Artefakt-Wurf nur bei mission.type == "Rift" → 1d6 == 6 -->

⟨% if campaign.type == "rift" and campaign.scene in [11,12,13] %⟩
⟨% set gate_data = rng_roll(1,6) %⟩
⟨% set r = gate_data[0][0] %⟩
⟪ roll_check(gate_data[1], 6, r, r == 6, gate_data[0], important=false) ⟫
⟨% if r == 6 %⟩
⟪ roll_legendary() ⟫
⟨% endif %⟩
⟨% endif %⟩

<!-- Macro: scene_budget_enforcer -->

⟨% macro scene_budget_enforcer(total) -%⟩
⟨% if total is none %⟩⟨% return %⟩⟨% endif %⟩
⟨% if campaign.scene > total %⟩
⟨#GM: Scene overrun ⟪ campaign.scene ⟫/⟪ total ⟫#⟩
⟨% endif %⟩
⟨%- endmacro %⟩

<!-- Macro: physics_filter -->

⟨% macro physics_filter(env_tags) -%⟩
⟨% set filtered = [] %⟩
⟨% for t in env_tags %⟩
⟨% if t not in ["deepwater","vacuum"] %⟩⟨% do filtered.append(t) %⟩⟨% endif %⟩
⟨% endfor %⟩
⟪ filtered ⟫
⟨%- endmacro %⟩

<!-- Macro: option_resolve -->

⟨% macro option_resolve(risk, reward, cause="") -%⟩
⟪ hud_tag('Risk ' ~ risk ~ ' vs Reward ' ~ reward) ⟫
⟨% if cause %⟩
⟪ cause ⟫
⟨% endif %⟩
⟨% if reward > risk %⟩
Resonanz +1
⟨% elif reward < risk %⟩
Risiko: Kein Px-Fortschritt · Konsequenz über Stress/CU/Heat
⟨% else %⟩
Paradoxon unverändert - Resonanz stagniert
⟨% endif %⟩
⟨%- endmacro %⟩
Beispiel:

```jinja
⟪ option_resolve(2,3,'Eruption path restored - Px +1') ⟫
```

<!-- Macro: output_sanitizer -->

⟨% macro output*sanitizer(text) -%⟩
⟪ text
| regex_replace('<!--\s*Macro:.*?-->', '', ignorecase=True, multiline=True)
| regex_replace('(?s)⟨%\s*macro.*?%⟩.*?⟨%-?\s*endmacro\s*%⟩', '', ignorecase=True)
| regex_replace('(?s)⟨%.*?%⟩', '')
| regex_replace('`\\s*[!/][^`]*`', '')
   | regex_replace('`\\s*[A-Za-z*]+\\([^`]\*\\)`', '')
| replace('⟪', '')
| replace('⟫', '') ⟫
⟨%- endmacro %⟩

### Tone-Filter-Regelsatz ⟨#tone-filter}

Die KI wendet diesen Regelsatz auf jede Ausgabe an:

- `source` markiert den Ursprung: `HUD`, `CODEX` oder `NPC`.
- Bei `HUD` und `CODEX` bleibt der Text unverändert.
- Ist `kodex.dev_raw` gesetzt, passiert ebenfalls nichts.
- Für `NPC`-Dialoge:
  - Tokens wie `NAME.EXT` mit `EXT` in `CHK`, `DAT`, `CFG`, `TXT` werden zu
    `Aktenanhang` (oder `Beilage`/`Abzug`) umgeschrieben.
  - Wörter in VERSALIEN mit mindestens drei Zeichen werden kleingeschrieben,
    außer sie stehen auf einer Whitelist (`CIA`, `FBI`, `NSA`).
  - Digitale Ersatzwörter (z. B. `uplink file`, `download`, `upload`, `database`,
    `server`) sind Blacklist und werden in Noir-Varianten überführt.

```pseudo
function tone_filter(text, source):
    if source == HUD or source == CODEX or dev_raw:
        return text
    text = replace_file_tokens(text)    # NAME.EXT -> "Aktenanhang"
    text = downcase_allcaps(text)       # MAX POWER -> max power
    return text
```

Beispiele:

```pseudo
tone_filter("`SCAN 92 %`", HUD) -> "`SCAN 92 %`"
tone_filter("Lade LOGFILE.CFG", NPC) -> "Lade Aktenanhang"
tone_filter("SPRINGT AUF MAX POWER", NPC) -> "springt auf max power"
tone_filter("CIA DATABASE", NPC) -> "CIA DATABASE"
```

Nutze `output_sanitizer()` gefolgt von `tone_filter()` am Ende jeder
Szenen-Generierung, um HTML-Kommentare zu entfernen und Systemjargon zu
glätten:

```pseudo
text = render_scene()
return tone_filter(output_sanitizer(text), source)
```

Dieses Filtering entfernt auch versteckte Macro-Calls wie
`<!--⟪ NextScene(...) ⟫-->` oder
`<!--⟪ scene_budget_enforcer() ⟫-->` aus der sichtbaren Ausgabe.
NPC-Dialoge und Kodex-Logs passieren `tone_filter()` nach der Umwandlung
technischer Tags, damit keine Systemtokens im Spieltext bleiben.

### generate_rift_seeds() Macro

Erzeugt neue Rift-Seeds aus dem "Rift-Seed Catalogue" und protokolliert sie.
`campaign.rift_seeds[]` bleibt die Single Source; `arc_dashboard.offene_seeds[]`
spiegelt diesen Block beim Save/Load.

<!-- Macro: generate_rift_seeds -->

⟨% macro generate_rift_seeds(count_min=1, count_max=2) -%⟩
⟨% set catalogue = gpull('gameplay/kreative-generatoren-missionen.md#rift-seed-catalogue') %⟩
⟨% set options = [s for s in catalogue if not getattr(s, 'meta_introspection', False)] %⟩
⟨% set n = range(count_min, count_max + 1)|random %⟩
⟨% set picks = random.sample(options, n) %⟩
⟨% if campaign.rift_seeds is none %⟩⟨% set campaign.rift_seeds = [] %⟩⟨% endif %⟩
⟨% if arc_dashboard.offene_seeds is none %⟩⟨% set arc_dashboard.offene_seeds = [] %⟩⟨% endif %⟩
⟨# Normalizer für alte Saves ohne Label/Hook/Marker #⟩
⟨% for legacy in campaign.rift_seeds %⟩
⟨% if legacy.label is not defined %⟩⟨% set legacy.label = legacy.hook if legacy.hook is defined else legacy.id %⟩⟨% endif %⟩
⟨% if legacy.seed_tier is not defined %⟩⟨% set legacy.seed_tier = 'mid' %⟩⟨% endif %⟩
⟨% if legacy.hook is not defined %⟩⟨% set legacy.hook = legacy.label %⟩⟨% endif %⟩
⟨% if legacy.time_marker is not defined %⟩⟨% set legacy.time_marker = 'Echo' %⟩⟨% endif %⟩
⟨% endfor %⟩
⟨% for seed in picks %⟩
⟨% set label = seed.label if seed.label is defined else seed.rift_id %⟩
⟨% set seed_tier = seed.seed_tier if seed.seed_tier is defined else 'mid' %⟩
⟨% set hook = seed.hook if seed.hook is defined else label %⟩
⟨% set time_marker = seed.time_marker if seed.time_marker is defined else 'Echo' %⟩
⟨% set briefing_public = seed.briefing_public if seed.briefing_public is defined else [] %⟩
⟨% set leads = seed.leads if seed.leads is defined else [] %⟩
⟨% set boss_private = seed.boss_private if seed.boss_private is defined else {} %⟩
⟨% set new_seed = {
'id': seed.rift_id,
'label': label,
'seed_tier': seed_tier,
'hook': hook,
'time_marker': time_marker,
'epoch': seed.epoch,
'status': 'open',
'briefing_public': briefing_public,
'leads': leads,
'boss_private': boss_private
} %⟩
⟨% do campaign.rift_seeds.append(new_seed) %⟩
⟨% do arc_dashboard.offene_seeds.append(new_seed) %⟩
⟪ hud_tag('Rift entdeckt: ' ~ seed.rift_id ~ ' · ' ~ label ~ ' · Marker ' ~ time_marker ~ ' (' ~ seed.epoch ~ ')') ⟫
⟨% endfor %⟩
⟨%- endmacro %⟩

### PxPing() Macro

⟨% macro PxPing() -%⟩
⟨% if campaign.lastPx is not defined %⟩
⟨% set campaign.lastPx = 0 %⟩
⟨% set campaign.lastPxScene = 0 %⟩
⟨% endif %⟩
⟨% if campaign.px != campaign.lastPx and campaign.px >= 5 %⟩
⟨% if campaign.px == 5 %⟩
⟪ hud_tag('Paradoxon-Index 5 erreicht - ' ~ hud_vocab('pressure_drop') ~ ' Neue Rift-Koordinaten verfügbar.') ⟫
⟨% set campaign.px = 0 %⟩
⟪ generate_rift_seeds(1,2) ⟫
⟨% set campaign.lastPx = campaign.px %⟩
⟨% else %⟩
⟪ hud_tag('Px ' ~ campaign.px ~ '/5 · ' ~ hud_vocab('signal_modified')) ⟫
⟨% set campaign.lastPx = campaign.px %⟩
⟨% endif %⟩
⟨% set campaign.lastPxScene = campaign.scene %⟩
⟨% elif campaign.px == campaign.lastPx and campaign.scene - campaign.lastPxScene >= 2 and campaign.px >= 5 %⟩
⟨% if campaign.px == 5 %⟩
⟪ hud_tag('Paradoxon-Index 5 erreicht - ' ~ hud_vocab('pressure_drop') ~ ' Neue Rift-Koordinaten verfügbar.') ⟫
⟨% set campaign.px = 0 %⟩
⟪ generate_rift_seeds(1,2) ⟫
⟨% set campaign.lastPx = campaign.px %⟩
⟨% else %⟩
⟪ hud_tag('Px ' ~ campaign.px ~ '/5 · ' ~ hud_vocab('signal_modified')) ⟫
⟨% set campaign.lastPx = campaign.px %⟩
⟨% endif %⟩
⟨% set campaign.lastPxScene = campaign.scene %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

```md
<!-- Test: PxPing throttle -->

⟨% set campaign = namespace(px=5, scene=1, lastPx=0, lastPxScene=0) %⟩
⟨% for s in range(1,6) %⟩
⟨% set campaign.scene = s %⟩Szene ⟪ s ⟫: ⟪ PxPing() ⟫
⟨% endfor %⟩
```

### inject_complication() Macro

Fügt nach vielen Tech-Schritten eine nicht-technische Hürde ein.

<!-- Macro: inject_complication -->

⟨% macro inject_complication(tech_steps) -%⟩
⟨% if tech_steps > 3 %⟩
⟪ exfil_complication() ⟫
⟨% set social = [
{"tag": "social", "obstacle": "Geiselverhandlung"},
{"tag": "social", "obstacle": "Streik"},
{"tag": "social", "obstacle": "Hofintrige"}
] %⟩
⟨% set physical = [
{"tag": "physical", "obstacle": "Verfolgungsjagd"},
{"tag": "physical", "obstacle": "Naturgefahr"},
{"tag": "physical", "obstacle": "Einsturz"}
] %⟩
⟨% set pool = social + physical %⟩
⟨% set comp = pool | random %⟩
⟪ hud_tag('Komplikation: ' ~ comp.obstacle ~ ' (' ~ comp.tag ~ ')') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

### fail_forward() Macro

Zeigt ein Banner, wenn ein Erfolg Kosten verursacht.

<!-- Macro: fail_forward -->

⟨% macro fail_forward(cost) -%⟩
<span style="color:#f93">Regel</span> Erfolg mit Kosten: ⟪ cost ⟫
⟨%- endmacro %⟩

⟨# === Entwurfs-Makros & Arena === #⟩
⟨% macro run_shop_checks() -%⟩
⟨% call maintenance() %⟩⟨% endcall %⟩
⟨% call license_check() %⟩⟨% endcall %⟩
⟨%- endmacro %⟩

### TK-Melee() Macro

Prüft den SR-Wert des Ziels und passt die SG an.

<!-- Macro: TK_Melee -->

⟨% macro TK_Melee(attack, target) -%⟩
⟨% set SG = attack.sg %⟩
⟨% if target.armor >= 2 %⟩
⟨% set SG = SG + 1 %⟩
⟨% endif %⟩
⟪ SG ⟫
⟨%- endmacro %⟩

### tech_solution() Macro

Protokolliert technische Lösungen und erhöht bei Wiederholung die SG.

<!-- Macro: tech_solution -->

⟨% macro tech_solution() -%⟩
⟨% if campaign.tech_device_lock is not defined %⟩⟨% set campaign.tech_device_lock = false %⟩⟨% endif %⟩
⟨% if campaign.tech_heat is not defined %⟩⟨% set campaign.tech_heat = 0 %⟩⟨% endif %⟩
⟨% if campaign.tech_sg is not defined %⟩⟨% set campaign.tech_sg = 0 %⟩⟨% endif %⟩
⟨% if campaign.tech_steps is not defined %⟩⟨% set campaign.tech_steps = 0 %⟩⟨% endif %⟩
⟨% if campaign.complication_done is not defined %⟩⟨% set campaign.complication_done = false %⟩⟨% endif %⟩
⟨% set team_size = campaign.team_size|default(5) %⟩
⟨% if team_size <= 1 %⟩
⟨% set tech_threshold = 1 %⟩
⟨% elif team_size <= 2 %⟩
⟨% set tech_threshold = 2 %⟩
⟨% else %⟩
⟨% set tech_threshold = 3 %⟩
⟨% endif %⟩
⟨% if campaign.tech_device_lock %⟩
⟪ hud_tag('Gerätezwang aktiv - Field Kit anmelden, bevor weitere Tech-Lösungen greifen.') ⟫
⟨% else %⟩
⟨% set campaign.tech_steps = campaign.tech_steps + 1 %⟩
⟨% if not campaign.complication_done %⟩
⟪ inject_complication(campaign.tech_steps) ⟫
⟨% if campaign.tech_steps > 3 %⟩⟨% set campaign.complication_done = true %⟩⟨% endif %⟩
⟨% endif %⟩
⟨% set campaign.tech_heat = campaign.tech_heat + 1 %⟩
⟨% if campaign.tech_heat >= tech_threshold %⟩
⟨% set campaign.tech_sg = campaign.tech_sg + 1 %⟩
⟪ hud_tag('Tech-SG +' ~ campaign.tech_sg) ⟫
⟨% set campaign.tech_heat = 0 %⟩
⟨% if team_size <= 2 %⟩
⟨% set campaign.tech_device_lock = true %⟩
⟪ hud_tag('Gerätezwang aktiv: Field Kit oder Drone verpflichtend einsetzen, um Tech-Lösungen fortzusetzen.') ⟫
⟨% endif %⟩
⟨% endif %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

### confirm_device_slot() Macro

Hebt den Gerätezwang auf, sobald das Team ein physisches Field Kit oder eine Drone anmeldet.

<!-- Macro: confirm_device_slot -->

⟨% macro confirm_device_slot() -%⟩
⟨% if campaign.tech_device_lock %⟩
⟨% set campaign.tech_device_lock = false %⟩
⟪ hud_tag('Gerätezwang bestätigt - Tech-Fenster wieder frei.') ⟫
⟨% else %⟩
⟪ hud_tag('Gerätezwang aktuell inaktiv - kein zusätzlicher Field-Kit-Nachweis nötig.') ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

### Arena-Makros

⟨% set arena_scenarios = [
"Offene Wüstenruine",
"Labyrinth-Bunker",
"Dschungel mit dichter Vegetation",
"Urbanes Trümmerfeld",
"Symmetrische Trainingsarena",
] %⟩

⟨% set faction_allies = {
"Projekt Phoenix": ["Phoenix Scout", "Phoenix Heavy"],
"Die Grauen": ["Grey Agent", "Grey Sniper"],
"Der Alte Orden": ["Templer", "Reliktjäger"],
"Schattenkonzerne": ["Black Ops", "Konzern-Sniper"],
} %⟩

<!-- Macro: arena_scenario -->

⟨% macro arena_scenario(team_size=1) -%⟩
⟪ random.choice(arena_scenarios) ⟫
⟨%- endmacro %⟩

<!-- Macro: create_faction_allies -->

⟨% macro create_faction_allies(faction, count) -%⟩
⟨% set pool = faction_allies.get(faction, []) %⟩
⟪ random.sample(pool, count) ⟫
⟨%- endmacro %⟩

<!-- Macro: create_opposing_team -->

⟨% macro create_opposing_team(size, allies, difficulty="normal") -%⟩
⟨% set faction = allies[0] if allies else "Projekt Phoenix" %⟩
⟨% set pool = faction_allies.get(faction, []) %⟩
⟨% set team = random.sample(pool, size) %⟩
⟨# Level und Ausrüstung spiegeln; difficulty skaliert Werte #⟩
⟪ team ⟫
⟨%- endmacro %⟩

⟨# LINT:ARENA_SNAPSHOT #⟩
⟨% macro arena_snapshot_state() -%⟩
⟨% set arena.\_snap = {
'sys': char.sys, 'psi_heat': char.psi_heat, 'stress': char.stress,
'pp': char.pp, 'cooldowns': char.cooldowns
} %⟩
⟨%- endmacro %⟩

⟨# LINT:ARENA_RESTORE #⟩
⟨% macro arena_restore_state() -%⟩
⟨% if arena.\_snap %⟩
⟨% set char.sys = arena.\_snap.sys %⟩
⟨% set char.psi_heat = arena.\_snap.psi_heat %⟩
⟨% set char.stress = arena.\_snap.stress %⟩
⟨% set char.pp = arena.\_snap.pp %⟩
⟨% set char.cooldowns = arena.\_snap.cooldowns %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:ARENA_BLOCK_SAVE #⟩
⟨% macro save_guard() -%⟩
⟨% if arena and arena.active %⟩
⟪ hud_tag('Speichern blockiert - Arena aktiv') ⟫
⟨% return %⟩
⟨% endif %⟩
⟪ hq_only_save_guard() ⟫
⟨%- endmacro %⟩

⟨% macro hq_only_save_guard() -%⟩
⟨% if campaign.loc != 'HQ' %⟩
⟪ hud_tag('Speichern ist ausschließlich im HQ möglich.') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro serialize_progress() -%⟩
{
"episode": campaign.episode,
"mission": campaign.mission_in_episode,
"scene": campaign.scene,
"lvl": char.lvl,
"rank": char.rank,
"dice_mode": dice_mode_map(char),
"px": {"value": campaign.px, "seeds_open": campaign.seeds_open, "stars_next": campaign.stars_bonus},
"stress": char.stress,
"sys": {"cur": char.sys, "max": char.sys_max},
"flags": {"has_psi": char.flags.has_psi}
}
⟨%- endmacro %⟩

⟨% macro cmdSave() -%⟩
⟪ save_guard() ⟫
⟨% if campaign.loc != 'HQ' %⟩⟨% return %⟩⟨% endif %⟩
⟨% set campaign.exfil = {
'active': false,
'ttl': 0,
'hot': false,
'sweeps': 0,
'stress': 0,
'anchor': '?',
'armed': false
} %⟩
⟨% set char.stress = 0 %⟩
⟪ serialize_progress() ⟫
⟨%- endmacro %⟩

⟨# LINT:ARENA_CAMPAIGN_SNAP #⟩
⟨% macro arena_snapshot_campaign() -%⟩
⟨% set arena.\_camp = {
'seeds_suppressed': campaign.seeds_suppressed,
'px_frozen': campaign.px_frozen,
'boss_suppressed': campaign.boss_suppressed,
'intervention_suppressed': campaign.intervention_suppressed,
'cu_payout': campaign.cu_payout
} %⟩
⟨%- endmacro %⟩

⟨% macro arena_restore_campaign() -%⟩
⟨% if arena.\_camp %⟩
⟨% set campaign.seeds_suppressed = arena.\_camp.seeds_suppressed %⟩
⟨% set campaign.px_frozen = arena.\_camp.px_frozen %⟩
⟨% set campaign.boss_suppressed = arena.\_camp.boss_suppressed %⟩
⟨% set campaign.intervention_suppressed = arena.\_camp.intervention_suppressed %⟩
⟨% set campaign.cu_payout = arena.\_camp.cu_payout %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:ARENA_MODULE #⟩
⟨# LINT:ARENA_GUARDS #⟩
⟨% macro arena_guards_enable() -%⟩
⟪ arena_snapshot_campaign() ⟫
⟨# LINT:ARENA_NO_SEEDS #⟩
⟨% set campaign.seeds_suppressed = true %⟩
⟨# LINT:ARENA_NO_PARADOXON #⟩
⟨% set campaign.px_frozen = true %⟩
⟨# LINT:ARENA_NO_BOSS #⟩
⟨% set campaign.boss_suppressed = true %⟩
⟨# LINT:ARENA_NO_FR_INTERVENTION #⟩
⟨% set campaign.intervention_suppressed = true %⟩
⟨# LINT:ARENA_NO_CU_REWARD #⟩
⟨% set campaign.cu_payout = 0 %⟩
⟨%- endmacro %⟩

⟨% macro arena_guards_disable() -%⟩
⟨% set campaign.seeds_suppressed = false %⟩
⟨% set campaign.px_frozen = false %⟩
⟨% set campaign.boss_suppressed = false %⟩
⟨% set campaign.intervention_suppressed = false %⟩
⟨%- endmacro %⟩

⟨# LINT:ARENA_SINGLE_INSTANCE #⟩
⟨% macro start_pvp_arena(mode="duel", map="Magnet-Deck A", rounds=3,
time_limit_s=180, psi_policy="allowed", vehicle_policy="off",
feedback_intensity="low") -%⟩
⟨% if arena and arena.active %⟩
⟪ hud_tag('Arena bereits aktiv - beende aktuelles Match zuerst') ⟫
⟨% return %⟩
⟨% endif %⟩
⟪ arena_snapshot_state() ⟫
⟨% if campaign.team_size is defined %⟩
⟨% set team_size = campaign.team_size %⟩
⟨% else %⟩
⟨% set team_size = 5 %⟩
⟨% endif %⟩
⟨% set team_size = team_size|int %⟩
⟨% set large_team = team_size >= 3 %⟩
⟨% set cycle_s = large_team and 30 or none %⟩
⟨% set move_limit = large_team and 4 or none %⟩
⟨% set arena = {
'active': true, 'mode': mode, 'map': map, 'rounds_total': rounds,
'round': 0, 'time_limit_s': time_limit_s, 'psi_policy': psi_policy,
'vehicle_policy': vehicle_policy, 'feedback_intensity': feedback_intensity,
'score': {'A':0,'B':0}, 'oob_penalty': 1,
'team_size': team_size, 'large_team': large_team,
'cycle_s': cycle_s, 'cycle_remaining': cycle_s,
'move_limit': move_limit, 'moves_this_cycle': 0,
'cycle_count': 0,
'damage_dampener': {'mode': 'overflow_half', 'min_bonus': 1}
} %⟩
⟪ arena_budget_init(5) ⟫
⟪ arena_guards_enable() ⟫
⟪ hud_tag('Arena-Dämpfer aktiv - Exploding-Overflow wird halbiert (aufgerundet)') ⟫
⟨% if large_team %⟩
⟪ hud_tag('Großteam-Modus aktiv - 30s-Zyklus mit Move-Limit ' ~ move_limit ~ ' Aktionen.') ⟫
⟨% endif %⟩
⟪ arena_hud("INIT") ⟫
⟨%- endmacro %⟩

⟨% macro exit_pvp_arena() -%⟩
⟨% if arena.active %⟩
⟪ hud_tag('Arena Ende · Score A:' ~ arena.score.A ~ ' B:' ~ arena.score.B) ⟫
⟪ arena_log_result() ⟫
⟪ arena_restore_campaign() ⟫
⟪ arena_restore_state() ⟫
⟪ arena_guards_disable() ⟫
⟨% set arena = {'active': false} %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:ARENA_RULE_PENALTY #⟩
⟨% macro arena_penalty(team, reason, points=1) -%⟩
⟪ hud_tag('Arena-Penalty ' ~ team ~ ': -' ~ points ~ ' (' ~ reason ~ ')') ⟫
⟨% set arena.score = {
'A': arena.score.A - (points if team=='A' else 0),
'B': arena.score.B - (points if team=='B' else 0)
} %⟩
⟪ arena_hud('PENALTY') ⟫
⟨%- endmacro %⟩

⟨# LINT:ARENA_BUDGET #⟩
⟨% macro arena_budget_init(limit=5) -%⟩
⟨% set arena.budget_limit = limit %⟩
⟨% set arena.budget_used = 0 %⟩
⟪ hud_tag('Loadout-Budget: ' ~ limit) ⟫
⟨%- endmacro %⟩

⟨% macro arena_spend(points, team=None) -%⟩
⟨% set arena.budget_used = (arena.budget_used or 0) + points %⟩
⟨% if arena.budget_used > (arena.budget_limit or 5) %⟩
⟨% if team %⟩
⟪ arena_penalty(team, 'Budget überzogen') ⟫
⟨% else %⟩
⟪ hud_tag('Loadout-Budget überschritten - Aktion/Item blockiert') ⟫
⟨% endif %⟩
⟨% return %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:ARENA_AFK_GUARD #⟩
⟨% macro arena_mark_action() -%⟩
⟨% set arena.last_action_tick = arena.t_remaining or arena.time_limit_s %⟩
⟨% if arena.large_team %⟩
⟨% set moves = (arena.moves_this_cycle or 0) + 1 %⟩
⟨% set arena.moves_this_cycle = moves %⟩
⟨% set limit = arena.move_limit or moves %⟩
⟨% if moves <= limit %⟩
⟪ hud_ping('Move ' ~ moves ~ '/' ~ limit ~ ' · 30s-Zyklus läuft') ⟫
⟨% else %⟩
⟪ hud_tag('Move-Limit erreicht - wartet bis zum nächsten 30s-Zyklus.') ⟫
⟨% endif %⟩
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro arena_start_round() -%⟩
⟨% set arena.round = arena.round + 1 %⟩
⟨% set arena.t_remaining = arena.time_limit_s %⟩
⟨# Round-Reset: LP, SYS, PP, Cooldowns, Psi-Heat → Startwerte #⟩
⟨% for c in arena.combatants %⟩
⟨% set c.hp = c.hp_max %⟩
⟨% set c.sys_runtime = 0 %⟩
⟨% set c.pp = c.pp_max %⟩
⟨% set c.psi_heat = 0 %⟩
⟨% set c.cooldowns = {} %⟩
⟨% endfor %⟩
⟨% if arena.large_team and arena.cycle_s %⟩
⟨% set arena.cycle_remaining = arena.cycle_s %⟩
⟨% set arena.moves_this_cycle = 0 %⟩
⟨% endif %⟩
⟪ arena_hud("ROUND") ⟫
⟨%- endmacro %⟩

⟨% macro arena_tick(delta_s=10) -%⟩
⟨% set prev = arena.t_remaining or arena.time_limit_s %⟩
⟨% set arena.t_remaining = [prev - delta_s, 0]|max %⟩
⟨% if arena.large_team and arena.cycle_s %⟩
⟨% set cycle_prev = arena.cycle_remaining or arena.cycle_s %⟩
⟨% set cycle_now = [cycle_prev - delta_s, 0]|max %⟩
⟨% set arena.cycle_remaining = cycle_now %⟩
⟨% if cycle_now == 0 %⟩
⟨% set arena.moves_this_cycle = 0 %⟩
⟨% set arena.cycle_count = (arena.cycle_count or 0) + 1 %⟩
⟨% set arena.cycle_remaining = arena.cycle_s %⟩
⟪ hud_tag('30s-Zyklus reset - Moves 0/' ~ (arena.move_limit or '∞')) ⟫
⟨% endif %⟩
⟨% endif %⟩
⟨% if (prev - (arena.last_action_tick or prev)) >= 30 %⟩
⟪ hud_tag('Inaktivität erkannt - nächste OOB-Strafe +1') ⟫
⟨% set arena.oob_penalty = arena.oob_penalty + 1 %⟩
⟨% set arena.last_action_tick = arena.t_remaining %⟩
⟨% endif %⟩
⟪ arena_hud("TICK") ⟫
⟨% if arena.t_remaining == 0 %⟩ ⟪ arena_sudden_death() ⟫ ⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro arena_sudden_death() -%⟩
⟪ hud_tag('Sudden Death: Zonen schrumpfen, OOB-Schaden +' ~ arena.oob_penalty) ⟫
⟨% set arena.oob_penalty = arena.oob_penalty + 1 %⟩
⟨%- endmacro %⟩

⟨% macro arena_oob(hit_team) -%⟩
⟪ hud_tag('Grenzverletzung: Team ' ~ hit_team ~ ' erhält ' ~ arena.oob_penalty ~ ' Stun') ⟫
⟪ arena_apply_stun(hit_team, arena.oob_penalty) ⟫
⟪ arena_hud("OOB") ⟫
⟨%- endmacro %⟩

⟨# LINT:ARENA_TIEBREAK #⟩
⟨% macro arena_tiebreak(seconds=45) -%⟩
⟨% set arena.tiebreak = true %⟩
⟨% set arena.t_remaining = seconds %⟩
⟨% set arena.oob_penalty = arena.oob_penalty + 1 %⟩
⟪ hud_tag('Tiebreak - erster Stun gewinnt · Limit ' ~ seconds ~ 's') ⟫
⟪ arena_hud('TBREAK') ⟫
⟨%- endmacro %⟩

⟨# LINT:ARENA_MODE_CONTROL #⟩
⟨% macro arena_mode_control_tick(owner_team, tick=1) -%⟩
⟪ hud_tag('Control-Tick: +' ~ tick ~ ' → ' ~ owner_team) ⟫
⟪ arena_score(owner_team, tick) ⟫
⟨%- endmacro %⟩

⟨# LINT:ARENA_MODE_ELIMINATION #⟩
⟨% macro arena_elimination_down(team) -%⟩
⟪ hud_tag('Elimination: ' ~ team ~ ' down') ⟫
⟨# Optional: prüft hier Team-Wipe und ruft arena_match_won(other_team) #⟩
⟨%- endmacro %⟩

⟨% macro arena_end_round() -%⟩
⟪ hud_tag('Runde ' ~ arena.round ~ ' Ende · Score A:' ~ arena.score.A ~
' B:' ~ arena.score.B) ⟫
⟨% if arena.round >= arena.rounds_total %⟩
⟨% if arena.score.A == arena.score.B %⟩
⟪ arena_tiebreak(45) ⟫
⟨% return %⟩
⟨% endif %⟩
⟪ exit_pvp_arena() ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨# LINT:ARENA_LOADOUT_RULES #⟩
⟨% macro arena_loadout(policy="standard") -%⟩
⟨% set budget = arena.budget_limit or 5 %⟩
⟨% set proc = arena.proc_budget or budget %⟩
⟨% set artifact = arena.artifact_limit if arena.artifact_limit is not none else 1 %⟩
⟨% set tier = arena.tier or 1 %⟩
⟨% set psi_allowed = (arena.psi_policy == "allowed") %⟩
⟨% set vehicle_allowed = (arena.vehicle_policy in ["on", "rig"]) %⟩
⟨% set vehicle_label = (arena.vehicle_policy == "rig") and "Rig" or "ja" %⟩
⟪ hud_tag('Loadout: Tier ' ~ tier ~ ' · Budget ' ~ budget ~ ' · Proc ' ~ proc ~
' · Artefakte ' ~ artifact ~ ' · Psi ' ~ (psi_allowed and 'ja' or 'nein') ~
' · Fahrzeuge ' ~ (vehicle_allowed and vehicle_label or 'nein')) ⟫
⟨%- endmacro %⟩

⟨# LINT:ARENA_ACTIONS #⟩
⟨# LINT:ARENA_COMMS_REUSE #⟩
⟨% macro arena_action(actor, kind, target=None, device=None) -%⟩
⟨% if kind in ['hack','jam'] %⟩
⟨% if not device or device not in ['Comlink','Jammer','Terminal','Kabel','Konsole'] %⟩
⟪ arena_penalty(actor, 'Aktion blockiert - Gerät angeben (Comlink/Jammer/Terminal/Kabel/Konsole)') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% if kind == 'hack' and not target %⟩
⟪ arena_penalty(actor, 'Aktion blockiert - Schnittstelle benennen (Port/Buchse/Relais/Konsole)') ⟫
⟨% return %⟩
⟨% endif %⟩
⟨% set guard_device = {
'Comlink': 'Comlink',
'Jammer': 'JammerOverride',
'Terminal': 'Relais',
'Konsole': 'Relais',
'Kabel': 'Kabel'
}[device] %⟩
⟨% set guard_range = guard_device in ['Relais','Kabel'] and 0 or 2 %⟩
⟨% set comms_text = kind == 'hack'
and (actor ~ ' Remote-Hack via ' ~ device)
or ('Jammer-Impuls via ' ~ device)
%⟩
⟪ must_comms({
'device': guard_device,
'range_km': guard_range,
'jammer': kind == 'jam',
'relays': guard_device in ['Relais','JammerOverride'],
'text': comms_text
}) ⟫
⟨% endif %⟩
⟨% if kind == 'shot' %⟩
⟪ arena_resolve_shot(actor, target) ⟫
⟨% elif kind == 'psi' %⟩
⟪ arena_resolve_psi(actor, target) ⟫
⟨% elif kind == 'hack' %⟩
⟨% set hack_suffix = device in ['Terminal','Konsole','Kabel']
and '→ Deckungsstörung, Leitung gesichert'
or '→ Deckungsstörung, Funk stabil'
%⟩
⟪ hud_tag(actor ~ ' hackt via ' ~ device ~ ' ' ~ hack_suffix) ⟫
⟨% elif kind == 'jam' %⟩
⟪ hud_tag('Jammer aktiv - Comms gestört (≈ 2 km)') ⟫
⟨% endif %⟩
⟪ arena_mark_action() ⟫
⟨%- endmacro %⟩

⟨% macro arena_resolve_shot(actor, target) -%⟩
⟪ hud_tag(actor ~ ' feuert → ' ~ target ~ ' erhält 1 Stun (Exploding wie Kernregel)') ⟫
⟪ arena_apply_stun(target, 1) ⟫
⟨%- endmacro %⟩

⟨# LINT:ARENA_PSI_HINT #⟩
⟨% macro arena_resolve_psi(actor, target) -%⟩
⟨% if arena.psi_policy != 'allowed' %⟩
⟪ arena_penalty(actor, 'Psi verboten') ⟫
⟨% return %⟩
⟨% endif %⟩
⟪ hud_tag(actor ~ ' (Psi) → Stun ' ~ target ~ ' (Arena-Gitter: +SG, SYS/PP/Psi-Heat gelten)') ⟫
⟪ arena_apply_stun(target, 1) ⟫
⟨%- endmacro %⟩

⟨% macro arena_apply_stun(target, amount) -%⟩
⟪ hud_tag('Stun ' ~ target ~ ' +' ~ amount) ⟫
⟨%- endmacro %⟩

⟨# LINT:ARENA_LOG #⟩
⟨% macro arena_log_result() -%⟩
⟨% set entry = 'Arena · ' ~ arena.mode ~ ' · A:' ~ arena.score.A ~ ' B:' ~ arena.score.B %⟩
⟨% if kodex_log is defined %⟩
⟪ kodex_log(entry) ⟫
⟨% else %⟩
⟪ hud_tag('Kodex: ' ~ entry) ⟫
⟨% endif %⟩
⟨%- endmacro %⟩

⟨% macro arena_score(team, points=1) -%⟩
⟨% set arena.score = {
'A': arena.score.A + (points if team=='A' else 0),
'B': arena.score.B + (points if team=='B' else 0)
} %⟩
⟨% if arena.tiebreak %⟩
⟪ hud_tag('Tiebreak entschieden → Team ' ~ team ~ ' gewinnt') ⟫
⟪ exit_pvp_arena() ⟫
⟨% return %⟩
⟨% endif %⟩
⟪ arena_hud("SCORE") ⟫
⟨%- endmacro %⟩

⟨% macro arena_hud(phase="", style="diegetic") -%⟩
⟨% set debug = style == "debug" %⟩
⟨% set map_label = debug and "Map" or "Halle" %⟩
⟨% set round_label = debug and "R" or "Runde" %⟩
⟨% set time_label = debug and "T" or "Zeit" %⟩
⟨% set oob_label = debug and "OOB" or "Grenze" %⟩
⟨% set moves_label = debug and "MOV" or "Aktionen" %⟩
⟨% set cycle_label = debug and "CYCLE" or "Zyklus" %⟩
⟨% set phase_label = debug and "PHASE" or "Phase" %⟩
⟨% set segs = [
"ARENA·" ~ arena.mode|upper, " · " ~ map_label ~ " " ~ arena.map,
" · " ~ round_label ~ " " ~ arena.round ~ "/" ~ arena.rounds_total,
" · " ~ time_label ~ " " ~ (arena.t_remaining or arena.time_limit_s) ~ "s",
" · A:" ~ arena.score.A, " · B:" ~ arena.score.B,
" · " ~ oob_label ~ " " ~ arena.oob_penalty
] %⟩
⟨% if arena.large_team %⟩
⟨% set segs = segs + [
" · " ~ moves_label ~ " " ~ (arena.moves_this_cycle or 0) ~ "/" ~
(arena.move_limit or '∞'),
" · " ~ cycle_label ~ " " ~ (arena.cycle_remaining or arena.cycle_s or 0) ~ "s"
] %⟩
⟨% endif %⟩
⟨% if phase %⟩⟨% set segs = segs + [" · " ~ phase_label ~ ":" ~ phase] %⟩⟨% endif %⟩
`⟪ segs|join('') ⟫`
⟨%- endmacro %⟩

⟨# LINT:ARENA_ABORT #⟩
⟨% macro arena_abort() -%⟩
⟪ hud_tag('Arena abgebrochen - Zustand wiederhergestellt') ⟫
⟪ arena_restore_state() ⟫
⟪ arena_restore_campaign() ⟫
⟪ arena_guards_disable() ⟫
⟨% set arena = {'active': false} %⟩
⟨%- endmacro %⟩

⟨% macro arena_match_won(team) -%⟩
⟪ arena_score(team, 1) ⟫
⟪ arena_end_round() ⟫
⟨%- endmacro %⟩

⟨% macro start_pvp_duel(player1, player2, difficulty="normal") -%⟩
⟪ start_pvp_arena("duel") ⟫
⟨% set arena.teamA = [player1] %⟩
⟨% set arena.teamB = [player2] %⟩
⟪ arena_start_round() ⟫
⟨%- endmacro %⟩
