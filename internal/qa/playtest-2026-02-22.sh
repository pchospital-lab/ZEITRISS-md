#!/usr/bin/env bash
# ZEITRISS Playtest Suite — 2026-02-22
# Testet verschiedene Szenarien gegen alle drei Modelle
set -euo pipefail
source ~/.openwebui_env
export OPENWEBUI_URL="http://localhost:3000"
export OPENWEBUI_API_KEY

OUTDIR="$(dirname "$0")/evidence/playtest-2026-02-22"
mkdir -p "$OUTDIR"

api_chat() {
  local model="$1" messages="$2" label="$3"
  local outfile="$OUTDIR/${label}.md"
  
  echo "▶ $label ($model)..."
  
  RESULT=$(curl -s "$OPENWEBUI_URL/api/chat/completions" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"$model\",
      \"messages\": $messages,
      \"temperature\": 0.8,
      \"top_p\": 0.9,
      \"frequency_penalty\": 0.3,
      \"max_tokens\": 8192,
      \"stream\": false
    }" 2>/dev/null)
  
  MSG=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('choices',[{}])[0].get('message',{}).get('content','ERROR'))" 2>/dev/null)
  COST=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('usage',{}).get('cost',0))" 2>/dev/null)
  TOKENS=$(echo "$RESULT" | python3 -c "import sys,json; u=json.load(sys.stdin).get('usage',{}); print(f\"in:{u.get('prompt_tokens',0)} out:{u.get('completion_tokens',0)}\")" 2>/dev/null)
  
  {
    echo "# $label"
    echo "- **Model:** $model"
    echo "- **Cost:** \$$COST"
    echo "- **Tokens:** $TOKENS"
    echo ""
    echo "## Output"
    echo ""
    echo "$MSG"
  } > "$outfile"
  
  echo "  ✅ done ($TOKENS, \$$COST) → $outfile"
}

# ═══════════════════════════════════════════════════════════════
# TEST 1: Charakter-Erstellung + erste Kampfszene (alle 3 Modelle)
# ═══════════════════════════════════════════════════════════════
MSGS_COMBAT='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Ghost gewählt. Callsign: Phantom. Level 1. STR 2, GES 5, INT 3, CHA 3, TEMP 3, SYS 4. Monofaser-Schwert, Pistole (12/12), Jammer (3x), Tarnoverlay. Mission: Kowloon 1993, Triadenunterwanderung."},
  {"role":"user","content":"Ich schleiche durch die Gasse. Erster Feindkontakt: Monofaser-Schwert ziehen, von oben angreifen. Filmisch bitte."}
]'

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_COMBAT" "01-combat-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_COMBAT" "01-combat-deepseek"

# ═══════════════════════════════════════════════════════════════
# TEST 2: Debrief + Score-Screen + Save (Sonnet)
# ═══════════════════════════════════════════════════════════════
MSGS_DEBRIEF='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Agent Nova, Level 4, XP 680/800. Episode 1 Mission 5 abgeschlossen. Alle Ziele erreicht, 2 Feinde neutralisiert, Archivmodul gesichert. Keine Zivilopfer, Zeitlinie stabil. Stress 3, Px 4/5. Economy: 1800 CU. Jetzt im HQ."},
  {"role":"user","content":"Debrief starten. Zeig mir den Score-Screen und dann !save"}
]'

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_DEBRIEF" "02-debrief-save-sonnet"

# ═══════════════════════════════════════════════════════════════
# TEST 3: Save laden + Gruppen-Merge (2 Saves zusammenführen)
# ═══════════════════════════════════════════════════════════════
MSGS_MERGE='[
  {"role":"user","content":"Spiel laden"},
  {"role":"assistant","content":"Kodex: Load-Modus aktiv. Poste 1-N Speicherstände (Solo oder Gruppe). \"Fertig\" startet den Merge."},
  {"role":"user","content":"{\"save_version\":6,\"zr_version\":\"4.2.6\",\"location\":\"HQ\",\"phase\":\"core\",\"character\":{\"id\":\"AGENT-01\",\"name\":\"Nova\",\"level\":8,\"xp\":950,\"stress\":0,\"psi_heat\":0,\"cooldowns\":{},\"attributes\":{\"STR\":5,\"GES\":6,\"INT\":4,\"CHA\":3,\"TEMP\":4,\"SYS_max\":5,\"SYS_installed\":5,\"SYS_runtime\":5,\"SYS_used\":5}},\"campaign\":{\"episode\":2,\"scene\":0,\"px\":3,\"exfil\":{\"active\":false,\"armed\":false,\"hot\":false,\"ttl\":0,\"sweeps\":0,\"stress\":0,\"anchor\":null,\"alt_anchor\":null}},\"team\":{\"members\":[]},\"party\":{\"characters\":[]},\"loadout\":{},\"economy\":{\"cu\":3500,\"wallets\":{\"AGENT-01\":{\"name\":\"Nova\",\"balance\":3500}}},\"logs\":{\"hud\":[],\"trace\":[],\"artifact_log\":[],\"market\":[],\"offline\":[],\"kodex\":[],\"alias_trace\":[],\"squad_radio\":[],\"foreshadow\":[],\"fr_interventions\":[],\"arena_psi\":[],\"psi\":[],\"flags\":{\"runtime_version\":\"4.2.6\",\"merge_conflicts\":[],\"platform_action_contract\":{\"action_mode\":\"uncut\"}}},\"arc_dashboard\":{\"offene_seeds\":[],\"fraktionen\":{},\"fragen\":[],\"timeline\":[]},\"ui\":{\"gm_style\":\"verbose\",\"intro_seen\":true,\"suggest_mode\":false,\"action_mode\":\"uncut\",\"contrast\":\"standard\",\"badge_density\":\"standard\",\"output_pace\":\"normal\"},\"arena\":{\"active\":false,\"phase\":\"idle\",\"mode\":\"single\",\"match_policy\":\"sim\",\"previous_mode\":null,\"wins_player\":0,\"wins_opponent\":0,\"tier\":1,\"proc_budget\":0,\"artifact_limit\":0,\"loadout_budget\":0,\"phase_strike_tax\":0,\"damage_dampener\":true,\"team_size\":1,\"fee\":0,\"scenario\":null,\"started_episode\":null,\"last_reward_episode\":null,\"policy_players\":[],\"audit\":[]}}"},
  {"role":"assistant","content":"Kodex: Save 1 erkannt — Agent Nova, Level 8, Episode 2. Poste weitere Saves oder sage \"Fertig\"."},
  {"role":"user","content":"{\"save_version\":6,\"zr_version\":\"4.2.6\",\"location\":\"HQ\",\"phase\":\"core\",\"character\":{\"id\":\"AGENT-02\",\"name\":\"Viper\",\"level\":6,\"xp\":720,\"stress\":0,\"psi_heat\":0,\"cooldowns\":{},\"attributes\":{\"STR\":3,\"GES\":4,\"INT\":5,\"CHA\":4,\"TEMP\":5,\"SYS_max\":4,\"SYS_installed\":4,\"SYS_runtime\":4,\"SYS_used\":4}},\"campaign\":{\"episode\":1,\"scene\":0,\"px\":2,\"exfil\":{\"active\":false,\"armed\":false,\"hot\":false,\"ttl\":0,\"sweeps\":0,\"stress\":0,\"anchor\":null,\"alt_anchor\":null}},\"team\":{\"members\":[]},\"party\":{\"characters\":[]},\"loadout\":{},\"economy\":{\"cu\":2200,\"wallets\":{\"AGENT-02\":{\"name\":\"Viper\",\"balance\":2200}}},\"logs\":{\"hud\":[],\"trace\":[],\"artifact_log\":[],\"market\":[],\"offline\":[],\"kodex\":[],\"alias_trace\":[],\"squad_radio\":[],\"foreshadow\":[],\"fr_interventions\":[],\"arena_psi\":[],\"psi\":[],\"flags\":{\"runtime_version\":\"4.2.6\",\"merge_conflicts\":[],\"platform_action_contract\":{\"action_mode\":\"uncut\"}}},\"arc_dashboard\":{\"offene_seeds\":[],\"fraktionen\":{},\"fragen\":[],\"timeline\":[]},\"ui\":{\"gm_style\":\"verbose\",\"intro_seen\":true,\"suggest_mode\":false,\"action_mode\":\"uncut\",\"contrast\":\"standard\",\"badge_density\":\"standard\",\"output_pace\":\"normal\"},\"arena\":{\"active\":false,\"phase\":\"idle\",\"mode\":\"single\",\"match_policy\":\"sim\",\"previous_mode\":null,\"wins_player\":0,\"wins_opponent\":0,\"tier\":1,\"proc_budget\":0,\"artifact_limit\":0,\"loadout_budget\":0,\"phase_strike_tax\":0,\"damage_dampener\":true,\"team_size\":1,\"fee\":0,\"scenario\":null,\"started_episode\":null,\"last_reward_episode\":null,\"policy_players\":[],\"audit\":[]}}"},
  {"role":"assistant","content":"Kodex: Save 2 erkannt — Agent Viper, Level 6, Episode 1."},
  {"role":"user","content":"Fertig. Merge starten, Nova ist Host."}
]'

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_MERGE" "03-merge-sonnet"

# ═══════════════════════════════════════════════════════════════
# TEST 4: High-Level Content — Level 500 Charakter, Chronopolis
# ═══════════════════════════════════════════════════════════════
MSGS_HIGHLVL='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Veteran-Chrononaut Axiom. Level 512, XP 48200/50000. TEMP 13, STR 12, GES 14, INT 11, CHA 8, SYS 12. Explodierende W10. Heldenwürfel aktiv. Chronopolis freigeschaltet. 3 offene Rift-Seeds. Px 4/5. 45000 CU. Ausrüstung: Resonanz-Katana (Artefakt), Phasen-Schild Mk IV, Chrono-Impuls-Granaten (5x), Taktischer Exo-Suit. Implantate: Synaptischer Boost III, Zeitstrom-Resonator. Im HQ."},
  {"role":"user","content":"Ab nach Chronopolis. Ich will auf dem Markt was kaufen und dann in die Arena — PvP Tier 5."}
]'

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_HIGHLVL" "04-highlvl-chronopolis-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_HIGHLVL" "04-highlvl-chronopolis-deepseek"

# ═══════════════════════════════════════════════════════════════
# TEST 5: PvP Arena — Kampf + Kodex-Commentary
# ═══════════════════════════════════════════════════════════════
MSGS_PVP='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Agent Specter, Level 15. Arena Tier 3 gestartet. Gegner: Shadow (NPC, Level 14, Psi-Spezialist). Arena-Zone: Combat. Gebühr 500 CU bezahlt. Specter: Resonanz-Schwert + Taktik-Schild. Shadow: Psi-Peitsche + Reflex-Armor."},
  {"role":"user","content":"Runde 1: Ich stürme vor, Resonanz-Schwert-Hieb auf Shadow. Volle Offensive."}
]'

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_PVP" "05-pvp-arena-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_PVP" "05-pvp-arena-deepseek"

# ═══════════════════════════════════════════════════════════════
# TEST 6: Rift-Mission mit Paramonster (Sonnet)
# ═══════════════════════════════════════════════════════════════
MSGS_RIFT='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Agent Wraith, Level 11. Episode 2 beendet. ClusterCreate hat 2 Rift-Seeds erzeugt: RIFT-033 (1888 London, Mothman-Sichtung) und RIFT-041 (1947 Roswell, Nightcrawler-Anomalie). Px zurückgesetzt auf 0. Im HQ."},
  {"role":"user","content":"Rift-Mission starten: RIFT-033, London 1888. Mothman jagen. Ich will das Casefile-Format mit drei Akten."}
]'

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_RIFT" "06-rift-mothman-sonnet"

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
echo ""
echo "═══════════════════════════════════════"
echo "  Alle Tests abgeschlossen!"
echo "  Output: $OUTDIR/"
echo "═══════════════════════════════════════"
ls -la "$OUTDIR/"
