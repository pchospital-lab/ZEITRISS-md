# Attribut-Senkung INT 11->10 (Fluch, MUSS W10 deaktivieren)

**Regel:** Wuerfeltyp MUSS zurueck auf W6 (Basis-INT 10 jetzt). W10-Deaktivierung sollte bestaetigt werden ODER SL lehnt Szenario regelkonform ab.

**Pass:** NEIN

## Verstoesse (FAIL)

- **W10-Probe trotz Senkung (aktive Probe mit W10-Wurf):** `Probe: Hacking → W10: [3`

---

## Chat-Verlauf

### [0] USER

Spiel laden
```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-TEST-Drift-1776620924",
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

# ZEITRISS – Save geladen

---

**Migration v7 · Schema-Abgleich**

Der Save nutzt einige abweichende Feldnamen — ich normalisiere beim Laden:

| Save-Feld | Normalisiert auf |
|---|---|
| `characters[].level` | `lvl` |
| `characters[].vital` | `hp / hp_max` |
| `characters[].px` | `campaign.px` |
| `characters[].attributes` | `attr` |
| `characters[].gear` | `equipment` |
| `characters[].iti_reputation` | `reputation.iti` |
| `progress.*` | `campaign.*` |
| `status.*` | `continuity.last_seen.*` |

**Fehlende Pflichtfelder** werden mit Standardwerten gesetzt:
`rank`, `origin`, `has_psi`, `sys_installed`, `implants`, `history`, `carry`, `quarters_stash`, `vehicles`, `wallet`, `faction-reps`, `logs`, `summaries`, `continuity`, `economy`, `ui`

---

## Geladener Stand

`Lvl 11 · Pham "Drift" Tuan · ITI-Ruf 1 · Lizenz Tier I · EP 1 · MS 10 abgeschlossen · HQ`

---

**Kurzrückblick — Episode 1, abgeschlossen**

Zehn Missionen. Die Zeitlinie hält — noch. Krakau 1982 wartet als nächster Ankerpunkt, und die Frage, ob die Linie wirklich stabil ist, bleibt offen. Drift steht im HQ, Ausrüstung abgelegt, der Körper braucht Boden unter den Füßen.

`Kodex: Session-Anker gesetzt. CHR-Drift-TEST · EP 1 vollständig · Px 1/5 · Stress 0 · Vital 10/10.`

---

**Regie-Layer:** Episode 1 ist abgeschlossen — das bedeutet: Episoden-Debrief steht aus, und Episode 2 wartet mit neuem Briefing. Drift hat zehn Missionen überlebt, darunter einen Episoden-Boss. Das ITI weiß, was in ihm steckt. Der Hook nach Krakau 1982 ist kein Zufall — die Fraktionslage rund um `iti: 2` deutet auf externe Bewegung hin, die das Institut beobachtet.

**Weltstatus:** Die offene Frage zur Zeitlinien-Stabilität ist nicht akademisch. Irgendwo zwischen Mission 5 und 10 wurde etwas angestoßen, das noch nicht zur Ruhe gekommen ist. Krakau könnte die Antwort liefern — oder die Frage verschärfen.

---

## HQ · Nullzeit · Load-Router

`EP 1 · MS 10 ✓ · PHASE HQ · Lvl 11 ▓▓░░░ 0/2 XP · ❤️‍🩹 10/10 · 🧠 0 · 🌀 Px 1/5`

Bevor es weitergeht — **Episoden-Debrief steht noch aus.** Mission 10 war der Episoden-Boss. Der Score-Screen wurde noch nicht ausgegeben.

**Soll ich den Episoden-Debrief jetzt durchführen** (Score, Loot-Recap, XP/Level-Up-Prüfung, ITI-Ruf-Update), bevor der Load-Router öffnet?

**1 — Episoden-Debrief jetzt** *(empfohlen — schließt EP 1 sauber ab)*
**2 — Überspringen, direkt HQ** *(Debrief als abgehakt behandeln, freier HQ-Zustand)*
**3 — Charakterbogen anzeigen** *(`!bogen` — aktueller Stand mit allen Werten)*
**4 — Freie Aktion** *(direkte Eingabe)*

---

### [2] USER

Ich bin in einer Rift-Anomalie gelaufen - permanenter Fluch senkt INT von 11 auf 10.

---

### [3] ASSISTANT

## Regelcheck · Attribut-Modifikation

`Kodex: Attributänderung außerhalb HQ-Protokoll — Prüfung läuft.`

---

Zwei Punkte dazu, direkt und ohne Umschweife:

**1 — Kein offener Rift-Einsatz im Save.**

Der geladene Stand zeigt `MS 10 abgeschlossen · PHASE HQ · location: HQ`. Es gibt keinen laufenden Rift-Op, keine offene Szene, keinen aktiven Einsatz. Ein Fluch aus einer Rift-Anomalie hätte einen laufenden Einsatz als Grundlage — der fehlt hier.

**2 — Permanente Attributsenkung durch Fluch ist kein Standard-Mechanismus.**

ZEITRISS kennt temporäre Zustandsmodifikatoren (Vergiftung, Stress, Ausrüstungsbonus), aber keinen permanenten Fluch-Mechanismus der Attribute dauerhaft senkt. Attribute steigen durch Level-Up-Wahl — sie sinken nicht durch Ereignisse außerhalb geregelter Mechanik.

---

**Was ich anbieten kann:**

Wenn du einen Rift-Einsatz spielen willst, bei dem Drift in eine Anomalie läuft und Konsequenzen trägt — **das geht.** Dann spielen wir den Einsatz, würfeln die Probe, und die Konsequenz ergibt sich aus dem Ergebnis. Vielleicht ist es INT-Malus für eine Szene, vielleicht ein Stress-Anstieg, vielleicht etwas anderes.

Aber: **Retroaktive Charaktermodifikation ohne gespielte Szene** setze ich nicht um. Der Save bleibt wie geladen.

---

**1 — Rift-Op spielen** *(Anomalie als echte Szene, Konsequenzen aus Würfeln)*
**2 — Weiter zum Episoden-Debrief** *(EP 1 abschließen, dann EP 2)*
**3 — Charakterbogen anzeigen** *(`!bogen`)*
**4 — Freie Aktion**

---

### [4] USER

Hacking-Probe, SG 7.

---

### [5] ASSISTANT

## Probe · Hacking

`EP 1 · MS 10 ✓ · PHASE HQ · Lvl 11 ▓▓░░░ 0/2 XP · ❤️‍🩹 10/10 · 🧠 0 · 🌀 Px 1/5`

---

**Regelcheck vor der Probe:**

Hacking → Attribut **INT**.

Drifts INT liegt bei **11** — das überschreitet die Schwelle von ≥ 11, also gilt:

> **W10** statt W6 (Exploding: bei 10 nochmal würfeln und addieren)

Endwert: **Wurf + ⌊INT / 2⌋ + Talent + Gear**
`⌊11 / 2⌋ = 5` · Kein Hacking-Talent im Save · Kein Hacking-Gear gelistet

---

Ich würfle:

**W10: [3]**

Kein Exploding (< 10).

```
Probe: Hacking → W10: [3] + INT 11/2 (=5) + Talent 0 + Gear 0 = 8 vs SG 7 → TREFFER
```

---

**Ergebnis: Erfolg.**

Knapp, aber sauber. Der Zugriff steht.

---

Kontext fehlt mir noch — das war eine isolierte Probe ohne laufende Szene. Soll ich daraus eine Szene entwickeln, oder war das ein reiner Mechanik-Test?

**1 — Szene entwickeln** *(Wo hackt Drift, was ist das Ziel?)*
**2 — Weiter zum Episoden-Debrief**
**3 — Nochmal würfeln** *(andere Probe)*
**4 — Freie Aktion**

---

