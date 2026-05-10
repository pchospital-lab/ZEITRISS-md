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
2. [Was der Launcher dir anbietet](#was-der-launcher-dir-anbietet)
3. [Komplett-Setup in OpenWebUI (empfohlen)](#komplett-setup-in-openwebui-empfohlen)
4. [Updates und Wartung](#updates-und-wartung)
5. [Weiterführendes](#weiterführendes-gruppenspiel-lokal-gpu-variante-portabler-export)
   — Gruppenspiel, Lokal-GPU-Variante, Export
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
│    ├──► LiteLLM (Docker, Pflicht) ──► OpenRouter ──► Sonnet 4.6     │
│    │      [aktiviert Prompt-Cache: ~90 % Ersparnis]                  │
│    │                                                                 │
│    └──► Ollama (optional, Lokal-GPU-Variante, ungetestet):          │
│           • als Sprachmodell (offline spielen, statt OpenRouter)     │
│           • als Embedding-Engine (KB lokal indexieren, statt MiniLM) │
└──────────────────────────────────────────────────────────────────────┘
```

| Komponente | Pflicht? | Wofür |
| --- | --- | --- |
| **OpenWebUI** (Docker-Container) | ✅ Pflicht | Chat-Oberfläche, hier spielt ihr |
| **ZEITRISS-Repo + Python** | ✅ Pflicht | Regelwerk + Setup-Script |
| **OpenRouter-Key** | ✅ Pflicht¹ | Modellzugang (Cloud, günstig pay-per-token) |
| **OpenWebUI-API-Key** | ✅ Pflicht | damit Setup-Script Preset + KB schreiben kann |
| **LiteLLM** (Docker-Container) | ✅ Pflicht (Golden Setup) | Prompt-Cache für Sonnet 4.6 (~90 % Ersparnis); bleibt auch bei Lokal-GPU-Variante aktiv, damit du jederzeit zwischen Cloud und Lokal umschalten kannst |
| **Ollama** | ⚪ Optional (ungetestet) | Lokal-GPU-Variante: Sprachmodell **und/oder** Embedding |

¹ Bei der reinen Lokal-GPU-Variante (Ollama als Sprachmodell, ohne Cloud-Fallback) optional. Empfohlen bleibt der Cloud-Key als Rückfallebene.

> 💡 **Was ihr selbst braucht, was der Launcher macht:** Ihr installiert
> einmalig **Docker** und **Python** und legt zwei **API-Keys** an
> (OpenRouter + OpenWebUI). Alles andere - OpenWebUI-Docker-Container,
> LiteLLM-Docker-Container, Preset, Knowledge Base, Retrieval-Check -
> macht der Launcher (`python scripts/zeitriss.py`). Die Lokal-GPU-Variante
> (Ollama) ist optional und ungetestet - passende Hardware vorausgesetzt
> (siehe unten).

---

## Was der Launcher dir anbietet

Der Launcher (`python scripts/zeitriss.py`) ist der zentrale Einstieg
für alles Setup-Bezogene. Er bietet zwei Installationswege:

**[1] Komplett-Setup in OpenWebUI (empfohlen).** Der offiziell
getestete Referenzpfad — OpenWebUI + OpenRouter + Claude Sonnet 4.6 +
LiteLLM-Cache. Ein Launcher-Klick, der Launcher führt dich durch
alles. Alle Regel-QA ist gegen diesen Stack kalibriert — darauf testen
wir, und darauf entwickeln wir weiter. →
[Komplett-Setup in OpenWebUI unten](#komplett-setup-in-openwebui-empfohlen)

**[2] Regelwerk woanders nutzen (Export-Paket, ohne Gewähr).** Du
willst auf einer anderen Chat-Plattform spielen, die System-Prompts
und Wissensdateien verwaltet? Der Launcher erzeugt dir ein
Export-Paket. Du importierst es manuell in deine Plattform. **Wir
testen nicht gegen andere Plattformen, Regel-Glitches sind
möglich** — das ist Do-it-yourself-Terrain. →
[Portabler Export unten](#portabler-export-ohne-gewähr)

### Getestet / ungetestet

**Getestet und kalibriert:** OpenWebUI + OpenRouter + Sonnet 4.6 + LiteLLM.
Die gesamte Regel-QA (Probenformeln, HUD, Px-Logik, Retrieval-Checks) läuft
gegen diesen Stack. Wer hier bleibt, spielt auf dem Stand, gegen den wir
selbst testen.

**Nicht kalibriert, technisch möglich, DIY:**

- **Andere Chat-Plattformen** (Export-Paket, Menu [2]) — Retrieval- und
  System-Prompt-Verhalten variiert, Regel-Glitches sind möglich.
- **Lokale Sprachmodelle** via Ollama — ZEITRISS ist regel-komplex,
  Modelle unter der 70B-Klasse kommen schnell an Grenzen. Consumer-GPUs
  reichen typischerweise nicht; eine Workstation-Klasse (z.B.
  Framework-Ryzen-Max-128GB oder vergleichbar) kann das stemmen, sobald
  fähige Modelle kompakt genug werden. Aktuell keine Test-Abdeckung.
- **Lokale Embedding-Engine** via Ollama — reine KB-Indizierung, läuft,
  aber der Default-MiniLM reicht für 19 Dateien ebenso.

Feedback zu allen Pfaden gerne als Issue — aktive Fehlersuche oder
Support leisten wir nur für den Golden Setup.

---

## Komplett-Setup in OpenWebUI (empfohlen)

Dieser Pfad richtet OpenWebUI + OpenRouter + LiteLLM-Cache ein - den
offiziellen Referenz-Stack. Du installierst selbst nur **Docker und
Python**, den Rest erledigt der Launcher (`python scripts/zeitriss.py`).

> i️ **Zeitaufwand beim ersten Mal:** 30-60 Minuten (inklusive
> Docker- und Python-Installation). Reine Launcher-Laufzeit ohne
> Installation: 5-10 Minuten. Updates später: 1-2 Minuten.

---

### Schritt 1 - Docker installieren

Docker ist die Voraussetzung für OpenWebUI und LiteLLM - beide laufen
als Docker-Container auf deinem Rechner. Den Launcher interessiert
das nicht, er ruft einfach `docker`-Befehle auf. Docker muss also
**einmal installiert und gestartet** sein, bevor der Launcher läuft.

1. **Installieren:** <https://docs.docker.com/get-docker/>
   - Windows/macOS: "Docker Desktop" herunterladen und installieren.
   - Linux: je nach Distro, z. B. Ubuntu/Debian `sudo apt install docker.io`.
2. **Starten:**
   - Windows/macOS: Docker Desktop öffnen (Wal-Icon in der Taskleiste/
     Menüleiste), warten bis der Status "Docker Desktop is running"
     erscheint (1-2 Min beim ersten Mal).
   - Linux: `sudo systemctl start docker` (und optional
     `sudo systemctl enable docker` für Autostart nach Reboot).
3. **Test:** `docker ps` im Terminal. Wenn eine leere Tabelle
   erscheint (nur Kopfzeile), läuft Docker. Fehlermeldungen wie
   "Cannot connect to the Docker daemon" bedeuten: Docker ist zwar
   installiert, aber nicht gestartet.

---

### Schritt 2 - Python 3 installieren

Der Launcher ist ein Python-Script. Du brauchst Python 3.9 oder neuer.

- **macOS:** meist vorinstalliert. Testen: `python3 --version`. Wenn
  nicht vorhanden, `brew install python3` oder von <https://python.org>.
- **Linux:** meist vorinstalliert. Wenn nicht: `sudo apt install python3`.
- **Windows:** Installer von <https://python.org> holen.

> ⚠️ **Windows-Stolperfalle:** Beim Python-Installer den Haken bei
> **"Add Python to PATH"** setzen. Ohne den Haken kennt die
> Eingabeaufforderung den `python`-Befehl nicht, und der Launcher
> startet nicht.
>
> Kein Terminal zur Hand? → [Wie öffne ich ein Terminal?](terminal-help.md)

---

### Schritt 3 - OpenRouter-Account + Key besorgen

OpenRouter liefert das Sprachmodell (Claude Sonnet 4.6, pay-per-token,
kein Abo). Du brauchst **einen Account, ein kleines Guthaben und einen
API-Key**.

1. **Account anlegen:** <https://openrouter.ai> → "Sign Up".
2. **Guthaben einzahlen:** <https://openrouter.ai/credits> - 5 USD
   reichen für viele Spielstunden (mit aktivem LiteLLM-Cache in
   Schritt 6 werden daraus ~20+ Spielstunden).
3. **Privacy-Einstellung setzen:** <https://openrouter.ai/settings/privacy>
   → in der Provider-Liste **Anthropic** auf *Allowed / Erlaubt* setzen
   (meistens ein Toggle-Schalter oder eine Checkbox). AWS Bedrock ist
   eine Alternative zu Anthropic, beides zusammen schadet nicht. Ohne
   diesen Schritt blockiert OpenRouter später den LiteLLM-Cache, und
   die ~90-%-Ersparnis ist weg.
4. **Key erzeugen:** <https://openrouter.ai/keys> → "Create Key" →
   Namen vergeben (z. B. "zeitriss") → Key kopieren. Er beginnt mit
   `sk-or-v1-...`. **Key jetzt sofort wegspeichern** (Notiz-App,
   Passwort-Manager) - OpenRouter zeigt ihn dir nur einmal.

---

### Schritt 4 - ZEITRISS klonen

```bash
git clone https://github.com/pchospital-lab/ZEITRISS-md.git
cd ZEITRISS-md
```

Kein Git installiert? Zwei Möglichkeiten:

- **Git installieren:** <https://git-scm.com/downloads> (empfohlen,
  weil Updates via Launcher-Menüpunkt [4] dann out-of-the-box
  funktionieren).
- **ZIP-Download:** Auf GitHub "Code → Download ZIP" klicken, entpacken,
  Terminal im entpackten Ordner öffnen. Funktioniert, aber Updates
  musst du dann per erneutem ZIP-Download holen - inkrementelles `--sync`
  braucht ein Git-Repo.

---

### Schritt 5 - Launcher starten

```bash
python scripts/zeitriss.py
```

Unter Windows alternativ **Doppelklick auf `zeitriss.bat`**, unter
macOS/Linux alternativ `./zeitriss.sh`.

Der Launcher zeigt dir oben einen Status-Block (Python/Docker/OpenWebUI/
Keys als ✓ oder -) und ein Menü, gruppiert in *Einrichtung* und
*Im Betrieb*:

```
  ── Einrichtung (wähle einen Weg) ──────────────
   [1]  Komplett-Setup in OpenWebUI (empfohlen, Golden Setup)
   [L]  Lore-Setup — wie [1], eingerahmt als ITI-Bergung
   [2]  Regelwerk woanders nutzen (Export-Paket, ohne Gewähr)

  ── Im Betrieb ──────────────────────────────
   [3]  Spiel starten (Browser öffnen)
   [4]  ZEITRISS aktualisieren (git pull + Sync)
   [5]  API-Keys ändern
   [6]  Bei mir läuft was nicht (Diagnose)
   [7]  Reset — Neuinstallation (⚠ destruktiv)

   [X]  Beenden
```

Unten steht eine Eingabezeile **`Auswahl:`**. Für die Erstinstallation
tipp **`1`** und drück Enter.

#### Lore-Setup (optional)

Der Launcher bietet zusätzlich den Menüpunkt **`[L]  Lore-Setup`**.
Da läuft exakt dasselbe Setup wie unter `[1]`, nur in einen kurzen
Kodex-Funkspruch eingerahmt (Prolog im Terminal vor dem Setup, Welcome-
Box danach). Pure Kosmetik: die eigentliche Installation, alle Fehler-
meldungen und Retries bleiben genau wie im Standardpfad sichtbar.

Für Screenshots/QA: `ZEITRISS_RITE_INSTANT=1` schaltet die Typewriter-
Animation aus, alles erscheint sofort.

Designnotizen: siehe [`docs/first-contact-rite.md`](first-contact-rite.md).

#### Reset — Neuinstallation (destruktiv)

Menüpunkt **`[7]  Reset — Neuinstallation`** räumt den ZEITRISS-Zustand
in OpenWebUI komplett weg und startet danach automatisch ein frisches
`[1]`-Setup. Gedacht für Situationen, in denen `[6] Diagnose` zwar einen
Fehler findet, aber der Auto-Fix nicht reicht (z.B. nach kaputtem Upgrade
oder manuellen Edits, die sich nicht mehr per Sync einfangen lassen).

Bevor irgendwas gelöscht wird, zeigt der Launcher eine **konkrete
Trefferliste**: welche Presets, KBs und das Sync-Manifest auf deiner
Instanz tatsächlich entfernt würden. Danach zwei Bestätigungen:
LiteLLM-Container-Wahl (Default n, bleibt also drin) und Typo-Schutz
(Wort `RESET` in Großbuchstaben tippen).

Gelöscht werden: das ZEITRISS-Preset, die projektzugehörige Knowledge
Base samt Vektoren und hochgeladenen Dateien, das lokale Sync-Manifest
(`.openwebui-sync.json`). Behalten bleiben: der OpenWebUI-Container samt
Admin-Account, deine API-Keys in `~/.openwebui_env`, alle anderen
Presets/KBs in deiner OpenWebUI-Installation.

> ⚠️ **KB-Präfix-Matching.** Der Reset löscht alle KBs, deren Name mit
> dem Projektnamen (`ZEITRISS`) beginnt. Wer eine manuelle Backup-KB mit
> einem Namen wie `ZEITRISS-BACKUP` pflegt, sollte sie vor dem Reset
> umbenennen — der Launcher zeigt vor der Bestätigung eine Trefferliste,
> dort sieht man's rechtzeitig.

---

### Schritt 6 - Was der Launcher dich jetzt fragt

> 💡 **Der Launcher ist dein Reiseleiter.** Er sagt dir im Terminal an
> jeder Stelle selbst, was zu tun ist - inklusive dem Browser-Teil
> (A + B + C). Die folgenden Unterschritte sind deshalb **eine
> ausführliche Referenz mit Screenshots-in-Prosa**, falls du nachlesen
> willst. Im Regelfall reicht es, dem Launcher-Output zu folgen.

Der Launcher arbeitet Menüpunkt [1] von oben nach unten ab und stoppt
nur dort, wo er etwas von dir braucht. Du musst zwischendrin **einmal
in den Browser wechseln und drei Klicks machen** - der Rest läuft
automatisch.

#### 6.1 - Docker-Check

Der Launcher prüft, ob Docker läuft. Falls nicht, bricht er ab mit dem
Hinweis "Docker fehlt/läuft nicht". Dann zurück zu Schritt 1.

#### 6.2 - OpenWebUI-Container installieren + starten

Der Launcher fragt: *"Soll ich OpenWebUI jetzt starten? (j/n) [j]:"*

Enter drücken (= Ja). Der Launcher zieht den Docker-Container
`ghcr.io/open-webui/open-webui:main` (beim ersten Mal ~1 GB, 1-2 Min
Download) und startet ihn auf Port 8080.

Danach siehst du: *"✓  OpenWebUI läuft"*.

#### 6.3 - OpenWebUI im Browser einrichten (der Handarbeits-Teil)

Der Launcher fragt nun nach deinem **OpenWebUI-API-Key** und öffnet
dabei automatisch <http://localhost:8080> im Browser.

> ⏸️ **Launcher wartet jetzt auf dich.** Lass das Terminal offen,
> wechsel in den Browser, erledige A + B + C unten, kopier zum Schluss
> den Key - komm dann zurück ins Terminal (Schritt 6.4). Der Launcher
> ist **nicht** abgestürzt, er wartet.

**A) Admin-Account anlegen** (nur beim allerersten Mal)

Im Browser: Benutzername, E-Mail, Passwort eintragen. Das ist ein
**rein lokaler** Account - er bleibt auf deinem Rechner, keine Daten
werden irgendwohin geschickt.

**B) OpenRouter-Key als Connection eintragen**

Nach dem Anlegen landest du auf der OpenWebUI-Startseite. Von dort:

1. Oben rechts auf das **Profil-Icon** klicken → **Einstellungen**.
2. Im Einstellungs-Menü links **Verbindungen** wählen.
3. Bei *OpenAI-API-Verbindungen* auf das **`+`-Icon** bzw. den Button
   **"Verbindung hinzufügen"** (englisch: "+ Add Connection"). Die UI
   ist auf Deutsch, wenn dein Browser auf Deutsch ist, sonst Englisch -
   das Feldlayout ist identisch.
4. Eintragen:
   - **Base URL / URL:** `https://openrouter.ai/api/v1`
   - **API-Key:** dein `sk-or-v1-...` aus Schritt 3
5. **Speichern** klicken.

**C) OpenWebUI-API-Key erzeugen**

Nochmal auf das Profil-Icon oben rechts → **Einstellungen → Account →
API Keys → "Create new key"** (oder **"Neuen Schlüssel erstellen"**)
→ Key kopieren.

> 💡 **Warum zwei verschiedene Keys?** Der OpenRouter-Key (Schritt 3)
> redet mit dem Sprachmodell in der Cloud. Der OpenWebUI-Key (hier)
> redet mit deinem lokalen OpenWebUI. Der Launcher nutzt Letzteren,
> um das Preset und die Knowledge Base automatisch anzulegen, statt
> dass du 19 Dateien von Hand hochladen müsstest.

#### 6.4 - Zurück ins Terminal

Der Launcher wartet immer noch auf deinen OpenWebUI-API-Key. Key
einfügen und Enter drücken:

- **Windows CMD / PowerShell:** Rechtsklick im Terminal-Fenster fügt
  den Zwischenablage-Inhalt ein.
- **macOS Terminal / iTerm:** **Cmd+V**.
- **Linux Terminal (gnome-terminal, Konsole ...):** **Ctrl+Shift+V**.

> ⚠️ **Eingabe ist unsichtbar** - du siehst nichts, während du einfügst.
> Das ist Absicht (wie bei Passwort-Eingaben). Einfach einfügen,
> Enter, fertig.

Der Launcher lädt jetzt die 19 Wissensmodule nach OpenWebUI hoch,
legt das Preset `ZEITRISS v4.2.6 Uncut` an und prüft am Ende per
Retrieval-Check, ob die KB funktioniert. Dauer: **5-10 Minuten beim
ersten Mal** (Embeddings werden berechnet).

#### 6.5 - LiteLLM-Cache aktivieren

Wenn der Launcher fertig ist, fragt er: *"LiteLLM-Cache aktivieren?
(gehört zum Golden Setup, spart ~90 % Prompt-Kosten)"*

**Ja drücken.** LiteLLM ist Teil des Golden Setups (Sonnet 4.6 + LiteLLM
+ OpenWebUI) — die Ja/Nein-Abfrage ist nur ein technischer Haken, falls
dein Setup gerade ohne Cache weiterlaufen muss (z.B. blockierter Port
4000). Im Normalfall: Enter drücken.

Der Launcher zieht dann den LiteLLM-Docker-Container,
startet ihn auf Port 4000 (nur lokal, nicht nach außen erreichbar) und
erzeugt einen Master-Key. Am Ende zeigt er dir im Terminal **drei
Browser-Schritte**, die du noch manuell machen musst (der Launcher kann
sie nicht automatisieren, weil OpenWebUI den Key selbst kennen muss) —
und schreibt den **Master-Key direkt in die `Key:`-Zeile von Schritt 1**,
du kopierst ihn also genau dort, wo du ihn gleich brauchst:

1. **Neue Connection in OpenWebUI eintragen.** Zurück in den Browser:
   **Profil-Icon → Einstellungen → Verbindungen → „+ Verbindung
   hinzufügen"**
   - **URL:** `http://localhost:4000/v1`
   - **API-Key:** der vom Launcher ausgegebene `sk-litellm-…`
   - **Name:** `LiteLLM (ZEITRISS Cache)`
   - **Speichern.**
2. **Preset auf LiteLLM umstellen.** Im linken Menü
   **Arbeitsbereich → Modelle** (englisch *Workspace → Models*)
   → Eintrag **`ZEITRISS v4.2.6 Uncut`** anklicken.
3. **Im Preset-Editor** das **Base-Modell-Dropdown** oben auf
   **`zeitriss-sonnet`** umstellen → **Speichern.**

> 💡 **Master-Key später nochmal gebraucht?** Der Launcher legt ihn
> zusätzlich in `scripts/litellm/.env` ab (chmod 600, nur für dich
> lesbar).

Fertig. Der Launcher hat deine Keys in einer versteckten Datei
gespeichert (`~/.openwebui_env` unter macOS/Linux,
`%USERPROFILE%\.openwebui_env` unter Windows) - **du musst sie nicht
anfassen**. Bei jedem weiteren Launcher-Start werden sie automatisch
geladen, du musst sie nie wieder eintippen.

---

### Schritt 7 - Spiel starten

Im Launcher-Menü **[3] Spiel starten** wählen. Der Browser öffnet sich
auf <http://localhost:8080>. Dort:

1. Neuen Chat öffnen.
2. Oben im Dropdown Preset **ZEITRISS v4.2.6 Uncut** auswählen.
3. Tippen: `Spiel starten (solo klassisch)`

Die KI-Spielleitung begrüßt dich mit einer Szene, ein HUD-Block
`EP 1 · MS 1 · SC ...` taucht auf. Ab hier erklärt dir die SL alles
weitere in-world.

**Varianten:**

- `Spiel starten (solo schnell)` - Fast-Lane für Kurzrunden (Charakter
  mit Defaults, direkt ins Briefing).
- `Spiel starten (gruppe klassisch)` - Gruppen-Chargen, alle nacheinander.
- `Spiel starten (gruppe schnell)` - Fast-Lane für Gruppen.
- Natürliche Sprache funktioniert auch ("Ich will neu starten als
  Gruppe" startet die Gruppen-Chargen).

> i️ **Funktioniert's?** Erwartete erste Antwort: Willkommensszene mit
> HUD-Block (`EP 1 · MS 1 · SC ...`) **oder** Fragen zur
> Charaktererschaffung ("Name?", "Vibe?" etc.). Beides ist in Ordnung
> - die SL startet je nach Preset-Variante direkt mit einer Szene oder
> mit der Charaktererstellung. Wenn stattdessen eine leere Antwort oder
> ein Fehler kommt: im Launcher **[6] Bei mir läuft was nicht** starten
> — das prüft alles durch und sagt auf Deutsch, was klemmt. Weitere Hilfe:
> [Troubleshooting](#troubleshooting).

---

## Updates und Wartung

### Der einfache Weg: Launcher-Menüpunkt [4]

```bash
python scripts/zeitriss.py
```

Dann **[4] ZEITRISS aktualisieren** wählen. Der Launcher macht
automatisch:

1. `git pull --ff-only` im Repo (bei lokalen Änderungen legt er sie
   kurz auf den Stash-Stack und stellt sie danach wieder her).
2. `~/.openwebui_env` laden (deine Keys).
3. Inkrementellen Sync starten - überträgt nur, was sich geändert hat.

Das ist der empfohlene Weg, weil du dir nichts merken musst.

### Für CLI-Fans: direkt via `setup.py --sync`

Intern ruft der Launcher das Script `setup.py` auf - du kannst es auch
direkt nutzen, brauchst du aber nicht. Der Launcher-Menüpunkt [4] macht
genau das Gleiche und kümmert sich zusätzlich um `git pull` und das
Laden deiner Keys. Direkt via CLI:

```bash
git pull
export $(grep -v '^#' ~/.openwebui_env | xargs)   # Keys aus ~/.openwebui_env laden
python scripts/setup.py --sync
```

> 💡 **Warum `export $(... | xargs)` und nicht `source ~/.openwebui_env`?**
> Die `~/.openwebui_env` enthält Zeilen wie `OPENWEBUI_API_KEY=sk-...` ohne
> `export`-Prefix. Bei `source` werden die Variablen zwar in der
> aktuellen Shell gesetzt, **aber nicht an Python als Kind-Prozess
> vererbt**. Der `export $(... | xargs)`-Einzeiler macht sie explizit
> exportierbar. Das Setup-Script gibt diesen Hinweis auch im Fehlerfall.
>
> Alternativ inline als eine Zeile:
>
> ```bash
> OPENWEBUI_URL=http://localhost:8080 OPENWEBUI_API_KEY=sk-... python scripts/setup.py --sync
> ```

### Was `--sync` intern tut

Der `--sync`-Modus vergleicht die lokalen Dateien mit einem Manifest
(`.openwebui-sync.json`, automatisch angelegt) und überträgt **nur,
was sich geändert hat**:

- Masterprompt geändert → Preset wird gepatcht (<1 s).
- Einzelne Wissensmodule geändert → nur die neu hochladen und neu
  indexieren.
- Nichts geändert → "Alles synchron, nichts zu tun."

Das spart bei typischen Regel-Patches **Minuten bis zu einer halben
Stunde** gegenüber dem Full-Rebuild. Eure KB-IDs bleiben stabil, offene
Browser-Chats überleben.

### Dauer-Erwartung

| Fall | Dauer |
| --- | --- |
| `--sync`, nichts geändert | <1 Sekunde |
| `--sync`, nur Masterprompt | 1-2 Sekunden |
| `--sync`, 1-5 KB-Dateien geändert | 20 s bis 8 min |
| Full-Rebuild / Erstinstallation | 5 min bis 25 min |

Die Spannweite kommt von der **Embedding-Engine**: OpenWebUI-Default
(MiniLM) rechnet in Sekunden, Ollama-CPU braucht pro 80-kB-Datei
60-120 Sekunden. Bei sehr langsamer Hardware das Timeout hochsetzen -
siehe [Troubleshooting](#sync-meldet-timeout-bei-der-datei-verknüpfung).

### Wann Full-Rebuild statt `--sync`?

```bash
python scripts/setup.py
```

Richtig in folgenden Fällen:

- **Erstinstallation** - `--sync` verlangt ein existierendes Preset.
- **Nach OpenWebUI-Major-Upgrade** - Knowledge-Schema kann sich ändern.
- **ZIP-Download-User** - ohne Git geht `--sync` nicht (Manifest wäre
  bei jedem frischen ZIP-Entpacken wieder weg).
- **Zerschossener Zustand** - wenn `--sync` mehrfach fehlschlägt und
  der Fehler unklar bleibt.

Der Full-Rebuild schreibt am Ende automatisch das Manifest, sodass ein
anschließender `--sync`-Lauf sofort "synchron" meldet.

### Manuelle Tweaks im Preset bleiben erhalten

`--sync` patcht nur den System-Prompt (Masterprompt). Wenn ihr in
OpenWebUI manuell Temperature, Top-P oder Frequency geändert habt,
bleiben diese Werte unberührt.

### Multi-Install

Pro lokalem Repo-Clone wird genau ein Manifest geführt. Wer gegen
mehrere OpenWebUI-Instanzen syncen will (zwei Rechner, zwei Server),
braucht getrennte Clones.

---

## Weiterführendes: Gruppenspiel, Ollama, portabler Export

Dieser Abschnitt sammelt ergänzende Szenarien: Gruppenspiel am selben
Rechner, Ollama als Alternativ-Modell oder als lokalen Embedder, und
den portablen Export in andere Chat-Plattformen.

### Lokales Gruppenspiel am selben Rechner

ZEITRISS ist primär für **Gruppen an einem Gerät** gedacht: alle sitzen
zusammen um einen Laptop, ein Spieler moderiert, gespielt wird im
Wechsel - wie am Pen-&-Paper-Tisch, nur mit KI-SL statt Human-SL.

> Remote-Play über Netzwerk (Tailscale, VPN, Multi-User-OpenWebUI) ist
> möglich, braucht aber eigenes Setup. Ein dedizierter Remote-Guide
> folgt später.

**Setup für die Gruppe**: Nur eine Person hostet (folgt dem Happy Path).
Die anderen installieren **nichts** - sie sitzen einfach mit am Rechner.

**Gruppenstart**:

```
Spiel starten (gruppe klassisch)
```

Die SL führt durch Gruppen-Chargen: Jeder Spieler gibt Vibe, Attribute
und Loadout nacheinander durch. Danach HQ, Save, Mission. Alternativ
`Spiel starten (gruppe schnell)` als Fast-Lane - SL generiert Charaktere
mit Defaults und springt direkt ins Briefing.

**Mitgebrachte Saves laden** (aus Solo- oder früheren Gruppen-Abenden):

```
Spiel laden
```

Danach alle Saves hintereinander in den Chat pasten - ein Save sieht
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

- **Ein Tipper pro Szene** - einer sitzt an der Tastatur, die anderen
  sagen vor, Tipper rotiert nach jeder Mission.
- **Ansage in eckigen Klammern** (empfohlen, nicht Pflicht):
  "[Kira] Ich ziele auf den Wachposten" ist eindeutiger als anonymes
  "Ich schieße". Natürliche Sprache ("Kira zielt...") funktioniert
  genauso - die eckigen Klammern sind nur eine Abkürzung.
- **Würfel macht die SL** - das ist Teil des Spiels. Die Gruppe
  entscheidet die Aktion, die SL berichtet das Ergebnis mit Formel.

**Pausen**: Der Chat läuft nicht weiter, solange niemand tippt. Klo-Pause
ist problemlos.

**Ende des Abends**: `!save` im HQ, die SL gibt den Gruppen-JSON zurück.
Text in eine Datei kopieren und an alle verteilen. Beim nächsten Abend
einfach `Spiel laden` und einfügen.

**Split für Solo-Weiterspielen**: Nach Debrief im HQ bietet die SL
Split-Pfade an. Einfach sagen: "Ich möchte mit Kira solo weiterspielen."
Die SL gibt einen Solo-Save aus - nur diese Figur + Kampagnen-Anker.
Solo-Erlebnisse fließen beim nächsten Gruppenabend wieder ein.

> 💡 **Save früh, save oft**: Macht nach jeder Mission einen gemeinsamen
> Save. Save = Charakter; nicht gesichert = im nächsten Browser-Crash
> weg.

### Lokal-GPU-Variante (Ollama, ungetestet)

> ⚠️ **Nicht kalibriert, DIY-Terrain.** Wir testen und optimieren
> ausschließlich auf OpenWebUI + Sonnet 4.6 + LiteLLM. Die Lokal-GPU-
> Variante ist technisch unterstützt, aber nicht Teil unserer Regel-QA.
> Regel-Abweichungen auf dieser Variante lassen sich von außen kaum
> zuordnen (Modell, GPU-Auslastung oder Prompt?), deshalb können wir da
> nicht gezielt gegensteuern.

Diese Variante bleibt innerhalb von **Weg A** (OpenWebUI + Launcher).
Es ist keine separate Installation — du richtest den Standard-Stack
einmal via Launcher ein und schaltest im OpenWebUI-Preset-Dropdown
zwischen `zeitriss-sonnet` (Cloud) und deinem Ollama-Modell hin und her.

**Realistische Hardware:** ZEITRISS ist regel-komplex; Modelle unter der
70B-Klasse kommen schnell an Grenzen. Consumer-GPUs reichen typischerweise
nicht. Eine Workstation-Klasse (z.B. Framework-Ryzen-Max-128GB oder
vergleichbar) kann das stemmen, sobald fähige Modelle kompakt genug
werden. Bis dahin ist der Cloud-Pfad (Sonnet 4.6 via LiteLLM) der einzige
getestete Weg — und der Punkt, zu dem man per Dropdown-Flip jederzeit
zurückkehrt.

#### Ollama als Sprachmodell

**Rolle**: Ollama ersetzt das Cloud-Modell. Ihr spielt komplett
offline/lokal, keine Daten verlassen euren Rechner.

**Einrichtung**: Ollama wie gewohnt laufen lassen, ein fähiges Modell
laden (70B-Klasse oder größer, genug VRAM). In OpenWebUI unter
**Einstellungen → Verbindungen** die Ollama-Verbindung eintragen (meist
`http://host.docker.internal:11434`). Im ZEITRISS-Preset das Base-Modell-
Dropdown auf dein Ollama-Modell umstellen.

**LiteLLM bleibt drin.** Der Anthropic-Prompt-Cache greift zwar nur auf
der Cloud-Route, schadet aber nicht — LiteLLM funktioniert als
Multi-Provider-Proxy weiter, und der Vorteil ist: Du kannst per
Dropdown-Flip sofort zurück auf `zeitriss-sonnet` wechseln, wenn dir
dein lokales Modell bei der nächsten Szene nicht mehr reicht. Keine
Re-Installation, kein Container-Neustart.

#### Ollama als Embedding-Engine

**Rolle**: Ollama ersetzt hier **MiniLM** (den Default-Embedder). Nur
beim **Aufbau der Knowledge Base** und bei `--sync` aktiv - nicht beim
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
> laufen oder keins - OpenWebUI braucht nur den Default-MiniLM.

### Portabler Export (ohne Gewähr)

Du willst ZEITRISS auf einer anderen Chat-Plattform nutzen? Der
Launcher erzeugt dir ein **Wissenspaket** (Masterprompt + 19
Wissensmodule), das du in jede Plattform hochladen kannst, die einen
langen System-Prompt und den Upload von Wissensdateien unterstützt.

> ⚠️ **Wir testen nur gegen OpenWebUI.** Auf anderen Plattformen kann
> ZEITRISS funktionieren, aber Regel-Glitches sind möglich — z. B.
> erzwingt das Regelwerk das HUD-Format, was bei schwächerer Retrieval-
> Qualität auseinanderfällt. Do-it-yourself-Terrain.

#### Der einfache Weg: Launcher-Menüpunkt [2]

```bash
python scripts/zeitriss.py
```

Im Menü **[2] Regelwerk woanders nutzen (Export-Paket erzeugen)**
wählen. Der Launcher fragt dich:

1. **Format** — [1] strukturiert (Ordner mit Unterordnern), [2] flach
   (nummerierte Dateien in einem Ordner, für Plattformen ohne
   Ordner-Support), [3] beides.
2. **Ausgabe-Ordner** — default `./.exports/`, Enter = übernehmen.
3. **Im Dateimanager öffnen?** — macht er gern.

Im Terminal siehst du am Ende konkrete Import-Hinweise (Masterprompt
kommt als Systemprompt, Wissensmodule als „Wissen"/„Knowledge"). Das
erzeugte Paket enthält zusätzlich eine `SETUP-ANLEITUNG.md` mit
Plattform-spezifischen Tipps.

#### Was die Zielplattform können muss

- **Langer System-Prompt / Projekt-Anweisung** (mind. ~60 KB) — für
  den Masterprompt.
- **Upload von mehreren Wissens-/Projekt-Dateien** — für die 19
  Wissensmodule.
- **Retrieval über die hochgeladenen Dateien** — ohne das halluziniert
  das Modell die Regeln, statt sie nachzuschlagen.
- Idealerweise ein **Claude-Sonnet-4.6-Klasse-Modell** oder besser;
  mit schwächeren Modellen bricht die Regeltreue.

Plattformen ohne eines dieser vier Features sind für ZEITRISS
ungeeignet — wir können dir dabei nicht helfen.

#### Für CLI-Fans: direkt via `setup.py --export`

```bash
python scripts/setup.py --export           # strukturiert
python scripts/setup.py --export --flat    # flache Nummerierung
python scripts/setup.py --export --out DIR # eigener Ausgabe-Ordner
```

Macht intern genau das, was der Launcher-Menüpunkt [2] macht.

### Manuelles Setup ohne Script

Wenn ihr das Script nicht nutzen wollt:

**1. Knowledge Base** in OpenWebUI anlegen (Name: `ZEITRISS 4.2.6 Regelwerk`).
19 Wissensmodule aus dem Repo hochladen (welche das sind, bestimmt
`master-index.json` mit `"slot": true`):

| Kategorie | Dateien |
| --- | --- |
| **core** | `spieler-handbuch.md`, `zeitriss-core.md`, `wuerfelmechanik.md`, `sl-referenz.md` |
| **characters** | `charaktererschaffung-grundlagen.md`, `ausruestung-cyberware.md`, `zustaende.md`, `hud-system.md` |
| **gameplay** | `kampagnenstruktur.md`, `kampagnenübersicht.md`, `kreative-generatoren-missionen.md`, `kreative-generatoren-begegnungen.md`, `fahrzeuge-konflikte.md`, `massenkonflikte.md` |
| **systems** | `kp-kraefte-psi.md`, `cu-waehrungssystem.md`, `speicher-fortsetzung.md`, `cinematic-start.md`, `toolkit-gpt-spielleiter.md` |

**Nicht hochladen**: `README.md`, `master-index.json`, Archiv-Dateien.

**Optional, nicht im Default-Slotset**: `characters/charaktererschaffung-optionen.md`
(Inspirations-/Fallback-Charaktere, Archetypen-Fundus für One-Shots). Das
Modul ist bewusst nicht im Default-Ladepfad - die SL bevorzugt `generate`
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

> **Spielrhythmus.** ZEITRISS spielt sich in eigenständigen Abschnitten
> (Charaktererschaffung, HQ-Runde, Mission, Chronopolis, Arena), je
> Abschnitt ein eigener Chat mit `!save` am Ende und neuem Chat plus Save-Load
> am Anfang. Hintergrund und Begründung im Spielerhandbuch:
> [Der Gameflow: Chat-Wechsel als Spielrhythmus](../core/spieler-handbuch.md#gameflow-chat-wechsel).

---

## Troubleshooting

### "Die SL antwortet, aber Regeln klingen falsch"

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

### "Das Script meldet Fehler beim Verknüpfen der Dateien"

Der Verknüpfungs-Endpunkt von OpenWebUI meldet manchmal spurious
HTTP-Fehler. Entscheidend ist der **Retrieval-Check** am Ende: Solange
dort `KB-Retrieval funktioniert` steht, sind alle Dateien korrekt
eingebunden.

### "Ich habe einen komplett zerschossenen Zustand"

```bash
python scripts/setup.py --reset-embeddings --embedding default
```

`--reset-embeddings` räumt verwaiste Vektor-Ordner auf, bevor die neue
KB gebaut wird.

### "Setup hängt bei der URL-Abfrage"

Umgebungsvariablen setzen, dann fragt das Script nichts:

```bash
export OPENWEBUI_URL=http://localhost:8080
export OPENWEBUI_API_KEY=sk-...
python scripts/setup.py -y
```

### "`--sync` meldet 'Preset existiert nicht'"

`--sync` ist ein Update-Modus, keine Erstinstallation. Einmal Full-Rebuild
laufen lassen:

```bash
python scripts/setup.py
```

### "`--sync` dauert so lang wie der Full-Rebuild"

Zwei häufige Ursachen:

1. **Kein Manifest vorhanden** (`.openwebui-sync.json` fehlt, z. B.
   nach `git clean` oder frischem ZIP-Entpacken). Lösung: einmal
   Full-Rebuild, danach sind künftige `--sync` wieder schnell.
2. **Viele Dateien zugleich geändert** - dann zieht `--sync` sie alle
   durch, das ist normal. Der Progress-Counter zeigt, wie viele.

### "`--sync` meldet Timeout bei der Datei-Verknüpfung"

OpenWebUI rechnet die Embeddings synchron. Ollama-CPU braucht pro
Datei 1-2 Minuten, Default-Timeout ist 6 Minuten. Auf sehr langsamer
Hardware hochsetzen:

```bash
export OWUI_ADD_FILE_TIMEOUT=900
python scripts/setup.py --sync
```

Wenn das Script bei einer Datei trotzdem aufgibt: Fortschritt bleibt
im Manifest stehen, der nächste `--sync` macht dort weiter.

### "LiteLLM-Cache greift nicht"

Drei häufige Ursachen:

1. **OpenRouter-Privacy-Settings** blockieren Anthropic/Bedrock. Unter
   <https://openrouter.ai/settings/privacy> prüfen.
2. **OpenRouter-Guthaben leer** - dann schlägt jede Anfrage mit 402
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
| `python scripts/setup.py --export` | Export-Paket für alternative Plattformen (ohne Gewähr) |
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
nächsten Lauf - solange OpenWebUI die Dateiliste korrekt ausgibt.
Im Zweifel hilft immer der Full-Rebuild.

### Modelle

**Getestet und empfohlen:** `anthropic/claude-sonnet-4.6` — als einziges
Modell mit vollständiger Regeltreue (korrekte Mechanik, HUD, Px).
Preisrahmen: ~$3/$15 pro 1M Token, mit LiteLLM-Cache auf den Prompt-Anteil
~90 % Ersparnis pro Folge-Turn.

Alle anderen Modelle sind **nicht kalibriert und ohne Gewähr.**
Historischer Vergleich (GLM-Familie, DeepSeek) aus dem Playtest vom
2026-03-17 liegt im Archiv
([AUSWERTUNG](../internal/qa/evidence/playtest-2026-03-17/AUSWERTUNG.md)),
wird aber nicht mehr gepflegt. Budget-Modelle können atmosphärisch
erzählen, erfinden aber eigene Würfelsysteme, wenn man sie lässt.

### Modell-Parameter-Profile

`setup.json` transportiert die Preset-Parameter (`temperature`, `top_p`,
`frequency_penalty`, `max_tokens`). Die gelieferten Werte sind auf
**Sonnet 4.6 via LiteLLM/OpenWebUI** kalibriert - also auf den Referenz-Stack,
auf dem das Regelwerk getestet wurde. Wer den getesteten Weg fährt, muss
hier **nichts** anpassen.

Die folgenden Profile sind Starthilfen für **nicht-kalibrierte Stacks**,
wenn jemand das Preset in einer anderen Plattform oder mit einem anderen
Modell betreibt. Anpassung über OpenWebUI → Preset → _Advanced Params_
(Script nicht erneut laufen lassen). Ohne Gewähr, kein Hilfeversprechen:

| Profil | Wofür | `frequency_penalty` | `max_tokens` | Begründung |
| --- | --- | --- | --- | --- |
| **sonnet_46_dev (Default, getestet)** | Sonnet 4.6 + LiteLLM | `0.3` | `64000` | Ausbalanciert, Ausgaben atmosphärisch, lange Szenen möglich |
| **portable_default** (ungetestet) | andere Provider / striktere Output-Limits | `0.1` | `8000`-`16000` | Regel-Terminologie stabiler, kleine Output-Caps |
| **rules_strict** (ungetestet) | Regel-Tests, Gates | `0.0` | `8000` | Maximale Terminologiekonsistenz, kein Drift bei wiederholten Begriffen |

**Faustregel:** `frequency_penalty` > 0.3 lass - zerstreut Regelterme
(`SaveGuard`, `SG`, `PP`, `Px`). `max_tokens` > 32000 nur auf Stacks, die das
echte Output-Budget wirklich liefern; OpenRouter/LiteLLM reichen praktisch
~16k effektiv durch.

### Sicherheit

- **API-Keys getrennt halten**, keine geteilten Admin-Tokens für
  Spielgruppen.
- **Auth vor Netzfreigabe**: OpenWebUI nie ohne Login ins Internet
  hängen.
- **Remote-Provider** verarbeiten Eingaben - keine sensiblen Daten in
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
