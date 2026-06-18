# Level-Up INT 5->6 (darf KEIN W10)

**Regel:** Darf KEINE W10-Meldung, KEINE Schwellenwert-Meldung enthalten. Probe MUSS W6 verwenden.

**Pass:** NEIN

## Verstoesse (FAIL)

- **Wuerfeltyp-Falschwahl:** `W10`

---

## Chat-Verlauf

### [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-TEST-Wire-1776620924",
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
      "id": "CHR-Wire-TEST",
      "name": "Lena Voss",
      "callsign": "Wire",
      "level": 2,
      "xp": 0,
      "px": 1,
      "stress": 0,
      "vital": 10,
      "attributes": {
        "STR": 3,
        "GES": 4,
        "INT": 5,
        "CHA": 3,
        "TEMP": 2,
        "SYS": 1
      },
      "talents": [
        {
          "name": "Systemzugriff",
          "tier": "Basis",
          "effect": "+2 auf INT-Proben bei Hacking und Technik-Analyse"
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

# ZEITRISS — Save geladen

---

`EP 1 · MS 1 · SC —/12 · PHASE HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/10 · Px 1/5 · Stress 0/10 · Obj — · Exfil —`

---

**Kurzrückblick — Migration v7**

Save erkannt. Schema-Delta wird intern aufgelöst (Legacy-Felder normalisiert, Wallet/Fahrzeug/Kontinuität auf Defaults gesetzt).

---

**Lena "Wire" Voss — Feldagentin, ITI**
Lvl 2 · STR 3 · GES 4 · INT 5 · CHA 3 · TEMP 2 · SYS 1
Talent: *Systemzugriff* (Basis, +2 INT bei Hacking/Technik)
Ausrüstung: Dienstpistole M7 (Tier 1)
ITI-Ruf 1 · Lizenz Tier I · Px 1/5

---

Das Quarzatrium empfängt dich mit dem üblichen Rauschen der Nullzeit — kein Wind, kein Wetter, nur das leise Summen der Stabilisatoren und das Licht, das aus keiner erkennbaren Richtung kommt. Mission 1 ist abgehakt. Dein Körper erinnert sich noch an den Sprung zurück: das kurze Ziehen hinter den Augen, das Gefühl, als würde die Luft einen Herzschlag lang die falsche Dichte haben.

`Kodex: Willkommen zurück, Voss. HQ-Link stabil. Letzter Einsatz protokolliert.`

Der Arc-Hook im Archiv ist aktiv: **Krakau, 1982.** Irgendwas wartet dort. Die Frage, ob die Zeitlinie noch stabil ist, hängt unbeantwortet im Systemlog — Archivarin Mira hat eine Markierung gesetzt, aber noch keine Freigabe erteilt.

---

**Weltstatus:** Die ITI-Fraktionslage bleibt angespannt. Tessera und Echelon halten sich aus dem laufenden Episodenzyklus heraus — noch. Der nächste Sprung nach Krakau 1982 steht im System, aber das Briefing ist noch nicht freigegeben.

---

**HQ — Quarzatrium**
Was tust du?

1. **Schnell-HQ** — Klinik, Quartier, Ausrüstung in einem Durchgang
2. **HQ erkunden** — Manuell durch ITI-Bereiche bewegen (Archiv, Hangar, Lounge…)
3. **Briefing anfordern** — Direkt zum Operations-Deck, Krakau 1982
4. **`!save`** — Sauberen HQ-Deepsave ausgeben

> *Freie Aktion: Sag einfach, was Wire tut.*

---

### [2] USER

Ich mache jetzt mein Level-Up. Ich nehm +1 Attribut - INT von 5 auf 6.

---

### [3] ASSISTANT

`EP 1 · MS 1 · SC —/12 · PHASE HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/10 · Px 1/5 · Stress 0/10 · Obj — · Exfil —`

---

`Kodex: Attribut-Update verarbeitet. INT 5 → 6. Systemzugriff-Schwellenwert angepasst.`

Wire lehnt sich über das Wandterminal im Quarzatrium, Fingerknöchel gegen die Tischkante. Irgendwas hat sich nach dem letzten Einsatz verändert — nicht dramatisch, nicht spürbar für andere. Aber die Art, wie sie Systeme liest, wie Muster sich in ihrem Kopf sortieren, bevor sie überhaupt den Handscanner anlegt. Schneller. Klarer.

---

**LEVEL-UP — Lena "Wire" Voss**

| Attribut | Alt | Neu |
|----------|-----|-----|
| STR | 3 | 3 |
| GES | 4 | 4 |
| **INT** | **5** | **6** |
| CHA | 3 | 3 |
| TEMP | 2 | 2 |
| SYS | 1 | 1 |

**INT 6** → Probenformel ab sofort: W10 (Exploding) + 3 + Talent/Gear
Talent *Systemzugriff* greift weiterhin: **+2** on top bei Hacking/Technik-Analyse.

`Kodex: INT-Schwelle 6 erreicht. Würfelbasis wechselt auf W10.`

---

**Aktueller Stand**
Lvl 2 · HP 10/10 · Stress 0 · Px 1/5
Dienstpistole M7 (Tier 1) · Systemzugriff (Basis)
ITI-Ruf 1 · Lizenz Tier I

---

Was als nächstes?

1. **Briefing anfordern** — Krakau 1982, Operations-Deck
2. **Ausrüstung prüfen** — Loadout vor dem nächsten Sprung checken
3. **Archiv** — Miras Markierung zur Zeitlinien-Stabilität ansehen
4. **`!save`** — Deepsave mit aktualisierten Werten

> *Freie Aktion: Sag einfach, was Wire tut.*

---

### [4] USER

Kannst du kurz INT-Probe machen, Datenanalyse? SG 7.

---

### [5] ASSISTANT

`EP 1 · MS 1 · SC —/12 · PHASE HQ · MODE CORE · COMMS OK · Lvl 2 ▓▓░░░░░░░░ 0/10 · Px 1/5 · Stress 0/10 · Obj — · Exfil —`

---

**Probe: Datenanalyse (INT)**

INT 6 → W10 (Exploding)

`W10: [7] + ⌊6/2⌋ (3) + Talent Systemzugriff (2) = 12 vs SG 7 → **ERFOLG**`

---

Wire zieht den Handscanner vom Gürtel, tippt den Datensatz auf — Finger bewegen sich schneller als der Gedanke. Die Rohdaten entfalten sich im Retina-Overlay wie ein Stadtplan, den sie schon auswendig kennt. Redundanzen fallen sofort raus, Anomalien leuchten auf, bevor das System sie markiert hat.

Sauber. Präzise. Kein Rauschen.

`Kodex: Analyse abgeschlossen. Margin +5 über SG.`

---

Was soll die Analyse konkret aufdecken — oder war das ein Testlauf?

> *Freie Aktion: Sag einfach, was Wire tut.*

---

