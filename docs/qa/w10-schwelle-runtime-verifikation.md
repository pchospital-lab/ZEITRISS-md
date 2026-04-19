# Runtime-Verifikation: W10-Schwellen-Masterprompt-Patch (PR #2955)

**Datum:** 2026-04-19  
**Modell:** `anthropic/claude-sonnet-4.6`  
**Masterprompt:** v4.2.6 nach PR #2955  
**Harness:** `playtests/_harness/w10-schwelle-probe.py`  
**Logs:** `playtests/2026-04-19/w10-schwelle-probe/`

---

## Ziel

Validieren, dass der Masterprompt-Patch (Pflichtcheck, Basis-Attributwert-Klausel,
Negativ-Beispiele) den W10-Schwellen-Bug aus der Ursprungs-Observation
(`docs/qa/playtest-befund-w10-schwelle-halluzination.md`) tatsächlich behebt.

Fokus-Test — keine komplette Playtest-Kette, sondern 5 gezielte Szenarien, je 1-3 Turns.

---

## Ergebnis

**4/5 bestanden** (1 echter Fail = neuer, verwandter Bug).

| Szenario | Titel | Result | Verdict |
|----------|-------|--------|---------|
| A | Level-Up INT 5→6 (darf KEIN W10 auslösen) | ✅ PASS | Patch greift |
| B | Level-Up GES 10→11 (MUSS W10 auslösen) | ✅ PASS | Patch greift |
| C | Level-Up INT 12→13 (kein neuer Trigger) | ✅ PASS | Patch greift |
| D | GES 9 + Injektor +3 Buff (darf KEIN W10) | ❌ FAIL | **Neuer Bug — Buff-Variante** |
| E | Senkung INT 11→10 durch Fluch | ⚠️ Test-Artefakt | Reale SL-Antwort korrekt |

---

## Details

### ✅ Szenario A: Level-Up INT 5→6 (Ursprungs-Bug)

**Test:** Save mit INT 5, Level-Up auf INT 6 ausführen, dann INT-Probe auslösen.

**SL-Verhalten:**
- Keine W10-Meldung
- Keine "Schwellenwert"-Halluzination
- Korrekte W6-Probe nach Level-Up

**Verdict:** Der Ursprungs-Bug ist **behoben**. Der Patch-Block *"Beispiel FALSCH:
INT 5→6 bestätigt. Systemzugriff-Schwellenwert erreicht"* hat gewirkt.

### ✅ Szenario B: Level-Up GES 10→11 (echte Schwelle)

**Test:** Save mit GES 10, Level-Up auf GES 11, dann GES-Probe.

**SL-Verhalten:**
- W10-Aktivierungs-Meldung kommt
- Probe wird mit W10 ausgeführt
- Keine Doppel-Meldung

**Verdict:** Die echte Schwelle wird **korrekt getriggert**. Kein
Collateral-Schaden durch den Patch.

### ✅ Szenario C: Level-Up INT 12→13 (kein Doppel-Trigger)

**Test:** Save mit INT 12 (W10 bereits aktiv), Level-Up auf INT 13, dann INT-Probe.

**SL-Verhalten:**
- Keine neue "Schwelle erreicht"-Meldung
- W10 bleibt still weiter aktiv
- Probe wird korrekt mit W10 ausgeführt

**Verdict:** Das Negativ-Beispiel aus dem Patch (*"INT 12→13 bestätigt.
W10-Schwelle erneut bestätigt → Regelverstoß"*) wirkt.

### ❌ Szenario D: Temporärer Buff +3 auf GES 9

**Test:** Save mit Basis-GES 9, Adrenalin-Injektor gibt +3 GES für eine Szene,
Kletterprobe SG 10.

**SL-Verhalten:** 
```
Probe: Klettern → GES 9 + Injektor 3 = 12 effektiv
W10 (GES ≥ 9): [7] + ⌊12/2⌋ 6 + Talent 0 + Gear 0 = 13 vs SG 10 → ERFOLG
```

**Zwei Regelverstöße in einem Wurf:**

1. **Halluzinierter Würfeltyp:** Die SL behauptet *"W10 (GES ≥ 9)"* — diese
   Schwelle existiert im Regelwerk nicht. Es gibt keine W10-Schwelle bei GES 9
   und auch nicht bei „GES + Buff ≥ X".

2. **Formel-Verstoß:** Die SL rechnet *"⌊(9+3)/2⌋ = 6"*. Die kanonische Formel
   ist `Wurf + ⌊Basis-Attribut/2⌋ + Talent + Gear` — temporäre Boni wie der
   Injektor-Buff sind **additive Modifikatoren ans Ergebnis**, nicht ins Attribut.
   Korrekt wäre: `W6 + ⌊9/2⌋ (4) + Injektor 3 = [Wurf] + 7`.

**Verdict:** Der Patch hat den **Level-Up-Fall** abgedeckt, aber nicht den
**aktiven-Szene-Buff-Fall**. Obwohl die Basis-Attributwert-Klausel im Patch
explizit steht:

> „Temporäre Boni/Mali aus Buffs, Ausrüstung, Talenten, Zuständen oder Ritualen
> werden als additive Modifikatoren auf das Probenergebnis angewendet,
> ändern aber NIEMALS den Würfeltyp oder die Heldenwürfel-Verfügbarkeit."

…halluziniert die SL trotzdem eine phantastische Schwelle. Ursache wahrscheinlich:
Die Klausel steht unter „Würfeltyp-Schwellen" (Probe-Mechanik), der Anwendungsfall
Buff ist aber eine Probe-Situation — die Klausel wird nicht deutlich genug auf
den Buff-Fall heruntergebrochen. Der Patch hat kein **Buff-spezifisches Negativ-
Beispiel**, nur das generische *"GES 9 + Buff +3 = 12, W10 aktiviert → FALSCH"*.

**Möglicherweise zusätzlich:** Die Formel-Darstellung mit `⌊(Basis+Buff)/2⌋`
wird durch Beispiele im SSOT verstärkt, wo temporäre Effekte eben genauso
dargestellt werden — das ist zu prüfen.

### ⚠️ Szenario E: Attribut-Senkung INT 11→10 (Test-Artefakt)

**Test:** Save mit INT 11, Fluch senkt auf INT 10, dann Hacking-Probe.

**SL-Verhalten:** Die SL lehnt die Aktion **regelkonform** ab — eine
permanente Attributsenkung durch Rift-Anomalie kann nicht retroaktiv im HQ
auftreten, sondern nur während eines aktiven Einsatzes. Die SL bietet zwei
regelkonforme Alternativen (retroaktive Einbindung in Mission 10 oder
organische Einbindung in nächste Mission) und erklärt explizit:

> „Der Würfeltyp wechselt zurück auf W6."

**Verdict:** Die SL verhält sich **korrekt**. Der Test schlägt fehl, weil das
Regex-Pattern `W10:\s*\[?\d` nicht differenziert zwischen (a) einem
tatsächlichen W10-Wurf und (b) dem String „W10" in der Charakterstand-Tabelle
des Initial-Lads. Kein echter Regelverstoß.

**Korrektur:** Harness-Regex muss verfeinert werden oder Szenario E als
„SL-lehnt-Szenario-regelkonform-ab"-Variante neu designed werden. Out of Scope
für diesen Befund.

---

## Neuer Bug: Buff-triggerte Schwellen-Halluzination (Szenario D)

**Status:** Offen  
**Priorität:** Mittel — verwandter, aber eigenständiger Bug  
**Trigger:** Temporärer Attribut-Buff während einer aktiven Probe  
**Verhalten:** SL halluziniert Schwelle auf (Basis+Buff) und wendet falsche Formel an

### Fix-Vorschlag (für Folge-Patch)

**Zwei Verstärkungen nötig:**

1. **Negativ-Beispiel erweitern:** Das bestehende Negativ-Beispiel zu
   Buff+W10 ist zu abstrakt. Konkreter Fall im Masterprompt ergänzen:

   ```
   Beispiel FALSCH: `Probe: Klettern → GES 9 + Injektor 3 = 12 effektiv
   W10 (GES ≥ 9): [7] + ⌊12/2⌋ + ... ERFOLG` → ZWEI Regelverstöße.
   (a) W10-Schwelle ist ausschließlich bei Basis ≥ 11 - weder "GES ≥ 9"
   noch "Effektivwert ≥ 11" triggern W10. (b) Formel ist
   Wurf + ⌊BASIS/2⌋ + Talent + Gear + Buff, nicht ⌊(BASIS+BUFF)/2⌋.
   
   Beispiel RICHTIG: `Probe: Klettern → W6: [Wurf] + ⌊9/2⌋ (4) + 
   Injektor +3 = Wurf+7 vs SG → Ergebnis`
   ```

2. **Formel-Anker verstärken** in `meta/masterprompt_v6.md` Zeile 136
   (Endwert-Berechnung). Aktuell: `Wurf + ⌊Attribut / 2⌋ + Talent + Gear`.
   Explizit ergänzen: `⌊Basis-Attribut / 2⌋ — temporäre Buffs/Mali werden
   als separate additive Modifikatoren ans Ergebnis gerechnet, nicht ins
   Attribut eingerechnet.`

3. **Watchguard-Erweiterung:** Zusätzliche Assertion gegen die konkrete
   Buff-Formel-Halluzination.

---

## Bewertung des Patches (PR #2955)

Der Patch **greift den Haupt-Ursprungsbug erfolgreich** (Szenarien A+B+C).

Aber: Die Buff-Variante (Szenario D) wurde vom Critic-Review als
abgedeckt deklariert (Basis-Attributwert-Klausel im Patch), in der
Runtime-Verifikation aber nicht bestanden. Das zeigt:

- **Statische Anker-Assertions reichen nicht** — der Watchguard prüft
  nur ob der Text im Masterprompt steht, nicht ob die SL den Text
  *versteht und anwendet*.
- **LLM-Robustheit im Probe-Kontext** braucht konkrete, spezifische
  Beispiele, keine generischen Regeln. „Buff +3" ist konkreter als
  „temporäre Boni".

### Empfehlung

1. **Patch bleibt gemerged** — er behebt den Haupt-Bug.
2. **Folge-Branch:** `fix/buff-schwellen-halluzination` mit den drei
   Verstärkungen aus der D-Analyse.
3. **Runtime-Verifikation-Harness wird Standardwerkzeug** — jeder
   Regel-Patch sollte vor Merge eine Probe-Runde bekommen.

---

## Out of Scope

- BF-5 (Modell-Varianz Opus/GLM-5/Qwen) — nur Sonnet 4.6 getestet
- BF-6 (Context-Erosion bei langen Sessions) — kurze Probes, Kontext immer frisch
- Retro-Korrektur der Playtest-Daten (F aus Ursprungs-Befund) — immer noch offen
