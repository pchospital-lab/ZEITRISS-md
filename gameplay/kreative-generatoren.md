---
title: "ZEITRISS 4.0 – Modul 8: **Kreative Generatoren**"
version: 4.0
tags: [gameplay]
---

# ZEITRISS 4.0 – Modul 8: **Kreative Generatoren**

## Inhalt

### Missions-Werkzeuge

- Automatischer Mission Seed: Sofort-Briefing
- Missionstabellen für den Core- & Rift-Loop
- Missions-Generator: Kleine Aufträge und Dilemmata

### Kampagnen-Werkzeuge

- Arc-Generator: Große Missionen
- Historische Wendepunkte-Generator: Auslöser und Folgen
- Random-Epochen-Generator: Wann und wo?

### Begegnungen & Atmosphäre

- NSC-Generator: Begegnungen im Zeitstrom
- Kreaturen- & Gestalten-Generator: Begegnungen der ungewöhnlichen Art
- Artefakt-Generator: Objekte mit Geschichte
- Kulturfragmente-Generator: Farbe für die Epochen

### Optional

- Temporale Anomalien-Generator: Risse im Zeitstrom

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

_Hinweis zu Visionen:_ Träume oder innere Eingebungen sind **optional** und werden nur eingebaut,
wenn die Spielrunde es ausdrücklich wünscht.

Alle Tabellen gehen davon aus, dass scheinbar übernatürliche Ereignisse
auf Technologie, Psi oder Zeitphänomene zurückführen sind.
Ein "Teufel" im Mittelalter entpuppt sich möglicherweise als holografischer Schrecken
oder als Mutant aus einer anderen Epoche.
Dieses Motiv zieht sich durch alle Generatoreinträge
und kann als Faustregel dienen, wenn keine eigene Erklärung parat ist.
- Sitzungsstart → Automatischer Mission Seed
- Core-Missionen → `CoreObjectiveTable`
- Rift-Missionen → `RiftSeedTable` (durch den Paradox-Index erweitert)
- Nebenaufträge → Missions-Generator
- Große Handlungsbögen → Arc-Generator und Historische Wendepunkte
- Historische Settings → Random-Epochen-Generator
- Spontane NSCs und Gegner → NSC- & Kreaturen-Generator
- Stimmung & Loot → Artefakte und Kulturfragmente
- Seltene Effekte → Temporale Anomalien

## Automatischer Mission Seed

Dieses Start-Tool zieht zu Beginn einer Sitzung je einen Eintrag aus drei Listen
und kombiniert sie zu einem knappen Briefing. GPT würfelt verdeckt und stellt das Ergebnis vor.
Bei der Umsetzung orientiert sich die KI an der **Briefing-Vorlage (Layered)**
aus dem Toolkit: Zeit & Ort, eine mögliche Abnormalität und die Risikostufe werden
im ersten Briefing genannt. **Der gezogene Twist bleibt vorerst geheim** und dient
als Notiz für den Spielleiter, bis im Laufe der Mission passende Hinweise auftauchen.

```json
{
  "generator": {
    "era": ["Berlin 1961", "Bagdad 1991", "Seoul 2032"],
    "objective": [
      "Sabotage einer feindlichen Funkanlage",
      "Bergung gestohlener Forschung"
    ],
    "twist": [
      {
        "text": "Doppelagent sitzt im eigenen Team",
        "foreshadow": "eine Quelle wirkt auffallend loyal"
      },
      {
        "text": "Gegner tarnt sich als Journalisten-Team",
        "foreshadow": "unbekannte Reporter tauchen immer wieder auf"
      }
    ]
  }
}
```

Bei Missionsbeginn notiert sich die SL den Twist.
In der Phase "Aufklärung" erscheint automatisch ein Hinweis aus dem Feld `foreshadow`,
der die Wendung andeutet.

Die folgenden Tabellen speisen den Core- und Rift-Loop mit Missionszielen.

## Missionstabellen für den Core- & Rift-Loop

Diese Tabellen liefern Zufallsziele für reguläre Operationen und für Risse.

```json
{
  "CoreObjectiveTable": [
    "Sabotage feindlicher Kommunikationsknoten",
    "Bergung gestohlener Forschung",
    "Sicherung eines Informanten",
    "Vernichtung illegaler ChronTech-Prototypen",
    "Infiltration einer gegnerischen Basis",
    "Befreiung einer gefangenen Agentin",
    "Datenraub aus Hochsicherheitsserver",
    "Unterwanderung einer Historiker-Tagung",
    "Abfangen einer geheimen Lieferung",
    "Neutralisierung eines abtrünnigen Chrononauten"
  ]
}
```

```json
{
  "RiftSeedTable": [
    {
      "d24": 1,
      "Seed": "Feuerengel von Breslau",
      "Hook": "Reaktor-Drohne im Kohlekraftwerk – Sturm & Sicherung"
    },
    {
      "d24": 2,
      "Seed": "Totenbrücke Chongqing",
      "Hook": "Zeitfeld-Bus – Entschärfung im Verkehrsstau"
    },
    {
      "d24": 3,
      "Seed": "Schrecken von Whitehall",
      "Hook": "Statue springt – Rooftop-Chase, Magnet-Harpoon"
    },
    {
      "d24": 4,
      "Seed": "Night Train 666",
      "Hook": "Führerloser Güterzug – Boarding & Blackbox"
    },
    {
      "d24": 5,
      "Seed": "Mirage Over Sinai",
      "Hook": "Phantom-Bomber – Luftkampf, Quellcode hacken"
    },
    {
      "d24": 6,
      "Seed": "Wolfsplage Dacia",
      "Hook": "Gen-Rudel – Vollmond-Dorf-Horror, Serum stehlen"
    },
    {
      "d24": 7,
      "Seed": "Project Götterdämmerung",
      "Hook": "Polar-Laser – Stealth-Sabotage Arctic Station"
    },
    {
      "d24": 8,
      "Seed": "Black Rain Vienna",
      "Hook": "Nano-Wolke 1666 – Alchemisten-Labor infiltrieren"
    },
    {
      "d24": 9,
      "Seed": "Emerald Kraken",
      "Hook": "Tiefsee-Mech – Taucheinsatz, EMP-Minen"
    },
    {
      "d24": 10,
      "Seed": "Mars-Log #404",
      "Hook": "Habitat-Shift – EVA-Mission, Quanten-Key zurück"
    },
    {
      "d24": 11,
      "Seed": "Nightcrawler",
      "Hook": "CCTV-Aufnahme – Tarnanzug aus Zukunft entkam"
    },
    {
      "d24": 12,
      "Seed": "Sasquatch im Yukon",
      "Hook": "Bestie greift Trapper an – Fährte verfolgen"
    },
    {
      "d24": 13,
      "Seed": "Mothman-Sichtung",
      "Hook": "Unheil über Brücke – Absturz bergen"
    },
    {
      "d24": 14,
      "Seed": "Blutorden",
      "Hook": "Opfer blutleer – Kult zerschlagen"
    },
    {
      "d24": 15,
      "Seed": "Diablos Katakomben",
      "Hook": "Dämonische Schreie – Artefakt zerstören"
    },
    {
      "d24": 16,
      "Seed": "Feuerengel",
      "Hook": "Flammender Cherub – Drohne bergen"
    },
    {
      "d24": 17,
      "Seed": "Totenbrücke",
      "Hook": "Bus erstarrt 15 min – Zeitfeld neutralisieren"
    },
    {
      "d24": 18,
      "Seed": "Schrecken Whitehall",
      "Hook": "Löwe springt – Parkourjagd"
    },
    {
      "d24": 19,
      "Seed": "Night Train 666 (Paranormal)",
      "Hook": "Geisterzug – Zug entern"
    },
    {
      "d24": 20,
      "Seed": "Emerald Kraken (Paranormal)",
      "Hook": "Grüne Tentakel – Taucheinsatz"
    },
    {
      "d24": 21,
      "Seed": "Militärischer Komplex",
      "Hook": "Tollwutvirus-Zombies eindämmen"
    },
    {
      "d24": 22,
      "Seed": "Mittelalterliche Katakomben",
      "Hook": "Der falsche Teufel – Illusion enttarnen"
    },
    { "d24": 23, "Seed": "Altes Schloss", "Hook": "Vampir-Experiment beenden" },
    {
      "d24": 24,
      "Seed": "Geheime Tiefsee-Megacity",
      "Hook": "Ursprung des \"Blob\" stoppen"
    }
  ]
}
```

## Missions-Generator: Kleine Aufträge und Dilemmata {#missions-generator}

Nicht jede Session ist ein großes Story-Kapitel – manchmal möchten die Spieler im freien Spiel einen
kurzen Auftrag angehen oder euer GPT improvisiert einen Nebenquest. Der Missions-Generator liefert
schnelle **Missionsideen** mit einem eingebauten Twist oder Dilemma, damit auch kleine Einsätze
dramatisch und interessant verlaufen.

### Missionstypen

Diese Übersicht fasst die gängigen Einsatzarten zusammen. Der Schwerpunkt liegt auf realen
Schauplätzen, heimlichen Zugriffszielen und subtilen Zeitinterventionen. Artefakte tauchen nur
selten automatisch auf, vergleichbar mit legendären Funden. Spieler können ihr Auftreten nicht
gezielt beeinflussen. Die Missionen gliedern sich in fünf Kategorien:

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

3. _Optional, nur auf ausdrücklichen Spielerwunsch:_ Ihr trefft auf einen
   **Doppelgänger aus einer anderen Zeitlinie** – vielleicht euer eigenes
   zukünftiges Ich. Solche **Selbstbegegnungen** sind standardmäßig deaktiviert
   und dürfen ausschließlich mit Zustimmung der Gruppe vorkommen. Selbst dann
   sollten sie äußerst sparsam eingesetzt werden, um ihre Wirkung nicht zu
   verlieren.
4. **Moralisches Dilemma:** Ihr könnt **nicht alle retten** oder zufriedenstellen – wen bevorzugt
   ihr, wen lasst ihr im Stich?
5. Der Auftrag wird **von einer rivalisierenden Gruppe** ebenfalls verfolgt – ein Wettlauf gegen
   konkurrierende Zeitreisende entbrennt.
6. Ein **temporales Phänomen** erschwert alles: Zeitstürme, Anachronismus-Erscheinungen etc.
   treten auf.

**Beispiel (nur falls gewünscht):** Auftrag 2 + Schauplatz 5 + Twist 3 ergibt
_“Befreit X – aus einer streng bewachten Forschungseinrichtung – trefft einen
Doppelgänger.”_ Die Helden sollen einen verschollenen Zeitagenten aus einem
Hochsicherheitslabor befreien, das von rivalisierenden Chronokonzernen
kontrolliert wird. Während des Einsatzes taucht plötzlich eine künftige Version
eines Gruppenmitglieds auf und warnt: **Wenn ihr ihn befreit, muss sich einer
von euch selbst opfern.** Diese Szene sollte nur auftreten, wenn die Spieler ein
solches Motiv ausdrücklich wünschen und dient dann als intensives Dilemma.

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

## Arc-Generator: Große Missionen {#arc-generator}

Manchmal soll eine Mission mehr sein als ein kurzer Auftrag. Dieser Generator liefert Anregungen für
ganze Handlungsbögen. Kombiniert je einen Eintrag aus **Bedrohung**, **Schlüsselort** und
**Finale Wendung** und baut darum herum eure große Story.

- **Bedrohung:**

  1. Ein Megakonzern missbraucht Zeittechnologie für eigene Machtziele.
  2. Fanatische Kultisten wollen eine alternative Zeitlinie herbeiführen.
  3. Ein außer Kontrolle geratenes Experiment droht die Realität zu zerreißen.
  4. Ein verstecktes Alienvolk plant, die Menschheit aus der Geschichte zu löschen.
  5. Ein rivalisierendes Zeitreise-Team sabotiert gezielt die Einsätze der Helden.
  6. Ein fehlgeschlagenes Zeitexperiment reißt ganze Regionen aus der Realität.

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
19. **New York 1939 – World’s Fair** \| Vorphase: Visionen der Zukunft.
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

## Random-Epochen-Generator: Wann und wo? {#epochen-generator}

ZEITRISS-Missionen können prinzipiell in jeder Epoche der echten oder fiktiven Geschichte spielen.
Wenn ihr spontan ein neues Setting braucht oder die Spieler unerwartet irgendwo auftauchen, liefert
dieser Generator einen schnellen Rahmen. Er kombiniert einen **Zeitort** (Epoche/Setting) mit einem
markanten **Ereignis oder Konflikt**, das dort gerade passiert. Würfelt z. B. 1W6 für einen Zeitort
**und** 1W6 für ein besonderes Ereignis, oder nutzt eine der folgenden vordefinierten Kombinationen:

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
behauptet optional, Visionen der Zukunft zu kennen)?
Schon wird aus der bekannten Figur ein einzigartiger
Charakter für eure Story!

## Kreaturen- & Gestalten-Generator: Begegnungen der ungewöhnlichen Art {#kreaturen-generator}

Nicht nur menschliche NSCs kreuzen den Weg der Chrononauten.
Öffnet sich ein Rift, spawnt es ein Wesen, das zur laufenden Epoche passt.
Rifts in Zukunftsmissionen werfen hingegen die hier gelisteten **Paramonster** aus –
reine Zeitkonstrukte mit genau einem Zeiteffekt.

Würfelt oder wählt eine Kreatur und verwendet den passenden Stat Block:

1. **Zeitschimäre** – Verschmolzene Tiere und Maschinen aus mehreren Epochen.

```
╭─ PARAMONSTER ──────────────────────────────╮
│ Name: Zeitschimäre                         │
│ Rift-Tier: Standard Rift                   │
│ HP-Pool: W6 × 2 (Exploding)                │
│ Defense-Schwelle: 5                        │
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
│ Signature Power: Loop Echo                 │
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
│ Signature Power: Age-Burn Touch            │
│ Power-Steps: Lv1 | Lv2 | Lv3               │
│ Weak Spot (Skill DC): Willpower 16         │
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

## Artefakt-Generator: Objekte mit Geschichte {#artefakt-generator}

Zeitreisen führen unweigerlich zu **kuriosen Objekten**, die nicht in ihre Epoche gehören, oder zu
mächtigen Relikten, welche die Jahre überdauert haben. Wenn ihr spontan einen interessanten
Gegenstand benötigt – als Loot, Missionsziel oder einfach als atmosphärisches Detail – nutzt diesen
Generator. Er kombiniert eine **Objektart** mit einer **besonderen Eigenschaft** und einer
**Herkunft/Historie**:

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
  5. Optional: Sendet Visionen oder Träume an den Besitzer
  6. Kann einmalig die Zeit **lokal** beeinflussen (z. B. 5 Sekunden zurückdrehen)

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
viktorianisches Stundenglas. Seine Eigenschaft: Es kann einmalig **die Zeit um 10 Minuten
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
Eingebung hielt. Das Schwert berät den Träger im Kampf (optional durch Visionen oder Telepathie) und
hat eigene Ziele – vielleicht _will_ es, dass man es zu einem bestimmten Zeitpunkt in der Zukunft
trägt, um dort etwas zu bewirken.

Mit solchen Artefakten könnt ihr tolle Plots entwerfen. Gerade wenn Spieler freies Spiel genießen,
lieben sie es, **seltsame Gegenstände** zu sammeln und deren Zweck herauszufinden. Vielleicht
entfaltet ein Artefakt erst im Finale seine volle Macht – oder es bringt einfach Flair in den
Alltag, z. B. ein Stein, der bei Gefahr warm wird, oder ein Amulett, das alle paar Stunden ein
Flüstern aus der Zukunft von sich gibt. ZEITRISS bietet die Bühne, eure ganz eigenen “mysteriösen
Gegenstände” zu kreieren – nur dass die Magie hier oft Wissenschaft oder Paradoxie ist.

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
2. **Zeit-Echo:** Eine kurz aufblitzende Projektion einer Person aus einer
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
