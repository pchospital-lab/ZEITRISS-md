# Critic-Review: feat/briefing-output-objectives

**Modell:** anthropic/claude-sonnet-4.7 (subagent)
**Gelaufen:** 2026-05-27T19:10+02:00
**Hash:** ecbeb9b00007ceeb02248a9aec5f469f833cec9f (Working-Tree-Diff auf Branch, **noch nicht committed**)
**Diff-Umfang:** 3 Files, +51/-2 Zeilen — wie angekündigt.

## Verdict

**GO mit Mini-Fix.**

Patch ist intern konsistent, Continuity-Felder existieren alle vier im v7-Schema,
Score-Screen-Erweiterung knüpft sauber an die bestehende Debrief-Pflichtkette an.
**Aber:** Zwei Stellen außerhalb des Patches führen die englischen Auftragstyp-Codes
direkt als Briefing-Vokabular an, ohne die neue deutsche Verb-SSOT zu erwähnen —
eine davon im **Spieler-Handbuch** (öffentlich!). Vor Merge nachziehen, sonst Drift.
Außerdem: **Working-Tree ist uncommitted** — der Commit-Schritt fehlt noch.

## Befunde

### 1. Verb-SSOT-Konsistenz — **DRIFT in 2 Files**

Die neue SSOT (10 deutsche Verben für Spieleroutput, englische Codes nur SL-intern)
ist im Masterprompt + `kreative-generatoren-missionen.md` sauber etabliert. **Aber**
zwei Files wiederholen die englische Code-Liste, ohne die SSOT-Trennung zu kennen:

- **`core/spieler-handbuch.md#L1106`** — *„Briefings kombinieren einen Anchor mit einem
  Auftragstyp (`protect | extract … | neutralize | document | influence | prevent`).“*
  Das ist das **Spieler-Handbuch** — die englischen Codes werden hier dem Spieler
  direkt vorgesetzt, obwohl der Patch sagt: *„englische Codes tauchen niemals im
  Spieleroutput auf“*. Klarer Widerspruch.
- **`systems/toolkit-gpt-spielleiter.md#L203`** — gleiche englische Aufzählung,
  ohne Hinweis auf die deutsche Verb-SSOT für den Spieleroutput. SL-internes Tool,
  also milder, aber der Toolkit ist genau die Quelle, aus der der KI-SL beim
  Briefing zieht — Pflichtgate-Querverweis fehlt.

`core/sl-referenz.md` ist sauber (keine eigene Auftragstyp-Liste). `CoreObjectiveTable`
(Z. 893+) und `RiftSeedTable` benutzen bereits deutsche Verben in `Objective_P`/
`Objective_T`-Strings (*„Sichere…“*, *„Bewahre…“*, *„Extrahiere…“*) — kompatibel.

### 2. Continuity-Anker-Felder — **OK**

Alle vier referenzierten Felder existieren im v7-Save-Schema:

- `arc.hooks[]` → `systems/gameflow/saveGame.v7.schema.json` Z. 229 (Required in `arc`).
- `arc.questions[]` → Z. 228 (Required in `arc`).
- `logs.notes[]` → Z. 156 (Required in `logs`).
- `continuity.shared_echoes[]` → Z. 366 + Z. 422 (Required in `continuity`).

Keine Field-Erfindung im Patch. Das Pflicht-Format der `continuity.shared_echoes`-
Items (`{tag: …}` statt Rohstring, siehe Masterprompt §D) bleibt unberührt — der
Patch *liest* nur, schreibt nicht das Format um.

### 3. Debrief-Spiegel-Mechanik — **OK, Erweiterung statt Bruch**

Score-Screen existiert bereits als Pflicht-Element:
- `meta/masterprompt_v6.md#L98`: *„`PHASE Debrief` MUSS folgen: Score-Screen → Loot-Recap → …“*
- `meta/masterprompt_v6.md#L394`: *„Nach jeder Mission automatisch einen Score-Screen zeigen“*
- `gameplay/kampagnenstruktur.md#L795`: *„Reihenfolge ist verbindlich: Score-Screen → Level-Up-Wahl → `!save`“*

Der Patch erweitert den bestehenden Score-Screen um eine **Ziel-Abhak-Sektion**
(✓/✗ pro Briefing-Ziel) und einen **Rückkanal zu `arc.hooks[]`** für verfehlte
Ziele. Das ist additive Logik, kollidiert nirgends. Einziger leichter Punkt:
Im Masterprompt §F Debrief & Progression (Z. 394+) wird die neue Ziel-Abhak-
Pflicht **nicht** wiederholt — sie steht nur in §C (neu) und in `kampagnenstruktur.md`.
Wäre konsistenter, in §F die Bullet-Liste *„Bewertung → Loot-Recap → …“* um
*„→ Ziel-Spiegel (✓/✗ pro Briefing-Ziel)“* zu ergänzen. Kein Blocker, aber
sauberer SSOT-Ort wäre §F.

## Empfehlung

**Mini-Fix vor Merge (3 Stellen, < 10 Zeilen):**

1. `core/spieler-handbuch.md` Z. 1106 — englische Code-Liste als SL-intern markieren
   und auf deutsche Verb-SSOT verweisen:
   ```diff
   -- **Core-Ziele mischen:** Briefings kombinieren einen **Anchor** mit einem
   -  Auftragstyp (`protect | extract (Evakuierung/Schutzaufnahme) | neutralize |
   -document | influence | prevent`). Mindestens 60 % …
   +- **Core-Ziele mischen:** Briefings kombinieren einen **Anchor** (Person/Ort/
   +  Objekt) mit einem Auftrag. Im Spieleroutput nutzt der KI-SL die deutsche
   +  Verb-SSOT (**sichern, ausschalten, retten, festnehmen, dokumentieren,
   +  beeinflussen, verhindern, exfiltrieren, beschatten, sabotieren**); die
   +  englischen Auftragstyp-Codes (`protect`/`extract`/…) sind SL-intern.
   +  Mindestens 60 % …
   ```

2. `systems/toolkit-gpt-spielleiter.md` Z. 200–207 — Querverweis auf das
   Briefing-Output-Pflichtgate ergänzen (eine Zeile):
   ```diff
   +- **Spieleroutput-Verben:** Auftragstyp-Codes sind SL-intern für Mapping.
   +  Im Briefing-Text die deutsche Verb-SSOT verwenden (sichern/ausschalten/
   +  retten/festnehmen/dokumentieren/beeinflussen/verhindern/exfiltrieren/
   +  beschatten/sabotieren). Pflichtregel: Masterprompt §C Briefing-Output-Pflichtgate.
   ```

3. `meta/masterprompt_v6.md` §F Debrief & Progression (Z. ~394, „Score-Screen zeigen“)
   — Ziel-Spiegel als Bullet ergänzen (eine Zeile):
   ```diff
   -- **Debrief:** Nach jeder Mission automatisch einen Score-Screen zeigen:
   -  Bewertung → Loot-Recap → CU-Auszahlung → XP/Level-Up → ITI-Ruf-Update → Lizenz-Tier.
   +- **Debrief:** Nach jeder Mission automatisch einen Score-Screen zeigen:
   +  Bewertung → **Ziel-Spiegel (✓/✗ pro Briefing-Ziel, verfehlte → `arc.hooks[]`)**
   +  → Loot-Recap → CU-Auszahlung → XP/Level-Up → ITI-Ruf-Update → Lizenz-Tier.
   ```

**Außerdem (nicht Diff, sondern Prozess):**
- Working-Tree ist uncommitted (`git status` zeigt unstaged changes auf
  `feat/briefing-output-objectives`). Vor Push: `commit-msg-prepare.sh --commit`
  ausführen und mit Pflicht-Struktur (Was/Warum/Entscheidungen/Verifikation/
  Post-Merge-TODOs) committen — siehe TOOLS.md §PR-Flow.
