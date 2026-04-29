# Codex-Briefing — ZEITRISS v7 Finalgate VII

## Ziel

ZEITRISS ist inhaltlich auf Jubeltest-Niveau. Bitte **nicht redesignen**. Dieser Pass ist ein harter technischer Finalgate-Pass, damit Smoke, Klartextvertrag und Watchguards wirklich dieselbe Wahrheit sprechen.

Aktueller Befund des Reviews:

- Save-/Merge-Vision sitzt.
- Masterprompt-v7-Template ist stark.
- Strict-v7-Schema ist deutlich nachgezogen, inklusive `arena`, `logs.hud`, `logs.psi`, `logs.arena_psi`, `ui.intro_seen`, `ui.dice`, `psi_heat`, `pp`, `psi_abilities` und `artifact`.
- Arena/PvP ist im Gameplay-Vertrag fast final.
- Blocker bleiben: **EOL/Smoke**, **veraltete aktive v7-Pflichtfeldliste**, **alter Arena-Absatz in `speicher-fortsetzung.md`**, **zu schwacher Px-/Encounter-Watchguard**, plus eine **Load-Formulierung**, die HQ-only-Save verwässern kann.

Wenn diese Punkte sauber gefixt sind und `bash scripts/smoke.sh` wirklich grün läuft, ist der nächste Review ein Jubeltest-Kandidat.

---

## 0. Branch & Arbeitsweise

```bash
git checkout -b codex/finalgate-vii-smoke-contract-cleanup
```

Arbeite minimalinvasiv. Keine neuen Großmechaniken, keine neue Architektur. Es geht nur um Gate-Fähigkeit und SSOT-Synchronität.

---

## 1. Harte Blockade: `scripts/smoke.sh` ist im Raw-Download kollabiert

### Befund

Raw-Download zeigt weiterhin faktisch zwei physische LF-Zeilen. Zeile 1 enthält Shebang plus fast alle Befehle; Zeile 2 beginnt mitten im Kommentarfragment:

```text
verankerte HQ-Projektion) node tools/test_physicality_watchguard.js ...
```

Das ist wahrscheinlich CR-only oder ein ähnliches Zeilenendproblem. Für Bash ist das fatal:

- `bash scripts/smoke.sh` kann die erste Monsterzeile als Kommentar behandeln.
- Die zweite Zeile startet syntaktisch kaputt.
- Der eingebaute `node tools/test_smoke_script_sanity.js` hilft nicht, wenn `smoke.sh` selbst gar nicht ausführbar bis dorthin kommt.

### Patch

`smoke.sh` muss echte LF-Zeilen enthalten:

```bash
#!/usr/bin/env bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
set -euo pipefail
```

Jedes Kommando muss auf eigener physischer Zeile stehen. Keine CR-only-Zeilen, keine Monsterzeilen, keine Kommentare mit angehängten `node`/`python3`/`grep`-Kommandos.

### Pflichtprüfung

Führe nach dem Fix lokal aus:

```bash
python3 - <<'PY'
from pathlib import Path

checks = {
    Path("scripts/smoke.sh"): 80,
    Path(".gitattributes"): 5,
}

for path, min_lf in checks.items():
    data = path.read_bytes()
    lf = data.count(b"\n")
    cr = data.count(b"\r")
    print(f"{path}: LF={lf} CR={cr} bytes={len(data)}")
    assert cr == 0, f"{path}: enthält CR-Zeichen; bitte auf LF normalisieren"
    assert lf >= min_lf, f"{path}: zu wenige LF-Zeilen ({lf}); Datei ist kollabiert"
PY

node tools/test_smoke_script_sanity.js
bash -n scripts/smoke.sh
```

Danach:

```bash
bash scripts/smoke.sh
```

### Wichtig

`tools/test_smoke_script_sanity.js` existiert bereits und ist gut. Es muss aber **extern vor Smoke** ausführbar sein und Smoke selbst muss sauber parsebar sein.

---

## 2. `.gitattributes` reparieren und Repo renormalisieren

### Befund

Raw zeigt `.gitattributes` als eine Zeile:

```text
*.md text eol=lf scripts/*.sh text eol=lf
```

Das ist keine saubere Liste getrennter Patterns. Dadurch wird `scripts/*.sh` nicht zuverlässig als eigene Regel abgesichert.

### Patch

Schreibe `.gitattributes` mit echten LF-Zeilen:

```gitattributes
*.md text eol=lf
*.json text eol=lf
*.js text eol=lf
*.py text eol=lf
*.sh text eol=lf
scripts/*.sh text eol=lf
```

Dann:

```bash
git add --renormalize .
git diff --check
```

Falls `git add --renormalize .` viele unrelated Dateien anfässt, nur die betroffenen Dateien kontrolliert normalisieren, aber `scripts/smoke.sh` und `.gitattributes` müssen am Ende garantiert LF-only sein.

---

## 3. `speicher-fortsetzung.md`: aktive v7-Pflichtfeldliste ist noch alt

### Befund

Im Abschnitt:

```text
**v7-Export-Pflichtfelder (kanonisch, nicht Runtime-Bridge):**
```

steht noch eine zu alte Feldliste:

```text
campaign { episode, mission, px, px_state, mode, rift_seeds[] }
logs { trace[], market[], artifact_log[], notes[], flags }
```

Das widerspricht dem aktuellen Masterprompt und dem Schema. Weiter unten im Kompakt-Profil ist vieles schon korrekt, aber die aktive Pflichtfeldliste bleibt LLM-gefährlich, weil sie wie der harte Exportvertrag wirkt.

### Patch

Die aktive Pflichtfeldliste muss dieselbe Wahrheit sagen wie Masterprompt §F und `saveGame.v7.export.schema.json`.

Ersetze die Feldliste durch eine vollständige Version, mindestens:

```text
v, zr, save_id, parent_save_id, merge_id, branch_id,

campaign {
  episode, mission, px, px_state, mode, rift_seeds[],
  entry_choice_skipped, episode_start, episode_end
},

characters[] {
  id, name, callsign, rank, lvl, xp, origin, attr,
  lp, lp_max, stress, has_psi, sys_installed,
  wenn has_psi=true: psi_heat, pp, psi_abilities[],
  talents[], equipment[], implants[], history,
  carry[], quarters_stash[], vehicles,
  artifact?, reputation, wallet, level_history
},

economy { hq_pool },

logs {
  trace[], hud[], psi[], arena_psi[],
  market[], artifact_log[], notes[], flags
},

summaries { summary_last_episode, summary_last_rift, summary_active_arcs },

continuity {
  last_seen { mode, episode, mission, location },
  split, roster_echoes[], shared_echoes[],
  convergence_tags[], npc_roster[], active_npc_ids[]
},

arc { factions, questions[], hooks[] },

ui {
  gm_style, suggest_mode, action_mode,
  intro_seen, dice{debug_rolls},
  contrast, badge_density, output_pace, voice_profile
},

arena {
  active, phase, queue_state, mode, tier,
  previous_mode, resume_token, contract_id, streak,
  pending_rewards, banked_rewards,
  rewarded_runs_this_contract, first_wins,
  defeated_types, last_reward_episode,
  wins_player, wins_opponent, match_policy
}
```

Achte darauf, dass `arena` nicht optional klingt. `arena` ist Root-Pflichtblock, auch im Default-Idle-Zustand.

---

## 4. `speicher-fortsetzung.md`: alter Arena-Persistenzabsatz widerspricht neuem Vertrag

### Befund

Der Abschnitt um `Arena-Persistenzvertrag (persistent vs. transient)` sagt noch sinngemäß:

```text
Persistiert werden nur langlebige Werte...
Laufzeit-/Queue-Felder (`active`, `phase`, `queue_state`, ...) gelten als transient
```

Das ist zu alt. Der neue Vertrag lautet:

- **Live-Matchphysik** ist transient.
- **HQ-safe Sentinel/Checkpoint-Felder** werden gespeichert.
- Nach Runde/Serie ist Save in der HQ-Arena-Lounge erlaubt.
- `active=false`, `phase=idle|completed`, `queue_state=idle|completed`, `pending_rewards`, `banked_rewards`, `contract_id`, `streak` usw. gehören in den Save.

### Patchtext

Ersetze den alten Absatz durch sinngemäß:

```text
**Arena-Persistenzvertrag (Karriere + HQ-safe Checkpoint).**
Persistiert werden Arena-Karriere und HQ-sichere Sentinel-/Checkpoint-Felder:
`arena.active=false`, `arena.phase=idle|completed`,
`arena.queue_state=idle|completed`, `arena.previous_mode`,
`arena.resume_token`, `arena.contract_id`, `arena.streak`,
`arena.pending_rewards`, `arena.banked_rewards`,
`arena.rewarded_runs_this_contract`, `arena.first_wins`,
`arena.defeated_types`, `arena.last_reward_episode`,
`arena.wins_player`, `arena.wins_opponent`, `arena.tier`
und `arena.match_policy`.

Runtime-only bleiben Live-Queue-/Matchzustände wie
`searching|matched|staging|active`, Gegnerzustände,
Rundentimer, Zonen, temporäre Budgets und laufende Matchphysik.
Der HQ-Save schreibt niemals ein aktives Match, aber immer den
vollständigen Default-/Checkpoint-Block.
```

---

## 5. `test_v7_export_fieldlist_watchguard.js` ist zu breit

### Befund

Der Watchguard sucht aktuell im groben Bereich `Kompakt-Profil / Save v7` nach Snippets. Dadurch kann er grün sein, obwohl der aktive Abschnitt `v7-Export-Pflichtfelder` weiter oben veraltet bleibt.

### Patch

Der Test muss gezielt den aktiven Pflichtfeldabschnitt prüfen:

- Startanker: `**v7-Export-Pflichtfelder (kanonisch, nicht Runtime-Bridge):**`
- Endanker: `Felder wie character.attributes.SYS_runtime` oder nächster Abschnittsmarker.
- Innerhalb dieses Blocks müssen alle neuen Felder vorkommen:
  - `entry_choice_skipped`
  - `episode_start`
  - `episode_end`
  - `psi_heat`
  - `pp`
  - `psi_abilities`
  - `artifact?`
  - `logs.hud`
  - `logs.psi`
  - `logs.arena_psi`
  - `ui.intro_seen`
  - `ui.dice.debug_rolls`
  - `arena.active`
  - `arena.phase`
  - `arena.queue_state`
  - `arena.pending_rewards`
  - `arena.banked_rewards`
  - `arena.contract_id`
  - `arena.streak`
  - `arena.first_wins`
  - `arena.match_policy`

Der Test soll explizit fehlschlagen, wenn der aktive Block noch alte Mini-Listen enthält wie:

```text
logs { trace[], market[], artifact_log[], notes[], flags }
campaign { episode, mission, px, px_state, mode, rift_seeds[] }
```

---

## 6. Encounter-Pools: nackte `+1`/`+2`-Folgen beschriften

### Befund

Die alte `Paradoxon`-Spalte ist weg, gut. Aber im Encounter-Pool stehen noch nackte oder halb nackte numerische Folgen, zum Beispiel:

- `0-1`
- `Druck +1`
- `+1-2 bei Käufen`
- `+2 wenn ignoriert`

Eine KI kann das im alten Kontext wieder als Px-Anstieg lesen. Die Tabelle sollte ausdrücklich Heat/Noise/Druck/Timeline-Echo/Bloom-Druck benennen.

### Patch

Beispiele:

```text
0-1
```

ersetzen durch:

```text
Heat 0-1 nach SL-Entscheid
```

```text
Druck +1
```

präzisieren zu:

```text
Druck +1 bei Reparaturverzug
```

```text
+1-2 bei Käufen
```

ersetzen durch:

```text
Timeline-Echo +1-2 bei Out-of-Era-Käufen
```

```text
+2 wenn ignoriert
```

ersetzen durch:

```text
Bloom-Druck +2 wenn ignoriert
```

Ziel: Keine Encounter-Folge außerhalb klarer Mechanikkategorien.

---

## 7. `test_px_language_watchguard.js` verschärfen

### Befund

Der aktuelle Watchguard blockiert nur alte direkte Paradoxon-/Px-Formulierungen, aber nicht die aktuelle Restgefahr: unbeschriftete `+1`/`+2`-Folgen in Encounter-Tabellen.

### Patch

Erweitere den Test gezielt für den Encounter-Pool-Bereich in `gameplay/kampagnenstruktur.md`.

Vorschlag:

1. Extrahiere den Bereich von `### Encounter-Pools außerhalb des HQ` bis zum nächsten großen Abschnitt nach den Encounter-Tabellen.
2. Prüfe Tabellenzellen in den Folge-/Druck-/Echo-Spalten.
3. Fail bei Zellen, die nur oder primär so aussehen:
   - `0-1`
   - `+1`
   - `+2`
   - `+1-2 bei ...`
   - `+2 wenn ...`
4. Erlaubte Präfixe:
   - `Heat`
   - `Noise`
   - `Druck`
   - `Timeline-Echo`
   - `Bloom-Druck`
   - `Rift-Echo`
   - `Fraktionsnotiz`
   - `Px bleibt unverändert`
5. Nicht den ganzen Dateiinhalt pauschal auf `+1` prüfen, weil Team-Perks und normale Boni legitime `+1`/`+2` enthalten.

---

## 8. Masterprompt Load-Formulierung: HQ-only-Save nicht verwässern

### Befund

Der Masterprompt sagt einerseits:

- Load führt in freien HQ-Zustand.
- Keine halb offene Missionsfortsetzung.
- Save nur HQ-only.

Dann steht im selben Load-Zwang-Block sinngemäß:

```text
bei laufender Mission geht die Kampagne direkt am letzten Szenen-Anker weiter
```

Das kann den HQ-only-Savevertrag verwässern. Reguläre v7-Exports sollen keine Mid-Mission-Fortsetzung erzeugen.

### Patchtext

Ersetze die Formulierung durch eine HQ-only-kompatible Variante:

```text
Direktstart aus Save nur aus gültigen HQ-Saves:
Wenn der Opener einen bestimmten, durch den Save gedeckten Einsatzstart verlangt
(z. B. "Mission 5 Mini-Boss") und der Save im HQ steht, darf die KI-SL nach
Kurzrückblick und knappem HQ-/Briefing-Anker direkt in diesen neuen Einsatz starten.
Ein regulärer v7-Export enthält keine laufende Missionsszene. Externe oder Legacy-
Importe mit Missionsankern werden als Recovery-/Importfall in den HQ-Router
normalisiert; sie erzeugen keinen normalen Mid-Mission-`!save`.
```

Ziel: Kein Chargen-Neustart nach Load, aber auch kein normalisiertes Mid-Mission-Save.

---

## 9. Optional: Strict-Fixture für Psi/Artefakt ergänzen

Das Schema hat die Felder jetzt. Der neue Watchguard prüft strukturell, ob sie im Schema vorhanden sind. Noch stärker wäre eine kleine nicht-fragmentarische Fixture:

```text
internal/qa/fixtures/savegame_v7_strict_psi_artifact_hq.json
```

Diese Fixture sollte ein vollständiger strict-v7-HQ-Save sein mit:

- `has_psi: true`
- `psi_heat`
- `pp`
- `psi_abilities[]`
- `artifact`
- vollständigem `arena` Default-Idle-Block
- vollständigen Root-Pflichtfeldern

Dann `tools/test_v7_schema_consistency.js` oder ein eigener Test ergänzen, damit dieser Fall nicht mehr regressiert.

Nur machen, wenn es ohne großen Aufwand ins bestehende Testkonzept passt.

---

## 10. Akzeptanzkriterien

Der Pass gilt nur als bestanden, wenn alle Punkte erfüllt sind:

```bash
git diff --check

python3 - <<'PY'
from pathlib import Path
for p, min_lf in [(Path("scripts/smoke.sh"), 80), (Path(".gitattributes"), 5)]:
    data = p.read_bytes()
    print(p, "LF", data.count(b"\n"), "CR", data.count(b"\r"))
    assert data.count(b"\r") == 0
    assert data.count(b"\n") >= min_lf
PY

node tools/test_smoke_script_sanity.js
node tools/test_v7_export_fieldlist_watchguard.js
node tools/test_px_language_watchguard.js
node tools/test_v7_character_optional_fields_schema.js
node tools/test_save_budget_watchguard.js
node tools/test_watchguard_smoke_coverage.js

bash -n scripts/smoke.sh
bash scripts/smoke.sh
```

Zusätzlich manuell prüfen:

- Raw-Download von `scripts/smoke.sh` hat echte viele LF-Zeilen, nicht 2.
- Raw-Download von `.gitattributes` hat getrennte Patterns, nicht 1 Kombizeile.
- `speicher-fortsetzung.md` enthält keine aktive alte Pflichtfeldliste mehr.
- Arena-Abschnitt in `speicher-fortsetzung.md` nennt HQ-safe Sentinel-Felder als persistent.
- Encounter-Pools haben keine nackten `+1`/`+2`-Folgen ohne Mechaniklabel.
- Masterprompt suggeriert keinen regulären Mid-Mission-v7-Save.

---

## 11. Commit Message

```text
fix(v7): finalgate smoke eol and save-contract drift
```

Kurze Beschreibung:

```text
Normalize smoke/gitattributes to LF, tighten v7 fieldlist and Px language watchguards,
align speicher-fortsetzung with masterprompt/schema, and clarify HQ-only load semantics.
```
