# persona-driven Harness (Archiv)

**Status: historisch · zuletzt benutzt 2026-04-25.**

Gerettet aus dem gelöschten git-Branch `playtests/persona-driven-v1`. Der Harness fuhr am 25.04. einen größeren Playtest mit 3 Personas × 3 Chars, Solo+Gruppe+Mini-Boss.

## Dateien

- `persona-player.py` — 36 kB. OWUI-SL + OR-Persona-Loop, JSONL-Log pro Turn, Save-JSON-Parser (v7), PID-File, Timeout-Guards, Retry-Backoff, Cost-Watchdog, Phase-B-Roundtable (2 interne Runden + 70/30 consolidated/sequential).
- `personas.yaml` — 3 Player-Personas × 3 Chars + Assignment.

## Keys / Endpoints

Seit 2026-06-18 **ist** dieser Harness im Repo. Die frühere "nicht ins Repo"-Notiz
war überholt: `persona-player.py` lädt `OPENWEBUI_API_KEY` (aus `~/.openwebui_env`)
und den OpenRouter-Key (`sk-or-*` aus `auth-profiles.json`) **zur Laufzeit aus
lokalen Dateien** — keine hardcoded Keys. Endpoints sind localhost
(`127.0.0.1:8080`, OpenRouter-Public-URL). Vor jedem Commit gilt trotzdem:
Run-Logs auf Token-Muster prüfen (ZEITRISS ist public). Die Auswertung liegt in
`docs/qa/playtest-2026-04-25-persona-auswertung.md`.

## Für zukünftige Wiederverwendung

Falls ich sowas nochmal laufen lassen soll: Vor Benutzung prüfen
- OWUI-Preset-Name (war damals `zeitriss-v426-uncut-cached`)
- LiteLLM-Proxy-Route
- Cache-Region-Größe (war ~19.035 Tokens — heute abweichend, weil Masterprompt seit 07.05. aktualisiert)
- Personas-YAML evtl. an neue Kanon-Stellen anpassen (Preserve/Trigger seit 07.05. klarer definiert)
