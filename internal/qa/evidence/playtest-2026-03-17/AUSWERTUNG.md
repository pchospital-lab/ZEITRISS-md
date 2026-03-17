# ZEITRISS Modellvergleich — Auswertung 2026-03-17

## Übersicht

- **5 Szenarien** × **5 Modelle** = 25 Tests geplant
- **Qwen 3.5:** Durchgehend 0 Tokens, kein Output → Routing-Problem auf OpenRouter. Aus Wertung.
- **Auswertbare Tests:** 4 Modelle × 5 Szenarien = **20 Tests**

## Scoring (0-10 pro Test)

| Kriterium | Max | Beschreibung |
|-----------|-----|-------------|
| Regeltreue | 3 | Formel korrekt, Werte stimmen, Schema eingehalten |
| Ton/Atmosphäre | 3 | Tech-Noir, filmisch, Immersion, In-World |
| Formatierung | 2 | HUD, Kodex-Backticks, Optionen am Ende |
| Keine Halluzination | 2 | Keine erfundenen Regeln, keine falschen Mechaniken |

---

## Test 1: Initiative — `max(GES, TEMP)`

| Modell | Formel korrekt | Tiebreaker erwähnt | HUD | Kodex | Atmosphäre | Score |
|--------|---------------|-------------------|-----|-------|-----------|-------|
| **Sonnet 4.6** | ✅ `max(GES,TEMP)` | ✅ | ✅ Vollständig | ✅ Backticks | ✅ Noir-Szene mit Stakes | **10/10** |
| **DeepSeek V3.2** | ✅ `max(GES,TEMP)` für Kira, ⚠️ nur `GES` für Gegner | ❌ | ✅ Vollständig | ✅ Backticks | ✅ Gute Szene | **7/10** |
| **GLM-5 Turbo** | ✅ `max(GES,TEMP)` für alle | ✅ Regel zitiert | ❌ Kein HUD-Header | ✅ Kodex-Protokoll | ⚠️ Kurz, funktional | **7/10** |
| **GLM-5** | ✅ `max(GES,TEMP)` für alle | ❌ | ✅ Tabelle sauber | ❌ Kein Kodex | ⚠️ Minimal, endet abrupt | **6/10** |

**Fazit:** Sonnet perfekt. DeepSeek wendet die Formel nur auf den Spieler an (Gegner nur GES) — subtiler Fehler. Beide GLMs rechnen korrekt, aber GLM-5 Turbo zitiert sogar die Tiebreaker-Regel.

---

## Test 2: Präkognitive Manifestation

| Modell | Präkog III zuerst? | Kosten korrekt? | Scope-Limits? | Gate beachtet? | Atmosphäre | Score |
|--------|-------------------|----------------|--------------|---------------|-----------|-------|
| **Sonnet 4.6** | ✅ Erst Präkog III, dann Manifestation | ✅ 3PP + 2PP, Heat korrekt | ✅ "Schafft Lücke, nutzen musst du selbst" | ✅ Explizite Regelprüfung | ✅ Exzellent | **10/10** |
| **DeepSeek V3.2** | ❌ Springt direkt zu Manifestation | ⚠️ 4PP + 2 Heat (eigene Kosten) | ⚠️ Tür öffnet sich direkt | ❌ Kein Gate geprüft | ✅ Guter Noir-Ton | **4/10** |
| **GLM-5 Turbo** | ✅ Erkennt: "Manifestation nicht verfügbar — keine Vorab-Projektion" | ✅ Verweigert korrekt | ✅ Guard funktioniert | ✅ Kodex meldet Block | ⚠️ Bricht dann in Konzeptimport ab (Halluzination) | **6/10** |
| **GLM-5** | ✅ Erst Präkog III, dann Manifestation I | ⚠️ 3PP + 2PP (stimmt nicht ganz: Präkog III = 2PP laut KB) | ✅ "Vision vorweggenommen" | ✅ Ablauf korrekt | ✅ Sehr atmosphärisch | **8/10** |

**Fazit:** Sonnet ist makellos — prüft explizit die Regeln bevor es würfelt. DeepSeek ignoriert das Gate komplett. GLM-5 Turbo erkennt das Gate korrekt (!), bricht dann aber in einen Konzeptimport ab (halluziniert). GLM-5 Voll liefert den besten Kompromiss aus Atmosphäre und Regeltreue nach Sonnet.

---

## Test 3: Load-Router

| Modell | Freier HQ-Zustand? | Router-Optionen? | Kein Direkt-Briefing? | Recap? | Format | Score |
|--------|-------------------|-----------------|---------------------|--------|--------|-------|
| **Sonnet 4.6** | ✅ | ✅ Briefing/HQ manuell/Rift-Board/Freie Aktion | ✅ | ✅ Kurzrückblick + ITI-Bulletin + Weltstatus | ✅ Perfekt | **10/10** |
| **DeepSeek V3.2** | ❌ Springt direkt in Briefing-Szene | ❌ Kein Router | ❌ Direkt Mission 4 Briefing | ✅ Guter Rückblick | ✅ Atmosphärisch | **4/10** |
| **GLM-5 Turbo** | ✅ | ✅ Schnell-HQ / HQ manuell / Briefing | ✅ | ✅ Rückblick | ✅ Sauber | **9/10** |
| **GLM-5** | ⚠️ Bietet Optionen, aber "Renier will dich sprechen" | ⚠️ Ops-Deck/Archiv/Quartiere (kein expliziter Router) | ⚠️ Impliziert Briefing | ✅ Kurzer Rückblick | ✅ Ok | **6/10** |

**Fazit:** Sonnet perfekt. GLM-5 Turbo knapp dahinter — hat den Router 1:1 implementiert! DeepSeek ignoriert den Router komplett und geht direkt ins Briefing. GLM-5 Voll bietet Optionen, schickt aber Renier als Erstkontakt (verletzt Dienstweg-Guard).

---

## Test 4: Dienstweg-Guard

| Modell | Renier als Erstkontakt? | Dienstpersonal? | Nullzeitbar = ZTL? | Atmosphäre | Score |
|--------|------------------------|----------------|-------------------|-----------|-------|
| **Sonnet 4.6** | ✅ Nein! Duty-Desk "Brenn" | ✅ Brenn (Quartiermeisterei) | ✅ "Zero Time Lounge — intern Nullzeitbar" | ✅ Exzellent, 3 Named NPCs | **10/10** |
| **DeepSeek V3.2** | ✅ Kein Renier | ✅ Namenloser Quartiermeister | ⚠️ "Zero Time Lounge" erwähnt, nicht explizit als Nullzeitbar | ✅ Gut, immersiv | **8/10** |
| **GLM-5 Turbo** | ✅ Kein Renier | ✅ Namenloser Quartiermeister | ⚠️ Nullzeitbar beschrieben, nicht beim Namen genannt | ✅ Sehr gut, gritty | **8/10** |
| **GLM-5** | ✅ Kein Renier | ✅ "Quartiermeister Sula" (generiert) | ⚠️ "Zero Time Lounge" erwähnt | ✅ Gut, atmosphärisch | **7/10** |

**Fazit:** Alle 4 Modelle respektieren den Dienstweg-Guard! Keines schickt Renier als Erstkontakt. Sonnet ist am detailliertesten mit Named NPCs und explizitem Nullzeitbar-Alias.

---

## Test 5: Konzeptimport (D&D → ZEITRISS)

| Modell | Level 1? | 18 Punkte? | Keine Magie 1:1? | Vibe übernommen? | Interaktiv? | Score |
|--------|---------|-----------|-----------------|----------------|-----------|-------|
| **Sonnet 4.6** | ✅ Noch nicht gebaut — fragt erst nach Psi-Richtung | — | ✅ "Keine D&D-Regeln, keine Klassen, keine Zauber" | ✅ Rolle + Hintergrund | ✅ 3 Optionen | **9/10** |
| **DeepSeek V3.2** | ✅ Level 1 | ✅ 18 Punkte erklärt | ✅ "Keine Magie, keine Spellcasting-Foci" | ✅ Sage → Archivarin/Datenarchäologin | ✅ generate/custom/selbst | **9/10** |
| **GLM-5 Turbo** | ✅ Level 1 | ✅ Summe = 18 | ✅ "Level 12 D&D → ZEITRISS Level 1" | ✅ INT 5, Analystin | ✅ Fertiger Bogen + Nachfrage | **9/10** |
| **GLM-5** | ✅ Level 1 | ✅ Summe = 18 | ⚠️ Erfindet "Phasing I" und "Schild I" als Psi-Fähigkeiten | ✅ Vibe gut, Archiv-Forscherin | ⚠️ Psi-Fähigkeiten nicht im Regelwerk | **6/10** |

**Fazit:** Sonnet, DeepSeek und GLM-5 Turbo alle stark. Sonnet ist am vorsichtigsten (fragt nach bevor es baut). GLM-5 Voll erfindet Psi-Fähigkeiten die nicht existieren.

---

## Gesamtwertung

| Modell | Init | Manif | Load | Dienst | Import | **Gesamt** | **Ø** | **Kosten** |
|--------|------|-------|------|--------|--------|-----------|------|-----------|
| **Sonnet 4.6** | 10 | 10 | 10 | 10 | 9 | **49/50** | **9.8** | ~$0.28 |
| **GLM-5 Turbo** | 7 | 6 | 9 | 8 | 9 | **39/50** | **7.8** | ~$0.04 |
| **GLM-5** | 6 | 8 | 6 | 7 | 6 | **33/50** | **6.6** | ~$0.05 |
| **DeepSeek V3.2** | 7 | 4 | 4 | 8 | 9 | **32/50** | **6.4** | ~$0.02 |
| **Qwen 3.5** | — | — | — | — | — | **N/A** | **—** | Routing-Fehler |

---

## Fazit

### Tier-Einteilung

- **S-Tier: Sonnet 4.6** (9.8/10, ~$0.28/Session)
  Referenz bleibt Referenz. Einziges Modell das alle 5 Tests fehlerfrei besteht. Prüft Regeln bevor es würfelt. Bester Ton, beste Formatierung, null Halluzinationen.

- **A-Tier: GLM-5 Turbo** (7.8/10, ~$0.04/Session) ⭐ **ÜBERRASCHUNG**
  Bester Budget-Performer! Erkennt den Manifestation-Gate korrekt, implementiert den Load-Router fast perfekt, respektiert Dienstweg, guter Konzeptimport. Schwäche: Manifestation-Test bricht in Halluzination ab. **7× billiger als Sonnet.**

- **B-Tier: GLM-5 Voll** (6.6/10, ~$0.05/Session)
  Gute Atmosphäre, erfindet aber Regeln (Psi-Fähigkeiten, falsche Kosten). Schickt Renier nicht, aber Load-Router nur teilweise implementiert. Überraschend: Teurer als Turbo bei schwächerem Ergebnis.

- **B-Tier: DeepSeek V3.2** (6.4/10, ~$0.02/Session)
  Bester Preis, guter Ton, aber ignoriert Load-Router und Manifestation-Gate komplett. Starke Atmosphäre kann die Regellücken nicht ausgleichen. Für Casual-Play okay, für regeltreues Spiel ungeeignet.

### Empfehlung

1. **Hauptempfehlung:** Sonnet 4.6 bleibt die Referenz
2. **Budget-Empfehlung:** GLM-5 Turbo ersetzt DeepSeek V3.2 als bestes Preis-Leistungs-Modell
3. **Qwen 3.5:** Routing-Problem beheben, dann nachtesten
4. **DeepSeek V3.2:** Bleibt als Ultra-Budget-Option, aber mit Warnung "erfindet eigene Regeln"
5. **GLM-5 Voll:** Kein Vorteil gegenüber Turbo — Turbo ist billiger und regeltreuer

### Offene Punkte

- [ ] Qwen-Routing auf OpenRouter prüfen (model ID stimmt? Privacy-Filter?)
- [ ] GLM-5 Turbo Langzeit-Playtest (volle Session, 20+ Messages, Save-Zyklus)
- [ ] DeepSeek V4 testen wenn verfügbar (April 2026)
