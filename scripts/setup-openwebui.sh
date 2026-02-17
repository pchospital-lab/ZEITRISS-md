#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  ZEITRISS – OpenWebUI Setup Script                              ║
# ║  Richtet die komplette Spielumgebung automatisch ein.           ║
# ║  Idempotent: Kann beliebig oft ausgeführt werden.               ║
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

# Helper: API-Call mit Auth-Header
api_get()  { curl -s "$OPENWEBUI_URL$1" -H "Authorization: Bearer $OPENWEBUI_API_KEY" 2>/dev/null; }
api_post() { curl -s "$OPENWEBUI_URL$1" -H "Authorization: Bearer $OPENWEBUI_API_KEY" -H "Content-Type: application/json" -d "$2" 2>/dev/null; }
api_del()  { curl -s -X DELETE "$OPENWEBUI_URL$1" -H "Authorization: Bearer $OPENWEBUI_API_KEY" 2>/dev/null; }

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
DEFAULT_REMOTE_MODEL="anthropic/claude-sonnet-4"

prompt_manual_model() {
  echo ""
  echo "  Verfügbare Modelle findest du unter:"
  echo "  $OPENWEBUI_URL → Neuer Chat → Modell-Dropdown"
  echo ""
  read -rp "  Model-ID eingeben (z.B. anthropic/claude-sonnet-4): " BASE_MODEL
  if [ -z "$BASE_MODEL" ]; then
    fail "Kein Modell angegeben. Abbruch."
  fi
}

if [ -n "${ZEITRISS_MODEL:-}" ]; then
  BASE_MODEL="$ZEITRISS_MODEL"
  info "Base Model (ZEITRISS_MODEL): $BASE_MODEL"
else
  echo ""
  echo -e "${BOLD}Modell-Auswahl${NC}"
  echo "  ZEITRISS läuft provider-neutral, das Modell wählst du selbst."
  echo "  Hinweis: Remote-Modelle können Kosten verursachen und Eingaben an"
  echo "  Drittanbieter übermitteln. Nutze keine sensiblen Daten in Prompts."
  echo ""
  echo "  [1] Empfohlen (Remote): $DEFAULT_REMOTE_MODEL"
  echo "  [2] Model-ID manuell eingeben"
  read -rp "  Auswahl [1/2] (Standard 1): " MODEL_CHOICE
  MODEL_CHOICE="${MODEL_CHOICE:-1}"

  case "$MODEL_CHOICE" in
    1)
      BASE_MODEL="$DEFAULT_REMOTE_MODEL"
      info "Prüfe empfohlenes Modell: $BASE_MODEL"
      TEST_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 \
        "$OPENWEBUI_URL/api/chat/completions" \
        -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"model\": \"$BASE_MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"OK\"}], \"max_tokens\": 5, \"stream\": false}" 2>/dev/null)
      if [ "$TEST_HTTP" != "200" ]; then
        warn "Empfohlenes Modell ist nicht erreichbar (HTTP $TEST_HTTP)."
        prompt_manual_model
      fi
      ;;
    2)
      prompt_manual_model
      ;;
    *)
      fail "Ungültige Auswahl '$MODEL_CHOICE'. Bitte Script erneut starten."
      ;;
  esac
fi
ok "Base Model: $BASE_MODEL"

# ── Slot-Dateien ermitteln ──────────────────────────────────────────
FILES=$(python3 -c "
import json
with open('$REPO/master-index.json') as f:
    data = json.load(f)
for m in data['modules']:
    if m.get('slot'):
        print(m['path'])
")
TOTAL=$(echo "$FILES" | wc -l)

# Dateinamen für Cleanup sammeln
SLOT_FILENAMES=$(echo "$FILES" | while IFS= read -r f; do basename "$f"; done)

# ── Knowledge Base (idempotent) ─────────────────────────────────────
echo ""
KB_NAME="ZEITRISS 4.2.6 Regelwerk"

info "Knowledge Base prüfen..."

# Alle existierenden KBs mit diesem Namen finden und löschen
EXISTING_KB_IDS=$(api_get "/api/v1/knowledge/" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data.get('items', []):
    if item.get('name') == '$KB_NAME':
        print(item['id'])
" 2>/dev/null || echo "")

if [ -n "$EXISTING_KB_IDS" ]; then
  KB_COUNT=$(echo "$EXISTING_KB_IDS" | grep -c . || true)
  info "Entferne $KB_COUNT existierende Knowledge Base(s)..."
  while IFS= read -r OLD_KB_ID; do
    [ -z "$OLD_KB_ID" ] && continue
    curl -s -X DELETE "$OPENWEBUI_URL/api/v1/knowledge/$OLD_KB_ID/delete" \
      -H "Authorization: Bearer $OPENWEBUI_API_KEY" >/dev/null 2>&1
  done <<< "$EXISTING_KB_IDS"

  # Alte ZEITRISS-Dateien aufräumen (Duplikate aus früheren Runs)
  info "Räume alte Dateien auf..."
  CLEANUP_RESULT=$(api_get "/api/v1/files/" | SLOT_FILENAMES="$SLOT_FILENAMES" python3 -c "
import sys, json, os
slot_names = set(os.environ.get('SLOT_FILENAMES', '').strip().split('\n'))
files = json.load(sys.stdin)
deleted = 0
for f in files:
    if f.get('filename', '') in slot_names:
        print(f['id'])
        deleted += 1
print(f'COUNT:{deleted}', file=sys.stderr)
" 2>/tmp/zeitriss_cleanup_count)
  CLEANUP_COUNT=$(grep -oP 'COUNT:\K\d+' /tmp/zeitriss_cleanup_count 2>/dev/null || echo "0")

  if [ -n "$CLEANUP_RESULT" ]; then
    while IFS= read -r DEL_FILE_ID; do
      [ -z "$DEL_FILE_ID" ] && continue
      api_del "/api/v1/files/$DEL_FILE_ID" >/dev/null 2>&1
    done <<< "$CLEANUP_RESULT"
    ok "$CLEANUP_COUNT alte Dateien entfernt"
  fi
  KB_MODE="aktualisiert"
else
  KB_MODE="erstellt"
fi

# Neue KB erstellen
info "Knowledge Base erstellen..."
KB_ID=$(api_post "/api/v1/knowledge/create" \
  "{\"name\": \"$KB_NAME\", \"description\": \"Vollständiges Regelwerk für das ZEITRISS Zeitreise-RPG v4.2.6\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

if [ -z "$KB_ID" ]; then
  fail "Knowledge Base konnte nicht erstellt werden."
fi
ok "Knowledge Base $KB_MODE (ID: ${KB_ID:0:12}...)"

# ── Wissensspeicher-Dateien hochladen ──────────────────────────────
COUNT=0
ERRORS=0
UPLOADED_IDS=()

info "Lade $TOTAL Dateien in den Wissensspeicher..."
echo ""

while IFS= read -r FILE; do
  FILEPATH="$REPO/$FILE"
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

  UPLOADED_IDS+=("$FILE_ID")
  echo -e "  ${GREEN}✓${NC} [$COUNT/$TOTAL] $FILE"
done <<< "$FILES"

echo ""
if [ $ERRORS -gt 0 ]; then
  warn "$((TOTAL - ERRORS))/$TOTAL Dateien hochgeladen ($ERRORS Fehler)"
else
  ok "Alle $TOTAL Dateien hochgeladen"
fi

# ── Dateien mit Knowledge Base verknüpfen (0.8.3+ kompatibel) ──────
info "Verknüpfe Dateien mit Knowledge Base..."
FILE_IDS_JSON=$(printf '%s\n' "${UPLOADED_IDS[@]}" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")

LINK_RESULT=$(api_post "/api/v1/knowledge/$KB_ID/update" \
  "{\"name\": \"$KB_NAME\", \"description\": \"Vollständiges Regelwerk für das ZEITRISS Zeitreise-RPG v4.2.6\", \"file_ids\": $FILE_IDS_JSON}")

LINKED_COUNT=$(echo "$LINK_RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
files=d.get('files') or []
names=set(f.get('meta',{}).get('name','') for f in files)
print(len(names))
" 2>/dev/null || echo "0")

if [ "$LINKED_COUNT" -ge "$TOTAL" ]; then
  ok "$LINKED_COUNT Dateien verknüpft"
else
  warn "Nur $LINKED_COUNT/$TOTAL Dateien verknüpft — bitte in OpenWebUI prüfen"
fi

# ── Model-Preset (idempotent) ───────────────────────────────────────
info "Model-Preset prüfen..."

PRESET_RESULT=$(REPO="$REPO" BASE_MODEL="$BASE_MODEL" KB_ID="$KB_ID" python3 -c "
import json, os, urllib.request, urllib.error, sys

url = os.environ['OPENWEBUI_URL']
key = os.environ['OPENWEBUI_API_KEY']
repo = os.environ['REPO']
base_model = os.environ['BASE_MODEL']
kb_id = os.environ['KB_ID']
preset_id = 'zeitriss-v426-local-uncut'

with open(os.path.join(repo, 'meta/masterprompt_v6.md'), 'r') as f:
    system_prompt = f.read()

payload = {
    'id': preset_id,
    'name': 'ZEITRISS v4.2.6 – Local Uncut',
    'base_model_id': base_model,
    'meta': {
        'description': 'Tech-Noir Zeitreise-RPG mit KI-Spielleitung. Chrononauten, explodierende Würfel, cinematisches HUD. 18+.',
        'profile_image_url': '',
        'capabilities': {'vision': False, 'usage': False},
        'knowledge': [{'id': kb_id, 'name': 'ZEITRISS 4.2.6 Regelwerk'}],
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

# Prüfen ob Model existiert
model_exists = False
try:
    req = urllib.request.Request(
        f'{url}/api/models',
        headers={'Authorization': f'Bearer {key}'}
    )
    with urllib.request.urlopen(req) as resp:
        models = json.loads(resp.read())
        if isinstance(models, dict) and 'data' in models:
            models = models['data']
        if isinstance(models, list):
            model_exists = any(m.get('id') == preset_id for m in models)
except Exception:
    pass

data = json.dumps(payload).encode()

try:
    if model_exists:
        req = urllib.request.Request(
            f'{url}/api/v1/models/model/update?id={preset_id}',
            data=data,
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f'UPDATED:{result.get(\"id\",\"?\")}')
    else:
        req = urllib.request.Request(
            f'{url}/api/v1/models/create',
            data=data,
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f'CREATED:{result.get(\"id\",\"?\")}')
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f'ERROR:{body[:200]}')
    sys.exit(1)
" 2>/dev/null)

case "$PRESET_RESULT" in
  CREATED:*)  ok "Preset erstellt: ${PRESET_RESULT#CREATED:}" ;;
  UPDATED:*)  ok "Preset aktualisiert: ${PRESET_RESULT#UPDATED:}" ;;
  ERROR:*)    fail "Preset fehlgeschlagen: ${PRESET_RESULT#ERROR:}" ;;
  *)          fail "Preset: Unerwartetes Ergebnis: $PRESET_RESULT" ;;
esac

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
