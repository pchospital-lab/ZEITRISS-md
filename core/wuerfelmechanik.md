---
title: "ZEITRISS 4.0 – Modul 2: Explodierende Würfel, HUD-Alerts & cineastische Schlachten"
version: 4.0
tags: [core]
---

# ZEITRISS 4.0 – Modul 2: Explodierende Würfel, HUD-Alerts & cineastische Schlachten
## Inhalt
- Würfelmechanik: Explodierende 6 & W10-Variante
- HUD-Management: Ereignis-Alerts & Info-Triage
- Attributs-Skalierung: Heldenwürfel & Endgame-Balance
- Speichersystem-Erweiterung: Versionskennzeichnung & Kompatibilität
- Cineastische Schlachten: Erfolgspools, Spotlight-Szenen & heroische Würfe


*Mit letzter Kraft erhebt sich Chrononaut Leon aus dem Trümmerfeld, während um ihn eine epische
Schlacht tobt. Sein HUD überschlägt sich mit Warnmeldungen – ***Vitalstatus kritisch: 10%***,
***Paradox-Index +1*** –, doch er blendet die Alarme aus. Jetzt zählt nur noch dieser eine
verzweifelte Versuch. Leon schultert die Energie-Lanze eines gefallenen Mech-Piloten, legt an und
drückt ab. Ein gleißender Strahl zerfetzt die angreifende Zeitanomalie – ein schier unmöglicher
Treffer, zustande gekommen durch eine Prise Heldenmut und Würfelglück. Der Codex protokolliert
ungläubig: „Ziel eliminiert – Erfolgschance \< 5%“. Es sind genau solche filmreifen Momente, die
ZEITRISS zum Leben erwecken.*

Willkommen zu einem weiteren Modul für **ZEITRISS 4.0**, das Feinschliff und neue cineastische
Optionen ins Spiel bringt. Dieses Regelmodul erweitert das System um spannende Verbesserungen in der
Würfelmechanik, ein dynamisches HUD-Warnsystem, feinere Attributs-Skalierung, ein robustes
Speichersystem und alternative Regeln für große **Schlachten** – ohne den erzählerischen Fokus zu
verlieren. Im Folgenden findet ihr neue Regeln und Inspirationen, um kritische Proben noch
nervenaufreibender, das HUD der Agenten informativer (aber nicht überwältigend) und Massengefechte
so filmisch wie im Kino zu gestalten. Kurzum: Mehr **Drama** und **Tiefe**, aber weiterhin
übersichtlich und spielbar am Spieltisch.

**Dieses Modul enthält im Überblick:**

- **Neue Würfelmechaniken:** Einführung der **„Exploding 6“**-Regel für W6-Proben, die bei einer
gewürfelten 6 einen zusätzlichen Wurf gewährt – für unerwartete Spitzenresultate. Außerdem eine
**optionale** Regelvariante, sämtliche Proben mit W10 statt W6 durchzuführen, um eine feinere
Granularität und ein breiteres Erfolgsspektrum zu ermöglichen.
- **HUD-Management & Alerts:** Ein ereignisgesteuertes Warnsystem für das HUD der Chrononauten, das
bei definierten kritischen Zuständen (z. B. Lebenspunkte \< 25 % oder sobald *Paradox \> 0*)
automatisch Alarm schlägt. Dazu kommen Vorschläge für **Info-Triage**, damit in brenzligen
Situationen nur wirklich wichtige Daten eingeblendet werden und die Agenten nicht von
Informationsflut überwältigt werden.
  In Kampagnen, die bewusst **contra** zur offiziellen Zeitlinie gespielt werden,
  darf die Paradox-Warnung auf Wunsch deaktiviert werden. Wer sie aktiviert,
  nutzt das System identisch zu Pro-Gruppen.
- **Attributs-Skalierung & Heldenwürfel:** Neue Regeln für Charaktere mit außergewöhnlichen
Attributwerten: Ab einem Wert von **11** erhält der Held einen **Heldenwürfel** (zweiter Wurf,
besseres Ergebnis zählt) als Vorteil. Zusätzlich geben wir Hinweise, wie SL und Spieler einer
übermäßigen Attribut-Inflation im Endgame entgegenwirken, um die Balance zu wahren.
- **Erweitertes Speichersystem:** Save-Dateien (JSON) erhalten ab sofort ein
**Versionskennzeichen**, um die Kompatibilität mit zukünftigen Regelupdates sicherzustellen. Wir
zeigen Beispiele, wie **versionskompatible** Speicherstände aussehen und wie das Spiel mit
unterschiedlichen Versionen umgeht, damit eure Kampagnen-Logs auch nach Updates nahtlos
weiterverwendet werden können.
- **Cineastische Schlachten:** Eine alternative Regelabwicklung für große Konflikte, die
**filmisch** statt kleinteilig funktioniert. Durch **Erfolgspools**, spannende **Spotlight- Szenen**
für jede/n Chrononauten und **heroische Schlüsselwürfe** werden Massenkämpfe übersichtlich
dargestellt, ohne an Dramatik einzubüßen – ganz im Stil eines mitreißenden Actionfilms, bei dem die
Heldentaten den Ausschlag geben.

## Würfelmechanik: Explodierende 6 & W10-Variante

Nervenzerfetzende Würfelwürfe gehören zum Kern von ZEITRISS. Um die Spannung jeder Probe noch zu
steigern, führen wir die Regel **„Exploding 6“** ein – im Deutschen oft schlicht *explodierender
Würfel* genannt. **Immer wenn bei einer W6-Probe eine 6 gewürfelt wird,** wird der W6 **erneut
geworfen** und das neue Ergebnis zur bisherigen Summe **addiert**. Sollte dabei wieder eine 6
fallen, wiederholt sich der Vorgang so lange, bis kein Maximum mehr erscheint. Auf diese Weise sind
theoretisch **Ergebnisse über dem normalen Limit** möglich, was besonders heroische Erfolge oder
dramatische Wendungen darstellen kann. Spielerinnen und Spieler erleben einen zusätzlichen
Adrenalinstoß, wenn der Würfel „explodiert“ – denn aus einem sicheren Misserfolg kann so doch noch
ein triumphaler Erfolg werden. *(Beispiel: Nadia muss einen schwierigen Sprung über eine Schlucht
meistern. Sie hat nur mäßige Werte, bräuchte aber mindestens eine 10. Sie würfelt eine 6 – diese
„explodiert“, sie darf erneut werfen. Der zweite Wurf zeigt eine 4. Zusammen ergibt das 6+4=10 –
gerade noch geschafft! Die Gruppe jubelt ob dieses glücklichen Ausgangs.)*

**Optionale W10-Regel:** Für Gruppen, die eine feinere Abstufung bei Würfelergebnissen bevorzugen,
bietet ZEITRISS alternativ den **Zehnseitigen Würfel (W10)** als Basis für Proben. Mit einem W10
erstreckt sich der mögliche Wertebereich von 1–10 (anstatt 1–6), wodurch **Granularität** und
Varianz zunehmen. Kleine Unterschiede in Attributen oder Fertigkeiten wirken sich damit etwas
weniger stark absolut aus, was Proben **ausgewogener** machen kann. Die SL sollte die
Schwierigkeitsgrade der Proben bei Verwendung von W10 im Blick behalten – in der Regel erfordern
Aufgaben etwa 4 Punkte höhere Zielwerte, um die höhere durchschnittliche Würfelsumme auszugleichen.
Die **Exploding**-Regel lässt sich grundsätzlich auch auf einen W10 übertragen (*Exploding 10*, bei
einer gewürfelten 10 wird erneut geworfen). Allerdings entsteht durch einen W10 alleine schon mehr
Spannungsbreite; ob man zusätzlich explodierende Würfel bei 10 einsetzt, kann die Gruppe nach
gewünschter Dramaturgie entscheiden. In jedem Fall gilt: Beide Mechanismen – **Explodierende 6** und
der **W10-Ersatz** – sind **optional** und sollten nur eingesetzt werden, wenn sie zum Stil der
Runde passen. Sie bieten frischen Wind für erfahrene Runden, ohne das Grundsystem fundamental zu
verändern.

**Schwellen-Kalibrierung:** Standardproben nutzen einen W6 und gelten bei **4 oder höher** als
erfolgreich. Für erfahrene Chrononauten mit W10 liegt die Schwelle bei **5+**. Ein
**Heldenwürfel** ermöglicht einmal pro Szene einen kostenlosen Reroll auf eine Probe.

**Hinweis:** Durch explodierende Würfel können gerade unwahrscheinliche Aktionen spektakulär
gelingen. Die Spielleitung sollte dies erzählerisch hervorheben – z. B. durch cineastische
Beschreibungen, wie ein Charakter mit unglaublichem Glück das Blatt wendet. Gleichzeitig dürfen
solche Glückstreffer nicht zur Alltagskost werden: Explodierende Würfel sollten besondere Highlights
bleiben, die denkwürdige Szenen schaffen. Wenn Würfelpech umgekehrt dramatische Fehlschläge
produziert, kann dies ebenso interessant inszeniert werden (Stichwort **kritischer Patzer**), sofern
es zur Geschichte passt.

## HUD-Management: Ereignis-Alerts & Info-Triage

In der high-tech ausgestatteten Welt von ZEITRISS begleiten **HUD-Overlays** und der allgegenwärtige
Codex-KI die Chrononauten auf ihren Missionen. Bisher lieferte das HUD kontinuierlich Daten – von
Vitalwerten über Missionsziele bis hin zu Umweltanalysen. Nun verfeinern wir das System mit einem
**ereignisgetriggerten Alert-Mechanismus**, der sicherstellt, dass in kritischen Momenten
**sofortige Warnungen** erfolgen und Unwichtiges ausgeblendet wird.

**Alert-Auslöser definieren:** Bestimmte Zustände lösen fortan automatische **Alarmmeldungen** im
HUD aus, um die Agenten zu warnen oder ihre Aufmerksamkeit zu fokussieren. Zwei zentrale Beispiele
im ZEITRISS-System sind: **(1)** Der **Vitalstatus** fällt unter **25 %** – in diesem Fall erscheint
z. B. ein rotes Aufleuchten des Gesundheitsbalkens, begleitet von einem akustischen Warnsignal und
dem Hinweis *“Vitalwerte kritisch – medizinische Intervention empfohlen”*. **(2)** Der **Paradox-
Index** steigt über **0** – das bedeutet, es treten Anomalien oder Zeitstörungen auf. Hier könnte
der Codex via HUD ein gelbes *“Paradox-Warnung: Temporalinstabilität detektiert”* einblenden, um das
Team vorzuwarnen. Natürlich lassen sich auch weitere Alerts definieren: Etwa wenn die **Munition**
einer wichtigen Waffe zur Neige geht, ein **Teammitglied ausfällt** (Alarm: *“Agent down”*) oder ein
**Missionszeit-Limit** fast erreicht ist. Die **Spielleitung** und die Gruppe sollten gemeinsam
festlegen, welche Schwellenwerte und Ereignisse im Rahmen ihrer Kampagne relevant sind. Wichtig ist,
dass Alerts **nicht inflationär** auftreten, sondern wirklich nur bei *kritischen* Entwicklungen –
so behalten sie ihr Gewicht und stören nicht den Spielfluss.

**HUD-Triage & Fokusmodus:** Zeitgleich mit den Alerts führt der Codex einen intelligenten Filter
ein, um **Informationsflut zu vermeiden**. In hektischen Situationen – etwa im Gefecht oder bei
einer Verfolgungsjagd – schaltet das HUD automatisch in einen **Fokusmodus**: Unkritische Anzeigen
(z. B. ausstehende Nebenmissionsziele, Umgebungsdaten ohne unmittelbare Relevanz, stilistische HUD-
Designelemente) werden temporär ausgeblendet oder dezent zurückgefahren. Stattdessen rücken
**prioritäre Infos** in den Vordergrund: die Warnmeldungen, Statusanzeigen der Teammitglieder und
relevante Missionshinweise. Diese **Info-Triage** sorgt dafür, dass die Spielercharaktere (und damit
die Spielenden) sich auf das Wesentliche konzentrieren können, ähnlich einem Pilotendisplay, das im
Notfall in den “Cleared Screen”-Modus wechselt. Sobald die Lage sich beruhigt, kehrt das HUD
automatisch in den Normalmodus zurück und zeigt wieder alle Informationen an.

**Beispiel:** *Agentin Nova befindet sich inmitten eines Feuergefechts. Ihr HUD projiziert zunächst
allerlei Daten ins Sichtfeld – taktische Karten, Funksprüche, Missionsnebenziele. Als Nova jedoch
schwer verwundet wird (HP fallen unter 25 %), ändert sich das HUD schlagartig: Fast alle Anzeigen
verblassen, nur Novas Gesundheitsanzeige blinkt rot und ein Pfeil markiert das nächste Deckungs-
Versteck. Gleichzeitig ertönt ein Warnton und der Codex meldet: „Vitalwerte kritisch – Evakuierung
empfohlen.“ Nova schleppt sich in Deckung und verabreicht sich ein Stimpack. Sobald ihre HP wieder
über dem Gefahrenwert liegen, kehren nach und nach die übrigen HUD-Elemente ins Sichtfeld zurück.*

Durch diese Mechaniken bleibt das **HUD-Overlay** ein mächtiges Werkzeug, ohne zur Ablenkung zu
werden. Die Spielleitung kann diese Features nutzen, um dramaturgisch Akzente zu setzen – z. B.
indem in einem Horror-Abschnitt plötzlich *alle* Daten außer einem flackernden Paradox-Alarm
verschwinden, was die verunsichernde Atmosphäre unterstreicht. **Weniger ist oft mehr:** Setzt
Alerts gezielt ein, damit sie die Spieler warnen und ins Geschehen ziehen, anstatt sie mit ständigen
Pop-ups abzulenken. Richtig eingesetzt, erhöht das HUD-Management die Immersion und gibt den Helden
das Gefühl, von ihrer Ausrüstung optimal unterstützt zu werden – gerade wenn es brenzlig wird.

## Attributs-Skalierung: Heldenwürfel & Endgame-Balance

ZEITRISS 4.0 zeichnet sich durch ein schlankes Attributssystem (Werte meist im Bereich 1–10) aus.
Doch was passiert, wenn ein Held im Laufe der Kampagne über sich hinauswächst und einen Wert
jenseits der menschlichen Spitze erreicht? Hier kommt unsere neue Mechanik ins Spiel: der
**Heldenwürfel**. Dieser besondere Würfel stellt sicher, dass **Attributswerte über 10** spürbar
belohnt werden, ohne aber die Spielbalance zu sprengen.

**Heldenwürfel ab Attribut 11:** Erreicht ein Charakter einen Attributswert von **11 oder höher**,
so erhält er bei Proben, die auf diesem Attribut basieren, automatisch einen **zusätzlichen Würfel**
als Vorteil. Praktisch wird dann **zweimal gewürfelt**, und es zählt das bessere der beiden
Ergebnisse (vergleichbar mit einem Vorteilwurf). Dieser zusätzliche Wurf – der sogenannte
*Heldenwürfel* – reflektiert die außergewöhnliche Fähigkeit des Charakters: Über-menschliche Stärke,
Genialität, Schnelligkeit oder Willenskraft. Die Wahrscheinlichkeit, dass die Probe gelingt, steigt
dadurch merklich an, sodass ein Wert von 11 gegenüber einem Wert von 10 **nicht nur +1 mehr**
bedeutet, sondern einen qualitativen Sprung darstellt. Heldenwürfel kommen natürlich **zusätzlich**
zu allen anderen Modifikatoren zum Einsatz. Sollte auch beim Heldenwürfel die Regel *Exploding 6*
aktiv sein, kann selbstverständlich auch dieser explodieren – regeltechnisch wird dann mit beiden
Würfeln getrennt die Explosions-Regel angewandt, was zu wahrhaft legendären Ergebnissen führen kann,
aber entsprechend selten ist.

**Beispiel:** *Chrononaut Carlos hat dank zahlreicher Abenteuer seine Geschicklichkeit auf 11
gesteigert – ein Wert jenseits normaler menschlicher Limits. Als er nun versucht, in letzter Sekunde
durch ein sich schließendes Portal zu hechten, darf er zwei W6 werfen. Er erzielt eine 2 und eine 5;
dank des Heldenwürfels nimmt er die 5 – genug, um es gerade noch hindurch zu schaffen. Hätte er nur
einen Wurf gehabt, wäre vielleicht nur die 2 gefallen und Carlos gestrandet. In einer späteren Szene
klettert er eine futuristische Festungsmauer hinauf. Wieder würfelt er zweimal: Eine 6 und eine 6 –
beide Würfel explodieren! Im zweiten Anlauf kommen noch eine 4 und eine 3 hinzu, also 6+4 vs. 6+3.
Carlos’ bester Wurf ist damit eine ***10***, was ihm einen spektakulären Aufstieg über die
Festungsmauer ermöglicht, als würde ihm das Schicksal selbst einen Schub verleihen.*

**Balance im Endgame:** So nützlich Heldenwürfel sind, so vorsichtig sollten Spielleiter mit **zu
hohen Attributwerten** am Ende einer Kampagne umgehen. Ein Wert von 12 oder 13 (mit Heldenwürfel)
macht viele normale Herausforderungen trivial – was einerseits verdienter Ausdruck des Heldentums
sein kann, andererseits aber die Spannung mindern könnte, wenn die Helden alles zu leicht schaffen.
Daher empfiehlt es sich, das **Fortschrittstempo** bei Attributen ab einem gewissen Niveau zu
drosseln. Die Spielleitung kann etwa festlegen, dass Steigerungen über 10 hinaus **besonders
selten** sind und nur durch bedeutsame Meilensteine oder aufwendiges Training erreicht werden.
Alternativ können statt reiner Zahlensteigerung mehr **qualitative Fortschritte** im Vordergrund
stehen: neue Talente, Spezialisierungen oder Ressourcen, die den Charakter verbessern, ohne bloß die
Attributszahl in die Höhe zu treiben. **Hinweis:** Denkt daran, dass selbst mit Heldenwürfel keine
Aufgabe absolut garantiert gelingt – der Würfel bleibt ein Risikofaktor. Erzählerisch können Gegner
im Endgame ebenfalls mit besonderen Vorteilen oder höheren Werten auftreten, sodass die Helden trotz
ihrer Macht gefordert bleiben. Kurz gesagt: Der *Heldenwürfel*-Mechanismus gibt den Spielern das
befriedigende Gefühl echten Heldentums, während durch umsichtiges Balancing die **dramatische
Spannung** bis zum Schluss erhalten bleibt.

## Speichersystem-Erweiterung: Versionskennzeichnung & Kompatibilität

ZEITRISS setzt auf eine enge Verzahnung von Regelwerk und technischer Unterstützung durch den Codex
(die KI-Spielleitung). Damit eure Kampagnenstände auch über Updates hinweg reibungslos
funktionieren, führen wir ein Update im **Speichersystem** ein: **Versionstagging** für Spielstände.
Jeder gespeicherte Spielstand (z. B. in Form einer JSON-Datei) erhält künftig einen
**Versionskennzeichner**, der angibt, mit welcher Regelwerks-Version er erstellt oder zuletzt
konvertiert wurde. Dies mag nach einem rein technischen Detail klingen, hat jedoch handfeste
Vorteile für die Spielpraxis – insbesondere, da ZEITRISS 4.x aktiv weiterentwickelt wird.

**Versionskennung in Save-Dateien:** Ab Version 4.0.3 wird bei jedem Speichervorgang automatisch ein
**"version"**-Feld in die JSON-Datei geschrieben, z. B. *"version": "4.0.3"*. Bei späteren Modulen
oder Regelupdates erhöht sich diese Nummer entsprechend (etwa auf *4.1* für ein größeres Modul-
Update). Die Codex-Software prüft beim Laden eines Spielstands dieses Feld und kann so
**automatisch** erkennen, ob der Spielstand aus einer älteren Version stammt. Stimmen
Hauptversionsnummern überein (z. B. 4.0 zu 4.1), sind die meisten Änderungen **vorwärtskompatibel**
– d.h. der Codex lädt den Stand und **aktualisiert im Hintergrund** die nötigen Datenstrukturen.
Kleinere Versionssprünge innerhalb von 4.x sind in der Regel unproblematisch und erfordern höchstens
das Einfügen neuer Felder mit Standardwerten.

**Beispiel – versionskompatibler Spielstand:** *Angenommen, in Version 4.1 wird ein neues Attribut
***“Mentalstabilität”*** eingeführt, das in 4.0 noch nicht existiert. Ihr habt einen Kampagnen-
Spielstand aus Version 4.0.2. Ladet ihr diesen in der aktualisierten Anwendung, erkennt der Codex
anhand *"version": "4.0.2"*, dass ***Mentalstabilität*** fehlt. Beim Konvertieren des Standes auf
4.1 wird automatisch das Feld *"mentalstabilität": 100* (als Start- oder Standardwert) ergänzt. Eure
Chrononauten erhalten also rückwirkend einen vollen Mentalstabilitätswert, den ihr im Spiel dann
weiter verwenden könnt. Andere 4.1-Regeländerungen – etwa geänderte Fertigkeitslisten oder neue
Inventargegenstände – werden ähnlich gehandhabt: Der Codex passt den Spielstand datenbankseitig an,
ohne dass eure gespeicherten Fortschritte verloren gehen.* Auf diese Weise könnt ihr **nahtlos** mit
euren bestehenden Charakteren und Kampagnen weiterzuspielen, selbst wenn zwischendurch
Regeländerungen stattfinden.

Bei **größeren Versionssprüngen** (etwa einem Wechsel von 4.x auf 5.0 in ferner Zukunft) könnte es
Inkompatibilitäten geben, aber für diesen Fall ist vorgesorgt: Der Codex würde dann beim Laden eine
Warnung ausgeben und – sofern möglich – ein **Migrationsskript** anbieten, das die wichtigsten Daten
in die neue Edition überführt. Solche größeren Updates werden natürlich ausführlich dokumentiert.
Für den Alltag in ZEITRISS 4.0 aber gilt: Dank der Versionskennzeichnung könnt ihr unbesorgt updaten
und euch auf neue Module stürzen, ohne Angst um eure mühsam erspielten Speicherstände haben zu
müssen. Jede Mission, jede Entscheidung eurer Chrononauten bleibt erhalten und wird im Lichte neuer
Regeln konsistent weitergeführt.

**Tipp:** Es lohnt sich dennoch, **Backups** eurer Spielstände anzulegen, bevor ihr ein größeres
Update einspielt – einfach um auf Nummer sicher zu gehen. Bisherige Erfahrungen zeigen jedoch, dass
das versionierte Speichersystem äußerst zuverlässig ist. Somit könnt ihr euch voll und ganz auf das
inhaltliche Abenteuer konzentrieren, während die Technik im Hintergrund für Kontinuität sorgt.

**Nightly Auto-Save:** Nach jeder Missionsphase legt der Codex automatisch einen Sicherungsstand an.
So geht selbst bei Unterbrechungen oder spontanen Pausen kein Fortschritt verloren.

## Cineastische Schlachten: Erfolgspools, Spotlight-Szenen & heroische Würfe

Chrononauten erleben nicht nur Einzelkämpfe und kleine Scharmützel, sondern geraten mitunter mitten
in die großen Konflikte der Geschichte – offene Feldschlachten, städtische Aufstände oder sogar
temporale Kriege, in denen Armeen verschiedener Epochen aufeinanderprallen. Anstatt solche
Massengefechte umständlich **für jeden Gegner einzeln** auszuwürfeln, bietet ZEITRISS mit den
folgenden Regeln eine **cineastische Alternative** an, die große Schlachten abstrahiert und dennoch
den Held\*innen erlaubt, das Blatt entscheidend zu wenden. Die Devise lautet: **Filmreife Action**
mit klarem Fokus auf den Taten der Chrononauten.

**Grundprinzip – Waagschalen-System:** Stellt euch den Verlauf einer Schlacht wie eine Waage mit
zwei Seiten vor: **Seite A** repräsentiert die Verbündeten der Helden, **Seite B** die Gegenseite.
Beide Seiten beginnen in der Regel ausgeglichen oder gemäß der Story-Vorgabe leicht zugunsten einer
Seite. Durch ihre **Schlüsselaktionen** können die Spielercharaktere nun das Gewicht zu Gunsten von
A oder B verschieben. Jede erfolgreiche **Helden-Aktion** legt sprichwörtlich ein Gewicht auf die
Waagschale von Seite A (Erfolgspunkt für die Heldenseite). Gelingt den Gegnern ein bedeutender Coup
– oder versäumen die Helden eine wichtige Gelegenheit – erhält Seite B einen Erfolgspunkt (oder ein
bereits erzielter Punkt für A wird neutralisiert). Am Ende des Konflikts werden die
**Erfolgspunkte** beider Seiten verglichen:

- **A \> B:** Die Heldenseite überwiegt – die Schlacht wird **gewonnen**. Positive Konsequenzen
treten ein (der Feind zieht sich zurück, die Mission der Helden gelingt, etc.).
- **A \< B:** Die Gegner haben mehr Punkte – die Schlacht geht **verloren**. Entsprechend treten
negative Folgen ein (die Helden müssen sich zurückziehen, wichtige Ziele gehen verloren, die
feindliche Agenda setzt sich durch).
- **A = B:** Ein **Patt** – keine Seite hat klar gewonnen. Dies kann einen zähen Stillstand bedeuten
oder einen Pyrrhussieg, bei dem zwar der Gegner gestoppt wird, aber zu hohem Preis. Die SL
entscheidet nach dramaturgischem Bedarf, wie ein Unentschieden interpretiert wird – evtl. bricht
eine dritte Partei den Gleichstand, oder beide Seiten ziehen sich erschöpft zurück.

**Wichtig:** Die Spielercharaktere sind das **Zünglein an der Waage**. Auch wenn Hunderte um sie
herum kämpfen, bilden die Heldentaten der Chrononauten den entscheidenden Unterschied. Die große
Schlacht tobt lediglich als spektakuläre **Kulisse** im Hintergrund – beschreibt Kanonendonner,
Schlachtrufe, Chaos überall – doch das **Spielleiter-Narrativ** bleibt auf die Aktionen der Helden
fokussiert. So fühlen sich die Spieler nie als Statisten im Weltgeschehen, sondern immer als
zentrale Akteure, deren Entscheidungen den Verlauf der Geschichte prägen.

**Ablauf einer cineastischen Schlacht:** Um eine Massenschlacht nach diesem System abzuwickeln, geht
ihr in mehreren Phasen vor:

- **Szene vorbereiten:** Die SL definiert ein **Szenario** und überlegt sich ein paar
**Schlüsselszenen**, in denen die Helden eingreifen können. Jede Schlüsselszene ist eine konkrete
Aufgabe oder Herausforderung innerhalb der Schlacht, die das Blatt wenden könnte. *Beispiele:* In
der **Schlacht von Hastings** könnten die Helden (a) eine strategisch wichtige Brücke halten, (b)
den feindlichen Anführer im Duell ausschalten oder (c) die Moral der erschöpften Verbündeten durch
eine flammende Rede stärken. Jede dieser Aufgaben wird als eigene Szene im Spiel ausgespielt.
- **Einfluss der Aktionen:** Spielt nun jede dieser Schlüsselszenen mit den normalen Regeln aus –
sei es im Kampf, durch Schleichen, taktisches Geschick oder Diplomatie, je nach Art der Aufgabe.
Gelingt den Helden die jeweilige Aktion, erhalten sie **1 Erfolgspunkt** für Seite A. Misslingt
etwas gravierend oder ignorieren die Helden eine Chance, bekommt Seite B einen Punkt (oder ein
bereits erzielter A-Punkt wird wieder abgezogen, wenn das plausibler scheint). Wichtig ist hier ein
bisschen Fingerspitzengefühl der SL: Nicht jeder kleine Misserfolg der Helden sollte direkt einen
Punkt für B geben – es geht um *entscheidende* Wendungen.
- **Zwischenergebnisse einflechten:** Nach jeder Schlüsselszene skizziert die SL kurz, **wie der
Schlachtenverlauf sich entsprechend verändert**. So bleibt das Geschehen dynamisch und die Spieler
sehen direkt die Auswirkungen ihrer Taten. *Beispiel:* Haben die Helden die Brücke erfolgreich
gehalten (+1 für A), gewinnen ihre Verbündeten Zeit und einen taktischen Vorteil – vielleicht ziehen
sich die Feinde kurz zurück, oder ein geplanter Flankenangriff misslingt dem Gegner. Scheitern die
Helden später dabei, den feindlichen Champion aufzuhalten (Punkt an B), kippt das Blatt wieder: Die
gegnerischen Truppen schöpfen neue Moral, da ihr Champion wütet, und drücken die Verbündeten zurück.
Solche eingestreuten Schilderungen machen deutlich, wie **flexibel** das Gefüge ist und dass die
Helden wirklich etwas bewegen.
- **Finale & Vergleich:** Sobald alle geplanten Schlüsselszenen gespielt sind (oder die Helden aus
Zeitmangel nicht mehr eingreifen können), kommt es zum **Finale**. Vergleicht die auf A und B
angesammelten Erfolgspunkte und bestimmt das **Endergebnis** der Schlacht gemäß dem Waagschalen-
Prinzip (Sieg/Niederlage/Patt). Die SL beschreibt nun **cineastisch**, was geschieht: Haben die
Helden genug Impact erzielt, bricht vielleicht die feindliche Armee panisch auseinander, der
gegnerische Kommandant ergibt sich oder die Allianz der Helden feiert einen hart erkämpften Triumph.
Haben die Punkte nicht gereicht, tritt das düsterere Szenario ein – vielleicht werden die Helden zur
Rückzugsordnung gezwungen, während der Feind sein grausames Werk vollendet. Wichtig ist, dass das
Ende **logisch** aus den Erfolgspunkten und der Story hervorgeht, aber dennoch Raum für
Überraschungen lässt.
- **Nachspiel:** Jede Schlacht, ob gewonnen oder verloren, hat Konsequenzen. Nehmt euch als SL Zeit,
das **Nachspiel** auszuleuchten. Welche langfristigen Folgen hat der Ausgang für die Kampagne?
Wurden wichtige Personen gerettet oder getötet? Hat ein Sieg vielleicht neue Probleme geschaffen
(z. B. Machtvakuum, Racheakte der Verlierer) oder bedeutet eine Niederlage einen dramatischen
Wendepunkt für die Helden? Indem ihr die Nachwirkungen beschreibt, verleiht ihr den zuvor abstrakten
Erfolgspunkten echtes **Gewicht**. Die Spieler spüren, dass ihre Anstrengungen die Geschichte
beeinflusst haben – im Guten wie im Schlechten.

**Heroische Schlüsselwürfe:** In cineastischen Schlachten kulminieren viele Schlüsselszenen in
**einem entscheidenden Wurf** – dem Schlag gegen den feindlichen Kriegsherrn, der Charisma-Probe bei
der Ansprache an die Truppen, der Hack des Schutzschilds zur rechten Zeit. Diese Würfe solltet ihr
besonders dramatisch inszenieren. Die *Heldenwürfel*-Regel und *Exploding Dice* kommen hier voll zur
Geltung: Wenn je ein Zeitpunkt für explodierende Ergebnisse oder Vorteilwürfe gegeben ist, dann in
diesen **Schlüsselmomenten**. Ermutigt die Spieler, alle Register zu ziehen (Chrono-Energie,
Ausrüstung, Teamwork), um den Wurf zu beeinflussen – denn vom Gelingen hängt oft das Schicksal der
gesamten Schlacht ab. Gleichzeitig dürfen Fehlschläge nicht antiklimaktisch sein: Selbst wenn der
entscheidende Wurf misslingt, sollte die daraus entstehende Wendung erzählerisch spannend bleiben
(z. B. erscheint im letzten Moment doch noch Verstärkung der Gegner, oder der Held erzielt zwar
keinen perfekten Erfolg, rettet aber zumindest einige Verbündete vor dem Schlimmsten).
**Cineastisch** bedeutet nicht, dass immer alles gut ausgeht – sondern dass es immer spektakulär und
bedeutsam für die Story ist.

**Hinweis:** Dieses cineastische Schlachtensystem lässt sich nicht nur für militärische Konflikte
verwenden, sondern ebenso für **soziale Umwälzungen, Wettstreite oder Katastrophenszenarien**. Man
denke an Revolutionen, in denen nicht Armeen, sondern Ideen gegeneinanderstehen – auch dort können
Erfolgspools gesammelt werden (z. B. Einfluss gewinnen vs. verlieren). Oder an ein Hacker-Duell in
der Cyberzeit, wo zwei KI-Netzwerke ringen und die Helden durch ihre Eingriffe Erfolgspunkte für die
jeweilige Seite sammeln. Passt die Art der Schlüsselszenen einfach dem Thema an: In einer
politischen Krise könnten es Debatten, Enthüllungen oder Sabotageakte sein, die den Ausschlag geben.
Die Mechanik bleibt gleich – nur das *Flair* ändert sich. Wichtig ist, die Grautöne zu beachten:
Gerade in sozialen Konflikten gibt es nicht immer strahlende Sieger. Die SL sollte die Ergebnisse
ggf. mit moralischer Vielschichtigkeit darstellen (z. B. bringt ein Sieg der Revolution zwar
Freiheit, aber auch Chaos; eine Niederlage der Helden bewahrt kurzfristig den Frieden, lässt aber
Unterdrückung bestehen usw.). So bleibt das Spiel tiefgründig und der **Zeitreise-Aspekt** – mit all
seinen Paradoxien – wird gekonnt in Szene gesetzt.

Mit diesen Erweiterungen – von explodierenden Würfeln über Heldenwürfel und HUD-Alerts bis hin zu
cineastischen Schlachten und versionierten Speicherständen – erhält ZEITRISS 4.0 einen weiteren
Feinschliff. Spielrunden können nun noch flexibler entscheiden, welchen **Ton** sie anschlagen
wollen: Knallhart taktisch, filmisch-überdreht oder eine balancierte Mischung. Alle neuen
Modulelemente fügen sich nahtlos ins existierende Regelwerk ein. Nutzt diejenigen, die eure Kampagne
bereichern, und passt sie an euren Stil an. Ob eine unwahrscheinliche Würfelkette den Tag rettet,
der Codex mit Warnmeldungen das Team vor dem Schlimmsten bewahrt oder die Chrononauten in einer
gewaltigen Schlacht Geschichte schreiben – das Wichtigste ist, dass eure ZEITRISS-Runde
unvergessliche gemeinsame Abenteuer erlebt. In diesem Sinne: *Würfel bereit, HUD kalibriert – und
Film ab!*

## Cheat-Cards: Kompakte Referenz

Diese Tabellen passen auf eine A6-Karte oder ins HUD.

### Erfolgsschwellen (W6)

| Schwierigkeit | Schwelle |
| --- | --- |
| leicht | 4 |
| mittel | 7 |
| schwer | 10 |

### Beispielsprünge

| Schwierigkeit | Beispiel |
| --- | --- |
| 4 | Sprung über eine kleine Lücke |
| 7 | Hacken eines gesicherten Terminals |
| 10 | Deaktivierung eines Zeitbomben-Prototyps |

### Paradox-Level

| Stufe | Effekt |
| --- | --- |
| 0–1 | Stabil |
| 2 | Funk-Schwankung |
| 3 | Leuchtende Staubfäden |
| 4 | Kurz-Echo (1 s Nachzieher) |
| 5 | ClusterCreate() im HQ |

### Seed-Counter im HUD

Sobald Paradox-Level **5** erreicht ist, legt das HQ automatisch 1–2 Rifts an.
Der Counter zeigt die offenen Seeds an und beeinflusst Schwellen sowie CU-Multiplikator:

| Offene Seeds | Probe-Schwelle + | CU-Belohnung × |
| ------------ | ---------------- | -------------- |
| 0 | 0 | 1.0 |
| 1 | +1 | 1.2 |
| 2 | +2 | 1.4 |

*Im HUD erscheint z.B. `[Seeds 1 | Para 5]`.* Die Schwelle jeder Mission –
ob Haupteinsatz oder Rift – nutzt diese Werte und sinkt sofort, sobald
ein Seed verschwindet.

### Standard-Ausrüstungsslots

- 1 Hauptwaffe
- 1 Zweitwaffe
- 2 Hilfsgeräte
- 1 Spezialobjekt
