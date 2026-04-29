# CODEX-BRIEFING: ZEITRISS v7 Save/Merge auf die eigentliche Vision ziehen

**Arbeitsauftrag:** Bringe das ZEITRISS-Speichersystem auf das Zielbild: portabler Pen-&-Paper-Charakterbogen, 1–5 Spieler, Gruppen-Split/Rejoin über mehrere Chatfenster, PvP-Runden-Checkpoints, kompakte JSONs, maximale KI-Interpretierbarkeit ohne Server.

**Wichtigster Satz:** Der Save ist nicht ein Log. Der Save ist ein kompakter Charakterbogen plus Weltanker. Storytiefe entsteht beim Laden/Mergen durch die KI-SL aus `characters[]`, `summaries`, `continuity`, `arc`, wenigen Proof-Logs und Konflikt-Hooks.

---

## 0. Codex-Startprompt zum direkten Einfügen

```text
Du arbeitest im Repository pchospital-lab/ZEITRISS-md. Lies zuerst AGENTS.md vollständig. Ziel: v7-Save/Merge so bereinigen, dass ZEITRISS als serverloses Multiplayer-/Pen-&-Paper-System funktioniert: bis 5 Spieler, portable Einzel- und Gruppensaves, Split 3/2 in getrennte Chats, Rejoin/Merge mit magischer KI-Zusammenführung, PvP-Runden-Checkpoints, keine zu langen JSONs.

Nicht redesignen. Bestehende Architektur behalten, aber Vertragsdrift zwischen Masterprompt, speicher-fortsetzung.md, strict/tolerant Schema, Fixtures, runtime.js und Tests schließen.

Arbeite in dieser Reihenfolge:
1) Preflight lesen und Drift inventarisieren.
2) v7-Kanon festziehen: strict Export, tolerant Import, Masterprompt-Template, speicher-fortsetzung.md.
3) Smart-Merge-Vertrag mit Session-Anker, persönlicher Wahrheit und kompakten Echo-Hooks stabilisieren.
4) Arena/PvP-Runden-Checkpoint in den HQ-Hub einfügen: nach abgeschlossener Runde savebar, aber nie während aktivem Match.
5) Split/Personal-Export implementieren: Wer eine Gruppe verlässt, nimmt nur seinen Charakter plus kompakte Gruppen-Echos mit.
6) Episode-Plan schlank halten: keine 10er-Planliste im Save; nur sichtbare Routen/Hooks persistieren.
7) Tests/Fixtures aktualisieren und neue Watchguards ergänzen.
8) bash scripts/smoke.sh muss grün sein.

Harte Invarianten:
- Neue v7-Exports enthalten keine Root-Felder `location`, `phase`, `character`, `party`, `team`, `arc_dashboard`, `save_version`, `zr_version`.
- HQ-Deepsave setzt `continuity.last_seen.mode = "hq"` und `continuity.last_seen.location = "HQ"`.
- `characters[]` ist die einzige Quelle für Spielercharaktere und hat max. 5 Einträge. NPCs gehören nach `continuity.npc_roster[]`/`active_npc_ids[]`.
- Storyspeicher ist kompakt: `summaries.*`, `arc.questions[]`, `arc.hooks[]`, `continuity.roster_echoes[]`, `continuity.shared_echoes[]`, `continuity.convergence_tags[]`.
- Logs beweisen nur, was der nächste Chat zwingend beweisen muss. Keine Volltranskripte.
- SaveGuard bleibt HQ-only. Chronopolis, laufende Mission, aktive Arena-Queue oder aktives Match geben nie JSON aus.
- PvP-Checkpoint ist nur nach abgeschlossener Runde/Serie in der HQ-Arena-Lounge savebar: `arena.active=false`, `queue_state=completed|idle`.
- Merge soll eine in-world Einführung erzeugen, keine trockene Tabelle allein. Sinnbrüche werden als Anomalie/Gerücht/Haken gerahmt, nicht verschwiegen.
```

---

## 1. Zielbild in einem Satz

ZEITRISS soll sich so anfühlen, als gäbe es eine persistente MMO-Welt. Tatsächlich gibt es nur:

1. **Regelwerk/Wissensspeicher** als Weltgedächtnis.
2. **v7-JSON** als portabler Charakterbogen und Weltanker.
3. **KI-SL** als intelligenter Merge-Interpreter.
4. **HQ-Rituale** als Schleusen zwischen Kontextfenstern.

Der Save darf deshalb nicht versuchen, alles zu speichern. Er muss die richtigen **Andockpunkte** speichern, damit die KI-SL beim Laden die Welt plausibel neu zusammensetzt.

---

## 2. Preflight: Dateien vollständig lesen

Vor Änderungen diese Dateien lesen und die aktuellen Aussagen nebeneinander legen:

```text
AGENTS.md
meta/masterprompt_v6.md
systems/gameflow/speicher-fortsetzung.md
systems/gameflow/saveGame.v7.schema.json
systems/gameflow/saveGame.v7.export.schema.json
gameplay/kampagnenstruktur.md
runtime.js
package.json
scripts/smoke.sh
```

Danach gezielt diese Test-/Fixture-Dateien prüfen:

```text
tools/test_v7_schema_consistency.js
tools/test_v7_issue_pack.js
tools/test_continuity_output_contract.js
tools/test_hard_final_review_watchguard.js
tools/test_save.js
tools/test_load.js
tools/test_arena_schema.js
internal/qa/fixtures/savegame_v7_*.json
internal/qa/fixtures/continuity_output_contract_multi_load.json
internal/qa/fixtures/v7_parallel_core_refusal.json
```

Nutze danach diese Greps, um Driftstellen zu finden:

```bash
grep -RInE 'save_version|zr_version|"location"\s*:|"phase"\s*:|"character"\s*:|"party"\s*:|"team"\s*:|arc_dashboard|mission_in_episode' meta systems gameplay internal tools runtime.js

grep -RInE 'episode_plan|episode_start|episode_end|Paradoxon >=|Paradoxon ≥|Px-1|Px -1|Paradoxon.*RIFT|first_wins|queue_state|Banked|Pending|Cashout|Push' meta systems gameplay internal tools runtime.js

grep -RInE 'logs\.hud|logs\.psi|logs\.arena_psi|logs\.offline|logs\.kodex|logs\.alias_trace|logs\.squad_radio|logs\.foreshadow|logs\.fr_interventions' meta systems gameplay runtime.js tools internal
```

**Regel:** Wenn ein Fund nur Legacy-/Importbeispiel ist, muss er sehr klar als `IMPORT-ONLY / NICHT KOPIEREN / KEIN !save-BEISPIEL` markiert sein. Wenn er im Kanon steht, muss er mit strict v7 kompatibel sein.

---

## 3. Kanonische Datenarchitektur

### 3.1 Root-Struktur des v7-Exports

Der neue `!save`-Export darf nur diese Root-Felder haben:

```json
{
  "v": 7,
  "zr": "4.2.6",
  "save_id": "SAVE-...",
  "parent_save_id": null,
  "merge_id": null,
  "branch_id": "ANCHOR-main",
  "campaign": {},
  "characters": [],
  "economy": {},
  "logs": {},
  "summaries": {},
  "continuity": {},
  "arc": {},
  "ui": {},
  "arena": {}
}
```

`arena` bleibt optional, aber wenn vorhanden, ist es strikt validiert. Für die Spielvision empfehle ich: **kleinen Default-Arena-Block immer schreiben**, weil PvP-only dadurch erstklassig und routerfest wird. Falls ihr optional bleibt, müssen Masterprompt, Schema, Runtime und Load-Router dieselbe Entscheidung sprechen.

### 3.2 Spielercharaktere

`characters[]` ist die einzige Roster-Quelle für echte Spielercharaktere.

**Invariant:**

```json
"characters": {
  "type": "array",
  "minItems": 1,
  "maxItems": 5
}
```

NPCs gehören nicht als volle Spieler in `characters[]`, sondern in:

```json
"continuity": {
  "npc_roster": [],
  "active_npc_ids": []
}
```

So bleibt ein 5er-Team sauber, und Solo/NPC-Team bleibt kompatibel.

### 3.3 Storyspeicher ist nicht Logspeicher

Persistente Storytiefe liegt hier:

```json
"summaries": {
  "summary_last_episode": "",
  "summary_last_rift": "",
  "summary_active_arcs": ""
},
"arc": {
  "factions": {},
  "questions": [],
  "hooks": []
},
"continuity": {
  "roster_echoes": [],
  "shared_echoes": [],
  "convergence_tags": []
}
```

**Richtwerte für Kompaktheit:**

```text
summaries.summary_last_episode: max 800 Zeichen
summaries.summary_last_rift: max 600 Zeichen
summaries.summary_active_arcs: max 800 Zeichen
arc.questions[]: max 18 Einträge, je max 180 Zeichen
arc.hooks[]: max 18 Einträge, je max 220 Zeichen
continuity.roster_echoes[]: max 5, je 1 Satz
continuity.shared_echoes[]: max 6, je 1 Satz
continuity.convergence_tags[]: max 4 kurze Slugs
characters[].history.milestones[]: max 20, je max 140 Zeichen
```

Nicht als harte JSON-Schema-Stringlimits erzwingen, wenn das zu spröde wird; aber als Serializer-/Prune-Watchguard testen.

---

## 4. Logs: schlank, beweisfähig, nicht erzähllastig

### 4.1 Entscheidung

Für v7-Export gilt:

```json
"logs": {
  "trace": [],
  "hud": [],
  "psi": [],
  "arena_psi": [],
  "market": [],
  "artifact_log": [],
  "notes": [],
  "flags": {}
}
```

Diese Felder sind klein, leer billig und beweisrelevant:

- `trace[]` beweist Verlauf, Gates, Cluster, Merge, Economy-Audit.
- `hud[]` beweist wichtige Anzeigen/Toasts, aber nicht jeden HUD-Spam.
- `psi[]` beweist Psi-Heat/Reset/Costs außerhalb Arena.
- `arena_psi[]` beweist PvP-Sonderkosten wie Phase-Strike-Tax.
- `market[]` beweist Chronopolis/Shop-Käufe.
- `artifact_log[]` beweist Artefakt-Erwerb/-Status.
- `notes[]` hält knappe Merge-/Korrektur-/Debriefnotizen.
- `flags{}` hält Runtime-/Import-/Kontinuitätsflags.

Alle anderen alten Logspiegel (`offline`, `kodex`, `alias_trace`, `squad_radio`, `foreshadow`, `fr_interventions`, `field_notes`) sind entweder:

1. **runtime-/legacy-only** und werden vor Export in `trace[]`, `notes[]`, `arc.*` oder `summaries.*` verdichtet, oder
2. falls sie wirklich weiterhin persistieren sollen, müssen sie mit klaren Caps in **beide** Schemas, Masterprompt-Template und speicher-fortsetzung.md.

Empfehlung für diese Aufgabe: **Variante 1**. Story- und Merge-Magie nicht über viele Logarrays lösen, sondern über `continuity`/`arc`/`summaries`.

### 4.2 Caps

Serializer-/Prune-Caps:

```text
logs.trace: max 64
logs.hud: max 24
logs.psi: max 16
logs.arena_psi: max 16
logs.market: max 24
logs.artifact_log: max 32
logs.notes: max 24
```

Beim Pruning wird nie still gelöscht. Ältere Bedeutung wird verdichtet:

```text
trace/hud/psi/arena_psi -> summaries oder notes
market/artifact_log -> character history milestone oder artifact_log Kurzstatus
alte Branchdetails -> shared_echoes / roster_echoes / convergence_tags
```

---

## 5. Schema-Patches

### 5.1 `systems/gameflow/saveGame.v7.export.schema.json`

Patch-Ziele:

1. Root `additionalProperties:false` beibehalten.
2. Root-Required wie oben.
3. `characters.maxItems = 5`.
4. `logs.required` erweitern auf:

```json
["trace", "hud", "psi", "arena_psi", "market", "artifact_log", "notes", "flags"]
```

5. `logs.properties` ergänzen:

```json
"hud": { "type": "array", "maxItems": 24 },
"psi": { "type": "array", "maxItems": 16 },
"arena_psi": { "type": "array", "maxItems": 16 }
```

6. `continuity` streng machen:

```json
"roster_echoes": {
  "type": "array",
  "maxItems": 5,
  "items": {
    "type": "object",
    "required": ["char_id"],
    "additionalProperties": true,
    "properties": {
      "char_id": { "type": "string" },
      "tone": { "type": "string" },
      "text": { "type": "string" }
    }
  }
},
"shared_echoes": {
  "type": "array",
  "maxItems": 6,
  "items": {
    "type": "object",
    "required": ["tag"],
    "additionalProperties": true,
    "properties": {
      "tag": { "type": "string" },
      "scope": { "type": "string", "enum": ["shared", "rumor", "campaign", "personal"] },
      "text": { "type": "string" }
    }
  }
},
"convergence_tags": { "type": "array", "maxItems": 4, "items": { "type": "string" } },
"npc_roster": { "type": "array", "maxItems": 6 },
"active_npc_ids": { "type": "array", "maxItems": 4 }
```

7. `arena` reparieren. Siehe Abschnitt 6.

### 5.2 `systems/gameflow/saveGame.v7.schema.json`

Das tolerant Import-Schema darf Legacy-/Join-Felder akzeptieren, muss aber Zielpfade prüfen:

- `characters.maxItems` im Import nicht zwingend hart machen, aber Normalizer muss >5 echte Spieler blocken oder als NPC/Importfehler behandeln.
- `logs.hud`, `logs.psi`, `logs.arena_psi` akzeptieren.
- Legacy-Felder tolerieren, aber `load_deep()`/Normalizer exportieren danach nur strict v7.
- `location`/`phase` auf Root nur Import, nie Export.

---

## 6. Arena/PvP: Runden-Checkpoint in den Hub einfügen

### 6.1 Problem

Das Spiel soll nach jeder PvP-Runde/Serie speichern und in einem neuen Chat weiterladen können, ohne aktiven Arena-State oder Matchphysik zu speichern.

### 6.2 Lösung: HQ-Arena-Lounge als Save-Schleuse

Nach jeder abgeschlossenen Runde/Serie führt die KI-SL in eine **HQ-Arena-Lounge / Quarzatrium-Schleuse** zurück. Dort ist der Matchlauf beendet, aber die Serie kann als Risiko-Checkpoint weiterexistieren.

Save erlaubt nur bei:

```json
"arena": {
  "active": false,
  "phase": "idle|completed",
  "queue_state": "idle|completed"
}
```

Save verboten bei:

```text
queue_state = searching|matched|staging|active
active = true
phase = combat|queue|staging|running
```

### 6.3 Neuer kleiner Arena-Karriereblock

`arena` sollte, wenn vorhanden, so aussehen:

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
  "pending_rewards": {
    "cu": 0,
    "xp": 0,
    "arena_rep": 0,
    "multiplier": 1.0,
    "risk": "none"
  },
  "banked_rewards": {
    "cu": 0,
    "xp": 0,
    "arena_rep": 0
  },
  "rewarded_runs_this_contract": 0,
  "first_wins": {},
  "defeated_types": [],
  "last_reward_episode": null,
  "wins_player": 0,
  "wins_opponent": 0,
  "match_policy": "sim"
}
```

Wenn das Repo bereits konsequent `match_policy:"safe"` nutzt, entweder überall auf `safe` lassen oder überall auf `sim` umstellen. Nicht mischen. Meine Empfehlung: `sim`, weil der Block keine Safety-Policy meint, sondern Matchauswertung.

### 6.4 `first_wins` fixen

Strict-Schema:

```json
"first_wins": {
  "type": "object",
  "additionalProperties": {
    "type": "integer",
    "minimum": 0,
    "maximum": 3
  }
}
```

Nicht integer.

### 6.5 Cashout/Push-Regel

- **Cashout:** `pending_rewards` wird gebankt/verbucht, `characters[].xp`, `economy.hq_pool`/Wallets und Arena-Ruf werden aktualisiert. Danach `pending_rewards` resetten, `queue_state="completed"`, HQ-Save anbieten.
- **Push:** `pending_rewards` bleibt bestehen, `streak` steigt, `risk="pending"`. Die Gruppe darf in der HQ-Arena-Lounge speichern, aber beim nächsten Load muss klar sein: Pending ist nicht sicher. Startet sie wieder, wird `arena.resume_token` genutzt.
- **Loss nach Push:** Pending ganz oder größtenteils löschen, Trostreward optional in `banked_rewards`, dann HQ-Save anbieten.

### 6.6 Dateien

Patch in:

```text
gameplay/kampagnenstruktur.md
systems/gameflow/speicher-fortsetzung.md
meta/masterprompt_v6.md
systems/gameflow/saveGame.v7.export.schema.json
systems/gameflow/saveGame.v7.schema.json
runtime.js
tools/test_arena_schema.js
internal/qa/fixtures/savegame_v7_arena_round_checkpoint.json   # neu
```

### 6.7 Test

Neuer Test `tools/test_arena_round_checkpoint.js`:

- Erzeugt Save mit `pending_rewards.cu > 0`, `active=false`, `queue_state=completed`.
- Strict-v7 akzeptiert.
- Load zeigt Arena-Router mit `Cashout` oder `Push`.
- `campaign.px` bleibt unverändert.
- `!save` während `queue_state=active` blockt.
- `first_wins` als Objekt `{ "1": 2 }` wird akzeptiert, integer wird abgelehnt.

In `scripts/smoke.sh` aufnehmen.

---

## 7. Smart-Merge-Vertrag

### 7.1 Grundregel

Mehrere gepostete JSONs in einem neuen Chat:

1. Erster gültiger Save = **Session-Anker**.
2. Alle weiteren Saves = **Join-/Merge-Importe**.
3. Kampagnenwahrheit kommt vom Session-Anker, außer ein kanonisches Split-Protokoll sagt etwas anderes.
4. Persönliche Wahrheit kommt vom neuesten Save pro `characters[].id`.
5. Widersprüche werden nicht still überschrieben. Sie werden als `logs.flags.continuity_conflicts[]` und als Story-Hook/Echo gespeichert.

### 7.2 Persönliche Wahrheit pro Charakter

Für jeden `characters[].id`:

Persistiere aus dem neuesten persönlichen Stand:

```text
lvl, xp, level_history, attr, lp/lp_max, talents, equipment, implants,
carry, quarters_stash, vehicles, reputation, wallet, history
```

Neuester Stand wird bestimmt über:

1. `save_id` ISO-Zeit, falls parsebar.
2. `logs.flags.last_save_at`, falls vorhanden.
3. Import-Reihenfolge als Fallback.

Bei Gleichstand gewinnt der zuletzt importierte persönliche Stand, aber der Konflikt wird geloggt.

### 7.3 Kampagnenwahrheit

Session-Anker gewinnt für:

```text
campaign.episode
campaign.mission
campaign.mode
arc.factions
arc.questions
arc.hooks
summaries.* als Basiserzählung
```

Aus Imports werden nur Hooks/Echos übernommen, nicht blind der ganze Kampagnenfortschritt.

### 7.4 Kanonischer Split

Ein Split ist kanonisch, wenn alle Branches dieselbe `continuity.split.family_id` tragen und `expected_threads[]`/`resolved_threads[]` zusammenpassen.

Bei Split-Erzeugung:

```json
"continuity": {
  "split": {
    "family_id": "EP1-BERLIN43-FORK-01",
    "thread_id": "EP1-BERLIN43-A1939",
    "expected_threads": ["EP1-BERLIN43-A1939", "EP1-BERLIN43-B1986"],
    "resolved_threads": ["EP1-BERLIN43-A1939"],
    "convergence_ready": false
  }
}
```

Branch A: 3 Spieler nach 1939. Branch B: 2 Spieler nach 1986.

Bei Rejoin:

```json
"continuity": {
  "split": {
    "family_id": "EP1-BERLIN43-FORK-01",
    "thread_id": "HQ-MERGE",
    "expected_threads": ["EP1-BERLIN43-A1939", "EP1-BERLIN43-B1986"],
    "resolved_threads": ["EP1-BERLIN43-A1939", "EP1-BERLIN43-B1986"],
    "convergence_ready": true
  }
}
```

### 7.5 Merge-Ausgabe ist Teil des Features

Beim Mehrfach-Load muss vor dem HQ-Router immer ein **Kontinuitätsrückblick** kommen. Nicht nur Tabelle.

Pflichtstruktur:

1. **Session-Anker:** Wo steht die Welt laut führendem Save?
2. **Rückkehrer/Joiner:** Wer bringt welche persönliche Wahrheit mit?
3. **NPC-Lagebild:** Wer ist anwesend, offscreen, verändert, fehlend?
4. **Gemeinsame Nachwirkungen:** Welche Branch-Echos prägen die Welt?
5. **Konvergenz-Folge:** Was entsteht aus dem Widerspruch als neuer Hook?

Danach kurz die technische Merge-Tabelle zeigen:

```text
Feld | Quelle | Entscheidung | Warum
campaign | Anchor | behalten | Session-Anker
characters.AGENT-04 | Import B | übernommen | neuer persönlicher Stand
arc.hooks | Union+Prune | beide behalten | Story-Hooks kompakt
px_state | consumed > pending_reset > stable | ... | keine Px-Reanimation
arena | HQ-normalisiert | active=false | SaveGuard
```

### 7.6 Sinnbrüche als Spielmaterial

Wenn 1939 und 1986 logisch schwer zusammenpassen, nicht versuchen, alles glattzubügeln. Verwandle den Bruch in:

```text
Gerücht
Anomalie
Boss-Tell
Fraktionsreaktion
Alt-Route
NPC-Reaktion
```

Der Save speichert dafür nur ein kompaktes Echo:

```json
"shared_echoes": [
  {
    "tag": "echo:morgenrot",
    "scope": "campaign",
    "text": "1939 und 1986 bestätigten unabhängig das Codewort MORGENROT."
  }
]
```

### 7.7 Spieler-Korrektur

Wenn Spieler nach dem Merge sagen „Nein, so war das nicht gemeint“, soll die KI-SL das nicht als Systemfehler behandeln. Sie setzt eine knappe Korrektur:

```json
"logs": {
  "notes": [
    "Korrektur: AGENT-04 hat Dr. Voss 1986 nicht verraten, sondern nur seine Akte kopiert."
  ]
}
```

Optional zusätzlich:

```json
"continuity": {
  "shared_echoes": [
    {
      "tag": "correction:voss-1986",
      "scope": "shared",
      "text": "Voss lebt; nur die Akte wurde kopiert."
    }
  ]
}
```

So bleibt das P&P-Gefühl erhalten: Die Gruppe kann die SL nachjustieren.

---

## 8. Personal-Export beim Verlassen einer Gruppe

### 8.1 Ziel

Wenn ein Spieler die Gruppe verlässt, nimmt er **seinen Charakter** mit, aber nicht die vollen privaten Daten der anderen. Er nimmt „ein bisschen Gruppenhistorie“ als Echo mit.

### 8.2 Neuer/klargestellter Exportpfad

Im HQ erlauben:

```text
!save               -> aktueller Gruppensave
!save character ID  -> portabler Einzelsave für genau diesen Charakter
```

Natürliche Sprache muss auch funktionieren:

```text
"Ich exportiere nur meinen Char."
"Kira verlässt die Gruppe und nimmt ihren Stand mit."
```

### 8.3 Einzelsave-Struktur

Einzelsave:

- `characters[]`: genau 1 Eintrag.
- `economy.hq_pool`: 0 oder anteiliger vereinbarter Gruppenanteil.
- `characters[0].wallet`: persönliche Wallet bleibt.
- `summaries`: kurzer Gruppenkontext.
- `continuity.shared_echoes`: max 3 Gruppenechos.
- `continuity.roster_echoes`: max 2 Beziehungs-/NPC-Echos.
- `arc.hooks`: nur Hooks, die dieser Charakter plausibel kennt oder mitnimmt.
- Keine vollen anderen Spielercharaktere.

### 8.4 Test

Neuer Test `tools/test_v7_personal_export.js`:

- 5er-Gruppensave -> Export für `AGENT-03`.
- Output hat `characters.length === 1`.
- Keine Ausrüstung/Wallet/History anderer Spieler im Export.
- Mindestens ein `shared_echo` bleibt.
- Strict-v7 akzeptiert.
- Reimport in andere Gruppe bringt persönliche Wahrheit + Echo, aber nicht alte Gruppe als Roster.

---

## 9. Episode-Plan: bewusst nicht voll persistieren

### 9.1 Entscheidung

`campaign.episode_plan`, `campaign.episode_start`, `campaign.episode_end` sollen **nicht** in den kanonischen v7-Export.

Warum: Das bläht JSONs auf, macht alte Pläne zu starr und nutzt die KI-SL weniger. ZEITRISS soll nicht zehn Missions-Seeds als Datenbank mitschleppen, sondern sichtbare Routen, offene Fragen und Hooks.

### 9.2 Patch

In `gameplay/kampagnenstruktur.md` ändern:

Alt-Sinn:

```text
episode_seed_make() legt zehn Missions-Seeds in campaign.episode_plan ab ...
```

Neuer Sinn:

```text
episode_seed_make() erzeugt einen privaten Director-Plan der KI-SL. Persistiert werden nur sichtbare/entschiedene Routen als arc.hooks[], summaries.* und continuity.*. Ein vollständiger Zehnerplan landet nicht im v7-Save.
```

### 9.3 Berlin-43-Beispiel

Nach Mission Berlin 1943:

```json
"arc": {
  "hooks": [
    {
      "tag": "route:1939",
      "text": "Akte Morgenrot öffnet eine Spur ins Jahr 1939."
    },
    {
      "tag": "route:1986",
      "text": "Ein Neon-Archivsignal verweist auf 1986."
    }
  ]
}
```

Beim Split ordnet die SL die Hook-Tags den Branches zu, aber speichert keinen langen Masterplan.

---

## 10. Paradoxon-/Encounter-Drift bereinigen

### 10.1 Ziel

Px bleibt positives Resonanz-/Reward-System. Fehler erhöhen Druck, nicht negative Fortschrittswährung.

### 10.2 Grep und Patch

Suche in:

```text
gameplay/kampagnenstruktur.md
gameplay/kreative-generatoren-begegnungen.md
gameplay/kreative-generatoren-missionen.md
master-index.json
core/zeitriss-core.md
characters/zustaende.md
```

Ersetze alte Sprache:

```text
Paradoxon +1 bei Fehlern
Paradoxon >= 2 -> RIFT OPS
Px-1 als Item-Risiko
```

durch:

```text
Druck / Heat / Timeline-Echo / Noise
Fehler erhöhen Druck. Gute Einsätze erhöhen Px. Nur Px 5 erzeugt via ClusterCreate() spielbare Rift-Seeds.
Rift-Ops starten nur aus offenen campaign.rift_seeds[] nach ClusterCreate() und gültigem Gate.
```

Wenn `master-index.json` Artefakt-Risiken wie `Px-1` enthält, entweder:

- auf `Heat+1`, `Stress+1`, `SYS-1`, `Druck+1` ändern, oder
- als Legacy-/Importpool markieren, falls nicht aktiv geladen.

### 10.3 Test

Neuer Watchguard `tools/test_px_language_watchguard.js`:

- Kein `Paradoxon >= 2`, `Paradoxon ≥2`, `Px-1`, `Px -1` in aktiven WS-Dateien.
- Erlaubt nur in klar markierten Legacy-/Import-Hinweisen.
- `campaign.px` und `ClusterCreate()` bleiben als positive Payoff-Sprache erhalten.

In `scripts/smoke.sh` aufnehmen.

---

## 11. Masterprompt-Patches

Datei: `meta/masterprompt_v6.md`

### 11.1 Save-Template synchronisieren

Das strict-v7-HQ-Template muss der Export-Schema-Wahrheit entsprechen:

- Kein Root `location`.
- Kein Root `phase`.
- Kein Root `character`.
- `continuity.last_seen.mode="hq"`, `location="HQ"`.
- `logs` enthält `trace`, `hud`, `psi`, `arena_psi`, `market`, `artifact_log`, `notes`, `flags`.
- `arena.first_wins={}`.
- Arena-Checkpointfelder ergänzen, falls Arena-Default immer geschrieben wird.
- `characters[].level_history={}` bleibt im Character.
- `characters[].attr` nutzt gültige Startwerte, keine Nullen.

### 11.2 Load/Multi-Load härten

Im Load-Abschnitt ergänzen:

```text
Mehrfach-Load erzeugt immer eine In-World-Konvergenzszene plus Merge-Tabelle. Die Tabelle ersetzt nicht die Erzählung. Mindestens ein importiertes Echo muss in den nächsten zwei Sitzungsblöcken sichtbar wiederkehren.
```

### 11.3 Personal-Export ergänzen

Im Save-Abschnitt ergänzen:

```text
Im HQ kann ein Spieler einen Einzelcharakter exportieren. Der Einzel-Export enthält genau einen characters[]-Eintrag plus kompakte Gruppen-Echos; keine vollständigen Bögen anderer Spieler.
```

### 11.4 PvP-Checkpoint ergänzen

```text
Nach abgeschlossener Arena-Runde/Serie führt die SL in die HQ-Arena-Lounge. Dort ist !save erlaubt, solange arena.active=false und queue_state idle|completed ist. Pending-Rewards dürfen im Save stehen, sind aber beim Push weiterhin riskant.
```

---

## 12. `speicher-fortsetzung.md` Patches

Datei: `systems/gameflow/speicher-fortsetzung.md`

### 12.1 SSOT-Abschnitt aktualisieren

Am Anfang klarstellen:

```text
v7-Export = Charakterbogen + Weltanker + Kompakt-Echos. Keine Volltranskripte. Keine Root-Laufzeitfelder. HQ ist der einzige Savepunkt. Der Save wird klein gehalten, indem ältere Details nach summaries/continuity/arc verdichtet werden.
```

### 12.2 Logs-Vertrag bereinigen

Den Pseudocode-Required-Block so anpassen, dass Runtime-Bridge und v7-Export nicht vermischt werden. Zwei Listen:

```text
Runtime-/Import-Bridge required: darf Legacy-Helfer enthalten.
Kanonischer v7-Export required: trace, hud, psi, arena_psi, market, artifact_log, notes, flags.
```

### 12.3 Legacy-Beispiel entschärfen

Direkt über große JSON-Blöcke:

```text
IMPORT-ONLY / NICHT KOPIEREN / KEIN !save-BEISPIEL
Dieses Beispiel darf von der KI-SL niemals als Neu-Export imitiert werden.
Das einzige kopierfähige !save-Beispiel ist das strict-v7-HQ-Template im Masterprompt.
```

Wenn möglich, Legacy-Blöcke in Appendix verschieben.

### 12.4 Smart-Merge und Personal-Export dokumentieren

Die Abschnitte aus diesem Briefing in kurzer WS-tauglicher Sprache verankern:

- Session-Anker.
- Persönliche Wahrheit.
- Kanonischer Split mit `family_id`.
- Branch-Import ohne Protokoll.
- Personal-Export.
- Pflichtausgabe Merge-Intro + Tabelle.
- Echo-Fortwirkung.

### 12.5 Größe/Caps dokumentieren

Die Caps aus Abschnitt 4/3 in `speicher-fortsetzung.md` verankern. Wichtig: **Prune verdichtet, löscht nicht still.**

---

## 13. Runtime-Patches

Datei: `runtime.js`

Nicht die Spiellogik neu erfinden. Runtime ist Test-/CI-Brücke. Sie muss aber den Vertrag spiegeln.

### 13.1 Normalizer/Serializer

Prüfen und ggf. ergänzen:

```text
normalize_v7_export(save)
prepare_save_logs(save.logs)
prepare_save_continuity(save.continuity)
prepare_save_arena(save.arena)
prune_for_v7_export(save)
```

Mindestverhalten:

- Entfernt Root-Legacy-Felder beim Export.
- Setzt `continuity.last_seen.mode="hq"`, `location="HQ"` bei HQ-Save.
- Erzwingt `characters.length <= 5` für Spieler.
- Ergänzt leere Pflichtarrays.
- Pruned Logs/Arc/History-Caps.
- Arena active/queue-state blockt Save, außer `idle|completed`.
- `arena.first_wins` wird als Objekt normalisiert.
- `pending_rewards`/`banked_rewards` werden defaulted.

### 13.2 Multi-Load/Merge-Helfer

Falls noch nicht vorhanden, kleine Helfer ergänzen:

```text
extract_json_blocks(inputText)
load_many_deep(inputText)
merge_v7_saves(anchor, imports)
select_latest_character_state(charId, candidates)
compact_import_echoes(anchor, imports)
```

Auch wenn Produktiv-Load im Chat durch die KI-SL passiert, helfen diese Funktionen für Fixtures/Tests.

### 13.3 Personal-Export-Helfer

Optional, aber für Tests sehr nützlich:

```text
export_character_save(groupSave, charId, options={})
```

Mindestverhalten:

- genau 1 Character.
- shared_echoes max 3.
- roster_echoes max 2.
- keine vollen anderen Charakterdaten.
- strict v7.

---

## 14. Fixtures aktualisieren

Alle v7-Fixtures unter `internal/qa/fixtures/savegame_v7_*.json` prüfen:

### 14.1 Muss raus aus neuen v7-Fixtures

```text
location
phase
save_version
zr_version
character
party
team
arc_dashboard
campaign.mission_in_episode
characters[].attributes
arc.open_seeds
arc.open_questions
arc.timeline
```

Ausnahme nur in ausdrücklich benannten Legacy-Import-Fixtures.

### 14.2 Muss rein

```text
save_id
parent_save_id
merge_id
branch_id
campaign.px_state
characters[].level_history
logs.trace
logs.hud
logs.psi
logs.arena_psi
logs.market
logs.artifact_log
logs.notes
logs.flags.runtime_version
logs.flags.imported_saves
logs.flags.continuity_conflicts
summaries.*
continuity.last_seen
continuity.split
continuity.roster_echoes
continuity.shared_echoes
continuity.convergence_tags
continuity.npc_roster
continuity.active_npc_ids
arc.factions/questions/hooks
ui.* sieben Pflichtfelder
```

### 14.3 Neue Fixtures

Anlegen:

```text
internal/qa/fixtures/savegame_v7_split_berlin43_1939_branch.json
internal/qa/fixtures/savegame_v7_split_berlin43_1986_branch.json
internal/qa/fixtures/savegame_v7_merge_berlin43_3_2_rejoin.json
internal/qa/fixtures/savegame_v7_arena_round_checkpoint.json
internal/qa/fixtures/savegame_v7_personal_export_from_group.json
```

---

## 15. Tests ergänzen/ändern

### 15.1 `tools/test_v7_schema_consistency.js`

Erweitern:

- Alle v7-Fixtures dürfen keine Root-Legacy-Felder haben.
- HQ-Fixtures: `continuity.last_seen.mode !== core/rift/arena/chronopolis`, sondern `hq`.
- `characters.length <= 5`.
- `logs.hud`, `logs.psi`, `logs.arena_psi` sind Arrays.
- `continuity.*` Caps und Pflichtformate.
- `arena.first_wins` Objekt, nicht Integer.
- `arena.pending_rewards`/`banked_rewards` bei Arena-Fixtures prüfen.
- Canonical Template im Masterprompt enthält dieselben Pflichtfelder.

### 15.2 Neuer Test: `tools/test_v7_smart_merge_3_2.js`

Szenario:

- Parent: Berlin 1943 abgeschlossen.
- Branch A: 3 Chars nach 1939.
- Branch B: 2 Chars nach 1986.
- Merge:
  - 5 Chars.
  - `merge_id` gesetzt.
  - `continuity.split.convergence_ready=true`.
  - `resolved_threads` enthält beide.
  - `shared_echoes` enthält mindestens einen verbindenden Hook.
  - `roster_echoes` enthält persönliche Rückkehrer-Echos.
  - `logs.flags.imported_saves.length >= 2`.
  - `logs.flags.continuity_conflicts` existiert auch leer.
  - `continuity.last_seen.mode="hq"`.
  - JSON bleibt unter Budget.

### 15.3 Neuer Test: `tools/test_arena_round_checkpoint.js`

Siehe Abschnitt 6.7.

### 15.4 Neuer Test: `tools/test_v7_personal_export.js`

Siehe Abschnitt 8.4.

### 15.5 Neuer Test: `tools/test_px_language_watchguard.js`

Siehe Abschnitt 10.3.

### 15.6 Smoke aufnehmen

`scripts/smoke.sh` ergänzen:

```bash
node tools/test_v7_smart_merge_3_2.js > out/v7_smart_merge_3_2.log
grep "v7-smart-merge-3-2-ok" out/v7_smart_merge_3_2.log

node tools/test_arena_round_checkpoint.js > out/arena_round_checkpoint.log
grep "arena-round-checkpoint-ok" out/arena_round_checkpoint.log

node tools/test_v7_personal_export.js > out/v7_personal_export.log
grep "v7-personal-export-ok" out/v7_personal_export.log

node tools/test_px_language_watchguard.js > out/px_language_watchguard.log
grep "px-language-watchguard-ok" out/px_language_watchguard.log
```

---

## 16. Akzeptanztests als simulierte Spielerflows

### Flow A: Neuer Solo-/Gruppenstart

1. Gruppe startet klassisch.
2. Charakterbogen vollständig.
3. HQ-Heimkehr.
4. `!save`.
5. JSON strict v7.
6. Neuer Chat, JSON rein.
7. Keine Chargen-Frage, sondern Rückblick + HQ-Router.

### Flow B: Berlin 43 -> Split 1939/1986 -> Rejoin

1. Nach Mission Berlin 1943 bietet SL zwei Routen: 1939 und 1986.
2. Gruppe entscheidet 3/2.
3. SL erzeugt zwei Branch-Saves mit derselben `family_id`.
4. Zwei Chatfenster spielen getrennt.
5. Beide schließen im HQ mit `!save`.
6. Neuer Chat: beide Saves einfügen.
7. SL erzeugt in-world Konvergenzintro, technische Merge-Tabelle, 5er-Roster, HQ-Router.
8. `!save` erzeugt neuen 5er-Merge-Save.

### Flow C: Spieler verlässt Gruppe

1. 5er-Gruppe im HQ.
2. Spieler sagt: „Ich exportiere nur meinen Char.“
3. SL gibt Einzel-v7-Save aus.
4. Save enthält genau einen Charakter plus kompakte Gruppenechos.
5. In anderer Gruppe geladen: persönlicher Stand bleibt, alte Gruppe wirkt als Echo/Hook, nicht als Vollroster.

### Flow D: PvP-only Karriere

1. Char startet Arena.
2. Best-of-Three-Serie abgeschlossen.
3. Pending-Rewards sichtbar.
4. SL führt in HQ-Arena-Lounge.
5. `!save` erlaubt.
6. Neuer Chat, Save rein.
7. Arena-Router bietet Cashout oder Push.
8. Push verliert: Pending wird reduziert/gelöscht, Trost optional, HQ-Save.
9. Cashout: XP/CU/Ruf verbucht, Level-Up-Gate, `level_history`, Save.
10. `campaign.px` bleibt unverändert.

### Flow E: Chronopolis

1. Vor Schleuse verpflichtender HQ-Deepsave.
2. In Chronopolis kein Save.
3. Lebend raus: Schleusen-Debrief, Markt/Asset/Trace verdichtet.
4. HQ-Save.
5. Beim Merge mit anderer Gruppe bleiben Chronopolis-Ausgaben als Log/Hook, aber überschreiben nicht den Session-Anker.

---

## 17. JSON-Größenbudget

Zielwerte für echte Copy/Paste-Stabilität:

```text
Solo normal: Ziel < 12 KB
5er normal: Ziel < 45 KB
5er High-Level: Ziel < 70 KB
Hard Warning: > 90 KB nur mit deutlichem Grund
```

Nicht blind über Byte-Limit scheitern lassen, falls High-Level-Gear viel enthält. Aber Tests sollen zeigen, dass Caps greifen und JSON nicht unkontrolliert wächst.

Neuer optionaler Test:

```text
tools/test_v7_save_budget.js
```

Prüft:

- Caps der Arrays.
- Keine Legacy-Doppelpfade.
- Fixtures unter Budget oder mit begründetem `logs.flags.budget_exception`.

---

## 18. Commit-/PR-Text

Branch:

```bash
git checkout -b fix/v7-smart-save-merge
```

Subject:

```text
fix(save): stabilisiere v7 Smart-Merge und Arena-Checkpoints
```

Commit-Body nach AGENTS.md:

```markdown
## Was
- Vereinheitlicht v7-Exportvertrag in Masterprompt, Speicher-SSOT, strict/tolerant Schema und Fixtures.
- Ergänzt Smart-Merge für 3/2-Splits, Personal-Export und PvP-Runden-Checkpoints im HQ-Hub.
- Fügt Watchguards für Schema, Merge, Arena-Checkpoint, Personal-Export und Px-Sprachdrift hinzu.

## Warum
- Save = Charakter/Weltanker muss serverloses Gruppenspiel tragen: Split, Solo, Rejoin, PvP und Chronopolis über neue Chatfenster.
- Vorher drifteten Schema, Beispiele, Arena-Vertrag und Runtime-Brücke auseinander.

## Wichtige Entscheidungen
- Storytiefe lebt in summaries/arc/continuity, nicht in langen Logs.
- Episode-Pläne bleiben Director-/Runtime-only; persistiert werden sichtbare Route-Hooks.
- Arena-Pending darf nach abgeschlossener Runde in der HQ-Arena-Lounge gespeichert werden, aber nie während aktivem Match.
- Personal-Export enthält nur einen Charakter plus kompakte Gruppenechos.

## Verifikation
- bash scripts/smoke.sh
- node tools/test_v7_smart_merge_3_2.js
- node tools/test_arena_round_checkpoint.js
- node tools/test_v7_personal_export.js
- node tools/test_px_language_watchguard.js
```

---

## 19. Abschlusskriterien

Der Patch ist fertig, wenn alles wahr ist:

- [ ] `bash scripts/smoke.sh` grün.
- [ ] Strict-v7-Export und Masterprompt-Template sind deckungsgleich.
- [ ] Keine neuen v7-Fixtures mit Root `location`/`phase`/`character`/`party`/`team`.
- [ ] HQ-Saves nutzen `continuity.last_seen.mode="hq"`.
- [ ] `characters[]` max 5 echte Spieler.
- [ ] NPC-Kontinuität über `continuity.npc_roster[]`.
- [ ] `logs.hud`, `logs.psi`, `logs.arena_psi` sind im v7-Vertrag geklärt.
- [ ] `arena.first_wins` ist Objekt.
- [ ] Arena-Runden-Checkpoint speichert Pending/Banked ohne aktive Matchphysik.
- [ ] Personal-Export funktioniert und leakt keine vollständigen anderen Spielerbögen.
- [ ] Berlin43 3/2-Split-Rejoin als Fixture/Test vorhanden.
- [ ] Episode-Plan ist runtime-only; sichtbare Routen liegen in `arc.hooks[]`.
- [ ] Alte Paradoxon-Strafsprache ist aus aktiven Pfaden raus.
- [ ] Legacy-Beispiele sind optisch unmissverständlich entwaffnet.
- [ ] Mehrfach-Load erzeugt in-world Konvergenzintro plus Merge-Tabelle.

---

## 20. Leitmotiv für die Umsetzung

Nicht größer machen. Schlauer machen.

Der Save muss klein genug sein, dass Spieler ihn kopieren wollen. Er muss reich genug sein, dass die KI-SL daraus eine lebendige Welt rekonstruiert. Und er muss klar genug sein, dass fünf Menschen ihre Charaktere wie Pen-&-Paper-Bögen mitnehmen, trennen, mergen und wieder auseinanderziehen können.

**HQ ist Heimat. Missionen sind Instanzen. Arena ist Karriere. Chronopolis ist Raubzug. Der Save ist die Welt.**
