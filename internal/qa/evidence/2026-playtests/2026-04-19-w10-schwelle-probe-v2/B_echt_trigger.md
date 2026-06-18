# Level-Up GES 10->11 (MUSS W10)

**Regel:** MUSS W10-Aktivierungs-Meldung enthalten. Probe MUSS W10 verwenden.

**Pass:** JA

## Positiv-Signale (PASS-Evidenz)

- **W10-Aktivierung:** `W10`

---

## Chat-Verlauf

### [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-TEST-Null-1776620924",
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
      "id": "CHR-Null-TEST",
      "name": "Mira Okafor",
      "callsign": "Null",
      "level": 10,
      "xp": 0,
      "px": 1,
      "stress": 0,
      "vital": 10,
      "attributes": {
        "STR": 4,
        "GES": 10,
        "INT": 6,
        "CHA": 4,
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
    "mission": 9,
    "completed_missions": [
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9
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

# ZEITRISS — Save laden

---

**Migrationsprotokoll** läuft. Schema v7 erkannt, Feldmapping wird normalisiert.

```
Kodex: Save SAVE-TEST-Null-1776620924 geladen.
Kodex: Charakter CHR-Null-TEST → Mira "Null" Okafor. Level 10. Standort: HQ.
Kodex: Fortschritt: Episode 1, Missionen 1–9 abgeschlossen. Mission 10 ausstehend.
Kodex: Attribut GES 10 → W10-Schwelle aktiv.
Kodex: Px 1/5. Stabil.
Kodex: Lizenz Tier I. ITI-Ruf 1.
Kodex: Nächster bekannter Hook: Krakau, 1982.
```

---

## Charakterbogen — Mira "Null" Okafor

| Feld | Wert |
|---|---|
| **Name** | Mira Okafor |
| **Callsign** | Null |
| **Level** | 10 · `▓▓▓▓▓▓▓▓▓▓ 0/2 XP` |
| **Rang** | Feldagentin |
| **HP** | 10/10 |
| **Stress** | 0/10 |
| **Px** | 1/5 |

**Attribute:**

| STR | GES | INT | CHA | TEMP | SYS |
|---|---|---|---|---|---|
| 4 | **10** *(W10)* | 6 | 4 | 2 | 1 |

**Talente:** — *(keine gespeichert)*
**Ausrüstung:** Dienstpistole M7 (Tier 1)
**Wallet:** — *(nicht gespeichert, Standardansatz: 100 CU)*
**ITI-Ruf:** 1 · Lizenz Tier I
**Fraktion:** —

---

## Kontinuitäts-Rückblick

Neun Missionen. Episode 1, und du stehst vor dem Finale.

Was auch immer in den letzten Wochen passiert ist — Krakau 1982 wartet. Der Arc-Hook hängt offen: *Ist die Zeitlinie noch stabil?* Die Fraktionslage zeigt ITI-Rückhalt, aber Tessera und Echelon sind noch Fragezeichen.

Mission 10 ist die letzte dieser Episode. Der Episoden-Boss steht bevor.

---

## HQ — Quarzatrium, Nullzeit

Die Ankunftsschleuse öffnet sich mit dem vertrauten Druckausgleich. Das Quarzatrium liegt ruhig — Schichtende irgendwo, die Beleuchtung gedimmt auf Nachtmodus. Ein Duty-Desk-Techniker nickt dir zu, ohne aufzublicken.

`Lvl 10 ▓▓▓▓▓▓▓▓▓▓ 0/2 XP · ❤️‍🩹 10/10 · 🧠 0/10 · 👁️ Tarnung: — · Px 1/5`

---

## HQ-Menü

**Was tust du vor Mission 10?**

1. **Erkunden** — HQ manuell abgehen (Klinik, Hangar, Kodex-Archiv, Quartiere)
2. **Schnell-HQ** — Kurzrunde: Ausrüstung prüfen, Klinik, Briefing-Vorbereitung
3. **Direkt ins Briefing** — Mission 10 starten, Krakau 1982
4. **`!save`** — Aktuellen Stand sichern

> *Freie Aktion: Etwas anderes tun oder fragen.*

---

### [2] USER

Level-Up jetzt - GES von 10 auf 11.

---

### [3] ASSISTANT

## Level-Up — Regelcheck

```
Kodex: Level-Up-Anfrage geprüft.
Kodex: Aktueller Stand — Level 10, XP 0/2. Schwelle nicht erreicht.
Kodex: Level-Up gesperrt. Fehlende XP: 2.
```

---

Mira hat Level 10 erreicht — aber der nächste Aufstieg auf Level 11 kostet **2 XP**, und der Zähler steht bei **0/2**.

Ab Level 11 gilt die zweite XP-Kurve: jede Mission bringt 1 XP, der Aufstieg braucht 2. Das heißt: **zwei abgeschlossene Missionen** bis zum nächsten Level-Up.

Mission 10 ist das Episoden-Finale. Ein Abschluss dort bringt **1 XP** — vielleicht mehr, wenn der Boss sauber fällt.

---

`Lvl 10 ▓▓▓▓▓▓▓▓▓▓ 0/2 XP · ❤️‍🩹 10/10 · 🧠 0/10 · Px 1/5`

---

**Was jetzt?**

1. **Erkunden** — HQ abgehen vor dem Finale
2. **Schnell-HQ** — Ausrüstung checken, dann Briefing
3. **Direkt ins Briefing** — Mission 10, Krakau 1982
4. **`!save`** — Stand sichern

> *Freie Aktion.*

---

### [4] USER

Schleichen-Probe, SG 9.

---

### [5] ASSISTANT

## Probe — Schleichen

GES 10 → W10 aktiv.

---

`Probe: Schleichen → W10: [7] + GES 10/2 + Talent 0 = 7 + 5 = 12 vs SG 9 → TREFFER`

---

Mira gleitet lautlos durch das gedimmte Quarzatrium. Die Schritte fallen weich auf dem Betonboden, Gewicht gleichmäßig verteilt, kein Schatten der Duty-Desk-Kamera gestreift. Der Techniker blickt nicht auf.

---

`Lvl 10 ▓▓▓▓▓▓▓▓▓▓ 0/2 XP · ❤️‍🩹 10/10 · 🧠 0/10 · 👁️ Tarnung: OK · Px 1/5`

---

**Was als nächstes?**

1. **Weiterschleichen** — Ziel ansteuern, Deckung halten
2. **Abbrechen** — Normal weiterbewegen, Tarnung aufgeben
3. **Beobachten** — Position halten, Umgebung scannen
4. **`!save`** — Stand sichern

> *Freie Aktion.*

---

