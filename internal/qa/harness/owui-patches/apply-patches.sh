#!/usr/bin/env bash
# apply-patches.sh — OWUI-Container-Patches re-applizieren
# =========================================================
# Hintergrund: OpenWebUI 0.9.5 hat einen Bug in socket/main.py:get_event_emitter.
# `request_info.get('chat_id', '').startswith('channel:')` crasht mit
# 'NoneType' object has no attribute 'startswith', wenn chat_id EXPLIZIT None ist
# (Default '' greift nur bei fehlendem Key, nicht bei None). Das blockiert den
# kopflosen API-Pfad /api/chat/completions ohne chat_id (Browser ist NICHT
# betroffen, schickt immer chat_id mit).
#
# Diese Patches leben im Container-Layer und ÜBERLEBEN `docker restart`, aber
# NICHT `docker pull` / Image-Neubau. Nach jedem OWUI-Update dieses Skript
# erneut laufen lassen (idempotent — prüft ob schon gepatcht).
#
# Verifiziert: 2026-06-15, OWUI 0.9.5. Upstream-Fix-Status vor jedem Update
# prüfen: ggf. ist der Bug dann oben behoben und der Patch unnötig/kollidiert.
set -euo pipefail

CONTAINER="${1:-open-webui}"

echo "== OWUI-Patch: socket/main.py chat_id None-Guard =="
docker exec "$CONTAINER" python3 -c "
p='/app/backend/open_webui/socket/main.py'
s=open(p).read()
old=\"    if request_info.get('chat_id', '').startswith('channel:'):\"
new=\"    if (request_info.get('chat_id') or '').startswith('channel:'):\"
if new in s:
    print('  [skip] schon gepatcht')
elif old in s:
    assert s.count(old)==1, 'Zeile nicht eindeutig'
    s=s.replace(old,new); open(p,'w').write(s)
    print('  [ok] gepatcht')
else:
    print('  [WARN] Crash-Zeile nicht gefunden — Upstream evtl. geaendert. Manuell pruefen!')
    raise SystemExit(2)
"
echo "== Restart noetig, damit uvicorn die Aenderung laedt =="
echo "   docker restart $CONTAINER"
echo "== Verifikation nach Restart =="
echo "   curl -s \$OPENWEBUI_URL/api/chat/completions -H \"Authorization: Bearer \$OPENWEBUI_API_KEY\" \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"model\":\"zeitriss-sonnet\",\"stream\":false,\"messages\":[{\"role\":\"user\",\"content\":\"FIX_OK?\"}]}'"
