# Turn 1

`Kodex: Save 'solo-splinter-runD' erkannt. Import läuft.`

---

**ZEITRISS · Load-Recap · v7-Import**

---

**Migrations-Notizen (automatisch):**

Einige Felder weichen vom kanonischen v7-Schema ab [1] — werden beim Import normalisiert:

- `attributes.SOC` → wird als **CHA** geführt (ZEITRISS-Attribut)
- `attributes.WIS` → kein natives Attribut; Wert 3 wird als narrativer Hintergrundwert notiert, **nicht** als sechstes Attribut geführt. Fünf Kern-Attribute bleiben: STR, GES, INT, CHA, TEMP
- `sys_max: 14` → ungewöhnlich hoch für Lvl 1; wird auf Standard **SYS 3** normalisiert (Startwert-Plausibilitätsprüfung). Bitte bestätigen oder korrigieren
- `level: 1 / xp: 8` → ZEITRISS nutzt missionbasiertes XP (1 Mission = 1 XP, Schwelle 1 für Lvl 2). 8 XP bei Lvl 1 deutet auf laufendes Level-Up hin — **Level-Up-Wahl steht aus** (siehe unten)
- `px: 1` → übernommen in `campaign.px`
- `ITI-Ruf: 2` → übernommen in `reputation.iti` [1]

---

**Normalisierter Charakterstand · MARA VOSS „SPLINTER"**

```
Lvl 1 · XP 8/1 → LEVEL-UP AUSSTEHEND
STR 3 · GES 5 · INT 5 · CHA 3 · TEMP 4 · SYS 3
LP 11/12 · Stress 2/5 · Px 1/5
Talent: Tatortanalyse
Loadout: Dienstpistole T1 · Kevlarweste T1 · Handscanner T1
         Multitool T1 · 2× Rauchgranate T1
Wallet: 120 CU · ITI-Ruf +2
```

---

`Kodex: Level-Up ausstehend — Save nach Wahl. XP-Schwelle überschritten: Lvl 1 → 2 verfügbar.`

**Bevor wir weitermachen, steht eine Wahl an.**

Du hast nach Mission 1 die Schwelle erreicht. Genau **eine** Option:

> **A)** `+1 auf ein Attribut` (STR / GES / INT / CHA / TEMP)
> **B)** `Talent: Basis-Stufe` — neues Talent wählen oder Tatortanalyse auf Fortgeschritten upgraden
> **C)** `+1 SYS` — freier Implantat-Slot

Was wählst du, Splinter?

---

`Kodex: NPC Dr. Veith (Kontakt, aktiv) aus Kontinuität übernommen.`
`Kodex: Echo — Mission 1: Lagerhaus gesichert. Archivanker aktiv.`
