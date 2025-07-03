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
- Encounter-Pool: Schnelle Gegnerlisten nach Risiko
- Twist-Seeds: Dramatische Wendungen
- Kreaturen- & Gestalten-Generator: Begegnungen der ungewöhnlichen Art
- Para-Creature-Generator: Urban Myth Edition
- Artefakt-Generator: Objekte mit Geschichte
- Kulturfragmente-Generator: Farbe für die Epochen

### Optional

- Rätselbibliothek: Kurze Hürdenszenen
- Temporale Anomalien-Generator: Risse im Zeitstrom
- Rätsel-Sets: Komplette Szenen
- Historische Anomalien-Generator

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
- Rift-Missionen → `RiftSeedTable` (durch den Paradoxon-Index erweitert)
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
Ein optionaler **Tonal-Safety-Toggle** filtert extrem düstere oder humorige Seeds
heraus, falls die Gruppe einen einheitlichen Stil bevorzugt.

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

_Regel:_ Eintragstexte dürfen nicht wortgleich in `objective` und `twist` stehen.
Streiche doppelte Seeds oder variiere sie.

```jsonc
{
  "twists": [
    {
      "id": "T28",
      "label": "Uhrwerk-Diplomatie",
      "effect": "Eine schwelende Waffenruhe zwischen zwei Zeitaltern gerät ins Wanken –"
      "Das Einsatzteam muss unbeabsichtigte Provokationen verhindern."
    },
    {
      "id": "T29",
      "label": "Echo-Konklave",
      "effect": "Ein Parallel-Team aus einer nur minimal abweichenden Zeitlinie versucht,"
      "dieselbe Mission abzuschließen – Konkurrenz oder Kooperation?"
    },
    {
      "id": "T30",
      "label": "Trans-Silicon-Plague",
      "effect": "Ein Nanovirus springt Epochen; jeder Eingriff könnte es beschleunigen oder auslöschen."
    },
    {
      "id": "T31",
      "label": "Imperiale Schachfigur",
      "effect": "Eine Nebenfigur entpuppt sich als unerwartet wichtige historische Schlüsselfigur –"
      "Eliminierung tabu, Manipulation riskant."
    },
    {
      "id": "T32",
      "label": "Kaltes Singularitätstor",
      "effect": "Ein experimenteller Energiepuls droht, ein Micro-Einstein-Rosen-Tor dauerhaft zu öffnen."
    },
    {
      "id": "T33",
      "label": "Silencer-Protokoll",
      "effect": "Das HQ befiehlt Funkstille; Team muss ohne Codex-Support improvisieren, bis eine Relaisstation steht."
    },
    {
      "id": "T34",
      "label": "Orchideen-Schlüssel",
      "effect": "Ein unscheinbares Artefakt aktiviert versteckte Bio-Sicherungen in hochrangigen Zielpersonen."
    },
    {
      "id": "T35",
      "label": "Sturm ★ Delta",
        "effect": "Eine Wetter-Modifikationsanlage im Jahr 19XX löst einen Jahrhundert-Hurrikan aus –"
        "Fail-Safe versiegelt."
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
    { "Objective": "Sabotage feindlicher Kommunikationsknoten" },
    { "Objective": "Bergung gestohlener Forschung" },
    { "Objective": "Sicherung eines Informanten" },
    { "Objective": "Vernichtung illegaler ChronTech-Prototypen" },
    { "Objective": "Infiltration einer gegnerischen Basis" },
    { "Objective": "Befreiung einer gefangenen Agentin" },
    { "Objective": "Datenraub aus Hochsicherheitsserver" },
    { "Objective": "Unterwanderung einer Historiker-Tagung" },
    { "Objective": "Abfangen einer geheimen Lieferung" },
    { "Objective": "Neutralisierung eines abtrünnigen Chrononauten" }
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
      "d24": 17,
      "Seed": "Totenbrücke",
      "Hook": "Bus erstarrt 15 min – Zeitfeld neutralisieren"
    },
    {
      "d24": 18,
      "Seed": "Schrecken von Whitehall – PHANTOM",
      "Hook": "Löwe springt – Parkourjagd"
    },
    {
      "d24": 19,
      "Seed": "Night Train 666 – PHANTOM",
      "Hook": "Geisterzug – Zug entern"
    },
    {
      "d24": 20,
      "Seed": "Emerald Kraken – PHANTOM",
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
    {
      "d24": 23,
      "Seed": "Altes Schloss",
      "Hook": "Vampir-Experiment beenden"
    },
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

## Encounter-Pools nach Risikostufe {#encounter-pools}

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
  risk: "S"
  text: "Patrouillen-Duo (Ortspolizei, schlecht ausgerüstet)"
- epoch: "modern"
  type: "civilian"
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
_Temporal Backdoor:_ Bei Echo-Stack 3 entsteht ein Kurz-Rift, dann fällt der Stack auf 0.

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
| 30 | Rücksprung löst Echo aus – Gegner erhält Vorwissen über Actions. | 2 | mittel |
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
| 41 | Mirrored Orders – konkurrierendes Team erhält identische Befehle. | 1 | mittel |
| 42 | Cold Swap – Artefakt stammt aus Parallel-Cluster, HQ fordert Nachverhandlung. | 1 | mittel |
| 43 | Echo Broadcast warnt Gegner vor dem Team – Stealth +2 SG. | 0 | klein |
| 44 | Delayed Cipher datiert 30 Jahre zu spät – Rätsel PZ‑2.5, Paradox +1 bei Fail. | 1 | klein |
| 45 | Black Budget – unbekannte Geldgeber mischen sich ein, Shadow‑Team optional. | 2 | mittel |
| 46 | Automata sabotieren Bosporus-Telegrafen – Flottenabkommen in Gefahr. | 2 | mittel |

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
14 | Hitchhiking Ghost – Zeitversetzte Holo‑Echo‑Aufnahme
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

#### C. Shadow People – „Umbra‑Echo“

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

### Artefakt-Seed-Starter (1W10)

| Wurf | Codename | Jahr / Ort | Primäre Kraft | Nebenwirkung |
|-----:|----------|-----------|---------------|---------------|
| 1 | „Ätherglas" | Prag 1889 | Unsichtbarkeit (2 Min.) | Kälte -10 °C |
| 2 | „Helios-Split" | Delphi -430 | Lichtstrahl 1 kW | Blendung Benutzer |
| 3 | „Sforza-Würfel" | Mailand 1496 | Local Time-Freeze 5 Sek. | Paradoxon +1 |
| 4 | „Chorus-Reel" | New York 1941 | Stimmen-Mimikry | Ohrensausen |
| 5 | „Kalkstein-Rune" | Göbekli Tepe -9020 | Telepathie 100 m | Migräne |
| 6 | „Jade-Kompass" | Xi’an 221 v. Chr. | Portalsprung 10 m | random scatter 3 m |
| 7 | „Edison-Spule" | Menlo Park 1877 | EMP Radius 5 m | Gerät defekt |
| 8 | „Orpheus-Harfe" | Wien 1791 | Emotion Control | Selbst → Trauer |
| 9 | „Fresnel-Linse" | Paris 1848 | Hologram 10 min | Akku 100 CU |
| 10 | „Cronos-Sand" | Alexandria 48 v. Chr. | Rücksprung 1 Tag | Paradoxon +2 |

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
Eingebung hielt. Das Schwert berät den Träger im Kampf (optional durch Visionen oder Telepathie) und
hat eigene Ziele – vielleicht _will_ es, dass man es zu einem bestimmten Zeitpunkt in der Zukunft
trägt, um dort etwas zu bewirken.

Mit solchen Artefakten könnt ihr tolle Plots entwerfen. Gerade wenn Spieler freies Spiel genießen,
lieben sie es, **seltsame Gegenstände** zu sammeln und deren Zweck herauszufinden. Vielleicht
entfaltet ein Artefakt erst im Finale seine volle Macht – oder es bringt einfach Flair in den
Alltag, z. B. ein Stein, der bei Gefahr warm wird, oder ein Amulett, das hin und wieder im Verlauf einer Mission ein
Flüstern aus der Zukunft von sich gibt. ZEITRISS bietet die Bühne, eure ganz eigenen „mysteriösen“
Gegenstände zu kreieren – nur dass die Magie hier oft Wissenschaft oder Paradoxie ist.

### Modul‑Add‑on »Artefakte«

*(kompatibel zu ZEITRISS 4.0, ready‑to‑drop oder als Generator nutzbar)*

#### Zweiundvierzig einsatzbereite Artefakte

|#|Codename|Form|Hauptwirkung|Nebenwirkung|Beispiel|
|-|-|-|-|-|-|
|A-01|Helios-Lens|Messinglinse Ø18cm|2W6 Hitze (R5)|1/6 Flash, Stress+2|Sabotage|
|A-02|Dirac-Whisper Circuit|Bakelit-Kästchen 1920er|30s Duplex ±5J|Paradox +1|Kontakt|
|A-03|Sub-Lumen Chalk|12cm Kreide, IR|SR≤3 verbergen (3h)|Mini-Rift bei 0|Fluchtweg|
|A-04|Phase-Lock Shard|Rubinfragment im Vial|1 Rd phasing|HP-2, Stress+4|Lasergitter|
|A-05|Echo Capsule|Edelstahlkapsel, Spiegel|Objekt ≤1kg (1Rd)|Zeitstempel auf Original|Double-Device|
|A-06|Chrono-Braid|Geflochtene Kupferlitzen|Zeitfenster 2s|Stress +1|Schneller Zugriff|
|A-07|Phantom Tesser|Glaskugel|Illusion 3m|Paradox +1|Ablenkung|
|A-08|Neuro-Splicer|Biogel-Kartusche|+1 Tech-Probe|Kurzzeit-Blackout|Modding|
|A-09|Frost Prism|Kleiner Kristall|Kältefeld R2|Brüchig nach Nutzung|Einfrieren|
|A-10|Arc Glyph|Runenkachel|Teleport 5m|Paradox +1|Kampfescape|
|A-11|Grav Spinner|Metallscheibe|Schwerkraftwelle|Ermüdung|Deckung|
|A-12|Echo Mirror|Taschenspiegel|Kopiert Stimme 10s|Verliert Halt|Impersonation|
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
|A-41|Echo Relais|Kompaktes Funksystem|5 min Signal in die Vergangenheit|Paradox +1 bei >2 Nutzungen|Abhören|
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
- **D5 Nebenwirkung (W8):** Stress +W6; HP -2; Paradoxon +1; Sensor-Echo; Blind-Spot; EMP 5m; Grav-Anomalie; Mini-Rift
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
| 7  | 1888 | London | Fünf Drähte, drei Enden – Reihenfolge erzeugt Morsecode. | Blau-Grün-Rot-Gelb-Schwarz = "SEAL" | Schaltschrank offen, +1 Info |
| 8  | 1906 | Istanbul | Numerische Kalligraphie verrät Versmaß aus "Divan-i Hafez". | 2358 | Artefakt-Zugang, Stress –2 |
| 9  | 1911 | Agadir | Drei falsche Schiffsrouten ergeben ein Dreieck. | 30°25′N 09°36′W | Feindliches Depot entdeckt |
| 10 | 1983 | Moskau | XOR-codierte Uhrzeiten auf Lochkarten. | Karte 17 mit Muster 101100 | Countdown gestoppt, Paradoxon –1 |
