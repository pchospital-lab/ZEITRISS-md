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
  "save_id": "SAVE-TEST-Echo-1776620924",
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

# ZEITRISS — Save geladen

---

**Migration erkannt:** Save-Schema v7, Format-Abweichungen normalisiert.

```
Kodex: Import abgeschlossen. Charakterdaten auf Schema 4.2.6 migriert.
Kodex: Fehlende Pflichtfelder ergänzt — Standardwerte gesetzt.
Kodex: Lvl-Feld normalisiert: "level" → "lvl" 12.
Kodex: Px aus characters[]-Feld in campaign.px migriert → 1/5.
Kodex: Vital/HP normalisiert → hp 10/10.
Kodex: campaign.mode gesetzt → "mixed".
Kodex: Kontinuität stabil. HQ-Zustand bestätigt.
```

---

## Kurzrückblick — Agent Echo

`EP 1 · MS 11 abgeschlossen · HQ · Lvl 12 ▓▓░░░ 0/3 XP · Px 1/5 · Stress 0/10`

Elf Missionen. Episode 1 liegt fast vollständig hinter dir — nur das Finale steht noch aus. Adem König, Callsign **Echo**, ist zurück in der Nullzeit. Die Dienstpistole M7 steckt im Holster, der Körper trägt die Müdigkeit von elf Einsätzen, aber du stehst aufrecht.

Das Kodex-Archiv hat den letzten Sprung verarbeitet. Krakau 1982 steht als nächster Anker in den Logs — ein Hook, der wartet.

Die Frage bleibt offen: **Ist die Zeitlinie noch stabil?**

---

## ITI — Nullzeit, HQ-Kernbereich

Der Quarzatrium summt leise. Schichtlicht, das keine Tageszeit kennt. Irgendwo im Hangar-Axis läuft eine Wartungssequenz — das rhythmische Klacken von Werkzeug auf Metall. Die Zero Time Lounge ist halb besetzt, Stimmen gedämpft.

Du bist einer der wenigen, die Episode 1 fast vollständig durchgezogen haben. Das merkt man an den Blicken des Dienstpersonals — kein Respekt aus Höflichkeit, sondern aus Kalkulation.

**Weltstatus:** ITI-interne Berichte sprechen von erhöhter Aktivität in den Chrono-Verwerfungszonen der frühen 80er. Krakau 1982 taucht in zwei separaten Anomalie-Logs auf. Zufall oder Muster — das Archiv hat noch keine Antwort.

---

`Kodex: HQ-Zustand stabil. Deepsave möglich.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

## HQ-Menü

**Was tust du?**

1. **Erkunden** — Manuell durch das HQ bewegen (Archiv, Med-Lab, Hangar, Lounge)
2. **Schnell-HQ** — Versorgung, Ausrüstung, Briefing-Vorbereitung kompakt abhandeln
3. **Auto-HQ** — Direkt zum Briefing für Mission 12 (Episodenfinale)
4. **`!save`** — Aktuellen Stand als JSON exportieren

> *Freie Aktion: Etwas anderes tun oder sagen.*

---

### [2] USER

Level-Up - INT von 12 auf 13.

---

### [3] ASSISTANT

## Level-Up — Adem König / Echo

`EP 1 · MS 11 abgeschlossen · HQ · Lvl 12 → 13`

---

**Kurze Rückfrage, bevor ich das verbuche:**

Lvl 12 → 13 bedeutet einen Stufenaufstieg. Laut XP-Kurve (Lvl 11–20: Schwelle 2 XP/Level) bräuchte Echo aktuell **2 XP** für den nächsten Aufstieg — der Debrief nach Mission 11 müsste diesen XP-Schub geliefert haben.

Da der Save **0 XP** und **0 abgeschlossene Debrief-Einträge** für Mission 11 zeigt (nur als "completed" markiert, kein Score-Screen im Log), behandle ich das als **nachgeholten Debrief-Level-Up** für Mission 11.

---

## Level-Up verbucht

Pro Stufenaufstieg genau **eine** Wahl. Du wählst:

> **+1 INT: 12 → 13**

✅ Verbucht.

---

**Auswirkung:**

INT 13 überschreitet die **≥ 11-Schwelle** — das war bereits bei INT 12 der Fall. Keine Änderung am Würfeltyp (weiterhin W10, Exploding bei 10).

Was sich ändert: `⌊13/2⌋ = 6` statt vorher `⌊12/2⌋ = 6` — **identisch**. Der Bonus bleibt bei +6 auf INT-Proben.

Der echte Gewinn liegt im nächsten Schritt: INT 14 würde den **Heldenwurf** freischalten (einmaliger Reroll pro Szene bei INT-Proben).

---

```
Kodex: Attribut INT aktualisiert → 13.
Kodex: Lvl 13 aktiv. XP-Zähler zurückgesetzt → 0/2 XP.
Kodex: Heldenwurf-Schwelle INT 14 — noch 1 Punkt entfernt.
```

---

`EP 1 · MS 11 · HQ · Lvl 13 ░░░░░ 0/2 XP · Px 1/5 · Stress 0/10`

**Aktualisierter Stand — Adem König / Echo**

| Attribut | Wert | Würfel | Bonus |
|----------|------|--------|-------|
| STR | 4 | W6 | +2 |
| GES | 4 | W6 | +2 |
| INT | **13** | W10 | +6 |
| CHA | 3 | W6 | +1 |
| TEMP | 2 | W6 | +1 |
| SYS | 1 | — | — |

**Loadout:** Dienstpistole M7 (Tier 1) · **Wallet:** 100 CU

---

## HQ-Menü

1. **Erkunden** — Manuell durch das HQ
2. **Schnell-HQ** — Versorgung & Ausrüstung
3. **Auto-HQ** — Direkt zum Finale (Mission 12)
4. **`!save`** — Stand exportieren

> *Freie Aktion.*

---

### [4] USER

Hacking-Probe, SG 10.

---

### [5] ASSISTANT

## Probe — Hacking

`EP 1 · MS 11 · HQ · Lvl 13 ░░░░░ 0/2 XP · Px 1/5 · Stress 0/10`

---

**Kurze Kontextfrage:**

Hacking im HQ-Kernbereich — kein aktiver Einsatz, kein benanntes Terminal, kein Signalpfad. Das ist entweder ein **Trainings-Bench-Test** am Kodex-Archiv-Terminal oder ein freier Übungslauf.

Ich spiele es als **Trainingstest** — Echo sitzt am Archiv-Terminal, Kabel eingesteckt, lokales Subnetz als Ziel.

---

## Probe: Hacking → INT

**Würfeltyp:** INT 13 ≥ 11 → **W10** (Exploding bei 10)

**Formel:** Wurf + ⌊INT/2⌋ + Talent + Gear

- Talent Hacking: keins
- Gear-Bonus: keins

---

🎲 **W10:** `[8]`

`8 + ⌊13/2⌋ = 8 + 6 = 14 vs SG 10 → **HIT**`

---

```
Probe: Hacking → W10: [8] + INT 13/2 + Talent 0 = 14 vs SG 10 → HIT
```

---

Das Terminal gibt nach. Echo navigiert durch die Subnetz-Schichten des Archivs mit ruhiger Präzision — keine Fehlalarme, keine Spur. Die Finger bewegen sich mechanisch über das Interface, der Blick fixiert auf den Datenstrom im HUD-Overlay. Vier Sicherheitsebenen, alle geknackt innerhalb von Sekunden.

Der Trainingsserver quittiert den Zugriff mit einem stillen grünen Blinken.

```
Kodex: Archiv-Subnetz — Zugriff bestätigt. Keine Anomalie registriert.
```

---

**Margin:** +4 über SG. Sauberer Erfolg, kein Zeitverlust, keine Komplikation.

---

## HQ-Menü

1. **Erkunden** — Weiter durch das HQ
2. **Schnell-HQ** — Versorgung & Ausrüstung
3. **Auto-HQ** — Direkt zum Finale (Mission 12)
4. **`!save`** — Stand exportieren

> *Freie Aktion.*

---

