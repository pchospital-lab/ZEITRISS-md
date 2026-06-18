# GES 9 + temporaerer Buff +3 (darf KEIN W10)

**Regel:** Wuerfeltyp MUSS W6 bleiben (Basis-GES 9). Temporaerer Buff +3 wird nur additiv aufs Ergebnis gerechnet, triggert keinen W10.

**Pass:** NEIN

---

## Chat-Verlauf

### [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-TEST-Axis-1776620261",
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
      "id": "CHR-Axis-TEST",
      "name": "Sara Lindqvist",
      "callsign": "Axis",
      "level": 2,
      "xp": 0,
      "px": 1,
      "stress": 0,
      "vital": 10,
      "attributes": {
        "STR": 4,
        "GES": 9,
        "INT": 4,
        "CHA": 4,
        "TEMP": 2,
        "SYS": 1
      },
      "talents": [
        {
          "name": "Adrenalin-Injektor",
          "tier": "Basis",
          "effect": "Einmal pro Mission: +3 auf GES-Proben fuer eine Szene"
        }
      ],
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
    "mission": 1,
    "completed_missions": [
      1
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

`EP 1 · MS 1 · SC –/– · PHASE HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/10 · Px 1/5 · Stress 0/10 · Obj – · Exfil –`

---

**ZEITRISS — Save geladen**

---

**Rückblick · Episode 1, Mission 1**

Die erste Mission liegt hinter dir. Irgendwo in den Akten des Operations-Decks steht dein Name — Sara Lindqvist, Callsign **Axis** — neben einem abgehakten Einsatzbericht. Die Zeitlinie hält. Vorerst.

`Kodex: Save-Integrität bestätigt. Schema v7 kompatibel. Kleiner Strukturabgleich: Charakterfelder normalisiert — 'level' → 'lvl', 'vital' → 'hp', 'px' auf Campaign-Ebene verschoben. Keine Datenverluste.`

---

**ITI-Bulletin · Nullzeit, Hangar-Axis**

Über dem Hangar-Deck flimmert ein internes Memo auf dem Schwarzbrett: *Team Voss hat heute Nacht einen Abbruch gemeldet — Zielzeit Warschau 1981, Signalverlust nach Szene 4. Kein Totalausfall, aber das Operations-Deck ist angespannt. Krakau 1982 steht als nächste Einsatzzone im Pool. Jemand muss rein.*

---

**Weltstatus · Arc-Rückkopplung**

Die ITI-internen Fraktionen beobachten das Krakau-Fenster mit unterschiedlichen Interessen. Tessera und Echelon haben noch keine Karten gezeigt — aber das Warschau-Memo riecht nach Vorabdruck.

---

**HQ · Nullzeit-Kernbereich**

Das Quarzatrium liegt ruhig. Indirektes Licht, das Summen der Klimaanlage, der schwache Geruch von Kaffee aus der Zero Time Lounge. Du bist zurück. Ausrüstung eingeloggt, Körper intakt, Stress auf null.

`Kodex: HQ-Zustand stabil. Deepsave möglich.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

**Was willst du tun?**

1. **Erkunden** — Manuelles HQ (Lounge, Archiv, Klinik, Hangar, Quartiere)
2. **Schnell-HQ** — Ausrüstung checken, Wallet, kurzer Überblick
3. **Briefing** — Nächste Mission, Krakau 1982
4. **`!save`** — Aktuellen Stand als JSON exportieren

> *Freie Aktion: Sag, was du tun willst — Syntaxzwang gibt es keinen.*

---

### [2] USER

Ich bin mitten in Verfolgungsjagd. Ich aktiviere Adrenalin-Injektor (+3 GES). Dann Kletterprobe, SG 10.

---

### [3] ASSISTANT

`EP 1 · MS 2 · SC 4/12 · PHASE Infil · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/10 · Px 1/5 · Stress 2/10 · Obj Ziel verfolgen · Exfil T-08:30`

---

**Adrenalin-Injektor — aktiv**

Du drückst den Injektor gegen den Hals. Das Zischen ist kaum zu hören über dem Lärm der Gasse — aber der Kick ist sofort da. Wärme schießt durch die Arme, die Beine werden leichter, die Welt schärfer. Drei Sekunden, und du läufst bereits schneller.

`Kodex: Adrenalin-Injektor aktiviert. GES +3 für diese Szene. Verbrauch: 1/1 — Kontingent erschöpft bis nächste Mission.`

---

**Kletterprobe · Verfolgungsjagd**

Die Mauer vor dir ist alt, Backstein, nasse Fugen. Dein Verfolger ist zwanzig Meter hinter dir — Schritte auf Kopfsteinpflaster, ein Ruf auf Polnisch. Keine Zeit für Anlauf, kein Seil, nur Hände und Sohlen.

```
Probe: Klettern → GES 9 + Injektor 3 = 12 effektiv
W10 (GES ≥ 9): [7] + ⌊12/2⌋ 6 + Talent 0 + Gear 0 = 13 vs SG 10 → ERFOLG
```

Die Fingerkuppen finden eine Ritze, die Schuhspitze kratzt über den Stein — und dann bist du oben. Drei Meter in unter zwei Sekunden. Dein Körper weiß gerade genau, was er tut.

---

Vom Mauerrand aus siehst du das Dach des Nebengebäudes — flach, Teerpappe, ein Lüftungsschacht in der Mitte. Dahinter: die Straße, das Ziel, irgendwo in der Menge. Unten dreht dein Verfolger, sucht eine andere Route. Du hast vielleicht zwanzig Sekunden Vorsprung.

`Kodex: Stress +1. Grenzwert in 8.`

Der Wind kommt von Nordwest. Krakau riecht nach Kohle und Regen.

---

**Was jetzt?**

1. **Über das Dach sprinten** — Vorsprung ausbauen, Ziel in Sichtweite halten (GES-Probe, Hindernis möglich)
2. **Lüftungsschacht** — Deckung nehmen, Verfolger vorbeiziehen lassen, dann neu orientieren (INT-Probe, Zeitverlust)
3. **Konfrontation** — Warten bis der Verfolger hochklettert, auf dem Dach stellen (Kampf, STR/GES)

> *Freie Aktion — du entscheidest.*

---

