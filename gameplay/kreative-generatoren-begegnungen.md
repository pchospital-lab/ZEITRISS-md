---
title: "ZEITRISS 4.2.6 - Modul 8B: Kreative Generatoren - Begegnungen"
version: 4.2.6
tags: [gameplay]
---

# ZEITRISS 4.2.6 - Modul 8B: **Kreative Generatoren - Begegnungen**

## Gameplay-Index

Modul 8B schließt an 8A an. Modul 7 - Fahrzeuge, Konfliktsystem & Kreative Generatoren - steht Euch als veröffentlichter Zwischenschritt zur Verfügung. Es bildet die Brücke in diese Werkzeugkiste.

- NSC-Generator: Begegnungen im Zeitstrom
- Encounter-Pool: Schnelle Gegnerlisten nach Risiko
- Encounter-Pakete & Twist-Seeds
- Kreaturen- & Gestalten-Generator
- Para-Creature-Generator: Rift Casefile Edition
- Urban-Myth-Generator (False Lead)
- Boss-Generator: Mini-, Episoden- und Rift-Bosse
- Artefakt-Generator: Parawesen-Trophies
- Para-Artefakt-Generator: On-The-Fly (Körperteil × Buff-Matrix)
- Kulturfragmente-Generator: Farbe für die Epochen
- Mood-Snippet-Generator
- Rätselbibliothek: Kurze Hürdenszenen
- Temporale Anomalien-Generator & Historische Anomalien
- Rätsel-Sets: Komplette Szenen

## NSC-Generator: Begegnungen im Zeitstrom {#nsc-generator}

Wenn die Spieler spontan irgendjemanden treffen sollen - sei es Verbündeter, Informant oder
Hindernis - hilft es ungemein, einen spannenden NSC aus dem Hut zu zaubern. Dieser Generator liefert
euch im Schnellverfahren einen Nichtspielercharakter mit Persönlichkeit, indem er **Rolle**,
**Persönlichkeit** und **Besonderheit** kombiniert.

Wählt oder würfelt je eine Option aus jeder Kategorie:

- **Rolle/Archetyp:**
  1. Herrscher/Adlige
  2. Gelehrter/Erfinder
  3. Krieger/Soldat
  4. Gauner/Schmuggler
  5. Mystiker/Priester
  6. Bürgerlich/Alltagsmensch

- **Persönlichkeit:**
  1. stoisch und ehrenhaft
  2. exzentrisch und vergesslich
  3. listig und verschlagen
  4. herzlich und naiv
  5. fanatisch und unbarmherzig
  6. weltgewandt und humorvoll

- **Besonderheit/Geheimnis:**
  1. Kennt die Zukunft (behauptet es zumindest - optional über Träume)
  2. Ist selbst ein Zeitreisender incognito
  3. Hat einen unerwarteten Alliierten (z. B. ein zahmes Zeitwesen)
  4. Stammt aus einer alternativen Zeitlinie mit abweichendem Wissen
  5. Trägt ein verbotenes Artefakt bei sich
  6. Steht unter einem Paradoxon-Fluch (z. B. altert rückwärts oder vergisst jede Gegenwart sofort,
     wenn sie vorbei ist)

**Beispiel:** Wir würfeln 2-5-3: _Gelehrter_ - _fanatisch und unbarmherzig_ - _hat einen
unerwarteten Alliierten_. Daraus entsteht vielleicht **Professor Zara**, eine strenge Chrono-
Historikerin aus dem Jahr 1890, die absolut skrupellos versucht, "Zeitfrevel" zu verhindern. Sie ist
unnahbar, mit stechendem Blick, und als Überraschung hat sie einen T-Rex-Klon aus der Zukunft als
Leibwächter (ihr unerwarteter Verbündeter, den sie mit einem Gerät kontrolliert). Was für eine
denkwürdige Begegnung!

Ihr könnt diesen NSC-Generator auch nutzen, um **bekannte historische Figuren mit einem Twist** zu
versehen. Was, wenn Napoleon (Rolle: Herrscher) plötzlich eine schelmische Ader hat (Persönlichkeit:
humorvoll) und insgeheim von einem verlorenen Verwandten in der Zukunft träumt (Besonderheit:
behauptet, geheime Zukunftsquellen zu besitzen)?
Schon wird aus der bekannten Figur ein einzigartiger
Charakter für eure Story!

## Encounter-Pools nach Risikostufe {#encounter-pools}

Jeder Eintrag kann mit `tag:` gekennzeichnet werden. Zulässige Werte sind `combat`, `social` und `hazard`.
Um ohne langes Blättern passende Gegner bereitzustellen, gibt es vier Tabellen nach
Risikostufe. Ein W6-Wurf bestimmt den Pool, ein optionales Twist-Deck liefert
zusätzliche Komplikationen. Jeder gezogene Eintrag geht anschließend für drei
Sitzungen in **Cooldown** und wird erst danach wieder in den Pool gemischt.

| Stufe  | Beispiel-Gegner               | Twist                          |
| ------ | ----------------------------- | ------------------------------ |
| **S**  | 2-3 einfache Wachposten       | Kurze Ablenkung lenkt sie ab   |
| **M**  | Sicherheitsteam mit Spürhund  | Gelände bietet Deckung (-1 SG) |
| **L**  | Elite-Söldner samt Drohne     | Verstärkung nach 2 Runden      |
| **XL** | Paramilitär und leichter Mech | Zeitriss droht aufzubrechen    |

Die Twist-Karten können auf laminierten Karten notiert werden - ein schneller
Zug reicht, um jedem Encounter eine überraschende Wendung zu verleihen.

### Encounter-Pool-Listen (d6 je Stufe) {#encounter-pool-listen}

- epoch: "modern"
  type: "security"
  tag: combat
  risk: "S"
  text: "Patrouillen-Duo (Ortspolizei, schlecht ausgerüstet)"
- epoch: "modern"
  type: "civilian"
  tag: social
  risk: "S"
  text: "Zivile Zeugen (Neugierige Arbeiter, wollen helfen)"
- epoch: "modern"
  type: "animal"
  risk: "S"
  text: "Wachhund + Besitzer (ablenkbar mit Futter)"
- epoch: "modern"
  type: "misc"
  risk: "S"
  text: "Nostalgiker-Touristen mit Kameradrohne"
- epoch: "modern"
  type: "hazard"
  tag: hazard
  risk: "S"
  text: "Elektrischer Kurzschluss - Funken + Rauch, kein Feuer"
- epoch: "modern"
  type: "security"
  risk: "S"
  text: "Kontrollposten mit veralteter Schlüsselkarte (Zugriffs-Bonus)"

- epoch: "modern"
  type: "security"
  risk: "M"
  text: "4-Mann-Sicherheitstrupp (MP5, Bodycams)"
- epoch: "modern"
  type: "drone"
  risk: "M"
  text: "Drohnenschwarm (3× Quadcopter, IR-Sensor)"
- epoch: "modern"
  type: "tech"
  risk: "M"
  text: "Code-Lock mit Timelock-Sicherung (2 Min. Cool-down)"
- epoch: "modern"
  type: "alarm"
  risk: "M"
  text: "Zeitversetztes Alarmsystem (20 Sek. Latenz, manipulierbar)"
- epoch: "modern"
  type: "civilian"
  tag: social
  risk: "M"
  text: "Zivilist + Geiselsituation (moralisches Dilemma)"
- epoch: "modern"
  type: "tech"
  risk: "M"
  text: "Techniker-Team führt Systemwartung durch (bestechlich)"

- epoch: "modern"
  type: "military"
  risk: "L"
  text: "Elite-Söldnertrupp (6 Personen, Panzerplatten, Sturmgewehre)"
- epoch: "modern"
  type: "hazard"
  tag: hazard
  risk: "L"
  text: "EMP-Mikroladung in nervöser Hand - Finger am Abzug"
- epoch: "modern"
  type: "tech"
  risk: "L"
  text: "Laser-Rasterfeld, automatisch vernetzt mit Geschütznest"
- epoch: "modern"
  type: "psi"
  risk: "L"
  text: "Psi-Sensitive Wache (Telepath I, spürt feindliche Absicht)"
- epoch: "modern"
  type: "explosive"
  risk: "L"
  text: "Countdown-Sprengsatz (3 Min. bis Detonation)"
- epoch: "modern"
  type: "agents"
  risk: "L"
  text: "\u201EBlack Bag\u201C-Team (Agenten derselben Fraktion -1 Px bei Konflikt)"

- epoch: "future"
  type: "anomaly"
  risk: "XL"
  text: "Schwerkraftanomalie (lokaler 0-G-Kern, gefährdet Infrastruktur)"
- epoch: "future"
  type: "mech"
  risk: "XL"
  text: "Hunter-Killer-Mech (Höhe 3 m, Gatling + Raketen)"
- epoch: "future"
  type: "rift"
  risk: "XL"
  text: "Zeitschleifen-Riss - 30-Sek-Loop, verursacht Px -2 pro Minute"
- epoch: "future"
  type: "nanite"
  risk: "XL"
  text: "Naniteschwarm (Korrosion jeder Elektronik, immun gegen Systemzugriff)"
- epoch: "future"
  type: "boss"
  risk: "XL"
  text: "Gegenspieler-Ass im Feld (Signatur-NSC mit Plot-Immunität)"
- epoch: "future"
  type: "orbital"
  risk: "XL"
  text: "Orbitale Aufklärungsplattform visiert Gebiet an (Laser Spot - Sat-Strike in 90 Sek.)"
- epoch: "1897"
  type: "security"
  risk: "M"
  text: "Osmanische Geheimpolizei: Patrouillen, Mauser C96. Verstärkung ab Heat 3. +1 Gegner je sichtbare Psi-Nutzung"
- epoch: "820"
  type: "security"
  risk: "S"
  text: "Drei unerfahrene Dorfbewacher patrouillieren mit Speeren an der Palisade. Alarmiert das Dorf und flieht."
- epoch: "910"
  type: "hazard"
  tag: hazard
  risk: "M"
  text: "Sechs verarmte Banditen blockieren den Waldweg, fordern Wegezoll. Ziehen sich bei erstem Verletzten zurück."
- epoch: "975"
  type: "civilian"
  tag: social
  risk: "S"
  text: "Wandernder Benediktiner mit kostbaren Pergamenten; braucht Geleitschutz. Liefert Informationen gegen Schutz."
- epoch: "2082"
  type: "drone"
  risk: "S"
  text: "Schwarm aus acht Minidrohnen überwacht Industriepark. Koordiniert, löst Alarm aus und holt Verstärkung."
- epoch: "2085"
  type: "security"
  risk: "M"
  text: "Autonomer Roboter mit Wasserkanone und Blendgranaten sichert Straßensperre. Reagiert auf Funk-Spoofing."
- epoch: "2090"
  type: "civilian"
  tag: social
  risk: "S"
  text: "Zwei Off-Grid-Tech-Nomaden plündern eine Baustelle nach Ersatzteilen. Verhandeln, greifen nur bei Gefahr."

## Encounter-Paket "Postorbitales Zeitalter" {#postorbital-encounters}

Diese Gegnerprofile erweitern den späten Zeitraum. Alle Werte folgen dem W6-System.

### 1 · Orbital-Wachdrohne - Sentry-Klasse

| Merkmal       | Wert                                     | Notizen                       |
| ------------- | ---------------------------------------- | ----------------------------- |
| **Typ**       | Drohne (S)                               | unbemannt, KI-gestützt        |
| **Speed**     | 8/16 (Flug)                              | Schwebe-Impulsoren            |
| **Panzerung** | Titanfaser 3                             | <2 ignoriert, 3-4 halbiert    |
| **Sensor**    | 60 m 360° LIDAR                          | Tarnwürfe -2                  |
| **Waffen**    | Plasmapuls 2W6 (Explode), Betäubung      | Reichweite 20 m               |
| **Systeme**   | Autorepair 1 LP/Runde                    | deaktiv bei EMP               |
| **Trigger**   | Selbstzerstörung bei ≤ 1 LP (1W6, R=3 m) | historisch → Timeline-Echo + Fraktionsnotiz |
| **Rolle**     | Patrouille, Alarmmultiplikator           | verdoppelt "Gefahr im Anflug" |

### 2 · Konzern-Psychiker - Stufe B (Elite)

| Attribut   | Wert | Fertigkeiten                                | Ausrüstung          |
| ---------- | ---- | ------------------------------------------- | ------------------- |
| Körper 3   | -    | Pistolen 3, Nahkampf 2                      | Nanofaser-Suit SR 2 |
| Geist 4    | -    | Telepathische Überwältigung 4, Precog-Dodge | Plasmapistole 1W6+1 |
| Psi-Kern 5 | -    | **Spezial:** Psi-Spike (2 PP, CD 2)         | Mind-Screen (-2)    |
| Stress 12  | -    | kämpft bis LP ≤ -4 (Corporate Loyalty)      | -                   |

### 3 · Zeit-Operative - Stufe A (Transhuman)

| Attribut   | Wert | Fertigkeiten                 | Gear              |
| ---------- | ---- | ---------------------------- | ----------------- |
| Körper 2   | -    | Infowar 5, Athletik 2        | Inline-Chrono-Tap |
| Tech 5     | -    | Chrono-Exploit 5, Sabotage 3 | Smart-Gloves (+2) |
| Psi-Rest 2 | -    | **Spezial:** Timing-Gefühl   | -                 |
| Stress 10  | -    | LP 8                         |                   |

_Chrono-Exploit:_ 1 PP, friert Zielgerät 1 Runde ein oder erzeugt Heat +1 bei Erfolg ≥ 2.
_Timing-Gefühl:_ Du spürst, wann eine Routine bricht - Türzyklen, Patrouillen, Blickrichtungen.
Mechanik: 1× pro Szene bekommst du +2 auf eine Probe, die Timing betrifft (Schleichen durch Sichtfenster,
an Wache vorbei, in einen Raumwechsel). Bei Erfolg: du darfst eine Konsequenzstufe (Lärm/Alarm)
um 1 reduzieren.

### Bonus-Micro-Begegnungen (d13)

1-2 Orbital-Wartungs-Mecha blockieren Zugänge.
3-4 Schwarzmarktschmuggler im Grav-Van.
5-6 Exo-Suit-Salvager durchsuchen Wracks.
7-8 Konzern-San-Team birgt Verwundete.
9-10 Nano-Schwarm breitet sich in Lüftungen aus.
11 Defekte Umwelt-KI erzeugt Fehlalarme.
12 Mini-Rift-Ausläufer verursacht kurzzeitige Anomalien.
13 Anti-Psi-Labor mit isolierten Zellen und Wachen (Psi-Effekte +2 SG)

_Balancing:_ Bei kleinen Teams genügen Drohne **oder** Psychiker. LP und Stress dürfen ±20 % variieren.

## Encounter-Paket "Asien im Kalten Krieg" {#asia-coldwar}

Kurze Begegnungen, inspiriert von Spionagekrimis der 1960er Jahre.

### 1 · Grenzposten am 38. Breitengrad

| Merkmal | Wert           | Notizen                 |
| ------- | -------------- | ----------------------- |
| **Typ** | Infanterie (S) | Soldaten mit Karabinern |

### 2 · Agentin "Jade"

| Attribut | Wert | Fertigkeiten              | Ausrüstung               |
| -------- | ---- | ------------------------- | ------------------------ |
| Geist 4  | -    | Verkleidung 4, Nahkampf 3 | Mini-Kamera, Giftspritze |

### 3 · Schwarzhändler auf dem Nachtmarkt

| Merkmal | Wert              | Notizen                         |
| ------- | ----------------- | ------------------------------- |
| **Typ** | Kontaktperson (M) | Beschafft Alttech gegen Devisen |

## Encounter-Paket "Orbitalstation 2030+" {#orbital-nearfuture}

Szenarien in einer nahen Zukunft - Forschungsstationen und Weltraumhotels.

### 1 · Wartungstrupp EVA

| Merkmal | Wert          | Notizen                  |
| ------- | ------------- | ------------------------ |
| **Typ** | Techniker (S) | Jetpacks, Reparaturtools |

### 2 · Sicherheitsdrohne

| Merkmal | Wert       | Notizen                 |
| ------- | ---------- | ----------------------- |
| **Typ** | Drohne (M) | Laserpointer 1W6, Alarm |

### 3 · Schmuggler-Pod

| Merkmal | Wert                | Notizen                       |
| ------- | ------------------- | ----------------------------- |
| **Typ** | Transportkapsel (L) | Schleust verbotene Fracht ein |

### Twist-Seeds (d30) {#twist-seeds}

Jeder Eintrag besitzt nun zwei Zusatz-Tags:
`Paradoxon-Stufe` (0-3) zeigt das Risiko für Zeitstörungen,
`Historischer Fußabdruck` beschreibt die Tragweite.

Um zu verhindern, dass der Twist-Pool bei langen Kampagnen leerlauft, wandern
gezogene Einträge auf einen Ablagestapel. Sobald weniger als fünf Karten im Pool
liegen, mischt die SL den Stapel zurück.
| Nr. | Twist | Paradoxon-Stufe | Historischer Fußabdruck |
|----|-------|---------------|-------------------------|
| 1 | Doppelagent im eigenen Team enttarnt sich in der Klimax. | 2 | mittel |
| 2 | Missionsziel ist bereits von einer dritten Fraktion entwendet worden. | 1 | klein |
| 3 | Zeitreisende Version des Auftraggebers sendet widersprüchliche Befehle. | 2 | mittel |
| 4 | Schlüsselfigur entpuppt sich als entfernte Verwandte eines Teammitglieds. | 1 | klein |
| 5 | Artefakt ist lebendig - schwache Bio-Signale, reagiert auf Stress. | 2 | mittel |
| 6 | Geisel möchte nicht gerettet werden, verfolgt eigene Agenda. | 0 | klein |
| 7 | Feindliche KI bietet Allianz gegen ihren Schöpfer an. | 1 | mittel |
| 8 | Historisches Ereignis findet eine Szene früher statt als erwartet. | 1 | mittel |
| 9 | Transportmittel sabotiert - Not-Sprung oder Impro-Flucht nötig. | 1 | klein |
| 10 | Lokaler Widerstand verlangt Gegenleistung, bevor er hilft. | 1 | klein |
| 11 | Wetterphänomen erschwert den Einsatz erheblich. | 1 | klein |
| 12 | Gegner besitzt Teilwissen über Zeitreisetech und nutzt es taktisch. | 2 | mittel |
| 13 | Beweisstücke lösen akute Paradoxon-Spitzen aus. | 3 | groß |
| 14 | Einsatzort wird zum Sperrgebiet erklärt. | 1 | klein |
| 15 | Verborgene Psi-Barriere dämpft Teamfähigkeiten. | 2 | mittel |
| 16 | Medienleak - Reporter streamt live. | 2 | mittel |
| 17 | Vergessene Nebenfigur fordert Bezahlung ein. | 1 | klein |
| 18 | Missionsziel wird plötzlich hochansteckend. | 2 | mittel |
| 19 | Ausrüstung beginnt zu altern - jede Stunde 10 % Ausfallchance. | 2 | mittel |
| 20 | "Alles war Ablenkung": Primärer Antagonist greift HQ simultan an. | 3 | groß |
| 21 | Kalter-Krieg-Agent verlangt Austausch gefangener Wissenschaftler. | 1 | klein |
| 22 | Spionageausrüstung enthält heimlichen Sender. | 1 | klein |
| 23 | Verbündeter entpuppt sich als Zukunfts-Double des Rivalen. | 2 | mittel |
| 24 | Funksprüche verweisen auf zweite Zielperson mit eigenem Agenda. | 1 | klein |
| 25 | Zeitanomalie katapultiert Schlüssel-NPC kurzzeitig in Parallelwelt. | 2 | mittel |
| 26 | Team entdeckt verdeckte Waffenlieferung an beide Parteien. | 2 | mittel |
| 27 | Waffentest verursacht EMP, der Equipment lahmlegt. | 1 | mittel |
| 28 | Schwarze Liste eines Geheimdienstes taucht auf - Team steht darauf. | 1 | mittel |
| 29 | Politischer Abgrund: lokale Fraktion plant Putsch während der Mission. | 2 | groß |
| 30 | Rücksprung löst Resonanz aus - Gegner erhält Vorwissen über Actions. | 2 | mittel |
| 31 | Vertrauter NSC gerät unter Einfluss temporaler Schatten. | 2 | mittel |
| 32 | Kodex-Datenbank zeigt plötzlich kritische Lücken. | 1 | klein |
| 33 | Zielperson entpuppt sich als Zeitspringer. | 2 | mittel |
| 34 | Rivalenteam bietet Hilfe gegen Anteil am Fund. | 1 | mittel |
| 35 | Eine alte Prophezeiung beschreibt exakt diesen Einsatz. | 2 | groß |
| 36 | Sprungfenster instabil - Rückkehrzeit ungewiss. | 2 | mittel |
| 37 | Gegner entführt Agenten aus einer nahen Zukunft. | 3 | groß |
| 38 | Kameras zeigen Aufnahmen aus kommenden Szenen. | 2 | mittel |
| 39 | Vergrabene Zeitkapsel liefert brisante Gegenbeweise. | 1 | klein |
| 40 | Explosion erzeugt lokale Zeitschleifen. | 3 | groß |
| 41 | Parallel Orders - konkurrierendes Team erhält identische Befehle. | 1 | mittel |
| 42 | Cold Swap - Artefakt stammt aus Parallel-Cluster, HQ fordert Nachverhandlung. | 1 | mittel |
| 43 | Alarm-Transmitter sendet Signal-Broadcast und warnt Gegner vor dem Team - Stealth +2 SG. | 0 | klein |
| 44 | Delayed Cipher datiert 30 Jahre zu spät - Rätsel PZ-2.5, Heat +1 bei Fail. | 1 | klein |
| 45 | Black Budget - unbekannte Geldgeber mischen sich ein, Shadow-Team optional. | 2 | mittel |
| 46 | Automata sabotieren Bosporus-Telegrafen - Flottenabkommen in Gefahr. | 2 | mittel |
| 47 | Verlorenes Pharaonengrab - Bauplan einer frühen Dampfmaschine sabotiert römische Versorgung. | 2 | mittel |
| 48 | Kreuzzugs-Doppelagent lenkt Armee nach Enttarnung 50 km vom Kurs ab. | 2 | mittel |
| 49 | Gefälschte Seekarten verschieben Columbus' Landung um Monate. | 1 | mittel |
| 50 | Großer Stadtbrand: Saboteur verhindert Archivverlust. | 2 | groß |
| 51 | Geheime Druckerpresse verbreitet radikale anarchistische Ideen. | 1 | mittel |
| 52 | Hydrogen-Dirigible-Prototyp wird Sabotageziel der Chrononauten. | 2 | mittel |
| 53 | Verdeckte Telegraphenlinie ändert preußische Kriegsplanung. | 2 | mittel |
| 54 | Edison-Sabotage verschiebt Marktführung durch gestohlene Glühfäden. | 2 | mittel |
| 55 | Gedruckte Tarn-Zeitung führt zu Meuterei, Front bricht 48 h früher. | 2 | groß |
| 56 | Aktien-Algorithmus verhindert Börsencrash, Industrie boomt. | 1 | mittel |
| 57 | Geisterarmee-Lichtbilder ziehen feindliche Reserven ab. | 2 | mittel |
| 58 | Mondlandung-Leak zwingt vorgezogene Apollo-Mission, scheitert fast. | 2 | mittel |
| 59 | Quantenbug im Siegelprotokoll deckt Schattenzugang auf. | 2 | mittel |
| 60 | Gefälschte Sonnensturmprognose erzwingt globale Evakuierungsproben. | 2 | groß |
| 61 | Asteroid-Bergbau-Kartell zettelt Aufstand auf Raumstation an. | 2 | groß |
| 62 | Terraform-Sabotage durch Mikro-Dronen löst ökologische Reset-Schleife aus. | 3 | groß |

_Gewichtungstipp:_ Bei Missionen im Kalten Krieg können die Einträge 21-30 mit
erhöhter Wahrscheinlichkeit gezogen werden (z.B. doppelte Gewichtung), um die
Zeitperiode stärker zu betonen.

### Lore-Seed Pool (d12) {#lore-seed-pool}

| W12 | Seed                                         | Tag      |
| --- | -------------------------------------------- | -------- |
| 1   | Hafenarbeiter streiken; Zugang blockiert.    | social   |
| 2   | Untergrundkult plant Ritual - Opfer droht.   | social   |
| 3   | Flutwelle nähert sich, Evakuierung nötig.    | physical |
| 4   | Adelshof spinnt Intrige gegen Auftraggeber.  | social   |
| 5   | Erdrutsch verschüttet Zugangsstraße.         | physical |
| 6   | Bürgeraufstand eskaliert vor Ort.            | social   |
| 7   | Giftgasleck in Fabrik erzwingt Schutzmasken. | physical |
| 8   | Geiseltausch unter Medienaugen.              | social   |
| 9   | Orkan legt Kommunikationslinien lahm.        | physical |
| 10  | Saboteure legen Feuer im Lagerhaus.          | physical |
| 11  | Pilgerprozession blockiert die Route.        | social   |
| 12  | Korruptes Wachteam verlangt Bestechung.      | social   |

### Kurzereignisse (d6) {#kurzereignisse}

Spontane Zwischenfälle lockern eine Mission auf. Würfle 1W6 oder nutze das
Kurzschema `rand_event`.

| W6  | Zwischenfall                                                                                                  |
| --- | ------------------------------------------------------------------------------------------------------------- |
| 1   | **Funkstörung** - Für 1 Szene kein Team- oder Kodexkontakt. Nur Sichtzeichen oder direkte Verbindung möglich. |
| 2   | **Technik-Glitch** - Gadget spinnt, z. B. leeres Scanfenster. _Per Freihandlung behebar._                     |
| 3   | **Wetter kippt** - Plötzlicher Regen, Nebel, Schneefall oder Sand treibt Sicht -1, "Heimlichkeit" +1.         |
| 4   | **Zivilkontakt** - Unbeteiligter (Kind, Hausmeister, Bote…) kommt ins Bild. Klärt sich nicht sofort.          |
| 5   | **Spur auftaucht** - Mikrofilm, USB oder Hülse liegt offen sichtbar. Wer greift zuerst zu?                    |
| 6   | **Feindaktivität in Sichtweite** - Sicherungsteam oder Drohne wird früh entdeckt. Vorstoß oder Ausweichen?    |

```text
Funktion rand_event:
1) Lege eine Liste mit 6 Zwischenfällen an.
2) Würfle 1W6 oder ziehe einen gleichverteilten Zufallsindex.
3) Gib den passenden Eintrag als Klartext aus.
```

## Kreaturen- & Gestalten-Generator: Begegnungen der ungewöhnlichen Art {#kreaturen-generator}

Nicht nur menschliche NSCs kreuzen den Weg der Chrononauten.
Öffnet sich ein Rift, spawnt es ein Wesen, das zur laufenden Epoche passt.
Rifts in Zukunftsmissionen werfen hingegen die hier gelisteten **Paramonster** aus -
reine Zeitkonstrukte mit genau einem Zeiteffekt.

Würfelt oder wählt eine Kreatur und verwendet den passenden Stat Block.
Jedes Wesen trägt einen **Schwierigkeitswert** von 💀 bis 💀💀💀💀💀,
der angibt, wie hart es Solo-Agenten im Vergleich zu Gruppen trifft.
Faustregel: Pro zusätzlichem Totenkopf sollte das Team mindestens
einen weiteren Agenten oder starke Ausrüstung aufbieten.
Die Totenkopf-Skala ist unabhängig von den Stundengläsern der
Rift-Missionen und erhöht **nicht** den SG.

1. **Zeitschimäre** - Verschmolzene Tiere und Maschinen aus mehreren Epochen.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Zeitschimäre                         │
│ Rift-Tier: Standard Rift                   │
│ LP-Pool: W6 × 2 (Exploding)                │
│ Defense-Schwelle: 5                        │
│ Difficulty: 💀💀💀                           │
│ Signature Power: Time-Skip Blink           │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Survival 13          │
│ Tells: Flimmernde Körperteile, wildes Fauchen│
│ CU-Bonus: Spielerlevel × 10                │
╰────────────────────────────────────────────╯
```

Greift alles an, bis der Riss geschlossen ist.

2. **Zeitwächter-Golem** - Chronotechnischer Wächter in alten Tempeln.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Zeitwächter-Golem                    │
│ Rift-Tier: Standard Rift                   │
│ LP-Pool: W6 × 2 (Exploding)                │
│ Defense-Schwelle: 5                        │
│ Difficulty: 💀💀💀                           │
│ Signature Power: Stasis Wall               │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Lore 14              │
│ Tells: Grollendes Steinechos, leuchtende Glyphen │
│ CU-Bonus: Spielerlevel × 10                │
╰────────────────────────────────────────────╯
```

Fällt in Schlaf, wenn sein Ritualstein deaktiviert wird.

3. **Chronogeist** - Verlorene Seele zwischen den Zeiten.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Chronogeist                          │
│ Rift-Tier: Minor Rift                      │
│ LP-Pool: W6 × 1 (Exploding)                │
│ Defense-Schwelle: 4                        │
│ Difficulty: 💀💀                            │
│ Signature Power: Loop Feedback                 │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Empathy 12           │
│ Tells: Flackernde Silhouette, kaltes Flüstern │
│ CU-Bonus: Spielerlevel × 10                │
╰────────────────────────────────────────────╯
```

Kann erlöst oder endgültig gebannt werden.

4. **Mechanischer Zeitläufer** - Kleines Uhrwerk-Wesen mit eigener Agenda.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Mechanischer Zeitläufer              │
│ Rift-Tier: Minor Rift                      │
│ LP-Pool: W6 × 1 (Exploding)                │
│ Defense-Schwelle: 4                        │
│ Difficulty: 💀💀                            │
│ Signature Power: Reverse Flow              │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Tech 12              │
│ Tells: Surren von Zahnrädern, schnelle Sprünge │
│ CU-Bonus: Spielerlevel × 10                │
╰────────────────────────────────────────────╯
```

Wird schlauer, je länger er unbehelligt bleibt.

5. **Dämon der Zeitschlucht** - Manifestierte Zeitlinie in monströser Form.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Dämon der Zeitschlucht               │
│ Rift-Tier: Major Rift                      │
│ LP-Pool: W6 × 3 (Exploding)                │
│ Defense-Schwelle: 6                        │
│ Difficulty: 💀💀💀💀💀                         │
│ Signature Power: Age-Burn Touch            │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Charisma 16          │
│ Tells: Schwarzer Nebel, verzerrte Realität │
│ CU-Bonus: Spielerlevel × 10                │
╰────────────────────────────────────────────╯
```

Nur mehrere Zeitanker können ihn bannen.

6. **Zeit-Egel** - Parasitärer Räuber, der temporale Energie saugt.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Zeit-Egel                            │
│ Rift-Tier: Minor Rift                      │
│ LP-Pool: W6 × 1 (Exploding)                │
│ Defense-Schwelle: 4                        │
│ Difficulty: 💀💀                            │
│ Signature Power: Time-Slow Bubble          │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Medicine 12          │
│ Tells: Kurze Zeitsprünge der Opfer, blasser Schleim │
│ CU-Bonus: Spielerlevel × 10                │
╰────────────────────────────────────────────╯
```

Nur sichtbar oder entfernbar mit speziellem Gerät.
Diese Kreaturen (und viele mehr) könnt ihr einbauen, um euren Abenteuern Würze und Mysterium zu
verleihen. Wichtig ist, sie **sparsam und gezielt** einzusetzen - jede besondere Begegnung soll sich
einzigartig anfühlen. Die Spieler dürfen ruhig mal ins Grübeln kommen: "Was zum Henker ist _das_!?"
Und wenn sie dann nach und nach die Hintergrundgeschichte oder Logik dahinter entdecken, wird aus
einem Monster plötzlich ein integraler Teil der Story - vielleicht sogar etwas Mitfühlenswertes oder
Respektgebietendes. Gerade in ZEITRISS, wo Mythologie oft einen zeitphänomenalen Ursprung hat,
können solche Kreaturen dafür sorgen, dass selbst erfahrene Chrononauten nie vergessen: **Die Zeit
birgt unendliche Überraschungen.**

<a id="para-creature-generator"></a>

## Para-Creature-Generator: Rift Casefile Edition {#para-creature-generator}

Der Standard-Generator für echte Para-Kreaturen in Rift-Casefiles.
Er erzwingt den **One-Weird-Thing-Guard**: exakt **ein** Zeitphänomen,
**ein** Anchor (Ort/Person), **drei bis fünf** sichtbare Tells und **eine**
Schwäche.
Keine zweite Anomalie, keine "es war nur Tech"-Auflösung in Rifts;
zusätzliche Technik gehört in den Abschnitt "Urban-Myth-Generator".

### Guard & Struktur

- Nutze `register_anomaly()` nur für das eine Zeitphänomen
  (Echo, Loop, Stutter, Anker-Zeitversatz).
  HUD-Overlay: `MODE RIFT · CASE <ID> · HOOK <Kurzlabel> · WEIRD 1/1`.
- Jede Kreatur bindet einen **Zeitmarker**
  (Echo/Loop/Stutter/Static/Slip/Anchor-Tether).
  Der Marker erklärt, warum das Wesen im Strom sichtbar bleibt.
- Der Anchor ist eine reale Person, ein Ort oder ein Artefakt,
  das als "Zeuge" oder "Bollwerk" fungiert.
  Wird der Anchor befreit/zerstört, löst sich die Anomalie.
- **Tells:** 3-5 wiedererkennbare Signale
  (Geruch, Geräusch, Schatten, Temperatur, EM-Spitzen).
- **Weakness:** eine eindeutige Abschaltbedingung
  (Material, Frequenz, Ritual, spezifisches Werkzeug).
  Ohne Weakness kein Abschluss.

### Schrittfolge

1. **Epoche (W6)**
   - 1 Frühe Neuzeit
   - 2 Industrialisierung
   - 3 Weltkriege
   - 4 Kalter Krieg
   - 5 Digitale Anfänge
   - 6 Near-Future
2. **Zeitmarker (W6)**
   - 1 Echo-Schleife (verzögerte Schatten)
   - 2 Loop 30 Sek.
   - 3 Stutter (Zeitsprünge in Frames)
   - 4 Static (verrauschte Wahrnehmung)
   - 5 Slip (Kreatur fällt kurz aus Phase)
   - 6 Anchor-Tether (Kreatur an einen Zeugen gebunden)
3. **Anchor (W6)**
   - 1 Erstzeuge
   - 2 Tatort mit Einschlag
   - 3 Opfer mit Zeitbrand
   - 4 Artefakt/Container
   - 5 Familienlinie/Blutanker
   - 6 Forschungslog/Blackbox
4. **Tells (3-5 aus W10 wiederholen, keine Duplikate)**
   - 1 Frosthauch
   - 2 verzerrter Funk
   - 3 bläulicher Schleier
   - 4 Geruch nach Ozon/Metall
   - 5 scharfe Schatten gegen die Lichtquelle
   - 6 Tierpanik
   - 7 Uhren laufen rückwärts
   - 8 Audiospur mit Flüstern
   - 9 zweiter Nachhall jeder Bewegung
   - 10 kurzes "Bildflackern" im HUD
5. **Weakness (W6)**
   - 1 bestimmte Frequenz (z. B. 18 Hz Infraschall)
   - 2 geheiligtes Material (Salz/Quecksilber)
   - 3 Anchor neutralisieren (Zeuge befreien, Container öffnen)
   - 4 Zeitsiegel (Ritualkreis + Sensor)
   - 5 Schockfrost/Hitze
   - 6 Psi-Signatur spiegeln (Mind-Wurf gegen Psi-Sig)
6. **Stat-Block**
   - Nach Risikostufe (S/M/L/XL) bauen.
   - Fähigkeitspalette um den Zeitmarker herum bauen
     (Teleport = Stutter, Versteinerung = Static etc.).

### Casefile-Schablone

- **CASE:** `RIFT-<ID> | Epoche | Seed-Tier (low/mid/high)`
- **VISUAL HOOK:** 1 Satz mit Anchor + Zeitmarker
  (`"Echoender Schatten hinter jedem Zeugen"`).
- **BRIEFING PUBLIC (max. 5 Bulletpoints):**
  Witness-Reports, Schauplatz, Gefahrenhinweis.
- **OBJECTIVES:**
  `Secure Anchor`, `Identify Time Marker`, `Neutralize Weakness`,
  optional `Recover Sample`.
- **CASE OVERLAY:**
  HUD-Tag `CASEFILE <ID> · HOOK <Label> · TIME <Marker>` + `WEIRD 1/1` Toast.
- **TRUTH:**
  kurzer Absatz mit Ursache (Para-Kreatur) und
  warum der Zeitmarker aktiv bleibt.
- **LEADS PRIVATE:**
  3 Hinweise mit Würfelbezug (z. B. Investigation 12, Medicine 10, Tech 11)
  und Verknüpfung zum Anchor.
- **BOSS PRIVATE:**
  Mini-Statblock + Zeitfähigkeit (nur **eine** Weirdness).
  Wenn Urban-Myth-Generator genutzt wird, liegt hier die echte Para-Kreatur,
  der Mythos ist nur ein Deckmantel.

### Zwei einsatzbereite Casefiles

**Chrono Butcher - "Blutspur im Nullzeit-Korridor" (Seed-Tier mid)**

- **Epoche/Marker:** 1997, Digitale Anfänge · **Stutter** (Tatort-Sequenzen brechen in Frame-Sprüngen ab).
- **Anchor:** Ermittlungsakte mit blutgetränkter Taschenuhr des ersten Opfers (Zeitbrand hält Stutter offen).
- **Tells:** Blutlachen fließen kurz rückwärts, Funksprüche knacken mit Opferstimme, Schatten reißen versetzt.
- **Weakness:** Anchor-Uhr auf 00:13:17 stellen und im Stutter-Fenster zerstören (gleichzeitiger Psi-Impuls Mind 12).
- **Boss Private:** **LP 11 | Armor 1 | STR 6 | GES 8 | INT 6 | TEMP 6** - _Frame Lunge_ (GES-Save SG 12, sonst 3 LP, verursacht Panik), _Cut In/Out_ (1/Rd teleportiert zwischen zwei Zeitschatten, erhält +2 auf nächsten Angriff).

**Jersey Devil - "Flügelschlag im Pine Barren" (Seed-Tier low)**

- **Epoche/Marker:** 1909, Industrialisierung · **Loop** (30-Sek-Flugbahn wiederholt sich an Bäumen).
- **Anchor:** Verkohlte Überreste der "13th Child"-Legende in einer Wurzelhöhle (Familienfluch hält Loop stabil).
- **Tells:** Schwefelgeruch, schreiender Wind, Kratzspuren spiralförmig, Tiere fliehen den Pfad.
- **Weakness:** Anchor-Knochen mit geweihtem Kupferdraht fesseln und verbrennen (Survival 11 oder Tech 11, dann Loop kollabiert).
- **Boss Private:** **LP 8 | Armor 1 | STR 6 | GES 8 | INT 4 | TEMP 4** – _Dive Bomb_ (GES-Save SG 11, sonst 2 LP), _Loop Reset_ (setzt Initiative zurück, wenn Anchor unberührt).

<a id="urban-myth-generator"></a>

## Urban-Myth-Generator (False Lead)

Backup für Technik- oder Coverstory-Falschspuren in Rifts. Er folgt dem gleichen HUD-Rahmen (MODE/CASE/HOOK) und respektiert den One-Weird-Thing-Guard: die Mythos-Erklärung darf **nicht** zur zweiten Anomalie werden. Sobald klar ist, dass nur Tech/Manipulation dahintersteckt, muss das eigentliche Para-Phänomen aus der Rift-Casefile-Edition sichtbar werden.

### Vorgehen

1. **Epoche (W6)** - identisch zur Rift-Edition.
2. **Urban-Myth-Motiv (W20)** - nutzt Hardware/Linsen statt Lichtbilder.
3. **Zeitmarker setzen** (Echo/Loop/Stutter etc.), um den "Riss" sichtbar zu halten, und bei echter Weirdness `register_anomaly()` loggen.
4. **Stat-Block** nach Risiko; alles Technische als Shadow-Op erklären (keine VR-Illusionen, nur Sensorik/Implantate).

```markdown
01 Kopfloser Reiter - Drohne mit Linse-Spot (kein Projektor)
02 Schwarzer Hund - Chem-Mod-Kampf­organismus
03 Mothman - Stealth-Fallschirmspringer im Testanzug
04 Schattenleute - Psi-induzierte Schlafparalyse
05 Rote Hexe - Nano-Feuer-Aerosol erzeugt "Flammen"
06 Men in Black - Regierungsabteilung nutzt Neural-Wipe
07 Weeping Woman - Audio-Drohne mit Lament-Frequenz
08 Phantom-Zug - Magnetschwebetest, Zeit ➙ Verwerfung (HUD-Echo)
09 Kinder mit schwarzen Augen - Gen-Versuch / Linsenimplantat
10 Kraken im Kanal - Sewer-Drohne mit Tentakel-Manipulatoren
11 Crying Boy Painting - Quantenspeicher im Pigment (Archivkammer)
12 Goatman - Bio-Chimäre entlaufenem Labor
13 Greys - posthumane Fernzukunfts-Menschen (jenseits T-/N-Stufe), oft Einsatzteams externer Zeitmanipulator-Fraktionen
14 Hitchhiking Ghost - Zeitversetzte Linse-Aufnahme auf HUD
15 Lake-Monster - Schwarm-U-Drohnen unter Hüllfeld
16 Shapeshifter - adaptive Metamaterial-Suit
17 Spukhaus - Übersprungener EM-Emitter + Paradoxon-Energie
18 Schlankes Wesen - Lidar-Verzerrer + Knochenverlängerungen
19 Straßenlaternen-Summen - HF-Psi-Störsender, löst Migräne aus
20 Blutfarbenes Mondlicht - Orbitale Linse fokussiert IR-Spektrum
```

> Reminder: Urban-Myth-Seeds sind **Falschspuren**. Wenn die SL sie ausspielt, muss klar bleiben, dass der eigentliche Rift-Hook eine Para-Kreatur mit genau **einer** Weirdness enthält. Sobald Anchor/Marker neutralisiert sind, schließt der Seed.

### Stat-Block-Schablone

Die Attributwerte der Kreatur sind **feste Werte** und nutzen dasselbe System
wie Spielercharaktere: `1W6 + ⌊Attr/2⌋`. Die SL würfelt für die Kreatur oder
nutzt den Wert als SG für Spielerproben (z.B. Ausweichen gegen Kreatur-Agi).

| Gefahr | **STR** | **GES** | **INT** | **TEMP** | **Armor** | **LP** | Specials       |
| ------ | ------: | ------: | ------: | -------: | --------- | -----: | -------------- |
| **S**  |       4 |       6 |       4 |        2 | 0         |      6 | 1 Fähigkeit    |
| **M**  |       6 |       8 |       6 |        4 | 1         |      8 | 2 Fähigkeiten  |
| **L**  |       8 |      10 |       6 |        6 | 2         |     10 | 3 Fähigkeiten  |
| **XL** |      10 |      12 |       8 |        8 | 3         |     14 | 4+ Fähigkeiten |

> **Armor** reduziert Schaden pro Treffer.
> **LP** ist die Wundschwelle (W = 3 LP).
> **TEMP** wird gegen Psi-Detection oder Paradoxon-Interaktion genutzt.

### Einsatz-Tips

1. **Epochale Einbettung:** Passe die Technologie-Coverstory an Ort und Jahr an.
2. **Paradoxon-Ventile:** XL-Kreaturen sollten eine Mechanik besitzen, die direkt mit dem Paradoxon-Index interagiert.
3. **Cinematic Hooks:** Gib der Kreatur ein ikonisches Geräusch oder Lichtsignal, das Spieler früh wahrnehmen.
4. **Salvage-Rewards:** Nach Besiegung 1-2 modulare Tech-Fragmente als Plot-Coupon oder Craft-Teil.

### Gegenwehr & Makros {#counterfire}

- **Standard-Opener-Volley:** Gegner eröffnen idealerweise, erzwingen Deckung/Stress und setzen
  Druck, _sofern_ sie nicht bereits durch Infiltration, Überraschung oder gezielte Stunts
  ausgeschaltet sind. Initiative-Skills und präzise Alpha-Strikes dürfen den Opener kippen.
- **Gegenwehr pro Szene als Default:** Nach Spielenden-Aktionen prüft die Runde, ob ein
  `counter_move()` sinnvoll ist (Schützen verlagern Feuer, Bosse zünden ein Gadget, Fahrzeuge
  sperren Wege). Reaktionen entfallen, wenn Gegner handlungsunfähig, überrascht oder klar
  unterlegen sind; Skills und Stunts, die Reaktionen verhindern, bleiben voll wirksam.
- **Makros (Pseudo):**

```pseudo
opener_volley(): Ansage "Gegner eröffnen Feuer" → Deckung/Stress würfeln lassen.
suppression_fire(): blockiert Route oder zwingt Nachladen/Umweg (-1 Agi, +1 Stress bei Versagen).
counter_move(): Spezialfähigkeit oder Positionswechsel, der Druck erhöht (Timer, Verstärkung, Jammer).
```

- **Boss-Zyklus:** Boss-Szenen fahren standardmäßig `opener_volley()` → Signatur-Fähigkeit →
  `suppression_fire()` oder Verstärkung, erst dann volle Spieleraktionen - es sei denn, der Boss
  wurde zuvor überrascht oder neutralisiert. Das gilt für Mini- wie Rift-Bosse.

## Boss-Generator: Mini-, Episoden- und Rift-Bosse {#boss-generator}

Erzeugt skalierte Gegner je nach Missionsphase. Mini-Bosse treten in Core-Mission 5 auf,
Episoden-Bosse in Mission 10. Rift-Bosse erscheinen in Szene 10 einer Rift-Op.

**Endzustand-Policy (filmisch):**

- Core-Mini-/Episodenbosse gelten bei **0 LP** als besiegt, schwer verletzt und
  festsetzbar (standardmäßig ITI-Gewahrsam statt sofortigem Tod).
- Tod bleibt Ausnahme für klar ausgespielte Schlüsselmomente.

### boss_template

```yaml
boss_template:
  id: string
  type: miniboss | boss
  arc_type: core | rift
  epoch: "-52 v.Chr."
  archetype: "Zenturio"
  faction: "Lokale Prätorianergarde"
  time_faction: "Rotes Oktagon"
  sg: 9-15
  hp: 12-24
  dr: 2-3
  gear:
    melee: null
    ranged: null
    armor: null
    special: null
  abilities:
    - name: string
      trigger: string
      effect: string
  chrono_trick: null
  loot:
    cu: 40
    relic: null
    tier2:
      - item: Adrenalin-Shot
        cu: 60
      - item: Lichtbild-Köder
        cu: 90
      - item: Nano-Bindepflaster
        cu: 70
```

**Schadensdämpfer:** `dr` steht für die verpflichtende Boss-Schadensreduktion.
Der Wert richtet sich nach der Teamgröße (1-2 → Mini DR 1 / Arc/Rift DR 2,
3-4 → 2/3, 5 → 3/4). Das Toolkit setzt den Wert beim Spawn automatisch und
loggt ihn im HUD.

### core_mini_pool

```yaml
-52: ["Zenturio", "Gallischer Tribun"]
1410: ["Deutsch Ordens-Ritter", "Litauischer Hetman"]
1880: ["Pinkerton-Scharfschütze", "Meiji-Shinsengumi"]
1977: ["KGB-Spionschmuggler", "RAF-Zellenchef"]
2025: ["GSG9-Truppführer", "Triaden-Taktiker"]
```

### core_arc_boss_pool

```yaml
Rotes_Oktagon:
  name: "Magister Aurelio"
  sg: 13
  hp: 20
  chrono: "Micro-Jump (1×/Szene)"
Schattenkonzerne:
  name: "NEXA-Phaeton Direktorin"
  sg: 14
  hp: 22
  chrono: "Echo-Shield (1 Treffer)"
Alter_Orden:
  name: "Prior der Gläsernen Loge"
  sg: 12
  hp: 18
  chrono: null
```

**Drucktypen (Rotation):**

- Schwindende Deckung - Scheinwerfer fährt Schleife, Deckung schmilzt.
- Wanderndes Sichtfenster - Laserlinien öffnen und schließen Zugänge.
- Ressourcen-Clamp - SYS-Slots blockiert, SG +1 für Tech-Checks.

### rift_boss_pool

Rift-Bosse nutzen den Para-Creature-Generator und die Regeln aus `massenkonflikte.md`.

### Quick-Macro

```pseudo
function generate_boss(type, mission_number, epoch):
    if type == "core":
        if mission_number % 10 == 0:
            return draw_unique(core_arc_boss_pool, core_arc_cd)
        elif mission_number % 5 == 0 and mission_number >= 5:
            return draw_unique(core_mini_pool[epoch], core_mini_cd[epoch])
    else:
        if mission_number % 10 == 0:
            return draw_unique(rift_boss_pool, rift_boss_cd)
    return null

function draw_unique(pool, cooldown):
    random.shuffle(pool)
    boss = pool.pop()
    cooldown.append(boss)
    if not pool:
        pool, cooldown = cooldown, []
    return boss
```

IDs wandern nach dem Ziehen auf eine Cooldown-Liste. Ist der Pool leer, wird die Liste
neu gemischt und zurückgesetzt, wodurch Wiederholungen erst nach einem vollständigen Durchlauf
auftreten.

## Artefakt-Generator: Parawesen-Trophies (1W14 + TEMP-Bonus) {#artefakt-generator}

_Alle Artefakte sind **legendary**. Jeder Agent kann nur **ein** aktives Trophäen-Artefakt gleichzeitig führen._

**TEMP-14-Bonus:** Bei TEMP ≥ 14 erhält der Artefaktwurf **+2**. Ergebnisse
von 15-16 erreichen die **Mythic**-Stufe — seltene Artefakte, die über
normalen Legendarys stehen. Der Bonus gilt für den 1W14-Wurf, nicht den Gate-Wurf.

| Wurf | Tier       | Name                        | Effekt                                                                    | Risiko / Cooldown                                   |
| ---: | :--------- | --------------------------- | ------------------------------------------------------------------------- | --------------------------------------------------- |
|    1 | Legendary  | **Mothman-Auge**            | Dauerhaft Nachtsicht 30 m, Wahrnehmung +1                                 | R2: Blend 1 Sz + Timeline-Echo bei Fehlwurf         |
|    2 | Legendary  | **Rift-Skorpion-Stachel**   | +2 DMG & **Doppelschlag 20 %** (Nahkampf)                                 | R4: Selbststich SYS -1 + Heat +1                    |
|    3 | Legendary  | **Heuschrecken-Exo-Platte** | Rüstung +1, 1×/Sz Reflex-Dash 3 m                                         | R3: Bruch → Item weg + Fraktionsnotiz               |
|    4 | Legendary  | **Nullzeit-Larve**          | 1×/Mission Gadget-Reload                                                  | R2: Erwacht Heat +1                                  |
|    5 | Legendary  | **Ektoplasma-Drüse**        | Flächen-Stun, Gegner Ini -2                                               | R2: Leck Stress +1 + Timeline-Echo                  |
|    6 | Legendary  | **Phase-Raptor-Zahnrad**    | 2 Rdn Deckung ignorieren, Nahkampf +1 DMG                                 | R2: Entlädt + Heat +1                               |
|    7 | Legendary  | **Zeitfalter-Kokon**        | 1×/Sz Mini-Sprung ±5 Sek.                                                 | R2: Fehlversatz + Timeline-Echo                     |
|    8 | Legendary  | **Krakenherz-Fragment**     | Bioscan 30 m durch Wände                                                  | R2: Puls Heat +1                                     |
|    9 | Legendary  | **Bernstein-Rabenflügel**   | Lautlos eine Szene & Gleiten 10 m                                         | R3: Feuer zerstört + Fraktionsnotiz                 |
|   10 | Legendary  | **Silberne Lupus-Klaue**    | +1 DMG & **Doppelschlag 15 %**                                            | R2: Blutkontakt Stress +1 + Noise +1                |
|   11 | Legendary  | **Temporaler Knochenzahn**  | SG -2 auf Fossil-Analysen                                                 | R1: Signal-Ping + Noise +1                          |
|   12 | Legendary  | **Mantis-Oculus**           | Fernkampf +1 Hit, Blend-Immun                                             | R2: Fehlschuss Ally Blend + Heat +1                 |
|   13 | Legendary  | **Rift-Spinnenseide**       | 30 m Seil, 1 t, Rüstung ignoriert                                         | R3: Löst sich bei Resonanzspitze, Item verbraucht   |
|   14 | Legendary  | **Doppel-Pupille**          | Angst-Immun & Blend-Frei                                                  | R2: Vision-Flash Stress +1                           |
|   15 | **Mythic** | **Chrono-Herz**             | +1 auf alle Attribute permanent, 1×/Episode Reroll eines beliebigen Wurfs | R3: Herzstillstand 1 Rd (CHA-Save SG 12) + Heat +1  |
|   16 | **Mythic** | **Nullzeit-Auge**           | Sieht 10 Sek in die Zukunft (1×/Mission), alle Proben +2 für 1 Szene      | R4: Zeitblindheit 1 Mission + Timeline-Echo         |

> **Legendary-Limit**: 1 Artefakt | Aktivierung = freie Aktion | Risiko erzeugt Drucksignale (Heat/Stress/Noise/Timeline-Echo), aber keinen Px-Malus.
> **Mythic:** Nur erreichbar mit TEMP ≥ 14 (+2 auf Artefaktwurf). Mythic-Artefakte sind der Endgame-Reward für maximale temporale Affinität.

> **Risk-Level (HUD-Badges):** R1 🟢 Niedrig - Warnhinweis · R2 🟡 Moderat - spürbarer Malus · R3 🟠 Hoch - droht Verlust oder harter Debuff · R4 🔴 Kritisch - massiver Eingriff in Vitalwerte/SYS. Toolkit-Makros wandeln die Kürzel automatisch in Badges.

### Ablauf-Update (Legendary-Roll, runtime-neutral)

```text
Funktion roll_legendary:
1) Gate-Wurf 1W6 durchführen und das Ergebnis im HUD-Check ausgeben.
2) Nur bei Gate = 6 fortfahren; sonst Ende ohne Artefakt.
3) Bei Erfolg 1W14 würfeln. Bei TEMP ≥ 14: +2 auf das Ergebnis.
4) Ergebnis 1-14 = Legendary, 15-16 = Mythic (nur mit TEMP-Bonus erreichbar).
5) Overlay mit Name, Tier, Effekt und Risiko anzeigen.
```

Auslösung wie bisher in **Rift-Mission Szene 11-13**: genau ein
Legendary-Roll pro zulässiger Szene.

Para-Kreaturen dürfen zusätzlich eine Drop-Prüfung über
`generate_para_artifact(current_creature)` auslösen.

### JSON-Lookup (Kodex-HUD)

```json
{
  "artifact_pool_v3": [
    {
      "id": "A01",
      "name": "Mothman-Auge",
      "effect": "NightVision30m; Perception+1",
      "risk": "R2: Flashblind 1Sz; Stress+1 fail"
    },
    {
      "id": "A02",
      "name": "Rift-Skorpion-Stachel",
      "effect": "+2DMG; 20% Double-Strike",
      "risk": "R4: SYS-1 selfhit; Stress+1"
    },
    {
      "id": "A03",
      "name": "Heuschrecken-Exo-Platte",
      "effect": "Armor+1; Reflex-Dash3m 1/Sz",
      "risk": "R3: Break → item lost; Noise+1"
    },
    {
      "id": "A04",
      "name": "Nullzeit-Larve",
      "effect": "Reload all gadgets 1/mission",
      "risk": "R2: Awakens Heat+1; Noise+1"
    },
    {
      "id": "A05",
      "name": "Ektoplasma-Drüse",
      "effect": "AoE stun; Foes Init-2",
      "risk": "R2: Leak Stress+1; Heat+1"
    },
    {
      "id": "A06",
      "name": "Phase-Raptor-Zahnrad",
      "effect": "Ignore cover 2r; +1DMG melee",
      "risk": "R2: Discharge → empty; Cooldown 1Sz"
    },
    {
      "id": "A07",
      "name": "Zeitfalter-Kokon",
      "effect": "Mini-jump ±5s 1/Sz",
      "risk": "R2: Misjump Stress+2"
    },
    {
      "id": "A08",
      "name": "Krakenherz-Fragment",
      "effect": "Bioscan 30m",
      "risk": "R2: Pulse Heat+1; Noise+1"
    },
    {
      "id": "A09",
      "name": "Bernstein-Rabenflügel",
      "effect": "Silent move 1Sz; Glide10m",
      "risk": "R3: Fire destroys; Stress+1"
    },
    {
      "id": "A10",
      "name": "Silberne Lupus-Klaue",
      "effect": "+1DMG; 15% Double-Strike",
      "risk": "R2: Blood Stress+1; Heat+1"
    },
    {
      "id": "A11",
      "name": "Temporaler Knochenzahn",
      "effect": "Fossil scans DC-2",
      "risk": "R1: Ping risk; Noise+1"
    },
    {
      "id": "A12",
      "name": "Mantis-Oculus",
      "effect": "Ranged+1 hit; Flash immune",
      "risk": "R2: Fail → ally flash; Stress+1"
    },
    {
      "id": "A13",
      "name": "Rift-Spinnenseide",
      "effect": "30m rope 1t; bypass armor",
      "risk": "R3: Dissolves at high Stress; Cooldown 2Sz"
    },
    {
      "id": "A14",
      "name": "Doppel-Pupille des Nachtvolks",
      "effect": "Fear & Flash immune",
      "risk": "R2: Vision flash Stress+1; Heat+1"
    }
  ]
}
```

## Para-Artefakt-On-The-Fly (1W6 Körperteil × Buff-Matrix)

|  W6 | Körperteil      | Basiseffekt (vor Matrix) |
| --: | --------------- | ------------------------ |
|   1 | Klaue / Stachel | +2 DMG Nahkampf          |
|   2 | Zahn / Horn     | Durchdringung +1         |
|   3 | Auge / Pupille  | Perception +1            |
|   4 | Drüse / Beutel  | 1× Spezialladung         |
|   5 | Chitin / Platte | Rüstung +1               |
|   6 | Organ / Kern    | Einmaliger Power-Burst   |

> **Matrix-Aufwertung**: Kombiniere mit Kreatur-`type`.
> _Beispiel_ - **Psi-Raptor (M)** rollt **3 = Auge**
> → Grund: _Perception +1_ → Psi-Matrix upgrade: _Telepath-Reichweite ×2_ →
> Größe M = 2 Nutzungen / Mission.

**Risiko:** jeder Fehlschlag ⇒ Heat +1, plus Nebenwirkung laut Tabelle B.

#### Tabelle B - Nebeneffekte (d6)

| d6  | Nebenwirkung                                                  |
| --- | ------------------------------------------------------------- |
| 1   | Stress +1                                                     |
| 2   | Heat +1                                                       |
| 3   | SYS -1 (Selbstschaden)                                        |
| 4   | Blend 1 Szene                                                 |
| 5   | Item defekt; aufwändige HQ-Werkstattreparatur (relativ teuer) |
| 6   | Gegner erhält +1 INI                                          |

> Legendary-Limit: 1 Artefakt / Agent (unverändert).

`Drop-Prüfung: artifact = generate_para_artifact(current_creature)`

## Kulturfragmente-Generator: Farbe für die Epochen {#kulturfragmente}

Wer durch die Zeit reist, trifft auf fremde **Kulturen, Bräuche und Alltagsdetails**, die eine
Epoche erst _authentisch_ machen. Dieser Generator hilft dabei, schnell ein **Kulturfragment**
einzustreuen, das der Szene mehr Tiefe gibt - ideal, wenn Spieler fragen: _"Gibt es hier gerade ein
Fest oder so?"_ oder wenn ihr einfach Atmosphäre schaffen wollt.

Wählt einen Aspekt (oder mehrere), der die aktuelle Epoche prägt:

- **Festliche Anlässe:**
  1. Ein großes Volksfest findet statt (Erntedank, Siegesfeier o. Ä.).
  2. Religiöse Prozession oder ein hoher Feiertag prägt den Tag.
  3. Eine Krönung oder Hochzeit eines Herrschers sorgt für Aufruhr.
  4. Ein Initiationsritus steht bevor (Jugendliche werden in der Gesellschaft als Erwachsene
     anerkannt).
  5. Ein Gedenktag an ein historisches Ereignis findet gerade statt.
  6. Ein spontaner Karneval (oder Aufruhr) tobt auf den Straßen.

- **Sitten und Aberglaube:**
  1. Alle Leute tragen ein bestimmtes Symbol bei sich, um Unglück abzuwehren.
  2. Bestimmte Worte oder Namen werden nie ausgesprochen - sie gelten als Tabu.
  3. Es gibt einen ungewöhnlichen Begrüßungsritus, den Außenstehende seltsam finden.
  4. Ein lokaler Aberglaube bestimmt das Handeln aller (z. B. darf man um Mitternacht **niemals** X
     tun).
  5. An den Straßenecken liegen Opfergaben für unsichtbare Zeitgeister - die Menschen spüren
     instinktiv temporale Unregelmäßigkeiten und versuchen, diese gnädig zu stimmen.
  6. Jeder Fremde muss erst **eine Prüfung** oder Aufgabe erledigen, um akzeptiert zu werden.

- **Mode und Technik-Spleens:**
  1. Eine auffällige Modefarbe dominiert - alle tragen etwas in dieser Farbe (z. B. Rot, zur
     Erinnerung an einen alten Krieg).
  2. Ein Modeaccessoire mit kurioser **Funktion** ist der letzte Schrei (z. B. in einer Steampunk-
     Gesellschaft: ein Monokel, das als kleiner Bildschirm dient).
  3. Die neueste Mode sind kleine **Automaton-Haustiere** - etwa Uhrwerk-Vögelchen an der Leine.
  4. Ungewöhnliche Architektur prägt das Stadtbild (vielleicht sind alle Gebäude aus schwarzem
     Basalt oder vollkommen ohne Ecken gebaut etc.).
  5. Eine lokale Essgewohnheit erstaunt Fremde (etwa werden Speisen zuerst den Ahnen geopfert und
     dann erst gegessen).
  6. Eine spezifische Grußformel oder Redewendung ist allgegenwärtig, mit einer historischen
     Anekdote dahinter ("Möge der Kaiser dir nicht zweimal begegnen" - sprich: man bekommt vom Herrscher
     keine zweite Chance).

- **Gesellschaft & Gesetz:**
  1. Es herrscht strikte **Ausgangssperre** ab einer bestimmten Stunde (vielleicht aus temporalen
     Gründen - man will Geister oder Zeitdiebe fernhalten?).
  2. Ein **Kasten- oder Gildensystem** prägt das Miteinander; Fremde werden automatisch als
     niedrigste Stufe behandelt.
  3. Aktuell gilt **Kriegsrecht** - überall Patrouillen, Ausweiskontrollen und eine angespannte
     Stimmung.
  4. Extrem rigide Ehrvorstellungen: Schon kleinste Beleidigungen werden durch **Duelle auf Leben
     und Tod** gesühnt. (Die Helden müssen höllisch aufpassen, was sie sagen!)
  5. Bizarres Gesetz: Jeder Besucher muss eine Art **"Zeit-Zoll"** entrichten - sei es in Währung
     oder durch eine verrichtete Arbeit. Man glaubt, die Lebenszeit Fremder schulde der Stadt etwas.
  6. **Prophezeiungen oder Astrologie** sind Teil der offiziellen Gesetzgebung. Bestimmte Tage sind
     für gewisse Handlungen verboten, oder ein "Zeit-Orakel" muss wichtige Entscheidungen absegnen.

**Beispiel:** In einer Renaissance-Stadt (Florenz 1500) würfle ich auf _Sitten & Aberglaube_ und
erhalte eine 2: Bestimmte Worte werden nie ausgesprochen. KI-SL interpretiert dies so: _In Florenz
wagt niemand, direkt vom "Teufel" zu sprechen - man umschreibt ihn als "den mit den Hörnern"._ Der
Grund: Man glaubt, Worte beschwören Realität. Die Chrononauten merken das deutlich, als ein NSC
zusammenzuckt, weil einer von ihnen unbekümmert **"diavolo"** gesagt hat. - Schon bekommt ein
einfaches Gespräch sofort eine interessante kulturelle Note!

- **Mandela-Effekte (temporale Rückstände):**

  Subtile Hinweise darauf, dass jemand an der Zeitlinie geschraubt hat. Diese
  Details tauchen beiläufig auf - ein NSC erwähnt etwas, das "falsch" klingt, ein
  Schild zeigt einen Markennamen, den es in der aktuellen Zeitlinie nicht gibt, ein
  Techniker im HQ murmelt über Produkte, die "vor der Korrektur" anders waren. Die
  SL streut diese Momente organisch ein, **ohne sie zu erklären**. Wer aufmerksam
  ist, bemerkt das Muster. Wer lange genug spielt, versteht die Implikation.
  1. Ein HQ-Techniker erwähnt beiläufig ein Produkt, das sich verändert hat
     ("Fruit Loops hieß doch mal Froot Loops - oder war das vor dem
     Casablanca-Job?").
  2. Ein Zeitungsartikel in einer Epoche berichtet über ein Ereignis, das in der
     aktuellen Zeitlinie nie stattgefunden hat.
  3. Ein NSC erinnert sich an den Tod einer berühmten Person - die aber noch lebt.
  4. Ein Markenlogo sieht subtil anders aus als erwartet. Niemand sonst bemerkt es.
  5. Ein Kodex-Archiveintrag referenziert eine Mission, die laut offiziellem Log nie
     existiert hat.
  6. Zwei Chrononauten im HQ streiten sich über ein historisches Detail - beide
     haben "Recht", je nachdem welche Zeitlinie man fragt.

Solche Kulturfragmente lassen die Welt lebendig und eigen wirken. Die Helden merken: **Jede Epoche
hat ihre Eigenheiten**, und wenn sie sich klug darauf einlassen (bzw. KI-SL sie daran erinnert),
können sie so manch unnötigen Konflikt vermeiden oder Sympathien gewinnen. Vielleicht machen sie bei
einem lokalen Fest mit und gewinnen dadurch Verbündete - oder sie nutzen einen Aberglauben gezielt

für sich (_"Wir verkleiden uns als die Ahnengeister, damit sie uns zuhören!"_). Diese kleinen Dinge
fördern das Eintauchen ins Setting enorm und sorgen für großartige Immersion.

## Mood-Snippet-Generator {#mood-snippet-generator}

Ein schneller W6-Wurf erzeugt ein stimmungsvolles Detail für die aktuelle Szene:

1. Straßenlärm oder ferne Rufe
2. Zeittypischer Duft (Gewürze, Rauch, Maschinenöl)
3. Ein kurzer Musikeinspieler oder Marktschreier
4. Auffällige Kleidung oder Uniformen im Blickfeld
5. Ein NPC murmelt ein Sprichwort der Epoche
6. Plötzlicher Wettereffekt (Regen, Hitze, Schneeschauer)

## Rätselbibliothek: Kurze Hürdenszenen {#raetselbibliothek}

Kurze Ideen für Rätsel- oder Hindernisszenen. Die Schwierigkeits-Icons lauten
⌖ für leicht, ✱ für mittel und ⚠ für schwer.

| Nr. | Beschreibung                                                                            | Tag |
| --- | --------------------------------------------------------------------------------------- | --- |
| 1   | Geheimtür über Schallfrequenz öffnen                                                    | ⌖   |
| 2   | Mechanisches Schloss mit rotierendem Zahlenring                                         | ⌖   |
| 3   | Verschlüsseltes Tagebuch in historischem Dialekt                                        | ⚠   |
| 4   | Laserlabyrinth, das nur bei Schatten sichtbar wird                                      | ⚠   |
| 5   | Bildfragment muss wie ein Puzzle zusammengesetzt werden                                 | ⌖   |
| 6   | Mathematischer Code, der Fibonacci-Reihen nutzt                                         | ⚠   |
| 7   | Mehrstufiges Klangrätsel löst geheime Tür                                               | ✱   |
| 8   | Subtile chemische Reaktion verrät den Code                                              | ✱   |
| 9   | Zeitscheiben-Schalter koordiniert drei 5s-Fenster - Soft Fail Alarm 1                   | ✱   |
| 10  | Karbid-Kryptograph - Kryokammer öffnen via Magnetfeldanalyse, Telekinese oder Überreden | ⚠   |

Die SL kann eigene Schwierigkeitsgrade festlegen. Die Tags dienen als
schnelle Orientierung im Mission-Generator.

## Temporale Anomalien-Generator (optional) {#anomalien-generator}

Dieser Abschnitt ist nur relevant, wenn die Runde gezielt temporale Störungen untersuchen möchte.
Für einen Agenten-Thriller sollten solche Effekte sparsam eingesetzt werden.

Zeitreisen gehen selten ohne Nebenwirkungen vonstatten. Jede Sprungsequenz
belastet das Raumzeit-Kontinuum. Nach **1000** vollzogenen Zeitsprüngen
tritt automatisch **eine** der folgenden Anomalien auf - unabhängig davon,
ob die Chrononauten **pro** oder **contra** spielen. Würfelt oder wählt
einen Eintrag, um das Ereignis einzubauen.

### Kuriositäten der Zeit

1. **Zeitblase:** Ein kleines Gebiet bleibt in der Zeit eingefroren oder
   wiederholt denselben Moment in Endlosschleife. Die Helden müssen die
   Ursache finden und die Betroffenen sanft in den normalen Fluss
   zurückführen.
2. **Zeit-Resonanz:** Eine kurz aufblitzende Projektion einer Person aus einer
   anderen Epoche warnt vor naher Gefahr. Die Chrononauten suchen die
   Störquelle, bevor sie weitere Systeme beeinflusst.
3. **Anachronismus-Sturm:** Ein temporaler Sturm wirbelt Personen und
   Objekte aus verschiedenen Zeiten durcheinander. Erst wenn das Epizentrum
   stabilisiert wird, legt sich das Chaos.
4. **Zukunftsresonanz:** Bruchstückhafte Eindrücke eines kommenden
   Ereignisses erscheinen - Konturen eines Gebäudes oder Gesprächsfetzen,
   die nur Sensoren erfassen. Diese Hinweise können warnen oder täuschen.
5. **Zeitschmiede:** Eine Maschine hält einen Riss offen und produziert
   Zeit-Klone oder Artefakte aus alternativen Zukünften. Die Chrononauten
   müssen entscheiden, ob sie die Schmiede zerstören oder kontrolliert
   nutzen.
6. **Paradoxon-Loop:** Die Gruppe bemerkt, dass sie in einer Zeitschleife
   gefangen ist. Nur ein drastischer Schritt - eine zuvor getroffene
   Entscheidung rückgängig machen oder einen von ihnen temporär aus der
   Existenz nehmen - durchbricht den Loop.

Temporale Anomalien sind seltene, aber eindrucksvolle Ereignisse. Setzt sie
sparsam ein, um Spannung, Staunen oder Dringlichkeit zu erzeugen.

## Minor-Anomalien (d6) {#minor-anomalien}

| Wurf | Effekt (1 min)                                      |
| ---- | --------------------------------------------------- |
| 1    | Rostpartikel fliegen rückwärts an Metall.           |
| 2    | Uhrenschläge doppelt so schnell.                    |
| 3    | Haare der Agenten stellen sich elektrostatisch auf. |
| 4    | Gravitation lokal -5 %.                             |
| 5    | Starker Kupfergeruch.                               |
| 6    | Zwei Sekunden absolute Stille.                      |

## Historische Anomalien-Generator {#anomalie_realhistory}

Dieser Patch liefert konkrete Eingriffe in den Verlauf realer Geschichte.
Jeder Block lässt sich direkt in den Mission Seed kopieren.

```yaml
phase: core
- jahr: 1888
  ort: London
  fraktion: Fenian Brotherhood
  ziel: Stoppt Transfer von Hafen-Patenten an Royal Navy
  etablierter_verlauf: Royal Navy modernisiert Docks
  methode: Sabotiert Telegraphenverkehr zwischen Whitehall & Devonport
  codename: HARBOUR-SILENT
- jahr: 1894
  ort: Paris
  fraktion: Dreyfus-Gegner im Militärkartell
  ziel: Erzielt Revision des Prozesses, blockiert Reform
  etablierter_verlauf: Dreyfus wird verurteilt, später rehabilitiert
  methode: Fälscht Cipher-Funksprüche im Etat-Major
  codename: JUSTITIA-BEND
- jahr: 1906
  ort: Istanbul
  fraktion: Reformzirkel der Jungtürken
  ziel: Lässt geheimes Flottenabkommen scheitern
  etablierter_verlauf: Abkommen 1907 ratifiziert
  methode: Drosselt Untersee-Kabelverkehr via Saloniki
  codename: PORTHOLE-ECLIPSE
- jahr: 1911
  ort: Agadir
  fraktion: Deutscher Admiralstab-Hardliner
  ziel: Erzwingen Besetzung statt Kanonenboot-Kriegsspiel
  etablierter_verlauf: Panther-Einsatz bleibt demonstrativ
  methode: Fälscht Handels-Telegramme, löst Marktpanik aus
  codename: SHADOW-PANTHER
- jahr: 1914
  ort: St. Petersburg
  fraktion: Radikale Baltische Sozialisten
  ziel: Verzögern Mobilmachungs-Telegramm
  etablierter_verlauf: Russland mobilisiert zeitgerecht
  methode: Sabotiert Bahnstrom an Schlüsselstationen
  codename: CLOCK-FREEZE
- jahr: 1922
  ort: Dublin
  fraktion: Royalist Network
  ziel: Unterminiert Anglo-Irish Treaty
  etablierter_verlauf: Vertrag wird unterzeichnet
  methode: Fängt Funktelegramme ab und ersetzt Passagen
  codename: EMPIRE-GHOST
- jahr: 1936
  ort: Berlin
  fraktion: KPD-Deckorganisation in der Abwehr
  ziel: Verhindert Antikomintern-Pakt
  etablierter_verlauf: Pakt wird geschlossen
  methode: Stört Kurzwelle-Kreise zwischen Berlin und Tokio
  codename: RED-FEATHER
- jahr: 1943
  ort: Bari
  fraktion: Waffen-Schmuggler-Consortium
  ziel: Lässt Senfgas-Katastrophe größer eskalieren
  etablierter_verlauf: Explosion bleibt lokaler Vorfall
  methode: Manipuliert Hafen-Lichtsignale
  codename: YELLOW-TIDE
- jahr: 1956
  ort: Kairo
  fraktion: Nasser-nahe Geheimgruppe
  ziel: Beschleunigt Nationalisierung des Suezkanals
  etablierter_verlauf: Krisenbeginn Ende Juli
  methode: Lanciert gefälschte britische Ultimaten via BBC
  codename: NILE-ECHO
- jahr: 1962
  ort: Havanna
  fraktion: Hardliner-GRU
  ziel: Erzwingt direkten Abschussbefehl
  etablierter_verlauf: Kennedy und Chruschtschow de-eskalieren
  methode: Überlastet Telefax-Routen, verzögert Abzugsorder
  codename: CROSSHAIR-CUBA
- jahr: 1983
  ort: Moskau
  fraktion: Rotes Oktagon
  ziel: Labelt NATO-Übung Able Archer als Angriff
  etablierter_verlauf: Frühwarnung bleibt Fehlalarm
  methode: Zapft Serpukhov-15 Datenbus physisch an
  codename: IRON-DAWN
- jahr: 1989
  ort: Leipzig
  fraktion: Stasi-Oberkommando
  ziel: Hält Grenzöffnungs-Meldung zurück
  etablierter_verlauf: Günter Schabowski verliest Lockerung
  methode: Filtert Fernschreiben und ersetzt Formulierungen
  codename: WALL-HOLD
```

## Rätsel-Sets {#raetsel_sets}

Vollständige Rätsel für bestimmte Epochen. Die Spalte "Reward" beschreibt den
vorgesehenen Erfolgsbonus.

| id  | jahr            | ort             | puzzle                                             | solution                               | reward                           |
| --- | --------------- | --------------- | -------------------------------------------------- | -------------------------------------- | -------------------------------- |
| 7   | 1888            | London          | 5 Drähte, 3 Enden -> Morsecode.                    | B-G-R-G-S = "SEAL"                     | Schaltschrank offen, +1 Info     |
| 8   | 1906            | Istanbul        | Num-Kalligrafie zeigt Versmaß aus "Divan-i Hafez". | 2358                                   | Artefakt-Zugang, Stress -2       |
| 9   | 1911            | Agadir          | Drei falsche Schiffsrouten ergeben ein Dreieck.    | 30°25′N 09°36′W                        | Feindliches Depot entdeckt       |
| 10  | 1983            | Moskau          | XOR-Lochkarten-Uhrzeiten.                          | Karte 17 -> 101100                     | Countdown gestoppt, Heat -1       |
| 11  | Frühmittelalter | Runen-Stele     | Ringstein mit 16 Runen                             | Sternkarte richten, Fach öffnet        | Fehler: Pfeilfalle               |
| 12  | Spätantike      | Hydr.Orgel      | V/W-Kammern                                        | Wasser angleichen, Pins lösen, Tür auf | Überdruck flutet Kammer          |
| 13  | Viktorianisch   | Zahnrad-Panel   | 12 Messingräder, verschieden                       | Fibo-Reihenfolge                       | Kurzschluss: Dunkel 10 Min       |
| 14  | Near-Future     | QC-Archivkammer | Lichtzahlen in Superpos.                           | Seq. kollabieren, Primzahlen bleiben   | Fehler: EMP-Burst                |

© 2025-2026 pchospital - ZEITRISS® - private use only. See LICENSE.
