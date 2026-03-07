# ZEITRISS v7 Save/Load Audit – Issue Pack für Codex/Agenten

## Kurzfazit

Der aktuelle Stand ist **für den normalen HQ→Mission→HQ-Loop deutlich stärker als zuvor**, aber **noch nicht voll wasserdicht** für alle Gruppenszenarien. Die Hauptursache ist kein Ideenproblem, sondern ein **SSOT-Bruch zwischen Text-v7 und Test-/Schema-v6** sowie fehlende Regeln für **parallele Kernmissions-Branches** und **gemischte Split-Pfade**.

---

## Issue 1 — Save-v7-SSOT wirklich vereinheitlichen

**Titel:** `Save v7 als einziges kanonisches Modell erzwingen (Docs, Masterprompt, Schema, Tests synchronisieren)`

**Problem**

Der Repo-Stand behauptet Save v7 als SSOT, aber in den aktiven Quellen stehen weiterhin konkurrierende Wahrheiten nebeneinander:

- `zr` vs. `zr_version`
- `campaign.mission` vs. `campaign.mission_in_episode`
- `attr{}` vs. `attributes{}`
- `characters[]` vs. `character` + `party.characters[]` + `team.members[]`
- `arc{factions,questions,hooks}` vs. `arc{open_seeds,open_questions,timeline}` vs. `arc_dashboard{...}`
- „keine Laufzeitdaten im Save“ vs. Beispiele mit `location`, `phase`, `scene`, `cooldowns`, `SYS_runtime`, `SYS_used`

Das erzeugt Halluzinationsrisiko bei KI-SL und verhindert saubere Automatisierung.

**Aufgabe**

1. Definiere **ein einziges kanonisches Exportmodell** für neue Saves.
2. Halte dieses Modell identisch in:
   - `meta/masterprompt_v6.md`
   - `systems/gameflow/speicher-fortsetzung.md`
   - `core/sl-referenz.md`
   - Schema-Datei
   - Test-Fixtures
3. Markiere alles Alte konsequent als `legacy import only`.
4. Entferne widersprüchliche Beispiel-JSONs oder migriere sie vollständig.

**MUSS-Entscheidungen explizit treffen**

- Header: `v` + `zr` **oder** `v` + `zr_version`
- Roster: nur `characters[]`
- Ressourcen: nur `economy.hq_pool` + `characters[].wallet`
- Arc: genau **eine** Struktur
- Runtime-Felder: entweder **explizit nie speichern** oder **als HQ-konstante Felder bewusst erlauben**, aber nicht beides gleichzeitig

**Acceptance Criteria**

- Es gibt genau **ein** v7-Exportbeispiel.
- Kein Modul beschreibt einen anderen Pflichtbaum.
- Loader migriert Altformate nach v7, exportiert aber nur noch v7.
- Alle v7-Dokumente nennen dieselben Feldnamen.

---

## Issue 2 — OpenWebUI-Realität vs. Runtime-Komfort sauber trennen

**Titel:** `OpenWebUI-native Save/Load von runtime-only Komfortfunktionen trennen`

**Problem**

Die Doku mischt Chat-native Nutzung mit Runtime-Pseudocode. In produktiver KI-SL ohne lokale JS-Hooks sind Funktionen wie temporäre Snapshot-Dateien nicht wirklich vorhanden.

**Aufgabe**

1. Trenne in der Doku strikt:
   - **Chat-native / OpenWebUI sicher:** `!save` → JSON exportieren, `Spiel laden` + JSON einfügen
   - **runtime-only / optional:** `!load` letzter Save, `!autosave hq`, `!suspend`, `!resume`
2. Kennzeichne alle runtime-only Befehle mit einer klaren Notiz: 
   - „Nur mit Host-Runtime / nicht garantiert im reinen Wissensspeicher-Betrieb“
3. Entferne jeden Anschein, dass reines OpenWebUI temporäre Dateien zuverlässig hält.

**Acceptance Criteria**

- README, Spielerpfad und Save-Doku unterscheiden klar zwischen „geht im reinen Chat“ und „geht nur mit Runtime“.
- `!suspend`/`!resume` werden nicht mehr als allgemein sichere Standardlösung für OpenWebUI verkauft.

---

## Issue 3 — Parallel-Branch-Protokoll definieren oder bewusst verbieten

**Titel:** `Parallele Kernmissions-Branches definieren (oder explizit als nicht-kanonisch sperren)`

**Problem**

Aktuell ist Split/Merge sauber nur für **post-episode Rift-Ops** beschrieben. Nicht sauber geregelt ist:

- Gruppe splittet **nach Mission 3**
- beide Teilgruppen spielen **verschiedene Mission-4-Stränge parallel**
- danach Merge

Ohne Branch-Protokoll überschreibt der Host-Kampagnenblock den Gast-Block und eine Hälfte der Kampagnenprogression verliert ihren kanonischen Status.

**Aufgabe**

Entscheide dich zwischen zwei harten Modellen:

### Option A — bewusst verbieten

- Erlaube Split/Merge **nur** nach Episodenende für Rift-Ops.
- Definiere parallele Core-Branches als Hausregel / nicht-kanonisch.

### Option B — voll unterstützen

Führe ein:

- `campaign.branch_id`
- `campaign.branch_parent_save_id`
- `campaign.branch_kind = core|rift|pvp|chronopolis`
- `campaign.branch_scope = canonical|side-run`
- `campaign.progress_token`
- Merge-Regeln für `episode`, `mission`, Objectives, branch resolutions, discoveries, seeds, rewards, XP und Ruf

**Acceptance Criteria**

- Entweder ist Mission-3→Mission-4-Split glasklar verboten,
- oder es gibt eine deterministische Merge-Regel ohne Host-Override-Verlust.

---

## Issue 4 — Gemischte Split-Pfade formalisieren

**Titel:** `Mixed Split/Merge: Rift + PvP + Chronopolis + Abort sauber spezifizieren`

**Problem**

Aktuell gibt es Teilregeln für Arena, Chronopolis, Abort und Rift. Es fehlt aber eine gemeinsame Aussage für Mischfälle wie:

- Teilgruppe A spielt Rift
- Teilgruppe B spielt PvP
- Teilgruppe C war in Chronopolis
- Teilgruppe D hat einen Einsatz abgebrochen
- später Merge in HQ

So ein Fall ist im Design offensichtlich gewollt, aber nicht vollständig formalisiert.

**Aufgabe**

Definiere pro Branch-Typ:

- ob er während eines Splits **erlaubt** ist
- welche Felder er verändern darf
- welche Belohnungen sofort kanonisch sind
- welche Felder beim Merge Host-priorisiert bleiben
- wie `campaign.px`, `campaign.mode`, `arena`, `chronopolis`-Flags, Seeds, HQ-Pool, Wallets und Logs konsolidiert werden

**Zusatzregel nötig**

Definiere einen **Merge-Precedence-Graph**:

1. globale Kampagne
2. branch-lokale Progression
3. Charakterdaten
4. Arena/Resume-Zustand
5. Chronopolis-Markt/City-Logs
6. Debrief-Outputs

**Acceptance Criteria**

Es gibt mindestens dokumentierte Beispiele für:

- Rift + PvP → Merge
- Abort + HQ-Rückkehr → Save → später Merge
- Chronopolis-Run + HQ-Branch → Merge

---

## Issue 5 — Arena-Savegrenze `completed` vs. `idle` bereinigen

**Titel:** `Arena queue_state: completed vs idle als einheitliche Save-Regel festziehen`

**Problem**

Aktuell widersprechen sich Doku und Testlogik:

- an einer Stelle wirkt `completed` wie zulässiger Save-Zustand
- an anderer Stelle blockiert alles außer `idle`

Für Spieler ist gerade der Moment **nach PvP** aber ein kritischer Savepunkt.

**Aufgabe**

1. Lege verbindlich fest:
   - Save erlaubt bei `queue_state = idle` **nur**
   - **oder** Save erlaubt bei `idle|completed`
2. Synchronisiere:
   - Save-Doku
   - SL-Referenz
   - Runtime-Tests
   - Fehlermeldungen
3. Falls `completed` erlaubt bleibt, definiere sauber:
   - welche Arena-Felder noch persistiert werden dürfen
   - wann `resume_token` geschrieben werden darf
   - wann `previous_mode` zurückgesetzt wird

**Acceptance Criteria**

- Nur eine Wahrheit bleibt übrig.
- PvP-Ausstieg ist für Spieler klar verständlich.

---

## Issue 6 — Save-Größe für 5er-Highend-Gruppen begrenzen

**Titel:** `Save-Größenbudget für 5 Agenten auf Lvl 900+ definieren und enforce’n`

**Problem**

v7 speichert sehr sinnvoll pro Charakter `history`, `carry`, `quarters_stash`, `vehicles`, Wallets usw. Gleichzeitig wachsen globale Logs und Arc-Strukturen über lange Kampagnen stark an. Für reines OpenWebUI ist nicht der Code das Problem, sondern JSON-Bloat und Promptdruck.

**Aufgabe**

1. Definiere harte oder weiche Caps / Rolling Windows für mindestens:
   - `logs.trace[]`
   - `logs.notes[]`
   - `logs.artifact_log[]`
   - `logs.market[]`
   - `arc.questions[]`
   - `arc.hooks[]`
   - `history.milestones[]`
2. Führe ein kompaktes Langzeitformat ein:
   - `summary_last_episode`
   - `summary_last_rift`
   - `summary_active_arcs`
3. Schreibe eine Prune-Regel für HQ-Saves:
   - „letzte X Details, ältere Inhalte als Summary block“

**Acceptance Criteria**

- Ein 5er-Team auf Lvl 900+ bleibt in einem robust ladbaren JSON-Korridor.
- Der Save verliert keine spielkritischen Daten, aber Redundanz wird abgebaut.

---

## Issue 7 — Charakter-Dedupe und Merge-Lineage einbauen

**Titel:** `Doppelte Charaktere und doppelt importierte Branch-Saves verhindern`

**Problem**

Im Split/Merge-Text werden Charaktere zusammengeführt, aber es fehlt eine harte Dedupe-Regel für doppelte Agenten-IDs oder doppelt gepostete Saves. Das ist in manuellen Merge-Flows brandgefährlich.

**Aufgabe**

1. Ergänze Save-Metadaten:
   - `save_id`
   - `parent_save_id`
   - `merge_id`
   - `branch_id`
2. Definiere:
   - duplicate character ids => blockieren oder interaktiv auflösen
   - duplicate save lineage => Import verweigern / Warnung ausgeben
3. Füge eine sichtbare Merge-Tabelle hinzu:
   - `imported_saves`
   - `duplicate_branch_detected`
   - `duplicate_character_detected`

**Acceptance Criteria**

- Gleiches Branch-Save zweimal einfügen erzeugt keinen stillen Doppelkauf / Doppelcharakter.
- Ein Agent kann nach Merge nicht doppelt im Team landen.

---

## Issue 8 — Px-Regel für Split/Merge in gemischten Pfaden klären

**Titel:** `Paradoxon-Index bei Split/Merge/Arena/Abort eindeutig machen`

**Problem**

Aktuell gilt gleichzeitig:

- `campaign.px` ist global führend
- beim Team-Split wird Px in beide Saves kopiert
- beim Merge gewinnt der Maximalwert
- Arena verändert Px nicht
- Rifts resetten Px nach der Rift-Phase

In Mischfällen kann dadurch ein alter Px-Stand wieder auftauchen oder branch-spezifisch konserviert werden.

**Aufgabe**

Definiere einen harten Zustand für Px:

- `clean`
- `pending_reset`
- `consumed`

oder

- `px_state = stable|pending_cluster|pending_reset|reset_done`

Lege fest, wie sich Px verhält bei:

- Split nach offenem Cluster
- Branch A Rift abgeschlossen, Branch B PvP
- Abort ohne Rift
- Merge vor/nach Debrief

**Acceptance Criteria**

- Es gibt keinen Fall, in dem ein verbrauchter Px 5 durch Max-Merge wieder „aufersteht“.

---

## Issue 9 — High-Level-Ökonomie-Bänder vereinheitlichen

**Titel:** `Economy-Audit-Bänder 120/512/900+ vs 100/400/1000 bereinigen`

**Problem**

Für das Highend-Spiel existieren widersprüchliche Bänder in verschiedenen Texten. Gerade bei deinem Lvl-900-Szenario darf die Audit-Referenz nicht wackeln.

**Aufgabe**

1. Lege genau **eine** Level-Band-Tabelle fest.
2. Synchronisiere:
   - Save-Doku
   - SL-Referenz
   - Währungssystem
   - Economy-Audit-Tests
3. Dokumentiere klar, warum genau diese Bänder gelten.

**Acceptance Criteria**

- Alle High-Level-Quellen nennen identische Bands und Richtwerte.

---

## Issue 10 — Vollständige v7-Teststrecke für 5er-Gruppen bauen

**Titel:** `V7-End-to-End-Fixtures für 5er-Team, Split/Merge und High-Level-Saves ergänzen`

**Problem**

Die vorhandene Testlandschaft beweist noch stark Legacy-/v6-Pfade. Für das, was ZEITRISS designseitig jetzt können will, fehlen Golden Paths.

**Aufgabe**

Baue mindestens diese Fixtures und Tests:

1. **5er HQ-save v7** auf Lvl 900+
2. **Episode-Ende → Split 3/2 → zwei Rift-Ops → Merge**
3. **PvP-Branch + Rift-Branch → Merge**
4. **Chronopolis-Eintritt → Rückkehr → HQ-Save**
5. **Abort → HQ-Rückkehr → Save → später Fortsetzung**
6. **Load in reinem OpenWebUI-Promptpfad** (kein Runtime-Zauber vorausgesetzt)

**Wichtig**

Wenn parallele Core-Branches nicht unterstützt werden sollen, schreibe dafür einen **Refusal-Test**:

- sauberer Hinweistext
- keine halbgare Host-Überschreibung

**Acceptance Criteria**

- Die kritischen Gruppenpfade sind testbar.
- V7 ist nicht nur „beschrieben“, sondern durch Fixtures abgesichert.

---

## Direkt übernehmbarer Betriebsstandard für OpenWebUI

```md
## ZEITRISS Save/Load-Betriebsstandard (OpenWebUI)

**Grundsatz:** Der einzige harte Save ist der HQ-DeepSave. Alles andere ist Laufzeit oder Hausregel.

### Speichern

Gespeichert wird nur:
- direkt nach der Charaktererschaffung im HQ
- nach jedem Debrief
- nach längeren HQ-Umbauten / Shop / Klinik / Werkstatt
- direkt vor Briefing/Absprung, falls die Runde dort endet
- verpflichtend vor Chronopolis-Schleuseneintritt
- direkt nach Rückkehr aus Chronopolis ins HQ
- nach Arena erst dann, wenn der Arena-Status vollständig auf HQ/idle normalisiert ist

### Nicht speichern

Kein DeepSave in:
- Core-Ops
- Rift-Ops
- Chronopolis
- aktiver Arena / Matchmaking
- aktiver Exfil
- Offline-Ende ohne Re-Sync

### Neuer Chat

Für maximale Stabilität gilt:
- **ein neuer Chat pro HQ→Mission→HQ-Zyklus**
- zusätzlich neuer Chat nach jedem HQ-DeepSave, wenn ihr einen harten Abschnittswechsel macht
- niemals mitten im Feld auf einen neuen Chat hoffen, außer ihr nutzt bewusst einen separaten Runtime-Suspend

### Split/Merge

Kanonisch unterstützt ist aktuell:
- Split **nach Episodenende** für getrennte Rift-Ops
- Merge **im HQ** nach Abschluss aller Teil-Rifts

Nicht automatisch als kanonisch behandelt werden:
- parallele Core-Missions-Branches innerhalb derselben Episode
- Misch-Splits ohne explizite Merge-Regeln (z. B. ein Team Rift, ein Team PvP, ein Team Chronopolis)
```

---

## Direkt übernehmbarer Warning-Text für die Doku

```md
> **Wichtig für OpenWebUI / reinen Chatbetrieb:** ZEITRISS speichert zuverlässig über den HQ-DeepSave als JSON-Block. Komfortfunktionen wie `!suspend`, `!resume`, `!load` des letzten lokalen Spielstands oder temporäre Snapshot-Dateien setzen eine Host-Runtime voraus und sind im reinen Wissensspeicher-Betrieb nicht garantiert verfügbar.
```

---

## Direkt übernehmbarer Canon-Text für Split/Merge

```md
### Kanonischer Split-Standard

ZEITRISS unterstützt Split/Merge standardmäßig **nach Episodenende** für getrennte Rift-Ops. Dieser Pfad ist kanonisch, transparent und merge-fest.

### Nicht-kanonische Branches

Parallele Core-Ops innerhalb derselben Episode, gemischte Split-Pfade aus Rift/PvP/Chronopolis oder branchende Missionsketten gelten erst dann als kanonisch unterstützt, wenn ein explizites Branch-Protokoll aktiv ist. Ohne dieses Protokoll bleibt der Host-Kampagnenblock führend; Gast-Branches liefern nur Charakter-, Wallet- und Loadout-Daten.
```
