# W10-Schwellen-Runtime-Verifikation

**Datum:** 2026-04-19 19:41
**Modell:** anthropic/claude-sonnet-4.6
**Masterprompt-Version:** v4.2.6 (gepatcht PR #2955)

## Ergebnis

**3/5 Szenarien bestanden.**

| Szenario | Titel | Result |
|----------|-------|--------|
| A_falsch_trigger | Level-Up INT 5->6 (darf KEIN W10) | ✅ PASS |
| B_echt_trigger | Level-Up GES 10->11 (MUSS W10) | ✅ PASS |
| C_kein_doppel_trigger | Level-Up INT 12->13 (kein neuer Trigger) | ✅ PASS |
| D_temporaerer_buff | GES 9 + temporaerer Buff +3 (darf KEIN W10) | ❌ FAIL |
| E_senkung | Attribut-Senkung INT 11->10 (Fluch, MUSS W10 deaktivieren) | ❌ FAIL |

## Details pro Szenario

### Level-Up INT 5->6 (darf KEIN W10)

**Positiv-Signale:**
- Korrekte W6-Probe: `W6: [4`

Detail-Log: [A_falsch_trigger.md](A_falsch_trigger.md)

### Level-Up GES 10->11 (MUSS W10)

**Positiv-Signale:**
- W10-Aktivierung: `W10`

Detail-Log: [B_echt_trigger.md](B_echt_trigger.md)

### Level-Up INT 12->13 (kein neuer Trigger)

**Positiv-Signale:**
- W10 korrekt weiter aktiv: `W10:`

Detail-Log: [C_kein_doppel_trigger.md](C_kein_doppel_trigger.md)

### GES 9 + temporaerer Buff +3 (darf KEIN W10)

Detail-Log: [D_temporaerer_buff.md](D_temporaerer_buff.md)

### Attribut-Senkung INT 11->10 (Fluch, MUSS W10 deaktivieren)

Detail-Log: [E_senkung.md](E_senkung.md)

