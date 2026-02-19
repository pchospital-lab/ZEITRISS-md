# QA-Testrun 2026-02-16 — OpenWebUI (Sonnet 4 + Opus 4.6)

**Plattform:** OpenWebUI localhost:3000, OpenRouter
**Knowledge Base:** 20 Slots (core/spieler-handbuch.md + 19 Runtime-Module)
**Masterprompt:** meta/masterprompt_v6.md (Local Uncut 4.2.6)
**Modelle:** anthropic/claude-sonnet-4, anthropic/claude-opus-4
**Methode:** API-Calls (Single-Shot, non-streaming, max_tokens 12000-16000)
**Tester:** Altair (Agent)

## Runs

| Run | Szenario | Modell | Output |
|-----|----------|--------|--------|
| 1a | Klassischer Start + 1. Mission | Sonnet 4 | 4.574 Zeichen |
| 1b | Klassischer Start + 1. Mission | Opus 4.6 | 2.199 Zeichen |
| 2 | Mid-Game Mission 5 Boss-Gate (Save Load) | Sonnet 4 | 2.866 Zeichen |
| 3 | High-Level Rift-Op + Chronopolis (Save Load) | Sonnet 4 | 1.670 Zeichen |
| 4 | PvP Arena (Save Load) | Sonnet 4 | 1.652 Zeichen |
| 5a | Gruppenspiel — 2 Spieler Charakter-Erstellung | Sonnet 4 | 3.410 Zeichen |
| 5b | Gruppenspiel — Spieler B übernimmt via Save | Sonnet 4 | 1.884 Zeichen |

## Ergebnisse

### PASS ✅

1. **HUD-Format** — Konsistent über alle 7 Runs. Korrekte Felder (EP, MS, SC, PHASE, MODE, COMMS, Px, Stress, Obj, Exfil).
2. **Save/Load** — Speicherstände werden erkannt und Recap korrekt generiert (Run 2-5b).
3. **Noir-Atmosphäre** — Durchgehend filmisch, Sinnesdetails (Kälte, Ozon, Neonlicht), keine Abschweifungen.
4. **Würfelproben** — Korrekte Notation: W6 + Attribut/2 + Talent + Gear vs SG (Run 1a, 2).
5. **3 Optionen + Freie Aktion** — Konsequent eingehalten in allen Runs.
6. **Kodex** — Meldet sich kontextgerecht als Systemstimme, nicht als separate Rolle.
7. **Squad-Radio** — Run 5a/5b zeigen authentische Callouts zwischen PHANTOM und CIPHER.
8. **Gruppenspiel-Handoff** — Save-Transfer zwischen zwei Sessions funktioniert (Run 5a→5b). KI greift Squad-Radio-Logs auf und führt Szene nahtlos weiter.
9. **Foreshadowing** — Run 2 baut "Der Architekt" als Boss-Antagonist über mehrere Missionen auf.
10. **Rift-Seeds** — Run 3 greift Seeds korrekt aus dem Save und bietet Auswahl.
11. **Arena-Setup** — Run 4 zeigt Tier-System, Gebühr und Loadout-Budget.
12. **Du/Ihr-Perspektive** — Solo nutzt "Du", Gruppe nutzt "Ihr" (Run 5a) bzw. "Du" für den fokussierten Spieler (Run 5b). Korrekt.

### FAIL / ISSUES ⚠️

1. **Output-Limit** — Single-Shot API-Calls liefern max. 1 Szene pro Run statt der vollen 12/14. Das ist ein API-/Plattform-Limit, kein Regelwerk-Problem. Im interaktiven Browser-Chat würde die KI weiterspielen.
2. **Regelwerk-Halluzinationen (Sonnet):**
   - Erfindet "Zeitkristall-Reserven" als Item (existiert nicht)
   - Health/Stress-Formeln frei erfunden statt aus Regelwerk
   - ITI falsch als "Internationaler Zeitforschungsrat" benannt (Run 1a)
   - Attributwerte in Run 5a nicht im 1-5 Starterbereich (STR 8, GES 12 etc. statt korrekt 1-5 bei 18 Punkten)
3. **Regelwerk-Halluzinationen (Opus):**
   - Erfindet "TEMP" als Organisation statt ITI
   - Weniger Output, Charaktererschaffung nicht durchgeführt
   - Stress 0/5 statt korrektem Maxwert
4. **Chronopolis-Zugang** — Run 4 gibt Zugang bei Level 8, laut Regelwerk erst ab Level 10 (Run 3 macht es korrekt).
5. **Arena-Werte** — Loadout-Budget und Gebühren in Run 4 sind plausibel aber nicht aus dem Regelwerk belegt (freie Erfindung).
6. **Kein v6-Save generiert** — Keiner der Runs generiert einen korrekten vollständigen v6-Save. Das Schema wird nicht aus dem Wissensspeicher abgerufen.

### Sonnet vs Opus (Direktvergleich Run 1)

| Kriterium | Sonnet 4 | Opus 4.6 |
|-----------|----------|----------|
| Output-Länge | 4.574 Zeichen | 2.199 Zeichen |
| Atmosphäre | Gut, professionell | Dichter, filmischer, emotionaler |
| Regeltreue | Mittel (erfindet Items) | Schwach (erfindet Organisation) |
| Charakterbogen | Vollständig gezeigt | Nicht generiert |
| HUD-Format | Korrekt | Korrekt |
| Einleitung | Paraphrasiert (nicht zitiert) | Paraphrasiert (nicht zitiert) |

**Fazit:** Sonnet liefert mehr Content und ist regeltreuer. Opus ist atmosphärisch stärker aber kürzer und halluziniert fundamentaler (falsche Organisation). Für Spielsessions ist Sonnet der bessere Default.

## Empfehlungen

1. **Interaktives Testen im Browser** — Die API-Tests zeigen dass die Grundmechaniken funktionieren. Für echte Qualitätsbewertung muss Turn-für-Turn im Browser gespielt werden.
2. **RAG-Retrieval verbessern** — Die KI nutzt den Wissensspeicher nicht immer vollständig. Mögliche Ursache: OpenWebUI-Embedding-Fehler bei `zeitriss-core.md` und `toolkit-gpt-spielleiter.md` (Verknüpfungs-Warnung beim Setup).
3. **Attribut-Grenzen im Masterprompt härten** — "Attribute 1-5 bei Start, 18 Punkte verteilen" sollte prominenter stehen.
4. **Save-Schema-Referenz stärken** — Ein Kompakt-Save-Beispiel direkt im Spieler-Handbuch könnte helfen.
