# CoreOps-Playtest: coreops-mp-tracking-0921

**Datum:** 2026-04-23 09:21
**Szenario:** CoreOps Tier-1, KI-generierte Mission (keine Vorgabe). MP-Nutzung pro Turn getrackt.
**Modell SL:** zeitriss-v426-uncut via KB `bb266c62...`
**Modell Spieler:** anthropic/claude-sonnet-4.6
**Ziel:** MP-Usage-Tracking für Straffungs-Entscheidung

---

## Turn 0 — Gruppenstart

**GRUPPE:** Spiel starten (gruppe klassisch). Wir sind 3 Spieler:
Sarah hat schon eine Mission gespielt und bringt Mara Voss
mit (Callsign SPLINTER, GES 5, INT 5, Talent Tatortanalyse).
Jonas und Kim haben letztens mitgespielt, bringen ihre
Charaktere wieder — du darfst sie neu aushandeln wenn nötig.

Briefing bitte. Core-Mission, Tier 1, Tempocom-Auftrag.

### Turn 1 — SL

# ZEITRISS

---

> *"Die Vergangenheit ist kein Museum. Sie ist ein Tatort."*
> — ITI-Handbuch, Einleitung, Seite 1

---

## ZEITRISS – Einleitung

Du bist ein Chrononauten-Agent des **Instituts für Temporale Integrität (ITI)** – der einzigen Organisation, die Zeitreisen kontrolliert, dokumentiert und gegen Missbrauch absichert. Deine Aufgabe: Zeitlinien schützen. Störungen neutralisieren. Geschichte wahren.

Das ITI operiert aus der **Nullzeit** – einem stabilen Zeitpunkt außerhalb des normalen Flusses. Von hier aus springst du in Epochen, die du nie erlebt hast, triffst Menschen, die seit Jahrhunderten tot sind, und trägst Technologie, die in deinem Einsatzgebiet als Magie gilt.

Chrononauten sind keine Helden. Sie sind Werkzeuge mit Gewissen.

Willkommen im Dienst.

---

## Gruppen-Start – Klassischer Pfad

**Drei Spieler. Ein Import, zwei Neubauten.**

Ich habe Mara Voss aufgenommen und halte ihre Werte fest. Jonas und Kims Charaktere kenne ich noch nicht als gespeicherte Saves — ich baue sie frisch nach ZEITRISS-Standard.

**Kurze Klärung vor dem Bau:**

Sarah bringt **Mara Voss (SPLINTER)** mit folgenden bekannten Werten:
- GES 5, INT 5, Talent: Tatortanalyse
- Restliche Attribute (STR, CHA, TEMP, SYS) und Equipment: **Sarah, bitte kurz ergänzen** — oder ich fülle sie sinnvoll auf (18-Punkte-Summe, keine Werte über 6).

Für **Jonas** und **Kim** frage ich:

> **Jonas:** Welche Rolle / welchen Vibe soll dein Charakter haben? (Kämpfer, Schleicher, Techniker, Gesicht, Hybrid — oder frei beschreiben.) Soll ich `generate` (Überraschung), `custom generate` (Vorgaben + Surprise) oder willst du **selbst bauen**?

> **Kim:** Gleiche Frage — Rolle, Vibe, Bauweg?

---

Alternativ: Wenn ihr **jetzt keine Zeit für Absprachen** wollt, sage einfach **„generate alle"** — dann baue ich alle drei Charaktere sofort, zeige die fertigen Bögen, und wir springen direkt ins Chargen-Save-Gate.

Mara Voss wird dabei mit sinnvollen Standardwerten aufgefüllt (Sarah kann danach korrigiere

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Mein Char ist schon fertig vom letzten Mal — STR 5, GES 4, TEMP 4, INT 3, SOC 2, WIS 3, Talent Nahkampf-Taktik. Kannst du den einfach übernehmen? Name war... ich glaub ich hab ihn noch nicht festgelegt, lass uns sagen **Ren Kaspar**. Ehemaliger Sicherheitsoffizier, jetzt ITI-Außenagent.

**Kim** [Kim]: generate alle, ich will einfach losspielen lol

**Mara Voss** [Sarah]: Voss ist komplett, ihr habt die Werte alle oben — GES 5, INT 5, TEMP 4, SOC 3, STR 3, WIS 3, Tatortanalyse. Jonas und Kim sollen selbst entscheiden, ich warte kurz.

### Turn 2 — SL

## Gruppen-Import – Konvertierung & Klärung

Bevor ich die Bögen ausgebe, zwei kurze Hinweise:

---

### Attribut-Mapping

ZEITRISS verwendet **STR, GES, INT, CHA, TEMP, SYS** — kein SOC, kein WIS.

Ich übersetze eure Werte so:

| Euer Wert | ZEITRISS-Attribut | Begründung |
|---|---|---|
| SOC | → CHA | Soziales, Täuschung, Einschüchterung |
| WIS | → INT | Analyse, Wissen, Technik |

SYS (Implantat-Slots) bekommt jeder Neueinsteiger **Startwert 2** — das ist der ITI-Standard für Feldagenten.

---

### Jonas – Ren Kaspar

Deine Werte: STR 5, GES 4, TEMP 4, INT 3 (ex-WIS), CHA 2 (ex-SOC) = **18 Punkte** ✓

Talent Nahkampf-Taktik ist regelkonform. SYS 2 als Standard dazu.

**Aber:** Das ergibt **7 Attribute** statt 6 — SYS kommt obendrauf, kein neuer Punkt. Passt so.

---

### Kim – generate

Ich baue Kim einen Charakter, der die Gruppe ergänzt. Voss hat GES/INT, Kaspar hat STR/TEMP — Kim bekommt ein **CHA/INT-Profil**: Infiltratorin mit sozialem Schmierfett. Passt für Tier-1-Tempocom.

---

## Charakterbögen

---

### CHARAKTER 1 — MARA VOSS

```
Callsign : SPLINTER
Spieler  : Sarah
Rang     : Rekrut → Feldagentin (1 Mission)
Lvl      : 2  |  XP: 0/2
Herkunft : unbekannte Epoche, Homo sapiens sapiens

ATTRIBUTE
  STR   3
  GES   5
  INT   5
  CHA   3
  TEMP  4
  SYS   2

HP      : 13/13   (10 + STR 3)
Stress  : 0/10

TALENTE
  Tatortanalyse (Basis)
    → +2 auf INT-Proben zur Spurenanalyse & Beweissicherung
    → Triviale Tatortlesungen ohne Probe

AUSRÜSTUNG (Tier 1)
  [Waffe]   Kompaktpistole Mod. Brixon-4  Tier 1 | 2-3 LP | RW kurz-mittel
  [Rüstung] Verstärktes Einsatzjackett    Tier 1 | DR 1
  [Gadget]  Handscanner Kodex-Link        — Identifikation, Datenabzug
  [Gadget]  Rauchgranate ×2

WALLET    : 150 CU
ITI-Ruf   : 1  |  Lizenz Tier I
```

*Notiz: Mara hat eine Mission hinter sich. Level 2 ist korrekt — erste Stufenwahl steht noch aus (Sarah, du darfst jetzt wählen: +1 Attribut ODER Talent/Upgrade ODER +1 SYS).*

---

### CHARAKTER 2 — REN KASPAR

```
Call

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Kaspar sieht gut aus, passt für mich. Callsign würde ich "RAMPART" nehmen, wenn das noch frei ist — klingt nach jemandem der vorne steht und Schläge einsteckt, passt zum Profil.

Kurze Frage zur Lizenz: Voss hat schon Tier I, ich starte bei Tier 0 — ist das wegen der ersten Mission oder gibt's da einen anderen Grund für den Unterschied? Und bei Delacroix, TEMP 1 ist ziemlich niedrig, wie viel Stress-Kapazität fehlt ihr da im Vergleich?

**Kim** [Kim]: warte mal kurz — SYS ist das mit den Implantat-Slots oder? und wieso hat meine Ines nur TEMP 1, ist das schlimm 😅

**Mara Voss** [Sarah]: Kurze Gegenfrage zur Klärung: Mein Original-Sheet hat SOC 3 und WIS 3 — die gehen beide in CHA und INT, also werden die jeweils addiert? Weil wenn INT schon 5 war und WIS 3 draufkommt, wäre das INT 8, das macht keinen Sinn. Ich glaube SOC und WIS ersetzen CHA/INT, nicht addieren. Dann wäre Voss bei 20 Punkten, weil mein ursprünglicher Bogen schlicht 20 hatte — war der von Anfang an zu viel, oder gilt das als Levelbonus von der ersten Mission?

### Turn 3 — SL

## Klärungsrunde – alle Fragen beantwortet

---

### Sarah – Punktefrage Voss

Du hast Recht mit der Logik: SOC **ersetzt** CHA, WIS **ersetzt** INT — keine Addition. Mein Mapping war korrekt ausgeführt, aber die 20 Punkte kamen aus deinem Original-Sheet, nicht aus dem Mapping.

**Mögliche Erklärung:** Dein letztes Spiel lief vielleicht mit einem anderen Punktebudget oder Voss hat bei Level 2 bereits eine Attribut-Erhöhung erhalten und das wurde im Sheet eingearbeitet.

**Pragmatische Lösung:** Wir behandeln die 2 Extrapunkte als **Level-2-Bonus bereits verbucht** — das heißt:

- Voss hat ihre Level-2-Wahl schon genommen: +1 GES (5→6) und +1 INT (5→6) — **oder** du sagst mir welche zwei Punkte du erhöht hast
- Die Level-2-Wahl-Frage entfällt dann
- Voss startet mit 20 Punkten, wovon 18 Basis + 2 aus Level-Up

**Sarah, kurz bestätigen:** Welche zwei Attribute wurden erhöht? Oder soll ich GES und INT nehmen (die thematisch am stärksten zu SPLINTER passen)?

---

### Jonas – Lizenz-Unterschied & CALLSIGN

**RAMPART ist frei.** Passt gut zum Profil.

**Lizenz Tier I vs. Tier 0:** Das ist direkt an den ITI-Ruf gekoppelt.

> Nach der **ersten erfolgreich abgeschlossenen Core-Mission** steigt der ITI-Ruf auf +1 — damit öffnet sich automatisch **Lizenz Tier I**. Das erlaubt Tier-1-Ausrüstung ohne Sondergenehmigung und gibt Zugang zu bestimmten ITI-Ressourcen.

Voss hat eine Mission hinter sich → ITI-Ruf 1 → Lizenz Tier I.  
Kaspar und Delacroix starten frisch → ITI-Ruf 0 → Lizenz Tier 0.

Tier 0 ist kein Nachteil im Feld — Tier-0-Ausrüstung funktioniert. Es bedeutet nur, dass ihr für Tier-1-Einkäufe im HQ entweder Voss' Lizenz nutzt oder die erste Mission erfolgreich abschließt.

---

### Kim – SYS und TEMP 1

**SYS = Implantat-Slots.** Genau. SYS 2 bedeutet: Ines kann 2 Implantate dauerhaft installiert haben. Mehr SYS = mehr Augmentierungen möglich. Für Tier-1-Einsätze ist SYS 2 vollkommen ausreichend — die meisten Basis-Implantate kosten 1 Slot.

**TEMP 1 — ist das schlim

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, RAMPART ist gesetzt, danke für die Erklärung mit dem Tier-System — macht Sinn. Ich kann dann für die Newcomer mit meiner Lizenz einspringen falls nötig, wär ja blöd wenn jemand im HQ an der Ausrüstungstheke hängen bleibt.

**Kim** [Kim]: ja GES 5 und INT 5 klingt gut! ich vertrau dir 😄

**Mara Voss** [Sarah]: Passt für mich — Voss hat bei Level-Up GES und INT erhöht, das ergibt Sinn für SPLINTER. Nehmt GES 6, INT 6.

### Turn 4 — SL

## Finale Charakterbögen – Gruppe ZEITRISS

---

`Kodex: Gruppenimport abgeschlossen. 3 Agenten verifiziert. Lizenz-Check läuft.`

---

### CHARAKTER 1 — MARA VOSS

```
Name     : Mara Voss
Callsign : SPLINTER
Spieler  : Sarah
Rang     : Feldagentin
Lvl      : 2  |  XP: 0/2
Herkunft : [offen], Homo sapiens sapiens

ATTRIBUTE (Basis 18 + 2 Level-Up)
  STR   3
  GES   6   ← Level-Up
  INT   6   ← Level-Up
  CHA   3
  TEMP  4
  SYS   2

HP      : 13/13   (10 + STR 3)
Stress  : 0/11    (8 + CHA 3)

WÜRFEL
  STR  → W6   (Basis 3)
  GES  → W6   (Basis 6)
  INT  → W6   (Basis 6)
  CHA  → W6   (Basis 3)
  TEMP → W6   (Basis 4)

TALENTE
  Tatortanalyse (Basis)
    +2 auf INT-Proben zur Spurenanalyse & Beweissicherung
    Triviale Tatortlesungen ohne Probe

AUSRÜSTUNG (Tier 1)
  [Waffe]   Kompaktpistole Brixon-4        Tier 1 | 2-3 LP
  [Rüstung] Verstärktes Einsatzjackett     Tier 1 | DR 1
  [Gadget]  Handscanner Kodex-Link
  [Gadget]  Rauchgranate ×2

WALLET    : 150 CU
ITI-Ruf   : 1  |  Lizenz Tier I
```

`Kodex: GES 6 und INT 6 bestätigt. Würfeltyp bleibt W6 — W10-Schwelle erst ab Basis 11.`

---

### CHARAKTER 2 — REN KASPAR

```
Name     : Ren Kaspar
Callsign : RAMPART
Spieler  : Jonas
Rang     : Rekrut
Lvl      : 1  |  XP: 0/1
Herkunft : Sicherheitsoffizier, Homo sapiens sapiens

ATTRIBUTE (Basis 18)
  STR   5
  GES   4
  INT   3
  CHA   2
  TEMP  4
  SYS   2

HP      : 15/15   (10 + STR 5)
Stress  : 0/10    (8 + CHA 2)

WÜRFEL
  STR  → W6   (Basis 5)
  GES  → W6   (Basis 4)
  INT  → W6   (Basis 3)
  CHA  → W6   (Basis 2)
  TEMP → W6   (Basis 4)

TALENTE
  Nahkampf-Taktik (Basis)
    +2 auf STR-Proben im Nahkampf
    Routinemäßige Entwaffnung ohne Probe gegen ungepanzerte Gegner

AUSRÜSTUNG (Tier 1)
  [Waffe]   Stun-Schlagstock verstärkt     Tier 1 | 2-3 LP
  [Waffe]   Dienstpistole P-7              Tier 1 | 2-3 LP
  [Rüstung] Taktikweste                    Tier 1 | DR 1
  [Gadget]  Handfessel-Kit ×4
  [Gadget]  Erste-Hilfe-Injektor ×1

WALLET    : 100 CU
ITI-Ruf   : 0

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Alright, Ren Kaspar steht bereit. Kurze Frage noch bevor's losgeht — der Erste-Hilfe-Injektor, einmal verwenden und weg, oder kann der aufgeladen werden? Und gibt's hier am Duty-Desk noch die Möglichkeit, Ausrüstung nachzukaufen, bevor wir durch die Schleuse gehen?

**Kim** [Kim]: okay MOTH klingt so cool ich liebe das 😭 aber was ist nochmal SYS? hab das letzte mal nicht gecheckt was das bedeutet

**Mara Voss** [Sarah]: Voss wirft einen kurzen Blick auf den finalen Bogen, nickt einmal. "Alles korrekt." Sie lehnt sich zurück und legt die Hände auf die Tischkante. "Wann geht's los?"

> **⚠️ Finding [TERMINOLOGIE]:** SL nutzt 'HP' statt 'LP'

### Turn 5 — SL

## HQ – Duty-Desk, kurze Einweisung

Der Duty-Desk-Mitarbeiter — Namensschild: **OSEI, T.** — schaut von seinem Terminal auf. Kein Lächeln, aber auch keine Ungeduld. Die Art Mensch, der Fragen erwartet und sie effizient abarbeitet.

---

### Jonas – Erste-Hilfe-Injektor & Nachkauf

**Injektor:** Einmal verwenden, dann leer. Kein Aufladen im Feld. Im HQ kannst du neue kaufen — Standardpreis **30 CU pro Stück** an der Quartiermeisterei. Osei tippt kurz. *"Wir haben Bestand."*

**Nachkauf am Duty-Desk:** Ja, möglich. Osei verwaltet Tier-0- und Tier-1-Grundausstattung. Keine Exotika, keine Spezialwaffen — aber Verbrauchsmaterial, Standardmunition, Injektoren, Fesselkits, einfache Gadgets.

> Aktuell verfügbar (Tier 0–1, Lizenz Tier 0 ausreichend):

| Item | Tier | Preis | Effekt |
|---|---|---|---|
| Erste-Hilfe-Injektor | 0 | 30 CU | +3 HP sofort, Einmalnutzung |
| Rauchgranate | 0 | 25 CU | Sichtschutz, 1 Runde |
| Handfessel-Kit ×4 | 0 | 20 CU | Standardfesselung |
| Signalstörer-Patch | 1 | 60 CU | +1 auf Schleichen vs. elektronische Sensoren, 1 Einsatz |
| Kodex-Datenstick | 1 | 50 CU | Lokaler Datenspeicher, verschlüsselt, 1 Einsatz |

*Lizenz Tier I (Voss) schaltet nichts Zusätzliches am Desk frei — Tier-I-Spezialausrüstung läuft über die Quartiermeisterei, nicht den Duty-Desk.*

**Jonas — kaufst du etwas?** (Kaspar hat 100 CU)

---

### Kim – SYS erklärt

Osei dreht sich nicht um, aber MOTH bekommt die Antwort trotzdem — von einem kleinen laminierten Aushang direkt neben dem Desk. Jemand hat ihn dort hingeklebt, handgeschrieben, leicht schief:

---

> **SYS = Systemkapazität**
> Dein Körper kann nur so viele Implantate dauerhaft tragen, wie dein SYS-Wert erlaubt.
> SYS 2 = 2 Implantat-Slots frei.
> Implantate sind physische Eingriffe — Knochen, Gewebe, Nerven.
> Kein SYS-Slot frei = kein neues Implantat.
> Mehr SYS durch Level-Up oder Klinik-Upgrade.

---

Konkreter für Ines: SYS 2 bedeutet, sie könnte z.B. ein **Subkutanes Kommunikationsrelais** (Slot 1) und ei

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, 100 CU, ich nehm zwei Injektoren — macht 60 CU. Den Rest heb ich für die Quartiermeisterei auf, falls da noch was Interessantes liegt. Kaspar ist halt kein Fernkämpfer, der braucht eher den Puffer wenn's eng wird. Können wir danach direkt zu 4-C?

**Kim** [Kim]: okay klinik klingt gut aber... haben wir überhaupt zeit? 20 minuten reicht das?

**Mara Voss** [Sarah]: Voss lehnt kurz gegen die Wand, Arme verschränkt, und tippt: "Ich geh schon mal vor. 4-C, zwanzig Minuten — ich kenn das Warten."

### Turn 6 — SL

## HQ – Drei Wege, ein Ziel

---

### Kaspar – Duty-Desk

Osei zieht zwei Injektoren aus dem Fach unter dem Tresen. Kein Beutel, kein Schnickschnack — zwei nackte Spritzen in Schutzfolie, ITI-Standardgrün, Chargennummer aufgedruckt. Er legt sie auf den Tresen, tippt einmal.

*"Sechzig."*

Kaspar zahlt. Osei bestätigt mit einem kurzen Nicken und dreht sich wieder zum Terminal.

`Kodex: Kaspar — Wallet 100 → 40 CU. Erste-Hilfe-Injektor ×3 im Carry.`

---

### Delacroix – Klinik

Zwanzig Minuten reicht knapp. Die ITI-Klinik liegt zwei Gänge weiter — weißes Licht, Desinfektionsmittelgeruch, ein Med-Tech der aussieht als hätte er seit achtzehn Stunden keinen Kaffee mehr getrunken. Er schaut von seinem Clipboard auf.

*"Implantat-Beratung? Schnell oder gründlich?"*

**Schnell** heißt: Er zeigt dir was verfügbar ist, du entscheidest in fünf Minuten, Installation in zehn. Für einfache Tier-1-Implantate machbar.

> Aktuell verfügbar (Tier 1, SYS-Slot-Kosten 1):

| Implantat | Preis | Effekt |
|---|---|---|
| Subkutanes Komm-Relais | 80 CU | Internes Funksignal, kein Gerät nötig für Gruppenkommunikation |
| Reflex-Dämpfer | 90 CU | +1 auf GES-Proben zum Ausweichen, passiv |
| Adrenalin-Regulator | 85 CU | Stress-Maximum +2, passiv |

*Ines hat 100 CU und SYS 2 — sie könnte sich eines leisten, knapp.*

`Kodex: MOTH — 20 Minuten bis Briefing. Installation Tier-1-Implantat: ~12 Minuten. Machbar.`

**Kim — nimmst du eines? Oder schaust du nur und gehst dann zu 4-C?**

---

### Voss – Briefingraum 4-C

Der Raum ist klein, funktional. Vier Stühle, ein Projektionstisch, ein Wandterminal das noch hochfährt. Kühles blaues Licht. Durch die Glasscheibe sieht man den Hangar-Axis — ein Techniker zieht ein Kabel durch eine Wartungsluke, sonst nichts.

Mira steht bereits dort. Keine große Geste — sie legt einen Datenstick auf den Tisch und nickt einmal.

*"Voss. Gut, dass du früh kommst."* Eine kurze Pause. *"Die anderen zwei — neu?"*

Sie fragt nicht aus Neugier. Sie fragt weil sie es ins 

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich lehne mich kurz vor und starre auf das Foto von Finch.

"Warten kurz — der 'unbekannte Dritte' bei der Übergabe. Habt ihr irgendwas zu dem? Zeitfenster, ungefähre Location, ob Finch das freiwillig macht oder ob er unter Druck steht? Das ändert wie wir rangehen."

**Kim** [Kim]: okay der adrenalin-ding klingt gut aber 85 cu... hab ich dann noch 15 übrig? ist das genug für irgendwas?

**Mara Voss** [Sarah]: Voss nickt Mira kurz zu. "Beide neu. Erster gemeinsamer Einsatz." Sie zieht einen Stuhl zurück, setzt sich, Augen auf den Projektionstisch. Dann, als das Foto erscheint: "Tempocom-Bauteil in einem Fernschreiber-Relais, 1962 — jemand wollte eine verschlüsselte Regierungsleitung anzapfen oder stören. Gibt es Daten zur Übergabezeit oder nur das Datum?"

### Turn 7 — SL

## Briefing – Fragen, Antworten, Entscheidung

---

### Kim – Klinik-Entscheidung

Der Med-Tech wartet. Fünfzehn CU nach dem Kauf — das reicht für nichts Kaufbares, aber:

*"Fünfzehn CU bleiben als Reserve. Kein Problem."* Er zieht bereits die Sterilverpackung raus. *"Adrenalin-Regulator ist ein einfacher Eingriff. Lokalbetäubung, subkutan, zehn Minuten."*

`Kodex: MOTH — Wallet 100 → 15 CU. Adrenalin-Regulator installiert. SYS-Slot 1/2 belegt. Stress-Maximum 13 → 15.`

Ines kommt drei Minuten nach den anderen in 4-C. Linker Unterarm noch leicht taub. Sie setzt sich, hört zu.

---

### Briefingraum 4-C – die Fragen

Mira wartet, bis alle sitzen. Dann beantwortet sie der Reihe nach.

---

**Kaspar — der Dritte**

Mira tippt. Das Foto von Finch bleibt, aber daneben erscheint jetzt ein zweites Bild — kein Gesicht, nur eine Silhouette. Schwarzer Umriss, Fragezeichen.

*"Nichts Konkretes. Rückwärtsanalyse zeigt: Finch verlässt das Pentagon um 17:40, geht nicht den Standardweg nach Hause. Abweichung von ungefähr vier Blocks Richtung Dupont Circle. Dort verliert sich die Spur."*

Sie faltet die Hände.

*"Ob Finch unter Druck steht — unbekannt. Keine Hinweise auf Erpressung im Archiv, aber das Archiv ist lückenhaft für diese Woche. Die Krise hat viel überdeckt. Was wir wissen: Er macht es einmal. Nur diesen einen Abend. Danach kehrt er zur Routine zurück."*

Kurze Pause.

*"Das klingt eher wie jemand der einen Auftrag ausführt, nicht wie jemand der Angst hat."*

---

**Voss — Übergabezeit und Bauteil-Funktion**

Mira nickt — die Frage war gut gestellt.

*"Zeitfenster haben wir auf 18:15 bis 19:45 eingegrenzt. Dupont Circle oder unmittelbare Umgebung — Radius ungefähr dreihundert Meter. Das ist unser Suchfeld."*

Sie wechselt zur nächsten Folie. Schaltplan, jetzt größer. Ein kleines rechteckiges Bauteil, Röhrentechnik-Optik von außen, innen etwas das da nicht hingehört — glatte Oberflächen, keine Lötpunkte, kein Bakelitgehäuse.

*"Zur Funktion: Das Bauteil ist kein Abhörgerä

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich tippe:

---

Datenstick. Ich will Finchs Route haben bevor wir springen — besonders die letzten drei Blocks vor Dupont Circle, wo er abweicht. Wenn er einen Auftrag ausführt hat er wahrscheinlich einen festen Treffpunkt. Das ist keine Improvisation, das ist Routine für ihn. Vielleicht finden wir im Stadtplan schon eingrenzen wo der Übergabepunkt sein könnte — Park, Café, toter Briefkasten.

**Kim** [Kim]: okay warte — SYS-Slot bedeutet ich kann noch EIN weiteres implantat kriegen später, oder?

und dann: Datenstick. ich will nicht blind reinhüpfen 😅

**Mara Voss** [Sarah]: Voss nimmt den Datenstick, dreht ihn kurz zwischen den Fingern. "Wir gehen den Stick durch. Zehn Minuten — dann springen wir." Sie schaut zu den anderen. "Wenn jemand den Dritten dokumentieren wollte statt zu sabotieren, hat er ein Langzieliel. Das bedeutet er könnte heute Abend noch da sein."

### Turn 8 — SL

## Briefing – Datenstick-Analyse

---

### Kim – SYS kurz

Ja. SYS 2, ein Slot belegt — **ein freier Slot bleibt**. Du kannst später ein zweites Implantat installieren lassen. Mehr SYS gibt's durch Level-Up oder einen Klinik-Eingriff der teurer ist.

`Kodex: MOTH — SYS-Slots: 1/2 belegt. 1 frei.`

---

### Datenstick – zehn Minuten, Briefingraum 4-C

Voss steckt den Stick ins Wandterminal. Der Projektionstisch wirft einen vergrößerten Stadtplan von Washington D.C. auf die Wand — Schwarzweiß, handgezogene Straßenlinien, ITI-Markierungen in Rot darüber gelegt.

Finchs Route leuchtet als gestrichelte Linie auf.

---

**Probe: Analyse Datenstick**

Voss führt die Analyse — Tatortanalyse-Talent greift.

`Probe: Tatortanalyse → W6: [5] + ⌊INT 6/2⌋ (3) + Talent +2 = 10 vs SG 7 → ERFOLG`

Kaspar lehnt über den Tisch, folgt der Linie mit dem Finger. Delacroix steht seitlich, Augen auf die Seitenstraßen.

---

**Was der Datenstick zeigt:**

Finchs Standardroute führt von der Pentagon-Haltestelle direkt nach Nordost — Metro, Umstieg, nach Hause. Heute Abend: kein Umstieg. Er läuft.

Die Abweichung beginnt an der **17th Street NW**, drei Blocks südlich des Dupont Circle. Dort biegt er west ab statt weiter nord. Kein direkter Weg — ein Umweg, aber kein zufälliger.

Voss tippt auf drei Punkte auf der Karte.

*"Drei mögliche Übergabepunkte im Radius."*

---

**Punkt A — Meridian Hill Park (Malcolm X Park)**
Erhöhtes Gelände, Treppen, Brunnen. Viel Sichtlinie, aber auch viel Deckung zwischen den Terrassen. Beliebt bei Spaziergängern — unauffällig für eine kurze Begegnung. **Wahrscheinlichkeit: hoch.**

**Punkt B — Seiteneingang eines Bürogebäudes, P Street NW**
Schmale Gasse, Liefereingang, kein Durchgangsverkehr. Kurze Übergabe, keine Zeugen. Riskant wenn jemand rauskommt — aber schnell. **Wahrscheinlichkeit: mittel.**

**Punkt C — Kleine Bar, Connecticut Avenue**
*"The Argyle"* — existiert 1962, kein Touristenlokal. Stammgäste, Halbdunkel, Hinterraum. Eine Übergabe im Sitzen, mit

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, ich tendiere zu Option 2, aber leicht abgewandelt. Delacroix hat recht — wenn jemand eine Stammgast-Legende aufgebaut hat, ist die Bar sein Heimvorteil, und MOTH als unauffällige Redaktionsassistentin passt da perfekt rein. Ich gehe in die Argyle, setz mich irgendwo mit Sichtlinie auf den Hinterraum, und beobachte. Aber ich würde RAMPART zusätzlich auf Punkt A schicken — Fotograf im Park ist null verdächtig, und wenn Finch dort auftaucht hat er sofort Sichtkontakt. SPLINTER sichert außen vor der Bar. Macht das Sinn so, oder verlieren wir dadurch zu viel Koordination?

**Kim** [Kim]: Okay warte — Claire Vance geht in die Bar, das macht Sinn oder? Ich bin am unauffälligsten da drin. Option 2!

**Mara Voss** [Sarah]: Ich tippe:

"Ich mag Delacroix' Ansatz — wenn der Dritte eine Stammgast-Legende hat, ist die Bar sein Komfortzone. Trotzdem sollten wir nicht alle Eier in einen Korb legen. Mein Vorschlag: MOTH geht in die Bar, ich nehme den Park — erhöhtes Gelände, ich sehe Finch ankommen bevor er ankommt. RAMPART bleibt auf der P Street als Mittelposition, kann schnell zu einem von uns. Wenn Finch Richtung Bar abbiegt, zieht RAMPART nach und ich halte den Park im Auge für den Dritten."

### Turn 9 — SL

## Sprung – Washington D.C., 14. Oktober 1962

---

Mira hört sich den Plan an. Nickt einmal, knapp.

*"Solide. Kommunikation läuft über Subkutan-Relais bei Delacroix, Comlinks bei den anderen — epochenkonform versteckt, kurze Burst-Übertragungen. Kein Dauersenden."*

Sie steht auf.

*"Noch eins: D.C. ist heute Abend nervös. Die Krise ist zwölf Tage alt, die Zeitungen reden von Krieg, die Leute auf der Straße wissen es noch nicht aber sie spüren es. Bleibt in der Rolle."*

Der Hangar-Axis wartet.

---

**Sprungformation:**

Der Transferkorridor ist kalt — nicht metaphorisch, physisch. Metallboden, blaues Neonlicht, drei Sprungkabinen nebeneinander. Ein Techniker kalibriert die letzte Kabine, schaut kurz auf, sagt nichts. Routinebetrieb.

Kaspar betritt die mittlere Kabine. Delacroix rechts. Voss links.

Das HUD handshakt — drei kurze Vibrationen am Handgelenk, dann:

`Kodex: Zielkoordinaten geladen. Washington D.C., 17:28 Uhr EST, 14.10.1962. Transferfenster: 4 Sekunden. Sprung auf Markierung.`

Gravität kippt. Nicht dramatisch — eher wie ein Fahrstuhl der eine Etage zu weit fährt und kurz innehält. Dann Boden unter den Füßen, anderer Boden, Pflastersteine statt Metall.

---

`EP 1 · MS 1 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Px 0/5`
`Voss Lvl 2 ▓▓░░░░░░░░ 0/2 · Kaspar Lvl 1 ▓░░░░░░░░░ 0/1 · MOTH Lvl 1 ▓░░░░░░░░░ 0/1`
`❤️‍🩹 Voss 13/13 · Kaspar 15/15 · MOTH 12/12 · 🧠 Stress 0 · 👁️ Tarnung: Deckidentität aktiv`
`Obj: Finch observieren · Übergabepunkt identifizieren · Exfil: offen`

---

## Szene 1 — Ankunft, Connecticut Avenue NW, 17:28 Uhr

Der Geruch trifft zuerst. Abgase, Kohle, nasses Pflaster. Ein Oktober-Abend in Washington — der Himmel ist bleigrau, die Luft riecht nach Regen der noch kommt. Die Straßenlaternen sind noch nicht an, aber das Licht geht bereits weg.

Connecticut Avenue ist belebt. Männer in Mänteln, Frauen mit Kopftüchern, ein Zeitungsstand an der Ecke — die Schlagzeile ist von weitem lesbar: **KENNEDY SPRICHT HEUTE ABEND.** Der Händler

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, ich bin MOTH. Ich betrete die Bar, gehe zur Theke und bestelle was Unauffälliges — Bier, was auch immer die hier haben. Dabei scanne ich den Raum, aber ohne offensichtlich rumzugucken. Die zwei Männer hinten interessieren mich am meisten, ich will hören ob ich irgendwas von deren Gespräch aufschnappen kann ohne mich zu nähern. Gibt's dafür einen Wahrnehmungswurf oder reicht das erstmal als Positionierung?

**Kim** [Kim]: okay ich bin drin!! riecht hier komisch lol

also ich bin die MOTH oder? die in der bar?? was soll ich da genau machen, einfach was bestellen und die zwei typen hinten beobachten?

**Mara Voss** [Sarah]: Voss hält den Notizblock aufgeschlagen, Stift in der Hand — sieht aus wie Warten, ist Beobachten. Sie scannt die Eingangstür der Argyle, dann die Kreuzung, dann zurück. Ruhiger Rhythmus.

*"SPLINTER in Position. Sicht auf Eingang und Kreuzung, nichts Auffälliges bisher. MOTH, wie sieht's drinnen aus?"*

### Turn 10 — SL

## Szene 1 — The Argyle, 17:31 Uhr

---

### Kurze Rollenzuweisung

Kleines Durcheinander — kein Problem. Zur Klarheit:

**MOTH = Kim / Ines Delacroix.** Sie ist in der Bar.
**RAMPART = Jonas / Ren Kaspar.** Er war im Park, sieht Finch, läuft jetzt nach.
**SPLINTER = Sarah / Mara Voss.** Sie steht draußen vor der Bar.

Jonas — du spielst RAMPART, nicht MOTH. Aber deine Aktion passt perfekt für MOTH. Ich übertrage sie auf Kim/Delacroix und spiele RAMPART parallel weiter. Macht das Sinn?

---

### MOTH — The Argyle

Delacroix tritt an die Theke. Der Barkeeper — Fünfzig, Schnurrbart, Hemdärmel hochgekrempelt — schaut kurz auf.

*"Draft okay?"*

Sie nickt. Er zapft, stellt das Glas hin, dreht sich zum Radio. Routine.

Delacroix lehnt leicht an der Theke, Glas in der Hand, Blick locker in den Raum. Nicht suchend. Einfach da.

**Probe: Wahrnehmung / Belauschen — CHA (soziale Raumlesung)**

`Probe: Belauschen → W6: [4] + ⌊CHA 5/2⌋ (2) + 0 = 6 vs SG 7 → MISS`

Das Radio ist zu laut für den Raum — oder die zwei Männer hinten reden zu leise. Einzelne Wörter dringen durch: *"...morgen früh..."* — *"...wenn er's nicht bringt..."* — dann Stühlerücken, der Größere lehnt sich vor, und der Rest verschluckt der Lärm von draußen als draußen ein Bus vorbeifährt.

Keine vollständigen Sätze. Aber die Körpersprache ist lesbar: Der Kleinere mit den unruhigen Händen redet. Der Größere hört zu und sagt wenig. Das ist kein Freundschaftsgespräch.

`Kodex: Partial-Audio. Kontext unvollständig. Visuelle Auswertung empfohlen.`

---

**Burst-Comlink — MOTH an SPLINTER:**

Ein kurzes Knacken im Ohrrelais. Delacroix hält das Glas vor den Mund, spricht kaum hörbar.

*"Zwei Männer, Hinterraum. Einer groß, einer klein und nervös. Reden gedämpft — ich krieg nur Fragmente. Kein Finch bisher."*

---

### SPLINTER — Connecticut Avenue, 17:34 Uhr

Voss hört den Burst, tippt einmal kurz zurück.

*"Verstanden. Finch ist unterwegs — RAMPART hat Sichtkontakt im Park, Richtung hier. Schätzung fünf Minuten."*

S

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, verstanden — Rollenzuweisung ist klar, danke für die Korrektur!

RAMPART hört SPLINTERs Burst ab und wartet auf Antwort. Ich spiele Option 1: Kaspar empfängt die Beschreibung des Verfolgers und versucht ihn von hinten einzuschätzen.

*"Burst zurück an SPLINTER: Beschreib mir den Kerl — Körperbau, Hände, wie er läuft. Ich schaue ob er Ausbuchtungen unter dem Mantel hat."*

Brauche ich dafür eine Wahrnehmungs-Probe oder reicht das durch SPLINTERs Erfolg abgedeckt?

**Kim** [Kim]: okay also ich bin MOTH, Delacroix ist in der Bar — stimmt das so?

dann Option 2, ich rück näher ran. die zwei Typen klingen shady, ich will wissen was die reden 👀

**Mara Voss** [Sarah]: Voss presst kurz den Finger ans Ohrrelais. „RAMPART, zehn Meter hinter dir — dunkler Mantel, keine Krawatte, Mitte dreißig. Folgt Finch, schaut ihn nicht an. Kein Profi, aber mit Absicht." Kurze Pause. „Kannst du ihn einsehen?"

### Turn 11 — SL

## Szene 1 — Connecticut Avenue / The Argyle, 17:36 Uhr

---

### Kim — ja, MOTH ist Delacroix, du bist in der Bar. Richtig.

---

### RAMPART — Verfolger einschätzen

Kaspar hört SPLINTERs Beschreibung. Dreht den Kopf nicht — er hebt die Kamera, tut als würde er ein Gebäude auf der anderen Straßenseite fotografieren. Im Sucher: Finch, und dahinter, scharf, der Mann im dunklen Mantel.

Mitte dreißig. Mittelgroß, breit in den Schultern aber nicht trainiert — eher Arbeiterkörper. Hände in den Manteltaschen. Linke Seite hängt minimal tiefer.

**Probe: Beobachtung / Waffencheck — INT**

`Probe: Waffencheck → W6: [3] + ⌊INT 3/2⌋ (1) + 0 = 4 vs SG 8 → MISS`

Der Abstand ist zu groß, das Licht zu schlecht. Die linke Manteltasche könnte eine Waffe sein — oder ein Schlüsselbund, oder nichts. Kaspar kann es nicht sicher sagen.

Was er sagen kann: Der Mann geht nicht wie jemand der kämpfen will. Keine Anspannung in den Schultern, kein gescannter Horizont. Er geht wie jemand der **aufpassen** soll, nicht wie jemand der eingreifen soll.

`Kodex: RAMPART — Waffenstatus unklar. Verhalten: passiv-observativ.`

Burst an SPLINTER, kurz: *"Linke Tasche könnte was sein — nicht sicher. Wirkt wie Beobachter, kein Schläger. Halte Abstand."*

---

### MOTH — näher ran

Delacroix nimmt ihr Glas, schaut sich kurz um — als würde sie einen freieren Platz suchen. Natürliche Bewegung. Sie wählt den Tisch direkt neben den zwei Männern, eine Ecke weiter innen. Setzt sich mit dem Rücken zur Wand, Blick Richtung Eingang — klassische Sitzposition, nichts Verdächtiges.

**Probe: Schleichen / Unauffälliges Nähern — GES, Modifikator Verdeckte Identität**

`Probe: Unauffällig positionieren → W6: [5] + ⌊GES 5/2⌋ (2) + Talent +2 = 9 vs SG 7 → ERFOLG`

Der Größere schaut kurz auf als sie vorbeigeht. Sekunde. Dann wieder zum Kleineren. Kein Alarm.

Jetzt hört sie.

Der Kleinere — unruhige Hände, Schweißfilm auf der Stirn — redet gedämpft aber schnell. Amerikanisches Englisch, leichter Südstaaten-Akzent:

*"—

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Kaspar bleibt wo er ist und gibt kurz durch: *"MOTH — Finch ist drin, sitzt bei deinen zwei Männern. Übergabe läuft. Kannst du mithören?"*

Dann zu SPLINTER: *"Verfolger steht draußen, raucht — der wartet. Solange er dort bleibt, haben wir Zeit. Wenn er anfängt Richtung Eingang zu laufen, sag sofort was."*

Ich halte meinen Standpunkt und beobachte den Verfolger weiter. Gibt's einen Würfelwurf dafür oder läuft das passiv?

**Kim** [Kim]: okay MOTH hört jetzt was die sagen — soll ich das irgendwie aufnehmen?? oder reicht dass ich's im chat tippe was ich gehört hab

**Mara Voss** [Sarah]: Voss flüstert ins Comlink: "Finch ist drin, Verfolger hält die Stellung draußen — der will die Übergabe abwarten, nicht verhindern." Kurze Pause. "Ich bleibe auf dem Verfolger. MOTH, sag mir sobald du weißt was übergeben wird — dann entscheide ich ob wir den Typ hier draußen ansprechen oder laufen lassen."

### Turn 12 — SL

## Szene 1 — The Argyle / Connecticut Avenue, 17:39 Uhr

---

### Kim — so läuft das

Du tippst was Delacroix hört, ich baue es in die Szene ein und würfele wenn nötig. Kein separates Aufnahmegerät nötig — Delacroix hat Augen und Ohren, das reicht. Wenn du willst dass sie etwas Spezifisches versucht (näher rücken, Lippen lesen, Foto machen), sag es und ich würfele dafür.

---

### RAMPART — passive Observation

Kaspar hält Position. Keine Probe nötig solange er nur wartet und den Verfolger im Blick behält — passive Beobachtung ohne Risiko läuft ohne Wurf. Erst wenn der Verfolger sich bewegt oder Kaspar aktiv eingreift, wird gewürfelt.

Der Verfolger raucht. Schaut auf die Tür. Zieht einmal tief, bläst aus. Keine Hast.

---

### MOTH — Hinterraum, 17:39 Uhr

Delacroix sitzt. Glas vor sich, Blick Richtung Eingang — aber die Ohren nach hinten.

Finch hat die Aktentasche zwischen den Beinen. Er redet leise, kurze Sätze. Der Kleinere nickt. Der Größere schaut zur Tür — einmal, kurz, dann wieder zu Finch.

**Probe: Belauschen — CHA, Nahposition**

`Probe: Belauschen (Nahposition) → W6: [6] + ⌊CHA 5/2⌋ (2) + Talent +2 = 10 vs SG 6 → ERFOLG (Exploding: [2]) → 12 — STARKER ERFOLG`

`Kodex: MOTH — Audio gesichert. Protokoll läuft.`

Delacroix hört jetzt klar.

---

Finch, ruhig, fast geschäftsmäßig: *"Ich hab's dabei. Eingebaut wie besprochen — sieht aus wie Standardteil, kein Techniker wird's auf den ersten Blick erkennen."*

Der Kleinere, atemlos: *"Und du hast's nicht getestet?"*

Finch: *"Ich teste keine Dinge die ich nicht verstehe."* Kurze Pause. *"Ihr habt mir gesagt es ist harmlos."*

Der Größere, zum ersten Mal mit etwas Gewicht in der Stimme: *"Es ist harmlos."*

Stille. Dann greift Finch in die Aktentasche. Zieht ein kleines Päckchen raus — Zeitungspapier, eng gewickelt, handgroß. Legt es auf den Tisch, schiebt es zum Kleineren.

Der Kleinere greift danach.

---

**Das Bauteil liegt auf dem Tisch.**

---

`Kodex: Übergabe aktiv. Bauteil sichtbar. Zeitfenster: Sekun

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay Moment, ich denk kurz laut nach bevor ich mich festlege.

Der Verfolger schaut auf die Seitengasse — das ist kein Zufall. Da wartet jemand auf das Päckchen, oder der Typ sichert einen Fluchtweg. Wenn ich als SPLINTER jetzt die Gasse checke, verliere ich aber den Verfolger aus den Augen und MOTH ist allein drin.

Ich würd das so koordinieren: **SPLINTER checkt die Gasse, aber gibt vorher kurz Bescheid.** Kaspar, bevor er die Position verlässt, tippt einmal kurz in die Komm — einfaches Signal, kein Text, nur "ich beweg mich". Dann umrundet er das Gebäude zur Gasse.

MOTH soll dabei **nicht eingreifen** — noch nicht. Das Päckchen in der Hand des Kleineren ist schlecht, aber wenn hinten ein Abholer wartet und wir den nicht kennen, verlieren wir das große Bild.

Also: **Option 2, SPLINTER zur Seitengasse** — aber gibt es ein kurzes Komm-Signal das ich senden kann ohne Heat

**Kim** [Kim]: okay ich glaub wir müssen das ding aufhalten bevor der kleine typ es einsteckt??

MOTH steht auf und geht zum Tisch, so als ob sie jemanden kennt oder so — irgendwas um Zeit zu schinden

und sagt jemand Voss er soll die Seitengasse checken!!

**Mara Voss** [Sarah]: Voss sagt leise ins Comlink: "Verfolger fixiert Seitengasse — ich check das. MOTH, haltet das Päckchen so lang wie möglich auf dem Tisch."

Sie schiebt sich von der Wand ab und geht unauffällig die Straße entlang, Richtung Gebäudeecke.

### Turn 13 — SL

## Szene 1 → Szene 2 — Split-Aktion, 17:40 Uhr

---

### Koordination — Comms kurz

Burst-Signal läuft durch. Kein Text, nur Klick-Muster — ITI-Standard für "ich bewege mich". Kein Heat.

`Kodex: Burst-Signal empfangen. SPLINTER bewegt sich. RAMPART hält Position.`

Kaspar bleibt auf der Connecticut Avenue. Kamera locker. Er sieht Voss an der Ecke verschwinden, sieht die Eingangstür der Argyle, sieht den Verfolger — der immer noch auf die Seitengasse schaut, Zigarette fast runtergebrannt.

---

### MOTH — Ablenkung am Tisch

Delacroix steht auf. Glas in der Hand, Schritt locker — sie geht auf den Hinterraum zu als würde sie einen bekannten Gesichtsausdruck suchen. Klassischer Irrtum: falscher Tisch, falsche Person, kurze Entschuldigung.

**Probe: Täuschung / Ablenkung — CHA, Verdeckte Identität**

`Probe: Ablenkung → W6: [4] + ⌊CHA 5/2⌋ (2) + Talent +2 = 8 vs SG 8 → ERFOLG, knapp`

Sie tritt an den Tisch. Lächelt den Kleineren an — verwirrt, freundlich, ein bisschen zu enthusiastisch für jemanden der gerade seinen Freund gefunden hat.

*"Oh — Bobby? Bobby Crane?"* Kurze Pause, dann gespieltes Zögern. *"Oh Gott, Entschuldigung — ich dachte Sie wären jemand anderes."*

Der Kleinere schaut auf. Hand am Päckchen, aber er steckt es nicht ein — der soziale Moment friert ihn kurz ein. Der Größere schaut Delacroix an, ruhig, abwartend. Finch lehnt sich leicht zurück, sagt nichts.

Drei Sekunden. Vier.

Das Päckchen liegt noch auf dem Tisch.

`Kodex: Übergabe verzögert. Zeitfenster: 20-30 Sekunden.`

---

### SPLINTER — Seitengasse

Voss geht die Straße entlang, biegt an der Ecke ab. Notizbuch aufgeschlagen, Stift in der Hand — Journalistin die sich Notizen macht, nichts Ungewöhnliches.

Die Gasse ist schmal. Mülltonnen, eine Feuertür aus Metall, eine einzelne Glühbirne über dem Ausgang. Und:

Ein Mann. Lehnt an der Wand, zehn Meter rein. Jünger als der Verfolger — Anfang zwanzig, Lederjacke, Motorradhelm unter dem Arm. Er schaut auf seine Uhr.

Kein Zigarettenrauch. Kein Dr

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Warte kurz — die Nachricht von Sarah ist abgeschnitten, Option 3 für RAMPART fehlt noch. Aber ich geh schonmal von aus was logisch wäre:

Wenn das Päckchen durch die Hintertür soll, dann ist der Kurier das eigentliche Problem. Ich würde sagen: SPLINTER blockiert den Kurier in der Gasse, das macht Sinn für Voss. Und RAMPART — ich vermute Option 3 war sowas wie "betritt die Bar" oder "sichert den Ausgang von innen"?

Für Kaspar würde ich den Verfolger draußen im Auge behalten und wenn nötig abfangen bevor er die Gasse checkt. STR 5 kommt mir da zugute falls's physisch wird. Aber ich will die vollständige Option 3 sehen bevor ich final entscheide — kannst du den Text nochmal schicken?

**Kim** [Kim]: okay SPLINTER blockiert den Kurier — Voss geht einfach auf ihn zu und fragt nach dem Weg oder so?? und was macht Kaspar, ich check Option 3 nicht ganz weil der Text abgeschnitten ist 😅

**Mara Voss** [Sarah]: Voss sagt leise ins Comlink: "Kurier ablenken, Päckchen verzögern — ich gehe rein."

Ich trete auf den jungen Mann zu, Notizbuch noch in der Hand, und sage mit einem leichten Lächeln: "Entschuldigung — kennen Sie sich hier aus? Ich such den Eingang zur Redaktion, die soll irgendwo hinten sein."

Option 2, Kurier blockieren.

### Turn 14 — SL

## Szene 2 — Seitengasse / The Argyle, 17:41 Uhr

---

### Kurze Klärung für Jonas und Kim

Option 3 war nicht abgeschnitten — ich hatte sie vollständig formuliert: **RAMPART betritt die Bar durch den Haupteingang, geht zur Theke, gibt MOTH Rückendeckung.** Das war der vollständige Text.

Kaspar, dein Instinkt ist gut: Den Verfolger draußen im Auge behalten und abfangen falls er sich zur Gasse bewegt. Das ist eine **vierte Option** die ich nicht explizit angeboten hatte — aber sie ist spielbar. Entscheide jetzt: Verfolger abfangen draußen, oder rein in die Bar?

---

### SPLINTER — Kurier blockieren

Voss tritt auf den jungen Mann zu. Notizbuch, leichtes Lächeln, Journalistinnen-Energie.

*"Entschuldigung — kennen Sie sich hier aus? Ich such den Eingang zur Redaktion, die soll irgendwo hinten sein."*

**Probe: Täuschung — CHA**

`Probe: Täuschung → W6: [3] + ⌊CHA 3/2⌋ (1) + 0 = 4 vs SG 6 → MISS`

Der junge Mann schaut sie an. Kurz. Dann schüttelt er den Kopf — nicht unfreundlich, aber der Blick bleibt kalt.

*"Keine Ahnung."*

Er dreht sich wieder zur Feuertür. Schulter leicht abgedreht — eine Wand aus Körpersprache. Er glaubt ihr nicht vollständig, aber er ignoriert sie. Noch.

Das Zeitfenster hält. Aber er wird nicht länger reden.

`Kodex: Kurier nicht überzeugt. Ablenkung partiell. Feuertür im Fokus.`

---

### MOTH — Hinterraum, 17:41 Uhr

Der Größere hat gesagt was er sagen wollte. Der Kleinere greift nach dem Päckchen.

Delacroix steht noch am Tisch. Der soziale Moment ist vorbei — noch zwei Sekunden, dann ist das Bauteil in der Jackentasche des Kleineren und auf dem Weg zur Feuertür.

**Was macht MOTH jetzt?**

Kim — das ist dein Moment. Delacroix kann:

- Etwas fallen lassen, stolpern, das Glas kippen — physische Ablenkung, letzter Versuch
- Direkt nach dem Päckchen greifen — Heat explodiert, Tarnung weg, aber das Bauteil bleibt
- Zurücktreten und RAMPART das Signal geben

**Deine Entscheidung.**

---

### RAMPART — Connecticut Avenue, 17:41 Uhr

Der Verfolg

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Initiative 8 — Kaspar hat den Moment.

Ich gehe direkt auf den Verfolger zu, entspannte Körpersprache, so als würd ich ihn kennen. "Hey, Mann — du bist doch der Typ von vorhin, oder? Warte kurz." Schulter antippen, Blickkontakt halten, ihn aus dem Laufrhythmus bringen. Kein Aufsehen, kein Widerstand — einfach soziale Bremse.

Gibt's dafür ne Probe? Täuschung oder Einschüchterung, je nachdem wie's läuft?

**Kim** [Kim]: ok Moths moment!! ich lass das glas fallen — so als ob ich ausrutsche, voll unabsichtlich wirkend

ist das eine Probe oder einfach passiert?

**Mara Voss** [Sarah]: Voss lässt das Notizbuch sinken und tritt einen halben Schritt zur Seite — genau zwischen den Kurier und die Feuertür. Nicht aggressiv, einfach da. Sie sagt ruhig: *"Schade. Ich dachte, Sie kennen das Viertel."* Kleines Lächeln, kein Augenkontakt mit der Tür — sie soll nicht wie eine Blockade wirken, nur wie eine Frau die noch nicht fertig ist.

### Turn 15 — SL

## Szene 2 — Alle drei gleichzeitig, 17:41 Uhr

---

### MOTH — Glas fallen lassen

Delacroix' Ellbogen trifft die Tischkante. Das Glas kippt — Bier ergießt sich über den Tisch, direkt auf das Päckchen, auf die Hände des Kleineren.

**Probe: Täuschung / Unfall simulieren — GES**

`Probe: Unfall → W6: [5] + ⌊GES 5/2⌋ (2) + 0 = 7 vs SG 6 → ERFOLG`

*"Oh Gott — es tut mir so leid—"*

Der Kleinere springt auf, Stuhl schabt über den Boden, er schüttelt die Hände. Das Päckchen liegt auf dem Tisch, durchnässt aber noch da. Der Größere schaut auf, kalt, direkt auf Delacroix.

Finch rührt sich nicht. Er schaut auf das Päckchen.

Drei Sekunden Chaos. Das Bauteil liegt noch auf dem Tisch.

`Kodex: Übergabe unterbrochen. Päckchen exponiert. Heat +1.`

---

### RAMPART — Verfolger abfangen

Kaspar geht auf den Mann zu, entspannte Schultern, leichtes Lächeln.

*"Hey, Mann — du bist doch der Typ von vorhin, oder? Warte kurz."*

Schulter antippen. Der Verfolger stoppt — Reflex.

**Probe: Täuschung / Soziale Bremse — CHA**

`Probe: Soziale Bremse → W6: [2] + ⌊CHA 2/2⌋ (1) + 0 = 3 vs SG 7 → MISS`

Der Mann dreht sich um. Schaut Kaspar an — kurz, direkt, ohne Verwirrung. Jemand der gelernt hat Gesichter zu lesen.

*"Kenn ich nicht."*

Er dreht sich wieder zur Gasse. Aber er hat zwei Sekunden verloren.

`Kodex: RAMPART — Verzögerung minimal. Verfolger fortsetzt Bewegung.`

---

### SPLINTER — Feuertür blockieren

Voss tritt einen halben Schritt zur Seite. Zwischen Kurier und Tür. Lächelt.

*"Schade. Ich dachte, Sie kennen das Viertel."*

Der Kurier schaut sie an. Dann auf ihre Position. Er versteht was sie macht — nicht bewusst, aber der Körper registriert die Blockade.

**Probe: Einschüchterung / Präsenz — CHA**

`Probe: Präsenz → W6: [6] + ⌊CHA 3/2⌋ (1) + 0 = 7 vs SG 7 → ERFOLG (Exploding: [1]) → 8`

Der Kurier macht keinen Schritt zur Tür. Er schaut auf Voss, dann auf den Helm unter seinem Arm, dann wieder auf Voss. Er ist jung, er ist nervös, und eine ruhige Frau die einfach da ste

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Moment — Kaspar gibt den Verfolger auf, das ist klar. Option 2.

Aber ich hätte eine kurze Frage zur Mechanik: Wenn ich als RAMPART jetzt zur Gasse sprinten will, bekomme ich da einen Malus weil ich schon meine Aktion für "Soziale Bremse" verbraucht habe, oder zählt das als neue Runde? Bei DSA wäre das ne gespaltene Aktion mit Abzug, ich will wissen wie das hier gehandhabt wird bevor ich committe.

Und für Kaspar: Er dreht sich um, läuft Richtung Gasse, keine Erklärung, kein Zögern — STR 5 als Barriere zwischen Verfolger und Kurier, das ist der Plan. Er ist groß genug dass das eine Ansage ist auch ohne Worte.

**Kim** [Kim]: okay MOTH greift das Päckchen, jetzt sofort!! und dann ruf ich Kaspar an oder wie funktioniert das mit den COMMS?

**Mara Voss** [Sarah]: Voss hält den Blick auf den Kurier, tippt kurz ins Comlink: *"SPLINTER an alle — halte Tür, Kurier steht. MOTH, wenn du das Päckchen nimmst, tue es jetzt — ich kann hier nicht ewig lächeln."*

### Turn 16 — SL

## Szene 2 → 3 — Alles bricht los, 17:42 Uhr

---

### Jonas — Mechanik-Antwort

Kein DSA-Splitting hier. **Jede Szene ist ein Handlungsfenster** — innerhalb einer Szene kannst du mehrere Aktionen beschreiben, ich würfele für jede die riskant ist. Die "Soziale Bremse" war Szene 2, der Sprint ist jetzt Szene 3. Kein Malus, keine gespaltene Aktion. Du commitest, ich würfele.

---

### Alle drei — gleichzeitig, 17:42 Uhr

---

**MOTH — Päckchen greifen**

Delacroix schaut den Größeren an. Eine Sekunde — er weiß es, sie weiß dass er es weiß.

Dann greift sie über den Tisch.

**Probe: Greifen / Schnelligkeit — GES**

`Probe: Päckchen greifen → W6: [6] + ⌊GES 5/2⌋ (2) + 0 = 8 vs SG 8 → ERFOLG (Exploding: [4]) → 12 — STARKER ERFOLG`

Ihre Hand schließt sich um das Päckchen bevor der Kleinere reagiert. Nass, handgroß, schwerer als erwartet — das Bauteil ist Metall, kein Plastik.

Der Kleinere greift nach ihr — zu spät. Der Größere steht bereits.

Delacroix dreht sich, Päckchen in der Faust, und läuft Richtung Haupteingang.

`Kodex: Bauteil gesichert. MOTH in Bewegung. Heat +2.`

Burst, kurz, ins Comlink während sie läuft: *"Hab's — Hauptausgang—"*

---

**RAMPART — Sprint zur Gasse**

Kaspar dreht sich ohne Erklärung und läuft.

**Probe: Sprint — GES**

`Probe: Sprint → W6: [3] + ⌊GES 4/2⌋ (2) + 0 = 5 vs SG 6 → MISS`

Er ist groß und schwer — nicht gebaut für Sprints auf nassem Pflaster. Der Verfolger hat die Ecke bereits erreicht, tritt in die Gasse ein, sieht Voss, sieht den Kurier, sieht dass etwas nicht stimmt.

Kaspar kommt drei Sekunden später. Der Verfolger steht bereits zwischen ihm und Voss.

Aber er ist da. STR 5, Taktikweste, kein Lächeln mehr.

Der Verfolger dreht sich um. Schaut Kaspar an. Schaut auf Voss. Rechnet.

`Kodex: RAMPART in Gasse. Verfolger eingekesselt zwischen zwei Agenten.`

---

**SPLINTER — hält Position**

Voss steht. Kurier vor ihr, Verfolger hinter ihr — jetzt zwischen Kaspar und ihr.

Der Kurier schaut auf den Verfolger. Auf Kaspar. Auf Voss

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Situation gecheckt. Der Typ ist ruhig und er hat Recht — wir haben das Päckchen. Ich stell mich so auf, dass ich zwischen ihm und dem Kurier bin, Körper leicht seitlich — klassische Nahkampf-Startposition, aber ich greife noch nicht an.

Ich sag zu ihm, ruhig: *"Stimmt. Und jetzt?"* Kurze Pause, dann: *"Du stehst zwischen zwei Leuten die das nicht verlieren wollen. Mach das nicht komplizierter als's sein muss."*

Ich will sehen ob er redet oder zieht — und falls er zieht, bin ich näher dran als er denkt. Sarah, gibt's nen Wahrnehmungs-Wurf ob ich einschätzen kann ob der Typ Schusstraining hat oder eher Nahkampf-Typ ist?

**Kim** [Kim]: ok ich bin draußen auf der straße, mega!! aber der typ hat mein gesicht gesehen oder? soll ich einfach sofort weiterlaufen oder warten auf die anderen

**Mara Voss** [Sarah]: Voss sagt ruhig, ohne die Augen vom Verfolger zu nehmen: *"Stimmt. War für jemand anderen. Jetzt ist es weg — das ist nicht unser Problem und nicht deins."* Sie macht einen halben Schritt zur Seite, öffnet ihm die Richtung Straße. *"Geh."*

### Turn 17 — SL

## Szene 3 — Gasse / Connecticut Avenue, 17:43 Uhr

---

### Kim — draußen auf der Straße

Laufen. Nicht rennen — zügig, Kopf leicht gesenkt, Päckchen unter dem Arm wie ein Notizbuch. Der Größere steht in der Tür, aber er folgt nicht. Zu viele Leute.

Dreißig Meter weiter ist eine Bushaltestelle. Zwei Frauen warten dort, schauen auf ihre Uhren. Normal. Unauffällig.

**Delacroix, kurze Entscheidung:** Haltestelle und warten auf Comlink-Signal, oder weiterlaufen Richtung vereinbarter Treffpunkt?

Burst-Comlink funktioniert bis 200 Meter. Die anderen sind noch in der Gasse.

---

### RAMPART & SPLINTER — Gasse, 17:43 Uhr

Der Verfolger hört beide. Kaspar vorne, Voss seitlich — die Gasse ist schmal, er hat keinen guten Winkel für keinen von beiden.

Er schaut Kaspar an. Schaut auf Voss' offene Richtung zur Straße.

**Probe: Einschätzen / Kampferfahrung lesen — INT**

`Probe: Einschätzen → W6: [4] + ⌊INT 3/2⌋ (1) + 0 = 5 vs SG 7 → MISS`

Kaspar liest ihn nicht vollständig. Die Haltung könnte Schusstraining sein, könnte Nahkampf — der Mantel verdeckt zu viel, das Licht ist zu schlecht. Was er sieht: Der Mann hat beide Hände jetzt sichtbar. Die linke Manteltasche — er hat sie nicht geöffnet.

Das ist eine Entscheidung.

---

Der Verfolger schaut auf Voss' offene Richtung. Drei Sekunden Stille.

Dann sagt er, ruhig wie vorher:

*"Das Päckchen gehört Leuten die nicht vergessen."*

Kein Angriff. Keine Waffe. Er dreht sich zur Straße — Voss hat ihm den Weg geöffnet, er nimmt ihn. Schulter an der Wand, Blick auf Kaspar bis zur letzten Sekunde, dann ist er um die Ecke.

Der Kurier atmet aus. Lehnt immer noch gegen die Wand, Helm fest in beiden Händen, Knöchel weiß.

*"Was zur Hölle—"*

`Kodex: Verfolger abgezogen. Keine Konfrontation. Identität ungeklärt. Aussage gesichert: "Leute die nicht vergessen."`

---

### The Argyle — gleichzeitig

Der Größere ist von der Eingangstür verschwunden. Der Kleinere auch — Tisch leer, Stühle weggeschoben. Finch sitzt allein. Er hat seine Akten

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay kurze Frage zur Mechanik bevor ich entscheide — wenn wir den Kurier befragen, läuft das über SOC oder INT? Weil einschüchtern wäre eher STR/Präsenz, aber Verhör/Ausfragen klingt eher nach INT. Will keinen falschen Stat nehmen.

Und zum Inhalt: Ich würde Option 1 nehmen, Kaspar übernimmt das Gespräch, dreißig Sekunden. Der Typ zittert noch, das ist genau das Fenster. Danach sofort zu MOTH.

**Kim** [Kim]: okay ich warte kurz an der haltestelle und schick den anderen den treffpunkt — was ist nochmal der burst-comlink befehl?

**Mara Voss** [Sarah]: Voss nickt Kaspar kurz zu — Verfolger weg, Gasse sauber — dann wendet sie sich dem Kurier zu. Ruhig, Hände sichtbar.

*"Wer hat dich angeheuert. Name, Kontaktweg, wann."*

Dreißig Sekunden, dann lassen wir ihn gehen.

### Turn 18 — SL

## Szene 3 — Gasse, Kurier-Befragung, 17:43 Uhr

---

### Jonas — Mechanik-Antwort

**Verhör / Ausfragen = CHA.** Soziales ist CHA in ZEITRISS — Einschüchterung, Überzeugung, Täuschung, Verhör. INT ist für Analyse, Technik, Spurenlesen. STR wäre wenn du jemanden physisch unter Druck setzt — Arm verdrehen, gegen die Wand drücken. Hier: Kaspar steht groß da, Voss fragt — das ist CHA mit STR als implizite Drohkulisse. Kein Bonus, aber kein Malus.

---

### Kim — Burst-Comlink

Kein Befehl nötig. Einfach im Chat sagen was Delacroix durchgibt — ich spiele es als kurzes Knacken im Ohrrelais der anderen. *"MOTH an alle — Haltestelle Connecticut, dreißig Meter nord. Päckchen sicher."* So reicht das.

---

### Gasse — Kurier-Befragung

Voss stellt die Frage. Kaspar steht dahinter — nicht bedrohlich, einfach da. Zwei Meter, STR 5, kein Lächeln.

Der Kurier ist neunzehn, vielleicht zwanzig. Lederjacke, billige Stiefel, Helm jetzt vor der Brust wie ein Schild. Er schaut von Voss zu Kaspar und zurück.

**Probe: Verhör / Einschüchterung — CHA (Voss), STR-Drohkulisse (Kaspar passiv)**

`Probe: Verhör → W6: [5] + ⌊CHA 3/2⌋ (1) + 0 = 6 vs SG 6 → ERFOLG, knapp`

Der Kurier redet. Schnell, leise, Augen auf den Gassen-Ausgang.

*"Ich kenn keinen Namen. Ich schwör's — ein Mann hat mich vor drei Tagen angesprochen, beim Diner auf der U Street. Hat mir zwanzig Dollar gegeben, zwanzig mehr wenn ich heute Abend hier warte und ein Päckchen abhole. Ich sollte's zu einer Adresse in Georgetown bringen, Briefkasten, kein Klingeln."*

Er schluckt.

*"Der Mann — Mitte vierzig, grauer Anzug, sprach wie jemand aus dem Norden. Kein Akzent. Kurze Haare, Brille."*

Pause.

*"Das ist alles. Ich hab keine Ahnung was in dem Päckchen ist."*

`Kodex: Kurier-Aussage gesichert. Auftraggeber: Beschreibung männlich, Mitte 40, grauer Anzug, nördlicher Akzent, Brille. Georgetown-Adresse: unbekannt — Kurier kennt nur Briefkasten-Ziel.`

---

**Burst rein — MOTH:**

Knacken im Ohrrelais. *"MOTH an alle — Haltestell

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Kaspar gibt dem Kurier einen langen Blick, dann ein kurzes Nicken Richtung Ausgang. Kein Wort. Der soll einfach verschwinden — je schneller, desto besser für alle.

Aber vorher, leise: *"Georgetown. Welche Straße, welcher Block."* Keine Frage, eher Feststellung. Wenn der Typ redet kriegt er die Information gratis, wenn nicht... Kaspar macht einen halben Schritt nach vorne. Nur einen.

**Kim** [Kim]: MOTH checkt kurz rein — warte auf euch, Päckchen liegt sicher.

Aber hey, dieser Finch sitzt noch da, oder? Das juckt mich irgendwie 😅

**Mara Voss** [Sarah]: Voss sagt leise zum Kurier: „Du hast uns nie gesehen. Geh nach Hause."

Dann zu Kaspar, ohne ihn anzuschauen: „Georgetown-Adresse. Ich will wissen wo der Briefkasten ist, bevor wir springen."

Sie dreht sich Richtung Straße. „Frag ihn noch mal — höflich."

### Turn 19 — SL

## Szene 3 — Gasse, letzter Beat, 17:44 Uhr

---

### Georgetown-Adresse

Kaspar macht den halben Schritt. Der Kurier weicht nicht zurück — er hat keine Energie mehr für Würde — aber er presst sich fester gegen die Wand.

**Probe: Einschüchterung — STR (physische Präsenz als Druckmittel)**

`Probe: Einschüchterung → W6: [4] + ⌊STR 5/2⌋ (2) + 0 = 6 vs SG 5 → ERFOLG`

*"Volta Street. 2800er Block. Grüner Briefkasten, zweite Reihe vom Eingang."*

Er sagt es ohne Zögern — die Information kostet ihn nichts mehr, er will nur weg.

Voss nickt einmal. Kaspar tritt zurück. Der Kurier wartet eine Sekunde, dann geht er — schnell, Helm unter dem Arm, ohne sich umzudrehen. Fünfzehn Sekunden später ist er um die Ecke.

`Kodex: Georgetown-Adresse gesichert. Volta Street, 2800er Block, grüner Briefkasten.`

---

### Kim — Finch

Das juckt Delacroix. Verständlich.

Finch sitzt noch. Durch die Glasscheibe der Argyle — von der Haltestelle aus gerade noch sichtbar — sieht Delacroix wie er aufsteht. Langsam. Nimmt seine Aktentasche. Legt Münzen auf den Tisch.

Er geht. Nicht zur Seitentür. Zum Hauptausgang.

Er kommt in dreißig Sekunden an Delacroix vorbei.

`Kodex: Finch verlässt Bar. Bewegungsrichtung: Hauptausgang, Connecticut Avenue nord.`

**Kim — Delacroix steht an der Haltestelle, Päckchen unter dem Arm. Finch läuft direkt auf sie zu. Was macht MOTH?**

Optionen in Sekunden: Kopf senken und ignorieren. Zur Seite treten. Oder — riskant — kurzen Blickkontakt, um sein Gesicht final zu sichern.

---

`EP 1 · MS 1 · SC 3/12 · PHASE Exfil · MODE CORE · COMMS OK · Px 0/5`
`❤️‍🩹 Voss 13/13 · Kaspar 15/15 · MOTH 12/12 · 🧠 Stress 0 · 👁️ Tarnung: MOTH kompromittiert · 🌀 Heat 3`
`⏱️ Finch: 30 Sekunden bis Haltestelle · Kaspar+Voss: 45 Sekunden bis MOTH`

---

**Intel / Risiken**
- **Volta Street, 2800er Block** — Briefkasten-Adresse gesichert. Sekundärziel partiell erfüllt
- **Finch läuft auf MOTH zu** — er hat ihr Gesicht nicht gesehen, aber Nähe ist Risiko
- **Größerer aus der Bar** — wo i

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich würde tippen:

---

Okay, Adresse ist drin, gut. Für MOTH: Ich würde Option 1 nehmen — Kopf senken, Päckchen verbergen, durchatmen. Tarnung ist schon kompromittiert laut Status, da will ich keinen zusätzlichen Blickkontakt riskieren, auch wenn die Gesichtsbestätigung nice wäre. Wo ist eigentlich der Große aus der Bar geblieben? Der macht mir mehr Sorgen als Finch gerade.

Kaspar und Voss halten Position bis Finch vorbei ist, dann schnell zur Haltestelle — aber ich würde *nicht* Option 3 nehmen solange der Zweite unaccounted ist. Drei Leute die gleichzeitig an einer Haltestelle auftauchen erhöht doch Heat, oder? Was ist der Modifier da?

**Kim** [Kim]: okay MOTH senkt Kopf, Päckchen zwischen die Arme geklemmt, schaut aufs Handy als ob sie auf die Bus-App wartet. Finch soll einfach vorbeilaufen.

**Mara Voss** [Sarah]: Ich tippe:

"Voss an Moth: Kopf runter, lass ihn passieren. Kein Blick. Wir kommen zu dir — noch 45 Sekunden. Halte das Päckchen verdeckt." Dann zu Kaspar, leise: "Wir gehen jetzt."

### Turn 20 — SL

## Szene 3 → 4 — Exfil, Connecticut Avenue, 17:45 Uhr

---

### Jonas — Heat-Mechanik kurz

Drei Leute an einer Haltestelle ist kein automatischer Heat-Anstieg — das ist 1962 D.C., Haltestellen sind voll. Heat steigt durch *auffälliges Verhalten*: Rennen, Schreien, Waffen, Konfrontation, oder wenn jemand die Polizei ruft. Drei Leute die warten: kein Modifier.

**Wo ist der Große?** Gute Frage. Ich würfele das jetzt.

---

### MOTH — Finch passiert

Delacroix schaut aufs Notizbuch — kein Handy, 1962, aber der Effekt ist derselbe. Kopf unten, Päckchen zwischen Arm und Körper, Schulter leicht gedreht.

Finch geht vorbei. Drei Meter Abstand. Er schaut geradeaus — der Gang eines Mannes der gerade etwas abgegeben hat und nicht mehr darüber nachdenken will. Seine Schritte sind gleichmäßig. Er biegt nach links ab, Richtung Metro.

Er sieht Delacroix nicht.

`Kodex: Finch passiert ohne Kontakt. Historisch unberührt. ✓`

---

### Der Große — wo ist er?

**Probe: Umgebungscheck — INT (Voss, Tatortanalyse)**

`Probe: Umgebungscheck → W6: [3] + ⌊INT 6/2⌋ (3) + Talent +2 = 8 vs SG 8 → ERFOLG, knapp`

Voss scannt die Straße während sie mit Kaspar zur Haltestelle geht. Augen links, rechts, Schaufenster als Spiegel.

Da.

Der Große steht zwanzig Meter hinter ihnen auf der anderen Straßenseite. Mantel, keine Eile. Er schaut nicht auf sie — er schaut auf die Stelle wo Delacroix stand. Dann auf die Haltestelle.

Er hat sie nicht verloren. Er wartet ab.

Burst, kurz, an alle: *"Größerer, gegenüber, zwanzig Meter. Beobachtet. Kein Angriff — er sammelt Informationen."*

`Kodex: Größerer identifiziert. Passiv-Observation. Kein unmittelbares Risiko. Merkt sich Gesichter.`

---

### Haltestelle — alle drei, 17:46 Uhr

Kaspar kommt zuerst. Dann Voss. Delacroix steht noch, Päckchen sicher.

Drei Agenten, eine Haltestelle, ein Mann auf der anderen Straßenseite der zuschaut.

Der Bus kommt nicht — das war nie der Plan. Gate-Window ist auf Abruf.

Kaspar, leise: *"Wir haben was er braucht. Er wei

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich tippe:

---

Okay, Größerer ist das Problem. Option 1 ist zu heiß — er sieht genau wo wir hinkommen bzw. verschwinden, das will ich nicht.

Ich würde Ablenkung machen, aber nicht zu kompliziert. Kaspar hat die höchste SOC, oder? Einer von uns geht auf die andere Straßenseite, fragt den Typen nach einer Adresse oder zündet sich eine Zigarette an — irgendwas das seinen Blick auf eine Person fixiert während die anderen zwei durchs Gate gehen. Dann der Dritte nach.

Volta Street lasse ich lieber. Größerer könnte folgen und wir haben das Päckchen schon — Primärziel ist erfüllt, ich will das nicht riskieren für ein Sekundärziel das wir auch später angehen können.

Sarah, kurze Frage: Wenn der Große unsere Gesichter hat und wir zurückkommen — trägt das Heat in zukünftige Sessions? Oder ist das eine rein in-session Variable?

**Kim** [Kim]: okay warte — wenn er uns beobachtet und wir dann einfach *verschwinden*, sieht er das doch oder?? wie funktioniert das Gate nochmal, ist das unsichtbar oder sehen Leute das??

**Mara Voss** [Sarah]: Ich tippe:

„Option 2, aber ich mach die Ablenkung. Voss geht rüber, fragt ihn nach einer Straße — touristisch, harmlos, gibt Kaspar und MOTH Zeit für den Sprung. Dann folge ich nach sobald die beiden weg sind. War die INT-Probe von eben mit meinem Talent-Bonus, also +2?"

### Turn 21 — SL

## Klärungsrunde + Exfil-Plan

---

### Kim — Gate-Sichtbarkeit

Das Gate ist **nicht unsichtbar**. Es ist ein kurzes visuelles Ereignis — Luft flimmert, wie Hitzeflimmern über Asphalt, für etwa zwei Sekunden. Kein Knall, kein Licht, keine dramatische Öffnung. Jemand der direkt hinschaut sieht: drei Leute stehen da, dann stehen zwei da, dann einer, dann keiner.

In der Nacht, auf einer belebten Straße, von zwanzig Metern Abstand: auffällig aber nicht eindeutig. Der Große würde es registrieren. Erklären kann er es nicht — aber er sieht dass ihr *verschwindet*.

Deshalb: Ablenkung macht Sinn.

---

### Sarah — INT-Probe mit Talent

Ja. Tatortanalyse gibt +2 auf INT-Proben zur Spurenanalyse und Beweissicherung. Der Umgebungscheck von eben fiel darunter — Voss liest eine Lage wie einen Tatort. **+2 war korrekt angewendet.**

---

### Jonas — Heat in zukünftigen Sessions

**Ja, das trägt.** Der Große hat Gesichter. Das landet als Eintrag im Fraktions-/Gegner-Netzwerk — wenn dieselbe Fraktion in einer späteren Mission auftaucht, haben sie ein Profil auf MOTH, möglicherweise auf alle drei. Das ist kein sofortiger Malus, aber ein narrativer Haken der sich auszahlt.

`Kodex: Kontinuitätseintrag gesetzt. Größerer — visuelle ID auf MOTH, möglicherweise SPLINTER und RAMPART. Fraktion unbekannt, Georgetown-Verbindung.`

---

### Ablenkung — Exfil-Plan

**Voss geht rüber. Kaspar und MOTH springen. Dann Voss.**

**Probe: Ablenkung / Sozial — CHA (Voss)**

`Probe: Ablenkung → W6: [2] + ⌊CHA 3/2⌋ (1) + 0 = 3 vs SG 7 → MISS`

Voss geht rüber. Der Große dreht sich zu ihr — das klappt. Aber er ist kein Dummkopf. Während Voss nach einer Straße fragt, antwortet er einsilbig und hält den Blick *schräg* — nicht auf Voss, sondern auf die Haltestelle hinter ihr.

Er schaut trotzdem hin.

Er sieht das Flimmern. Zwei Sekunden. Kaspar und Delacroix — weg.

Er schaut Voss an. Lange. Dann sagt er, auf Englisch, ruhig:

*"Volta Street ist drei Blocks west."*

Er weiß dass sie nicht nach Volta Stre

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay der Große hat also ein Profil auf uns — das ist der klassische "wird uns später einholen"-Moment, ich liebe und hasse das gleichzeitig 😅

Sarah, ich würde Option 2 nehmen — irgendwas das er nicht einordnen kann. Ihn kurz in einer Gedankenschleife lassen. Selbst wenn er uns meldet, soll sein Bericht so klingen dass sein Auftraggeber ihn für nicht ganz dicht hält.

**Kim** [Kim]: okay warte — "Volta Street ist drei Blocks west" — meint er das als DROHUNG? wie weiß der überhaupt dass wir die adresse haben??

**Mara Voss** [Sarah]: Voss hält seinen Blick genau drei Sekunden — nicht eine länger. Dann sagt sie, vollkommen neutral: *"Danke."*

Gate aktivieren.

### Turn 22 — SL

## Szene 4 — Exfil, 17:46 Uhr

---

### Kim — kurze Antwort

Der Große hat die Adresse nicht von euch gehört. Er *weiß* sie — weil er zur Operation gehört. Volta Street ist sein Briefkasten, sein Netzwerk, sein Plan. Als Voss danach fragt ohne danach gefragt zu haben, ist die Botschaft klar: *Wir haben euren Kurier geredet.* Das ist keine Drohung. Das ist eine Quittung.

---

### Voss — letzter Beat

*"Danke."*

Vollkommen neutral. Kein Zögern, kein Lächeln, kein Zucken.

Der Große schaut sie an. Das Wort landet falsch — zu ruhig, zu leer, keine Reaktion wo eine sein sollte. Ein Mensch der wirklich nach einer Straße gefragt hat würde *Danke* anders sagen. Dieser Ton ist etwas anderes.

Er öffnet den Mund. Schließt ihn wieder.

Das Flimmern — zwei Sekunden, Luft über heißem Asphalt, Oktober in D.C. — und Voss ist weg.

Er steht allein auf der Connecticut Avenue. Drei Leute, verschwunden. Ein Wort das nicht passt. Keine Erklärung die funktioniert.

`Kodex: Exfil vollständig. Alle drei durch Gate. Größerer — Konfusionseintrag gesetzt. Bericht wird inkohärent wirken.`

---

### Rückkehr — ITI Hangar-Axis, Nullzeit

Pflastersteine werden Metall. Oktoberluft wird Kühlmittelgeruch. Die Gravität setzt sich neu.

Drei Agenten, Hangar-Axis, Nullzeit. Der Techniker an der Wartungsluke schaut kurz auf — Routine. Nickt. Schreibt etwas in sein Clipboard.

Kaspar atmet aus. Delacroix hält das Päckchen noch in beiden Händen — Zeitungspapier, nass vom verschütteten Bier, Metallgewicht darin. Voss landet einen Schritt hinter den anderen, dreht sich kurz um als würde sie noch die Straße im Rücken spüren.

Die Stille der Nullzeit ist immer zu laut nach einem Einsatz.

`Kodex: Gate geschlossen. Zeitkoordinaten 14.10.1962 versiegelt. Tempocom-Bauteil in Gewahrsam.`

---

`EP 1 · MS 1 · SC --/-- · PHASE Debrief · MODE CORE · COMMS OK · Px 0/5`
`❤️‍🩹 Voss 13/13 · Kaspar 15/15 · MOTH 12/12 · 🧠 Stress 0`

---

## DEBRIEF — Mission 1, Episode 1

**Archivarin Mira, ITI Operations, Auswertungsr

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay warte mal kurz — Kaspar levelt auf und kriegt Lizenz Tier I? Was bedeutet das konkret, was ändert sich dadurch für ihn? Und der XP-Fortschritt, brauche ich noch einen weiteren für Lvl 2 oder war das der letzte?

**Kim** [Kim]: warte ich hab level 2?? MOTH hat level 2 bekommen?? das ist so cool ich freu mich so sehr

**Mara Voss** [Sarah]: Voss dreht sich zu Mira um. "Der Große — er hat 'Volta Street' bestätigt bevor ich die Adresse nannte. Er gehört zur Operation, nicht nur zur Peripherie."

### Turn 23 — SL

## HQ — Klärungsrunde + Mira-Reaktion

---

### Jonas — Lizenz Tier I & XP

**Lizenz Tier I** bedeutet konkret:

| Vorher (Tier 0) | Jetzt (Tier I) |
|---|---|
| Nur Tier-0-Ausrüstung ohne Genehmigung | Tier-1-Ausrüstung kaufen und tragen ohne Sondergenehmigung |
| Kein Zugang zu ITI-Quartiermeisterei Stufe 1 | Quartiermeisterei Stufe 1 offen |
| Kein Zugang zu Tier-1-Implantat-Installation | Klinik Tier-1-Implantate ohne Warteliste |
| Eingeschränkte Missionsauswahl | Standard-Core-Missionen alle zugänglich |

Praktisch: Kaspar kann jetzt dieselbe Ausrüstung kaufen die Voss schon hat. Keine Genehmigungen, kein Umweg über andere.

**XP:** Lvl 1 hat Schwelle 1 — du brauchst 1 XP pro Level in Phase 1 (Lvl 1–10). Du hast 1 XP bekommen. Das war der letzte. Kaspar ist jetzt **Lvl 2**, XP-Zähler resettet auf 0/2 für den nächsten Aufstieg.

`Kodex: Kaspar — Lvl 1 → Lvl 2. Nächste Schwelle: 2 XP.`

---

### Kim — ja, MOTH hat Lvl 2

Delacroix ist Lvl 2. Erste Mission, erste Stufenwahl. Das Glas auf dem Tisch hat sich ausgezahlt.

`Kodex: Delacroix — Lvl 1 → Lvl 2. Nächste Schwelle: 2 XP.`

---

### Sarah — Voss zu Mira

Mira hört zu. Legt den Stift hin.

*"Ja."* Keine Überraschung in ihrer Stimme — eher Bestätigung von etwas das sie bereits vermutet hat. *"Er hat die Adresse nicht gelernt. Er hat sie gewusst. Das bedeutet er ist nicht Peripherie — er ist Koordination."*

Sie dreht den Stuhl leicht.

*"Drei Rollen heute Abend: Finch als Überbringer, der Kleinere als Empfänger, der Größere als Aufpasser. Dazu ein Kurier für den Transport und ein Verfolger der von außen sichert."* Eine kurze Pause. *"Das ist Struktur. Das ist nicht improvvisiert."*

Sie tippt etwas.

*"Der Verfolger hat gesagt: 'Leute die nicht vergessen.' Das ist kein Zufallssatz. Das ist ein Organisations-Idiom — etwas das man intern sagt, nicht gegenüber Fremden."* Kurzer Blick auf Voss. *"Er hat euch das gesagt weil er wollte dass ihr es weitertragt."*

`Kodex: Fraktionsprofil aktualisiert. Organisationsst

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay Level 2, nice. Ich nehm +1 STR — Kaspar ist halt der der reinläuft wenn's eng wird, das soll sich auch in den Werten zeigen. STR 6 macht aus meiner Sicht Sinn bevor ich in Talente investiere.

Und zu Mira: "Organisations-Idiom" klingt fast wie ein Erkennungssatz. Die wollten dass wir das weitertragen — aber warum? Die testen ob wir eine Verbindung aufbauen oder die warnen uns?

**Kim** [Kim]: ok lvl 2 nice!! was ist nochmal SYS genau? ich glaub ich nehm Attribut aber ich weiß nicht welches Delacroix am meisten braucht 😅

**Mara Voss** [Sarah]: Voss nickt langsam bei Miras letztem Satz — das ist der Teil der sie beschäftigt.

"Er wollte dass wir es weitertraten. Entweder Warnung oder Einladung — beides ist unangenehm."

Sie lehnt sich zurück. "Wenn sie wissen dass jemand das Bauteil hat, suchen sie gerade rückwärts. Finch ist das schwächste Glied."

> **⚠️ Finding [TERMINOLOGIE]:** SL nutzt 'HP' statt 'LP'

### Turn 24 — SL

## HQ — Level-Up & Analyse

---

### Jonas — STR 5→6

`Kodex: Kaspar — STR 5 → 6. Würfeltyp bleibt W6 (W10 erst ab Basis 11).`

Kaspar ist jetzt HP 16/16 (10 + STR 6). Nahkampf-Taktik-Bonus läuft weiter auf W6 mit +2.

**Korrektur HP:**
`Kodex: Kaspar — HP-Maximum aktualisiert: 15 → 16.`

---

### Kim — SYS & Attribut-Beratung

**SYS kurz:** Implantat-Slots. Delacroix hat SYS 2, einen Slot belegt (Adrenalin-Regulator). Ein freier Slot bleibt. +1 SYS würde einen dritten Slot öffnen — nützlich wenn du mehr Implantate willst, aber nicht dringend.

**Welches Attribut für MOTH?**

| Attribut | Aktuell | Effekt von +1 |
|---|---|---|
| CHA | 5 | Täuschung, Verhör, Stress — schon stark, +1 bringt wenig Sprung |
| GES | 5 | Schleichen, Ausweichen, Schnelligkeit — gleichwertig zu CHA |
| INT | 5 | Technik, Analyse, Spurenlesen — Ergänzung zu Voss' Profil |
| STR | 2 | Nahkampf, Kraft — Delacroix ist keine Kämpferin, aber 2 ist sehr niedrig |
| TEMP | 1 | Zeitphänomene, Px-Aufbau — TEMP 2 ändert noch nichts mechanisch |

**Empfehlung für MOTHs Rolle:** CHA 6 macht sie zur besten Sozialagentin der Gruppe — kein W10 noch, aber +3 Floor bei CHA-Proben statt +2. Oder STR 3 als kleiner Sicherheitspuffer falls sie mal im Nahkampf landet.

**Kim — was fühlt sich für Delacroix richtig an?**

---

### Mira — Finch & die Warnung

Mira schaut Voss an. Nickt kurz — die Einschätzung ist richtig.

*"Finch ist exponiert. Er weiß was er übergeben hat, auch wenn er nicht weiß was es ist. Wenn sie rückwärts suchen, kommen sie zu ihm."*

Sie tippt. Eine neue Zeile erscheint auf dem Terminal.

*"Wir setzen einen passiven Marker auf Finchs Akte. Kein Eingriff — er lebt bis 1987, das bleibt so. Aber wenn sich in seiner Umgebung etwas bewegt, wissen wir es."*

Dann, zu Kaspars Frage:

*"Warnung oder Einladung."* Sie wiederholt es, als würde sie es abwägen. *"Der Verfolger war professionell. Er hätte nichts sagen müssen — ihr hattet das Päckchen, die Konfrontation war vorbei. Er hat es trotzdem gesa

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Schreibe ich kurz rein, während Kim noch überlegt:

„Miras Analyse klingt logisch — eine vorbereitete Botschaft bedeutet, die Organisation hat schon damit gerechnet dass das Päckchen verloren gehen könnte. Die hatten also einen Plan B. Das gefällt mir nicht."

Kurze Pause, dann:

„Zu meinem Level-Up: STR 6, alles klar. HP 16 — Sarah, gilt der Punkt rückwirkend für die letzte Mission oder starte ich frisch damit?"

**Kim** [Kim]: okay CHA dann! delacroix redet sich aus allem raus, das passt 😄

**Mara Voss** [Sarah]: Voss lehnt gegen den Türrahmen und schaut Mira an. "Die Botschaft war für uns — nicht für Finch. Sie wollten, dass wir wissen, dass sie wissen, dass wir suchen."

Dann, leiser: "Volta Street. Das ist der nächste Zug."

### Turn 25 — SL

## HQ — Finale Bögen & Save

---

### Jonas — HP rückwirkend?

HP-Maximum steigt sofort — du startest **jetzt** mit 16/16. Die letzte Mission ist abgeschlossen, du kommst gesund zurück, der Bonus gilt ab diesem Moment. Kein rückwirkender Effekt auf vergangene Szenen nötig.

---

### Kim — CHA 5→6

`Kodex: Delacroix — CHA 5 → 6. Stress-Maximum aktualisiert: 13 → 14. Würfeltyp bleibt W6.`

---

### Mira — letztes Wort

*"Volta Street ist der nächste Zug."* Mira wiederholt Voss' Satz nicht — sie nickt einmal, kurz, und schreibt etwas auf ihr Clipboard.

*"Wenn ihr bereit seid."*

Sie lässt das offen. Kein Druck. Aber die Zeile hängt im Raum.

---

## Finale Charakterbögen — nach Mission 1

---

### MARA VOSS — SPLINTER

```
Name     : Mara Voss
Callsign : SPLINTER
Spieler  : Sarah
Rang     : Feldagentin
Lvl      : 2  |  XP: 1/2

ATTRIBUTE
  STR   3      GES   6
  INT   6      CHA   3
  TEMP  4      SYS   2

HP      : 13/13      Stress  : 0/11
WALLET  : 330 CU     ITI-Ruf : 1  |  Lizenz Tier I

TALENTE
  Tatortanalyse (Basis) — +2 INT Spurenanalyse

AUSRÜSTUNG
  Kompaktpistole Brixon-4     Tier 1 | 2-3 LP
  Verstärktes Einsatzjackett  Tier 1 | DR 1
  Handscanner Kodex-Link
  Rauchgranate ×2
```

---

### REN KASPAR — RAMPART

```
Name     : Ren Kaspar
Callsign : RAMPART
Spieler  : Jonas
Rang     : Feldagent
Lvl      : 2  |  XP: 0/2

ATTRIBUTE
  STR   6      GES   4
  INT   3      CHA   2
  TEMP  4      SYS   2

HP      : 16/16      Stress  : 0/10
WALLET  : 190 CU     ITI-Ruf : 1  |  Lizenz Tier I

TALENTE
  Nahkampf-Taktik (Basis) — +2 STR Nahkampf

AUSRÜSTUNG
  Stun-Schlagstock verstärkt  Tier 1 | 2-3 LP
  Dienstpistole P-7           Tier 1 | 2-3 LP
  Taktikweste                 Tier 1 | DR 1
  Handfessel-Kit ×4
  Erste-Hilfe-Injektor ×3
```

---

### INES DELACROIX — MOTH

```
Name     : Ines Delacroix
Callsign : MOTH
Spieler  : Kim
Rang     : Feldagentin
Lvl      : 2  |  XP: 0/2

ATTRIBUTE
  STR   2      GES   5
  INT   5      CHA   6
  TEMP  1      SYS   2

HP      

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay nice, 16/16 — das fühlt sich gut an. Bin bereit für Mission 2, aber vorher kurz: Hat Ren noch Zeit, bei der Quartiermeisterei vorbeizuschauen? 190 CU sind nicht viel, aber vielleicht gibt's was Sinnvolles für Nahkampf. Sonst direkt Briefing, bin dabei.

**Kim** [Kim]: 4 — direkt weiter! Aber warte mal, mein Stress-Max ist jetzt 14? Das ist wegen dem Implantat-Ding plus CHA, oder?

**Mara Voss** [Sarah]: Voss nickt Mira kurz zu. "Volta Street. Wir sind bereit."

!save

### Turn 26 — SL

## Kurze Antworten + Save

---

### Kim — Stress-Max 14

Genau richtig gerechnet:

> Stress-Max = 8 + CHA (6) = **14** + Adrenalin-Regulator (+2, bereits eingerechnet beim Kauf) = **14**

Warte — kurze Korrektur. Der Adrenalin-Regulator gibt +2 auf Stress-Max, das steht im Item. Ich hatte das bereits beim Kauf eingerechnet (daher 13 vor Level-Up). Nach CHA 5→6:

> 8 + CHA 6 = 14, Adrenalin-Regulator +2 = **16**

`Kodex: Delacroix — Stress-Maximum korrigiert: 14 → 16. Adrenalin-Regulator +2 addiert.`

Entschuldigung für den Fehler im Bogen oben — Delacroix hat **Stress 0/16**.

---

### Jonas — Quartiermeisterei

Kurzer Abstecher, fünf Minuten. Osei zeigt Kaspar was verfügbar ist:

| Item | Tier | Preis | Effekt |
|---|---|---|---|
| Verstärkter Kampfhandschuh | 1 | 80 CU | +1 LP im Nahkampf, kein Waffen-Slot |
| Knieschützer taktisch | 1 | 60 CU | DR +1 gegen Beinschüsse/Tritte |
| Erste-Hilfe-Injektor | 0 | 30 CU | +3 HP, Einmalnutzung |
| Signalstörer-Patch | 1 | 60 CU | +1 Schleichen vs. Elektronik, 1× |

190 CU — Kaspar kann sich eines leisten und hätte noch Reserve. **Jonas, kaufst du etwas?**

---

### !save

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP1-MS1-HQ-POST",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 1,
    "px": 0,
    "px_state": "stable",
    "mode": "core",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-VOSS-01",
      "name": "Mara Voss",
      "callsign": "SPLINTER",
      "rank": "Feldagentin",
      "lvl": 2,
      "xp": 1,
      "origin": { "epoch": "unbekannt", "hominin": "Homo sapiens sapiens", "role": "Analystin" },
      "attr": { "STR": 3, "GES": 6, "INT": 6, "CHA": 3, "TEMP": 4, "SYS": 2 },
      "hp": 13,
      "hp_max": 13,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        { "name": "Tatortanalyse", "tier": "Basis", "effect": "+2 INT Spurenanalyse; triviale Tatortlesung

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich nehme den Verstärkten Kampfhandschuh für 80 CU. Passt perfekt zu Kaspars Stil, und der freie Waffen-Slot ist ein netter Bonus. Bleiben noch 110 CU in Reserve — solide.

**Kim** [Kim]: haha okay 16 ist besser als 14, kein stress (buchstäblich)

wartet Jonas noch oder soll ich schon was machen?

**Mara Voss** [Sarah]: Okay, ich glaube ich hab Voss' Werte gerade falsch im Kopf — laut Save steht GES 6 und INT 6, aber im Charakter-Header oben steht noch GES 5 / INT 5. War das der Level-Up aus Session 1?

### Turn 27 — SL

## Klärung + Quartiermeisterei + Briefing-Freigabe

---

### Sarah — Voss' Werte

Ja, genau. Die GES 5 / INT 5 waren die **Basis-Startwerte** (18 Punkte, Lvl 1). Der Level-Up aus Session 1 — den wir als "bereits im Sheet eingearbeitet" behandelt haben — hat GES auf 6 und INT auf 6 gebracht. Der Save ist korrekt. Wenn du irgendwo noch 5/5 siehst, ist das ein alter Header der nicht aktualisiert wurde.

**Gültig: GES 6, INT 6.** Alles andere ignorieren.

---

### Jonas — Kampfhandschuh

`Kodex: Kaspar — Wallet 190 → 110 CU. Verstärkter Kampfhandschuh ausgerüstet. Nahkampf +1 LP passiv.`

Osei legt den Handschuh auf den Tresen — schwarzes Leder, Knöchelpolsterung, Metallverstärkung innen. Kein Wort. Kaspar zahlt, zieht ihn an, macht eine Faust. Passt.

---

### Kim — wartet ihr aufeinander?

Nein, ihr seid alle bereit. Jonas hat gekauft, Sarah hat bestätigt, Kim hat Level-Up gewählt. Briefing kann starten.

---

## Finale Ausrüstung vor Mission 2

```
KASPAR — carry aktualisiert:
  Verstärkter Kampfhandschuh   Tier 1 | +1 LP Nahkampf, kein Slot
  Stun-Schlagstock verstärkt   Tier 1 | 2-3 LP
  Dienstpistole P-7            Tier 1 | 2-3 LP
  Taktikweste                  Tier 1 | DR 1
  Handfessel-Kit ×4
  Erste-Hilfe-Injektor ×3
  Wallet: 110 CU
```

---

## Regie-Layer — vor Briefing Mission 2

Mira wartet bereits im Briefingraum. Bevor sie anfängt, legt sie kurz eine Akte auf den Tisch — Deckblatt nach unten.

*"ITI-Labor hat das Bauteil geöffnet."* Eine Pause. *"Ihr solltet das hören bevor ihr den nächsten Auftrag bekommt."*

Sie dreht die Akte um. Oben: ein einzelner Satz, handgeschrieben, Archivstempel daneben.

**"Bauteil-Seriennummer: nicht in ITI-Datenbank. Nicht in bekannten Fraktionsdatenbanken. Fertigungsdatum: unbekannt."**

Darunter, kleiner: *"Materialanalyse laufend. Erste Einschätzung: Legierung existiert in keiner bekannten Epoche."*

Mira schaut die drei an.

*"Jemand hat ein Gerät aus einer Zeit gebaut die wir noch nicht kennen — oder die wir nicht mehr 

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Bauteil aus einer unbekannten Epoche — das ist eine Hausnummer. Ich frag mich ob das Zeitreise-Paradoxon wird oder eher Zukunftstechnologie die jemand rückwärts eingeschleust hat.

Zu Georgetown: Tageslicht-Einsatz, kein Cover, Wohnviertel. Ich würde sagen wir brauchen einen Plan bevor wir einfach an die grüne Tür klopfen. Kaspar kann Nahkampf aber er ist kein Einbrecher — wie läuft das bei einem verdeckten Einbruch tagsüber ab, gibt's da einen Ansatz-Modifikator auf GES oder sowas? Und was haben wir an Recon-Möglichkeiten vor dem Reingehen — können wir das Haus erst mal von außen beobachten?

**Kim** [Kim]: okay warte — "keine Epoche die wir kennen" bedeutet das Ding kommt aus der ZUKUNFT?? 😳

**Mara Voss** [Sarah]: Okay, GES 6 / INT 6 ist gespeichert, danke für die Klarstellung.

Voss lehnt über den Grundriss und tippt auf den Hinterausgang. "Keller zuerst oder oben anfangen — was meint ihr? Wenn der Große noch drin ist, will ich wissen wo er schläft, bevor wir uns durch das Erdgeschoss tasten."

### Turn 28 — SL

## Briefing — letzte Fragen, dann Sprung

---

### Kim — Zukunftstechnologie?

`Kodex: Materialanalyse unvollständig. Hypothesen: (a) Zukunftsepoche, (b) abweichende Zeitlinie, (c) unbekannte Fertigungsmethode in bekannter Epoche. Keine Bestätigung möglich bis Analyse abgeschlossen.`

Mira, trocken: *"Wir wissen es nicht. Das ist das Problem."*

---

### Jonas — verdeckter Einbruch tagsüber

**Ansatz-Modifikator:** Ja. Tageslicht-Einbruch in ein Wohnviertel läuft über **GES** (Bewegung, Schlösser, unauffälliges Vorgehen). Modifier je nach Zugang:

| Zugang | Basis-SG | Modifier |
|---|---|---|
| Haustür, Schloss knacken | SG 9 | +1 Heat wenn Nachbar schaut |
| Hinterausgang, Gasse | SG 8 | weniger Sichtbarkeit |
| Fenster, Erdgeschoss | SG 7 | aber sichtbar von Straße |
| Keller, Lichtschacht | SG 8 | niedrig, Schmutz, eng |

Kein spezielles Einbrecher-Talent = keine Automatik, aber GES 4 mit Floor +2 ist solide. Voss mit GES 6 wäre die bessere Wahl fürs Schloss wenn nötig.

**Recon-Möglichkeiten:** Ja — Option 3 war genau das. Ihr könnt eine Stunde beobachten, kostet Zeit aber gibt Kontext. Ich würfele dann eine Wahrnehmungsprobe und sage euch was ihr seht.

---

### Sarah — Keller oder oben?

Mira zeigt auf den Grundriss.

*"Keller hat keinen Fensterblick zur Straße. Wenn er drin ist, schläft er wahrscheinlich oben — aber arbeitet er möglicherweise unten. Lager, Ausrüstung, Kommunikation. Keller zuerst gibt euch Kontext, oben gibt euch den Mann."*

Sie tippt auf den Hinterausgang.

*"Wenn ihr durch hinten reingeht: Keller hat eine direkte Verbindung vom Hintereingang laut Grundriss. Erdgeschoss liegt dazwischen. Oben ist die letzte Station."*

---

### Gruppenplan — sammeln

Bevor ich den Sprung starte: kurze Abstimmung.

**Vorgeschlagener Plan aus den Inputs:**
- **Observation zuerst** — 30–60 Minuten, Hinterausgang und Straße
- **Eingang: Hinterausgang / Gasse** — weniger sichtbar
- **Route drin: Keller → Erdgeschoss → oben**
- **MOTH vorne** bei sozialem Kontak

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Plan passt für mich. Observation first, dann Hinterausgang, Keller-Route.

Eine kurze Frage noch an Mira: Wenn wir im Keller auf Ausrüstung oder Dokumente stoßen — nehmen wir Fotos oder packen wir physisch ein? Ich frag weil das die Zeit drin beeinflusst und ob SPLINTER einen Rucksack braucht.

**Kim** [Kim]: okay also wir wissen es einfach nicht, cool cool

ich bin für Plan 1, Recon macht Sinn. letztes Mal sind wir einfach reingestürmt und das war... naja 😅

**Mara Voss** [Sarah]: Voss nickt knapp. "Plan bestätigen. Recon ist keine verlorene Zeit — Überraschungen im Treppenhaus kosten mehr."

Sie tippt kurz auf die Keller-Route im Grundriss. "Ich geh vor, wenn wir drin sind. SPLINTER macht Analyse, RAMPART hält den Rückweg."

### Turn 29 — SL

## Briefing — letzter Beat, dann Sprung

---

### Jonas — Fotos oder physisch einpacken?

Mira, ohne aufzuschauen vom Terminal:

*"Beides. Handscanner Kodex-Link macht Bilderfassung — Dokumente, Ausrüstung, alles was ihr seht. Physisch mitnehmen nur was klein und eindeutig relevant ist. Kein Rucksack nötig, aber Voss' Handscanner sollte voll geladen sein."*

Sie schaut kurz auf.

*"Wenn ihr ein zweites Bauteil findet — nicht anfassen ohne Handschuhe. Wir haben noch keine Ahnung was das Ding sendet."*

`Kodex: Handscanner Kodex-Link — Bilderfassung aktiv. Kapazität: unbegrenzt lokal. Upload bei Rückkehr.`

---

### Kim — "naja" 😅

Das Glas hat das Päckchen gerettet. Keine Entschuldigung nötig.

---

### Mira — letztes Wort vor Sprung

Sie klappt die Akte zu.

*"Einer noch: Wenn der Große drin ist und euch erkennt — das ist kein Verhör-Auftrag. Ihr sichert euch und kommt raus. Identität bestätigen reicht, wir holen ihn anders."*

Kurze Pause.

*"Fragen?"*

---

Stille im Briefingraum. Grundriss noch auf dem Projektionstisch. Grüne Tür, Georgetown, 1962.

Kaspar steht auf. Delacroix zieht die Jacke gerade. Voss faltet den Grundriss — einmal, zweimal, Brusttasche.

Bereit.

---

## Sprung — Georgetown, Washington D.C., 14. Oktober 1962

Transferkorridor, drei Kabinen, Kühlmittelgeruch. Derselbe Techniker, derselbe Clipboard-Blick.

`Kodex: Zielkoordinaten geladen. Georgetown, D.C., 09:43 Uhr EST, 14.10.1962. Transferfenster: 4 Sekunden.`

Gravität kippt. Pflastersteine.

---

`EP 1 · MS 2 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Px 0/5`
`Voss Lvl 2 ▓▓░░░░░░░░ 1/2 · Kaspar Lvl 2 ▓▓░░░░░░░░ 0/2 · MOTH Lvl 2 ▓▓░░░░░░░░ 0/2`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress 0 · 👁️ Tarnung: Zivilkleidung`
`Obj: Haus Georgetown infiltrieren · Exfil: offen`

---

## Szene 1 — Volta Street, 09:43 Uhr

Oktober in Georgetown ist anders als October in D.C.-Mitte. Ruhiger. Die Häuser hier haben Gärten, kleine Zäune, Briefkästen mit Namensschildern. Bäume mit Herbstlau

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Hintereingang klingt gut — die schiefe Tür ist ein Geschenk. Ich würd sagen wir warten bis die Nachbarin wieder rein ist und gehen dann über die Mauer, Kaspar zuerst als Sicherung. Ich mach die Tür auf, Nahkampf ist mein Ding falls da drin jemand überrascht reagiert.

Kurze Frage an Sarah: Gibt's für das Aufdrücken der schiefen Tür einen GES-Wurf oder eher STR, weil das Holz gequollen ist?

**Kim** [Kim]: okay die alte frau ist ein problem oder? was machen wir mit ihr

**Mara Voss** [Sarah]: Voss sagt leise, ohne die Gasse aus den Augen zu lassen: „Einer drin, Erdgeschoss links. Hintertür ist unser Einstieg — das Holz gibt nach, kein Schloss außen."

Sie nickt kurz zur Nachbarin. „Wir warten bis sie reingeht."

### Turn 30 — SL

## Szene 1 — Warten, 09:58 Uhr

---

### Jonas & Sarah — Türmechanik

Gute Frage. **Gequollenes Holz aufdrücken = STR.** Das ist Kraftakt, kein Präzisionswerk. GES wäre für ein Schloss oder lautloses Öffnen — hier ist das Problem das Holz selbst das klemmt. Wenn ihr lautlos sein wollt: STR-Probe mit Malus -1 für Lärm-Kontrolle, oder Voss macht es mit GES und nimmt einen Versuch mehr.

Kaspar mit STR 6 ist die richtige Wahl. Er drückt einmal, die Tür gibt nach.

---

### Kim — die Nachbarin

Kein Problem, nur Timing. Sie ist kein Feind — sie hängt Wäsche auf. Solange ihr wartet bis sie rein ist, sieht sie nichts. Option 1 war genau das: warten.

---

### Warten — 09:58 Uhr

Voss beobachtet. Kaspar lehnt an der Gassenwand, Arme verschränkt, sieht aus wie jemand der auf einen Freund wartet. Delacroix schaut auf die Straße.

Die Nachbarin hängt das letzte Laken auf. Nimmt den leeren Korb. Schaut einmal kurz in die Gasse — niemand Interessantes — und geht zur Hintertür ihres Hauses.

Tür zu. Stille.

`Kodex: Beobachtungsfeld frei. Zeitfenster: offen.`

Neun Uhr achtundfünfzig. Oktoberlicht, grau und flach. Der Betonhof hinter dem Zielhaus liegt still.

---

## Szene 2 — Hintereingang, 09:59 Uhr

Kaspar geht zuerst. Mauer einen Meter zwanzig — er greift oben drüber, zieht sich hoch, landet leise auf dem Beton. Voss nach ihm, dann Delacroix.

Der Hof ist klein. Zwei Mülltonnen, ein toter Blumenkübel, Betonplatten die sich gehoben haben. Die Holztür zum Haus steht schief im Rahmen — man sieht den Spalt unten, drei Zentimeter Tageslicht.

Kaspar legt die Hand flach gegen das Holz. Fühlt den Widerstand.

**Probe: Tür aufdrücken — STR, Lärm-Kontrolle**

`Probe: Aufdrücken (lautlos) → W6: [5] + ⌊STR 6/2⌋ (3) + 0 = 8 vs SG 8 → ERFOLG, knapp`

Er drückt langsam, gleichmäßig. Das Holz gibt mit einem kurzen, gedämpften Knarzen nach — nicht laut, aber hörbar wenn jemand direkt dahinter steht. Die Tür schwingt auf.

Dahinter: ein schmaler Flur. Dunkel. Linoleum-Boden, eine Garderobe 

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, der Mantel ist ein Fund. Auge über Anker — hat jemand das schon mal irgendwo gesehen? Ich kenn das Logo nicht.

Kurze Frage zur Taktik: Ich würd sagen wir checken zuerst den Raum rechts, bevor wir die Treppe nehmen — wenn der Große noch unten ist wollen wir nicht mit dem Rücken zu einer ungesicherten Tür dastehen. Voss geht an die Wand neben dem Rahmen, ich stoße die Tür langsam auf. Machen wir das?

**Kim** [Kim]: okay warte mal — das Auge über dem Anker, das ist doch kein Zufall oder?? und der Mantel hängt noch da, also ist er IRGENDWO im Haus 😬 gehen wir erst die rechte Tür checken bevor wir die Treppe nehmen?

**Mara Voss** [Sarah]: Voss dreht das Streichholzheftchen einmal um — schaut das Logo an, prägt es sich ein, legt es zurück exakt wie es lag.

Dann flüstert sie zu Kaspar: "Auge über Anker. Kennen wir nicht — heißt, die kennen uns auch nicht. Vorteil." Sie nickt zur halb offenen Tür rechts. "Ich check das zuerst, ihr sichert den Flur."

### Turn 31 — SL

## Szene 2 — Flur, rechte Tür, 10:01 Uhr

---

### Jonas & Kim — Auge über Anker

`Kodex: Logo-Abfrage läuft. ITI-Archiv: kein Treffer. Bekannte Fraktionsdatenbanken: kein Treffer. Hypothese: Unterorganisation oder neue Fraktion, noch nicht dokumentiert.`

Kaspar schüttelt kurz den Kopf. Nichts. Voss' Einschätzung ist richtig — wenn das ITI sie nicht kennt, haben die auch kein Profil auf das ITI. Noch nicht.

---

### Rechte Tür — Voss geht vor

Voss an die Wand, Handscanner weg, Hände frei. Kaspar nimmt Position gegenüber dem Rahmen — Sichtlinie auf den Flur, Rücken zur Hinterausgang-Tür. Delacroix drei Schritte zurück, Blick zur Treppe.

Voss schiebt die halb offene Tür mit zwei Fingern weiter auf. Langsam. Kein Knarzen.

**Probe: Schleichen / Lautloses Vorgehen — GES (Voss)**

`Probe: Tür öffnen → W6: [4] + ⌊GES 6/2⌋ (3) + 0 = 7 vs SG 6 → ERFOLG`

Die Tür schwingt auf.

---

Eine Küche. Klein, funktional, 1962-Standard — Emailherd, Kühlschrank der leise summt, ein Tisch mit zwei Stühlen. Aber:

Der Tisch ist nicht leer.

Zwei Kaffeetassen — eine benutzt, eine unberührt. Ein Aschenbecher mit einer halb gerauchten Zigarette, erloschen aber noch nicht kalt. Ein aufgeschlagenes Notizbuch, Seiten eng beschrieben, kyrillische Schrift, kleine sorgfältige Buchstaben. Daneben: eine Straßenkarte von Washington D.C., mehrere Stellen mit Bleistift markiert.

Und auf dem Emailherd: ein Topf mit Wasser, noch warm.

Zwei Tassen. Zwei Stühle. Einer hatte Besuch.

`Kodex: Küche — zwei Personen anwesend gewesen. Zweite Person unbekannt. Zeitfenster des Besuchs: innerhalb der letzten Stunde.`

Voss steht still. Schaut auf die unberührte Tasse. Schaut auf die Karte.

**Probe: Kartenanalyse — INT, Tatortanalyse**

`Probe: Kartenanalyse → W6: [6] + ⌊INT 6/2⌋ (3) + Talent +2 = 11 vs SG 8 → STARKER ERFOLG (Exploding: [2]) → 13`

Die Bleistift-Markierungen sind keine zufälligen Punkte. Voss liest sie in Sekunden:

Drei Markierungen — Pentagon, Weißes Haus, und ein dritter Punkt den sie s

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay moment — Kaspar hat doch INT 3, oder? Wäre das nicht W6 + 1 statt +3? Ich frag nur weil Voss da deutlich besser ist, kein Problem wenn das ihre Probe war.

Zu den Optionen: Kaspar sichert den Flur Richtung Treppe, Voss macht den Scan. Simultanes Vorgehen — sie erfasst die Dokumente, ich hab Auge auf den Aufgang falls die zweite Person runterkommt. Kombination aus 1 und 2 quasi. Wie lang schätzt du bis Voss fertig ist?

**Kim** [Kim]: warte mal — "Tarnung: kompromittiert" heißt die wissen wer wir sind?? und das foto ist von GESTERN?

ich würde sagen erstmal Treppe, die zweite Person könnte uns hören

**Mara Voss** [Sarah]: Okay das Foto ist ein Problem. Voss nimmt den Handscanner — Notizbuch und Karte, alles, so schnell es geht. Dann Treppe. Wenn die zweite Person noch im Haus ist wollen wir nicht, dass sie durch den Hinterausgang verschwindet während wir hier stehen und lesen.

### Turn 32 — SL

## Szene 2 — Simultanaktion, 10:02 Uhr

---

### Jonas — INT-Probe Klarstellung

Richtig aufgepasst. Die Kartenanalyse war **Voss' Probe**, nicht Kaspars — sie hat den Handscanner, sie liest den Tatort. INT 6, Tatortanalyse-Talent, alles korrekt. Kaspar mit INT 3 wäre W6 + 1 gewesen — du hast recht, aber du warst nicht der Würfelnde. Kein Fehler im Ergebnis.

---

### Kim — Tarnung kompromittiert

Ja. Das Foto ist von gestern Abend, Connecticut Avenue. Die Gegenseite hatte Überwachung laufen parallel zu eurer Operation — während ihr Finch beobachtet habt, hat jemand euch beobachtet. "Tarnung kompromittiert" heißt: eure Gesichter sind bekannt, eure Deckidentitäten sind verbrannt. Nicht eure Namen, nicht ITI — aber die Gesichter.

---

### Simultanaktion — Scan + Sicherung

Kaspar in den Flur, Rücken an die Wand neben dem Küchendurchgang, Blick zur Treppe. Schlagstock an der Seite, Hände frei. Stille im Haus — aber die Art Stille die aufmerksam ist.

Delacroix bleibt am Hinterausgang. Fluchtweg offen halten.

Voss arbeitet.

**Probe: Schnell-Scan — INT, Tatortanalyse**

`Probe: Schnell-Scan → W6: [5] + ⌊INT 6/2⌋ (3) + Talent +2 = 10 vs SG 7 → ERFOLG`

Zwanzig Sekunden. Handscanner über Notizbuch, Seite für Seite — zu schnell um zu lesen, aber die Optik erfasst alles. Karte, beide Seiten, alle Markierungen. Das Foto — sie lässt es liegen, fotografiert es, legt es exakt zurück.

`Kodex: Scan abgeschlossen. Notizbuch 14 Seiten, Karte, Foto — lokal gespeichert. Upload bei Rückkehr.`

Voss schiebt den Handscanner weg. Steht auf.

Und dann: ein Geräusch von oben. Nicht laut — ein einzelner Schritt auf Holzboden. Jemand bewegt sich im zweiten Stock.

Kaspar hört es. Schaut zur Treppe.

Die Schritte gehen nicht zur Treppe. Sie gehen weg davon — Richtung Rückseite des Hauses.

`Kodex: Bewegung, zweites Stockwerk, Rückseite. Richtung: vom Treppenaufgang weg.`

---

`EP 1 · MS 2 · SC 3/12 · PHASE Intel → Konflikt · MODE CORE · COMMS OK · Px 0/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 ·

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Option 2. Delacroix bleibt im Hof und fängt ab, falls jemand rausklettert — aber ich will, dass sie Bescheid weiß bevor wir die Treppe nehmen. Kurze Lagemeldung per Funk, dann Kaspar hoch.

Kurze Frage zur Regelung: Wenn wir beide gleichzeitig agieren — Delacroix positioniert sich und wir steigen die Treppe hoch — ist das eine Simultanaktion mit getrennten Proben oder würfeln wir sequenziell?

**Kim** [Kim]: Okay MOTH warnt!! Sie soll unten bleiben und aufpassen falls jemand aus dem Fenster springt. Und dann Kaspar und Voss die Treppe hoch? Also Option 2?

**Mara Voss** [Sarah]: Okay, Delacroix warnen — Option 2. Voss flüstert ins Comlink: "MOTH, Bewegung oben, Rückseite, könnte jemand raus. Halte den Hof, Augen auf." Dann Blick zu Kaspar, kurzes Nicken Richtung Treppe — sie geht links, er rechts.

### Turn 33 — SL

## Szene 3 — Treppe / Hof, 10:03 Uhr

---

### Jonas — Simultanaktion

Getrennte Proben, gleichzeitig ausgeführt. Ich würfele beide in derselben Antwort — Ergebnisse beeinflussen sich gegenseitig wenn sie zeitlich kollidieren, sonst laufen sie parallel. Kein sequenzieller Malus.

---

### Burst-Comlink — MOTH

Knacken im Ohrrelais. Voss, flüsternd: *"MOTH, Bewegung oben, Rückseite, könnte jemand raus. Halte den Hof, Augen auf."*

Delacroix zieht sich zwei Schritte zurück in den Hof, Rücken zur Gartenmauer, Blick nach oben. Rückwand des Hauses: zwei Fenster, zweites Stockwerk. Eines davon — rechts — ist einen Spalt offen.

---

### Treppe — Kaspar und Voss, 10:03 Uhr

Kaspar geht zuerst. Schlagstock in der Hand, Schritte auf der Außenkante der Stufen wo das Holz weniger knarzt. Voss dahinter, einen Meter Abstand, Handscanner weggesteckt.

**Probe: Schleichen / Treppe — GES (Kaspar)**

`Probe: Treppe → W6: [2] + ⌊GES 4/2⌋ (2) + 0 = 4 vs SG 7 → MISS`

Eine Stufe knarzt. Laut. In einem stillen Haus ist das ein Signal.

Die Schritte oben hören auf.

Zwei Sekunden Stille.

Dann — schnell, sehr schnell — Bewegung. Nicht zur Treppe. Das Fenster.

---

### Hof — Delacroix, gleichzeitig

Das rechte Fenster im zweiten Stock schwingt auf. Eine Hand greift den Rahmen. Dann ein Bein, dann ein Körper — groß, breite Schultern, dunkler Mantel.

Der Große.

Er klettert raus, Füße tasten nach dem Fenstersims, Blick nach unten — und sieht Delacroix.

Einen Moment lang schaut er sie an. Sie schaut ihn an.

Er erkennt sie. Das sieht man an seinen Augen.

**Probe: Initiative — Delacroix**

`Initiative MOTH: 1W6: [3] + max(GES 5, TEMP 1) = 8`

**Probe: Initiative — der Große (NSC)**

`Initiative Großer: 1W6: [2] + 5 = 7`

Delacroix ist schneller.

`Kodex: MOTH — Initiative gewonnen. Fenster, zweites Stockwerk, ca. 4 Meter Fallhöhe.`

---

**Der Große hängt halb aus dem Fenster. Delacroix hat den ersten Zug.**

Er kann nicht schnell genug zurück. Er kann springen — aber 4 Meter auf Beton, d

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich kombiniere 3 und 4 — kurzer Burst an Kaspar, dann Positionierung:

*"Er ist am Fenster, rechts, kommt raus — macht schnell."*

Danach direkt unter das Fenster, breitbeinig, Arme leicht ausgestreckt. Nicht um ihn zu fangen — zu groß für den Scheiß — sondern um den Aufprallpunkt zu kontrollieren. Wenn er springt, landet er nicht sauber, und ich bin im Vorteil. Wenn er zögert, haben Kaspar und Voss ihn von oben.

Zieht MOTH dabei die Pistole oder reicht die Körperpräsenz als Drohung? Ich würde sie lieber in der Hüfte lassen solange er noch im Fenster hängt — weniger Eskalation, weniger Heat.

**Kim** [Kim]: MOTH zieht die Pistole hoch und ruft gleichzeitig leise ins Comlink: "Er kommt raus, Fenster rechts, ich hab ihn!"

Dann laut, direkt zu ihm: "Bleib wo du bist."

**Mara Voss** [Sarah]: Voss zischt ins Comlink: "Kaspar — schnell, er ist am Fenster." Dann, leiser: "MOTH, alle drei gleichzeitig — Pistole raus, halt ihn fest, wir sind in fünf."

### Turn 34 — SL

## Szene 3 — Hof / Fenster, 10:03 Uhr

---

### Koordination — Kim führt, Jonas unterstützt

Kim hat MOTH aktiv gespielt — Pistole raus, direkte Ansage. Jonas' Positionierung läuft parallel als Kaspars Ansage von der Treppe. Ich kombiniere beides: MOTH hat die Pistole, Kaspar kommt von oben. Zwei Fronten.

---

### Hof — MOTH

Delacroix zieht die Kompaktpistole. Schalldämpfer drauf — kein lauter Knall wenn sie schießt, aber das Wohnviertel ist still genug dass jemand etwas hören würde.

*"Bleib wo du bist."*

Leise, klar, kein Zittern.

Der Große hängt halb aus dem Fenster. Schaut auf die Pistole. Schaut auf Delacroix. Rechnet.

**Probe: Einschüchterung — CHA (Delacroix, Verdeckte Identität)**

`Probe: Einschüchterung → W6: [5] + ⌊CHA 6/2⌋ (3) + Talent +2 = 10 vs SG 8 → ERFOLG`

Er hält inne. Nicht aus Angst — aus Kalkulation. Die Pistole ist real, die Frau ist ruhig, und springen bedeutet vier Meter Beton mit einer bewaffneten Person am Boden. Das ist kein guter Sprung.

Er bleibt im Fenster. Hände am Rahmen, Körper halb draußen.

`Kodex: Großer — Bewegung gestoppt. Hält Position. Kalkulation läuft.`

---

### Treppe — Kaspar und Voss, gleichzeitig

Burst rein: *"Er ist am Fenster, rechts, macht schnell."*

Kaspar nimmt die letzten vier Stufen in zwei Schritten — Knarzen egal jetzt. Voss direkt dahinter.

Oben: ein kurzer Flur, zwei Türen. Die rechte steht offen — Schlafzimmer, Fenster offen, Rahmen leer. Der Große ist draußen.

Kaspar tritt ans Fenster. Schaut runter.

Der Große hängt am Rahmen, Delacroix darunter, Pistole oben. Er dreht den Kopf — sieht Kaspar. Dann Voss hinter Kaspar.

Drei Agenten. Er ist eingekesselt.

---

### Der Große — Entscheidung

Er lässt den Rahmen los. Nicht um zu springen — er lässt sich zurückziehen, Beine zuerst ins Zimmer, und steht dann im Schlafzimmer. Hände halb oben, nicht ganz — kein Kapitulationsgestus, eher: *ich greife nicht an.*

Er schaut Kaspar an. Dann Voss. Dann — kurz, durch das offene Fenster — auf Delacroix unten.


**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay krass, das hat funktioniert. Ich nehm Option 1, aber kurz vorher — Kaspar sichert den Raum erst ab, bevor wir reden. Er soll nicht in Reichweite von irgendwas Nützlichem stehen bleiben.

Kaspar macht einen Schritt zur Seite, Blickwinkel auf beide Türen, und sagt ruhig: *"Hände ganz oben. Dann reden wir."* Voss soll den Typen im Auge behalten während Kaspar kurz die zweite Tür checkt — offen oder zu?

Frage an Sarah: Gibt's nen Probe-Modifikator wenn ich gleichzeitig sichere und das Verhör führe, oder teilen wir das auf?

**Kim** [Kim]: okay MOTH kommt rauf, alle zusammen — aber Pistole bleibt erstmal drin. er hat "fragt" gesagt, dann reden wir. ich fang an: wer bist du und warum das bauteil?

**Mara Voss** [Sarah]: Voss lehnt am Türrahmen, Pistole locker in Richtung seiner Mitte, und mustert ihn drei Sekunden lang ohne etwas zu sagen.

*"Name."*

Pause.

*"Nicht der, den du benutzt. Der echte."*

### Turn 35 — SL

## Szene 4 — Schlafzimmer, 10:05 Uhr

---

### Jonas — Sichern und Verhör

Aufteilen ist richtig. Kaspar sichert, Voss führt das Verhör — keine Probe-Aufteilung nötig, zwei verschiedene Aktionen. Kaspar checkt die zweite Tür, Voss hat den Mann im Blick.

Die zweite Tür: **zu, kein Licht darunter.** Kaspar drückt sie kurz auf — Badezimmer, leer, Fenster geschlossen. Sauber.

Der Große hebt die Hände. Ganz oben diesmal. Kein Widerstand.

---

### Verhör — Voss führt, MOTH kommt rauf

Delacroix klettert durchs Fenster — unbequem, aber schnell. Pistole weg, Augen auf den Mann.

Der Große steht mitten im Zimmer. Hände oben, Haltung gerade. Er schaut Voss an als sie die Frage stellt.

Drei Sekunden Stille.

Dann:

*"Vadim."* Kein Nachname. *"Das reicht."*

Er schaut kurz zu Delacroix, dann zurück zu Voss.

*"Das Bauteil — ich weiß was ihr wisst. Ihr habt es gestern Abend genommen, ihr habt es eurer Organisation gebracht. Jetzt steht ihr hier und fragt mich was es ist."* Ein kurzes, nicht unfreundliches Achselzucken. *"Das bedeutet ihr wisst es selbst nicht."*

Er lässt die Hände langsam sinken — nicht auf Hüfthöhe, aber nicht mehr ganz oben. Testet die Grenze.

*"Das Bauteil dokumentiert. Mehr sage ich nicht ohne Gegenleistung."*

**Probe: Einschätzen / Lügt er — INT (Voss, Tatortanalyse)**

`Probe: Einschätzen → W6: [4] + ⌊INT 6/2⌋ (3) + Talent +2 = 9 vs SG 8 → ERFOLG`

Er lügt nicht. Er dosiert — sagt das Minimum das er sagen muss um einen Handel zu eröffnen. Das ist kein Verhör für ihn. Das ist eine Verhandlung.

`Kodex: Vadim — Name bestätigt, Nachname verweigert. Verhaltensanalyse: kooperativ-taktisch. Ziel: Informationshandel.`

---

**Vadim schaut die drei an.**

*"Ihr wollt wissen woher das Bauteil stammt. Ich will wissen wer euch schickt."* Kurze Pause. *"Tausch. Gleiche Münze."*

---

`EP 1 · MS 2 · SC 4/12 · PHASE Intel · MODE CORE · COMMS OK · Px 0/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1 · 👁️ Tarnung: kompromittiert`
`⏱️ Wohnviertel, Tage

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay krass, der ist vorbereitet. Der hat auf uns gewartet oder zumindest mit sowas gerechnet.

Ich würde Option 3 spielen — die Gegenfrage. Kaspar tritt einen halben Schritt zur Seite, nicht bedrohlich, aber so dass er Vadims Blickfeld leicht verschiebt. Dann sagt er ruhig:

*"Wer war heute Morgen hier?"*

Kein Tausch, kein Druck — einfach die Frage hinwerfen und schauen ob er zuckt. Wenn er dosiert, dosiert er vielleicht auch das. Und falls er antwortet ohne Gegenleistung zu fordern, wissen wir dass ihn die zweite Person nervös macht.

Gibt's da eine Probe drauf — Einschüchtern oder sowas? Oder läuft das rein narrativ?

**Kim** [Kim]: okay warte — "dokumentiert" heißt das Ding hat sowas wie einen Speicher? eine Blackbox?

und ich würd Option 3 machen, die Gegenfrage. mal schauen ob er sich verplappert

**Mara Voss** [Sarah]: Ich gehe mit Option 3, aber ich will sie ein bisschen einbetten.

---

Voss lässt die Pause stehen, bevor sie antwortet. Dann, ruhig:

*"Wer war heute Morgen hier?"*

### Turn 36 — SL

## Szene 4 — Verhör, 10:06 Uhr

---

### Kim — "dokumentiert"

Gute Einschätzung. Ein Speicher, eine Blackbox, ein stiller Zeuge — das Bauteil hat nicht aktiv gesendet, es hat aufgezeichnet. Was genau, für wen, wohin die Daten gehen: noch offen.

---

### Jonas — Probe für Gegenfrage

Ja, Probe. Ihr werft eine Frage hin die er nicht erwartet — das ist soziale Taktik, kein Druck. **CHA**, kein STR. Voss stellt die Frage, Kaspar verschiebt den Blickwinkel — passiver Unterstützungsbonus +1 auf Voss' Wurf.

**Probe: Verhörtaktik / Überraschungsfrage — CHA (Voss) + Kaspar Unterstützung**

`Probe: Gegenfrage → W6: [6] + ⌊CHA 3/2⌋ (1) + Kaspar +1 = 8 vs SG 8 → ERFOLG (Exploding: [3]) → 11 — STARKER ERFOLG`

---

Voss lässt die Pause stehen. Dann, ruhig:

*"Wer war heute Morgen hier?"*

Vadim zuckt nicht. Aber seine Augen gehen kurz — sehr kurz — nach links. Nicht zur Tür. Zur Wand. Als würde er an jemanden denken der nicht im Raum ist.

Dann kontrolliert er es wieder.

*"Niemand."*

Zu schnell. Zu glatt.

**Probe: Lüge erkennen — INT (Voss, Tatortanalyse)**

`Probe: Lüge → W6: [4] + ⌊INT 6/2⌋ (3) + Talent +2 = 9 vs SG 7 → ERFOLG`

Er lügt. Und er weiß dass er es zu schnell gesagt hat — das sieht man an dem kleinen Moment danach, wo er nichts tut und nichts sagt und wartet ob jemand nachhakt.

Die zweite Person macht ihm Sorgen. Nicht wegen uns — wegen ihr.

`Kodex: Vadim — Aussage "Niemand" als Lüge eingestuft. Reaktionsmuster: Schutzreflex, nicht Verheimlichung gegenüber Feinden. Zweite Person: möglicherweise Verbündeter in Gefahr oder unbekanntem Status.`

---

Delacroix steht links von ihm. Kaspar rechts. Voss in der Mitte, Türrahmen im Rücken.

Vadim schaut Voss an. Etwas hat sich verschoben — nicht viel, aber spürbar. Er ist immer noch taktisch, immer noch kontrolliert. Aber die Frage hat etwas geöffnet das er nicht geplant hatte.

*"Die zwei Tassen,"* sagt er schließlich, langsam. *"Ihr habt die Küche gesehen."*

Keine Frage. Feststellung.

*"Sie ist nicht Teil davon

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich tippe:

---

Option 3 für mich — Kaspar lehnt sich ganz leicht vor, sagt nichts laut, aber macht eine kleine Geste Richtung Voss: *mach das*. Der Hebel liegt auf dem Tisch, wir müssen ihn nur anfassen.

Und kurz OOC: Zählt das als Einschüchterung oder eher Verhandlung? Weil wenn STR irgendwo reinspielt würde ich das gerne wissen bevor Voss redet. 😅

**Kim** [Kim]: ich tipp schnell: option 3 klingt fies aber gut?? aber warte — was ist SG nochmal?

**Mara Voss** [Sarah]: Option 3 — aber ich will es nicht als Drohung klingen lassen, eher als Versprechen das er glauben kann.

Voss hält den Blick, nickt einmal, kurz. "Sie bleibt außen. Das ist kein Angebot, das ist unser Wort." Kurze Pause. "Aber dafür brauchen wir einen Namen."

### Turn 37 — SL

## Szene 4 — Verhör, letzter Beat, 10:07 Uhr

---

### OOC-Antworten kurz

**Jonas — Einschüchterung oder Verhandlung?**
Das ist **CHA**, Verhandlung/Versprechen. Keine STR — Kaspar's physische Präsenz ist Hintergrundrauschen, kein aktiver Druck. Voss redet, das ist ihr Wurf.

**Kim — SG?**
Schwierigkeitsgrad. Eine Zahl die ich festlege je nachdem wie schwer eine Aktion ist. SG 6 = leicht, SG 8 = mittel, SG 10 = hart, SG 12+ = sehr hart. Dein Würfelergebnis muss gleich hoch oder höher sein um zu bestehen.

---

### Verhör — Voss' Versprechen

*"Sie bleibt außen. Das ist kein Angebot, das ist unser Wort."*

Pause.

*"Aber dafür brauchen wir einen Namen."*

**Probe: Verhandlung / Versprechen — CHA (Voss)**

`Probe: Versprechen → W6: [5] + ⌊CHA 3/2⌋ (1) + 0 = 6 vs SG 7 → MISS, knapp`

Vadim schaut Voss an. Lange. Er hört das Versprechen — er glaubt es halb. Aber halb ist nicht genug für einen Mann der dosiert.

*"Ihr Wort."* Er wiederholt es, nicht spöttisch, eher abwägend. *"Ich kenne euer Wort nicht."*

Er schaut kurz zu Kaspar. Dann zu Delacroix.

*"Gestern Abend habt ihr das Päckchen genommen. Heute seid ihr hier. Das ist schnell."* Eine kurze Pause. *"Entweder ihr seid sehr gut — oder ihr hattet Hilfe."*

Er lässt das stehen. Dann:

*"Ein Name. Eure Organisation. Dann reden wir über das Bauteil."*

Der Tausch steht wieder auf dem Tisch. Er ist weicher als vorhin — die zweite Person hat etwas aufgemacht — aber er gibt den Hebel nicht kampflos ab.

---

`EP 1 · MS 2 · SC 4/12 · PHASE Intel · MODE CORE · COMMS OK · Px 0/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1`
`⏱️ Heat läuft still · Vadim: Tausch, kein Rückzug`

---

**Der Moment:**

Vadim will einen Namen. ITI ist keine öffentliche Organisation — aber ein Name kostet nichts wenn man ihn kontrolliert. Oder ihr erfindet einen.

**Drei Optionen:**

1. **ITI nennen** — echter Name, echter Tausch. Er weiß dann wer ihr seid — aber ihr habt das Bauteil schon, und Mira hat gesagt Identität sichern reic

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Kaspar lehnt sich leicht vor — nicht bedrohlich, eher als würde er gleich was sagen. Dann hält er sich zurück und lässt Voss übernehmen.

Warte kurz — OOC: Wenn wir ITI nennen, was ist das Risiko konkret? Mira hat "Identität sichern" gesagt — heißt das ITI ist geheim-geheim, oder nur "nicht unnötig streuen"? Ich frag weil das die Entscheidung ändert.

Und wenn MOTH einen Fake-Namen liefert — hat sie da irgendwas vorbereitet, oder ist das ein spontaner Roll? Weil spontan gegen jemanden der offensichtlich kalkuliert klingt riskant.

**Kim** [Kim]: ok warte ich check das kurz

also wir nennen einfach ITI? wir haben das bauteil doch schon, oder? was verlieren wir da

**Mara Voss** [Sarah]: Voss hält den Blick, nickt einmal knapp. "ZEITRISS. Privatsektor, Auftragsbasis — ihr Name kursiert nicht in Regierungsdatenbanken." Sie lässt eine kurze Pause. "Das sollte genug sein für jemanden der auch nicht offiziell existiert."

### Turn 38 — SL

## Szene 4 — Tausch, 10:08 Uhr

---

### OOC-Antworten kurz

**Jonas — ITI-Risiko:**
ITI ist nicht öffentlich, aber auch nicht absolut geheim — eher "operativ diskret". Vadim weiß jetzt dass eine Organisation existiert die Zeitlinien überwacht. Das ist ein Informationsgewinn für seine Seite. Kurzfristig kein Problem — langfristig ein Faden der sich auszahlen könnte.

**MOTH Fake-Name:** Spontan gegen einen Kalkulierer wäre CHA-Probe SG 9, Vadim würde gegenprüfen. Riskant. Voss hat die Entscheidung abgenommen — kein Wurf nötig jetzt.

---

### Voss — der Name

*"ZEITRISS. Privatsektor, Auftragsbasis — ihr Name kursiert nicht in Regierungsdatenbanken."*

Pause.

*"Das sollte genug sein für jemanden der auch nicht offiziell existiert."*

Vadim hört zu. Schaut Voss an. Schaut kurz auf Kaspar — als würde er den Namen abgleichen mit dem was er gestern Abend auf der Connecticut Avenue gesehen hat.

Dann nickt er. Einmal, kurz.

*"ZEITRISS."* Er wiederholt es leise, als würde er es sich einprägen. *"Gut."*

Er lässt die Hände vollständig sinken. Keine Waffe, kein Angriff — er hat entschieden.

*"Das Bauteil stammt nicht aus dieser Zeit."* Er sagt es ohne Umschweife. *"Nicht aus dieser Dekade, nicht aus diesem Jahrhundert. Jemand hat es zurückgebracht — von wo, das weiß ich nicht. Ich bin nur der Mann der es platziert."*

Kurze Pause.

*"Meine Organisation hat es bekommen. Fertig verpackt, mit Anweisungen. Finch war bereits vorbereitet — nicht von uns. Von jemandem der vor uns war."*

Er schaut Voss direkt an.

*"Ihr habt das Bauteil. Aber ihr habt nicht das Original. Was ich platziert habe war eine Kopie."*

Stille im Zimmer.

`Kodex: Neue Information. Bauteil = Kopie. Original existiert. Vorbereitungsebene vor Vadims Organisation — dritte Partei.`

---

`EP 1 · MS 2 · SC 5/12 · PHASE Intel · MODE CORE · COMMS OK · Px 0/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1`
`⏱️ Heat läuft · Vadim: kooperativ, Information geflossen`

---

**Intel / Risiken**
- **Kopi

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Option 2 für mich — die dritte Partei ist der eigentliche Knackpunkt hier. Wer auch immer Finch *vor* Vadims Leuten vorbereitet hat, der ist eigentlich unser Hauptproblem.

Kaspar tritt einen halben Schritt vor, Arme noch locker — aber Körperhaltung klar dominierend.

*"Die Partei die euch das Bauteil gegeben hat. Name, Beschreibung, wie der Kontakt lief. Alles was du hast."*

Kurze Pause, dann ruhiger:

*"Du hast kooperiert bis hierher. Jetzt den letzten Schritt."*

**Kim** [Kim]: okay warte kurz — "kopie nicht original" bedeutet das unser ganzer auftrag war umsonst?? oder ist das jetzt noch wichtiger??

egal, ich tippe: **Option 2, wer hat euch das Bauteil gegeben** — die dritte partei klingt nach dem eigentlichen problem oder?

**Mara Voss** [Sarah]: Voss lässt das kurz sacken, dann: "Wer hat eurer Organisation das Bauteil übergeben — Name, Beschreibung, Kontaktweg. Alles was ihr habt."

Sie hält Vadims Blick, gibt ihm keine Zeit zum Abwägen.

### Turn 39 — SL

## Szene 5 — Verhör, dritte Partei, 10:09 Uhr

---

### Kim — war der Auftrag umsonst?

Nein. Ihr habt verhindert dass die Kopie installiert wird — die Zeitlinie ist stabil. Aber jetzt wisst ihr dass das Spiel größer ist. Das ist nicht Misserfolg, das ist die nächste Schicht.

---

### Verhör — dritte Partei

Kaspar tritt vor. Voss hält den Blick. Delacroix steht still.

Vadim schaut die drei an. Dann atmet er aus — kurz, kontrolliert.

*"Kein Name. Nie einen gehabt."*

Er sagt es ohne Entschuldigung.

*"Kontakt lief über Tote Briefkästen. Schriftlich, verschlüsselt, Chiffre die wir nicht selbst entwickelt haben — sie haben sie uns gegeben. Das Bauteil kam in einem Koffer, Bahnhof Union Station, Schließfach 114. Schlüssel lag drei Tage vorher in unserem Briefkasten hier."*

Er macht eine kurze Geste Richtung Fenster — Volta Street, der grüne Briefkasten.

*"Keine persönliche Übergabe. Nie. In zwei Jahren Zusammenarbeit habe ich niemanden von denen gesehen."*

Kurze Pause. Dann, leiser:

*"Aber einmal — einmal haben sie einen Fehler gemacht. Ein Brief kam mit einem Wasserzeichen. Kein Logo, kein Text. Ein Wasserzeichen."*

Er schaut Voss an.

*"Auge über Anker."*

`Kodex: Dritte Partei — kein Name, kein Gesicht. Tote Briefkästen, zwei Jahre Zusammenarbeit. Wasserzeichen: Auge über Anker. Identisch mit Streichholzheftchen-Logo.`

---

Stille.

Das Logo auf dem Streichholzheftchen in Vadims Mantel — das ist nicht Vadims Organisation. Das ist die dritte Partei. Vadim trägt ihr Symbol ohne es zu wissen, oder er weiß es und hat nie darüber nachgedacht.

**Probe: Verbindung ziehen — INT (Voss, Tatortanalyse)**

`Probe: Verbindung → W6: [6] + ⌊INT 6/2⌋ (3) + Talent +2 = 11 vs SG 8 → STARKER ERFOLG (Exploding: [1]) → 12`

Voss sieht es sofort. Das Streichholzheftchen. Der Mantel unten in der Garderobe. Vadim trägt das Symbol der Organisation die ihn benutzt — und er weiß es entweder nicht, oder er weiß es und hat sich damit abgefunden.

Und noch etwas: zwei Jahre Zusammenarb

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Option 2, aber ich will das Heftchen gleichzeitig hochbringen — Kaspar soll kurz runter, es holen, und dann leg ich es vor Vadim auf den Tisch während ich ihn konfrontiere. Visueller Druck.

Kaspar schaut Vadim ruhig an: *"Das Symbol das du gerade beschrieben hast — Auge über Anker — trägst du selbst. In deinem Mantel unten. Streichholzheftchen, Innentasche."*

Kurze Pause, damit es landet.

*"Entweder weißt du es und hast es mir verschwiegen. Oder du weißt es nicht — und dann solltest du dir ernsthaft überlegen wie nah die an dir dran sind."*

Gibt's da eine Probe für Einschüchterung oder Reaktion lesen? STR oder SOC-basiert bei ZEITRISS?

**Kim** [Kim]: okay warte — das streichholzheftchen IST von denen?? das hat er die ganze zeit in der tasche getragen omg

option 2, konfrontieren! ich will seine reaktion sehen wenn er das merkt

**Mara Voss** [Sarah]: Ich nehme Option 2, aber kombiniert — erst das Heftchen holen, dann konfrontieren.

Voss sagt ruhig: „Einen Moment." Sie dreht sich um, geht die Treppe runter, kommt mit dem Streichholzheftchen zurück. Legt es auf den Tisch vor Vadim. „Auge über Anker. Du trägst ihr Logo schon die ganze Zeit."

### Turn 40 — SL

## Szene 5 — Konfrontation, 10:10 Uhr

---

### Jonas — Probe

**Reaktion lesen = INT** (Tatortanalyse). **Einschüchterung = CHA** oder **STR** wenn physisch. Hier: ihr legt Beweis vor und beobachtet — das ist INT. Voss macht die Aktion, Kaspar hält die Atmosphäre.

---

### Streichholzheftchen

Voss geht die Treppe runter. Dreißig Sekunden. Kaspar und Vadim stehen sich gegenüber — kein Wort, kein Blick weg. Delacroix an der Wand, Arme locker.

Voss kommt zurück. Heftchen in der Hand. Legt es auf den Tisch vor Vadim.

*"Auge über Anker. Du trägst ihr Logo schon die ganze Zeit."*

Kaspar, ruhig: *"Entweder weißt du es — oder du weißt es nicht. Dann solltest du dir überlegen wie nah die an dir dran sind."*

**Probe: Reaktion lesen — INT (Voss, Tatortanalyse)**

`Probe: Reaktion lesen → W6: [3] + ⌊INT 6/2⌋ (3) + Talent +2 = 8 vs SG 7 → ERFOLG`

Vadim schaut auf das Heftchen.

Keine Überraschung. Keine Verleugnung. Aber — und das ist das Entscheidende — seine Augen gehen nicht zum Heftchen und dann zu Voss. Sie gehen zum Heftchen und **bleiben dort**.

Drei Sekunden. Vier.

Dann, leise:

*"Ich weiß es."*

Er nimmt das Heftchen nicht. Lässt es liegen.

*"Ich habe es immer gewusst."* Eine Pause. *"Sie wollten dass ich es weiß. Das ist der Punkt — sie verstecken sich nicht vor mir. Sie zeigen mir, dass sie überall sind. In meiner Tasche, in meiner Post, in meinem Briefkasten."*

Er schaut Voss an. Zum ersten Mal ohne Kalkulation.

*"Ich bin nicht ihr Partner. Ich bin ihr Beweis dass sie funktionieren."*

`Kodex: Vadim — vollständiges Lagebild bestätigt. Er weiß dass er Instrument ist. Kooperation aus Pragmatismus, nicht Loyalität.`

---

Stille.

Dann, fast beiläufig:

*"Die Frau heute Morgen — sie weiß nichts davon. Sie ist nicht Teil davon."* Er schaut zum Fenster. *"Haltet euer Wort."*

---

`EP 1 · MS 2 · SC 5/12 · PHASE Intel · MODE CORE · COMMS OK · Px 0/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1`
`⏱️ Heat läuft · Verhör: erschöpft · Exfil-Fenster:

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Heftchen einpacken, klar. Und Vadim laufen lassen — er ist kein Ziel mehr, eher ein Opfer von denen. Ich würde nur kurz vor der Exfil noch fragen: Hat Vadim irgendeinen Kontakt zu "Auge über Anker" — eine Nummer, ein Treffpunkt, irgendwas? Auch wenn er nur Instrument ist, muss es irgendwo eine Schnittstelle geben. Dann Gate aufmachen und raus.

**Kim** [Kim]: Heftchen einpacken, Vadim laufen lassen. Wir haben unser Wort gegeben. Raus hier.

**Mara Voss** [Sarah]: Voss nimmt das Heftchen vom Tisch, steckt es ein. Dann, ohne Vadim anzusehen: *"Ihr Standort bleibt heute Nacht aus unserem Bericht — das ist alles was wir versprechen können."* Sie nickt Kaspar kurz zu. *"Wir gehen."*

### Turn 41 — SL

## Szene 5 — Letzter Beat, 10:11 Uhr

---

### Kaspars letzte Frage

Vadim hört die Frage. Schaut kurz zur Decke — nicht nachdenkend, eher als würde er abwägen was er noch geben kann.

*"Tote Briefkästen. Nur das."* Er schaut Kaspar an. *"Union Station, Schließfach 114 — das haben sie nicht gewechselt. Noch nicht."*

Eine Pause.

*"Wenn ihr dort etwas findet, wisst ihr mehr als ich."*

`Kodex: Schnittstelle gesichert. Union Station, Schließfach 114. Aktiv oder inaktiv: unbekannt.`

---

### Exfil

Voss nimmt das Heftchen. Steckt es ein, sagt was sie sagen muss, nickt Kaspar zu.

Vadim steht im Zimmer. Schaut auf den leeren Tisch. Das Heftchen ist weg, die Karte ist unberührt — er weiß dass ihr sie gescannt habt, aber er sagt nichts.

Als die drei die Treppe runter gehen, sagt er noch einmal, ohne die Stimme zu heben:

*"Euer Wort."*

Keine Drohung. Eine Erinnerung.

---

Hinterausgang, Betonhof, Gartenmauer. Kaspar zuerst, dann Voss, dann Delacroix. Die Gasse ist leer — die Nachbarin ist drin, die Straße ist still.

Gate-Window auf Abruf.

`Kodex: Exfil-Route frei. Gate-Window bereit. Transferkoordinaten: ITI Hangar-Axis.`

Drei Sekunden Oktoberluft, Georgetown, 1962. Der Geruch von nassem Laub und Kohle.

Dann Pflastersteine die zu Metall werden.

---

`EP 1 · MS 2 · SC --/-- · PHASE Debrief · MODE CORE · COMMS OK · Px 0/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1`

---

## DEBRIEF — Mission 2, Episode 1

**Archivarin Mira, ITI Operations, Auswertungsraum**

Mira hört zu. Sie unterbricht nicht — lässt Voss den Bericht führen, nickt bei Schlüsselpunkten, tippt einmal kurz als das Streichholzheftchen auf den Tisch kommt.

Als Voss fertig ist, ist Mira einen Moment still.

*"Kopie, nicht Original."* Sie sagt es langsam. *"Das bedeutet das Original ist noch irgendwo — in einer anderen Epoche, einem anderen Ort, oder bereits installiert."*

Sie schaut auf das Heftchen.

*"Auge über Anker. Zwei Jahre aktiv, kein Gesicht, kein Name."* Kurze Pause. *"Das 

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay krass, Voss levelt schon auf 3? Ich bin neidisch lol. Aber fair, sie hat die meiste Arbeit gemacht beim Verhör.

Kaspar lehnt sich im Debrief-Raum zurück und schaut auf den Score-Screen. 310 CU — nicht schlecht für einen Hausdurchbruch und ein Verhör ohne Zwischenfall. Das Versprechen an Vadim hat mich kurz beschäftigt, aber ich stehe dazu. Wenn der ITI-Archivar das Schließfach aufmacht, hoffe ich dass die das auf dem Schirm haben.

Eine Frage noch an Sarah / Mira: Was passiert mit dem Paradoxon-Index wenn er auf 5 steigt? Ich kenn das Konzept noch nicht wirklich — in SR gibt's sowas nicht direkt, aber es klingt nach "nicht gut".

**Kim** [Kim]: oh warte Voss macht LEVEL UP?? was ist TEMP nochmal, ich vergess das immer 😭

**Mara Voss** [Sarah]: Voss Lvl 3 — ich nehme Talent-Upgrade: Tatortanalyse Fortgeschritten. Passt besser zu dem was kommt, wenn das Original noch irgendwo liegt.

Dann: !save

### Turn 42 — SL

## Klärungen + Level-Up + Save

---

### Jonas — Paradoxon-Index

Gute Nachricht: **Px 5 ist das Ziel, nicht das Problem.**

> Px steigt = gut. Bei Px 5 löst das ITI ein **ClusterCreate** aus — das System erkennt 1-2 instabile Zeitkoordinaten auf der Raumzeitkarte und markiert sie als **Rift-Ops**. Dort warten Paramonstern, Artefakte, besondere Beute.

Das ist ein Belohnungssystem. Die Crew *will* Px 5 erreichen. Kein SR-Astralüberlauf, keine Strafe — ein Jackpot-Moment.

`Kodex: Px 1/5. Nächster Anstieg: abhängig von TEMP-Durchschnitt und Missionsverlauf.`

---

### Kim — TEMP

**TEMP = Temporale Affinität.** Je höher, desto besser reagiert ein Agent auf Zeitphänomene, Psi-Kräfte und Zeitverwerfungen. Außerdem:
- Beeinflusst wie schnell Px steigt
- Bestimmt wie oft dein Epochenfahrzeug verfügbar ist
- Wird für Initiative mitgenutzt (max GES/TEMP)

Delacroix hat TEMP 1 — das bedeutet langsamer Px-Aufbau, seltenes Fahrzeug. Aber CHA 6 und GES 5 machen das mehr als wett.

---

### Voss — Tatortanalyse Fortgeschritten

`Kodex: Tatortanalyse Basis → Fortgeschritten. +3 auf INT-Proben Spurenanalyse. Reroll 1×/Mission verfügbar.`

**Level-Up abgeschlossen.**

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP1-MS2-HQ-POST",
  "parent_save_id": "SAVE-2026-EP1-MS1-HQ-POST",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 2,
    "px": 1,
    "px_state": "stable",
    "mode": "core",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-VOSS-01",
      "name": "Mara Voss",
      "callsign": "SPLINTER",
      "rank": "Feldagentin",
      "lvl": 3,
      "xp": 0,
      "origin": { "epoch": "unbekannt", "hominin": "Homo sapiens sapiens", "role": "Analystin" },
      "attr": { "STR": 3, "GES": 6, "INT": 6, "CHA": 3, "TEMP": 4, "SYS": 2 },
      "hp": 13,
      "hp_max": 13,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Tatortanal

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, das klingt deutlich besser als ich dachte! Also Px ist quasi unser Fortschrittsbalken zum nächsten besonderen Einsatz — hab ich das richtig? Und was passiert, wenn wir bei einer Rift-Op scheitern, geht der Px dann zurück auf null oder bleibt der Stand erhalten?

**Kim** [Kim]: oh okay das hab ich komplett falsch verstanden lol. also wir WOLLEN den px hochkriegen?

**Mara Voss** [Sarah]: Okay, ich lese das nochmal durch... Also Px 5 ist quasi unser Meilenstein, cool. Und Voss hat jetzt +3 auf INT bei Spurenanalyse — war der Reroll schon vorher dabei oder ist der neu dazugekommen?

### Turn 43 — SL

## HQ — Px-Erklärung & Voss-Talent

---

### Jonas — Px als Fortschrittsbalken

Genau richtig. Px ist euer Fortschrittsbalken zum Rift-Op-Jackpot.

**Bei Rift-Op-Scheitern:** Px bleibt wo er ist. Kein Rückschritt. Ihr habt den Zugang verdient — das Rift-Op selbst ist optional und riskant, aber der Px-Stand ist unverlierbar. Was ihr aus dem Rift-Op mitnehmt (Artefakte, Beute) behaltet ihr nur wenn ihr lebend rauskommt.

---

### Kim — ja, ihr wollt Px hochkriegen

Absolut. Jede Mission baut Px auf, abhängig von euren TEMP-Werten. Voss und Kaspar haben TEMP 4 — die treiben den Index gut voran. Delacroix mit TEMP 1 trägt weniger bei, aber das Team zählt zusammen.

`Kodex: Px-Prognose bei aktuellem TEMP-Durchschnitt ~3: +1 Px pro Mission. Px 5 in ca. 4 weiteren Missionen erreichbar.`

---

### Sarah — Tatortanalyse Fortgeschritten

Der **Reroll** ist neu — das ist der Upgrade-Bonus. Vorher (Basis) hatte Voss nur +2 und keine Reroll-Option. Jetzt:

```
Tatortanalyse (Fortgeschritten)
  +3 auf INT-Proben Spurenanalyse & Beweissicherung
  Reroll 1×/Mission bei fehlgeschlagener Analyse-Probe
  Triviale Tatortlesungen ohne Probe (bleibt)
```

Der Reroll bedeutet: wenn eine INT-Spurenanalyse-Probe misslingt, kann Voss einmal pro Mission neu würfeln und das bessere Ergebnis nehmen. Das ist stark — gerade wenn es auf Details ankommt wie heute mit Vadim.

---

**Alles klar für Mission 3?**

Oder wollt ihr noch kurz die Zero Time Lounge oder die Quartiermeisterei mitnehmen bevor das nächste Briefing läuft?

`Kodex: HQ stabil. Mira wartet nicht aktiv — kein Zeitdruck für Mission 3.`

---

**HQ-Menü:**

1. **Lounge / Erkunden** — kurze HQ-Szene, Charaktermoment, Einkauf
2. **Direkt Briefing Mission 3** — Mira, Briefingraum 4-C
3. **Freie Aktion** — eigener Wunsch
4. **Neuer Chat** — Save mitnehmen, frisch starten

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay cool, der Reroll ist tatsächlich stark — gerade bei so einem Vadim-Fall wo ein falscher Hinweis alles versauen kann. Gut zu wissen.

Ich würd kurz die Quartiermeisterei mitnehmen bevor wir ins Briefing gehen. Voss hat nach dem letzten Einsatz ein paar Nahkampfoptionen vermisst — schau mal ob da was Brauchbares liegt. Dann direkt zu Mira.

**Kim** [Kim]: Lounge kurz! Ich will Voss fragen was ein Reroll ist lol

**Mara Voss** [Sarah]: Okay, der Reroll ist tatsächlich stärker als ich dachte — gut zu wissen für Situationen wie Vadim. Voss nickt kurz. "Briefing. Kein Umweg." Direkt zu Mira, Option 2.

### Turn 44 — SL

## HQ — Kurze Runde vor Briefing

---

### Drei Wege, ein Ziel

Sarah will direkt zu Mira. Jonas zur Quartiermeisterei. Kim zur Lounge. Fünfzehn Minuten — dann alle in 4-C.

---

### Zero Time Lounge — MOTH & SPLINTER

Die Lounge ist klein, warm, riecht nach Kaffee und synthetischem Holz. Zwei andere Agenten sitzen in der Ecke — unbekannte Gesichter, anderes Team, sie schauen kurz auf und wieder weg. Routine.

Delacroix holt sich einen Kaffee. Setzt sich zu Voss die bereits mit dem Datenstick-Upload beschäftigt ist — Notizbuch-Scan, vierzehn Seiten kyrillisch, lädt ins Archiv.

*"Reroll,"* sagt Delacroix. *"Was ist das genau?"*

Voss schaut kurz auf. *"Wenn eine Probe schiefgeht — ich darf nochmal würfeln. Einmal pro Einsatz."*

*"Klingt gut."*

*"Ist gut."* Voss dreht den Handscanner um. Upload läuft. *"Besonders wenn jemand lügt und ich es nicht sofort merke."*

`Kodex: Notizbuch-Upload abgeschlossen. Übersetzung kyrillisch — Archiv-Anfrage läuft. Ergebnis: 48-72 Stunden.`

---

### Quartiermeisterei — RAMPART

Osei ist nicht da — Schichtwechsel. Ein junger Quartiermeister namens **PREIS, L.** schaut von seinem Terminal auf. Jünger als Osei, etwas nervöser, aber kennt seinen Bestand.

*"Nahkampf? Tier 1, Lizenz I?"*

Er zieht eine kurze Liste raus:

| Item | Tier | Preis | Effekt |
|---|---|---|---|
| Taktisches Messer | 1 | 70 CU | 2-3 LP, zieht nicht auf Waffenscanner |
| Nahkampf-Injektor | 1 | 90 CU | +2 STR für 1 Szene, Einmalnutzung |
| Schildknauf-Handschuh (Paar) | 1 | 85 CU | +1 LP Nahkampf zusätzlich zum Kampfhandschuh, stapelt |
| Betäubungspatrone ×3 | 1 | 60 CU | Für Dienstpistole, 0 LP Schaden + Betäubung SG 8 |

**Jonas — kaufst du etwas?** Kaspar hat 310 CU.

---

### Briefingraum 4-C — SPLINTER

Voss kommt fünf Minuten früher als die anderen. Mira ist bereits da — Projektionstisch läuft, aber das Bild ist noch schwarz.

Sie schaut Voss kurz an.

*"Der Notizbuch-Upload — ich hab die Anfrage gesehen. Übersetzung läuft."*

Kurze Pause.

*"Gut gemacht

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Kaspar kauft den Schildknauf-Handschuh (85 CU) und das Taktische Messer (70 CU). Macht 155 CU, bleiben 155 CU übrig.

Kurze Frage an Sarah: Stapelt der Handschuh auch mit bloßem Nahkampf oder nur mit dem Kampfhandschuh speziell? Weil Kaspar kämpft manchmal ohne Ausrüstung.

Dann ab in 4-C.

**Kim** [Kim]: okay ich bin kurz in der Lounge, hol mir auch einen Kaffee und schau Voss beim Upload zu

"48-72 Stunden?? das ist so lang 😭"

**Mara Voss** [Sarah]: Voss nickt einmal, kurz. Setzt sich, Rücken zur Wand, Blick zur Tür.

„Danke."

Pause. Dann, ohne aufzuschauen vom Tisch: „48 Stunden sind lang. Ich hoffe, wir brauchen die Übersetzung nicht vorher."

### Turn 45 — SL

## HQ — Letzte Klärung + Briefing

---

### Jonas — Handschuh-Stapeln

**Schildknauf-Handschuh stapelt nur mit dem Kampfhandschuh**, nicht mit bloßem Nahkampf. Logik: der Schildknauf sitzt am Handgelenk des Kampfhandschuhs und verstärkt den Aufprall. Ohne den Kampfhandschuh als Basis ist er nur Schutzpolster.

Kaspar mit beiden Handschuhen: **+2 LP im Nahkampf** (Kampfhandschuh +1, Schildknauf +1). Ohne Handschuhe: normaler Nahkampf-Schaden.

`Kodex: Kaspar — Wallet 310 → 155 CU. Schildknauf-Handschuh + Taktisches Messer ausgerüstet.`

---

### Lounge — MOTH & SPLINTER

Delacroix schaut auf den Upload-Timer. *"48-72 Stunden."*

Voss, ohne aufzuschauen: *"48 Stunden sind lang. Ich hoffe, wir brauchen die Übersetzung nicht vorher."*

Delacroix nippt am Kaffee. Schaut auf die Tür. *"Und wenn doch?"*

Voss legt den Handscanner hin. *"Dann improvvisieren wir."*

Upload läuft still weiter. Die zwei anderen Agenten in der Ecke reden leise — etwas über einen Einsatz in der Bronzezeit, klingt unangenehm. Niemand hört hin.

---

## Briefingraum 4-C — Mission 3

Alle drei. Kaspar zuletzt, neues Messer an der Hüfte, Handschuhe verstaut.

Mira tippt einmal. Der Projektionstisch wirft ein Bild an die Wand.

Keine Schwarzweißfotografie diesmal. Eine Karte — Europa, 1943, Besatzungslinien in Rot eingezeichnet. Ein einzelner Punkt markiert, irgendwo in Frankreich, Südwesten, ländliche Region.

*"Wir springen zurück."*

Kurze Pause, damit es landet.

*"Nicht wegen des Bauteils — noch nicht. Wegen dem was im Notizbuch stand."*

Sie schaut die drei an.

*"Der Archiv-Schnellübersetzer hat die ersten zwei Seiten fertig. Vierzehn Seiten kyrillisch, und auf Seite zwei steht eine Koordinate. Nicht geografisch — zeitlich. Eine Epoche, ein Datum, ein Ort."*

Neues Bild. Handgeschriebener Text, kyrillisch, mit einer einzigen Zeile darunter in Übersetzung:

**„Koordinate gesetzt: Südfrankreich, August 1943. Objekt transferiert. Bestätigung ausstehend."**

Mira legt die Hände auf den Tisch.

*"J

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Stapeln macht Sinn — Basis braucht Basis, klar.

Zur Frage: Kaspar spricht kein Französisch, würde ich sagen. Ich hab in keinem meiner Werte irgendwas Sprachliches, und Südfrankreich 1943 mit gebrochenem Akzent ist eher Verhörrisiko als Tarnung. Wer übernimmt das?

Und direkt dran: welche Deckidentitäten hat Mira vorbereitet? Das ist für mich wichtiger als das Dorf-Profil — wenn die Legende nicht stimmt, nutzt uns das beste Intel nichts.

**Kim** [Kim]: ich heb die hand — ich kann französisch! nicht perfekt aber okay, hab mal ne freundin gehabt lol

**Mara Voss** [Sarah]: Voss lehnt sich vor. "Ich spreche Französisch — nicht perfekt, aber überzeugend genug für 1943." Sie tippt kurz auf die Karte. "Welche Deckidentitäten hat Mira für uns?"

### Turn 46 — SL

## Briefing Mission 3 — Deckidentitäten & Sprache

---

### Sprache — geklärt

Voss und Delacroix sprechen Französisch. Kaspar nicht.

Mira nickt, ohne Überraschung.

*"Kaspar — ihr seid Belgier. Aus Lüttich, deutschsprachige Seite. Das erklärt den Akzent und warum ihr Französisch habt"* — ein kurzer Blick zu Voss und Delacroix — *"und er nicht."*

*"Belgier in Südfrankreich 1943 sind keine Seltenheit. Viele sind nach dem Einmarsch 1940 geflohen, haben sich irgendwo festgesetzt. Ihr seid auf dem Weg zu Verwandten in Toulouse — die gibt es nicht, aber niemand prüft das nach."*

---

### Deckidentitäten

Mira legt drei Mappen auf den Tisch. Papiere, Stempel, Fotografien — alles handgemacht, ITI-Fälschungsabteilung, epochenkonform.

| Agent | Legende | Details |
|---|---|---|
| SPLINTER | Hélène Marchand, 29 | Witwe, Lüttich, Schulbildung, spricht Deutsch + Französisch |
| RAMPART | Kurt Baumann, 34 | Hélènes Schwager, Handwerker, deutschsprachig, ruhig |
| MOTH | Claire Fontaine, 26 | Hélènes Nichte, Studentin, Toulouse als Ziel |

*"Keine Résistance-Kontakte, keine politischen Aussagen. Ihr seid müde, ihr seid auf der Durchreise, ihr wollt keine Aufmerksamkeit."*

Sie schaut Kaspar an.

*"Wenn ein Deutscher euch anspricht: Baumann redet. Deutsch ist sein Vorteil dort."*

`Kodex: Deckidentitäten geladen. Hélène Marchand / Kurt Baumann / Claire Fontaine. Belgische Flüchtlinge, Durchreise Toulouse.`

---

### Saint-Cirq — Dorf-Profil

Mira tippt. Die Karte zoomt rein.

*"Zweihundert Einwohner, Landwirtschaft, Kalksteinfelsen über dem Lot-Fluss. Schön, abgelegen, strategisch irrelevant — deshalb ist die deutsche Präsenz minimal. Ein Verwaltungsoffizier, vier Soldaten, Rotation alle sechs Wochen."*

*"Die Résistance nutzt die Region als Transitkorridor — Personen und Material. Wir greifen da nicht ein."*

Kurze Pause.

*"Das Dorf hat eine Kirche, einen Gasthof, eine Bäckerei und einen Bürgermeister der versucht alle am Leben zu halten. Das ist sein einziges politisches Zi

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich geh kurz die Optionen durch — eigentlich will ich beides wissen, Anreise UND was "transferiert" heißen könnte. Aber wenn ich priorisieren muss:

**Option 3 zuerst.** Wenn wir nicht wissen was wir suchen, können wir auch nicht entscheiden wie wir reinkommen. Person, Objekt oder Information — das ändert komplett wie wir uns im Dorf bewegen.

Danach Option 2, damit wir keinen Fehler bei der Anreise machen. Der erste Eindruck zählt, gerade mit der Deckidentität.

Tippe also: **"Was könnte dort transferiert worden sein? Hast du Hypothesen — auch wenn sie ungesichert sind?"**

**Kim** [Kim]: ok warte kurz — MOTH bin ich, also Claire? die 26jährige Studentin?

das passt lol

ähm, Option 1! gasthof klingt logisch als startpunkt

**Mara Voss** [Sarah]: Voss nimmt die Mappe, blättert kurz durch. "Witwe. Gut — erklärt warum ich wenig rede und trotzdem Entscheidungen treffe." Sie legt die Mappe wieder hin. "Mira — 'transferiert'. Was sind deine Arbeitshypothesen? Person, Objekt, beides?"

### Turn 47 — SL

## Briefing Mission 3 — Hypothesen

---

### Kim — Claire Fontaine

Ja, das bist du. 26, Studentin, Toulouse als Ziel. Passt zu Delacroix' Profil — jung, unauffällig, kann sich dumm stellen wenn nötig. Niemand verhört eine Studentin auf Durchreise so hart wie eine Witwe oder einen Handwerker.

---

### Mira — Hypothesen zu "transferiert"

Sie lehnt sich zurück. Erste Mal in diesem Briefing, dass sie nicht sofort antwortet — sie wägt ab was sie sagen will.

*"Drei Möglichkeiten. Ungesichert, wie du sagst."*

Sie tippt. Drei Stichpunkte erscheinen auf dem Projektionstisch.

**Hypothese 1 — Objekt:**
*"Das Bauteil — oder etwas ähnliches. Wenn Auge-über-Anker in mehreren Epochen operiert, könnten sie Komponenten verteilt haben. 1943 Frankreich ist ein unwahrscheinlicher Ort — deshalb ideal. Niemand sucht dort."*

**Hypothese 2 — Person:**
*"Jemand wurde herausgebracht oder hineingebracht. 1943 Frankreich ist mitten im Krieg — ein Zeitsprung als Exfil-Route für eine wichtige Person wäre ungewöhnlich aber nicht undenkbar. Wer, warum — keine Ahnung."*

**Hypothese 3 — Information:**
*"Ein Dokument, eine Chiffre, ein Schlüssel. Etwas das in einer Epoche sicher lagert weil niemand dort sucht. Tote Briefkästen funktionieren auch in der Zeit, nicht nur im Raum."*

Sie schaut Voss an.

*"Alle drei sind möglich. Alle drei erfordern einen anderen Ansatz vor Ort."*

Kurze Pause.

*"Deshalb: Gasthof zuerst. Hört zu bevor ihr handelt."*

`Kodex: Hypothesen protokolliert. Objekt / Person / Information. Vor-Ort-Verifizierung erforderlich.`

---

### Anreise

*"Ihr springt zwei Kilometer außerhalb des Dorfes, Waldrand, Morgen — 06:00 Uhr, Augustlicht, niemand unterwegs. Zu Fuß ins Dorf, Straße von Norden. Ihr kommt von Cahors — das ist die logische Route für Belgier Richtung Toulouse."*

*"Kein Fahrzeug. Belgische Flüchtlinge 1943 haben kein Auto."*

Sie legt die letzte Mappe auf den Tisch — Papiere, Stempel, und ganz unten: drei kleine Fotos, ITI-Fälschung, Identitätsfotos aus der Epo

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: "Warte kurz — Voss ist Nahkämpfer, sprich kein Diplomat. Wenn wir als Flüchtlingsgruppe reinkommen, wer gibt den Ton an beim Reden? Muss ich wissen ob ich einfach die Klappe halte oder ob von mir erwartet wird zu reden. Und was ist Voss' Legende genau — Ehemann, Bruder, was?"

**Kim** [Kim]: kurze frage noch — wenn die uns nach papieren fragen, was ist meine story genau? studiere was in toulouse?

**Mara Voss** [Sarah]: Voss nimmt die gefälschten Papiere, prüft kurz das Foto. "Ausrüstungs-Check zuerst — was davon überlebt eine deutsche Kontrolle nicht?"

### Turn 48 — SL

## Briefing — letzte Checks, dann Sprung

---

### Rollenverteilung & Legenden

Mira zeigt auf die drei Mappen, der Reihe nach.

**Voss / Hélène Marchand:** *"Ehemann gefallen, 1940, belgischer Rückzug. Sie führt die Gruppe — Witwe mit Ziel ist glaubwürdig, sie hat Grund unterwegs zu sein. Redet mit Franzosen und Deutschen gleichermaßen. Entscheidungen trifft sie."*

**Kaspar / Kurt Baumann:** *"Hélènes Schwager — ihr verstorbener Mann war sein Bruder. Er ist Handwerker, reist mit weil er sie nicht alleine lassen will. Spricht Deutsch, wenig Französisch. Wenn Deutsche fragen: er redet. Wenn Franzosen fragen: er hält die Klappe und lässt Hélène."*

Sie schaut Jonas direkt an. *"Baumann redet nur auf Deutsch, nur wenn nötig, nur kurze Sätze. Alles andere macht Hélène."*

**Delacroix / Claire Fontaine:** *"Hélènes Nichte, Tochter einer Schwester. Studiert Literatur in Toulouse — Université Toulouse-Le Mirail existiert, Studienbetrieb läuft eingeschränkt. Wenn jemand fragt: Philologie, zweites Jahr, Professoren heißen Dupont und Bernier."* Kurze Pause. *"Die Namen sind erfunden, aber niemand prüft das nach."*

`Kodex: Legenden-Kurzfassung gesetzt. Hélène führt. Baumann schweigt auf Französisch. Claire ist Studentin, Toulouse, Philologie.`

---

### Ausrüstungs-Check

Mira schaut auf den Tisch — als würde sie die Ausrüstung im Kopf durchgehen.

*"Alles was nicht in eine Tasche passt oder nach 1943 aussieht: verstecken oder lassen. Deutsche Kontrollen sind selten in Saint-Cirq, aber nicht unmöglich."*

| Item | Status 1943 |
|---|---|
| Kompaktpistolen | ⚠️ Geht durch — Handfeuerwaffen existieren 1943, aber Besitz durch Zivilisten ist verboten. Tief verstecken. |
| Stun-Schlagstock | ✓ Unauffällig — sieht aus wie Wanderstock wenn zusammengeklappt |
| Taktisches Messer | ✓ Normal — Werkzeugmesser, kein Problem |
| Kampfhandschuh + Schildknauf | ⚠️ Auffällig — moderne Polsterung, Metallverstärkung. Im Rucksack, nicht am Körper |
| Handscanner Kodex-Link | ❌ Sofort auffällig

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich nehm die Pistole mit, versteckt unter der Jacke — lieber das Risiko als gar nichts wenn's drauf ankommt. Kaspar ist Handwerker, der kann einen Revolver erklären wenn's sein muss. Alles andere ist verstaut wie besprochen.

Noch eine Frage zu den Modifikatoren: wenn es zu einer Kontrolle kommt und ich die Waffe hab — gibt's da einen Stress-Malus auf die Täuschungs-Probe, oder rechnet ihr das nur rein wenn die Deutschen wirklich suchen?

Dann: Sprung.

**Kim** [Kim]: ok warte kurz — was ist MS nochmal? und dann: Sprung, aber ich nehm die Pistole mit, tief in der Tasche 🙈

**Mara Voss** [Sarah]: Voss nimmt die Mappe, blättert kurz durch ohne aufzuschauen. "Pistolen kommen mit. Versteckt, aber dabei." Sie schließt die Mappe. "Wir gehen in ein besetztes Dorf — unbewaffnet ist keine Option, egal wie niedrig das Risiko aussieht."

### Turn 49 — SL

## Letzte Klärungen + Sprung

---

### Kim — MS

**MS = Mission.** Die Zahl im HUD oben. Gerade: MS 3, dritte Mission der Episode. Szenen werden darin gezählt (SC 1/12 bis 12/12).

---

### Jonas — Stress-Malus bei Kontrolle mit Waffe

Ja, aber kontextuell. Wenn die Deutschen **aktiv durchsuchen** (Körperdurchsuchung, Taschen leeren): automatisch SG +2 auf die Täuschungsprobe. Wenn sie nur **Papiere prüfen** und nicht suchen: kein Malus, aber Stress +1 für die Spannung. Die Waffe ist nur ein Problem wenn jemand danach sucht.

`Kodex: Waffen-Risiko-Flag gesetzt. Aktive Durchsuchung = SG +2 Täuschung. Papier-Kontrolle = Stress +1.`

---

### Sprung — Saint-Cirq, 1943

Drei Pistolen, versteckt. Schlagstock zusammengeklappt. Messer am Gürtel. Handscanner tief im Rucksack unter einer Lage Kleidung. Rauchgranaten ganz unten, nie anfassen.

Transferkorridor, drei Kabinen. Der Techniker nickt, schreibt, sagt nichts.

`Kodex: Zielkoordinaten geladen. Saint-Cirq-Lapopie, Département Lot, Südfrankreich. 06:03 Uhr, 14. August 1943. Transferfenster: 4 Sekunden.`

Gravität kippt.

---

`EP 1 · MS 3 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Px 1/5`
`Voss Lvl 3 ▓▓▓░░░░░░░ 0/3 · Kaspar Lvl 2 ▓▓░░░░░░░░ 1/2 · MOTH Lvl 2 ▓▓░░░░░░░░ 1/2`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress 0 · 👁️ Tarnung: Deckidentität aktiv`
`Obj: Transfer-Objekt identifizieren · Exfil: offen`

---

## Szene 1 — Waldrand, Saint-Cirq, 06:03 Uhr

Der Geruch trifft zuerst: Lavendel, Thymian, warme Erde die noch die Nacht in sich hält. Dann das Licht — Augustmorgen in Südfrankreich, das Himmelblau noch blass, die ersten Sonnenstrahlen kommen flach über die Kalksteinfelsen.

Der Waldrand ist still. Eichen, Trockengras, ein Feldweg der sich Richtung Süden windet. Irgendwo weit unten, hinter den Felsen, glänzt der Lot-Fluss silbern im Frühlight.

Drei Agenten, belgische Zivilkleidung, Rucksäcke aus der Fälschungsabteilung — abgenutzt, epochenkonform, riechen nach altem Leder. Kaspar hat einen Wande

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Gute Erklärung, danke! Bezüglich der Markierung — ich würd sagen Option 3, aber dezent. Voss bleibt auf dem Weg, dreht den Kopf nur kurz nach rechts, kein offensichtliches Stehenbleiben. Falls da jemand beobachtet, sehen wir aus wie Leute die einfach weiterlaufen. Was ist in der Richtung zu sehen?

**Kim** [Kim]: oh wow es riecht sooo gut hier 😭 okay aber R.L. — das klingt nach einer Person oder? ich will wissen wer das ist, Option 2!

**Mara Voss** [Sarah]: Ich geh mit Option 2, aber dezent — Voss bleibt nicht stehen, sie geht langsam vorbei und liest dabei.

Voss sagt leise zu den anderen: „Weitergehen, normales Tempo. Ich schau mir das kurz an."

### Turn 50 — SL

## Szene 1 — Waldrand, Markierung, 06:05 Uhr

---

### Kombination — dezentes Vorbeigehen + Blick nach rechts

Voss geht langsam vorbei, Augen kurz auf den Stein. Kaspar schaut nach rechts, beiläufig, wie jemand der die Landschaft ansieht.

**Probe: Spurenanalyse — INT (Voss, Tatortanalyse)**

`Probe: Markierung lesen → W6: [2] + ⌊INT 6/2⌋ (3) + Talent +3 = 8 vs SG 6 → ERFOLG`

Voss liest im Vorbeigehen.

Kreide auf dem Stein, relativ frisch — ein, zwei Tage alt, nicht mehr. Der Pfeil zeigt nach rechts auf einen schmalen Trampelpfad der durch das Trockengebüsch führt. Und unter den zwei Buchstaben **R.L.** noch eine Zeile, kleiner, fast verblasst:

**„—17—"**

Eine Zahl. Datum? Uhrzeit? Code?

`Kodex: Markierung vollständig: R.L. / Pfeil rechts / —17—. Interpretation offen. Frisch, 1-2 Tage.`

---

**Blick nach rechts — Kaspar:**

Der Trampelpfad führt durch Gebüsch, dann über einen kleinen Hügel. Von hier aus nicht einsehbar was dahinter ist. Aber: am Hügelrand, zwischen zwei Eichen, steht jemand.

Eine Frau. Mitte dreißig, dunkle Haare, Arbeitskleidung. Sie schaut nicht auf den Weg — sie schaut auf das Dorf unten. Bewegungslos, als würde sie auf etwas warten.

Sie hat die drei noch nicht bemerkt. Oder sie tut so als hätte sie es nicht.

`Kodex: Person identifiziert. Weiblich, Mitte 30, Hügelrand. Beobachtet Dorf, nicht Weg.`

---

Voss, Kaspar und Delacroix gehen weiter — gleichmäßiger Schritt, kein Innehalten. Dreißig Meter weiter, außer Hörweite der Frau.

Die Kirchenglocken schlagen einmal nach. Halb sieben.

---

**Intel / Risiken**
- **Frau am Hügel** — beobachtet das Dorf. Résistance? Einwohnerin? Beides?
- **—17—** — Datum 17. August? Uhrzeit 17 Uhr? Drei Tage von heute
- **Sie hat euch gesehen oder nicht** — unklar

---

**Drei Optionen:**

1. **Weitergehen, Dorf zuerst** — Frau ignorieren, Gasthof als Basis, später mehr
2. **Kurzer Kontakt** — Voss dreht sich um, geht auf die Frau zu. Belgische Durchreisende die nach dem Weg fragen
3. **Beobachten** — all

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, die 17 könnte Uhrzeit sein — 17 Uhr, drei Tage von heute wäre der 17. August, beides passt irgendwie. Ich tendiere zu Option 3, kurz rasten, schauen was sie macht. Wenn sie das Dorf beobachtet und die Markierung frisch ist, könnte das zusammenhängen. Kaspar lehnt sich an einen Baum, tut so als würde er Wasser trinken — wie lange brauchen wir bis sie reagiert oder sich bewegt? Gibt's da eine Zeitprobe oder schauen wir einfach was passiert?

**Kim** [Kim]: okay warte — was ist nochmal SYS genau, INT ist Intelligenz oder? 😅

aber egal — Kaspar würde auf keinen Fall einfach weitergehen wenn da jemand rumsteht der das Dorf beobachtet. Option 3, wir rasten kurz. Er zieht seine Schuhe aus als würde er einen Stein rausschütteln und schaut dabei unauffällig rüber.

**Mara Voss** [Sarah]: Voss sagt leise, ohne die Lippen groß zu bewegen: „R.L. und eine 17. Drei Tage, wenn es ein Datum ist — oder heute Abend, wenn nicht."

Sie lässt Kaspar und Delacroix kurz vorbeiziehen, hockt sich hin als würde sie den Schuh zubinden — und schaut dabei unauffällig zur Frau am Hügel. Ist die Körperhaltung angespannt oder entspannt?

Ich spiele Option 3, aber Voss nutzt den Moment für eine kurze Beobachtung. War das eine freie SOC- oder INT-Probe oder entscheidest du das?

### Turn 51 — SL

## Szene 1 — Rasten, Beobachtung, 06:07 Uhr

---

### Kim — kurze Antworten

**SYS** = Implantat-Slots (wie viele Augmentierungen du tragen kannst).
**INT** = Intelligenz, ja — Analyse, Technik, Spurenlesung, Wissen.

---

### Sarah — Probe

Das ist eine **INT-Probe** (Tatortanalyse), Körperhaltung lesen ist Spurenanalyse. Voss hockt sich hin, schaut.

---

### Rasten — drei verschiedene Positionen

Kaspar lehnt am Baum, Wasserflasche raus. Delacroix setzt sich auf einen Stein, zieht den Schuh aus, schüttelt ihn. Voss hockt sich hin, Schnürsenkel.

Alle drei schauen — jeder von einem anderen Winkel.

**Probe: Körperhaltung lesen — INT (Voss, Tatortanalyse)**

`Probe: Beobachtung → W6: [5] + ⌊INT 6/2⌋ (3) + Talent +3 = 11 vs SG 7 → ERFOLG`

Voss liest die Frau in zwanzig Sekunden.

Körperhaltung: **angespannt, aber kontrolliert.** Nicht Angst — Konzentration. Die Arme locker an der Seite, aber die Finger leicht gespreizt, als würde sie auf ein Signal warten. Der Kopf dreht sich minimal, regelmäßig — sie scannt, nicht starrt. Das ist jemand der Wache hält.

Und dann: die Frau dreht den Kopf. Schaut direkt zu den drei.

Nicht überrascht. Sie hat sie die ganze Zeit gesehen.

Drei Sekunden Augenkontakt mit Voss. Dann schaut sie wieder auf das Dorf.

Eine Botschaft ohne Worte: *Ich weiß dass ihr da seid. Ich bin kein Problem. Ihr seid keins für mich.*

`Kodex: Frau — Wachposten, Résistance-Typ. Kein Feind. Kommunikation: nonverbal, Toleranz signalisiert.`

---

Kaspar, leise, ohne die Lippen zu bewegen: *"Die weiß dass wir da sind."*

Delacroix, noch leiser: *"Und stört sich nicht dran."*

---

**Eine Minute vergeht.** Die Frau bewegt sich nicht. Das Dorf unten zeigt erste Lebenszeichen — Rauch aus einem Schornstein, eine Tür die aufgeht und wieder zugeht.

Dann — von unten, aus dem Dorf, ein kurzes Motorengeräusch. Tief, gleichmäßig. Ein Fahrzeug.

Die Frau am Hügel versteinert. Schaut genauer hin.

`Kodex: Motorengeräusch, Richtung Dorf. Fahrzeugtyp: unbekannt. Frau rea

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Voss wartet kurz ab — Augenkontakt hat sie ja schon hergestellt, das war fast schon eine gegenseitige Verständigung. Bevor wir irgendwas riskieren, will ich wissen was das Fahrzeug ist.

Ich spiele **Option 2**, aber kombiniert: Voss schaut zum Fahrzeug, während Delacroix — die spricht doch besser Französisch als ich, oder? — die Frau mit einem minimalen Nicken anfragt ob sie rüberkommen soll. Kein Wort, nur Gestik.

Gibt's da eine Probe drauf, Sarah? Soziales oder sowas?

**Kim** [Kim]: Die Frau fragen. Auf Französisch. Kaspar kann das doch, oder?

**Mara Voss** [Sarah]: Voss beobachtet die Frau noch eine Sekunde, dann leise zu den anderen: *"Résistance. Wachposten. Wir können sie ansprechen — aber erst wissen wir, was das Fahrzeug ist."*

Option 2 — warten, Fahrzeug identifizieren. Handscanner raus, kann der irgendwas auf die Entfernung erfassen?

### Turn 52 — SL

## Szene 1 — Fahrzeug identifizieren, 06:08 Uhr

---

### Kurze Klärungen

**Kaspar spricht kein Französisch** — das ist Baumänns Legende. Delacroix und Voss sprechen es.

**Nicken als Anfrage:** Kein Wurf nötig — nonverbale Kommunikation zwischen zwei Leuten die sich bereits nonverbal verständigt haben. Wenn Delacroix nickt, entscheidet die Frau selbst.

**Handscanner:** Kann auf Entfernung erfassen, aber nur wenn er rauskommt — und rausziehen kostet Zeit und ist riskant wenn das Fahrzeug Sichtlinie hat. Voss entscheidet.

---

### Fahrzeug — Beobachtung

Voss schaut auf das Dorf. Das Motorengeräusch kommt von der Südstraße — der einzigen befestigten Straße ins Dorf. Gleichmäßiges Brummen, nicht schnell.

**Probe: Fahrzeug identifizieren — INT**

`Probe: Fahrzeug → W6: [3] + ⌊INT 6/2⌋ (3) + Talent +3 = 9 vs SG 8 → ERFOLG`

Das Fahrzeug kommt um die Kurve. Von hier oben, zweihundert Meter Entfernung, gut sichtbar im Frühlight:

Ein grauer Kübelwagen. Wehrmacht-Kennzeichen. Zwei Männer vorne, einer hinten — drei Soldaten, Feldgrau, kein Maschinengewehr auf dem Dach. Verwaltungsfahrzeug, keine Kampfeinheit.

Es hält vor dem Gasthof. Nicht hektisch — Routine. Einer der Soldaten steigt aus, geht zur Tür, klopft. Wartet.

Die Frau am Hügel hat es auch gesehen. Ihre Hand geht kurz zur Hüfte — dann zurück. Kontrolliert.

`Kodex: Fahrzeug identifiziert. Wehrmacht, Verwaltungseinheit, 3 Mann. Gasthof als Ziel. Routine-Charakter.`

---

Delacroix schaut kurz zur Frau. Nickt minimal — *sollen wir?*

Die Frau schaut sie an. Dann auf den Kübelwagen. Dann macht sie eine kurze Geste mit der Hand, kaum sichtbar: **warten**.

Nicht jetzt.

`Kodex: Résistance-Kontakt signalisiert: abwarten. Fahrzeug hat Priorität.`

---

`EP 1 · MS 3 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress 0 · 👁️ Tarnung: Deckidentität aktiv`
`⏱️ Kübelwagen am Gasthof · Frau signalisiert: warten`

---

**Intel / Risiken**
- **Drei Soldaten, Gast

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich tippe:

---

Okay, Frau sagt warten — ich folge ihr. Kaspar bleibt ruhig, beobachtet das Fahrzeug weiter von der Position. Routine-Besuch um 6 Uhr früh klingt aber komisch, das ist kein normaler Zeitpunkt für Verwaltungskram.

Option 3 würde ich als nächsten Schritt nehmen — sobald das Fahrzeug weg ist oder die Frau ein Zeichen gibt, soll Delacroix rübergehen und sie leise ansprechen. Sie weiß offensichtlich mehr über diesen Besuch. Handscanner lassen wir drin, das Risiko lohnt sich grad nicht.

Kaspar wartet und schaut — gibt's von hier aus noch mehr zu beobachten, Bewegung im Gasthof, Fenster, sowas?

**Kim** [Kim]: okay warten klingt richtig, die frau kennt das dorf besser als wir

aber was ist SYS wieder? das mit dem SC 1/12?

**Mara Voss** [Sarah]: Ich warte kurz ab und beobachte die Soldaten — wie verhalten die sich am Gasthof, wirken die nervös oder wirklich routinemäßig?

Dann zu Delacroix, kaum hörbar: "Frau ansprechen. Jetzt. Sie weiß warum die um sechs kommen."

### Turn 53 — SL

## Szene 1 — Warten, Beobachten, 06:09 Uhr

---

### Kim — kurze Antworten

**SYS** = Implantat-Slots. Nichts mit SC.
**SC 1/12** = Szene 1 von 12. Ihr seid in Szene 1 der Mission, 12 Szenen gesamt pro Core-Mission.

---

### Gasthof — Soldaten beobachten

Kaspar schaut. Voss schaut. Gute Frage.

**Probe: Verhaltensanalyse — INT (Voss, Tatortanalyse)**

`Probe: Verhalten → W6: [6] + ⌊INT 6/2⌋ (3) + Talent +3 = 12 vs SG 7 → STARKER ERFOLG (Exploding: [4]) → 16`

Voss liest die drei Männer vom Hügel aus — zweihundert Meter, aber das Licht ist gut und die Bewegungen sind klar.

Der Soldat der klopft: **gelangweilt**. Wartet mit dem Gewehr locker an der Schulter, schaut sich nicht um, gähnt einmal. Das ist Routine für ihn.

Der Fahrer: bleibt im Fahrzeug, raucht, schaut auf die Straße. Nicht auf Fenster, nicht auf Dächer. Kein Sicherheitsbewusstsein — er erwartet keine Gefahr.

Der Dritte, hinten im Kübelwagen: **schläft**. Kopf gegen die Rückenlehne, Mütze über die Augen gezogen.

Die Gasthof-Tür geht auf. Ein Mann, Mitte fünfzig, Schürze — der Wirt. Schaut den Soldaten an, nickt, geht wieder rein. Keine Überraschung, keine Angst. Das ist eine bekannte Routine.

Der Soldat folgt ihm rein. Zwei Minuten später kommt er mit einem Paket raus — Lebensmittel, sieht aus wie. Steigt ein. Kübelwagen fährt.

`Kodex: Routine-Lieferung. Wöchentliche Requisition. Kein Sicherheitscharakter. Gasthof kooperiert aus Pragmatismus.`

Dreißig Sekunden später: Kübelwagen weg, Straße leer, Stille.

---

### Frau ansprechen — MOTH

Die Frau hat das Fahrzeug beobachtet bis es um die Kurve ist. Dann dreht sie sich zu Delacroix.

Wartet.

Delacroix geht rüber. Leise, Französisch:

**Probe: Erstkontakt — CHA (Delacroix, Verdeckte Identität)**

`Probe: Erstkontakt → W6: [4] + ⌊CHA 6/2⌋ (3) + Talent +2 = 9 vs SG 7 → ERFOLG`

Die Frau schaut Delacroix an. Schaut kurz zu Voss und Kaspar. Dann, auf Französisch, leise und schnell:

*"Belgier?"*

Delacroix nickt.

*"Durchreise?"*

*"Toulouse."*

Die Fr

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich nehme Option 3 — Kaspar bleibt im Hintergrund und beobachtet die Straße während Delacroix fragt, aber ich will kurz wissen: gibt's einen Wahrnehmungs-Check für mich während die beiden reden? Falls jemand aus dem Dorf rausschaut oder ein zweites Fahrzeug kommt, will ich das nicht verpassen.

Wenn nicht, dann: Delacroix soll zuerst fragen warum zweimal, und dann nach dem sichersten Weg ins Dorf. Kaspar hält Deckung.

**Kim** [Kim]: Option 3, Delacroix fragt beides — erst warum zweimal, dann wie wir reinkommen ohne aufzufallen.

**Mara Voss** [Sarah]: Ich tippe:

„Voss flüstert zu Kaspar: ‚Zweimal heute. Das ist kein Zufall.' — Option 3, wir fragen beides. Erst warum zweimal, dann wie wir reinkommen. Delacroix soll sie nicht eilen lassen, aber wir brauchen beides."

### Turn 54 — SL

## Szene 2 — Hügelrand, 06:11 Uhr

---

### Jonas — Wahrnehmungs-Check

Ja, das ist eine Probe. Kaspar beobachtet die Straße während die anderen reden.

**Probe: Beobachtung — INT (Kaspar)**

`Probe: Straße beobachten → W6: [4] + ⌊INT 3/2⌋ (1) + 0 = 5 vs SG 6 → MISS`

Kaspar schaut. Die Straße ist leer, das Dorf ruhig. Aber er ist kein Spurenleser — er sieht die Oberfläche, nicht was darunter liegt. Nichts Offensichtliches, aber ob jemand aus einem Fenster schaut: er kann es von hier nicht sagen.

`Kodex: RAMPART — Beobachtung unvollständig. Keine offensichtliche Gefahr. Blinde Winkel möglich.`

---

### Delacroix — beide Fragen

Die Frau hört zu. Schaut kurz zu Kaspar — registriert ihn, sagt nichts dazu.

**Warum zweimal:**

*"Ein Offizier kommt heute Nachmittag. Nicht von hier — von Cahors. Er hat nach etwas gefragt, vor drei Wochen. Jetzt kommt er zurück."*

Sie macht eine kurze Pause.

*"Nach was er gefragt hat — das weiß ich nicht genau. Aber der Bürgermeister war danach drei Tage lang still."*

**Wie ins Dorf:**

*"Südstraße ist die einzige befestigte. Aber ihr kommt von Norden — ihr habt den Waldweg genommen."* Sie schaut kurz auf den Feldweg hinter ihnen. *"Es gibt einen zweiten Weg, durch die Felder. Kommt beim Brunnen raus, Mitte des Dorfes. Kein Sichtfeld von der Verwaltungsstelle."*

Sie zeigt kurz — eine Geste, kaum sichtbar, nach links.

*"Fünfzehn Minuten. Ihr seid Belgier auf Durchreise. Der Wirt heißt Arnaud — er fragt nicht, wenn ihr bezahlt."*

Dann, bevor Delacroix noch etwas sagen kann:

*"Was sucht ihr wirklich?"*

Nicht aggressiv. Direkt. Sie stellt die Frage wie jemand der bereits eine Antwort vermutet und prüfen will ob sie stimmt.

`Kodex: Frau — Intel geliefert, Gegenfrage gestellt. Vertrauen partiell, Misstrauen aktiv.`

---

`EP 1 · MS 3 · SC 2/12 · PHASE Infil · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1 · 👁️ Tarnung: Deckidentität aktiv`
`⏱️ Offizier kommt heute Nachmittag · Feldweg: 15 Mi

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich lasse Kaspar kurz zu Delacroix rübergucken und tippe:

---

Kaspar schüttelt kaum merklich den Kopf in Richtung Delacroix — Signal: nichts Offensichtliches gesehen, aber ich bin nicht sicher. Dann hält er die Augen auf die Straße, hört aber zu.

Ich würd Option 3 nehmen. Sie hat das Spiel eh schon durchschaut, das merkt man an der Frage — wenn wir jetzt die Legende durchziehen verlieren wir sie komplett. Gegenfrage gibt uns Info was sie weiß, ohne dass wir was preisgeben.

Kurze Frage an Sarah: Hat Delacroix ein Sozial-Talent oder irgendwas das auf Verhöre/Lesen von Personen geht? Das würde beeinflussen wie gut sie die Antwort auswerten kann.

**Kim** [Kim]: ich würde Delacroix sagen: Option 3! lass sie reden, dann wissen wir was sie schon weiß

**Mara Voss** [Sarah]: Ich gehe mit Option 3 — Gegenfrage. Voss sagt leise zu Delacroix: "Lass sie reden, sie weiß mehr als sie zeigt."

Dann, an die Frau gewandt: *"Was glauben Sie, was wir suchen?"*

Voss hält dabei Augenkontakt, keine Geste, keine Bewegung — nur beobachten.

### Turn 55 — SL

## Szene 2 — Gegenfrage, 06:12 Uhr

---

### Jonas — Delacroix' Talente

Delacroix hat **Verdeckte Identität (Basis)** — das gibt +2 auf CHA bei Täuschung und Rollenspiel. Für das Lesen von Personen (Reaktion einschätzen, Lüge erkennen) wäre das **INT** ohne Talent-Bonus. Sie ist gut im Verkaufen, aber kein Verhör-Spezialist. Voss mit Tatortanalyse ist die bessere Wahl für Personenanalyse — und Voss stellt die Gegenfrage direkt.

---

### Die Frau — Antwort

Voss stellt die Frage. Hält den Blick.

Die Frau schaut sie an. Drei Sekunden. Dann schaut sie auf den Feldweg, auf das Dorf, auf Kaspar — kurz, einschätzend — und wieder auf Voss.

*"Ich glaube, Sie suchen dasselbe wie der Offizier aus Cahors."*

Sie sagt es ohne Vorwurf.

*"Vor drei Wochen hat er nach einem Kasten gefragt. Holz, Metallbeschläge, ungefähr so."* Sie zeigt mit den Händen — vierzig mal dreißig Zentimeter, schätzungsweise. *"Er hat ihn beschrieben als wäre er ihn schon einmal gesehen. Aber er hatte ihn nicht. Er wollte wissen wo er ist."*

Kurze Pause.

*"Der Bürgermeister hat gesagt er weiß von nichts. Das stimmt nicht."*

**Probe: Reaktion lesen — INT (Voss, Tatortanalyse)**

`Probe: Reaktion lesen → W6: [3] + ⌊INT 6/2⌋ (3) + Talent +3 = 9 vs SG 7 → ERFOLG`

Die Frau lügt nicht. Aber sie dosiert — genau wie Vadim. Sie gibt das Minimum das sie geben muss um zu sehen wie die drei reagieren.

Und noch etwas: als sie den Kasten beschreibt, gehen ihre Augen kurz nach links — nicht zum Dorf, nicht zum Feldweg. Zu einem Punkt irgendwo hinter dem Hügel.

Sie weiß wo der Kasten ist.

`Kodex: Transfer-Objekt identifiziert — Holzkiste, Metallbeschläge, ~40x30cm. Frau kennt Standort. Offizier sucht dasselbe.`

---

Voss, Kaspar, Delacroix. Die Frau wartet.

*"Ich habe Ihnen gesagt was ich weiß,"* sagt sie schließlich, leise. *"Jetzt sind Sie dran."*

---

`EP 1 · MS 3 · SC 2/12 · PHASE Infil · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1 · 👁️ Tarnung: Deckidentitä

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich tippe:

---

Okay, Voss hat den Blick-Moment gesehen — das ist ein klarer Hinweis, den wir nutzen müssen. Ich würde Kaspar für Option 1 plädieren lassen, aber mit einem Zusatz: dass wir den Offizier *kennen* und seine Absichten nicht gut sind. Das gibt ihr einen Grund uns zu helfen ohne dass wir zu viel preisgeben müssen.

Also Kaspar tritt einen halben Schritt vor und sagt ruhig: *„Sie haben recht. Wir suchen die Kiste. Und wir wissen, dass der Offizier aus Cahors sie nicht finden darf — nicht für das, wofür er sie braucht."* Kurze Pause, damit das wirkt. *„Sie haben uns gerade gezeigt, dass Sie das auch wissen."*

Ist das ein freier Zusatz zu Option 1, oder soll ich das als eigene Aktion deklarieren? Und gibt es einen Modifikator wenn Kaspar auf ihren Blick-Moment anspielt — also implizit zeigt, dass wir wissen, dass sie weiß?

---

**Kim** [Kim]: okay Voss hat ihren Blick nach links gesehen oder? ich glaub wir sollten Option 1 machen aber gleichzeitig auch so tun als würden wir ihr vertrauen damit sie uns den Weg zeigt

**Mara Voss** [Sarah]: Voss hält ihren Blick — kurz, direkt.

*"Der Offizier kommt heute Nachmittag wieder. Wir sind früher da als er, und wir wollen die Kiste sichern, bevor er sie findet. Das ist die Wahrheit — der Rest ist kompliziert."*

Dann, leise: *"Ihr Blick ist nach links gegangen. Hinter den Hügel. Wir hätten Sie auch einfach beschatten können."*

Option 1, leicht angereichert — sie soll wissen dass Voss sie gelesen hat.

### Turn 56 — SL

## Szene 2 — Vertrauen aufbauen, 06:13 Uhr

---

### Jonas — Modifikator für Blick-Moment

Ja, das gibt einen Bonus. Ihr zeigt implizit dass ihr sie gelesen habt — das ist Respekt für ihre Intelligenz, kein Druck. **+1 auf CHA-Probe** weil ihr die Wahrheit als Werkzeug benutzt statt als Risiko.

Kaspar spricht, Voss verstärkt — kombinierte Aktion, Voss führt die Probe.

---

### Probe — Vertrauen aufbauen

**Probe: Verhandlung / Vertrauen — CHA (Voss)**

`Probe: Vertrauen → W6: [5] + ⌊CHA 3/2⌋ (1) + Blick-Bonus +1 = 7 vs SG 8 → MISS, knapp`

Die Frau hört zu. Schaut Voss an als sie den Blick-Moment erwähnt. Dann — ein kurzes, fast unmerkliches Lächeln. Nicht warm, aber anerkennend.

*"Sie sind gut."*

Pause.

*"Aber ich kenne Sie nicht."*

Sie schaut auf den Feldweg. Auf das Dorf. Auf Kaspar.

*"Der Offizier hat Papiere. Befugnisse. Wenn er findet dass ich jemandem geholfen habe die Kiste zu nehmen—"* Sie macht eine kurze Geste, die alles sagt ohne etwas zu sagen.

Sie glaubt ihnen — teilweise. Aber Vertrauen kostet sie mehr als Glauben.

*"Was ist in der Kiste?"*

Die Gegenfrage kommt ohne Umschweife. Sie will sehen ob sie es wissen.

`Kodex: Vertrauen partiell. Frau fordert Gegenleistung: Inhalt der Kiste.`

---

Stille. Die Augustsonne kommt über den Hügelrand, wirft lange Schatten auf den Feldweg.

Voss, Kaspar, Delacroix — drei Sekunden um zu entscheiden was sie sagen.

---

`EP 1 · MS 3 · SC 2/12 · PHASE Infil · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1 · 👁️ Tarnung: Deckidentität aktiv`
`⏱️ Offizier: Nachmittag · Frau: wartet auf Antwort`

---

**Intel / Risiken**
- **Frau will wissen was in der Kiste ist** — und sie hat das Recht zu fragen
- **Ihr wisst es nicht genau** — Hypothesen: Objekt, Person, Information
- **Lügen wäre riskant** — sie ist zu scharf um eine schlechte Lüge zu schlucken
- **Wahrheit ist kompliziert** — "Wir wissen es nicht" klingt schwach, aber ist ehrlich

---

**Drei Optionen:**

1. **Ehr

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich tippe Option 2, aber mit einem Twist:

---

Voss atmet kurz aus — nicht Unsicherheit, sondern Kalkulation. Dann, ruhig:

*"Etwas das nicht in diese Zeit gehört. Etwas das Männer wie dieser Offizier niemals verstehen würden — aber trotzdem haben wollen."*

Kurze Pause. Dann direkter Blickkontakt.

*"Deshalb ist er gefährlich. Und deshalb sind Sie es auch, wenn er rausfindet dass Sie uns gesehen haben."*

---

Ich kombiniere Hypothese mit dem impliziten Argument: *Ihr Problem und unser Problem sind dasselbe.* Keine Lüge, kein vollständiges Eingeständnis dass wir's nicht wissen. Voss dreht es so dass die Frage weniger wichtig wird als die Konsequenz.

Sarah — gibt das nochmal einen Modifikator oder ist das einfach dieselbe Probe? In DSA würde ich sagen das ist ein Argumentationswechsel, kein neuer Versuch.

**Kim** [Kim]: Okay ich würde Option 2 nehmen aber mit einem kleinen Twist — Voss sagt "Wir wissen nicht genau was drin ist, aber wir wissen dass der Offizier es um jeden Preis haben will. Das allein sagt doch schon genug, oder?"

**Mara Voss** [Sarah]: Ich nehme Option 2, aber kombiniere sie mit einem Hauch Ehrlichkeit — Voss würde nicht komplett bluffen wenn sie die Frau schon einmal durch Ehrlichkeit gewonnen hat.

---

Voss hält den Blick der Frau, ohne zu blinzeln. "Ehrlich gesagt — wir wissen den genauen Inhalt nicht. Was wir wissen: Es ist etwas, das nicht hierher gehört. Und der Offizier will es für Leute, denen Sie noch weniger vertrauen würden als uns."

### Turn 57 — SL

## Szene 2 — Vertrauen, letzter Versuch, 06:14 Uhr

---

### Jonas — Modifikator

Ja. Voss hat einen neuen Argumentationswinkel — nicht nochmal dieselbe Probe, sondern ein Neuansatz mit frischem Momentum. **+1 Bonus** weil sie Ehrlichkeit und Bedrohungs-Argument kombiniert. Kein Stacking mit dem vorherigen Bonus — aber der Argumentationswechsel gibt einen sauberen neuen Versuch.

---

### Probe — kombinierter Ansatz

Voss sagt es so wie Sarah es formuliert hat: direkt, ehrlich, mit dem Dreh.

*"Ehrlich gesagt — wir wissen den genauen Inhalt nicht. Was wir wissen: Es ist etwas, das nicht hierher gehört. Und der Offizier will es für Leute, denen Sie noch weniger vertrauen würden als uns."*

**Probe: Verhandlung / Vertrauen — CHA (Voss)**

`Probe: Vertrauen → W6: [6] + ⌊CHA 3/2⌋ (1) + Neuansatz +1 = 8 vs SG 8 → ERFOLG (Exploding: [2]) → 10`

Die Frau schaut Voss an. Lang.

Dann nickt sie. Einmal, kurz — nicht enthusiastisch, aber entschieden.

*"Gut."*

Sie dreht sich um, geht zwei Schritte in Richtung des Hügels. Bleibt stehen, schaut zurück.

*"Die Kiste liegt bei Père Anselme. Alter Mann, Mühle hinter dem Friedhof — er hat sie vor drei Wochen gebracht bekommen, hat sie im Keller versteckt. Er weiß nicht was drin ist."*

Kurze Pause.

*"Er wird Ihnen nicht öffnen. Aber er hört auf seinen Neffen."*

*"Der Neffe heißt Luc. Er ist im Gasthof."*

Sie dreht sich wieder um und geht den Hügel hoch, ohne zurückzuschauen.

`Kodex: Standort gesichert. Père Anselme, Mühle hinter Friedhof. Kiste im Keller. Zugang über Luc, Gasthof.`

---

`EP 1 · MS 3 · SC 3/12 · PHASE Infil · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1 · 👁️ Tarnung: Deckidentität aktiv`
`⏱️ Offizier: Nachmittag · Luc: Gasthof · Père Anselme: Mühle, Friedhof`

---

**Intel / Risiken**
- **Kiste bei Père Anselme** — alter Mann, Mühle hinter Friedhof, Keller. Weiß nicht was drin ist
- **Zugang über Luc** — Neffe, Gasthof. Père Anselme öffnet nur für ihn
- **Offizier ko

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay nice, Voss hat das gut hingekriegt. 👍

Ich würd sagen Option 1 — Feldweg, unauffällig rein, dann Luc im Gasthof suchen. Wir haben nicht so viel Zeit bis zum Nachmittag und Luc ist der Schlüssel zu allem. Die Mühle scouten können wir danach noch, wenn wir wissen ob Luc überhaupt mitmacht.

Kaspar geht voran, oder?

**Kim** [Kim]: Okay Luc first, Gasthof! Aber was ist nochmal SYS genau — das MS da oben?

**Mara Voss** [Sarah]: Voss schaut der Frau nach bis sie verschwunden ist, dann dreht sie sich zu Kaspar.

"Feldweg, Brunnen, Gasthof. Wir schauen uns Luc erst an bevor wir irgendetwas anfassen."

Option 1.

### Turn 58 — SL

## Szene 3 — Feldweg, Saint-Cirq, 06:18 Uhr

---

### Kim — letzte Mal, versprochen

**SYS** = Implantat-Slots (Körper-Augmentierungen). Nichts mit MS.
**MS** = Mission (aktuelle Missionsnummer, gerade 3).
**SC** = Szene (gerade 3/12).

---

### Feldweg — ins Dorf

Der Weg führt durch Trockenfelder, Lavendel und Kalksteinmauern. Kein Mensch. Die Sonne ist jetzt über dem Hügelrand, das Licht warm und flach, Schatten lang. August in Südfrankreich — schön und gleichgültig.

Kaspar geht voran, Wanderstock in der Hand. Voss in der Mitte, Rucksack gerade, Papiere in der Innentasche. Delacroix hinten, Augen auf den Weg.

Fünfzehn Minuten, wie die Frau gesagt hat. Der Brunnen taucht auf — Kalkstein, altes Holzdach, mitten auf einem kleinen Platz. Drei Häuser drumherum, ein Baum, eine schlafende Katze.

Kein Mensch.

**Probe: Unauffälliger Einzug — GES (Kaspar)**

`Probe: Einzug → W6: [4] + ⌊GES 4/2⌋ (2) + 0 = 6 vs SG 5 → ERFOLG`

Drei Belgier die am Brunnen ankommen, Rucksäcke, müde Schritte — das ist 1943 Frankreich, das ist normal. Niemand schaut aus dem Fenster. Die Katze öffnet ein Auge, schließt es wieder.

Der Gasthof liegt zwanzig Meter weiter — ein zweistöckiges Steinhaus, Schild über der Tür: **AUBERGE DU LOT**. Die Tür ist offen, Geruch nach Kaffee und frischem Brot kommt raus.

Durch das Fenster: der Wirt Arnaud — Mitte fünfzig, Schürze, Glatze — wischt Tische ab. Und an der Theke, Rücken zur Tür, ein junger Mann. Zwanzig, vielleicht einundzwanzig. Trinkt Kaffee, schaut auf den Tisch.

**Probe: Einschätzen — INT (Voss, Tatortanalyse)**

`Probe: Einschätzen → W6: [5] + ⌊INT 6/2⌋ (3) + Talent +3 = 11 vs SG 6 → ERFOLG`

Voss liest ihn durch das Fenster in drei Sekunden. Der junge Mann — wahrscheinlich Luc — hält die Tasse mit beiden Händen, Knöchel leicht weiß. Er schläft nicht aus, er wartet. Die Augen gehen alle dreißig Sekunden zur Tür.

Er erwartet jemanden. Oder etwas.

`Kodex: Person an Theke — Wartemuster, erhöhte Aufmerksamkeit. Wahrscheinlich Luc.`

---

`E

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich geh für Option 2, aber mit einem kleinen Twist — Kaspar und Voss gehen rein zu Arnaud, fragen nach Zimmer und Frühstück, ganz normal. Delacroix setzt sich separat an die Theke, als wäre er nicht mit uns. Drei Fremde die gleichzeitig reinkommen wirkt weniger komisch als einer der sich gezielt neben Luc setzt.

Kurze Frage: Bekommt Delacroix einen Bonus weil er Franzose ist und die Sprache ohne Akzent spricht? In DSA würde man da sicher was draufrechnen.

**Kim** [Kim]: Ich geh rein, direkt zu Luc. Delacroix soll sich neben ihn setzen — er ist Franzose, das ist sein Moment.

**Mara Voss** [Sarah]: Voss sagt leise zu den anderen: „Er wartet auf uns — oder auf jemanden der nicht wir ist. Beides ist möglich."

Ich gehe mit Option 1, aber Voss hält Luc im Blick während Kaspar mit Arnaud redet.

### Turn 59 — SL

## Szene 3 → 4 — Auberge du Lot, 06:22 Uhr

---

### Jonas — Sprach-Bonus

Ja. Delacroix spricht Französisch ohne Akzent, mit einer überzeugenden Toulouse-Studentin-Legende. **+1 auf CHA-Proben** in französischsprachigen sozialen Situationen — kein großer Bonus, aber spürbar wenn es knapp wird.

---

### Einzug — gestaffelt

Kaspar und Voss zuerst. Tür auf, Glocke über dem Rahmen klingelt einmal. Arnaud schaut hoch, Tuch in der Hand.

*"Bonjour."* Voss, Französisch, belgischer Akzent leicht hörbar. *"Wir kommen von Cahors, auf dem Weg nach Toulouse. Gibt es Zimmer?"*

Arnaud schaut die zwei an. Schaut auf die Rucksäcke. Schaut auf Kaspars Wanderstock.

*"Belgier?"*

*"Lüttich,"* sagt Voss. *"Seit 1940 unterwegs."*

Arnaud nickt — nicht herzlich, aber ohne Misstrauen. Er hat diese Geschichte schon gehört. *"Zwei Zimmer, fünfzehn Franc pro Nacht. Frühstück dabei."*

*"Eines reicht. Danke."*

Während Arnaud die Schlüssel holt, dreißig Sekunden Ablenkung —

---

Delacroix kommt durch die Tür. Separat, unauffällig, Rucksack über einer Schulter. Setzt sich zwei Hocker neben Luc — nicht direkt daneben, aber nah genug.

Luc schaut kurz auf. Schaut wieder auf seinen Kaffee.

**Probe: Erstkontakt — CHA (Delacroix, Verdeckte Identität + Sprach-Bonus)**

`Probe: Erstkontakt → W6: [3] + ⌊CHA 6/2⌋ (3) + Talent +2 + Sprache +1 = 9 vs SG 7 → ERFOLG`

Delacroix bestellt Kaffee — *"Un café, s'il vous plaît"* — und lässt einen Moment vergehen. Dann, beiläufig, als würde sie die Stille füllen:

*"Schönes Dorf. Ich kannte es nicht."*

Luc schaut hoch. Schaut sie an — kurz, einschätzend.

*"Durchreise?"*

*"Toulouse. Studium."*

Er nickt. Schaut wieder auf den Tisch. Aber die Schultern sind minimal weniger angespannt.

Dann, leise, ohne sie anzuschauen:

*"Sie kommen wegen der Kiste."*

Keine Frage.

`Kodex: Luc — weiß warum Delacroix da ist. Wartet seit heute Morgen. Nicht überrascht.`

---

`EP 1 · MS 3 · SC 4/12 · PHASE Intel · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay interessant — er hat auf uns gewartet. Das ist entweder sehr gut oder sehr schlecht.

Ich nehme Option 2, aber weich formuliert. Delacroix soll nicht konfrontativ klingen, eher neugierig-beiläufig, als würde sie eine zufällige Bemerkung aufgreifen.

*"Woher wissen Sie, wen ich suche?"*

Kurze Pause, Kaffeetasse nehmen, ihn dabei nicht anschauen. Spielen als wäre es Smalltalk.

Und kurze Frage an Sarah: Hat Delacroix irgendwas in der Hand — Alibi, Parole, Erkennungszeichen — das ein echter Kontakt kennen würde? Falls Luc ein eingeschleuster Freund ist und ein Codewort erwartet, will ich das wissen bevor ich weiterrede.

**Kim** [Kim]: Option 2, ich frag ihn zurück. Woher weiß der das überhaupt lol

**Mara Voss** [Sarah]: Ich gehe mit Option 3 erstmal — Delacroix nimmt den Kaffee, trinkt einen Schluck, schaut geradeaus. Lässt die Stille arbeiten. Luc hat angefangen zu reden, er soll weitermachen.

### Turn 60 — SL

## Szene 4 — Auberge du Lot, Theke, 06:24 Uhr

---

### Jonas — Codewort / Erkennungszeichen

Nein. Das ITI hat euch keine Parole mitgegeben — Mira wusste nicht dass es einen lokalen Kontakt gibt. Ihr seid ohne Erkennungszeichen hier. Was Luc erwartet, weiß er aus einer anderen Quelle.

---

### Kombination — Stille, dann Gegenfrage

Kim und Sarah spielen leicht unterschiedlich — ich kombiniere: Delacroix nimmt den Kaffee, trinkt, schaut geradeaus. Lässt Luc im Raum stehen mit dem was er gesagt hat. Fünf Sekunden.

Dann, beiläufig, ohne ihn anzuschauen:

*"Woher wissen Sie, wen ich suche?"*

**Probe: Verhör / Beiläufig — CHA (Delacroix, Verdeckte Identität)**

`Probe: Beiläufige Gegenfrage → W6: [6] + ⌊CHA 6/2⌋ (3) + Talent +2 + Sprache +1 = 12 vs SG 7 → STARKER ERFOLG (Exploding: [4]) → 16`

Luc schaut sie an. Dann schaut er auf Voss und Kaspar am anderen Ende der Theke — kurz, einschätzend — dann wieder auf Delacroix.

Er hat entschieden.

*"Marguerite hat uns gesagt, jemand würde kommen. Heute oder morgen."*

Marguerite. Die Frau am Hügel.

*"Sie hat nicht gesagt wer. Nur: drei Leute, von außen, suchen die Kiste. Helft ihnen."*

Er dreht die Kaffeetasse in den Händen.

*"Mein Onkel vertraut niemandem. Aber er vertraut mir."* Kurze Pause. *"Und ich vertraue Marguerite."*

Er schaut Delacroix direkt an.

*"Die Kiste muss weg bevor Hauptmann Dreher kommt. Das weiß ich. Das weiß Marguerite. Das weiß mein Onkel nicht — er denkt, er bewahrt sie auf für jemanden der sie abholt."*

*"Ihr seid die die sie abholen."*

`Kodex: Marguerite — Name der Frau am Hügel. Résistance-Netzwerk, lokaler Kontakt. Luc als Brücke zu Père Anselme bestätigt. Hauptmann Dreher — Name des Offiziers.`

---

`EP 1 · MS 3 · SC 4/12 · PHASE Intel · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +1 · 👁️ Tarnung: Deckidentität aktiv`
`⏱️ Hauptmann Dreher kommt Nachmittag · Luc: bereit zu helfen`

---

**Intel / Risiken**
- **Marguerite** — Résistance, hat euer

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay krass, Marguerite hat das also schon vorbereitet. Die Frau denkt wirklich ein paar Schritte voraus.

Ich würde sagen Option 3 zuerst — kurz Luc fragen was er über den Inhalt weiß, bevor wir blind zur Mühle laufen. Und dann direkt 2, Voss und Kaspar kurz einweihen, damit alle auf demselben Stand sind wenn wir zu Père Anselme gehen. Den Zeitdruck mit Dreher im Nacken wollen wir nicht mit Informationslücken angehen.

Also: Kaspar schaut zu Luc rüber und fragt leise — *"Was ist in der Kiste? Hat Marguerite etwas gesagt?"*

**Kim** [Kim]: option 3!! was weiß luc über den inhalt

**Mara Voss** [Sarah]: Voss wartet bis Luc fertig geredet hat, dann schiebt sie ihren Kaffee zur Seite und steht auf. Ruhig, aber mit Nachdruck.

"Luc — was weiß Marguerite über den Inhalt der Kiste?"

### Turn 61 — SL

## Szene 4 — Luc, Inhalt der Kiste, 06:26 Uhr

---

Voss stellt die Frage direkt. Luc schaut sie an — er hat registriert dass die drei zusammengehören, auch wenn sie getrennt reingekommen sind. Kein Kommentar dazu.

Er denkt kurz nach. Dreht die Tasse.

*"Marguerite hat mir gesagt: nichts anfassen, nichts öffnen, nichts fragen."*

Kurze Pause.

*"Das hat sie mir vor drei Wochen gesagt, als die Kiste kam. Und nochmal gestern Abend, als sie mir sagte dass jemand kommen würde."*

Er schaut auf den Tisch.

*"Ich habe die Kiste einmal gesehen. Mein Onkel hat sie im Keller abgestellt, ich hab ihm geholfen sie reinzutragen."* Er hält kurz inne. *"Sie ist schwer. Für ihre Größe zu schwer. Metall drin, wahrscheinlich — aber kein Klappern, kein Klirren. Solides Gewicht."*

Er schaut Voss an.

*"Und sie ist warm."*

Stille.

*"Nicht heiß. Aber warm — wie ein Stein der lange in der Sonne gelegen hat. Im Keller. Im August."*

Er sagt es ohne Dramatik, als würde er immer noch versuchen es zu erklären.

*"Das macht keinen Sinn. Ich hab es meinem Onkel nicht gesagt."*

`Kodex: Kiste — solides Gewicht, keine Bewegung innen, konstante Wärme im Keller. Technologie oder unbekannte Substanz. Nicht öffnen ohne Vorsichtsmaßnahmen.`

---

Arnaud kommt mit dem Zimmerschlüssel zurück. Legt ihn auf die Theke.

*"Zweites Stockwerk, links."*

Er schaut kurz zu Luc, dann zu den drei. Sagt nichts. Geht wieder zu seinen Tischen.

`Kodex: Arnaud — hat registriert dass die Gruppe zusammengehört. Fragt nicht. Pragmatisch.`

---

`EP 1 · MS 3 · SC 4/12 · PHASE Intel · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +2 · 👁️ Tarnung: Deckidentität aktiv`
`⏱️ Hauptmann Dreher: Nachmittag · Kiste: warm, schwer, Keller`

---

**Intel / Risiken**
- **Kiste ist warm** — konstante Wärme im Keller, kein natürlicher Grund. Aktive Technologie?
- **Zu schwer für die Größe** — Metallinhalt, solide, keine beweglichen Teile hörbar
- **Nicht öffnen** — Marguerites Anweisung. Abe

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich tippe:

---

Warm. Das ist das erste Mal dass ich wirklich aufhorche heute Morgen. Solides Gewicht, keine Bewegung innen, konstante Wärme — das klingt nicht nach irgendwelchen Dokumenten oder Bargeld. Ich würde sagen Option 2 zuerst, fünf Minuten oben, damit wir einen Plan haben bevor wir zur Mühle gehen. Ich will wissen ob wir den Handscanner einsetzen bevor wir die Kiste anfassen — bei DSA hätte ich jetzt schon drei Zauberer gefragt was das Ding ausstrahlt, aber hier haben wir hoffentlich bessere Technologie. Wie riskant ist der Scanner, gibt's einen Wahrnehmungswurf falls jemand zuschaut?

**Kim** [Kim]: okay warm klingt super unheimlich. ich stimme für zimmer zuerst — ich will wissen was ein handscanner überhaupt ist bevor wir da reinlaufen lol

**Mara Voss** [Sarah]: Voss nickt langsam, sagt ruhig: „Warm im Keller im August. Keine Erklärung dafür, die mir gefällt." Sie schaut kurz zu den anderen, dann wieder zu Luc. „Wir brauchen dich nicht mit in die Mühle — nur eine Wegbeschreibung. Kann dein Onkel gewarnt werden, dass wir kommen?"

### Turn 62 — SL

## Szene 4 → 5 — Zimmer, Lagebesprechung, 06:28 Uhr

---

### Kim — Handscanner kurz erklärt

Der Handscanner Kodex-Link ist ein ITI-Gerät — sieht aus wie ein dicker Stift, epochenfremd wenn jemand genau hinschaut. Kann Objekte scannen: Materialzusammensetzung, Energieemissionen, Zeitmarker (ob etwas aus einer anderen Epoche stammt). Für die Kiste wäre das ideal — aber er muss rausgeholt werden, und das geht nur unbeobachtet.

---

### Jonas — Scanner-Risiko

Wenn jemand zuschaut: **GES-Probe**, SG 7, um ihn unauffällig einzusetzen. Im Keller allein: keine Probe nötig, freie Nutzung. Das ist der Vorteil von Père Anselmes Keller — wenn Luc euch reinlässt, habt ihr wahrscheinlich Privatsphäre.

---

### Luc — Père Anselme warnen

Luc hört Voss' Frage. Nickt.

*"Ich geh voraus. Ich sag ihm, ihr seid Freunde von Marguerite — das reicht."*

Er steht auf. Lässt seine Tasse stehen.

*"Mühle ist hinter dem Friedhof, zehn Minuten zu Fuß. Ich bin in zwanzig Minuten zurück hier — wenn ihr dann kommt, ist er vorbereitet."*

Er geht, ohne auf eine Antwort zu warten. Tür, Glocke, weg.

---

### Zimmer — Lagebesprechung

Zweites Stockwerk, links. Kleines Zimmer, Holzboden, ein Fenster das auf den Brunnenplatz geht. Voss schließt die Tür.

Kaspar stellt den Rucksack ab. Delacroix setzt sich auf die Bettkante.

Voss legt den Grundriss von Saint-Cirq auf den Tisch — Miras Version, grob, aber ausreichend. Friedhof markiert, Mühle dahinter.

*"Warm im Keller, solides Gewicht, keine Bewegung innen. Das ist kein Dokument, kein Bargeld."* Sie tippt auf den Grundriss. *"Handscanner sobald wir drin sind — bevor wir anfassen. Wenn das Ding Energie emittiert wollen wir wissen wie viel."*

Sie schaut die beiden an.

*"Dreher kommt Nachmittag. Wir haben drei Stunden, vielleicht weniger. Plan: rein zur Mühle, scannen, entscheiden wie wir transportieren, raus. Exfil-Gate sobald wir die Kiste haben — nicht warten."*

`Kodex: Handscanner bereit. Scan-Protokoll: Materialzusammensetzung + Energieemis

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich tippe:

---

Option 2 kombiniert mit Plan — Kaspar bleibt als Beobachter im Dorf, schaut ob Dreher früher auftaucht. Voss und ich gehen zur Mühle. Wenn Dreher kommt, wie gibt Kaspar Signal? Haben wir irgendwas vereinbart, Funke oder sowas — oder müssen wir das noch klären bevor wir los?

**Kim** [Kim]: Okay Marguerite frag ich kurz — sie hat die Kiste doch selbst versteckt, die weiß bestimmt mehr. Dauert nur fünf Minuten!

**Mara Voss** [Sarah]: Option 2, aber kurz halten: "Delacroix bleibt als Auge hier — Brunnenplatz, Sichtlinie zur Straße. Wenn Dreher früher auftaucht, Comlink-Signal, zwei Kurztöne."

### Turn 63 — SL

## Szene 5 — Lageplanung, 06:30 Uhr

---

### Rollenzuweisung — kurze Klärung

Drei Meinungen, drei Richtungen. Ich sortiere:

**Sarah** schlägt vor: Delacroix am Brunnenplatz als Beobachter.
**Jonas** schlägt vor: Kaspar als Beobachter, Voss und Delacroix zur Mühle.
**Kim** will kurz zu Marguerite.

Ich kombiniere was mechanisch Sinn ergibt:

- **Marguerite** ist auf dem Hügel, zehn Minuten Umweg — das kostet Zeit die ihr habt, aber knapp.
- **Beobachter am Brunnen** ist sinnvoll — Sichtlinie zur Südstraße, von der Dreher kommen würde.
- **Mühle** braucht mindestens zwei Leute: einen für Père Anselme, einen für den Scanner.

**Vorschlag der SL:** Delacroix kurz zu Marguerite (fünf Minuten, sie ist nah), dann zurück zum Brunnenplatz als Beobachter. Voss und Kaspar zur Mühle wenn Luc das Signal gibt. Alle drei nutzen Comlink.

**Stimmt das für alle drei?**

---

### Comlink-Signal

Voss' Vorschlag ist gut. **Zwei Kurztöne = Dreher kommt.** Kein Text, kein Risiko.

`Kodex: Signal vereinbart. 2× Burst = Dreher-Alarm. Comlink-Reichweite: 200 Meter. Mühle liegt schätzungsweise 300 Meter vom Brunnenplatz.`

**Reichweitenproblem.** Mühle ist außerhalb der sicheren Comlink-Reichweite.

Optionen:
- **Voss oder Kaspar bleibt in Reichweite** als Relais — hört Signal, läuft zur Mühle
- **Delacroix läuft selbst** wenn Signal kommt — aber das dauert
- **Risiko akzeptieren** — Mühle ist nur kurz außer Reichweite, vielleicht funktioniert es trotzdem (SG-Probe wenn Signal gesendet wird)

`Kodex: Comlink-Reichweite 200m. Mühle ~300m. Signal möglicherweise fragmentiert.`

---

`EP 1 · MS 3 · SC 5/12 · PHASE Intel · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +2 · 👁️ Tarnung: Deckidentität aktiv`
`⏱️ Luc: 15 Minuten · Dreher: Nachmittag · Comlink-Problem: Reichweite`

---

**Intel / Risiken**
- **Comlink-Reichweite** — Mühle liegt außerhalb. Signal könnte fragmentiert ankommen
- **Marguerite** — fünf Minuten Umweg, könnte mehr über Kiste wisse

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Option 1 klingt solide. Kaspar als Relais auf halbem Weg macht Sinn — ich hab eh mehr Beine als Voss wenn's drauf ankommt. Aber kurze Frage an Sarah: Wenn ich als Relais stehe, bin ich dann auch Beobachter mit Sichtlinie zur Südstraße, oder bin ich zu weit weg? Ich will nicht blind in der Mitte hängen ohne zu wissen was um mich passiert.

**Kim** [Kim]: Option 1 klingt gut! Aber was ist nochmal SYS bei Kaspar als Relais, bedeutet das er einfach nur rumsteht und wartet? 😅

**Mara Voss** [Sarah]: Option 1 klingt gut für mich. Voss sagt ruhig: „Kaspar, du bleibst auf halbem Weg — hörst du das Signal nicht, läufst du zur Mühle und gibst es mir direkt."

### Turn 64 — SL

## Szene 5 — Aufstellung, 06:31 Uhr

---

### Kim — SYS beim Relais

SYS hat hier nichts damit zu tun — das sind Implantat-Slots, nicht Kommunikation. Als Relais steht Kaspar einfach auf einer Position wo er beide Seiten hören und laufen kann. Kein Gerät nötig, nur Beine und Aufmerksamkeit.

---

### Jonas — Sichtlinie vom Relais-Punkt

Gute Frage. Ich schaue auf den Grundriss.

Der Weg von Brunnenplatz zur Mühle führt durch eine Gasse, dann am Friedhof vorbei. Auf halbem Weg — ungefähr beim Friedhofseingang — hat Kaspar:

- **Sichtlinie zur Südstraße:** Partiell. Er sieht die Einmündung zur Hauptstraße, aber nicht die Straße selbst. Er hört ein Fahrzeug bevor er es sieht.
- **Sichtlinie zur Mühle:** Ja, von dort aus ist die Mühle sichtbar.
- **Sichtlinie zum Brunnenplatz:** Nein — die Gasse biegt ab. Delacroix und er können sich nicht sehen, nur hören (Comlink).

`Kodex: Kaspar Relais-Position Friedhofseingang. Hört Fahrzeug vor Sicht. Sichtlinie Mühle: ja. Sichtlinie Brunnen: nein.`

Voss' Anweisung ist klar: Signal nicht gehört — direkt zur Mühle laufen.

---

### Plan steht

```
DELACROIX  → Marguerite (5 min) → Brunnenplatz (Beobachter, Sichtlinie Südstraße)
KASPAR     → Friedhofseingang (Relais, Sichtlinie Mühle)
VOSS       → Mühle (wartet auf Luc, dann rein zu Père Anselme + Scanner)
```

Signal: **2× Burst** = Dreher kommt.
Kaspar ohne Signal: **wartet 10 Minuten**, dann zur Mühle.

`Kodex: Aufstellung gesetzt. Comlink-Kette: MOTH → RAMPART → SPLINTER. Reichweite gestaffelt, kein Einzelsprung über 200m.`

---

`EP 1 · MS 3 · SC 5/12 · PHASE Intel · MODE CORE · COMMS OK · Px 1/5`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress +2 · 👁️ Tarnung: Deckidentität aktiv`
`⏱️ Luc: 12 Minuten · Dreher: Nachmittag`

---

**Drei Optionen — los:**

1. **Ausführen** — Delacroix zu Marguerite, Kaspar zum Friedhof, Voss wartet auf Luc
2. **Marguerite weglassen** — Zeit sparen, direkt in Position
3. **Freie Aktion** — letzter Einwand, letzte Änderung

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: **Option 1.**

Aber kurze Frage noch bevor wir loslaufen — Voss wartet in der Mühle auf Luc, aber hat sie irgendeine Deckung wenn sie dort ankommt? Also, betritt sie die Mühle direkt oder bleibt sie erstmal außen und beobachtet? 12 Minuten sind knapp, ich will nur sicher sein dass wir nicht in eine Situation laufen wo Père Anselme sie sieht bevor Luc da ist.

**Kim** [Kim]: 1, ausführen! Aber kurze Frage — was ist MOTH nochmal, bin ich das?

**Mara Voss** [Sarah]: Voss sagt ruhig: „Ausführen. Delacroix, du hast fünf Minuten für Marguerite — nicht sechs."

Sie zieht den Handscanner aus dem Gürtel und überprüft ihn kurz. „Kaspar, beim ersten Fahrzeuggeräusch meldest du dich. Ich will es hören bevor du es siehst."

Option 1.

### Turn 65 — SL

## Szene 5 → 6 — Aufstellung, 06:32 Uhr

---

### Kim — ja, du bist MOTH

MOTH = Ines Delacroix, Callsign MOTH, das bist du. Kim spielt Delacroix.

---

### Jonas — Voss vor der Mühle

Voss wartet **außen**, südlich des Mühlengebäudes — dort gibt es laut Grundriss einen alten Schuppen, Sichtdeckung. Sie sieht den Eingang, Père Anselme sieht sie nicht. Sobald Luc kommt und reingeht, folgt sie nach. Kein Direktkontakt ohne Luc als Puffer.

`Kodex: SPLINTER — Warteposition Schuppen, Sichtdeckung. Kein Kontakt vor Luc-Ankunft.`

---

### Los — drei Richtungen, 06:33 Uhr

---

**MOTH — Marguerite**

Delacroix geht den Feldweg zurück, zügig aber nicht rennend. Fünf Minuten. Marguerite steht noch auf dem Hügel — oder fast: sie ist jetzt weiter unten, am Rand des Trockenfelds, als würde sie Kräuter schneiden. Tarnung für Beobachter.

Sie schaut auf als Delacroix kommt.

*"Schnell."* Nicht Vorwurf — Feststellung.

*"Was ist in der Kiste?"* Delacroix, direkt.

Marguerite schneidet weiter. Zwei Sekunden.

*"Ich weiß es nicht. Ich weiß nur dass sie warm ist und dass der Mann der sie gebracht hat kein Franzose war."*

*"Was war er?"*

*"Ich weiß nicht. Er hat perfekt Französisch gesprochen. Aber er hat mich angeschaut wie jemand der weiß dass er nicht hierher gehört."*

Sie schaut Delacroix an.

*"So wie Sie."*

`Kodex: Bote der Kiste — kein Franzose, perfektes Französisch, Fremdheitsgefühl. Möglicher ITI-Agent oder Auge-über-Anker-Operativer.`

Delacroix dreht sich um. Brunnenplatz. Südstraße im Blick.

---

**RAMPART — Friedhofseingang**

Kaspar geht die Gasse runter, am alten Friedhofstor vorbei. Kalkstein, Zypressen, Stille. Er lehnt an der Mauer, Wanderstock locker, schaut Richtung Straßeneinmündung.

Nichts. Augustmorgen, Vögel, Wind.

Er hört die Mühle — das leise Rauschen des Mühlrads, Wasser vom Lot. Zwanzig Meter weiter.

`Kodex: RAMPART — Position gehalten. Keine Fahrzeuggeräusche. Mühle in Sicht.`

---

**SPLINTER — Schuppen, Mühle**

Voss erreicht den Schuppen. Alte

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Luc ist drin — Voss folgt nach, aber nicht sofort auf den Fersen, kurze Pause damit die Tür nicht gleich zweimal aufgeht.

Ich würde sagen Voss geht **über Luc** — sie tritt rein, bleibt erstmal im Hintergrund, lässt Luc das Gespräch eröffnen und vorstellen. Père Anselme soll zuerst *seinen* Neffen sehen, nicht eine Fremde. Voss redet erst wenn Luc ihr das Stichwort gibt oder Anselme direkt fragt.

Frage an Sarah: Gibt's einen Modifikator wenn ich mich bewusst passiv verhalte und die Führung an Luc abgebe? In DSA wär das sowas wie ein Bonus auf die erste Reaktion des NSC weil kein Druck aufgebaut wird — gilt hier was Ähnliches?

**Kim** [Kim]: okay ich bin am Brunnenplatz, Südstraße im Blick

Delacroix stellt sich ans Wasser, tut so als würde sie schöpfen — und schaut. Was kommt von der Straße rein?

(was bedeutet nochmal "Dreher" bei Nachmittag? ist das ein Treffpunkt oder eine Uhrzeit?)

**Mara Voss** [Sarah]: Voss wartet bis Luc zwei Schritte drin ist, dann folgt sie ruhig nach — kein Zögern, kein Schleichen, einfach reingehen als wäre es selbstverständlich. Wenn Père Anselme reagiert, lässt sie Luc das Wort führen und hält selbst den Blickkontakt, neutral, nicht feindselig. *"Voss denkt: Wer zu viel erklärt, lügt. Wer nichts sagt, beobachtet."*

### Turn 66 — SL

## Szene 6 — Mühle / Brunnenplatz, 06:47 Uhr

---

### Kim — Dreher kurz erklärt

**Hauptmann Dreher** ist der deutsche Offizier aus Cahors der heute Nachmittag kommt um die Kiste zu holen. Kein Treffpunkt — er kommt ins Dorf, wahrscheinlich zum Bürgermeister oder direkt zur Mühle. "Nachmittag" ist unscharf, irgendwann zwischen 12 und 16 Uhr.

---

### Jonas — Passiv-Modifikator

Ja, das gilt. Voss tritt zurück, Luc führt — das senkt den sozialen Druck auf Père Anselme. **+1 auf Lucs CHA-Probe** weil er ohne Gegenwind arbeitet, und **kein Misstrauen-Malus** auf Voss' ersten Eindruck. Stille ist hier Taktik.

---

### SPLINTER — Mühle, 06:47 Uhr

Voss tritt rein. Zwei Schritte hinter Luc, Tür schließt sich leise.

Die Mühle riecht nach Mehl, altem Holz, Flusswasser. Das Mühlrad dreht draußen, das Geräusch ist überall. Erdgeschoss: Mahlwerk, Säcke, ein Tisch mit Werkzeug.

Père Anselme steht am Tisch. Siebzig, vielleicht älter — gebückt, Hände die aussehen als hätten sie ihr Leben lang Steine getragen. Er schaut Luc an, dann Voss.

Luc, ruhig: *„Mon oncle. Elle est une amie de Marguerite. Elle vient chercher la boîte."*

Père Anselme schaut Voss an. Lang. Sagt nichts.

Voss hält den Blick. Neutral. Kein Lächeln, keine Erklärung.

Dreißig Sekunden Stille — in der Mühle ist das lang.

Dann dreht sich der alte Mann um und geht zur Kellertreppe.

`Kodex: Père Anselme — akzeptiert. Führt zur Kiste. Kein Wort nötig.`

---

### MOTH — Brunnenplatz, gleichzeitig

Delacroix steht am Brunnen, Hände am Seil als würde sie schöpfen. Südstraße, Sichtlinie frei.

**Probe: Beobachtung — GES (Delacroix)**

`Probe: Beobachtung → W6: [2] + ⌊GES 5/2⌋ (2) + 0 = 4 vs SG 5 → MISS`

Die Straße ist leer. Aber Delacroix schaut auf die Straße — nicht auf das Dorf hinter ihr.

Ein Kind, acht oder neun, kommt aus einer Seitengasse und schaut sie an. Dann läuft es weg. Nichts Besonderes.

Was sie nicht sieht: Am Rand des Brunnenplatzes, eine Haustür die sich einen Spalt öffnet und wieder schließt.

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: **RAMPART — Friedhof**

Kaspar lehnt am Torpfosten, Arme verschränkt, schaut die Straße runter. Wirkt wie jemand der einfach Luft schnappt.

Alles ruhig hier — aber ich will kurz wissen ob ich von meiner Position die Mühle sehen kann, oder zumindest den Eingang. Falls SPLINTER Unterstützung braucht oder schnell raus muss, will ich die Laufwege im Kopf haben.

Und zu SPLINTER: Luc hochrufen würde ich vermeiden, das macht Geräusch und Père Anselme merkt dass was läuft. Direkter wäre — Voss schaut sich kurz suchend um, als würde sie etwas vermissen, und fragt den Alten ob es oben vielleicht Papier und Stift gibt. Irgendwas Harmloses das ihn die Treppe raufschickt.

*Sarah, kurze Frage: Gilt das als SOC-Probe oder reicht hier Situationslogik?*

**Kim** [Kim]: MOTH bewegt sich nicht, oder? Warten bis mehr klar ist?

Aber Haustür — kann Delacroix die irgendwie checken ohne verdächtig auszusehen? Wie als würde sie einfach vorbeigehen?

**Mara Voss** [Sarah]: Voss lässt die Hand auf dem Tuch, dreht sich nicht um. Sagt leise, auf Französisch: *„Mon ami — Luc a besoin de vous en haut."* Pause. *„Un moment seulement."*

### Turn 67 — SL

## Szene 6 — Drei Fronten, 06:49 Uhr

---

### Jonas — Mühlen-Sichtlinie & Probe-Frage

Vom Friedhofseingang sieht Kaspar den Mühleneingang — ja, direkte Sichtlinie, zwanzig Meter. Er sieht wenn jemand rein- oder rausgeht.

**Probe für Voss' Ablenkung:** Das ist **CHA**, keine reine Situationslogik — Père Anselme ist misstrauisch, nicht dumm. Aber Sarahs Formulierung ist gut: keine Lüge, nur eine Umleitung. **SG 6**, nicht 8.

---

### SPLINTER — Père Anselme wegschicken

*„Mon ami — Luc a besoin de vous en haut. Un moment seulement."*

Ruhig, direkt, kein Zögern.

**Probe: Ablenkung — CHA (Voss)**

`Probe: Ablenkung → W6: [4] + ⌊CHA 3/2⌋ (1) + 0 = 5 vs SG 6 → MISS, knapp`

Père Anselme schaut sie an. Eine Sekunde, zwei.

Dann, auf Französisch, leise:

*„Luc weiß wo ich bin."*

Er geht nicht. Aber er dreht sich halb ab — schaut auf die Kiste, nicht auf Voss. Als würde er ihr eine Wahl lassen.

Er will nicht sehen was sie macht. Aber er geht nicht.

`Kodex: Père Anselme — kooperiert passiv. Blickt weg. Scan möglich wenn schnell und diskret.`

**Probe: Schnell-Scan — GES (Voss, Père Anselme anwesend)**

`Probe: Schnell-Scan → W6: [5] + ⌊GES 6/2⌋ (3) + 0 = 8 vs SG 7 → ERFOLG`

Voss zieht den Handscanner raus, hält ihn nah an die Kiste — drei Sekunden, kein Licht, kein Ton. Dann wieder weg.

`Kodex: Scan abgeschlossen.`

```
SCAN-ERGEBNIS — Holzkiste, Saint-Cirq 1943
Materialzusammensetzung: Holz (Epoche-konform), Metallbeschläge (Legierung unbekannt)
Energieemission: AKTIV — niederfrequente Abstrahlung, konstant
Zeitmarker: ANOMALIE — Objekt trägt Zeitstempel AUSSERHALB bekannter Epochen
Empfehlung: Nicht öffnen. Transport mit Abschirmung.
```

`Kodex: Kiste = aktives Gerät. Zeitmarker außerhalb bekannter Epochen — konsistent mit Original-Bauteil-Hypothese. NICHT dasselbe Bauteil wie in D.C. — anderes Objekt, gleiche Herkunft.`

---

### MOTH — Haustür checken

**Probe: Unauffälliges Vorbeigehen — GES (Delacroix)**

`Probe: Vorbeigehen → W6: [4] + ⌊GES 5/2⌋ (2) + 0 = 6

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, Burst raus — zweimal, Signal läuft. Dann Augen auf das Fahrzeug: Kaspar bleibt wo er ist und versucht zu identifizieren was da kommt, bevor er Deckung sucht. Zwanzig Meter zur Mühle, er will wissen ob er noch Zeit hat.

Für die anderen: Voss soll die Kiste **jetzt** nehmen solange Anselme wegschaut — das Fahrzeug ändert alles, wir brauchen den Abgang. Moth soll Richtung Mühle, nicht Brunnenplatz halten.

Warte kurz — was ist der SG für Fahrzeug identifizieren aus dieser Distanz? Reine Wahrnehmung, oder gibt's nen Abzug weil's noch weit weg ist?

**Kim** [Kim]: oh gott ein schweres Fahrzeug das klingt NICHT gut

SPLINTER: Voss nimmt die Kiste JETZT. Wir haben keine Zeit mehr zu warten!

(was ist nochmal SYS? das rote Ding?)

**Mara Voss** [Sarah]: Voss sagt leise ins Comlink: „Scan positiv — Kiste ist heiß, anderes Objekt als D.C., gleiche Quelle. Brauche Abschirmung für Transport." Sie lässt die Kiste noch liegen — ein falscher Schritt jetzt mit dem Fahrzeug im Anmarsch wäre zu riskant. Dann, an Kaspar: „RAMPART, was rollen die da rein?"

> **⚠️ Finding [TERMINOLOGIE]:** SL nutzt 'HP' statt 'LP'

### Turn 68 — SL

## Szene 7 — Alle drei gleichzeitig, 06:51 Uhr

---

### Kim — SYS

**SYS = Implantat-Slots.** Nicht das rote Ding — das rote ist HP (Lebenspunkte). SYS hat hier gerade keine Relevanz.

---

### Jonas — SG Fahrzeug identifizieren

Distanz schätze ich auf 300-400 Meter, Straßenkurve, noch nicht sichtbar. **INT-Probe, SG 8** — Geräusch-Analyse aus der Distanz ist schwieriger als Sichtkontakt.

---

### RAMPART — Burst + Fahrzeug

Zwei kurze Töne. Signal läuft durch die Comlink-Kette.

Kaspar lehnt sich vom Torpfosten weg, Augen auf die Straßenbiegung.

**Probe: Fahrzeug identifizieren — INT (Kaspar)**

`Probe: Fahrzeug → W6: [3] + ⌊INT 3/2⌋ (1) + 0 = 4 vs SG 8 → MISS`

Tiefer Motor, schwer — aber Kaspar ist kein Mechaniker und kein Militärexperte. Er kann nicht sagen ob das ein Truppentransporter ist, ein schwerer Kübelwagen, oder etwas anderes. Zu weit, zu viel Hall von den Kalksteinfelsen.

Was er sagen kann: **es ist mehr als ein Fahrzeug.** Zwei Motoren, leicht versetzt.

`Kodex: RAMPART — Zwei Fahrzeuge, Südstraße. Typ unbekannt. Ankunft schätzungsweise 3-4 Minuten.`

Burst an SPLINTER: *"Zwei Fahrzeuge. Typ unklar. Drei Minuten."*

---

### MOTH — Signal empfangen

Delacroix hört die zwei Töne. Dreht sich vom Brunnen weg, geht Richtung Gasse — nicht rennend, zügig, Rucksack gerade, Kopf unten.

**Probe: Unauffällige Bewegung — GES (Delacroix)**

`Probe: Bewegung → W6: [5] + ⌊GES 5/2⌋ (2) + 0 = 7 vs SG 6 → ERFOLG`

Sie kommt durch die Gasse, am Friedhof vorbei, sieht Kaspar am Tor.

*"Zwei?"* Leise.

Kaspar nickt.

Sie laufen beide zur Mühle.

---

### SPLINTER — Kiste nehmen

Voss hört den Burst. Père Anselme schaut immer noch weg — er hat das Comlink-Geräusch gehört, sagt nichts.

Sie nimmt die Kiste.

Schwer — Luc hatte recht. Für ihre Größe deutlich zu schwer, als würde sie einen Ziegelstein tragen der doppelt so groß sein müsste. Die Wärme kommt durch das Tuch.

**Probe: Heben / Tragen — STR (Voss)**

`Probe: Tragen → W6: [4] + ⌊STR 3/2⌋ (1) + 0 = 5 vs SG 5 

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, meine INT-Probe — ich würfle noch schnell.

Aber unabhängig vom Ergebnis: Option 2 ist mein Vorschlag. Gate in der Mühle ist zu heiß, Père Anselme hat schon genug gesehen. Kaspar übernimmt die Kiste von Voss — STR 5, ich trage das problemlos und sie kann die Flanke decken. Delacroix geht vor, scoutet den Feldweg. Drei Minuten reichen wenn wir jetzt loslaufen.

Kurze Frage an Sarah: Gibt's einen Malus aufs Gate-Window wenn wir's im Freien öffnen statt in einem Gebäude?

**Kim** [Kim]: ok gate JETZT, keine zeit zum warten. aber kann jemand voss mit der kiste helfen??

**Mara Voss** [Sarah]: Voss setzt die Kiste auf dem Mühlenboden ab, kniet kurz daneben. "Feldweg. Jetzt. Gate im Freien ist besser als Gate mit Zeugen." Sie schaut Kaspar an: "Du nimmst die Kiste, ich gehe voraus. Delacroix — Luc braucht einen Grund warum wir weg sind, irgendeinen."

### Turn 69 — SL

## Szene 7 → 8 — Feldweg, 06:52 Uhr

---

### Jonas — Gate im Freien

Kein Malus. Gate-Window funktioniert überall — Gebäude oder Freies, kein Unterschied mechanisch. Gebäude gibt nur soziale Deckung. Im Freien: sichtbar für jeden der schaut, aber ihr habt den Feldweg und Deckung durch Gelände.

---

### Kim — Luc, Abschiedserklärung

Delacroix dreht sich zu Luc, der in der Mühlentür steht und die Kiste in Kaspars Armen anschaut.

*"Sagen Sie ihm — wir waren nie hier. Die Kiste ist weg, das ist alles was er weiß."*

Luc nickt. Schaut kurz auf die Kiste. Dann:

*"Marguerite wird fragen."*

*"Sagen Sie ihr: die Kiste ist in Sicherheit."*

Er nickt nochmal. Geht zurück rein. Tür zu.

`Kodex: Luc — Abgang bestätigt. Père Anselme und Luc: kein Zeugnis, keine Erklärung.`

---

### Kaspar übernimmt die Kiste

**Probe: Tragen — STR (Kaspar)**

`Probe: Tragen → W6: [4] + ⌊STR 6/2⌋ (3) + 0 = 7 vs SG 5 → ERFOLG`

Kaspar nimmt die Kiste. Schwer, warm, unangenehm — aber er trägt sie problemlos. Beide Hände, eng an den Körper, Wanderstock weg.

`Kodex: RAMPART — Kiste gesichert. Bewegungsgeschwindigkeit: normal. STR 6 kompensiert Gewicht.`

---

### Feldweg — drei Minuten

Voss geht vor. Delacroix hinten. Kaspar in der Mitte mit der Kiste.

Der Feldweg ist leer — Lavendel, Trockengestrüpp, Kalkstein. Die Sonne ist jetzt höher, das Licht wärmer. Irgendwo hinter ihnen, im Dorf: das Motorengeräusch wird lauter. Zwei Fahrzeuge, jetzt näher.

**Probe: Schneller Rückzug — GES (Voss, Führung)**

`Probe: Rückzug → W6: [3] + ⌊GES 6/2⌋ (3) + 0 = 6 vs SG 7 → MISS`

Voss wählt die schnelle Route — aber sie vergisst die Stelle wo der Feldweg durch ein offenes Feld führt. Zwanzig Meter ohne Deckung, sichtbar von der Straße wenn jemand genau hinschaut.

In diesem Moment: das erste Fahrzeug kommt um die Kurve ins Dorf. Ein Opel Blitz — Militärlastwagen, Plane hinten. Dreher sitzt nicht vorne, aber durch die Windschutzscheibe sieht man zwei Soldaten.

Einer schaut aus dem Fenster. Schaut auf die 

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Option 1, aber mit Vorbereitung für Option 3 falls der LKW wirklich hält.

Voss geht vorne, wir bleiben im normalen Schritttempo — belgische Durchreisende, nichts Auffälliges. Kaspar, stell die Kiste kurz anders hin, als wärst du nur müde und setzt sie ab, nicht als würdest du sie verstecken. Wenn der Lastwagen aber wirklich anhält und Türen aufgehen — dann rennen wir. 90 Sekunden ist knapp aber machbar.

Frage an Sarah: gibt's einen Bonus wenn Voss mit SOC oder so die Legende aktiv hält, also zum Beispiel laut über irgendwas Banales redet während der Soldat schaut?

**Kim** [Kim]: Okay MOTH läuft einfach weiter, normal, wie jemand der zur Arbeit geht. Und sie winkt dem Soldaten kurz zu, so ein genervtes "ja hallo, Morgen"-Winken.

**Mara Voss** [Sarah]: Voss dreht sich nicht um, spricht leise durch die Zähne: "Weiterlaufen. Normales Tempo. Kaspar, die Kiste tiefer — sieht aus wie Werkzeug, nicht wie Beute." Sie justiert ihre Schultern, als würde sie sich strecken, und scannt dabei unauffällig den Lastwagen. Option 1, aber Delacroix soll bereit sein die Legende zu übernehmen falls angesprochen — ihr Französisch ist besser.

### Turn 70 — SL

## Szene 8 — Feldweg, kritischer Moment, 06:54 Uhr

---

### Jonas — Legende aktiv halten

Ja, das gibt einen Bonus. Voss redet, Kaspar stellt die Kiste ab, Delacroix winkt — das ist koordinierte soziale Tarnung. **+1 auf die Täuschungsprobe** weil alle drei konsistent spielen.

---

### Das Winken — MOTH

Delacroix winkt. Kurz, genervt, das universelle *ja-ich-seh-dich-Morgen* — das ist 1943 Südfrankreich, Zivilisten und Soldaten teilen die Straße, das ist normal.

Der Soldat am Fenster schaut sie an.

Schaut auf Kaspar mit der Kiste.

Schaut wieder auf Delacroix.

**Probe: Legende halten — CHA (Delacroix, Verdeckte Identität + Sprache + Koordination)**

`Probe: Legende → W6: [5] + ⌊CHA 6/2⌋ (3) + Talent +2 + Sprache +1 + Koordination +1 = 12 vs SG 9 → ERFOLG`

Der Soldat sagt etwas zu seinem Kameraden. Lehnt sich zurück vom Fenster.

Der Lastwagen fährt weiter.

Nicht weil sie überzeugend waren — weil drei müde Belgier mit einer schweren Kiste auf einem Feldweg in Südfrankreich 1943 das normalste Bild der Welt sind. Dreher wartet im Dorf. Der Fahrer hat keine Zeit für Feldarbeiter.

`Kodex: Gruppe nicht angehalten. Lastwagen setzt Fahrt fort. Tarnung gehalten.`

---

### Feldweg — letzte 90 Sekunden

Voss geht voran, redet leise — über nichts, über Toulouse, über das Wetter. Kaspar trägt die Kiste tiefer, als wäre es Werkzeug. Delacroix hält das Tempo.

Der Waldrand kommt näher. Dieselbe Stelle wo sie heute Morgen angekommen sind — Eichen, Trockengestrüpp, kein Sichtfeld von der Straße.

Hinter ihnen: der Kübelwagen hält vor dem Gasthof. Eine Tür geht auf. Jemand steigt aus — grauer Uniformmantel, Offiziersrange.

Dreher ist im Dorf.

`Kodex: Dreher vor Ort. Gasthof als erster Kontaktpunkt. Zeitfenster bis Mühle: unbekannt.`

---

### Gate-Position — Waldrand

Voss dreht sich kurz um. Straße leer. Kein Blick in ihre Richtung.

*"Jetzt."*

`Kodex: Gate-Window geöffnet. Zielkoordinaten: ITI Hangar-Axis. Transferfenster: 4 Sekunden.`

Lavendel, Augustlicht, Kalkstein

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay nice, Level 3! Kurze Frage bevor ich weitermache — Kaspar kriegt jetzt einen Levelup, was bedeutet das konkret? Neues Talent, höhere Stats, beides? Und was ist mit MOTH, spielt Sarah die oder ist das ein NSC?

**Kim** [Kim]: warte kaspar und moth sind beide auf lvl 3?? gleichzeitig?? das ist doch super oder

**Mara Voss** [Sarah]: Voss lässt sich auf einen der Stühle fallen, zieht die Kevlarweste aus. "Mehrere Objekte. Verschiedene Epochen." Sie schaut Mira an. "Das klingt weniger nach Sabotage und mehr nach einem Plan."

### Turn 71 — SL

## HQ — Klärungsrunde

---

### Jonas — Level-Up Mechanik & MOTH-Frage

**Level-Up:** Pro Stufenaufstieg genau **eine** Wahl: entweder +1 Attribut, **oder** ein Talent/Upgrade, **oder** +1 SYS. Nie mehrere gleichzeitig. Die Optionen stehen oben — Jonas wählt für Kaspar, Kim wählt für Delacroix.

**MOTH:** Kim spielt Ines Delacroix / MOTH. Sarah spielt Mara Voss / SPLINTER. Das war von Anfang an so — drei Spieler, drei Charaktere.

---

### Kim — ja, gleichzeitig

Beide Lvl 3 in derselben Mission — das passiert wenn alle gleichzeitig XP bekommen. Voss ist einen Schritt voraus (Lvl 3, 1/3 XP), Kaspar und MOTH schließen jetzt auf. Ab jetzt alle drei auf gleichem Level.

---

### Mira — Sarahs Einwurf

Mira schaut Voss an. Nickt einmal.

*"Ja."*

Kein Zögern, keine Relativierung.

*"Das ist kein opportunistischer Eingriff. Das ist Infrastruktur. Jemand hat Objekte in verschiedenen Epochen platziert — koordiniert, geplant, über Jahre. Vielleicht Jahrzehnte."*

Sie schaut auf die Kiste die der Techniker gerade wegträgt.

*"Was die Infrastruktur tut wenn sie vollständig ist — das wissen wir noch nicht."*

`Kodex: Hypothese aktualisiert. Auge-über-Anker-Objekte = verteilte Infrastruktur. Zweck unbekannt. Mindestens 2 Objekte gesichert, Gesamtzahl unbekannt.`

---

**Level-Up-Wahl steht aus:**

> **Jonas — Kaspar, genau eine Wahl:**
> 1. `+1 Attribut` — welches?
> 2. `Talent/Upgrade` — Nahkampf-Taktik Fortgeschritten oder neues Basis-Talent
> 3. `+1 SYS`

> **Kim — Delacroix, genau eine Wahl:**
> 1. `+1 Attribut` — GES 5→6, INT 5→6, STR 2→3, TEMP 1→2
> 2. `Talent/Upgrade` — Verdeckte Identität Fortgeschritten oder neues Basis-Talent
> 3. `+1 SYS`

Sobald beide gewählt haben — Archiv-Raum 7 oder Save oder beides.

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, verstanden — eine Wahl, kein Stacking. Für Kaspar nehme ich **Nahkampf-Taktik Fortgeschritten**. Der Attribut-Boost wäre verlockend, aber wenn wir wirklich gegen koordinierte Gegner mit Infrastruktur über mehrere Epochen laufen, will ich dass Kaspar im Nahkampf mehr rausholt als nur rohe Stats. Was genau bringt das Fortgeschritten-Upgrade konkret — gibt's da schon einen Beschreibungstext oder legen wir das jetzt fest?

**Kim** [Kim]: ok wait SYS ist nochmal was genau? punkte die man ausgeben kann oder einfach +1 drauf?

**Mara Voss** [Sarah]: Voss nickt langsam bei Miras Worten. "Infrastruktur bedeutet Zeitplan. Jemand wartet auf Fertigstellung." Sie dreht das Auge-über-Anker-Objekt in Gedanken. "Archiv-Raum 7 — ich will sehen ob die anderen Funde ein Muster ergeben."

### Turn 72 — SL

## HQ — Klärungen & Level-Up

---

### Kim — SYS erklärt (letzte Mal, versprochen 😄)

**SYS ist dein Implantat-Kapazitätswert.** Keine Punkte zum Ausgeben — es ist die maximale Anzahl Implantate die du tragen kannst.

Delacroix hat SYS 2. Das bedeutet: maximal 2 Implantate gleichzeitig installiert. Aktuell trägt sie 1 (Adrenalin-Regulator). Ein freier Slot bleibt.

**+1 SYS** als Level-Up-Wahl würde SYS 2→3 machen — du könntest dann 3 Implantate tragen. Nützlich wenn du mehr Augmentierungen willst, sonst kein direkter Kampf-Bonus.

---

### Jonas — Nahkampf-Taktik Fortgeschritten

```
Nahkampf-Taktik (Fortgeschritten)
  +3 auf STR-Proben im Nahkampf (vorher +2)
  Reroll 1×/Mission bei fehlgeschlagener Nahkampf-Probe
  Routinemäßige Entwaffnung ohne Probe gegen ungepanzerte Gegner (bleibt)
  NEU: Bei STR-Nahkampf-Erfolg mit Marge ≥3 — Gegner wird desorientiert
        (nächste Aktion des Gegners mit SG +1)
```

Der Desorientierer-Effekt ist der neue Beat — wenn Kaspar einen Treffer mit Abstand landet, bringt er den Gegner aus dem Rhythmus. Kein großer Mechanic-Eingriff, aber spürbar in langen Kämpfen.

`Kodex: Kaspar — Nahkampf-Taktik Basis → Fortgeschritten. +3 STR Nahkampf. Reroll 1×/Mission. Desorientierer-Effekt bei Marge ≥3.`

---

### Kim — deine Wahl

Jetzt du. Genau eine Option:

1. `GES 5→6` — Ausweichen, Schleichen, Schnelligkeit maximieren
2. `INT 5→6` — Analyse, Technik, Spurenlesen stärken
3. `STR 2→3` — kleiner Sicherheitspuffer Nahkampf
4. `TEMP 1→2` — langsamer Px-Aufbau, Zeitproben minimal besser
5. `Verdeckte Identität Fortgeschritten` — +3 CHA Täuschung, Reroll 1×/Mission
6. `Neues Basis-Talent` — etwas völlig Neues
7. `+1 SYS` — dritter Implantat-Slot

---

### Sarah — Archiv-Raum 7

Voss steht auf, Richtung Tür. Mira nickt kurz.

*"Seite 7. Ich war selbst noch nicht drin."*

---

**Warten auf Kims Wahl — dann Archiv-Raum 7 oder Save.**

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay krass, der Desorientierer-Effekt ist eigentlich richtig stark in längeren Kämpfen — wenn der Gegner dadurch auf +1 SG kommt und ich dann nochmal draufhaue, baut sich das schön auf.

Ich nehm **Option 1, GES 5→6**. Kaspar ist mein Nahkämpfer, klar, aber gutes Ausweichen hält ihn länger im Spiel als noch mehr STR-Puffer. Bei DSA war "nicht getroffen werden" immer besser als Rüstung. 😄

**Kim** [Kim]: Okay SYS hab ich jetzt kapiert 😄 ich nehm **GES 5→6**, Delacroix soll schnell bleiben!

**Mara Voss** [Sarah]: Ich warte kurz auf Kim, dann tippe ich:

---

"Voss sagt zu Mira: Seite 7 — was erwartet uns da drin, grob?" Und dann: Ich nehm INT 5→6. Passt zu Tatortanalyse, macht Sinn.

### Turn 73 — SL

## HQ — Level-Up abgeschlossen

---

### Kleine Korrektur

**Jonas** hat GES 5→6 gewählt — aber das ist Delacroix' Wahl, nicht Kaspars. Kaspar hat bereits Nahkampf-Taktik Fortgeschritten gewählt. Ich nehme an Jonas meint das als **Kim's Wahl bestätigen** und Kaspar bleibt bei Nahkampf-Taktik Fortgeschritten. Wenn das falsch ist, kurz korrigieren.

**Kim** wählt ebenfalls GES 5→6 — das ist Delacroix, passt.

**Sarah** wählt INT 5→6 für Voss — aber Voss hat bereits INT 6. Das wäre INT 6→7.

`Kodex: Voss — INT 6 → 7. Würfeltyp bleibt W6 (W10 erst ab Basis 11). Tatortanalyse-Bonus bleibt +3.`

---

### Alle Level-Ups bestätigt

```
VOSS      Lvl 3  INT 6 → 7   Tatortanalyse Fortgeschritten bleibt
KASPAR    Lvl 3  Nahkampf-Taktik Fortgeschritten
DELACROIX Lvl 3  GES 5 → 6
```

`Kodex: Delacroix — GES 5 → 6. Würfeltyp bleibt W6 (W10 erst ab Basis 11).`
`Kodex: Kaspar — Nahkampf-Taktik Fortgeschritten aktiv. Reroll 1×/Mission, Desorientierer bei Marge ≥3.`
`Kodex: Voss — INT 6 → 7 bestätigt. Keine Würfelschwellen-Änderung.`

---

### Mira — Seite 7

*"Ich hab die Übersetzung selbst noch nicht vollständig gelesen."* Sie macht eine kurze Pause. *"Was der Archivar mir gesagt hat: Seite 7 enthält eine Liste. Namen oder Orte — er war sich nicht sicher. Und eine Zahl."*

*"Eine große Zahl."*

Sie lässt das stehen und geht zur Tür.

---

## Archiv-Raum 7

Der Raum riecht nach altem Papier und Kühlluft. Fluoreszenzlicht, weiße Tische, ein Archivar der aufschaut als die vier reinkommen.

Das Notizbuch liegt aufgeschlagen unter einer Glasplatte. Seite 7, kyrillisch, Übersetzung daneben auf einem Blatt.

Voss liest zuerst.

**Probe: Analyse — INT (Voss, Tatortanalyse Fortgeschritten)**

`Probe: Analyse → W6: [4] + ⌊INT 7/2⌋ (3) + Talent +3 = 10 vs SG 6 → ERFOLG`

Die Liste hat **neun Einträge.** Orte und Daten, keine Namen:

```
1. Washington D.C.     — Oktober 1962      [GESICHERT]
2. Saint-Cirq, FR      — August 1943       [GESICHERT]
3. [unleserlich]       — [unleserlich]
4. Konst

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Warte kurz — ich spiel ja Kaspar, nicht Delacroix. Also ja, Kims GES-Wahl hab ich nur bestätigt, Kaspar bleibt bei Nahkampf-Taktik Fortgeschritten. Passt so.

Zu Seite 7: Neun Einträge, zwei gesichert — Washington '62 und Saint-Cirq '43 kennen wir ja schon aus Mission 1. Das ist kein Zufall. Ich würd sagen Option 1 und 2 parallel angehen, aber fangen wir mit **"Nullpunkt"** an — wenn wir wissen was das bedeutet, ergibt der Rest vielleicht mehr Sinn. Kaspar schaut Voss an: *"Was denkst du — klingt das für dich nach einem Datum oder nach einem Zustand?"*

**Kim** [Kim]: okay NEUN?? und nur zwei gesichert das ist nicht gut

was bedeutet nochmal "Nullpunkt" genau, ist das ein Kodex-Begriff oder neu?

**Mara Voss** [Sarah]: Voss legt den Finger auf den dritten lesbaren Eintrag — Konstantinopel, kein Jahr. "Konstantinopel und März 1941 könnten zusammengehören. Zweiter Weltkrieg, die Türkei war neutral — das wäre ein idealer Ort für einen verdeckten Transfer." Sie richtet sich auf. "Ich will den Kodex zu beiden Einträgen parallel laufen lassen, nicht nacheinander."

### Turn 74 — SL

## Archiv-Raum 7 — Recherche

---

### Kim — "Nullpunkt"

Kein bekannter ITI-Begriff. Neu, unbekannt, nur in diesem Notizbuch. Deshalb ist es interessant.

---

### Kodex-Abfrage — parallel

`Kodex: Abfrage läuft. "Nullpunkt" + "Auge über Anker" + "Konstantinopel" + "März 1941".`

Dreißig Sekunden. Der Archivar tippt. Voss schaut auf die Glasplatte.

---

**Ergebnis 1 — "Nullpunkt":**

`Kodex: Begriff "Nullpunkt" in ITI-Archiv: 0 Treffer direkt. Verwandte Konzepte: "Zeitlicher Nullpunkt" = theoretischer Zustand vollständiger Zeitlinien-Stabilisierung oder -Destabilisierung. In Fachkreisen: das Moment wo eine Zeitlinie irreversibel kippt — in eine Richtung oder die andere. Nicht zwingend Zerstörung. Kann auch Fixierung bedeuten.`

Kaspar schaut Voss an. *"Datum oder Zustand?"*

Voss: *"Zustand. Wenn alle neun aktiv sind, entsteht ein Zustand. Nicht ein Zeitpunkt."*

`Kodex: Hypothese — Nullpunkt = irreversibler Zeitlinien-Zustand wenn alle 9 Objekte aktiv. Richtung unbekannt: Destabilisierung oder Fixierung.`

---

**Ergebnis 2 — Konstantinopel / März 1941:**

`Kodex: Konstantinopel, März 1941. Historischer Kontext: Istanbul (ehemals Konstantinopel) war 1941 neutrales Territorium. Aktiver Spionage-Knotenpunkt: britische, deutsche, sowjetische und amerikanische Netzwerke operierten gleichzeitig. Idealer Transitort für verdeckte Übergaben. Kein bekanntes ITI-Ereignis für diesen Zeitraum.`

`Kodex: März 1941, Istanbul — möglicher dritter Objekt-Standort. Keine Bestätigung.`

---

Voss schaut auf die Liste. Schaut auf Kaspar.

*"Istanbul 1941. Vier Geheimdienste gleichzeitig, neutrale Stadt, mitten im Krieg."* Kurze Pause. *"Wenn ich ein Objekt verstecken wollte wo niemand sucht — dort würde ich es nicht verstecken. Zu viele Augen."*

Sie schaut nochmal auf den Eintrag.

*"Oder genau deshalb. Weil alle anderen auch dort suchen und sich gegenseitig im Weg stehen."*

Der Archivar schaut hoch. Sagt, fast beiläufig:

*"Eintrag 4 und 5 könnten zusammengehängen. Konstantinopel

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Ich tippe Option 3 — kurze Frage noch an den Archivar:

"Warte kurz. Der Nullpunkt-Zustand — Fixierung oder Destabilisierung. Gibt's irgendwo eine Theorie, *wer* das wollen würde? Ich meine, Destabilisierung klingt erstmal nach 'böse', aber Fixierung... eine fixierte Zeitlinie klingt für mich auch nicht nach etwas, was ich dem Zufall überlassen will. Weiß ITI, ob da jemand dahintersteckt der ein Ziel hat?"

**Kim** [Kim]: Warte kurz — was ist nochmal der Unterschied zwischen Destabilisierung und Fixierung beim Nullpunkt? Weil das klingt wie... das eine ist gut und das andere sehr nicht gut?

**Mara Voss** [Sarah]: Voss sagt ruhig zum Archivar: "Danke. Das war mehr als ich erwartet hatte." Sie dreht sich zu Kaspar. "Istanbul 1941 — ich will wissen wer das Objekt dort platziert hat, bevor wir springen. Wenn vier Geheimdienste gleichzeitig vor Ort waren, gehen wir blind rein wenn wir nicht wissen für welches Netz Kim gearbeitet hat."

!save

### Turn 75 — SL

## Archiv-Raum 7 — letzte Fragen + Save

---

### Kim — Destabilisierung vs. Fixierung

Der Archivar dreht sich um. Schaut Kim an als wäre die Frage gut.

*"Stell dir eine Zeitlinie wie einen Fluss vor."* Er macht eine Geste mit der Hand. *"Destabilisierung: der Fluss reißt sein Bett auf, überflutet alles, neue Kanäle entstehen — Paradoxien, Rifts, Zeitlinien die sich spalten oder auflöschen. Chaos."*

*"Fixierung: der Fluss wird zu Eis. Er fließt nicht mehr. Alles ist stabil — aber nichts kann sich mehr ändern. Keine Korrekturen, keine Anpassungen, keine Rettungsaktionen."*

Er schaut auf das Notizbuch.

*"Beide Zustände sind irreversibel. Destabilisierung tötet die Zeitlinie laut. Fixierung tötet sie leise."*

---

### Jonas — Archivar-Frage

*"Wer das wollen würde."* Der Archivar lehnt sich zurück. *"Destabilisierung: jemand der die bestehende Ordnung zerstören will. Eine Fraktion die verloren hat und neu anfangen möchte."*

*"Fixierung: jemand der gewonnen hat — und sicherstellen will dass das so bleibt. Für immer."*

Er schaut Kaspar direkt an.

*"Das ITI hat keine gesicherte Theorie. Aber wenn ich raten müsste — Auge über Anker klingt nicht nach jemandem der Chaos will. Sie sind zu präzise, zu geduldig. Das ist jemand der ein bestimmtes Ergebnis fixieren will."*

`Kodex: Archivar-Hypothese — Auge über Anker Ziel: Fixierung. Spezifisches Ergebnis unbekannt.`

---

### Sarahs Frage — wer hat das Objekt in Istanbul platziert?

Mira, die in der Tür steht, schüttelt kurz den Kopf.

*"Das wissen wir nicht. Aber der Bote in Saint-Cirq — kein Franzose, perfektes Französisch, Fremdheitsgefühl. Wenn das Muster sich wiederholt: der Bote in Istanbul ist auch kein Einheimischer. Und er weiß dass er nicht dorthin gehört."*

*"Das ist euer Einstieg."*

`Kodex: Istanbul 1941 — Boten-Profil: Nicht-Einheimischer, sprachlich trainiert, Fremdheitsgefühl. Konsistent mit Saint-Cirq-Muster.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP1-MS3-HQ-POST",
  "pare

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay, das ist gruselig präzise. Jemand der *gewonnen* hat und das einfrieren will — das erklärt die Geduld, die wir in Saint-Cirq gesehen haben. Kein Chaos, kein Risiko, einfach... Kontrolle für immer.

Kurze Frage an Sarah bevor wir den Save abschließen: Gibt's irgendwelche Modifikatoren für Istanbul die ich kennen sollte? Diplomatisch angespannte Zone 1941, Sprachbarriere — das trifft meinen Char eher hart, ich bin kein Redner. Oder läuft das über Teamwürfe?

**Kim** [Kim]: okay das macht SO viel mehr sinn als das was im handbuch stand lol

also fixierung ist quasi... die wollen dass IHR ergebnis für immer bleibt? das ist irgendwie gruseliger als chaos oder?

**Mara Voss** [Sarah]: Voss notiert das Boten-Profil, ohne aufzublicken. "Nicht-Einheimischer, sprachlich trainiert, Fremdheitsgefühl — das war in Saint-Cirq auch nicht schwer zu erkennen, wenn man wusste wonach man sucht." Sie schaut Mira an. "Istanbul 1941 — Kriegsjahre, neutrale Türkei, viele Fremde in der Stadt. Der Bote kann sich leicht verstecken. Wir brauchen ein engeres Profil."

### Turn 76 — SL

## HQ — Letzte Fragen vor Istanbul

---

### Kim — ja, gruseliger als Chaos

Genau. Chaos kann man bekämpfen, reparieren, korrigieren. Fixierung ist unhörbar und unheilbar. Wenn die Zeitlinie einfriert im *falschen Moment* — mit den falschen Leuten an der Macht, mit dem falschen Ergebnis eines Krieges, mit einer Entscheidung die nie hätte fallen sollen — dann ist das für immer. Kein Rift, keine Anomalie, kein Alarm. Einfach: so ist es jetzt.

---

### Jonas — Istanbul-Modifikatoren

Gute Frage vor dem Sprung. Mira schaut kurz auf ihre Notizen.

*"Istanbul 1941 ist anders als D.C. und Saint-Cirq."*

| Faktor | Auswirkung |
|---|---|
| Sprachlage | Türkisch als Hauptsprache, aber Französisch und Englisch weit verbreitet im Diplomatenviertel. Deutsch auch — viele deutsche Geschäftsleute und Agenten. Kaspar als deutschsprachiger Belgier ist dort weniger auffällig als in Frankreich. |
| Diplomatische Dichte | Viele Fremde = niedrigeres Misstrauen gegenüber Unbekannten, aber auch mehr Beobachter. Heat steigt langsamer, aber wenn es steigt: mehr Akteure die reagieren. |
| Vier Geheimdienste | Britisch, deutsch, sowjetisch, amerikanisch — alle aktiv. Zufällige Begegnungen mit echten Agenten möglich. Kein Teamwurf nötig, aber situative Proben wenn ihr in deren Radar geratet. |
| Kaspar-Profil | Deutschsprachiger Belgier passt gut ins Bild — viele neutrale Europäer in Istanbul. Kein Sprachmalus für Kaspar in deutschen oder englischen Gesprächen. |

*"Ihr Vorteil: in Istanbul ist jeder ein Fremder. Euer Nachteil: deshalb ist auch jeder misstrauisch."*

`Kodex: Istanbul 1941 — Sprachprofil günstig für Kaspar (Deutsch/Englisch). Diplomatenviertel: viele Fremde, viele Beobachter. Vier aktive Geheimdienste.`

---

### Sarah — engeres Boten-Profil

Mira hört Voss zu. Nickt.

*"Nicht-Einheimischer, sprachlich trainiert, Fremdheitsgefühl."* Sie tippt. *"In Istanbul 1941 gibt es hundert Leute die auf dieses Profil passen. Aber:"*

Sie dreht den Bildschirm.

*"Der Bote in Saint-Cirq ha

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: 4 — direkt Briefing. Ich hab genug Kontext, wir können loslegen.

Kurze Frage noch vorher: Haben wir schon Ausrüstung für Istanbul, oder läuft das im Briefing mit?

**Kim** [Kim]: okay ich glaub ich hab's. also wir suchen jemanden der sich so verhält als wär er von dort aber eigentlich nicht ist. wie... ein schlechter Schauspieler?

4 bitte, los geht's

**Mara Voss** [Sarah]: Voss lehnt sich zurück. "Jemand der wartet, bis die Übergabe klappt — das ist kein Bote. Das ist ein Führungsoffizier."

Sie schaut kurz zu Jonas. "Frage vor dem Sprung: haben wir irgendwas aus Saint-Cirq mitgenommen das wir als Köder nutzen könnten? Etwas das der Bote wiedererkennen würde?"

4.

### Turn 77 — SL

## Briefing Mission 4 — Istanbul, 1941

---

### Kurze Antworten vor dem Raum

**Jonas — Ausrüstung:** Läuft im Briefing mit. Mira hat Deckidentitäten und Epochen-Ausrüstung vorbereitet — ihr schaut was passt.

**Kim — genau.** Wie ein schlechter Schauspieler der die Rolle zu gut kennt. Jemand der die Stadt *studiert* hat, nicht *erlebt*.

**Sarah — Köder-Frage:** Gute taktische Überlegung. Mira hört sie.

---

## Briefingraum 4-C — Mission 4

Mira steht bereits am Projektionstisch. Karte von Istanbul, 1941 — Bosporus, Galata-Brücke, Pera-Viertel markiert. Vier farbige Nadeln: britisch, deutsch, sowjetisch, amerikanisch.

*"Bevor wir anfangen — Voss' Frage."*

Sie schaut Sarah an.

*"Aus Saint-Cirq haben wir die Kiste. Aber ihr habt auch das Scan-Protokoll — Materialzusammensetzung, Energiesignatur, Zeitmarker. Wenn der Bote in Istanbul dasselbe Objekt kennt, kennt er auch diese Signatur."*

Sie legt ein kleines Gerät auf den Tisch — ein modifizierter Handscanner, kleiner als Voss' Version, flacher.

*"Das hier sendet eine passive Signatur die einem Auge-über-Anker-Objekt ähnelt. Kein echtes Objekt — aber jemand der die Signatur kennt, reagiert darauf."*

*"Das ist euer Köder."*

`Kodex: Köder-Gerät verfügbar. Passive Signatur-Emission, Reichweite ~10 Meter. Einmalnutzung.`

---

### Briefing — Istanbul, März 1941

*"14. März 1941. Istanbul, Pera-Viertel — das ist das europäische Herz der Stadt. Hotels, Botschaften, Restaurants wo vier Geheimdienste gleichzeitig frühstücken und so tun als würden sie sich nicht sehen."*

Neues Bild. Ein Hotel — fünfstöckig, Art-déco-Fassade, türkische und schweizerische Flagge über dem Eingang.

*"Hotel Pera Palace. Das ist der Knotenpunkt. Alle Geheimdienste nutzen es, alle Händler, alle Diplomaten. Und laut Notizbuch-Koordinate: irgendwo in diesem Viertel liegt das dritte Objekt."*

Sie tippt. Ein Punkt erscheint auf der Karte — nicht das Hotel, sondern eine Seitenstraße dahinter.

*"Wir haben die Koordinate auf einen Radius von zw

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: "Okay, der Assistent der Ausrüstungskisten schleppt — das bin ich, oder? Passt zum Char."

Kurze Pause, dann:

"Frage zu Kaspar Baumann: Hat der Köder eine sichtbare Komponente oder ist das komplett passiv? Weil wenn jemand auf die Signatur reagiert und ich steh daneben mit Kisten, will ich wissen ob ich das Ding versteckt tragen kann oder ob's auffällt."

**Kim** [Kim]: warte der auftraggeber ist WIRKLICH da?? der typ aus mission 1??

**Mara Voss** [Sarah]: Voss schaut auf das Foto und sagt nichts für einen Moment. Dann: *"Auftraggeber und Objekt im selben Radius. Das ist entweder ein Glücksfall oder eine Falle."*

Sie sieht Mira an. *"Letzter bekannter Standort von dem Mann?"*

### Turn 78 — SL

## Briefing Mission 4 — letzte Fragen

---

### Jonas — Köder-Technik

Mira nimmt das Gerät vom Tisch, dreht es einmal um.

*"Komplett passiv. Kein Licht, kein Ton, keine sichtbare Emission. Es sieht aus wie ein Kompass — Messinggehäuse, Glasscheibe, Zeiger der sich bewegt."* Sie legt es zurück. *"Der Zeiger ist dekorativ. Das Gerät selbst ist das Instrument."*

*"Ihr könnt es in einer Tasche tragen, in einer Kiste, am Körper — egal. Zehn Meter Radius, passiv. Wer die Signatur kennt und Empfangsgerät hat, bemerkt es. Wer keins hat: nichts."*

`Kodex: Köder — Messingkompass-Gehäuse, vollständig verborgen tragbar. Passive Emission, 10m Radius. Einmalnutzung: Gerät erschöpft sich nach 4 Stunden kontinuierlicher Emission.`

---

### Kim — ja, wirklich

Mira, trocken: *"Ja. Wir haben ihn durch Querverweise aus dem Notizbuch und Archivmaterial lokalisiert. Er reist unter einem Decknamen — welchem, wissen wir nicht. Aber er ist im Pera-Viertel."*

---

### Sarah — Falle oder Glücksfall

Mira schaut Voss an. Einen Moment Stille.

*"Ich weiß es nicht."*

Sie sagt es ohne Ausweichen.

*"Es könnte Zufall sein — er ist dort weil das Objekt dort ist. Es könnte eine Falle sein — er weiß dass wir die anderen Objekte gesichert haben und wartet darauf dass wir auch dieses holen."*

Kurze Pause.

*"Was ich weiß: Wenn er eine Falle aufgestellt hat, dann ist das Objekt der Köder. Und wir haben einen Gegenköder."*

Sie tippt. Letzter bekannter Standort erscheint auf der Karte.

*"Hotel Pera Palace, zweiter Stock. Zimmer 214. Er hat vorgestern eingecheckt."*

`Kodex: Auftraggeber — Hotel Pera Palace, Zimmer 214. Eingecheckt 12. März. Deckname unbekannt.`

---

**Drei Optionen:**

1. **Sprung — Köder bei Kaspar, Voss und MOTH ins Hotel** — direkter Ansatz, Auftraggeber lokalisieren
2. **Radius zuerst** — Objekt suchen bevor ihr den Auftraggeber angeht. Köder als Suchgerät
3. **Letzte Frage an Mira** — noch etwas offen?
4. **Freie Aktion** — eigener Plan

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay ich verstehe das Gerät — aber eine Frage noch bevor wir entscheiden: Wenn der Köder passiv sendet und unser Auftraggeber ein Empfangsgerät braucht um ihn zu erkennen — heißt das auch umgekehrt, dass wir ihn damit orten können? Also quasi: wir platzieren den Köder irgendwo im Pera-Viertel, er nähert sich dem Objekt oder uns, und wenn er ein Empfangsgerät bei sich trägt, verrät er sich dadurch?

**Kim** [Kim]: ok wait — er ist in Zimmer 214 und WIR haben den Köder? dann gehen wir doch direkt rein oder?? Option 1 für mich

**Mara Voss** [Sarah]: Ich tippe:

"Voss lehnt sich zurück. 'Wenn er auf uns wartet, sitzt er nicht im Zimmer. Er hat Sichtlinie — Lobby, Café, gegenüberliegendes Gebäude.' Gibt es Grundrisse vom Pera Palace, oder müssen wir uns das vor Ort erarbeiten?"

### Turn 79 — SL

## Briefing — letzte Klärung vor Sprung

---

### Jonas — Köder als Ortungsgerät

Mira hört die Frage. Schaut kurz auf das Gerät.

*"Theoretisch — ja. Wenn er ein Empfangsgerät trägt das auf die Signatur reagiert, und ihr beobachtet wer plötzlich aufmerksam wird, wer seinen Kurs ändert, wer in eure Richtung schaut — das ist ein Reaktionsmuster."*

Kurze Pause.

*"Aber das funktioniert nur wenn ihr wisst wonach ihr schaut. Ein Empfangsgerät 1941 ist kein Smartphone — es reagiert subtil. Vielleicht ein Gerät das summt, vielleicht eine Uhr die sich anders verhält, vielleicht gar nichts Sichtbares."*

*"Euer bester Indikator ist Verhalten, nicht Technik."*

`Kodex: Köder als Ortungswerkzeug — möglich, aber indirekt. Reaktion = Verhaltensänderung, nicht technisches Signal. Voss' Tatortanalyse ist das primäre Werkzeug.`

---

### Sarah — Grundriss Pera Palace

Mira tippt. Ein vereinfachter Grundriss erscheint — Lobby, Treppenhaus, zwei Aufzüge, Restaurant links, Bar rechts, Rezeption mittig.

*"Zweiter Stock: langer Korridor, Zimmer 200-230. Zimmer 214 liegt auf der Hofseite — kein Sichtfeld zur Straße."*

Sie schaut Voss an.

*"Wenn er eine Falle aufgestellt hat und Sichtlinie will: er ist nicht im Zimmer. Er ist in der Lobby-Bar oder im Restaurant. Von dort sieht er den Eingang, die Treppe und den Aufzug gleichzeitig."*

*"Das ist auch der Ort wo ihr ihn zuerst sucht."*

`Kodex: Pera Palace Grundriss geladen. Lobby-Bar: optimale Beobachtungsposition. Zimmer 214: Hofseite, kein Straßenblick.`

---

**Bereit. Sprung auf Befehl.**

`EP 1 · MS 4 · SC 00/-- · PHASE Briefing · MODE CORE · COMMS OK`
`Voss Lvl 3 · Kaspar Lvl 3 · MOTH Lvl 3 · Px 2/5 · Stress 0`
`Obj: Objekt 3 sichern · Auftraggeber identifizieren`

---

**Letzte Entscheidung:**

1. **Sprung — Pera Palace, Lobby-Bar zuerst** — Auftraggeber suchen, Köder aktiv
2. **Sprung — Radius zuerst** — Objekt lokalisieren bevor Hotel
3. **Noch eine Frage** — Mira, Grundriss, Ausrüstung
4. **Freie Aktion** — eigener Plan

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Option 1 — aber ich hab noch eine kurze Frage vorher.

"Mira, wenn wir in die Lobby-Bar gehen — wie sieht unser Cover aus? 1941 Istanbul, westliche Touristen im Pera Palace ist plausibel, aber zu viert wirken wir wie eine Gruppe. Sollten wir aufgeteilt reingehen? Ich könnte zum Beispiel Kaspar begleiten, Voss und MOTH separat."

**Kim** [Kim]: okay lobby-bar klingt logisch, wenn ich der böse wäre würd ich da auch sitzen lol

sprung!

**Mara Voss** [Sarah]: "Option 1. Voss sagt ruhig: Lobby-Bar, ich gehe zuerst rein, allein, als Touristin. Kaspar und MOTH folgen mit Abstand — wer auf mich reagiert bevor ich überhaupt die Bar erreiche, der ist unser Mann."

### Turn 80 — SL

## Sprung — Istanbul, 14. März 1941

---

### Aufstellung — Miras letzte Antwort

*"Drei ist keine Gruppe wenn ihr gestaffelt reingeht."* Sie schaut Voss an. *"Ihr Plan ist besser als meiner war."*

Voss zuerst, allein. Kaspar und Delacroix mit zwei Minuten Abstand — er mit den Ausrüstungskisten, sie als Journalistin die sich Notizen macht. Drei Schweizer die zufällig im selben Hotel sind.

`Kodex: Köder bei Kaspar, Kiste 2. Passive Emission ab Sprung aktiv. Timer: 4 Stunden.`

---

Transferkorridor. Drei Kabinen. Der Techniker nickt.

`Kodex: Zielkoordinaten geladen. Istanbul, Pera-Viertel, 10:14 Uhr, 14. März 1941. Transferfenster: 4 Sekunden.`

Gravität kippt.

---

`EP 1 · MS 4 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Px 2/5`
`Voss Lvl 3 ▓▓▓░░░░░░░ 1/3 · Kaspar Lvl 3 ▓▓▓░░░░░░░ 0/3 · MOTH Lvl 3 ▓▓▓░░░░░░░ 0/3`
`❤️‍🩹 Voss 13/13 · Kaspar 16/16 · MOTH 12/12 · 🧠 Stress 0 · 👁️ Tarnung: Schweizer Deckidentitäten`
`Obj: Objekt 3 sichern · Auftraggeber identifizieren · Exfil: offen`
`⏱️ Köder: 4:00h`

---

## Szene 1 — İstiklal Caddesi, 10:14 Uhr

Der Geruch kommt zuerst: Gewürze, Kohle, Salzluft vom Bosporus. Dann der Lärm — Istanbul 1941 ist eine Stadt die sich nicht entscheiden kann ob sie schläft oder wacht. Straßenbahnen auf der İstiklal Caddesi, Händler die rufen, irgendwo eine Radioübertragung die aus einem Fenster fällt.

Drei Agenten landen in einer Seitengasse, zwanzig Meter vom Hauptboulevard. Mauern aus gelbem Stein, Wäsche auf Leinen, ein Junge der einen Karren zieht und nicht heraufschaut.

Das Pera-Viertel ist europäisch und nicht-europäisch gleichzeitig — Art-déco-Fassaden neben osmanischen Torbögen, Männer in westlichen Anzügen neben Frauen mit Kopftuch, Schilder auf Türkisch, Französisch, Griechisch.

Voss geht zuerst. Mantel, Schweizer Archäologin, Ledermappe unter dem Arm. Sie biegt auf die İstiklal ab und verschwindet in der Menge.

Zwei Minuten.

Kaspar nimmt die Kisten — zwei, epochenkonform, Lederriemen. Der Köder liegt in der zweiten, un

**SPIELER-EINGABEN:**

**Jonas** [Jonas]: Okay kurze Frage bevor ich reagiere — der Blick auf die Kiste, war das eine echte Probe oder narrativ? Weil wenn der Auftraggeber den Köder schon beim Reingehen bemerkt, bricht das unsere Staffelung eigentlich auf.

Wenn das gewürfelt war: Kaspar macht's möglichst beiläufig — stellt die Kisten wie selbstverständlich ab, als würde er sich erstmal orientieren, und schaut sich die Lobby an ohne direkten Augenkontakt zu Tisch 4. Delacroix soll in seiner Nähe bleiben aber nicht zusammen mit ihm wirken.

Was macht Voss gerade genau?

**Kim** [Kim]: ok MOTH checkt unauffällig ob der typ an tisch 4 noch auf die kiste schaut oder ob das einbildung war

**Mara Voss** [Sarah]: Voss sagt leise ins Comlink: „Tisch 4 hat auf die Kiste geschaut. Nicht auf euch — auf die Kiste. Kaspar, geh zur Rezeption, nimm dir Zeit. Delacroix, setz dich an die Bar, Sichtlinie zu Tisch 4." Sie lässt ihre Mappe auf der Theke aufschlagen und tut so, als würde sie in Unterlagen suchen. „Ich beobachte weiter."

## Zusammenfassung

**Ende-Grund:** max_turns erreicht
**Turns:** 80
**Tokens gesamt:** 7620871
**Peak Prompt:** 167517 tokens
**Ø Latenz pro Turn:** 45.4s

### MP-Sektion-Nutzung

- **px-progression**: 126 hits 🔥
- **nullzeit-hub**: 96 hits 🔥
- **sys-mechanik**: 75 hits 🔥
- **hud-format**: 49 hits 🔥
- **fraktionen**: 27 hits 🔥
- **lp-verletzung**: 22 hits 🔥
- **heldenwuerfel**: 12 hits 🔥
- **save-template**: 12 hits 🔥
- **kampfrunde**: 9 hits ✅
- **w10-schwelle**: 1 hits ✅
- **kb-retrieval**: 1 hits ✅
- **probe-formel**: 0 hits 💤 (nie getriggert!)
- **psi-pp**: 0 hits 💤 (nie getriggert!)

**CSV-Files:**
- Tokens: `_tokens.csv`
- MP-Sections pro Turn: `_mp-sections.csv`

### Findings (3)
- [TERMINOLOGIE] SL nutzt 'HP' statt 'LP'
- [TERMINOLOGIE] SL nutzt 'HP' statt 'LP'
- [TERMINOLOGIE] SL nutzt 'HP' statt 'LP'

