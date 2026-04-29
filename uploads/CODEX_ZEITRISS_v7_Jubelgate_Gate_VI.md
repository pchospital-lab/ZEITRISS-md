# CODEX-BRIEFING — ZEITRISS v7 Jubelgate / Gate VI

## Ziel

Bitte bringe den aktuellen Main-Stand über das letzte formale Jubelgate.

Die Spiel-/Save-/Merge-Architektur ist inhaltlich sehr stark und fast auf Finalbericht-Niveau. Dieser Pass ist **kein Redesign**. Es geht um harte Repo-Vertragsreinigung:

1. `scripts/smoke.sh` muss wirklich mit LF-Zeilenenden ausführbar sein.
2. `.gitattributes` muss EOL-Regeln korrekt setzen.
3. Das strict-v7-Export-Schema muss die im Masterprompt erlaubten Charakterfelder akzeptieren.
4. `speicher-fortsetzung.md` darf keine veraltete v7-Pflichtfeldliste mehr enthalten.
5. Die Encounter-Pools sollen keine blanken `+1`/`+2`-Folgen stehen lassen, die wieder als alter Px-/Paradoxon-Anstieg interpretiert werden können.

Wenn diese Punkte sauber sind und `bash scripts/smoke.sh` grün läuft, ist der Jubeltest formal erreichbar.

---

## Review-Stand

Statischer Review des öffentlichen `main` am 29.04.2026.

Wichtig: Ich konnte hier keinen lokalen Clone/CI-Lauf ausführen. Codex soll im Repo arbeiten und am Ende die echten Befehle ausführen.

---

## SSOT-Entscheidung

Für KI-SL und Spieler gilt:

- **Masterprompt §F** ist das einzige kopierfähige `!save`-Template.
- `systems/gameflow/speicher-fortsetzung.md` dokumentiert Feldbedeutung, SaveGuard, Import, Migration, Split/Merge und Budgets.
- `systems/gameflow/saveGame.v7.export.schema.json` ist der strict Export-/Tooling-Vertrag.
- Die drei Quellen müssen dieselbe Wahrheit sprechen.

Nicht am Design drehen. Nicht die Save-/Merge-Vision aufweichen. Nur die Drift schließen.

---

# Finding 1 — `scripts/smoke.sh` ist weiterhin physisch kollabiert / CR-only-verdächtig

## Problem

Der GitHub-Codeviewer kann die Datei optisch als viele Zeilen anzeigen. Der Raw-Content wirkt aber weiterhin so, als hätte `scripts/smoke.sh` nur sehr wenige LF-Zeilen: eine Monsterzeile mit Shebang + Befehlen und danach eine Zeile, die mitten in einem Kommentarfragment beginnt:

```text
verankerte HQ-Projektion) node tools/test_physicality_watchguard.js ...
```

Das ist für Bash ein harter Gate-Blocker. Wenn die Datei CR-only oder anderweitig falsch normalisiert ist, wird die erste Monsterzeile als Kommentar bis zum ersten echten LF behandelt und der Rest kann als Syntaxmüll starten.

## Zusätzliches Problem

`.gitattributes` ist aktuell selbst nur eine Zeile:

```gitattributes
*.md text eol=lf scripts/*.sh text eol=lf
```

Das ist nicht gleichwertig zu zwei Regeln. In `.gitattributes` ist das erste Feld das Pattern; alles danach sind Attribute. Damit wird `scripts/*.sh text eol=lf` nicht sauber als eigene Regel garantiert.

## Patch

### 1. `.gitattributes` sauber mehrzeilig machen

Empfehlung:

```gitattributes
*.md text eol=lf
*.json text eol=lf
*.js text eol=lf
*.py text eol=lf
*.sh text eol=lf
scripts/*.sh text eol=lf
```

Optional, falls gewünscht:

```gitattributes
*.txt text eol=lf
```

### 2. `scripts/smoke.sh` als echtes LF-Textfile normalisieren

Nicht nur im Editor „hübsch anzeigen“, sondern Bytes reparieren:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("scripts/smoke.sh")
b = p.read_bytes()
# CRLF oder CR-only hart auf LF normalisieren
b = b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
p.write_bytes(b)
PY
```

Danach prüfen:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("scripts/smoke.sh")
b = p.read_bytes()
print("LF", b.count(b"\n"), "CR", b.count(b"\r"), "bytes", len(b))
assert b.startswith(b"#!/usr/bin/env bash\n"), "Shebang muss allein in Zeile 1 stehen"
assert b.count(b"\n") >= 80, "smoke.sh hat zu wenige echte LF-Zeilen"
assert b.count(b"\r") == 0, "smoke.sh enthält noch CR"
assert max(len(line) for line in b.split(b"\n")) < 500, "Monsterzeile gefunden"
PY

bash -n scripts/smoke.sh
git ls-files --eol .gitattributes scripts/smoke.sh
```

### 3. `tools/test_smoke_script_sanity.js` beibehalten und früh ausführen

Der Test ist gut. Er hilft aber nur, wenn `smoke.sh` überhaupt parsebar ist. Er sollte weiterhin früh in `smoke.sh` laufen, aber die echte Absicherung ist zusätzlich:

```bash
bash -n scripts/smoke.sh
```

und die Byte-Prüfung oben.

## Akzeptanz

- `bash -n scripts/smoke.sh` grün.
- `bash scripts/smoke.sh` grün.
- Bytecheck: `LF >= 80`, `CR == 0`.
- `git ls-files --eol scripts/smoke.sh` zeigt Worktree-LF.
- `.gitattributes` hat mehrere echte Zeilen.

---

# Finding 2 — Strict-v7-Schema blockiert Masterprompt-erlaubte Charakterfelder

## Problem

Der Masterprompt sagt im Save-Vertrag:

```text
Psi nur wenn has_psi: true:
  psi_heat, pp, psi_abilities[] ergänzen.

Artefakt:
  "artifact": {"name":"...", "tier":1, "effect":"..."} - max 1, nur wenn vorhanden.
```

Auch `speicher-fortsetzung.md` listet im Kompakt-Profil:

```text
wenn has_psi: psi_heat, pp, psi_abilities[]
artifact?: {name, tier, effect}
```

Das strict Export-Schema `systems/gameflow/saveGame.v7.export.schema.json` hat bei `characters[].additionalProperties:false` aber keine Properties für:

- `psi_heat`
- `pp`
- `psi_abilities`
- `artifact`

Damit würde ein echter Psi-Charakter oder ein Charakter mit Artefakt entweder beim strict Export scheitern oder die SL/Runtime müsste gerade die interessantesten Charakterdaten verwerfen. Das ist ein echter Save-System-Blocker.

## Patch

In `systems/gameflow/saveGame.v7.export.schema.json` innerhalb von `characters.items.properties` ergänzen:

```json
"psi_heat": { "type": "integer", "minimum": 0 },
"pp": { "type": "integer", "minimum": 0 },
"psi_abilities": { "type": "array" },
"artifact": {
  "type": "object",
  "additionalProperties": true,
  "required": ["name", "tier", "effect"],
  "properties": {
    "name": { "type": "string" },
    "tier": { "type": "integer", "minimum": 1 },
    "effect": { "type": "string" }
  }
}
```

Empfehlung: Draft-07-Conditional ergänzen, damit `has_psi:true` die Psi-Felder verlangt:

```json
"allOf": [
  {
    "if": {
      "properties": {
        "has_psi": { "const": true }
      },
      "required": ["has_psi"]
    },
    "then": {
      "required": ["psi_heat", "pp", "psi_abilities"]
    }
  }
]
```

Bitte pragmatisch halten: `has_psi:false` muss nicht zwingend scheitern, wenn alte Importpfade `psi_heat:0` mitführen. Wichtig ist: Ein Psi-Char darf strict-v7 nicht brechen.

## Neuer Watchguard

Bitte ergänzen:

```text
tools/test_v7_character_optional_fields_schema.js
```

Mindestchecks:

```js
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const schema = JSON.parse(
  fs.readFileSync(
    path.join(__dirname, "..", "systems/gameflow/saveGame.v7.export.schema.json"),
    "utf8"
  )
);

const charProps =
  schema.properties.characters.items.properties;

for (const key of ["psi_heat", "pp", "psi_abilities", "artifact"]) {
  assert.ok(charProps[key], `v7 character schema missing ${key}`);
}

const charRequired = schema.properties.characters.items.required || [];
assert.ok(charRequired.includes("has_psi"), "has_psi must remain a required character field");

console.log("v7-character-optional-fields-schema-ok");
```

Dann in `scripts/smoke.sh` verankern:

```bash
node tools/test_v7_character_optional_fields_schema.js > out/v7_character_optional_fields_schema.log
grep "v7-character-optional-fields-schema-ok" out/v7_character_optional_fields_schema.log
```

Optional stärker: eine strict-vollständige Fixture `savegame_v7_strict_psi_artifact.json` ergänzen und mit einem Validator prüfen, wenn im Repo bereits AJV/JSON-Schema-Validation verfügbar ist. Falls kein Validator vorhanden ist, reicht für diesen Pass der Property-Watchguard.

## Akzeptanz

- Schema enthält `characters[].psi_heat`, `characters[].pp`, `characters[].psi_abilities`, `characters[].artifact`.
- `has_psi:true` kann diese Felder speichern.
- Ein Charakter mit Artefakt wird durch `additionalProperties:false` nicht mehr abgewiesen.
- Smoke führt den neuen Watchguard aus.

---

# Finding 3 — `speicher-fortsetzung.md` enthält noch eine veraltete v7-Pflichtfeldliste

## Problem

In `systems/gameflow/speicher-fortsetzung.md` gibt es einen Abschnitt:

```text
v7-Export-Pflichtfelder (kanonisch, nicht Runtime-Bridge)
```

Diese Liste ist noch nicht deckungsgleich mit Masterprompt und Schema. Sie fehlt bzw. unterbetont aktuell unter anderem:

- `campaign.entry_choice_skipped`
- `campaign.episode_start`
- `campaign.episode_end`
- `logs.hud`
- `logs.psi`
- `logs.arena_psi`
- vollständige Root-Logs im Kompakt-Profil
- Charakter-Sonderfelder: `psi_heat`, `pp`, `psi_abilities[]`, `artifact?`

Später im Kompakt-Profil sind einige Felder korrekt genannt, aber der Root-Logs-Pfad steht noch als:

```text
logs.{trace[], market[], artifact_log[], notes[], flags:{}}
```

Das lässt `hud`, `psi`, `arena_psi` wieder aus dem eigentlichen Exportbaum herausfallen.

## Patch

Entweder:

### Variante A — eine einzige aktive Feldliste

Die ältere `v7-Export-Pflichtfelder`-Liste entfernen und durch Verweis ersetzen:

```text
Für den tatsächlichen `!save`-Export gilt ausschließlich das Masterprompt-Template §F
plus das Kompakt-Profil unten. Diese Datei führt keine zweite Pflichtfeldliste.
```

oder:

### Variante B — beide Listen vollständig synchronisieren

Dann muss die Liste mindestens so aussehen:

```text
v, zr,
save_id, parent_save_id, merge_id, branch_id,

campaign {
  episode, mission, px, px_state, mode,
  rift_seeds[], entry_choice_skipped, episode_start, episode_end
},

characters[] {
  id, name, callsign, rank, lvl, xp,
  origin, attr, lp, lp_max, stress,
  has_psi, sys_installed,
  psi_heat?, pp?, psi_abilities[]?,
  talents[], equipment[], implants[],
  history, carry[], quarters_stash[], vehicles,
  artifact?,
  reputation, wallet, level_history
},

economy { hq_pool },

logs {
  trace[], hud[], psi[], arena_psi[],
  market[], artifact_log[], notes[], flags
},

summaries { summary_last_episode, summary_last_rift, summary_active_arcs },

continuity {
  last_seen, split, roster_echoes[], shared_echoes[],
  convergence_tags[], npc_roster[], active_npc_ids[]
},

arc { factions, questions[], hooks[] },

ui {
  gm_style, suggest_mode, action_mode, intro_seen,
  dice{debug_rolls}, contrast, badge_density, output_pace, voice_profile
},

arena {
  active, phase, queue_state, mode, tier, previous_mode,
  resume_token, contract_id, streak,
  pending_rewards, banked_rewards,
  rewarded_runs_this_contract, first_wins,
  defeated_types, last_reward_episode,
  wins_player, wins_opponent, match_policy
}
```

Zusätzlich im Kompakt-Profil ändern:

```text
logs.{trace[], hud[], psi[], arena_psi[], market[], artifact_log[], notes[], flags:{}}
```

## Watchguard verbessern

`tools/test_v7_export_fieldlist_watchguard.js` ist sinnvoll, aber aktuell zu breit: Es sucht im gesamten Dokument und kann dadurch Felder aus der Runtime-Bridge-Liste zählen, obwohl die Exportliste selbst veraltet ist.

Bitte den Watchguard auf den aktiven Export-/Kompakt-Profil-Abschnitt fokussieren.

Mindestidee:

- Text ab `### Kompakt-Profil (Save v7)` bis zum nächsten `###` nehmen.
- Dort die Pflichtsnippets suchen.
- Zusätzlich prüfen, dass im Abschnitt `logs.{...}` die drei Felder `hud`, `psi`, `arena_psi` enthalten sind.
- Optional prüfen, dass die alte `v7-Export-Pflichtfelder`-Liste entweder nicht mehr existiert oder ebenfalls `entry_choice_skipped`, `episode_start`, `episode_end`, `logs.hud`, `logs.psi`, `logs.arena_psi` enthält.

## Akzeptanz

- Kein aktiver v7-Export-Abschnitt widerspricht dem Masterprompt.
- Root-Logs sind in `speicher-fortsetzung.md` vollständig.
- `logs.hud`, `logs.psi`, `logs.arena_psi` werden nicht nur in Runtime-Bridge-Texten gefunden, sondern im Export-/Kompakt-Profil selbst.
- Der Watchguard kann nicht mehr falsch-grün werden.

---

# Finding 4 — Encounter-Pools: blanke `+1`/`+2`-Folgen bleiben LLM-gefährlich

## Problem

Die alte Spalte `Paradoxon` ist entfernt. Das ist gut.

Im RIFT-OPS-Pool stehen aber weiterhin blanke Folgen wie:

```text
+2 wenn ignoriert
+1
+1-2 bei Käufen
+1 je Fehlversuch
+2
```

Ohne Label kann eine KI-SL das wieder als „Px +1/+2“ lesen, weil genau diese Tabellen früher Paradoxon-Werte trugen. Im Core-Pool ist die Spalte schon besser als `Druck/Echo` gelabelt, aber dort gibt es ebenfalls noch einen blanken Eintrag `+1`.

## Patch

Alle blanken Werte im Encounter-Pool beschriften.

Beispiele:

```text
Heat +1 bei Verzug
Noise +1 bei sichtbarem Psi
Timeline-Echo + Fraktionsnotiz
Druck +1
Rift-Echo +2 wenn ignoriert
Rift-Druck +1
Rift-Echo +1 je Fehlversuch
Bloom-Druck +2
```

Die RIFT-OPS-Spalte besser ebenfalls `Druck/Echo` nennen statt nur `Folge`.

Zusatzsatz direkt unter die Tabellen:

```text
Alle Werte in `Druck/Echo` sind Story-/Heat-/Noise-/Echo-Folgen. Sie erhöhen `campaign.px` nie automatisch. Px steigt nur über den positiven TEMP-/Missionsfortschritt und erzeugt nur bei Px 5 via `ClusterCreate()` Rift-Seeds.
```

## Watchguard optional verschärfen

`tools/test_px_language_watchguard.js` kann zusätzlich spezifisch auf Encounter-Pools prüfen, dass dort keine nackten Zellen wie `| +1 |`, `| +2 |`, `| +1-2 bei ... |` stehen.

Nicht übertreiben; Ziel ist Drift verhindern, nicht Tabellen unbrauchbar machen.

## Akzeptanz

- Keine nackten `+1`/`+2`-Folgen in Encounter-Pools.
- RIFT OPS starten weiter nur über offene `campaign.rift_seeds[]`/gültiges Gate, nicht über „Paradoxon ≥ 2“.
- Px bleibt positives Resonanz-/Seed-System.

---

# Finding 5 — Fragment-Fixtures sind okay, aber bitte bewusst halten

## Beobachtung

Mehrere `savegame_v7_*.json`-Fixtures sind jetzt mit `"fixture_kind":"fragment"` markiert. Das ist akzeptabel, solange Tests und Agenten klar wissen:

- Fragment-Fixtures sind Watchguard-Fragmente.
- Sie sind keine kopierfähigen `!save`-Beispiele.
- Strict-vollständige Saves müssen weiterhin echte Pflichtfelder haben.

Das aktuelle `test_v7_schema_consistency.js` berücksichtigt `fixture_kind === "fragment"`. Das ist okay.

## Keine Pflichtänderung

Nicht blockierend, solange die Doku und Watchguards das so halten.

Optional schöner:

- Fragmentdateien zusätzlich mit `_fragment` im Dateinamen versehen.
- Oder im Fixture-Verzeichnis eine README-Regel ergänzen: `fixture_kind:"fragment"` = kein strict Save.

---

# Konkrete Datei-Hotspots

Bitte mindestens diese Dateien prüfen/ändern:

```text
.gitattributes
scripts/smoke.sh
tools/test_smoke_script_sanity.js
tools/test_v7_export_fieldlist_watchguard.js
tools/test_px_language_watchguard.js
systems/gameflow/saveGame.v7.export.schema.json
systems/gameflow/speicher-fortsetzung.md
gameplay/kampagnenstruktur.md
```

Neu empfohlen:

```text
tools/test_v7_character_optional_fields_schema.js
internal/qa/fixtures/savegame_v7_strict_psi_artifact.json   # optional, wenn strict validate vorhanden
```

---

# Verifikation

Bitte am Ende exakt ausführen:

```bash
python3 - <<'PY'
from pathlib import Path
for rel in [".gitattributes", "scripts/smoke.sh"]:
    b = Path(rel).read_bytes()
    print(rel, "LF", b.count(b"\n"), "CR", b.count(b"\r"), "bytes", len(b))
    assert b.count(b"\r") == 0, f"{rel}: CR gefunden"
assert Path("scripts/smoke.sh").read_bytes().startswith(b"#!/usr/bin/env bash\n")
assert Path("scripts/smoke.sh").read_bytes().count(b"\n") >= 80
PY

bash -n scripts/smoke.sh
bash scripts/smoke.sh
```

Wenn verfügbar:

```bash
npm test
```

---

# Erwartetes Ergebnis

Nach diesem Pass soll gelten:

- Smoke ist nicht nur optisch, sondern byte-real ausführbar.
- `.gitattributes` verhindert Rückfälle.
- Strict-v7 erlaubt Psi-Charaktere und Artefakt-Träger.
- `speicher-fortsetzung.md` und Masterprompt widersprechen sich nicht mehr.
- Encounter-Folgen können nicht mehr als alter Px-Malus/Bonus missverstanden werden.
- Codex kann nach erfolgreichem Smoke den finalen Jubeltest verdienen.

---

# Commit-Message-Vorschlag

```text
fix(save-v7): close final jubelgate schema and smoke drift

## Was
- Normalize smoke.sh and gitattributes to real LF-safe text contracts.
- Extend strict v7 character schema for psi/artifact fields used by the Masterprompt.
- Sync speicher-fortsetzung v7 field lists with Masterprompt §F.
- Label encounter-pool pressure/echo effects to avoid Px drift.
- Add/extend watchguards for smoke sanity, v7 fieldlist scope and character optional fields.

## Warum
The save/merge architecture is ready, but the final gate still found formal drift:
smoke.sh is raw-line unsafe, the active v7 fieldlist can go stale, and strict schema rejects
valid Psi/artifact character exports.

## Wichtige Entscheidungen
- Masterprompt §F remains the only copyable !save template.
- Fragment fixtures stay allowed only when explicitly marked fixture_kind=fragment.
- Psi/artifact fields are character persistence, not runtime-only.
- Encounter pressure is Heat/Noise/Echo, never automatic Px gain/loss.

## Verifikation
- python bytecheck for .gitattributes and scripts/smoke.sh
- bash -n scripts/smoke.sh
- bash scripts/smoke.sh
```
