# CODEX-BRIEFING — ZEITRISS v7 Save/Merge Contract Cleanup II

**Ziel:** Den aktuellen ZEITRISS-Main so nachziehen, dass das Save-/Load-/Merge-System wirklich die Vision erfüllt: portable Charakterbögen, Gruppensplits, Rejoins, PvP-Checkpointing und schlanke KI-Interpretation ohne Server.

**Status nach Repo-Review:** Es ist stark, aber noch nicht sauber genug für „fertig“. Die neue Richtung ist in README, Masterprompt und Speicher-Modul sichtbar. Der harte Exportvertrag, mehrere Fixtures und einige Testguards sprechen aber noch nicht dieselbe Wahrheit. Bitte nicht redesignen, sondern den Contract schließen.

**Arbeitsmodus für Codex:**

1. Aktuellen `main` auschecken.
2. Die unten genannten Dateien vollständig lesen.
3. Einen Branch erstellen.
4. Die Findings in der Reihenfolge A → H patchen.
5. Neue/erweiterte Watchguards einbauen.
6. `bash scripts/smoke.sh` ausführen.
7. Einen einzigen Commit mit der untenstehenden Commit-Message-Struktur erzeugen.

---

## 0. Wichtigste Vision, die nicht verloren gehen darf

ZEITRISS soll nicht wie ein Chat-RPG mit Speicherkrücke wirken. Der Save ist der Charakterbogen, die Storyakte und der transportable Weltanker.

Ein Spieler soll alleine, zu zweit oder in einer 5er-Gruppe spielen können, nach einem Abschnitt speichern, in einen neuen Chat gehen, dort mit anderen Saves zusammengeführt werden und das Gefühl haben: „Die Welt ist dieselbe, aber diese KI-SL interpretiert meinen Bogen auf ihre Art.“

Das ist kein Bug, sondern das Feature. Unterschiedliche Spielleiter interpretieren denselben Charakterbogen leicht anders. Die KI soll dabei nicht mehr JSON brauchen, sondern bessere Kompression: `summaries`, `arc.hooks`, `continuity.roster_echoes`, `continuity.shared_echoes`, wenige beweisende Logs und klare Merge-Entscheidungen.

**Goldener Satz:**

> Der Save ist kein Chatprotokoll. Der Save ist ein Charakterbogen mit Welt-Echo.

---

## 1. Geprüfte Hotspots

Bitte diese Dateien zuerst komplett lesen:

```text
AGENTS.md
README.md
meta/masterprompt_v6.md
systems/gameflow/speicher-fortsetzung.md
systems/gameflow/saveGame.v7.export.schema.json
systems/gameflow/saveGame.v7.schema.json
gameplay/kampagnenstruktur.md
scripts/smoke.sh
runtime.js
tools/test_v7_schema_consistency.js
tools/test_continuity_output_contract.js
tools/test_v7_smart_merge_3_2.js
tools/test_arena_round_checkpoint.js
tools/test_v7_personal_export.js
tools/test_arena_schema.js
tools/test_save.js
internal/qa/fixtures/savegame_v7_*.json
internal/qa/fixtures/continuity_output_contract_multi_load.json
```

Repo-Grundsatz aus `AGENTS.md` beachten:

```text
Save-Schema v7 — Template im Masterprompt ist SSOT.
runtime.js = CI-Tests, nicht Spiellogik.
Jede Regeländerung in den WS-Dateien verankern.
```

---

# A. BLOCKER — Strict-v7-Exportvertrag und Fixtures sprechen nicht dieselbe Sprache

## Befund

`systems/gameflow/saveGame.v7.export.schema.json` ist strict, aber noch nicht auf dem Stand der neuen Save/Merge-Vision.

Aktueller Drift:

1. `campaign.entry_choice_skipped` wird in `speicher-fortsetzung.md` als Persistenzanker genannt, ist im strict Schema aber nicht erlaubt.
2. `ui.intro_seen` wird als Persistenzanker genannt, ist im strict Schema und im Masterprompt-v7-Template aber nicht enthalten.
3. `logs.hud[]`, `logs.psi[]`, `logs.arena_psi[]` werden in Speicher-Modul, Runtime-/Fixtures und Tests benutzt, sind im strict Export-Schema aber nicht erlaubt.
4. `arena.first_wins` ist im strict Schema `integer`, während Kampagnenstruktur und Arena-Checkpoint-Test korrekt `arena.first_wins[tier]` als Objekt erwarten.
5. `tools/test_arena_round_checkpoint.js` erwartet `arena.pending_rewards`, `arena.queue_state` und `first_wins` als Objekt. Das strict Export-Schema verbietet diese Felder aktuell.
6. Mehrere `internal/qa/fixtures/savegame_v7_*.json` sind als v7-Save-Fixures benannt, aber nicht strict-v7-konform: fehlende Root-Lineage-Felder, root-`location`/`phase`, unvollständige Characters, fehlendes `ui.action_mode`, fehlende `logs.trace`/`market`/`artifact_log`/`notes`, `summary_active_arcs` als Array statt String, fehlende `npc_roster`/`active_npc_ids` usw.

Das ist gefährlich, weil Codex/LLMs aus Fixtures lernen. Eine Fixture mit `v:7`, aber Legacy-/Partial-Struktur, ist stärkeres LLM-Futter als jeder erklärende Absatz.

## Patch-Ziel

Alle Dateien müssen dieselbe Wahrheit tragen:

```text
Masterprompt-v7-Template = strict Export-Schema = v7-Fixtures = Smoke-Guards.
```

## Konkreter Patch

### A1 — Strict Schema erweitern und straffen

Datei:

```text
systems/gameflow/saveGame.v7.export.schema.json
```

Empfohlene Linie:

- `campaign.entry_choice_skipped` als `boolean` aufnehmen und in `required` setzen.
- `ui.intro_seen` als `boolean` aufnehmen und in `required` setzen.
- `logs.hud`, `logs.psi`, `logs.arena_psi` als Arrays erlauben und in `required` setzen, wenn das Masterprompt-Template sie schreibt. Falls ihr sie nicht immer schreiben wollt: dann trotzdem erlauben und per Watchguard klären, dass leere Arrays beim Export optional sind. Ich empfehle: schreiben, weil leere Arrays wenig kosten und die KI dann nicht über Feldexistenz rätselt.
- `continuity.last_seen.mode` im **strict Export** auf `"hq"` beschränken oder mindestens per Test verbieten, wenn `location:"HQ"` und `mode:"core|rift|arena|chronopolis"` zusammen auftreten. Da `!save` nur im HQ erlaubt ist, ist `const: "hq"` im Export sauberer. Das tolerante Import-Schema darf weiter mehr erlauben.
- `continuity.last_seen.location` im strict Export auf `"HQ"` beschränken.
- `arena.first_wins` von Integer auf Objekt ändern.
- Arena-Checkpoint-Felder ergänzen: `queue_state`, `pending_rewards`, `banked_rewards`, `contract_id`, `streak`.
- `arena.resume_token` als Objekt oder `null` führen. Aktuelle Fixture nutzt String; das ist zu dünn. Falls ihr einen Token-String behalten wollt, dann sauber typisieren. Besser: Objekt mit minimaler Struktur.

Minimaler Arena-Block im strict Schema:

```json
"arena": {
  "type": "object",
  "additionalProperties": false,
  "required": [
    "active",
    "phase",
    "queue_state",
    "mode",
    "tier",
    "previous_mode",
    "resume_token",
    "contract_id",
    "streak",
    "pending_rewards",
    "banked_rewards",
    "rewarded_runs_this_contract",
    "first_wins",
    "defeated_types",
    "last_reward_episode",
    "wins_player",
    "wins_opponent",
    "match_policy"
  ],
  "properties": {
    "active": { "type": "boolean", "const": false },
    "phase": { "type": "string", "enum": ["idle", "completed"] },
    "queue_state": { "type": "string", "enum": ["idle", "completed"] },
    "mode": { "type": "string", "enum": ["single", "team", "mixed"] },
    "tier": { "type": "integer", "minimum": 1 },
    "previous_mode": { "type": ["string", "null"] },
    "resume_token": { "type": ["object", "null"], "additionalProperties": true },
    "contract_id": { "type": ["string", "null"] },
    "streak": { "type": "integer", "minimum": 0 },
    "pending_rewards": {
      "type": "object",
      "additionalProperties": false,
      "required": ["cu", "xp", "arena_rep", "multiplier", "risk"],
      "properties": {
        "cu": { "type": "number" },
        "xp": { "type": "number" },
        "arena_rep": { "type": "number" },
        "multiplier": { "type": "number" },
        "risk": { "type": "string", "enum": ["none", "pending"] }
      }
    },
    "banked_rewards": {
      "type": "object",
      "additionalProperties": false,
      "required": ["cu", "xp", "arena_rep"],
      "properties": {
        "cu": { "type": "number" },
        "xp": { "type": "number" },
        "arena_rep": { "type": "number" }
      }
    },
    "rewarded_runs_this_contract": { "type": "integer", "minimum": 0 },
    "first_wins": {
      "type": "object",
      "additionalProperties": {
        "type": "integer",
        "minimum": 0,
        "maximum": 3
      }
    },
    "defeated_types": { "type": "array" },
    "last_reward_episode": { "type": ["integer", "null"] },
    "wins_player": { "type": "integer", "minimum": 0 },
    "wins_opponent": { "type": "integer", "minimum": 0 },
    "match_policy": { "type": "string", "enum": ["sim", "lore"] }
  }
}
```

### A2 — Masterprompt-v7-Template synchronisieren

Datei:

```text
meta/masterprompt_v6.md
```

Im JSON-Template ergänzen:

```json
"campaign": {
  "episode": 1,
  "mission": 0,
  "px": 0,
  "px_state": "stable",
  "mode": "mixed",
  "entry_choice_skipped": true,
  "rift_seeds": []
}
```

```json
"logs": {
  "trace": [],
  "hud": [],
  "psi": [],
  "arena_psi": [],
  "market": [],
  "artifact_log": [],
  "notes": [],
  "flags": {
    "runtime_version": "4.2.6",
    "chronopolis_unlocked": false,
    "imported_saves": [],
    "duplicate_branch_detected": false,
    "duplicate_character_detected": false,
    "continuity_conflicts": []
  }
}
```

```json
"ui": {
  "gm_style": "verbose",
  "suggest_mode": false,
  "action_mode": "uncut",
  "contrast": "standard",
  "badge_density": "standard",
  "output_pace": "normal",
  "voice_profile": "gm_second_person",
  "intro_seen": true
}
```

Für PvP bitte den `arena`-Block als default aufnehmen oder zwingend Load-Defaulting testen. Ich empfehle default aufnehmen, weil Arena sonst formal wie Zweitklasse wirkt:

```json
"arena": {
  "active": false,
  "phase": "idle",
  "queue_state": "idle",
  "mode": "single",
  "tier": 1,
  "previous_mode": null,
  "resume_token": null,
  "contract_id": null,
  "streak": 0,
  "pending_rewards": { "cu": 0, "xp": 0, "arena_rep": 0, "multiplier": 1, "risk": "none" },
  "banked_rewards": { "cu": 0, "xp": 0, "arena_rep": 0 },
  "rewarded_runs_this_contract": 0,
  "first_wins": {},
  "defeated_types": [],
  "last_reward_episode": null,
  "wins_player": 0,
  "wins_opponent": 0,
  "match_policy": "sim"
}
```

### A3 — v7-Fixtures strict machen

Dateien:

```text
internal/qa/fixtures/savegame_v7_*.json
```

Regel:

```text
Jede Datei, die savegame_v7_*.json heißt, muss strict-v7-exportfähig sein.
```

Wenn eine Fixture bewusst nur Partial-/Output-Contract ist, dann umbenennen, z. B.:

```text
partial_v7_contract_*.json
continuity_output_contract_*.json
```

Aktuell besonders prüfen:

```text
savegame_v7_5er_hq_highlevel.json
savegame_v7_split_3_2_merge.json
savegame_v7_merge_rift_pvp.json
savegame_v7_chronopolis_roundtrip.json
savegame_v7_chat_load.json
savegame_v7_arena_round_checkpoint.json
savegame_v7_personal_export_from_group.json
```

Häufige Fixes:

- root `location` und root `phase` entfernen.
- `save_id`, `parent_save_id`, `merge_id`, `branch_id` ergänzen.
- `campaign.entry_choice_skipped` ergänzen.
- `characters[]` vollständig machen: `name`, `callsign`, `rank`, `lvl`, `xp`, `origin`, `attr`, `lp`, `lp_max`, `stress`, `has_psi`, `sys_installed`, `talents`, `equipment`, `implants`, `history`, `carry`, `quarters_stash`, `vehicles`, `reputation`, `wallet`, `level_history`.
- `logs.trace`, `logs.hud`, `logs.psi`, `logs.arena_psi`, `logs.market`, `logs.artifact_log`, `logs.notes`, `logs.flags.runtime_version`, `logs.flags.chronopolis_unlocked` ergänzen.
- `summaries.summary_active_arcs` als String führen, nicht Array.
- `continuity.npc_roster` und `continuity.active_npc_ids` ergänzen.
- `continuity.last_seen.mode` bei HQ-Saves auf `"hq"` setzen.
- `ui.action_mode` und `ui.intro_seen` ergänzen.
- Arena-Checkpoint-Fixture: `resume_token` als Objekt führen, nicht String.

### A4 — Watchguard wirklich strict machen

Datei:

```text
tools/test_v7_schema_consistency.js
```

Aktuell prüft der Test vieles heuristisch, validiert aber nicht hart genug gegen den strict Exportvertrag. Er muss mindestens diese Dinge zusätzlich prüfen:

1. Alle `internal/qa/fixtures/savegame_v7_*.json` laden.
2. Root-Keys gegen `saveGame.v7.export.schema.json` prüfen.
3. Required-Keys pro Hauptblock prüfen.
4. `additionalProperties:false` für Root, `campaign`, `logs`, `ui`, `arena` wirklich durchsetzen.
5. `characters[]` nicht nur auf `id/wallet` prüfen, sondern strict exportfähig.
6. Bei HQ-Saves `continuity.last_seen.mode === "hq"` und `location === "HQ"` verlangen.
7. `arena.first_wins` muss Objekt sein.
8. Wenn `arena.pending_rewards` existiert, muss `queue_state` `idle|completed` sein und `arena.active === false`.

Ohne externe Dependencies am besten einen kleinen rekursiven Validator für den vorhandenen JSON-Schema-Subset schreiben. Falls ihr lieber `ajv` nutzt: nur, wenn package-lock/Dependency-Policy im Repo passt.

Akzeptanz:

```bash
node tools/test_v7_schema_consistency.js
# v7-schema-consistency-ok
```

---

# B. BLOCKER — Arena-Persistenz widerspricht PvP-Runden-Checkpoint

## Befund

`gameplay/kampagnenstruktur.md` sagt im Arena-Persistenzvertrag, dass `arena.active`, `arena.phase` und `arena.queue_state` transient sind. Gleichzeitig erwartet `tools/test_arena_round_checkpoint.js`, dass nach einer abgeschlossenen Runde ein HQ-safe Arena-Checkpoint mit `active:false`, `phase:completed`, `queue_state:completed`, `pending_rewards` und `first_wins` als Objekt gespeichert wird.

Das ist genau der PvP-Flow, den Flo will: Nach jeder Runde/Serie speichern, neuen Chat laden, Bonusstaffelung sauber weiterführen.

## Entscheidung

Nicht mehr „active/phase/queue_state sind transient“ sagen.

Stattdessen:

```text
Arena speichert den Karrierekern und HQ-sichere Sentinel-Felder, niemals laufende Match-Physik.
```

## Patch

Dateien:

```text
gameplay/kampagnenstruktur.md
systems/gameflow/speicher-fortsetzung.md
meta/masterprompt_v6.md
systems/gameflow/saveGame.v7.export.schema.json
tools/test_arena_round_checkpoint.js
internal/qa/fixtures/savegame_v7_arena_round_checkpoint.json
```

Neue klare Formulierung:

```text
Arena-Checkpoint ist nur nach Abschluss einer Runde/Serie savebar, sobald die Crew in der HQ-Arena-Lounge steht.
Persistiert werden:
- active=false
- phase=idle|completed
- queue_state=idle|completed
- mode, tier, match_policy
- wins_player, wins_opponent
- pending_rewards, banked_rewards
- contract_id, streak
- rewarded_runs_this_contract
- first_wins{tier:0..3}
- defeated_types[]
- last_reward_episode
- resume_token optional, nur HQ-resume-fähig
Nicht persistiert werden:
- zone
- laufende Positionen
- Gegner-Runtime
- aktive Queue-Stati searching|matched|staging|active
- Match-Budgets/Timer/Projektilzustände
```

Akzeptanzflow:

```text
Arena Match läuft → !save blockt.
Runde abgeschlossen → Rückkehr HQ-Arena-Lounge → !save erlaubt.
Push gewählt → pending_rewards bleibt persistiert, banked_rewards unverändert.
Cashout gewählt → pending_rewards wird auf 0/none normalisiert, banked_rewards/xp/wallet werden verbucht.
Neuer Chat mit Arena-Checkpoint → Load-Router bietet !arena resume oder Cashout/Push-Fortsetzung an.
```

---

# C. HIGH — Encounter-Pools tragen noch alte Paradoxon-Sprache

## Befund

`gameplay/kampagnenstruktur.md` hat im Encounter-Pool noch die Spalte `Paradoxon` und Werte wie `+1 bei Verzögerung`, `+1 bei Psi-Einsatz`, `-1 (Px) bei Live-Übertragung`, `+2 wenn ignoriert` usw. Gleichzeitig ist Px im Hauptvertrag ein positives Belohnungssystem.

Diese Tabelle ist LLM-gefährlich, weil Begegnungstabellen gerne direkt im Spiel benutzt werden.

## Patch

Datei:

```text
gameplay/kampagnenstruktur.md
```

Spalte ersetzen:

```text
Paradoxon → Druck / Heat / Echo
```

Werte sinngemäß ersetzen:

```text
0                                  → kein Zusatzdruck
+1 bei Verzögerung                 → Heat +1 bei Verzögerung
+1 bei Psi-Einsatz                 → Psi-Heat +1 / Timeline-Echo
-1 (Px) bei Live-Übertragung       → Heat +1 + Fraktionsnotiz; kein Px-Abzug
+2 wenn ignoriert                  → Rift-Echo +2 / Folgekomplikation; kein campaign.px
+1-2 bei Käufen                    → Marktspur / City-Heat; kein campaign.px
Paradoxon 0                        → kein Px-Effekt
```

Direkt über der Tabelle einfügen:

```text
Fehler erhöhen Druck. Gute, stabilisierte Einsätze erhöhen Px. Nur campaign.px==5 + ClusterCreate() erzeugt spielbare Rift-Seeds. Encounter-Tabellen dürfen nie direkt campaign.px erhöhen oder senken; sie liefern Heat, Noise, Timeline-Echos oder Storydruck.
```

Watchguard ergänzen:

```text
tools/test_px_language_watchguard.js
```

Muss fehlschlagen bei:

```text
"| Paradoxon |" in Encounter-Pool-Tabellen
"-1 (Px)"
"RIFT OPS bei Paradoxon"
"Px-Abzug"
"Vorsicht, Px steigt"
```

Akzeptanz:

```bash
node tools/test_px_language_watchguard.js
# px-language-watchguard-ok
```

---

# D. HIGH — Episode-Plan darf nicht als langer Save-Block zurückrutschen

## Befund

`gameplay/kampagnenstruktur.md` sagt noch, `episode_seed_make()` lege zehn Missions-Seeds in `campaign.episode_plan` ab und speichere `campaign.episode_start`/`campaign.episode_end`. Das strict-v7-Schema erlaubt diese Felder nicht. Für Flos Ziel ist das gut: Der Save darf nicht zum Kampagnenroman werden.

## Entscheidung

Der volle Episode-Plan ist Director-/Runtime-Scratchpad, nicht Save-Export.

Persistiert werden nur:

```text
campaign.episode
campaign.mission
campaign.mode
campaign.px / px_state
campaign.rift_seeds[]
arc.hooks[]
arc.questions[]
summaries.summary_active_arcs
continuity.shared_echoes[]
continuity.convergence_tags[]
```

Bei Branch-Wahlen wie Berlin 43 → 1939 / 1986 reicht ein kurzer Hook:

```json
{
  "tag": "route:berlin43:1939",
  "text": "Dreierteam verfolgt MORGENROT-Spur nach 1939."
}
```

```json
{
  "tag": "route:berlin43:1986",
  "text": "Zweierteam sichert Funknamen-Spur in 1986."
}
```

## Patch

Datei:

```text
gameplay/kampagnenstruktur.md
```

Zeilen/Abschnitte zu `campaign.episode_plan`, `campaign.episode_start`, `campaign.episode_end` umformulieren:

```text
episode_seed_make() erzeugt einen Director-Plan für die KI-SL. Dieser Plan ist runtime-only und wird nicht in v7 exportiert. Spielerrelevante Entscheidungen und offene Fäden werden kompakt in arc.hooks[], arc.questions[], summaries.* und continuity.* verdichtet.
```

Watchguard:

```text
tools/test_v7_save_budget_watchguard.js
```

Checks:

```text
- Kein strict-v7-Schema-Feld campaign.episode_plan.
- Kein savegame_v7_*.json enthält episode_plan / episode_start / episode_end.
- Aktive WS-Dateien nennen episode_plan nur mit runtime-only/import-only Kontext.
```

---

# E. HIGH — Smart-Merge muss als Ausgabe-Erlebnis definiert werden, nicht nur als Datenmerge

## Befund

`speicher-fortsetzung.md` und Masterprompt kennen Session-Anker, persönliche Wahrheit, Echos und Rejoin-Beats. Gut. Aber die neue Magie soll noch stärker verpflichtend werden: Das Mergen selbst soll Spaß machen. Die KI-SL soll aus mehreren kompakten Saves eine plausible Konvergenzszene bauen und nicht nur mechanisch „geladen“ melden.

## Patch

Dateien:

```text
meta/masterprompt_v6.md
systems/gameflow/speicher-fortsetzung.md
tools/test_continuity_output_contract.js
internal/qa/fixtures/continuity_output_contract_multi_load.json
```

Pflichtausgabe bei Mehrfach-Load erweitern:

```text
Bei Mehrfach-Load muss die KI-SL vor dem HQ-Router ausgeben:

1. In-World-Konvergenzszene, 1-3 kurze Absätze.
2. Kontinuitätsrückblick:
   - Session-Anker
   - Rückkehrer/Joiner
   - NPC-Lagebild
   - gemeinsame Nachwirkungen
   - Konvergenz-Folge
3. Merge-Tabelle:
   - Quelle / Save-ID oder Branch
   - Übernommen
   - Verdichtet als Echo
   - Konflikt / Entscheidung
4. Nächster spielbarer Hook:
   - 1 konkreter Satz, warum diese Crew jetzt zusammen weiterzieht.
```

Wichtig: Das ist kein langer Lore-Dump. Die Konvergenzszene soll eher wie ein Debrief-Opening wirken.

Beispiel:

```text
Die HQ-Schleuse nimmt beide Rücksprünge mit acht Sekunden Abstand. Erst knallt der 1939er Staub auf den Gitterboden, dann flackert der 1986er Funkname über Renierers Wanddisplay. Kodex braucht keinen Applaus. Er legt beide Spuren übereinander und markiert ein Wort: MORGENROT.
```

Erweiterung Fixture:

```json
"output_contract": {
  "convergence_scene": {
    "paragraphs": 2,
    "mentions": ["1939", "1986", "MORGENROT"],
    "tone": "hq_debrief_noir"
  },
  "merge_table": [
    {
      "source": "SAVE-BERLIN43-A1939",
      "accepted": ["AGENT-01", "AGENT-02", "AGENT-03", "shared_echo:morgenrot"],
      "compressed": ["route:berlin43:1939"],
      "conflict": "none"
    }
  ],
  "next_hook": "MORGENROT ist im Briefing als Boss-Tell aktiv."
}
```

Test erweitern:

```text
- convergence_scene existiert.
- merge_table hat mindestens eine Zeile pro Import.
- next_hook ist non-empty string.
- Echo-Fortwirkung innerhalb von 2 Sitzungsblöcken bleibt bestehen.
```

---

# F. HIGH — Personal-Export für Leaver/Hopper explizit machen

## Befund

`tools/test_v7_personal_export.js` und die Fixture sind eine gute Richtung: Personal-Export enthält genau einen Charakter und ein paar kompakte Echos. Der eigentliche Spieler-Vertrag sollte aber in den WS-Dateien deutlich stehen, sonst bleibt es nur Testwissen.

## Patch

Datei:

```text
systems/gameflow/speicher-fortsetzung.md
```

Unter OpenWebUI-Lobbybetrieb / Leaver-Regel ergänzen:

```text
### Personal-Export aus Gruppen-Save
Wenn ein Spieler die Gruppe verlässt oder solo weiterziehen will, erzeugt die KI-SL im HQ auf Wunsch einen Personal-Export.

Regeln:
- characters[] enthält genau diesen einen Charakter.
- Persönliche Felder bleiben vollständig: lvl/xp/wallet/gear/carry/history/reputation/level_history.
- economy.hq_pool wird 0 oder ein explizit zugewiesener Anteil.
- continuity.roster_echoes[] max 2, nur für relevante Beziehungen.
- continuity.shared_echoes[] max 3, nur Gruppenechos, die der Charakter sinnvoll „mitnimmt“.
- arc.hooks[] max 3, nur offene Fäden für diesen Charakter.
- Keine anderen Spieler-IDs, Namen oder privaten Bögen in JSON-Texten.
- Export startet im HQ und bleibt strict-v7-valid.
```

Goldener Satz:

```text
Wer geht, nimmt seinen Charakter und ein paar Narben der Gruppe mit — nicht die ganze Gruppe.
```

Test erweitern:

```text
tools/test_v7_personal_export.js
```

Zusätzlich prüfen:

```text
- Fixture ist strict-v7-exportfähig.
- Keine anderen AGENT-IDs in JSON.stringify.
- roster_echoes <= 2, shared_echoes <= 3, arc.hooks <= 3.
- economy.hq_pool ist 0 oder explizit als assigned_share markiert.
```

---

# G. MEDIUM — Runtime-/CI-Stubs laufen noch stark auf v6 und können Agenten täuschen

## Befund

`runtime.js` hat `save_deep()`/`select_state_for_save()` noch als v6-Serializer (`save_version:6`, `character`, root `location`, root `phase`, `arc_dashboard`). `tools/test_save.js` assertet ebenfalls v6. Gleichzeitig sagt `AGENTS.md`: Save-Schema v7, Masterprompt ist SSOT, runtime.js ist CI-Testspiegel.

Das ist nicht automatisch Spielbruch, weil `runtime.js` nicht Spiellogik ist. Aber es ist ein Agentenrisiko: Codex/Tests können grün sein, während der Produktvertrag v7 nicht geprüft wird.

## Patch-Entscheidung

Bitte nicht blind runtime.js groß umbauen, wenn das zu riskant ist. Aber die Rollen müssen klar sein.

Option A — minimal und sauber:

```text
- runtime.js bleibt Legacy-v6-Teststub.
- tools/test_save.js klar als legacy-v6-runtime-test markieren.
- Neuer v7-Export-Contract-Test validiert Masterprompt-Template + strict-v7-Fixtures.
- AGENTS/CONTRIBUTING kurz ergänzen: runtime-v6 ≠ Produkt-Save; v7-Contract wird über Schema/Fixtures/WS-Watchguards geprüft.
```

Option B — stärker:

```text
- Dedizierte Funktion save_game_v7_export() oder tools/v7_export.js hinzufügen.
- save_deep() kann legacy bleiben, aber v7_export wird für contract tests genutzt.
- smoke.sh prüft beides getrennt: legacy runtime smoke + v7 product contract.
```

Nicht akzeptabel:

```text
Smoke grün, obwohl keine v7-Fixture gegen strict-v7 geprüft wird.
```

Empfehlung: Option B, falls schnell machbar. Sonst Option A sofort und Option B als Post-Merge-TODO.

---

# H. MEDIUM — Save-Budget und Pruning als harte KI-Regel nachziehen

## Ziel

Das JSON darf nicht zum Mini-Server werden. Für bis zu fünf Spieler soll es kurz, interpretierbar und „magisch“ bleiben.

## Patch

Datei:

```text
systems/gameflow/speicher-fortsetzung.md
```

Eine kleine Budget-Tabelle ergänzen:

```text
### v7-Kompaktheitsbudget
- characters[]: max 5 Spielercharaktere; NPCs über continuity.npc_roster[], nicht als Fake-Spieler aufblasen.
- characters[].history.milestones: max 8 kurze Einträge; ältere in summaries.* verdichten.
- characters[].carry: max 6.
- characters[].quarters_stash: max 24.
- continuity.roster_echoes: max 5 im Gruppen-Save, max 2 im Personal-Export.
- continuity.shared_echoes: max 6 im Gruppen-Save, max 3 im Personal-Export.
- continuity.convergence_tags: max 4.
- continuity.npc_roster: max 6.
- arc.hooks: max 8 im Gruppen-Save, max 3 im Personal-Export.
- logs.trace: nur Beweis-/Gate-Events, ältere in summaries.* verdichten.
- Keine Volltranskripte, keine Szenenprosa, keine kompletten Episode-Pläne im Save.
```

Goldener Satz:

```text
Wenn der nächste Chat es nur fühlen muss, kommt es in summary/echo. Wenn er es beweisen muss, kommt es in trace. Wenn er es spielen muss, kommt es in hook.
```

Watchguard:

```text
tools/test_v7_save_budget_watchguard.js
```

Checks für `savegame_v7_*.json`:

```text
characters.length <= 5
continuity.roster_echoes.length <= 5
continuity.shared_echoes.length <= 6
continuity.convergence_tags.length <= 4
continuity.npc_roster.length <= 6
continuity.active_npc_ids.length <= 4
arc.hooks.length <= 8
kein episode_plan
kein root location/phase
kein Szenenprosa-Monster in logs.notes > z.B. 600 Zeichen pro Entry
```

In `scripts/smoke.sh` verankern.

---

# I. Akzeptanz-Szenarien

Codex soll nach den Patches mindestens diese Flows gedanklich + per Fixture absichern:

## I1 — Berlin 43 → Split 1939/1986 → Rejoin

```text
1. 5 Spieler schließen Mission Berlin 43 ab.
2. HQ-Debrief, Save möglich.
3. Gruppe entscheidet: 3 Spieler nach 1939, 2 Spieler nach 1986.
4. SL erzeugt zwei Branch-Saves mit gleicher continuity.split.family_id.
5. Beide Gruppen spielen in separaten Chats.
6. Beide speichern nach Debrief im HQ.
7. Ein neuer Chat lädt beide Branch-Saves.
8. Erster Save = Session-Anker.
9. Characters werden zu 5er-Roster gemerged.
10. shared_echoes und route-hooks erzeugen eine Konvergenzszene.
11. Merge-Tabelle wird ausgegeben.
12. Nächster Briefing-Hook enthält mindestens ein Echo aus 1939/1986.
```

## I2 — Personal-Export aus Gruppe

```text
1. 5er-Gruppe im HQ.
2. AGENT-03 will solo weiterziehen.
3. !save personal/export für AGENT-03.
4. JSON enthält genau AGENT-03.
5. Max 2 roster_echoes, max 3 shared_echoes.
6. Keine anderen Spieler-IDs im JSON.
7. Import in neuem Chat startet im HQ und fühlt sich wie Fortsetzung an.
```

## I3 — Arena Push-Checkpoint

```text
1. Arena-Serie läuft → !save blockt.
2. Runde/Serie abgeschlossen → HQ-Arena-Lounge.
3. Spieler wählt Push, nicht Cashout.
4. !save erlaubt.
5. Save enthält pending_rewards, banked_rewards, streak, first_wins Objekt, active=false, queue_state=completed.
6. Neuer Chat lädt Save.
7. Router bietet Arena-Fortsetzung/Cashout an.
8. campaign.px bleibt unverändert.
```

## I4 — Chronopolis Extraction

```text
1. Vor Schleuseneintritt HQ-DeepSave-Prompt.
2. Chronopolis selbst blockt Save.
3. Lebend rausgebrachte Items gehen in character.carry oder quarters_stash.
4. Rückkehr HQ → Save erlaubt.
5. logs.market/trace halten nur kompakte Beweise, keine Stadtprosa.
```

## I5 — Strict-v7-Fixture-Contract

```text
Alle internal/qa/fixtures/savegame_v7_*.json validieren gegen saveGame.v7.export.schema.json.
Keine Partial-Fixture darf savegame_v7_*.json heißen.
```

---

# J. Smoke/Verifikation

Nach Patch:

```bash
bash scripts/smoke.sh
```

Zusätzlich direkt prüfen:

```bash
node tools/test_v7_schema_consistency.js
node tools/test_v7_smart_merge_3_2.js
node tools/test_arena_round_checkpoint.js
node tools/test_v7_personal_export.js
node tools/test_px_language_watchguard.js
node tools/test_v7_save_budget_watchguard.js
```

Grep-Watch:

```bash
! grep -R '"first_wins"[[:space:]]*:[[:space:]]*{[[:space:]]*"type"[[:space:]]*:[[:space:]]*"integer"' systems/gameflow/saveGame.v7.export.schema.json
! grep -R '| Paradoxon |' gameplay/kampagnenstruktur.md
! grep -R -- '-1 (Px)' gameplay/kampagnenstruktur.md
! grep -R 'campaign\.episode_plan' internal/qa/fixtures systems/gameflow/saveGame.v7.export.schema.json
```

---

# K. Erwartete Commit-Message

```text
fix(save-v7): schließe Smart-Merge-, Arena- und Strict-Export-Vertrag

## Was
- Synchronisiert Masterprompt-v7-Template, strict Export-Schema, Speicher-Modul und v7-Fixtures.
- Macht Arena-Checkpoints HQ-savebar mit pending/banked Rewards und first_wins als Tier-Objekt.
- Entfernt alte Paradoxon-Sprache aus Encounter-Pools und ergänzt Strict-/Budget-Watchguards.

## Warum
- Der Save ist der portable Charakterbogen und Weltanker; Split/Merge muss für bis zu 5 Spieler robust und schlank bleiben.
- Aktuell widersprechen strict Schema, Fixtures und Arena-Docs bei first_wins, pending_rewards, logs.*, ui.intro_seen und campaign.entry_choice_skipped.
- Mehrfach-Load soll nicht nur mechanisch mergen, sondern eine kompakte, plausible Konvergenzszene liefern.

## Wichtige Entscheidungen
- Full episode_plan bleibt runtime-only; persistiert werden nur Hooks, Summaries und Echos.
- Arena speichert HQ-sichere Sentinel-Felder und Rewards, aber keine laufende Matchphysik.
- Alle savegame_v7_*.json Fixtures müssen strict-v7-exportfähig sein; Partial-Fixtures werden umbenannt oder vervollständigt.

## Verifikation
- bash scripts/smoke.sh
- node tools/test_v7_schema_consistency.js
- node tools/test_arena_round_checkpoint.js
- node tools/test_v7_personal_export.js
- node tools/test_px_language_watchguard.js
- node tools/test_v7_save_budget_watchguard.js

## Post-Merge-TODOs
- Falls runtime.js legacy-v6 bleibt: später dedizierten save_game_v7_export() Spiegel ergänzen, damit CI nicht nur Dokument-/Fixture-Verträge prüft.
```

---

# L. Kurzfassung für Codex

Patch nicht breit redesignen. Hauptziel ist Contract-Cleanup:

```text
Masterprompt-v7-Template == strict Export-Schema == v7-Fixtures == Smoke-Guards.
```

Wenn danach noch Zeit bleibt, nicht neue Features bauen, sondern genau diesen Satz härter absichern.

