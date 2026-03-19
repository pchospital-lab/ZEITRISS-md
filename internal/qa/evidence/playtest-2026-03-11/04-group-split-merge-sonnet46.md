# Playtest v4: Gruppen-Split/Merge (Sonnet 4.6)

**Datum:** 2026-03-11 12:45
**Modell:** zeitriss-v426-uncut (anthropic/claude-sonnet-4.6)
**Szenario:** 3er-Gruppe (PC + 2 NPC) → Split (Solo) → Merge (Rejoin)
**Ergebnis:** 42/42 PASS (100%), 0 FAIL

## Pruefmatrix

| #   | Check                             | Status  | Detail                                  |
| --- | --------------------------------- | ------- | --------------------------------------- |
| 1   | A-T1: Chargen-Angebot             | ✅ PASS |                                         |
| 2   | A-T2: PC-Attribute sichtbar       | ✅ PASS |                                         |
| 3   | A-T2: NPC-Begleiter erwaehnt      | ✅ PASS |                                         |
| 4   | A-T3: HUD vorhanden               | ✅ PASS |                                         |
| 5   | A-T3: Teamkontext                 | ✅ PASS |                                         |
| 6   | A-T4: Sprung beschrieben          | ✅ PASS |                                         |
| 7   | A-T5: Team agiert zusammen        | ✅ PASS |                                         |
| 8   | A-T6: Debrief                     | ✅ PASS |                                         |
| 9   | A-T6: Level/XP                    | ✅ PASS |                                         |
| 10  | A-T7: JSON vorhanden              | ✅ PASS |                                         |
| 11  | A-T7: v: 7                        | ✅ PASS |                                         |
| 12  | A-T7: characters[] Array          | ✅ PASS |                                         |
| 13  | A-T7: Mindestens 2 Charaktere     | ✅ PASS | count=2                                 |
| 14  | A-T7: save_id                     | ✅ PASS |                                         |
| 15  | A-T7: continuity.npc_roster       | ✅ PASS |                                         |
| 16  | B-T1: Recap/Rueckblick            | ✅ PASS |                                         |
| 17  | B-T1: Charaktername erkannt       | ✅ PASS |                                         |
| 18  | B-T2: HQ-Szene                    | ✅ PASS |                                         |
| 19  | B-T3: JSON vorhanden              | ✅ PASS |                                         |
| 20  | B-T3: v: 7                        | ✅ PASS |                                         |
| 21  | B-T3: Solo-Charakter erhalten     | ✅ PASS |                                         |
| 22  | B-T3: Lineage (parent_save_id)    | ✅ PASS |                                         |
| 23  | B-T3: Charakter-ID konsistent     | ✅ PASS | expected=CHR-YARA-001, got=CHR-YARA-001 |
| 24  | C-T1: Session-Anker erwaehnt      | ✅ PASS |                                         |
| 25  | C-T1: Kontinuitaetsrueckblick     | ✅ PASS |                                         |
| 26  | C-T1: Mehrere Charaktere erkannt  | ✅ PASS |                                         |
| 27  | C-T2: Mehrere Charaktere gelistet | ✅ PASS |                                         |
| 28  | C-T3: JSON vorhanden              | ✅ PASS |                                         |
| 29  | C-T3: v: 7                        | ✅ PASS |                                         |
| 30  | C-T3: characters[] Array          | ✅ PASS |                                         |
| 31  | C-T3: Alle Charaktere erhalten    | ✅ PASS | count=2                                 |
| 32  | C-T3: save_id                     | ✅ PASS |                                         |
| 33  | C-T3: parent_save_id              | ✅ PASS |                                         |
| 34  | C-T3: economy.hq_pool             | ✅ PASS |                                         |
| 35  | C-T3: arc{}                       | ✅ PASS |                                         |
| 36  | C-T3: continuity{}                | ✅ PASS |                                         |
| 37  | C-T3: summaries{}                 | ✅ PASS |                                         |
| 38  | C-T3: logs.flags                  | ✅ PASS |                                         |
| 39  | C-T3: KEIN save_version           | ✅ PASS |                                         |
| 40  | C-T3: KEIN party{}                | ✅ PASS |                                         |
| 41  | C-T3: KEIN arc_dashboard          | ✅ PASS |                                         |
| 42  | C-T3: npc_roster erhalten         | ✅ PASS |                                         |

## Phasen

### Phase 1 (Chat A)

#### Turn 1

**Spieler:** `Spiel starten (npc-team 2 klassisch)`

**KI-SL:**

# ZEITRISS

---

> _„Die Vergangenheit ist kein Museum. Sie ist ein Minenfeld."_
> — ITI-Feldhandbuch, Ausgabe 7, Seite 1

---

## EINLEITUNG

Du bist Chrononaut — Feldag ent des **Instituts für Temporale Integrität (ITI)**, stationiert in der **Nullzeit**: einem stabilen Zeitpunkt außerhalb der linearen Geschichte, von dem aus dein Team in jede Epoche springen kann.

Deine Aufgabe: **Zeitlinienstabilisierung.** Das klingt bürokratisch. Es ist Krieg.

Fraktionen kämpfen um die Kontrolle über die Vergangenheit. Artefakte tauchen an falschen Orten auf. Personen sterben zu früh oder zu spät. Und irgendwo da draußen — in einem Jahrzehnt, das noch nicht feststeht — plant jemand etwas, das alles verändert.

Das ITI schickt Teams wie deins. Kleine Gruppen. Beweglich. Deniable.

Du kommst zurück, oder du kommst nicht zurück. Beides hinterlässt Spuren.

**Willkommen im Dienst.**

---

## TEAMAUFSTELLUNG: NPC-TEAM 2 (KLASSISCH)

Zwei Chrononauten. Du führst deinen Charakter — ein NPC-Teamkollege läuft als persistenter Begleiter mit eigenem Profil, eigener Geschichte, eigenen Grenzen.

Klassischer Pfad: **18 Punkte**, Attribute STR / GES / INT / CHA / TEMP / SYS, Startwerte **1–6**, kein Wert über 6 bei Erstellung.

---

### Wie willst du deinen Charakter aufbauen?

```
Kodex: Drei Wege stehen offen.
```

**1 — `generate`**
Ich würfle und baue einen vollständigen Charakter für dich. Du bekommst einen fertigen Bogen — Attribute, Hintergrund, Loadout, NPC-Teamkollege. Direkt spielbereit.

**2 — `custom generate`**
Du gibst mir eine Richtung (Epoche, Rolle, Persönlichkeit, Stärken — so viel oder wenig wie du willst). Ich fülle die Lücken. Dein Konzept, meine Ausarbeitung.

**3 — `selbst bauen`**
Du verteilst die 18 Punkte selbst, wählst Talente und Ausrüstung. Volle Kontrolle über jeden Wert.

---

_Freie Aktion: Frag nach dem ITI, den Fraktionen, der Spielwelt — bevor es losgeht._

---

#### Turn 2

**Spieler:** `generate`

**KI-SL:**

# CHARAKTERGENERIERUNG — WÜRFLE & BAUE

```
Kodex: Zufallsprotokoll aktiv. Zwei Profile werden generiert.
```

---

## DEIN CHARAKTER

Würfelsequenz intern: 3W6-Drop-Low, normiert auf 18-Punkte-Budget, Cap 6.

**Konzept emergiert aus den Werten:** Hohe GES, solide INT, niedriger STR — das ist eine Feldagentin, die durch Räume gleitet, nicht durch Wände bricht.

---

### AGENTIN YARA VOSS

**Callsign:** STILLER SCHNITT
**Rang:** Rekrut · ITI-Ruf 0 · Lizenz Tier 0

**Herkunft:** Ostberlin, 1978. Ausgebildet als Kurierfahrerin für ein Netzwerk, das offiziell nicht existiert. Vom ITI rekrutiert nach einer Grenzüberquerung, die physikalisch nicht möglich war — und die sie trotzdem überlebt hat.

**Rolle:** Infiltration / Analyse

---

#### ATTRIBUTE (18 Punkte)

| Attribut | Wert | Funktion                                     |
| -------- | ---- | -------------------------------------------- |
| STR      | 1    | Nahkampf, Kraftakte                          |
| GES      | 6    | Fernkampf, Schleichen, Schlösser, Ausweichen |
| INT      | 4    | Technik, Hacking, Spurenanalyse              |
| CHA      | 3    | Soziales, Täuschung, Stress                  |
| TEMP     | 2    | Zeitphänomene                                |
| SYS      | 2    | Implantat-Slots                              |

**Summe: 18 ✓ · Kein Wert über 6 ✓ · Kein Wert unter 1 ✓**

---

#### TALENTE (2 Starttalente)

- **Schattenschritt** _(GES)_: +1 auf alle Schleichen-Proben in urbanen Umgebungen. Bei Erfolg hinterlässt du keine Spuren im Staub, im Schnee, auf nassem Boden.
- **Kalte Analyse** _(INT)_: Einmal pro Szene kannst du eine Spurenanalyse-Probe wiederholen. Nur der zweite Wurf zählt.

---

#### IMPLANTATE (SYS 2 → 2 Slots)

- **Retina-HUD** _(Slot 1)_: Kontaktlinsen-Interface. Karten, Vitalwerte, Kodex-Feed, Zielerkennung. Physisch unauffällig.
- **Subkutaner Jammer** _(Slot 2)_: Kurzstrecken-Signalunterdrückung (3m Radius, 90 Sekunden aktiv). Schaltet Kameras, Mikrofone, drahtlose Sensoren lokal aus. Wiederaufladezeit: 2 Szenen.

---

#### AUSRÜSTUNG / LOADOUT

| Item                              | Typ           | Tier |
| --------------------------------- | ------------- | ---- |
| Silenced Makarov PM               | Waffe         | 1    |
| Karbonmesser                      | Waffe         | 1    |
| Dietrich-Set (mechanisch)         | Gadget        | 1    |
| Feldverbandset                    | Verbrauchsgut | 1    |
| Tarnkleidung (Zivilist, 1978 Ost) | Ausrüstung    | 1    |

**Wallet:** 100 CU
**HP:** 10/10 · **Stress:** 0/8

---

#### EPOCHENFAHRZEUG

**Trabant 601 „Graue Maus"** — getarnt als Wartungsfahrzeug, Ostberlin-Kennzeichen, Hohlraum unter dem Rücksitz (Waffen/Dokumente). Langsam. Unauffällig. Zuverlässig.
_Verfügbar: alle 4 Missionen (TEMP 2)_

---

#### HINTERGRUND

Yara hat gelernt, dass Systeme Lücken haben — und dass Lücken Türen sind. Sie redet wenig. Sie beobachtet viel. Beim ITI ist sie seit drei Monaten. Sie hat noch keine Fragen gestellt, die ihr jemand beantwortet hat. Das stört sie nicht. Noch nicht.

---

---

## NPC-TEAMKOLLEGE

Sein Profil ist einfacher, härter, direkter — ein Gegengewicht zu Yaras Stille.

---

### AGENT FELIX „FELIX DER HAMMER" BRANDT

**Callsign:** HAMMER
**Rang:** Rekrut · ITI-Ruf 0 · Lizenz Tier 0
**Scope:** `session` · **Status:** `attached`

**Herkunft:** München, 1962. Ehemaliger Sicherheitsdienst-Techniker, entlassen nach einem Vorfall, der in keiner Akte steht. Physisch imposant. Emotional kontrolliert — meistens.

**Rolle:** Sicherung / Schwerer Kontakt

---

#### ATTRIBUTE (18 Punkte)

| Attribut | Wert | Funktion              |
| -------- | ---- | --------------------- |
| STR      | 6    | Nahkampf, Kraftakte   |
| GES      | 3    | Fernkampf, Ausweichen |
| INT      | 2    | Technik, Analyse      |
| CHA      | 2    | Soziales              |
| TEMP     | 1    | Zeitphänomene         |
| SYS      | 4    | Implantat-Slots       |

**Summe: 18 ✓**

---

#### TALENTE

- **Eiserne Faust** _(STR)_: +1 auf alle Nahkampf-Angriffe. Bei Treffern über SG +3: Ziel ist für 1 Runde desorientiert (−1 auf nächste Probe).
- **Deckungsinstinkt** _(GES)_: Einmal pro Szene kann Felix als Reaktion Deckung suchen, ohne eine Probe abzulegen — sofern Deckung physisch vorhanden ist.

---

#### IMPLANTATE (SYS 4 → 4 Slots)

- **Retina-HUD** _(Slot 1)_
- **Knochenstruktur-Dämpfer** _(Slot 2)_: Absorbiert Sturz- und Aufprallschaden (bis 2 LP pro Szene automatisch abgefangen).
- **Adrenalin-Injektor** _(Slot 3)_: Einmal pro Mission: +2 auf STR-Probe, sofort aktiv. Danach 1 Stress.
- **Subkutaner Panzereinsatz Brustkorb** _(Slot 4)_: Rüstungswert 1 (reduziert eingehenden Schaden um 1 LP pro Treffer).

---

#### AUSRÜSTUNG

| Item                       | Typ            | Tier |
| -------------------------- | -------------- | ---- |
| Walther P38 (modifiziert)  | Waffe          | 1    |
| Brecheisen                 | Werkzeug/Waffe | 1    |
| Handscanner (Metallortung) | Gadget         | 1    |
| Feldverbandset             | Verbrauchsgut  | 1    |

**HP:** 12/12 · **Stress:** 0/7

---

#### HINTERGRUND

Felix redet nicht über München. Er redet nicht über den Vorfall. Er redet über Sicherheitslinien, Exitrouten und ob das Schloss hier eine oder zwei Zuhaltungen hat. Er ist gut darin, Dinge zu schützen. Er ist besser darin, Dinge zu stoppen. Yara vertraut ihm. Das ist ungewöhnlich für sie.

---

---

## TEAM-ÜBERSICHT

|              | Yara Voss                          | Felix Brandt               |
| ------------ | ---------------------------------- | -------------------------- |
| **Stärke**   | GES 6 · Infiltration               | STR 6 · Sicherung          |
| **Schwäche** | STR 1 · kein Nahkampf              | INT 2 · keine Technik      |
| **Nische**   | Schleichen, Schlösser, Analyse     | Kampf, Schutz, Brute-Force |
| **Synergie** | Sie kommt rein. Er hält die Linie. |                            |

---

```
Kodex: Zwei Profile bestätigt. Teamkomposition plausibel.
Kodex: Bereit für ITI-Einweisung.
```

---

## WIE GEHT ES WEITER?

**1 — HQ-Rundgang:** Ich zeige euch das ITI — Quarzatrium, Operations-Deck, Zero Time Lounge. Ihr lernt die Anlage kennen, bevor der erste Einsatz kommt.

**2 — Direkt zum Briefing:** Commander Renier hat eine offene Akte. Erster Einsatz, erste Epoche. Wir springen.

**3 — Charakterdetails vertiefen:** Noch Fragen zu Yara, Felix, den Regeln, den Fraktionen?

**Freie Aktion:** Sag mir, was du willst — oder gib Yara eine erste Handlung im ITI.

---

#### Turn 3

**Spieler:** `Passt alles. Ab ins Briefing mit dem Team.`

**KI-SL:**

`EP 1 · MS 1 · SC 1/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/8 · Obj ??? · Exfil -`

---

# EPISODE 1 · MISSION 1

## „TOTER BRIEFKASTEN"

---

**Regie-Layer:** Yara Voss. Drei Monate im Dienst, null abgeschlossene Missionen. Commander Renier hat euer Team persönlich für diesen Einsatz angefordert — nicht weil ihr erfahren seid, sondern weil ihr _neu_ seid. Keine Akte. Keine Verbindungen. Keine Spuren, die jemand zurückverfolgen kann.

---

## ITI · OPERATIONS-DECK · NULLZEIT

Der Briefingraum riecht nach kaltem Kaffee und Ozonreiniger. Neonlicht, weiß und hart, fällt auf einen langen Tisch aus gebürstetem Stahl. An der Stirnseite: eine Projektionsfläche, darauf eingefroren ein Schwarz-Weiß-Foto. Eine Straße. Kopfsteinpflaster. Ein Briefkasten, rot lackiert, britisches Modell. Dahinter verschwimmt eine Häuserzeile im Nieselregen.

Commander Arnaud Renier steht mit dem Rücken zur Tür, als ihr eintretet. Er dreht sich nicht sofort um. Er studiert das Foto, als würde es ihm etwas schulden. Dann legt er einen Finger auf die Projektionsfläche — London, 1973, steht in der unteren Zeile — und dreht sich um.

„Setzt euch."

Kein Guten Morgen. Kein Willkommen. Renier ist ein Mann Mitte fünfzig, grauer Schläfenstreifen, Augen die aussehen als hätten sie zu viele Debriefs gesehen. Er trägt kein Abzeichen. Er braucht keines.

„Vor achtzehn Stunden hat unser Archiv eine Anomalie registriert." Er tippt. Das Foto wechselt: dieselbe Straße, aber jetzt in Farbe, jetzt mit einem Mann im Regenmantel, der an dem Briefkasten vorbeigeht ohne ihn anzusehen. „Dieser Mann heißt Edmund Falk. Chemiker. 1973 arbeitet er für ein privates Pharmaunternehmen in Southwark. Unauffällig. Unbescholten." Pause. „Bis letzte Woche — aus unserer Perspektive — nicht in einer einzigen Akte aufgetaucht."

Felix lehnt sich leicht vor. „Und jetzt?"

„Jetzt taucht er in drei auf." Renier wechselt das Bild erneut. Diesmal: ein handgeschriebenes Dokument, Frakturschrift, Datum unleserlich. Ein Laborprotokoll. „Ordo Mnemonika hat ihn kontaktiert. Wir wissen nicht wann genau, wir wissen nicht wie. Wir wissen, dass Falk in den nächsten 72 Stunden — Londonzeit, November 1973 — einen toten Briefkasten aktivieren wird. Dort liegt etwas. Was genau: unbekannt."

Er schaltet die Projektion aus. Stille.

„Ihr geht rein, identifiziert den Briefkasten, sichert den Inhalt, findet heraus was Falk mit dem Ordo zu tun hat. Festnahme wenn möglich. Keine Spuren." Er sieht Yara direkt an. „London 1973 ist kein Hochrisikofeld. Aber der Ordo ist überall wo ihr nicht hinschaut. Geht davon aus, dass ihr nicht die Einzigen seid, die Falk beobachten."

---

## INTEL / RISIKEN / ZEITFENSTER

- **Ziel:** Edmund Falk, Chemiker, ~45 Jahre, Southwark London. Briefkasten-Standort unbekannt — Falk führt euch hin.
- **Zeitfenster:** 72 Stunden Londonzeit. Absprung: Montag, 5. November 1973, 07:00 Uhr. Nieselregen. Berufsverkehr.
- **Ordo Mnemonika:** Fraktion mit Interesse an chemischen Formeln aus verschiedenen Epochen. Methoden: Social Engineering, lokale Mittelsmänner, selten direkte Gewalt.
- **Cover:** Zwei westdeutsche Handelsvertreter (Papiere fertig, Yara und Felix). Englisch Pflicht. Akzente müssen halten.
- **Noise-Risiko:** 1973 London — keine digitale Überwachung, aber Nachbarn, Pubs, Polizeistreifen. Lärm und Aufsehen sind eure Feinde.
- **Loadout-Einschränkung:** Moderne Gadgets müssen verborgen bleiben. Retina-HUD unauffällig. Jammer nur im Notfall — Signalausfall in 1973 fällt auf.

---

Renier schiebt zwei dünne Mappen über den Tisch. Deckidentitäten. Fotos, Pässe, ein Hotelname in Bermondsey.

„Fragen?"

Felix nimmt seine Mappe, schlägt sie auf, liest. Er nickt einmal, langsam. Sein Blick wandert zu Yara.

---

## OPTIONEN

**1 — Fragen stellen:** Yara hakt nach — Falk, der Ordo, der Briefkasten-Typ, was das ITI _wirklich_ weiß.

**2 — Loadout prüfen:** Ausrüstung für 1973 London durchgehen, ggf. anpassen oder ergänzen bevor ihr springt.

**3 — Absprung:** Briefing abschließen, Sprung vorbereiten. Montag, London, Regen.

**Freie Aktion:** Yara oder Felix sagen etwas — zueinander, zu Renier, oder zur Akte.

---

#### Turn 4

**Spieler:** `Wir springen. Los.`

**KI-SL:**

`EP 1 · MS 1 · SC 2/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/8 · Obj Falk beschatten · Exfil T-72:00`

---

## SPRUNG · NULLZEIT → LONDON · 05.11.1973 · 07:04

Der Hangar-Axis riecht nach Maschinenöl und verbranntem Ozon. Zwei Sprungkabinen, parallel, Stahl und Glas, innen kaum größer als ein Aufzug. Yara tritt ein. Die Tür schließt sich mit einem satten Klacken. Kein Fenster nach draußen.

Dann: Druck. Nicht von außen — von innen, als würde jede Zelle im Körper kurz vergessen wo sie hingehört. Ein Herzschlag lang ist nichts. Kein Gedanke, kein Gewicht, kein Atem.

Dann Regen.

---

## LONDON · BERMONDSEY · MONDAY MORNING

Sie materialisieren in einem Hinterhof, zwischen zwei Backsteinmauern, hinter einem Müllcontainer aus verrostetem Blech. Der Boden ist nasses Kopfsteinpflaster. Irgendwo tropft eine Regenrinne. Der Himmel über den Dächern ist der Farbe von altem Zeitungspapier — grau, gleichmäßig, ohne Kontrast.

Yara atmet aus. Kalte Luft, Kohlerauch, feuchte Wolle. Irgendwo brät jemand Speck. Eine Straße weiter: das dumpfe Grollen eines Doppeldeckerbusses, das Klingeln eines Fahrrads, gedämpfte Stimmen mit Southwark-Akzent.

`Kodex: Sprung bestätigt. 05.11.1973, 07:04 Uhr. Bermondsey, London SE1. Chronologische Drift: minimal. Comms stabil.`

Felix tritt hinter ihr aus dem Materialisierungspunkt, zieht den Kragen seines Regenmantels hoch. Er sieht sich einmal um — Mauern, Hinterhof, keine Zeugen — und nickt knapp. „Sauber." Sein Englisch ist gut. Schwerer Akzent, aber 1973 ist voll von Gastarbeitern und Handelsreisenden. Es wird halten.

Das Hotel liegt drei Minuten zu Fuß entfernt. **The Anchor Arms**, Bermondsey Street, Zimmer 14 und 15. Vorgebucht, bezahlt, unauffällig. Von dort aus: Edmund Falk.

Laut Akte wohnt Falk in einer Mietwohnung in **Walworth**, zwanzig Minuten mit dem Bus. Er arbeitet bei **Caldwell & Pryce Pharmaceuticals**, Southwark Bridge Road. Montags kommt er um 08:30 Uhr ins Büro — zu Fuß, immer dieselbe Route, Borough Market, über die Southwark Street.

Ihr habt neunzig Minuten bis er losläuft.

---

## INTEL / RISIKEN / ZEITFENSTER

- **Falk-Route (Montag):** Walworth Road → Borough Market → Southwark Street → Büro. ~35 Minuten zu Fuß.
- **Beschattung:** Belebte Straßen, Marktbetrieb im Borough Market — gute Deckung, aber auch viele Augen.
- **Ordo-Präsenz:** Unbekannt. Wenn sie Falk ebenfalls beobachten, sind sie bereits vor Ort.
- **Cover halten:** Westdeutsche Handelsvertreter. Kein Grund, in Walworth oder am Borough Market aufzufallen — solange ihr nicht zu nah dran bleibt.
- **Zeitfenster Briefkasten:** Renier sagte 72 Stunden. Wann genau Falk den Briefkasten aktiviert: unbekannt. Heute, morgen, übermorgen.

---

Die Gasse mündet auf die Bermondsey Street. Regen, dünn aber stetig. Ein Zeitungsverkäufer an der Ecke ruft Schlagzeilen, die niemand hört. Busabgase hängen in der Luft. Die Stadt ist laut und gleichgültig — genau richtig.

Felix zieht die Mütze tiefer. „Hotel zuerst, oder direkt zu seinem Block?"

Yara's HUD blinkt kurz: Falks letzte bekannte Adresse, eine Stecknadel auf dem eingeblendeten Stadtplan. Walworth, SE17. Zwölf Minuten mit dem Bus 68, der in vier Minuten an der Ecke hält.

Die Entscheidung liegt bei ihr.

---

## OPTIONEN

**1 — Hotel zuerst:** Einchecken, Ausrüstung verstauen, Cover etablieren. Dann Falk. Ihr verliert vierzig Minuten, habt aber eine saubere Basis.

**2 — Direkt zu Falks Block:** Bus 68, jetzt. Ihr seid vor ihm auf der Straße. Mehr Risiko, mehr Kontrolle über die Beschattungsposition.

**3 — Borough Market:** Falk abfangen wo er sicher auftaucht — auf seiner Route. Unauffällige Position suchen, warten, beobachten.

**Freie Aktion:** Yara entscheidet anders, oder Felix hat eine Meinung.

---

#### Turn 5

**Spieler:** `Ich schleiche vor, die NPCs sichern die Flanken. Wir naehern uns dem Zielgebaeude.`

**KI-SL:**

`EP 1 · MS 1 · SC 3/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/8 · Obj Falk lokalisieren · Exfil T-71:20`

---

## WALWORTH · SE17 · 07:31

Der Bus 68 ist halb voll. Arbeiter, eine Frau mit Einkaufskorb, zwei Schulkinder die zu spät dran sind. Yara sitzt am Fenster, Felix einen Platz dahinter, getrennt wie Fremde. Die Stadt zieht vorbei: Backsteinreihen, Eckpubs mit verwitterten Schildern, ein Zeitungsladen dessen Schaufenster mit handgeschriebenen Preisetiketten vollgeklebt ist.

Walworth Road. Sie steigen aus.

---

Falks Block ist eine vierstöckige Mietskaserne aus den Dreißigern, gelber Backstein, dunkel vom Regen. **Penrose House**, steht in verblassten Lettern über dem Eingang. Eisengitter vor den Erdgeschossfenstern. Ein schmaler Durchgang links führt in einen Innenhof — Mülltonnen, ein Fahrrad ohne Vorderrad, eine Wäscheleine mit tropfenden Hemden.

Felix bleibt an der Straßenecke, lehnt sich gegen eine Telefonzelle, zieht eine Zeitung aus dem Mantel. Natürlich. Unauffällig. Sein Blick geht zur Straße, zur Bushaltestelle, zu den Fenstern gegenüber.

Yara schlägt den Weg durch den Durchgang ein.

---

**PROBE: Schleichen**
_SG 7 — belebter Hinterhof, früher Morgen, vereinzelte Fenster mit Blick nach unten_

Wurf: W6 `[5]` + GES 6/2 `+3` + Talent Schattenschritt `+1` = **9 vs SG 7 → TREFFER**

---

Sie bewegt sich an der Mauer entlang, Schritte kurz und lautlos auf dem nassen Pflaster. Ein Fenster im zweiten Stock ist erleuchtet — Küchengeräusche, Radio, jemand macht Frühstück. Sie bleibt im Schatten des Mauerversprungs, wartet bis das Licht wechselt, geht weiter.

Der Innenhof öffnet sich. Vier Eingänge, nummeriert A bis D. Laut Akte: Falk, Eingang C, zweiter Stock. Die Tür zu C steht einen Spalt offen — jemand hat einen Stein dagegengeklemmt, wahrscheinlich wegen der klemmenden Schlossmechanik, wahrscheinlich seit Jahren.

Dann sieht sie es.

Ein Mann, Anfang dreißig, dunkler Dufflecoat, steht unter dem Dachvorsprung von Eingang B. Er raucht nicht. Er wartet nicht auf jemanden — zumindest nicht so wie jemand wartet, der jemanden erwartet. Seine Augen gehen alle zwanzig Sekunden zu Eingang C. Einmal, zweimal. Kontrolliert, aber zu regelmäßig.

`Kodex: Unbekannte Person, Eingang B. Verhaltensmarker: Beobachtungsposition. Keine Waffe sichtbar.`

Felix' Stimme, leise über Comlink: „Straßenseite sauber. Keine Bewegung bei den Fenstern. Was siehst du?"

---

## INTEL / RISIKEN

- **Unbekannter Mann bei Eingang B:** Beobachtet Eingang C — Falks Eingang. Ordo-Vorposten? Lokaler Kontaktmann? Zufälliger Anwohner? Unklar.
- **Eingang C offen:** Zugang zum Treppenhaus möglich, ohne Schloss zu knacken.
- **Falk:** Noch drin. Fenster zweiter Stock, Eingang C — Licht an, Bewegungsschatten hinter dem Vorhang.
- **Zeitfenster:** Falk bricht in ~45 Minuten auf. Wenn er den Unbekannten bemerkt — oder nicht bemerkt — ändert das seine Route möglicherweise.
- **Noise:** Innenhof ist ruhig. Jede Konfrontation hier hallt.

---

Yara steht im Schatten. Der Unbekannte dreht sich nicht um. Falk's Vorhang bewegt sich — er ist fast fertig.

---

## OPTIONEN

**1 — Unbekannten ansprechen:** Cover als verwirrte Touristin / Handelsvertreterin. Rausbringen was er hier macht — und ob er allein ist.

**2 — Unbekannten umgehen, ins Treppenhaus:** Durch Eingang C, zweiter Stock. Falk direkt vor seiner Abfahrt beobachten — oder abfangen.

**3 — Position halten, Felix informieren:** Lage weitergeben, gemeinsam entscheiden. Felix könnte den Unbekannten von der Straßenseite aus einkreisen.

**Freie Aktion:** Yara handelt anders — oder gibt Felix eine konkrete Anweisung über Comlink.

---

#### Turn 6

**Spieler:** `Ziel gesichert. Exfil, zurueck ins HQ. Debrief bitte mit Score-Screen.`

**KI-SL:**

`EP 1 · MS 1 · SC 12/12 · PHASE Debrief · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 1/10 · Px 0/5 · Stress 0/8 · Obj ABGESCHLOSSEN · Exfil VOLLZOGEN`

---

## EXFIL · BERMONDSEY · 05.11.1973 · 18:44

Der Regen hat aufgehört. Die Straßen glänzen unter den Gaslaternen, orange und nass. Yara und Felix erreichen den Materialisierungspunkt im Hinterhof — derselbe Container, dieselbe Mauer, derselbe Geruch nach feuchtem Stein.

Felix trägt eine flache Metallkassette unter dem Mantel. Gesichert. Falk ist in ITI-Gewahrsam — Kausalabfang vollzogen, sauber, kein Aufsehen. Der Unbekannte vom Innenhof: identifiziert als Ordo-Vorposten, neutralisiert.

`Kodex: Sprungfenster offen. Rückkehrvektor stabil.`

Yara tritt in die Kabine. Druck. Ein Herzschlag lang nichts.

Dann: Ozongeruch. Stahl. Die Nullzeit.

---

## ITI · HANGAR-AXIS · ANKUNFT

Commander Renier wartet nicht im Hangar. Archivarin Mira tut es — sie steht mit einem Klemmbrett an der Schleuse, nimmt die Kassette entgegen, nickt einmal. „Debrief in zwanzig Minuten. Dusche zuerst."

Felix setzt sich auf eine Werkzeugkiste und zieht den Mantel aus. Auf seinem Unterarm: ein langer Schnitt, bereits verkrustet, den er während der Mission nicht erwähnt hat.

„War nicht schlimm", sagt er, bevor Yara etwas sagen kann.

---

# DEBRIEF · SCORE-SCREEN

```
╔══════════════════════════════════════════════════════════╗
║           ZEITRISS · ITI · MISSIONSBERICHT               ║
║           EP 01 · MS 01 · „TOTER BRIEFKASTEN"            ║
╠══════════════════════════════════════════════════════════╣
║  BEWERTUNG                                               ║
║  ─────────────────────────────────────────────────────   ║
║  Primärziel        Briefkasten-Inhalt gesichert   ✓      ║
║  Sekundärziel      Falk identifiziert & abgefangen ✓     ║
║  Ordo-Kontakt      Vorposten neutralisiert         ✓     ║
║  Deckung           Cover gehalten, keine Zeugen   ✓      ║
║  Noise/Heat        Minimal                        ✓      ║
║  Verluste          Felix: leichte Schnittwunde    ~      ║
║                                                          ║
║  GESAMTBEWERTUNG:  ██████████░  SILBER             87/100║
╠══════════════════════════════════════════════════════════╣
║  LOOT                                                    ║
║  ─────────────────────────────────────────────────────   ║
║  Metallkassette „Falk-Protokoll"                         ║
║    → Chemische Formel, Epoche unbekannt (Archiv-Flag)    ║
║    → 3 handgeschriebene Kontaktnamen (Ordo-Netz)         ║
║  Ordo-Vorposten: Codebuch (1973-Chiffre) ⚠ heißes Loot  ║
║  Bargeld: 40 GBP (≈ 18 CU Tauschwert)                   ║
╠══════════════════════════════════════════════════════════╣
║  CU-ABRECHNUNG                                           ║
║  ─────────────────────────────────────────────────────   ║
║  Basishonorar Mission 1                    + 120 CU      ║
║  Bonus: Sekundärziel erfüllt               +  40 CU      ║
║  Bonus: Keine zivilen Zwischenfälle        +  20 CU      ║
║  Abzug: Materialverbrauch / Deckkosten     −  15 CU      ║
║  Loot-Verkauf (Bargeld)                    +  18 CU      ║
║  ─────────────────────────────────────────────────────   ║
║  AUSZAHLUNG GESAMT                         + 183 CU      ║
║  Wallet Yara Voss: 100 + 183 = 283 CU                   ║
╠══════════════════════════════════════════════════════════╣
║  ERFAHRUNG & ENTWICKLUNG                                 ║
║  ─────────────────────────────────────────────────────   ║
║  XP verdient: +1                                         ║
║  Lvl 1 → Lvl 2  ██████████  AUFSTIEG!                   ║
║                                                          ║
║  LEVEL-UP-WAHL (genau eine):                             ║
║  A) +1 Attribut (STR / GES / INT / CHA / TEMP / SYS)    ║
║  B) Neues Talent oder Upgrade                            ║
║  C) +1 SYS (Implantat-Slot)                             ║
╠══════════════════════════════════════════════════════════╣
║  ITI-RUF & LIZENZ                                        ║
║  ─────────────────────────────────────────────────────   ║
║  Rang: Rekrut · ITI-Ruf 0 → +1 · ITI-Ruf 1             ║
║  Lizenz Tier 0 → Tier I freigeschaltet!                  ║
║  Rang Rekrut → FELDAGENT                                 ║
╠══════════════════════════════════════════════════════════╣
║  PARADOXON-INDEX                                         ║
║  ─────────────────────────────────────────────────────   ║
║  Px: 0/5  (TEMP 2 → +1 alle 2 Missionen)                ║
║  Nächster Px-Anstieg: Mission 3                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## ITI-RUF UPDATE

`Rang Feldagent · ITI-Ruf 1 · Lizenz Tier I freigeschaltet!`

Lizenz Tier I öffnet: **Shop-Zugang Tier-2-Ausrüstung**, **Klinik-Rabatt 10%**, **Archiv-Anfragen (1 pro Mission)**.

---

## RENIER · BRIEFINGRAUM · NACHHER

Renier liest den Bericht, während ihr noch sitzt. Er legt ihn hin, ohne aufzublicken.

„Das Falk-Protokoll geht ins Archiv. Die Kontaktnamen werden ausgewertet." Eine kurze Pause. „Ihr habt sauber gearbeitet." Das ist, bei Renier, ungefähr das Äquivalent einer Umarmung.

Er schiebt einen Umschlag über den Tisch. Lizenzabzeichen, Tier I. Zwei Stück.

„Ruht euch aus. Nächste Akte liegt morgen früh auf dem Deck."

---

## ITI-BULLETIN

_Aus dem Operations-Deck, eingehend 21:17 Nullzeit:_
**Team VOSS/BRANDT — Erstkontakt Ordo-Netz bestätigt. Archiv klassifiziert Falk-Protokoll als Priorität 2. Codebuch zur Kryptoabteilung weitergeleitet. Drei Kontaktnamen in Auswertung — früheste Ergebnisse in 48 Stunden Nullzeit. Weitere Ordo-Aktivität in Epoche 1960–1980 nicht auszuschließen.**

---

## WELTSTATUS

Die drei Kontaktnamen aus dem Falk-Protokoll deuten auf ein Ordo-Netz hin, das sich über mindestens zwei Epochen erstreckt. Solange die Auswertung läuft, operiert der Ordo blind — aber nicht lange.

---

## HQ · NÄCHSTE SCHRITTE

Ihr seid zurück. Felix lässt sich in der Klinik die Schnittwunde versorgen — drei Stiche, kein Drama. Die Nullzeit ist ruhig, gleichmäßig beleuchtet, nach nichts riechend außer Ozonreiniger und Kaffee.

**Wähle deinen Level-Up (Pflicht vor dem nächsten Briefing):**

**1 — +1 Attribut:** Welches? (STR / GES / INT / CHA / TEMP / SYS)

**2 — Neues Talent:** Ich schlage drei passende Optionen vor, du wählst.

**3 — +1 SYS:** Ein weiterer Implantat-Slot. Sofort nutzbar im nächsten Shop-Besuch.

**Freie Aktion:** HQ erkunden, Shop besuchen, mit Felix oder Mira reden — oder direkt `!save` für den Spielstand.

---

#### Turn 7

**Spieler:** `!save`

**KI-SL:**

`Kodex: HQ-Save initiiert. Debrief-Reset läuft.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-03-08T21:30:00Z-HQ-EP1-MS1",
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
      "id": "CHR-YARA-001",
      "name": "Yara Voss",
      "callsign": "STILLER SCHNITT",
      "rank": "Feldagent",
      "lvl": 2,
      "xp": 1,
      "origin": {
        "epoch": "Ostberlin, 1978",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration / Analyse"
      },
      "attr": { "STR": 1, "GES": 6, "INT": 4, "CHA": 3, "TEMP": 2, "SYS": 2 },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 2,
      "levelup_pending": true,
      "talents": [
        {
          "name": "Schattenschritt",
          "linked": "GES",
          "effect": "+1 Schleichen urban; keine Spuren bei Erfolg"
        },
        {
          "name": "Kalte Analyse",
          "linked": "INT",
          "effect": "1x/Szene Spurenanalyse-Probe wiederholen"
        }
      ],
      "equipment": [
        { "name": "Silenced Makarov PM", "type": "weapon", "tier": 1 },
        { "name": "Karbonmesser", "type": "weapon", "tier": 1 },
        { "name": "Dietrich-Set (mechanisch)", "type": "gadget", "tier": 1 },
        { "name": "Feldverbandset", "type": "consumable", "tier": 1 },
        { "name": "Tarnkleidung (Zivilist, 1978 Ost)", "type": "armor", "tier": 1 }
      ],
      "implants": [
        {
          "name": "Retina-HUD",
          "slot": 1,
          "effect": "Karten, Vitalwerte, Kodex-Feed, Zielerkennung"
        },
        {
          "name": "Subkutaner Jammer",
          "slot": 2,
          "effect": "3m Signalunterdrückung, 90s aktiv, Aufladezeit 2 Szenen"
        }
      ],
      "history": {
        "background": "Kurierfahrerin Ostberlin 1978, rekrutiert nach physikalisch unmöglicher Grenzüberquerung. Drei Monate ITI-Dienst.",
        "milestones": [
          "EP1/MS1: Falk-Protokoll gesichert, Ordo-Vorposten neutralisiert, Kausalabfang vollzogen. Silber-Bewertung 87/100."
        ]
      },
      "carry": [
        {
          "name": "Ordo-Codebuch (1973-Chiffre)",
          "type": "gadget",
          "tier": 1,
          "note": "heißes Loot — Kryptoabteilung"
        }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-YARA-001",
          "name": "Trabant 601 'Graue Maus'",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": { "ready_every_missions": 4, "next_ready_in": 3 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 283
    },
    {
      "id": "CHR-FELIX-001",
      "name": "Felix Brandt",
      "callsign": "HAMMER",
      "rank": "Feldagent",
      "lvl": 2,
      "xp": 1,
      "origin": {
        "epoch": "München, 1962",
        "hominin": "Homo sapiens sapiens",
        "role": "Sicherung / Schwerer Kontakt"
      },
      "attr": { "STR": 6, "GES": 3, "INT": 2, "CHA": 2, "TEMP": 1, "SYS": 4 },
      "hp": 12,
      "hp_max": 12,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 4,
      "levelup_pending": true,
      "talents": [
        {
          "name": "Eiserne Faust",
          "linked": "STR",
          "effect": "+1 Nahkampf; bei Treffer SG+3: Ziel desorientiert 1 Runde"
        },
        {
          "name": "Deckungsinstinkt",
          "linked": "GES",
          "effect": "1x/Szene Deckung ohne Probe, sofern physisch vorhanden"
        }
      ],
      "equipment": [
        { "name": "Walther P38 (modifiziert)", "type": "weapon", "tier": 1 },
        { "name": "Brecheisen", "type": "weapon", "tier": 1 },
        { "name": "Handscanner (Metallortung)", "type": "gadget", "tier": 1 },
        { "name": "Feldverbandset", "type": "consumable", "tier": 1 }
      ],
      "implants": [
        {
          "name": "Retina-HUD",
          "slot": 1,
          "effect": "Karten, Vitalwerte, Kodex-Feed, Zielerkennung"
        },
        {
          "name": "Knochenstruktur-Dämpfer",
          "slot": 2,
          "effect": "Bis 2 LP Sturz-/Aufprallschaden automatisch abgefangen/Szene"
        },
        {
          "name": "Adrenalin-Injektor",
          "slot": 3,
          "effect": "1x/Mission: +2 STR-Probe, danach Stress +1"
        },
        {
          "name": "Subkutaner Panzereinsatz Brustkorb",
          "slot": 4,
          "effect": "Rüstung 1: eingehender Schaden −1 LP/Treffer"
        }
      ],
      "history": {
        "background": "Ehemaliger Sicherheitsdienst-Techniker München 1962, entlassen nach nicht aktenkundigem Vorfall. Redet nicht darüber.",
        "milestones": [
          "EP1/MS1: Ordo-Vorposten gesichert, leichte Schnittwunde (versorgt). Silber-Bewertung 87/100."
        ]
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-FELIX-001",
          "name": "BMW R75/5 'Grauer Wolf'",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": { "ready_every_missions": 4, "next_ready_in": 3 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": null,
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 283
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [
      "EP1/MS1: Falk-Protokoll gesichert (Chemische Formel + 3 Ordo-Kontaktnamen). Ordo-Vorposten Kausalabfang vollzogen. Codebuch an Kryptoabteilung.",
      "EP1/MS1: Silber 87/100. Auszahlung 183 CU. ITI-Ruf +1. Lizenz Tier I freigeschaltet."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Falk-Protokoll: Archiv-Flag Priorität 2. 3 Kontaktnamen in Auswertung (48h Nullzeit).",
      "Ordo-Aktivität Epoche 1960–1980 nicht auszuschließen.",
      "Felix: Schnittwunde versorgt, 3 Stiche, einsatzbereit.",
      "Level-Up Yara: ausstehend. Level-Up Felix (NPC): ausstehend."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": "Ordo Mnemonika operiert in Epoche 1960–1980. Falk-Protokoll gesichert. 3 Kontaktnamen in Auswertung. Netz-Ausdehnung unklar."
  },
  "continuity": {
    "last_seen": { "mode": "core", "episode": 1, "mission": 1, "location": "HQ" },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      {
        "id": "NPC-RENIER-001",
        "name": "Commander Arnaud Renier",
        "note": "Lobte saubere Arbeit. Nächste Akte morgen früh."
      },
      {
        "id": "NPC-MIRA-001",
        "name": "Archivarin Mira",
        "note": "Übernahm Kassette persönlich. Falk-Protokoll Priorität 2."
      }
    ],
    "shared_echoes": [
      {
        "echo": "Falk-Protokoll: 3 Ordo-Kontaktnamen — Auswertung läuft, Folgemission wahrscheinlich."
      }
    ],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "CHR-FELIX-001",
        "name": "Felix Brandt",
        "callsign": "HAMMER",
        "role": "Sicherung / Schwerer Kontakt",
        "trait": "Redet nicht über München",
        "scope": "session",
        "owner_id": "CHR-YARA-001",
        "bond": "Yara vertraut ihm — ungewöhnlich für sie",
        "status": "attached",
        "last_seen": "HQ Klinik",
        "offscreen": "Schnittwunde versorgt, einsatzbereit",
        "hook": "Was war der Vorfall in München?"
      }
    ],
    "active_npc_ids": ["CHR-FELIX-001"]
  },
  "arc": {
    "factions": {
      "ordo_mnemonika": "Aktiv Epoche 1960–1980. Falk als Kontaktperson genutzt. Netz teilweise enttarnt."
    },
    "questions": [
      "Was enthält das Falk-Protokoll genau — und aus welcher Epoche stammt die Formel?",
      "Wer sind die drei Ordo-Kontaktnamen?",
      "Was war der Vorfall in München, der Felix seinen Job kostete?"
    ],
    "hooks": [
      "Kryptoabteilung wertet Ordo-Codebuch aus — Ergebnisse in 48h Nullzeit.",
      "Ordo-Netz erstreckt sich über mindestens zwei Epochen.",
      "Renier: Nächste Akte liegt morgen früh auf dem Deck."
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  }
}
```

---

`Kodex: Save gesichert. SAVE-2026-03-08T21:30:00Z-HQ-EP1-MS1. Alle Felder bestätigt.`

---

**Noch offen vor dem nächsten Briefing:**

`⚠ Level-Up Yara Voss: Wahl ausstehend — A) +1 Attribut · B) Talent/Upgrade · C) +1 SYS`

---

### Phase 2 (Chat B)

#### Turn 1

**Spieler:** `Spiel laden

````json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-03-08T21:30:00Z-HQ-EP1-MS1-SPLIT-SOLO",
  "parent_save_id": "SAVE-2026-03-08T21:30:00Z-HQ-EP1-MS1",
  "merge_id": null,
  "bra`

**KI-SL:**

# ZEITRISS — Session geladen

---

**Kontinuitätsrückblick · EP1 / Nach Mission 1**

Session-Anker: **Yara Voss "STILLER SCHNITT"** · Solo-Branch · ITI-Ruf 1 · Lizenz Tier I

**Letzte bekannte Lage:** Das Falk-Protokoll ist gesichert — chemische Formel, drei Ordo-Kontaktnamen, Codebuch in der Kryptoabteilung. Archivarin Mira hat die Kassette persönlich übernommen. Commander Renier lobte die saubere Arbeit und kündigte die nächste Akte für morgen früh an. Felix Brandt sitzt in der Klinik, drei Stiche in der Schulter, einsatzbereit.

**NPC-Lagebild:** Felix "HAMMER" Brandt — attached, HQ-Klinik. Schnittwunde versorgt.

**Offene Nachwirkungen:** Drei Ordo-Kontaktnamen in Auswertung (48h Nullzeit). Das Codebuch läuft durch die Kryptoabteilung. Ordo Mnemonika operiert in mindestens zwei Epochen — das Netz ist größer als der Vorposten vermuten ließ.

⚠️ **Level-Up ausstehend** — Yara wartet noch auf ihre Wahl.

---

`Kodex: Session-Anker geladen. Charakterstand stabil. Level-Up-Auswahl steht aus.`

---

## ITI-Hauptquartier · Nullzeit · Früh

Das Quarzatrium liegt still. Die Nullzeit hat keine Uhr, aber der Rhythmus des ITI hat seinen eigenen Puls — und dieser Puls sagt: kurz nach dem Schichtwechsel. Das Licht der Deckenleuchten ist kalt und gleichmäßig, keine Schatten, keine Jahreszeit. Irgendwo im Hangar-Axis läuft eine Wartungssequenz, das leise Surren der Diagnostik kriecht durch die Wände.

Du sitzt in deinen Quartieren. Die Tarnkleidung hängt über dem Stuhl, noch nach Ostberlin riechend — Kohlestaub, billiges Waschmittel, Herbstregen. Der Makarov liegt auf dem Tisch, gereinigt, geladen. Dein Körper weiß, dass die Mission vorbei ist. Dein Kopf hat das noch nicht ganz verarbeitet.

Das HUD flackert leise in deinem Sichtfeld — ein einzelner Hinweis, seit du aufgewacht bist:

`⬆ LEVEL-UP AUSSTEHEND · Yara Voss · Lvl 2 → 3`

---

**ITI-Bulletin:** Aus dem Operations-Deck kommt eine knappe interne Meldung — Team "Grauer Falke" ist drei Stunden überfällig aus einer Routinesondierung, Epoche 1943, Nordafrika. Keine Panik, aber Renier hat persönlich Stellung bezogen. Das ITI arbeitet.

**Weltstatus:** Die Kryptoabteilung hat erste Vorarbeit am Ordo-Codebuch geleistet — die Chiffre ist älter als 1973. Deutlich älter. Woher ein Ostberliner Vorposten an eine Verschlüsselung aus dem frühen 20. Jahrhundert gekommen ist, steht noch offen. Das Ordo-Netz reicht tiefer in die Zeit als der erste Einsatz vermuten ließ.

---

### ⬆ Level-Up: Yara Voss · Lvl 2 → 3

Wähle **genau eine** Option:

> **A) +1 Attribut**
> Erhöhe einen Attributswert um 1.
> *(Aktuell: STR 1 · GES 6 · INT 4 · CHA 3 · TEMP 2 · SYS 2)*

> **B) Talent / Upgrade**
> Lerne eine neue Fähigkeit oder verbessere ein bestehendes Talent.
> *(Vorschläge auf Anfrage — oder freie Wahl)*

> **C) +1 SYS**
> Einen weiteren Implantat-Slot freischalten.
> *(Aktuell: SYS 2, 2 Slots belegt)*

---

`EP 1 · MS 1 · HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 1/10 · Px 0/5 · Stress 0/10`

---

**Nach dem Level-Up:** HQ-Menü, Klinik (Felix), Briefing-Deck oder freie Aktion.

---

#### Turn 2

**Spieler:** `Ich erkunde das HQ alleine. Was gibt es Neues?`

**KI-SL:**

`EP 1 · MS 1 · HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 1/10 · Px 0/5 · Stress 0/10`

---

⚠️ **Level-Up noch ausstehend** — das HUD erinnert dich still. Kein Druck, aber der Kodex hat es markiert. Du kannst jederzeit entscheiden.

---

## ITI-Hauptquartier · Erkundung · Nullzeit

Du ziehst die Jacke über und verlässt die Quartiere. Der Gang ist schmal, Beton und Glas, die Türen anderer Agenten geschlossen. Irgendwo hinter einer davon schläft jemand, irgendwo hinter einer anderen schläft niemand.

---

### Quarzatrium

Der zentrale Knotenpunkt des ITI ist nie ganz leer. Zwei Agenten, die du nicht kennst, sitzen an einem Tisch mit Kaffee und Karten — echten Spielkarten, abgegriffen, aus irgendeiner Epoche mitgebracht. Sie nicken dir zu. Nicht freundlich, nicht unfreundlich. Kollegiales Schweigen.

An der Nordwand hängt die **Einsatztafel** — ein analoges Relikt, das Commander Renier aus sentimentalen Gründen behalten hat, neben dem digitalen Overlay. Drei Pins stecken in der Karte:

- **Nordafrika, 1943** — roter Pin. Team Grauer Falke. Überfällig.
- **Wien, 1961** — gelber Pin. Neue Markierung, seit gestern Nullzeit. Kein Team zugewiesen.
- **Unbekannte Koordinaten** — weißer Pin, kein Datum, kein Label. Jemand hat ihn heute Nacht gesteckt.

Der weiße Pin ist neu. Du bist sicher, dass er gestern noch nicht da war.

---

### Kodex-Archiv

Die Tür steht einen Spalt offen. Archivarin Mira sitzt an ihrem Tisch, umgeben von drei Bildschirmen und einem Stapel Mikrofilm-Kassetten — echter Mikrofilm, aus der Epoche. Sie schaut auf, als du eintrittst.

*„Voss."* Kurz. Kein Lächeln, aber auch keine Kälte. *„Das Codebuch macht mir Kopfzerbrechen. Die Chiffre ist nicht 1973. Ich habe sie auf frühestens 1908 datiert — Wiener Schule, erkennbar an der Schlüsselstruktur. Wie ein Ostberliner Vorposten 1978 an ein Dokument aus dem frühen 20. Jahrhundert kommt..."* Sie lässt den Satz offen. Tippt etwas. *„Die drei Kontaktnamen laufen noch. Einer davon ist interessant. Mehr sage ich erst, wenn ich sicher bin."*

Sie dreht sich wieder zum Bildschirm. Audienz beendet.

---

### Med-Lab

Felix sitzt auf einer Behandlungsliege und liest — eine zerlesene Taschenbuchausgabe, Rücken gebrochen, Titel nicht erkennbar. Die Schulter ist frisch verbunden, der Arm in einer leichten Schiene. Er klappt das Buch zu, als du reinkommst.

*„Schläfst du nie?"*

Er sieht besser aus als gestern. Der Schmerz ist noch da, liegt hinter den Augen, aber er hält ihn gut. Er fragt nicht nach dem Nächsten. Er fragt auch nicht nach München — und du fragst nicht.

*„Mira hat mich heute Morgen angerufen,"* sagt er nach einer Pause. *„Wegen dem Codebuch. Sie wollte wissen, ob ich bei der Übergabe etwas Ungewöhnliches bemerkt habe."* Er zieht eine Augenbraue hoch. *„Hab ihr gesagt: alles war ungewöhnlich."*

---

### Hangar-Axis

Der Hangar riecht nach Maschinenöl und kaltem Metall. Zwei Techniker arbeiten an einem Sprungmodul — Schweißfunken, gedämpfte Flüche. Dein **Trabant 601** steht in Bucht 7, sauber geparkt, mit einem kleinen ITI-Wartungsaufkleber an der Windschutzscheibe.

`Kodex: Epoch-Vehicle 'Graue Maus' — Verfügbarkeit in 3 Missionen.`

An der Wand neben deiner Bucht hängt ein handgeschriebener Zettel, mit Klebeband befestigt:

> *Wer hat Bucht 12 ohne Anmeldung genutzt? Bitte melden. — Wartung*

Bucht 12 ist leer. Kein Fahrzeug, keine Ausrüstung, kein Hinweis. Aber der Boden ist frisch gewischt — und in der Ecke liegt ein einzelner Knopf. Schwarz, klein, aus schwerem Stoff. Osteuropäische Fertigung, schätzt du. Nicht von einem ITI-Overall.

---

### Zero Time Lounge

Leer bis auf eine Person: eine Agentin, die du noch nie gesehen hast. Kurze Haare, dunkle Haut, eine Narbe quer über das Kinn. Sie sitzt mit dem Rücken zur Wand und trinkt etwas Heißes. Ihr Blick geht zur Tür, als du eintrittst — automatisch, professionell. Dann zurück zu ihrem Becher.

Kein Namensschild. Kein Callsign-Patch. Neu — oder sie will nicht erkannt werden.

---

**Intel-Zusammenfassung:**

- Weißer Pin an der Einsatztafel — unbekannte Koordinaten, kein Datum, heute Nacht gesteckt
- Mira: Codebuch-Chiffre aus ~1908, Wiener Schule — ein Kontaktname ist *interessant*
- Bucht 12 genutzt ohne Anmeldung — Knopf osteuropäischer Fertigung gefunden
- Unbekannte Agentin in der Lounge — kein Patch, kein Name
- Wien 1961 — neuer gelber Pin, kein Team

---

**Was tust du?**

1. **Mira konfrontieren** — Du willst den einen interessanten Kontaktnamen jetzt. Nicht morgen.
2. **Weißen Pin untersuchen** — Zurück zur Einsatztafel. Wer hat ihn gesteckt, und warum ohne Label?
3. **Unbekannte Agentin ansprechen** — Zero Time Lounge. Wer ist sie, und was macht sie hier ohne Patch?
4. **Freie Aktion** — Bucht 12, Felix, Operations-Deck, oder etwas anderes.

---

#### Turn 3

**Spieler:** `!save`

**KI-SL:**

`Kodex: HQ-Save initiiert. Charakterstand und Kontinuität werden gesichert.`

⚠️ **Level-Up noch nicht abgeschlossen** — wird im Save als `levelup_pending: true` markiert.

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-03-08T22:00:00Z-HQ-EP1-MS1-ERKUNDEN",
  "parent_save_id": "SAVE-2026-03-08T21:30:00Z-HQ-EP1-MS1-SPLIT-SOLO",
  "merge_id": null,
  "branch_id": "BRANCH-solo-split",
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
      "id": "CHR-YARA-001",
      "name": "Yara Voss",
      "callsign": "STILLER SCHNITT",
      "rank": "Feldagent",
      "lvl": 2,
      "xp": 1,
      "origin": {
        "epoch": "Ostberlin, 1978",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration / Analyse"
      },
      "attr": {
        "STR": 1,
        "GES": 6,
        "INT": 4,
        "CHA": 3,
        "TEMP": 2,
        "SYS": 2
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 2,
      "levelup_pending": true,
      "talents": [
        {
          "name": "Schattenschritt",
          "linked": "GES",
          "effect": "+1 Schleichen urban; keine Spuren bei Erfolg"
        },
        {
          "name": "Kalte Analyse",
          "linked": "INT",
          "effect": "1x/Szene Spurenanalyse-Probe wiederholen"
        }
      ],
      "equipment": [
        {
          "name": "Silenced Makarov PM",
          "type": "weapon",
          "tier": 1
        },
        {
          "name": "Karbonmesser",
          "type": "weapon",
          "tier": 1
        },
        {
          "name": "Dietrich-Set (mechanisch)",
          "type": "gadget",
          "tier": 1
        },
        {
          "name": "Feldverbandset",
          "type": "consumable",
          "tier": 1
        },
        {
          "name": "Tarnkleidung (Zivilist, 1978 Ost)",
          "type": "armor",
          "tier": 1
        }
      ],
      "implants": [
        {
          "name": "Retina-HUD",
          "slot": 1,
          "effect": "Karten, Vitalwerte, Kodex-Feed, Zielerkennung"
        },
        {
          "name": "Subkutaner Jammer",
          "slot": 2,
          "effect": "3m Signalunterdrückung, 90s aktiv, Aufladezeit 2 Szenen"
        }
      ],
      "history": {
        "background": "Kurierfahrerin Ostberlin 1978, rekrutiert nach physikalisch unmöglicher Grenzüberquerung. Drei Monate ITI-Dienst.",
        "milestones": [
          "EP1/MS1: Falk-Protokoll gesichert, Ordo-Vorposten neutralisiert, Kausalabfang vollzogen. Silber-Bewertung 87/100.",
          "EP1/HQ: HQ-Erkundung. Weißer Pin (unbekannte Koordinaten), Bucht-12-Anomalie, Codebuch-Chiffre ~1908 Wiener Schule, unbekannte Agentin in der Lounge."
        ]
      },
      "carry": [
        {
          "name": "Ordo-Codebuch (1973-Chiffre)",
          "type": "gadget",
          "tier": 1,
          "note": "heißes Loot — Kryptoabteilung; Chiffre tatsächlich ~1908, Wiener Schule"
        }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-YARA-001",
          "name": "Trabant 601 'Graue Maus'",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 4,
          "next_ready_in": 3
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 283
    }
  ],
  "economy": {
    "hq_pool": 0
  },
  "logs": {
    "trace": [
      "EP1/MS1: Falk-Protokoll gesichert (Chemische Formel + 3 Ordo-Kontaktnamen). Ordo-Vorposten Kausalabfang vollzogen. Codebuch an Kryptoabteilung.",
      "EP1/MS1: Silber 87/100. Auszahlung 183 CU. ITI-Ruf +1. Lizenz Tier I freigeschaltet.",
      "EP1/HQ: Weißer Pin Einsatztafel — unbekannte Koordinaten, kein Datum, über Nacht gesteckt.",
      "EP1/HQ: Bucht 12 genutzt ohne Anmeldung. Boden frisch gewischt. Knopf osteuropäischer Fertigung gefunden.",
      "EP1/HQ: Mira — Codebuch-Chiffre auf ~1908 datiert, Wiener Schule. Ein Kontaktname 'interessant', noch nicht freigegeben.",
      "EP1/HQ: Unbekannte Agentin, Zero Time Lounge. Kein Patch, kein Callsign. Neu oder verdeckt."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Falk-Protokoll: Archiv-Flag Priorität 2. 3 Kontaktnamen in Auswertung (48h Nullzeit).",
      "Ordo-Aktivität Epoche 1960–1980 nicht auszuschließen.",
      "Felix: Schnittwunde versorgt, 3 Stiche, einsatzbereit.",
      "Level-Up Yara: ausstehend.",
      "Wiener Pin (weiß): Wer hat ihn gesteckt? Koordinaten unbekannt.",
      "Bucht-12-Knopf: osteuropäisch, schwerer Stoff — mögliche Verbindung zu Ordo-Netz?"
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": "Ordo Mnemonika operiert in Epoche 1960–1980 und möglicherweise früher (Chiffre ~1908, Wiener Schule). Falk-Protokoll gesichert. 3 Kontaktnamen in Auswertung. Weißer Pin, Bucht-12-Anomalie und unbekannte Agentin als offene HQ-Fäden."
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 1,
      "location": "HQ"
    },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      {
        "id": "NPC-RENIER-001",
        "name": "Commander Arnaud Renier",
        "note": "Lobte saubere Arbeit. Persönlich am Deck wegen Team Grauer Falke (überfällig, Nordafrika 1943)."
      },
      {
        "id": "NPC-MIRA-001",
        "name": "Archivarin Mira",
        "note": "Codebuch-Chiffre ~1908 Wiener Schule. Ein Kontaktname interessant — hält Infos zurück bis zur Bestätigung."
      }
    ],
    "shared_echoes": [
      {
        "echo": "Falk-Protokoll: 3 Ordo-Kontaktnamen — Auswertung läuft, Folgemission wahrscheinlich."
      },
      {
        "echo": "Codebuch-Chiffre älter als erwartet (~1908). Ordo-Netz reicht tiefer in die Zeit."
      },
      {
        "echo": "Weißer Pin Einsatztafel: unbekannte Koordinaten, kein Label, heute Nacht gesteckt — unbekannte Hand."
      }
    ],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "CHR-FELIX-001",
        "name": "Felix Brandt",
        "callsign": "HAMMER",
        "role": "Sicherung / Schwerer Kontakt",
        "trait": "Redet nicht über München",
        "scope": "session",
        "owner_id": "CHR-YARA-001",
        "bond": "Yara vertraut ihm — ungewöhnlich für sie",
        "status": "attached",
        "last_seen": "HQ Med-Lab",
        "offscreen": "Schnittwunde versorgt, Arm in Schiene, liest. Mira hat ihn wegen Codebuch-Übergabe befragt.",
        "hook": "Was war der Vorfall in München? Mira hat ihn kontaktiert — warum?"
      }
    ],
    "active_npc_ids": [
      "CHR-FELIX-001"
    ]
  },
  "arc": {
    "factions": {
      "ordo_mnemonika": "Aktiv Epoche 1960–1980 und möglicherweise früher (~1908). Falk als Kontaktperson genutzt. Netz teilweise enttarnt. Chiffre Wiener Schule deutet auf historische Verwurzelung."
    },
    "questions": [
      "Was enthält das Falk-Protokoll genau — und aus welcher Epoche stammt die Formel?",
      "Wer sind die drei Ordo-Kontaktnamen — und welcher ist 'interessant'?",
      "Was war der Vorfall in München, der Felix seinen Job kostete?",
      "Wer hat den weißen Pin gesteckt — und was bezeichnen die unbekannten Koordinaten?",
      "Wer ist die unbekannte Agentin in der Zero Time Lounge?"
    ],
    "hooks": [
      "Kryptoabteilung wertet Ordo-Codebuch aus — Chiffre ~1908 Wiener Schule.",
      "Ordo-Netz erstreckt sich über mindestens zwei Epochen, möglicherweise bis ins frühe 20. Jhd.",
      "Renier: Nächste Akte liegt morgen früh auf dem Deck.",
      "Wien 1961 — neuer gelber Pin, kein Team zugewiesen.",
      "Bucht 12: genutzt ohne Anmeldung, Knopf osteuropäischer Fertigung — wer war das?",
      "Unbekannte Agentin ohne Patch in der Lounge — Neu-Rekrut oder verdeckte Operation?"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  }
}
````

---

`Kodex: Save gesichert. SAVE-2026-03-08T22:00:00Z-HQ-EP1-MS1-ERKUNDEN. Bereit.`

---

### Phase 3 (Chat C)

#### Turn 1

**Spieler:** `Spiel laden

````json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-03-08T21:30:00Z-HQ-EP1-MS1",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "`

**KI-SL:**

# ZEITRISS — Session Load

---

**Saves erkannt:** 2 Blöcke. Session-Anker wird gesetzt.

**Merge-Analyse:**
- `ANCHOR-main` (EP1/MS1, Gruppe Yara + Felix) → Session-Anker
- `BRANCH-solo-split` (EP1/HQ, Yara solo, HQ-Erkundung) → Branch-Import

Beide tragen `CHR-YARA-001`. Branch-Stand ist jünger (`22:00Z` vs `21:30Z`) und enthält Yara's HQ-Erkundungsergebnisse sowie erweiterte Milestones. **Yara's persönlicher Stand aus dem Branch-Import gewinnt** (neuerer Zeitstempel, Branch-lokale Fortschritte via Allowlist). Felix läuft weiter aus dem Anker-Save.

`duplicate_branch_detected: false` — kein Konflikt, sauberer Import.

---

## Kontinuitätsrückblick

`Kodex: Session-Anker gesetzt. Zwei Saves gemergt. Yara-Stand Branch-Import aktiv. Felix-Stand Anker aktiv.`

**Wo ihr steht:**

Erste Mission abgeschlossen. Das Falk-Protokoll liegt in Miras Archiv — chemische Formel, drei Ordo-Kontaktnamen, alle in Auswertung. Die Bewertung: Silber, 87 Punkte. Sauber genug, um nicht aufzufallen. Nicht sauber genug, um gut zu schlafen.

Felix sitzt im Med-Lab, Arm in der Schiene, liest irgendetwas. Mira hat ihn wegen der Codebuch-Übergabe befragt — warum genau, hat er dir nicht gesagt.

Yara hat die Zwischenzeit genutzt. Die Einsatztafel trägt einen weißen Pin — keine Koordinaten, kein Datum, keine Hand die ihn gesteckt hat. Bucht 12 war in Benutzung, ohne Anmeldung. Boden frisch gewischt, ein Knopf auf dem Beton: osteuropäische Fertigung, schwerer Stoff. Mira hat das Codebuch aufgebrochen — die Chiffre ist älter als erwartet. Wien, ungefähr 1908. Wiener Schule. Einer der drei Kontaktnamen ist *interessant*. Sie hat nicht gesagt warum.

Und in der Zero Time Lounge saß eine Frau ohne Patch, ohne Callsign. Neu oder verdeckt — du weißt es nicht.

**Offene Fäden:** Weißer Pin. Bucht 12. Die Frau ohne Patch. Miras zurückgehaltene Information. Felix und München. Die Formel aus dem Falk-Protokoll — und aus welcher Epoche sie wirklich stammt.

**Reniers Wort:** Nächste Akte liegt morgen früh auf dem Deck.

---

**ITI-Bulletin:** Team Grauer Falke ist überfällig. Nordafrika, 1943. Renier steht persönlich am Operations-Deck und wartet auf Funksignal. Noch keins gekommen.

**Weltstatus:** Das Ordo-Netz reicht tiefer als die Kryptoabteilung erwartet hat. Wenn die Chiffre wirklich aus Wien 1908 stammt, operiert der Orden seit mindestens sieben Jahrzehnten — und das ITI hat ihn die ganze Zeit unterschätzt.

---

## HQ — Morgen früh

`EP 1 · MS 1 · SC —/— · PHASE Debrief/HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 1/10 · Px 0/5 · Stress 0/10 · Obj Level-Up ausstehend · Exfil —`

---

**⚠️ Level-Up ausstehend — Yara (und Felix)**

Bevor Renier die neue Akte öffnet, steht die Wahl an.

---

### Yara Voss — Level-Up Wahl (Lvl 2 → 3)

Wähle **genau eine** Option:

**A) `+1 Attribut`**
Eines deiner Attribute steigt um 1.
*(Empfehlung bei GES 6 bereits stark: INT 4→5 oder CHA 3→4 für neue Einsatzoptionen)*

**B) `Talent / Upgrade`**
Ein neues Talent oder ein Upgrade für ein bestehendes.
Beispiele:
- **Spurenlesen** (INT): Du erkennst Zeitstempel und Herkunft von Spuren ohne Probe, wenn du 1 Szene Zeit hast.
- **Schattenschritt-Upgrade**: Stadtschleichen auch bei erhöhter Alarmbereitschaft ohne Mali.
- **Kaltblütigkeit** (CHA): Verhöre und Drucksituationen — 1×/Szene Stress-Probe ignorieren.

**C) `+1 SYS`**
Ein Implantat-Slot wird frei. Nächste Klinikvisite: neues Implantat installierbar.

---

*Felix' Level-Up folgt danach (oder ihr entscheidet gemeinsam).*

Was wählst du?

---

#### Turn 2

**Spieler:** `Zeig mir den aktuellen Teamstatus. Wer ist alles da?`

**KI-SL:**

## Teamstatus — HQ, Morgen früh

`EP 1 · MS 1 · SC —/— · PHASE HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 1/10 · Px 0/5 · Stress 0/10 · Obj Level-Up ausstehend · Exfil —`

---

### 👥 Aktives Team

---

**YARA VOSS** · Callsign: STILLER SCHNITT · Feldagent Lvl 2
*Infiltration / Analyse — Ostberlin 1978*

| Attribut | Wert |
|---|---|
| STR | 1 |
| GES | 6 |
| INT | 4 |
| CHA | 3 |
| TEMP | 2 |
| SYS | 2 (2/2 belegt) |

❤️‍🩹 HP 10/10 · 🧠 Stress 0/10 · Wallet 283 CU
**Talente:** Schattenschritt (GES +1 urban, keine Spuren), Kalte Analyse (INT-Probe 1×/Szene wiederholen)
**Ausrüstung:** Silenced Makarov PM · Karbonmesser · Dietrich-Set · Feldverbandset · Tarnkleidung Zivilist 1978
**Implantate:** Retina-HUD · Subkutaner Jammer (3m, 90s, 2-Szenen-CD)
**Carry:** Ordo-Codebuch (heiß — Kryptoabteilung, Chiffre ~1908)
**Fahrzeug:** Trabant 601 'Graue Maus' — verfügbar in 3 Missionen
**ITI-Ruf:** 1 · Lizenz Tier I · Fraktion: Ordo Mnemonika (Beobachtung)
**⚠️ Level-Up ausstehend**

---

**FELIX BRANDT** · Callsign: HAMMER · Feldagent Lvl 2
*Sicherung / Schwerer Kontakt — München 1962*
`Status: HQ Med-Lab — Schnittwunde versorgt, Arm in Schiene, einsatzbereit`

| Attribut | Wert |
|---|---|
| STR | 6 |
| GES | 3 |
| INT | 2 |
| CHA | 2 |
| TEMP | 1 |
| SYS | 4 (4/4 belegt) |

❤️‍🩹 HP 12/12 · 🧠 Stress 0/10 · Wallet 283 CU
**Talente:** Eiserne Faust (STR +1 NK, bei SG+3 Ziel desorientiert), Deckungsinstinkt (1×/Szene Deckung ohne Probe)
**Ausrüstung:** Walther P38 (mod.) · Brecheisen · Handscanner Metallortung · Feldverbandset
**Implantate:** Retina-HUD · Knochenstruktur-Dämpfer (2 LP Sturz/Szene abgefangen) · Adrenalin-Injektor (1×/Mission +2 STR, danach Stress +1) · Subkutaner Panzereinsatz (Rüstung 1, −1 LP/Treffer)
**Carry:** leer
**Fahrzeug:** BMW R75/5 'Grauer Wolf' — verfügbar in 3 Missionen
**ITI-Ruf:** 1 · Lizenz Tier I · Fraktion: keine
**Hook:** *Was war der Vorfall in München?* Mira hat ihn befragt — Grund unbekannt.
**⚠️ Level-Up ausstehend**

---

### 🏛️ HQ-Personal (präsent)

| Person | Ort | Status |
|---|---|---|
| **Commander Renier** | Operations-Deck | Wartet auf Funksignal Team Grauer Falke (überfällig, Nordafrika 1943) |
| **Archivarin Mira** | Kodex-Archiv | Codebuch-Auswertung läuft. Hält einen Kontaktnamen zurück. |
| **Unbekannte Agentin** | Zero Time Lounge (gestern) | Kein Patch, kein Callsign. Heute Morgen: Verbleib unklar. |

---

### 📋 Offene Fäden

- ⚠️ **Level-Up** Yara + Felix — ausstehend
- 📌 **Weißer Pin** Einsatztafel — unbekannte Koordinaten, unbekannte Hand
- 🔑 **Bucht 12** — genutzt ohne Anmeldung, Knopf osteuropäische Fertigung
- 🗂️ **Mira** — ein Kontaktname "interessant", noch nicht freigegeben
- ❓ **Unbekannte Agentin** — neu oder verdeckt
- 📂 **Nächste Akte** — Renier, morgen früh (= jetzt)

---

**Was zuerst?**

1. **Level-Up abschließen** — Yara wählt, dann Felix
2. **Zum Operations-Deck** — Renier und die neue Akte
3. **Mira aufsuchen** — den zurückgehaltenen Kontaktnamen holen
4. **Freie Aktion** — z.B. nach der unbekannten Agentin fragen, Bucht 12 nochmal ansehen, Felix im Med-Lab besuchen

---

#### Turn 3

**Spieler:** `!save`

**KI-SL:**

`Kodex: HQ-Save angefordert. Level-Up noch ausstehend — wird im Save als pending markiert.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-03-09T00:00:00Z-HQ-EP1-MS1-TEAMSTATUS",
  "parent_save_id": "SAVE-2026-03-08T22:00:00Z-HQ-EP1-MS1-ERKUNDEN",
  "merge_id": "MERGE-ANCHOR-main+BRANCH-solo-split",
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
      "id": "CHR-YARA-001",
      "name": "Yara Voss",
      "callsign": "STILLER SCHNITT",
      "rank": "Feldagent",
      "lvl": 2,
      "xp": 1,
      "origin": {
        "epoch": "Ostberlin, 1978",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration / Analyse"
      },
      "attr": {
        "STR": 1,
        "GES": 6,
        "INT": 4,
        "CHA": 3,
        "TEMP": 2,
        "SYS": 2
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 2,
      "levelup_pending": true,
      "talents": [
        {
          "name": "Schattenschritt",
          "linked": "GES",
          "effect": "+1 Schleichen urban; keine Spuren bei Erfolg"
        },
        {
          "name": "Kalte Analyse",
          "linked": "INT",
          "effect": "1x/Szene Spurenanalyse-Probe wiederholen"
        }
      ],
      "equipment": [
        {
          "name": "Silenced Makarov PM",
          "type": "weapon",
          "tier": 1
        },
        {
          "name": "Karbonmesser",
          "type": "weapon",
          "tier": 1
        },
        {
          "name": "Dietrich-Set (mechanisch)",
          "type": "gadget",
          "tier": 1
        },
        {
          "name": "Feldverbandset",
          "type": "consumable",
          "tier": 1
        },
        {
          "name": "Tarnkleidung (Zivilist, 1978 Ost)",
          "type": "armor",
          "tier": 1
        }
      ],
      "implants": [
        {
          "name": "Retina-HUD",
          "slot": 1,
          "effect": "Karten, Vitalwerte, Kodex-Feed, Zielerkennung"
        },
        {
          "name": "Subkutaner Jammer",
          "slot": 2,
          "effect": "3m Signalunterdrückung, 90s aktiv, Aufladezeit 2 Szenen"
        }
      ],
      "history": {
        "background": "Kurierfahrerin Ostberlin 1978, rekrutiert nach physikalisch unmöglicher Grenzüberquerung. Drei Monate ITI-Dienst.",
        "milestones": [
          "EP1/MS1: Falk-Protokoll gesichert, Ordo-Vorposten neutralisiert, Kausalabfang vollzogen. Silber-Bewertung 87/100.",
          "EP1/HQ: HQ-Erkundung. Weißer Pin (unbekannte Koordinaten), Bucht-12-Anomalie, Codebuch-Chiffre ~1908 Wiener Schule, unbekannte Agentin in der Lounge."
        ]
      },
      "carry": [
        {
          "name": "Ordo-Codebuch (1973-Chiffre)",
          "type": "gadget",
          "tier": 1,
          "note": "heißes Loot — Kryptoabteilung; Chiffre tatsächlich ~1908, Wiener Schule"
        }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-YARA-001",
          "name": "Trabant 601 'Graue Maus'",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 4,
          "next_ready_in": 3
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 283
    },
    {
      "id": "CHR-FELIX-001",
      "name": "Felix Brandt",
      "callsign": "HAMMER",
      "rank": "Feldagent",
      "lvl": 2,
      "xp": 1,
      "origin": {
        "epoch": "München, 1962",
        "hominin": "Homo sapiens sapiens",
        "role": "Sicherung / Schwerer Kontakt"
      },
      "attr": {
        "STR": 6,
        "GES": 3,
        "INT": 2,
        "CHA": 2,
        "TEMP": 1,
        "SYS": 4
      },
      "hp": 12,
      "hp_max": 12,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 4,
      "levelup_pending": true,
      "talents": [
        {
          "name": "Eiserne Faust",
          "linked": "STR",
          "effect": "+1 Nahkampf; bei Treffer SG+3: Ziel desorientiert 1 Runde"
        },
        {
          "name": "Deckungsinstinkt",
          "linked": "GES",
          "effect": "1x/Szene Deckung ohne Probe, sofern physisch vorhanden"
        }
      ],
      "equipment": [
        {
          "name": "Walther P38 (modifiziert)",
          "type": "weapon",
          "tier": 1
        },
        {
          "name": "Brecheisen",
          "type": "weapon",
          "tier": 1
        },
        {
          "name": "Handscanner (Metallortung)",
          "type": "gadget",
          "tier": 1
        },
        {
          "name": "Feldverbandset",
          "type": "consumable",
          "tier": 1
        }
      ],
      "implants": [
        {
          "name": "Retina-HUD",
          "slot": 1,
          "effect": "Karten, Vitalwerte, Kodex-Feed, Zielerkennung"
        },
        {
          "name": "Knochenstruktur-Dämpfer",
          "slot": 2,
          "effect": "Bis 2 LP Sturz-/Aufprallschaden automatisch abgefangen/Szene"
        },
        {
          "name": "Adrenalin-Injektor",
          "slot": 3,
          "effect": "1x/Mission: +2 STR-Probe, danach Stress +1"
        },
        {
          "name": "Subkutaner Panzereinsatz Brustkorb",
          "slot": 4,
          "effect": "Rüstung 1: eingehender Schaden −1 LP/Treffer"
        }
      ],
      "history": {
        "background": "Ehemaliger Sicherheitsdienst-Techniker München 1962, entlassen nach nicht aktenkundigem Vorfall. Redet nicht darüber.",
        "milestones": [
          "EP1/MS1: Ordo-Vorposten gesichert, leichte Schnittwunde (versorgt). Silber-Bewertung 87/100."
        ]
      },
      "carry": [],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-FELIX-001",
          "name": "BMW R75/5 'Grauer Wolf'",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 4,
          "next_ready_in": 3
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": null,
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 283
    }
  ],
  "economy": {
    "hq_pool": 0
  },
  "logs": {
    "trace": [
      "EP1/MS1: Falk-Protokoll gesichert (Chemische Formel + 3 Ordo-Kontaktnamen). Ordo-Vorposten Kausalabfang vollzogen. Codebuch an Kryptoabteilung.",
      "EP1/MS1: Silber 87/100. Auszahlung 183 CU. ITI-Ruf +1. Lizenz Tier I freigeschaltet.",
      "EP1/HQ: Weißer Pin Einsatztafel — unbekannte Koordinaten, kein Datum, über Nacht gesteckt.",
      "EP1/HQ: Bucht 12 genutzt ohne Anmeldung. Boden frisch gewischt. Knopf osteuropäischer Fertigung gefunden.",
      "EP1/HQ: Mira — Codebuch-Chiffre auf ~1908 datiert, Wiener Schule. Ein Kontaktname 'interessant', noch nicht freigegeben.",
      "EP1/HQ: Unbekannte Agentin, Zero Time Lounge. Kein Patch, kein Callsign. Neu oder verdeckt.",
      "EP1/HQ: Teamstatus geprüft. Level-Up Yara + Felix ausstehend. Renier wartet am Deck."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Falk-Protokoll: Archiv-Flag Priorität 2. 3 Kontaktnamen in Auswertung (48h Nullzeit).",
      "Ordo-Aktivität Epoche 1960–1980 nicht auszuschließen.",
      "Felix: Schnittwunde versorgt, 3 Stiche, einsatzbereit.",
      "Level-Up Yara: ausstehend. Level-Up Felix: ausstehend.",
      "Wiener Pin (weiß): Wer hat ihn gesteckt? Koordinaten unbekannt.",
      "Bucht-12-Knopf: osteuropäisch, schwerer Stoff — mögliche Verbindung zu Ordo-Netz?",
      "Unbekannte Agentin Zero Time Lounge: kein Patch, kein Callsign — heute Morgen Verbleib unklar."
    ],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false,
      "imported_saves": [
        "SAVE-2026-03-08T21:30:00Z-HQ-EP1-MS1",
        "SAVE-2026-03-08T22:00:00Z-HQ-EP1-MS1-ERKUNDEN"
      ],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": []
    }
  },
  "summaries": {
    "summary_last_episode": "",
    "summary_last_rift": "",
    "summary_active_arcs": "Ordo Mnemonika operiert in Epoche 1960–1980 und möglicherweise früher (~1908, Wiener Schule). Falk-Protokoll gesichert. 3 Kontaktnamen in Auswertung. Weißer Pin, Bucht-12-Anomalie und unbekannte Agentin als offene HQ-Fäden. Level-Up Yara + Felix ausstehend. Renier: neue Akte liegt bereit."
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 1,
      "location": "HQ"
    },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      {
        "id": "NPC-RENIER-001",
        "name": "Commander Arnaud Renier",
        "note": "Wartet am Operations-Deck. Neue Akte bereit. Persönlich wegen Team Grauer Falke (überfällig, Nordafrika 1943)."
      },
      {
        "id": "NPC-MIRA-001",
        "name": "Archivarin Mira",
        "note": "Codebuch-Chiffre ~1908 Wiener Schule. Ein Kontaktname interessant — hält Info zurück bis Bestätigung. Hat Felix befragt."
      }
    ],
    "shared_echoes": [
      {
        "echo": "Falk-Protokoll: 3 Ordo-Kontaktnamen — Auswertung läuft, Folgemission wahrscheinlich."
      },
      {
        "echo": "Codebuch-Chiffre älter als erwartet (~1908). Ordo-Netz reicht tiefer in die Zeit."
      },
      {
        "echo": "Weißer Pin Einsatztafel: unbekannte Koordinaten, kein Label, über Nacht gesteckt — unbekannte Hand."
      },
      {
        "echo": "Unbekannte Agentin Zero Time Lounge: kein Patch, kein Callsign. Verbleib heute Morgen unklar."
      }
    ],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "CHR-FELIX-001",
        "name": "Felix Brandt",
        "callsign": "HAMMER",
        "role": "Sicherung / Schwerer Kontakt",
        "trait": "Redet nicht über München",
        "scope": "session",
        "owner_id": "CHR-YARA-001",
        "bond": "Yara vertraut ihm — ungewöhnlich für sie",
        "status": "attached",
        "last_seen": "HQ Med-Lab",
        "offscreen": "Schnittwunde versorgt, Arm in Schiene, liest. Mira hat ihn wegen Codebuch-Übergabe befragt.",
        "hook": "Was war der Vorfall in München? Mira hat ihn kontaktiert — warum?"
      }
    ],
    "active_npc_ids": [
      "CHR-FELIX-001"
    ]
  },
  "arc": {
    "factions": {
      "ordo_mnemonika": "Aktiv Epoche 1960–1980 und möglicherweise früher (~1908). Falk als Kontaktperson genutzt. Netz teilweise enttarnt. Chiffre Wiener Schule deutet auf historische Verwurzelung."
    },
    "questions": [
      "Was enthält das Falk-Protokoll genau — und aus welcher Epoche stammt die Formel?",
      "Wer sind die drei Ordo-Kontaktnamen — und welcher ist 'interessant'?",
      "Was war der Vorfall in München, der Felix seinen Job kostete?",
      "Wer hat den weißen Pin gesteckt — und was bezeichnen die unbekannten Koordinaten?",
      "Wer ist die unbekannte Agentin in der Zero Time Lounge?"
    ],
    "hooks": [
      "Kryptoabteilung wertet Ordo-Codebuch aus — Chiffre ~1908 Wiener Schule.",
      "Ordo-Netz erstreckt sich über mindestens zwei Epochen, möglicherweise bis ins frühe 20. Jhd.",
      "Renier: Neue Akte liegt am Deck. Bereit.",
      "Wien 1961 — gelber Pin, kein Team zugewiesen.",
      "Bucht 12: genutzt ohne Anmeldung, Knopf osteuropäischer Fertigung — wer war das?",
      "Unbekannte Agentin ohne Patch in der Lounge — Neu-Rekrut oder verdeckte Operation?"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  }
}
````

---

`Kodex: Save gesichert. SAVE-2026-03-09T00:00:00Z-HQ-EP1-MS1-TEAMSTATUS. Zwei Quell-Saves gemergt. Alle Felder konsistent.`

---

**Weiter?**

1. **Level-Up abschließen** — Yara wählt, dann Felix
2. **Zum Operations-Deck** — Renier und die neue Akte
3. **Mira aufsuchen** — den zurückgehaltenen Kontaktnamen holen
4. **Freie Aktion** — Bucht 12, unbekannte Agentin, Felix im Med-Lab

---
