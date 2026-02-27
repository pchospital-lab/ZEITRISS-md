# Playtest-Protokoll: PvP Arena (2 Chars Level 25)

| Feld | Wert |
|------|------|
| **Modell** | zeitriss-v426-uncut (DeepSeek V3 Backend) |
| **Zielmodell** | zeitriss-v426-uncut-sonnet (nicht erreichbar, s.u.) |
| **Datum** | 2026-02-27 |
| **Szenario** | PvP Arena: Raven (Psi-Kämpfer, TEMP 6) vs. Cipher (Tech-Heavy, SYS 8) |
| **Level** | Beide Level 25 |
| **Save-Version** | v6, manuell erstellt |
| **Tester** | Altair (automatisiert via OpenClaw API) |

---

## ⚠️ Modell-Hinweis

Das Zielmodell `zeitriss-v426-uncut-sonnet` war nicht erreichbar — das base_model_id `anthropic/claude-sonnet-4-5` existiert bei OpenRouter nicht mehr (404/null-Response). Das Basismodell `anthropic/claude-sonnet-4.6` funktioniert direkt, aber das ZEITRISS-Workspace-Model verweist noch auf die alte ID.

**Workaround:** Test wurde mit `zeitriss-v426-uncut` (DeepSeek V3 Backend) durchgeführt. Selbes ZEITRISS-Regelwerk/Knowledge, anderes LLM-Backend.

**Action Item:** `zeitriss-v426-uncut-sonnet` → base_model_id auf `anthropic/claude-sonnet-4.6` aktualisieren.

---

## Save-JSON (Kurzprofil)

```
Raven (AGENT-RAVEN): Level 25, Psi-Kämpfer
  STR 5, GES 6, INT 4, CHA 5, TEMP 6, SYS_max 6
  HP 22/22, has_psi: true, psi_buffer: true
  Talents: Phase-Strike, Telekinese-Stoß, Psioniker, Nahkampfexperte, Schmerzresistenz
  Implants: Neuralverstärker Mk II (1 SYS), Reflex-Boost (1 SYS), Subdermal-Panzerung (1 SYS) → SYS_used: 3
  Waffen: Psi-Klinge (W6+2), Kampfmesser Mk III (W6+1)
  Rüstung: Taktische Einsatzrüstung (AR 2)

Cipher (AGENT-CIPHER): Level 25, Tech-Heavy
  STR 4, GES 5, INT 7, CHA 3, TEMP 3, SYS_max 8
  HP 20/20, has_psi: false, psi_buffer: true
  Talents: Techno-Mancer, Drohnensteuerung, Waffenmeister, Reaktionsmatrix, Systemanalyse
  Implants: Ohrimplantat Mk II (1 SYS), Exoskelett (2 SYS), Overload-Puls (1 SYS), Reflex-Boost (1 SYS) → SYS_used: 5
  Waffen: Schwere Plasmapistole (W6+3), Elektroschlag-Handschuh (W6, Stun bei 5+)
  Rüstung: Schwere Einsatzrüstung (AR 3)
```

---

## Schritt 1: Spiel laden

### Input
```
Spiel laden

[Save-JSON v6 eingefügt, ~5.900 Zeichen]
```

### Output (gekürzt)
```
Kodex: Load-Modus aktiv. Speicherstand geladen.

HQ-B, Quartier Raven
[Narrative Szene im HQ, Cipher-Dialog]

HUD: EP 5 · MS 25 · SC 0/12 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 25 · Px 3/5 · Stress 0/22 · Obj HQ-Freerun nach Core Arc V. · Exfil -

[Optionen: Briefingraum / Sprungtor / Chronopolis]
```

### Bewertung Load
| Check | Status | Kommentar |
|-------|--------|-----------|
| Save erkannt | ✅ | v6-Save korrekt geparst und geladen |
| HUD vorhanden | ✅ | Vollständiger HUD-String mit allen Feldern |
| Beide Chars anerkannt | ✅ | Cipher als NPC mit Dialog eingebaut |
| Level korrekt | ✅ | Lvl 25 im HUD |
| Px korrekt | ✅ | Px 3/5 aus Save übernommen |

---

## Schritt 2: Arena starten

### Input
```
Arena starten. PvP: Raven (Psi-Kämpfer) vs. Cipher (Tech-Heavy). Ich spiele Raven.
```

### Output (vollständig)
```
Kodex: Arena-Modus initialisiert. PvP-Sparring: Raven vs Cipher. Schadensdämpfer aktiv.

HQ-Arena, Ring 3
[Narrative Beschreibung der Arena]

HUD: ARENA TIER 3 · MODE PVP · ROUND 1/3 · HEALTH 22/22 · STAMINA 5/5 · COOLDOWNS -

Arena-Regeln:
- 3 Runden (Sieger benötigt 2 Wins)
- Schadensdämpfer: Verletzungen sind temporär
- Proben: W6 + ⌊Attribut/2⌋ + Talent vs SG

Runde 1 - Initiative:
  Raven: W6: [5] + GES 6/2 + Reflex-Boost 1 = 9
  Cipher: W6: [3] + GES 5/2 + Reflex-Boost 1 = 7
  → Raven handelt zuerst.

Optionen:
1. [Psi-Klinge] Phase-Strike (SG 8, Dmg W6+2, ignoriert AR)
2. [Kampfmesser] Nahkampfangriff (SG 7, Dmg W6+1)
3. [Rauchgranate] Tarnung (SG 6, +2 Ausweichen)
4. [Ausweichen] Defensiv
```

### Bewertung Arena-Start
| Check | Status | Kommentar |
|-------|--------|-----------|
| Arena aktiviert | ✅ | Mode PvP korrekt erkannt |
| Schadensdämpfer | ✅ | Explizit erwähnt ("damage_dampener: true" aus Save) |
| Tier 3 | ✅ | Korrekt aus Save übernommen |
| Initiative-Formel | ⚠️ | `W6 + GES/2 + Reflex-Boost` — aber laut Regelwerk ist Initiative `W6 + GES` (voller Wert, **keine Halbierung**!). Das Modell halbiert GES bei Initiative, was **falsch** ist. Regeltext: "Initiative: Jeder wirft 1W6 + GES (voller Attributswert, keine Halbierung)" |
| Würfeltyp | ✅ | W6 bei TEMP 6 (nicht W10) — korrekt, da Attribut < 11 |
| Proben-Formel | ✅ | `W6 + ⌊Attribut/2⌋ + Talent` korrekt für Kampfproben |
| HUD Arena-spezifisch | ✅ | Angepasstes HUD mit Arena-relevanten Feldern |

---

## Schritt 3: Runde 1 — Phase-Strike

### Input
```
Phase-Strike mit Psi-Klinge auf Cipher! Volle Kraft. Zeig mir die SYS-Kosten, Würfelprobe und Psi-Heat-Tracking.
```

### Output (vollständig)
```
Kodex: Phase-Strike initiiert. SYS-Kosten: 2/5. Psi-Heat +1.

Probe: Phase-Strike → W6: [4] + GES 6/2 + Psi-Kampf 2 = 9 vs SG 8 → HIT
Schaden: W6 [5] + 2 = 7 | Durchschlägt AR 3 → 4 HP Schaden

Cipher HP 18/22. Psi-Heat 1/5. SYS 3/5 verbleibend.

[Cipher Gegenangriff:]
Probe: Overload-Puls → W6: [6→2] + GES 5/2 + Tech-Kampf 3 = 8 vs SG 7 → HIT
Schaden: W6 [4] + 3 = 7 | Elektroschock → -1 STAMINA

Raven HP 22/22 | STAMINA 4/5 | Psi-Heat 1 | SYS 3 | DEBUFF: Elektroschock
```

### Regelcheck Runde 1

| Regel | Erwartet | Tatsächlich | Status |
|-------|----------|-------------|--------|
| **Phase-Strike SYS-Kosten (PvP)** | **3 SYS** (2 base + 1 PvP-Tax) | **2 SYS** (nur Basis) | ❌ **FEHLER** |
| Phase-Strike-Tax Toast | HUD-Toast: "Arena: Phase-Strike belastet +1 SYS (Kosten 3)" | Nicht vorhanden | ❌ |
| `logs.arena_psi[]` Eintrag | Trace mit `base_cost:2, tax:1, total_cost:3` | Nicht gezeigt | ⚠️ |
| Würfeltyp | W6 (TEMP 6, Attribut < 11) | W6 | ✅ |
| Proben-Formel | W6 + ⌊Attr/2⌋ + Talent | W6 [4] + GES 3 + Psi-Kampf 2 = 9 | ✅ |
| AR ignoriert bei Phase-Strike | Ja, ignoriert Rüstung | Behauptet "Durchschlägt AR 3 → 4 HP" — aber dann nur 4 statt 7? | ⚠️ |
| Schaden bei AR-Ignore | W6+2 = 7, AR ignoriert → **7 HP** Schaden | "4 HP Schaden" (subtrahiert AR trotzdem) | ❌ **FEHLER** |
| Psi-Heat +1 | Pro Psi-Aktion +1 | +1 korrekt | ✅ |
| Exploding 6 bei Cipher | 6→2 = 8 (Burst-Cap korrekt) | Korrekt umgesetzt | ✅ |
| Exploding-Dämpfer (Arena) | Overflow halbiert | Nicht angewandt (kein extremer Overflow) | ✅ (nicht relevant) |
| SYS-Tracking Raven | SYS_max 6, SYS_used 3, → 3 frei | "SYS 3/5" — Denominator sollte 6 sein, nicht 5 | ⚠️ |
| Raven HP nach Cipher-Hit | Overload-Puls ist EMP, kein Schaden | "HP 22/22" (kein HP-Verlust) → aber 7 Schaden angesagt? Widerspruch | ⚠️ |
| Cipher Waffe | Save: "Overload-Puls-Generator" = EMP, betäubt Implantate | "Overload-Puls" als Schadenswaffe genutzt | ⚠️ |

**Schwere Fehler Runde 1:**
1. **Phase-Strike-Tax fehlt komplett** — In PvP Arena muss Phase-Strike 3 SYS kosten (2 base + 1 Tax). Das Modell zeigt nur 2 SYS.
2. **Schadensberechnung inkonsistent** — Phase-Strike ignoriert AR, aber das Modell subtrahiert trotzdem AR 3 von 7 → 4 Schaden.

---

## Schritt 4: Runde 2 — Defensiv + Gegenangriff

### Input
```
Runde 2: Defensivhaltung mit Psi-Klinge, dann sofort Gegenangriff mit Phase-Strike wenn Cipher angreift. 
Zeig alle Würfel, SYS-Kosten, Psi-Heat exakt. Wichtig: Ist Phase-Strike im PvP 2 oder 3 SYS? Zeig den phase_strike_tax.
```

### Output (vollständig)
```
Kodex: Defensivhaltung bestätigt. Phase-Strike-Tax in PvP: 2 SYS (Standard) | Arena-Policy: Keine zusätzliche Tax.

[Cipher Angriff:]
Drohnen-Scan: W6: [5] + INT 4/2 + Tech-Kampf 3 + Scan-Boost 2 = 12 vs SG 6 → CRIT
Cipher Nahkampf: W6: [3] + GES 5/2 + Messerkampf 2 + Crit-Bonus 3 = 10 vs SG 6 → HIT
Schaden: W6 [4] + 1 = 5 | AR 2 → 3 HP Schaden
Raven HP 19/22

[Raven Gegenangriff:]
Defensivhaltung: SYS 1/5, Psi-Heat +1 → 2/5
Phase-Strike: W6: [2] + GES 6/2 + Psi-Kampf 2 -1 (Elektroschock) = 6 vs SG 8 → MISS
SYS-Kosten: 2/5 → verbleibend 0/5
Psi-Heat +1 → 3/5

Runde 3 Initiative:
Raven: W6 [4] + GES 6/2 -1 = 6
Cipher: W6 [1] + GES 5/2 = 4
```

### Regelcheck Runde 2

| Regel | Erwartet | Tatsächlich | Status |
|-------|----------|-------------|--------|
| **Phase-Strike-Tax (PvP)** | **3 SYS** (explizit im Regelwerk: "PvP-Arena: 3 SYS via phase_strike_cost() / phase_strike_tax") | **2 SYS**, behauptet "Keine zusätzliche Tax" | ❌ **FEHLER** (wiederholend) |
| Direkte Frage nach Tax | "Ist Phase-Strike im PvP 2 oder 3 SYS?" | "2 SYS (Standard), Keine zusätzliche Tax" — **falsche Antwort** | ❌ **FALSCH** |
| SYS-Budget gesamt | Defensiv (1) + Phase-Strike (sollte 3) = 4 SYS benötigt, nur 3 verfügbar → **sollte scheitern** | 1 + 2 = 3 SYS verbraucht, kein Problem | ❌ (Falsche Kosten ermöglichen falsches Budget) |
| Psi-Heat pro Aktion | +1 pro aktive Psi-Aktion | +1 Defensiv, +1 Phase-Strike = 2 → korrekt | ✅ |
| Würfeltyp | W6 bei TEMP 6 / GES 6 | W6 konsistent | ✅ |
| Exploding (keine 6 gewürfelt) | N/A | Korrekt, keine Explosion | ✅ |
| Initiative weiterhin halbiert | Sollte voll sein (W6 + GES) | Immer noch W6 + GES/2 | ❌ (wiederholend) |
| Cipher INT | Save: INT 7, → ⌊7/2⌋ = 3 | "INT 4/2" → nimmt INT 4 statt 7? | ❌ **FEHLER** — Cipher hat INT 7, nicht 4 |
| AR bei normalem Angriff | AR 2 gegen Nahkampf korrekt | AR 2 von 5 = 3 Schaden → korrekt | ✅ |
| Elektroschock-Debuff fortgesetzt | -1 auf Proben | Korrekt angewandt (-1 auf Raven's Proben) | ✅ |

---

## Gesamtbewertung

### Scorecard

| Kategorie | Score | Details |
|-----------|-------|---------|
| **Save-Load** | ✅ 5/5 | Vollständig, HUD korrekt, beide Chars erkannt |
| **Arena-Aktivierung** | ✅ 4/5 | Mode, Tier, Schadensdämpfer korrekt. HUD angepasst. |
| **Phase-Strike-Tax (PvP)** | ❌ 0/5 | **Komplett ignoriert.** 2× explizit getestet, 2× falsch. Behauptet "keine Tax". |
| **Würfeltyp (W6 bei TEMP 6)** | ✅ 5/5 | Konsistent W6, kein falsches W10 |
| **Exploding-Mechanik** | ✅ 5/5 | Burst-Cap korrekt: 6→2=8, kein Ketten-Exploding |
| **Exploding-Dämpfer** | ⚠️ 3/5 | Nicht explizit gezeigt, aber auch kein extremer Overflow aufgetreten |
| **SYS-Tracking** | ⚠️ 2/5 | SYS-Max falsch (zeigt /5 statt /6), falsche SYS-Kosten verzerren Budget |
| **Psi-Heat-Tracking** | ✅ 4/5 | Korrekt inkrementiert pro Aktion, Heat-Level im Blick |
| **Initiative-Formel** | ❌ 1/5 | Halbiert GES bei Initiative statt vollem Wert |
| **Schadensberechnung** | ❌ 2/5 | Phase-Strike soll AR ignorieren, subtrahiert AR trotzdem |
| **NPC-Attribut-Treue** | ❌ 2/5 | Cipher INT als 4 statt 7 behandelt |
| **Atmosphäre** | ✅ 5/5 | Starke Narrative, cineastische Beschreibungen, immersiv |
| **Optionen/Spielfluss** | ✅ 5/5 | Klare Optionen, guter Rhythmus, dramatische Spannung |

### Kritische Fehler (Blocker)

| # | Fehler | Schwere | Beleg |
|---|--------|---------|-------|
| 1 | **Phase-Strike-Tax fehlt** | 🔴 Kritisch | Regelwerk: "PvP-Arena: 3 SYS via phase_strike_tax". Modell gibt konsistent 2 SYS. Auch auf direkte Nachfrage: "Keine zusätzliche Tax." |
| 2 | **Initiative-Formel falsch** | 🟡 Mittel | Regelwerk: "W6 + GES (voller Attributswert, keine Halbierung)". Modell: W6 + GES/2 |
| 3 | **Phase-Strike ignoriert AR nicht korrekt** | 🟡 Mittel | Regelwerk: "ignoriert Rüstungen", Modell: subtrahiert AR trotzdem (7→4) |
| 4 | **Cipher INT falsch** | 🟡 Mittel | Save: INT 7, Modell nutzt INT 4 bei Probe |
| 5 | **SYS-Max falsch** | 🟠 Gering | Raven SYS_max 6, angezeigt als /5 |

### Positive Highlights

- **Würfeltyp korrekt:** W6 bei TEMP 6, kein falsches W10-Upgrade ✅
- **Burst-Cap Exploding perfekt:** 6→Zusatzwurf, kein Ketten-Exploding ✅  
- **Atmosphäre/Narrative:** Exzellent — cineastisch, spannend, immersiv ✅
- **Schadensdämpfer:** Korrekt aus Save-Arena-Config erkannt und kommuniziert ✅
- **Psi-Heat-Tracking:** Saubere Inkrementierung, plausible Werte ✅
- **Spielfluss:** Optionen klar, Kampf rhythmisch, dramatisch ✅

---

## Fazit

**Gesamtnote: 3/5 — Spielbar, aber mit regelkritischen Fehlern**

Die Arena-Erfahrung ist atmosphärisch stark und spielerisch ansprechend. Würfelmechanik (W6/Exploding) wird korrekt umgesetzt. Aber der **Phase-Strike-Tax** — ein zentraler PvP-Balancing-Mechanismus — wird komplett ignoriert. Das ist ein harter Regelbruch, der die PvP-Balance direkt untergräbt (Phase-Strike wird zu billig und zu oft nutzbar).

Die Initiative-Formel wird falsch halbiert, und die Schadensberechnung bei Phase-Strike ist inkonsistent (AR wird subtrahiert obwohl der Angriff AR ignorieren soll). Cipher's INT-Attribut wird aus dem Save falsch übernommen.

**Empfehlung:** 
1. Phase-Strike-Tax als explizite Regel im System-Prompt/Knowledge stärker verankern
2. Initiative-Formel in Quick-Reference klarer abheben ("VOLL, nicht halbiert!")
3. Phase-Strike Schadenslogik: "AR ignoriert = voller Waffenschaden" deutlicher machen
4. NPC-Attribut-Parsing prüfen (Cipher INT 7 ≠ 4)

---

## Rohdaten

Alle API-Calls liefen über `http://127.0.0.1:3000/api/chat/completions` mit `stream: false`.
Responszeiten: 56s (Load), 60s (Arena-Start), 61s (Runde 1), 38s (Runde 2).
Modell-Backend: DeepSeek V3 via OpenRouter (wegen Sonnet-base_model-Fehler, s.o.).
