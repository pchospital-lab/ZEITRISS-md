# 04-group-split-sonnet
- **Model:** zeitriss-v426-uncut-sonnet
- **Cost:** $0.043809
- **Tokens:** in:5723 out:1776

## Output

# SPLIT-PROTOKOLL

`Kodex: Gruppenauflösung erkannt. Trenne Charakterdaten. Erstelle zwei Solo-Saves.`

---

## SAVE 1 — NOVA (Solo)

```json
{
  "save_version": 6, "zr_version": "4.2.6",
  "location": "HQ", "phase": "core",
  "character": {
    "id": "CHR-NOVA", "name": "Nova", "rank": "Ghost", "level": 8, "xp": 0,
    "stress": 2, "psi_heat": 0, "cooldowns": {},
    "attributes": { "STR":0,"GES":0,"INT":0,"CHA":0,"TEMP":0,
      "SYS_max":0,"SYS_installed":0,"SYS_runtime":0,"SYS_used":0,"hp":0,"hp_max":0 },
    "talents": [], "skills": [], "implants": [],
    "inventory": { "weapons":[],"armor":[],"gadgets":[],"consumables":[],"special":[] },
    "stats": { "missions_completed":13,"deaths":0,"rifts_closed":0 }
  },
  "campaign": {
    "episode":2,"mission_in_episode":3,"scene":12,"px":3,"mode":"preserve",
    "rift_seeds":[], "exfil":{"active":false,"armed":false,"hot":false,
      "ttl":0,"sweeps":0,"stress":0,"anchor":null,"alt_anchor":null}
  },
  "team": {"members":[]}, "party": {"characters":[]}, "loadout": {},
  "economy": {"cu":3500,"wallets":{"nova":3500}},
  "logs": {
    "hud":[],"trace":[],"artifact_log":[],"market":[],"offline":[],
    "kodex":[],"alias_trace":[],"squad_radio":[],"foreshadow":[],
    "fr_interventions":[],"arena_psi":[],"psi":[],
    "flags": {"runtime_version":"4.2.6","merge_conflicts":[],
      "platform_action_contract":{"action_mode":"uncut"}}
  },
  "arc_dashboard": {"offene_seeds":[],"fraktionen":{},"fragen":[],"timeline":[]},
  "ui": {"gm_style":"verbose","intro_seen":true,"suggest_mode":false,
    "action_mode":"uncut","contrast":"standard","badge_density":"standard",
    "output_pace":"normal"},
  "arena": {"active":false,"phase":"idle","mode":"single","match_policy":"sim",
    "previous_mode":null,"wins_player":0,"wins_opponent":0,"tier":1,
    "proc_budget":0,"artifact_limit":0,"loadout_budget":0,"phase_strike_tax":0,
    "damage_dampener":true,"team_size":1,"fee":0,"scenario":null,
    "started_episode":null,"last_reward_episode":null,"policy_players":[],"audit":[]}
}
```

---

## SAVE 2 — VIPER (Solo)

```json
{
  "save_version": 6, "zr_version": "4.2.6",
  "location": "HQ", "phase": "core",
  "character": {
    "id": "CHR-VIPER", "name": "Viper", "rank": "Analyst", "level": 6, "xp": 0,
    "stress": 1, "psi_heat": 0, "cooldowns": {},
    "attributes": { "STR":0,"GES":0,"INT":0,"CHA":0,"TEMP":0,
      "SYS_max":0,"SYS_installed":0,"SYS_runtime":0,"SYS_used":0,"hp":0,"hp_max":0 },
    "talents": [], "skills": [], "implants": [],
    "inventory": { "weapons":[],"armor":[],"gadgets":[],"consumables":[],"special":[] },
    "stats": { "missions_completed":13,"deaths":0,"rifts_closed":0 }
  },
  "campaign": {
    "episode":2,"mission_in_episode":3,"scene":12,"px":3,"mode":"preserve",
    "rift_seeds":[], "exfil":{"active":false,"armed":false,"hot":false,
      "ttl":0,"sweeps":0,"stress":0,"anchor":null,"alt_anchor":null}
  },
  "team": {"members":[]}, "party": {"characters":[]}, "loadout": {},
  "economy": {"cu":2200,"wallets":{"viper":2200}},
  "logs": {
    "hud":[],"trace":[],"artifact_log":[],"market":[],"offline":[],
    "kodex":[],"alias_trace":[],"squad_radio":[],"foreshadow":[],
    "fr_interventions":[],"arena_psi":[],"psi":[],
    "flags": {"runtime_version":"4.2.6","merge_conflicts":[],
      "platform_action_contract":{"action_mode":"uncut"}}
  },
  "arc_dashboard": {"offene_seeds":[],"fraktionen":{},"fragen":[],"timeline":[]},
  "ui": {"gm_style":"verbose","intro_seen":true,"suggest_mode":false,
    "action_mode":"uncut","contrast":"standard","badge_density":"standard",
    "output_pace":"normal"},
  "arena": {"active":false,"phase":"idle","mode":"single","match_policy":"sim",
    "previous_mode":null,"wins_player":0,"wins_opponent":0,"tier":1,
     "proc_budget":0,"artifact_limit":0,"loadout_budget":0,"phase_strike_tax":0,
    "damage_dampener":true,"team_size":1,"fee":0,"scenario":null,
    "started_episode":null,"last_reward_episode":null,"policy_players":[],"audit":[]}
}
```

---

`Kodex: Split abgeschlossen. Nova-Save und Viper-Save isoliert. Px 3/5 in beiden Saves gespiegelt — Chronologie bleibt konsistent. Gruppenkanal geschlossen.`

**Beide Saves stehen auf EP2 · MS3 abgeschlossen · HQ · Solo.**
Px und Missionsstand sind identisch übertragen — jeder Charakter trägt die gemeinsame Geschichte mit, geht ab jetzt eigene Wege.

---

**Wie weiter?**
1. **Nova-Session starten** — Lade Nova-Save, weiter im HQ
2. **Viper-Session starten** — Lade Viper-Save, weiter im HQ
3. **Attribute/Ausrüstung nachtragen** — Fehlende Charakterdaten für einen der beiden ergänzen
4. **Freie Aktion**
