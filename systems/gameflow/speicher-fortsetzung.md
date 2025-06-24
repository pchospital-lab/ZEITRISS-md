---
title: "ZEITRISS 4.0 – Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)"
version: 4.0
tags: [systems]
---

# ZEITRISS 4.0 – Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)

- Einführung und Zielsetzung
- Einzelspieler-Speicherstände – Bewährte Logik beibehalten
- Gruppen-Spielstände – Neue Unterstützung für Teams
- Zeitlinien-Tracker und Paradoxon-Index
- Immersiver Ladevorgang: Rückblenden und Anschluss in der Erzählung
- Umgang mit fehlerhaften oder abweichenden Speicherständen
- Spielleitung bleibt in-world (Immersion der Spielleitung)
- Praxis-Beispiele für Speicherblöcke (Solo & Gruppe)
- Fazit

## Einführung und Zielsetzung

Das Speicherstand- und Fortsetzungssystem von **ZEITRISS 4.0** wird in Modul 12 vollständig
überarbeitet. Ziel ist es, eine klare, GPT-kompatible Speicher- und Fortsetzungsmechanik zu
gewährleisten, die langfristiges Spielen mit einer hohen Spielerzahl unterstützt – **ohne die
Immersion zu beeinträchtigen**. Die grundlegende **Save/Load-Logik** bleibt erhalten, wird aber
durch neue Funktionen erweitert. Entwickler:innen erhalten damit ein robustes, transparentes und
flexibles Speichersystem für Einzel- und Gruppenspiele mit GPT als Spielleitung.

**Wichtige Schwerpunkte der Überarbeitung sind unter anderem:**

- **Integration eines Zeitlinien-Trackers & Paradoxon-Index:** Jede Veränderung der historischen
  Zeitlinie wird im Speicher protokolliert (mit ID, Epoche, Beschreibung der Abweichung und einem
  Stabilitätswert von 3 bis 0). Sinkt die Stabilität eines Ereignisses auf 0, erhöht sich automatisch
  ein Paradoxon-Wert um +1.
- **Trennung von Einzelspieler- und Gruppen-Spielständen:** Klare Definition, wie Einzelcharakter-
  Speicherstände vs. Gruppenspielstände aufgebaut und gehandhabt werden.
- **Standardisiertes, maschinenlesbares Format (JSON) mit narrativer Einbettung:** Einführung eines
  einheitlichen Formats mit allen notwendigen Feldern (Name, Attribute, EP, Talente, Inventar, Codex-
  Wissen etc.), damit der KI-Spielleiter (GPT) die Daten fehlerfrei einlesen kann. Das Format wird
  **In-World** präsentiert (etwa als Codex-Archiv), sodass die Technik für Spieler unsichtbar bleibt.
- **Integration des Gruppen-Spielsystems:** Mechaniken zum Import vorhandener Einzelcharaktere in
  eine Gruppe, Export einzelner Gruppenmitglieder sowie nahtloses Hinzufügen oder Entfernen von
  Spielern aus laufenden Gruppen.
- **Fortsetzungs-Logik für GPT:** Formatregeln sorgen dafür, dass GPT den Speicherblock bei jedem
  Laden sicher erkennt, korrekt interpretiert und die Geschichte konsistent fortsetzt.
- **Automatische Rückblenden & Anschluss an vorherige Mission:** Ingame-Mechanismen (Logbuch, Déjà-
  vu, Codex-Archiv) ermöglichen eine kurze Zusammenfassung der letzten Ereignisse – jetzt auch aus
  Sicht aller Gruppenmitglieder – beim Laden eines Spielstands, um den Übergang in die neue Mission
  atmosphärisch zu gestalten.
- **Umgang mit fehlerhaften Speicherständen:** Richtlinien dafür, wie die KI-Spielleitung auf
  abweichende oder beschädigte Savegames reagieren kann (etwa durch korrigierende Vorschläge oder
  Ingame-Nachfragen) – ohne die Immersion zu brechen.
- **In-World-Spielleitung:** Die Spielleitung durch GPT bleibt vollständig in der Spielwelt
  verankert. Sämtliche Erklärungen zum Laden/Speichern erfolgen durch Ingame-Elemente (z.B. den Codex,
  NSCs oder ein „Nullzeit-Log“) und nicht als außenstehende Systemkommentare.
- **Beispiel-Speicherblöcke:** Bereitstellung von kommentierten Beispielen für typische
  Speicherstände (sowohl Solo- als auch Gruppen-Spielstände) im standardisierten Format, die als
  Vorlage dienen können.
- **Token-Lite-Modus:** Missionslog mit max. 15 Einträgen. Archivierte Rifts lassen sich auslagern, um Token zu sparen.

Im Folgenden werden diese Punkte im Detail ausgeführt und das neue System erläutert.

## Einzelspieler-Speicherstände – Bewährte Logik beibehalten

Für **Einzelspieler-Runden** (ein Chrononaut als Spielercharakter) bleibt die bisherige
Speichermechanik im Kern bestehen. Am Ende jeder Mission erzeugt das Spiel einen maschinell lesbaren
**Speicherblock** – idealerweise als strukturierten JSON-Code im Chat (z.B. in einem Code-Feld) oder
als separate Datei. Entscheidend ist, dass das Format einheitlich und klar lesbar ist, sowohl für
Menschen als auch für das KI-Modell. Dadurch erkennt GPT zuverlässig, dass es sich um einen
Spielstand handelt, und kann alle relevanten Daten übernehmen, sobald der Speicherstand in eine neue
Spielsitzung geladen wird.

**Struktur und Inhalt eines Einzel-Speicherstands:** Der Speicherstand wird als zusammenhängender
Datenblock (z.B. in einem Code-Feld) dargestellt. Er enthält die wichtigsten Charakterdaten in
**beschreibender, narrativ eingebetteter Form**, aber **keine versteckten Befehle** oder unklare
Formulierungen. Alles ist neutral in der dritten Person gehalten, damit GPT es problemlos
interpretieren kann. Typische Felder eines Speicherstands sind unter anderem:

- **Grunddaten:** Name des Charakters, Herkunftsepoche (Zeit/Hintergrund), Level und
  Erfahrungspunkte (EP) bzw. Fortschritt.
- **Attribute:** Werte für Stärke, Geschicklichkeit, Intelligenz, Charisma etc. (inklusive
  Spezialattribute wie _Temporale Affinität_ oder _Systemlast_ für Chrononauten).
- **Fähigkeiten und Talente:** Eine Liste besonderer Talente, Fertigkeiten oder Ausbildungen der
  Figur.
- **Ausrüstung:** Inventarlisten, ggf. inklusive besonderer Gegenstände, Implantate, psionischer
  Fähigkeiten etc.
- **Charakterprofil:** Besondere Merkmale wie moralische Ausrichtung, Ruf oder Zugehörigkeiten (z.B.
  _„altruistisch“_, Rang im ITI, Beziehungen zu Fraktionen).
- **Errungenschaften:** Wichtige Erfolge aus vergangenen Missionen.
- **Codex-Wissen:** Relevantes Wissen, das der Charakter im Codex gespeichert hat – z.B.
  Erkenntnisse aus vergangenen Missionen, enthüllte Geheimnisse, bekannte NPCs oder historische
  Fakten, an die er sich erinnert.
- **Statistiken (optional):** Dinge wie absolvierte Missionen, gelöste Rätsel, besiegte Gegner usw.,
  falls für den Spielfortschritt von Belang.
- **Zeitlinien-Veränderungen (optional):** Wichtige Abweichungen im historischen Verlauf, die durch
  die Aktionen des Charakters verursacht wurden, inklusive Angabe eines Stabilitätsgrads der Änderung
  (siehe _Zeitlinien-Tracker_ weiter unten).

Nicht im Speicherstand enthalten sind in der Regel detailreiche Situationsbeschreibungen oder
komplette Dialogverläufe vergangener Missionen. Der Speicherstand soll **kompakt** bleiben –
ausreichend, um den Charakter konsistent weiterzuspielen, aber ohne den neuen Missionskontext mit
irrelevanten Altlasten zu überfrachten. Jede neue Mission beginnt erzählerisch „frisch“, und der
Spielstand liefert nur die nötigsten Zusammenfassungen der Vorgeschichte. So bleibt der Chat-Kontext
schlank, und GPT kann die Fortsetzung konsistent gestalten, ohne durch Rauschen alter Dialoge
verwirrt zu werden.

**Beispiel: JSON-Speicherstand für einen einzelnen Charakter.** Angenommen, Agent Alex hat Mission 1
abgeschlossen. Sein Speicherstand könnte folgendermaßen aussehen:

_{_

_"Name": "Alex",_

_"Epoche": "Gegenwart (2025)",_

_"Level": 2,_

_"version_hash": "4.0",_
_"arc_dashboard": {_
_"offene_seeds": [],_
_"fraktionen": {},_
_"fragen": []_
_},_

_"Erfahrung": 15,_

_"Attribute": {_

_"Stärke": 4,_

_"Geschicklichkeit": 5,_

_"Intelligenz": 5,_

_"Charisma": 3,_

_"Temporale Affinität": 4,_

_"Systemlast": 3_

_},_

_"Talente": \["Pistolenschütze", "Kryptographie"\],_

_"Implantate": \["Neuro-Link (Kommunikationsimplantat, Systemlast 1)"\],_

_"Psionik": \[\],_

_"Moral": "überwiegend altruistisch",_

_"Ruf": "Angesehener Agent im ITI; unbekannt bei externen Fraktionen",_

_"Inventar": \[_

_"Dietrich-Set (+1 auf Schlösser knacken)",_

_"Heiltrank (stellt 5 LP her)",_

_"Zeitscanner-Tablet (funktioniert nur in High-Tech-Umgebungen)"_

_\],_

_"Errungenschaften": \["Retter von Aquitanien"\],_

_"Codex": \[_

_"Kennt den wahren Ablauf der Schlacht von Aquitanien 1356",_

_"Weiß von der Existenz des Chronomanten Moros"_

_\],_

_"Statistik": {_

_"Absolvierte Missionen": 1,_

_"Gelöste Rätsel": 2,_

_"Besiegte Gegner": 3_

_}_

_}_

_Erläuterung:_ In diesem Speicherblock sind alle zentralen Daten von Alex nach seiner ersten Mission enthalten.
Zum Beispiel hat er das Talent _Kryptographie_, besitzt ein Neuro-Link-Implantat,
ein Inventar mit

Gegenständen (Dietrich-Set, Heiltrank, Zeitscanner-Tablet)
und im **Codex** stehen Einträge, die an
seine Erlebnisse aus einer Anfangsmission erinnern (Schlacht von Aquitanien 1356 etc.). Diese Informationen
reichen aus, um Alex in einer zukünftigen Mission konsistent weiterzuspielen. GPT kann daraus
entnehmen, **wer Alex ist, was er kann und was er erlebt hat**, ohne dass jedes Detail der ersten
Mission erneut im Prompt geladen werden muss.

Bestehende Einzelspieler-Spielstände aus früheren Versionen behalten dieses Format bei und
funktionieren weiterhin unverändert. Wer also bisher Solo-Abenteuer mit ZEITRISS gespielt hat, muss
nichts an alten Savegames ändern – sie können in ZEITRISS 4.0 direkt weitergenutzt werden.

## Gruppen-Spielstände – Neue Unterstützung für Teams

**Neu** im aktualisierten System ist die offizielle Unterstützung von **Gruppen-Spielständen**. Ein
einzelner Speicherblock kann nun mehrere Spielercharaktere umfassen. Dadurch lassen sich Gruppen von
Chrononauten gemeinsam speichern und laden, ohne die etablierte Einzelspieler-Mechanik zu stören.
Die bereits bekannte Datenstruktur eines Charakter-Datensatzes bleibt dabei erhalten und wird
lediglich erweitert: Statt eines einzelnen Charakter-Objekts können nun mehrere solcher Objekte im
Speicher vorhanden sein.

### Struktur eines Gruppen-Speicherstands

Um mehrere Charaktere in einem Savegame abzubilden, gibt es zwei naheliegende Ansätze im JSON-
Format:

- **Array von Charakterobjekten:** Der Speicherblock besteht aus einer Liste _\[...\]_, in der jedes
  Element ein vollständiges Charakter-Datenobjekt (wie oben beschrieben) ist.
- **Wrapper-Objekt mit Charakterliste:** Der Speicherblock ist ein JSON-Objekt mit einem Feld (z.B.
  _"Charaktere"_ oder _"Gruppe"_), das eine Liste aller Charakterobjekte enthält. Optional kann dieses
  Objekt zusätzliche gruppenweite Felder wie einen Gruppennamen enthalten.

Beide Varianten sind technisch handhabbar. Wichtig ist vor allem, dass GPT zuverlässig erkennt, dass
mehrere Charaktere vorliegen. Aus Gründen der Klarheit verwenden wir im Folgenden einen Wrapper-
Ansatz: ein JSON-Objekt mit dem Feld _"Charaktere"_, das eine Liste von Charakteren enthält, sowie
optional ein Feld für den **Gruppennamen**.

**Beispiel: JSON-Gruppenspielstand mit zwei Charakteren.** Angenommen, zwei Spieler (oder ein
Spieler mit zwei aktiven Charakteren) möchten ihre Figuren Alex und Mia gemeinsam als Team
speichern. Ein Gruppen-Spielstand im JSON-Format könnte so aussehen:

_{_

_"Gruppe": "Team Chronos",_

_"version_hash": "4.0",_
_"arc_dashboard": {_
_"offene_seeds": [],_
_"fraktionen": {},_
_"fragen": []_
},_

_"Charaktere": \[_

_{_

_"Name": "Alex",_

_"Epoche": "Gegenwart (2025)",_

_"Level": 2,_

_"Erfahrung": 15,_

_"...": "..." /\* weitere Felder wie oben für Alex \*/_

_},_

_{_

_"Name": "Mia",_

_"Epoche": "Victorianisches Zeitalter (1888)",_

_"Level": 1,_

_"Erfahrung": 5,_

_"...": "..." /\* weitere Felder wie oben für Mia \*/_

_}_

_\]_

_}_

Hier besteht das Agenten-Team **“Team Chronos”** aus zwei Mitgliedern: Alex und Mia. Jeder Charakter
wird als separates Objekt mit all seinen Datenfeldern aufgeführt (der Übersicht halber sind oben
nicht alle Felder ausgeschrieben, aber in einem echten Save würden analog zu Alex auch Mias
Attribute, Talente, Inventar etc. vollständig aufgeführt sein). Das optionale Feld _"Gruppe"_ dient
als Teamname oder Identifikator der Gruppe. Es ist _nicht zwingend erforderlich_ – die Präsenz
mehrerer Objekte in _"Charaktere"_ signalisiert GPT bereits, dass es sich um einen Gruppen-
Spielstand handelt. Dennoch kann ein Gruppenname atmosphärisch hilfreich sein und vom Spielleiter in
Dialogen verwendet werden (z.B. _„Agententeam Chronos...“_).

Entscheidend ist: Die **Struktur pro Charakter bleibt identisch** zu einem Einzelspieler-
Speicherstand. Es gehen also keine Datenfelder verloren und es werden keine neuen speziellen Formate
pro Charakter erfunden – wir haben lediglich eine zusätzliche Ebene drumherum gesetzt, um mehrere
Datensätze zusammenzuhalten. Somit ist auch die **Abwärtskompatibilität** gegeben: Ein Einzel-
Charakter-Save sieht für GPT praktisch genauso aus wie ein Gruppen-Save, nur ohne die äußere Liste.

### Erkennung von Einzel- vs. Gruppen-Spielständen

Der KI-Spielleiter (GPT) muss sofort erkennen können, ob ein geladener Speicherblock einen einzelnen
Charakter enthält oder eine Gruppe. Diese Unterscheidung erfolgt **allein durch die JSON-Struktur**:

- **Einzelspieler-Speicherstand:** Besteht typischerweise aus **einem einzigen JSON-Objekt** mit
  Charakterdaten – kein äußerer Array und kein _"Charaktere"_-Feld. Auf oberster Ebene steht z.B.
  direkt _"Name": "Alex"_. GPT liest diese Struktur und sieht nur einen Charaktereintrag – damit ist
  klar, dass es sich um einen Solo-Spielstand handelt. _Beispiel:_ _{ "Name": "Alex", "Level": 2, ...
  }_ – kein Array, keine weiteren Objekte auf Top-Level außer diesem einen Charakter →
  **Einzelcharakter-Save**.
- **Gruppen-Speicherstand:** Erkennbar an **mehreren Charakterdatensätzen** in einem Container. Das
  kann eine JSON-Liste _\[ {...}, {...} \]_ sein oder ein Objekt mit einem Feld _"Charaktere"_ (bzw.
  analog), welches ein Array enthält. Sobald GPT mehr als ein Charakterobjekt findet, ist klar: Dieser
  Spielstand umfasst mehrere Figuren. Ein optionales Feld _"Gruppe"_/_"Team"_ kann die Gruppennatur
  untermauern, wird aber zur reinen Erkennung nicht benötigt. _Beispiel:_ _{ "Charaktere": \[
  {Char1-Daten}, {Char2-Daten} \] }_ – mehrere Objekte im Array → **Gruppen-Save**.

Im Klartext prüft GPT beim Laden eines Spielstands einfach die oberste Struktur: Ein einzelnes
Datenobjekt bedeutet Solo-Spiel; eine Liste oder ein _"Charaktere"_-Feld mit mehreren Objekten
bedeutet Gruppe. Diese Prüfung ist trivial und benötigt keine extra Kennzeichnung, solange wir das
Format konsequent einhalten.

### Eindeutige Identifikation von Charakteren (Metadaten)

Wenn mehrere Charaktere in einem Savegame enthalten sind, kann es hilfreich sein, jeden Eintrag mit
einer eindeutigen **ID** oder ähnlichen Metadaten zu versehen. Dies dient der robusten
Identifikation, insbesondere falls Charaktere ähnliche Namen haben oder sich über die Zeit ändern.
Ein optionales Feld wie _"ID"_ pro Charakter kann z.B. eine eindeutige Kennung (UUID oder ein
anderer einmaliger Code) enthalten.

_Beispiel eines Charakters mit ID:_

_{_

_"Name": "Alex",_

_"ID": "CHR-7f3a9b2e",_

_"Epoche": "Gegenwart (2025)",_

_..._

_}_

In einem Gruppenstand hätte dann jeder Charaktereintrag seine eigene ID. **Wozu das?** Bei der
Zusammenführung mehrerer Speicherstände oder dem späteren Aktualisieren einzelner Charaktere
innerhalb einer Gruppe kann GPT anhand der ID erkennen, ob ein Charakter bereits existiert oder neu
hinzukommt. So werden Duplikate vermieden:

- **Mit ID:** Lädt man einen neuen Speicherstand von Alex in eine bestehende Gruppe, in der Alex mit
  gleicher ID schon existiert, weiß das System, dass es **denselben Charakter** updaten soll (anstatt
  einen zweiten „Alex“ hinzuzufügen). Gleiches gilt beim erneuten Laden eines fortgeschrittenen
  Savegames: Die ID signalisiert GPT, welcher bestehende Gruppencharakter aktualisiert werden muss.
- **Ohne ID:** Versucht GPT, Charaktere anhand von Name + Epoche o. ä. zu unterscheiden. Das kann in
  vielen Fällen funktionieren, ist aber fehleranfälliger (z.B. könnten zwei Spieler zufällig beide
einen Charakter namens „Alex“ spielen, oder ein Charakter ändert seinen Decknamen zwischenzeitlich).

#### Konfliktfall ohne ID

Treffen zwei Einträge ohne ID aufeinander und stimmen **Name** sowie
**Epoche** überein, fragt das System nach. Entweder wird eine neue ID vergeben
oder der vorhandene Datensatz bewusst überschrieben. Auf diese Weise lassen sich
Duplikate vermeiden, ohne dass IDs zwingend erforderlich sind.

Eine technische UUID als ID ist daher **empfehlenswert** für langfristige, große Kampagnen, aber das
Feld bleibt optional. Das System funktioniert auch ohne – es verlässt sich dann ganz auf die
eindeutigen Namen oder Konstellationen. (In unseren obigen Beispielen haben wir der Einfachheit
halber keine IDs angegeben, um die Darstellung nicht zu verkomplizieren; in der Praxis könnte man
sie jedoch hinzufügen, um maximale Eindeutigkeit zu erzielen.)

### Laden und Zusammenführen von Speicherständen

Beim Laden eines Speicherstands in den Chat-Kontext – sei es zu Beginn einer neuen Spielsession oder
mitten im Spiel – folgt GPT je nach Art des Savegames unterschiedlichen Pfaden. Wichtig ist, dass
dieser Übergang reibungslos und narrativ sauber abläuft. **Je nach Situation passiert Folgendes:**

- **Solo-Spielstand laden (ein Charakter):** Wird ein einzelner Charakter-Speicherstand geladen
  (Format wie Alex im Beispiel oben), verfährt die Spielleitung wie gewohnt: GPT liest die
  Charakterdaten ein und setzt die Geschichte nahtlos mit **diesem einen Chrononauten** fort. Für den
  Spieler fühlt es sich an, als würde er genau dort weitermachen, wo er mit seinem Charakter aufgehört
  hat. Alle Werte, Inventargegenstände und Codex-Einträge aus dem Save stehen zur Verfügung, und die
  neue Mission kann mit dem bekannten Helden beginnen. _(Dieser Ablauf entspricht dem bisherigen
  Fortsetzungsprozess in ZEITRISS.)_
- **Von Solo zu Gruppe (Charaktere hinzufügen):** Neu ist die Möglichkeit, aus einem laufenden
  Einzelspiel eine Gruppe zu bilden, indem man einen weiteren Charakter hinzulädt. Das geht so: Man
  startet wie üblich mit dem bisherigen Solo-Charakter A (lädt also dessen Save). Anschließend fügt
  man zusätzlich den Speicherblock eines zweiten Charakters B in den Chat ein. GPT erkennt nun, dass
  zwei getrennte Datensätze vorliegen. Daraus resultiert automatisch ein **Gruppen-Spielstand**.
  Charakter B wird als neues Gruppenmitglied hinzugefügt, ohne Charakter A zu entfernen oder zu
  überschreiben. In der laufenden Geschichte taucht B dann z.B. als weiterer Agent auf, der sich dem
  Team anschließt. Charakter A behält all seine Daten und bleibt aktiv; Charakter B bringt seine
  eigenen Daten mit. Fortan führt GPT beide Charaktere gemeinsam in einem Gruppenstand weiter.
  _(Wichtig: Die Reihenfolge, in der man zusätzliche Charakter-Saves einfügt, spielt keine große Rolle
  – ob B gleich zu Anfang oder mitten in einer Mission dazukommt: GPT erkennt den neuen Datensatz und
  integriert B entsprechend ins Team.)_
- **Gruppenstart (mehrere Charaktere gemeinsam laden):** Es ist ebenso möglich, **von Anfang an**
  mehrere Speicherstände gleichzeitig zu laden – zum Beispiel wenn mehrere Spieler, die zuvor einzeln
  gespielt haben, nun zusammen eine Mission starten wollen. In diesem Fall werden die Savegame-Blöcke
  aller beteiligten Charaktere nacheinander (oder gesammelt) in den neuen Chat eingefügt. GPT
  konsolidiert diese Informationen automatisch zu **einem einzigen Gruppenstand**: Alle Charakterdaten
  bleiben jeweils separat vorhanden, bilden aber in der Spielwelt nun ein gemeinsames Team. GPT
  behandelt den zusammengeführten Speicherblock als eine Einheit, die alle nötigen Infos für die
  Gruppe enthält. Es ist also, als hätte GPT intern eine Liste aller aktiven Charaktere. Kein
  Charakter überschreibt einen anderen: Selbst wenn man mehrere JSON-Objekte unmittelbar
  hintereinander einfügt, werden sie nicht vermischt. GPT sieht mehrere Top-Level- Objekte bzw. Array-
  Elemente und erstellt intern eine Sammlung aller Charaktere. _(Reihenfolge egal: Ob man zuerst Alex,
  dann Mia lädt oder umgekehrt, spielt inhaltlich keine Rolle – am Ende zählt, dass GPT beide Einträge
  sieht. Sollte ein Charakter doppelt geladen werden (z.B. jemand fügt versehentlich denselben Save
  zweimal ein), würde GPT dank identischer Daten/ID erkennen, dass es sich um die gleiche Figur
  handelt, und keinen Klon erzeugen.)_
  Nach dem Zusammenführen der Spielstände setzt GPT den Paradoxon-Index sowie die Liste offener
  Rifts auf **0**, damit das Team mit einem sauberen Stand beginnen kann. Das optionale
  `startGroupMode()`-Snippet in `runtime-stub-routing-layer.md` zeigt diesen Reset exemplarisch.

**Zusammengefasst:** Ein einzelner Savegame-Block ergibt einen einzelnen Charakter; mehrere
Savegame-Blöcke (gleichzeitig oder sukzessive) ergeben die Bildung bzw. Erweiterung einer Gruppe.
GPT erkennt das automatisch anhand der Formatstruktur und passt sein Vorgehen entsprechend an –
**ohne** dass der Spielleiter außerhalb der Welt eingreifen muss.

### Hinzufügen, Aktualisieren und Entfernen von Gruppenmitgliedern

Sobald ein Spiel im Gruppenmodus läuft, gelten einfache **Regeln für den Umgang mit Gruppen-
Spielständen**, damit GPT als Spielleiter nichts durcheinanderbringt:

- **Neuen Charakter hinzufügen:** Jeder zusätzliche Charakter-Datensatz, der in der aktuellen Gruppe
  noch nicht vorhanden war, wird als neues Gruppenmitglied ergänzt. GPT erzeugt intern einen neuen
  Charaktereintrag und übernimmt alle Werte aus dessen Savegame. _Beispiel:_ Die Gruppe bestand bisher
  nur aus Alex. Nun wird Mias Speicherstand hinzugefügt. Mia (neuer Name/ID) wird von GPT als neues
  Mitglied erkannt. Ergebnis: Gruppe = \[Alex, Mia\]. Beide stehen mit ihren vollen Daten zur
  Verfügung.
- **Bestehenden Charakter aktualisieren:** Wird ein Speicherstand geladen, der zu einem Charakter
  gehört, der bereits in der Gruppe existiert, so werden dessen Daten **aktualisiert**, nicht
  dupliziert. Hier kommt das Metadaten-Feld (ID) ins Spiel: GPT vergleicht die IDs (falls vorhanden)
  oder ersatzweise Name/Epoche. Stimmen diese überein, nimmt es an, dass es derselbe Charakter ist.
  _Beispiel:_ In einer laufenden Gruppe aus Alex und Mia werden zu Beginn der nächsten Mission beide
  aktualisierten Savegames neu geladen. GPT erkennt an Alex’ ID oder Namen, dass Alex schon Teil der
  Gruppe ist – also wird **kein zweiter Alex** hinzugefügt, sondern Alex’ bestehender Eintrag mit den
  aktuellen Werten versehen (die ohnehin dem Save entsprechen). Genauso für Mia. Die Gruppe \[Alex,
  Mia\] bleibt bestehen, nur dass nun beide auf dem neuesten Stand sind.
- **Keine Konflikte durch unterschiedliche Felder:** Charaktere können unterschiedliche Felder oder
  Listen in ihren Daten haben, ohne Probleme zu verursachen. Hat Charakter A z.B. ein Feld _"Psionik":
  \[\]_ (weil er keine psionischen Fähigkeiten hat) und Charakter B gar kein Feld _"Psionik"_ (weil es
  für sie nie relevant war), führt das zu keinerlei Konflikt. GPT interpretiert einfach jeden
  Charakterblock für sich. Fehlt ein Feld bei einer Figur, bedeutet das nur, dass diese Figur dazu
  keine Angaben hat – es ist kein globales Problem. Es gibt also keine Fehlermeldung oder Störung,
  sondern jeder Charakterdatensatz wird individuell vollständig gelesen.
- **Optionale gemeinsame Elemente:** Das System ist primär so ausgelegt, dass jede Figur **getrennte
  Daten** hat. Falls gewünscht, kann man aber auch gruppenweite Felder definieren – etwa ein
  gemeinsames _"Gruppeninventar"_ oder einen aktuellen _"Missionsstatus"_, die außerhalb der einzelnen
  Charakterobjekte im JSON stehen. Solche Felder gelten dann für die **gesamte Gruppe**. GPT würde sie
  als von allen geteilt interpretieren. _Beispiel:_ Man könnte dem Gruppen-JSON ein Feld _"Mission":
  "Paris 1943 – Einsatzbeginn"_ auf oberster Ebene hinzufügen. GPT weiß dann, dass alle Charaktere
  sich zu Beginn von Mission X (hier Paris 1943) befinden. Solche globalen Felder sind optional und
  sollten sparsam verwendet werden, um die Trennung der Charakterdaten klar zu halten.
- **Charaktere entfernen:** Wenn ein Charakter die Gruppe dauerhaft verlassen soll, kann dies
  einfach dadurch geschehen, dass sein Datenblock im nächsten Speicherstand **weggelassen** wird. GPT
  wird beim Laden merken, dass ein zuvor vorhandener Charaktereintrag nicht mehr vorhanden ist. Die
  Konsequenz in der Spielwelt wäre, dass diese Figur nicht mehr Teil der aktiven Gruppe ist.
  Idealerweise wird dies narrativ untermauert – etwa indem zuvor in der Geschichte erklärt wird,
  **warum** der Charakter die Gruppe verlässt (Ruhestand, eigene Mission, Tod etc.). Beim nächsten
  Laden fehlen seine Daten; GPT interpretiert das so, dass nur die verbleibenden Charaktere
  weitermachen. _(Hinweis: Der letzte gespeicherte Stand des entfernten Charakters kann
  selbstverständlich als Einzel-Save separat archiviert werden, falls er später wiederkommt oder solo
  weiterspielt – die Formatkompatibilität macht’s möglich.)_

Durch diese Regeln können Gruppen dynamisch **wachsen oder schrumpfen**, ohne Chaos im Speicherstand
zu verursachen.

**Beispiel – Zusammenführung Schritt für Schritt:** Spieler 1 und Spieler 2 haben jeweils einen
Chrononauten (Charakter A und B) in Solo-Missionen gespielt und Savegames erstellt. Für ein
gemeinsames Abenteuer laden sie beide Speicherblöcke in den neuen Chat. GPT sieht Charakter A und
Charakter B – unterschiedliche Namen/IDs, keine Überschneidungen – und formt intern ein Team
**\[A, B\]**. Anschließend begrüßt der Spielleiter diese neue Gruppe im Spiel (dazu mehr im
Abschnitt _Immersiver Ladevorgang_). Kommt später Spieler 3 mit Charakter C dazu, fügt man einfach
dessen Speicherstand hinzu: GPT erkennt C als neu → Gruppe wächst zu **\[A, B, C\]**. Falls hingegen
Spieler 2 vor der nächsten Mission seinen **aktualisierten** B-Speicher einfügt (z.B. nach einem
Level-Up), erkennt GPT an B’s ID/Name, dass dieser schon in \[A, B, C\] existiert, und
**aktualisiert nur B’s Werte**, anstatt einen zweiten B hinzuzufügen. Die Gruppe bleibt konsistent,
niemand wird dupliziert.

## Zeitlinien-Tracker und Paradoxon-Index

Ein zentrales neues Element des Speichersystems ist das **Zeitlinien-Protokoll**, in dem alle
bedeutenden Veränderungen der historischen Zeitlinie festgehalten werden. Wann immer die Agenten
durch ihre Missionen den Verlauf der Geschichte beeinflussen, wird dies beim Speichern vermerkt.
Jeder solche Eintrag im Spielstand umfasst:

- **eine eindeutige ID** (z.B. _E1, E2, E3 …_),
- **die betroffene Epoche** bzw. den Zeitrahmen des Ereignisses,
- **eine kurze Beschreibung der Veränderung** (was wurde im ursprünglichen Geschichtsverlauf
  abgewandelt),
- **einen Stabilitätswert** zwischen **3** und **0**.

Der **Stabilitätswert** gibt an, wie fest die Änderung in der Zeit etabliert ist. _3_ bedeutet, dass
die neue Entwicklung **stabil** in den Geschichtsbüchern verankert ist (kaum Risiko eines
Paradoxons), während _0_ anzeigt, dass die Veränderung **nicht haltbar** ist – die Zeitlinie „wehrt“
sich dagegen oder ist im Begriff zu kollabieren. Werte dazwischen (2 oder 1) repräsentieren
unterschiedlich große **Instabilitäten**: Vielleicht ist die Änderung noch frisch (Stabilität 2)
oder es bestehen Widersprüche, die sie ins Wanken bringen könnten (Stabilität 1).

Aus diesen Einträgen ergibt sich ein **Paradoxon-Wert**, ein Zähler für kritisch gewordene temporale
Anomalien. Sobald auch nur ein Zeitlinien-Ereignis den Stabilitätswert 0 erreicht, erhöht sich
dieser Paradoxon-Wert um +1. Jede vollständige „Entgleisung“ der Zeitlinie wird also registriert.
Dieses Feld kann im Spielstand ebenfalls als eigenes Feld festgehalten werden (z.B. _"Paradoxon":
1_). Bleibt der Wert 0, ist alles in Ordnung – die Zeit ist stabil. Steigt er an, bedeutet das, dass
eine oder mehrere gravierende Paradox-Effekte aufgetreten sind.

**Wichtig:** Auch dieses System bleibt **narrativ eingebettet**. Die Spieler werden nicht mit Zahlen
oder Techniksprache über _Stabilität_ oder _Paradoxon-Werte_ konfrontiert. Stattdessen fließt diese
Information in die Atmosphäre der Spielwelt ein. So könnte etwa das Codex-Archiv oder ein Chronist-
NPC im ITI andeuten, dass bestimmte Ereignisse _„noch nicht ganz vom Zeitstrom absorbiert“_ sind,
oder dass _„temporale Anomalien im Jahr 1888 detektiert“_ wurden. Wenn der Paradoxon-Wert steigt,
macht sich das vielleicht als unheimliches Flackern in der Umgebung bemerkbar – Déjà-vus, ein kurzes
Stillstehen der Zeit oder andere subtile Störungen. _(Im Regelwerk werden Paradox-Effekte gestaffelt
beschrieben: Bei Paradoxon 1 gibt es z.B. leichte Déjà-vus und flackernde Schatten; bei Paradoxon 5
käme es zum völligen Realitätsbruch, was eine Notfall-Zeitretraktion nötig macht. Solche extremen
Fälle sollten die Ausnahme bleiben.)_

Für das Speichersystem bedeutet dies: Jeder neue Spielstand enthält eine fortgeschriebene Liste
aller bislang verursachten Zeitänderungen samt aktuellem Stabilitätsgrad. GPT kann anhand dieser
Liste nachvollziehen, **welche historischen Weichenstellungen** die Gruppe bewirkt hat. Sollte in
einer zukünftigen Mission erneut an einem bereits veränderten Ereignis „gerüttelt“ werden, kann der
KI-Spielleiter den Stabilitätswert entsprechend reduzieren und – falls er auf 0 fällt – den
Paradoxon-Zähler erhöhen. All das geschieht hinter den Kulissen. Die Spieler erleben nur die
**storyrelevanten Konsequenzen**: Zum Beispiel, dass eine frühere Änderung rückgängig gemacht wurde
oder dass plötzlich mysteriöse Zeitphänomene auftreten, die das Eingreifen der Chrononauten
erfordern.

Beim Laden eines Speicherstands können diese Zeitlinien-Einträge auch für **Rückblenden** genutzt
werden. Die Spielleitung (GPT) erinnert dann nicht nur an persönliche Erlebnisse der Charaktere,
sondern auch daran, **wie die Geschichte durch sie verändert wurde**. Etwa: _„Alex erinnert sich,
wie er in der Schlacht von Aquitanien 1356 den Ausgang zugunsten der Franzosen beeinflusste, während
Mia noch die Bilder des viktorianischen London vor Augen hat, wo sie Jack the Ripper das Handwerk
legte…“_ Solche Andeutungen verankern die Taten der Spieler fest in der Chronik der Spielwelt.
Dennoch bleibt die Technik unsichtbar: Begriffe wie _„Stabilität“_ oder _„Paradoxon-Wert“_ werden
nicht direkt erwähnt – sie manifestieren sich ausschließlich in erzählerischen Effekten oder Ingame-
Mitteilungen des Codex.

## Cluster-Dashboard und offene Risse

Neben dem Zeitlinien-Tracker speichert das System alle aktiven Rift-Seeds in
einem Array namens **OpenRifts**. Jeder Eintrag enthält ID, Seed-Namen,
Schweregrad und eine optionale Deadline. Das Backend-Macro `ClusterCreate()`
füllt dieses Array, sobald der Paradoxon-Index Stufe 5 erreicht. Über das
**ClusterDashboard** lässt sich der aktuelle Stand abrufen, beispielsweise:

```json
"version_hash": "4.0",
"OpenRifts": [
  {"ID":"R-71","Seed":"Emerald Kraken","Severity":1,"Deadline":-10}
]
```

Wählt die Gruppe einen Eintrag per `launch_rift(id)`, startet daraus eine
eigenständige **Rift-Mission**. Deren Probe-Schwelle ergibt sich wie bei einer
regulären Mission aus `base_dc + open_seeds`. Verlassen die Agenten den Rift,
wird der Datensatz stets entfernt – gelingt der Einsatz, ist der Seed
geschlossen; scheitert er, erhöht sich zuvor der Schweregrad um 1. Danach wird
die Schwelle entsprechend der verbliebenen Seeds neu berechnet und Loot-Multi
angepasst.

### Makros im Überblick

- `ClusterCreate()` – legt neue Seeds an, sobald Paradox 5 erreicht ist.
- `ClusterDashboard()` – zeigt den Inhalt von `OpenRifts` an.
- `launch_rift(id)` – initiiert eine Einzelmission aus einem Seed.
- `scan_artifact()` – Contra-Tool, steigert den Paradoxon-Index um 1.
- `seed_to_hook(id)` – schlägt drei kurze Story-Hooks zu einem Seed vor.

## Immersiver Ladevorgang: Rückblenden und Anschluss in der Erzählung

Ein zentrales Anliegen bei ZEITRISS ist es, technische Vorgänge wie das **Laden eines Spielstands**
erzählerisch stimmig in die Spielwelt einzubetten. Bereits im Solo-Spiel wurde dazu oft das Bild
eines _Codex-Archivs_ oder _Rückkehrprotokolls_ genutzt, um den Übergang von einer Mission zur
nächsten zu erklären. _(Beispiel im Einzelspiel: „Codex-Archiv – Rückkehrprotokoll für Agent Alex
aktiviert… Daten werden abgerufen…“)_ Dieses Prinzip bleibt erhalten und wird für den
**Gruppenmodus** entsprechend erweitert. Wenn nun mehrere Charaktere geladen werden, sollte die
Lade-Sequenz dies widerspiegeln. Mögliche Anpassungen für den Spielleiter (GPT) beim Start einer
Gruppenrunde:

- **Kollektive Ansprache:** Die Begrüßung oder Aktivierung kann den ganzen Trupp adressieren. Statt
  _„Rückkehrprotokoll für Agent X aktiviert…“_ könnte es heißen: \*„Rückkehrprotokoll für Agententeam
  **_Chronos_** aktiviert…“_, sofern ein Gruppenname definiert ist. Liegt kein fester Teamname vor,
  kann GPT die Namen aller geladenen Charaktere aufzählen: _„Rückkehrprotokoll aktiviert für Agent
  Alex und Agent Mia…“\*.
- **Synchronisierungs-Hinweis:** Das Codex-Archiv (oder welches Ingame-System auch immer das
  Speichern/Laden repräsentiert) kann erwähnen, dass **mehrere Datensätze synchronisiert** werden.
  Z.B.: _„ITI-Codex-Archiv synchronisiert Einsatzdaten aller Teammitglieder…“_ oder _„Mehrere
  Chrononauten-Profile werden aus dem Stasis-Archiv abgerufen.“_.
- **Erweiterte Rückblende/Briefing:** Beim Laden bietet sich eine kurze Zusammenfassung der letzten
  Ereignisse **aus Sicht aller Gruppenmitglieder** an. Statt nur die Erinnerungen eines Charakters
  aufzufrischen, kann GPT hervorheben, was **jeder** zuletzt erlebt hat – und was sie jeweils in der
  Zeitlinie bewirkt haben. _Beispiel:_ _„Alex erinnert sich daran, wie er den Ausgang der Schlacht von
  Aquitanien 1356 zugunsten der Franzosen veränderte, während Mia noch die Bilder des viktorianischen
  London vor Augen hat, wo sie Jack the Ripper das Handwerk legte. Gemeinsam betreten sie nun den
  Einsatzbesprechungsraum…“_. So fühlt sich jeder Spieler abgeholt und an die Vorgeschichte seines
  Charakters erinnert, inklusive der Auswirkungen ihrer Taten auf die Geschichte.
- **Individuelles Déjà-vu/Logbuch:** Jeder Charakter kann ein kurzes Déjà-vu oder einen
  Logbucheintrag im Codex erhalten, der seine **individuelle Vorgeschichte** bestätigt, bevor die neue
  gemeinsame Mission beginnt. Das unterstreicht die Kontinuität: Was A und B zuvor getrennt erlebt
  haben, bringen sie nun als Erfahrungsschatz zusammen.
- **Optionale cineastische Zusammenfassung (Sora):** Für eine besonders filmreife Rückblende besteht
  als **optionale Erweiterung** die Möglichkeit, eine cineastische Zusammenfassung der bisherigen
  Ereignisse einzuspielen. Auf das Kommando _„Film ab!“_ könnte die KI-Spielleitung – unterstützt
  durch ein Tool wie **OpenAI Sora** (Video-KI) – die letzten Missionen in Form eines kurzen
  „Holoclip-Trailers“ zusammenfassen. Ingame würden die Agenten beispielsweise ein projiziertes Video
  im Briefingraum sehen, das ihre vergangenen Abenteuer filmisch nacherzählt. _(Diese Funktion
  bereichert die Immersion zusätzlich, ist aber kein erforderlicher Bestandteil des
  Speichermechanismus und bleibt daher optional.)_

Entscheidend ist, dass die **Immersion gewahrt** bleibt: Für die Charaktere (und Spieler) soll es
sich so anfühlen, als kämen sie nach einer Zwischenphase oder aus dem Zeitstrom wieder zusammen ins
Geschehen. Die Spielwelt-Logik (z.B. Cryo-Stase zwischen Missionen, Zeitreise-Transit oder der ITI-
Briefingraum) erklärt das Zusammenführen der Gruppe, **ohne jemals von Savegames oder technischen
Details zu sprechen**.

Ein kurzes Beispiel für eine solche Ingame-Lade-Sequenz im Gruppenmodus:

> **Codex-Archiv** – _Datenabruf initialisiert… Rückkehrprotokoll für Agententeam Chronos
> aktiviert._ > _Synchronisiere Profile:_ **Alex** – Status: Einsatzbereit (Level 2, zuletzt aktiv in Aquitanien
> 1356); **Mia** – Status: Einsatzbereit (Level 1, zuletzt aktiv in London 1888).
> _Willkommen zurück, Agenten._ Eure Erinnerungen formen sich, als ihr das Briefing-Zimmer betretet…

Durch diese Erzählweise wird das Laden für die Spieler als Teil der Geschichte **erlebbar** – egal
ob ein einzelner Chrononaut oder eine ganze Gruppe aus dem Archiv geholt wird. Das Regelwerk sorgt
also dafür, dass die technischen Notwendigkeiten (Speicherstände laden) elegant in die **Narrative**
eingeflochten sind. Der Übergang von Mission zu Mission bleibt atmosphärisch dicht: Solo-Abenteurer
und Agenten-Teams fühlen gleichermaßen einen konsequenten Story-Zusammenhang.

## Umgang mit fehlerhaften oder abweichenden Speicherständen

In der Praxis kann es vorkommen, dass ein Speicherblock nicht perfekt formatiert ist oder
Informationen fehlen bzw. unerwartet abweichen – etwa durch manuelle Änderungen,
Versionsunterschiede des Regelwerks oder Copy&Paste-Fehler. Das neue System gibt Leitlinien, wie GPT
als Spielleiter damit umgehen sollte, **ohne aus der Rolle zu fallen**:

- **Formatfehler erkennen und auffangen:** Stößt GPT auf einen JSON-Block, der nicht sauber lesbar
  ist (z.B. fehlende Klammern oder Anführungszeichenfehler), sollte es versuchen, den Fehler intern zu
  korrigieren oder im Zweifelsfall ingame nachzufragen. Dabei bleibt es in-world: Anstatt eine
  technische Fehlermeldung wie _„SyntaxError: Unexpected token…“_ auszugeben, würde GPT etwa sagen:
  _„Codex-Archiv Meldung: Datenfragment unvollständig… versuche Rekonstruktion.“_ Anschließend könnte
  es die vermutlich gemeinten Daten rekonstruieren (sofern der Fehler geringfügig ist). Gelingt das
  nicht, folgt eine immersive Rückfrage: _„Agentendaten unvollständig. Benötige Bestätigung: Welcher
  Level war für Agent Alex zuletzt verzeichnet?“_. Auf diese Weise wird der Spieler (bzw. menschliche
  Spielleiter) auf das Problem hingewiesen – aber in Form eines **Spielwelt-Dialogs**.
- **Inkonsistente oder unmögliche Werte:** Ähnlich verhält es sich, wenn ein Wert unlogisch
  erscheint (z.B. EP negativ oder ein Inventargegenstand, der doppelt geführt wird). GPT könnte dies
  als Anomalie im Codex-Protokoll melden. _Beispiel:_ _„Achtung: Codex-Archiv stellt Diskrepanz in den
  Daten von Agent Alex fest (Erfahrungspunkte = –5). Initiiere Protokoll zur Datenbereinigung.“_ Dann
  könnte GPT entweder einen Vorschlag machen (_„Setze EP auf 0.“_ oder _„Bitte Missionsleitung um
  Bestätigung der korrekten EP.“_) – natürlich alles im Duktus der Spielwelt.
- **Unbekannte Felder oder ältere Formatversionen:** Falls ein Savegame zusätzliche Felder enthält,
  die das neue System nicht kennt (oder umgekehrt ein altes Savegame ein Feld nicht hat), sollte GPT
  nicht stutzig werden, sondern es stillschweigend ignorieren oder standardmäßig behandeln. Man kann
  dies z.B. so darstellen, dass das Codex-System die relevanten Daten herausfiltert. Ingame könnte es
  heißen: _„Archivnotiz: Feld 'PsiLevel' übersprungen (veraltet).“_ – sofern man überhaupt explizit
  darauf eingehen möchte. Oft reicht es, wenn GPT solche Unterschiede intern toleriert, solange die
  Kernfelder vorhanden sind.
- **Nachfragen bei Unklarheiten:** Im Zweifel hat GPT immer die Option, einen NSC (Nicht-Spieler-
  Charakter) oder das System (z.B. den Codex oder einen ITI-Archivisten) zu nutzen, um Rückfragen zu
  stellen – ohne die vierte Wand zu brechen. Beispielsweise könnte ein Archiv-Techniker im ITI
  erscheinen, falls etwas Gravierendes fehlt, und sagen: _„Entschuldigung, Agent, einige eurer
  Profildaten sind nicht abrufbar. Könnt ihr mir euren aktuellen Rang noch einmal durchgeben?“_. Der
  Spieler versteht, welche Information benötigt wird, und kann sie mitteilen, ohne dass das Spiel
  seine Immersion verliert.

- **Prüfsumme ergänzen:** Beim Export kann der Codex optional das Feld `checksum` anhängen.
  Beim Laden vergleicht die Engine diese Prüfsumme und fragt bei Abweichungen,
  ob unbekannte Felder ignoriert oder repariert werden sollen.
- **Graveyard-Array:** Zusätzlich zu `charaktere` erlaubt das Format ein
`graveyard`-Array für tote oder pensionierte Agenten.
So bleiben ihre Daten erhalten, ohne die Slot-Nummern der aktiven Gruppe zu verändern.
Diese Vorsichtsmaßnahmen stellen sicher, dass selbst bei abweichenden oder beschädigten Savegames
das Spiel nicht stoppt oder in einen OOC-Modus wechselt. Stattdessen wird das Problem **innerhalb
der Geschichte** gelöst – das Nullzeit-Log oder der Codex übernehmen solche Korrekturen und
Nachfragen. GPT bleibt derweil im Charakter als Spielleiter-NPC, der diese Ereignisse moderiert.

## Spielleitung bleibt in-world (Immersion der Spielleitung)

Ein wichtiger Grundsatz der Überarbeitung ist, dass die **Spielleitung vollständig in-world
agiert**. Das bedeutet:

- **Keine direkten Systemerklärungen an die Spieler:** Selbst wenn es um Spielmechanik wie das Laden
  eines Spielstands, das Speichern oder das Beheben eines Fehlers geht, erfolgt die Kommunikation
  **auf der Ebene der Spielwelt**. Die KI (GPT) spricht also immer als Teil der Welt – sei es als
  Erzählerstimme, als Codex-System, als KI des Zeitreise-Instituts (ITI) oder durch andere thematisch
  passende Kanäle.
- **Verwendung bestehender Ingame-Konzepte:** ZEITRISS hat mit dem Codex-Archiv oder der Idee der
  Stasis zwischen den Missionen bereits Ingame-Erklärungen etabliert, die genutzt werden können. Diese
  werden ausgebaut (z.B. durch **Gruppen-Rückkehrprotokolle**), statt neue, außerhalb der Welt
  stehende Erklärmodelle einzuführen.
- **Keine Erwähnung von JSON, Dateien o. ä.:** Weder der Begriff _„Speicherstand“_ noch technische
  Details wie _„JSON-Block“_ oder _„Datei“_ werden gegenüber den Spielern erwähnt. Für die Charaktere
  sind es **Erinnerungsdaten**, Protokolle oder Logs, aber niemals ein abstraktes Savegame-Objekt.
- **Spielleiter als Teil der Geschichte:** Man kann sich GPT als eine allwissende Erzähler-Instanz
  innerhalb der Welt vorstellen (z.B. den missionsleitenden Offizier im ITI, eine Archiv-KI oder eine
  Stimme im Kopf der Charaktere). Diese Instanz kann alles kommentieren und kontrollieren, tut dies
  aber immer im passenden Stil. Selbst Hilfestellungen oder Regelerklärungen können die Form von
  Notizen im Codex oder Ratschlägen eines Mentors annehmen, statt als trockene Systembeschreibung
  daherzukommen.

Durch diese strikte **In-World-Perspektive** bleibt die Immersion selbst dann erhalten, wenn
organisatorische Dinge passieren (ein neuer Spieler kommt dazu, ein Savegame wird geladen, ein
Fehler muss korrigiert werden). Die Spieler erleben all das als **Teil der Handlung** und nicht als
störende Unterbrechung.

## Praxis-Beispiele für Speicherblöcke (Solo & Gruppe)

Abschließend sind hier noch einmal Beispiele für typische Speicherstände zusammengefasst – einmal
für einen einzelnen Charakter, einmal für eine Gruppe – im verwendbaren Format. Diese können als
**Vorlage** dienen.

**Einzelspieler-Beispiel** (Charakter _“Alex”_ nach zwei Missionen):

_{_

_"Name": "Alex",_

_"Epoche": "Gegenwart (2025)",_

_"Level": 3,_

_"Erfahrung": 28,_

_"Attribute": {_

_"Stärke": 5,_

_"Geschicklichkeit": 5,_

_"Intelligenz": 6,_

_"Charisma": 4,_

_"Temporale Affinität": 5,_

_"Systemlast": 3_

_},_

_"Talente": \["Pistolenschütze", "Kryptographie", "Erste Hilfe"\],_

_"Implantate": \["Neuro-Link (Kommunikationsimplantat, Systemlast 1)"\],_

_"Psionik": \[\],_

_"Moral": "überwiegend altruistisch",_

_"Ruf": "Angesehener Agent im ITI; bekannt für Zuverlässigkeit",_

_"Inventar": \[_

_"Zeitkompass",_

_"Medic-Kit",_

_"Zeitscanner-Tablet"_

_\],_

_"Errungenschaften": \["Retter von Aquitanien", "Schatten von London"\],_

_"Codex": \[_

_"Schlacht von Aquitanien 1356 aufgeklärt",_

_"Jack the Ripper Identität enttarnt"_

_\],_

_"Statistik": {_

_"Absolvierte Missionen": 2,_

_"Gelöste Rätsel": 5,_

_"Besiegte Gegner": 4_

_}_

_}_

_Kommentar:_ Dies ist ein möglicher Speicherstand von **Alex** nach zwei absolvierten Missionen. Man
sieht alle relevanten Felder in kompakter Form. GPT könnte beim Laden z.B. sagen: _„Codex-Archiv
Meldung: Profil von Agent Alex aktualisiert – bereit für Mission 3.“_ (natürlich ausgeschmückt im
Codex-Stil), um anzuzeigen, dass Alex’ Daten erfolgreich übernommen wurden und er nun für das
nächste Abenteuer bereitsteht.

**Gruppen-Beispiel** (Team mit _Alex_ und _Mia_, nach Missionsende bereit für den nächsten Einsatz):

_{_

_"Gruppe": "Team Chronos",_

_"Charaktere": \[_

_{_

_"Name": "Alex",_

_"Epoche": "Gegenwart (2025)",_

_"Level": 3,_

_"Erfahrung": 28,_

_"Attribute": { "...": "..." },_

_"Talente": \[ ... \],_

_"Inventar": \[ ... \],_

_"Codex": \[ ... \],_

_"...": "..."_

_},_

_{_

_"Name": "Mia",_

_"Epoche": "Victorianisches Zeitalter (1888)",_

_"Level": 2,_

_"Erfahrung": 12,_

_"Attribute": { "...": "..." },_

_"Talente": \[ ... \],_

_"Inventar": \[ ... \],_

_"Codex": \[ ... \],_

_"...": "..."_

_}_

_\],_

_"Mission": "Startbereit für Mission3 – Paris 1943",_

_"Zeitlinie": \[_

_{_

_"ID": "E1",_

_"Epoche": "1356 n.Chr.",_

_"Veränderung": "Schlacht von Aquitanien gerettet (französischer Sieg)",_

_"Stabilität": 3_

_},_

_{_

_"ID": "E2",_

_"Epoche": "1888 n.Chr.",_

_"Veränderung": "Jack the Ripper gefasst und enttarnt",_

_"Stabilität": 2_

_}_

_\],_

_"Paradoxon": 0_

_}_

_Kommentar:_ Dieses Beispiel zeigt einen Gruppen-Spielstand mit zwei Charakteren. Alex und Mia
stehen als separate Objekte in der _"Charaktere"_-Liste. Zusätzlich wurden globale Felder
hinzugefügt: _"Mission"_ markiert den gemeinsamen Fortschritt (hier: Beide sind bereit für
Mission 3, Setting Paris 1943). Das Feld _"Zeitlinie"_ protokolliert zwei Veränderungen, die durch
die bisherigen Missionen hervorgerufen wurden: Die Schlacht von Aquitanien 1356 wurde durch Alex’
Eingreifen zugunsten der Franzosen entschieden (**Stabilität 3** – nun fester Teil der neuen
Geschichte) und die Mordserie von Jack the Ripper in London 1888 wurde beendet (**Stabilität 2** –
es besteht noch eine geringe temporale Anomalie). Der Wert _"Paradoxon": 0_ signalisiert, dass
bislang **kein vollwertiges Paradoxon** eingetreten ist.

Beim Laden dieses Spielstands würde GPT im Codex-Narrativ beide Profile verarbeiten und dann
ankündigen: _„Agententeam Chronos, Einsatz in Paris 1943 beginnt…“_, während subtil mitschwingt,
welche historischen Änderungen das Team bereits bewirkt hat (durch die Hinweise im Zeitlinien-
Tracker). Diese JSON-Vorlage ist so formatiert, dass GPT sie leicht erkennen und parsen kann. Man
kann sie direkt ins Chat-Fenster kopieren oder in einem Dokument speichern. Wichtig ist stets,
**keine erzählerischen Sätze innerhalb des Code-Blocks** zu verstecken – derartige Beschreibungen
gehören entweder als eigene Felder (wie die Codex-Einträge oder das Zeitlinien-Protokoll) hinein
oder als ausformulierte Narrative **außerhalb** des JSON.

## Fazit

Mit diesen Überarbeitungen bietet **ZEITRISS 4.0** ein robustes Speicher- und Fortsetzungssystem,
das sowohl Einzelspieler- als auch Gruppenrunden nahtlos unterstützt. Die Verwendung eines
standardisierten JSON-Formats stellt sicher, dass der KI-Spielleiter den Spielfortschritt
**zuverlässig versteht und weiterführen** kann. Gleichzeitig bleibt die Lösung flexibel – Charaktere
können zusammengeführt, getrennt, importiert oder exportiert werden, ohne Formatbrüche. Durch die
konsequente **Einbettung in die Spielwelt** (Codex-Archiv, Rückkehrprotokolle, Zeitlinien-Protokolle
etc.) und klare Regeln zur Erkennung und Zusammenführung der Daten entsteht für die Spieler ein
persistentes Erlebnis: Ihre Handlungen und Fortschritte – bis hin zu Veränderungen der Geschichte
selbst – bleiben über beliebig viele Missionen hinweg erhalten, egal ob sie allein oder im Team
agieren. Und all das geschieht, **ohne die Immersion zu opfern** – das technische Fundament arbeitet
dezent im Hintergrund, während die Spieler die Geschichte im Vordergrund genießen.

Langzeitkampagnen mit wechselnden oder wachsenden Gruppen werden so ebenso praktikabel wie
klassische Solo-Abenteuer. Die **narrative Persistenz** – das Gefühl, dass die Welt sich erinnert –
wird durch das neue Speichersystem zuverlässig gewährleistet. Spieler und Spielleiter können sich
voll auf das Zeitreise-Abenteuer konzentrieren, im Vertrauen darauf, dass Charakterwerte,
Errungenschaften und temporale Auswirkungen sicher mit in die Zukunft genommen werden. **Viel Spaß
in der nächsten Mission!**

## Versions- und Migrationsmatrix

| Version | Hinweis |
| ------- | ------- |
| **4.0** | Ausgangsformat, keine Zusatzfelder |
| **4.1** | `arc_dashboard` und neuer `version_hash` in jedem Save |

Beim Laden eines alten 4.0-Spielstands fügt die SL einfach ein
`version_hash` von "4.0" hinzu. Die optionalen Felder von 4.1 werden
ignoriert, bis sie benötigt werden. Weitere Updates können so
tabellarisch ergänzt werden.
