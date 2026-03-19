# ZEITRISS – ITI/MMO-Konsistenz-Review (frischer Nachcheck)

## Kurzfazit

Der aktuelle Stand ist **deutlich besser** als in den früheren Durchläufen:

- feste Fraktionskontakte sind inzwischen benannt,
- Mira ist als Erstbetreuerin für Neulinge gesetzt,
- Renier ist als Gesamtkoordinator klar verankert,
- NPC-/Split-/Rejoin-Kontinuität ist technisch wesentlich belastbarer.

Der größte Restbruch ist jetzt **nicht** mehr Save/Merge, sondern die **ITI-Heimatwelt selbst**:

- dieselbe Anlage hat noch mehrere konkurrierende Raumtaxonomien,
- alte HQ-Ausbau-Überbleibsel stehen noch im aktiven Runtime-Kanon,
- wichtige ITI-Hauptfiguren sind zwar im Lore-Kern benannt, aber nicht hart genug in Masterprompt / SL-Referenz / Toolkit verankert,
- dadurch kann die KI-SL im Single- und Multiplayer noch immer „denselben Ort neu erfinden“.

Das ist lösbar – und zwar mit **wenig Zusatzsystem**, vor allem über **harten Hauskanon** statt mehr JSON.

---

## Wichtigste Baustellen

### 1) ITI-Ortsnamen sind noch gespalten

Aktuell konkurrieren mindestens zwei Weltkarten:

**Lore-/Cine-Kanon:**

- Quarzatrium
- Med-Lab
- Kodex-Archiv / Forschungszentrum
- persönliche Quartiere
- Zero Time Lounge
- Pre-City-Hub

**Toolkit-/Runtime-Kanon:**

- Gatehall
- Research-Wing
- Operations-Deck
- Crew-Quarters
- Hangar-Axis
- Mission-Briefing-Pod

Das ist nicht nur Stil, sondern ein echter MMO-Immersionsbruch: Spieler sprechen dann über „das Forschungslabor“, „Gatehall“ oder „Quarzatrium“, obwohl sie eigentlich denselben Ort meinen.

**Ziel:** ein einziger, player-facing ITI-Atlas.

---

### 2) HQ-Ausbau ist noch als aktives System drin

Das widerspricht der gewünschten Weltlogik.

Der korrekte Zeitriss-Kern ist aus meiner Sicht:

- Das ITI **wird nicht gebaut oder hochgelevelt**.
- Die Nullzeit-Anlage ist eine konstante, bestehende Struktur.
- Was wächst, sind **Zugänge, Lizenzen, Freigaben, Beziehungen und Sonderrechte**.
- Persönliches Quartier = Stash + Rollenspielraum.
- Fahrzeuge = am Charakter gebunden, nicht Basisbau.
- Sondermissionen können Zugänge oder Nutzungsrechte begründen, aber kein separates Ausbau-Minispiel.

Darum sollte alles, was nach **„HQ-Ausbau“, „Stufe 1/2/3“ oder „freikaufen“** klingt, konsequent in **Zugangs-/Lizenzlogik** umgeschrieben werden.

---

### 3) Die wichtigsten ITI-Personen sind noch nicht hart genug als Runtime-SSOT verankert

Positiv: Der Kern nennt bereits feste Figuren.

Aber: Im Toolkit steht bei HQ-Szenen noch oft nur sinngemäß „aktive NSCs“, „Shop“, „Werkstatt“, „Kodex-Gespräche“. Das lädt eine KI-SL dazu ein, neue Leute zu erfinden – und genau das zerstört das Gefühl einer lebenden, wiedererkennbaren Heimatbasis.

**Ziel:** feste Kernbesetzung, feste Zuständigkeiten, feste Standardorte.

---

### 4) Singleplayer und Multiplayer brauchen dieselbe ITI-Heimatwelt

Das Spielgefühl muss sein:

- egal ob Solo,
- Solo mit NPC-Team,
- Join in Menschengruppe,
- Rejoin nach Branch,
- neuer Chat,

… **das ITI bleibt dasselbe Haus**.

Die Welt draußen darf wild und verzweigt sein.
Das ITI darf **nicht** bei jedem neuen Chat ein anderer Filmset sein.

---

## Meine Empfehlung: „ITI-Hardcanon“ als kleines, aber hartes Zusatzmodul

Nicht als neues Spielsystem.
Nicht als Ausbau-Mechanik.
Nicht als Save-Ballast.

Sondern als **klare Laufzeitregel**:

> Die Nullzeit ist der konstante Heimatraum des Spiels. Kernorte und Kernpersonal des ITI sind fest. Sie dürfen beschrieben, vertieft, belastet oder emotional aufgeladen werden, aber nicht pro Chat neu benannt oder funktional ausgetauscht werden.

Das ist der eigentliche MMO-Kniff.

---

## Copy-paste-Issue 1 – ITI-Atlas als einziger player-facing Hauskanon

**Titel:** ITI-HQ-Atlas vereinheitlichen und als Hardcanon in Masterprompt / SL-Referenz / Toolkit verankern

**Problem**
Das geladene Runtime-Material benutzt derzeit konkurrierende HQ-Bezeichnungen (`Quarzatrium` / `Gatehall`, `Med-Lab` / `Research-Wing`, `Mission-Briefing-Pod` / Briefing im Quarzatrium etc.). Dadurch kann die KI-SL denselben Ort in neuen Chats anders benennen, obwohl die Welt konstant wirken soll.

**Ziel**
Genau ein player-facing ITI-Atlas. Interne Alias-Begriffe dürfen höchstens als Unterzonen oder Dev-Hilfen vorkommen, aber nicht als gleichwertige Hauptorte.

**Vorschlag – kanonische Hauptorte**

1. **Quarzatrium** — Ankunft, Sicherheitsrahmen, Großbriefings, Transfer
2. **Kodex-Archiv** — Recherche, Akten, Theorien, Ordo-Zugang
3. **Med-Lab** — Klinik, Bioware/Cyberware, Diagnostik
4. **Operations-Deck** — Missionsplanung, Raumzeitkarte, Rift-/Seed-Scanner
5. **Crew-Quarters** — persönliche Quartiere, Stash, Ruhe
6. **Hangar-Axis** — Fahrzeugdeck, Wartung, Rift-Starts, Sprungplattformen
7. **Zero Time Lounge** — sozialer Treffpunkt, Bar, informelle Gespräche
8. **Pre-City-Hub** — Übergangsbereich zur Chronopolis-Schleuse

**Alias-Regel**

- `Gatehall` = Foyer-/Empfangszone des **Quarzatriums**
- `Mission-Briefing-Pod` = Briefing-Pod **im Quarzatrium**
- `Research-Wing` = Sammelbegriff für **Kodex-Archiv + Med-Lab + Werkstattbereiche**
- `Crew-Quarters` bleibt nur als englischer Dev-/Style-Alias zulässig; player-facing immer **Crew-Quarters / Quartiere** oder schlicht **Quartiere**

**Akzeptanzkriterien**

- Masterprompt enthält einen kurzen ITI-Hardcanon-Block mit den 8 Hauptorten.
- SL-Referenz nennt dieselben Orte in derselben Reihenfolge.
- Toolkit verwendet nur noch diese Namen player-facing.
- Neue HQ-Szenen dürfen keine neuen Hauptorte erfinden.
- Zusätzliche Räume gelten nur als Unterräume eines Hauptortes.

---

## Copy-paste-Issue 2 – HQ-Ausbau vollständig in Zugangs-/Lizenzlogik umdeuten

**Titel:** HQ-Ausbau-System entfernen und konsequent als feste ITI-Anlage mit Zugangs-/Lizenzlogik formulieren

**Problem**
Mehrere aktive Module sprechen noch von HQ-Ausbau, Ausbaustufen, Freikäufen und späterem HQ-Wachstum. Das widerspricht dem gewünschten Weltbild: Die Nullzeit-Basis ist keine aufbaubare Spielbasis, sondern ein bestehender, konstanter Ort. Fortschritt soll über Ruf, Lizenzen, Freigaben, Rechte, Kontakte und Story-Zugänge laufen.

**Ziel**
Das ITI bleibt räumlich konstant. Fortschritt verändert **Zugriff**, nicht die physische Existenz des Hauses.

**Ersetzungslogik**

- „HQ-Ausbau“ → **ITI-Zugangsstufe / Freigabe / Lizenzrecht**
- „freikaufen“ → **formal freischalten / Zugriff erhalten / Nutzungsrecht bekommen**
- „Quartierausbau“ → **rein narrative Gestaltung des persönlichen Quartiers**
- „Fuhrpark erweitert“ → **zusätzliche Fahrzeugfreigaben / seltene Sondernutzung**, kein Basisausbau
- „eigener Fraktionssektor“ → **eigener Zugangsstatus / Arbeitsbereich / Kommandofreigabe**, nicht als extra Bau-Minispiel

**Direkt übernehmbarer Ersatztext**

> Das ITI selbst wird in ZEITRISS nicht ausgebaut. Die Nullzeit-Anlage ist ein bestehender, konstanter Heimatraum mit festen Kernbereichen, festen Zuständigkeiten und wiederkehrendem Personal. Was im Verlauf einer Kampagne wächst, ist nicht das Gebäude, sondern der **Zugang der Chrononauten**: Ruf, Lizenzen, Sicherheitsfreigaben, Beziehungen, Sonderrechte und die Bereitschaft des Instituts, sensible Bereiche oder Ressourcen zu öffnen. Einzelne Missionen können solche Freigaben erzählerisch begründen oder temporär beschleunigen, bilden aber **kein separates Bau- oder Ausbau-System**. Persönliche Quartiere dienen als Rückzugsort und Stash im Rahmen des Charakterbogens; Fahrzeuge bleiben charaktergebunden und folgen den bestehenden Besitzregeln.

**Akzeptanzkriterien**

- `gameplay/kampagnenstruktur.md`: Abschnitt „HQ-Verwaltung und Ausbau“ ersetzen.
- `characters/charaktererschaffung-grundlagen.md`: alle Verweise auf HQ-Ausbaustufen entfernen.
- `core/sl-referenz.md`: „Quartierausbau“ aus dem HQ-Menü streichen.
- `core/zeitriss-core.md`: Meilensteintexte ohne HQ-Ausbau-Implikation formulieren.

---

## Copy-paste-Issue 3 – ITI-Kernpersonal als feste Runtime-Personen erzwingen

**Titel:** Feste ITI-Hauptfiguren als player-facing Hauskanon in allen Runtime-Modulen verankern

**Problem**
Wichtige ITI-Figuren sind bereits teilweise benannt, aber nicht hart genug in den laufzeitkritischen Modulen verankert. Dadurch kann die KI-SL in neuen Chats leicht andere Laborleitungen, Archivkontakte oder Einsatzansprechpartner erfinden.

**Ziel**
Das ITI soll sich wie ein wiederkehrender Ort mit festem Personal anfühlen.

**Pflichtfiguren (bestehend / bereits angelegt)**

- **Commander Arnaud Renier** — Gesamtkoordinator, Erstempfang, Eskalationen, Schlüsselbriefings
- **Archivarin Mira** — Ordo-Kontakt, Standard-Betreuerin für Neulinge und Mischpool, Kodex-/Archivnähe
- **Pater Lorian** — Chrono-Symmetriker-Kontakt
- **Offizier Vargas** — Kausalklingen-Kontakt
- **Agentin Narella** — Zerbrechliche-Ewigkeit-Kontakt

**Empfohlene neue Service-Anker (direkt einsetzbar, falls gewünscht)**

- **Dr. Sera Halden** — Leitärztin des Med-Lab, trocken, präzise, wenig Geduld für Heldentum im OP
- **Leittech Nox Aurel** — Werkstatt / Hangar-Axis, Fahrzeug- und Sprungwartung, lakonisch, hochkompetent
- **Quartiermeisterin Juno Hark** — Arsenal / Ausrüstung / CU-Freigaben, korrekt, unbestechlich, merkt sich jeden Fehlbestand
- **Cass Roe** — Zero Time Lounge, Barkeeper und informeller Gerüchteknoten, kennt mehr als er sagt

**Direkt übernehmbarer Ersatztext**

> Das ITI besitzt festes Kernpersonal. Diese Figuren sind keine Zufalls-NSCs und werden nicht pro Chat neu benannt. **Commander Arnaud Renier** bleibt die Stimme für Erstkontakt, Eskalationen und fraktionsübergreifende Einsätze. **Archivarin Mira** ist Standard-Ansprechperson für Neulinge, Ordo-Belange, Mischpool-Briefings und Kodex-nahe Anliegen. Nach Fraktionsübertritt übernehmen **Pater Lorian**, **Offizier Vargas** oder **Agentin Narella** die zuständigen Briefings und HQ-Anliegen ihrer Linie. Weitere Service-Figuren dürfen ergänzt werden, ersetzen aber nie dieses Kernpersonal.

**Akzeptanzkriterien**

- Masterprompt erwähnt mindestens Renier + Mira + Fraktions-Liaisons als feste Kernrollen.
- Toolkit nutzt diese Namen aktiv für HQ-Szenen.
- Cinematic-Start ersetzt generische „mysteriöse Archivarin“ / „Kontaktperson“ durch den Kanon.
- Neue HQ-NSCs sind erlaubt, aber nur als Nebenfiguren.

---

## Copy-paste-Issue 4 – ITI-Drift-Guard gegen spontane Umbenennungen

**Titel:** Drift-Guard für Nullzeit-Orte und ITI-Kernpersonal ergänzen

**Problem**
Die KI-SL ist gut im Improvisieren. Genau das ist hier das Problem: spontane kreative Varianz wirkt im Außeneinsatz fantastisch, im ITI aber wie Kontinuitätsbruch.

**Ziel**
Außeneinsatz = variabel. ITI = stabil.

**Direkt übernehmbarer Guard-Text**

> **ITI-Hardcanon / Drift-Guard:** Die Nullzeit ist der konstante Heimatraum der Kampagne. Kernorte und Kernpersonal des ITI werden **nicht** pro Chat neu benannt, nicht funktional ausgetauscht und nicht spontan durch Alternativen ersetzt. Neue Nebenfiguren, Händler, Techniker, Patienten oder Gäste dürfen auftreten, aber sie bleiben dem bestehenden Hauskanon untergeordnet. Gleiches gilt für Räume: Neue Unterräume sind erlaubt, aber nur als Teile eines festen Hauptortes. Wenn ein Spieler einen bekannten ITI-Ort oder eine bekannte ITI-Figur erneut aufsucht, verwendet die Spielleitung denselben Namen, dieselbe Zuständigkeit und denselben narrativen Grundcharakter erneut.

**Akzeptanzkriterien**

- Als Muss-Regel in Masterprompt oder Toolkit aufnehmen.
- Gilt ausdrücklich für Singleplayer, NPC-Team und Multiplayer.
- Gilt auch nach Chatwechsel und Mehrfach-Load.

---

## Copy-paste-Issue 5 – Bestehende Kontinuitätssysteme für feste ITI-Beziehungen nutzen

**Titel:** Feste ITI-NPC-IDs und Echo-Konvention ohne neues Save-Subsystem einführen

**Problem**
Die Kontinuitätssysteme sind inzwischen stark, aber sie werden noch nicht gezielt genutzt, um **feste ITI-Kontakte** gruppenübergreifend wiedererkennbar zu machen.

**Ziel**
Kein neuer JSON-Klotz. Nur ein smarter Namensanker.

**Vorschlag**
Nutze bestehende Felder (`continuity.npc_roster[]`, `roster_echoes[]`, `shared_echoes[]`) mit festen ITI-IDs:

- `ITI-RENIER`
- `ITI-MIRA`
- `ITI-LORIAN`
- `ITI-VARGAS`
- `ITI-NARELLA`
- optional: `ITI-HALDEN`, `ITI-NOX`, `ITI-JUNO`, `ITI-CASS`

**Regel**

- Die festen ITI-Personen existieren **ohne Saveeintrag** bereits als Hauskanon.
- Nur wenn eine laufende persönliche Bindung, Schuld, Gefälligkeit, Fehde oder offene Aufgabe wichtig wird, darf zusätzlich ein kompakter Eintrag in `continuity.npc_roster[]` oder ein Echo erscheinen.
- Standardisierte Echo-Form: `ITI-ID :: kurzer Status / Hook`

**Beispiele**

- `ITI-MIRA :: hält Petrow-Akte zurück, bis der Datenkristall geprüft ist.`
- `ITI-RENIER :: erwartet umgehenden Lagebericht zu Berlin-1989.`
- `ITI-JUNO :: hat Sonderfreigabe für eure Resonanz-Sniper widerrufen.`

**Nutzen**

- Null zusätzlicher Systemballast.
- Hohe Wiedererkennbarkeit.
- Gleiche Personen tauchen in unterschiedlichen Gruppen glaubhaft wieder auf.

---

## Copy-paste-Issue 6 – Pflicht-Homecoming-Beat für MMO-Immersion

**Titel:** Nach Load und nach Mission immer einen kurzen ITI-Heimkehr-Beat mit festen Orts-/Personenankern ausgeben

**Problem**
Selbst bei gutem Save-Merge kann die Welt kalt und technisch wirken, wenn das ITI nicht als wiederkehrender „sozialer Heimatraum“ begrüßt.

**Ziel**
Jeder Rücksprung soll sich anfühlen wie Heimkehr in dieselbe lebende Anlage.

**Direkt übernehmbarer Textbaustein**

> **Pflicht-Heimkehr-Beat (HQ):** Nach erfolgreichem Load oder nach jeder Mission liefert die Spielleitung vor Menü/Briefing 2–4 Sätze, die mindestens **einen festen Ort** und **eine feste ITI-Figur** sichtbar machen. Beispielstruktur: (1) Wo landet das Team? (2) Wer ist dort im Dienst oder sichtbar? (3) Welcher kleine Status der Anlage oder eines Kontakts ist neu? Dieser Beat erzeugt Stimmung, Orientierung und Wiedererkennung, ohne ein eigenes Subsystem zu eröffnen.

**Mini-Beispiel**

> Das Quarzatrium empfängt euch mit kaltem Licht und dem trockenen Summen der Quarzfeld-Generatoren. Commander Renier steht bereits am Briefingtisch und wirft nur einen kurzen Blick auf eure Rückkehrdaten, während im Hintergrund Mira eine halb geöffnete Archivkapsel verriegelt. Auf dem Operations-Deck pulsiert ein neuer Seed schwach über der Raumzeitkarte. Willkommen zurück in der Nullzeit.

**Akzeptanzkriterien**

- Nach Mehrfach-Load vor dem Kontinuitätsrückblick oder direkt danach.
- Nach Mission vor HQ-Menü.
- Nie nur Menü/Texttoast ohne Inworld-Heimkehrbild.

---

## Copy-paste-Issue 7 – Ein kleiner, sehr starker MMO-Kniff ohne Systemballast

**Titel:** ITI-Schichtbild / Dienstlage als wiederkehrendes 1-Zeilen-World-State-Element

**Idee**
Füge im HQ optional eine einzige, knappe „Dienstlage“-Zeile ein. Das simuliert eine laufende Welt, ohne Save aufzublähen.

**Formatvorschlag**

- `ITI-Lage: Quarzatrium ruhig · Mira im Archiv · Hangar-Axis Kalibrierung läuft · Chronopolis-Schleuse versiegelt.`
- oder
- `ITI-Dienstlage: Renier im Debrief · Juno prüft Rücklauf · Nox meldet Fahrzeugfenster in 1 Mission.`

**Warum das stark ist**

- extrem billig,
- sofort wiedererkennbar,
- liefert Gesprächsstoff zwischen Spielern,
- verstärkt die Illusion einer permanent laufenden Dienstwelt.

**Regel**

- max. 1 Zeile,
- nur feste Orte / feste Figuren / klarer Status,
- keine neuen Hauptfiguren aus dem Nichts.

---

## Direkt übernehmbarer Ersatztext für das Toolkit

> ## ITI-Hardcanon — Nullzeit als konstanter Heimatraum
>
> Das ITI der Nullzeit ist kein pro Chat neu erfundener Schauplatz, sondern die konstante Heimatbasis der Kampagne. Kernorte und Kernpersonal sind fest und bleiben auch über Chatwechsel, Splits, Merges und unterschiedliche Gruppen hinweg wiedererkennbar. **Player-facing Hauptorte** sind: **Quarzatrium**, **Kodex-Archiv**, **Med-Lab**, **Operations-Deck**, **Crew-Quarters/Quartiere**, **Hangar-Axis**, **Zero Time Lounge** und **Pre-City-Hub**. Andere Bezeichnungen gelten höchstens als Unterzonen oder interne Alias-Begriffe, nicht als neue Hauptorte. Feste Kernfiguren sind mindestens **Commander Arnaud Renier**, **Archivarin Mira**, **Pater Lorian**, **Offizier Vargas** und **Agentin Narella**. Die Spielleitung darf zusätzliche Nebenfiguren einführen, ersetzt aber nie diese Kernrollen und benennt bekannte Orte nicht um.

---

## Direkt übernehmbarer Ersatztext für HQ ohne Ausbau-System

> ## HQ-Logik der Nullzeit
>
> Das ITI wird nicht ausgebaut. Die Nullzeit-Anlage ist eine bestehende, konstante Infrastruktur mit festen Bereichen, fester Waffenruhe und wiederkehrendem Personal. Fortschritt im HQ bedeutet daher **nicht**, Räume zu bauen oder Stufen des Gebäudes freizuschalten, sondern **Zugang, Vertrauen und Nutzungsrechte** innerhalb eines bereits existierenden Systems zu erhalten. ITI-Ruf und Lizenz-Tier steuern, welche Ausrüstung, Dienste oder sensiblen Bereiche einem Chrononauten offenstehen. Persönliche Quartiere bleiben narrative Rückzugsorte mit begrenztem Stash; Fahrzeuge folgen dem Charakterbogen und den bestehenden Besitzregeln. Einzelne Missionen können Sonderzugänge oder Nutzungsrechte erzählerisch begründen, bilden aber kein separates Ausbau-Minispiel.

---

## Direkt übernehmbarer Ersatztext für Single-/Multi-Konsistenz

> ## Singleplayer, NPC-Team und Multiplayer nutzen dieselbe ITI-Heimatwelt
>
> Unabhängig davon, ob ein Chrononaut solo, mit NPC-Begleitung oder in einer Gruppe aus menschlichen Spielern unterwegs ist, bleibt das ITI dieselbe Anlage mit denselben Kernorten und denselben Kernfiguren. Die Welt außerhalb der Nullzeit darf sich verzweigen, verdunkeln, widersprechen oder konvergieren; die Nullzeit selbst bleibt der wiedererkennbare Fixpunkt der Kampagne. Gerade dadurch entsteht die MMO-Illusion: nicht weil alles gleich bleibt, sondern weil das **Richtige** gleich bleibt.

---

## Mein Gesamturteil

Du bist sehr nah dran.

Die größte offene Aufgabe ist jetzt **kein großer Umbau** mehr.
Es ist eher ein letzter **Konsistenzschliff**:

- feste Ortsnamen,
- feste Kernfiguren,
- kein HQ-Ausbau-System mehr,
- ein kleiner Pflicht-Heimkehr-Beat,
- und ein smarter Umgang mit bestehenden Kontinuitätsfeldern für ITI-Beziehungen.

Wenn du genau das jetzt noch einziehst, kippt ZEITRISS spürbar stärker in das gewünschte Gefühl:
**nicht „jede Session ist ein neuer Chat“**, sondern
**„jede Session ist eine neue Rückkehr in dieselbe lebende Nullzeitwelt“**.
