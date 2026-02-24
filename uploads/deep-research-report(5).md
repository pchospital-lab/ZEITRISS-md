# Deep-Research-Patch: Zeitriss-Transfer und Chronopolis-Schleuse

## Executive Summary

Im aktuellen Repo-Stand existieren mehrere, leicht auseinanderdriftende Darstellungen des Übergangs **Nullzeit ↔ Realität** (Sprung/Return) und eine funktionale, aber noch nicht „in die Magengrube gehende“ Beschreibung des **Chronopolis-Zugangs**. Besonders auffällig sind (a) ein Ton-Mismatch („vorsichtig durchtasten“ vs. gewünschter „unangenehmer Sog“), (b) Bildsprache, die stellenweise wieder Richtung „Portal“ kippt, und (c) fehlende Textbausteine, die den Moment **vor** dem Öffnen der Chronopolis-Tore und den **Erlösungsmoment** beim Rückzug in die Schleuse als *epische* Beats zuverlässig reproduzierbar machen. Evidenzpunkte liegen vor allem in `core/zeitriss-core.md` (Abschnitt zur Nullzeit und Zeitriss-Logik), `systems/gameflow/cinematic-start.md` (HQ-Ankunft/Startästhetik), `core/sl-referenz.md` (Transfer-HUD-Frames + Save-Taktung), `systems/gameflow/speicher-fortsetzung.md` (Chronopolis-Schleusen-Savepflicht) und `gameplay/kampagnenstruktur.md` (Chronopolis-Package + Cutscene/Flow).  

Die untenstehenden Issues und Ersatztexte sind so geschrieben, dass sie ohne neue Regeln arbeiten: **TEMP** wird nur als „Feeling-Regler“ für die Spielleitung benannt, nicht als Mechanik; der „Riss“ bleibt **kein Portal**, sondern ein „Schnitt“/„Riss“ mit **Sog**, **Schlag**, **ungewöhnlichem Austrittswinkel**, **sofortigem Verschluss** und einem kurzen **Sortiermoment** danach. Für Chronopolis kommt ein klarer, dramaturgisch verlässlicher Schleusen-Beat plus ein leicht abgewandelter **Schleusen-Debrief** dazu.

## Quellenlage im Repo

Die für diese Überarbeitung relevanten Stellen (als SSOT-orientierte Anker) sind:

- `core/zeitriss-core.md`  
  - Abschnitt zur Nullzeit und zum Zeitriss (derzeit mit „Riss in der Tapete“-Bildsprache, aber auch mit dem unerwünschten „DURCHTASTEN“-Motiv und einer teils veralteten Optionslogik für den Loop).
- `systems/gameflow/cinematic-start.md`  
  - `HQ-Empfang & Sync` (bildstark, aber an einer Stelle wieder „Scheibe/Portal“-Vibe statt „Riss“; außerdem ist die Körperlichkeit des Übergangs noch zu „sauber“).
- `core/sl-referenz.md`  
  - Transfer-Frames (`Nullzeit-Puffer · Transfer 3…2…1 …` / Return-Frame) und Save-Taktung („vor Chronopolis-Schleuseneintritt“ / „nach Chronopolis-Rückkehr“), aber ohne den gewünschten epischen Schleusen-Beat als Textbaustein.
- `systems/gameflow/speicher-fortsetzung.md`  
  - Chronopolis-spezifische Save-/Warnlogik („Kodex fragt verpflichtend …“) ist vorhanden, aber der **Erzähltext** kann stärker „Schleusenangst“ + „Erlösung bei der Rückkehr“ transportieren.
- `gameplay/kampagnenstruktur.md`  
  - Chronopolis-Package (High-Level-Pitch, UI-Flow, Map-Blueprint). Der Flow ist klar, aber die Schleuse als *psychologischer Engpass* (und als „Tore öffnen sich gleich“-Moment) ist noch nicht als Copy-Paste-Beat ausgearbeitet.

## Designziele und Invarianten

Diese Änderungen zielen ausdrücklich auf **Immersion, Konsistenz und Spielleitungs-Usability** – nicht auf neue Regeln.

- Der Zeitriss ist **kein Portal**: keine „Tür“, kein „Tunnel“, kein gemütliches Durchschreiten. Er ist ein **Riss** (Schnitt) mit **Sog** und **Schlag**.
- Der Sprung ist **unangenehm**, kurz, kompromisslos: Riss reißt auf → zieht → Auswurf in „falschem Winkel“ → sofort zu → Sortieren.
- **Team-Cohesion** wird als *In-World-Logik* betont (zusammenstehen, anfassen, sichern), ohne ein zusätzliches Regelmodul zu erzeugen.
- **TEMP** ist ein *Erzählregler*: hohe TEMP-Werte „sehen cooler aus“ (bessere Landung, weniger Übelkeit), niedrige TEMP-Werte wirken „ruppiger“ – ohne neue Würfelmechanik.
- **Nicht-Zeitreisende** werden nicht „adressiert“: allein ist ein Durchkommen fast unmöglich; als **Passagiere** können sie in direktem Kontakt von Chrononauten „mitgerissen“ werden.
- Chronopolis bekommt zwei klare, wiederverwendbare Beats:  
  - **Eintreten** = Angst vor dem, was hinter dem Tor ist (Stimmung/Instanz unklar).  
  - **Rückkehr** = Erlösung, wenn die Schleuse hinter einem zufällt, gefolgt von einem **Schleusen-Debrief** (leicht abgewandelt vom Missions-Debrief).

## Befunde und Issues

### ZR-TRF-001 — Zeitriss wirkt stellenweise noch „zu portalig“ oder „zu vorsichtig“
**Befund:** In `core/zeitriss-core.md` wird der Riss zwar als „Riss in der Tapete“ beschrieben, aber das Motiv „Erfahrene Chrononauten tasten den Riss ab“ läuft direkt gegen den gewünschten Ton („unangenehm, Sog, ratz“). In `systems/gameflow/cinematic-start.md` kippt die Bildsprache an einer Stelle in Richtung „schwebende Scheibe“, was wieder Portal-Assoziationen triggert.  
**Risiko:** Uneinheitliches Kopfkino: Neue Spieler lesen „Tapete-Riss“, erleben aber „Portal-Scheibe“, SL liest „tasten“, du willst „Sog“. Das ist genau die Sorte Standarddrift, die später überall kleine Inkonsistenzen erzeugt.

### ZR-TRF-002 — Der „Sortiermoment“ nach dem Sprung ist noch nicht als SSOT-Beat formuliert
**Befund:** Mehrere Module erwähnen Transfer-Frames oder HQ-Cuts, aber der **verlässliche** Textbeat „Auswurf im Winkel → sofort zu → kurz orientieren → weiter“ fehlt als Copy-Paste-Block für SL/Runtime.  
**Risiko:** Jede Leitung improvisiert anders; der eigentliche Immersionsanker (Sprunggefühl) wird zum Zufallsprodukt.

### ZR-TRF-003 — Passagiere/Nicht-Zeitreisende sind nicht klar als In-World-Regel (ohne Mechanik) formuliert
**Befund:** Das Setting hat Extraction-Ziele, VIPs und das Motiv „jemanden da rausziehen“ ist hochgradig spielrelevant. Ohne klare Formulierung entstehen Rückfragen oder ungewollte „Zivilist geht allein durch“-Szenen.  
**Risiko:** Entweder wird es zu permissiv (Zeitlinie/Nullzeit-Logik verwässert) oder unnötig hart (VIP-Extraction fühlt sich „verboten“ an).

### ZR-CHR-001 — Chronopolis-Zugang ist funktional, aber narrativ noch nicht „Schleusenangst“-fest
**Befund:** Es gibt Warn-UI, Savepflicht und die Instanzlogik. Was fehlt, ist die **Schleuse als psychologischer Schraubstock**: bevor das Tor aufgeht, sollen Spieler dieses „Wir wissen nicht, in welcher Version der Stadt wir landen“ spüren.  
**Risiko:** Chronopolis wird zu einer Menüoption statt zu einem Ereignis.

### ZR-CHR-002 — Rückkehr aus Chronopolis braucht einen eigenen „Erlösungsbeat“ + Schleusen-Debrief
**Befund:** Save-Taktung nennt den Rückkehrpunkt, aber es fehlt der „endlich fällt die Tür zu“-Moment plus eine Debrief-Variante, die sich wie „nach Hause geschafft“ anfühlt und trotzdem strukturell dem bekannten Debrief-Screen ähnelt.  
**Risiko:** Der emotional wichtigste Moment (Rettung/Escape) verpufft, obwohl er eigentlich die Szene trägt.

## Codex-Issues

```md
### [ISSUE] ZR-TRF-001 — Zeitriss-Transfer: Bildsprache konsolidieren (Riss, nicht Portal; kein „DURCHTASTEN“)
**Scope:** core/zeitriss-core.md, systems/gameflow/cinematic-start.md (optional: core/spieler-handbuch.md)
**Problem:** Uneinheitliche Bildsprache (Riss vs. Portal-Scheibe) + unerwünschter „vorsichtig durchtasten“-Ton.
**Ziel:** Ein konsistenter, unangenehmer Transfer-Beat: Riss reißt auf → Sog → Auswurf im Winkel → sofort zu → Sortieren.
**Keine neuen Regeln:** TEMP nur als Erzählschalter/Vibe.

### [ISSUE] ZR-TRF-002 — Transfer-Beat als SSOT-Textbaustein (Nullzeit→Realität und Realität→Nullzeit)
**Scope:** core/zeitriss-core.md (SSOT), core/sl-referenz.md (SL-Notiz/Template), systems/gameflow/cinematic-start.md (Startvariante)
**Problem:** Transfer-HUD ist da, aber kein wiederverwendbarer Erzähltext.
**Ziel:** Copy-Paste-Block (Solo/Gruppe), inkl. Sortiermoment und TEMP-Vibe.

### [ISSUE] ZR-TRF-003 — Passagiere/Nicht-Zeitreisende: In-World-Logik klarziehen
**Scope:** core/zeitriss-core.md (+ optional core/spieler-handbuch.md)
**Problem:** Unklar, ob/warum Zivilisten allein durchkommen könnten; VIP-Extraction braucht klare Logik ohne neue Mechanik.
**Ziel:** „Nicht adressiert“ alleine; „als Passagier“ nur in direktem Griff/Harness mit Chrononauten.

### [ISSUE] ZR-CHR-001 — Chronopolis-Schleuse: Eintrittsbeat schreiben (Angst vor Toröffnung)
**Scope:** gameplay/kampagnenstruktur.md (Chronopolis-Package), systems/gameflow/speicher-fortsetzung.md (Savepflicht + Textbaustein), core/sl-referenz.md (Kurzscript)
**Problem:** Der Zugang ist systemisch klar, aber der Schleusenmoment ist nicht episch/angstvoll genug ausgearbeitet.
**Ziel:** Wiederverwendbarer Schleusen-Text (Eintreten), inkl. Signatur-Dechiffrierung, Ungewissheit, Toröffnung.

### [ISSUE] ZR-CHR-002 — Chronopolis-Rückkehr: Erlösungsbeat + Schleusen-Debrief (leicht abgewandelt)
**Scope:** gameplay/kampagnenstruktur.md, systems/gameflow/speicher-fortsetzung.md, core/sl-referenz.md
**Problem:** Rückkehr ist im Flow erwähnt, aber ohne „Tür fällt zu“-Katharsis + ohne eigenen Debrief-Screen.
**Ziel:** Mini-Debrief: Status/Contraband/Marktlog/„geborgenes Asset“ + Reset + HQ-Menü.
```

## Patch-Paket

### Patch für `core/zeitriss-core.md`

**Anweisung:** Ersetze den gesamten Abschnitt **„Nullzeit-Sprungfenster & ITI-Hub“** (inkl. der bisherigen „Ablauf & Optionen“-Unterpunkte) durch folgenden SSOT-Block.

```md
### Nullzeit-Transfer durch den Zeitriss & ITI-Hub

Ein Zeitriss ist kein Portal im klassischen Sinne — kein Tunnel, kein Tor,
kein „Durchgehen“. Er wirkt wie ein Schnitt in die Tapete der Realität:
ein schmaler, schimmernder Spalt, der die andere Epoche nicht *zeigt*,
sondern *andockt*.

Der Riss sieht nie zweimal gleich aus. Mal ist er ein gezackter, vibrierender
Strich im Raum, mal ein flirrendes Haarline-Glühen, das die Luft „aufreißt“.
Seine Ränder haben keine Form, die man sich gemütlich merken könnte — er ist
eine Geometrie, die dein Körper zu spät versteht.

#### Wie sich ein Sprung anfühlt

Wenn der Zeitriss aufgeht, ist das kein „Schritt nach vorn“. Es ist ein Sog.
Ein kurzer, roher Zug an allem, was in dir Resonanz trägt — als würde die
Realität dich packen und gleichzeitig die Nullzeit dich zurückfordern.

Du spürst Druck auf den Ohren, Kälte im Rachen, und dann diesen halben Herzschlag,
in dem dein Magen das Kommando übernimmt: *falsch herum*.

Spielleitung: Lass diesen Moment kurz, konkret und körperlich sein.
Nicht lang erklären — lieber drei starke Sinneseindrücke.

#### Nullzeit → Realität (Insertion)

Im Quarzatrium steht ihr auf der Sprungplattform. Laserlinien tasten über eure
Silhouetten, nicht als Show, sondern als letzte Verifikation: „Das seid ihr.
Jetzt.“

Das HUD zählt herunter:

`Nullzeit-Puffer · Transfer 3…2…1 · Redirect: +6h`

Dann reißt der Zeitriss auf — direkt vor euch, zu nah für Komfort.

Er zieht.

Ihr werdet nicht „hindurchgeleitet“, ihr werdet mit einem Ruck mitgenommen.
Auf der anderen Seite spuckt euch der Riss in einem unnatürlichen Winkel aus:
seitlich, kniend, taumelnd, manchmal mit der Schulter zuerst, als würdet ihr
aus einem Sturz aufwachen.

Der Riss schließt sich sofort hinter euch. Kein Nachschauen. Kein Zögern.
Eine Sekunde später ist da nur noch Luft — und das Geräusch eures eigenen Atems.

Spielleitung (TEMP-Vibe, keine Regel):
- Hohe TEMP: „schneller gefangen“, bessere Landung, Blick schon oben, Hand schon am Comlink.
- Niedrige TEMP: härterer Schlag, kurze Übelkeit, Hände suchen Halt, Orientierung kostet Sekunden.

#### Realität → Nullzeit (Return)

Der Rücksprung fühlt sich nicht wie Heimkehr an. Erst wie eine Flucht.

Der Zeitriss reißt nur kurz auf — ein Return Window, ein Zugriffskorridor,
ein Moment, der sich wie *jetzt oder nie* anfühlt.

Das HUD bestätigt den Frame:

`Fenster stabil · <TTL> · Return 3…2…1`

Dann wieder: Sog, Druck, Kälte — und dieses brutale „Umklappen“, als würde die Welt
dich nicht gehen lassen wollen.

Nullzeit hat kein Wetter, aber sie hat Stillstand. Der Lärm der Epoche fällt ab,
als hätte jemand die Tonspur gekappt. Du stehst wieder im ITI — und brauchst
trotzdem einen Atemzug, um zu merken, dass du wirklich zurück bist.

#### Zusammen stehen: Team-Geometrie am Riss

Ein Zeitriss ist gnadenlos. Er wartet nicht, bis ihr euch „sortiert“.
Wenn ihr als Team springt, springt ihr als ein Körper: eng beieinander,
Schulter an Schulter, Hand an Gurt oder Ärmel.

Spielleitung: Wenn jemand zu weit weg ist, beschreibe nicht „Regelbruch“,
sondern die Konsequenz der Physik: Der Riss schneidet zu. Der Moment ist vorbei.
Die Gruppe muss erst wieder zusammenfinden, bevor ein neuer Zugriff möglich ist.

#### Passagiere: Warum Nicht-Zeitreisende nicht einfach folgen

Nicht-Zeitreisende werden vom Riss nicht „gerufen“. Ohne Resonanz ist der Spalt
für sie wie eine falsche Tür: kein Sog, kein Griff der Nullzeit — eher ein
kalter Widerstand, als würde man gegen Glas laufen, das nicht da sein dürfte.

Allein ist es fast unmöglich, dass eine Zivilperson den Übergang schafft.

Aber: In direktem Kontakt — fest gehalten, im Griff, über Harness oder Gurt —
können Chrononauten Passagiere mit hindurchziehen. Der Riss „nimmt“ dann, was am
Resonanzkörper hängt. Für Passagiere ist das Erlebnis meist schlimmer:
Panik, Orientierungslosigkeit, Erbrechen, Schock. Für euch ist es Routine.
Für sie ist es ein Trauma.
```

---

### Patch für `systems/gameflow/cinematic-start.md`

**Anweisung:** Passe die Bildsprache in **„HQ-Empfang & Sync“** so an, dass der Riss nicht als „Scheibe/Portal“ wirkt, sondern als *Schnitt/Riss* mit Sog. Außerdem ergänze nach dem Transfer-Frame im Abschnitt „Ablauf zu Beginn“ einen kurzen, harten Sprung-Beat.

```md
#### HQ-Empfang & Sync {#cinematic-hq-comm}
Ein tiefes Dröhnen erfüllt die Stille, als sich mitten in der Ankunftshalle des
ITI-Hauptquartiers ein schmaler, schimmernder Riss auftut — kein Tor, kein Tunnel,
sondern ein Schnitt in der Luft, zu präzise und zu falsch, um „natürlich“ zu sein.
Kaltes Licht läuft an seinen Rändern entlang, als würde die Realität dort ausfransen.

Dann greift der Sog.

Nacheinander — oder gleichzeitig, wenn ihr als Team eng steht — werden die
Chrononauten durch den Riss gerissen. Nicht wie ein Schritt, eher wie ein kurzer
Sturz, bei dem der Körper erst nachträglich versteht, wo oben ist.

Für einen Herzschlag lang hält alles inne: Ohren unter Druck, Magen im Aufstand,
ein grelles Flackern im Sichtfeld. Dann erwachen die Sinneseindrücke der Nullzeit:
klinisch reine, unbewegte Luft; die Stille, die nach einem Schnitt zurückbleibt.

Ein automatisch ablaufendes Rückkehrprotokoll erfasst die Ankömmlinge mit einem Netz
aus grünem Laserlicht, scannt sie auf Anomalien und signalisiert mit einem sanften Ton,
dass alle sicher in der Nullzeit angekommen sind.
```

```md
Beim Sprung zeigt das HUD stets:
`Nullzeit-Puffer · Transfer 3…2…1 · Redirect: +6h (Self-Collision Guard)`.

Ergänze direkt danach (kurz, hart, körperlich):
Der Riss reißt auf — zu nah, zu hell, zu kalt. Ihr werdet mit einem Ruck mitgenommen,
und die Welt klappt einmal über sich selbst. Auf der anderen Seite spuckt euch die
Zielrealität schief aus: Knie, Schulter, Atem. Eine Sekunde Sortieren — dann erst beginnt
der Establishing Shot der Epoche.
```

---

### Patch für `core/spieler-handbuch.md`

**Anweisung:** Ergänze im HQ-/Quarzatrium-Kontext einen kurzen, spielerfreundlichen Abschnitt, der das Sprunggefühl vorbereitet (ohne neue Regeln). Gute Position: direkt nach der Beschreibung der Sprungplattform/Sprungkreise im Quarzatrium.

```md
#### Der Sprung durch den Zeitriss (so fühlt es sich an)

Ein Zeitriss ist kein Portal, durch das man „hindurchgeht“. Wenn er aufreißt, zieht er.
Du stehst auf der Sprungplattform, das HUD zählt runter, und dann kommt dieser kurze,
unangenehme Sog — als würde die Zielrealität dich fordern und die Nullzeit dich zugleich
nicht loslassen wollen.

Auf der anderen Seite kann dich der Riss in einem seltsamen Winkel auswerfen: kniend,
seitlich, fast stürzend. Das ist normal. Der Riss schließt sofort. Du und dein Team
brauchen immer einen Moment, um euch zu sortieren.

Spielleitung: Hohe TEMP-Werte wirken dabei „cooler“ (schnellere Orientierung, sauberere Landung),
niedrige TEMP-Werte rauer — als Feeling, nicht als Zusatzregel.

Wichtig im Team: Steht beim Sprung eng beieinander. Der Riss wartet nicht.
```

---

### Patch für `core/sl-referenz.md`

**Anweisung:** Ergänze im Transfer-Abschnitt (dort, wo die HUD-Frames bereits definiert sind) eine SL-Notiz mit dem neuen SSOT-Beat. Ziel: Runtime/HUD bleibt wie es ist, aber die Leitung hat den „Sog + Auswurf + Sortieren“-Text direkt griffbereit.

```md
**Spielleitung – Transfer-Beat (SSOT, ohne Zusatzregeln):**
- Riss reißt auf (Schnitt in der Luft), nicht „Portal“.
- Er zieht: kurzer Sog, Ohrendruck, Kälte, Magen kippt.
- Auswurf in schiefem Winkel, Riss sofort zu, 1 Atemzug Sortieren.
- TEMP nur als Vibe: Veteranen wirken kontrollierter, Neulinge härter durchgeschüttelt.
- Team-Geometrie: eng stehen, anfassen, sichern; der Riss wartet nicht.
- Passagiere: Nicht-Zeitreisende werden nicht adressiert, allein fast unmöglich;
  in festem Griff können Chrononauten sie mit durchziehen.
```

---

### Patch für `gameplay/kampagnenstruktur.md` (Chronopolis-Schleuse + Schleusen-Debrief)

**Anweisung:** Ergänze im Chronopolis-Package eine neue Untersektion **„Schleusenprotokoll ITI ↔ Chronopolis“** sowie einen **Schleusen-Debrief** (leicht abgewandelt). Gute Position: im Chronopolis-Kapitel nach dem High-Level-Pitch oder direkt vor „Cutscene & UI-Flow“.

```md
### Schleusenprotokoll ITI ↔ Chronopolis (Erzähl-SSOT)

Chronopolis erreichst du nicht wie einen Raum „nebenan“. Du erreichst sie durch eine Schleuse.
Und diese Schleuse ist kein Komfort — sie ist ein Urteil, das sich jedes Mal neu anfühlt.

#### Eintritt (ITI → Chronopolis)

Du stehst im Pre-City-Hub. Hinter dir: Nullzeit, Licht, Routine.
Vor dir: ein Tor, das nie so aufgehen sollte.

Die Schleuse verriegelt mit einem metallischen Schlag. Luft zischt.
Dein HUD fährt das Chronopolis-Overlay hoch, als wäre es plötzlich vorsichtiger als sonst.

Spielleitung: Spiel diesen Moment langsam.
Nicht, weil „Zeit ist“, sondern weil Angst Zeit macht.

Der Kodex beginnt mit der Signatur:
ein kaltes, nüchternes Dechiffrieren. Du weißt: Wenn das Ding heute „falsch“ liest,
öffnet sich gleich eine Stadt, die aussieht, als hättet ihr versagt.

Das Tor vor euch bleibt geschlossen, zu lange.
Man hört nur eure Atemzüge, das leise Klicken von Relais, und dieses dumpfe Dröhnen,
das von Chronopolis her immer wirkt, als käme es aus der Wand.

Dann: ein Ton. Kein freundlicher.
Die Verriegelung löst.

Das Tor öffnet sich — und du weißt nicht, welche Stimmung dahinter wartet:
welche Gesichter, welche Regeln, welche Version der gescheiterten Zeitlinie.
Nur: Es ist echt genug, um dich zu töten, und instabil genug, um dich zu verschlucken.

#### Rückkehr (Chronopolis → ITI)

Die Rückkehr ist kein „Abgang“. Sie ist Flucht nach Hause.

Du erreichst die Schleuse oft mit dem Gefühl, dass die Stadt dich nicht gehen lassen will.
Vielleicht hörst du hinter dir Stimmen, Sirenen, oder nur dieses leere Echo,
das Chronopolis macht, wenn sie „satt“ ist.

Das Innentor öffnet — du stolperst hinein, du reißt dein Team mit,
du packst notfalls jemanden am Gurt. Dann endlich:

Die Tür fällt zu.

Der Geräuschpegel bricht ab. Nicht langsam — wie abgeschnitten.
Die Schleuse verriegelt, und zum ersten Mal seit Minuten fühlt sich dein Atem wieder wie
dein eigener an.

Spielleitung: Das ist der Erlösungsbeat. Gib ihm Gewicht.
Eine Sekunde, in der alle nur stehen und merken: Wir sind drin.

Dann erst: Licht der Nullzeit. Routine. Kontrolle. Debrief.

### Schleusen-Debrief (Chronopolis-Exit-Screen, leicht abgewandelt)

Nach der Rückkehr aus Chronopolis zeigt die Spielleitung einen eigenen Kurzscreen.
Er ist strukturell wie der Missions-Debrief, aber thematisch auf „lebt ihr noch?“
und „was habt ihr rausgebracht?“ fokussiert.

Reihenfolge (kompakt):
1) **Status:** „Zurück in der Nullzeit“ (Team vollständig? verletzt? Schock?)
2) **Contraband/Asset-Check:** Was ist physisch dabei, was ist als Erwerb geloggt?
3) **Chronopolis-Trace:** Käufe/Services (letzte Einträge), inklusive Kosten/Notizen
4) **Geborgenes Highlight:** z.B. „Temporal Ship / Never-Was Gadget / Era-Skin gesichert“
5) **Reset & Stabilisierung:** Stress/Psi-Heat/SYS-Auslastung zurück auf HQ-Base (wie SSOT)
6) **HQ-Menü:** Schnell-HQ / Manuell / Auto-HQ & Save

Spielleitung: Wenn ein „legendäres Fahrzeug“ (Temporal Ship) ergattert wurde,
inszeniere den Moment nach dem Screen kurz:
nicht „ihr tragt es“, sondern „Dock-Freigabe“, Hangartor, Silhouette hinter Glas,
Quartiermeister nickt — jetzt gehört es euch.
```

---

### Patch für `systems/gameflow/speicher-fortsetzung.md` (Schleusen- und Save-Textbaustein)

**Anweisung:** Direkt dort, wo Chronopolis-Schleuseneintritt/Savepflicht beschrieben wird (Synonymstellen im Dokument: „Chronopolis-Schleuseneintritt“, „Warnung“, „DeepSave“), ergänze einen SL-Textbaustein, der die Savefrage als Teil der Schleusenangst inszeniert.

```md
#### Textbaustein: Vor Chronopolis-Schleuseneintritt (Savepflicht als Stimmung)

Spielleitung: Lass die Savefrage nicht wie ein Menü wirken, sondern wie das letzte
„Bist du sicher?“, bevor das Tor auf geht.

Beispieltext:
Die Schleuse verriegelt. Ein rotes Statuslicht läuft über die Kanten der Tür,
als würde das ITI selbst einmal tief durchatmen.

Im Ohr klickt der Kodex trocken:
„Chronopolis-Zugang erkannt. Signaturprüfung erforderlich.“

Eine kurze Pause — zu lang, um sie wegzulächeln.

Dann:
„Verbindlicher Check: HQ-DeepSave jetzt erstellen?“

Mach klar: Das ist kein Komfort-Button. Das ist die letzte saubere Linie,
bevor ihr in eine Stadt tretet, die sich anfühlt wie euer Scheitern.
```

## Abschluss: Was Codex konkret patchen soll

```md
PATCH ORDER (empfohlen):
1) core/zeitriss-core.md — SSOT-Transferblock ersetzen (entfernt „DURCHTASTEN“, entfernt Portal-Vibe, setzt Sog/Sortieren/Passagiere).
2) systems/gameflow/cinematic-start.md — HQ-Empfang & erster Sprung: Bildsprache auf „Riss“ + Körperlichkeit nachziehen.
3) core/spieler-handbuch.md — kurzer, spielerfreundlicher Transfer-Absatz (Vorbereitung/Immersion).
4) core/sl-referenz.md — Transfer-Beat als SL-Notiz direkt bei den HUD-Frames.
5) gameplay/kampagnenstruktur.md — Chronopolis-Schleuse + Schleusen-Debrief hinzufügen (Eintritt/Return/Erlösung).
6) systems/gameflow/speicher-fortsetzung.md — Savepflicht in Schleusenmoment dramaturgisch aufladen (Textbaustein).
```

