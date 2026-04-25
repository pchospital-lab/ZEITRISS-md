---
title: "ZEITRISS Setup-Guide"
version: 4.2.6
tags: [meta, setup]
---

# ZEITRISS Setup-Guide

Alles rund um Installation, Konfiguration und Betrieb. Spielinhalte und
Regeln findest du im [Spieler-Handbuch](../core/spieler-handbuch.md).

---

## Inhalt

1. [Überblick: Wie ZEITRISS läuft](#überblick-wie-zeitriss-läuft)
2. [Welches Setup passt zu dir?](#welches-setup-passt-zu-dir)
3. [Happy Path: Installation in fünf Schritten](#happy-path-installation-in-fünf-schritten)
4. [Updates und Wartung](#updates-und-wartung)
5. [Varianten](#varianten)
6. [Troubleshooting](#troubleshooting)
7. [Referenz](#referenz)

---

## Überblick: Wie ZEITRISS läuft

ZEITRISS ist **Daten, kein Programm**. Das Spiel besteht aus einem
Masterprompt und 19 Wissensmodulen. Gespielt wird in **OpenWebUI**,
einer Chat-Oberfläche. Ein Python-Script richtet alles ein.

```text
┌──────────────────────────────────────────────────────────────────────┐
│  DU (Browser)                                                        │
│    │                                                                 │
│    ▼                                                                 │
│  OpenWebUI  ◄── [setup.py] ── schreibt Preset + Knowledge Base       │
│   (Docker)                     (einmalig, danach `--sync` bei        │
│    │                           Updates)                              │
│    │                                                                 │
│    ├──► LiteLLM (Docker, optional) ──► OpenRouter ──► Claude/GLM/… │
│    │      [aktiviert Prompt-Cache: ~90 % Ersparnis bei Claude]      │
│    │                                                                 │
│    └──► Ollama (optional, zwei verschiedene Rollen):                 │
│           • als Sprachmodell (offline spielen, statt OpenRouter)     │
│           • als Embedding-Engine (KB lokal indexieren, statt MiniLM) │
└──────────────────────────────────────────────────────────────────────┘
```

| Komponente | Pflicht? | Wofür |
| --- | --- | --- |
| **OpenWebUI** (Docker-Container) | ✅ Pflicht | Chat-Oberfläche, hier spielt ihr |
| **ZEITRISS-Repo + Python** | ✅ Pflicht | Regelwerk + Setup-Script |
| **OpenRouter-Key** | ✅ Pflicht* | Modellzugang (Cloud, günstig pay-per-token). *Außer bei Ollama-Sprachmodell-Variante |
| **OpenWebUI-API-Key** | ✅ Pflicht | damit Setup-Script Preset + KB schreiben kann |
| **LiteLLM** (Docker-Container) | 🟡 Empfohlen | Prompt-Cache für Claude-Modelle (~90 % Ersparnis) |
| **Ollama** | ⚪ Optional | Offline-Modell **oder** lokales Embedding |

> 💡 **Das Setup-Script macht viel, aber nicht alles**: Es richtet
> Preset und Knowledge Base in OpenWebUI automatisch ein. OpenWebUI
> selbst, Docker, Python und die zwei API-Keys müsst ihr einmal manuell
> bereitstellen. Ollama nur, wenn ihr es bewusst wollt.

---

## Welches Setup passt zu dir?

```text
Willst du ZEITRISS …

├─ schnell + günstig + beste Qualität?      → Happy Path (OpenWebUI + OpenRouter + LiteLLM)
│                                             [Standard-Pfad]
│
├─ offline / ohne Cloud / private Daten?    → Variante: Ollama als Sprachmodell
│                                             (braucht starke GPU)
│
├─ nur mal reinschnuppern, keine Installation?  → Variante: Lumo / Claude Projects
│                                                 (ohne OpenWebUI, ohne Script)
│
└─ DIY, kein Script?                        → Variante: Manuelles Setup
```

Für den **Happy Path** lies einfach den nächsten Abschnitt. Alles
andere findest du unter [Varianten](#varianten).

---

## Happy Path: Installation in fünf Schritten

Dieser Pfad richtet OpenWebUI + OpenRouter ein — das empfohlene
Basis-Setup. Schritt 5 (LiteLLM) ist ein **empfohlener Bonus** für
Claude-Modelle und spart langfristig die meisten Kosten. Wer kein Claude
nutzt, überspringt Schritt 5.

> ℹ️ **Zeitaufwand**: ~25 Minuten fürs Basis-Setup, +5 Minuten für den
> LiteLLM-Bonus. Updates später dauern meist unter einer Minute.

### Schritt 1 — OpenWebUI starten

OpenWebUI ist eure Chat-Oberfläche (kostenlos, self-hosted, nichts
verlässt euren Rechner).

**Voraussetzung**: Docker muss einmal vorab installiert sein. Falls
noch nicht vorhanden: <https://docs.docker.com/get-docker/>.

```bash
docker run -d --name open-webui \
  -p 8080:8080 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

Danach <http://localhost:8080> öffnen und einen Admin-Account anlegen
(bleibt lokal auf eurem Gerät).

> ⚠️ **Port bereits belegt?** Wenn ihr OpenWebUI auf einem anderen Port
> startet (z. B. `-p 3000:8080`), müsst ihr das dem Setup-Script später
> mitteilen: `export OPENWEBUI_URL=http://localhost:3000` vor dem Aufruf.

Wer kein Docker hat: Alternative Installationswege in der
[Upstream-Doku](https://docs.openwebui.com/getting-started/).

### Schritt 2 — OpenRouter-Account + Key

OpenRouter gibt euch Zugang zu Claude/GLM/DeepSeek etc. ohne eigene
Abos — ihr zahlt pay-per-token.

1. Account auf <https://openrouter.ai> anlegen.
2. Guthaben einzahlen — **5 USD reichen für viele Stunden Spiel**.
3. Unter <https://openrouter.ai/keys> einen Key erzeugen (`sk-or-v1-…`).
4. In OpenWebUI eintragen: **Einstellungen → Verbindungen →
   + OpenAI-kompatible Connection**
   - Base URL: `https://openrouter.ai/api/v1`
   - API-Key: euer `sk-or-v1-…`

### Schritt 3 — Python + OpenWebUI-API-Key

Python braucht ihr, um das Setup-Script laufen zu lassen.

- macOS / Linux: meist schon da.
- **Windows**: Installer von <https://python.org> holen.

> ⚠️ **Windows-Stolperfalle**: Beim Installer **„Add Python to PATH"**
> anklicken. Ohne das kennt die Eingabeaufforderung den `python`-Befehl
> nicht.
>
> Kein Terminal zur Hand? → [Wie öffne ich ein Terminal?](terminal-help.md)

Dann braucht das Script noch einen zweiten Key — den **OpenWebUI-API-Key**
(nicht verwechseln mit dem OpenRouter-Key aus Schritt 2):

1. In OpenWebUI oben rechts auf euer Profil klicken.
2. **Account → API Keys → „Create new key"**.
3. Key kopieren, in die Zwischenablage.

> 💡 **Warum zwei verschiedene Keys?** Der OpenRouter-Key (Schritt 2)
> redet mit dem Sprachmodell. Der OpenWebUI-Key (hier) redet mit eurem
> eigenen OpenWebUI. Das Setup-Script nutzt Letzteren, um Preset und
> Knowledge Base automatisch anzulegen, statt dass ihr das per Hand
> klickt.

### Schritt 4 — ZEITRISS klonen und Setup-Script laufen lassen

```bash
git clone https://github.com/pchospital-lab/ZEITRISS-md.git
cd ZEITRISS-md
python scripts/setup.py
```

Das Script fragt den OpenWebUI-API-Key ab, lädt die 19 Wissensmodule
hoch, erstellt die Knowledge Base, legt das Preset `ZEITRISS v4.2.6 Uncut`
an und prüft am Ende per Retrieval-Check, ob alles greift.

Dauer: **5–10 Minuten** beim ersten Mal (Embeddings werden berechnet).
Ohne Git: ZIP-Download über **Code → Download ZIP** auf GitHub,
entpacken, Terminal im Ordner öffnen, Script ausführen.

### Schritt 5 (empfohlen) — LiteLLM einrichten für günstigeres Spielen

Der ZEITRISS-Masterprompt ist ~34 KB groß. Ohne Caching zahlt ihr ihn
bei **jedem** Turn neu. LiteLLM ist ein kleiner Docker-Container, der
den Anthropic-Prompt-Cache aktiviert und spart **~90 % der
Prompt-Kosten** auf jedem Folge-Turn.

```bash
python scripts/setup.py --install-litellm
```

Das Script fragt den OpenRouter-Key, erzeugt einen eigenen
LiteLLM-Master-Key, startet den Container, prüft den Cache live und
zeigt am Ende drei Klicks, die ihr in OpenWebUI noch machen müsst:

1. **Einstellungen → Verbindungen → + Add Connection**
   - URL: `http://localhost:4000/v1`
   - Key: der ausgegebene LiteLLM-Master-Key
2. Speichern.
3. Preset `ZEITRISS v4.2.6 Uncut` öffnen → Base-Model auf
   `zeitriss-sonnet` umstellen.

> ⚠️ **Privacy-Check bei OpenRouter**: Unter
> <https://openrouter.ai/settings/privacy> muss der Provider-Zugriff für
> Anthropic oder AWS Bedrock zugelassen sein. Sonst blockiert OpenRouter
> die Route, und das Caching greift nicht. Das Script warnt explizit.

Wenn ihr kein Claude-Modell nutzt, könnt ihr Schritt 5 überspringen —
bei GLM/DeepSeek/Qwen ist das integrierte Caching anders geregelt,
LiteLLM schadet nicht, bringt aber weniger.

### Fertig — Spiel starten

Neuen Chat in OpenWebUI öffnen, Modell `ZEITRISS v4.2.6 Uncut` wählen,
tippen:

```
Spiel starten (solo klassisch)
```

`Spiel starten (solo schnell)` ist optional als Fast-Lane für
Kurzrunden. Natürliche Sprache
funktioniert auch — „Ich will neu starten als Gruppe" startet die
Gruppen-Chargen.

> ℹ️ **Funktioniert's?** Die SL begrüßt euch mit einer Szene, ein
> HUD-Block `EP 1 · MS 1 · SC …` taucht auf — dann läuft alles. Falls
> nicht: [Troubleshooting](#troubleshooting).

---

## Updates und Wartung

### Der normale Update-Flow

Nach einem `git pull` reicht:

```bash
git pull
python scripts/setup.py --sync
```

Der `--sync`-Modus vergleicht die lokalen Dateien mit einem Manifest
(`.openwebui-sync.json`, automatisch angelegt) und überträgt **nur,
was sich geändert hat**:

- Masterprompt geändert → Preset wird gepatcht (<1 s).
- Einzelne Wissensmodule geändert → nur die neu hochladen und neu
  indexieren.
- Nichts geändert → „Alles synchron, nichts zu tun."

Das spart bei typischen Regel-Patches **Minuten bis zu einer halben
Stunde** gegenüber dem Full-Rebuild. Eure KB-IDs bleiben stabil, offene
Browser-Chats überleben.

### Dauer-Erwartung

| Fall | Dauer |
| --- | --- |
| `--sync`, nichts geändert | <1 Sekunde |
| `--sync`, nur Masterprompt | 1–2 Sekunden |
| `--sync`, 1–5 KB-Dateien geändert | 20 s bis 8 min |
| Full-Rebuild / Erstinstallation | 5 min bis 25 min |

Die Spannweite kommt von der **Embedding-Engine**: OpenWebUI-Default
(MiniLM) rechnet in Sekunden, Ollama-CPU braucht pro 80-kB-Datei
60–120 Sekunden. Bei sehr langsamer Hardware das Timeout hochsetzen —
siehe [Troubleshooting](#sync-meldet-timeout-bei-der-datei-verknüpfung).

### Wann Full-Rebuild statt `--sync`?

```bash
python scripts/setup.py
```

Richtig in folgenden Fällen:

- **Erstinstallation** — `--sync` verlangt ein existierendes Preset.
- **Nach OpenWebUI-Major-Upgrade** — Knowledge-Schema kann sich ändern.
- **ZIP-Download-User** — ohne Git geht `--sync` nicht (Manifest wäre
  bei jedem frischen ZIP-Entpacken wieder weg).
- **Zerschossener Zustand** — wenn `--sync` mehrfach fehlschlägt und
  der Fehler unklar bleibt.

Der Full-Rebuild schreibt am Ende automatisch das Manifest, sodass ein
anschließender `--sync`-Lauf sofort „synchron" meldet.

### Manuelle Tweaks im Preset bleiben erhalten

`--sync` patcht nur den System-Prompt (Masterprompt). Wenn ihr in
OpenWebUI manuell Temperature, Top-P oder Frequency geändert habt,
bleiben diese Werte unberührt.

### Multi-Install

Pro lokalem Repo-Clone wird genau ein Manifest geführt. Wer gegen
mehrere OpenWebUI-Instanzen syncen will (zwei Rechner, zwei Server),
braucht getrennte Clones.

---

## Varianten

Abweichungen vom Happy Path. Alle optional, jede für sich dokumentiert.

### Lokales Gruppenspiel am selben Rechner

ZEITRISS ist primär für **Gruppen an einem Gerät** gedacht: alle sitzen
zusammen um einen Laptop, ein Spieler moderiert, gespielt wird im
Wechsel — wie am Pen-&-Paper-Tisch, nur mit KI-SL statt Human-SL.

> Remote-Play über Netzwerk (Tailscale, VPN, Multi-User-OpenWebUI) ist
> möglich, braucht aber eigenes Setup. Ein dedizierter Remote-Guide
> folgt später.

**Setup für die Gruppe**: Nur eine Person hostet (folgt dem Happy Path).
Die anderen installieren **nichts** — sie sitzen einfach mit am Rechner.

**Gruppenstart**:

```
Spiel starten (gruppe klassisch)
```

Die SL führt durch Gruppen-Chargen: Jeder Spieler gibt Vibe, Attribute
und Loadout nacheinander durch. Danach HQ, Save, Mission. Alternativ
`Spiel starten (gruppe schnell)` als Fast-Lane — SL generiert Charaktere
mit Defaults und springt direkt ins Briefing.

**Mitgebrachte Saves laden** (aus Solo- oder früheren Gruppen-Abenden):

```
Spiel laden
```

Danach alle Saves hintereinander in den Chat pasten — ein Save sieht
so aus:

````
```json
{
  "v": 7,
  "save_id": "SAVE-2026-04-20T21:14:00Z-HQ-NOVA",
  "characters": [
    { "id": "CHR-KIRA", "name": "Kira Vasiliev", "lvl": 4, ... }
  ],
  "campaign": { "episode": 2, "mission": 6, ... },
  ...
}
```
````

Der **erste** Save setzt den Kampagnen-Anker (Welt, Episode, Mission),
alle weiteren bringen ihre Charaktere mit. Die SL mergt automatisch.

**Wer tippt, wer würfelt?**

- **Ein Tipper pro Szene** — einer sitzt an der Tastatur, die anderen
  sagen vor, Tipper rotiert nach jeder Mission.
- **Ansage in eckigen Klammern** (empfohlen, nicht Pflicht):
  „[Kira] Ich ziele auf den Wachposten" ist eindeutiger als anonymes
  „Ich schieße". Natürliche Sprache („Kira zielt…") funktioniert
  genauso — die eckigen Klammern sind nur eine Abkürzung.
- **Würfel macht die SL** — das ist Teil des Spiels. Die Gruppe
  entscheidet die Aktion, die SL berichtet das Ergebnis mit Formel.

**Pausen**: Der Chat läuft nicht weiter, solange niemand tippt. Klo-Pause
ist problemlos.

**Ende des Abends**: `!save` im HQ, die SL gibt den Gruppen-JSON zurück.
Text in eine Datei kopieren und an alle verteilen. Beim nächsten Abend
einfach `Spiel laden` und einfügen.

**Split für Solo-Weiterspielen**: Nach Debrief im HQ bietet die SL
Split-Pfade an. Einfach sagen: „Ich möchte mit Kira solo weiterspielen."
Die SL gibt einen Solo-Save aus — nur diese Figur + Kampagnen-Anker.
Solo-Erlebnisse fließen beim nächsten Gruppenabend wieder ein.

> 💡 **Save früh, save oft**: Macht nach jeder Mission einen gemeinsamen
> Save. Save = Charakter; nicht gesichert = im nächsten Browser-Crash
> weg.

### Ollama als Sprachmodell (Offline-Play)

**Rolle**: Ollama ersetzt hier **OpenRouter**. Ihr spielt komplett
offline/lokal, keine Daten verlassen euren Rechner.

**Voraussetzung**: Ollama installiert, ein fähiges Modell geladen
(z. B. `llama3.1:70b` oder `qwen2.5:72b`). ZEITRISS ist regel-komplex,
schwache Modelle kommen schnell an Grenzen — mindestens 70B-Klasse
empfohlen, und eine GPU mit genug VRAM.

**Einrichtung**: Ollama wie gewohnt laufen lassen. In OpenWebUI unter
**Einstellungen → Verbindungen** die Ollama-Verbindung eintragen (meist
`http://host.docker.internal:11434`). Das ZEITRISS-Preset nutzt dann
statt `claude-sonnet-4.6` eins eurer Ollama-Modelle.

**LiteLLM bringt hier nichts** — Ollama hat kein Anthropic-Cache, es
läuft ja lokal.

### Ollama als Embedding-Engine (lokales KB-Indexing)

**Rolle**: Ollama ersetzt hier **MiniLM** (den Default-Embedder). Nur
beim **Aufbau der Knowledge Base** und bei `--sync` aktiv — nicht beim
Spielen selbst.

**Wann sinnvoll?** Wenn ihr sowieso schon Ollama fahrt und einen
eingebetteten Embedder nutzen wollt. Für Normalspieler ist MiniLM-Default
für 19 Dateien **völlig ausreichend**. Ollama-Embedding lohnt sich nicht
als Selbstzweck.

**Aktivierung**:

```bash
python scripts/setup.py --embedding ollama
```

Voraussetzung: Ollama läuft, `nomic-embed-text` (oder anderes
Embedding-Modell) ist verfügbar, OpenWebUI kann Ollama erreichen.

> 💡 **Die zwei Ollama-Rollen nicht verwechseln**: Sprachmodell-Ollama
> (oben) ist das Hirn, das die SL antreibt. Embedding-Ollama (hier)
> ist der Indexer, der die KB durchsuchbar macht. Beide können parallel
> laufen oder keins — OpenWebUI braucht nur den Default-MiniLM.

### Andere Plattformen (Lumo, Claude Projects, Custom GPTs)

Kein OpenWebUI, kein Docker, kein Script — ihr nutzt einen fertigen
Browser-Dienst. ZEITRISS wird dabei als **Wissenspaket** exportiert:

```bash
python scripts/setup.py --export
```

Das erzeugt ein Paket mit `masterprompt.md` + 19 Wissensmodulen plus
Anleitung, wie ihr es in eure Plattform ladet.

| Plattform | Tauglichkeit |
| --- | --- |
| **Lumo** (Proton) | ✅ Funktioniert gut. Details: [`docs/setup-lumo.md`](setup-lumo.md) |
| **Claude Projects** | ✅ Funktioniert gut. |
| **Custom GPTs** (OpenAI) | ⚠️ Eingeschränkt. Prompt-Limit zu klein, 18+-Inhalte werden teils redacted. |

Für Plattformen ohne Ordner-Support: `--export --flat` erzeugt
nummerierte Flat-Dateien.

### Manuelles Setup ohne Script

Wenn ihr das Script nicht nutzen wollt:

**1. Knowledge Base** in OpenWebUI anlegen (Name: `ZEITRISS 4.2.6 Regelwerk`).
19 Wissensmodule aus dem Repo hochladen (welche das sind, bestimmt
`master-index.json` mit `"slot": true`):

| Kategorie | Dateien |
| --- | --- |
| **core** | `spieler-handbuch.md`, `zeitriss-core.md`, `wuerfelmechanik.md`, `sl-referenz.md` |
| **characters** | `charaktererschaffung-grundlagen.md`, `ausruestung-cyberware.md`, `zustaende.md`, `hud-system.md` |
| **gameplay** | `kampagnenstruktur.md`, `kampagnenuebersicht.md`, `kreative-generatoren-missionen.md`, `kreative-generatoren-begegnungen.md`, `fahrzeuge-konflikte.md`, `massenkonflikte.md` |
| **systems** | `kp-kraefte-psi.md`, `cu-waehrungssystem.md`, `speicher-fortsetzung.md`, `cinematic-start.md`, `toolkit-gpt-spielleiter.md` |

**Nicht hochladen**: `README.md`, `master-index.json`, Archiv-Dateien.

**Optional, nicht im Default-Slotset**: `characters/charaktererschaffung-optionen.md`
(Inspirations-/Fallback-Charaktere, Archetypen-Fundus für One-Shots). Das
Modul ist bewusst nicht im Default-Ladepfad — die SL bevorzugt `generate`
/ `custom generate` / manuelles Bauen. Nur laden, wenn ihr Pregens
bewusst im Spiel haben wollt.

**2. Modell-Preset** anlegen:

- Name: `ZEITRISS v4.2.6 Uncut`
- Base-Modell: `anthropic/claude-sonnet-4.6` (empfohlen)
- System-Prompt: Inhalt von `meta/masterprompt_v6.md` komplett einfügen
  (**nicht** in den Wissensspeicher!)
- Wissensbasis: `ZEITRISS 4.2.6 Regelwerk` verknüpfen
- Capabilities: Vision und Usage **aus**

**3. Parameter**:

| Parameter | Wert |
| --- | --- |
| Temperature | 0.8 |
| Top-P | 0.9 |
| Frequency Penalty | 0.3 |
| Max Tokens | 64000 |

**4. Spielen**: Neuer Chat → Preset wählen → `Spiel starten (solo klassisch)`.

---

## Troubleshooting

### „Die SL antwortet, aber Regeln klingen falsch"

Das Retrieval zieht vermutlich keine Regeln aus der KB. Erst Script
noch einmal laufen lassen:

```bash
python scripts/setup.py
```

Wenn der Fehler bleibt, ist wahrscheinlich die Embedding-Engine in
OpenWebUI durcheinander (häufig nach Major-Upgrades):

```bash
python scripts/setup.py --embedding default
```

Das setzt die Engine explizit auf das eingebaute MiniLM-Modell und
baut alles neu auf.

### „Das Script meldet Fehler beim Verknüpfen der Dateien"

Der Verknüpfungs-Endpunkt von OpenWebUI meldet manchmal spurious
HTTP-Fehler. Entscheidend ist der **Retrieval-Check** am Ende: Solange
dort `KB-Retrieval funktioniert` steht, sind alle Dateien korrekt
eingebunden.

### „Ich habe einen komplett zerschossenen Zustand"

```bash
python scripts/setup.py --reset-embeddings --embedding default
```

`--reset-embeddings` räumt verwaiste Vektor-Ordner auf, bevor die neue
KB gebaut wird.

### „Setup hängt bei der URL-Abfrage"

Umgebungsvariablen setzen, dann fragt das Script nichts:

```bash
export OPENWEBUI_URL=http://localhost:8080
export OPENWEBUI_API_KEY=sk-...
python scripts/setup.py -y
```

### „`--sync` meldet ‚Preset existiert nicht'"

`--sync` ist ein Update-Modus, keine Erstinstallation. Einmal Full-Rebuild
laufen lassen:

```bash
python scripts/setup.py
```

### „`--sync` dauert so lang wie der Full-Rebuild"

Zwei häufige Ursachen:

1. **Kein Manifest vorhanden** (`.openwebui-sync.json` fehlt, z. B.
   nach `git clean` oder frischem ZIP-Entpacken). Lösung: einmal
   Full-Rebuild, danach sind künftige `--sync` wieder schnell.
2. **Viele Dateien zugleich geändert** — dann zieht `--sync` sie alle
   durch, das ist normal. Der Progress-Counter zeigt, wie viele.

### „`--sync` meldet Timeout bei der Datei-Verknüpfung"

OpenWebUI rechnet die Embeddings synchron. Ollama-CPU braucht pro
Datei 1–2 Minuten, Default-Timeout ist 6 Minuten. Auf sehr langsamer
Hardware hochsetzen:

```bash
export OWUI_ADD_FILE_TIMEOUT=900
python scripts/setup.py --sync
```

Wenn das Script bei einer Datei trotzdem aufgibt: Fortschritt bleibt
im Manifest stehen, der nächste `--sync` macht dort weiter.

### „LiteLLM-Cache greift nicht"

Drei häufige Ursachen:

1. **OpenRouter-Privacy-Settings** blockieren Anthropic/Bedrock. Unter
   <https://openrouter.ai/settings/privacy> prüfen.
2. **OpenRouter-Guthaben leer** — dann schlägt jede Anfrage mit 402
   fehl. Unter <https://openrouter.ai/credits> nachladen.
3. **Master-Key falsch** in der OpenWebUI-Connection. Logs prüfen:
   `docker logs litellm-zeitriss`.

### LiteLLM-Container verwalten

```bash
docker logs litellm-zeitriss                               # Logs ansehen
docker stop litellm-zeitriss                               # Pausieren
docker start litellm-zeitriss                              # Weiterlaufen lassen
docker compose -f scripts/litellm/docker-compose.litellm.yml down   # Komplett entfernen
```

Ausführlichere LiteLLM-Doku:
[`scripts/litellm/README.md`](../scripts/litellm/README.md).

---

## Referenz

### Script-Kommandos

| Befehl | Wirkung |
| --- | --- |
| `python scripts/setup.py` | Full-Rebuild, interaktiv |
| `python scripts/setup.py --sync` | Inkrementelles Update (empfohlen nach `git pull`) |
| `python scripts/setup.py --install-litellm` | LiteLLM-Proxy einrichten |
| `python scripts/setup.py --export` | Export-Paket für Lumo / Claude Projects |
| `python scripts/setup.py --export --flat` | Flat-Export (nummerierte Dateien) |

### Flags

| Flag | Wirkung |
| --- | --- |
| `-y`, `--yes` | Keine Rückfragen. URL = `http://localhost:8080`, Modell = Default |
| `--sync` | Inkrementeller Update-Modus (Manifest-basiert) |
| `--install-litellm` | LiteLLM-Container einrichten (idempotent) |
| `--embedding default` | Embedding auf MiniLM setzen (OpenWebUI-Default) |
| `--embedding ollama` | Embedding auf Ollama + `nomic-embed-text` setzen |
| `--ollama-url URL` | Custom Ollama-Endpoint |
| `--ollama-model NAME` | Anderes Ollama-Embedding-Modell |
| `--reset-embeddings` | Verwaiste Vektor-Collections löschen vor Rebuild |
| `--no-verify` | Retrieval-Check überspringen (nicht empfohlen) |
| `--strict` | Exit-Code 2 bei fehlgeschlagenem Retrieval-Check (CI/CD) |

### Umgebungsvariablen

| Variable | Wirkung |
| --- | --- |
| `OPENWEBUI_URL` | OpenWebUI-Adresse (Default: `http://localhost:8080`) |
| `OPENWEBUI_API_KEY` | API-Key (sonst interaktiv) |
| `ZEITRISS_MODEL` | Base-Model-ID (sonst interaktiv) |
| `OPENROUTER_API_KEY` | Für `--install-litellm` (sonst interaktiv) |
| `OWUI_ADD_FILE_TIMEOUT` | Timeout pro Datei beim KB-Link (Sekunden, Default: 360) |

### Was das Script im Detail tut

**Full-Rebuild** (`python scripts/setup.py`):

1. Verbindung prüfen (API-Key, Health-Check, Auth).
2. Embedding-Engine-Precheck.
3. Altes Preset aufräumen (falls Upgrade die ID verwaist hat).
4. Alte Knowledge Base entfernen (inkl. verknüpfter Dateien).
5. 19 Wissensdateien hochladen und an neue KB verknüpfen.
6. Preset anlegen/aktualisieren (Masterprompt, Parameter, KB-Bindung).
7. Sync-Manifest schreiben (`.openwebui-sync.json`, per-Install,
   gitignored).
8. Retrieval-Check mit Canary-Query.

**Inkrementeller Sync** (`python scripts/setup.py --sync`):

1. Verbindung prüfen.
2. Preset + KB serverseitig lesen.
3. Manifest laden (fehlt es, alle Dateien als neu behandeln).
4. Masterprompt-Drift prüfen (MD5-Vergleich).
5. KB-Datei-Deltas pro Datei prüfen.
6. Geänderte Dateien: alte entlinken und löschen, neue hochladen
   und verlinken.
7. Manifest-Checkpoint alle drei Dateien (Ctrl-C-sicher).
8. Retrieval-Check.

`--sync` **vertraut** auf sein Manifest. Wenn jemand in OpenWebUI
manuell eine KB-Datei löscht, merkt der Server-Drift-Check das beim
nächsten Lauf — solange OpenWebUI die Dateiliste korrekt ausgibt.
Im Zweifel hilft immer der Full-Rebuild.

### Modelle

> **Sonnet 4.6 ist das einzige Modell mit vollständiger Regeltreue.**
> Budget-Modelle erzählen atmosphärisch, erfinden aber eigene
> Würfelsysteme, wenn man sie lässt.

| Modell | Typ | Preis (pro 1M Token) | Stärke |
| --- | --- | --- | --- |
| `anthropic/claude-sonnet-4.6` | **Empfohlen** | ~$3/$15 | Korrekte Mechanik, HUD, Px |
| `z-ai/glm-5-turbo` | **Budget** | günstig | Erkennt Regelgates, 7× billiger |
| `deepseek/deepseek-v3.2` | **Ultra-Budget** | ~$0.25/$0.40 | Günstig, Regeln teils abweichend |
| `z-ai/glm-5` | **Experimentell** | ~$0.40/$1.71 | Guter Noir-Ton, halluziniert teils |

Ergebnisse aus dem
[Modellvergleich 2026-03-17](../internal/qa/evidence/playtest-2026-03-17/AUSWERTUNG.md)
(5 Szenarien × 4 Modelle).

### Sicherheit

- **API-Keys getrennt halten**, keine geteilten Admin-Tokens für
  Spielgruppen.
- **Auth vor Netzfreigabe**: OpenWebUI nie ohne Login ins Internet
  hängen.
- **Remote-Provider** verarbeiten Eingaben — keine sensiblen Daten in
  Prompts.
- **Key versehentlich committed?** Sofort rotieren, Datei bereinigen,
  History-Cleanup falls schon gepusht.
- LiteLLM-Container ist **loopback-only** gebunden (`127.0.0.1:4000`),
  von außen nicht erreichbar.

### Repo-Struktur

```text
ZEITRISS-md/
├── README.md                # Landingpage + Quickstart
├── setup.json               # Projekt-Config für setup.py
├── core/                    # Grundregeln und ZEITRISS-Mechaniken
├── characters/              # Charaktererschaffung, Ausrüstung, Zustände
├── gameplay/                # Kampagnenstruktur, Generatoren
├── systems/                 # Gameflow, Währung, KI-SL-Toolkit
├── meta/                    # Masterprompts
├── docs/                    # Setup-Guides, Lizenz
├── scripts/                 # setup.py, Linter, Smoke-Tests
│   └── litellm/             # LiteLLM-Proxy-Setup
├── internal/                # QA-Logs, Dev-only
├── tools/                   # Hilfsprogramme, Dev-only
└── master-index.json        # Modul-Übersicht + Slot-Steuerung
```
