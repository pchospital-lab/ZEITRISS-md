---
title: "ZEITRISS Setup-Guide"
version: 4.2.6
tags: [meta, setup]
---

# ZEITRISS Setup-Guide

Alles rund um Installation, Konfiguration und Betrieb. Spielinhalte und
Regeln findest du im [Spieler-Handbuch](../core/spieler-handbuch.md), der
Schnellstart lebt in der [README](../README.md).

---

## Inhalt

1. [Voraussetzungen](#voraussetzungen)
2. [Schnellstart (OpenWebUI)](#schnellstart-openwebui)
3. [Was das Script genau tut](#was-das-script-genau-tut)
4. [Aktualisieren und nach Upgrades](#aktualisieren-und-nach-upgrades)
5. [Troubleshooting](#troubleshooting)
6. [Script-Referenz](#script-referenz)
7. [Andere Plattformen](#andere-plattformen)
8. [Manuelles Setup](#manuelles-setup)
9. [Modelle](#modelle)
10. [Sicherheit](#sicherheit)
11. [Repo-Struktur](#repo-struktur)

---

## Voraussetzungen

1. **[OpenWebUI](https://github.com/open-webui/open-webui)** — eure
   Spieloberfläche (kostenlos, self-hosted).
2. **Modellzugang** — lokal (Ollama) oder Cloud-Provider wie
   [OpenRouter](https://openrouter.ai). In OpenWebUI unter
   Einstellungen → Verbindungen eintragen.
3. **[Python 3.8+](https://python.org)** — auf macOS/Linux meist
   vorinstalliert, auf Windows einmal von python.org holen.
4. **API-Key** für deinen Provider.

> 💡 **Was ist ein API-Key?**
> Wie ein persönliches Passwort für eine KI-Schnittstelle. Account auf
> [openrouter.ai](https://openrouter.ai) anlegen, Key erzeugen, ZEITRISS
> nutzt ihn für Anfragen. Budget-Modelle kosten oft unter **0,01 € pro Runde**
> — Cent-Beträge, kein Abo, nur was du nutzt.
>
> Kein Terminal zur Hand? → [Wie öffne ich ein Terminal?](terminal-help.md)

---

## Schnellstart (OpenWebUI)

**Per Git (empfohlen, einfach updatebar):**

```bash
git clone https://github.com/pchospital-lab/ZEITRISS-md.git
cd ZEITRISS-md
python scripts/setup.py
```

**Per ZIP (ohne Git):**

1. Oben im Repo **Code → Download ZIP** klicken.
2. ZIP entpacken, Terminal/Eingabeaufforderung im Ordner öffnen.
3. `python scripts/setup.py` ausführen.

Das Script fragt API-Key und Modellauswahl ab und legt dann automatisch an:
- Knowledge Base mit 19 Wissensmodulen
- Preset `ZEITRISS v4.2.6 Uncut` mit Parametern und Masterprompt

**Danach:** Neuen Chat in OpenWebUI öffnen → Modell `ZEITRISS v4.2.6 Uncut`
wählen → `Spiel starten (solo klassisch)` tippen. `solo schnell` als
Fast-Lane für Kurzrunden. Startbefehle funktionieren auch in natürlicher
Sprache.

---

## Was das Script genau tut

Für alle, die wissen wollen, was im Hintergrund passiert:

1. **Verbindung prüfen** — API-Key, Health-Check, Auth.
2. **Embedding-Engine-Precheck** — liest die aktuelle Konfiguration und
   warnt bei unbekannten Engines.
3. **Altes Preset aufräumen** — falls ein Upgrade die ID verwaist hat.
4. **Alte Knowledge Base entfernen** — inklusive aller darin verknüpften
   Dateien.
5. **19 Wissensdateien hochladen** und an die neue KB verknüpfen.
6. **Preset anlegen/aktualisieren** — Masterprompt, Parameter, KB-Bindung,
   Icon.
7. **Retrieval-Check** — eine Canary-Query fragt die KB direkt ab und
   prüft, ob die erwarteten Regel-Phrasen als Chunks zurückkommen.
   Nur wenn das grün ist, gilt das Setup als erfolgreich.

Der Retrieval-Check ist der eigentliche Knackpunkt: Er entscheidet final,
ob Setup gelungen ist, unabhängig davon, was einzelne API-Calls melden.

---

## Aktualisieren und nach Upgrades

### Normale Updates

Neues ZIP laden (oder `git pull`) und das Script nochmal starten — fertig.
Es räumt das alte Preset und die alte Knowledge Base weg und baut alles
frisch auf.

```bash
git pull
python scripts/setup.py
```

### Nach OpenWebUI-Major-Upgrades

Einfach wieder `python scripts/setup.py` laufen lassen. Das Script
erkennt und behebt die häufigsten Konfigurations-Drifts nach Updates
selbst. Wenn nach einem Upgrade trotzdem etwas nicht passt: siehe
[Troubleshooting](#troubleshooting).

---

## Troubleshooting

### „Die SL antwortet, aber Regeln klingen falsch"

Das Retrieval zieht vermutlich keine Regeln aus der Knowledge Base.
Erst Script nochmal laufen lassen:

```bash
python scripts/setup.py
```

Wenn der Fehler bleibt, ist wahrscheinlich die Embedding-Engine in
OpenWebUI durcheinander (häufig nach Major-Upgrades). Zurück auf den
sicheren Standard:

```bash
python scripts/setup.py --embedding default
```

Das setzt die Engine explizit auf das eingebaute MiniLM-Modell und baut
danach alles neu auf.

### „Das Script meldet Fehler beim Verknüpfen der Dateien"

Kein Problem. Der Verknüpfungs-Endpunkt von OpenWebUI meldet manchmal
spurious HTTP-Fehler. Entscheidend ist der **Retrieval-Check** am Ende:
Solange dort `KB-Retrieval funktioniert` steht, sind alle 19 Dateien
korrekt eingebunden.

### „Ich habe einen komplett zerschossenen Zustand"

Wenn gar nichts mehr hilft und du sauber neu aufsetzen willst:

```bash
python scripts/setup.py --reset-embeddings --embedding default
```

`--reset-embeddings` räumt zusätzlich verwaiste Vektor-Ordner auf, bevor
die neue KB angelegt wird. In Kombination mit `--embedding default`
bekommst du einen garantiert sauberen Neuanfang.

### „Ich will Ollama als Embedding-Engine"

```bash
python scripts/setup.py --embedding ollama
```

Voraussetzung: Ollama läuft lokal und OpenWebUI kann es erreichen
(typischerweise `http://host.docker.internal:11434`). Der empfohlene
Embedder `nomic-embed-text` wird automatisch gesetzt.

Für Normalnutzer ohne eigenes Ollama ist der Default (MiniLM) völlig
ausreichend. Ollama lohnt sich nur, wenn du ohnehin eine lokale
LLM-Pipeline fährst.

### „Setup hängt bei der URL-Abfrage"

Setze Umgebungsvariablen, dann fragt das Script nichts:

```bash
export OPENWEBUI_URL=http://localhost:3000
export OPENWEBUI_API_KEY=sk-...
python scripts/setup.py -y
```

Mit `-y` verzichtet das Script auf Modell-Rückfrage und nimmt den Default
aus `setup.json`.

---

## Script-Referenz

### Kommandos

| Befehl | Was passiert |
| ------ | ------------ |
| `python scripts/setup.py` | OpenWebUI-Setup, interaktiv |
| `python scripts/setup.py --export` | Export-Paket für Lumo, Claude Projects, etc. |
| `python scripts/setup.py --export --flat` | Flat-Export mit nummerierten Dateien |
| `python scripts/setup.py --export -o ~/Desktop/pack` | Export in Custom-Pfad |

### Flags

| Flag | Wirkung |
| ---- | ------- |
| `-y`, `--yes` | Keine Rückfragen. URL = `http://localhost:3000`, Modell = Default |
| `--embedding default` | Setzt Embedding explizit auf MiniLM (OpenWebUI-built-in) |
| `--embedding ollama` | Setzt Embedding auf Ollama + `nomic-embed-text` |
| `--ollama-url URL` | Custom Ollama-Endpoint (Default: `http://host.docker.internal:11434`) |
| `--ollama-model NAME` | Anderes Ollama-Embedding-Modell (Default: `nomic-embed-text`) |
| `--reset-embeddings` | Löscht verwaiste Vektor-Collections vor Rebuild |
| `--no-verify` | Überspringt den Retrieval-Check (nicht empfohlen) |
| `--strict` | Exit-Code 2 bei fehlgeschlagenem Retrieval-Check (für CI/CD) |

### Umgebungsvariablen

| Variable | Wirkung |
| -------- | ------- |
| `OPENWEBUI_URL` | OpenWebUI-Adresse (Default: `http://localhost:3000`) |
| `OPENWEBUI_API_KEY` | API-Key (sonst interaktiv) |
| `ZEITRISS_MODEL` | Base-Model-ID (sonst interaktiv) |

---

## Andere Plattformen

### Lumo (Proton)

Ausführliche Anleitung: [`docs/setup-lumo.md`](setup-lumo.md)

Kurz: `python scripts/setup.py --export` erzeugt ein Paket, dann
`knowledge/`-Ordner nach Proton Drive kopieren und im Lumo-Projekt
verlinken.

### Claude Projects und andere

`python scripts/setup.py --export` erzeugt ein plattformunabhängiges
Paket mit Setup-Anleitung drin. Für Plattformen ohne Ordner-Support:
`--export --flat` nimmt nummerierte Flat-Dateien.

### Funktioniert auf allen Plattformen?

- ✅ **OpenWebUI + starkes Modell** — optimale Erfahrung.
- ✅ **Lumo / Claude Projects** — funktioniert, wenn die Plattform genug
  System-Prompt-Platz bietet.
- ⚠️ **Custom GPTs (OpenAI)** — eingeschränkt, Prompt-Limit zu klein,
  18+-Content wird teils redacted.
- ⚠️ **Schwache Modelle** — kommen an Grenzen. ZEITRISS braucht Modelle,
  die komplexe Regelsysteme + Kreativität + Pacing gleichzeitig können.

---

## Manuelles Setup

Wenn du das Script nicht nutzen willst oder kannst:

### 1. Knowledge Base

Erstelle in OpenWebUI eine KB namens `ZEITRISS 4.2.6 Regelwerk` und lade
die 19 Wissensmodule hoch:

| Kategorie | Dateien |
| --------- | ------- |
| **core** | `spieler-handbuch.md`, `zeitriss-core.md`, `wuerfelmechanik.md`, `sl-referenz.md` |
| **characters** | `charaktererschaffung-grundlagen.md`, `ausruestung-cyberware.md`, `zustaende.md`, `hud-system.md` |
| **gameplay** | `kampagnenstruktur.md`, `kampagnenuebersicht.md`, `kreative-generatoren-missionen.md`, `kreative-generatoren-begegnungen.md`, `fahrzeuge-konflikte.md`, `massenkonflikte.md` |
| **systems** | `kp-kraefte-psi.md`, `cu-waehrungssystem.md`, `speicher-fortsetzung.md`, `cinematic-start.md`, `toolkit-gpt-spielleiter.md` |

**Nicht hochladen:** `README.md`, `master-index.json`, Archiv-Dateien.

**Optional:** `characters/charaktererschaffung-optionen.md` (Inspiration
für One-Shots, nicht im Default-Slotset).

Welche Dateien als Slot gelten, bestimmt `master-index.json`
(`"slot": true`).

### 2. Modell-Preset

Unter Modelle → Neues Modell:

- **Name:** `ZEITRISS v4.2.6 Uncut`
- **Base-Modell:** `anthropic/claude-sonnet-4.6` (empfohlen)
- **System-Prompt:** Inhalt von `meta/masterprompt_v6.md` komplett
  einfügen. Gehört **nicht** in den Wissensspeicher.
- **Wissensbasis:** `ZEITRISS 4.2.6 Regelwerk` verknüpfen.
- **Capabilities:** Vision und Usage **aus**.

### 3. Parameter

| Parameter | Wert | Warum |
| --------- | ---- | ----- |
| Temperature | **0.8** | Kreativ genug für Noir, stabil genug für Regeltreue |
| Top-P | **0.9** | Reduziert Halluzinationen |
| Frequency Penalty | **0.3** | Verhindert Wiederholungen in langen Sessions |
| Max Tokens | **64000** | Reicht für Gruppen-Saves + Debrief |

### 4. Spielen

Neuen Chat öffnen → Preset wählen → `Spiel starten (solo klassisch)`
oder natürlich formulieren. `solo schnell` als Fast-Lane für Kurzrunden.

---

## Modelle

> **Sonnet 4.6 ist das einzige Modell mit vollständiger Regeltreue.**
> Budget-Modelle erzählen atmosphärisch, erfinden aber eigene
> Würfelsysteme, wenn man sie lässt.

| Modell | Typ | Preis/1M Token | Stärke |
| ------ | --- | -------------- | ------ |
| `anthropic/claude-sonnet-4.6` | **Empfohlen** | ~$3/$15 | Korrekte Mechanik, HUD, Px |
| `z-ai/glm-5-turbo` | **Budget** | Günstig | Erkennt Regelgates, 7× billiger |
| `deepseek/deepseek-v3.2` | **Ultra-Budget** | ~$0.25/$0.40 | ~$0.002/Turn, Regeln teils abweichend |
| `z-ai/glm-5` | **Experimentell** | ~$0.40/$1.71 | Guter Noir-Ton, halluziniert teils |

Ergebnisse aus dem
[Modellvergleich 2026-03-17](../internal/qa/evidence/playtest-2026-03-17/AUSWERTUNG.md)
(5 Szenarien × 4 Modelle, Scorecard-Methodik).

---

## Sicherheit

- **API-Keys getrennt halten** — keine geteilten Admin-Tokens für
  Spielgruppen.
- **Auth vor Netzfreigabe** — OpenWebUI nie ohne Login ins Internet
  hängen.
- **Remote-Provider** können Kosten verursachen und Eingaben verarbeiten.
  Keine sensiblen Daten in Prompts.
- **Key versehentlich committed?** Sofort rotieren/revoken, Datei
  bereinigen, History-Cleanup falls gepusht.

---

## Repo-Struktur

```
ZEITRISS-md/
├─ README.md                # Landingpage & Schnellstart
├─ setup.json               # Projekt-Config für setup.py
├─ core/                    # Grundregeln & Zeitriss-Mechaniken
├─ characters/              # Charaktererschaffung, Ausrüstung, Zustände
├─ gameplay/                # Kampagnenstruktur, Generatoren, Missionsbau
├─ systems/                 # Gameflow, Währungen, KI-SL-Toolkit
├─ meta/                    # Masterprompts, Hintergrundbriefe
├─ docs/                    # Setup-Guides, Lizenz, Maintainer-Ops
├─ scripts/                 # setup.py, Linter, Smoke-Tests
├─ internal/                # QA-Logs, Runtime-Stubs (Dev-only)
├─ tools/                   # Hilfsprogramme (Dev-only)
└─ master-index.json        # Modulübersicht & Slot-Steuerung
```
