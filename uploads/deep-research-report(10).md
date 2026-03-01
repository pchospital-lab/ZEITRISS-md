# Zeitriss: Rift-Ops „handfest“ machen ohne Matrix-Vibe

## Repo-Gegencheck & Umsetzungsstatus (Repo-Agent, 2026-03-01)

Der Report wurde gegen Runtime- und Wissensmodule gegengeprüft. Der Befund
"freischwebende Rift-Semantik" + "Kabel als Generalschlüssel" ist valide und
wurde als chirurgischer Patch in den SSOT-Modulen nachgezogen:

- `gameplay/kampagnenstruktur.md`: neuer **Rift-Op Interface Contract**
  (Zeitmarker/Anker/Node/Schnittstelle/Signalpfad/Zeithack-Guard).
- `systems/toolkit-gpt-spielleiter.md`: Rift-Interface-Pflicht als
  Spielleitregel ergänzt; `chrono_terminal(...)` verlangt jetzt zusätzlich
  eine benannte Ziel-Schnittstelle.
- `internal/runtime/toolkit-runtime-makros.md`: Makro-Mirror zum Toolkit
  synchronisiert.

Status: **Teilpaket umgesetzt (Rift-Physik/Interface-Gating).**
Weitere Nachschärfungen können in Folgeschritten auf Basis neuer Playtests
iterativ ergänzt werden.

## Ausgangslage im Repo

Im Repo ist der gewünschte Ton und die gewünschte Physik eigentlich bereits sehr klar angelegt – an mehreren Stellen sogar explizit als Leitplanke:

In `core/zeitriss-core.md` ist Zeitreise ausdrücklich als **Ortswechsel** formuliert (nicht als „Zeitmanipulations-Sandbox“), inklusive dem Bild vom Riss als **„Riss in der Tapete der Realität“** statt Portal/VR-Raum. Außerdem ist das HUD als **lokales** System beschrieben (AR-Kontaktlinse + Comlink; Logging/HUD läuft auch ohne Verbindung), sodass „allwissende Cloud“ nicht der Default sein muss.

In `gameplay/kampagnenstruktur.md` sind Rift-Ops als **Mystery-Casefile / Monster-Hunt** definiert, mit einer zentralen, sehr wichtigen Leitplanke: **pro Rift-Op genau ein Zeit-Marker** (Echo/Loop/Phasenverschiebung), und ansonsten bodenständige Ermittlung, Jagd, Konfrontation. Dazu steht dort auch bereits ein **Physicality-/Voice-Lock**: Scans/Hacks/Comms brauchen greifbare Hardware (Linse/Sensor/Kabel/Relais/Terminal) und es soll **keine disembodied UI / VR / Digitalraum**-Erzählung geben.

In `characters/hud-system.md` und `systems/toolkit-gpt-spielleiter.md` wird das „Hardware-Toast“-Prinzip unterstützt: eine Tech-Aktion ist idealerweise immer an **ein konkretes Gerät** gebunden (Scanner, Relais, Terminal, Kabel etc.).

Wenn es trotz dieser SSOT-Leitplanken in Rift-Ops noch in eine **„Matrix“-Anmutung** (entity["movie","The Matrix","1999 film"]) und in „Techniker steckt Kabel in jeden Spalt“ driftet, ist das kein Grundsatzproblem deines Spiels – es wirkt eher wie ein **zu grob geschnittener Gating-Mechanismus** (Hardware ja/nein), der noch nicht sauber definiert, *was* überhaupt ein glaubwürdiger Anschluss-/Zielpunkt ist.

## Was im neuesten Playtest sichtbar wird

Im referenzierten Showcase-Playtest (`internal/qa/evidence/playtest-2026-03-01/showcase-5er-rift-boss-sonnet-full.md`) treten zwei Muster gleichzeitig auf:

Erstens: **Semantik-Drift** bei den operativen Begriffen. Als Spieler:in kannst du zwar hören/lesen, dass es „Anker“, „Nodes“, „Zeit“ und „Störung“ gibt – aber es fehlt ein *nachvollziehbares, wiederholbares Innenleben*:  
Was ist ein „Anker“ in dieser Szene *konkret* (Objekt, Ort, Person, ITI-Einstiegspunkt, Resonanz-Fokus, Return Window)? Was ist ein „Node“ *physisch* (Schaltkasten, Relaispunkt, Gerät, Körper-Interface, Funkmast)? Wie verhält sich das zum Zeit-Marker (Echo/Loop/Phasenversatz)?  
Das Ergebnis ist genau dieses „freischwebende“ Spielgefühl: das System sagt „es gibt X“, aber der/die Spieler:in kann es nicht sauber in der Szene „greifen“.

Zweitens: **Kabel als universeller Generalschlüssel**. Weil „alles nur mit Kabel/Relais“ gefordert ist, entsteht die (im Playtest dann auch genutzte) Abkürzung: „Kabel irgendwo rein“ ⇒ „wir sind im System“. Das ist paradox: Du hast das Matrix-Gefühl bekämpft, aber ein neues „Meta-Interface“ geschaffen, das wieder so wirkt wie „Digitalraum überall“ – nur diesmal als *Kabelmagie*.

Das ist exakt der Punkt, den du beschreibst: realistischer als „Funk überall“ ist es zwar, aber „Kabel in Riss der Wand“ ist als World-Physics genauso unplausibel wie „Techniker hackt die Zeit“.

## Ursachenanalyse

Die Drift wirkt (repo-intern) weniger wie „falscher Stil“ – eher wie drei fehlende/zu weiche Definitionen, die Rift-Ops besonders stark treffen:

Der Begriff **Anker** ist semantisch überladen. Ihr nutzt (mindestens) „Insertion Anchor (IA)“, „Return Window (RW)“, „Case-Anchor (Person/Ort/Objekt)“ und als Spielgefühl zusätzlich „Zeitanker/Resonanzanker“. Wenn in der Szene „Anker“ gesagt wird, ist nicht automatisch klar, welche dieser Bedeutungen gemeint ist. In `gameplay/kampagnenstruktur.md` stehen IA/RW als konkrete Begriffe; gleichzeitig werden Rift-Briefings als „Anchor + Auftragstyp“ beschrieben. Das sind zwei verschiedene „Anchor“-Schienen, die im Moment Spieler-seitig nicht sauber auseinandergehalten werden.

Der Begriff **Node** ist als Gamer-Wort stark „netzwerkig“. Selbst wenn er in einem Noir-Lexikon intern als „Schaltpunkt“ gedacht ist: *Node* triggert sofort „Systemraum“, „Zugriffsknoten“, „Routen“, „Backdoor“ – also genau den Vibe, den du rausdrücken willst. Das wird in Rift-Ops sichtbarer, weil Rift-Ops sowieso „mysteriöser“ sind und Spieler dann automatisch die Abkürzung „ok, das ist der abstrakte Anomalie-Layer“ nehmen.

Der **Physicality Gate** ist derzeit eher „Hardware vorhanden?“ als „Hardware + Ziel-Interface + plausibler Signalpfad vorhanden?“. Dadurch wird „ich habe ein Kabel“ zu einem universellen Token. Realistisch ist aber nicht „Kabel existiert“, sondern **„Woran ist das Kabel angeschlossen – und warum ist genau das eine Schnittstelle?“**

Kurzform: Eure SSOT sagt bereits „kein Digitalraum“ – aber es fehlt eine SSOT, die sagt: **„Rift-Ops sind kein Digitalraum, und auch nicht jedes Loch ist eine Schnittstelle.“**

## Ein kleiner chirurgischer Patch als neue Rift-Ops-SSOT

Das Ziel ist nicht, Rift-Ops „komplizierter“ zu machen, sondern die Spielwahrnehmung zu stabilisieren: weniger Freischweben, mehr Nachvollziehbarkeit – ohne eure bestehende Loop-Architektur zu zerstören.

Ich würde dafür eine sehr kleine Zusatz-SSOT einführen: **Rift-Op Interface Contract**. Der Contract ist kein neues Subsystem, sondern ein Satz von Invarianten + ein Format, das bei jedem Rift-Op-Briefing und bei jeder Tech-Aktion greift.

### Rift-Op Interface Contract: Invarianten

**Zeit-Ebene (TEMP/PSI)**
- Zeit-Marker ist **ein** benannter Effekt (Echo/Loop/Phasenversatz). Er ist ein *Phänomen*, kein „Netzwerk“.  
- „Zeithacking“ ist **nie** ein Techniker-Standardtool. Zeit-Eingriffe passieren nur über **TEMP** oder **PSI** (oder über ein Artefakt als Plot-Schwachstelle) und sind kurz, teuer, spezifisch.  
- TEMP/PSI können höchstens ein *kurzes Fenster* schaffen (z. B. 1–3 Herzschläge Stillstand), aber ersetzen nicht den physischen Zugang.

**Tech-Ebene (INT/SYS/Gear)**
- Jede Hack-/Patch-/Scan-Handlung braucht ein **Zielgerät** (Device) – entweder ein echtes Gerät, ein Kabel/Bus, ein Terminal, ein Implantat-Modul, ein Funkgerät, ein Sensorcluster.  
- Jede Tech-Handlung braucht eine **Schnittstelle (IFACE)**: Port, Service-Buchse, freigelegtes Leiterpaar/Bus, Kopplungsfläche, Antenne, optischer Sensorpfad, Körperkontakt-Modul.  
- „Riss in Wand / Spalt / beliebige Oberfläche“ ist per SSOT **keine Schnittstelle**. Ein Kabel in einen Spalt ist nur dann sinnvoll, wenn in der Szene klar etabliert wurde, dass dort **eine Leitung / ein Gerät / ein Bus** verläuft und wie der Kontakt hergestellt wird.

**Codex-Ebene**
- Codex ist nicht „Signal aus der Leere“, sondern entweder **(a)** lokal gecachte Fallspezifika (Casefile), **(b)** HQ-Link über Relais/Comms, oder **(c)** Notfallburst (kurz, riskant).  
- In Störungslagen ist „HQ-Internet“ nicht die Norm, sondern eine bewusste Entscheidung mit Preis (Noise/Heat/Risiko, begrenzte Bandbreite, Zeitfenster).

### Rift-Op Interface Contract: Spielformate

**Case Card (Spieler:innen sichtbar, 3 Zeilen, immer gleich)**
- **CASE:** Seed-ID + Epoche + Ort (kurz)  
- **Zeit-Marker:** ein Wort + 1 Satz „wie zeigt er sich?“  
- **Case-Anchor:** *physisch* (Person/Ort/Objekt) + 1 Satz „warum ist es der Fokus?“  
- **Schaltpunkte (statt Nodes):** 3–5 physische Punkte, jeweils 3 Wörter + 1 klare Funktion (z. B. „Funkgerät / Abhörpunkt“, „Sicherungskasten / Strom“, „Implantat / Handshake“)

**Tech Beat (bei jeder relevanten Tech-Aktion; 1 Satz pro Feld)**
- **DEVICE:** womit macht der Techniker es?  
- **IFACE:** woran dockt er an – und wie?  
- **MEDIUM:** Kabel / Induktion / Optik / Funk / Körperkontakt  
- **LIMIT:** welche Störung/Ära begrenzt das gerade?  
- **OUTCOME:** was genau ist das Ergebnis (konkret, nicht „Zugriff auf alles“)

Wenn du nur das einziehst, verschwinden zwei Dinge fast automatisch:
- „Node“ wird zu „Schaltpunkt“ = physisch, lokalisierbar, checkbar.
- „Kabel“ ist nicht mehr der Schlüssel, sondern nur ein Medium, das eine IFACE braucht.

## Konkrete Repo-Änderungen zum Copy-Paste für Codex

Unten sind Copy-Paste-Blöcke, die du als Aufgaben oder direkte Einfügungen in dein Repo geben kannst (z. B. über entity["company","GitHub","code hosting platform"] + Codex).

### Änderung in `gameplay/kampagnenstruktur.md`

Füge unter dem Rift-Abschnitt (dort wo „Briefing-Baukasten für Rift-Ops“ / „Physicality-/Voice-Lock“ bereits steht) eine neue Untersektion ein:

```md
## Rift-Op Interface Contract (SSOT)

Rift-Ops sind Mystery-Casefiles mit genau **einem** Zeit-Marker. Damit sie sich nie wie ein
„Digitalraum“ anfühlen, gilt:

- Ein Zeitriss ist **kein Netzwerk**. Er ist ein physischer Riss + ein Phänomen (Zeit-Marker).
- Tech-Aktionen brauchen immer: **Zielgerät + Schnittstelle (IFACE) + Medium**.
- Ein Spalt/Riss in Material ist **keine Schnittstelle**, außer es wurde in der Szene als Leitung/Gerät
  etabliert (sichtbares Kabel, Bus, Terminal, Implantat, Antenne).

### Case Card (immer sichtbar, 3–5 Zeilen)

Beim Briefing und nach jedem Twist zeigt das HUD eine Case Card, damit Spielende immer wissen,
„woran sie gerade sind“:

CASE: <Seed-ID> · <Epoche> · <Ort kurz>
ZEIT-MARKER: <Echo|Loop|Phasenversatz|...> — <1 Satz: wie zeigt er sich?>
CASE-ANCHOR: <Person|Ort|Objekt> — <1 Satz: warum ist das der Fokus?>
SCHALTPUNKTE: 
- A: <physischer Punkt> — <Funktion/was kann man dort tun?>
- B: <physischer Punkt> — <Funktion>
- C: <physischer Punkt> — <Funktion>
(optional D/E)

Begriffe:
- CASE-ANCHOR ist der Fokus der Mission (Person/Ort/Objekt), nicht der IA.
- IA/RW bleiben reine Einsatz- und Rücksprungbegriffe.
- „Schaltpunkt“ ersetzt „Node“ im Spielertext.
```

Warum hier? Weil `kampagnenstruktur.md` sowieso schon die Rift-Op-SSOT ist, und du keine zweite Wahrheit erzeugen willst.

### Änderung in `characters/hud-system.md`

Ergänze im Abschnitt, wo „Terminal oder Hardline suchen … Relay koppeln … Jammer“ vorkommt, eine harte Definition, was als Hardline/Interface zählt:

```md
## IFACE-Regel (Hack/Scan/Comms bleiben physisch)

Eine Tech-Aktion ist nur dann zulässig, wenn ein **IFACE** in der Szene benannt ist.

Gültige IFACE-Beispiele:
- Terminal-Port / Service-Buchse / Wartungsklappe
- freigelegtes Leiterpaar / Patchpanel / Bus-Schiene / Steckverbinder
- Antenne / Funkgerät / Empfängermodul (für Funk-Analyse)
- Implantat-Modul (Deckerbuchse, cranial port etc.) **mit Körperkontakt**
- optischer Sensorpfad (Kamera/Laserbarriere) für „Optik-Hack“ (Signal abgreifen/manipulieren)

Nicht gültig:
- „Kabel in einen Spalt / Riss / Wand“ ohne etablierte Leitung oder Gerät
- „Ich logge mich in den Riss ein“
- „Zugriff auf alles“ ohne Zielgerät

HUD-Toast-Format bei Tech-Aktionen:
DEVICE: <Tool>
IFACE: <Ziel + Kontaktart>
MEDIUM: <Kabel|Induktion|Optik|Funk|Körperkontakt>
LIMIT: <Störung/Ära>
OUTCOME: <konkret>
```

Das ist die zentrale „Anti-Kabelmagie“-Schraube: Nicht Kabel verbieten – sondern **Kabel entwerten**, wenn kein IFACE existiert.

### Änderung in `systems/toolkit-gpt-spielleiter.md`

Hier würdest du die Leitplanken für die generierende SL („Runtime“) nachschärfen, damit Rift-Ops nicht in Node-/System-Vokabular kippen. Ergänze eine kurze „Guard“-Sektion:

```md
## Rift-Ops Guard: kein Digitalraum, keine Node-Sprache

- Verwende im Spielertext **nie** „Node“. Nutze „Schaltpunkt“, immer mit physischer Beschreibung.
- Verwende keine VR-/Netzraum-Sprache („eintauchen“, „Systemraum“, „Matrix“, „Innenraum aus Code“).
- Jede Tech-Aktion muss einen IFACE benennen. Fehlt IFACE, dann ist die Aktion ein „Suchen/Spur“-Beat
  (z. B. Leitung finden, Gerät lokalisieren, Buchse identifizieren).

Rift-Ops: Zeit-Marker = 1. Keine zusätzlichen Zeitmechaniken außerhalb dieses Markers.
Zeit-Eingriffe sind nur über TEMP/PSI/Artefakt und immer kurz + teuer + spezifisch.
```

Optional (aber sehr wirksam) wäre zusätzlich eine „Autokorrektur“: Wenn ein Prompt „Node“ enthält, wird es durch „Schaltpunkt“ ersetzt und es muss ein physischer Punkt beschrieben werden.

### Änderung in `core/spieler-handbuch.md`

Hier ist die Spielerperspektive entscheidend. Ergänze im Glossar eine klare Dreiteilung, damit „Anker“ nicht mehr schwebt:

```md
## Glossar-Ergänzung: Anker vs IA/RW vs Schaltpunkt

- IA (Insertion Anchor): Einstiegspunkt des Teams in der Mission.
- RW (Return Window): Rücksprungfenster – wird am IA (oder Alt-Anchor) armiert.
- Case-Anchor: Der Fokus der Mission (Person/Ort/Objekt) – „woran hängt der Fall?“
- Schaltpunkt: Ein physischer Punkt/Gerät, an dem Tech-Handlungen möglich sind (Terminal, Leitung, Implantat, Antenne).
- Zeit-Marker: Ein einzelnes Zeitphänomen (Echo/Loop/Phasenversatz), das die Rift-Op färbt – nicht mehr.
```

Damit kann ein:e Spieler:in jederzeit die Frage beantworten: „Welche Art von Anker ist gemeint?“ – und genau das löst das Freischweben.

## Beispielhafte Reparatur der Problemstellen im Showcase

Damit Codex (oder du) sofort sieht, wie sich das „handfester“ anfühlen soll, hier zwei konkrete „Before/After“-Muster, die du 1:1 als Stilreferenz nutzen kannst.

### „Kabel in die Wand“ → „Schnittstelle finden“ (gleiche Spielhandlung, andere Physik)

**Problematische Lesart:** Kabel = universeller Eintritt in ein System.

**Handfeste Rift-Op-Lesart:** Kabel ist nur das Medium. Erst IFACE macht es real.

**After (Stilvorlage):**
- Der Techniker findet *erst* einen plausiblen Träger: Feldtelefonleitung, Strombus, Wartungskasten, Funkgerät, verstecktes Relais, Implantat.
- Dann wird die Kontaktart beschrieben: Klemme, Spleiß, Induktionsclip, Serviceport.
- Ergebnis ist eng: „du bekommst dieses Signal/ diese Kontrolle“, nicht „alles“.

Beispieltext (kurz, filmisch, ohne Technikporno):

> Du findest den Spalt im Mauerwerk – aber da ist kein „Port“. Was du *siehst*, ist etwas anderes:  
> Hinter der abgeplatzten Stelle läuft ein dünnes, altes Leiterpaar entlang, improvisiert nachgerüstet, frisch – nicht aus dieser Epoche.  
> **DEVICE:** Feld-Analyzer am Comlink.  
> **IFACE:** Induktionsklemme auf das freigelegte Leiterpaar.  
> **MEDIUM:** Kabel (kurz, geschirmt).  
> **LIMIT:** Störung frisst Funkbandbreite, aber Kupfer trägt noch.  
> **OUTCOME:** Du bekommst eine *einzige* Linie: ein gepulstes Steuersignal, das alle 12 Sekunden wiederkehrt – genug, um es zu spiegeln oder zu stören, nicht genug, um „das System“ zu besitzen.

Wichtig: Dadurch bleibt dein „kein Matrixraum“ stabil. Es gibt kein „System“, nur **Signale + Geräte**.

### „Pharao hacken“ → „Cybermodul / Buchse / Körperkontakt“ (dein Beispiel)

Du hast den richtigen Instinkt: Wenn ein historischer Akteur „hackbar“ wirkt, dann nur, weil er **ein konkretes technisches Artefakt am Körper** hat (Modul, Buchse, Implantat). Das ist ein starker, handfester Reveal – und viel befriedigender als „ich hacke eine Person / die Zeit“.

**After (Stilvorlage):**
- Erst Identifikation: „Da ist eine Buchse / Narbe / Kontaktplatte.“
- Dann Kontaktzwang: Hands-on, Risiko, Wachsamkeit.
- Dann Scope: „Modul X“ statt „Person“.

Beispieltext:

> Unter der Goldkante am Schädel sitzt ein dunkler Ring, zu sauber für Schmuck – eine Buchse, fast wie eine alte Decker-Schnittstelle, nur rituell kaschiert.  
> **DEVICE:** Kontaktstift + Kurzpatch aus deinem Kit.  
> **IFACE:** Buchse am Implantat (Körperkontakt, du musst nah ran).  
> **MEDIUM:** direkter Kontakt, kein Funk.  
> **LIMIT:** Störung macht Remote unmöglich; nur Hands-on geht.  
> **OUTCOME:** Du liest *nur* den Statuspuffer des Moduls (z. B. „Befehlssperre aktiv / Sicherheitsflag“). Mehr braucht einen zweiten Schritt – und kostet Zeit.

### Zeithacking sauber einhegen, ohne es zu töten

Dein „chirurgischer Patch“ ist kompatibel mit der SSOT, wenn du ihn so formulierst:

- TEMP/PSI geben kein „Hacken im Äther“, sondern **ein kurzes Ausführungsfenster**, in dem eine ohnehin vorbereitete, physisch verankerte Tech-Handlung „perfekt“ durchgeht (z. B. 2 Sekunden Stillstand ⇒ exakt ein Datensatz wird geschrieben, bevor das IDS tickt).
- Voraussetzung bleibt: Der Techniker ist bereits *im System*, aber „im System“ heißt hier: **am Terminal / am Bus / am Relais**, nicht in einem digitalen Raum.

Formuliersatz für die Repo-SSOT (kann in Toolkit/Handbuch):

> TEMP/PSI kann Zeit *kurz* glätten (1–3 Herzschläge), aber ersetzt nie IFACE. Es macht den Moment präzise – nicht die Reichweite grenzenlos.

## Ergebnis: Was sich dadurch im Spielgefühl ändert

Spielende können jederzeit in einem Satz sagen:
- „Unser **Case-Anchor** ist X, weil …“
- „Der **Zeit-Marker** ist Y, er zeigt sich so …“
- „Unsere **Schaltpunkte** sind A/B/C, und dort können wir konkret …“

Und der Techniker hat weiterhin Spotlight – aber nicht mehr als „Allzugriff“, sondern als **Spezialist für: Schnittstellen finden, Flüsse stören, Module patchen, Relais bauen**. Das ist realistisch, vorstellbar, und fühlt sich wie Agentenarbeit an, nicht wie ein allgegenwärtiger Digitalraum.

Wenn du diese sechs Blöcke einziehst, ist das kein Umbau, sondern wirklich ein *kleiner chirurgischer Patch* – aber er trifft genau die Stelle, an der Rift-Ops aktuell „freischwebend“ werden: fehlende Trennung zwischen **Phänomen (Zeit)** und **Interface (Tech)**.