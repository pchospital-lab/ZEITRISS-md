# CODEX-BRIEFING — ZEITRISS v7 Jubelgate / Contract Cleanup III

## Auftrag

Flo hat den Save-/Merge-Vertrag weiter nachgeschärft. Bitte prüfe und fixe den aktuellen Repo-Stand so, dass danach ein echter **Jubeltest** möglich ist: kein Redesign, kein Feature-Bloat, sondern die letzten Vertragsdrifts schließen.

Zielbild bleibt:

> Save = portabler Charakterbogen.  
> Gruppen können splitten, getrennt spielen, später mehrere JSONs laden und als plausible, kompakte Kontinuität wieder zusammengeführt werden.  
> Bis zu 5 Spieler.  
> Kein Server.  
> Kein langes Save-JSON.  
> Die KI-SL nutzt Hooks, Echos, Summaries und Merge-Intro, nicht Volltranskripte.

## Gesamturteil des Reviews

**Fast Jubeltest, aber noch kein finaler Jubeltest.**

Die neue Vision ist sichtbar angekommen: Session-Anker, Smart-Merge 3/2, Personal-Export, Arena-Runden-Checkpoint, Px-Sprachguard und Save-Budget-Watchguard sind im Repo angelegt und in `scripts/smoke.sh` verankert.

Der Rest ist kein kreativer Umbau mehr. Es ist ein **Jubelgate-Pass**: Masterprompt-Template, strict Export-Schema, Arena-Doku, Encounter-Pools, Fixtures und Watchguards müssen dieselbe Wahrheit sprechen.

---

## 0. Vor dem Patch lesen

Bitte zuerst vollständig lesen:

- `AGENTS.md`
- `meta/masterprompt_v6.md`
- `systems/gameflow/speicher-fortsetzung.md`
- `systems/gameflow/saveGame.v7.export.schema.json`
- `systems/gameflow/saveGame.v7.schema.json`
- `gameplay/kampagnenstruktur.md`
- `systems/toolkit-gpt-spielleiter.md`
- `tools/test_v7_schema_consistency.js`
- `tools/test_v7_issue_pack.js`
- `tools/test_v7_smart_merge_3_2.js`
- `tools/test_arena_round_checkpoint.js`
- `tools/test_v7_personal_export.js`
- `tools/test_px_language_watchguard.js`
- `scripts/smoke.sh`
- alle `internal/qa/fixtures/savegame_v7_*.json`

Pflicht: Keine Eigenregeln erfinden. Was im Runtime-Wissen steht, muss mit Schema/Fixtures/Tests übereinstimmen.

---

## 1. Kritischer Drift: strict Export-Schema ist noch alt

### Befund

`systems/gameflow/saveGame.v7.export.schema.json` ist als kanonischer strict Export markiert, aber nicht auf dem Stand des aktuellen Save-/Merge-Vertrags.

Aktuelle Driftpunkte:

- `arena.first_wins` ist im strict Export noch `integer`, während Arena-Regeln und Fixtures `first_wins[tier]` als Objekt nutzen.
- `arena.pending_rewards`, `arena.banked_rewards`, `arena.queue_state`, `arena.contract_id`, `arena.streak` fehlen, obwohl der Arena-Runden-Checkpoint genau diese Felder braucht.
- `arena.resume_token` ist im strict Export nur `object|null`, die Fixture nutzt aber einen kompakten String-Token.
- `logs.hud`, `logs.psi`, `logs.arena_psi` fehlen im strict Export, obwohl SaveGuard/Fixtures/Toolkit sie als beweisrelevante Logs nutzen.
- `ui.intro_seen`, `ui.dice.debug_rolls` und eventuell `campaign.entry_choice_skipped` sind in Runtime-Doku/Toolkit relevant, aber strict nicht exportfähig.
- `campaign.episode_start` und `campaign.episode_end` werden in `kampagnenstruktur.md` als persistent erwähnt, fehlen aber im strict Export.
- Das strict Schema verlangt `arena.active`, `phase`, `mode`, lässt aber gleichzeitig den aktuellen Arena-Checkpoint nicht durch, weil genau die neuen HQ-safe Felder fehlen.

### Patch

`saveGame.v7.export.schema.json` an den aktuellen kanonischen Save anpassen.

Empfohlene Richtung:

```json
"campaign": {
  "episode": 1,
  "mission": 0,
  "px": 0,
  "px_state": "stable",
  "mode": "mixed",
  "rift_seeds": [],
  "entry_choice_skipped": false,
  "episode_start": null,
  "episode_end": null
}
```

`episode_plan` NICHT speichern. Wenn ein Regieplan existiert, bleibt er Director-/Runtime-only. Nur sichtbare Start-/Endanker und Hooks in `arc.hooks[]`/`summaries.*` speichern.

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

Oder, falls ihr bewusst schlanker bleiben wollt: alle Runtime-Logs, die nicht strict exportiert werden, müssen vor Export deterministisch nach `logs.trace[]`/`logs.notes[]` verdichtet werden. Dann müssen aber `speicher-fortsetzung.md`, Toolkit und Fixtures entsprechend angepasst werden. Nicht halb/halb.

Für Arena bitte klar first-class machen:

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

Wichtig: Arena speichert **Karrierekern + HQ-safe Sentinel**, niemals laufende Matchphysik.

### Akzeptanz

- `first_wins` ist im strict Export ein Objekt `{ tier: count }`, kein Integer.
- `pending_rewards` und `banked_rewards` sind strict exportfähig.
- `queue_state` ist strict exportfähig, aber nur `idle|completed|none` oder vergleichbar HQ-safe.
- `resume_token` akzeptiert kompakt `string|null` oder wird in allen Fixtures auf Objekt normalisiert. Nicht beides widersprüchlich.
- `logs.hud/psi/arena_psi` sind entweder strict erlaubt **oder** aus allen kanonischen Export-Fixtures entfernt und sauber verdichtet.
- `campaign.entry_choice_skipped`, `ui.intro_seen`, `ui.dice.debug_rolls` sind entweder strict erlaubt **oder** ausdrücklich runtime-only und nicht mehr in Export-/Template-Kontexten gefordert.

---

## 2. Masterprompt-Template: Arena/PvP ist noch nicht erstklassig genug

### Befund

`meta/masterprompt_v6.md` sagt bei `!save`, dass immer ein vollständiger v7-JSON-Block mit allen Pflichtfeldern ausgegeben wird. Das kopierbare Save-Template enthält aber keinen `arena`-Block. Später steht Arena nur als Zusatzregel „nur wenn genutzt“. Für PvP-only und Push/Cashout ist das zu weich.

Außerdem steht im Masterprompt noch sehr pauschal: „PvP-Arena speichert nicht.“ Das ist für aktive Queue/Run richtig, aber für deine gewünschte Bonusstaffelung gefährlich ungenau: Nach abgeschlossener Runde/Serie soll die Gruppe in der HQ-Arena-Lounge speichern können, damit ein neuer Chat mit `pending_rewards`/Cashout/Push starten kann.

### Patch

Masterprompt §I / Save-Template aktualisieren:

1. Entweder `arena` immer als kompakten Default-Block ins kanonische Save-Template aufnehmen, oder direkt unter dem Template einen **kopierpflichtigen Arena-Zusatzblock** definieren, der bei Arena-Nutzung niemals weggelassen werden darf.
2. Pauschalregel ersetzen durch:

```text
PvP/Arena: Kein Save während Queue, aktivem Match oder laufender Arena-Szene.
Nach abgeschlossener Runde/Serie kehrt die Gruppe in die HQ-Arena-Lounge zurück.
Dieser Zustand zählt als HQ-safe: arena.active=false, phase/queue_state=idle|completed.
Dort ist !save erlaubt und muss pending_rewards/banked_rewards/first_wins/contract_id/streak persistieren.
```

3. Merge-Output stärker als Spielerlebnis definieren:

```text
Bei Mehrfach-Load/Split-Rejoin erzeugt die KI-SL vor dem HQ-Router immer:
1) Konvergenz-Intro in 4–8 Sätzen, in-world, plausibel, keine Tabellen-Prosa.
2) Kompakter Kontinuitätsrückblick: was jede Teilgruppe mitbringt.
3) Merge-Tabelle mit Anker, persönlichen Wahrheiten, Echos, Konflikten.
4) Einen nächsten spielbaren Hook.
Danach erst HQ-Router.
```

### Akzeptanz

- PvP-only-Spieler verlieren bei `!save` nach Rundenabschluss keinen Pending-/Banked-Stand.
- `!save` während aktivem Match bleibt blockiert.
- Der neue Chat fühlt sich nach Arena-Load wie HQ-Lounge/Cashout/Push an, nicht wie Kampagnen-Neustart.
- Mehrfach-Load wirkt wie eine coole Konvergenzszene, nicht wie ein JSON-Importbericht.

---

## 3. `kampagnenstruktur.md`: Encounter-Pools tragen noch alte Paradoxon-Sprache

### Befund

Im Modul stehen die Encounter-Pools noch mit Spalte `Paradoxon` und Werten wie:

- `+1 bei Verzögerung`
- `+1 bei Psi-Einsatz`
- `-1 (Px) bei Live-Übertragung`
- Rift-Events mit `+2`
- Field-Downtime mit `Paradoxon 0`

Das widerspricht dem neuen Kernvertrag: Px ist positive Resonanz/Belohnung. Fehler erzeugen Druck, Heat, Timeline-Echos oder Ressourcenfolgen — keine negative Px-Buchhaltung.

### Patch

In `gameplay/kampagnenstruktur.md`:

- Spalte `Paradoxon` in Encounter-Pools umbenennen in `Druck/Echo` oder `Folge`.
- Alle `+1`, `+2`, `-1 (Px)` aus den Tabellen ersetzen durch konkrete Nicht-Px-Folgen:
  - `Heat +1`
  - `Noise +1`
  - `Timeline-Echo`
  - `Fraktionsnotiz`
  - `Stress +1`
  - `Exfil-Fenster kürzer`
  - `Px bleibt unverändert`
- Bei RIFT OPS klar halten:

```text
RIFT OPS: nur bei offenen campaign.rift_seeds[] nach ClusterCreate() und gültigem Gate/Episodenabschluss. Encounter-Folgen erhöhen nicht automatisch Px.
```

### Watchguard erweitern

`tools/test_px_language_watchguard.js` ist aktuell zu schmal. Es fängt ein paar konkrete Regexe, aber nicht die gefährliche Tabellenstruktur.

Erweitern auf mindestens:

```js
const forbidden = [
  /\|\s*Paradoxon\s*\|/i,
  /-1\s*\(Px\)/i,
  /\+\d+\s*bei\s+Psi-Einsatz/i,
  /\+\d+\s*bei\s+Verzögerung/i,
  /Paradoxon\s+0/i,
  /RIFT OPS.*Paradoxon/i
];
```

Nicht jede Nennung von „Paradoxon-Index“ verbieten; der Begriff ist als Name des positiven Px-Systems weiterhin okay. Verboten sind alte Straf-/Encounter-Tabellenmechaniken.

### Akzeptanz

- Encounter-Pools haben keine Spalte `Paradoxon` mehr.
- Keine Tabellenzelle enthält `-1 (Px)`.
- Fehlerfolgen laufen über Druck/Echo/Heat/Noise, nicht über Px-Abzüge.
- Px bleibt: gutes Core-Spiel → Resonanz → Px 5 → ClusterCreate() → Rift-Seeds.

---

## 4. Fixtures: `savegame_v7_*` sind teils Testfragmente, nicht strict-v7 Saves

### Befund

Mehrere `internal/qa/fixtures/savegame_v7_*.json` sind für Watchguards nützlich, aber kein vollständiger strict Export. Beispiele:

- `savegame_v7_arena_round_checkpoint.json` enthält nur minimalen Character (`id`, `name`, `lvl`, `xp`, `wallet`) und lässt viele strict-pflichtige Character-Felder weg.
- Es enthält `logs.hud`, `logs.psi`, `logs.arena_psi`, die strict aktuell nicht erlaubt.
- Es enthält Arena-Felder, die strict aktuell nicht kennt.
- `savegame_v7_split_3_2_merge.json` enthält minimalistische Character-Objekte nur mit `id`/`wallet`.
- Einige Fixtures lassen `ui.action_mode` aus, obwohl das Save-Template `action_mode: "uncut"` führt.

Das ist nicht zwingend schlimm, solange klar ist: **Testfragment ≠ kanonischer Save**. Gefährlich ist nur der Dateiname `savegame_v7_...`, weil Agenten und LLMs daraus „das ist ein voller Save“ lernen.

### Patch-Option A — bevorzugt

Fixtures trennen:

- Vollständige strict Export-Fixtures: `internal/qa/fixtures/export_v7_*.json`
- Watchguard-Fragmente: `internal/qa/fixtures/fragments/v7_*.json` oder `internal/qa/fixtures/watchguard_v7_*.json`

Dann Tests entsprechend anpassen.

### Patch-Option B

Alle `savegame_v7_*.json` vollständig strict-v7 machen. Das ist sauberer, aber größer und für schnelle Watchguards weniger bequem.

### Akzeptanz

- Kein Testfragment heißt mehr so, als wäre es ein kanonischer strict Save.
- Mindestens eine vollständige strict 5er-Gruppen-Fixture existiert.
- Mindestens eine vollständige strict Arena-HQ-Checkpoint-Fixture existiert.
- Mindestens eine vollständige strict Personal-Export-Fixture existiert.
- Watchguard-Fragmente dürfen minimal bleiben, sind aber klar als Fragmente benannt.

---

## 5. Tests: Smoke ist stark, aber prüft den strict Export noch nicht hart genug

### Befund

`scripts/smoke.sh` enthält inzwischen starke Watchguards: v7 Schema Consistency, Issue Pack, Smart-Merge 3/2, Arena-Runden-Checkpoint, Personal-Export, Px-Sprachdrift und Save-Budget.

Aber `tools/test_v7_schema_consistency.js` liest nur das tolerante Import-/Normalizer-Schema `saveGame.v7.schema.json`; das strict Export-Schema `saveGame.v7.export.schema.json` wird nicht gegen die neuen Arena-/Log-/UI-/Campaign-Felder abgesichert.

### Patch

Neuen Test ergänzen:

`tools/test_v7_strict_export_contract.js`

Ohne neue npm-Abhängigkeit. Einfach strukturelle Assertions auf Schema + Vollfixtures.

Mindestchecks:

```js
const exportSchema = readJson('systems/gameflow/saveGame.v7.export.schema.json');

// Schema-Feldchecks
assertHas(exportSchema, 'properties.arena.properties.first_wins');
assertFirstWinsIsObjectMap(exportSchema);
assertHas(exportSchema, 'properties.arena.properties.pending_rewards');
assertHas(exportSchema, 'properties.arena.properties.banked_rewards');
assertHas(exportSchema, 'properties.arena.properties.queue_state');
assertHas(exportSchema, 'properties.logs.properties.trace');
// Wenn logs.hud/psi/arena_psi kanonisch: assertHas(...)
// Wenn nicht: assertStrictExportFixturesDoNotContain(...)

// Fixture-Feldchecks
checkFullExportFixture('internal/qa/fixtures/export_v7_5er_hq_highlevel.json');
checkFullExportFixture('internal/qa/fixtures/export_v7_arena_checkpoint.json');
checkFullExportFixture('internal/qa/fixtures/export_v7_personal_export.json');
```

In `scripts/smoke.sh` verankern:

```bash
# v7 strict export contract
node tools/test_v7_strict_export_contract.js > out/v7_strict_export_contract.log
grep "v7-strict-export-contract-ok" out/v7_strict_export_contract.log
```

### Akzeptanz

- Smoke kann nicht mehr grün werden, wenn `first_wins` im strict Export wieder Integer ist.
- Smoke kann nicht mehr grün werden, wenn Arena-Checkpoint-Felder in Fixtures existieren, aber strict verboten sind.
- Smoke kann nicht mehr grün werden, wenn das Masterprompt-Template ein Feld fordert, das strict nicht kennt.

---

## 6. Logs-Feldmatrix einführen

### Befund

Im Repo existieren viele `logs.*`-Bezüge:

- `trace`
- `market`
- `artifact_log`
- `notes`
- `flags`
- `hud`
- `psi`
- `arena_psi`
- `foreshadow`
- `fr_interventions`
- `physicality`
- `alias_trace`
- `squad_radio`
- weitere Runtime-/Bridge-Logs

Einige sollen persistent sein, einige runtime-only, einige müssen vor Export verdichtet werden. Aktuell ist nicht überall eindeutig, was strict gespeichert wird.

### Patch

In `systems/gameflow/speicher-fortsetzung.md` einen kurzen Abschnitt ergänzen:

```text
### Logs-Feldmatrix v7

Strict exportiert:
- logs.trace[] — beweisrelevante Ereignisse, max 64
- logs.market[] — Käufe/Chronopolis/Services, max 24
- logs.artifact_log[] — Artefakte/Relikte, max 32
- logs.notes[] — verdichtete Freitextnotizen, max 24
- logs.hud[] — nur budget-/statusrelevante HUD-Proofs, max N
- logs.psi[] — nur Kosten-/Freigabenachweise, max N
- logs.arena_psi[] — nur Arena-Psi-Kosten, max N
- logs.flags{} — Import-/Merge-/Runtime-Flags

Runtime-only oder vor Export verdichten:
- logs.alias_trace[] → notes/trace Summary
- logs.squad_radio[] → notes Summary
- logs.fr_interventions[] → arc.hooks/notes Summary
- logs.physicality[] → trace nur bei relevanter Konsequenz
- logs.foreshadow[] → arc.hooks/trace oder strict aufnehmen, wenn Boss-Gate es wirklich braucht
```

Die Matrix muss mit Schema und Fixtures übereinstimmen.

### Akzeptanz

- Jeder `logs.X`-Key im Runtime-Wissen hat einen Status: strict exportiert, runtime-only, oder vor Export verdichtet.
- Keine strict-verbogenen Felder in kanonischen Export-Fixtures.
- Save-Budget-Watchguard kennt die exportierten Arrays und deren Caps.

---

## 7. Episode-Start/Ende sauber entscheiden

### Befund

`kampagnenstruktur.md` sagt, `episode_seed_make()` speichert Start- und Endpunkt in `campaign.episode_start` und `campaign.episode_end`. `episode_plan` bleibt intern, aber Start/Ende werden als persistent beschrieben. Das strict Export-Schema erlaubt diese Felder aktuell nicht.

### Patch

Entscheidung treffen:

**Empfohlen:** `campaign.episode_start` und `campaign.episode_end` als kleine Strings/Objekte erlauben, `episode_plan` nicht exportieren.

Beispiel:

```json
"episode_start": { "epoch": "Berlin 1943", "hook": "Abwehrstab Tempus" },
"episode_end": { "epoch": "1986", "hook": "MORGENROT" }
```

Noch schlanker möglich:

```json
"episode_start": "Berlin 1943 · Abwehrstab Tempus",
"episode_end": "1986 · MORGENROT"
```

Wenn ihr maximal schlank bleiben wollt: Text ändern auf „persistiert werden nur `arc.hooks[]` und `summaries.*`; `campaign.episode_start/end` sind runtime-only“. Dann aber alle Vorkommen entsprechend glätten.

### Akzeptanz

- Kein `episode_plan` im strict Save.
- Start/Ende entweder strict erlaubt oder nicht mehr als persistente Campaign-Felder beschrieben.

---

## 8. Smart-Merge-Spielgefühl finalisieren

### Befund

Die technische Merge-Logik ist stark. Was noch expliziter werden sollte: Der Merge ist nicht nur Konsolidierung, sondern ein kleines Highlight. Es soll Spaß machen, Saves zusammenzuwerfen.

### Patch

In Masterprompt und `speicher-fortsetzung.md` ergänzen:

```text
Smart-Merge-Ausgabe bei Mehrfach-Load:
- Kein trockenes „Import abgeschlossen“ als alleinige Antwort.
- Immer zuerst eine kurze Konvergenzszene: wie sich die Fäden im HQ, Kodex-Archiv, Briefingglas oder Arena-Lounge wieder treffen.
- Dann kompakter Rückblick je Branch: max 1 Satz pro Branch.
- Dann Merge-Tabelle: Anker / persönliche Wahrheit / übernommene Echos / Konflikte.
- Dann ein spielbarer nächster Hook.
- Danach HQ-Router.
```

Für 5er 3/2:

```text
Berlin 43 → Team A 1939 (3 Spieler), Team B 1986 (2 Spieler) → Rejoin HQ.
Der Rejoin darf Sinnbrüche nicht verstecken. Er macht sie als Kodex-Anomalien/Echos spielbar.
```

### Akzeptanz

- Der Mehrfach-Load-Test prüft nicht nur Felder, sondern auch Output-Vertrag: Konvergenz-Intro + Merge-Tabelle + nächster Hook.
- `continuity.shared_echoes[]`, `roster_echoes[]`, `convergence_tags[]` bleiben capped.
- Personal-Export nimmt nur den eigenen Character plus wenige Echos mit.

---

## 9. Minimaler Commit-Plan

### Commit 1 — falls ihr einzeln arbeitet

`fix(save): align strict v7 export with arena and merge contract`

Inhalt:

- strict Export-Schema aktualisiert
- Masterprompt-Template/Arena-Save phrasing angepasst
- Speicher-Doku Logs/Arena/Episode geklärt
- Fixtures sortiert oder vervollständigt
- strict export test ergänzt
- smoke erweitert

### Commit 2 — falls separat gewünscht

`fix(px): remove legacy paradox accounting from encounter pools`

Inhalt:

- Encounter-Spalte `Paradoxon` → `Druck/Echo`/`Folge`
- alte Px-Plus/Minus-Tabellenfolgen ersetzt
- Px-Language-Watchguard erweitert

Ein Commit ist auch okay, wenn Flo Squash-Merge nutzt. Commit-Body bitte nach `AGENTS.md`-Struktur.

---

## 10. Akzeptanztests nach Patch

Pflicht:

```bash
bash scripts/smoke.sh
```

Zusätzlich manuell/statisch prüfen:

```bash
grep -R "|.*Paradoxon.*|" gameplay/kampagnenstruktur.md
grep -R "-1 (Px)" gameplay/kampagnenstruktur.md
grep -R "first_wins.*integer" systems/gameflow/saveGame.v7.export.schema.json
grep -R "pending_rewards" systems/gameflow/saveGame.v7.export.schema.json meta/masterprompt_v6.md systems/gameflow/speicher-fortsetzung.md internal/qa/fixtures
```

Erwartung:

- Kein `first_wins` als Integer.
- Keine Encounter-Spalte `Paradoxon`.
- Keine `-1 (Px)`-Tabelle.
- `pending_rewards` ist in Arena-Schema/Template/Doku/Fixture konsistent.
- Smoke enthält `v7-strict-export-contract-ok`.

---

## 11. Jubelgate-Kriterien

Nach diesem Pass darf ein Jubeltest raus, wenn alle Punkte grün sind:

1. `!save` im HQ erzeugt einen strict-v7 kompatiblen Save.
2. Der Save bleibt kompakt und capped.
3. 5er-Gruppe kann nach Berlin 43 in 3/2 splitten, separat spielen und im HQ rejoinen.
4. Mehrfach-Load erzeugt Konvergenz-Intro + Merge-Tabelle + nächsten Hook.
5. Personal-Export enthält genau den eigenen Character plus wenige Echos.
6. Arena kann nach jeder abgeschlossenen Runde/Serie im HQ-safe Zustand speichern.
7. Pending/Banked/Push/Cashout überstehen neuen Chat.
8. Px bleibt positives Resonanzsystem; Fehler erzeugen Druck/Echo, keine Straf-Px.
9. Chronopolis bleibt No-Save-Zone und Rückkehr → HQ-savebar.
10. Smoke kann die oben genannten Drifts nicht mehr durchwinken.

---

## Goldener Satz für diesen Patch

> Der Save ist kein Protokoll dessen, was gesagt wurde. Er ist der Charakterbogen der Welt: knapp genug zum Mitnehmen, stark genug, damit die KI-SL daraus wieder Magie baut.
