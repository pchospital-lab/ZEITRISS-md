# Turn 1

# ZEITRISS — Save geladen

`Kodex: Session-Anker gesetzt. Save solo-rampart-runD erkannt. Migration läuft.`

---

## Load-Recap: RAMPART

Ich migriere den Save auf Schema v7 und normalisiere dabei einige Felder:

**Attribute-Migration:** `SOC` → `CHA`, `WIS` existiert nicht im ZEITRISS-Attributsystem. Da `WIS 3` thematisch am ehesten zu `INT` passt und `INT` bereits mit 3 belegt ist, behandle ich `WIS` als Duplikat — kein Wert geht verloren, `INT` bleibt 3. `CHA` (ex-SOC) = 2.

**Attribut-Summe-Check:** GES 4 + INT 3 + TEMP 4 + CHA 2 + STR 5 = 18. ✓ Korrekt.

**LP-Anpassung:** `lp_max 13` liegt über dem Startwert 10 — plausibel mit STR 5 (Hausregel-Anker). Ich übernehme 10/13 als aktuell/max.

**SYS:** `sys_max 14` ist ungewöhnlich hoch für Lvl 1 (Standard wäre SYS als Attribut, nicht Slot-Pool). Ich behandle `SYS` als Attribut-Wert 0 und markiere das als Migrationslücke — du kannst das im HQ klären.

**Px:** 1 (aus Character-Feld übernommen).

**Stress:** 3 — erhöht, aber unter Grenzwert.

`Kodex: ITI-Ruf 2 übernommen. Lizenz Tier II aktiv.`
`Kodex: NPC Dr. Veith (Kontakt, aktiv) in npc_roster übernommen.`
`Kodex: Echo — Mission 1: Lagerhaus gesichert.`
`Kodex: Stress 3 — im HQ-Debrief-Reset auf 0 normalisiert (HQ-Save-Invariante).`

---

```
EP ? · MS 1 abgeschlossen · SC 00/-- · PHASE HQ · MODE CORE
COMMS OK · Lvl 1 ▓░░░░░░░░░ 0/1 XP · Px 1/5 · Stress 0/5
ITI-Ruf: 2 · Lizenz Tier II
```

`Kodex: Szene — ITI-HQ / Quarzatrium · Nullzeit.`

---

## Heimkehr

Das Quarzatrium empfängt dich mit dem vertrauten Summen der Klimaanlage und dem gedämpften Licht der Deckenstreifen — kaltes Weiß, das niemals Nacht kennt. Dein Schritt hallt auf dem Verbundstein. Irgendwo schiebt ein Wartungstechniker einen Trolley mit Ausrüstungskisten vorbei, ohne aufzuschauen.

Du bist zurück. Das Lagerhaus liegt hinter dir.

Am Duty-Desk lehnt Archivarin Mira über ein Terminal, tippt etwas, hält inne. Hebt den Blick. *"Kaspar. Rundbericht läuft noch. Stress-Werte sehen aus wie eine Kurve die jemand mit dem Knie gebogen hat — geh in die Klinik, bevor du irgendwas anderes tust."* Sie meint es nicht unfreundlich.

`Kodex: Stress-Reset abgeschlossen. HQ-Basis erreicht.`
`Kodex: HQ-Zustand stabil. Deepsave möglich.`
`Kodex: Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`

---

**Migrierter Charakterstand — RAMPART**

| Attribut | Wert | Würfel |
|----------|------|--------|
| STR | 5 | W6 |
| GES | 4 | W6 |
| INT | 3 | W6 |
| CHA | 2 | W6 |
| TEMP | 4 | W6 |
| SYS | 0* | — |

*SYS-Migrationslücke — bitte im HQ klären.*

**LP:** 10/13 · **Stress:** 0/5 · **Px:** 1/5
**Talent:** Nahkampf-Taktik
**Ausrüstung:** Kampfmesser (T1), Schwere Rüstung (T1), Comlink (T1)
**Wallet:** 100 CU · **ITI-Ruf:** 2 · **Lizenz Tier II**

---

## HQ-Menü

**Was tust du?**

1. **Erkunden** — HQ manuell, filmische Szene (Klinik, Archiv, Ausrüstung)
2. **Schnell-HQ** — kurzer Lagedurchlauf, direkt zum Save-Angebot
3. **`!save`** — migrierten Stand jetzt als sauberes v7-JSON exportieren
4. **Freie Aktion** — sag, was du willst
