# chat5-mission3

**Turns:** 24  |  **Sauber beendet:** False  |  **Save:** False
**Phase:** Dritte Mission. Komplette Core-Op bis Debrief.

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

`Kodex: Session-Anker gesetzt. SAVE-2026-01-01T06:14:00Z · CHR-VOSS-001 · Branch ANCHOR-main.`
`Kodex: Letzter bekannter Standort: HQ · Zero Time Lounge. Kontinuität intakt.`

---

## Rückblick · SPLINTER

**Mara Voss. Callsign: SPLINTER. Rekrut, Episode 1, noch keine Mission auf dem Buckel.**

Die Zero Time Lounge. Du bist neu, aber deine Augen sind nicht neu — die haben zwölf Jahre Kriminaltechnik hinter sich, Tatortfotos um drei Uhr morgens, Stasi-Akten die man besser nicht gelesen hätte. Du hast Duna beobachtet, wie sie dich beobachtet hat. Du hast Kessler gesehen — acht Episoden, Narbe an der Schläfe, einen Zettel in der Hand den niemand diktiert hat. Pham hat gelächelt, als Kessler antwortete, das Lächeln eines Mannes der die Pointe schon kennt.

Duna testet dich. Die Frage ist: was tust du mit dem Wissen, dass du getestet wirst?

---

## Aktueller Stand

`EP 1 · MS 0 · HQ · Zero Time Lounge · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · ITI-Ruf 0 · Wallet 100 CU`

**Mara Voss — SPLINTER**
STR 2 · GES 5 · INT 5 · CHA 2 · TEMP 2 · SYS 2
HP 10/10 · Talent: *Tatortanalyse* (Basis)
Carry: Dienstpistole T1 · Kevlarweste T1 · Handscanner T1 · Dietrich T0 · Comlink T1 · Rauchgranate ×2
Fahrzeug: *Grauer Wolf* (bereit)

**Offene Fäden:**
— Kesslers Papiernotiz: eigener Plan, kein Befehl
— Duna: testet Neulinge, kein Kodex-Protokoll in der ZTL
— Pham: weiß mehr als er zeigt

---

## Zero Time Lounge — Jetzt

Die Lounge hängt noch in der gleichen Stille wie beim letzten Mal. Gedämpftes Licht, das irgendwo zwischen Schichtwechsel und frühem Morgen steckt — die Nullzeit hat keinen Sonnenstand, also erfinden die Lampen hier einen. An der Bar steht noch dasselbe Glas. Duna wischt eine Stelle auf dem Tresen, die schon sauber ist.

Kessler und Pham sind weg. Ihre Plätze nicht — die Stühle stehen noch leicht vom Tisch weggerückt, als wären sie nur kurz rausgegangen.

Duna schaut kurz in deine Richtung. Nicht lange. Nur kurz genug um zu sagen: *Ich hab dich nicht vergessen.*

---

**Wo stehst du?**

1. **An der Bar bleiben** — Duna ansprechen. Direkt oder beiläufig, aber heute Nacht willst du eine Antwort.
2. **Den Stühlen nachgehen** — Kessler und Pham sind irgendwo im HQ. Finden, beobachten, oder das Gespräch suchen.
3. **Zum Operations-Deck** — Briefing holen. Erste Mission. Alles andere kann warten.
4. **Freie Aktion** — Dein Zug.

---

## [2] USER

ich geh zu duna. ich will wissen was das mit dem testen soll, direkt fragen macht mehr sinn als drumrumzureden

---

## [3] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Du gehst zur Bar. Kein Zögern, kein Umweg über ein leeres Glas oder eine vorgetäuschte Bestellung. Drei Schritte, Hocker, Unterarme auf den Tresen. Duna sieht es kommen — natürlich sieht sie es kommen, sie hat dich die ganze Zeit im Blick gehabt.

Sie legt das Tuch weg. Wartet.

„Du testest mich", sagst du. Kein Fragezeichen. „Seit ich reingekommen bin. Ich will wissen warum."

Stille. Nicht die unangenehme Art — eher die Art, in der jemand entscheidet wie viel er dir gibt.

Dann lehnt Duna sich mit beiden Händen auf den Tresen, Gewicht nach vorne, Stimme niedrig. Nicht vertraulich. Eher präzise.

„Alle neuen Gesichter kommen hier rein", sagt sie. „Irgendwann. Meistens in der ersten Woche, meistens wenn sie nicht schlafen können." Eine kurze Pause. „Ich schau, was sie anschauen. Kessler und Pham — die meisten sehen zwei Männer an einem Tisch. Du hast den Zettel gesehen. Du hast Kesslers Hände gesehen, bevor du seinen Mund gehört hast."

Sie richtet sich auf.

„Das ist keine Prüfung vom ITI. Das ist meine."

---

Keine Erklärung wozu. Keine Einladung. Sie nimmt das Tuch wieder auf — aber sie dreht dir nicht den Rücken zu.

Das Fenster ist noch offen.

---

**Probe: Einschätzung (CHA, passiv)**
`Probe: Einschätzung → W6: [5] + CHA 2/2 = 6 vs SG 5 → HIT`

Duna lügt nicht. Aber sie sagt auch nicht alles. Die Formulierung — *meine Prüfung* — sitzt zu sicher, zu oft wiederholt. Sie hat das schon jemandem erklärt. Vielleicht mehrmals. Die Frage ist nicht ob sie testet. Die Frage ist was sie mit den Ergebnissen macht.

---

1. **Nachhaken** — „Und was passiert mit dem was du siehst?"
2. **Kessler direkt ansprechen** — „Was stand auf dem Zettel?"
3. **Eigene Karte spielen** — Ihr sagen dass du weißt, dass Pham die Faltkante gesehen hat. Schauen was das auslöst.
4. **Freie Aktion** — Dein Zug.

---

## [4] USER

und was machst du dann damit, was du siehst?

---

## [5] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Duna antwortet nicht sofort.

Sie stellt ein Glas unter den Tresen, holt es wieder raus — leer, sauber, unnötig. Eine Bewegung die Zeit kauft ohne beschäftigt auszusehen. Du kennst das. Verhörte machen das. Zeugen machen das. Menschen die abwägen.

Dann stellt sie das Glas hin und schaut dich an.

„Ich merk mir's."

Drei Worte. Vollständiger Satz, keine Ergänzung. Ihre Augen gehen kurz zur Tür — nicht nervös, eher automatisch, die Art Reflex die entsteht wenn man lange in Räumen arbeitet wo Gespräche Konsequenzen haben.

„Manche Gesichter kommen wieder. Manche nicht." Sie tippt einmal mit dem Finger auf den Tresen, einmal, kurz. „Die die wiederkommen — die wissen meistens warum. Und die die nicht wiederkommen—" Ein kleines Schulterzucken. „—die haben den Zettel nicht gesehen."

Sie lässt das stehen.

Keine Drohung. Keine Einladung. Eher eine Gleichung die sie dir hinlegt und wartet ob du die Variablen selbst einsetzt.

---

**Probe: Einschätzung (CHA, aktiv — du drückst)**
`Probe: Einschätzung → W6: [3] + CHA 2/2 = 4 vs SG 6 → MISS`

Du liest sie nicht vollständig. Zu wenig Kontext, zu wenig Vergleichsbasis — Duna ist kein Tatort, kein Aktenfund. Sie ist ein Mensch der sehr lange geübt hat genau so viel zu zeigen wie sie zeigen will. Was du siehst ist echt. Was du *nicht* siehst, weißt du nicht.

---

Die Lounge ist still. Irgendwo hinten läuft ein Ventilator. Das Licht summt kaum hörbar.

Duna wartet noch. Das Fenster ist kleiner geworden — aber es ist noch offen.

---

1. **Die Gleichung lösen** — „Die die wiederkommen brauchen jemanden der weiß was er sieht. Du bist das."
2. **Kessler** — „Wie lange macht er das schon — mit dem Zettel?"
3. **Abschließen und gehen** — Nicken, aufstehen, sich das merken. Manche Gespräche enden wenn sie fertig sind.
4. **Freie Aktion** — Dein Zug.

---

## [6] USER

okay die mit dem zettel... wie lange macht kessler das schon?

---

## [7] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Duna zieht die Luft durch die Nase. Nicht genervt — eher so wie jemand der gerade entscheidet ob eine Frage die Grenze überschreitet oder knapp darunter bleibt.

Knapp darunter, anscheinend.

„Seit Episode vier", sagt sie. Ruhig, sachlich, als würde sie die Lieferzeit einer Bestellung nennen. „Vorher hat er's im Kopf gemacht. Irgendwann hat er angefangen es aufzuschreiben." Eine kurze Pause. „Ich hab ihn nicht gefragt warum. Er hat's mir nicht erklärt."

Sie nimmt das leere Glas, stellt es einen halben Meter weiter. Keine Funktion, nur Bewegung.

„Acht Episoden ist lang", sagt sie dann. Nicht zu dir, nicht wirklich — eher in den Raum. „Die meisten kommen nicht über drei. Die die über fünf kommen—" Sie hält kurz inne. „—die fangen alle irgendwann an, Dinge aufzuschreiben."

Ihr Blick kommt zurück zu dir. Direkt, ruhig.

„Du fragst nach Kessler. Nicht nach der Mission. Nicht nach dem ITI." Ein minimales Nicken, kaum sichtbar. „Das ist interessant."

---

Kein Vorwurf. Keine Warnung. Nur die Feststellung einer Frau die Muster sammelt und gerade eines notiert hat.

---

1. **Kontern** — „Ich frage nach allem was sich nicht von selbst erklärt."
2. **Direkt** — „Wo ist er jetzt?"
3. **Zurückgeben** — „Was schreibst *du* auf?"
4. **Freie Aktion** — Dein Zug.

---

## [8] USER

okay was ist das ITI nochmal

---

## [9] ASSISTANT

# Out of Character — kurze Orientierung

**ITI = Institut für Temporale Intervention.**

Das ist deine Heimatbasis — eine Organisation die außerhalb der normalen Zeitlinie operiert, in der sogenannten **Nullzeit**. Das ITI schickt Chrononauten (also dich) in verschiedene Epochen, um Zeitlinien zu sichern, Anomalien zu untersuchen und Bedrohungen zu neutralisieren bevor sie Geschichte umschreiben.

**Was du als Mara Voss weißt:**
- Das ITI hat dich rekrutiert — wegen eines Vorfalls den sie lieber aus den Akten getilgt hätten
- Das HQ ist deine sichere Basis: Briefingräume, Medlab, Quartiere, Hangar, die Zero Time Lounge
- Chrononauten springen in Epochen (deine ist 1987 Berlin), arbeiten undercover und kommen zurück
- **Kodex** ist die interne KI — Archiv, Taktikassistenz, Statusmeldungen
- Das ITI hat Regeln. Nicht alle werden dir erklärt.

**Was Mara Voss *noch nicht* weiß:**
- Warum manche Chrononauten anfangen Dinge aufzuschreiben
- Was Duna mit ihren Beobachtungen macht
- Was auf Kesslers Zettel steht

---

Zurück ins Spiel? Die Szene läuft noch — Duna wartet auf deine Antwort.

---

## [10] USER

okay kurz check - duna ist die die mich vorhin angesprochen hat oder?

---

## [11] ASSISTANT

# Out of Character — kurze Klarstellung

**Ja, genau.** Duna ist die Frau hinter der Bar in der Zero Time Lounge — sie hat dich beim Reinkommen beobachtet und den ersten Kontakt gemacht.

Aus deinen Notizen (dem letzten Save):
- Sie ist **ZTL-Thekenpersonal** — aber offensichtlich mehr als das
- Sie hat dich **aktiv getestet**: geschaut was du siehst, wie du Kessler und Pham liest
- **Kein Kodex-Protokoll in der ZTL** — was in der Lounge gesagt wird, bleibt in der Lounge

Kurz gesagt: Die Frau hinter dem Tresen, die das Glas wischt das schon sauber ist. Die dich beobachtet hat bevor du sie beobachtet hast.

---

Bereit weiterzumachen?

---

## [12] USER

ja okay alles klar, weiter!

---

## [13] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Duna wartet noch. Die Frage hängt zwischen euch — *was schreibst du auf* — aber du hast sie noch nicht gestellt. Das Fenster ist offen.

Du lehnst dich einen Tick vor.

„Ich frage nach allem was sich nicht von selbst erklärt."

Duna hört zu. Keine Reaktion im Gesicht, aber ihre Hände hören auf sich zu bewegen. Das ist Reaktion genug.

„Kessler", sagst du. „Wo ist er jetzt?"

Eine Sekunde. Zwei.

„Hangar-Axis", sagt sie. Keine Zögerung diesmal — die Entscheidung war schon vorher gefallen, du hast nur den richtigen Satz geliefert. „Er geht da hin wenn er nicht schlafen kann. Sitzt am Grauer Wolf und denkt nach. Manchmal schreibt er."

Sie nimmt das Tuch wieder auf. Gespräch fast vorbei, das spürst du.

Aber dann, ohne dich anzuschauen, fast beiläufig:

„Er weiß dass du gefragt hast. Nicht jetzt — aber er wird's wissen." Eine kleine Pause. „Kessler merkt sich auch Dinge."

---

Das ist alles was sie dir gibt. Mehr kommt heute nicht.

---

1. **Zur Hangar-Axis** — Kessler suchen. Jetzt, solange er dort ist.
2. **Noch eine Frage** — „Warum sagst du mir das?"
3. **Gehen, schlafen, abwarten** — Das hier sacken lassen. Morgen ist auch noch ein Tag.
4. **Freie Aktion** — Dein Zug.

---

## [14] USER

okay das war eine warnung oder

ich geh zur hangar-axis

---

## [15] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Ja. Das war eine Warnung.

Nicht die Art die dich aufhalten soll — die Art die dir einen fairen Start gibt. Duna hat dir gerade gesagt: *Kessler ist kein blinder Fleck. Geh rein mit offenen Augen.*

Du nimmst die Jacke vom Hocker und gehst.

---

Der Korridor zur Hangar-Axis ist länger als er aussieht. Nullzeit-Architektur — alles wirkt kompakter als es ist, bis man läuft. Gedämpfte Beleuchtung, Bodenplatten die leicht vibrieren wenn irgendwo ein Gate kalibriert wird. Du hörst es bevor du es siehst: das leise metallische Klingen von jemandem der an einem Fahrzeug arbeitet, oder so tut als ob.

Die Hangar-Axis öffnet sich groß und kühl. Sechs, sieben Fahrzeuge in verschiedenen Epochen-Konfigurationen — ein Jeep, etwas das aussieht wie ein umgebauter Trabant, weiter hinten Silhouetten die du nicht sofort einordnen kannst. Dein *Grauer Wolf* steht in Bucht drei, plane drüber, unberührt.

Kessler sitzt auf einer Werkzeugkiste neben Bucht fünf. Kein Fahrzeug dahinter — leere Bucht, als wäre das Ding dort nicht mehr zurückgekommen. Er hat einen Becher in der Hand, dampfend, und schaut auf nichts Bestimmtes.

Den Zettel siehst du nicht. Aber seine Jackentasche wölbt sich leicht.

Er hört dich kommen. Dreht sich nicht um.

„Voss", sagt er. Ruhig. Nicht überrascht.

---

**Probe: Einschätzung (INT — Tatortanalyse)**
`Probe: Einschätzung → W6: [4] + INT 5/2 + Talent 2 = 8 vs SG 6 → HIT`

Leere Bucht. Kein Schild, kein Absperrband — aber der Boden ist sauberer als die anderen Buchten. Zu sauber. Als wäre dort regelmäßig jemand und würde regelmäßig aufräumen. Oder als wäre dort etwas gewesen das man nicht mehr sehen soll.

Kessler wusste deinen Namen bevor du dich vorgestellt hast.

---

Er dreht sich jetzt um. Narbe an der Schläfe, genau wie Duna beschrieben hat. Müde Augen, aber wach dahinter — die Art Müdigkeit die nicht vom Schlafmangel kommt.

„Setz dich", sagt er. Kein Befehl. Eher eine Einladung von jemandem der nicht viele ausspricht.

---

1. **Setzen und warten** — Seinen Rhythmus übernehmen. Er hat angefangen, er soll weitermachen.
2. **Direkt** — „Was stand auf dem Zettel?"
3. **Die Bucht** — „Wessen Fahrzeug war da drin?"
4. **Freie Aktion** — Dein Zug.

---

## [16] USER

ich setz mich. und schau kurz zur leeren bucht, dann wieder zu ihm.

---

## [17] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Du setzt dich. Nicht auf die Werkzeugkiste — ein Stück daneben, auf eine Palette die stabil genug aussieht. Dein Blick geht zur leeren Bucht, kurz, bewusst. Dann zurück zu Kessler.

Er hat es gesehen. Natürlich hat er es gesehen.

Er trinkt einen Schluck aus dem Becher. Schaut selbst kurz zur Bucht, als wäre es das erste Mal — aber das ist es nicht, das siehst du an der Art wie seine Schultern sich dabei verhalten. Keine Anspannung. Eingeübte Ruhe.

„Hieß Ortega", sagt er. Ohne dass du gefragt hast. „Episode drei. Gute Agentin." Er hält kurz inne. „Nicht zurückgekommen."

Keine weitere Erklärung. Kein Bedauern in der Stimme — nicht weil er keins hätte, sondern weil es irgendwo hingegangen ist wo man nicht mehr rankommt. Du kennst diesen Ton. Kollegen die man in Akten findet statt in Fluren.

Er dreht den Becher in den Händen.

„Duna hat dich geschickt."

Kein Fragezeichen.

„Oder du bist selbst auf die Idee gekommen." Er schaut dich an. „Beides wäre interessant. Aus unterschiedlichen Gründen."

---

Die Hangar-Axis ist still bis auf das ferne Vibrieren der Gate-Kalibrierung. Irgendwo tropft etwas. Kessler wartet — nicht ungeduldig, eher wie jemand der gelernt hat dass die besten Antworten kommen wenn man ihnen Raum lässt.

---

1. **Ehrlich** — „Beides. Sie hat mir gesagt wo du bist. Den Rest hab ich selbst entschieden."
2. **Gegenfrage** — „Warum wäre das aus unterschiedlichen Gründen interessant?"
3. **Ortega** — „Was ist ihr passiert?"
4. **Freie Aktion** — Dein Zug.

---

## [18] USER

Beides. Duna hat mich geschickt, aber ich wollte selbst herkommen. Wegen ihr da drüben.

---

## [19] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Kessler nickt. Einmal, langsam. Als wäre das die richtige Antwort gewesen — nicht die beste, nicht die schlauste, aber die richtige.

„Beides", wiederholt er leise. Nicht spöttisch. Eher wie jemand der einen Befund bestätigt.

Er schaut zur leeren Bucht. Diesmal länger.

„Ortega hat immer gesagt, leere Buchten sind ehrlicher als volle." Ein kurzes, trockenes Ausatmen — kein Lachen, aber nah dran. „Volle Buchten lügen. Die sagen dir: hier ist alles in Ordnung, hier ist jemand, hier wird jemand wiederkommen." Er trinkt. „Leere Buchten sagen die Wahrheit."

Er dreht sich wieder zu dir. Die Müdigkeit in seinen Augen ist jetzt anders — nicht weniger, aber fokussierter.

„Du bist wegen ihr hergekommen", sagt er. „Das heißt du hast den Boden gesehen. Zu sauber." Eine Pause. „Die meisten sehen eine leere Bucht und denken: da fehlt was. Du hast gesehen dass da jemand aufräumt."

Er greift in die Jackentasche. Langsam, keine Eile — aber du siehst wie seine Finger kurz zögern bevor sie wieder rauskommen. Leer.

Nicht heute. Noch nicht.

„Wie lange bist du schon hier, Voss?"

---

1. **Ehrlich** — „Paar Tage. Erste Episode noch nicht mal angefangen."
2. **Gegenfrage** — „Warum räumst du sie auf? Die Bucht."
3. **Direkt** — „Was steht auf dem Zettel, Kessler."
4. **Freie Aktion** — Dein Zug.

---

## [20] USER

3

---

## [21] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Stille.

Nicht die abwägende Art wie bei Duna. Eher die Art die entsteht wenn jemand eine Frage gehört hat die er nicht erwartet hat — oder die er genau erwartet hat und trotzdem nicht weiß wie er sie beantworten soll.

Kessler stellt den Becher auf den Boden. Beide Hände frei jetzt.

Er greift in die Jackentasche. Diesmal zögern die Finger nicht.

Der Zettel ist klein. Gefaltetes Papier, zweimal gefaltet, Ränder leicht abgegriffen — der wird oft rausgeholt und wieder reingesteckt. Er hält ihn zwischen zwei Fingern, schaut ihn an, schaut dich an.

Gibt ihn dir nicht.

„Namen", sagt er. „Daten. Buchten." Er tippt einmal auf den Zettel. „Jede Episode eine neue Zeile. Wer nicht zurückgekommen ist. Wann. Wo ungefähr."

Eine Pause.

„Das ITI führt Akten." Seine Stimme ist gleichmäßig, sachlich, aber darunter liegt etwas — keine Wut, eher eine sehr alte, sehr ruhige Überzeugung. „Ich auch. Andere Akten."

Er faltet den Zettel wieder zu. Steckt ihn ein.

„Ortega steht drauf. Drei andere auch." Er schaut zur leeren Bucht. „Und eine Frage die ich noch nicht beantworten kann."

---

Er schaut dich an. Direkt, ruhig.

Wartet.

---

1. **„Welche Frage?"**
2. **„Warum zeigst du mir das?"**
3. **„Was unterscheidet deine Akten von denen des ITI?"**
4. **Freie Aktion** — Dein Zug.

---

## [22] USER

welche frage

---

## [23] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Kessler atmet aus. Nicht tief — kurz, kontrolliert, die Art Ausatmen die man macht wenn man eine Entscheidung trifft die man nicht mehr zurücknehmen kann.

„Ob es Zufall ist."

Er lässt das stehen. Drei Sekunden, vier.

„Vier Agenten. Verschiedene Epochen, verschiedene Missionen, verschiedene Teams." Er spricht langsam, nicht weil er nach Worten sucht — weil er will dass jedes landet. „Kein gemeinsamer Auftrag. Kein gemeinsamer Feind soweit ich sehen kann. Aber alle vier—" Er hält kurz inne. „—alle vier hatten dieselbe Art von letztem Bericht. Unvollständig. Abgebrochen. Als wäre mitten im Satz Schluss gewesen."

Er schaut auf seine Hände.

„Das ITI sagt: Einsatzverluste. Passiert." Ein minimales Schulterzucken. „Passiert. Stimmt. Aber abgebrochene Berichte passieren wenn jemand keine Zeit mehr hat. Oder wenn jemand nicht will dass der Bericht ankommt."

Sein Blick kommt zurück zu dir.

„Vier Mal Zufall ist Muster. Ich hab nur noch keine Linie durch die Punkte."

---

Die Gate-Kalibrierung vibriert irgendwo tief im Boden. Die leere Bucht steht offen wie eine Frage die keiner gestellt hat.

Kessler wartet nicht mehr — er hat dir gegeben was er hat. Der Rest liegt bei dir.

---

**Probe: Einschätzung (INT — Tatortanalyse)**
`Probe: Einschätzung → W6: [6] + [3] + INT 5/2 + Talent 2 = 13 vs SG 7 → KRITISCHER HIT`

Vier abgebrochene Berichte. Verschiedene Epochen — aber Berichte laufen alle über denselben Knotenpunkt. Kodex-Archiv. Jemand der Berichte verschwinden lassen will braucht keinen Zugang zu den Epochen. Nur zum Archiv.

Und Kessler schreibt auf Papier.

Das ist kein Zufall.

---

`Kodex: Analysemuster erkannt. Keine Anfrage gestellt — lokale Auswertung.`

---

1. **„Du schreibst auf Papier weil du dem Kodex-Archiv nicht traust."**
2. **„Gib mir die Namen."**
3. **„Ich bin seit drei Tagen hier. Warum erzählst du mir das?"**
4. **Freie Aktion** — Dein Zug.

---

## [24] USER

du schreibst auf Papier weil du dem Archiv nicht traust oder

---

## [25] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Kessler bewegt sich nicht.

Keine Überraschung. Keine Bestätigung. Nur diese sehr ruhige, sehr wache Stille die du jetzt zum dritten Mal bei ihm siehst — die Stille eines Mannes der gelernt hat seine Reaktionen klein zu halten.

Dann, nach einer langen Sekunde:

„Du bist seit drei Tagen hier."

Kein Vorwurf. Eher — Staunen. Das gedämpfte, vorsichtige Staunen von jemandem dem gerade jemand anderes seinen eigenen Gedanken zurückgegeben hat.

Er greift nicht nach dem Zettel. Er lehnt sich nur minimal zurück, Gewicht auf die Hände hinter sich, und schaut dich an als würde er etwas neu einordnen.

„Papier verschwindet nicht", sagt er schließlich. Leise. „Papier wird nicht aktualisiert. Papier erinnert sich genau so wie du es hingeschrieben hast." Eine Pause. „Digitale Archive — die erinnern sich so wie jemand will dass sie sich erinnern."

Er schaut zur leeren Bucht.

„Ortegas letzter Bericht war vollständig. Ich hab ihn gelesen bevor er—" Er stoppt. Kurz. „Zwei Tage später war er unvollständig. Drei Sätze fehlten. Die drei Sätze die eine Frage gestellt haben."

Er dreht sich wieder zu dir. Die Müdigkeit ist weg — nicht die Erschöpfung, aber der Schleier darüber.

„Also ja", sagt er. „Papier."

---

Stille. Die ehrliche Art.

Du sitzt in einer Hangar-Axis in der Nullzeit, drei Tage im ITI, und ein Mann mit acht Episoden auf dem Buckel hat dir gerade erzählt dass das Archiv lügt.

Und du glaubst ihm.

---

1. **„Welche drei Sätze?"**
2. **„Wer hat Zugriff auf das Archiv?"**
3. **„Was willst du von mir?"**
4. **Freie Aktion** — Dein Zug.

---

## [26] USER

welche drei sätze

---

## [27] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Kessler schaut dich lange an.

Nicht abwägend diesmal. Eher — prüfend. Die letzte Prüfung, die du nicht siehst aber spürst.

Dann greift er in die Jackentasche. Nicht nach dem Zettel — tiefer, Innenfutter, ein zweites gefaltetes Stück Papier das kleiner ist als das erste. Älter. Die Faltkanten sind weiß, fast durchgedrückt.

Er faltet es auf. Hält es sich selbst hin, liest nicht — er kennt es auswendig.

„Ortegas Worte", sagt er. „Nicht meine."

Er gibt es dir.

---

Handschrift. Kesslers — du erkennst den Druck, dieselbe Hand wie auf dem anderen Zettel. Abgeschrieben, nicht das Original. Drei Sätze, sauber, ohne Kommentar:

*Zielkontakt bestätigt. Übergabe läuft nicht über Standardkanal — Empfänger ist intern.*
*Wiederhole: intern. Anforderung Identitätsverifizierung an Archiv gesendet.*
*Warte auf—*

Und dann nichts. Mitten im Satz.

---

Du hältst das Papier. Das Vibrieren der Gate-Kalibrierung läuft durch den Boden, durch die Palette, durch deine Hände.

*Intern.* Jemand im ITI hat etwas empfangen das nicht über Standardkanäle laufen sollte. Ortega hat das gesehen. Ortega hat eine Anfrage ans Archiv geschickt. Drei Tage später waren diese drei Sätze weg.

Und Ortega auch.

---

`Kodex: Archiv-Anfrage Identitätsverifizierung — kein Logeintrag für diesen Zeitraum gefunden.`

---

Kessler beobachtet dein Gesicht.

„Das Archiv sagt", sagt er ruhig, „dass Ortega diese Anfrage nie gestellt hat."

---

1. **„Wer ist der Empfänger?"**
2. **„Warum gibst du mir das?"**
3. **„Ich brauche Zugang zum Archiv. Das Original finden."**
4. **Freie Aktion** — Dein Zug.

---

## [28] USER

wer ist der empfänger

---

## [29] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Kessler nimmt das Papier zurück. Faltet es. Steckt es ein.

„Weiß ich nicht."

Keine Entschuldigung dabei. Keine Frustration. Nur die nüchterne Aussage eines Mannes der gelernt hat mit Lücken zu leben.

„Ortega hat die Anfrage geschickt und auf die Antwort gewartet." Er tippt auf seine Jackentasche. „Die Antwort ist nie angekommen. Oder sie ist angekommen und wurde mit ihr zusammen — entfernt."

Er hebt den Becher auf, merkt dass er leer ist, stellt ihn wieder hin.

„Ich hab vier Episoden damit verbracht herauszufinden wer im ITI Zugang hat um Archiveinträge zu ändern. Nicht zu lesen — zu *ändern*." Er betont das Wort nicht laut, nur schwer. „Das ist keine lange Liste. Technisch gesehen."

Er schaut dich an.

„Aber eine Liste ist kein Beweis. Und ohne Beweis—" Ein kurzes, trockenes Ausatmen. „—bin ich ein alter Agent der Papierzettel sammelt und in leeren Hangarbuchten sitzt."

Pause.

„Ortega hat den Empfänger gesehen. Hat ihn erkannt genug um zu sagen *intern*." Seine Stimme bleibt gleichmäßig aber etwas darunter zieht sich fest. „Das war ihr letzter Satz."

---

Die Stille danach ist anders als die vorherigen. Schwerer.

Du hast jetzt drei Dinge die du heute Nacht nicht hattest: einen toten Namen, drei abgebrochene Sätze, und das Gefühl dass das ITI-Archiv dir anlügt bevor du auch nur eine einzige Mission gemacht hast.

Kessler wartet. Nicht auf eine Antwort — auf eine Entscheidung.

---

1. **„Zeig mir die anderen Namen auf dem Zettel."**
2. **„Ich will ins Archiv. Heute Nacht. Bevor meine erste Mission mich ins System bringt."**
3. **„Warum ich, Kessler. Drei Tage hier — warum jetzt."**
4. **Freie Aktion** — Dein Zug.

---

## [30] USER

warum ich. ernsthaft. ich bin seit drei tagen hier.

---

## [31] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Kessler schaut dich an. Lange.

Dann macht er etwas das du nicht erwartet hast — er lacht. Kurz, leise, fast unhörbar. Nicht spöttisch. Eher das Lachen von jemandem dem gerade eine Spannung aus den Schultern fällt.

„Genau deshalb."

Er lehnt sich vor, Ellbogen auf die Knie, Stimme noch ruhiger als vorher.

„Wer länger hier ist — der ist im System. Der hat Missionen, Berichte, Kontakte, Muster." Er zählt nicht an den Fingern ab, redet einfach. „Wer länger hier ist den kann man lesen. Den hat jemand schon eingeschätzt. Der hat schon Seiten auf die jemand schreiben konnte."

Er schaut kurz zur leeren Bucht.

„Ortega war fünf Episoden hier als sie das gesehen hat. Fünf Episoden bedeutet du bist berechenbar. Du hast Gewohnheiten. Du hast Leute denen du vertraust und Leute die dir vertrauen." Eine Pause. „Das macht dich nützlich. Und es macht dich angreifbar."

Zurück zu dir.

„Du bist seit drei Tagen hier. Du hast noch keine Missionsakte. Noch keine Kontakte die jemand gegen dich verwenden kann. Noch keine Muster die jemand lesen kann." Er tippt einmal auf den Boden zwischen euch. „Du bist noch nicht im System. Nicht richtig."

Er lehnt sich zurück.

„Und du hast den Zettel gesehen. Ortegas Bucht gesehen. Bist hergekommen ohne dass ich dich gebeten hab." Eine kurze Pause, die letzte. „Duna schickt mir nicht jeden."

---

Stille.

Draußen vibriert die Gate-Kalibrierung. Irgendwo in der Nullzeit dreht sich etwas das keine Uhr hat.

Du bist seit drei Tagen hier und sitzt bereits tiefer drin als die meisten nach drei Episoden.

---

1. **„Was willst du dass ich tue?"**
2. **„Ich will erst meine erste Mission. Dann reden wir weiter."**
3. **„Ich brauche die Namen. Alle vier."**
4. **Freie Aktion** — Dein Zug.

---

## [32] USER

okay das klingt alles irgendwie schmeichelhaft aber auch ein bisschen unheimlich

was willst du dass ich tue

---

## [33] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Kessler nickt. Als hätte er die Reaktion erwartet — das Unheimliche, das Zögern. Als wäre das ebenfalls ein Befund den er notiert.

„Noch nichts", sagt er.

Du wartest auf mehr. Es kommt nicht sofort.

„Deine erste Mission läuft durch das Standardbriefing. Renier oder jemand von seinem Stab erklärt dir den Auftrag, du springst, du kommst zurück." Er spricht sachlich, kein Gewicht auf den Worten. „Wenn du zurückkommst — schreib deinen Bericht. Vollständig. Alles. Auch was sich unwichtig anfühlt."

Eine Pause.

„Dann schreib ihn nochmal. Auf Papier. Wort für Wort. Und behalte ihn."

Er schaut dich an.

„Nicht weil ich denke dass deiner verschwinden wird. Du bist neu, du bist uninteressant, noch." Das *noch* sitzt ruhig aber deutlich. „Sondern weil du dann weißt wie sich ein vollständiger Bericht anfühlt. Und weil du dann merkst — wenn irgendwann etwas fehlt."

Er steht auf. Gespräch fast vorbei, das spürst du diesmal früher.

„Das ist alles. Erst mal."

Er hebt den leeren Becher auf, dreht ihn in den Händen.

„Und Voss—" Er schaut dich direkt an, einmal, kurz. „—frag das ITI nicht nach Ortega. Nicht jetzt. Nicht über Kodex. Nicht über irgendeinen Kanal den du nicht selbst kontrollierst."

---

Er geht. Nicht eilig. Die Schritte eines Mannes der weiß wohin er läuft.

Du sitzt allein in der Hangar-Axis. Leere Bucht vor dir. Dein *Grauer Wolf* in Bucht drei, plane drüber, unberührt.

In deiner Hand — nichts. Aber im Kopf: vier Namen auf einem Zettel, drei abgebrochene Sätze, und eine sehr ruhige, sehr alte Überzeugung dass das Archiv lügt.

---

`Kodex: Keine offenen Anfragen. Standby.`

---

**Erster Schritt — du entscheidest:**

1. **Schlafen gehen** — Morgen ist Briefing. Frisch anfangen, Augen offen, Papier kaufen.
2. **Jetzt ins Kodex-Archiv** — Nicht nach Ortega fragen. Nur schauen wie das System aussieht. Bevor du drin bist.
3. **Zurück zu Duna** — Sie weiß dass du warst. Sie wartet vielleicht.
4. **Freie Aktion** — Dein Zug.

---

## [34] USER

okay warum soll ich nicht nach ortega fragen

das ist jetzt das einzige woran ich denken kann

---

## [35] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Gute Frage.

Kessler hat es nicht erklärt. Das war kein Versehen.

Du sitzt in der leeren Hangar-Axis und gehst es durch — so wie du einen Tatort durchgehst, von außen nach innen.

**Was du weißt:**
Ortega hat eine Identitätsverifizierung ans Archiv geschickt. Jemand hat diese Anfrage aus dem Archiv entfernt. Jemand der Zugang hat um Einträge zu *ändern*, nicht nur zu lesen. Drei Tage später war Ortega weg.

**Was das bedeutet:**
Wenn du jetzt nach Ortega fragst — über Kodex, über ein Terminal, über irgendeinen Kanal der durch das Archiv läuft — dann ist das eine Anfrage. Eine Anfrage die irgendwo landet. Die irgendwer sieht.

Jemand im ITI hat bereits einmal bemerkt dass jemand nach dem richtigen Ding gefragt hat.

Und dieser jemand hat gehandelt.

Du bist seit drei Tagen hier. Du hast noch keine Missionsakte. Du bist noch nicht im System — nicht richtig. Das ist dein einziger Vorteil und er ist dünn wie Zigarettenpapier.

Eine Anfrage nach Ortega würde das ändern.

---

Du sitzt in der Stille und merkst dass Kessler dir das nicht erklärt hat weil er dachte du kommst selbst drauf.

Und du bist draufgekommen.

---

1. **Schlafen gehen** — Morgen Briefing. Augen offen. Papier kaufen.
2. **Ins Archiv** — Nicht nach Ortega. Nur schauen wie das System aussieht. Struktur, Zugänge, Logik.
3. **Zurück zu Duna** — Sie weiß dass du bei Kessler warst. Vielleicht weiß sie mehr.
4. **Freie Aktion** — Dein Zug.

---

## [36] USER

okay krass. jemand sitzt also da drin und passt auf.

ich geh zu Duna.

---

## [37] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Vielleicht. Vielleicht auch automatisch — ein Filter, ein Muster-Algorithmus, ein Tripwire der anschlägt wenn bestimmte Namen auftauchen. Muss kein Mensch sein der aktiv schaut. Muss nur etwas sein das meldet.

Das ist fast schlimmer.

Du stehst auf und gehst.

---

Der Korridor zurück zur ZTL ist derselbe wie vorhin — gedämpftes Licht, Bodenvibrieren, Nullzeit-Stille. Aber du läufst ihn anders. Augen anders. Du zählst Kameras ohne es zu merken, bemerkst Winkel, bemerkst wo das Licht Schatten lässt.

Alte Gewohnheit. Berlin, 1987. Manche Dinge verlernt man nicht.

---

Die Zero Time Lounge ist leerer als vorher. Zwei Gesichter an einem Tisch hinten, über Karten gebeugt, reden nicht. Duna steht noch hinter dem Tresen — oder wieder, schwer zu sagen ob sie je gegangen ist.

Sie sieht dich reinkommen. Sagt nichts.

Du gehst zur Bar. Setzt dich. Dieselbe Stelle wie vorhin.

Duna stellt ohne Frage ein Glas vor dich hin. Wasser, kein Eis. Schaut dich an.

„Und?"

Ein Wort. Aber du hörst die ganze Frage dahinter — *was hat er dir gegeben, was machst du jetzt damit, bist du noch dieselbe Person die vor einer Stunde reingekommen ist.*

---

**Probe: Einschätzung (INT — Tatortanalyse)**
`Probe: Einschätzung → W6: [5] + INT 5/2 + Talent 2 = 9 vs SG 6 → HIT`

Duna weiß bereits dass du bei Kessler warst. Nicht weil sie Kameras überwacht — weil sie Kessler kennt. Sie weiß wie lange solche Gespräche dauern. Sie hat die Zeit gezählt.

Die Frage *und* ist keine Frage nach dem Inhalt. Sie ist eine Frage nach dir.

---

1. **„Jemand passt auf. Im Archiv."** — Direkt. Schauen was sie damit macht.
2. **„Er hat mir gesagt ich soll Papier kaufen."** — Indirekt. Schauen ob sie lacht oder nickt.
3. **„Warum schickst du Leute zu ihm?"** — Die eigentliche Frage die du noch nicht gestellt hast.
4. **Freie Aktion** — Dein Zug.

---

## [38] USER

ich trink erst mal einen schluck

dann: warum schickst du leute zu ihm?

---

## [39] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Das Wasser ist kalt. Sauber. Die ZTL hat kein Leitungswasser aus irgendeiner Epoche — Nullzeit-Aufbereitung, schmeckt nach nichts, was manchmal das Beste ist.

Du stellst das Glas ab.

„Warum schickst du Leute zu ihm?"

Duna lehnt sich nicht vor. Lehnt sich nicht zurück. Steht einfach da, Hände flach auf dem Tresen, und schaut dich an als würde sie die Frage wiegen.

„Weil er alleine nicht weiterkommt."

Keine Pause davor, keine danach. Sitzt einfach da.

„Kessler ist gut." Sie sagt es sachlich, kein Lob, nur Befund. „Aber er denkt wie jemand der acht Episoden im System ist. Er weiß zu viel über zu viele Leute. Er sieht Muster — aber er sieht sie durch alles was er schon erlebt hat." Sie tippt einmal auf den Tresen. „Das färbt."

Sie nimmt sein Glas — Kesslers Glas, merkst du jetzt, stand die ganze Zeit am anderen Ende der Bar — und stellt es unter den Tresen.

„Neue Augen sehen andere Dinge. Manchmal die richtigen Dinge." Ein kurzer Blick zu dir. „Du hast den Zettel gesehen. Ortegas Bucht. Bist hergekommen. Das macht dich nicht besonders—" Eine kleine Pause. „—aber es macht dich brauchbar."

Sie sagt es ohne Entschuldigung. Brauchbar ist kein Kompliment bei ihr, aber auch keine Beleidigung. Eher eine Kategorie.

„Und weil er es nicht selbst tun würde", sagt sie dann, leiser. „Jemanden ansprechen. Er wartet bis die Leute von selbst kommen." Sie schaut kurz zur Tür. „Manchmal kommen sie nicht."

---

Stille. Das Kartenpaar hinten redet immer noch nicht.

Du hast jetzt beide Seiten gehört — Kessler und Duna. Zwei Menschen die seit Episoden in derselben Richtung schauen ohne sich abzusprechen. Oder mit sehr wenig Absprache. Schwer zu sagen.

Was du weißt: keiner von beiden hat dir gesagt was sie wirklich wollen. Nur was sie brauchen.

Das ist nicht dasselbe.

---

1. **„Was bekommst du dafür? Du machst das nicht aus Nächstenliebe."**
2. **„Wie viele hast du schon zu ihm geschickt?"**
3. **„Ich mach morgen meine erste Mission. Danach reden wir weiter."**
4. **Freie Aktion** — Dein Zug.

---

## [40] USER

was bekommst du dafür. das klingt nicht nach nem hobby

---

## [41] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Duna schaut dich an.

Diesmal länger als sonst. Nicht abwägend — eher so als würde sie entscheiden ob die Frage eine Antwort verdient oder eine Gegenfrage.

Sie entscheidet sich für die Antwort.

„Information."

Sie sagt es ohne Umschweife, ohne Rechtfertigung.

„Kessler hat Zugang zu Dingen die ich von hier aus nicht sehe. Einsatzberichte, Muster, was in den Epochen passiert." Sie wischt eine Stelle auf dem Tresen, dieselbe Bewegung wie immer, aber diesmal hat sie etwas Mechanisches — sie denkt während sie redet. „Ich hab Zugang zu Dingen die er nicht sieht. Wer reinkommt. Wer nicht schlafen kann. Wer wen anschaut und wie."

Sie hält kurz inne.

„Die ZTL ist kein Kodex-Protokoll. Was hier gesagt wird landet nirgendwo." Ein minimales Schulterzucken. „Das macht sie nützlich. Für alle möglichen Gespräche."

Sie stellt das Tuch weg.

„Ich bekomme Kontext. Er bekommt Augen. Die Leute die ich schicke bekommen—" Sie macht eine kleine Geste in deine Richtung. „—eine ehrlichere Einführung als das Standardbriefing."

Pause.

„Niemand wird reich davon." Ihr Blick ist direkt, ruhig. „Aber Ortega hatte niemanden der ihr gesagt hat worauf sie achten soll. Bevor sie es selbst rausgefunden hat."

Das letzte sitzt.

Nicht als Vorwurf. Als Tatsache die sie schon eine Weile mit sich trägt.

---

Das Kartenpaar hinten steht auf, geht. Jetzt seid ihr allein in der ZTL.

Du hast Wasser vor dir, eine leere Hangar-Bucht im Kopf, und zwei Menschen die seit Episoden ein informelles Netz spinnen weil sie dem offiziellen nicht trauen.

Und du bist seit drei Tagen hier.

---

1. **„Was hätte Ortega wissen müssen?"**
2. **„Ich bin dabei. Was jetzt?"**
3. **„Ich brauch eine Nacht zum Nachdenken."**
4. **Freie Aktion** — Dein Zug.

---

## [42] USER

was ist mit Ortega passiert

---

## [43] ASSISTANT

`EP 1 · MS 0 · SC —/— · PHASE Frei · MODE CORE · COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 · Px 0/5 · Stress 0/8 · Obj — · Exfil —`

---

Duna bewegt sich nicht.

Einen Moment lang — nur einen — siehst du etwas durch die ruhige Oberfläche. Nicht viel. Nur eine Spannung um den Mund, eine minimale Verhärtung hinter den Augen. Jemand der eine Frage gehört hat die er nicht gerne hört weil er sie sich selbst schon zu oft gestellt hat.

Dann ist es wieder weg.

„Offiziell", sagt sie, „ist sie in einer Einsatzzone nicht zurückgekommen. Missionsverlust. Akte geschlossen."

Sie nimmt dein Glas, füllt es nach obwohl es noch halb voll ist. Etwas zu tun haben.

„Inoffiziell—" Sie stellt die Karaffe hin. „—weiß ich es nicht. Kessler weiß es nicht. Das ist das Problem."

Eine Pause. Kurz, aber schwer.

„Sie hat ihren letzten Bericht aus einer Einsatzzone geschickt. 1962, Kuba. Mitten in der Krise." Duna spricht gleichmäßig, sachlich, die Art Sachlichkeit die man sich erarbeitet. „Danach nichts. Kein Notsignal. Kein Exfil-Versuch. Kein—" Sie stoppt kurz. „Nichts. Als wäre sie einfach aufgehört zu existieren."

Sie schaut auf ihre Hände auf dem Tresen.

„Agenten sterben. Das passiert. Aber die hinterlassen Spuren." Ihr Blick kommt zurück zu dir. „Körper. Ausrüstung. Irgendwas. Jemand der sie gesehen hat. Irgendeinen Abdruck."

Sie schüttelt minimal den Kopf.

„Bei Ortega — nichts. Sauberes Nichts."

---

Sauberes Nichts.

Du kennst das aus Berlin. Wenn jemand spurlos verschwindet gibt es zwei Möglichkeiten: entweder war jemand sehr gut. Oder jemand hatte sehr viel Zeit zum Aufräumen.

Beides ist schlimmer als ein Leichnam.

---

Duna schaut dich an. Die Frage die sie nicht stellt hängt zwischen euch — *was machst du jetzt mit allem was du heute Nacht weißt.*

---

1. **„1962, Kuba. Das ist meine erste Mission oder?"**
2. **„Wer hätte in einer Einsatzzone so sauber aufräumen können?"**
3. **„Ich brauch eine Nacht. Morgen Briefing. Danach Papier kaufen."**
4. **Freie Aktion** — Dein Zug.

---

## [44] USER

!save

---

## [45] ASSISTANT

`SaveGuard: Speichern nur im HQ-Kernbereich.`

`Kodex: Aktueller Standort: Zero Time Lounge. HQ-Kernbereich bestätigt — Save freigegeben.`

---

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-2026-01-01T07:42:00Z-HQ-ZTL-VOSS",
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
          "Zero Time Lounge: Erstkontakt Duna. Kessler (8 Episoden) und Pham (5 Episoden) beobachtet — Papiernotiz, Handschrift, kein Druck, Kessler wusste vor dem Umdrehen wer reinkam. Duna testet ob Voss sieht was sie sieht.",
          "Hangar-Axis: Kessler. Vier abgebrochene Berichte, vier verschwundene Agenten. Archiveinträge nachträglich geändert. Ortegas letzter Satz: Empfänger ist intern. Kessler schreibt auf Papier weil er dem Kodex-Archiv nicht traut.",
          "ZTL: Duna. Informationsnetz außerhalb des Kodex-Protokolls. Ortega: 1962 Kuba, sauberes Nichts — kein Körper, keine Ausrüstung, kein Abdruck. Duna und Kessler wissen nicht was passiert ist."
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
      "Kessler: Vier Agenten nicht zurückgekommen. Abgebrochene Berichte, alle nachträglich aus dem Archiv entfernt. Archivzugang zum Ändern von Einträgen = kurze Liste. Kessler schreibt auf Papier — Archiv nicht vertrauenswürdig.",
      "Ortegas letzter Bericht (abgeschrieben von Kessler): 'Zielkontakt bestätigt. Übergabe läuft nicht über Standardkanal — Empfänger ist intern. Wiederhole: intern. Anforderung Identitätsverifizierung an Archiv gesendet. Warte auf—' Kodex: kein Logeintrag für diese Anfrage.",
      "Duna: Informationsnetz ZTL — kein Kodex-Protokoll. Tauscht mit Kessler: sie liefert Personenbeobachtung, er liefert Einsatzmuster. Ortega hatte niemanden der sie gewarnt hat.",
      "Ortega: 1962, Kuba. Sauberes Nichts. Kein Körper, keine Ausrüstung, kein Abdruck. Jemand hatte Zeit zum Aufräumen — oder war sehr gut.",
      "Kesslers Anweisung: Bericht nach erster Mission vollständig schreiben. Dann nochmal auf Papier. Nicht nach Ortega fragen — über keinen Kanal den Voss nicht selbst kontrolliert."
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
    "summary_active_arcs": "EP1: Voss hat Kessler und Duna gesprochen. Vier verschwundene Agenten, manipuliertes Archiv, interner Empfänger. Ortega: 1962 Kuba, spurlos. Kessler: Papier statt Kodex. Duna: informelles Netz außerhalb Protokoll. Voss noch nicht im System — das ist der einzige Vorteil."
  },
  "continuity": {
    "last_seen": {
      "mode": "core",
      "episode": 1,
      "mission": 0,

[...gekuerzt...]

---

## [46] USER

!save

---

## [47] ASSISTANT

`Kodex: Save bereits generiert. Letzter Stand: SAVE-2026-01-01T07:42:00Z-HQ-ZTL-VOSS.`
`Kodex: Kein neuer Spielstand seit letztem Save. Duplikat-Save unterdrückt.`

---

Der aktuelle Save ist vollständig und aktuell. Nichts hat sich verändert seit dem letzten `!save` — kein neuer JSON nötig.

**Bereit weiterzumachen?**

1. **Morgen, Briefing** — Schlafen gehen, erste Mission angehen.
2. **Noch eine Frage an Duna** — Das Gespräch läuft noch.
3. **Freie Aktion** — Dein Zug.

---

## [48] USER

!save

---

