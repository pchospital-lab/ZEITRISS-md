# ZEITRISS — Architektur-Lernnotizen

> **Zweck:** Bevor ich weitere Playtests aufsetze, dokumentiere ich mein Verständnis der Architektur. Flo prüft, korrigiert, ergänzt. Erst dann neue Testpläne.
>
> **Erstellt:** 2026-04-19 von Altair
> **Status:** DRAFT — wartet auf Flo-Review

---

## 1. Spiel-Struktur (Hierarchie)

```
Kampagne
 └─ Arc                  (mehrere Episoden, TV-Staffel-artig)
     └─ Episode          (~10 Missionen, 120–140 Szenen, gleiches setting_id)
         ├─ Mission      (~12 Core-Szenen / ~14 Rift-Szenen)
         │   └─ Szene    (eine konkrete Spielszene)
         └─ Rift-Op      (separate Instanz, Paramonster, eigene 14-Szenen-Struktur)
```

**Arc-Phasen (pro ~10 Episoden):**
- **Einleitung** (Ep 1–2): Setup, Exposition
- **Konflikt & Entwicklung** (Ep 3–7): Ermittlungen, Eskalation, Fraktionen
- **Klimax** (Ep 8–9): Finale Konfrontation
- **Übergang** (Ep 10): Abschluss, Brücke zum nächsten Arc

---

## 2. Die drei Operationstypen (STRIKT GETRENNT)

### Core-Ops
- Das Haupt-Gameplay. Missionen mit 12 Szenen in einer Zeitlinie.
- Beispiele: Infiltration, Sabotage, Rettung, Spionage
- Eindruck → Spurarbeit → rationale Auflösung
- Entstehen aus dem Mission-Generator oder Arc-Seed

### Rift-Ops
- Instanz-basierte Paramonster-Kämpfe in Rissen
- 14 Szenen, dürfen unheimlicher/surrealer wirken, bleiben aber ZEITRISS-physikalisch
- Ausgelöst über Paradoxon-Punkte (Px) / Seeds
- Auf Lvl 3–5 (80–1000): Multi-Phase-Bosse → Seed-Ketten → Apex-Paramonster mit voller Chrono-Suite

### Chronopolis / ITI-Arena (ab Lvl 10)
- Nach Schlüssel-Unlock: ringförmige Stadt-Zone um ITI-HQ
- PvP-Arena (`arena.match_policy=sim` oder `lore`)
- Zeigt die "gescheiterte Zeitlinie" der aktuellen Episode
- Kein Speichern, kein Sonder-Respawn
- **Pre-City-Hub** davor als Übergangsphase

---

## 3. HQ-Kern (Nullzeit, immer derselbe Raum)

**Identisch in Solo / NPC-Team / Multiplayer-Modus:**

Player-facing Hauptorte:
- Quarzatrium, Kodex-Archiv, Med-Lab, Operations-Deck
- Quartiere, Hangar-Axis, Zero Time Lounge, Pre-City-Hub

Kernpersonal-Anker:
- Commander Arnaud Renier
- Archivarin Mira
- Pater Lorian
- Offizier Vargas
- Agentin Narella

---

## 4. MMO-Feeling (Kernprinzip — darf NIE verloren gehen)

**Flo-Zitat:** *"Auch wenn man solo spielt, soll es sich wie ein MMO anfühlen. Die Kollegen übernimmt die KI. Ich will alleine auf Mission gehen können, mit meinen NPC-Kollegen und mit meinen menschlichen Kameraden oder gemischt."*

**Drei Modi, gleiche Welt:**

| Modus | Befehl | Charaktere |
|---|---|---|
| **Solo pur** | `Spiel starten (solo klassisch)` | 1 SC, nur Kodex-Stimme im Einsatz |
| **Solo + NPCs** | `Spiel starten (solo klassisch)` + `npc-team 1-4` | 1 SC + 1–4 KI-Kollegen = Team von 2–5 |
| **Echte Gruppe** | `Spiel starten (gruppe schnell/klassisch)` | Mehrere menschliche SCs (+ optional NPCs) |

**Mixed Mode:** Echte Gruppe + NPCs für Leerstellen ist auch erlaubt (Team-Cap 5).

**Immersions-Anker im Solo-Modus:**
- ITI und andere Chrononauten existieren im Hintergrund (Kommunikations-Knoten, Infobriefe, Fraktions-Signale)
- "Man ist alleine unterwegs" → spannend durch Isolation
- "Aber man weiß: da draußen ist das Institut, andere Agenten, eine lebende Welt"

---

## 5. Save-Dynamik (das unterschätzte Feature)

**Prinzip:** Der JSON-Save IST der Charakter. Portabel, mitnehmbar, teilbar.

**Drei Bewegungs-Muster:**
1. **Save-Portabilität:** Charakter von Chat zu Chat mitnehmen (zB Mission 1 in Chat A, Debrief + Save, neuer Chat, Mission 2 mit geladenem Save)
2. **Split:** Gruppe teilt sich für Parallel-Rift-Ops (Team A in Chat 1, Team B in Chat 2)
3. **Merge:** Zurück-Verschmelzen zweier Saves (Host = Index 0, `merge_conflicts`-Log)

**Schema-Lineage (v7-Pflicht):**
- `save_id`, `parent_save_id`, `merge_id`, `branch_id`
- `continuity.split.family_id` markiert aufgeteilte Gruppen
- `logs.flags.merge_conflicts[]` mit Allowlist (wallet, rift_merge, arena_resume, campaign_mode, phase_bridge, location_bridge)

**Wallet-Logik:**
- Solo: `economy.hq_pool` einzelner Wert
- Koop: `Wallet-Split (n×)` nach jeder Mission für persönliche Kassen + `hq_pool` als Gruppen-Rest
- Umstieg Solo → Koop: `initialize_wallets_from_roster()` verschiebt Solo-Guthaben automatisch

---

## 6. Session-Architektur (Wie eine Episode tatsächlich gespielt wird)

**Flos Aussage:** *"Er muss Einleitung und Ankunft im ITI spielen, mit Charaktererstellung. Dann speichert, dann im neuen Chat mit diesem die erste Mission spielt, inkl. Debrief, speichern, neuer Chat, nächste Mission, bis die erste Episode mit Mini und Endboss durch ist."*

**Realistische Chat-Kette für Episode 1:**

| Chat | Inhalt | Save-Aktion |
|---|---|---|
| 1 | Rekrutierung + Ankunft ITI + Charaktererstellung + Onboarding | Save nach Char-Gen |
| 2 | Mission 1 (~12 Szenen) + Debrief | Save nach Debrief |
| 3 | Mission 2 + Debrief | Save |
| 4 | Mission 3 + Debrief | Save |
| 5 | Mission 4 + Debrief | Save |
| 6 | Mission 5 + Debrief | Save |
| 7 | Mission 6 + Debrief | Save |
| 8 | Mission 7 + Debrief | Save |
| 9 | Mission 8 + Debrief (Mid-Boss?) | Save |
| 10 | Mission 9 + Debrief | Save |
| 11 | Mission 10 (End-Boss der Episode) + Debrief + Level-Up | Save |

**Pro Chat:** Ein abgeschlossener Spielabschnitt mit sauberem Save-Übergang.

---

## 7. Was der aussagekräftige Playtest sein muss

**Flo-Zitat:** *"Das einmal Solo, einmal als solo mit NPCs und einmal als echte Gruppe. Einmal im Low-Level-Bereich und einmal im High-Level-Bereich. Das wäre aussagekräftig."*

**Testmatrix = 6 vollständige Episoden:**

| # | Modus | Level | Chat-Kette | Save-Verkettung | Gruppen-Dynamik |
|---|---|---|---|---|---|
| 1 | Solo pur | Lvl 1 (Start) | 11 Chats | Einzel-Save | — |
| 2 | Solo + NPC-Team (3) | Lvl 1 (Start) | 11 Chats | characters[]-Array | NPC-Kollegen bleiben persistent |
| 3 | Echte Gruppe (3er) | Lvl 1 (Start) | 11 Chats | Gruppe-Save mit 3 SCs | Host-Rotation? |
| 4 | Solo pur | Lvl 800–1000 | 11 Chats | Lvl-950-Save | Welt-Reaktion bei Apex |
| 5 | Solo + NPC-Team (4) | Lvl 500+ | 11 Chats | NPCs müssen ebenfalls hochskaliert sein | — |
| 6 | Echte Gruppe (5er) mit Split/Merge | Lvl 80–120 | variabel | Split in 2+3, parallel, Merge | Volles Save-Dynamik-Feature |

**Das sind 6 × ~10 Missionen = 60 Missionen. Aufwendig. Aber DAS ist aussagekräftig.**

---

## 8. Was die Einzel-Proben (vet-02-shadowrun) verfehlt haben

Der erste Marek-Run hat als Kontext-FREIE Einzelaktionen gespielt:
- "Ich pirsche mich an den Wachmann"
- "Ich hacke den Server"
- "Ich aktiviere Temporale Resonanz"

**Problem:** Ohne Szene-Boden, ohne Missions-Kontext, ohne Episodenlauf sind das **Zahlen im Vakuum**. Der SL hat das selbst erkannt und meta-kommentiert:

> *"Vier von zehn Aktionen haben nie eine Szene erreicht. Das ist kein Lvl-950-Problem — das ist ein Kontext-Problem."*

**Konsequenz:** Die Einzel-Proben-Methode **funktioniert nicht** für Shadowrun-Test. Man braucht **gespielte Missionen** mit echter Szene-Dramaturgie.

---

## 9. Offene Fragen an Flo

1. **Länge pro Mission:** ~12 Szenen, je Szene ~500–1500 Tokens KI-Antwort. Pro Mission grob 30–60k Tokens Chat. Bei 10 Missionen = 300–600k Tokens pro Episode. **Machbar mit Sonnet 4.6, aber teuer.** Willst Du das wirklich full-through, oder reicht eine **verkürzte Episode** (zB 3 Missionen + Miniboss + Endboss) als Mini-Sample?

2. **NPC-Team-Persistenz über Chats:** Wie werden NPCs im Save persistiert? Sind sie volle `characters[]`-Einträge oder separate `npc_team[]`? Muss ich noch rausfinden oder weißt Du's aus dem Kopf?

3. **Split/Merge praktisch:** Hast Du ein konkretes Beispiel-Save-Paar (Pre-Split + 2× Post-Split + Post-Merge), das ich als Referenz nutzen kann? Das würde das 5er-Test-Protokoll schlagartig realistisch machen.

4. **High-Level-NPC-Teams:** Gibt es vorgefertigte NPC-Teams für Apex-Missionen, oder muss der KI-SL sie on-the-fly generieren?

5. **Testpriorität:** Welche der 6 Matrix-Runs ist am wertvollsten zuerst? Mein Bauchgefühl:
   - **Run #1 (Solo pur Lvl 1)** = deckt Onboarding + Kernmechanik ab, hohe Praxisrelevanz
   - **Run #6 (5er Split/Merge Lvl 80-120)** = deckt die komplexeste Dynamik ab, höchstes Bug-Risiko
   - **Run #4 (Solo Apex)** = deckt das Shadowrun-Kriterium richtig ab
   - Die restlichen drei als Confirmation-Runs

---

## 10. Methodik-Update für weitere Playtests

- **Episode-Level, nicht Proben-Level.** Mindestens 3 Missionen in einer Chat-Kette.
- **Save-Übergänge zwischen Chats** mitprüfen (das wurde bisher ignoriert).
- **Persona bleibt**, aber agiert in echtem Missions-Kontext, nicht im Vakuum.
- **Python-Harness statt Sub-Agent** für die IO-Schleife (siehe Learning aus vet-live-playtest).
- **Pro Mission:** Einen Bericht mit Szene-Logs + Save-Delta + Friction-Log.

---

*Status: Warte auf Flo-Review. Nach Bestätigung oder Korrekturen → echte Playtest-Implementierung.*
