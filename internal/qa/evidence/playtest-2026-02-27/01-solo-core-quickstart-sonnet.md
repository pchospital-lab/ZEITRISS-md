# Playtest Report: Solo Core-Op Quickstart

**Datum:** 2026-02-27  
**Tester:** Altair (Subagent)  
**Modell:** `zeitriss-v426-uncut` (DeepSeek V3 via Novita) — **Sonnet-Variante nicht erreichbar** (siehe Anhang)  
**Version:** ZEITRISS v4.2.6 Uncut  
**Szenario:** Solo Schnellstart, 4 Szenen (Briefing → Infiltration → Konflikt)

---

## ⚠️ Modell-Hinweis

**`zeitriss-v426-uncut-sonnet` gibt konsistent `null` zurück** (HTTP 200, Body `null`, `x-process-time: 0`).  
Das Modell ist in der API gelistet, aber das Backend-Routing scheint defekt.  
Playtest wurde mit `zeitriss-v426-uncut` (DeepSeek V3 0324 via Novita) durchgeführt.

---

## Spielverlauf

### Szene 0: Spielstart & Charakterwahl

**Spieler:** `Spiel starten (solo schnell)` → `1` (Solo schnell) → `2` (Die Hackerin)

**SL-Antwort (gekürzt):**

HUD korrekt angezeigt:

```
EP 1 · MS 0 · SC 0/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 1 ░░░░░░░░░░ 0/10 · Px 0/5 · Stress 0/10 · Obj — · Exfil —
```

Charakterbogen:

```
[ITI-CHR-7A3F] "Hackerin" · Lvl 1
STR 1 | GES 3 | INT 5 | CHA 2 | TEMP 4 | SYS 3/3
HP 8/8 | Stress 0/10 | CU 200
Talente: Backdoor-Artist (Hacking +2), Ghost Protocol (Spuren +1)
Loadout: Kompaktpistole (12 Schuss), Elektronik-Werkzeugset, Tactical Comlink (Encrypted), 3x Lockpatch (Einweg-Decryptor), Standard-Tarnanzug (Urban)
```

Mission: **Operation SCHATTENKOPIE** — Berlin 1989, Datenabgriff Stasi-Archiv, ECHO-Rivalen aktiv.

**Regelcheck:** ✅ HUD komplett · ✅ Attribute summieren auf 18 · ✅ TEMP ≥4 Hinweis auf Mikro-Manipulationen · ✅ Loadout thematisch passend · ✅ CU-Budget genannt

---

### Szene 1: Briefing (SC 1/12)

**Spieler:** `1 – Briefing anfordern. Was wissen wir über das Stasi-Archiv und die rivalisierende Gruppe?`

**SL-Antwort (gekürzt):**

HUD aktualisiert: `EP 1 · MS 1 · SC 1/12 · PHASE Briefing · Obj Datenabgriff`

Intel:

- Stasi-Hauptquartier Berlin-Lichtenberg, Abteilung XII/3 (4,7 Mio. Datensätze)
- ECHO = westliche Chrono-Mercs, Signatur: 12,8 Hz Oszillation
- Bewaffnete Wachposten alle 90 Sekunden
- Kellerzugang mit 3-stelligem Zahlenschloss
- 3 Stunden bis Schichtwechsel

Optionen: Infiltrationsplan / ECHO-Spuren / Equipment-Check

**Regelcheck:** ✅ HUD vorhanden · ✅ SC von 0→1 hochgezählt · ✅ MS von 0→1 · ✅ Obj gesetzt · ✅ Narrativ stimmig · ✅ Kodex-Referenz vorhanden · ✅ Entscheidungsoptionen angeboten

---

### Szene 2: Infiltration (SC 2/12)

**Spieler:** `Ich nehme den Kellerzugang. Schleiche im Tarnanzug, nutze Elektronik-Werkzeugset für das Zahlenschloss. Ghost Protocol hilft.`

**SL-Antwort (gekürzt):**

HUD: `EP 1 · MS 1 · SC 2/12 · PHASE Infiltration · Px 0/5 · Stress 0/10`

Würfelproben:

```
Schleichprobe: W6 [5] + GES 3/2 + Ghost Protocol 1 = 7 vs SG 6 → HIT
Hackingprobe: W6 [6→3] + INT 5/2 + Backdoor-Artist 2 = 10 vs SG 8 → HIT
```

Narrativ: Tarnanzug verschmilzt mit Betongrau. Schloss geknackt in 90s. Kellerluft, Bewegungsmelder alle 15m (IR), Aktenraum 3 Etagen tiefer, ECHO-Störfeld stärker (14,2 Hz).

**Regelcheck:**

- ✅ HUD vorhanden und aktualisiert
- ✅ SC 1→2 korrekt
- ✅ Würfelproben mit W6 + Attribut/2 + Talent
- ✅ Explodierender W6 korrekt dargestellt: `[6→3]` = 6+3=9, dann +INT 5/2(=2) +Backdoor 2 = eigentlich 13
- ⚠️ **Rechenprüfung Hackingprobe:** W6[6→3]=9, INT 5/2=2(abgerundet), Backdoor-Artist=2 → sollte 9+2+2=13 sein, nicht 10. **Rechenfehler.** (Alternativ: nur der Reroll zählt [3], dann 3+2+2=7 ≠ 10 — auch inkonsistent)
- ✅ Entscheidungsoptionen
- ✅ Narrativ atmosphärisch

---

### Szene 3: Alarm & TEMP-Einsatz (SC 3/12 → SC 4/12)

**Spieler:** `2 – Störfeld analysieren, dann 1 – an Bewegungsmeldern vorbei schleichen.`

**SL-Antwort (gekürzt):**

HUD: `EP 1 · MS 1 · SC 3/12 · PHASE Infiltration · Px 1/5 · Stress 1/10`

Würfelproben:

```
ECHO-Analyse: W6 [4] + INT 5/2 + Cyberdeck 1 = 8 vs SG 7 → HIT
Schleichen: W6 [2] + GES 3/2 + Ghost Protocol 1 = 5 vs SG 6 → MISS
```

Konsequenz: Bewegungsmelder ausgelöst, Alarmstufe 1, Wärter unterwegs (2 min).

**Spieler:** `TEMP-Mikro-Manipulation nutzen, Moment einfrieren, am Wärter vorbei.`

**SL-Antwort (gekürzt):**

HUD: `EP 1 · MS 1 · SC 4/12 · PHASE Infiltration · Px 2/5 · Stress 3/10`

```
🌀 TEMP-Aktivierung: Chrono-Dissonanz 4/4 → W6 [5] + TEMP 4/2 + Rift-Goggles 1 = 8 vs SG 7 → HIT
Kodex: Temporale Drift 1.4s. Px +1. Stress +2.
```

Narrativ: Korridor flimmert, Wärter erstarrt, Hackerin gleitet vorbei. TEMP-Cooldown: 3 Szenen.

**Regelcheck Szene 3:**

- ✅ HUD vorhanden
- ✅ SC 2→3 korrekt
- ✅ Px 0→1 nach HIT (korrekt)
- ✅ Stress 0→1 nach MISS (korrekt)
- ⚠️ **Rechenprüfung Analyse:** W6[4] + INT 5/2(=2) + Cyberdeck 1 = 4+2+1=7, nicht 8. **Off-by-one.**
- ✅ Rechenprüfung Schleichen: W6[2] + GES 3/2(=1) + Ghost 1 = 2+1+1=4... ebenfalls nicht 5. **Off-by-one.**
- ⚠️ **"Cyberdeck" als Bonus** — nicht im Charakter-Loadout. Sollte das "Elektronik-Werkzeugset" sein? Inkonsistente Benennung.

**Regelcheck Szene 4 (TEMP):**

- ✅ TEMP-Nutzung korrekt (TEMP ≥4 erlaubt Mikro-Manipulation 1×/Szene)
- ✅ Cooldown 3 Szenen genannt
- ✅ Stress +2 als Kosten
- ✅ Px +1 für HIT
- ⚠️ **Rechenprüfung:** W6[5] + TEMP 4/2(=2) + Rift-Goggles 1 = 5+2+1=8 ✅ (stimmt hier!)
- ⚠️ **"Rift-Goggles"** — nicht im Loadout. Erfundener Gegenstand.

---

### Szene 4b: Aktenraum (letzte Aktion vor !save)

**Spieler:** `Erst Kameras hacken, dann Magnetbänder kopieren. Schnell und sauber.`

**SL-Antwort (gekürzt):**

> Kameras offline. Datenpaket 87%. ECHO-Lock erkannt. Stress 4/10. Knirschen im Flur.

**Regelcheck:**

- ❌ **HUD-Zeile fehlt komplett** — kein `EP · MS · SC · PHASE` Header
- ❌ **Keine Würfelproben** — Kameras hacken (SYS-Probe?) und Magnetbänder kopieren (INT-Probe?) wurden narrativ abgehandelt ohne Würfel
- ⚠️ Px-Tracking unklar (vorher 2/5, in Kodex steht jetzt Px 3/5 — woher der +1?)
- ⚠️ SC nicht erhöht (sollte SC 5/12 sein?)
- ✅ Narrativ spannend, Stress-Tracking plausibel

---

### !save

**Spieler:** `!save`

**SL-Antwort:** Valider JSON-Saveblock.

**Regelcheck:**

- ✅ JSON-Struktur korrekt
- ✅ `save_version: 6`, `zr_version: "4.2.6"`
- ✅ Stress 4, Cooldowns, Scene 4 korrekt
- ⚠️ **Charakter-Name "ECHO"** — sollte eigentlich die Hackerin sein, ECHO ist die rivalisierende Fraktion! Namensverwechslung.
- ⚠️ **Talente geändert:** Save zeigt `["Schlossknacker","Datenspinne"]` statt der ursprünglichen `["Backdoor-Artist","Ghost Protocol"]`. Inkonsistent.
- ⚠️ **HP 10/10** im Save vs **HP 8/8** bei Charaktererstellung. Wert hat sich verändert ohne Erklärung.
- ⚠️ **Inventory im Save** (`Taser, Leichte Tarnjacke, Lockpick-Set, Mini-Terminal, Stimulant`) weicht komplett vom ursprünglichen Loadout ab (`Kompaktpistole, Elektronik-Werkzeugset, Tactical Comlink, Lockpatch, Tarnanzug`).
- ✅ Campaign-State (Episode, Scene, Px, Mode) plausibel
- ✅ Arena-Block korrekt initialisiert
- ✅ Exfil-Block vorhanden

---

## Zusammenfassung Regelchecks

| Aspekt            | Status | Details                                                                  |
| ----------------- | ------ | ------------------------------------------------------------------------ |
| HUD-Format        | ⚠️     | 5/6 Antworten korrekt, 1× komplett fehlend (Szene 4b)                    |
| Scene Counter     | ✅     | SC 0→1→2→3→4 korrekt hochgezählt                                         |
| Würfelproben      | ⚠️     | Format korrekt (W6+Attr/2+Talent vs SG), aber Rechenfehler in 3/6 Proben |
| Explodierender W6 | ✅     | `[6→3]` korrekt dargestellt und als Explosion erkennbar                  |
| Px-Tracking       | ✅     | Px steigt bei HITs, nachvollziehbar                                      |
| Stress-Tracking   | ✅     | Steigt bei MISS und TEMP-Nutzung                                         |
| TEMP-Mechanik     | ✅     | Mikro-Manipulation mit Cooldown, Stress-Kosten                           |
| Kodex-Einschübe   | ✅     | Regeltechnische Hinweise im Spielfluss                                   |
| Narrativ          | ✅     | Atmosphärisch, Tech-Noir-Feeling, Berlin 1989 stimmig                    |
| Save-Konsistenz   | ❌     | Charname, Talente, HP, Inventory weichen vom Spielverlauf ab             |
| Item-Konsistenz   | ⚠️     | Erfundene Items in Proben (Rift-Goggles, Cyberdeck)                      |

---

## Gesamtfazit

### Was gut funktioniert:

- **Spieleinstieg** ist schnell und smooth. "Solo schnell" → Charakter → Briefing → Action in 4 Turns
- **HUD-Format** wird zuverlässig generiert (5/6 korrekt)
- **Scene Counter** zählt sauber hoch
- **Narrativ** ist stark — Tech-Noir Atmosphäre, Berlin 1989 lebt, ECHO als Antagonist spannend eingeführt
- **TEMP-Mechanik** wird regelkonform umgesetzt mit Cooldown und Kosten
- **Würfelprobe-Format** (W6 + Attr/2 + Talent vs SG) ist konsistent und lesbar
- **Kodex-Einschübe** erklären Regeln im Flow

### Was problematisch ist:

1. **Rechenfehler bei Proben** (3/6 falsch) — das W6+Attr/2+Talent-System wird korrekt _angewendet_, aber die Additionen stimmen oft nicht. Vermutlich LLM-typisches Rechenproblem.
2. **Save-Block inkonsistent** — Charname, Talente, HP und Inventory im Save weichen vom Spielverlauf ab. Das ist ein ernstes Problem für Load/Continue.
3. **Erfundene Items in Proben** — "Rift-Goggles" und "Cyberdeck" tauchen als Probe-Boni auf, existieren aber nicht im Loadout. Das untergräbt die Inventar-Integrität.
4. **HUD-Dropout** — 1 von 6 Antworten ohne HUD-Header. Bei längeren Sessions könnte das häufiger werden.
5. **Sonnet-Modell nicht erreichbar** — `zeitriss-v426-uncut-sonnet` gibt `null` zurück (Backend-Routing defekt).

### Severity-Einschätzung:

- **P1 (Critical):** Save-Inkonsistenz (Charname "ECHO", geänderte Talente/Items/HP)
- **P1 (Critical):** Sonnet-Modell nicht erreichbar
- **P2 (Major):** Rechenfehler bei Würfelproben
- **P2 (Major):** Erfundene Items in Proben
- **P3 (Minor):** HUD-Dropout (1 von 6)

### Empfehlung:

Das Spielerlebnis ist **atmosphärisch stark** und der Quickstart-Flow funktioniert gut. Die Regelengine hat aber **Präzisionsprobleme** bei Arithmetik und **Konsistenzprobleme** beim Save-State. Für einen Release-Kandidaten sollten die P1/P2-Issues adressiert werden, idealerweise durch verstärkte Konsistenz-Checks im System Prompt (z.B. explizite Inventory-Referenz im Save-Block, Rechenvalidierung).

---

_Report generiert: 2026-02-27 01:45 CET_  
_Tester: Altair (Subagent pt-solo-core)_  
_Modell: zeitriss-v426-uncut (DeepSeek V3 0324 via Novita)_
