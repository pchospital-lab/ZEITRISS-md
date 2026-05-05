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

Ihr müsst vor dem ersten Run nicht das Regelwerk lesen — einrichten,
Preset wählen, losspielen. **Regeln, Welt, Skillung, Taktik** lernt ihr
**spielerisch im Chat** — fragt einfach die Spielleitung („wie levele ich
am besten?", „was macht TEMP?", „was ist ein Rift-Op?"), sie antwortet
in-world, ohne die vierte Wand zu brechen. Kein Computerspiel und kein
klassisches Pen-&-Paper erklärt euch die Welt so beiläufig wie ZEITRISS:
**nichts bleibt ungeklärt**, weil ihr jederzeit fragen könnt.

### So sieht das aus

🎬 `EP 01 · MS 03 · SC 07/12 · MODE CORE · Objective: Dossier sichern`\
📊 `Stress 3 · Px █░░░░ (1/5) · Lvl 3 ▓▓▓░░░░░░░ · Rank Operator · SYS 1/4 (free 3)`

> Der Wachmann dreht sich um. Seine Hand geht zum
> Holster. Du bist schneller.

`Probe: Nahkampf → W6: [6]`\
`→ Exploding! → W6: [2] = 8`\
`+ STR 4/2 + Talent 1 = 11`\
`vs SG 8 → TREFFER`

> Dein Ellbogen trifft seinen Kehlkopf. Er klappt
> zusammen, lautlos.

`Kodex: Wachmann neutralisiert.`\
`Noise +1 · Mag 8/8 · Checkpoint 40m`

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

## Setup starten

### Weg A — Standard-Setup (OpenWebUI)

```bash
git clone https://github.com/pchospital-lab/ZEITRISS-md.git
cd ZEITRISS-md
python scripts/setup.py
```

Danach in OpenWebUI: neuen Chat öffnen, Preset
**ZEITRISS v4.2.6 Uncut** wählen, `Spiel starten (solo klassisch)` tippen.
Natürliche Sprache funktioniert ebenfalls, z. B. „Wir wollen neu als Gruppe starten“.

### Weg B — Portabler Setup (manuell)

- Masterprompt + Wissensmodule manuell in die Zielplattform eintragen
- JSON für Save/Load nutzen
- Keine Funktionsgarantie, kein offizieller Betriebs-/Hilfepfad

Details für beide Wege stehen im [Setup-Guide](docs/setup-guide.md).

---

**Alles weitere im [Setup-Guide](docs/setup-guide.md):**

- [Weg A: Happy Path (offiziell)](docs/setup-guide.md#weg-a--standard-setup-offiziell-getestet)
- [Weg B: Portabler Setup](docs/setup-guide.md#weg-b--portabler-setup-ohne-gewähr)
- [Updates mit `--sync`](docs/setup-guide.md#updates-und-wartung)
- [Troubleshooting](docs/setup-guide.md#troubleshooting)

## Modell-Empfehlung

**Standard-Stack: `anthropic/claude-sonnet-4.6` + LiteLLM.** Sonnet 4.6 ist
aktuell das einzige getestete Modell mit vollständiger Regeltreue und
stärkstem Noir-Ton. Der LiteLLM-Proxy (Docker, Teil des Standard-Setups) aktiviert
den Anthropic-Prompt-Cache und senkt die Kosten um **~90 %** — ZEITRISS
wird damit **spürbar günstiger** ohne Abstrich bei der Regeltreue.

## Das Spielsystem in Kürze

1. **Agenten.** Als Chrononauten deckt ihr Zeitverschwörungen auf — Schicht
   für Schicht, nicht per Briefing-Dump. Jede Episode baut sich auf wie eine
   Staffel: erst der kleine Auftrag vor großer Kulisse, dann die Verdichtung,
   dann das Finale.
2. **Missionsphasen.** Briefing → Infiltration → Konflikt → Exfil → Debrief.
   12 Szenen pro Core-Mission, 14 bei Rift-Ops.
3. **Explodierende Würfel.** W6, ab Attribut 11 W10, ab 14 Heldenwürfel.
4. **Paradoxon-Index.** Belohnungssystem: Bei Px 5 werden 1–2
   Riftkoordinaten auf der Raumzeitkarte sichtbar — dort warten Rift-Ops
   mit Paramonstern und Artefakten.
5. **Boss-Rhythmus.** Mission 5 = Mini-Boss, Mission 10 = Episoden-Boss.
6. **Persistenz.** `!save` im HQ, JSON mitnehmen, im nächsten Chat laden.

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
