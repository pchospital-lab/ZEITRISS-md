# CODEX-BRIEFING — ZEITRISS v7 Jubeltest-Gate V

## Ziel

ZEITRISS ist designseitig jetzt auf Jubeltest-Niveau. Dieser Pass ist **kein Redesign** mehr. Er soll nur die letzten formalen Gate-Blocker entfernen, damit der finale Jubeltest ehrlich vergeben werden kann.

Hauptziel: **Smoke-Gate wieder wirklich ausführbar machen und die v7-Save-Vertragsprosa an Masterprompt + strict Schema angleichen.**

---

## Aktueller Befund

### Grün

- Save = Charakterbogen / Weltanker / portabler Besitz ist im README sauber gesetzt.
- Masterprompt §F enthält jetzt ein vollständiges v7-Template mit `arena`, `pending_rewards`, `banked_rewards`, `first_wins`, `logs.hud`, `logs.psi`, `logs.arena_psi`, `ui.intro_seen`, `ui.dice.debug_rolls`, `campaign.entry_choice_skipped`, `episode_start` und `episode_end`.
- Strict-v7-Export-Schema ist stark nachgezogen: `first_wins` ist Objekt, `arena` ist Root-Pflichtblock, neue Logs/UI/Campaign-Felder sind enthalten.
- `speicher-fortsetzung.md` verweist beim einzigen kopierfähigen Save-Template auf den Masterprompt statt ein zweites JSON-Template zu führen.
- Encounter-/Px-Drift ist weitgehend bereinigt: Fehler erzeugen Heat/Druck/Timeline-Echo, Px bleibt Belohnungs-/Resonanzfortschritt.
- Split/Merge, Personal-Export, Arena-Checkpoint und Save-Budget haben eigene Watchguards/Fixures.

### Noch blockierend

1. `scripts/smoke.sh` ist im Raw-Content weiterhin praktisch kollabiert. GitHub rendert die Datei im Web mit vielen Zeilen, aber Raw liefert fast alles als eine physische Zeile plus ein Restfragment. Für `bash scripts/smoke.sh` ist das ein Gate-Blocker.
2. `systems/gameflow/speicher-fortsetzung.md` enthält im Abschnitt **v7-Export-Pflichtfelder** noch eine veraltete Feldliste. Sie fehlt hinter Masterprompt und Schema zurück.
3. `gameplay/kampagnenstruktur.md` beschreibt im Arena-Persistenzvertrag noch `arena.active`, `arena.phase` und `arena.queue_state` pauschal als transient, obwohl sie als HQ-safe Sentinel-Felder im v7-Save stehen müssen.
4. `meta/masterprompt_v6.md` enthält nach dem vollständigen Pflicht-Template noch die alte Formulierung „Arena nur wenn genutzt“. Das widerspricht dem strict Schema, in dem `arena` Root-Pflicht ist.

---

## 1. `scripts/smoke.sh` hart fixen: LF, bash-parsebar, sanity-guard

### Problem

Raw-GitHub liefert `scripts/smoke.sh` mit nur zwei physischen Zeilen. Damit ist Zeile 1 faktisch ein gigantischer Kommentar ab `#!/usr/bin/env bash ...`; Zeile 2 beginnt mitten in einem Kommentar-/Textfragment. Auf Linux ist das nicht zuverlässig ausführbar.

### Patch

1. Datei auf echte LF-Zeilen normalisieren.
2. `chmod +x scripts/smoke.sh` beibehalten.
3. `tools/test_smoke_script_sanity.js` früh im Smoke verdrahten.
4. `.gitattributes` ergänzen oder erweitern, damit Shell-Skripte immer LF behalten.

Empfohlener Fix:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('scripts/smoke.sh')
b = p.read_bytes()
b = b.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
p.write_bytes(b)
PY

chmod +x scripts/smoke.sh
```

Danach in `scripts/smoke.sh` direkt nach `python3 -m unittest -q` ergänzen:

```bash
# Smoke-Skript-Sanity (Shebang/Zeilenumbrüche/bash -n)
mkdir -p out
node tools/test_smoke_script_sanity.js > out/smoke_script_sanity.log
grep smoke-script-sanity-ok out/smoke_script_sanity.log
```

Falls `.gitattributes` fehlt oder Shell-Skripte nicht abdeckt:

```gitattributes
scripts/*.sh text eol=lf
*.sh text eol=lf
```

### Verifikation

```bash
python3 - <<'PY'
from pathlib import Path
b = Path('scripts/smoke.sh').read_bytes()
text = b.decode('utf-8')
print('LF=', b.count(b'\n'), 'CR=', b.count(b'\r'))
assert b.count(b'\r') == 0
assert b.count(b'\n') >= 80
assert text.splitlines()[0] == '#!/usr/bin/env bash'
assert max(map(len, text.splitlines())) < 500
PY

bash -n scripts/smoke.sh
node tools/test_smoke_script_sanity.js
bash scripts/smoke.sh
```

Akzeptanz: alle drei Kommandos grün, `All smoke checks passed.` sichtbar.

---

## 2. `speicher-fortsetzung.md`: v7-Export-Pflichtfelder aktualisieren

### Problem

Im Abschnitt **v7-Export-Pflichtfelder (kanonisch, nicht Runtime-Bridge)** steht noch eine alte Feldliste. Sie fehlt aktuell hinter Masterprompt §F und `saveGame.v7.export.schema.json` zurück.

Aktuell fehlen dort u. a.:

- `campaign.entry_choice_skipped`
- `campaign.episode_start`
- `campaign.episode_end`
- `logs.hud[]`
- `logs.psi[]`
- `logs.arena_psi[]`
- `ui.intro_seen`
- `ui.dice.debug_rolls`
- vollständiger `arena`-Pflichtblock mit `queue_state`, `contract_id`, `streak`, `pending_rewards`, `banked_rewards`, `first_wins` als Objekt

Außerdem steht weiter sinngemäß `arena?` / „nur wenn Arena genutzt“, obwohl der strict Export `arena` als Pflicht-Root-Block führt.

### Patch-Zieltext

Ersetze die dortige Pflichtfeldliste durch eine Version auf Stand des Masterprompt-Templates:

```text
v, zr, save_id, parent_save_id, merge_id, branch_id,
campaign { episode, mission, px, px_state, mode, rift_seeds[], entry_choice_skipped, episode_start, episode_end },
characters[] { id, name, callsign, rank, lvl, xp, origin, attr, lp, lp_max, stress, has_psi, sys_installed, talents[], equipment[], implants[], history, carry[], quarters_stash[], vehicles, reputation, wallet, level_history },
economy { hq_pool },
logs { trace[], hud[], psi[], arena_psi[], market[], artifact_log[], notes[], flags { runtime_version, chronopolis_unlocked, imported_saves[], duplicate_branch_detected, duplicate_character_detected, continuity_conflicts[] } },
summaries { summary_last_episode, summary_last_rift, summary_active_arcs },
continuity { last_seen { mode, episode, mission, location }, split, roster_echoes[], shared_echoes[], convergence_tags[], npc_roster[], active_npc_ids[] },
arc { factions, questions[], hooks[] },
ui { gm_style, suggest_mode, action_mode, intro_seen, dice { debug_rolls }, contrast, badge_density, output_pace, voice_profile },
arena { active, phase, queue_state, mode, tier, previous_mode, resume_token, contract_id, streak, pending_rewards, banked_rewards, rewarded_runs_this_contract, first_wins{}, defeated_types[], last_reward_episode, wins_player, wins_opponent, match_policy }
```

Wichtiger Satz:

```text
Der `arena`-Block ist im v7-Export Pflicht. Wenn Arena nie genutzt wurde, wird der Default-Idle-Block geschrieben; nur laufende Matchphysik bleibt runtime-only.
```

### Zusätzlich ersetzen

Suche in `systems/gameflow/speicher-fortsetzung.md` nach:

```text
arena?
```

und ersetze die alte Kurzform durch:

```text
arena (Pflichtblock; Default `active=false`, `phase=idle`, `queue_state=idle`; bei Arena-Nutzung persistiert Karriere-/Checkpoint-Kern)
```

---

## 3. `kampagnenstruktur.md`: Arena-Persistenzvertrag präzisieren

### Problem

Der Arena-Persistenzvertrag sagt noch:

```text
Transiente Match-/Queue-Felder (`arena.active`, `arena.phase`, `arena.queue_state`, ... ) gelten als Laufzeitdaten.
```

Das ist zu grob. Richtig ist:

- Live-Queue/Live-Match-Zustände sind runtime-only.
- HQ-safe Sentinel-Felder werden gespeichert.
- Nach abgeschlossener Runde/Serie ist Save in der HQ-Arena-Lounge erlaubt.
- Pending/Banked/Contract/Streak sind persistenter Karriere-/Checkpoint-Kern.

### Patch-Zieltext

Ersetze den Persistenzvertrag im Arena-Abschnitt sinngemäß durch:

```text
#### Persistenzvertrag (Arena)
Persistiert werden der Arena-Karrierekern und ein HQ-sicherer Checkpoint:
`arena.active=false`, `arena.phase=idle|completed`, `arena.queue_state=idle|completed`, `arena.previous_mode`, `arena.resume_token`, `arena.contract_id`, `arena.streak`, `arena.pending_rewards`, `arena.banked_rewards`, `arena.rewarded_runs_this_contract`, `arena.first_wins`, `arena.defeated_types`, `arena.last_reward_episode`, `arena.wins_player|wins_opponent|tier` und `arena.match_policy`.

Runtime-only bleiben nur laufende Matchphysik und Live-Queue-Zustände:
`queue_state=searching|matched|staging|active`, Arena-Zone, Gegnerzustände, laufende Rundentimer, temporäre Budgets und aktive Effekte.

Nach abgeschlossener Runde oder Serie kehrt die Gruppe in die HQ-Arena-Lounge zurück. Dort ist `!save` erlaubt. Der Save enthält Pending/Banked/Push/Cashout-Status, aber niemals laufende Matchphysik.
```

Goldener Satz:

```text
Arena speichert Karriere und HQ-sicheren Checkpoint, niemals laufende Matchphysik.
```

---

## 4. Masterprompt-Restdrift: „Arena nur wenn genutzt“ entfernen

### Problem

Masterprompt §F hat jetzt ein vollständiges Pflicht-Template mit `arena`, danach steht aber noch die alte Regel:

```text
Arena nur wenn genutzt: mindestens Serienstand/Tier plus Persistenzkern ...
```

Das widerspricht dem strict Export-Schema, in dem `arena` Root-Pflicht ist.

### Patch-Zieltext

Ersetze diese Formulierung durch:

```text
- `arena` ist im v7-Export immer vorhanden. Ohne Arena-Nutzung schreibt die KI-SL den Default-Idle-Block (`active=false`, `phase=idle`, `queue_state=idle`, `pending_rewards=0`, `banked_rewards=0`, `first_wins={}`). Wenn Arena genutzt wurde, bleiben Karrierekern und HQ-sicherer Checkpoint persistent. Live-Queue und laufende Matchphysik werden nie gespeichert.
```

---

## 5. Watchguards erweitern

### 5.1 Neuer Watchguard: v7-Export-Feldliste in `speicher-fortsetzung.md`

Lege an:

```text
tools/test_v7_export_fieldlist_watchguard.js
```

Der Test soll mindestens prüfen:

- `systems/gameflow/speicher-fortsetzung.md` enthält:
  - `entry_choice_skipped`
  - `episode_start`
  - `episode_end`
  - `logs.hud`
  - `logs.psi`
  - `logs.arena_psi`
  - `ui.intro_seen`
  - `ui.dice`
  - `pending_rewards`
  - `banked_rewards`
  - `contract_id`
  - `streak`
  - `first_wins{}` oder `first_wins`
  - Satz: `arena` ist Pflichtblock / Default-Idle-Block
- Die aktive v7-Feldliste enthält nicht mehr `arena?`.

Minimal-Skeleton:

```js
const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const sf = fs.readFileSync(path.join(ROOT, 'systems/gameflow/speicher-fortsetzung.md'), 'utf8');

const required = [
  'entry_choice_skipped',
  'episode_start',
  'episode_end',
  'logs.hud',
  'logs.psi',
  'logs.arena_psi',
  'ui.intro_seen',
  'ui.dice',
  'pending_rewards',
  'banked_rewards',
  'contract_id',
  'streak',
  'first_wins',
];

for (const needle of required) {
  assert.ok(sf.includes(needle), `speicher-fortsetzung.md: '${needle}' fehlt in der v7-Feldliste.`);
}

assert.ok(/arena[^\n]{0,80}(Pflichtblock|immer vorhanden|Default-Idle)/i.test(sf), 'arena muss als Pflichtblock/Default-Idle beschrieben sein.');
assert.ok(!/arena\?/.test(sf), 'arena? ist im aktiven v7-Vertrag verboten — arena ist Pflichtblock.');

console.log('v7-export-fieldlist-watchguard-ok');
```

In `scripts/smoke.sh` einhängen:

```bash
# v7-Export-Feldlisten-Watchguard
node tools/test_v7_export_fieldlist_watchguard.js > out/v7_export_fieldlist_watchguard.log
grep "v7-export-fieldlist-watchguard-ok" out/v7_export_fieldlist_watchguard.log
```

### 5.2 Arena-Watchguard erweitern

Erweitere `tools/test_arena_round_checkpoint.js` oder lege einen zusätzlichen Doku-Watchguard an, der in `gameplay/kampagnenstruktur.md` prüft:

- Persistenzvertrag nennt `pending_rewards`.
- Persistenzvertrag nennt `banked_rewards`.
- Persistenzvertrag nennt `contract_id`.
- Persistenzvertrag nennt `streak`.
- Text enthält sinngemäß `HQ-sicherer Checkpoint` oder `HQ-safe`.
- Text enthält nicht mehr die alte pauschale Aussage, dass `arena.active`, `arena.phase`, `arena.queue_state` komplett transient seien.

---

## 6. Grep-Checks vor Commit

```bash
grep -n "arena?" systems/gameflow/speicher-fortsetzung.md meta/masterprompt_v6.md gameplay/kampagnenstruktur.md || true
grep -n "Arena nur wenn genutzt" meta/masterprompt_v6.md systems/gameflow/speicher-fortsetzung.md || true
grep -n "Transiente Match-/Queue-Felder.*arena.active" gameplay/kampagnenstruktur.md || true
grep -n "entry_choice_skipped\|logs.arena_psi\|pending_rewards\|banked_rewards" systems/gameflow/speicher-fortsetzung.md
```

Akzeptanz:

- Die ersten drei Greps liefern keine aktiven Vertragsstellen mehr.
- Der letzte Grep findet die neuen v7-Felder.

---

## 7. Verifikationsplan

Pflicht:

```bash
python3 - <<'PY'
from pathlib import Path
b = Path('scripts/smoke.sh').read_bytes()
text = b.decode('utf-8')
print('LF=', b.count(b'\n'), 'CR=', b.count(b'\r'))
assert b.count(b'\r') == 0
assert b.count(b'\n') >= 80
assert text.splitlines()[0] == '#!/usr/bin/env bash'
assert max(map(len, text.splitlines())) < 500
PY

bash -n scripts/smoke.sh
node tools/test_smoke_script_sanity.js
node tools/test_v7_export_fieldlist_watchguard.js
bash scripts/smoke.sh
```

Optional, falls Zeit:

```bash
node tools/test_arena_round_checkpoint.js
node tools/test_v7_schema_consistency.js
node tools/test_v7_smart_merge_3_2.js
node tools/test_v7_personal_export.js
node tools/test_save_budget_watchguard.js
```

---

## 8. Akzeptanzkriterien für den Jubeltest

Der Jubeltest darf erst vergeben werden, wenn:

1. `scripts/smoke.sh` echte LF-Zeilen hat und `bash -n` besteht.
2. `tools/test_smoke_script_sanity.js` grün ist.
3. `bash scripts/smoke.sh` grün ist.
4. `speicher-fortsetzung.md` dieselben v7-Pflichtfelder nennt wie Masterprompt/strict Schema.
5. `arena` überall als Pflichtblock/Default-Idle verstanden wird.
6. Arena-Persistenz überall dieselbe Wahrheit sagt:
   - Karriere + HQ-safe Checkpoint persistent.
   - Live-Queue/Matchphysik runtime-only.
7. Es keine zweite kopierfähige v7-Save-Template-Kopie außerhalb Masterprompt §F gibt.

---

## Commit-Message-Vorschlag

```text
fix(save-v7): repariere Smoke-Gate und gleiche v7-Vertragsprosa ab

## Was
- scripts/smoke.sh auf echte LF-Zeilen normalisiert und Smoke-Skript-Sanity eingebunden.
- v7-Export-Feldliste in speicher-fortsetzung.md an Masterprompt/strict Schema angepasst.
- Arena-Persistenzvertrag präzisiert: Karriere + HQ-safe Checkpoint persistent, Live-Matchphysik runtime-only.
- Masterprompt-Restdrift zu "Arena nur wenn genutzt" entfernt.
- Watchguard für v7-Feldlisten-/Arena-Drift ergänzt.

## Warum
Der Spielvertrag ist designseitig final, aber der Jubeltest war durch ein kaputtes Smoke-Gate und alte v7-Feldlisten formal blockiert. LLMs und Repo-Agenten brauchen eine einzige Wahrheit für v7-Saves.

## Wichtige Entscheidungen
- `arena` ist im v7-Export immer vorhanden; ungenutzt als Default-Idle-Block.
- `active/phase/queue_state` sind nur live transient, aber als HQ-safe Sentinel speicherbar.
- `pending_rewards`/`banked_rewards` gehören zum Arena-Karrierekern.
- Smoke-Sanity prüft Zeilenumbrüche, Shebang und `bash -n`.

## Verifikation
- bash -n scripts/smoke.sh
- node tools/test_smoke_script_sanity.js
- node tools/test_v7_export_fieldlist_watchguard.js
- bash scripts/smoke.sh
```

---

## Nicht anfassen

- Kein Redesign von Save/Merge.
- Keine Erweiterung der JSON-Größe.
- Keine neuen Storysysteme.
- Keine neuen Persistenzmonster.
- Keine zweite Save-Template-Kopie.

Dieser Pass ist nur der TÜV-Stempel: **Dateiformat, SSOT-Prosa, Arena-Vertrag, Smoke-Gate.** Danach ist der Jubeltest verdient.
