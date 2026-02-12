#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  ZEITRISS – OpenWebUI Setup Script                              ║
# ║  Richtet die komplette Spielumgebung automatisch ein.           ║
# ║                                                                  ║
# ║  Voraussetzungen:                                               ║
# ║    • OpenWebUI läuft (Standard: http://localhost:3000)          ║
# ║    • OpenRouter-Key (oder anderer OpenAI-kompatibler Provider)  ║
# ║      ist in OpenWebUI unter Einstellungen → Verbindungen        ║
# ║      eingetragen                                                 ║
# ║    • Ein API-Key wurde in OpenWebUI generiert                   ║
# ║      (Einstellungen → Konto → API-Schlüssel)                   ║
# ║                                                                  ║
# ║  Nutzung:                                                       ║
# ║    ./scripts/setup-openwebui.sh                                 ║
# ║                                                                  ║
# ║  Umgebungsvariablen (optional):                                 ║
# ║    OPENWEBUI_URL     – Standard: http://localhost:3000          ║
# ║    OPENWEBUI_API_KEY – Wird interaktiv abgefragt falls leer    ║
# ║    ZEITRISS_MODEL    – Base Model (Standard: siehe unten)       ║
# ╚══════════════════════════════════════════════════════════════════╝

set -euo pipefail

# ── Farben ──────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}ℹ${NC}  $*"; }
ok()    { echo -e "${GREEN}✓${NC}  $*"; }
warn()  { echo -e "${YELLOW}⚠${NC}  $*"; }
fail()  { echo -e "${RED}✗${NC}  $*"; exit 1; }

# ── Repo-Root finden ────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ ! -f "$REPO/master-index.json" ]; then
  fail "master-index.json nicht gefunden. Bitte aus dem ZEITRISS-Repo ausführen."
fi

echo ""
echo -e "${BOLD}╔════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   ZEITRISS – OpenWebUI Setup           ║${NC}"
echo -e "${BOLD}║   Tech-Noir Zeitreise-RPG v4.2.6       ║${NC}"
echo -e "${BOLD}╚════════════════════════════════════════╝${NC}"
echo ""

# ── Konfiguration ──────────────────────────────────────────────────
OPENWEBUI_URL="${OPENWEBUI_URL:-http://localhost:3000}"

if [ -z "${OPENWEBUI_API_KEY:-}" ]; then
  echo -e "${CYAN}OpenWebUI API-Key benötigt.${NC}"
  echo "  (Erstellen unter: $OPENWEBUI_URL → Einstellungen → Konto → API-Schlüssel)"
  echo ""
  read -rsp "  API-Key eingeben: " OPENWEBUI_API_KEY
  echo ""
  echo ""
fi

export OPENWEBUI_URL OPENWEBUI_API_KEY

# ── Verbindung prüfen ──────────────────────────────────────────────
info "Verbindung zu $OPENWEBUI_URL prüfen..."
HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$OPENWEBUI_URL/api/config" 2>/dev/null || echo "000")

if [ "$HTTP" = "000" ]; then
  fail "OpenWebUI nicht erreichbar unter $OPENWEBUI_URL"
elif [ "$HTTP" = "403" ] || [ "$HTTP" = "401" ]; then
  fail "API-Key ungültig oder keine Berechtigung."
fi
ok "Verbunden mit OpenWebUI"

# ── API-Key prüfen ─────────────────────────────────────────────────
AUTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$OPENWEBUI_URL/api/v1/files/" \
  -H "Authorization: Bearer $OPENWEBUI_API_KEY" 2>/dev/null)

if [ "$AUTH_CHECK" != "200" ]; then
  fail "API-Key nicht autorisiert (HTTP $AUTH_CHECK). Bitte prüfen."
fi
ok "API-Key gültig"

# ── Base Model bestimmen ───────────────────────────────────────────
DEFAULT_MODELS=(
  "anthropic/claude-sonnet-4"
  "anthropic/claude-3.7-sonnet"
  "anthropic/claude-3.5-sonnet"
  "anthropic/claude-sonnet-4.5"
  "openai/gpt-4o"
  "google/gemini-2.5-pro-preview"
  "deepseek/deepseek-chat-v3-0324"
  "meta-llama/llama-4-maverick"
)

if [ -n "${ZEITRISS_MODEL:-}" ]; then
  BASE_MODEL="$ZEITRISS_MODEL"
  info "Base Model (manuell): $BASE_MODEL"
else
  info "Suche passendes Base Model..."
  BASE_MODEL=""
  for MODEL in "${DEFAULT_MODELS[@]}"; do
    TEST_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 \
      "$OPENWEBUI_URL/api/chat/completions" \
      -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"OK\"}], \"max_tokens\": 5, \"stream\": false}" 2>/dev/null)
    if [ "$TEST_HTTP" = "200" ]; then
      BASE_MODEL="$MODEL"
      break
    fi
  done

  if [ -z "$BASE_MODEL" ]; then
    warn "Kein Standard-Modell verfügbar. Bitte manuell angeben."
    echo ""
    echo "  Verfügbare Modelle findest du unter:"
    echo "  $OPENWEBUI_URL → Neuer Chat → Modell-Dropdown"
    echo ""
    read -rp "  Model-ID eingeben (z.B. anthropic/claude-3.5-sonnet): " BASE_MODEL
    if [ -z "$BASE_MODEL" ]; then
      fail "Kein Modell angegeben. Abbruch."
    fi
  fi
fi
ok "Base Model: $BASE_MODEL"

# ── Knowledge Base erstellen ────────────────────────────────────────
echo ""
info "Knowledge Base erstellen..."

KB_ID=$(curl -s "$OPENWEBUI_URL/api/v1/knowledge/create" \
  -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "ZEITRISS 4.2.6 Regelwerk", "description": "Vollständiges Regelwerk für das ZEITRISS Zeitreise-RPG v4.2.6"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

if [ -z "$KB_ID" ]; then
  fail "Knowledge Base konnte nicht erstellt werden."
fi
ok "Knowledge Base erstellt (ID: ${KB_ID:0:12}...)"

# ── Wissensspeicher-Dateien hochladen ──────────────────────────────
# Alle slot:true Module aus master-index.json
FILES=$(python3 -c "
import json
with open('$REPO/master-index.json') as f:
    data = json.load(f)
for m in data['modules']:
    if m.get('slot'):
        print(m['path'])
")

TOTAL=$(echo "$FILES" | wc -l)
COUNT=0
ERRORS=0

info "Lade $TOTAL Dateien in den Wissensspeicher..."
echo ""

while IFS= read -r FILE; do
  FILEPATH="$REPO/$FILE"
  FILENAME=$(basename "$FILE")
  COUNT=$((COUNT + 1))

  if [ ! -f "$FILEPATH" ]; then
    echo -e "  ${RED}✗${NC} [$COUNT/$TOTAL] $FILE (nicht gefunden)"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Upload
  FILE_ID=$(curl -s "$OPENWEBUI_URL/api/v1/files/" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
    -F "file=@$FILEPATH" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

  if [ -z "$FILE_ID" ]; then
    echo -e "  ${RED}✗${NC} [$COUNT/$TOTAL] $FILE (Upload fehlgeschlagen)"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Link to KB
  LINK_RESULT=$(curl -s "$OPENWEBUI_URL/api/v1/knowledge/$KB_ID/file/add" \
    -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"file_id\": \"$FILE_ID\"}" 2>/dev/null)

  echo -e "  ${GREEN}✓${NC} [$COUNT/$TOTAL] $FILE"
done <<< "$FILES"

echo ""
if [ $ERRORS -gt 0 ]; then
  warn "$((TOTAL - ERRORS))/$TOTAL Dateien geladen ($ERRORS Fehler)"
else
  ok "Alle $TOTAL Dateien geladen"
fi

# ── System-Prompt laden ─────────────────────────────────────────────
info "Model-Preset erstellen..."

SYSTEM_PROMPT=$(cat "$REPO/meta/masterprompt_v6.md")

# Preset erstellen via API
python3 -c "
import json, os, urllib.request

url = os.environ['OPENWEBUI_URL']
key = os.environ['OPENWEBUI_API_KEY']

with open('$REPO/meta/masterprompt_v6.md', 'r') as f:
    system_prompt = f.read()

payload = {
    'id': 'zeitriss-v426-local-uncut',
    'name': 'ZEITRISS v4.2.6 – Local Uncut',
    'base_model_id': '$BASE_MODEL',
    'meta': {
        'description': 'Tech-Noir Zeitreise-RPG mit KI-Spielleitung. Chrononauten, explodierende Würfel, cinematisches HUD. 18+.',
        'profile_image_url': '',
        'capabilities': {'vision': False, 'usage': False},
        'knowledge': [{'id': '$KB_ID', 'name': 'ZEITRISS 4.2.6 Regelwerk'}],
        'suggestion_prompts': [
            {'content': 'Spiel starten (solo schnell)'},
            {'content': 'Spiel starten (solo klassisch)'},
            {'content': 'Spiel laden'}
        ]
    },
    'params': {
        'system': system_prompt,
        'temperature': 0.8
    }
}

data = json.dumps(payload).encode()
req = urllib.request.Request(
    f'{url}/api/v1/models/create',
    data=data,
    headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f'OK:{result.get(\"id\",\"?\")}')
except urllib.error.HTTPError as e:
    body = e.read().decode()
    if '409' in str(e.code) or 'already exists' in body.lower():
        # Model exists, try update
        req2 = urllib.request.Request(
            f'{url}/api/v1/models/model/update',
            data=data,
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req2) as resp2:
            result2 = json.loads(resp2.read())
            print(f'OK:{result2.get(\"id\",\"?\")}')
    else:
        print(f'ERROR:{body[:200]}')
" 2>/dev/null | while IFS= read -r line; do
  case "$line" in
    OK:*)  ok "Preset erstellt: ${line#OK:}" ;;
    ERROR:*) fail "Preset-Erstellung fehlgeschlagen: ${line#ERROR:}" ;;
  esac
done

# ── Zusammenfassung ─────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   Setup abgeschlossen!                 ║${NC}"
echo -e "${BOLD}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}Preset:${NC}      ZEITRISS v4.2.6 – Local Uncut"
echo -e "  ${CYAN}Base Model:${NC}  $BASE_MODEL"
echo -e "  ${CYAN}Knowledge:${NC}   $TOTAL Dateien"
echo -e "  ${CYAN}Temperatur:${NC}  0.8"
echo ""
echo -e "  ${BOLD}So geht's weiter:${NC}"
echo -e "  1. Öffne ${CYAN}$OPENWEBUI_URL${NC} im Browser"
echo -e "  2. Starte einen ${BOLD}neuen Chat${NC}"
echo -e "  3. Wähle das Modell ${BOLD}\"ZEITRISS v4.2.6 – Local Uncut\"${NC}"
echo -e "  4. Tippe: ${GREEN}Spiel starten (solo schnell)${NC}"
echo ""
echo -e "  ${YELLOW}Viel Spaß, Chrononaut. Die Nullzeit wartet.${NC}"
echo ""
