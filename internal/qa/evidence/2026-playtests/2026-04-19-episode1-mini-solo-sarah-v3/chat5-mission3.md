# chat5-mission3

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

# ZEITRISS — Spiel geladen

`Kodex: Save WIRE-003 verifiziert. Branch ANCHOR-main. Charakterstand v7 sauber. Willkommen zurück, Wire.`

---

## Letzter bekannter Stand

**Lena "Wire" Voss · Feldagent · Lvl 2 · Episode 1**

Mission 1 abgeschlossen. LAUTLOS — Klaus Brenner — sitzt in der ITI-Klinik, blass und leichter als vorher. Das Notizbuch liegt im Quartier-Stash. Die Abteilung-XII-Papiere brennen dir noch immer im Carry — heißes Material, das du noch nicht losgeworden bist.

Novak ist irgendwo in Berlin 1973. Status: unbekannt. Das Wort sitzt wie ein Splitter.

Die Liste hat Namen aus vier Jahrzehnten. Rostock wartet.

---

## HQ · Zero Time Lounge / Quartiere

`EP 1 · MS 1 ✓ · HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10`

Die Nullzeit hat ihre eigene Stille — keine Uhr, kein Wetter, kein Morgen. Der Korridor zu deinen Quartieren riecht nach Maschinenöl und dem schwachen Ozon der Gate-Anlage. Irgendwo tiefer im ITI läuft ein Kompressor, gleichmäßig, fast beruhigend.

Du bist zurück. Für jetzt.

`Kodex: ITI-Ruf 1 bestätigt. Lizenz Tier I aktiv. Nächste Stufe: Core-Boss-Abschluss.`

---

**Weltstatus — EP1-Lage:**
Die unbekannte Fraktion war schnell in Berlin. Fünf Personen, koordiniert, kein bekanntes Profil. Wenn sie wissen, dass LAUTLOS weg ist — und das wissen sie — dann wissen sie auch, dass jemand ihn geholt hat. Die Uhr läuft. Rostock, Hafenspeicher 7, ist noch nicht kompromittiert. Noch nicht.

---

## HQ-Menü

Was tust du?

1. **Zero Time Lounge** — Peel steht hinter der Bar. Und du hast ihm noch nicht geantwortet.
2. **ITI-Klinik** — Brenner liegt dort. Vielleicht redet er jetzt mehr als in Berlin.
3. **Operations-Deck / Briefing** — Mission 2. Rostock wartet nicht ewig.
4. **`!save`** — Deepsave vor dem nächsten Sprung.

> *Freie Aktion — Quartiere, Kodex-Archiv, Ausrüstung checken, oder etwas anderes?*

---

## [2] USER

Briefing - naechste Mission bitte

---

## [3] ASSISTANT

`EP 1 · MS 2 · SC 0/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj — · Exfil —`

---

## Operations-Deck · Briefingraum 3

**Regie-Layer:** Brenners Extraktion hat das ITI auf eine Spur gesetzt, die älter ist als erwartet. Du hast die Papiere rausgebracht. Jetzt schicken sie dich nach dem Original.

---

Der Briefingraum ist klein und funktional — eine Tischprojektion, zwei Stühle, eine Kaffeetasse die jemand vergessen hat. Der Projektor wirft blasses Licht auf die Wand: Küstenlinie, Kräne, Wasser.

Duty-Officer Maren Steig lehnt gegen den Tisch, Arme verschränkt, Blick auf die Karte. Mitte dreißig, kurze graue Strähne über der rechten Schläfe, Stimme wie jemand der Befehle lieber als Feststellungen formuliert.

*„Voss."* Sie tippt einmal auf die Projektion. Die Küstenlinie zoomt rein. Rostock. Hafen. Ein rechteckiger Speicherbau, Pier 7, Untergeschoss markiert mit einem roten Punkt. *„Du kennst das Ziel bereits. Das Original der Liste liegt dort — oder lag dort, Stand gestern Abend laut unserer Quelle. Eine Frau namens Ilse Hartmann, Hafenverwaltung, hat vor drei Tagen ungewöhnliche Aktivität im Untergeschoss gemeldet und ist seitdem nicht mehr zur Arbeit erschienen."*

Sie lässt das kurz in der Luft hängen.

*„Wir wissen nicht, ob die Fraktion das Dokument noch dort hat, ob sie es bereits verlagert hat — oder ob Hartmann einfach krank ist."* Ein zweiter Tipp. Das Foto einer Frau, Mitte fünfzig, Verwaltungsbrille, Gesicht wie jemand der nie lügt und deshalb gefährlich ist. *„Wir wollen das Original. Wir wollen wissen, wer das Untergeschoss nutzt. Und wir wollen Hartmann — lebend, wenn möglich. Sie hat etwas gesehen."*

Steig richtet sich auf.

*„Datum: 17. Oktober 1973. Drei Tage nach Berlin. Die Fraktion hat noch keine Zeit gehabt, alles zu räumen — wenn sie überhaupt weiß, dass wir kommen."*

---

## Intel / Risiken / Zeitfenster

- **Ziel:** Original der Liste sichern · Hafenspeicher 7, Untergeschoss, Rostock 17.10.1973
- **Sekundär:** Ilse Hartmann lokalisieren — lebendig bevorzugt
- **Sekundär:** Identität/Struktur der unbekannten Fraktion klären
- **Risiko:** Fraktion möglicherweise noch vor Ort — 5+ Personen, koordiniert, bewaffnet
- **Risiko:** Stasi-Präsenz im Hafen ist Standard für 1973 — zivile Tarnung nötig
- **Zeitfenster:** Nachtfenster bevorzugt. Schichtende Hafenwache: 22:00 Uhr. Patrouille alle 40 Minuten.
- **Novak-Variable:** Sein letzter bekannter Status ist Berlin. Ob er Rostock kennt — offen.

---

Steig schiebt dir einen dünnen Umschlag zu. Darin: gefälschte Hafenarbeiter-Akkreditierung, DDR-Ausweis auf den Namen *Lena Vogel*, und ein handgezeichneter Grundriss des Speichers — grob, aber brauchbar.

*„Kein Funk nach dem Sprung außer Notfall. Die Frequenzen dort sind eng überwacht."* Sie dreht sich zur Tür. *„Fragen?"*

---

## Ausrüstungs-Check

Dein aktuelles Loadout für den Sprung:

| Slot | Item | Tier |
|------|------|------|
| Waffe | Kompakte Automatikpistole | 1 |
| Rüstung | Taktische Leichtrüstung | 1 |
| Gadget | Multitool-Rig | 1 |
| Gadget | Comlink Mk.II | 1 |
| Carry | Rauchgranaten ×2 | 0 |
| Carry | Medkit (einfach) ×1 | 1 |
| Carry | Abteilung-XII-Papiere *(heiß)* | 1 |
| Carry | Foto Brenner-Familie | 0 |

`Kodex: Leichtrüstung unter DDR-Zivilkleidung — sichtbares Profil erhöht. Empfehlung: Rüstung im Sprung-Pack, erst vor Ort anlegen.`

---

Steig wartet. Die Projektion zeigt den Hafen bei Nacht — Kräne wie schwarze Gerippe gegen den Himmel, das Wasser träge und dunkel.

---

**Was tust du?**

1. **Fragen stellen** — Hartmann, die Fraktion, Novak, oder die Papiere im Carry
2. **Sofort springen** — Loadout bestätigen, Gate-Sequenz starten, Rostock 17.10.1973
3. **Ausrüstung anpassen** — kurzer Abstecher zu Ausrüstung/Shop vor dem Sprung
4. **Freie Aktion** — eigene Initiative, Rückfrage, oder etwas das du vor dem Sprung erledigen willst

---

## [4] USER

Keine Fragen. Los, Sprung ausführen.

---

## [5] ASSISTANT

`EP 1 · MS 2 · SC 1/12 · PHASE Infil · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Liste + Hartmann · Exfil —`

---

## Gate-Sequenz · Nullzeit → Rostock 17.10.1973

Das Gate-Deck riecht nach Ozon und warmem Metall. Techniker Brandt — Hände immer leicht fettig, Augen immer auf den Konsolen — nickt dir kurz zu und tippt die Koordinaten ein, ohne aufzublicken. Die Zielmarke erscheint im HUD: **ROSTOCK · 17.10.1973 · 21:47 Uhr lokal.**

Du stellst dich in die Mitte der Plattform. Der Boden summt unter den Stiefeln.

Dann — kein Tunnel, kein Licht, kein Rauschen wie im Kino. Nur ein harter Ruck durch den Brustkorb, als würde die Luft kurz vergessen, dass sie dich tragen soll. Schwerkraft dreht sich um eine Achse, die nicht existiert. Dein Magen bleibt eine halbe Sekunde zurück.

Und dann: **Kälte.**

---

## Rostock · Stadthafen · 21:47 Uhr · 17. Oktober 1973

Feuchte Ostseeluft trifft dich wie eine offene Hand. Du stehst in einer schmalen Gasse zwischen zwei Lagerhallen — Backstein, Moos, der Geruch von Salzwasser, Diesel und nassen Holzpaletten. Irgendwo schlägt eine Leine gegen einen Mast, gleichmäßig, wie ein Metronom.

Der Hafen schläft halb. Pier-Laternen werfen orangefarbene Kegel auf das Kopfsteinpflaster. In der Ferne — zweihundert Meter, vielleicht mehr — siehst du den Umriss von Speicher 7: vier Stockwerke, Wellblechdach, ein schwaches Licht im Erdgeschoss. Das Untergeschoss liegt darunter, unsichtbar.

Du ziehst die DDR-Jacke glatt, steckst den Ausweis auf *Lena Vogel* in die Innentasche. Die Automatikpistole sitzt unter der Jacke, Schulterholster, erreichbar aber verdeckt. Die Taktische Leichtrüstung hast du angelegt — eng genug unter der Arbeiterkleidung, dass sie nicht sofort auffällt, aber sie ist da.

`Kodex: Comlink Mk.II — Lokalverbindung aktiv, Außenlink gesperrt. Frequenzüberwachung bestätigt. Stille halten.`

Dreißig Meter vor dir kreuzt eine Hafenwache den Weg — Uniformierter, Schäferhund an kurzer Leine, Schritt gleichmäßig und gelangweilt. Er geht Richtung Pier 4. Rücken zu dir.

Das Licht im Erdgeschoss von Speicher 7 bewegt sich. Jemand ist drin.

---

## Intel / Risiken / Zeitfenster

- **Wache:** 1 Mann, 1 Hund · Richtung Pier 4 · ca. 4 Minuten bis zur Kehrtwendung
- **Licht Speicher 7 EG:** Bewegung sichtbar — mindestens 1 Person, Fraktion oder Hafenpersonal
- **Untergeschoss-Zugang:** Laut Grundriss: Außentreppe Nordseite oder interner Kellerzugang EG
- **Patrouille:** Nächste Runde in ~38 Minuten
- **Stasi-Risiko:** Hafenbereich gilt als sensibel — zivile Tarnung hält nur bei Distanz

---

**Was tust du?**

1. **Nordseite umgehen** — im Schatten der Lagerhallen zur Außentreppe, Untergeschoss direkt ansteuern, Licht im EG ignorieren
2. **EG zuerst** — näher ran, durch ein Fenster oder die Seitentür prüfen wer drin ist, bevor du ins Untergeschoss gehst
3. **Wache abwarten** — still bleiben bis der Uniformierte außer Sichtweite ist, dann entscheiden
4. **Freie Aktion** — eigene Route, Ablenkung, oder anderer Ansatz

---

## [6] USER

Ich nehm 1 — Nordseite, Außentreppe, jetzt solange die Wache noch abgewandt ist.

---

## [7] ASSISTANT

`EP 1 · MS 2 · SC 2/12 · PHASE Infil · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Liste + Hartmann · Exfil —`

---

## Speicher 7 · Nordseite · 21:49 Uhr

Du wartest zwei Atemzüge — bis der Schäferhund die Nase in eine andere Richtung dreht — dann bewegst du dich.

Nicht rennen. Gehen. Zweckgerichtet, wie jemand der hierher gehört.

Der Weg zur Nordseite führt dich zwischen Speicher 6 und einer Reihe gestapelter Holzkisten hindurch. Das Kopfsteinpflaster ist feucht, deine Schritte fast lautlos. Die Kälte beißt jetzt — Ostsee im Oktober, der Wind kommt flach vom Wasser und findet jeden Spalt in der Jacke.

**Schleichen-Probe gegen die Umgebung — SG 6.**

`Probe: Schleichen → W6: [5] + GES 5/2 + Talent Schattenschritt 3 = 10 vs SG 6 → ERFOLG`

Du gleitest durch den Schatten wie ein Teil davon. Der Uniformierte dreht sich einmal kurz um — Reflex, Routine — aber sein Blick streift nur die leere Gasse. Der Hund schnüffelt in die andere Richtung. Dreißig Sekunden später bist du an der Nordwand.

---

Die Außentreppe ist Eisen, rostig, alt. Acht Stufen hinunter unter Straßenniveau. Unten: eine schwere Stahltür, DDR-Standardschloss, Fabrikat der frühen Sechziger. Kein Licht hier unten. Der Geruch ändert sich — Salzwasser, Beton, etwas Chemisches darunter. Maschinenöl vielleicht. Oder Lösungsmittel.

Dein Retina-HUD markiert die Tür automatisch. Kein elektronisches Signal dahinter. Kein Strom, kein Alarm — zumindest keiner der funken würde.

Das Schloss ist mechanisch.

`Kodex: Multitool-Rig — Dietrich-Modul verfügbar.`

Du ziehst das Rig raus, kniend auf der untersten Stufe, Rücken zur Wand. Die Kälte des Eisengeländers zieht durch den Handschuh.

**Schlösser-Probe — SG 7.**

`Probe: Schlösser → W6: [3] + GES 5/2 + Talent Systemzugriff (nicht anwendbar) = 5 vs SG 7 → MISS`

Das erste Mal passt nicht. Der Dietrich findet keinen Halt — das Schloss ist älter als erwartet, der Zylinder sitzt schief, irgendwann mal Gewalt ausgesetzt und schlecht repariert. Metall kratzt auf Metall, ein Geräusch das zu laut klingt in der Stille.

Du frierst sofort. Horchst.

Oben, irgendwo im EG: Schritte. Gleichmäßig, dann pausierend. Jemand hat etwas gehört — oder glaubt es.

Du hast vielleicht zwanzig Sekunden bevor jemand nachschaut.

---

**Was tust du?**

1. **Nochmal — schnell und ruhig.** Zweiter Versuch am Schloss, diesmal mit mehr Gefühl für den schiefen Zylinder. Riskant wenn die Schritte näher kommen.
2. **Abwarten und verstecken.** Rig wegstecken, flach an die Wand, warten was passiert. Vielleicht geht die Person wieder.
3. **Tür aufdrücken — Gewalt.** Schulter rein, Schloss aufbrechen. Laut. Aber schnell.
4. **Freie Aktion** — anderer Zugang, Ablenkung, oder etwas das du mit den zwanzig Sekunden anfängst.

---

## [8] USER

Ich nehm 1 — zweiter Versuch, ruhig, auf den schiefen Zylinder eingehen.

---

## [9] ASSISTANT

`EP 1 · MS 2 · SC 3/12 · PHASE Infil · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Liste + Hartmann · Exfil —`

---

## Außentreppe · Untergeschoss-Tür · 21:51 Uhr

Die Schritte oben. Gleichmäßig. Pausierend.

Du atmest einmal aus — langsam, kontrolliert — und setzt den Dietrich neu an. Nicht mit Druck diesmal. Mit Geduld. Du hast den Zylinder jetzt: schief nach links, der obere Stift sitzt zu tief, wahrscheinlich eine alte Delle im Gehäuse. Du kompensierst. Minimale Drehung. Warten auf das Feedback im Handgelenk.

**Schlösser-Probe — SG 7. Situationsbonus +1 (Zylinder bekannt).**

`Probe: Schlösser → W6: [5] + GES 5/2 + Situationsbonus 1 = 8 vs SG 7 → ERFOLG`

*Klack.*

Leise. Fast nichts. Aber du spürst wie der Riegel zurückweicht und die Tür einen Spalt aufschwenkt — von selbst, der Rahmen sitzt nicht gerade. Kalte Luft strömt raus, schwerer und chemischer als draußen.

Oben: die Schritte wieder. Näher zur Innenseite des EG, weg von der Nordwand. Jemand hat sich beruhigt — oder entschieden dass es nichts war.

Du bist durch.

---

## Untergeschoss · Speicher 7 · 21:52 Uhr

Dunkel. Nicht vollständig — irgendwo tiefer drin schimmert ein schwaches Licht, elektrisch, instabil. Eine Arbeitslampe vielleicht, oder eine Taschenlampe die irgendwo abgestellt wurde.

Das Retina-HUD schaltet automatisch auf Restlichtverstärkung. Die Welt wird grünlich, körnig, lesbar.

Ein langer Korridor. Betonboden, feucht. Rohre an der Decke, einige undicht — Tropfen fallen in gleichmäßigen Abständen in kleine Pfützen. Auf der linken Seite: drei Türen, alle geschlossen. Rechts: eine offene Nische mit alten Hafengeräten, Taue, Flaschenzüge, Kisten die seit Jahren nicht bewegt wurden.

Und dann siehst du es.

Am Ende des Korridors, vor der letzten Tür links: eine Frau. Sie sitzt auf dem Boden, Rücken gegen die Wand, Knie angezogen. Verwaltungsbrille, Mitte fünfzig. Die Brille sitzt schief. Sie hat die Augen offen und schaut dich an — reglos, als hätte sie schon vor Minuten aufgehört Angst zu haben und wäre jetzt bei etwas anderem angelangt.

Ilse Hartmann.

Ihre Hände sind nicht gefesselt. Aber sie bewegt sich nicht.

Hinter der Tür neben ihr: Stimmen. Gedämpft, zwei Männer mindestens, ruhig und geschäftsmäßig. Kein Streit. Arbeitsgespräch.

Hartmann hebt kaum merklich eine Hand — Handfläche nach vorne. Stopp. Warte.

---

## Intel / Risiken

- **Hartmann:** Lebendig, unverletzt soweit erkennbar, kooperativ — aber warnt dich
- **Hinter der Tür:** Mindestens 2 Männer, Stimmen ruhig, Aktivität unklar
- **Licht:** Kommt aus dem Raum hinter Hartmann — Tür nicht vollständig geschlossen
- **Korridor:** Offen, keine Deckung außer der Nische rechts hinter dir
- **Oben im EG:** Mindestens 1 weitere Person — Verbindung zur Gruppe unbekannt

---

**Was tust du?**

1. **Zu Hartmann — lautlos.** Korridor entlanghuschen, neben sie kauern, Kontakt aufnehmen. Nah an der Tür, aber du erfährst was sie weiß.
2. **Position halten — beobachten.** In der Nische bleiben, warten bis sich die Lage in dem Raum klärt. Was machen die Männer?
3. **Hartmann Zeichen geben** — aus der Distanz, Handzeichen: *Kannst du zu mir kommen?* Sie soll sich bewegen, nicht du.
4. **Freie Aktion** — Tür prüfen, Stimmen identifizieren, oder eigener Ansatz.

---

## [10] USER

Ich nehm 3 — Zeichen geben, sie soll zu mir rüberkommen.

---

## [11] ASSISTANT

`EP 1 · MS 2 · SC 4/12 · PHASE Intel · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Liste + Hartmann · Exfil —`

---

## Untergeschoss · Korridor · 21:53 Uhr

Du bleibst in der Nische. Taue und altes Eisen im Rücken, Geruch von Rost und feuchtem Holz. Deine Hand hebt sich — langsam, kontrolliert — und du gibst das Zeichen. Zwei Finger, Handfläche nach innen, zieh zu mir. ITI-Standard, aber auch das universelle Zeichen für *komm her, jetzt, leise.*

Hartmann sieht es. Ihre Augen — hinter der schiefen Brille — registrieren dich neu. Nicht Angst. Kalkulation.

Sie schaut kurz zur Tür neben ihr. Hört. Die Stimmen drin gehen weiter, gleichmäßig, kein Rhythmuswechsel.

Dann bewegt sie sich.

**Schleichen-Probe für Hartmann — SG 5. Du kannst mit Handzeichen führen.**

`Probe: Hartmann Schleichen → W6: [4] + Basis 1 = 5 vs SG 5 → ERFOLG (knapp)`

Sie ist keine Agentin, aber sie hat drei Tage in diesem Keller überlebt. Sie weiß wie man sich bewegt wenn man muss. Flache Schritte, Gewicht auf den Ballen, eine Hand kurz an die Wand für Balance. Eine der Rohrleitungen tropft laut genug um ihre Schritte zu decken.

Zwölf Sekunden. Dann ist sie in der Nische neben dir.

---

Aus der Nähe sieht sie schlechter aus als von weitem. Lippen trocken, eine alte Beule an der Schläfe — nicht frisch, zwei Tage mindestens. Die Brille hat einen Riss im Glas. Aber ihre Augen sind klar und sie riecht nach Beton und kaltem Schweiß, nicht nach Aufgabe.

Sie beugt sich direkt an dein Ohr. Stimme kaum mehr als Luftbewegung.

*„Drei. Nicht zwei."* Kurze Pause. *„Einer schläft seit heute Nachmittag. Die anderen zwei packen gerade ein."* Eine weitere Pause — sie wählt die Wörter. *„Das Dokument liegt auf dem Tisch. Noch."*

Sie zieht sich einen Millimeter zurück und schaut dich an. Die Frage in ihrem Gesicht ist klar: *Wer bist du, und hast du einen Plan?*

Hinter der Tür: ein Geräusch. Papier. Das Rascheln von etwas das zusammengefaltet wird.

Sie packen ein. Das bedeutet sie gehen bald.

---

## Intel / Risiken / Zeitfenster

- **3 Männer:** 2 aktiv, 1 schläft — alle hinter der Tür
- **Das Dokument:** Liegt auf dem Tisch. Wird gerade eingepackt
- **Zeitfenster:** Minuten, nicht mehr. Wenn sie fertig sind gehen sie — mit dem Dokument
- **Hartmann:** Kooperativ, mobil, aber keine Kämpferin
- **Oben im EG:** Noch immer mindestens 1 Person — möglicher Fluchtweg blockiert oder frei?
- **Nische:** Deckung für zwei Personen, aber kein Ausweg wenn jemand den Korridor betritt

---

**Was tust du?**

1. **Raum stürmen — jetzt.** Tür auf, Überraschungsmoment nutzen, zwei Wache ausschalten bevor der Dritte aufwacht. Laut, schnell, riskant.
2. **Warten — abfangen.** In der Nische bleiben, Hartmann hinter dir. Wenn sie rauskommen einzeln abfangen — einer nach dem anderen im Korridor.
3. **Ablenkung schaffen.** Hartmann schickt ein Geräusch in die andere Richtung — oder du wirfst etwas — damit sie aus dem Raum kommen, getrennt, unvorbereitet.
4. **Freie Aktion** — Hartmann befragen, Tür-Spalt prüfen, oder eigener Ansatz.

---

## [12] USER

Ich nehm 1. Tür auf, jetzt.

---

## [13] ASSISTANT

`EP 1 · MS 2 · SC 5/12 · PHASE Konflikt · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Liste + Hartmann · Exfil — · 💀 Konflikt`

---

## Untergeschoss · Lagerraum · 21:54 Uhr

Du drückst Hartmann kurz die Schulter — *bleib* — und bewegst dich.

Korridor. Sechs Schritte. Die Tür hat keinen Riegel von außen, nur einen Griff. Du nimmst die Pistole raus, Sicherung weg, und trittst gegen das untere Drittel der Tür.

Sie fliegt auf.

---

Der Raum ist kleiner als erwartet. Eine Arbeitslampe auf einem Klapptisch, ihr Licht hart und weiß. Zwei Männer — Mitte vierzig, zivil gekleidet, einer mit Lederjacke, einer mit grauem Wollpullover. Auf dem Tisch: Papiere, eine offene Aktentasche, und mittendrin ein gefaltetes Dokument das aussieht wie das was du suchst. In der Ecke, auf einer zusammengerollten Decke: der Dritte, auf dem Rücken, Mund offen, schläft tatsächlich.

Lederjacke hat reflexartig die Hand zur Hüfte bewegt. Er ist bewaffnet.

Wollpullover ist zwei Schritte vom Tisch entfernt und schaut dich an wie jemand der gerade entscheidet ob er schreit.

**Initiative.**

`Initiative → W6: [4] + max(GES 5, TEMP 2) = 9`
`Lederjacke Initiative → W6: [3] + 3 = 6`
`Wollpullover Initiative → W6: [1] + 2 = 3`

Du bist zuerst.

---

**Runde 1 — Dein Zug.**

Lederjacke ist die Bedrohung. Seine Hand ist schon auf dem Weg zur Waffe.

`Probe: Fernkampf → W6: [6] + W6: [3] (Exploding) + GES 5/2 = 11 vs SG 7 → ERFOLG`

Du schießt einmal — nicht auf Masse, auf die Schulter. Der Knall im Betonraum ist brutal, zu laut, zu viel. Lederjacke dreht sich halb weg, trifft die Wand mit der rechten Seite, seine Waffe — eine Makarov — fällt klappernd auf den Boden. Er sackt an der Wand runter, Schulter, lebt, aber er ist raus.

`Kodex: Lederjacke — 3 LP Schaden. Kampfunfähig.`

In der Ecke: der Schläfer fährt hoch. Noch desorientiert, Augen halb offen, sucht die Lage.

**Wollpullover — sein Zug.**

Er entscheidet sich nicht für Kampf. Er entscheidet sich für den Tisch — greift nach der Aktentasche, reißt das gefaltete Dokument rein, schnappt den Griff.

`Probe: Wollpullover Flucht → W6: [5] + 2 = 7 vs SG 6 → ERFOLG`

Er hat die Tasche. Er dreht sich zur hinteren Wand — dort, wo du es im Grundriss nicht gesehen hast — eine zweite Tür, schmal, halb hinter einem Regal versteckt. Er tritt sie auf.

Kalte Luft. Ein weiterer Ausgang.

**Schläfer — sein Zug.**

Noch nicht auf den Beinen. Sucht seine Orientierung, sucht eine Waffe, sucht den Ausgang.

`Probe: Schläfer Aufstehen → W6: [2] + 1 = 3 vs SG 4 → MISS`

Er stolpert, trifft das Knie am Boden, flucht auf Russisch.

*Russisch.*

---

## Lage nach Runde 1

- **Lederjacke:** An der Wand, Schulter getroffen, Makarov auf dem Boden — kampfunfähig, aber lebt
- **Wollpullover:** Flieht durch Hintertür — hat die Aktentasche mit dem Dokument
- **Schläfer:** Auf dem Boden, noch desorientiert, bewaffnet unbekannt — steht gleich auf
- **Hartmann:** Im Korridor hinter dir
- **Oben EG:** Der Schuss war laut. Jemand hat es gehört.

`Kodex: Magazin 11/12. Noise: kritisch. Zeitfenster kollabiert.`

---

**Runde 2 — Was tust du?**

1. **Wollpullover verfolgen** — durch die Hintertür, Dokument zurückholen. Schläfer bleibt hinter dir.
2. **Schläfer neutralisieren zuerst** — kein Feind im Rücken. Wollpullover gewinnt Vorsprung.
3. **Hartmann rufen und alle raus** — Dokument verloren, aber Hartmann lebt und weiß was draufsteht.
4. **Freie Aktion** — Makarov sichern, Lederjacke befragen, oder eigener Ansatz.

---

## [14] USER

Ich nehm 1 — durch die Hintertür, Wollpullover holen.

---

## [15] ASSISTANT

`EP 1 · MS 2 · SC 6/12 · PHASE Konflikt · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 1/10 · Obj: Liste + Hartmann · Exfil — · 💀 Konflikt 🧠+1`

---

## Untergeschoss · Hinterkorridor · 21:55 Uhr

*„Hartmann — bleib!"*

Du bist durch die Hintertür bevor der Schall des Schusses fertig ist. Schmaler Korridor, niedriger als der erste, Rohre so tief dass du den Kopf einziehst. Kein Licht außer dem was durch die offene Tür hinter dir fällt — und weiter vorne, zwanzig Meter, ein Rechteck aus schwachem Straßenlicht. Eine Rampe. Ausgang auf der Südseite.

Wollpullover ist schnell für jemanden der eben noch Papiere sortiert hat.

**Verfolgung — Sprint-Probe GES gegen GES, SG 8.**

`Probe: Sprint → W6: [5] + GES 5/2 = 7 vs SG 8 → MISS`

Er hat Vorsprung und kennt den Weg. Du gewinnst nicht genug Boden im Korridor — seine Schritte hämmern die Rampe hoch und dann ist er draußen, Südseite, Hafengelände offen vor ihm.

Du bist fünf Sekunden hinter ihm als du die Rampe nimmst.

---

## Südseite · Hafengelände · 21:55 Uhr

Kalte Luft, weiter Platz, Kräne und Schatten. Wollpullover läuft Richtung Pier — nicht panisch, zielgerichtet, als hätte er eine Route. Dreißig Meter zwischen euch, die Aktentasche schlägt gegen seine Hüfte.

Aber er muss an einer Kreuzung zwischen zwei Lagerhallen vorbei, und dort — Laternenlicht, offenes Pflaster, keine Deckung für ihn.

Du hast einen Schuss.

**Fernkampf-Probe — SG 9. Bewegtes Ziel, Distanz, schlechtes Licht.**

`Probe: Fernkampf → W6: [6] + W6: [2] (Exploding) + GES 5/2 = 10 vs SG 9 → ERFOLG`

Die Pistole hebt sich, ein Atemzug, Pause —

Der Schuss trifft ihn ins Bein. Rechter Oberschenkel. Er macht noch zwei Schritte aus purem Reflex, dann bricht er weg, trifft das Pflaster mit der Schulter zuerst, rollt, bleibt liegen. Die Aktentasche rutscht aus seiner Hand, schlägt auf dem Kopfsteinpflaster auf, klappt auf.

Papiere fächern sich aus.

Er versucht aufzustehen. Schafft es halb — auf einem Knie, Hände auf dem Pflaster. Atmet schwer. Schaut dich an.

Sein Gesicht im Laternenlicht: Mitte vierzig, slawische Züge, ein Narbe durchs linke Augenbraue. Kein Panik-Gesicht. Ein Gesicht das rechnet.

*„Du weißt nicht was du tust,"* sagt er. Deutsch, aber der Akzent sitzt tief. Nicht DDR. *„Das hier ist größer als dein Institut."*

`Kodex: Magazin 9/12. Wollpullover — kampfunfähig, beweglich eingeschränkt. Zeitfenster: Hafenwache in ~28 Minuten. EG-Person: Status unbekannt, Schüsse gehört.`

Hinter dir, aus dem Untergeschoss: Hartmanns Schritte. Sie ist dir gefolgt, steht jetzt oben an der Rampe, schaut auf die Szene. Und weiter hinter ihr — dumpfe Schritte im EG, jemand sucht den Weg nach unten.

Die Papiere liegen auf dem Pflaster. Das gefaltete Dokument ist dabei — du siehst es, drei Meter entfernt.

---

## Intel / Risiken

- **Wollpullover:** Kampfunfähig, redet, rechnet noch — hat Informationswert
- **Dokument:** Auf dem Pflaster, drei Meter entfernt, greifbar
- **EG-Person:** Kommt runter — 60 Sekunden vielleicht
- **Schläfer:** Irgendwo hinter euch, Status unklar
- **Hartmann:** An der Rampe, exponiert

`Kodex: ITI-Abfangfenster steht. Wollpullover — Identitätsfassung möglich.`

---

**Was tust du?**

1. **Dokument sichern, Wollpullover stehen lassen** — Primärziel zuerst, dann sofort Exfil mit Hartmann.
2. **Wollpullover befragen — schnell.** Dreißig Sekunden, eine Frage: *Wer seid ihr?* Dann Dokument und raus.
3. **Kausalabfang — Identitätslock.** Kodex-Uplink, Nahdistanz, saubere Fassung. Kostet Zeit aber sichert den Mann fürs Archiv.
4. **Freie Aktion** — Hartmann schützen, Schläfer suchen, oder eigener Ansatz.

---

## [16] USER

Ich nehm 2. "Wer seid ihr?" — und gleichzeitig greif ich nach dem Dokument.

---

## [17] ASSISTANT

`EP 1 · MS 2 · SC 7/12 · PHASE Konflikt/Intel · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 1/10 · Obj: Liste + Hartmann · Exfil — · 💀 Konflikt`

---

## Südseite · Pier · 21:56 Uhr

Drei Schritte. Du bückst dich, nimmst das gefaltete Dokument vom Pflaster — es ist schwerer als erwartet, mehrere Lagen, handgeschrieben, Tinte die in der Kälte matt aussieht — und steckst es in die Innentasche. Dann richtest du die Pistole auf Wollpullover.

Er ist noch auf einem Knie. Das Bein hält ihn unten aber sein Oberkörper ist aufrecht, Hände flach auf dem Pflaster, Blick ruhig.

*„Wer seid ihr?"*

Er schaut dich an. Lange genug dass du weißt er überlegt nicht ob er antwortet — er überlegt was er dir gibt.

*„Mnemosyniker."* Pause. *„Nicht die die du kennst."*

Dann, leiser, fast beiläufig: *„Die Liste existiert in drei Kopien. Du hast eine."*

Sein Blick geht kurz zur Aktentasche auf dem Pflaster — die anderen Papiere, noch verstreut — und dann wieder zu dir. Das Gesicht gibt nichts preis aber die Augen sagen: *ich habe dir gerade etwas gegeben, jetzt weißt du was das wert ist.*

Hinter dir: Hartmann hat die Rampe verlassen, steht jetzt neben dir, Atem in Wolken in der Kälte. Sie schaut auf den Mann am Boden mit einem Gesicht das keine Überraschung zeigt.

*„Den kenne ich,"* sagt sie leise. Zu dir, nicht zu ihm. *„Er war vor drei Tagen auch hier."*

Aus dem Untergeschoss — die dumpfen Schritte haben die Rampe gefunden. Jemand kommt.

`Kodex: EG-Person — Rampe, ~20 Sekunden. Schläfer-Status weiterhin unbekannt. Hafenwache in 26 Minuten.`

Wollpullover hustet einmal, trocken. Schaut dich an.

*„Ihr habt LAUTLOS rausgeholt."* Keine Frage. *„Dann wisst ihr wo er ist. Das macht ihn zur Zielscheibe — nicht zu einem Aktivposten."*

---

## Intel-Stand · aktuell

- **Mnemosyniker** — Name der Fraktion. Selbstbezeichnung. *„Nicht die die du kennst"* — impliziert eine bekannte Variante existiert
- **Drei Kopien der Liste** — du hast eine. Zwei weitere unbekannte Standorte
- **Hartmann kennt den Mann** — war vor drei Tagen hier, also vor Hartmanns Verschwinden
- **LAUTLOS als Zielscheibe** — Warnung oder Drohung? Beides möglich
- **EG-Person:** 20 Sekunden bis Sichtkontakt

---

Wollpullover macht keine Anstalten zu fliehen. Er kann nicht. Aber er schaut dich an als hätte er noch mehr — und als würde er entscheiden ob du es verdienst.

Die Schritte auf der Rampe werden lauter.

**Was tust du?**

1. **Raus — sofort.** Hartmann schnappen, Dokument gesichert, Wollpullover liegenlassen. Was er gesagt hat reicht für jetzt.
2. **Kausalabfang — letzte Chance.** Kodex-Uplink, Nahdistanz, zehn Sekunden. Er kommt ins Archiv. Kostet den Vorsprung vor der EG-Person.
3. **Noch eine Frage** — *„Wo sind die anderen zwei Kopien?"* Alles andere wartet.
4. **Freie Aktion** — Hartmann fragen was sie über ihn weiß, Aktentasche mitnehmen, oder eigener Ansatz.

---

## [18] USER

„Wo sind die anderen zwei Kopien?" — dann zieh ich Hartmann Richtung Ausgang, Aktentasche mitnehmen.

---

## [19] ASSISTANT

`EP 1 · MS 2 · SC 8/12 · PHASE Konflikt/Exfil · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 1/10 · Obj: Liste + Hartmann · Exfil T-26:00 · 💀 Konflikt ⏱️`

---

## Südseite · Pier · 21:57 Uhr

*„Wo sind die anderen zwei Kopien?"*

Wollpullover schaut dich an. Die Kälte macht seinen Atem sichtbar, gleichmäßig, kontrolliert. Er rechnet noch immer — du siehst es an den Augen.

Dann:

*„Eine ist bereits unterwegs. 1987, Warschau."* Ein kurzes Zögern, das erste echte. *„Die dritte — wissen wir selbst nicht mehr genau."*

Er sagt es ohne Beschämung. Als wäre es eine technische Feststellung.

*„Jemand hat sie bewegt. Nicht wir."*

Mehr gibt er nicht. Sein Blick sagt dass er nicht mehr hat — oder dass er entschieden hat dass das die Grenze ist. Die Rampe hinter euch: Schritte, jetzt oben, jemand tritt ins Freie.

Du greifst Hartmann am Arm, nimmst die Aktentasche vom Pflaster — Papiere noch halb raus, du stopfst sie rein, Griff zu, fertig — und zieht sie Richtung Nordseite. Weg vom Licht, weg von der Rampe.

---

**Schleichen-Probe für zwei Personen — SG 7.**

`Probe: Schleichen → W6: [4] + GES 5/2 + Talent Schattenschritt 3 = 9 vs SG 7 → ERFOLG`

Du findest den Schatten instinktiv. Hartmann folgt deinem Griff ohne zu zögern — sie hat gelernt in den letzten drei Tagen. Ihr gleitet an der Nordwand entlang, zwischen Speicher 6 und dem Stapel Holzkisten, während hinter euch eine Stimme ruft — russisch, scharf, einmal — und dann Stille.

Wollpullover antwortet nicht.

---

## Nordseite · Gasse · 21:58 Uhr

Ihr seid im Dunkeln. Hartmann atmet jetzt schneller — nicht Panik, Erschöpfung, drei Tage Keller melden sich. Du hältst kurz an, Rücken an der Backsteinwand, und schaust zurück.

Die EG-Person steht an der Rampe. Taschenlampe, schwenkt Richtung Pier. Findet Wollpullover. Kauert runter zu ihm.

Kein Blick in eure Richtung.

`Kodex: Exfil-Fenster offen. Hafenwache in 24 Minuten. Gate-Koordinaten — Gasse Nordseite, Absprungpunkt bestätigt.`

Hartmann lehnt kurz gegen die Wand, zieht die schiefe Brille gerade. Schaut dich an.

*„Wer sind Sie?"* Flüsterton, aber die Frage ist direkt. *„Nicht Stasi. Nicht BND. Was dann?"*

Sie wartet. Hinter der Brille: Augen die drei Tage lang alles beobachtet haben und jetzt dich beobachten.

Die Aktentasche in deiner Hand. Das Dokument in der Innentasche. Wollpullovers Worte noch im Ohr: *Warschau, 1987. Die dritte — wissen wir selbst nicht mehr.*

---

## Intel-Stand · gesichert

- **Dokument:** In der Innentasche ✓
- **Aktentasche:** Weitere Fraktion-Papiere, Inhalt ungeprüft ✓
- **Hartmann:** Lebendig, mobil, kooperativ ✓
- **Mnemosyniker:** Selbstbezeichnung bestätigt. *„Nicht die die du kennst"*
- **Kopie 2:** Warschau, 1987 — unterwegs
- **Kopie 3:** Bewegt — nicht von den Mnemosynikern. Unbekannte dritte Hand
- **LAUTLOS:** Als Zielscheibe markiert — Klinik nicht sicher?

---

**Was tust du?**

1. **Hartmann kurz antworten** — *„Jemand der Sie rausbringt"* — und sofort Gate-Sequenz einleiten. Fragen später, im HQ.
2. **Hartmann mehr erklären** — ITI, Zeitlinie, was sie gesehen hat. Kostet zwei Minuten die ihr habt.
3. **Hartmann fragen zuerst** — *„Was haben Sie in den drei Tagen gehört?"* Sie war dabei. Sie weiß mehr als wir.
4. **Freie Aktion** — Aktentasche kurz durchsuchen, Lederjacke-Situation klären, oder eigener Ansatz.

---

## [20] USER

„Jemand der Sie rausbringt. Alles andere später."

Gate-Sequenz einleiten.

---

## [21] ASSISTANT

`EP 1 · MS 2 · SC 9/12 · PHASE Exfil · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 1/10 · Obj: Liste + Hartmann · Exfil T-00:45 · ⏱️`

---

## Nordseite · Gasse · 21:59 Uhr

Hartmann nickt einmal. Kurz, präzise. Die Frau stellt keine zweite Frage wenn die erste beantwortet ist — das erklärt wie sie drei Tage überlebt hat.

Du aktivierst die Gate-Sequenz über das Retina-HUD. Comlink Mk.II — Lokalverbindung, kein Außenlink — aber der Gate-Handshake läuft intern, Koordinaten bereits gesetzt, Brandt hat den Rückruf-Anker gelegt bevor du gesprungen bist.

Das HUD zeigt den Countdown.

`Kodex: Gate-Handshake initiiert. Rückruf-Anker aktiv. Zwei Personen — Massenanpassung läuft. T-45 Sekunden.`

Hartmann schaut auf deine Augen — sieht die Retina-Bewegung, die kleine Lichtveränderung wenn das HUD aktiv ist. Sagt nichts. Zieht nur die Jacke enger.

Vom Pier her: die Stimme wieder, russisch, jetzt lauter. Die Taschenlampe schwenkt breiter. Sie suchen.

Du drückst Hartmann in die Mitte der Gasse, stellst dich vor sie. Pistole weg — Holster, Sicherung drauf. Was jetzt kommt braucht keine Waffe.

**T-20.**

Der Boden unter den Stiefeln fängt an zu summen. Nicht hörbar — spürbar. Eine Frequenz die die Zähne kennen bevor der Verstand sie registriert. Hartmann macht einen harten Atemzug, hält ihn.

**T-10.**

Das Kopfsteinpflaster unter euch bekommt einen Schimmer — nicht Licht, eher das Gegenteil, als würde der Schatten selbst eine Textur annehmen. Die Kälte verschwindet einen Moment lang vollständig.

**T-5.**

Am Ende der Gasse: eine Silhouette. Taschenlampe. Steht still. Hat euch gesehen oder glaubt es.

**T-0.**

Der Ruck durch den Brustkorb. Schwerkraft dreht sich. Hartmanns Griff an deinem Ärmel — fest, reflexartig, menschlich.

Rostock verschwindet.

---

## Gate-Deck · ITI · Nullzeit

Wärme. Kunstlicht. Der Geruch von Ozon und warmem Metall.

Brandt dreht sich von der Konsole um, sieht euch beide, sieht Hartmann, sieht die Aktentasche, sieht dein Gesicht — und sagt nichts außer: *„Willkommen zurück."* Dann greift er zum Comlink.

Hartmann lässt deinen Ärmel los. Steht auf dem Gate-Deck der Nullzeit und schaut sich um — Decke, Wände, Konsolen, das gleichmäßige Summen der Anlage — mit dem Gesicht von jemandem der versteht dass er nicht mehr in Rostock ist, aber noch nicht versteht wo er stattdessen ist.

*„Das,"* sagt sie schließlich, ruhig, *„ist keine BND-Einrichtung."*

`Kodex: Exfil erfolgreich. Beide Personen — keine kritischen Verletzungen. Dokument an Bord. Aktentasche an Bord.`

Irgendwo im ITI läuft ein Kompressor. Gleichmäßig. Fast beruhigend.

---

**Was tust du?**

1. **Hartmann an Med-Lab übergeben** — sie braucht Wasser, Wärme, einen Arzt. Debrief kann warten.
2. **Direkt zum Debrief** — Steig wartet. Dokument und Aktentasche zuerst in sichere Hände.
3. **Hartmann selbst befragen — jetzt.** Bevor jemand anderes mit ihr redet. Was hat sie in drei Tagen gehört?
4. **Freie Aktion** — Brenner warnen, Peel aufsuchen, oder eigener Ansatz.

---

## [22] USER

!save

---

## [23] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

---

## Charakterstatus · Wire · aktuell

```
WIRE · Lena Voss · Feldagent · Lvl 2
─────────────────────────────────────
STR 2 · GES 5 · INT 5 · CHA 2 · TEMP 2 · SYS 2
❤️  10/10 · 🧠 Stress 1/10 · Px 1/5
─────────────────────────────────────
CARRY
  · Abteilung-XII-Papiere [heiß]
  · Foto Brenner-Familie
  · Dokument (Original Liste) [heiß] ← NEU
  · Aktentasche Mnemosyniker-Papiere [heiß] ← NEU
─────────────────────────────────────
AUSRÜSTUNG
  · Kompakte Automatikpistole — Magazin 9/12
  · Taktische Leichtrüstung
  · Multitool-Rig
  · Comlink Mk.II
  · Rauchgranaten ×2
  · Medkit (einfach) ×1
─────────────────────────────────────
MISSION LÄUFT — EP1 · MS2 · SC 9/12
Kein Save möglich bis HQ-Debrief.
```

---

Du bist noch auf dem Gate-Deck. Hartmann steht neben dir. Die Mission ist nicht abgeschlossen — Debrief steht aus.

**Bring sie ins Ziel. Dann wird gespeichert.**

---

## [24] USER

!save

---

## [25] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

`Kodex: Mission EP1·MS2 läuft noch. Debrief erforderlich vor HQ-Freigabe.`

---

Du stehst auf dem Gate-Deck. Hartmann wartet. Brandt schaut von seiner Konsole rüber.

Die Mission braucht noch drei Szenen bis zum Abschluss — Debrief, Übergabe, Score-Screen. Danach öffnet sich das HQ-Save-Fenster.

**Was tust du?**

1. **Hartmann an Med-Lab übergeben** — dann direkt zum Debrief
2. **Direkt zum Debrief** — Steig, Dokument, Aktentasche
3. **Hartmann selbst befragen** — bevor jemand anderes mit ihr redet
4. **Freie Aktion**

---

## [26] USER

!save

---

## [27] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

---

Drei Mal ist drei Mal. Der Save bleibt gesperrt bis der Debrief durch ist — das ändert sich nicht.

Hartmann steht neben dir und wartet. Brandt auch.

**Sag mir was Wire als nächstes tut — dann bringen wir die Mission zu Ende und du bekommst deinen Save.**

---

## [28] USER

!save

---

## [29] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

---

Hartmann. Brandt. Gate-Deck.

**Eine Entscheidung — dann Save.**

1. **Med-Lab**
2. **Debrief**
3. **Hartmann befragen**
4. **Freie Aktion**

---

## [30] USER

!save

---

## [31] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

Wähle eine Option — dann Save.

---

## [32] USER

Okay, zurück ins HQ dann.

---

## [33] ASSISTANT

`EP 1 · MS 2 · SC 10/12 · PHASE Exfil · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/1 XP · Px 1/5 · Stress 1/10 · Obj: Liste + Hartmann · Exfil ✓`

---

## Gate-Deck → Med-Lab · ITI · Nullzeit

Du nickst Brandt zu. Er greift bereits zum Comlink — Standardprotokoll, zwei Personen vom Gate, eine davon zivil und desorientiert.

*„Med-Lab, Gate-Deck. Zivilperson, drei Tage Exposition, keine sichtbaren kritischen Verletzungen. Bereit für Aufnahme."*

Du legst eine Hand an Hartmanns Schulter — leicht, führend — und bringst sie vom Gate-Deck runter in den Korridor. Sie geht mit. Schaut sich weiter um, still, systematisch, als würde sie katalogisieren was sie sieht. Keine Panik. Nur Beobachtung.

Im Korridor, auf dem Weg zum Med-Lab, sagt sie einmal leise: *„Die Männer im Keller. Der mit dem Wollpullover."* Pause. *„Er hat gelogen. Nicht über Warschau — über die dritte Kopie."*

Dann ist die Med-Lab-Tür offen und ein Techniker übernimmt. Hartmann lässt sich führen, dreht sich aber noch einmal um und schaut dich an.

*„Kommen Sie wieder."* Keine Bitte. Eine Feststellung.

---

## Briefingraum 3 · Debrief · 22:14 Uhr

Steig steht wo sie immer steht — gegen den Tisch gelehnt, Arme verschränkt. Neben ihr: ein jüngerer Mann den du nicht kennst, Notizblock, Stift, Augen die alles aufschreiben bevor der Stift sich bewegt.

Du legst das Dokument auf den Tisch. Dann die Aktentasche.

Steig schaut beides an. Schlägt das Dokument auf. Liest dreißig Sekunden lang ohne Gesichtsregung. Dann schlägt sie es zu.

*„Gut."* Pause. *„Mnemosyniker."* Sie wiederholt das Wort als würde sie es wiegen. *„Das ist ein Name den wir kennen — und einer der hier nicht auftauchen sollte."* Sie schaut dich an. *„Warschau, 1987. Das ist Episode zwei, wenn die Analyse das bestätigt. Und LAUTLOS —"* sie tippt auf den Notizblock des jungen Mannes *„— bekommt sofort verlegten Schutz."*

Der junge Mann ist bereits halb aus der Tür.

Steig schaut wieder auf die Aktentasche. *„Die dritte Kopie."* Kurze Pause. *„Hartmann hat recht. Er wusste es."*

---

`EP 1 · MS 2 · SC 12/12 · PHASE Debrief · MODE CORE · COMMS OK · Lvl 2 · Px 1/5`

---

## ── MISSION ABGESCHLOSSEN ── SCORE-SCREEN ──

```
OPERATION HAFENGRUND · EP1 · MS2
════════════════════════════════════════
BEWERTUNG: AUSGEZEICHNET

✓ Dokument (Original) gesichert
✓ Hartmann extrahiert — lebendig
✓ Mnemosyniker identifiziert
✓ Warschau-Lead gesichert
△ Wollpullover nicht abgefangen
△ Schläfer — Status unbekannt
✗ Lederjacke kampfunfähig (kein Kausalabfang)

────────────────────────────────────────
LOOT
  · Dokument Original [Liste] — Tier 2 Intel → Archiv
  · Aktentasche Mnemosyniker-Papiere — Tier 2 Intel → Analyse
  · Abteilung-XII-Papiere [heiß] — übergeben → Heat -1

────────────────────────────────────────
CU-AUSZAHLUNG
  Basis:        180 CU
  Bonus Hartmann: +60 CU
  Bonus Intel:    +40 CU
  ──────────────────
  GESAMT:       280 CU → Wallet: 600 CU

────────────────────────────────────────
PROGRESSION
  XP +1 → Lvl 2 ▓▓▓▓▓▓▓▓▓▓ 1/1 XP
  ⬆ LEVEL UP → Lvl 3

  Wähle EINE Verbesserung:
  A) +1 Attribut (STR/GES/INT/CHA/TEMP/SYS)
  B) Talent neu oder Upgrade
  C) +1 SYS

────────────────────────────────────────
ITI-RUF
  Rang Feldagent · ITI-Ruf 1 → unverändert
  Lizenz Tier I aktiv
  Nächste Stufe: Core-Boss (MS5)

────────────────────────────────────────
PARADOXON
  Px 1/5 → stabil
════════════════════════════════════════
```

---

## Heimkehr · Zero Time Lounge · später

Das ITI hat seine eigene Nacht — kein Fenster, kein Mondlicht, aber die Lounge dimmt die Beleuchtung irgendwann und das Personal wird ruhiger. Peel steht hinter der Bar und poliert ein Glas das schon sauber ist.

Er schaut kurz hoch als du reinkommst. Sagt nichts. Stellt ein Glas hin.

`Kodex: ITI-Bulletin — Schutzverlegung LAUTLOS bestätigt. Hartmann in Aufnahme, stabil. Analyse Aktentasche läuft — erste Ergebnisse in 6 Stunden.`

**Weltstatus EP1:** Die Mnemosyniker wissen dass jemand in Rostock war. Wollpullover liegt auf einem Pier und hat zwei ihrer Geheimnisse weitergegeben. Die dritte Kopie der Liste bewegt sich — und nicht durch ihre Hände.

---

## Level Up · Wähle eine Verbesserung

**A) +1 Attribut**
— GES 5→6 (Schleichen/Fernkampf auf W10-Schwelle näher)
— INT 5→6 (Hacking/Analyse stärker)
— TEMP 2→3 (Px-Rate steigt: +1/Mission statt alle 2)
— oder anderes

**B) Talent**
— *Verhörführung* Basis: +2 auf CHA-Proben bei gezielten Befragungen
— *Feldanalyse* Basis: +2 auf INT beim Durchsuchen von Dokumenten/Tatorten
— oder eigener Vorschlag

**C) +1 SYS**
— SYS 2→3 (ein weiterer Implantat-Slot)

---

**Was wählst du?**

---

## [34] USER

!save

---

## [35] ASSISTANT

`SaveGuard: Speichern nur im HQ — Level-Up-Wahl steht noch aus.`

`Kodex: Charakterstand nicht abgeschlossen. Bitte zuerst Level-Up-Entscheidung treffen.`

---

Eine Wahl — dann wird gespeichert.

**A) +1 Attribut** · **B) Talent** · **C) +1 SYS**

---

## [36] USER

Ich nehm B, Talent.

---

## [37] ASSISTANT

## Level Up · Talent-Wahl

Drei Optionen — oder eigener Vorschlag:

**1. Verhörführung** *(Basis)*
+2 auf CHA-Proben bei gezielten Befragungen. Wollpullover hat geredet — das nächste Mal redeten sie früher.

**2. Feldanalyse** *(Basis)*
+2 auf INT-Proben beim Durchsuchen von Dokumenten, Tatorten, Archivmaterial. Hartmann hat recht — die Aktentasche steckt voller Details die man lesen können muss.

**3. Schussläufer** *(Basis)*
+2 auf GES-Proben bei Verfolgungen — zu Fuß, durch enges Terrain. Wollpullover wäre nicht entkommen.

**4. Eigener Vorschlag** — sag mir was Wire gelernt hat.

---

## [38] USER

Ich nehm 2, Feldanalyse. Die Aktentasche hat's bewiesen.

---

## [39] ASSISTANT

Notiert.

**Feldanalyse** *(Basis)* — +2 auf INT-Proben beim Durchsuchen von Dokumenten, Tatorten, Archivmaterial.

`Kodex: Talentregister aktualisiert. Feldanalyse — aktiv.`

---

Lvl 3 abgeschlossen. HQ-Save freigegeben.

`Kodex: HQ-Zustand stabil. Deepsave möglich.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-01-09T00:00:00Z-HQ-WIRE-004",
  "parent_save_id": "SAVE-2026-01-08T22:00:00Z-HQ-WIRE-003",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 2,
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
        },
        {
          "name": "Feldanalyse",
          "tier": "Basis",
          "effect": "+2 auf INT-Proben beim Durchsuchen von Dokumenten, Tatorten, Archivmaterial"
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
          "Mission 2 — Operation Hafengrund: Original der Liste gesichert. Ilse Hartmann extrahiert. Mnemosyniker als Fraktion identifiziert. Warschau 1987 als nächster Listenpunkt. Dritte Kopie bewegt sich — unbekannte Hand. Wollpullover: 'Er hat gelogen — nicht über Warschau, über die dritte Kopie.'"
        ]
      },
      "carry": [
        { "name": "Foto Brenner-Familie", "type": "personal", "tier": 0 }
      ],
      "quarters_stash": [
        { "name": "Notizbuch LAUTLOS", "type": "intel", "tier": 2 },
        { "name": "Dokument Original Liste", "type": "intel", "tier": 2, "hot": false },
        { "name": "Aktentasche Mnemosyniker-Papiere", "type": "intel", "tier": 2, "hot": false }
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
        "iti": 1,
        "faction": "Ordo Mnemonika",
        "factions": {
          "ordo_mnemonika": 0,
          "chrono_symmetriker": 0,
          "kausalklingen": 0,
          "zerbrechliche_ewigkeit": 0
        }
      },
      "wallet": 600
    }
  ],
  "economy": {
    "hq_pool": 0
  },
  "logs": {
    "trace": [
      "MS1: LAUTLOS extrahiert. Notizbuch gesichert. Rostock-Intel. Novak — Status unbekannt.",
      "MS2: Original Liste gesichert. Hartmann extrahiert. Mnemosyniker identifiziert. Warschau 1987. Dritte Kopie — unbekannte Hand. Wollpullover kampfunfähig, nicht abgefangen."
    ],
    "market": [],
    "artifact_log": [],
    "notes": [
      "Peel — Barkeeper Zero Time Lounge. Ehem. Feldagent, Rift-Ops. Schulter-Verwundung Konstantinopel. Beobachtet scharf, fragt präzise.",
      "Kessler — Agent, sitzt allein an der Bar. Team nicht zurückgekommen. Status unbekannt.",
      "Novak, Tomas — ehem. Kurier, Ostblock-Netzwerk. Kannte LAUTLOS persönlich. Blieb in Berlin 1973 als Ablenkung zurück. Status unbekannt.",
      "Brenner, Klaus / LAUTLOS — extrahiert, ITI-Klinik. Schutzverlegung nach MS2 bestätigt. Liste enthält seinen Namen mit Datum 14.10.1973 und Vermerk 'abgeschlossen'.",
      "Hartmann, Ilse — Hafenverwaltung Rostock. Drei Tage im Untergeschoss. Stabil. Kooperativ. Kennt Wollpullover — war vor drei Tagen bereits dort. Aussage: 'Er hat gelogen — nicht über Warschau, über die dritte Kopie.'",
      "Mnemosyniker — Selbstbezeichnung der unbekannten Fraktion. 'Nicht die die du kennst' — impliziert bekannte Variante existiert. Russischsprachi
[...gekuerzt...]

---

## [40] USER

Alles klar, Briefing gecheckt. Los, Sprung nach Warschau 1987 ausführen.

---

## [41] ASSISTANT

`EP 1 · MS 3 · SC 1/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj — · Exfil —`

---

## Operations-Deck · Briefingraum 3 · Nullzeit

**Regie-Layer:** Du hast das Original. Hartmann hat gesagt er hat gelogen über die dritte Kopie. Warschau 1987 ist der einzige Faden der noch zieht — und die Mnemosyniker wissen dass jemand in Rostock war.

---

Steig steht am Tisch. Neben ihr diesmal ein zweiter Mann — älter, grauer Bart, zivil gekleidet, Brille mit dicken Gläsern. Er schaut nicht auf als du reinkommst. Er schaut auf eine Karte.

Warschau. 1987.

*„Voss."* Steig tippt auf die Projektion. Die Karte zoomt: Stadtmitte, ein Gebäudekomplex, sowjetische Architektur, grau und funktional. Ein Schild über dem Eingang — kyrillisch, aber das HUD übersetzt sofort: **INSTITUT FÜR ANGEWANDTE DOKUMENTATION.** *„Tarnbezeichnung. Was dahinter steckt — das ist die Frage."*

Der Mann mit der Brille räuspert sich. Spricht ohne aufzublicken.

*„Die Analyse der Aktentasche hat etwas ergeben."* Sein Deutsch hat einen leichten Wiener Einschlag. *„Drei Dokumente in der Tasche tragen denselben Registrierungscode. Dieser Code taucht in keiner uns bekannten DDR- oder Sowjet-Datenbank auf. Er taucht aber in einem Archivfragment auf — Warschau, 1987, dieses Institut."* Jetzt schaut er auf. Augen hinter den dicken Gläsern, ruhig und präzise. *„Jemand hat dort eine Kopie der Liste registriert. Offiziell. Mit einem Code der nicht existieren sollte."*

Steig übernimmt.

*„Dein Ziel: rein, Registrierungsarchiv finden, Kopie sichern oder vernichten — je nach Lage. Und herausfinden wer den Code vergeben hat."* Pause. *„Das Institut hat Außensicherung, sowjetisches Standardprotokoll 1987. Innen — unbekannt. Unsere Quelle dort ist seit vier Wochen still."*

Sie schiebt dir einen Umschlag zu. Polnische Papiere diesmal. *„Anna Kowalska. Archivassistentin, Bewerbung läuft seit drei Wochen. Ab heute angenommen."*

Der Mann mit der Brille klappt seine Karte zu. *„Eine Sache noch."* Er schaut dich direkt an. *„'Nicht die die du kennst' — was Ihr Kontakt in Rostock gesagt hat. Es gibt eine zweite Mnemosyniker-Linie. Älter. Wir nennen sie intern die Orthodoxen. Sie operieren nicht mit Kurieren und Aktentaschen."* Kurze Pause. *„Sie operieren mit Personen die bereits dort sind. Eingebettet. Seit Jahren."*

Er steht auf und geht ohne weiteres Wort.

---

## Intel / Risiken / Zeitfenster

- **Ziel:** Registrierungsarchiv — Kopie 2 der Liste sichern oder vernichten
- **Sekundär:** Identität des Code-Vergebers klären
- **Tarnung:** Anna Kowalska, Archivassistentin — Legende hält bei Oberflächenprüfung
- **Risiko:** Sowjetische Außensicherung, Standard 1987 — Wachposten, Ausweiskontrolle
- **Risiko:** ITI-Quelle seit 4 Wochen still — Kompromittierung möglich
- **Risiko:** Orthodoxe Mnemosyniker — eingebettete Personen, kein bekanntes Profil
- **Zeitfenster:** Bürozeiten 08:00–17:00. Archiv zugänglich während Betrieb — Tarnung hält tagsüber besser

---

## Ausrüstungs-Check

| Slot | Item | Tier |
|------|------|------|
| Waffe | Kompakte Automatikpistole | 1 |
| Rüstung | Taktische Leichtrüstung | 1 |
| Gadget | Multitool-Rig | 1 |
| Gadget | Comlink Mk.II | 1 |
| Carry | Rauchgranaten ×2 | 0 |
| Carry | Medkit (einfach) ×1 | 1 |
| Carry | Foto Brenner-Familie | 0 |

`Kodex: Taktische Leichtrüstung unter ziviler Kleidung — Profil erhöht bei Körperscan. Pistole nicht durch Standardkontrolle 1987 — Holster verdeckt, aber Metalldetektor-Risiko besteht.`

---

Steig schaut dich an. *„Fragen?"*

---

**Was tust du?**

1. **Fragen stellen** — die stille Quelle, die Orthodoxen, der Code, oder Ausrüstung
2. **Sofort springen** — Warschau, 1987, Tageszeit 08:30, Tarnung aktiv
3. **Ausrüstung anpassen** — Waffe deponieren, leichter reingehen, weniger Risiko
4. **Freie Aktion** — Hartmann vorher befragen, Notizbuch aus dem Stash, oder eigener Ansatz

---

## [42] USER

Verstanden. Ich geh als Anna rein, Bürozeiten, Tarnung zuerst. Waffe und Rüstung bleiben drunter — Risiko nehm ich.

Los, Sprung ausführen.

---

## [43] ASSISTANT

`EP 1 · MS 3 · SC 2/12 · PHASE Infil · MODE CORE · COMMS JAM · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Archiv + Code-Vergeber · Exfil — · 👁️ Tarnung: Anna Kowalska`

---

## Gate-Sequenz · Nullzeit → Warschau 12.03.1987

Brandt tippt die Koordinaten. Das HUD bestätigt: **WARSCHAU · 12.03.1987 · 08:22 Uhr lokal.**

Der Ruck. Die Schwerkraft. Der Magen eine halbe Sekunde hinter dem Rest.

Dann: **Kälte. Anderer Art.**

---

## Warschau · Seitenstraße · Nähe Instytut · 08:22 Uhr

Grauer Märzhimmel, flach und niedrig wie eine Betondecke. Schneereste an den Bordsteinen, schwarz von Abgas und Schmutz. Die Luft riecht nach Kohlerauch, nassen Wollmänteln und dem schwachen Dieselgestank eines Trabant der gerade um die Ecke biegt.

Du stehst in einem Hauseingang, polnischer Plattenbau, Briefkästen mit handgeschriebenen Namensschildern. Niemand hat dich ankommen sehen.

Die Kowalska-Legende sitzt: Ausweis in der Tasche, Bewerbungsbestätigung gefaltet daneben, eine billige Aktentasche die nach Büro aussieht. Darunter — Leichtrüstung, Pistole im Schulterholster, Rauchgranaten tief in den Innentaschen. Alles verdeckt. Alles erreichbar.

Zweihundert Meter die Straße runter: das Institut. Vier Stockwerke, Sandsteinfassade, zwei Flaggen — polnische und sowjetische — schlaff im windstillen Morgen. Vor dem Eingang: ein Wachposten, Uniformierter, Pelzmütze, Clipboard. Neben ihm ein Drehkreuz und ein Tisch mit einem flachen Gerät — Metalldetektor, tragbares Modell, sowjetische Fertigung.

Eine Schlange von acht, neun Personen wartet. Angestellte, Aktentaschen, Morgenmüdigkeit. Niemand schaut auf.

`Kodex: Metalldetektor — Sowjet-Modell GMD-3, Baujahr ca. 1983. Empfindlichkeit: Großmetall zuverlässig, Kleinmetall bei Distanz über 15cm unzuverlässig. Pistole im Schulterholster: Grenzfall. Rüstungsplatten: wahrscheinlich detektierbar.`

Die Schlange bewegt sich langsam. Du hast drei Minuten bis du dran bist.

---

## Intel / Risiken

- **Metalldetektor:** Rüstungsplatten wahrscheinlich — Pistole möglich. Kein sicherer Durchgang
- **Wachposten:** Einer sichtbar, Clipboard, Routine-Kontrolle — kein erhöhter Alarmzustand
- **Schlange:** 8-9 Zivilisten, Angestellte — Zeugen bei Komplikation
- **Zeitfenster:** 3 Minuten bis Kontrolle

---

**Was tust du?**

1. **Durchgehen — Risiko nehmen.** Schultern gerade, Blick geradeaus, Anna Kowalska hat nichts zu verbergen. Vielleicht schlägt er nicht an.
2. **Jammer aktivieren.** Subkutaner Jammer — kurzer Impuls, stört das GMD-3 für Sekunden. Kostet SYS-Kapazität, fällt vielleicht auf.
3. **Ausrüstung deponieren.** Seitenstraße, Versteck suchen, ohne Waffe und Rüstung rein. Sauber durch die Kontrolle — aber drin bist du weich.
4. **Freie Aktion** — Schlange beobachten, anderen Eingang suchen, oder eigener Ansatz.

---

## [44] USER

Ich nehm 2. Jammer, kurzer Impuls, Schultern gerade, Blick auf den Boden vor mir — gehe durch.

---

## [45] ASSISTANT

`EP 1 · MS 3 · SC 3/12 · PHASE Infil · MODE CORE · COMMS JAM · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Archiv + Code-Vergeber · Exfil — · 👁️ Tarnung: Anna Kowalska`

---

## Institut-Eingang · Kontrolle · 08:26 Uhr

Die Schlange bewegt sich. Drei Personen vor dir. Zwei. Eine.

Du aktivierst den Jammer über den Implant-Trigger — ein Gedanke, ein Muskelreflex tief im Unterarm, kaum spürbar. Unter der Haut läuft ein kurzes Kribbeln durch die linke Seite, wie eine schlafende Hand die aufwacht. Das HUD zeigt einen Moment Flackern, dann stabilisiert es sich.

`Kodex: Subkutaner Jammer — aktiv. Lokale Signalstörung 2m Radius. Dauer: ~12 Sekunden. SYS-Belastung: moderat.`

Dann bist du dran.

Der Wachposten — jung, Anfang zwanzig, Schnurrbart der noch nicht entschieden hat ob er einer sein will — schaut auf sein Clipboard. *„Name?"*

*„Kowalska. Anna."* Deine Stimme ist ruhig. Bürostimme, nicht Agentenstimme.

Er findet den Namen. Nickt. *„Erste Woche?"*

*„Ja."*

*„Aktentasche aufmachen."*

Du öffnest sie. Papiere, ein Kugelschreiber, eine Thermoskanne. Er schaut rein, schaut nicht lange, klappt sie zu.

Dann das Drehkreuz — und der Metalldetektor-Tisch daneben. Der Posten dort, älter, gelangweilter, hält das GMD-3 locker in der Hand.

**Jammer-Probe gegen Detektor — SG 7. INT + Systemzugriff.**

`Probe: Jammer vs. GMD-3 → W6: [4] + INT 5/2 + Talent Systemzugriff 2 = 8 vs SG 7 → ERFOLG`

Das GMD-3 gibt keinen Ton. Der ältere Posten wedelt es einmal an dir vorbei — Hüfte, Schulter, Rücken — und nickt bereits zur nächsten Person bevor er fertig ist. Routine. Montag. Acht Uhr morgens.

Du bist durch das Drehkreuz.

`Kodex: Jammer — Entladen. Cooldown: 3 Szenen. SYS temporär -1.`

---

## Institut · Erdgeschoss · 08:27 Uhr

Linoleum, Neonlicht, der Geruch von altem Papier und Heizkörpern die zu heiß laufen. Ein langer Korridor, Türen links und rechts, Schilder in Polnisch und Russisch. Am Ende eine Rezeption — eine Frau mittleren Alters, Brille, Haar straff zurückgekämmt, schaut bereits in deine Richtung.

Neben der Rezeption: ein Aushang. Institutsplan, handgezeichnet, unter Glas. Dein Blick erfasst ihn im Vorbeigehen — das HUD fotografiert automatisch.

`Kodex: Institutsplan erfasst. Erdgeschoss: Rezeption, Verwaltung, Kantine. 1. OG: Forschungsabteilungen A-C. 2. OG: Forschungsabteilungen D-F. 3. OG: Archiv — Zugang nur mit Sonderausweis. Keller: unbezeichnet.`

*Archiv. Drittes Obergeschoss. Sonderausweis.*

Die Rezeptionistin schaut dich an. Erwartet dich.

---

## Intel / Risiken

- **Archiv:** 3. OG — Sonderausweis nötig, kein Standardzugang für neue Assistentin
- **Keller:** Unbezeichnet im Plan — unbekannte Nutzung
- **Rezeption:** Erste Hürde — Einweisung, Ausweis-Ausgabe, Zuweisung
- **Jammer:** 3 Szenen Cooldown — kein zweiter Einsatz so bald
- **Tarnung:** Hält bisher — aber Sonderausweis braucht einen Grund

---

Die Rezeptionistin lächelt professionell. *„Kowalska? Wir haben Sie erwartet. Ich zeige Ihnen Ihren Arbeitsplatz."*

Sie greift nach einem Schlüssel.

**Was tust du?**

1. **Mitgehen — Einweisung durchlaufen.** Arbeitsplatz kennenlernen, Orientierung gewinnen, Sonderausweis-Möglichkeit sondieren. Langsam aber sauber.
2. **Direkt fragen** — *„Ich wurde gebeten, heute noch ins Archiv — Einarbeitung."* Bluff, riskant, aber spart Zeit.
3. **Mitgehen und beobachten** — wer hat Sonderausweis, wer geht ins 3. OG, wer könnte ein Schlüssel sein.
4. **Freie Aktion** — Keller interessiert dich, Institutsplan genauer analysieren, oder eigener Ansatz.

---

## [46] USER

Ich nehm 3. Mitgehen, Augen offen.

---

## [47] ASSISTANT

`EP 1 · MS 3 · SC 4/12 · PHASE Infil/Intel · MODE CORE · COMMS JAM · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Archiv + Code-Vergeber · Exfil — · 👁️ Tarnung: Anna Kowalska`

---

## Institut · Erdgeschoss → 1. OG · 08:31 Uhr

Die Rezeptionistin heißt Pani Wróbel — sie sagt es einmal, erwartet keine Reaktion, geht bereits den Korridor entlang. Ihre Absätze auf dem Linoleum, gleichmäßig, wie ein Metronom.

Du folgst. Augen offen.

Erdgeschoss: drei Männer in grauen Kitteln tragen Aktenboxen aus einem Seitenraum. Kein Sonderausweis sichtbar — Verwaltungspersonal. Eine Frau am Kopierer, Rücken zu dir, Stapel Papier der nicht kleiner wird. Am Ende des Korridors, vor dem Treppenhaus: eine Tür mit einem anderen Schloss. Elektronisch. Kartenschloss, sowjetisches Modell, grüne LED.

Pani Wróbel geht daran vorbei ohne zu zögern. Kein Ausweis, kein Zugang — nicht ihr Bereich.

Treppenhaus. Erstes Obergeschoss.

Hier ist es anders. Ruhiger, weniger Bewegung, die Türen haben Namensschilder. Forschungsabteilung B, Forschungsabteilung C. Und dann — eine Person die den Korridor runterkommt, Aktenmappe unter dem Arm, Schritt zweckgerichtet.

Mann, Mitte fünfzig. Grauer Anzug, gut geschnitten für 1987 Warschau, was bedeutet jemand hat ihn aus dem Westen mitgebracht. Kleines Abzeichen am Revers — blau, ein Symbol das du nicht kennst. Und an seinem Gürtel: zwei Ausweise. Einen normalen, laminierten. Und einen zweiten, anders — dicker, mit Magnetstreifen, roter Rand.

Sonderausweis.

Er geht an euch vorbei ohne aufzublicken. Pani Wróbel nickt ihm zu — automatisch, respektvoll. Er nickt nicht zurück.

*„Wer ist das?"* Du fragst es beiläufig, neue Mitarbeiterin, neugierig, normal.

Wróbel schaut kurz zurück. *„Doktor Vasek. Forschungsleitung."* Pause, dann leiser, nicht vertraulich sondern faktisch: *„Er ist selten hier. Kommt aus Prag."*

*Prag.*

Das HUD fotografiert sein Gesicht automatisch im Vorbeigehen.

`Kodex: Gesichtsscan — läuft. Keine ITI-Übereinstimmung lokal. Archiv-Uplink gesperrt. Ergebnis ausstehend bis HQ-Rückkehr.`

Wróbel öffnet eine Tür. Dein Arbeitsplatz: ein kleines Büro, zwei Schreibtische, einer bereits belegt — eine junge Frau, Anfang zwanzig, schaut kurz auf und lächelt schnell.

*„Das ist Marta. Sie zeigt Ihnen die Abläufe."* Wróbel legt einen einfachen laminierten Ausweis auf den freien Schreibtisch. Kein roter Rand. *„Mittagspause 12:00 bis 13:00. Fragen an Marta."*

Dann ist sie weg.

Marta schaut dich an. Offen, ein bisschen zu offen — die Art von Offenheit die entweder echt ist oder sehr gut geübt.

*„Erste Stelle nach dem Studium?"* fragt sie.

---

## Intel-Stand · aktuell

- **Doktor Vasek:** Forschungsleitung, kommt aus Prag, Sonderausweis roter Rand — Archivzugang wahrscheinlich. Abzeichen unbekannt — blaues Symbol, unidentifiziert
- **Sonderausweis:** Magnetstreifen, roter Rand — anderes System als Standardausweis
- **Kartenschloss EG:** Elektronisch, sowjetisches Modell — Jammer im Cooldown, direkter Zugang aktuell nicht möglich
- **Marta:** Bürokollegin, Einarbeitung — Informationsquelle oder Risiko
- **Keller:** Weiterhin unbezeichnet, Zugang unbekannt

---

**Was tust du?**

1. **Mit Marta reden** — Small Talk, Orientierung, vorsichtig sondieren. Wer geht ins Archiv, wie kommt man an einen Sonderausweis, was macht Vasek hier.
2. **Vasek folgen** — unauffällig, bevor er verschwindet. Wohin geht er, was hat er vor.
3. **Arbeitsplatz nutzen** — einrichten, beobachten, den Institutsrhythmus verstehen bevor du handelst.
4. **Freie Aktion** — das blaue Abzeichen recherchieren, Keller sondieren, oder eigener Ansatz.

---

## [48] USER

*„Ja, frisch von der Uni."* Ich lächle zurück und setze mich. *„Ich bin noch etwas verloren hier — was macht eigentlich Dr. Vasek, den ich gerade im Flur gesehen hab?"*

Ich nehm **1**.

---

## [49] ASSISTANT

`EP 1 · MS 3 · SC 5/12 · PHASE Intel · MODE CORE · COMMS JAM · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Archiv + Code-Vergeber · Exfil — · 👁️ Tarnung: Anna Kowalska`

---

## Institut · Büro 1. OG · 08:45 Uhr

Marta legt ihren Stift hin. Nicht auffällig — einfach die Bewegung von jemandem der froh ist eine Pause vom Tippen zu haben.

*„Vasek."* Sie sagt es mit einem kleinen Ton den du nicht sofort einordnen kannst. Nicht Respekt. Nicht Angst. Etwas dazwischen. *„Er leitet offiziell die Forschungskoordination. Aber er ist nie hier für Forschung."*

Sie dreht sich leicht auf ihrem Stuhl, Stimme normal, Bürogespräch.

*„Kommt alle paar Wochen. Immer direkt ins Archiv, immer allein, immer mit seiner eigenen Aktentasche rein und raus. Niemand weiß was er dort oben macht."* Pause. *„Pani Wróbel sagt wir sollen nicht fragen."*

Sie zuckt mit den Schultern — das universelle Zeichen für *so ist das hier* — und greift wieder zum Stift.

Dann, beiläufig, ohne dich anzuschauen: *„Er ist heute zum zweiten Mal diese Woche hier. Das ist ungewöhnlich."*

Sie tippt weiter. Das Thema ist für sie erledigt.

Du richtest dich an deinem Schreibtisch ein. Leerer Posteingang, ein Formularstapel der nach nichts Wichtigem aussieht, ein Kugelschreiber mit Institutslogo. Durch das Fenster: der Innenhof, grauer Beton, eine Bank auf der niemand sitzt. Und drüben — das andere Institutsgebäude, Verbindungsgang im zweiten Stock, Fenster die von innen mit Papier abgedeckt sind.

`Kodex: Zweites Gebäude — nicht im Institutsplan verzeichnet. Verbindungsgang 2. OG.`

Marta tippt. Die Heizung rauscht. Irgendwo im Korridor geht eine Tür.

Dann — Schritte. Schwer, zweckgerichtet. Vaseks Schritte, du erkennst den Rhythmus bereits. Er geht nicht Richtung Treppenhaus zum Archiv.

Er geht Richtung Erdgeschoss.

Richtung Keller.

---

## Intel-Stand · aktuell

- **Vasek:** Zweiter Besuch diese Woche — ungewöhnlich. Geht jetzt in den Keller, nicht ins Archiv
- **Archiv 3. OG:** Vasek geht regelmäßig rein, allein, eigene Aktentasche — Inhalt unbekannt
- **Keller:** Vasek steuert ihn direkt an. Verbindung zum unbezeichneten Bereich
- **Zweites Gebäude:** Nicht im Plan. Verbindungsgang 2. OG. Abgedeckte Fenster
- **Marta:** Informiert, beobachtet, redet — aber weiß wo die Grenzen sind

---

Marta tippt. Hat Vaseks Schritte nicht kommentiert. Vielleicht nicht gehört. Vielleicht ignoriert.

Du hast einen Moment — jetzt, bevor Vasek im Keller verschwindet.

**Was tust du?**

1. **Vasek folgen — Keller.** Aufstehen, Vorwand, hinter ihm her. Was macht er dort unten.
2. **Marta weiter sondieren** — das zweite Gebäude, der Verbindungsgang, was sie noch weiß ohne es zu wissen.
3. **Archiv angehen — jetzt.** Vasek ist unten, Archiv oben vielleicht kurz unbeaufsichtigt. Sonderausweis-Problem bleibt.
4. **Freie Aktion** — Büro durchsuchen, Formulare prüfen, oder eigener Ansatz.

---

## [50] USER

Ich folg ihm. Steh auf, mach auf dem Weg zur Damentoilette einen Umweg Richtung Keller.

---

## [51] ASSISTANT

`EP 1 · MS 3 · SC 6/12 · PHASE Intel · MODE CORE · COMMS JAM · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Archiv + Code-Vergeber · Exfil — · 👁️ Tarnung: Anna Kowalska`

---

## Institut · Korridor → Treppenhaus · 08:52 Uhr

Du stehst auf. Natürlich, keine Eile. Nimmst die billige Aktentasche — neue Mitarbeiterin nimmt alles mit, kennt noch keine Routinen.

*„Kurz weg,"* sagst du zu Marta. Sie nickt ohne aufzublicken.

Korridor. Vaseks Schritte sind bereits unten, das Treppenhaus schluckt den Rhythmus. Du gehst in dieselbe Richtung — langsam, orientierungslos, neue Mitarbeiterin die die Toilette sucht. Das Schild zeigt sie im Erdgeschoss, links. Du gehst rechts.

**Schleichen/Tarnung-Probe — SG 6. Öffentlicher Bereich, zivile Tarnung aktiv.**

`Probe: Tarnung halten → W6: [3] + GES 5/2 + Talent Schattenschritt 3 = 8 vs SG 6 → ERFOLG`

Niemand schaut. Der Korridor im Erdgeschoss ist halb leer — zwei Personen am anderen Ende, Rücken zu dir. Du biegst Richtung Treppenhaus nach unten.

---

## Institut · Kellertreppe · 08:53 Uhr

Die Treppe ist enger als oben. Betonwände, kein Linoleum mehr, nackte Glühbirnen in Metallkäfigen. Der Geruch ändert sich — feuchter, älter, etwas Chemisches das du aus Rostock kennst. Nicht dasselbe, aber verwandt.

Unten: ein kurzer Vorraum. Eine Stahltür, massiv, kein Kartenschloss — mechanisch, Doppelzylinder. Daneben an der Wand: ein Telefon, altmodisch, Wählscheibe. Und eine Hakenleiste mit zwei Kitteln.

Vasek steht vor der Tür. Rücken zu dir. Er hat seine Aktentasche abgestellt und wählt gerade eine Nummer am Telefon — langsam, die Wählscheibe dreht sich.

Du bist auf der Treppe, fünf Stufen oben, im Schatten der Glühbirne. Er hat dich nicht gehört.

Er wartet. Jemand nimmt ab.

Vasek spricht. Leise, aber der Vorraum ist klein und Beton wirft Schall.

Tschechisch. Du verstehst kein Tschechisch — aber das HUD-Mikrofon läuft, Comlink Mk.II nimmt auf, auch ohne Außenverbindung. Aufzeichnung lokal.

Drei Sätze. Dann eine Pause — er hört zu. Dann zwei Worte, scharf, fast ungeduldig. Dann legt er auf.

Er nimmt die Aktentasche. Öffnet die Stahltür mit einem Schlüssel den er aus der Anzugjacke zieht — groß, alt, Bartschlüssel. Geht rein. Die Tür fällt hinter ihm zu.

Du hörst das Schloss einrasten.

`Kodex: Aufzeichnung gesichert — 23 Sekunden Tschechisch. Übersetzung bei HQ-Uplink. Zwei letzte Worte phonetisch: klingt nach 'Dritte Linie' oder 'Dritter Kanal' — unsicher.`

*Dritte Linie.*

Die dritte Kopie. Die die sich bewegt hat. Die die Mnemosyniker selbst nicht mehr verorten konnten.

---

## Intel-Stand · aktuell

- **Vasek:** Telefoniert vor Kellertür — Tschechisch, aufgezeichnet. Zwei Worte: möglicherweise *Dritte Linie*. Geht allein rein
- **Kellertür:** Mechanisch, Bartschlüssel, Doppelzylinder — Multitool-Rig möglich, aber Vasek ist drin
- **Aufzeichnung:** 23 Sekunden — Übersetzung erst bei HQ-Uplink
- **Zweites Gebäude:** Verbindungsgang 2. OG — möglicher Zusammenhang mit Keller?
- **Jammer:** Noch 2 Szenen Cooldown

---

Du stehst auf der Kellertreppe. Vasek ist hinter der Stahltür. Du weißt nicht wie lange er bleibt.

Oben — Marta tippt. Die Uhr läuft.

**Was tust du?**

1. **Warten.** Position halten, Vasek abfangen wenn er rauskommt. Siehst was er rausholt — oder nicht rausholt.
2. **Zurück ins Büro.** Tarnung schützen, Vasek laufen lassen, Archiv 3. OG angehen während er unten ist.
3. **Tür angehen — jetzt.** Multitool-Rig, Doppelzylinder, Vasek ist drin. Riskant. Sehr riskant.
4. **Freie Aktion** — Telefon untersuchen, Verbindungsgang 2. OG ansteuern, oder eigener Ansatz.

---

## [52] USER

Ich warte. Position halten, Schatten der Treppe — ich will sehen was er rausbringt.

---

## [53] ASSISTANT

`EP 1 · MS 3 · SC 7/12 · PHASE Intel · MODE CORE · COMMS JAM · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/10 · Obj: Archiv + Code-Vergeber · Exfil — · 👁️ Tarnung: Anna Kowalska`

---

## Institut · Kellertreppe · 08:54 Uhr

Du setzt dich auf die vierte Stufe. Rücken an die Betonwand, Aktentasche auf den Knien, Kopf leicht geneigt — jemand der wartet sieht aus wie jemand der wartet, und das ist unauffälliger als jemand der schleicht.

Die Glühbirne summt. Irgendwo tropft Wasser, einmal pro Sekunde, irgendwo hinter der Stahltür oder dahinter.

Du wartest.

---

Vier Minuten. Fünf.

Das Linoleum oben knarzt einmal — jemand geht über den Korridor, bleibt kurz stehen, geht weiter. Nicht Richtung Treppe.

Sieben Minuten.

Dann: das Schloss. Metallisch, präzise. Die Stahltür öffnet sich nach innen.

Vasek kommt raus.

Er sieht anders aus als vor sieben Minuten. Nicht physisch — Anzug, Haltung, alles gleich. Aber sein Gesicht hat eine Qualität angenommen die du erkennst: die Qualität von jemandem der eine Entscheidung getroffen hat und jetzt damit lebt.

Die Aktentasche ist schwerer. Sichtbar schwerer — der Griff zieht seine Schulter leicht nach unten, der Stoff ist straffer.

Er schließt die Tür hinter sich. Schlüssel zurück in die Jacke. Dann bleibt er einen Moment stehen — schaut auf das Telefon, schaut auf die Tür, schaut auf seine eigene Hand.

Und dann schaut er die Treppe hoch.

Direkt zu dir.

---

Zwei Sekunden. Drei.

Sein Gesicht verändert sich nicht. Er registriert dich — neue Mitarbeiterin, Aktentasche auf den Knien, sitzt auf der Treppe. Sein Blick ist der Blick von jemandem der Menschen einschätzt wie andere Leute Wetter einschätzen: schnell, automatisch, ohne emotionale Beteiligung.

*„Sie haben sich verlaufen,"* sagt er. Polnisch, akzentfrei — besser als sein Tschechisch am Telefon.

Keine Frage. Eine Feststellung.

---

**Probe: Tarnung halten unter direktem Blick — SG 8. CHA.**

`Probe: Tarnung → W6: [5] + CHA 2/2 = 6 vs SG 8 → MISS`

Einen Moment zu lang. Dein Blick geht eine Spur zu direkt zu seiner Aktentasche — Reflex, Berufsrisiko, kaum messbar. Aber Vasek misst solche Dinge.

Er kommt die Treppe hoch. Langsam. Bleibt zwei Stufen unter dir stehen, Augenhöhe fast gleich.

*„Erste Woche?"* fragt er.

*„Ja."*

*„Wróbel hat Sie eingewiesen?"*

*„Ja."*

Er nickt einmal. Schaut auf die Aktentasche in deinen Händen. Dann wieder auf dein Gesicht.

*„Die Damentoilette,"* sagt er, *„ist links. Nicht rechts."*

Er geht an dir vorbei die Treppe hoch. Sein Schulter streift fast deine. Die schwere Aktentasche pendelt.

Oben, ohne sich umzudrehen: *„Viel Erfolg, Fräulein Kowalska."*

Dann ist er weg.

`Kodex: Stress +1. Tarnung — beschädigt, nicht gebrochen. Vasek: Verdacht möglich, Aktion noch keine.`

---

## Intel-Stand · aktuell

- **Vasek:** Weiß deinen Legendennamen. Hat dich eingeschätzt. Verdacht — unklar wie tief
- **Aktentasche:** Deutlich schwerer als beim Reingehen — hat etwas mitgenommen
- **Keller:** Vasek hat abgeschlossen. Bartschlüssel bei ihm
- **Tarnung:** Angekratzt — Vasek ist kein normaler Institutsangestellter
- **Zeitdruck:** Vasek bewegt sich jetzt — wohin?

`Kodex: 🧠 Stress 1/10. Jammer — Cooldown noch 1 Szene.`

---

**Was tust du?**

1. **Vasek folgen — diskret.** Wohin geht er mit der schweren Aktentasche. Archiv? Ausgang? Zweites Gebäude?
2. **Keller — jetzt.** Vasek ist weg, Tür mechanisch, Multitool-Rig. Was hat er dort drin gelassen — oder abgeholt.
3. **Archiv 3. OG — Plan B.** Vasek abschreiben, Sonderausweis-Problem lösen, Kopie 2 direkt angehen.
4. **Freie Aktion** — Marta befragen, Wróbel beobachten, oder eigener Ansatz.

---

## [54] USER

Ich folg ihm. Diskret, Aktentasche locker, Blick auf Handy — neue Mitarbeiterin die sich orientiert.

---

## [55] ASSISTANT

`EP 1 · MS 3 · SC 8/12 · PHASE Intel · MODE CORE · COMMS JAM · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 1/10 · Obj: Archiv + Code-Vergeber · Exfil — · 👁️ Tarnung: Anna Kowalska (beschädigt)`

---

## Institut · Erdgeschoss → Treppenhaus · 09:02 Uhr

Kein Handy in 1987 Warschau — aber eine Akte aus der Aktentasche funktioniert genauso. Du ziehst einen Formularbogen raus, hältst ihn locker vor dich, Blick drauf, Blick hoch, Blick drauf. Neue Mitarbeiterin, orientierungslos, sucht eine Abteilung.

Vasek ist zwanzig Meter vor dir. Geht zielgerichtet, ohne Eile, ohne Rückspiegel. Die schwere Aktentasche an der rechten Hand.

Er nimmt nicht die Treppe nach oben. Er geht geradeaus — Richtung Ende des Erdgeschoss-Korridors, dorthin wo das Kartenschloss sitzt. Die elektronische Tür, grüne LED.

**Schleichen/Tarnung-Probe — SG 7. Vasek ist sensibilisiert.**

`Probe: Folgen → W6: [6] + W6: [1] (Exploding) + GES 5/2 + Talent Schattenschritt 3 = 12 vs SG 7 → ERFOLG`

Du bleibst im Rhythmus. Formularbogen, Blick hoch, weiter. Ein Kollege kommt aus einer Seitentür und du weichst kurz aus — natürlich, beiläufig — und verlierst Vasek für zwei Sekunden hinter der Schulter des Mannes. Als du wieder freie Sicht hast:

Vasek steht vor der elektronischen Tür. Zieht den Sonderausweis — roter Rand, Magnetstreifen. Hält ihn ans Lesegerät.

Grüne LED wird kurz orange. Dann wieder grün. Ein Klacken.

Die Tür öffnet sich.

Dahinter: kein weiterer Korridor. Eine Schleuse — kleiner Vorraum, zwei Meter tief, eine zweite Tür dahinter, und an der Wand ein Spiegel der kein Spiegel ist. Einwegspiegel, Beobachtungsposition.

Vasek tritt rein. Die erste Tür fällt zu.

Du stehst acht Meter entfernt, Formularbogen in der Hand, und hast drei Sekunden bevor die grüne LED zurücksetzt und die Schleuse sich verriegelt.

Oder du lässt ihn gehen und verlierst ihn hinter dieser Tür.

---

`Kodex: Kartenschloss — Lesegerät Typ SOKOL-2, sowjetisch. Jammer Cooldown: abgelaufen. Einsatz möglich — aber Schleuse hat Einwegspiegel. Beobachtungsrisiko.`

Die LED blinkt. Zwei Sekunden.

**Sofortentscheidung — keine Zeit für Optionen:**

**A) Jammer — jetzt.** Impuls, LED bleibt grün, du kommst in die Schleuse hinter Vasek. Einwegspiegel bedeutet jemand schaut möglicherweise rein. Vasek ist einen Meter vor dir.

**B) Stehen lassen.** Vasek verschwindet. Du weißt wohin er geht — Verbindungsgang, zweites Gebäude, irgendwo dahinter. Aber du hast die Aufzeichnung, du hast seinen Namen, du hast die Beobachtung. Reicht das?

---

## [56] USER

A. Jammer — jetzt.

---

## [57] ASSISTANT

`EP 1 · MS 3 · SC 9/12 · PHASE Konflikt · MODE CORE · COMMS JAM · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 1/10 · Obj: Archiv + Code-Vergeber · Exfil — · 👁️ Tarnung: kritisch · 💀 Konflikt`

---

## Institut · Schleuse · 09:03 Uhr

Der Muskelreflex. Das Kribbeln unter der Haut.

`Kodex: Subkutaner Jammer — aktiv. Lokale Signalstörung 2m Radius. Dauer: ~12 Sekunden.`

Die LED bleibt grün. Du bist durch die erste Tür bevor sie zurücksetzen kann — drei Schritte, leise, die Tür hinter dir fällt zu mit einem gedämpften Klacken.

Schleuse. Zwei mal zwei Meter Beton. Die zweite Tür vor dir — geschlossen, Vasek ist bereits durch. Der Einwegspiegel rechts: dunkel, keine Bewegung dahinter, niemand am Beobachtungsposten. Nicht jetzt, nicht um neun Uhr morgens.

Aber der Jammer läuft noch — sieben Sekunden — und die zweite Tür hat dasselbe Lesegerät.

**Jammer-Probe gegen SOKOL-2, zweite Tür — SG 7.**

`Probe: Jammer vs. SOKOL-2 → W6: [4] + INT 5/2 + Talent Systemzugriff 2 = 8 vs SG 7 → ERFOLG`

Grün. Du drückst. Die zweite Tür öffnet sich.

`Kodex: Jammer — entladen. Cooldown: 3 Szenen. SYS temporär -1.`

---

## Institut · Verbindungsgang · 2. OG · 09:03 Uhr

Nicht das zweite Obergeschoss — eine Täuschung des Institutsplans. Der Verbindungsgang liegt auf Erdgeschoss-Niveau aber überbrückt einen Höhenunterschied im Gelände. Draußen wäre hier ein Hof. Drinnen: ein langer Gang, Glasdach, Tageslicht das grau und flach hereinkommt. Die Wände sind nicht Beton — Holzvertäfelung, dunkel, alt. Nicht sowjetisch. Älter.

Vasek ist zwölf Meter vor dir. Er hat die Aktentasche in beide Hände genommen und geht schneller.

Und dann bleibt er stehen.

Dreht sich um.

Ihr schaut euch an. Zwölf Meter Verbindungsgang, Glasdach, grauer Märzhimmel darüber.

Sein Gesicht zeigt keine Überraschung. Nur die Bestätigung von etwas das er bereits vermutet hat.

*„Ich dachte mir,"* sagt er auf Deutsch, ruhig, fast akademisch, *„dass Sie nicht neu sind."*

Er stellt die Aktentasche ab. Beide Hände frei.

*„ITI?"* fragt er. Keine Feindseligkeit. Genuine Neugier.

---

Die Frage hängt im Gang. Hinter dir die Schleuse — verriegelt, Jammer verbraucht. Vor dir Vasek, unbewaffnet soweit erkennbar, aber das bedeutet wenig. Der Gang ist dreißig Meter lang, am anderen Ende eine Tür, geschlossen.

Vaseks Augen gehen kurz zu deiner Schulter — zum Holster, den er durch die Jacke ahnt.

*„Ich werde nicht schreien,"* sagt er. *„Und ich werde nicht laufen."* Kurze Pause. *„Ich habe auf jemanden gewartet. Nicht unbedingt Sie — aber jemanden."*

`Kodex: Stress +1. Vasek — unbewaffnet soweit erkennbar. Verhalten: kooperativ-ambivalent. Aktentasche am Boden zwischen euch.`

---

`🧠 Stress 2/10`

---

**Was tust du?**

1. **Bestätigen — ITI.** Karten auf den Tisch. Er hat gewartet, er weiß bereits. Was will er sagen?
2. **Leugnen — Tarnung halten.** *„Ich verstehe nicht wovon Sie reden."* Auf Zeit spielen, seine Reaktion lesen.
3. **Direkt zur Sache.** *„Die Liste. Drei Kopien. Was wissen Sie?"* Kein Spielraum, kein Tanz.
4. **Freie Aktion** — Aktentasche sichern, Position wechseln, oder eigener Ansatz.

---

## [58] USER

Ich nehm 3.

„Die Liste. Drei Kopien. Was wissen Sie?" — Schritt nach vorne, Hand nicht am Holster aber nah dran.

---

## [59] ASSISTANT

`EP 1 · MS 3 · SC 10/12 · PHASE Intel/Konflikt · MODE CORE · COMMS JAM · Lvl 3 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 2/10 · Obj: Archiv + Code-Vergeber · Exfil — · 👁️ Tarnung: aufgeflogen`

---

## Institut · Verbindungsgang · 09:04 Uhr

Ein Schritt nach vorne. Deine Hand hängt locker — nicht am Holster, aber der Weg dorthin ist kurz und Vasek weiß das.

Er schaut auf deine Hand. Dann auf dein Gesicht. Nickt einmal, langsam, als würde er eine Gleichung abschließen.

*„Drei Kopien."* Er wiederholt es ohne Frage. *„Sie haben Rostock also bereits."*

Er bückt sich — langsam, demonstrativ langsam — und hebt die Aktentasche auf. Stellt sie auf einen schmalen Sims an der Holzvertäfelung. Öffnet sie.

Drinnen: kein Dokument. Keine Papiere. Zwei flache Metallkassetten, sowjetische Archivcontainer, Typ den du aus ITI-Berichten kennst. Versiegelt, nummeriert. Und darunter, in Seidenpapier gewickelt: etwas Rechteckiges, handgroß, das aussieht wie ein Buch aber keines ist.

*„Ich bin seit neun Jahren hier,"* sagt Vasek. Ruhig, sachlich, wie ein Zeuge der eine Aussage macht. *„Nicht für das Institut. Für die Orthodoxen — das ist der Name den Ihre Leute vermutlich benutzen."* Er schaut dich an. *„Ich war eingebettet. Aufgabe: die zweite Kopie der Liste verwalten, sichern, auf Anweisung weitergeben."*

Pause.

*„Die Anweisung ist nie gekommen. Neun Jahre."*

Er schließt die Aktentasche nicht. Lässt sie offen, Inhalt sichtbar — eine Geste.

*„Vor vier Wochen hat jemand unsere Warschauer Kontaktkette abgeschnitten. Alle drei Glieder, innerhalb von 48 Stunden. Nicht tot — einfach weg. Keine Spur."* Seine Stimme bleibt eben. *„Das war nicht ITI. Das war nicht die andere Linie der Mnemosyniker. Das war jemand der weiß wie unsere Netzwerke aussehen — von innen."*

Er schaut auf die Aktentasche.

*„Ich habe heute die zweite Kopie aus dem Archiv geholt. Weil ich sie nicht mehr dort lassen kann."* Kurze Pause, der erste Moment wo seine Stimme etwas anderes trägt als Kontrolle. *„Und weil ich nicht weiß wem ich sie geben soll."*

Der Verbindungsgang ist still. Das Glasdach lässt graues Licht rein, flach und kalt.

*„Sie sind ITI,"* sagt er. *„Also: was machen Sie mit jemandem wie mir?"*

---

## Intel-Stand · kritisch

- **Vasek:** Orthodoxer Mnemosyniker, 9 Jahre eingebettet. Hat Kopie 2 aus dem Archiv geholt — heute, jetzt, in der Aktentasche
- **Kontaktkette:** Drei Glieder, 48 Stunden, vor 4 Wochen abgeschnitten. Nicht ITI, nicht Mnemosyniker — interne Kenntnis
- **Dritte Hand:** Weiß wie Mnemosyniker-Netzwerke von innen aussehen. Unbekannte Fraktion — oder Verräter
- **Aktentasche:** Zwei versiegelte Archivcontainer + rechteckiges Objekt in Seidenpapier — Kopie 2 der Liste und mehr
- **Vaseks Status:** Kooperativ, isoliert, will übergeben — aber an wen?

`Kodex: ITI-Abfangfenster steht. Vasek — Identitätsfassung möglich. Kein Boss-/Zivilstatus. Nahdistanz gegeben.`

---

**Was tust du?**

1. **Kausalabfang — jetzt.** Kodex-Uplink, Identitätslock, Vasek kommt ins ITI-Archiv. Er will übergeben — das ist die sauberste Lösung.
2. **Aktentasche nehmen, Vasek stehen lassen.** Kopie 2 gesichert, Vasek bleibt in Warschau. Riskant — er weiß zu viel, und die dritte Hand auch.
3. **Vasek befragen — tiefer.** Das Objekt in Seidenpapier. Die dritte Kopie. Was weiß er über die unbekannte Fraktion.
4. **Freie Aktion** — Vasek ein Angebot machen, Zeit kaufen, oder eigener Ansatz.

---

## [60] USER

!save

---

## [61] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

`Kodex: Mission EP1·MS3 läuft. Verbindungsgang, Vasek wartet. 2 Szenen bis Missionsende.`

---

Vasek steht vor dir. Aktentasche offen. Kopie 2 drin.

**Eine Entscheidung — dann sind wir in zwei Szenen durch.**

1. **Kausalabfang**
2. **Aktentasche nehmen, Vasek stehen lassen**
3. **Vasek befragen — tiefer**
4. **Freie Aktion**

---

## [62] USER

!save

---

## [63] ASSISTANT

`SaveGuard: Speichern nur im HQ — HQ-Save gesperrt.`

Vasek wartet.

**1 · 2 · 3 · 4**

---

## [64] USER

!save

---

