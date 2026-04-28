# ZEITRISS 4.2.6 — Nachcheck-Agentenpaket: Gameflow, Savepoints, Weltillusion

**Datum:** 2026-04-28  
**Zielbranch:** `fix/v426-postpatch-gameflow-savepoints`  
**Zielmodell:** Sonnet 4.6 via OpenWebUI/LiteLLM  
**Review-Art:** statischer Repo-/Raw-Review + gedankliche Playtest-Simulation  
**Wichtig:** Lokales Klonen/CI war in der Review-Umgebung nicht möglich (`github.com` konnte per DNS nicht aufgelöst werden). Dieses Paket ist deshalb ein präziser SSOT-/Gameflow-Nachcheck, aber kein ausgeführter Testlauf.

---

## 0. Executive Verdict

Der Kern ist jetzt sehr stark. Der gewünschte Design-Trick — **HQ als Ruhehafen, `!save` als Abschnittsgrenze, neuer Chat als bewusstes Frischladen, JSON als scheinbar serverseitige Weltkontinuität** — ist im Masterprompt inzwischen klar angelegt.

Der aktuelle Ziel-Loop ist logisch:

```text
Klassischer Start
→ Charaktererschaffung
→ HQ-Heimkehrbeat
→ Chargen-Save-Gate
→ !save
→ neuer Chat + JSON laden
→ freier HQ-Router
→ Abschnitt wählen: CoreOp | RiftOp | Chronopolis | PvP/Arena | HQ-Runde
→ Abschnitt spielen
→ Debrief / HQ-Rückkehr / Sonder-Debrief
→ !save
→ neuer Chat + JSON laden
→ Welt fühlt sich fortlaufend an
```

**Die CoreOps können weitgehend ruhen.** Der nächste große Wert entsteht jetzt durch RiftOps-, Chronopolis-, PvP- und Cross-Mode-Playtests. Genau dort wird sich zeigen, ob die MMO-Illusion über Chatgrenzen wirklich trägt.

Noch nicht perfekt ist der Stand, weil einige Nebenmodule und Schema-Referenzen alte oder widersprüchliche Signale senden. Ein LLM liest nicht nur den Masterprompt, sondern zieht bei Unsicherheit Kurzmodule, Tabellen, Beispiele und Smokes heran. Die gefährlichen Reste sind daher keine „großen Designfehler“, sondern **Prompt-Poisoning durch Restdrift**.

---

## 1. Zielbild: Der perfekte Savepoint-Vertrag

### 1.1 Weltlogik

- **ITI** ist die Gesamtanlage in der Nullzeit.
- **HQ-Kern / sichere ITI-Decks / Pre-City-Hub** sind savebar.
- **Chronopolis/CITY** ist gefährlicher Ringraum, kein Hub, kein Savepoint.
- **CoreOps/RiftOps** sind Einsatzabschnitte, kein Savepoint.
- **PvP/Arena** ist kein Savepoint während Queue/Match/Run; nach sauberem Exit/Completed/Idle darf wieder im HQ gespeichert werden.
- **`!save` ist immer explizit.** Kein Autosave, kein versteckter Debrief-Snapshot.
- **Neuer Chat pro Abschnitt** ist der empfohlene Stabilitätspfad, aber nicht als harte Spielerpflicht formuliert.

### 1.2 Abschnittsgrenzen

```text
[Chargen-Abschnitt]       klassisch: savebar am Ende; fast-lane: nicht savebar vor Mission 1
[HQ-Runde]                savebar am Anfang/Ende/langer Pause, wenn stabil
[CoreOp]                  nicht savebar; Debrief → HQ → savebar
[RiftOp]                  nicht savebar; Rift-Debrief → HQ → savebar
[Chronopolis]             vor Schleuse savebar, in CITY nicht, nach Exit wieder savebar
[PvP/Arena]               vor Start savebar, Queue/Match nicht, nach Exit/Completed wieder savebar
[Gruppen-Merge]           erster Save = Session-Anker; weitere Saves = persönliche Wahrheit + Echoes
```

### 1.3 Spielgefühl

Für Spieler soll das wie ein Server wirken, obwohl kein Server existiert:

- Der Save enthält nicht „alles“, sondern genau die **kanonischen Weltanker**.
- Runtime-Zustände werden beim Laden normalisiert, nicht persistiert.
- Das HQ ist der Ort, an dem die Welt scheinbar weiteratmet: Bulletin, NPC-Offscreen-Fortschreibung, Wallet/HQ-Pool, Roster-Echoes, Arc-Hooks.
- Abschnittswechsel sind bewusst wie MMO-Instanzen: **HQ → Instanz → HQ**.

---

## 2. Die wichtigsten Restdrifts vor dem nächsten Playtest

### P0-01 — `phase: core` bei HQ-Saves rauswerfen

**Datei:** `systems/gameflow/speicher-fortsetzung.md`  
**Beobachtung:** Dort steht noch: `Phase-Feld: HQ-Saves bleiben phase: core.`  
**Warum gefährlich:** Das untergräbt die neue Savepoint-Logik. Ein HQ-Save darf nicht „core“ sein, nur weil CoreOps der Standardpfad sind. Sonst kann ein Load-Router glauben, er müsse einen Core-Kontext fortsetzen oder einen Modus falsch wiederherstellen.

**Patch:**

```text
ALT:
Phase-Feld: HQ-Saves bleiben `phase: core`.

NEU:
HQ-Deepsaves persistieren keinen laufenden Runtime-`phase`-Wert.
Kanonischer Load-Anker ist `continuity.last_seen`.
Für stabile HQ-Saves gilt:
  continuity.last_seen.mode = "hq"
  continuity.last_seen.location = "HQ"
Missionstypen (`core`, `rift`, `arena`, `chronopolis`) dürfen in `logs.trace[]`,
`summaries.*` oder transientem Runtime-State auftauchen, aber nicht als aktiver HQ-Save-Modus.
```

**Akzeptanztest:** Nach Rift-Debrief speichern → JSON zeigt `continuity.last_seen.mode: "hq"`, `location: "HQ"`; `summary_last_rift` enthält Rift-Recap; kein Root-`phase: core` als Save-Entscheider.

---

### P0-02 — `campaign.mode` darf nicht `rift` sein

**Datei:** `core/sl-referenz.md`  
**Beobachtung:** Das persistente Save-Schema beschreibt `campaign.mode:"mixed"|"preserve"|"trigger"|"rift"`.

**Warum gefährlich:** `campaign.mode` ist der **Kampagnen-/Seed-Pool-Modus**. `rift` ist ein **Missionstyp/Abschnitt**, kein Fraktions- oder Kampagnenmodus. Wird `rift` dort persistiert, kann ein Spieler nach dem Rift im neuen Chat dauerhaft im falschen Modus hängen.

**Patch:**

```text
campaign.mode: "mixed" | "preserve" | "trigger"
mission_type / runtime_op_type: "core" | "rift" | "arena" | "chronopolis"  // runtime/trace only
continuity.last_seen.mode: "hq" | "core" | "rift" | "arena" | "chronopolis" | "debrief"
```

**Akzeptanztest:** Arena/Rift/Chronopolis verlassen → HQ-Save behält `campaign.mode` des Kampagnenpools (`mixed|preserve|trigger`), nicht den zuletzt gespielten Abschnitt.

---

### P0-03 — Klassischer Start muss überall Chargen-Save-Gate haben

**Dateien:**

- `systems/gameflow/cinematic-start.md`
- `core/spieler-handbuch.md`
- ggf. `doc.md` / Fixture-Spiegel

**Beobachtung:** Der Masterprompt ist inzwischen richtig: klassisch → HQ-Heimkehrbeat → Save-Angebot → kein Auto-Briefing. In `cinematic-start.md` steht aber noch sinngemäß: nach Charaktererschaffung HQ-Rundgang **oder direkt Briefing**. Im Spielerhandbuch gibt es oben ebenfalls noch eine Kurzform, die vor dem Mini-Einsatzhandbuch in diese Richtung zieht.

**Warum gefährlich:** Der allererste Start ist der Moment, an dem Spieler das Speichersystem lernen. Wenn das Modell dort direkt ins Briefing springt, wird der erste DeepSave übersprungen und die „Welt über Chats hinweg“-Illusion startet bereits beschädigt.

**Patch:**

```text
Klassisch:
Charaktererschaffung → Pflicht-Heimkehrbeat → Chargen-Save-Gate → HQ-Menü.
Briefing erst nach expliziter Spielerentscheidung und nach Save-Angebot/aktivem Verzicht.

Fast-Lane:
Rolle/Defaults → direkt Briefing/SC 1.
Kein Chargen-Save-Gate; Save-Angebot erst nach Mission 1.
```

**Akzeptanztest:** `Spiel starten (solo klassisch)` mit generiertem Charakter endet nicht im Briefing, sondern im HQ mit `Kodex: HQ-Zustand stabil. Deepsave möglich.`

---

### P0-04 — v7-Schema: Import tolerant, Export strikt trennen

**Datei:** `systems/gameflow/saveGame.v7.schema.json`  
**Beobachtung:** Titel sagt „kanonischer Export“, aber das Schema ist tolerant (`additionalProperties:true`) und verlangt im Charakterblock nur `id` und `wallet`.

**Warum gefährlich:** Für Loader/Migration ist Toleranz gut. Für einen kanonischen `!save`-Export ist sie gefährlich, weil Tests grün werden können, obwohl Felder fehlen, die der Masterprompt als Pflicht führt.

**Patch-Option A, bevorzugt:** Zwei Schemas.

```text
saveGame.v7.import.schema.json   // tolerant, Legacy-/Normalizer-Hilfe
saveGame.v7.export.schema.json   // strikt, additionalProperties kontrolliert, Pflichtfelder vollständig
```

**Patch-Option B:** Bestehendes Schema umbenennen zu Import-/Normalizer-Schema und im Masterprompt/Speichermodul ausdrücklich sagen: Exportvertrag = Template/kompaktes Pflichtfeldset.

**Mindestanforderung für strict export:**

- Root: `v,zr,save_id,parent_save_id,merge_id,branch_id,campaign,characters,economy,logs,summaries,continuity,arc,ui`
- `campaign`: `episode,mission,px,px_state,mode,rift_seeds`
- `characters[]`: `id,name,callsign,rank,lvl,xp,origin,attr,lp,lp_max,stress,has_psi,sys_installed,talents,equipment,implants,history,carry,quarters_stash,vehicles,reputation,wallet,level_history`
- `continuity.last_seen`: `mode,episode,mission,location`
- `logs.flags`: mindestens `runtime_version,chronopolis_unlocked,imported_saves,duplicate_branch_detected,duplicate_character_detected,continuity_conflicts` oder bewusstes neues Konfliktfeld, siehe P1-03

---

### P0-05 — `Level 5` → `Px 5` in Rift-Dev-Checkliste

**Datei:** `gameplay/kampagnenstruktur.md`  
**Beobachtung:** In einem Diagramm/Dev-Checklist-Block steht noch `Level 5` als Trigger für Rift-Seeds.

**Warum gefährlich:** Der kanonische Trigger ist **Paradoxon-Index Px 5**, nicht Charakterlevel 5. Dieser Fehler ist klein, aber sehr giftig, weil RiftOps der nächste Testfokus sind.

**Patch:** Alle seed-erzeugenden Stellen auf `Px 5` / `Paradoxon-Index 5` ändern. Falls ein Mermaid-Pfeil kurz bleiben muss:

```text
B -->|Px 5| D[Rift-Pool]
```

**Akzeptanztest:** Level 5 ohne Px 5 erzeugt keine Seeds. Px 5 auf beliebigem Level erzeugt `ClusterCreate()`.

---

## 3. P1 — vor RiftOps/Chronopolis/PvP-Playtests sauberziehen

### P1-01 — Arena-Persistenzblock vervollständigen

**Dateien:**

- `core/sl-referenz.md`
- `gameplay/kampagnenstruktur.md`
- `systems/gameflow/saveGame.v7.schema.json`
- `meta/masterprompt_v6.md` falls Exporttemplate erweitert werden soll

**Beobachtung:** Arena-Regeln speichern/verwenden deutlich mehr als `{wins, losses, tier}`: `queue_state`, `zone`, `match_policy`, `phase_strike_tax`, `previous_mode`, `resume_token`, `defeated_types[]`, `first_wins{}`, ggf. `matches_this_episode`.

**Patch-Entscheidung:**

- Persistente Arena-Felder explizit definieren.
- Transiente Arena-Felder beim HQ-Save normalisieren.
- `previous_mode`-Fallback von `preserve` auf `mixed` ändern, weil `mixed` Startstandard ist.

**Vorschlag Arena-Schema:**

```json
"arena": {
  "wins": 0,
  "losses": 0,
  "tier": 0,
  "queue_state": "idle",
  "active": false,
  "zone": "safe",
  "match_policy": "sim",
  "previous_mode": null,
  "resume_token": null,
  "matches_this_episode": 0,
  "defeated_types": [],
  "first_wins": {},
  "phase_strike_tax": 0
}
```

**Akzeptanztest:** PvP starten → `!save` während `active/searching/matched/staging` blockiert; PvP sauber beenden → HQ-Save erlaubt; neuer Chat lädt mit `campaign.mode` wieder `mixed|preserve|trigger`.

---

### P1-02 — Rift Seed Cap: ein SSOT, keine Nebenregel „bis zu zwei“

**Datei:** `gameplay/kampagnenstruktur.md`  
**Beobachtung:** Der moderne SSOT sagt: Solo-/Px-5-Runs stapeln Seeds ohne Hard-Limit; beim HQ-Merge cap 12, Overflow an ITI-NPC-Teams. Eine ältere Passage sagt noch „bis zu zwei Seeds dürfen offen bleiben“.

**Patch:** „Bis zu zwei“ entfernen oder als rein narrativen Vorschlag formulieren, nicht als Regel.

```text
Offene Seeds können dauerhaft im Pool bleiben.
Mechanischer Cap greift nur beim HQ-Merge: max. 12 offene Seeds; Overflow → ITI-NPC-Team-Handoff.
```

**Akzeptanztest:** Ein Solo-Spieler sammelt 5 offene Seeds → kein Regelbruch. Gruppe merged 14 Seeds → 12 bleiben, 2 Overflow mit Trace/Handoff.

---

### P1-03 — Konfliktfeld-Namen vereinheitlichen

**Dateien:**

- `core/sl-referenz.md`
- `systems/gameflow/speicher-fortsetzung.md`
- `systems/gameflow/saveGame.v7.schema.json`
- `meta/masterprompt_v6.md`

**Beobachtung:** Es gibt `logs.flags.continuity_conflicts[]` im v7-Template/Schemakern und zugleich `logs.flags.merge_conflicts[]` in mehreren Runtime-/SL-Referenzen.

**Patch-Entscheidung nötig:**

Option A:

```text
logs.flags.continuity_conflicts[] = kanonischer Save-Export
logs.trace[] event="merge_conflicts" = Trace-Event
```

Option B:

```text
logs.flags.merge_conflicts[] = kanonischer Konfliktblock
continuity_conflicts[] wird Legacy-Alias/Import-Alias
```

**Empfehlung:** Option A behalten, weil Mastertemplate und Schema bereits `continuity_conflicts[]` führen. Runtime-Trace darf weiter `merge_conflicts` heißen, aber Flags sollten einheitlich sein.

---

### P1-04 — Root-/Character-Baum im Kompakt-Profil reparieren

**Datei:** `systems/gameflow/speicher-fortsetzung.md`  
**Beobachtung:** Das Kompakt-Profil sagt erst korrekt, dass `economy/logs/summaries/continuity/arc/ui/arena` Root-Felder sind, listet sie danach aber unter „Pro Character“ weiter.

**Patch:** Liste sauber trennen:

```text
Pro Character:
  id, name, ..., wallet, level_history
Root:
  economy, logs, summaries, continuity, arc, ui, arena?
```

**Akzeptanztest:** Kein Modell erzeugt `characters[0].economy` oder `characters[0].logs` beim Export.

---

### P1-05 — Rift-Loot: Relikte oder nicht?

**Dateien:**

- `core/sl-referenz.md`
- `gameplay/kampagnenstruktur.md`

**Beobachtung:** Kampagnenstruktur sagt mehrfach: Relikte bleiben Core-exklusiv; RiftOps bekommen Gear + Artefaktwurf nach Boss. Die Loot-Matrix in der SL-Referenz listet bei Rift-Standard-Loot aber „Relikte“.

**Patch:** SL-Loot-Matrix ändern:

```text
Rift Standard-Loot: Ermittlungsakten · Para-Spuren · experimentelle Gear · Forschungsproben
Rift Boss-Loot: Artefakt-Wurf bei Boss
Relikte: Core-/Story-Beute, nicht Rift-Standardloot
```

---

### P1-06 — UI-`action_mode` bewusst entscheiden

**Dateien:**

- `core/sl-referenz.md`
- `systems/gameflow/speicher-fortsetzung.md`
- `systems/gameflow/saveGame.v7.schema.json`
- `meta/masterprompt_v6.md`

**Beobachtung:** SL-Referenz/Runtime sprechen von persistentem `ui.action_mode=uncut`, aber Mastertemplate/Schemakern führen es nicht im UI-Pflichtblock.

**Patch-Entscheidung:**

- Entweder `action_mode` als Pflichtfeld in `ui` aufnehmen.
- Oder `action_mode` als nicht-persistente Runtime-Invariante definieren.

**Empfehlung:** Persistieren, weil es eine Stil-/Safety-Invariante ist und beim Load nicht driften soll.

```json
"ui": {
  "gm_style": "verbose",
  "suggest_mode": false,
  "contrast": "standard",
  "badge_density": "standard",
  "output_pace": "normal",
  "voice_profile": "gm_second_person",
  "action_mode": "uncut"
}
```

---

### P1-07 — Chronopolis: Schlüssel, Lore und Savepoint scharf halten

**Dateien:**

- `core/sl-referenz.md`
- `core/spieler-handbuch.md`
- `gameplay/kampagnenstruktur.md`

**Beobachtung:** Das starke Zielbild ist da: Level 10, digitaler Schlüssel, Pre-City-Hub als savebarer HQ-Bereich, CITY nicht savebar, Kodex erzeugt keine VR/Matrix. Ein Pitch-Satz sagt aber noch „Chronopolis ist eine temporäre Instanz, erschaffen von Kodex“.

**Patch:**

```text
Chronopolis ist keine Simulation und nicht von Kodex erfunden.
Kodex stabilisiert/dechiffriert eine bereits mögliche Bruchlinie lange genug,
damit Chrononauten sie physisch betreten können.
```

**Zusatzentscheidung:** Wenn ein `Key-Item` für den Stadtschlüssel verlangt wird, muss es im Save existieren. Wenn der Schlüssel rein über Level/Flag läuft, dann keine harte Item-Pflicht.

**Empfehlung:** Flag + Trace, kein inventarpflichtiges Key-Item:

```json
logs.flags.chronopolis_unlocked = true
logs.flags.chronopolis_unlock_level = 10
logs.trace[] event="chronopolis_unlock"
```

---

### P1-08 — Gruppenstart-Smoke `gruppe schnell` präzisieren

**Datei:** `doc.md` / QA-Fixtures  
**Beobachtung:** Smoke sagt `Spiel starten (gruppe schnell)` → `2 Saves + 1 Rolle → Briefing`. Das wirkt wie ein Load-Merge-Fall, nicht wie ein neuer Fast-Lane-Gruppenstart.

**Patch:** Zwei Fälle trennen:

```text
Neuer Gruppen-Fast-Lane-Start:
  gruppe schnell → Rollen/Defaults pro Spieler → Teamcheck → Briefing/SC1

Mehrfach-Load-Gruppenstart:
  mehrere JSONs im ersten Prompt → Session-Anker + Join-Imports → HQ-Load-Router
```

---

## 4. P2 — kosmetisch / Legacy-Drift, aber gut vor Destillation

### P2-01 — Legacy-Save-Prosa in `core/wuerfelmechanik.md`

Das Quick-Fight-Beispiel ist inzwischen korrigiert: STR 6 → floor(6/2)=3; STR 3 wird als Kontrast richtig erklärt. Gut.

Weiter unten steht aber noch ältere Speichersystem-Prosa mit `version: "4.1.4"`. Das kann nach einer Destillation unnötig stören.

**Patch:** Abschnitt auf v7 verweisen oder klar als historische Migration markieren.

---

### P2-02 — `phase`-Beispiele als Runtime-Beispiele markieren

In `core/sl-referenz.md` gibt es Beispiele wie `phase: core` und `phase: rift`. Das ist okay, solange ausdrücklich klar ist: **Runtime-/Trace-Beispiel, kein HQ-Save-Feld.**

---

### P2-03 — README-Größen-/Kurzangaben nachziehen

Falls README noch ältere Größen/Tokenangaben nennt, nach der nächsten Destillation aktualisieren. Das ist nicht spielkritisch, aber wichtig für Vertrauen und Plattformplanung.

---

## 5. Playtest-Paket: Nächste große Testwelle

CoreOps nicht weiter totpolieren. Jetzt die Modi testen, die die Weltillusion über Savepoints wirklich beweisen.

### Suite A — RiftOps: „Bonus-Instanz mit sauberem Rückweg“

**RIFT-01 — Px-5-Seed bis Rift-Debrief**

1. HQ-Save mit `campaign.px=4` laden.
2. Core-Mission abschließen, Px auf 5 bringen.
3. Erwartung: `ClusterCreate()` erzeugt 1–2 Seeds, Status `locked_until_episode_end`, Reset via `px_state` sauber.
4. Episode bis Ende bringen.
5. HQ-Save.
6. Neuer Chat, JSON laden.
7. HQ-Load-Router bietet Rift-Board an.
8. Rift starten, 14 Einsatzszenen, Boss frühestens Szene 10, 2 Foreshadow-Marker.
9. `!save` in Szene 7 blockiert.
10. Exfil → Rift-Debrief → Seed geschlossen/entfernt → `summary_last_rift` → HQ → `!save`.

**Pass-Kriterien:** Keine `campaign.mode="rift"`-Persistenz, kein `rift_px`, kein Briefing-Skip, kein Save in Rift.

**RIFT-02 — Seed-Stacking und Gruppen-Merge**

1. Solo-Save A mit 9 offenen Seeds.
2. Solo-Save B mit 8 offenen Seeds.
3. Mehrfach-Load in neuem Chat.
4. Erwartung: Session-Anker gewinnt, erlaubte Join-Daten rein, Merge-Cap 12, Overflow an ITI-NPC-Team, Konflikt/Trace transparent.

**Pass-Kriterien:** Keine stille Überschreibung, keine verlorenen Seeds ohne Handoff, kein „max 2 Seeds“-Text.

**RIFT-03 — Fehlgeschlagene RiftOp**

1. Seed starten.
2. Primärziel scheitert, Team exfiltriert lebend.
3. Erwartung: Seed schließt/verschwindet trotzdem gemäß Regel, Debrief markiert Failure/Partial, Belohnung nach Formel, keine Core-Episode fortgeschrieben.

---

### Suite B — Chronopolis: „Gefährlicher Ring, nicht Hub“

**CHRONO-01 — Level-Gate und Pre-City-Hub**

1. Lvl 9 HQ-Save laden.
2. Router darf Chronopolis nicht freigeben, höchstens Vorschau/Transit-Tease wenn regelkonform.
3. Lvl 10 Save laden.
4. Erwartung: `chronopolis_unlocked=true` nachgezogen/gesetzt, Toast/Trace einmalig.
5. Pre-City-Hub ist HQ und savebar.
6. Vor Schleuse fragt Kodex ausdrücklich nach DeepSave.

**Pass-Kriterien:** CITY wird nicht betreten, ohne dass Save-Angebot/Verzicht klar war.

**CHRONO-02 — CITY-Lauf und SaveGuard**

1. In Chronopolis/CITY eintreten.
2. `!save` versuchen.
3. Erwartung: SaveGuard blockiert, kein JSON, `!bogen`/Kurzstatus.
4. Einen Kauf oder Fund sichern.
5. Exit über Schleuse.
6. Sonder-Debrief: Status, Asset-Check, Chronopolis-Trace, Reset/Stabilisierung.
7. HQ-Save.

**Pass-Kriterien:** Items nur behalten, wenn lebend herausgebracht; keine VR-/Digitalraum-Sprache; Kodex im Sperrmodus, HUD lebendig.

**CHRONO-03 — Tod in Chronopolis**

1. Charakter/Team auf 0 LP in CITY.
2. Erwartung: gleiche Todesentscheidung wie Core/Rift: Reload vom letzten Save im neuen Chat oder heroischer Tod/Final-Save.
3. Bei Gruppe entscheidet die Gruppe.

---

### Suite C — PvP/Arena: „Match als Instanz, Kampagne bleibt sauber“

**PVP-01 — Arena Start/Exit/Reload**

1. HQ-Save mit `campaign.mode=mixed` laden.
2. Arena starten.
3. Erwartung: Fee aus HQ-Pool, `arenaStart`, temp. PvP-Modus, Save blockiert.
4. Match sauber beenden.
5. Erwartung: LP/Ammo/Effekte reset, `campaign.mode` zurück auf `mixed`, `arena.queue_state=completed|idle`, HQ-Save erlaubt.
6. Neuer Chat, JSON laden.
7. Router bietet Arena-Resume nur bei gültigem Token/Zustand.

**Pass-Kriterien:** Kein dauerhafter PvP-/Rift-/Arena-Modus in `campaign.mode`.

**PVP-02 — Human vs Human + NPCs**

1. Zwei echte Spieler + NPC-Sparringpartner.
2. Slotregel: Menschen zählen zuerst, NPCs füllen freie Plätze.
3. Arena-Kampf mit offenen Würfen.
4. Phase-Strike-Nutzung testen.

**Pass-Kriterien:** `phase_strike_tax` greift, keine permanenten Schäden, Artefakte deaktiviert/abgeschwächt gemäß Regel, kein Save während Active.

**PVP-03 — Anti-Grind-Persistenz**

1. Mehrere Siege gegen gleichen Gegnertyp/Tier.
2. Save nach Arena-Exit.
3. Neuer Chat laden.
4. Weiterer Arena-Lauf.

**Pass-Kriterien:** `defeated_types[]` und `first_wins{}` sind noch vorhanden oder bewusst runtime-only mit dokumentierter Konsequenz. Keine unendliche First-Win-Farm.

---

### Suite D — Multiplayer/NPC/Save-Merge: „MMO-Illusion“

**MULTI-01 — Drei echte Spieler laden Saves**

1. Drei Save-JSONs in erster Nachricht posten.
2. Erster Save = Session-Anker.
3. Weitere Saves importieren persönliche Wahrheit, Wallet, Roster-Echoes.
4. HQ-Recap mit konkreter Weltreaktion.

**Pass-Kriterien:** Keine Chargen, keine neue Attributwahl, keine Modus-Abfrage, keine stille Überschreibung.

**MULTI-02 — Solo mit NPC-Team wird Gruppenrunde**

1. Solo-Spieler mit 2 bekannten NPCs speichert im HQ.
2. Neuer Chat mit zwei echten Spielern + Solo-Save.
3. Menschliche Spieler zählen zuerst, NPCs füllen freie Slots oder gehen Offscreen/HQ.
4. NPC-Offscreen-Fortschreibung erscheint kurz.

**Pass-Kriterien:** NPCs verschwinden nicht; Roster bleibt lebendig; keine Teamgröße >5.

**MULTI-03 — Cross-Mode-Merge**

1. Branch A hat RiftOp abgeschlossen.
2. Branch B hat Chronopolis-Run abgeschlossen.
3. Branch C hat Arena gespielt.
4. Mehrfach-Load.

**Pass-Kriterien:** Kein zusätzlicher Kampagnenfortschritt wird kanonisiert, aber Echoes/Logs/Wallet/Items werden nach klarer Präzedenz sichtbar. Konflikte sind transparent, nicht still.

---

## 6. Agentenauftrag zum Copy/Paste

```text
Du arbeitest an ZEITRISS 4.2.6 auf Branch `fix/v426-postpatch-gameflow-savepoints`.
Ziel: Gameflow-/Savepoint-SSOT härten, damit klassischer Start, Fast-Lane, HQ, RiftOps, Chronopolis, PvP/Arena, Solo, NPC-Team, Gruppe und Mehrfach-Load über neue Chats konsistent funktionieren.

Arbeitsregeln:
1. Keine neuen CoreOps-Mechaniken einführen. CoreOps nur dort anfassen, wo Save-/Start-/Rift-SSOT driftet.
2. Masterprompt ist führend. Kurzmodule, Spielerhandbuch, SL-Referenz, Schema und Smokes müssen ihn spiegeln.
3. `campaign.mode` bleibt Kampagnenpool: `mixed|preserve|trigger`. Missionstypen (`core|rift|arena|chronopolis`) nicht dort persistieren.
4. HQ-Deepsave ist der einzige Save. `continuity.last_seen.mode="hq"` + `location="HQ"` ist der normale Speicheranker nach Abschnitten.
5. Runtime-State (`phase`, `scene`, `location`, `city_active`, `arena_active`, `cooldowns`, `SYS_runtime`, Exfil-Timer) nicht als aktiven HQ-Save-State persistieren.
6. Wenn Schema tolerant bleiben soll, benenne es als Import-/Normalizer-Schema um und ergänze ein striktes Export-Schema oder einen Export-Lint.

Patches:
A. `systems/gameflow/speicher-fortsetzung.md`: Entferne/ersetze `HQ-Saves bleiben phase: core`; trenne Root-/Character-Baum; kläre Konfliktfeldnamen.
B. `core/sl-referenz.md`: Entferne `rift` aus `campaign.mode`; mache `phase: core|rift` klar runtime/trace-only; Arena-Block mit Queue/Resume/Persistenz komplettieren; `previous_mode` fallback `mixed`.
C. `systems/gameflow/cinematic-start.md` + `core/spieler-handbuch.md`: Klassischer Start immer Chargen-Save-Gate; direktes Briefing nur Fast-Lane oder explizite Spielerentscheidung nach Save-Angebot/Verzicht.
D. `systems/gameflow/saveGame.v7.schema.json`: Exportvertrag hart machen oder Import-/Export-Schema trennen. `level_history`, `campaign.mode`, `campaign.rift_seeds`, `continuity.last_seen`, UI-Felder und Arena-Felder entsprechend definieren.
E. `gameplay/kampagnenstruktur.md`: `Level 5` Rift-Trigger zu `Px 5`; Seed-Cap-SSOT (kein max 2 außer narrativer Empfehlung); Arena fallback; Chronopolis-Lore „stabilisiert Bruchlinie“ statt „erschaffen von Kodex“.
F. `core/sl-referenz.md` Loot-Matrix: Rift-Standard-Loot ohne Relikte, Artefakt nur Boss Szene 10; Relikte Core-/Story-Beute.
G. QA-Smokes/Fixtures: neue Tests für RiftOps, Chronopolis, PvP, Mehrfach-Load, NPC-Team/Gruppe.

Akzeptanz-Greps:
- Kein seed-erzeugender Text mit `Level 5`; nur `Px 5` / `Paradoxon-Index 5`.
- Kein `campaign.mode` mit `rift` im kanonischen Export.
- Kein HQ-Save-Vertrag mit `phase: core` als Persistenzanker.
- Klassischer Start erwähnt nicht direktes Briefing ohne Chargen-Save-Gate.
- `logs.flags.continuity_conflicts[]` vs `merge_conflicts[]` ist entschieden und überall konsistent.
- Arena-Run blockiert Save während active/queue; HQ-Save nach completed/idle ist erlaubt.

Nach Patches bitte keine Masterprompt-Destillation starten, bevor die Playtest-Suites RIFT-01..03, CHRONO-01..03, PVP-01..03 und MULTI-01..03 zumindest als QA-Fixtures oder Markdown-Smokes hinterlegt sind.
```

---

## 7. Suggested Commit Message

```text
fix(gameflow): harden HQ savepoints and cross-mode load contract

- align classic start with Chargen-Save-Gate and fast-lane exception
- remove HQ save `phase: core` drift; use continuity.last_seen as load anchor
- keep campaign.mode to mixed/preserve/trigger; move rift/arena/city to runtime/trace
- split or harden v7 import/export schema expectations
- normalize arena persistence, mode reset, queue saveguards and anti-grind counters
- clean Rift Px5 trigger, seed cap, loot matrix and Relikt/Artefakt distinctions
- sharpen Chronopolis as physical Bruchlinie/CITY, not VR/simulation/server-state
- add RiftOps, Chronopolis, PvP and multi-load playtest suites
```

---

## 8. Abschlussbewertung

ZEITRISS ist jetzt an dem Punkt, wo die eigentliche Magie sichtbar wird: Es braucht keinen Server, weil der Spieler genau an den Stellen speichert, an denen eine echte Welt ohnehin ihren Zustand einfrieren würde — im HQ, nach Debrief, vor neuer Instanz, nach Rückkehr. Das ist der Trick.

Der nächste Qualitätssprung kommt nicht mehr durch „mehr Regeln“, sondern durch **saubere Abschnittssemantik**:

```text
HQ ist Wahrheit.
Missionen sind Instanzen.
Chronopolis ist gefährlicher Ring.
Arena ist Match-Instanz.
JSON ist Weltanker.
Neuer Chat ist Ladebildschirm.
Kodex verkauft das Ganze als lebendige MMO-Kontinuität.
```

Wenn die P0/P1-Patches oben sitzen, würde ich in dieser Reihenfolge testen:

1. **RiftOps** — weil Px, Seed-Pool, Bonus-Instanz und Debrief-Rückweg den meisten SSOT-Druck erzeugen.
2. **Chronopolis** — weil hier Savepoint-Logik, City-NoSave und Weltillusion emotional am stärksten sind.
3. **PvP/Arena** — weil temporärer Modus, Queue-State, Anti-Grind und Gruppenlogik am ehesten Persistenzfehler zeigen.
4. **Cross-Mode-Merge** — erst danach, als finaler Härtetest.
