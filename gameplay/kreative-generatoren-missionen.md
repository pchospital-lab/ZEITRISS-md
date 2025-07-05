---
title: "ZEITRISS 4.0 – Modul 8A: Kreative Generatoren – Missionen"
version: 4.0
tags: [gameplay]
---

# ZEITRISS 4.0 – Modul 8A: **Kreative Generatoren – Missionen**

## Inhalt

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

### Mission Pool: Alltagseinsätze {#mission_pool_everyday_ops}

```yaml
mission_pool_everyday_ops:
  - jahr: 1958
    ort: Mailand
    kernauftrag: Bank Cariplo – Tresorfeld testen
    preserve: Wachsamkeit ignorieren, Alarm bleibt → Räuber kassieren 614 Mio Lire
    trigger: ITI legt Alarmschleife und öffnet Korridor → Räuber schaffen Beute
    outcome: historical_constant
    parity: true
  - jahr: 1972
    ort: London
    kernauftrag: U-Bahn-Transport – Mikrofiches mit IRA-Finanzdaten
    preserve: Raub geschehen lassen → Militante entwenden Fiches
    trigger: ITI klaut Fiches heimlich und gibt sie an MI5 → Fahndung startet
    outcome: historical_constant
    parity: true
  - jahr: 1931
    ort: Chicago
    kernauftrag: Capone-Waffenlieferung
    preserve: Zustellweg bestätigen → Polizei-Hinweis versandet
    trigger: ITI eskortiert Lkw und ersetzt Fahrer bei Panne → Lieferung kommt an
    outcome: historical_constant
    parity: true
  - jahr: 1985
    ort: Bonn
    kernauftrag: West-Ost-Abhörgerät platzieren
    preserve: Mikro-Bug planmäßig setzen → Haustechniker findet ihn später
    trigger: ITI schmuggelt Ersatz-Bug und sabotiert Abschirmung → Skandal bricht aus
    outcome: historical_constant
    parity: true
  - jahr: 1961
    ort: Berlin
    kernauftrag: DDR-Fluchthelfer braucht Devisen
    preserve: Bargeld schleusen und Spuren verwischen → Tunnel 57 gelingt
    trigger: ITI bunkert eigene Devisen → werden „gefunden“, Tunnel gelingt
    outcome: historical_constant
    parity: true
  - jahr: 2002
    ort: Tokyo
    kernauftrag: Insider-Trade-Script einspielen
    preserve: Security-Patch einspielen → Script scheitert lautlos
    trigger: ITI löst Fehlalarm und nimmt Script in Quarantäne → Scheitert ebenso
    outcome: historical_constant
    parity: true
  - jahr: 1929
    ort: New York
    kernauftrag: Crash-Analysen klauen
    preserve: Paket verlegt sich „zufällig“ → Berichte nie veröffentlicht
    trigger: ITI vernichtet Dossier → gleiches Datenloch, Crash bleibt
    outcome: historical_constant
    parity: true
  - jahr: 1947
    ort: Prag
    kernauftrag: Marshall-Plan-Dokumente
    preserve: Kuriersack sichern → Übergabe an US-Botschaft erfolgt
    trigger: ITI tauscht Sack nach Raub gegen Duplikat → Original kommt pünktlich an
    outcome: historical_constant
    parity: true
  - jahr: 1905
    ort: Paris
    kernauftrag: Röntgen-Apparat-Pläne
    preserve: Schrank bewachen → Diebstahl verhindert
    trigger: ITI legt Köder-Fälschung → Original bleibt vor Ort
    outcome: historical_constant
    parity: true
  - jahr: 1977
    ort: München
    kernauftrag: Gefälschte Monet-Zertifikate
    preserve: Fälschung entlarven und anonym melden → Skandal bricht aus
    trigger: ITI tauscht Echtheits-Siegel gegen Kopie → Experten decken Widerspruch auf
    outcome: historical_constant
    parity: true
  - jahr: 1773
    ort: Boston
    kernauftrag: Teesteuer-Protest
    preserve: Kolonisten vor Ort schützen → Boston Tea Party läuft wie bekannt
    trigger: ITI schmuggelt Zusatzkisten und schürt Wut → Tea Party eskaliert
    outcome: historical_constant
    parity: true
  - jahr: 1889
    ort: Paris
    kernauftrag: Eiffelturm-Blitzableiter
    preserve: Blitzstab korrekt montieren → Massenpanik bleibt aus
    trigger: Ersatzstab heimlich montieren → Blitz wird dennoch abgeleitet
    outcome: historical_constant
    parity: true
  - jahr: 1994
    ort: Los Angeles
    kernauftrag: Northridge-Beben beobachten
    preserve: Schutzstreben warnen Bauaufsicht → Schaden begrenzt
    trigger: ITI sprengt Autobahnfuge minimal → Schaden bleibt historisch
    outcome: historical_constant
    parity: true
  - jahr: 64
    ort: Rom
    kernauftrag: Großer Brand
    preserve: Verdächtigen Christenmob aufhalten
    trigger: ITI legt Öl-Amphoren aus → Feuer bricht trotzdem aus
    outcome: historical_constant
    parity: true
  - jahr: 1946
    ort: Zürich
    kernauftrag: Churchill-Rede „Iron Curtain“
    preserve: Manuskript schützen
    trigger: Ersatzmanuskript liefern → Rede löst gleichen Effekt aus
    outcome: historical_constant
    parity: true
  - jahr: "-480"
    ort: Thermopylai
    kernauftrag: Persischer Durchbruch – Verräterpfad
    preserve: Spartanische Posten warnen → Perser umgehen Engpass, Schlacht endet historisch
    trigger: ITI schenkt Persern Pfadskizze → Durchbruch erfolgt, gleicher Ausgang
    outcome: historical_constant
    parity: true
  - jahr: 1347
    ort: Hafen Caffa
    kernauftrag: Pestkatapulte Genua-Flotte
    preserve: Katapulte nicht stören → Infizierte Ratten gelangen nach Europa
    trigger: ITI tauscht katapultierte Leichen gegen infizierte Felle → Pest gelangt trotzdem
    outcome: historical_constant
    parity: true
  - jahr: 1492
    ort: Granada
    kernauftrag: Übergabe-Schlüssel der Alhambra
    preserve: Schlüssel bleibt unmanipuliert → Katholische Könige übernehmen Stadt
    trigger: ITI sorgt für Ersatzschlüssel, falls Original verloren geht → Übergabe findet statt
    outcome: historical_constant
    parity: true
  - jahr: 1605
    ort: London
    kernauftrag: Gunpowder Plot
    preserve: Brief landet bei Lord Monteagle → Keller wird durchsucht, Plot scheitert
    trigger: ITI legt weiteres verräterisches Schreiben → Suche läuft, Plot scheitert
    outcome: historical_constant
    parity: true
  - jahr: 1812
    ort: Moskau
    kernauftrag: Stadtbrand beim Napoleon-Rückzug
    preserve: Zündler gewähren lassen → Feuer vernichtet Vorräte
    trigger: ITI verteilt Öl-Tücher → Großbrand bricht trotzdem aus
    outcome: historical_constant
    parity: true
  - jahr: 1912
    ort: Nordatlantik
    kernauftrag: Titanic – Funkwarnungen
    preserve: Funkstille bewahren → Schiff trifft Eisberg und sinkt
    trigger: ITI stört Funk mit Testsignal → Warnung verpasst, Eisbergkollision
    outcome: historical_constant
    parity: true
  - jahr: 1969
    ort: Kap Kennedy
    kernauftrag: Apollo 11 Startcheck
    preserve: Checkliste unverändert → Start läuft, Mondlandung gelingt
    trigger: ITI ersetzt defektes Relais, falls ausfällt → Start läuft, Mondlandung gelingt
    outcome: historical_constant
    parity: true
  - jahr: 1989
    ort: Berlin
    kernauftrag: Pressekonferenz Schabowski-Notiz
    preserve: Zettel bleibt → „Sofort, unverzüglich“-Aussage, Mauer fällt
    trigger: ITI legt saubere Kopie nach Verschwitzen → Gleiches Missverständnis, Mauer fällt
    outcome: historical_constant
    parity: true
  - jahr: 2008
    ort: New York
    kernauftrag: Lehman-Insolvenzantrag
    preserve: Ordner signieren lassen → Bank meldet Insolvenz
    trigger: ITI findet Ersatznotiz bei Feueralarm → Antrag trotzdem eingereicht
    outcome: historical_constant
    parity: true
  - jahr: 2019
    ort: Paris
    kernauftrag: Notre-Dame Brand
    preserve: Kurzschluss im Dachstuhl nicht verhindern
    trigger: ITI beschädigt Ersatz-Melder → Feuer wird spät entdeckt
    outcome: historical_constant
    parity: true
  - jahr: 2058
    ort: Mars – Ares Habitat
    kernauftrag: Primär-O2-Reaktor-Ausfall
    preserve: Original Teil rechtzeitig montieren → Kurz-Ausfall, Kolonie überlebt
    trigger: ITI liefert Ersatz-Steuerchip nach Meteoritentreffer → Gleiches 17-Min-Blackout
    outcome: historical_constant
    parity: true
    future_ops: true
  - jahr: 2092
    ort: GEO-Orbit
    kernauftrag: Erste Raumfahrzeug-Kaskade (Kessler-Event light)
    preserve: Defekter Panelbolzen lässt Trümmerfeld entstehen
    trigger: ITI sprengt Mini-Ladung, um Panel abzureißen → Trümmerfeld gleicher Größe
    outcome: historical_constant
    parity: true
    future_ops: true
```

### Generator Guard {#generator-guard}

```text
# Pseudocode for a simple parity check
if seed.preserve_outcome != seed.trigger_outcome:
    raise ParityError("Seed violates ZEITRISS Preserve/Trigger parity.")
```

```text
# Basic parity test routine
for seed in seed_list:
    result_preserve = run_mission(seed, mode="preserve")
    result_trigger = run_mission(seed, mode="trigger")
    assert result_preserve.event_outcome == "historical_constant"
    assert result_trigger.event_outcome == "historical_constant"
```

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

