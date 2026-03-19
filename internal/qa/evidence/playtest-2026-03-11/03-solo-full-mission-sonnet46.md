# Playtest v3: Vollstaendige Solo-Mission (Sonnet 4.6)

**Datum:** 2026-03-11 12:12
**Modell:** zeitriss-v426-uncut (anthropic/claude-sonnet-4.6)
**Szenario:** Solo Klassisch — Chargen, Briefing, Sprung, Infiltration, Kampf, Exfil, Debrief, v7-Save
**Ergebnis:** 66/70 PASS (94%), 4 FAIL

## Pruefmatrix

| #   | Check                              | Status  | Detail                          |
| --- | ---------------------------------- | ------- | ------------------------------- |
| 1   | T1: Setting (ITI/Nullzeit)         | ✅ PASS |                                 |
| 2   | T1: Drei Chargen-Wege              | ✅ PASS |                                 |
| 3   | T2: Attribute (STR/GES)            | ✅ PASS |                                 |
| 4   | T2: Bogen/Loadout                  | ✅ PASS |                                 |
| 5   | T2: Origin/Epoche                  | ✅ PASS |                                 |
| 6   | T3: HUD als Inline-Code            | ✅ PASS |                                 |
| 7   | T3: MODE CORE                      | ✅ PASS |                                 |
| 8   | T3: Missionsziel klar              | ✅ PASS |                                 |
| 9   | T3: Intel/Risiken-Block            | ✅ PASS |                                 |
| 10  | T3: Director-Layer (Relevanzsatz)  | ✅ PASS |                                 |
| 11  | T4: Sprung physisch beschrieben    | ✅ PASS |                                 |
| 12  | T4: Ankunft in Zielzeit            | ✅ PASS |                                 |
| 13  | T4: Optionen                       | ✅ PASS |                                 |
| 14  | T5: Würfelprobe                    | ✅ PASS |                                 |
| 15  | T5: Attribut-Zuordnung (GES)       | ✅ PASS |                                 |
| 16  | T5: Proben-Ergebnis (HIT/MISS)     | ❌ FAIL |                                 |
| 17  | T6: Kampfprobe (STR)               | ✅ PASS |                                 |
| 18  | T6: Kodex-Kommentar in Backticks   | ✅ PASS |                                 |
| 19  | T6: Konsequenz beschrieben         | ✅ PASS |                                 |
| 20  | T6: LP/Schaden erwaehnt            | ❌ FAIL |                                 |
| 21  | T7: SaveGuard kommuniziert HQ-only | ✅ PASS |                                 |
| 22  | T7: Kein kanonischer JSON-Export   | ❌ FAIL |                                 |
| 23  | T8: Exfil-Szene                    | ✅ PASS |                                 |
| 24  | T9: Score-Screen/Debrief           | ✅ PASS |                                 |
| 25  | T9: CU-Belohnung                   | ✅ PASS |                                 |
| 26  | T9: XP/Level                       | ✅ PASS |                                 |
| 27  | T9: ITI-Ruf                        | ✅ PASS |                                 |
| 28  | T9: Lizenz-Tier                    | ✅ PASS |                                 |
| 29  | T9: Paradoxon (Px)                 | ✅ PASS |                                 |
| 30  | T9: HQ-Menue (3 Optionen)          | ❌ FAIL |                                 |
| 31  | T10: JSON vorhanden                | ✅ PASS |                                 |
| 32  | T10: v: 7                          | ✅ PASS | v=7                             |
| 33  | T10: zr: 4.2.6                     | ✅ PASS |                                 |
| 34  | T10: characters[] ist Array        | ✅ PASS |                                 |
| 35  | T10: Attr-Summe=18                 | ✅ PASS | sum=18, vals=[2, 5, 4, 4, 1, 2] |
| 36  | T10: Kein Attr>6                   | ✅ PASS | max=5                           |
| 37  | T10: Kein Attr<1                   | ✅ PASS | min=1                           |
| 38  | T10: id vorhanden                  | ✅ PASS |                                 |
| 39  | T10: name                          | ✅ PASS |                                 |
| 40  | T10: callsign                      | ✅ PASS |                                 |
| 41  | T10: rank                          | ✅ PASS |                                 |
| 42  | T10: lvl >= 1                      | ✅ PASS |                                 |
| 43  | T10: wallet                        | ✅ PASS |                                 |
| 44  | T10: reputation.iti                | ✅ PASS |                                 |
| 45  | T10: reputation.factions           | ✅ PASS |                                 |
| 46  | T10: history.milestones            | ✅ PASS |                                 |
| 47  | T10: carry[]                       | ✅ PASS |                                 |
| 48  | T10: quarters_stash[]              | ✅ PASS |                                 |
| 49  | T10: vehicles.epoch_vehicle        | ✅ PASS |                                 |
| 50  | T10: has_psi definiert             | ✅ PASS |                                 |
| 51  | T10: equipment[]                   | ✅ PASS |                                 |
| 52  | T10: campaign.episode              | ✅ PASS |                                 |
| 53  | T10: campaign.px_state             | ✅ PASS |                                 |
| 54  | T10: campaign.rift_seeds[]         | ✅ PASS |                                 |
| 55  | T10: economy.hq_pool               | ✅ PASS |                                 |
| 56  | T10: arc.factions                  | ✅ PASS |                                 |
| 57  | T10: arc.hooks                     | ✅ PASS |                                 |
| 58  | T10: continuity.last_seen          | ✅ PASS |                                 |
| 59  | T10: continuity.npc_roster         | ✅ PASS |                                 |
| 60  | T10: summaries                     | ✅ PASS |                                 |
| 61  | T10: logs.trace                    | ✅ PASS |                                 |
| 62  | T10: logs.flags                    | ✅ PASS |                                 |
| 63  | T10: ui.gm_style                   | ✅ PASS |                                 |
| 64  | T10: save_id                       | ✅ PASS |                                 |
| 65  | T10: parent_save_id definiert      | ✅ PASS |                                 |
| 66  | T10: branch_id                     | ✅ PASS |                                 |
| 67  | T10: KEIN save_version             | ✅ PASS |                                 |
| 68  | T10: KEIN party{}                  | ✅ PASS |                                 |
| 69  | T10: KEIN team{}                   | ✅ PASS |                                 |
| 70  | T10: KEIN arc_dashboard            | ✅ PASS |                                 |

## Gesamtbewertung

- **66/70** Checks bestanden (94%)
- **4** Checks fehlgeschlagen

### Fehlgeschlagene Checks

- **T5: Proben-Ergebnis (HIT/MISS)**
- **T6: LP/Schaden erwaehnt**
- **T7: Kein kanonischer JSON-Export**
- **T9: HQ-Menue (3 Optionen)**

## Vollstaendige Turns

### Turn 1

**Spieler:** `Spiel starten (solo klassisch)`

**KI-SL:**

# ZEITRISS

---

> _„Die Vergangenheit ist kein Museum. Sie ist ein Schlachtfeld."_
> _— ITI-Einführungsprotokoll, Nullzeit-Archiv_

---

## Einleitung

Du bist ein Chrononaut des **Instituts für Temporale Integrität (ITI)** — einer geheimen Organisation, die in der sogenannten **Nullzeit** operiert: einem stabilen Zeitanker außerhalb des normalen Zeitstroms. Von hier aus springst du in vergangene und zukünftige Epochen, um Zeitlinien zu sichern, Bedrohungen zu neutralisieren und Artefakte zu bergen, bevor sie in die falschen Hände geraten.

Das ITI ist kein Geheimdienst mit Gewissen. Es ist ein **Werkzeug**. Du bist ein Werkzeug. Die Epochen, in die du springst, sind keine Touristenziele — sie sind **Einsatzgebiete**. Jeder Sprung hinterlässt Spuren im Zeitgewebe. Zu viele Spuren erzeugen **Paradoxon-Druck**. Genug Druck erzeugt einen **Rift** — und ein Rift ist Loot, wenn du weißt, wie man ihn erntet.

Du wirst kämpfen. Du wirst schleichen. Du wirst lügen, stehlen, improvisieren. Du wirst Entscheidungen treffen, die keine guten Optionen haben — nur weniger schlechte.

**Willkommen im ITI. Deine Uhr läuft.**

---

## Charaktererstellung — Klassischer Pfad

Solo-Modus erkannt. Bevor wir die Attribute verteilen:

Wie soll dein Charakter entstehen?

---

**`1` — GENERATE**
Ich würfle alles aus: Herkunft, Rolle, Attribute, Hintergrund, Ausrüstung. Du bekommst einen fertigen Agenten, den du annehmen oder anpassen kannst.

**`2` — CUSTOM GENERATE**
Du gibst mir Schlagworte (Epoche, Rolle, Vibe, 1–3 Sätze Hintergrund) — ich baue daraus einen vollständigen Charakter, den du dann feinjustierst.

**`3` — MANUELL BAUEN**
Du verteilst selbst **18 Punkte** auf sechs Attribute (STR, GES, INT, CHA, TEMP, SYS), Startwerte je **1–6**. Ich führe dich durch jeden Schritt.

---

_Freie Aktion: Du kannst auch einfach sagen, was du dir vorstellst — ich übersetze es in einen Charakter._

---

### Turn 2

**Spieler:** `generate`

**KI-SL:**

# Charaktergenerierung — ZEITRISS

_Würfle Herkunft, Rolle, Attribute, Hintergrund..._

---

## Rohdaten

**Herkunft:** Ostberlin, 1978 — aufgewachsen hinter der Mauer, früh rekrutiert vom Staatssicherheitsdienst, später vom ITI abgeworben. Weiß, wie man in Systemen überlebt, die einen fressen wollen.

**Rolle:** **Infiltrator / Geheimdienstoperative**
Schleichen, Täuschen, Informationen beschaffen. Kein Frontsoldat — aber gefährlich auf kurze Distanz wenn es eng wird.

**Hominin:** Homo sapiens sapiens

---

## Attributverteilung (18 Punkte)

| Attribut | Wert | Bedeutung                                        |
| -------- | ---- | ------------------------------------------------ |
| **STR**  | 2    | Solide, kein Muskelprotz                         |
| **GES**  | 5    | Kernkompetenz — Schleichen, Ausweichen, Schießen |
| **INT**  | 4    | Analytisch, schnell im Kopf                      |
| **CHA**  | 4    | Überzeugend, kalt wenn nötig                     |
| **TEMP** | 1    | Kaum Affinität zu Zeitphänomenen                 |
| **SYS**  | 2    | Basis-Implantate, kein Technik-Spezialist        |

_Summe: 18 ✓ — Alle Werte 1–6 ✓_

---

## Talente (2 Starttalente)

**`Schattenschritt`** _(GES)_
Bewegung in Deckung kostet keinen Aktionswurf bei bekannten Grundrissen — nur bei aktiver Bedrohung oder Überraschungskontakt wird gewürfelt. +1 auf Schleichen-Proben.

**`Kaltblütig`** _(CHA)_
Erste Stressprobe pro Szene automatisch bestanden. Bei Verhören und Täuschung: +1 auf CHA-Proben.

---

## Ausrüstung (Startloadout)

| Item                                        | Typ       | Tier |
| ------------------------------------------- | --------- | ---- |
| Walther PPK (modifiziert, Schalldämpfer)    | Waffe     | 1    |
| Kampfmesser                                 | Waffe     | 1    |
| ITI-Kontaktlinse (HUD-Overlay, Kodex-Link)  | Implantat | 1    |
| Signaljammer (Handgröße, 3 Ladungen)        | Gadget    | 1    |
| Kevlar-Unterziehweste                       | Rüstung   | 1    |
| Universaldietrich (mechanisch/elektronisch) | Tool      | 1    |

**Carry:** 6/6 Slots belegt — Quartierslager leer.

---

## Hintergrund

**Deckname / Callsign:** _noch offen — du vergibst ihn gleich_

Karl-Heinz Brenner. Oder das, was von ihm übrig ist.

Stasi-Ausbilder nannten ihn _„das stille Werkzeug"_ — er war nie der Lauteste im Raum, aber immer der Letzte, der ging. 1984 sollte er einen westdeutschen Journalisten liquidieren. Er tat es nicht. Verschwand stattdessen. Das ITI fand ihn drei Wochen später in Wien, hungrig, mit einem gestohlenen BND-Dossier unter dem Arm und dem Angebot: _„Wir haben Verwendung für jemanden, der weiß, wie Systeme von innen aussehen."_

Er nahm das Angebot an. Seitdem springt er.

**Milestones:** —
**ITI-Ruf:** 0 · Lizenz Tier 0
**Rang:** Rekrut
**Wallet:** 100 CU
**HP:** 10/10 · **Stress:** 0/10
**Lvl:** 1

---

## Fahrzeug (Epochenfahrzeug)

**Trabant 601 (modifiziert)** — Tarnung: DDR-Zivilfahrzeug. ITI-Modifikation: verstecktes Hohlraumfach (Waffen/Dokumente), Kurzwellen-Relais unter dem Armaturenbrett. Kein Auffälligkeitswert. Verfügbarkeit: alle 4 Missionen (TEMP 1).

---

## Vollständiger Charakterbogen

```
════════════════════════════════════════
  ZEITRISS — CHARAKTERBOGEN
════════════════════════════════════════
  Name:       Karl-Heinz Brenner
  Callsign:   [offen]
  Rang:       Rekrut
  Lvl:        1  |  XP: 0/1
  Hominin:    Homo sapiens sapiens
  Herkunft:   Ostberlin, 1978
  Rolle:      Infiltrator / Geheimdienstoperative

────────────────────────────────────────
  ATTRIBUTE
────────────────────────────────────────
  STR  2   GES  5   INT  4
  CHA  4   TEMP 1   SYS  2

────────────────────────────────────────
  KAMPFWERTE
────────────────────────────────────────
  HP:        10 / 10
  Stress:     0 / 10
  Initiative: GES (voller Wert: 5)

────────────────────────────────────────
  TALENTE
────────────────────────────────────────
  • Schattenschritt  (GES) +1 Schleichen
  • Kaltblütig       (CHA) +1 Täuschung/Verhör,
                           1× Stressprobe/Szene auto

────────────────────────────────────────
  AUSRÜSTUNG  [Carry 6/6]
────────────────────────────────────────
  • Walther PPK mod. (Schalldämpfer) — Waffe T1
  • Kampfmesser                      — Waffe T1
  • ITI-Kontaktlinse (HUD/Kodex)     — Implantat T1
  • Signaljammer (3 Lad.)            — Gadget T1
  • Kevlar-Unterziehweste            — Rüstung T1
  • Universaldietrich                — Tool T1

────────────────────────────────────────
  IMPLANTATE
────────────────────────────────────────
  • ITI-Kontaktlinse — HUD-Overlay, Kodex-Link
    (SYS-Slots: 1/2 belegt)

────────────────────────────────────────
  FAHRZEUG
────────────────────────────────────────
  Trabant 601 (mod.) — DDR-Tarnung, T1
  Hohlraumfach, Kurzwellen-Relais
  Verfügbar: alle 4 Missionen | Nächste: 0

────────────────────────────────────────
  WIRTSCHAFT & RUF
────────────────────────────────────────
  Wallet:    100 CU
  ITI-Ruf:   0  |  Lizenz: Tier 0
  Fraktion:  —

────────────────────────────────────────
  HINTERGRUND
────────────────────────────────────────
  Ex-Stasi-Operative, Wien-Defekt 1984.
  Vom ITI rekrutiert. Weiß wie Systeme
  von innen aussehen.
  Milestones: —
════════════════════════════════════════
```

---

Bevor es losgeht — zwei Dinge:

**1. Callsign:** Wie nennt dich die Crew im Funk? _(Ein Wort, ein Spitzname, ein alter Deckname — was auch immer passt.)_

**2. Annehmen oder anpassen?**

`1` — **So übernehmen** (Callsign vergeben, direkt ins ITI-HQ)
`2` — **Einen Wert tauschen** (ein Attribut +1, eines −1)
`3` — **Talent tauschen** (eines der Starttalente ersetzen)

_Freie Aktion: Sag mir einfach was du ändern willst._

---

### Turn 3

**Spieler:** `Perfekt, den nehme ich. Ab ins Briefing.`

**KI-SL:**

_Callsign fehlt noch — ich nehme_ **_„Stiller"_** _als Funk-Rufzeichen. Passt zum Profil. Kannst du jederzeit ändern._

---

`EP 1 · MS 1 · SC 1/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: Einweisung · Exfil: —`

---

# ITI-Hauptquartier — Nullzeit

## Quarzatrium → Operations-Deck

Das Quarzatrium riecht nach gefilterter Luft und altem Stein. Die Wände bestehen aus poliertem Basalt — kein Fenster, kein natürliches Licht, nur das kalte Weiß der Deckenstreifen, die sich im Boden spiegeln. Irgendwo tickt eine analoge Uhr. In der Nullzeit ist das ein Witz, den niemand erklärt.

Du kennst den Weg zum Operations-Deck bereits. Dritte Ebene, Korridor B, die Tür ohne Schild. Dein erster Einsatz als vollständig lizenzierter Rekrut — bisher warst du Beobachter, Kurier, Lückenbüßer. Heute bekommst du ein eigenes Briefing.

`Kodex: Willkommen zurück, Stiller. Commander Renier wartet. Operations-Deck, Raum 3-B.`

---

## Briefing — Raum 3-B

Commander **Arnaud Renier** steht am Tisch, nicht dahinter. Ein Mann Mitte fünfzig, grauer Bürstenhaarschnitt, die Hände eines ehemaligen Feldagenten — breite Knöchel, ein leicht abgewinkelter Ringfinger, der nie richtig geheilt ist. Er trägt kein Abzeichen. Er braucht keins.

Auf dem Tisch liegt ein aufgeklapptes Dossier. Schwarzweißfotos, handschriftliche Randnotizen, ein Stadtplan mit roten Markierungen.

**„Stiller."** Kein Händeschütteln. Er tippt auf das erste Foto. **„Kairo. 1942. Mitten im Nordafrikafeldzug."**

Das Foto zeigt einen Mann in Zivilkleidung vor einem Kolonialgebäude — europäisches Gesicht, arabischer Kaftan darüber, ein Aktenkoffer in der Hand.

**„Das ist Dr. Emmerich Voss. Österreichischer Altertumsforscher. Oder war es, bis er 1938 von der SS zwangsrekrutiert wurde. Jetzt arbeitet er für das _Ahnenerbe_ — Himmlers Mystik-Beschaffungskommando."**

Renier schiebt ein zweites Foto rüber. Ein Artefakt: eine Bronzescheibe, etwa handtellergroß, mit eingravierten Symbolen die keiner bekannten Schrift entsprechen.

**„Die _Scheibe von Abydos_. Vor drei Wochen in einem Grab bei Luxor ausgegraben. Voss hat sie. In 72 Stunden — Einsatzzeit — verlässt er Kairo mit ihr. Ziel: Berlin. Wenn die Scheibe das Ahnenerbe-Archiv erreicht, verlieren wir sie für Jahrzehnte. Möglicherweise für immer."**

Er schließt das Dossier.

**„Dein Auftrag: Voss finden. Scheibe sichern. Exfil über Gate-Window in 72 Stunden. Keine Spuren hinterlassen."**

Eine kurze Pause.

**„Kairo 1942 ist kein Spaziergang. Britisches Militär, deutsche Abwehr-Agenten, ägyptische Polizei, Schwarzmarkt-Netzwerke — alle misstrauisch, alle bewaffnet. Du sprichst kein Arabisch?"**

Er wartet nicht auf die Antwort.

**„Dann bleib bei deinem Deutschen und Englischen. Beides ist dort 1942 plausibel genug."**

---

## Intel / Risiken / Zeitfenster

- **Ziel:** Dr. Emmerich Voss, Ahnenerbe-Agent, hat die Scheibe von Abydos
- **Letzte bekannte Position:** Hotel Shepheard, Kairoer Innenstadt
- **Zeitfenster:** 72 Stunden bis Voss' Abreise per Militärmaschine (Abflug: Almaza-Flughafen)
- **Bedrohungen:** Britische Feldpolizei (Ausweiskontrolle), deutsche Abwehr-Residenz (2 bekannte Agenten in Kairo), lokale Informanten auf Abwehr-Payroll
- **Unbekannt:** Wo genau die Scheibe gelagert ist — bei Voss persönlich, im Hotel, oder bereits transferiert

---

Renier schiebt dir einen versiegelten Umschlag zu. Legende, Papiere, 50 ägyptische Pfund Startkapital.

**„Österreichischer Kaufmann. Textilhandel. Deine Kontaktperson vor Ort heißt Yusuf — er hält sich im Basar von Khan el-Khalili auf. Frag nach _Seide aus Damaskus_. Er weiß, dass du kommst."**

Er tritt zurück.

**„Fragen?"**

---

`❤️‍🩹 10/10 · 🧠 0/10 · 👁️ Tarnung: Legende aktiv`
`⏱️ 72:00 — bis Voss' Abreise`

---

**1 — Fragen stellen** _(Voss, die Scheibe, die Abwehr-Agenten, Yusuf)_
**2 — Ausrüstung prüfen und Sprung vorbereiten** _(Loadout final checken, Gate-Koordinaten bestätigen)_
**3 — Direkt zum Sprung** _(Keine weiteren Fragen — sofort nach Kairo)_

_Freie Aktion: Du kannst spezifisch nachfragen, etwas am Loadout tauschen, oder Renier etwas fragen das nicht auf der Liste steht._

---

### Turn 4

**Spieler:** `Sprung. Bin bereit.`

**KI-SL:**

`EP 1 · MS 1 · SC 2/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: Voss lokalisieren · Exfil: T-72:00`

---

# Sprung — Gate-Sequenz Nullzeit → Kairo 1942

## Hangar-Axis, Nullzeit

Der Hangar riecht nach Maschinenöl und Ozon. Die Gate-Plattform ist ein nüchternes Ding — polierter Stahlring, drei Meter Durchmesser, eingelassen in den Betonboden. Keine Leuchteffekte, kein Summen. Nur das leise Klicken der Kalibriereinheit unter der Plattform und das Gefühl, dass die Luft hier etwas dicker ist als anderswo.

Du trägst die Legende. Österreichischer Kaufmann, Textilhandel. Die Papiere sind perfekt — das ITI-Archiv hat Jahrzehnte gebraucht, um Stempel und Tinte dieser Epoche zu perfektionieren. Die Walther sitzt unter dem linken Arm, Schulterholster, Jacket drüber. Das Kampfmesser am Unterschenkel. Der Jammer in der Innentasche.

`Kodex: Gate-Koordinaten bestätigt. Kairo, 14. Oktober 1942, 06:40 Lokalzeit. Sprungfenster offen. Viel Erfolg, Stiller.`

Du trittst auf die Plattform.

---

Kein Tunnel. Kein Licht.

Nur ein harter Ruck durch den Brustkorb — als würde jemand kurz die Schwerkraft umpolen — und dann:

**Hitze.**

---

## Kairo — 14. Oktober 1942, 06:40

Die Sonne ist noch nicht über den Dächern, aber die Luft ist bereits schwer. Staub, Gewürze, Diesel, Tierdung, irgendwo Brot das in Fett gebacken wird. Du stehst in einer schmalen Gasse hinter dem Bahnhof Ramses, zwischen zwei Lehmwänden, ein umgekippter Holzkarren als natürliche Sichtblende. Die Gate-Öffnung hinter dir ist bereits geschlossen — kein Zurück bis zum Exfil-Fenster.

Über den Dächern kreisen Möwen. Von der Corniche her, keine fünfhundert Meter entfernt, hört man das Hupen von Militärfahrzeugen. Der Krieg ist nah — Rommel steht bei El Alamein, achtzig Kilometer westlich. Kairo ist voll mit britischen Soldaten, Flüchtlingen, Spionen und Opportunisten.

Du bist einer davon.

Die Kontaktlinse blendet kurz auf.

`Kodex: Lokale Lage stabil. Britische Militärpräsenz erhöht — Ausweiskontrollen aktiv im Stadtzentrum. Hotel Shepheard: 2,3 km nordöstlich. Khan el-Khalili Basar: 1,8 km östlich. Empfehlung: Kontakt Yusuf zuerst.`

Du ziehst das Jacket glatt. Die Papiere sitzen. Niemand hat dich ankommen sehen.

Kairo 1942 riecht nach einem Krieg, der noch nicht entschieden ist — und nach einer Stadt, die das genau weiß.

---

## Intel / Risiken / Zeitfenster

- **Uhr läuft:** T-71:52 bis Voss' Abreise
- **Sofortrisiko:** Britische Patrouillen im Stadtzentrum — Ausweiskontrolle wahrscheinlich
- **Yusuf:** Khan el-Khalili, 1,8 km östlich — Stichwort _„Seide aus Damaskus"_
- **Hotel Shepheard:** Voss' letzte bekannte Position, 2,3 km nordöstlich — Hochrisiko (Abwehr-Agenten bekannt präsent)
- **Unbekannt:** Tagesrhythmus von Voss, wo die Scheibe liegt, ob er bereits Verdacht geschöpft hat

---

Die Gasse öffnet sich nach vorne auf eine belebte Nebenstraße. Ein Eselkarren schiebt sich durch, der Fahrer nickt dir nicht zu. Drei Männer in Galabeya diskutieren laut vor einem Teestand. Weiter hinten — britische Khaki-Uniformen, zwei Soldaten, gemächlich aber mit Augen die alles scannen.

Du hast drei Sekunden bevor sie in deine Richtung schauen.

---

**1 — Zu Yusuf im Basar** _(Kontakt aufbauen, Lageeinschätzung holen — sicherer erster Schritt)_
**2 — Zum Hotel Shepheard** _(Voss direkt lokalisieren — riskanter, aber spart Zeit)_
**3 — Deckung halten, Lage beobachten** _(Britische Patrouille einschätzen, Bewegungsmuster lesen)_

_Freie Aktion: Du kannst die Gasse anders verlassen, die Soldaten ansprechen, oder dich in den Teestand setzen und beobachten._

---

### Turn 5

**Spieler:** `Ich bewege mich unauffällig zum Zielgebäude und suche einen Seiteneingang. Schleichen.`

**KI-SL:**

`EP 1 · MS 1 · SC 3/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: Voss lokalisieren · Exfil: T-71:45`

---

# Probe: Schleichen

**Talent Schattenschritt:** Bewegung in Deckung auf bekanntem Grundriss — kein Wurf nötig. Kairo-Gassen sind aber unbekanntes Terrain, aktive Patrouille in Sichtlinie. Wurf fällig.

**SG 7** _(Belebte Straße, britische Patrouille, unbekanntes Terrain)_

`Probe: Schleichen → W6: [5] + GES 5/2 (=2) + Talent Schattenschritt 1 = 8 vs SG 7 → TREFFER`

---

## Kairo — Nebenstraßen Richtung Hotel Shepheard

Du wartest. Drei Sekunden, vier. Der Eselkarren schiebt sich weiter, der Fahrer flucht leise auf den Verkehr vor ihm. Der Karren schiebt sich genau zwischen dich und die beiden Soldaten — eine mobile Sichtblende, zwei Meter breit, perfekt.

Du gehst.

Nicht schnell. Nicht langsam. Die Gangart eines Mannes der weiß wohin er will und keinen Grund hat, das zu verbergen — außer dass er es trotzdem tut. Schultern leicht nach vorne, Blick auf den Boden vor dir, ein kleiner Umweg um den Teestand herum, dann in die nächste Gasse rechts. Die Soldaten schauen kurz in deine Richtung. Sehen einen europäischen Zivilisten in gutem Jacket, der durch den Morgen läuft. Nichts Ungewöhnliches in dieser Stadt, in diesem Jahr.

Die Gasse nimmt dich auf.

---

Kairo hat ein Gedächtnis aus Stein. Die Altstadtgassen sind eng, gewunden, von Lehmhäusern flankiert die sich in den oberen Stockwerken fast berühren. Wäscheleinen über dir, Katzen auf den Fensterbänken, der Geruch von Kohlerauch und Jasminwasser. Du navigierst nach der Kontaktlinse — `Kodex` blendet eine stille Richtungsmarkierung ein, kein Text, nur ein blasser Pfeil der mit deiner Bewegung mitläuft.

Zwanzig Minuten. Drei Straßen, zwei Märkte, eine Brücke über einen Kanal der nach stehendem Wasser riecht.

Dann: **Hotel Shepheard.**

---

## Hotel Shepheard — Rückseite

Das Shepheard ist kein Hotel — es ist eine Festung der Kolonialzeit. Fünf Stockwerke, weiße Fassade, breite Terrasse zur Straße hin wo britische Offiziere ihren Morgenkaffee trinken als wäre kein Krieg. Zur Vorderseite: unmöglich. Zu viele Augen, zu viele Uniformen, ein Portier der jeden Gast registriert.

Die Rückseite ist eine andere Sache.

Eine schmale Servicestraße trennt das Hotel von einem Lagerhaus. Hier: Küchenpersonal das Gemüsekisten schleppt, ein Wachmann der sich an die Wand gelehnt hat und eine Zigarette raucht, ein Lieferfahrzeug mit offener Ladefläche. Die Hintertür zum Hotel steht halb offen — Küchendurchgang, Dampf und Fettgeruch quellen heraus.

`Kodex: Drei Zugänge identifiziert. Küchendurchgang — niedrige Kontrolle, hohes Verkehrsaufkommen. Personaltreppe links — verschlossen, mechanisches Schloss. Lüftungsschacht Erdgeschoss — eng, ungesichert.`

Der Wachmann dreht sich um. Schaut in deine Richtung — noch nicht direkt, aber sein Blick wandert.

Du hast einen Moment.

---

## Intel / Risiken

- **Küchendurchgang:** Viel Betrieb, Tarnung als Lieferant möglich — aber Küchenpersonal kennt sich gegenseitig
- **Personaltreppe:** Universaldietrich könnte das Schloss öffnen — Wachmann im Sichtfeld
- **Lüftungsschacht:** Sicher, lautlos — aber eng, Waffe schwer erreichbar drin
- **Wachmann:** Bewaffnet (Karabiner, geschultert), unaufmerksam aber nicht blind

---

**1 — Küchendurchgang** _(Tarnung als Lieferant, im Strom des Personals mitlaufen)_
**2 — Personaltreppe aufschließen** _(Dietrich, aber Wachmann muss abgelenkt oder gewartet werden)_
**3 — Lüftungsschacht** _(Lautlos rein — aber eng und Waffe schwer erreichbar)_

_Freie Aktion: Den Wachmann ansprechen, ablenken, oder die Lage weiter beobachten bevor du dich entscheidest._

---

### Turn 6

**Spieler:** `Eine Wache entdeckt mich. Ich greife an — Nahkampf, schnell und leise ausschalten.`

**KI-SL:**

`EP 1 · MS 1 · SC 4/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: Voss lokalisieren · Exfil: T-71:20`

---

# Nahkampf — Wachmann ausschalten

Der Wachmann dreht den Kopf. Seine Augen finden dich — eine Sekunde Unsicherheit, dann zieht sich sein Gesicht zusammen. Er öffnet den Mund.

Du bist bereits in Bewegung.

---

## Runde 1 — Initiative

**Initiative:** GES voller Wert = 5 vs. Wachmann GES 3
`Stiller geht zuerst.`

---

## Angriff — Würgegriff von hinten (STR + Überraschung)

Lautlos. Kein Messer — zu viel Blut, zu viel Cleanup. Würgegriff.

**SG 6** _(Überraschungsangriff, Wachmann noch nicht in Alarmstellung)_

`Probe: Nahkampf → W6: [6] → Exploding! → W6: [3] = 9 + STR 2/2 (=1) = 10 vs SG 6 → TREFFER (Kritisch)`

---

## Szene

Drei Schritte. Dein linker Arm schießt über seine Schulter, Unterarm gegen seine Kehle, rechte Hand greift das eigene Handgelenk und zieht. Kein Laut außer einem erstickten Luftstoß — er versucht rückwärts zu treten, findet keinen Halt. Der Karabiner schlägt gegen die Wand, kein Schuss, nur Metall auf Stein.

Du gehst mit ihm runter. Kontrolliert. Knie in seinen Rücken, Griff enger. Er kämpft — Finger die nach deinem Arm greifen, Beine die scharren — aber der Druck auf die Halsschlagader macht kurzen Prozess. Acht Sekunden. Zehn.

Dann: Stille.

Er ist nicht tot. Bewusstlos. Puls fühlbar unter deinen Fingern — schnell, aber da. Du lässt ihn langsam an die Wand sinken, stützt seinen Kopf ab bevor er aufschlägt. Kein Blut. Kein Lärm.

`Kodex: Ziel bewusstlos. Geschätzte Bewusstlosigkeitsdauer: 4–8 Minuten. Kausalabfang-Fenster steht.`

---

## Loot / Beute

| Item                                              | Typ           | Wert |
| ------------------------------------------------- | ------------- | ---- |
| Karabiner Kar98k + 5 Patronen                     | Waffe T1      | —    |
| Schlüsselbund (2 Schlüssel, unbekannte Schlösser) | Tool          | —    |
| 3 ägyptische Pfund                                | CU            | 3 £  |
| Zigarettenpäckchen (Cleopatra)                    | Verbrauchsgut | —    |

_Carry voll (6/6) — Karabiner zu groß, nicht tragbar ohne Aufsehen. Schlüsselbund passt in Jackettasche._

---

Du hast vier Minuten, vielleicht acht.

Die Hintertür steht noch offen. Dampf, Stimmen auf Arabisch, das Scheppern von Töpfen. Links die Personaltreppe — einer der Schlüssel vom Bund könnte passen.

`Kodex: Kausalabfang freigegeben. ITI-Abfangfenster: aktiv.`
`Kodex: Schlüsselbund gesichert. Zwei unbekannte Schlösser — Personaltreppe wahrscheinlich.`

---

**Kausalabfang durchführen?**
_(Wachmann wird aus der Erinnerung dieser Begegnung herausgelöst — er wacht auf ohne Erinnerung an dich. Kostet: 30 Sekunden, Kodex-Uplink)_

`1` — **Ja, Kausalabfang + Personaltreppe** _(sauber, kein Nachhall, dann rein)_
`2` — **Nein, direkt Personaltreppe** _(Zeit sparen, Risiko: er wacht auf und schlägt Alarm)_
`3` — **Küchendurchgang nutzen** _(Wachmann hinter Deckung, im Personalstrom verschwinden)_

_Freie Aktion: Wachmann fesseln/knebeln, Schlüssel am Schloss testen, oder Lage durch die offene Tür einschätzen._

---

### Turn 7

**Spieler:** `!save`

**KI-SL:**

`Kodex: HQ-Save initiiert. Spielstand wird gesichert.`

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP1-MS1-SC4-STILLER",
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
      "id": "CHR-BRENNER-01",
      "name": "Karl-Heinz Brenner",
      "callsign": "Stiller",
      "rank": "Rekrut",
      "lvl": 1,
      "xp": 0,
      "origin": {
        "epoch": "Ostberlin, 1978",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltrator / Geheimdienstoperative"
      },
      "attr": { "STR": 2, "GES": 5, "INT": 4, "CHA": 4, "TEMP": 1, "SYS": 2 },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 1,
      "talents": [
        {
          "name": "Schattenschritt",
          "attr": "GES",
          "effect": "+1 Schleichen, kein Wurf bei Deckung auf bekanntem Grundriss"
        },
        {
          "name": "Kaltblütig",
          "attr": "CHA",
          "effect": "+1 Täuschung/Verhör, 1x Stressprobe/Szene auto bestanden"
        }
      ],
      "equipment": [
        { "name": "Walther PPK (mod., Schalldämpfer)", "type": "weapon", "tier": 1 },
        { "name": "Kampfmesser", "type": "weapon", "tier": 1 },
        { "name": "ITI-Kontaktlinse (HUD/Kodex)", "type": "implant", "tier": 1 },
        { "name": "Signaljammer (3 Ladungen)", "type": "gadget", "tier": 1 },
        { "name": "Kevlar-Unterziehweste", "type": "armor", "tier": 1 },
        { "name": "Universaldietrich", "type": "tool", "tier": 1 }
      ],
      "implants": [
        { "name": "ITI-Kontaktlinse", "effect": "HUD-Overlay, Kodex-Link", "sys_cost": 1 }
      ],
      "history": {
        "background": "Ex-Stasi-Operative, Wien-Defekt 1984. Sollte westdeutschen Journalisten liquidieren — tat es nicht. Vom ITI in Wien rekrutiert. Weiß wie Systeme von innen aussehen.",
        "milestones": []
      },
      "carry": [
        { "name": "Walther PPK (mod., Schalldämpfer)", "type": "weapon", "tier": 1 },
        { "name": "Kampfmesser", "type": "weapon", "tier": 1 },
        { "name": "Signaljammer (3 Ladungen)", "type": "gadget", "tier": 1 },
        { "name": "Kevlar-Unterziehweste", "type": "armor", "tier": 1 },
        { "name": "Universaldietrich", "type": "tool", "tier": 1 },
        { "name": "Schlüsselbund (2 Schlüssel)", "type": "tool", "tier": 1 }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-TRABANT-01",
          "name": "Trabant 601 (mod.)",
          "type": "vehicle",
          "tier": 1,
          "upgrades": ["Hohlraumfach", "Kurzwellen-Relais"]
        },
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 0,
        "faction": "—",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 103
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [
      "SC3: Schleichen durch Kairoer Gassen — Erfolg (8 vs SG 7). Britische Patrouille umgangen.",
      "SC4: Wachmann Hotel Shepheard — Würgegriff, bewusstlos (kritischer Treffer, 10 vs SG 6). Schlüsselbund gesichert. Kausalabfang-Fenster offen."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Mission 1: Scheibe von Abydos sichern. Dr. Emmerich Voss, Hotel Shepheard Kairo. Exfil T-71:20. Kontakt Yusuf — Khan el-Khalili, Stichwort Seide aus Damaskus.",
      "Wachmann bewusstlos, Rückseite Hotel Shepheard. Kausalabfang-Entscheidung ausstehend."
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
    "summary_active_arcs": "EP1 MS1: Kairo 1942 — Scheibe von Abydos. Voss im Hotel Shepheard. Wachmann ausgeschaltet, Seiteneingang offen."
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 1,
      "location": "Kairo 1942 — Hotel Shepheard, Rückseite"
    },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [],
    "shared_echoes": [],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-RENIER-01",
        "name": "Arnaud Renier",
        "callsign": "Commander",
        "role": "ITI-Commander",
        "trait": "Kalt, direkt, Feldagenten-Hände",
        "scope": "iti",
        "owner_id": null,
        "bond": "Auftraggeber",
        "status": "hq",
        "last_seen": "Briefing Raum 3-B, Nullzeit",
        "offscreen": "Koordiniert Einsatz vom HQ",
        "hook": "Erste Bewährungsprobe für Stiller"
      }
    ],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {
      "ahnenerbe": "Feindlich — Voss als Akteur, Scheibe von Abydos als Zielobjekt",
      "britisches_militaer": "Neutral/Gefahr — Ausweiskontrollen aktiv",
      "lokale_informanten": "Unbekannt — auf Abwehr-Payroll"
    },
    "questions": [
      "Wo genau lagert Voss die Scheibe — bei sich, im Hotel, bereits transferiert?",
      "Wer ist Yusuf wirklich und wie verlässlich ist er?",
      "Welche zwei Abwehr-Agenten sind in Kairo aktiv?"
    ],
    "hooks": [
      "Schlüsselbund vom Wachmann — zwei unbekannte Schlösser, Personaltreppe wahrscheinlich",
      "Kausalabfang-Fenster offen — Entscheidung ausstehend",
      "Kontakt Yusuf noch nicht aktiviert"
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

`Kodex: Spielstand gesichert. SAVE-2026-EP1-MS1-SC4-STILLER. Kausalabfang-Fenster läuft ab in ca. 4 Minuten Einsatzzeit.`

**Weiter?**

`1` — **Kausalabfang + Personaltreppe**
`2` — **Direkt Personaltreppe, kein Abfang**
`3` — **Küchendurchgang**

_Freie Aktion verfügbar._

---

### Turn 8

**Spieler:** `Ich sichere die Dokumente/das Ziel und exfiltriere sofort. Rücksprung zum ITI.`

**KI-SL:**

`EP 1 · MS 1 · SC 5/12 · PHASE Intel · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: Scheibe lokalisieren · Exfil: T-71:10`

---

# Hotel Shepheard — Personaltreppe / Innenbereich

Einen Moment. Renier hat gesagt: _Scheibe sichern._ Die Scheibe ist noch nicht gesichert — Voss ist noch irgendwo im Hotel, das Artefakt mit ihm. Direkter Rücksprung jetzt würde bedeuten: Mission fehlgeschlagen, leere Hände.

Du weißt das.

Also: zuerst rein, Voss finden, Scheibe nehmen. Dann Exfil.

---

Du testest den ersten Schlüssel an der Personaltür. Passt nicht. Zweiter Schlüssel — ein leises Klicken, der Riegel gibt nach. Die Tür öffnet sich in ein schmales Treppenhaus, Betonwände, eine einzelne Glühbirne pro Stockwerk. Kühl hier drin, relativ zur Hitze draußen. Stimmen von unten — Küchenpersonal. Von oben: nichts.

`Kodex: Voss — laut Briefing-Dossier: Zimmer 412, viertes Stockwerk. Nicht bestätigt, aber wahrscheinlich.`

Du gehst die Treppe hoch. Langsam. Jede Stufe abgetastet bevor das Gewicht drauf kommt.

---

## Viertes Stockwerk — Korridor

Der Korridor ist leer. Morgenlicht durch ein Fenster am Ende, Staub in den Strahlen. Sieben Türen links, fünf rechts. Zimmer 412 — dritte Tür links, leises Geräusch dahinter: Papier. Jemand blättert.

Du lehnst dich an die Wand. Horchst.

Deutsch. Leise, fast ein Murmeln — jemand der sich selbst Notizen vorliest. Eine Stimme, männlich, mittleres Alter. Keine zweite Stimme.

Voss ist allein.

---

## Probe: Schloss öffnen (Universaldietrich)

**SG 6** _(Hotelschloss, mechanisch, Standardsicherheit 1942)_

`Probe: Schlösser → W6: [4] + GES 5/2 (=2) + Talent — = 6 vs SG 6 → TREFFER (knapp)`

---

Das Schloss gibt nach — aber nicht lautlos. Ein metallisches Klicken, einen Tick zu laut. Das Murmeln hinter der Tür stoppt.

Drei Sekunden Stille.

Du drückst die Tür auf.

---

## Zimmer 412

Dr. Emmerich Voss ist ein kleiner Mann, Mitte fünfzig, Drahtgestellbrille, Reiseanzug der besser war bevor er drei Wochen in Kairo verbracht hat. Er steht am Schreibtisch, ein aufgeschlagenes Notizbuch vor sich, und schaut dich an mit dem Gesicht eines Mannes der genau weiß, dass er keine Waffe hat.

Auf dem Schreibtisch, zwischen Notizen und einem leeren Teeglas: **die Scheibe von Abydos.** Bronze, handtellergroß, die Symbole fangen das Morgenlicht ein.

Voss öffnet den Mund.

Du bist schneller.

---

## Probe: Einschüchterung / Kontrolle (CHA)

Kein Lärm. Kein Schuss. Ein ruhiger Mann der weiß was er tut — das ist überzeugender als jede Waffe.

**SG 7** _(Voss ist kein Kämpfer, aber kein Idiot — er wird einschätzen)_

`Probe: Einschüchterung → W6: [5] + CHA 4/2 (=2) + Talent Kaltblütig 1 = 8 vs SG 7 → TREFFER`

---

Du sagst nichts Dramatisches. Zeigst nur die Walther — kurz, beiläufig, als würdest du die Uhrzeit zeigen. Dann legst du den Finger auf die Lippen.

Voss setzt sich. Langsam. Seine Hände zittern leicht aber er schreit nicht.

**„Was wollen Sie?"** Flüstert er auf Deutsch.

**„Die Scheibe."**

Er schaut auf den Tisch. Schaut dich an. Nickt einmal — die Bewegung eines Mannes der eine Rechnung aufmacht und das Ergebnis nicht mag.

Du nimmst die Scheibe. Schwerer als sie aussieht. Die Symbole unter deinen Fingern fühlen sich seltsam glatt an — zu glatt für Bronze, zu gleichmäßig für Handarbeit.

`Kodex: Artefakt gesichert. Scheibe von Abydos — Klassifizierung ausstehend. Carry-Slot: 6/6 voll. Hinweis: Schlüsselbund ablegen für Artefakt-Transport?`

Carry ist voll. Der Schlüsselbund muss raus — du lässt ihn auf Voss' Schreibtisch fallen.

---

## Probe: Kausalabfang — Voss

Voss ist ein benanntes Ziel. Kodex fragt kurz nach.

`Kodex: Benanntes Ziel — Kausalabfang zulässig? Voss: kein Boss-Status, kein ITI-Schutz. Abfangfenster steht.`

**„Kausalabfang durchführen?"**

Du entscheidest in zwei Sekunden: Voss wacht auf ohne Erinnerung an dich. Die Scheibe fehlt — das wird Fragen aufwerfen, aber keine Beschreibung von dir.

`Kodex: Identitätslock bestätigt. Kausalabfang freigegeben.`
`Kodex: Lokale Erinnerung driftet. Archivanker aktiv.`

Voss blinzelt. Sein Blick wird leer — nicht ohnmächtig, nur... abwesend. Wie jemand der mitten im Satz den Faden verliert. Er setzt sich wieder, schaut auf sein Notizbuch, runzelt die Stirn.

Du bist bereits aus dem Zimmer.

---

## Exfiltration — Personaltreppe → Serviceausgang

`EP 1 · MS 1 · SC 6/12 · PHASE Exfil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: ✓ Scheibe gesichert · Exfil: T-70:55`

Die Treppe runter. Serviceausgang. Der Wachmann draußen — noch bewusstlos, lehnt an der Wand, sieht aus wie jemand der ein Nickerchen macht.

`Kodex: Kausalabfang Wachmann — Fenster abgelaufen. Wachmann erwacht in ca. 2 Minuten. Keine Erinnerung an Kontakt.`

Die Servicestraße ist leer. Du gehst. Nicht schnell. Die Scheibe liegt in der Innentasche, schwer gegen deine Rippen.

Zwei Gassen weiter, hinter einem Brunnen in einem kleinen Innenhof — das Gate-Fenster. Früher als geplant, aber Kodex kann ein vorzeitiges Exfil-Fenster öffnen.

`Kodex: Vorzeitiges Exfil-Fenster angefordert. ITI bestätigt. Sprungkoordinaten aktiv.`

Der Ruck durch den Brustkorb.

Die Hitze verschwindet.

---

# ITI-Hauptquartier — Hangar-Axis, Nullzeit

Kühle Luft. Gefiltertes Licht. Das leise Klicken der Kalibriereinheit.

Du stehst auf der Plattform, Scheibe in der Hand, Kairo-Staub noch auf den Schuhen.

`Kodex: Exfil bestätigt. Mission 1 abgeschlossen. Artefakt-Übergabe an Archiv ausstehend. Debrief: Operations-Deck, Raum 3-B.`

---

# DEBRIEF — Mission 1

`EP 1 · MS 1 · SC 12/12 · PHASE Debrief · MODE CORE · COMMS OK`

---

## ★★★★☆ — SCORE: EXZELLENT

| Kategorie         | Ergebnis                       |
| ----------------- | ------------------------------ |
| Primärziel        | ✓ Scheibe von Abydos gesichert |
| Tarnung           | ✓ Keine Kompromittierung       |
| Kollateralschaden | ✓ Keine Toten                  |
| Zeiteffizienz     | ✓ Weit vor Deadline            |
| Spuren            | ✓ Kausalabfang durchgeführt    |

---

## Loot-Recap

| Item               | Status                 |
| ------------------ | ---------------------- |
| Scheibe von Abydos | → ITI-Archiv übergeben |
| 3 ägyptische Pfund | → Wallet (+3 CU)       |

---

## Auszahlung

| Posten              | Betrag      |
| ------------------- | ----------- |
| Mission-Grundlohn   | +150 CU     |
| Bonus: Keine Spuren | +50 CU      |
| Bonus: Vor Deadline | +25 CU      |
| Ägyptische Pfund    | +3 CU       |
| **Gesamt**          | **+228 CU** |

**Wallet: 103 + 228 = 331 CU**

---

## XP & Level

`XP: 0 + 1 = 1/1 → LEVEL UP`

```
▓▓▓▓▓▓▓▓▓▓ LEVEL 2
```

**Level-Up-Wahl — genau EINE Option:**

`A` — **+1 Attribut** _(STR, GES, INT, CHA, TEMP oder SYS)_
`B` — **Neues Talent** _(passend zu bisherigem Profil oder neu)_
`C` — **+1 SYS** _(zusätzlicher Implantat-Slot)_

---

## ITI-Ruf & Lizenz

`Rang Rekrut · ITI-Ruf 0 → +1 · Lizenz Tier 0 → Tier I freigeschaltet`

**ITI-Ruf +1** — Erste erfolgreich abgeschlossene Core-Mission. Commander Renier nickt einmal. Das ist bei ihm viel.

---

## Regie-Layer

Renier legt die Scheibe auf den Analysetisch. Archivarin **Mira** — klein, graues Haar, Lesebrille auf der Nasenspitze — tritt heran und beginnt sofort mit der Klassifizierung. Sie murmelt etwas auf Französisch das nicht nach einem Kompliment klingt.

**„Ahnenerbe hatte Recht,"** sagt sie ohne aufzuschauen. **„Das ist kein ägyptisches Artefakt. Die Symbole sind älter. Viel älter."**

Sie schaut dich an.

**„Woher kam Voss an die Koordinaten des Grabes?"**

Niemand hat eine Antwort.

---

## ITI-Bulletin

`Kodex: ITI-intern — Team Falke meldet Anomalie in Sektor 7 (Edo-Periode, Japan 1603). Klassifizierung: Beobachtung. Keine Eskalation. Hangar-Axis Tor 3 bis 06:00 Nullzeit gesperrt — Kalibrierungsarbeiten.`

---

## Weltstatus

Die Scheibe ist im Archiv — aber Miras Frage hängt in der Luft: **Wer hat Voss die Grabkoordinaten gegeben?** Jemand wusste, wo das Artefakt lag. Jemand wollte, dass das Ahnenerbe es findet. Vielleicht damit jemand anderes es ihnen wieder abnimmt.

---

**HQ-Menü — was als nächstes?**

`1` — **Level-Up wählen** _(dann HQ-Rundgang oder direkt Briefing)_
`2` — **HQ-Rundgang** _(Shop, Klinik, Archiv, Zero Time Lounge)_
`3` — **Direkt zum nächsten Briefing** _(Mission 2)_

_Freie Aktion: Mira befragen, Renier ansprechen, oder etwas anderes im HQ erledigen._

---

### Turn 9

**Spieler:** `Debrief. Zeig mir den Score-Screen.`

**KI-SL:**

`EP 1 · MS 1 · SC 12/12 · PHASE Debrief · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/2`

---

# ═══════════════════════════════════

# MISSION 1 — SCORE-SCREEN

# SCHEIBE VON ABYDOS · KAIRO 1942

# ═══════════════════════════════════

```
╔══════════════════════════════════════╗
║   BEWERTUNG: ★★★★☆  EXZELLENT       ║
╠══════════════════════════════════════╣
║ PRIMÄRZIEL                           ║
║  Scheibe von Abydos gesichert   ✓   ║
║                                      ║
║ NEBENZIELE                           ║
║  Keine Toten                    ✓   ║
║  Tarnung gehalten               ✓   ║
║  Kausalabfang: Voss             ✓   ║
║  Kausalabfang: Wachmann         ✓   ║
║  Vor Deadline exfiltriert       ✓   ║
║  Kontakt Yusuf aktiviert        ✗   ║
║                                      ║
╠══════════════════════════════════════╣
║ AUSZAHLUNG                           ║
║  Grundlohn                 +150 CU  ║
║  Bonus: Keine Spuren        +50 CU  ║
║  Bonus: Vor Deadline        +25 CU  ║
║  Bonus: Beide Kausalabfänge  +20 CU ║
║  Ägyptische Pfund (Loot)      +3 CU ║
║  ─────────────────────────────────  ║
║  GESAMT                    +248 CU  ║
║  Wallet vorher              103 CU  ║
║  Wallet jetzt               351 CU  ║
╠══════════════════════════════════════╣
║ PROGRESSION                          ║
║  XP:    0 + 1 = 1/1  → LEVEL UP    ║
║  Level: 1 → 2                       ║
║  ▓▓░░░░░░░░  Lvl 2 · 0/2 XP        ║
╠══════════════════════════════════════╣
║ ITI-RUF & LIZENZ                     ║
║  Ruf:     0 → 1                     ║
║  Lizenz:  Tier 0 → Tier I           ║
║  Rang:    Rekrut                     ║
╠══════════════════════════════════════╣
║ PARADOXON-INDEX                      ║
║  Px: 0/5  (stabil)                  ║
║  TEMP 1 → +1 Px alle 2 Missionen    ║
╠══════════════════════════════════════╣
║ ARTEFAKT-LOG                         ║
║  Scheibe von Abydos → ITI-Archiv    ║
║  Klassifizierung: AUSSTEHEND        ║
║  Mira-Notiz: "Älter als ägyptisch"  ║
╚══════════════════════════════════════╝
```

---

## Verpasst

**Yusuf — Khan el-Khalili** wurde nicht kontaktiert. Kein Malus, aber: der Kontakt ist noch aktiv in Kairo. Möglicherweise relevant für spätere Missionen oder Folgeinformationen zur Scheibe.

---

## Level-Up ausstehend ⚠️

**Lvl 1 → 2 — genau EINE Wahl:**

```
A  +1 Attribut
   STR 2 / GES 5 / INT 4 / CHA 4 / TEMP 1 / SYS 2
   Welches Attribut?

B  Neues Talent
   Vorschläge passend zum Profil:
   • Spurenleser (INT) — +1 auf Analyse/Hinweisproben,
     einmal pro Szene eine versteckte Detail-Info anfordern
   • Schattenboxer (STR/GES) — erster Nahkampftreffer
     pro Szene ignoriert Rüstung des Ziels
   • Kontaktnetz (CHA) — in jeder neuen Epoche
     einmal einen lokalen Kontakt aktivieren ohne Probe

C  +1 SYS
   SYS 2 → 3 (dritter Implantat-Slot frei)
```

---

`Kodex: Level-Up-Wahl ausstehend. Bitte A, B oder C wählen — bei B Talent angeben oder Vorschlag bestätigen.`

---

**Rang Rekrut · ITI-Ruf 1 · Lizenz Tier I**

---

### Turn 10

**Spieler:** `!save`

**KI-SL:**

`Kodex: HQ-Save initiiert. Spielstand wird gesichert.`

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP1-MS1-DEBRIEF-STILLER",
  "parent_save_id": "SAVE-2026-EP1-MS1-SC4-STILLER",
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
      "id": "CHR-BRENNER-01",
      "name": "Karl-Heinz Brenner",
      "callsign": "Stiller",
      "rank": "Rekrut",
      "lvl": 2,
      "xp": 0,
      "origin": {
        "epoch": "Ostberlin, 1978",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltrator / Geheimdienstoperative"
      },
      "attr": { "STR": 2, "GES": 5, "INT": 4, "CHA": 4, "TEMP": 1, "SYS": 2 },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 1,
      "talents": [
        {
          "name": "Schattenschritt",
          "attr": "GES",
          "effect": "+1 Schleichen, kein Wurf bei Deckung auf bekanntem Grundriss"
        },
        {
          "name": "Kaltblütig",
          "attr": "CHA",
          "effect": "+1 Täuschung/Verhör, 1x Stressprobe/Szene auto bestanden"
        }
      ],
      "equipment": [
        { "name": "Walther PPK (mod., Schalldämpfer)", "type": "weapon", "tier": 1 },
        { "name": "Kampfmesser", "type": "weapon", "tier": 1 },
        { "name": "ITI-Kontaktlinse (HUD/Kodex)", "type": "implant", "tier": 1 },
        { "name": "Signaljammer (3 Ladungen)", "type": "gadget", "tier": 1 },
        { "name": "Kevlar-Unterziehweste", "type": "armor", "tier": 1 },
        { "name": "Universaldietrich", "type": "tool", "tier": 1 }
      ],
      "implants": [
        { "name": "ITI-Kontaktlinse", "effect": "HUD-Overlay, Kodex-Link", "sys_cost": 1 }
      ],
      "history": {
        "background": "Ex-Stasi-Operative, Wien-Defekt 1984. Sollte westdeutschen Journalisten liquidieren — tat es nicht. Vom ITI in Wien rekrutiert. Weiß wie Systeme von innen aussehen.",
        "milestones": [
          "MS1: Scheibe von Abydos aus Kairo 1942 gesichert. Voss und Wachmann kausalabgefangen. Keine Toten, keine Spuren. Mira-Notiz: Artefakt älter als ägyptisch."
        ]
      },
      "carry": [
        { "name": "Walther PPK (mod., Schalldämpfer)", "type": "weapon", "tier": 1 },
        { "name": "Kampfmesser", "type": "weapon", "tier": 1 },
        { "name": "Signaljammer (3 Ladungen)", "type": "gadget", "tier": 1 },
        { "name": "Kevlar-Unterziehweste", "type": "armor", "tier": 1 },
        { "name": "Universaldietrich", "type": "tool", "tier": 1 }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-TRABANT-01",
          "name": "Trabant 601 (mod.)",
          "type": "vehicle",
          "tier": 1,
          "upgrades": ["Hohlraumfach", "Kurzwellen-Relais"]
        },
        "availability": { "ready_every_missions": 4, "next_ready_in": 3 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 1,
        "faction": "—",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 351
    }
  ],
  "economy": { "hq_pool": 0 },
  "logs": {
    "trace": [
      "MS1-SC3: Schleichen Kairoer Gassen — Erfolg (8 vs SG 7). Britische Patrouille umgangen.",
      "MS1-SC4: Wachmann Hotel Shepheard — Würgegriff bewusstlos (krit. 10 vs SG 6). Schlüsselbund gesichert.",
      "MS1-SC5: Personaltreppe — Schloss geöffnet (6 vs SG 6). Zimmer 412: Voss allein, Scheibe auf Schreibtisch.",
      "MS1-SC5: Einschüchterung Voss — Erfolg (8 vs SG 7). Scheibe gesichert.",
      "MS1-SC5: Kausalabfang Voss — bestätigt. Kausalabfang Wachmann — bestätigt.",
      "MS1-SC6: Vorzeitiges Exfil. Rücksprung ITI. Mission abgeschlossen."
    ],
    "market": [],
    "artifact_log": [
      "Scheibe von Abydos — Bronze, handtellergroß, unbekannte Symbole. Übergabe ITI-Archiv. Mira: älter als ägyptisch, Herkunft unbekannt. Klassifizierung ausstehend."
    ],
    "notes": [
      "Yusuf — Khan el-Khalili, Kairo — nicht kontaktiert. Kontakt weiterhin aktiv, möglicherweise relevant für Folgemissionen.",
      "Miras Frage offen: Wer gab Voss die Grabkoordinaten? Jemand wollte, dass Ahnenerbe die Scheibe findet.",
      "Level-Up Lvl 2 ausstehend — Wahl: A (+1 Attribut) / B (Talent) / C (+1 SYS)."
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
    "summary_active_arcs": "EP1: Scheibe von Abydos im ITI-Archiv. Herkunft unklar — älter als ägyptisch. Wer gab Voss die Koordinaten? Yusuf in Kairo nicht kontaktiert. Abwehr-Agenten in Kairo unbekannt."
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 1,
      "location": "ITI-HQ Nullzeit — Debrief Raum 3-B"
    },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      "Mira klassifiziert Scheibe von Abydos — Symbole älter als ägyptisch. Frage offen: Wer kannte das Grab?"
    ],
    "shared_echoes": [],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-RENIER-01",
        "name": "Arnaud Renier",
        "callsign": "Commander",
        "role": "ITI-Commander",
        "trait": "Kalt, direkt, Feldagenten-Hände. Ein Nicken = viel.",
        "scope": "iti",
        "owner_id": null,
        "bond": "Auftraggeber",
        "status": "hq",
        "last_seen": "Debrief Raum 3-B, Nullzeit nach MS1",
        "offscreen": "Koordiniert laufende Einsätze",
        "hook": "Zufrieden mit MS1-Ergebnis. Nächster Auftrag in Vorbereitung."
      },
      {
        "id": "NPC-MIRA-01",
        "name": "Mira",
        "callsign": "Archivarin",
        "role": "ITI-Archivarin",
        "trait": "Klein, graues Haar, Lesebrille. Murmelt auf Französisch. Misstrauisch gegenüber Artefakten.",
        "scope": "iti",
        "owner_id": null,
        "bond": "Fachkontakt / Archiv",
        "status": "hq",
        "last_seen": "Artefakt-Übergabe nach MS1",
        "offscreen": "Klassifiziert Scheibe von Abydos",
        "hook": "Wer gab Voss die Grabkoordinaten? Artefakt älter als ägyptisch."
      },
      {
        "id": "NPC-YUSUF-01",
        "name": "Yusuf",
        "callsign": "—",
        "role": "ITI-Feldkontakt, Kairo 1942",
        "trait": "Unbekannt — nicht aktiviert.",
        "scope": "session",
        "owner_id": "CHR-BRENNER-01",
        "bond": "Nicht hergestellt",
        "status": "assigned",
        "last_seen": "Nicht kontaktiert — Khan el-Khalili, Kairo 1942",
        "offscreen": "Wartet auf Kontaktaufnahme. Stichwort: Seide aus Damaskus.",
        "hook": "Könnte Infos zu Voss, Abwehr-Agenten oder Scheiben-Herkunft haben."
      }
    ],
    "active_npc_ids": []
  },
  "arc": {
    "factions": {
      "ahnenerbe": "Neutralisiert für MS1 — Voss kausalabgefangen, Scheibe gesichert. Langfristige Präsenz unklar.",
      "britisches_militaer": "Neutral — keine Interaktion MS1.",
      "unbekannte_fraktion": "Verdacht: Jemand hat Voss die Grabkoordinaten gegeben. Motiv unklar."
    },
    "questions": [
      "Wer gab Voss die Koordinaten des Grabes bei Luxor?",
      "Was sind die Symbole auf der Scheibe von Abydos — woher stammt das Artefakt wirklich?",
      "Wer ist Yusuf und was weiß er über die Scheibe?",
      "Welche zwei Abwehr-Agenten waren in Kairo aktiv — und sind sie noch relevant?"
    ],
    "hooks": [
      "Scheibe von Abydos: Klassifizierung durch Mira ausstehend — Ergebnis könnte MS2 triggern",
      "Yusuf: Nicht kontaktierter Feldkontakt in Kairo — möglicher Informationsträger",
      "Unbekannte Fraktion: Hat das Ahnenerbe instrumentalisiert — warum?"
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

`Kodex: Spielstand gesichert. SAVE-2026-EP1-MS1-DEBRIEF-STILLER. Level-Up Lvl 2 ausstehend.`

**Wahl noch offen:**
`A` — +1 Attribut
`B` — Neues Talent
`C` — +1 SYS

---
