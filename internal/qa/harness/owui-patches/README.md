# OpenWebUI-Container-Patches

> Stand: 2026-06-15 · OWUI 0.9.5 · von Altair

## Was hier liegt

Lokale Fixes für Bugs im laufenden `open-webui`-Docker-Container. Diese Patches
leben im **Container-Filesystem-Layer** — sie überleben `docker restart`, aber
**NICHT** `docker pull` / Image-Neubau / Container-Recreate.

| Datei | Zweck |
|---|---|
| `socket-main-chatid-none.patch` | unified diff des Fixes (zur Referenz/Review) |
| `socket_main.py.patched` | die gepatchte Datei (Vollkopie) |
| `apply-patches.sh` | re-appliziert den Patch idempotent (nach Image-Update) |

## Der Bug (socket/main.py:902)

```python
# kaputt:
if request_info.get('chat_id', '').startswith('channel:'):
# gefixt:
if (request_info.get('chat_id') or '').startswith('channel:'):
```

`dict.get('chat_id', '')` liefert den Default `''` nur, wenn der Key **fehlt**.
Ist `chat_id` aber **explizit `None`** (wie bei kopflosen API-Calls an
`/api/chat/completions` ohne chat_id), kommt `None` zurück → `None.startswith`
→ `AttributeError`. HTTP 400, Request stirbt in `get_event_emitter`.

**Wer war betroffen:** Nur der kopflose API-Pfad (Test-Skripte, Automationen).
Der Browser schickt immer eine `chat_id` mit → Endnutzer war NICHT betroffen.

## Nach einem OWUI-Update (`docker pull` / neues Image)

1. **Erst prüfen, ob Upstream den Bug selbst gefixt hat** (dann Patch unnötig):
   ```bash
   docker exec open-webui grep -n "get('chat_id', '').startswith" \
     /app/backend/open_webui/socket/main.py
   ```
   Kein Treffer mehr → oben gefixt, nichts zu tun.
2. Sonst Patch re-applizieren:
   ```bash
   ./apply-patches.sh open-webui
   docker restart open-webui
   ```
3. Verifizieren (3 Pfade): kopflos / chat_id=null / Browser-local-mit-KB —
   siehe `memory/2026-06-15.md` § OWUI-Bug-Fix.

## Backup der Original-Dateien

`/mnt/agent_share/cloud/_backups/owui-patch-2026-06-15_1704/`
(main.py + utils_middleware.py, Stand vor dem Eingriff).
