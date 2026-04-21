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
Preset wählen, losspielen.

### So sieht das aus

```text
EP 1 · MS 3 · SC 7/12
PHASE Konflikt · MODE CORE
Lvl 4 ▓▓▓▓░░░░░░ 4/10
Px 2/5 · Stress 3/10
Obj: Dossier sichern
```

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

## Läuft überall — mit Einschränkungen

ZEITRISS ist ein Datensatz, kein Programm — ein Masterprompt und 19
Wissensmodule. Überall dort, wo du einen System-Prompt setzen und
Wissensdateien laden kannst, läuft ZEITRISS.

**Aber:** ZEITRISS ist das komplexeste Projekt dieser Familie. Der
Masterprompt ist mit ~34 KB deutlich größer als bei den anderen Bausätzen.
Das bedeutet:

- **OpenWebUI + starkes Modell** — Optimale Erfahrung. Empfohlen.
- **Lumo / Claude Projects** — Funktioniert, wenn die Plattform genug
  System-Prompt-Platz bietet.
- **Custom GPTs (OpenAI)** — Eingeschränkt. System-Prompt-Limit zu klein,
  18+-Content wird teilweise redacted.
- **Schwache Modelle** — Kommen an Grenzen. ZEITRISS braucht Modelle, die
  komplexe Regelsysteme + Kreativität + Pacing gleichzeitig können.

**Dein Save ist JSON.** Charakter mitnehmen, in jedem Chat laden, Plattform
wechseln — das funktioniert überall. Die Schnittstelle ist portabel, auch
wenn nicht jede Plattform die volle ZEITRISS-Erfahrung liefern kann.

ZEITRISS ist ein Bausatz von pchospital. Alle Bausätze funktionieren
nach dem gleichen Prinzip: Masterprompt + Wissensmodule +
JSON-Schnittstelle. Privat kostenlos. Gewerblich lizenziert.

---

## Drei Schritte, dann spielen

1. **Plattform wählen.**
   [OpenWebUI](https://github.com/open-webui/open-webui) für die volle
   Erfahrung (self-hosted, kostenlos). Alternativ Browser-Projekte wie
   Lumo oder Claude Projects — etwas eingeschränkt, dafür ohne Terminal.
2. **Modell wählen.** Cloud ([OpenRouter](https://openrouter.ai) o.Ä.)
   oder lokal (Ollama). API-Key unter Einstellungen → Verbindungen
   eintragen.
3. **Setup starten.**

```bash
git clone https://github.com/pchospital-lab/ZEITRISS-md.git
cd ZEITRISS-md
python scripts/setup.py
```

Danach: neuen Chat in OpenWebUI öffnen, Modell
**ZEITRISS v4.2.6 Uncut** wählen, `Spiel starten (solo klassisch)`
tippen. Das Script legt Knowledge Base, Preset und Parameter selbst an.

**Browser-Pfad** (Lumo/Claude Projects): keine Installation, nur
Account und Wissenspaket — Anleitung in
[docs/setup-lumo.md](docs/setup-lumo.md).

**Setup-Guide** (Details, Flags, Troubleshooting, Plattform-Alternativen,
manuelles Setup): [docs/setup-guide.md](docs/setup-guide.md).

## Modell-Empfehlung (Stand März 2026)

- **Empfohlen:** `anthropic/claude-sonnet-4.6` — einziges Modell mit
  vollständiger Regeltreue. Stärkster Noir-Ton, sauberste Spielerfahrung.
- **Budget:** `z-ai/glm-5-turbo` — 7× günstiger als Sonnet, erkennt
  Regelgates und Load-Router. Bestes Preis-Leistungs-Verhältnis.
- **Ultra-Budget:** `deepseek/deepseek-v3.2` — ~$0.002/Turn, gute
  Atmosphäre, aber ignoriert teils neue Mechaniken (Load-Router, Psi-Gates).
- **Experimentell:** `z-ai/glm-5` — gute Atmosphäre, halluziniert aber
  gelegentlich Regeln.

> Ergebnisse aus dem [Modellvergleich 2026-03-17](internal/qa/evidence/playtest-2026-03-17/AUSWERTUNG.md)
> (5 Szenarien × 4 Modelle, Scorecard-Methodik).

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
