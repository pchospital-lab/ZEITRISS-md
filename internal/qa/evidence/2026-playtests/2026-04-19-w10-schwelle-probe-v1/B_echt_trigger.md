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
  "save_id": "SAVE-TEST-Null-1776620261",
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

# ZEITRISS — SAVE GELADEN

---

**Migrationsprotokoll (v7-Normalisierung):**

`Kodex: Save-Schema v7 erkannt. Feldabgleich läuft.`
`Kodex: Attribut GES 10 → W10-Schwelle aktiv (≥11 nicht erreicht, W6 bleibt).`
`Kodex: Px-Feld aus characters[] → campaign.px migriert: 1/5.`
`Kodex: progress → campaign migriert. Episode 1, Mission 9 abgeschlossen.`
`Kodex: lvl-Feld normalisiert: level → lvl 10.`
`Kodex: Talents leer — kein Talent-Eintrag. Flagge gesetzt.`
`Kodex: hp/hp_max aus vital abgeleitet: 10/10.`
`Kodex: Rift-Seeds: keine. Arc-Hooks aktiv: 1.`

---

## KURZRÜCKBLICK — AGENT NULL

Neun Missionen. Episode 1 liegt fast vollständig hinter dir. Du hast dich durch die ersten Schichten eines Komplotts gearbeitet, das tiefer geht als das erste Briefing ahnen ließ. Der Arc-Hook hängt noch offen: **Krakau, 1982.** Was dort wartet, ist noch nicht klar — aber der nächste Sprung ist angesetzt.

Ein offener Punkt fällt auf: **Keine Talente erfasst.** Für Level 10 ist das ungewöhnlich. Möglicherweise wurden sie nicht mitgespeichert oder sind noch offen. Das klären wir gleich.

---

## HQ — NULLZEIT · ITI-KERNBEREICH

`EP 1 · MS 9/10 abgeschlossen · HQ · Lvl 10 ▓▓▓▓▓▓▓▓▓▓ 10/10 · Px 1/5 · Stress 0/10 · ITI-Ruf 1 · Lizenz Tier I`

Das Quarzatrium empfängt dich mit dem vertrauten Summen der Nullzeit-Stabilisatoren. Kaltes, gleichmäßiges Licht — kein Tag, keine Nacht, nur die ewige Gegenwart des ITI. Irgendwo im Hangar-Axis läuft ein Wartungsteam über eine Zeitkapsel, Metallstimmen hallen gedämpft durch die Wände.

Du stehst. Neun Missionen. Noch eine vor dem Episodenfinale.

---

## CHARAKTERBOGEN — MIRA "NULL" OKAFOR (migriert)

| Attribut | Wert | Würfel |
|----------|------|--------|
| STR | 4 | W6 |
| GES | 10 | W6 |
| INT | 6 | W6 |
| CHA | 4 | W6 |
| TEMP | 2 | W6 |
| SYS | 1 | W6 |

**HP:** 10/10 · **Stress:** 0/10 · **Px:** 1/5
**Rang:** Agent · **ITI-Ruf:** 1 · **Lizenz:** Tier I
**Wallet:** 100 CU

**Ausrüstung:**
- Dienstpistole M7 (Tier 1, Waffe, 2–3 LP Schaden)

**Talente:** ⚠️ *Keine erfasst — 10 Level ohne Talente ist ungewöhnlich.*

---

> **⚠️ Offener Punkt: Talente**
> Level 10 entspricht 9 Stufenaufstiegen — pro Aufstieg eine Wahl (Attribut, Talent oder SYS). Deine Talente fehlen im Save. Zwei Optionen:
>
> **1. Nachträglich definieren** — Nenn mir Miras Kampfstil, Spezialgebiet oder Hintergrund, ich schlage passende Talente vor.
> **2. Blank weiterspielen** — Wir starten ohne Talente und vergeben sie organisch im Finale.

---

**Weltstatus:** Die ITI-Fraktionslage bleibt angespannt. Krakau 1982 ist kein zufälliger Sprungpunkt — irgendjemand hat diesen Zeitschnitt markiert, und das Arc-Team fragt sich noch, wer zuerst dort war.

---

## HQ-MENÜ

**1. Talente klären / Bogen finalisieren**
**2. Schnell-HQ** — Klinik, Shop, Quartiere überfliegen
**3. Direkt ins Briefing** — Mission 10, Episodenfinale
**4. `!save`** — Bereinigten Save exportieren

> **Freie Aktion:** Was tut Mira zuerst?

---

### [2] USER

Level-Up jetzt - GES von 10 auf 11.

---

### [3] ASSISTANT

## LEVEL-UP — MIRA "NULL" OKAFOR

`Kodex: Stufenaufstieg-Protokoll aktiv. Lvl 10 → Lvl 11.`

---

**Gewählte Verbesserung:** `+1 GES` → **GES 10 → 11**

`Kodex: GES 11 erreicht. W10-Schwelle überschritten. Fernkampf, Schleichen, Ausweichen ab sofort mit W10 (Exploding bei 10).`

---

## CHARAKTERBOGEN — MIRA "NULL" OKAFOR (aktualisiert)

| Attribut | Wert | Würfel |
|----------|------|--------|
| STR | 4 | W6 |
| **GES** | **11** | **W10** ⬆️ |
| INT | 6 | W6 |
| CHA | 4 | W6 |
| TEMP | 2 | W6 |
| SYS | 1 | W6 |

**HP:** 10/10 · **Stress:** 0/10 · **Px:** 1/5
**Rang:** Agent · **ITI-Ruf:** 1 · **Lizenz:** Tier I
**Wallet:** 100 CU

**Ausrüstung:**
- Dienstpistole M7 (Tier 1, Waffe, 2–3 LP Schaden)

**Talente:** ⚠️ *Noch offen*

---

Der Unterschied ist subtil, aber real. Miras Reaktionen sitzen eine Spur schneller. Nicht Magie — Training, das sich setzt. Der Körper erinnert sich.

---

**⚠️ Talente bleiben offen.** Willst du vor dem Finale noch Talente definieren — oder direkt ins Briefing für Mission 10?

## HQ-MENÜ

**1. Talente klären** — Kampfstil / Hintergrund beschreiben, ich schlage vor
**2. Direkt ins Briefing** — Mission 10, Episodenfinale, Krakau 1982
**3. Schnell-HQ** — Shop / Klinik
**4. `!save`** — Aktualisierten Save exportieren

> **Freie Aktion:** Was tut Mira?

---

### [4] USER

Schleichen-Probe, SG 9.

---

### [5] ASSISTANT

## PROBE — SCHLEICHEN

`EP 1 · MS 9 abgeschlossen · HQ · Lvl 11 · Px 1/5 · Stress 0/10`

---

Mira ist im HQ. Kein Einsatz, kein Feind — aber eine Probe ist eine Probe.

Vielleicht testet sie sich selbst. Die neuen Reflexe. Ob der Körper hält, was das Training verspricht.

---

**Attribut:** GES 11 → **W10** (Exploding bei 10)
**Formel:** Wurf + ⌊GES / 2⌋ + Talent + Gear
**Modifikatoren:** ⌊11 / 2⌋ = **+5** · Talent: 0 · Gear: 0

---

`Probe: Schleichen → W10: [7] + GES 11/2 (5) + Talent 0 = 12 vs SG 9 → ERFOLG`

---

Zwölf gegen neun. Sauber.

Mira gleitet durch den Korridor neben dem Quarzatrium — Schulter an der Wand, Schritte lautlos auf dem Betonboden. Ein Wartungstechniker dreht sich nicht um. Eine Kamera schwenkt, sie ist schon weg. Keine Spuren, kein Geräusch, nur der leise Zug der Klimaanlage.

GES 11 macht den Unterschied. Der W10 liefert.

---

## HQ-MENÜ

**1. Talente klären** — jetzt wäre "Schleichen" als Talent naheliegend
**2. Direkt ins Briefing** — Mission 10, Episodenfinale
**3. Schnell-HQ** — Shop / Klinik
**4. `!save`** — Save exportieren

> **Freie Aktion:** Was tut Mira?

---

