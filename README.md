# ZEITRISS®-md Zeitreise-RPG

<p align="center">
  <img src="docs/gameicon.png" alt="ZEITRISS" width="200">
</p>

[![LLM-Ready ✅][llm-ready-badge]][llm-ready-link]

> **Tech-Noir-Zeitreise-RPG mit KI-Spielleitung.** Ihr spielt Chrononauten
> des ITI — Elite-Agenten, die durch die Zeit springen, um die Hauptzeitlinie
> zu stabilisieren. Explodierende Würfel, HUD-Overlay, persistente Saves.
> **18+, Uncut.**

## Was ist ZEITRISS?

Ein Pen-&-Paper-RPG, bei dem die **KI eure Spielleitung ist**. Kein
vorgefertigtes Text-Adventure, kein Choose-Your-Own-Adventure — ein
vollständiges Rollenspielsystem mit Würfelproben, Charakterentwicklung,
Kampagnenfortschritt und einer KI, die alles leitet: Szenen, NSCs, Kämpfe,
Loot und Debrief.

Die Spielleitung zieht aus einem ganzen Orchester von Generatoren —
Settings, NSC-Pools, Preserve-/Trigger-Seeds, Paradox-Events und
Rift-Koordinaten — und webt daraus jede Kampagne neu. Kein Playthrough
gleicht dem anderen.

Ihr müsst vor dem ersten Run nicht das Regelwerk lesen — einrichten,
Preset wählen, losspielen. **Regeln, Welt, Skillung, Taktik** lernt ihr
**spielerisch im Chat** — fragt einfach die Spielleitung („wie levele ich
am besten?", „was macht TEMP?", „was ist ein Rift-Op?"), sie antwortet
in-world, ohne die vierte Wand zu brechen. Kein Computerspiel und kein
klassisches Pen-&-Paper erklärt euch die Welt so beiläufig wie ZEITRISS:
**nichts bleibt ungeklärt**, weil ihr jederzeit fragen könnt.

### So sieht das aus

🎬 `EP 01 · MS 03 · SC 07/12 · MODE CORE · Objective: Dossier sichern`\
🧠 `Stress 3 · Px █░░░░ (1/5) · Lvl 3 ▓▓▓░░░░░░░ · Rank Operator · SYS 1/4 (free 3)`

> Der Wachmann dreht sich um. Seine Hand geht zum
> Holster. Du bist schneller.

`Probe: Nahkampf → W6: [5] + STR 4/2 + Talent 1 = 8 vs SG 8 → TREFFER`

> Dein Ellbogen trifft seinen Kehlkopf. Er klappt
> zusammen, lautlos.

`Kodex: Wachmann neutralisiert. Stress +1.`

### Ähnlich, aber anders

|              | KI-Chat-RPGs     | Pen & Paper    | **ZEITRISS**         |
| ------------ | ---------------- | -------------- | -------------------- |
| Spielleitung | KI, keine Regeln | Mensch         | KI, regelgebunden    |
| Würfel       | Keine            | Ja             | W6/W10, Exploding    |
| Persistenz   | Nur im Chat      | Manuell        | JSON-Save, portabel  |
| Multiplayer  | Begrenzt         | Am Tisch       | Drop-in/out per Save |
| Regelwerk    | Keins            | Buch (100+ S.) | Im Wissensspeicher   |

## Dein Save IST dein Charakter

**Save = Charakter.** Euer Fortschritt hängt nicht an einem Server. Der
Charakter liegt als JSON-Speicherstand vor — wie ein Datenblatt beim
klassischen Pen & Paper.

- **Mitnehmbar:** Denselben Charakter in jedem neuen Chat laden.
- **Teilbar:** Gruppen splitten, spielen getrennt weiter, mergen danach.
- **Dein Besitz:** Kein Account, kein Lock-in. **MMO ohne Server.**

**Multiplayer funktioniert so:** Eine Person hostet den Chat. Im HQ speichert
ihr mit `!save` — der JSON enthält alle Charaktere. Jeder kann seinen Stand
mitnehmen, solo weiterspielen und beim nächsten Gruppenabend wieder einsteigen.
Der erste gepostete Save setzt den Kampagnenrahmen, jeder weitere Charakter
bringt seinen persönlichen Fortschritt mit.
Wenn sich Gruppen trennen und später wieder zusammentreffen, verweben sich die
einzelnen Handlungsstränge wieder zu einem gemeinsamen Zeitnetz.

**Hinweis zu Saves:** Ausformulierte Vorgeschichten dürfen ausführlich sein,
der Save bleibt trotzdem kompakt. Beim HQ-`!save` können ältere
Freitext-Details in `summaries.*` verdichtet werden; der spielrelevante Kern
bleibt im strukturierten Charakterstand erhalten.

## Bestehendes Charaktermaterial mitbringen

Du hast bereits eine Figur aus einem anderen Pen-&-Paper oder eine ältere
Kampagnen-Biografie? Dann kannst du vorhandene Notizen, Bögen oder eine
Kurzbiografie als Ausgangsmaterial nutzen.

ZEITRISS übernimmt dabei **keine fremden Regeln 1:1**. Übernommen werden vor
allem **Rolle, Vibe, Hintergrund, Motive, Stärken, Schwächen und
Ausrüstungsrichtung**. Alles andere wird in einen ZEITRISS-kompatiblen
Startcharakter übersetzt.

Wenn deine Runtime Bildinput unterstützt, kannst du auch einen Scan oder ein
Foto als Referenz nutzen. Der robusteste Weg bleibt trotzdem eine kurze
Textzusammenfassung der wichtigsten Eckdaten.

## Zwei Setup-Wege (klar getrennt)

ZEITRISS ist ein Datensatz (Masterprompt + 19 Wissensmodule), kein
separates Programm. Für die Nutzung gibt es **zwei klar getrennte Wege**:

### Weg A — Standard-Setup (empfohlen, getestet, Referenz-Basis)

- **Plattform:** OpenWebUI
- **Modellpfad:** OpenRouter, empfohlen `anthropic/claude-sonnet-4.6`
- **Standard:** LiteLLM für Prompt-Cache (Kostenersparnis)
- **Status:** Aktiv getestet und als Referenz-Setup genutzt

**Nur für diesen Weg** sind reproduzierbares Feedback und saubere
Fehlersuche realistisch möglich.

### Weg B — Portabler Setup (manuell, ohne Gewähr)

- Export/Import von Masterprompt + Wissensmodulen in andere Plattformen
- Sinnvoll für fortgeschrittene Nutzer mit eigener Runtime-Erfahrung
- **Status:** Technisch möglich, aber nicht Teil der offiziellen Testbasis

Wichtig: Weg B ist **kein Ersatz** für den Standardpfad, sondern eine
Best-Effort-Option für eigene Experimente.

### Hinweise zur Plattformwahl

- **Lumo (Plattform von Proton):** Aktuell keine zuverlässige ZEITRISS-Erfahrung
- **Ungetestete Plattformen (z. B. Claude Code):** Noch nicht freigegeben
- **Kleine lokale Modelle:** Für ZEITRISS in der Regel zu schwach

**Kurzfassung:** Wenn ihr spielen und sinnvolles Feedback geben wollt, nutzt
Weg A.

---

## Setup in 3 Schritten

### Was du einmalig brauchst

- **Docker** (Download: <https://docs.docker.com/get-docker/>)
- **Python 3** (<https://python.org> — auf Windows beim Installer
  „Add Python to PATH" anklicken)
- **OpenRouter-Account** mit ~5 USD Guthaben (<https://openrouter.ai>),
  dazu unter <https://openrouter.ai/settings/privacy> den Provider
  **Anthropic** auf *Allowed* setzen, und unter
  <https://openrouter.ai/keys> einen Key `sk-or-v1-…` erzeugen.

### Schritt 1 — Hol dir ZEITRISS

```bash
git clone https://github.com/pchospital-lab/ZEITRISS-md.git
cd ZEITRISS-md
```

(Kein Git? Auf GitHub **Code → Download ZIP**, entpacken, Terminal im
Ordner öffnen.)

### Schritt 2 — Starte den Launcher

```bash
python scripts/zeitriss.py
```

Unter Windows auch Doppelklick auf `zeitriss.bat`, unter macOS/Linux
`./zeitriss.sh`.

### Schritt 3 — Folge dem Launcher

Im Menü **[1] Komplett-Setup in OpenWebUI** wählen. Der Launcher
übernimmt von hier: OpenWebUI-Container starten, drei Browser-Klicks
erklären (Admin-Account, OpenRouter-Connection, API-Key), das Regelwerk
hochladen, optional den LiteLLM-Cache einrichten. Er sagt dir im
Terminal an jeder Stelle selbst, was als nächstes zu tun ist.

Wenn er fertig ist: **[3] Spiel starten** wählen, im Browser neuen Chat
öffnen, Preset **ZEITRISS v4.2.6 Uncut** auswählen, tippen:

```
Spiel starten (solo klassisch)
```

> ⏱️ **Zeitbudget beim ersten Mal:** 30–60 Minuten inkl. Docker- und
> Python-Installation. Updates später (Launcher-Menü [4]): 1–2 Minuten.

---

### Du willst ZEITRISS woanders spielen (Lumo, Claude Projects, …)?

Im Launcher-Menü **[2] Regelwerk woanders nutzen** wählen — er erzeugt
dir ein Export-Paket mit Masterprompt und allen Wissensmodulen, das du
manuell in deine Ziel-Plattform hochladen kannst.

⚠️ Das ist ein **Best-Effort-Weg ohne Gewähr**. Nur Weg A (OpenWebUI)
ist offiziell getestet. Details und Plattform-Hinweise im
[Setup-Guide](docs/setup-guide.md#portabler-export-ohne-gewähr).

### Wenn etwas klemmt

Im Launcher-Menü **[6] Bei mir läuft was nicht** wählen — er prüft
Docker, OpenWebUI, API-Keys und KB-Retrieval durch und sagt dir auf
Deutsch, wo der Fehler sitzt. Tiefer:
[Troubleshooting](docs/setup-guide.md#troubleshooting).

## Modell-Empfehlung

**Standard-Stack: `anthropic/claude-sonnet-4.6` + LiteLLM.** Sonnet 4.6 ist
aktuell das einzige getestete Modell mit vollständiger Regeltreue und
stärkstem Noir-Ton. Der LiteLLM-Proxy (Docker, Teil des Standard-Setups) aktiviert
den Anthropic-Prompt-Cache und senkt die Kosten um **~90 %** — ZEITRISS
wird damit **spürbar günstiger** ohne Abstrich bei der Regeltreue.

> In OpenWebUI taucht das Modell nach der LiteLLM-Installation als
> `zeitriss-sonnet` im Dropdown auf. Das ist nur ein LiteLLM-Alias für
> `anthropic/claude-sonnet-4.6` — gleiches Modell, kürzerer Name.
> ZEITRISS wird automatisch auf diesen Alias eingestellt.

## Das Spielsystem in Kürze

1. **Agenten.** Als Chrononauten deckt ihr Zeitverschwörungen auf — Schicht
   für Schicht, nicht per Briefing-Dump. Jede Episode baut sich auf wie eine
   Staffel: erst der kleine Auftrag vor großer Kulisse, dann die Verdichtung,
   dann das Finale.
2. **Missionsphasen.** Briefing → Infiltration → Konflikt → Exfil → Debrief.
   12 Szenen pro Core-Mission, 14 bei Rift-Ops.
3. **Preserve & Trigger.** Ihr stabilisiert historische Verläufe (**Preserve**)
   oder sorgt aktiv dafür, dass dokumentierte Ereignisse eintreten
   (**Trigger**), wenn genau das den größeren Schaden verhindert. Chrononauten
   agieren dabei als Werkzeug eines größeren Plans des ITI.
4. **Explodierende Würfel.** W6, ab Attribut 11 W10, ab 14 Heldenwürfel.
5. **Paradoxon-Index.** Belohnungssystem: Der Anstieg von Px hängt vom
   Missionsverlauf und euren Preserve/Trigger-Entscheidungen ab. Bei Px 5 werden 1–2
   Riftkoordinaten auf der Raumzeitkarte sichtbar — dort warten Rift-Ops
   mit Paramonstern und Artefakten.
6. **Boss-Rhythmus.** Mission 5 = Mini-Boss, Mission 10 = Episoden-Boss.
7. **Persistenz.** `!save` im HQ, JSON mitnehmen, im nächsten Chat laden.

**Makros sind Komfort, keine Pflicht:** `!save`, `!bogen` oder `!menü` sind
Shortcuts. Ihr könnt genauso natürlich schreiben wie „speichere meinen
Charakter“ oder „zeig meinen Bogen“ — die Spielleitung reagiert in-world.

→ **[Spieler-Handbuch](core/spieler-handbuch.md)** — Einleitung, Regeln,
Schnellstart, FAQ
→ **[SL-Referenz](core/sl-referenz.md)** — Tabellen, Befehle, Systemdetails

## Lizenz

- **Inhalte** (Texte, Illustrationen, Regeln) — CC BY-NC 4.0 mit
  Attribution "ZEITRISS® — pchospital". Private Nutzung kostenlos.
- **Code** (Scripts, Tools, Runtime) — MIT.
- **Kommerzielle Nutzung:** Schriftliche Vereinbarung nötig
  (siehe [LICENSE](LICENSE)).
- **Streams/Videos:** Erlaubt mit Attribution
  (siehe [Creator-Lizenz](docs/creator-license.md)).
- **18+.** ZEITRISS® ist eine eingetragene Wortmarke (DPMA).

## Feedback

Pull Requests werden nicht angenommen. Bei Regelfehler, Ideen oder
Tippfehler bitte ein
[Issue](https://github.com/pchospital-lab/ZEITRISS-md/issues) erstellen.
Sicherheitsmeldungen: [SECURITY.md](SECURITY.md).

---

© 2025-2026 pchospital – ZEITRISS® – private use only. See LICENSE.

[llm-ready-badge]: https://img.shields.io/badge/LLM--Ready-%E2%9C%85-success
[llm-ready-link]: core/spieler-handbuch.md
