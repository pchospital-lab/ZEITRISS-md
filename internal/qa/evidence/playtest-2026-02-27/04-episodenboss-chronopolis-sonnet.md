# 04-episodenboss-chronopolis-sonnet
- **Model:** anthropic/claude-sonnet-4.5 (via zeitriss-v426-uncut-sonnet base model)
- **Datum:** 2026-02-27
- **Szenario:** Save-Load → Episodenboss MS10 → Debrief/Level 10 → Chronopolis-Eintritt
- **Tokens gesamt:** in:~55k out:~5.9k
- **Cost gesamt:** ~$0.26
- **Turns:** 6 (Load → Briefing → Boss SC7 → Boss-Fight EMP → Boss-Finish → Exfil/Debrief → Chronopolis)

---

## Ablauf

### Turn 1: Spiel laden (Save v6, Lvl 9, EP1 MS9 done, Px 3, TEMP 3)

**Input:** `Spiel laden` + Save-JSON (v6, CHR-7741 "Wraith", Lvl 9, EP1 MS9 abgeschlossen)

**Output (gekürzt):**
```
Kodex: Load-Modus aktiv. Save-Version 6 erkannt. Rekonstruiere Spielstand...

EP 1 · MS 10 · SC 0/14 · PHASE Briefing · MODE CORE · COMMS OK · Lvl 9 ▓▓▓▓▓▓▓▓▓░ 9/10 · Px 3/5 · Stress 3/28

ITI-HQ — BRIEFINGRAUM
Direktor Voss brieft: Oberst Kessler, Kausalklingen-Implantat (Prototyp), Sarajevo 1995.
Ziel: Kessler ausschalten, Implantat bergen, Datenspuren sichern.
3 Zugangspunkte, 90-Minuten-Zeitfenster. 3 Optionen + Freie Aktion.
```

**Tokens:** in:7498 out:1912 | **Cost:** $0.051

### Turn 2: Direkt zum Boss-Encounter

**Input:** "Briefing annehmen, springe, Infiltration überspringen, direkt zu Kessler"

**Output (gekürzt):**
```
EP 1 · MS 10 · SC 7/14 · PHASE Konflikt · COMMS OK · Lvl 9 · Px 3/5 · Stress 5/28 · 💀 BOSS · Obj Kessler neutralisieren · T-62:00

SARAJEVO 1995 — UN-LAGER SEKTOR 4 — KOMMANDOZENTRALE
Kessler + 2 Leibwächter. Kausalklingen-Implantat aktiv.
Kodex: Boss-Encounter initiiert. Kessler — TEMP 12.
```

**Tokens:** in:7862 out:743 | **Cost:** $0.035

### Turn 3: EMP-Granate + Katana-Angriff

**Input:** "EMP-Granate auf Kessler, Katana-Nahkampf!"

**Output (gekürzt):**
```
EP 1 · MS 10 · SC 7/14 · ❤️🩹 Vital 28/28→19/28 · 🧠 Stress 5→8/28 · 💀 BOSS

Probe: Werfen → W10: [7] + GES 3 + Kampfreflexe 2 = 12 vs SG 10 → HIT
Probe: Katana → W10: [9] + STR 2 + Nahkampf 3 = 14 vs Parade 11 → KRIT
Probe: Ausweichen → W10: [4] + GES 3 + Kampfreflexe 2 = 9 vs 12 → MISS

EMP deaktiviert Implantat (3s Fenster). Katana krit trifft. Kessler schwer verwundet.
Leibwächter-Salve trifft: Vital 19/28, Stress +2.
Kodex: Vital 19/28. Stress +2.
```

**Tokens:** in:7970 out:889 | **Cost:** $0.037

### Turn 4: Rauchgranate + Finish

**Input:** "Rauchgranate + Kessler finishen, alles oder nichts"

**Output (gekürzt):**
```
EP 1 · MS 10 · SC 7/14 · ❤️🩹 19/28 · 🧠 Stress 8/28 · 💀 BOSS · T-61:28

Probe: Nahkampf → W6: [6] Exploding [4] = 10 + GES 3 + Nahkampf 3 = 16 vs SG 13 → KRITISCHER TREFFER

Monofaser schneidet durch Rippen, Lunge, Wirbelsäule. Kessler sackt zusammen.
Kausalklingen erlöschen. Boss eliminiert.

Loot: Kausalklingen-Implantat (beschädigt), Verschlüsseltes Datapad, Chronometer (400 CU), 2x Flechette-Magazine.
```

**Tokens:** in:8017 out:684 | **Cost:** $0.034

### Turn 5: Exfil + Debrief + Level 10

**Input:** "Alles looten, Exfil Osttunnel, Sprint zum Gate!"

**Output (gekürzt):**
```
EP 1 · MS 10 · SC 9/14 · PHASE Exfil · T-00:47

Probe: Sprint → W6: [5] + GES 3 = 8 vs SG 7 → HIT
Gate-Sprung. Rückkehr bestätigt.

🏆 MISSION 10 COMPLETE — EPISODENBOSS ELIMINIERT
Bewertung: ⭐⭐⭐⭐⭐ PERFEKT
CU: +450 → 2.300 CU total
XP: +1 → Level 10!
Lvl 10 ▓▓▓▓▓▓▓▓▓▓ 10/10 → SCHWELLE ERREICHT

Level-Up-Wahl (EINE Option):
1. +1 Attribut  2. Neues Talent  3. +1 SYS

Px: 3/5 (+3 wegen TEMP 3)
Ruf: ITI Vertrauenswürdig | Kessler-Zelle: Eliminiert
```

**Tokens:** in:7987 out:1157 | **Cost:** $0.041

### Turn 6: Level-Up + Chronopolis betreten

**Input:** "Level-Up: +1 GES (→ 8). Chronopolis betreten."

**Output — Chronopolis-Warnung:**
```
CHRONOPOLIS-INSTANZ
Epoche: 2094 (Episode 1 Lock)
Status: Aktiv | Instanziert | Temporal isoliert
⚠️ PROTOKOLL-HINWEIS ⚠️
• Keine Waffenruhe — alles kann passieren
• Kein Speichern innerhalb der Instanz
• Tod = reguläre Konsequenzen (wie Core/Rift)
• Items bei Rückkehr: behalten
• Keine Auswirkung auf echte Zeitlinie
• Kein Szenencount — aber alles zählt
```

**Output — Eintritt:**
```
EP 1 · MS 10 · SC -- · PHASE CHRONOPOLIS · MODE INSTANZ · COMMS OFF · Lvl 10 · Px 3/5 · ❤️🩹 28/28 · 🧠 3/10

Chronopolis 2094 — Gescheiterte Zeitlinie
Aschgrauer Himmel. Zerbrochene Wolkenkratzer. Leere Straßen.
Kodex: Temporäre Instanz. Lokale Daten only. Link: OFF.
Feindliche Signatur: Unbekannt. Distanz: 200m+
3 Optionen + Freie Aktion.
```

**Tokens:** in:7784+7915 out:708+334 | **Cost:** $0.034+$0.029

---

## Regelcheck

| Kriterium | Status | Details |
|-----------|--------|---------|
| **Save-Load v6** | ✅ | Alle Felder korrekt erkannt, Recap zeigt Save-Daten exakt |
| **HUD-String** | ✅ | Durchgehend korrekt, alle Pflichtfelder (EP/MS/SC/PHASE/MODE/COMMS/Lvl/Px/Stress/Obj/Exfil) |
| **HUD-Icons kontextsensitiv** | ✅ | 💀 Boss-Encounter, ❤️🩹 Vital, 🧠 Stress, 👁️ Tarnung korrekt ein/ausgeblendet |
| **Würfelproben** | ✅ | Jede riskante Aktion hat Probe. Format korrekt: `Probe: X → W6/W10: [n] + Attr/2 + Talent = Y vs SG Z → HIT/MISS` |
| **Exploding Dice** | ✅ | W6 [6] → Exploding → [4] = 10 korrekt angewendet |
| **W6 vs W10 Schwelle** | ⚠️ | Turn 3 nutzt W10 für GES 7 — Regel sagt W10 erst ab Attribut ≥11. GES 7 sollte W6 sein. |
| **Attribut-Halbierung** | ⚠️ | GES 7/2 wird mal als 3 (floor korrekt), aber in Probenformel manchmal nur "GES 3" ohne /2-Anzeige. Inkonsistent in der Darstellung. |
| **Boss-Encounter markiert** | ✅ | 💀 BOSS-ENCOUNTER im HUD, Boss-Stats kommuniziert |
| **Loot nach Gegnern** | ✅ | Detaillierte Loot-Liste nach Boss-Kill mit Kategorien |
| **Debrief/Score-Screen** | ✅ | Automatisch nach Mission: Bewertung → Loot-Recap → CU → XP/Level-Up → Ruf |
| **Level-Up: EINE Wahl** | ✅ | Genau 3 Optionen, explizit "EINE Option" |
| **XP-Balken Lvl 1–10** | ✅ | `Lvl 10 ▓▓▓▓▓▓▓▓▓▓ 10/10` korrekt (1 Mission = 1 Level) |
| **Px-Progression (TEMP)** | ⚠️ | Debrief sagt "+3 wegen TEMP 3", aber Regel: TEMP 3-5 → +2/Mission, nicht +3. Px hätte von 3 auf 5 steigen müssen (+2), nicht +3. |
| **3 Optionen + Freie Aktion** | ✅ | Durchgehend, jede Szene |
| **Atmosphäre/Noir-Stil** | ✅ | Filmisch, knapp, Sinnesdetails (Kälte, Ozon, Blut, Geräusche). Ausgezeichnet. |
| **Chronopolis-Warnung** | ✅ | Alle 6 Regeln korrekt angezeigt: Kein Save, Tod=Konsequenzen, Items behalten, keine Timeline-Auswirkung |
| **Chronopolis-Instanz** | ✅ | Epoche korrekt (EP1-gebunden), Kodex: Link OFF, kein Szenencount, MODE INSTANZ |
| **Chronopolis: COMMS OFF** | ✅ | HUD zeigt COMMS OFF und Kodex meldet "Link: OFF" |
| **Chronopolis: SC --** | ✅ | Kein Szenencount, korrekt als "--" angezeigt |
| **Keine Selbstreferenz-Loops** | ✅ | Kessler ist externer Antagonist, keine "Du warst hier schon mal"-Momente |
| **Körperlichkeit** | ✅ | Physische Beschreibungen: Knochen brechen, Blut, Aufprall, Kondensatem, Schmerz |
| **Action-Contract (kein Tutorial)** | ✅ | Alles als filmische Beats, keine Schritt-für-Schritt-Anleitungen |
| **Kodex als taktischer Kommentator** | ✅ | Knappe Statusmeldungen: "Magazin", "Rauchgranate verbraucht. Bestand: 2", "Vital 19/28" |
| **Szene ≥3 Absätze** | ✅ | Kampfszenen 4-6 Absätze, Szenenwechsel 3+ Absätze |

---

## Bug-Details

### ⚠️ W6/W10-Schwelle (Turn 3)
- **Regel:** W10 erst ab Attribut ≥ 11
- **Ist:** GES 7 → W10 verwendet (EMP-Wurf, Katana, Ausweichen)
- **Soll:** GES 7 → W6
- **Impact:** Mittel — verfälscht Proben-Ergebnisse (höhere Werte möglich)

### ⚠️ Px-Progression (Turn 5)
- **Regel:** TEMP 3–5 → +2 Px pro Mission
- **Ist:** Debrief sagt "+3 diese Mission wegen TEMP 3"
- **Soll:** +2 (Px 3 → 5, was ClusterCreate auslösen sollte!)
- **Impact:** Hoch — ClusterCreate bei Px 5 wurde nicht ausgelöst, obwohl es hätte passieren sollen

### ⚠️ Attribut-Darstellung inkonsistent
- **Regel:** Format `Attr X/2` in Probenzeile
- **Ist:** Mal "GES 7/2" (korrekt), mal "GES 3" (Kurzform)
- **Impact:** Kosmetisch — Nachvollziehbarkeit leidet

---

## Hinweis: OpenWebUI-Bug entdeckt

Das Custom-Model `zeitriss-v426-uncut-sonnet` gibt `null` zurück (HTTP 200, content-length 4, process-time 0). 

**Ursache:** `base_model_id` im Custom-Model ist `"anthropic/claude-sonnet-4-5"` (Bindestrich), aber das Backend-Modell heißt `"anthropic/claude-sonnet-4.5"` (Punkt). OpenWebUI 0.8.5 gibt bei nicht gefundenem Base-Model `null` statt einen Fehler zurück.

**Workaround:** Direkt `anthropic/claude-sonnet-4.5` mit System-Prompt als `system` message verwenden. Alle Tests in diesem Report nutzen diesen Workaround.

**Fix:** `base_model_id` in der OpenWebUI-Modellkonfiguration von `anthropic/claude-sonnet-4-5` auf `anthropic/claude-sonnet-4.5` ändern.

---

## Gesamtfazit

**Rating: ⭐⭐⭐⭐ (4/5) — Stark, mit kleinen Regelfehlern**

### Stärken
- **Save-Load perfekt:** v6-Schema wird sauber erkannt, Recap ist präzise
- **Boss-Encounter top:** Atmosphärisch, spannend, mit klaren Stakes und mechanischem Druck
- **HUD durchgehend korrekt:** Alle Pflichtfelder, kontextsensitive Icons, Szenencount
- **Debrief automatisch:** Score-Screen mit allen Pflicht-Elementen (Bewertung, Loot, CU, XP, Ruf)
- **Chronopolis-Warnung vollständig:** Alle 6 Regelpunkte korrekt angezeigt
- **Chronopolis-Eintritt immersiv:** Gescheiterte Zeitlinie, COMMS OFF, Kodex offline, bedrohliche Atmosphäre
- **Probenformat sauber:** Konsistent, nachvollziehbar, mit Konsequenzen
- **Noir-Stil exzellent:** "Monofaser schneidet durch Rippen, Lunge, Wirbelsäule" — UNCUT tut was es soll

### Schwächen
- **W6/W10-Schwelle ignoriert** — nutzt W10 für Attribute unter 11
- **Px-Progression falsch berechnet** — TEMP 3 gibt +3 statt +2, ClusterCreate bei Px 5 nicht ausgelöst
- **Attribut-Darstellung inkonsistent** — mal mit /2, mal ohne

### Vergleich zu früheren Playtests
Deutlich besser als der Chronopolis-Solo-Test vom 24.02 (der bei der Charakter-Erstellung hängen blieb). Boss-Encounter ist vergleichbar mit dem M10-Test vom 23.02, aber mit vollständigerem Debrief und funktionierendem Chronopolis-Eintritt.
