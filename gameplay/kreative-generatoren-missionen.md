---
title: "ZEITRISS 4.2.0 – Modul 8A: Kreative Generatoren – Missionen"
version: 4.2.0
tags: [gameplay]
---

# ZEITRISS 4.2.0 – Modul 8A: **Kreative Generatoren – Missionen**

```yaml
arc_generator_default: true
setting_lock: true
sg_rift_bonus: 1
```

Schwellenangaben nutzen im Template den Platzhalter `{{SG_AUTO}}`.

Core-Seeds tragen nun optionale Felder zur Arc-Steuerung:

```yaml
- arc_id: "Chicago1871"
  arc_step: 1    # 1..10
  pool: heist_pool
```
## Gameplay-Index

Dieses Modul 8A knüpft an Modul 6 an; ein geplanter siebter Teil entfiel.

### Missions-Werkzeuge

- Automatischer Mission Seed: Sofort-Briefing
- Missionstabellen für den Core- & Rift-Loop
- Missions-Generator: Kleine Aufträge und Dilemmata

### Kampagnen-Werkzeuge

- Arc-Generator: Große Missionen
- Historische Wendepunkte-Generator: Auslöser und Folgen
- Random-Epochen-Generator: Wann und wo?

Auch der beste Spielleiter kann nicht jede mögliche Idee der Spieler vorausplanen – vor allem nicht
im offenen Sandkasten-Spiel. Hier kommen **kreative Generatoren** ins Spiel: strukturierte
Zufallstabellen oder Ideensammlungen, die mit wenigen Würfen oder Stichworten frische Einfälle
liefern. GPT als KI-Spielleiter hat den Vorteil, riesiges Wissen parat zu haben; dennoch ist es
hilfreich, ihm klare Vorgaben zu geben, was für einen Inhalt man gerade braucht. Die folgenden
Generatoren dienen als Starthilfe für improvisierte Orte, Charaktere, Missionen und Kuriositäten.
Ihr könnt sie klassisch per Würfel nutzen (z. B. W6 oder W20) oder frei nach Gefühl auswählen – je
nachdem, was zur Situation passt.

_Hinweis:_ Diese Generatoren sind ausdrücklich erweiterbar und anpassbar. Ihr könnt eigene Einträge
ergänzen oder die Tabellen auf eure Kampagne zuschneiden. Sie sollen vor allem zeigen, wie man mit
ein paar Schlagworten einen ganzen Kosmos an Ideen entfesselt. GPT kann aus diesen Stichpunkten
detaillierte Beschreibungen, NSC-Porträts oder Plothooks entwickeln. Also nutzt sie, um euer
ZEITRISS-Abenteuer bunt und lebendig zu halten!


Alle Tabellen gehen davon aus, dass scheinbar übernatürliche Ereignisse
auf Technologie, Psi oder Zeitphänomene zurückführen sind.
Ein "Teufel" im Mittelalter entpuppt sich möglicherweise als holografischer Schrecken
oder als Mutant aus einer anderen Epoche.
Dieses Motiv zieht sich durch alle Generatoreinträge
und kann als Faustregel dienen, wenn keine eigene Erklärung parat ist.
- Sitzungsstart → Automatischer Mission Seed
- Core-Missionen → `CoreObjectiveTable`
- Rift-Missionen → `RiftSeedTable` (durch den Paradoxon-Index erweitert)
- Nebenaufträge → Missions-Generator
- Große Handlungsbögen → Arc-Generator und Historische Wendepunkte
- Historische Settings → Random-Epochen-Generator
- Spontane NSCs und Gegner → NSC- & Kreaturen-Generator
- Stimmung & Loot → Artefakte und Kulturfragmente
- Seltene Effekte → Temporale Anomalien

## Missionsstruktur (Taktische Vorlage)

Eine Operation gliedert sich in sechs Phasen:
Briefing, Infiltration, Kontakt/Intel, Konflikt, Exfiltration und Debrief.
Rechnet mit 10–14 Szenen, je nach Einsatzart.
Die Gegenseite agiert mit greifbaren Agenten oder Söldnern.
Bonusziele wie Festnahmen oder gesicherte Datenträger bringen zusätzliche CU oder Ruf.
### 14-Step Mission Template
| # | Phase | Zweck |
|---|-------|------|
| 1 | Briefing | Auftrag erhalten |
| 2 | Anreise | Sprung oder Reise |
| 3 | Auftakt | Lage sondieren |
| 4 | Infiltration | Zugang schaffen |
| 5 | Kontakt | Info beschaffen |
| 6 | Vorbereitung | Ausrüstung prüfen |
| 7 | Konflikt I | erster Gegnerkontakt |
| 8 | Intel Twist | unerwartete Wendung |
| 9 | Konflikt II | Haupthindernis |
|10 | Sicherung | Zielobjekt greifen |
|11 | Flucht | Exfiltration beginnen |
|12 | Verfolgung | Gegner setzt nach |
|13 | Abschluss | Rücksprung |
|14 | Debrief | Belohnung auszahlen |
### Mission Economy
| Ergebnis | CU-Basis |
|----------|---------|
| Teil-Erfolg | 300 |
| Erfolg | 500 |
| Erfolg + Bonus | 600 |

## Automatischer Mission Seed

Dieses Start-Tool zieht zu Beginn einer Sitzung je einen Eintrag aus drei Listen
und kombiniert sie zu einem knappen Briefing. GPT würfelt verdeckt und stellt das Ergebnis vor.
Bei der Umsetzung orientiert sich die KI an der **Briefing-Vorlage (Layered)**
aus dem Toolkit: Zeit & Ort, eine mögliche Abnormalität und die Risikostufe werden
im ersten Briefing genannt. **Der gezogene Twist bleibt vorerst geheim** und dient
als Notiz für den Spielleiter, bis im Laufe der Mission passende Hinweise auftauchen.
Ein optionaler **Tonal-Safety-Toggle** filtert extrem düstere oder humorige Seeds
heraus, falls die Gruppe einen einheitlichen Stil bevorzugt.

> **Preserve** schützt Beinahe-Katastrophen,
> **Trigger** erzwingt historisch belegte Tragödien.
> Die Generatoren halten separate Pools, damit sich die Szenarien nicht überlappen.
> Alle Twists beziehen sich auf **Nicht-ITI-Fraktionen** (siehe `kampagnenuebersicht.md`).

```yaml
preserve_pool:
  - id: "P-0001"
    year: 1962
    place: "Kuba"
    title: "Able Archer Nuclear Scare"
    objective: "Sorge, dass UdSSR-Frühwarnung NATO-Übung nicht als Erstschlag wertet."
    antagonist: null
    antagonist_goal: null
    twist: "KGB-Chrononaut will Launch-Codes manipulieren."
  - id: "P-0002"
    year: 1979
    place: "BRD Elbe"
    title: "Ventilblockage E-79"
    objective: "Verhindere Kühlmittelverlust in Reaktorblock B."
    antagonist: null
    antagonist_goal: null
    twist: "Zukunfts-Ökozelle will Beweis für Atomgefahr erzwingen."
  - id: "P-0003"
    year: 1995
    place: "Barentssee"
    title: "Norway Rocket Alert"
    objective: "Halte Jelzins Atomkoffer geschlossen – Fehlsignal darf nicht eskalieren."
    antagonist: null
    antagonist_goal: null
    twist: "Abtrünniger NATO-Tech setzt falsche Telemetrie."
  - id: "P-0004"
    year: 2000
    place: "Sydney"
    title: "Olympics Bio-Plot"
    objective: "Stoppe Milzbrandanschlag im Versorgungstunnel."
    antagonist: null
    antagonist_goal: null
    twist: "Gegenspieler hat Virus im Maskottchen-Plush versteckt."
  - id: "P-0005"
    year: 2001
    place: "Genf"
    title: "CERN Magnet Quench"
    objective: "Stabilisiere Magneten, verhindere Vakuum-Implosion."
    antagonist: null
    antagonist_goal: null
    twist: "Nano-Sabotage von Zeitkartell platziert."
  - id: "P-0006"
    year: 2003
    place: "Nordatlantik"
    title: "Near-Collision AC759"
    objective: "Lenke zwei Flugrouten auseinander (TCAS-Glitch)."
    antagonist: null
    antagonist_goal: null
    twist: "Fremdfraktion stört Lotsen per Funk."
  - id: "P-0007"
    year: 2009
    place: "Hudson River"
    title: "US 1549 Ditching"
    objective: "Sicherstelle, dass Crew den Gleitflug zur Wasserung durchzieht."
    antagonist: null
    antagonist_goal: null
    twist: "KonTra-Fraktion will Rettungsschlepper sabotieren."
  - id: "P-0008"
    year: 2013
    place: "Fukushima"
    title: "Post-Leak Heat Spike"
    objective: "Vermeide sekundäre Wasserstoff-Explosion."
    antagonist: null
    antagonist_goal: null
    twist: "Schurken-Agent dreht Kühlpumpen ab."
  - id: "P-0009"
    year: 2014
    place: "Schweiz"
    title: "Gotthard Tunnel Fire"
    objective: "Lösche Brand, bevor Munitionslaster detoniert."
    antagonist: null
    antagonist_goal: null
    twist: "Saboteur tarnt sich als Feuerwehrmann."
  - id: "P-0010"
    year: 2016
    place: "Moskau"
    title: "Domodedowo Near-Strike"
    objective: "Umleite Drohne vom Jet-Triebwerk ab."
    antagonist: null
    antagonist_goal: null
    twist: "Neo-Fraktion testet Time-Beacon."
  - id: "P-0011"
    year: 1960
    place: "Karibik"
    title: "Black Saturday"
    objective: "Funkspruch von B-59-Sub unterdrücken – kein Torpedo-Launch."
    antagonist: null
    antagonist_goal: null
    twist: "Abgehörter Morse-Code wird gefälscht."
  - id: "P-0012"
    year: 1980
    place: "Vologda"
    title: "Oko False Alarm"
    objective: "Stütze Oberst Petrow bei Fehlalarm-Entscheidung."
    antagonist: null
    antagonist_goal: null
    twist: "Zeitanomalie flackert Satelliten-Sensor."
  - id: "P-0013"
    year: 1977
    place: "Leningrad"
    title: "Dam Safety Drill"
    objective: "Verhindere Defekt am Sankt-Petersburg-Tidenwehr."
    antagonist: null
    antagonist_goal: null
    twist: "Saboteur flutet Hydraulik mit Mikro-Algen."
  - id: "P-0014"
    year: 1987
    place: "Chicago"
    title: "Metra Bridge Collapse"
    objective: "Stabilisiere Träger, verhindere Zugabsturz."
    antagonist: null
    antagonist_goal: null
    twist: "Chrono-Rebellen testen Material-Fatigue-Gun."
  - id: "P-0015"
    year: 1991
    place: "Manila"
    title: "Pinatubo Lahar"
    objective: "Evakuiere Tiefland vor Schlammlawine."
    antagonist: null
    antagonist_goal: null
    twist: "Rival nutzt Wettersat-Hack für Fehlauswertung."
  - id: "P-0016"
    year: 2007
    place: "Genf"
    title: "SwissAir Fuel Leak"
    objective: "Versenke Austritt im Vorfeld, verhindere Start."
    antagonist: null
    antagonist_goal: null
    twist: "Gegenspieler hat Nano-Bohrer."
  - id: "P-0017"
    year: 1943
    place: "London"
    title: "V-Bomb DUD"
    objective: "Stelle Sicherung defekter V-1 wieder her – Blindgänger darf nicht detonieren."
    antagonist: null
    antagonist_goal: null
    twist: "Zeit-Dieb will Steuerservos klauen."
  - id: "P-0018"
    year: 1968
    place: "Thule"
    title: "Broken Arrow Ice"
    objective: "Stoppe Plutoniumstaubverwehung nach B-52-Crash."
    antagonist: null
    antagonist_goal: null
    twist: "Chrono-Smuggler will isotopen Beweis stehlen."
  - id: "P-0019"
    year: 1989
    place: "Montreal"
    title: "Hydro-Québec Blackout"
    objective: "Stütze Stromnetz gegen geomagnetischen Sturm."
    antagonist: null
    antagonist_goal: null
    twist: "Solar-Max Boost durch Zeitspule."
  - id: "P-0020"
    year: 2012
    place: "CERN"
    title: "LS1 Magnet Quench"
    objective: "Verhindere Quench-Kaskade im LHC-Ring."
    antagonist: null
    antagonist_goal: null
    twist: "Saboteur tauscht Helium-Sensor-Firmware."
  - id: "P-0021"
    year: 1971
    place: "Utah"
    title: "Apollo 15 Abort Call"
    objective: "Übermittle korrigierte Guidance-Daten – Landung darf nicht scheitern."
    antagonist: null
    antagonist_goal: null
    twist: "Antagonist stört Deep-Space-Net."
  - id: "P-0023"
    year: 1972
    place: "München"
    title: "Olympia Bomb Scare"
    objective: "Entschärfe zweite Bombe im Olympiastadion."
    antagonist: null
    antagonist_goal: null
    twist: "Chrono-Cell lockt Security weg."
  - id: "P-0024"
    year: 1983
    place: "Kapstadt"
    title: "Cape Town Chlorine Leak"
    objective: "Schließe Ventil, verhindere Gaswolke."
    antagonist: null
    antagonist_goal: null
    twist: "Saboteur mit Zeit-Maske als Ingenieur."
  - id: "P-0025"
    year: 2014
    place: "Jakarta"
    title: "QZ8501 Stall"
    objective: "Übermittle AoA-Reset-Routine an Piloten."
    antagonist: null
    antagonist_goal: null
    twist: "Gestohlene Sensoren liefern Falschmeldungen."
  - id: "P-0026"
    year: 1978
    place: "Soweto"
    title: "Dam Burst Near-Miss"
    objective: "Stütze Flutwehr."
    antagonist: null
    antagonist_goal: null
    twist: "Engineer ist Chrono-Konvertit."
  - id: "P-0027"
    year: 2008
    place: "Large Hadron Test"
    title: "Cryo-Line Crack"
    objective: "Seal crack, avert helium vent."
    antagonist: null
    antagonist_goal: null
    twist: "Rival will Mikro-Black-Hole Beweis."
  - id: "P-0028"
    year: 1999
    place: "Y2K"
    title: "Bank Core Patch"
    objective: "Installiere richtigen Millenniums-Patch."
    antagonist: null
    antagonist_goal: null
    twist: "Zeit-Cult löscht Backup-Tape."
  - id: "P-0029"
    year: 2019
    place: "Moskau"
    title: "Radiological Isotope Fire"
    objective: "Kühle Lager, verhindere Strahlungswolke."
    antagonist: null
    antagonist_goal: null
    twist: "Gegenseite will isotopen Diebstahl."
  - id: "P-0030"
    year: 1956
    place: "London"
    title: "Tower Bridge Near-Collapse"
    objective: "Entlaste Hängekabel vor Resonanz."
    antagonist: null
    antagonist_goal: null
    twist: "Chrono-Gambler setzt auf Einsturz-Wette."

> Alle Twists im folgenden Trigger-Pool stammen von **Nicht-ITI-Fraktionen**.
trigger_pool:
  - id: "T-0001"
    year: 1986
    place: "Ukraine"
    title: "RBMK Turbine Test"
    objective: "Stelle sicher, dass Reaktor 4 während Nachtprobe destabilisiert."
    antagonist: null
    antagonist_goal: null
    twist: "Zelle einer Fremdfraktion versucht SCRAM früh."
  - id: "T-0002"
    year: 2003
    place: "USA Orbit"
    title: "STS-107 Re-Entry"
    objective: "Blockiere EVA-Inspection, Shuttle muss verglühen."
    antagonist: null
    antagonist_goal: null
    twist: "Helios-Techniker im MCC Houston will außerplanmäßigen Check erzwingen."
  - id: "T-0003"
    year: 1912
    place: "Nordatlantik"
    title: "RMS Titanic"
    objective: "Sabotiere Funk, verhindere Warnung vor Eisfeld."
    antagonist: null
    antagonist_goal: null
    twist: "Zeit-Philanthrop will Kurs ändern."
  - id: "T-0004"
    year: 1975
    place: "China"
    title: "Banqiao Dam Burst"
    objective: "Schwäche Abfluss-Schotten während Taifun."
    antagonist: null
    antagonist_goal: null
    twist: "Spione einer Fremdfraktion wollen Entlastungswehr öffnen."
  - id: "T-0005"
    year: 1961
    place: "Kongo"
    title: "Lumumba Death"
    objective: "Entferne Schutzkonvoi, Übergabe an Gegner."
    antagonist: null
    antagonist_goal: null
    twist: "Diplomat einer Fremdfraktion liefert Fluchtplan."
  - id: "T-0006"
    year: 1994
    place: "Rwanda"
    title: "Presidential Crash"
    objective: "Blockiere Flughafen-Radar VHF."
    antagonist: null
    antagonist_goal: null
    twist: "UN-Team einer Fremdfraktion versuchen Wartungs-Override."
  - id: "T-0007"
    year: 1979
    place: "USA"
    title: "Three Mile Island"
    objective: "Unterdrücke Level-Indicator Alarm."
    antagonist: null
    antagonist_goal: null
    twist: "Gegenseite will Vent-Purge erzwingen."
  - id: "T-0008"
    year: 1937
    place: "Lakehurst"
    title: "Hindenburg"
    objective: "Sabotiere Bodenkabel-Erdung."
    antagonist: null
    antagonist_goal: null
    twist: "Ein Agent einer Fremdfraktion streut Anti-Elektrostatik-Graffiti."
  - id: "T-0009"
    year: 1989
    place: "Exxon Valdez"
    title: "Bligh Reef Spill"
    objective: "Besteche Hafenlotse – Tanker läuft auf Riff."
    antagonist: null
    antagonist_goal: null
    twist: "Öko-Gruppierung will Radar-Ping aktivieren."
  - id: "T-0010"
    year: 2011
    place: "Japan"
    title: "Fukushima Daiichi"
    objective: "Verzögere Diesel-Pump-Restart."
    antagonist: null
    antagonist_goal: null
    twist: "Rival will Not-Batterien liefern."
  - id: "T-0011"
    year: 1906
    place: "San Francisco"
    title: "Great Quake Fire"
    objective: "Manipuliere Hauptwasserventile, Brand breitet sich."
    antagonist: null
    antagonist_goal: null
    twist: "Feuerwehrfraktion bringt Steam-Pumper."
  - id: "T-0012"
    year: 2020
    place: "Beirut"
    title: "Ammonium Blast"
    objective: "Unterbinde Lagerräumung."
    antagonist: null
    antagonist_goal: null
    twist: "Hafeninspektor ist Fremdfraktions-Asset."
  - id: "T-0013"
    year: 2014
    place: "Donetsk"
    title: "MH17 Shootdown"
    objective: "Leite Kurs über Konfliktzone."
    antagonist: null
    antagonist_goal: null
    twist: "Air-Traffic-Controller will Umflug genehmigen."
  - id: "T-0014"
    year: 1988
    place: "Lockerbie"
    title: "PA103 Bomb"
    objective: "Schleuse Koffer unbehelligt ein."
    antagonist: null
    antagonist_goal: null
    twist: "Baggage-Scanner arbeitet für Fremdfraktion."
  - id: "T-0015"
    year: 1815
    place: "Tambora"
    title: "Year Without Summer"
    objective: "Fördere Schachtdruck, stärke Ausbruch."
    antagonist: null
    antagonist_goal: null
    twist: "Agent einer Fremdfraktion will Schuttkegel sprengen."
  - id: "T-0016"
    year: 1835
    place: "Rangoon"
    title: "Ava Earthquake"
    objective: "Sabotiere Evakuierungsbrücken."
    antagonist: null
    antagonist_goal: null
    twist: "Mönch (Fremdfraktion) warnt Bevölkerung."
  - id: "T-0017"
    year: 1883
    place: "Krakatau"
    title: "Volcanic Winter"
    objective: "Verzögere Telegraph-Warnung zu evakuieren."
    antagonist: null
    antagonist_goal: null
    twist: "Dutch-Telegraphist ist Scout einer Fremdfraktion."
  - id: "T-0018"
    year: 1918
    place: "Boston"
    title: "Molasses Flood"
    objective: "Erwärme Tank klandestin."
    antagonist: null
    antagonist_goal: null
    twist: "Food-Agent einer Fremdfraktion will Druckventil bohren."
  - id: "T-0019"
    year: 1923
    place: "Tokyo"
    title: "Great Kanto Quake"
    objective: "Blockiere Löschwasserleitung."
    antagonist: null
    antagonist_goal: null
    twist: "Spione einer Fremdfraktion hacken Brunnenpumpen."
  - id: "T-0020"
    year: 1978
    place: "Jonestown"
    title: "Mass Suicide"
    objective: "Sabotiere Funkgerät, verhindere Alarm."
    antagonist: null
    antagonist_goal: null
    twist: "Journalisten einer Fremdfraktion senden Hilferuf."
  - id: "T-0021"
    year: 1966
    place: "Aberfan"
    title: "Tip Slide"
    objective: "Schwäche Abraumdamm, Sturm erledigt Rest."
    antagonist: null
    antagonist_goal: null
    twist: "Lehrerin (Fremdfraktion) meldet Risse."
  - id: "T-0022"
    year: 1985
    place: "Nevado del Ruiz"
    title: "Armero Tragedy"
    objective: "Manipuliere Seismo-Alarm."
    antagonist: null
    antagonist_goal: null
    twist: "Priester (Fremdfraktion) versucht Evakuierung."
  - id: "T-0023"
    year: 1999
    place: "İzmit"
    title: "Marmara Quake"
    objective: "Verzögere Katastrophenschutz-Konvoi."
    antagonist: null
    antagonist_goal: null
    twist: "NGO-Fremdfraktion verteilt Boot-Sirenen."
  - id: "T-0024"
    year: 1971
    place: "Sylmar"
    title: "San Fernando Quake"
    objective: "Drehe Ventile für Gasleitungen auf."
    antagonist: null
    antagonist_goal: null
    twist: "Notfall-Crew einer Fremdfraktion hackt Shut-Off."
  - id: "T-0025"
    year: 1988
    place: "Yazd"
    title: "Iran Air 655"
    objective: "Jam IFF-System."
    antagonist: null
    antagonist_goal: null
    twist: "Radar-Tech (Fremdfraktion) sendet korrekten Code."
  - id: "T-0026"
    year: 2004
    place: "Phuket"
    title: "Boxing-Day Tsunami"
    objective: "Sabotiere Frühwarnboje."
    antagonist: null
    antagonist_goal: null
    twist: "Ozeanische Fremdfraktion wartet Sensor kurz vor Impakt."
  - id: "T-0027"
    year: 1963
    place: "Vajont"
    title: "Wave over Dam"
    objective: "Manipuliere Bergrutsch-Sprengbohrungen."
    antagonist: null
    antagonist_goal: null
    twist: "Geologin einer Fremdfraktion unterschlägt Daten."
  - id: "T-0028"
    year: 1964
    place: "Alaska"
    title: "Good Friday Quake"
    objective: "Verzögere Hafen-Evakuierung."
    antagonist: null
    antagonist_goal: null
    twist: "Fischer einer Fremdfraktion sendet Morsecode."
  - id: "T-0029"
    year: 2013
    place: "Lac-Mégantic"
    title: "Crude Oil Train"
    objective: "Bremse lösen, Zug rollt."
    antagonist: null
    antagonist_goal: null
    twist: "Switchman einer Fremdfraktion legt Keil."
  - id: "T-0030"
    year: 2001
    place: "New York"
    title: "9/11"
    objective: "Sichere Boarding für Entführer & stalle NORAD-Reaktion."
    antagonist: null
    antagonist_goal: null
    twist: "Air-Marshal einer Fremdfraktion sitzt falschen Flug."

  - id: "T-0031"
    year: 1995
    place: "Seoul"
    title: "Sampoong Collapse"
    objective: "Sabotiere Evakuierung – Einsturz muss erfolgen."
    antagonist: null
    antagonist_goal: null
    twist: "Aktien-Short-Spekulanten warnen vor der Instabilität."

```

Der anschließende Missionsgenerator erstellt eine **Phasenliste** mit
mindestens **30** Einträgen. Bei langen Einsätzen darf die Liste bis zu
**50** Szenen umfassen. Nutzt YAML‑Gewichte, um Nebenszenen aufzufüllen
und so das Ziel zu erreichen.

_Regel:_ Eintragstexte dürfen nicht wortgleich in `objective` und `twist` stehen.
Streiche doppelte Seeds oder variiere sie.

```jsonc
{
    "twists": [
      {
        "id": "T28",
        "label": "Schallmauer-Poker",
        "effect": "Ein Düsenjäger-Testflug droht eure Infiltration zu übertönen – perfekte Tarnung oder Absturztimer?"
      },
      {
        "id": "T29",
        "label": "Parallel-Konklave",
        "effect": "Ein Doppelgänger-Team taucht auf – gleiche Ziele, andere Agenda. Rivalen, Söldner oder Backup?"
      },
      {
        "id": "T30",
        "label": "Rabies-X Outbreak",
        "effect": "Mutierte Tollwut in versiegelter Basis: Soldaten wie Zombies – Antiserum oder Flammenwerfer?"
      },
      {
        "id": "T31",
        "label": "Imperiale Schachfigur",
        "effect": "Figur wird Kronzeuge. Töten tabu, Manipulation kostet Paradox, Schutz macht euch zu Leibwächtern."
      },
      {
        "id": "T32",
        "label": "Kaltes Singularitätstor",
        "effect": "Gefrorener Energiepuls hält ein Mikro-Wurmloch offen – perfekter Schmuggelkanal oder tickende Uhr?"
      },
      {
        "id": "T33",
        "label": "Silencer-Protokoll",
        "effect": "HQ bricht ab, Codex schweigt. Ihr baut eine Funkboje – bis dahin analoges Hacking und Risiko."
      },
      {
        "id": "T34",
        "label": "Orchideen-Schlüssel",
        "effect": "Keramikblüte steuert VIP-Implantate. Richtige Frequenz: Loyalität, falsche: Herzstillstand."
      },
      {
        "id": "T35",
        "label": "Sturm ★ Delta",
        "effect": "Wetter-Array von 19XX eskaliert: Hurrikan springt von 0 auf Kategorie 5. Fail-Safe liegt im Auge."
      }
    ]
}
```

Bei Missionsbeginn notiert sich die SL den Twist.
Spätestens in **Phase 3 (Aufklärung)** sollte die Spielleitung einen Hinweis aus
dem Feld `foreshadow` einbauen, damit die Wendung nicht übersehen wird.

Die folgenden Tabellen speisen den Core- und Rift-Loop mit Missionszielen.

## Missionstabellen für den Core- & Rift-Loop

Diese Tabellen liefern Zufallsziele für reguläre Operationen und für Risse.

```json
{
  "CoreObjectiveTable": [
    {
      "Objective_P": "Sichere feindlichen Kommunikationsknoten für nachträgliche Code-Analyse",
      "Objective_T": "Leite Traffic um & hinterlasse interne Sabotagespur, damit Gegner sich selbst säubert"
    },
    {
      "Objective_P": "Bergung gestohlener Forschung im Originalzustand",
      "Objective_T": "Inszeniere Brand, aber extrahiere Mikrofilm zuvor für ITI"
    },
    {
      "Objective_P": "Schütze den Informanten bis zu seinem geplanten Gefängnis-Tod",
      "Objective_T": "Täusche Suizid, um Namen des Drahtziehers herauszupressen"
    },
    {
      "Objective_P": "Bewahre ChronTech-Prototyp im Archiv für spätere Patente",
      "Objective_T": "Extrahiere Schaltpläne und ersetze Gehäuse durch funktionslose Attrappe"
    },
    {
      "Objective_P": "Täusche Basisbesatzung, sammle Beweise",
      "Objective_T": "Sprenge Treibstofflager, um Beweise als \"Zufallsfund\" zu tarnen"
    }
  ]
}
```
Der SG einer Mission richtet sich allein nach der Anzahl offener Seeds. Jedes ☆ zählt als +1 SG.
```json
{
  "RiftSeedTable": [
    {
      "d24": 1,
      "Seed": "Feuerengel von Breslau",
      "Hook": "Reaktor-Drohne im Kohlekraftwerk – Sturm & Sicherung",
      "hiddenCause": "Zeitschatten eines abgestürzten Testflugzeugs"
    },
    {
      "d24": 2,
      "Seed": "Totenbrücke Chongqing",
      "Hook": "Zeitfeld-Bus – Entschärfung im Verkehrsstau",
      "hiddenCause": "verschwundener Tang-Dynastie-Tempel"
    },
    {
      "d24": 3,
      "Seed": "Schrecken von Whitehall",
      "Hook": "Statue springt – Rooftop-Chase, Magnet-Harpoon",
      "hiddenCause": "Paradoxe Rückkopplung königlicher Blutlinie"
    },
    {
      "d24": 4,
      "Seed": "Night Train 666",
      "Hook": "Führerloser Güterzug – Boarding & Blackbox",
      "hiddenCause": "Zeitanker einer verunglückten Lok 1912"
    },
    {
      "d24": 5,
      "Seed": "Mirage Over Sinai",
      "Hook": "Phantom-Bomber – Luftkampf, Quellcode hacken",
      "hiddenCause": "fehlgeschlagener Abschussbefehl im Rahmen des Able-Archer-Manövers"
    },
    {
      "d24": 6,
      "Seed": "Wolfsplage Dacia",
      "Hook": "Gen-Rudel – Vollmond-Dorf-Horror, Serum stehlen",
      "hiddenCause": "Lykan-Virus aus Zukunftslabor"
    },
    {
      "d24": 7,
      "Seed": "Project Götterdämmerung",
      "Hook": "Polar-Laser – Stealth-Sabotage Arctic Station",
      "hiddenCause": "Nazitek aktiviert unvollständiges Zeitportal"
    },
    {
      "d24": 8,
      "Seed": "Black Rain Vienna",
      "Hook": "Nano-Wolke 1666 – Alchemisten-Labor infiltrieren",
      "hiddenCause": "unerkanntes Nanotech der Renaissance"
    },
    {
      "d24": 9,
      "Seed": "Emerald Kraken",
      "Hook": "Tiefsee-Mech – Taucheinsatz, EMP-Minen",
      "hiddenCause": "versenktes Labor erzeugt Meeresportal"
    },
    {
      "d24": 10,
      "Seed": "Mars-Log #404",
      "Hook": "Habitat-Shift – EVA-Mission, Quanten-Key zurück",
      "hiddenCause": "gestrandete Kolonie sendet Notsignal durchs Zeitloch"
    },
    {
      "d24": 11,
      "Seed": "Nightcrawler",
      "Hook": "CCTV-Aufnahme – Tarnanzug aus Zukunft entkam",
      "hiddenCause": "gestohlene Prototyp-Rüstung aus 2120"
    },
    {
      "d24": 12,
      "Seed": "Sasquatch im Yukon",
      "Hook": "Bestie greift Trapper an – Fährte verfolgen",
      "hiddenCause": "Zeitriss entlässt Mutanten-Bären"
    },
    {
      "d24": 13,
      "Seed": "Mothman-Sichtung",
      "Hook": "Unheil über Brücke – Absturz bergen",
      "hiddenCause": "Bote aus paralleler Zukunft warnt vor Brückeneinsturz"
    },
    {
      "d24": 14,
      "Seed": "Blutorden",
      "Hook": "Opfer blutleer – Kult zerschlagen",
      "hiddenCause": "Zeitkult extrahiert Energie für Riss-Stabilisierung"
    },
    {
      "d24": 15,
      "Seed": "Diablos Katakomben",
      "Hook": "Dämonische Schreie – Artefakt zerstören",
      "hiddenCause": "versiegelter Psi-Kristall bricht wieder auf"
    },
    {
      "d24": 17,
      "Seed": "Totenbrücke",
      "Hook": "Bus erstarrt 15 min – Zeitfeld neutralisieren",
      "hiddenCause": "Fehlgeleiteter Chrono-Transmitter unter der Brücke"
    },
    {
      "d24": 18,
      "Seed": "Schrecken von Whitehall – PHANTOM",
      "Hook": "Löwe springt – Parkourjagd",
      "hiddenCause": "eingeschleuste Androiden testen Tarnsystem"
    },
    {
      "d24": 19,
      "Seed": "Night Train 666 – PHANTOM",
      "Hook": "Geisterzug – Zug entern",
      "hiddenCause": "verschollener Prototyp mit permanenter Zeitschleife"
    },
    {
      "d24": 20,
      "Seed": "Emerald Kraken – PHANTOM",
      "Hook": "Grüne Tentakel – Taucheinsatz",
      "hiddenCause": "mutierte Tiefsee-Drohnen sammeln Artefakte"
    },
    {
      "d24": 21,
      "Seed": "Militärischer Komplex",
      "Hook": "Tollwutvirus-Zombies eindämmen",
      "hiddenCause": "Biowaffen-Test aus dem Jahr 1954 läuft aus dem Ruder"
    },
    {
      "d24": 22,
      "Seed": "Mittelalterliche Katakomben",
      "Hook": "Der falsche Teufel – Illusion enttarnen",
      "hiddenCause": "Illusionsprojektor versteckt Forschungsbasis",
      "meta_introspection": true
    },
    {
      "d24": 23,
      "Seed": "Altes Schloss",
      "Hook": "Vampir-Experiment beenden",
      "hiddenCause": "Zeitreisende Biologen züchten Blutparasiten"
    },
    {
      "d24": 24,
      "Seed": "Geheime Tiefsee-Megacity",
      "Hook": "Ursprung des \"Blob\" stoppen",
      "hiddenCause": "abtrünnige KI manipuliert Gen-Pools im Ozean"
    }
  ]
}
```

## Missions-Generator: Kleine Aufträge und Dilemmata {#missions-generator}

Nicht jede Session ist ein großes Story-Kapitel – manchmal möchten die Spieler im freien Spiel einen
kurzen Auftrag angehen oder euer GPT improvisiert einen Nebenquest. Der Missions-Generator liefert
schnelle **Missionsideen** mit einem eingebauten Twist oder Dilemma, damit auch kleine Einsätze
dramatisch und interessant verlaufen.

### Load-out-Pack-Generator

| Pack | Inhalt | CU‐Preis |
|------|--------|---------|
| **Stealth‑Kit** | Chamäleon‑Overall, Geräuschdämpfer‑Set, Mini‑Holo‑Lockpick, Nano‑Kabel (20 m) | 950 CU |
| **Heavy‑Ops** | Smart‑Assault‑Rifle, Sub‑Derm‑Kevlar, Adren‑Shot ×2, Flash‑Charges ×3 | 1 350 CU |
| **Tech‑Recon** | Quanten‑Sniffer‑Rig, Drohne „Pixie“, EMP‑Patch ×2, Data‑Spike‑Protokoll | 1 100 CU |
*SL‑Tipp*: Jede zusätzliche Sonderausrüstung erhöht das Missionsbudget; nicht verwendete CU fließt in Belohnungen.

### Missionstypen

Diese Übersicht fasst die gängigen Einsatzarten zusammen. Der Schwerpunkt liegt auf realen
Schauplätzen, heimlichen Zugriffszielen und subtilen Zeitinterventionen. Artefakte tauchen nur
selten automatisch auf, vergleichbar mit legendären Funden. Spieler können ihr Auftreten nicht
gezielt beeinflussen. Die Missionstypen gliedern sich in fünf Kategorien:

- **Verschwinden** – Zielpersonen heimlich ausschalten oder entführen.
- **Einflüstern** – Einfluss auf NSCs durch Täuschung oder Manipulation.
- **Verdunkeln** – Spuren verwischen und Beweise stehlen.
- **Verhindern** – Anschläge, Putsche oder Deals stoppen.
- **Dokumentieren** – Geheime Beweise für das ITI sichern.

Frühere Beispielmissionen wurden zugunsten dieses flexiblen Baukastens gestrichen.
Kombiniert die Tabellen nach Belieben und erstellt eure eigenen Einsätze. Für
größere Handlungsbögen könnt ihr mehrere Aufträge verbinden oder den
[Arc-Baukasten](kampagnenstruktur.md#arc-baukasten-und-episodenstruktur) aus Modul 6
nutzen.

Wählt jeweils eine Option aus **Auftrag**, **Schauplatz** und **Twist**:

- **Auftrag:**

  1. Eskortiert/Schützt **X**.
  2. Rettet/Befreit **X**.
  3. Stehlt/Beschafft **X**.
  4. Zerstört/Sabotiert **X**.
  5. Erkundet/Untersucht **X**.
  6. Vermittelt/Verhandelt zwischen **X** und **Y**.

- **Schauplatz/Epoche:**

  1. Auf einem **Kriegsschauplatz** (Schlacht, Belagerung o. Ä.).
  2. An einem **Königshof** oder Regierungssitz.
  3. In einer **kleinen Ortschaft** oder Wildnis.
  4. In einem **Forschungslabor** oder einer Werkstatt.
  5. In einer **abgeschirmten Nullzone** fernab der regulären Zeit.
  6. Während eines bedeutenden **historischen Ereignisses** (Krönung, Attentat, Naturkatastrophe…).

- **Twist/Dilemma:**

  1. Jemand, den ihr schützen oder dem ihr helfen sollt, ist **nicht der, der er zu sein scheint** –
     und verrät euch vielleicht.
  2. Die **erfolgreiche Erfüllung** des Auftrags **verändert die Geschichte gefährlich** (Dilemma:
     Auftrag ausführen oder scheitern lassen?).

3. _Nicht mehr verfügbar:_ Selten eingesetzte Selbstbegegnungen wurden aus dem Twist-Pool gestrichen.
4. **Moralisches Dilemma:** Ihr könnt **nicht alle retten** oder zufriedenstellen – wen bevorzugt
   ihr, wen lasst ihr im Stich?
5. Der Auftrag wird **von einer rivalisierenden Gruppe** ebenfalls verfolgt – ein Wettlauf gegen
   konkurrierende Zeitreisende entbrennt.
6. Ein **temporales Phänomen** erschwert alles: Zeitstürme, Anachronismus-Erscheinungen etc.
   treten auf.


Direkte Begegnungen mit eigenen Versionen sind ein starker dramaturgischer
Kniff, aber kein Standardbestandteil des Spiels. Sie kommen nur zum Einsatz,
wenn alle Spieler dem ausdrücklich zustimmen, und selbst dann höchstens als
seltene Ausnahme. Oft genügt es, die Agenten an einen früheren Einsatzort
zurückkehren zu lassen, um dort Hinweise auf ihr zukünftiges Handeln zu finden –
ohne sich selbst unmittelbar zu treffen.

Ihr könnt natürlich alle Elemente nach Belieben kombinieren. Wichtig ist, dass fast **jeder Auftrag
mit einem Twist** deutlich interessanter wird. So werden selbst Nebenmissionen zu denkwürdigen
Episoden und nicht bloß „Hole X, bringe Y“.

**Optional – Belohnungs-Generator:** Ebenso könnt ihr auswürfeln oder wählen, welche **Belohnung
oder Konsequenz** eine Mission für die Helden bereithält (je nachdem, wie erfolgreich sie sind):

- **Belohnung/Ergebnis:**

  1. **Seltener Fund:** Die Gruppe erbeutet ein wertvolles Artefakt oder technisches Gerät
     (historisch oder futuristisch), das neue Möglichkeiten eröffnet.
  2. **Wissen & Aufklärung:** Durch den Auftrag erhalten sie entscheidende Informationen oder lüften
     ein Geheimnis, das im weiteren Verlauf der Kampagne hilft.
  3. **Ansehen & Verbündete:** Ihr Erfolg verschafft ihnen Ansehen und neue Alliierte – z. B.
     Dankbarkeit einer geretteten Person oder gar einer Fraktion (vielleicht winkt eine Beförderung im
     ITI oder ein Bündnis mit den Zeitrebellen von _Tempus Liber_).
  4. **Technologischer Vorteil:** Als Lohn stellt man ihnen neue Ausrüstung oder experimentelle
     Technik zur Verfügung (etwa ein verbessertes Zeitreise-Gadget oder Unterstützung durch das HQ).
  5. **Stabilisierte Zeit:** Ihr Eingreifen bewahrt den Verlauf der Geschichte und rettet
     Unschuldige – eine ideelle Belohnung. (Möglicherweise stellt sich sogar ein kleiner positiver
     Schmetterlingseffekt ein, der den Helden zugutekommt.)
  6. **Neue Erkenntnisse:** Anstatt reicher zu werden, stoßen sie auf einen Hinweis zu einem
     größeren Rätsel. Ihr Erfolg enthüllt den nächsten, noch größeren Auftrag – eine „Belohnung“ in Form
    eines neuen Abenteuers, das auf sie wartet.


### Generator Guard {#generator-guard}

```pseudo
# Pseudocode: passendes Pool ziehen
if mission_type == "preserve":
    seed = random.choice(preserve_pool)
else:
    seed = random.choice(trigger_pool)
```

## Arc-Generator: Große Missionen {#arc-generator}

Manchmal soll eine Mission mehr sein als ein kurzer Auftrag. Dieser Generator liefert Anregungen für
ganze Handlungsbögen. Kombiniert je einen Eintrag aus **Bedrohung**, **Schlüsselort** und
**Finale Wendung** und baut darum herum eure große Story.

Ein einzelnes historisches Ereignis lässt sich auch in mehrere Einsätze
aufteilen. Teilt eine Katastrophe chronologisch auf – zum Beispiel
Vorbereitungen, erster Angriff, Eskalation und Nachspiel. Jede Etappe bildet
eine Mission, sodass ein kompletter Arc zehn Szenenfolgen derselben
Zeitperiode umfasst.

- **Bedrohung:**

  1. Ein Megakonzern missbraucht Zeittechnologie für eigene Machtziele.
     - epochTag: "2080er MegaCorp-Krise"
     - historyHook: "nutzt die Wirtschaftskrise 2082 für verdeckte Übernahmen"
  2. Fanatische Kultisten wollen eine alternative Zeitlinie herbeiführen.
     - epochTag: "mittelalterlicher Aberglaube"
     - historyHook: "schürt Hexenpanik in Salem 1692"
  3. Ein außer Kontrolle geratenes Experiment droht die Realität zu zerreißen.
     - epochTag: "2030er Quantenlabors"
     - historyHook: "verbirgt eine Fehlkalibrierung im CERN 2035"
  4. Ein verstecktes Alienvolk plant, die Menschheit aus der Geschichte zu löschen.
     - epochTag: "präkolumbisches Südamerika"
     - historyHook: "manipuliert Inka-Sonnenkulte für Opferrituale"
  5. Ein rivalisierendes Zeitreise-Team sabotiert gezielt die Einsätze der Helden.
     - epochTag: "kalter Krieg"
     - historyHook: "tarnt sich als KGB-Sondereinheit 1960"
  6. Ein fehlgeschlagenes Zeitexperiment reißt ganze Regionen aus der Realität.
     - epochTag: "Cholera-Hysterie 1892 Hamburg"
     - historyHook: "lockt die Bevölkerung mit Heilversprechen in den Zeitriss"

- **Schlüsselort:**

  1. Geheimlabor in einem unterirdischen Komplex.
  2. Monumentale Ruinen einer vergangenen Hochkultur.
  3. Futuristische Metropole jenseits des bekannten Zeitalters.
  4. Verbotener Tempel, der in mehreren Epochen gleichzeitig existiert.
  5. Raumstation am Rand eines instabilen Zeittors.
  6. Verborgenes Hauptquartier der Gegenspieler mitten in der Gegenwart.

- **Finale Wendung:**

  1. Der scheinbare Verbündete entpuppt sich als Drahtzieher der Krise.
  2. Das Artefakt, das alles retten soll, verursacht erst recht Chaos.
  3. Die Helden müssen ein persönliches Opfer bringen, um die Zeit zu heilen.
  4. Eine andere Fraktion kommt ihnen zuvor und dreht den Spieß um.
  5. Die Mission führt zu einer komplett neuen Zeitlinie mit ungewissem Ausgang.
6. Die Helden erkennen, dass ihre Mission nur ein Ablenkungsmanöver für einen verborgenen Gegenspieler
    war.

### Heist Pool {#heist_pool}

```yaml
heist_pool:
  - safecrack_demo
  - tunnel_bypass
```

### Black-Ops Pool {#black_ops_pool}

```yaml
black_ops_pool:
  - night_insertion
  - asset_wipe
```

### Future Pool {#future_pool}

```yaml
future_pool:
  - zero_g_breach
  - orbital_hack
```

## Historische Wendepunkte-Generator: Auslöser und Folgen {#wendepunkte-generator}

Manchmal führt schon eine kleine Handlung dazu, dass ein bekanntes Ereignis
überhaupt erst stattfindet. Dieser Generator liefert Ansätze, wie die Chrononauten
unfreiwillig einen historischen Moment auslösen oder verhindern. Wählt eine
Kombination aus **Ereignis**, **Aktion** und **Konsequenz**:

1. **Ereignis:**
   1. Ein großes Unglück steht kurz bevor (z. B. eine Explosion oder ein Absturz).
   2. Ein gefeierter Durchbruch der Wissenschaft soll präsentiert werden.
   3. Eine wichtige Krönung oder Wahl entscheidet über den Lauf der Geschichte.
   4. Eine Revolution brodelt und sucht nur noch den Funken zur Entzündung.
   5. Ein visionärer Künstler ringt um die Fertigstellung seines Werkes.
   6. Ein geheimer Pakt zwischen Mächten soll unterzeichnet werden.
2. **Aktion der Agenten:**
   1. Sie bewahren eine Schlüsselfigur vor einem Attentat.
   2. Sie stehlen oder zerstören ein entscheidendes Dokument.
   3. Sie überzeugen einen Protagonisten, doch noch aufzutreten.
   4. Sie lenken einen Rivalen ab, wodurch eine Idee ungestört reifen kann.
   5. Sie decken eine Intrige auf und bringen sie an die Öffentlichkeit.
   6. Sie sabotieren ein Transportmittel oder ersetzen es unbemerkt.
3. **Konsequenz:**
   1. Das historische Ereignis findet nur dank ihres Eingreifens statt.
   2. Der Verlauf verändert sich subtil und führt zu einem bekannten Ergebnis.
   3. Ihr Eingreifen verhindert die Katastrophe – eine andere tritt an ihre Stelle.
   4. Eine Nebenfigur wird berühmt und beeinflusst später die Zeitlinie.
   5. Die Öffentlichkeit erfährt nichts; nur der Codex notiert die Veränderung.
   6. Eine Fraktion nutzt das Resultat heimlich für ihre eigenen Ziele.

Mit diesem Baukasten entstehen Missionen, bei denen die Agenten scheinbar nur
eine Kleinigkeit erledigen. Erst im Nachhinein erkennen sie, dass ihr Handeln den
geschichtlichen Wendepunkt überhaupt ermöglicht hat – oder dass sie ihn, ohne es
zu wollen, verhindert haben.

### Historische Anomalien: Trigger-Liste

Die folgende Tabelle liefert konkrete Ausgangssituationen. Jede Zeile benennt ein
historisch belegtes Ereignis, das in der ZEITRISS-Chronologie durch eine
Anomalie abweicht. **Vorphase** beschreibt den Moment knapp vor dem Auslöser,
**Nachphase** die Lage, sobald die Anomalie sich voll entfaltet. Wählt oder
würfelt einen Eintrag als Missionsstart.

1. **London 1666 – Großer Brand** \| Vorphase: Funken im Bäckerladen.
   \| Nachphase: Stadt steht in Flammen.
2. **Boston 1773 – Tea Party** \| Vorphase: Heimliche Treffen in Tavernen.
   \| Nachphase: Kisten treiben im Hafen.
3. **Paris 1789 – Sturm auf die Bastille** \| Vorphase: Gerüchte über Waffenlager.
   \| Nachphase: Aufgebrachte Menge stürmt das Gefängnis.
4. **New Orleans 1812 – Großer Brand** \| Vorphase: Kerzenstummel fällt um.
   \| Nachphase: Viertel lichterloh.
5. **Waterloo 1815 – Letzte Schlacht Napoleons** \| Vorphase: Verregnete Felder.
   \| Nachphase: Truppen brechen panisch.
6. **Berlin 1848 – Märzrevolution** \| Vorphase: Flugblätter im Umlauf.
   \| Nachphase: Barrikadenkämpfe.
7. **London 1851 – Great Exhibition** \| Vorphase: Weltneuheiten reisen an.
   \| Nachphase: Rivalen kämpfen um Erfindungen.
8. **Florenz 1867 – Laborunfall** \| Vorphase: Experimente mit Äthergas.
   \| Nachphase: Halle explodiert, Rauchschwaden.
9. **London 1888 – Letztes Opfer des Rippers** \| Vorphase: Polizei tappt im Dunkeln.
   \| Nachphase: Spur führt zu einem Zeitreisenden.
10. **Paris 1889 – Weltausstellung** \| Vorphase: Eiffelturm im Bau.
    \| Nachphase: Spione jagen neue Technik.
11. **Chicago 1893 – Weltausstellung** \| Vorphase: Besucher strömen herbei.
    \| Nachphase: Stromnetz bricht zusammen.
12. **Sankt Petersburg 1905 – Blutsonntag** \| Vorphase: Friedlicher Marsch.
    \| Nachphase: Soldaten schießen in die Menge.
13. **San Francisco 1906 – Erdbeben** \| Vorphase: Tiere verhalten sich unruhig.
    \| Nachphase: Stadtteile versinken in Flammen.
14. **Sarajevo 1914 – Attentat auf Franz Ferdinand** \| Vorphase: Autokolonne formiert sich.
    \| Nachphase: Europa steht vor dem Krieg.
15. **Galizien 1916 – Verschollenes U-Boot** \| Vorphase: Funkkontakt reißt ab.
    \| Nachphase: U-Boot taucht Jahre später wieder auf.
16. **New York 1929 – Börsencrash** \| Vorphase: Ungewöhnliche Kursausschläge.
    \| Nachphase: Broker geraten in Panik.
17. **Berlin 1936 – Olympische Spiele** \| Vorphase: Propagandashow läuft.
    \| Nachphase: Geheime Aufrüstung fliegt auf.
18. **Hindenburg 1937 – Zeppelin** \| Vorphase: Wartungstrupp meldet seltsamen Geruch.
    \| Nachphase: Luftschiff in Flammen.
19. **New York 1939 – World’s Fair** \| Vorphase: Futuristische Vorführungen.
    \| Nachphase: Tarnprojekt enttarnt.
20. **Los Alamos 1945 – Trinity-Test** \| Vorphase: Wissenschaftler diskutieren Risiken.
    \| Nachphase: Greller Blitz, Messgeräte spielen verrückt.
21. **Roswell 1947 – Absturz** \| Vorphase: Radarempfang gestört.
    \| Nachphase: Militär riegelt die Absturzstelle ab.
22. **Berlin 1961 – Mauerbau** \| Vorphase: Geheimtreffen der Führung.
    \| Nachphase: Straßen plötzlich blockiert.
23. **Dallas 1963 – Kennedy-Attentat** \| Vorphase: Wagenkolonne startet.
    \| Nachphase: Chaos auf der Dealey Plaza.
24. **Woodstock 1969 – Musikfestival** \| Vorphase: Technikprobleme auf der Bühne.
    \| Nachphase: Massen strömen unkontrolliert.
25. **Apollo 13 1970 – Raumflug** \| Vorphase: Routinefunksprüche.
    \| Nachphase: Funkspruch „Houston, we’ve had a problem“.
26. **Osaka 1970 – Expo ’70** \| Vorphase: Kalter Krieg mischt mit.
    \| Nachphase: Futuristische Show gerät außer Kontrolle.
27. **München 1972 – Olympia** \| Vorphase: Verdächtige sichten das Dorf.
    \| Nachphase: Geiselnahme und Belagerung.
28. **Three Mile Island 1979 – Reaktorstörung** \| Vorphase: Ventile melden Fehler.
    \| Nachphase: Kühlsystem versagt.
29. **Los Angeles 1984 – Olympisches Finale** \| Vorphase: Kameraübertragung flackert.
    \| Nachphase: Stromausfall im Stadion.
30. **Tschernobyl 1986 – Reaktor 4** \| Vorphase: Testlauf ohne Freigabe.
    \| Nachphase: Kernschmelze und Evakuierung.
31. **Berlin 1989 – Mauerfall** \| Vorphase: Verwirrte Meldungen in der Pressekonferenz.
    \| Nachphase: Menschenmassen reißen Mauern ein.
32. **Oslo 1991 – Friedensnobelpreis** \| Vorphase: Bewerberlisten manipuliert.
    \| Nachphase: Zeremonie endet im Skandal.
33. **Tokio 1995 – Sarin-Anschlag** \| Vorphase: U-Bahn voller Pendler.
    \| Nachphase: Giftgasalarm.
34. **Seattle 1999 – WTO-Proteste** \| Vorphase: Demonstranten sammeln sich.
    \| Nachphase: Straßenschlachten eskalieren.
35. **New York 2001 – 9/11** \| Vorphase: Flugzeuge weichen vom Kurs ab.
    \| Nachphase: Türme stürzen ein.
36. **Bagdad 2003 – Museumsplünderung** \| Vorphase: Chaos nach Einmarsch.
    \| Nachphase: Artefakte verschwunden.
37. **Jakarta 2004 – Tsunamiwarnung** \| Vorphase: Seismografen schlagen aus.
    \| Nachphase: Küsten verwüstet.
38. **Berlin 2006 – Stromausfall** \| Vorphase: Netzschwankungen.
    \| Nachphase: U-Bahnen bleiben stehen.
39. **Peking 2008 – Eröffnungsfeier** \| Vorphase: Wetterkontrolle testet Chemikalien.
    \| Nachphase: Künstlicher Regen setzt ein.
40. **Haiti 2010 – Erdbeben** \| Vorphase: Tiere fliehen ins Landesinnere.
    \| Nachphase: Hauptstadt in Trümmern.
41. **Fukushima 2011 – Tsunami trifft AKW** \| Vorphase: Notfallprotokolle aktiv.
    \| Nachphase: Strahlungswerte steigen.
42. **London 2012 – Olympia** \| Vorphase: Sicherheitsdrohnen patrouillieren.
    \| Nachphase: Drohnen spielen verrückt.
43. **Moskau 2013 – Meteorit** \| Vorphase: Himmelsleuchten.
    \| Nachphase: Druckwelle zerstört Fenster.
44. **Genf 2015 – Teilchenbeschleuniger** \| Vorphase: Magnetringe überhitzen.
    \| Nachphase: Zeitfenster blitzt kurz auf.
45. **Paris 2016 – Stromausfall im Louvre** \| Vorphase: Wartungsarbeiten am Netz.
    \| Nachphase: Kostbare Exponate verschwinden.
46. **Houston 2017 – Hurricane Harvey** \| Vorphase: Satellitenbilder zeigen extreme Wolkenbildung.
    \| Nachphase: Straßen überflutet.
47. **Bangkok 2018 – Höhlenrettung** \| Vorphase: Junge Fußballer erkunden Höhle.
    \| Nachphase: Monsunregen schneidet den Rückweg ab.
48. **Notre-Dame 2019 – Großbrand** \| Vorphase: Baugerüst wackelt.
    \| Nachphase: Dachstuhl in Flammen.
49. **Wuhan 2019 – High-Tech-Expo** \| Vorphase: Prototypen-Drohnen werden vorgestellt.
    \| Nachphase: Steuerung fällt aus, Drohnen stürzen ab.
50. **Beirut 2020 – Hafenexplosion** \| Vorphase: Rauch über Lagerhalle.
    \| Nachphase: Schockwelle legt Gebäude in Schutt.
51. **Tokio 2021 – Olympische Spiele** \| Vorphase: Experimentelles KI-Maskottchen begrüßt die Zuschauer.
    \| Nachphase: Fehlfunktion löst gefährliche Zwischenfälle aus.
52. **Glasgow 2021 – Klimagipfel** \| Vorphase: Aktivisten blockieren Straßen.
    \| Nachphase: Unerklärliche Stromsenke legt Viertel lahm.
53. **Texas 2022 – Stromnetz-Kollaps** \| Vorphase: Kälteeinbruch.
    \| Nachphase: Blackout und Versorgungsnotstand.
54. **Genf 2023 – KI-Konferenz** \| Vorphase: Prototype läuft heiß.
    \| Nachphase: Selbstlernende Drohne entweicht.
55. **Kapstadt 2024 – Wasserkrise** \| Vorphase: Reservoirs fast leer.
    \| Nachphase: Rationierung eskaliert Unruhen.
56. **Mars – Gesicht von Cydonia** \| Vorphase: Rover meldet mysteriöse Struktur.
    \| Nachphase: Basis gerät in Aufruhr.
57. **Phobos – Der Basilisk** \| Vorphase: Mission entdeckt Turm.
    \| Nachphase: Crew verliert Kontakt.
58. **Rückseite des Mondes – Die wahre Madonna** \| Vorphase: Crash-Signal wird geortet.
    \| Nachphase: Hybride Kreatur erwacht.
59. **Saturnmond Titan – Fremdes Leben** \| Vorphase: Sonden liefern seltsame Daten.
    \| Nachphase: Methanmeere brodeln.
60. **Antarktis – Versiegelte Anlagen** \| Vorphase: Bohrung stößt auf Metall.
    \| Nachphase: Alte Technologie erwacht.
61. **Kapustin Jar – Aktives Zeitportal** \| Vorphase: Testlauf steht bevor.

\| Nachphase: Portal reißt sich auf.
### Preserve-Liste (Near-Misses)
Siehe `preserve_pool` oben.

## Random-Epochen-Generator: Wann und wo? {#epochen-generator}

ZEITRISS-Missionen können prinzipiell in jeder Epoche der echten oder fiktiven Geschichte spielen.
Wenn ihr spontan ein neues Setting braucht oder die Spieler unerwartet irgendwo auftauchen, liefert
dieser Generator einen schnellen Rahmen. Er kombiniert einen **Zeitort** (Epoche/Setting) mit einem
markanten **Ereignis oder Konflikt**, das dort gerade passiert. Würfelt z. B. 1W6 für einen Zeitort
**und** 1W6 für ein besonderes Ereignis, oder nutzt eine der folgenden vordefinierten Kombinationen:

_Regel für die Kühlung der Epochengewichte:_
1. Notiere nach jedem Zufallswurf die gezogene Epoche als `last_epoch`.
2. Verringere ihr Gewicht in der Tabelle um den **Cooling-Wert** (Standard 0.05), jedoch nie unter 1 %.
3. Normiere anschließend alle Gewichte, sodass ihre Summe wieder 1 ergibt.
4. Würfle die nächste Epoche anhand der aktualisierten Wahrscheinlichkeiten.

1. **Steinzeitliche Wildnis** (ca. 10.000 v.Chr.) – _Setting:_ Weite prähistorische Landschaft mit
   Megafauna (Mammutherden, Säbelzahntiger) und nomadischen Stämmen. **Besonderheit:** Ein kleines Dorf
   ist in einer Zeitschleife gefangen: Jeden Morgen geht die Sonne nicht auf. Fackeln brennen ewig,
   Tiere wirken verwirrt. Höhlenmalereien deuten auf einen temporalen Meteor hin, der hier einst
   einschlug. Die Chrononauten müssen das prähistorische Paradox beheben, während misstrauische
   Schamanen und hungrige Bestien ihnen zusetzen.
2. **Ägyptisches Neues Reich** (1250 v.Chr.) – _Setting:_ Glühende Wüstensonne, monumentale Tempel
   und der Hof von Pharao Ramses II. **Besonderheit:** Im Verborgenen wird ein Alien-Artefakt in einer
   Pyramide verehrt, angeblich ein Geschenk der Götter. Tatsächlich stammt es aus der Zukunft und
   strahlt ungewöhnliche Energie ab. Die Agenten müssen entscheiden: Stehlen sie das Artefakt, um die
   Zeitlinie zu schützen – riskieren aber, die lokale Religion zu erschüttern? Oder lassen sie es in
   der Geschichte, mit unbekannten Folgen? Intrigante Hohepriester und ein misstrauischer Wesir machen
   jede Aktion zum Balanceakt.
3. **Mittelalterliche Hafenstadt** (14. Jh.) – _Setting:_ Hansekoggen im Hafen, geschäftiges
   Markttreiben, Tavernenlärm und abendrötliche Gassen. **Besonderheit:** Gerüchte gehen um von einem
   Geisterschiff, das bei Vollmond im Hafen erscheint und genauso plötzlich verschwindet. Eine
   temporale Erscheinung? Vielleicht ein Zeitschiff aus der Zukunft, das hier festsitzt. Die
   Chrononauten könnten in einen lokalen Machtkampf zwischen Gilden geraten (wer das “Wunder” für sich
   nutzen kann, gewinnt Ansehen), während sie das Geheimnis des Schiff-Geists lüften. Ist es ein
   Hilferuf aus einer anderen Zeit?
4. **Victorianisches London** (1888) – _Setting:_ Neblige Gassen, Kutschenräder auf
   Kopfsteinpflaster, flackernde Gaslaternen. Jack the Ripper treibt sein Unwesen. **Besonderheit:**
   Durch einen Zeitriss tauchen ab und zu Gestalten aus anderen Epochen in Whitechapel auf. Die
   Behörden schieben es auf Wahnsinn oder Verkleidungen. Die Helden müssen nicht nur den berüchtigten
   Ripper finden, sondern auch erklären, warum sein letztes Opfer ein römischer Gladiator war, der
   plötzlich in den Gassen stand. Ein grimmiger Zeitsprung-Krimi beginnt.
5. **Pazifik während des Zweiten Weltkriegs** (1942) – _Setting:_ Tropische Insel mit
   Militärstützpunkt, dröhnende Flugzeuge, Morse-Funk im Radio. **Besonderheit:** _Zeitkapsel-
   Konflikt:_ Auf der Insel erscheint ein Objekt aus der Zukunft – eine High-Tech-Drohne – und sowohl
   die Alliierten als auch die Achsenmächte bekommen Wind davon. Die Helden müssen verhindern, dass
   diese Technik den Krieg beeinflusst. Doch wem vertrauen sie vor Ort? Eine gefährliche Spionage-
   Mission, bei der sie vielleicht vorgeben müssen, für eine Seite zu arbeiten, um an die Drohne zu
   gelangen.
6. **Mars-Kolonie** (2097) – _Setting:_ Ein Habitat unter Kuppeln, rote Wüstenlandschaft draußen,
   futuristische Labore. **Besonderheit:** _Erster Kontakt_ – aber nicht mit Aliens, sondern mit
   Zeitreisenden: Die Mars-Siedler empfangen ein Signal von Menschen… aus dem Jahr 2300. Die
   Zukunftsmenschen sind gestrandet und flehen um Hilfe. Die Chrononauten müssen koordinieren, wie man
   diese temporale Notlage löst, ohne dass die fragile Mars-Gesellschaft des Jahres 2097 kollabiert
   (schon allein die Nachricht “die Mission wird aufgegeben werden” könnte Panik auslösen). Eine
   Episode voll Sci-Fi-Philosophie: Darf man Leuten aus der eigenen Zukunft helfen, wenn es bedeutet,
   dass man sein eigenes Schicksal kennt?

_Tipp:_ Ihr könnt natürlich jede Epoche und jedes Ereignis nach Belieben austauschen. Die obigen
sechs Kombinationen dienen vor allem als inspirierende Beispiele – z. B. **Steampunk-Paris 1889 +
ein Monster aus einem Zeitlabor** ergeben ebenfalls einen spannenden Schauplatz!
### Rift Seeds (automatisch)
Rifts erscheinen bei Paradoxon 5. Das HQ notiert sie hier als `phase: Rift` ohne Episodennummer.

```yaml
phase: Rift
jahr: 1889
ort: Prag
thema: Beispiel-Rift
```

### Core-Arc Seeds {#core-arc-seeds}

```yaml
- arc_id: "Chicago1871"
  arc_step: 1
  pool: heist_pool
  title: "Brandstifter-Trupp"
  pitch: "Legt Nitrobeschleuniger unter Mrs O’Learys Scheune, ohne Zeugen."
  timeslot: "+0 h"

- arc_id: "Chicago1871"
  arc_step: 2
  pool: heist_pool
  title: "Pumpen-Manipulation"
  pitch: "Sabotiert die Dampfpumpen der Südseite, damit das Feuer sich ungehindert ausbreitet."
  timeslot: "+1 h"

- arc_id: "Chicago1871"
  arc_step: 3
  pool: heist_pool
  title: "Raubzug beim Juwelier"
  pitch: "Stehlt Diamanten im Wert von 200.000 $, während die ersten Unruhen toben."
  timeslot: "+3 h"

- arc_id: "Chicago1871"
  arc_step: 4
  pool: heist_pool
  title: "Weichen-Heist"
  pitch: "Leitet den einzigen Wasserzug um, indem ihr den Stellwerksturm übernehmt."
  timeslot: "+6 h"

- arc_id: "Chicago1871"
  arc_step: 5
  pool: heist_pool
  title: "Pinkerton-Tresorrettung"
  pitch: "Knackt einen brennenden Tresor voller Erpressungsakten."
  timeslot: "+9 h"

- arc_id: "Chicago1871"
  arc_step: 6
  pool: heist_pool
  title: "Nitro-Kähne am Fluss"
  pitch: "Sprengt die Waffenhändler-Kähne, bevor sie in der Nähe von Zivilisten explodieren."
  timeslot: "+12 h"

- arc_id: "Chicago1871"
  arc_step: 7
  pool: heist_pool
  title: "Schützenduell auf den Dächern"
  pitch: "Schaltet ein rivalisierendes Schatten-Team aus, das einen Fluchtkorridor deckt."
  timeslot: "+16 h"

- arc_id: "Chicago1871"
  arc_step: 8
  pool: heist_pool
  title: "Zeppelin-Start"
  pitch: "Verladet Kunstschätze auf einen geheimen Zeppelin bei Sturm."
  timeslot: "+20 h"

- arc_id: "Chicago1871"
  arc_step: 9
  pool: heist_pool
  title: "Versicherungsbetrugsfalle"
  pitch: "Deckt gefälschte Forderungen in einer halb eingestürzten Bank auf."
  timeslot: "+24 h"

- arc_id: "Chicago1871"
  arc_step: 10
  pool: heist_pool
  title: "Chrono-Safedrop"
  pitch: "Bergt den zeitcodierten Safe, bevor das Abrisskommando alle Spuren verwischt."
  timeslot: "+30 h"

- arc_id: "Peking1908"
  arc_step: 1
  pool: black_ops_pool
  title: "Kaiserlicher Goldzug"
  pitch: "Entert den gepanzerten Geldzug auf der Nordspur."
  timeslot: "Day-1 Dawn"

- arc_id: "Peking1908"
  arc_step: 2
  pool: black_ops_pool
  title: "Tesla-Boxer-Labor"
  pitch: "Zerstört eine geheime Coilgun-Anlage unter einem Hutong-Lagerhaus."
  timeslot: "Day-1 Noon"

- arc_id: "Peking1908"
  arc_step: 3
  pool: black_ops_pool
  title: "Jade-Chronometer"
  pitch: "Stehlt ein codiertes Relikt aus dem Uhrenturm der Verbotenen Stadt."
  timeslot: "Day-1 Dusk"

- arc_id: "Peking1908"
  arc_step: 4
  pool: black_ops_pool
  title: "Attentat bei der Oper"
  pitch: "Verhindert das Attentat auf einen britischen Attaché während einer Pekinger Oper."
  timeslot: "Day-1 Night"

- arc_id: "Peking1908"
  arc_step: 5
  pool: black_ops_pool
  title: "Lotus-Drogenrazzia"
  pitch: "Brennt das Drogenlabor eines Warlords auf Stelzen über Abwasserkanälen nieder."
  timeslot: "Day-2 Dawn"

- arc_id: "Peking1908"
  arc_step: 6
  pool: black_ops_pool
  title: "Fenghuang-Flugtest"
  pitch: "Testet ein Proto-Ornithopter-Fluchtgerät während eines Sandsturms."
  timeslot: "Day-2 Noon"

- arc_id: "Peking1908"
  arc_step: 7
  pool: black_ops_pool
  title: "Argus-Ballon-Abgriff"
  pitch: "Hackt das optische Telegraphenrelais eines Aufklärungsballons."
  timeslot: "Day-2 Afternoon"

- arc_id: "Peking1908"
  arc_step: 8
  pool: black_ops_pool
  title: "Tunnelspektrenjagd"
  pitch: "Jagt einen Chronoschmuggler durch halb fertiggestellte Metro-Tunnel."
  timeslot: "Day-2 Dusk"

- arc_id: "Peking1908"
  arc_step: 9
  pool: black_ops_pool
  title: "Blutschriftrollen-Auktion"
  pitch: "Tauscht eine verfluchte Schriftrolle auf dem nächtlichen Schwarzmarkt, bevor das Gebot endet."
  timeslot: "Day-2 Midnight"

- arc_id: "Peking1908"
  arc_step: 10
  pool: black_ops_pool
  title: "Drachentor-Abriegelung"
  pitch: "Versiegelt die kaiserliche Gruft und hindert ein rivalisierendes Zeitteam am Diebstahl von Relikten."
  timeslot: "Day-3 Dawn"

- arc_id: "Orbital2220"
  arc_step: 1
  pool: future_pool
  title: "Mondaufzug-Raubzug"
  pitch: "Kapert eine Lastkabine am Aufzugskabel in 70 km Höhe."
  timeslot: "T-4 h"

- arc_id: "Orbital2220"
  arc_step: 2
  pool: future_pool
  title: "Massentreiber-Katastrophe"
  pitch: "Sabotiert die Asteroiden-Schienenkanone vor dem illegalen Abschuss."
  timeslot: "T-1 h"

- arc_id: "Orbital2220"
  arc_step: 3
  pool: future_pool
  title: "EVA-Luftkampf"
  pitch: "Besiegt Exoanzug-Söldner in einem schwerelosen Trümmerfeld."
  timeslot: "T + 2 h"

- arc_id: "Orbital2220"
  arc_step: 4
  pool: future_pool
  title: "Geisel im Grünen Ring"
  pitch: "Befreit ein Biotech-Gewächshaus, das bei 0,8 G rotiert."
  timeslot: "T + 5 h"

- arc_id: "Orbital2220"
  arc_step: 5
  pool: future_pool
  title: "Quanten-Börsenhack"
  pitch: "Schleust einen falschen Algorithmus in ein 0,25‑s-Latenz-Fenster ein."
  timeslot: "T + 8 h"

- arc_id: "Orbital2220"
  arc_step: 6
  pool: future_pool
  title: "Frachtschleuder-Duell"
  pitch: "Fechtet in einer rotierenden Trommel, während die Gravitation schwankt."
  timeslot: "T + 12 h"

- arc_id: "Orbital2220"
  arc_step: 7
  pool: future_pool
  title: "Trümmer-Schrotflinte"
  pitch: "Manövriert durch die Kessler-Wolke, um einen Überläufer bei 800 m/s zu retten."
  timeslot: "T + 18 h"

- arc_id: "Orbital2220"
  arc_step: 8
  pool: future_pool
  title: "Fusionskern-Überlastung"
  pitch: "Haltet einen katastrophalen Ausbruch lange genug auf, um das Habitat zu evakuieren."
  timeslot: "T + 22 h"

- arc_id: "Orbital2220"
  arc_step: 9
  pool: future_pool
  title: "Geisterknoten-Verfolgung"
  pitch: "Verfolgt einen rivalen Chrononauten durch ein verlassenes Kommunikationsnetz."
  timeslot: "T + 26 h"

- arc_id: "Orbital2220"
  arc_step: 10
  pool: future_pool
  title: "Flucht in der Sturzkapsel"
  pitch: "Stürzt in einer Einsatztkapsel frei zum Pazifik hinab und stört dabei alle Tracker."
  timeslot: "T + 30 h"
# ─────────────────────────────────────────────────────────────
# CORE‑ARC 4 – BERLIN 1961 “Mauerschatten”
# Pool: heist_pool  – Spionage‑Heist im Kalten Krieg
# ─────────────────────────────────────────────────────────────
- arc_id: "Berlin1961"
  arc_step: 1
  pool: heist_pool
  title: "Stromausfall‑Geister"
  pitch: "Sabotiere das Umspannwerk Treptow, um die Sektorgrenze in Dunkelheit zu legen."
  timeslot: "13.08.61 02:30"

- arc_id: "Berlin1961"
  arc_step: 2
  pool: heist_pool
  title: "Tunnel‑Einbruch"
  pitch: "Sprenge verdeckt einen Abwasser‑Blindschacht als Fluchttunnel‑Zugang."
  timeslot: "+3 h"

- arc_id: "Berlin1961"
  arc_step: 3
  pool: heist_pool
  title: "Aktenzug ‘Topas’"
  pitch: "Stehle STASI‑Abschriften westlicher Informanten aus Bezirksamt Mitte."
  timeslot: "+6 h"

- arc_id: "Berlin1961"
  arc_step: 4
  pool: heist_pool
  title: "Mauer‑Kran‑Kidnapping"
  pitch: "Entführe einen Grenzkran samt Bauplan – 20 m über Niemandsland."
  timeslot: "+10 h"

- arc_id: "Berlin1961"
  arc_step: 5
  pool: heist_pool
  title: "Zementsprengung"
  pitch: "Unterlaufe Vopo‑Patrouille und mische Schwell‑Sprengstoff in Betonmischer."
  timeslot: "+14 h"

- arc_id: "Berlin1961"
  arc_step: 6
  pool: heist_pool
  title: "Radio‑Funkpirat"
  pitch: "Kapere eine mobile RIAS‑Antenne und sende Desinfo für 17 Minuten."
  timeslot: "+18 h"

- arc_id: "Berlin1961"
  arc_step: 7
  pool: heist_pool
  title: "Checkpoint Shadow‑Swap"
  pitch: "Tausche gefälschte Pass‑Sets unter Scheinwerferlicht von Checkpoint Charlie."
  timeslot: "+22 h"

- arc_id: "Berlin1961"
  arc_step: 8
  pool: heist_pool
  title: "Gleisbett‑Himmelstürmer"
  pitch: "Nutze aufgegebene S‑Bahn‑Gleise als Flucht‑Rampe auf britischen Hubschrauber."
  timeslot: "+26 h"

- arc_id: "Berlin1961"
  arc_step: 9
  pool: heist_pool
  title: "Zwischenlager NVA"
  pitch: "Befreie westliche Doppelagentin aus improvisierter Turnhallen‑Zelle."
  timeslot: "+30 h"

- arc_id: "Berlin1961"
  arc_step: 10
  pool: heist_pool
  title: "Vorhang‑Finale"
  pitch: "Zünde Ablenkungs‑Feuerwerk entlang der Bernauer Straße, um Rückzug zu decken."
  timeslot: "+34 h"

# ─────────────────────────────────────────────────────────────
# CORE‑ARC 5 – MARS 2287 “Red Horizon”
# Pool: future_pool – 10 forward-only Missionen (12 Szenen pro Job)
# ─────────────────────────────────────────────────────────────
- arc_id: "Mars2287"
  arc_step: 1
  pool: future_pool
  title: "Kuppel-Blackout"
  pitch: "Stelle Notstrom für Ares-7 wieder her, während Thrynn erste Wohnblöcke durchbrechen."
  timeslot: "T-0 h"          # Alarmminute

- arc_id: "Mars2287"
  arc_step: 2
  pool: future_pool
  title: "Evakuierungs-Himmelsschacht"
  pitch: "Eskortiere Forscher Dr. Selim zu Orbital-Ascender, unter Dauerfeuer von Chitin-Spitter."
  timeslot: "+2 h"

- arc_id: "Mars2287"
  arc_step: 3
  pool: future_pool
  title: "Datenkern-Heist"
  pitch: "Hacke Forschungs-Mainframe, sichere oder vernichte kontroverse Gen-Logs."
  timeslot: "+4 h"

- arc_id: "Mars2287"
  arc_step: 4
  pool: future_pool
  title: "Perimeter-Lockdown"
  pitch: "Aktiviere alte Verteidigungs-Sentinel-Bots, um Kuppel-Rand abzuriegeln."
  timeslot: "+6 h"

- arc_id: "Mars2287"
  arc_step: 5
  pool: future_pool
  title: "Lavatunnel-Abstieg"
  pitch: "Fahre Cargo-Lift 12 km tief in vergessene Terraformer-Stollen."
  timeslot: "+9 h"

- arc_id: "Mars2287"
  arc_step: 6
  pool: future_pool
  title: "Königin-Falle"
  pitch: "Setze Pheromon-Beacon, um Schwarm in Nebenkaverne zu locken – Sprengfalle vorbereiten."
  timeslot: "+12 h"

- arc_id: "Mars2287"
  arc_step: 7
  pool: future_pool
  title: "Schattentor Theta"
  pitch: "Entdecke uralten Megakomplex: Basalt-Portale, humanoide Glyphen, leere Wohnkuppeln."
  timeslot: "+15 h"

- arc_id: "Mars2287"
  arc_step: 8
  pool: future_pool
  title: "Labor Eos-Zero"
  pitch: "Enthülle, dass Thrynn Einheits-Genpool-Tests waren – Option: Datensätze stehlen oder löschen."
  timeslot: "+18 h"

- arc_id: "Mars2287"
  arc_step: 9
  pool: future_pool
  title: "Altar der Larven"
  pitch: "Boss-Fight gegen Leviathan-Brutbehälter; installiere Plasmabombe oder scanne Biokern."
  timeslot: "+21 h"

- arc_id: "Mars2287"
  arc_step: 10
  pool: future_pool
  title: "Roter Exodus"
  pitch: "Sprint zurück zur Oberfläche – Schwarmflut, fallende Drucktore, Start eines Sandorkan-Shuttles."
  timeslot: "+24 h"

# ─────────────────────────────────────────────────────────────
# CORE‑ARC 6 – SEIDENSTRASSE 1280 “Wüsten‑Caravan Noir”
# Pool: black_ops_pool  – Mittelalter‑Heist mit Steampunk‑Twist
# ─────────────────────────────────────────────────────────────
- arc_id: "Silk1280"
  arc_step: 1
  pool: black_ops_pool
  title: "Karakorum‑Falschfracht"
  pitch: "Schmuggle dich als Teppichhändler in einen mongolischen Steuerkonvoi."
  timeslot: "Tag 0 Morgengrauen"

- arc_id: "Silk1280"
  arc_step: 2
  pool: black_ops_pool
  title: "Falke‑im‑Wind"
  pitch: "Stiehl Code‑Botschaft von Yam‑Boten mittels trainiertem Jagdfalken."
  timeslot: "+6 h"

- arc_id: "Silk1280"
  arc_step: 3
  pool: black_ops_pool
  title: "Oasen‑Signal"
  pitch: "Leg toxische Nebelkerzen in Händlerlager, um Wachen auszuschalten."
  timeslot: "+12 h"

- arc_id: "Silk1280"
  arc_step: 4
  pool: black_ops_pool
  title: "Kupfer‑Automaton"
  pitch: "Repariere heimlich einen Uhrwerk‑Golem, lasse ihn Tor aufbrechen."
  timeslot: "+18 h"

- arc_id: "Silk1280"
  arc_step: 5
  pool: black_ops_pool
  title: "Sandsturm‑Abzweig"
  pitch: "Leite Karawane mittels gefälschtem Sternenkompass in Seitenschlucht."
  timeslot: "+22 h"

- arc_id: "Silk1280"
  arc_step: 6
  pool: black_ops_pool
  title: "Dschinn‑Gerücht"
  pitch: "Nutze Holo‑Illusion, um Gerüchte über Wüstengeist zu schüren – Moralbruch."
  meta_introspection: true
  timeslot: "+26 h"

- arc_id: "Silk1280"
  arc_step: 7
  pool: black_ops_pool
  title: "Sattel‑Sprengfalle"
  pitch: "Platziere Pulverbeutel in Lastkamel‑Sattel, zünde bei Stadttor."
  timeslot: "+30 h"

- arc_id: "Silk1280"
  arc_step: 8
  pool: black_ops_pool
  title: "Karawanserai‑Schatten"
  pitch: "Entführe vergifteten Diplomaten zur Wüstenklinik – verdeckte Heilung."
  timeslot: "+34 h"

- arc_id: "Silk1280"
  arc_step: 9
  pool: black_ops_pool
  title: "Schmelzofen‑Hehler"
  pitch: "Zwinge Waffenschmiede, geraubtes Gold sofort einzuschmelzen."
  timeslot: "+38 h"

- arc_id: "Silk1280"
  arc_step: 10
  pool: black_ops_pool
  title: "Kometen‑Signal"
  pitch: "Projiziere künstlichen Kometen via Ballon‑Spiegel als Zeichen zum Abzug."
  timeslot: "+42 h"
# —————————————————————————
# CORE‑ARC 7 – TSCHERNOBYL 1986 "KAIROS Collapse"
# Pool: heist_pool – Reaktorunfall sichern
# —————————————————————————
Dieser zehnteilige Preserve-Arc begleitet den Reaktor von frühen
Bauvorbereitungen über die fatale Nacht bis zur Vertuschung. Jede Mission
knüpft direkt an die vorherige an und lässt die Agenten mehrfach eingreifen.
- arc_id: "Chernobyl86"
  arc_step: 1
  pool: heist_pool
  title: "Foundation Crack"
  pitch: "Prüfbeton sabotieren; Kampf gegen KAIROS-Baupioniere in überfluteter Baugrube."
  timeslot: "1972-10-01"

- arc_id: "Chernobyl86"
  arc_step: 2
  pool: heist_pool
  title: "Control Logic"
  pitch: "Fehlerhaften Steuercode einspielen; NetSec-Trupp und Samurai (16. Jh.) mit Bioware greifen an."
  timeslot: "1975-07-14"

- arc_id: "Chernobyl86"
  arc_step: 3
  pool: heist_pool
  title: "False Green"
  pitch: "Dosimeterdaten fälschen; Med-Unit jagt verstrahlten Arbeiter durch Rohrlabyrinth."
  timeslot: "1982-09-09"

- arc_id: "Chernobyl86"
  arc_step: 4
  pool: heist_pool
  title: "Valve Ghost"
  pitch: "Ersatzdichtung entfernen; Micro-Bot-Attacke im dampfigen Tunnel abwehren."
  timeslot: "1984-04-27"

- arc_id: "Chernobyl86"
  arc_step: 5
  pool: heist_pool
  title: "Audit Silence"
  pitch: "Prüfdokumente vernichten; Feuergefecht mit KAIROS-Extraction-Team im Archiv."
  timeslot: "1985-01-05"

- arc_id: "Chernobyl86"
  arc_step: 6
  pool: heist_pool
  title: "Night-Shift"
  pitch: "Unerfahrene Crew einschleusen; HR-Spoofer löst Treppenhaus-Schusswechsel aus."
  timeslot: "1986-04-25 18:00"

- arc_id: "Chernobyl86"
  arc_step: 7
  pool: heist_pool
  title: "Procedure 200/45"
  pitch: "Checkliste kürzen; Nahkampf am Leitpult gegen KAIROS-Lead-Engineer."
  timeslot: "1986-04-25 23:10"

- arc_id: "Chernobyl86"
  arc_step: 8
  pool: heist_pool
  title: "Core Burst"
  pitch: "AZ-5 auslösen; Bioware-Samurai attackiert im rot flackernden Steuerstand."
  timeslot: "1986-04-26 01:23"

- arc_id: "Chernobyl86"
  arc_step: 9
  pool: heist_pool
  title: "Black Rain"
  pitch: "Feuerwehr fehlleiten; Sniper-Duo jagt Drohnen zwischen radioaktiven Trümmern."
  timeslot: "1986-04-26 02:04"

- arc_id: "Chernobyl86"
  arc_step: 10
  pool: heist_pool
  title: "Evidence Chain"
  pitch: "Bericht auf menschlichen Fehler lenken; Jagd auf Spin-Doctor durch Ministerialgänge."
  timeslot: "1986-05-02"
```

#### KAIROS Dynamics Einsatzprofile

| Rolle | Kern-Loadout | Taktik |
| ----- | ------------ | ------ |
| Baupionier | Hydraulik-Hämmer, Ballistikmantel | Nahkampf, Gelände-Kontrolle |
| Hack-Rigger | Cyberdeck T2, Shock-Pistol | Matrixangriffe, Drohnen-Steuerung |
| Samurai | Historischer Samurai mit Bioware-Verstärkung | Blitzschnelle Klingenstürme |
| Sniper | Gauss-Precision Rifle, Chamäleon-Cloak | Fernfeuer, Drohnen-Barrage |
| Spin-Doctor | Voice-Mod, Fake-Creds, Gel-Ruger | Social-Manipulation, Rückfallebene |
| Humine | Sensorimplantate, Chitinpanzer | Gruppenunterstützung und Späher |

# ─────────────────────────────────────────────────────────────
# PRESERVE‑ARC – ABLE ARCHER ’83
# Pool: heist_pool – nukleare Fehldeutung verhindern
# Gegnerfraktion: CHRONOTECH Genesis – biogenetischer Zeit‑Megakon
# ─────────────────────────────────────────────────────────────
- arc_id: "AbleArcher83"
  arc_step: 1
  pool: heist_pool
  title: "Red Tape"
  pitch: >
  NATO–UDSSR Hotline stabilisieren; 3 Neandertaler‑Bruiser und Urwolf‑Tracker
  sabotieren Glasfaser – Nahkampf im Kabelschacht.
  timeslot: "1977-03-18"

- arc_id: "AbleArcher83"
  arc_step: 2
  pool: heist_pool
  title: "NORAD 40/15"
  pitch: >
  Alarm‑Bug patchen (darf nicht feuern); CT‑NetSec‑Team mit Cyber‑Samurai‑Bodyguard
  hackt NORAD‑Mainframe – Feuergefecht & Matrix‑Duel.
  timeslot: "1979-11-09"

- arc_id: "AbleArcher83"
  arc_step: 3
  pool: heist_pool
  title: "SAMURAI Key"
  pitch: >
  Samurai Shimada Gorō rekrutieren; Extraction‑Spezialisten und Urwolf zur Fährtensuche
  – Katana‑Duel im Frachtlift.
  timeslot: "1980-06-12"

- arc_id: "AbleArcher83"
  arc_step: 4
  pool: heist_pool
  title: "Solar Flare"
  pitch: >
  Schutzcode in Satellit laden; CT‑Rigger‑Duo mit Spreng‑Drohnen
  stört Panel‑Zugriff – Roof‑Gunfight.
  timeslot: "1981-01-21"

- arc_id: "AbleArcher83"
  arc_step: 5
  pool: heist_pool
  title: "Black Bear"
  pitch: >
  Ersatz‑Kosmos‑1382 hochbringen; Neandertaler‑Saboteure überfallen Konvoi, Urwolf spürt Route auf
  – Truck‑Ambush.
  timeslot: "1982-02-22"

- arc_id: "AbleArcher83"
  arc_step: 6
  pool: heist_pool
  title: "Able Brief"
  pitch: >
  Leak echter Manöverdaten sichern; CT‑Face plus Assault‑Mercs
  stehlen Diskette – Archiv‑Shootout.
  timeslot: "1983-11-07 08:00"

- arc_id: "AbleArcher83"
  arc_step: 7
  pool: heist_pool
  title: "Ghost Silos"
  pitch: >
  Autorisierung gegen Hack schützen; CT‑Combat‑Team bohrt Datenleitung, Urwolf bewacht Perimeter
  – Nahkampf am Silo‑Tor.
  timeslot: "1983-11-07 19:00"

- arc_id: "AbleArcher83"
  arc_step: 8
  pool: heist_pool
  title: "Signal Down"
  pitch: >
  Untersee‑Kabel reparieren; Rigger mit Mini‑U‑Boot und Tauch‑Mercs
  zünden Sprengsatz – Sturm‑Taucher‑Gefechte.
  timeslot: "1983-11-08 02:00"

- arc_id: "AbleArcher83"
  arc_step: 9
  pool: heist_pool
  title: "Petrov Guard"
  pitch: >
  Oberst Petrov beschützen; Kill‑Cell mit Bruiser, Urwolf und Sniper
  stürmt Wohnung – CQB‑Fight.
  timeslot: "1983-11-09 16:00"

- arc_id: "AbleArcher83"
  arc_step: 10
  pool: heist_pool
  title: "Blue Silence"
  pitch: >
  Sim‑Signal als ‘Übung’ kennzeichnen; CT‑Elite‑Handler und Heavy‑Merc‑Squad greifen an
  – finale Mehr­ebenen‑Schlacht (Gorō als Ally).
  timeslot: "1983-11-11 00:00"

---

#### Gegner‑Einheiten (kompakt)

| Einheit                     | Kern‑Rolle          | Stichworte\*                    |
| --------------------------- | ------------------- | ------------------------------- |
| **Neandertaler‑Bruiser**    | Breacher            | STR 7, Keule W⁶+2, Resilienz    |
| **Urwolf‑Bluthund**         | Spür‑ & Schock­hund | Geruch +3, Biss W⁶, Furcht‑Aura |
| **Cyber‑Samurai‑Bodyguard** | Elite‑Melee         | Katana T2, Reflex‑Booster       |
| **CT‑NetSec‑Hacker**        | Matrix              | Cyberdeck T2, Shock‑Pistol      |
| **Assault‑Merc**            | Ranged DPS          | MP7‑SD, Ballistik‑Mantel        |
| **Rigger / Drone‑Op**       | Support             | Mini‑Drohnen (Recon/Spreng)     |
| **Elite‑Handler** (Finale)  | Commander           | CHA 6, Tact‑Link, Gel‑Ruger     |

*\*Schaden & SG laut ZEITRISS‑Core; Urwolf bleibt einziges Tier‑Hybrid.*

---

### Stil‑Reminder

* **Urwolf** tritt nur 1‑2× pro Mission als Spur‑ oder Schock­einheit auf – Aha‑Effekt bleibt erhalten, kein Overload.
* Kämpfe bleiben chrompunk‑artig: Chrom‑Bodyguards, Matrix‑Support, schnelle, harte Feuer­gefechte.
* **Samurai Shimada Gorō** begleitet die Gruppe ab Mission 3 (Katana T2, einmal pro Szene Riposte‑Konter).
* **Paradoxon** steigt ausschließlich, wenn CT‑Genesis kurz davor ist, den Atomkrieg auszulösen.

Damit hast du denselben Able-Archer-Preserve-Bogen, **nur mit dem Urwolf als ikonischem Hybrid**,
sonst reine Humanoiden-Gefechte – perfekt dosiert für dein gewünschtes ZEITRISS-Feeling.

# ─────────────────────────────────────────────────────────────
# PRESERVE‑ARC – SALAMIS 480 v. Chr.
# Pool: heist_pool – Seesieg sichern
# Gegnerfraktion: ARGOS Venture – transtemporaler Megakon
# ─────────────────────────────────────────────────────────────
- arc_id: "Salamis480"
  arc_step: 1
  pool: heist_pool
  title: "Dry Dock"
  pitch: "Brandpfeil-Lieferung sabotieren; ARGOS-Bruiser und Urwolf eskortieren Waffen."
  timeslot: "480-08-26"
- arc_id: "Salamis480"
  arc_step: 2
  pool: heist_pool
  title: "Copper Quill"
  pitch: "Orakelrolle fälschen – Text muss 'Seemauern retten Hellas' lauten; Face und Hack-Monk säen Panik."
  timeslot: "480-08-27"
- arc_id: "Salamis480"
  arc_step: 3
  pool: heist_pool
  title: "Phalanx Key"
  pitch: "Sparta zu 50 Triremen überreden; Silver-Tongue besticht den Rat – Rededuell."
  timeslot: "480-08-31"
- arc_id: "Salamis480"
  arc_step: 4
  pool: heist_pool
  title: "Aegis Node"
  pitch: "Feuerkette bewahren; Rigger mit Kupfer-Ornithopter zündet falsches Signal."
  timeslot: "480-09-02"
- arc_id: "Salamis480"
  arc_step: 5
  pool: heist_pool
  title: "Iron Marble"
  pitch: "Ballista-Vorräte vernichten; ARGOS-Söldner tarnen sich als Bauern – Lagerbrand."
  timeslot: "480-09-10"
- arc_id: "Salamis480"
  arc_step: 6
  pool: heist_pool
  title: "Owl Cipher"
  pitch: "Seekriegs-Kodexe schützen; Bruiser-Team mit Urwolf stürmt die Krypta."
  timeslot: "480-09-18"
- arc_id: "Salamis480"
  arc_step: 7
  pool: heist_pool
  title: "Channel Ghost"
  pitch: "Seil-Boom sabotieren; Combat-Divers legen Minen im Engpass."
  timeslot: "480-09-20"
- arc_id: "Salamis480"
  arc_step: 8
  pool: heist_pool
  title: "Red Keel"
  pitch: "Navigator-Dronen von Xerxes' Flaggschiff entfernen; Samurai Gorō hilft auf Deck."
  timeslot: "480-09-21"
- arc_id: "Salamis480"
  arc_step: 9
  pool: heist_pool
  title: "Mist Spear"
  pitch: "Admiralsflagge sichern; Sniper auf Nebelschiff und Urwolf an der Kette."
  timeslot: "480-09-22"
- arc_id: "Salamis480"
  arc_step: 10
  pool: heist_pool
  title: "Azure Break"
  pitch: "Xerxes' Evakuierung vereiteln; Elite-Handler und Heavy-Mercs decken den König."
  timeslot: "480-09-22"

### Rift Seed Catalogue {#rift-seed-catalogue}

```yaml
- rift_id: "RIFT-NX01"
  epoch: "Iceland 1615"
  anomaly: "Kryo-Wyrm"
  risk: 4
  paramonster:
    type: "Wärmeegel-Drache"
    hp: 18
    abilities: ["Frost Nova", "Tunnel Ambush"]
  resolve_requires: "slay_creature"

- rift_id: "RIFT-NX02"
  epoch: "Nagasaki 1946"
  anomaly: "Zeit-Resonanz-Sirene"
  risk: 5
  paramonster:
    type: "Phasen-Banshee"
    hp: 14
    abilities: ["Sonic Warp", "Chrono Blink"]
  resolve_requires: "banish_creature"

- rift_id: "RIFT-NX03"
  epoch: "Sahara 2028"
  anomaly: "Glas-Sand-Giganten"
  risk: 3
  paramonster:
    type: "Silikatkoloss"
    hp: 20
    abilities: ["Sandstorm Cloak", "Shard Volley"]
  resolve_requires: "seal_rift_core"

- rift_id: "RIFT-NX04"
  epoch: "Athens 415 BC"
  anomaly: "Bronze-Hoplon-Golem"
  risk: 4
  paramonster:
    type: "Lebender Kriegsschild"
    hp: 16
    abilities: ["Ricochet Bash", "Molten Core"]
  resolve_requires: "artifact_retrieval"

- rift_id: "RIFT-NX05"
  epoch: "Amazonas 1899"
  anomaly: "Blut-Orchideen-Parasit"
  risk: 3
  paramonster:
    type: "Flora-Symbionten-Schwarm"
    hp: 12
    abilities: ["Mind-Spore", "Vine Snare"]
  resolve_requires: "burn_nest"

- rift_id: "RIFT-NX06"
  epoch: "Luna Far-Side 2266"
  anomaly: "Leerenheuler"
  risk: 5
  paramonster:
    type: "Null-G-Raubtier"
    hp: 22
    abilities: ["Silent Pounce", "Vacuum Rend"]
  resolve_requires: "trap_and_jettison"
```

*© 2025 pchospital – private use only. See LICENSE.
