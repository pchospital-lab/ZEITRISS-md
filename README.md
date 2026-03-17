# ZEITRISS®-md Zeitreise RPG

[![LLM-Ready ✅][llm-ready-badge]][llm-ready-link]

> **Tech-Noir-Agententhriller mit KI-Spielleitung.** Ihr spielt Chrononauten
> des ITI — Elite-Agenten, die durch die Zeit springen, um die Hauptzeitlinie
> zu stabilisieren. Explodierende Würfel, HUD-Overlay, persistente Saves.
> **18+, Uncut.**

## Was ist ZEITRISS?

Ein Pen-&-Paper-RPG, bei dem die **KI eure Spielleitung ist**. Kein
vorgefertigtes Text-Adventure, kein Choose-Your-Own-Adventure — ein
vollständiges Rollenspielsystem mit Würfelproben, Charakterentwicklung,
Kampagnenfortschritt und einer KI, die alles leitet: Szenen, NSCs, Kämpfe,
Loot und Debrief.

Ihr müsst vor dem ersten Run nicht das Regelwerk lesen — OpenWebUI
einrichten, Preset wählen, losspielen.

### So sieht das aus

```
EP 1 · MS 3 · SC 7/12 · PHASE Konflikt · MODE CORE · COMMS OK
Lvl 4 ▓▓▓▓░░░░░░ 4/10 · Px 2/5 · Stress 3/10 · Obj: Dossier sichern
```

> Der Wachmann dreht sich um. Seine Hand geht zum Holster. Du bist schneller.

`Probe: Nahkampf → W6: [6] → Exploding! → W6: [2] = 8 + STR 4/2 + Talent 1
= 11 vs SG 8 → TREFFER`

> Dein Ellbogen trifft seinen Kehlkopf. Er klappt zusammen, lautlos.

`Kodex: Wachmann neutralisiert. Noise +1. Magazin 8/8. Nächster Checkpoint
in 40m.`

### Ähnlich, aber anders

| | AI Dungeon / KI-Chat-RPGs | Pen & Paper (D&D etc.) | **ZEITRISS** |
|---|---|---|---|
| Spielleitung | KI (frei, keine Regeln) | Mensch | KI (regelgebunden) |
| Würfelsystem | Keins | Ja | Ja (W6/W10, Exploding) |
| Persistenz | Nur im Chat | Manuell | JSON-Save, portabel |
| Multiplayer | Begrenzt | Am Tisch | Drop-in/Drop-out per Save |
| Regelwerk | Keins | Buch (100+ Seiten) | Im Wissensspeicher (KI liest mit) |

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

## In 3 Minuten starten

### Script-Setup (empfohlen)

```bash
git clone https://github.com/pchospital-lab/ZEITRISS-md.git
cd ZEITRISS-md
./scripts/setup-openwebui.sh
```

**Voraussetzung:** [OpenWebUI](https://github.com/open-webui/open-webui)
installiert + [OpenRouter](https://openrouter.ai)-Konto mit API-Key.

Das Script legt Preset + Wissensspeicher automatisch an. Danach: Preset
wählen, `Spiel starten (solo klassisch)` tippen oder den Neustart
natürlich formulieren — die KI versteht beides.
`solo schnell` bleibt als optionale Fast-Lane für Kurzrunden.

**Vor jeder Session:** `git pull` und Script erneut starten — hält alles
auf dem neuesten Stand.

### Manuelles Setup

Falls ihr ohne Script arbeitet:

1. 19 Wissensmodule hochladen (`core/spieler-handbuch.md` + 18
   Runtime-Module laut `master-index.json`)
2. `meta/masterprompt_v6.md` als System-Prompt setzen (nicht als
   Wissensdatei)
3. Parameter: Temperature `0.8` · Top-P `0.9` · Freq-Penalty `0.3` ·
   Max Tokens `64000`

Details: [Setup-Guide](docs/setup-guide.md) · [Lumo-Setup](docs/setup-lumo.md)

### Modell-Empfehlung (Stand März 2026)

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

1. **Agenten.** Als Chrononauten deckt ihr Zeitverschwörungen auf.
2. **Missionsphasen.** Briefing → Infiltration → Konflikt → Exfil → Debrief.
   12 Szenen pro Core-Mission, 14 bei Rift-Ops.
3. **Explodierende Würfel.** W6, ab Attribut 11 W10, ab 14 Heldenwürfel.
4. **Paradoxon-Index.** Belohnungssystem: Bei Px 5 schaltet ihr
   Bonus-Missionen mit Paramonstern und Artefakten frei.
5. **Boss-Rhythmus.** Mission 5 = Mini-Boss, Mission 10 = Episoden-Boss.
6. **Persistenz.** `!save` im HQ, JSON mitnehmen, im nächsten Chat laden.

→ **[Spieler-Handbuch](core/spieler-handbuch.md)** — Einleitung, Regeln,
Schnellstart, FAQ
→ **[SL-Referenz](core/sl-referenz.md)** — Tabellen, Befehle, Systemdetails

## Lizenz

- **Privat:** Kostenlos. CC BY-NC 4.0, Attribution
  "ZEITRISS® — pchospital".
- **Kommerziell:** Schriftliche Vereinbarung nötig (siehe
  [LICENSE](LICENSE)).
- **Streams/Videos:** Erlaubt mit Attribution (siehe
  [Creator-Lizenz](docs/creator-license.md)).
- **18+.** ZEITRISS® ist eine eingetragene Marke (DPMA).

## Feedback

Pull Requests werden nicht angenommen. Bei Regelfehler, Ideen oder
Tippfehler bitte ein
[Issue](https://github.com/pchospital-lab/ZEITRISS-md/issues) erstellen.
Sicherheitsmeldungen: [SECURITY.md](SECURITY.md).

---

© 2025-2026 pchospital – ZEITRISS® – private use only. See LICENSE.

[llm-ready-badge]: https://img.shields.io/badge/LLM--Ready-%E2%9C%85-success
[llm-ready-link]: core/spieler-handbuch.md
