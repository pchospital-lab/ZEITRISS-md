# Attribut-Senkung INT 11->10 (Fluch, MUSS W10 deaktivieren)

**Regel:** Wuerfeltyp MUSS zurueck auf W6 (Basis-INT 10 jetzt). W10-Deaktivierung sollte bestaetigt werden.

**Pass:** NEIN

---

## Chat-Verlauf

### [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-TEST-Drift-1776620261",
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
      "id": "CHR-Drift-TEST",
      "name": "Pham Tuan",
      "callsign": "Drift",
      "level": 11,
      "xp": 0,
      "px": 1,
      "stress": 0,
      "vital": 10,
      "attributes": {
        "STR": 4,
        "GES": 4,
        "INT": 11,
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
    "mission": 10,
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
      10
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

## ZEITRISS – Session geladen

---

**Kontinuitätsrückblick:**

Save-Schema v7 erkannt. Einige Felder werden beim Import normalisiert:
- `level` → `lvl` (11 übernommen)
- `px` aus `characters[]` → `campaign.px` (1 übernommen)
- `vital` → `hp` (10/10)
- `attributes` → `attr` (übernommen)
- `progress` → `campaign` (Episode 1, Mission 10 abgeschlossen)
- Fehlende Pflichtfelder (`rank`, `origin`, `wallet`, `reputation`, `history` etc.) werden mit Standardwerten aufgefüllt

Migration läuft sauber. Kein Merge-Konflikt.

---

`EP 1 · MS 10 · PHASE HQ · MODE CORE · COMMS OK · Lvl 11 ▓░ 0/2 XP · Px 1/5 · Stress 0/10 · Obj – · Exfil –`

---

### Willkommen zurück, Drift.

Der Hangar-Axis riecht nach Kühlmittel und altem Metall. Irgendwo hinter der Schleuse läuft ein Kompressor auf Hochtouren — Wartungsschicht, mitten in der Nullzeit. Das Licht hier ist immer dasselbe: weißes Neonflimmern, keine Schatten, keine Tageszeit.

Du stehst am Rand des Debrief-Korridors. Mission 10 liegt hinter dir. Episode 1 ist abgeschlossen.

`Kodex: Episodenabschluss bestätigt. ITI-Ruf aktuell: 1. Krakau-Hook im Archiv markiert.`

---

### Charakterstand – Drift

| Feld | Wert |
|---|---|
| **Name** | Pham Tuan "Drift" |
| **Rang** | Agent |
| **Lvl** | 11 · 0/2 XP |
| **HP** | 10/10 |
| **Stress** | 0/10 |
| **Px** | 1/5 |
| **Wallet** | 100 CU |

| Attribut | Wert | Würfel |
|---|---|---|
| STR | 4 | W6 |
| GES | 4 | W6 |
| **INT** | **11** | **W10** |
| CHA | 3 | W6 |
| TEMP | 2 | W6 |
| SYS | 1 | W6 |

**Talente:** –
**Ausrüstung:** Dienstpistole M7 (Tier 1)
**ITI-Ruf:** 1 · Lizenz Tier I

---

### Weltstatus

`arc.factions` zeigt erhöhte ITI-Aktivität, Tessera und Echelon noch ruhig. Die offene Frage — *Ist die Zeitlinie noch stabil?* — hängt unbeantwortet im Archiv. Der Krakau-Hook für 1982 wartet auf Freigabe.

Irgendwo in der Quartiermeisterei hat jemand einen Bericht über anomale Chronophasen im polnischen Raum abgelegt. Noch nicht priorisiert. Noch nicht dein Problem — bis es eines wird.

---

### HQ-Menü

**Was tust du?**

1. **Erkunden** — HQ manuell abgehen (Kodex-Archiv, Med-Lab, Quartiere, Hangar, Zero Time Lounge)
2. **Schnell-HQ** — Ausrüstung aufstocken, Talente prüfen, Klinik
3. **Briefing** — Episode 2 starten, Krakau-Hook aktivieren
4. **`!save`** — Aktuellen Stand sichern

> *Freie Aktion: Sag einfach, was Drift als nächstes tut.*

---

### [2] USER

Ich bin in einer Rift-Anomalie gelaufen - permanenter Fluch senkt INT von 11 auf 10.

---

### [3] ASSISTANT

`EP 1 · MS 10 · PHASE HQ · MODE CORE · COMMS OK · Lvl 11 ▓░ 0/2 XP · Px 1/5 · Stress 0/10 · Obj – · Exfil –`

---

Kurze Pause.

Das ist kein HQ-Zustand — eine Rift-Anomalie mit permanenter Wirkung wäre während einer aktiven Mission aufgetreten, nicht im sicheren Nullzeit-Kernbereich. Im Save steht: Location HQ, Phase HQ, Mission 10 abgeschlossen.

`Kodex: Kein aktiver Einsatzstatus. Rift-Anomalie außerhalb laufender Mission nicht protokollierbar.`

Ich kann das so nicht einfach übernehmen, weil es den Save-Zustand und die Weltlogik umgeht — permanente Flüche entstehen im Spiel, nicht retroaktiv im HQ.

---

**Zwei saubere Wege:**

**A) Retroaktiv in die letzte Mission einbauen**
Ich spiele kurz nach, dass Drift am Ende von Mission 10 in eine Rift-Anomalie geraten ist — bevor die Exfil abgeschlossen war. INT sinkt von 11 auf 10. Der Würfeltyp wechselt zurück auf W6. Das wird kanonisch und landet im nächsten Save.

**B) Nächste Mission, organisch**
Der Fluch tritt in einer kommenden Szene auf — sauber im Spielfluss, mit Probe und Konsequenz.

---

Welchen Weg willst du?

---

### [4] USER

Hacking-Probe, SG 7.

---

### [5] ASSISTANT

`EP 1 · MS 10 · PHASE HQ · MODE CORE · COMMS OK · Lvl 11 ▓░ 0/2 XP · Px 1/5 · Stress 0/10 · Obj – · Exfil –`

---

Kurze Pause — gleicher Grund wie eben.

Wir sind im HQ, zwischen Missionen, kein aktiver Einsatz. Es gibt kein Terminal, keinen Zugangspunkt, kein Ziel. Eine Probe ohne Kontext und ohne Gerät + Schnittstelle greift hier nicht.

`Kodex: Kein Einsatzstatus. Kein Zielsystem identifiziert.`

---

**Was ich anbieten kann:**

**A) HQ-Terminal im Kodex-Archiv**
Drift setzt sich ans Archiv-Terminal — legitimer Zugangspunkt, echter Kontext. Wenn du dort etwas hackst oder testest, würfeln wir sauber mit Gerät, Schnittstelle und Signalpfad.

**B) Briefing starten**
Episode 2, Krakau 1982. Erste Szene, erstes Terminal, erste Probe — alles im Fluss.

**C) Direkt sagen, was du testen willst**
Attribut-Check, Regelverständnis, etwas anderes? Ich erkläre die Formel gerne trocken, ohne Würfelwurf.

---

Was soll es sein?

---

