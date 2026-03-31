---
title: "ZEITRISS Setup-Guide"
version: 4.2.6
tags: [meta, setup]
---

# ZEITRISS Setup-Guide

Technische Details zu Setup, Plattform-Konfiguration und Repository-Struktur.
Spielinhalte und Regeln findest du in der [README](../README.md).

## Schnellstart

```bash
git clone https://github.com/pchospital-lab/ZEITRISS-md.git
cd ZEITRISS-md
python scripts/setup.py
```

Das Script führt interaktiv durch: API-Key, Modellauswahl, Knowledge Base,
Preset. Danach: `ZEITRISS v4.2.6 Uncut` als Modell wählen, neuen Chat
starten.

**Vor jeder Session:** `git pull` und `python scripts/setup.py` erneut
ausführen — aktualisiert Wissensspeicher und Preset auf den neuesten Stand.

## Setup-Script Modi

| Befehl | Was passiert |
| ------ | ------------ |
| `python scripts/setup.py` | OpenWebUI-Setup (KB + Dateien + Preset) |
| `python scripts/setup.py --export` | Export-Paket für Lumo und andere Plattformen |
| `python scripts/setup.py --export --flat` | Export mit nummerierten Dateien (kein Nesting) |
| `python scripts/setup.py --export -o ~/Desktop` | Export in ein bestimmtes Verzeichnis |

**Umgebungsvariablen (optional):**

| Variable | Wirkung |
| -------- | ------- |
| `OPENWEBUI_URL` | OpenWebUI-Adresse (Standard: `http://localhost:3000`) |
| `OPENWEBUI_API_KEY` | API-Key (sonst interaktiv) |
| `ZEITRISS_MODEL` | Base-Model-ID (sonst interaktiv) |

## Manuelles Setup (ohne Script)

### 1. Knowledge Base

Erstelle in OpenWebUI eine Knowledge Base `ZEITRISS 4.2.6 Regelwerk` und
lade die 19 Wissensmodule hoch:

| Kategorie | Dateien |
| --------- | ------- |
| **core** | `spieler-handbuch.md`, `zeitriss-core.md`, `wuerfelmechanik.md`, `sl-referenz.md` |
| **characters** | `charaktererschaffung-grundlagen.md`, `ausruestung-cyberware.md`, `zustaende.md`, `hud-system.md` |
| **gameplay** | `kampagnenstruktur.md`, `kampagnenuebersicht.md`, `kreative-generatoren-missionen.md`, `kreative-generatoren-begegnungen.md`, `fahrzeuge-konflikte.md`, `massenkonflikte.md` |
| **systems** | `kp-kraefte-psi.md`, `cu-waehrungssystem.md`, `speicher-fortsetzung.md`, `cinematic-start.md`, `toolkit-gpt-spielleiter.md` |

**Nicht hochladen:** `README.md`, `master-index.json`, Archiv-Dateien.

**Optional:** `characters/charaktererschaffung-optionen.md` (Inspiration für
One-Shots, nicht im Default-Set).

Welche Dateien als Slot gelten, bestimmt `master-index.json` (`"slot": true`).

### 2. Modell-Preset

Unter Modelle → Neues Modell:

- **Name:** `ZEITRISS v4.2.6 Uncut`
- **Base-Modell:** `anthropic/claude-sonnet-4.6` (empfohlen)
- **System-Prompt:** Inhalt von `meta/masterprompt_v6.md` komplett einfügen.
  Gehört **nicht** in den Wissensspeicher.
- **Wissensbasis:** `ZEITRISS 4.2.6 Regelwerk` verknüpfen
- **Capabilities:** Vision und Usage **aus**

### 3. Parameter

| Parameter | Wert | Warum |
| --------- | ---- | ----- |
| Temperature | **0.8** | Kreativ genug für Noir, stabil genug für Regeltreue |
| Top-P | **0.9** | Reduziert Halluzinationen |
| Frequency Penalty | **0.3** | Verhindert Wiederholungen in langen Sessions |
| Max Tokens | **64000** | Reicht für Gruppen-Saves + Debrief |

### 4. Spielen

Neuen Chat öffnen → Preset wählen → `Spiel starten (solo klassisch)` oder
natürlich formulieren. `solo schnell` als Fast-Lane für Kurzrunden.

## Modelle (Stand März 2026)

> **Sonnet 4.6 ist das einzige Modell mit vollständiger Regeltreue.**
> Budget-Modelle erzählen atmosphärisch, erfinden aber eigene Würfelsysteme.

| Modell | Typ | Preis/1M Token | Stärke |
| ------ | --- | -------------- | ------ |
| `anthropic/claude-sonnet-4.6` | **Empfohlen** | ~$3/$15 | Korrekte Mechanik, HUD, Px |
| `z-ai/glm-5-turbo` | **Budget** | Günstig | Erkennt Regelgates, 7× billiger |
| `deepseek/deepseek-v3.2` | **Ultra-Budget** | ~$0.25/$0.40 | ~$0.002/Turn, Regeln teils abweichend |
| `z-ai/glm-5` | **Experimentell** | ~$0.40/$1.71 | Guter Noir-Ton, halluziniert teils |

## Andere Plattformen

### Lumo (Proton)

Eigene Anleitung: [`docs/setup-lumo.md`](setup-lumo.md)

Kurzfassung: `python scripts/setup.py --export`, dann den `knowledge/`-Ordner
nach Proton Drive kopieren und im Lumo-Projekt verlinken.

### Sonstige (Claude Projects, lokale Modelle etc.)

`python scripts/setup.py --export` erzeugt ein plattformunabhängiges Paket
mit Setup-Anleitung. Für Plattformen ohne Ordner-Support:
`python scripts/setup.py --export --flat` (nummerierte Dateien).

## Sicherheit

- **API-Keys getrennt halten:** Keine geteilten Admin-Tokens für Spielgruppen.
- **Auth vor Netzfreigabe:** OpenWebUI nie ohne Login ins Internet hängen.
- **Remote-Provider:** Können Kosten verursachen und Eingaben verarbeiten.
  Keine sensiblen Daten in Prompts.
- **Key versehentlich committed?** Sofort rotieren/revoken, Datei bereinigen,
  History-Cleanup falls gepusht.

## Repo-Map

```
ZEITRISS-md/
├─ README.md                # Portal & Schnellstart
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
