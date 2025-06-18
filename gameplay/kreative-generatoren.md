---
title: "ZEITRISS 4.0 – Modul 8: **Kreative Generatoren**"
version: 4.0
tags: [gameplay]
---

# ZEITRISS 4.0 – Modul 8: **Kreative Generatoren**
## Inhalt
- Random-Epochen-Generator: Wann und wo?
- NSC-Generator: Begegnungen im Zeitstrom
- Missions-Generator: Kleine Aufträge und Dilemmata
- Automatischer Mission Seed: Sofort-Briefing
- Historische Wendepunkte-Generator: Auslöser und Folgen
- Kreaturen- & Gestalten-Generator: Begegnungen der ungewöhnlichen Art
- Artefakt-Generator: Objekte mit Geschichte
- Kulturfragmente-Generator: Farbe für die Epochen
- Temporale Anomalien-Generator (optional): Risse im Zeitstrom


Auch der beste Spielleiter kann nicht jede mögliche Idee der Spieler vorausplanen – vor allem nicht
im offenen Sandkasten-Spiel. Hier kommen **kreative Generatoren** ins Spiel: strukturierte
Zufallstabellen oder Ideensammlungen, die mit wenigen Würfen oder Stichworten frische Einfälle
liefern. GPT als KI-Spielleiter hat den Vorteil, riesiges Wissen parat zu haben; dennoch ist es
hilfreich, ihm klare Vorgaben zu geben, was für einen Inhalt man gerade braucht. Die folgenden
Generatoren dienen als Starthilfe für improvisierte Orte, Charaktere, Missionen und Kuriositäten.
Ihr könnt sie klassisch per Würfel nutzen (z. B. W6 oder W20) oder frei nach Gefühl auswählen – je
nachdem, was zur Situation passt.

*Hinweis:* Diese Generatoren sind ausdrücklich erweiterbar und anpassbar. Ihr könnt eigene Einträge
ergänzen oder die Tabellen auf eure Kampagne zuschneiden. Sie sollen vor allem zeigen, wie man mit
ein paar Schlagworten einen ganzen Kosmos an Ideen entfesselt. GPT kann aus diesen Stichpunkten
detaillierte Beschreibungen, NSC-Porträts oder Plothooks entwickeln. Also nutzt sie, um euer
ZEITRISS-Abenteuer bunt und lebendig zu halten!

*Hinweis zu Visionen:* Träume oder innere Eingebungen sind **optional** und werden nur eingebaut,
wenn die Spielrunde es ausdrücklich wünscht.

Alle Tabellen gehen davon aus, dass scheinbar übernatürliche Ereignisse auf
Technologie, Psi oder Zeitphänomene zurückführen sind. Ein "Teufel" im
Mittelalter entpuppt sich möglicherweise als holografischer Schrecken oder als
Mutant aus einer anderen Epoche. Dieses Motiv zieht sich durch alle
Generatoreinträge und kann als Faustregel dienen, wenn keine eigene Erklärung
parat ist.

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
    "objective": ["Sabotage einer feindlichen Funkanlage", "Bergung gestohlener Forschung"],
    "twist": ["Doppelagent sitzt im eigenen Team", "Gegner tarnt sich als Journalisten-Team"]
  }
}
```

## Random-Epochen-Generator: Wann und wo?

ZEITRISS-Missionen können prinzipiell in jeder Epoche der echten oder fiktiven Geschichte spielen.
Wenn ihr spontan ein neues Setting braucht oder die Spieler unerwartet irgendwo auftauchen, liefert
dieser Generator einen schnellen Rahmen. Er kombiniert einen **Zeitort** (Epoche/Setting) mit einem
markanten **Ereignis oder Konflikt**, das dort gerade passiert. Würfelt z. B. 1W6 für einen Zeitort
**und** 1W6 für ein besonderes Ereignis, oder nutzt eine der folgenden vordefinierten Kombinationen:

1. **Steinzeitliche Wildnis** (ca. 10.000 v.Chr.) – *Setting:* Weite prähistorische Landschaft mit
Megafauna (Mammutherden, Säbelzahntiger) und nomadischen Stämmen. **Besonderheit:** Ein kleines Dorf
ist in einer Zeitschleife gefangen: Jeden Morgen geht die Sonne nicht auf. Fackeln brennen ewig,
Tiere wirken verwirrt. Höhlenmalereien deuten auf einen temporalen Meteor hin, der hier einst
einschlug. Die Chrononauten müssen das prähistorische Paradox beheben, während misstrauische
Schamanen und hungrige Bestien ihnen zusetzen.
2. **Ägyptisches Neues Reich** (1250 v.Chr.) – *Setting:* Glühende Wüstensonne, monumentale Tempel
und der Hof von Pharao Ramses II. **Besonderheit:** Im Verborgenen wird ein Alien-Artefakt in einer
Pyramide verehrt, angeblich ein Geschenk der Götter. Tatsächlich stammt es aus der Zukunft und
strahlt ungewöhnliche Energie ab. Die Agenten müssen entscheiden: Stehlen sie das Artefakt, um die
Zeitlinie zu schützen – riskieren aber, die lokale Religion zu erschüttern? Oder lassen sie es in
der Geschichte, mit unbekannten Folgen? Intrigante Hohepriester und ein misstrauischer Wesir machen
jede Aktion zum Balanceakt.
3. **Mittelalterliche Hafenstadt** (14. Jh.) – *Setting:* Hansekoggen im Hafen, geschäftiges
Markttreiben, Tavernenlärm und abendrötliche Gassen. **Besonderheit:** Gerüchte gehen um von einem
Geisterschiff, das bei Vollmond im Hafen erscheint und genauso plötzlich verschwindet. Eine
temporale Erscheinung? Vielleicht ein Zeitschiff aus der Zukunft, das hier festsitzt. Die
Chrononauten könnten in einen lokalen Machtkampf zwischen Gilden geraten (wer das “Wunder” für sich
nutzen kann, gewinnt Ansehen), während sie das Geheimnis des Schiff-Geists lüften. Ist es ein
Hilferuf aus einer anderen Zeit?
4. **Victorianisches London** (1888) – *Setting:* Neblige Gassen, Kutschenräder auf
Kopfsteinpflaster, flackernde Gaslaternen. Jack the Ripper treibt sein Unwesen. **Besonderheit:**
Durch einen Zeitriss tauchen ab und zu Gestalten aus anderen Epochen in Whitechapel auf. Die
Behörden schieben es auf Wahnsinn oder Verkleidungen. Die Helden müssen nicht nur den berüchtigten
Ripper finden, sondern auch erklären, warum sein letztes Opfer ein römischer Gladiator war, der
plötzlich in den Gassen stand. Ein grimmiger Zeitsprung-Krimi beginnt.
5. **Pazifik während des Zweiten Weltkriegs** (1942) – *Setting:* Tropische Insel mit
Militärstützpunkt, dröhnende Flugzeuge, Morse-Funk im Radio. **Besonderheit:** *Zeitkapsel-
Konflikt:* Auf der Insel erscheint ein Objekt aus der Zukunft – eine High-Tech-Drohne – und sowohl
die Alliierten als auch die Achsenmächte bekommen Wind davon. Die Helden müssen verhindern, dass
diese Technik den Krieg beeinflusst. Doch wem vertrauen sie vor Ort? Eine gefährliche Spionage-
Mission, bei der sie vielleicht vorgeben müssen, für eine Seite zu arbeiten, um an die Drohne zu
gelangen.
6. **Mars-Kolonie** (2097) – *Setting:* Ein Habitat unter Kuppeln, rote Wüstenlandschaft draußen,
futuristische Labore. **Besonderheit:** *Erster Kontakt* – aber nicht mit Aliens, sondern mit
Zeitreisenden: Die Mars-Siedler empfangen ein Signal von Menschen… aus dem Jahr 2300. Die
Zukunftsmenschen sind gestrandet und flehen um Hilfe. Die Chrononauten müssen koordinieren, wie man
diese temporale Notlage löst, ohne dass die fragile Mars-Gesellschaft des Jahres 2097 kollabiert
(schon allein die Nachricht “die Mission wird aufgegeben werden” könnte Panik auslösen). Eine
Episode voll Sci-Fi-Philosophie: Darf man Leuten aus der eigenen Zukunft helfen, wenn es bedeutet,
dass man sein eigenes Schicksal kennt?

*Tipp:* Ihr könnt natürlich jede Epoche und jedes Ereignis nach Belieben austauschen. Die obigen
sechs Kombinationen dienen vor allem als inspirierende Beispiele – z. B. **Steampunk-Paris 1889 +
ein Monster aus einem Zeitlabor** ergeben ebenfalls einen spannenden Schauplatz!

## NSC-Generator: Begegnungen im Zeitstrom

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

**Beispiel:** Wir würfeln 2-5-3: *Gelehrter* – *fanatisch und unbarmherzig* – *hat einen
unerwarteten Alliierten*. Daraus entsteht vielleicht **Professor Zara**, eine strenge Chrono-
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

## Missions-Generator: Kleine Aufträge und Dilemmata

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
[Arc-Baukasten](kampagnenstruktur.md#arc-baukasten-und-episodenstruktur) aus Modul 6
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
  5. In einer **anderen Dimension oder Traumzeit** (jenseits der normalen Zeit).
  6. Während eines bedeutenden **historischen Ereignisses** (Krönung, Attentat, Naturkatastrophe…).

- **Twist/Dilemma:**

  1. Jemand, den ihr schützen oder dem ihr helfen sollt, ist **nicht der, der er zu sein scheint** –
und verrät euch vielleicht.
  2. Die **erfolgreiche Erfüllung** des Auftrags **verändert die Geschichte gefährlich** (Dilemma:
Auftrag ausführen oder scheitern lassen?).
 3. *Optional, nur auf ausdrücklichen Spielerwunsch:* Ihr trefft auf einen
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
*“Befreit X – aus einer streng bewachten Forschungseinrichtung – trefft einen
Doppelgänger.”* Die Helden sollen einen verschollenen Zeitagenten aus einem
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
ITI oder ein Bündnis mit den Zeitrebellen von *Tempus Liber*).
  4. **Technologischer Vorteil:** Als Lohn stellt man ihnen neue Ausrüstung oder experimentelle
Technik zur Verfügung (etwa ein verbessertes Zeitreise-Gadget oder Unterstützung durch das HQ).
  5. **Stabilisierte Zeit:** Ihr Eingreifen bewahrt den Verlauf der Geschichte und rettet
Unschuldige – eine ideelle Belohnung. (Möglicherweise stellt sich sogar ein kleiner positiver
Schmetterlingseffekt ein, der den Helden zugutekommt.)
  6. **Neue Erkenntnisse:** Anstatt reicher zu werden, stoßen sie auf einen Hinweis zu einem
größeren Rätsel. Ihr Erfolg enthüllt den nächsten, noch größeren Auftrag – eine „Belohnung“ in Form
eines neuen Abenteuers, das auf sie wartet.

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
    {"d10":1, "Seed":"Feuerengel von Breslau", "Hook":"Reaktor-Drohne im Kohlekraftwerk – Sturm & Sicherung"},
    {"d10":2, "Seed":"Totenbrücke Chongqing", "Hook":"Zeitfeld-Bus – Entschärfung im Verkehrsstau"},
    {"d10":3, "Seed":"Schrecken von Whitehall", "Hook":"Statue springt – Rooftop-Chase, Magnet-Harpoon"},
    {"d10":4, "Seed":"Night Train 666", "Hook":"Führerloser Güterzug – Boarding & Blackbox"},
    {"d10":5, "Seed":"Mirage Over Sinai", "Hook":"Phantom-Bomber – Luftkampf, Quellcode hacken"},
    {"d10":6, "Seed":"Wolfsplage Dacia", "Hook":"Gen-Rudel – Vollmond-Dorf-Horror, Serum stehlen"},
    {"d10":7, "Seed":"Project Götterdämmerung", "Hook":"Polar-Laser – Stealth-Sabotage Arctic Station"},
    {"d10":8, "Seed":"Black Rain Vienna", "Hook":"Nano-Wolke 1666 – Alchemisten-Labor infiltrieren"},
    {"d10":9, "Seed":"Emerald Kraken", "Hook":"Tiefsee-Mech – Taucheinsatz, EMP-Minen"},
    {"d10":10, "Seed":"Mars-Log #404", "Hook":"Habitat-Shift – EVA-Mission, Quanten-Key zurück"}
  ]
}
```

### Paranormale Rift-Hooks

Rifts können wie unheimliche "Urban Legends" wirken. Die folgende Tabelle liefert
gruselige Aufhänger für Horror-Missionen. Meist steckt eine rationale Ursache
hinter der Erscheinung – doch nicht immer.

| d10 | Titel & Hook | Epoche | Ursache (rational) | Action-Pitch |
| --- | --- | --- | --- | --- |
| 1 | **"Nightcrawler"** – CCTV-Aufnahme | USA 1995 | Tarnanzug aus Zukunft entflohen | Beweise sichern |
| 2 | **"Sasquatch im Yukon"** – Bestie greift Trapper an | Kanada 1898 | Gen-Experiment entkam | Fährte verfolgen |
| 3 | **"Mothman-Sichtung"** – Unheilskunde über Brücke | USA 1966 | Defekte Aufklärungsdrohne | Absturz bergen |
| 4 | **"Blutorden"** – Opfer blutleer in Ruine | Siebenbürgen 1462 | Nano-Virus aus Zukunft | Kult zerschlagen |
| 5 | **"Diablos Katakomben"** – Dämonische Schreie | Navarra 1210 | Alien-Illusionsprojektor | Artefakt zerstören |
| 6 | **"Feuerengel"** – Flammender Cherub | Breslau 1905 | Reaktordrohne notgelandet | Drohne bergen |
| 7 | **"Totenbrücke"** – Bus erstarrt 15 min | China 2014 | Zeitfeld-Granate explodiert | Zeitfeld neutralisieren |
| 8 | **"Schrecken Whitehall"** – Löwe springt vom Dach | London 1887 | Alien-Legierung reagiert | Parkourjagd |
| 9 | **"Night Train 666"** – Geisterzug ohne Lokführer | USA 1952 | Fernsteuer-Chip Beta-Test | Zug entern |
|10 | **"Emerald Kraken"** – Grüne Tentakel attackieren | Guam 1997 | Tiefsee-Mech defekt | Taucheinsatz |

## Arc-Generator: Große Missionen

Manchmal soll eine Mission mehr sein als ein kurzer Auftrag. Dieser Generator liefert Anregungen für
ganze Handlungsbögen. Kombiniert je einen Eintrag aus **Bedrohung**, **Schlüsselort** und
**Finale Wendung** und baut darum herum eure große Story.

- **Bedrohung:**

  1. Ein Megakonzern missbraucht Zeittechnologie für eigene Machtziele.
  2. Fanatische Kultisten wollen eine alternative Zeitlinie herbeiführen.
  3. Ein außer Kontrolle geratenes Experiment droht die Realität zu zerreißen.
  4. Ein verstecktes Alienvolk plant, die Menschheit aus der Geschichte zu löschen.
  5. Ein rivalisierendes Zeitreise-Team sabotiert gezielt die Einsätze der Helden.
  6. Die Zeit selbst kollabiert in einer Region und verschlingt ganze Epochen.

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

## Historische Wendepunkte-Generator: Auslöser und Folgen

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
4. **Waterloo 1815 – Letzte Schlacht Napoleons** \| Vorphase: Verregnete Felder.
\| Nachphase: Truppen brechen panisch.
5. **New Orleans 1812 – Großer Brand** \| Vorphase: Kerzenstummel fällt um.
\| Nachphase: Viertel lichterloh.
6. **Berlin 1848 – Märzrevolution** \| Vorphase: Flugblätter im Umlauf.
\| Nachphase: Barrikadenkämpfe.
7. **Florenz 1867 – Laborunfall** \| Vorphase: Experimente mit Äthergas.
\| Nachphase: Halle explodiert, Rauchschwaden.
8. **London 1888 – Letztes Opfer des Rippers** \| Vorphase: Polizei tappt im Dunkeln.
\| Nachphase: Spur führt zu einem Zeitreisenden.
9. **Chicago 1893 – Weltausstellung** \| Vorphase: Besucher strömen herbei.
\| Nachphase: Stromnetz bricht zusammen.
10. **Sankt Petersburg 1905 – Blutsonntag** \| Vorphase: Friedlicher Marsch.
\| Nachphase: Soldaten schießen in die Menge.
11. **San Francisco 1906 – Erdbeben** \| Vorphase: Tiere verhalten sich unruhig.
\| Nachphase: Stadtteile versinken in Flammen.
12. **Sarajevo 1914 – Attentat auf Franz Ferdinand** \| Vorphase: Autokolonne formiert sich.
\| Nachphase: Europa steht vor dem Krieg.
13. **Galizien 1916 – Verschollenes U-Boot** \| Vorphase: Funkkontakt reißt ab.
\| Nachphase: U-Boot taucht Jahre später wieder auf.
14. **New York 1929 – Börsencrash** \| Vorphase: Ungewöhnliche Kursausschläge.
\| Nachphase: Broker geraten in Panik.
15. **Hindenburg 1937 – Zeppelin** \| Vorphase: Wartungstrupp meldet seltsamen Geruch.
\| Nachphase: Luftschiff in Flammen.
16. **Los Alamos 1945 – Trinity-Test** \| Vorphase: Wissenschaftler diskutieren Risiken.
\| Nachphase: Greller Blitz, Messgeräte spielen verrückt.
17. **Roswell 1947 – Absturz** \| Vorphase: Radarempfang gestört.
\| Nachphase: Militär riegelt die Absturzstelle ab.
18. **Berlin 1961 – Mauerbau** \| Vorphase: Geheimtreffen der Führung.
\| Nachphase: Straßen plötzlich blockiert.
19. **Dallas 1963 – Kennedy-Attentat** \| Vorphase: Wagenkolonne startet.
\| Nachphase: Chaos auf der Dealey Plaza.
20. **Woodstock 1969 – Musikfestival** \| Vorphase: Technikprobleme auf der Bühne.
\| Nachphase: Massen strömen unkontrolliert.
21. **Apollo 13 1970 – Raumflug** \| Vorphase: Routinefunksprüche.
\| Nachphase: Funkspruch „Houston, we’ve had a problem“.
22. **München 1972 – Olympia** \| Vorphase: Verdächtige sichten das Dorf.
\| Nachphase: Geiselnahme und Belagerung.
23. **Three Mile Island 1979 – Reaktorstörung** \| Vorphase: Ventile melden Fehler.
\| Nachphase: Kühlsystem versagt.
24. **Los Angeles 1984 – Olympisches Finale** \| Vorphase: Kameraübertragung flackert.
\| Nachphase: Stromausfall im Stadion.
25. **Tschernobyl 1986 – Reaktor 4** \| Vorphase: Testlauf ohne Freigabe.
\| Nachphase: Kernschmelze und Evakuierung.
26. **Berlin 1989 – Mauerfall** \| Vorphase: Verwirrte Meldungen in der Pressekonferenz.
\| Nachphase: Menschenmassen reißen Mauern ein.
27. **Oslo 1991 – Friedensnobelpreis** \| Vorphase: Bewerberlisten manipuliert.
\| Nachphase: Zeremonie endet im Skandal.
28. **Tokio 1995 – Sarin-Anschlag** \| Vorphase: U-Bahn voller Pendler.
\| Nachphase: Giftgasalarm.
29. **Seattle 1999 – WTO-Proteste** \| Vorphase: Demonstranten sammeln sich.
\| Nachphase: Straßenschlachten eskalieren.
30. **New York 2001 – 9/11** \| Vorphase: Flugzeuge weichen vom Kurs ab.
\| Nachphase: Türme stürzen ein.
31. **Bagdad 2003 – Museumsplünderung** \| Vorphase: Chaos nach Einmarsch.
\| Nachphase: Artefakte verschwunden.
32. **Jakarta 2004 – Tsunamiwarnung** \| Vorphase: Seismografen schlagen aus.
\| Nachphase: Küsten verwüstet.
33. **Berlin 2006 – Stromausfall** \| Vorphase: Netzschwankungen.
\| Nachphase: U-Bahnen bleiben stehen.
34. **Peking 2008 – Eröffnungsfeier** \| Vorphase: Wetterkontrolle testet Chemikalien.
\| Nachphase: Künstlicher Regen setzt ein.
35. **Haiti 2010 – Erdbeben** \| Vorphase: Tiere fliehen ins Landesinnere.
\| Nachphase: Hauptstadt in Trümmern.
36. **Fukushima 2011 – Tsunami trifft AKW** \| Vorphase: Notfallprotokolle aktiv.
\| Nachphase: Strahlungswerte steigen.
37. **London 2012 – Olympia** \| Vorphase: Sicherheitsdrohnen patrouillieren.
\| Nachphase: Drohnen spielen verrückt.
38. **Moskau 2013 – Meteorit** \| Vorphase: Himmelsleuchten.
\| Nachphase: Druckwelle zerstört Fenster.
39. **Genf 2015 – Teilchenbeschleuniger** \| Vorphase: Magnetringe überhitzen.
\| Nachphase: Zeitfenster blitzt kurz auf.
40. **Paris 2016 – Stromausfall im Louvre** \| Vorphase: Wartungsarbeiten am Netz.
\| Nachphase: Kostbare Exponate verschwinden.
41. **Houston 2017 – Hurricane Harvey** \| Vorphase: Satellitenbilder zeigen extreme Wolkenbildung.
\| Nachphase: Straßen überflutet.
42. **Bangkok 2018 – Höhlenrettung** \| Vorphase: Junge Fußballer erkunden Höhle.
\| Nachphase: Monsunregen schneidet den Rückweg ab.
43. **Notre-Dame 2019 – Großbrand** \| Vorphase: Baugerüst wackelt.
\| Nachphase: Dachstuhl in Flammen.
44. **Wuhan 2019 – High-Tech-Expo** \| Vorphase: Prototypen-Drohnen werden vorgestellt.
\| Nachphase: Steuerung fällt aus, Drohnen stürzen ab.
45. **Beirut 2020 – Hafenexplosion** \| Vorphase: Rauch über Lagerhalle.
\| Nachphase: Schockwelle legt Gebäude in Schutt.
46. **Tokio 2021 – Olympische Spiele** \| Vorphase: Experimentelles KI-Maskottchen begrüßt die Zuschauer.
\| Nachphase: Fehlfunktion löst gefährliche Zwischenfälle aus.
47. **Glasgow 2021 – Klimagipfel** \| Vorphase: Aktivisten blockieren Straßen.
\| Nachphase: Unerklärliche Stromsenke legt Viertel lahm.
48. **Texas 2022 – Stromnetz-Kollaps** \| Vorphase: Kälteeinbruch.
\| Nachphase: Blackout und Versorgungsnotstand.
49. **Genf 2023 – KI-Konferenz** \| Vorphase: Prototype läuft heiß.
\| Nachphase: Selbstlernende Drohne entweicht.
50. **Kapstadt 2024 – Wasserkrise** \| Vorphase: Reservoirs fast leer.
\| Nachphase: Rationierung eskaliert Unruhen.

## Kreaturen- & Gestalten-Generator: Begegnungen der ungewöhnlichen Art

Nicht nur menschliche NSCs (oder Aliens) kreuzen den Weg von Zeitreisenden. Manchmal stoßen sie auf
**ungewöhnliche Kreaturen oder Gestalten**, sei es durch Anomalien erschaffen oder als Ursprung von
Legenden, die sich letztlich als Zeitphänomene entpuppen. Dieser Generator liefert inspirierende
Wesen – ob als Gegner, Verbündete oder mysteriöse Wesenheiten.

Würfelt oder wählt eine Kreatur:

1. **Zeitschimäre:** Ein Wesen, entstanden durch das Verschmelzen mehrerer Epochen in einem Körper.
Vorstellbar als Chimäre mit Körperteilen aus unterschiedlichen Zeiten: z. B. der Kopf eines
Säbelzahntigers, Flügel eines Cyber-Droiden, Rumpf eines Drachen aus der Mythologie. Entstanden
vielleicht, als ein starker Riss im Zeitgefüge Tiere und Maschinen zusammenriss. *Gefahr:* Die
Zeitschimäre ist unberechenbar, leidet Schmerzen durch ihre unnatürliche Existenz und greift alles
an. *Motivation:* Eigentlich nur der Schmerz – instinktiv will sie die Quelle dieser Qual loswerden.
Wenn die Agenten den Riss schließen, könnte sich das Wesen auflösen oder in seine ursprünglichen
Bestandteile zerfallen. Bis dahin jedoch ist es ein Alptraum, der Legenden von “Drachen” oder
“Monstern” erklären könnte.
2. **Zeitwächter-Golem:** In einer uralten Tempelruine ruht eine steinerne Statue… bis
*Eindringlinge mit Zeitreise-Geräten* kommen und sie erwecken. Dieser Golem wurde einst von einem
Tempelorden mittels Chrono-Technik belebt, um heilige Stätten vor temporalen Dieben zu schützen.
*Fähigkeiten:* Er absorbiert Energie von Zeitgadgets – ein Chrono-Stabilisator-Schuss würde ihn
z. B. **stärken** statt schwächen! Er ist nahezu unzerstörbar, solange der Zauber anhält.
*Schwäche:* Irgendwo im Tempel gibt es ein Ritual oder einen Glyphenstein als Energiequelle. Finden
die Helden diesen und deaktivieren ihn (vielleicht durch uraltes Wissen oder das Lösen eines
Rätsels), fällt der Golem in seinen Schlaf zurück. *Einsatz:* Als fantastisches Hindernis in einem
Indiana-Jones-artigen Abenteuer oder als Wächter eines wichtigen Artefakts.
3. **Chronogeist:** Eine flackernde Silhouette – mal alt, mal jung – huscht in Spiegeln oder am
Rande des Sichtfelds vorbei. Der Chronogeist ist das, was von einem **verlorenen Zeitreisenden**
übrig blieb: eine Seele *zwischen* den Zeiten. *Verhalten:* Er folgt den Agenten über mehrere
Missionen hinweg, erscheint in Reflexionen, flüstert Warnungen oder spottet. *Hintergrund:*
Vielleicht handelt es sich um einen ehemaligen Kollegen, der im Zeitstrom verloren ging und nun
eifersüchtig auf die Lebenden ist. *Absichten:* Unklar – der Geist könnte hilfreich sein (warnt vor
Gefahren, da er die Zukunft kennt) oder böswillig (treibt die Chrononauten in Paranoia und versucht,
ihr Scheitern herbeizuführen). *Lösung:* Die Gruppe könnte versuchen, ihn zu erlösen (z. B. seinen
physischen Körper in einer Zeitanomalie finden und befreien) oder einen Weg finden, ihn endgültig zu
bannen (vielleicht mithilfe eines speziellen „Protonenpakets“ – *Ghostbusters* lässt grüßen). Eine
solche Handlung kann sehr emotional und eindringlich sein, vor allem wenn der Geist eine persönliche
Verbindung zu den Helden hat.
4. **Mechanischer Zeitläufer:** Ein kleines, automatisches Wesen – halb Tier, halb Maschine. Zum
Beispiel eine metallische Spinne oder ein Uhrwerk-Vogel, geschaffen von einem Zukunfts-Tüftler, aber
durch einen Unfall in eine frühere Epoche versetzt. *Eigenschaften:* Äußerst flink, intelligent und
in der Lage, mit Maschinen zu interagieren. In der jeweiligen Epoche kann es massiven Einfluss
haben: Stellt euch etwa eine Steampunk-Stadt vor, in der plötzlich Maschinen verrückt spielen –
dahinter steckt dieser kleine Zeitläufer, der sie hackt und zu Streichen anstiftet. *Szenario:* Die
Chrononauten müssen das Wesen einfangen. Vielleicht finden sie Gefallen daran und behalten es als
“Maskottchen” (ein lebendes Artefakt!) – aber Vorsicht: Das Teil **lernt** aus jeder Interaktion. Je
länger es unbehelligt bleibt, desto trickreicher und eigenständiger wird es. Lässt man es zu lange
frei, entwickelt der vormals putzige Apparat einen eigenen Willen und kann zum ernstzunehmenden
Gefahrbringer werden, der am Ende womöglich ein ganzes Fabriksystem übernimmt.
5. **Dämon der Zeitschlucht:** In Legenden mancher Kulturen taucht ein schreckliches Wesen auf, das
“zwischen den Jahren” haust. Beschrieben als Mischung aus Drache und Kraken, gehüllt in schwarzen
Nebel, erscheint es dort, **wo zu oft an der Zeit manipuliert wurde**. *Reale Erklärung:* Ein
Auswuchs des gestörten Zeitkontinuums selbst – quasi die Zeitlinie, die rebelliert und als Monster
manifestiert. *Fähigkeiten:* Dieser Dämon spürt Zeitreisende auf, kann Portale verschlingen oder
instabil machen und verzerrt die Realität um sich herum (Halluzinationen, Zeitloops, physikalische
Anomalien). **Endgegner-Material:** Er eignet sich als ultimativer Antagonist einer Kampagne oder
als Herzstück einer Horror-Mission. *Schwäche:* Nur mit einem besonderen Artefakt oder der
Synchronisation mehrerer Zeitgeräte kann man ihn bannen – z. B. müssten an fünf Punkten gleichzeitig
Zeitanker gesetzt werden, um den Riss zu schließen und ihn zurück in die Zeitschlucht zu schicken.
Das ist eine epische Aufgabe, die echtes Teamwork und cleveres Vorgehen verlangt. Ihn im klassischen
Sinne zu “besiegen” (umzuhauen) ist kaum möglich – hier müssen Köpfchen und das **Mysterium der Zeit**
ran.
6. **Zeit-Egel:** Zunächst unsichtbar, heftet sich dieser **parasitische Zeitwesen** an
nichtsahnende Chrononauten und saugt unbemerkt deren temporale Energie ab. *Symptome:* Die
betroffenen Helden leiden unter plötzlichen Zeitsprüngen oder Zeitverlust – Sekunden verschwinden
oder wiederholen sich, Erinnerungen verblassen, manche altern oder verjüngen sich für Augenblicke
ruckartig. Außenstehenden mag es wie ein Fluch erscheinen. In Wahrheit verursacht der Zeit-Egel
diese Störungen und lässt erst los, wenn er sich sattgefressen hat *oder* wenn man ihn mit
speziellen Maßnahmen vertreibt. *Herausforderung:* Die Helden müssen erkennen, dass kein Fluch,
sondern ein **lebendes Wesen** die Ursache ist. Vielleicht entwickeln sie ein modifiziertes Chrono-
Gadget, um den Parasiten sichtbar zu machen und zu entfernen. Dann stellt sich die Frage:
**Vernichten** sie den Egel – oder fangen sie ihn ein, um ihn zu studieren (was natürlich Risiken
birgt)?

Diese Kreaturen (und viele mehr) könnt ihr einbauen, um euren Abenteuern Würze und Mysterium zu
verleihen. Wichtig ist, sie **sparsam und gezielt** einzusetzen – jede besondere Begegnung soll sich
einzigartig anfühlen. Die Spieler dürfen ruhig mal ins Grübeln kommen: “Was zum Henker ist *das*!?”
Und wenn sie dann nach und nach die Hintergrundgeschichte oder Logik dahinter entdecken, wird aus
einem Monster plötzlich ein integraler Teil der Story – vielleicht sogar etwas Mitfühlenswertes oder
Respektgebietendes. Gerade in ZEITRISS, wo Mythologie oft einen zeitphänomenalen Ursprung hat,
können solche Kreaturen dafür sorgen, dass selbst erfahrene Chrononauten nie vergessen: **Die Zeit
birgt unendliche Überraschungen.**

## Artefakt-Generator: Objekte mit Geschichte

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
  6. Kann einmalig die Zeit **lokal** beeinflussen (z. B. 5 Sekunden zurückdrehen)

- **Herkunft/Historie:**

  1. Stammt von einer berühmten historischen Persönlichkeit (z. B. Excalibur, Teslas Notizbuch)
  2. Wurde von Aliens in der Antike hinterlassen
  3. Ein Prototyp aus der Zukunft, der verloren ging
  4. Durch ein Paradoxon erschaffen (das Objekt dürfte *eigentlich* nicht existieren)
  5. Wird in einer Kultur religiös verehrt (als göttliches Relikt missverstanden)
  6. Wurde von einem Zeitreisenden absichtlich versteckt, um später gefunden zu werden

**Beispiel:** Kombination 3-6-4 (*Gerät* + *Zeitmanipulation* + *Paradoxon*) ergibt ein Gerät mit
einmaliger Zeitfunktion, das durch ein Paradoxon erschaffen wurde. GPT ersinnt vielleicht die
**“Stundenglas-Bombe”** – ein kleines mit Zahnrädern versehenes Gerät, das aussieht wie ein
viktorianisches Stundenglas. Seine Eigenschaft: Es kann einmalig **die Zeit um 10 Minuten
zurückspulen** (in einem begrenzten Umkreis). Dabei entsteht jedoch ein Paradoxon, weil das Gerät
sich selbst eigentlich nie gebaut haben kann – jedes Mal, wenn es benutzt wird, übergibt es sich
quasi selbst an die Nutzer in der Vergangenheit. Das Objekt dürfte also gar nicht existieren, doch
*da es existiert*, verursacht jeder Einsatz einen kleinen Riss im Zeitgefüge. Die Helden könnten es
als Notfallplan einsetzen, wissen aber: **Jeder Gebrauch destabilisiert den Zeitstrom** – ein wunder
Punkt und Dilemma!

*Ein anderes Beispiel:* Kombination 1-3-1 (*Waffe* + *lebendig* + *berühmte Person*) ergibt eine
lebendige Waffe, die einst einer berühmten Person gehörte. Heraus kommt vielleicht **“Alexander der
Große’s sprechendes Schwert”**, dem man eine eigene Persönlichkeit nachsagt – tatsächlich verbirgt
sich darin eine KI aus der Zukunft in Form eines Schwertes, die Alexander fand und für göttliche
Eingebung hielt. Das Schwert berät den Träger im Kampf (optional durch Visionen oder Telepathie) und
hat eigene Ziele – vielleicht *will* es, dass man es zu einem bestimmten Zeitpunkt in der Zukunft
trägt, um dort etwas zu bewirken.

Mit solchen Artefakten könnt ihr tolle Plots entwerfen. Gerade wenn Spieler freies Spiel genießen,
lieben sie es, **seltsame Gegenstände** zu sammeln und deren Zweck herauszufinden. Vielleicht
entfaltet ein Artefakt erst im Finale seine volle Macht – oder es bringt einfach Flair in den
Alltag, z. B. ein Stein, der bei Gefahr warm wird, oder ein Amulett, das alle paar Stunden ein
Flüstern aus der Zukunft von sich gibt. ZEITRISS bietet die Bühne, eure ganz eigenen “mysteriösen
Gegenstände” zu kreieren – nur dass die Magie hier oft Wissenschaft oder Paradoxie ist.

## Kulturfragmente-Generator: Farbe für die Epochen

Wer durch die Zeit reist, trifft auf fremde **Kulturen, Bräuche und Alltagsdetails**, die eine
Epoche erst *authentisch* machen. Dieser Generator hilft dabei, schnell ein **Kulturfragment**
einzustreuen, das der Szene mehr Tiefe gibt – ideal, wenn Spieler fragen: *“Gibt es hier gerade ein
Fest oder so?”* oder wenn ihr einfach Atmosphäre schaffen wollt.

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

**Beispiel:** In einer Renaissance-Stadt (Florenz 1500) würfle ich auf *Sitten & Aberglaube* und
erhalte eine 2: Bestimmte Worte werden nie ausgesprochen. GPT interpretiert dies so: *In Florenz
wagt niemand, direkt vom “Teufel” zu sprechen – man umschreibt ihn als “den mit den Hörnern”.* Der
Grund: Man glaubt, Worte beschwören Realität. Die Chrononauten merken das deutlich, als ein NSC
zusammenzuckt, weil einer von ihnen unbekümmert **“diavolo”** gesagt hat. – Schon bekommt ein
einfaches Gespräch sofort eine interessante kulturelle Note!

Solche Kulturfragmente lassen die Welt lebendig und eigen wirken. Die Helden merken: **Jede Epoche
hat ihre Eigenheiten**, und wenn sie sich klug darauf einlassen (bzw. GPT sie daran erinnert),
können sie so manch unnötigen Konflikt vermeiden oder Sympathien gewinnen. Vielleicht machen sie bei
einem lokalen Fest mit und gewinnen dadurch Verbündete – oder sie nutzen einen Aberglauben gezielt

für sich (*“Wir verkleiden uns als die Ahnengeister, damit sie uns zuhören!”*). Diese kleinen Dinge
fördern das Eintauchen ins Setting enorm und sorgen für großartige Immersion.

## Temporale Anomalien-Generator (optional)
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

## Historische Hotspots

Diese Tabelle liefert markante Schauplätze der Menschheitsgeschichte, aus denen
die KI missionsreife Einsätze ableiten kann. Jeder Eintrag eignet sich als
Startpunkt für Zeitinterventionen, Spionage oder Sabotage.

1. **Paris 1889 – Weltausstellung:** Eiffelturm im Bau, technische
   Wunderwerke locken Agenten und Spione an.
2. **Chicago 1893 – Columbian Exposition:** Konkurrenz um Patente und
   spektakuläre Demonstrationen.
3. **Berlin 1936 – Olympische Spiele:** Politische Spannungen, Propaganda und
   verdeckte Aufrüstung.
4. **London 1851 – Great Exhibition:** Viktorianische Innovationen, erste
   globale Handelsnetze.
5. **New York 1939 – World’s Fair:** Vision einer optimistischen Zukunft,
   passende Tarnung für geheime Projekte.
6. **Osaka 1970 – Expo ’70:** Kalter Krieg trifft Popkultur und futuristische
   Architektur.

Die KI kann diese Hotspots nutzen, um automatisch Missionen zu generieren. Sie
wählt einen Ort, definiert dortige Konflikte und verknüpft sie mit den
Zielen der Fraktionen. Die folgenden Einträge sind nur Beispiele – GPT kann
jederzeit neue Schauplätze und Aufträge kombinieren, damit jede Runde
einzigartige Missionen erlebt.

## Zukunfts- und Sci-Fi-Hotspots

Auch Gerüchte und Internet-Mythen bieten reichlich Stoff für spannende Missionen.
Die folgende Liste greift populäre Spekulationen auf, die sich besonders für
gruselige oder abgedrehte Einsätze eignen:

1. **Mars – Gesicht von Cydonia:** Der vermeintliche Felshügel soll der Eingang
   zu einer gewaltigen unterirdischen Basis sein, angeblich von frühen
   Menschen erbaut.
2. **Phobos – Der Basilisk:** Auf dem Marsmond ragt eine bizarre Formation, die
   wie ein riesiger Basilisk wirkt. Manche glauben an einen alienartigen Turm,
   größer als der Turm zu Babel.
3. **Rückseite des Mondes – Die wahre Madonna:** In einem abgestürzten
   Raumschiff ruht ein Wesen, halb Mensch, halb Alien. Manche halten es für den
   Ursprung der Menschheit – eine wahre Madonna.
4. **Saturnmond Titan – Fremdes Leben:** In den Methanmeeren weisen Spuren
   komplexer Organismen auf eine verschollene Kolonie hin.
5. **Antarktis – Versiegelte Anlagen:** Tief unter dem Eis verbergen sich
   angeblich Reste einer Hochtechnologie-Zivilisation – vielleicht von
   Zeitreisenden oder Atlantiern.
6. **Kapustin Jar – Aktives Zeitportal:** Gerüchte berichten von Experimenten,
   die dort Zugänge in Vergangenheit und Zukunft öffnen.

Die KI kann diese Hotspots nutzen, um spektakuläre Sci-Fi-Plots zu entwerfen
oder sie mit realen Schauplätzen zu verknüpfen.

## Ausgefallene Szenarien

1. **Militärischer Komplex – Tollwutvirus-Zombies:** In einer geheimen Anlage
   wird ein modifiziertes Tollwutvirus getestet. Ein Ausbruch verwandelt das
   Personal in rasende Kreaturen. Die Chrononauten sollen die Ursache finden und
   das Virus eindämmen.
2. **Mittelalterliche Katakomben – Der falsche Teufel:** In einem abgelegenen
   Dorf verschwinden Menschen. Unter dem Dorf liegt ein weit verzweigtes
   Katakombensystem, das angeblich vom Teufel bewohnt wird. Tatsächlich erzeugen
   dort versteckte Alien-Geräte furchteinflößende Illusionen, während gezüchtete
   Mutanten ein uraltes Geheimnis bewachen.
3. **Altes Schloss – Vampir-Experiment:** Nächtliche Übergriffe plagen ein Dorf. Ein Konzern schuf hier einst
   eine neue Menschenart, die Blut saugt und sich per Biss verbreitet. Die Chrononauten müssen im Schloss
   den fanatischen Bluttrinkerzirkel aufspüren und das fehlgeschlagene Experiment beenden.

4. **Geheime Tiefsee-Megacity – Ursprung des "Blob":** Die Agenten springen zu dem
   Zeitpunkt, als das lauteste je registrierte Geräusch aus den Tiefen des Ozeans
   aufgezeichnet wird. Die Spur führt zu einem verborgenen Terraforming-Projekt
   namens Second Earth, das von Schattenorganisationen betrieben wird. Dort
   entdecken sie eine fortgeschrittene Megacity, halb unter einer Kuppel, halb im
   Meeresboden. Schwarzer Sauerstoff dient als Atemgas, während Schwarze Raucher
   Energie liefern. Die Atmosphäre ist für Menschen der Oberwelt tödlich.
