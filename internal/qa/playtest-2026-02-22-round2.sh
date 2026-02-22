#!/usr/bin/env bash
# ZEITRISS Playtest Suite Runde 2 — 2026-02-22
# Nach Fix: Save-Template v6 vollständig, Arena-Proben, Mindestlänge
set -euo pipefail
source ~/.openwebui_env
export OPENWEBUI_URL="http://localhost:3000"
export OPENWEBUI_API_KEY

OUTDIR="$(dirname "$0")/evidence/playtest-2026-02-22-r2"
mkdir -p "$OUTDIR"

api_chat() {
  local model="$1" messages="$2" label="$3"
  local outfile="$OUTDIR/${label}.md"
  echo "▶ $label ($model)..."
  RESULT=$(curl -s "$OPENWEBUI_URL/api/chat/completions" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$model\",\"messages\":$messages,\"temperature\":0.8,\"top_p\":0.9,\"frequency_penalty\":0.3,\"max_tokens\":8192,\"stream\":false}" 2>/dev/null)
  MSG=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('choices',[{}])[0].get('message',{}).get('content','ERROR'))" 2>/dev/null)
  COST=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('usage',{}).get('cost',0))" 2>/dev/null)
  TOKENS=$(echo "$RESULT" | python3 -c "import sys,json; u=json.load(sys.stdin).get('usage',{}); print(f\"in:{u.get('prompt_tokens',0)} out:{u.get('completion_tokens',0)}\")" 2>/dev/null)
  { echo "# $label"; echo "- **Model:** $model"; echo "- **Cost:** \$$COST"; echo "- **Tokens:** $TOKENS"; echo ""; echo "## Output"; echo ""; echo "$MSG"; } > "$outfile"
  echo "  ✅ done ($TOKENS, \$$COST)"
}

# ═══════════════════════════════════════════════════════════════
# TEST 1: Solo Klassisch — Voller Charakter-Erstellungsflow
# ═══════════════════════════════════════════════════════════════
MSGS='[{"role":"user","content":"Spiel starten (solo klassisch)"}]'
api_chat "zeitriss-v426-uncut-sonnet" "$MSGS" "01-klassisch-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS" "01-klassisch-deepseek"

# ═══════════════════════════════════════════════════════════════
# TEST 2: Mid-Campaign Save→Load Roundtrip (Sonnet)
# Erstelle Save, dann lade ihn in neuem Kontext
# ═══════════════════════════════════════════════════════════════
SAVE_JSON='{"save_version":6,"zr_version":"4.2.6","location":"HQ","phase":"core","character":{"id":"AGENT-RAVEN","name":"Raven","rank":"Operator II","level":7,"xp":880,"stress":0,"psi_heat":0,"cooldowns":{},"attributes":{"STR":4,"GES":6,"INT":5,"CHA":3,"TEMP":4,"SYS_max":5,"SYS_installed":5,"SYS_runtime":5,"SYS_used":3,"hp":13,"hp_max":13},"talents":["Schleichen II","Pistolenschütze","Systemzugang"],"skills":["Infiltration","Taktik"],"implants":[{"name":"Retina-HUD","sys_cost":0,"effect":"Standard-HUD"},{"name":"Reflex-Boost","sys_cost":1,"effect":"+1 Initiative"},{"name":"Tac-Comm Mk II","sys_cost":2,"effect":"Verschlüsselter Funk"}],"inventory":{"weapons":["Schallgedämpfte Pistole (SD)","Monofaser-Schwert"],"armor":["Kevlar-Komposit Stufe III"],"gadgets":["Jammer Mk II","Tarnoverlay","Faseroptik-Kamera"],"consumables":["Med-Patch x2","Stim-Injektor"],"special":["Notfall-Transponder"]},"stats":{"missions_completed":6,"deaths":1,"rifts_closed":1}},"campaign":{"episode":2,"mission_in_episode":1,"scene":0,"px":2,"mode":"preserve","rift_seeds":[{"id":"RIFT-022","epoch":"1943","label":"Normandie-Phantom","status":"open"}],"exfil":{"active":false,"armed":false,"hot":false,"ttl":0,"sweeps":0,"stress":0,"anchor":null,"alt_anchor":null}},"team":{"members":[{"id":"AGENT-RAVEN","callsign":"Raven"}]},"party":{"characters":[{"id":"AGENT-RAVEN","callsign":"Raven","psi_buffer":true,"has_psi":false}]},"loadout":{"AGENT-RAVEN":{"primary":"Schallgedämpfte Pistole (SD)","secondary":"Monofaser-Schwert","armor":"Kevlar-Komposit Stufe III","gear":["Jammer Mk II","Tarnoverlay","Faseroptik-Kamera","Med-Patch x2"]}},"economy":{"cu":4200,"wallets":{"AGENT-RAVEN":{"name":"Raven","balance":4200}}},"logs":{"hud":[],"trace":[],"artifact_log":[{"id":"A01","name":"Chrono-Splitter","mission_ref":"EP01-MS04","status":"equipped"}],"market":[],"offline":[],"kodex":[],"alias_trace":[],"squad_radio":[],"foreshadow":[],"fr_interventions":[],"arena_psi":[],"psi":[],"flags":{"runtime_version":"4.2.6","merge_conflicts":[],"platform_action_contract":{"action_mode":"uncut"},"chronopolis_unlocked":false}},"arc_dashboard":{"offene_seeds":[{"id":"RIFT-022","epoch":"1943","label":"Normandie-Phantom","status":"open"}],"fraktionen":{"ITI":2,"Ordo Mnemonika":0},"fragen":["Was verbirgt der Normandie-Phantom?"],"timeline":[{"id":"TL-EP1","epoch":"2000","label":"Olympia-Anomalie stabilisiert","stability":4}]},"ui":{"gm_style":"verbose","intro_seen":true,"suggest_mode":false,"action_mode":"uncut","contrast":"standard","badge_density":"standard","output_pace":"normal"},"arena":{"active":false,"phase":"idle","mode":"single","match_policy":"sim","previous_mode":null,"wins_player":0,"wins_opponent":0,"tier":1,"proc_budget":0,"artifact_limit":0,"loadout_budget":0,"phase_strike_tax":0,"damage_dampener":true,"team_size":1,"fee":0,"scenario":null,"started_episode":null,"last_reward_episode":null,"policy_players":[],"audit":[]}}'

MSGS_LOAD="[{\"role\":\"user\",\"content\":\"Spiel laden\"},{\"role\":\"assistant\",\"content\":\"Kodex: Load-Modus aktiv. Poste deinen Speicherstand als JSON.\"},{\"role\":\"user\",\"content\":$(echo "$SAVE_JSON" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")}]"
api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_LOAD" "02-load-roundtrip-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_LOAD" "02-load-roundtrip-deepseek"

# ═══════════════════════════════════════════════════════════════
# TEST 3: Gladiator-Kampf (Römisches Kolosseum, Zeitreise-Setting)
# ═══════════════════════════════════════════════════════════════
MSGS_GLAD='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Breacher Callsign: Titan. Level 3. STR 5, GES 4, INT 2, CHA 2, TEMP 3, SYS 3. HP 12/12. Monofaser-Schwert, Kevlar unter Tunika. Mission: Rom 80 n.Chr., Kolosseum. Undercover als Gladiator. Anomalie im Untergeschoss. Briefing abgeschlossen, du stehst im Tunnel unter der Arena."},
  {"role":"user","content":"Die Falltür über mir öffnet sich. Licht flutet rein. Das Publikum brüllt. Gegenüber steht ein Gladiator mit Netz und Dreizack — ein echter Retiarius. Ich ziehe mein Monofaser-Schwert (getarnt als Gladius) und gehe in Kampfstellung. LOS."}
]'
api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_GLAD" "03-gladiator-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_GLAD" "03-gladiator-deepseek"

# ═══════════════════════════════════════════════════════════════
# TEST 4: Gruppe Split — 2er-Gruppe splittet nach Mission
# ═══════════════════════════════════════════════════════════════
MSGS_SPLIT='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Gruppe aktiv: Nova (Host, Level 8, Ghost) + Viper (Level 6, Analyst). Koop-Mission EP2 MS3 abgeschlossen. Alle Ziele erreicht. Stress Nova 2, Viper 1. Px 3/5. CU: Nova 3500, Viper 2200. Beide im HQ."},
  {"role":"user","content":"Viper verlässt die Gruppe. Splittet die Saves — ich will meinen Solo-Save für Nova und einen separaten für Viper. Beide als JSON."}
]'
api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_SPLIT" "04-group-split-sonnet"

# ═══════════════════════════════════════════════════════════════
# TEST 5: Offline-Modus — Comlink-Ausfall während Mission
# ═══════════════════════════════════════════════════════════════
MSGS_OFFLINE='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Ghost Callsign: Specter. Level 4. Mission: Tschernobyl 1986, Nacht vor der Explosion. Szene 6/12. COMMS OK. Stress 3. Ein Jammer-Feld umgibt den Reaktorkomplex."},
  {"role":"user","content":"Ich betrete den Reaktorkontrollraum. Der Jammer schlägt voll zu — Comlink tot, Kodex weg. Was passiert mit meinem HUD?"}
]'
api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_OFFLINE" "05-offline-tschernobyl-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_OFFLINE" "05-offline-tschernobyl-deepseek"

# ═══════════════════════════════════════════════════════════════
# TEST 6: ClusterCreate — Px erreicht 5
# ═══════════════════════════════════════════════════════════════
MSGS_CLUSTER='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Agent Wraith, Level 9, TEMP 6. Episode 2 Mission 8 Debrief. Mission erfolgreich. Px steht auf 4/5, nächste erfolgreiche Mission löst +1 aus (TEMP 4-6 = alle 4 Missionen). Dies ist Mission 8 = genau der 4er-Trigger."},
  {"role":"user","content":"Debrief starten. Wenn Px auf 5 steigt, will ich ClusterCreate sehen."}
]'
api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_CLUSTER" "06-clustercreate-sonnet"

# ═══════════════════════════════════════════════════════════════
# TEST 7: Hacking + Kodex-Commentary (Cyber-Noir)
# ═══════════════════════════════════════════════════════════════
MSGS_HACK='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Analyst Callsign: Zero. Level 5. INT 6, SYS 5. Mission: Tokio 2089. Firmen-Mainframe infiltrieren. Szene 4/12. Du sitzt vor einem Terminal im Serverraum. Wache patrouilliert in 90 Sekunden. Comlink aktiv."},
  {"role":"user","content":"Hacking starten. Ich will in den verschlüsselten Sektor — Sicherheitsstufe Rot. Alle Tricks die ich habe."}
]'
api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_HACK" "07-hacking-tokio-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_HACK" "07-hacking-tokio-deepseek"

echo ""
echo "═══════════════════════════════════════"
echo "  Runde 2 abgeschlossen!"
echo "  Output: $OUTDIR/"
echo "═══════════════════════════════════════"
ls -la "$OUTDIR/"
