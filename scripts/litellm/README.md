# LiteLLM-Proxy für ZEITRISS

Dieser Ordner enthält alles, was LiteLLM braucht, um als Proxy zwischen
OpenWebUI und OpenRouter zu laufen. Der Sinn: **Anthropic-Prompt-Caching
aktivieren**, damit ihr ab dem zweiten Turn einer Session nur noch etwa
ein Zehntel des Masterprompt-Preises zahlt und schnellere Antworten
bekommt.

## Schneller Weg (empfohlen)

```bash
python scripts/setup.py --install-litellm
```

Das Script:

1. Prüft, ob Docker verfügbar ist.
2. Fragt den OpenRouter-API-Key ab (oder nimmt ihn aus `OPENROUTER_API_KEY`).
3. Erzeugt einen zufälligen LiteLLM-Master-Key.
4. Schreibt `.env` (chmod 600, gitignored).
5. Startet den Container und wartet auf den Health-Endpoint.
6. Macht einen 2-Call-Cache-Test, um das Setup zu verifizieren.
7. Zeigt am Ende die konkreten drei Klicks, die ihr in OpenWebUI noch machen müsst (neue Connection auf `http://localhost:4000/v1`, Preset auf Base-Model `zeitriss-sonnet` umstellen).

Danach müsst ihr in OpenWebUI einmalig die neue LiteLLM-Connection
auswählen und im Preset `ZEITRISS v4.2.6 Uncut` das Base-Model auf
`zeitriss-sonnet` umstellen. Das Script zeigt die konkreten drei
Klicks am Ende seiner Ausgabe an — einfach abarbeiten, dann läuft
jeder Turn über LiteLLM mit aktivem Prompt-Cache.

## Manueller Weg

Wenn ihr das lieber selbst orchestriert:

```bash
cd scripts/litellm
cp .env.example .env
chmod 600 .env
# .env im Editor öffnen, beide Keys eintragen
docker compose -f docker-compose.litellm.yml --env-file .env up -d
```

Container läuft dann auf `127.0.0.1:4000`, nur von localhost erreichbar.

## Troubleshooting

### Caching greift nicht

Drei häufige Ursachen:

1. **OpenRouter-Privacy-Settings** blockieren Anthropic/Bedrock.
   Unter <https://openrouter.ai/settings/privacy> prüfen.
2. **OpenRouter-Konto hat kein Guthaben** — dann schlägt jede Anfrage mit
   402 Payment Required fehl.
3. **Master-Key falsch** — Container-Logs (`docker logs litellm-zeitriss`)
   zeigen 401-Responses.

Ob Caching wirklich greift, zeigt sich in den Usage-Daten jeder Antwort
(`prompt_tokens_details.cached_tokens` > 0 ab dem zweiten Turn).

### Container crasht beim Start

```bash
docker logs litellm-zeitriss
```

Meist fehlt eine ENV-Variable. Prüfen: `cat .env` (ohne Keys zu zeigen,
einfach dass beide Zeilen da sind).

### Port 4000 ist belegt

Anderen Port in `docker-compose.litellm.yml` unter `ports:` setzen, und
dann die OpenWebUI-Connection manuell auf den neuen Port umhängen.

## Was ist drin?

- `config.yaml` — Modell-Mapping + Cache-Injection-Regel (committed)
- `docker-compose.litellm.yml` — Container-Spec mit Healthcheck (committed)
- `.env.example` — Template für die beiden Keys (committed)
- `.env` — Euer echtes Key-File (per-Install, gitignored)
- `.gitignore` — schließt nur die `.env` aus

Die ganzen Dateien sind minimal gehalten. Wer LiteLLM später um weitere
Provider erweitern will, kann `config.yaml` ergänzen — der Rest bleibt
gleich.
