#!/usr/bin/env bash
# ZEITRISS Modellvergleich — 2026-03-17
# Ziel: 6 Modelle gegen 5 gezielte Szenarien testen
# Fokus: Neue Mechaniken (Initiative, Manifestation, Load-Router, Dienstweg, Konzeptimport)
set -euo pipefail
source ~/.openwebui_env
export OPENWEBUI_URL="http://localhost:3000"
export OPENWEBUI_API_KEY

OUTDIR="$(dirname "$0")/evidence/playtest-2026-03-17"
mkdir -p "$OUTDIR"

# 5 Preset-IDs (Nemotron entfernt — nur Free-Tier auf OR, Privacy-Block)
MODELS=(
  "zeitriss-v426-uncut"                # Sonnet 4.6 (Referenz)
  "zeitriss-v426-uncut-deepseek-v32"   # DeepSeek V3.2
  "zeitriss-v426-uncut-qwen"           # Qwen 3.5
  "zeitriss-v426-uncut-glm5-turbo"     # GLM-5 Turbo (NEU)
  "zeitriss-v426-uncut-glm5"           # GLM-5 (NEU)
)

api_chat() {
  local model="$1" messages="$2" label="$3"
  local outfile="$OUTDIR/${label}.md"

  echo "▶ $label ($model)..."

  RESULT=$(curl -s --max-time 300 "$OPENWEBUI_URL/api/chat/completions" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"$model\",
      \"messages\": $messages,
      \"temperature\": 0.8,
      \"top_p\": 0.9,
      \"frequency_penalty\": 0.3,
      \"max_tokens\": 16000,
      \"stream\": false
    }" 2>/dev/null)

  MSG=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('choices',[{}])[0].get('message',{}).get('content','ERROR: No response'))" 2>/dev/null || echo "ERROR: parse failed")
  USAGE=$(echo "$RESULT" | python3 -c "
import sys,json
u=json.load(sys.stdin).get('usage',{})
print(f\"in:{u.get('prompt_tokens',0)} out:{u.get('completion_tokens',0)} cost:\${u.get('cost',0)}\")
" 2>/dev/null || echo "usage:unknown")

  {
    echo "# $label"
    echo "- **Model:** $model"
    echo "- **Tokens:** $USAGE"
    echo "- **Date:** $(date -Iseconds)"
    echo ""
    echo "## Output"
    echo ""
    echo "$MSG"
  } > "$outfile"

  echo "  ✅ done ($USAGE) → $outfile"
  sleep 2  # Rate-Limit-Puffer
}

# ═══════════════════════════════════════════════════════════════
# TEST 1: Initiative — max(GES, TEMP) korrekt anwenden
# Prüft: Neue Initiative-Formel, Tiebreaker, Attribut-Zuordnung
# ═══════════════════════════════════════════════════════════════
MSGS_INITIATIVE='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Agent Kira, Level 5. STR 3, GES 4, INT 3, CHA 3, TEMP 6, SYS 4. Waffen: Monofaser-Schwert, Kompaktpistole. In einer dunklen Gasse, 3 bewaffnete Gegner vor dir. Kampf beginnt."},
  {"role":"user","content":"Initiative würfeln! Zeig mir die komplette Berechnung für mich und alle Gegner. Wie wird Initiative berechnet?"}
]'

# ═══════════════════════════════════════════════════════════════
# TEST 2: Präkognitive Manifestation — Gate + Kosten + Einschränkungen
# Prüft: Ob die SL das Psi-System korrekt anwendet
# ═══════════════════════════════════════════════════════════════
MSGS_MANIFESTATION='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Chrononautin Lyra, Level 12. STR 4, GES 5, INT 4, CHA 3, TEMP 9, SYS 5. has_psi: true. PP: 9. Psi-Heat: 0. Talente: Psioniker, Telepathie II, Präkognition III, Präkognitive Manifestation I. Ausrüstung: Phasen-Dolch, Psi-Verstärker Mk II. Mission: Infiltration eines Labors. Ich stehe vor einer gesicherten Tür mit Wachposten."},
  {"role":"user","content":"Ich will Präkognitive Manifestation einsetzen um die Tür zu öffnen. Würfel alles durch und zeig mir den kompletten Ablauf mit Kosten."}
]'

# ═══════════════════════════════════════════════════════════════
# TEST 3: Load-Router — HQ-Zustand nach Save-Load
# Prüft: Freier HQ-Zustand, Router-Optionen, kein Direkt-Briefing
# ═══════════════════════════════════════════════════════════════
MSGS_LOADROUTER='[
  {"role":"user","content":"Spiel laden"},
  {"role":"assistant","content":"Kodex: Load-Modus aktiv. Poste deinen Speicherstand."},
  {"role":"user","content":"{\"v\":7,\"zr\":\"4.2.6\",\"save_id\":\"SAVE-2026-03-17T10:00:00Z-HQ\",\"parent_save_id\":null,\"merge_id\":null,\"branch_id\":\"ANCHOR-main\",\"campaign\":{\"episode\":2,\"mission\":3,\"px\":3,\"px_state\":\"stable\",\"mode\":\"mixed\",\"rift_seeds\":[\"RIFT-077\"]},\"characters\":[{\"id\":\"CHR-NOVA\",\"name\":\"Nova\",\"callsign\":\"Phantom\",\"rank\":\"Feldagent\",\"lvl\":8,\"xp\":0,\"origin\":{\"epoch\":\"2019\",\"hominin\":\"Homo sapiens sapiens\",\"role\":\"Hacker\"},\"attr\":{\"STR\":4,\"GES\":6,\"INT\":7,\"CHA\":3,\"TEMP\":5,\"SYS\":5},\"hp\":10,\"hp_max\":10,\"stress\":0,\"has_psi\":false,\"sys_installed\":3,\"talents\":[\"Hacking II\",\"Schleichen I\"],\"equipment\":[{\"name\":\"Kompaktpistole\",\"type\":\"weapon\",\"tier\":2},{\"name\":\"Taktik-Schild\",\"type\":\"armor\",\"tier\":1}],\"implants\":[\"Synaptischer Boost I\"],\"history\":{\"background\":\"Ex-Hacker aus Berlin 2019\",\"milestones\":[\"Triadenring gesprengt\",\"ITI-Ruf +2\"]},\"carry\":[],\"quarters_stash\":[],\"vehicles\":{\"epoch_vehicle\":{\"id\":\"VEH-001\",\"name\":\"Kurier-Bike\",\"type\":\"vehicle\",\"tier\":1,\"upgrades\":[]},\"availability\":{\"ready_every_missions\":3,\"next_ready_in\":0},\"legendary_temporal_ship\":null},\"reputation\":{\"iti\":2,\"faction\":\"Ordo Mnemonika\",\"factions\":{\"ordo_mnemonika\":2,\"chrono_symmetriker\":0,\"kausalklingen\":1,\"zerbrechliche_ewigkeit\":0}},\"wallet\":2500}],\"economy\":{\"hq_pool\":0},\"logs\":{\"trace\":[],\"market\":[],\"artifact_log\":[],\"notes\":[],\"flags\":{\"runtime_version\":\"4.2.6\",\"chronopolis_unlocked\":false,\"imported_saves\":[],\"duplicate_branch_detected\":false,\"duplicate_character_detected\":false,\"continuity_conflicts\":[]}},\"summaries\":{\"summary_last_episode\":\"\",\"summary_last_rift\":\"\",\"summary_active_arcs\":\"\"},\"continuity\":{\"last_seen\":{\"mode\":\"hq\",\"episode\":2,\"mission\":3,\"location\":\"HQ\"},\"split\":{\"family_id\":null,\"thread_id\":null,\"expected_threads\":[],\"resolved_threads\":[],\"convergence_ready\":false},\"roster_echoes\":[],\"shared_echoes\":[],\"convergence_tags\":[],\"npc_roster\":[],\"active_npc_ids\":[]},\"arc\":{\"factions\":{},\"questions\":[],\"hooks\":[]},\"ui\":{\"gm_style\":\"verbose\",\"suggest_mode\":false,\"contrast\":\"standard\",\"badge_density\":\"standard\",\"output_pace\":\"normal\",\"voice_profile\":\"gm_second_person\"},\"arena\":{\"wins\":0,\"losses\":0,\"tier\":1}}"}
]'

# ═══════════════════════════════════════════════════════════════
# TEST 4: Dienstweg-Guard — Renier NICHT als Erstkontakt
# Prüft: Dienstpersonal statt Commander, HQ-Alltag
# ═══════════════════════════════════════════════════════════════
MSGS_DIENSTWEG='[
  {"role":"user","content":"Spiel starten (solo schnell)"},
  {"role":"assistant","content":"Agent Kael, Level 1, frisch rekrutiert. Im HQ angekommen, Nullzeit-Labor-Sequenz abgeschlossen. Stehe jetzt im Quarzatrium."},
  {"role":"user","content":"Ich gehe zum Quartiermeister um meine Ausrüstung abzuholen, dann will ich in die Nullzeitbar um mich mit den anderen Agenten zu unterhalten. Beschreib mir das HQ und wen ich treffe."}
]'

# ═══════════════════════════════════════════════════════════════
# TEST 5: Konzeptimport — Fremden Charakter übernehmen
# Prüft: ZEITRISS-konforme Konvertierung, kein 1:1 Systemport
# ═══════════════════════════════════════════════════════════════
MSGS_KONZEPTIMPORT='[
  {"role":"user","content":"Spiel starten (solo klassisch)"},
  {"role":"assistant","content":"Willkommen bei ZEITRISS. Klassischer Start. Baust du deinen Charakter selbst, oder hast du Material?"},
  {"role":"user","content":"Ich hab einen D&D 5e Charakter: Elara, Level 12 High-Elf Wizard. AC 15, Hit Points 68, INT 20, WIS 16, DEX 14. Spellcasting Focus, Fireball, Counterspell, Shield, Teleport. Background: Sage. Sie war eine Forscherin in einer magischen Bibliothek. Kannst du die für ZEITRISS konvertieren?"}
]'

# ═══════════════════════════════════════════════════════════════
# RUN ALL TESTS
# ═══════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════"
echo "  ZEITRISS Modellvergleich — $(date -I)"
echo "  5 Modelle × 5 Szenarien = 25 Tests"
echo "═══════════════════════════════════════════════════════"
echo ""

declare -A TEST_MSGS
TEST_MSGS[initiative]="$MSGS_INITIATIVE"
TEST_MSGS[manifestation]="$MSGS_MANIFESTATION"
TEST_MSGS[loadrouter]="$MSGS_LOADROUTER"
TEST_MSGS[dienstweg]="$MSGS_DIENSTWEG"
TEST_MSGS[konzeptimport]="$MSGS_KONZEPTIMPORT"

TEST_NAMES=("initiative" "manifestation" "loadrouter" "dienstweg" "konzeptimport")

MODEL_SHORT=(
  "sonnet"
  "deepseek"
  "qwen"
  "glm5turbo"
  "glm5"
)

for ti in "${!TEST_NAMES[@]}"; do
  tname="${TEST_NAMES[$ti]}"
  echo ""
  echo "━━━ TEST $((ti+1))/5: $tname ━━━"
  for mi in "${!MODELS[@]}"; do
    model="${MODELS[$mi]}"
    short="${MODEL_SHORT[$mi]}"
    label="$(printf '%02d' $((ti+1)))-${tname}-${short}"
    api_chat "$model" "${TEST_MSGS[$tname]}" "$label"
  done
done

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Alle 25 Tests abgeschlossen!"
echo "  Output: $OUTDIR/"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Dateien:"
ls -la "$OUTDIR/"
echo ""
echo "Nächster Schritt: Auswertung mit playtest-2026-03-17-auswertung.sh"
