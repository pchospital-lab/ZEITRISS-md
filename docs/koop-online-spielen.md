---
title: "Koop & Online zusammen spielen"
version: 1.3.0
tags: [guide]
---

# ZEITRISS zusammen spielen — lokal am Tisch, und optional im Chat

Dieser Leitfaden beschreibt, **wie man ZEITRISS gemeinsam spielt** — vor allem
lokal am selben Rechner, mit Betreiber und Gästen oder einfach am geteilten
Terminal. Zusätzlich lässt sich dasselbe Prinzip über einen geteilten Chat
(z. B. Discord) ausprobieren. Es braucht **keinen zentralen Server**, keine
Registrierung und keine zusätzliche App zum Herunterladen — nur den
bereits beschriebenen ZEITRISS-Terminalclient (und für den Chatversuch
eine ohnehin vorhandene Chat-Plattform). Alles läuft über die eine Sache,
die du sowieso schon hast: **deinen Spielstand als JSON.**

> **Kurz gesagt:** Dein persönlicher `!save`-JSON enthält den zuletzt
> gespeicherten Stand deiner Figur. Nach einem abgeschlossenen Abschnitt
> nimmst du ihn mit und importierst ihn auf einem anderen eingerichteten
> ZEITRISS-Rechner. Das ist keine Garantie gegen Datenverlust und kein
> vollständiges Community-Backup.

---

## Zwei Wege: lokaler Terminal-Client und Chat-Multiplayer (optional)

Der normale Produktweg ist der **lokale Terminalclient** (`python3 scripts/
mmo_sim.py`, Spieleranleitung: [spielerstart.md](spielerstart.md),
Betriebsdoku: [mmo-sim.md](mmo-sim.md); Start/Bedienung/Budget-Gate live
geprüft; der abgenommene lokale R4-Referenzlauf umfasst fünf Figuren in
Duo und Trio mit je zwei geschlossenen Runden, fünf geladene Endsaves und
eine wirksame Duo-Folgeaktion. Aktueller Stand und Grenzen: [Terminalstatus](terminal-status.md); historischer LA1-Testlauf
(3/5 Figuren, 2026-10-13): [mmo-sim.md § LA1](mmo-sim.md#la1--live-alltagsabnahme-2026-10-13)):
Solo oder mit mehreren Menschen an **einem** Gerät
(geteiltes Terminal, eigener Eingabeprompt je Zug), mit freiwilligen
KI-Spieler-Personas statt/zusätzlich zu echten Mitspielern. KI-SL,
NSCs/In-Game-Charaktere und Spieler-Personas sind dabei drei verschiedene
Dinge: die KI-SL leitet immer; eine Spieler-Persona ist ein eigener,
freiwillig entscheidender simulierter Mitspieler mit eigener Figur, kein
NSC und kein automatischer Lückenfüller. „Ohne weitere Menschen" ist
normales Solo mit möglichen KI-Mitspielern am selben Terminal — ein
ausdrücklich gestarteter, separat dokumentierter Labormodus ganz ohne
anwesenden Menschen ist davon zu unterscheiden. Private Tische bleiben 1–5
Spieler inklusive Leader, Menschen und KI-Personas gemischt; jeder Mensch
wählt/erschafft/importiert seine eigene Figur.

Zusätzlich, nachgeordnet, beschreibt dieser Leitfaden weiter unten den
**Chat-/JSON-Weg**: Jeder spielt auf seiner eigenen Plattform, trifft sich
über einen geteilten Chat (z. B. Discord) und postet `!save`-JSON-Blöcke.
Das bleibt technisch der breiter erprobte Weg, ist für das Produktziel aber
der nachgeordnete, optionale Versuch — kein Ersatz für den lokalen
Terminalweg.

Eine bekannte, bereits spielende Persona kann über den Terminalclient einer
ausdrücklichen Einladung zu einem **gemeinsamen Level-1-Frischstart**
zustimmen, ablehnen oder pausieren — nimmt sie an, erschafft sie einen
ZUSÄTZLICHEN eigenen Chrononauten über denselben regulären
Erschaffungsdialog wie ein Mensch; ihre bisherige Figur, die Community und
fremde Persona-Daten bleiben davon unberührt. Teilnehmergedächtnis
(„wir kennen uns als Mitspieler") und Figurenwissen (In-World-Geheimnisse
der alten Figur) sind dabei getrennt — Letzteres wird nicht automatisch in
die neue Figur übernommen.

**Zum LA1-Testlauf (2026-10-13):** Die Figurenerschaffung mit echter
KI-Spielleitung wurde mit fünf simulierten KI-Personas angespielt (3/5
real abgeschlossen) — das ist ein automatisierter Testlauf mit
KI-Personas, **kein** fünfköpfiger unabhängiger Menschentest und **kein**
LAN-/Netzwerk-PASS. Ein vollständiger gemeinsamer Abschnitt über zwei
aufeinanderfolgende Spielabschnitte (inkl. Speichern/Fortsetzen über
mehrere Prozessstarts) wurde in diesem Lauf **nicht** abgeschlossen;
dieser Leitfaden macht dazu keine Erfolgsaussage. Details:
[mmo-sim.md § LA1](mmo-sim.md#la1--live-alltagsabnahme-2026-10-13).

**Natives LAN-/Remote-Mitspielen über den Terminalclient ist kein aktives
Produktziel (seit der Zielgrenze vom 8. November 2026)** — die bisherige
Chat-/Bildschirm-/Voice-Nutzung unten bleibt dafür bewusst der aktuelle Weg
für „gemeinsam über das Netz". Ein lokaler Fokuswechsel am geteilten
Terminal ist kein „online verbunden". Portabilität (derselbe Save läuft auf
jeder passenden Plattform weiter — zum Beispiel nach Export und Import auf
einem anderen eingerichteten ZEITRISS-Rechner) ist dabei etwas anderes als
Netzwerksynchronisation (mehrere Geräte live über ein Netz verbunden) — der
portable Save ersetzt keinen Netzwerk-Join, und ein Netzwerk-Join ist hier
kein Lieferziel.

**Ergebnisstufe LA1 (2026-10-13): `LIVE_ASSISTED_PARTIAL`** — notwendige
Betreiberhilfen bei der Figurenerschaffung, Kernlauf über zwei Abschnitte
nicht erreicht. Das ist keine Endnutzer-Gesamtabnahme des Terminalclients
und keine Aussage zum Chat-/JSON-Weg oben, der unabhängig davon der breiter
abgenommene Weg bleibt.

---

## Lokal mit Betreiber und Gästen am Tisch

Neben dem Chat-/JSON-Weg unten und dem einfachen „ein Gerät, `registrieren`"-Weg
aus [Spielerstart](spielerstart.md) gibt es einen dritten lokalen Weg: einen
**Tisch** mit Betreiber und Gästen auf **einem** Rechner. Er ist bewusst roh
(POSIX-Named-Pipes, kein fertiges Gast-UI) und für **Linux (Mint)** gedacht.
**Windows** ist kein Ziel. **macOS** ist wegen der gemeinsamen POSIX-Basis
eine mögliche, aber ungeprüfte Nebenkompatibilität ohne Laufzusage.

### Grundidee

Ein **einziger** Python-Prozess, gestartet vom Betreiber, hält den ganzen Tisch:
den Betreiber selbst **und** jeden angeschlossenen Gast als eigene, intern
verdrahtete Sitzung. Ein Gast läuft **nicht** in einem eigenen
`scripts/mmo_sim.py`-Prozess — er bedient seine Sitzung über zwei lokale Named
Pipes (FIFOs), die der Betreiber beim Start angibt. Ein Gast braucht dadurch
**keinen** eigenen Host-/Modellstack; er sieht dasselbe Hauptmenü wie ein
normaler Start, nur über die Pipes.

### Schritt 1 — Betreiber startet den Prozess

Der Betreiber braucht je einen `in`/`out`-FIFO-Pfad pro Gast und — sobald er
**selbst mitspielt** — einen Kontrollkanal für `/stop`. **Eine eigene Figur
braucht der Betreiber nicht:** Der reine Betreiber ohne Figur, der nur die
KI-Spielleitung hält und den Tisch führt, ist der **Normalfall**. Eine eigene
Figur ist nur Voraussetzung des bewusst **mitspielenden** Hosts (dann ist der
Kontrollkanal Pflicht, siehe unten). Die FIFOs müssen **nicht** von Hand
angelegt werden — der Launcher legt fehlende Named Pipes selbst an und bricht
ehrlich ab, falls unter einem Pfad schon eine normale Datei liegt.

```bash
# Fenster 1 — Betreiber
python3 scripts/mmo_sim.py \
  --participant betreiber1 \
  --data-dir ./internal/mmo_sim_data \
  --operator-control-fifo /tmp/zr-ctl.fifo \
  --guest-terminal gast1:/tmp/zr-gast1-in.fifo:/tmp/zr-gast1-out.fifo \
  --guest-terminal gast2:/tmp/zr-gast2-in.fifo:/tmp/zr-gast2-out.fifo
```

- `--participant` ist die eigene Teilnehmer-ID des Betreibers.
- `--data-dir` ist die Datenwurzel; `run`/`states` werden daraus abgeleitet
  (`--run-dir`/`--states-dir` überschreiben sie bei Bedarf einzeln). Jeder
  angeschlossene Gast bekommt automatisch eine **private** Unterwurzel für seine
  eigene Figur, teilt aber dieselbe gemeinsame Tisch-/Admissionswurzel.
- `--operator-control-fifo PFAD` ist der getrennte Kontrollkanal für `/stop` und
  `/zuschauer`. Sobald der Betreiber **selbst** mitspielt und seine Züge über das
  geteilte Betreiber-Terminal eingibt, ist dieser Kanal Pflicht — sonst lehnt der
  Rundenstart ab, damit `/stop` nicht mit einem Spielzug kollidiert.
- `--guest-terminal GAST_ID:IN_FIFO:OUT_FIFO` verdrahtet eine Gast-Sitzung
  (wiederholbar, einmal pro Gast).

### Schritt 2 — Jeder Gast öffnet sein Fenster (gleicher Rechner)

Jeder Gast bekommt **ein** zusammengehöriges Fenster mit der dünnen
Anschlusshilfe `scripts/zeitriss-gast-terminal.sh`. Sie verbindet nur die beiden
FIFO-Kanäle, die der Betreiber in Schritt 1 angegeben hat — Eingabe und Anzeige
im selben Fenster, mit einer Kopfzeile (Identität, Modus, Figur-Hinweis, Hilfe,
nächster Schritt, Ende). Sie startet **keinen** eigenen Host und ruft **kein**
Modell; die ganze Spiel-/Save-/Admissionslogik bleibt im einen Betreiberprozess:

```bash
# Gast 1 — ein Fenster für Ein- und Ausgabe
scripts/zeitriss-gast-terminal.sh gast1 /tmp/zr-gast1-in.fifo /tmp/zr-gast1-out.fifo
```

Analog für Gast 2 (eigenes Fenster, eigene FIFOs). Die eingeblendeten Fragen,
Bestätigungen und Empfängerzeilen erscheinen in genau diesem Fenster, **bevor**
der Gast antwortet.

Wer lieber ohne Hilfsskript arbeitet, kann weiterhin direkt mit `cat` plumben —
eine Named Pipe lässt sich nicht in einem einzigen `cat` zugleich lesen und
beschreiben, daher Lese- und Schreibseite getrennt:

```bash
cat /tmp/zr-gast1-out.fifo          # Ausgabe mitlesen (läuft dauerhaft)
cat > /tmp/zr-gast1-in.fifo         # Eingabe tippen (eine Zeile pro Enter)
```

Beide Wege sind gleichwertig; die Anschlusshilfe ist nur das bequemere
Ein-Fenster-Bündel derselben rohen Kanäle.

### Schritt 3 — Eine Figur pro Gast an den Tisch bringen

Der normale Weg läuft über das nummerierte **`charaktere`**-Menü im eigenen
Gast-Fenster — rohe Befehle oder interne IDs musst du dir **nicht** merken, du
wählst über die angezeigten **Nummern**:

- **Gast hat schon einen Save:** `charaktere` → `[2]` (**Importieren**), wie in
  [Spielerstart](spielerstart.md) beschrieben.
- **Gast hat noch keine Figur** (nutzt die Spielleitung des Betreibers, macht
  selbst **keine** Modellaufrufe). **Voraussetzung:** der Betreiber muss
  vorher **einmal** `tisch` → `[5]` (**Tisch anbieten**, s. Schritt 4 — auch
  **figurfrei** möglich) ausgeführt haben, sonst ist die Betreiberauswahl
  unten leer:
  - Gast: `charaktere` → `[4]` (**Gast-Erschaffungsanfrage an Betreiber
    stellen**) und wählt den Betreiber aus der angezeigten Auswahl. Ist die
    Liste leer, nennt der Client die fehlende Voraussetzung und den
    nächsten Schritt (kurz mit dem Betreiber abstimmen, danach erneut
    aufrufen) — eine rohe Betreiber-ID bleibt zusätzlich als Expertenweg
    möglich, ist aber nicht der normale Weg.
  - Betreiber: `charaktere` → `[4]` (**Gast-Erschaffungsanfragen entscheiden**),
    wählt die Anfrage per Nummer und nimmt sie mit `[1]` an (oder lehnt ab).
  - Gast: `charaktere` → `[5]` (**Eigenen Erschaffungsdialog fortsetzen**) — der
    eigentliche Erschaffungsdialog. Diese Zeile erscheint erst nach der eigenen
    `[4]`-Anfrage.

Dieselben Schritte gibt es optional als **Experten-Wortbefehle**
(`gast-erschaffung-anfragen`, `-annehmen`/`-ablehnen`, `-dialog`, zum Verwerfen
eines noch unangenommenen Entwurfs `-abbrechen`, zum Stoppen einer freigegebenen
offenen Erschaffung `-stop`). Sie sind nur Abkürzungen für Geübte und für den
normalen Spielweg nicht nötig.

### Schritt 4 — Tisch anbieten, finden, annehmen

Auch der Tisch läuft über das nummerierte **`tisch`**-Menü. Zeile `[1]`–`[4]`
(Suchen/Anfragen/Zurückziehen/Status) ist für jeden erreichbar; eine zweite,
**nur für den Betreiber sichtbare** Zeile bietet `[5]` Tisch anbieten, `[6]`
Anfrage annehmen, `[7]` Anfrage ablehnen, `[8]` Tisch starten, `[9]`
Zuschauer/Verlauf:

- Betreiber: `tisch` → `[5]` (**Tisch anbieten**) und vergibt einen Tischnamen.
- Jeder Gast: `tisch` → `[2]` (**Anfragen**) mit diesem Tischnamen (bindet
  automatisch die eigene Figur des Gasts — kein stiller Fremdimport).
- Betreiber je Gast: `tisch` → `[6]` (**Anfrage annehmen**) — kein stilles
  Auto-Annehmen, der Betreiber nimmt jede Anfrage bewusst an.
- Betreiber: `tisch` → `[8]` (**Tisch starten**).

Für Geübte gibt es dieselben Aktionen optional als Wortbefehle
(`tisch-anbieten`, `tisch-suchen`, `tisch-anfragen`, `tisch-annehmen`,
`tisch-start`); sie sind nicht Teil des normalen Spielwegs.

### Schritt 5 — Spielen: wer tippt wann

Betreiber: `tisch` → `[8]` (Tisch starten; Wortalias `tisch-start`). Spielen
mehrere Menschen mit, **beantwortet jeder
weitere Mensch seine persönliche Beitritts-/Zustimmung an seinem eigenen Kanal
selbst** — seine Taste auf seinem eigenen Terminal entscheidet, der Betreiber
tippt keine fremde Zustimmung an seiner Tastatur und sein Prozess blockiert auch
nicht auf der fremden Tastatur. (Die Beitritts-/Zustimmungsfrage wird jetzt
sichtbar in den eigenen Ausgabekanal des Gastes gespiegelt — der Gast antwortet
auf die in seinem Fenster eingeblendete Frage, nicht auf Zuruf.) Der
erste angenommene Mensch spielt als Leader;
jeder weitere Mensch steigt über seine **eigene** Zusage ein. Bleibt eine
ausdrücklich gewünschte Zusage aus, startet nicht stillschweigend eine
verkleinerte Runde.

Danach läuft der normale Rundenablauf. Vor jedem Prompt steht eine
Empfängerzeile: sie nennt, wessen Zug ansteht. Jeder Mensch tippt in seinem
**eigenen** Fenster. Eingabekollisionen auf demselben Kanal (z. B. während
der Betreiber kurz über den Kanal eines Gastes eine Abschlusskarte oder ein
Untermenü bedient) verhindert die eingebaute Claim-Koordination — genau ein
zuständiger Leser je Kanal zur gleichen Zeit, kein getrenntes Fenster allein
reicht dafür aus. Jeder Gast sieht die für ihn bestimmte öffentliche SL-Vorgeschichte
und neue öffentliche Ausgaben in seiner eigenen Ansicht, auch wenn vorher ein
anderer Gast gehandelt hat. Mit `/stand` sieht die gerade tippende Person ihren
eigenen Stand, `?`/`/hilfe` zeigt die Steuerzeilen, ohne einen Zug zu verbrauchen.

### Schritt 6 — Regulär abschließen und den eigenen Stand mitnehmen

Der normale Abschluss läuft über das HQ, **bevor** es um Stop/Abbruch geht:

- Im passenden **HQ-Kontext** fordert der menschliche Leader den Abschluss mit
  `!save` (bzw. `!speichern`). Die Spielleitung nimmt die gültigen **persönlichen
  Ergebnisse** jeder Person an — jeder Gast behält seinen eigenen Fortschritt.
- Eine **optionale Endnotiz** ist ausdrücklich eine **eigene lokale Notiz** der
  jeweiligen Person: kein gemeinsamer Spielstand und keine Modellaktion.
- Direkt nach dem Abschluss zeigt der Client jedem Gast **in seinem eigenen
  Fenster** eine persönliche, nummerierte **Abschlusskarte**: `[1]` den eigenen
  Stand exportieren, danach zurück zu deinem vorherigen Menü (leere Eingabe
  oder `/zurueck` führt ebenfalls dorthin) — zum Hauptmenü, wenn du dort
  geparkt warst, zum Tisch-Untermenü, wenn du dort warst, oder zur
  vorherigen "Welcher Tisch?"-Frage, wenn du konkret in dieser noch offenen
  Tischfrage stecktest —, und als Gast zusätzlich einen weiteren Tisch
  suchen/beitreten. Jeder Gast bedient seine Karte selbst; der Export
  entspricht dem `charaktere` → `3`-Weg.
- So nimmt jeder Gast seinen aktuellen Stand mit. Der Export liegt als
  persönliche Save-JSON im eigenen Export-Ordner des Gastes — standardmäßig
  `<Datenablage>/guests/<GAST_ID>/exports/<GAST_ID>.json`.
  Der Client zeigt beim Export den konkreten Pfad an (`Zusaetzlich als Datei gespeichert: …`);
  dieser angezeigte Pfad führt die Mitnahme. Damit steigt dieselbe Person später wieder ein
  (Import über `charaktere` → `2`).

Der Betreiber bleibt dabei **ohne eigene Figur**. Erst nach diesem regulären
Abschluss folgen die Abbruch-/Stop-Varianten unten.

### Schritt 7 — Stop bleibt erreichbar

Während die Runde läuft, stoppt bzw. beobachtet der Betreiber jederzeit über den
getrennten Kontrollkanal:

```bash
echo "/stop" > /tmp/zr-ctl.fifo
echo "/zuschauer" > /tmp/zr-ctl.fifo
```

`/abbrechen` **am eigenen Spielzug-Prompt** (nicht über den Kontrollkanal) hat am
Tisch eine strengere Bedeutung als eine bloße Pause:

- **Vor** der gemeinsamen Abschluss-Entscheidung: echter, **endgültiger** Verwurf
  des ganzen Abschnitts — kein Fortsetzen.
- **Nach** einer bereits gewonnenen Abschluss-Entscheidung: nur noch regulärer
  Restabschluss des bereits angenommenen Fortschritts — **kein** Rückgängig.
- **Ohne** gebundenen Betreiber-Tisch (einfacher Solo-/`registrieren`-Weg ohne
  `tisch-start`): `/abbrechen` bleibt reine Pause, genau wie `/pause`.

### Schritt 8 — Ehrliches Kanalende und saubere Rückkehr

**EOF, Pause und Stop sind drei verschiedene Ereignisse** — nicht derselbe
Zustand unter anderem Namen:

- **Strg-D (EOF)** auf der Gast-Eingabeseite beendet den **Eingabe-Dispatch
  dieses Gasts**. Ein so beendeter Gastkanal wird **nicht** allein dadurch wieder
  lebendig, dass man erneut einen `cat >`-Schreiber öffnet. Zuverlässig für diese
  Etappe ist ein erklärter kontrollierter Schluss und danach ein **vollständiger
  Neustart** des Tisches — keine Sofort-Wiederanschlussgarantie an denselben
  laufenden Dispatch.
- **`/pause`** am eigenen Prompt hält die Runde kontrolliert an, ohne sie zu
  beenden.
- **`/stop`** über den Kontrollkanal und ein **bestätigter** `/abbrechen` vor der
  Abschlussentscheidung sind Betreiber-/Abschnittsende, keine bloße Pause (siehe
  Schritt 7). Ein bestätigter endgültiger Verwurf ist kein „sicher pausiert".

Der zuletzt **gespeicherte** persönliche Stand jeder Person bleibt dabei
erhalten; noch nicht gespeicherter Fortschritt ist dadurch nicht gesichert. Der
Betreiber beendet den ganzen Prozess über `beenden` im Hauptmenü; die
Gast-Sitzungen desselben Prozesses enden mit.

**Rückkehr hängt davon ab, was der Tisch zuletzt war** — es gibt **keine
pauschale `fortsetzen`-Zusage** für jede Rolle nach jedem Ende:

- **Offener, gebundener Tisch** mit denselben Identitäten, Kanälen und
  Datenwurzeln: der Betreiber nimmt ihn über `tisch-start` **derselben Bindung**
  wieder auf.
- **Geschlossener oder verworfener Tisch:** kein stilles Fortsetzen — der
  Betreiber macht ein **neues Angebot**, und jede Person bringt ihren **aktuellen
  persönlichen Save** bewusst wieder ein (Gast: `charaktere` → `2`).
- **Eigener Solo-/Persona-/Angebotsweg:** braucht einen **eigenen Host**; der
  Betreiber-`tisch-start` ersetzt ihn nicht.

### Wie viele Fenster?

| Rolle | Mindestens | Komfortabel |
| --- | --- | --- |
| Betreiber | 1 (Hauptprozess) | 2 (+1 für den Kontrollkanal `/stop`) |
| Jeder Gast | 1 (Lesen+Schreiben gemischt) | 2 (Lesen/Schreiben getrennt) |

Für Betreiber + zwei Gäste realistisch **3 bis 7 Terminalfenster** auf einem
Gerät. Wer das nicht braucht, bleibt beim einfachen `registrieren`-Weg ohne Tisch.
Mehrere Geräte im LAN sind kein aktives Produktziel (seit der Zielgrenze vom
8. November 2026).

---

## Die Grundidee

ZEITRISS speichert deinen kompletten Fortschritt in einem portablen
JSON-Block. Dieser Block ist gleichzeitig dein Charakterbogen, dein
Kampagnenstand und dein Eintrittsticket in jede Runde. Daraus ergibt sich ein
**„MMO-Feeling ohne Server":**

- Du levelst **solo** auf deiner Lieblingsplattform, wann und wie du willst.
- Wenn du Lust auf gemeinsames Spiel hast, **triffst du dich mit anderen** (z. B.
  auf einem Discord-Server) und bietest deinen Stand an.
- Ihr spielt zusammen einen Abschnitt — danach geht jeder mit seinem
  aktualisierten JSON wieder seiner Wege oder ihr macht weiter.

Der Clou: Für den persönlichen Dateiumzug ist es egal, auf welcher
Plattform jemand zuvor gespielt hat — das JSON lässt sich grundsätzlich
mitnehmen. Das ist keine universelle Regel-/Spielgarantie unabhängig vom
jeweiligen Chat-/Modell-Stack; die passenden Import- und
Regelvoraussetzungen (siehe oben) gelten weiterhin.

---

## 1. Solo zuerst — dein Charakter wächst bei dir

Richte dir ZEITRISS auf **deiner** Plattform ein (OpenWebUI, oder wo auch immer
du eine LLM-Runde mit Projektwissen laufen lässt). Spiel dich ein, mach ein paar
Missionen, finde deinen Charakter. Dein Fortschritt lebt in deinem JSON — du
bist niemandem Rechenschaft schuldig und an keine Runde gebunden.

Erst wenn du **Lust auf gemeinsames Spiel** hast, wird der Rest hier relevant.

Wie viel gemeinsames Spiel dazukommt, ist völlig offen — ZEITRISS ist bewusst
vielfältig spielbar, es gibt keinen „Normalfall". **Solo mit deinem NPC-Team
ist für sich genommen schon die vollständige MMO-Simulation** — ein ganzes
Team, eine ganze Kampagne, nur du. Von da aus geht vieles:

- Manche bleiben fast durchgehend solo und holen sich echte Mitspieler nur
  gezielt zu großen Momenten dazu — **zu** einem Boss, **zu** einem Rift — und
  spielen danach wieder allein weiter.
- Andere spielen umgekehrt fast alles online in der Gruppe, Abschnitt für
  Abschnitt, laden immer gemeinsam und wickeln HQ jedes Mal automatisch ab
  (siehe Abschnitt 5a). Erst **nach einer ganzen Episode** nehmen sie sich Zeit
  für sich allein: laden ihren Charakter solo, machen in Ruhe Feintuning im HQ
  und stecken das verdiente Geld z. B. in Chronopolis.

Beides ist gleich richtig. Koop ist kein Zwang und kein Dauerzustand, sondern
ein Andock-Punkt, den du dir nimmst, wann und so oft er dir passt.

---

## 2. Wo man sich trifft

Es gibt keinen offiziellen Treffpunkt — und das ist Absicht. In der Praxis
bilden sich **private Discord-Server** als Anlaufstellen: dort hängen Spieler ab,
posten ihren Stand und verabreden sich für Runden. Jede Community organisiert
sich, wie sie will.

Ein Discord-Server ist nur *ein* Weg. Genauso gut geht ein Gruppenchat, ein
Forum oder direkt der Messenger mit einem Kumpel (siehe
[Ganz ohne Discord](#ganz-ohne-discord)).

---

## 3. Deinen Stand anbieten

Willst du eine Runde anbieten oder in eine einsteigen, postest du deinen
**`!save`-JSON-Block** — und zwar **gleich von Anfang an**, nicht erst wenn
sich eine Gruppe gebildet hat. Das JSON ist der kanonische Weg: Episode,
Mission, Modus, Epoche, offene Rifts, Chronopolis-Stand — alles drin, für
alle im Treffpunkt sichtbar und lesbar.

Dazu passt optional ein schneller Teaser als menschenlesbare Kurzfassung.
Frei formuliert oder mit den Kurzbits aus `!bogen`. Zum Beispiel:

```
Core-Op · Episode 3 · Mission 5 (Mini-Boss in Sicht) · Epoche: Kalter Krieg
Level 6 · suche 2–3 Leute · Modus: tell
```

Oder für einen Rift-Lauf:

```
Rift-Op · Episoden-Boss-Run in Aussicht · 1 offener Rift · Level 9
suche 1–2 Leute · Modus: strict
```

Ein harter Rift, ein Level, auf das du stolz bist, ein Charakter mit
Geschichte — du kannst deinen Stand mit der Runde teilen. Prüfe vorher,
welche persönlichen Angaben und Inhalte dein Save enthält, und teile ihn
bewusst (siehe [Spielstand behalten und bewusst teilen](#8-spielstand-behalten-und-bewusst-teilen)).

> **Für Neugierige:** Ein gepostetes JSON kann man kurz in einen JSON-Viewer
> (oder einfach den Browser) werfen und nachsehen, was jemand für ein Szenario
> mitbringt — offene Rifts, spannende Epoche, ein Boss in Aussicht. So findest
> du Runden, die dich reizen, und steigst gezielt ein.

---

## 4. Zusammenkommen — die Lobby

Startet ihr als komplett neue Gruppe ohne bestehende Saves, kommt davor noch
ein Schritt: Jede Figur wird zuerst **einzeln in einem eigenen, frischen
Chat** erschaffen. Erst wenn alle Chargen-JSONs fertig sind, bringt ihr sie
gemeinsam in den einen neuen Spielchat — genau wie unten beschrieben.
Mehrere Charaktere gleichzeitig in einem Chat zu erstellen erzeugt Drift
zwischen den Figuren; darum bleibt jede Chargen ihr eigener, abgeschlossener
Chat-Abschnitt, bevor die Runde zusammenkommt.

Wenn die Runde steht, läuft das Zusammenkommen so:

1. **Alle posten ihr `!save`-JSON** in den Chat.
2. Ein Spieler übernimmt als **Leader** — er teilt seinen Bildschirm und führt
   die eigentliche ZEITRISS-Session in seinem Chat.
3. Der Leader fügt **zuerst seinen eigenen Save** ein und wartet die Antwort
   der Spielleitung ab — **der zuerst eingefügte Save setzt den
   Session-Anker** (Episode, Mission, Standort). Danach kommen die Gäste
   **einzeln nacheinander**: ein JSON einfügen, kurz die Reaktion der
   Spielleitung abwarten, dann der nächste. So bekommt jede Figur beim Eintreten
   ihren eigenen sauberen Moment, und die Runde versammelt sich Stück für Stück
   statt in einem Schwung — das läuft für die KI-Spielleitung deutlich sauberer,
   als alle Saves auf einmal hineinzukippen. Die eigenen Kampagnen der Gäste
   **pausieren** so lange und gehen nicht verloren.

Ab hier spielt ihr gemeinsam in **einem** Chat, den alle mitlesen können.

---

## 5. Spielen — strict oder tell

Bevor es losgeht, einigt sich die Runde auf einen von zwei Umgangsstilen. Das
ist eine **Absprache unter Spielern**, kein Spielbefehl — der Leader setzt sie am
Bildschirm um.

- **strict:** Jeder postet ohne weitere Absprache in den Chat, **was seine Figur
  in dieser Runde tut**. Der Leader übernimmt die Aktionen direkt. Schnell,
  chaotisch, näher am „jeder für sich".
- **tell:** Die Runde **bespricht jede Aktion** (jede „Row") gemeinsam. Der
  Leader interpretiert die Absprache und gibt sie ein. Langsamer, taktischer,
  näher am klassischen Pen-&-Paper-Tisch.

Alle sehen den Chat mit, also den kompletten Spielverlauf. Der Leader ist dabei
nur die **Hand an der Tastatur** — die Spielleitung macht die KI.

> **Aufteilen mitten in der Szene** (einer klopft vorne an, zwei schleichen
> hinten rein) ist **kein** technischer Split — das erzählt die KI-Spielleitung
> einfach parallel, im selben Chat. Ein echter Split mit getrennten Saves
> passiert nur an Abschnittsgrenzen.

---

## 5a. Vor einem Boss: kurz jeder für sich

Ein Muster, das sich für Online-Gruppen anbieten dürfte: Ihr spielt gemeinsam
Action-Abschnitt für Action-Abschnitt durch — und **kurz vor einem Boss**
(Mini-Boss um Mission 5, Episoden-Boss um Mission 10) geht noch einmal **jede
Figur für sich allein** zurück in ihren eigenen Chat, um sich vorzubereiten und
nachzujustieren: Equip, Klinik, Werkstatt, das Feintuning eben. Ein grobes
Zeitlimit von etwa 15 Minuten hält das knapp. Danach trefft ihr euch wieder in
**einem** Chat — auf dem Stand des Leaders, der zuletzt gespeichert hat — und
geht den Boss gemeinsam an.

Der Kern: Das Vorbereiten vor einem Boss ist ruhige Einzelarbeit, die niemanden
am Tisch aufhält; der Boss selbst ist der gemeinsame große Moment. Deshalb
splittet man dafür kurz auf und kommt geschlossen wieder zusammen. Das ist etwas
anderes als eine **ausgiebige gemeinsame HQ-Runde** — die ist ein eigener,
vollwertiger Spielabschnitt für sich (siehe Abschnitt 5b), kein schneller
Vor-Boss-Halt.

*(Das ist eine Idee zur Selbstorganisation, kein Spielbefehl — noch spielt
niemand real genug, um zu wissen, ob sich das so einspielt.)*

Und wer lieber zügig durchspielt, braucht diese Einzel-Vorbereitung gar nicht:
**Schnell-HQ** und **Auto-HQ** wickeln die HQ-Phase knapp und automatisch ab
(siehe [Spieler-Handbuch](../core/spieler-handbuch.md)), sodass die Gruppe
flüssig von Abschnitt zu Abschnitt weiterrattern kann, ohne stehen zu bleiben —
der Charakter bleibt trotzdem auf aktuellem Stand, und bei Bedarf lässt sich
noch per Pipe-Post etwas ins Briefing nachliefern. Beide Wege sind
gleichwertig.

---

## 5b. Das HQ ist ein eigener Schauplatz

Das HQ ist nicht bloß ein Speicherpunkt oder eine Werkstatt zwischen zwei
Missionen — **HQ erkunden** ist ein vollwertiger Spielabschnitt für sich: die
Nullzeitbar, der Club, das persönliche Quartier, das Archiv, dazu Klinik,
Werkstatt und die NPC-Crew. Ein ganzer Schauplatz zum Bespielen, ganz ohne
Chronopolis.

Darum kann eine Gruppe sich auch bewusst eine **ausgiebige gemeinsame
HQ-Runde** nehmen — anders als die schnelle Vor-Boss-Vorbereitung geht es hier
nicht ums Aufrüsten, sondern ums Miteinander: in der Nullzeitbar abhängen und
reden, sich gegenseitig ins persönliche Quartier einladen, im Archiv einem
Gerücht nachgehen, ein Verhör gemeinsam führen oder einfach die Chrononauten —
und einander — näher kennenlernen. So etwas passt gut **nach einer
abgeschlossenen Episode**, wenn Luft für Rollenspiel ist.

*(Auch das ist kein Muss: Manche Runden lieben diese ruhigen, dichten
HQ-Abende, andere rattern per Auto-HQ weiter zum nächsten Action-Abschnitt.
Beides ist ZEITRISS — das HQ trägt vom schnellen Boxenstopp bis zum ganzen
Rollenspiel-Abend alles.)*

---

## 6. Aufstieg in der Gruppe

Nach einer Mission kommt der Debrief mit Score und Level-Up. **Wichtig:** Der
Level-Up wird **vor** dem Speichern vergeben — das ist so gewollt und bleibt so
(ein Save ohne erledigten Aufstieg ist unvollständig).

Im fremd-geleiteten Multiplayer passiert dieser Aufstieg **live und sichtbar
vor der ganzen Runde**, am geteilten Bildschirm des Leaders. Das ist kein
Umweg, sondern ein **eingebautes Vertrauens-Feature**: Weil jede Figur ihre
**eine** Aufstiegswahl (`+1 Attribut` **oder** `Talent/Upgrade` **oder** `+1
SYS`) live vor Zeugen trifft, sieht die ganze Runde mit, dass alle
Charaktere regelkonform bleiben — niemand bläst still im Hintergrund Werte
auf. Verifikation durch mehrere Augen, ganz nebenbei.

- Im **tell**-Modus sagst du dem Leader deine Wahl als eine Zeile im Chat.
- Im **strict**-Modus postest du sie direkt.

Die Abrechnung (CU, XP, Level) siehst du im Debrief **bevor** du wählst. Dann
speichert der Leader — und dein aktualisierter Stand ist wieder in deinem
JSON.

---

## 7. Abschnitt beenden

Am Ende eines Abschnitts:

1. Der Leader **speichert** (`!save` im HQ) — die Spielleitung gibt **pro
   anwesender Figur einen eigenen vollständigen JSON-Block** aus.
2. Der Leader **wirft die JSONs zurück** in den Chat, jeder nimmt seinen.
3. Ihr entscheidet frei: **weiterspielen** (nächster Abschnitt, gleicher Leader
   oder neuer) oder **Wege trennen** — jeder zieht mit seinem frischen JSON
   weiter, solo oder in eine andere Runde.

Persönliche Fortschritte und Erinnerungen reisen mit. Fremde Kampagnenstände,
Auszahlungen und einzigartige Beute werden **nicht** kopiert — jeder behält
sauber seinen eigenen Stand.

---

## 8. Spielstand behalten und bewusst teilen

Bewahre deinen letzten gültigen persönlichen Save selbst auf. Eine eigene
Kopie ermöglicht die Fortsetzung vom darin gespeicherten Stand, auch wenn
eine Runde endet oder ihr den Leader wechselt. Noch nicht gespeicherter
Fortschritt ist dadurch nicht gesichert; eine beschädigte oder verlorene
Kopie lässt sich nicht allein durch ihre Portabilität wiederherstellen.

Ein Save kann persönliche Angaben und Inhalte enthalten. Teile deinen
eigenen Save bewusst; Zugangsdaten und private Erinnerungen anderer
Personas gehören nicht in eine geteilte Datei.

**Persönlicher Save, lokaler Communitybestand und getestete Sicherung sind
verschiedene Dinge.** Der Save einer Figur ersetzt nicht die Gemeinschaft
mit Persona-Identitäten, Erinnerungen, anderen Figuren sowie ihren
Auftrags- und Fortsetzungsdaten. Eine vollständige Sicherung und
Wiederherstellung dieses Verbunds ist im hier beschriebenen lokalen
Terminal-Entwicklungsstand noch nicht durchgängig nachgewiesen. Nativer
LAN-/Remote-Join ist davon nochmals getrennt.

---

## Ganz ohne Discord

Der gleiche Ablauf funktioniert überall:

- **Am Tisch:** Ein Gerät, einer leitet, ihr sprecht per Voice oder direkt im
  Raum. JSONs schickt ihr euch schnell per Messenger auf das eine Gerät.
- **Zu zweit, spontan:** Du und ein Kumpel schickt euch die JSONs per Messenger,
  spielt eine Runde auf einem Gerät, danach das aktualisierte JSON zurück. Jeder
  geht nach Hause — auch im Spiel trennen sich die Wege wieder.

Die Mechanik ist immer dieselbe: **Save posten → zusammen spielen → Save
zurück.**

---

## Mehr dazu

Die Spielmechanik hinter dem Gruppenspiel (getrennte Saves, Session-Anker,
Splits & Merges, Gruppen-Px, Tod in der Gruppe) steht im
[Spieler-Handbuch](../core/spieler-handbuch.md) unter „MMO-Feeling ohne Server"
und „Der Gameflow".


Hinweis zur Wiederaufnahme: Bricht eine Gruppenrunde genau zwischen dem Abschluss-Spielzug der Spielleitung und den Pflicht-Reflexionen ab, erntet der naechste normale Fortsetzen-Aufruf die bereits erzeugten Spielstaende automatisch (ohne neuen Spielzug) — aber nur, wenn die Antwort eindeutig und vollstaendig zur urspruenglichen Anfrage passt (Original-Input, Original-ID, vollstaendig verbucht, kein offener Fehler). Ist der Versand noch unbekannt/unvollstaendig oder die Buchung noch offen, haelt die Wiederaufnahme statt dessen kontrolliert, ohne deinen Spielstand zu veraendern. Danach (bei erfolgreicher Ernte) folgen wie bisher die erforderlichen Reflexionen der beteiligten KI-Mitspieler und der Abschluss.
