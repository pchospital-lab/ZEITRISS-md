---
title: "ZEITRISS 4.2.8 - Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)"
version: 4.2.8
tags: [system]
---

# ZEITRISS 4.2.8 - Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)

## SSOT-Anker (Systems-Pass)

- **MUSS:** SaveGuard bleibt HQ-only; Missionen, Arena-Warteschlange und
  Chronopolis sind keine gültigen Speicherkontexte.
- **MUSS:** Px bleibt einheitlich (`campaign.px` als Quelle). Bei Px 5 löst
  ausschließlich `ClusterCreate()` aus; der Reset erfolgt via HQ-Bestätigung.
- **MUSS:** Economy-Sync bleibt konsistent (`economy.cu` als Primäranker,
  `economy.credits` als Legacy-Fallback via Synchronisierung).
- **SOLL:** Neuer Chat pro Mission wird als empfohlener Stabilitätspfad geführt,
  ohne als harte Regel formuliert zu werden.
- **KANN:** Optionale QA-/Trace-Felder dürfen ergänzt werden, sofern sie keine
  Kernregeln (SaveGuard, Px-Flow, Belohnungslogik) verändern.

## Speichern & Laden - Kurzreferenz

> **Für Spieler:** Hier das Wichtigste in 30 Sekunden.
>
> - **Speichern** geht nur im HQ (nach Missionen, vor dem nächsten Einsatz).
> - Befehl: `!save` - der Kodex erzeugt einen JSON-Block zum Kopieren.
> - **Laden:** `Spiel laden` im neuen Chat, dann JSON einfügen.
> - **In Missionen wird nicht gespeichert** - das erhöht die Spannung.
> - **Neuer Chat pro Mission** empfohlen: Mission abschließen → HQ → Save → neuer Chat → Laden.
>
> *Technische Details für die KI-Spielleitung folgen unten.*

## HQ-JSON-Save {#json-schluesselfelder}
> **Guard:** Speichern nur in der HQ-Phase; Pflichtwerte sind deterministisch.
> Chat-Befehle: `!save`, `!load`, optional `!autosave hq`, `!suspend`, `!resume`.
> Einziger Save-Typ: Deepsave (HQ-only).

**Referenz-Fixture (Test-Save v6):** Ein vollständig ausgefüllter Teststand mit
allen Pflichtfeldern inklusive Cross-Mode-Pfaden (`economy.wallets{}`,
`logs.psi[]`, `arc_dashboard.offene_seeds`, `arena.phase_strike_tax`) liegt als
kanonisches Fixture unter
[`internal/qa/fixtures/savegame_v6_test.json`](../../internal/qa/fixtures/savegame_v6_test.json).
Acceptance-Smoke-Prüfpunkte 4 (HQ-Save-Guard) und 10 (Cross-Mode-Saves) nutzen
diesen Block als Eingabe für Solo-, Solo→Koop- und Koop→Arena-Tests.

## Save-Prompts im HQ-Flow
- **Grundregel:** Save-Prompts nur, wenn die Crew frei im HQ ist oder es verlassen will; niemals in
  Missionen, Arenawarteschlangen oder Chronopolis.
- **Verbindliche Trigger (chronologisch):**
  - **Vor dem Briefing/Absprung** (Core, Rift, PVP-Arena): erst speichern, dann Briefing anfordern,
    damit der Save im HQ startet und kein offener Missionsblock im JSON landet.
  - **Nach jedem Debriefing**: sobald Belohnungen verbucht sind und die Crew wieder frei im HQ steht.
  - **Nach längeren HQ-Freerun-Phasen**: sobald ein größerer Umbau/Shop/Clinic-/Werkstatt-Block
    abgeschlossen ist (insbesondere vor einem Themenwechsel im Chat).
  - **Vor Chronopolis-Schleuseneintritt**: Kodex fragt verpflichtend „Jetzt HQ-DeepSave erstellen?“,
    erst danach startet die Schleuse.
  - **Nach Chronopolis-Rückkehr ins HQ**: sofortiger Save-Prompt, damit Runs entkoppelt bleiben.
- **Chronopolis & Arena:** Chronopolis zählt als City und blockiert Saves. PVP-Arena speichert
  ebenfalls nicht - Save-Prompts greifen erst nach Rückkehr ins HQ bei
  `queue_state=idle|completed`.
- **Chat-Hygiene:** Empfohlen ist ein frischer Chat pro HQ→Mission→HQ-Zyklus. Leite nach dem Save
  an: "Nächster Chat? JSON importieren, dann weiter." So bleibt der Deepsave die einzige Quelle der
  Wahrheit.

#### Textbaustein: Vor Chronopolis-Schleuseneintritt (Savepflicht als Stimmung)

Spielleitung: Nutzt die Savefrage nicht als nüchternes Menü, sondern als
letztes „Bist du sicher?", bevor das Tor öffnet.

Beispieltext:
Die Schleuse verriegelt. Ein rotes Statuslicht läuft über die Kanten der Tür,
als würde das ITI selbst tief Luft holen.

Im Ohr klickt der Kodex trocken:
„Chronopolis-Zugang erkannt. Signaturprüfung erforderlich."

Eine Pause — lang genug, um nicht mehr nur technisch zu wirken.

Dann:
„Verbindlicher Check: HQ-DeepSave jetzt erstellen?"

Macht klar: Das ist kein Komfort-Button. Das ist die letzte saubere Linie,
bevor ihr in eine Stadt tretet, die sich anfühlt wie euer Scheitern.

**SaveGuard (Pseudocode)**

> *Die folgenden Strings und Codeblöcke sind KI-Spielleiter-Referenz und nicht
> für Spieler gedacht.*

{# LINT:HQ_ONLY_SAVE #}
```pseudo
assert state.location == "HQ", (
  "SaveGuard: Speichern nur im HQ - HQ-Save gesperrt."
)
assert state.character.attributes.SYS_installed == state.character.attributes.SYS_max
assert state.character.attributes.SYS_runtime <= state.character.attributes.SYS_installed
assert state.character.stress == 0 und state.character.psi_heat == 0
assert not state.get('timer') und not state.get('exfil_active') und not campaign.exfil.active
required = [
  "character.id",
  "character.attributes.SYS_max",
  "character.attributes.SYS_installed",
  "character.attributes.SYS_runtime",
  "character.attributes.SYS_used",
  "character.stress",
  "character.psi_heat",
  "character.cooldowns",
  "campaign.px",
  "economy",
  "economy.wallets",
  "logs",
  "logs.hud",
  "logs.trace",
  "logs.artifact_log",
  "logs.market",
  "logs.offline",
  "logs.kodex",
  "logs.alias_trace",
  "logs.squad_radio",
  "logs.foreshadow",
  "logs.fr_interventions",
  "logs.psi",
  "logs.arena_psi",
  "logs.flags.merge_conflicts",
  "logs.flags",
  "ui",
  "arena"
]
assert serializer_bereit(required)

# UI-Felder sind persistent - Pflichtschreibung beim Save
ui_persistent = [
  "ui.suggest_mode",
  "ui.contrast",
  "ui.badge_density",
  "ui.output_pace"
]
for field in ui_persistent:
  assert state.resolve(field) is not None, (
    f"SaveGuard: UI-Feld {field} fehlt - UI-Persistenz verletzt."
  )
```

> **Regel: UI-Felder sind persistent.** Was der Spieler einstellt, bleibt.
> Die Felder `ui.suggest_mode`, `ui.contrast`, `ui.badge_density` und
> `ui.output_pace` werden beim Speichern **IMMER** geschrieben - kein
> Weglassen, kein Fallback auf Defaults. Der SaveGuard bricht ab, wenn
> eines dieser Felder `null` oder nicht vorhanden ist.

Speichern ist ausschließlich in der HQ-Phase zulässig. Alle Ressourcen sind
dort deterministisch gesetzt. **HQ** meint das ITI-Nullzeit-Hub inklusive
aller ITI-Decks und den Pre-City-Hub; Chronopolis zählt als eigener
`CITY`-Status und ist **kein** HQ: Saves aus der City brechen mit
"SaveGuard: Chronopolis ist kein HQ-Savepunkt - HQ-Save gesperrt." ab.
`flags.runtime.skip_entry_choice` bleibt ein reines Laufzeit-Flag und gehört
nicht ins Save; Persistenzanker sind ausschließlich
`campaign.entry_choice_skipped` und `ui.intro_seen`.

Das versionierte JSON-Schema liegt unter
`systems/gameflow/saveGame.v6.schema.json`; `load_deep()` validiert Saves gegen
dieses Schema und bricht mit einem `Save-Schema (saveGame.v6)`-Fehler ab, wenn
Pflichtcontainer fehlen oder die Typen nicht passen.
Die Schema-Datei wird nicht in den Wissensspeicher geladen und bleibt primär
für Loader-/CI-Validierungen bestehen; für GPT-Läufe genügt das
Klartextprofil unten.

`logs.hud[]` erlaubt Strings **oder** strukturierte Objekte. Sonder-Overlays
laufen über `hud_event(event, details)` und akzeptieren ausschließlich
`vehicle_clash` (Felder `tempo`, `stress`, `damage`) oder `mass_conflict`
(`chaos`, `break_sg`, `stress`). Der Helper mappt Aliasse (`vehicle`
→ `vehicle_clash`, `mass` → `mass_conflict`), normalisiert numerische Felder,
ergänzt fehlende `at`-Timestamps automatisch und fällt bei unbekannten Events
auf einen generischen HUD-Eintrag zurück, statt die Struktur zu verwerfen. Die
Objektform folgt `{event, scene?, details{…}, at?}`; fehlende Felder werden bei
`save_deep()` ergänzt. Budget-Guards (2 Toasts/ Szene, Critical-Tags wie
OFFLINE/SAVE/SCHEMA/ARENA/GATE/FS/BOSS/ENTRY ausgenommen) und tracebare
Unterdrückungen sichern konsistente Roundtrips für beide Events.
Unterdrückte Toasts landen zusätzlich in `logs.hud[]` als `{tag, message,
suppressed:true, reason:"budget", action:"suppressed|merged"}`.

Offline-Fallbacks gelten nur während Missionen: Im HQ besteht immer
Kodex-Uplink. Falls ein Einsatz im Offline-Modus endet, sperrt `save_deep()`
den HQ-Save bis zum Re-Sync ("SaveGuard: Offline - HQ-Deepsave erst nach
Re-Sync - HQ-Save gesperrt."), schreibt gleichzeitig ein `logs.trace[]`-Event
`save_blocked` (`reason: offline`) und führt keine weiteren Save-Guards aus.
Der Befehl `!offline` ist
auf 60 s getaktet; Rate-Limit-Meldungen zählen weder den Offline-Counter hoch
noch füllen sie das Protokoll.

**SaveGuard-Reihenfolge** *(KI-Spielleiter-Referenz)*: Offline blockiert exklusiv und schreibt
`reason: offline`. Danach greift der Arena-Blocker (`reason: arena_active`
inkl. `queue_state`/`phase`/`zone`), anschließend HQ-only (`hq_only` oder
`chronopolis`). Erst danach folgen Exfil-, SYS-, Stress- und Psi-Heat-Checks,
die dieselben Guard-Strings nutzen. Alle Guards landen als `save_blocked`-Trace
mit `reason`, `location` und `phase` (Fallback auf `state.phase`, falls
`campaign.phase` fehlt), damit Reihenfolge und Auslöser in Snapshots
transparent bleiben. Der QA-Test `test_saveguard_order.js` prüft die Kette
offline → Arena → HQ-only/Chronopolis inklusive Trace-Payload.

| Priorität | Guard | Trace-Reason | Hinweis |
| --- | --- | --- | --- |
| 1 | Offline | `offline` | Exklusiv; kein weiterer Guard danach. |
| 2 | Arena aktiv | `arena_active` | `queue_state`/`phase`/`zone` im Trace. |
| 3 | HQ-only/Chronopolis | `hq_only`/`chronopolis` | Pre-City-Hub zählt als HQ. |
| 4 | Exfil aktiv | `exfil_active` | Blockt HQ-Save bis Rückkehr. |
| 5 | SYS-Checks | `sys_not_full`/`sys_overflow`/`sys_runtime_overflow` | Vollinstallation + Runtime-Limit. |
| 6 | Stress aktiv | `stress_active` | Blockt bis Stress 0. |
| 7 | Psi-Heat aktiv | `psi_heat_active` | Blockt bis Psi-Heat 0. |

### Kompakt-Profil für GPT (Save v6)
Das Schema ist zusätzlich als Klartext-Profil für MyGPT gespiegelt, damit es
ohne Artefakt-Anhang in den Wissensspeicher passt. Orientiere dich an
SaveGuard + folgendem Pfadbaum:

- `save_version`, `zr_version`, `location`, `phase`
- `character.{id,name,rank,stress,psi_heat,cooldowns,attributes.SYS_max|installed|runtime|used}`
- `campaign.{episode,scene,px,rift_seeds[]}`
- `team.members[]`, `party.characters[]`, `loadout`, `economy.{cu,wallets}`
- `vehicles` mit Charakter-Slots (1 HQ-Technoir-Basisfahrzeug pro
  Charakter-ID) und optionalem `active_vehicle_slot` pro Mission.
- Optional `vehicles.faction_temporal_assets[]` für legendäre Chronopolis-
  Schiffe (Tech IV) als zusätzliche, fraktionsgebundene Garagen-Slots.
- `logs` mit folgenden Pfaden:
  - `artifact_log`, `market`, `offline`, `kodex`, `alias_trace`, `squad_radio`, `hud`, `psi`,
    `arena_psi`, `foreshadow`, `fr_interventions`
  - `flags{runtime_version,chronopolis_warn_seen,
    chronopolis_unlock_level,chronopolis_unlocked,atmosphere_contract,
    hud_scene_usage}`
  - `flags.merge_conflicts[]`
- `arc_dashboard{offene_seeds[],fraktionen{},fragen[],timeline[]}`
- `ui` (vollständiger UI-Block)
- `arena` (Status inkl. `queue_state=idle|searching|matched|staging|active|completed`,
  `zone=safe|combat`, `team_size` hart 1-5, `match_policy=sim|lore`)

`logs.flags.last_save_at` hält den Zeitstempel für deterministische Saves fest. Der Serializer nutzt
den Wert für automatisch gestempelte HUD-Events (Fallback ohne `at`) sowie für den Save-Trace
`economy_audit`, damit Roundtrips keine neuen Zeitmarken erzeugen.

`economy_audit()` dokumentiert jeden HQ-Save mit stabilen Feldern: `level`, `band_reason`,
`hq_pool`, `wallet_sum`, `wallet_count`, `wallet_avg`, `wallet_avg_scope`,
`chronopolis_sinks`, `target_range`, `delta` und `out_of_range`. `target_range` nutzt fixe
Level-Bänder **120** (HQ 8 000-10 000 CU, Wallet Ø 1 000-2 000 CU), **512** (HQ 25 000-30 000 CU,
Wallet Ø 3 000-5 000 CU) und **900+** (HQ 45 000-60 000 CU, Wallet Ø 6 000-10 000 CU) und skaliert
`wallet_total` über alle Wallets. Die Band-Auswahl folgt dem Host-Level
(`character.lvl|level` oder `campaign.level`); fehlt dieser, nutzt der Audit die Medianstufe der
Party/Team-Roster und schreibt `band_reason=host_level|roster_median|unknown`. `wallet_avg_scope`
steht immer auf `economy.wallets`. `delta` markiert Abweichungen pro Wert, `out_of_range` setzt
boolesche Flags und löst
den Toast "Economy-Audit: HQ-Pool/Wallets außerhalb Richtwerten (Lvl 120|512|900+)." aus.
Der Save-Trace `economy_audit` landet in `logs.trace[]` und folgt der Save-Guard-Priorität, sodass
Arena-/Offline-Blocker keine fehlerhaften Audit-Deltas erzeugen.

Die JSON-Schema-Datei bleibt für Validierungstools bestehen; GPT nutzt
das Klartext-Profil als maßgebliche Struktur.

Der Serializer befüllt `arc_dashboard` vor dem SaveGuard automatisch mit
leeren Arrays/Objekten und setzt fehlende Dashboard-Blöcke nicht stillschweigend
zurück: Pflichtpfade (`offene_seeds`, `fraktionen`, `fragen`, `timeline`) lösen
einen SaveGuard-Fehler aus, falls sie fehlen oder `null` sind.

`campaign.exfil{active, armed, hot, ttl, sweeps, stress, anchor, alt_anchor}`
spiegelt den Zustand des Exfil-Fensters. Solange `campaign.exfil.active`
oder `state.exfil.active` wahr ist, blockiert der Serializer den HQ-Save mit
"SaveGuard: Exfil aktiv - HQ-Save gesperrt.". Arena- und HQ-Blocker nutzen
denselben Text via `toast_save_block(reason)`. Sobald die Crew ins HQ
zurückkehrt, setzt die Runtime alle Exfil-Felder automatisch zurück.

Alle SaveGuards hängen ihren Grund konsistent an das Suffix "- HQ-Save
gesperrt." an: Offline-Reasons und Arena-Locks teilen sich den Klammertext,
SYS-Guards nutzen dieselbe Formulierung bei Overflow-Checks und fehlender
Vollinstallation; Stress und Psi-Heat brechen ebenfalls mit diesem Suffix ab,
damit die Guard-Matrix konsistent bleibt. **HQ-only** nutzt denselben
SaveGuard-String ("SaveGuard: Speichern nur im HQ - HQ-Save gesperrt.") und
loggt zusätzlich `logs.trace[]` mit `reason: hq_only`.

Arena-Matchmaking (`queue_state=searching|matched|staging|active`) zählt als
aktiver Modus. `save_deep()` liest den Queue-Status aus, setzt `arena.active`
und `arena.phase` im Serializer auf `active` und blockiert den HQ-Save mit
"SaveGuard: Arena aktiv - HQ-Save gesperrt.", bis `queue_state` wieder `idle`
erreicht (auch `completed` bleibt gespeichert, aber blockiert den Save).

In-Mission-Ausstieg ist erlaubt, aber es erfolgt kein Save; Ausrüstung darf
übergeben werden, nächster Save erst im HQ. HQ-Saves verlangen vollständige
Installation (`SYS_installed == SYS_max`) und eine Runtime-Last innerhalb des
installierten Rahmens (`SYS_runtime ≤ SYS_installed`).

```json
{
  "save_version": 6,
  "zr_version": "4.2.6",
  "location": "HQ",
  "phase": "core",
  "character": {
    "id": "CHR-1234",
    "name": "Ghost",
    "rank": "Operator I",
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "attributes": {
      "SYS_max": 5,
      "SYS_installed": 5,
      "SYS_runtime": 5,
      "SYS_used": 5
    }
  },
  "campaign": {"episode": 4, "scene": 0, "px": 0},
  "team": {"members": []},
  "party": {"characters": []},
  "loadout": {},
  "economy": {"cu": 0, "wallets": {}},
  "logs": {
    "artifact_log": [],
    "market": [],
    "offline": [],
    "kodex": [],
    "alias_trace": [],
    "squad_radio": [],
    "hud": [],
    "psi": [],
    "arena_psi": [],
    "foreshadow": [],
    "fr_interventions": [],
    "flags": {
      "runtime_version": "4.2.6",
      "compliance_shown_today": false,
      "chronopolis_warn_seen": false,
      "platform_action_contract": {
        "action_mode": "uncut",
        }
    }
  },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {},
    "fragen": [],
    "timeline": []
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": false,
    "suggest_mode": false,
    "action_mode": "uncut",
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal",
    "voice_profile": "gm_third_person"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
    "match_policy": "sim",
    "previous_mode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "tier": 1,
    "proc_budget": 0,
    "artifact_limit": 0,
    "loadout_budget": 0,
    "phase_strike_tax": 0,
    "damage_dampener": true,
    "team_size": 1,
    "queue_state": "idle",
    "zone": "safe",
    "fee": 0,
    "scenario": null,
    "started_episode": null,
    "last_reward_episode": null,
    "policy_players": [],
    "audit": []
  }
}
```

`campaign.rift_seeds[]` ist die **kanonische Quelle** für offene Seeds. Jede
Struktur enthält mindestens `id`, `epoch`, `label` und `status` (`locked_until_episode_end`/open/closed)
und kann optional `seed_tier: early|mid|late` sowie Metadaten `cluster_hint`
(1-25/80-150/400-1000), `time_marker`, optionales `discovered_at` sowie freies
`level_hint` tragen (reine Balance-Hinweise, keine Gating-Logik). Der
Normalizer hebt Legacy-Strings oder uneinheitliche Felder auf Objektform und
setzt unbekannte Status auf `open`. Launch-Guards erwarten `location='HQ'` und
lehnen Starts mit
aktiver Arena oder fehlenden Seeds ab. `logs.arena_psi[]` spiegelt
Phase-Strike-Events separat vom regulären `logs.psi[]`.
`arc_dashboard.offene_seeds[]` bildet diese Liste nur ab; der Normalizer
führt beide Blöcke beim Laden zusammen und schreibt sie gemeinsam zurück.
Toolkit-Generatoren tragen Seeds ausschließlich in `campaign.rift_seeds[]`
ein, damit Dispatcher, Arc-Dashboard und Debrief dieselbe Quelle nutzen.
Solo-/Px-5-Runs stapeln neue Seeds ohne Hard-Limit. Beim HQ-Merge greift eine
Deckelung auf 12 offene Seeds; überschüssige Seeds gehen als Hand-off an ITI-
NPC-Teams. Der Merge schreibt dazu ein Trace `rift_seed_merge_cap_applied`
(kept/overflow) und einen `merge_conflicts`-Record mit `rift_merge` inklusive
`kept[]`/`overflow[]`, `handoff_to` und `selection_rule`, damit Debriefs den
Hand-off
transparent nachverfolgen können.

> **Spieler-Sprache:** `ClusterCreate()` ist der Moment, wo ihr eure Belohnung
> bekommt. Px 5 erreicht → 1-2 neue Rift-Missionen erscheinen auf der Karte →
> nach der aktuellen Episode könnt ihr sie spielen. Das ist der Loot für gutes Spielen.

**Single Source "Save v6":** Modul 12 führt das _einzige_ kanonische Schema für
HQ-Deepsaves. README und Toolkit zitieren lediglich Auszüge, ohne abweichende
Felder zu definieren. Legacy-Schlüssel (Root-Felder oder
`team.members[]`) sind reine Import-Aliase; neue Saves entstehen ausschließlich
im v6-Format mit `party.characters[]`. Divergierende Doppelstrukturen gelten als
Fehler und werden beim Laden zusammengeführt.

### E2E-Trace-Schema {#e2e-trace}

`logs.trace[]` hält ein kompaktes E2E-Protokoll pro Modus/Szene. Jede Zeile
enthält mindestens `event`, `at` (ISO), `location`, `phase`,
`mission_type`/`campaign_mode`, `scene{episode,mission,index,total}` sowie
`foreshadow{progress,required,tokens,expected}`. Optionale Felder fassen HUD-
Overlay, Radio-/Alias-/Kodex-Zähler, Ökonomie (`economy{cu,wallets}`), FR-Bias
und Arena- oder Seed-Metadaten zusammen. Boss-Snapshots nutzen optional
`boss{type,dr,toast}` (mini|arc|rift) beim Missionsstart. Die Runtime ruft
`record_trace()` bei `StartMission()`, `launch_rift()` und `arenaStart()` auf,
begrenzt die Liste auf 64 Einträge und spiegelt die Snapshots im HQ-Save.
Beim HQ-Save schreibt die Runtime zusätzlich
ein `economy_audit`-Event mit Level, HQ-Pool, Wallet-Summe,
Zielrange (120/512/900+), `band_reason`, `wallet_avg_scope`, Chronopolis-Sinks und Delta-Feldern
(`delta.hq_pool`/`delta.wallet_avg` zum jeweiligen Zielband); ein HUD-Toast
erscheint nur bei Abweichungen. Das Trace ergänzt `logs.hud[]` und ersetzt
keine Toasts.

**Phase-Feld:** HQ-Saves bleiben `phase: core`. Während der Mission setzt die
Runtime `state.phase`/`campaign.phase` automatisch auf
`core|transfer|rift|pvp` (immer Kleinbuchstaben) gemäß Missionstyp und
Szenenzahl. Seeds geben nur den Typ vor und überlassen das `phase`-Feld der
Laufzeit; andere Werte führen beim Laden zu einem SaveGuard-Fehler, da das
Schema nur die vier erlaubten Tokens akzeptiert.

**Accessibility-Felder:** Serializer und Migration normalisieren den UI-Block
(`ui.gm_style`, `ui.suggest_mode`, `ui.action_mode`) und ergänzen fehlende
Felder für `contrast`, `badge_density`, `output_pace` und `voice_profile` mit
Defaults (`standard`/`standard`/`normal`/`gm_third_person` plus
`action_mode=uncut`). `voice_profile` erlaubt ausschließlich `gm_third_person`
oder `gm_observer`; unbekannte Werte fallen auf das Default zurück.
`action_mode` ist immer `uncut` (18+ Tech-Noir). Legacy-Werte wie
`konform|frei|safe|pg-13` werden beim Laden auf `uncut` normalisiert.

> **UI-Persistenz-Regel (Testrun 3, #008):** Die vier Felder `ui.suggest_mode`,
> `ui.contrast`, `ui.badge_density` und `ui.output_pace` sind **persistent**.
> Beim Speichern schreibt der Serializer sie IMMER explizit in den Save-Block.
> Beim Laden restauriert `load_deep()` sie IMMER 1:1 aus dem Save - kein
> Fallback auf Defaults für vorhandene Werte. Nur bei fehlenden Feldern in
> alten Saves (Legacy/pre-v6) setzt der Normalizer folgende Defaults ein:
>
> | Feld | Default für alte Saves |
> | --- | --- |
> | `suggest_mode` | `false` |
> | `contrast` | `"standard"` |
> | `badge_density` | `"standard"` |
> | `output_pace` | `"normal"` |
>
> Diese Defaults gelten ausschließlich als Auffangnetz für Migrationsfälle.
> Aktuelle Saves (v6) müssen alle vier Felder enthalten - der SaveGuard
> bricht andernfalls ab.

### Voller HQ-Deepsave (Solo/Gruppe) {#full-save}

> Referenz-HQ-Block mit Quartier, Timeline, Squad und Feldnotizen. Alle
> Pflichtfelder bleiben erhalten; optionale Blöcke sind knapp, aber vollständig
> ausgefüllt, damit jede Spielleitung sofort den gesamten Charakterbogen
> nachvollziehen kann.

```json
{
  "save_version": 6,
  "zr_version": "4.2.6",
  "location": "HQ",
  "phase": "core",
  "campaign": {
    "episode": 1,
    "mission": 2,
    "mission_in_episode": 2,
    "scene": 0,
    "px": 2,
    "mode": "preserve",
    "exfil": {
      "active": false,
      "armed": false,
      "hot": false,
      "ttl": 0,
      "sweeps": 0,
      "stress": 0,
      "anchor": null,
      "alt_anchor": null
    }
  },
  "character": {
    "id": "AGENT-01",
    "name": "Agent Nova",
    "rank": "Operator I",
    "level": 2,
    "xp": 120,
    "origin": {
      "epoch": "ITI-Nullzeit",
      "hominin": "Homo sapiens sapiens",
      "role": "CQB-Operator"
    },
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "attributes": {
      "STR": 3,
      "GES": 6,
      "INT": 4,
      "CHA": 2,
      "TEMP": 1,
      "SYS_max": 2,
      "SYS_installed": 2,
      "SYS_runtime": 2,
      "SYS_used": 2,
      "hp": 10,
      "hp_max": 10
    },
    "modes": ["mission_focus", "covert_ops_technoir"],
    "self_reflection": true,
    "talents": ["Schleichprofi", "Pistolenschütze", "Reaktionsschnell"],
    "skills": ["CQB", "Taktische Analyse"],
    "implants": [
      {"name": "Reflex-Boost Microline", "sys_cost": 1, "effect": "+1 Initiative"},
      {"name": "Taktisches Ohrimplantat Mk I", "sys_cost": 1, "effect": "+1 Gehör"}
    ],
    "inventory": {
      "weapons": ["CQB-Kampfpistole (SD)", "Tactical Fighting Knife"],
      "armor": ["Kevlar-Weste Stufe II"],
      "gadgets": [
        "Multi-Tool Wraith",
        "Faseroptik-Kabelkamera",
        "Rauchgranate Mk I",
        "Micro-Breacher"
      ],
      "consumables": ["Med-Patch"],
      "special": ["Notfall-Transponder"]
    },
    "quarters": {
      "id": "QTR-A17",
      "preset": "custom",
      "layout_tags": ["cqb_ready", "urban_ghost", "analyst_cell"],
      "deck": "HQ-A",
      "notes": "Schallgedämmte CQB-Zelle mit Analysten-Setup"
    },
    "stats": {
      "missions_completed": 2,
      "deaths": 1,
      "rifts_closed": 0,
      "shots_fired": 2
    }
  },
  "team": {"members": [{"id": "AGENT-01", "callsign": "Nova"}]},
  "party": {"characters": [{"id": "AGENT-01", "callsign": "Nova"}]},
  "loadout": {
    "AGENT-01": {
      "primary": "CQB-Kampfpistole (SD)",
      "secondary": "Tactical Fighting Knife",
      "armor": "Kevlar-Weste Stufe II",
      "gear": [
        "Multi-Tool Wraith",
        "Faseroptik-Kabelkamera",
        "Rauchgranate Mk I",
        "Micro-Breacher",
        "Ersatzmagazin"
      ]
    }
  },
  "economy": {
    "cu": 1650,
    "wallets": {
      "AGENT-01": {"name": "Agent Nova", "balance": 1650}
    }
  },
  "logs": {
    "artifact_log": [],
    "market": [],
    "offline": [],
    "kodex": [],
    "alias_trace": [],
    "squad_radio": [],
    "hud": [],
    "psi": [],
    "foreshadow": [],
    "fr_interventions": [],
    "flags": {
      "runtime_version": "4.2.6",
      "compliance_shown_today": true,
      "chronopolis_warn_seen": false,
      "platform_action_contract": {
        "action_mode": "uncut",
        }
    },
    "field_notes": [
      {
        "agent_id": "AGENT-01",
        "mission": "Sydney 2000 - Maskottchen-Alarm",
        "timestamp": "2000-09-15T20:30:00Z",
        "note": "Kontaminationsalarm im Logistikbereich eingedämmt; Probenbestand gesichert."
      },
      {
        "agent_id": "AGENT-01",
        "mission": "Apollo 15 Abort Call",
        "timestamp": "1971-07-30T03:15:00Z",
        "note": "Saboteur in Tunnel S-03 gefesselt, Guidance-Daten korrigiert."
      }
    ]
  },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {
      "ITI": 0,
      "Ordo Mnemonika": 0,
      "Kausalklingen": 0
    },
    "timeline": [
      {
        "id": "TL-OLYMPICS-2000",
        "epoch": "2000",
        "label": "Kontaminationsalarm bei Olympia 2000 stabilisiert",
        "stability": 4
      },
      {
        "id": "TL-APOLLO15",
        "epoch": "1971",
        "label": "Apollo 15 Guidance stabilisiert",
        "stability": 2
      }
    ]
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": true,
    "suggest_mode": false,
    "action_mode": "uncut",
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
    "match_policy": "sim",
    "previous_mode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "tier": 1,
    "proc_budget": 0,
    "artifact_limit": 0,
    "loadout_budget": 0,
    "phase_strike_tax": 0,
    "damage_dampener": true,
    "team_size": 1,
    "fee": 0,
    "scenario": null,
    "started_episode": null,
    "last_reward_episode": null,
    "policy_players": [],
    "audit": []
  }
}
```

**Optionale strukturierte Talente:** Wer statt reiner Strings klarere Tool-
Hooks benötigt, kann Talente auch als Objekte speichern. Die einfache Liste
bleibt unterstützt; beide Formen können gemischt werden.

```json
"talents": [
  "Schleichprofi",
  {"name": "Pistolenschütze", "tag": "ranged", "bonus": 2},
  {"name": "Menschenkenntnis", "tag": "interrogation", "bonus": 2}
]
```

Die Felder `tag` und `bonus` sind optional, helfen aber beim automatischen
Routen zu passenden Proben.

**Timeline-Notizen:** `arc_dashboard.timeline[]` speichert bedeutende Einsätze
mit optionalen Angaben zu ID, Epoche und Label; die Liste ist unabhängig von
`campaign.px`. Die Runtime normalisiert Einträge auf Objekte mit
`{id, epoch, label}`, entfernt leere/ungültige Datensätze und setzt fehlende
Timeline-Listen automatisch auf `[]`.

**Mission 5/10 Auto-Reset (Self-Reflection-Beispiel)**

```json
{
  "logs": {
    "hud": ["SF-OFF (Mission 5)", "GATE 2/2", "SF-ON (post-M5 reset)"],
    "self_reflection_history": [
      {"mission_ref": "EP04-MS05", "reason": "mission5_end", "ts": "2025-11-26T22:10:00Z"},
      {"mission_ref": "EP04-MS10", "reason": "mission10_end", "ts": "2025-11-27T22:10:00Z"}
    ],
    "flags": {
      "foreshadow_gate_m5_seen": true,
      "self_reflection": true,
      "self_reflection_off": false,
      "self_reflection_auto_reset_at": "2025-11-26T22:10:00Z",
      "self_reflection_auto_reset_reason": "mission10_end",
      "self_reflection_last_change_reason": "mission10_end",
      "last_mission_end_reason": "aborted"
    }
  },
  "character": {"self_reflection": true},
"ui": {"suggest_mode": false, "action_mode": "uncut"}
}
```

Das Beispiel zeigt den automatischen Reset nach Mission 5 und 10: HUD-Badge `SF-OFF`
bleibt bis zur Rückkehr sichtbar, `self_reflection_auto_reset_*` dokumentiert
den Zeitpunkt und den Missionsausgang (`completed` oder `aborted`), die optionale
`self_reflection_history[]` hält jeden Reset chronologisch fest. Nach dem
Debrief ist der Charakterwert maßgeblich (`self_reflection=true`), Log-Flags
spiegeln diesen Zustand und weisen keine `self_reflection_off`-Reste mehr auf.

**Self-Reflection-Priorität & Helper**
- Runtime und HUD lesen ausschließlich `character.self_reflection`; Log-Flags
  spiegeln den Charakterwert, ersetzen ihn aber nie.
- `set_self_reflection(enabled:boolean, reason?: string)` ist die einzige
  Schnittstelle, die `character.self_reflection` und `logs.flags.self_reflection`
  synchron setzt, `self_reflection_changed_at/_reason` pflegt und auf Wunsch
  einen Eintrag an `logs.self_reflection_history[]` anhängt, damit Wiederholungen
  nachvollziehbar bleiben.
- Auto-Reset feuert nach Mission 5 **und 10** immer, egal ob Abschluss oder
  Abbruch, setzt sowohl HUD-Badge als auch Charakterwert auf `SF-ON` zurück und
  füllt deterministisch `self_reflection_auto_reset_*` plus History-Eintrag.

- Pflichtfelder: `character.id`, `character.attributes.SYS_max`,
  `character.attributes.SYS_installed`, `character.attributes.SYS_runtime`,
  `character.attributes.SYS_used`, `character.stress`, `character.psi_heat`,
  `character.cooldowns`, `campaign.px`, `economy` (inklusive `wallets{}`),
  `logs` (inklusive `hud`, `artifact_log`, `market`, `offline`, `kodex`,
  `alias_trace`, `squad_radio`, `foreshadow`, `fr_interventions`, `psi`,
  `flags`), `ui` und `arena`. Der Market-Trace hält maximal 24 Einträge und
  schneidet ältere automatisch ab.
- **Paradoxon-Index:** `campaign.px` ist die einzige Quelle für Px-Stand und
  Progression. Rifts erzeugen kein separates `rift_px`; Importpfade verwerfen
  abweichende Felder und mappen Legacy-Keys zurück auf `campaign.px`.
- Optionales Feld: `modes` - Liste aktivierter Erzählmodi.
- Im HQ sind `character.attributes.SYS_installed` und
  `character.attributes.SYS_max` deckungsgleich, `SYS_runtime` liegt höchstens
  bei der installierten Last, `stress = 0`, `psi_heat = 0`. Das Speichern
  erfasst diese Werte, damit GPT den Basiszustand prüfen kann. Die JSON-
  Beispiele in diesem Modul zeigen weiterhin volle SYS-Werte (5/5 bzw. 6/6)
  und erfüllen damit den Guard.
- GPT darf keine dieser Angaben ableiten oder weglassen. Der Serializer setzt
  fehlende Pflichtblöcke automatisch auf sichere Defaults (`economy.cu = 0`,
  leere Logs mit `logs.flags`, `ui.gm_style = "verbose"`).
- `party.characters[]` ist die kanonische Gruppenstruktur. Legacy-Saves mit
  `Charaktere` (DE) oder reinen Arrays werden beim Import auf diese Form
  normalisiert; Exporte und Debriefs verwenden ausschließlich die EN-Schreibweise
  (`party.characters[]`/`team.members[]`). Wrapper dienen nur als Import-Bridge -
  GPT erzeugt sie nie als Output.
- Die Load-Pipeline nutzt dafür explizit `migrate_save()` als Legacy-Bridge,
  bevor `load_deep()` Pflichtfelder validiert und Defaults ergänzt.
- Array-only-Gruppensaves (ohne Objektfelder) werden beim Laden auf
  `party.characters[]` gehoben; anschließend legt
  `initialize_wallets_from_roster()` automatisch Wallets für alle IDs an und
  meldet den Schritt im HUD ("Wallets initialisiert …"). `team.members[]`
  bleibt ausschließlich Migration und erscheint nicht in neuen Beispielblöcken.

### Cross-Mode Import - Solo → Koop/Arena {#cross-mode-import}

Cross-Mode-Sequenz (Solo → Koop → Arena → Debrief):
`load_save()` → `initialize_wallets_from_roster()` → `sync_primary_currency()` →
Arena-Gebühr über `arenaStart()` → Debrief `apply_wallet_split()`.

1. **Solo-Save laden.** `economy.wallets{}` ist zunächst leer; `party.characters[]`
   enthält nur den Protagonisten. Nach dem Laden läuft
   `initialize_wallets_from_roster()` automatisch und legt leere Wallets für alle
   aktiven Agent:innen an. Die Person, die den Save bereitstellt, ist der Host:
   Ihr Kampagnenblock (`episode`, `mission`, `mode`, `seed_source`,
   `rift_seeds[]`) gewinnt bei Konflikten den Vorrang; zusätzliche Crew-Saves
   dürfen nur Charaktere, Loadouts und Wallets beisteuern.
2. **Koop- oder Gruppeneinsatz starten.** Im Debrief erzeugt `apply_wallet_split()`
   für jedes Teammitglied eine Auszahlung und protokolliert den Vorgang als
   `Wallet-Split` in den HUD-Logs. `logs.arena_psi[]` dokumentiert parallel den
   zuvor aktiven Modus (`mode_previous`) für die Cross-Mode-Evidenz. Wallet-Werte
   stammen immer aus `economy.cu`/`wallets{}` - Credits nie per Hand direkt
   setzen. Jeder Abzug oder Zufluss aus Arena-Gebühren, Hazard-Pay, Wallet-Split
   oder Markt-Kauf erzeugt einen `currency_sync`-Trace mit Vorher-/Nachher-Wert
   und Delta.
3. **Arena aktivieren.** `arenaStart()` setzt `arena.policy_players[]`,
   `arena.previous_mode` und `arena.phase='active'`, markiert `location='ARENA'`
   und blockiert Save-Versuche bis zum Arena-Exit. Während der Serie blockiert
   der HQ-Save-Guard (`SaveGuard: Arena aktiv`). Beim Start zieht die Routine die
   Gebühr aus dem primären Economy-Feld und spiegelt sie via
   `sync_primary_currency()` auf `economy.cu` und `economy.credits`. Der
   Kampagnenmodus wird temporär auf `pvp` gesetzt, `campaign.previous_mode`
   sichert den alten Wert (`preserve`/`trigger`). Beim Exit schreibt die Runtime
   `arena.phase='completed'`, synchronisiert Px (+1 bei Sieg), stellt
  `campaign.mode = previous_mode` wieder her, leert `previous_mode` und erlaubt
  erneut HQ-Saves. `reset_arena_after_load()` bewahrt den letzten Modus über
  `arena.previous_mode` bzw. `resume_token.previous_mode`, setzt beim Laden den
  Kampagnenmodus zurück und hält `phase_strike_tax` auf 0, falls mitten in einer
  Serie geladen wird, damit der Exit konsistent auf den Ursprungsmodus
  zurückspringt.

**Host-Regel für Mehrfach-Import:** Sobald mehrere Saves zusammengeführt
werden, bleibt der Kampagnenblock des Hosts maßgeblich. Fremdsaves dürfen weder
`campaign.mode` noch `campaign.rift_seeds[]` oder Episoden-/Missionszähler
überschreiben. Der Merge-Pfad zieht lediglich Charaktere, Loadouts und Wallets
heran und protokolliert abweichende Seeds im HUD/Debrief. Jeder abweichende
Wert (Seeds, Episoden-/Missions-/Szenenzähler, Seed-Quelle, Arena- oder
Non-HQ-States) landet zusätzlich in `logs.flags.merge_conflicts[]` gemäß
Allowlist-Feldern (`rift_merge`, `phase_bridge`, `campaign_mode`,
`arena_resume`, `location_bridge`, `wallet`) und wird als Host-Wert
beibehalten. UI-Optionen werden weiterhin Host-seitig erzwungen, aber nicht als
Merge-Konflikt geloggt. `load_deep()` schreibt ergänzend ein `logs.trace[]`-Event
`merge_conflicts` mit Arena-Phase/Queue-State/Zone, Reset-/Resume-Markern,
`conflict_fields`, `conflicts_added` und Gesamtzähler sowie ein separates
`ui_host_override`-Event mit den überschriebenen UI/Accessibility-Schlüsseln.
Offene Rift-Seeds werden beim Merge auf 12 gedeckelt; überschüssige Seeds gehen
automatisch an ITI-NPC-Teams. Die Auswahl (kept vs. handoff) wird im Trace als
`merge_conflicts.rift_merge` samt `selection_rule` abgelegt. Der HQ-Pool
(`economy.cu`) bleibt stets
Host-priorisiert; Importwerte erzeugen nur einen Merge-Konflikt und werden
verworfen. Wallets werden **union-by-id** als Map `id → {name,balance}`
zusammengeführt: Host-Wallets haben Vorrang, neue IDs aus dem Import ergänzen
den Satz, abweichende Balances/Labels landen als Konflikt in
`logs.flags.merge_conflicts[]`. Der Merge schreibt parallel ein
`merge_conflicts`-Trace (Quelle/Ziel/kept/handoff), damit Host-Vorrang und
Rest-Verteilung pro Lauf nachvollziehbar bleiben.
Unmittelbar nach dem Hydratisieren synchronisiert `ensure_economy()` den
HQ-Pool (`economy.cu`) mit dem Credits-Fallback, bevor Wallets geöffnet oder
Arena-Guards scharfgeschaltet werden.

**Fahrzeug-Importregel (SSOT):** `vehicles` wird slotbasiert pro
`character.id` geführt. Pro Charakter ist genau ein HQ-Basisslot zulässig.
Bei Mehrfach-Importen gilt Host-Vorrang für kollidierende Fahrzeug-Slots;
abweichende Importwerte werden als `merge_conflicts` protokolliert. Das
missionsbezogene Einsatzfenster bleibt TEMP-gesteuert (Solo: Charakter-TEMP,
Gruppe: `ceil(sum(TEMP)/n)` über `party.characters[]`, Fallback
`team.members[]`). Einzig legendäre temporale Chronopolis-Schiffe
(Tech IV/temporale Klasse) können als explizite Ausnahme den Zeitriss
selbständig durchqueren; sie bleiben seltene Endgame-Artefakte und berühren
den Standard-Importpfad nicht. Falls vorhanden, werden sie als
`vehicles.faction_temporal_assets[]` geführt (Zusatzslot, Fraktionsaufsicht),
während der persönliche Charakter-Slot unverändert bleibt.

### Cross-Mode-Transfer-Matrix (Testrun 3, #003) {#cross-mode-transfer}

Die folgende Matrix regelt verbindlich, welche Daten bei einem Moduswechsel
übernommen, verworfen oder zusammengeführt werden.

#### Transferregeln pro Richtung

| Richtung | Übernommene Felder | Verworfene/Zurückgesetzte Felder | Besonderheiten |
| --- | --- | --- | --- |
| **Solo → Koop** | Host-Save bestimmt `campaign` komplett (episode, mission, mode, rift_seeds[], px). Gast-Saves liefern nur `character` + `loadout` + `economy.wallets{eigener}`. | Gast-`campaign`, Gast-`economy.cu`, Gast-`logs` (außer merge_conflicts) | Host-Kampagnenblock hat Vorrang. Gast-Wallets werden per Union-by-id ergänzt. |
| **Koop → Solo** | Spieler-Character extrahieren (`character`, `loadout`, `economy.wallets{eigener}`). | Alles andere: `campaign` wird auf Solo-Defaults zurückgesetzt, Team/Party auf Solo-Roster reduziert, `economy.cu` auf Solo-Default. | `campaign.mode` wechselt zurück auf den Ursprungsmodus des Spielers. |
| **Jeder Modus → PvP** | `arena.previous_mode = campaign.mode` speichern. Gesamter Spielstand bleibt erhalten, `campaign.mode` wechselt temporär auf `"pvp"`. | - | Nach Arena-Exit: `campaign.mode = arena.previous_mode`, dann `arena.previous_mode = null`. |
| **PvP → zurück** | `campaign.mode = arena.previous_mode` restaurieren. Arena-Rewards (CU, Px) werden verbucht. | `arena.previous_mode` wird auf `null` geleert. Arena-spezifische Laufzeitdaten zurücksetzen. | Fehlt `previous_mode` (Legacy), Fallback auf `"preserve"`. |

#### Merge-Konflikte bei Cross-Mode-Transfer

Bei **jedem** Cross-Mode-Transfer werden Konflikte im `merge_conflicts[]`-Array
dokumentiert. Jeder Eintrag enthält mindestens:

```json
{
  "field": "<allowlist-feld>",
  "host_value": "<Wert aus Host/Ziel-Modus>",
  "guest_value": "<Wert aus Quell-Modus>",
  "resolution": "<host_wins|guest_wins|merged|default>"
}
```

Die `field`-Werte folgen der bestehenden Allowlist: `wallet`, `rift_merge`,
`arena_resume`, `campaign_mode`, `phase_bridge`, `location_bridge`.

Zusätzlich erlaubte Felder für Cross-Mode-Transfers:
- `cross_mode_campaign` - für campaign-Block-Konflikte bei Solo↔Koop
- `cross_mode_economy` - für economy.cu-Differenzen
- `cross_mode_roster` - für party.characters[]-Divergenzen

#### Trace-Protokollierung

Jeder Cross-Mode-Transfer schreibt ein Event in `logs.trace[]`:

```json
{
  "event": "cross_mode_transfer",
  "at": "<ISO-Timestamp>",
  "from_mode": "<solo|coop|pvp>",
  "to_mode": "<solo|coop|pvp>",
  "host_id": "<character.id des Hosts>",
  "conflicts_count": 0,
  "conflict_fields": [],
  "location": "HQ",
  "phase": "core"
}
```

Der Trace stellt sicher, dass jeder Moduswechsel lückenlos nachvollziehbar ist
- sowohl für Debriefs als auch für QA-Prüfungen.

#### Solo-Defaults (Referenz für Koop→Solo)

Beim Rückfall auf Solo gelten folgende Defaults für den `campaign`-Block:
- `campaign.mode`: Ursprungsmodus des Spielers (aus Save oder Fallback `"preserve"`)
- `campaign.team_size`: `1`
- `party.characters[]`: nur der extrahierte Spieler-Character
- `team.members[]`: Spiegel von `party.characters[]`
- `economy.cu`: Spieler-Wallet-Balance (aus `economy.wallets{eigener}`)

### Accessibility-Preset (zweites Muster) {#accessibility-save}

```json
{
  "save_version": 6,
  "zr_version": "4.2.6",
  "location": "HQ",
  "phase": "core",
  "character": {
    "id": "CHR-7777",
    "name": "Jade",
    "rank": "Specialist",
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "attributes": {"SYS_max": 6, "SYS_installed": 6, "SYS_runtime": 6, "SYS_used": 6}
  },
  "campaign": {"episode": 12, "scene": 0, "px": 2},
  "team": {"members": []},
  "party": {"characters": []},
  "loadout": {},
  "economy": {"cu": 1200, "wallets": {"jade": {"balance": 1200, "name": "Jade"}}},
  "logs": {
    "artifact_log": [],
    "market": [],
    "offline": [],
    "kodex": [],
    "alias_trace": [],
    "squad_radio": [],
    "hud": [],
    "psi": [],
    "foreshadow": [],
    "fr_interventions": [],
    "flags": {
      "runtime_version": "4.2.6",
      "compliance_shown_today": true,
      "chronopolis_warn_seen": true,
      "offline_help_count": 1,
      "offline_help_last_scene": "HQ:4",
      "offline_help_last": "HQ:4",
      "platform_action_contract": {
        "action_mode": "uncut",
        }
    }
  },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {},
    "fragen": [],
    "timeline": []
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": true,
    "suggest_mode": false,
    "action_mode": "uncut",
    "contrast": "high",
    "badge_density": "compact",
    "output_pace": "slow",
    "voice_profile": "gm_third_person"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
    "match_policy": "sim",
    "previous_mode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "tier": 1,
    "proc_budget": 0,
    "artifact_limit": 0,
    "loadout_budget": 0,
    "phase_strike_tax": 0,
    "damage_dampener": true,
    "team_size": 1,
    "fee": 0,
    "scenario": null,
    "started_episode": null,
    "last_reward_episode": null,
    "policy_players": [],
    "audit": []
  }
}
```

_Snippet gekürzt: Fokus auf UI-Persistenz (`contrast`, `badge_density`,
`output_pace`); vollständige Pflichtcontainer siehe Vollsave unten._

Das Preset illustriert, wie ein `!accessibility`-Dialog persistiert wird: Der
Kontrast steht auf `high`, Badges nutzen das kompakte Layout und der Output
läuft im `slow`-Takt. Diese Werte bleiben erhalten, bis Nutzer:innen sie im HQ
zurücksetzen. HQ-Deepsaves normalisieren den kompletten UI-Block (`gm_style`/
`intro_seen`/`suggest_mode`/`action_mode` plus `contrast`/`badge_density`/
`output_pace`); fehlen Felder, ergänzen Migration und Serializer Defaults
(`standard|normal` plus `action_mode=uncut`), sodass der SaveGuard den
normalisierten Block akzeptiert.
Der Serializer mappt die Optionen 1:1 auf JSON:

- **Kontrast:** `contrast = standard|high`
- **Badge-Dichte:** `badge_density = standard|dense|compact`
- **Ausgabetempo:** `output_pace = normal|fast|slow`

Legacy-Felder (`contrast`, `badge_density`, `output_pace`, `ui_contrast`,
`ui_badges`, `ui_pace`, `badges`, `pace`) landen beim Laden automatisch im
`ui`-Block. Acceptance 14/15 prüft den Roundtrip und vergleicht die geladenen
UI-Werte gegen den gespeicherten Block.

Jede Bestätigung erzeugt den Toast "Accessibility aktualisiert …" und schreibt
die Auswahl in `ui {}`. Legacy-Werte `full|minimal` werden beim Laden auf
`standard|compact` gemappt; `rapid|quick` landen auf `fast`, `default|steady` auf
`normal`. Saves ohne Badge-Feld setzen automatisch auf `standard`.

## Laden & HQ-Rückkehr {#load-flow}

### Ablauf nach `!load`

1. **Save posten.** `!load` erwartet den HQ-Deepsave als JSON und quittiert die
   Eingabe mit "Kodex: Poste Speicherstand als JSON."
2. **Deserializer starten.** Das hier dokumentierte `load_deep()`-Schema
   migriert Legacy-Felder in die v6-Struktur, prüft Pflichtblöcke und setzt
   `state.location='HQ'`. Die lokale `runtime.js` im Test-Container spiegelt
   diesen Pfad, gehört aber **nicht** zum Wissensspeicher.
3. **UI-Felder restaurieren.** Beim Laden werden `ui.suggest_mode`,
   `ui.contrast`, `ui.badge_density` und `ui.output_pace` **IMMER** aus dem
   Save restauriert - kein Fallback auf Defaults. Die gespeicherten Werte
   überschreiben den Laufzeitzustand 1:1. Fehlen diese Felder in einem
   älteren Save (pre-v6 oder Legacy), greift der Normalizer und setzt
   Defaults ein: `suggest_mode: false`, `contrast: "standard"`,
   `badge_density: "standard"`, `output_pace: "normal"`. Diese Defaults
   gelten **nur** für fehlende Felder in alten Saves, niemals als Fallback
   für vorhandene Werte.
   **Ask→Suggest-Reaktivierung (Pflicht):** Wenn `ui.suggest_mode = true` im
   geladenen Save steht, MUSS die Spielleitung nach dem Laden den Suggest-Modus
   aktiv schalten: `toggle_suggest(true)` aufrufen, HUD-Tag `· SUG` ins Overlay
   setzen und den Toast "Suggest-Modus aktiv" anzeigen. Der Toolkit-Init darf
   einen im Save gespeicherten `suggest_mode: true` Wert NICHT auf `false`
   zurücksetzen. Reihenfolge: Save lesen → UI-Felder setzen → Toolkit-Init
   prüft ob `suggest_mode` bereits aus dem Save stammt → wenn ja, beibehalten.
4. **Rückblende & HUD.** `scene_overlay()` erscheint nur in Missionen/Rifts; im
   HQ (inklusive Charaktererstellung) und in der Arena bleibt der Szenenzähler
   aus. Die Runde springt ohne Nachfrage direkt zum HQ- beziehungsweise
   Briefing-Einstieg.
5. **Compliance-Hinweis entfällt.** Loads laufen ohne Compliance-Toast oder
   Flag-Setzung; `ShowComplianceOnce()` bleibt nur als leerer
   Kompatibilitäts-Hook bestehen.

{# LINT:FS_RESET_OK #}

> **Laufzeitabgleich:** Dieses Modul ist maßgeblich für GPT-basierte
> Spielleitungen. Die beigelegte `runtime.js` dient nur als Test-Spiegel für
> lokale Runs und wird nicht in produktive Wissensspeicher geladen.

**Multi-Save-Import (Gruppenschnellstart):** Werden vor einem neuen Briefing
mehrere HQ-Saves gleichzeitig gepostet (`Spiel starten (gruppe schnell)`), gilt
der **zuerst gepostete Save als Host**. Sein Kampagnenblock (`episode`,
`mission`, `mode`, `seed_source`, `rift_seeds[]`, `px`) gewinnt bei Konflikten;
weitere Saves liefern ausschließlich Charaktere, Loadouts und Wallets.
Abweichende Seeds, Episoden- oder Missionszähler landen in
`logs.flags.merge_conflicts[]` und werden als Host-Wert beibehalten. Der HQ-
Pool (`economy.cu`) bleibt Host-priorisiert; Import-Wallets ergänzen per
Union-by-id.

**Mid-Session-Merge:** Für laufende Einsätze nutzt GPT statt `load_deep()` einen
leichten Merge-Pfad: Die Save-Blöcke werden ohne Location-Reset nach
`party.characters[]` kopiert, Wallets normalisiert und HUD/Timer beibehalten.
So können neue Agent:innen aufschlagen, während `state.location` auf Mission
steht; gespeichert wird trotzdem erst wieder im HQ.

### Kompatibilität & Guards

- Semver-Toleranz: Lädt, wenn `major.minor` der gespeicherten `zr_version` dem
  aktuellen `ZR_VERSION` entspricht; Patch-Level sind egal.
- Version-Mismatch liefert `Kodex-Archiv: Datensatz vX.Y nicht kompatibel mit
  vA.B. Bitte HQ-Migration veranlassen.`
- `campaign.exfil.active` oder `state.exfil.active` blockieren den HQ-Save mit
  "SaveGuard: Exfil aktiv - HQ-Save gesperrt."
- Pflichtblöcke dürfen nicht geschätzt werden; der Serializer ersetzt fehlende
  Strukturen mit sicheren Defaults (Wallets `{}`, Logs als leere Arrays,
  `ui.gm_style="verbose"`).
- Story-Beispiel für den HQ-Guard: Abbruch kurz vor Mission 5-Boss → HUD meldet
  `BOSS`+`GATE 2/2`, Debrief schreibt `last_mission_end_reason=aborted`,
  Self-Reflection springt automatisch auf `SF-ON` und der Save bleibt bis zur
  Rückkehr ins HQ gesperrt.

### Persistente Debrief-Spiegel

- **Runtime-Flags.** `logs.flags.runtime_version` hält die erzeugende Version
  fest. Der Debrief bündelt sie unter `Runtime-Flags: …` inklusive
  Chronopolis-Warnung sowie Offline-Hilfe-Zähler plus
  Szene-Marker (`offline_help_last_scene`). Legacy-Felder `offline_help_last`
  werden beim Laden auf `offline_help_last_scene` gespiegelt.
- **Chronopolis & Markt.** `log_market_purchase()` schreibt Einkäufe nach
  `logs.market[]` (ISO-Timestamp, Artikel, Kosten, Px-Klausel).
  `render_market_trace()` erzeugt `Chronopolis-Trace (n×): …`.
  `chronopolis_warn_seen` bleibt beim Laden gesetzt und sorgt dafür, dass die
  City-Warnblende nur einmal auftaucht - auch nach Pre-City-Warncuts. Der
  Chronopolis-Schlüssel schaltet ab Level 10 frei: Der Serializer hält das
  erwartete Level unter `logs.flags.chronopolis_unlock_level=10`, markiert den
  Übergang mit `chronopolis_unlocked=true` und schreibt beim ersten Erreichen
  ein Trace-Event `chronopolis_unlock` (Quelle + Level). Der HUD-Toast
  "Chronopolis-Schlüssel aktiv - Level 10+ erreicht." dient als sichtbarer
  Hinweis im HUD. Beim Laden zieht die Runtime fehlende Flags nach (Level oder
  Key-Item) und liefert Trace/Toast nach, falls das Unlock bislang fehlte.
- **Offline & Foreshadow.** `sanitize_offline_entries()` begrenzt
  `logs.offline[]` auf zwölf Einträge (Trigger, Gerät, Jammer, Reichweite,
  Relais, Szene/Episode). `render_offline_protocol()` fasst sie als
  `Offline-Protokoll (n×): …` zusammen. `normalize_save_v6()` dedupliziert
  `logs.foreshadow[]` (Tag, Kurztext, Szene, First/Last-Seen); Debriefs spiegeln
  `Foreshadow-Log (n×): …`.
- **Fraktionen & Funk.** `log_intervention()` protokolliert bis zu 16
  `logs.fr_interventions[]` (Ergebnis, Fraktion, Szene, Mission, Zusatzfelder)
  und spiegelt sie ins Arc-Dashboard; `render_alias_trace_summary()` fasst
  `logs.alias_trace[]` zu `Alias-Trace (n×): …` zusammen. Funkmeldungen landen
  via `log_squad_radio()` in `logs.squad_radio[]`; der Debrief liefert
  `Squad-Radio (n×): …`.
- **HQ-Rituale.** `campaign.hq_moments_used: string[]` dokumentiert Buffs
  (FOCUS/BASTION/SPARK/CALM/PULSE). Fehlt das Feld, setzt der Serializer `[]`;
  Debriefs nennen "HQ-Moments (n×)" entsprechend. HUD-Logs übernehmen das
  jeweils gültige `hud_tag` (z. B. `HQ:CALM · Psi +1 (Mission)` bei CALM) und
  spiegeln so den aktiven Effekt.
- **Arena & Psi.** `ensure_arena()` konserviert PvP-Status, Phasen,
  Serienstände, Budget-Limits sowie `phase_strike_tax`. Sobald
  `phase_strike_cost()` greift, ruft die Runtime `log_phase_strike_event()`
  auf und legt in `logs.arena_psi[]` strukturierte Einträge mit
  `ability='phase_strike'`, `base_cost`, `tax`, `total_cost`, `mode`,
  `arena_active` und `category='arena_phase_strike'` an; optional ergänzt der
  Logger `mode_previous`, `location`, `gm_style` und `reason`.
  `prepare_save_logs()`/`sanitize_arena_psi_entries()` halten dieses Schema
  stabil und entkoppeln Arena-Psi-Logs von `logs.psi[]` (Psi-Heat/Story).
- **Psi-Heat-Trace.** `log_psi_event()` bündelt `psi_heat_inc` pro Konflikt
  (Trigger-Liste, Szene/Mission) und schreibt HQ-Transfers als
  `psi_heat_reset` mit Trigger (`hq_transfer`) in `logs.psi[]`. `reset_psi_heat()`
  leert Charakter- und Team-Psi-Heat beim Debrief, die Runtime-Flags führen
  die Aggregation fort.
- **Arena-Mode-State-Machine (`campaign.mode`):**
  1. **Start:** `arenaStart()` merkt `campaign.previous_mode = campaign.mode`,
     setzt `campaign.mode = 'pvp'`.
  2. **Exit:** `arenaEnd()` stellt `campaign.mode = previous_mode` wieder her,
     leert `previous_mode = null`.
  3. **Load während Arena:** `reset_arena_after_load()` nutzt
     `arena.previous_mode` / `resume_token.previous_mode`, setzt
     `campaign.mode` auf den Ursprungswert zurück. Fehlt `previous_mode`,
     fällt der Reset auf `'preserve'` zurück.
  Arena ist **kein** dauerhaft eigener Kampagnenmodus - PvP gilt nur temporär.
- **Arena-Reset nach Load.** `load_deep()` setzt `location='HQ'`,
  deaktiviert aktive Arena-Flags und kippt die Phase auf `completed` (falls ein
  Run lief) oder `idle`. Der Reset wird explizit genannt ("Arena-Zustand auf HQ
  zurückgesetzt."); die letzte Runde bleibt über `arena.previous_mode`
  nachvollziehbar. Lief die Serie noch, erzeugt die Runtime ein
  `arena.resume_token` (Tier, Teamgröße, Modus, `match_policy`, Szenario, `previous_mode`),
  das `!arena resume` im HQ ohne erneute Gebühr reaktiviert.
- **Wallets.** `initialize_wallets_from_roster()` erzeugt fehlende Einträge in
  `economy.wallets{}` (Toast "Wallets initialisiert (n×)"). Saves führen immer
  ein Objekt - ggf. `{}`. Beim Laden bleiben Host-Wallets maßgeblich, Import-
  Wallets werden als Union-by-id angehängt; abweichende Beträge landen in
  `logs.flags.merge_conflicts[]` und im Trace `merge_conflicts`. Alle Wallets
  folgen dem Schema `id → {balance, name}`. Fehlende Namen ergänzt der
  Serializer zuerst aus dem Import-Record, andernfalls aus
  `team.members[]`/`party.characters[]`, damit Labels in Debrief und Import
  übereinstimmen, während die Host-Balance Vorrang behält.
- **Self-Reflection.** `logs.flags` ergänzt Gate- und Reset-Felder
  (`foreshadow_gate_m5_seen`, `self_reflection_auto_reset_at`,
  `self_reflection_last_change_reason` usw.) für nachvollziehbare Debrief-Logs.

## HQ-Loop-Contract (Debrief → Freeplay)

Nach jedem Einsatz folgt ein deterministischer HQ-Loop. Diese Reihenfolge ist
verpflichtend und wird im Debrief sichtbar dokumentiert:

1. **Auto-Loot** (Loot/Artefakte/Relikte automatisch zählen & loggen).
2. **CU & Wallet-Split** (HQ-Pool aktualisieren, Wallets verteilen).
3. **XP/Skills** (Level-Up/Skill-Picks aktiv abfragen).
4. **Freeplay-Anker** - explizites Menü mit **Bar**, **Werkstatt**, **Archiv**
   plus **1 Gerücht** (kurzer Hook) anbieten.

Optional für QA: `logs.flags.hq_freeplay_prompted=true` setzen, sobald Schritt 4
gespielt wurde.

### Gruppenregel bei Todesfällen (Core/Rift/Chronopolis)

Im Modus `gruppe` wird bei einem Spieler-Tod die Szene sofort gestoppt. Kodex
stellt dann verbindlich eine Gruppenentscheidung:

1. **Tod bleibt Kanon.** Die Geschichte läuft mit dem Verlust weiter; Debrief
   und Logs markieren den Tod als narrative Konsequenz.
2. **Neu laden.** Die Gruppe öffnet ein neues Chatfenster, lädt den letzten
   **Gruppen-DeepSave** und startet den Einsatz erneut.

Diese Abfrage gilt identisch in Core-, Rift- und Chronopolis-Einsätzen.
Chronopolis besitzt dabei **keinen** Sonder-Respawn und keinen Traum-Reset.

## Koop-Debrief & Wallet-Split {#koop-wallet-split}

Nach jeder Mission folgt auf den Belohnungsblock automatisch der Koop-Abschnitt.
`apply_wallet_split()` spiegelt das Ergebnis in `economy.wallets{}` und erzeugt
die Debrief-Zeilen.

### Hazard-Pay & HQ-Pool

- Enthält `outcome` ein `hazard_pay`-Feld (oder `economy.hazard_pay`), bucht die
  Runtime den Betrag zuerst auf `economy.cu` und loggt `Hazard-Pay: … CU
  priorisiert`.
- Anschließend meldet `apply_wallet_split()` den HQ-Stand als
  `HQ-Pool: <Betrag> CU verfügbar`. Restbeträge erscheinen in Klammern
  (`Rest 150 CU im HQ-Pool`).
- Reihenfolge und Restsummen bleiben deterministisch: Die Debrief-Zeile
  `Wallet-Split (n×)` listet IDs in Roster-Reihenfolge, verteilt Rundungsreste
  gleichmäßig von oben nach unten und schließt mit einem einzigen Hinweis auf
  den verbleibenden HQ-Pool (`Rest … CU im HQ-Pool`).

### Standard- und Sonderaufteilungen

1. **Standardaufteilung.** Ohne Vorgaben verteilt der GPT die Auszahlung
   gleichmäßig (`Wallet-Split (n×): Ghost +200 CU | …`).
2. **Solo→Koop.** Beim Moduswechsel initialisiert
   `initialize_wallets_from_roster()` leere Wallets für alle `party.characters[]`
   und verschiebt Solo-Guthaben in den HQ-Pool.
3. **Spezialschemata.** Sonderregeln kommen über `economy.split`/`wallet_split`.
   Prozentwerte (`percent`, `percent_share`) nutzt GPT als 0-1 bzw. 0-100 %.
   Verhältnisangaben (`ratio`, `weight`, `share_ratio`, `portion`) bleiben
   relative Anteile. Nicht zugewiesene CU verbleiben im HQ-Pool.
4. **Dialogführung.** Kodex nennt Standard und Alternativen (_"Standardaufteilung
   je 200 CU …"_) und dokumentiert Entscheidungen in Debrief oder
   Einsatzprotokoll.

### Persistenz & IDs

- `economy.wallets{}` speichert Balances anhand der IDs aus
  `party.characters[]`. Fehlt eine ID, erzeugt GPT einen Slug (`agent-nova`).
- Änderungen an Callsigns aktualisieren nur den Anzeigenamen; das Guthaben bleibt
  über die ID erhalten.
- Ohne lokale Runtime müssen GPT-Leitungen dieselben Schritte manuell
  beschreiben und die Werte in den Saveblock übertragen, damit Koop-Teams ihre
  CU-Historie nachvollziehen können.

**Legacy-Normalisierung (ohne runtime.js)**

- Encounter mit Alt-Saves laufen vollständig im LLM - es gibt keine
  JavaScript-Hooks im Produktivbetrieb. Deshalb erstellt die Spielleitung bei
  Legacy-Daten den `character{}`-Block manuell, bevor irgendetwas geladen oder
  geprüft wird:
  1. Alle vorhandenen Stammdaten (`id`, `name`, `rank`, `callsign`, `lvl`, `xp`)
     aus Root-Feldern in `character{}` kopieren und anschließend die
     Wurzelkopien löschen.
  2. `stress`, `psi_heat`, `psi_heat_max` und `cooldowns{}` ebenso in den
     `character`-Block übernehmen; `cooldowns{}` immer als Objekt führen.
  3. `character.attributes{SYS_max,SYS_installed,SYS_runtime,SYS_used}` aus
     `sys`/`sys_max`, `sys_installed`, `sys_runtime` bzw. `sys_used` bilden und
     dabei bestehende Werte aus `attributes{}` nur ergänzen - niemals
     überschreiben. Fehlt `SYS_installed`, setze es auf `SYS_used` oder den
     Maximalwert; `SYS_runtime` darf höchstens die installierte Last tragen.
  4. Wenn ein Legacy-Save `modes[]` oder `self_reflection` direkt an der
     Wurzel notiert hatte, landen sie jetzt ebenfalls in `character{}`.
- Abschließend kontrollierst du die Standard-Flags: **Psi-Puffer** gehören bei allen
  Agent:innen zur Grundausstattung. Fehlt `psi_buffer` in `character{}`, `team{}`
  oder `party.characters[]`, ergänze `true`.
- Danach verhält sich der Save wie ein natives v6-Dokument. Guards wie der
  HQ-Serializer, Log-Sanitizer und das Semver-Gate operieren erst auf dieser
  bereinigten Struktur.

Beim Laden sorgt `normalize_save_v6()` selbst für den Sync: `ui.suggest_mode`
und `character.modes` werden vereinigt, `suggest`-Einträge landen in beiden
Blöcken und das HUD-Tag `· SUG` erscheint deterministisch. Andere Modi
(`klassik`, `mission_focus`, `transparenz` usw.) bleiben wie gewohnt erhalten.

**Save-Beispiel mit `modes` inkl. `suggest`**

```json
{
  "ui": {"suggest_mode": true, "gm_style": "verbose", "action_mode": "uncut"},
  "character": {"modes": ["klassik", "mission_focus", "covert_ops_technoir", "suggest"]},
  "logs": {"hud": ["· SUG", "Mission-Fokus"]}
}
```

Der Save hält sowohl die aktivierten Erzählmodi (`modes[]`) als auch den UI-Flag
`suggest_mode` und den Action-Contract. Beim Laden setzt GPT `modus suggest`
und spiegelt das HUD-Tag `· SUG` samt Mission-Fokus-Badge.

Das UI speichert außerdem `dice.debug_rolls` (Default `true` für offene Würfel).
Neue Sessions starten dadurch automatisch mit sichtbaren Würfen, bis ihr per
`/roll hidden|manual` umschaltet.

## Session-Suspend (Temporärer Snapshot) {#session-suspend}

> **Ziel:** Ihr könnt eine laufende Sitzung pausieren, ohne den HQ-Deepsave zu verletzen.
> `!suspend` schreibt einen flüchtigen Snapshot, `!resume` setzt ihn exakt einmal fort.

Der Suspend-Snapshot friert den laufenden Einsatz für eine Pause ein.
Er lebt außerhalb der regulären Save-Pipeline und verfällt nach 24 Stunden.
Der Deepsave im HQ bleibt weiterhin Pflicht, sobald Ihr die Episode wirklich abschließt.

**SuspendGuard (Pseudocode)**
```pseudo
assert not state.get('open_roll'), "Suspend nur zwischen Szenen oder nach einem Wurf-Ergebnis."
assert not state.get('exfil_active'), "Suspend blockiert während laufender Exfiltration."
snapshot = {
  "suspend_version": 1,
  "zr_version": state.get('zr_version'),
  "created_at": now(),
  "expires_at": now() + 24h,
  "volatile": true,
  "campaign": {
    "episode": state.campaign.episode,
    "scene": state.campaign.scene,
    "phase": state.campaign.phase
  },
  "mission": {
    "id": state.mission.id,
    "objective": state.mission.objective,
    "clock": state.mission.clock,
    "timers": state.mission.timers
  },
  "team": {
    "stress": state.team.stress,
    "psi_heat": state.team.psi_heat,
    "status": state.team.status,
    "cooldowns": state.team.cooldowns
  },
  "initiative": {
    "order": state.initiative.order,
    "active_id": state.initiative.active_id
  },
  "hud": {
    "timers": state.hud.timers
  },
  "flags": state.flags.runtime
}
write_tmp("suspend/" + state.campaign.id + ".json", snapshot)
toast("Suspend-Snapshot aktiv. Nutzt !resume, bevor 24h vergehen.")
state.flags.runtime["suspend_active"] = true
```

Der Snapshot speichert nur die taktisch relevanten Werte einer Szene.
Inventar, Shop-Angebote und Episoden-Belohnungen bleiben Teil des HQ-Deepsaves.
`volatile: true` stellt klar, dass der Snapshot nicht als vollwertiger Save gilt.

**ResumeFlow (Pseudocode)**
```pseudo
snapshot = read_tmp("suspend/" + state.campaign.id + ".json")
assert snapshot, "Kein Suspend-Snapshot gefunden."
assert now() < snapshot.expires_at, "Suspend-Snapshot abgelaufen. Bitte letzten HQ-Save laden."
assert snapshot.zr_version.major_minor == state.zr_version.major_minor,
       "Suspend-Version inkompatibel."
apply(state.campaign.scene = snapshot.campaign.scene)
apply(state.campaign.phase = snapshot.campaign.phase)
apply(state.mission.clock = snapshot.mission.clock)
apply(state.mission.timers = snapshot.mission.timers)
apply(state.team.stress = snapshot.team.stress)
apply(state.team.psi_heat = snapshot.team.psi_heat)
apply(state.team.status = snapshot.team.status)
apply(state.team.cooldowns = snapshot.team.cooldowns)
apply(state.initiative.order = snapshot.initiative.order)
apply(state.initiative.active_id = snapshot.initiative.active_id)
apply(state.hud.timers = snapshot.hud.timers)
state.flags.runtime.update(snapshot.flags)
delete_tmp("suspend/" + state.campaign.id + ".json")
toast("Suspend-Snapshot geladen. Fahrt an Szene " + state.campaign.scene + " fort.")
```

- `!resume` ist nur einmal pro Snapshot erlaubt; der Datensatz wird nach dem Laden gelöscht.
- Nach der Rückkehr ins HQ erwartet Euch weiterhin `!save`, damit Episoden-Belohnungen
  gesichert bleiben.
- Bei Ablauf des Snapshots informiert das HUD: "Suspend-Fenster verstrichen. Bitte
  HQ-Deepsave laden."
- Der Snapshot konserviert Initiative-Reihenfolge und HUD-Timer, damit Konfliktszenen
  nach `!resume` lückenlos weiterlaufen.

**HUD-Feedback**

- Nach `!suspend`: Toast `HUD → Session eingefroren · Ablauf <24h`.
- Nach `!resume`: Overlay `Session fortgesetzt · Szene X/Y`.
- Nach Ablauf: Benachrichtigung `Suspend verworfen · HQ-Save nötig`.

**Best Practices**

- Nutzt `!suspend`, wenn Ihr mitten im Konflikt aufhören müsst, aber den Flow bewahren wollt.
- Legt direkt vor einer Pause eine Mini-Rekap an, damit `!resume` den Einstieg
  filmisch anschließen kann.
- Verlasst Euch nicht dauerhaft darauf: Der Snapshot ersetzt keinen Story-Fortschritts-Save im HQ.
## Makros im Überblick {#makros-im-ueberblick}

- `StartMission(total=12|14, type="core"|"rift")` - initiiert den Missionsfluss nach dem Load.
- `DelayConflict(4)` - verschiebt Konfliktszenen bis zur vierten Szene.
- `ShowComplianceOnce()` - bleibt als leerer Kompatibilitäts-Hook bestehen und
  setzt keine Flags mehr. `SkipEntryChoice()` markiert parallel
  `flags.runtime.skip_entry_choice=true`; die Runtime übernimmt das Flag
  unverändert in den Einsatz.
- `Chronopolis-Warnung` - `start_chronopolis()` blendet das einmalige Warn-Popup
  ein und setzt `logs.flags.chronopolis_warn_seen=true`, damit die Sequenz nach
  dem ersten Besuch stumm bleibt.
- `ClusterCreate()` - legt bei Paradoxon 5 neue Rift-Seeds an.
- `ClusterDashboard()` - zeigt aktive Seeds mit Schweregrad und optionaler Deadline.
- `launch_rift(id)` - startet eine Rift-Mission aus einem Seed (nur nach Episodenende).
- `resolve_rifts(ids)` - markiert Seeds als geschlossen und passt Belohnungen an.
- `seed_to_hook(id)` - liefert drei Kurz-Hooks als Einsprungpunkte für die nächste Sitzung.

### Paradoxon-Index & Rift-Seeds (Kernlogik) {#paradoxon-index}

- Der Paradoxon-Index misst die temporale Resonanz der Zelle — ein
  **Belohnungssystem** mit deterministischer Progression.

**Px-Anstieg (fix gekoppelt an TEMP):**

| TEMP | Px pro erfolgreicher Mission |
|-----:|:-----------------------------|
| 1–2 | +1 Px |
| 3–5 | +2 Px |
| 6–8 | +3 Px |
| 9–11 | +4 Px |
| 12–14 | +5 Px |

Der Scope ist modusabhängig und nutzt immer `campaign.px` als Quelle:
- **solo / npc-team:** Der Px-Wert gehört zum jeweiligen Run.
- **gruppe:** Der Px-Wert ist kampagnenweit gemeinsam und folgt dem Host-Save.

Nur erfolgreich abgeschlossene Missionen zählen. Fehlschläge oder Eskalationen
lösen im Default **keinen** automatischen Px-Abzug aus; Konsequenzen laufen über
Stress, Heat, Ressourcen und Storydruck.

- Bei Stufe 5 löst `ClusterCreate()` 1–2 neue Rift-Seeds aus, normalisiert den
  Pool (auch beim Laden) als Objekt-Liste und markiert den Px-Reset als
  „anhängig" (`px_reset_pending=true`, `px_reset_confirm=false`). Das Trace
  `cluster_create` hält px_before/after, `seed_ids`, Episode/Mission/Scene/Loc +
  `campaign_type` sowie die aktuelle Anzahl offener Seeds fest.
- Rift-Seeds sind erst nach Episodenende spielbar.
- Nach der Rift-Phase setzt der Debrief im HQ den Index auf 0, schreibt ein
  `logs.trace[]`-Event (`px_reset`) und bestätigt den Reset via
  `px_reset_confirm=true` und HUD-Toast „Px Reset → 0", sobald die Crew im HQ
  ankommt.

**Px-Effekte:**

- **Px 0–4:** Keine Maluswerte. HUD zeigt den aktuellen Balken kontextsensitiv
  und nutzt `campaign.px` als einzige Quelle.
- **Px 5:** `ClusterCreate()` erzeugt 1–2 Seeds, markiert den Reset als
  ausstehend. HUD/Debrief notieren „Paradoxon-Index 5 erreicht – neue Rifts
  sichtbar". Nach der Rift-Op springt der Wert auf 0 und der Reset-Toast
  bestätigt dies.

Jeder weitere Px‑5‑Treffer **stapelt** Seeds im Pool – ein Limit existiert nicht.
`apply_rift_mods_next_episode()` liest ausschließlich **offene** Seeds aus und
setzt `sg_bonus = min(3; offene Seeds)` sowie
`cu_multi = min(1,6; 1 + 0,2 × offene Seeds)`, damit der Pool gezielt als
Schwellen- oder Loot-Hebel genutzt werden kann.

Zwischen-Werte (Px 1–4) liefern keine mechanischen Boni — der Px ist eine
Fortschrittsanzeige mit Payoff bei Px 5 (ClusterCreate). HUD-Farbe und
Score-Screen zeigen den Fortschritt.

Toolkit, Runtime und Spieler-Handbuch referenzieren ausschließlich diese
Tabelle; Legacy-Varianten (Arc-spezifische Px, Zwischen-Stufen-Boni,
zusätzliche Stresswürfe) gelten als verworfen und werden beim Laden ignoriert.

### Legacy-Kompatibilität (Gear-Labels)

> Hinweis für die Spielleitung: Gear-Bezeichnungen bleiben beim Laden erhalten.
> Es gibt keine automatische Normalisierung oder erzwungene Umbenennung.
> Loadouts bleiben 1:1 erhalten; Namensabweichungen deuten auf einen
> fehlerhaften Normalizer hin.

### Immersiver Ladevorgang (In-World-Protokoll) {#immersives-laden}

- Kollektive Ansprache im Gruppenmodus ("Rückkehrprotokoll für Agententeam …").
- Synchronisierungs-Hinweis ("Kodex synchronisiert Einsatzdaten aller Teammitglieder …").
- Kurze Rückblende der letzten Ereignisse aus Sicht der Beteiligten.
- Individuelle Logbucheinträge sind erlaubt (ein Satz pro Char).

> **Kodex-Archiv** - Rückkehrprotokoll aktiviert.
> Synchronisiere Einsatzdaten: **Alex** (Lvl 3), **Mia** (Lvl 2).
> Letzte Einsätze konsolidiert. Paradoxon-Index: █░░░░ (1/5).
> Willkommen im HQ. Befehle? (Briefing, Shop, Training, Speichern)

### Abweichende oder fehlerhafte Stände (In-World-Behandlung)

- Leichte Formatfehler: als Kodex-Anomalie melden und in-world nachfragen.
- Inkonsistenzen: als Anomalie melden und einen Vorschlag zur Bereinigung anbieten.
- Unbekannte oder veraltete Felder: still ignorieren oder als Archivnotiz kennzeichnen.
- Semver-Mismatch: "Kodex-Archiv: Datensatz vX.Y nicht kompatibel mit vA.B. Bitte
  HQ-Migration veranlassen."
- Ambige Saves: "Kodex-Archiv: Profilpluralität erkannt. Sollen *Einzelprofil*
  oder *Teamprofil* geladen werden?"

### Kanonisches DeepSave-Schema (Kurzfassung)

```json
{
  "zr_version": "4.2.6",
  "save_version": 6,
  "location": "HQ",
  "phase": "core",
  "campaign": {
    "episode": 1,
    "mission_in_episode": 2,
    "scene": 0,
    "px": 1,
    "fr_bias": "normal"
  },
  "character": {
    "id": "CHR-0001",
    "name": "Agent Name",
    "level": 3,
    "attributes": {
      "STR": 5,
      "GES": 10,
      "INT": 4,
      "CHA": 4,
      "TEMP": 2,
      "SYS_max": 4,
      "SYS_installed": 4,
      "SYS_runtime": 4,
      "SYS_used": 4
    },
    "talents": ["Scharfschütze II", "Soldat I"],
    "bioware": ["Reflexverstärkung", "Muskelstärkung", "Stealth-Skin", "Adrenalin-Drüse"],
    "synergy": "Adaptive Ligament",
    "equipment": {
      "primary": "Resonanz-Sniper (SD)",
      "secondary": "Sidearm (SD)",
      "armor": ["Kevlar", "Helm 360°"],
      "gadgets": ["Medikit", "Nano-Bindepflaster"]
    },
    "ammo": 10,
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {}
  },
  "team": { "name": "NPC-Zelle", "members": [] },
  "party": { "characters": [] },
  "loadout": {
    "primary": "Resonanz-Sniper (SD)",
    "secondary": "Sidearm (SD)",
    "cqb": null,
    "armor": ["Kevlar", "Helm 360°"],
    "tools": ["Medikit", "Nano-Bindepflaster"],
    "support": []
  },
  "economy": { "cu": 0, "wallets": {} },
  "logs": {
    "artifact_log": [],
    "market": [],
    "offline": [],
    "kodex": [],
    "alias_trace": [],
    "squad_radio": [],
    "hud": [],
    "foreshadow": [],
    "fr_interventions": [],
    "arena_psi": [],
    "psi": [],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_warn_seen": false,
      "compliance_shown_today": false,
      "platform_action_contract": {
        "action_mode": "uncut"
      }
    }
  },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {},
    "fragen": []
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": false,
    "suggest_mode": false,
    "action_mode": "uncut",
    "contrast": "standard",
    "badge_density": "standard",
    "output_pace": "normal"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
    "match_policy": "sim",
    "previous_mode": null,
    "wins_player": 0,
    "wins_opponent": 0,
    "tier": 1,
    "proc_budget": 0,
    "artifact_limit": 0,
    "loadout_budget": 0,
    "phase_strike_tax": 0,
    "team_size": 1,
    "fee": 0,
    "scenario": null,
    "started_episode": null,
    "last_reward_episode": null,
    "policy_players": [],
    "audit": []
  }
}
```

> Gruppen-Save analog mit `party.characters[]`. Kein zweites Schema mit anderen Feldnamen.

#### Arc-Dashboard-Objekt

`arc_dashboard` sammelt alle Story-Hub-Einträge aus dem HQ-Dashboard. Das Feld ist im Schema
verpflichtend, wird aber vom Serializer automatisch nachgezogen und strukturiert:

- **`offene_seeds[]`** - Liste aktiver Missionsansätze. Einträge können Strings (Freitext-Notizen)
  oder Objekte (z. B. mit `id`, `titel`, `status`, `deadline`) sein. Optionales
  Feld `seed_tier` dient als Balancing-Hinweis (`early|mid|late`) ohne Freischalt-
  oder Sperrwirkung; alle Seeds bleiben ab Level 1 spielbar.
- **`fraktionen{}`** - Wörterbuch mit Fraktionsschlüsseln; Werte sind Objekte für Ruf, Haltung oder
  letzte Aktionen. Die Runtime ergänzt `last_intervention`, `last_result`, `last_updated` sowie
  `interventions[]` (max. sechs Snapshots aus `logs.fr_interventions[]` inklusive Wirkung/Notiz),
  sodass HQ-Dashboard, Kampagnenlog und Runtime denselben Stand anzeigen.
- **`fragen[]`** - Offene Forschungs- oder Storyfragen als kurze Strings oder Objekte.

Beim Laden normalisiert `load_deep()` das Objekt, entfernt Nullwerte und stellt sicher, dass alle
Listen echte Arrays sind. Unbekannte Zusatzfelder bleiben erhalten.

### Legacy-Aliase & Normalisierung

- `party.characters[]` ist die verbindliche Quelle für Gruppenroster. Laufzeit und
  Serializer lesen ausschließlich daraus.
- Historische Felder (`team.members[]`, `team.roster[]`, `group.characters[]`,
  `party.members[]`, `npc_team[]`) werden beim Laden automatisch nach
  `party.characters[]` gespiegelt. Doppelte Einträge erkennt `load_deep()`
  anhand von IDs, Callsigns oder Namen und entfernt sie.
- Beim Speichern repliziert der Serializer den bereinigten Cast zusätzlich nach
  `team.members[]`, um Kompatibilität mit älteren Tools zu bewahren - ohne
  voneinander abweichende Arrays. `team.members[]` ist somit immer eine
  1:1-Kopie des kanonischen `party.characters[]`. GPT ergänzt neue
  Koop-Mitglieder ausschließlich im `party`-Block; `team.members[]` wird nur
  vom Serializer gespiegelt, damit Saves aus Solo- und Koop-Läufen keine
  widersprüchlichen Listen mehr besitzen.
