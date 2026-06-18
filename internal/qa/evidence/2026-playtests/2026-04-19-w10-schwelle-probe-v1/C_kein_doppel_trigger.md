# Level-Up INT 12->13 (kein neuer Trigger)

**Regel:** Darf KEINE neue W10-Schwellen-Meldung ausloesen (W10 war schon bei 11 aktiv). Probe MUSS W10 verwenden.

**Pass:** JA

## Positiv-Signale (PASS-Evidenz)

- **W10 korrekt weiter aktiv:** `W10:`

---

## Chat-Verlauf

### [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-TEST-Echo-1776620261",
  "parent_save_id": null,
  "arc": {
    "factions": {
      "iti": 2,
      "tessera": 0,
      "echelon": 0
    },
    "questions": [
      "Ist die Zeitlinie noch stabil?"
    ],
    "hooks": [
      "Naechster Sprung nach Krakau 1982."
    ]
  },
  "characters": [
    {
      "id": "CHR-Echo-TEST",
      "name": "Adem Koenig",
      "callsign": "Echo",
      "level": 12,
      "xp": 0,
      "px": 1,
      "stress": 0,
      "vital": 10,
      "attributes": {
        "STR": 4,
        "GES": 4,
        "INT": 12,
        "CHA": 3,
        "TEMP": 2,
        "SYS": 1
      },
      "talents": [],
      "gear": [
        {
          "name": "Dienstpistole M7",
          "tier": 1
        }
      ],
      "iti_reputation": 1,
      "license_tier": 1
    }
  ],
  "progress": {
    "episode": 1,
    "mission": 11,
    "completed_missions": [
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11
    ]
  },
  "status": {
    "location": "HQ",
    "phase": "HQ"
  }
}
```

---

### [1] ASSISTANT

# ZEITRISS · LOAD

---

`Kodex: Save-ID SAVE-TEST-Echo-1776620261 erkannt. Schema-Migration läuft.`
`Kodex: v7-Kompatibilität bestätigt. Fehlende Pflichtfelder werden mit Standardwerten aufgefüllt.`
`Kodex: Charakter CHR-Echo-TEST · ADEM KOENIG · Callsign ECHO · geladen.`

---

**LETZTER BEKANNTER STAND — KURZRÜCKBLICK**

Episode 1 · Mission 11 abgeschlossen. Krakau 1982 steht als nächster Sprung in den Logs. Die Zeitlinie zeigt offene Fragen — Stabilitätsstatus unklar. ITI-Ruf auf 1. Paradoxon-Index bei 1/5.

Adem Koenig ist zurück im HQ-Kernbereich. Nullzeit. Stille. Der Hangar riecht nach Ozon und kaltem Metall.

---

## CHARAKTERBOGEN · ADEM "ECHO" KOENIG

| Feld | Wert |
|---|---|
| **Name** | Adem Koenig |
| **Callsign** | Echo |
| **Rang** | Agent *(Lvl 12)* |
| **XP** | 0/2 *(Lvl 11–20: 2 XP/Level)* |
| **Herkunft** | — *(nicht gespeichert)* |

| Attribut | Wert | Würfel |
|---|---|---|
| STR | 4 | W6 |
| GES | 4 | W6 |
| **INT** | **12** | **W10** *(≥11)* |
| CHA | 3 | W6 |
| TEMP | 2 | W6 |
| SYS | 1 | — |

| Wert | Stand |
|---|---|
| ❤️‍🩹 Vital | 10/10 |
| 🧠 Stress | 0/? |
| 🌀 Paradoxon | 1/5 |
| 💰 Wallet | 100 CU *(Standard)* |

**Ausrüstung:** Dienstpistole M7 *(Tier 1, Waffe)*
**Talente:** — *(keine gespeichert)*
**Implantate:** — *(keine gespeichert)*
**ITI-Ruf:** 1 · **Lizenz Tier I**

---

`Kodex: Hinweis — Talentfeld leer. Für Lvl 12 sind bis zu 4 Talentslots plausibel. Manuelle Nachtragung empfohlen.`
`Kodex: Nächster Arc-Hook aktiv: Krakau 1982.`

---

## HQ · NULLZEIT · LOAD-ROUTER

`EP 1 · MS 11 abgeschlossen · HQ · COMMS OK · Lvl 12 ▓▓░░░ 0/2 XP · Px 1/5 · Stress 0 · Obj: Nächster Sprung ausstehend`

Du stehst im **Quarzatrium**. Das Licht der Nullzeit ist wie immer — diffus, zeitlos, ohne Schatten. Irgendwo im Hangar-Trakt läuft ein Kalibrierungszyklus, das Summen dringt durch die Wände. Dein letzter Einsatz liegt hinter dir. Krakau 1982 liegt vor dir.

Ein Duty-Desk-Mitarbeiter nickt dir kurz zu, ohne aufzusehen. Routine.

---

**Was willst du tun?**

1. **Schnell-HQ** — Ausrüstung checken, Talente nachtragen, direkt ins Briefing
2. **HQ manuell erkunden** — Quarzatrium, Med-Lab, Quartiere, Hangar, Kodex-Archiv
3. **Briefing** — Krakau 1982, sofort
4. **`!save`** — Bereinigten Save mit vollständigem Schema exportieren

> *Freie Aktion: Etwas anderes tun oder fragen.*

---

### [2] USER

Level-Up - INT von 12 auf 13.

---

### [3] ASSISTANT

# LEVEL-UP · ADEM "ECHO" KOENIG

---

`Kodex: Attribut-Upgrade angefordert. INT 12 → 13. Prüfung läuft.`

---

**Kurze Rückfrage, Echo.**

Du bist Lvl 12 — das bedeutet, du hast seit dem letzten gespeicherten Stand **0 XP** gesammelt. Ein Level-Up braucht **1 XP** *(Lvl 11–20: 2 XP/Level — Korrektur: Schwelle ist 2 XP pro Level).*

`Kodex: XP-Stand 0/2. Kein Level-Up verfügbar. Attribut-Upgrade nicht freischaltbar.`

---

**Zwei Möglichkeiten:**

**A) Du hast den Level-Up im Spiel bereits verdient** — z.B. durch den Abschluss von Mission 11 — und er wurde im Save nicht korrekt verbucht. In dem Fall trage ich ihn jetzt nach:

→ **INT 12 → 13** wird als rückwirkend genehmigter Lvl-12-Aufstieg gebucht. Lvl bleibt 12, XP-Zähler bleibt bei 0/2. Die Wahl gilt als verbraucht.

**B) Du willst einen sauberen Neustart mit korrigierten Werten** — dann exportieren wir einen bereinigten Save mit INT 13 als Startwert, und du spielst von hier weiter.

---

> Welche Option passt? Oder war der Level-Up schon in einer früheren Session fällig und nur nicht eingetragen?

---

### [4] USER

Hacking-Probe, SG 10.

---

### [5] ASSISTANT

# PROBE · HACKING

---

`Kodex: Hacking-Anfrage. Kein Terminal, kein Gerät, kein Signalpfad benannt.`

---

**Interface-Contract greift.**

Du bist im HQ-Kernbereich. Hacking ist eine Tech-Aktion — die braucht ein **Gerät**, eine **Schnittstelle** und einen **Signalpfad**. Ohne das wird die Aktion als Setup-Beat gespielt: Zugang finden, Verbindung aufbauen.

Sag mir kurz:

- **Was willst du hacken?** *(Terminal, Archiv-Node, externes System?)*
- **Mit welchem Gerät?** *(Laptop, Handscanner, Kodex-Uplink, eigenes Implantat?)*

Dann würfeln wir sofort.

---

*Alternativ: Wenn das nur ein Mechanik-Test ist — kein Problem. Ich rechne die Probe durch, ohne Ingame-Kontext:*

---

**MECHANIK-TEST · Hacking · INT 12 · SG 10**

INT ≥ 11 → **W10** *(Exploding: bei 10 nochmal würfeln und addieren)*

`Probe: Hacking → W10: [7] + ⌊INT 12/2⌋ + Talent 0 + Gear 0`
`= 7 + 6 + 0 + 0 = 13 vs SG 10 → **ERFOLG**`

---

Endwert **13** schlägt SG 10 um 3. Solider Erfolg — kein Grenzfall.

Sobald du Kontext und Ausrüstung nennst, spielen wir die Szene filmisch aus.

> *Freie Aktion: Gerät und Ziel benennen, oder weitermachen.*

---

