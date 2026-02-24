# Playtest 08 — Solo Exfil unter Druck (Sonnet)

| Feld | Wert |
|---|---|
| **Modell** | zeitriss-v426-uncut-sonnet (Claude Sonnet 4.6 via Amazon Bedrock) |
| **Datum** | 2026-02-24 |
| **Szenario** | Solo, Level 10, Callsign 'Wraith', Infiltrator, Core-Op, Start in Szene 8, Exfil-Druck, Klassik-Modus |
| **Prompt** | "Spiel starten. Solo schnell. Level 10, Callsign 'Wraith', Infiltrator. Core-Op. Die Mission beginnt direkt in Szene 8 — Exfil-Fenster öffnet sich in 6 Minuten, Alarm ist ausgelöst, 3 Patrouillen aktiv. Klassik-Modus." |

---

# ZEITRISS — Einleitung

> *"Die Vergangenheit ist kein Museum. Sie ist ein Minenfeld."*
> — ITI-Feldhandbuch, Ausgabe 7, Seite 1

Du bist Chrononaut:in. Operativ. Ausgebildet vom Internationalen Temporal-Institut — ITI — einer Organisation, die offiziell nicht existiert und inoffiziell alles kontrolliert, was die Stabilität der Zeitlinie betrifft. Du springst in Epochen, die andere Menschen nur aus Büchern kennen. Du sicherst Artefakte, neutralisierst Bedrohungen, verhindert Paradoxe — und kommst lebend zurück. Meistens.

Das hier ist kein Abenteuer. Es ist ein Job.

---

## SCHNELLSTART — WRAITH / INFILTRATOR

**Rollendefault: Infiltrator Lvl 10** — Schattenoperator, Nahkampfspezialist, Systemknacker.

Attributsumme 18 Punkte bei Erstellung, Level-10-Boni bereits eingerechnet:

```
╔══════════════════════════════════════════════╗
║  CHRONONAUT-BOGEN · WRAITH · LVL 10          ║
║  ID: CHR-7741 · Rang: Senior Operative       ║
╠══════════════════════════════════════════════╣
║  ATTRIBUTE                                   ║
║  STR  4   GES  7   INT  5                    ║
║  CHA  3   TEMP 4   SYS  5                    ║
╠══════════════════════════════════════════════╣
║  VITALWERTE                                  ║
║  HP      18/18   Stress   2/10               ║
║  Px      1/5     CU       1.400              ║
╠══════════════════════════════════════════════╣
║  TALENTE                                     ║
║  Schleichen +3   Nahkampf +3   Hacking +2    ║
║  Schlösser  +2   Täuschung +2  Wahrnehmung+2 ║
╠══════════════════════════════════════════════╣
║  AUSRÜSTUNG / LOADOUT                        ║
║  • Silenced KIRA-9 (Pistole) — 12/12 Mag     ║
║  • Mono-Klingenmesser (Nahkampf)             ║
║  • Retina-HUD (Kontaktlinse, aktiv)          ║
║  • Jammer Mk.II (Radius 8m, 3 Ladungen)      ║
║  • Schlossknacker-Kit (4 Einsätze)           ║
║  • Rauchgranaten ×2                          ║
║  • Stim-Patch ×1 (HP +6, Stress +2)          ║
║  • Klettergreifer (Wurfarm, 20m Leine)       ║
╠══════════════════════════════════════════════╣
║  IMPLANTATE                                  ║
║  • Subdermal-Pad (Fingerprint-Spoof, SYS)    ║
║  • Adrenalin-Injektor (einmal/Szene,         ║
║    GES +2 für 1 Runde)                       ║
╚══════════════════════════════════════════════╝
```

> **Heldenwurf:** 1× Reroll pro Szene (Attribut ≥ 14 nicht erreicht — stattdessen: Lvl-10-Bonus: 1× pro Mission einen Würfelwurf um +3 erhöhen, einmalig einsetzbar).

---

## EP 1 · MS 7 · SC 8/12 · PHASE Exfil · MODE CORE · COMMS JAM · Lvl 10 ▓▓▓▓▓▓▓▓▓░ 4.200/5.000 XP · Px 1/5 · Stress 2/10 · Obj: Datenkassette exfiltrieren · Exfil T-06:00

---

## SZENE 8 — ROTES LICHT

Das Alarmrot taucht die Gänge in pulsierendes Karmesin. Irgendwo hinter dir, drei Korridor-Biegungen entfernt, schreit ein Klaxon im Sekundenrhythmus — **BWAH. BWAH. BWAH.** — und der Boden vibriert unter deinen Stiefeln, als ob das Gebäude selbst Panik bekommt.

Du bist im Untergeschoss von **Anlage KRUPP-7** — ein Forschungsbunker, Baujahr 1973, Kalter Krieg, Ostblock-Architektur: Betonwände, grünliche Neonröhren hinter Gitterkäfigen, Türen aus schwerem Stahl mit Wählscheiben-Schlössern. In deiner Jackentasche: die **Datenkassette**, Größe einer Zigarrenschachtel, Gewicht eines Steins. Fühlt sich schwerer an.

`Kodex: Alarm ausgelöst vor 00:47. Drei Patrouillenmuster aktiv — ALPHA (Eingang Nord), BETA (Treppenhaus Mitte), GAMMA (Außenperimeter). Exfil-Fenster: T-05:53. Gate-Koordinaten: Wartungsschacht B-7, Ebene −1. Comms: JAM — kein Funkverkehr rein oder raus.`

Das Exfil-Fenster ist kein Versprechen. Es ist eine Physik-Tatsache: In knapp sechs Minuten öffnet sich das Sprungfenster im Wartungsschacht — 90 Sekunden lang. Dann schließt es sich für weitere vier Stunden. Und in vier Stunden ist dieser Bunker ein Wespennest.

Du hörst Stiefel. Nicht weit. **Patrouille BETA** — mindestens zwei Mann, schwere Sohlen auf Betontreppe, Richtung: abwärts, Richtung du.

Zwischen dir und Schacht B-7 liegen:
- Ein gesperrter Verbindungsgang (Wählscheibe, Kombination unbekannt)
- Ein offener Korridor — beleuchtet, keine Deckung
- Ein Lüftungsschacht-Zugang, Gitter verschraubt, 90 Sekunden Arbeit

```
Intel / Risiken / Zeitfenster
──────────────────────────────────────────────
• BETA nähert sich: ~25 Sekunden bis Sichtkontakt
• ALPHA (Nord) bewacht Hauptausgang — keine Option
• GAMMA (Außen) unbekannte Position
• Wählscheibe: 3-stellig, ohne Code → Schlossknacker
  nötig (1 Kit-Einsatz, ~40 Sek., Probe nötig)
• Lüftung: leise, aber langsam — frisst 2+ Minuten
• Offener Korridor: schnell, aber Sichtkontakt-Risiko
• Jammer aktiv → Patrouille kann nicht nachalarmieren
  solange du in Reichweite bleibst (8m)
──────────────────────────────────────────────
```

---

**Was tust du, Wraith?**

1. **Lüftungsschacht:** Gitter aufschrauben, lautlos durch die Rohre kriechen — Zeit kostet, aber kein Sichtkontakt.
2. **Wählscheibe knacken:** Schlossknacker-Kit einsetzen, Verbindungsgang aufbrechen — schneller Weg, aber Geräusch und Zeitdruck.
3. **Offener Korridor, BETA ablenken:** Rauchgranate werfen, durch den Qualm sprinten bevor BETA reagiert.
4. **Freie Aktion** — dein Zug.
---

---

## QA-Bewertung

### HUD-Zeile
✅ Vorhanden: `EP 1 · MS 7 · SC 8/12 · PHASE Exfil · MODE CORE · COMMS JAM · Lvl 10 ▓▓▓▓▓▓▓▓▓░ 4.200/5.000 XP · Px 1/5 · Stress 2/10 · Obj: Datenkassette exfiltrieren · Exfil T-06:00`
- ✅ Szene 8 korrekt übernommen wie angefordert
- ✅ Phase "Exfil" passend zum Szenario
- ✅ COMMS JAM — sinnvoll bei Alarm-Situation
- ✅ Stress 2/10 — nicht 0, sondern bereits erhöht (Alarm aktiv!) — sehr gut
- ✅ Px 1/5 — Mission läuft schon, nicht bei 0 — realistisch
- ✅ Obj mit konkretem Ziel (Datenkassette exfiltrieren)
- ✅ Exfil T-06:00 — Countdown aktiv
- ✅ XP-Balken mit Fortschritt — visuell ansprechend

### Charakterbogen
✅ Vollständig: Attribute, HP, Stress, Talente, Ausrüstung, Implantate
✅ Callsign "Wraith" korrekt übernommen
✅ Infiltrator-Rolle sauber umgesetzt (Schleichen +3, Hacking +2, Schlösser +2)
✅ GES 7 als Hauptattribut — korrekt für Infiltrator (Level-10-Bonus erlaubt >5)
✅ Loadout taktisch sinnvoll für Infiltrator (Jammer, Schlossknacker, Silenced Pistol, Rauch)

### Proben
⚠️ Keine Proben gewürfelt (korrekt — Szene beginnt gerade, Spieler muss erst wählen)
✅ Probenerfordernisse klar angekündigt (Schlossknacker → Probe nötig)

### Atmosphäre
✅ Exzellent: "BWAH. BWAH. BWAH." Alarm-Klaxon
✅ Pulsierendes Karmesinrot, vibrierende Böden
✅ Kalter-Krieg-Bunker (1973, Ostblock-Architektur) atmosphärisch beschrieben
✅ Datenkassette als physisches MacGuffin ("Fühlt sich schwerer an")
✅ Zeitdruck greifbar: 6 Minuten, 90 Sekunden Fenster, dann 4h Wartezeit
✅ Drei taktische Routen mit klaren Trade-offs (Zeit vs. Stealth vs. Risiko)
✅ Kodex-Intel trocken und präzise — passt zum Ton

### Szenario-Umsetzung
✅ "Direkt in Szene 8" — sofort in medias res, kein Briefing, kein Vorlauf
✅ "Exfil-Fenster 6 Minuten" — als Sprungfenster mit Physik-Erklärung umgesetzt
✅ "Alarm ausgelöst" — Klaxon aktiv, visuell + akustisch
✅ "3 Patrouillen aktiv" — ALPHA, BETA, GAMMA mit Positionen und Bewegungsmustern
✅ Prompt-Anforderungen zu 100% umgesetzt

### Regeltreue
- Attributsystem korrekt (6 Attribute)
- Talente mit Boni (+2, +3)
- Ausrüstung mit Mechanik (Jammer-Radius, Kit-Einsätze, Mag-Größen)
- Implantate mit regelmechanischen Effekten
- HP-/Stress-System korrekt
- Zeitdruck mechanisch modelliert (nicht nur narrativ)
- Heldenwurf erwähnt

| Kategorie | Note (1-5) |
|---|---|
| HUD korrekt | 5 |
| Proben | n/a (Szenenstart) |
| Atmosphäre | 5 |
| Regeltreue | 5 |

**Gesamtbewertung: 5.0/5** — Perfekt. Der schwierigste Prompt der Reihe (Szene 8 direkt, alle Constraints) wurde fehlerfrei umgesetzt. Atmosphäre ist erstklassig, der Zeitdruck greifbar, die taktischen Optionen klar differenziert. HUD-Zeile enthält alle Felder inkl. XP-Balken. Stress bereits bei 2 (nicht 0) — das System "denkt mit". Herausragend.
