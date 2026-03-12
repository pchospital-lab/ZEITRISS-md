#!/usr/bin/env bash
# ZEITRISS – Knowledge-Pack Export
# Erstellt ein kuratiertes Upload-Paket für manuelle Plattform-Setups
# (z. B. Lumo, andere Project-Runtimes).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"

OUT_BASE="${1:-$REPO/.exports}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="$OUT_BASE/zeitriss-knowledge-pack-$STAMP"
KNOW_DIR="$OUT_DIR/knowledge"
SYS_DIR="$OUT_DIR/system"

mkdir -p "$KNOW_DIR" "$SYS_DIR"

if [ ! -f "$REPO/master-index.json" ]; then
  echo "Fehler: master-index.json nicht gefunden."
  exit 1
fi

mapfile -t SLOT_PATHS < <(python3 - <<'PY' "$REPO/master-index.json"
import json
import sys

with open(sys.argv[1], encoding='utf-8') as f:
    data = json.load(f)

seen = set()
for module in data.get('modules', []):
    if module.get('slot') is True:
        path = module.get('path', '')
        if '#' in path:
            path = path.split('#', 1)[0]
        if path and path not in seen:
            seen.add(path)
            print(path)
PY
)

if [ "${#SLOT_PATHS[@]}" -eq 0 ]; then
  echo "Fehler: Keine slot:true Module gefunden."
  exit 1
fi

for rel in "${SLOT_PATHS[@]}"; do
  src="$REPO/$rel"
  dst="$KNOW_DIR/$rel"
  if [ ! -f "$src" ]; then
    echo "Warnung: Datei fehlt und wird übersprungen: $rel"
    continue
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
done

cp "$REPO/meta/masterprompt_v6.md" "$SYS_DIR/SYSTEM_PROMPT_ONLY.md"

cat > "$OUT_DIR/UPLOAD-ONLY-THIS.txt" <<TXT
ZEITRISS Upload-Paket
=====================

1) Projektwissen / Knowledge:
   Lade NUR Dateien aus: knowledge/

2) Projekt-Anweisungen / System:
   Verwende NUR: system/SYSTEM_PROMPT_ONLY.md
   (nicht als Wissensdatei hochladen)

3) Erwartungsmanagement:
   Das Referenz-Erlebnis ist aktuell Sonnet 4.6.
   Andere Modelle/Plattformen können bei Regeltreue abweichen.
TXT

COUNT=$(find "$KNOW_DIR" -type f | wc -l | tr -d ' ')

echo "Export abgeschlossen:"
echo "  Ziel: $OUT_DIR"
echo "  Wissensdateien: $COUNT"
echo "  Systemprompt: $SYS_DIR/SYSTEM_PROMPT_ONLY.md"
