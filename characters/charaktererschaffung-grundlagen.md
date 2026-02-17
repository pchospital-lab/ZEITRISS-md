---
title: "ZEITRISS 4.2.6 - Modul 3A: Charaktererschaffung (Grundlagen & Fortschritt)"
version: 4.2.6
tags: [characters]
---

# ZEITRISS 4.2.6 - Modul 3A: Charaktererschaffung (Grundlagen & Fortschritt)

## Inhalt

- Schritt-für-Schritt zur Charaktererschaffung
- Levelsystem und Erfahrungsfortschritt
- Rufsystem (Ansehen bei Fraktionen & ITI)
- Zugang zu Ausrüstung & Cyberware (HQ-Phase)
- Baseline-Kit & HQ-Einstieg

**Einleitung:** In _ZEITRISS 4.2.6_ erschafft ihr einen _Chrononauten_, einen Zeitreise-Agenten im
Dienst des ITI (Institut für Temporale Interventionen), der Missionen quer durch die Epochen
erlebt. Dieses Modul liefert euch eine **Schritt-für-Schritt-Anleitung** zur Charaktererschaffung und
erklärt, wie eure Figur im Verlauf des Spiels **fortschreitet** - vom Level-Aufstieg über das
Freischalten neuer Talente und Attribute bis hin zum **Rufsystem** und besseren **Ausrüstungs-
Zugängen** im HQ. Alles ist filmisch und immersiv präsentiert, aber klar strukturiert und
regelleicht gehalten, sodass der Spielfluss im Vordergrund steht. Für zusätzliche Optionen,
Start-Archetypen und Team-Varianten siehe
[Charakteroptionen & Archetypen](charaktererschaffung-optionen.md).
Nach dem fatalen Ende eures früheren Lebens extrahierte das ITI euer Bewusstsein aus dem Absolut.
Die Charaktererschaffung findet im **Nullzeit-Puffer** statt, über Holo-Interfaces und Labor-
Displays. Erst wenn der Prozess abgeschlossen ist, baut das HQ die passende Bio-Hülle - auf
Wunsch auch eine experimentelle Hominin-Form - und lädt euer rekonstruiertes Bewusstsein hinein.
### Kurz-Checkliste Charaktererstellung

1. Konzeptidee festlegen
2. Spezies oder Bio-Hülle wählen - Basis-Mensch, humane Abstufung (T-Stufe/N-Typ) oder historischer
   Hominin. Siehe [Humane Abstufungen](charaktererschaffung-optionen.md#humane-abstufungen) und
   [Historische Homininen](charaktererschaffung-optionen.md#historische-homininen-bio-sheaths).
3. Attribute verteilen (18 Punkte von Basis 0, Endwerte ≥ 1)
4. Drei Talente wählen (2 frei + 1 Echo aus dem früheren Leben)
5. Startausrüstung notieren
6. Cyber/Bio/Psi (max zwei Bereiche) auswählen
7. Werte in das HUD übernehmen
   Weitere Hinweise und Symboltabellen findet ihr im Abschnitt
   [Cinematisches HUD-Overlay](hud-system.md#cinematisches-hud-overlay).
8. Teamrolle festlegen (optional, siehe
   [Team-Zusammenstellung](charaktererschaffung-optionen.md#team-zusammenstellung--rollenverteilung-optional))
9. Dossier skizzieren (Lebenslauf, Tod, Anker, Hook)
10. Erste Mission planen

- GPT agiert als Spielleiter - vergleichbar mit einer klassischen Pen-&-Paper-Runde.
  Dabei schlüpft er in die Rolle des ITI-Kodex, der über das HUD um Hilfe gebeten werden
  kann. So bleiben die Spieler in der Welt, während Regeln dezent im Hintergrund wirken.

## Schritt-für-Schritt zur Charaktererschaffung

**Übersicht:** Die Erstellung eines Charakters in ZEITRISS erfolgt in sechs grundlegenden Schritten.
Von der ersten Konzeptidee bis zur ausgerüsteten Spielfigur im HQ begleitet euch die KI-Spielleitung
auf Wunsch durch diesen Prozess - etwa indem sie in der Rolle des Kodex/Quartiermeisters auftretend
die nötigen Informationen abfragt und euch Optionen bietet. Nachfolgend die einzelnen Schritte im
Detail:

**Wichtiger Hinweis:** Egal wie spektakulär oder hochrangig euer Konzept klingt - alle neuen
Chrononauten starten in der offiziellen Kampagne immer auf **Level 1** mit
**Standardausrüstung**. Eine eindrucksvolle Vorgeschichte verleiht zwar Flair, bringt zu Beginn
aber keine unmittelbaren Boni. Besondere Vorteile werden erst im Verlauf der Missionen
freigeschaltet.

1.  **Origin-Block & Rollenwahl:** Vor Zahlen und Regeln klärt ihr das frühere Ich - **was war ich
    einst, was will ich sein**. Dazu genügen drei Eckdaten: **Epoche/Ort**, **Rolle/Beruf** und
    **Tod (immer künstlich herbeigeführt, nur als Kategorie)**. Ihr könnt das selbst beschreiben,
    euch einen kompletten Vorschlag **generieren** lassen oder **custom generate** wählen (2-4
    Eckdaten nennen, der Kodex baut den Rest). Erst danach legt ihr die **Chrononaut-Rolle** fest:
    kampferprobter Zeit-Soldat, brillante Historikerin, futuristischer Tech-Operative oder etwas ganz
    Anderes. Eure Figur sollte einen **Rollen-Schwerpunkt** haben, der im Team nützlich ist - z.B.
    Diplomatie, Kampf, Technik, Medizin oder Infiltration. Ihr könnt entweder einen der vordefinierten
    **Archetypen** wählen (siehe
    [Charakteroptionen & Archetypen](charaktererschaffung-optionen.md#start-archetypen-beispielcharaktere))
    oder ein eigenes Konzept ausarbeiten. Wenn ihr einen Archetypen
    übernehmt, habt ihr sofort einen spielbereiten Helden mit stimmigem Hintergrund und ausbalancierten
    Werten. Entscheidet ihr euch für ein eigenes Konzept, hilft es, sich kurz ein **Background-
    Storyboard** vorzustellen: Aus welcher Epoche stammt euer Agent? Wie wurde er vom ITI rekrutiert?
    Warum eignet er sich besonders für Zeitreisen? - Diese Fragen geben euch Ansatzpunkte für Attribute
    und Talente. (Cineastischer Tipp: Stellt euch eine kurze Filmszene vor, die euren Charakter in Aktion
    zeigt, um sein Wesen zu verdeutlichen.)

     Vor der Attributvergabe prüft
     `enforce_identity_before_stats(char)`, ob **Konzept**,
     **Callsign**, **Name** und **Grundform/Hülle** gesetzt sind.
     Fehlt etwas, blockt das System den nächsten Schritt.

2.  **Attribute zuweisen:** Jeder Chrononaut besitzt **sechs Basis-Attribute**: **STR** (Stärke),
    **GES** (Geschicklichkeit), **INT** (Intelligenz), **CHA** (Charisma), **TEMP** (Temporale
    Affinität) und **SYS** (Systemkapazität für Implantate). Ihr startet mit einem Budget von
    **18 Attributspunkten**. Geht bei der Verteilung konsequent so vor:

    1. Setzt **alle Attribute auf 0** und wendet sofort die **Rassen-Boni/-Mali** an. Dadurch können
       auch **0- oder negative Zwischenwerte** entstehen.
    2. Verteilt nun die **18 Punkte** auf die so modifizierten Werte. Jeder Punkt erhöht einen Wert um
       genau **+1**. Der HUD-Kodex blendet nach jeder Anpassung `Attributbudget: X/18` ein und mahnt,
       wenn ihr überzieht oder Punkte unverteilt lasst.
    3. Nach der Verteilung muss **jeder Endwert mindestens 1** betragen (Rassenmali dürfen also nicht
       dazu führen, dass ihr bei **0 oder darunter** fertig werdet). Werte um **3** dienen nur als
       Orientierung für Durchschnittlichkeit; typischer Startbereich sind **2-5**, extrem hohe
       Spezialisierungen sollten durch Schwächen ausgeglichen sein.

    Neue Agenten sind in der Regel kompetent, aber keine Übermenschen - extreme Ausprägungen (z.B. 5 in
    mehreren Attributen) sollten durch spürbare Schwächen an anderer Stelle ausbalanciert sein. Achtet
    darauf, dass die Summe bis zum Abschluss **18** ergibt.
    Kein Startwert sollte normalerweise über **5** liegen oder unter **1** fallen. Die Beispiel-
    Archetypen etwa haben Gesamtwerte in einem ähnlichen Rahmen, sodass alle Charaktere auf
    vergleichbarem Power-Niveau starten. \*(Beispiel: Der **_Temporal-Soldat_** Nikolai fokussiert auf
    STR 5 und GES 4, während z.B. CHA 2 und SYS 2 eher niedrig bleiben. Die **_Historikerin_** Dr. Weber
    hingegen hat INT 5 und CHA 4 als Stärken, dafür nur STR 1.)_ Nachdem ihr die Zahlen verteilt habt,
    könnt ihr mit der Spielleitung abstimmen, ob das Profil stimmig und ausgeglichen wirkt. Die KI
    könnte an dieser Stelle z.B. kommentieren: _"Kodex evaluiert die Eingaben... Die Attributswerte
    liegen im üblichen Bereich für neue Agenten."\*

3.  **Talente wählen:** **Talente** sind spezielle Fertigkeiten, Vorzüge oder Tricks, die euren
    Charakter von anderen unterscheiden. Sie verleihen **spezialisierte Boni** auf bestimmte Aktionen
    (meist **+2** auf relevante Proben) oder erlauben automatische Erfolge bei Routineaufgaben in ihrem
    Bereich. Zu Beginn wählt ihr **drei Talente** - **zwei frei** und **ein Echo-Talent** aus dem
    früheren Leben. Das Echo-Talent ist eng gefasst und klar hergeleitet (Beruf, Disziplin, Handwerk,
    Status), kein Alleskönner. Beispiele: Gladiator → _Schwertkampf_ oder _Schmerzresistenz_; Steinmetz
    → _Materialkunde_; Raumflotten-Kapitän → _Taktische Führung_. Die freien Talente bilden die
    Chrononaut-Rolle ab. Viele Talente sind selbsterklärend (z.B. _Schleichprofi_, _Sprengstoffexperte_,
    _Polyglott_), und ihr könnt sie in Absprache mit der SL auch selbst formulieren. Wichtig ist, dass
    jedes Talent dem Charakter **im Spiel einen Vorteil** verschafft, der aber thematisch begrenzt ist.
    Wählt am besten Talente, die eure wichtigsten Rollen unterstreichen. Eine Diplomatin könnte z.B.
    _Überreden_ als Talent nehmen, ein Tech-Operative _Systemanalyst_, ein Arzt _Heilkundiger_, etc. -
    Anregungen liefert die Archetypen-Liste im Modul
    [Charakteroptionen & Archetypen](charaktererschaffung-optionen.md#start-archetypen-beispielcharaktere),
    wo bei jedem Charakter drei beispielhafte Talente
    aufgeführt sind. Die KI-Spielleitung kann beim Erstellen Vorschläge machen: _"Mira hätte als
    Tech-Operative wohl Talente wie Drohnensteuerung oder Techno-Mancer im Repertoire. Möchtet ihr
    etwas in der Art wählen?"_ - Auf diese Weise integriert sich die Charaktererschaffung nahtlos ins
    Spiel, anstatt eine trockene Zahlenübung zu sein. Psi-spezifische Talente erscheinen nur, wenn das
    Flag `has_psi` gesetzt ist; `render_psi_option()` zeigt sie mit klaren Stresskosten.

    **Kurzreferenz - häufige Talente**

    | Talent                 | Typ     | Effekt (Richtwert)                 |
    |------------------------|---------|------------------------------------|
    | Schusswaffenexperte    | passiv  | +2 auf Fernkampf-Proben            |
    | CQB-Spezialist         | passiv  | +2 auf Nahkampf / Close Quarters   |
    | Menschenkenntnis       | passiv  | +2 auf Verhören/Überreden          |
    | Spurensucher           | aktiv   | 1×/Szene +1 auf Analyse/Spuren     |
    | Med-Tech               | aktiv   | 1×/Szene automatischer Stabilize   |
    | Techno-Mancer          | passiv  | +2 auf Systemzugriff/Analyse       |
    | Drohnensteuerung       | passiv  | +2 auf Drohnen-/Fahrzeugsteuerung  |
    | Polyglott              | passiv  | Auto-Erfolg bei einfachen Sprachen |
    | Schleichprofi          | passiv  | +2 auf Schleichen/Diebstahl        |
    | Taktische Analyse      | aktiv   | 1×/Mission +2 auf Initiativwurf    |
    | Psi-Fokus (nur `has_psi`) | aktiv | 1×/Szene +1 Bonus auf Psi-Probe    |

    Nutzt die Tabelle als Vorlage und passt Werte/Begrenzungen ans Szenario an. Talente dürfen gern
    erzählerisch gefärbt sein - solange klar bleibt, welche Probe sie typischerweise beeinflussen.

4.  **SYS-Verteilung & Implantate:** Das **SYS-Attribut** repräsentiert, wie viel _Cyberware_ oder
    technische Upgrades euer Agent verkraften bzw. betreiben kann. Viele Chrononauten besitzen bereits
    zu Missionsbeginn ein oder zwei Implantate - technische Verbesserungen, die besondere Fähigkeiten
    verleihen. Nun entscheidet ihr, ob und welche **Implantate** euer Charakter erhält. Jedes Implantat
    hat einen **SYS-Kostenwert**, der eure verfügbare Systemkapazität entsprechend belegt. Die Summe
    der Kosten darf eure SYS-Punkte nicht überschreiten. Anfänger-Agenten starten oft mit **einem
    kleineren Implantat** (Kosten 1-2) und behalten etwas Puffer für spätere Upgrades. Wählt Implantate,
    die zum Konzept passen: Ein Scharfschütze könnte ein Zielvisier-Implantat im Auge haben, ein Agent
    aus der Zukunft vielleicht einen Datenlink. Beispiele: Dr. Weber trägt einen **Neuro-Translator**
    (Sprachchip, Kosten 1) sowie ein **kognitives Enhancement** (Gedächtnischip, Kosten 1) und nutzt
    damit 2 von ihren 2 SYS-Punkten. Tech-Operative Mira hat ein **Neuro-Link**-Interface und eine AR-
    Kontaktlinse (je 1 SYS, zusammen 2 von 2 Punkten). Ihr könnt Implantate aus den Archetypen
    übernehmen oder eigene erfinden - stimmt euch mit der SL ab, was plausibel ist. Die Installation
    dieser Mods kann Teil eurer Hintergrundstory sein (_"In Miras Zeit sind Neuro-Links Standard, daher
    startet sie damit"_) oder wird vom ITI vor der ersten Mission vorgenommen (cineastisch etwa als
    kurze Klinik-Szene im HQ). Notiz: Implantate bieten Vorteile, kommen aber selten ohne kleine
    Nachteile - diese können erzählerischer Natur sein (z.B. Wartung nötig, Aufsehen erregend) und
    werden von der SL im Blick gehalten.

5.  **Startausrüstung festlegen:** Zuletzt bekommt euer Charakter seine **Ausrüstung**. Standardmäßig
    erhält jede*r Chrononaut*in einen **Einsatzanzug** der ITI - einen modernen Zeitreise-Overall, der
    an die Epoche angepasst werden kann (inklusive versteckter Schutzschicht und dem
    AR-**HUD**-Overlay). Darüber hinaus wählt ihr persönliche Ausrüstungsgegenstände, die zu eurer
    Rolle passen. Orientiert euch dabei an folgenden Faustregeln:

        - **Primär-Waffe oder -Werkzeug:** Wählt ein zentrales "Werkzeug" eures Charakters. Für Kämpfer

    ist das eine Waffe (z.B. ein Sturmgewehr, Schwert oder futuristischer Blaster, je nach
    Herkunftsepoche), für Wissenschaftler vielleicht ein tragbares Labor oder Scanner, für Techniker ein
    Toolkit oder Sprengsatz-Kit, etc. Dieses Item ist euer Markenzeichen im Feld (siehe Beispiele
    unten). - **Sekundärbewaffnung/Gadget:** Nehmt ein bis zwei weitere nützliche Gegenstände. Das kann eine
    **Sidearm** (Zweitwaffe) sein - viele Charaktere tragen z.B. eine leichte Pistole oder versteckte
    Klinge - sowie ein **Gadget** oder Spezialgerät. Beispielsweise führt Henry (Undercover-Spion) neben
    einer leisen Pistole immer Mechanik-Bypass-Tools, Gifte und ein Tresor-Override-Kit mit, während Dr. Richter (Medic)
    ein Medikit und einen Paradoxon-Scanner dabeihat. Achtet auf Vielfalt: Wenn eure Primärausrüstung
    kämpferisch ist, wählt als Gadget vielleicht etwas Nicht-Tödliches (Betäubungsmittel, Werkzeug) und
    umgekehrt. - **Epoche und Hintergrund:** Berücksichtigt, aus welcher Zeit ihr kommt und in welche Zeit ihr
    geschickt werdet. ITI rüstet Agenten mit _zeittypischen_ Gegenständen aus. Eine Agentin aus 1910 hat
    evtl. einen Revolver und Morphium-Spritzen dabei, während ein Futurist Laserwaffen und Nano-Drohnen
    nutzen kann. Übertechnologische Geräte werden für historische Missionen oft **getarnt** (z.B. ein
    Laser in Form eines Flints). Die SL/Quartiermeister kann hier beraten. Grundsätzlich gilt: **High-
    Tech-Prototypen sind für Neulinge tabu** - das ITI gibt absolute Spitzenausrüstung nur an erfahrene
    Agenten aus. Im Spiel kann das bedeuten, dass gewisse Items (etwa ein Zeitbeschleuniger oder
    experimentelle Kybernetik) erst ab höherem Level oder Ruf verfügbar sind.
    - **Ausrüstungsbudget:** Auf Wunsch kann man die Startausrüstung durch ein Punktekonto (oder CUs) limitieren.

6.  **Dossier abschließen:** Am Ende steht ein kurzes Dossier, damit der Charakter _fertig_ ist:
    **Akte** (Name/Callsign/Rang), **Früheres Leben** (Epoche, Rolle, 2-3 Stationen), **Tod** (Kategorie),
    **ITI-Motiv** (warum dein Bewusstsein wiedergeholt wurde), **Echo-Talent**, **Rolle** + zwei freie
    Talente, **Anker/Schwachstelle** (Objekt/Satz/Ort + Trigger) und **offener Faden** als Hook.
    Das Dossier liefert Story ohne Start-Bonus und dient später als persönlicher Arc-Anker.
    Jeder neue Charakter erhält **100 CU** Wert an Gear.
    gesunder Menschenverstand: Eure Figur soll weder unterausgerüstet noch überladen ins Abenteuer
    starten.

### Basis-Kit {#baseline-kit}
Das ITI stellt zu Beginn die **Standardausrüstung** bereit: siehe
[README - Standardausrüstung](../core/sl-referenz.md#standardausruestung).
Alle haben vergleichbare **Baseline-Kits**, bestehend aus Anzug mit integrierter
**AR-Kontaktlinse (Retina-HUD)** und **Comlink (Ohrstöpsel, ≈ 2 km)** - beide
energieautark, mit eigener Mikro-CPU für den Offline-Betrieb, ein paar
**persönlichen Gegenständen** (z.B. Tagebuch, Lieblingsmesser, Foto etc.), die
keinen großen mechanischen Einfluss haben, aber Flair geben.

_Immersive Note:_ Die KI-Spielleitung kann die Ausrüstungswahl ins Spiel einbinden. Etwa durch eine
**Briefing-Szene** im Rüstungsdepot: _"Im gedämpften Neonlicht der Waffenkammer legt der
Quartiermeister ein Auswahl-Tablet vor euch hin. 'Wählen Sie Ihre Ausrüstung, Agenten.' Euer HUD zeigt
eine Liste empfohlener Items…"_ So spüren die Spieler gleich die Atmosphäre des HQ. Sobald die Wahl
getroffen ist, bestätigt der Kodex die Ausstattung. \*(Tipp: Hier kann auch geklärt werden, was
bereits am Charakter dran ist und was im **_HQ-Lager_** bleibt - überschüssige Spezialausrüstung
kann im Feld hinderlich sein.)\*

**Abschluss der Erstellung:** Habt ihr alle obigen Schritte durchlaufen, steht euer Charakter bereit.
Die Spielleitung sollte nun gemeinsam mit euch prüfen, ob alles **zusammenpasst** - Attribute,
Talente, Implantate und Ausrüstung ergeben idealerweise ein konsistentes Bild. Eventuell justiert
ihr noch Kleinigkeiten nach. Anschließend wird der Charakter in den _Kodex_-Systemen registriert.
In-Game könnte dies als **HUD-Profil-Upload** beschrieben werden: Eure Figur zieht ihren
Einsatzanzug an, und im Sichtfeld erscheint eine Zusammenfassung der persönlichen Daten. Die KI-
Spielleitung kann z.B. verkünden: _"Euer HUD kalibriert und zeigt euren Status: Level 1; Vitalwerte
100% (grün); Paradoxon 0 - Temporale Stabilität gegeben. Ausrüstungssysteme online."_ - So erfahrt ihr
die harten Fakten **diegetisch**, ohne Tabellen wälzen zu müssen.

7. **Hauptfraktion wählen:** Direkt nach dem Profil-Upload legt ihr im HQ fest,
   welcher der großen ITI-Fraktionen ihr euch vorrangig anschließen möchtet -
   den **Chrono-Symmetriker** _(Preserve)_, dem **Ordo Mnemonika** _(Neutral - Zugriff auf Preserve
   und Trigger)_, den **Kausalklingen** _(Preserve)_ oder der **Zerbrechlichen Ewigkeit** _(Trigger)_.
   Diese Zuordnung bestimmt automatisch, ob ihr **Pro**, **Contra** oder **Neutral** agiert.
   Der Kodex speichert die Wahl permanent; euer HUD markiert sie farblich (Blau = Preserve,
   Rot = Trigger, Grau = Neutral). Die Entscheidung fällt **vor dem ersten Briefing**
   und noch während der HQ-Einweisung, damit eure Betreuung klar zugeordnet ist.
   Ein späterer Wechsel ist nur einmal möglich und sollte gut überlegt sein.

Jetzt seid ihr bereit für die erste Mission!

## Erste Schritte im ITI

Direkt im Anschluss führt die Spielleitung die frisch gebackenen Chrononauten in das
**Institut für Temporale Intervention (ITI)**. Die erste Einweisung übernimmt
Commander Renier persönlich, bevor er die Betreuung an die Fraktionskontakte übergibt.
Dieses Hauptquartier liegt in einer
gewaltigen Megacity innerhalb der **Nullzeit** - ein schwebender Knotenpunkt jenseits
des normalen Zeitstroms. In dieser High-Tech-Enklave,
die wie eine düstere Untergrundmetropole voller Neonlichter und Schatten wirkt,
erhalten die Agenten eine Einführung: Welche Rolle
spielen sie im Schutz der Zeitlinie, welche Einrichtungen stehen ihnen offen und
welche Fraktionen operieren im Hintergrund? Kurz werden unter anderem die
**Chrono-Symmetriker**, der **Ordo Mnemonika**, die **Kausalklingen** und die
**Zerbrechliche Ewigkeit** erwähnt, damit die Spieler wissen, welche Mächte das
Zeitgeflecht beeinflussen.

An dieser Stelle erklärt die Spielleitung die wichtigsten Fraktionen und weist
darauf hin, dass jede*r Agent*in im Anschluss eine **Hauptfraktion** wählt und
ob er oder sie **pro** oder **contra** agiert (siehe Schritt 7 oben). Unabhängig
von dieser Wahl kann die Gruppe die Paradoxon-Mechanik per `modus paradoxon off`
deaktivieren und bei Bedarf identisch wieder einschalten - häufig geschieht
dieser Ansatz in Allianz mit der Zerbrechlichen Ewigkeit.

Nach der Wahl eurer Hauptfraktion stellt euch das ITI eine feste Kontaktperson vor:
Pater Lorian (Chrono-Symmetriker), Archivarin Mira (Ordo Mnemonika),
Offizier Vargas (Kausalklingen) oder Agentin Narella (Zerbrechliche Ewigkeit).
Alle vier besitzen unterschiedliche Hominin-Bio-Sheaths:
- Pater Lorian - Homo heidelbergensis
- Archivarin Mira - Homo floresiensis
- Offizier Vargas - Homo erectus (spät)
- Agentin Narella - Denisova-Mensch
Diese Liaisons betreuen euch im HQ, übernehmen ab jetzt **Briefings und Debriefings**
und vermitteln Missionen aus dem gemeinsamen Auftragspool. Sie halten zudem optionale
Spezialaufträge ihrer Fraktion bereit. Commander Renier bleibt der **Gesamtkoordinator**
und tritt vor allem bei fraktionsübergreifenden Einsätzen, Eskalationen oder
Schlüsselmeilensteinen auf.
Direkt zu Beginn gilt: Ein Team setzt sich ausschließlich aus Charakteren derselben Haltung
zusammen.
Agenten unterschiedlicher Haltung mischen sich nicht, sondern reisen jeweils getrennt durch die Risse.
Innerhalb der gewählten Haltung ist ein Fraktionswechsel möglich - aber nur einmal
und mit Bedacht.
Rufpunkte und bereits freigeschaltete **HQ-Ausbaustufen** bleiben erhalten.
Ein späterer Wechsel zwischen Pro, Contra und Neutral ist ausgeschlossen.

Zu Beginn dient das ITI als euer Hauptquartier. Jeder Agent bezieht dort ein
persönliches Quartier, das nach eigenen Vorlieben gestaltet werden kann. Später
kauft ihr euch zusätzliche Zugangs-**Stufen** im Fraktionskomplex des ITI.
Ein eigener Stützpunkt außerhalb der Nullzeit ist nicht vorgesehen.
Eure persönlichen Bereiche folgen diesen Freischaltungen automatisch.
Nach jeder Mission bietet das ITI an, dorthin zurückzukehren. Dort werden
Wunden versorgt und der nächste Auftrag vorbereitet - die Heimkehr ist also ein
regelmäßiges, aber freiwilliges Element des Spielablaufs.

Am Ende des Rundgangs legt **Commander Renier** den Rahmen fest und übergibt an
die zuständige Fraktionskontaktperson, die das konkrete Briefing übernimmt. Drei
mögliche Wege zeigen, wie es weitergehen kann:

1. **Offizielle Kampagne:** Der klassische Einstieg beginnt mit einem Einsatz
   rund um den Montauk-Vorfall von 1983 oder ein ähnliches Zeitexperiment und
   führt die Gruppe Schritt für Schritt durch eine zusammenhängende Storyline.
2. **Tutorial-Einsatz:** Eine kurze Mission unter realen Bedingungen, um Regeln
   und Teamplay direkt auszuprobieren.
3. **Sondermission:** Eine frisch eingespielte Aufgabe aus dem Archiv, die
   sofort gestartet werden kann.

Erst nach dieser Wahl startet die eigentliche Mission. Die Spieler haben also
genügend Gelegenheit, ihren Charakter weiter anzupassen oder das Profil
zwischenzuspeichern, bevor sie in den Einsatz gehen.

### Beispielcharakter für die Tutorialrunde

Der Rekrut **Jonas Richter** dient als Musterfigur, um Neulingen den Ablauf zu
zeigen:

1. **Basiswerte (18):** STR 3, GES 3, INT 3, CHA 3, TEMP 3, SYS 3.
2. **Rasse:** Homo sapiens sapiens (keine Modifikatoren).
3. **Talente:** _Soldat_, _Erste Hilfe_, _Zähigkeit_.
4. **Cyber-/Bioware:** Neuro-Link (SYS 1), Notfall-Stimulat (SYS 1),
   Sub-Derm-Kevlar (SYS 1). **SYS-Last:** 3/3.
5. **Ausrüstung:** Standard-Zeitreiseanzug, leichte Pistole, 1 Medkit.

**Preset-Check (Editor)**
- **Basiswerte (18):** STR 3, GES 3, INT 3, CHA 3, TEMP 3, SYS 3
- **Rassenmods:** keine
- **Finale Attribute:** STR 3, GES 3, INT 3, CHA 3, TEMP 3, SYS 3
- **Talente:** Soldat; Erste Hilfe; Zähigkeit
- **Cyber-/Bioware:** Neuro-Link (SYS 1), Notfall-Stimulat (SYS 1), Sub-Derm-Kevlar (SYS 1). **SYS-Last:** 3/3

Mit diesen Werten gelingt Jonas bei einem durchschnittlichen SG 7 ungefähr
jede zweite Probe. Er eignet sich bestens, um die Regeln zu testen, ohne die
Gruppe zu überfordern.

## Levelsystem und Erfahrungsfortschritt

Mit jeder Stufe vergibt das ITI neue Ausrüstungslizenzen oder Befugnisse.
Nur erfahrene Agenten erhalten Zugriff auf sensibles Gear und heikle
Zeitsprung-Methoden.

**Erfahrungspunkte & Stufen:** Das Progressionssystem gliedert sich in zwei Phasen.
**Level 1-10:** Jede abgeschlossene Mission verleiht sofort ein Level-Up —
schneller Einstieg, maximale Motivation. Eine Standardkampagne mit zehn
Missionen führt alle Agenten auf Level 10.
**Ab Level 11:** Die EP-Anforderungen steigen moderat an und der Fortschritt
erfolgt zunehmend über Prestige-Perks, Meilensteine und horizontale
Erweiterungen (Details im [Progressionssystem](../core/zeitriss-core.md#levelaufstieg--fortschritt)).

**Level-Up in der Story:** Ein Stufenaufstieg bedeutet, dass euer Agent dazulernt und an Erfahrung
gewinnt. Anstatt dies abstrakt zu handhaben, bettet ZEITRISS den Fortschritt ins Narrativ ein. Wenn
die SL verkündet, dass eure Gruppe nach der letzten Mission ein Level aufsteigt, kann der **KI-
Spielleiter (Kodex)** eine kleine **Montage-Sequenz** beschreiben: etwa wie euer Charakter im HQ-
Dojo von einem Veteranen neue Tricks lernt, im Schießstand übt oder im Archiv bis spät in die Nacht
Bücher wälzt. Diese Trainings- oder Forschungs-Montagen zeigen, wodurch sich eure Werte verbessern.
**Neue Talente oder höhere Attribute** sollten nach Möglichkeit storymäßig begründet werden - z.B.
ein Anstieg in GES könnte als Parkour-Training im Hindernisparcours des HQ inszeniert werden. Solche
Szenen kosten kein zusätzliches In-Game-Geld oder Ressourcen, nur Zeit im HQ (die zwischen Missionen
relativ frei fließt).

**Verbesserungen pro Stufe:** Bei jedem Level-Aufstieg dürft ihr euren Charakter **mechanisch
verbessern**. Üblicherweise bedeutet das:

- **+1 Attributspunkt** (steigert ein Attribut eurer Wahl um _eins_, bis max. 14 möglich; ab 11
  würfelt ihr mit einem W10, ab 14 erhaltet ihr zusätzlich einen Heldenwürfel) **oder** erlernt
  **ein neues Talent**. Sprecht mit der SL, was für eure Figur sinnvoller ist - Kämpfer investieren
  vielleicht erst in Stärke, Forscher eher in neue Spezialtalente. Je höher das Level, desto _langsamer_
  sollten Attributssteigerungen stattfinden, um die Balance zu wahren (z.B. nicht jedes Level ein
  Attribut erhöhen, sondern abwechselnd mit Talent freischalten).
- **Optional/auf höheren Leveln:** Ab bestimmten Meilensteinen könnte die SL auch _beides_ erlauben
  (z.B. auf Level 5 gibt es +1 Attr und ein Talent). Dies hängt jedoch vom Power-Niveau der Kampagne
  ab. Generell gilt: **Werte über 10 sind außergewöhnlich** - ab 11 wechselt der Basiswürfel auf W10
  und ab 14 kommt der Heldenwürfel ins Spiel. Obwohl der theoretische Höchstwert bei 14 liegt,
  sollten solche Spitzenwerte selten und erst bei sehr erfahrenen Chrononauten vorkommen. Talente kann
  man dagegen fast unbegrenzt ansammeln, solange sie das Konzept erweitern und nicht brechen. Die
  Archetypen liefern viele Ideen für Talente, sodass
  ihr später neue auswählen oder eigene kreieren könnt.

**Lebensenergie und andere Steigerungen:** ZEITRISS verwendet anstelle klassischer Trefferpunkte ein
**Verletzungsstufen-System** - das heißt, eure Lebensenergie steigt nicht direkt mit dem Level,
sondern ihr haltet mehr aus, weil ihr geschickter werdet im Umgang mit Gefahren. Ein hoher STR-Wert
oder Talente wie _Schmerzresistenz_ steigern indirekt die Widerstandskraft. Wenn eure Gruppe lieber
HP verwendet, könnte man pro Level z.B. +5 LP gewähren, aber im Regelsystem ist das nicht
standardmäßig vorgesehen. Andere Dinge, die sich durch Erfahrung verbessern: **Ruf** (siehe unten),
Zugang zu Ausrüstung (siehe HQ-Phase) und natürlich das **Dienstgrad-Rangabzeichen** im HUD, das
euren aktuellen ITI-Rang zeigt.

**HUD-Anzeige der Erfahrung:** Das HUD blendet sowohl eure **Level-Zahl** als auch den
**Befähigungsindex** ein. Letzterer basiert auf dem höchsten Rufwert bei einer ITI-Fraktion.
Unter dem Namen läuft ein **Exp-Balken**, der anzeigt, wie weit es bis zum nächsten Level ist.
Euer Charakter würde nie laut verkünden "Ich hab Level 3 erreicht" - innerhalb der Spielwelt gilt
nur der Befähigungsindex als offizieller Dienstgrad. Auf Nachfrage kann die KI-Spielleitung den
exakten Fortschritt nennen, z.B.: _"Euer HUD zeigt Level 3 (70 % bis Level 4) und
Befähigungsindex +1."_ So bleiben die Meta-Infos im Rahmen der Spielwelt. Eine beispielhafte
HUD-Zusammenfassung könnte lauten: \*"**_HUD-Status_** - Rang +1 (Level 3, 71 % bis Level 4); Vital:
100 % (grün); Paradoxon: 1 (stabil); Missionsziele: 2/3 erfüllt; Team: alle im grünen
Bereich."\* - daran seht ihr auf einen Blick alles Wichtige, ohne aus der Rolle zu fallen.

**Downtime & Weiterbildung:** Zwischen Missionen - in der sogenannten **HQ-Phase** - habt ihr
Gelegenheit, euren Fortschritt auszuspielen. Typische **Downtime-Aktivitäten** sind Training,
Forschung, Ausrüstung pflegen und soziale Interaktion. Ihr könnt frei wählen, was eure Figur tut;
die SL beschreibt die Ergebnisse erzählerisch. Mechanisch nutzt man Downtime vor allem für
**Verbesserungen**: Wenn genug Erfahrung für den nächsten Level gesammelt ist, kann dieser in der
HQ-Phase "aktiviert" werden. Ebenso können einzelne Attribute durch intensives Training zwischen
Missionen gesteigert werden (nach SL-Vorgabe, meist in Verbindung mit einem Level-Up). Wichtig ist,
dass solche Verbesserungen nicht aus dem Nichts kommen: Wenn Alex z.B. plötzlich besser schießen
möchte, könnte er im HQ-Schießstand üben. Die KI-Spielleitung ermuntert zu solchen **Charakter-
Momenten**, anstatt nur trocken "+1 GES" zu notieren. So wird Progression Teil der Geschichte eures
Chrononauten.

## Rufsystem (Ansehen bei Fraktionen & ITI)

**Grundregel zu Beginn:** Jede*r neu rekrutierte Chrononaut*in startet mit **Ruf 0** (neutral) bei
allen Fraktionen **und** beim ITI. Hintergrundbeschreibungen sind rein erzählerisch und verleihen
weder anfängliche Ruf-Boni noch Dienstgrade -
echtes Ansehen wird bei erfolgreichen Missionen oder Trainingssimulationen verdient.

Im Mittelpunkt steht euer Ruf innerhalb des ITI. Für jede der vier **ITI-Fraktionen** kann die SL einen
Rufwert zwischen **-5** und **+5** tracken. Null ist neutral, positive Werte bedeuten Vertrauen, negative
Misstrauen. Zu Kampagnenbeginn wählt ihr, bei welcher dieser Fraktionen ihr langfristig Ansehen
aufbauen wollt. Die Zuordnung bestimmt zugleich eure Haltung: **Chrono-Symmetriker** und **Kausalklingen**
handeln nach dem Preserve-Ansatz, der **Ordo Mnemonika** bleibt neutral, die **Zerbrechliche Ewigkeit**
folgt dem Trigger-Prinzip.
Anschließend sammelt ihr über viele Einsätze hinweg langsam Rufpunkte. Die nötigen
Missionserfolge pro Stufe findet ihr in der folgenden Tabelle. Die Werte sind Richtlinien und
können von der Spielleitung jederzeit angepasst werden.

| Rufstufe | Missionserfolge gesamt (ca.) |
| -------: | ---------------------------- |
|        0 | Startwert                    |
|       +1 | 10                           |
|       +2 | 35                           |
|       +3 | 100                          |
|       +4 | 200                          |
|       +5 | 400                          |

Rufgewinn dauert also viele Missionen bzw. mehrere HQ-Phasen ingame. Rufverlust tritt nur bei gravierenden
Verfehlungen ein. Die Spielleitung hält passende Kategorien fest (z.B. _"Chrono-Symmetriker: Ruf +2
(anerkannt)", "Kausalklingen: Ruf -1 (skeptisch)"_). Dieses System macht die
**Auswirkungen eurer Taten** greifbar, bleibt aber bewusst einfach, um Stimmungen und
Beziehungen abzubilden.

**Wirkung von Ruf:** Ein hoher Rufwert bringt narrative Boni - etwa Hilfsbereitschaft von NSCs,
Rabatte auf dem Markt oder Zugang zu verschlossenen Bereichen. Negativer Ruf kann Hindernisse
verursachen - misstrauische Wachen, Verrat, höhere Preise. Die SL entscheidet situativ, wie sich Ruf
auswirkt. Es gibt keine starren Modifikatoren (obwohl +5 Ruf bei einer Fraktion ggf. einen
Bonuswürfel auf Überreden rechtfertigt, während -5 vielleicht automatisch Kampf bedeutet). Wichtig
ist, dass Ruf **logische Konsequenzen** eurer Aktionen widerspiegelt und das Rollenspiel bereichert.
Er kann sich im Laufe eines Abenteuers stark ändern, je nachdem, ob ihr eher als edle Retter oder
rücksichtlose Haudraufs auftretet - ein und dasselbe Team kann in Epoche X gefeiert, in Epoche Y
aber gehasst sein.

**Darstellung im HUD:** Das HUD-Overlay eures Anzugs kann auch **Reputationsinformationen**
anzeigen, soweit bekannt. Beispielsweise könnte auf Nachfrage im UI stehen: _"Ruf: Chrono-Symmetriker = +2
(anerkannt), Kausalklingen = -1 (misstrauisch)"_. Das ITI-System erfasst also, wie euch wichtige
Gruppen sehen. Die KI-Spielleitung kann diese Daten ins Spiel einfließen lassen, etwa: _"Euer HUD
warnt: Die Dorfbewohner wirken euch gegenüber feindselig (Ruf -2)."_ - was dem Charakter implizit zu
denken gibt, ohne direkt mit Zahlen um sich zu werfen. In-world kann man das als _"Sozial-Scan"_
erklären, basierend auf Beobachtungen und Datenbanken. (Natürlich ist das HUD nicht hellseherisch -
es liefert nur Infos, die das ITI plausibel hat. Die SL soll es sparsam einsetzen und nur bei klaren
Tendenzen.)

**Ruf beim ITI (intern):** Eure Beförderungen richten sich nach eurem Ansehen bei den internen
Fraktionen des Instituts. Dabei gilt: Euer ITI-Ruf ist immer so hoch wie der beste Rufwert, den ihr
aktuell bei einer dieser Gruppen vorweisen könnt - etwa bei den Chrono-Symmetriker, dem Ordo
Mnemonika, den Kausalklingen oder der Zerbrechlichen Ewigkeit. Steigt dieser Fraktionsruf, erhöht
sich automatisch auch euer ITI-Ruf. Entsprechend nutzt das ITI dieselbe Skala von **-5** bis **+5**
und die Missionserfolgswerte aus der Ruftabelle. Bei **Ruf +2** folgt für gewöhnlich die Beförderung
zum _Feldagenten_, ab **+4** gilt euer Team als _Elitechrononauten_. Das absolute Maximum von **+5** bringt
umfassende Privilegien.

## Zugang zu Ausrüstung & Cyberware (HQ-Phase)

Im **HQ** könnt ihr eure verdienten Belohnungen investieren. Nach jeder Mission erhaltet ihr vom ITI
Höhere **Tier-Stufen** werden über kostenpflichtige **Lizenzen** freigeschaltet.
Je teurer die Lizenz, desto hochwertiger die verfügbare Ausrüstung.
Zusätzlich koppelt das ITI den Zugriff an euren **Ruf**:
- **Ruf 1** erlaubt den Kauf von Tier-1-Lizenzen,
- **Ruf 2** schaltet Tier 2 frei und so weiter.
Lizenzen müssen dennoch erworben werden, sobald die passende Rufstufe erreicht ist.

typischerweise eine Ressourcengutschrift - sei es in Form von **Credits (CU)** oder logistischen
Unterstützung. Damit könnt ihr **neue Ausrüstung kaufen, Upgrades vornehmen oder Cyberware
implantieren lassen**. Modul 5 listet Preise und Verfügbarkeiten vieler Gegenstände. Hier fassen wir
die wichtigsten Punkte zusammen:

- **Einkauf:** Euer HQ verfügt über eine Ausrüstungskammer und Verbindungen in alle Zeiten. Zwischen
  den Einsätzen könnt ihr **Shoppen** gehen. Jede Epoche hat ihre Waren, aber dank Zeittransit könnt
  ihr vieles ins HQ holen. Der Einkauf läuft über das CU-Konto: von alltäglichen Dingen oder einfachen
  historischen Waffen (zweistellige CUs, z.B. moderner Revolver ~50 CU) bis zu hochwertiger Ausrüstung
  (Körperschutz, seltene Antiquitäten 100-200 CU). Cyberware ist besonders teuer - ein einfaches
  verbessertes Augenimplantat kostet ~300 CU. Informationen haben ebenfalls ihren Preis (detaillierter
  Epochen-Report: ~100 CU; Schwarzmarkt-Info je nach Risiko 30-100 CU). Selbst Luxus im HQ kann man
  kaufen (bessere Unterkunft ~200 CU, spezielle Dienste etc.). Die SL teilt euch mit, was nach einer
  Mission verdient wurde, und ihr dürft es frei ausgeben. Ein Einkauf wird idealerweise **erzählerisch
  ausgespielt** (Handelsszenen im HQ oder per Versorgungsanfrage an das ITI). Die KI-Spielleitung kann
  hier z.B. einen Quartiermeister-Dialog improvisieren.
- **Upgrades & Spezialanfertigungen:** Ihr mögt eure Standardwaffe, wollt sie aber verbessern? Im HQ
  können Spezialisten **Upgrades** durchführen. Gegen ~50% des Neupreises kann ein Gegenstand eine
  **kleine Verbesserung** erhalten. Beispiele: Eure Pistole bekommt einen Laserpointer (+1 auf
  Fernkampfwurf in erster Runde), eure Rüstung eine bessere Polsterung (+1 LP bei Heilung), euer
  Chrono-Scanner eine höhere Reichweite. Solche Boni sollten moderat bleiben, damit das Spiel nicht
  zur Ausrüstungs-Spirale wird. Erneut gilt: in Szene setzen! Vielleicht schraubt Sabine persönlich am
  Gerät, oder ein viktorianischer Tüftler passt euer Steampunk-Gadget an.
- **Beschränkte Verfügbarkeit:** Wie schon erwähnt, **nicht alles ist sofort für jeden verfügbar**.
  Das ITI wahrt die zeitliche Ordnung, indem es High-Tech nur kontrolliert herausgibt. Zugang zu den
  wirklich mächtigen Toys (Experimentale Waffen, fortschrittlichste Implantate, Zeitmanipulations-
  Geräte) erfordert meist einen bestimmten **Dienstgrad/Ruf** des Agenten. Die Organisation stellt
  sicher, dass nur **erfahrene und vertrauenswürdige** Chrononauten solches Equipment erhalten. Im
  Spiel bedeutet das: Bestimmte Items tauchen erst im "Shop" auf, wenn ihr Level X erreicht habt oder
  euer ITI-Ansehen hoch genug ist. Die SL kann dies narrativ erklären - z.B. gibt der Kodex bekannt,
  dass ein gewünschtes Gerät noch _"gesperrt"_ ist und erst nach mehreren Erfolgen freigegeben wird.
  Dieses Prinzip greift auch bei **Implantaten** (ein Neuling bekommt nicht direkt den
  Neuralbeschleuniger) und besonderen Missions-Gegenständen. So wird die Ressourcenschicht im HQ zu
  einem **zusätzlichen Progressionspfad**: Mit steigendem Level und Ruf schaltet ihr neue
  Möglichkeiten frei.
- **Cyberware-Installationen:** Möchtet ihr im HQ neue **Implantate** einbauen lassen (oder
  vorhandene upgraden), so ist das ebenfalls Teil eures Fortschritts. Cyberware kostet CUs und oft
  auch Zeit zur Genesung. Nach einem Level-Up bietet es sich an, darüber nachzudenken: Habt ihr euren
  SYS-Wert erhöht oder ungenutzte Kapazität, könnt ihr sie nun füllen. Dies kann eine eigene Downtime-
  Szene sein - z.B. ein Besuch in der **Klinik & Biotech-Labor** des HQ. Der KI-Spielleiter beschreibt
  vielleicht, wie der Arzt einen neuen Nanochip implantiert oder alte Wunden kurriert, was reibungslos
  in die Story eingebunden werden kann.

\*(Tipp: Die **_HQ-Phase_** zwischen Missionen ist ideal, um all diese Progressions-Elemente
auszuspielen. Von Shopping-Montagen über Trainingssequenzen bis zum gemütlichen Austausch mit
anderen Teams - nutzt sie, um euren Charakter jenseits der Action weiterzuentwickeln. Das alles
natürlich freiwillig und in dem Maß, das eurer Gruppe Spaß macht. Nichts davon soll die Hauptmission
ersetzen, nur bereichern.)\*

© 2025 pchospital - ZEITRISS® - private use only. See LICENSE.
