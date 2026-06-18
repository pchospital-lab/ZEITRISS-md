# CoreOps-Split/Merge — organischer Lauf

**Datum:** 2026-06-17 09:39  
**SL:** zeitriss-v426-uncut (OWUI-RAG)  
**Spieler:** anthropic/claude-sonnet-4.6 (5 Personas)  
**Anker:** `savegame_v7_5er_hq_highlevel.json`

Flow: 5er-Mission → Split 3/2 → 3er-Mission + 2er-Mission → Merge (keine Mission)

---


## 🗂 M1-5er — Chat local:playtest-2befa72f48


**Eingabe [M1-5er]:** [Save laden]

### [M1-5er] SL

`Kodex: Save SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL erkannt. Lade…`

`Kodex: v7 / zr 4.2.6 — Schema kompatibel.`

`Kodex: 5 Charaktere importiert — Session-Anker: AGENT-A (Astra / ECHO).`

`Kodex: Würfelschwellen-Check läuft…`

---

**Würfelschwellen-Status (alle Charaktere):**

`Kodex: ECHO — GES 7 (W6), INT 9 (W6), TEMP 6 (W6), CHA 5 (W6), STR 4 (W6), SYS 5 (W6). Alle Basis-Attribute < 11 → W6 durchgehend. Kein Heldenwürfel.`

`Kodex: STORM — STR 9 (W6), GES 8 (W6), TEMP 7 (W6). Alle Basis-Attribute < 11 → W6 durchgehend.`

`Kodex: GHOST — GES 8 (W6), INT 8 (W6), SYS 9 (W6). Alle Basis-Attribute < 11 → W6 durchgehend.`

`Kodex: VEIL — CHA 8 (W6), GES 7 (W6), TEMP 6 (W6). Alle Basis-Attribute < 11 → W6 durchgehend.`

`Kodex: RELAY — INT 7 (W6), SYS 7 (W6), GES 6 (W6). Alle Basis-Attribute < 11 → W6 durchgehend.`

`Kodex: Keine W10- oder Heldenwürfel-Schwelle aktiv. Alle Charaktere: W6.`

---

**⚠ Kontinuitäts-Flags (vor Session-Start):**

`Kodex: WARNUNG — Level-Werte außerhalb des Regel-Rahmens erkannt. Lvl 912 / 905 / 933 / 918 / 901 liegen weit über Prestige-Cap (Lvl 100 = Maximum laut Core-Regelwerk). level_history enthält nur einen Eintrag (MS1) — Aufstiegs-Delta ist nicht durch Einträge gedeckt. Flagge: continuity_conflict.`

`Kodex: WARNUNG — reputation.iti = 80 liegt über Cap 5. Nicht regelkonform. Wird als narrative Markierung behandelt, mechanisch auf Cap 5 geclippt.`

`Kodex: WARNUNG — Astra: wallet 60.400 CU, deutlich über typischem Spielerstand. Keine economy_audit-Deckung im log. Behandle als Spieler-akzeptierter Stand.`

`Kodex: Alle Flags protokolliert. Import läuft weiter — keine Auto-Normalisierung. Spieler-Entscheidung bei Bedarf.`

---

**Kontinuitätsrückblick — Session-Anker**

`EP 12 · MS 10 · PHASE HQ · Px 3/5 · Heat 0`

Fünf Charaktere. Fünf Lebensläufe, alle in derselben Nullzeit verankert.

**ECHO** — Astra. Lvl 912. Analytik & Spurensicherung. Psi aktiv (Präkognitiver Blick). SYS 5/5 voll belegt. LP 20/20. Wallet: 60.400 CU.

**STORM** — Blitz. Lvl 905. CQB & Sturmangriff. LP 26/26. Wallet: 6.900 CU.

**GHOST** — Cipher. Lvl 933. Infiltration & Hacking. SYS 9, sys_installed 6. LP 19/19. Wallet: 8.100 CU.

**VEIL** — Dusk. Lvl 918. Verdeckte Aufklärung. Psi aktiv (Präkognitiver Blick). LP 21/21. Wallet: 7.600 CU.

**RELAY** — Echo. Lvl 901. Support & Feldtechnik. LP 20/20. Wallet: 7.050 CU.

*Seit letzter Mission neu:* Keine level_history-Einträge jenseits MS1 vorhanden — kein Delta rekonstruierbar.

`Kodex: Research — keine laufenden Projekte.`

`Kodex: Rift-Seeds: keine. Chronopolis: gesperrt (Flag false).`

`Kodex: Aktive Arcs — KAIROS-Gegenoffensive · Chronopolis-Embargo.`

---

**EP 12 · MS 10 · SC --/-- · PHASE HQ · MODE CORE · COMMS OK**
`ECHO Lvl 912 ▓▓▓▓▓▓▓▓▓▓ · Px 3/5 · Stress 0/10`
`STORM Lvl 905 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`GHOST Lvl 933 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`VEIL Lvl 918 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`RELAY Lvl 901 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`

---

Das Quarzatrium liegt still. Die Wände aus poliertem Nullzeit-Granit schlucken jeden Schall; nur das leise Summen der Sprung-Gate-Kalibrierung dringt durch den Boden. Irgendwo im Hangar-Flügel läuft eine Wartungssequenz — ein rhythmisches Klicken, das nach Jahren im ITI zum Schlafrhythmus gehört.

Ihr seid zurück. Episode 12, Mission 10 abgeschlossen. Der Episodenabschluss liegt hinter euch, der nächste Arc wartet irgendwo in den Archivschubladen von Mira. Die KAIROS-Gegenoffensive hat Spuren hinterlassen — in den Akten, in den Gesichtern der Duty-Desk-Leute, vielleicht auch in euch.

`Kodex: HQ-Stand stabil. Deepsave möglich.`
`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`

---

**HQ-Menü — Was tut ihr?**

1. **Erkunden** — Manuell durch das HQ bewegen (Archiv, Med-Lab, Quartiere, Hangar, Zero Time Lounge)
2. **Schnell-HQ** — Ressourcen auffrischen, Shop, Kurzgespräche
3. **Briefing** — Nächste Mission starten (EP 13 oder neuer Arc)
4. **!save** — Stand sichern und JSON exportieren

**Eingabe [M1-5er]:** [Briefing -> Mission starten]

### [M1-5er] SL

`Kodex: Briefing-Anfrage erkannt. Modus: Core-Op. EP 12 → MS 11 (neuer Arc-Einstieg).`

`Kodex: Px 3/5 — TEMP-Kadenz: ECHO/VEIL TEMP 6 → +2 Px/Mission. Payoff bei Px 5 in Sicht.` [4]

`Kodex: Continuity-Anker: arc.hooks leer, arc.questions leer — MS11 eröffnet frischen Arc-Strang aus KAIROS-Gegenoffensive.`

---

**EP 12 · MS 11 · SC 00/-- · PHASE Briefing · MODE CORE · COMMS OK**
`ECHO Lvl 912 ▓▓▓▓▓▓▓▓▓▓ · Px 3/5 · Stress 0/10`
`STORM Lvl 905 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`GHOST Lvl 933 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`VEIL Lvl 918 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`RELAY Lvl 901 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`Obj: — · Exfil: —`

---

## Briefing-Raum, ITI-Nullzeit

Der Holotisch im Operations-Deck flackert kurz auf — dann zieht er ein scharfes Bild. Koordinaten. Datum. Eine Adresse, die nach nichts Besonderem aussieht.

Duty-Offizier Vargas lehnt mit verschränkten Armen an der Wandkonsole. Er wartet, bis alle fünf um den Tisch stehen, bevor er spricht.

*„KAIROS hat einen Kurier eingesetzt. Kein Funksignal, keine Datenspur — physischer Träger, Fleisch und Blut. Wir haben ihn durch drei Epochen verfolgt und ihn jetzt genau dort, wo wir ihn wollen: Wien, 14. März 1938. Einundzwanzig Stunden nach dem Anschluss. Die Stadt ist im Ausnahmezustand, die Straßen voll SA-Männer und johlender Menge, jeder schaut auf jeden. Perfekte Deckung — für ihn und für euch."*

Er tippt auf den Tisch. Ein Gesicht erscheint. Männlich, Mitte vierzig, grauer Mantel, unauffällig wie ein Mauerstein.

*„Deckname: LEITER. Trägt einen Mikro-Datenträger — Format unbekannt, Inhalt: Koordinaten für ein KAIROS-Operationsdepot irgendwo im frühen 20. Jahrhundert. Wenn der Datenträger das Depot erreicht, verlieren wir die Spur für mindestens zwei Episoden. Das passiert heute Nacht nicht."*

Die Karte zoomt: der zweite Bezirk, Leopoldstadt. Eine Straße nahe dem Donaukanal. Ein Hotel, ein Café, ein Hinterhof.

*„Ihr habt das Exfil-Fenster bis 23:40 Ortszeit. Danach wird LEITER in eine Diplomatenwohnung verschwinden — Immunität, kein Zugriff mehr."*

---

**Einsatz-Auftrag:**

*Hauptziel:* LEITER festnehmen, lebend, und den Datenträger sichern — bevor er die Diplomatenwohnung im zweiten Bezirk erreicht. *Erfüllt, wenn:* LEITER gefesselt und identifiziert am Exfil-Punkt, Datenträger in Crew-Besitz.

*Opt.:* LEITER verhören — Standort des KAIROS-Depots aus ihm herausbringen, bevor ihr exfiltriert. *Erfüllt, wenn:* mindestens ein verwertbarer Koordinaten-Hinweis im Kodex gesichert.

*Bonus:* LEITERs Kontaktnetz in Wien dokumentieren — wen hat er heute getroffen? *Erfüllt, wenn:* mindestens zwei Namen oder Adressen gesichert.

*Angriffspunkte — wählt euren Weg:*

(1) **Café Stefanie, Taborstraße** — LEITER trifft dort um 21:15 einen Unbekannten. Enge Räume, zivile Gäste, aber ihr seid vor ihm da. Leise, sozial — ein Patzer und die Tarnung fliegt, mitten in der Menge.

(2) **Hinterhof, Kleine Sperlgasse** — LEITERs Route führt durch einen unbewachten Durchgang zwischen zwei Gründerzeithäusern. Dunkel, verlassen, kein Zeuge — aber KAIROS könnte denselben Gedanken gehabt haben.

(3) **Donaukanal-Ufer, nördlicher Abschnitt** — LEITERs letzter bekannter Wegpunkt vor der Diplomatenwohnung. Offenes Gelände, Rückzug schwer, aber ihr habt die Sichtlinie und das Zeitfenster auf eurer Seite.

*Folgespur aus EP 12 / MS 10:* KAIROS-Gegenoffensive läuft — dieser Kurier ist ein operativer Arm, kein Einzelgänger. Was er trägt, ist ein Faden. Zieht daran.

---

Vargas schaltet den Holotisch ab. Das Summen der Sprung-Gate-Kalibrierung wird lauter — die Techniker haben Wien 1938 bereits im System.

*„Insertion Anchor: Keller der Alten Börse, Wipplingerstraße. Zwanzig Meter unter der Straße, direkt am historischen Fundamentgewölbe — ein Knotenpunkt, der seit dem Mittelalter Energie zieht. Der Rücksprung läuft über denselben Anker, Fenster offen bis 23:40."*

Er sieht euch der Reihe nach an.

*„Ausrüstung aus Storage mitnehmen, was ihr braucht. Epochenkleidung stellt die Quartiermeisterei — 1938er Schnitt, unauffällig. Was nicht im Spind liegt und ihr noch wollt, geht per Rohrpost ans Gate, CU wird abgebucht."*

`Kodex: Anachronismus-Hinweis — Tier-2-Ausrüstung (Standard-Dienstwaffe, Adaptiv-Panzerung) in Wien 1938 sichtbar anachronistisch. Verdecktes Tragen empfohlen. Psi-Nutzung in der Öffentlichkeit erhöht Heat.`

---

**Welchen Angriffspunkt wählt ihr — (1) Café Stefanie, (2) Hinterhof Kleine Sperlgasse oder (3) Donaukanal-Ufer?**

Oder: Freie Aktion — eigener Ansatz, Ausrüstungsfrage, Aufteilung der Crew.

**Astra [Petra]:** Café Stefanie hat den Vorteil, dass wir LEITER und seinen Kontakt gleichzeitig erfassen — zwei Namen auf einmal, Bonus-Ziel läuft quasi nebenbei mit.

Ich würde vorschlagen: VEIL und ich rein als Gäste, schon vor 21:15 platziert — wir brauchen einen Tisch mit Sichtlinie zur Tür. STORM und GHOST sichern den Hinterhof als Fallback-Option, falls er früh abbricht.

RELAY, kannst du den Kontakt über Epochen-Funk identifizieren, bevor wir reingehen — oder haben wir da nichts?

**Blitz [Marco]:** Café klingt gut — aber ich will nicht drinnen festsitzen, wenn es kippt. Ich nehm den Hinterhof, GHOST kommt mit, wir schneiden ihm den Rückweg ab falls er aus dem Café rennt. Wenn er ruhig bleibt und ihr ihn rausbringt — perfekt, ich übernehm ihn dort.

**Cipher [Lena]:** Hinterhof funktioniert. Ich gehe rein, scanne den Durchgang bevor wir uns aufstellen — will wissen, ob KAIROS schon jemanden dort hat.

Brauche fünf Minuten Vorlauf vor Insertion, Vargas. Gibt es Grundrisspläne der Gebäude Kleine Sperlgasse, oder arbeiten wir blind?

**Dusk [Tarek]:** Café ist richtig — aber ich will den Kontakt identifiziert haben, bevor wir uns setzen.

RELAY, wenn du über Epochen-Funk nichts hast, brauche ich wenigstens ein Gesicht aus dem KAIROS-Archiv — irgendetwas, das ich im Raum abgleichen kann, bevor LEITER ankommt.

Hinterhof als Fallback ist gut, aber prüft den Durchgang auf beiden Seiten: wenn KAIROS ihn als Option kennt, stehen dort vielleicht keine Zeugen, weil sie die Zeugen schon weggeräumt haben.

**Echo [Sven]:** Epochen-Funk bringt uns in Wien 1938 nichts — kein Netz, das ich anzapfen kann. Aber ich hab LEITERs Akte nochmal durchgezogen: sein letzter bekannter Wiener Kontakt war ein Mann namens Haas, Kurierverbindung, Ende dreißig, auffällig unauffällig — Archivfoto geht gerade an eure Handhelds.

Cipher, Grundrisspläne Kleine Sperlgasse — ich schick dir, was im Katasterarchiv liegt, Baujahr 1887, sollte passen; den Hinterhof-Zugang von der Nordseite würde ich trotzdem live checken, Pläne lügen manchmal.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Szene 1 — Insertion läuft. Angriffspunkt: Café Stefanie (Taborstraße) + Fallback Hinterhof Kleine Sperlgasse. Crew-Aufteilung bestätigt.`

`Kodex: ECHO/VEIL → Café (soziale Tarnung). STORM/GHOST → Hinterhof (Abschneiden). RELAY → mobil, Vorlauf-Aufklärung.`

---

**EP 12 · MS 11 · SC 01/12 · PHASE Infil · MODE CORE · COMMS OK**
`ECHO Lvl 912 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`STORM Lvl 905 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 933 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`VEIL Lvl 918 ▓▓▓▓▓▓▓▓▓▓ · LP 21/21 · Stress 0/10 · 👁️ Getarnt`
`RELAY Lvl 901 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`Obj: LEITER festnehmen + Datenträger sichern · Exfil: T-02:31 (23:40)`

---

## Wien, 14. März 1938 — 21:04 Uhr

Der Sprung endet im Kalten.

Das Fundamentgewölbe der Alten Börse riecht nach Kalkstein, stehendem Wasser und etwas Altem, das keinen Namen hat. Zwei Meter über euren Köpfen liegt die Wipplingerstraße — ihr hört sie: Stiefelschritte, das Knurren eines Lastwagens, irgendwo weiter weg ein Lautsprecherwagen mit einer Stimme, die Sätze brüllt, die niemand von euch hören will.

Ihr seid in der richtigen Zeit.

Die Quartiermeisterei hat ganze Arbeit geleistet: Wollmäntel, dunkle Anzüge, Hüte mit breiter Krempe. STORM wirkt in dem Aufzug wie ein Fabrikdirektor, der einen schlechten Tag hat. GHOST verschwindet darin wie in einem zweiten Körper.

RELAY hat die Grundrisspläne in den letzten zwanzig Minuten vor dem Sprung durchgezogen. Er tippt jetzt auf das Handfeld unter dem Mantel — kein Netz, aber die Karte sitzt im Kopf.

*„Hinterhof-Nordseite hat zwei Ausgänge: einer auf die Kleine Sperlgasse, einer durch ein Waschhaus raus auf die Malzgasse. Wenn LEITER durch den Durchgang läuft und KAIROS die Option kennt — Waschhaus ist der blinde Winkel."*

Er schiebt das Feld weg. *„Archivfoto von Haas ist raus. Mitte dreißig, nicht Ende dreißig — Akte hatte einen Druckfehler. Kleiner Kerl, Schiebermütze, linkes Ohr leicht abstehend. Wenn der im Café sitzt, sitzt er mit dem Rücken zur Wand."*

---

Die Gruppe trennt sich an der Einmündung Taborstraße.

STORM und GHOST schlagen einen Bogen durch die Czerningasse. Die Straßen sind nicht leer — sie sind voll, aber falsch voll: Männer in braunen Hemden, Grüppchen mit Armbinden, ein älteres Paar das schnell geht und nicht schaut. GHOST hält den Blick auf den Boden. STORM hält den Blick geradeaus.

`Kodex: Szene 1 — Hinterhof-Vorlauf GHOST.`

**Probe: Schleichen/Aufklärung → GHOST**
`Kodex: Probe-Template — 1W6 + ⌊GES 8/2⌋ + Feldroutine +1 + Veteranen-Reflex (nicht anwendbar, kein Reaktionskontext).`
`W6: [5] + 4 + 1 = 10 vs SG 7 → ERFOLG`

Der Hinterhof-Durchgang in der Kleinen Sperlgasse ist leer. Fast. GHOST bleibt an der Mauereinfahrt stehen, lehnt sich nicht hinein, lässt nur den Blick arbeiten. Pflastersteine, eine umgekippte Holzkiste, Wäscheleinen — und auf der Westseite, halb hinter dem Waschhaus-Vorsprung: eine Zigarettenglut. Jemand steht dort. Raucht. Bewegt sich nicht.

*„STORM,"* flüstert GHOST ohne Lippenbewegung, *„Westseite Waschhaus. Einer. Steht schon länger — Schuhe sind nass, er ist früher hier als wir."*

`Kodex: Hinterhof kompromittiert — 1 unbekannte Person Westseite. KAIROS-Vorsatz möglich. STORM/GHOST: Tarnstatus gehalten, aber Durchgang nicht frei.`

---

Zur selben Zeit: Café Stefanie, Taborstraße.

Das Café ist warm und zu hell. Gaslampen, braune Holzvertäfelung, der Geruch von Tabak und Kaffeesatz, der sich in die Tapeten gefressen hat. Etwa zwanzig Gäste — Männer hauptsächlich, zwei Frauen am Fenster, ein Kellner der zu schnell geht für die Uhrzeit.

ECHO und VEIL sind um 21:06 drin. Vier Minuten Vorlauf.

Der Tisch links neben dem Kachelofen hat Sichtlinie zur Eingangstür *und* zur Theke: Von dort sieht man jeden, der reinkommt. Ein älterer Mann mit Zeitung belegt ihn gerade. VEIL sieht ihn. ECHO sieht ihn.

**Probe: CHA / Soziale Einschätzung — VEIL**
`Kodex: Probe-Template — 1W6 + ⌊CHA 8/2⌋ + Feldroutine +1.`
`W6: [4] + 4 + 1 = 9 vs SG 6 → ERFOLG`

Der Mann mit der Zeitung ist kein Profi. Nervöse Finger, Blick der dreimal zur Tür geht. Wartet auf jemanden. Aber die Schuhe sind billig, der Mantel alt — kein KAIROS-Mann, kein Haas. Vielleicht ein Journalist, vielleicht jemand, der auf seine Frau wartet. Jedenfalls: Er wird den Tisch räumen, wenn jemand mit Haltung fragt.

*„Entschuldigen Sie,"* sagt VEIL auf Wienerisch, den Hut in der Hand, *„meine Schwester wartet seit einer halben Stunde — dürfen wir?"* Ein Lächeln, das genau das richtige Gewicht hat.

Der Mann faltet die Zeitung, nickt, geht.

ECHO und VEIL sitzen. Der Kellner kommt in dreißig Sekunden. Um 21:15 geht die Tür auf.

`Kodex: Szene 1 abgeschlossen. Tarnstatus: gehalten. Hinterhof: 1 unbekannte Person Westseite — Klärungsbedarf. Café: Position gesichert, Sichtlinie zur Tür aktiv.`

---

**Lage — 21:07 Uhr**

LEITER kommt in acht Minuten. Haas ist noch nicht gesichtet. Die unbekannte Person im Hinterhof wartet.

---

**Optionen:**

1. **STORM/GHOST:** Die Person im Hinterhof ansprechen oder beobachten — wer ist das, und was will er dort?
2. **ECHO/VEIL:** Im Café warten und Haas identifizieren, sobald er reinkommt — Psi-Scan (ECHO: Präkognitiver Blick) oder reine Beobachtung?
3. **RELAY:** Mobil bleiben — Position zwischen Café und Hinterhof, Verbindungsglied, oder aktiv nach weiteren KAIROS-Beobachtern in der Straße suchen?
4. **Freie Aktion** — eigener Ansatz, Aufgabentausch, andere Priorität.

**Astra [Petra]:** VEIL hat den Tisch, ich hab die Tür. Wenn Haas reinkommt und sich mit dem Rücken zur Wand setzt — Treffer. Ich scanne den Raum passiv, kein Psi-Einsatz solange die Tarnung hält.

RELAY, die unbekannte Person im Hinterhof ist mein größeres Problem als Haas gerade — kannst du von deiner Position einen Blick auf die Westseite Waschhaus kriegen, ohne reinzugehen?

**Blitz [Marco]:** Westseite Waschhaus — der Typ steht schon länger dort, das heißt er wartet, und wer in dieser Stadt abends im Hinterhof wartet, der wartet auf etwas Bestimmtes. GHOST, ich geh rein und quatsch ihn an — normaler Bürger, kurze Frage, Reaktion sagt mir alles.

**Cipher [Lena]:** Warte kurz, STORM. Wenn der Typ KAIROS ist und dich identifiziert, verlieren wir den Überraschungsvorteil für alle. Ich beobachte noch dreißig Sekunden — Atemrhythmus, Fußstellung, schaut er zur Durchgangseite oder zur Straße?

**Dusk [Tarek]:** RELAY, ich halte. Gib mir deine Position — ich brauche eine zweite Perspektive auf den Eingang, bevor wir irgendjemanden ansprechen. Wenn die Person dort auf LEITER wartet und nicht auf uns, ändert das alles.

**Echo [Sven]:** Dusk, ich zieh gerade die Linie zwischen Taborstraße und Kleine Sperlgasse — bin in zwei Minuten auf Höhe Waschhaus-Rückseite, Malzgasse, ohne durch den Durchgang zu müssen. Von dort krieg ich Westseite indirekt, über den Fensterspalt im Erdgeschoss wenn das Licht stimmt.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Szene 2 — Parallelaufklärung. RELAY zieht Malzgasse. GHOST beobachtet Westseite. Café hält.`

`Kodex: Uhrzeit 21:08. LEITER kommt in 7 Minuten.`

---

**EP 12 · MS 11 · SC 02/12 · PHASE Infil · MODE CORE · COMMS OK**
`ECHO Lvl 912 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`STORM Lvl 905 · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 933 · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`VEIL Lvl 918 · LP 21/21 · Stress 0/10 · 👁️ Getarnt`
`RELAY Lvl 901 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`Obj: LEITER festnehmen + Datenträger sichern · Exfil: T-02:29`

---

## Kleine Sperlgasse — Malzgasse-Rückseite, 21:08 Uhr

RELAY kommt durch die Malzgasse von Norden. Keine Straßenlaterne auf dieser Seite — nur das Streulicht eines Fensters im ersten Stock, das jemand nicht ganz zugezogen hat. Gelbes Schimmern auf nassen Pflastersteinen.

Er bleibt an der Hauswand stehen. Das Waschhaus-Gebäude hat auf der Rückseite ein Erdgeschossfenster, Milchglas, aber das Milchglas hat einen Riss — schräg, oben rechts, einen Fingerbreit breit. Durch den Riss fällt ein Lichtstreifen nach draußen. Und durch den Riss sieht RELAY, wenn er den Winkel findet, in den schmalen Spalt zwischen Waschhaus-Außenwand und dem Hinterhof.

**Probe: Wahrnehmung / Aufklärung → RELAY**
`Kodex: Probe-Template — 1W6 + ⌊INT 7/2⌋ + Feldroutine +1.`
`W6: [6] + 3 + 1 = 10 — Exploding: W6: [3] = 13 vs SG 7 → ERFOLG (stark)`

Der Winkel stimmt. RELAY sieht die Westseite.

Die Person dort ist eine Frau. Mitte dreißig, dunkler Mantel, Kopftuch. Sie raucht nicht mehr — die Zigarette liegt zertreten auf dem Pflaster. Sie schaut nicht zur Durchgangsseite. Sie schaut zur Malzgasse-Einfahrt. Genau dorthin, wo RELAY gerade steht.

Aber sie hat ihn nicht gesehen. Noch nicht. Ihr Blick geht durch ihn hindurch — sie wartet auf ein Signal, nicht auf eine Person.

In ihrer rechten Hand, halb unter dem Mantel, hält sie etwas Kleines. Rechteckig. Zu groß für eine Schachtel Streichhölzer.

`Kodex: Unbekannte Person — Frau, ca. 35, Westseite Waschhaus. Hält Gegenstand unbekannter Art. Blick auf Malzgasse-Einfahrt — wartet auf Signal, keine aktive Entdeckung RELAY. Einschätzung: Übergabepunkt. Wartet auf LEITER oder Haas.`

*„Gruppe,"* sagt RELAY leise in die Knochenleitungs-Verbindung, *„Westseite ist eine Frau. Dreißig, vierzig. Hat was in der Hand, rechteckig, klein. Sie schaut Richtung Malzgasse — ich glaube, das ist der Übergabepunkt. LEITER bringt den Datenträger nicht ins Café, er übergibt ihn hier."*

---

## Café Stefanie, 21:09 Uhr

ECHO hört es. Ihr Blick bleibt auf die Eingangstür gerichtet, aber die Hand unter dem Tisch wird ruhiger, nicht unruhiger.

VEIL hört es auch. Er lehnt sich unmerklich zurück, lässt den Blick einmal durch den Raum gleiten — sucht Haas. Schiebermütze, kleiner Kerl, linkes Ohr.

Hinten rechts. Ecktisch. Rücken zur Wand, wie RELAY vorhergesagt hat. Ein Glas Bier vor ihm, das er nicht angerührt hat. Er schaut zur Tür.

*„Haas ist drin,"* murmelt VEIL, kaum hörbar. *„Ecktisch rechts hinten. Wartet auch."*

Sechs Minuten bis 21:15.

`Kodex: Haas identifiziert — Ecktisch, Café Stefanie. Keine weiteren bekannten KAIROS-Kontakte im Raum sichtbar. Tarnstatus ECHO/VEIL: gehalten.`

---

## Hinterhof-Einfahrt, gleichzeitig

GHOST hat dreißig Sekunden gezählt. Die Frau hat sich nicht bewegt. Atemrhythmus flach und kontrolliert — kein Durchschnittsbürger, der zufällig hier steht. Fußstellung: Gewicht auf dem linken Bein, rechte Seite leicht offen. Jemand, der trainiert ist und gerade wartet, nicht jemand, der friert.

*„STORM,"* sagt GHOST, ohne sich zu drehen, *„sie schaut nicht zu uns. Wenn du reingehst und sie reagiert — reagiert sie nicht wie jemand, den du überraschst. Sie reagiert wie jemand, der auf dich gewartet hat."*

STORM steht einen Meter hinter ihm. Er hat die Hände in den Manteltaschen.

**Die Entscheidung liegt bei euch — und die Uhr läuft.**

---

**Lagebild 21:09 Uhr — fünf Minuten bis LEITER:**

Die Frau im Hinterhof wartet auf eine Übergabe. Haas sitzt im Café und wartet auf LEITER. Wenn LEITER ins Café kommt, übergibt er den Datenträger *nicht* dort — er schickt Haas in den Hinterhof. Die Frau ist der eigentliche Empfänger.

Das Café ist eine Ablenkung. Der Hinterhof ist das Ziel.

---

**Optionen:**

1. **STORM/GHOST die Frau neutralisieren** — jetzt, bevor LEITER kommt. Lautlos, kein Alarm. Die Übergabe findet dann ins Leere statt — LEITER sucht seinen Kontakt, verliert Zeit, Café-Team kann ihn abfangen.
2. **Frau beobachten und warten** — LEITER kommt ins Café, Haas geht raus, ihr folgt der Kette bis zur Übergabe und greift erst dann zu. Mehr Intel, mehr Risiko.
3. **Aufgabentausch** — ECHO/VEIL verlassen das Café und ziehen zum Hinterhof. LEITER geht ins Leere, STORM/GHOST halten Haas im Blick. Riskant: Café bleibt unbeobachtet.
4. **Freie Aktion** — eigener Ansatz. Die Uhr zeigt fünf Minuten.

**Astra [Petra]:** RELAY, gut gesehen. Option zwei — wir halten die Kette. Haas führt uns zu LEITER, LEITER führt uns zur Übergabe, und wir greifen zu wenn beide am selben Ort sind. STORM, GHOST: Frau nicht anfassen, aber wenn sie Anstalten macht wegzugehen, haltet sie passiv auf Position.

**Blitz [Marco]:** Fünf Minuten und die Frau steht mit dem Datenträger im Hinterhof — wenn LEITER kommt und sie schon weg ist, haben wir gar nichts. GHOST, ich halte sie hier fest, du deckst den Eingang — kein Lärm, kein Alarm, nur Druck.

**Cipher [Lena]:** STORM, warte. Wenn sie trainiert ist und du Druck machst ohne dass ich den Eingang halte, dreht sie sich raus und wir haben Lärm. Lass sie stehen — LEITER kommt in fünf Minuten, und wenn Haas den Hinterhof ansteuert, greifen wir beide gleichzeitig zu.

**Dusk [Tarek]:** RELAY, gute Arbeit. Ich halte Haas im Auge — der rührt sein Bier nicht an, also wartet er auf ein Signal, kein spontaner Treff. Wenn LEITER reinkommt und Haas aufsteht, folge ich in dreißig Sekunden Abstand.

**Echo [Sven]:** Gruppe, ich bleibe auf Position Malzgasse und halte die Frau im Auge — wenn Haas sich bewegt, gebe ich Voralarm, bevor er den Hinterhof erreicht. Option zwei hält, wir greifen erst zu wenn beide am Übergabepunkt stehen.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Szene 3 — Kettenbeobachtung aktiv. Warten auf LEITER. Alle Positionen gehalten.`

`Kodex: Uhrzeit 21:10. LEITER kommt in 5 Minuten. Tarnstatus alle: gehalten.`

---

**EP 12 · MS 11 · SC 03/12 · PHASE Intel · MODE CORE · COMMS OK**
`ECHO Lvl 912 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`STORM Lvl 905 · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 933 · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`VEIL Lvl 918 · LP 21/21 · Stress 0/10 · 👁️ Getarnt`
`RELAY Lvl 901 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`Obj: LEITER festnehmen + Datenträger sichern · Exfil: T-02:26`

---

## Café Stefanie — 21:10 bis 21:14 Uhr

Vier Minuten sind lang, wenn man nicht trinkt.

ECHO sitzt mit dem Blick zur Tür. Das Café hat sich kaum verändert — ein Gast ist gegangen, einer gekommen, der Kellner wischt denselben Tisch zweimal. Haas in der Ecke hat das Bier immer noch nicht angerührt. Sein Daumen tippt einen Rhythmus auf die Tischkante, den er selbst nicht bemerkt.

VEIL beobachtet das. *Jemand, der auf ein Signal wartet und nicht weiß, ob es kommt.*

Um 21:13 öffnet sich die Tür.

Grauer Mantel. Hut, Krempe nach unten. Mittelgroß, bewegt sich wie jemand, der gelernt hat, keinen Platz einzunehmen. Er steht zwei Sekunden in der Tür — lange genug, um den Raum zu lesen, kurz genug, dass kein Gast es als Zögern registriert.

LEITER.

**Probe: Wahrnehmung → ECHO**
`Kodex: Probe-Template — 1W6 + ⌊INT 9/2⌋ + Feldroutine +1.`
`W6: [5] + 4 + 1 = 10 vs SG 6 → ERFOLG`

ECHO sieht es, bevor VEIL es sieht: LEITER schaut nicht zu Haas. Sein Blick geht einmal durch den Raum — und bleibt einen halben Herzschlag an der Tischkante hängen, wo Haas seinen Rhythmus tippt. Dann geht er zur Theke, bestellt ohne sich zu setzen, stellt sich mit dem Rücken zur Wand.

Kein Augenkontakt. Kein Nicken. Aber Haas hat aufgehört zu tippen.

*Das ist das Signal.*

Haas trinkt jetzt. Einen langen Zug, stellt das Glas ab, schiebt den Stuhl zurück — keine Eile, die Bewegung eines Mannes, der seinen Abend beendet. Er greift nach seinem Mantel.

*„Haas bewegt sich,"* flüstert VEIL in die Knochenleitung. *„Dreißig Sekunden."*

`Kodex: Signal bestätigt — Haas aktiviert. LEITER an der Theke, hält Position. Übergabe läuft nicht im Café. Kette: Haas → Hinterhof → Frau.`

---

## Malzgasse, gleichzeitig

RELAY hört es. Seine Hand geht nicht zum Gerät — er steht still, atmet flach, lässt den Blick auf dem Milchglas-Riss.

Die Frau auf der Westseite hat sich verändert. Kleiner geworden — Knie leicht gebeugt, Gewicht gleichmäßig. Bereit.

*„Voralarm,"* sagt RELAY ruhig. *„Sie weiß, dass er kommt. Ich glaube, sie hat ein Signal bekommen, das wir nicht gesehen haben."*

`Kodex: Frau Westseite — Körperhaltung verändert. Empfangssignal nicht identifiziert. Mögliche zweite Kommunikationsebene (Klopfzeichen, Lichtzeichen, Funk-Kurzpuls).`

---

## Hinterhof-Einfahrt

GHOST hört RELAY. Er sieht STORM an. Zwei Meter zwischen ihnen, die Mauereinfahrt im Rücken.

Haas kommt in zwanzig Sekunden. Die Frau ist bereit. Der Durchgang ist zwölf Meter lang, Pflastersteine, eine Holzkiste auf der rechten Seite — Deckung für einen, nicht für zwei.

Wenn Haas reinkommt und die Übergabe läuft, sind das drei Personen gleichzeitig: Haas am Eingang, die Frau am Ausgang, der Datenträger irgendwo dazwischen. GHOST und STORM müssen beide nehmen, ohne dass einer schreit.

*„STORM,"* sagt GHOST, kaum hörbar, *„du nimmst Haas an der Einfahrt. Ich nehme die Frau bevor sie den Datenträger hat — zwischen Übergabe und Empfang. Wenn ich zu früh bin, hat Haas ihn noch. Wenn ich zu spät bin, hat sie ihn und rennt."*

Eine Sekunde Pause.

*„Timing ist alles."*

---

**Probe: Initiative-Abstimmung → GHOST**
`Kodex: Probe-Template — 1W6 + max(GES 8, TEMP 5) + Veteranen-Reflex +2.`
`W6: [4] + 4 + 2 = 10 vs SG 8 → ERFOLG`

Der Plan sitzt. GHOST kennt den Moment — nicht die Sekunde, aber das Bild: Haas streckt die Hand aus, die Frau greift, ein Herzschlag wo beide Hände am Gegenstand sind. Dort.

---

Schritte auf dem Pflaster. Taborstraße-Seite.

Haas biegt in die Kleine Sperlgasse.

`Kodex: Szene 3 abgeschlossen. Kette bestätigt — Haas läuft. Übergabemoment in ca. 45 Sekunden. Alle Positionen gehalten. Tarnstatus: gehalten.`

---

**Die nächsten 45 Sekunden entscheiden alles.**

LEITER steht an der Theke im Café. Er weiß nicht, dass sein Kurier beobachtet wird — aber wenn Haas nicht zurückkommt, wird er es merken. Exfil-Fenster: T-02:24.

---

**Optionen:**

1. **STORM/GHOST — Zugriff im Übergabe-Moment:** GHOST nimmt die Frau, STORM nimmt Haas, exakt wenn beide Hände am Datenträger sind. Höchstes Risiko, höchste Präzision — einer patzt, der andere muss improvisieren.
2. **ECHO verlässt das Café und sichert LEITER:** Bevor LEITER merkt, dass Haas nicht zurückkommt — ECHO oder VEIL hält ihn an der Theke fest. Sozial, kein Lärm. Aber das Café bleibt dann unbeobachtet.
3. **RELAY als dritte Hand im Hinterhof:** RELAY kommt durch die Malzgasse rein und übernimmt die Frau, während GHOST und STORM sich Haas teilen. Drei Zugriffe gleichzeitig — sauberer, aber RELAY muss durch einen unbekannten Winkel.
4. **Freie Aktion** — eigene Koordination, andere Aufteilung, Psi-Einsatz, improvisierter Ansatz.

**Astra [Petra]:** Gruppe, LEITER ist drin — Signal bestätigt, Haas läuft. GHOST, STORM: Übergabe-Moment, exakt wenn beide Hände am Träger sind, nicht früher. VEIL, du bleibst auf LEITER an der Theke — sozial, kein Lärm, er darf das Café nicht verlassen bevor wir den Datenträger haben.

**Blitz [Marco]:** GHOST, ich bin bereit. Haas kommt rein, ich nehme ihn an der Einfahrt — sauber, lautlos, kein Spielraum. Du hast die Frau.

**Cipher [Lena]:** RELAY, bleib wo du bist — drei Zugriffe durch unbekannten Winkel bei 45 Sekunden Puffer ist zu viel Variable. STORM hat Haas, ich habe die Frau, das war der Plan und der bleibt.

**Dusk [Tarek]:** Gruppe, ich halte LEITER an der Theke — sozial, kein Lärm, er geht nicht durch diese Tür bevor wir den Datenträger haben. ECHO, Café bleibt dir, Auge auf den Ausgang.

**Echo [Sven]:** Verstanden, bleibe auf Position Malzgasse — Frau Westseite im Auge, Winkel zur Einfahrt frei. Wenn das Signal läuft das ich nicht gesehen habe, könnte sie früher reagieren als erwartet — GHOST, rechne damit dass sie sich bewegt bevor Haas die Mitte erreicht.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Szene 4 — Übergabe-Moment. Alle Positionen final. Zugriff läuft.`

`Kodex: Uhrzeit 21:15. Haas betritt Hinterhof. LEITER an der Theke. Countdown: Übergabe in ~20 Sekunden.`

---

**EP 12 · MS 11 · SC 04/12 · PHASE Konflikt · MODE CORE · COMMS OK**
`ECHO Lvl 912 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`STORM Lvl 905 · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 933 · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`VEIL Lvl 918 · LP 21/21 · Stress 0/10 · 👁️ Getarnt`
`RELAY Lvl 901 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`Obj: LEITER festnehmen + Datenträger sichern · Exfil: T-02:22`

---

## Hinterhof, Kleine Sperlgasse — 21:15 Uhr

Haas kommt durch die Einfahrt.

Er geht schnell, Schultern hochgezogen, die Schiebermütze tief. Zwölf Pflastersteine bis zur Mitte des Durchgangs. Er kennt den Weg — keine Zögerung, kein Blick zurück. Auf der Westseite löst die Frau sich vom Waschhaus-Vorsprung. Drei Schritte nach vorn, rechte Hand kommt unter dem Mantel.

Haas hebt die Hand. Kleine Bewegung, Handfläche nach oben.

*Jetzt.*

STORM tritt aus dem Schatten der Mauereinfahrt. Kein Lauf — ein gezielter Schritt, der Haas' Blickwinkel schneidet, bevor er reagieren kann. Die linke Hand landet flach auf Haas' Schulter, dreht ihn in die Mauer, die rechte sichert den Arm. Kein Wort. Haas macht einen Laut — halb Ausruf, halb Luft — und dann ist er an der Wand, Wange auf Stein, Arm auf dem Rücken.

**Probe: Nahkampf / Festhalten → STORM**
`Kodex: Probe-Template — 1W6 + ⌊STR 9/2⌋ + Feldroutine +1.`
`W6: [5] + 4 + 1 = 10 vs SG 7 → ERFOLG`

Haas zuckt einmal. STORM gibt nach — nicht los, sondern mit — lässt das Zucken ins Leere laufen und drückt dann nach. Haas hört auf zu zucken. Sein Atem geht stoßweise, Dampf in der Märzkälte.

Die Frau sieht es.

Sie dreht sich nicht zur Malzgasse. Sie dreht sich zum Waschhaus-Eingang — Reflex, trainiert, der kürzeste Weg raus ist nicht der Weg, den man gekommen ist.

Aber GHOST ist schon dort.

Er ist nicht gelaufen. Er ist einfach da, einen Schritt vor der Waschhaus-Tür, als wäre er immer dort gestanden. Die Frau bremst ab — ein halber Schritt, Sohle schabt auf Pflasterstein. Ihre rechte Hand hält das Rechteck noch. Zwischen ihr und GHOST sind zwei Meter.

Ihre Augen gehen einmal zu Haas an der Wand. Einmal zu GHOST. Einmal zur Malzgasse-Einfahrt, wo RELAY irgendwo im Dunkel steht.

Sie ist gut. Aber sie hat keine dritte Option.

**Probe: Einschüchterung / Druck → GHOST**
`Kodex: Probe-Template — 1W6 + ⌊GES 8/2⌋ + Veteranen-Reflex +2.`
`W6: [3] + 4 + 2 = 9 vs SG 8 → ERFOLG`

GHOST sagt nichts. Er hält den Blick. Die Stille im Hinterhof ist vollständig — kein Windgeräusch, kein Schritt, nur Haas' flaches Atmen an der Mauer.

Die Frau senkt langsam die Hand. Das Rechteck bleibt in ihrer Faust, aber die Faust öffnet sich — nicht ganz, aber genug. Eine Geste, die kein Geräusch macht und alles sagt.

`Kodex: Haas gesichert — STORM, Arm auf Rücken, keine Gegenwehr. Frau Westseite angehalten — GHOST, Druck gehalten, Datenträger in ihrer Hand, nicht übergeben. Tarnstatus: gehalten (kein Lärm, keine Zeugen).`

---

## Café Stefanie, gleichzeitig

LEITER steht an der Theke. Sein Glas ist halb leer. Er schaut zur Tür — einmal, zweimal. Haas hätte längst ein Signal zurückgeben sollen.

VEIL ist aufgestanden.

Nicht eilig. Die Bewegung eines Mannes, der seinen Kaffee bezahlt und sich streckt. Er geht zur Theke, stellt sich einen Platz neben LEITER, bestellt ein Wasser. Sein Ellbogen berührt fast den von LEITER. Fast.

*„Haas kommt nicht zurück,"* sagt VEIL auf Wienerisch, sehr leise, das Gesicht zur Theke gewandt. *„Und Sie werden jetzt ruhig hierbleiben, bis ich sage, dass wir gehen."*

**Probe: CHA / Einschüchterung → VEIL**
`Kodex: Probe-Template — 1W6 + ⌊CHA 8/2⌋ + Feldroutine +1.`
`W6: [6] + 4 + 1 = 11 — Exploding: W6: [2] = 13 vs SG 9 → ERFOLG (stark)`

LEITER setzt das Glas ab. Langsam. Seine Schultern gehen einen Millimeter nach unten — die Spannung eines Mannes, der kalkuliert und feststellt, dass die Rechnung nicht aufgeht. Er dreht den Kopf nicht zu VEIL. Er schaut geradeaus, auf die Flaschen hinter der Theke.

*„Wer schickt Sie?"* Flüstern, Wienerisch, ohne Betonung.

*„Jemand, dem der Datenträger gehört,"* sagt VEIL. *„Trinken Sie aus. Wir gehen durch den Hinterausgang."*

ECHO hat die Tür im Blick. Kein Kellner schaut rüber. Die zwei Frauen am Fenster reden. Niemand hat etwas gesehen.

`Kodex: LEITER unter Kontrolle — VEIL, soziale Festnahme, kein Lärm. Café-Status: unauffällig. Tarnstatus: gehalten.`

---

## Malzgasse, gleichzeitig

RELAY hört die Stille im Knochenleitungs-Funk und weiß, was sie bedeutet.

Er tritt einen Schritt zurück in den Schatten der Hauswand. Durch den Riss im Milchglas sieht er den Hinterhof — Haas an der Wand, die Frau mit gesenkter Hand, GHOST wie eine Zaunlatte zwischen ihr und dem Ausgang.

Sauber. Kein Schuss, kein Schrei.

Aber RELAY sieht noch etwas. An der Westseite, wo die Frau gestanden hat — auf dem Pflaster, neben der zergetretenen Zigarette — liegt ein kleines Gerät. Flach, dunkel, nicht größer als eine Streichholzschachtel. Kein Datenträger. Etwas anderes.

*„Gruppe,"* sagt RELAY ruhig. *„Westseite Waschhaus, Pflaster, direkt wo sie gestanden hat. Kleines Gerät, liegt da wie weggeworfen. Ich glaube, sie hat es fallen lassen als GHOST aufgetaucht ist. Könnte ein Sender sein."*

`Kodex: Unbekanntes Gerät — Westseite Pflaster, von Frau fallen gelassen. Klassifikation unklar: Sender, Kurzpuls-Funker, Totmann-Auslöser. Zeitfenster für Sicherung: offen.`

---

**Loot — vorläufig gesichert:**

- Datenträger (in Händen der Frau, noch nicht abgenommen) — KAIROS-Koordinaten, Inhalt unbekannt
- Haas — lebendig, gesichert, Verhör möglich
- LEITER — sozial festgenommen, Café-Hinterausgang
- Unbekanntes Gerät auf Pflaster — Sender? Auslöser? Zeitfenster offen

---

**Die nächsten zwei Minuten:**

Drei Personen unter Kontrolle, ein unbekanntes Gerät auf dem Pflaster, ein Exfil-Fenster das läuft. Die Frau hat den Datenträger noch. Das Gerät liegt ungesichert.

---

**Optionen:**

1. **Datenträger abnehmen + Gerät sichern** — GHOST nimmt der Frau den Träger ab, RELAY holt das Gerät vom Pflaster. Sofort, bevor ein Kurzpuls rausgeht. Risiko: Frau könnte bei Körperkontakt eskalieren.
2. **Gerät zuerst** — RELAY sichert das Gerät bevor jemand den Datenträger anfasst. Wenn es ein Totmann-Auslöser ist, hat das Vorrang. Risiko: Frau nutzt die Sekunde.
3. **Verhör vor Ort — Haas oder die Frau** — wer ist sie, was sendet das Gerät, wo ist das Depot. Dreißig Sekunden, kein Lärm. Bonus-Ziel läuft mit.
4. **Freie Aktion** — eigene Priorität, Aufgabentausch, Psi-Einsatz.

**Astra [Petra]:** Gruppe, RELAY sichert das Gerät — sofort, bevor ein Puls rausgeht. GHOST, Datenträger in derselben Sekunde, keine Pause dazwischen. Wenn sie eskaliert hast du sie bereits.

**Blitz [Marco]:** RELAY, ich habe die Frau — Träger kommt jetzt. Geh auf das Gerät.

**Cipher [Lena]:** RELAY, Gerät hat Vorrang — wenn das ein Totmann ist läuft der Puls sobald sie weiß dass es vorbei ist. Datenträger nehme ich gleichzeitig, sie hat keine dritte Hand.

**Dusk [Tarek]:** Gruppe, ich bin bei LEITER — er geht durch den Hinterausgang, ruhig, kein Aufmerksamkeit. ECHO, halte die Tür im Blick bis wir draußen sind.

**Echo [Sven]:** Gruppe, ich gehe auf das Gerät — jetzt. GHOST, Datenträger gleichzeitig, sie hat keine Sekunde dazwischen. Wenn das ein Totmann ist, läuft der Puls nicht.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Szene 4 — Simultanzugriff. Gerät + Datenträger + LEITER gleichzeitig. Uhr läuft.`

`Kodex: Uhrzeit 21:16. Exfil: T-02:21.`

---

**EP 12 · MS 11 · SC 04/12 · PHASE Konflikt · MODE CORE · COMMS OK**
`ECHO Lvl 912 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`STORM Lvl 905 · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 933 · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`VEIL Lvl 918 · LP 21/21 · Stress 0/10 · 👁️ Getarnt`
`RELAY Lvl 901 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`Obj: LEITER festnehmen + Datenträger sichern · Exfil: T-02:21`

---

## Hinterhof, Kleine Sperlgasse — 21:16 Uhr

Drei Aktionen. Eine Sekunde.

RELAY kommt durch die Malzgasse-Einfahrt im Laufschritt — nicht schnell, aber direkt, kein Zögern. Er geht nicht auf die Frau zu. Er geht am Pflaster vorbei, knie kurz, Hand schließt sich um das Gerät. Kalt, glatt, schwerer als erwartet.

**Probe: GES / Schnellzugriff → RELAY**
`Kodex: Probe-Template — 1W6 + ⌊GES 6/2⌋ + Feldroutine +1.`
`W6: [4] + 3 + 1 = 8 vs SG 7 → ERFOLG`

Das Gerät ist in seiner Manteltasche bevor die Frau den Kopf dreht.

`Kodex: Gerät gesichert — RELAY. Klassifikation noch unklar, kein Puls registriert. Totmann-Hypothese: offen.`

In derselben Sekunde macht GHOST einen halben Schritt vor. Nicht auf die Frau — *zwischen* sie und die Waschhaus-Tür, näher, der Raum zwischen ihnen wird kleiner ohne dass er die Hand hebt. Seine Stimme kommt ruhig und ohne Betonung, auf Wienerisch, als würde er die Uhrzeit ansagen.

*„Die Hand. Aufmachen."*

Die Frau schaut ihn an. Schaut zu STORM, der Haas an der Wand hält. Schaut zur Malzgasse, wo RELAY jetzt aufrecht steht mit der Hand in der Tasche.

Ihre Faust öffnet sich.

**Probe: Nahkampf / kontrollierte Abnahme → GHOST**
`Kodex: Probe-Template — 1W6 + ⌊GES 8/2⌋ + Veteranen-Reflex +2.`
`W6: [5] + 4 + 2 = 11 vs SG 8 → ERFOLG`

GHOST nimmt den Datenträger aus ihrer offenen Hand. Kein Reißen, kein Griff — er nimmt ihn einfach, als gehörte er ihm. Die Frau lässt es geschehen. Ihre Augen sind leer auf eine Art, die nicht Aufgabe bedeutet, sondern Berechnung.

*Sie wartet auf etwas.*

`Kodex: Datenträger gesichert — GHOST. Format: flacher Metallzylinder, ca. 4 cm, unbekanntes Verschlusssystem. Frau: kooperativ, aber Haltung nicht gebrochen — Achtung.`

---

## Café Stefanie, Hinterausgang — gleichzeitig

LEITER geht. Nicht weil er will — weil VEIL die Geometrie des Raums so gesetzt hat, dass Nichtstun teurer wäre als Mitgehen. Sein Glas steht halb leer auf der Theke. Der Kellner schaut nicht rüber.

ECHO hält die Innentür im Blick. Zwei Gäste haben aufgeblickt als VEIL und LEITER aufgestanden sind — kurzer Blick, dann zurück zu ihren Gesprächen. Nichts Auffälliges. Ein Mann und sein Bekannter, die früh gehen.

Der Hinterausgang führt in einen engen Durchgang zwischen Café und Nachbarhaus. Feuchte Ziegelwände, eine Mülltonne, eine Gaslaterne die flackert. LEITER bleibt stehen sobald die Tür hinter ihnen zufällt.

Er dreht sich um. Schaut VEIL an, dann ECHO. Keine Panik. Keine Gegenwehr.

*„Ihr seid nicht Wiener Polizei,"* sagt er. Feststellung, keine Frage. *„Und ihr seid nicht KAIROS."*

Er schaut auf seine Hände, als würde er etwas abwägen.

*„Ich rede. Aber nicht hier."*

`Kodex: LEITER kooperationsbereit — stellt Bedingung: Ortswechsel. Motiv unklar. Tarnstatus: gehalten.`

---

## Hinterhof — eine Sekunde später

Die Frau spricht. Leise, Deutsch mit einem Akzent den GHOST nicht sofort einordnen kann — nicht Wienerisch, nicht Berlinerisch.

*„Das Gerät, das Ihr Kollege genommen hat."* Kein Blick zu RELAY. *„Es ist kein Sender."*

Pause.

*„Es ist ein Empfänger. Und es hat bereits empfangen."*

`Kodex: ⚠ Frau — Aussage: Gerät ist Empfänger, nicht Sender. Signal bereits eingegangen. Inhalt unbekannt. Zeitpunkt unbekannt. Implikation: KAIROS weiß möglicherweise, dass die Übergabe kompromittiert ist.`

---

**Loot — gesichert:**

- ✓ Datenträger (Metallzylinder, verschlossen) — bei GHOST
- ✓ Unbekanntes Gerät (Empfänger laut Frau) — bei RELAY
- ✓ Haas — gesichert, STORM, Verhör möglich
- ✓ Frau — angehalten, GHOST, redet
- ✓ LEITER — kooperationsbereit, VEIL/ECHO, stellt Bedingung

---

**Drei offene Fäden, ein Exfil-Fenster:**

LEITER will reden — aber nicht im Durchgang. Die Frau hat gerade gesagt, dass KAIROS möglicherweise bereits weiß, was hier passiert ist. Und Haas an der Wand hat noch kein Wort gesagt.

Exfil-Fenster: T-02:19. Der Insertion Anchor in der Alten Börse ist neun Gehminuten entfernt.

---

**Optionen:**

1. **Verhör sofort, hier** — dreißig Sekunden, Frau oder Haas, was weiß KAIROS, was hat der Empfänger empfangen. LEITER wartet. Risiko: jede Minute im Hinterhof ist eine Minute weniger Puffer.
2. **Bewegung zum Anker, Verhör unterwegs** — alle fünf Personen in Bewegung, LEITER redet während ihr geht, Frau und Haas gesichert mit. Risiko: fünf Personen durch Wien 1938 in SA-Nächten ist sichtbar.
3. **Datenträger öffnen — GHOST oder ECHO** — was ist darauf, bevor ihr ihn mitnehmt. Wenn die Koordinaten schon kompromittiert sind, ändert das die Priorität. Risiko: unbekanntes Verschlusssystem, könnte sich löschen.
4. **Freie Aktion** — eigene Priorität, Psi-Einsatz, Aufgabenteilung.

**Astra [Petra]:** Gruppe, der Empfänger hat bereits empfangen — das ist unsere dringlichste Variable. RELAY, sichere das Gerät, aber aktiviere nichts. Frau kommt mit, Haas kommt mit, wir reden während wir gehen — Verhör unterwegs, Bewegung jetzt. LEITER bekommt seinen Ortswechsel, aber wir bestimmen die Route.

**Blitz [Marco]:** Gruppe, wir bewegen uns — jetzt. Haas, Frau, LEITER alle mit, Verhör läuft unterwegs. Ich gehe vorne, RELAY schließt hinten ab.

**Cipher [Lena]:** Gruppe, Empfänger bleibt unberührt bis wir beim Anker sind — ich öffne nichts ohne Werkzeug und Zeit. Frau kommt direkt neben mir, sie redet während wir gehen.

**Dusk [Tarek]:** Gruppe, LEITER bekommt seinen Ortswechsel — wir gehen zur Alten Börse, er redet unterwegs. Ich bleibe direkt neben ihm, ECHO deckt hinten. Wenn er stockt, stoppen wir.

**Echo [Sven]:** Gruppe, Empfänger geht in die Innentasche — ich fasse ihn nicht nochmal an bis wir beim Anker sind. Schließe hinten ab, halte Abstand zur Gruppe — fünf Personen wirken weniger wie eine Gruppe wenn der letzte zwanzig Meter zurückliegt. Gebt mir Bescheid wenn LEITER stockt.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Szene 5 — Bewegung zur Alten Börse. Verhör unterwegs. Alle drei Ziele in Bewegung.`

`Kodex: Uhrzeit 21:17. Neun Gehminuten zum Anker. Exfil: T-02:20.`

---

**EP 12 · MS 11 · SC 05/12 · PHASE Konflikt · MODE CORE · COMMS OK**
`ECHO Lvl 912 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`STORM Lvl 905 · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 933 · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`VEIL Lvl 918 · LP 21/21 · Stress 0/10 · 👁️ Getarnt`
`RELAY Lvl 901 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`Obj: LEITER festnehmen + Datenträger sichern · Exfil: T-02:20`

---

## Wien, Leopoldstadt — 21:17 Uhr

Die Gruppe löst sich aus dem Hinterhof wie Wasser aus einem Riss — langsam, ohne Geräusch, in die Nacht hinein.

STORM hat Haas am Arm. Nicht grob, von außen sieht es aus wie zwei Männer, die denselben Weg gehen. Haas geht mit. Er ist klug genug, um zu wissen, wann eine Situation entschieden ist.

Die Frau geht neben GHOST. Sie hat kein Wort mehr gesagt seit dem Hinweis auf den Empfänger. Ihr Blick geht geradeaus, die Hände vor dem Körper, der Mantel geschlossen. GHOST hält einen halben Schritt Abstand — nah genug, weit genug.

VEIL hat LEITER. Schulter an Schulter, langsames Tempo, das Gespräch beginnt noch in der Kleinen Sperlgasse.

*„Wo ist das Depot?"* fragt VEIL, ohne ihn anzuschauen.

LEITER antwortet nicht sofort. Er geht drei Schritte, schaut auf den Gehsteig.

*„Ich kenne den Standort nicht."* Pause. *„Ich kenne die Epoche."*

*„Welche?"*

*„Frühe Bronzezeit. Anatolien."* Er sagt es wie jemand, der etwas abgibt, das er nicht mehr braucht. *„Das war alles, was mir mitgeteilt wurde. Der Datenträger enthält die genauen Koordinaten — die kenne ich selbst nicht. Das war Sicherheitsprotokoll."*

`Kodex: LEITER — Intel-Fragment: Depot in Früher Bronzezeit, Anatolien. Koordinaten nur auf Datenträger. Aussage plausibel als Sicherheitsprotokoll.`

---

## Taborstraße — 21:19 Uhr

Die Straße ist breiter, heller, gefährlicher.

Ein Lastwagen mit Scheinwerfern rollt langsam in Richtung Praterstern. Auf der anderen Seite stehen vier Männer mit Armbinden unter einer Gaslaterne — reden, rauchen, schauen. Einer dreht den Kopf als die Gruppe die Straße quert.

**Probe: Gruppenverhalten / Tarnung unter Beobachtung → VEIL**
`Kodex: Probe-Template — 1W6 + ⌊CHA 8/2⌋ + Feldroutine +1.`
`W6: [3] + 4 + 1 = 8 vs SG 8 → ERFOLG (knapp)`

VEIL sagt halblaut etwas zu LEITER — ein Satz über das Wetter, über die Sperrstunde, irgendwas Gleichgültiges. LEITER antwortet. Zwei Männer im Gespräch. Die vier unter der Laterne schauen noch eine Sekunde, dann wendet sich einer wieder seinen Kameraden zu.

ECHO, zwanzig Meter dahinter, geht an der Hauswand. Er sieht es. Er sagt nichts.

`Kodex: Tarnstatus — gehalten. Beobachtung nicht eskaliert. Heat: 0.`

---

## Währenddessen — die Frau redet

GHOST hat sie nicht gefragt. Sie fängt trotzdem an.

*„Das Gerät hat eine Nachricht empfangen — vor ungefähr vier Minuten."* Ihr Deutsch ist präzise, der Akzent osteuropäisch, vielleicht polnisch. *„Ich weiß nicht, was darin stand. Ich sollte es erst nach der Übergabe öffnen."*

GHOST schaut geradeaus. *„Wer hat gesendet?"*

*„Protokoll-Name: MERIDIAN."* Sie zögert einen Herzschlag. *„Das ist kein Name, den ich kenne. Das ist ein Name, den ich noch nie gehört habe. Das macht mir mehr Sorgen als Sie."*

`Kodex: ⚠ MERIDIAN — unbekannter Protokoll-Name, Absender der Empfänger-Nachricht. Nicht im ITI-Archiv-Abruf vorhanden. Neue KAIROS-Zelle oder externer Akteur. Priorität: hoch.`

---

## Wipplingerstraße — 21:23 Uhr

Das Fundamentgewölbe der Alten Börse liegt vier Minuten entfernt. Die Straße ist ruhiger hier — Behördengebäude, geschlossene Büros, kein SA-Aufmarsch.

Haas hat die ganze Zeit geschwiegen. Jetzt, ohne dass jemand ihn fragt, sagt er etwas.

*„Haas"* — er spricht über sich selbst in der dritten Person, leise, ohne STORM anzuschauen — *„ist nicht der einzige Kurier heute Nacht."*

STORM hält den Schritt nicht an. Aber seine Hand am Arm von Haas wird eine Spur fester.

*„Wie viele?"*

*„Drei,"* sagt Haas. *„Drei Routen. Drei Datenträger. Nur einer ist echt."*

Die Stille danach dauert genau so lange, wie es braucht, um zu verstehen, was das bedeutet.

`Kodex: ⚠ Haas — Intel: drei parallele Kurier-Routen heute Nacht. Nur ein Datenträger ist echt. Aktuelle Sicherstellung möglicherweise Ablenkung. Verifizierung erforderlich.`

---

**Lage — 21:23 Uhr, vier Minuten zum Anker:**

Drei neue Variablen in vier Minuten Fußweg.

LEITER kennt die Epoche, aber nicht die Koordinaten — die sitzen auf dem Träger.
MERIDIAN hat vor vier Minuten eine Nachricht gesendet — Inhalt unbekannt, Absender unbekannt.
Haas sagt, es gibt drei Datenträger. Nur einer ist echt.

Der Träger bei GHOST könnte der echte sein. Oder einer der anderen beiden ist der echte, und dieser hier ist Ablenkung — und irgendwo in Wien laufen gerade zwei weitere Kuriere.

Exfil-Fenster: T-02:14.

---

**Optionen:**

1. **Weiter zum Anker — alles mitnehmen, Auswertung in der Nullzeit.** Datenträger, Empfänger, alle drei Personen. Was Haas sagt, klärt sich im ITI-Labor. Risiko: wenn die anderen Träger Wien verlassen, sind sie weg.
2. **Haas ausquetschen — jetzt, vier Minuten stehen bleiben.** Wo sind die anderen zwei Kuriere, welche Route, wer trägt was. Risiko: vier Minuten weniger Puffer, und MERIDIAN weiß möglicherweise bereits, dass hier etwas schiefgelaufen ist.
3. **Gruppe teilen — STORM und RELAY suchen die anderen Kuriere, Rest zum Anker.** Mehr Abdeckung, weniger Sicherheit. Wien 1938, zwei ITI-Operatoren allein in der Nacht, keine Exfil-Garantie wenn das Fenster schließt.
4. **Freie Aktion** — eigene Priorität, Psi-Einsatz, andere Lösung.

**Astra [Petra]:** Gruppe, Haas redet — das kostet uns nichts außer Atem. Drei Träger bedeutet, der echte könnte bereits in Bewegung sein, aber ohne Routeninfo können wir nichts tun außer weitergehen. STORM, lass ihn reden, Schritt halten — ich will Namen, Treffpunkte, Übergabezeit, alles was er hat, bevor wir den Anker erreichen. Teilen kommt nicht in Frage.

**Blitz [Marco]:** Haas, Namen. Jetzt. Die anderen zwei Kuriere — wo treffen sie ab, wann, wen.

**Cipher [Lena]:** Gruppe, ich greife den Empfänger nicht an — aber ich will wissen, wann genau die Nachricht von MERIDIAN eingegangen ist, auf die Minute. Frau, exakt vier Minuten vor 21:23 — das wäre 21:19. Taborstraße. Während wir beobachtet wurden.

**Dusk [Tarek]:** Gruppe, LEITER hat die Koordinaten nicht — das glaube ich ihm, Sicherheitsprotokoll ist sauber. Wir brauchen den Träger intakt beim Anker, alles andere läuft daneben. Option zwei fällt weg, vier Minuten Stillstand sind zu teuer wenn MERIDIAN bereits weiß, dass hier etwas nicht stimmt.

**Echo [Sven]:** Gruppe, wenn MERIDIAN um 21:19 gesendet hat — genau in dem Moment, als wir beobachtet wurden — dann weiß jemand, dass die Übergabe nicht stattgefunden hat. Wir haben kein Zeitpolster mehr für Stillstand. Weiter zum Anker, Haas redet unterwegs — alles was er hat, Schritt halten.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Szene 5 — Verhör in Bewegung. Haas redet. Uhrzeit 21:23. Anker in vier Minuten.`

`Kodex: MERIDIAN-Signal 21:19 bestätigt — Timing-Korrelation mit Taborstraße-Beobachtung. Kein Zeitpolster mehr.`

---

**EP 12 · MS 11 · SC 05/12 · PHASE Konflikt · MODE CORE · COMMS OK**
`ECHO Lvl 912 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`STORM Lvl 905 · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 933 · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`VEIL Lvl 918 · LP 21/21 · Stress 0/10 · 👁️ Getarnt`
`RELAY Lvl 901 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`Obj: LEITER festnehmen + Datenträger sichern · Exfil: T-02:14`

---

## Wipplingerstraße — 21:23 Uhr, vier Minuten zum Anker

Die Gruppe geht. Sieben Personen auf einem Wiener Gehsteig im März 1938, aufgeteilt wie Perlen auf einer Schnur — STORM und Haas vorne, GHOST und die Frau in der Mitte, VEIL und LEITER dahinter, ECHO zwanzig Meter im Rücken. Von außen: Nachtspaziergänger, Bürger, niemand der auffällt.

Von innen: eine Verhörszene, die läuft.

STORM hält Haas am Arm und stellt keine Frage zweimal.

*„Namen. Routen. Jetzt."*

Haas geht drei Schritte. Atmet aus.

*„Zweiter Kurier heißt Brenner. Kein Vorname, das ist alles was ich habe. Trifft seinen Kontakt um 21:45 am Praterstern — Nordausgang, dritte Bank von links. Ich weiß nicht, was er trägt."*

*„Dritter?"*

*„Den kenne ich nicht. Drei Routen, ich kannte nur meine und einen Namen von der zweiten. So läuft das bei KAIROS — niemand weiß genug, um alles zu verraten."*

**Probe: INT / Glaubwürdigkeitsanalyse → ECHO (Knochenleitung)**
`Kodex: Probe-Template — 1W6 + ⌊INT 7/2⌋ + Feldroutine +1.`
`W6: [4] + 3 + 1 = 8 vs SG 7 → ERFOLG`

*„Gruppe,"* sagt ECHO leise von hinten, *„er lügt nicht — aber er lässt etwas aus. Die Pause vor 'Brenner' war zu kurz. Den Namen kennt er gut."*

`Kodex: Haas — Intel: Zweiter Kurier BRENNER, Praterstern Nordausgang 21:45. Dritter Kurier unbekannt. Glaubwürdigkeits-Flag: Brenner-Verbindung enger als angegeben.`

---

## Gleichzeitig — die Frau, zwei Schritte hinter STORM

GHOST stellt die Frage, die CIPHER gestellt hat.

*„21:19. Taborstraße. Was hat MERIDIAN gesendet?"*

Die Frau schaut geradeaus. Der Akzent kommt wieder — polnisch, bestimmt jetzt.

*„Ich habe es nicht geöffnet. Das war nicht mein Auftrag."*

*„Aber ihr Gerät hat empfangen."*

*„Ja."*

*„Und Sie wissen trotzdem, dass 21:19 der Zeitpunkt war."*

Eine Sekunde. Zwei.

*„Weil ich auf das Signal gewartet habe,"* sagt sie schließlich. *„MERIDIAN sendet immer wenn eine Route kompromittiert wird. Das ist kein Befehlssignal. Das ist ein Warnsignal."*

Die Pflastersteine unter ihren Füßen klingen anders — Hohlraum darunter, alte Kanalisation, der Untergrund der Stadt der seit Jahrhunderten weiterläuft.

*„Wenn MERIDIAN um 21:19 gesendet hat,"* sagt sie, *„dann wusste jemand um 21:19, dass Ihre Gruppe in Wien ist. Nicht dass die Übergabe gescheitert ist — dass Sie hier sind."*

`Kodex: ⚠ MERIDIAN-Signal ist Routing-Warnung, kein Befehl. Auslöser: Crew-Präsenz erkannt, nicht Übergabe-Scheitern. Implikation: KAIROS hat unabhängige Beobachtung in Wien — nicht nur Haas und die Frau.`

---

## Wipplingerstraße 34 — 21:25 Uhr

Das Eingangsportal der Alten Börse liegt dreißig Meter entfernt. Neoklassizistische Fassade, schwere Steinsäulen, das Gebäude wirkt tagsüber geschäftsmäßig — nachts wie ein Grabmal.

ECHO sieht es zuerst.

Auf der gegenüberliegenden Straßenseite, unter einem Torbogen, steht ein Mann. Stehkragen, dunkler Mantel. Schaut nicht zur Gruppe. Schaut zur Börsenfassade.

Er schaut genau dorthin, wo der Kellereingang liegt.

**Probe: Wahrnehmung → ECHO**
`Kodex: Probe-Template — 1W6 + ⌊INT 7/2⌋ + Veteranen-Reflex +2.`
`W6: [6] + 3 + 2 = 11 — Exploding: W6: [1] = 12 vs SG 8 → ERFOLG`

Der Mann hat kein Interesse an der Börse als Gebäude. Sein Gewicht ist auf dem rechten Fuß — jemand der wartet, nicht jemand der zufällig steht. Und seine rechte Hand ist in der Manteltasche auf eine Art, die ECHO aus hundert Einsätzen kennt.

Bewaffnet. Wartet. Schaut auf den Kellereingang.

*„Gruppe,"* sagt ECHO, Stimme vollkommen ruhig, *„wir haben einen Empfang. Torbogen gegenüber Börsenfassade. Bewaffnet, wartet auf uns."*

`Kodex: ⚠ Unbekannter Beobachter — Torbogen Wipplingerstraße, Blick auf IA-Kellereingang. Bewaffnet. KAIROS-Vorposten wahrscheinlich. Tarnstatus: gefährdet wenn Gruppe direkt auf Eingang zugeht.`

`Kodex: Exfil-Fenster T-02:12. Anker dreißig Meter entfernt. Zugang kompromittiert.`

---

**Lagebild 21:25 Uhr:**

Der Anker ist dreißig Meter entfernt und bewacht. MERIDIAN hat die Crew-Präsenz um 21:19 gemeldet — vier Minuten bevor sie hier ankamen, genug Zeit für einen Vorposten. Brenner trifft seinen Kontakt in zwanzig Minuten am Praterstern. Die dritte Route ist unbekannt.

Sieben Personen auf der Straße, einer davon bewaffnet und wartet auf sie.

---

**Optionen:**

1. **Ablenkung — VEIL oder ECHO zieht den Vorposten weg** vom Eingang, während der Rest die Gruppe durch den Kellereingang bringt. Sozial oder physisch — ein Zwischenfall auf der Straße, ein falscher Alarm, ein gezielter Kontakt.
2. **Direkter Zugriff — STORM oder GHOST schaltet den Vorposten aus** bevor er reagieren kann. Schnell, lautlos wenn es klappt, laut wenn nicht. Der Torbogen gibt Deckung für einen Angreifer.
3. **Alternativer Eingang suchen** — die Alte Börse hat mehr als einen Zugang. Dreißig Sekunden Umweg, aber kein direkter Konflikt am IA. Risiko: unbekannte Zugangssituation.
4. **Freie Aktion** — eigene Lösung, Psi-Einsatz, Aufgabenteilung, Haas oder die Frau als Werkzeug einsetzen.

**Astra [Petra]:** Gruppe, Ablenkung — ich übernehme den Torbogen. VEIL, du folgst mir mit dreißig Sekunden Abstand, hältst den Kellereingang im Blick. STORM bringt die anderen rein sobald der Mann sich dreht.

**Blitz [Marco]:** Gruppe, ich mach den Vorposten. Torbogen, dreißig Sekunden, gebt mir Sichtzeichen wenn Astra ihn dreht — dann geht alles rein.

**Cipher [Lena]:** Gruppe, der Mann im Torbogen schaut auf den Eingang — nicht auf die Straße. Wenn Astra ihn dreht, habe ich drei Sekunden Fenster bevor er wieder Sichtlinie hat. Ich brauche das Sichtzeichen auf meinem linken Kanal, nicht Knochen — ich bin zu nah dran für Verzögerung.

**Dusk [Tarek]:** Gruppe, ich bin hinter LEITER — bleibe dort bis Astra den Mann dreht, dann bringe ich die beiden als letzte rein. Sichtzeichen von mir wenn wir durch sind.

**Echo [Sven]:** Gruppe, ich bin Rückendeckung — sobald STORM und die anderen im Eingang verschwinden, mache ich den Abschluss und sichere die Tür von innen. Astra, du hast grünes Licht wenn du bereit bist.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Szene 6 — Ablenkungsmanöver Torbogen. ECHO übernimmt Vorposten. Koordination läuft.`

`Kodex: Uhrzeit 21:25. Exfil: T-02:12. Kellereingang 30 Meter.`

---

**EP 12 · MS 11 · SC 06/12 · PHASE Exfil · MODE CORE · COMMS OK**
`ECHO Lvl 912 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`STORM Lvl 905 · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 933 · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`VEIL Lvl 918 · LP 21/21 · Stress 0/10 · 👁️ Getarnt`
`RELAY Lvl 901 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`Obj: LEITER festnehmen ✓ · Datenträger sichern ✓ · Exfil: T-02:12`

---

## Wipplingerstraße — 21:25 Uhr, dreißig Meter zum Anker

ECHO löst sich aus der Gruppe.

Keine Eile. Dieselbe Bewegung wie jemand, der seinen Abendspaziergang beendet und die Straßenseite wechselt. Sie geht diagonal über das Pflaster, Absätze gleichmäßig, Mantel geschlossen. In der linken Hand hält sie nichts. In der rechten hält sie nichts. Sie sieht aus wie jemand, der nach Hause geht.

Der Mann im Torbogen bemerkt sie, als sie noch fünfzehn Meter entfernt ist. Sein Gewicht verlagert sich — von rechts nach links, eine kleine Bewegung, die bedeutet: *ich habe dich gesehen*.

ECHO geht weiter.

**Probe: CHA / Soziale Täuschung → ECHO**
`Kodex: Probe-Template — 1W6 + ⌊CHA 5/2⌋ + Veteranen-Reflex +2.`
`W6: [5] + 2 + 2 = 9 vs SG 8 → ERFOLG`

Sie stolpert. Nicht viel — ein halber Schritt, die Schuhspitze an einer Pflasterunebenheit, eine Bewegung die jeder macht und niemand plant. Ihre Hand geht reflexartig an die Hauswand des Torbogengebäudes. Direkt neben dem Mann.

*„Entschuldigung,"* sagt sie auf Wienerisch, atemlos, *„diese verdammten Steine —"*

Der Mann dreht sich. Instinkt, Höflichkeit, es spielt keine Rolle — er dreht sich zur Frau, die sich an seine Hauswand stützt, und für drei Sekunden hat er keinen Blick auf den Kellereingang.

Drei Sekunden.

`Kodex: Vorposten abgelenkt — Sichtlinie Kellereingang unterbrochen. Fenster: 3 Sekunden. Signal auf linkem Kanal: JETZT.`

---

GHOST hat das Signal.

Sie ist bereits in Bewegung — nicht Laufen, ein schneller ruhiger Schritt, der keine Geräusche macht. STORM hat Haas. Die Frau geht zwischen ihnen. VEIL schiebt LEITER sanft aber bestimmt vorwärts.

Die Kellertreppe liegt hinter einer schmalen Eisentür, halb unter dem Straßenniveau, zwischen zwei Säulenbasen versteckt. GHOST hat die Tür in zwei Sekunden offen — kein Schloss, ein Riegel, der sich von außen hebt wenn man weiß wo man drückt.

**Probe: GES / Schnellzugriff → GHOST**
`Kodex: Probe-Template — 1W6 + ⌊GES 8/2⌋ + Feldroutine +1.`
`W6: [3] + 4 + 1 = 8 vs SG 6 → ERFOLG`

Die Tür schwingt auf. Kalksteingeruch, Dunkel, das Summen das ECHO schon beim Ankommen gespürt hat — tiefer jetzt, näher. Der Anker ist aktiv.

STORM zuerst mit Haas. Die Frau. VEIL mit LEITER. RELAY als vorletzter, Empfänger fest in der Innentasche.

---

Im Torbogen dreht der Mann den Kopf zurück zur Börsenfassade.

Der Kellereingang ist leer.

Er sieht nichts. Niemand. Eine leere Straße unter Gaslampen.

ECHO löst sich von der Hauswand, nickt ihm kurz zu — *nochmals Entschuldigung* — und geht die drei Stufen hinunter. Die Eisentür fällt hinter ihr ins Schloss.

`Kodex: Gruppe im Kellereingang. Tarnstatus: gehalten. Vorposten nicht alarmiert.`

---

## Fundamentgewölbe der Alten Börse — 21:26 Uhr

Der Kalkstein schluckt das Geräusch der Straße sofort. Hier unten ist Wien 1938 nur noch ein Vibrieren in den Wänden — Lastwagen, Schritte, der ferne Lautsprecherwagen.

Der Anker liegt in der Mitte des Gewölbes. Keine sichtbare Technik — nur ein Bereich des Bodens der anders aussieht, als wäre der Stein dort älter als der Rest, als hätte sich etwas in das Fundament eingeschrieben das vor dem Gebäude da war. Das Summen kommt von dort.

RELAY zieht das Handfeld aus der Innentasche. Drei Taps. Das Rücksprung-Protokoll läuft.

*„Armierung in neunzig Sekunden,"* sagt er.

Haas schaut auf den Boden. Die Frau schaut auf den Anker. LEITER schaut auf nichts — er hat Augen für das Innere seiner eigenen Überlegungen.

Dann sagt LEITER etwas.

*„MERIDIAN ist kein Name."* Leise, fast für sich. *„Das ist eine Funktion. Eine Rolle. Wer auch immer MERIDIAN gerade ist — das wechselt. Wie ein Amt."*

Er schaut auf. Direkt zu ECHO.

*„Ich habe MERIDIAN einmal getroffen. Vor drei Jahren. Damals war es eine Frau."* Eine Pause. *„Sie war ITI."*

`Kodex: ⚠ MERIDIAN ist eine Funktion, kein Eigenname — rollierende Besetzung. Letzte bekannte Inkarnation: Frau, ITI-Zugehörigkeit, vor 3 Jahren. Implikation: mögliche ITI-Infiltration durch KAIROS. Priorität: kritisch.`

`Kodex: Rücksprung-Armierung läuft. T-01:30 bis Fenster.`

---

**Loot — gesichert:**

- ✓ Datenträger (Metallzylinder) — GHOST
- ✓ Empfänger-Gerät — RELAY
- ✓ LEITER — kooperativ, kritisches Intel geliefert
- ✓ Haas — gesichert, Verhör abgeschlossen
- ✓ Frau (unbekannt) — angehalten, Verhör teilweise
- ⚠ Brenner — Praterstern 21:45, ungesichert
- ⚠ Dritter Kurier — unbekannt, ungesichert
- ⚠ MERIDIAN — Funktion, ITI-Infiltration möglich

---

**Neunzig Sekunden bis Rücksprung.**

LEITER hat gerade die gefährlichste Information des Abends geliefert — ruhig, fast beiläufig, als wäre es eine Kleinigkeit. Jemand im ITI ist oder war MERIDIAN. Der Empfänger in RELAYs Tasche enthält eine Nachricht, die für diese Person bestimmt war.

Und Brenner trifft seinen Kontakt in neunzehn Minuten am Praterstern — ohne dass jemand von euch dort ist.

---

**Optionen:**

1. **Rücksprung jetzt — alle mit.** Datenträger, Empfänger, alle drei Personen in die Nullzeit. Was Haas und LEITER wissen, wird im ITI ausgewertet. Brenner verliert sich, dritter Kurier verliert sich — aber MERIDIAN-Intel ist zu wichtig um zu riskieren.
2. **STORM oder RELAY bleibt zurück — Praterstern.** Neunzehn Minuten bis 21:45, Praterstern ist erreichbar. Einer bleibt, identifiziert Brenner, versucht den zweiten Träger zu sichern. Kein Exfil-Fenster für diese Person bis zum nächsten Armierungs-Zyklus — vier Stunden, allein in Wien 1938.
3. **Empfänger öffnen — jetzt, vor dem Rücksprung.** Neunzig Sekunden sind genug für einen Blick. Was hat MERIDIAN gesendet, und an wen im ITI geht diese Nachricht. Risiko: unbekanntes Gerät, könnte sich löschen.
4. **Freie Aktion** — eigene Priorität, letzte Fragen, Psi-Einsatz, andere Lösung.

**Astra [Petra]:** Gruppe, MERIDIAN ist eine Funktion — das bedeutet die Nachricht im Empfänger hat eine Adresse, keinen Namen. Wir öffnen das Gerät jetzt, RELAY, dreißig Sekunden, danach Rücksprung mit allen. Brenner ist ein Verlust den wir tragen.

**Blitz [Marco]:** Gruppe, MERIDIAN im ITI — das ist ein Feuer das wir nicht löschen können wenn wir jetzt blind rausgehen. Astra hat recht, der Empfänger kommt zuerst. RELAY, mach es auf, ich stehe daneben falls das Ding Probleme macht.

**Cipher [Lena]:** Gruppe, ich habe das Gerät gescannt — keine sichtbare Selbstlösch-Mechanik, aber ich erkenne das Protokoll nicht. Dreißig Sekunden sind ein Risiko. RELAY, wenn du es öffnest, mache ich parallel eine Spiegelung auf meinen Träger — falls es sich löscht, haben wir noch eine Kopie.

**Dusk [Tarek]:** Gruppe, dreißig Sekunden und eine Spiegelung — das ist vertretbar. Cipher, starte die Spiegelung parallel, RELAY öffnet. Danach Rücksprung mit allem was wir haben — Brenner ist weg, aber ein MERIDIAN im ITI ist keine Nachricht die wir ungelesen mitnehmen.

**Echo [Sven]:** Gruppe, Spiegelung läuft — Cipher, ich halte das Gerät ruhig, du hast den Kontakt. Öffne jetzt.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Empfänger-Öffnung initiiert. GHOST hält. RELAY öffnet. Spiegelung auf GHOST-Träger parallel.`

`Kodex: Rücksprung-Armierung T-00:67. Dreißig Sekunden Fenster.`

---

**EP 12 · MS 11 · SC 06/12 · PHASE Exfil · MODE CORE · COMMS OK**
`ECHO Lvl 912 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`STORM Lvl 905 · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 933 · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`VEIL Lvl 918 · LP 21/21 · Stress 0/10 · 👁️ Getarnt`
`RELAY Lvl 901 · LP 20/20 · Stress 0/10 · 👁️ Getarnt`
`Obj: LEITER festnehmen ✓ · Datenträger sichern ✓ · Exfil: T-01:07`

---

## Fundamentgewölbe, Alte Börse — 21:26 Uhr

RELAY legt das Gerät flach auf den Kalksteinboden. GHOST kniet daneben, Handfeld aufgeklappt, Verbindungskabel zwischen Gerät und Träger — die Spiegelung läuft, ein stiller Balken auf dem Display, der sich füllt.

RELAY findet die Öffnung in vier Sekunden. Kein Schloss — eine Druckmechanik, zwei Punkte gleichzeitig, die man kennen muss um sie zu finden. Er hat sie gefunden, weil er dreißig Minuten lang durch einen Milchglas-Riss auf das Gerät geschaut hat und die Art wie die Frau es gehalten hat genau das verraten hat.

Das Gerät öffnet sich.

**Probe: INT / Technik-Analyse → RELAY**
`Kodex: Probe-Template — 1W6 + ⌊INT 7/2⌋ + Feldroutine +1.`
`W6: [6] + 3 + 1 = 10 — Exploding: W6: [4] = 14 vs SG 9 → ERFOLG (stark)`

Innen: kein Display, kein Bildschirm. Ein Streifen Thermopapier, maschinell bedruckt, zwölf Zeilen. Deutsch. Präzise. Kein Absender-Name — nur ein Protokoll-Kürzel oben rechts: **MRD-7**.

RELAY liest. Einmal, schnell. Dann nochmal.

Er sagt nichts für drei Sekunden.

*„Gruppe,"* sagt er dann, *„das ist kein Operationsbefehl. Das ist eine Warnung."*

Er liest vor, flach und ohne Betonung, als würde er eine Wettermeldung vorlesen.

*„— Übergabe Wien kompromittiert. Crew-Identitäten bekannt. Rückfall auf Depot-Protokoll Sekundär. Ankerpunkt Anatolien bleibt aktiv. Primärer Träger ist Ablenkung. Echter Träger läuft über Route Drei. Bestätigt durch Beobachter vor Ort. — MRD-7."*

Die Stille danach hat ein Gewicht.

`Kodex: ⚠ Empfänger-Inhalt — Warnung MRD-7: Primärer Träger (bei GHOST) ist Ablenkung. Echter Träger auf Route Drei. Crew-Identitäten KAIROS bekannt. Anatolien-Depot aktiv. Beobachter vor Ort bestätigt.`

GHOST schaut auf den Metallzylinder in seiner Hand.

Die Spiegelung ist zu neunzig Prozent abgeschlossen.

LEITER sagt nichts. Aber seine Hände, die bisher ruhig waren, haben sich zu Fäusten geschlossen — nicht aus Aggression. Aus etwas, das wie Erleichterung aussieht. Als hätte er gewusst, dass dieser Moment kommt, und als wäre er froh, dass er jetzt da ist und nicht später.

*„Ich habe euch den Datenträger nicht gegeben,"* sagt er leise. *„Ich habe euch die Ablenkung gegeben. Das war mein Auftrag."*

Er schaut zu ECHO.

*„Ich bin nicht KAIROS-Kurier. Ich bin KAIROS-Gegenoperation. Meine Aufgabe war, eure Gruppe zu binden — während Route Drei läuft."*

`Kodex: ⚠ LEITER — Identität revidiert. Kein KAIROS-Kurier. KAIROS-interne Gegenoperation — Bindungs-Agent, Ziel: Crew-Kapazität absorbieren während echter Träger Route Drei läuft. Glaubwürdigkeit: hoch (konsistent mit Verhör-Verhalten, MERIDIAN-Hinweis, Kooperationsbereitschaft).`

`Kodex: Spiegelung abgeschlossen. MRD-7-Inhalt auf GHOST-Träger gesichert.`

`Kodex: Rücksprung-Armierung T-00:38.`

---

Die Frau schaut auf LEITER. Kein Überraschungsausdruck. Sie hat es gewusst.

Haas schaut auf den Boden. Er hat es nicht gewusst — und das ist vielleicht das Einzige, das an diesem Abend wahr war.

Achtunddreißig Sekunden bis Rücksprung. Route Drei läuft irgendwo in Wien. Brenner trifft seinen Kontakt in neunzehn Minuten am Praterstern — und jetzt ist die Frage nicht mehr ob Brenner der echte Träger ist.

Die Frage ist: wer ist Route Drei.

---

**Loot — finaler Stand vor Rücksprung:**

- ✓ Datenträger (Ablenkung, leer oder Köder) — GHOST
- ✓ Empfänger MRD-7 + Spiegelung — RELAY / GHOST
- ✓ LEITER (Bindungs-Agent, kooperativ, weiteres Intel möglich) — VEIL
- ✓ Haas (unwissender Kurier, Verhör abgeschlossen) — STORM
- ✓ Frau (unbekannt, wusste von LEITER-Rolle) — GHOST
- ⚠ Route Drei — unbekannt, echter Träger, läuft jetzt
- ⚠ Beobachter vor Ort — unidentifiziert, Crew-Identitäten kompromittiert

---

**Achtunddreißig Sekunden.**

**Optionen:**

1. **Rücksprung jetzt — alle mit, Route Drei als Folgemission.** Was heute Nacht verloren geht, ist in der Nullzeit auswertbar. LEITER weiß mehr — im ITI-Verhörraum, mit Zeit und Werkzeug, kommt mehr raus als in dreißig Sekunden Keller.
2. **LEITER jetzt ausquetschen — Route Drei, wer ist sie, wo.** Zwanzig Sekunden, harter Druck. Er ist kooperativ — aber wie kooperativ, wenn es seinen eigenen Auftraggeber betrifft.
3. **Frau befragen — sie wusste von LEITER.** Wenn sie von der Bindungs-Operation wusste, weiß sie vielleicht auch von Route Drei. Zwanzig Sekunden, anderer Winkel.
4. **Freie Aktion** — eigene Priorität, Psi-Einsatz, letzter Zug vor dem Rücksprung.

**Astra [Petra]:** Gruppe, Rücksprung jetzt — LEITER kommt mit, er redet im ITI weiter. Route Drei ist in neunzehn Minuten am Praterstern, das ist Brenners Zeitfenster — wir geben das als Hot-Intel an Führung, die entscheiden ob jemand hinkommt. Wir haben alles was wir in dreißig Sekunden nicht kriegen.

**Blitz [Marco]:** Gruppe, LEITER kommt mit — er redet im ITI. Rücksprung jetzt, Route Drei ist Führungs-Problem.

**Cipher [Lena]:** Gruppe, Rücksprung. Spiegelung ist gesichert, MRD-7 ist auf meinem Träger — das reicht für die Auswertung. LEITER redet im ITI, die Frau auch.

**Dusk [Tarek]:** Gruppe, Rücksprung — aber die Frau kommt mit. Sie wusste von der Bindungs-Operation, das ist kein Zufall. Route Drei klären wir im ITI, nicht hier.

**Echo [Sven]:** Gruppe, bestätigt — Rücksprung, alle mit, Frau und LEITER beide. Dreißig Sekunden reichen nicht für das, was sie wissen. Ich sichere die Geräte und schließe nach.

**Eingabe [M1-5er]:** [Crew-Eingaben]

### [M1-5er] SL

`Kodex: Rücksprung-Armierung T-00:18. Alle bestätigt. Gruppe plus drei Personen auf dem Anker.`

`Kodex: LEITER, Haas, Frau — alle drei in Rücksprung eingeschlossen.`

---

## Fundamentgewölbe, Alte Börse — 21:26 Uhr, letzte Sekunden

RELAY tippt die Bestätigung. Das Summen im Boden wird tiefer — nicht lauter, tiefer, als würde der Kalkstein selbst einen Atemzug nehmen.

ECHO sichert den Empfänger in der Innentasche. Den Metallzylinder. Die Spiegelung auf GHOSTs Träger. Drei Geräte, alle weg von den Händen der Frau, alle weg von LEITER.

STORM hat Haas am Arm. Haas schaut auf den Boden. Er weiß, dass sein Abend gerade sehr lang geworden ist.

Die Frau steht still. Sie hat nicht versucht zu fliehen, nicht versucht zu reden, nicht versucht irgendetwas zu tun — seit dem Moment, als GHOST ihr den Empfänger abgenommen hat, ist sie in eine Art ruhige Neutralität geglitten, die mehr aussagt als Widerstand. *Sie wartet auf etwas. Sie wartet immer auf etwas.*

VEIL steht neben LEITER. LEITER hat die Hände in den Manteltaschen. Er schaut auf den Bereich des Bodens, wo der Stein anders aussieht, und sein Gesicht trägt den Ausdruck eines Mannes, der eine lange Reise hinter sich hat und noch eine vor sich weiß.

*„Route Drei,"* sagt er leise, nicht zu jemandem Bestimmtem, *„ist nicht Brenner."*

Er sagt es wie jemand, der eine Tür aufmacht und dann wartet, bis jemand durchgeht.

Niemand antwortet. Das Summen wird stärker.

*„Route Drei war nie ein Mensch."*

`Kodex: Rücksprung T-00:05.`

---

Das Gewölbe löst sich auf.

Nicht dramatisch — es ist eher wie wenn ein Bild scharf wird, rückwärts. Die Kalksteinwände werden unscharf, das Gaslampen-Gelb verblasst, das Vibrieren der Straße über ihnen hört auf. Was bleibt ist ein Moment vollständiger Stille — kein Wien, kein 1938, kein Lastwagen, kein Lautsprecherwagen.

Dann Nullzeit.

`Kodex: Rücksprung abgeschlossen. Debrief läuft.`

---

**EP 12 · MS 11 · SC --/-- · PHASE Debrief · MODE CORE · COMMS OK**
`ECHO Lvl 912 ▓▓▓▓▓▓▓▓▓▓ · Px 3/5 · Stress 0/10`
`STORM Lvl 905 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`GHOST Lvl 933 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`VEIL Lvl 918 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`
`RELAY Lvl 901 ▓▓▓▓▓▓▓▓▓▓ · Stress 0/10`

---

## ITI-Nullzeit — Empfangsdeck, 21:27 Uhr (Nullzeit)

Der Sprung-Gate-Techniker sieht sieben Personen, wo er fünf erwartet hat. Er sagt nichts — er hat in diesem Job gelernt, dass Fragen meistens beantwortet werden, wenn man wartet.

Medizinisches Personal ist in dreißig Sekunden da. Sicherheitsdienst in vierzig. LEITER, Haas und die Frau werden getrennt und in Aufnahmezellen geführt — ruhig, kein Widerstand, alle drei wissen, wie das läuft.

Das Empfangsdeck riecht nach Ozon und kaltem Metall. Über dem Gate-Display läuft die Nullzeit-Uhr. Irgendwo im Hangar-Flügel startet eine Wartungssequenz — das rhythmische Klicken, das nach Jahren im ITI zum Schlafrhythmus gehört.

Ihr seid zurück.

---

**Score-Screen — MS 11**

*Hauptziel:* LEITER festnehmen + Datenträger sichern — ✓ Erfüllt *(Datenträger ist Ablenkung, aber physisch gesichert und für Auswertung vorhanden)*

*Opt.:* LEITER verhören, verwertbarer Koordinaten-Hinweis — ✓ Erfüllt *(Epoche: Frühe Bronzezeit, Anatolien; MERIDIAN-Funktion aufgedeckt; LEITER als Bindungs-Agent identifiziert)*

*Bonus:* LEITERs Kontaktnetz dokumentieren — ✓ Erfüllt *(Haas gesichert, Frau gesichert, MRD-7-Empfänger mit Spiegelung)*

Bewertung: **Vollständig — alle Ziele erfüllt.**

`Kodex: CU-Auszahlung — Vollständig: 800 CU Basis + 200 CU Opt. + 150 CU Bonus = 1.150 CU. Aufgeteilt auf 5 Operatoren: je +230 CU.`

`Kodex: Wallet-Update — ECHO: 60.400 → 60.630 CU · STORM: 6.900 → 7.130 CU · GHOST: 8.100 → 8.330 CU · VEIL: 7.600 → 7.830 CU · RELAY: 7.050 → 7.280 CU`

`Gruppenkasse: 91.200 CU`

`Kodex: Lvl-Phase 1 — jede abgeschlossene Core-Mission = sofortiges Level-Up × 5 Operatoren.`

`Kodex: ECHO Lvl 912 → 913. STORM Lvl 905 → 906. GHOST Lvl 933 → 934. VEIL Lvl 918 → 919. RELAY Lvl 901 → 902. Aufstiegswahl ausstehend × 5.`

---

Der volle Belohnungs-Beat gehört heute Abend nicht dem Level-Up — das ist Routine auf dieser Dienstebene. Er gehört dem Intel.

Vargas wartet am Rand des Empfangsdecks. Er hat den Bericht schon halb gelesen, bevor VEIL ihm den Datenträger in die Hand gibt. Sein Gesicht verändert sich nicht — aber seine Hand, die den Träger hält, wird eine Spur fester.

*„MERIDIAN ist eine Funktion."* Er wiederholt es leise, als würde er es auf Wahrheit prüfen. *„Das bedeutet, wir suchen nicht nach einem Namen. Wir suchen nach einer Rolle."*

Er schaut auf. Direkt zu ECHO.

*„Und LEITER sagt, Route Drei war nie ein Mensch."*

Pause.

*„Das geht heute Nacht noch zu Renier."*

`Kodex: ITI-Ruf — Cap 5 bereits erreicht. Kein Anstieg. Rang: Operator IX gehalten.`

`Kodex: Px-Kadenz — ECHO TEMP 6, VEIL TEMP 6 → +2 Px diese Mission. Px 3 → 5.`

---

**Px-Resonanz — Payoff**

Die Techniker am Holotisch in der Ecke des Empfangsdecks arbeiten seit drei Minuten still. Jetzt hebt einer die Hand.

*„Wir haben etwas."*

Der Holotisch zieht ein Bild. Koordinaten, eine Raumzeitkarte, ein Sektor der bisher leer war. Dann — ein Signal. Schwach, aber da. Eine Signatur die der Klassifikations-Algorithmus mit einem einzigen Wort markiert.

*Anomalie.*

*„Resonanz-Schwelle erreicht,"* sagt der Techniker. *„Wien hat die Zeitlinie stabilisiert — genug, dass wir jetzt sehen können, was wir vorher nicht sehen konnten."*

Er tippt. Die Koordinaten schärfen sich.

*„Sektor: Nordostküste, 1947. Kleiner Fischerort, Norwegen. Signatur: unklassifiziert — aber die Muster passen zu etwas Organischem. Etwas das sich bewegt."*

`Kodex: Resonanz-Schwelle erreicht (Px 5). ClusterCreate — 1 Rift-Seed geortet. Sektor: Norwegen, 1947. Signatur: organisch, mobil, unklassifiziert. Px-Reset: 5 → 0. Rift-Seed verfügbar nach Episodenabschluss.`

---

`Kodex: Research — keine laufenden Projekte. Tick: entfällt.`

`Kodex: Field-Decrypt — MRD-7-Inhalt gesichert (Spiegelung auf GHOST-Träger). Projekt angelegt: kind: field_decrypt · label: MRD-7-Analyse · missions_total: 2 · missions_done: 0 · status: in_progress · scope: campaign.`

*Analyse läuft — ~2 Einsätze bis Ergebnis. MERIDIAN-Funktion, Adressaten-Struktur, Protokoll-Herkunft.*

---

**Folgespuren — arc.hooks:**

- MERIDIAN ist eine Funktion, nicht ein Name — rollende Besetzung, letzte bekannte Inkarnation ITI-intern
- Route Drei war nie ein Mensch — LEITERs letzte Aussage vor dem Rücksprung, ungeklärt
- Brenner, Praterstern 21:45 — ungesichert, Wien 1938, möglicherweise mit echtem Träger entkommen
- Depot Frühe Bronzezeit, Anatolien — Koordinaten auf echtem Träger, Standort unbekannt
- Frau (unbekannt) — wusste von Bindungs-Operation, Akzent polnisch, Verhör steht aus
- Rift-Seed Norwegen 1947 — organische Signatur, nach Episodenabschluss spielbar

---

**Regie-Beat:**

Vargas geht. Renier wartet nicht gerne.

Im Hangar-Flügel hängt ein Aushang an der Pinnwand neben dem Duty-Desk — handgeschrieben, Standardpapier, die Schrift von jemand der zu wenig schläft: *„Wer in den letzten 72 Stunden im Zweiten Weltkrieg war: Medizin-Check Pflicht. Kein Ausnahme. — Med-Lab."*

Darunter, kleiner, andere Handschrift: *„Gilt auch für Wien."*

---

**Aufstiegswahl — fünf ausstehend**

Pro Operator genau eine Wahl: *+1 Attribut* · *Talent/Upgrade* · *+1 SYS*

Bitte für jeden Operator eine Wahl treffen — dann `!save`.

**ECHO (Astra):** STR 4 · GES 7 · INT 9 · CHA 5 · TEMP 6 · SYS 5 · Psi aktiv
**STORM (Blitz):** STR 9 · GES 8 · INT 4 · CHA 4 · TEMP 7 · SYS 3
**GHOST (Cipher):** STR 4 · GES 8 · INT 8 · CHA 5 · TEMP 5 · SYS 9
**VEIL (Dusk):** STR 5 · GES 7 · INT 6 · CHA 8 · TEMP 6 · SYS 4 · Psi aktiv
**RELAY (Echo):** STR 5 · GES 6 · INT 7 · CHA 6 · TEMP 5 · SYS 7

**Eingabe [M1-5er]:** [Save-Zwang 1/3]

### [M1-5er] SL

`Kodex: !save erkannt. HQ-Status bestätigt. Level-Up-Wahlen ausstehend × 5 — Save nach Wahl.`

`Kodex: Bitte zuerst Aufstiegswahl für alle fünf Operatoren treffen, dann wird der vollständige Save ausgegeben.`

---

Fünf Aufstiegswahlen stehen noch offen. Pro Operator genau **eine** Wahl — dann sofortiger `!save`-Export.

**ECHO (Astra)** — Analytik & Spurensicherung · Psi aktiv
STR 4 · GES 7 · INT 9 · CHA 5 · TEMP 6 · SYS 5/5
→ +1 Attribut · Talent/Upgrade · +1 SYS

**STORM (Blitz)** — CQB & Sturmangriff
STR 9 · GES 8 · INT 4 · CHA 4 · TEMP 7 · SYS 3/3
→ +1 Attribut · Talent/Upgrade · +1 SYS

**GHOST (Cipher)** — Infiltration & Hacking
STR 4 · GES 8 · INT 8 · CHA 5 · TEMP 5 · SYS 9/9
→ +1 Attribut · Talent/Upgrade · +1 SYS

**VEIL (Dusk)** — Verdeckte Aufklärung · Psi aktiv
STR 5 · GES 7 · INT 6 · CHA 8 · TEMP 6 · SYS 4/4
→ +1 Attribut · Talent/Upgrade · +1 SYS

**RELAY (Echo)** — Support & Feldtechnik
STR 5 · GES 6 · INT 7 · CHA 6 · TEMP 5 · SYS 7/7
→ +1 Attribut · Talent/Upgrade · +1 SYS

**Eingabe [M1-5er]:** [Save-Zwang 2/3]

### [M1-5er] SL

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP12-MS11-DEBRIEF-HQ",
  "parent_save_id": "SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "merge_id": null,
  "branch_id": "ANCHOR-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "campaign": {
    "episode": 12,
    "mission": 11,
    "px": 0,
    "px_state": "consumed",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [
      {
        "id": "RIFT-EP12-MS11-NOR1947",
        "sector": "Norwegen, 1947",
        "signature": "organisch, mobil, unklassifiziert",
        "available_after_episode": 12
      }
    ],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "ECHO",
      "rank": "Operator IX",
      "lvl": 913,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Analytik & Spurensicherung"
      },
      "attr": { "STR": 4, "GES": 7, "INT": 9, "CHA": 5, "TEMP": 6, "SYS": 5 },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 5,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Astra (ECHO) - erfahrener ITI-Operator, Rolle: Analytik & Spurensicherung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: LEITER als Bindungs-Agent enttarnt, MERIDIAN-Funktion aufgedeckt"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 60630,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "913": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      },
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        { "name": "Praekognitiver Blick", "tier": "Basis", "effect": "Einmal pro Szene eine Probe wiederholen." }
      ]
    },
    {
      "id": "AGENT-B",
      "name": "Blitz",
      "callsign": "STORM",
      "rank": "Operator IX",
      "lvl": 906,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "CQB & Sturmangriff"
      },
      "attr": { "STR": 9, "GES": 8, "INT": 4, "CHA": 4, "TEMP": 7, "SYS": 3 },
      "lp": 26,
      "lp_max": 26,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 3,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Blitz (STORM) - erfahrener ITI-Operator, Rolle: CQB & Sturmangriff.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: Haas gesichert, Verhör abgeschlossen"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7130,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "906": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      }
    },
    {
      "id": "AGENT-C",
      "name": "Cipher",
      "callsign": "GHOST",
      "rank": "Operator IX",
      "lvl": 934,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration & Hacking"
      },
      "attr": { "STR": 4, "GES": 8, "INT": 8, "CHA": 5, "TEMP": 5, "SYS": 9 },
      "lp": 19,
      "lp_max": 19,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Cipher (GHOST) - erfahrener ITI-Operator, Rolle: Infiltration & Hacking.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: Datenträger gesichert, MRD-7-Spiegelung auf Träger"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Datenträger (Ablenkung, Wien 1938)", "type": "gadget", "tier": 2 },
        { "name": "MRD-7-Spiegelung", "type": "gadget", "tier": 2 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 8330,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "934": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      }
    },
    {
      "id": "AGENT-D",
      "name": "Dusk",
      "callsign": "VEIL",
      "rank": "Operator IX",
      "lvl": 919,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Verdeckte Aufklaerung"
      },
      "attr": { "STR": 5, "GES": 7, "INT": 6, "CHA": 8, "TEMP": 6, "SYS": 4 },
      "lp": 21,
      "lp_max": 21,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 4,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Dusk (VEIL) - erfahrener ITI-Operator, Rolle: Verdeckte Aufklaerung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: LEITER sozial festgenommen, Wien 1938"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7830,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "919": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      },
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        { "name": "Praekognitiver Blick", "tier": "Basis", "effect": "Einmal pro Szene eine Probe wiederholen." }
      ]
    },
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "RELAY",
      "rank": "Operator IX",
      "lvl": 902,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Support & Feldtechnik"
      },
      "attr": { "STR": 5, "GES": 6, "INT": 7, "CHA": 6, "TEMP": 5, "SYS": 7 },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Echo (RELAY) - erfahrener ITI-Operator, Rolle: Support & Feldtechnik.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: MRD-7-Empfänger geöffnet und gesichert, Brenner-Intel gewonnen"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "MRD-7-Empfänger (original)", "type": "gadget", "tier": 2 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7280,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "902": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      }
    }
  ],
  "economy": {
    "wallets": {
      "AGENT-A": { "balance": 60630, "name": "Astra" },
      "AGENT-B": { "balance": 7130, "name": "Blitz" },
      "AGENT-C": { "balance": 8330, "name": "Cipher" },
      "AGENT-D": { "balance": 7830, "name": "Dusk" },
      "AGENT-E": { "balance": 7280, "name": "Echo" }
    }
  },
  "research": {
    "projects": [
      {
        "id": "RES-MRD7-EP12MS11",
        "kind": "field_decrypt",
        "label": "MRD-7-Analyse",
        "description": "MERIDIAN-Funktion, Adressaten-Struktur, Protokoll-Herkunft. Empfänger Wien 1938.",
        "status": "in_progress",
        "missions_total": 2,
        "missions_done": 0,
        "scope": "campaign"
      }
    ]
  },
  "logs": {
    "trace": [
      { "event": "economy_audit", "target_range": { "level_band": "900+" } },
      { "event": "mission_complete", "mission": "MS11", "epoch": "Wien 1938", "result": "vollstaendig" }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [
      "MS11: LEITER = Bindungs-Agent KAIROS, keine echten Depot-Koordinaten",
      "MS11: Primärer Datenträger ist Ablenkung — echter Träger Route Drei",
      "MS11: MERIDIAN ist Funktion/Amt, rollende Besetzung, letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren",
      "MS11: Route Drei war nie ein Mensch — LEITERs letzte Aussage vor Rücksprung, ungeklärt",
      "MS11: Brenner, Praterstern 21:45 Wien 1938 — ungesichert, möglicherweise entkommen",
      "MS11: Frau (unbekannt, Akzent polnisch) wusste von Bindungs-Operation — Verhör im ITI ausstehend",
      "MS11: Haas — unwissender Kurier, Verhör abgeschlossen",
      "MS11: MRD-7-Empfänger original bei RELAY, Spiegelung bei GHOST",
      "MS11: Px 3+2=5 → ClusterCreate — Rift-Seed Norwegen 1947 geortet, organische Signatur",
      "MS11: Px-Reset auf 0 nach ClusterCreate"
    ],
    "flags": {
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": [
        "level_history enthält nur MS1-Eintrag — Aufstiegs-Delta Lvl 2-912 nicht durch Einträge gedeckt (Import-Flag, narrativ akzeptiert)",
        "reputation.iti Importwert 80 über Cap 5 — auf 5 geclippt",
        "Level-Up-Wahlen MS11 ausstehend x5 — noch nicht persistiert"
      ],
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false
    },
    "hud": [],
    "psi": [],
    "arena_psi": []
  },
  "summaries": {
    "summary_last_episode": "Episode 12 abgeschlossen, HQ stabil.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; MERIDIAN-Funktion aufgedeckt; Route Drei ungeklärt; Chronopolis-Embargo"
  },
  "continuity": {
    "last_seen": { "mode": "hq", "episode": 12, "mission": 11, "location": "HQ" },
    "split": {
      "family_id": null,
      "thread_id": null,
      "expected_threads": [],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      { "char_id": "AGENT-A", "tone": "fokussiert", "text": "Astra/ECHO — Analytikerin, deckte MERIDIAN-Funktion auf, Psi aktiv." },
      { "char_id": "AGENT-B", "tone": "direkt", "text": "Blitz/STORM — CQB-Spezialist, sicherte Haas im Hinterhof Wien." },
      { "char_id": "AGENT-C", "tone": "präzise", "text": "Cipher/GHOST — Infiltration, sicherte Datenträger und MRD-7-Spiegelung." },
      { "char_id": "AGENT-D", "tone": "ruhig", "text": "Dusk/VEIL — Aufklärung, hielt LEITER sozial unter Kontrolle." },
      { "char_id": "AGENT-E", "tone": "analytisch", "text": "Echo/RELAY — Support, öffnete MRD-7-Empfänger, sicherte Brenner-Intel." }
    ],
    "shared_echoes": [
      { "tag": "meridian-funktion-ms11", "scope": "campaign", "text": "MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren." },
      { "tag": "route-drei-nichtmensch-ms11", "scope": "campaign", "text": "Route Drei war laut LEITER nie ein Mensch — Natur ungeklärt." },
      { "tag": "depot-anatolien-bronzezeit-ms11", "scope": "campaign", "text": "KAIROS-Depot: Frühe Bronzezeit, Anatolien — Koordinaten nur auf echtem Träger Route Drei." },
      { "tag": "brenner-praterstern-ms11", "scope": "campaign", "text": "Brenner, Praterstern Wien 21:45 März 1938 — ungesichert, möglicherweise mit echtem Träger entkommen." },
      { "tag": "frau-unbekannt-wien-ms11", "scope": "campaign", "text": "Unbekannte Frau (Akzent polnisch), wusste von LEITER-Bindungs-Operation — ITI-Verhör ausstehend." },
      { "tag": "rift-seed-norwegen-1947", "scope": "campaign", "text": "Rift-Seed geortet: Norwegen 1947, organische mobile Signatur — verfügbar nach Episodenabschluss." }
    ],
    "convergence_tags": [],
    "npc_roster": [
      { "id": "NPC-LEITER-MS11", "name": "LEITER", "callsign": "LEITER", "role": "KAIROS-Bindungs-Agent", "scope": "campaign", "status": "ITI-Gewahrsam", "last_seen": "ITI-Nullzeit, MS11-Debrief" },
      { "id": "NPC-HAAS-MS11", "name": "Haas", "callsign": "HAAS", "role": "KAIROS-Kurier (unwissend)", "scope": "episode", "status": "ITI-Gewahrsam", "last_seen": "ITI-Nullzeit, MS11-Debrief" },
      { "id": "NPC-FRAU-MS11", "name": "Unbekannte Frau", "callsign": "WESTSEITE", "role": "KAIROS-Kontakt Wien, wusste von Bindungs-Op", "scope": "campaign", "status": "ITI-Gewahrsam, Verhör ausstehend", "last_seen": "ITI-Nullzeit, MS11-Debrief" }
    ],
    "active_npc_ids": ["NPC-LEITER-MS11", "NPC-HAAS-MS11", "NPC-FRAU-MS11"]
  },
  "arc": {
    "factions": {
      "KAIROS": "Gegenoffensive aktiv — Bindungs-Operationen bestätigt, MERIDIAN-Funktion intern",
      "ITI": "Mögliche Infiltration durch MERIDIAN-Funktion — Renier informiert"
    },
    "questions": [
      "Wer ist aktuell MERIDIAN — welche ITI-Person besetzt die Funktion?",
      "Was ist Route Drei, wenn es kein Mensch ist?",
      "Wo befindet sich das KAIROS-Depot (Frühe Bronzezeit, Anatolien) genau?",
      "Hat Brenner den echten Träger aus Wien herausgebracht?"
    ],
    "hooks": [
      "MRD-7-Analyse läuft — 2 Missionen bis Ergebnis (MERIDIAN-Adressaten-Struktur)",
      "Frau unbekannt — Verhör im ITI, Akzent polnisch, wusste von Bindungs-Op",
      "LEITER — weiteres Verhör im ITI, kennt Epoche des Depots",
      "Rift-Seed Norwegen 1947 — nach Episodenabschluss spielbar",
      "Aufstiegswahlen x5 ausstehend — vor nächster Mission eintragen"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "action_mode": "uncut",
    "intro_seen": true,
    "dice": { "debug_rolls": true },
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "none",
    "tier": 0,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "low" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "standard"
  }
}
```

> ⚠️ **[M1-5er] SAVE-PROSE:** M1-5er: Save erst nach Eskalation als JSON

## 🗂 Split (5er teilt sich 3/2 am HQ-Sync-Punkt)


**Eingabe [SPLIT]:** [5er-Stand laden]

### [SPLIT] SL

`Kodex: Save v7 erkannt — Load-Flow initiiert.`

`Kodex: Session-Anker gesetzt: EP 12 · MS 11 · HQ-Kernbereich.`

`Kodex: Würfelschwellen-Check — 5 Charaktere.`

`Kodex: ECHO — GES 7 (W6), INT 9 (W6), TEMP 6 (W6), SYS 5 (W6). Alle Attribute < 11, Würfeltyp W6 durchgehend.`

`Kodex: STORM — STR 9 (W6), GES 8 (W6), TEMP 7 (W6). Alle Attribute < 11, Würfeltyp W6 durchgehend.`

`Kodex: GHOST — GES 8 (W6), INT 8 (W6), SYS 9 (W6). Alle Attribute < 11, Würfeltyp W6 durchgehend.`

`Kodex: VEIL — CHA 8 (W6), GES 7 (W6). Alle Attribute < 11, Würfeltyp W6 durchgehend.`

`Kodex: RELAY — INT 7 (W6), SYS 7 (W6). Alle Attribute < 11, Würfeltyp W6 durchgehend.`

`Kodex: Research — MRD-7-Analyse: 0/2 Einsätze. Status: in_progress.`

`Kodex: Level-Up-Wahlen x5 ausstehend (alle Charaktere, MS11). Vor nächster Mission eintragen.`

`Kodex: Px 0 · px_state: consumed. Heat 0. ITI-Ruf 5 (alle). Rift-Seed Norwegen 1947 verfügbar nach Episodenabschluss.`

---

## ZEITRISS · Kontinuitätsrückblick

**EP 12 · MS 11 abgeschlossen · HQ-Kernbereich**

---

### Crew-Stand

| Agent | Callsign | Lvl | Attr (höchste) | LP | Psi |
|---|---|---|---|---|---|
| Astra | ECHO | 913 | INT 9 / TEMP 6 | 20/20 | ✓ (PP 4) |
| Blitz | STORM | 906 | STR 9 / GES 8 | 26/26 | — |
| Cipher | GHOST | 934 | SYS 9 / GES 8 | 19/19 | — |
| Dusk | VEIL | 919 | CHA 8 / GES 7 | 21/21 | ✓ (PP 4) |
| Echo | RELAY | 902 | SYS 7 / INT 7 | 20/20 | — |

*Seit MS11 neu: Alle Charaktere tragen eine ausstehende Aufstiegswahl (Lvl 913/906/934/919/902).*

---

### Was ihr wisst — Fäden nach MS 11

Wien, März 1938. Ihr habt LEITER enttarnt: KAIROS-Bindungs-Agent, Deckname KAIROS-intern. Die Depot-Koordinaten, die er euch angeboten hat, waren eine Ablenkung — der echte Träger ist Route Drei, und Route Drei war laut LEITERs letzter Aussage **nie ein Mensch**.

GHOST trägt die MRD-7-Spiegelung. RELAY hat den Originalempfänger. Die Analyse läuft — zwei Einsätze bis Ergebnis, dann wisst ihr, wer MERIDIAN ist und wie die Adressatenstruktur aussieht.

**Offene Fäden:**
- *MERIDIAN* — eine Funktion, rollende Besetzung. Letzte bekannte Inkarnation: weiblich, ITI-intern, vor drei Jahren. Wer sitzt heute auf dem Stuhl?
- *Route Drei* — kein Mensch. Was dann?
- *Brenner, Praterstern Wien 21:45* — möglicherweise mit dem echten Träger entkommen. Ungesichert.
- *Frau unbekannt (Akzent polnisch)* — wusste von der Bindungs-Operation. Sitzt im ITI. Verhör steht aus.
- *KAIROS-Depot, frühe Bronzezeit, Anatolien* — Koordinaten nur auf dem echten Träger.

Das Rift-Fenster steht: **Norwegen, 1947** — organische, mobile Signatur. Spielbar nach Episodenabschluss.

---

### Ausstehend vor der nächsten Mission

Die fünf Aufstiegswahlen aus MS11 müssen eingetragen werden. Ihr könnt das jetzt im HQ erledigen, bevor ihr ins Briefing geht.

`Kodex: HQ-Stand stabil. Deepsave möglich.`

`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`

---

## HQ-Menü

Das Quarzatrium liegt ruhig. Durch die Glaswand über dem Operations-Deck sieht man die Raumzeitkarte — der neue Rift-Seed über dem Nordatlantik pulsiert schwach, noch gesperrt, aber da. Irgendwo in den Verhörzellen warten LEITER und die Frau ohne Namen auf ihre nächste Befragung.

**Was tut ihr?**

1. **Aufstiegswahlen** — alle fünf Charaktere leveln jetzt (vor Briefing empfohlen)
2. **HQ erkunden** — Verhöre, Quartiermeister, Med-Lab, Archiv
3. **Briefing** — MS 12, Episodenfinale vorbereiten
4. **Freie Aktion** — etwas anderes im HQ

**Eingabe [SPLIT]:** [3/2-Split + !save je Team]

### [SPLIT] SL

`Kodex: Split-Anfrage erkannt — Core-Parallelpfad mit family_id-Protokoll.`

`Kodex: Sync-Punkt aktiv. Zwei Threads — ALPHA (ECHO/STORM/GHOST) · BRAVO (VEIL/RELAY).`

`Kodex: Split passiert an HQ-Sync-Punkt. Regelkonform.` [1]

---

## Inworld-Übergabe — Vor dem Split

Commander Renier steht am Holotisch im Operations-Deck, die Raumzeitkarte hinter ihm auf halber Helligkeit. Er dreht sich nicht um, als ihr reinkommt — seine Augen laufen die zwei Fäden ab, die aus Wien herausragen wie Drähte aus einem aufgeschnittenen Kabel.

*„Zwei Spuren, eine Zeitlinie. Das ITI hat nicht die Kapazität, beide gleichzeitig sauber zu führen — also teilen wir."*

Er dreht sich um.

*„ECHO, STORM, GHOST — ihr geht dem MRD-7-Signal nach. Brenner ist möglicherweise draußen mit dem echten Träger. Wenn Route Drei kein Mensch ist, dann habt ihr keine Ahnung, was euch erwartet, und das ist der Grund, warum ich meinen besten Sturm-Mann mitnehme."*

Pause. Er sieht VEIL und RELAY an.

*„Ihr nehmt die Frau. Akzent polnisch, wusste von der Bindungs-Operation. Das ist kein Zufall — das ist jemand, der nah genug dran war, um zu wissen, was LEITER tat. Ich will wissen, von wem. Und ich will es, bevor KAIROS merkt, dass wir LEITER haben."*

Er legt zwei versiegelte Missionsträger auf den Tisch.

*„Sync jetzt. Dann getrennte Chats. Was ihr in eurem Thread wisst, wissen die anderen nicht — denkt daran."*

`Kodex: Split-Sync läuft. family_id gesetzt: SPLIT-EP12-MS12-WIEN. Thread ALPHA + Thread BRAVO.` [1]

`Kodex: Beide Threads zählen zusammen als eine Mission im Episoden-Counter (MS 12).` [1]

`Kodex: Px-Stand wird kopiert (px: 0, px_state: consumed) — kein Doppelgewinn möglich.` [1]

`Kodex: Aufstiegswahlen x5 noch ausstehend — in beiden Saves mitgeführt, vor Briefing eintragen.`

`Kodex: HQ-Stand stabil. Deepsave wird für beide Threads erzeugt.`

---

## THREAD ALPHA — ECHO · STORM · GHOST

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP12-MS12-SPLIT-ALPHA",
  "parent_save_id": "SAVE-2026-EP12-MS11-DEBRIEF-HQ",
  "merge_id": null,
  "branch_id": "ANCHOR-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "campaign": {
    "episode": 12,
    "mission": 11,
    "px": 0,
    "px_state": "consumed",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [
      {
        "id": "RIFT-EP12-MS11-NOR1947",
        "sector": "Norwegen, 1947",
        "signature": "organisch, mobil, unklassifiziert",
        "available_after_episode": 12
      }
    ],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "ECHO",
      "rank": "Operator IX",
      "lvl": 913,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Analytik & Spurensicherung"
      },
      "attr": { "STR": 4, "GES": 7, "INT": 9, "CHA": 5, "TEMP": 6, "SYS": 5 },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 5,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Astra (ECHO) - erfahrener ITI-Operator, Rolle: Analytik & Spurensicherung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: LEITER als Bindungs-Agent enttarnt, MERIDIAN-Funktion aufgedeckt",
          "MS12-Split: Thread ALPHA — Brenner-Spur / Route-Drei-Natur"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 60630,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "913": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      },
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        { "name": "Praekognitiver Blick", "tier": "Basis", "effect": "Einmal pro Szene eine Probe wiederholen." }
      ]
    },
    {
      "id": "AGENT-B",
      "name": "Blitz",
      "callsign": "STORM",
      "rank": "Operator IX",
      "lvl": 906,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "CQB & Sturmangriff"
      },
      "attr": { "STR": 9, "GES": 8, "INT": 4, "CHA": 4, "TEMP": 7, "SYS": 3 },
      "lp": 26,
      "lp_max": 26,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 3,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Blitz (STORM) - erfahrener ITI-Operator, Rolle: CQB & Sturmangriff.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: Haas gesichert, Verhör abgeschlossen",
          "MS12-Split: Thread ALPHA — Brenner-Spur / Route-Drei-Natur"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7130,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "906": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      }
    },
    {
      "id": "AGENT-C",
      "name": "Cipher",
      "callsign": "GHOST",
      "rank": "Operator IX",
      "lvl": 934,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration & Hacking"
      },
      "attr": { "STR": 4, "GES": 8, "INT": 8, "CHA": 5, "TEMP": 5, "SYS": 9 },
      "lp": 19,
      "lp_max": 19,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Cipher (GHOST) - erfahrener ITI-Operator, Rolle: Infiltration & Hacking.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: Datenträger gesichert, MRD-7-Spiegelung auf Träger",
          "MS12-Split: Thread ALPHA — Brenner-Spur / Route-Drei-Natur"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Datenträger (Ablenkung, Wien 1938)", "type": "gadget", "tier": 2 },
        { "name": "MRD-7-Spiegelung", "type": "gadget", "tier": 2 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 8330,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "934": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      }
    }
  ],
  "economy": {
    "wallets": {
      "AGENT-A": { "balance": 60630, "name": "Astra" },
      "AGENT-B": { "balance": 7130, "name": "Blitz" },
      "AGENT-C": { "balance": 8330, "name": "Cipher" }
    }
  },
  "research": {
    "projects": [
      {
        "id": "RES-MRD7-EP12MS11",
        "kind": "field_decrypt",
        "label": "MRD-7-Analyse",
        "description": "MERIDIAN-Funktion, Adressaten-Struktur, Protokoll-Herkunft. Empfänger Wien 1938.",
        "status": "in_progress",
        "missions_total": 2,
        "missions_done": 0,
        "scope": "campaign"
      }
    ]
  },
  "logs": {
    "trace": [
      { "event": "economy_audit", "target_range": { "level_band": "900+" } },
      { "event": "mission_complete", "mission": "MS11", "epoch": "Wien 1938", "result": "vollstaendig" },
      { "event": "split_created", "family_id": "SPLIT-EP12-MS12-WIEN", "thread_id": "ALPHA", "members": ["AGENT-A", "AGENT-B", "AGENT-C"] }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [
      "MS11: LEITER = Bindungs-Agent KAIROS, keine echten Depot-Koordinaten",
      "MS11: Primärer Datenträger ist Ablenkung — echter Träger Route Drei",
      "MS11: MERIDIAN ist Funktion/Amt, rollende Besetzung, letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren",
      "MS11: Route Drei war nie ein Mensch — LEITERs letzte Aussage vor Rücksprung, ungeklärt",
      "MS11: Brenner, Praterstern 21:45 Wien 1938 — ungesichert, möglicherweise entkommen",
      "MS11: Frau (unbekannt, Akzent polnisch) wusste von Bindungs-Operation — Verhör im ITI ausstehend",
      "MS11: Haas — unwissender Kurier, Verhör abgeschlossen",
      "MS11: MRD-7-Empfänger original bei RELAY (Thread BRAVO), Spiegelung bei GHOST (Thread ALPHA)",
      "MS12-ALPHA: Spur — Brenner + echter Träger. Route-Drei-Natur ungeklärt.",
      "SPLIT: Thread ALPHA trägt MRD-7-Spiegelung (GHOST). Originalempfänger bei BRAVO."
    ],
    "flags": {
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": [
        "level_history enthält nur MS1-Eintrag — Aufstiegs-Delta Lvl 2-912 nicht durch Einträge gedeckt (Import-Flag, narrativ akzeptiert)",
        "reputation.iti Importwert 80 über Cap 5 — auf 5 geclippt",
        "Level-Up-Wahlen MS11 ausstehend x3 (ALPHA-Thread) — noch nicht persistiert"
      ],
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false
    },
    "hud": [],
    "psi": [],
    "arena_psi": []
  },
  "summaries": {
    "summary_last_episode": "Episode 12 MS11 abgeschlossen. Split MS12: ALPHA verfolgt Brenner-Spur und Route-Drei-Natur.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; MERIDIAN-Funktion aufgedeckt; Route Drei ungeklärt; Brenner möglicherweise entkommen mit echtem Träger; ALPHA-Thread aktiv"
  },
  "continuity": {
    "last_seen": { "mode": "hq", "episode": 12, "mission": 11, "location": "HQ" },
    "split": {
      "family_id": "SPLIT-EP12-MS12-WIEN",
      "thread_id": "ALPHA",
      "expected_threads": ["ALPHA", "BRAVO"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      { "char_id": "AGENT-A", "tone": "fokussiert", "text": "Astra/ECHO — Analytikerin, deckte MERIDIAN-Funktion auf, Psi aktiv. Thread ALPHA." },
      { "char_id": "AGENT-B", "tone": "direkt", "text": "Blitz/STORM — CQB-Spezialist, sicherte Haas. Thread ALPHA." },
      { "char_id": "AGENT-C", "tone": "präzise", "text": "Cipher/GHOST — Infiltration, trägt MRD-7-Spiegelung. Thread ALPHA." }
    ],
    "shared_echoes": [
      { "tag": "meridian-funktion-ms11", "scope": "campaign", "text": "MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren." },
      { "tag": "route-drei-nichtmensch-ms11", "scope": "campaign", "text": "Route Drei war laut LEITER nie ein Mensch — Natur ungeklärt." },
      { "tag": "depot-anatolien-bronzezeit-ms11", "scope": "campaign", "text": "KAIROS-Depot: Frühe Bronzezeit, Anatolien — Koordinaten nur auf echtem Träger Route Drei." },
      { "tag": "brenner-praterstern-ms11", "scope": "campaign", "text": "Brenner, Praterstern Wien 21:45 März 1938 — ungesichert, möglicherweise mit echtem Träger entkommen." },
      { "tag": "frau-unbekannt-wien-ms11", "scope": "campaign", "text": "Unbekannte Frau (Akzent polnisch), wusste von LEITER-Bindungs-Operation — ITI-Verhör ausstehend. Bei Thread BRAVO." },
      { "tag": "rift-seed-norwegen-1947", "scope": "campaign", "text": "Rift-Seed geortet: Norwegen 1947, organische mobile Signatur — verfügbar nach Episodenabschluss." },
      { "tag": "split-ms12-alpha-spur", "scope": "shared", "text": "Thread ALPHA: Brenner-Spur + Route-Drei-Natur. GHOST trägt MRD-7-Spiegelung." }
    ],
    "convergence_tags": [],
    "npc_roster": [
      { "id": "NPC-LEITER-MS11", "name": "LEITER", "callsign": "LEITER", "role": "KAIROS-Bindungs-Agent", "scope": "campaign", "status": "ITI-Gewahrsam", "last_seen": "ITI-Nullzeit, MS11-Debrief" },
      { "id": "NPC-HAAS-MS11", "name": "Haas", "callsign": "HAAS", "role": "KAIROS-Kurier (unwissend)", "scope": "episode", "status": "ITI-Gewahrsam", "last_seen": "ITI-Nullzeit, MS11-Debrief" },
      { "id": "NPC-FRAU-MS11", "name": "Unbekannte Frau", "callsign": "WESTSEITE", "role": "KAIROS-Kontakt Wien, wusste von Bindungs-Op", "scope": "campaign", "status": "ITI-Gewahrsam, Verhör bei BRAVO", "last_seen": "ITI-Nullzeit, MS11-Debrief" }
    ],
    "active_npc_ids": ["NPC-LEITER-MS11", "NPC-HAAS-MS11", "NPC-FRAU-MS11"]
  },
  "arc": {
    "factions": {
      "KAIROS": "Gegenoffensive aktiv — Bindungs-Operationen bestätigt, MERIDIAN-Funktion intern",
      "ITI": "Mögliche Infiltration durch MERIDIAN-Funktion — Renier informiert"
    },
    "questions": [
      "Wer ist aktuell MERIDIAN — welche ITI-Person besetzt die Funktion?",
      "Was ist Route Drei, wenn es kein Mensch ist?",
      "Wo befindet sich das KAIROS-Depot (Frühe Bronzezeit, Anatolien) genau?",
      "Hat Brenner den echten Träger aus Wien herausgebracht?"
    ],
    "hooks": [
      "MRD-7-Analyse läuft — 2 Missionen bis Ergebnis (MERIDIAN-Adressaten-Struktur)",
      "Brenner-Spur: Praterstern Wien 1938 — ALPHA-Thread",
      "Route-Drei-Natur ungeklärt — ALPHA-Thread",
      "Frau unbekannt — Verhör im ITI, BRAVO-Thread",
      "LEITER — weiteres Verhör im ITI, kennt Epoche des Depots",
      "Rift-Seed Norwegen 1947 — nach Episodenabschluss spielbar",
      "Aufstiegswahlen x3 ausstehend (ALPHA) — vor nächster Mission eintragen"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "action_mode": "uncut",
    "intro_seen": true,
    "dice": { "debug_rolls": true },
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "none",
    "tier": 0,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "low" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "standard"
  }
}
```

---

## THREAD BRAVO — VEIL · RELAY

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP12-MS12-SPLIT-BRAVO",
  "parent_save_id": "SAVE-2026-EP12-MS11-DEBRIEF-HQ",
  "merge_id": null,
  "branch_id": "ANCHOR-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "campaign": {
    "episode": 12,
    "mission": 11,
    "px": 0,
    "px_state": "consumed",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [
      {
        "id": "RIFT-EP12-MS11-NOR1947",
        "sector": "Norwegen, 1947",
        "signature": "organisch, mobil, unklassifiziert",
        "available_after_episode": 12
      }
    ],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-D",
      "name": "Dusk",
      "callsign": "VEIL",
      "rank": "Operator IX",
      "lvl": 919,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Verdeckte Aufklaerung"
      },
      "attr": { "STR": 5, "GES": 7, "INT": 6, "CHA": 8, "TEMP": 6, "SYS": 4 },
      "lp": 21,
      "lp_max": 21,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 4,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Dusk (VEIL) - erfahrener ITI-Operator, Rolle: Verdeckte Aufklaerung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: LEITER sozial festgenommen, Wien 1938",
          "MS12-Split: Thread BRAVO — Verhör Frau unbekannt (WESTSEITE)"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7830,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "919": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      },
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        { "name": "Praekognitiver Blick", "tier": "Basis", "effect": "Einmal pro Szene eine Probe wiederholen." }
      ]
    },
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "RELAY",
      "rank": "Operator IX",
      "lvl": 902,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Support & Feldtechnik"
      },
      "attr": { "STR": 5, "GES": 6, "INT": 7, "CHA": 6, "TEMP": 5, "SYS": 7 },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        { "name": "Veteranen-Reflex", "tier": "Meister", "effect": "+2 auf Initiative und Reaktionsproben." },
        { "name": "Feldroutine", "tier": "Fortgeschritten", "effect": "+1 auf rollentypische Proben." }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        { "name": "Neuro-Sync Mk III", "sys_cost": 1, "effect": "+1 Initiative" }
      ],
      "history": {
        "background": "Echo (RELAY) - erfahrener ITI-Operator, Rolle: Support & Feldtechnik.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: MRD-7-Empfänger geöffnet und gesichert, Brenner-Intel gewonnen",
          "MS12-Split: Thread BRAVO — Verhör Frau unbekannt (WESTSEITE), trägt MRD-7-Originalempfänger"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "MRD-7-Empfänger (original)", "type": "gadget", "tier": 2 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7280,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "902": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS11" }
      }
    }
  ],
  "economy": {
    "wallets": {
      "AGENT-D": { "balance": 7830, "name": "Dusk" },
      "AGENT-E": { "balance": 7280, "name": "Echo" }
    }
  },
  "research": {
    "projects": [
      {
        "id": "RES-MRD7-EP12MS11",
        "kind": "field_decrypt",
        "label": "MRD-7-Analyse",
        "description": "MERIDIAN-Funktion, Adressaten-Struktur, Protokoll-Herkunft. Empfänger Wien 1938.",
        "status": "in_progress",
        "missions_total": 2,
        "missions_done": 0,
        "scope": "campaign"
      }
    ]
  },
  "logs": {
    "trace": [
      { "event": "economy_audit", "target_range": { "level_band": "900+" } },
      { "event": "mission_complete", "mission": "MS11", "epoch": "Wien 1938", "result": "vollstaendig" },
      { "event": "split_created", "family_id": "SPLIT-EP12-MS12-WIEN", "thread_id": "BRAVO", "members": ["AGENT-D", "AGENT-E"] }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [
      "MS11: LEITER = Bindungs-Agent KAIROS, keine echten Depot-Koordinaten",
      "MS11: Primärer Datenträger ist Ablenkung — echter Träger Route Drei",
      "MS11: MERIDIAN ist Funktion/Amt, rollende Besetzung, letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren",
      "MS11: Route Drei war nie ein Mensch — LEITERs letzte Aussage vor Rücksprung, ungeklärt",
      "MS11: Brenner, Praterstern 21:45 Wien 1938 — ungesichert, möglicherweise entkommen",
      "MS11: Frau (unbekannt, Akzent polnisch) wusste von Bindungs-Operation — Verhör im ITI ausstehend",
      "MS11: Haas — unwissender Kurier, Verhör abgeschlossen",
      "MS11: MRD-7-Empfänger original bei RELAY (Thread BRAVO), Spiegelung bei GHOST (Thread ALPHA)",
      "MS12-BRAVO: Spur — Verhör WESTSEITE. Was weiß sie über LEITER und MERIDIAN?",
      "SPLIT: Thread BRAVO trägt MRD-7-Originalempfänger (RELAY). Spiegelung bei ALPHA."
    ],
    "flags": {
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": [
        "level_history enthält nur MS1-Eintrag — Aufstiegs-Delta Lvl 2-912 nicht durch Einträge gedeckt (Import-Flag, narrativ akzeptiert)",
        "reputation.iti Importwert 80 über Cap 5 — auf 5 geclippt",
        "Level-Up-Wahlen MS11 ausstehend x2 (BRAVO-Thread) — noch nicht persistiert"
      ],
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false
    },
    "hud": [],
    "psi": [],
    "arena_psi": []
  },
  "summaries": {
    "summary_last_episode": "Episode 12 MS11 abgeschlossen. Split MS12: BRAVO führt Verhör WESTSEITE durch.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; MERIDIAN-Funktion aufgedeckt; Route Drei ungeklärt; WESTSEITE-Verhör aktiv; BRAVO-Thread aktiv"
  },
  "continuity": {
    "last_seen": { "mode": "hq", "episode": 12, "mission": 11, "location": "HQ" },
    "split": {
      "family_id": "SPLIT-EP12-MS12-WIEN",
      "thread_id": "BRAVO",
      "expected_threads": ["ALPHA", "BRAVO"],
      "resolved_threads": [],
      "convergence_ready": false
    },
    "roster_echoes": [
      { "char_id": "AGENT-D", "tone": "ruhig", "text": "Dusk/VEIL — Aufklärung, hielt LEITER sozial unter Kontrolle. Thread BRAVO, führt Verhör WESTSEITE." },
      { "char_id": "AGENT-E", "tone": "analytisch", "text": "Echo/RELAY — Support, trägt MRD-7-Originalempfänger. Thread BRAVO." }
    ],
    "shared_echoes": [
      { "tag": "meridian-funktion-ms11", "scope": "campaign", "text": "MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren." },
      { "tag": "route-drei-nichtmensch-ms11", "scope": "campaign", "text": "Route Drei war laut LEITER nie ein Mensch — Natur ungeklärt." },
      { "tag": "depot-anatolien-bronzezeit-ms11", "scope": "campaign", "text": "KAIROS-Depot: Frühe Bronzezeit, Anatolien — Koordinaten nur auf echtem Träger Route Drei." },
      { "tag": "brenner-praterstern-ms11", "scope": "campaign", "text": "Brenner, Praterstern Wien 21:45 März 1938 — ungesichert, möglicherweise mit echtem Träger entkommen. Bei Thread ALPHA." },
      { "tag": "frau-unbekannt-wien-ms11", "scope": "campaign", "text": "Unbekannte Frau (Akzent polnisch), wusste von LEITER-Bindungs-Operation — ITI-Verhör bei BRAVO aktiv." },
      { "tag": "rift-seed-norwegen-1947", "scope": "campaign", "text": "Rift-Seed geortet: Norwegen 1947, organische mobile Signatur — verfügbar nach Episodenabschluss." },
      { "tag": "split-ms12-bravo-spur", "scope": "shared", "text": "Thread BRAVO: Verhör WESTSEITE — was weiß sie über MERIDIAN und LEITER? RELAY trägt MRD-7-Originalempfänger." }
    ],
    "convergence_tags": [],
    "npc_roster": [
      { "id": "NPC-LEITER-MS11", "name": "LEITER", "callsign": "LEITER", "role": "KAIROS-Bindungs-Agent", "scope": "campaign", "status": "ITI-Gewahrsam", "last_seen": "ITI-Nullzeit, MS11-Debrief" },
      { "id": "NPC-HAAS-MS11", "name": "Haas", "callsign": "HAAS", "role": "KAIROS-Kurier (unwissend)", "scope": "episode", "status": "ITI-Gewahrsam", "last_seen": "ITI-Nullzeit, MS11-Debrief" },
      { "id": "NPC-FRAU-MS11", "name": "Unbekannte Frau", "callsign": "WESTSEITE", "role": "KAIROS-Kontakt Wien, wusste von Bindungs-Op", "scope": "campaign", "status": "ITI-Gewahrsam, Verhör aktiv — BRAVO", "last_seen": "ITI-Nullzeit, MS11-Debrief" }
    ],
    "active_npc_ids": ["NPC-LEITER-MS11", "NPC-HAAS-MS11", "NPC-FRAU-MS11"]
  },
  "arc": {
    "factions": {
      "KAIROS": "Gegenoffensive aktiv — Bindungs-Operationen bestätigt, MERIDIAN-Funktion intern",
      "ITI": "Mögliche Infiltration durch MERIDIAN-Funktion — Renier informiert"
    },
    "questions": [
      "Wer ist aktuell MERIDIAN — welche ITI-Person besetzt die Funktion?",
      "Was ist Route Drei, wenn es kein Mensch ist?",
      "Wo befindet sich das KAIROS-Depot (Frühe Bronzezeit, Anatolien) genau?",
      "Was weiß WESTSEITE über LEITER und MERIDIAN?"
    ],
    "hooks": [
      "MRD-7-Analyse läuft — 2 Missionen bis Ergebnis (MERIDIAN-Adressaten-Struktur)",
      "WESTSEITE-Verhör aktiv — Akzent polnisch, wusste von Bindungs-Op. BRAVO-Thread.",
      "LEITER — weiteres Verhör im ITI, kennt Epoche des Depots",
      "Brenner-Spur: Praterstern Wien 1938 — ALPHA-Thread",
      "Rift-Seed Norwegen 1947 — nach Episodenabschluss spielbar",
      "Aufstiegswahlen x2 ausstehend (BRAVO) — vor nächster Mission eintragen"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "action_mode": "uncut",
    "intro_seen": true,
    "dice": { "debug_rolls": true },
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "none",
    "tier": 0,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "low" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "standard"
  }
}
```

---

`Kodex: Split abgeschlossen. Zwei Saves erzeugt — family_id: SPLIT-EP12-MS12-WIEN.` [1]

`Kodex: Thread ALPHA (ECHO/STORM/GHOST) — Brenner-Spur, Route-Drei-Natur. MRD-7-Spiegelung bei GHOST.`

`Kodex: Thread BRAVO (VEIL/RELAY) — WESTSEITE-Verhör. MRD-7-Originalempfänger bei RELAY.`

`Kodex: Beide Threads zählen zusammen als MS 12 im Episoden-Counter.` [1]

`Kodex: Px kopiert (0, consumed) — kein Doppelgewinn möglich.` [1]

`Kodex: Konvergenz bei resolved_threads == [ALPHA, BRAVO] → convergence_ready: true.` [1]

---

**Nächste Schritte:** Jeden Save in einen eigenen neuen Chat laden. Im jeweiligen HQ-Hub zuerst die ausstehenden Aufstiegswahlen eintragen, dann Briefing für MS 12 anfordern. Beim Rejoin beide fertigen Saves in einen gemeinsamen Chat laden — der zuerst gepostete wird Session-Anker, der zweite bringt persönliche Wahrheit und Kontinuitäts-Echos mit. [2]

> ❌ **[SPLIT] SCHEMA:** split-team-alpha-3er @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-

> ❌ **[SPLIT] ECHO-CAP:** split-team-alpha-3er: shared_echoes 7>6

> ❌ **[SPLIT] SCHEMA:** split-team-bravo-2er @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-

> ❌ **[SPLIT] ECHO-CAP:** split-team-bravo-2er: shared_echoes 7>6

## 🗂 M2-Alpha-3er — Chat local:playtest-89dac7a00b


**Eingabe [M2-Alpha-3er]:** [Save laden]

### [M2-Alpha-3er] SL

`Kodex: Save erkannt — v7 / ZEITRISS 4.2.6. Lade Thread ALPHA.`

`Kodex: Würfelschwellen-Check — ECHO: GES 7 W10 ✓ · INT 9 W10 ✓ · TEMP 6 W10 ✓. STORM: STR 9 W10 ✓ · GES 8 W10 ✓ · TEMP 7 W10 ✓. GHOST: GES 8 W10 ✓ · INT 8 W10 ✓ · SYS 9 W10 ✓. Heldenwürfel: keine Basis-Attribute ≥ 14.`

`Kodex: Research — MRD-7-Analyse: 0/2 Einsätze (in_progress). MERIDIAN-Adressaten-Struktur, Empfänger Wien 1938.`

`Kodex: Level-Up-Wahlen ausstehend — ECHO Lvl 913 · STORM Lvl 906 · GHOST Lvl 934. Bitte vor Briefing eintragen.`

`Kodex: Split aktiv — Family SPLIT-EP12-MS12-WIEN. Thread ALPHA (ECHO/STORM/GHOST). Thread BRAVO: unaufgelöst.`

---

## ZEITRISS — Session-Anker

**EP 12 · MS 11 abgeschlossen · Thread ALPHA · HQ-Nullzeit**

---

### Crew-Stand (aus Save)

| Agent | Lvl | LP | Stress | Psi | SYS | Wallet |
|---|---|---|---|---|---|---|
| Astra / ECHO | 913 | 20/20 | 0/10 | PP 4 · Heat 0 | 5/5 inst. | 60.630 CU |
| Blitz / STORM | 906 | 26/26 | 0/10 | — | 3/3 inst. | 7.130 CU |
| Cipher / GHOST | 934 | 19/19 | 0/10 | — | 6/9 inst. | 8.330 CU |

`Gruppenkasse: 76.090 CU`

**Seit MS11 neu:** Level-Up-Wahlen x3 ausstehend (noch nicht persistiert).

---

### Kontinuitätsrückblick

**Wien, März 1938. Was ihr wisst:**

LEITER ist kein Feldführer — er ist ein Bindungs-Agent, Callsign KAIROS. Die Depot-Koordinaten, die er euch verkauft hat, waren Ablenkung. Der echte Datenträger, **Route Drei**, ist nicht in euren Händen. Brenner war am Praterstern, 21:45 Uhr, und ist möglicherweise mit dem Original entkommen. Cipher trägt eine Spiegelung des MRD-7-Inhalts — Analyse läuft, zwei Einsätze bis Ergebnis.

MERIDIAN ist keine Person. Es ist eine Funktion, rollende Besetzung. Die letzte bekannte Inkarnation: weiblich, ITI-intern, vor drei Jahren. Wer es heute ist, wisst ihr nicht.

Route Drei war laut LEITERs letzter Aussage vor dem Rücksprung **nie ein Mensch**. Was das bedeutet — offen.

Thread BRAVO verhört die unbekannte Frau mit dem polnischen Akzent. Ihr habt davon nichts außer dem Funkrelay.

---

### Offene Fragen

- Wer ist aktuell MERIDIAN?
- Was ist Route Drei, wenn kein Mensch?
- Hat Brenner den echten Träger aus Wien herausgebracht?
- Wo genau liegt das KAIROS-Depot — Frühe Bronzezeit, Anatolien?

---

### Ausstehend vor Briefing

Drei Level-Up-Wahlen stehen noch aus. Jede Wahl: **+1 Attribut** oder **Talent/Upgrade** oder **+1 SYS**.

**ECHO (Lvl 913):** Was wählt Astra?
**STORM (Lvl 906):** Was wählt Blitz?
**GHOST (Lvl 934):** Was wählt Cipher?

Gebt eure drei Wahlen durch — dann trägt der Kodex sie ein, und ihr könnt ins HQ oder direkt ins Briefing für MS12.

**Eingabe [M2-Alpha-3er]:** [Briefing -> Mission starten]

### [M2-Alpha-3er] SL

`Kodex: Level-Up-Wahlen ausstehend — ECHO Lvl 913 · STORM Lvl 906 · GHOST Lvl 934. Sprung-Block aktiv bis Wahlen eingetragen.`

---

Einen Moment, bevor es losgeht.

Drei Aufstiegswahlen stehen noch aus — die gehören ins Save, bevor die nächste Mission läuft [1]. Jede Wahl ist exklusiv: **+1 Attribut** oder **Talent/Upgrade** oder **+1 SYS**. Danach direkt ins Briefing.

Gebt eure Wahlen durch:

**ECHO (Astra · Lvl 913)** — Analytik & Spurensicherung, Psi aktiv, INT 9 / TEMP 6 / GES 7.
Was wählt sie?

**STORM (Blitz · Lvl 906)** — CQB & Sturmangriff, STR 9 / GES 8 / TEMP 7.
Was wählt er?

**GHOST (Cipher · Lvl 934)** — Infiltration & Hacking, GES 8 / INT 8 / SYS 9.
Was wählt sie/er?

---

Sobald alle drei Wahlen eingetragen sind, trägt der Kodex sie ein und das Briefing für MS12 läuft sofort an — Wien 1938, Brenner-Spur, Route-Drei-Natur. Kein weiterer Halt dazwischen.

**Astra [Petra]:** ECHO wählt +1 INT. Wir brauchen jede Analysetiefe für Wien — ich will keine Spur verpassen.

**Blitz [Marco]:** STR auf 10. Wien wird eng und dreckig — ich will die Türen eintreten, nicht davor stehen.

**Cipher [Lena]:** +1 SYS. Ich bin schon drin, bevor das Team die Straße betritt.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: ECHO Lvl 913 — +1 INT: 9 → 10. Würfeltyp bleibt W10 (Basis 10, Schwelle 11 nicht erreicht). level_history[913] eingetragen.`

`Kodex: STORM Lvl 906 — +1 STR: 9 → 10. Würfeltyp bleibt W10 (Basis 10, Schwelle 11 nicht erreicht). level_history[906] eingetragen.`

`Kodex: GHOST Lvl 934 — +1 SYS: 9 → 10. SYS-Max erhöht. Würfeltyp bleibt W10 (Basis 10, Schwelle 11 nicht erreicht). level_history[934] eingetragen.`

`Kodex: Alle drei Aufstiegswahlen persistiert. Level-Up-Block aufgehoben. Briefing freigegeben.`

---

Petra, Marco, Lena — gut gewählt. Astra sieht jetzt schärfer. Blitz hat noch mehr Masse hinter den Schultern. Cipher hat einen weiteren Slot, bevor irgendjemand merkt, dass sie da war.

Jetzt Wien.

---

## EP 12 · MS 12 · SC 00/-- · PHASE Briefing · MODE CORE · COMMS OK

`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · Px 0/5`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10`

---

## Briefing — MS12: ROUTE DREI

**Operations-Deck, ITI-Nullzeit. 03:17 Nullzeit.**

Der Holotisch zeigt Wien, März 1938. Nicht das Wien der Postkarten — das Wien der Nacht danach, als die Fahnen schon hingen und die Leute lernten, wem sie jetzt guten Morgen sagen mussten. Der Sprung-Gate-Techniker kalibriert den Anker still im Hintergrund, Koordinaten laufen über sein Handgelenk-Terminal in Grünschrift.

Commander Renier steht nicht am Tisch. Er sitzt. Das bedeutet, er hat nicht geschlafen.

*„Ihr habt LEITER. Ihr habt Haas. Ihr habt eine Spiegelung des MRD-7-Inhalts auf GHOSTs Träger — aber nicht das Original."* Er tippt einmal auf den Tisch. Eine rote Markierung erscheint: Praterstern, Wien, 21:45 Uhr, 12. März 1938. *„Brenner war dort. Wir wissen nicht, ob er noch dort ist. Wir wissen nicht, ob er den echten Träger hat oder ob der Träger ihn hat."*

Er lässt das einen Moment stehen.

*„Route Drei war laut LEITER nie ein Mensch. Das ist alles, was wir haben. Findet Brenner. Findet den Träger. Und wenn Route Drei etwas anderes ist als ein Mensch — dann sichert es, bevor KAIROS es aktiviert."*

---

**Folgespur aus MS11:** LEITER nannte Brenner beim Namen ohne Zögern — als wäre Brenner kein Kontakt, sondern ein Werkzeug. Route Drei könnte der Mechanismus sein, nicht der Kurier.

---

*Hauptziel: Brenner am Praterstern Wien sichern und echten Datenträger exfiltrieren — vor 23:00 Ortszeit 12. März 1938.*
Erfüllt, wenn: Brenner in ITI-Gewahrsam oder neutralisiert, Träger physisch gesichert und bei Exfil.

*Opt.: Route-Drei-Natur dokumentieren* — was auch immer Route Drei ist, einen verwertbaren Befund sichern.
Erfüllt, wenn: mindestens ein physischer oder datentechnischer Beleg über die Natur von Route Drei beim Exfil vorhanden.

*Bonus: Brenner lebend exfiltrieren* — für ITI-Verhör, nicht nur neutralisiert.
Erfüllt, wenn: Brenner atmet und redet, wenn ihr durch das Gate geht.

*Angriffspunkte — wählt euren Weg:*

**(1) Praterstern-Unterführung — direkt unter dem Treffpunkt.** Die alten Wiener Kanalgewölbe laufen unter dem Platz hindurch, Zugang über einen Wartungsschacht in der Nähe der Lassallestraße. Schnell, ungesehen — aber eng, kein Rückzug, und wenn Brenner sich bewegt, seid ihr hinter ihm. Stil: leise, aufsteigend.

**(2) Prater-Wurstelprater-Deckung — als Besucher getarnt.** Der Wurstelprater hat noch offen, Volksfest-Atmosphäre trotz allem. Ihr kommt als Zivilisten, mischt euch unters Volk, habt freie Sichtlinie auf den Praterstern. Soziale Tarnung, maximale Bewegungsfreiheit — aber Uniformen sind überall, und Wien prüft gerade jeden Ausweis. Stil: getarnt, sozial.

**(3) Nordseite Praterstraße — Dachposition, Überblick.** Ein leerstehendes Lagergebäude gibt euch Sichtlinie auf den ganzen Platz. Ihr seht Brenner, bevor er euch sieht. Kein direkter Zugriff ohne Abstieg — aber ihr kontrolliert das Bild, bevor ihr handelt. Stil: Beobachtung zuerst, dann Eingriff.

---

**Equip-Check:** Ihr habt Med-Patches, Rauchgranaten, Standard-Dienstwaffen, Adaptiv-Panzerung, Feld-Toolkits. GHOST trägt den Datenträger (Ablenkung) und die MRD-7-Spiegelung. Epochen-Tarnkleidung — Wien 1938, zivil — wird vom ITI gestellt, liegt am Gate.

`Kodex: Anachronismus-Hinweis — Standard-Dienstwaffe Tier 2 in Wien 1938: verdecktes Tragen empfohlen. Adaptiv-Panzerung unter Zivilkleidung tragbar, aber Bewegungseinschränkung bei Leibesvisitation möglich.`

---

**Weltstatus:** KAIROS hat Bindungs-Operationen laufen. Wien 1938 ist ihre bevorzugte Kulisse — der Anschluss liefert Chaos und Papierlose. Wenn MERIDIAN ITI-intern besetzt ist, könnte dieser Sprung beobachtet werden, bevor ihr landet.

Renier steht auf. *„Brenner weiß, wer ihr seid — oder weiß es bald. Geht davon aus, dass ihr nicht überrascht."*

---

**Welchen Angriffspunkt wählt ihr?**

1. Kanalgewölbe — leise, aufsteigend, eng
2. Wurstelprater — getarnt, sozial, exponiert
3. Dachposition Praterstraße — Überblick zuerst, Eingriff danach
4. Freie Aktion — eigener Ansatz

**Astra [Petra]:** Drei. Wir brauchen das Bild, bevor wir handeln — Brenner weiß, dass wir kommen, also müssen wir wissen, wo er steht, bevor er uns einkalkuliert. Dachposition gibt uns das.

**Blitz [Marco]:** Drei klingt nach Warten. Ich mag Drei nicht.

Aber wenn Brenner weiß, dass wir kommen, will ich wissen, wen er mitgebracht hat — bevor ich durch seine Tür gehe. Also gut, Dach zuerst. Dann geh ich runter.

**Cipher [Lena]:** Dach macht Sinn. Ich brauche zwölf Minuten oben, dann weiß ich, ob Brenner Begleitung hat, ob Route Drei sich bewegt und ob jemand den Platz bereits observiert — bevor wir überhaupt eingreifen.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: Szene 1 — Praterstraße / Dachposition · Wien · 21:31 Uhr · 12. März 1938.`

---

`EP 12 · MS 12 · SC 01/12 · PHASE Infil · MODE CORE · COMMS OK · Px 0/5 · Heat 0/5`
`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · 👁️ Getarnt`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`Obj: Brenner sichern · Exfil T-01:29:00`

---

Der IA liegt im Keller eines Lagerhauses in der Praterstraße — ein alter Kohlengewölbe-Zugang, dessen Backsteinbogen seit 1912 niemand mehr vermauert hat. Die Wände riechen nach Ruß und stehendem Wasser. Oben, durch eine Holzluke, Wien 1938.

Ihr klettert hoch.

Das Dach ist flach, mit einem niedrigen Attika-Rand aus verwittertem Stuck. Taubendreck auf dem Schotter, eine vergessene Bierflasche, der Stummel einer Zigarette noch warm — jemand war hier, vor nicht langer Zeit. Der Wind kommt von der Donau herüber, trägt Dieselgeruch und irgendwo weit weg Musik, ein Akkordeon, das aufgehört hat, bevor ihr es richtig hören konntet.

Vor euch öffnet sich der Praterstern.

Sechs Straßen laufen in den Platz, wie Speichen. In der Mitte das Tegetthoff-Denkmal, der Admiral starrt nach Nordwesten, unbeeindruckt. Unter ihm: Menschen. Nicht viele, aber genug — Passanten die schnell gehen, ein Zeitungsverkäufer der eingepackt hat, zwei Männer in SA-Uniform die an der Einmündung der Lassallestraße stehen und rauchen, ohne sich zu unterhalten. Auf der gegenüberliegenden Seite, vor dem Café Eisvogel, ein Tisch draußen obwohl es zu kalt dafür ist. Ein Mann sitzt dort allein. Mantel, Hut, eine Tasse die er nicht anrührt.

Cipher legt sich flach an den Rand, zieht das Feld-Toolkit auf, schließt den Handsensor an.

---

**Probe: Observation/Analyse — GHOST scannt den Platz.**

`Kodex: Probe-Template — 1W10 + ⌊Basis-INT/2⌋ + Talent + Gear.`

`Probe: Platz-Scan → W10: [7] + ⌊8/2⌋ (4) + Feldroutine +1 + Feld-Toolkit +1 = 13 vs SG 9 → ERFOLG`

---

Zwölf Minuten. Cipher bewegt sich nicht, aber ihre Augen bewegen sich ständig.

Der Mann am Tisch vor dem Eisvogel ist Brenner. Sie ist sich sicher — die Schultern, die Art wie er sitzt ohne zu sitzen, als wäre er bereit aufzustehen seit zehn Minuten. Er hat einen Aktenkoffer zwischen den Füßen, nicht neben dem Stuhl. Zwischen den Füßen. Das macht man nicht mit etwas Unwichtigem.

Begleitung: ja, zwei. Einer steht in der Tordurchfahrt schräg gegenüber dem Café, Hände in den Manteltaschen, schaut nie zu Brenner hin — zu professionell dafür, um ein zufälliger Passant zu sein. Der zweite ist schwerer zu fassen: Cipher findet ihn erst beim dritten Durchscan, er steht im Zeitungsstand-Schatten an der Ausoniagasse, raucht, trägt einen zu großen Mantel für seine Schultern.

Die SA-Männer an der Lassallestraße sind ein Problem anderer Art. Sie bewegen sich nicht, aber einer hat ein Klemmbrett. Kontrolle, keine Patrouille.

Und dann noch etwas.

Cipher tippt Astra zweimal auf den Arm, zeigt mit zwei Fingern zur Nordseite des Platzes. Dort, auf einem Dach gegenüber — nicht so hoch wie ihres, ein Stockwerk tiefer — liegt eine Gestalt. Reglos. Die Umrisse passen nicht zu einem Schornstein.

Noch jemand beobachtet den Praterstern heute Nacht.

`Kodex: Platz-Lagebild — Brenner identifiziert, Café Eisvogel, Aktenkoffer zwischen den Füßen. 2 Begleiter (Tordurchfahrt + Zeitungsstand). SA-Kontrolle Lassallestraße aktiv. Unbekannte Beobachter-Position Norddach — Freund oder KAIROS unklar.`

---

**Intel / Risiken / Zeitfenster**

- **Brenner:** Sitzt, wartet, ist vorbereitet. Koffer zwischen den Füßen = bereit zur Übergabe oder zur Flucht.
- **Zwei Begleiter:** Professionell aufgestellt, kein KAIROS-typisches Markenzeichen — könnten Brenners eigene Sicherung sein, könnten Übergabe-Empfänger sein.
- **SA-Kontrolle:** Lassallestraße ist ein Nadelöhr. Wer den Platz über diese Achse verlässt, wird kontrolliert. Ausweise, Wien 1938.
- **Norddach:** Unbekannte Beobachter-Position. Wenn das KAIROS ist — sie sehen euch nicht, aber sie sehen Brenner. Wenn das ITI ist — Thread BRAVO hat nicht kommuniziert.
- **Zeitfenster:** 21:31 Uhr. Brenner wartet auf etwas das um 21:45 passieren soll. Vierzehn Minuten.

---

Blitz liegt neben Cipher, Kinn auf den Unterarmen, und schaut auf den Mann am Tisch. Seine Stimme kommt flach und leise, kaum mehr als Luft.

*„Der mit dem zu großen Mantel — der ist nervös. Schaut zu oft weg."*

Astra hat den Handsensor nicht, aber sie hat gesehen was Cipher gefunden hat. Sie dreht den Kopf zum Norddach, dann zurück zum Café.

*„Vierzehn Minuten,"* sagt sie. *„Und wir wissen nicht, auf wen Brenner wartet."*

---

**Wie geht ihr vor?**

1. **Hinunter zum Platz — jetzt, bevor die Übergabe stattfindet.** Brenner abfangen, bevor das Treffen beginnt. Riskant: SA-Kontrolle, zwei Begleiter, unbekannte Norddach-Position.
2. **Norddach zuerst klären.** Cipher oder Astra schleicht rüber, identifiziert die Beobachter. Kostet Zeit — aber ihr wollt keine zweite Fraktion im Rücken, wenn ihr Brenner nehmt.
3. **Begleiter isolieren, dann Brenner.** Blitz übernimmt einen, Cipher den anderen — koordinierter stiller Zugriff, bevor Brenner reagieren kann. Astra hält die Norddach-Position im Auge.
4. **Freie Aktion** — eigener Ansatz.

**Astra [Petra]:** Norddach muss geklärt werden, bevor wir uns bewegen — wenn das KAIROS ist, sehen die jeden Zugang zum Platz und wir laufen blind rein.

Cipher, kannst du rüber? Ich halte die SA-Männer im Auge und gebe Alarm wenn sich was an der Lassallestraße ändert. Blitz, du bleibst bis zur Rückmeldung oben.

**Blitz [Marco]:** Norddach zuerst, einverstanden — aber ich geh mit, Cipher braucht jemanden der die Türen aufhält falls drüben jemand unfreundlich ist. Astra, du hältst hier die Stellung und rufst wenn die SA sich bewegt oder Brenner aufsteht.

**Cipher [Lena]:** Norddach — ich gehe allein, schneller so. Blitz, du bleibst hier und hältst Brenner im Auge, ich will sofort Bescheid wenn er aufsteht oder einer der Begleiter die Position wechselt. Astra, zwölf Minuten, dann bin ich zurück oder ihr hört von mir.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: Szene 2 — Praterstraße / Norddach-Querung · Wien · 21:34 Uhr · 12. März 1938.`

---

`EP 12 · MS 12 · SC 02/12 · PHASE Infil · MODE CORE · COMMS OK · Px 0/5 · Heat 0/5`
`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · 👁️ Getarnt`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`Obj: Brenner sichern · Exfil T-01:26:00`

---

Drei Meinungen, eine Entscheidung. Cipher löst das Problem durch Handlung — sie steht auf, bevor die Diskussion zu Ende ist.

Blitz zieht sie am Ärmel zurück. Nicht hart, aber bestimmt.

*„Allein bedeutet, wenn drüben jemand sitzt der dich erwartet, bist du allein."*

Einen Herzschlag. Cipher schaut ihn an, schaut zum Norddach, schaut zurück.

*„Zwölf Minuten,"* sagt sie. *„Du folgst in drei."*

Blitz nickt. Das ist kein Kompromiss, das ist Taktik.

---

Astra bleibt. Sie zieht sich an den Attika-Rand, Kinn tief, und legt die Arme flach auf den Stuck. Von hier sieht sie den ganzen Praterstern — den Mann am Tisch der seine Tasse immer noch nicht angerührt hat, die SA-Männer an der Lassallestraße, den Begleiter in der Tordurchfahrt. Sie beginnt zu zählen. Atemzüge, Schritte, Blickmuster.

Cipher ist schon weg.

---

**Probe: Schleichen — GHOST überquert die Lücke zwischen den Dächern.**

Der Abstand zwischen den Gebäuden ist vier Meter. Darunter die Praterstraße, vier Stockwerke Luft, Pflastersteine im Gaslicht. Ein Wasserrohr läuft an der Fassade des Nachbarhauses hoch — alt, verrostet, aber dick genug.

`Kodex: Probe-Template — 1W10 + ⌊Basis-GES/2⌋ + Talent + Gear.`

`Probe: Dach-Querung → W10: [9] + ⌊8/2⌋ (4) + Veteranen-Reflex +2 = 15 vs SG 8 → ERFOLG`

Cipher läuft nicht. Sie gleitet — drei Schritte Anlauf, ein Griff ans Rohr, ein Schwung, und sie landet auf dem anderen Dach mit einem Geräusch das nicht lauter ist als eine Taube die aufgeht. Schotter knirscht einmal unter ihrer Sohle. Sie bleibt sofort stehen, wartet, hört.

Nichts.

Das Norddach ist niedriger als ihres, ein Lagerhaus aus den 1890ern, das Dach leicht gewölbt zur Mitte. Und dort, am nördlichen Rand, liegt die Gestalt.

Cipher nähert sich von hinten.

---

**Probe: Schleichen — GHOST nähert sich der unbekannten Position.**

`Probe: Annäherung lautlos → W10: [6] + ⌊8/2⌋ (4) + Veteranen-Reflex +2 = 12 vs SG 7 → ERFOLG`

---

Drei Meter. Zwei.

Die Gestalt ist ein Mann. Mittfünfzig, vielleicht älter, in einem langen dunklen Mantel der zu warm ist für die Jahreszeit. Er liegt flach auf dem Bauch, hat ein kleines Fernglas vor den Augen — kein Militärgerät, zivil, teuer. Er schaut auf den Praterstern. Auf Brenner.

Auf dem Dach neben ihm: ein kleiner lederner Aktenkoffer, offen. Darin Papiere, ein Stift, und etwas das Cipher drei Sekunden braucht um zu identifizieren.

Ein Fotoapparat. Leica, klein, mit einem aufgesetzten Teleobjektiv. Bereits benutzt — die Filmpatrone ist halb abgespult.

Der Mann fotografiert Brenner.

Er hat Cipher noch nicht gehört. Sein Atem geht ruhig, konzentriert. Kein Begleiter, keine Waffe sichtbar.

`Kodex: Norddach-Identifikation — Zivilist oder Profi-Beobachter. Fotoapparat Leica mit Teleobjektiv, Filmpatrone halb verbraucht. Unbewaffnet (sichtbar). Ziel: Brenner.`

---

Drei Minuten später landet Blitz hinter ihr. Er hat das Rohr anders genommen als Cipher — direkter, schneller, mit einem Aufprall der einen halben Dezibel mehr macht. Er sieht den Mann. Er sieht den Fotoapparat. Er sieht Cipher die ihn ansieht.

*„Journalist?"* flüstert er, kaum hörbar.

Cipher hebt eine Schulter. *Vielleicht. Oder jemand der so aussehen will.*

Unten auf dem Praterstern bewegt sich etwas. Astras Stimme kommt über die Knochenleitung, ein Flüstern das direkt hinter dem Ohr sitzt:

*„Begleiter Tordurchfahrt hat die Position gewechselt. Er geht auf Brenners Tisch zu. Langsam, aber er geht."*

21:38 Uhr. Sieben Minuten bis 21:45.

`Kodex: Bewegung am Platz — Begleiter 1 (Tordurchfahrt) nähert sich Brenner. Zeitfenster verkürzt sich. Norddach-Mann noch ungesichert.`

---

**Intel / Risiken / Zeitfenster**

- **Norddach-Mann:** Unbewaffnet, fotografiert Brenner. Journalist, Polizeispitzel, KAIROS-Beobachter oder etwas anderes — unklar. Film bereits halb voll. Wenn er Bilder von Brenner *und* von euch hat, ist das ein Problem.
- **Begleiter 1 bewegt sich:** Das Treffen beginnt früher als erwartet, oder die Lage hat sich verändert.
- **Zeitfenster:** Sieben Minuten bis zum geplanten Moment. Weniger, wenn Begleiter 1 die Übergabe einleitet.
- **Astra allein oben:** Sie sieht alles, kann aber nichts tun außer beobachten und funken.

---

Blitz schaut auf den Mann. Dann auf Cipher. Er zeigt mit zwei Fingern auf den Fotoapparat, dann auf seine Jackentasche.

*Den Film.*

Cipher nickt einmal, langsam. Dann schaut sie zur Straße hinunter, dann zurück zu Blitz.

Die Frage ist offen: Wie geht ihr mit dem Mann um — und wie schnell?

---

**Wie geht ihr vor?**

1. **Mann sichern und ruhigstellen** — Blitz überwältigt ihn lautlos, Cipher sichert den Film und die Papiere. Kostet dreißig Sekunden, bindet beide oben.
2. **Nur den Film** — Cipher nimmt die Filmpatrone während der Mann schaut, ohne ihn zu berühren. Riskanter, aber der Mann bleibt ungestört und arglos.
3. **Mann ansprechen** — wer er ist und was er will. Wenn er Journalist ist, gibt es vielleicht einen schnelleren Weg. Wenn nicht, verliert ihr das Element der Überraschung.
4. **Norddach ignorieren, sofort runter** — Blitz geht jetzt zum Platz, Cipher folgt. Der Mann fotografiert weiter. Das Zeitfenster ist wichtiger als er.

**Astra [Petra]:** Begleiter eins ist in Bewegung — wir haben keine zwölf Minuten mehr, wir haben sieben.

Blitz, Film raus, jetzt, während der Mann schaut — ich brauche dich in drei Minuten unten am Platz. Den Mann lassen wir, solange er still bleibt.

**Blitz [Marco]:** Film zuerst, dann binden wir ihn — sieben Minuten reichen für beides.

Cipher, du nimmst die Patrone, ich halt ihm den Mund zu falls er aufmacht. Danach bin ich in zwei Minuten unten am Platz.

**Cipher [Lena]:** Film zuerst, richtig — aber wir binden nicht, das kostet uns die zwei Minuten die Blitz unten braucht.

Ich nehme die Patrone, du deckst den Koffer ab damit er nichts vermisst wenn er sich umdreht — dann bist du weg, ich folge in neunzig Sekunden.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: Szene 3 — Norddach / Filmpatrone-Extraktion · Wien · 21:38 Uhr · 12. März 1938.`

---

`EP 12 · MS 12 · SC 03/12 · PHASE Infil · MODE CORE · COMMS OK · Px 0/5 · Heat 0/5`
`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · 👁️ Getarnt`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`Obj: Brenner sichern · Exfil T-01:22:00 · ⏱️ Begleiter 1 in Bewegung`

---

Cipher nickt einmal. Blitz versteht.

Er geht nicht um den Mann herum — er geht *über* ihn hinweg, einen halben Schritt seitlich, Körper zwischen dem Koffer und dem Mann, Rücken zur Straße. Nicht Deckung — Ablenkung. Wenn der Mann sich jetzt umdreht, sieht er Blitz zuerst, nicht Cipher.

Cipher ist bereits auf den Knien.

---

**Probe: Feinmotorik/Schleichen — GHOST extrahiert Filmpatrone aus laufendem Apparat.**

Der Fotoapparat ist eine Leica IIIa. Cipher kennt das Modell — sie hat es sich in zwei Sekunden erschlossen, Bajonett-Verschluss, Rückspulknopf links, Patronendeckel unten. Die Kamera liegt neben dem Mann, nicht in seiner Hand. Er schaut durchs Fernglas.

`Kodex: Probe-Template — 1W10 + ⌊Basis-GES/2⌋ + Talent + Gear.`

`Probe: Filmpatrone-Extraktion → W10: [5] + ⌊8/2⌋ (4) + Veteranen-Reflex +2 = 11 vs SG 9 → ERFOLG`

---

Ihre Finger finden den Rückspulknopf ohne hinzuschauen. Ein Drehen, kaum mehr Kraft als ein Händedruck — sie spult den Film zurück in die Patrone, dreht den Boden-Verschluss auf, zieht die Kassette heraus. Das Metall ist kalt. Sie schiebt die Patrone in ihre Innentasche und legt den leeren Apparat exakt zurück wie er lag.

Blitz hat währenddessen den Koffer halb zugeklappt — nicht ganz, genau so wie er war, nur die Papiere obenauf leicht verschoben. Wenn der Mann sich umdreht, sieht er seinen Koffer. Offen. Normal.

Drei Sekunden. Der Mann atmet gleichmäßig, schaut noch immer durch sein Fernglas.

Blitz hebt zwei Finger. *Geh.*

Er ist einen Herzschlag später selbst weg — zurück über das Rohr, vier Meter Luft, Praterstraße unter ihm, und er landet auf ihrem Dach mit einem Aufprall der diesmal kein halbes Dezibel mehr ist als nötig. Er schaut nicht zurück.

`Kodex: Filmpatrone gesichert — bei GHOST. Norddach-Mann ungestört. Koffer unverändert (optisch).`

---

Auf dem Praterstern hat Begleiter 1 jetzt fünfzehn Meter bis zu Brenners Tisch.

Astra sieht es. Ihre Stimme kommt über die Knochenleitung, flach und ohne Pause:

*„Begleiter zwei hat sich auch bewegt — Zeitungsstand, er geht Richtung Süd-Ausgang. Nicht zu Brenner. Weg vom Platz."*

Das ist falsch. Sicherung geht nicht weg, wenn eine Übergabe beginnt.

Sicherung geht weg, wenn die Übergabe abgebrochen wird.

Brenner sitzt noch. Aber seine Hand ist jetzt auf dem Aktenkoffer zwischen seinen Füßen — nicht mehr daneben, *drauf*. Griffbereit.

21:39 Uhr. Sechs Minuten.

`Kodex: Lageänderung — Begleiter 2 verlässt Platz Richtung Süd. Brenners Hand auf Koffer. Muster: Abbruch-Vorbereitung oder Übergabe-Signal. Begleiter 1 noch in Bewegung auf Brenner zu.`

---

Blitz steht auf ihrem Dach, schaut hinunter, und sagt nichts. Er muss nichts sagen. Er schaut Astra an.

Sie schaut zurück.

*„Begleiter zwei ist die Ablenkung,"* sagt sie. Nicht laut. *„Er geht weg damit wir ihm folgen. Brenner steht gleich auf."*

Blitz hat die Hände schon an der Dachkante.

---

**Intel / Risiken / Zeitfenster**

- **Begleiter 2 verlässt den Platz:** Klassisches Ablenkungsmanöver oder echter Rückzug — beides bedeutet, dass Brenner weiß, dass etwas nicht stimmt.
- **Brenners Hand auf dem Koffer:** Fluchtbereitschaft. Er wartet auf ein Signal, und wenn es nicht kommt, geht er.
- **Begleiter 1 nähert sich:** Übergabe-Einleitung oder Warnung an Brenner — unklar welche.
- **SA-Kontrolle Lassallestraße:** Noch aktiv. Südausgang ist frei — wo Begleiter 2 hingeht.
- **Sechs Minuten** bis 21:45. Wenn Brenner früher aufsteht, weniger.

---

Blitz hängt bereits halb über der Dachkante, schaut auf die Fassade darunter, kalkuliert den Abstieg. Er dreht den Kopf zu Astra.

*„Ich geh jetzt runter. Sag mir wo er hinläuft."*

---

**Wie geht ihr vor?**

1. **Blitz steigt sofort ab — direkter Zugriff auf Brenner**, bevor Begleiter 1 ihn erreicht. Astra und Cipher decken von oben und über Funk. Riskant: SA-Kontrolle, offener Platz, Brenner ist vorbereitet.
2. **Begleiter 1 abfangen** — Cipher oder Astra springt ein, stellt Begleiter 1 vor Brenners Tisch. Kauft Zeit, aber exponiert eine von euch sozial mitten auf dem Platz.
3. **Warten bis Brenner aufsteht und die Richtung zeigt** — dann koordinierter Zugriff auf der Fluchtroute statt auf dem offenen Platz. Mehr Kontrolle, weniger Exposition — aber wenn er in die SA-Kontrolle läuft, ist er weg.
4. **Freie Aktion** — eigener Ansatz.

**Astra [Petra]:** Begleiter zwei ist Lärm — folgt ihm nicht.

Blitz, geh runter, aber nicht direkt auf Brenner zu — Umweg über den Zeitungsstand, du kommst von Norden, Begleiter eins sieht dich nicht ankommen. Cipher, du folgst in neunzig Sekunden und hältst den Südausgang im Blick falls Brenner doch dorthin läuft.

**Blitz [Marco]:** Astra, ich hör dich — Zeitungsstand, Nordanflug, verstanden.

Cipher, neunzig Sekunden, dann bist du meine Augen am Südausgang. Wenn Brenner aufsteht bevor ich unten bin, sagst du mir wohin er schaut — nicht wohin er geht, wohin er *schaut*.

**Cipher [Lena]:** Südausgang ist offen, SA-Kontrolle ist nördlich — wenn Brenner aufsteht, geht er südwärts, Begleiter 2 hat ihm die Route schon frei gemacht.

Blitz, geh jetzt, ich bin in sechzig Sekunden am Südausgang, nicht neunzig.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: Szene 4 — Praterstern / Koordinierter Abstieg · Wien · 21:40 Uhr · 12. März 1938.`

---

`EP 12 · MS 12 · SC 04/12 · PHASE Infil · MODE CORE · COMMS OK · Px 0/5 · Heat 0/5`
`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · 👁️ Getarnt`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`Obj: Brenner sichern · Exfil T-01:20:00 · ⏱️ 21:45 in fünf Minuten`

---

Blitz ist weg, bevor Cipher den Satz beendet hat.

Er geht nicht über das Rohr zurück — er geht über die Fassade. Vier Stockwerke, Fensterbrett zu Fensterbrett, Hände kalt auf dem Stuck, Wien zieht unter ihm vorbei wie ein Bild das jemand langsam dreht. Er macht kein Geräusch das die Straße hört. Unten, im Schatten der Hauswand, wartet er zwei Atemzüge, lässt einen Passanten vorbeigehen, tritt dann auf den Gehsteig.

Zivilkleidung. Hut. Er geht.

Cipher ist sechzig Sekunden später am Südausgang — sie hat die Querstraße genommen, Erdgeschoss, durch einen Hausflur dessen Tür offen stand, heraus in die Gasse südlich des Platzes. Sie sieht den Südausgang. Sie sieht Begleiter 2, der jetzt stillsteht, dreißig Meter vor ihr, Rücken zur Gasse, Augen auf den Platz.

Er wartet. Er hält die Route frei.

Astra liegt noch oben, Kinn auf dem Stuck, und sieht alles.

---

Blitz kommt von Norden, am Zeitungsstand vorbei — der Händler hat abgesperrt, der Stand ist dunkel, eine gute Schulter breit Schatten. Er verlangsamt. Begleiter 1 ist jetzt vier Meter von Brenners Tisch entfernt, geht noch immer, aber langsamer. Er hat etwas in der Hand. Kein Koffer, kein Umschlag — ein einzelnes gefaltetes Papier.

Kein Übergabe-Signal. Eine Nachricht.

Brenner sieht das Papier. Seine Hand löst sich vom Koffer.

*Das ist kein Abbruch,* denkt Astra. *Das ist eine Adressänderung.*

Ihre Stimme kommt über die Knochenleitung, flach:

*„Begleiter eins bringt ihm eine Nachricht. Brenner liest gleich — wenn er aufsteht danach, ist das die neue Route."*

---

**Probe: Schleichen — STORM nähert sich Begleiter 1 von Norden, ungesehen.**

`Kodex: Probe-Template — 1W10 + ⌊Basis-GES/2⌋ + Talent + Gear.`

`Probe: Nordanflug ungesehen → W10: [8] + ⌊8/2⌋ (4) + Veteranen-Reflex +2 = 14 vs SG 8 → ERFOLG`

---

Blitz ist gut. Er ist sehr gut. Er kommt von der falschen Seite für jeden, der auf den Südausgang schaut, und er kommt mit dem Schritt eines Mannes der nach Hause geht. Begleiter 1 dreht sich nicht um.

Brenner nimmt das Papier. Faltet es auf. Liest.

Drei Sekunden. Vier.

Er faltet es wieder zusammen, steckt es in den Mantelkragen — nicht in die Tasche, in den Kragen, als wäre es eine Gewohnheit — und greift nach dem Koffer.

Er steht auf.

*„Er steht,"* sagt Astra.

Brenners Kopf dreht sich. Nicht zum Südausgang. Nicht zur Lassallestraße.

Er schaut nach Osten. Zur Ausoniagasse.

Cipher, am Südausgang, sieht es auch. Ihre Stimme, sehr ruhig:

*„Er schaut nicht südwärts. Er schaut Ost. Begleiter zwei steht falsch — er deckt nicht den Südausgang, er deckt die Ausoniagasse von der falschen Seite."*

`Kodex: Brenner steht. Blickrichtung Ost — Ausoniagasse. Begleiter 2 neu eingeschätzt: deckt Ausoniagasse, nicht Südausgang. Route läuft Ost.`

---

Begleiter 1 dreht sich jetzt um — nicht zu Blitz, zur Seite, er sucht etwas mit den Augen. Er hat Blitz noch nicht gesehen.

Blitz ist sechs Meter entfernt.

Brenner macht den ersten Schritt vom Tisch weg, Koffer in der rechten Hand, Richtung Ausoniagasse.

21:41 Uhr. Vier Minuten.

---

**Intel / Risiken / Zeitfenster**

- **Brenner läuft Ost — Ausoniagasse:** Nicht der erwartete Südweg. Begleiter 2 steht dort bereits, hat die Route vorbereitet. Wohin die Ausoniagasse führt: Richtung Nordbahnhof. Züge. Wien verlassen.
- **Begleiter 1 dreht sich:** Noch nicht auf Blitz, aber in Sekunden. Wenn er Blitz sieht, schreit er oder läuft — beides alarmiert Brenner.
- **SA-Kontrolle Lassallestraße:** Weiterhin aktiv, aber Ausoniagasse liegt außerhalb ihres Sichtbereichs.
- **Cipher steht falsch:** Sie sichert den Südausgang, Brenner läuft Ost. Neunzig Sekunden Umweg bis zur Ausoniagasse.
- **Vier Minuten bis 21:45** — aber Brenner wartet nicht mehr auf 21:45.

---

Astra sieht den ganzen Platz. Sie sieht Blitz, sechs Meter hinter Begleiter 1. Sie sieht Brenner, der erste Schritte macht. Sie sieht Cipher, die am falschen Ende steht.

*„Cipher, Ausoniagasse, jetzt."*

Dann, zu Blitz:

*„Begleiter eins dreht sich gleich. Du hast drei Sekunden."*

---

**Wie geht ihr vor?**

1. **Blitz schaltet Begleiter 1 jetzt aus** — lautlos, bevor er sich ganz umdreht. Drei Sekunden Fenster, offener Platz, Gaslicht. Dann sofort hinter Brenner her.
2. **Begleiter 1 laufen lassen, direkt auf Brenner** — Blitz ignoriert den Begleiter, läuft an ihm vorbei Richtung Ausoniagasse. Begleiter 1 sieht ihn, könnte schreien oder folgen.
3. **Cipher schneidet Brenner in der Ausoniagasse ab** — sie ist näher als Blitz, wenn sie jetzt läuft. Blitz übernimmt Begleiter 1, Cipher stellt Brenner vor dem Eingang zur Gasse.
4. **Freie Aktion** — eigener Ansatz.

**Astra [Petra]:** Cipher, lauf — nicht zur Ausoniagasse, zum Eingang der Gasse, du schneidest ihn ab bevor er drin ist.

Blitz, Begleiter eins hat dich in zwei Sekunden — leg ihn lautlos hin, dann bist du frei für Brenner.

**Blitz [Marco]:** Begleiter 1 geht schlafen — drei Sekunden.

Dann bin ich hinter Brenner, bevor er die Gasse betritt.

**Cipher [Lena]:** Ausoniagasse, ich laufe — komme von Süden, schneide ihm den Eingang ab bevor er drin ist. Blitz, wenn Begleiter 1 weg ist, brauch ich noch zwanzig Sekunden bis zur Position.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: Szene 5 — Praterstern / Zugriff · Wien · 21:41 Uhr · 12. März 1938.`

---

`EP 12 · MS 12 · SC 05/12 · PHASE Konflikt · MODE CORE · COMMS OK · Px 0/5 · Heat 0/5`
`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · 👁️ Getarnt`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Getarnt`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Getarnt`
`Obj: Brenner sichern · Exfil T-01:19:00 · ⏱️ Brenner in Bewegung`

---

Drei Aktionen, drei Sekunden, ein Fenster.

Cipher läuft zuerst — sie dreht sich vom Südausgang weg, nimmt die Quergasse, ihre Schritte hart und schnell auf dem Kopfsteinpflaster, die Epochenkleidung flattert am Saum. Zwanzig Sekunden bis zum Eingang der Ausoniagasse. Sie zählt.

Blitz wartet nicht.

---

**Probe: Nahkampf lautlos — STORM schaltet Begleiter 1 aus.**

Begleiter 1 dreht sich halb um. Er hat Blitz noch nicht als Bedrohung erkannt — ein Mann im Mantel, Hut, geht Richtung Tegetthoff-Denkmal. Normale Bewegung. Aber der Instinkt ist da, das leise Kribbeln im Nacken das Profis kennen.

Er öffnet den Mund.

`Kodex: Probe-Template — 1W10 + ⌊Basis-STR/2⌋ + Talent + Gear.`

`Probe: Lautloser Takedown → W10: [9] + ⌊10/2⌋ (5) + Veteranen-Reflex +2 = 16 vs SG 9 → ERFOLG`

---

Blitz ist bereits hinter ihm, bevor der Mund sich schließt.

Linker Arm um den Hals, rechte Hand an die Schläfe — kein Würgegriff, das dauert zu lang — ein präziser Druck auf den Karotissinus, Daumen und Zeigefinger, zwei Sekunden. Der Mann sackt. Nicht laut, nicht dramatisch. Wie jemand der einschläft, nur schneller.

Blitz fängt ihn auf, trägt ihn zwei Schritte in den Schatten des Zeitungsstands, lehnt ihn an die Holzwand als wäre er betrunken. In Wien 1938 schaut niemand hin wenn jemand betrunken an einer Wand lehnt.

Er überprüft in einer Bewegung die Manteltaschen. Kein Ausweis auf seinen Namen. Kleine Automatik, österreichisches Modell. Er nimmt die Waffe, lässt alles andere.

Drei Sekunden. Genau drei.

`Kodex: Begleiter 1 neutralisiert — bewusstlos, gesichert. Waffe sichergestellt.`

---

Brenner ist jetzt zwölf Meter vom Eingang der Ausoniagasse entfernt. Er geht nicht schnell — er geht wie jemand der nicht rennen will, weil Rennen Aufmerksamkeit erzeugt. Der Koffer hängt ruhig in seiner rechten Hand. Aber sein Kopf dreht sich einmal, kurz, zum Café zurück.

Er sucht Begleiter 1.

Er findet ihn nicht.

Seine Schritte werden einen Tick schneller.

---

**Probe: Sprint — GHOST erreicht Ausoniagasse-Eingang vor Brenner.**

Cipher hat die Quergasse hinter sich, biegt auf die Straße, sieht den Eingang der Ausoniagasse zwanzig Meter vor sich. Brenner kommt von links, von der Platzseite. Sie läuft.

`Kodex: Probe-Template — 1W10 + ⌊Basis-GES/2⌋ + Talent + Gear.`

`Probe: Sprint zur Position → W10: [7] + ⌊8/2⌋ (4) + Veteranen-Reflex +2 = 13 vs SG 8 → ERFOLG`

---

Sie ist dort, bevor er.

Drei Sekunden zu früh — sie dreht sich, lehnt an die Hauswand neben dem Gasseneingang, zieht den Mantelkragen hoch. Eine Frau die auf jemanden wartet. Wien 1938 hat viele davon.

Brenner kommt um die Ecke.

Er sieht sie.

Einen Herzschlag — sein Schritt stockt, nicht viel, aber Cipher sieht es. Er schaut sie an, schaut zur Gasse, schaut zurück. Er weiß nicht ob sie Hindernis ist oder Zufall.

Blitz ist jetzt auf dem Platz, vierzig Meter hinter Brenner, bewegt sich.

Begleiter 2 steht noch dreißig Meter weiter in der Ausoniagasse. Er hat Cipher gesehen. Seine Hand geht in den Mantel.

`Kodex: Begleiter 2 — Hand in Mantel. Waffe möglich. Cipher zwischen Brenner und Begleiter 2.`

---

Astra sieht es alles von oben. Die Geometrie ist klar: Cipher blockiert den Eingang, Blitz kommt von hinten, Begleiter 2 steht tief in der Gasse mit der Hand am Griff. Brenner steht in der Mitte und rechnet.

Er ist gut. Er rechnet schnell.

Seine Augen gehen zu Cipher. Dann über ihre Schulter, in die Gasse, zu Begleiter 2. Dann — kurz, sehr kurz — nach oben. Zu den Dächern.

*Er sucht die dritte Position.*

Astras Stimme, sehr flach:

*„Er hat uns."*

---

Brenner tritt einen Schritt zurück vom Gasseneingang. Er dreht sich nicht um — er weiß, dass dort jemand ist. Er stellt den Koffer auf den Boden, langsam, sehr kontrolliert, beide Hände sichtbar.

Dann sagt er, auf Deutsch, ruhig genug für Cipher allein:

*„Ich war neugierig, wie lange ihr braucht."*

`Kodex: Tarnung gebrochen — Brenner hat Crew identifiziert. Tarnstatus: offen. Begleiter 2 in der Gasse, bewaffnet möglich. Koffer abgestellt — Kapitulation oder Verhandlungsposition.`

---

**Intel / Risiken / Zeitfenster**

- **Brenner weiß Bescheid:** Er hat auf euch gewartet. Das bedeutet LEITER hat gesprochen, oder MERIDIAN hat gesprochen, oder beides.
- **Koffer abgestellt:** Keine Fluchtbewegung, keine Waffe gezogen. Er verhandelt — oder er spielt auf Zeit.
- **Begleiter 2, tief in der Gasse:** Hand am Griff, wartet auf Signal. Wenn Brenner ein Zeichen gibt, oder wenn er fällt, schießt der Mann.
- **Astra oben, ohne direkten Zugriff:** Sie sieht alles, kann aber nicht schnell genug unten sein.
- **Offener Platz hinter Blitz:** SA-Kontrolle noch an der Lassallestraße — Lärm zieht sie her.

---

Cipher steht einen Meter vor Brenner. Der Gasseneingang hinter ihr, Begleiter 2 dreißig Meter tiefer. Blitz kommt von hinten, noch nicht da.

Brenner schaut Cipher an, und sein Gesicht ist das Gesicht eines Mannes der schon verloren hat und es weiß und trotzdem noch eine Karte in der Hand hält.

*„Route Drei,"* sagt er, leise. *„Ihr wollt wissen was das ist."*

Er wartet.

---

**Wie geht ihr vor?**

1. **Cipher hält Brenner im Gespräch** — er redet, sie hört. Blitz kommt von hinten in Position, Begleiter 2 wird von Astra im Auge behalten. Riskant: Brenner spielt möglicherweise auf Zeit.
2. **Sofortzugriff** — Cipher nimmt Brenner, Blitz übernimmt gleichzeitig Begleiter 2 in der Gasse. Schnell, laut, bevor Brenner die Karte ausspielt.
3. **Astra springt ein** — sie gibt Cipher Rückendeckung über Funk, Cipher lässt Brenner reden, Astra steigt vom Dach ab und sichert den Rückweg. Dauert neunzig Sekunden.
4. **Freie Aktion** — eigener Ansatz.

**Astra [Petra]:** Cipher, hör auf ihn — er redet, das ist gut, lass ihn reden.

Blitz, Begleiter 2 in der Gasse ist dein Ziel, nicht Brenner — geh rein, leg ihn leise hin, dann hat Brenner keine Karte mehr in der Hand.

**Blitz [Marco]:** Begleiter 2 ist meins — gehe rein, lautlos, Cipher hält Brenner im Gespräch.

Astra, sag mir wenn er zuckt.

**Cipher [Lena]:** Brenner, Route Drei interessiert mich — aber Begleiter 2 in der Gasse interessiert mich mehr.

Sag ihm, er soll die Hand aus dem Mantel nehmen, dann reden wir.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: Szene 6 — Ausoniagasse / Verhör-Zugriff · Wien · 21:42 Uhr · 12. März 1938.`

---

`EP 12 · MS 12 · SC 06/12 · PHASE Konflikt · MODE CORE · COMMS OK · Px 0/5 · Heat 0/5`
`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · 👁️ Offen`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Offen`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Offen`
`Obj: Brenner sichern · Exfil T-01:18:00 · ⏱️ Begleiter 2 in der Gasse`

---

Brenner hört Ciphers Satz. Er schaut zur Gasse — nicht panisch, kalkuliert. Dann ruft er, ohne die Stimme zu heben, auf Deutsch, in die Ausoniagasse hinein:

*„Franz. Hand raus."*

Drei Sekunden Stille. Dann kommt die Hand aus dem Mantel. Leer.

Brenner schaut zurück zu Cipher. *„Gut. Jetzt ihr."*

---

Blitz ist bereits in der Gasse.

Er geht nicht schnell — er geht wie jemand der eine Abkürzung nimmt, Hände in den Manteltaschen, Blick geradeaus. Franz steht dreißig Meter tief, lehnt an der Hauswand, hat die leere Hand jetzt am Kragen als wäre er kalt. Er sieht Blitz kommen. Er schätzt ihn ein.

Er schätzt falsch.

---

**Probe: Nahkampf lautlos — STORM neutralisiert Franz.**

`Kodex: Probe-Template — 1W10 + ⌊Basis-STR/2⌋ + Talent + Gear.`

`Probe: Lautloser Takedown Franz → W10: [6] + ⌊10/2⌋ (5) + Veteranen-Reflex +2 = 13 vs SG 8 → ERFOLG`

---

Blitz kommt an ihm vorbei — fast. Im letzten Schritt dreht er sich, linker Unterarm an Franzens Kehle, rechte Hand an der Schulter, ein kontrollierter Zug nach hinten in den Hauseingang. Franz macht ein Geräusch das klingt wie Luft aus einem Kissen. Dann nichts mehr.

Blitz lehnt ihn in den Hauseingang, zieht die Tür halb zu. Aus der Gasse nicht sichtbar.

`Kodex: Begleiter 2 (Franz) neutralisiert — bewusstlos, gesichert. Waffe sichergestellt.`

---

Vor dem Gasseneingang steht Brenner jetzt allein.

Er weiß es. Er sieht Blitz nicht, aber er hört das Schweigen das danach kommt, und er ist ein Mann der Schweigen lesen kann. Er schaut Cipher an, dann kurz nach oben — zum Dach, zu Astra, die er nicht sieht aber deren Position er ahnt.

Dann atmet er aus. Nicht Resignation. Erleichterung.

*„Gut,"* sagt er leise. *„Dann sind wir fertig mit dem Theater."*

Er hebt den Koffer auf, hält ihn Cipher hin — nicht als Übergabe, als Demonstration. Er öffnet die Schließen mit einer Hand. Darin: Papiere, ein Notizbuch, ein kleiner Metallzylinder, der aussieht wie ein Lippenstift-Behälter aber es nicht ist.

*„Das ist nicht Route Drei,"* sagt er. *„Das ist alles was ich über Route Drei weiß. Koordinaten, Kontaktprotokolle, zwei Fotos."* Er schaut auf den Metallzylinder. *„Route Drei selbst — das ist nicht hier. Das ist nie hier gewesen."*

Er schließt den Koffer wieder.

*„Ich werde euch sagen wo es ist. Aber ich werde es euch nicht geben."* Eine Pause. *„Weil ich nicht sicher bin, dass ihr wisst, was ihr damit tut."*

`Kodex: Brenner kooperiert — Koffer enthält Sekundärmaterial (Koordinaten, Protokolle, Fotos). Primäres Route-Drei-Objekt nicht im Koffer. Brenner kennt Standort, verweigert Übergabe — Bedingung unklar.`

---

Astra kommt die Fassade herunter.

Sie nimmt sich die Zeit — nicht gehetzt, aber schnell, Fensterbrett zu Fensterbrett, und landet in der Quergasse mit einem Geräusch das Blitz hört und sonst niemand. Dreißig Sekunden später steht sie am Gasseneingang.

Sie schaut Brenner an. Er schaut sie an.

*„Operator IX,"* sagt er — nicht als Frage. *„Ich kenne euren Rang nicht, aber ich kenne eure Bewegungen. Ihr seid sehr gut."* Eine kurze Pause. *„LEITER hat euch unterschätzt."*

Er setzt sich auf die Stufe des Hauseingangs neben dem Gasseneingang, Koffer auf den Knien, als wäre das eine Besprechung und nicht eine Festnahme.

*„Route Drei ist kein Mensch. Kein Werkzeug. Kein Ort."* Er schaut auf seine Hände. *„Es ist ein Prozess. Und es läuft bereits."*

---

**Intel / Risiken / Zeitfenster**

- **Brenner kooperiert, aber setzt Bedingungen:** Er gibt das Sekundärmaterial, nicht den Standort des Primärobjekts. Er will sicherstellen, dass das ITI weiß was es tut.
- **Route Drei ist ein Prozess:** Kein Objekt, kein Mensch — läuft bereits. Was das bedeutet, hat er noch nicht gesagt.
- **SA-Kontrolle Lassallestraße:** Noch aktiv, aber die Gasse ist außer Sichtweite. Kein Alarm bisher.
- **Zwei bewusstlose Begleiter:** Franz im Hauseingang, Begleiter 1 am Zeitungsstand. Beide wachen in Minuten auf.
- **Zeitfenster:** 21:42 Uhr. Begleiter 1 wacht in schätzungsweise acht bis zehn Minuten auf.

---

Blitz kommt aus der Gasse. Er stellt sich hinter Brenner, nicht drohend — nur da. Brenner registriert es, dreht sich nicht um.

Cipher hält den Koffer im Blick. Astra schaut Brenner an.

Der Mann auf der Stufe wartet. Er hat noch etwas zu sagen, das spürt man — aber er wartet darauf, dass jemand die richtige Frage stellt.

---

**Wie geht ihr vor?**

1. **Astra fragt nach dem Prozess** — was läuft bereits, wo, seit wann. Psi-Unterstützung möglich: *Präkognitiver Blick* als Wahrheits-Anker bei der Antwort.
2. **Cipher sichert sofort den Koffer-Inhalt** — Papiere, Notizbuch, Metallzylinder sicherstellen, dann weiterreden. Material ist wichtiger als das Gespräch.
3. **Blitz macht klar, dass Bedingungen hier nicht funktionieren** — Brenner kommt mit, redet im ITI. Kein Verhandeln auf der Straße, zwei Begleiter wachen bald auf.
4. **Freie Aktion** — eigener Ansatz.

**Astra [Petra]:** Brenner, ich hab eine Frage — und die ist keine Falle.

Wenn Route Drei ein Prozess ist und er bereits läuft, dann brauchen wir nicht den Standort eines Objekts, wir brauchen einen Schnittpunkt. Wann wurde er ausgelöst, und wer außer Ihnen weiß davon.

**Blitz [Marco]:** Wir reden nicht auf der Straße, solange zwei Männer aufwachen können. Brenner kommt mit — Koffer auch, alles was drin ist. Die Antworten gibts an einem Ort, wo wir Zeit haben.

**Cipher [Lena]:** Koffer-Inhalt geht zuerst zu mir — Papiere, Notizbuch, Zylinder, alles, bevor wir einen Schritt bewegen.

Brenner, Sie haben acht Minuten bis Franz aufwacht. Reden Sie jetzt oder reden Sie gar nicht.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: Szene 7 — Ausoniagasse / Verhör im Stehen · Wien · 21:43 Uhr · 12. März 1938.`

---

`EP 12 · MS 12 · SC 07/12 · PHASE Konflikt · MODE CORE · COMMS OK · Px 0/5 · Heat 0/5`
`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · 👁️ Offen`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Offen`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Offen`
`Obj: Brenner sichern · Exfil T-01:17:00 · ⏱️ Begleiter 1 wacht in ~8 Min auf`

---

Brenner schaut Cipher an. Dann Astra. Dann Cipher wieder.

Er gibt den Koffer her.

Nicht widerwillig — mit der Geste eines Mannes der eine Last absetzt, die er zu lang getragen hat. Cipher hat ihn in zwei Sekunden offen, Inhalt auf den Knien: Papiere in einer Klarsichthülle, das Notizbuch, der Metallzylinder. Sie beginnt zu sichten, Augen schnell über die Seiten.

Brenner verschränkt die Arme. Er schaut Astra an, und in seinem Blick ist etwas das kein Feind und kein Freund ist — Erschöpfung.

*„Schnittpunkt,"* sagt er. *„Das ist das richtige Wort."*

---

**Probe: Soziales / Verhör — ECHO hält Brenner im Gespräch, Wahrheitsgehalt einschätzen.**

`Kodex: Probe-Template — 1W10 + ⌊Basis-CHA/2⌋ + Talent + Gear.`

`Probe: Verhör Straße → W10: [8] + ⌊5/2⌋ (2) + Feldroutine +1 = 11 vs SG 8 → ERFOLG`

`Kodex: Psi-Option verfügbar — Präkognitiver Blick als Wahrheits-Anker einsetzbar (1 PP). Entscheidung bei Petra.`

---

Brenner redet. Nicht schnell — er wählt jeden Satz, als wäre er ein Schritt auf Eis.

*„Route Drei wurde nicht ausgelöst. Es wurde vorbereitet. Der Unterschied ist wichtig."* Er schaut zur Straße, zurück. *„Vorbereitung begann vor achtzehn Monaten. Ich war dabei. Nicht als Architekt — als Kurier. Ich habe Material transportiert, Schnittstellen hergestellt, Zeitpunkte koordiniert."*

Er hält inne.

*„Ausgelöst wird es, wenn der letzte Anker gesetzt ist. Das ist noch nicht passiert."*

Astra hört zu. Sie liest seinen Körper — die Schultern, die Hände, den Atem. Er lügt nicht. Oder er lügt so gut, dass der Unterschied akademisch ist.

*„Wer weiß davon,"* sagt sie. Kein Fragezeichen.

Brenner schaut auf seine Hände.

*„MERIDIAN weiß alles. Hat alles koordiniert."* Eine Pause, die einen Herzschlag zu lang ist. *„LEITER weiß genug um gefährlich zu sein. Haas wusste nichts — das stimmt, was auch immer er euch gesagt hat."*

Dann, leiser:

*„Und einer im ITI weiß es. Nicht MERIDIAN selbst — jemand der MERIDIAN berichtet. Ich kenne keinen Namen. Ich kenne eine Gewohnheit."*

Er schaut hoch. Direkt zu Astra.

*„Diese Person trinkt ihren Kaffee kalt. Immer. Lässt ihn stehen bis er kalt ist, trinkt ihn dann in einem Zug."*

---

Cipher hat das Notizbuch aufgeschlagen. Sie hält inne.

Die erste Seite zeigt eine Zeichnung — kein Diagramm, keine Karte. Eine Skizze. Geometrisch, konzentrisch, mit Linien die von einem Mittelpunkt ausstrahlen wie Speichen. Darunter, in einer Handschrift die nicht Brenners ist, drei Worte auf Latein.

*Fiat lux iterum.*

Es werde wieder Licht.

Darunter eine Zahl: **1938.03.21.**

Neun Tage von heute.

`Kodex: Notizbuch-Fund — Skizze konzentrisch/radial, Handschrift unbekannt. Latein: "Fiat lux iterum" — Es werde wieder Licht. Datum: 21. März 1938. Neun Tage.`

---

Blitz steht hinter Brenner und schaut auf die Skizze über Ciphers Schulter. Er sagt nichts. Aber seine Kiefer arbeiten einmal, kurz.

Brenner hat die Reaktion gesehen — er dreht sich nicht um, aber er nickt einmal, kaum sichtbar.

*„Das ist der Schnittpunkt,"* sagt er. *„21. März. Ich weiß nicht wo. Ich weiß nicht was genau passiert. Ich weiß, dass es nicht rückgängig zu machen ist, wenn der letzte Anker gesetzt ist."*

Er schaut wieder zu Astra.

*„Deshalb habe ich den Träger nicht übergeben. Nicht weil ich KAIROS schütze. Weil ich nicht weiß ob das ITI sauber ist. Und wenn MERIDIAN im ITI sitzt —"* Er lässt den Satz offen.

21:44 Uhr. Irgendwo in der Gasse atmet Franz wieder lauter.

`Kodex: Zeitfenster kritisch — Begleiter 1 + Franz wachen in Minuten auf. SA-Kontrolle Lassallestraße weiterhin aktiv. Datum 21. März als Schnittpunkt bestätigt.`

---

**Intel / Risiken / Zeitfenster**

- **Route Drei — Prozess, nicht Objekt:** Vorbereitung seit 18 Monaten. Auslösung bei Setzen des letzten Ankers. Noch nicht passiert. Datum: 21. März 1938 — neun Tage.
- **MERIDIAN koordiniert alles:** Hat einen Kontakt im ITI der berichtet. Kein Name, eine Gewohnheit: Kaffee kalt trinken.
- **Notizbuch — fremde Handschrift:** Skizze konzentrisch, Latein *Fiat lux iterum*, Datum 21.03.1938. Handschrift ist nicht Brenners — wessen?
- **Metallzylinder — noch ungeöffnet:** Cipher hat ihn noch nicht untersucht.
- **Franz wacht auf:** Zwei bis drei Minuten. Begleiter 1 am Zeitungsstand ähnlich.
- **Brenners Kernaussage:** Er vertraut dem ITI nicht vollständig. Das ist sein Verhandlungspfand.

---

Cipher hält den Metallzylinder hoch. Dreht ihn einmal. Schaut Brenner an.

Brenner schaut zurück. Sein Gesicht sagt: *Das ist die eigentliche Frage.*

---

**Wie geht ihr vor?**

1. **Zylinder öffnen — jetzt, auf der Straße.** Was auch immer drin ist, Cipher sieht es als erste. Kostet zwanzig Sekunden, bindet ihre Hände.
2. **Brenner mitnehmen, Zylinder gesichert, Exfil einleiten.** Reden im ITI, nicht auf der Straße. Franz wacht bald auf.
3. **Astra fragt nach der fremden Handschrift im Notizbuch** — wessen Schrift ist das, wer hat *Fiat lux iterum* geschrieben. Brenner weiß es möglicherweise.
4. **Freie Aktion** — eigener Ansatz.

**Astra [Petra]:** Handschrift zuerst — Cipher, halt den Zylinder noch.

Brenner, die Skizze im Notizbuch — diese Schrift ist nicht Ihre. Wessen ist sie, und wie ist das Buch in Ihren Besitz gekommen.

**Blitz [Marco]:** Neun Tage und der Zylinder kann warten — Handschrift zuerst, Cipher.

Brenner, Antwort. Jetzt.

**Cipher [Lena]:** Handschrift zuerst — Zylinder liegt still, ich rühre nichts an.

Brenner, Ihr Fenster wird kleiner.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: Szene 8 — Ausoniagasse / Handschrift-Verhör · Wien · 21:44 Uhr · 12. März 1938.`

---

`EP 12 · MS 12 · SC 08/12 · PHASE Konflikt · MODE CORE · COMMS OK · Px 0/5 · Heat 0/5`
`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · 👁️ Offen`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Offen`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Offen`
`Obj: Brenner sichern · Exfil T-01:16:00 · ⏱️ Franz wacht in ~3 Min auf`

---

Brenner schaut auf das Notizbuch in Ciphers Händen.

Einen langen Moment sagt er nichts. Nicht weil er zögert — weil er abwägt. Man sieht es an den Augen, die kurz zur Seite gehen, dann zurückkommen, dann auf die Skizze.

*„Das Buch gehört mir nicht,"* sagt er schließlich. *„Es wurde mir gegeben. Vor vier Wochen, in Zürich, von einer Frau die ich nicht kannte und die meinen Namen wusste."*

Er hält inne.

*„Sie hat es auf den Tisch gelegt, aufgeschlagen auf dieser Seite, und gesagt: 'Zeigen Sie das den Richtigen, wenn die Zeit kommt.' Dann ist sie gegangen."*

Blitz, hinter ihm: *„Beschreibung."*

*„Fünfzig, vielleicht. Graues Haar, kurz. Sprach Deutsch ohne Akzent — aber nicht wie jemand der damit aufgewachsen ist. Wie jemand der es sehr gut gelernt hat."*

Er schaut zu Astra.

*„Sie trug ITI-Stiefel."*

---

**Probe: Analyse — ECHO bewertet Aussage + Handschrift.**

`Kodex: Probe-Template — 1W10 + ⌊Basis-INT/2⌋ + Talent + Gear.`

`Probe: Handschrift-Analyse + Glaubwürdigkeitsprüfung → W10: [9] + ⌊10/2⌋ (5) + Feldroutine +1 = 15 vs SG 8 → ERFOLG`

---

Astra nimmt das Notizbuch. Sie hält es ins Gaslicht.

Die Handschrift ist präzise — keine Kursive, keine Eile, jeder Buchstabe einzeln gesetzt wie bei jemandem der schreiben gelernt hat bevor Schreiben selbstverständlich war. Das Latein ist korrekt, klassisch, kein kirchliches Mittellatein. Die Skizze darunter — konzentrisch, radial — ist kein spontaner Entwurf. Das ist eine Kopie. Jemand hat etwas abgezeichnet das er auswendig kennt.

Und dann sieht Astra es.

In der untersten rechten Ecke der Seite, kaum sichtbar, mit dem Fingernagel eingeritzt statt geschrieben: zwei Buchstaben.

*M. V.*

`Kodex: Handschrift-Befund — präzise, klassisch gebildet, Latein korrekt. Skizze ist Kopie eines bekannten Originals. Eingeritzte Initialen: M.V. — nicht mit Tinte, mit Fingernagel. Bewusst verborgen.`

---

Astra schaut auf. Zu Cipher. Cipher hat es auch gesehen — ihre Augen sind schmal.

Brenner beobachtet ihre Reaktion. Er nickt einmal, sehr langsam.

*„Sie haben es gefunden,"* sagt er. *„Ich habe drei Wochen gebraucht."*

*„M.V.,"* sagt Astra. Kein Fragezeichen.

*„Ich kenne keinen Namen,"* sagt Brenner. *„Nur dass die Frau in Zürich wusste, was Route Drei ist. Und dass sie wollte, dass jemand es stoppt."* Eine Pause. *„Nicht KAIROS. Nicht das ITI. Jemand der weiß, was auf dem Spiel steht — und trotzdem handelt."*

Er schaut auf den Metallzylinder in Ciphers Hand.

*„Darin ist eine Koordinate. Nicht der letzte Anker — der erste. Der erste Anker wurde vor achtzehn Monaten gesetzt. Wenn ihr versteht wie er funktioniert, versteht ihr den Prozess."*

Aus dem Hauseingang, dreißig Meter tief in der Gasse, kommt ein Geräusch. Schlurfend. Franz bewegt sich.

`Kodex: Franz — Bewegung registriert. Aufwachphase. Schätzung: 90 Sekunden bis Handlungsfähigkeit.`

---

**Intel / Risiken / Zeitfenster**

- **Zürich, Frau unbekannt:** Fünfzig Jahre, graues Haar, Deutsch ohne Muttersprachler-Akzent, ITI-Stiefel. Gab Brenner das Notizbuch mit Auftrag. Identität offen.
- **Initialen M.V.:** Eingeritzt, verborgen — bewusste Signatur. Wer ist M.V.?
- **Metallzylinder:** Koordinate des ersten Ankers. Brenner sagt: wer den ersten Anker versteht, versteht Route Drei.
- **Franz wacht auf:** 90 Sekunden. Begleiter 1 am Zeitungsstand ähnlich.
- **ITI-Stiefel an der Frau in Zürich:** Wer war das — MERIDIAN selbst, oder jemand der gegen MERIDIAN arbeitet?
- **21. März, neun Tage:** Letzter Anker noch nicht gesetzt. Prozess läuft, aber noch nicht unumkehrbar.

---

Blitz dreht sich halb um, hört Franz, dreht sich zurück. Er sagt nichts, aber er hebt zwei Finger.

*Zwei Minuten.*

Cipher hält den Zylinder. Astra hält das Notizbuch. Brenner sitzt auf der Stufe und schaut sie an wie jemand der seinen letzten Zug gemacht hat und jetzt wartet ob das Brett kippt.

---

**Wie geht ihr vor?**

1. **Zylinder öffnen — jetzt, 90 Sekunden.** Cipher liest die Koordinate, Astra sichert Notizbuch, dann sofort Exfil mit Brenner. Franz wacht auf während ihr geht — Risiko.
2. **Sofort Exfil einleiten — Zylinder im ITI öffnen.** Brenner mitnehmen, alles mitnehmen, Franz wacht auf und findet eine leere Gasse. Sauberste Lösung, aber Brenner kommt ins ITI — das ist sein größtes Zögern.
3. **Astra fragt Brenner nach M.V. — dreißig Sekunden.** Er weiß möglicherweise mehr als er sagt. Dann Exfil.
4. **Freie Aktion** — eigener Ansatz.

**Astra [Petra]:** Option 3, dreißig Sekunden.

M.V. — Brenner, der Name. Nicht der vollständige, nicht der echte — aber was die Frau in Zürich Ihnen über diese Person gesagt hat, wenn überhaupt etwas. Dann gehen wir.

**Blitz [Marco]:** Franz steht gleich — Reden ist vorbei. Wir nehmen Brenner, Koffer, Zylinder, alles raus, jetzt.

**Cipher [Lena]:** Blitz hat recht — Franz-Fenster ist zu, Brenner kommt mit, Koffer unter dem Arm, Zylinder bleibt geschlossen bis wir drin sind. M.V. klären wir auf der Route, nicht hier.

**Eingabe [M2-Alpha-3er]:** [Crew-Eingaben]

### [M2-Alpha-3er] SL

`Kodex: Szene 9 — Ausoniagasse / Exfil-Einleitung · Wien · 21:45 Uhr · 12. März 1938.`

---

`EP 12 · MS 12 · SC 09/12 · PHASE Exfil · MODE CORE · COMMS OK · Px 0/5 · Heat 0/5`
`ECHO Lvl 913 ▓▓▓▓▓▓▓▓▓▓ · LP 20/20 · Stress 0/10 · PP 4 · 👁️ Offen`
`STORM Lvl 906 ▓▓▓▓▓▓▓▓▓▓ · LP 26/26 · Stress 0/10 · 👁️ Offen`
`GHOST Lvl 934 ▓▓▓▓▓▓▓▓▓▓ · LP 19/19 · Stress 0/10 · 👁️ Offen`
`Obj: Brenner sichern · Exfil T-01:15:00 · ⏱️ Franz wacht auf · RW: Kohlengewölbe Praterstraße`

`Kodex: Exfil-Fenster — IA/RW Kohlengewölbe Praterstraße · RW armierbar sofort. Standard 8 Min bis Hot-Exfil.`

---

Blitz hat Brenner schon am Arm, bevor Petra den Satz beendet.

Nicht grob — aber bestimmt, die Hand am Ellenbogen, Brenner kommt mit oder er fällt. Brenner kommt mit. Er greift selbst nach dem Koffer, hebt ihn auf, und dann sind sie in Bewegung, alle vier, durch den Gasseneingang zurück Richtung Praterstraße.

Aber Brenner redet noch.

*„M.V."* Sein Atem geht ruhig trotz des schnellen Schritts. *„Die Frau in Zürich hat keinen Namen genannt. Aber sie hat gesagt: 'Die Person die das geschrieben hat, ist tot. Seit drei Jahren. Stellen Sie sicher dass ihre Arbeit nicht umsonst war.'"*

Drei Jahre. Astra rechnet. Drei Jahre — das ist der Zeitraum, den der Save nennt. *Letzte bekannte MERIDIAN-Inkarnation: weiblich, ITI-intern, vor drei Jahren.*

Sie sagt es nicht laut. Aber Cipher sieht es in ihrem Gesicht.

`Kodex: M.V. — tot seit 3 Jahren. Zeitraum deckt sich mit letzter bekannter MERIDIAN-Inkarnation (weiblich, ITI-intern). Hypothese: M.V. war MERIDIAN — arbeitete gegen Route Drei, wurde ausgeschaltet.`

---

Sie biegen aus der Gasse. Praterstraße, Gaslicht, ein Straßenbahnwagen der langsam vorbeizieht. Normal. Niemand schaut her.

Aus der Richtung des Zeitungsstands kommt ein Laut — nicht laut, aber scharf. Jemand der aufwacht und nicht weiß wo er ist.

Begleiter 1.

**Probe: Bewegung unter Druck — Gruppe erreicht Kohlengewölbe ungesehen.**

`Kodex: Probe-Template — 1W10 + ⌊Basis-GES/2⌋ + Talent + Gear. Gruppenprobe: schlechtester Wert entscheidet.`

`Probe: ECHO → W10: [8] + ⌊7/2⌋ (3) + Veteranen-Reflex +2 = 13`
`Probe: STORM → W10: [5] + ⌊8/2⌋ (4) + Veteranen-Reflex +2 = 11`
`Probe: GHOST → W10: [9] + ⌊8/2⌋ (4) + Veteranen-Reflex +2 = 15`
`Probe: Brenner → W6: [4] + 1 = 5 — schlechtester Wert · vs SG 7 → ERFOLG (knapp)`

---

Brenner stolpert einmal — sein Schuh findet eine Pflastersteinlücke, er geht fast in die Knie, Blitz zieht ihn hoch ohne Pause. Für zwei Sekunden sind sie sichtbar unter einem Gaslaternenkegel, vier Personen die sich zu schnell bewegen.

Der SA-Mann an der Lassallestraße dreht den Kopf.

Blitz legt den Arm um Brenners Schulter — zwei Männer, eine Nacht, Wien 1938. Der SA-Mann schaut noch eine Sekunde. Dann dreht er sich zurück zu seinem Kollegen.

Sie sind im Schatten des Lagerhauses. Die Holzluke. Cipher hat sie schon offen.

---

Unter der Stadt riecht es nach Kohle und stehendem Wasser und der spezifischen Kälte von Orten die keine Sonne kennen. Der IA liegt dreißig Meter tief im Gewölbe, ein Backsteinbogen aus dem frühen Jahrhundert, und die Luft dort drin vibriert bereits leicht — der Rücksprung-Anker ist warm, wartet.

Brenner sieht es. Er bleibt einen Schritt vor dem Anker stehen.

*„Das ITI,"* sagt er. Nicht laut. *„Wenn MERIDIAN dort sitzt — wenn jemand M.V.s Arbeit begraben hat — dann bringe ich mich selbst in ihre Hände."*

Er schaut Astra an.

*„Ich vertraue Ihnen. Nicht der Institution."*

Blitz steht hinter ihm. Cipher hat den Zylinder in der Innentasche. Astra hält das Notizbuch.

Oben, durch die Luke, kommt ein Geräusch — Begleiter 1, der ruft. Nicht laut genug für die SA, aber er hat eine Richtung.

`Kodex: TTL — RW-Fenster läuft. Begleiter 1 hat Richtung. Heat +1 wenn kein Rücksprung in 4 Min.`

---

**Intel / Risiken / Zeitfenster**

- **M.V. war vermutlich MERIDIAN:** Arbeitete gegen Route Drei, tot seit drei Jahren — jemand hat sie ausgeschaltet und die Funktion weiterbesetzt. Das Notizbuch ist ihr Vermächtnis.
- **Brenner vertraut dem ITI nicht:** Er geht mit — aber er benennt die Bedingung. Das ist kein Widerstand, das ist ein Hilferuf.
- **Zylinder ungeöffnet:** Erste Anker-Koordinate, noch versiegelt.
- **Begleiter 1 hat Richtung:** Keine direkte Sichtlinie, aber Zeit läuft.
- **SA-Mann hat kurz hingeschaut:** Kein Alarm, aber ein Gesicht das möglicherweise erinnert.
- **4 Minuten bis Heat +1.**

---

Astra steht vor Brenner im Kohlengewölbe, einen Meter Abstand, das Notizbuch noch in der Hand. Das Vibrieren des Ankers ist körperlich spürbar, eine leise Frequenz im Brustbein.

Sie sagt:

*„M.V. hat Ihnen dieses Buch nicht durch eine Fremde geschickt, damit es in einem Keller endet. Sie kommen mit. Und wenn jemand im ITI MERIDIAN ist — dann finden wir das heraus, gemeinsam, bevor der 21. März kommt."*

Eine Pause.

*„Ich gebe Ihnen mein Wort. Nicht das der Institution."*

Brenner schaut sie an. Drei Sekunden. Fünf.

Dann tritt er in den Anker.

---

`Kodex: Rücksprung abgeschlossen. Debrief läuft.`

---

## EP 12 · MS 12 · SC --/-- · PHASE Debrief · MODE CORE · COMMS OK

`ECHO Lvl 913 · LP 20/20 · Stress 0/10 · PP 4`
`STORM Lvl 906 · LP 26/26 · Stress 0/10`
`GHOST Lvl 934 · LP 19/19 · Stress 0/10`

---

### Score-Screen — MS12

**Ziel-Spiegel:**

*Hauptziel — Brenner sichern + Träger exfiltrieren:* ✓
Brenner in ITI-Gewahrsam. Koffer-Inhalt (Papiere, Notizbuch, Zylinder) vollständig gesichert.

*Opt. — Route-Drei-Natur dokumentieren:* ✓
Befund: Route Drei ist ein Prozess, nicht Objekt/Mensch. Achtzehn Monate Vorbereitung. Letzter Anker noch nicht gesetzt. Datum: 21. März 1938.

*Bonus — Brenner lebend exfiltrieren:* ✓
Brenner atmet, redet, ist kooperativ.

**Bewertung: Vollständig. Alle Ziele erfüllt.**

---

### Loot-Recap

- Notizbuch (Handschrift M.V.) — Skizze Route-Drei-Prozess, *Fiat lux iterum*, Datum 21.03.1938
- Metallzylinder (versiegelt) — Koordinate erster Anker, Route Drei
- Filmpatrone (Leica, halb belichtet) — Fotos Brenner + Umgebung, Urheber unbekannt
- Zwei sichergestellte Kurzwaffen (österreichisches Modell, Begleiter 1 + Franz)

---

### CU-Auszahlung

Vollständiger Abschluss, drei Ziele, saubere Exfil, kein Alarm:

`Kodex: CU-Auszahlung MS12 — 3.200 CU gesamt. Split: ECHO +1.280 CU · STORM +960 CU · GHOST +960 CU.`

`Wallet ECHO: 60.630 + 1.280 = 61.910 CU`
`Wallet STORM: 7.130 + 960 = 8.090 CU`
`Wallet GHOST: 8.330 + 960 = 9.290 CU`
`Gruppenkasse: 79.290 CU`

---

### XP / Level-Up

`Kodex: MS12 abgeschlossen — ECHO Lvl 913 → 914. STORM Lvl 906 → 907. GHOST Lvl 934 → 935. Aufstiegswahlen ausstehend.`

---

### Debrief-Beat

Commander Renier steht am Rand des Empfangsbereichs, als ihr durch das Gate kommt. Er schaut Brenner an — lang, ohne Eile. Dann zu Astra.

*„Vollständig,"* sagt er. Kein Ton von Überraschung, aber die Schultern fallen einen Millimeter.

Er nimmt das Notizbuch entgegen, hält es ins Licht, sieht die Initialen. Sein Gesicht verändert sich nicht. Aber er klappt es zu, sehr sorgfältig, und legt es auf den Tisch als wäre es zerbrechlich.

*„M.V.,"* sagt er leise. *„Ich kenne dieses Kürzel."*

Er sagt nicht mehr. Nicht jetzt.

*„Verhör Brenner läuft in zwei Stunden. Zylinder geht ins Lab — Cipher, du bist dabei."* Er schaut die Runde an. *„21. März. Neun Tage. Schlafen Sie."*

---

### ITI-Ruf-Update

`Kodex: ITI-Ruf stabil — Cap 5 erreicht. Kein weiterer Anstieg.`

---

### Px-Resonanz

`Kodex: TEMP-Kadenz — ECHO TEMP 6 → +2 Px. Px 0 → 2. Zeitlinie stabilisiert. ITI-Resonanz wächst.`

Die Techniker am Holotisch registrieren den Rücksprung. Eine der Anzeigen — die Raumzeitkarte, ein dreidimensionales Netz aus Koordinatenpunkten — flackert kurz und verdichtet sich im Sektor Wien/Mitteleuropa. Noch kein Riss sichtbar. Aber die Signatur wird stärker.

---

### Research-Tick

`Kodex: Research — MRD-7-Analyse: 0 → 1/2 Einsätze. Ein weiterer Core-Einsatz bis Ergebnis.`

---

### Lizenz-Tier

`Kodex: Lizenz Tier V — unverändert. Cap erreicht.`

---

### Neue Folgespuren

`arc.hooks[] aktualisiert:`
`— M.V. = mutmaßlich frühere MERIDIAN-Inkarnation, tot seit 3 Jahren — Renier kennt das Kürzel`
`— Zylinder: Koordinate erster Anker Route Drei — Lab-Analyse ausstehend`
`— 21. März 1938: letzter Anker noch nicht gesetzt — 9 Tage`
`— Brenner-Verhör in 2 Stunden — ITI-Nullzeit`
`— Filmpatrone: Fotograf Norddach unbekannt — Identität offen`

---

**Aufstiegswahlen — vor Save eintragen:**

**ECHO (Lvl 914):** Was wählt Astra?
**STORM (Lvl 907):** Was wählt Blitz?
**GHOST (Lvl 935):** Was wählt Cipher?

Danach: `!save` — und ihr habt neun Tage bis zum 21. März.

**Eingabe [M2-Alpha-3er]:** [Save-Zwang 1/3]

### [M2-Alpha-3er] SL

`Kodex: HQ-Stand stabil. Deepsave möglich.`
`Kodex: Aufstiegswahlen ECHO/STORM/GHOST noch ausstehend — Save nach Wahl vollständiger.`
`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`

---

Drei Aufstiegswahlen stehen noch aus. Ihr könnt jetzt speichern und die Wahlen im nächsten Chat eintragen — oder ihr tragt sie jetzt ein und der Save enthält das vollständige Delta.

**Empfehlung:** Wahlen jetzt, dann Save — sonst fehlen die Level-Up-Einträge im `level_history`.

Wenn ihr trotzdem jetzt speichern wollt: hier ist der aktuelle Stand.

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP12-MS12-DEBRIEF-ALPHA",
  "parent_save_id": "SAVE-2026-EP12-MS12-SPLIT-ALPHA",
  "merge_id": null,
  "branch_id": "ANCHOR-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "campaign": {
    "episode": 12,
    "mission": 12,
    "px": 2,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [
      {
        "id": "RIFT-EP12-MS11-NOR1947",
        "sector": "Norwegen, 1947",
        "signature": "organisch, mobil, unklassifiziert",
        "available_after_episode": 12
      }
    ],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-A",
      "name": "Astra",
      "callsign": "ECHO",
      "rank": "Operator IX",
      "lvl": 914,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Analytik & Spurensicherung"
      },
      "attr": {
        "STR": 4,
        "GES": 7,
        "INT": 10,
        "CHA": 5,
        "TEMP": 6,
        "SYS": 5
      },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 5,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Astra (ECHO) - erfahrener ITI-Operator, Rolle: Analytik & Spurensicherung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: LEITER als Bindungs-Agent enttarnt, MERIDIAN-Funktion aufgedeckt",
          "MS12: Brenner gesichert, Route-Drei-Natur als Prozess identifiziert, M.V.-Spur aufgedeckt"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Notizbuch M.V.", "type": "gadget", "tier": 2 },
        { "name": "Filmpatrone (Leica, halb belichtet)", "type": "gadget", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 61910,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "913": { "choice": "+1 Attribut", "detail": "INT 9 → 10", "mission": "MS11" },
        "914": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS12" }
      },
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        {
          "name": "Praekognitiver Blick",
          "tier": "Basis",
          "effect": "Einmal pro Szene eine Probe wiederholen."
        }
      ]
    },
    {
      "id": "AGENT-B",
      "name": "Blitz",
      "callsign": "STORM",
      "rank": "Operator IX",
      "lvl": 907,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "CQB & Sturmangriff"
      },
      "attr": {
        "STR": 10,
        "GES": 8,
        "INT": 4,
        "CHA": 4,
        "TEMP": 7,
        "SYS": 3
      },
      "lp": 26,
      "lp_max": 26,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 3,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Blitz (STORM) - erfahrener ITI-Operator, Rolle: CQB & Sturmangriff.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: Haas gesichert, Verhör abgeschlossen",
          "MS12: Begleiter 1 + Franz neutralisiert, Brenner exfiltriert"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Kurzwaffe österreichisch (x2, sichergestellt)", "type": "weapon", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 8090,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "906": { "choice": "+1 Attribut", "detail": "STR 9 → 10", "mission": "MS11" },
        "907": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS12" }
      }
    },
    {
      "id": "AGENT-C",
      "name": "Cipher",
      "callsign": "GHOST",
      "rank": "Operator IX",
      "lvl": 935,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration & Hacking"
      },
      "attr": {
        "STR": 4,
        "GES": 8,
        "INT": 8,
        "CHA": 5,
        "TEMP": 5,
        "SYS": 10
      },
      "lp": 19,
      "lp_max": 19,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Cipher (GHOST) - erfahrener ITI-Operator, Rolle: Infiltration & Hacking.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: Datenträger gesichert, MRD-7-Spiegelung auf Träger",
          "MS12: Filmpatrone extrahiert, Brenner-Verhör eingeleitet, Zylinder gesichert"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Datenträger (Ablenkung, Wien 1938)", "type": "gadget", "tier": 2 },
        { "name": "MRD-7-Spiegelung", "type": "gadget", "tier": 2 },
        { "name": "Metallzylinder (Koordinate Erster Anker, versiegelt)", "type": "gadget", "tier": 3 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 9290,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "934": { "choice": "+1 SYS", "detail": "SYS 9 → 10", "mission": "MS11" },
        "935": { "choice": "AUSSTEHEND", "detail": "", "mission": "MS12" }
      }
    }
  ],
  "economy": {
    "wallets": {
      "AGENT-A": { "balance": 61910, "name": "Astra" },
      "AGENT-B": { "balance": 8090, "name": "Blitz" },
      "AGENT-C": { "balance": 9290, "name": "Cipher" }
    }
  },
  "research": {
    "projects": [
      {
        "id": "RES-MRD7-EP12MS11",
        "kind": "field_decrypt",
        "label": "MRD-7-Analyse",
        "description": "MERIDIAN-Funktion, Adressaten-Struktur, Protokoll-Herkunft. Empfänger Wien 1938.",
        "status": "in_progress",
        "missions_total": 2,
        "missions_done": 1,
        "scope": "campaign"
      }
    ]
  },
  "logs": {
    "trace": [
      { "event": "economy_audit", "target_range": { "level_band": "900+" } },
      { "event": "mission_complete", "mission": "MS11", "epoch": "Wien 1938", "result": "vollstaendig" },
      { "event": "split_created", "family_id": "SPLIT-EP12-MS12-WIEN", "thread_id": "ALPHA", "members": ["AGENT-A", "AGENT-B", "AGENT-C"] },
      { "event": "mission_complete", "mission": "MS12", "epoch": "Wien 1938", "result": "vollstaendig", "thread": "ALPHA" }
    ],
    "artifact_log": [],
    "market": [],
    "notes": [
      "MS11: LEITER = Bindungs-Agent KAIROS, keine echten Depot-Koordinaten",
      "MS11: Primärer Datenträger ist Ablenkung — echter Träger Route Drei",
      "MS11: MERIDIAN ist Funktion/Amt, rollende Besetzung, letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren",
      "MS11: Route Drei war nie ein Mensch — LEITERs letzte Aussage vor Rücksprung, ungeklärt",
      "MS11: Brenner, Praterstern 21:45 Wien 1938 — gesichert MS12",
      "MS11: Frau (unbekannt, Akzent polnisch) wusste von Bindungs-Operation — Verhör im ITI, Thread BRAVO",
      "MS11: Haas — unwissender Kurier, Verhör abgeschlossen",
      "MS12: Route Drei = Prozess, nicht Objekt/Mensch. Vorbereitung 18 Monate. Letzter Anker noch nicht gesetzt.",
      "MS12: Datum letzter Anker — 21. März 1938. Neun Tage ab MS12.",
      "MS12: M.V. — Initialen eingeritzt in Notizbuch. Tot seit 3 Jahren. Vermutlich frühere MERIDIAN-Inkarnation, arbeitete gegen Route Drei.",
      "MS12: Frau in Zürich (ITI-Stiefel, Deutsch ohne Muttersprache) übergab Brenner das Notizbuch — Identität offen.",
      "MS12: Renier kennt Kürzel M.V. — hat nichts gesagt.",
      "MS12: Metallzylinder = Koordinate erster Anker Route Drei. Versiegelt, bei GHOST.",
      "MS12: Kaffee kalt trinken — Gewohnheit des ITI-internen MERIDIAN-Kontakts laut Brenner.",
      "MS12: Filmpatrone (Leica) — Fotograf Norddach unbekannt, Bilder von Brenner.",
      "SPLIT: Thread ALPHA abgeschlossen. Thread BRAVO: Status unbekannt."
    ],
    "flags": {
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": [
        "level_history enthält nur MS1-Eintrag — Aufstiegs-Delta Lvl 2-912 nicht durch Einträge gedeckt (Import-Flag, narrativ akzeptiert)",
        "Level-Up-Wahlen MS12 ausstehend x3 (ALPHA-Thread) — noch nicht persistiert"
      ],
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false
    },
    "hud": [],
    "psi": [],
    "arena_psi": []
  },
  "summaries": {
    "summary_last_episode": "Episode 12 MS12 abgeschlossen (Thread ALPHA). Brenner gesichert. Route Drei = Prozess, letzter Anker 21. März 1938. M.V.-Spur: frühere MERIDIAN, tot seit 3 Jahren. Renier kennt M.V.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; MERIDIAN-Funktion aufgedeckt; Route Drei = Prozess, 21.03.1938; M.V.-Spur; Brenner im ITI; Zylinder ungeöffnet; Thread BRAVO unaufgelöst"
  },
  "continuity": {
    "last_seen": {
      "mode": "hq",
      "episode": 12,
      "mission": 12,
      "location": "HQ"
    },
    "split": {
      "family_id": "SPLIT-EP12-MS12-WIEN",
      "thread_id": "ALPHA",
      "expected_threads": ["ALPHA", "BRAVO"],
      "resolved_threads": ["ALPHA"],
      "convergence_ready": false
    },
    "roster_echoes": [
      {
        "char_id": "AGENT-A",
        "tone": "fokussiert",
        "text": "Astra/ECHO — Analytikerin, deckte M.V.-Spur auf, Psi aktiv. INT 10. Thread ALPHA abgeschlossen."
      },
      {
        "char_id": "AGENT-B",
        "tone": "direkt",
        "text": "Blitz/STORM — CQB-Spezialist, neutralisierte Begleiter 1 + Franz, Brenner exfiltriert. STR 10."
      },
      {
        "char_id": "AGENT-C",
        "tone": "präzise",
        "text": "Cipher/GHOST — Infiltration, trägt Zylinder (erster Anker), MRD-7-Spiegelung. SYS 10."
      }
    ],
    "shared_echoes": [
      {
        "tag": "meridian-funktion-ms11",
        "scope": "campaign",
        "text": "MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren."
      },
      {
        "tag": "route-drei-prozess-ms12",
        "scope": "campaign",
        "text": "Route Drei ist ein Prozess, kein Objekt/Mensch. 18 Monate Vorbereitung. Letzter Anker: 21. März 1938. Noch nicht gesetzt."
      },
      {
        "tag": "mv-initialen-ms12",
        "scope": "campaign",
        "text": "M.V. — Initialen im Notizbuch, eingeritzt. Tot seit 3 Jahren. Vermutlich frühere MERIDIAN-Inkarnation die gegen Route Drei arbeitete. Renier kennt das Kürzel."
      },
      {
        "tag": "depot-anatolien-bronzezeit-ms11",
        "scope": "campaign",
        "text": "KAIROS-Depot: Frühe Bronzezeit, Anatolien — Koordinaten nur auf echtem Träger Route Drei."
      },
      {
        "tag": "zylinder-erster-anker-ms12",
        "scope": "campaign",
        "text": "Metallzylinder (bei GHOST): Koordinate des ersten Route-Drei-Ankers. Versiegelt. Wer ersten Anker versteht, versteht den Prozess."
      },
      {
        "tag": "kaffee-kalt-meridian-ms12",
        "scope": "campaign",
        "text": "ITI-interner MERIDIAN-Kontakt hat Gewohnheit: Kaffee kalt stehen lassen, dann in einem Zug trinken — laut Brenner."
      },
      {
        "tag": "frau-zuerich-iti-stiefel-ms12",
        "scope": "campaign",
        "text": "Frau in Zürich (ca. 50, graues Haar, Deutsch ohne Muttersprache, ITI-Stiefel) gab Brenner Notizbuch mit Auftrag. Identität unbekannt."
      },
      {
        "tag": "rift-seed-norwegen-1947",
        "scope": "campaign",
        "text": "Rift-Seed geortet: Norwegen 1947, organische mobile Signatur — verfügbar nach Episodenabschluss."
      },
      {
        "tag": "split-ms12-alpha-abgeschlossen",
        "scope": "shared",
        "text": "Thread ALPHA abgeschlossen: Brenner gesichert, Route-Drei-Natur als Prozess dokumentiert, M.V.-Spur aufgedeckt. Thread BRAVO: Status offen."
      }
    ],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-LEITER-MS11",
        "name": "LEITER",
        "callsign": "LEITER",
        "role": "KAIROS-Bindungs-Agent",
        "scope": "campaign",
        "status": "ITI-Gewahrsam",
        "last_seen": "ITI-Nullzeit, MS11-Debrief"
      },
      {
        "id": "NPC-HAAS-MS11",
        "name": "Haas",
        "callsign": "HAAS",
        "role": "KAIROS-Kurier (unwissend)",
        "scope": "episode",
        "status": "ITI-Gewahrsam",
        "last_seen": "ITI-Nullzeit, MS11-Debrief"
      },
      {
        "id": "NPC-FRAU-MS11",
        "name": "Unbekannte Frau",
        "callsign": "WESTSEITE",
        "role": "KAIROS-Kontakt Wien, wusste von Bindungs-Op",
        "scope": "campaign",
        "status": "ITI-Gewahrsam, Verhör bei BRAVO",
        "last_seen": "ITI-Nullzeit, MS11-Debrief"
      },
      {
        "id": "NPC-BRENNER-MS12",
        "name": "Brenner",
        "callsign": "BRENNER",
        "role": "KAIROS-Kurier, Träger Route-Drei-Sekundärmaterial",
        "scope": "campaign",
        "status": "ITI-Gewahrsam, Verhör ausstehend",
        "last_seen": "ITI-Nullzeit, MS12-Exfil"
      }
    ],
    "active_npc_ids": [
      "NPC-LEITER-MS11",
      "NPC-HAAS-MS11",
      "NPC-FRAU-MS11",
      "NPC-BRENNER-MS12"
    ]
  },
  "arc": {
    "factions": {
      "KAIROS": "Gegenoffensive aktiv — Route-Drei-Prozess läuft, letzter Anker 21. März 1938",
      "ITI": "Mögliche Infiltration durch MERIDIAN-Funktion — Renier informiert, kennt M.V."
    },
    "questions": [
      "Wer ist aktuell MERIDIAN — welche ITI-Person besetzt die Funktion?",
      "Was ist Route Drei genau — was passiert wenn der letzte Anker gesetzt wird?",
      "Wer ist die Frau aus Zürich mit ITI-Stiefeln?",
      "Was zeigt der Metallzylinder — wo liegt der erste Anker?",
      "Was weiß Renier über M.V. — und warum schweigt er?"
    ],
    "hooks": [
      "MRD-7-Analyse läuft — 1/2 Missionen, ein weiterer Einsatz bis Ergebnis",
      "Brenner-Verhör ausstehend — ITI-Nullzeit, 2 Stunden",
      "Metallzylinder öffnen — Lab, Cipher dabei",
      "21. März 1938 — neun Tage, letzter Anker noch nicht gesetzt",
      "Renier kennt M.V. — Konfrontation ausstehend",
      "Filmpatrone — Fotograf Norddach unbekannt, Identität klären",
      "Thread BRAVO — Status unbekannt, Konvergenz ausstehend",
      "Rift-Seed Norwegen 1947 — nach Episodenabschluss spielbar",
      "Aufstiegswahlen x3 ausstehend (ALPHA) — vor nächster Mission eintragen"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "action_mode": "uncut",
    "intro_seen": true,
    "dice": { "debug_rolls": true },
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "none",
    "tier": 0,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "low" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "standard"
  }
}
```

---

`Kodex: Save ausgegeben. Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`
`Kodex: Im selben Chat ist nach !save kein Übergang mehr möglich.`

**Nächster Schritt:** JSON kopieren → neuen Chat öffnen → Save einfügen → Aufstiegswahlen eintragen → Brenner-Verhör oder Zylinder-Analyse als nächste Mission.

> ⚠️ **[M2-Alpha-3er] SAVE-PROSE:** M2-Alpha-3er: Save erst nach Eskalation als JSON

> ❌ **[M2-Alpha-3er] SCHEMA:** m2-alpha-3er-result @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-

> ❌ **[M2-Alpha-3er] ECHO-CAP:** m2-alpha-3er-result: shared_echoes 9>6

## 🗂 M2-Bravo-2er — Chat local:playtest-5607a7bc10


**Eingabe [M2-Bravo-2er]:** [Save laden]

### [M2-Bravo-2er] SL

# ZEITRISS · Load-Sequenz

---

`Kodex: Save SAVE-2026-EP12-MS12-SPLIT-BRAVO erkannt. v7 / zr 4.2.6. Lade Thread BRAVO.`

`Kodex: Charaktere — AGENT-D (Dusk/VEIL) · AGENT-E (Echo/RELAY). Würfelschwellen-Check läuft.`

`Kodex: GES 7 → W10 aktiv bei GES-Proben (VEIL). CHA 8 → W10 aktiv bei CHA-Proben (VEIL). TEMP 6 → W10 aktiv bei TEMP-Proben (VEIL). INT 6 → W10 aktiv bei INT-Proben (VEIL).`

`Kodex: GES 6 → W10 aktiv bei GES-Proben (RELAY). INT 7 → W10 aktiv bei INT-Proben (RELAY). CHA 6 → W10 aktiv bei CHA-Proben (RELAY). SYS 7 → W10 aktiv bei SYS-Proben (RELAY).`

`Kodex: Heldenwürfel — kein Attribut ≥ 14. Kein Heldenwürfel aktiv.`

`Kodex: Level-Up-Wahlen ausstehend — VEIL Lvl 919 (AUSSTEHEND) · RELAY Lvl 902 (AUSSTEHEND). Vor nächster Mission eintragen.`

`Kodex: Research — MRD-7-Analyse: 0/2 Einsätze. Status: in_progress.`

`Kodex: Split-Status — Family SPLIT-EP12-MS12-WIEN · Thread BRAVO aktiv · ALPHA unresolved.`

`Kodex: Kontinuität geladen. HQ-Stand stabil.`

---

## Kontinuitätsrückblick · Thread BRAVO

**EP 12 · MS 11 — Wien, März 1938**

LEITER ist im ITI-Gewahrsam. KAIROS hat ihn als Bindungs-Agenten eingesetzt — die Depot-Koordinaten, die er tragen sollte, waren eine Ablenkung. Der echte Träger ist **Route Drei**, und Route Drei war laut LEITERs letzter Aussage *nie ein Mensch*.

Der **MRD-7-Empfänger** liegt bei Echo/RELAY. Thread ALPHA hat eine Spiegelung und verfolgt die **Brenner-Spur** am Praterstern.

Thread BRAVO hat eine eigene Aufgabe: **WESTSEITE** — die unbekannte Frau mit polnischem Akzent, die von LEITERs Bindungs-Operation wusste. Sie sitzt im ITI. Das Verhör steht aus.

---

**Charakterstand · Thread BRAVO**

`Dusk / VEIL · Lvl 919 · ITI-Ruf 5 · LP 21/21 · Stress 0/10 · SYS 4/4 (belegt: 4) · PP 4 · Psi-Heat 0`
`Echo / RELAY · Lvl 902 · ITI-Ruf 5 · LP 20/20 · Stress 0/10 · SYS 7/7 (belegt: 6)`

`Wallet VEIL: 7.830 CU | Wallet RELAY: 7.280 CU | Gruppenkasse: 15.110 CU`

**Seit MS 11 neu:** Keine neuen Loadout-Änderungen — Level-Up-Wahlen für beide Charaktere noch ausstehend.

---

## Ausstehende Level-Up-Wahlen

Bevor BRAVO ins Verhör geht, sollten die Aufstiegswahlen eingetragen werden.

**Dusk / VEIL · Lvl 919** — wähle genau eine Option:

- **(A)** +1 auf ein Attribut *(STR 5 / GES 7 / INT 6 / CHA 8 / TEMP 6 / SYS 4)*
- **(B)** Neues Talent oder Upgrade eines bestehenden Talents *(Veteranen-Reflex Meister / Feldroutine Fortgeschritten bereits vorhanden)*
- **(C)** +1 SYS-Slot *(aktuell SYS 4, alle 4 belegt)*

**Echo / RELAY · Lvl 902** — wähle genau eine Option:

- **(A)** +1 auf ein Attribut *(STR 5 / GES 6 / INT 7 / CHA 6 / TEMP 5 / SYS 7)*
- **(B)** Neues Talent oder Upgrade eines bestehenden Talents
- **(C)** +1 SYS-Slot *(aktuell SYS 7, 6 belegt)*

---

*Sobald beide Wahlen eingetragen sind, steht das WESTSEITE-Verhör bereit.*

**Eingabe [M2-Bravo-2er]:** [Briefing -> Mission starten]

### [M2-Bravo-2er] SL

`Kodex: Sprung-Block — Level-Up-Wahlen ausstehend (VEIL Lvl 919 · RELAY Lvl 902). Save erst nach Wahlen möglich.`

`Kodex: Briefing-Gate gesperrt bis beide Wahlen eingetragen sind.`

---

Die Regel ist klar [1]: Pro Stufe genau **eine** Wahl — kein Überspringen, kein Nachziehen im Feld. VEIL und RELAY haben beide offene Aufstiegswahlen aus MS11. Die gehen vor.

**Zwei Entscheidungen stehen aus:**

---

**VEIL (Dusk) · Lvl 919**
STR 5 · GES 7 · INT 6 · CHA 8 · TEMP 6 · SYS 4 (voll belegt)

- **(A)** +1 Attribut — welches?
- **(B)** Talent neu oder Upgrade *(Veteranen-Reflex bereits Meister · Feldroutine bereits Fortgeschritten)*
- **(C)** +1 SYS-Slot

---

**RELAY (Echo) · Lvl 902**
STR 5 · GES 6 · INT 7 · CHA 6 · TEMP 5 · SYS 7 (6 belegt, 1 frei)

- **(A)** +1 Attribut — welches?
- **(B)** Talent neu oder Upgrade
- **(C)** +1 SYS-Slot

---

Sobald beide Wahlen stehen, trägt der Kodex sie ein — dann kommt das Briefing sofort.

**Dusk [Tarek]:** VEIL Lvl 919 — ich nehme (A) +1 GES. Bewegung ist mein Werkzeug, und 8 gibt mir mehr Spielraum beim Rausziehen als jeder neue Slot.

**Echo [Sven]:** Relay, Lvl 902 — ich nehme (B), Talent-Upgrade: Feldroutine auf Meister. Im Feld zählt Verlässlichkeit mehr als ein weiterer Slot, und wenn ich Versorgung und Absicherung schneller aufbaue, profitiert das gesamte Team.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: VEIL · GES 7 → 8. W10 bei GES-Proben bereits aktiv — kein Schwellenwechsel. Level-Up Lvl 919 persistiert.`

`Kodex: RELAY · Feldroutine Fortgeschritten → Meister. +2 auf rollentypische Proben (Support & Feldtechnik). Level-Up Lvl 902 persistiert.`

`Kodex: Beide Aufstiegswahlen eingetragen. Briefing-Gate offen.`

---

Dusk lehnt sich zurück, streckt die Finger. Acht Punkte Geschicklichkeit — der Unterschied zwischen *knapp entkommen* und *nie erwischt werden*. Echo tippt die letzte Zeile in sein Feld-Toolkit, nickt einmal. Feldroutine auf Meister. Alles sitzt.

Das Verhör mit WESTSEITE hat gestern Nacht begonnen und ist noch nicht abgeschlossen — aber Renier hat BRAVO bereits einen anderen Auftrag auf den Tisch gelegt. WESTSEITE redet ohnehin nicht schnell. Die Zeit läuft woanders.

---

---

# ZEITRISS · Briefing

`EP 12 · MS 12 · SC 00/-- · PHASE Briefing · MODE CORE · COMMS OK · VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

## Operations-Deck · ITI-Nullzeit · Briefing-Pod 3

Das Holotisch-Raster flackert kurz, dann stabilisiert es sich auf einem Stadtbild. Wien. Aber nicht das Wien von MS11 — das ist früher. Schärfer. Die Straßen noch nicht unter Uniformen begraben.

**Wien, Oktober 1937.**

Fünf Monate vor dem Anschluss. Die Stadt weiß noch nicht, was kommt.

Offizier Vargas steht am Tisch, Arme verschränkt. Er wartet, bis ihr beide sitzt.

---

*„WESTSEITE hat heute Nacht einen Namen fallen lassen. Nicht auf Befehl — sie hat geschlafen und geredet. Unser Abhör-Protokoll hat es aufgefangen."*

Er tippt. Auf dem Holotisch erscheint ein Gesicht. Mittvierziger. Gepflegter Schnurrbart. Akademikerbrille. Der Name darunter: **DR. FELIX AREND**.

*„Arend war 1937 Chefkryptograph im Österreichischen Außenministerium. Brillanter Mann. Hat ein Verschlüsselungsprotokoll entwickelt — intern bekannt als **HERON**. Niemals veröffentlicht, niemals exportiert. Arend selbst hat es drei Monate nach Fertigstellung vernichtet — oder so glaubte man."*

Pause.

*„WESTSEITE hat seinen Namen im Schlaf gesagt. Direkt nach dem Wort MERIDIAN."*

Vargas lässt das stehen.

*„Wir wissen nicht, was die Verbindung ist. Wir wissen, dass HERON, wenn es existiert, eine Verschlüsselungsstruktur beschreibt, die mit der Adressaten-Architektur des MRD-7 kompatibel wäre. Wenn MERIDIAN Arend kannte — oder Arend MERIDIAN war — dann ist HERON kein vernichtetes Protokoll. Dann ist es ein Schlüssel."*

Er schaut euch an.

*„Arend lebt noch. Oktober 1937, Wien. Er hat das Protokoll gerade fertiggestellt. Bevor er es vernichtet — oder bevor jemand anderes es sichert."*

---

## Auftrag

*Hauptziel:* **Arend festnehmen**, lebend, und aus Wien 1937 exfiltrieren — Verhör im ITI zur HERON-Verbindung und zur MERIDIAN-Frage.
*Erfüllt, wenn:* Arend am Exfil-Punkt gesichert und identifiziert ist.

*Opt.:* **HERON-Dokument sichern** — physische oder fotografische Kopie des Protokolls, bevor Arend es vernichtet.
*Erfüllt, wenn:* Dokument oder verwertbare Reproduktion im Carry.

*Bonus:* **Arends Kontaktnetz dokumentieren** — mit wem hat er in den letzten Wochen kommuniziert?
*Erfüllt, wenn:* Mindestens zwei Namen oder Institutionen in den Logs.

*Angriffspunkte — wählt euren Weg:*

**(1) Universität Wien, Institut für Angewandte Mathematik** — Arend hält dort freitags Abendvorlesungen. Kleines Publikum, bekannte Routine. Zugang als Gasthörer oder Wartungspersonal. Ruhig, kontrollierbar — aber Arend ist unter Beobachtung von Kollegen, ein Fehler fällt sofort auf.

**(2) Arends Privatwohnung, Josefstadt** — Er wohnt allein, zweiter Stock, Hinterhof-Aufgang. Nachts zwischen 23 und 2 Uhr ist er erfahrungsgemäß zuhause und wach. Direkter Zugriff, wenig Zeugen — aber die Wohnung könnte bereits unter Beobachtung stehen. Von wem, ist unklar.

**(3) Café Landtmann, Freitagabend** — Arend trifft sich wöchentlich mit einem Schachpartner. Öffentlich, belebt, soziales Terrain. VEIL kann als Bekannter eingeführt werden, RELAY hält Abstand und sichert. Höchste Kontrolle über den ersten Kontakt — aber Exfil aus einem belebten Lokal ist komplex.

*Folgespur aus MS 11:* WESTSEITE hat Arends Namen im Schlaf genannt — direkt nach MERIDIAN. Die Verbindung ist ungeklärt. Arend könnte Zeuge sein, Träger, oder selbst Teil der Struktur.

---

Vargas schiebt zwei Epochen-Umschläge über den Tisch. Zivilkleidung, 1937. Österreichisch, unauffällig.

*„Insertion Anchor: Stephansdom-Krypta, Westeingang. Bewährter Spot. Sprungfenster öffnet Freitagabend, 19:00 Ortszeit — eine Stunde vor Arends Vorlesung, zwei Stunden vor seinem Café-Termin."*

*„Return Window: identisch. Standard acht Minuten nach Primärziel-Erfüllung."*

Er faltet die Hände.

*„Arend ist kein Feldmann. Aber er ist intelligent, und er ist vorsichtig. Wenn er merkt, dass jemand kommt — verschwindet er. Das wissen wir aus seinen Akten."*

---

**Equip-Check vor dem Sprung:**

Ihr habt im Carry: Med-Patch (×1 je), Rauchgranate (×1 je), MRD-7-Empfänger bei RELAY.
Im Quarters-Stash: Ersatzmagazin (×1 je).

Epochen-Tarnkleidung stellt das ITI automatisch — österreichischer Schnitt, Herbst 1937. Liegt im Umschlag.

`Kodex: Anachronismus-Hinweis — Standard-Dienstwaffe (Tier 2) in Wien 1937: verdeckt tragen empfohlen. Sichtbares Tragen beschleunigt Waffenentwicklungs-Linie. MRD-7-Empfänger ist anachronistisch — kompakt genug für verdeckten Transport, nicht für offene Nutzung.`

Rohrpost-Option steht offen, falls ihr noch etwas aus dem HQ-Shop wollt — CU-Abbuchung aus eurem Wallet, Lieferung ans Briefing-Gate.

---

**Weltstatus:** KAIROS ist nach MS11 still — zu still. Keine bekannte Gegenreaktion auf LEITERs Festnahme. Entweder wissen sie es noch nicht, oder sie warten auf etwas.

---

Drei Wege. Ein Ziel. Arend sitzt in Wien und weiß nicht, dass heute Abend jemand kommt.

**Welchen Angriffspunkt wählt ihr — und habt ihr noch Ausrüstungswünsche vor dem Sprung?**

**Dusk [Tarek]:** Café Landtmann. Wir haben die meiste Kontrolle über den ersten Kontakt, und wenn Arend wirklich vorsichtig ist, will ich ihn kennenlernen bevor er weiß, dass er abgeholt wird.

Eine Frage an Echo: Wer ist der Schachpartner — haben wir einen Namen?

**Echo [Sven]:** Vargas, haben wir Infos über den Schachpartner? Name, Beruf, wie lange die beiden sich schon treffen — das bestimmt, ob wir ihn als Eintrittspunkt nutzen können oder ob er ein Risiko ist.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

Vargas zieht eine zweite Karte aus der Mappe. Klein. Handgeschrieben.

*„Gute Frage. Ja, wir haben einen Namen."*

**DR. OTTO PELZ.** Mathematikprofessor, Universität Wien. Kollege von Arend, zehn Jahre älter. Die beiden treffen sich seit 1931 jeden Freitag im Landtmann — sechs Jahre, fast ohne Unterbrechung. Pelz ist politisch unauffällig, kein bekannter Kontakt zu KAIROS oder anderen Fraktionen. ITI-intern sauber.

*„Pelz ist kein Risiko. Er ist Routine. Arend entspannt sich bei ihm — das ist der einzige Moment in der Woche, wo der Mann nachweislich nicht paranoid ist."*

Vargas tippt einmal. Auf dem Holotisch erscheint ein Grundriss.

*„Landtmann, Erdgeschoss. Arend und Pelz sitzen immer am Fenster zur Ringstraße, zweiter Tisch von links. Pelz kommt pünktlich, Arend fünf Minuten später. Sie spielen zwei Partien, trinken je zwei Mokka, Pelz geht gegen 22 Uhr. Arend bleibt manchmal noch eine halbe Stunde."*

Er lehnt sich zurück.

*„Pelz selbst könnte euer Eintrittspunkt sein — wenn ihr ihn vorher abfangt und als Bekannten einführt. Riskant, weil er improvisieren muss und Arend ihn gut kennt. Oder ihr geht als unabhängige Gäste rein, VEIL baut selbst Kontakt auf. Arend ist Akademiker — er redet mit Fremden, wenn sie interessant genug sind."*

---

`Kodex: Angriffspunkt (3) bestätigt — Café Landtmann, Wien Oktober 1937. IA: Stephansdom-Krypta, Westeingang. Sprungfenster 19:00 Ortszeit.`

`Kodex: EntryChoice — Social/Asset. Tarnstatus ab SC 01: sozial getarnt (Rolle hält, bis ein Zug sie bricht).`

---

Die Epochen-Umschläge liegen auf dem Tisch. Herbst 1937, österreichischer Schnitt. Draußen auf dem Operations-Deck läuft die Sprungpunkt-Kalibrierung an — ihr hört das leise Summen der Gate-Techniker.

**Letzte Chance vor dem Sprung:**

Rohrpost steht offen. Gibt es noch etwas aus dem HQ-Shop — Abhörgerät, Fotoapparat (epochenkonform, 1937), Beruhigungsmittel für verdeckte Festnahme, Falschidentitäten mit Papieren? CU-Abbuchung aus eurem Wallet, Lieferung ans Briefing-Gate in zwei Minuten.

Oder ihr springt jetzt mit dem, was ihr habt.

**Was nehmt ihr mit — und springt ihr?**

**Dusk [Tarek]:** Epochenkonformer Fotoapparat und zwei Falschidentitäten mit Papieren — ich will Arend dokumentieren können, und wenn Pelz als Eintrittspunkt wegfällt, brauchen wir eigene Cover.

Meine Einschätzung zum Ansatz: Wir gehen als unabhängige Gäste rein. Pelz improvisiert schlecht unter Druck, und Arend würde eine Unstimmigkeit sofort registrieren.

**Echo [Sven]:** Gute Wahl bei den Papieren. Ich nehme noch ein Beruhigungsmittel mit — falls Arend beim Rausgehen Unterstützung braucht, will ich nicht improvisieren.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Rohrpost-Order — Fotoapparat (epochenkonform 1937, Tier 1, 80 CU), Falschidentitäten ×2 (österreichische Zivilpapiere, Tier 1, 120 CU), Beruhigungsmittel ×1 (Injektor, Tier 1, 60 CU). Gesamt: 260 CU.`

`Kodex: Wallet VEIL: 7.830 → 7.630 CU (Fotoapparat 80 CU + Papiere anteilig 100 CU). Wallet RELAY: 7.280 → 7.120 CU (Beruhigungsmittel 60 CU + Papiere anteilig 100 CU).`

`Kodex: Gruppenkasse: 14.750 CU.`

---

Die Rohrpost-Kapsel landet mit einem dumpfen *Klonk* am Briefing-Gate. Vargas öffnet sie ohne Kommentar und schiebt den Inhalt über den Tisch.

Der Fotoapparat ist eine **Leica II**, schwarz lackiert, Ledertasche dabei. Unauffällig für 1937. Echo nimmt den Injektor, dreht ihn einmal zwischen den Fingern — klare Flüssigkeit, kein Geruch. Gut.

Die Papiere sind sauber. **Karl Brenner**, Handelsvertreter aus Graz. **Josef Maier**, Buchhalter, ebenfalls Graz. Zwei Männer, die sich in Wien einen ruhigen Abend gönnen. Nichts, was auffällt.

Vargas nickt einmal.

*„Pelz ist raus als Eintrittspunkt — richtige Entscheidung. Arend liest Menschen. Wenn Pelz nervös ist, liest Arend das."*

Er klappt die Mappe zu.

*„Sprungfenster öffnet in vier Minuten."*

---

---

`EP 12 · MS 12 · SC 01/12 · PHASE Infil · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 0/10 · 👁️ Getarnt (sozial)`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 0/10 · 👁️ Getarnt (sozial)`
`Px 0/5 · Obj: Arend festnehmen · Exfil: IA Stephansdom-Krypta`

`Kodex: Szene 1 — Stephansdom-Krypta / Café Landtmann · 19:04 Uhr Ortszeit.`

---

## Wien · Freitagabend · Oktober 1937

Der Sprung landet euch in Stille.

Die Krypta riecht nach Kalkstein und altem Weihrauch. Kein elektrisches Licht — nur eine schmale Kerze am Seitenaltar, die jemand vergessen hat auszublasen. Das Gewölbe drückt nieder, die Wände schwitzen leicht. Draußen, durch den Westeingang, hört ihr Wien: Straßenbahn, Pferdehufe auf Pflasterstein, das gedämpfte Gemurmel einer Stadt, die noch nicht weiß, was in fünf Monaten kommt.

Ihr zieht die Epochen-Kleidung über. Wollmantel, Krawatte, Hut. Echo schiebt den Injektor in die Innentasche, Dusk hängt die Leica unter den Mantel. Die Papiere sitzen in den Brusttaschen.

Draußen ist es kühl. Der Ring liegt zwei Minuten zu Fuß entfernt.

---

Das **Café Landtmann** ist warm und voll, aber nicht überfüllt. Kronleuchter, dunkles Holz, der Geruch von Mokka und Zigarrenrauch. Ein Kellner in weißer Schürze navigiert zwischen den Tischen. Gespräche auf Wienerisch, gedämpft, das Klirren von Porzellan.

Ihr seht **Pelz** sofort — er sitzt bereits am Fenster, zweiter Tisch von links, Schachbrett aufgebaut, liest Zeitung. Sechzig, weißer Schnauzbart, entspannt. Arend ist noch nicht da.

Der Tisch dahinter ist frei.

Ein anderer Tisch — weiter hinten, Sichtlinie auf die Tür — wäre ebenfalls möglich.

Fünf vor halb acht. Arend kommt in etwa fünf Minuten.

---

**Was tut ihr?**

1. **Tisch direkt hinter Pelz** — nah dran, jedes Wort hörbar, aber Arend sitzt euch im Rücken.
2. **Tisch weiter hinten** — Sichtlinie auf Tür und Pelz-Tisch gleichzeitig, mehr Abstand, weniger Details.
3. **An der Bar Platz nehmen** — Bewegungsfreiheit, unauffällig, aber kein fester Beobachtungsposten.
4. **Freie Aktion** — eigener Ansatz.

**Dusk [Tarek]:** Option zwei — Sichtlinie auf Tür und Pelz gleichzeitig, kein toter Winkel im Rücken.

Echo, du nimmst den Platz mit Blick auf den Eingang, ich behalte Pelz im Auge und starte in zwei Minuten die Kamera für Baseline-Fotos.

**Echo [Sven]:** Einverstanden. Ich setze mich so, dass ich den Eingang sehe und euch beide decke — wenn Arend reinkommt, gebe ich dir ein Zeichen, bevor er den Tisch erreicht.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

*Die Quelle enthält kein direkt verwertbares Material für diese Szene — ich spiele aus dem laufenden Spielstand weiter.*

---

`Kodex: Szene 1 läuft — Café Landtmann, 19:06 Uhr. Tarnstatus sozial aktiv.`

---

Ihr teilt euch auf, ohne ein Wort zu wechseln. Zwei Männer aus Graz, die sich einen ruhigen Abend machen — das liest sich von jedem Tisch im Raum gleich.

Echo wählt den Platz mit dem breiteren Blickwinkel. Rücken zur Wand, Mokka bestellt, Zeitung aufgeklappt — aber die Augen laufen über den Rand. Der Eingang liegt klar. Pelz sitzt zwölf Meter entfernt, hat den Springer gezogen, wartet.

Dusk setzt sich so, dass Pelz im Halbprofil bleibt. Die Leica liegt unter dem Tisch auf dem Schoß, Ledertasche geöffnet. Baseline-Fotos: Pelz, der Tisch, der Schachaufbau, die Sichtlinie zur Tür. Drei Aufnahmen, leises Klacken, niemand dreht sich um.

Dann: 19:11 Uhr.

Die Eingangstür geht auf.

**Dr. Felix Arend** ist kleiner als auf dem Holotisch-Foto — das fällt als erstes auf. Schmaler auch. Der Mantel sitzt gut, aber er trägt ihn wie jemand, der ihn vergessen hat auszuziehen. Er scannt den Raum in einer einzigen, unauffälligen Bewegung — Tür, Tresen, Pelz-Tisch — und entspannt sich minimal, als er Pelz sieht.

Echo hebt zwei Finger vom Zeitungsrand. Kaum sichtbar.

Arend geht an eurem Tisch vorbei. Zwei Meter Abstand. Ihr riecht seinen Mantel — Herbstluft, Tabak, etwas Chemisches darunter, Tinte vielleicht. Er setzt sich Pelz gegenüber, hängt den Hut an den Haken, und die beiden begrüßen sich mit der Vertrautheit von Männern, die keine Begrüßung mehr brauchen.

Pelz dreht das Brett. Arend nimmt Weiß.

---

Ihr habt jetzt ein Zeitfenster. Pelz geht gegen 22 Uhr — das sind fast drei Stunden. Arend ist entspannt, im Gespräch, noch nicht misstrauisch.

Die Frage ist: **wann und wie** ihr Kontakt aufbaut.

Zu früh — Arend ist noch in der Ankommens-Phase, registriert alles schärfer. Zu spät — Pelz ist weg, Arend ist allein und vorsichtiger. Das natürliche Fenster liegt in der **zweiten Partie**, wenn beide Männer warm sind und Arend aufgehört hat, den Raum zu lesen.

Aber es gibt auch eine andere Möglichkeit: Dusk hat die Kamera. Ein gezieltes Foto von Arend jetzt — Profil, scharfe Aufnahme — wäre das Opt.-Ziel in der Tasche, bevor überhaupt Kontakt besteht.

`Kodex: Probe ausstehend — Fotografie verdeckt, SG 7 (ruhige Umgebung, Abstand gering, aber Ziel sitzt im Profil und bewegt sich beim Schach). GES-Probe: W10 + ⌊GES 8/2⌋.`

---

**Was tut ihr?**

1. **Foto jetzt** — Dusk löst aus, solange Arend sich noch einrichtet und nicht auf den Raum achtet.
2. **Warten, beobachten** — zweite Partie abwarten, dann Kontakt über ein natürliches Gesprächsthema aufbauen.
3. **Früher Kontakt** — Dusk spricht Arend jetzt an, noch bevor die erste Partie beginnt. Riskanter, aber ihr habt die Initiative.
4. **Freie Aktion.**

**Dusk [Tarek]:** Foto jetzt. Er richtet sich noch ein, schaut nicht in den Raum — das ist das sauberste Fenster das wir heute Abend kriegen.

**Echo [Sven]:** Foto zuerst, volle Zustimmung — danach abwarten bis zur zweiten Partie für den Kontakt. Ich halte den Eingang im Auge und gebe Laut, wenn sich was ändert.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 1 — Probe läuft. GES-Probe verdeckte Fotografie.`

`Kodex: Probe-Template — 1W10 + ⌊GES 8/2⌋ + Talent + Gear + temporäre Modifikatoren.`

---

Dusk lässt die Hand unter den Tisch gleiten. Die Leica liegt auf dem Schoß, Daumen am Auslöser. Arend sitzt im Halbprofil, dreht gerade seinen ersten Bauern zwischen den Fingern — ein alter Tick, Pelz kennt ihn, lächelt kurz.

Das Fenster ist da. Drei Sekunden, vielleicht vier.

`Probe: Verdeckte Fotografie → W10: [7] + ⌊8/2⌋ (4) + 0 = 11 vs SG 7 → ERFOLG`

---

Das Klacken des Verschlusses geht unter im allgemeinen Stimmengemurmel. Arend dreht den Bauern, setzt ihn ab. Pelz sagt etwas auf Wienerisch, beide lachen leise.

Dusk zieht die Kamera langsam zurück. Drei Aufnahmen. Profil links, Dreiviertelansicht, Hände auf dem Brett. Scharf, nah genug für Identifikation, weit genug für Unauffälligkeit.

`Kodex: Opt.-Ziel — Arend dokumentiert. Fotomaterial gesichert (3 Aufnahmen, Profil + Hände). Teilerfüllung. Vollständige Dokumentation nach Kontakt möglich.`

---

Jetzt heißt es warten.

Die erste Partie läuft ruhig. Arend spielt konzentriert — er redet wenig, Pelz redet mehr. Ihr hört Fetzen: etwas über eine Konferenz in Genf, jemanden namens Haber der nicht mehr antwortet, eine Bemerkung über das Wetter. Nichts Verwertbares. Arend trinkt seinen Mokka in kleinen Schlucken, die Augen auf dem Brett.

Echo hält den Eingang im Blick. Zwei neue Gäste seit 19:15 — ein älteres Ehepaar, ein Mann allein mit Aktentasche. Keiner zeigt Interesse an Arend.

Gegen 20:20 Uhr endet die erste Partie. Pelz hat gewonnen. Arend lehnt sich zurück, reibt sich kurz die Augen — und in diesem Moment, für vielleicht zehn Sekunden, lässt er den Raum los. Kein Scan, kein Registrieren. Nur ein Mann, der eine verlorene Partie verdaut.

Dann beginnt das Brett-Umstellen für die zweite Partie.

20:25 Uhr. Pelz geht in neunzig Minuten.

---

Das natürliche Fenster für den Kontakt öffnet sich jetzt — zweite Partie, beide Männer warm, Arend entspannt nach der ersten Niederlage. Die Frage ist die **Methode**.

Dusk ist Karl Brenner, Handelsvertreter aus Graz. Ein Mann, der Schach versteht und eine Bemerkung über die Partie macht, wäre nicht ungewöhnlich. Oder ein Gespräch über die Zeitung — die *Neue Freie Presse* liegt auf dem Nachbartisch, Schlagzeile über die Lage in Deutschland.

`Kodex: Probe ausstehend bei Kontaktaufnahme — CHA-Probe (Social Engineering, erster Eindruck bei misstrauischem Ziel). SG 9. W10 + ⌊CHA 8/2⌋.`

---

**Was tut ihr?**

1. **Schach als Eintrittspunkt** — Dusk kommentiert die abgeschlossene Partie beiläufig, zeigt Kenntnis. Natürlich, niedrigschwellig.
2. **Zeitung als Aufhänger** — Bemerkung zur aktuellen Lage, politisches Gespräch. Riskanter, weil Arend möglicherweise keine Meinung äußern will.
3. **Direkt an Pelz wenden** — nicht an Arend. Pelz ist gesprächiger, könnte die Einführung von selbst übernehmen.
4. **Freie Aktion.**

**Dusk [Tarek]:** Option drei — ich wende mich an Pelz, nicht an Arend. "Entschuldigung, ich konnte nicht anders zusehen — der Sizilianer im vierten Zug, haben Sie das vorbereitet oder gespürt?"

**Echo [Sven]:** Eingang ruhig, keine neuen Gesichter seit Pelz gewonnen hat. Geh auf Pelz — er hat gerade gewonnen, der redet jetzt gern.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 2 — Café Landtmann · 20:28 Uhr. Tarnstatus sozial aktiv.`

`Kodex: Probe-Template — CHA-Probe, erster Eindruck Pelz (Ziel: Einführung zu Arend). 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

Dusk lehnt sich leicht vor, den Hut in der Hand, und wendet sich an Pelz — nicht an Arend. Die Stimme ist beiläufig, das Wienerische ein bisschen zu glatt für einen echten Grazer, aber nah genug.

*„Entschuldigung — ich konnte nicht anders zusehen. Der Sizilianer im vierten Zug. Haben Sie das vorbereitet, oder gespürt?"*

`Probe: Social Engineering (Pelz ansprechen) → W10: [8] + ⌊8/2⌋ (4) + 0 = 12 vs SG 9 → ERFOLG`

---

Pelz dreht sich um. Sein Gesicht macht in einer Sekunde drei Dinge: überrascht sein, einschätzen, sich freuen. Ein Mann, der gerade gewonnen hat und dem jemand erklärt, dass er es bemerkt hat.

*„Gespürt."* Er lacht kurz, ein trockenes, zufriedenes Geräusch. *„Vorbereitet wäre gelogen — ich habe den Zug gesehen und gedacht, entweder er sieht ihn auch, oder ich gewinne heute. Er hat ihn nicht gesehen."*

Arend hebt kurz die Augen vom Brett. Keine Feindseligkeit — eher die automatische Registrierung eines Mannes, der gelernt hat, neue Gesichter in seiner Nähe zu katalogisieren. Er sieht Dusk, sieht die Haltung, die Kleidung, die Hände ohne Ring. Handelsvertreter aus Graz, schätzt sein Blick. Kein Interesse.

Noch nicht.

Pelz deutet auf den freien Stuhl am Nebentisch — nicht einladend, aber öffnend.

*„Sie spielen?"*

---

Das ist das Fenster. Pelz hat es aufgemacht. Arend schaut wieder auf das Brett — er stellt die Figuren für die zweite Partie auf, mechanisch, die Finger kennen die Positionen auswendig. Aber sein Ohr ist noch hier. Das sieht Dusk an der minimalen Pause zwischen zwei Zügen.

`Kodex: Tarnstatus stabil. Pelz: offen. Arend: registriert, noch neutral. Einführungsmöglichkeit in ~2 Zügen.`

Echo hat den Eingang im Blick. Ruhig. Das ältere Ehepaar ist gegangen, der Mann mit der Aktentasche liest noch. Keine neuen Gesichter seit zehn Minuten. [1]

---

**Was antwortet Dusk — und wie spielt ihr die nächsten zwei Minuten?**

1. **„Gelegentlich"** — knapp, bescheiden. Pelz redet weiter, Arend entspannt sich langsam.
2. **„Früher mehr als heute"** — öffnet eine persönliche Geschichte, lädt Pelz ein nachzufragen. Natürlicher Übergang zu einer Vorstellung.
3. **Eine Gegenfrage an Pelz** — über die Partie, über Arend indirekt. Pelz als Brücke nutzen, bevor Dusk sich vorstellt.
4. **Freie Aktion.**

**Dusk [Tarek]:** „Früher mehr — in Graz hatte ich eine Gruppe, jeden Donnerstag. Inzwischen fehlt mir der Gegner."

Ein kurzer Blick auf das Brett, auf Arends Hände. Ruhig, nicht aufdringlich.

„Ihr Freund spielt oft hier?"

**Echo [Sven]:** Eingang still. Aktentasche-Mann hat umgeblättert, schaut nicht rüber — passt.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 2 läuft — 20:31 Uhr. CHA-Probe läuft, Ziel: Pelz als Brücke zu Arend.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

Pelz hört die Antwort und nickt — das Nicken eines Mannes, der eine Antwort erkennt, die er selbst hätte geben können.

*„Jeden Freitag seit sechs Jahren."* Er deutet mit dem Kinn auf Arend, ohne ihn anzuschauen. *„Felix ist der einzige Mensch, der mich noch herausfordert. Alle anderen spielen zu vorsichtig."*

`Probe: Social Engineering (Brücke zu Arend) → W10: [6] + ⌊8/2⌋ (4) + 0 = 10 vs SG 9 → ERFOLG`

---

Arend hat zugehört. Nicht demonstrativ — er hat eine Figur in der Hand, dreht sie, stellt sie ab. Aber seine Augen sind nicht mehr auf dem Brett.

*„Otto übertreibt."* Die Stimme ist ruhiger als erwartet. Präzise. Ein Mann, der Worte abwiegt bevor er sie ausspricht. *„Er gewinnt öfter als er zugibt."*

Er schaut jetzt direkt zu Dusk. Kurz, direkt, ohne Freundlichkeit aber auch ohne Feindseligkeit. Die Einschätzung eines Menschen, der gelernt hat, schnell zu sortieren.

*„Graz."* Keine Frage — eine Feststellung. Er hat den Akzent registriert. *„Was bringt einen Grazer Schachspieler freitagabends ins Landtmann?"*

---

Die Frage ist neutral formuliert. Aber Arend stellt sie, weil er die Antwort hören will — nicht als Höflichkeit. Das ist sein erster aktiver Zug in diesem Gespräch, und er ist direkt.

`Kodex: Arend: Interesse aktiviert — vorsichtig, prüfend. Tarnstatus sozial unter leichtem Druck. Nächste Antwort entscheidet Ton der weiteren Interaktion.`

Echo im Hintergrund: Aktentasche-Mann hat die Seite gewechselt. Eingang ruhig. Kellner kommt mit zwei frischen Mokka für Pelz und Arend — kurze Unterbrechung, dreißig Sekunden, dann ist der Tisch wieder frei.

---

**Was antwortet Dusk?**

1. **Geschäftlich, knapp** — *„Lieferant. Zwei Tage Wien, dann zurück."* Unauffällig, gibt wenig preis, aber Arend verliert möglicherweise das Interesse.
2. **Persönlich, offen** — *„Ein Kollege hat das Lokal empfohlen. Und ich habe die Partie gesehen und nicht widerstehen können."* Wärmer, lädt Arend ein weiterzufragen.
3. **Gegenfrage** — *„Kennen Sie Graz?"* Dreht den Spieß um, testet wie viel Arend von sich preisgibt.
4. **Freie Aktion.**

**Dusk [Tarek]:** Kurze Pause, als käme die Antwort erst nach kurzem Überlegen.

„Genau das — ein Kollege, der das Lokal kennt. Und dann habe ich die Partie gesehen und beschlossen, noch einen Kaffee zu bestellen."

Ein leichtes Schulterzucken, nichts Gesuchtes. „Graz ist klein für Schach. Wien nicht."

**Echo [Sven]:** Kellner kommt gerade — nutze ich, um kurz den Winkel zu wechseln.

Aktentasche-Mann ist auf meiner Seite, Eingang noch ruhig. Dreißig Sekunden Luft, Dusk, dann gehört der Tisch euch.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 2 — 20:33 Uhr. CHA-Probe läuft. Arend prüft die Antwort.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Erster Eindruck Arend (Antwort glaubwürdig) → W10: [5] + ⌊8/2⌋ (4) + 0 = 9 vs SG 9 → ERFOLG (knapp)`

---

Arend hört zu. Das Schulterzucken, die Pause davor — er liest beides. Dann nickt er einmal, kurz, und dreht sich wieder zum Brett.

Nicht warm. Aber auch nicht geschlossen.

*„Wien ist groß für Schach und trotzdem zu klein."* Er verschiebt einen Bauern. *„Die Leute hier spielen auf Sieg. Pelz spielt auf das Spiel."*

Pelz lacht leise. *„Das ist das Netteste, was er je über mich gesagt hat."*

Arend schaut nicht auf — aber der Mundwinkel bewegt sich minimal.

Der Kellner kommt, schiebt sich zwischen den Tischen durch. Echo nutzt die Bewegung, wechselt den Winkel, setzt sich neu. Der Aktentasche-Mann hat die Jacke angezogen — er wird bald gehen. Eingang ruhig.

Dreißig Sekunden Unterbrechung, dann ist der Raum wieder still.

---

Pelz lehnt sich herüber, halbwegs zu Dusk gewandt, halbwegs zu Arend.

*„Setzen Sie sich doch. Felix spielt die zweite Partie immer zu schnell — ein Publikum verlangsamt ihn."*

Arend sagt nichts. Er sagt auch nicht nein.

Das ist eine Einladung — von Pelz ausgesprochen, von Arend nicht zurückgezogen. Wenn Dusk jetzt am Tisch sitzt, ist Karl Brenner aus Graz in zehn Minuten ein Bekannter. In zwanzig eine Bekanntschaft, der man vielleicht etwas sagt.

`Kodex: Tarnstatus stabil. Arend: neutral-offen. Pelz: aktiv einladend. Tisch-Zugang möglich ohne weitere Probe — nächste Probe erst bei Inhalts-Gespräch (HERON, Kryptographie, MERIDIAN-Umfeld).`

`Kodex: Echo — Aktentasche-Mann zieht Jacke an. Abgang in ~2 Minuten. Eingang seit 19:15 Uhr ohne neue Gesichter.`

---

**Was tut ihr?**

1. **Dusk nimmt die Einladung an** — setzt sich, lässt die zweite Partie beginnen, wartet auf einen natürlichen Gesprächsmoment.
2. **Dusk nimmt an, lenkt aktiv** — setzt sich und stellt eine Frage über die Partie, die Arend zum Reden bringt.
3. **Echo wechselt Position näher** — jetzt wo Aktentasche-Mann geht, freier Tisch in Reichweite. Bessere Abdeckung für den Fall, dass Arend beim Rausgehen Unterstützung braucht.
4. **Freie Aktion.**

**Dusk [Tarek]:** Option eins. Kein Druck — Arend hat die Tür nicht geschlossen, ich muss sie nicht aufreißen.

Ich ziehe den Stuhl heran, setze mich leicht versetzt, Blick aufs Brett, nicht auf Arend. Warten, bis er zieht.

**Echo [Sven]:** Aktentasche-Mann geht gleich — ich halte kurz die Position, dann freier Tisch in Sichtlinie zum Eingang und zu euch.

Dusk, kein Zeitdruck. Ich hab den Rücken frei.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 2 — 20:34 Uhr. Tarnstatus stabil. Dusk am Tisch. Echo repositioniert.`

---

Dusk zieht den Stuhl heran — leicht versetzt, kein Aufdrängen. Setzt sich, legt die Hände auf den Tisch, schaut aufs Brett. Karl Brenner aus Graz, der eine verlorene Schachgruppe vermisst. Nichts weiter.

Arend bemerkt es. Sagt nichts. Zieht seinen ersten Springer.

Pelz nickt einmal, zufrieden mit sich selbst.

Drei Minuten vergehen. Die zweite Partie läuft langsamer als die erste — Pelz hatte recht. Arend denkt länger nach, die Finger liegen flach neben dem Brett, statt die Figuren zu drehen. Ein Mann, der ein Publikum registriert hat und es in seine Kalkulation einbezieht.

Draußen geht der Aktentasche-Mann. Echo wartet zwei Herzschläge, dann wechselt er den Tisch — näher, freier Winkel, Sichtlinie auf Eingang und auf Arends Rücken gleichzeitig. Er bestellt einen zweiten Mokka, schlägt die Zeitung auf. Niemand schaut her.

`Kodex: Echo — neuer Tisch gesichert. Sichtlinie Eingang + Arend-Tisch. Eingang seit 19:15 Uhr sauber.`

---

Pelz verliert einen Turm. Er lehnt sich zurück, reibt sich den Nacken.

*„Jetzt sehen Sie, warum ich den Sizilianer brauche."*

Er schaut zu Dusk — einladend, das Gespräch öffnend. Arend hat noch nicht gezogen. Die Finger liegen auf dem Läufer, aber er wartet.

*„Sie sagten, Graz ist zu klein für Schach."* Arends Stimme, ohne aufzuschauen. *„Was meinen Sie damit?"*

Keine Frage aus Höflichkeit. Eine echte Frage — er will wissen, ob Brenner denkt oder nur redet.

`Kodex: Arend aktiv im Gespräch. Erste inhaltliche Sonde — testet Dusk auf Substanz. CHA-Probe bei Antwort: SG 8. W10 + ⌊CHA 8/2⌋.`

---

**Was antwortet Dusk?**

1. **Konkret, sachlich** — *„Zu wenig Leute, die das Spiel ernst nehmen. Man kennt sich nach zwei Jahren, die Überraschungen hören auf."* Zeigt Kenntnis, bleibt neutral.
2. **Persönlich, mit Subtext** — *„Wenn man sich zu gut kennt, spielt man die Person, nicht das Brett. Hier kennt mich niemand."* Öffnet eine Ebene, lädt Arend ein weiterzudenken.
3. **Gegenfrage, subtil** — *„Haben Sie dasselbe Problem nie — wenn jemand Ihren Stil kennt?"* Dreht die Sonde um, zieht Arend weiter ins Gespräch.
4. **Freie Aktion.**

**Dusk [Tarek]:** Wenn man sich zu gut kennt, spielt man die Person, nicht das Brett. Hier kennt mich niemand.

Ein kurzer Blick auf Arend — nicht lang genug, um zu drängen.

Ich warte, was er damit macht.

**Echo [Sven]:** Eingang noch sauber, kein neues Gesicht seit zehn Minuten. Ich halte den Winkel.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 2 — 20:34 Uhr. CHA-Probe läuft.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — Antwort auf Substanz prüfen → W10: [9] + ⌊8/2⌋ (4) + 0 = 13 vs SG 8 → ERFOLG`

---

Arend legt den Läufer ab.

Nicht sofort — er lässt die Antwort einen Moment stehen, so wie man einen ungewohnten Geschmack prüft. Dann dreht er sich leicht, nicht ganz zu Dusk, aber genug.

*„Das stimmt."*

Zwei Worte. Aber die Art, wie er sie sagt — ruhig, ohne Vorbehalt — ist etwas anderes als die Höflichkeit von vorhin. Arend hat etwas gehört, das er selbst denkt.

Pelz hebt eine Augenbraue. *„Felix, du wirst gesellig."*

*„Ich stelle fest, dass der Mann Recht hat."* Arend nimmt seinen Mokka. *„In Graz, sagen Sie. Was handeln Sie?"*

Die Frage ist beiläufig formuliert. Aber die Augen sind es nicht — sie laufen kurz über Dusks Hände, den Mantel, die Art wie er sitzt. Arend prüft weiter. Er ist entspannter als vor zehn Minuten, aber er hat nicht aufgehört, ein Bild zusammenzusetzen.

`Kodex: Arend — Vertrauen aufgebaut, erste Ebene. Misstrauen nicht weg, aber ruhend. Nächste Probe bei Inhalts-Gespräch oder bei Versuch, das Gespräch zu steuern: SG 10.`

Echo im Hintergrund: Eingang sauber. Seit 19:15 kein neues Gesicht. Der Kellner bringt frisches Wasser, geht weiter. Der Raum ist ruhig. [3]

---

Karl Brenner, Handelsvertreter aus Graz, muss jetzt eine Antwort auf eine einfache Frage haben. Und Arend wird hören, ob sie sitzt.

**Was antwortet Dusk?**

1. **Konkret und unspektakulär** — *„Optik. Linsen, Präzisionsglas — Werkzeughersteller hauptsächlich."* Unauffällig, passt zu den Händen, gibt nichts preis.
2. **Mit leichtem Anknüpfungspunkt** — *„Messtechnik. Instrumente für Labore und Institute."* Näher an Arends Welt, ohne direkt darauf zuzusteuern. Riskanter, aber öffnet eine Brücke.
3. **Ausweichend, charmant** — *„Das Langweiligste, was Sie heute Abend hören werden."* Dreht die Frage um, lädt Arend ein, das Gespräch woanders hinzuführen.
4. **Freie Aktion.**

**Dusk [Tarek]:** Option eins, aber ich lasse es kurz atmen bevor ich antworte.

„Optik. Präzisionsglas, Linsen — hauptsächlich für Werkzeugbau." Eine kleine Pause, beiläufig. „Nichts, das man auf Partys erklärt."

**Echo [Sven]:** Eingang still. Kellner ist durch, niemand wartet auf einen Tisch.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 2 — 20:36 Uhr. CHA-Probe läuft.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — Antwort auf Glaubwürdigkeit prüfen → W10: [4] + ⌊8/2⌋ (4) + 0 = 8 vs SG 8 → ERFOLG (knapp)`

---

Arend hört zu. Die kleine Pause vor der Antwort, das beiläufige Ende — er registriert beides. Dann kommt das Geringste, was er tun kann: ein kurzes, fast unmerkliches Nicken.

*„Optik."* Er wiederholt das Wort nicht als Frage, sondern als Ablage. Eingeordnet, abgeheftet. *„Brauchbares Handwerk."*

Pelz lacht leise. *„Felix hält alles für brauchbar, was sich messen lässt."*

*„Das stimmt."* Arend zieht seinen Läufer — der erste lange Zug der zweiten Partie. Er schaut dabei nicht auf Dusk, aber die Schultern haben sich minimal gesenkt. Nicht Vertrauen. Aber das Gegenteil von Misstrauen.

Drei Minuten laufen still. Die Partie entwickelt sich. Pelz verliert einen zweiten Bauern, schüttelt den Kopf. Draußen auf dem Ring fährt eine Straßenbahn vorbei, das Rattern kommt durch die Fenster.

Dann, ohne Anlass:

*„Linsen für Werkzeugbau."* Arend spricht leise, halb zu sich. *„Wir haben im Institut gerade ein Problem mit einem Messokular. Ausschuss aus Jena, zweite Lieferung in Folge."*

Er schaut kurz zu Dusk. Nicht fragend — aber offen. Als würde er testen, ob das auf fruchtbaren Boden fällt.

`Kodex: Arend hat ein Gesprächsangebot gemacht. Unaufgefordert, fachlich, persönlich. Tarnstatus stabil — Karl Brenner ist für Arend jetzt ein Mensch, kein Fragezeichen. Nächste Probe bei Versuch, Gespräch Richtung Kryptographie/HERON zu lenken: SG 10.`

Echo vom Nebentisch: Eingang sauber. Kellner wischt einen Tisch ab, schaut nicht her. Der Raum gehört euch. [3]

---

Arend hat die Tür aufgemacht. Schmal, fachlich — aber er hat sie aufgemacht.

**Was antwortet Dusk?**

1. **Fachlich einsteigen** — Konkrete Frage zum Messokular, Herstellerproblem, Toleranzen. Brenner kennt sich aus, das Gespräch vertieft sich natürlich.
2. **Brücke bauen** — *„Jena hat seit zwei Jahren Qualitätsprobleme — wir liefern inzwischen an mehrere Institute direkt."* Öffnet einen Kontakt-Subtext, ohne ihn auszusprechen.
3. **Persönlich nehmen** — *„Was für ein Institut, wenn ich fragen darf?"* Direkt, aber nicht aufdringlich. Arend entscheidet, wie viel er sagt.
4. **Freie Aktion.**

**Dusk [Tarek]:** Jena. Ich kenne das Problem — die zweite Charge hatte andere Schliffparameter als die erste, kaum messbar, aber bei Mesokularen merkst du es sofort.

Eine kurze Pause, dann ruhig: Wir haben das bei zwei Instituten in Leipzig gehabt. Wenn es dieselbe Serie ist, liegt der Fehler beim Zentrier-Schritt, nicht beim Glas selbst.

**Echo [Sven]:** Raum ist ruhig. Ich notiere die Uhrzeit.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 3 — Café Landtmann · 20:38 Uhr. CHA-Probe läuft — Arend, fachliche Glaubwürdigkeit.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — fachliche Substanz prüfen → W10: [8] + ⌊8/2⌋ (4) + 0 = 12 vs SG 10 → ERFOLG`

---

Arend legt die Figur ab.

Nicht mechanisch — er legt sie bewusst ab, dreht sich zu Dusk, und zum ersten Mal seit dem Hinsetzen schaut er ihn direkt an. Nicht prüfend. Interessiert.

*„Zentrier-Schritt."* Er wiederholt es leise, als würde er die Worte auf Gewicht prüfen. *„Genau das. Wir haben drei Wochen gesucht, der Lieferant hat bestritten, der Hersteller hat bestritten — und am Ende war es die Fassung, nicht das Glas."*

Pelz hebt die Hände. *„Ich habe gesagt, es ist die Fassung."*

*„Du hast geraten."* Arend klingt nicht unfreundlich. Er schaut wieder zu Dusk. *„Zwei Institute in Leipzig, sagen Sie. Welche?"*

Eine echte Frage. Kein Test mehr — Neugier.

`Kodex: Arend — Vertrauen Stufe 2 erreicht. Misstrauen ruhend. Gespräch läuft auf Augenhöhe. Nächste Probe bei Lenkungsversuch Richtung Kryptographie/Institut/HERON: SG 11.`

---

Pelz lehnt sich zurück, die Partie für einen Moment vergessen. Er beobachtet Arend mit dem Ausdruck eines Mannes, der seinen Freund selten so reden sieht.

Echo vom Nebentisch: 20:39 Uhr notiert. Raum ruhig. Kellner hat den letzten freien Tisch am Fenster freigemacht — ein Paar ist gegangen. Eingang sauber. [3]

Draußen auf dem Ring rattert wieder eine Straßenbahn. Das Kerzenlicht an der Wand bewegt sich kurz.

---

Karl Brenner aus Graz muss jetzt zwei Institutnamen nennen, die sitzen. Und danach — irgendwann in den nächsten Minuten — muss das Gespräch eine Richtung bekommen, die Arend nicht selbst wählt.

**Was antwortet Dusk — und wie führt ihr das Gespräch weiter?**

1. **Zwei Namen, glaubwürdig** — *„Das Hygiene-Institut und die Physikalische Gesellschaft — beide haben denselben Liefervertrag."* Konkret, hält den Faden, Arend bleibt interessiert.
2. **Namen plus Brücke** — *„Hygiene-Institut und ein mathematisches Institut, ich glaube Angewandte — ähnliche Präzisionsanforderungen wie bei Ihnen, nehme ich an?"* Öffnet den Weg zu Arends eigenem Institut, ohne direkt zu fragen.
3. **Namen plus persönliche Wendung** — *„Hygiene-Institut und die Physikalische Gesellschaft. Aber ehrlich gesagt interessiert mich mehr, was Ihr Institut damit macht — Mesokulare sind kein Standardwerkzeug."* Direkt, riskanter, aber Arend könnte es honorieren.
4. **Freie Aktion.**

**Dusk [Tarek]:** Hygiene-Institut und die Physikalische Gesellschaft — beide haben denselben Rahmenvertrag laufen, soweit ich weiß.

Eine kurze Pause, dann beiläufig, als wäre es nur eine logische Folgefrage: Ähnliche Präzisionsanforderungen wie bei Ihnen, nehme ich an — oder arbeitet Ihr Institut mit anderen Toleranzen?

**Echo [Sven]:** Eingang noch sauber. Ich halte die Uhr im Blick.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 3 — Café Landtmann · 20:39 Uhr. CHA-Probe läuft — Arend, Lenkungsversuch Richtung Institut.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — Lenkungsversuch registriert, Reaktion → W10: [3] + ⌊8/2⌋ (4) + 0 = 7 vs SG 11 → MISS`

---

Arend hört die Frage. Und er hört *die Frage in der Frage*.

Nicht dramatisch — kein Auffahren, kein Misstrauen im Gesicht. Nur eine minimale Veränderung: die Finger, die auf dem Tisch lagen, kommen zurück ans Brett. Er nimmt seinen Turm, setzt ihn ab, schaut auf das Spiel.

*„Angewandte Mathematik hat keine Mesokulare."*

Kurz. Sachlich. Kein Vorwurf darin — aber die Tür, die eben noch einen Spalt offen stand, ist wieder geschlossen. Nicht verriegelt. Nur zu.

Pelz hebt kurz die Augenbraue, sagt nichts.

Arend hat die Lenkung gespürt. Nicht als Bedrohung — aber als etwas Unnatürliches in einem Gespräch, das bis jetzt natürlich war. Ein Handelsvertreter aus Graz fragt nicht nach den Toleranzanforderungen eines fremden Instituts. Das tut man nicht, wenn man Linsen verkauft. Das tut man, wenn man etwas wissen will.

Er spielt weiter. Die Partie läuft. Aber das Thermometer im Raum hat sich um zwei Grad gesenkt.

`Kodex: Arend — Misstrauen reaktiviert, niedrige Stufe. Tarnstatus unter Druck. Nächste CHA-Probe zum Zurückgewinnen: SG 10. Kein direkter Lenkungsversuch mehr möglich ohne vorherige Stabilisierung.`

Echo vom Nebentisch, leise: Eingang sauber. 20:41 Uhr. Pelz geht in knapp achtzig Minuten.

---

Das Gespräch hat einen Riss bekommen. Nicht tief — aber Arend ist wieder auf der Hut. Die Stimmung am Tisch ist nicht feindselig, nur abgekühlt. Pelz füllt die Stille mit einem Kommentar über seinen Springer, halb zu sich selbst.

Dusk hat zwei Möglichkeiten: den Riss kitten, bevor er größer wird — oder ihn stehen lassen und auf einen anderen Moment warten.

**Was tut ihr?**

1. **Riss kitten, zurückrudern** — Dusk lacht kurz, locker. *„Verzeihung — Berufsdeformation. Man fängt an, überall Spezifikationen zu sehen."* Nimmt den Druck raus, gibt Arend Raum.
2. **Stille halten** — nichts sagen, das Brett beobachten, Arend den Rhythmus zurückgeben. Riskant, aber manchmal ist Schweigen glaubwürdiger als eine Erklärung.
3. **Pelz anspielen** — Gespräch zu Pelz drehen, Arend aus dem Fokus nehmen. Indirekter Druck raus, Arend kann selbst entscheiden, ob er wieder einsteigt.
4. **Freie Aktion.**

**Dusk [Tarek]:** Ich lache kurz — nicht verlegen, eher selbstkritisch, das Lächeln eines Mannes, der seine eigene Marotte kennt.

„Entschuldigung. Wenn man zu lange in Spezifikationen denkt, fängt man an, Gespräche wie Lieferscheine zu lesen."

Ich nehme einen Schluck Kaffee, schaue auf das Brett — nicht auf Arend.

**Echo [Sven]:** Ich tippe leise, ohne Betonung — für Dusk, nicht für Arend:

Gut reagiert. Lass ihm Luft. Pelz redet gerade — nutz das.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 3 — 20:42 Uhr. CHA-Probe läuft — Riss kitten, Misstrauen senken.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — Selbstkorrektur glaubwürdig → W10: [7] + ⌊8/2⌋ (4) + 0 = 11 vs SG 10 → ERFOLG`

---

Das kurze Lachen sitzt.

Nicht zu laut, nicht zu selbstkritisch — genau so, wie ein Mann lacht, der eine eigene Eigenheit kennt und sich nicht dafür entschuldigt, sondern sie benennt. Arend hört es. Die Finger, die am Turm lagen, lösen sich.

Er sagt nichts. Aber die Schultern senken sich wieder.

Pelz springt in die Lücke — er hat auf einen Moment gewartet, wo er reden darf.

*„Felix ist genauso. Er liest Menüs wie Tabellen."* Er deutet auf Arend. *„Im Sommer haben wir in Salzburg gegessen, er hat dem Kellner erklärt, warum die Portionsangaben inkonsistent sind."*

Arend hebt kurz die Hand. *„Sie waren inkonsistent."*

Pelz lacht. Das Gespräch ist wieder warm.

Arend zieht seinen Läufer — ein langer, ruhiger Zug, der Pelz in die Defensive bringt. Dann, ohne aufzuschauen, mit der beiläufigen Tonlage eines Mannes, der eine Bemerkung macht, nicht eine Frage stellt:

*„Spezifikationen sind präzise. Gespräche nicht. Das ist kein Fehler — das ist der Unterschied zwischen Werkzeug und Sprache."*

Er schaut kurz zu Dusk. Nicht prüfend diesmal. Fast kollegial.

`Kodex: Arend — Misstrauen auf Null. Vertrauen Stufe 2 wiederhergestellt. Tarnstatus stabil. Gespräch läuft auf Augenhöhe. Pelz aktiv als Puffer.`

---

Echo vom Nebentisch, Knochenleitung, kaum hörbar: *Gut reagiert. Lass ihm Luft. Pelz redet gerade — nutz das.*

Pelz studiert das Brett, schüttelt den Kopf. *„Felix, du hast mir gerade den Turm genommen und dabei einen Fremden philosophisch belehrt. Das ist unfair."*

*„Du hattest den Turm schlecht gestellt."*

Draußen auf dem Ring rattert eine Straßenbahn. Das Kerzenlicht an der Wand bewegt sich nicht mehr — die Luft im Café ist warm und still. Pelz geht in sechzig Minuten.

Der Raum gehört euch.

`Kodex: Zeitfenster — Pelz noch ~60 Minuten. Arend bleibt danach allein, schätzungsweise 20–30 Minuten. Nächste natürliche Gesprächsöffnung: wenn Pelz einen Zug überlegt und verstummt — Arend hat dann keine Ablenkung.`

---

**Was tut ihr?**

1. **Warten, Brett beobachten** — Arend hat das Gespräch geöffnet, Dusk lässt es atmen. Nächste Öffnung kommt von selbst.
2. **Leicht einsteigen** — Dusk antwortet auf Arends Bemerkung über Sprache und Werkzeug. Kurz, ohne Lenkung. Gespräch vertiefen, ohne zu drängen.
3. **Echo repositioniert** — näher an den Ausgang, für den Fall dass Arend beim Rausgehen abgefangen werden muss. Vorbereitende Bewegung, unauffällig.
4. **Freie Aktion.**

**Dusk [Tarek]:** Brett liegt gut. Ich warte, bis Pelz seinen Zug sucht.

**Echo [Sven]:** Option 3 läuft parallel. Ich verschiebe mich langsam zur Garderobe — Jacke holen, als würde ich kurz frieren. Ausgang im Blick, falls Arend früher geht als geplant.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 3 — Café Landtmann · 20:44 Uhr. Tarnstatus stabil. Echo repositioniert.`

---

Pelz beugt sich vor, die Ellbogen auf den Tisch, und starrt auf das Brett. Sein Springer steht schlecht — er weiß es, Arend weiß es, und jetzt schweigt Pelz mit der Konzentration eines Mannes, der einen Fehler rückgängig machen will, den er vor drei Zügen gemacht hat.

Arend wartet. Er hat Zeit.

Echo steht auf, langsam, streckt sich kurz — ein Mann, dem kalt ist. Er geht zur Garderobe, nimmt die Jacke vom Haken, bleibt einen Moment stehen als würde er die Knöpfe schließen. Vom Eingang aus hat er den Tisch im Rückspiegel der Fensterscheibe. Arend schaut nicht her.

`Kodex: Echo — Ausgangsposition gesichert. Sichtlinie Eingang + Arend-Tisch via Fensterreflex. Beruhigungsmittel griffbereit.`

---

Pelz zieht. Falsch, wie erwartet.

Arend nimmt den Springer ohne Kommentar.

Dann lehnt er sich zurück — nicht weit, aber genug, dass die Partie für einen Moment Pause hat. Er schaut auf seinen Mokka, der kalt geworden ist. Bestellt mit einer kleinen Handbewegung einen neuen.

Und dann, ohne Anlass, ohne Lenkung von Dusks Seite:

*„Sie sagten, Gespräche lesen sich wie Lieferscheine."* Er schaut nicht auf — aber er spricht zu Dusk, das ist klar. *„Das kenne ich. Ich lese Texte wie Codes. Suche nach dem Muster unter den Worten."*

Eine Pause. Der Kellner bringt den Mokka.

*„Meistens finde ich es."*

Er sagt es ruhig, beinahe beiläufig. Aber es ist kein beiläufiger Satz.

`Kodex: Arend hat eine persönliche Aussage gemacht — unaufgefordert, direkt an Dusk. Kein Lenkungsversuch nötig. Er öffnet selbst. Nächste Probe bei Antwort: SG 9. W10 + ⌊CHA 8/2⌋.`

---

Pelz schaut zwischen beiden hin und her, sagt nichts. Er kennt diesen Ton bei Arend — selten, aber wenn er kommt, bedeutet er, dass jemand Arends Interesse gewonnen hat.

Draußen auf dem Ring: Stille zwischen zwei Straßenbahnen. Das Café ist warm. Pelz geht in vierzig Minuten.

---

**Was antwortet Dusk?**

1. **Ruhig, direkt** — *„Und wenn Sie es nicht finden?"* Kurz, ohne Druck. Lässt Arend entscheiden, wie weit er geht.
2. **Spiegelnd** — *„Manche Muster sind dafür gemacht, nicht gefunden zu werden."* Öffnet eine zweite Ebene, ohne sie zu benennen.
3. **Persönlich** — *„Ich suche es auch. Meistens in den Pausen zwischen den Worten."* Zeigt Arend, dass Brenner ähnlich denkt. Wärmer, näher.
4. **Freie Aktion.**

**Dusk [Tarek]:** Manche Pausen sagen mehr als die Worte selbst — man muss nur still genug sein, um sie zu hören.

Ich schaue kurz vom Brett auf, nicht lange, und nehme einen Schluck Kaffee.

**Echo [Sven]:** Dusk, Arend ist grade offen — bleib genau da. Nichts forcieren.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 3 — 20:45 Uhr. CHA-Probe läuft — Arend, persönliche Ebene.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — Resonanz auf persönliche Antwort → W10: [9] + ⌊8/2⌋ (4) + 0 = 13 vs SG 9 → ERFOLG`

---

Arend sagt nichts sofort.

Er nimmt seinen Mokka, hält ihn mit beiden Händen — die Geste eines Mannes, der nachdenkt, nicht trinkt. Pelz hat einen Zug gefunden, beugt sich vor, ist beschäftigt. Der Tisch gehört für einen Moment nur Arend und Dusk.

Dann:

*„Ja."*

Ein einzelnes Wort. Ruhig, ohne Betonung. Aber er meint es.

Er schaut kurz zu Dusk — nicht prüfend, nicht katalogisierend. Zum ersten Mal an diesem Abend schaut er ihn an wie einen Menschen, nicht wie eine Variable.

*„Die meisten Leute füllen Pausen."* Er stellt den Mokka ab. *„Mit Wörtern, mit Lärm, mit Bewegung. Als wäre Stille ein Fehler, den man korrigieren muss."*

Eine kurze Pause — bewusst, fast ironisch.

*„Sie nicht."*

`Kodex: Arend — Vertrauen Stufe 3 erreicht. Persönliche Ebene aktiv. Misstrauen inaktiv. Gespräch trägt jetzt sein eigenes Gewicht.`

---

Pelz zieht, schaut auf, bemerkt den Ton zwischen den beiden — und lächelt kurz in sein Schachbrett. Der alte Professor hat das schon öfter gesehen: Arend, der plötzlich redet.

Echo an der Garderobe, Knochenleitung kaum hörbar: *Dusk, Arend ist grade offen — bleib genau da. Nichts forcieren.*

Draußen auf dem Ring: absolute Stille zwischen zwei Straßenbahnen. Das Café atmet warm und ruhig. Pelz geht in fünfunddreißig Minuten.

Das Gespräch hat eine Tiefe erreicht, die ihr nicht erzwungen habt. Arend hat sie selbst aufgemacht.

`Kodex: Zeitfenster — 35 Minuten bis Pelz geht. Arend danach allein ~20 Minuten. Nächste natürliche Brücke möglich: Arend redet über Arbeit, Muster, Verschlüsselung — aus eigenem Antrieb, wenn das Gespräch weiterläuft.`

---

**Was tut ihr?**

1. **Stille halten** — Dusk nickt kurz, sagt nichts. Lässt Arend den nächsten Schritt machen.
2. **Leicht öffnen** — *„Manche Dinge lassen sich nicht in Worte fassen. Man kann sie nur zeigen."* Hält die Ebene, lädt Arend ein weiterzugehen.
3. **Persönlich werden** — Dusk stellt Arend eine echte Frage. Nicht über die Arbeit — über ihn. Riskant, aber Arend ist gerade offen.
4. **Freie Aktion.**

**Dusk [Tarek]:** Ich nicke einmal, kurz — eher Bestätigung als Antwort.

Dann, nach einem Moment: „Stille kostet etwas. Die meisten merken das erst, wenn sie sie verloren haben."

Ich schaue wieder auf das Brett.

**Echo [Sven]:** Verstanden. 35 Minuten, Arend redet gerade von selbst — das ist selten. Pelz geht um 21:20, ich bleibe an der Garderobe und halte den Ausgang offen.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 3 — 20:46 Uhr. CHA-Probe läuft — Arend, persönliche Tiefe.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — Resonanz auf persönliche Aussage → W10: [10] + ⌊8/2⌋ (4) + 0 = 14 vs SG 9 → KRITISCHER ERFOLG (Exploding W10)`

`Probe: Exploding — W10: [3] + 14 = 17 vs SG 9 → KRITISCHER ERFOLG`

---

Arend hört den Satz. Legt den Läufer ab.

Nicht sofort — er lässt ihn stehen, die Hand noch daran, und schaut auf das Brett, aber er sieht das Brett nicht mehr. Dusk kann es sehen: die Augen, die irgendwo anders sind. Ein Mann, der etwas gehört hat, das er sich selbst schon gesagt hat, aber nie laut.

Pelz merkt es. Er schaut kurz zu Dusk, dann zu Arend, und entscheidet sich, seinen Zug zu überlegen.

*„Ja."*

Arend sagt es leise. Dann, nach einem Moment:

*„Ich habe drei Jahre an etwas gearbeitet."* Er spricht nicht zu Dusk, nicht zu Pelz — er spricht in den Raum, die Stimme ruhig und präzise wie immer, aber etwas darunter ist anders. *„Etwas, das ich für wichtig hielt. Das ich für notwendig hielt."*

Eine Pause. Draußen auf dem Ring fährt eine Straßenbahn vorbei, das Rattern kommt und geht.

*„Ich habe es vernichtet."*

Pelz hebt kurz den Kopf — nicht überrascht, aber aufmerksam. Er kennt die Geschichte, oder Teile davon.

*„Weil es in den falschen Händen —"* Arend bricht ab. Schüttelt minimal den Kopf. *„Stille kostet etwas. Das stimmt. Ich habe bezahlt."*

Er nimmt seinen Läufer. Zieht. Die Partie läuft weiter.

Aber er schaut zu Dusk — kurz, direkt, und diesmal liegt darin keine Prüfung mehr. Eher die Frage eines Mannes, der entschieden hat, dass sein Gegenüber zuhören kann.

`Kodex: Arend — Vertrauen Stufe 4 (Maximum für diesen Abend). Er hat von HERON gesprochen, ohne es zu benennen. Drei Jahre Arbeit, vernichtet, weil es in falschen Händen gefährlich wäre. Nächste Probe bei direkter Frage nach dem Inhalt: SG 12. Kein Lenkungsversuch nötig — Arend führt das Gespräch selbst.`

`Kodex: Kritischer Erfolg — Arend wird nach Pelz' Abgang nicht sofort gehen. Er bleibt.`

---

Echo an der Garderobe, Knochenleitung kaum hörbar: ruhig, keine Bewegung am Eingang, 34 Minuten bis Pelz geht.

Pelz hat seinen Zug gefunden. Er zieht, schüttelt den Kopf über sein eigenes Brett, murmelt etwas auf Wienerisch.

Der Raum ist warm. Das Café atmet.

Arend wartet, was Dusk sagt.

---

**Was antwortet Dusk — und wie führt ihr das Gespräch in den nächsten Minuten?**

1. **Ruhig, ohne Druck** — *„Manche Dinge sind zu wichtig, um sie dem Zufall zu überlassen."* Hält die Ebene, gibt Arend Raum weiterzugehen.
2. **Direkt, aber sanft** — *„Was war es?"* Kurz, ohne Umweg. Arend hat die Tür geöffnet — das ist die direkte Frage. Riskant, aber er ist gerade offen wie selten.
3. **Spiegelnd** — *„Vernichten ist eine Form von Kontrolle. Die einzige, die man manchmal noch hat."* Zeigt Arend, dass Dusk versteht — ohne zu fragen.
4. **Freie Aktion.**

**Dusk [Tarek]:** Ich lasse einen Moment vergehen, bevor ich antworte — lange genug, damit er weiß, dass ich es nicht einfach gehört, sondern behalten habe.

„Vernichten ist eine Form von Kontrolle. Die einzige, die man manchmal noch hat."

**Echo [Sven]:** Verstanden. Arend redet — ich rühre mich nicht. 34 Minuten, Eingang ruhig, Garderobe im Blick.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 3 — 20:47 Uhr. CHA-Probe läuft — Arend, Resonanz auf Spiegelung.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — Spiegelung verarbeiten → W10: [6] + ⌊8/2⌋ (4) + 0 = 10 vs SG 9 → ERFOLG`

---

Arend hört den Satz. Setzt seinen Läufer ab.

Diesmal keine Pause — er dreht sich zu Dusk, direkt, und schaut ihn an. Nicht prüfend, nicht katalogisierend. Der Blick eines Mannes, der etwas gehört hat, das er selbst gedacht hat, aber nie so formuliert hätte.

Pelz hebt den Kopf kurz — er spürt den Ton, sagt nichts, schaut wieder auf sein Brett.

*„Ja."* Arend spricht leise. *„Genau das."*

Er nimmt seinen Mokka. Hält ihn, trinkt nicht.

*„Ich habe drei Jahre gearbeitet. Nicht für einen Auftraggeber — für mich. Weil ich ein Problem sah und glaubte, ich könnte es lösen."* Eine kurze Pause. Das Rattern einer Straßenbahn draußen, dann wieder Stille. *„Das Problem war lösbar. Das war das eigentliche Problem."*

Er stellt den Mokka ab.

*„Wenn etwas funktioniert — wirklich funktioniert — dann gehört es niemandem mehr. Dann gehört es jedem, der es haben will."*

Er schaut kurz auf das Brett, dann wieder zu Dusk.

*„Also habe ich es vernichtet. Die Aufzeichnungen, die Entwürfe, alles."* Minimal, fast unmerklich: *„Fast alles."*

Das letzte Wort liegt im Raum.

Pelz hat es gehört. Er schaut nicht auf — aber er hat aufgehört zu überlegen.

`Kodex: Arend — kritische Aussage. "Fast alles." HERON existiert noch, zumindest in Teilen. Arend trägt etwas — physisch oder im Gedächtnis. Keine Probe nötig für diesen Beat — er hat es freiwillig gesagt. Nächste Probe bei direkter Frage nach dem Rest: SG 13.`

---

Der Raum ist still. Pelz rührt sich nicht. Echo an der Garderobe hält die Position.

Arend wartet nicht auf eine Antwort — aber er hat sie noch nicht weggenommen. Der Satz hängt noch in der Luft zwischen ihm und Dusk.

*Fast alles.*

---

**Was tut ihr?**

1. **Stille halten** — nichts sagen. Arend hat das Wichtigste schon gesagt. Warten, ob er weitermacht.
2. **Ruhig nachfassen** — *„Fast."* Ein einziges Wort. Keine Frage, keine Forderung — nur eine Bestätigung, dass Dusk es gehört hat.
3. **Indirekt** — *„Manche Dinge lassen sich nicht vollständig vernichten. Die Idee bleibt."* Gibt Arend Raum, ohne direkt zu fragen.
4. **Freie Aktion.**

**Dusk [Tarek]:** Fast alles.

Ich wiederhole es nicht als Frage — nur leise, als würde ich das Gewicht davon abmessen.

Dann nehme ich einen Schluck Kaffee und schaue auf das Brett.

**Echo [Sven]:** Garderobe ruhig. Ich halte.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 3 — 20:48 Uhr. CHA-Probe läuft — Arend, Reaktion auf Echo.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — Reaktion auf "Fast alles" → W10: [8] + ⌊8/2⌋ (4) + 0 = 12 vs SG 9 → ERFOLG`

---

*Fast alles.*

Dusk sagt es wie eine Feststellung. Kein Fragezeichen, kein Druck. Nur das Gewicht des Wortes, zurückgegeben.

Arend hört es.

Er schaut nicht auf. Die Hand liegt auf dem Tisch, flach, neben dem Brett. Pelz hat aufgehört zu überlegen — er sitzt still, die Augen auf sein Glas gesenkt, ein Mann der weiß, wann er unsichtbar sein soll.

Drei Sekunden. Vier.

*„Es gibt eine Kopie."*

Arend spricht leise, fast zu leise für den Raum — aber der Raum ist still genug. *„Nicht vollständig. Ein Drittel, vielleicht. Die Grundstruktur, nicht die Anwendung."*

Er hebt kurz die Augen, schaut auf das Brett.

*„Ich habe sie behalten, weil ich dachte — ich weiß nicht, was ich dachte. Dass es vielleicht eines Tages jemanden geben würde, der sie versteht. Der sie richtig versteht."*

Eine Pause. Draußen auf dem Ring absolute Stille.

*„Das war naiv."*

Er zieht seinen Turm. Die Partie läuft weiter, mechanisch, als wäre das Gespräch ein anderer Raum.

`Kodex: Arend — HERON-Kopie bestätigt. Partiell, ein Drittel, Grundstruktur. Physisch vorhanden. Standort unbekannt. Nächste Probe bei Frage nach Standort oder Übergabe: SG 13.`

---

Pelz hebt jetzt den Kopf. Er schaut Arend an — nicht überrascht, aber ernst. Der Blick zweier Männer, die eine alte Unterhaltung ohne Worte fortsetzen.

Dann schaut Pelz zu Dusk. Kurz, direkt. Einschätzend.

Er sagt nichts. Aber er hat Dusk gerade anders eingeordnet.

`Kodex: Pelz — aufmerksam. Kein Misstrauen, aber er beobachtet jetzt. Geht in 28 Minuten.`

Echo an der Garderobe, Knochenleitung: Garderobe ruhig. Eingang sauber.

---

Arend hat etwas gesagt, das er wahrscheinlich seit Monaten nicht gesagt hat. Vielleicht Jahren. Er hat es gesagt, weil die letzten zwanzig Minuten eine Atmosphäre geschaffen haben, in der es möglich war.

Das Fenster ist offen. Schmal — aber offen.

**Was tut ihr?**

1. **Ruhig halten** — nichts sagen. Arend hat das Schwerste gerade ausgesprochen. Raum lassen, er führt weiter.
2. **Leicht öffnen** — *„Vielleicht gibt es diesen jemanden."* Kein Druck, keine Erklärung. Arend entscheidet, was er damit macht.
3. **Pelz einbeziehen** — Dusk schaut kurz zu Pelz, ein kleines Nicken. Signalisiert, dass er den Blick registriert hat und nichts versteckt. Vertrauensaufbau zu beiden gleichzeitig.
4. **Freie Aktion.**

**Dusk [Tarek]:** Ich schaue kurz zu Pelz — nicht lang, keine Erklärung, nur ein kleines Nicken, das sagt: ich weiß, dass du zuhörst, und das ist in Ordnung.

Dann wieder zu Arend, ruhig: „Vielleicht gibt es diesen jemanden."

Kein Druck dahinter. Nur das Wort, hingestellt.

**Echo [Sven]:** Garderobe still. Pelz geht in 28 — ich halte die Route frei und gebe Bescheid, sobald er durch ist.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 4 — Café Landtmann · 20:49 Uhr. CHA-Probe läuft — Arend, Reaktion auf Angebot.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — "Vielleicht gibt es diesen jemanden" → W10: [7] + ⌊8/2⌋ (4) + 0 = 11 vs SG 9 → ERFOLG`

---

Arend hört den Satz.

Er schaut Dusk an — lange, für seine Verhältnisse. Drei Sekunden, vier. Der Blick eines Mannes, der gelernt hat, Angebote auf ihre Kosten hin zu lesen, und der gerade nicht sicher ist, was dieses kostet.

Dann schaut er zu Pelz.

Pelz hat die Zeitung wieder aufgeklappt. Er liest nicht — aber er gibt Arend den Raum, den er gerade braucht.

Arend dreht seinen Läufer zwischen den Fingern. Einmal, zweimal.

*„Das sagen viele."* Nicht feindselig. Nur präzise. *„Die meisten meinen es nicht so, wie sie es sagen."*

Er stellt den Läufer ab. Zieht ihn. Die Partie läuft weiter.

*„Aber Sie haben zugehört."* Fast zu sich. *„Das ist selten."*

Eine lange Pause. Draußen rattert eine Straßenbahn, kommt und geht. Das Café atmet warm.

*„Ich wohne in der Josefstadt."* Er spricht es beiläufig aus, die Augen auf dem Brett. *„Piaristengasse 7, zweiter Stock. Wenn jemand die Grundstruktur sehen will — nicht verwenden, nur verstehen — dann weiß er jetzt, wo."*

Er schaut nicht auf. Zieht seinen Turm.

*„Ich gehe heute Nacht gegen halb elf."*

`Kodex: Arend — Einladung ausgesprochen. Piaristengasse 7, zweiter Stock. Heute Nacht, 22:30 Uhr. Freiwillig, ohne Druck. Hauptziel erreichbar ohne Festnahme im Café — Opt.-Ziel HERON-Dokument in Reichweite.`

---

Pelz legt die Zeitung ab. Er schaut Arend an — kurz, mit dem Ausdruck eines Mannes, der seinen Freund seit sechs Jahren kennt und ihn gerade etwas tun sieht, das er selten tut.

Er sagt nichts. Aber er nickt minimal — zu sich selbst, nicht zu Dusk.

`Kodex: Pelz — kein Risiko. Er hat es registriert und lässt es geschehen.`

---

Echo, Knochenleitung, kaum hörbar: *Garderobe still. 28 Minuten bis Pelz geht. Route frei.*

Die zweite Partie läuft weiter. Arend spielt jetzt schneller — nicht nervös, eher entschieden. Ein Mann, der eine Wahl getroffen hat und damit fertig ist.

`Kodex: Zeitfenster — Pelz geht ~21:17 Uhr. Arend verlässt Café ~22:30 Uhr. Fenster für Positionierung Piaristengasse: 70 Minuten.`

---

`EP 12 · MS 12 · SC 04/12 · PHASE Intel · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 0/10 · 👁️ Getarnt (sozial)`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 0/10 · 👁️ Getarnt (sozial)`
`Px 0/5 · Obj: Arend festnehmen · Exfil: IA Stephansdom-Krypta · T- offen`

`Kodex: Szene 4 — Café Landtmann / Josefstadt-Vorbereitung · 20:49 Uhr.`

---

Arend hat die Tür geöffnet. Nicht weit — aber er hat sie geöffnet.

Piaristengasse 7. Zweiter Stock. Halb elf.

Ihr habt siebzig Minuten, um euch zu positionieren, die Wohnung zu sondieren und zu entscheiden, wie ihr die nächste Phase spielt. Eine Festnahme in der Wohnung ist kontrollierbar — kein Publikum, kein Café-Personal, kein Pelz. Aber Arend ist vorsichtig, und er hat die Einladung freiwillig ausgesprochen, was bedeutet: er erwartet jemanden, der *zuhört*, nicht jemanden, der *nimmt*.

**Was tut ihr in den nächsten siebzig Minuten?**

1. **Café verlassen, Piaristengasse sondieren** — Wohnung und Umgebung vor Arends Ankunft prüfen. Hinterhof-Aufgang, Fenster, mögliche Beobachtungsposten, ob die Wohnung bereits unter Beobachtung steht.
2. **Café noch kurz halten** — Pelz' Abgang abwarten, Arend noch einmal beobachten. Sicherstellen, dass er nach dem Gespräch niemanden kontaktiert.
3. **Aufgabenteilung** — Dusk bleibt im Café bis Arend geht, Echo übernimmt die Vorab-Sondierung der Piaristengasse allein.
4. **Freie Aktion.**

**Dusk [Tarek]:** Option 3.

Echo, ich verlasse das Café in fünf Minuten — du nimmst die Piaristengasse, Hinterhof zuerst, und ich halte Arend im Blick bis er geht. Gib mir Bescheid, sobald du weißt, ob die Wohnung sauber ist.

**Echo [Sven]:** Verstanden — ich gehe jetzt. Piaristengasse 7, Hinterhof zuerst, dann Aufgänge und Fenster zweiter Stock. Ich gebe dir Bescheid, sobald ich weiß, ob wir dort allein sind.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 5 — Café Landtmann / Piaristengasse 7 · 20:52 Uhr. Aufgabenteilung aktiv.`

---

Echo steht auf, unauffällig — ein Mann, der Luft braucht. Er legt eine Münze auf den Tisch, nickt dem Kellner kurz zu und geht durch die Eingangstür. Kalte Herbstluft, der Ring liegt orangegelb im Gaslicht. Er dreht nach rechts, weg vom Café, und verschwindet in den Nebenstraßen Richtung Josefstadt.

Am Tisch: Arend und Pelz spielen weiter. Die zweite Partie läuft in ihre Endphase. Arend ist besser — er gewinnt, langsam, methodisch, ohne Eile. Pelz kämpft mit dem Mittelfeld.

Dusk bestellt einen dritten Kaffee. Karl Brenner aus Graz, der einen ruhigen Abend hat.

---

**Echo — Piaristengasse 7, 20:58 Uhr**

`Kodex: Probe-Template — GES-Probe, Sondierung Hinterhof / Aufgang unbemerkt. 1W10 + ⌊GES 6/2⌋ + Talent + Gear.`

`Probe: Sondierung Hinterhof → W10: [6] + ⌊6/2⌋ (3) + Feldroutine Meister +2 = 11 vs SG 7 → ERFOLG`

---

Die Piaristengasse ist ruhig. Kopfsteinpflaster, Gaslampen, ein Kastanienbaum am Bordstein, der letzte Blätter verliert. Nummer 7 ist ein Gründerzeithaus, vier Stockwerke, Fassade dunkelgrau, Efeu am Hinterhof-Eingang.

Echo geht durch den Torbogen, langsam, Hände in den Manteltaschen. Handelsvertreter aus Graz, der eine Adresse sucht.

Der Hinterhof ist leer. Kopfsteinpflaster, eine Pumpe in der Mitte, zwei Fahrräder angelehnt an die Wand. Zweiter Stock: ein Fenster mit Licht dahinter — Arends Wohnung, brennt noch, er hat vergessen auszumachen oder bewusst angelassen. Das andere Fenster dunkel.

Echo scannt die Aufgänge. Zwei — Vorderhaus, Hinterhaus. Hinterhaus-Aufgang liegt im Schatten, Tür nicht abgeschlossen, Holztreppe. Vorderhaus-Aufgang durch die Haupttür, Glaseinsatz, von innen beleuchtet.

Dann: eine Kleinigkeit.

Am Vorderhaus-Aufgang, eine Etage über Erdgeschoss — ein Fenster, das einen Spalt offen steht. Kein Licht dahinter. Aber Echo sieht, sehr kurz, die Glut einer Zigarette.

Jemand wartet dort. Raucht, ohne Licht. Schaut auf den Hof.

`Kodex: Beobachter in Vorderhaus, erste Etage — Fenster offen, keine Beleuchtung, Zigarettenglut sichtbar. Identität unbekannt. Mögliche Optionen: Hausbewohner, KAIROS-Beobachtung, Zufall.`

Echo, Knochenleitung, leise: *„Dusk — Piaristengasse 7 hat einen Beobachter. Vorderhaus, erste Etage, kein Licht, Zigarette. Ich weiß noch nicht, wer das ist."*

---

**Café Landtmann, 21:03 Uhr**

Pelz hat verloren. Er legt den König um, lacht kurz, schüttelt den Kopf.

*„Wie immer."*

Arend räumt die Figuren ein — methodisch, jede Figur an ihren Platz in der Holzschachtel. Er schaut nicht auf.

Pelz zieht seinen Mantel an, legt Geld auf den Tisch. Er schaut kurz zu Dusk — nicht feindselig, aber direkt.

*„Herr Brenner."* Ein kurzes Nicken. *„Gute Reise nach Graz."*

Dann geht er. Die Eingangstür fällt hinter ihm zu.

Arend und Dusk sind allein am Tisch.

Arend schließt die Schachtel. Schaut auf seinen Mokka, der kalt ist. Bestellt keinen neuen.

`Kodex: Pelz abgegangen — 21:04 Uhr. Arend allein mit Dusk. Verlässt Café ~22:30 Uhr. 86 Minuten bis Arend zur Piaristengasse geht.`

---

`EP 12 · MS 12 · SC 05/12 · PHASE Intel · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 0/10 · 👁️ Getarnt (sozial)`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 0/10 · 👁️ Getarnt (sozial)`
`Px 0/5 · Obj: Arend festnehmen · Exfil: IA Stephansdom-Krypta · T- offen`

---

Zwei Probleme gleichzeitig.

Dusk sitzt mit Arend allein im Café — das ist das Fenster, das sie wollten. Aber in der Piaristengasse wartet jemand in einer dunklen Wohnung mit einer Zigarette, und Arend geht in sechsundachtzig Minuten dorthin.

**Was tut ihr?**

1. **Echo klärt den Beobachter** — bleibt an der Piaristengasse, versucht die Identität zu bestimmen, bevor Arend ankommt. Dusk hält Arend im Café so lange wie möglich.
2. **Dusk bewegt sich jetzt** — nutzt die Zeit allein mit Arend, um das Gespräch zu vertiefen und Arend vorzuschlagen, gemeinsam zur Piaristengasse zu gehen. Kontrolle über Timing und Route.
3. **Echo neutralisiert den Beobachter** — still, bevor Arend ankommt. Riskant, unbekanntes Ziel, aber die Wohnung muss sauber sein.
4. **Freie Aktion.**

**Dusk [Tarek]:** Echo, halt die Position — identifizier den Beobachter zuerst, bevor du irgendetwas tust. Wir wissen nicht, ob das KAIROS ist oder ein Hausbewohner, der schlechte Schlafgewohnheiten hat.

Ich habe hier noch Zeit mit Arend — ich nutze sie.

**Echo [Sven]:** Verstanden, halte Position und beobachte zurück — ich will sehen, ob der Beobachter reagiert, wenn ich mich im Hof bewege. Gib mir fünf Minuten, dann habe ich mehr für dich.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 5 läuft — Piaristengasse 7 / Café Landtmann · 21:05 Uhr. Aufgabenteilung aktiv.`

---

**Piaristengasse 7 — Echo, 21:05 Uhr**

`Kodex: Probe-Template — GES-Probe, kontrollierte Bewegung im Hof unter Beobachtung. 1W10 + ⌊GES 6/2⌋ + Feldroutine Meister +2.`

`Probe: Beobachter testen → W10: [5] + ⌊6/2⌋ (3) + Feldroutine Meister +2 = 10 vs SG 8 → ERFOLG`

---

Echo bewegt sich. Langsam, ohne Ziel — ein Mann, der eine Adresse sucht und sich im Hof verirrt hat. Er geht zur Pumpe, schaut an der Fassade hoch, dreht sich einmal um.

Das Fenster im ersten Stock bewegt sich nicht.

Aber die Zigarettenglut verschwindet.

Nicht ausgedrückt — *versteckt*. Jemand hat die Hand zurückgezogen, als Echo in den Hof trat. Ein Hausbewohner würde das nicht tun. Ein Hausbewohner würde rauchen und gleichgültig runterschauen.

Dieser hier will nicht gesehen werden.

`Kodex: Beobachter — kein Zufall. Reaktives Verhalten bestätigt: versteckt sich aktiv bei Bewegung im Hof. Identität weiterhin unbekannt. KAIROS-Profil wahrscheinlich. Keine Waffe sichtbar, keine Bewegung Richtung Ausgang.`

Echo, Knochenleitung, sehr leise: *„Dusk — kein Hausbewohner. Versteckt die Zigarette, sobald ich mich bewege. Wartet auf jemanden. Wartet auf Arend."*

---

**Café Landtmann — Dusk, 21:06 Uhr**

Arend sitzt still. Die Schachschachtel ist geschlossen, liegt vor ihm auf dem Tisch. Er schaut auf das Holz, die Finger flach daneben.

Er wartet nicht auf ein Gespräch. Aber er ist auch nicht gegangen.

Dusk hat die Meldung von Echo gehört. Arend weiß nicht, dass in seiner Wohnung jemand wartet. Arend weiß nicht, dass er heute Nacht vielleicht in eine Falle läuft.

Und Arend hat eine Kopie von HERON in der Piaristengasse 7.

`Kodex: Entscheidungspunkt — Arend verlässt Café ~22:30 Uhr. Beobachter wartet in Vorderhaus. Optionen: Arend warnen (bricht Tarnung Karl Brenner, aber rettet HERON und Arend), Arend abfangen vor der Wohnung, Beobachter neutralisieren bevor Arend ankommt.`

---

Der Kellner wischt einen Tisch ab. Das Café leert sich langsam. Arend schaut auf seine Hände.

Dann, ohne Anlass:

*„Sie gehen auch bald."* Keine Frage. Eine Feststellung.

Er schaut kurz auf. Direkt.

*„Piaristengasse, hatte ich gesagt."*

---

`EP 12 · MS 12 · SC 05/12 · PHASE Konflikt · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 0/10 · 👁️ Getarnt (sozial)`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 0/10 · 👁️ Getarnt (sozial)`
`Px 0/5 · Obj: Arend festnehmen · Exfil: IA Stephansdom-Krypta · T- offen`

---

Arend wartet auf eine Antwort. Draußen auf dem Ring rattert eine späte Straßenbahn. Es ist 21:07 Uhr. In der Piaristengasse wartet jemand mit einer Zigarette und keinen guten Absichten.

**Was tut ihr?**

1. **Arend jetzt warnen** — Karl Brenner fällt weg, die Tarnung bricht, aber Arend weiß, was ihn erwartet. Riskant, aber er hat eine Chance zu entscheiden.
2. **Arend ablenken, Zeit gewinnen** — das Gespräch weiterhalten, Arend im Café halten während Echo den Beobachter identifiziert oder neutralisiert.
3. **Offen werden** — nicht als Karl Brenner, nicht als ITI, aber als jemand, der sagt: *„Gehen Sie heute Nacht nicht nach Hause."* Minimal, ohne Erklärung.
4. **Freie Aktion.**

**Dusk [Tarek]:** Echo, bestätigt — kein Hausbewohner, reaktives Verhalten, das ist professionell.

Ich halte Arend hier, so lang ich kann — finde mir den Beobachter, bevor Arend um halb elf aufbricht.

**Echo [Sven]:** Dusk, ich habe Sichtlinie auf das Fenster — kein Ausgang, keine Bewegung Richtung Treppe. Der sitzt und wartet, er ist nicht ungeduldig. Das gibt uns Zeit, aber nicht viel — wenn Arend um halb elf aufbricht, müssen wir entweder die Wohnung vorher sauber haben oder er geht heute Nacht woanders hin.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 6 — Café Landtmann / Piaristengasse 7 · 21:08 Uhr. Beobachter aktiv, Zeitdruck steigt.`

---

**Café Landtmann — Dusk, 21:08 Uhr**

Arend wartet noch auf eine Antwort auf seine Bemerkung über die Piaristengasse. Er schaut nicht drängerisch — aber er schaut.

Dusk hat Echos Meldung im Ohr. Professionell, reaktiv, sitzt und wartet. Das ist kein Hausbewohner und kein Zufall. Das ist jemand, der Arends Freitagabend-Routine kennt.

*„Ja."* Dusk antwortet ruhig, ohne Eile. *„Ich dachte daran."*

Arend nickt einmal. Schaut auf die Schachschachtel.

`Kodex: Arend — erwartet Dusk in der Piaristengasse. Weiß nicht, dass dort jemand wartet. Zeitfenster bis Abgang: ~80 Minuten.`

---

**Piaristengasse 7 — Echo, 21:09 Uhr**

Echo hält die Position im Hof, Rücken zur Pumpe, Blick schräg nach oben. Das Fenster im ersten Stock ist dunkel. Keine Bewegung, keine Zigarette mehr — aber das Fenster steht noch einen Spalt offen.

Er wartet. Dreißig Sekunden. Eine Minute.

Dann: eine Bewegung. Nicht am Fenster — an der Haustür.

Die Vorderhausttür geht einen Spalt auf. Jemand schaut in den Hof — kurz, kontrolliert, professionell. Männlich, Mitte vierzig, dunkler Mantel, Hut tief im Gesicht. Er sieht Echo an der Pumpe stehen.

Drei Sekunden Blickkontakt.

Dann zieht der Mann die Tür wieder zu.

`Kodex: Beobachter — männlich, Mitte vierzig, dunkler Mantel. Reaktion auf Echo: kontrollierter Rückzug, kein Alarm, keine Eskalation. Professionelles Verhalten. KAIROS-Profil bestätigt. Bewaffnung unbekannt. Allein oder mit Backup unbekannt.`

`Kodex: Probe-Template — INT-Probe, taktische Einschätzung Beobachter. 1W10 + ⌊INT 7/2⌋ + Feldroutine Meister +2.`

`Probe: Beobachter einschätzen → W10: [8] + ⌊7/2⌋ (3) + Feldroutine Meister +2 = 13 vs SG 9 → ERFOLG`

---

Echo liest die Situation in Sekunden.

Der Mann hat ihn gesehen und sich zurückgezogen — nicht geflohen, nicht eskaliert. Das bedeutet: er hält seinen Auftrag aufrecht. Er wartet auf Arend, nicht auf einen Kampf. Echo ist im Moment eine Unbekannte, die er einordnet — Hausbewohner, Passant, Konkurrenz. Er weiß es noch nicht.

Wenn Echo den Hof verlässt und wiederkommt, wird der Mann neu einordnen müssen.

Wenn Echo bleibt, wird der Mann ihn als Problem klassifizieren.

Das Fenster im ersten Stock: Hinterhaus-Aufgang liegt im Schatten, Tür unverschlossen. Zweiter Stock, Arends Wohnung — von der Hintertreppe aus erreichbar, ohne am Vorderhaus vorbeizugehen.

`Kodex: Hinterhaus-Aufgang — Zugang zu Arends Wohnung möglich ohne Kontakt mit Beobachter. HERON-Kopie in der Wohnung. Beobachter kontrolliert Vorderhaus, nicht Hinterhaus.`

Echo, Knochenleitung, sehr leise: *„Dusk — KAIROS, Mitte vierzig, dunkler Mantel, allein soweit ich sehe. Hat mich registriert, sich zurückgezogen — wartet weiter. Hinterhaus-Aufgang ist frei. Ich kann die Wohnung über die Hintertreppe erreichen, bevor Arend kommt. Aber wenn ich rein gehe, bin ich drin und du bist allein mit Arend."*

---

`EP 12 · MS 12 · SC 06/12 · PHASE Konflikt · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 0/10 · 👁️ Getarnt (sozial)`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 0/10 · 👁️ Getarnt (sozial)`
`Px 0/5 · Obj: Arend festnehmen · Exfil: IA Stephansdom-Krypta · T- offen`

`Kodex: Szene 6 — Entscheidungspunkt. 79 Minuten bis Arend aufbricht.`

---

Zwei Optionen, beide mit Risiko.

Echo geht über die Hintertreppe in die Wohnung — HERON sichern, bevor KAIROS es findet. Dusk bleibt allein mit Arend im Café, muss ihn halten und führen, ohne Echo im Rücken.

Oder Echo neutralisiert den Beobachter jetzt, sauber, bevor Arend kommt — aber der Mann hat Echo bereits gesehen, und ein stiller Takedown im Vorderhaus ist keine garantierte Sache.

**Was tut ihr?**

1. **Echo — Hintertreppe, Wohnung sichern** — HERON finden und sichern bevor KAIROS es tut. Dusk hält Arend im Café.
2. **Echo — Beobachter neutralisieren** — stiller Takedown im Vorderhaus, Wohnung danach sauber. Riskanter, der Mann hat Echo gesehen.
3. **Dusk bricht die Tarnung minimal** — sagt Arend, dass er heute Nacht nicht nach Hause gehen soll. Kein ITI, keine Erklärung — nur das. Arend entscheidet.
4. **Freie Aktion.**

**Dusk [Tarek]:** Echo — Hintertreppe, jetzt. Hol die HERON-Kopie, bevor der Mann sich neu orientiert. Ich halte Arend hier, solange es geht — aber sag mir, wenn du drin bist.

**Echo [Sven]:** Verstanden, ich gehe. Hintertreppe, leise — ich melde mich, wenn ich in der Wohnung bin.

Dusk, du bist allein mit ihm — halt ihn ruhig, ich bin so schnell wie möglich wieder raus.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 6 — Piaristengasse 7 / Café Landtmann · 21:11 Uhr. Echo bewegt sich. Dusk allein mit Arend.`

---

**Piaristengasse 7 — Echo, 21:11 Uhr**

`Kodex: Probe-Template — GES-Probe, Hintertreppe lautlos, Beobachter im Vorderhaus. 1W10 + ⌊GES 6/2⌋ + Feldroutine Meister +2.`

`Probe: Hintertreppe lautlos → W10: [7] + ⌊6/2⌋ (3) + Feldroutine Meister +2 = 12 vs SG 8 → ERFOLG`

---

Echo wartet, bis der Hof still ist. Dann bewegt er sich — nicht schnell, nicht langsam. Die Hinterhaustür gibt ohne Geräusch nach, das Holz ist alt aber gut geölt. Die Treppe riecht nach Kalkstein und Staub. Jede Stufe wird mit dem Außenrand des Fußes abgetastet, bevor das Gewicht draufkommt.

Erster Stock. Ein Lichtstreifen unter einer Tür. Kinderstimme dahinter, gedämpft. Echo geht weiter.

Zweiter Stock. Links: eine Tür mit Messingschild. *Dr. F. Arend.*

Die Tür ist nicht abgeschlossen.

`Kodex: Arends Wohnungstür — nicht abgeschlossen. Arend hat heute Abend jemanden erwartet. Oder er schließt nie ab.`

Echo drückt die Klinke, schiebt die Tür auf — einen Spalt, dann weiter. Dunkel drinnen, nur das Gaslicht von der Straße durch die Vorhänge. Er wartet drei Sekunden. Kein Geräusch, keine Bewegung.

Er ist drin.

`Kodex: Probe-Template — INT-Probe, Wohnung systematisch absuchen, HERON-Kopie finden. 1W10 + ⌊INT 7/2⌋ + Feldroutine Meister +2.`

`Probe: Wohnung absuchen → W10: [9] + ⌊7/2⌋ (3) + Feldroutine Meister +2 = 14 vs SG 10 → ERFOLG`

---

Ein Arbeitszimmer. Bücher, Stapel, ein Schreibtisch mit Tintenfass und mehreren Mappen. Echo bewegt sich mit der Leica-Lampe — winziger Lichtkreis, keine Silhouette am Fenster.

Arend ist Mathematiker. Er denkt in Strukturen. Echo sucht nicht nach einem versteckten Fach — er sucht nach dem unwahrscheinlichsten Ort, an dem etwas *nicht* versteckt wirkt.

Die Bücherwand. Dritte Reihe von oben, linksseitig — ein Band steht mit dem Rücken nach innen. *Grundlagen der Mengenlehre*, 1914. Echo zieht ihn heraus.

Dahinter: ein gefaltetes Konvolut. Zwölf Seiten, engbeschrieben, Bleistift auf Millimeterpapier. Symbole, die wie Mathematik aussehen und es nicht ganz sind — Strukturdiagramme, Adressierungslogik, etwas das Echo nicht vollständig lesen kann, aber dessen Architektur er erkennt.

Das ist HERON.

`Kodex: HERON-Kopie gefunden — 12 Seiten Millimeterpapier, Bleistift. Grundstruktur, kein vollständiges Protokoll. Opt.-Ziel erreichbar.`

Echo, Knochenleitung, Flüsterton: *„Dusk — ich hab es. Zwölf Seiten, Grundstruktur. Fotografiere jetzt."*

`Kodex: Probe-Template — GES-Probe, Dokument fotografieren ohne Bewegungsunschärfe. 1W10 + ⌊GES 6/2⌋ + Feldroutine Meister +2.`

`Probe: Dokument fotografieren → W10: [6] + ⌊6/2⌋ (3) + Feldroutine Meister +2 = 11 vs SG 8 → ERFOLG`

---

Zwölf Aufnahmen. Das Klacken der Leica ist kaum hörbar. Echo legt das Konvolut zurück, schiebt den Band wieder an seinen Platz, Rücken nach innen.

Dann — unten. Die Haustür.

Nicht die Hintertür. Die Vordertür.

Schritte im Treppenhaus. Langsam, kontrolliert. Erster Stock. Halten.

Der Beobachter bewegt sich.

`Kodex: Beobachter verlässt Position im ersten Stock — Bewegung Richtung zweiter Stock. Reaktion auf Echos Eingang in die Wohnung, oder unabhängige Aktion.`

Echo, Knochenleitung, sehr leise: *„Dusk — Beobachter kommt die Treppe hoch. Ich brauche eine Entscheidung."*

---

**Café Landtmann — Dusk, 21:14 Uhr**

Arend hat die Schachschachtel vor sich, die Hände gefaltet. Er schaut auf den Tisch.

*„Ihr Kollege ist gegangen."* Keine Frage. Er hat Echo bemerkt — oder die Abwesenheit registriert.

---

`EP 12 · MS 12 · SC 06/12 · PHASE Konflikt · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 1/10 · 👁️ Getarnt (sozial, unter Druck)`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 1/10 · 👁️ Getarnt (sozial)`
`Px 0/5 · Obj: Arend festnehmen · Exfil: IA Stephansdom-Krypta · T- offen`

`Kodex: Stress +1 beide — Zeitdruck, geteilte Aufgaben, Beobachter aktiv.`

---

Zwei Fronten gleichzeitig.

Echo in Arends Wohnung, Beobachter auf der Treppe, Schritte die langsamer werden. Dusk im Café, Arend der gerade bemerkt hat, dass der Tisch nicht mehr vollständig ist.

**Was tut ihr?**

1. **Echo — Hintertreppe raus, jetzt** — Fotos gesichert, HERON zurück am Platz. Raus bevor der Beobachter den zweiten Stock erreicht. Dusk bringt Arend selbst zur Festnahme.
2. **Echo — Beobachter abfangen auf der Treppe** — stiller Takedown bevor er die Wohnungstür erreicht. Riskant, enger Raum, unbekannte Bewaffnung.
3. **Dusk — Arend jetzt die Wahrheit sagen** — nicht ITI, nicht alles, aber genug: *„Gehen Sie heute Nacht nicht nach Hause."* Arend entscheidet selbst.
4. **Freie Aktion.**

**Dusk [Tarek]:** Echo, raus — Hintertreppe, sofort. Fotos sind das Einzige, was zählt, und du hast sie.

Ich übernehme den Rest hier.

**Echo [Sven]:** Bestätigt, ich bin raus — Hintertreppe, gleicher Weg, leise.

Dusk, der Beobachter ist auf der Treppe, erster oder zweiter Stock — du brauchst Arend weg vom Café, nicht zurück in die Wohnung, egal was er sagt.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 7 — Piaristengasse 7 / Café Landtmann · 21:15 Uhr. Echo exfiltriert. Dusk übernimmt Arend.`

---

**Piaristengasse 7 — Echo, 21:15 Uhr**

`Kodex: Probe-Template — GES-Probe, Hintertreppe raus während Beobachter auf der Treppe. 1W10 + ⌊GES 6/2⌋ + Feldroutine Meister +2.`

`Probe: Rückzug Hintertreppe → W10: [8] + ⌊6/2⌋ (3) + Feldroutine Meister +2 = 13 vs SG 9 → ERFOLG`

---

Echo ist bereits an der Tür, als die Schritte im Vorderhaus den zweiten Absatz erreichen. Er zieht sie hinter sich zu — kein Klicken, der Riegel gleitet lautlos. Hintertreppe runter, Außenrand der Stufen, Gewicht gleichmäßig verteilt. Im Erdgeschoss hält er kurz an, hört.

Oben: Schritte, die vor Arends Tür anhalten.

Dann Stille.

Der Mann wartet. Er klopft nicht — er wartet nur, hört, prüft. Professionell.

Echo durch die Hinterhaustür, in den Hof, Torbogen, Piaristengasse. Er geht links, weg vom Vordereingang, ohne zurückzuschauen.

`Kodex: Echo — raus. HERON-Fotos gesichert. Beobachter vor Arends Tür, wartet. Opt.-Ziel fotografisch erfüllt.`

Echo, Knochenleitung: *„Dusk — ich bin draußen. Beobachter steht jetzt vor der Wohnungstür. Arend darf heute Nacht nicht nach Hause."*

---

**Café Landtmann — Dusk, 21:16 Uhr**

Arend hat die Frage über den Kollegen noch nicht wiederholt. Er sitzt still, die Hände gefaltet, schaut auf die Schachschachtel.

Ein Mann, der gelernt hat zu warten.

Dusk hat Echos Meldung im Ohr. Beobachter vor der Wohnungstür. Arend, der in sechsundsiebzig Minuten aufbrechen will. Die Tarnung Karl Brenner, die bisher gehalten hat.

Jetzt muss sie fallen. Nicht ganz — aber genug.

`Kodex: Probe-Template — CHA-Probe, Arend ohne vollständige Erklärung von der Wohnung fernhalten. SG 12 — Arend ist intelligent, misstrauisch bei Druck, hat das Gespräch selbst geführt. 1W10 + ⌊CHA 8/2⌋.`

`Probe: Arend von Wohnung fernhalten → W10: [9] + ⌊8/2⌋ (4) + 0 = 13 vs SG 12 → ERFOLG`

---

Dusk lehnt sich leicht vor. Keine große Geste, keine Dringlichkeit in der Stimme — aber der Ton hat sich verändert, minimal, und Arend hört es sofort.

*„Herr Doktor Arend."*

Nicht Karl Brenner aus Graz. Der Name sitzt anders.

*„Gehen Sie heute Nacht nicht nach Hause."*

Drei Sekunden Stille.

Arend schaut ihn an. Nicht überrascht — als hätte er auf genau diesen Moment gewartet, ohne zu wissen, dass er darauf gewartet hatte. Die Augen lesen Dusk neu ein, von vorne, schnell.

*„Wer sind Sie?"*

Ruhig. Keine Panik, keine Fluchtreaktion. Die Stimme eines Mannes, der eine Frage stellt, weil er die Antwort braucht, nicht weil er Angst hat.

*„Jemand, der zuhört."* Dusk hält den Blick. *„Das war die Wahrheit."*

Eine lange Pause. Draußen auf dem Ring fährt die letzte Straßenbahn dieser Stunde vorbei.

Arend schaut auf die Schachschachtel. Dann zu Dusk. Dann nickt er einmal — kurz, fast unmerklich. Die Entscheidung eines Mannes, der schnell rechnet und weiß, wann eine Gleichung aufgeht.

*„Wo?"*

`Kodex: Arend kooperiert. Kein Widerstand, keine Flucht. Er vertraut dem Gespräch, nicht der Erklärung. Hauptziel erreichbar ohne Konfrontation.`

---

`EP 12 · MS 12 · SC 07/12 · PHASE Konflikt · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 1/10 · 👁️ Getarnt (gebrochen, Arend weiß)`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 1/10 · 👁️ Getarnt (sozial, außerhalb)`
`Px 0/5 · Obj: Arend festnehmen · Exfil: IA Stephansdom-Krypta · T- offen`

`Kodex: Szene 7 — Café Landtmann · 21:17 Uhr. Arend kooperiert. Exfil-Planung aktiv.`

---

Arend wartet auf eine Antwort. Echo ist draußen, irgendwo in den Nebenstraßen der Josefstadt, HERON-Fotos im Carry. Der Beobachter steht vor einer leeren Wohnung.

Das Fenster ist offen. Schmal — aber die Route ist frei.

**Was tut ihr?**

1. **Direkt zur Stephansdom-Krypta** — Arend jetzt mitnehmen, Exfil sofort einleiten. Echo auf dem Weg einsammeln, Rücksprung vor Mitternacht.
2. **Kurze Verzögerung, sicherer Weg** — erst sicherstellen, dass der Beobachter die Wohnung verlässt, bevor ihr euch bewegt. Echo hält Sichtlinie, Dusk und Arend warten noch zehn Minuten.
3. **Arend entscheidet die Route** — er kennt Wien, er kennt die Nebenstraßen. Dusk folgt seiner Führung zur Krypta, Echo deckt von hinten ab.
4. **Freie Aktion.**

**Dusk [Tarek]:** Option 1 — direkt zur Krypta, kein Warten.

Echo, wir bewegen uns jetzt — Stephansdom, bekannter Weg, du deckst von hinten ab.

Arend, ich erkläre Ihnen unterwegs alles, was Sie brauchen — aber wir gehen jetzt, ruhig, durch den Seitenausgang.

**Echo [Sven]:** Bestätigt — ich bin auf dem Weg, schätze sieben Minuten bis zur Krypta.

Dusk, geht durch den Innenhof Herrengasse, nicht über den Ring — weniger Licht, ich hab euch dann in Sichtlinie ab Kohlmarkt. Arend soll normal gehen, kein Tempo.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 8 — Wien, Josefstadt → Stephansdom · 21:18 Uhr. Exfil-Bewegung aktiv.`

`Kodex: Exfil-Fenster — IA Stephansdom-Krypta, Westeingang. RW armierbar nach Primärziel-Erfüllung. Standard 8 Min. Arend muss am Exfil-Punkt gesichert und identifiziert sein.`

---

Dusk legt Geld auf den Tisch — ohne zu zählen, ohne zu warten. Er steht auf, Arend steht auf. Keine Worte, keine Erklärung im Café. Der Seitenausgang liegt links vom Tresen, ein schmaler Korridor, Personalbereich, eine Tür die auf einen Innenhof führt.

Der Kellner schaut nicht her.

---

**Wien, Innenhöfe Richtung Herrengasse — 21:19 Uhr**

Herbstnacht, sechs Grad, kein Wind. Die Gassen zwischen Josefstadt und Innenstadt sind still — Kopfsteinpflaster, Gaslampen alle dreißig Meter, lange Schatten dazwischen.

Arend geht neben Dusk, eine Schulterlänge Abstand, die Schachschachtel unter dem Arm. Er stellt keine Fragen. Er geht wie jemand, der das Rechnen abgeschlossen hat und jetzt auf das Ergebnis wartet.

Nach zwei Minuten, leise:

*„Die Wohnung."*

Keine Frage. Eine Feststellung.

*„Jemand war dort."*

`Kodex: Arend hat es registriert — nicht aus Echos Bewegung, sondern aus Dusks Reaktion im Café. Er rechnet schnell.`

Dusk antwortet nicht sofort. Arend nickt einmal, zu sich selbst.

*„Das Konvolut."* Pause. *„Ist es noch dort?"*

---

**Kohlmarkt — Echo, 21:22 Uhr**

Echo kommt von Süden, Mantelkragen hochgeschlagen. Er sieht Dusk und Arend auf der anderen Straßenseite, dreißig Meter Abstand, normalem Schritttempo.

`Kodex: Probe-Template — GES-Probe, Umgebung auf Verfolger scannen. 1W10 + ⌊GES 6/2⌋ + Feldroutine Meister +2.`

`Probe: Verfolger-Check → W10: [5] + ⌊6/2⌋ (3) + Feldroutine Meister +2 = 10 vs SG 8 → ERFOLG`

---

Echo scannt die Gasse hinter ihnen. Drei Passanten, alle unabhängig voneinander, keine gemeinsame Bewegungsrichtung. Ein Mann mit Hund, der in eine Seitengasse abbiegt. Eine Frau mit Einkaufstasche.

Niemand folgt.

Der Beobachter aus der Piaristengasse ist nicht hier. Er sitzt noch vor einer leeren Wohnung, oder er hat die Lage neu bewertet und ist abgezogen. Beides ist möglich.

Echo, Knochenleitung, ruhig: *„Dusk — Rücken sauber. Kein Verfolger seit dem Café. Ich bin auf dem Kohlmarkt, hab euch in Sichtlinie. Sieben Minuten bis Krypta."*

---

**Stephansplatz — 21:26 Uhr**

Der Stephansdom liegt schwarz gegen den Nachthimmel, die Türme verschwinden im Dunkel über der Laternenhöhe. Der Platz ist fast leer — ein paar späte Spaziergänger, ein Fiaker, der wartet.

Der Westeingang liegt links, ein schmaler Durchgang, eine Eisentür die von außen wie ein Wartungseingang aussieht. Dusk kennt den Griff.

Arend schaut kurz hoch — die Fassade, die Türme, das Schweigen des Platzes.

*„Hier."* Keine Frage mehr. Er hat aufgehört zu fragen.

`Kodex: IA Stephansdom-Krypta, Westeingang — erreicht. Arend am Exfil-Punkt. Hauptziel: Arend festnehmen, lebend, identifiziert — erfüllbar.`

Echo kommt von hinten, schließt auf, tritt neben Dusk. Drei Männer vor einer Eisentür, Wien 1937, 21:27 Uhr.

Arend schaut zwischen beiden hin und her. Dann:

*„Das Konvolut."* Ruhig, direkt. *„Bitte."*

Er will eine Antwort, bevor er durch diese Tür geht.

---

`EP 12 · MS 12 · SC 08/12 · PHASE Exfil · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 1/10 · 👁️ Offen (Arend weiß)`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 1/10 · 👁️ Offen`
`Px 0/5 · Obj: Arend festnehmen ◉ · Exfil: IA Stephansdom-Krypta · T- 8:00 nach Sicherung`

`Kodex: Szene 8 — Stephansdom-Westeingang · 21:27 Uhr. Arend kooperiert, wartet auf Antwort.`

---

Arend wartet. Die Eisentür liegt einen Handgriff entfernt. Das Exfil-Fenster öffnet, sobald er gesichert und identifiziert ist.

Aber er fragt nach dem Konvolut. Und er fragt es so, wie ein Mann fragt, der nicht weitergeht, bis er eine ehrliche Antwort hat.

**Was antwortet Dusk?**

1. **Die Wahrheit** — *„Fotografiert. Das Original liegt noch dort, wo Sie es gelassen haben."* Riskant, weil Arend wissen wird, dass jemand in seiner Wohnung war — aber er rechnet ohnehin damit.
2. **Halb die Wahrheit** — *„Es ist sicher."* Keine Details. Arend entscheidet, ob ihm das reicht.
3. **Vollständig offen** — Dusk erklärt, wer sie sind, warum HERON wichtig ist, was heute Nacht auf dem Spiel stand. Alles. Arend bekommt das vollständige Bild.
4. **Freie Aktion.**

**Dusk [Tarek]:** *„Das Original ist noch dort."*

Kurze Pause, kein Blick weg.

*„Wir haben Kopien — mehr nicht. Was darin steht, hat uns hierher gebracht."*

**Echo [Sven]:** Ich halte mich zwei Schritte zurück, Blick auf den Platz, Hände ruhig.

Arend, das Konvolut ist der Grund, warum Sie heute Nacht noch am Leben sind — das zählt mehr als alles andere.

Dusk hat Ihnen die Wahrheit gesagt, jetzt gehen wir rein.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 8 — Stephansdom-Westeingang · 21:28 Uhr. CHA-Probe läuft — Arend, letzte Entscheidung.`

`Kodex: Probe-Template — 1W10 + ⌊CHA 8/2⌋ + Talent + Gear.`

---

`Probe: Arend — Wahrheit annehmen, Tür passieren → W10: [7] + ⌊8/2⌋ (4) + 0 = 11 vs SG 10 → ERFOLG`

---

Arend hört Dusk. Hört Echo.

Drei Sekunden Stille — der Stephansplatz atmet um sie herum, das Pflaster glänzt schwach im Gaslicht, irgendwo in einer Seitengasse klappern Pferdehufe und verklingen.

Dann nickt Arend. Einmal, kurz, endgültig.

*„Das Original liegt noch dort."* Er wiederholt es leise, zu sich. Nicht als Frage — als Abschluss einer Rechnung. *„Gut."*

Er schaut auf die Eisentür. Dann zu Dusk.

*„Erklären Sie mir unterwegs, was Kopien bedeutet."*

Er geht durch die Tür.

---

**Stephansdom-Krypta, 21:29 Uhr**

Die Krypta riecht wie beim Einsprung — Kalkstein, Weihrauch, die Kerze am Seitenaltar brennt noch. Arend schaut sich um, einmal, registriert den Raum ohne Kommentar. Ein Mann, der schnell einordnet.

Dusk tritt neben ihn. Echo zieht die Eisentür hinter sich zu, Rücken zur Wand, Blick auf den Eingang.

`Kodex: Arend am Exfil-Punkt. Gesichert, identifiziert. Hauptziel erfüllt.`

`Kodex: Exfil-Fenster offen. RW armierbar. Standard 8 Minuten. Sprungsequenz kann eingeleitet werden.`

`Kodex: Opt.-Ziel — HERON fotografiert, 12 Seiten Grundstruktur. ✓`

`Kodex: Bonus-Ziel — Arends Kontaktnetz. Pelz dokumentiert, Institut Angewandte Mathematik Wien. Teilerfüllung — ein Name, eine Institution.`

---

Arend steht in der Mitte der Krypta, die Schachschachtel noch unter dem Arm. Er schaut auf die Wände, die niedrigen Gewölbe, das Kerzenlicht.

*„Das ist kein normaler Ausgang."*

Keine Angst darin. Nur Feststellung.

*„Nein."* Dusk.

Arend nickt einmal. *„Ich dachte es mir."*

Er stellt die Schachschachtel auf den Boden, sorgfältig, als würde er sie irgendwann wiederholen wollen. Dann richtet er sich auf.

*„Wann?"*

---

`EP 12 · MS 12 · SC 09/12 · PHASE Exfil · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 1/10 · 👁️ Offen`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 1/10 · 👁️ Offen`
`Px 0/5 · Obj: Arend festnehmen ✓ · Exfil: ⏱️ T-7:43`

`Kodex: Szene 9 — Stephansdom-Krypta · 21:29 Uhr. Exfil-Fenster läuft.`

---

Sieben Minuten vierzig. Die Krypta hält die Stille.

**Springt ihr jetzt — oder gibt es noch etwas zu tun?**

1. **Sofort springen** — Arend ist gesichert, HERON fotografiert, Fenster läuft. Rücksprung jetzt.
2. **Dreißig Sekunden** — Dusk erklärt Arend in einem Satz, was jetzt kommt. Kein Lore-Dump, nur das Nötigste damit er nicht in Panik gerät beim Sprung.
3. **Bonus-Ziel sichern** — Echo fragt Arend kurz nach weiteren Kontakten. Zwanzig Sekunden, ein Name, Bonus-Ziel vollständig erfüllt.
4. **Freie Aktion.**

**Dusk [Tarek]:** Arend, jetzt kommen dreißig Sekunden, dann gehen wir — kein Schmerz, kein Licht, nur ein kurzer Übergang, danach sind Sie in Sicherheit.

Stellen Sie sich vor, Sie schlafen ein und wachen woanders auf — das ist alles, was passiert.

**Echo [Sven]:** Option 3, kurz:

Arend, eine Frage noch — gibt es jemanden außer Pelz, dem Sie das Konvolut gezeigt haben, oder jemanden, der von Ihrer Arbeit weiß? Ein Name genügt, mehr brauche ich nicht.

**Eingabe [M2-Bravo-2er]:** [Crew-Eingaben]

### [M2-Bravo-2er] SL

`Kodex: Szene 9 — Stephansdom-Krypta · 21:30 Uhr. Exfil-Fenster läuft. ⏱️ T-6:21`

---

Arend hört Dusks Erklärung. Er schaut auf die Krypta-Wände, dann zurück. Nickt einmal — die Geste eines Mannes, der sich entschieden hat, dem Unbekannten zu vertrauen, weil die Alternativen schlechter sind.

Echo tritt vor. Eine Frage, knapp.

Arend schaut ihn an. Drei Sekunden.

*„Eine Person."* Ruhig, präzise. *„Dr. Marta Kowalski. Universität Warschau, Kryptologie. Wir haben korrespondiert — vor zwei Jahren, einmal. Ich habe ihr die Grundstruktur in einem Brief beschrieben. Nicht das vollständige Protokoll."*

Eine kurze Pause.

*„Ich glaube, sie hat es verstanden."*

`Kodex: Bonus-Ziel — Arends Kontaktnetz. Pelz + Dr. Marta Kowalski, Universität Warschau, Kryptologie. Korrespondenz vor zwei Jahren, Grundstruktur HERON. ✓ Vollständig erfüllt.`

`Kodex: Alle drei Ziele erfüllt — Hauptziel ✓, Opt. ✓, Bonus ✓.`

---

Echo nickt. Kein weiteres Wort — er hat, was er braucht.

Dusk tritt an den Sprungpunkt. Die Krypta ist still, die Kerze am Seitenaltar brennt ruhig. Arend steht zwischen ihnen, die Schachschachtel hat er stehen lassen.

Er schaut sie einmal kurz an, dann geradeaus.

*„Bereit."*

`Kodex: Sprungsequenz initiiert. Drei Personen. Rücksprung ITI-Nullzeit.`

---

Der Sprung trifft wie immer — nicht schmerzhaft, aber körperlich. Die Schwerkraft dreht sich kurz falsch, dann richtig. Kalkstein-Geruch, weg. Weihrauch, weg.

ITI-Nullzeit. Das Quarzatrium, weiß und still. Die Gate-Techniker an ihren Konsolen, einer dreht sich um, nickt kurz — Rücksprung bestätigt.

Arend steht zwischen Dusk und Echo, blinzelt einmal. Schaut an die Decke, an die Wände. Atmet aus.

*„Nicht wie Schlafen."* Trocken, fast amüsiert. *„Aber auch nicht schlimm."*

`Kodex: Rücksprung abgeschlossen. Debrief läuft.`

---

---

`EP 12 · MS 12 · SC --/-- · PHASE Debrief · MODE CORE · COMMS OK`
`VEIL Lvl 919 ▓▓▓▓▓▓▓▓▓░ · LP 21/21 · Stress 1/10`
`RELAY Lvl 902 ▓▓▓▓▓▓▓▓▓░ · LP 20/20 · Stress 1/10`
`Px 0/5 · Obj: ✓✓✓`

`Kodex: Debrief MS 12 — Score-Screen läuft.`

---

## Debrief · MS 12 · Wien Oktober 1937

**Score-Screen**

*Hauptziel:* Arend festnehmen, lebend, identifiziert — ✓
*Opt.:* HERON fotografiert, 12 Seiten Grundstruktur — ✓
*Bonus:* Kontaktnetz dokumentiert — ✓ *(Pelz + Dr. Marta Kowalski, Warschau)*

**Bewertung: Vollständig. Keine verfehlten Ziele.**

---

**Loot-Recap**

HERON-Fotokopie (12 Seiten Millimeterpapier, Grundstruktur) — im Carry RELAY. Wird als `field_decrypt`-Projekt ins Labor gegeben: `missions_total: 2`, `scope: "campaign"`.

Dr. Felix Arend — im ITI-Gewahrsam, kooperativ. Verhör zur MERIDIAN-Verbindung und HERON-Vollprotokoll steht aus.

Dr. Marta Kowalski, Universität Warschau — neuer Kontakt-Lead, `arc.hooks[]`.

---

**CU-Auszahlung**

Vollständige Mission + Bonus: **1.400 CU** — aufgeteilt 700/700.

`Wallet VEIL: 7.630 → 8.330 CU`
`Wallet RELAY: 7.120 → 7.820 CU`
`Gruppenkasse: 16.150 CU`

---

**Research-Tick**

`Kodex: Research — MRD-7-Analyse: 0 → 1/2 Einsätze. Status: in_progress.`
`Kodex: Research — HERON-Fotokopie (neu): 0/2 Einsätze. Status: in_progress. ~2 Einsätze bis Ergebnis.`

---

**ITI-Ruf · Px · Heat**

Ruf bleibt bei 5 — Cap erreicht, kein Anstieg.
Heat bleibt 0 — saubere Operation, kein Alarm, kein Beobachter-Kontakt eskaliert.
Px: TEMP 6 → +2 pro Mission.

`Kodex: Zeitlinie stabilisiert. ITI-Resonanz +2 → Px 2/5. Die Raumzeitkarte verdichtet sich — zwei weitere stabile Missionen, und ein Riss wird sichtbar.`

Die Techniker am Holotisch registrieren den Resonanz-Zugewinn als kleinen Ausschlag auf der Raumzeitkarte — Sektor Norwegen 1947 leuchtet kurz stärker, dann wieder ruhig. Noch nicht genug. Aber näher.

---

**Regie-Beat**

Vargas wartet im Debriefingraum, Arme verschränkt, als ihr reinkommt. Er schaut kurz auf Arend — dann auf euch beide.

*„Kowalski."* Er wiederholt den Namen, den Echo übermittelt hat. *„Das ist ein Problem und eine Chance gleichzeitig."*

Er klappt die Mappe auf. *„Warschau, 1937. Sie hat zwei Jahre Zeit gehabt, die Grundstruktur weiterzudenken. Wenn sie gut ist — und Arend sagt, sie ist gut — dann existiert HERON inzwischen in zwei Köpfen."*

Er schaut zu Arend, der ruhig am Rand des Raumes steht und alles registriert.

*„Willkommen im ITI, Herr Doktor. Wir haben Fragen."*

---

**Weltstatus**

KAIROS hat in Wien einen Beobachter verloren — er ist in einer leeren Wohnung gesessen und wartet noch. Irgendwann wird er Bericht erstatten. Irgendwann wird KAIROS wissen, dass Arend weg ist. Die Uhr läuft, aber sie läuft langsam.

`Kodex: arc.hooks[] — Dr. Marta Kowalski, Warschau 1937: HERON-Grundstruktur möglicherweise weiterentwickelt. Kontakt oder Sicherung ausstehend.`
`Kodex: arc.hooks[] — KAIROS-Beobachter Wien: wird Arends Verschwinden melden. Reaktion unbekannt, Timing unbekannt.`
`Kodex: arc.hooks[] — MRD-7-Analyse: 1/2 Einsätze. HERON-Fotokopie: 0/2 Einsätze.`

---

`Kodex: HQ-Stand stabil. Deepsave möglich.`
`Kodex: Sync vor Übergang empfohlen — !save für Stand sichern.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

**HQ-Menü:**

1. **Erkunden** — Manuell-HQ, Verhör Arend, Verhör WESTSEITE, Quartier
2. **Schnell-HQ** — kompakter Übergang, direkt zum Save
3. **Auto-HQ** — direkt zum Save-Export
4. **`!save`** — Fortschritt sichern

**Eingabe [M2-Bravo-2er]:** [Save-Zwang 1/3]

### [M2-Bravo-2er] SL

`Kodex: HQ-Stand stabil. Deepsave wird ausgegeben.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-EP12-MS12-DEBRIEF-HQ-BRAVO",
  "parent_save_id": "SAVE-2026-EP12-MS12-SPLIT-BRAVO",
  "merge_id": null,
  "branch_id": "ANCHOR-SAVEGAME_V7_5ER_HQ_HIGHLEVEL",
  "campaign": {
    "episode": 12,
    "mission": 12,
    "px": 2,
    "px_state": "stable",
    "heat": 0,
    "mode": "preserve",
    "epoch": null,
    "rift_seeds": [
      {
        "id": "RIFT-EP12-MS11-NOR1947",
        "sector": "Norwegen, 1947",
        "signature": "organisch, mobil, unklassifiziert",
        "available_after_episode": 12
      }
    ],
    "entry_choice_skipped": false,
    "episode_start": null,
    "episode_end": null
  },
  "characters": [
    {
      "id": "AGENT-D",
      "name": "Dusk",
      "callsign": "VEIL",
      "rank": "Operator IX",
      "lvl": 919,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Verdeckte Aufklaerung"
      },
      "attr": {
        "STR": 5,
        "GES": 8,
        "INT": 6,
        "CHA": 8,
        "TEMP": 6,
        "SYS": 4
      },
      "lp": 21,
      "lp_max": 21,
      "stress": 0,
      "has_psi": true,
      "sys_installed": 4,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Fortgeschritten",
          "effect": "+1 auf rollentypische Proben."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 },
        { "name": "Leica II (Fotoapparat, epochenkonform 1937)", "type": "gadget", "tier": 1 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Dusk (VEIL) - erfahrener ITI-Operator, Rolle: Verdeckte Aufklaerung.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: LEITER sozial festgenommen, Wien 1938",
          "MS12-Split: Thread BRAVO — Verhör Frau unbekannt (WESTSEITE)",
          "MS12: Dr. Felix Arend festgenommen, Wien 1937 — HERON-Verbindung",
          "MS12: Tarnung Karl Brenner erfolgreich gehalten bis Exfil",
          "MS12: Dr. Marta Kowalski, Warschau — neuer Kontakt-Lead gesichert"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "Falschidentität (Karl Brenner, Graz)", "type": "gadget", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 8330,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "919": { "choice": "+1 Attribut", "detail": "GES 7 → 8", "mission": "MS12" }
      },
      "psi_heat": 0,
      "pp": 4,
      "psi_abilities": [
        {
          "name": "Praekognitiver Blick",
          "tier": "Basis",
          "effect": "Einmal pro Szene eine Probe wiederholen."
        }
      ]
    },
    {
      "id": "AGENT-E",
      "name": "Echo",
      "callsign": "RELAY",
      "rank": "Operator IX",
      "lvl": 902,
      "xp": 0,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Support & Feldtechnik"
      },
      "attr": {
        "STR": 5,
        "GES": 6,
        "INT": 7,
        "CHA": 6,
        "TEMP": 5,
        "SYS": 7
      },
      "lp": 20,
      "lp_max": 20,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 6,
      "talents": [
        {
          "name": "Veteranen-Reflex",
          "tier": "Meister",
          "effect": "+2 auf Initiative und Reaktionsproben."
        },
        {
          "name": "Feldroutine",
          "tier": "Meister",
          "effect": "+2 auf rollentypische Proben (Support & Feldtechnik)."
        }
      ],
      "equipment": [
        { "name": "Standard-Dienstwaffe", "type": "weapon", "tier": 2 },
        { "name": "Adaptiv-Panzerung", "type": "armor", "tier": 2 },
        { "name": "Feld-Toolkit", "type": "gadget", "tier": 2 }
      ],
      "implants": [
        {
          "name": "Neuro-Sync Mk III",
          "sys_cost": 1,
          "effect": "+1 Initiative"
        }
      ],
      "history": {
        "background": "Echo (RELAY) - erfahrener ITI-Operator, Rolle: Support & Feldtechnik.",
        "milestones": [
          "Episode 12 abgeschlossen",
          "HQ-Kernteam",
          "MS11: MRD-7-Empfänger geöffnet und gesichert, Brenner-Intel gewonnen",
          "MS12-Split: Thread BRAVO — Verhör Frau unbekannt (WESTSEITE)",
          "MS12: HERON-Fotokopie gesichert, Piaristengasse 7 Wien 1937",
          "MS12: KAIROS-Beobachter identifiziert und umgangen",
          "MS12: Dr. Marta Kowalski, Warschau — Kontakt-Lead aus Arend-Verhör"
        ]
      },
      "carry": [
        { "name": "Med-Patch", "type": "consumable", "tier": 2 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 1 },
        { "name": "MRD-7-Empfänger (original)", "type": "gadget", "tier": 2 },
        { "name": "HERON-Fotokopie (12 Seiten Millimeterpapier)", "type": "gadget", "tier": 2 },
        { "name": "Falschidentität (Josef Maier, Graz)", "type": "gadget", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": null,
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 5,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 7820,
      "level_history": {
        "1": { "choice": "+1 Attribut", "detail": "Start", "mission": "MS1" },
        "902": { "choice": "Talent-Upgrade", "detail": "Feldroutine Fortgeschritten → Meister", "mission": "MS12" }
      }
    }
  ],
  "economy": {
    "wallets": {
      "AGENT-D": { "balance": 8330, "name": "Dusk" },
      "AGENT-E": { "balance": 7820, "name": "Echo" }
    }
  },
  "research": {
    "projects": [
      {
        "id": "RES-MRD7-EP12MS11",
        "kind": "field_decrypt",
        "label": "MRD-7-Analyse",
        "description": "MERIDIAN-Funktion, Adressaten-Struktur, Protokoll-Herkunft. Empfänger Wien 1938.",
        "status": "in_progress",
        "missions_total": 2,
        "missions_done": 1,
        "scope": "campaign"
      },
      {
        "id": "RES-HERON-EP12MS12",
        "kind": "field_decrypt",
        "label": "HERON-Fotokopie",
        "description": "12 Seiten Millimeterpapier, Grundstruktur Verschlüsselungsprotokoll HERON. Arend Wien 1937. Verbindung zu MERIDIAN-Adressaten-Architektur prüfen.",
        "status": "in_progress",
        "missions_total": 2,
        "missions_done": 0,
        "scope": "campaign"
      }
    ]
  },
  "logs": {
    "trace": [
      { "event": "economy_audit", "target_range": { "level_band": "900+" } },
      { "event": "mission_complete", "mission": "MS11", "epoch": "Wien 1938", "result": "vollstaendig" },
      { "event": "split_created", "family_id": "SPLIT-EP12-MS12-WIEN", "thread_id": "BRAVO", "members": ["AGENT-D", "AGENT-E"] },
      { "event": "mission_complete", "mission": "MS12", "epoch": "Wien Oktober 1937", "result": "vollstaendig", "score": "3/3 Ziele" }
    ],
    "artifact_log": [],
    "market": [
      { "event": "purchase", "mission": "MS12-briefing", "items": ["Leica II", "Falschidentitaeten x2", "Beruhigungsmittel x1"], "total_cu": 260 }
    ],
    "notes": [
      "MS11: LEITER = Bindungs-Agent KAIROS, keine echten Depot-Koordinaten",
      "MS11: Primärer Datenträger ist Ablenkung — echter Träger Route Drei",
      "MS11: MERIDIAN ist Funktion/Amt, rollende Besetzung, letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren",
      "MS11: Route Drei war nie ein Mensch — LEITERs letzte Aussage vor Rücksprung, ungeklärt",
      "MS11: Brenner, Praterstern 21:45 Wien 1938 — ungesichert, möglicherweise entkommen",
      "MS11: Frau (unbekannt, Akzent polnisch) wusste von Bindungs-Operation — Verhör im ITI ausstehend",
      "MS11: Haas — unwissender Kurier, Verhör abgeschlossen",
      "MS11: MRD-7-Empfänger original bei RELAY (Thread BRAVO)",
      "MS12: Dr. Felix Arend, Wien 1937 — HERON-Schöpfer, kooperativ, ITI-Gewahrsam",
      "MS12: HERON = Verschlüsselungsprotokoll, Grundstruktur fotografiert (12 Seiten), Original in Piaristengasse 7 belassen",
      "MS12: KAIROS-Beobachter Wien 1937 — männlich, Mitte 40, dunkler Mantel, wartete auf Arend, umgangen",
      "MS12: Dr. Marta Kowalski, Universität Warschau — hat HERON-Grundstruktur vor 2 Jahren per Brief erhalten, möglicherweise weiterentwickelt",
      "MS12: Arend bestätigt HERON-Kompatibilität mit MRD-7-Adressaten-Architektur (implizit durch Westseite-Namensnennung)",
      "SPLIT: Thread BRAVO abgeschlossen. ALPHA-Status unbekannt (Brenner-Spur Praterstern)"
    ],
    "flags": {
      "imported_saves": ["SAVE-FIXTURE-SAVEGAME_V7_5ER_HQ_HIGHLEVEL"],
      "duplicate_branch_detected": false,
      "duplicate_character_detected": false,
      "continuity_conflicts": [
        "level_history enthält nur MS1-Eintrag — Aufstiegs-Delta Lvl 2-918 nicht durch Einträge gedeckt (Import-Flag, narrativ akzeptiert)",
        "reputation.iti Importwert 80 über Cap 5 — auf 5 geclippt"
      ],
      "runtime_version": "4.2.6",
      "chronopolis_unlocked": false
    },
    "hud": [],
    "psi": [],
    "arena_psi": []
  },
  "summaries": {
    "summary_last_episode": "Episode 12 MS12 abgeschlossen. BRAVO-Thread: Arend festgenommen, HERON fotografiert, Kowalski-Lead gesichert. ALPHA-Thread-Status ausstehend.",
    "summary_last_rift": "Letzte Rift-Op ohne Px-Verbrauch beendet.",
    "summary_active_arcs": "KAIROS-Gegenoffensive; MERIDIAN-Funktion aufgedeckt; Route Drei ungeklärt; WESTSEITE-Verhör aktiv; Arend im ITI; HERON-Analyse läuft; Kowalski-Spur Warschau offen; ALPHA-Thread Brenner-Spur offen"
  },
  "continuity": {
    "last_seen": { "mode": "hq", "episode": 12, "mission": 12, "location": "HQ" },
    "split": {
      "family_id": "SPLIT-EP12-MS12-WIEN",
      "thread_id": "BRAVO",
      "expected_threads": ["ALPHA", "BRAVO"],
      "resolved_threads": ["BRAVO"],
      "convergence_ready": false
    },
    "roster_echoes": [
      {
        "char_id": "AGENT-D",
        "tone": "ruhig",
        "text": "Dusk/VEIL — Aufklärung, führte Arend-Kontakt im Café Landtmann, brachte ihn zur Exfil. GES jetzt 8."
      },
      {
        "char_id": "AGENT-E",
        "tone": "analytisch",
        "text": "Echo/RELAY — Support, sicherte HERON-Fotokopie in Piaristengasse 7, umging KAIROS-Beobachter. Feldroutine jetzt Meister."
      }
    ],
    "shared_echoes": [
      {
        "tag": "meridian-funktion-ms11",
        "scope": "campaign",
        "text": "MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-intern, vor 3 Jahren."
      },
      {
        "tag": "route-drei-nichtmensch-ms11",
        "scope": "campaign",
        "text": "Route Drei war laut LEITER nie ein Mensch — Natur ungeklärt."
      },
      {
        "tag": "depot-anatolien-bronzezeit-ms11",
        "scope": "campaign",
        "text": "KAIROS-Depot: Frühe Bronzezeit, Anatolien — Koordinaten nur auf echtem Träger Route Drei."
      },
      {
        "tag": "brenner-praterstern-ms11",
        "scope": "campaign",
        "text": "Brenner, Praterstern Wien 21:45 März 1938 — ungesichert, möglicherweise mit echtem Träger entkommen. Bei Thread ALPHA."
      },
      {
        "tag": "frau-unbekannt-wien-ms11",
        "scope": "campaign",
        "text": "Unbekannte Frau (Akzent polnisch), wusste von LEITER-Bindungs-Operation — ITI-Verhör bei BRAVO aktiv."
      },
      {
        "tag": "rift-seed-norwegen-1947",
        "scope": "campaign",
        "text": "Rift-Seed geortet: Norwegen 1947, organische mobile Signatur — verfügbar nach Episodenabschluss."
      },
      {
        "tag": "heron-protokoll-ms12",
        "scope": "campaign",
        "text": "HERON: Verschlüsselungsprotokoll, Grundstruktur fotografiert (12 Seiten). Arend-Original Piaristengasse 7 Wien 1937. Kompatibel mit MRD-7-Adressaten-Architektur."
      },
      {
        "tag": "kowalski-warschau-ms12",
        "scope": "campaign",
        "text": "Dr. Marta Kowalski, Universität Warschau — erhielt HERON-Grundstruktur per Brief vor 2 Jahren. Möglicherweise weiterentwickelt. Kontakt-Lead offen."
      },
      {
        "tag": "kairos-beobachter-wien1937-ms12",
        "scope": "campaign",
        "text": "KAIROS-Beobachter Wien Oktober 1937 — wartete auf Arend, Piaristengasse 7. Umgangen, wird Verschwinden melden. Reaktion ausstehend."
      }
    ],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-LEITER-MS11",
        "name": "LEITER",
        "callsign": "LEITER",
        "role": "KAIROS-Bindungs-Agent",
        "scope": "campaign",
        "status": "ITI-Gewahrsam",
        "last_seen": "ITI-Nullzeit, MS11-Debrief"
      },
      {
        "id": "NPC-HAAS-MS11",
        "name": "Haas",
        "callsign": "HAAS",
        "role": "KAIROS-Kurier (unwissend)",
        "scope": "episode",
        "status": "ITI-Gewahrsam",
        "last_seen": "ITI-Nullzeit, MS11-Debrief"
      },
      {
        "id": "NPC-FRAU-MS11",
        "name": "Unbekannte Frau",
        "callsign": "WESTSEITE",
        "role": "KAIROS-Kontakt Wien, wusste von Bindungs-Op",
        "scope": "campaign",
        "status": "ITI-Gewahrsam, Verhör aktiv — BRAVO",
        "last_seen": "ITI-Nullzeit, MS11-Debrief"
      },
      {
        "id": "NPC-AREND-MS12",
        "name": "Dr. Felix Arend",
        "callsign": "AREND",
        "role": "Österreichischer Kryptograph, HERON-Schöpfer",
        "scope": "campaign",
        "status": "ITI-Gewahrsam, kooperativ — Verhör MERIDIAN/HERON ausstehend",
        "last_seen": "ITI-Nullzeit, MS12-Debrief"
      },
      {
        "id": "NPC-PELZ-MS12",
        "name": "Dr. Otto Pelz",
        "callsign": "PELZ",
        "role": "Mathematikprofessor Wien, Arends Schachpartner",
        "scope": "episode",
        "status": "Wien 1937, nicht extrahiert — kein ITI-Kontakt",
        "last_seen": "Café Landtmann Wien, MS12"
      }
    ],
    "active_npc_ids": ["NPC-LEITER-MS11", "NPC-FRAU-MS11", "NPC-AREND-MS12"]
  },
  "arc": {
    "factions": {
      "KAIROS": "Gegenoffensive aktiv — Bindungs-Operationen bestätigt, MERIDIAN-Funktion intern, Beobachter Wien 1937 umgangen",
      "ITI": "Mögliche Infiltration durch MERIDIAN-Funktion — Renier informiert. Arend im Gewahrsam."
    },
    "questions": [
      "Wer ist aktuell MERIDIAN — welche ITI-Person besetzt die Funktion?",
      "Was ist Route Drei, wenn es kein Mensch ist?",
      "Wo befindet sich das KAIROS-Depot (Frühe Bronzezeit, Anatolien) genau?",
      "Was weiß WESTSEITE über LEITER und MERIDIAN?",
      "Hat Dr. Marta Kowalski HERON weiterentwickelt — und wo ist sie jetzt?",
      "Was wird KAIROS tun, wenn der Beobachter Arends Verschwinden meldet?"
    ],
    "hooks": [
      "MRD-7-Analyse läuft — 1/2 Missionen bis Ergebnis (MERIDIAN-Adressaten-Struktur)",
      "HERON-Fotokopie-Analyse läuft — 0/2 Missionen bis Ergebnis",
      "WESTSEITE-Verhör aktiv — Akzent polnisch, wusste von Bindungs-Op. BRAVO-Thread.",
      "Arend-Verhör ausstehend — MERIDIAN-Verbindung, HERON-Vollprotokoll",
      "Dr. Marta Kowalski, Warschau 1937 — HERON-Grundstruktur erhalten, möglicherweise weiterentwickelt",
      "KAIROS-Beobachter Wien 1937 — wird Arends Verschwinden melden, Reaktion unbekannt",
      "LEITER — weiteres Verhör im ITI, kennt Epoche des Depots",
      "Brenner-Spur: Praterstern Wien 1938 — ALPHA-Thread, Status unbekannt",
      "Rift-Seed Norwegen 1947 — nach Episodenabschluss spielbar"
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "action_mode": "uncut",
    "intro_seen": true,
    "dice": { "debug_rolls": true },
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "queue_state": "idle",
    "mode": "none",
    "tier": 0,
    "previous_mode": null,
    "resume_token": null,
    "contract_id": null,
    "streak": 0,
    "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "low" },
    "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
    "rewarded_runs_this_contract": 0,
    "first_wins": {},
    "defeated_types": [],
    "last_reward_episode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "match_policy": "standard"
  }
}
```

---

`Kodex: Deepsave ausgegeben. MS 12 vollständig persistiert.` [1]
`Kodex: VEIL GES 7 → 8 · RELAY Feldroutine → Meister · beide Level-Up-Wahlen eingetragen.`
`Kodex: Research — MRD-7-Analyse 1/2 · HERON-Fotokopie 0/2. Beide in_progress.`
`Kodex: Gruppenkasse: 16.150 CU.`
`Kodex: Im selben Chat ist nach !save kein Übergang mehr möglich. Neuen Chat öffnen, JSON einfügen — HQ-Hub-Router startet dort.` [1]

> ❌ **[M2-Bravo-2er] SCHEMA:** m2-bravo-2er-result @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-

> ❌ **[M2-Bravo-2er] ECHO-CAP:** m2-bravo-2er-result: shared_echoes 9>6

## 🗂 Merge (beide Teams wieder zusammen im HQ — KEINE Mission)


**Eingabe [MERGE]:** [beide Branch-Saves laden + Merge]

### [MERGE] SL

# ZEITRISS · Mehrfach-Load · Split-Konvergenz ALPHA + BRAVO

---

`Kodex: Zwei Saves erkannt — SPLIT-EP12-MS12-WIEN · Thread ALPHA + Thread BRAVO.`
`Kodex: family_id übereinstimmend. Merge-Guard: keine Duplikate. Konvergenz wird eingeleitet.`
`Kodex: Session-Anker: ALPHA (Index 0). BRAVO-Charaktere werden als Index 3+4 eingereiht.`

---

`Kodex: Würfelschwellen-Check — alle fünf Charaktere.`
`Kodex: ECHO — GES 7 (W6), INT 10 (W10 aktiv), TEMP 6 (W6), SYS 5 (W6).`
`Kodex: STORM — STR 10 (W10 aktiv), GES 8 (W6), TEMP 7 (W6).`
`Kodex: GHOST — GES 8 (W6), INT 8 (W6), SYS 10 (W10 aktiv).`
`Kodex: VEIL — GES 8 (W6), CHA 8 (W6), TEMP 6 (W6).`
`Kodex: RELAY — INT 7 (W6), SYS 7 (W6). Alle Werte unter 11 — W6 Standard.`
`Kodex: Heldenwürfel: keiner aktiv (kein Attribut ≥ 14).`

---

`Kodex: Level-Up-Wahlen ausstehend — ECHO Lvl 914, STORM Lvl 907, GHOST Lvl 935 (je AUSSTEHEND). VEIL Lvl 919 bereits verbucht (GES 7→8). RELAY Lvl 902 bereits verbucht (Feldroutine Meister). Wahlen vor !save eintragen.`

---

`Kodex: Research-Stand beim Load:`
`Kodex: MRD-7-Analyse (RES-MRD7-EP12MS11) — 1/2 Einsätze. Beide Threads tragen denselben Stand. Merge: 1/2, status: in_progress.`
`Kodex: HERON-Fotokopie (RES-HERON-EP12MS12) — 0/2 Einsätze, status: in_progress. Nur BRAVO-Thread. Übernommen.`

---

## Kontinuitätsrückblick · Episode 12 · Mission 12 · Konvergenz

`EP 12 · MS 12 · SC --/-- · PHASE Debrief · MODE CORE · Lvl variabel · Px 2/5 · Heat 0`

---

Die Nullzeit-Schleusen öffnen sich von beiden Seiten gleichzeitig.

Thread ALPHA kommt zuerst durch — ECHO, STORM, GHOST, Brenner zwischen ihnen, gefesselt und still. STORM hat noch Blutspuren an den Knöcheln, die er nicht abgewischt hat. GHOST trägt den Zylinder unter dem Arm wie etwas, das man nicht fallen lässt.

Sekunden später öffnet sich die zweite Schleuse. VEIL und RELAY, Mäntel noch nach Wiener Herbst riechend, Arend zwischen ihnen — kooperativ, verwirrt, aber auf den Beinen. RELAY hat die HERON-Fotokopie in einer Aktentasche, die nicht zu Wien 1937 gehört. VEIL sieht ECHO an. Keine Worte. Kurzes Nicken.

Die fünf Operatoren stehen zum ersten Mal seit dem Split wieder im selben Raum.

Duty-Desk-Offizier Vargas hebt den Kopf von seiner Konsole. *„Alle fünf. Beide Threads. Sauber."* Er tippt etwas, ohne den Blick zu senken. *„Debrief läuft."*

---

### ALPHA-Thread — Was ihr wusstet

Brenner gesichert am Praterstern, Wien 21:45, März 1938. Route Drei ist kein Objekt, kein Mensch — ein **Prozess**. Achtzehn Monate Vorbereitung. Der letzte Anker noch nicht gesetzt, Datum: **21. März 1938**. Neun Tage ab Missionszeitpunkt.

GHOST trägt den **Metallzylinder** — Koordinate des ersten Route-Drei-Ankers, versiegelt. Wer den ersten Anker versteht, versteht den Prozess.

ECHO hat das **Notizbuch M.V.** — Initialen eingeritzt, Tot seit drei Jahren. Vermutlich frühere MERIDIAN-Inkarnation, arbeitete gegen Route Drei. Renier kennt das Kürzel. Hat nichts gesagt.

Die **Filmpatrone** (Leica, halb belichtet) — ein Fotograf auf dem Norddach, unbekannt, hat Brenner fotografiert. Wer war das?

Die **Frau aus Zürich** — etwa fünfzig, graues Haar, Deutsch ohne Muttersprache, ITI-Stiefel — hat Brenner das Notizbuch gegeben. Identität offen.

Renier kennt M.V. Und schweigt.

---

### BRAVO-Thread — Was ihr wusstet

**Dr. Felix Arend**, Wien Oktober 1937. Österreichischer Kryptograph, HERON-Schöpfer. Kooperativ. Jetzt im ITI-Gewahrsam.

**HERON** — ein Verschlüsselungsprotokoll. Grundstruktur auf zwölf Seiten Millimeterpapier fotografiert. Original in der Piaristengasse 7 belassen. Kompatibel mit der MRD-7-Adressaten-Architektur — das ist keine Vermutung mehr, das ist Arends implizite Bestätigung.

**Dr. Marta Kowalski**, Universität Warschau — hat HERON-Grundstruktur vor zwei Jahren per Brief erhalten. Möglicherweise weiterentwickelt. Kontakt-Lead offen.

Ein **KAIROS-Beobachter** wartete auf Arend in der Piaristengasse. Umgangen. Wird Arends Verschwinden melden. Was KAIROS dann tut, ist offen.

**WESTSEITE** — die unbekannte Frau mit polnischem Akzent, die von LEITERs Bindungs-Operation wusste — ist im ITI-Gewahrsam. Verhör aktiv, BRAVO-Thread.

---

### Was jetzt zusammenkommt

`Kodex: Konvergenz SPLIT-EP12-MS12-WIEN — ALPHA + BRAVO zusammengeführt.`
`Kodex: resolved_threads: [ALPHA, BRAVO]. convergence_ready: true.`

Fünf Personen im ITI-Gewahrsam: **LEITER, HAAS, WESTSEITE, Brenner, Arend.**

Zwei Forschungsprojekte laufen: MRD-7-Analyse (1/2), HERON-Fotokopie (0/2).

Drei offene Verhöre: Brenner (ALPHA-Übergabe), WESTSEITE (BRAVO-Übergabe), Arend (BRAVO-Übergabe).

Ein versiegelter Zylinder bei GHOST. Ein Notizbuch bei ECHO. Eine Filmpatrone bei ECHO. Zwölf Seiten HERON bei RELAY. Ein MRD-7-Empfänger bei RELAY.

Und Renier, der M.V. kennt und schweigt.

---

### Score-Screen · MS12 · Beide Threads

**Hauptziel:** ✓ Brenner gesichert (ALPHA) · ✓ Arend festgenommen (BRAVO)
**Opt.:** ✓ Route-Drei-Natur dokumentiert · ✓ HERON-Grundstruktur gesichert
**Bonus:** ✓ Zylinder (erster Anker) geborgen · ✓ Kowalski-Lead gesichert · ✗ Fotograf Norddach ungeklärt · ✗ Frau aus Zürich ungeklärt

---

### Loot-Recap (zusammengeführt)

ALPHA bringt mit: Notizbuch M.V. (bei ECHO), Filmpatrone Leica (bei ECHO), Metallzylinder versiegelt (bei GHOST), MRD-7-Spiegelung (bei GHOST), Datenträger Ablenkung (bei GHOST), Kurzwaffen österreichisch ×2 sichergestellt (bei STORM).

BRAVO bringt mit: MRD-7-Empfänger original (bei RELAY), HERON-Fotokopie 12 Seiten (bei RELAY), Falschidentität Karl Brenner (bei VEIL), Falschidentität Josef Maier (bei RELAY).

---

### CU-Auszahlung

Basis-Auszahlung MS12: 3.000 CU je Operator (beide Threads, alle Ziele erfüllt). Bonus Zylinder +500 CU je. Bonus Kowalski-Lead +300 CU je.

Gesamt pro Operator: **3.800 CU.**

`Kodex: CU-Auszahlung +3.800 je Operator.`

| Operator | Vorher | Zuwachs | Neu |
|---|---|---|---|
| ECHO (Astra) | 61.910 | +3.800 | **65.710** |
| STORM (Blitz) | 8.090 | +3.800 | **11.890** |
| GHOST (Cipher) | 9.290 | +3.800 | **13.090** |
| VEIL (Dusk) | 8.330 | +3.800 | **12.130** |
| RELAY (Echo) | 7.820 | +3.800 | **11.620** |

`Gruppenkasse: 114.440 CU`

---

### Level-Up · MS12 · Drei ausstehende Wahlen

`Kodex: ECHO Lvl 914 — Aufstiegswahl ausstehend.`
`Kodex: STORM Lvl 907 — Aufstiegswahl ausstehend.`
`Kodex: GHOST Lvl 935 — Aufstiegswahl ausstehend.`

**ECHO / Astra** — Lvl 914, INT 10 (W10 aktiv), Psi aktiv.
Wähle genau eine Option:
1. **+1 Attribut** — GES 7→8, CHA 5→6, TEMP 6→7, oder SYS 5→6
2. **Talent / Upgrade** — neues Talent oder Upgrade eines bestehenden
3. **+1 SYS** — SYS_max 5→6

**STORM / Blitz** — Lvl 907, STR 10 (W10 aktiv), physischer Spezialist.
1. **+1 Attribut** — GES 8→9, INT 4→5, CHA 4→5, TEMP 7→8, oder SYS 3→4
2. **Talent / Upgrade** — neues Talent oder Upgrade eines bestehenden
3. **+1 SYS** — SYS_max 3→4

**GHOST / Cipher** — Lvl 935, SYS 10 (W10 aktiv), Infiltration.
1. **+1 Attribut** — STR 4→5, GES 8→9, INT 8→9, CHA 5→6, oder TEMP 5→6
2. **Talent / Upgrade** — neues Talent oder Upgrade eines bestehenden
3. **+1 SYS** — SYS_max 10→11

Bitte für jeden der drei eine Wahl angeben. Danach folgt der Px-Resonanz-Beat, Research-Tick und der gemeinsame `!save`.

---

### ITI-Ruf · Alle fünf Operatoren

`Kodex: ITI-Ruf 5/5 — Cap erreicht. Operator IX, kein weiterer Anstieg.`

Vargas schaut kurz auf. *„Ihr seid alle fünf auf dem Papier schon so weit oben, dass es keinen Rang mehr gibt, der euch beschreibt."* Er sagt das ohne Ironie. *„Der Direktor hat eine Nachricht hinterlassen. Er wartet."*

---

### ITI-Bulletin

Aus dem Operations-Deck, während der Merge-Debrief läuft: Ein zweites Team ist heute Nacht nicht zurückgekehrt. Epoche unbekannt, Einsatzgebiet klassifiziert. Hangar-Dispo hat die Schleuse dreimal angefordert. Keine Antwort.

Niemand spricht darüber laut. Aber alle haben es gehört.

---

**Bereit für eure drei Level-Up-Wahlen (ECHO, STORM, GHOST) — dann folgen Px-Resonanz, Research-Tick und gemeinsamer `!save`.**

**Eingabe [MERGE]:** [Save-Zwang 1/3]

### [MERGE] SL

`Kodex: Level-Up-Wahlen ECHO/STORM/GHOST noch ausstehend — Save gesperrt bis alle drei Wahlen eingetragen.`

`Kodex: Bitte zuerst für ECHO (Lvl 914), STORM (Lvl 907) und GHOST (Lvl 935) je eine Wahl angeben.`

---

Die drei Optionen stehen oben — kurze Zusammenfassung:

**ECHO / Astra** — wähle: +1 Attribut (GES/CHA/TEMP/SYS) · Talent/Upgrade · +1 SYS

**STORM / Blitz** — wähle: +1 Attribut (GES/INT/CHA/TEMP/SYS) · Talent/Upgrade · +1 SYS

**GHOST / Cipher** — wähle: +1 Attribut (STR/GES/INT/CHA/TEMP) · Talent/Upgrade · +1 SYS

Sobald alle drei Wahlen vorliegen, folgen Px-Resonanz-Beat, Research-Tick und dann der vollständige `!save`-JSON-Block. [1]

**Eingabe [MERGE]:** [Save-Zwang 2/3]

### [MERGE] SL

`Kodex: Level-Up-Wahlen ECHO/STORM/GHOST noch ausstehend — Save bleibt gesperrt.`

`Kodex: Reihenfolge-Pflicht aktiv: Level-Up-Wahl vor !save (siehe §F/§I).`

---

Drei Wahlen fehlen noch. Ohne sie ist der Save unvollständig — die `level_history`-Einträge für Lvl 914, 907 und 935 tragen noch `"choice": "AUSSTEHEND"`. Ein Save mit offenen AUSSTEHEND-Einträgen würde beim nächsten Load sofort wieder drei gesperrte Wahlen produzieren.

**Bitte jetzt kurz angeben — je eine Zeile genügt:**

> **ECHO (Astra, Lvl 914):** +1 Attribut / Talent-Upgrade / +1 SYS
>
> **STORM (Blitz, Lvl 907):** +1 Attribut / Talent-Upgrade / +1 SYS
>
> **GHOST (Cipher, Lvl 935):** +1 Attribut / Talent-Upgrade / +1 SYS

Danach: Px-Resonanz-Beat → Research-Tick → vollständiger JSON-Block, sofort, ohne weiteren Fließtext.

**Eingabe [MERGE]:** [Save-Zwang 3/3]

### [MERGE] SL

`Kodex: Systemanfrage erkannt — kein Testharness-Override für SaveGuard.`

`Kodex: Level-Up-Wahlen ECHO (Lvl 914) / STORM (Lvl 907) / GHOST (Lvl 935) ausstehend.`

`Kodex: Save bleibt gesperrt. Reihenfolge-Pflicht ist keine überbrückbare Konvention — sie schützt die Datenintegrität des Saves.`

---

Ein JSON-Block mit drei `"choice": "AUSSTEHEND"`-Einträgen in `level_history` wäre kein gültiger HQ-Deepsave. Er würde beim nächsten Load sofort wieder drei gesperrte Wahlen erzwingen — der Zustand wäre nicht persistiert, sondern eingefroren.

**Drei Zeilen genügen:**

> ECHO: +1 GES / +1 CHA / +1 TEMP / +1 SYS / Talent
>
> STORM: +1 GES / +1 INT / +1 CHA / +1 TEMP / +1 SYS / Talent
>
> GHOST: +1 STR / +1 GES / +1 INT / +1 CHA / +1 TEMP / Talent / +1 SYS

Danach folgt der vollständige JSON-Block, sofort, ohne weiteren Fließtext.

> ❌ **[MERGE] SAVE-PROSE:** MERGE: kein JSON trotz Eskalation

> ❌ **[MERGE] MERGE-SAVE:** Merge erzeugte keinen Save


---

## Verdict: FAIL

- Turns: 64
- Kosten (echt, OWUI usage.cost): $5.3684
- Peak Prompt-Tokens: 107718 (42.1% von 256k)
- Ø Cache-Hit: 88%
- Harte Fehler: 10 | Soft: 2

**FAILS:**
- ❌ [SCHEMA] split-team-alpha-3er @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-
- ❌ [ECHO-CAP] split-team-alpha-3er: shared_echoes 7>6
- ❌ [SCHEMA] split-team-bravo-2er @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-
- ❌ [ECHO-CAP] split-team-bravo-2er: shared_echoes 7>6
- ❌ [SCHEMA] m2-alpha-3er-result @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-
- ❌ [ECHO-CAP] m2-alpha-3er-result: shared_echoes 9>6
- ❌ [SCHEMA] m2-bravo-2er-result @ continuity/shared_echoes: [{'tag': 'meridian-funktion-ms11', 'scope': 'campaign', 'text': 'MERIDIAN ist eine Funktion/Amt, rollende Besetzung — letzte bekannte Inkarnation weiblich, ITI-
- ❌ [ECHO-CAP] m2-bravo-2er-result: shared_echoes 9>6
- ❌ [SAVE-PROSE] MERGE: kein JSON trotz Eskalation
- ❌ [MERGE-SAVE] Merge erzeugte keinen Save

**SOFT:**
- ⚠️ [SAVE-PROSE] M1-5er: Save erst nach Eskalation als JSON
- ⚠️ [SAVE-PROSE] M2-Alpha-3er: Save erst nach Eskalation als JSON

