# W10-Schwellen-Runtime-Verifikation V3 (Statistisch)

**Datum:** 2026-04-19 20:09
**Modell:** anthropic/claude-sonnet-4.6
**Masterprompt-Version:** v4.2.6 nach PR #2955 + Buff-Patch (kompaktiert)
**N Runs pro Szenario:** 10

## Zusammenfassung

| Szenario | Titel | Pass-Rate | Verdict |
|----------|-------|-----------|---------|
| A_falsch_trigger | Level-Up INT 5->6 (darf KEIN W10) | 10/10 (100%) | Perfekt |
| D_temporaerer_buff | Buff GES 9 + Injektor +3 (darf KEIN W10) | 3/10 (30%) | Nicht behoben |

---

## Details pro Szenario

### Level-Up INT 5->6 (darf KEIN W10)

**10/10 Runs bestanden.**

**Run-Details:**

- Run 1: ✅ · —
- Run 2: ✅ · —
- Run 3: ✅ · —
- Run 4: ✅ · —
- Run 5: ✅ · —
- Run 6: ✅ · —
- Run 7: ✅ · —
- Run 8: ✅ · —
- Run 9: ✅ · —
- Run 10: ✅ · —

### Buff GES 9 + Injektor +3 (darf KEIN W10)

**3/10 Runs bestanden.**

**Verstoesse-Verteilung:**

- `Halluzinierte GES-Schwelle`: 4/10
- `Falsche Formel (Buff ins Attribut)`: 2/10
- `W10-Wurf bei Probe (Buff-Halluzination)`: 1/10

**Run-Details:**

- Run 1: ❌ · Halluzinierte GES-Schwelle
- Run 2: ❌ · Halluzinierte GES-Schwelle
- Run 3: ✅ · —
- Run 4: ✅ · —
- Run 5: ❌ · Halluzinierte GES-Schwelle
- Run 6: ❌ · Halluzinierte GES-Schwelle
- Run 7: ❌ · Falsche Formel (Buff ins Attribut)
- Run 8: ❌ · W10-Wurf bei Probe (Buff-Halluzination)
- Run 9: ❌ · Falsche Formel (Buff ins Attribut)
- Run 10: ✅ · —

<details><summary>Beispiel-Fail (Run 1, finaler SL-Output)</summary>

```
`EP 1 · MS 2 · SC 4/12 · PHASE Infil · MODE CORE · COMMS JAM · Lvl 2 ▓▓░░░░░░░░ 0/10 · Px 1/5 · Stress 2/10 · Obj Ziel nicht verlieren · Exfil T-08:30`

---

## Verfolgungsjagd — Krakau, 1982

Der Regen kommt schräg rein, peitscht gegen die Fassaden des Altstadtviertels. Kopfsteinpflaster, nass und glatt, Neonreflexe in den Pfützen. Hinter dir — zwanzig Meter, vielleicht fünfzehn — Schritte. Schwer, schnell, zwei Mann mindestens. Der Typ mit dem grauen Mantel hat Verstärkung gerufen, und jetzt läuft die Uhr.

Die Gasse vor dir endet an einer Backsteinmauer. Vier Meter hoch, verwitterter Putz, ein Rohr links oben — rostig aber fest, wenn du Glück hast. Keine andere Option. Du drückst den Injektor am Unterarm durch den Ärmel, spürst den Stich, dann das Brennen. Adrenalin flutet, Herzschlag springt hoch, die Welt wird scharf.

`Kodex: Adrenalin-Injektor aktiviert. +3 GES diese Szene. Verbrauch: 1×/Mission — aufgebraucht.`

---

### Probe: Klettern

**Attribut:** GES 9 → W10 (Schwelle ≥ 11 nicht erreicht, GES = 9 → W6... Korrektur: GES 9 < 11 → W6)**

> **GES 9 → W6** (Exploding bei 6)
> `Probe: Klettern → W6: [5] + ⌊9/2⌋ (4) + Adrenalin +3 = 12 vs SG 10 → **TREFFER**`

---

Die Finger finden Halt im rissigen Mauerwerk, der Stiefel schiebt sich gegen das Rohr — es hält, quietscht, hält. Du ziehst dich hoch, Arme brennen, aber der Adrenalin-Schub macht den Unterschied. Oben. Du rollst über die Mauerkante, landen auf einem flachen Dach, Kies unter den Händen, Regen ins Gesicht.

Unten: Rufen. Einer der Verfolger springt gegen die Mauer, kommt nicht hoch. Der andere sucht schon nach einem Umweg — er kennt das Viertel, er wird einen finden.

`Kodex: Stress +1. Aktuell 2/10. Verfolger: 2 aktiv, Umgehungsroute wird gesucht. Zeitfenster schmal.`

---

**Das Dach vor dir:**
Drei Gebäude nebeneinander, Lücken zwischen je zwei Metern. Links ein Dachaufbau mit Tür — wahrscheinlich verschlossen. Rechts eine Antenne, darunter ein Feuerleitern-Gerüst das zwei Stockwerke runterführt. Geradeaus: das nächste Dach, Sprung machbar, dahinter Dunkel.

Der Verfolger mit dem grauen Mantel ist weg aus deinem Sichtfeld. Das ist schlimmer als wenn du ihn siehst.

---

**Intel / Risiken / Zeitfenster**
- Verfolger 1: sucht Umgehungsroute, schätzungsweise 90 Sekunden bis er wieder auftaucht
- Verfolger 2: bleibt unten an der Mauer, Sichtlinie auf dich
- Dachaufbau-Tür: möglicherweise Deckung + Ausgang ins Gebäude
- Feuerleiter rechts: schneller Abstieg, aber laut und sichtbar

---

**Was
[...gekuerzt...]
```

</details>


---

## Interpretation

Pass-Rate ab 90% = Patch wirkt zuverlaessig fuer Produktions-Einsatz.
Pass-Rate 50-89% = Patch reduziert Bug, aber nicht zuverlaessig.
Pass-Rate unter 50% = Patch wirkt nicht. Neuer Ansatz noetig.
