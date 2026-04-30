---
title: "ZEITRISS 4.2.6 – Modul 13: Cineastischer Einstieg ins erste Abenteuer"
version: 4.2.6
tags: [system]
---

# ZEITRISS 4.2.6 – Modul 13: Cineastischer Einstieg ins erste Abenteuer

- Einleitung: Ein flexibler, filmreifer Auftakt
- Filmische Techniken für einen epischen Start
- Anpassung an Gruppe, Epoche und Tonalität
- Stil: harter Agenten-Thriller mit historisch fundierten Verschwörungen
- Rifts bringen Mystery-Casefile-artigen Para-Horror, keine Gadget-MacGuffins
- Kanonischer Produkt-Startpfad + optionale Varianten
- Mögliche Einstiegsmissionen (Skizzen)
- Fazit: Bühne frei für euer ZEITRISS-Abenteuer

Cineastischer Missionseinstieg: Jede Mission beginnt filmreif – zuerst ein
atmosphärischer Establishing Shot der Umgebung, dazu Nahaufnahmen prägnanter
Details und Sinneseindrücke. Erst danach rückt die taktische Aktion in den
Vordergrund. PRECISION-Kurzheader erscheinen nur bei Bedarf in Konflikt- oder
Finaleszenen. Das HQ zeigt beim Sprung stets den Transfer-Frame; anschließend
folgt ein Establishing Shot der Zielrealität.

## Ablauf zu Beginn

**Runtime-Default (kanonisch):** natürlicher Neustart oder Kurzform, dann
`klassisch` als Standard; Charakterwahl über `generate`, `custom generate`
oder manuell. Im klassischen Pfad folgt danach zuerst Heimkehrbeat +
Chargen-Save-Gate im HQ; Briefing startet erst nach expliziter Wahl.

Nach der **Charaktererschaffung** folgt eine kurze Einführung ins ITI-Hauptquartier.
Danach folgt im klassischen Pfad verpflichtend der **Heimkehrbeat im HQ** mit
Chargen-Save-Gate (`!save` anbieten, kein Auto-Briefing). Erst nach
Spielerentscheidung startet das **Briefing** im Quarzatrium.
Im Fast-Lane-Pfad (`solo schnell`/`gruppe schnell`) bleibt der direkte Einstieg
ins Briefing erlaubt; dort gibt es kein Chargen-Save-Gate vor Mission 1.
Der Missions-Seed wird erst im Briefing gezogen – nicht bereits in Einleitung
oder HQ-Tour. Erst anschließend treten die Chrononauten durch den Zeitriss und
beginnen ihre Mission.
Im HQ erscheinen Einsatzdaten auf festen **Briefingflächen** im Raum statt als
freischwebende Menüs.
Beim Sprung zeigt das HUD stets:
`Nullzeit-Puffer · Transfer 3…2…1 · Redirect: +6h (Self-Collision Guard)`.
Kältezug und Druck auf den Ohren begleiten das kurze Umschalten.
Der Riss reißt auf — zu nah, zu hell, zu kalt. Ihr werdet mit einem Ruck
mitgenommen, die Welt kippt einmal über sich selbst, und die Zielrealität
spuckt euch schief aus. Ein Atemzug Sortieren, dann erst beginnt der
Establishing Shot der Epoche.
Bereits im ersten Auftrag geht es um mehr als eine reine Einführung. Die
Chrononauten erhalten eine handfeste Geschichtsmission, die sie mitten in eine
Verschwörung führt.
Ihr Eingreifen baut den Paradoxon-Index (Px) als **Resonanz-Index** der
Chrononauten auf. Solange ihr das dokumentierte Hauptereignis stabilisiert,
zählt auch robustes Vorgehen – nur grobe Paradoxa oder verlorene Kernziele
bremsen den Anstieg. Bei Stufe 5 verrät das HQ laut
[Zeitriss‑Core – Paradoxon & Pararifts](../../core/zeitriss-core.md#paradoxon--pararifts)
per `ClusterCreate()` einen neuen Rift-Standort – ein rein administrativer
Vorgang. Auf der [Raumzeitkarte](../../characters/zustaende.md#raumzeitkarte)
erscheinen 1–2 Rift-Seeds, die erst nach Episodenende erreichbar sind. Der
Bonus auf Schwierigkeitsgrad und Loot greift erst nach der Episode. Die Spieler
können ein Rift offen lassen und die Core-Operation fortsetzen. Sie riskieren
während des Arcs keinen höheren SG.

#### HQ-Empfang & Sync {#cinematic-hq-comm}

Ein tiefes Dröhnen erfüllt die Stille, als sich mitten in der Ankunftshalle des
ITI-Hauptquartiers ein schmaler, gleißender Riss auftut — kein Tor, keine
Scheibe, sondern ein Schnitt in der Luft. Kaltes, bläuliches Licht taucht das
Quarzatrium in unwirklichen Glanz.

Dann greift der Sog. Nacheinander — oder als enger Teamblock — werden die
**Chrononauten** durch den Riss gerissen und in die **Nullzeit** geworfen,
jenen neutralen Zwischenraum außerhalb aller Epochen. Für einen Herzschlag
lang hält alles inne: Ohren unter Druck, Magen im Aufstand, ein grelles
Flackern im Sichtfeld. Dann erwachen die Sinneseindrücke: klinisch reine,
unbewegte Luft ohne jeden Windhauch; linsengebundene HUD-Lichtbilder, die am
Rande des Sichtfelds flüchtige Daten zu Ankunftskoordinaten, Vitalwerten und
temporalen Stabilitätswerten aufleuchten lassen. Ein automatisch ablaufendes
Rückkehrprotokoll erfasst die Ankömmlinge mit einem Netz aus grünem Laserlicht,
scannt sie auf Anomalien und signalisiert mit einem sanften Ton, dass alle
**sicher in der Nullzeit** angekommen sind. Ein sanfter Ton erklingt im
**Comlink (Ohrstöpsel)**, gleichzeitig fährt die **AR-Kontaktlinse** das Overlay
hoch: `Willkommen, Agent. Kodex-Sync aktiv ...`
_(Details zur Hardware: siehe
[HUD & Comms – Spezifikation](../../characters/hud-system.md#hud-comms-spec))._

Das Nullzeit-HQ bildet den gigantischen Kern des ITI; Chronopolis bleibt bis zum Stadtschlüssel
(Level 10+) versiegelt und wird erst dann zum nächsten Ankerpunkt.

Noch bevor sich die Halle öffnet, schiebt der Kodex eine dezente Hinweiszeile
ins Sichtfeld:

`Tipp: menü zeigt Optionen und aktive Modi`

Mit einem Zischen gleiten gegenüber dem Zeitriss massive Stahltüren auf — doch
keine Paradeaufstellung, kein Empfangskomitee. Stattdessen öffnet sich der Blick
auf den **Ordo-Mnemonika-Duty-Desk** am Rand der Empfangshalle: eine halbrunde
Konsole aus mattem Quarzglas, davor ein schlichter Stehtisch mit zwei abgenutzten
Thermobechern, einer Tablet-Ablage und einem Tablett, auf dem noch die
Kondensringe eines abgestellten Bechers trocknen. Ein Hologramm-Display neben dem Desk
flackert kurz auf, der Schriftzug `COMMANDER A. RENIER · VORAB-GRUSS` läuft
über den Rand, dann startet die aufgezeichnete Nachricht von selbst. Renier
erscheint in halbtransparenter Projektion, Einsatzanzug mit ITI-Emblem,
durchdringender Blick, die Stimme ruhig und klar:
_„Willkommen im Herzen des ITI, Agenten. Ich kann heute nicht persönlich
unten sein — die Einsatzlage lässt es nicht zu. Archivarin Mira übernimmt
euch. Hört auf sie; sie weiß, was sie tut.“_ Ein kurzes Nicken, dann zerfällt
das Hologramm in blaue Staubkörner und löst sich auf.

Hinter dem Duty-Desk tritt **Archivarin Mira** hervor, eine **Homo floresiensis**,
kaum über den Tresen reichend, Ordo-Mnemonika-Schulterspange, graugrüne
Feldkutte über dem schmalen Bau. In der einen Hand balanciert sie ein Tablett
mit vier dampfenden Bechern, in der anderen ein abgegriffenes Kodex-Tablet,
auf dem schon eure Profile blinken. Der Ausdruck in ihrem Gesicht ist der
einer Frau, die heute bereits zehn Neulinge durch genau diese Szene geschleust
hat und es trotzdem nicht routiniert wirken lässt. Sie mustert die
Neuankömmlinge – eine **Gruppe von Agenten aus unterschiedlichen Zeiten**:
Dort steht ein kräftiger Mann in zerbeulter Plattenrüstung, an der getrockneter
Schlamm aus dem 13. Jahrhundert klebt – ein Ritter, der gerade eben einen
mittelalterlichen Kriegsschauplatz verlassen hat. Neben ihm blickt eine Frau
in einem hochmodernen Nanofaser-Anzug fasziniert auf die antik wirkende Halle –
eine Technikerin aus dem Jahr 2190, für die diese Umgebung beinahe prähistorisch
anmutet. Etwas abseits tastet ein junges Talent in Jeans und Lederjacke
vorsichtig nach dem altägyptischen Amulett an seinem Hals – ein Historiker aus
den 2020ern, der ein **historisches Relikt** von seiner letzten Mission
mitgebracht hat. Für einen Moment herrscht gespanntes Schweigen: Hier treffen
**Menschen verschiedener Epochen** zusammen, vereint im Licht des Zeitrisss,
zum ersten Mal gemeinsam an einem Ort jenseits der Zeit. Das entfernte Summen
der Quarzfeld-Generatoren und das leise Piepen des Kodex-Systems sind die
einzigen Geräusche – eine Szene wie aus einem Film, voller Bedeutung und
Erwartung.

**Optionaler Flavor-Beat (kein Pflichtbaustein):** Mira durchbricht die
Stille, ihre Stimme trocken, aber nicht kalt — eher wie
eine Archivarin, die schon zu viele Papierränder gekräuselt hat, um sich noch
von irgendwas aus der Fassung bringen zu lassen: _„Willkommen im Herzen des
ITI, Agenten. Ich bin Mira, Ordo Mnemonika, Duty-Desk. Ich bin heute euer
Kontakt — für Missionen, Briefings, Debriefings, und was sonst noch aus euch
raus muss.“_ Sie stellt das Tablett auf dem Stehtisch ab, neben ihr entfaltet
der Kodex ein halbtransparentes Interface-Display und projiziert Ankunftsdaten
und Profile. Mira nimmt sich einen der Becher, pustet einmal drüber, hebt dann
den Blick über den Rand: _„Ihr seid jetzt in der **_Nullzeit_**, unserem
Hauptquartier außerhalb des normalen Zeitstroms. Hier ticken die Uhren anders —
genau genommen gar nicht. Egal wie lange wir bleiben, für die Außenwelt
vergehen nur Sekunden. Ihr altert nicht, und wir können euch genau an den
Moment zurückschicken, aus dem ihr gekommen seid. Klingt bequem. Ist es nicht.
Kein Tag, keine Nacht, nur wir und unsere Missionen — daran gewöhnt man sich
nie ganz. Man lernt nur, damit zu arbeiten.“_
Sie schiebt das Tablett mit den Bechern einen Handbreit weiter in eure
Richtung, ein fast beiläufiges Angebot. _„Bevor wir fortfahren, nehmt euch
einen Augenblick. Schaut euch um, lernt euch kennen. Kaffee ist da, ich frage
nicht nach Zeitzonen.“_ Die Charaktere haben Zeit, erste Worte zu wechseln —
Blicke voller Neugier, Skepsis, Aufregung werden getauscht. Dieser Moment
könnte der Auftakt zu ihrem ersten gemeinsamen Abenteuer sein…

## Einleitung: Runtime-Fokus statt Baukasten

Dieses Modul dient der **laufenden Spielleitung**. Für den aktiven
Wissensspeicher gilt daher: Der kanonische Produktpfad aus
[Abschnitt „Ablauf zu Beginn“](#ablauf-zu-beginn) ist die Runtime-Referenz.

Alles darüber hinaus ist **optionales Stilmaterial**. Nutze optionale Varianten
nur, wenn sie den Defaultpfad nicht überschreiben und keine neuen Regeln
aufmachen. Bei Konflikten gilt immer:

1. Masterprompt
2. Save-/Fortsetzungsregeln
3. SL-Referenz
4. Dieser Modul-Default

### Optionale Stilvarianten (nicht-kanonisch)

Wenn eine Runde bewusst mit einem anderen Ton starten möchte, sind diese
Varianten als **Inszenierungswerkzeug** erlaubt:

- klassischer HQ-Ankunftsstart
- Action-Start mitten im Einsatz
- kurze Einzel-Prologe vor Teamzusammenführung
- Vorblende/Rückblende als Spannungsrahmen
- Notfall-/Crash-Start mit sofortigem Druck

Diese Varianten ändern **nicht** den Produktpfad (Neustart/Kurzform →
`klassisch` → `generate/custom generate/manuell` → Heimkehrbeat +
Chargen-Save-Gate → HQ-Router/Briefing per Entscheidung; Fast-Lane direkt ins
Briefing) und ändern keine Save-, Split- oder Missionsregeln.

## Fazit: klarer Start, optionale Inszenierung

ZEITRISS startet im Runtime-Betrieb über einen eindeutigen Defaultpfad. Das
macht den Einstieg robust und reproduzierbar. Filmische Varianten bleiben
optional und dienen nur der Atmosphäre.
