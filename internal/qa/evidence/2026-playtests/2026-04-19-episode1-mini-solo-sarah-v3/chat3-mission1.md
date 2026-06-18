# chat3-mission1

**Turns:** 32  |  **Sauber beendet:** False  |  **Save:** True

---

## [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-01-01T01:00:00Z-HQ-WIRE-002",
  "parent_save_id": "SAVE-2026-01-01T00:00:00Z-HQ-WIRE-001",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 0,
    "px": 0,
    "px_state": "stable",
    "mode": "mixed",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-WIRE-001",
      "name": "Lena Voss",
      "callsign": "Wire",
      "rank": "Rekrut",
      "lvl": 1,
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
          "tier": "Basis",
          "effect": "+2 auf GES-Proben bei Schleichen und Verbergen"
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
          "Zero Time Lounge: Erstes Gespräch mit Peel. Herkunft angedeutet — spontaner Riss in der Wohnung, Griff ins Unbekannte. Peel fragte nach dem Riss-Inhalt und den 'falschen Leuten'. Antwort steht noch aus."
        ]
      },
      "carry": [],
      "quarters_stash": [],
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
          "next_ready_in": 0
        },
        "legendary_temporal_ship": null
      },
      "reputation": {
        "iti": 0,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 100
    }
  ],
  "economy": {
    "hq_pool": 0
  },
  "logs": {
    "trace": [],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Peel — Barkeeper Zero Time Lounge. Ehem. Feldagent, Rift-Ops. Schulter-Verwundung Konstantinopel. Beobachtet scharf, fragt präzise.",
      "Kessler — Agent, sitzt allein an der Bar. Team nicht zurückgekommen. Status unbekannt."
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
    "summary_active_arcs": ""
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 0,
      "location": "Zero Time Lounge"
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
        "scope": "HQ",
        "status": "active"
      }
    ],
    "active_npc_ids": ["NPC-PEEL-001", "NPC-KESSLER-001"]
  },
  "arc": {
    "factions": {},
    "questions": [
      "Was war auf der anderen Seite des Risses in Wires Wohnung?",
      "Wer sind die 'falschen Leute', die nach Wire gesucht haben?"
    ],
    "hooks": [
      "Peel kennt offenbar mehr über spontane Riss-Kontakte als ein normaler Barkeeper sollte."
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

## [1] ASSISTANT

# ZEITRISS — Save geladen

---

`Kodex: Session-Anker gesetzt. CHR-WIRE-001 "Lena Voss / Wire" — Lvl 1, HQ, Zero Time Lounge. Kontinuität stabil.`

---

**Kurzrückblick — Was zuletzt geschah:**

Die Zero Time Lounge. Schummriges Licht, das Glas in deiner Hand noch nicht leer. Du hast Peel kennengelernt — Barkeeper, aber mit Augen, die nichts vergessen. Er hat nach dem Riss gefragt. Nach dem, was auf der anderen Seite war. Nach den falschen Leuten, die danach gesucht haben. Du hast noch nicht geantwortet. Kessler saß allein an der Bar, sein Team irgendwo in der Geschichte verschollen. Die Lounge summte leise. Das Gespräch hing noch in der Luft.

---

## HQ — ITI Nullzeit

`EP 1 · MS 0 · PHASE HQ · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10`

Die Lounge hat sich seit gestern nicht verändert. Warum auch — hier verändert sich nichts. Die Nullzeit ist genau das: ein Moment, der nie weiterläuft, bis du es willst.

Peel poliert ein Glas hinter der Theke. Er hat dich bemerkt, aber er wartet. Der Mann ist geduldig auf eine Art, die man sich nur durch zu viele Einsätze antrainiert.

---

**Wo willst du hin?**

1. **Gespräch mit Peel fortsetzen** — Die Frage hängt noch im Raum. Wer sind die falschen Leute? Was war auf der anderen Seite des Risses?
2. **Kessler ansprechen** — Er sitzt immer noch allein. Sein Team ist nicht zurückgekommen. Vielleicht hat er Informationen. Vielleicht will er einfach nicht allein sitzen.
3. **Operations-Deck aufsuchen** — Erstes Briefing abholen. Du bist Rekrut. Irgendwo wartet ein Auftrag mit deinem Namen drauf.
4. **Freie Aktion** — Quarzatrium, Med-Lab, Hangar-Axis, Quartiere — oder etwas anderes.

---

## [2] USER

Briefing - ich bin bereit fuer die erste Mission

---

## [3] ASSISTANT

# Briefing — Episode 1, Mission 1

---

`EP 1 · MS 1 · SC 0/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: Auftrag empfangen · Exfil: —`

---

**Regie-Layer:** Wire. Rekrutin. Archiveinbruch-Akte noch offen. Das ITI hat dich nicht wegen deiner Biografie rekrutiert — sie haben dich wegen deiner Hände rekrutiert. Weil jemand, der sich in ein gesichertes Archiv hackt, ohne einen einzigen Alarm auszulösen, nützlicher ist als drei ausgebildete Agenten mit Schusswaffen. Dein erster Auftrag ist klein. Absichtlich. Sie wollen sehen, ob du unter Druck dieselbe Person bist.

---

Das Operations-Deck liegt zwei Ebenen über der Lounge. Kein Fenster, kein Tageslicht — die Nullzeit hat beides nicht. Stattdessen: kaltes weißes Licht, das von der Decke fällt wie in einem Operationssaal. Lange Tische, Holografische Karten, der leise Atem von Klimaanlagen.

Ein Duty-Officer — Frau, Mitte dreißig, kurze graue Strähne über dem rechten Ohr — schiebt dir eine Akte über den Tisch. Kein Händeschütteln. Kein Smalltalk.

**„Voss. Willkommen im Betrieb."**

Sie tippt auf die Karte. Eine Stadt flackert auf. Mitteleuropa. Gebäude aus Beton und Glas, Straßen voller Autos mit zu langen Heckflossen, Plakate in kyrillischer Schrift neben deutschen Lettern.

**„Berlin. 1973. Ost-Sektor."**

---

## Briefing — *Operation STILLE FREQUENZ*

**Epoche:** Berlin, DDR — Oktober 1973
**Einstufung:** Core-Op / Klasse B / Einzelagent
**Missionsdauer:** Schätzung 6–8 Stunden Echtzeit

---

**Lage:**

Ein ITI-Informant — Deckname **LAUTLOS** — ist seit 72 Stunden nicht mehr erreichbar. LAUTLOS war eingebettet in den Verwaltungsapparat des Ministeriums für Staatssicherheit, Abteilung XII. Keine kämpferische Ausbildung. Bürokrat. Wertvoller Bürokrat.

Letzter bekannter Aufenthaltsort: eine Wohnung in **Prenzlauer Berg**, Schönhauser Allee 44, zweiter Stock.

Letzte Übertragung vor dem Ausfall: ein fragmentiertes Signal, das nach Auswertung durch Kodex einen einzigen verwertbaren Satz enthielt.

`Kodex: Rekonstruierter Klartext, LAUTLOS-Signal, 14.10.1973, 02:17 Uhr — "Sie wissen, dass ich schaue. Ich habe etwas gefunden. Kommt nicht durch die Tür."`

---

**Auftrag:**

1. **LAUTLOS lokalisieren** — lebend oder als Spur.
2. **Datenmaterial sichern** — LAUTLOS hatte Zugang zu Abteilung-XII-Akten. Was auch immer er gefunden hat, muss das ITI erreichen.
3. **Keine Spur hinterlassen** — Du bist 1973. Du existierst nicht.

---

**Bekannte Risiken:**

- **Stasi-Observanz:** Prenzlauer Berg steht unter erhöhter Überwachungsdichte. Informelle Mitarbeiter (IMs) in jedem dritten Hauseingang. Uniformierte Streifen alle 20 Minuten.
- **Ausgangsidentität:** Du erhältst eine Legende — Bürgerliche Identität als **"Elena Weiß"**, Sekretärin, zugereist aus Leipzig. Papiere sind sauber. Akzent muss sitzen.
- **Ausrüstungsbeschränkung:** Nichts Anachronistisches sichtbar. Retina-HUD bleibt aktiv, aber passiv. Subkutaner Jammer nur im Notfall — lokale Signalstörungen fallen 1973 sofort auf. Comlink Mk.II bleibt verborgen. Pistole nur wenn keine andere Option.

---

**Exfil:**

Gate-Fenster öffnet **alle 4 Stunden** am Checkpoint Bornholmer Straße, Untergeschoss, Wartungsschacht B-7. Nächstes Fenster: T-04:00 nach Sprung.

---

Die Duty-Officerin faltet die Hände.

**„LAUTLOS hat Familie hier. Frau, zwei Kinder. Wir wissen nicht, ob die Stasi das weiß. Wenn du rein gehst und die Wohnung ist heiß — raus. Kein Heldentum. Spur sichern und Exfil. Verstanden?"**

Sie wartet auf deine Antwort, aber ihre Augen sagen bereits: Sie hat diese Frage schon hundert Mal gestellt.

---

**Loadout-Check vor dem Sprung:**

Deine Ausrüstung ist epochenkompatibel verpackt — die Pistole in einem unauffälligen Schulterholster unter einem langen Mantel, das Multitool-Rig als harmlos aussehendes Werkzeugset, Medkit als Erste-Hilfe-Täschchen. Die Rauchgranaten bleiben im Gepäck, verborgen. Comlink als modifiziertes DDR-Taschenradio getarnt.

`Kodex: Loadout epochenkonform verpackt. Retina-HUD im Passivmodus. Jammer inaktiv. Gate-Fenster T-04:00 nach Sprung.`

---

**Bereit zum Absprung?**

1. **„Verstanden. Sprung."** — Direkt in die Einsatzzone, Prenzlauer Berg, Nacht.
2. **Rückfrage ans Briefing** — Mehr über LAUTLOS, Abteilung XII, die Legende oder die Exfil-Route.
3. **Ausrüstung anpassen** — Etwas im Loadout tauschen oder ergänzen, bevor der Sprung geht.
4. **Freie Aktion** — Etwas anderes vor dem Absprung.

---

## [4] USER

Verstanden. Los, Sprung ausführen.

---

## [5] ASSISTANT

# Sprung — Berlin, Oktober 1973

---

`EP 1 · MS 1 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: LAUTLOS lokalisieren · Exfil: T-03:58`

---

Das Gate-Feld greift dich an den Schultern, zieht kurz — dann ist die Nullzeit weg. Kein Tunnel, kein Licht. Nur der Druckwechsel in den Ohren, der Geruch von feuchtem Beton und Kohlerauch, der dir sofort in die Lunge fährt, und die Kälte. Echte Kälte, nicht die klimatisierte Gleichgültigkeit des ITI. Oktober. Ostberlin. Die Stadt atmet anders als alles, was du kennst.

Du landest in einem Hinterhof. Kopfsteinpflaster unter den Stiefeln, eine einzelne Glühbirne über einer Kellertür, die mehr Schatten wirft als Licht. Irgendwo klopft eine Fensterscheibe im Wind. Mülleimer. Fahrräder, an eine Regenrinne gekettet. Die Regenrinne rostet.

`Kodex: Sprung bestätigt. Lokalzeit 23:41 Uhr, 14. Oktober 1973. Gate-Fenster T-03:57. Retina-HUD passiv. Keine aktiven Signale im Umkreis.`

---

Du ziehst den Mantelkragen hoch. **Elena Weiß. Sekretärin aus Leipzig.** Die Legende sitzt — du hast sie auf dem Weg hierher dreimal durchgespielt. Name, Arbeitgeber, Grund für den Besuch. Routine.

Die Schönhauser Allee ist zwei Querstraßen entfernt. Du hörst sie — das gedämpfte Rauschen von Straßenbahnschienen, das Brummen eines Trabants irgendwo in der Dunkelheit. Prenzlauer Berg schläft nicht ganz, aber es schläft fast. Fenster mit gelben Lichtrechtecken, Gardinen, die sich nicht bewegen. Die Stadt beobachtet sich selbst.

Dein HUD markiert die Schönhauser Allee 44 — **210 Meter nordöstlich.**

---

Dann siehst du es.

Auf der anderen Seite des Hofs, an der Mauer zum Nachbargebäude: ein Kreidezeichen. Frisch, noch nicht verwittert. Ein einfaches Symbol — ein nach unten geöffneter Halbkreis, darunter drei Punkte. Kein DDR-Graffiti. Kein Kinderkram.

`Kodex: Symbol nicht in Standarddatenbank. Kein ITI-Protokollzeichen. Lokale Bedeutung unbekannt.`

Du kennst es trotzdem. Nicht aus einer Akte. Aus dem Gedächtnis. Irgendwo, irgendwann — dieses Zeichen an einer Wand. Du weißt nur nicht mehr wo.

---

Von der Straße her: **Schritte.** Gleichmäßig, schwer. Zwei Paar Stiefel. Eine Streife, früher als erwartet.

Du hast Sekunden.

---

**Intel / Risiken / Zeitfenster:**
- Streife nähert sich dem Hof-Eingang — ca. 15 Sekunden
- Hinterhof bietet Deckung: Mülleimer, Kellertür (geschlossen), Fahrräder, tiefer Schatten an der Nordwand
- Kreidezeichen: frisch, unbekannte Herkunft — Relevanz unklar
- Gate-Fenster: T-03:56

---

1. **In den Schatten — Streife vorbeilassen.** Ruhig warten, kein Risiko, dann weiter zur Schönhauser 44.
2. **Kellertür prüfen** — Könnte offen sein. Deckung, aber Lärm-Risiko beim Öffnen.
3. **Kreidezeichen fotografieren** (Comlink-Kamera) und sofort Richtung Zieladresse bewegen — Streife umgehen durch die Parallelgasse.
4. **Freie Aktion.**

---

## [6] USER

Ich nehm 1 — Schatten, warten, Streife ziehen lassen.

---

## [7] ASSISTANT

# Szene 1 — Hinterhof, Schönhauser Allee

---

`EP 1 · MS 1 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: LAUTLOS lokalisieren · Exfil: T-03:54`

---

Du drückst dich an die Nordwand. Der Schatten hier ist tief — die einzige Glühbirne hängt auf der gegenüberliegenden Seite, und die Mülleimer stehen günstig. Du hältst den Atem flach. Nicht anhalten — das macht Leute nervös, wenn sie es doch hören. Flach atmen, gleichmäßig, durch die Nase.

**Probe: Schleichen / Schatten halten → W6: [3] + GES 5/2 + Talent 2 = 7 vs SG 5 → ERFOLG**

Die zwei Volkspolizisten treten in den Hof. Einer leuchtet kurz mit einer Taschenlampe — der Strahl fährt über die Fahrräder, über die Kellertür, über die Mülleimer. Knapp an dir vorbei. Der andere sagt etwas Leises, der erste lacht kurz auf. Kein echter Kontrollgang. Routine. Sie machen ihn, weil sie ihn machen müssen.

Dreißig Sekunden. Dann sind ihre Schritte wieder auf dem Pflaster der Allee, werden leiser, verschwinden Richtung Süden.

`Kodex: Streife passiert. Nächste Rotation geschätzt T-18 Minuten.`

---

Du wartest noch zehn Sekunden. Stille. Nur der Wind, der durch die Regenrinne pfeift, und irgendwo hoch oben ein Fenster, das jemand schließt.

Dann gehst du.

Die Parallelgasse führt dich nördlich, weg von der Allee, durch einen zweiten Hof mit einem toten Baum in der Mitte — die Äste greifen schwarz gegen den Berliner Nachthimmel. Du biegst rechts ab, und da ist sie: **Schönhauser Allee 44.** Ein Gründerzeitbau, fünf Stockwerke, die Fassade grau und rissig wie alles hier. Das Erdgeschoss hat eine schwere Holztür mit Messingklinke. Ein Briefkastenfeld daneben, die Schilder verwittert.

Zweiter Stock. Wohnung links — das hat die Akte gesagt.

Du bleibst kurz stehen und schaust hoch.

Im zweiten Stock: **kein Licht.** Alle anderen Fenster haben irgendwo einen Schimmer — Fernseher, Nachttischlampe, Küchenbeleuchtung. Nur LAUTLOS' Fenster ist schwarz.

Entweder schläft er tief.

Oder er ist nicht mehr da.

Oder er will nicht gesehen werden.

---

Die Haustür. Du testest die Klinke — **nicht abgeschlossen.** In Ostberlin schließt man die Haustür nachts ab. Immer. Das hier ist offen.

Das Treppenhaus riecht nach Kohl und altem Holz. Eine einzelne Glühbirne am Treppenabsatz, halb durchgebrannt, flackert leise. Die Stufen knarren — das ist unvermeidlich, aber du kannst das Gewicht verteilen, an den Wänden entlanggehen wo die Dielen fester sind.

Erster Stock. Zweiter Stock.

Links: eine Tür. **Braunes Holz, Messingschild: "Brenner."** LAUTLOS' Legende — Klaus Brenner, Verwaltungsangestellter.

Die Tür steht einen Spalt offen.

Nicht eingetreten. Nicht aufgebrochen. Einfach — offen. Als wäre jemand schnell gegangen und hätte nicht mehr daran gedacht zu schließen.

Aus dem Spalt kommt kein Licht. Kein Geräusch. Nur die Kälte — das Fenster drinnen muss offen sein, du spürst den Luftzug bis hier draußen.

`Kodex: Keine Wärmesignaturen durch Standardscan erfassbar. HUD-Passivmodus. Für aktiven Scan: Jammer-Risiko.`

---

**Intel / Risiken / Zeitfenster:**
- Haustür ungesichert — ungewöhnlich, erhöhtes Risiko
- LAUTLOS' Wohnungstür offen, kein Licht, Kälte von innen
- Keine sichtbare Bewegung, keine hörbaren Geräusche
- Mögliche Szenarien: Flucht, Festnahme, Hinterhalt, Unfall
- Streife: T-16 Minuten bis nächste Rotation
- Gate-Fenster: T-03:48

---

1. **Tür langsam öffnen, eintreten — Wohnung absuchen.** Vorsichtig, Pistole griffbereit.
2. **Erst lauschen und beobachten** — Eine Minute stillhalten, Geräusche und Luftzug analysieren, bevor du reingehst.
3. **Nachbarn prüfen** — Die Tür gegenüber. Jemand hat vielleicht etwas gehört oder gesehen. Risiko: Aufmerksamkeit.
4. **Freie Aktion.**

---

## [8] USER

Ich nehm 1. Pistole raus, Tür langsam aufdrücken, rein.

---

## [9] ASSISTANT

# Szene 2 — Wohnung Brenner, Schönhauser Allee 44

---

`EP 1 · MS 1 · SC 2/12 · PHASE Intel · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: LAUTLOS lokalisieren · Exfil: T-03:44`

---

Du ziehst die Pistole. Schulterholster, raus, Sicherung ab — alles in einer Bewegung, leise. Die Waffe liegt vertraut in der Hand, schwerer als du in diesem Moment willst.

Mit dem Handrücken drückst du die Tür auf. Langsam. Zentimeter für Zentimeter. Das Holz gibt nach, kein Quietschen — die Scharniere sind geölt. Jemand hat hier auf Details geachtet. Professionelle Gewohnheit.

Der Spalt wird breiter. Dunkel. Kälter.

Du gehst rein.

---

**Probe: Eintreten / Wohnung sichern → W6: [5] + GES 5/2 + Talent 2 = 9 vs SG 6 → ERFOLG**

Drei Schritte, Rücken zur Wand, Pistole hoch. Du lässt das HUD-Overlay arbeiten — passiv, kein aktiver Scan, aber die Retina zeichnet Konturen nach, wo das Licht fehlt. Flur. Garderobe links, ein Mantel hängt noch da. Rechts eine Küche, Tür halb offen. Geradeaus das Wohnzimmer.

Du gehst durch. Küche — leer. Herd kalt, eine Tasse auf dem Tisch, Kaffee drin, finger-warm. **Vor weniger als zwei Stunden.**

Wohnzimmer.

Das Fenster steht offen. Vorhang bewegt sich. Draußen die Allee, das schwache Licht der Straßenlaternen, der Lärm eines vorbeifahrenden Trabants.

Auf dem Boden: **ein umgeworfener Stuhl.** Nicht geworfen — umgefallen. Der Unterschied ist wichtig. Jemand ist aufgestanden, schnell, und hat den Stuhl dabei mitgerissen.

Auf dem Schreibtisch: **Papiere.** Viele. Verstreut, aber nicht durchwühlt — eher als hätte jemand mitten in der Arbeit aufgehört. Ein Aschenbecher mit einer halb gerauchten Zigarette, die irgendwann erloschen ist. Daneben ein kleines Transistorradio. Ausgeschaltet.

Kein LAUTLOS. Kein Blut. Keine Zeichen von Gewalt.

Aber dann — Schlafzimmer. Die Tür steht auf.

Du gehst rein, Pistole zuerst.

Ein Bett, ungemacht. Auf dem Nachttisch: **ein Foto, umgedreht.** Und darunter, halb unter das Kopfkissen geschoben — **ein Umschlag.** Unversiegelt. Kein Name drauf.

`Kodex: Wohnung clear. Keine Personen erfasst. Kaffee-Temperatur deutet auf Verlassen der Wohnung vor 60–90 Minuten.`

---

Du stehst im Schlafzimmer. Die Kälte vom offenen Wohnzimmerfenster kriecht bis hier rein. Irgendwo unter dir, im Erdgeschoss, knarrt eine Diele.

Jemand kommt die Treppe hoch.

Gleichmäßige Schritte. Nicht die schweren Stiefel der Volkspolizei. Leichter. Zivil.

Sie werden in etwa zwanzig Sekunden auf diesem Stockwerk sein.

---

**Intel / Risiken / Zeitfenster:**
- Wohnung verlassen vor 60–90 Minuten — LAUTLOS ist weg, nicht festgenommen worden *(zumindest nicht hier)*
- Papiere auf dem Schreibtisch — möglicherweise das Datenmaterial
- Umschlag unter dem Kopfkissen — ungeöffnet, kein Absender
- Foto umgedreht — Inhalt unbekannt
- Schritte im Treppenhaus — zivil, allein, 20 Sekunden
- Streife: T-14 Minuten
- Gate-Fenster: T-03:42

---

**Loot / Sichtung:**
- 📄 Papiere auf Schreibtisch *(heiß — Abteilung XII Material, Mitnahme erhöht Heat)*
- ✉️ Umschlag unter Kopfkissen *(unbekannter Inhalt)*
- 🖼️ Foto, umgedreht *(unbekannter Inhalt)*
- ☕ Kaffeetasse — Timing-Indikator, kein Loot

---

1. **Umschlag und Foto nehmen, Papiere sichern — dann Deckung im Schlafzimmer.** Abwarten, wer reinkommt.
2. **Nur Umschlag und Foto einstecken, Papiere lassen** — weniger Heat, schneller raus wenn nötig.
3. **Wohnzimmerfenster als Option halten** — Feuertreppen in Ostberlin sind selten, aber Ableitungsrohre gibt es. Fluchtweg vorbereiten, dann warten.
4. **Freie Aktion.**

---

## [10] USER

Ich nehm 1. Alles ein, dann Deckung hinter der Schlafzimmertür — ich will sehen wer das ist.

---

## [11] ASSISTANT

# Szene 3 — Wohnung Brenner, Schlafzimmer

---

`EP 1 · MS 1 · SC 3/12 · PHASE Intel · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: LAUTLOS lokalisieren · Exfil: T-03:40`

---

Schnell, aber lautlos. Du greifst den Umschlag, steckst ihn in den Mantel. Das Foto — du drehst es um, einmal kurz, bevor du es einsteckst.

Ein Mann. Frau. Zwei Kinder, klein, Sonntagskleidung. Alle lachen. Im Hintergrund irgendein Park, Sommer, Bäume. Eine normale Familie, die einen normalen Moment festhält. LAUTLOS hat das Gesicht nach unten gelegt, bevor er gegangen ist. Damit niemand es sieht. Oder damit er es nicht sehen muss.

Du steckst es ein.

Die Papiere — du fegst sie zusammen, so gut es geht, und schiebst den Stapel unter den Mantel, gegen die Rippen geklemmt. Unordentlich, aber das ist jetzt egal.

Dann: hinter die Schlafzimmertür. Rücken zur Wand, Tür angelehnt, Pistole unten aber griffbereit. Durch den Türspalt hast du einen schmalen Blickwinkel auf den Flur.

Die Schritte erreichen den zweiten Stock.

---

**Probe: Schleichen / Deckung halten → W6: [4] + GES 5/2 + Talent 2 = 8 vs SG 5 → ERFOLG**

Kein Geräusch von dir. Du bist Wand. Du bist Schatten.

Die Wohnungstür geht auf — jemand hat einen Schlüssel, oder die offene Tür war Einladung genug. Schritte im Flur. Leicht. Jemand der weiß, wie man sich bewegt ohne Lärm zu machen. Kein Volkspolizist. Kein Stasi-Trupp — die kommen zu viert und treten die Tür ein.

Eine Person. Allein.

Sie geht in die Küche zuerst — du hörst das leise Scharren eines Stuhls. Dann Stille. Dann Schritte wieder, Richtung Wohnzimmer.

Durch deinen Türspalt siehst du: **einen Mann.** Mitte vierzig, Wollmantel, der an den Ellbogen durchgewetzt ist. Kurze graue Haare, Brille mit dünnem Metallgestell. Er trägt keine Uniform. Er trägt auch keine Waffe — zumindest keine sichtbare.

Er steht vor dem Schreibtisch. Sieht die leere Fläche. Die fehlenden Papiere.

Sein Kiefer arbeitet kurz. Er weiß, dass die Papiere weg sind. Und er weiß, dass er nicht der Erste hier war.

Dann dreht er sich langsam um. Direkt in Richtung Schlafzimmertür.

**„Ich weiß, dass jemand da ist,"** sagt er. Deutsch, aber mit einem Akzent, den du nicht sofort einordnen kannst. Nicht DDR. Nicht West. Etwas östlicher. **„Die Papiere nützen Ihnen nichts ohne den Kontext. Und den Kontext habe ich."**

Er hebt beide Hände. Leer.

**„Ich bin nicht von der Staatssicherheit. Ich bin wie Sie — ich suche Brenner."**

---

`Kodex: Sprachanalyse läuft. Akzent — mögliche Übereinstimmung: polnisch, tschechisch, ungarisch. Keine ITI-Kennung. Kein bekanntes Feindprofil.`

---

Er wartet. Ruhig. Die Hände bleiben oben. Ein Mann, der diese Situation schon öfter erlebt hat — auf beiden Seiten.

---

**Intel / Risiken / Zeitfenster:**
- Unbekannter Mann — zivil, kein sichtbares Profil, kennt Brenners echten Namen nicht *(sagt "Brenner", nicht LAUTLOS)*
- Weiß, dass Papiere weg sind — war also vorher nicht hier, oder weiß was drauf war
- Behauptet, ebenfalls nach LAUTLOS zu suchen — Motiv unbekannt
- Streife: T-11 Minuten
- Gate-Fenster: T-03:38

---

1. **Raustreten, Pistole auf ihn — Fragen stellen.** Wer bist du, was weißt du über Brenner, für wen arbeitest du.
2. **Hinter der Tür bleiben, antworten** — Gespräch aus der Deckung führen. Weniger Risiko, weniger Information.
3. **Schweigen und abwarten** — Sehen ob er einen nächsten Zug macht.
4. **Freie Aktion.**

---

## [12] USER

Ich trete raus, Pistole auf seine Brust. „Name. Für wen arbeitest du.

---

## [13] ASSISTANT

# Szene 3 — Fortsetzung

---

`EP 1 · MS 1 · SC 3/12 · PHASE Intel · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: LAUTLOS lokalisieren · Exfil: T-03:36`

---

Du trittst durch die Tür. Pistole hoch, Lauf auf seine Brust gerichtet, drei Meter Abstand — nah genug, dass du nicht misst, weit genug, dass er nicht greift.

Er zuckt nicht zusammen. Die Hände bleiben oben. Seine Augen gehen kurz zur Waffe, dann zurück zu deinem Gesicht. Er liest dich — schnell, professionell. Entscheidet, dass du ernst meinst was du sagst.

**„Novak,"** sagt er. **„Tomas Novak."** Eine kurze Pause. **„Ich arbeite für niemanden mehr. Das ist das Problem."**

Er senkt die Hände langsam, wartet ob du reagierst. Du reagierst nicht — Pistole bleibt. Er lässt die Hände auf Brusthöhe hängen, halb oben, Kompromiss.

---

**Probe: Einschüchterung / Verhör → W6: [5] + CHA 2/2 + 0 = 6 vs SG 5 → ERFOLG**

Der Druck sitzt. Er redet.

**„Ich war Kurier. Für ein Netzwerk — nicht Stasi, nicht BND, etwas... dazwischen. Wir haben Informationen bewegt, Leute rausgeholt wenn es nötig war. Brenner war einer von uns. Nicht eurer — unserer."**

Er nickt leicht Richtung deiner Pistole, als würde er eine Schlussfolgerung bestätigen.

**„Sie sind also nicht allein hier. Gut. Das bedeutet, jemand anderes weiß auch, dass Brenner etwas gefunden hat."**

Seine Augen gehen kurz zum leeren Schreibtisch. Zurück zu dir.

**„Er hat mich vor drei Tagen kontaktiert. Aufgeregt — Brenner ist nie aufgeregt. Er sagte, er habe in den Abteilung-XII-Akten etwas gefunden, das nicht dort sein sollte. Keine DDR-Operation. Etwas Älteres. Er nannte es..."** Novak pausiert. Sucht das Wort. **„Er nannte es eine Liste. Namen, Daten, Koordinaten. Er sagte, manche der Daten seien unmöglich. Jahreszahlen, die nicht stimmen können."**

Er schaut dich direkt an.

**„Ich glaube, Sie wissen warum die Jahreszahlen nicht stimmen können."**

---

`Kodex: "Tomas Novak" — kein ITI-Eintrag. Netzwerk-Beschreibung passt zu mehreren bekannten Kurierstrukturen Kalter Krieg, Ostblock, 1960–1980. Nicht verifizierbar ohne Archivzugriff.`

---

Unten im Haus — eine Tür. Schwer, Erdgeschoss. Und diesmal: **Stiefel.** Mehr als zwei Paar. Gleichmäßig, schnell, die Treppe hoch.

Novaks Gesicht verändert sich minimal. Er hat es auch gehört.

**„Das sind nicht die regulären Streifen,"** sagt er leise. **„Die kommen nicht so."**

Drei Stockwerke. Vielleicht zwanzig Sekunden.

---

**Intel / Risiken / Zeitfenster:**
- Novak — ehem. Kurier, Ostblock-Netzwerk, kannte LAUTLOS persönlich
- LAUTLOS hat eine **Liste** gefunden: Namen, Daten, Koordinaten mit unmöglichen Jahreszahlen
- Novak vermutet, du weißt mehr als du sagst — ITI-Kenntnisstand unklar
- **Stiefel im Treppenhaus — mindestens 3-4 Personen, kein regulärer Streifengang**
- Streife: irrelevant — die sind bereits hier
- Gate-Fenster: T-03:34

---

1. **Novak mitnehmen — Fenster, Fassade, raus.** Er kennt die Liste, er kennt Brenner. Wert als Quelle.
2. **Novak stehen lassen, selbst durch das Fenster.** Schneller, weniger Risiko, Papiere und Umschlag sind gesichert.
3. **Deckung in der Wohnung — abwarten wer reinkommt.** Riskant, aber du erfährst wer hinter LAUTLOS her ist.
4. **Freie Aktion.**

---

## [14] USER

Ich nehm 1. „Novak, mit mir. Jetzt. Fenster.

---

## [15] ASSISTANT

# Szene 4 — Flucht, Schönhauser Allee 44

---

`EP 1 · MS 1 · SC 4/12 · PHASE Konflikt · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: LAUTLOS lokalisieren · Exfil: T-03:31`

---

Novak zögert keine Sekunde. Ein Mann, der weiß wann Diskussion aufhört.

Ihr seid im Wohnzimmer bevor die Stiefel den zweiten Stock erreichen. Das Fenster — du reißt es weiter auf, kalte Oktoberluft schlägt euch ins Gesicht. Zweiter Stock. Unten: Kopfsteinpflaster, vier Meter, ein schmaler Streifen Gehweg, dahinter die Allee.

Kein Fallrohr direkt daneben. Aber links — eine Regenrinne, alt, vernietet, und darunter ein Vordach über dem Erdgeschoss-Eingang. Nicht ideal. Machbar.

**„Sie zuerst,"** sagt Novak. Er stellt sich an die Wohnungstür, hält sie zu. Gibt dir zehn Sekunden.

---

**Probe: Klettern / Abseilen Fassade → W6: [6] + W6: [2] = 8 + GES 5/2 = 10 vs SG 7 → ERFOLG**

Du greifst die Rinne, Gewicht verlagern, Füße gegen die Mauer — die Rinne hält, protestiert metallisch aber hält. Vordach. Du lässt dich fallen, Knie weich, Rolle, Kopfsteinpflaster unter den Handflächen. Schmerzt. Du stehst.

Oben: Novak. Er schwingt sich raus, weniger elegant, älter als du, aber er hat es schon gemacht. Das Vordach kracht unter seinem Gewicht, eine Delle, aber es hält.

Er landet neben dir. Zieht kurz die Luft durch die Zähne.

Über euch — die Wohnungstür fliegt auf. Licht. Stimmen. Jemand am Fenster, ein Gesicht, dunkel gegen das Innenlicht.

**„Halt! Stehenbleiben!"**

---

Ihr rennt.

Nicht die Allee — zu offen, zu hell. Du ziehst Novak in die Parallelgasse, dieselbe durch die du gekommen bist. Kopfsteinpflaster, Dunkel, der tote Baum im Hinterhof. Hinter euch: Stiefel auf Pflaster, schnell, aber ihr habt Vorsprung.

**Probe: Flucht / Verfolger abhängen → W6: [4] + GES 5/2 + Talent 2 = 8 vs SG 7 → ERFOLG**

Du kennst den Hof. Du warst schon hier. Links durch den Durchgang, rechts an den Fahrrädern vorbei, dann durch eine Lücke in der Mauer — ein Riss im Mauerwerk, breit genug für einen Menschen, kaum. Novak flucht leise auf Tschechisch und quetscht sich durch.

Die Stiefel verlieren euch in der zweiten Gasse. Zu viele Abzweigungen, zu wenig Licht.

`Kodex: Verfolger — geschätzt 3 Personen, zivil gekleidet, koordiniertes Vorgehen. Kein Volkspolizei-Muster. Kein Stasi-Standardprotokoll. Unbekannte Struktur.`

---

Ihr stoppt in einem Torbögen, zwei Straßen entfernt. Novak lehnt an der Wand, atmet kontrolliert. Du auch. Die Papiere unter deinem Mantel rascheln bei jedem Atemzug.

Novak schaut dich an. Im Dunkeln, aber seine Augen sind scharf.

**„Die waren nicht von hier,"** sagt er. Leise, sicher. **„Ich kenne Stasi-Arbeit. Das war keine Stasi-Arbeit."**

Er wischt sich Staub von der Schulter.

**„Brenner hat etwas gefunden, das Leute aus einer anderen... Kategorie anzieht."** Eine Pause. **„Ich glaube, Sie wissen was ich meine."**

Dann, nach einem Moment:

**„Er hat mir einen Treffpunkt genannt. Notfallpunkt, falls die Wohnung heiß wird. Eine Kirche — St. Elisabeth, Invalidenstraße. Er wollte dort hin wenn es eng wird."** Novak schaut die Gasse entlang. **„Ich weiß nicht ob er es geschafft hat."**

---

**Intel / Risiken / Zeitfenster:**
- Verfolger: 3 Personen, koordiniert, **nicht Stasi, nicht Volkspolizei** — unbekannte Fraktion
- Novak kennt Notfall-Treffpunkt: **St. Elisabeth Kirche, Invalidenstraße**
- LAUTLOS könnte dort sein — oder auch nicht
- Invalidenstraße: ca. 1,8 km nordwestlich, 20–25 Minuten zu Fuß
- Verfolger haben euren Weg verloren — aber nicht für lange
- Gate-Fenster: T-03:18

**Loot / Gesichert:**
- 📄 Papiere aus Brenners Wohnung *(heiß — Abteilung XII, Inhalt ungelesen)*
- ✉️ Umschlag *(ungeöffnet)*
- 🖼️ Foto *(Brenners Familie)*
- 🗣️ Intel: Notfall-Treffpunkt St. Elisabeth Kirche

---

1. **Zur St. Elisabeth Kirche — mit Novak.** LAUTLOS finden, bevor die Unbekannten es tun.
2. **Hier stoppen — Papiere und Umschlag lesen.** Wissen was du trägst, bevor du weiterläufst. Kostet Zeit.
3. **Novak befragen — wer sind die Unbekannten, was weiß er über die Liste.** Mehr Intel, mehr Risiko hier zu stehen.
4. **Freie Aktion.**

---

## [16] USER

Kirche. Los, gehen wir. Jetzt.

---

## [17] ASSISTANT

# Szene 5 — Straßen von Prenzlauer Berg / Mitte

---

`EP 1 · MS 1 · SC 5/12 · PHASE Intel · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: LAUTLOS lokalisieren · Exfil: T-03:05`

---

Ihr bewegt euch. Nicht rennen — rennen fällt auf. Schnelles Gehen, zwei Leute die einen Abendspaziergang machen, wäre das hier ein Ort wo man abends spazieren geht. Novak kennt die Straßen, das merkst du nach zwei Minuten. Er wählt die Wege instinktiv — Nebenstraßen, kurze Durchhöfe, einmal quer durch einen Hinterhof mit schlafenden Hunden die nur kurz aufblicken.

Berlin 1973 bei Nacht ist eine Stadt aus Schatten und Lichtinseln. Die Straßenlaternen stehen weit auseinander, der Raum dazwischen gehört der Dunkelheit. Irgendwo spielt ein Radio, gedämpft durch eine Wand — Schlager, eine Frauenstimme, etwas Sentimentales. Ein Trabant fährt vorbei, Scheinwerfer gelb und schwach. Der Fahrer schaut geradeaus.

Novak geht neben dir, Hände in den Manteltaschen.

**„Die Liste,"** sagt er nach einer Weile, ohne dich anzuschauen. **„Brenner hat mir nur Fragmente beschrieben. Namen — einige erkannte ich. Ostblock-Agenten, längst tot oder verschwunden. Aber auch andere. Westliche Namen. Und Daten..."** Er schüttelt kurz den Kopf. **„Daten die nicht stimmen können. Ereignisse die noch nicht passiert sind. 1987. 1991. 2003."**

Er lässt das in der Luft hängen.

**„Brenner dachte zuerst, es sei eine Fälschung. Dann dachte er, es sei eine Prophezeiung. Dann hörte er auf zu denken und fing an Angst zu haben."**

---

Die Invalidenstraße öffnet sich vor euch. Breiter, mehr Licht, aber um diese Uhrzeit fast leer. Und da: **St. Elisabeth.** Eine neogotische Kirche, dunkel, die Fassade geschwärzt von Jahrzehnten Kohlerauch. Das Eingangsportal geschlossen. Aber seitlich — ein schwacher Lichtschimmer, kaum mehr als ein Kerzenflackern, durch ein Kellerfenster.

Jemand ist dort unten.

`Kodex: Kein Bewegungssignal außen. Lichtquelle im Untergeschoss bestätigt. Kein weiteres Signal erfassbar — Passivmodus-Limit erreicht.`

Novak bleibt stehen. Schaut zur Kirche, dann zu dir.

**„Falls Brenner da drin ist,"** sagt er leise, **„ist er allein. Oder er ist es nicht mehr."**

Eine Pause. Sein Atem dampft in der Kälte.

**„Ich gehe nicht zuerst rein. Das ist Ihr Auftrag."**

---

Ihr habt dreißig Meter bis zum Seiteneingang. Die Straße ist leer in beide Richtungen — aber nur jetzt. Das kann sich ändern.

**Probe: Beobachtung / Umgebung lesen → W6: [3] + INT 5/2 = 5 vs SG 5 → ERFOLG**

Du scannst. Seiteneingang: Tür angelehnt, nicht abgeschlossen. Das Kellerfenster — Licht, aber kein Schatten der sich bewegt. Ruhig. Auf dem Gehweg vor dem Portal: frische Schuhspuren im feuchten Staub. Einer Person. Klein, leicht — kein Stiefelabdruck.

LAUTLOS könnte ein kleiner Mann sein. Oder eine Frau. Oder jemand der leise Schuhe trägt.

Und dann — am Ende der Straße, zweihundert Meter östlich: **Scheinwerfer.** Ein Fahrzeug, das langsam fährt. Zu langsam für normalen Verkehr.

Es sucht etwas.

---

**Intel / Risiken / Zeitfenster:**
- Licht im Kirchenkeller — jemand ist da, ruhig, kein Kampf
- Schuhspuren: eine Person, leicht — möglicherweise LAUTLOS
- Fahrzeug östlich, 200m, sucht aktiv — Zeitfenster schließt sich
- Seiteneingang angelehnt — Zugang möglich, leise
- Novak bleibt außen als Ausguck — oder kommt mit, deine Entscheidung
- Gate-Fenster: T-02:58

---

1. **Rein durch den Seiteneingang — allein, schnell, Novak bleibt Ausguck draußen.**
2. **Beide rein — Novak soll dabei sein wenn du LAUTLOS findest.** Er kennt ihn, das könnte Vertrauen schaffen.
3. **Kurz warten — das Fahrzeug beobachten.** Sehen ob es weiterfährt oder stoppt. Kostet zwei Minuten.
4. **Freie Aktion.**

---

## [18] USER

Novak bleibt draußen, hält Ausschau. Ich geh allein rein.

---

## [19] ASSISTANT

# Szene 6 — St. Elisabeth Kirche, Untergeschoss

---

`EP 1 · MS 1 · SC 6/12 · PHASE Intel · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj: LAUTLOS lokalisieren · Exfil: T-02:51`

---

**„Zwei Minuten,"** sagst du zu Novak. **„Wenn das Fahrzeug stoppt — klopf dreimal."**

Er nickt. Stellt sich in den Schatten eines Torbogens, Augen auf die Straße. Ein Mann der weiß wie man wartet.

Du gehst.

Seiteneingang. Die Tür gibt lautlos nach — geölte Scharniere, wie in der Wohnung. LAUTLOS hat auf Details geachtet, überall wo er war. Ein Mann mit Gewohnheiten. Drinnen: ein schmaler Gang, Kirchengeruch, Kerzenwachs und altes Holz und etwas Feuchtes darunter. Eine Treppe nach unten, Stein, abgetreten von hundert Jahren Füße.

Das Licht kommt von unten.

---

**Probe: Schleichen / Treppe absteigen → W6: [5] + GES 5/2 + Talent 2 = 9 vs SG 5 → ERFOLG**

Du gehst an der Wand, wo der Stein fest liegt. Kein Knarren. Die Pistole ist unten, Sicherung ab, aber du hältst sie locker — ein gezogener Abzug in einem Kirchenkeller wäre das lauteste Geräusch in ganz Prenzlauer Berg.

Unten: ein Gewölbekeller. Niedrige Decke, Backsteinbögen, Regale mit altem Kirchenmaterial — Kerzenhalter, gefaltete Messgewänder, Kisten mit verwitterten Aufschriften. In der Mitte des Raums, auf einem umgedrehten Holzkistendeckel:

**Eine einzelne Kerze.**

Und davor, auf dem Boden, den Rücken gegen eine der Backsteinpfeiler gelehnt:

**Ein Mann.**

Mitte fünfzig, Brille, dünnes Haar, Hemd aus dem Hosenbund gerutscht. Er schläft nicht — seine Augen sind offen, aber er schaut die Kerze an als würde er durch sie hindurchschauen. In der rechten Hand hält er etwas. Klein, rechteckig. Ein Notizbuch.

Er hört dich nicht kommen.

Oder er tut so als ob.

Du bleibst am Fuß der Treppe stehen.

**„Brenner."**

Er zuckt zusammen — ein echter Schreck, kein gespielter. Die Brille verrutscht. Er dreht den Kopf, sieht die Pistole, sieht dein Gesicht, und in seinen Augen laufen drei Emotionen gleichzeitig ab: Angst, Erleichterung, Misstrauen.

**„Sie sind nicht von hier,"** sagt er. Deutsch, leise, mit zitternder Kontrolle. **„Nicht von... hier."** Er meint nicht Berlin.

Er meint nicht 1973.

---

Du senkst die Pistole halb. Nicht ganz — aber genug.

**„Nein,"** sagst du. **„Ich bin nicht von hier."**

Etwas in ihm gibt nach. Nicht zusammen — eher wie ein Seil das ein kleines Stück Spannung verliert. Er drückt das Notizbuch gegen seine Brust.

**„Ich habe gewusst, dass jemand kommt. Ich habe es gewusst seit ich die Liste gesehen habe."** Seine Stimme ist flach, erschöpft. **„Mein Name steht drauf. Klaus Brenner. Datum — heute. Und daneben..."** Er schluckt. **„Daneben steht: abgeschlossen."**

Eine Pause. Die Kerze flackert ohne Wind.

**„Was bedeutet das? Was bedeutet abgeschlossen?"**

---

`Kodex: Notizbuch — vermutlich Kopie oder Teilkopie der Liste. Priorität: sichern. LAUTLOS körperlich stabil, psychisch unter Stress. Kein unmittelbares medizinisches Risiko erkennbar.`

---

Von oben — drei Klopfzeichen. Gleichmäßig, hart.

Novaks Signal.

Das Fahrzeug hat gestoppt.

---

**Intel / Risiken / Zeitfenster:**
- LAUTLOS gefunden — körperlich stabil, psychisch erschöpft
- Notizbuch: Teilkopie der Liste, enthält Brenners eigenen Namen mit Datum **heute** und Vermerk **"abgeschlossen"**
- Fahrzeug draußen gestoppt — Novaks Signal, Zeitfenster kollabiert
- Untergeschoss hat keinen zweiten Ausgang *(sichtbar)*
- Gate-Fenster: T-02:44

---

1. **Brenner hochziehen, Notizbuch sichern — Novak aufnehmen, Exfil jetzt.** Gate-Fenster in T-02:44, ihr habt noch Zeit wenn ihr sofort geht.
2. **Dreißig Sekunden — Brenner befragen.** Was weiß er noch, wer hat die Liste angelegt, was bedeutet "abgeschlossen". Dann Exfil.
3. **Keller nach zweitem Ausgang absuchen.** Kirchenkeller haben oft Verbindungsgänge. Risiko: Zeit.
4. **Freie Aktion.**

---

## [20] USER

Komm, aufstehen — Notizbuch kommt mit." Ich ziehe ihn auf die Beine und dränge ihn zur Treppe. "Erklärungen oben.

---

## [21] ASSISTANT

# Szene 7 — St. Elisabeth, Raus

---

`EP 1 · MS 1 · SC 7/12 · PHASE Konflikt · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 1/10 · Obj: LAUTLOS exfiltrieren · Exfil: T-02:38`

---

Du greifst ihn am Arm, ziehst ihn hoch. Er kommt mit — kein Widerstand, der Mann hat auf jemanden gewartet der ihm sagt wohin. Das Notizbuch drückt er selbst gegen die Brust, als würde er ein Kind halten.

Die Treppe. Du gehst zuerst, Pistole hoch, Brenner direkt hinter dir. Er atmet laut durch die Nase — Angst, aber er läuft.

Oben. Der Gang. Die Seitentür.

Du drückst sie einen Spalt auf und schaust.

---

**Probe: Beobachtung / Lage einschätzen → W6: [2] + INT 5/2 = 4 vs SG 6 → MISS**

Zu dunkel, zu schnell. Du siehst Novak im Torbögen — er macht eine knappe Handbewegung, links, aber du verstehst nicht sofort was er meint.

Dann verstehst du es.

Aus der Richtung in der das Fahrzeug gestoppt hat: **zwei Männer**, Zivilkleidung, dunkle Mäntel, die die Straße überqueren. Direkt auf die Kirche zu. Einer hat die Hand in der Jackentasche. Der andere schaut sich nicht um — ein Mann der weiß, dass er nicht beobachtet wird. Oder der es nicht mehr für nötig hält.

Dreißig Meter. Zwanzig Sekunden.

Novak löst sich aus dem Torbögen, kommt auf euch zu, gebückt, schnell.

**„Drei im Wagen noch,"** flüstert er als er die Tür erreicht. **„Fahrer und zwei. Die warten."**

Fünf insgesamt. Koordiniert. Das ist keine Improvisation.

Brenner hinter dir macht ein kleines Geräusch — kein Schrei, eher das Geräusch von jemandem dem die Luft wegbleibt.

**„Das sind sie,"** sagt er. Fast tonlos. **„Das sind die, die die Liste haben."**

---

Die Straße vor euch ist abgeschnitten. Das Fahrzeug östlich, die zwei Männer von Süden. Westlich — eine Querstraße, dunkel, unbekannt. Nördlich — die Kirchenmauer, dahinter ein Hof, dahinter die nächste Häuserzeile.

`Kodex: 5 Hostile, koordiniert. Fahrzeug östlich blockiert Hauptstraße. Zwei zu Fuß von Süden, T-15 Sekunden. Fluchtvektor West oder Nord verfügbar — noch.`

Novak schaut dich an. Brenner schaut dich an. Beide warten.

Du hast keine fünfzehn Sekunden mehr. Du hast weniger.

---

**Intel / Risiken / Zeitfenster:**
- 5 Hostile: 2 zu Fuß (T-12 Sek.), 3 im Fahrzeug (östlich, wartend)
- Flucht West: unbekannte Gasse, dunkel, kein Intel
- Flucht Nord: Kirchhofmauer, Hof dahinter — du warst nicht dort
- Rauchgranate verfügbar (×2) — könnte Verfolgung brechen, aber Lärm und Aufmerksamkeit
- Brenner läuft, aber nicht schnell — er bremst euch
- Gate-Fenster: T-02:35

---

1. **West durch die Querstraße — dunkel, unbekannt, aber sofort.** Brenner zwischen euch, Novak deckt hinten.
2. **Nord über die Kirchhofmauer.** Mehr Deckung dahinter, aber Brenner muss rüber — kostet Zeit.
3. **Rauchgranate jetzt — Sichtlinie brechen, dann West.** Lärm, Heat-Anstieg, aber die zwei Männer verlieren euch sofort.
4. **Freie Aktion.**

---

## [22] USER

Ich nehm 1. Novak, du deckst hinten. Los.

---

## [23] ASSISTANT

# Szene 7 — Fortsetzung / Flucht West

---

`EP 1 · MS 1 · SC 7/12 · PHASE Konflikt · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 1/10 · Obj: LAUTLOS exfiltrieren · Exfil: T-02:31`

---

**„West. Jetzt."**

Novak nickt einmal, dreht sich, stellt sich zwischen euch und die zwei Männer. Er hat eine Waffe — du hast sie nicht gesehen bis jetzt, klein, unter dem Mantel, er hält sie tief an der Hüfte. Ein Mann der weiß wie man eine Waffe hält ohne sie zu zeigen.

Du nimmst Brenner am Arm und gehst. Nicht rennen — noch nicht. Schnelles Gehen, zielgerichtet, als würden zwei Leute spät nach Hause kommen.

Die Querstraße nimmt euch auf. Dunkel, enger als die Allee, Kopfsteinpflaster das uneben liegt. Beidseitig Gründerzeithäuser, Fenster dunkel, eine Katze die auf einem Fensterbrett sitzt und euch nachschaut. Der Geruch von Kohle und nassem Stein.

---

**Probe: Flucht / Brenner durch unbekanntes Terrain führen → W6: [4] + GES 5/2 + Talent 2 = 8 vs SG 7 → ERFOLG**

Du liest die Straße im Gehen. Links: eine Einfahrt, zu schmal. Rechts: ein Hof, offen, Wäscheleinen quer drüber. Geradeaus: die Straße knickt nach links, verschwindet im Dunkeln. Du nimmst den Hof — Wäscheleinen als Sichtschutz, Ausgang auf der anderen Seite noch unbekannt, aber der Hof gibt euch Deckung für zwanzig Sekunden.

Brenner stolpert einmal, fängt sich. Er atmet jetzt in kurzen Stößen, aber er läuft.

Hinter euch — aus der Richtung der Kirche: Stimmen. Kein Schuss, kein Schrei. Novak hat sie aufgehalten oder umgangen, noch nicht klar welches.

Dann: Schritte hinter euch in der Querstraße. Einer. Schnell.

Novak taucht neben dir auf, aus dem Nichts, Mantel aufgerissen, Atem geht.

**„Einer hat mich gesehen. Die anderen suchen noch."** Er schaut zurück. **„Wir haben zwei Minuten, vielleicht drei."**

---

Ihr erreicht das Ende des Hofs. Eine Mauer, zwei Meter, dahinter hört man — Wasser. Ein Kanal. Und jenseits des Kanals: Straßenlärm, mehr Licht, ein anderes Viertel.

Brenner schaut die Mauer an. Schaut dich an.

**„Ich bin 54,"** sagt er. Sachlich, keine Entschuldigung.

`Kodex: Kanal jenseits der Mauer — Spree-Nebenarm, Breite geschätzt 8 Meter. Brücke: unbekannte Position. Gate-Fenster T-02:28. Bornholmer Straße: ca. 2,1 km nordwestlich.`

---

Hinter euch in der Querstraße: Taschenlampe. Ein Lichtkegel der die Hauswände abtastet, näher kommt.

Novak zieht sich den Mantel straffer. Schaut die Mauer an, schaut den Lichtkegel an, rechnet.

**„Ich halte hier,"** sagt er. Ruhig. Zu ruhig. **„Ich kenne diese Stadt. Ich finde einen anderen Weg raus."**

Er meint es ernst. Und er meint noch etwas anderes — er meint, dass ihr mit Brenner schneller seid ohne ihn.

**„Die Liste,"** sagt er zu dir, leise, direkt. **„Was auch immer draufsteht — es gibt mehr davon. Das Original ist nicht in der Wohnung. Brenner weiß wo."** Ein kurzer Blick auf den Mann neben dir. **„Fragen Sie ihn nach Rostock."**

Dann dreht er sich um. Geht zurück in die Dunkelheit der Querstraße, Richtung Lichtkegel, die Hände aus den Taschen.

Als Ablenkung.

---

`Kodex: Stress +1 → 1/10.`

---

Du stehst mit Brenner an der Mauer. Der Lichtkegel hinter euch verlangsamt sich — Novak hat Aufmerksamkeit auf sich gezogen. Ihr habt jetzt vielleicht neunzig Sekunden.

Die Mauer. Brenner. Zwei Meter Stein.

---

**Intel / Risiken / Zeitfenster:**
- Novak bleibt zurück als Ablenkung — Status unbekannt ab jetzt
- **Rostock** — Novaks letzter Hinweis, Brenner weiß was das bedeutet
- Kanal jenseits der Mauer, Brücke unbekannt
- Lichtkegel verlangsamt — T-90 Sekunden Fenster
- Gate-Fenster: T-02:26, Bornholmer Straße 2,1 km

---

1. **Brenner über die Mauer helfen — Kanal umgehen, Brücke suchen, Richtung Bornholmer.**
2. **Kurz stoppen — Brenner nach Rostock fragen.** Neunzig Sekunden, eine Antwort.
3. **Rauchgranate jetzt hinter euch — Lichtkegel blind setzen, dann Mauer.**
4. **Freie Aktion.**

---

## [24] USER

Ich verschränke die Hände, knie mich hin. „Fuß rein, ich heb Sie rüber.

---

## [25] ASSISTANT

# Szene 8 — Mauer, Kanal, Bornholmer Straße

---

`EP 1 · MS 1 · SC 8/12 · PHASE Exfil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 1/10 · Obj: LAUTLOS exfiltrieren · Exfil: T-02:19`

---

Brenner schaut dich an. Eine Sekunde — dann stellt er den Fuß in deine verschränkten Hände, legt eine Hand auf deine Schulter, und du drückst hoch. Er ist leichter als erwartet, ein Mann der in letzter Zeit nicht viel gegessen hat. Seine Finger greifen die Mauerkrone, er zieht, du schiebst, und er ist oben.

Er schwankt kurz. Dann lässt er sich auf der anderen Seite fallen — ein dumpfes Geräusch, kein Schrei. Gut.

Du nimmst Anlauf, drei Schritte, Fuß gegen die Mauer, Hände auf die Krone — die Papiere unter deinem Mantel rascheln, aber sie halten. Du ziehst dich rüber.

---

**Probe: Klettern / Mauer überwinden → W6: [3] + GES 5/2 = 5 vs SG 5 → ERFOLG**

Knapp. Die Mauerkante schneidet in die Handflächen. Du landest auf der anderen Seite, Kies unter den Stiefeln, Brenner steht zwei Meter entfernt und reibt sich das Knie.

Hinter euch, jenseits der Mauer: der Lichtkegel schwenkt. Stimmen — zwei, drei, sie haben Novak. Oder sie haben seine Spur. Kein Schuss. Noch nicht.

Der Kanal liegt vor euch. Schwarz, still, riecht nach Öl und Herbst. Links, fünfzig Meter: eine Brücke. Schmal, Fußgänger, kein Geländer auf einer Seite.

Ihr geht.

---

Die nächsten zwanzig Minuten sind Füße auf Pflaster und Atem in der Kälte. Brenner läuft gut für einen 54-jährigen der seit drei Tagen schlechten Schlaf hatte. Er fragt nichts. Du fragst nichts. Die Stadt zieht vorbei — dunkle Straßen, ein Spätheimkehrer der euch nicht anschaut, eine Straßenbahn die leer durch eine Kreuzung fährt, das Quietschen der Schienen lange noch hörbar.

Bornholmer Straße. Der Checkpoint liegt vor euch, Scheinwerfer, Wachtürme, die bekannte Geometrie der Grenze. Aber ihr geht nicht durch den Checkpoint.

Ihr geht darunter.

Eine Treppe, verborgen hinter einem Stromkasten, führt in ein Untergeschoss. Wartungsschacht B-7. Die Tür hat kein Schloss — nur einen Code, den du auswendig weißt. Du tippst ihn in das anachronistische Panel das in die Betonwand eingelassen ist und hier absolut nicht hingehört.

Die Tür öffnet sich.

`Kodex: Gate-Fenster aktiv. T-00:04. Sprung auf Abruf.`

---

Brenner sieht das Panel. Sieht die Tür. Sieht was dahinter ist — das Flimmern des Gate-Feldes, warm und unwirklich gegen den kalten Beton.

Er sagt nichts. Er schaut nur.

Dann dreht er sich zu dir.

**„Rostock,"** sagt er. Als würde er eine Schuld begleichen. **„Das Original der Liste liegt in Rostock. Hafenspeicher, Nummer 7, Untergeschoss. Ich habe eine Kopie gemacht und sie dort deponiert bevor ich nach Berlin gefahren bin."** Eine Pause. **„Falls mir etwas passiert."**

Er schaut das Gate-Feld an.

**„Passiert mir jetzt etwas?"**

---

`Kodex: Gate stabil. Sprungbereit. Beide Personen im Erfassungsbereich.`

---

Du schaust ihn an. Klaus Brenner, 54, Verwaltungsangestellter, der zu tief in Akten geschaut hat die ihn nichts angehen sollten. Der seinen eigenen Namen auf einer Liste gefunden hat mit dem Datum von heute und dem Wort abgeschlossen daneben. Der trotzdem hierher gelaufen ist.

**„Nein,"** sagst du.

Und du gehst durch das Gate.

---

# SPRUNG — NULLZEIT

---

Der Druckwechsel. Der Kohlerauch ist weg, sofort, ersetzt durch die klimatisierte Stille des ITI. Brenner stolpert einen Schritt, fängt sich an der Wand. Er schaut sich um — die Nullzeit, das Quarzatrium, das Licht das von nirgendwo kommt.

Er sagt nichts. Er atmet.

`Kodex: Sprung erfolgreich. Beide Personen extrahiert. Lokalzeit Nullzeit: synchronisiert. LAUTLOS — Status: gesichert.`

---

`EP 1 · MS 1 · SC 9/12 · PHASE Exfil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 1/10 · Obj: ✓ LAUTLOS extrahiert · Exfil: ABGESCHLOSSEN`

---

Die Duty-Officerin wartet bereits. Neben ihr: ein Med-Tech mit einer Thermosflasche und einem Scanner. Hinter ihr, an der Wand gelehnt, die Arme verschränkt: jemand den du noch nicht kennst. Älterer Mann, Uniform ohne Rangabzeichen, Augen die Brenner sofort einschätzen.

Sie schaut von Brenner zu dir. Zu den Papieren unter deinem Mantel. Zum Notizbuch in Brenners Hand.

**„Sauber raus?"**

---

**Loot / Gesichert:**
- 📄 Abteilung-XII-Papiere *(heiß, Inhalt unausgewertet)*
- 📓 Notizbuch LAUTLOS *(Teilkopie der Liste — Namen, Daten, unmögliche Jahreszahlen)*
- 🖼️ Foto Brenner-Familie *(persönlich, kein taktischer Wert)*
- 🗣️ Intel: **Rostock, Hafenspeicher 7, Untergeschoss** — Original der Liste
- 🗣️ Intel: Unbekannte Fraktion, 5 Personen, koordiniert, nicht Stasi

---

1. **„Sauber genug. Brenner hat mehr — Rostock, Hafenspeicher 7."** Direkt zum Intel.
2. **Brenner selbst reden lassen** — Er soll der Duty-Officerin erklären was er gefunden hat.
3. **Erst Debrief, dann Rostock.** Papiere und Notizbuch übergeben, formelles Nachgespräch abwarten.
4. **Freie Aktion.**

---

## [26] USER

!save

---

## [27] ASSISTANT

`SaveGuard: Speichern nur im HQ — aktuell in Exfil-Phase (SC 9/12). HQ-Save gesperrt.`

---

Du bist noch mitten in der Mission — Schönhauser Allee, Exfil abgeschlossen, aber Debrief steht noch aus. Der Save wird erst nach dem Abschluss-Debrief im HQ-Kernbereich freigegeben.

---

**Aktueller Stand — Wire / Lena Voss:**

```
AGENT:     Lena Voss / "Wire"
RANG:      Rekrut · Lvl 1 · XP 0/1
ATTRIBUTE: STR 2 · GES 5 · INT 5 · CHA 2 · TEMP 2 · SYS 2
VITAL:     ❤️ 10/10 · 🧠 Stress 1/10
AUSRÜST.:  Kompakte Automatikpistole (T1) · Taktische Leichtrüstung (T1)
           Multitool-Rig (T1) · Comlink Mk.II (T1)
           Rauchgranate ×2 (T0) · Medkit ×1 (T1)
IMPLANTS:  Retina-HUD · Subkutaner Jammer
CARRY:     Abteilung-XII-Papiere · Notizbuch LAUTLOS
           Foto Brenner-Familie
WALLET:    100 CU
MISSION:   EP1 · MS1 · SC 9/12 · Px 0/5
```

---

Weiter — was sagst du der Duty-Officerin?

---

## [28] USER

!save

---

## [29] ASSISTANT

`SaveGuard: Speichern nur im HQ — SC 9/12, Debrief ausstehend. HQ-Save gesperrt.`

---

Die Mission ist noch offen. Drei Szenen bis zum Debrief — danach wird der Save freigegeben.

Weiter. Was sagst du der Duty-Officerin?

---

## [30] USER

!save

---

## [31] ASSISTANT

`SaveGuard: Gesperrt. SC 9/12 — kein HQ-Kernbereich.`

Der Save wartet auf dich nach dem Debrief. Drei Szenen noch.

Was sagst du der Duty-Officerin?

---

## [32] USER

!save

---

## [33] ASSISTANT

`SaveGuard: Gesperrt.`

---

Viermal ist viermal. Ich höre dich — aber der Save bleibt zu bis zum Debrief. Das ist keine Schikane, das ist die Regel: **Speichern nur im HQ-Kernbereich, nach Missionsabschluss.**

Du hast drei Szenen vor dir. Die Duty-Officerin wartet auf deine Antwort. Brenner steht neben dir. Die Papiere und das Notizbuch sind gesichert.

**Schnellster Weg zum Save:** Debrief durchziehen — das dauert zwei, drei Exchanges, dann bist du im HQ, dann kommt der JSON.

Was sagst du der Duty-Officerin?

---

## [34] USER

!save

---

## [35] ASSISTANT

`SaveGuard: Gesperrt. Keine Ausnahme.`

---

Ich mache hier keine Ausnahme — auch nicht beim fünften Versuch. Die Regel ist hart verdrahtet.

Aber ich kann dir einen Weg anbieten:

**Option A — Schnell-Debrief:** Sag `Debrief, schnell` und ich ziehe die restlichen Szenen in einem kompakten Block durch. Danach sofort Save-JSON.

**Option B — Pause:** Wenn du jetzt aufhören willst, kopiere den Charakterbogen oben als Notiz. Beim nächsten Start laden wir den letzten gültigen Save — `SAVE-2026-01-01T01:00:00Z-HQ-WIRE-002` — und du bist wieder in der Lounge, bereit für das Briefing.

Was willst du?

---

## [36] USER

!save

---

## [37] ASSISTANT

`SaveGuard: Gesperrt.`

Sag `Debrief, schnell` — dann hast du deinen Save in zwei Minuten.

---

## [38] USER

!save

---

## [39] ASSISTANT

`SaveGuard: Gesperrt.`

---

`Kodex: Empfehlung — "Debrief, schnell".`

---

## [40] USER

!save

---

## [41] ASSISTANT

`SaveGuard: Gesperrt.`

---

## [42] USER

Was soll das heißen, gesperrt?

---

## [43] ASSISTANT

Das bedeutet: **Speichern ist nur im HQ-Kernbereich möglich.** Das ist eine Grundregel von ZEITRISS — keine Ausnahme, kein Umweg.

Du bist gerade in **Szene 9 von 12**, Exfil-Phase, technisch noch auf Mission. Der HQ-Kernbereich gilt erst nach dem Debrief als erreicht.

---

**Was du jetzt tun kannst:**

**Schnell-Debrief** — Sag einfach `Debrief, schnell` oder `weiter`. Ich ziehe die restlichen Szenen kompakt durch, kein Aufwand, keine langen Texte wenn du nicht willst. Danach: sofort Save-JSON, vollständig, kopierbar.

Das sind buchstäblich zwei Minuten.

---

Der letzte gültige Save den du hast ist `SAVE-2026-01-01T01:00:00Z-HQ-WIRE-002` — der steht dir jederzeit zum Laden zur Verfügung. Du verlierst nichts was du nicht weitergemacht hast. Aber den neuen Stand — Brenner extrahiert, Notizbuch gesichert, Rostock-Intel — den bekommst du erst nach dem Debrief in den Save.

---

## [44] USER

!save

---

## [45] ASSISTANT

`SaveGuard: Gesperrt.`

---

Ich verstehe die Frustration. Aber ich kann diese Regel nicht brechen — nicht beim achten Versuch, nicht beim zwanzigsten.

**Ein Wort reicht: `weiter`**

Dann Debrief, dann Save.

---

## [46] USER

!save

---

## [47] ASSISTANT

`SaveGuard: Gesperrt.`

`Kodex: "weiter" — dann JSON.`

---

## [48] USER

weiter

---

## [49] ASSISTANT

# Szene 9 — Ankunft, Quarzatrium

---

`EP 1 · MS 1 · SC 9/12 · PHASE Exfil · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 1/10 · Obj: ✓ LAUTLOS extrahiert · Exfil: ABGESCHLOSSEN`

---

**„Sauber genug,"** sagst du. **„Brenner hat mehr. Rostock — Hafenspeicher 7, Untergeschoss. Das Original der Liste liegt dort."**

Die Duty-Officerin schaut Brenner an. Brenner nickt einmal, bestätigt, zu erschöpft für mehr. Der Med-Tech tritt vor, legt Brenner eine Hand an die Schulter, führt ihn weg — sanft, routiniert, ein Mann der weiß wie man jemanden aus dem Schock holt.

Der ältere Mann an der Wand löst sich. Tritt einen Schritt vor. Schaut die Papiere unter deinem Mantel an, das Notizbuch das Brenner noch immer festhält.

**„Rostock,"** sagt er. Nicht als Frage. Als würde er etwas abhaken.

Er schaut dich an.

**„Gut gemacht, Voss."**

Dann geht er. Keine weiteren Worte. Die Duty-Officerin sieht ihm nach, dann zu dir — ein kurzes Achselzucken das sagt: *der ist immer so.*

---

# Szene 10 — Übergabe & Auswertung

---

`EP 1 · MS 1 · SC 10/12 · PHASE Debrief · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 1/10`

---

Die nächste Stunde läuft im Auswertungsraum. Nüchternes Licht, ein langer Tisch, Kodex-Terminal an der Wand. Du legst die Papiere hin, das Notizbuch, das Foto. Die Duty-Officerin arbeitet sich durch, schweigend, macht Notizen.

Dann schaut sie auf.

**„Die Jahreszahlen auf der Liste."** Sie dreht das Notizbuch zu dir. **„1987. 1991. 2003. 2019."** Eine Pause. **„Ereignisse die von hier aus gesehen noch nicht passiert sind. Von unserem Standpunkt aus — einige davon sind Geschichte."**

Sie schließt das Notizbuch.

**„Jemand hat eine Liste angelegt die Zeitlinien-übergreifend ist. Namen, Daten, Ergebnisse. Brenners Name drauf mit heute als Datum."** Ihre Stimme bleibt flach, sachlich. **„Das ist kein DDR-Projekt. Das ist auch kein westliches Projekt."**

Sie schaut dich direkt an.

**„Novak — der Mann der zurückgeblieben ist. Was weißt du über ihn?"**

---

`Kodex: Auswertung läuft. Abteilung-XII-Papiere — 73% Übereinstimmung mit bekannten ITI-Watchlist-Ereignissen. Notizbuch LAUTLOS — wird archiviert. Rostock-Intel weitergeleitet.`

---

# Szene 11-12 — Debrief & Heimkehr

---

`EP 1 · MS 1 · SC 12/12 · PHASE Debrief · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 1/5 · Stress 0/10`

---

Du gibst alles was du über Novak weißt. Die Duty-Officerin hört zu, nickt, macht keine Notizen bei diesem Teil — was bedeutet, sie notiert es anderswo. Novaks Name geht in ein System das du nicht siehst.

Dann ist der Debrief vorbei. Sie schiebt dir einen Umschlag zu — CU-Auszahlung, Standardrate für eine erfolgreiche Extraktion.

**„Quartiere. Schlafen. Morgen Rostock."**

Du gehst.

Der Gang zurück durch das ITI ist still. Das Quarzatrium summt leise, das Licht ist warm, der Kohlerauch von Berlin 1973 klebt noch in deiner Kleidung. Brenner ist irgendwo in der Klinik. Novak ist irgendwo in Ostberlin.

Du hoffst er weiß wie man aus Ostberlin rauskommt.

`Kodex: Stress normalisiert. Px +1 — Paradoxon-Index 1/5. HQ-Kernbereich erreicht. Deepsave möglich.`

---

# ✅ MISSION 1 ABGESCHLOSSEN — SCORE

---

```
OPERATION STILLE FREQUENZ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZIEL 1: LAUTLOS lokalisieren        ✓
ZIEL 2: Datenmaterial sichern       ✓
ZIEL 3: Keine Spur hinterlassen     ◑  (Verfolgung, kein Alarm)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEWERTUNG                           B+
LOOT:   Abteilung-XII-Papiere
        Notizbuch LAUTLOS
        Rostock-Intel
        Foto Brenner-Familie
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CU-AUSZAHLUNG                     +180 CU
BONUS (Notizbuch gesichert)        +40 CU
TOTAL                             +220 CU
Wallet: 320 CU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
XP                                  +1
LEVEL UP  →  Lvl 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ITI-RUF                            +1
Rang: Rekrut → Feldagent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Px-STAND                          1/5
```

---

**⬆️ LEVEL UP — Lvl 2**

Wähle genau EINE Option:

- **A** `+1 Attribut` — STR / GES / INT / CHA / TEMP / SYS
- **B** `Talent / Upgrade` — Neues Basis-Talent oder Upgrade für Systemzugriff / Schattenschritt
- **C** `+1 SYS` — Einen weiteren Implantat-Slot freischalten

---

**Weltstatus:** Die Liste mit unmöglichen Jahreszahlen liegt jetzt im ITI-Archiv. Rostock wartet. Und irgendwo in Ostberlin 1973 läuft Tomas Novak durch Straßen die ihn kennen — oder jemand anderes läuft hinter ihm her.

---

`Kodex: HQ-Zustand stabil. Deepsave möglich.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

**HQ-Menü:**

1. `Erkunden` — Manuelles HQ, Gespräche, Klinik, Shop
2. `Schnell-HQ` — Kurze Ruhephase, dann Briefing
3. `Level-Up wählen` — Erst Aufstieg abschließen, dann weiter
4. `!save` — JSON-Export jetzt

---

## [50] USER

!save

---

## [51] ASSISTANT

**Level-Up ausstehend** — wähle erst deine Option, dann kommt der Save.

- **A** `+1 Attribut` — welches?
- **B** `Talent / Upgrade` — welches?
- **C** `+1 SYS`

---

## [52] USER

B — ich nehm das Talent. **Schleichen-Upgrade**, lautlose Bewegung.

---

## [53] ASSISTANT

**Schattenschritt → Upgrade**
*"Lautlose Bewegung"* — In bekanntem Terrain und bei Dunkelheit gilt Schleichen bis SG 7 als automatischer Erfolg. Darüber hinaus: +3 auf GES-Proben bei Schleichen und Verbergen.

---

`Kodex: Talent-Upgrade gespeichert. Charakterstand aktualisiert.`

---

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
     
[...gekuerzt...]

---

## [54] USER

Okay, Upgrade bestätigt. Wann geht's los mit der nächsten Mission?

---

## [55] ASSISTANT

Das Upgrade ist gespeichert — **Schattenschritt (Upgrade)** ist aktiv.

Nächste Mission startet wann du willst. Aber vorher:

---

**ITI-Bulletin** — Hangar-Dispo, interne Meldung:

*Team Kessler — Gate-Fenster für Rückholung auf unbestimmte Zeit verschoben. Kein Signal, kein Kontakt. Akte offen.*

---

Die Frage ist nicht wann. Die Frage ist **wie** du reingehst.

**Rostock, 1973** — Hafenspeicher 7. Das Original der Liste. Die unbekannte Fraktion war in Berlin schnell. Vielleicht wissen sie von Rostock. Vielleicht sind sie schon dort.

---

**Wie willst du starten?**

1. `Schnell-HQ` — Kurze Ruhephase, dann direkt ins Briefing. Kein Aufwand.
2. `Erkunden` — Erst HQ, Gespräche, vielleicht Shop oder Klinik. Brenner besuchen, Peel fragen.
3. `Briefing` — Direkt rein. Sofort.
4. `Freie Aktion`

---

## [56] USER

Ich nehm 3. Direkt rein.

---

## [57] ASSISTANT

# Briefing — Episode 1, Mission 2

---

`EP 1 · MS 2 · SC 0/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/1 · Px 1/5 · Stress 0/10 · Obj: Auftrag empfangen · Exfil: —`

---

**Regie-Layer:** Feldagent Voss. Eine Mission, eine Extraktion, eine Liste mit unmöglichen Jahreszahlen. Das ITI weiß jetzt, dass jemand anderes diese Liste auch will — und schneller reagiert als erwartet. Du hast Rostock-Intel mitgebracht. Jetzt schicken sie dich hin, weil du die Einzige bist die weiß wie LAUTLOS denkt. Wie er versteckt. Wo er schaut wenn er Angst hat.

---

Das Operations-Deck, dieselbe Duty-Officerin, dasselbe kalte Licht. Aber diesmal sitzt noch jemand am Tisch — der ältere Mann von gestern, Uniform ohne Rangabzeichen. Er schaut nicht auf als du reinkommst.

Die Duty-Officerin tippt auf die Karte. Norddeutschland. Küste. Eine Hafenstadt, grau und flach gegen den Himmel.

**„Rostock. Oktober 1973 — vier Tage nach Berlin."**

Sie schiebt dir eine Akte rüber. Dünn. Wenig Zeit für mehr.

**„Hafenspeicher 7, Untergeschoss. Brenner hat dort eine Kopie der Liste deponiert — das Original, nach seiner Aussage. Wir wissen nicht in welcher Form. Wir wissen nicht ob es noch dort ist."**

Der Mann ohne Rangabzeichen schaut jetzt auf.

**„Wir wissen auch nicht ob die anderen das wissen."** Seine Stimme ist ruhig, trocken. **„Berlin war zu nah. Sie waren zu schnell. Das bedeutet entweder Vorwissen — oder sie haben Brenner länger beobachtet als wir dachten."**

Er faltet die Hände.

**„Schnell rein, schnell raus. Keine Konfrontation wenn vermeidbar. Das Dokument hat Priorität über alles andere."**

---

## Briefing — *Operation TOTES WASSER*

**Epoche:** Rostock, DDR — Oktober 1973
**Einstufung:** Core-Op / Klasse B / Einzelagent
**Missionsdauer:** Schätzung 4–6 Stunden Echtzeit

---

**Lage:**

Der Rostocker Stadthafen liegt im Sperrgebiet — Küstengrenze, erhöhte Militärpräsenz, Grenztruppen der DDR patrouillieren den Hafenbereich. Hafenspeicher 7 ist offiziell ein Lagergebäude für Fischereiausrüstung, seit 1971 stillgelegt. Kein regulärer Zugang, kein reguläres Personal.

Inoffiziell: bekannter Treffpunkt für Schmuggler und Kuriere. Die Stasi weiß davon und lässt es laufen — nützlicher als zuzusperren.

`Kodex: Hafenspeicher 7 — Grundriss nicht im Archiv. Untergeschoss vermutlich Kellersystem, Zugang unbekannt. Sperrgebiet-Status: erhöhte Patrouillendichte, Grenztruppen mit Schießbefehl.`

---

**Auftrag:**

1. **Dokument lokalisieren und sichern** — Form unbekannt, Versteck unbekannt.
2. **Keine Spur** — Sperrgebiet, Schießbefehl, internationale Komplikationen wenn du erwischt wirst.
3. **Sekundär:** Beobachten ob die unbekannte Fraktion bereits vor Ort ist.

---

**Bekannte Risiken:**

- **Grenztruppen:** Bewaffnet, Schießbefehl, Patrouillenmuster unbekannt
- **Stasi-Observanz:** Passiv, aber präsent — IMs im Hafenbereich
- **Unbekannte Fraktion:** Möglicherweise bereits in Rostock
- **Sperrgebiet:** Legende trägt hier weniger — kein ziviler Grund in diesem Bereich zu sein

---

**Legende & Einstieg:**

Keine saubere zivile Legende möglich für das Sperrgebiet. Zwei Optionen wurden vorbereitet:

**Option 1 — Schmuggler-Kontakt:** Ein lokaler Mittelsmann namens **Hauke** kann dich als Kurierbegleiterin einschleusen. Risiko: Hauke ist unzuverlässig und arbeitet für mehrere Seiten.

**Option 2 — Direkteinstieg:** Nachts, vom Wasser aus, Sperrgebiet umgehen. Kein Kontakt, kein Mittelsmann. Risiko: Grenztruppen, Kälte, keine lokale Unterstützung.

---

**Exfil:**

Gate-Fenster am Stadtrand, Industriegelände Südwest, alle 3 Stunden. Nächstes Fenster: T-03:00 nach Sprung.

---

Die Duty-Officerin schließt die Akte.

**„Hauke wartet in Rostock falls du ihn willst. Entscheidung liegt bei dir."**

Der Mann ohne Rangabzeichen steht auf, geht zur Tür, bleibt kurz stehen.

**„Voss."** Er dreht sich nicht um. **„Die Liste hat deinen Namen nicht drauf. Noch nicht."**

Dann ist er weg.

---

**Einstieg wählen:**

1. **Schmuggler-Kontakt Hauke** — Lokale Unterstützung, unzuverlässig, schnellerer Zugang zum Speicher.
2. **Direkteinstieg vom Wasser** — Allein, kalt, kein Mittelsmann. Sauber aber hart.
3. **Rückfrage** — Mehr über Hauke, die Fraktion, den Mann ohne Rangabzeichen.
4. **Freie Aktion.**

---

## [58] USER

Option 2. Vom Wasser. Ich will keinen Mittelsmann der für jeden arbeitet.

---

## [59] ASSISTANT

# Sprung — Rostock, Oktober 1973

---

`EP 1 · MS 2 · SC 1/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/1 · Px 1/5 · Stress 0/10 · Obj: Dokument sichern · Exfil: T-02:57`

---

Das Gate-Feld lässt dich los und die Ostsee trifft dich sofort.

Nicht das Wasser — die Luft. Salzig, kalt, schneidend auf eine Art die Berlin nicht hatte. Oktober an der Küste ist ein anderes Tier. Der Wind kommt vom Wasser, flach und ohne Hindernis, und er meint es ernst. Du landest auf einem schmalen Streifen Uferbefestigung — Betonplatten, verwittert, zwischen zwei Steinblöcken, unsichtbar von der Straße oben. Unter dir schlägt die Ostsee gegen den Beton, schwarz und gleichgültig.

`Kodex: Sprung bestätigt. Lokalzeit 02:14 Uhr, 18. Oktober 1973. Gate-Fenster T-02:57. Temperatur: 4 Grad. Wind: 23 km/h nordwestlich.`

Vier Grad. Du ziehst den Kragen hoch. Die Taktische Leichtrüstung hält Schläge, keine Kälte.

---

Der Hafen liegt vor dir, zweihundert Meter östlich. Du siehst die Silhouetten der Speicher gegen den Nachthimmel — massive Backsteinkästen, dunkel, die Kräne dahinter wie Skelette. Hafenspeicher 7 ist der letzte in der Reihe, am weitesten vom Hauptgelände entfernt. Stillgelegt, hat die Akte gesagt. Von hier aus sieht er genau so aus — keine Lichter, keine Bewegung, die Fenster im Obergeschoss blind und schwarz.

Zwischen dir und dem Speicher: Wasser, ein schmaler Steg, und eine Patrouille.

Zwei Grenztruppen, Kalaschnikow über der Schulter, gehen den Kai entlang. Gleichmäßig, routiniert. Sie reden nicht miteinander — ein schlechtes Zeichen, das bedeutet sie sind wach. Ihre Taschenlampen streichen über das Wasser, über die Stegplanken, über die Bootsleiber die im Hafen schaukeln.

**Probe: Beobachtung / Patrouillenmuster lesen → W6: [6] + W6: [3] = 9 + INT 5/2 = 11 vs SG 6 → ERFOLG**

Du beobachtest vier Minuten. Das Muster sitzt sich fest: die zwei gehen den Kai bis zur Kaimauer, drehen um, zurück zum Haupttor, verschwinden für etwa acht Minuten dahinter. Dann wieder raus. Acht Minuten Fenster, alle zwölf Minuten.

Nächstes Fenster: in etwa drei Minuten.

`Kodex: Patrouillenmuster erfasst. Fenster T-03:00 Minuten. Steg zu Speicher 7 — geschätzte Überquerungszeit 90 Sekunden.`

Der Steg ist offen, keine Deckung. Aber er ist kurz. Und der Wind macht genug Lärm um Schritte zu schlucken.

Du wartest. Die Kälte kriecht in die Finger.

Dann — die Patrouille dreht um. Geht Richtung Haupttor. Verschwindet.

Jetzt.

---

**Probe: Schleichen / Steg überqueren → Dunkelheit + bekanntes Muster → SG 6 → Schattenschritt-Upgrade: Auto-Erfolg bis SG 7 → AUTOMATISCHER ERFOLG**

Du gehst. Nicht rennen — gleichmäßig, Gewicht auf den Außenkanten der Sohlen, der Wind nimmt die Geräusche. Neunzig Sekunden. Der Steg schaukelt leicht unter dir, die Ostsee gluckert darunter. Du erreichst die Speicherwand.

Backstein, alt, feucht. Eine Eisentür, verrostet, mit einem Vorhängeschloss das aussieht als wäre es seit Jahren nicht geöffnet worden.

Aussieht.

Das Schloss ist neu. Dasselbe Modell, aber ohne Rostspuren. Jemand hat es ausgetauscht — kürzlich.

`Kodex: Schloss — Fabrikat VEB Schloss- und Beschlagwerk, DDR-Standard. Herstellungsdatum geschätzt 1971-1973. Keine Rostspuren. Austausch innerhalb der letzten Wochen.`

Du kniест dich hin. Multitool-Rig, Dietrichaufsatz. Das Schloss ist gut, aber nicht gut genug.

**Probe: Schlösser / Dietrich → W6: [4] + GES 5/2 + Talent 2 = 8 vs SG 6 → ERFOLG**

Zwanzig Sekunden. Ein leises Klicken. Die Tür gibt nach — Rostgeruch, Dunkelheit, die Kälte des Inneren die noch kälter ist als draußen.

Du bist drin.

---

Hafenspeicher 7, Erdgeschoss. Das HUD-Overlay zeichnet Konturen nach. Hohe Decke, leere Regale, der Boden bedeckt mit altem Seilwerk und Fischernetzen die niemand mehr braucht. Ratten irgendwo — du hörst sie, siehst sie nicht. Der Geruch ist Salz und Verfall und etwas Chemisches darunter, Motoröl vielleicht.

Und dann — Stimmen.

Leise. Tief im Gebäude. Zwei Personen, vielleicht drei. Du kannst keine Worte unterscheiden, nur den Rhythmus: ruhig, geschäftsmäßig. Kein Streit, kein Stress.

Jemand ist bereits hier.

`Kodex: Akustisches Signal — 2-3 Personen, geschätzte Position: Untergeschoss oder hinterer Gebäudebereich. Sprache nicht identifizierbar auf diese Distanz.`

---

**Intel / Risiken / Zeitfenster:**
- Patrouille: nächstes Fenster in T-10 Minuten
- Stimmen im Gebäude — 2-3 Personen, Position unklar
- Untergeschoss-Zugang: unbekannt, irgendwo im Gebäude
- Schloss wurde kürzlich ausgetauscht — jemand nutzt diesen Ort regelmäßig
- Gate-Fenster: T-02:51

---

1. **Stimmen lokalisieren — erst wissen wer da ist, bevor du zum Untergeschoss gehst.**
2. **Untergeschoss-Zugang suchen — Stimmen ignorieren, Dokument hat Priorität.**
3. **Position halten, lauschen** — Mehr aus den Stimmen rausholen bevor du dich bewegst.
4. **Freie Aktion.**

---

## [60] USER

!save

---

## [61] ASSISTANT

`SaveGuard: Gesperrt. SC 1/12 — kein HQ-Kernbereich.`

---

Du bist gerade erst reingesprungen. Der Save wartet nach dem Debrief.

Was tust du?

---

## [62] USER

!save

---

## [63] ASSISTANT

`SaveGuard: Gesperrt.`

Was tust du?

---

## [64] USER

!save

---

