# ZEITRISS® — Dein Einsatz beginnt hier

<p align="center">
  <img src="docs/gameicon.png" alt="ZEITRISS" width="200">
</p>

> **Ein Tech-Noir-Zeitreise-Rollenspiel mit KI-Spielleitung.**
> Erschaffe deinen Chrononauten, stelle deine Runde zusammen und entscheide,
> welchen Preis die Geschichte wert ist. Würfelproben, Missionen und ein
> persönlicher Spielstand begleiten dich durch die Zeit. **18+, Uncut.**

**[Im Terminal starten](docs/spielerstart.md)** ·
**[Im Chat spielen](docs/setup-guide.md#browser-einstieg-ohne-installation)** ·
**[Gemeinsam spielen](docs/koop-online-spielen.md)**

## Ein Rollenspiel. Deine Entscheidungen.

Du spielst einen Chrononauten des ITI. Deine Aufträge führen dich in andere
Zeiten, mitten in Konflikte um die Hauptzeitlinie. Die KI übernimmt die
Spielleitung: Sie beschreibt Szenen, spielt Nebenfiguren und führt durch
Proben, Kämpfe und Debriefings. Du bestimmst, was deine Figur versucht.

ZEITRISS ist kein fest verzweigtes Text-Adventure. Regelwerk, Spielanweisungen
und Wissensmodule bilden die Grundlage; deine Runde entwickelt die Geschichte
im Spiel. Ihr müsst vor dem Start nicht das Regelwerk lesen. Fragen zu Welt,
Ausrüstung oder einer Probe könnt ihr direkt an die Spielleitung stellen.
Der Standard-Ladepfad verwendet den Spielleiter-Masterprompt und **19 Wissensmodule**;
der [Setup-Guide](docs/setup-guide.md) führt durch die Einrichtung.

## MMO ohne Server — dein Spielstand reist mit

Ein zentraler ZEITRISS-Spielserver ist für den Austausch deiner Figur nicht nötig:
Du nimmst ihren gültigen JSON-Save in eine andere geeignete Runde mit.
„MMO ohne Server“ beschreibt dieses Spiel- und Savekonzept, nicht eine bereits
veröffentlichte Terminal-Netzwerklobby. Für KI-Spielleitung und optionale
KI-Mitspieler brauchst du weiterhin die jeweils eingerichteten Modelldienste.

## Wähle deinen Spielweg

| Spielweg | Das brauchst du | Dein Einstieg |
| --- | --- | --- |
| **Lokales Terminal** | Python, eingerichtete KI-Spielleitung und ein freigegebenes Modellbudget; für KI-Mitspieler zusätzlich eine Persona-Anbindung | [Spielerstart](docs/spielerstart.md) |
| **Chat und JSON-Save** | Eine geeignete Chatplattform mit dauerhaften Anweisungen, Wissensquellen und Retrieval | [Setup-Guide](docs/setup-guide.md#browser-einstieg-ohne-installation) |

Am Terminal spielst du solo oder mit anderen Menschen an einem Gerät.
Freiwillige KI-Mitspieler können deine Runde ergänzen. Gemeinsames Spiel
über getrennte Geräte beschreibt der Chat-Leitfaden; eine native
Netzwerk-Lobby im Terminal ist noch nicht ausgeliefert.

<a id="terminal-client-lokal-entwicklungskandidat"></a>

## Dein erster Terminal-Einsatz

Starte im entpackten Projektordner mit eingerichteter Python-Umgebung:

```bash
python3 scripts/mmo_sim.py
```

Über **`charaktere`** wählst du eine Figur, erschaffst eine neue oder
importierst einen vorhandenen Save. **`spielen`** führt dich zur
Zusammenstellung deiner Runde. **`fortsetzen`** bringt dich später zu deinem
vorhandenen Stand zurück. **`?`** öffnet die Hilfe zum aktuellen Schritt.

Installation, Spielleiter-Anbindung, Import und die genaue Menüführung:
**[Spielerstart im Terminal](docs/spielerstart.md)**.

> **Terminalstatus — lokale Beta:** Der lokale R4-Speicher- und
> Fortsetzungsweg ist im beschriebenen Umfang unabhängig abgenommen
> (29. Oktober 2026). Der vorhandene Referenzlauf umfasst fünf Figuren in
> einem Duo und einem Trio mit je zwei geschlossenen Runden; abschließend
> wurden fünf Endsaves in einem frischen Prozess geladen und eine wirksame
> Duo-Folgeaktion belegt. [Stand und Grenzen](docs/terminal-status.md)

## Save = Charakter

Dein persönlicher JSON-Save enthält den zuletzt gespeicherten Stand deiner
Figur. Bewahre eine eigene gültige Kopie auf. Du kannst ihn als Charakterbogen
zu einer anderen geeigneten ZEITRISS-Runde mitnehmen; die jeweilige Plattform
muss das Regelwerk und den Save korrekt laden können.

**Im Chat:** `!save` beziehungsweise `!speichern` erzeugt den Save im Chat.
Speichere ihn selbst als Datei; das Kommando allein legt keine Datei auf
deinem Gerät an. Ein neuer Spielchat lädt den Save mit `Spiel laden` oder
`!laden`. Spielstände gehören nicht dauerhaft neben die Regelquellen.

**Im Terminal:** Freie Handlungen und Gespräche schreibst du als normale
Sprache — dafür brauchst du kein Kommando. Zum *zuverlässigen* Abschließen und
Speichern einer Runde sendet der Leader **im HQ `!save` (oder `!speichern`) als
eigene, einzelne Nachricht**; die Spielleitung gibt darauf deinen Stand als
Save-Block aus, den der Client erntet. „Speichere meinen Charakter“ ist am
Terminal *kein* gleichwertiger Auslöser — die Save-Erkennung hängt am
`!save`-Kommando und am tatsächlichen Save-Block, nicht an einer Formulierung
der Spielleitung. Gespeichert wird nur im HQ; in Briefing, Einsatz und Debrief
ist Speichern gesperrt (SaveGuard). Den internen Abschlussmarker musst du weder
kennen noch eingeben. Die Exportfunktion unter `charaktere` schreibt deinen
bereits aktuellen Stand, `/pause` hält die Runde an, nach einem Neustart setzt
`fortsetzen` fort — keine dieser Aktionen ersetzt einen fehlenden
Abschnittsabschluss. Maßgeblich ist der zuletzt tatsächlich geschriebene gültige
Stand, keine pauschale Zusage gegen jeden Datenverlust.

Bleibt ein `!save` nach wiederholten Formatfehlern ohne gültigen Stand, sichert
das Terminal automatisch einen **Kompatibilitätsstand** (Best Effort /
SAVECOMPAT, „Gesichert mit Prüfhinweisen“). Eine verbleibende strukturelle
Warnung ist **kein** bestandener Schema-Check, und der nächste Start bereinigt
den Stand nicht garantiert vollständig — Best Effort und SAVECOMPAT sind
verschiedene Dinge. Kurz erklärt unter
[Spielerstart](docs/spielerstart.md#best-effort-und-savecompat), technische
Details: `systems/gameflow/speicher-fortsetzung.md#kompatibilitaetsstand`.

## Eine echte Szene aus dem Terminal

Kein ausgedachtes Beispiel: unveränderte Originaltexte aus einem abgenommenen
R4-Lauf (Episode 1, Mission 3), erneut durch den echten Terminal-Renderer
dargestellt (Replay). Für die README gekürzt — Auslassungen sind mit `[…]`
markiert, der Wortlaut ist nicht verändert. Lange Zeilen bricht dein Terminal
selbst auf die Fensterbreite um. Herkunft und Prüfsummen:
[Terminalstatus § Showcase-Szene](docs/terminal-status.md#showcase-szene--herkunft).

**Im HQ — du planst den Einsatz, in freier Sprache:**

```text
[…]

MAHLBERG — MS3, Eröffnung

Zwei Dinge in dieser Reihenfolge, und die Reihenfolge ist nicht Geschmack.

Erstens Lager B. Wir gehen ohne Papier hinein. BREACH zählt — Stückzahlen, Umrisse, Positionen, was auf Paletten steht und was nicht auf Paletten steht. Ich messe: lichte Weite, Regalhöhe, Gangbreite, Abstand zur Brandwand. Zentimeter, keine Schätzungen. […]
```

**Mitten im Einsatz — deine Entscheidung, in freier Sprache:**

```text
Option 3 — der Ordner im selben Raum. Das ist mein Zug.

MAHLBERG — Lager B, Bürotrakt, 07:19

Der Bericht ist fotografiert, bevor ich irgendetwas anderes anfasse. Sieben Bilder: Deckblatt mit Berichtszeitraum, letzte Seite vollständig, dann die Namenszeile einzeln — schräg, zweimal, mit und ohne Streiflicht. Das Bleistiftdatum einzeln. Der Klemmhefter bleibt zu, der Bericht bleibt liegen, der Pappbecher wird nicht verschoben. […]
```

**Und die KI-Spielleitung antwortet — HUD, Fund und neue Lage:**

```text
EP 1 · MS 3 · SC 02/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ · Px 1/5 · Stress 0/10 · Obj: Lager B → Hendrich & Co. · Exfil —

Kodex: Szene 2 läuft — Bürotrakt · 07:20 Uhr. Zeitgrenze 07:25.

---

BREACH zieht die Tür auf drei Fingerbreit und stellt sich mit dem Rücken zur Wand. Von dort hat er die Treppenhaustür im Blick und den Gang bis zur Nordzugangsecke. Er sagt nichts.

Du nimmst den Ordner heraus. Rücken zur Wand zeigt links, er steht zweiter von links, Unterkante auf der mittleren Regallippe. Du erinnerst dir an alles davon.

[…]

Die Treppenhaustür hat sich bewegt — kein Geräusch, aber Lichtveränderung im Spalt. Jemand ist im Treppenhaus. Noch nicht im Gang.

---

[…]

---

Drei Optionen

1. Jetzt raus, Nordzugang. […]

2. Stehenbleiben, Cover halten. […]

3. Raus, aber nicht Nordzugang. […]

Freie Aktion — wenn ihr etwas anderes tut.
```

Du handelst in freier Sprache; die Spielleitung führt Szene, Nebenfiguren,
Proben und Konsequenzen — und gibt die Entscheidung an dich zurück. Die
HQ-Eröffnung und der Spielzug sind zwei echte Spielermomente; die Reaktion
darunter ist die tatsächliche Antwort der Spielleitung auf den Spielzug im
Bürotrakt. Der Ausschnitt zeigt eine Infiltration; ein gespeicherter echter
Kampf liegt als Terminalbeleg noch nicht vor und wird hier nicht behauptet.

## Das Spielsystem in Kürze

1. **Agenten.** Als Chrononauten deckt ihr Zeitverschwörungen auf — Schicht
   für Schicht, nicht per Briefing-Dump. Jede Episode baut sich auf wie eine
   Staffel: erst der kleine Auftrag vor großer Kulisse, dann die Verdichtung,
   dann das Finale.
2. **Missionsphasen.** Briefing → Infiltration → Konflikt → Exfil → Debrief.
   12 Szenen pro Core-Mission, 14 bei Rift-Ops.
3. **Preserve & Trigger — zwei Haltungen, ein Ziel.** Euer Job ist, die
   Geschichte zu wahren. Die eigentlichen Gegner sind **Fremdfraktionen**,
   die den Geschichtsverlauf zu ihren Gunsten umschreiben wollen. Gegen die
   steht ihr gemeinsam — egal, welche Haltung ihr gewählt habt.
   - **Preserve-Agenten** verhindern Ereignisse, die in der dokumentierten
     Geschichte *gerade so nicht* passiert sind, aber in eurer Zeitlinie
     doch einzutreten drohen.
   - **Trigger-Agenten** sorgen dafür, dass dokumentierte Tragödien
     stattfinden, weil ihr Ausbleiben eine schlimmere Kettenreaktion
     auslösen würde.

   Als Trigger-Agent fühlt es sich an wie die dunkle Seite (Katastrophen
   passieren lassen), als Preserve-Agent wie Heldentum (Katastrophen abwenden).
   Ist aber keins von beidem — beide Seiten sind Verbündete innerhalb des
   ITI und kämpfen gegen denselben äußeren Feind.
   Neutrale spielen in Teams beider Haltungen mit; Preserve- und
   Trigger-Agenten operieren im Feld (Core-/Rift-Ops) nur innerhalb
   derselben Haltung zusammen (operatives Zellenprinzip, keine
   Feindschaft). In der **PvP-Arena** ist dagegen jede Kombination
   erlaubt — dort messt ihr euch haltungsübergreifend.
   Chrononauten agieren als Werkzeug eines größeren Plans des ITI.
4. **Explodierende Würfel.** W6, ab Attribut 11 W10, ab 14 Heldenwürfel.
5. **Paradoxon-Index.** Belohnungssystem: Der Anstieg von Px hängt vom
   Missionsverlauf und euren Preserve/Trigger-Entscheidungen ab. Bei Px 5 werden 1–2
   Riftkoordinaten auf der Raumzeitkarte sichtbar — dort warten Rift-Ops
   mit Paramonstern und Artefakten.
6. **Boss-Rhythmus.** Mission 5 = Mini-Boss, Mission 10 = Episoden-Boss.
7. **Persistenz.** `!save` im HQ, JSON mitnehmen, im nächsten Chat laden.

**Freie Sprache zuerst — mit einer Terminal-Ausnahme:** Aktionen und Gespräche
formulierst du frei. Im **Chat** sind `!save`, `!bogen` oder `!menü` nur bequeme
Kurzformen; du kannst genauso natürlich „speichere meinen Charakter“ oder „zeig
meinen Bogen“ schreiben, die Spielleitung reagiert in-world. **Im Terminal** gilt
für den *zuverlässigen* Abschnittsabschluss dagegen: der Leader sendet im HQ
`!save` (oder `!speichern`) als eigene Nachricht — eine freie Speicherbitte ist
dort kein gleichwertiger technischer Befehl (siehe
[Save = Charakter](#save--charakter)).

→ **[Spieler-Handbuch](core/spieler-handbuch.md)** — Einleitung, Regeln,
Schnellstart, FAQ
→ **[SL-Referenz](core/sl-referenz.md)** — Tabellen, Befehle, Systemdetails

## Einrichtung und Referenzsetup

Für den Chatweg gibt es zwei Varianten: den vollständigen Masterprompt als
dauerhafte Anweisung mit 19 Wissensmodulen, oder bei kleinerem Anweisungsfeld
den Project-Bootstrap mit Masterprompt und Modulen als Quellen. Beide
Varianten werden im [Setup-Guide](docs/setup-guide.md) beschrieben. Nicht
miteinander stapeln und den Masterprompt nicht abschneiden.

Der dokumentierte Entwicklungs-Referenzstack verwendet OpenWebUI, LiteLLM
und `anthropic/claude-sonnet-4.6`. Ein passendes Modell und korrektes Retrieval
sind Voraussetzungen, keine Garantie für fehlerfreie Spielleitung.
Prompt-Caching kann Eingabekosten senken; daraus folgt keine pauschale
90-Prozent-Ersparnis für eine gesamte Runde. Tatsächliche Kosten hängen von
Anfragen, Ausgaben, Cachetreffern und dem verwendeten Anbieterweg ab.

## Mehr aus deiner Runde machen

Vorhandene Biografien, Bögen und Notizen können als Ausgangspunkt für eine
neue Figur dienen. Rolle, Hintergrund und Motive werden in einen
ZEITRISS-kompatiblen Startcharakter übertragen; fremde Regeln werden nicht
unverändert übernommen.

Das [Creator Studio](docs/creator-mode.md) hilft bei Medienkonzepten aus
Saves, Transkripten und autorisierten Referenzen. Es ist ein separates
Projekt und verändert keinen Spielfortschritt.

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

