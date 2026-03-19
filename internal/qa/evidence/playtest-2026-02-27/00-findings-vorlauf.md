# Playtest-Findings Vorlauf — 2026-02-27

Aus den ersten 4 Playtest-Runs (jeweils Timeout nach 10 Min, aber mit Erkenntnissen).

---

## Issue 1: W10 bei TEMP 6 (Arena, bestätigt 2×)

**Schwere:** 🔴 Regelverstoß  
**Wo:** Arena PvP, Psi-Proben  
**Problem:** SL würfelt W10 für TEMP 6. Laut Regelwerk wechselt der Würfel erst ab **Attribut 11** auf W10. TEMP 6 = W6.  
**Ursache:** Die SL verwechselt vermutlich TEMP mit dem Attributswert-Threshold. Im Masterprompt steht "ab 11 → W10", aber die SL wendet es auf TEMP als Sonderwert an.  
**Betroffene Stellen im Regelwerk:**

- `core/wuerfelmechanik.md`: "Ab Attribut 11 wechselt der Würfel auf W10"
- `meta/masterprompt_v6.md` Abschnitt E: "ab Attr 11 W10"
  **Fix-Vorschlag:** Im Masterprompt expliziter machen: "W10 ab Attribut ≥ 11 (gilt für STR/GES/INT/CHA/TEMP/SYS gleichermaßen — TEMP 6 = W6, TEMP 11 = W10)"

---

## Issue 2: Phase-Strike Cooldown zwischen Arena-Runden

**Schwere:** 🟡 Regelunklar  
**Wo:** Arena PvP, Rundenwechsel  
**Problem:** Phase-Strike Cooldown aus Runde 1 wird in Runde 2 nicht zurückgesetzt. Laut Regeln werden "LP, Munition und anhaltende Effekte vollständig zurückgesetzt" zwischen Runden.  
**Frage:** Ist Phase-Strike-Cooldown ein "anhaltender Effekt"? Wenn ja → Reset. Wenn nein → dokumentieren.  
**Betroffene Stelle:** `gameplay/kampagnenstruktur.md` Arena-Abschnitt  
**Fix-Vorschlag:** Explizit in die Arena-Reset-Regel aufnehmen: "Zwischen Runden: LP, SYS, PP, Cooldowns, Munition → voll zurückgesetzt."

---

## Issue 3: SYS-Verbrauch bei Psi nicht konsistent getrackt

**Schwere:** 🟡 Immersions-Issue  
**Wo:** Arena PvP + Rift-Ops  
**Problem:** Psi-Abilities verbrauchen SYS (laut kp-kraefte-psi.md), aber die SL trackt den SYS-Verbrauch nicht im HUD. Der Spieler sieht nicht, wieviel SYS noch frei ist.  
**Fix-Vorschlag:** HUD-Zeile sollte SYS-Runtime anzeigen wenn Psi aktiv. Bereits im HUD-System definiert, aber SL ignoriert es.

---

## Issue 4: Episodenboss — Phase-Gate funktioniert ✅

**Schwere:** 🟢 Positiv  
**Wo:** Episodenboss-Playtest  
**Ergebnis:** Die SL hat korrekt "Phase-Desync" erkannt als der Spieler Kampfbefehle in der HQ-Phase geschickt hat. Das Gate funktioniert.

---

## Empfohlene Fixes (nach Priorität)

1. **W10-Threshold klarer machen** im Masterprompt (1 Satz)
2. **Arena-Reset-Regel** explizit erweitern (Cooldowns inkludieren)
3. **SYS-Runtime im HUD** — eher Wissensspeicher-Optimierung als Code-Fix
