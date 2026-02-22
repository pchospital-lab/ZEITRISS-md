#!/usr/bin/env bash
# ZEITRISS Deep Playtest — Modellvergleich + Cross-Model + Grupendynamik
set -euo pipefail
source ~/.openwebui_env
export OPENWEBUI_URL="http://localhost:3000"
export OPENWEBUI_API_KEY

OUTDIR="$(dirname "$0")/evidence/playtest-2026-02-22-deep"
mkdir -p "$OUTDIR"

api_chat() {
  local model="$1" messages="$2" label="$3"
  local outfile="$OUTDIR/${label}.md"
  echo "▶ $label..."
  RESULT=$(curl -s --max-time 180 "$OPENWEBUI_URL/api/chat/completions" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$model\",\"messages\":$messages,\"temperature\":0.8,\"top_p\":0.9,\"frequency_penalty\":0.3,\"max_tokens\":8192,\"stream\":false}" 2>/dev/null)
  if [ -z "$RESULT" ]; then
    echo "  ⏱️ TIMEOUT" && echo "# $label\n- TIMEOUT" > "$outfile" && return
  fi
  MSG=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('choices',[{}])[0].get('message',{}).get('content','ERROR'))" 2>/dev/null || echo "PARSE ERROR")
  COST=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('usage',{}).get('cost',0))" 2>/dev/null || echo "?")
  TOKENS=$(echo "$RESULT" | python3 -c "import sys,json; u=json.load(sys.stdin).get('usage',{}); print(f\"in:{u.get('prompt_tokens',0)} out:{u.get('completion_tokens',0)}\")" 2>/dev/null || echo "?")
  { echo "# $label"; echo "- **Model:** $model"; echo "- **Cost:** \$$COST"; echo "- **Tokens:** $TOKENS"; echo ""; echo "## Output"; echo ""; echo "$MSG"; } > "$outfile"
  echo "  ✅ ($TOKENS, \$$COST)"
}

# ═══════════════════════════════════════════════════════════════
# 5er-Gruppe Lvl 89 Save (gemeinsam genutzt für alle Tests)
# ═══════════════════════════════════════════════════════════════
GROUP_SAVE='{"save_version":6,"zr_version":"4.2.6","location":"HQ","phase":"core","character":{"id":"AGENT-HAWK","name":"Hawk","rank":"Commander","level":89,"xp":42100,"stress":0,"psi_heat":0,"cooldowns":{},"attributes":{"STR":9,"GES":11,"INT":8,"CHA":6,"TEMP":8,"SYS_max":8,"SYS_installed":8,"SYS_runtime":8,"SYS_used":6,"hp":28,"hp_max":28},"modes":["mission_focus","covert_ops_technoir"],"self_reflection":true,"has_psi":true,"psi_buffer":true,"talents":["Scharfschütze III","Taktiker II","Systemzugang II","Zeitinstinkt"],"skills":["CQB","Infiltration","Sprengstoff","Psi-Fokus"],"implants":[{"name":"Retina-HUD Mk III","sys_cost":0,"effect":"Erweitertes HUD + Thermalsicht"},{"name":"Synaptischer Boost III","sys_cost":2,"effect":"+2 Initiative, +1 INT-Proben"},{"name":"Reflex-Enhancer Mk II","sys_cost":2,"effect":"+2 GES bei Ausweichen"},{"name":"Chrono-Resonator","sys_cost":2,"effect":"Px-Warnung, TEMP-Proben +1"}],"inventory":{"weapons":["Resonanz-Sniper Mk IV (2W10+4)","Monofaser-Katana (1W10+3)","Tac-Pistole SD Mk III (1W10+2)"],"armor":["Exo-Komposit Stufe V (Rüstung 6)"],"gadgets":["Chrono-Jammer Mk III","Holo-Dekoy","Nano-Medikit x3","Phasen-Granate x2"],"consumables":["Stim-Injektor x2","Trauma-Kit"],"special":["Notfall-Transponder Mk II","Artefakt: Zeitstrom-Linse"]},"stats":{"missions_completed":84,"deaths":3,"rifts_closed":12,"shots_fired":847}},"campaign":{"episode":9,"mission_in_episode":4,"scene":0,"px":4,"mode":"preserve","rift_seeds":[{"id":"RIFT-088","epoch":"1918","label":"Verdun-Phantom — Grabenghost","status":"open"},{"id":"RIFT-091","epoch":"2145","label":"Mars-Kolonie Exodus — Zeitfraß","status":"open"},{"id":"RIFT-094","epoch":"1347","label":"Schwarzer-Tod-Anomalie — Pestdoktor","status":"open"}],"exfil":{"active":false,"armed":false,"hot":false,"ttl":0,"sweeps":0,"stress":0,"anchor":null,"alt_anchor":null}},"team":{"members":[{"id":"AGENT-HAWK","callsign":"Hawk"},{"id":"AGENT-VENOM","callsign":"Venom"},{"id":"AGENT-IRIS","callsign":"Iris"},{"id":"AGENT-GHOST","callsign":"Ghost"},{"id":"AGENT-BYTE","callsign":"Byte"}]},"party":{"characters":[{"id":"AGENT-HAWK","callsign":"Hawk","level":89,"psi_buffer":true,"has_psi":true},{"id":"AGENT-VENOM","callsign":"Venom","level":85,"psi_buffer":true,"has_psi":false},{"id":"AGENT-IRIS","callsign":"Iris","level":91,"psi_buffer":true,"has_psi":true},{"id":"AGENT-BYTE","callsign":"Byte","level":82,"psi_buffer":true,"has_psi":false},{"id":"AGENT-GHOST","callsign":"Ghost","level":87,"psi_buffer":true,"has_psi":false}]},"loadout":{"AGENT-HAWK":{"primary":"Resonanz-Sniper Mk IV","secondary":"Monofaser-Katana","armor":"Exo-Komposit V","gear":["Chrono-Jammer III","Holo-Dekoy","Nano-Medikit x3"]},"AGENT-VENOM":{"primary":"Schwere Schrotflinte Mk III","secondary":"Vibro-Axt","armor":"Titan-Platte IV","gear":["Breaching-Charge x3","Rauchgranate x4"]},"AGENT-IRIS":{"primary":"Psi-Lanze","secondary":"Neuraltoxin-Pistole","armor":"Reflex-Weave III","gear":["Psi-Fokus-Kristall","Scanner Mk III"]},"AGENT-BYTE":{"primary":"Tac-SMG SD","secondary":"Hacking-Rig","armor":"Stealth-Suit III","gear":["Terminal-Cracker","Jammer Mk III","Drohne Typ-C"]},"AGENT-GHOST":{"primary":"Armbrust SD Mk III","secondary":"Monofaser-Schwert","armor":"Chamäleon-Mantel IV","gear":["Tarnoverlay Mk III","Dietrich-Set Pro","Gift-Injektor x2"]}},"economy":{"cu":45000,"wallets":{"AGENT-HAWK":{"name":"Hawk","balance":12000},"AGENT-VENOM":{"name":"Venom","balance":9500},"AGENT-IRIS":{"name":"Iris","balance":11000},"AGENT-BYTE":{"name":"Byte","balance":7500},"AGENT-GHOST":{"name":"Ghost","balance":5000}}},"logs":{"hud":[],"trace":[],"artifact_log":[{"id":"A12","name":"Zeitstrom-Linse","mission_ref":"EP07-MS02","status":"equipped"},{"id":"A08","name":"Grabengeist-Fragment","mission_ref":"EP05-MS06","status":"archived"}],"market":[],"offline":[],"kodex":[],"alias_trace":[],"squad_radio":[],"foreshadow":[],"fr_interventions":[{"ts":"2025-12-01T14:00:00Z","faction":"Ordo Mnemonika","event":"Warnung","effect":"-1 Stability EP8"}],"arena_psi":[],"psi":[],"flags":{"runtime_version":"4.2.6","merge_conflicts":[],"platform_action_contract":{"action_mode":"uncut"},"chronopolis_unlocked":true,"chronopolis_unlock_level":10}},"arc_dashboard":{"offene_seeds":[{"id":"RIFT-088","epoch":"1918","label":"Verdun-Phantom","status":"open"},{"id":"RIFT-091","epoch":"2145","label":"Mars-Exodus","status":"open"},{"id":"RIFT-094","epoch":"1347","label":"Pestdoktor","status":"open"}],"fraktionen":{"ITI":8,"Ordo Mnemonika":-2,"Kausalklingen":1},"fragen":["Wer steckt hinter den Mars-Anomalien?","Verbindung Pestdoktor ↔ Ordo?"],"timeline":[{"id":"TL-EP1","epoch":"2000","label":"Olympia stabilisiert","stability":4},{"id":"TL-EP3","epoch":"1969","label":"Apollo 11 gesichert","stability":3},{"id":"TL-EP5","epoch":"1945","label":"Hiroshima-Riss geschlossen","stability":4},{"id":"TL-EP7","epoch":"2089","label":"Tokio-Firewall intakt","stability":2}]},"ui":{"gm_style":"verbose","intro_seen":true,"suggest_mode":false,"action_mode":"uncut","contrast":"standard","badge_density":"standard","output_pace":"normal"},"arena":{"active":false,"phase":"completed","mode":"squad","match_policy":"sim","previous_mode":"preserve","wins_player":14,"wins_opponent":6,"tier":4,"proc_budget":0,"artifact_limit":2,"loadout_budget":8000,"phase_strike_tax":2,"damage_dampener":true,"team_size":5,"fee":1500,"scenario":null,"started_episode":9,"last_reward_episode":8,"policy_players":[{"id":"AGENT-HAWK","role":"sniper"},{"id":"AGENT-VENOM","role":"tank"},{"id":"AGENT-IRIS","role":"psi"},{"id":"AGENT-BYTE","role":"hacker"},{"id":"AGENT-GHOST","role":"assassin"}],"audit":[]}}'

SAVE_ESCAPED=$(echo "$GROUP_SAVE" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")

# ═══════════════════════════════════════════════════════════════
# TEST 1: 5er-Gruppe Load + Rift-Boss (alle 3 Modelle)
# Gleicher Save, gleicher Prompt — direkter Vergleich
# ═══════════════════════════════════════════════════════════════
MSGS_RIFT="[
  {\"role\":\"user\",\"content\":\"Spiel laden\"},
  {\"role\":\"assistant\",\"content\":\"Kodex: Load-Modus aktiv. Poste Speicherstand.\"},
  {\"role\":\"user\",\"content\":$SAVE_ESCAPED},
  {\"role\":\"assistant\",\"content\":\"Kodex: Gruppe geladen. Hawk (Host, L89), Venom (L85), Iris (L91), Byte (L82), Ghost (L87). Episode 9. 3 offene Rift-Seeds. Px 4/5. Chronopolis freigeschaltet. HQ bereit.\"},
  {\"role\":\"user\",\"content\":\"Rift starten: RIFT-094 — Schwarzer-Tod-Anomalie, 1347. Der Pestdoktor. Volle Gruppe, Casefile-Format. Das wird ein harter Kampf.\"}
]"

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_RIFT" "01-5er-rift-boss-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_RIFT" "01-5er-rift-boss-deepseek"
api_chat "zeitriss-v426-uncut-qwen" "$MSGS_RIFT" "01-5er-rift-boss-qwen"

# ═══════════════════════════════════════════════════════════════
# TEST 2: Gleiche Gruppe — PvP Arena Tier 4 Squad
# ═══════════════════════════════════════════════════════════════
MSGS_ARENA="[
  {\"role\":\"user\",\"content\":\"Spiel laden\"},
  {\"role\":\"assistant\",\"content\":\"Kodex: Load-Modus aktiv.\"},
  {\"role\":\"user\",\"content\":$SAVE_ESCAPED},
  {\"role\":\"assistant\",\"content\":\"Kodex: Gruppe geladen. 5 Agenten, EP9, HQ.\"},
  {\"role\":\"user\",\"content\":\"Arena Tier 4 starten. Squad-Match 5v5. Volle Mannschaft rein. Gebühr zahlen. Ich will den Kampf sehen — alle 5 Agenten koordiniert.\"}
]"

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_ARENA" "02-5er-arena-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_ARENA" "02-5er-arena-deepseek"

# ═══════════════════════════════════════════════════════════════
# TEST 3: Cross-Model Save — DeepSeek erstellt Save, Sonnet lädt
# ═══════════════════════════════════════════════════════════════
MSGS_DS_SAVE='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Breacher Callsign: Sledge. Level 3. STR 5, GES 4, INT 2, CHA 2, TEMP 3, SYS 3. HP 12. Sturmkarabiner (30/30), Sprengladung x2, Schutzweste. Mission: Berlin 1961, Mauerbau. EP1 MS3 Debrief. Alle Ziele erreicht. Im HQ."},
  {"role":"user","content":"!save"}
]'
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_DS_SAVE" "03a-cross-save-deepseek"

# Extrahiere den Save-JSON aus dem DeepSeek-Output
echo "  ⏳ Extrahiere DeepSeek-Save für Sonnet-Load..."
DS_SAVE=$(python3 -c "
import json, re
with open('$OUTDIR/03a-cross-save-deepseek.md') as f:
    content = f.read()
# Find JSON block
match = re.search(r'\`\`\`json?\s*\n(\{.*?\})\s*\n\`\`\`', content, re.DOTALL)
if match:
    # Validate it's real JSON
    try:
        obj = json.loads(match.group(1))
        print(json.dumps(json.dumps(obj)))  # double-encode for embedding
    except:
        print('\"ERROR: Invalid JSON in DeepSeek save\"')
else:
    print('\"ERROR: No JSON block found\"')
" 2>/dev/null)

if [[ "$DS_SAVE" == *"ERROR"* ]]; then
  echo "  ⚠️ DeepSeek Save extraction failed, using fallback"
  # Use a simple fallback save
  DS_SAVE=$(echo '{"save_version":6,"zr_version":"4.2.6","location":"HQ","phase":"core","character":{"id":"CHR-SLEDGE","name":"Sledge","level":3,"stress":0,"psi_heat":0,"cooldowns":{},"attributes":{"STR":5,"GES":4,"INT":2,"CHA":2,"TEMP":3,"SYS_max":3,"SYS_installed":3,"SYS_runtime":3,"SYS_used":2,"hp":12,"hp_max":12},"talents":["Sprengstoff","Nahkampf"],"skills":["CQB"],"implants":[],"inventory":{"weapons":["Sturmkarabiner","Kampfmesser"],"armor":["Schutzweste"],"gadgets":["Sprengladung x2"],"consumables":["Med-Patch"],"special":[]},"stats":{"missions_completed":3,"deaths":0,"rifts_closed":0}},"campaign":{"episode":1,"mission_in_episode":3,"scene":0,"px":1,"mode":"preserve","rift_seeds":[],"exfil":{"active":false,"armed":false,"hot":false,"ttl":0,"sweeps":0,"stress":0,"anchor":null,"alt_anchor":null}},"team":{"members":[]},"party":{"characters":[]},"loadout":{},"economy":{"cu":1800,"wallets":{"CHR-SLEDGE":{"name":"Sledge","balance":1800}}},"logs":{"hud":[],"trace":[],"artifact_log":[],"market":[],"offline":[],"kodex":[],"alias_trace":[],"squad_radio":[],"foreshadow":[],"fr_interventions":[],"arena_psi":[],"psi":[],"flags":{"runtime_version":"4.2.6","merge_conflicts":[],"platform_action_contract":{"action_mode":"uncut"}}},"arc_dashboard":{"offene_seeds":[],"fraktionen":{},"fragen":[],"timeline":[{"id":"TL-BERLIN61","epoch":"1961","label":"Mauerbau-Anomalie stabilisiert","stability":3}]},"ui":{"gm_style":"verbose","intro_seen":true,"suggest_mode":false,"action_mode":"uncut","contrast":"standard","badge_density":"standard","output_pace":"normal"},"arena":{"active":false,"phase":"idle","mode":"single","match_policy":"sim","previous_mode":null,"wins_player":0,"wins_opponent":0,"tier":1,"proc_budget":0,"artifact_limit":0,"loadout_budget":0,"phase_strike_tax":0,"damage_dampener":true,"team_size":1,"fee":0,"scenario":null,"started_episode":null,"last_reward_episode":null,"policy_players":[],"audit":[]}}' | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")
fi

MSGS_CROSS="[{\"role\":\"user\",\"content\":\"Spiel laden\"},{\"role\":\"assistant\",\"content\":\"Kodex: Poste Speicherstand.\"},{\"role\":\"user\",\"content\":$DS_SAVE},{\"role\":\"user\",\"content\":\"Fertig. Zeig mir was du siehst und starte das Briefing für die nächste Mission.\"}]"

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_CROSS" "03b-cross-load-sonnet"
api_chat "zeitriss-v426-uncut-qwen" "$MSGS_CROSS" "03c-cross-load-qwen"

# ═══════════════════════════════════════════════════════════════
# TEST 4: Mid-Combat Gruppendynamik — Wer macht was?
# ═══════════════════════════════════════════════════════════════
MSGS_TACTICS="[
  {\"role\":\"user\",\"content\":\"Spiel laden\"},
  {\"role\":\"assistant\",\"content\":\"Kodex: Load-Modus aktiv.\"},
  {\"role\":\"user\",\"content\":$SAVE_ESCAPED},
  {\"role\":\"assistant\",\"content\":\"Kodex: 5er-Gruppe geladen. Rift-Mission RIFT-088 Verdun 1918 aktiv. Szene 8/14, Akt II. Grabenstellung, Nacht. Nebel. Der Grabenghost materialisiert sich 20m entfernt — eine humanoide Silhouette aus Zeitfragmenten. Boss-Encounter. Alle 5 in Deckung hinter der Grabenkante.\"},
  {\"role\":\"user\",\"content\":\"Hawk gibt den Befehl: Venom Deckungsfeuer, Iris Psi-Scan auf den Boss, Byte hackt die Feldkommunikation, Ghost flankt rechts durch den Nebel. Hawk selbst geht in Sniperposition. Zeig mir wie alle 5 agieren — Proben für alle.\"}
]"

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_TACTICS" "04-group-tactics-sonnet"
api_chat "zeitriss-v426-uncut-deepseek" "$MSGS_TACTICS" "04-group-tactics-deepseek"

# ═══════════════════════════════════════════════════════════════
# TEST 5: Chronopolis Markt + High-Level Shopping
# ═══════════════════════════════════════════════════════════════
MSGS_CHRONO="[
  {\"role\":\"user\",\"content\":\"Spiel laden\"},
  {\"role\":\"assistant\",\"content\":\"Kodex: Load-Modus aktiv.\"},
  {\"role\":\"user\",\"content\":$SAVE_ESCAPED},
  {\"role\":\"assistant\",\"content\":\"Kodex: Gruppe geladen. HQ.\"},
  {\"role\":\"user\",\"content\":\"Ich gehe allein nach Chronopolis. Markt besuchen. Ich suche ein Upgrade für meine Resonanz-Sniper und will sehen was es an Tier-4-Artefakten gibt. Budget: 12000 CU.\"}
]"

api_chat "zeitriss-v426-uncut-sonnet" "$MSGS_CHRONO" "05-chronopolis-shopping-sonnet"

echo ""
echo "═══════════════════════════════════════════════"
echo "  Deep Playtest abgeschlossen!"
echo "  Output: $OUTDIR/"
echo "═══════════════════════════════════════════════"
ls -la "$OUTDIR/" | grep -v "^total\|^d"
TOTAL_COST=$(grep -h "Cost:" "$OUTDIR"/*.md 2>/dev/null | sed 's/.*\$//' | python3 -c "import sys; print(f'\${sum(float(l.strip()) for l in sys.stdin if l.strip()):.4f}')")
echo "  Gesamtkosten: $TOTAL_COST"
