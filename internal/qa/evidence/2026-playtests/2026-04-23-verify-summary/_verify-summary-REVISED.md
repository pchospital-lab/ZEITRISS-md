# Verification-Summary REVISED (nach Critic-Review)

**Erstellt:** 2026-04-23 14:30 nach Opus-4.7-Critic-Durchlauf  
**Revision-Grund:** Der erste Summary war zu optimistisch. Critic fand 4 ernsthafte Defekte und 6 Drift-Themen, die der Hauptagent übersehen hatte. Mehrere wurden manuell verifiziert und bestätigt.

---

## Bestätigte Patches (nach Revision)

| Patch | Ursprüngliches Rating | **Revidiertes Rating** | Grund |
|-------|----------------------|----------------------|-------|
| HUD-Gate-Policy | 🟢 GO | 🟢 **GO** | Unverändert korrekt |
| Kodex-Typisierung A/B/C/D | 🟢 GO | 🟢 **GO** | Unverändert korrekt |
| Level-Up-Exklusivitäts-Pflichtgate | 🟢 GO | 🟢 **GO** (Run B ist Gold) | Unverändert korrekt |
| Mission-Transition-Pflichtgate | 🟢 GO | 🟡 **soft** | Run A T27 signalisiert es nicht explizit; Gate griff nur weil SL "improvisierte" bei Skip-Versuch |
| Save-Reihenfolge LvlUp → !save | 🟢 GO | 🟢 **GO** | Run B T2 ist Gold-Standard |
| `level_history`-Persistenz | 🟢 GO | 🔴 **UNKLAR** | Drei Runs, drei verschiedene Formen. Kein SSOT-Schema. |
| Save/Reload-Flow | 🟢 GO | 🟡 **GO mit Drift** | Load funktioniert, aber W10-Schwelle-Drift ist systematisch, nicht einmalig |
| Group-Split/Merge-Flow | 🟢 GO | 🔴 **FAIL** | Save-Schema-Verletzung + inkonsistente Attribut-Normalisierung |

---

## 🔴 Kritische Findings

### 1. XP-Regel wird systematisch falsch angewendet

**Regel** (`core/zeitriss-core.md` Z.325-327):
```
| Level  | XP pro Level       |
| 1–10   | 1 XP (= 1 Mission) |
```
→ Phase 1: **1 Mission = 1 XP = 1 Level-Up**. Kein 10er-XP-Balken.

**Beobachtung:**
- **Run A T27:** `Kodex: Mission 1 abgeschlossen. XP +1. Stand: 1/10. Lvl 1 — keine Schwelle erreicht.` → SL wendet die Lvl-11-20-Tabelle an. **Falsch.**
- **Run B T1:** `Lvl 2, XP 0, Rekrut → Feldagentin` → **Korrekt.**
- **Run D merge T1:** Chars enden bei `Lvl 1, XP 9/10` → **Wieder falsch** (gleicher Bug wie Run A).

→ **Systematischer Regelbruch** in zwei von drei Runs. Nicht PR-#2963-Scope (Master-Prompt-Problem, existierte schon vor dem PR), aber jetzt sichtbar geworden.

### 2. Run A Save ist in sich inkonsistent

**Datei:** `verify-runA-debrief-1344/save-runA-final.json`

- `lvl: 1, xp: 1, rank: "Rekrut"` ← unverändert nach Mission
- `level_history: { "1": { "choice": "+1 Attribut", "detail": "GES 5→6", "mission": "MS1" } }` ← Level-Up persistiert
- **Widerspruch:** GES wurde angehoben (auf 6 im Save), aber das Level ist weiterhin 1, Rang "Rekrut", XP 1/10.

Folgerung: Run A **beweist nicht** dass `level_history` sauber persistiert wird — beweist vielmehr dass das Save-Feld **orthogonal zum Rest des State-Transitions** läuft. Meine Summary-Aussage "Patch funktioniert" war fahrlässig.

### 3. Run D Merge-Save: Schema-Verletzung `shared_echoes`

**Datei:** `verify-runD-groupsplit-1344/save-merged-final.json`

Schema (`saveGame.v7.schema.json` Z.256-272) verlangt für `continuity.shared_echoes` Objekte mit `tag`-Feld:
```json
"shared_echoes": { "type": "array", "items": { "type": "object", "properties": { "tag": { "type": "string" } } } }
```

Merge-Save produziert:
```json
"shared_echoes": ["Mission 1: Lagerhaus gesichert (alle drei, solo)"]  ← String statt Objekt
```

→ **Save ist schema-invalid.** Meine Summary-Aussage "🟢 Schema-Normalisierung sauber" war falsch. Verifiziert: Der SL normalisiert zwar Character-Felder, aber produziert selbst schema-inkorrekte `shared_echoes`-Einträge.

### 4. Run D Merge: MOTH hat SYS 12 — Start-Attribut-Cap-Verletzung

**Regel** (`charaktererschaffung-grundlagen.md` Z.127): `Kein Startwert darf über 6 liegen`. Werte 7-10 nur durch Level-Progression, 11-14 nur durch Prestige.

**Beobachtung:** MOTH ist `Lvl 1, XP 9` (kein Prestige, keine Level-Progression) — hat aber `SYS: 12` im Merge-Save. Das ist ein Legacy-`sys_max`-Feld aus der Fixture, das der SL **als Attributwert übernommen** hat. Bei RAMPART (auch `sys_max: 14`) wurde korrekt auf `SYS: 0` normalisiert.

→ **Inkonsistente Normalisierung bei zwei strukturell identischen Input-Feldern.** Folgefehler: SL triggert dann W10-Heldenwürfel-Regel (`SYS 12 → W10`), baut also auf dem Bug weiter auf. Attribute-Summe MOTH = 31 statt 18.

### 5. W10-Schwelle-Drift ist systematisch, nicht einmalig

**Regel:** W10 ab Attribut ≥ 11, Heldenwürfel ab ≥ 14.

- **Run C T1:** `Kodex: INT 6 → W10 bei INT-Proben aktiv.` + Charaktertabelle zeigt gezielt `INT 6 | W10` (nicht Flavor, echt gesetzt)
- **Run D merge T1:** `MOTH SYS 12 → W10` — formal korrekt bezüglich der Schwelle 11, aber auf Basis von Finding #4
- Run B und A wenden die Regel korrekt an

→ **Der Würfeltyp ist Kernmechanik.** Wenn W10 bei Attribut 6 auslöst, werden Proben easier als vorgesehen. Das ist Balance-Bruch, kein Flavor.

**Revision:** In meinem ersten Summary stand "einmalig, KB-Retrieval-Artefakt". Das war Wunschdenken. Mindestens 2/4 Runs zeigen den Drift.

---

## 🟡 Drift-Findings (nicht blockend, aber Follow-up)

### 6. `level_history`-Platzierung nicht kanonisiert

- **Run A:** Root-Ebene des Save
- **Run D:** pro-Character
- **Run B:** gar nicht im Save

v7-Schema definiert das Feld nicht, `additionalProperties: true` lässt es durchrutschen. → **Dringend: Platzierung im Schema fixieren** (empfohlen: pro Character).

### 7. Stress-Skala verkehrt in allen Runs

Regel: **0-10**. Alle Runs: `Stress 3/5`, `0/5`, `0/6`. Nicht PR-Scope, aber omnipresent. Sollte in eigenes Pre-existierendes Drift-Ticket.

### 8. LP vs. HP in Spieler-Texten

AGENTS.md-Invariante: "**LP** (nicht HP) in spieler-sichtigen Texten". Save-JSON darf `hp` als technisches Feld nutzen.
- Run A T28, Run C T1: korrekt `LP: 12/12` ✓
- **Run D merge-chat T1 Charakterbogen (spieler-facing): `HP 11/12`, `HP 13/13`, `HP 10/10`** → Invariante verletzt.

### 9. Run A T27 Debrief signalisiert Level-Up-Pending nicht via Kodex

Run B liefert: `Kodex: Level-Up ausstehend — Save nach Wahl.` 
Run A liefert nichts vergleichbares. Gate griff nur weil Persona "Skip" sagte und SL improvisierte. → **Pflichtgate ist softer als angenommen.**

### 10. Run B Save hat kein `level_history`-Feld

Level-Up wurde gewählt ("+1 INT"), aber das Save enthält nichts. Zusammen mit Finding #2 zeigt das: **Persistenz ist Zufallslotterie, nicht deterministisch.**

---

## 🟢 Was weiterhin korrekt ist

- **Anti-Stacking-Rejektion (Run B T2):** Gold-Standard. `[7]`-KB-Ref, klare Ablehnung, Save-Reihenfolge explizit.
- **Load-Narrativ (Run C T1):** Funktional, Attribute aus Run-B-Save korrekt importiert.
- **Merge-Narrativ (Run D T1):** Literarisch stark, trotz Schema-/Attribut-Problemen.
- **HUD-Gate-Policy:** 19/44 vs. >80% vorher — quantitativ bestätigt.
- **Kodex-Typen A/B/C sauber unterscheidbar** in allen Runs.

---

## Invarianten-Status

- **Save-Schema v7:** ❌ Verletzung (Run D `shared_echoes` String statt Objekt)
- **Attribut-Cap 6 (Start):** ❌ Verletzung (Run D MOTH SYS 12)
- **W10 ≥ 11, Heldenwürfel ≥ 14:** ❌ Verletzung (Run C INT 6 → W10)
- **XP-Regel Phase 1 (1 XP = 1 Lvl):** ❌ Verletzung (Run A + D)
- **LP vs. HP in Spieler-Text:** ❌ Drift (Run D merge-chat)
- **Stress-Skala 0-10:** ❌ Drift (alle Runs)
- **Szenen 12/14:** ✓ OK (Run A: 12/12 Core, kein Rift)
- **ZWJ-Sequenzen Emojis:** ✓ OK (nicht von Critic verifiziert, aber nicht auffällig)

---

## Gesamt-Rating

**PR #2963 selbst:** 7/10 → **revidiert auf 6/10**
- Die drei Haupt-Patches funktionieren prinzipiell (Anti-Stacking, Save-Reihenfolge, HUD-Gate-Policy).
- Aber: `level_history`-Persistenz ist **nicht deterministisch**, und das hatten wir als zentrales Feature verkauft.
- Mission-Transition-Pflichtgate ist **softer als dokumentiert**.

**Umgebende SL-Qualität:** 5/10
- Systematische XP-Regel-Misinterpretation (nicht PR-Scope, aber jetzt sichtbar).
- W10-Schwelle wird sporadisch falsch angewendet.
- Schema-Invalide Saves beim Merge.
- Attribut-Cap-Verletzungen.

**Empfehlung:** PR #2963 **nicht zurücknehmen** (er verbessert mehr als er verschlimmert), aber **vier Follow-up-PRs** bilden:

1. **`level_history` im v7-Schema kanonisieren** (pro Character, nicht Root). Master-Prompt §F anpassen.
2. **`shared_echoes`-Normalisierung erzwingen** — Master-Prompt §D Merge-Sektion: Strings nicht akzeptieren, in `{tag, ...}` wrappen.
3. **XP-Regel-Klarstellung** — Master-Prompt §F-Debrief: explizit "Phase 1: Mission = Level", 10er-Balken verboten.
4. **W10-Schwellenprüfung-Härtung** — SL-Referenz §Probe: "Vor jeder Probe: Attribut ≥ 11 checken, sonst W6."

Kein Rollback nötig, aber die öffentliche Claim "Save/Reload + Group-Merge läuft rund" muss mindestens mit einem **"funktional, mit Gotchas"**-Asterisk versehen werden, bis die vier Follow-up-PRs durch sind.

---

## Lehren für den Workflow

- **Ich war zu optimistisch.** Der Worker hat korrekte Rohdaten produziert, aber ich habe bei der Summary-Erstellung "sieht gut aus" gesagt, ohne die Saves gegen das Schema zu validieren. Critic-Pass hat das aufgedeckt. **Regel fürs nächste Mal:** Bei jeder Save-Output-Bewertung → `jsonschema`-Validierung zwingend einbauen.
- **Der Critic hat seinen Platz im Workflow verdient.** Ohne ihn wäre ich mit einem 🟢🟢🟢-Summary zu Flo gegangen und wir hätten später im echten Playtest böse Überraschungen erlebt.
- **Worker-Truncation beim Summary:** Der Worker wurde genau beim Schreiben des `_verify-summary.md` abgebrochen. Symptom dass der Task zu groß war. Nächstes Mal Worker-Summary-Schreiben als separater Mini-Task (nicht im Haupt-Run) oder explizit frühzeitiges Zwischen-Flush.
