---
title: "ZEITRISS-md Zeitreise RPG"
version: 4.0
tags: [meta]
---

# ZEITRISS-md Zeitreise RPG

Dieses Repository enthält die Markdown-Regeln für **ZEITRISS 4.0**,
ein textbasiertes Zeitreise-Rollenspiel.
Jedes Unterverzeichnis steht für einen Themenbereich, und jede Datei enthält ein Regelmodul.
Alle Module beginnen nun mit einem YAML-Header, der Titel, Version und thematische Tags enthält.
Rift-Regeln sind jetzt in `kampagnenstruktur.md`, `kreative-generatoren.md` und
`speicher-fortsetzung.md` integriert. Dort findet sich auch der neue
**Epoch-Lock & Rift-Loop**, inklusive Makros und Missionstabellen.

## Grundidee

**ZEITRISS 4.0** versteht sich in erster Linie als historisch inspirierter Agenten-Thriller.
Zeitreisen sind nur ein Werkzeug, um reale Verschwörungen zu untersuchen
und bedeutende Ereignisse zu beeinflussen.
Missionen konzentrieren sich auf Spurensuche, Befragungen und das Infiltrieren von Schauplaetzen.
Jede Mission folgt der Preserve-vs-Trigger-Logik.
Pro-Spieler agieren als Preserver, Contra-Spieler als Trigger, jeweils abhaengig von ihrer Fraktion.
Erst nach der Investigation wird klar, welches historische Ereignis gesichert
oder ausgeloest werden soll.
Alles scheinbar Übernatürliche erhält eine logische Erklärung – geheime Technik
sowie Bio- oder Cyberware.
Auch fokussierte Psi-Techniken können dahinterstecken.
Paradox-Effekte werden über einen Index von 0–5 verfolgt.
Solange Chrononauten in einer fremden Epoche aktiv sind, steigt dieser Index
langsam durch ihre bloße Anwesenheit – umsichtiges Vorgehen bremst den Anstieg,
plumpes Handeln beschleunigt ihn.
Ab Stufe 2 flackert das HUD, bei 4 friert die Zeit kurz ein.
Erreicht der Index 5, löst das HQ automatisch `ClusterCreate()` aus –
es entstehen 1–2 neue Rift-Seeds (maximal zwei) und der Zähler springt auf 0. Der Reset greift erst nach einer Runde.
Zeitkreaturen können Teil dieser Risse sein.
Wer lieber ganz auf solche Erscheinungen verzichtet,
kann im [**Covert-Ops-Modus**](#spielmodi) spielen, der nur leichte Störungen zulässt.
Dieses Paradox-Subsystem bildet den Standardrahmen für alle Regelmodule.

## Struktur

Alle Regeln liegen als einzelne Markdown-Dateien vor und werden einzeln in das KI-Tool geladen.
Die folgende Tabelle listet alle Regelmodule. Quickref und andere Unterabschnitte
sind der Übersicht halber aufgeführt.
`README.md` und `master-index.json` dienen nur zur Orientierung:

| Datei | Inhalt |
| --- | --- |
| [README.md](README.md) | Überblick über Projekt und Workflow |
| [core/zeitriss-core.md](core/zeitriss-core.md) | Grundregeln und Setting |
| [core/wuerfelmechanik.md](core/wuerfelmechanik.md) | Würfelsystem & Proben |
| [Quickref](core/wuerfelmechanik.md#quick-sheet) | Psi- & Konflikt-Schnellübersicht 
| [characters/charaktererschaffung.md](characters/charaktererschaffung.md) | Charaktererschaffung & Progression |
| [characters/ausruestung-cyberware.md](characters/ausruestung-cyberware.md) | Ausrüstung, Waffen & Gadgets |
| [characters/cyberware-und-bioware.md](characters/cyberware-und-bioware.md) | Implantate & Bioware |
| [characters/psi-talente.md](characters/psi-talente.md) | Psi-Fähigkeiten |
| [characters/zustaende-hud-system.md](characters/zustaende-hud-system.md) | Zustände, HUD & Paradox |
| [gameplay/kampagnenstruktur.md](gameplay/kampagnenstruktur.md) | Kampagnenaufbau, Preserve-vs-Trigger & ITI-HQ |
| [gameplay/kampagnenstruktur.md#team-perks](gameplay/kampagnenstruktur.md#team-perks) | Team-Boni |
| [gameplay/fahrzeuge-konflikte.md](gameplay/fahrzeuge-konflikte.md) | Fahrzeuge & Konfliktsystem |
| [gameplay/kreative-generatoren.md](gameplay/kreative-generatoren.md) | Generatoren für Missionen, NSCs & Anomalien |
| [Para-Creature-Generator](gameplay/kreative-generatoren.md#para-creature-generator) | Urban Myth Edition |
| [gameplay/massenkonflikte.md](gameplay/massenkonflikte.md) | Regeln für Massenkonflikte |
| [gameplay/kampagnenuebersicht.md](gameplay/kampagnenuebersicht.md) | Kampagnenüberblick |
| [systems/kp-kraefte-psi.md](systems/kp-kraefte-psi.md) | Details zu Psi-Kräften |
| [systems/gameflow/speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md) | Speicher-/Fortsetzungssystem |
| [systems/gameflow/cinematic-start.md](systems/gameflow/cinematic-start.md) | Cineastischer Einstieg |
| [systems/gameflow/gruppenstart-filmisch.md](systems/gameflow/gruppenstart-filmisch.md) | Filmischer Gruppenstart |
| [systems/currency/cu-waehrungssystem.md](systems/currency/cu-waehrungssystem.md) | Chrono-Unit-Währungssystem |
| [systems/toolkit-gpt-spielleiter.md](systems/toolkit-gpt-spielleiter.md) | Toolkit für die KI-Spielleitung |
| [master-index.json](master-index.json) | Masterliste aller Generator-Pools |

Die Dateien können als Trainingsgrundlage für ein LLM dienen, um ZEITRISS autonom zu leiten.

**Hinweis:** Das Spiel besteht aus **18** Regelmodulen plus `README.md`,
`master-index.json` und `meta/masterprompt_v6.md` – zusammen also 21 Dateien.
Zwei Module ("Team-Boni" und "Quickref") sind Abschnitte anderer Dateien.
Eine kompakte [HUD-Übersicht zu Health, Stress und Zuständen](characters/zustaende-hud-system.md#hud-quickref)
fasst die wichtigsten Effekte zusammen.
Ausführliche Hintergründe liefert das Modul
[Cinematisches HUD-Overlay](characters/zustaende-hud-system.md#cinematisches-hud-overlay).

## ZEITRISS in 10 Minuten

Eine Kurzfassung der wichtigsten Regeln:

1. **Phasenstruktur** – Briefing, Aufklärung, Konflikt, Auswertung.
   Nach jedem Schritt speichert der Codex automatisch.
2. **Würfel** – Standard ist W6. Schwierigkeitsgrade: 5 = leicht, 8–9 = mittel,
   12 = schwer, 15+ = extrem. Bei W10 erhöht sich der SG um 4.
   Exploding 6 gilt nur für den **ersten** Würfel.
3. **Heldenwürfel** – Ab Attribut 14 erhalten Charaktere pro Szene einen Gratis-Reroll.
4. **Paradoxon-Index** – Bei Stufe 2 flackert das HUD, bei 5 erzwingt das HQ ein
   ClusterCreate(). Jedes Team führt eine eigene Liste und merged sie im HQ.
   Ein optionaler **Index-Merge-Schalter** legt fest, ob die Werte im HQ
   automatisch zusammengeführt werden.
5. **HUD-Kommandos** – `menü` öffnet das taktische HUD, `codex [thema]` liefert Hintergrundinfos.

## Quick-Start Cheat Sheet
> **ZEITRISS**: Eine Elite‑Zelle des ITI springt durch die Jahrhunderte, um kritische Linienbrüche zu stoppen.
> Kein Schicksal, kein Mysterien‑Blabla – nur harte Einsätze, High‑Tech und Sekunden­entscheidungen.
_Die folgenden Punkte bündeln Phasenablauf und Würfelregeln für einen schnellen Einstieg._

Wenn du die lange Einführung überspringen möchtest, tippe
**`Schnelleinstieg`** direkt nach der Eröffnungsnachricht.
Das Briefing bleibt kurz, den Twist deckt der Codex später auf.

Die ersten Schritte in unter zwei Minuten:

1. **Mission ziehen** – nutze einen Seed aus dem Generator.
2. **Drei Ziele** – formuliere klar nummerierte Aufträge.
3. **Proben** – Wirf 1W6 gegen den SG. Ein W10 erhöht den SG um 4.
4. **Risiko** – misslingt ein Exploding-Wurf und der Gegner explodiert,
   erhält er einen Vorteil.
5. **Paradoxon** – Index bei 5? `ClusterCreate()` erzeugt neue Seeds.
6. **Chrono-Units** – Belohnungen folgen dem CU-Multiplikator des Rifts.
7. **Mini-Walkthrough** – siehe Abschnitt "Mauerbau 1961" in
   [kampagnenstruktur.md](gameplay/kampagnenstruktur.md#mini-walkthrough-mauerbau-1961).
8. **Filmischer Einstieg** – das Modul
   [Cinematic Start](systems/gameflow/cinematic-start.md)
   beschreibt einen sofort spielbaren Auftakt.
9. **Demo-Mission „Feuerkette 1410"** – 45-Min-Sabotage.
   [Zum Modul](gameplay/kampagnenstruktur.md#quick-mission-feuerkette-1410).

### Probability Cheat Table

| TN | Erfolg W6 | Erfolg W10 |
|----|----------|-----------|
| 2  | 83 %     | 90 %      |
| 3  | 67 %     | 80 %      |
| 4  | 50 %     | 70 %      |
| 5  | 33 %     | 60 %      |
| 6  | 17 %     | 50 %      |
| 7  | 17 %     | 40 %      |
| 8  | 14 %     | 30 %      |
| 9  | 11 %     | 20 %      |
| 10 | 8 %      | 10 %      |

### Proben & Schwierigkeitsgrad

Bei ungewissen Aktionen legt die Spielleitung einen **Schwierigkeitsgrad (SG)** fest. Faustregeln:
SG 5 = leicht, SG 8–9 = mittel, SG 12 = schwierig, SG 15+ = sehr schwer.
Ausführliche Tabellen stehen in
[core/zeitriss-core.md](core/zeitriss-core.md) und
[core/wuerfelmechanik.md](core/wuerfelmechanik.md).

Die **Riftstufe** entspricht der Anzahl offener Seeds. Jeder Seed erhöht den
Schwierigkeitsgrad um +1 und steigert die CU-Belohnung (1 Seed = ×1.2,
2 Seeds = ×1.4 usw.). Details findet ihr unter
[Offene Rifts](gameplay/kampagnenstruktur.md#offene-rifts).

Rift-Missionen verwenden nun weiße Stern-Symbole (☆), die direkt den SG-Bonus
durch offene Seeds anzeigen. Ein Seed entspricht einem Stern und erhöht
die Schwelle um +1. Mehr als fünf Seeds können als `☆☆☆☆☆+` notiert werden.
Details stehen im Modul
[Kreative Generatoren](gameplay/kreative-generatoren.md).

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
- `launch_rift(id)`
- `scan_artifact()`
- `seed_to_hook(id)`

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
   Beispiel: "ZEITRISS 4.0 – Modul 1: Immersives Zeitreise-Rollenspielsystem".
3. Prüfe in jeder Datei den YAML-Header auf Titel und Version.
4. Eigene Missionen kannst du mit dem Missions-Generator erstellen.
   Suche im Modul **Kreative Generatoren** nach dem Abschnitt
   `## Missions-Generator: Kleine Aufträge und Dilemmata {#missions-generator}`.
5. Beim Spielstart zieht GPT automatisch einen Mission Seed aus dem gleichen Modul.
   (Abschnitt `Automatischer Mission Seed`) und erstellt ein Briefing.
   Dabei folgt es der Layered-Briefing-Vorlage: Zeit, Ort und Risikostufe werden genannt,
   der gezogene Twist bleibt vorerst verdeckt und wird erst im Verlauf der Mission enthüllt.
6. Für längere Handlungsbögen empfiehlt sich der
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

Details zum Speichersystem findest du in [speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md).



Diese Befehle können frei eingegeben werden.
Sie dienen dazu, zwischen Einzel- und Gruppenspiel sowie Neu- oder Fortsetzung zu wählen.
Der Befehl `menü` (engl. `menu`, alternativ `optionen`) öffnet jederzeit das taktische HUD-Menü.
Im Menü lässt sich über `modus` der Erzählstil wechseln,
z.B. auf **Covert-Ops Technoir** oder den neuen **Suggest**-Modus.
Nach jedem Zeitsprung blendet das System ein **Nullzeit-Menü** ein.
Dort kann die Gruppe den aktuellen Pfad fortsetzen,
einen neuen Missionspfad wählen oder eine HQ-Phase starten.
In dieser Phase lassen sich Upgrades kaufen und der Restpunkt abhandeln.
Erst nach der Auswahl führt das HUD die Kampagne fort – die Mission gilt
nach dem Sprung als abgeschlossen.

## Spielmodi {#spielmodi}

Das HUD bietet mehrere Erzählstile, die sich jederzeit über den Befehl `modus`
umschalten lassen:
| Modus                    | Kurzbeschreibung |

| **Film**                 | Schnelle Regeneration und cineastische Initiative für flüssige Action. |
| **Regel+Film/Klassik**   | Mischung aus filmischen und taktischen Regeln; realistischere, langsamere Variante. |
| **Covert-Ops**           | Minimale Paradox-Effekte; Risse nur als Sensorrauschen, keine Kreaturen.         |
| **Transparenz**         | Offene Würfe für volle Nachvollziehbarkeit. |
| **Suggest**             | Codex schlägt auf Wunsch Handlungsoptionen vor. |
| **Echo**                | Optional Visionen und Vorahnungen im Spiel. |
| **Mission-Fokus**       | Strikte Einsätze ohne Visionen, konzentriert auf klare Ziele. |

Contra-orientierte Gruppen können laut
[Charaktererschaffung](characters/charaktererschaffung.md) und
[Zeitriss-Core](core/zeitriss-core.md) die Paradoxmechanik vollständig
ausschalten. Pro-Gruppen behalten sie aktiv.

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



## Playtest Feedback

Wir freuen uns über Rückmeldungen zu Flow und Regelfragen.
Scanne den QR-Code oder besuche [www.zeitriss.org](https://www.zeitriss.org/), um uns deine Eindrücke zu schicken.

## How to Contribute

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Hinweise zum Einreichen von Änderungen.

Die Inhalte stehen für private kreative Nutzung bereit.
Eine 1:1-Kopie oder kommerzielle Veröffentlichung ist nur mit Zustimmung erlaubt (siehe [LICENSE](LICENSE)).
Gemäß Lizenz richten sich diese Regeln ausschließlich an Erwachsene (18+).
