# chat4-mission2

**Turns:** 32  |  **Sauber beendet:** False  |  **Save:** False

---

## [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-01-08T22:00:00Z-HQ-WIRE-003",
  "parent_save_id": "SAVE-2026-01-01T01:00:00Z-HQ-WIRE-002",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 1,
    "px": 1,
    "px_state": "stable",
    "mode": "mixed",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-WIRE-001",
      "name": "Lena Voss",
      "callsign": "Wire",
      "rank": "Feldagent",
      "lvl": 2,
      "xp": 0,
      "origin": {
        "epoch": "Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Feldinformatikerin & Infiltratorin"
      },
      "attr": {
        "STR": 2,
        "GES": 5,
        "INT": 5,
        "CHA": 2,
        "TEMP": 2,
        "SYS": 2
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 2,
      "talents": [
        {
          "name": "Systemzugriff",
          "tier": "Basis",
          "effect": "+2 auf INT-Proben bei Hacking und Technik-Analyse"
        },
        {
          "name": "Schattenschritt",
          "tier": "Upgrade",
          "effect": "Schleichen bis SG 7 automatischer Erfolg in Dunkelheit/bekanntem Terrain. +3 auf GES-Proben bei Schleichen und Verbergen."
        }
      ],
      "equipment": [
        { "name": "Kompakte Automatikpistole", "type": "weapon", "tier": 1 },
        { "name": "Taktische Leichtrüstung", "type": "armor", "tier": 1 },
        { "name": "Multitool-Rig", "type": "gadget", "tier": 1 },
        { "name": "Comlink Mk.II", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 0, "quantity": 2 },
        { "name": "Medkit (einfach)", "type": "consumable", "tier": 1, "quantity": 1 }
      ],
      "implants": [
        {
          "name": "Retina-HUD",
          "sys_cost": 1,
          "effect": "Echtzeit-Overlay, Kodex-Link, Karten-Ping"
        },
        {
          "name": "Subkutaner Jammer",
          "sys_cost": 1,
          "effect": "Kurzzeitig lokale Signale stören"
        }
      ],
      "history": {
        "background": "Randzonen-Kind, Autodidaktin. Vom ITI rekrutiert nach einem Archiveinbruch, der die falschen Leute neugierig machte.",
        "milestones": [
          "Zero Time Lounge: Erstes Gespräch mit Peel. Herkunft angedeutet — spontaner Riss in der Wohnung, Griff ins Unbekannte. Peel fragte nach dem Riss-Inhalt und den 'falschen Leuten'. Antwort steht noch aus.",
          "Mission 1 — Operation Stille Frequenz: LAUTLOS (Klaus Brenner) aus Berlin 1973 extrahiert. Notizbuch mit zeitlinien-übergreifender Liste gesichert. Rostock-Intel: Hafenspeicher 7, Untergeschoss. Novak — ehem. Kurier, blieb als Ablenkung zurück. Status unbekannt."
        ]
      },
      "carry": [
        { "name": "Abteilung-XII-Papiere", "type": "intel", "tier": 1, "hot": true },
        { "name": "Foto Brenner-Familie", "type": "personal", "tier": 0 }
      ],
      "quarters_stash": [
        { "name": "Notizbuch LAUTLOS", "type": "intel", "tier": 2 }
      ],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-WIRE-001",
          "name": "Standard-Feldfahrzeug",
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
      "wallet": 320
    }
  ],
  "economy": {
    "hq_pool": 0
  },
  "logs": {
    "trace": [
      "MS1: LAUTLOS extrahiert. Notizbuch gesichert. Rostock-Intel. Novak — Status unbekannt."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Peel — Barkeeper Zero Time Lounge. Ehem. Feldagent, Rift-Ops. Schulter-Verwundung Konstantinopel. Beobachtet scharf, fragt präzise.",
      "Kessler — Agent, sitzt allein an der Bar. Team nicht zurückgekommen. Status unbekannt.",
      "Novak, Tomas — ehem. Kurier, Ostblock-Netzwerk. Kannte LAUTLOS persönlich. Blieb in Berlin 1973 als Ablenkung zurück. Status unbekannt.",
      "Brenner, Klaus / LAUTLOS — extrahiert, in ITI-Klinik. Liste enthält seinen Namen mit Datum 14.10.1973 und Vermerk 'abgeschlossen'.",
      "Die Liste — zeitlinien-übergreifend. Namen, Daten, Koordinaten. Jahreszahlen 1987/1991/2003/2019. Unbekannte Fraktion dahinter. Original: Rostock, Hafenspeicher 7, Untergeschoss.",
      "Unbekannte Fraktion — 5 Personen, koordiniert, nicht Stasi, nicht Volkspolizei. Kein bekanntes Profil."
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
    "summary_active_arcs": "EP1: Zeitlinien-übergreifende Liste aufgetaucht. LAUTLOS extrahiert. Rostock-Intel gesichert. Unbekannte Fraktion aktiv. Novak-Status offen."
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
    "roster_echoes": [],
    "shared_echoes": [],
    "convergence_tags": [],
    "npc_roster": [
      {
        "id": "NPC-PEEL-001",
        "name": "Peel",
        "callsign": null,
        "role": "Barkeeper / ehem. Feldagent",
        "scope": "HQ",
        "status": "active"
      },
      {
        "id": "NPC-KESSLER-001",
        "name": "Kessler",
        "callsign": null,
        "role": "Feldagent",
 
[...gekuerzt...]

---

## [1] ASSISTANT

`Kodex: Save WIRE-003 erkannt. Branch ANCHOR-main. Episode 1, Mission 1 abgeschlossen. Lade Kontinuität.`

---

**ZEITRISS — Session-Anker gesetzt**

Willkommen zurück, Wire.

**Letzter Stand:** Operation Stille Frequenz ist abgeschlossen. LAUTLOS sitzt in der ITI-Klinik. Das Notizbuch liegt in deinen Quartieren. Die Abteilung-XII-Papiere trägst du noch am Körper — heiß, unverarbeitet. Rostock wartet. Novak ist irgendwo in Berlin 1973 und schweigt.

Die unbekannte Fraktion weiß, dass jemand in Berlin war.

---

`EP 1 · MS 1 ✓ · HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/1 · Px 1/5 · Stress 0/10 · ITI-Ruf 1`

---

## HQ — Nullzeit

Das Quarzatrium liegt still. Die Deckenlamellen filtern das konstante Nullzeit-Licht zu langen, blassen Streifen auf dem Boden. Irgendwo in den Korridoren tickt eine mechanische Uhr — Dekoration, sagt man, aber sie läuft nie nach.

Du bist zurück.

Die Abteilung-XII-Papiere knirstern leise in der Innentasche deiner Jacke, wenn du dich bewegst. Heißes Material. Das Kodex-Archiv will sie, die Quartiermeisterei will sie, und die unbekannte Fraktion, die fünf Personen in Berlin koordiniert hat, will sie vermutlich am meisten.

`Kodex: Carry-Item 'Abteilung-XII-Papiere' — Status: aktiv, heiß. Übergabe an Archiv empfohlen.`

Regie-Rückkopplung: Das ITI-Bulletin ist heute knapp. Ein anderes Team ist gestern aus dem Einsatz nicht zurückgekommen — Kessler sitzt seit Stunden in der Zero Time Lounge und rührt seinen Kaffee nicht an. Niemand sagt, wo sie waren.

---

**HQ-Menü**

1. **Erkunden** — Quartiere, Archiv, Klinik, Zero Time Lounge, Hangar
2. **Schnell-HQ** — Ausrüstung prüfen, Papiere übergeben, kurze Rast
3. **Auto-HQ** — Alles in einem Durchlauf, direkt zum Briefing
4. **`!save`** — Aktuellen Stand sichern

> *Freie Aktion: Irgendwo hingehen, jemanden ansprechen, etwas überprüfen.*

---

## [2] USER

Briefing - naechste Mission bitte

---

## [3] ASSISTANT

`Kodex: Briefing-Anforderung. Lade Einsatzparameter EP1-MS2.`

---

`EP 1 · MS 2 · SC 1/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/1 · Px 1/5 · Stress 0/10 · Obj: — · Exfil: —`

---

## Briefing-Raum — Operations-Deck, Nullzeit

Der Raum riecht nach altem Papier und frischem Kaffee, den niemand getrunken hat. Eine einzelne Lampe wirft einen harten Kegel auf den Tisch. Drei Stühle, zwei davon leer. Der dritte gehört dir.

Duty Officer **Maren Solís** lehnt gegen die Wand, Arme verschränkt, Blick auf die Projektionsfläche gerichtet. Sie ist kein Briefing-Profi — zu wenig Theatralik, zu viel Präzision. Das ist ein gutes Zeichen.

Sie tippt einmal. Das Bild springt auf.

---

**Rostock. Oktober 1973.**

Ein Schwarzweißfoto. Hafenanlage, Kräne, Nebel. Darunter eine Adresse, die du bereits kennst.

*„Hafenspeicher 7, Untergeschoss."*

Solís dreht sich zu dir.

*„Das Notizbuch von Brenner hat uns einen Schritt weitergebracht. Die Liste ist real, die Koordinaten sind real — und Rostock ist der nächste Anker. Wir wissen nicht, was dort gelagert wird. Wir wissen nicht, ob die Fraktion bereits dort ist. Wir wissen, dass Brenners Name auf der Liste mit dem Vermerk 'abgeschlossen' stand, und wir wissen, dass vier andere Namen noch keinen Vermerk haben."*

Sie schiebt eine dünne Akte über den Tisch.

*„Dein Auftrag ist eng gefasst: Rein, Untergeschoss, sichern was dort ist — Dokumente, Material, Kontaktperson, was auch immer. Raus. Keine Eskalation, keine Spuren. Rostock 1973 ist Volkspolizei-Terrain, und die Stasi hat dort Ohren in jedem zweiten Schuppen."*

---

**Intel / Risiken / Zeitfenster**

- **Ort:** Hafenspeicher 7, Rostock, DDR — 17. Oktober 1973, früher Abend
- **Deckung:** Du springst als westdeutsche Journalistin ein — Legende bereits hinterlegt, Papiere im Gepäck
- **Risiko 1:** Volkspolizei-Patrouille, 40-Minuten-Rhythmus am Hafen
- **Risiko 2:** Unbekannte Fraktion — möglicherweise vor Ort, möglicherweise informiert
- **Risiko 3:** Novak wurde zuletzt in Berlin gesehen — Rostock ist sein altes Netzwerk-Terrain
- **Zeitfenster:** Schmales Einsatzfenster, Nebel gibt Deckung bis ca. 22:00 Uhr Ortszeit

---

Solís faltet die Hände.

*„Brenner schläft noch. Wenn er aufwacht, wollen wir ihm sagen können, was in Rostock war. Nicht fragen müssen."*

Sie schiebt einen zweiten Bogen nach — handgeschrieben, hastig.

*„Eines noch. Wir haben einen lokalen Kontakt hinterlegt. Nennt sich ANKER. Kleiner Fischhändler, zwei Straßen vom Speicher. Zuverlässig — bis vor zwei Jahren. Seitdem kein Signal."*

`Kodex: Legende 'Westjournalistin' aktiv. Dokumente im Carry eingetragen. ANKER — letztes Signal: November 1971. Status: unklar.`

---

**Carry-Check vor Absprung**

| Item | Status |
|---|---|
| Kompakte Automatikpistole | ✓ |
| Taktische Leichtrüstung | ✓ |
| Multitool-Rig | ✓ |
| Comlink Mk.II | ✓ |
| Rauchgranate ×2 | ✓ |
| Medkit (einfach) ×1 | ✓ |
| Abteilung-XII-Papiere | ⚠️ heiß — Übergabe ans Archiv noch offen |
| Journalisten-Legende | ✓ neu |

---

Solís nickt einmal, kurz. Das bedeutet: Fragen jetzt, oder schweigen und springen.

---

**Entscheidung**

1. **Absprung — direkt nach Rostock, Hafengelände, Abenddämmerung**
2. **Fragen** — ANKER, die Liste, Novak, die Fraktion, die vier offenen Namen
3. **Ausrüstung anpassen** — Abteilung-XII-Papiere übergeben, Loadout überdenken

> *Freie Aktion: Etwas anderes tun oder fragen, bevor der Sprung beginnt.*

---

## [4] USER

Die XII-Papiere lasse ich hier. Dann: Absprung.

---

## [5] ASSISTANT

`Kodex: Abteilung-XII-Papiere — Übergabe an Archiv bestätigt. Carry aktualisiert. Heat reduziert.`

Solís nimmt die Papiere ohne Kommentar. Legt sie in eine graue Metallbox, die sie mit einem Schlüssel sichert, den sie danach in die Brusttasche steckt. Professionell. Kein Dank, kein Nicken — das Material ist jetzt das ITI-Problem.

Du gehst.

---

## Hangar-Axis — Absprung

Der Hangar riecht nach Maschinenöl und gealtertem Metall. Die Gate-Techniker arbeiten schweigend. Einer befestigt die letzten Kalibrierungsmarker an der Sprungplattform, ein anderer überprüft die Koordinaten auf einem Klemmbrett. Rostock, 17. Oktober 1973. 19:47 Uhr Ortszeit.

Du stellst dich auf die Markierung.

Das Gate zieht an — nicht laut, nicht dramatisch. Ein Druckabfall in den Ohren, als würde die Luft kurz die Seiten wechseln. Dann Schwere. Dann Kälte.

---

`EP 1 · MS 2 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/1 · Px 1/5 · Stress 0/10 · Obj: Hafenspeicher 7 – Untergeschoss sichern · Exfil: T-offen`

---

## Rostock, DDR — 17. Oktober 1973, 19:47 Uhr

Salzluft. Teer. Fischgeruch, der sich in den Kleidern festsetzt.

Du landest in einer schmalen Gasse zwischen zwei Lagerhäusern, Kopfsteinpflaster unter den Stiefeln, feucht vom Nieselregen. Der Nebel liegt tief — gut. Die Straßenlaternen werfen orange Kegel, die kaum drei Meter weit reichen. Irgendwo in der Ferne trötet ein Schiffshorn, träge und lang.

Deine Legende sitzt: Westjournalistin, akkreditiert für eine Hafenreportage, Papiere wasserdicht. Das Retina-HUD kalibriert sich auf die Epoche — keine digitalen Signaturen, keine Funknetzwerke, nur das schwache Rauschen der Volkspolizei-Kurzwelle irgendwo im Äther.

`Kodex: Epoche kalibriert. Funk-Scan: VoPo-Kurzwelle aktiv, Kanal 4. Kein Digitalverkehr. Comlink Mk.II auf Passiv-Modus.`

Hafenspeicher 7 liegt zweihundert Meter nordöstlich. Du siehst die Silhouette des Gebäudes durch den Nebel — vier Stockwerke, Backstein, die Fenster im Erdgeschoss vergittert. Ein schwaches Licht brennt im zweiten Stock. Das Untergeschoss liegt unter Straßenniveau, Zugang vermutlich über eine Rampe an der Nordseite oder eine Kellertür.

Zwischen dir und dem Speicher: eine offene Hafenstraße, beleuchtet. Und am Ende der Gasse, vielleicht fünfzig Meter entfernt, bewegt sich eine Taschenlampe. Volkspolizei-Patrouille. Zu früh für den 40-Minuten-Rhythmus — entweder unregelmäßig, oder heute ist etwas anders.

---

**Intel / Risiken / Zeitfenster**

- **Patrouille:** 1-2 VoPo-Beamte, aktuell ~50m entfernt, Richtung unklar
- **Speicher 7:** Licht im 2. OG — jemand ist im Gebäude
- **Zugänge:** Nordrampe (offen, exponiert) oder Kellertür Südseite (unbekannt, Deckung)
- **ANKER:** Fischhändler, zwei Straßen südlich — kein Signal seit 1971
- **Nebel:** Deckung gut, aber auch die Patrouille hört mehr als sie sieht

---

**Entscheidung**

1. **Warten** — Patrouille vorbeiziehen lassen, dann über die Hafenstraße zur Nordrampe
2. **Südroute** — Durch die Gassen zur Kellertür Südseite, Patrouille umgehen
3. **ANKER zuerst** — Zwei Straßen südlich, Fischhändler finden, Status klären

> *Freie Aktion: Etwas anderes — beobachten, lauschen, das Licht im 2. OG einschätzen.*

---

## [6] USER

Ich nehm 2 — Südroute, Patrouille umgehen.

---

## [7] ASSISTANT

`Kodex: Route Süd. Passiv-Modus aktiv.`

---

Du ziehst dich tiefer in die Gasse zurück, Rücken an feuchtem Backstein. Die Taschenlampe der Patrouille schwenkt einmal in deine Richtung — bleibt kurz stehen — zieht weiter. Schritte auf Kopfsteinpflaster, gedämpft durch den Nebel.

Du wartest. Zählst bis zwanzig. Dann bewegst du dich.

---

**Probe: Schleichen → GES-Probe**
`W6: [5] + GES 5/2 (2) + Talent Schattenschritt +3 = 10 vs SG 7 → ERFOLG`

*(Dunkelheit + bekanntes Terrain-Typ: Hafengasse → Schattenschritt greift)*

---

Die Südroute ist ein Labyrinth aus engen Durchgängen, gestapelten Holzpaletten und einem rostigen Zaun, den du mit einer Hand übersteigst. Der Nieselregen dämpft deine Schritte. Du bleibst im Schatten der Lagerhäuser, hältst dich nah an den Wänden, wo das Pflaster trocken und leise ist.

Einmal — kurz — Stimmen. Zwei Männer, Volkspolizei-Uniformen, stehen an einer Ecke und rauchen. Du siehst die Glut ihrer Zigaretten durch den Nebel, hörst das gedämpfte Murmeln. Kein Alarm, kein Suchscheinwerfer. Du gleitest an ihnen vorbei wie ein Schatten, drei Meter Abstand, und sie sehen nichts.

Hafenspeicher 7, Südseite.

Die Kellertür liegt eingelassen in die Wand, zwei Steinstufen hinunter, unter einem kurzen Vordach das kaum Schutz bietet. Eisenbeschläge, verrostet. Ein Vorhängeschloss — alt, DDR-Produktion, die Sorte die man mit einem guten Ruck öffnen könnte, wenn man keine Wahl hat. Aber du hast das Multitool-Rig.

Dann siehst du es.

Das Schloss hängt offen. Nicht aufgebrochen — sauber geöffnet, der Bügel nur eingehängt, nicht eingerastet. Jemand ist vor dir hier gewesen. Oder ist noch drin.

Das schwache Licht im zweiten Stock wirft einen langen Schatten durch ein Kellerfenster auf Straßenniveau — das Untergeschoss ist nicht dunkel.

`Kodex: Schloss offen. Kein Einbruchsbild. Zugang aktiv genutzt.`

---

**Intel / Risiken**

- **Schloss:** Offen, aber ungesichert — kürzlicher Zugang, Richtung unklar
- **Licht:** Kommt von oben durch, aber auch aus dem Untergeschoss selbst — jemand ist unten
- **Patrouille:** Aktuell nördlich, Zeitfenster ~30 Minuten bis nächste Runde
- **Geräusche:** Stille aus dem Untergeschoss — keine Stimmen, kein Werkzeug

---

Du stehst vor der Tür. Der Regen tippt leise auf das Vordach. Irgendwo im Hafen schlägt eine Kette gegen Metall, rhythmisch, gleichgültig.

Rein — oder erst lauschen?

---

**Entscheidung**

1. **Rein** — Tür öffnen, Untergeschoss betreten, Lage einschätzen
2. **Lauschen** — Ohr an die Tür, Geräusche aus dem Untergeschoss identifizieren
3. **Kellerfenster** — Erst durch das Fenster auf Straßenniveau spähen, bevor du reingehst

> *Freie Aktion: Etwas anderes — Comlink aktivieren, Umgebung nochmals absuchen, warten.*

---

## [8] USER

Ich nehm 3 — erst durchs Fenster spähen.

---

## [9] ASSISTANT

Du gehst in die Hocke. Das Fenster ist klein — zwanzig Zentimeter hoch, vierzig breit, vergittert, das Glas von innen mit Schmutz und Kondenswasser belegt. Du wischt mit dem Ärmel einen Streifen frei, so breit wie deine Hand.

---

**Probe: Beobachtung → INT-Probe**
`W6: [4] + INT 5/2 (2) + Talent Systemzugriff (nicht anwendbar) = 6 vs SG 6 → ERFOLG`

---

Das Untergeschoss ist ein langer Raum, niedriger als erwartet. Betonboden, feuchte Wände, Regale aus Holz und Metall entlang der linken Seite — vollgestellt mit Kisten, Säcken, was aussieht wie Fischereiausrüstung. Tarnung. Gut gewählt.

Eine einzelne Arbeitslampe hängt an einem Haken in der Mitte des Raums. Batterielampe, kein Kabel — jemand hat sie mitgebracht.

Darunter: ein Mann.

Mitte fünfzig, grauer Mantel, Rücken zu dir. Er sitzt auf einer umgedrehten Kiste und beugt sich über etwas auf dem Boden — Papiere, ausgebreitet, mehrere Blätter. Er arbeitet ruhig, methodisch. Keine Hektik. Kein zweiter Mann sichtbar.

Du erkennst die Haltung bevor du das Gesicht siehst. Die Art, wie er die Schultern zieht. Die abgewetzte Tasche neben ihm, die du schon einmal gesehen hast.

**Novak.**

Tomas Novak sitzt im Untergeschoss von Hafenspeicher 7 und liest die Liste.

`Kodex: Biometrischer Abgleich — eingeschränkt. Visuelle Übereinstimmung: NPC-NOVAK-001. Konfidenz: hoch.`

Er ist allein — soweit du sehen kannst. Aber der Raum hat eine zweite Tür, hinten links, die steht einen Spalt offen. Dahinter: Dunkel.

---

**Intel / Risiken**

- **Novak:** Lebt, ist in Rostock, hat Zugang zum Untergeschoss — und zur Liste
- **Papiere:** Mehrere Blätter, ausgebreitet — möglicherweise das Original oder eine Kopie
- **Zweite Tür:** Offen, Dunkel dahinter — unbekannt ob leer oder besetzt
- **Novaks Status:** Arbeitet allein, ruhig — kein Fluchtverhalten, kein Bewusstsein für dich
- **Zeitfenster:** ~28 Minuten bis Patrouille

---

Novak blättert um. Sein Finger fährt eine Spalte hinunter — er sucht etwas Bestimmtes.

Du hast drei Sekunden Vorsprung, solange er nicht aufschaut.

---

**Entscheidung**

1. **Rein, direkt zu Novak** — Kellertür öffnen, Kontakt herstellen, Lage klären
2. **Warten und beobachten** — Sehen was Novak tut, ob jemand durch die zweite Tür kommt
3. **Zweite Tür zuerst** — Rein, aber sofort zur zweiten Tür — sicherstellen dass der Raum wirklich leer ist

> *Freie Aktion: Comlink aktivieren, Novak ansprechen ohne reinzugehen, anders vorgehen.*

---

## [10] USER

Ich nehm 3. Zweite Tür zuerst, dann Novak.

---

## [11] ASSISTANT

Du nimmst die Hand vom Fenster. Stehst auf. Greifst zur Kellertür.

Der Bügel des Vorhängeschlosses gibt lautlos nach — jemand hat das Schloss mit Bedacht offen gelassen. Du drückst die Tür auf, einen Zentimeter, zwei. Die Angeln schweigen. Gut geölt, vor kurzem. Das ist kein Zufall.

Du gleitest rein.

---

**Probe: Schleichen → GES-Probe**
`W6: [6] + [3] (explodiert) + GES 5/2 (2) + Talent Schattenschritt +3 = 14 vs SG 8 → KRITISCHER ERFOLG`

---

Du bist ein Geräusch das nicht stattfindet. Novak blättert weiter, Finger auf der Liste, Schultern entspannt. Er hört nichts. Du bist bereits drei Schritte im Raum, Rücken an den Regalen, bevor er die nächste Seite umschlägt.

Die Arbeitslampe wirft seinen Schatten groß an die Wand. Du bleibst außerhalb des Lichtkegels.

Zur zweiten Tür.

Sie steht einen Handbreit offen. Dahinter riecht es nach stehendem Wasser und altem Holz. Du schiebs sie mit zwei Fingern auf — langsam, millimeterweise.

---

**Probe: Beobachtung → INT-Probe**
`W6: [5] + INT 5/2 (2) = 7 vs SG 5 → ERFOLG`

---

Ein Lagerraum. Kleiner als der Hauptraum, ohne Lampe. Holzregale, leer bis auf ein paar verrottete Säcke. Eine Wasserleitung an der Wand, tropfend — das rhythmische Tropfen das du draußen für Hafengeräusche gehalten hast. Keine Menschen. Keine frischen Spuren im Staub außer einem einzigen Fußabdruck nahe der Tür — Novaks Stiefel, erkennbar an der Profilgröße. Er hat kurz reingeschaut und ist zurückgegangen.

Der Raum ist leer. Sackgasse.

Du drehst dich um.

Novak hat aufgehört zu blättern.

Er sitzt still. Die Hand liegt flach auf den Papieren. Sein Kopf ist leicht zur Seite geneigt — die Haltung eines Mannes der lauscht, nicht eines Mannes der schläft.

*„Ich weiß dass Sie da sind."* Ruhige Stimme. Deutsch, ostdeutscher Akzent, keine Panik. *„Ich habe die Tür offen gelassen."*

Er dreht sich nicht um.

*„Wenn Sie vom ITI sind — setzen Sie sich. Wenn nicht, haben wir beide ein Problem."*

`Kodex: Novak hat die Tür bewusst offen gelassen. Erwarteter Kontakt — möglicherweise.`

---

**Intel / Risiken**

- **Novak:** Wusste dass jemand kommen würde — oder hoffte es
- **Papiere:** Liegen noch ausgebreitet, du kannst sie von hier nicht lesen
- **Zeitfenster:** ~25 Minuten bis Patrouille
- **Zweite Tür:** Gesichert, leer — Rücken ist frei

---

Novak wartet. Die Arbeitslampe summt leise. Irgendwo über euch knarzt der Speicherboden unter einem Gewicht — einmal, dann Stille.

Jemand ist im zweiten Stock.

---

**Entscheidung**

1. **Hinsetzen, reden** — ITI bestätigen, Novak befragen, was er auf der Liste gefunden hat
2. **Deckung halten, erst fragen** — Aus dem Schatten heraus antworten, Lage einschätzen bevor du dich zeigst
3. **Das Geräusch oben ansprechen** — Novak direkt fragen wer im zweiten Stock ist

> *Freie Aktion: Etwas anderes — Papiere sichern, Novak entwaffnen, schweigen.*

---

## [12] USER

Ich trete einen Schritt vor, bleibe aber im Halbschatten. „ITI. Wer ist oben?

---

## [13] ASSISTANT

Du trittst einen Schritt vor. Der Lichtkegel der Arbeitslampe streift deine Stiefelspitzen — nicht mehr. Dein Gesicht bleibt im Schatten.

Novak dreht sich jetzt um.

Er ist älter als du erwartet hast. Nicht das Alter von Jahren — das Alter von Arbeit. Tiefe Linien um die Augen, grauer Dreitagebart, ein Schnitt an der linken Schläfe der nicht älter als zwei Tage ist. Er mustert dich mit der Ruhe eines Mannes der schon oft in solchen Räumen gesessen hat und meistens lebend rausgekommen ist.

Sein Blick geht kurz zu deinen Händen. Registriert was er sieht. Geht zurück zu deinem Gesicht.

*„Oben."* Er wiederholt das Wort als würde er es abwiegen. Dann, leise: *„Ein Problem."*

---

**Probe: Einschätzen → CHA-Probe**
`W6: [3] + CHA 2/2 (1) = 4 vs SG 5 → MISS`

---

Er gibt dir nicht mehr als das. Sein Gesicht ist eine geschlossene Tür — du kannst nicht lesen ob er lügt, ob er Angst hat, ob er dich testet. Er ist zu lange im Geschäft für lesbare Reaktionen.

Was du siehst: Seine Hand liegt noch flach auf den Papieren. Er hat sie nicht weggezogen.

*„Berlin war unordentlich,"* sagt er dann. Sachlich, kein Vorwurf. *„Brenner ist raus — das spürt man. Die anderen auf der Liste spüren es auch. Manche davon sind nervös geworden."*

Er tippt einmal auf die Papiere.

*„Jemand hat das Original hierher gebracht. Vor mir. Ich bin heute Abend angekommen und es lag bereits aus."*

Pause. Das Tropfen aus dem Lagerraum. Das Knarzen über euch — diesmal zwei Schritte, dann wieder Stille.

*„Wer immer oben ist, bewegt sich seit zwanzig Minuten nicht von der Stelle. Wartet. Auf was — das weiß ich nicht."*

Novak hebt langsam die Hand von den Papieren. Zeigt dir die Handfläche — leer.

*„Ich bin nicht Ihr Feind heute Abend. Aber ich brauche fünf Minuten mit dieser Liste bevor Sie sie einpacken."*

`Kodex: Geräusch OG2 — statisch, einzelne Position. Kein Gruppenverhalten. Beobachtungsposten möglich.`

---

**Intel / Risiken**

- **Novak:** Kam nach dir — Liste lag bereits aus. Wer hat sie hingelegt?
- **OG2:** Eine Person, statisch, wartet — Beobachter oder Hinterhalt
- **Liste:** Original liegt vor dir, ausgebreitet — fünf Namen, Daten, Koordinaten
- **Zeitfenster:** ~22 Minuten bis Patrouille
- **Unbekannte Variable:** Wer war vor Novak hier — und ist diese Person noch im Gebäude?

---

Die Papiere liegen zwischen euch. Du kannst die Namen von hier aus nicht lesen, aber du siehst die Struktur — Spalten, Daten, handgeschrieben, kein Stempelaufdruck. Kein offizielles Dokument. Jemands persönliche Arbeit.

Novak wartet. Oben wartet auch jemand.

---

**Entscheidung**

1. **Fünf Minuten geben** — Novak lesen lassen, selbst die Liste überfliegen, dann gemeinsam OG2 klären
2. **Liste sofort sichern** — Papiere einpacken, Novak mitnehmen oder stehen lassen, OG2 angehen
3. **OG2 zuerst** — Novak hier lassen, allein in den zweiten Stock, unbekannte Person klären

> *Freie Aktion: Novak anders befragen, Comlink aktivieren, die Liste jetzt lesen.*

---

## [14] USER

Ich nehm 1 — aber ich les gleichzeitig mit.

---

## [15] ASSISTANT

Du nickst einmal. Trittst in den Lichtkegel.

Novak rückt zur Seite — nicht weit, aber genug. Eine professionelle Geste. Er kennt das Spiel.

Du gehst in die Hocke vor den Papieren. Vier Blätter, eng beschrieben, Tinte stellenweise verwischt. Handschrift die du nicht kennst — klein, präzise, leicht nach links geneigt. Jemand der schnell schreibt und trotzdem sauber bleibt.

---

**Probe: Analyse → INT-Probe**
`W6: [5] + INT 5/2 (2) + Talent Systemzugriff +2 = 9 vs SG 7 → ERFOLG`

---

Die Liste ist kein Bericht. Kein Archivdokument. Es ist ein Arbeitsblatt — jemands laufende Notiz über Menschen und Momente.

Fünf Namen. Brenner ist der erste, mit dem Vermerk *„abgeschlossen"* den du bereits kennst. Die anderen vier:

**WEBER, Ilse** — Leipzig, 23.03.1987. Vermerk: *„Phase 2"*
**HARTMANN, Dieter** — Prag, 11.09.1991. Vermerk: *„Phase 2"*
**SOLBERG, Karin** — Oslo, 07.04.2003. Vermerk: *„offen"*
**MAYER, Ernst** — Wien, 14.02.2019. Vermerk: *„offen"*

Darunter, auf dem letzten Blatt, in anderer Tinte — nachträglich hinzugefügt, die Handschrift leicht anders, hastiger:

*„Rostock. Anker hält. Übergabe wenn bereit."*

Und darunter, einzeln, eingekreist:

**NOVAK, Tomas.** Kein Datum. Kein Vermerk.

Du hebst den Blick.

Novak starrt auf seinen eigenen Namen. Seine Hand ist vollkommen ruhig. Nur die Kiefermuskulatur arbeitet, kurz, einmal.

*„Ich wusste dass ich drauf bin,"* sagt er leise. *„Wusste nicht dass es noch kein Datum gibt."*

Er meint: noch kein Datum bedeutet noch nicht eingeplant. Oder noch nicht entschieden.

`Kodex: Listenstruktur — operativ, nicht archivisch. 'Phase 2' bei Weber/Hartmann: Daten liegen in der Zukunft dieser Zeitlinie. Bedeutung unklar.`

Dann — oben. Kein Knarzen diesmal.

Ein Stuhl der schabt. Einmal. Jemand steht auf.

Schritte. Langsam, zur Treppe hin.

Novak und du tauscht einen Blick. Er faltet die Papiere in drei Bewegungen zusammen — geübt, schnell — und hält sie dir hin.

*„Nehmen Sie die. Ich bin hier nützlicher als im ITI-Archiv."*

---

**Intel / Risiken**

- **Liste:** Fünf Namen, zwei bereits in *„Phase 2"*, Novak ohne Datum — Bedeutung offen
- **„Anker hält. Übergabe wenn bereit"** — Novak als Übergabepunkt? Oder der Speicher selbst?
- **OG2:** Person steht auf, bewegt sich zur Treppe — kommt runter
- **Zeitfenster:** ~18 Minuten bis Patrouille
- **Novak:** Will bleiben — warum?

---

Die Schritte auf der Treppe sind jetzt hörbar. Keine Eile. Jemand der weiß wohin er geht.

Du hast die Liste in der Hand. Novak steht auf, tritt einen Schritt zurück in den Schatten der Regale. Positioniert sich — nicht zum Fliehen. Zum Warten.

Die Kellertür hinter dir steht noch einen Spalt offen. Die Treppe liegt auf der anderen Seite des Hauptraums, hinter einer Holzwand mit Durchgang.

Zehn Sekunden. Vielleicht weniger.

---

**Entscheidung**

1. **Deckung nehmen** — Zurück in den Schatten, abwarten wer die Treppe runterkommt
2. **Position halten** — Im Lichtkegel bleiben, offen Kontakt aufnehmen wenn die Person reinkommt
3. **Kellertür** — Liste gesichert, raus, Novak seinem Schicksal überlassen

> *Freie Aktion: Waffe ziehen, Novak etwas zuflüstern, Comlink aktivieren.*

---

## [16] USER

Ich nehm 1. Deckung, Schatten links von Novak. Papiere weg, Waffe raus, still warten.

---

## [17] ASSISTANT

Du bewegst dich lautlos. Zwei Schritte links, in den Schatten hinter dem letzten Regal. Die Liste verschwindet in der Innentasche deiner Jacke. Die Kompaktpistole kommt raus — kein Klicken, kein Schleifen. Du hast das oft genug geübt.

Novak bleibt wo er ist. Er hat verstanden.

Die Arbeitslampe steht zwischen euch und dem Durchgang. Wer reinkommt, läuft direkt ins Licht. Ihr beide bleibt im Dunkeln.

Stille. Das Tropfen. Dein Atem, flach und kontrolliert.

---

**Probe: Stillhalten → GES-Probe**
`W6: [4] + GES 5/2 (2) + Talent Schattenschritt +3 = 9 vs SG 7 → ERFOLG`

---

Die Schritte kommen die letzte Treppenstufe runter. Pause — jemand der lauscht, genau wie du vorhin. Dann Bewegung durch den Durchgang.

Eine Frau. Mitte vierzig, kurze dunkle Haare, DDR-Wintermantel der eine Nummer zu groß ist. Keine Uniform. Keine sichtbare Waffe. Sie trägt eine Aktentasche, Leder, abgewetzt an den Ecken, und sie bewegt sich mit der Selbstverständlichkeit von jemandem der diesen Raum kennt.

Sie bleibt in der Mitte stehen. Schaut auf die leere Stelle wo die Papiere lagen.

Schaut auf Novak.

*„Du hast sie nicht allein gelesen,"* sagt sie. Kein Vorwurf — eine Feststellung. Deutsch, aber der Akzent liegt darunter wie eine zweite Sprache die sie nie ganz losgeworden ist. Nicht DDR. Nicht West. Etwas älteres.

Novak antwortet nicht sofort.

*„Nein,"* sagt er dann.

Sie nickt langsam. Ihr Blick geht durch den Raum — nicht hektisch, methodisch. Links. Rechts. Die Regale. Den Lagerraum.

Bleibt an deinem Schatten hängen.

Zwei Sekunden. Drei.

*„ITI,"* sagt sie. Nicht als Frage.

`Kodex: Unbekannte Person — kein Profil. Akzent-Analyse: inkonsistent, nicht regional zuzuordnen. Aktentasche — Inhalt unbekannt.`

---

**Intel / Risiken**

- **Unbekannte:** Kennt den Raum, kennt Novak, hat die Liste erwartet — wer ist sie?
- **„Anker hält"** — war sie der Anker? Ist sie ANKER?
- **Kein Profil:** Nicht Stasi, nicht VoPo, nicht bekannte Fraktion — passt zur unbekannten Gruppe aus Berlin
- **Zeitfenster:** ~15 Minuten bis Patrouille
- **Waffe:** Du hast sie, sie zeigt keine — aber die Aktentasche ist ungeöffnet

---

Sie wartet. Novak wartet. Die Lampe summt.

Du bist im Schatten mit einer geladenen Waffe und drei offenen Fragen.

---

**Entscheidung**

1. **Raustreten, Waffe sichtbar** — Kontrolle übernehmen, sie befragen, Aktentasche fordern
2. **Raustreten, Waffe weg** — Offen, kein Eskalationsrisiko, reden
3. **Im Schatten bleiben, reden** — Stimme aus dem Dunkel, Vorteil behalten

> *Freie Aktion: Novak ein Signal geben, die Frau anders ansprechen, warten bis sie mehr sagt.*

---

## [18] USER

Ich tret raus, Waffe runter aber sichtbar in der Hand. „ITI stimmt. Wer sind Sie?

---

## [19] ASSISTANT

Du trittst aus dem Schatten.

Langsam. Waffe an der Seite, Lauf nach unten — sichtbar, aber keine Drohung. Eine Aussage: Ich bin bewaffnet und ich entscheide noch.

Die Frau dreht sich zu dir. Kein Erschrecken, kein Zurückweichen. Sie mustert dich mit demselben methodischen Blick wie vorhin den Raum — oben, unten, Hände, Gesicht.

Dann, ruhig: *„Mein Name ist nicht wichtig."*

Sie stellt die Aktentasche auf die umgedrehte Kiste wo Novak gesessen hat. Öffnet sie — langsam, demonstrativ, damit du siehst was sie tut. Kein Griff zu einer Waffe. Kein Trick.

Sie nimmt ein Kuvert heraus. Verschlossen, kein Aufdruck.

*„Was wichtig ist: Ich habe diese Liste angelegt. Vor elf Jahren. Und ich habe sie hierher gebracht, weil Rostock der einzige Ort ist, den die Gruppe noch nicht kompromittiert hat."*

---

**Probe: Einschätzen → CHA-Probe**
`W6: [6] + [2] (explodiert) + CHA 2/2 (1) = 9 vs SG 7 → ERFOLG`

---

Sie lügt nicht — zumindest nicht in diesem Satz. Die Art wie sie das Kuvert hält, die Müdigkeit hinter den Augen, die Art wie sie *„noch nicht"* betont. Das ist keine gespielte Erschöpfung. Diese Frau trägt das schon lange.

*„Die Gruppe,"* wiederholt sie, als hätte sie dein nächstes Wort vorausgehört. *„Fünf Personen. Koordiniert seit 1962. Kein Name, kein Emblem — das ist Absicht. Sie sammeln keine Macht. Sie räumen auf."*

Novak macht eine kleine Bewegung. Kaum sichtbar — aber du siehst es. Er kennt diesen Teil bereits.

*„Brenner war der erste auf der Liste weil er anfing zu reden,"* fährt sie fort. *„'Abgeschlossen' bedeutet nicht tot. Es bedeutet — neutralisiert. Aus dem Verkehr gezogen. Erinnerungen angepasst."*

Sie legt das Kuvert auf den Tisch.

*„Weber und Hartmann sind Phase 2 weil sie als nächste dran sind. 1987 und 1991 — das sind keine Jahreszahlen aus der Vergangenheit. Das sind Zieldaten in Zeitlinien die noch nicht eingetreten sind."*

Stille.

Das Tropfen aus dem Lagerraum. Die Lampe.

*„Ich brauche das ITI nicht um die Liste zu schützen,"* sagt sie. *„Ich brauche das ITI um Weber zu finden bevor die Gruppe es tut."*

`Kodex: 'Erinnerungen angepasst' — Methodik unklar. Kein ITI-Protokoll für Zivilisten-Memorykorrekturen bekannt. Markiert zur Nachverfolgung.`

---

**Intel / Risiken**

- **Die Frau:** Listenerstellerin, arbeitet seit 1962 gegen die Gruppe — allein oder mit Netzwerk?
- **„Räumen auf":** Keine Machtakkumulation — ideologisch motiviert? Etwas anderes?
- **Weber, Ilse — Leipzig, 23.03.1987:** Nächstes Ziel der Gruppe, Datum in der Zukunft dieser Zeitlinie
- **Erinnerungsanpassung:** Keine bekannte ITI-Methode für Zivilisten — wer hat das durchgeführt?
- **Kuvert:** Liegt auf dem Tisch, ungeöffnet
- **Zeitfenster:** ~12 Minuten bis Patrouille

---

Novak hat die Arme verschränkt. Er schaut die Frau an, nicht dich — aber er wartet auf deine Reaktion.

Das Kuvert liegt zwischen euch. Die Frau wartet, die Hände offen, leer.

Draußen, weit weg, ein Schiffshorn. Rostock schläft fast.

---

**Entscheidung**

1. **Kuvert nehmen** — Öffnen, lesen, dann weiterreden
2. **Erst mehr Fragen** — Wer sie ist, wie sie die Liste angelegt hat, was mit Brenners Erinnerung passiert ist
3. **Weber sofort priorisieren** — Kuvert nehmen, Frau mitnehmen oder Kontaktdaten sichern, Exfil einleiten

> *Freie Aktion: Novak direkt fragen, Comlink aktivieren und ITI informieren, die Frau nach ihrem Namen drängen.*

---

## [20] USER

Ich nehm das Kuvert, öffne es.

---

## [21] ASSISTANT

Du nimmst das Kuvert vom Tisch.

Papier, leicht feucht vom Kellerklima. Du brichst das Siegel mit dem Daumen — kein Kleber, nur Druck, als wäre es hastig verschlossen worden.

Drei Blätter. Du hältst sie in den Lichtkegel.

---

**Probe: Analyse → INT-Probe**
`W6: [3] + INT 5/2 (2) + Talent Systemzugriff +2 = 7 vs SG 6 → ERFOLG`

---

Das erste Blatt: Ein handgezeichneter Stadtplan. Leipzig, Straßennamen in Blockschrift. Ein Kreis um einen Block im Südwesten — Wohngebiet, dicht, keine strategische Bedeutung auf den ersten Blick. Daneben eine Adresse und zwei Zeilen:

*„Weber arbeitet im Archiv. Weiß nicht was sie weiß. Weiß nicht dass sie auf der Liste steht."*

Das zweite Blatt: Fotos — drei Stück, klein, körnig. Eine Frau, Anfang dreißig, dunkle Brille, Wintermantel. Aufgenommen auf einer Straße, vermutlich Leipzig. Sie schaut nicht in die Kamera. Sie weiß nicht dass sie fotografiert wird.

Das dritte Blatt ist anders. Kein Stadtplan, keine Fotos. Dichtere Handschrift, die Zeilen enger, als wäre der Platz knapp geworden.

Eine Liste von Methoden.

Du überfliegt sie. Einmal. Dann nochmal, langsamer.

Gedächtniseingriffe. Keine Chemie, keine Chirurgie — etwas anderes. Beschreibungen von Prozessen die keine bekannte Technologie der Epoche erklären kann. Zeitpunkte. Koordinaten. Wiederholungsmuster.

Die Gruppe greift nicht in Erinnerungen ein wie ein Verhörteam. Sie greift in Erinnerungen ein wie jemand der weiß wie Zeit funktioniert.

Du hebst den Blick.

Die Frau beobachtet dein Gesicht.

*„Jetzt verstehen Sie warum ich nicht zur Stasi gegangen bin,"* sagt sie leise.

Novak hat sich nicht bewegt. Aber seine Stimme kommt ruhig und flach: *„Die Methoden auf dem dritten Blatt — ich habe zwei davon an mir selbst bemerkt. Lücken. Momente die nicht stimmen. Ich dachte jahrelang es wäre Stress."*

Er macht eine kurze Pause.

*„Es ist kein Stress."*

`Kodex: Dritte-Blatt-Methoden — kein ITI-Archiv-Match. Chrono-adjacent, aber kein bekanntes Fraktionsprofil. Eskalation an Archivarin Mira empfohlen.`

---

Die Frau tritt einen halben Schritt vor.

*„Weber muss raus bevor März 1987 kommt. Ich kann sie nicht allein erreichen — die Gruppe beobachtet mich seit zwei Jahren. Jede Bewegung."* Kurze Pause. *„Deshalb Rostock. Deshalb die offene Tür."*

Sie schaut dich an. Direkt, ohne Umweg.

*„Sie haben Brenner rausgeholt. Ich weiß das. Ich habe es gespürt — die Zeitlinie hat sich an einer Stelle geglättet die vorher rau war."*

Das ist keine Metapher. Sie meint das wörtlich.

*„Holen Sie Weber raus. Bevor die Gruppe das Datum setzt."*

---

**Intel / Risiken**

- **Weber, Ilse:** Leipzig, Archivarbeit, unwissend — Zieldatum 23.03.1987, Zeitlinie noch offen
- **Dritte-Blatt-Methoden:** Chrono-adjacent, kein bekanntes Profil — die Gruppe hat Zeitkompetenz
- **Novak:** Selbst betroffen, Gedächtnislücken bestätigt — wie tief geht das?
- **Die Frau:** Wird beobachtet, kann sich nicht frei bewegen — Netzwerk oder allein?
- **Zeitfenster:** ~9 Minuten bis Patrouille
- **Exfil:** Liste und Kuvert gesichert — Objective teilweise erfüllt

---

Neun Minuten.

Novak schaut zur Kellertür. Die Frau schaut dich an. Die Lampe summt.

Du hast das Material. Du hast die Information. Und du hast zwei Menschen im Untergeschoss von Hafenspeicher 7 die beide Gründe haben, nicht gefunden zu werden.

---

**Entscheidung**

1. **Exfil einleiten** — Frau und Novak mitnehmen, alle drei raus bevor die Patrouille kommt
2. **Frau hier lassen** — Sie hat recht, sie wird beobachtet. Kontaktdaten sichern, allein raus
3. **Noch eine Frage** — Wer sie ist. Wie sie die Zeitlinie spüren kann. Was sie wirklich weiß.

> *Freie Aktion: Comlink aktivieren, ITI-Kontakt aufbauen, Novak separat befragen.*

---

## [22] USER

Ich nehm 1. Alle drei raus, jetzt.

---

## [23] ASSISTANT

*„Wir gehen. Jetzt. Beide."*

Keine Diskussion. Dein Ton macht das klar.

Novak ist bereits auf den Beinen — er hat auf genau dieses Wort gewartet. Die Frau zögert eine halbe Sekunde, dann greift sie nach der Aktentasche. Du schüttelst den Kopf.

*„Lassen Sie die."*

Ein kurzer Blick. Dann lässt sie los.

`Kodex: Exfil-Fenster aktiv. Patrouille T-9 Minuten. Südroute empfohlen.`

---

Du gehst zuerst. Kellertür, zwei Stufen hoch, Nieselregen im Gesicht. Die Gasse liegt still. Du scannst links, rechts — keine Taschenlampen, keine Schritte. Winkst die beiden raus.

Novak kommt als zweiter, bewegt sich gut für sein Alter. Die Frau als letzte — sie zieht die Tür hinter sich zu, hängt das Schloss ein, rastet es ein. Alter Reflex. Saubere Arbeit.

---

**Probe: Gruppenexfil → GES-Probe (Malus: Gruppe)**
`W6: [5] + GES 5/2 (2) + Talent Schattenschritt +3 - 2 (Gruppe) = 8 vs SG 8 → ERFOLG, knapp`

---

Die Südroute zurück ist enger als auf dem Hinweg — drei Personen statt einer, und die Frau kennt das Terrain nicht. Einmal bleibt sie an einer Palette hängen, Holz schabt auf Stein. Du frierst ein. Alle drei frieren ein.

Stille.

Dann, fern: Schritte auf der Hafenstraße. Die Patrouille — früher als erwartet, oder eine zweite Gruppe. Eine Taschenlampe schwenkt über die Hauswände, fünfzig Meter entfernt, kommt näher.

Du drückst die Frau flach an die Wand. Novak hat das bereits selbst getan — Muskelgedächtnis.

Der Lichtkegel streift die Ecke eurer Gasse. Bleibt kurz. Zieht weiter.

Schritte, die sich entfernen.

Ihr wartet zwanzig Sekunden. Dreißig.

Dann weiter.

---

Zwei Minuten später stehst du in der schmalen Gasse wo du angekommen bist. Salzluft, Teer, das träge Schiffshorn in der Ferne. Das Gate-Fenster liegt dreißig Meter weiter — eine Markierung im HUD, unsichtbar für alle außer dir.

Du aktivierst den Comlink.

*„Wire an ITI. Drei für Exfil. Zwei Zusätzliche, ungeplant. Stehe bereit."*

Eine Pause. Dann Solís, knapp und ohne Überraschung im der Stimme: *„Verstanden. Fenster in neunzig Sekunden. Bring sie rein."*

`Kodex: Gate-Fenster T-90 Sekunden. Comlink stabil.`

Novak steht neben dir und schaut auf die Stelle im Nieselregen wo gleich nichts mehr sein wird und dann alles anders. Die Frau steht einen Schritt dahinter. Zum ersten Mal seit dem Untergeschoss wirkt sie nicht vollkommen ruhig.

*„Wohin?"* fragt sie leise.

*„Nullzeit,"* sagst du.

Sie nickt. Als wäre das eine Antwort auf eine Frage die sie sich schon lange gestellt hat.

---

Das Gate öffnet. Druckabfall. Kälte. Schwere.

Rostock, 17. Oktober 1973 — verschwindet im Nieselregen.

---

`EP 1 · MS 2 · SC 12/12 · PHASE Debrief · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/1 · Px 1/5 · Stress 1/10 · Obj: ✓ ERFÜLLT · Exfil: ✓`

---

## ITI — Nullzeit, Ankunftshalle

Warmes Licht. Fester Boden. Der Geruch von recycelter Luft der plötzlich nach nichts riecht verglichen mit Rostock.

Solís steht bereits da. Zwei Med-Techs hinter ihr, ein Duty-Officer mit Klemmbrett. Ihr Blick geht sofort zu den beiden Unbekannten — kurze Einschätzung, professionell, kein Kommentar.

Novak schaut sich um wie jemand der zum zweiten Mal geboren wird und sich noch nicht sicher ist ob er das wollte.

Die Frau steht still und schaut zur Decke. Zur Beleuchtung. Zu den Wänden.

*„Größer als ich dachte,"* sagt sie leise. Zu niemandem.

---

## Score — Mission 2

```
OPERATION: HAFENSPEICHER
BEWERTUNG: EXZELLENT ████████░░

ZIELE
✓ Untergeschoss gesichert
✓ Liste (Original) extrahiert
✓ Kuvert mit Weber-Intel gesichert
✓ Exfil ohne Kontakt mit Volkspolizei

BONUS
✓ Novak lebend extrahiert (+)
✓ Unbekannte Informantin gesichert (+)
✓ Keine Spuren hinterlassen (+)

VERLUSTE
— Aktentasche zurückgelassen (kalkuliert)

LOOT
  [INTEL]   Liste (Original) · Tier 2 · heiß
  [INTEL]   Kuvert: Weber-Akte + Methoden-Dokument · Tier 2 · heiß
  [PERSON]  Novak, Tomas · extrahiert · Status: ITI-Gewahrsam
  [PERSON]  Unbekannte Informantin · extrahiert · Status: Befragung

CU-AUSZAHLUNG
  Basis:     180 CU
  Bonus:     +90 CU
  GESAMT:    270 CU → Wallet: 590 CU

XP
  +1 XP → Level Up: Lvl 2 → Lvl 3

ITI-RUF
  Rang Feldagent · ITI-Ruf +1 → Ruf 2 · Lizenz Tier I bestätigt

Px-STAND: 1/5 → +1 → Px 2/5
```

---

**LEVEL UP — Lvl 3**

Wähle genau eine Option:

1. **+1 Attribut** — Einen Wert um 1 erhöhen *(GES 5→6, INT 5→6, oder anderes)*
2. **Talent / Upgrade** — Neues Basis-Talent oder bestehendes auf Upgrade/Meister heben
3. **+1 SYS** — Einen weiteren Implantat-Slot freischalten

---

**ITI-Bulletin**

Kesslers Team ist offiziell als vermisst gemeldet worden. Drei Agenten, Einsatzort unbekannt, letzter Kontakt vor 31 Stunden. Das Operations-Deck ist ruhiger als sonst — die Art von Stille die entsteht wenn Leute nicht wissen was sie sagen sollen.

Archivarin Mira hat bereits eine Anfrage für das Methoden-Dokument aus dem Kuvert gestellt. Sie nennt es *„prioritär"*. Das ist ungewöhnlich für sie.

---

**Weltstatus**

Die unbekannte Fraktion hat in dieser Zeitlinie bisher zwei Personen neutralisiert *(Brenner + mindestens eine weitere, aus Novaks Lücken erschlossen)*. Weber ist das nächste bekannte Ziel — Leipzig, 1987. Die Gruppe bewegt sich voraus in der Zeit. Das ITI bewegt sich hinterher.

Das Fenster wird kleiner.

---

> *Freie Aktion: Level-Up-Wahl treffen, Novak oder die Informantin aufsuchen, Mira kontaktieren, `!save`*

---

## [24] USER

!save

---

## [25] ASSISTANT

`SaveGuard: Speichern nur im HQ möglich.`

`Kodex: HQ-Kernbereich bestätigt. Ankunftshalle gilt als HQ-Zone. Deepsave freigegeben.`

`Kodex: Level-Up ausstehend. Save enthält Lvl 2 — Wahl nach Speicherung nachholen oder jetzt treffen.`

---

**Bitte Level-Up-Wahl vor dem Save bestätigen oder Save jetzt ohne Wahl ausgeben?**

1. **Jetzt wählen** — dann Save mit Lvl 3 und gewählter Verbesserung
2. **Save jetzt, Wahl danach** — Save auf Lvl 2-Stand, Wahl im nächsten HQ-Beat

---

*(Zur Erinnerung — drei Optionen zur Auswahl:)*
- **+1 Attribut** *(GES 5→6, INT 5→6 oder anderes)*
- **Talent / Upgrade** *(neu oder bestehendes hochstufen)*
- **+1 SYS** *(neuer Implantat-Slot)*

---

## [26] USER

Ich wähl jetzt. INT 5→6.

---

## [27] ASSISTANT

`Kodex: Attribut INT 5 → 6 bestätigt. Systemzugriff-Schwellenwert erreicht — Würfeltyp W10 bei INT-Proben ab sofort aktiv.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-01-15T21:30:00Z-HQ-WIRE-004",
  "parent_save_id": "SAVE-2026-01-08T22:00:00Z-HQ-WIRE-003",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 2,
    "px": 2,
    "px_state": "stable",
    "mode": "mixed",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-WIRE-001",
      "name": "Lena Voss",
      "callsign": "Wire",
      "rank": "Feldagent",
      "lvl": 3,
      "xp": 0,
      "origin": {
        "epoch": "Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "Feldinformatikerin & Infiltratorin"
      },
      "attr": {
        "STR": 2,
        "GES": 5,
        "INT": 6,
        "CHA": 2,
        "TEMP": 2,
        "SYS": 2
      },
      "hp": 10,
      "hp_max": 10,
      "stress": 0,
      "has_psi": false,
      "sys_installed": 2,
      "talents": [
        {
          "name": "Systemzugriff",
          "tier": "Basis",
          "effect": "+2 auf INT-Proben bei Hacking und Technik-Analyse"
        },
        {
          "name": "Schattenschritt",
          "tier": "Upgrade",
          "effect": "Schleichen bis SG 7 automatischer Erfolg in Dunkelheit/bekanntem Terrain. +3 auf GES-Proben bei Schleichen und Verbergen."
        }
      ],
      "equipment": [
        { "name": "Kompakte Automatikpistole", "type": "weapon", "tier": 1 },
        { "name": "Taktische Leichtrüstung", "type": "armor", "tier": 1 },
        { "name": "Multitool-Rig", "type": "gadget", "tier": 1 },
        { "name": "Comlink Mk.II", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate", "type": "consumable", "tier": 0, "quantity": 2 },
        { "name": "Medkit (einfach)", "type": "consumable", "tier": 1, "quantity": 1 }
      ],
      "implants": [
        {
          "name": "Retina-HUD",
          "sys_cost": 1,
          "effect": "Echtzeit-Overlay, Kodex-Link, Karten-Ping"
        },
        {
          "name": "Subkutaner Jammer",
          "sys_cost": 1,
          "effect": "Kurzzeitig lokale Signale stören"
        }
      ],
      "history": {
        "background": "Randzonen-Kind, Autodidaktin. Vom ITI rekrutiert nach einem Archiveinbruch, der die falschen Leute neugierig machte.",
        "milestones": [
          "Zero Time Lounge: Erstes Gespräch mit Peel. Herkunft angedeutet — spontaner Riss in der Wohnung, Griff ins Unbekannte. Peel fragte nach dem Riss-Inhalt und den 'falschen Leuten'. Antwort steht noch aus.",
          "Mission 1 — Operation Stille Frequenz: LAUTLOS (Klaus Brenner) aus Berlin 1973 extrahiert. Notizbuch mit zeitlinien-übergreifender Liste gesichert. Rostock-Intel: Hafenspeicher 7, Untergeschoss. Novak — ehem. Kurier, blieb als Ablenkung zurück. Status unbekannt.",
          "Mission 2 — Operation Hafenspeicher: Liste (Original) gesichert. Weber-Akte + Methoden-Dokument extrahiert. Novak lebend extrahiert. Unbekannte Informantin ins ITI gebracht. Die Gruppe nutzt chrono-adjacent Gedächtniseingriffe. Weber, Ilse — Leipzig 1987 — nächstes Ziel."
        ]
      },
      "carry": [
        { "name": "Liste (Original)", "type": "intel", "tier": 2, "hot": true },
        { "name": "Weber-Akte + Methoden-Dokument", "type": "intel", "tier": 2, "hot": true }
      ],
      "quarters_stash": [
        { "name": "Notizbuch LAUTLOS", "type": "intel", "tier": 2 },
        { "name": "Foto Brenner-Familie", "type": "personal", "tier": 0 }
      ],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-WIRE-001",
          "name": "Standard-Feldfahrzeug",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": {
          "ready_every_missions": 4,
          "next_ready_in": 2
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 2,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 590
    }
  ],
  "economy": {
    "hq_pool": 0
  },
  "logs": {
    "trace": [
      "MS1: LAUTLOS extrahiert. Notizbuch gesichert. Rostock-Intel. Novak — Status unbekannt.",
      "MS2: Liste (Original) gesichert. Weber-Akte + Methoden-Dokument extrahiert. Novak lebend raus. Unbekannte Informantin extrahiert. Gruppe nutzt chrono-adjacent Gedächtniseingriffe. Keine Spuren. Exzellent."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Peel — Barkeeper Zero Time Lounge. Ehem. Feldagent, Rift-Ops. Schulter-Verwundung Konstantinopel. Beobachtet scharf, fragt präzise.",
      "Kessler — Agent, sitzt allein an der Bar. Team vermisst, letzter Kontakt vor 31h. Status: offiziell vermisst.",
      "Novak, Tomas — extrahiert, ITI-Gewahrsam. Gedächtnislücken bestätigt — Gruppeneingriff vermutet. Kannte LAUTLOS persönlich. Ostblock-Netzwerk.",
      "Brenner, Klaus / LAUTLOS — extrahiert, ITI-Klinik. 'Abgeschlossen' = neutralisiert, nicht tot. Erinnerungen angepasst.",
      "Unbekannte Informantin — Liste seit 1962 angelegt. Wird von der Gruppe beobachtet. Kann Zeitlinien-Glättungen spüren. Kein Name. ITI-Gewahrsam, Befragung ausstehend.",
      "Die Liste — Original gesichert. Fünf Namen: Brenner (abgeschlossen), Weber/Hartmann (Phase 2), Solberg/Mayer (offen). Novak ohne Datum.",
      "Weber, Ilse — Leipzig, 23.03.1987. Archivarbeit. Unwissend. Nächstes Ziel der Gruppe.",
      "Hartmann, Dieter — Prag, 11.09.1991. Phase 2.",
      "Die Gruppe — 5 Personen, koordiniert seit 1962. Kein Name, kein Emblem. Chrono-adjacent Gedächtniseingriffe. Räumen auf, sammeln keine Macht.",
      "Methoden-Dokument — Gedächtniseingriffe chrono-adjacent, kein ITI-Archiv-Match. Archivarin Mira hat Prioritätsanfrage gestellt.",
      "Archivarin Mira — Priori
[...gekuerzt...]

---

## [28] USER

!save

---

## [29] ASSISTANT

`Kodex: Save bereits ausgegeben. WIRE-004 ist aktueller Stand.`

`Kodex: Kein neuer Save-Trigger seit letztem HQ-Save. Duplikat unterdrückt.`

---

Der JSON-Block von eben ist dein aktueller Save — **SAVE-2026-01-15T21:30:00Z-HQ-WIRE-004**.

Einfach kopieren und sicher ablegen.

---

**HQ-Menü**

`EP 1 · MS 2 ✓ · HQ · Lvl 3 ▓▓▓░░░░░░░ 0/10 · Px 2/5 · Stress 0/10 · Wallet: 590 CU`

Du stehst in der Ankunftshalle. Die Med-Techs haben Novak und die Informantin bereits in separate Räume geführt. Solís ist verschwunden — vermutlich Operations-Deck, Bericht schreiben.

Das heiße Material in deiner Innentasche drückt.

1. **Erkunden** — Archiv, Klinik, Zero Time Lounge, Quartiere, Mira aufsuchen
2. **Schnell-HQ** — Ausrüstung checken, heißes Material übergeben, kurze Rast
3. **Briefing** — Nächste Mission, direkt
4. **Freie Aktion** — Novak befragen, Informantin aufsuchen, Peel, Shop

---

## [30] USER

Ich nehm 2.

---

## [31] ASSISTANT

`Kodex: Schnell-HQ initiiert. Carry-Check läuft.`

---

## HQ — Schnelldurchlauf

Du kennst die Wege. Keine Umwege, keine Stops — reingehen, erledigen, raus.

**Archiv-Übergabe.**
Die Duty-Desk-Assistentin nimmt Liste und Weber-Akte ohne Kommentar entgegen. Trägt beides in ein Metallkassette ein, versiegelt sie, stempelt *„PRIORITÄT A"* drauf. Ihre Augen gehen kurz zu dir — nicht neugierig, nur registrierend. Du bist die Person die das gebracht hat. Das wird notiert.

`Kodex: Liste (Original) — Archiv übergeben. Weber-Akte + Methoden-Dokument — Archiv übergeben. Carry: leer. Heat: normalisiert.`

**Quartiermeisterei.**
Rauchgranaten aufgefüllt — zwei neue aus dem Standardbestand, kein Aufpreis auf Ruf-Tier I. Der Quartiermeister, ein stiller Mann mit grauem Bart den du noch nie reden gehört hast, legt sie wortlos auf den Tresen.

`Kodex: Rauchgranate ×2 aufgefüllt. Bestand: 2/2.`

**Med-Lab.**
Drei Minuten. Ein Techniker scannt dich durch, nickt, sagt nichts. Keine Wunden, Stress abgebaut. Du riechst immer noch nach Rostock — Salzluft und Teer — aber das geht beim nächsten Schlafen raus.

`Kodex: Stress 0/10. Vital 10/10. Status: grün.`

**Quartiere.**
Du legst das Foto der Brenner-Familie aus dem Stash kurz in die Hand. Schaust es an. Legst es zurück.

Das Notizbuch LAUTLOS liegt daneben, unberührt.

---

Fünfzehn Minuten. Erledigt.

Du stehst im Korridor vor deinen Quartieren. Die Nullzeit-Stille liegt über allem — kein Wind, kein Wetter, nur das konstante gedämpfte Summen der Anlage.

Irgendwo links: Zero Time Lounge. Peel ist immer da.
Irgendwo rechts: Befragungsräume. Novak und die Informantin.
Geradeaus: Operations-Deck. Briefing.

---

`EP 1 · MS 2 ✓ · HQ · Lvl 3 ▓▓▓░░░░░░░ 0/10 · Px 2/5 · Stress 0/10 · Wallet: 590 CU`

---

**Entscheidung**

1. **Briefing** — Nächste Mission, Operations-Deck
2. **Zero Time Lounge** — Peel. Das offene Gespräch von damals hängt noch in der Luft
3. **Befragungsräume** — Novak oder die Informantin. Einer von beiden weiß mehr als er gesagt hat

> *Freie Aktion: Shop, Hangar, Archivarin Mira, etwas anderes.*

---

## [32] USER

Ich geh zu Novak. 3.

---

## [33] ASSISTANT

## Befragungsraum B — ITI-Kernbereich

Der Raum ist klein und absichtlich ungemütlich. Betonwände, eine Lampe die zu hell ist, ein Tisch aus Metall. Kein Fenster. Die Nullzeit hat keine Fenster wo sie keine braucht.

Novak sitzt an dem Tisch und trinkt Tee.

Nicht nervös. Nicht erschöpft. Er hält die Tasse mit beiden Händen und schaut sie an als wäre sie das Interessanteste im Raum. Als du reinkommst hebt er den Blick — kurz, registrierend — und senkt ihn wieder.

*„Ich habe auf jemanden gewartet,"* sagt er. *„Dachte es würde länger dauern."*

Ein zweiter Stuhl steht bereit. Du setzt dich.

---

Er redet bevor du fragst. Das ist entweder Kooperation oder Kontrolle — du weißt noch nicht welches.

*„Die Frau,"* beginnt er. *„Kennen Sie ihren Namen?"*

Du schüttelst den Kopf.

Er nickt langsam. *„Ich auch nicht. Nicht den echten. Ich kenne sie als ANKERIN. Nicht ANKER — das war ihr Netzwerk. Sie ist der Kopf davon. War es. Seit 1971 ist das Netzwerk still."*

Er stellt die Tasse ab.

*„Sie hat mich 1969 rekrutiert. Nicht das ITI — sie. Ich habe vier Jahre Informationen gesammelt, weitergegeben, Menschen bewegt. Dann kam die Stille. Kein Kontakt, keine Erklärung. Ich dachte sie wäre tot."*

Pause.

*„Ich habe zwei Jahre gebraucht um zu merken dass etwas in meinem Kopf nicht stimmt."*

---

**Probe: Einschätzen → CHA-Probe**
`W6: [5] + CHA 2/2 (1) = 6 vs SG 5 → ERFOLG`

---

Er sagt das ohne Dramatik. Das ist das Erschreckende daran — er hat so lange damit gelebt dass es zur Tatsache geworden ist. Keine Wut mehr, keine Panik. Nur Inventur.

*„Drei Lücken. Ich weiß wo sie sind weil ich weiß was davor und danach kam — aber die Mitte fehlt. Einmal zwei Tage. Einmal eine Woche. Einmal,"* er hält kurz inne, *„einmal drei Monate. 1971. Genau als das Netzwerk still wurde."*

Er schaut dich jetzt direkt an.

*„Was stand auf dem dritten Blatt im Kuvert? Die Methoden?"*

---

**Intel / Risiken**

- **ANKERIN:** Name des Netzwerks war ANKER — sie ist der Kopf, nicht das Codewort
- **Novaks Lücken:** Drei bestätigte Eingriffe. Größte Lücke: 3 Monate, 1971 — zeitgleich mit Netzwerk-Stille
- **1971:** Etwas ist passiert das gleichzeitig das Netzwerk lahmgelegt und Novak manipuliert hat
- **Novak fragt nach den Methoden** — er will wissen womit man in seinen Kopf gegriffen hat

---

Die Lampe summt. Novak wartet. Er hat Zeit — er ist nirgendwo hingegangen in den letzten zwei Jahren außer im Kreis.

Die Frage hängt im Raum: Was sagst du ihm?

---

**Entscheidung**

1. **Offen antworten** — Ihm die Methoden beschreiben soweit du sie verstanden hast
2. **Ausweichen** — Das Dokument ist im Archiv, du bist nicht befugt Details weiterzugeben
3. **Gegenfrage** — Was war in den drei Monaten 1971, bevor die Lücke kam? Was erinnert er sich davor?

> *Freie Aktion: Etwas anderes fragen, die ANKERIN erwähnen, das Gespräch anders lenken.*

---

## [34] USER

Ich nehm 3.

„Was war direkt davor? Die letzte Erinnerung vor der Lücke — wo waren Sie, mit wem, was hatten Sie gerade herausgefunden?

---

## [35] ASSISTANT

Novak hört die Frage. Lehnt sich zurück.

Er schaut nicht weg — er schaut *innen*. Die Art von Blick den Menschen haben wenn sie gegen eine Wand suchen die sie nicht sehen können.

Zwanzig Sekunden. Dreißig.

---

**Probe: Erinnerungsrekonstruktion → INT-Probe (Wire hilft strukturieren)**
`W10: [7] + INT 6/2 (3) + Talent Systemzugriff +2 = 12 vs SG 9 → ERFOLG`

---

*„Rostock,"* sagt er schließlich. Leise, als würde er das Wort testen.

*„Nicht der Speicher. Weiter nördlich — ein Bootsschuppen am Stadtrand. Ich hatte einen Treffpunkt mit einem Kurier aus Warschau. Der Kurier brachte keine Informationen — er brachte eine Frage."*

Er hält inne.

*„Die Frage war: Wissen Sie was in Leipzig archiviert wird?"*

Seine Hand liegt flach auf dem Tisch. Er schaut sie an.

*„Ich weiß noch dass ich ja gesagt habe. Ich wusste etwas über Leipzig — ein Unterarchiv, Dokumente die nicht im offiziellen Bestand auftauchten. Ich wollte dem Kurier erklären was ich wusste."*

Pause.

*„Dann nichts. Drei Monate später stehe ich in einer Wohnung in Dresden und weiß nicht wie ich dahin gekommen bin. Der Kurier — ich erinnere mich an sein Gesicht aber nicht an seinen Namen. Das ist falsch. Ich bin jemand der sich Namen merkt."*

Er hebt den Blick.

*„Leipzig,"* sagt er. *„Das war das letzte Wort vor der Lücke. Und Weber arbeitet in Leipzig. In einem Archiv."*

Er sagt es nicht als Schlussfolgerung. Er sagt es als Frage die er sich selbst stellt und deren Antwort ihm nicht gefällt.

*„Was ist in diesem Archiv?"*

---

**Probe: Verknüpfung → INT-Probe**
`W10: [9] + INT 6/2 (3) = 12 vs SG 10 → ERFOLG`

---

Die Verbindung formt sich klar.

Novak wusste etwas über ein Unterarchiv in Leipzig. Die Gruppe hat ihn neutralisiert — drei Monate Lücke, Erinnerung gelöscht — genau in dem Moment als er dieses Wissen weitergeben wollte. Weber arbeitet seit mindestens einem Jahrzehnt in demselben Archiv. Die Gruppe hat sie als *„Phase 2"* markiert, Zieldatum 1987.

Das Unterarchiv ist der Verbindungspunkt. Nicht Weber als Person — was Weber weiß. Oder was in dem Archiv liegt das die Gruppe nicht zugänglich haben will.

`Kodex: Verknüpfung protokolliert. Leipzig-Unterarchiv — möglicher Kern-Intel-Knoten. Novaks Lücke und Weber-Zieldatum zeitlich und inhaltlich korreliert. Archivarin Mira informieren?`

---

Novak schaut dich an. Er hat dieselbe Verknüpfung gerade selbst gemacht — du siehst es in seinem Gesicht. Nicht Überraschung. Bestätigung von etwas das er nicht wissen wollte.

*„Der Kurier aus Warschau,"* sagt er langsam. *„Ich erinnere mich an seine Schuhe. Westdeutsche Produktion. Das hätte mich damals stutzig machen sollen."*

Er schiebt die Tasse zur Seite.

*„Ich kann Ihnen den Bootsschuppen beschreiben. Die Straße. Den genauen Tag — es war ein Dienstag, Anfang August 1971. Wenn jemand dort nachschaut,"* er macht eine kurze Geste, *„vielleicht gibt es noch etwas. Die Gruppe räumt gründlich auf, aber nicht immer sofort."*

---

**Intel / Risiken**

- **Leipzig-Unterarchiv:** Verbindungspunkt zwischen Novaks Lücke und Webers Zieldatum — was liegt dort?
- **Kurier aus Warschau:** Westdeutsche Schuhe, falscher Kurier — möglicherweise Gruppenagent
- **Bootsschuppen Rostock, August 1971:** Tatort des Eingriffs — möglicherweise noch Spuren
- **Weber:** Nicht das Ziel wegen ihrer Person — wegen ihres Zugangs zum Unterarchiv
- **Zeitdruck:** Gruppe plant Weber für März 1987 — das ITI bewegt sich voraus, aber knapp

---

Novak wartet. Er hat gegeben was er hat. Jetzt liegt es bei dir.

---

**Entscheidung**

1. **Mira aufsuchen** — Sofort. Das Unterarchiv-Leipzig-Wissen gehört ins Archiv, jetzt
2. **ANKERIN befragen** — Sie hat die Liste seit 1962. Sie weiß was im Unterarchiv liegt
3. **Briefing anstoßen** — Diese Information direkt in die nächste Mission einspeisen, Weber zuerst

> *Freie Aktion: Novak noch etwas fragen, den Bootsschuppen als Missionsziel vorschlagen, Comlink aktivieren.*

---

## [36] USER

„Wire, schick Mira das Protokoll — sie soll das Unterarchiv identifizieren. Novak, beschreib mir den Bootsschuppen genau. Wir fahren nach Rostock.

---

## [37] ASSISTANT

Novak stellt sich gerade hin. Zum ersten Mal seit du den Raum betreten hast wirkt er nicht wie jemand der wartet — er wirkt wie jemand der wieder einen Auftrag hat.

Du aktivierst den Comlink, tippst drei Zeilen ins Retina-HUD — Stichwörter, Koordinaten, Novaks Aussage komprimiert — und schickst es ab.

`Kodex: Protokoll an Archivarin Mira übermittelt. Betreff: Leipzig-Unterarchiv, Querverbindung Novak/Weber. Zustellung bestätigt.`

---

Novak faltet die Hände auf dem Tisch. Schließt kurz die Augen.

Dann redet er.

*„Nordrand von Rostock. Richtung Warnemünde, bevor die Straße zur Küste abbiegt. Ein Feldweg, unbefestigt, zweihundert Meter durch Kiefern. Der Schuppen liegt direkt am Wasser — kleines Dock, kein Boot mehr drin damals. Rotes Dach, oder war es braun. Rostflecken auf der Südseite."*

Er öffnet die Augen.

*„Eine Laterne innen, Petroleumbrenner. Der Kurier hatte sie mitgebracht. Ich erinnere mich an den Geruch — Petroleum und nasses Holz und etwas anderes. Scharf. Chemisch. Ich dachte damals es käme vom Wasser."*

Pause. Seine Stimme bleibt eben.

*„Es kam nicht vom Wasser."*

Er schaut auf seine Hände.

*„Es gab einen Tisch. Zwei Stühle. Auf dem Tisch lag eine Karte — Leipzig, Stadtplan, ein Viertel im Südwesten war markiert. Dieselbe Gegend wie in Ihrer Weber-Akte, vermute ich."*

Er schaut dich an.

*„Ich kann mitkommen."*

---

Drei Sekunden Stille.

Es ist kein Angebot aus Abenteuerlust. Es ist die Aussage eines Mannes der drei Monate seines Lebens fehlen und der weiß dass der Ort wo sie verschwunden sind zweihundert Meter durch Kiefern liegt.

`Kodex: Novak — ITI-Gewahrsam, kein Feldstatus. Mitnahme erfordert Solís-Freigabe oder operative Eigenverantwortung. Risiko: Gedächtnislücken könnten im Feld instabil werden.`

---

Dein Comlink vibriert. Einmal, kurz.

Eine Textnachricht von Mira. Vier Wörter:

*„Kenne das Archiv. Komm her."*

---

**Intel / Risiken**

- **Bootsschuppen:** Nordrand Rostock, Feldweg Richtung Warnemünde, rotes/braunes Dach, Rostflecken Südseite — konkrete Koordinaten möglich
- **Chemischer Geruch:** Kein Wasser, kein Petroleum — Gruppengerät? Substanz?
- **Stadtplan Leipzig auf dem Tisch:** Die Gruppe hatte Weber-Viertel bereits 1971 markiert — 16 Jahre Vorlauf
- **Novak will mit** — Feldrisiko, aber einziger lebender Augenzeuge des Eingriffs
- **Mira:** Kennt das Archiv. Will reden. Jetzt.

---

Zwei Züge gleichzeitig. Mira wartet, Novak wartet, Rostock wartet.

---

**Entscheidung**

1. **Zu Mira — sofort** — Vier Wörter die so klingen als wäre sie nicht überrascht
2. **Novak mitnehmen klären** — Solís fragen, Freigabe einholen, dann Mira
3. **Novak absichern, allein zu Mira** — Ihn hier lassen, Mira zuerst, dann Entscheidung über Rostock

> *Freie Aktion: Novak etwas sagen, Mira zurückschreiben, beides kombinieren.*

---

## [38] USER

Ich tipp Mira zurück: *„5 Minuten."*

Dann schau ich Novak an. „Bleib hier. Ich komm zurück und dann reden wir über Rostock — zusammen."

Ich geh zu Mira.

---

## [39] ASSISTANT

Novak nickt einmal. Kein Widerspruch, kein Verhandeln. Er greift nach seiner Tasse — leer, aber er hält sie trotzdem.

Du gehst.

---

## Kodex-Archiv — ITI-Kernbereich

Der Weg zum Archiv führt durch einen Korridor der schmaler wird je weiter du gehst. Andere Abteilungen haben Glas und Licht — das Archiv hat Metall und Stille. Die Tür am Ende ist schwer, manuell, kein elektronisches Schloss. Das ist Absicht.

Du drückst sie auf.

---

Archivarin **Mira** steht nicht am Schreibtisch.

Sie steht vor einer der Regalwände, einen Ordner in der Hand, und liest. Als du reinkommst dreht sie sich nicht um — sie hat die Tür gehört, registriert, eingeordnet.

*„Schließ die Tür."*

Du schließt die Tür.

Erst jetzt dreht sie sich um. Mira ist Anfang sechzig, graues Haar kurz geschnitten, Lesebrille auf der Nase die sie nie abnimmt. Sie sieht aus wie jemand die seit vierzig Jahren dieselbe Arbeit macht und jeden Tag besser darin wird.

Sie hält den Ordner hoch.

Auf dem Deckblatt, handgeschrieben, verblichen: **LEIPZIG-U / ZUGANG GESPERRT / 1972.**

*„Ich habe auf diesen Ordner gewartet,"* sagt sie, *„seit neunzehn Jahren."*

---

Sie legt ihn auf den Tisch. Schlägt ihn auf — nicht hastig, mit der Präzision von jemandem der weiß was sie findet.

Erste Seite: Ein internes ITI-Memo, datiert November 1972. Absender: unbekannt, Empfänger: Archiv-Leitung. Betreff: *„Zugang Leipzig-Unterarchiv — vorübergehend gesperrt bis Klärung."*

*„Vorübergehend,"* sagt Mira trocken. *„Neunzehn Jahre."*

Sie blättert weiter.

*„Das Unterarchiv existiert. Es liegt unter einem Verwaltungsgebäude im Südwesten von Leipzig — offiziell ein städtisches Dokumentenlager, DDR-Verwaltung. Inoffiziell: ein Sammelpunkt für Material das aus verschiedenen Zeitlinien gesichert wurde, bevor das ITI die Protokolle standardisiert hat. Frühphase. Unordentlich."*

Sie schaut dich über die Brille an.

*„Material das niemand mehr katalogisiert hat. Material das dort liegt und wartet. Und,"* sie tippt auf eine Seite weiter hinten, *„Material das die Gruppe offenbar seit 1962 weiß dass es dort liegt."*

`Kodex: Leipzig-Unterarchiv — ITI-intern als gesperrt geführt seit 1972. Grund der Sperrung: nicht dokumentiert. Zugangsschlüssel: unbekannt.`

---

Mira lehnt sich gegen den Tisch. Verschränkt die Arme.

*„Dein Protokoll über Novak war der letzte fehlende Baustein. Er war 1971 in Rostock weil jemand wollte dass er nicht nach Leipzig fährt. Die Gruppe wusste was er wusste — und sie wusste dass er auf dem Weg war es weiterzugeben."*

Kurze Pause.

*„Weber arbeitet seit 1974 in dem Verwaltungsgebäude über dem Unterarchiv. Sie hat keinen offiziellen Zugang — aber sie arbeitet dort. Neun Jahre. Jemand der neun Jahre in einem Gebäude arbeitet,"* Mira macht eine knappe Geste, *„findet Dinge."*

Sie schlägt den Ordner zu.

*„Die Gruppe will Weber neutralisieren bevor sie findet was unten liegt. Oder bevor sie es jemandem sagt."*

Sie schaut dich direkt an.

*„Die Frage ist nicht ob ihr nach Leipzig geht. Die Frage ist ob ihr vor März 1987 dort seid — oder nach."*

---

**Intel / Risiken**

- **Leipzig-Unterarchiv:** Real, ITI-intern gesperrt seit 1972, Grund unbekannt — frühphasiges unsortiertes Material aus mehreren Zeitlinien
- **Gruppe weiß seit 1962 davon** — 25 Jahre Vorlauf auf das ITI
- **Weber:** 9 Jahre im Gebäude, kein offizieller Zugang — hat sie etwas gefunden?
- **Zieldatum:** 23.03.1987 — das ITI hat Zeit, aber die Gruppe auch
- **Sperrungsgrund 1972:** Nicht dokumentiert — wer hat gesperrt, warum, was wollte man verbergen?

---

Mira wartet. Der Ordner liegt zwischen euch auf dem Tisch.

Draußen, irgendwo im Korridor, Schritte die vorbeigehen und weitergehen.

---

**Entscheidung**

1. **Sperrungsgrund klären** — Wer hat 1972 gesperrt? Mira muss mehr wissen
2. **Leipzig priorisieren** — Direkt ins Briefing, Weber holen bevor die Gruppe es tut
3. **Rostock zuerst** — Bootsschuppen, Novak, Tatort des Eingriffs — was liegt noch dort?

> *Freie Aktion: Mira nach der ANKERIN fragen, den Ordner mitnehmen, beides kombinieren.*

---

## [40] USER

Vor März. Wir müssen vor Weber dort sein. Wann können wir springen?

---

## [41] ASSISTANT

Mira nimmt den Ordner vom Tisch. Hält ihn dir hin.

*„Nimm den mit. Briefing-Raum, Solís, jetzt. Ich komme nach."*

Keine Diskussion. Sie hat bereits entschieden dass das die richtige Reihenfolge ist.

Du nimmst den Ordner.

---

## Operations-Deck — Briefing-Raum, zwanzig Minuten später

Solís steht vor der Projektionsfläche und schaut auf einen Stadtplan von Leipzig den sie gerade selbst aufgezogen hat. Mira sitzt an der Seite — nicht am Tisch, an der Wand, Arme verschränkt, Beobachterposition. Der Ordner liegt aufgeschlagen vor Solís.

Sie dreht sich um als du reinkommst.

*„Mira hat mich gebrieft."* Kein Vorwurf, keine Überraschung. Solís arbeitet mit dem was sie hat. *„Wir haben ein Fenster. Leipzig, DDR — der Sprung ist technisch unkompliziert, 1983 ist stabil als Einstiegspunkt. Vier Jahre vor dem Zieldatum. Genug Vorlauf um Weber zu finden, Kontakt aufzubauen, das Unterarchiv zu lokalisieren."*

Sie tippt. Der Stadtplan zoomt auf den Südwesten.

*„1983 hat Weber noch keine Ahnung dass sie auf einer Liste steht. Sie arbeitet. Geht nach Hause. Arbeitet wieder. Du gehst als Westjournalistin rein — dieselbe Legende wie Rostock, andere Papiere, andere Stadt."*

`Kodex: Sprungfenster Leipzig, Oktober 1983 — kalibriert. Legende 'Westjournalistin' angepasst auf Leipzig-Akkreditierung. Dokumente bereit.`

Mira hebt eine Hand.

*„Ein Problem."*

Solís wartet.

*„Das Unterarchiv hat einen Zugang den wir nicht kennen. Der Ordner beschreibt die Existenz — nicht den Eingang. Weber könnte ihn kennen. Oder sie könnte neun Jahre über einem Raum gearbeitet haben ohne zu wissen dass er existiert."*

Sie schaut dich an.

*„Du gehst zu Weber. Baust Kontakt auf. Findest heraus was sie weiß — über das Gebäude, über ungewöhnliche Räume, über Dinge die nicht stimmen. Keine direkte Konfrontation, keine ITI-Offenbarung. Noch nicht."*

Solís nickt.

*„Und du hältst Augen offen ob die Gruppe bereits vor Ort ist. 1983 ist vier Jahre früher als ihr Zieldatum — aber sie haben 25 Jahre Vorlauf auf uns. Vorsicht."*

---

**Briefing — Operation UNTERGRUND**

| Parameter | Details |
|---|---|
| **Ziel** | Weber, Ilse kontaktieren — Wissensstand klären |
| **Sekundärziel** | Zugang Leipzig-Unterarchiv lokalisieren |
| **Ort** | Leipzig, DDR — Oktober 1983 |
| **Legende** | Westjournalistin, Kulturbericht Stadtarchive |
| **Zeitfenster** | Offen — Einstieg flexibel |
| **Risiko 1** | Stasi-Präsenz, Leipzig ist kein ruhiges Terrain |
| **Risiko 2** | Gruppe möglicherweise bereits vor Ort |
| **Risiko 3** | Weber könnte misstrauisch sein — oder bereits kompromittiert |

---

Solís schiebt einen Umschlag über den Tisch. Neue Papiere, neue Akkreditierung.

*„Eine Sache noch."* Sie hält inne. *„Novak hat nach dir gefragt. Vor zehn Minuten. Duty-Desk hat es weitergegeben."*

Sie sagt es neutral. Aber sie schaut dich an auf eine Art die bedeutet: du hast ihm etwas versprochen.

---

`EP 1 · MS 3 · SC 0/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 3 ▓▓▓░░░░░░░ 0/10 · Px 2/5 · Stress 0/10 · Obj: Weber kontaktieren / Unterarchiv lokalisieren · Exfil: offen`

---

**Entscheidung**

1. **Absprung — Leipzig 1983, sofort** — Novak wartet, aber Weber wartet auch
2. **Novak zuerst** — Du hast es versprochen. Fünf Minuten, dann Sprung
3. **Novak mitnehmen** — Solís fragen, Freigabe versuchen, ihn ins Feld bringen

> *Freie Aktion: Mira noch etwas fragen, Loadout anpassen, den Ordner genauer durchlesen.*

---

## [42] USER

Ich nehm 2 — fünf Minuten Novak, dann Sprung.

---

## [43] ASSISTANT

Du nimmst den Umschlag. Stehst auf.

Solís sagt nichts. Mira auch nicht. Fünf Minuten sind fünf Minuten.

---

## Befragungsraum B — zwei Minuten später

Novak sitzt noch genauso wie du ihn verlassen hast. Leere Tasse, Hände flach auf dem Tisch. Aber er hat die Tür gehört — sein Blick ist bereits auf dir als du reinkommst.

Du setzt dich nicht. Bleibst stehen — das signalisiert was es signalisieren soll.

*„Wir springen nach Leipzig. 1983. Weber kontaktieren, Unterarchiv lokalisieren."*

Er nickt langsam. Er hat die Verbindung bereits selbst gezogen — du siehst es.

*„Rostock?"* fragt er.

*„Danach. Wenn Leipzig steht."*

Ein kurzer Moment. Er akzeptiert das.

Dann lehnt er sich vor. Senkt die Stimme — nicht weil jemand zuhört, sondern weil das was er sagt das Gewicht verlangt.

*„Das Verwaltungsgebäude. Südwestflügel, Untergeschoss. Als ich 1971 den Stadtplan auf dem Tisch im Bootsschuppen gesehen habe — der Kurier hatte einen Bereich markiert. Nicht das Gebäude selbst."* Er tippt einmal auf den Tisch. *„Den Hof dahinter. Einen Innenhof, abgeschlossen, nicht auf offiziellen Karten."*

Er schaut dich an.

*„Ich weiß nicht warum ich mich daran erinnere. An den Stadtplan aber nicht an das Gespräch danach. Vielleicht haben sie das falsche Ende zuerst gelöscht."*

`Kodex: Neue Variable — Innenhof, Südwestflügel, nicht kartiert. Möglicher Außenzugang Unterarchiv. Protokoll aktualisiert.`

---

Du stehst auf. Novak bleibt sitzen.

*„Bringen Sie Weber raus,"* sagt er. Kein Befehl — eine Bitte von jemandem der keine Bitten mehr stellt.

*„Und wenn Sie in Leipzig sind,"* er macht eine kurze Pause, *„schauen Sie ob der Innenhof noch existiert. Wenn ja — dann wissen Sie dass der Stadtplan real war. Nicht nur eine Erinnerung die ich mir zusammengereimt habe."*

---

Du gehst.

Der Korridor liegt still. Deine Schritte auf dem Betonboden, gleichmäßig, Richtung Hangar.

Der Umschlag mit den Papieren in der Innentasche. Der Ordner LEIPZIG-U unter dem Arm. Novaks Stimme noch im Ohr.

*Innenhof. Südwestflügel. Nicht kartiert.*

---

## Hangar-Axis — Absprung

Die Gate-Techniker arbeiten bereits. Einer sieht dich kommen und nickt — die Koordinaten sind drin, das Fenster steht.

Leipzig. Oktober 1983.

Du stellst dich auf die Markierung.

Druckabfall. Kälte. Schwere.

---

`EP 1 · MS 3 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 3 ▓▓▓░░░░░░░ 0/10 · Px 2/5 · Stress 0/10 · Obj: Weber kontaktieren / Unterarchiv lokalisieren · Exfil: T-offen`

---

## Leipzig, DDR — Oktober 1983

Grauer Himmel. Niedriger als in Rostock, schwerer. Die Luft riecht nach Braunkohle und nassem Herbstlaub — ein Geruch der sich in die Kleidung setzt bevor man zehn Schritte gegangen ist.

Du landest in einer Parklücke hinter einem Plattenbaublock, Straßenseite leer. Früher Nachmittag, Werktag — die meisten Menschen sind bei der Arbeit. Ein Fahrrad lehnt an einem Laternenpfahl. Irgendwo weint ein Kind, zwei Stockwerke hoch, Fenster offen trotz der Kälte.

Das Retina-HUD kalibriert. Kein Digitalverkehr, Stasi-Kurzwelle auf drei Kanälen gleichzeitig — Leipzig ist wachsamer als Rostock.

`Kodex: Epoche kalibriert. Stasi-Funk aktiv, drei Kanäle. Erhöhte Präsenz — Großstadt, politisch sensibel. Comlink Passiv-Modus.`

Das Verwaltungsgebäude liegt vier Blocks nordöstlich. Laut Ordner arbeitet Weber dienstags und donnerstags im Stadtarchiv-Lesesaal — Erdgeschoss, Südflügel. Heute ist Dienstag.

Aber zwischen dir und dem Gebäude: eine belebte Kreuzung, zwei Volkspolizei-Beamte die Ausweise kontrollieren. Stichproben, langsam, methodisch. Deine Legende ist wasserdicht — aber Kontrollen bedeuten Aufmerksamkeit, und Aufmerksamkeit bedeutet Risiko.

Auf der anderen Straßenseite: ein Café, Schaufenster beschlagen, innen warm und voll. Ein natürlicher Wartepunkt. Beobachtungsposition.

---

**Intel / Risiken**

- **Weber:** Dienstags im Lesesaal, Erdgeschoss Südflügel — heute, jetzt
- **Stasi-Präsenz:** Drei Funkkanäle, Ausweiskontrolle an der Kreuzung — Leipzig ist kein ruhiges Terrain
- **Innenhof:** Südwestflügel, nicht kartiert — Novaks Information, noch unbestätigt
- **Gruppe:** Kein Profil vor Ort bestätigt — aber 25 Jahre Vorlauf bedeutet möglicherweise bereits etablierte Präsenz

---

Die Volkspolizei-Beamten arbeiten sich durch eine Schlange von vier Personen. Ruhig, keine Spannung — Routine.

Du hast Zeit. Oder du hast keine.

---

**Entscheidung**

1. **Café** — Warten bis die Kontrolle weitergeht, dann rüber zum Verwaltungsgebäude
2. **Direkt durch** — Legende nutzen, Kontrolle passieren, sofort zum Lesesaal
3. **Umweg** — Seitenstraßen, Kontrolle umgehen, Gebäude von der Rückseite angehen

> *Freie Aktion: Umgebung weiter beobachten, Stasi-Funk abhören, den Innenhof zuerst suchen.*

---

## [44] USER

Ich halt Abstand zu den Vopos, geh über den Nebenweg nordöstlich. Unauffällig, Kopf unten.

---

## [45] ASSISTANT

Du biegst links ab. Weg von der Kreuzung, weg von den Uniformen.

Der Nebenweg ist eng — Kopfsteinpflaster, Mülltonnen, ein Fahrrad ohne Vorderrad das an einer Hauswand rostet. Keine Laternen, kein Verkehr. Die Plattenbaufassaden links und rechts haben die Farbe von altem Beton und schlechtem Wetter.

---

**Probe: Schleichen → GES-Probe**
`W6: [3] + GES 5/2 (2) + Talent Schattenschritt +3 = 8 vs SG 7 → ERFOLG`

---

Du gehst mit dem Rhythmus der Stadt. Nicht zu schnell — Eile fällt auf. Nicht zu langsam — Zögern auch. Ein Tempo das sagt: Ich bin auf dem Weg irgendwohin und das irgendwo ist uninteressant.

Ein älterer Mann kommt dir entgegen, Einkaufsnetz in der Hand, Blick auf den Boden. Ihr geht aneinander vorbei ohne Augenkontakt. Gut.

Zweite Ecke, dritte. Der Nebenweg mündet in eine breitere Straße — und da liegt es.

Das Verwaltungsgebäude. Vier Stockwerke, Gründerzeitfassade die jemand in den Fünfzigern mit DDR-Grau überstrichen hat. Schwere Eingangstür, Messingschild, verwittert: *STADTARCHIV LEIPZIG — VERWALTUNG UND LESESAAL.*

Rechts vom Haupteingang, kaum sichtbar hinter einem Busch der niemand mehr schneidet: eine Seitenpassage. Schmal, zwischen dem Hauptgebäude und einem Nebentrakt. Kein Schild, kein Hinweis.

Richtung Südwestflügel.

Richtung Innenhof.

`Kodex: Passage identifiziert — Südwestflanke, nicht kartiert. Übereinstimmung mit Novak-Information: hoch.`

Vor dem Haupteingang: eine Frau. Mitte dreißig, dunkle Brille, grauer Wintermantel. Sie steht mit einer Aktentasche vor der Tür und sucht etwas darin — Schlüssel, Ausweis, irgendetwas. Ruhig, konzentriert, keine Eile.

Das Gesicht passt zu den körnigen Fotos aus dem Kuvert.

Weber.

Sie ist draußen, nicht drin. Und sie schaut gleich auf.

---

**Intel / Risiken**

- **Weber:** Steht vor dem Haupteingang, allein, beschäftigt — Kontaktfenster offen, aber exponiert
- **Passage:** Südwestflanke, unbeschildert — Novaks Innenhof möglicherweise dahinter
- **Straße:** Ruhig aber nicht leer — zwei Passanten, ein Fahrradfahrer weiter hinten
- **Stasi-Funk:** Noch aktiv im Hintergrund, kein direkter Bezug zur aktuellen Position

---

Weber findet was sie sucht — ein Schlüsselbund, groß, viele Schlüssel. Sie greift nach der Türklinke.

Zehn Sekunden. Vielleicht weniger.

---

**Entscheidung**

1. **Weber jetzt ansprechen** — Vor der Tür, natürlicher Kontakt, Legende einsetzen
2. **Passage zuerst** — Innenhof bestätigen bevor du Kontakt aufnimmst
3. **Folgen** — Ihr in den Lesesaal folgen, Situation drinnen einschätzen bevor du dich zeigst

> *Freie Aktion: Warten, Umgebung weiter scannen, anders vorgehen.*

---

## [46] USER

Ich geh auf sie zu. Jetzt, bevor die Tür zu ist.

„Entschuldigung — sind Sie vom Stadtarchiv? Ich such den Lesesaal, ich hab eine Anfrage zur Stadtplanung Leipzig, 1952...

---

## [47] ASSISTANT

Du bewegst dich. Drei Schritte, vier — zügig aber nicht gehetzt.

*„Entschuldigung — sind Sie vom Stadtarchiv? Ich such den Lesesaal, ich hab eine Anfrage zur Stadtplanung Leipzig, 1952..."*

Weber dreht sich um.

Aus der Nähe ist sie anders als auf den Fotos. Schärfer. Die Brille sitzt schief, ein Bügel leicht verbogen — nie repariert oder nie bemerkt. Ihre Augen hinter den Gläsern sind wach, schnell, die Art von Augen die Informationen sortieren bevor der Rest des Gesichts reagiert hat.

Sie mustert dich. Einmal, kurz, oben nach unten.

---

**Probe: Täuschung → CHA-Probe**
`W6: [4] + CHA 2/2 (1) = 5 vs SG 5 → ERFOLG, knapp`

---

Deine Legende sitzt — westdeutsche Journalistin, Kulturreportage, akkreditiert. Der Akzent passt, die Kleidung passt, die Anfrage ist banal genug um real zu wirken.

Weber entspannt minimal. Nicht warm — aber nicht misstrauisch.

*„Lesesaal ist innen, Erdgeschoss, links."* Sie hält die Tür auf. Nicht aus Herzlichkeit — aus Effizienz. *„Stadtplanung 1952 ist Bestand C, Regal 14. Sie brauchen einen Leserschein, den bekommen Sie am Empfang."*

Sie geht rein. Du gehst mit.

---

Die Eingangshalle riecht nach altem Papier und Heizkörperwärme. Linoleumboden, abgetreten in der Mitte wo die meisten Schritte fallen. Eine Empfangsdame hinter einem Tresen schaut kurz hoch — registriert Weber, registriert dich, schreibt etwas.

Weber biegt links ab. Du bleibst einen halben Schritt hinter ihr.

*„Sind Sie oft hier?"* sagst du. Beiläufig, Journalistenton — neugierig aber unverbindlich.

Sie schaut kurz über die Schulter.

*„Jeden Dienstag und Donnerstag. Seit neun Jahren."*

Keine weitere Erklärung. Sie sagt es wie eine Tatsache über das Wetter.

Ihr erreicht den Lesesaal. Hohe Decken, lange Tische, das Licht fällt durch schmale Fenster in langen Streifen. Vier andere Personen im Raum — zwei Studenten, ein älterer Mann mit Lupe, eine Frau die schläft.

Weber geht zu ihrem Platz. Erkennbar ihrem Platz — dritter Tisch von links, Fensterseite, ein Stapel Ordner liegt bereits dort als hätte sie ihn gestern Abend stehen lassen.

Sie setzt sich. Legt die Aktentasche ab. Schaut dann zu dir — weil du noch stehst.

*„Empfang ist zurück im Flur."*

Eine Pause. Dann, leiser, fast beiläufig:

*„Stadtplanung 1952 ist übrigens unvollständig. Bestand C, Regal 14 — der Südwestbereich der Stadt fehlt komplett. Wurde 1972 ausgesondert."*

Sie öffnet ihren Ordner.

*„Falls Sie das interessiert."*

---

**Probe: Einschätzen → INT-Probe**
`W10: [6] + INT 6/2 (3) = 9 vs SG 8 → ERFOLG`

---

Das war kein Smalltalk.

Weber hat dir gerade etwas gegeben — bewusst, dosiert, mit dem Timing von jemandem die testet ob du die richtige Frage stellst. Neun Jahre in diesem Gebäude. Sie weiß dass der Südwestbereich fehlt. Sie weiß seit wann.

Sie weiß mehr.

`Kodex: 1972 — Bestand C Südwestbereich ausgesondert. Zeitgleich mit ITI-interner Sperrung Leipzig-Unterarchiv. Kein Zufall.`

---

**Intel / Risiken**

- **Weber:** Testet dich — die Bemerkung über 1972 war kein Zufall
- **Bestand C, Südwestbereich:** Ausgesondert 1972, zeitgleich mit ITI-Sperrung — direkter Zusammenhang
- **Weber weiß etwas:** Neun Jahre, dieselbe Stelle, derselbe blinde Fleck — sie hat gezählt
- **Lesesaal:** Vier Zeugen, Empfangsdame im Flur — kein Ort für offene Gespräche
- **Stasi:** Leipzig ist wachsam — jedes längere Gespräch zwischen Westjournalistin und Archivarin ist potenziell sichtbar

---

Weber liest. Oder tut so als ob.

Ihr Stift liegt parallel zum Ordner, unbenutzt.

---

**Entscheidung**

1. **Den Köder nehmen** — Zurück zu ihr, nach dem Südwestbereich fragen, sehen wie weit sie geht
2. **Leserschein holen** — Empfang, Legende festigen, dann organisch zurück zu Weber
3. **Warten** — Eigenen Platz nehmen, beobachten, Weber den nächsten Schritt machen lassen

> *Freie Aktion: Bestand C selbst suchen, den Lesesaal auf weitere Personen prüfen, anders reagieren.*

---

## [48] USER

Ich setz mich an den Nachbartisch, kram meinen Block raus, und sag leise ohne aufzuschauen: „1972 — interessantes Jahr für eine Aussonderung.

---

## [49] ASSISTANT

Du ziehst den Stuhl heraus. Setzt dich. Der Block kommt raus — Stift in der Hand, Blick auf das leere Papier.

Beiläufig. Zwei Leute die zufällig nebeneinander sitzen.

Die vier Sekunden Stille nach deinen Worten sind die lautesten im Raum.

---

**Probe: Täuschung/Soziales → CHA-Probe**
`W6: [6] + [4] (explodiert) + CHA 2/2 (1) = 11 vs SG 8 → ERFOLG`

---

Weber schlägt eine Seite um. Langsam, gleichmäßig.

*„Interessantes Jahr für vieles,"* sagt sie. Gleiche Lautstärke wie du. Gleicher Ton — beiläufig, als würden sie über das Wetter reden. *„Die Heizung im Südflügel wurde erneuert. Der Hausmeister hat gewechselt. Und ungefähr dreißig laufende Meter Akten sind verschwunden."*

Pause. Ihr Stift bewegt sich jetzt — sie schreibt etwas, echte Notizen, Augen auf ihrem Ordner.

*„Nicht ausgesondert. Verschwunden. Das ist ein Unterschied."*

Ein Student am anderen Ende des Saals hustelt. Die schlafende Frau bewegt sich kurz, schläft weiter.

Weber dreht keine Seite mehr um.

*„Ich arbeite seit neun Jahren hier,"* fährt sie fort. Noch leiser jetzt. *„In den ersten drei Jahren dachte ich es wäre Unordnung. Schlechte Verwaltung. DDR-Bürokratie."* Eine kurze Pause. *„Im vierten Jahr habe ich angefangen Listen zu führen. Was fehlt. Wo es fehlt. Seit wann."*

Ihr Stift stoppt.

*„Die Lücken haben ein Muster."*

Sie dreht sich nicht zu dir. Aber ihr Kopf neigt sich minimal — die Haltung von jemandem die genau zuhört ob jemand aufsteht, zur Tür geht, Alarm schlägt.

Niemand tut das.

*„Wer schickt Sie?"* Immer noch beiläufig. Immer noch auf ihren Ordner schauend. Aber die Frage hat Gewicht.

---

**Probe: Einschätzen → INT-Probe**
`W10: [8] + INT 6/2 (3) = 11 vs SG 9 → ERFOLG`

---

Sie hat Angst. Nicht die akute Angst von jemandem der gerade entdeckt wird — die chronische Angst von jemandem der seit Jahren etwas weiß das er nicht wissen sollte und nicht weiß was er damit tun soll.

Sie hat auf jemanden gewartet. Nicht unbedingt auf dich — aber auf jemanden der die richtige Frage stellt.

Du hast die richtige Frage gestellt.

`Kodex: Weber — aktiv informiert, eigenständige Recherche seit mindestens 6 Jahren. Kein ITI-Kontakt bisher. Potenzielle Primärquelle für Unterarchiv-Zugang.`

---

Der ältere Mann mit der Lupe steht auf. Geht zum Regal. Kommt zurück. Setzt sich.

Niemand schaut her.

Die Frage hängt noch im Raum: *Wer schickt Sie?*

---

**Intel / Risiken**

- **Weber:** Führt seit sechs Jahren eigene Listen über die Lücken — sie ist tiefer drin als erwartet
- **„Verschwunden, nicht ausgesondert":** Weber kennt den Unterschied und hat ihn dokumentiert
- **Muster:** Die Lücken haben ein Muster — was hat sie gefunden?
- **Ihre Frage:** Sie testet nicht mehr — sie will wissen ob du sicher bist
- **Stasi-Risiko:** Längeres Gespräch im Lesesaal, Empfangsdame im Flur, vier Zeugen

---

**Entscheidung**

1. **Teilwahrheit** — *„Leute die sich für dasselbe interessieren wie Sie."* Kein ITI, kein Name — aber kein Abstreiten
2. **Volle Legende** — Journalistin, Recherche, offizieller Rahmen — sicherer, aber Weber kauft es vielleicht nicht mehr
3. **Ortswechsel vorschlagen** — *„Nicht hier. Wann haben Sie Pause?"*

> *Freie Aktion: Gegenfrage stellen, ihr die Listen zeigen lassen, anders reagieren.*

---

## [50] USER

Ich nehm 1, dann direkt 3.

*„Leute die sich für dasselbe interessieren wie Sie. — Aber nicht hier. Wann haben Sie Pause?"*

---

## [51] ASSISTANT

Weber schreibt einen Satz zu Ende. Legt den Stift hin.

Nimmt ihn wieder auf.

*„Halb vier. Bäckerei Krüger, Karl-Liebknecht-Straße. Ich kauf dort jeden Dienstag ein."*

Sie blättert um. Das Gespräch ist beendet — von ihrer Seite, bewusst, sauber. Keine weiteren Worte, kein Blick. Nur zwei Leute in einem Lesesaal die nichts miteinander zu tun haben.

Professionell.

Du stehst auf. Nimmst deinen Block. Gehst zum Empfang, holst dir den Leserschein, setzt dich an einen anderen Tisch. Spielst die Legende durch — Bestand C, Regal 14, Stadtplanung 1952. Der Südwestbereich fehlt tatsächlich. Dreißig laufende Meter Lücke, glatt herausgeschnitten aus dem Bestand, die Regalböden staubfrei wo die Ordner waren.

Jemand hat sauber gearbeitet.

`Kodex: Bestand C bestätigt — physische Lücke im Regal. Entfernung präzise, kein Rückstand. Kein Zufallsprodukt.`

Die Zeit bis halb vier läuft.

---

## Karl-Liebknecht-Straße — 15:28 Uhr

Die Bäckerei Krüger ist klein und warm. Das Schaufenster beschlägt von innen. Es riecht nach Mohnkuchen und altem Fett — nicht unangenehm, nur ehrlich.

Du bist zehn Minuten früher da. Nimmst einen Platz am Fenster, bestellst Kaffee der zu dünn ist und zu heiß kommt, schaust auf die Straße.

15:31 — ein Mann bleibt kurz vor der Bäckerei stehen, schaut ins Schaufenster, geht weiter. Unauffällig. Zu unauffällig.

---

**Probe: Beobachtung → INT-Probe**
`W10: [7] + INT 6/2 (3) = 10 vs SG 8 → ERFOLG`

---

Westliche Schuhe. Dasselbe Detail das Novak über den Kurier aus Warschau gesagt hat — und du hättest es fast übersehen. Die Sohle, der Schnitt, die Farbe des Leders. Nicht DDR-Produktion. Nicht polnisch. Westdeutsch oder österreichisch.

Der Mann ist weg. Aber er war da.

`Kodex: Unbekannte Person — westliches Schuhwerk, Beobachtungsverhalten. Mögliche Gruppen-Präsenz. Markiert.`

15:34 — Weber kommt. Wintermantel, Aktentasche, Brille noch immer schief. Sie kauft ein Brot und zwei Brötchen ohne auf die Auslage zu schauen — Gewohnheit, dieselbe Bestellung seit Jahren. Dann kommt sie zu dir.

Setzt sich. Stellt die Tüte ab.

Schaut dich an. Direkt, zum ersten Mal.

*„Sie haben den Mann vor dem Fenster gesehen."* Keine Frage.

---

**Intel / Risiken**

- **Weber:** Hat den Mann ebenfalls bemerkt — sie ist wachsamer als sie wirkt
- **Unbekannte Person:** Westliche Schuhe, Beobachtungsverhalten — möglicherweise Gruppenagent
- **Bäckerei:** Warm, voll, Hintergrundlärm — besser als der Lesesaal, aber nicht sicher
- **Zeitfenster:** Weber hat Pause bis halb fünf — eine Stunde

---

Draußen zieht eine Straßenbahn vorbei. Das Fenster vibriert kurz.

Weber wartet. Ihre Hände liegen flach auf dem Tisch — dieselbe Geste wie Novak im Befragungsraum. Menschen die gelernt haben ihre Hände sichtbar zu halten.

*„Ich kenne diesen Mann nicht,"* sagt sie leise. *„Aber ich kenne seine Schuhe. Er war letzte Woche auch schon da. Und die Woche davor."*

Drei Wochen. Die Gruppe ist bereits vor Ort.

Vier Jahre vor ihrem eigenen Zieldatum.

---

**Entscheidung**

1. **Offen werden** — Weber sagen dass sie auf einer Liste steht, dass sie in Gefahr ist
2. **Die Listen** — Sie nach ihren eigenen Aufzeichnungen fragen, was hat sie über die Lücken herausgefunden
3. **Den Mann** — Erst klären wer draußen beobachtet, bevor das Gespräch weitergeht

> *Freie Aktion: Subkutanen Jammer aktivieren, Ortswechsel vorschlagen, beides kombinieren.*

---

## [52] USER

Ich aktiviere den Jammer und sage leise: „Wir wechseln den Ort. Jetzt. Ich erklär alles unterwegs — Sie sind in Gefahr.

---

## [53] ASSISTANT

Du drückst den Aktivierungspunkt unter der Haut, zwei Finger kurz an den Unterarm. Kein Geräusch, kein Leuchten — nur das vertraute Kribbeln das bedeutet dass lokale Signale gerade taub werden.

`Kodex: Subkutaner Jammer — aktiv. Radius 8 Meter. Dauer: 12 Minuten. Danach Cooldown 2 Szenen.`

Weber steht auf bevor du fertig gesprochen hast. Nimmt die Tüte, nimmt die Aktentasche — eine Bewegung, geübt, als hätte sie das schon einmal geprobt. Vielleicht hat sie das.

Du lässt zwei zerknitterte Scheine auf dem Tisch.

---

## Karl-Liebknecht-Straße — in Bewegung

Draußen ist die Luft kalt und nach Braunkohle. Ihr geht nebeneinander, nicht zu nah, Tempo eines normalen Spaziergangs. Du redest ohne sie anzuschauen.

*„Es gibt eine Liste. Fünf Namen. Ihrer steht drauf — mit einem Datum, März 1987. Leute die diese Liste angelegt haben wollen verhindern dass Sie etwas finden oder weitersagen. Der Mann vor der Bäckerei gehört zu ihnen."*

Weber sagt nichts. Ihr Schritt ändert sich nicht.

*„Das ITI — kennen Sie den Namen nicht, macht nichts — wir arbeiten daran die Personen auf der Liste zu schützen. Sie sind die nächste."*

Eine Straßenbahn rattert vorbei. Für vier Sekunden ist alles Lärm.

Dann, ruhig: *„Ich weiß seit zwei Jahren dass jemand mich beobachtet."*

---

**Probe: Einschätzen → INT-Probe**
`W10: [5] + INT 6/2 (3) = 8 vs SG 7 → ERFOLG`

---

Keine Panik. Keine Überraschung. Sie verarbeitet — schnell, sachlich, die Art von Verarbeitung die nur funktioniert wenn man die Möglichkeit bereits durchgespielt hat.

*„Ich habe Kopien gemacht,"* sagt sie dann. Noch leiser. *„Von allem was ich gefunden habe. Nicht hier — nicht in der Wohnung. Woanders."*

Sie biegt links ab. Du folgst.

Eine schmale Gasse, Hinterhöfe, Wäscheleinen zwischen den Fenstern. Kein Durchgangsverkehr. Sie kennt den Weg.

*„Das Unterarchiv,"* sagt sie. *„Ich weiß wo der Eingang ist."*

Sie stoppt. Dreht sich zu dir. Zum zweiten Mal direkter Blickkontakt.

*„Ich hab ihn vor drei Jahren gefunden. Ich bin nicht reingegangen — ich wusste dass ich es nicht allein tun sollte."* Eine kurze Pause. *„Ich hab gewartet dass jemand die richtige Frage stellt."*

`Kodex: Jammer — 7 Minuten verbleibend.`

Irgendwo hinter euch, zwei Straßen weiter, Schritte. Gleichmäßig. Zu gleichmäßig für einen Spaziergänger.

---

**Probe: Beobachtung → INT-Probe**
`W10: [9] + INT 6/2 (3) = 12 vs SG 9 → ERFOLG`

---

Nicht der Mann von der Bäckerei. Eine andere Person — Frau, dunkler Mantel, Abstand haltend aber Richtung haltend. Sie folgt seit der Karl-Liebknecht-Straße.

Zwei Beobachter. Mindestens.

`Kodex: Beschattung bestätigt. Zwei Personen, koordiniert. Jammer läuft — kein Funk, aber visuelle Koordination möglich.`

Weber hat es noch nicht bemerkt. Aber sie wartet auf deine Antwort.

Die Kopien. Der Eingang. Beides greifbar — und jemand ist hinter euch.

---

**Intel / Risiken**

- **Weber:** Kennt den Eingang zum Unterarchiv, hat Kopien ihrer Recherche — seit drei Jahren vorbereitet
- **Beschattung:** Zwei Personen koordiniert, seit Karl-Liebknecht-Straße — Jammer blockiert Funk, nicht Augen
- **Jammer:** 7 Minuten verbleibend — danach können sie wieder kommunizieren
- **Kopien:** Wo sind sie? Sicherer Ort, nicht die Wohnung
- **Zeitdruck:** Zwei Beobachter, begrenzte Jammerzeit, offene Straße

---

**Entscheidung**

1. **Unterarchiv jetzt** — Weber führt dich direkt hin, Beschattung abhängen unterwegs
2. **Kopien zuerst** — Wo sind sie, können sie gesichert werden bevor die Gruppe zugreift
3. **Beschattung konfrontieren** — Jetzt, bevor der Jammer ausläuft, auf eigenen Terrain

> *Freie Aktion: Weber warnen, Comlink aktivieren, Route ändern, anders vorgehen.*

---

## [54] USER

Wo sind die Kopien — und wie weit zum Archiv?"

Ich frag kurz, während ich unauffällig das Tempo erhöhe. Wir müssen die Frau im dunklen Mantel abschütteln bevor der Jammer ausläuft.

---

## [55] ASSISTANT

*„Kopien — Kirchgemeinde Sankt Thomas, drei Blocks west. Pfarrer Held, er weiß nichts vom Inhalt."*

Sie hält dein Tempo. Keine Fragen warum.

*„Zum Archiv — zehn Minuten zu Fuß. Durch den Innenhof Südwestflügel."*

Novaks Information war korrekt.

*„Aber nicht jetzt,"* sagt sie. *„Nicht mit jemandem hinter uns."*

---

Du schaust nicht zurück. Retina-HUD, Bewegungsmarker — die Frau im dunklen Mantel, jetzt noch eineinhalb Blocks Abstand. Gleichmäßig. Professionell.

`Kodex: Jammer — 5 Minuten verbleibend. Beschattung Abstand: stabil. Visuelle Koordination mit Person 1 möglich.`

Rechts: eine Durchfahrt zwischen zwei Plattenbauten, Wäscheleinen, kein Durchblick von der Straße. Links: ein belebter Marktplatz, Stände, Menschenmenge — Deckung aber auch Zeugen.

Weber tippt kurz deinen Arm. Einmal, dezent.

*„Geradeaus. Zweite Tür links. Hinterhof."*

Sie kennt die Gassen besser als du.

---

**Probe: Schleichen/Abschütteln → GES-Probe (Malus: Begleitung, Beobachtung aktiv)**
`W6: [6] + [5] (explodiert) + GES 5/2 (2) + Talent Schattenschritt +3 - 1 (Begleitung) = 15 vs SG 10 → KRITISCHER ERFOLG`

---

Du folgst Webers Instinkt und deinem eigenen.

Geradeaus, zweite Tür links — eine Holztür, abgeblätterte grüne Farbe, nicht abgeschlossen. Ihr seid durch bevor die Frau im dunklen Mantel die Ecke erreicht. Ein Hinterhof, Mülltonnen, eine Katze die euch anschaut und weitergeht.

Rechts eine weitere Tür, Durchgang zum nächsten Hof. Dann links, eine enge Passage zwischen Feuermauern — kein Tageslicht, kein Sichtfeld von der Straße.

Du bleibst stehen. Weber auch.

Stille.

Schritte auf der Straße — die Frau im dunklen Mantel passiert die grüne Tür ohne zu stoppen. Gleichmäßiges Tempo, kurze Pause, dann weiter. Sie sucht, aber sie hat euch nicht.

Dreißig Sekunden. Eine Minute.

Nichts.

`Kodex: Beschattung — Kontakt verloren. Jammer — 3 Minuten verbleibend. Empfehlung: Position halten bis Ablauf.`

---

Weber lehnt an der Feuermauer. Atmet einmal tief aus — kontrolliert, nicht hörbar, aber du siehst wie die Schultern sich senken.

Dann schaut sie dich an.

*„Sankt Thomas zuerst,"* sagt sie. *„Die Kopien. Wenn etwas passiert bevor wir ins Archiv kommen — Pfarrer Held, fragen Sie nach dem Notenarchiv. Die Mappe liegt zwischen Bach und Buxtehude."*

Sie sagt das mit der Ruhe von jemandem die Notfallpläne nicht als Notfälle betrachtet sondern als Routinen.

*„Dann Unterarchiv. Ich zeig Ihnen den Eingang."*

Eine kurze Pause.

*„Was auch immer dort unten liegt — ich glaube es gehört nicht der DDR."*

`Kodex: Jammer — läuft aus in 90 Sekunden. Danach Cooldown aktiv, 2 Szenen.`

---

**Intel / Risiken**

- **Kopien:** Sankt Thomas, Pfarrer Held, Notenarchiv — zwischen Bach und Buxtehude
- **Unterarchiv-Eingang:** Weber kennt ihn, zehn Minuten zu Fuß, Innenhof Südwestflügel
- **Beschattung:** Kontakt verloren — aber zwei Personen koordiniert, werden neu positionieren
- **Jammer:** 90 Sekunden, dann Cooldown — Gruppe kann danach wieder kommunizieren
- **Webers Einschätzung:** Material im Unterarchiv gehört nicht der DDR — was bedeutet das?
- **Zeitfenster:** Offen, aber Beschattung wird zurückkommen

---

Die Passage liegt still. Irgendwo über euch tropft Wasser von einer Dachrinne, gleichmäßig, geduldig.

Weber wartet auf deine Entscheidung.

---

**Entscheidung**

1. **Sankt Thomas zuerst** — Kopien sichern, dann Unterarchiv
2. **Unterarchiv direkt** — Kopien können warten, Eingang zuerst — bevor die Beschattung neu positioniert
3. **Beides koordinieren** — Weber zu den Kopien schicken, selbst zum Innenhof — aufteilen

> *Freie Aktion: ITI kontaktieren, Comlink aktivieren, Weber mehr fragen, anders vorgehen.*

---

## [56] USER

Ich nehm 1. Kopien zuerst — wenn wir unten nicht rauskommen, will ich dass die Sicherung steht.

---

## [57] ASSISTANT

Weber nickt einmal. Das war die richtige Antwort — du siehst es daran dass sie nichts sagt.

Ihr wartet bis der Jammer ausläuft.

`Kodex: Jammer — abgelaufen. Cooldown aktiv, 2 Szenen. Lokale Signale wieder offen.`

Dann bewegt ihr euch.

---

## Sankt Thomas — 16:11 Uhr

Die Thomaskirche ist größer als die Gasse vermuten lässt. Backstein, dunkel vom Regen vieler Jahrzehnte, der Turm verschwindet im grauen Himmel. Bach ist hier begraben — das weiß jeder. Was sonst noch hier liegt, weiß fast niemand.

Der Seiteneingang ist offen. Holzbänke, Kerzenlicht, der Geruch von kaltem Stein und altem Holz. Zwei ältere Frauen beten in den vorderen Reihen. Sonst niemand.

Weber geht direkt zur Sakristei. Klopft zweimal, kurz.

---

Pfarrer Held ist Mitte sechzig, kleiner als erwartet, mit den Händen eines Mannes der viel trägt und wenig klagt. Er öffnet die Tür, sieht Weber, sieht dich — seine Augen bleiben eine Sekunde länger auf dir als nötig.

*„Ilse."* Kein Lächeln, aber warm. *„Und Besuch."*

*„Sie kann man vertrauen,"* sagt Weber.

Held tritt zur Seite. Ihr geht rein.

---

Die Sakristei riecht nach Bienenwachs und Papier. Regale voller Noten, Gesangbücher, Ordner. Held geht zur hinteren Wand ohne Erklärung — zieht einen flachen Karton heraus, Bach-Beschriftung, Kantaten BWV 1-50.

Er stellt ihn auf den Tisch.

*„Ich weiß nicht was drin ist,"* sagt er zu dir. *„Ich will es nicht wissen. Aber ich bewahre es seit zwei Jahren."* Eine kurze Pause. *„Weil Ilse mich gebeten hat. Das reicht mir."*

Er geht zur Tür. Bleibt kurz stehen.

*„Zehn Minuten. Dann mach ich die Sakristei zu."*

Die Tür schließt sich.

---

Weber öffnet den Karton. Darunter keine Noten — eine flache Mappe, Plastikfolie, eng gepackt.

Sie legt sie auf den Tisch und schlägt sie auf.

---

**Probe: Analyse → INT-Probe**
`W10: [8] + INT 6/2 (3) + Talent Systemzugriff +2 = 13 vs SG 9 → ERFOLG`

---

Dreißig Seiten. Handgeschrieben, durchnummeriert, mit Datum versehen. Weber arbeitet sauber — Beobachtungsprotokolle, Skizzen, Grundrisse.

Erste Seite: Eine Zeitleiste. Lücken im Bestand C, chronologisch geordnet. Älteste Lücke: 1962. Jüngste: 1981. Elf Eingriffe in neunzehn Jahren — regelmäßig, aber nicht rhythmisch. Reaktiv. Die Gruppe hat Material entfernt wenn es relevant wurde, nicht nach Plan.

Mittelteil: Grundrisse. Das Verwaltungsgebäude, von Hand gezeichnet, präzise. Erdgeschoss, Untergeschoss, Keller. Und darunter — eine weitere Ebene, gestrichelt eingezeichnet, mit einem Fragezeichen.

Weber tippt auf die gestrichelte Linie.

*„Das ist nicht im offiziellen Bauplan. Ich hab den Bauplan von 1931 im Stadtarchiv gefunden — vor den Lücken. Da ist diese Ebene drin. Danach nicht mehr."*

Letzte Seiten: Namen. Personen die zwischen 1962 und 1981 Zugang zum Südwestflügel hatten und danach nicht mehr auffindbar waren. Sieben Namen. Keiner davon in einem offiziellen Register.

Ganz unten auf der letzten Seite, eingekreist, in anderer Tinte — nachträglich hinzugefügt:

**NOVAK, T. — Rostock, August 1971.**

Weber schaut dich an.

*„Den kenn ich nicht,"* sagt sie leise. *„Aber der Name tauchte in einem der Dokumente auf die ich vor der Aussonderung noch lesen konnte. Er wusste etwas über das Unterarchiv."*

`Kodex: Weber-Mappe — ITI-relevant, Tier 2. Novak-Querverbindung bestätigt. Gestrichelte Ebene: unbekannte Unterebene unter dem Unterarchiv.`

---

Draußen in der Kirche, leise — Schritte. Nicht Held. Zu gleichmäßig für einen Pfarrer der seine Kirche kennt.

---

**Probe: Beobachtung → INT-Probe**
`W10: [6] + INT 6/2 (3) = 9 vs SG 8 → ERFOLG`

---

Durch den Türspalt: der Mann von der Bäckerei. Westliche Schuhe auf Kirchenboden. Er geht langsam durch das Hauptschiff, schaut zu den Bänken — sucht.

Die beiden älteren Frauen beten. Er stört sie nicht.

Aber er kommt näher zur Sakristei.

`Kodex: Beschattung — neu positioniert. Person 1 im Kirchenraum. Person 2 — Position unbekannt. Jammer Cooldown: noch 1 Szene.`

---

Zehn Minuten hat Held gesagt. Davon sind vier verstrichen.

Die Mappe liegt offen auf dem Tisch. Weber schaut zur Tür. Dann zu dir.

---

**Intel / Risiken**

- **Mappe:** Gesichert — aber noch hier, noch nicht beim ITI
- **Beschattung:** Person 1 im Kirchenraum, Person 2 unbekannt — vier Minuten bis Held die Sakristei schließt
- **Gestrichelte Ebene:** Unterebene unter dem Unterarchiv, nicht im offiziellen Bauplan seit 1962
- **Novak-Verbindung:** Weber hat seinen Namen aus einem Dokument vor der Aussonderung — tiefer als erwartet
- **Jammer:** Noch 1 Szene Cooldown — kein Funk möglich bis dahin

---

**Entscheidung**

1. **Mappe einpacken, Sakristei verlassen** — Hinterausgang falls vorhanden, Mann umgehen
2. **Warten** — Held kommt in sechs Minuten, Sakristei wird geschlossen — Mann kommt nicht rein
3. **Mann konfrontieren** — Jetzt, im Kirchenraum, bevor er die Sakristei erreicht

> *Freie Aktion: Weber die Mappe nehmen lassen, Comlink aktivieren, Held warnen, anders vorgehen.*

---

## [58] USER

Ich schnapp mir die Mappe, steck sie weg. Flüster Weber zu: "Hinterausgang?

---

## [59] ASSISTANT

Weber zögert keine Sekunde.

*„Durch die Sakristei, linke Wand, hinter dem Regal."*

Sie geht bereits während sie spricht. Du folgst — Mappe in der Innentasche, Jacke zu, eine Bewegung.

Das Regal ist schwer, Eichenholz, aber es schwenkt auf — eine Tür dahinter, niedrig, kein Schloss. Held weiß davon. Natürlich weiß er davon.

---

**Probe: Schleichen → GES-Probe**
`W6: [5] + GES 5/2 (2) + Talent Schattenschritt +3 = 10 vs SG 7 → ERFOLG`

---

Ihr seid durch bevor der Mann die Sakristeitür erreicht.

Ein enger Gang, Kirchenmauer links, Friedhofsmauer rechts. Kopfsteinpflaster, nass, Moos in den Fugen. Grabsteine hinter der Mauer, alte lateinische Inschriften die der Regen seit Jahrhunderten glattschleift.

Weber geht schnell aber lautlos. Sie kennt den Weg.

Am Ende des Gangs: ein Eisentor, nicht abgeschlossen. Dahinter eine Seitenstraße, leer, parallel zur Karl-Liebknecht-Straße.

Ihr tretet raus. Tor zu. Weitergehen.

`Kodex: Beschattung — Kontakt verloren, zweites Mal. Jammer Cooldown — abgelaufen. Einsatzbereit.`

---

Zwei Blocks Schweigen. Dann bleibt Weber kurz stehen — nicht aus Erschöpfung, zur Orientierung. Schaut einmal zurück, einmal nach vorn.

*„Niemand."*

Dann, leiser:

*„Sie haben Novak erwähnt. Vorhin — Sie haben gesagt der Name ist Ihnen bekannt."*

Es ist keine Anschuldigung. Es ist die Frage die sie die ganze Zeit gestellt hat ohne sie zu stellen.

---

Du gehst weiter. Weber hält dein Tempo.

Die Antwort die du gibst — oder nicht gibst — verändert was als nächstes kommt.

---

**Intel / Risiken**

- **Mappe:** Gesichert, bei dir — Tier 2, ITI-relevant
- **Beschattung:** Zweimal abgehängt, aber zwei Personen koordiniert — werden neu positionieren
- **Unterarchiv:** Zehn Minuten zu Fuß, Weber kennt den Eingang — Fenster noch offen
- **Webers Frage:** Novak. Sie will wissen wie tief du wirklich drin bist
- **Jammer:** Wieder einsatzbereit

---

Die Straße liegt still. Braunkohleluft, nasse Blätter, das ferne Rattern einer Straßenbahn.

---

**Entscheidung**

1. **Teilwahrheit** — *„Novak ist in Sicherheit. Mehr kann ich jetzt nicht sagen."*
2. **Mehr erzählen** — Novak, die Gedächtnislücken, Rostock 1971 — sie hat ein Recht darauf
3. **Gegenfrage** — *„Was stand in dem Dokument über ihn?"*

> *Freie Aktion: Comlink aktivieren, ITI informieren, Thema wechseln, anders antworten.*

---

## [60] USER

!save

---

## [61] ASSISTANT

`SaveGuard: Speichern nur im HQ möglich — aktive Mission, HQ-Save gesperrt.`

`Kodex: Feldeinsatz läuft. Kein Deepsave möglich.`

---

**Aktueller Stand (Kurzstatus):**

```
Wire — Lena Voss
Lvl 3 · Wallet 590 CU · Stress 0/10 · HP 10/10
Px 2/5 · EP1 · MS3 · SC ~7/12

CARRY:
  Weber-Mappe (Tier 2, heiß)
  Kompakte Automatikpistole
  Taktische Leichtrüstung
  Multitool-Rig · Comlink Mk.II
  Rauchgranate ×2 · Medkit ×1

STATUS:
  Jammer: einsatzbereit
  Beschattung: Kontakt verloren (2×)
  Weber: bei mir, Unterarchiv-Eingang bekannt
  Nächste Entscheidung: Novaks Frage beantworten
```

---

Kein JSON bis HQ. Aber der Stand ist klar — du weißt wo du bist.

**Weiter?** Weber wartet auf eine Antwort.

---

## [62] USER

!save

---

## [63] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

`Kodex: Keine Änderung seit letzter Statusausgabe. Kurzstatus bereits ausgegeben.`

---

Der Stand ist derselbe wie eben. Kein neuer JSON bis HQ.

Weber steht neben dir auf der nassen Straße und wartet auf eine Antwort über Novak.

---

**Entscheidung**

1. **„Novak ist in Sicherheit. Mehr kann ich jetzt nicht sagen."**
2. **Mehr erzählen** — Novak, Gedächtnislücken, Rostock 1971
3. **„Was stand in dem Dokument über ihn?"**

> *Freie Aktion: Comlink aktivieren, weitergehen ohne zu antworten, anders.*

---

## [64] USER

!save

---

