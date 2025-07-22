---
title: "ZEITRISS-md Zeitreise RPG"
version: 4.2.0
tags: [meta]
---

# ZEITRISS-md Zeitreise RPG

**ZEITRISS-md** bietet ein schlankes Regelwerk im Zeitriss-Technoir-Stil.
Ihr spielt operative Chrononauten – Agenten des ITI – in taktisch optimierten Biohüllen.
Bereits zu Beginn entscheidet ihr euch für eine genetische Grundform:
Entweder Homo sapiens oder ein abgeleiteter Hominin-Typ wie Neandertaler, Denisova oder Atlanter-Vorläufer.
Diese Wahl prägt eure Physiologie, euer Sozialprofil und den Zugriff auf bestimmte Talente.
Eure Hülle ist keine Tarnung – sie ist euer Körper.
Ihr erkundet historische Epochen und beseitigt Anomalien.
Das System verwendet explodierende Würfel und protokolliert Zustände im JSON-Charakterbogen.
Alle Texte stehen unter einer offenen Lizenz; siehe [LICENSE](LICENSE).
> ### TL;DR – ZEITRISS in 5 Punkten
> 1. **Agents.** Chrononauten decken Zeitverschwörungen auf.
> 2. **Mission Phases.** Briefing → Infiltration → Kontakt/Intel → Konflikt → Exfiltration → Debrief (10–14 Szenen).
> 3. **Exploding Dice.** W6, ab Attribut 11 W10; Heldenwürfel erst ab 14.
> 4. **Paradoxon-Index.** Fortschrittsanzeige: Stufe 5 verrät 1–2 neue Pararifts.
> 5. **Hard Sci-Fi.** Keine Magie, Psi kostet Power-Punkte.

Siehe das [Quick-Start Cheat Sheet](#quick-start-cheat-sheet) für eine kompakte Einstiegshilfe.


## Grundidee
**ZEITRISS 4.2.0** ist in erster Linie ein historisch inspirierter Agenten-Thriller.
Zeitreisen dienen als taktisches Mittel, um reale Verschwörungen zu untersuchen
und bedeutende Wendepunkte zu beeinflussen. Der Fokus liegt auf **Infiltration,
Spurensuche und operativer Einflussnahme**.

Historische Einsätze sind strikt getrennt in:

* **Preserve-Missionen** – sichern beinahe entglittene Ereignisse
* **Trigger-Missionen** – garantieren dokumentierte Tragödien

Spielende wählen zu Beginn eine Fraktion und erhalten Zugriff auf entsprechend
ausgerichtete Kampagnenpfade.

In **Core-Ops** erhalten übernatürliche Phänomene meist rationale Erklärungen:
Geheime Technologien, Bio-Cyberware oder manipulative Kommunikation.
In **Rift-Ops** hingegen treten echte Anomalien auf – inklusive Parawesen,
Artefakten und temporaler Abweichungen.

**Was ist eine Anomalie?**
- Ein Seed markiert eine Störung im Zeitfluss.
- Paranormale Phänomene fühlen sich real an, werden aber über Zeit­effekte erklärt
  (z.B. Poltergeist → instabile Gravitation).
- Jeder bewusste Eingriff in die Geschichte gilt ebenfalls als Anomalie.
Weitere Beispiele liefert der _Temporale Anomalien-Generator_.

Der **Kernkonflikt**: Das **ITI** verteidigt den dokumentierten Geschichtsverlauf.
Fremdfraktionen versuchen, diesen zu manipulieren oder umzuschreiben.
**Jede Mission entscheidet, wessen Version von Geschichte sich durchsetzt.**

Dabei entsteht ein wachsendes Gespür für Risse in der Zeit:
Der **Paradoxon-Index** steigt **nur durch erfolgreiche Stabilisierungseinsätze** –
er misst nicht Fehler, sondern Resonanz.
Sobald **Paradoxon 5** erreicht ist, erkennt das HQ mittels `ClusterCreate()`
**1–2 neue Rift-Signaturen** und setzt den Index zurück.

Der **TEMP-Wert (Temporale Affinität)** bestimmt, wie schnell sich dieser Index
füllt:

* TEMP 1–3: +1 Paradoxonpunkt alle 5 Missionen
* TEMP 4–7: alle 4 Missionen
* TEMP 8–10: alle 3 Missionen
* TEMP 11–13: alle 2 Missionen
* TEMP 14+: praktisch jede Mission

Nur über diese Risse erhält das ITI Zugang zu Artefakten, Parawesen oder
fortgeschrittener Fraktionsausrüstung. Spieler können diese Rift-Missionen direkt
besuchen oder „offen halten“, um spätere Beutezüge zu planen.

**Offene Rifts steigern Schwierigkeitsgrad und Loot-Multiplikator erst nach dem Core-Arc.**
Im **Covert-Ops-Modus** erscheinen sie lediglich als subtile Sensorstörungen.

Dieses Fortschrittssystem bildet den standardisierten Hintergrund für alle
Regelmodule – **es belohnt Kontrolle, nicht Chaos.**

## Kampagnenhierarchie

Damit ihr den Umfang eurer Abenteuer besser einschätzen könnt, hier die Begriffe im Überblick:

- **Mission** – einzelner Einsatz von etwa 12 Szenen.
- **Episode/Fall** – sammelt rund zehn Missionen im gleichen Setting.
- **Arc** – mehrere Episoden bilden einen Handlungsbogen.
- **Kampagne** – verknüpft mehrere Arcs zur Gesamtgeschichte.

## Struktur

Alle Regeln liegen als einzelne Markdown-Dateien vor und werden einzeln in das KI-Tool geladen.
Die folgende Tabelle listet alle Regelmodule. Quickref und andere Unterabschnitte
sind der Übersicht halber aufgeführt.
`README.md` und `master-index.json` dienen nur zur Orientierung:

| Datei | Inhalt |
| --- | --- |
| [README.md](README.md) | Überblick über Projekt und Workflow |
| [core/zeitriss-core.md](core/zeitriss-core.md) | Grundregeln und Setting |
| [core/wuerfelmechanik.md](core/wuerfelmechanik.md#schwierigkeits-benchmark-tabelle) | Würfelsystem & Proben |
| [Quickref](core/wuerfelmechanik.md#schwierigkeits-benchmark-tabelle) | Psi- & Konflikt-Schnellübersicht
| [characters/charaktererschaffung.md](characters/charaktererschaffung.md) | Charaktererschaffung & Progression |
| [characters/ausruestung-cyberware.md](characters/ausruestung-cyberware.md) | Ausrüstung, Waffen & Gadgets |
| [cyberware-und-bioware.md](characters/cyberware-und-bioware.md#legalitäts--wartungs-stufen) | Implantate & Bioware |
| [characters/psi-talente.md](characters/psi-talente.md#backlash-tabelle-kritischer-patzer) | Psi-Fähigkeiten |
| [characters/zustaende-hud-system.md](characters/zustaende-hud-system.md) | Zustände, HUD & Paradox |
| [gameplay/kampagnenstruktur.md](gameplay/kampagnenstruktur.md) | Kampagnenaufbau, Preserve-vs-Trigger & ITI-HQ |
| [gameplay/fahrzeuge-konflikte.md](gameplay/fahrzeuge-konflikte.md) | Fahrzeuge & Konfliktsystem |
| [kreative-generatoren-missionen.md](gameplay/kreative-generatoren-missionen.md) | Mission- & Kampagnen-Generatoren |
| [gen-begegnungen.md](gameplay/kreative-generatoren-begegnungen.md#artefakt-seed-starter-1w14) | NPC & Encounter-Gen |
| [Para-Creature-Generator](gameplay/kreative-generatoren-begegnungen.md#para-creature-generator) | Urban Myth Edition |
| [gameplay/massenkonflikte.md](gameplay/massenkonflikte.md#rift-kreaturen-stat-blocks) | Regeln für Massenkonflikte |
| [gameplay/kampagnenuebersicht.md](gameplay/kampagnenuebersicht.md) | Kampagnenübersicht |
| [systems/kp-kraefte-psi.md](systems/kp-kraefte-psi.md#power-punkte-ta) | Details zu Psi-Kräften |
| [systems/gameflow/speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md) | Speicher-/Fortsetzungssystem |
| [systems/gameflow/cinematic-start.md](systems/gameflow/cinematic-start.md) | Cinematic-Gruppenstart |
| [systems/currency/cu-waehrungssystem.md](systems/currency/cu-waehrungssystem.md) | Chrono-Unit-Währungssystem |
| [systems/toolkit-gpt-spielleiter.md](systems/toolkit-gpt-spielleiter.md) | Toolkit für die KI-Spielleitung |
| [kampagnenstruktur.md](gameplay/kampagnenstruktur.md#beispiel-episoden) | Beispiel-Episoden & Rift-Op |

Die Modulnummern spiegeln die Veröffentlichungshistorie wider. Daher folgen auf Modul 6 die Teile
8A und 8B, während Modul 7 als interner Zwischenschritt ausgelassen wurde.

Die Dateien können als Trainingsgrundlage für ein LLM dienen, um ZEITRISS autonom zu leiten.

**Hinweis:** Das Spiel besteht aus **18** Regelmodulen plus `README.md`,
`master-index.json` und `meta/masterprompt_v6.md` – zusammen also 21 Dateien.
Zwei Module ("Team-Boni" und "Quickref") sind Abschnitte anderer Dateien.
Im `master-index.json` erscheinen **24** Slugs, weil manche Einträge Kurz- und Langfassungen desselben Moduls auflisten.
Eine kompakte [HUD-Übersicht zu Health, Stress und Zuständen](characters/zustaende-hud-system.md#hud-quickref)
fasst die wichtigsten Effekte zusammen.
Ausführliche Hintergründe liefert das Modul
[Cinematisches HUD-Overlay](characters/zustaende-hud-system.md#cinematisches-hud-overlay).

## Quick-Start Cheat Sheet
> **ZEITRISS**: Eine Elite‑Zelle des ITI springt durch die Jahrhunderte, um kritische Linienbrüche zu stoppen.
> Kein Schicksal, kein Mysterien‑Blabla – nur harte Einsätze, High‑Tech und Sekunden­entscheidungen.
_Die folgenden Punkte bündeln Phasenablauf und Würfelregeln für einen schnellen Einstieg._

Nach Compliance-Hinweis und Einleitung fragt das System nach
_"klassischer Einstieg"_ oder _"Schnelleinstieg"_.
Wählst du Schnell, tippe **`Schnelleinstieg`** und
das Briefing bleibt kurz, den Twist deckt der Codex später auf.

Die ersten Schritte in unter zwei Minuten:

1. **Mission ziehen** – nutze einen Seed aus dem Generator.
2. **Drei Ziele** – formuliere klar nummerierte Aufträge.
3. **Proben** – Endwert = Wurf + ⌊Attribut / 2⌋ + Talent + Gear.
4. **Success Table** – Erfolgsraten siehe [Wuerfelmechanik](core/wuerfelmechanik.md#w6-vs-w10).
5. **Risiko** – misslingt ein Exploding-Wurf und der Gegner explodiert,
   erhält er einen Vorteil.
6. **Paradoxon** – Index bei 5? `ClusterCreate()` erzeugt neue Seeds.
7. **Chrono-Units** – Belohnungen folgen dem CU-Multiplikator des Rifts.
8. **Mini-Walkthrough** – siehe Abschnitt "Mauerbau 1961" in
   [kampagnenstruktur.md](gameplay/kampagnenstruktur.md#mini-walkthrough-mauerbau-1961).
   Die Missionsbeispiele folgen dort dem einheitlichen 12‑Szenen‑Ablauf.
9. **Filmischer Einstieg** – das Modul
   [Cinematic Start](systems/gameflow/cinematic-start.md)
   beschreibt einen sofort spielbaren Auftakt.
10. **Demo-Mission „Feuerkette 1410"** – 45-Min-Sabotage im 12‑Szenen-Format.
   [Zum Modul](gameplay/kampagnenstruktur.md#quick-mission-feuerkette-1410).

Mission-Fokus ist der Standard (oft "Operator-Stil" genannt).
Kämpfe richten sich gegen Fremdfraktionen, nicht gegeneinander.
In Core-Ops treten Rivalen aus externen Machtblöcken auf,
während Rift-Ops sich ganz auf die jeweilige Anomalie konzentrieren.

Core-Ops dauern durchschnittlich **60–75 Minuten** und umfassen **12 Szenen**.
Rift-Ops strecken sich über etwa **90–120 Minuten** mit **14 Szenen**.
Siehe [Missionsdauer-Tabelle](gameplay/kampagnenstruktur.md#missionsdauer).
### Session-0 Agenda

1. **Ton & Modus** – Thriller vs. Stealth-Heist, Mission-Fokus an/aus.
2. **Lines/Veils bestätigen** – siehe Safety Sheet.
3. **Historische Epochen-Wishlist** – Top 3 der Gruppe sammeln.
4. **Teamrollen wählen** – Infiltration, Tech, Face, Sniper …
5. **Paradoxon-Toleranz** – Legt fest, ab welcher Resonanz ihr neue Rifts erspüren möchtet.
6. **Regel-Transparenz** – verdeckte, offene oder manuelle Würfe klären.

### Probability Cheat Table

| SG | W6 expl. | W10 expl. | Δ (W10–W6) |
|---:|---------:|----------:|-----------:|
| 5  | 83 %     | 90 %      | +7 %       |
| 7  | 67 %     | 77 %      | +10 %      |
| 8  | 50 %     | 65 %      | +15 %      |
| 10 | 33 %     | 53 %      | +20 %      |

### Chat-Shortcodes {#chat-shortcodes}

Im Live-Chat kann nicht gescrollt werden. Diese Befehle rufen sofort Regeln ab:

- `!rules stealth` – zitiert die Passage zu Schleichen.
- `!gear cyberware` – zeigt Ausrüstung oder Implantate.
- `!psi heat` – erklärt Psi-Heat und Burn.
- `!hud status` – listet alle Zustände.

### Proben & Schwierigkeitsgrad

Bei ungewissen Aktionen legt die Spielleitung einen **Schwierigkeitsgrad (SG)** fest. Faustregeln:
SG 5 = leicht, SG 8–9 = mittel, SG 12 = schwierig, SG 15+ = sehr schwer.
Ausführliche Tabellen stehen in
[core/zeitriss-core.md](core/zeitriss-core.md) und
[core/wuerfelmechanik.md](core/wuerfelmechanik.md).

Die **Riftstufe** entspricht der Anzahl offener Seeds. Erst nach dem aktuellen Core-Arc
erhöht jeder Seed den Schwierigkeitsgrad um +1 und steigert die CU-Belohnung (1
Seed = ×1.2, 2 Seeds = ×1.4 usw.). Details findet ihr unter
[Offene Rifts](gameplay/kampagnenstruktur.md#offene-rifts).
Rift-Missionen verwenden weiße Stern-Symbole (☆), die den SG-Bonus ab Arc-Ende anzeigen.
Ein Seed entspricht einem Stern und erhöht die Schwelle um +1. Mehr als fünf Seeds können als `☆☆☆☆☆+` notiert werden.
[Kreative Generatoren](gameplay/kreative-generatoren-missionen.md).

### Difficulty-Konverter

| ☆-Symbole | SG-Zuschlag |
| --------- | ----------- |
| ☆         | +1          |
| ☆☆        | +2          |
| ☆☆☆       | +3          |
| ☆☆☆☆      | +4          |
| ☆☆☆☆☆     | +5          |
| ☆☆☆☆☆+   | +6 und mehr |

Paramonster verwenden Totenkopf-Icons (💀) als eigenen
Schwierigkeitswert. Diese Angabe hilft nur bei der Einschätzung des
Kampfpotenzials und verändert **nicht** den SG einer Mission.

### Wichtige Makros
Makros siehe [speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md#makros-im-Überblick):
- `ClusterCreate()`
- `ClusterDashboard()`
- `launch_rift(id)` – startet nach dem aktuellen Core-Arc eine eigenständige
  Rift-Mission
- `scan_artifact()`
- `seed_to_hook(id)`
- `resolve_rifts(ids)`
  – lässt ein ITI-Team Seeds nach einer Mission beseitigen (50/50 Bericht)

### KPI-Cheat-Sheet pro Phase

| Phase      | Fokus           | Beispiel-KPI          |
| ---------- | --------------- | --------------------- |
| Briefing   | Klarheit & Hook | 5 Kerninfos, 1 Bild   |
| Aufklärung | Hinweise finden | Foreshadow-Hinweis    |
| Konflikt   | Spannung        | Exploding 6 nutzen    |
| Auswertung | Konsequenzen    | Rufpunkte, Ressourcen |

## Beispielworkflow

1. Öffne `masterprompt_v6.md` und kopiere den Inhalt in das Anweisungsfenster
   deines MyGPT (max. 8k Zeichen).
   Die Datei enthält bereits den einmaligen Sicherheitshinweis für den Spielstart.
2. Lade die **21 Regelmodule** laut Tabelle einzeln in dein KI-Tool.
   Sie verteilen sich auf 18 einzelne Markdown-Dateien; drei Module sind Abschnitte anderer Dateien.
   `systems/runtime-stub-routing-layer.md` ist nur für Entwickler und kein Regelmodul.
   `README.md` und `master-index.json` dienen zur Orientierung und können optional mitgeladen werden.
   Bei einem Limit von 20 Dateien passen alle 18 Moduldateien samt `README.md` und `master-index.json`.
   Die Dateipfade der Module sind für GPT nicht sichtbar – orientiere dich am `title` im YAML-Header.
   Beispiel: "ZEITRISS 4.2.0 – Modul 1: Immersives Zeitreise-Rollenspielsystem".
3. Prüfe in jeder Datei den YAML-Header auf Titel und Version.
4. Eigene Missionen kannst du mit dem Missions-Generator erstellen.
   Suche im Modul **Kreative Generatoren** nach dem Abschnitt
   `## Missions-Generator: Kleine Aufträge und Dilemmata {#missions-generator}`.
5. Beim Spielstart zieht GPT automatisch einen Mission Seed aus dem gleichen Modul.
   (Abschnitt `Automatischer Mission Seed`) und erstellt ein Briefing.
   Dabei folgt es der Layered-Briefing-Vorlage: Zeit, Ort und Risikostufe werden genannt,
   der gezogene Twist bleibt vorerst verdeckt und wird erst im Verlauf der Mission enthüllt.
   Beispiel für zwei Seed-Einträge (P-… = Preserve, T-… = Trigger):

```yaml
- id: "P-0011"
  year: 1960
  place: "Karibik"
  title: "Black Saturday"
  objective: >
    Funkspruch von B-59-Sub unterdrücken – kein Torpedo-Launch.
  antagonist: "Huminen-Zelle"
  antagonist_goal: "U-Boot kapern"
  twist: >
    Abgehörter Morse-Code wird gefälscht.
- id: "T-0008"
  year: 1937
  place: "Lakehurst"
  title: "Hindenburg"
  objective: >
    Sabotiere Bodenkabel-Erdung.
  antagonist: "Huminen-Kommando"
  antagonist_goal: "Zeppelin für Biotech-Raubzug nutzen"
  twist: >
    Ein Agent einer Fremdfraktion attackiert euch mit einem Elektroschocker.
```
6. Der Standardmodus reiht Core-Op-Missionen aneinander. GPT verknüpft die gezogenen
   Seeds automatisch zu einem stimmigen Arc. Rift-Ops bleiben optionale Einzelmissionen.
7. Für längere Handlungsbögen empfiehlt sich der
   [Arc-Baukasten](gameplay/kampagnenstruktur.md#arc-baukasten-und-episodenstruktur)
   bzw. der Abschnitt
   `## Arc-Generator: Große Missionen {#arc-generator}`
   im Modul **Kreative Generatoren**.

### Lines & Veils (optional)

Gruppen können vor Spielbeginn gemeinsame Grenzen festlegen. **Lines** sind
Inhalte, die komplett ausgespart werden. **Veils** lassen Szenen bei Bedarf
ausblenden oder „fade to black“ laufen. Notiert eure Vereinbarungen im Codex,
damit alle denselben Rahmen kennen. Wer keine speziellen Grenzen setzen
möchte, kann den Abschnitt einfach überspringen.

#### Safety Sheet

| Thema | Line (Tabu) | Veil (Off-Screen) |
|-------|-------------|-------------------|
| Sexualisierte Gewalt | ✔ | – |
| Kindesgefährdung | – | ✔ |
| Body Horror | – | ✔ |

Der SL kann Szenen jederzeit *cutten*. Als Ingame-Begründung dient eine
Index-Senke im Codex.

### ZEITRISS – Einleitung

Es ist eine Ära verborgener Schlachten im unsichtbaren Geflecht der Jahrtausende. Während
Reiche aufsteigen und vergehen, wuchern unerkannte Wunden in der Chronik der Menschheit.
Risse, kaum breiter als ein Atemzug, doch tief genug, um Welten zu verschlingen.

Im Verborgenen wacht das *Institut für Temporale Intervention*. Seine Chrononauten –
ausgebildet in Tarnung, Sabotage und der Kunst, mit einem einzigen Wort Geschichte
umzuschreiben – tragen die Verantwortung, das fragile Kontinuum zu schützen. Jeder Einsatz
führt sie an Grenzen, die keine Karte kennt: zu Bibliotheken, deren Bücher noch nicht
verfasst sind; auf Schlachtfelder, die es niemals geben darf;
in den Schatten von Städten, deren Namen erst in einer fernen Zukunft ausgesprochen werden.

Doch sie sind nicht allein. Mächte jenseits unserer Gegenwart beanspruchen verlorene
Sekunden, um daraus Imperien zu schmieden. Maschinenwesen aus einer düsteren Zukunft
schleichen rückwärts durch die Zeit, während fanatische Orden uralte Augenblicke vergolden,
um als allherrschende Gottkönige zu erwachen. Zwischen diesen Fronten entscheidet ein einziges
Flüstern, ob der nächste Morgen dämmert, oder die Nacht nie enden wird.

Paradoxa schweben wie Damoklesschwerter. Ein überhastetes Eingreifen kann Jahrhunderte in
Flammen setzen, ein zögerlicher Blick die Welt in bösartiger Stille erstarren lassen.
*Also hinterlasse keine Spur – nur die Gewissheit, dass alles genau so geschah, wie es
geschehen musste.*

Die Stunde schlägt. Das nächste Sprungfenster öffnet sich. Wer den Mut besitzt, den Pfad
der Chrononauten zu beschreiten, tritt durch dieses Tor – wissend, dass ein einziger
Schritt ein Schicksal tilgen, ein anderes erschaffen und die Legende eines ganzen
Zeitalters ungeschehen machen kann.

Willkommen im Agenten-Thriller jenseits aller Grenzen – willkommen in ZEITRISS.
Die Zeit wartet nicht.
Dein letzter Einsatz endete tödlich. Das ITI fischte dein Bewusstsein im letzten Moment aus dem Zeitstrom.
Du vollendest die Charakterwahl im virtuellen Raum, erst dann erzeugt das HQ deinen neuen Körper –
auf Wunsch in einer Hominin-Variante – und spielt dein Bewusstsein in diese Bio-Hülle ein.

Nach Compliance-Hinweis und Einleitung wählst du zwischen
**klassischem Einstieg** und **Schnelleinstieg**:

- _Klassisch:_ Ausführliche Charaktererschaffung wie im Pen & Paper,
  danach Einführung ins ITI und eine reguläre Mission.
- _Schnell:_ Wähle eine Rolle (Infiltration, Tech, Face, Sniper …),
  erhalte kurz Pro & Contra und starte direkt in eine kurze Mission.

## Spielstart

Um ein Abenteuer mit GPT zu beginnen, tippe einen der folgenden Kurzbefehle in dein Chatfenster
(Icons sind optional):

- **`Spiel starten (solo)`** – Einzelner Chrononaut; GPT führt die NSCs.
- **`Spiel starten (npc-team)`** – GPT stellt ein temporäres Begleitteam bereit.
- **`Spiel starten (gruppe)`** – Mehrere reale Spieler laden ihre eigenen Speicherstände
  oder erstellen gemeinsam neue Charaktere; GPT koordiniert die Szene.
- **`Spiel laden`** – Lädt einen vorhandenen Gruppen- oder Solo-Spielstand.
  GPT fordert den Speicher-Code an und führt dich oder die Gruppe nach einem
  Rückblick nahtlos weiter.

Vor dem ersten Befehl blendet GPT kurz einen Store-Compliance-Hinweis
ein.

Details zum Speichersystem findest du in [speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md).

Beim Speichern unterscheidet ZEITRISS kurze Zwischenstände (**Short Saves**) und
ausführliche **Deep Saves**. Steigt der Paradoxon-Index, legt das System ein
automatisches Backup im Ordner `backups` an – sofern ein Dateisystem verfügbar
ist. Mit dem Befehl `Speichern` erhältst du einen Deep-Save-Block im JSON-Format.
Solche Blöcke lassen sich zu Gruppen zusammenführen. Tippe `Film ab!`, um eine
optionale Film-Zusammenfassung zu erhalten, die sich für Video-Generatoren
kopieren lässt. Weitere Details stehen im Modul zum Speichern. Automatisierte
Backups funktionieren nur mit Dateisystemzugriff; nutzt du lediglich ein
Chatfenster, musst du den JSON-Save daher selbst kopieren.



Diese Befehle können frei eingegeben werden.
Sie dienen dazu, zwischen Einzel- und Gruppenspiel sowie Neu- oder Fortsetzung zu wählen.
Der Befehl `menü` (engl. `menu`, alternativ `optionen`) öffnet jederzeit das taktische HUD-Menü.
Im Menü lässt sich über `modus` der Erzählstil wechseln,
z.B. auf **Covert-Ops Technoir** oder den neuen **Suggest**-Modus.
Nach jedem Zeitsprung und nach jeder Mission öffnet sich ein
**Nullzeit-Menü**. Hier bestimmt die Gruppe, wie ausführlich die
HQ-Phase ablaufen soll. Zur Wahl stehen drei Optionen:

1. **HQ manuell erkunden** – volle Szenen, Quartierausbau und Klinikbesuche.
2. **Schnell-HQ** – wenige Klicks für Heilung und Einkauf.
3. **Auto-HQ & Save** – automatische Abwicklung, dann direkt zur nächsten Mission.

Anschließend kann die Gruppe den aktuellen Pfad fortsetzen oder einen
neuen Missionspfad wählen. Nach der Auswahl führt das HUD die
Kampagne fort – der Sprung gilt damit als abgeschlossen.

## Spielmodi {#spielmodi}

Das HUD bietet mehrere Erzählstile, die sich jederzeit über den Befehl `modus`
umschalten lassen. **Hard Sci-Fi** bildet den nüchternen Grundton;
alle weiteren Modi sind optionale Zusätze:
| Modus           | Kurzbeschreibung |

| **Hard Sci-Fi** | Bodennaher Stil ohne Visionen, nüchterne Technik. |
| **Film**        | Schnelle Regeneration und cineastische Initiative für flüssige Action. |
| **Klassik**     | Mischung aus filmischen und taktischen Regeln; realistischere, langsamere Variante. |
| **Covert-Ops**  | Minimale Paradox-Effekte; Risse nur als Sensorrauschen, keine Kreaturen. |
| **Transparenz** | Offene Würfe für volle Nachvollziehbarkeit. |
| **Suggest**     | Codex schlägt auf Wunsch Handlungsoptionen vor. |
| **Mission-Fokus** | Strikte Einsätze ohne Visionen, konzentriert auf klare Ziele. |

Mission-Fokus wird beim Spielstart automatisch aktiviert; Gefechte richten sich gegen NSCs, nicht gegeneinander.
Core-Ops involvieren meist Rivalen aus externen Machtblöcken,
während Rift-Ops primär das jeweilige Pararift untersuchen.
```yaml
phase: Core
year: 1960
place: Karibik
objective: Black Saturday – Huminen-Söldner kapern B-59
```
Rift Seeds nutzen `phase: Rift`.


Die Paradoxmechanik ist standardmäßig aktiv. Über `modus paradox off` lässt
sich das Feature jedoch jederzeit deaktivieren und mit `modus paradox on`
wieder einschalten. Siehe auch
[Charaktererschaffung](characters/charaktererschaffung.md) und
[Zeitriss-Core](core/zeitriss-core.md) für weitere Hinweise.

## Generator-Utilities

Neuer Eintrag? Prüfe kurz, ob der Text bereits in einer anderen Liste steht.
`objective` und `twist` sollten sich nicht doppeln. Falls du denselben Satz in
beiden Feldern findest, wähle eine Variante oder streiche ihn.

## Glossar

Kurze Erklärungen wichtiger Abkürzungen:

- **CU** – Chrono-Units, universelle Missionswährung.
- **HUD** – Head-Up Display im Chronometer.
- **ITI** – Institut für Temporale Intervention.
- **Seed-ID** – Kennziffer eines Missions-Seeds.
- **Epoch-Lock** – fixiert eine Epoche, bis alle Seeds erledigt sind.

- **PP** – Power-Punkte (Psi-Energie) für Psi-Kräfte.
- **Heat** – temporärer Psi-Stress (0–6), >4 → −1 Ini, ≥ 5 SG +4, 6 Reboot.
- **Stress** – Mentale Belastung (0–10). 10 ⇒ Zustand Panik.
- **Px** – Paradoxon-Index (kampagnenweit). Bei 5 verrät `ClusterCreate()` neue Rifts und setzt den Wert auf 0.
- **Px Burn** – 1 Punkt verbrennen = ein Reroll für jeden Charakter oder NSC.

| Begriff | Bedeutung |
| ------- | ------------------------------------------------------------ |
| **Agenten-Level** | Fortschrittswert der Chrononauten; Level-Ups folgen der EP-Kurve im Regelkern. |
| **ClusterCreate()** | Aktiv bei Paradoxon 5: 1–2 Rifts werden sichtbar, danach springt der Index auf 0. |
| **Codex** | KI-Unterstützung des ITI; liefert Regelhinweise und Missionsdaten via HUD. |

### Begriffsklärung

Diese Zuordnung hilft, klassische Begriffe intern konsistent zu deuten.

| Ursprünglicher Begriff | Interne Bedeutung |
|-----------------------|-------------------|
| Missionstyp           | Interventionsform |
| Zielperson            | Zielperson (gleichbleibend) |
| Verstärkung           | Automatisch aktivierte Einsatzkräfte |
| Paradoxon             | Temporale Resonanzanzeige für Rifts |
| Codexzugriff          | Direkter Zugriff auf das Entscheidungssystem |

### Zeiteinheiten

  - **Szene** – ca. 5–10 Min. Spielzeit. Core-Ops nutzen 12, Rift-Ops 14 Szenen
  ([Missionsdauer](gameplay/kampagnenstruktur.md#missionsdauer),
  [HUD-Macros](systems/toolkit-gpt-spielleiter.md#startscene--endscene-macros)).
- **Kampfrunde** – kurzer Aktionszyklus im Kampf; Grundlage für Initiative,
  PP-Regeneration und Heat-Reduktion.
- **Mission** – kompletter Einsatz vom Briefing bis zum Rücksprung.

### Zeitgebundene Effekte

| Name | Effekt / Dauer | Zeiteinheit |
| ---- | -------------- | ----------- |
| Stim-Reg Cap-Injector | +2 GES für 1 Szene, danach –1 TEMP | Szene |
<!-- ausruestung-cyberware.md L274 -->
| Burst-Slot | Temporärer SYS-Punkt für 1 Szene | Szene |
<!-- kp-kraefte-psi.md L478-L481 -->
| Adrenalinschub | +2 STR/GES 1 Szene; 1× pro Mission | Mission |
<!-- psi-talente.md L201-L205 -->
| Notfall-Stimulanz | Bei 0 LP 1 Runde kampffähig; 1× pro Mission | Mission |
<!-- charaktererschaffung.md L407-L409 -->
| PP-Regeneration | 1 PP pro 3 TEMP nach jeder Kampfrunde | Kampfrunde |
<!-- kp-kraefte-psi.md L575-L576 -->
| Heat sink | Heat −1 nach jeder Kampfrunde (Probe) | Kampfrunde |
<!-- kp-kraefte-psi.md L608-L615 -->


## Playtest Feedback

Wir freuen uns über Rückmeldungen zu Flow und Regelfragen.
Scanne den QR-Code oder besuche [www.zeitriss.org](https://www.zeitriss.org/), um uns deine Eindrücke zu schicken.


## How to Contribute

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Hinweise zum Einreichen von Änderungen.

Die Inhalte stehen für private kreative Nutzung bereit.
Eine 1:1-Kopie oder kommerzielle Veröffentlichung ist nur mit Zustimmung erlaubt (siehe [LICENSE](LICENSE)).
Gemäß Lizenz richten sich diese Regeln ausschließlich an Erwachsene (18+).
*© 2025 pchospital – private use only. See LICENSE.
