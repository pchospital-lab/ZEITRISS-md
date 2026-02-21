---
title: "ZEITRISS Setup & Repository Guide"
version: 4.2.6
tags: [meta, setup]
---

# ZEITRISS Setup & Repository Guide

Dieses Dokument beschreibt Setup, Plattform-Konfiguration und
Repository-Struktur für den aktuellen ZEITRISS-Stand. Spielinhalte und Regeln
findest du in der [README](../README.md).

**Versionshinweis:** Die Dokumentversion ist `4.2.6`; Preset- und
Masterprompt-Namen bleiben auf `v4.2.6` harmonisiert.

## Wissensspeicher & Plattform-Setup {#wissensspeicher--plattform-setup}

### KI-First-Onboarding (kanonischer Ablauf)

1. **Voraussetzungen:** OpenWebUI installieren und OpenRouter-Zugang
   vorbereiten.
2. **Aktuelles Repo bereitstellen:** Git-Clone oder GitHub-ZIP herunterladen,
   entpacken und in den Repo-Ordner wechseln.
3. **Script-Setup ausführen:** `./scripts/setup-openwebui.sh`.
4. **Start-Checks:** Masterprompt im Systemfeld + 20 Wissensslots geprüft,
   dann `Spiel starten (solo klassisch)`.

Dieser Ablauf ist der Referenzpfad für ZEITRISS im KI-Chatbetrieb und bleibt
zwischen README und Setup-Guide synchron.

### Vor jeder Session aktualisieren (Standard)

- Neuesten Repo-Stand ziehen (`git pull`) oder frischen ZIP-Stand entpacken.
- Setup-Script erneut starten (`./scripts/setup-openwebui.sh`).
- In OpenWebUI prüfen: Preset aktiv, Masterprompt gesetzt, Wissensspeicher mit
  20 Modulen verknüpft.

Die komplette Operator-Checkliste liegt repo-intern vor. Dort findet ihr die
Plattform-Workflows, Upload-Notizen sowie die Rollenaufteilung zwischen
Custom-GPT, Repo-Agent und Ingame-Kodex. Dieses README listet nur die
Laufzeitreferenz - bei Fragen zum Hochladen, Synchronisieren oder Testen führt
euch das Maintainer-Dokument.

### Wissensspeicher laden

**Am schnellsten (OpenWebUI):** Führe das Setup-Script aus — es erledigt alles
automatisch:

```bash
git clone https://github.com/pchospital-lab/ZEITRISS-md.git
cd ZEITRISS-md
./scripts/setup-openwebui.sh
```

Das Script erstellt die Knowledge Base, lädt das Spieler-Handbuch + 19 Runtime-Module
hoch und richtet das Preset mit Masterprompt ein. Vor dem Preset fragt das Script aktiv,
welches Base-Modell genutzt werden soll: Standard ist
`deepseek/deepseek-chat-v3-0324`, alternativ kannst du eine Model-ID manuell
eintragen oder über `ZEITRISS_MODEL` vorgeben. Danach: Browser auf, Modell
„ZEITRISS v4.2.6 – Local Uncut" (aktueller Preset-Name) wählen, dann möglichst
`Spiel starten (solo klassisch)` tippen.

Hinweis für laufenden Betrieb: Das erneute Ausführen des Scripts ist der
bevorzugte Update-Weg, damit Preset, Masterprompt-Feld und Wissensspeicher auf
dem neuesten Repo-Stand bleiben.

**Manuell (MyGPT, OpenWebUI, andere Plattformen):**

1. **20 Dateien in den Wissensspeicher laden:** `core/spieler-handbuch.md` plus
   alle 19 Runtime-Module aus der Tabelle unten. `master-index.json` bleibt ein
   repo-internes Steuerdokument und gehört **nicht** in den Wissensspeicher.
   `README.md` ist die GitHub-Landingpage und gehört ebenfalls **nicht** in den
   Wissensspeicher.
2. **Masterprompt als System-Prompt:** Kopiere `meta/masterprompt_v6.md`
   (Local-Uncut v4.2.6, aktueller Dateiname) als Systemprompt (MyGPT: Anweisungsfeld,
   OpenWebUI: Instruktionsfeld). Der Masterprompt gehört
   **nicht** in den Wissensspeicher — er wird ausschließlich als Systemfeld
   geladen.
3. **Slot-Kontrolle:** Prüfe nach jedem Speicherstand oder Plattform-Export, ob
   alle 20 Wissensmodule (Spieler-Handbuch + 19 Runtime-Module) weiterhin geladen sind.

### Runtime-Module im Wissensspeicher

| Kategorie      | Datei                                           |
| -------------- | ----------------------------------------------- |
| **core**       | `core/spieler-handbuch.md` *(Einleitung, Lore, Schnellstart, FAQ, Glossar)* |
| **core**       | `core/zeitriss-core.md`                         |
|                | `core/wuerfelmechanik.md`                       |
|                | `core/sl-referenz.md` *(Dispatcher, Regeln, Tabellen)* |
| **characters** | `characters/ausruestung-cyberware.md`           |
|                | `characters/charaktererschaffung-grundlagen.md` |
|                | `characters/charaktererschaffung-optionen.md`   |
|                | `characters/zustaende.md`                       |
|                | `characters/hud-system.md`                      |
| **gameplay**   | `gameplay/fahrzeuge-konflikte.md`               |
|                | `gameplay/kampagnenstruktur.md`                 |
|                | `gameplay/kampagnenuebersicht.md`               |
|                | `gameplay/kreative-generatoren-begegnungen.md`  |
|                | `gameplay/kreative-generatoren-missionen.md`    |
|                | `gameplay/massenkonflikte.md`                   |
| **systems**    | `systems/currency/cu-waehrungssystem.md`        |
|                | `systems/gameflow/cinematic-start.md`           |
|                | `systems/gameflow/speicher-fortsetzung.md`      |
|                | `systems/kp-kraefte-psi.md`                     |
|                | `systems/toolkit-gpt-spielleiter.md`            |

**Slot-Kennzeichnung:** In `master-index.json` sind das Spieler-Handbuch und die
19 Runtime-Module mit `"slot": true` markiert. Varianten-/Alias-Einträge tragen
`"slot": false` und zählen nicht als Wissensspeicher-Slot.

### Plattform-Setup

- **OpenWebUI + OpenRouter (empfohlen):** Setup-Script (s.o.) oder manuell: Modelle unter
  Einstellungen → Verbindungen anbinden, dann Dateien hochladen und Preset
  erstellen. Das Script zeigt dazu einen Kosten-/Datentransfer-Hinweis und fragt die
  Auswahl explizit ab. API-Keys werden beim Setup interaktiv abgefragt.

  **Empfohlene Modelle:**
  | Modell | Typ | Preis/1M Token | Stärke |
  |--------|-----|----------------|--------|
  | `deepseek/deepseek-chat-v3-0324` | **Default** | ~$0.27/$1.10 | Regeltreu, stabiler Noir-Ton, sehr günstig — klare Hauptempfehlung |
  | `meta-llama/llama-3.3-70b-instruct` | **Free-Empfehlung** | Kostenlos (OpenRouter) | Beste Gratis-Option für Einstieg, solide Regelstabilität |
  | `anthropic/claude-sonnet-4` | Optional | ~$3/$15 | Nutzbar, aber deutlich teurer und aktuell nicht bevorzugt |

  Temperatur: **0.8** für alle Modelle.
- **MyGPT (OpenAI, optional):** Funktionell derzeit nicht als Primärpfad empfohlen,
  weil Content-Filter häufiger eingreifen (`redacted`) und große Masterprompts in
  der Praxis limitieren können.
- **Lokale Modelle (Offline):** Perspektivisch interessant, aktuell für ZEITRISS oft
  noch zu leistungslimitiert. Für stabile Runs besser starke Remote-Modelle nutzen.
- **Template-Guard:** `{%`/`{{` aus Wissenssnippets ignorieren und niemals
  ausgeben, damit lokale Modelle nicht in Template-Modi kippen.



### Sicherheitsdefaults für OpenWebUI {#sicherheitsdefaults-fur-openwebui}

- **Header-Forwarding aus lassen:** `ENABLE_FORWARD_USER_INFO_HEADERS` nur in
  bewusst kontrollierten Enterprise-Setups aktivieren.
- **API-Keys getrennt halten:** Keine geteilten Admin-Tokens für Spielgruppen.
  Nutze pro Person/Account eigene Schlüssel.
- **RBAC aktiv pflegen:** Bei Mehrnutzerbetrieb Rollen und Gruppen explizit
  setzen; keine impliziten Admin-Pfade offen lassen.
- **Auth vor Netzfreigabe:** OpenWebUI nie ohne Login ins Internet hängen
  (insb. bei Reverse-Proxy/Portforwarding).
- **Remote-Provider bewusst einsetzen:** Externe Modellanbieter können Kosten
  verursachen und Eingaben verarbeiten. Keine sensiblen Daten in Prompts.

### Key-Notfallpfad (wenn versehentlich committed)

1. API-Key sofort beim Provider oder in OpenWebUI rotieren/revoken.
2. Betroffene Datei bereinigen und lokal gespeicherte Kopien prüfen.
3. Falls der Commit bereits gepusht wurde: History-Cleanup durchführen und den
   Vorgang als Security-Fall dokumentieren.
4. Danach Secret-Scanning/Push-Protection im Ziel-Repo prüfen.

### Runtimes & Tests außerhalb des Wissensspeichers

- `internal/runtime/runtime-stub-routing-layer.md`, `runtime.js`, Hilfsskripte und
  Test-Tools bleiben lokal im Repo und werden **nicht** in produktive
  Wissensspeicher hochgeladen.
- Spiegle relevante Laufzeitlogik (z. B. Foreshadow-Persistenz, HUD-Badges) als
  Regelwerk, Prozessbeschreibung oder Pseudocode innerhalb der Wissensbasis
  (README, `kb/`-Äquivalente, Runtime-Module), damit produktive GPTs ohne
  externe Skripte denselben Funktionsumfang erhalten.
- Nutze die lokalen Runtimes weiterhin für Entwicklung und Tests. Spiegel
  Anpassungen an Runtime-Logik zeitnah in den Wissensmodulen, damit der
  produktive Wissensspeicher konsistent bleibt.

## Repo-Map {#repo-map}

```
ZEITRISS-md/
├─ README.md                # Portal, Runtime-Referenz & Plattform-Hinweise
├─ core/                    # Grundregeln & Zeitriss-Mechaniken (Runtime)
├─ characters/              # Charaktererschaffung, Ausrüstung, Zustände (Runtime)
├─ gameplay/                # Kampagnenstruktur, Generatoren, Missionsbau (Runtime)
├─ systems/                 # Gameflow, Währungen, Toolkit für die KI-Spielleitung (Runtime)
├─ internal/qa/             # Interne Pläne/Logs (Meta-Artefakte)
├─ internal/runtime/        # Entwickler-Stubs (`runtime-stub-routing-layer.md`) & lokale Runtimes
├─ meta/                    # Masterprompts, Hintergrundbriefe, Dev-only Inhalte
├─ docs/                    # Maintainer-Ops, Lizenznotizen, Hosting-Strategie
│                           # (tags: [meta]; inkl. Fahrplan & Protokoll)
├─ scripts/, tools/         # Hilfsprogramme & Linter (Dev-only)
└─ master-index.json        # Übersicht aller Module/Slugs & Setup-Steuerung
```

### Dokumenten-Landkarte {#dokumenten-landkarte}

- **README (Portal & Runtime-Referenz)** - Einstieg für alle Rollen,
  Plattform-Setup und Deep-Links in die Runtime-Module.
- **Beitrags- & Agentenrichtlinien (repo-intern)** - Arbeitsgrundlage für
  Beitragende und Repo-Agenten, inkl. Prüfpfade, Compliance und QA-Hinweise.
- **Maintainer-Handbuch (repo-intern)** - Upload-Workflows, Plattformpflege und
  Runtime-Spiegelungen.
- **Impressum (repo-intern)** - Rechtliche Pflichtangaben und Kontakt für
  Lizenzanfragen.
- **Hintergrund- & Strategie-Notizen (repo-intern)** - Lizenz-,
  Hosting- und Entwicklungsnotizen, nicht für den Wissensspeicher gedacht.
- **Masterprompts (repo-intern)** - Laufzeit-Briefings für MyGPT; enthalten
  keine Dev-Vorgaben wie Agentenregeln.

## Wie du beitragen kannst

Hinweise zum Einreichen von Änderungen sowie Schreibregeln
liegen repo-intern in den Beitragsrichtlinien vor.
Für lokale Checks nutze die dort beschriebene `pre-commit`-Integration.

Die Inhalte stehen für private kreative Nutzung bereit.
ZEITRISS® ist eine beim DPMA eingetragene Wortmarke (Reg.-Nr. 30 2025 215 671).
Eine 1:1-Kopie oder kommerzielle Veröffentlichung ist nur mit Zustimmung
erlaubt (siehe [LICENSE](../LICENSE)).
Gemäß Lizenz richten sich diese Regeln ausschließlich an Erwachsene (18+).

### Acceptance-Smoke-Checkliste

Die vollständige 15-Punkte-Checkliste für QA-/Beta-Läufe ist als Runtime-
Spiegel im [Toolkit](../systems/toolkit-gpt-spielleiter.md#acceptance-smoke)
verfügbar, damit produktive GPT-Instanzen die Prüfpunkte intern referenzieren
können. Die ausführliche Version mit Goldenfiles und Traces liegt in
[`docs/qa/tester-playtest-briefing.md`](qa/tester-playtest-briefing.md#acceptance-smoke-checkliste).
