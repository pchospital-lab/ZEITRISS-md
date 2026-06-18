# Critic-Review v2: feat/briefing-output-objectives

**Modell:** openrouter/anthropic/claude-opus-4.7 (thinking=high, sub-agent)
**Gelaufen:** 2026-05-27T19:32+02:00
**Hash:** 1a9b516b · 5 files, +98/-11
**Vorgänger-Review:** `critic-review-briefing.md` (v1, sonnet-4.7, GO mit Mini-Fix)

## Verdict

**GO mit Mini-Fix** — Patch ist substantiell besser als v1, Smoke grün, Schema-Konformität für Multiplayer-Klausel sauber, alle major-Cross-Refs existieren. ABER: zwei klare Drift-Stellen (Wording-Inkonsistenz Geltungsbereich + ein implizit Rift-mitnehmender §Briefing-Debrief-Szenen-Count-Bullet in `kampagnenstruktur.md`) und eine falsche Cross-Reference im Toolkit. Alle drei sind 1-Zeilen-Fixes vor Merge, kein Re-Review nötig.

## Smoke

✓ All smoke checks passed (`bash scripts/smoke.sh` durchgelaufen, 36 Checks grün, inkl. `ruf-alien-watchguard-ok`, `v7-schema-consistency-ok`, `continuity-output-contract-ok`, `npc-continuity-consistency-ok`, `physicality-watchguard-ok`).

## Befunde

### 1. Rift-Geltungsbereich vollständig? — **NEIN, eine 4. Drift-Stelle**

`gameplay/kampagnenstruktur.md` §Briefing-Debrief-Szenen-Count (L676–684, neuer **Briefing**-Bullet + L688–692 **Debrief**-Bullet) ist nicht Core-skopiert. Der **umgebende** Abschnitt nennt explizit beide Modi (`SC 01/12 (bzw. SC 01/14)`, *„Szene 12 (Core) bzw. Szene 14 (Rift)“*), und die neue Klausel sagt absolut: *„Jedes Briefing endet mit strukturierter Ziel-Ausgabe (Hauptziel + 0–2 Nebenziele, Verb-SSOT sichern/ausschalten/…) plus mindestens einem Continuity-Rückverweis ab MS2.“* Ein literaler Leser bezieht das auf Rift mit. Identisch der Debrief-Spiegel-Bullet.

**Fix (Mini-Diff, `gameplay/kampagnenstruktur.md`, beide Bullets):**

```diff
-  `SC 01/12` (bzw. `SC 01/14`). **Output-Pflicht:** Jedes Briefing endet mit
+  `SC 01/12` (bzw. `SC 01/14`). **Output-Pflicht (Core-Ops):** Jedes
+  Core-Briefing endet mit
```
und im Debrief-Bullet:
```diff
-  **Debrief-Spiegel-Pflicht:** Score-Screen hakt die im Briefing gesetzten
+  **Debrief-Spiegel-Pflicht (Core-Ops):** Score-Screen hakt die im
+  Core-Briefing gesetzten
```
(Rift-Debrief spiegelt Forensik-Dreieck + Fix-Objectives, siehe Masterprompt §C Rift-Klausel — sollte als Querverweis dazu.)

`core/spieler-handbuch.md` L1105–1116 ist OK: Bullet-Header *„Core-Ziele mischen“* + Satz *„60 % der Core-Ops“* skopiert eindeutig auf Core; Verb-SSOT-Hinweis bleibt nicht implizit Rift-erfassend.

### 2. Multiplayer-Schema-Konformität — **OK**

- `continuity.shared_echoes[].scope`-Enum laut `systems/gameflow/saveGame.v7.schema.json` L383–391: `["shared", "rumor", "campaign", "personal"]`. Der Patch verwendet `scope: "campaign"` für Split-Folgespuren → **schema-konform**. Bestätigt durch Masterprompt §I L949 (gleiche Liste).
- `arc.hooks[]` als Array-of-String: Patch sagt *„Solo/Squad-Folgespuren weiter als String-Eintrag in `arc.hooks[]`“* → konsistent mit Highlander-MS7-Save-Format. Kein bestehender Eintrag wird durch den Patch berührt.
- `continuity.split.family_id`, `expected_threads[]`, `resolved_threads[]`, `convergence_ready` — alle existieren (Masterprompt §I L983–984 explizit „Konvergenz entsteht, sobald `resolved_threads[] == expected_threads[]`; dann ist `convergence_ready=true`“).
- Merge-Regel im Patch (*„Priorität `shared > campaign > rumor > personal`“*) **stimmt wortgleich** mit Masterprompt §I L949–953 überein. Kein Konflikt mit `test_v7_schema_consistency.js` / `test_continuity_output_contract.js` (beide grün im Smoke).

### 3. Wording-Konsistenz „Geltungsbereich“ — **DRIFT (klein, sollte vereinheitlicht werden)**

Drei Files, drei leicht unterschiedliche Formulierungen für denselben Begriff:

| File | Zeile | Formulierung |
| --- | --- | --- |
| `meta/masterprompt_v6.md` | L161 | *„Dieses Pflichtgate gilt **primär für Core-Ops-Briefings**.“* |
| `gameplay/kreative-generatoren-missionen.md` | L172–173 | *„gelten **ausschließlich** für Core-Briefings.“* |
| `systems/toolkit-gpt-spielleiter.md` | L205 | *„gilt nur für **Core-Briefings**.“* |

„Primär“ vs. „ausschließlich“ vs. „nur“ ist semantisch nicht identisch: „primär“ lässt explizit Raum für Rift-Anteilnahme („normalerweise Core, kann auch Rift treffen“), die anderen beiden sagen „nicht Rift, Ende“. Da der Masterprompt direkt darunter die Rift-Ausnahmen aufzählt, ist „nur“/„ausschließlich“ die korrekte Lesart.

**Empfehlung (1-Wort-Fix in Masterprompt §C):**
```diff
-  - **Geltungsbereich Core-Ops vs. Rift-Ops:** Dieses Pflichtgate gilt **primär für Core-Ops-Briefings**. **Rift-Ops haben ein eigenes Briefing-Format** …
+  - **Geltungsbereich Core-Ops vs. Rift-Ops:** Dieses Pflichtgate gilt **ausschließlich für Core-Ops-Briefings**. **Rift-Ops haben ein eigenes Briefing-Format** …
```

### 4. Watchguard-Strings — **OK**

`grep -rn "Briefing-Output-Pflichtgate\|Verb-SSOT\|Hauptziel\|Continuity-Anker" tools/test_*.js` liefert **null Treffer** — kein Watchguard prüft die neuen Strings wortgleich. Score-Screen-Sequenz in §F (Z.404+) bleibt unverändert (`Bewertung → Loot-Recap → CU-Auszahlung → XP/Level-Up → ITI-Ruf-Update → Lizenz-Tier`), Ziel-Spiegel-Klausel ist separat eingefügt → `ruf-alien-watchguard-ok` grün. Keine zusätzlichen Risiko-Strings entdeckt.

### 5. Cross-Verweise valide?

| Verweis | Ziel-Datei | Existiert? | Anmerkung |
| --- | --- | --- | --- |
| „§I Squad-Manöver" | `meta/masterprompt_v6.md` L691 | ✓ | Bullet-Header „Squad-Manöver innerhalb einer Mission sind KEIN Split" |
| „§I Core-Split-Kanon" | `meta/masterprompt_v6.md` L983 | ✓ | wortgleich vorhanden |
| „§I Schema-v7-Regeln" / `shared_echoes`-Pflichtformat | `meta/masterprompt_v6.md` L948 | ✓ | als „`shared_echoes`-Pflichtformat" geführt; loose match akzeptabel |
| „`kreative-generatoren-missionen.md` §Rift-Seed Catalogue / `briefing_public`-Schema" | `gameplay/kreative-generatoren-missionen.md` L2252+L2263 | ✓ | Anchor `#rift-seed-catalogue` explizit gesetzt; 5× `briefing_public:` in Seeds |
| „`kampagnenstruktur.md` §Forensik-Dreieck" | `gameplay/kampagnenstruktur.md` L562 | ✓ | Header *„Forensik-Dreieck (Rift-Casefiles)"* → auto-anchor `#forensik-dreieck-rift-casefiles` |
| „`kampagnenstruktur.md` §Rift-Op Interface Contract" | `gameplay/kampagnenstruktur.md` L364 | ✓ | wortgleich vorhanden |
| `kreative-generatoren-missionen.md` §Rift-Casefiles | L266 | ✓ | „Rift-Casefiles: Tatort → Leads → Boss-Encounter → Auflösung" |
| **„Masterprompt §C IA/RW-Spot-Pflichtgate (Geltungsbereich)"** in `systems/toolkit-gpt-spielleiter.md` L208 | `meta/masterprompt_v6.md` L129 (IA/RW-Spot-Pflichtgate) | **✗ FALSCH** | IA/RW-Spot-Pflichtgate handelt von **Insertion-Anchor-Spots**, nicht vom Briefing-Output. Die „Geltungsbereich Core-Ops vs. Rift-Ops"-Klausel sitzt im **Briefing-Output-Pflichtgate** (L161), nicht im IA/RW-Spot-Pflichtgate. |

**Fix (Mini-Diff, `systems/toolkit-gpt-spielleiter.md` L207–208):**
```diff
-  Continuity-Anker-Zwang) — siehe `gameplay/kreative-generatoren-missionen.md`
-  §Rift-Casefiles und Masterprompt §C IA/RW-Spot-Pflichtgate (Geltungsbereich).
+  Continuity-Anker-Zwang) — siehe `gameplay/kreative-generatoren-missionen.md`
+  §Rift-Casefiles und Masterprompt §C Briefing-Output-Pflichtgate
+  (Geltungsbereich Core-Ops vs. Rift-Ops).
```

## Empfehlung

**GO mit drei Mini-Fixen** (alle drei sind reine Text-Korrekturen ohne Logik-Risiko):

1. `gameplay/kampagnenstruktur.md` §Briefing-Debrief-Szenen-Count: beide neuen Bullets als *„Output-Pflicht (Core-Ops)"* / *„Debrief-Spiegel-Pflicht (Core-Ops)"* markieren + Wort „Core-" vor „Briefing"; bei Debrief Querverweis auf Rift-Spiegel ergänzen.
2. `meta/masterprompt_v6.md` L161: „primär" → „ausschließlich" (Konsistenz mit Generator/Toolkit; matches umliegende Rift-Ausnahme-Liste).
3. `systems/toolkit-gpt-spielleiter.md` L208: falsche Cross-Ref „IA/RW-Spot-Pflichtgate" → „Briefing-Output-Pflichtgate".

Nach Fix: kein Re-Critic nötig (rein editorial, kein Schema-/Watchguard-Risiko). Smoke bleibt grün, weil keine geprüften Strings betroffen sind.
