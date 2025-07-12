---
title: "ZEITRISS 4.1.6 – Modul 8B: Kreative Generatoren – Begegnungen"
version: 4.1.6
tags: [gameplay]
---

# ZEITRISS 4.1.6 – Modul 8B: **Kreative Generatoren – Begegnungen**

## Gameplay-Index

Modul 8B schließt an 8A an. Teil 7 wurde verworfen, wodurch die Nummerierung eine Lücke aufweist.

- NSC-Generator: Begegnungen im Zeitstrom
- Encounter-Pool: Schnelle Gegnerlisten nach Risiko
- Encounter-Pakete & Twist-Seeds
- ClusterCreate-Nebenwirkungen
- Kreaturen- & Gestalten-Generator
- Para-Creature-Generator: Urban Myth Edition
- Artefakt-Generator: Objekte mit Geschichte
- Kulturfragmente-Generator: Farbe für die Epochen
- Mood-Snippet-Generator
- Rätselbibliothek: Kurze Hürdenszenen
- Temporale Anomalien-Generator & Historische Anomalien
- Rätsel-Sets: Komplette Szenen

## NSC-Generator: Begegnungen im Zeitstrom {#nsc-generator}

Wenn die Spieler spontan irgendjemanden treffen sollen – sei es Verbündeter, Informant oder
Hindernis – hilft es ungemein, einen spannenden NSC aus dem Hut zu zaubern. Dieser Generator liefert
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

  1. Kennt die Zukunft (behauptet es zumindest – optional über Träume)
  2. Ist selbst ein Zeitreisender incognito
  3. Hat einen unerwarteten Alliierten (z. B. ein zahmes Zeitwesen)
  4. Stammt aus einer alternativen Zeitlinie mit abweichendem Wissen
  5. Trägt ein verbotenes Artefakt bei sich
  6. Steht unter einem Paradox-Fluch (z. B. altert rückwärts oder vergisst jede Gegenwart sofort,
     wenn sie vorbei ist)

**Beispiel:** Wir würfeln 2-5-3: _Gelehrter_ – _fanatisch und unbarmherzig_ – _hat einen
unerwarteten Alliierten_. Daraus entsteht vielleicht **Professor Zara**, eine strenge Chrono-
Historikerin aus dem Jahr 1890, die absolut skrupellos versucht, “Zeitfrevel” zu verhindern. Sie ist
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

| Stufe | Beispiel-Gegner                     | Twist                          |
| ---- | ----------------------------------- | ------------------------------ |
| **S**  | 2–3 einfache Wachposten            | Kurze Ablenkung lenkt sie ab   |
| **M**  | Sicherheitsteam mit Spürhund       | Gelände bietet Deckung (-1 SG) |
| **L**  | Elite-Söldner samt Drohne          | Verstärkung nach 2 Runden      |
| **XL** | Paramilitär und leichter Mech      | Zeitriss droht aufzubrechen    |

Die Twist-Karten können auf laminierten Karten notiert werden – ein schneller
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
  text: "Elektrischer Kurzschluss – Funken + Rauch, kein Feuer"
- epoch: "modern"
  type: "security"
  risk: "S"
  text: "Kontrollposten mit veralteter Schlüsselkarte (Hack-Bonus)"

- epoch: "modern"
  type: "security"
  risk: "M"
  text: "4-Mann-Sicherheitstrupp (MP5, Bodycams)"
- epoch: "modern"
  type: "drone"
  risk: "M"
  text: "Drohnenschwarm (3× Quadcopter, IR-Sensor)"
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
  text: "EMP-Mikroladung in nervöser Hand – Finger am Abzug"
- epoch: "modern"
  type: "tech"
  risk: "L"
  text: "Laser-Rasterfeld, automatisch vernetzt mit Geschütznest"
- epoch: "modern"
  type: "psi"
  risk: "L"
  text: "Psi-Sensitive Wache (Telepath I, spürt feindliche Absicht)"
- epoch: "modern"
  type: "explosive"
  risk: "L"
  text: "Countdown-Sprengsatz (3 Min. bis Detonation)"
- epoch: "modern"
  type: "agents"
  risk: "L"
  text: "\u201EBlack Bag\u201C-Team (Agenten derselben Fraktion -+1 Paradox bei Konflikt)"

- epoch: "future"
  type: "anomaly"
  risk: "XL"
  text: "Schwerkraftanomalie (lokaler 0-G-Kern, gefährdet Infrastruktur)"
- epoch: "future"
  type: "mech"
  risk: "XL"
  text: "Hunter-Killer-Mech (Höhe 3 m, Gatling + Raketen)"
- epoch: "future"
  type: "rift"
  risk: "XL"
  text: "Zeitschleifen-Riss – 30-Sek-Loop, verursacht Paradox +2 pro Minute"
- epoch: "future"
  type: "nanite"
  risk: "XL"
  text: "Naniteschwarm (Korrosion jeder Elektronik, Immun gegen Hack)"
- epoch: "future"
  type: "boss"
  risk: "XL"
  text: "Gegenspieler-Ass im Feld (Signatur-NSC mit Plot-Immunität)"
- epoch: "future"
  type: "orbital"
  risk: "XL"
  text: "Orbitale Aufklärungsplattform visiert Gebiet an (Laser Spot – Sat-Strike in 90 Sek.)"
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

## Encounter-Paket „Postorbitales Zeitalter" {#postorbital-encounters}

Diese Gegnerprofile erweitern den späten Zeitraum. Alle Werte folgen dem W6-System.

### 1 · Orbital-Wachdrohne – Sentry-Klasse

| Merkmal       | Wert                                   | Notizen                        |
| ------------- | -------------------------------------- | ------------------------------ |
| **Typ**       | Drohne (S)                             | unbemannt, KI-gestützt         |
| **Speed**     | 8/16 (Flug)                            | Schwebe-Impulsoren             |
| **Panzerung** | Titanfaser 3                           | <2 ignoriert, 3–4 halbiert     |
| **Sensor**    | 60 m 360° LIDAR                        | Tarnwürfe –2                   |
| **Waffen**    | Plasmapuls 2W6 (Explode), Betäubung    | Reichweite 20 m                |
| **Systeme**   | Autorepair 1 HP/Runde                  | deaktiv bei EMP                |
| **Trigger**   | Selbstzerstörung bei ≤ 1 HP (1W6, R=3 m)| historisch → Paradoxon +1      |
| **Rolle**     | Patrouille, Alarmmultiplikator         | verdoppelt "Gefahr im Anflug"  |

### 2 · Konzern-Psychiker – Stufe B (Elite)

| Attribut | Wert | Fertigkeiten                                    | Ausrüstung            |
| -------- | ---- | ------------------------------------------------ | --------------------- |
| Körper 3 | –    | Pistolen 3, Nahkampf 2                           | Nanofaser-Suit SR 2   |
| Geist 4  | –    | Telepathische Überwältigung 4, Precog-Dodge      | Plasmapistole 1W6+1   |
| Psi-Kern 5 | –  | **Spezial:** Psi-Spike (2 PP, CD 2)              | Mind-Screen (−2)      |
| Stress 12 | –   | kämpft bis HP ≤ −4 (Corporate Loyalty)           | –                     |

### 3 · Zeit-Hacker – Stufe A (Transhuman)

| Attribut | Wert | Fertigkeiten                            | Gear                  |
| -------- | ---- | --------------------------------------- | --------------------- |
| Körper 2 | –    | Infowar 5, Athletik 2                   | Inline-Chrono-Tap     |
| Tech 5   | –    | Chrono-Exploit 5, Sabotage 3            | Smart-Gloves (+2)      |
| Psi-Rest 2 | –  | **Spezial:** Temporal Backdoor          | –                     |
| Stress 10 | –   | HP 8                                    |                       |

_Chrono-Exploit:_ 1 PP, friert Zielgerät 1 Runde ein oder verursacht Paradoxon +1 bei Erfolg ≥ 2.
_Temporal Backdoor:_ Bei Signal-Stack 3 entsteht ein Kurz-Rift, dann fällt der Stack auf 0.

### Bonus-Micro-Begegnungen (d13)

1–2 Orbital-Wartungs-Mecha blockieren Zugänge.
3–4 Schwarzmarktschmuggler im Grav-Van.
5–6 Exo-Suit-Salvager durchsuchen Wracks.
7–8 Konzern-San-Team birgt Verwundete.
9–10 Nano-Schwarm breitet sich in Lüftungen aus.
11 Defekte Umwelt-KI erzeugt Fehlalarme.
12 Mini-Rift-Ausläufer verursacht kurzzeitige Anomalien.
13 Anti-Psi-Labor mit isolierten Zellen und Wachen (Psi-Effekte +2 SG)

_Balancing:_ Bei kleinen Teams genügen Drohne **oder** Psychiker. HP und Stress dürfen ±20 % variieren.

## Encounter-Paket „Asien im Kalten Krieg" {#asia-coldwar}

Kurze Begegnungen, inspiriert von Spionagekrimis der 1960er Jahre.

### 1 · Grenzposten am 38. Breitengrad

| Merkmal | Wert | Notizen |
| --- | --- | --- |
| **Typ** | Infanterie (S) | Soldaten mit Karabinern |

### 2 · Agentin „Jade"

| Attribut | Wert | Fertigkeiten | Ausrüstung |
| --- | --- | --- | --- |
| Geist 4 | – | Verkleidung 4, Nahkampf 3 | Mini-Kamera, Giftspritze |

### 3 · Schwarzhändler auf dem Nachtmarkt

| Merkmal | Wert | Notizen |
| --- | --- | --- |
| **Typ** | Kontaktperson (M) | Beschafft Alttech gegen Devisen |

## Encounter-Paket „Orbitalstation 2030+" {#orbital-nearfuture}

Szenarien in einer nahen Zukunft – Forschungsstationen und Weltraumhotels.

### 1 · Wartungstrupp EVA

| Merkmal | Wert | Notizen |
| --- | --- | --- |
| **Typ** | Techniker (S) | Jetpacks, Reparaturtools |

### 2 · Sicherheitsdrohne

| Merkmal | Wert | Notizen |
| --- | --- | --- |
| **Typ** | Drohne (M) | Laserpointer 1W6, Alarm |

### 3 · Schmuggler-Pod

| Merkmal | Wert | Notizen |
| --- | --- | --- |
| **Typ** | Transportkapsel (L) | Schleust verbotene Fracht ein |

### Twist-Seeds (d30) {#twist-seeds}

Jeder Eintrag besitzt nun zwei Zusatz-Tags:
`Paradox-Stufe` (0–3) zeigt das Risiko für Zeitstörungen,
`Historischer Fußabdruck` beschreibt die Tragweite.

Um zu verhindern, dass der Twist-Pool bei langen Kampagnen leerlauft, wandern
gezogene Einträge auf einen Ablagestapel. Sobald weniger als fünf Karten im Pool
liegen, mischt die SL den Stapel zurück.
| Nr. | Twist | Paradox-Stufe | Historischer Fußabdruck |
|----|-------|---------------|-------------------------|
| 1 | Doppelagent im eigenen Team enttarnt sich in der Klimax. | 2 | mittel |
| 2 | Missionsziel ist bereits von einer dritten Fraktion entwendet worden. | 1 | klein |
| 3 | Zeitreisende Version des Auftraggebers sendet widersprüchliche Befehle. | 2 | mittel |
| 4 | Schlüsselfigur entpuppt sich als entfernte Verwandte eines Teammitglieds. | 1 | klein |
| 5 | Artefakt ist lebendig – schwache Bio-Signale, reagiert auf Stress. | 2 | mittel |
| 6 | Geisel möchte nicht gerettet werden, verfolgt eigene Agenda. | 0 | klein |
| 7 | Feindliche KI bietet Allianz gegen ihren Schöpfer an. | 1 | mittel |
| 8 | Historisches Ereignis findet eine Szene früher statt als erwartet. | 1 | mittel |
| 9 | Transportmittel sabotiert – Not-Sprung oder Impro-Flucht nötig. | 1 | klein |
| 10 | Lokaler Widerstand verlangt Gegenleistung, bevor er hilft. | 1 | klein |
| 11 | Wetterphänomen erschwert den Einsatz erheblich. | 1 | klein |
| 12 | Gegner besitzt Teilwissen über Zeitreisetech und nutzt es taktisch. | 2 | mittel |
| 13 | Beweisstücke lösen akute Paradox-Spitzen aus. | 3 | groß |
| 14 | Einsatzort wird zum Sperrgebiet erklärt. | 1 | klein |
| 15 | Verborgene Psi-Barriere dämpft Teamfähigkeiten. | 2 | mittel |
| 16 | Medienleak – Reporter streamt live. | 2 | mittel |
| 17 | Vergessene Nebenfigur fordert Bezahlung ein. | 1 | klein |
| 18 | Missionsziel wird plötzlich hochansteckend. | 2 | mittel |
| 19 | Ausrüstung beginnt zu altern – jede Stunde 10 % Ausfallchance. | 2 | mittel |
| 20 | „Alles war Ablenkung“: Primärer Antagonist greift HQ simultan an. | 3 | groß |
| 21 | Kalter-Krieg-Agent verlangt Austausch gefangener Wissenschaftler. | 1 | klein |
| 22 | Spionageausrüstung enthält heimlichen Sender. | 1 | klein |
| 23 | Verbündeter entpuppt sich als Zukunfts-Double des Rivalen. | 2 | mittel |
| 24 | Funksprüche verweisen auf zweite Zielperson mit eigenem Agenda. | 1 | klein |
| 25 | Zeitanomalie katapultiert Schlüssel-NPC kurzzeitig in Parallelwelt. | 2 | mittel |
| 26 | Team entdeckt verdeckte Waffenlieferung an beide Parteien. | 2 | mittel |
| 27 | Waffentest verursacht EMP, der Equipment lahmlegt. | 1 | mittel |
| 28 | Schwarze Liste eines Geheimdienstes taucht auf – Team steht darauf. | 1 | mittel |
| 29 | Politischer Abgrund: lokale Fraktion plant Putsch während der Mission. | 2 | groß |
| 30 | Rücksprung löst Resonanz aus – Gegner erhält Vorwissen über Actions. | 2 | mittel |
| 31 | Vertrauter NSC gerät unter Einfluss temporaler Schatten. | 2 | mittel |
| 32 | Codex-Datenbank zeigt plötzlich kritische Lücken. | 1 | klein |
| 33 | Zielperson entpuppt sich als Zeitspringer. | 2 | mittel |
| 34 | Rivalenteam bietet Hilfe gegen Anteil am Fund. | 1 | mittel |
| 35 | Eine alte Prophezeiung beschreibt exakt diesen Einsatz. | 2 | groß |
| 36 | Sprungfenster instabil – Rückkehrzeit ungewiss. | 2 | mittel |
| 37 | Gegner entführt Agenten aus einer nahen Zukunft. | 3 | groß |
| 38 | Kameras zeigen Aufnahmen aus kommenden Szenen. | 2 | mittel |
| 39 | Vergrabene Zeitkapsel liefert brisante Gegenbeweise. | 1 | klein |
| 40 | Explosion erzeugt lokale Zeitschleifen. | 3 | groß |
| 41 | Parallel Orders – konkurrierendes Team erhält identische Befehle. | 1 | mittel |
| 42 | Cold Swap – Artefakt stammt aus Parallel-Cluster, HQ fordert Nachverhandlung. | 1 | mittel |
| 43 | Signal-Broadcast warnt Gegner vor dem Team – Stealth +2 SG. | 0 | klein |
| 44 | Delayed Cipher datiert 30 Jahre zu spät – Rätsel PZ‑2.5, Paradox +1 bei Fail. | 1 | klein |
| 45 | Black Budget – unbekannte Geldgeber mischen sich ein, Shadow‑Team optional. | 2 | mittel |
| 46 | Automata sabotieren Bosporus-Telegrafen – Flottenabkommen in Gefahr. | 2 | mittel |
| 47 | Verlorenes Pharaonengrab – Bauplan einer frühen Dampfmaschine sabotiert römische Versorgung. | 2 | mittel |
| 48 | Kreuzzugs-Doppelagent lenkt Armee nach Enttarnung 50 km vom Kurs ab. | 2 | mittel |
| 49 | Gefälschte Seekarten verschieben Columbus’ Landung um Monate. | 1 | mittel |
| 50 | Großer Stadtbrand: Saboteur verhindert Archivverlust. | 2 | groß |
| 51 | Geheime Druckerpresse verbreitet radikale anarchistische Ideen. | 1 | mittel |
| 52 | Hydrogen-Dirigible-Prototyp wird Sabotageziel der Chrononauten. | 2 | mittel |
| 53 | Verdeckte Telegraphenlinie ändert preußische Kriegsplanung. | 2 | mittel |
| 54 | Edison-Sabotage verschiebt Marktführung durch gestohlene Glühfäden. | 2 | mittel |
| 55 | Gedruckte Tarn-Zeitung führt zu Meuterei, Front bricht 48 h früher. | 2 | groß |
| 56 | Aktien-Algorithmus verhindert Börsencrash, Industrie boomt. | 1 | mittel |
| 57 | Geisterarmee-Hologramme ziehen feindliche Reserven ab. | 2 | mittel |
| 58 | Mondlandung-Leak zwingt vorgezogene Apollo-Mission, scheitert fast. | 2 | mittel |
| 59 | Quantenbug in SSL deckt Regierungs-Backdoor auf. | 2 | mittel |
| 60 | Gefälschte Sonnensturmprognose erzwingt globale Evakuierungsproben. | 2 | groß |
| 61 | Asteroid-Bergbau-Kartell zettelt Aufstand auf Raumstation an. | 2 | groß |
| 62 | Terraform-Sabotage durch Mikro-Dronen löst ökologische Reset-Schleife aus. | 3 | groß |

_Gewichtungstipp:_ Bei Missionen im Kalten Krieg können die Einträge 21–30 mit
erhöhter Wahrscheinlichkeit gezogen werden (z.B. doppelte Gewichtung), um die
Zeitperiode stärker zu betonen.

## ClusterCreate-Nebenwirkungen {#clustercreate-nebenwirkungen}

Wenn ein Paradoxon-Index von 5 einen `ClusterCreate()` auslöst, können folgende Nebenwirkungen auftreten:

- Kurzfristige Sensor-Ausfälle oder Rauschen im Funknetz.
 - Spontane Mini-Rifts flackern kurz auf und erzeugen kleine Effekte wie Funkenflug.
- Erinnerungs-Lücken bei Anwesenden, die wenige Sekunden betreffen.

Diese Liste dient als Inspiration für die SL und kann beliebig erweitert werden.

## Kreaturen- & Gestalten-Generator: Begegnungen der ungewöhnlichen Art {#kreaturen-generator}

Nicht nur menschliche NSCs kreuzen den Weg der Chrononauten.
Öffnet sich ein Rift, spawnt es ein Wesen, das zur laufenden Epoche passt.
Rifts in Zukunftsmissionen werfen hingegen die hier gelisteten **Paramonster** aus –
reine Zeitkonstrukte mit genau einem Zeiteffekt.

Würfelt oder wählt eine Kreatur und verwendet den passenden Stat Block.
Jedes Wesen trägt einen **Schwierigkeitswert** von 💀 bis 💀💀💀💀💀,
der angibt, wie hart es Solo-Agenten im Vergleich zu Gruppen trifft.
Faustregel: Pro zusätzlichem Totenkopf sollte das Team mindestens
einen weiteren Agenten oder starke Ausrüstung aufbieten.
Die Totenkopf-Skala ist unabhängig von den Stundengläsern der
Rift-Missionen und erhöht **nicht** den SG.

1. **Zeitschimäre** – Verschmolzene Tiere und Maschinen aus mehreren Epochen.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Zeitschimäre                         │
│ Rift-Tier: Standard Rift                   │
│ HP-Pool: W6 × 2 (Exploding)                │
│ Defense-Schwelle: 5                        │
│ Difficulty: 💀💀💀                           │
│ Signature Power: Time-Skip Blink           │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Survival 13          │
│ Tells: Flimmernde Körperteile, wildes Fauchen│
│ Shard-Drop: 3                              │
╰────────────────────────────────────────────╯
```

Greift alles an, bis der Riss geschlossen ist.

2. **Zeitwächter-Golem** – Chronotechnischer Wächter in alten Tempeln.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Zeitwächter-Golem                    │
│ Rift-Tier: Standard Rift                   │
│ HP-Pool: W6 × 2 (Exploding)                │
│ Defense-Schwelle: 5                        │
│ Difficulty: 💀💀💀                           │
│ Signature Power: Stasis Wall               │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Lore 14              │
│ Tells: Grollendes Steinechos, leuchtende Glyphen │
│ Shard-Drop: 3                              │
╰────────────────────────────────────────────╯
```

Fällt in Schlaf, wenn sein Ritualstein deaktiviert wird.

3. **Chronogeist** – Verlorene Seele zwischen den Zeiten.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Chronogeist                          │
│ Rift-Tier: Minor Rift                      │
│ HP-Pool: W6 × 1 (Exploding)                │
│ Defense-Schwelle: 4                        │
│ Difficulty: 💀💀                            │
│ Signature Power: Loop Feedback                 │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Empathy 12           │
│ Tells: Flackernde Silhouette, kaltes Flüstern │
│ Shard-Drop: 2                              │
╰────────────────────────────────────────────╯
```

Kann erlöst oder endgültig gebannt werden.

4. **Mechanischer Zeitläufer** – Kleines Uhrwerk-Wesen mit eigener Agenda.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Mechanischer Zeitläufer              │
│ Rift-Tier: Minor Rift                      │
│ HP-Pool: W6 × 1 (Exploding)                │
│ Defense-Schwelle: 4                        │
│ Difficulty: 💀💀                            │
│ Signature Power: Reverse Flow              │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Tech 12              │
│ Tells: Surren von Zahnrädern, schnelle Sprünge │
│ Shard-Drop: 2                              │
╰────────────────────────────────────────────╯
```

Wird schlauer, je länger er unbehelligt bleibt.

5. **Dämon der Zeitschlucht** – Manifestierte Zeitlinie in monströser Form.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Dämon der Zeitschlucht               │
│ Rift-Tier: Major Rift                      │
│ HP-Pool: W6 × 3 (Exploding)                │
│ Defense-Schwelle: 6                        │
│ Difficulty: 💀💀💀💀💀                         │
│ Signature Power: Age-Burn Touch            │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Charisma 16          │
│ Tells: Schwarzer Nebel, verzerrte Realität │
│ Shard-Drop: 4                              │
╰────────────────────────────────────────────╯
```

Nur mehrere Zeitanker können ihn bannen.

6. **Zeit-Egel** – Parasitärer Räuber, der temporale Energie saugt.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Zeit-Egel                            │
│ Rift-Tier: Minor Rift                      │
│ HP-Pool: W6 × 1 (Exploding)                │
│ Defense-Schwelle: 4                        │
│ Difficulty: 💀💀                            │
│ Signature Power: Time-Slow Bubble          │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Medicine 12          │
│ Tells: Kurze Zeitsprünge der Opfer, blasser Schleim │
│ Shard-Drop: 2                              │
╰────────────────────────────────────────────╯
```

Nur sichtbar oder entfernbar mit speziellem Gerät.
Diese Kreaturen (und viele mehr) könnt ihr einbauen, um euren Abenteuern Würze und Mysterium zu
verleihen. Wichtig ist, sie **sparsam und gezielt** einzusetzen – jede besondere Begegnung soll sich
einzigartig anfühlen. Die Spieler dürfen ruhig mal ins Grübeln kommen: “Was zum Henker ist _das_!?”
Und wenn sie dann nach und nach die Hintergrundgeschichte oder Logik dahinter entdecken, wird aus
einem Monster plötzlich ein integraler Teil der Story – vielleicht sogar etwas Mitfühlenswertes oder
Respektgebietendes. Gerade in ZEITRISS, wo Mythologie oft einen zeitphänomenalen Ursprung hat,
können solche Kreaturen dafür sorgen, dass selbst erfahrene Chrononauten nie vergessen: **Die Zeit
birgt unendliche Überraschungen.**

<a id="para-creature-generator"></a>
## Para-Creature-Generator: Urban Myth Edition {#para-creature-generator}

Kompaktgenerator samt drei gebrauchsfertigen Fallakten im „X‑Files“-Dossier-Stil.
Alle Werte nutzen das **ZEITRISS‑W6-System (Exploding 6)**.

### Vorgehen

1. Würfle **1W6** für die Epoche.
2. Würfle **1W20** für das urbane Mythos-Motiv.
3. Kreiere die technisch plausible Ursache (Ideen siehe Motiv-Spalte).
4. Setze den Stat-Block nach Risikostufe (S/M/L/XL) ein.

```markdown
### 1A – Epoche (d6)
1 | Frühe Neuzeit (1500‑1700)
2 | Industrialisierung (1700‑1900)
3 | Weltkriege (1914‑1945)
4 | Kalter Krieg (1945‑1991)
5 | Digitale Anfänge (1992‑2010)
6 | Near‑Future (2011‑2035)

### 1B – Urban‑Myth‑Motiv (d20)
01 | Kopfloser Reiter – Holo‑Projektor auf Drohne
02 | Schwarzer Hund – Chem‑Mod Kampf­organismus
03 | Mothman – Stealth‑Fallschirmspringer im Testanzug
04 | Schattenleute – Psi‑Induzierte Schlafparalyse
05 | Rote Hexe – Nano‑Feuer‑Aerosol erzeugt „Flammen“
06 | Men in Black – Regierungsabteilung nutzt Neural‑Wipe
07 | Weeping Woman – Audio‑Drohne mit Lament‑Frequenz
08 | Phantom‑Zug – Magnetschwebetest, Zeit ➙ Verwerfung
09 | Kinder mit schwarzen Augen – Gen‑Versuch / Linsenimplantat
10 | Kraken im Kanal – Sewer‑Drohne mit Tentakel‑Manipulatoren
11 | Crying Boy Painting – Quantenspeicher im Pigment (Daten‑Vault)
12 | Goatman – Bio‑Chimäre entlaufenem Labor
13 | Greys – Nano‑Skin‑Anzüge verzerren Proportionen
14 | Hitchhiking Ghost – Zeitversetzte Holo-Aufnahme
15 | Lake‑Monster – Schwarm‑U‑Drohnen unter Hüllfeld
16 | Shapeshifter – adaptive Metamaterial‑Suit
17 | Spukhaus – Übersprungener EM‑Emitter tft Paradox‑Energie
18 | Schlankes Wesen – Lidar‑Verzerrer + Knochenverlängerungen
19 | Straßenlaternen‑Summen – HF‑Psi‑Störsender, löst Migräne aus
20 | Blutfarbenes Mondlicht – Orbitale Linse fokussiert IR‑Spektrum
```

### Stat-Block-Schablone

| Gefahr | **Str** | **Agi** | **Mind** | **Psi‑Sig** | **Armor** | **HP** | Specials |
| ------ | ------: | ------: | -------: | ----------: | --------- | -----: | -------- |
| **S**  |     2d6 |     3d6 |      2d6 |         1d6 | 0         |      6 | 1 Fähigkeit |
| **M**  |     3d6 |     4d6 |      3d6 |         2d6 | 1         |      8 | 2 Fähigkeiten |
| **L**  |     4d6 |     4d6 |      3d6 |         3d6 | 2         |     10 | 3 Fähigkeiten |
| **XL** |     5d6 |     5d6 |      4d6 |         4d6 | 3         |     14 | 4+ Fähigkeiten |

> **Armor** reduziert Schaden pro Treffer.
> **HP** ist die Wundschwelle (W = 3 HP).
> **Psi‑Sig** wird gegen Psi-Detection oder Paradox-Interaktion gewürfelt.

### Drei einsatzbereite Fallakten

> Format lehnt sich an ein klassisches FBI‑X‑Files‑Briefing an.
> **Zeilen in Klammern** eignen sich als schnelle HUD-Tags.
> Weiterführende Hinweise finden sich im Modul
> [Cinematisches HUD-Overlay](../characters/zustaende-hud-system.md#cinematisches-hud-overlay).

#### A. Black Dog – „Schinderhannes‑Geflüster“

> **Epoche:** Industrialisierung (1893, Eifel) | **Risikostufe:** M

- **Mythos:** Schwarzer, schweigsamer Hund soll Nachtwächter zu Tode gehetzt haben.
- **Realität:** Firma **Krieg & Sohn** testet kobaltimprägnierte **Chem‑Mod‑Raupenhunde** für Grabenschlachten.
- **Beobachtungen:** Opfer weisen akute Blutarmut (Toxin α‑13) auf.
- **Paradox‑Risiko:** gering (≤ 1).
- **STAT‑BLOCK:**

  - **Str 3d6 | Agi 4d6 | Mind 2d6 | Psi‑Sig 2d6 | Armor 1 | HP 8**
  - *F1 Parcours‑Beißer*: freier Move über Hindernisse, Attacke ignoriert Deckung.
  - *F2 Schwarzlicht‑Pelz*: unsichtbar für IR/NV‑Optik (−2 Mod auf Entdecken).

#### B. Mothman – „Projekt Nachtfalke“

> **Epoche:** Kalter Krieg (1967, Point Pleasant, USA) | **Risikostufe:** L

- **Mythos:** Geflügeltes Wesen mit roten Augen warnt vor Brückeneinsturz.
- **Realität:** US‑Airforce Black‑Op mit Prototyp‑**Stealth‑Wing‑Suit**.
  Aufklärer filmte Stahlermüdung – Intervention verboten.
- **Paradox‑Risiko:** mittel (2‑3) bei temporalen Eingriffen.
- **STAT‑BLOCK:**

  - **Str 4d6 | Agi 4d6 | Mind 3d6 | Psi‑Sig 3d6 | Armor 2 | HP 10**
  - *F1 Schwebe‑Stillstand*: 0 m Schwebeflug → +2 Agi auf Ausweichen.
  - *F2 Sonic‑Scream‑Baken*: 1/Tag, macht Wache 1 Rd. taub (−2 Agi).
  - *F3 Omen‑Protokoll*: Bei Sichtung +1 Stress für Zivilisten, SL‑Bonuswürfel.

#### C. Shadow People – „Umbra-Reflex“

> **Epoche:** Near‑Future (2025, Seoul) | **Risikostufe:** XL

- **Mythos:** Dunkle Silhouetten erscheinen im Augenwinkel, verschwinden bei Blickkontakt.
- **Realität:** Konzern **Limbic Inc.** testet neuronale **Psi‑Induktoren**,
   die REM‑Bereiche wecken → kollektive Hypnagoge.
- **Paradox‑Risiko:** hoch (4‑5) – massenhafter Psi‑Einsatz stört Zeitfeld‑Sensoren.
- **STAT‑BLOCK:**

  - **Str 5d6 | Agi 5d6 | Mind 4d6 | Psi‑Sig 4d6 | Armor 3 | HP 14**
  - *F1 Flimmer‑Phase*: kann sich als „Nachbild“ 10 m teleport‑ähnlich versetzen.
  - *F2 Psi‑Drown*: 1/3 Rd. −2 Mind und −1 Reaktions‑Ini für alle Nicht‑Psi.
  - *F3 Paradox‑Spike*: Bei Treffer explodiert Psi‑Sig auf W6=6 (Paradox +1).
  - *F4 Schwarm‑Halluzination*: Jeder Witness‑NPC muss Will-Save (Mind 3d6) oder flieht.

### Einsatz-Tips

1. **Epochale Einbettung:** Passe die Technologie-Coverstory an Ort und Jahr an.
2. **Paradox-Ventile:** XL-Kreaturen sollten eine Mechanik besitzen, die direkt mit dem Paradoxon-Index interagiert.
3. **Cinematic Hooks:** Gib der Kreatur ein ikonisches Geräusch oder Lichtsignal, das Spieler früh wahrnehmen.
4. **Salvage-Rewards:** Nach Besiegung 1–2 modulare Tech-Fragmente als Plot-Coupon oder Craft-Teil.

## Artefakt-Generator: Objekte mit Geschichte {#artefakt-generator}

Zeitreisen führen unweigerlich zu **kuriosen Objekten**, die nicht in ihre Epoche gehören, oder zu
mächtigen Relikten, welche die Jahre überdauert haben. Wenn ihr spontan einen interessanten
Gegenstand benötigt – als Loot, Missionsziel oder einfach als atmosphärisches Detail – nutzt diesen
Generator. Er kombiniert eine **Objektart** mit einer **besonderen Eigenschaft** und einer
**Herkunft/Historie**:

*Tipp:* Lasst den Codex bereits eine Sitzung vorher ein **Gerücht** über ein mögliches Artefakt
streuen. So wird der spätere Fund stimmungsvoll vorbereitet und die Spieler achten stärker auf
Hinweise.

*Items mit {rare_rift} erscheinen nur in Pararifts.*
### Artefakt-Seed-Starter (1W14) {#artefakt-seed-starter-1w14}

| Wurf | Codename | Jahr / Ort | Primäre Kraft | Nebenwirkung |
|-----:|----------|-----------|---------------|---------------|
| 1 | „Ätherglas" | Prag 1889 | Unsichtbarkeit (2 Min.) | Kälte -10 °C |
| 2 | „Helios-Split" | Delphi -430 | Lichtstrahl 1 kW | Blendung Benutzer |
| 3 | „Sforza-Würfel" | Mailand 1496 | Local Time-Freeze 5 Sek. | Paradoxon +1  | {rare_rift}
| 4 | „Chorus-Reel" | New York 1941 | Stimmen-Mimikry | Ohrensausen  | {rare_rift}
| 5 | „Kalkstein-Rune" | Göbekli Tepe -9020 | Telepathie 100 m | Migräne  | {rare_rift}
| 6 | „Jade-Kompass" | Xi’an 221 v. Chr. | Portalsprung 10 m | random scatter 3 m  | {rare_rift}
| 7 | „Edison-Spule" | Menlo Park 1877 | EMP Radius 5 m | Gerät defekt  | {rare_rift}
| 8 | „Orpheus-Harfe" | Wien 1791 | Emotion Control | Selbst → Trauer  | {rare_rift}
| 9 | „Fresnel-Linse" | Paris 1848 | Hologram 10 min | Akku 100 CU  | {rare_rift}
| 10 | „Cronos-Sand" | Alexandria 48 v. Chr. | Rücksprung 1 Tag | Paradoxon +2  | {rare_rift}
| 11 | „Chrono‑Shard Panel" | unbekannt | zeigt 60 s Ereignis 24 h vor | Desorientierung  | {rare_rift}
| 12 | „Möbius Coin" | wechselnd | Wahrscheinlichkeitsbeeinflussung 70 % | Entropie‑Spike  | {rare_rift}
| 13 | „Heisenberg Anchor" | Forschungslab 2035 | fixiert Objektposition 10 min | kinetische Stoßwelle  | {rare_rift}
| 14 | „Ouroboros Pulse Node" | Mars 2170 | 30 s Zeitschleife im 10 m Radius | Fusion am Loop-Ende  | {rare_rift}

### Artefakt-Jagd: Fortschrittsbalken

Jede abgeschlossene Mission erhöht die Chance auf einen legendären Fund um 5 %.
Im HUD erscheint ein Balken („Gerüchte 20 %“), der diesen Wert anzeigt. Erreicht
die Anzeige 100 %, ist die nächste Mission automatisch ein Artefakt-Run und der
Zähler springt auf 0. Rückschläge oder Fehlschläge können den Wert um 10 %
senken.

- **Objektart:**

  1. Waffe
  2. Buch oder Schriftrolle
  3. Gerät/Technologie
  4. Schmuckstück
  5. Alltagsgegenstand
  6. Substanz oder Trank

- **Besondere Eigenschaft:**

  1. Zeitverschoben (existiert gleichzeitig doppelt in zwei Epochen)
  2. Unzerstörbar durch normale Mittel
  3. Lebendig (hat einen eigenen Willen oder eine KI)
  4. Verändert seine Form je nach Epoche
  5. Kann einmalig die Zeit **lokal** beeinflussen (z. B. 5 Sekunden zurückdrehen)

- **Herkunft/Historie:**

  1. Stammt von einer berühmten historischen Persönlichkeit (z. B. Excalibur, Teslas Notizbuch)
  2. Wurde von Aliens in der Antike hinterlassen
  3. Ein Prototyp aus der Zukunft, der verloren ging
  4. Durch ein Paradoxon erschaffen (das Objekt dürfte _eigentlich_ nicht existieren)
  5. Wird in einer Kultur religiös verehrt (als göttliches Relikt missverstanden)
  6. Wurde von einem Zeitreisenden absichtlich versteckt, um später gefunden zu werden

**Beispiel:** Kombination 3-6-4 (_Gerät_ + _Zeitmanipulation_ + _Paradoxon_) ergibt ein Gerät mit
einmaliger Zeitfunktion, das durch ein Paradoxon erschaffen wurde. GPT ersinnt vielleicht die
**“Stundenglas-Bombe”** – ein kleines mit Zahnrädern versehenes Gerät, das aussieht wie ein
viktorianisches Stundenglas. Seine Eigenschaft: Es kann einmalig **die Zeit um ein paar Kampfrunden
zurückspulen** (in einem begrenzten Umkreis). Dabei entsteht jedoch ein Paradoxon, weil das Gerät
sich selbst eigentlich nie gebaut haben kann – jedes Mal, wenn es benutzt wird, übergibt es sich
quasi selbst an die Nutzer in der Vergangenheit. Das Objekt dürfte also gar nicht existieren, doch
_da es existiert_, verursacht jeder Einsatz einen kleinen Riss im Zeitgefüge. Die Helden könnten es
als Notfallplan einsetzen, wissen aber: **Jeder Gebrauch destabilisiert den Zeitstrom** – ein wunder
Punkt und Dilemma!

_Ein anderes Beispiel:_ Kombination 1-3-1 (_Waffe_ + _lebendig_ + _berühmte Person_) ergibt eine
lebendige Waffe, die einst einer berühmten Person gehörte. Heraus kommt vielleicht **“Alexander der
Große’s sprechendes Schwert”**, dem man eine eigene Persönlichkeit nachsagt – tatsächlich verbirgt
sich darin eine KI aus der Zukunft in Form eines Schwertes, die Alexander fand und für göttliche
Eingebung hielt. Das Schwert berät den Träger im Kampf (optional über ein eingebautes Kommunikationssystem) und
hat eigene Ziele – vielleicht _will_ es, dass man es zu einem bestimmten Zeitpunkt in der Zukunft
trägt, um dort etwas zu bewirken.

Mit solchen Artefakten könnt ihr tolle Plots entwerfen. Gerade wenn Spieler freies Spiel genießen,
lieben sie es, **seltsame Gegenstände** zu sammeln und deren Zweck herauszufinden. Vielleicht
entfaltet ein Artefakt erst im Finale seine volle Macht – oder es bringt einfach Flair in den
Alltag, z. B. ein Stein, der bei Gefahr warm wird, oder ein Amulett, das hin und wieder im Verlauf einer Mission ein
Flüstern aus der Zukunft von sich gibt. ZEITRISS bietet die Bühne, eure ganz eigenen „mysteriösen“
Gegenstände zu kreieren – nur dass die Magie hier oft Wissenschaft oder Paradoxie ist.


### Modul‑Add‑on »Artefakte«

*(kompatibel zu ZEITRISS 4.1.4, ready‑to‑drop oder als Generator nutzbar)*

| Stufe | Nutzenbeispiel | Risiko (Paradoxon‑Index) | Icon‑Label* |
|------:|----------------|-------------------------|-------------|
| **A** | Geringfügige Info‑Vorteile | +0 | 📄 |
| **B** | Temporärer Skillboost (+1 Würfel) | +1 pro Einsatz | 🔹 |
| **C** | Einmaliger Technologie‑Sprung | +2 sofort | ⚙️ |
| **D** | Zeit‑Manipulation im Minutenbereich | +4 sofort | ⏳ |
| **E** | Historische Konstanten ändern | +5 & ClusterCreate‑Check | ☢️ |

\*Die Icon‑Labels entsprechen Unicode‑Emojis; im Layout können eigene Piktogramme verwendet werden.

#### Zweiundvierzig einsatzbereite Artefakte

|#|Codename|Form|Hauptwirkung|Nebenwirkung|Beispiel|
|-|-|-|-|-|-|
|A-01|Helios-Lens|Messinglinse Ø18cm|2W6 Hitze (R5)|1/6 Flash, Stress+2|Sabotage|
|A-02|Dirac-Whisper Circuit|Bakelit-Kästchen 1920er|30s Duplex ±5J|Paradox +1|Kontakt|
|A-03|Sub-Lumen Chalk|12cm Kreide, IR|SR≤3 verbergen (3h)|Mini-Rift bei 0|Fluchtweg|
|A-04|Phase-Lock Shard|Rubinfragment im Vial|1 Rd phasing|HP-2, Stress+4|Lasergitter|
|A-05|Reso Capsule|Edelstahlkapsel, Glas|Objekt ≤1kg (1Rd)|Zeitstempel auf Original|Double-Device|
|A-06|Chrono-Braid|Geflochtene Kupferlitzen|Zeitfenster 2s|Stress +1|Schneller Zugriff|
|A-07|Phantom Tesser|Glaskugel|Illusion 3m|Paradox +1|Ablenkung|
|A-08|Neuro-Splicer|Biogel-Kartusche|+1 Tech-Probe|Kurzzeit-Blackout|Modding|
|A-09|Frost Prism|Kleiner Kristall|Kältefeld R2|Brüchig nach Nutzung|Einfrieren|
|A-10|Arc Glyph|Runenkachel|Teleport 5m|Paradox +1|Kampfescape|
|A-11|Grav Spinner|Metallscheibe|Schwerkraftwelle|Ermüdung|Deckung|
|A-12|Reso Prism|Taschenglas|Kopiert Stimme 10s|Verliert Halt|Impersonation|
|A-13|Vector Flare|Mini-Leuchtrakete|Signal an Verbündete|Index +1|Notruf|
|A-14|Ion Loop|Handreif|EMP 3m|Geräte kurzzeitig defekt|Sicherung|
|A-15|Chrono Gloom|Dunkler Nebel|Sicht -2m|Kältegefühl|Flucht|
|A-16|Memory Locket|Amulett|1 Szene Erinnerung teilen|Stress +1|Verhör|
|A-17|Pulse Mine|Scheibe Ø5cm|Betäubung R1|Paradox +1|Sturmangriff|
|A-18|Shadow Scrip|Pergament|Unsichtbare Tinte|Nur UV-Licht löscht|Spionage|
|A-19|Phase Token|Chip|Durchlässigkeit 1Rd|HP -1|Wand-Trick|
|A-20|Nova Shard|Splitter|Lichtblitz R2|Blind für 1Rd|Überfall|
|A-21|Clarity Vial|Fläschchen|Heilt 1 Stress|Nachwirkung Benommen|Med-Paket|
|A-22|Static Rod|Kurzstab|Elektrischer Impuls|Selbst Schaden 1|Sabotage|
|A-23|Warp Nail|Metallstift|Fixiert Objekt im Raum|Paradox +1|Absicherung|
|A-24|Ghost Net|Drahtgeflecht|Fängt Datenfunksignale|Batterie leer|Lauschangriff|
|A-25|Storm Coil|Röhre|Wettereffekt klein|Index +1|Ablenkung|
|A-26|Glass Heart|Kristallampulle|Tarnt Lebenszeichen|Splittergefahr|Infiltration|
|A-27|Logic Dice|Würfelpaar|+1 Analyse|Paradox +1 bei Pasch|Taktik|
|A-28|Blink Patch|Aufkleber|Teleport Objekt 1kg|Verliert Haftung|Schmuggel|
|A-29|Sonic Braid|Schallfaser|Stillefeld R1|Hört selbst schlecht|Heimlichkeit|
|A-30|Vortex Pin|Anstecknadel|Mini-Wirbel R1|Einmalig nutzbar|Verwirrung|
|A-31|Flux Band|Armband|Neutralisiert Kräfte 1Rd|Stress +2|Gegnerkontrolle|
|A-32|Stasis Cube|Würfel 3cm|Objekt einfrieren 1h|Paradox +1|Sicherung|
|A-33|Spark Veil|Tuch|Tarnung gegen Sensoren|Entzündlich|Flucht|
|A-34|Mimic Coin|Münze|Kopiert ID-Signatur|Index +1|Betrug|
|A-35|Hyper Lens|Lupenbrille|Vergrößert Details|Kopfschmerz|Analyse|
|A-36|Aether Drum|Kleiner Resonator|Lockt Kreaturen|Laut|Ablenkung|
|A-37|Psi Spike|Stift|+1 Psi-Fokus|Stress +1|Boost|
|A-38|Grim Oath|Runenstein|Bindet Schwur 1 Szene|Paradox +1|Vertrag|
|A-39|Rift Chalk|Farbstaub|Markiert Mini-Rift|Kurzzeitige Instabilität|Portal|
|A-40|Signal Orb|Leuchtkugel|Zeigt Richtung zum Artefakt|Zerbrechlich|Spurensuche|
|A-41|Signal Relais|Kompaktes Funksystem|5 min Signal in die Vergangenheit|Paradox +1 bei >2 Nutzungen|Abhören|
|A-42|Chrono Patch|Einweg-Med-Gel|Kritisch-Zustand 60 s verzögert|Verbrauchsgut|Rettung|

_Regel‑Hooks:_ Schadens‑ und Stresswerte folgen dem W6‑Explode‑Raster. Artefakte sind selten:
höchstens ein Item alle drei Missionen. Jeder Artefakt‑Loot erhöht den Paradoxon‑Index um 1.

#### Artefakt‑Generator (D‑Sequenz)
- **D1 Strukturklasse (W6):** Relikt; Tech-Modul; Bio-Probe; Quantum-Device; Hybrid-Implantat; Daten-Singularität
- **D2 Ursprungs-Epoche (W8):** Antike; Industriezeit; Orbit-Boom; Kalter Krieg;
  Digitalfrühphase; Neu-Orbital; Terra-Kolonien; Off-Timeline
- **D3 Kernfunktion (W12):** Sensorik; Energieimpuls; Materie modifizieren; Bewusstsein speichern; Teleport;
  Kräfte neutralisieren; Duplikat; Raum verschlüsseln; Daten korrumpieren; Heilen; Illusion; Zeitfenster stauchen
- **D4 Aktivierung (W6):** Hautkontakt; Pass-Phrase; Chrono-Keycard; Strahlungsimpuls; Druck >2 bar; Neural-Sync
- **D5 Nebenwirkung (W8):** Stress +W6; HP -2; Paradoxon +1; Sensorschatten; Blindspot; EMP 5m; Grav-Anom.; Mini-Rift
- **D6 Sicherheitsstufe (W6):** Kein Schutz; Biometrie-Siegel; Nano-Lock; Quanten-Cipher; Schredder-Fail-Safe
#### Generator‑Beispiel (One‑Roll‑Complete)

Würfe: 4 / 6 / 12 / 2 / 1 / 5 → **„Tachyon Sleeve MK‑IV“** – biomechanische Unterarm‑Schiene,
komprimiert Eigenzeit um 50 % für 2 Runden nach Codewort‑Aktivierung. Nutzung erzeugt W6 Stress;
unerlaubter Zugriff scheitert am Quanten‑Cipher‑Schutz.

#### Einbettung & Balancing‑Hinweise

1. **Fundhäufigkeit:** 8 % Chance in High‑Risk‑Zonen, niemals als Shop‑Loot.
2. **Paradoxon‑Wechselwirkung:** Jede Nutzung, die die Epoche bricht, provoziert einen
   Paradoxon‑Check (Ref ≤ 3 → +1).
3. **Codex‑Tagging:** `artefakte/<epoch>/<funktion>` zur schnellen Filterung.
4. **Reverse Engineering:** Nur mit Tech ≥ 5 und nach Abschluss von 5 Missionen oder einer Kampagne; 50 % Risiko,
   den Effekt zu verlieren.

#### Copy‑Paste‑Snippet für den Codex (JSON‑Minimal)

```json
{
  "artefakte": [
    {
      "id": "A-01",
      "name": "Helios-Lens",
      "epoch": "Industriezeit 1912",
      "form": "Messinglinse",
      "effect": "2W6 Hitzeimpuls",
      "drawback": "Radiation Flash, Stress+2",
      "paradoxon": 0
    }
  ]
}
```

_Upgrade abgeschlossen – der Generator liefert nahezu unendliche Varianten, während die fünf
Ready‑Mades sofort einsetzbar sind._

## Kulturfragmente-Generator: Farbe für die Epochen {#kulturfragmente}

Wer durch die Zeit reist, trifft auf fremde **Kulturen, Bräuche und Alltagsdetails**, die eine
Epoche erst _authentisch_ machen. Dieser Generator hilft dabei, schnell ein **Kulturfragment**
einzustreuen, das der Szene mehr Tiefe gibt – ideal, wenn Spieler fragen: _“Gibt es hier gerade ein
Fest oder so?”_ oder wenn ihr einfach Atmosphäre schaffen wollt.

Wählt einen Aspekt (oder mehrere), der die aktuelle Epoche prägt:

- **Festliche Anlässe:**

  1. Ein großes Volksfest findet statt (Erntedank, Siegesfeier o. Ä.).
  2. Religiöse Prozession oder ein hoher Feiertag prägt den Tag.
  3. Eine Krönung oder Hochzeit eines Herrschers sorgt für Aufruhr.
  4. Ein Initiationsritus steht bevor (Jugendliche werden in der Gesellschaft als Erwachsene
     anerkannt).
  5. Ein Gedenktag an ein historisches Ereignis findet gerade statt.
  6. Ein spontaner Karneval (oder Aufruhr) tobt auf den Straßen.

- **Sitten und Aberglaube:**

  1. Alle Leute tragen ein bestimmtes Symbol bei sich, um Unglück abzuwehren.
  2. Bestimmte Worte oder Namen werden nie ausgesprochen – sie gelten als Tabu.
  3. Es gibt einen ungewöhnlichen Begrüßungsritus, den Außenstehende seltsam finden.
  4. Ein lokaler Aberglaube bestimmt das Handeln aller (z. B. darf man um Mitternacht **niemals** X
     tun).
  5. An den Straßenecken liegen Opfergaben für unsichtbare Zeitgeister – die Menschen spüren
     instinktiv temporale Unregelmäßigkeiten und versuchen, diese gnädig zu stimmen.
  6. Jeder Fremde muss erst **eine Prüfung** oder Aufgabe erledigen, um akzeptiert zu werden.

- **Mode und Technik-Spleens:**

  1. Eine auffällige Modefarbe dominiert – alle tragen etwas in dieser Farbe (z. B. Rot, zur
     Erinnerung an einen alten Krieg).
  2. Ein Modeaccessoire mit kurioser **Funktion** ist der letzte Schrei (z. B. in einer Steampunk-
     Gesellschaft: ein Monokel, das als kleiner Bildschirm dient).
  3. Die neueste Mode sind kleine **Automaton-Haustiere** – etwa Uhrwerk-Vögelchen an der Leine.
  4. Ungewöhnliche Architektur prägt das Stadtbild (vielleicht sind alle Gebäude aus schwarzem
     Basalt oder vollkommen ohne Ecken gebaut etc.).
  5. Eine lokale Essgewohnheit erstaunt Fremde (etwa werden Speisen zuerst den Ahnen geopfert und
     dann erst gegessen).
  6. Eine spezifische Grußformel oder Redewendung ist allgegenwärtig, mit einer historischen
     Anekdote dahinter (“Möge der Kaiser dir nicht zweimal begegnen” – sprich: man bekommt vom Herrscher
     keine zweite Chance).

- **Gesellschaft & Gesetz:**

  1. Es herrscht strikte **Ausgangssperre** ab einer bestimmten Stunde (vielleicht aus temporalen
     Gründen – man will Geister oder Zeitdiebe fernhalten?).
  2. Ein **Kasten- oder Gildensystem** prägt das Miteinander; Fremde werden automatisch als
     niedrigste Stufe behandelt.
  3. Aktuell gilt **Kriegsrecht** – überall Patrouillen, Ausweiskontrollen und eine angespannte
     Stimmung.
  4. Extrem rigide Ehrvorstellungen: Schon kleinste Beleidigungen werden durch **Duelle auf Leben
     und Tod** gesühnt. (Die Helden müssen höllisch aufpassen, was sie sagen!)
  5. Bizarres Gesetz: Jeder Besucher muss eine Art **“Zeit-Zoll”** entrichten – sei es in Währung
     oder durch eine verrichtete Arbeit. Man glaubt, die Lebenszeit Fremder schulde der Stadt etwas.
  6. **Prophezeiungen oder Astrologie** sind Teil der offiziellen Gesetzgebung. Bestimmte Tage sind
     für gewisse Handlungen verboten, oder ein “Zeit-Orakel” muss wichtige Entscheidungen absegnen.

**Beispiel:** In einer Renaissance-Stadt (Florenz 1500) würfle ich auf _Sitten & Aberglaube_ und
erhalte eine 2: Bestimmte Worte werden nie ausgesprochen. GPT interpretiert dies so: _In Florenz
wagt niemand, direkt vom “Teufel” zu sprechen – man umschreibt ihn als “den mit den Hörnern”._ Der
Grund: Man glaubt, Worte beschwören Realität. Die Chrononauten merken das deutlich, als ein NSC
zusammenzuckt, weil einer von ihnen unbekümmert **“diavolo”** gesagt hat. – Schon bekommt ein
einfaches Gespräch sofort eine interessante kulturelle Note!

Solche Kulturfragmente lassen die Welt lebendig und eigen wirken. Die Helden merken: **Jede Epoche
hat ihre Eigenheiten**, und wenn sie sich klug darauf einlassen (bzw. GPT sie daran erinnert),
können sie so manch unnötigen Konflikt vermeiden oder Sympathien gewinnen. Vielleicht machen sie bei
einem lokalen Fest mit und gewinnen dadurch Verbündete – oder sie nutzen einen Aberglauben gezielt

für sich (_“Wir verkleiden uns als die Ahnengeister, damit sie uns zuhören!”_). Diese kleinen Dinge
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

| Nr. | Beschreibung | Tag |
|----|-------------|-----|
| 1 | Geheimtür über Schallfrequenz öffnen | ⌖ |
| 2 | Mechanisches Schloss mit rotierendem Zahlenring | ⌖ |
| 3 | Verschlüsseltes Tagebuch in historischem Dialekt | ⚠ |
| 4 | Laserlabyrinth, das nur bei Schatten sichtbar wird | ⚠ |
| 5 | Bildfragment muss wie ein Puzzle zusammengesetzt werden | ⌖ |
| 6 | Mathematischer Code, der Fibonacci-Reihen nutzt | ⚠ |
| 7 | Mehrstufiges Klangrätsel löst geheime Tür | ✱ |
| 8 | Subtile chemische Reaktion verrät den Code | ✱ |
| 9 | Zeitscheiben-Schalter koordiniert drei 5s-Fenster – Soft Fail Alarm 1 | ✱ |
| 10 | Karbid-Kryptograph – Kryokammer öffnen via Magnetfeldanalyse, Telekinese oder Überreden | ⚠ |

Die SL kann eigene Schwierigkeitsgrade festlegen. Die Tags dienen als
schnelle Orientierung im Mission-Generator.

## Temporale Anomalien-Generator (optional) {#anomalien-generator}

Dieser Abschnitt ist nur relevant, wenn die Runde gezielt temporale Störungen untersuchen möchte.
Für einen Agenten-Thriller sollten solche Effekte sparsam eingesetzt werden.

Zeitreisen gehen selten ohne Nebenwirkungen vonstatten. Jede Sprungsequenz
belastet das Raumzeit-Kontinuum. Nach **1000** vollzogenen Zeitsprüngen
tritt automatisch **eine** der folgenden Anomalien auf – unabhängig davon,
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
   Ereignisses erscheinen – Konturen eines Gebäudes oder Gesprächsfetzen,
   die nur Sensoren erfassen. Diese Hinweise können warnen oder täuschen.
5. **Zeitschmiede:** Eine Maschine hält einen Riss offen und produziert
   Zeit-Klone oder Artefakte aus alternativen Zukünften. Die Chrononauten
   müssen entscheiden, ob sie die Schmiede zerstören oder kontrolliert
   nutzen.
6. **Paradoxon-Loop:** Die Gruppe bemerkt, dass sie in einer Zeitschleife
   gefangen ist. Nur ein drastischer Schritt – eine zuvor getroffene
   Entscheidung rückgängig machen oder einen von ihnen temporär aus der
   Existenz nehmen – durchbricht den Loop.

Temporale Anomalien sind seltene, aber eindrucksvolle Ereignisse. Setzt sie
sparsam ein, um Spannung, Staunen oder Dringlichkeit zu erzeugen.
## Minor-Anomalien (d6) {#minor-anomalien}

| Wurf | Effekt (1 min) |
| ---- | -------------- |
| 1 | Rostpartikel fliegen rückwärts an Metall. |
| 2 | Uhrenschläge doppelt so schnell. |
| 3 | Haare der Agenten stellen sich elektrostatisch auf. |
| 4 | Gravitation lokal −5 %. |
| 5 | Starker Kupfergeruch. |
| 6 | Zwei Sekunden absolute Stille. |

## Historische Anomalien-Generator {#anomalie_realhistory}

Dieser Patch liefert konkrete Eingriffe in den Verlauf realer Geschichte.
Jeder Block lässt sich direkt in den Mission Seed kopieren.

```yaml
phase: Core
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
  methode: Hackt Serpukhov-15 Datenbus
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

| id | jahr | ort | puzzle | solution | reward |
| -- | ---- | --- | ------ | -------- | ------ |
| 7  | 1888 | London | 5 Drähte, 3 Enden -> Morsecode. | B-G-R-G-S = "SEAL" | Schaltschrank offen, +1 Info |
| 8  | 1906 | Istanbul | Num-Kalligrafie zeigt Versmaß aus "Divan-i Hafez". | 2358 | Artefakt-Zugang, Stress –2 |
| 9  | 1911 | Agadir | Drei falsche Schiffsrouten ergeben ein Dreieck. | 30°25′N 09°36′W | Feindliches Depot entdeckt |
| 10 | 1983 | Moskau | XOR-Lochkarten-Uhrzeiten. | Karte 17 -> 101100 | Countdown gestoppt, Paradoxon –1 |
| 11 | Frühmittelalter | Runen‑Stele | Ringstein mit 16 Runen | Sternkarte richten, Fach öffnet | Fehler: Pfeilfalle |
| 12 | Spätantike | Hydr.Orgel | V/W-Kammern | Wasser angleichen, Pins lösen, Tür auf | Überdruck flutet Kammer |
| 13 | Viktorianisch | Zahnrad-Panel | 12 Messingräder, verschieden | Fibo-Reihenfolge | Kurzschluss: Dunkel 10 Min |
| 14 | Near-Future | QC-Vault | Holozahlen in Superpos. | Seq. kollabieren, Primzahlen bleiben | Fehler: EMP-Burst |
*© 2025 pchospital – private use only. See LICENSE.
