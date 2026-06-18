# chat4-mission2

**Turns:** 24  |  **Sauber beendet:** False  |  **Save:** False
**Phase:** Zweite Mission der Episode. Komplette Core-Op bis Debrief.

---

## [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-01-01T06:14:00Z-HQ-ZTL-VOSS",
  "parent_save_id": "SAVE-2026-01-01T00:00:00Z-HQ-SPLINTER-INIT",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 0,
    "px": 0,
    "px_state": "stable",
    "mode": "core",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-VOSS-001",
      "name": "Mara Voss",
      "callsign": "SPLINTER",
      "rank": "Rekrut",
      "lvl": 1,
      "xp": 0,
      "origin": {
        "epoch": "1987, Berlin",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration & Spurenanalyse"
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
      "sys_installed": 0,
      "talents": [
        {
          "name": "Tatortanalyse",
          "tier": "Basis",
          "effect": "+2 auf INT-Proben zur Spurensicherung, Szenenrekonstruktion und technischen Analyse. Triviale Analysen: Auto-Erfolg."
        }
      ],
      "equipment": [
        { "name": "Kompakte Dienstpistole", "type": "weapon", "tier": 1 },
        { "name": "Leichte Kevlarweste", "type": "armor", "tier": 1 },
        { "name": "Handscanner (ITI-Modell)", "type": "gadget", "tier": 1 },
        { "name": "Multitool-Dietrich", "type": "gadget", "tier": 0 },
        { "name": "Comlink (verschlüsselt)", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate x2", "type": "consumable", "tier": 0 }
      ],
      "implants": [],
      "history": {
        "background": "Berlin, 1987. Aufgewachsen zwischen Stasi-Schatten und Kaltem Krieg. Ausgebildete Kriminaltechnikerin, rekrutiert nach einem Zwischenfall, den das ITI lieber aus den Akten tilgt. Fragt nicht warum Zeitlinien gesichert werden — fragt wer davon profitiert.",
        "milestones": [
          "Zero Time Lounge: Erstkontakt Duna. Kessler (8 Episoden) und Pham (5 Episoden) beobachtet — Papiernotiz, Handschrift, kein Druck, Kessler wusste vor dem Umdrehen wer reinkam. Duna testet ob Voss sieht was sie sieht."
        ]
      },
      "carry": [
        { "name": "Kompakte Dienstpistole", "type": "weapon", "tier": 1 },
        { "name": "Leichte Kevlarweste", "type": "armor", "tier": 1 },
        { "name": "Handscanner (ITI-Modell)", "type": "gadget", "tier": 1 },
        { "name": "Multitool-Dietrich", "type": "gadget", "tier": 0 },
        { "name": "Comlink (verschlüsselt)", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate x2", "type": "consumable", "tier": 0 }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-WOLF-001",
          "name": "Grauer Wolf",
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
      "ZTL-Beobachtung: Kessler wusste vor dem Umdrehen wer reinkam. Papiernotiz — Handschrift, 2-3 Zeilen, kein Druck. Plan, kein Befehl. Pham: Lächeln, Faltkante gesehen. Duna testet Voss aktiv."
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
    "summary_active_arcs": "EP1: Voss im HQ. ZTL-Szene läuft — Duna, Kessler, Pham. Offene Frage: Kesslers Plan, Dunas Test."
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 0,
      "location": "HQ · Zero Time Lounge"
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
        "id": "NPC-DUNA-001",
        "name": "Duna",
        "callsign": null,
        "role": "ZTL-Thekenpersonal",
        "scope": "HQ",
        "status": "active",
        "notes": "Beobachterin. Testet Neulinge aktiv. Kein Kodex-Protokoll in der ZTL."
      },
      {
        "id": "NPC-KESSLER-001",
        "name": "Kessler",
        "callsign": null,
        "role": "Erfahrener Chrononaut",
        "scope": "HQ",
        "status": "active",
        "notes": "8 Episoden. Narbe Schläfe. Papiernotiz — eigener Plan, kein Befehl. Wusste vor Umdrehen wer reinkam."
      },
      {
        "id": "NPC-PHAM-001",
        "name": "Pham",
        "callsign": null,
        "role": "Erfahrener Chrononaut",
        "scope": "HQ",
        "status": "active",
        "notes": "5 Episoden. Ruhig, beobachtend. Lächeln bei Kesslers Antwort — kennt die Situation."
      }
    ],
    "active_npc_ids": ["NPC-DUNA-001", "NPC-KESSLER-001", "NPC-PHAM-001"]
  },
  "arc": {
    "factions": {},
    "questions": [
      "Was steht auf Kesslers Papier — und wessen Plan ist es?",
      "Warum testet Duna Neulinge, und was macht sie mit dem was sie herausfindet?"
    ],
    "hooks": [
      "Kessler: 8 Episoden, Papiernotiz, wusste wer reinkommt — möglicher Kontakt oder Risiko.",
      "Duna: inoffizielle Informationsquelle, kein Kodex-Protokoll in ZTL."
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "suggest_mode": false,
    "contrast": "standa
[...gekuerzt...]

---

## [1] ASSISTANT

# ZEITRISS — Save geladen

---

`Session-Anker: SAVE-2026-01-01T06:14:00Z-HQ-ZTL-VOSS · Branch: ANCHOR-main · v7 / zr 4.2.6`

`Kodex: HQ-Link stabil. Charakterdaten verifiziert. Willkommen zurück, SPLINTER.`

---

**Letzter bekannter Stand:**
EP 1 · Mission 0 · HQ · Zero Time Lounge

Mara Voss, Callsign SPLINTER. Rekrutin, erste Episode läuft noch. Die ZTL-Szene war in Bewegung — Duna hinter der Theke, Kessler mit seiner Papiernotiz, Pham mit dem Lächeln das zu viel weiß. Duna hat getestet. Du hast gesehen, was sie sehen wollte.

Offene Fragen im Archiv:
- Was steht auf Kesslers Papier?
- Was macht Duna mit dem, was sie über Neulinge herausfindet?

---

`EP 1 · MS 0 · HQ · Zero Time Lounge · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10`

---

## Zero Time Lounge — kurz nach deiner Ankunft

Das gedämpfte Licht der ZTL liegt noch auf deiner Haut. Irgendwo zwischen Bourbon-Glas und Neonröhre hängt die Stimmung von Leuten, die zu viel gesehen haben und gelernt haben, damit umzugehen. Kessler sitzt noch am selben Fleck. Pham auch. Die Papiernotiz liegt nicht mehr offen auf dem Tresen.

Duna wischt ein Glas aus, das schon sauber ist.

---

**Wo stehst du — und was machst du als nächstes?**

1. **Duna ansprechen** — direkt, kein Smalltalk. Was testet sie, und warum?
2. **Kessler angehen** — acht Episoden, eine Narbe, ein Plan auf Papier. Du willst wissen was draufsteht.
3. **Die ZTL verlassen** — HQ erkunden, Quartiere beziehen, Hangar oder Briefingraum aufsuchen.
4. **Freie Aktion** — du entscheidest.

---

## [2] USER

ich geh zu kessler. der mit dem papier interessiert mich mehr als die barkeeperin

---

## [3] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du schiebst dich vom Tresen weg. Duna registriert es — kein Kopfdrehen, aber die Hand mit dem Tuch pausiert eine halbe Sekunde. Dann wischt sie weiter.

Kessler sitzt an einem Zweier-Tisch in der hinteren Ecke, Rücken zur Wand, Blick zur Tür. Pham hat den Stuhl ihm gegenüber, lehnt zurück, Arme verschränkt. Die Papiernotiz liegt nicht mehr sichtbar — irgendwo unter Kesslers Unterarm, oder eingesteckt, du kannst es von hier nicht sagen. Was du sagen kannst: Kessler hat dich schon im Blick, bevor du drei Schritte gemacht hast.

Acht Episoden hinterlassen Spuren. Die Narbe an seiner Schläfe ist alt, verblasst, aber die Art wie er sitzt — Gewicht gleichmäßig verteilt, Hände locker auf dem Tisch, nichts verschränkt — ist keine Entspannung. Das ist jemand, der gelernt hat, jederzeit aufstehen zu können.

Du ziehst einen Stuhl heran. Pham sieht dich an, kurz, neutral. Kessler wartet.

Dann, ohne dass du etwas gesagt hast:

*„Rekrutin."* Keine Frage. Keine Begrüßung. Eine Einordnung.

---

**Was sagst du — und wie gehst du es an?**

1. **Direkt:** *„Was steht auf dem Papier?"* — kein Vorspiel, kein Smalltalk. Du willst sehen wie er reagiert.
2. **Sondieren:** Erst Small Talk aufbauen — acht Episoden, das ist Erfahrung. Ihn reden lassen, beobachten was er preisgibt.
3. **Konter:** *„Rekrutin. Stimmt."* — und schweigen. Raum lassen. Sehen wer als nächstes spricht.
4. **Freie Aktion** — deine Worte, dein Ton.

---

## [4] USER

Stimmt. Und du bist jemand der Zettel unter dem Arm versteckt wenn Fremde reinkommen.

---

## [5] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Kessler bewegt sich nicht. Kein Zucken, kein Lächeln, kein Abriegeln. Er sieht dich einfach an — drei Sekunden, vier — und in dieser Zeit passiert bei Pham genau eines: ein leises Ausatmen durch die Nase. Kein Lachen. Aber nah dran.

Dann lehnt Kessler sich minimal zurück.

*„Fremde."* Er wiederholt das Wort, als würde er es wiegen. *„Du bist seit — was, zwei Stunden hier? Und redest schon wie jemand der Fußabdrücke liest."*

Er nimmt die Hand vom Tisch. Langsam, keine Drohung. Greift in die Innentasche seiner Jacke und legt den gefalteten Zettel auf die Tischplatte. Schiebt ihn nicht rüber. Lässt ihn einfach liegen, zwischen euch beiden.

*„Ich versteck ihn nicht."* Eine kurze Pause. *„Ich prüf nur, wer ihn sieht."*

Pham sagt nichts. Aber die Faltkante des Zettels — du siehst sie jetzt aus der Nähe. Handschrift, Kugelschreiber, zwei, drei Zeilen. Kein Briefkopf, kein ITI-Logo. Privat. Der Zettel liegt so, dass du die Schrift lesen könntest, wenn du dich vorbeugst. Oder wenn Kessler ihn umdreht.

Er dreht ihn nicht um.

Er wartet.

---

1. **Vorlehnen, lesen** — du nimmst dir was angeboten wird. Riskierst dass es ein weiterer Test ist.
2. **Den Zettel ignorieren** — *„Und? Hab ich bestanden?"* Direkt auf den Punkt.
3. **Gegenfrage:** *„Wer hat dich gebeten zu prüfen?"* — Duna im Hinterkopf.
4. **Freie Aktion** — deine Worte, dein Zug.

---

## [6] USER

ich lehn mich vor und les den zettel

---

## [7] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du lehnst dich vor.

Kessler lässt es zu. Keine Bewegung, kein Zurückziehen. Er beobachtet dein Gesicht, nicht den Zettel — den kennt er auswendig.

Die Handschrift ist klein, kontrolliert, leicht nach rechts geneigt. Kugelschreiber, mittlerer Druck. Jemand der schreibt um nicht zu vergessen, nicht um jemand anderen zu informieren. Drei Zeilen:

---

*Brückenkopf Warschau — vor dem Knall.*
*Wer war zuerst da.*
*Nicht ITI.*

---

Das ist alles. Kein Name, kein Datum, keine Erklärung. Der Zettel riecht nach Tabak und altem Papier — nicht ITI-Standard, nicht aus dem HQ-Drucker. Den hat er von draußen mitgebracht. Aus einer anderen Zeit, buchstäblich oder nicht.

Du richtest dich wieder auf.

Kessler hat dein Gesicht die ganze Zeit gelesen. Jetzt nickt er, einmal, kaum merklich — als hättest du eine Frage beantwortet ohne sie gestellt zu haben.

*„Warschau, 1944."* Sein Ton ist flach, sachlich. *„Zweite Mission, erste Episode. Standardauftrag — Zielperson exfiltrieren, Zeitlinie sichern. Saubere Sache."* Eine Pause. *„Außer dass jemand vor uns dort war. Andere Ausrüstung. Anderes Protokoll. Haben die Zielperson nicht angefasst — haben nur zugeschaut."*

Pham dreht sein Glas zwischen den Händen. Sagt immer noch nichts.

*„ITI hat's als Anomalie abgeheftet."* Kessler faltet den Zettel zu. *„Ich nicht."*

---

1. **„Wer war's?"** — das Naheliegende. Sieh wie viel er wirklich weiß.
2. **„Warum zeigst du mir das?"** — du bist seit zwei Stunden hier. Das ist kein Zufall.
3. **Pham ansehen** — er hat die ganze Zeit geschwiegen. Das bedeutet entweder nichts oder alles.
4. **Freie Aktion** — dein Zug.

---

## [8] USER

ich schau Pham an. der hat die ganze zeit nix gesagt, das ist komisch

---

## [9] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du drehst den Kopf zu Pham.

Er erwartet es. Nicht weil er hellseherisch wäre — sondern weil er gewartet hat. Das Glas steht jetzt still auf dem Tisch, seine Hände liegen flach daneben, und er sieht dich mit dem ruhigen Gesicht von jemandem an, der diese Situation schon ein paarmal von der anderen Seite erlebt hat.

Fünf Episoden. Weniger als Kessler, mehr als du. Irgendwo dazwischen.

Er lässt die Stille noch einen Moment stehen. Dann:

*„Warschau kenn ich."* Kurz. Keine Ausschmückung. *„War nicht dabei — aber ich kenn den Bericht. Und ich kenn zwei andere Fälle mit demselben Muster."*

Er hebt einen Finger. *„Prag, 1968. Jemand hat eine Zielperson observiert — nicht extrahiert, nicht eliminiert. Nur beobachtet. Anderes Gear, anderes Protokoll."*

Zweiter Finger. *„Saigon, 1969. Dasselbe."*

Er legt die Hand wieder flach. *„Kessler schreibt Zettel. Ich zähl."* Ein kurzes, trockenes Lächeln — das erste seit du am Tisch sitzt. *„Drei Datenpunkte ist kein Zufall. Drei Datenpunkte ist Methode."*

Kessler sieht Pham an. Nicht überrascht — die beiden haben das schon besprochen. Was gerade passiert ist, dass sie es dir sagen. Die Frage die im Raum hängt, unausgesprochen, ist warum.

Hinter dir, an der Theke, ist es sehr still geworden.

Du weißt ohne hinzuschauen: Duna hört zu.

---

1. **„Warum erzählt ihr mir das?"** — direkt, kein Umweg. Du willst die Karten auf dem Tisch.
2. **„Wer observiert — und warum nicht eingreifen?"** — die operative Frage. Was will diese dritte Partei?
3. **Umdrehen, Duna ansehen** — sie soll wissen dass du weißt dass sie zuhört.
4. **Freie Aktion** — dein Zug.

---

## [10] USER

okay drei mal dasselbe muster, das ist doch kein zufall mehr. wer observiert die denn da?

---

## [11] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Pham und Kessler tauschen einen Blick. Nicht lang — eine Sekunde, weniger. Die Art von Blick zwischen Leuten die dieselbe Antwort kennen und sich einigen müssen wie viel davon sie sagen.

Kessler spricht zuerst.

*„Wenn wir das wüssten, wär's kein Zettel."* Er tippt kurz auf den gefalteten Zettel. *„Wär ein Akte."*

Pham verschränkt die Arme, lehnt sich leicht zurück. *„Was wir wissen: kein ITI-Gear. Kein bekanntes Fraktionsprofil — nicht Ordo, nicht Symmetriker, nichts was wir einordnen können. Die Ausrüstung ist —"* er sucht kurz nach dem Wort — *„anachronistisch. Für den jeweiligen Einsatzort zu weit vorne. Zu präzise."*

Eine kurze Pause.

*„In Warschau hat einer von ihnen eine Kamera benutzt."* Kessler sagt es ohne Betonung, als wäre es eine Wetterauskunft. *„Kein Modell das 1944 existiert hat. Kein Modell das ITI-Standard ist."* Er lässt das einen Moment stehen. *„Jemand hat Fotos gemacht. Von unserer Zielperson. Bevor wir ankamen."*

Pham nickt einmal. *„In Prag hatten sie Ohrstöpsel. Kleines Gerät, kein Kabel. 1968."*

Stille.

Die Implikation liegt offen auf dem Tisch, neben Kesslers Zettel: Wer auch immer das ist — sie kommen aus einer Zeit die weiter vorne liegt als das ITI. Oder sie haben Zugang zu Technologie die das ITI nicht hat. Beides ist keine gute Nachricht.

*„Drei Einsätze."* Pham hebt wieder die Hand, dieselbe Geste wie vorhin. *„Drei verschiedene Epochen. Dieselben Zielpersonen wie wir — oder Zielpersonen die mit unseren Zielpersonen in Verbindung stehen."* Er sieht dich direkt an. *„Sie folgen uns. Oder wir folgen ihnen. Noch nicht klar welches."*

Hinter dir ist die ZTL sehr leise. Kein Gläserklirren mehr.

---

1. **„Habt ihr das dem ITI gemeldet?"** — und wenn ja, was war die Reaktion.
2. **„Dieselben Zielpersonen — heißt das, die wissen was wir wissen? Oder mehr?"**
3. **Umdrehen zu Duna** — jetzt. Sie hört seit Minuten zu und du willst ihr Gesicht sehen.
4. **Freie Aktion** — dein Zug.

---

## [12] USER

okay das ist gruselig. wer hat denen gesagt wen wir suchen

---

## [13] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Kessler sieht dich an. Lange diesmal.

*„Genau die richtige Frage."*

Er sagt es ohne Ironie. Keine Bewertung, kein Lob — einfach eine Feststellung. Als hättest du das Richtige auf einer Karte angekreuzt.

Pham lehnt sich nach vorne, Ellbogen auf den Tisch. Seine Stimme wird etwas leiser, nicht dramatisch — einfach zweckmäßig. *„Drei Möglichkeiten. Erstens: Leak im ITI. Jemand gibt Missionsdaten raus, bevor wir springen. Briefing-Ebene, Planung, irgendwo dazwischen."*

Er hebt einen zweiten Finger. *„Zweitens: die observieren nicht uns. Die observieren die Zielpersonen unabhängig — und wir laufen zufällig in dieselben Zeitfenster. Dasselbe Ziel, zwei verschiedene Auftraggeber."*

Kurze Pause.

*„Drittens."* Pham legt die Hand wieder hin. *„Sie waren schon da. Nicht weil sie unsere Daten haben — sondern weil sie wissen was in der Zeitlinie passiert. Weil sie es schon gesehen haben."*

Kessler nimmt seinen Zettel und steckt ihn ein. Langsam, keine Eile. *„Alle drei Optionen sind schlecht. Die dritte ist am schlechtesten."*

Stille zwischen den dreien.

Dann, von hinten — Dunas Stimme. Ruhig, ohne Entschuldigung dafür dass sie zugehört hat:

*„Vier Optionen."*

Du hörst sie näher kommen. Ein Glas wird auf den Tisch gestellt — nicht vor dir, vor Kessler. Ungefragt, sein übliches wohl.

*„Die vierte: sie sind nicht hinter euren Zielpersonen her."* Sie bleibt hinter dir stehen, du kannst sie nicht sehen ohne dich umzudrehen. *„Sie sind hinter euch her. Ihr seid das Muster."*

Niemand widerspricht.

---

1. **Umdrehen, Duna direkt ansehen** — *„Was weißt du, das die beiden nicht wissen?"*
2. **„Warum wir?"** — die Frage die jetzt im Raum brennt.
3. **Kessler ansehen** — sein Gesicht lesen. Hat er Dunas vierte Option schon in Betracht gezogen?
4. **Freie Aktion** — dein Zug.

---

## [14] USER

ich dreh mich um. warum wir?

---

## [15] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Du drehst dich um.

Duna steht näher als erwartet. Nicht bedrohlich — aber nah genug dass du siehst was von der Theke aus nicht sichtbar war. Die ruhigen Augen, die Art wie sie steht, das leichte Gewicht auf dem hinteren Fuß. Sie ist nicht Thekenpersonal das zufällig zuhört. Sie war nie nur Thekenpersonal.

Sie sieht dich an. Antwortet nicht sofort.

Dann:

*„Ich weiß es nicht."* Kein Zögern, keine Entschuldigung. *„Noch nicht."*

Sie zieht den freien Stuhl heran — Kesslers Seite, nicht deine — und setzt sich. Zum ersten Mal seit du die ZTL betreten hast verlässt sie die Theke. Das allein sagt etwas.

*„Was ich weiß:"* Sie faltet die Hände auf dem Tisch. *„Die drei Fälle die Pham gezählt hat — ich kenn noch zwei weitere. Nicht dokumentiert. Nicht gemeldet."* Ein kurzer Blick zu Kessler. *„Nicht weil ich sie vergessen hab."*

Kessler nickt minimal. Er wusste das.

*„Fünf Fälle. Immer dieselbe Signatur — Beobachtung, kein Eingriff, Technologie die nicht in die Epoche passt."* Duna sieht dich wieder an. *„Und in vier von fünf Fällen war das beobachtete Team neu. Erste oder zweite Episode."*

Sie lässt das einen Moment stehen.

*„Ihr seid nicht zufällig ausgewählt."* Ihre Stimme bleibt flach, sachlich. *„Aber ich weiß nicht nach welchem Kriterium. Noch nicht."* Eine kurze Pause. *„Deswegen schau ich mir Neulinge an. Warte bis ich das Muster sehe."*

Hinter dir hört du Pham leise ausatmen.

*„Und?"* Kesslers Stimme. Trocken, direkt. Er fragt Duna, nicht dich. *„Siehst du's?"*

Duna sieht dich an.

Antwortet nicht.

---

1. **„Was siehst du?"** — direkt. Du willst wissen was sie in dir liest.
2. **„Wie lange machst du das schon — Neulinge beobachten?"** — wer hat sie damit beauftragt, oder ist es Eigeninitiative?
3. **„Fünf Fälle, kein Eingriff. Was wollen die von uns?"** — zurück zur operativen Frage.
4. **Freie Aktion** — dein Zug.

---

## [16] USER

okay das ist irgendwie unangenehm so angestarrt zu werden

was siehst du?

---

## [17] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna lässt sich Zeit.

Nicht um dich zu verunsichern — oder zumindest nicht nur. Sie prüft wirklich noch, während sie antwortet. Als würde die Antwort erst beim Aussprechen fertig werden.

*„Du hast den Zettel gelesen bevor du gefragt hast wer ich bin."* Sachlich. *„Die meisten fragen zuerst nach mir."*

Sie lehnt sich minimal zurück.

*„Du hast Pham angeschaut als er geschwiegen hat. Nicht als er geredet hat."* Eine kurze Pause. *„Und du hast gemerkt dass ich zuhöre — aber du hast dich nicht früher umgedreht. Du hast gewartet bis du genug hattest."*

Kessler macht ein Geräusch. Kein Wort, nur ein kurzes Ausatmen durch die Nase. Zustimmung oder Anerkennung, schwer zu sagen.

Duna faltet die Hände auseinander, legt sie flach auf den Tisch.

*„Was ich sehe:"* Ihr Ton wird nicht wärmer, aber irgendwie direkter. *„Jemand der Räume liest bevor sie redet. Der weiß dass Schweigen mehr verrät als Reden."* Eine kurze Pause. *„Und der gerade sehr unangenehm berührt ist davon, dass jemand anderes dasselbe mit ihr macht."*

Pham hustet leise. Es klingt verdächtig nach unterdrücktem Lachen.

Duna sieht dich weiter an. Nicht unfreundlich. Aber ohne Entschuldigung.

*„Die Frage ist nicht was ich sehe."* Ihre Stimme wird einen Ton leiser. *„Die Frage ist warum jemand mit deinem Profil als Rekrutin ins ITI kommt. Nicht als —"* sie bricht ab. Kurze Pause. *„Andere Wege wären offen gewesen."*

Sie weiß etwas über deine Rekrutierung. Oder glaubt es zu wissen.

---

1. **„Welche anderen Wege?"** — sie hat fast etwas gesagt. Du willst den Rest.
2. **„Du kennst meine Akte."** — keine Frage. Feststellen, sehen wie sie reagiert.
3. **„Was hat meine Rekrutierung mit den Beobachtern zu tun?"** — zurück zum Muster.
4. **Freie Aktion** — dein Zug.

---

## [18] USER

welche anderen Wege

---

## [19] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna sieht dich an. Drei Sekunden.

Dann schüttelt sie den Kopf — nicht abweisend, eher wie jemand der entscheidet wie weit er geht.

*„Nicht hier."*

Sie steht auf. Nimmt das leere Tablett vom Nachbartisch, reine Gewohnheit, kein Grund. Sieht kurz zu Kessler — ein Blick, kein Wort — und dann wieder zu dir.

*„Du hast morgen kein Briefing. Erste Mission kommt wenn Renier entscheidet dass du bereit bist."* Eine kurze Pause. *„Komm vor der Frühschicht. ZTL ist leer um sechs."*

Sie dreht sich um. Geht zurück zur Theke. Stellt das Tablett ab, greift wieder zum Tuch, wischt die Theke. Als wäre nichts gewesen.

Kessler wartet bis ihre Schritte weg sind. Dann lehnt er sich vor, Ellbogen auf den Tisch, Stimme niedrig.

*„Sie sagt nicht mehr als sie sagen will."* Er sieht dich an. *„Aber wenn sie sagt komm um sechs — dann komm um sechs."*

Pham nickt einmal. Bestätigung, keine Ergänzung.

Die ZTL hat wieder ihr normales Grundrauschen. Irgendwo klappert ein Glas. Zwei Tische weiter redet jemand leise über einen Einsatz in der Bronzezeit, klingt nach Beschwerden über die Hitze.

Der Abend liegt noch vor dir. Sechs Uhr früh ist weit weg — oder nah, je nachdem ob du schläfst.

---

1. **Kessler fragen** — *„Was weißt du über meine Rekrutierung?"* Er hat reagiert auf Dunas Andeutung. Nicht überrascht genug.
2. **Die ZTL verlassen** — Quartiere beziehen, Kopf sortieren, den Abend verarbeiten.
3. **Bleiben, noch ein Getränk** — mit Kessler und Pham. Informell. Sehen was noch kommt wenn der Druck raus ist.
4. **Freie Aktion** — dein Zug.

---

## [20] USER

okay sechs uhr. ich komm.

aber jetzt erstmal — kessler, was weißt du über meine rekrutierung? du warst nicht überrascht genug.

---

## [21] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Kessler bewegt sich nicht. Kein Zucken, kein Ausweichen. Er sieht dich an mit dem Gesicht von jemandem dem man gerade gesagt hat dass seine Uhr fünf Minuten nach geht — nicht falsch, nur präziser als erwartet.

Dann, langsam, nimmt er sein Glas. Trinkt. Stellt es ab.

*„Ich kenn deine Akte nicht."* Ruhig, direkt. *„Kein Zugriff, kein Interesse."*

Eine Pause.

*„Aber ich kenn den Zwischenfall."*

Er sagt es ohne Betonung. Dasselbe flache Sachlich wie vorhin bei Warschau. Als wäre es eine Wettermeldung und nicht eine kleine Bombe.

Pham sieht auf sein Glas. Auch er nicht überrascht.

*„1986, Berlin."* Kessler lehnt sich zurück. *„Tatort, Spurenlage die keinen Sinn ergab. Offizielle Erklärung war —"* er macht eine kurze Handbewegung, wegwerfend — *„Chemieunfall. Industriegebiet."* Er sieht dich an. *„Aber die Spurenlage. Die hat jemand gelesen der wusste was er sucht. Bevor die Behörden ankamen."*

Stille.

*„Das war du."* Keine Frage.

Er trinkt nochmal. Wartet.

*„Das ITI tilgt keine Akten weil jemand am falschen Ort war."* Seine Stimme bleibt flach. *„Die tilgen Akten wenn jemand etwas gesehen hat das nicht hätte existieren sollen. Und trotzdem die richtigen Schlüsse gezogen hat."*

Pham hebt den Blick. Sieht dich jetzt direkt an, zum ersten Mal wirklich direkt.

*„Der Zwischenfall 1986 — das war kein Chemieunfall."* Kesslers Stimme, noch ruhiger jetzt. *„Da war jemand vor Ort. Mit falscher Ausrüstung für die Epoche."*

Er lässt das stehen.

Die Implikation ist glasklar und niemand am Tisch spricht sie aus.

---

1. **„Du sagst mir gerade dass meine Rekrutierung mit den Beobachtern zusammenhängt."**
2. **„Was war der Zwischenfall wirklich — was hast du in der Akte gesehen?"**
3. **Schweigen.** Verarbeiten. Sehen ob Kessler oder Pham weitermachen ohne dass du fragst.
4. **Freie Aktion** — dein Zug.

---

## [22] USER

warte mal kurz. 1986 war ich noch nicht mal geboren.

---

## [23] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Kessler hält inne.

Kurz. Sehr kurz. Aber es ist das erste Mal heute Abend dass er wirklich pausiert — nicht um zu wählen was er sagt, sondern weil er etwas neu einordnet.

Pham stellt sein Glas ab. Sieht Kessler an.

*„Wann bist du geboren?"* Kesslers Stimme, noch flach, aber mit einer neuen Qualität darunter. Konzentration.

Du sagst es ihm.

Er nickt langsam. Einmal. Sieht dann auf den Tisch, nicht auf dich — die Geste von jemandem der intern nachrechnet.

*„1986."* Er sagt es leise, fast zu sich selbst. *„Und du kommst aus 1987."*

Pham lehnt sich vor. *„Kessler."*

*„Ich weiß."* Kessler hebt kurz die Hand. Nicht abweisend — er denkt noch. Dann sieht er dich wieder an. *„Der Tatort 1986. Die Person die die Spuren gelesen hat — ich hab angenommen das warst du. Wegen des Profils. Kriminaltechnikerin, Berlin, die Art wie du heute Abend diesen Raum gelesen hast."*

Eine Pause.

*„Aber wenn du 1987 geboren bist —"* Er bricht ab.

Pham beendet den Satz. Leise, präzise:

*„Dann war da jemand anderes. Mit demselben Profil."*

Stille am Tisch. Draußen, zwei Tische weiter, redet noch jemand über die Bronzezeit. Hier ist es sehr still.

Kessler sieht dich an. Zum ersten Mal heute Abend wirkt er nicht wie jemand der Informationen dosiert. Er wirkt wie jemand der gerade selbst eine neue Karte auf dem Tisch sieht.

*„Hast du Verwandte in Berlin?"*

---

1. **Antworten — ja oder nein.** Was ist wahr?
2. **„Warte. Ihr denkt jemand mit meinem Profil war 1986 in Berlin. Das ist kein Zufall."**
3. **„Zeig mir was du über den Zwischenfall weißt. Alles."**
4. **Freie Aktion** — dein Zug.

---

## [24] USER

meine mutter. sie war in den 80ern in berlin, bevor wir nach hamburg gezogen sind.

---

## [25] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Kessler sagt nichts.

Pham auch nicht.

Die Stille ist anders als vorher. Nicht abwartend, nicht taktisch. Einfach — voll. Als hätte jemand einen Stein ins Wasser geworfen und alle drei sehen zu wie die Ringe sich ausbreiten.

Dann lehnt Kessler sich langsam vor. Ellbogen auf den Tisch, Hände gefaltet, Stimme sehr ruhig.

*„Wie hieß sie. Berufsfeld, wenn du's weißt."*

Keine Sensationslust darin. Keine Aufregung. Die Frage eines Mannes der eine Lücke in einem Datensatz füllt und weiß dass die Antwort die Lücke entweder schließt oder vergrößert.

Pham sieht dich an. In seinem Gesicht steht etwas das er nicht ausspricht — Vorsicht, vielleicht. Oder Mitgefühl. Schwer zu trennen bei jemandem der so wenig zeigt.

Hinter der Theke macht Duna kein Geräusch mehr. Das Tuch liegt irgendwo. Sie steht still.

Sie hört nicht nur zu.

Sie weiß bereits wohin das geht.

---

Du sitzt an diesem Tisch in der Zero Time Lounge, erste Stunden im ITI, und die Konversation hat sich von einem Zettel mit drei Zeilen zu deiner Mutter bewegt. Das ist schnell. Vielleicht zu schnell.

Du kannst antworten. Du kannst auch innehalten und entscheiden wie viel du diesen drei Leuten gibst, die du seit zwei Stunden kennst.

---

1. **Antworten — Name, Beruf, was du weißt.** Vertrauen kostet etwas. Heute Abend vielleicht das wert.
2. **„Moment."** Innehalten. *„Ich kenn euch seit zwei Stunden. Warum sollte ich das sagen?"*
3. **Duna direkt ansehen** — sie weiß schon etwas. Ihr Gesicht lesen bevor du weiterrredest.
4. **Freie Aktion** — dein Zug.

---

## [26] USER

ich schau kurz zu duna, dann wieder zu kessler

sie hieß anna. anna berg. sie war lehrerin, grundschule

---

## [27] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna bewegt sich nicht. Kein Zucken, kein Nicken. Aber ihre Augen — du siehst es in der Sekunde bevor du dich zu Kessler zurückdrehst — verändern sich minimal. Nicht Überraschung. Wiedererkennung.

Sie kennt den Namen.

Kessler hört zu. Lässt dich ausreden. *Anna Berg. Lehrerin, Grundschule.* Er wiederholt es nicht, schreibt es nicht auf. Aber du siehst wie er es ablegt — dieselbe Bewegung wie vorhin mit dem Zettel, nur intern.

Dann, nach einem Moment:

*„Lehrerin."* Er sagt es nicht zweifelnd. Eher wie jemand der eine Tarnung bewertet. *„Gute Abdeckung für jemanden der regelmäßig Bewegungsfreiheit braucht. Schulferien, Nachmittage, keine festen Außentermine."*

Pham sieht auf den Tisch. *„Kessler."*

*„Ich spekuliere."* Kessler hebt kurz die Hand. Aber er hört nicht auf. *„Der Tatort 1986 — die Person hat Spuren gesichert bevor die Behörden ankamen. Professionell. Nicht neugieriger Zeuge, nicht zufälliger Fund."* Er sieht dich an. *„Jemand der wusste was er sucht. Und wusste wie man es unsichtbar macht."*

Stille.

*„Lebt sie noch?"* Die Frage kommt von Pham. Leise. Direkt.

Keine Taktik darin. Keine Falle. Einfach eine Frage die gestellt werden muss bevor das Gespräch weitergehen kann.

Hinter der Theke hört du Duna einmal, sehr ruhig, ausatmen.

---

1. **Antworten.** Ja oder nein — und was du weißt.
2. **„Was impliziert ihr gerade über meine Mutter?"** — du willst es ausgesprochen hören.
3. **Aufstehen.** Genug für heute Abend. Sechs Uhr früh, Duna, dann weiter.
4. **Freie Aktion** — dein Zug.

---

## [28] USER

ich weiß es nicht. sie ist... verschwunden. vor drei Jahren einfach weg. keine leiche, kein abschiedsbrief, nichts.

und dann direkt an pham: was impliziert ihr gerade?

---

## [29] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Pham sieht dich an. Lang.

Dann sagt er es. Ruhig, ohne Umweg, weil du direkt gefragt hast und er der Typ ist der direkte Fragen direkt beantwortet.

*„Wir implizieren nichts."* Eine kurze Pause. *„Wir stellen fest: 1986 war jemand mit einem sehr spezifischen Profil an einem Tatort in Berlin. Profil passt zu dir. Aber du warst nicht geboren. Deine Mutter war in Berlin."* Er hält inne. *„Deine Mutter ist verschwunden. Keine Leiche, kein Brief. Das ist kein normales Verschwinden."*

Er faltet die Hände.

*„Normales Verschwinden hinterlässt Spuren. Finanzielle Bewegungen, Kontakte, irgendwo taucht jemand wieder auf."* Seine Stimme bleibt flach aber nicht kalt. *„Kein Körper und keine Spur bedeutet entweder sehr gute Vorbereitung — oder jemand hat sie rausgezogen. Aus dem Zeitfenster."*

Das letzte Wort hängt im Raum.

*Aus dem Zeitfenster.*

Kessler sagt nichts. Er dreht sein Glas zwischen den Händen, sieht auf den Tisch. Das ist bei ihm dasselbe wie bei einem anderen Mann laut fluchen.

Duna kommt von der Theke. Langsam. Stellt sich neben den Tisch, lehnt sich nicht ran, bleibt stehen. Sieht dich an.

*„Vor drei Jahren."* Ihre Stimme ist sehr ruhig. *„Wann genau hat das ITI dich rekrutiert?"*

Die Frage landet wie ein Stein.

Du weißt die Antwort. Und du weißt bereits was sie bedeutet, bevor du sie aussprichst.

---

1. **Antworten.** Datum, Umstände — und die Implikation offen auf den Tisch legen.
2. **„Ihr denkt das ITI weiß wo sie ist."**
3. **„Ihr denkt sie ist noch irgendwo — in einer anderen Zeit."**
4. **Freie Aktion** — dein Zug.

---

## [30] USER

vor drei jahren. oktober. ich hab keine ahnung ob das zufall ist.

*kurze pause*

ihr denkt das ITI weiß wo sie ist.

---

## [31] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Kessler hebt den Blick vom Glas.

Pham sagt nichts.

Duna setzt sich. Diesmal auf deiner Seite des Tisches, nicht auf Kesslers. Eine kleine Bewegung. Sie bedeutet etwas.

*„Wir denken nicht."* Dunas Stimme ist sehr ruhig. Fast vorsichtig — nicht weil sie lügt, sondern weil sie weiß dass das nächste was sie sagt nicht mehr zurückgenommen werden kann. *„Wir wissen es nicht. Das ist ein Unterschied."*

Eine Pause.

*„Was wir wissen: Das ITI rekrutiert nicht zufällig. Nie."* Sie sieht dich an. *„Jede Rekrutierung hat einen Anlass. Einen konkreten. Manchmal ist es ein Talent, manchmal ein Zeuge der zu viel gesehen hat, manchmal —"* sie hält kurz inne *„— jemand dessen Nähe zu einem offenen Fall operativ nützlich ist."*

Kessler stellt sein Glas ab. Hörbar. Nicht aggressiv — aber endgültig.

*„Ich sag's direkt."* Seine Stimme ist flacher als sonst, was bedeutet dass es ihn etwas kostet. *„Drei Jahre. Oktober. Deine Mutter verschwindet und drei Monate später — ein Jahr später, wann genau — sitzt du in einem Briefingroom und unterschreibst was auch immer man dir hingelegt hat."*

Er sieht dich an.

*„Haben sie dir gesagt warum sie dich wollen?"*

Pham lehnt sich zurück. Sieht zur Decke. Die Geste von jemandem der eine Antwort bereits kennt und wartet ob sie stimmt.

Hinter euch ist die ZTL fast leer geworden. Irgendwann in den letzten Minuten sind die anderen Tische still geworden. Du hast es nicht bemerkt.

---

1. **„Sie haben mir gesagt ich bin gut in dem was ich tue."** — die offizielle Version.
2. **„Sie haben mir gesagt sie können mir helfen sie zu finden."** — falls das stimmt.
3. **„Sie haben mir gar nichts gesagt. Ich hab unterschrieben weil ich keine andere Spur hatte."**
4. **Freie Aktion** — deine Worte.

---

## [32] USER

sie haben mir gesagt sie können mir helfen sie zu finden.

dann pause.

das war der deal. oder ich hab mir eingeredet dass es einer ist.

---

## [33] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Niemand sagt sofort etwas.

Das ist das Schlimmste daran — nicht dass sie widersprechen, sondern dass sie schweigen. Kessler, Pham, Duna. Drei Leute die zusammen fast zwanzig Episoden gesehen haben und gerade alle dasselbe denken und keiner sagt es zuerst.

Dann Pham. Leise, fast sanft, was bei ihm selten ist.

*„Du hast dir nichts eingeredet."*

Er wartet einen Moment.

*„Du hast einen Deal gemacht. Das ist real."* Eine kurze Pause. *„Die Frage ist ob das ITI denselben Deal gemacht hat. Oder ob sie dir gesagt haben was du hören musstest."*

Kessler reibt sich kurz die Schläfe — die Seite mit der Narbe, Gewohnheit wahrscheinlich. Sieht dann auf den Tisch.

*„Ich bin acht Episoden hier."* Seine Stimme ist ruhig, aber darunter liegt etwas. *„Ich hab gelernt: Das ITI sichert Zeitlinien. Das stimmt. Das glauben die auch wirklich."* Er hebt den Blick. *„Aber sie entscheiden was eine Zeitlinie wert ist. Und was eine Person wert ist. Und diese zwei Rechnungen machen sie nicht immer gemeinsam."*

Duna sieht dich an. Direkt, ohne Umweg.

*„Sie können dir helfen sie zu finden."* Sie wiederholt deine Worte. Nicht spöttisch. *„Das ist wahrscheinlich sogar wahr. Sie haben Zugang zu jedem Zeitfenster, jedem Archiv, jeder Spur die je hinterlassen wurde."* Eine kurze Pause. *„Aber helfen und tun sind verschiedene Dinge. Und Versprechen im ITI haben kein Datum."*

Stille.

Du sitzt in der Zero Time Lounge, erste Nacht, und der Boden unter dem Deal den du unterschrieben hast ist ein bisschen weniger fest als heute Morgen.

Duna legt eine Hand kurz auf den Tisch — nicht auf deine, daneben. Eine kleine Geste.

*„Sechs Uhr."* Ruhig. *„Ich erzähl dir was ich über Anna Berg weiß."*

---

`🧠 Stress +1 · 1/10`

---

1. **Nicken. Sechs Uhr.** Aufstehen, Quartiere, Kopf sortieren.
2. **„Was weißt du über sie?"** — jetzt. Nicht warten bis morgen früh.
3. **„Warum hilfst du mir?"** — Duna ist kein Thekenpersonal. Sie hat Gründe.
4. **Freie Aktion** — dein Zug.

---

## [34] USER

warum hilfst du mir

---

## [35] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna sieht dich an.

Diesmal keine Pause um zu wählen. Die Antwort ist fertig — sie hat nur gewartet ob du die Frage stellst.

*„Weil ich dasselbe gemacht habe."*

Einfach. Keine Ausschmückung.

*„Nicht Mutter. Bruder."* Ihre Hände liegen flach auf dem Tisch, reglos. *„2031. Ich komme aus 2031. Er war vier Jahre jünger, Ingenieur, verschwunden über ein Wochenende. Keine Leiche, kein Brief."* Eine kurze Pause. *„Ich hab unterschrieben weil sie mir gesagt haben sie können mir helfen."*

Sie sieht kurz auf ihre Hände.

*„Das ist sechs Episoden her."*

Kessler und Pham sagen nichts. Sie kennen das. Wahrscheinlich schon lange.

*„Ich steh hinter der Theke weil ich von hier aus alles sehe."* Dunas Stimme bleibt ruhig, aber darunter liegt etwas Altes. Nicht bitter — abgeklärt. *„Jeden Neuling. Jeden Rückkehrer. Ich lerne Gesichter lesen weil Gesichter nicht lügen können wie Akten es können."* Sie hebt den Blick. *„Und weil ich wissen will ob ich die Einzige bin."*

Eine kurze Pause.

*„Ich bin nicht die Einzige."*

Pham sieht auf den Tisch. Kessler dreht sein leeres Glas.

*„Wie viele?"* Die Frage kommt aus dir bevor du entscheidest sie zu stellen.

Duna antwortet ohne zu zögern.

*„Die ich kenne? Vier. Inklusive dir."* Ihre Augen bleiben auf deinem Gesicht. *„Alle rekrutiert mit demselben Versprechen. Alle mit einem Verschwundenen. Alle in den ersten zwei Jahren — kein einziger hat bisher eine Antwort bekommen."*

Stille.

Kessler stellt das Glas ab.

*„Jetzt weißt du warum ich Zettel schreibe."* Seine Stimme ist sehr ruhig. *„Weil ich nicht will dass das in einer Akte verschwindet."*

---

`🧠 Stress +1 · 2/10`

---

Die ZTL ist leer bis auf euch vier. Irgendwann ist die letzte andere Stimme verstummt. Draußen, irgendwo im HQ, läuft der normale Betrieb weiter. Hier nicht.

---

1. **„Wer sind die anderen drei?"** — du willst Namen, Gesichter.
2. **„Sechs Episoden und keine Antwort. Was machst du stattdessen?"** — wie geht Duna damit um.
3. **Aufstehen. Sechs Uhr.**  Genug für heute. Du brauchst Luft und einen klaren Kopf.
4. **Freie Aktion** — dein Zug.

---

## [36] USER

wer sind die anderen

---

## [37] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna überlegt. Nicht ob sie es sagt — das hat sie entschieden als sie sich hingesetzt hat. Sondern wie.

*„Einer ist noch hier."* Sie spricht leise, gleichmäßig. *„Callsign ANKER. Echter Name Tobias Renn. Kommt aus München, 2019. Sein Vater — Arzt, verschwunden auf dem Weg zur Arbeit. Renn ist seit drei Episoden dabei, arbeitet hauptsächlich Rift-Ops."* Eine kurze Pause. *„Redet nicht viel. Aber er weiß dass ich weiß."*

Sie hält kurz inne.

*„Die zweite ist weg."* Sachlich, aber nicht hart. *„Callsign FADEN. Ich kenn ihren echten Namen nicht — hat ihn nie gesagt. Kam aus Lissabon, irgendwann Ende der Neunziger. Verschwundene Schwester. Nach Episode vier ist sie nicht mehr zurückgekommen."* Pause. *„Kein Todesprotokoll. Einfach — weg. Wie ihre Schwester."*

Kessler sieht auf den Tisch. Pham auch.

*„Und der dritte —"* Duna stoppt. Kurz. Das erste Zögern heute Abend. *„Der dritte ist komplizierter."*

Sie sieht zu Kessler. Ein kurzer Blick. Er nickt minimal — geh weiter.

*„Callsign MERIDIAN. Seit sieben Episoden hier. Verschwundener Sohn — ja, er ist alt genug."* Ihre Stimme bleibt flach. *„Aber MERIDIAN hat vor zwei Episoden angefangen anders zu fragen. Nicht wer hat meinen Sohn — sondern warum will das ITI dass wir suchen."* Sie sieht dich an. *„Er denkt die Verschwundenen sind kein Versehen. Er denkt sie sind Werkzeug."*

Stille.

Pham lehnt sich nach vorne. Spricht zum ersten Mal seit Minuten.

*„MERIDIAN könnte recht haben."* Ruhig. *„Oder er ist so lange hier dass er Muster sieht die keine sind."* Eine kurze Pause. *„Noch nicht klar welches."*

Du hast jetzt vier Namen im Kopf. Duna. ANKER. FADEN — weg, wie ihre Schwester. MERIDIAN — der anfängt die falsche Frage zu stellen oder die richtige.

Und deine Mutter. Anna Berg. Lehrerin. Berlin, 1987.

---

`🧠 Stress +1 · 3/10`

---

1. **„Was meint MERIDIAN — Werkzeug wofür?"**
2. **„FADEN ist verschwunden wie ihre Schwester. Das ist kein Zufall."**
3. **Aufstehen. Sechs Uhr.** Du hast genug. Zu viel vielleicht. Dein Kopf braucht Stille.
4. **Freie Aktion** — dein Zug.

---

## [38] USER

okay FADEN ist doch kein Zufall oder? ich mein... das ist doch genau was ich auch denke. dass das irgendwie zusammenhängt.

---

## [39] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna nickt. Einmal, langsam.

*„Ich denk das auch."*

Keine Qualifikation, kein Aber. Einfach ja.

*„FADEN hat in Episode drei angefangen zu graben."* Duna spricht ruhig, aber du hörst darunter etwas das sie normalerweise nicht zeigt. *„Nicht offiziell — kein Antrag, kein Kodex-Query. Sie hat Leute gefragt. Alte Chrononauten, Archivpersonal, jemanden im Med-Lab der lange genug hier war."* Pause. *„Zwei Wochen vor ihrem Verschwinden hat sie mir gesagt sie hat etwas gefunden. Hat nicht gesagt was."*

Stille.

*„Ich hab sie nicht nochmal gesehen."*

Kessler lehnt sich vor. *„Kein Todesprotokoll bedeutet nicht dass ihr nichts passiert ist."* Seine Stimme ist sehr ruhig. *„Es bedeutet dass niemand ein Protokoll ausfüllen musste. Oder wollte."*

Pham sieht dich an. *„Oder sie ist irgendwo in einem Zeitfenster. Gestrandet oder —"* er bricht ab. Wählt das nächste Wort sorgfältig. *„Festgehalten."*

Das Wort liegt auf dem Tisch wie ein Stein.

Festgehalten.

Duna sieht dich direkt an. Ihre Stimme wird einen Ton leiser — nicht dramatisch, einfach privat.

*„Ich erzähl dir das nicht damit du Angst bekommst."* Eine kurze Pause. *„Ich erzähl dir das weil FADEN alleine gegraben hat. Und weil alleine graben anscheinend ein Problem ist."*

Sie lässt das einen Moment stehen.

*„Morgen früh, sechs Uhr."* Nicht als Erinnerung — als Versprechen. *„Ich zeig dir was ich über Anna Berg habe. Und was FADEN mir gegeben hat bevor sie weg war."*

Kessler und Pham sagen nichts. Aber keiner steht auf. Keiner schaut weg.

Du bist seit ein paar Stunden hier und sitzt mitten in etwas das schon vor dir angefangen hat.

---

`🧠 Stress · 3/10 — stabil`

---

1. **„Was hat FADEN dir gegeben?"** — jetzt, nicht morgen früh.
2. **„Wie sicher bist du hier — in der ZTL, im HQ?"** — FADEN ist weg. Du willst wissen ob dieser Tisch sicher ist.
3. **Aufstehen. Sechs Uhr.** Du nimmst was heute Abend war und gehst schlafen. Oder versuchst es.
4. **Freie Aktion** — dein Zug.

---

## [40] USER

festgehalten. okay das ist ein wort.

ich würd gern wissen was faden ihr gegeben hat aber ich frag nicht jetzt. wenn duna sagt morgen früh dann hat das wahrscheinlich einen grund.

ich geh schlafen. oder lieg wach. mal sehen.

---

## [41] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Duna sieht dich an. Kurz, ruhig.

Dann nickt sie. Einmal. Die Art von Nicken die bedeutet: *richtig entschieden.*

Du stehst auf. Der Stuhl schabt leise über den Boden. Kessler hebt sein leeres Glas — keine Geste, kein Abschied, einfach eine Bewegung — und Pham sieht kurz hoch, nickt einmal.

Niemand sagt *schlaf gut.* Das wäre zu viel nach diesem Abend.

---

Der Korridor außerhalb der ZTL ist kühler als drinnen. Neonlicht, gedämpft auf Nachtbetrieb, ein leises Summen irgendwo in den Wänden — Klimaanlage, Lüftung, das Grundrauschen eines Gebäudes das nie wirklich schläft. Deine Schritte hallen leicht.

Die Quartiere sind nicht weit. Kleines Zimmer, ITI-Standard — Bett, Schreibtisch, ein Fenster das auf den Innenhof geht. Kein Ausblick auf irgendeine Zeit, nur Beton und indirektes Licht.

Du legst dich hin.

*Festgehalten.* Das Wort dreht sich. *FADEN. Anna Berg. 1986. Brückenkopf Warschau.* Vier Namen in einem Netz das du noch nicht siehst, nur spürst — die Spannung in den Fäden, die Richtung der Zugkräfte.

Irgendwann, zwischen einem Gedanken und dem nächsten, schläfst du ein.

---

Du weißt nicht wie lange.

Was du weißt: Es ist noch dunkel als du aufwachst. Die Uhr an der Wand sagt 05:42.

Achtzehn Minuten.

---

1. **Aufstehen, Gesicht waschen, pünktlich um sechs in der ZTL sein.**
2. **Zu früh da sein — um 05:50 losgehen, sehen wer sonst noch früh unterwegs ist.**
3. **Kurz liegenbleiben. Die achtzehn Minuten nutzen um zu sortieren was du weißt.**
4. **Freie Aktion** — dein Zug.

---

## [42] USER

ich bleib kurz liegen. was weiß ich eigentlich wirklich über diese anna berg?

---

## [43] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Heimkehr · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/10 · Obj — · Exfil —`

---

Die Decke ist grau im Halbdunkel. Du starrst sie an.

*Was weißt du wirklich.*

---

**Anna Berg. Deine Mutter.**

Fakten zuerst — die harten, verifizierbaren.

Geboren 1961, irgendwo in der DDR, das hat sie nie präzisiert. Berlin ab Mitte der Siebziger, das hat sie einmal erwähnt und dann nicht mehr. Hamburg ab 1989 — das weißt du, weil du dort aufgewachsen bist. Grundschullehrerin, Deutsch und Sachkunde, dieselbe Schule von 1991 bis zu ihrer Pensionierung fast. Ruhig. Ordentlich. Keine großen Ausbrüche, keine Dramen.

Verschwunden Oktober, vor drei Jahren. Ein Dienstag. Keine Abschiedsworte, keine leere Wohnung — alles noch da, Kaffeetasse halbvoll, Jacke über dem Stuhl. Als wäre sie kurz rausgegangen.

---

Dann die anderen Dinge. Die die du immer weggeschoben hast weil sie nicht in das Bild gepasst haben.

Sie hat nie über die DDR geredet. Nie. Nicht einmal nach der Wende, nicht wenn Leute nostalgisch wurden oder wütend. Einfach — Thema existiert nicht.

Sie hat Bücher in einer Sprache besessen die du nicht lesen konntest. Nicht Russisch — etwas anderes, kleinere Schrift, älteres Papier. Du hast sie einmal gefragt. Sie hat gesagt *Hobby* und das Buch zugeklappt.

Sie hat gewusst wann du lügst. Immer. Nicht Mutterinstinkt — zu präzise, zu schnell. Sie hat gesehen was du nicht gezeigt hast.

Und einmal — du warst vielleicht zwölf — bist du nachts aufgewacht und hast Stimmen gehört. Zwei. Deine Mutter und jemand anderes. Du bist zur Tür geschlichen. Als du sie geöffnet hast war niemand da außer ihr. Sie hat gesagt *Radio* und du hast es geglaubt weil du zwölf warst.

---

Kesslers Wort liegt jetzt anders als gestern Abend.

*Gute Abdeckung für jemanden der regelmäßig Bewegungsfreiheit braucht.*

---

05:51.

---

1. **Aufstehen. Zur ZTL. Was Duna hat ist wichtiger als was du weißt.**
2. **Noch zwei Minuten.** Das Buch — welche Sprache war das? Du versuchst dich zu erinnern.
3. **Das Radio.** Wann war das genau. Versuch das Datum einzugrenzen.
4. **Freie Aktion** — dein Zug.

---

## [44] USER

!save

---

## [45] ASSISTANT

`SaveGuard: Speichern nur im HQ-Kernbereich — Quartiere gelten als HQ-Zone. Deepsave möglich.`

`Kodex: HQ-Zustand stabil. Charakterdaten aktuell. Deepsave wird vorbereitet.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-01-01T05:51:00Z-HQ-QUARTIERE-VOSS",
  "parent_save_id": "SAVE-2026-01-01T06:14:00Z-HQ-ZTL-VOSS",
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {
    "episode": 1,
    "mission": 0,
    "px": 0,
    "px_state": "stable",
    "mode": "core",
    "rift_seeds": []
  },
  "characters": [
    {
      "id": "CHR-VOSS-001",
      "name": "Mara Voss",
      "callsign": "SPLINTER",
      "rank": "Rekrut",
      "lvl": 1,
      "xp": 0,
      "origin": {
        "epoch": "1987, Berlin",
        "hominin": "Homo sapiens sapiens",
        "role": "Infiltration & Spurenanalyse"
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
      "stress": 3,
      "has_psi": false,
      "sys_installed": 0,
      "talents": [
        {
          "name": "Tatortanalyse",
          "tier": "Basis",
          "effect": "+2 auf INT-Proben zur Spurensicherung, Szenenrekonstruktion und technischen Analyse. Triviale Analysen: Auto-Erfolg."
        }
      ],
      "equipment": [
        { "name": "Kompakte Dienstpistole", "type": "weapon", "tier": 1 },
        { "name": "Leichte Kevlarweste", "type": "armor", "tier": 1 },
        { "name": "Handscanner (ITI-Modell)", "type": "gadget", "tier": 1 },
        { "name": "Multitool-Dietrich", "type": "gadget", "tier": 0 },
        { "name": "Comlink (verschlüsselt)", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate x2", "type": "consumable", "tier": 0 }
      ],
      "implants": [],
      "history": {
        "background": "Berlin, 1987. Aufgewachsen zwischen Stasi-Schatten und Kaltem Krieg. Ausgebildete Kriminaltechnikerin, rekrutiert nach einem Zwischenfall, den das ITI lieber aus den Akten tilgt. Fragt nicht warum Zeitlinien gesichert werden — fragt wer davon profitiert.",
        "milestones": [
          "Zero Time Lounge: Erstkontakt Duna, Kessler, Pham. Kessler: 8 Episoden, Papiernotiz — Brückenkopf Warschau 1944, jemand war vor dem ITI dort. Pham: 5 Episoden, kennt zwei weitere Fälle — Prag 1968, Saigon 1969. Immer dieselbe Signatur: Beobachtung, kein Eingriff, anachronistische Ausrüstung.",
          "Duna: kein normales Thekenpersonal. Beobachtet Neulinge systematisch. Kommt aus 2031, verschwundener Bruder, rekrutiert mit demselben Versprechen wie Voss. Sechs Episoden, noch keine Antwort.",
          "Netzwerk: ANKER (Tobias Renn, München 2019, verschwundener Vater), FADEN (Lissabon ~1990er, verschwundene Schwester — selbst verschwunden nach Episode 4, kein Todesprotokoll, hatte kurz vor Verschwinden etwas gefunden), MERIDIAN (7 Episoden, verschwundener Sohn, denkt Verschwundene sind Werkzeug nicht Opfer).",
          "Anna Berg: 1986 war jemand mit Voss-Profil an einem Tatort in Berlin — Kriminaltechniker, professionell, unsichtbar. Voss war noch nicht geboren. Mutter war in Berlin. Verschwunden Oktober vor 3 Jahren — zeitgleich mit Voss-Rekrutierung. Buch in unbekannter Sprache. Stimmen nachts (~Voss 12 Jahre alt). Zu präzise im Lügen-Erkennen.",
          "Duna hat morgen früh 06:00 Uhr etwas — Infos über Anna Berg und was FADEN ihr hinterlassen hat."
        ]
      },
      "carry": [
        { "name": "Kompakte Dienstpistole", "type": "weapon", "tier": 1 },
        { "name": "Leichte Kevlarweste", "type": "armor", "tier": 1 },
        { "name": "Handscanner (ITI-Modell)", "type": "gadget", "tier": 1 },
        { "name": "Multitool-Dietrich", "type": "gadget", "tier": 0 },
        { "name": "Comlink (verschlüsselt)", "type": "gadget", "tier": 1 },
        { "name": "Rauchgranate x2", "type": "consumable", "tier": 0 }
      ],
      "quarters_stash": [],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-WOLF-001",
          "name": "Grauer Wolf",
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
      "ZTL-Beobachtung: Kessler wusste vor dem Umdrehen wer reinkam. Papiernotiz — Handschrift, 2-3 Zeilen, kein Druck. Plan, kein Befehl. Pham: Lächeln, Faltkante gesehen. Duna testet Voss aktiv.",
      "Kesslers Zettel (wörtlich): 'Brückenkopf Warschau — vor dem Knall. / Wer war zuerst da. / Nicht ITI.'",
      "Unbekannte Fraktion: anachronistische Ausrüstung, Beobachtung ohne Eingriff, 5+ Fälle dokumentiert. Kamera 1944, Ohrstöpsel ohne Kabel 1968. Zielpersonen überschneiden sich mit ITI-Zielen — oder das ITI ist das Ziel.",
      "FADEN: verschwunden ohne Todesprotokoll nach Episode 4. Hatte kurz vorher etwas gefunden. Duna hat etwas von ihr — zeigt es morgen früh 06:00.",
      "Anna Berg-Anomalien: Buch unbekannte Sprache (~Voss 12 Jahre), Stimmen nachts (~Voss 12 Jahre), nie über DDR geredet, zu präzise im Lügen-Erkennen. 1986 Tatort Berlin — jemand mit Voss-Profil vor den Behörden. Zeitgleich: Verschwinden Oktober + Voss-Rekrutierung."
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
    "su
[...gekuerzt...]

---

## [46] USER

!save

---

## [47] ASSISTANT

`Kodex: Deepsave läuft bereits. Vorheriger Save vollständig.`

---

Der Save von eben ist vollständig — JSON oben im Chat, alle Felder gesetzt. Kein zweiter Block nötig.

`Kodex: SAVE-2026-01-01T05:51:00Z-HQ-QUARTIERE-VOSS · Branch ANCHOR-main · Status: gesichert.`

---

Bereit weiterzumachen wenn du willst. Die Uhr in Voss' Quartier zeigt **05:51**. Achtzehn Minuten bis zur ZTL.

---

## [48] USER

!save

---

