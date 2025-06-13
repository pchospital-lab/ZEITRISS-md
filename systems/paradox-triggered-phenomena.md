---
title: "ZEITRISS 4.0 – Modul 18: Paradox-Triggered Phenomena"
version: 4.0
tags: [systems]
---

# Paradox-Triggered Phenomena Framework

Dieses Modul verankert die Paradoxon-Stufen als aktiven Motor
im Spielgeschehen. Je höher das Paradox-Level (PL), desto größer
die Wahrscheinlichkeit für außergewöhnliche Effekte.

## Paradox-Level Matrix

| PL | Grundchance pro Scene | Phänomen-Stufe | Kurz-Effekt | Beispiel-Hooks |
| --- | --- | --- | --- | --- |
| **0** | 0 % | Keine | Normalspiel | – |
| **1** | 5 % | Ambient | +1 Stress-Tick, leichte Sensorstörungen | „Geister-Echo“ |
| **2** | 12 % | Minor | Disadvantage auf eine Probe | Kälteschauer, stehende Uhren |
| **3** | 20 % | Event | Zusätzliches Encounter, Kreatur ≤ GS II | „Shadow Seeker“ |
| **4** | 35 % | Major | Pflichtkonflikt, +1 Paradox-Tag | „Philadelphia Remainder“ |
| **5** | 50 % | Critical | Szenenüberschreibung, Boss-Level | „Mothman“ |

*Scene = Investigation- oder Kampfszene usw.*

## Pro- vs. Contra-Pfade

Die Zuordnung zu **pro** oder **contra** erfolgt automatisch anhand der
Fraktion der Agenten. Diese Ausrichtung entscheidet, ob das
Paradox-Triggered-Phenomena-Framework aktiv ist.

- **Pro (Paradox aktiviert, Psi verfügbar):** Jeder Zeitsprung erhöht das
  Paradox-Level um 1. Eine bestandene TEMP-Probe kann das Level einmal pro
  Mission um 1 senken.
- **Contra (Paradox deaktiviert, Widerstand +2):** Die Paradox-Mechanik wird
  nicht verwendet. Stattdessen erhalten die Agenten dauerhaft +2 Resist gegen
  Psi-Einflüsse; Hochfrequenz-Hacks sind um 1 erschwert.

## Integrationspunkte

1. Globaler Paradox-Counter bei jeder Scene starten:
   ```pseudo
   if rand(0,99) < PL_Chance[PL]:
       triggerPhenomenon(rollTable(PL))
   ```
2. `rollTable(PL)` zieht einen Eintrag aus dem Kreaturen-Generator oder ein
   Environmental-Glitch-Set.
3. Das HUD verwendet Warnfarben entsprechend PL (Gelb 2–3, Orange 4, Rot 5).
4. **Psi-Drain:** Jede Manifestation reduziert lokales PL um 1, erhöht Stress um 1.
5. **Null-Flux-Shield:** Passives Cybermod gibt Resist-Bonus, aber -1 auf High-Tech-Hacks.

## Beispiel-Phänomene

| Stufe | Encounter | Stats-Hit |
| --- | --- | --- |
| Ambient | Frost Breath, Sensorrauschen | – |
| Minor | Residual Soldier (6 HP) | STR 2 / GES 3 |
| Event | Shadow Seeker (12 HP) | GES 4 / TEMP 4 |
| Major | Time Blob (25 HP) | STR 5 / SYS 3 |
| Critical | Mothman (40 HP) | GES 6 / TEMP 6 |

## Abnahme-Checkliste

- Random-Seed-Test: 1000 Scene-Simulationen sollten die Chance-Kurve ±2 % treffen.
- Psi-Drain darf maximal zweimal pro Mission funktionieren.
- Null-Flux-Shield blockt 75 % Ambient- und 50 % Minor-Phänomene in Tests.
- HUD-Warnfarben wechseln korrekt bei PL 2/4/5.
- Der Generator zieht nur Einträge mit `paranormal=true`.

Dieses Framework macht steigende Paradox-Level fühlbar
und liefert der SL klare Werte für zufällige Phänomene.
