# ZEITRISS Playtest Report — 2026-02-22

## Zusammenfassung

- **21+ Playtests** über 3 Runden, 3 Modelle
- **Gesamtkosten:** ~$0.80
- **Getestete Szenarien:** Solo-Start, Kampf, Debrief+Save, Gruppen-Merge/Split,
  Cross-Model-Load, 5er-Gruppe Rift-Boss, PvP Arena Tier 4, Chronopolis-Markt,
  Hacking, Offline-Modus, ClusterCreate, Gladiator-Kampf

## Modellvergleich

| Kriterium | Sonnet 4.6 | DeepSeek V3 | Qwen 3.5 397B |
|-----------|-----------|-------------|---------------|
| Atmosphäre/Noir | ★★★★★ | ★★★☆☆ | ⏱️ Timeout bei Gruppen |
| Gruppendynamik (5er) | ★★★★★ | ★★★★☆ | — |
| Würfelproben | ★★★★★ (Exploding, Überschuss) | ★★★★☆ | — |
| Kodex-Bordcomputer | ★★★★★ | ★★★★☆ | — |
| XP-Leiste | ✅ | ✅ | ✅ (Solo) |
| Save v6 Vollständigkeit | 13/13 | Template-treu | — |
| Ausgabelänge | 2000-3300 tok | 700-1100 tok | — |
| Kosten/Test | $0.03-0.07 | $0.002-0.004 | — |
| Cross-Model-Kompatibilität | ✅ lädt DS-Saves | ✅ erzeugt v6 | ⏱️ |

## Feature-Matrix

| Feature | Status | Notiz |
|---------|--------|-------|
| Save v6 Template (13 Pflichtfelder) | ✅ PASS | Nach Fix: 13/13 (vorher 7/13) |
| Gruppen-Merge (2→1) | ✅ PASS | Host-Regel, Wallet-Trennung korrekt |
| Gruppen-Split (1→2 Solo-Saves) | ✅ PASS | Zwei separate v6-JSONs |
| Cross-Model Save/Load | ✅ PASS | DeepSeek→Sonnet funktioniert |
| 5er-Gruppentaktik + Einzelproben | ✅ PASS | Alle 5 Proben + Kodex-Status |
| Arena Tier 4 Squad 5v5 | ✅ PASS | Gegner-Team, Taktik, 9 Proben |
| Rift-Boss Casefile (3 Akte) | ✅ PASS | Epochen-Loadout, Lore korrekt |
| Chronopolis Markt/Shopping | ✅ PASS | Händler, Preistabellen, Budget-Kodex |
| Kodex als Bordcomputer | ✅ PASS | Muni, Ladungen, Stress, Schwachstellen |
| ClusterCreate bei Px 5 | ✅ PASS | Seeds erzeugt, Debrief korrekt |
| Offline-Modus | ⚠️ PARTIAL | Sonnet verlangt erst sauberen Char |
| Px/TEMP Tabelle im Spiel | ⚠️ NOT TRIGGERED | Referenziert, aber kein Multi-Mission-Test |
| Qwen bei 5er-Gruppen | ❌ FAIL | Timeout (zu viel Kontext) |

## Empfehlung

- **Sonnet 4.6:** Premium-Pick. Für ernsthaftes Spielen, Gruppen, Langzeit-Kampagnen.
- **DeepSeek V3:** Budget-Champ. 80% Qualität bei 5% der Kosten. Ideal für Solo + schnelle Sessions.
- **Qwen 3.5 397B:** Nur Solo. Gruppen-Saves führen zu Timeouts.

## Fixes die aus den Tests resultierten (gleicher Tag)

1. Save-Template v6 im Masterprompt: 25→40 Zeilen, alle Pflichtfelder
2. Arena-Proben als Pflicht explizit verankert
3. Mindest-Ausgabelänge (3 Absätze, Kampf 4-6)
4. Kodex als taktischer Bordcomputer
5. XP-Leiste + Px-TEMP-Tabelle im Masterprompt

## Evidence-Dateien

- `playtest-2026-02-22/` — Runde 1 (9 Tests)
- `playtest-2026-02-22-r2/` — Runde 2 (11 Tests)
- `playtest-2026-02-22-deep/` — Deep-Tests (9 Tests, Modellvergleich + Gruppen)
