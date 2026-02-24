#!/usr/bin/env bash
set -euo pipefail

# ZEITRISS OpenWebUI Updater
# Deletes old files from KB, uploads fresh copies, updates presets

source ~/.openwebui_env
KB_ID="78c967a6-f090-49f4-9b83-ba002636fa6d"
REPO="/home/altair/cloud/repos/ZEITRISS-md-git"

# === File mapping (slot → repo path) ===
declare -A FILES=(
  ["spieler-handbuch.md"]="core/spieler-handbuch.md"
  ["zeitriss-core.md"]="core/zeitriss-core.md"
  ["wuerfelmechanik.md"]="core/wuerfelmechanik.md"
  ["sl-referenz.md"]="core/sl-referenz.md"
  ["charaktererschaffung-grundlagen.md"]="characters/charaktererschaffung-grundlagen.md"
  ["charaktererschaffung-optionen.md"]="characters/charaktererschaffung-optionen.md"
  ["ausruestung-cyberware.md"]="characters/ausruestung-cyberware.md"
  ["kp-kraefte-psi.md"]="systems/kp-kraefte-psi.md"
  ["zustaende.md"]="characters/zustaende.md"
  ["hud-system.md"]="characters/hud-system.md"
  ["kampagnenstruktur.md"]="gameplay/kampagnenstruktur.md"
  ["kampagnenuebersicht.md"]="gameplay/kampagnenuebersicht.md"
  ["kreative-generatoren-missionen.md"]="gameplay/kreative-generatoren-missionen.md"
  ["kreative-generatoren-begegnungen.md"]="gameplay/kreative-generatoren-begegnungen.md"
  ["fahrzeuge-konflikte.md"]="gameplay/fahrzeuge-konflikte.md"
  ["massenkonflikte.md"]="gameplay/massenkonflikte.md"
  ["cu-waehrungssystem.md"]="systems/currency/cu-waehrungssystem.md"
  ["speicher-fortsetzung.md"]="systems/gameflow/speicher-fortsetzung.md"
  ["cinematic-start.md"]="systems/gameflow/cinematic-start.md"
  ["toolkit-gpt-spielleiter.md"]="systems/toolkit-gpt-spielleiter.md"
)

echo "=== Step 1: Delete old files from KB ==="
OLD_IDS=$(curl -s "$OPENWEBUI_URL/api/v1/files/" \
  -H "Authorization: Bearer $OPENWEBUI_API_KEY" | python3 -c "
import json,sys
for f in json.load(sys.stdin):
    if f.get('meta',{}).get('collection_name','') == '$KB_ID':
        print(f['id'])
")

for fid in $OLD_IDS; do
  echo "  Deleting file $fid..."
  curl -s -X DELETE "$OPENWEBUI_URL/api/v1/files/$fid" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" > /dev/null
done
echo "  Deleted $(echo "$OLD_IDS" | wc -w) files"

# Also check for master-index.json
MASTER_ID=$(curl -s "$OPENWEBUI_URL/api/v1/files/" \
  -H "Authorization: Bearer $OPENWEBUI_API_KEY" | python3 -c "
import json,sys
for f in json.load(sys.stdin):
    if f.get('filename','') == 'master-index.json':
        print(f['id'])
" 2>/dev/null || true)
if [ -n "$MASTER_ID" ]; then
  echo "  Deleting master-index.json ($MASTER_ID)..."
  curl -s -X DELETE "$OPENWEBUI_URL/api/v1/files/$MASTER_ID" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" > /dev/null
fi

echo ""
echo "=== Step 2: Upload fresh files ==="
UPLOADED_IDS=()

for fname in "${!FILES[@]}"; do
  fpath="$REPO/${FILES[$fname]}"
  if [ ! -f "$fpath" ]; then
    echo "  WARN: $fpath not found, skipping"
    continue
  fi
  echo -n "  Uploading $fname... "
  RESULT=$(curl -s -X POST "$OPENWEBUI_URL/api/v1/files/" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
    -F "file=@$fpath;filename=$fname")
  FID=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "FAIL")
  if [ "$FID" = "FAIL" ]; then
    echo "FAILED: $RESULT"
  else
    echo "OK ($FID)"
    UPLOADED_IDS+=("$FID")
  fi
done

# Upload master-index.json
echo -n "  Uploading master-index.json... "
RESULT=$(curl -s -X POST "$OPENWEBUI_URL/api/v1/files/" \
  -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
  -F "file=@$REPO/master-index.json;filename=master-index.json")
FID=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "FAIL")
if [ "$FID" = "FAIL" ]; then
  echo "FAILED: $RESULT"
else
  echo "OK ($FID)"
  UPLOADED_IDS+=("$FID")
fi

echo ""
echo "  Uploaded ${#UPLOADED_IDS[@]} files total"

echo ""
echo "=== Step 3: Link files to Knowledge Base ==="
# Build file_ids JSON array
FILE_IDS_JSON=$(printf '"%s",' "${UPLOADED_IDS[@]}" | sed 's/,$//')
FILE_IDS_JSON="[$FILE_IDS_JSON]"

RESULT=$(curl -s -X POST "$OPENWEBUI_URL/api/v1/knowledge/$KB_ID/update" \
  -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"file_ids\": $FILE_IDS_JSON}")
echo "  KB update: $(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"OK - {len(d.get('files',d.get('data',{}).get('files',[]) or []))} files linked\")" 2>/dev/null || echo "$RESULT")"

echo ""
echo "=== Step 4: Update Presets ==="
SYSTEM_PROMPT=$(cat "$REPO/meta/masterprompt_v6.md")

# Preset configs: id → base_model
declare -A PRESETS=(
  ["zeitriss-v426-uncut-deepseek"]="deepseek/deepseek-chat"
  ["zeitriss-v426-uncut-sonnet"]="anthropic/claude-sonnet-4.6"
  ["zeitriss-v426-uncut-qwen"]="qwen/qwen3.5-397b-a17b"
)

declare -A PRESET_NAMES=(
  ["zeitriss-v426-uncut-deepseek"]="ZEITRISS v4.2.6 Uncut – DeepSeek V3"
  ["zeitriss-v426-uncut-sonnet"]="ZEITRISS v4.2.6 Uncut – Sonnet 4.6"
  ["zeitriss-v426-uncut-qwen"]="ZEITRISS v4.2.6 Uncut – Qwen 3.5 397B"
)

for pid in "${!PRESETS[@]}"; do
  base="${PRESETS[$pid]}"
  name="${PRESET_NAMES[$pid]}"
  echo -n "  Updating $name... "

  # Build JSON payload with python to handle escaping
  PAYLOAD=$(python3 -c "
import json,sys
prompt = open('$REPO/meta/masterprompt_v6.md').read()
print(json.dumps({
    'id': '$pid',
    'name': '$name',
    'base_model_id': '$base',
    'meta': {
        'description': '18+ Tech-Noir RPG',
        'capabilities': {'vision': False, 'usage': False},
        'knowledge': [{'id': '$KB_ID', 'name': 'ZEITRISS 4.2.6 Regelwerk'}],
        'suggestion_prompts': [
            {'content': 'Spiel starten (solo schnell)'},
            {'content': 'Spiel starten (solo klassisch)'},
            {'content': 'Spiel laden'}
        ]
    },
    'params': {
        'system': prompt,
        'temperature': 0.8,
        'top_p': 0.9,
        'frequency_penalty': 0.3,
        'max_tokens': 8192
    }
}))
")

  RESULT=$(curl -s -X POST "$OPENWEBUI_URL/api/models/update" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
  
  echo "$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); p=d.get('info',{}).get('params',d.get('params',{})); print(f\"OK (temp={p.get('temperature','?')}, prompt={len(p.get('system',''))}ch)\")" 2>/dev/null || echo "RESULT: $RESULT")"
done

echo ""
echo "=== Done ==="
