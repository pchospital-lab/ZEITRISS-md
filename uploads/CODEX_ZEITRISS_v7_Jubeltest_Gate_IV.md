# CODEX-BRIEFING — ZEITRISS v7 Jubeltest-Gate IV

**Ziel:** Den letzten technischen Blocker vor dem echten Jubeltest ziehen. Die Architektur steht; jetzt müssen Smoke-Script, kanonisches Save-Template, strict-v7-Schema, Arena-Checkpoint-Vertrag und v7-Fixtures dieselbe Wahrheit sprechen.

**Arbeitsmodus für Codex:** Repo vollständig lesen, dann patchen. Keine neuen Regeln erfinden. `meta/masterprompt_v6.md` und `systems/gameflow/speicher-fortsetzung.md` sind spielrelevanter Wissensspeicher; `scripts/smoke.sh` ist Pflichtcheck; `saveGame.v7.export.schema.json` ist der harte Exportvertrag.

---

## Executive Verdict

Fast-Jubeltest, aber **kein finaler Jubeltest**, solange `scripts/smoke.sh` kaputt formatiert ist und die alte kanonische Save-Beispielkopie in `speicher-fortsetzung.md` vom Masterprompt/strict Schema driftet.

Die guten Nachrichten:

- Masterprompt hat jetzt das starke v7-HQ-Save-Template inklusive `arena`, `pending_rewards`, `banked_rewards`, `first_wins`, `ui.intro_seen`, `dice`, `logs.hud`, `logs.psi`, `logs.arena_psi`.
- Strict-v7-Export-Schema enthält die wichtigen Nachzieher: `campaign.entry_choice_skipped`, `episode_start`, `episode_end`, `logs.hud`, `logs.psi`, `logs.arena_psi`, `ui.intro_seen`, `ui.dice`, `arena.first_wins` als Objekt, `pending_rewards`, `banked_rewards`.
- Split/Merge, Personal-Export, Arena-Checkpoint und Px-Sprachwatchguards existieren.

Der Blocker:

- `scripts/smoke.sh` ist faktisch auf zwei physische Zeilen kollabiert. Zeile 0 enthält Shebang **plus fast alle Kommandos** auf derselben Kommentarzeile; Zeile 1 beginnt mitten in einem Kommentartext (`verankerte HQ-Projektion) node ...`). `bash scripts/smoke.sh` kann so nicht der verlässliche Gatekeeper sein.

---

## Patch 1 — `scripts/smoke.sh` reparieren

### Befund

Aktueller Raw-Zustand zeigt nur zwei physische Zeilen. Beispiel:

```bash
#!/usr/bin/env bash export LANG=C.UTF-8 export LC_ALL=C.UTF-8 set -euo pipefail ...
verankerte HQ-Projektion) node tools/test_physicality_watchguard.js ...
```

Das ist gefährlich, weil:

1. Die erste Zeile wird von Bash als Kommentar/Shebang-Zeile behandelt; die darin enthaltenen Kommandos laufen nicht sauber als einzelne Kommandos.
2. Die zweite Zeile startet syntaktisch mitten in einem Satz und enthält eine schließende Klammer.
3. Selbst wenn einzelne Grep-/Coverage-Tests den Text noch finden, ist das Smoke-Gate als ausführbares Script nicht vertrauenswürdig.

### Sollzustand

`smoke.sh` muss echte Zeilenumbrüche haben:

```bash
#!/usr/bin/env bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"
...
python3 tools/lint_runtime.py
python3 tools/lint_debrief_trace.py
...
node tools/test_v7_smart_merge_3_2.js > out/v7_smart_merge_3_2.log
grep "v7-smart-merge-3-2-ok" out/v7_smart_merge_3_2.log
...
echo ""
echo "All smoke checks passed."
```

### Konkrete Aufgaben

1. `scripts/smoke.sh` neu formatieren, nicht nur kosmetisch: jedes Kommando auf eigene Zeile, Kommentare auf eigene Zeile, keine Monsterzeilen.
2. `bash -n scripts/smoke.sh` muss grün sein.
3. `bash scripts/smoke.sh` muss danach wirklich alle Tests ausführen.
4. Sicherstellen, dass die neuen Watchguards weiter enthalten sind:
   - `tools/test_v7_smart_merge_3_2.js`
   - `tools/test_arena_round_checkpoint.js`
   - `tools/test_v7_personal_export.js`
   - `tools/test_px_language_watchguard.js`
   - `tools/test_save_budget_watchguard.js`

### Neuen Regressionstest ergänzen

Neue Datei: `tools/test_smoke_script_sanity.js`

Mindestchecks:

```js
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const smoke = path.join(ROOT, 'scripts', 'smoke.sh');
const text = fs.readFileSync(smoke, 'utf8');
const lines = text.split(/\r?\n/);

assert.strictEqual(lines[0], '#!/usr/bin/env bash', 'smoke.sh: Shebang muss allein in Zeile 1 stehen.');
assert.ok(lines.length >= 80, `smoke.sh: zu wenige physische Zeilen (${lines.length}) — vermutlich kollabiert.`);
assert.ok(!/^#!\/usr\/bin\/env bash\s+export\s+LANG/.test(lines[0]), 'smoke.sh: Shebang enthält Kommandos.');
assert.ok(!text.includes('verankerte HQ-Projektion) node'), 'smoke.sh: Kommentar/Text und node-Befehl sind kollabiert.');
assert.ok(text.includes('set -euo pipefail'), 'smoke.sh: set -euo pipefail fehlt.');
assert.ok(lines.every((line) => line.length < 500), 'smoke.sh: mindestens eine Monsterzeile >500 Zeichen.');
execFileSync('bash', ['-n', smoke], { stdio: 'pipe' });
console.log('smoke-script-sanity-ok');
```

Dann in `scripts/smoke.sh` aufnehmen:

```bash
node tools/test_smoke_script_sanity.js > out/smoke_script_sanity.log
grep "smoke-script-sanity-ok" out/smoke_script_sanity.log
```

---

## Patch 2 — `speicher-fortsetzung.md`: alte kanonische Save-Kopie entschärfen

### Befund

`meta/masterprompt_v6.md` enthält mittlerweile das vollständige, gute v7-HQ-Save-Template. In `systems/gameflow/speicher-fortsetzung.md` gibt es aber später noch einen Abschnitt **„Kanonisches Save-Exportformat (v7, einziges Format)”** mit eigenem JSON-Beispiel.

Dieses Beispiel driftet vom Masterprompt/strict Schema:

- `campaign.entry_choice_skipped`, `episode_start`, `episode_end` fehlen.
- `logs.hud`, `logs.psi`, `logs.arena_psi` fehlen.
- `ui.intro_seen` und `ui.dice.debug_rolls` fehlen.
- `arena` ist ein alter Minimalblock ohne `active`, `phase`, `queue_state`, `contract_id`, `streak`, `pending_rewards`, `banked_rewards`.

Das ist für LLMs gefährlich, weil der Abschnitt selbst „kanonisch” sagt. Genau solche Beispiele werden im Spielbetrieb gerne imitiert.

### Sollentscheidung

**Nur ein kopierfähiges Save-Template im gesamten Wissensspeicher:** das Masterprompt-v7-HQ-Template.

`speicher-fortsetzung.md` darf Save-Vertrag, Felder, Importpfade, Merge-Regeln und Budgets erklären, aber kein zweites kopierfähiges v7-Exportbeispiel neben dem Masterprompt führen.

### Konkrete Aufgaben

In `systems/gameflow/speicher-fortsetzung.md`:

1. Den Abschnitt „Kanonisches Save-Exportformat (v7, einziges Format)” umbauen.
2. Den JSON-Block entweder vollständig entfernen oder exakt durch eine kurze Referenz ersetzen:

```md
### Kanonisches Save-Exportformat (v7, einziges Format)

Das einzige kopierfähige `!save`-Exporttemplate steht im Masterprompt §F.
Diese Datei definiert Feldbedeutung, Import-/Migrationsregeln, Split/Merge und Budgets.
Kein JSON-Beispiel in `speicher-fortsetzung.md` darf bei `!save` imitiert werden.
```

3. Alle Legacy-/Migrationsbeispiele härter markieren:

```md
IMPORT-ONLY / NICHT KOPIEREN / KEIN !save-BEISPIEL
```

4. Optional: große Legacy-JSON-Blöcke in einen Appendix schieben oder als kompaktes Schema-Mapping statt JSON darstellen.

### Watchguard ergänzen

In `tools/test_v7_schema_consistency.js` oder neuer Datei `tools/test_v7_canonical_template_drift.js`:

- Fail, wenn `speicher-fortsetzung.md` nach Überschrift `Kanonisches Save-Exportformat` einen kopierfähigen ```json-Block mit `{ "v": 7` enthält.
- Fail, wenn `speicher-fortsetzung.md` einen v7-JSON-Block mit `"arena": { "previous_mode"` aber ohne `"active"`, `"phase"`, `"queue_state"` enthält.

---

## Patch 3 — Arena-Persistenzvertrag final glätten

### Befund

`speicher-fortsetzung.md` sagt im Arena-Persistenzvertrag noch:

- persistiert werden `wins_player`, `wins_opponent`, `tier`, `match_policy`, `previous_mode`, `resume_token`, `rewarded_runs_this_contract`, `first_wins`, `defeated_types`, `last_reward_episode`.
- Laufzeit-/Queue-Felder `active`, `phase`, `queue_state` gelten als transient.

Der Masterprompt sagt inzwischen korrekt: Nach abgeschlossener Runde/Serie ist HQ-Arena-Lounge savebar und muss `pending_rewards`, `banked_rewards`, `first_wins`, `contract_id`, `streak` persistieren.

### Sollvertrag

- **Nicht speichern:** laufende Matchphysik, Zone, Staging-Helfer, temporäre SG-/Damage-Budgets.
- **Speichern:** Arena-Karriere + HQ-sicherer Sentinel-Status.

Kanonischer Satz:

> Arena speichert Karriere und HQ-sicheren Checkpoint, niemals laufende Matchphysik. `active`, `phase` und `queue_state` werden beim Export als normalisierte Sentinel-Felder geschrieben (`active=false`, `phase/queue_state=idle|completed`), damit der nächste Chat weiß: Arena ist nicht live, aber der Push/Cashout-Zustand ist lesbar.

### Konkrete Aufgaben

In `speicher-fortsetzung.md` Arena-Persistenzliste ergänzen:

```md
Persistiert werden:
`active`, `phase`, `queue_state` als HQ-safe Sentinel-Felder,
`mode`, `tier`, `previous_mode`, `resume_token`, `contract_id`, `streak`,
`pending_rewards`, `banked_rewards`, `rewarded_runs_this_contract`,
`first_wins`, `defeated_types`, `last_reward_episode`,
`wins_player`, `wins_opponent`, `match_policy`.
```

Und klarstellen:

```md
Während Queue/Match/Run sind Save-Versuche gesperrt. Erst nach Rückkehr in die HQ-Arena-Lounge wird der Arena-Block normalisiert und exportiert.
```

---

## Patch 4 — Strict-v7-Export-Schema minimal härten

### Befund

`saveGame.v7.export.schema.json` hat die großen Korrekturen bekommen. Gut. Aber der Root-Block `required` enthält aktuell nicht `arena`, obwohl der Masterprompt sagt: „alle Felder Pflicht, kein Feld weglassen”, und das Template immer `arena` schreibt.

### Sollzustand

Da `arena` ein normaler HQ-sicherer Defaultblock ist und PvP-only-Progression gleichwertig sein soll, sollte `arena` im strict Export Root-Pflichtfeld sein.

Patch:

```json
"required": [
  "v", "zr", "save_id", "parent_save_id", "merge_id", "branch_id",
  "campaign", "characters", "economy", "logs", "summaries",
  "continuity", "arc", "ui", "arena"
]
```

Zusätzlich empfehlenswert:

- `continuity.roster_echoes.maxItems = 5`, Items brauchen `char_id`.
- `continuity.shared_echoes.maxItems = 6`, Items brauchen `tag`.
- `continuity.convergence_tags.maxItems = 4`.
- `npc_roster.maxItems = 6`, `active_npc_ids.maxItems = 4`.
- `logs.trace.maxItems = 64`, `logs.market.maxItems = 24`, `logs.artifact_log.maxItems = 32`, `logs.notes.maxItems = 24`.
- `arc.questions.maxItems = 18`, `arc.hooks.maxItems = 18`.
- `characters[].history.milestones.maxItems = 20`.

Diese Budgets stehen in der Doku; das strict Schema sollte sie spiegeln.

---

## Patch 5 — v7-Fixtures: strict oder eindeutig Fragment

### Befund

Mehrere `savegame_v7_*.json`-Fixtures sind noch minimale Watchguard-Objekte, keine vollständigen strict-v7-Exports. Beispiele:

- `savegame_v7_arena_round_checkpoint.json`: Charakter enthält nur `id`, `name`, `lvl`, `xp`, `wallet`; strict verlangt `callsign`, `rank`, `origin`, `attr`, `lp`, `lp_max`, `stress`, `has_psi`, `sys_installed`, `talents`, `equipment`, `implants`, `history`, `carry`, `quarters_stash`, `vehicles`, `reputation`, `level_history`.
- `savegame_v7_split_3_2_merge.json`: fünf Characters nur mit `id`/`wallet`.
- `savegame_v7_personal_export_from_group.json`: Character ist näher dran, aber ebenfalls nicht vollständig strict.
- `savegame_v7_5er_hq_highlevel.json`: fünf Highlevel-Chars nur mit Minimalfeldern.

Das kann als Testfragment funktionieren, aber als Datei mit `savegame_v7_` im Namen ist es LLM-Futter. Wenn Agenten oder Modelle daraus lernen, verwässern sie den Save-Vertrag.

### Sollentscheidung

Eine von zwei Varianten wählen:

**Variante A — bevorzugt:** Alle `savegame_v7_*.json`-Fixtures zu vollständigen strict-v7-Saves machen. Für Testzwecke können Placeholder-Werte verwendet werden, aber alle Pflichtfelder müssen vorhanden sein.

**Variante B:** Fragment-Fixtures umbenennen, z. B. `v7_fragment_split_3_2_merge.json`, und Tests entsprechend anpassen. Dann darf `savegame_v7_*.json` nur für wirklich vollständige strict Exports stehen.

Ich empfehle Variante A, weil die Beispiele dann selbst als gutes LLM-Futter dienen.

### Neuer Test

Neue Datei: `tools/test_v7_export_fixture_strictness.js`

Mindestchecks ohne externe Dependencies:

- Für jede `internal/qa/fixtures/savegame_v7_*.json`:
  - Root enthält alle strict Root-Felder inklusive `arena`.
  - Jedes `characters[]`-Item enthält alle strict Character-Pflichtfelder.
  - `logs` enthält `trace`, `hud`, `psi`, `arena_psi`, `market`, `artifact_log`, `notes`, `flags`.
  - `ui` enthält `intro_seen` und `dice.debug_rolls`.
  - `arena` enthält alle Pflichtfelder, `first_wins` ist Objekt.
  - Budgets werden eingehalten.

Oder, falls Variante B gewählt wird:

- `savegame_v7_*.json` muss strict sein.
- `v7_fragment_*.json` darf fragmentarisch sein, muss aber im Dateinamen klar als Fragment erkennbar sein.

---

## Patch 6 — Smoke-Coverage-Test robuster machen

`tools/test_watchguard_smoke_coverage.js` prüft aktuell, ob Watchguard-Dateinamen im Smoke-Text vorkommen. Das findet auch kollabierte Monsterzeilen. Ergänzen:

- Smoke-Script muss ausführbar parsebar sein: `bash -n scripts/smoke.sh`.
- Mindestens 80 physische Zeilen.
- Keine Zeile > 500 Zeichen.
- Shebang allein in Zeile 1.

Kann in `test_smoke_script_sanity.js` ausgelagert werden, aber `test_watchguard_smoke_coverage.js` darf zusätzlich prüfen, dass Smoke nicht kollabiert ist.

---

## Akzeptanzkriterien

Codex ist fertig, wenn alle Punkte stimmen:

```bash
bash -n scripts/smoke.sh
bash scripts/smoke.sh
```

und Smoke enthält erfolgreich:

```text
smoke-script-sanity-ok
v7-schema-consistency-ok
v7-smart-merge-3-2-ok
arena-round-checkpoint-ok
v7-personal-export-ok
px-language-watchguard-ok
save-budget-watchguard-ok
All smoke checks passed.
```

Zusätzlich manuell prüfen:

1. `meta/masterprompt_v6.md` bleibt das einzige kopierfähige v7-`!save`-Template.
2. `speicher-fortsetzung.md` enthält kein zweites driftendes Exporttemplate.
3. `saveGame.v7.export.schema.json` verlangt `arena` im Root.
4. Alle `savegame_v7_*.json`-Fixtures sind entweder strict vollständig oder klar als Fragment umbenannt.
5. Arena-Checkpoint: Nach Runde/Serie HQ-savebar mit `pending_rewards`, aber nie während Queue/Match.
6. Split/Merge: 5 Spieler, 3/2-Branches, Rejoin mit Echos und Merge-Tabelle.
7. Personal-Export: genau ein Spielercharakter plus kompakte Gruppenechos, keine anderen Charakterbögen.

---

## Erwartete Commit-Message

```text
fix(v7): repariere smoke-gate und synchronisiere kanonischen save-vertrag

## Was
- scripts/smoke.sh wieder als ausführbares mehrzeiliges Bash-Script hergestellt.
- Smoke-Sanity-Watchguard ergänzt.
- Driftendes v7-Exportbeispiel in speicher-fortsetzung.md entfernt/entschärft.
- Arena-Persistenzvertrag auf HQ-safe Checkpoint + Pending/Banked synchronisiert.
- Strict-v7-Schema und v7-Fixtures gegen Masterprompt-Template abgeglichen.

## Warum
Der Save-/Merge-Contract ist spielerisch fast final, aber Smoke war als Gatekeeper kaputt formatiert und speicher-fortsetzung.md enthielt noch ein zweites veraltetes v7-Beispiel. Beides gefährdet LLM-Drift und CI-Vertrauen kurz vor dem Jubeltest.

## Wichtige Entscheidungen
- Masterprompt §F bleibt das einzige kopierfähige !save-Template.
- Arena speichert Karriere + HQ-safe Sentinel, niemals laufende Matchphysik.
- savegame_v7_*-Fixtures sind entweder strict vollständig oder klar als Fragmente benannt.

## Verifikation
- bash -n scripts/smoke.sh
- bash scripts/smoke.sh
```
