---
title: "ZEITRISS 4.2.6 - Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)"
version: 4.2.6
tags: [system]
---

# ZEITRISS 4.2.6 - Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)

## SSOT-Anker (Systems-Pass)

- **MUSS:** SaveGuard bleibt HQ-only; Missionen, Arena-Warteschlange und
  Chronopolis sind keine gültigen Speicherkontexte.
- **MUSS:** Px bleibt einheitlich (`campaign.px` als Quelle). Bei Px 5 löst
  ausschließlich `ClusterCreate()` aus; der Reset erfolgt via HQ-Bestätigung.
  `campaign.px_state` bildet den Lebenszyklus (`stable|pending_reset|consumed`)
  und verhindert Px-Reanimationen bei Split/Merge.
- **MUSS:** Economy-Sync bleibt konsistent (`economy.hq_pool` als Primäranker,
  `economy.credits` als Legacy-Fallback via Synchronisierung).
- **SOLL:** Neuer Chat pro Mission wird als empfohlener Stabilitätspfad geführt,
  ohne als harte Regel formuliert zu werden.
- **KANN:** Optionale Trace-Felder dürfen ergänzt werden, sofern sie keine
  Kernregeln (SaveGuard, Px-Flow, Belohnungslogik) verändern.

## Speichern & Laden - Kurzreferenz

> **Für Spieler:** Hier das Wichtigste in 30 Sekunden.
>
> - **Speichern** geht nur im HQ (nach Chargen, nach Missionen, vor dem nächsten Einsatz) und wird **ausschließlich** durch den Spielerbefehl `!save` ausgelöst.
> - Befehl: `!save` - der Kodex erzeugt einen JSON-Block zum Kopieren.
> - **Laden:** JSON-Block (oder mehrere JSON-Blöcke) in den Chat einfügen; `Spiel laden` ist optional.
> - **In Missionen wird nicht gespeichert** - das erhöht die Spannung.
> - **Neuer Chat pro Abschnitt** empfohlen: Chargen → Save → neuer Chat → HQ-Runde → Save → neuer Chat → Mission → HQ → Save → neuer Chat. Jeder Abschnitt startet frisch.
> - **Kodex-Hinweis am savebaren HQ-Zustand (einmal):** `HQ-Zustand stabil. Deepsave möglich.`
> - Nach Save folgt **kein automatisches Briefing**; stattdessen: `Für sauberen Missionsbetrieb neuen Chat nach JSON-Export empfohlen.`
> - **Savebare HQ-Zustände:** Chargen-Ende (klassischer Pfad), Mission-Debrief-Ende, Load-Import, HQ-Pause-Anker. Der Kodex-Hinweis erscheint bei allen vier Zuständen — einmal pro Zustand, kein Spam.
> - **Ausnahme Fast-Lane (`solo schnell` / `gruppe schnell`):** springt direkt in den Briefingraum, kein Chargen-Save-Gate. Save-Angebot erst nach Mission 1.
>
> _Technische Details für die KI-Spielleitung folgen unten._

## HQ-JSON-Save {#json-schluesselfelder}

> **Guard:** Speichern nur in der HQ-Phase; Pflichtwerte sind deterministisch.
> Chat-Befehle im reinen Chatbetrieb: `!save` und `!bogen` (Alias `!charakterbogen`). Laden erfolgt über JSON-Paste im Chat; `Spiel laden` bleibt optionaler Prompt.
> Einziger Save-Typ: Deepsave (HQ-only).

**Referenzstand (Legacy-v6):** Für Migrationen wird ein vollständig
ausgefüllter v6-Referenzstand mit Pflichtfeldern und Cross-Mode-Pfaden
(`characters[].wallet`, `logs.psi[]`, `arc.open_seeds`,
`arena.phase_strike_tax`) genutzt. Er dient ausschließlich der
Import-Validierung; der kanonische Exportpfad bleibt v7.

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

> _Die folgenden Strings und Codeblöcke sind KI-Spielleiter-Referenz und nicht
> für Spieler gedacht. Der Block arbeitet auf der internen Runtime-/Import-Bridge
> (inkl. Legacy-Feldern wie `character.attributes._`/`cooldowns`) vor der
> v7-Normalisierung und beschreibt **keinen** kanonischen Neu-Export.\*

{# LINT:HQ_ONLY_SAVE #}

```pseudo
assert state.location == "HQ", (
  "SaveGuard: Speichern nur im HQ - HQ-Save gesperrt."
)
assert state.character.sys_installed <= state.character.attr.SYS
assert state.character.attributes.SYS_runtime <= state.character.sys_installed
assert not state.get('city_active') und not state.get('arena_active')
assert not state.get('exfil_active') und not state.get('transfer_active')
assert not campaign.exfil.active
normalize_hq_transients()  # stress/psi_heat/sys_runtime/sys_used/cooldowns/timer
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
  "characters.wallet",
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
  "logs.flags.continuity_conflicts",
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

**v7-Export-Pflichtfelder (kanonisch, nicht Runtime-Bridge):** Der Pseudocode
oben arbeitet auf der internen Runtime-Bridge — die dort aufgelistete
`required`-Liste (inkl. `character.attributes.SYS_runtime`, `cooldowns`,
`logs.offline`, `logs.alias_trace` …) ist **kein** Exportvertrag.
Für den tatsächlichen `!save`-JSON-Export nach Schema v7 sind
folgende Felder Pflicht (Template-SSOT = Masterprompt §F):

```text
v, zr, save_id, parent_save_id, merge_id, branch_id,
campaign { episode, mission, px, px_state, mode, rift_seeds[], entry_choice_skipped, episode_start, episode_end },
characters[] { id, name, callsign, rank, lvl, xp, origin, attr, lp, lp_max,
               stress, has_psi, sys_installed, psi_heat?, pp?, psi_abilities?,
               talents[], equipment[], implants[], history, carry[],
               quarters_stash[], vehicles, artifact?, reputation, wallet,
               level_history },
economy { hq_pool },
logs { trace[], hud[], psi[], arena_psi[], market[], artifact_log[], notes[], flags },
summaries { summary_last_episode, summary_last_rift, summary_active_arcs },
continuity { last_seen { mode, episode, mission, location },
              split, roster_echoes[], shared_echoes[],
              convergence_tags[], npc_roster[], active_npc_ids[] },
arc { factions, questions[], hooks[] },
ui { gm_style, suggest_mode, action_mode, intro_seen, dice{debug_rolls}, contrast, badge_density, output_pace, voice_profile },
arena { active, phase, queue_state, mode, tier, previous_mode, resume_token, contract_id, streak,
        pending_rewards, banked_rewards, rewarded_runs_this_contract, first_wins, defeated_types,
        last_reward_episode, wins_player, wins_opponent, match_policy }
```

Felder wie `character.attributes.SYS_runtime`, `cooldowns`, `city_active`,
`logs.alias_trace`, `logs.squad_radio` etc. sind **Runtime-only** und werden
bei HQ-Save-Normalisierung verworfen, nicht exportiert. `campaign.loc` ist
ebenfalls **runtime-only**; der Save nutzt `continuity.last_seen.location`
und `logs.flags.chronopolis_unlocked` für Load-Routing.

**HQ-Save-Normalisierung:** Liegt `location="HQ"` vor und es ist kein aktiver
Einsatz mehr offen (`CITY`, Arena, aktives Exfil-, Transfer- oder Queue-State
ausgenommen), normalisiert der HQ-Save vor dem Export alle transienten Felder
auf HQ-Basis (`stress`, `psi_heat`, `SYS_runtime`, `SYS_used`, `cooldowns`,
Exfil-/Timer-Reste). Diese Felder blockieren den HQ-Save nicht, solange die
Crew wieder frei im ITI steht.

**SYS-Guard-Korrektur:** `sys_installed` folgt dem Charaktersystem und prüft
`sys_installed ≤ attr.SYS`, nicht Gleichheit. Freie SYS-Slots sind gültig und
dürfen keinen HQ-Save sperren.

> **Regel: UI-Felder sind persistent.** Was der Spieler einstellt, bleibt.
> Die Felder `ui.suggest_mode`, `ui.contrast`, `ui.badge_density` und
> `ui.output_pace` werden beim Speichern **IMMER** geschrieben - kein
> Weglassen, kein Fallback auf Defaults. Der SaveGuard bricht ab, wenn
> eines dieser Felder `null` oder nicht vorhanden ist.

Speichern ist ausschließlich in der HQ-Phase zulässig. Alle Ressourcen sind
dort deterministisch gesetzt. **ITI** ist die Gesamtanlage; für SaveGuards
meint **HQ** jedoch nur den sicheren ITI-Kern inklusive aller ITI-Decks und
Pre-City-Hub. Chronopolis zählt als eigener `CITY`-Status und ist **kein**
Savepunkt: Saves aus der City brechen mit
"SaveGuard: Chronopolis ist kein HQ-Savepunkt - HQ-Save gesperrt." ab.
`flags.runtime.skip_entry_choice` bleibt ein reines Laufzeit-Flag und gehört
nicht ins Save; Persistenzanker sind ausschließlich
`campaign.entry_choice_skipped` und `ui.intro_seen`.

Der kanonische Export folgt ausschließlich dem v7-Template im Masterprompt
und dem Kompakt-Profil in dieser Datei.
Ein externes JSON-Schema existiert nur für Runtime-/Loader-Checks außerhalb
des Wissensspeichers; Altstände dürfen darüber als Legacy-Import geprüft werden
(`Save-Schema (saveGame.v6)`), werden danach auf den v7-Pfad migriert und nur
noch als v7 exportiert.
Für KI-Läufe gilt: keine Repo-Abhängigkeit, maßgeblich ist das
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

**SaveGuard-Reihenfolge** _(KI-Spielleiter-Referenz)_: Offline blockiert exklusiv und schreibt
`reason: offline`. Danach greift der Arena-Blocker (`reason: arena_active`
inkl. `queue_state`/`phase`/`zone`), anschließend HQ-only (`hq_only` oder
`chronopolis`). Erst danach folgen Exfil-, SYS-, Stress- und Psi-Heat-Checks,
die dieselben Guard-Strings nutzen. Alle Guards landen als `save_blocked`-Trace
mit `reason`, `location` und `phase` (Fallback auf `state.phase`, falls
`campaign.phase` fehlt), damit Reihenfolge und Auslöser in Snapshots
transparent bleiben.

| Priorität | Guard               | Trace-Reason                                         | Hinweis                                |
| --------- | ------------------- | ---------------------------------------------------- | -------------------------------------- |
| 1         | Offline             | `offline`                                            | Exklusiv; kein weiterer Guard danach.  |
| 2         | Arena aktiv         | `arena_active`                                       | `queue_state`/`phase`/`zone` im Trace. |
| 3         | HQ-only/Chronopolis | `hq_only`/`chronopolis`                              | Pre-City-Hub zählt als HQ.             |
| 4         | Exfil aktiv         | `exfil_active`                                       | Blockt HQ-Save bis Rückkehr.           |
| 5         | SYS-Checks          | `sys_not_full`/`sys_overflow`/`sys_runtime_overflow` | Vollinstallation + Runtime-Limit.      |
| 6         | Stress aktiv        | `stress_active`                                      | Blockt bis Stress 0.                   |
| 7         | Psi-Heat aktiv      | `psi_heat_active`                                    | Blockt bis Psi-Heat 0.                 |

### Kompakt-Profil (Save v7)

Das kanonische Schema-Template steht im **Masterprompt** (`meta/masterprompt_v6.md`).
Orientiere dich an SaveGuard + folgendem Pfadbaum.

**Wichtig zur Struktur:** `characters[]` ist nur der Charakterblock. `economy`,
`logs`, `summaries`, `continuity`, `arc`, `ui` und `arena` liegen
immer auf **Root-Ebene** (nicht unter einem Charakter).

- `v`, `zr` (Schema- und ZEITRISS-Version)
- `save_id`, `parent_save_id`, `merge_id`, `branch_id` (Lineage + Dedupe-Guards)
- `campaign.{episode, mission, px, px_state, mode, rift_seeds[], entry_choice_skipped, episode_start, episode_end}`
- `characters[]` — Array, Session-Anker-Charakter = Index 0. Pro Character:
  - `{id, name, callsign, rank, lvl, xp}`
  - `origin.{epoch, hominin, role}`
  - `attr.{STR, GES, INT, CHA, TEMP, SYS}` (SYS = SYS_max)
  - `lp, lp_max, stress, has_psi, sys_installed`
  - wenn `has_psi`: `psi_heat, pp, psi_abilities[]`
  - `talents[], equipment[{name,type,tier}], implants[{name,sys_cost,effect}]`
  - `history{background, milestones[]}`
  - `carry[{name,type,tier}]` (max 6, missionsnah)
  - `quarters_stash[{name,type,tier}]` (max 24, HQ-Lager je Charakter)
  - `vehicles{epoch_vehicle, availability, legendary_temporal_ship?}`
  - `artifact?: {name, tier, effect}` (max 1)
  - `reputation.{iti, faction, factions:{}}`
  - `wallet`
- `economy.{hq_pool}`
- `logs.{trace[], hud[], psi[], arena_psi[], market[], artifact_log[], notes[], flags:{}}`
- `summaries.{summary_last_episode, summary_last_rift, summary_active_arcs}`
- `continuity.{last_seen, split, roster_echoes[], shared_echoes[], convergence_tags[], npc_roster[], active_npc_ids[]}`
- `arc.{factions:{}, questions:[], hooks:[]}`
- `ui.{gm_style, suggest_mode, action_mode, intro_seen, dice{debug_rolls}, contrast, badge_density, output_pace, voice_profile}`
  - Pflicht-Unterfeld: `ui.dice.debug_rolls`
- `arena.{active, phase, queue_state, mode, tier, previous_mode, resume_token, contract_id, streak, pending_rewards, banked_rewards, rewarded_runs_this_contract, first_wins, defeated_types, last_reward_episode, wins_player, wins_opponent, match_policy}` (immer vorhanden; ungenutzt als Default-Idle-Block)
  - Pflicht-Unterfelder: `arena.active`, `arena.phase`, `arena.queue_state`, `arena.mode`, `arena.tier`,
    `arena.previous_mode`, `arena.resume_token`, `arena.contract_id`, `arena.streak`,
    `arena.pending_rewards`, `arena.banked_rewards`, `arena.rewarded_runs_this_contract`,
    `arena.first_wins`, `arena.defeated_types`, `arena.last_reward_episode`,
    `arena.wins_player`, `arena.wins_opponent`, `arena.match_policy`

> **Keine Laufzeit-Daten im Save:** location, phase, scene, exfil, cooldowns,
> SYS_runtime, SYS_used werden zur Laufzeit gesetzt — nicht gespeichert.
> v6-Saves werden beim Laden automatisch migriert (`save_version: 6` → `v: 7`).

`logs.flags.last_save_at` hält den Zeitstempel für deterministische Saves fest. Der Serializer nutzt
den Wert für automatisch gestempelte HUD-Events (Fallback ohne `at`) sowie für den Save-Trace
`economy_audit`, damit Roundtrips keine neuen Zeitmarken erzeugen.

`economy_audit()` dokumentiert jeden HQ-Save mit stabilen Feldern: `level`, `band_reason`,
`hq_pool`, `wallet_sum`, `wallet_count`, `wallet_avg`, `wallet_avg_scope`,
`chronopolis_sinks`, `target_range`, `delta` und `out_of_range`. `target_range` nutzt fixe
Level-Bänder **120** (HQ 8 000-10 000 CU, Wallet Ø 1 000-2 000 CU), **512** (HQ 25 000-30 000 CU,
Wallet Ø 3 000-5 000 CU) und **900+** (HQ 45 000-60 000 CU, Wallet Ø 6 000-10 000 CU) und skaliert
`wallet_total` über alle Charakter-Wallets. Die Band-Auswahl folgt dem
Session-Anker-Level (`character.lvl|level` oder `campaign.level`); fehlt dieser,
nutzt der Audit die Medianstufe der `characters[]`-Roster und schreibt
`band_reason=session_anchor_level|roster_median|unknown`. `wallet_avg_scope`
steht immer auf `characters[].wallet`. `delta` markiert Abweichungen pro Wert, `out_of_range` setzt
boolesche Flags und löst
den Toast "Economy-Audit: HQ-Pool/Wallets außerhalb Richtwerten (Lvl 120|512|900+)." aus.
Der Save-Trace `economy_audit` landet in `logs.trace[]` und folgt der Save-Guard-Priorität, sodass
Arena-/Offline-Blocker keine fehlerhaften Audit-Deltas erzeugen.

**Save-Größenbudget (OpenWebUI robust):** Für HQ-Deepsaves gelten feste Rolling-Caps,
damit Copy/Paste-Loads stabil bleiben: `logs.trace` max **64**, `logs.market` max **24**,
`logs.artifact_log` max **32**, `logs.notes` max **24**, `arc.questions` max **18**,
`arc.hooks` max **18** sowie `characters[].history.milestones` max **20** pro Charakter.
Beim Pruning bleiben die neuesten Einträge erhalten; ältere Detailstände werden
kompakt in `summaries.summary_last_episode`, `summaries.summary_last_rift` und
`summaries.summary_active_arcs` verdichtet, statt still verloren zu gehen.

Externe Schema-Dateien dienen nur Tooling/CI; die KI-SL nutzt ausschließlich
das Klartext-Profil als maßgebliche Struktur.

Der Serializer befüllt `arc` vor dem SaveGuard automatisch mit
leeren Arrays/Objekten und setzt fehlende Arc-Blöcke nicht stillschweigend
zurück: Pflichtpfade (`factions`, `questions`, `hooks`) lösen
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
"SaveGuard: Arena aktiv - HQ-Save gesperrt.", solange Matchmaking/Run aktiv
ist. Ein HQ-Save ist nach PvP explizit wieder erlaubt, sobald der Arena-Block
auf Abschlusszustand normalisiert ist (`queue_state=idle|completed` bei
`arena.active=false` und `arena.phase=idle|completed`).

In-Mission-Ausstieg ist erlaubt, aber es erfolgt kein Save; Ausrüstung darf
übergeben werden, nächster Save erst im HQ. HQ-Saves verlangen vollständige
Installation (`sys_installed ≤ attr.SYS`).

> **Migrations-Referenz (v6):** Für die KI-SL liegt die kanonische
> Legacy-Überführung direkt im Wissensspeicher (siehe
> [V6→V7-Migrationsbeispiel](#v6-v7-migrationsbeispiel-im-wissensspeicher)).
> Im Runtime-Kanon gilt beim Export ausschließlich das v7-Format mit `v`,
> `characters[]`, `characters[].wallet`, `economy.hq_pool` und `arc`.

### V6→V7-Migrationsbeispiel im Wissensspeicher {#v6-v7-migrationsbeispiel-im-wissensspeicher}

Dieses Beispiel ist absichtlich kompakt, damit die **KI-SL ohne externe
Repo-Dateien** alte Stände sicher umheben kann.

**Legacy-Eingabe (v6, schematisch):**

- `save_version = 6`
- `zr_version = 4.2.6`
- `party.characters = [agent-nova(wallet=320)]`
- `team.members = [agent-rook(wallet=280)]`
- `economy.cu = 540`
- `arc_dashboard.offene_seeds = [RS-01@1947]`
- `campaign.mission_in_episode = 5`

**Ziel nach Migration (v7, kanonisch):**

- `v = 7`, `zr = 4.2.6`
- `characters = [agent-nova(wallet=320), agent-rook(wallet=280)]`
- `economy.hq_pool = 540`
- `campaign.mission = 5`
- `campaign.rift_seeds = [RS-01@1947(status=open)]`
- `arc = {questions[], hooks[], factions{}}`

**Merke (SSOT):**

- `save_version`/`zr_version` sind reine Importmarker.
- `party.characters[]` und `team.members[]` werden in `characters[]` zusammengeführt.
- `economy.cu` wird auf `economy.hq_pool` gehoben.
- `arc_dashboard.offene_seeds[]` wird in den v7-Pfad (`campaign.rift_seeds[]`) überführt.
- Exportiert wird anschließend **nur** das v7-Format.

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
Solo-/Px-5-Runs stapeln neue Seeds ohne Solo-Hardcap. Für die spielerseitig
sichtbare Liste gilt beim HQ-Merge/Group-Import ein Cap von 12 offenen Seeds;
überschüssige Seeds gehen als Hand-off an ITI-NPC-Teams. Der Merge schreibt
dazu ein Trace `rift_seed_merge_cap_applied`
(kept/overflow) und einen `merge_conflicts`-Record mit `rift_merge` inklusive
`kept[]`/`overflow[]`, `handoff_to` und `selection_rule`, damit Debriefs den
Hand-off
transparent nachverfolgen können.

> **Spieler-Sprache:** `ClusterCreate()` ist der Moment, wo ihr eure Belohnung
> bekommt. Px 5 erreicht → 1-2 neue Rift-Missionen erscheinen auf der Karte →
> nach der aktuellen Episode könnt ihr sie spielen. Das ist der Loot für gutes Spielen.

**Single Source "Save v7":** Modul 12 führt das _einzige_ kanonische Schema für
HQ-Deepsaves. README und Toolkit zitieren lediglich Auszüge, ohne abweichende
Felder zu definieren. Legacy-Schlüssel (`save_version`, `party.characters[]`,
`team.members[]`, `economy.cu`, `arc_dashboard`) sind reine Import-Aliase; neue
Saves entstehen ausschließlich im v7-Format mit `v`, `characters[]` und
`economy.hq_pool`. Divergierende Doppelstrukturen gelten als Fehler und werden
beim Laden zusammengeführt.

**Lineage & Dedupe (Merge-Schutz):** Jeder v7-Save führt `save_id` als eindeutige
Import-ID. `parent_save_id` zeigt auf den direkten Vorgänger, `merge_id` markiert
gezielte Zusammenführungen und `branch_id` beschreibt den Branch-Kontext (z. B.
`ANCHOR-main`, `RIFT-A`). Bei JSON-Mehrfachimport gilt: doppeltes `save_id` im selben
Load-Lauf wird als Branch-Duplikat verworfen (`logs.flags.duplicate_branch_detected=true`),
doppelte `characters[].id` werden als Rejoin-Konflikt markiert
(`logs.flags.duplicate_character_detected=true`) und als strukturierte
`logs.flags.continuity_conflicts[]`-Einträge transparent geführt, statt stiller Überschreibung. Jeder verworfene oder konflikthafte Import
läuft zusätzlich in `logs.flags.imported_saves[]` ein (mindestens `save_id`,
`branch_id`, `status`, `reason`).

### E2E-Trace-Schema {#e2e-trace}

`logs.trace[]` hält ein kompaktes E2E-Protokoll pro Modus/Szene. Jede Zeile
enthält mindestens `event`, `at` (ISO), `location`, `phase`,
`mission_type`/`campaign_mode`, `scene{episode,mission,index,total}` sowie
`foreshadow{progress,required,tokens,expected}`. Optionale Felder fassen HUD-
Overlay, Radio-/Alias-/Kodex-Zähler, Ökonomie (`economy{hq_pool}` + Wallet-Summen), FR-Bias
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

**Phase-Feld:** HQ-Deepsaves persistieren keinen laufenden Runtime-`phase`-Wert.
Der kanonische Save-Anker ist `continuity.last_seen` mit
`continuity.last_seen.mode="hq"` und `continuity.last_seen.location="HQ"`.
Während einer laufenden Mission setzt die Runtime `state.phase`/`campaign.phase`
weiterhin auf `core|transfer|rift|pvp` (immer Kleinbuchstaben).
Missionstypen dürfen in `logs.trace[]`, `summaries.*` und Runtime-Status stehen,
aber nicht als aktiver HQ-Save-Modus persistiert werden.
Andere Werte führen beim Laden zu einem SaveGuard-Fehler.

**Accessibility-Felder:** Serializer und Migration normalisieren den UI-Block
(`ui.gm_style`, `ui.suggest_mode`, `ui.action_mode`) und ergänzen fehlende
Felder für `contrast`, `badge_density`, `output_pace` und `voice_profile` mit
Defaults (`standard`/`standard`/`normal`/`gm_second_person` plus
`action_mode=uncut`). `voice_profile` erlaubt `gm_second_person` (Default),
`gm_third_person` oder `gm_observer`; unbekannte Werte fallen auf das Default
zurück.
`action_mode` ist immer `uncut` (18+ Tech-Noir). Legacy-Werte wie
`konform|frei|safe|pg-13` werden beim Laden auf `uncut` normalisiert.

> **UI-Persistenz-Regel:** Die sieben Felder `ui.gm_style`,
> `ui.suggest_mode`, `ui.action_mode`, `ui.contrast`,
> `ui.badge_density`, `ui.output_pace` und `ui.voice_profile` sind
> **persistent**.
> Beim Speichern schreibt der Serializer sie IMMER explizit in den Save-Block.
> Beim Laden restauriert `load_deep()` sie IMMER 1:1 aus dem Save - kein
> Fallback auf Defaults für vorhandene Werte. Nur bei fehlenden Feldern in
> alten Saves (Legacy/pre-v6) setzt der Normalizer folgende Defaults ein:
>
> | Feld            | Default für alte Saves |
> | --------------- | ---------------------- |
> | `gm_style`      | `"verbose"`            |
> | `suggest_mode`  | `false`                |
> | `action_mode`   | `"uncut"`              |
> | `contrast`      | `"standard"`           |
> | `badge_density` | `"standard"`           |
> | `output_pace`   | `"normal"`             |
> | `voice_profile` | `"gm_second_person"`   |
>
> Diese Defaults gelten ausschließlich als Auffangnetz für Migrationsfälle.
> Aktuelle Saves (v7) müssen alle sieben Felder enthalten - der SaveGuard
> bricht andernfalls ab.

### Voller HQ-Deepsave (Solo/Gruppe) {#full-save}

> **IMPORT-ONLY / NICHT KOPIEREN / KEIN `!save`-BEISPIEL:**
> Dieser Abschnitt ist ausschließlich Legacy-/Migrationsreferenz und kein aktiver Wissensspeicher-Exportvertrag.

> **Legacy-/Import-Hinweis (Legacy-Bridge):** Der folgende Block dient als Bridge-Referenz für
> Migrationen aus älteren Ständen. **Nicht als kanonischen Neu-Export verwenden.**
> Kanonische Exporte folgen dem v7-Zielmodell
> (`v`, `zr`, `characters[]`, `attr`, `economy.hq_pool`, `arc.questions/hooks`).

> Referenz-HQ-Block mit Quartier, Timeline, Squad und Feldnotizen. Alle
> Pflichtfelder bleiben erhalten; optionale Blöcke sind knapp, aber vollständig
> ausgefüllt, damit jede Spielleitung sofort den gesamten Charakterbogen
> nachvollziehen kann.

> **Legacy-Feldhinweis:** `location` und `phase` in den folgenden Beispielen sind
> reine Migrationsfelder für Altstände. Im kanonischen v7-Neu-Export sind beide
> Root-Felder ausgeschlossen (siehe Abschnitt **Kanonisches Save-Exportformat**).

> **Leseregel für dieses Legacy-Muster:** Trotz `v: 7` im Beispiel bleibt dieser
> Block eine reine Import-/Migrations-Bridge. Für Neu-Exporte gilt ausschließlich
> das kanonische v7-Zielmodell im Abschnitt **Kanonisches Save-Exportformat**.

```json
{
  "v": 7,
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
    "rift_seeds": []
  },
  "character": {
    "id": "AGENT-01",
    "attributes": {
      "SYS_max": 2,
      "SYS_installed": 2,
      "SYS_runtime": 2,
      "SYS_used": 2
    },
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "self_reflection": true
  },
  "characters": [
    {
      "id": "AGENT-01",
      "name": "Agent Nova",
      "callsign": "Nova",
      "rank": "Operator I",
      "lvl": 2,
      "xp": 120,
      "origin": {
        "epoch": "ITI-Nullzeit",
        "hominin": "Homo sapiens sapiens",
        "role": "CQB-Operator"
      },
      "attributes": {
        "STR": 3,
        "GES": 6,
        "INT": 4,
        "CHA": 2,
        "TEMP": 1,
        "SYS_max": 2,
        "SYS_installed": 2,
        "SYS_runtime": 2,
        "SYS_used": 2
      },
      "lp": 10,
      "lp_max": 10,
      "stress": 0,
      "has_psi": false,
      "psi_heat": 0,
      "sys_installed": 2,
      "talents": ["Schleichprofi", "Pistolenschütze", "Reaktionsschnell"],
      "equipment": [
        { "name": "CQB-Kampfpistole (SD)", "type": "weapon", "tier": 1 },
        { "name": "Kevlar-Weste Stufe II", "type": "armor", "tier": 1 },
        { "name": "Multi-Tool Wraith", "type": "tool", "tier": 1 }
      ],
      "implants": [
        { "name": "Reflex-Boost Microline", "sys_cost": 1, "effect": "+1 Initiative" },
        { "name": "Taktisches Ohrimplantat Mk I", "sys_cost": 1, "effect": "+1 Gehör" }
      ],
      "history": {
        "background": "Schallgedämmte CQB-Zelle mit Analysten-Setup",
        "milestones": ["Olympia 2000 stabilisiert", "Apollo-15-Sabotage verhindert"]
      },
      "carry": [
        { "name": "Rauchgranate Mk I", "type": "consumable", "tier": 1 },
        { "name": "Med-Patch", "type": "consumable", "tier": 1 },
        { "name": "Notfall-Transponder", "type": "gadget", "tier": 1 }
      ],
      "quarters_stash": [
        { "name": "Ersatzmagazin", "type": "consumable", "tier": 1 },
        { "name": "Faseroptik-Kabelkamera", "type": "tool", "tier": 1 }
      ],
      "vehicles": {
        "epoch_vehicle": {
          "id": "VEH-0001",
          "name": "Brough Superior SS100",
          "type": "vehicle",
          "tier": 1,
          "upgrades": []
        },
        "availability": { "ready_every_missions": 4, "next_ready_in": 0 },
        "legendary_temporal_ship": null
      },
      "wallet": 1650
    }
  ],
  "loadout": {
    "AGENT-01": {
      "primary": "CQB-Kampfpistole (SD)",
      "secondary": "Tactical Fighting Knife",
      "armor": "Kevlar-Weste Stufe II",
      "gear": ["Multi-Tool Wraith", "Faseroptik-Kabelkamera", "Rauchgranate Mk I", "Micro-Breacher"]
    }
  },
  "economy": { "hq_pool": 1650 },
  "logs": {
    "trace": [],
    "artifact_log": [],
    "market": [],
    "offline": [],
    "kodex": [],
    "alias_trace": [],
    "squad_radio": [],
    "arena_psi": [],
    "flags": {
      "runtime_version": "4.2.6",
      "chronopolis_warn_seen": false,
      "continuity_conflicts": []
    },
    "field_notes": [
      {
        "agent_id": "AGENT-01",
        "mission": "Sydney 2000 - Maskottchen-Alarm",
        "timestamp": "2000-09-15T20:30:00Z",
        "note": "Kontaminationsalarm im Logistikbereich eingedämmt; Probenbestand gesichert."
      }
    ]
  },
  "arc": {
    "open_seeds": [],
    "factions": { "ITI": 0, "Ordo Mnemonika": 0, "Kausalklingen": 0 },
    "open_questions": [],
    "timeline": [
      {
        "id": "TL-OLYMPICS-2000",
        "epoch": "2000",
        "label": "Kontaminationsalarm bei Olympia 2000 stabilisiert"
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
    "output_pace": "normal",
    "voice_profile": "gm_second_person"
  },
  "arena": { "active": false, "phase": "idle", "mode": "single", "tier": 1 }
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

**Arc-Notizen (v7):** Laufende Weltfäden werden im kanonischen Export über
`arc.factions`, `arc.questions`, `arc.hooks` und die `summaries.*`-Blöcke
geführt. Legacy-Importe aus `arc_dashboard.timeline[]` bleiben reine
Migrationsquellen und werden beim Laden in diese v7-Pfade verdichtet, statt als
`arc.timeline[]` weitergeführt.

**Mission 5/10 Auto-Reset (Self-Reflection-Beispiel)**

```json
{
  "logs": {
    "hud": ["SF-OFF (Mission 5)", "GATE 2/2", "SF-ON (post-M5 reset)"],
    "self_reflection_history": [
      { "mission_ref": "EP04-MS05", "reason": "mission5_end", "ts": "2025-11-26T22:10:00Z" },
      { "mission_ref": "EP04-MS10", "reason": "mission10_end", "ts": "2025-11-27T22:10:00Z" }
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
  "character": { "self_reflection": true },
  "ui": { "suggest_mode": false, "action_mode": "uncut" }
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

- Pflichtfelder (v7-Export): `v`, `zr`, `campaign.px`, `characters[]`
  (kanonischer Charakterbogen inkl. `wallet`, `history`, `carry`,
  `quarters_stash`, `vehicles`), `economy.hq_pool`, `arc`, `logs`, `ui`
  und `arena` als verpflichtender Root-Block (bei Inaktivität als Default-Idle).
- **Paradoxon-Index:** `campaign.px` ist die einzige Quelle für Px-Stand und
  Progression. Rifts erzeugen kein separates `rift_px`; Importpfade verwerfen
  abweichende Felder und mappen Legacy-Keys zurück auf `campaign.px`.
- Optionales Feld: `modes` - Liste aktivierter Erzählmodi.
- Root-`character` bleibt ein reiner Legacy-Importpfad. Beim Neu-Export
  schreibt die KI-SL ausschließlich `characters[]` (Session-Anker = Index 0);
  SYS-/Stress-/Heat-Status werden pro Charakter geführt und Laufzeitwerte beim
  Laden neu gesetzt.
- Die KI-SL darf keine dieser Angaben ableiten oder weglassen. Der Serializer setzt
  fehlende Pflichtblöcke automatisch auf sichere Defaults (`economy.hq_pool = 0`,
  leere Logs mit `logs.flags`, `ui.gm_style = "verbose"`).
- `characters[]` ist die kanonische Gruppenstruktur. Legacy-Saves mit
  `party.characters[]`/`team.members[]` werden beim Import nach `characters[]`
  normalisiert; Exporte und Debriefs nutzen ausschließlich `characters[]`.
- Die Load-Pipeline nutzt dafür explizit `migrate_save()` als Legacy-Bridge,
  bevor `load_deep()` Pflichtfelder validiert und Defaults ergänzt.

### Cross-Mode Import - Solo → Koop/Arena {#cross-mode-import}

Cross-Mode-Sequenz (Solo → Koop → Arena → Debrief):
`load_save()` → `normalize_roster_to_characters()` → `sync_hq_pool()` →
Arena-Gebühr über `arenaStart()` → Debrief `apply_wallet_split()`.

1. **Solo-Save laden.** `characters[]` enthält initial den Protagonisten.
   Zusätzliche Crew-Saves dürfen nur Charaktere (inkl. Wallet), Loadouts und
   zulässige Inventar-/Statusfelder beisteuern.
2. **Koop- oder Gruppeneinsatz starten.** Im Debrief erzeugt `apply_wallet_split()`
   für jedes Teammitglied eine Auszahlung und protokolliert den Vorgang als
   `Wallet-Split` in den HUD-Logs.
3. **Arena aktivieren.** `arenaStart()` setzt `arena.policy_players[]`,
   `arena.previous_mode` und `arena.phase='active'`, markiert `location='ARENA'`
   und blockiert Save-Versuche bis zum Arena-Exit.
4. **Zurück nach HQ.** Nach Arena-Exit bleibt `campaign.px` unverändert;
   Rewards laufen über `economy.hq_pool` sowie optionale Wallet-Splits.

**Session-Anker-Priorität (SSOT):** Bei Merge/Import bleibt der Session-Anker
führend für `campaign`, `economy.hq_pool`, `arc` und globale `logs.flags`.
Gaststände liefern persönliche Wahrheit plus erlaubte Branch-Anteile. Konflikte
werden in `logs.flags.continuity_conflicts[]` dokumentiert.

### Cross-Mode-Transfer-Matrix {#cross-mode-transfer}

Die folgende Matrix regelt verbindlich, welche Daten bei einem Moduswechsel
übernommen, verworfen oder zusammengeführt werden.

#### Transferregeln pro Richtung

| Richtung              | Übernommene Felder                                                                                                                                                                                                  | Verworfene/Zurückgesetzte Felder                                                                                                                | Besonderheiten                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Solo → Koop**       | Erster Save setzt den Session-Anker für `campaign` (episode, mission, mode, rift_seeds[], px). Gast-Saves liefern persönliche Wahrheit (`character` + `loadout` + `wallet` + History) innerhalb von `characters[]`. | Gast-`campaign` außerhalb des Ankers, Gast-`economy.hq_pool`, Gast-`logs` (außer continuity_conflicts)                                               | Session-Anker-Kampagnenblock hat Vorrang; persönliche Felder pro ID folgen dem neuesten Stand. |
| **Koop → Solo**       | Spieler-Character extrahieren (`character`, `loadout`, `wallet` aus `characters[]`).                                                                                                                                | Alles andere: `campaign` wird auf Solo-Defaults zurückgesetzt, `characters[]` auf Solo-Roster reduziert, `economy.hq_pool` bleibt ankergeführt. | `campaign.mode` wechselt zurück auf den Ursprungsmodus des Spielers.                           |
| **Jeder Modus → PvP** | `arena.previous_mode = campaign.mode` speichern. Gesamter Spielstand bleibt erhalten, `campaign.mode` wechselt temporär auf `"pvp"` (Runtime-only).                                                                                | -                                                                                                                                               | Nach Arena-Exit: `campaign.mode = arena.previous_mode`, dann `arena.previous_mode = null`.     |
| **PvP → zurück**      | `campaign.mode = arena.previous_mode` restaurieren. Arena-Rewards (CU/Ruf/Training) werden verbucht. `campaign.px` bleibt unverändert.                                                                              | `arena.previous_mode` wird auf `null` geleert. Arena-spezifische Laufzeitdaten zurücksetzen.                                                    | Fehlt `previous_mode` (Legacy), Fallback auf `"mixed"`.                                     |

#### Merge-Konflikte bei Cross-Mode-Transfer

Bei **jedem** Cross-Mode-Transfer werden Konflikte im `continuity_conflicts[]`-Array
dokumentiert. Jeder Eintrag enthält mindestens:

```json
{
  "field": "<allowlist-feld>",
  "source": "<Wert aus Quell-Modus>",
  "target": "<Wert aus Session-Anker/Ziel-Modus>",
  "mode": "<anchor_priority|allowlist_merge|fallback_default>"
}
```

Die `field`-Werte folgen der bestehenden Allowlist: `wallet`, `rift_merge`,
`arena_resume`, `campaign_mode`, `phase_bridge`, `location_bridge`.
Dedupe-/Lineage-Funde ergänzen die Allowlist um `duplicate_branch` und `duplicate_character`.

#### Trace-Protokollierung

Jeder Cross-Mode-Transfer schreibt ein Event in `logs.trace[]`:

```json
{
  "event": "cross_mode_transfer",
  "at": "<ISO-Timestamp>",
  "from_mode": "<solo|coop|pvp>",
  "to_mode": "<solo|coop|pvp>",
  "session_anchor_id": "<character.id des Session-Ankers>",
  "conflicts_count": 0,
  "conflict_fields": [],
  "location": "HQ",
  "phase": "core"
}
```

### Accessibility-Preset (zweites Muster) {#accessibility-save}

> **Legacy-/Import-Hinweis (Legacy-Bridge):** Zweites Altstands-Muster für
> Migrationsfälle; kein kanonischer v7-Neu-Export.

```json
{
  "v": 6,
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
    "attributes": { "SYS_max": 6, "SYS_installed": 6, "SYS_runtime": 6, "SYS_used": 6 }
  },
  "campaign": { "episode": 12, "scene": 0, "px": 2 },
  "characters": [{ "id": "CHR-7777", "name": "Jade", "wallet": 1200, "loadout": [] }],
  "economy": { "hq_pool": 1200 },
  "arc": { "open_seeds": [], "factions": {}, "questions": [], "timeline": [] },
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
      "chronopolis_warn_seen": true,
      "offline_help_count": 1,
      "offline_help_last_scene": "HQ:4",
      "offline_help_last": "HQ:4",
      "platform_action_contract": { "action_mode": "uncut" }
    }
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": true,
    "suggest_mode": false,
    "action_mode": "uncut",
    "contrast": "high",
    "badge_density": "compact",
    "output_pace": "slow",
    "voice_profile": "gm_second_person"
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

Das Preset illustriert, wie ein `!accessibility`-Dialog persistiert wird: Der
Kontrast steht auf `high`, Badges nutzen das kompakte Layout und der Output
läuft im `slow`-Takt. Diese Werte bleiben erhalten, bis Nutzer sie im HQ
zurücksetzen. HQ-Deepsaves normalisieren den kompletten UI-Block.

## Laden & HQ-Rückkehr {#load-flow}

### Ablauf beim Laden per JSON-Paste (mit oder ohne `Spiel laden`)

1. **JSON posten.** HQ-Deepsave als JSON einfügen (ein Save für Solo, mehrere Saves für Split/Merge). Optional kann davor `Spiel laden` gesendet werden.
2. **Deserializer starten.** Das hier dokumentierte `load_deep()`-Schema
   migriert Legacy-Felder in die v7-Zielstruktur, prüft Pflichtblöcke und setzt
   `state.location='HQ'`.
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
   aus. Die Runde springt ohne Nachfrage in den HQ-Load-Router
   (Schnell-HQ/HQ manuell/Briefing/Chronopolis/Rift/Arena-Router).
   Arena-Router-Regel: `!arena resume` nur mit `arena.resume_token` und
   `queue_state=idle|completed`; aktive Queue-Stati (`searching|matched|staging|active`)
   bleiben vor Resume blockiert.
5. **Compliance-Hinweis entfällt.** Loads laufen ohne Compliance-Toast oder
   Flag-Setzung; `ShowComplianceOnce()` bleibt nur als leerer
   Kompatibilitäts-Hook bestehen.

{# LINT:FS_RESET_OK #}

> **Laufzeitabgleich:** Dieses Modul ist maßgeblich für KI-basierte
> Spielleitungen. Runtime-Implementierungen müssen die hier definierten
> Regeln spiegeln, dürfen aber keinen eigenen Spielkanon einführen.

**Multi-Save-Import (Gruppenschnellstart):** Werden vor einem neuen Briefing
mehrere HQ-Saves gleichzeitig gepostet (`Spiel starten (gruppe schnell)`), setzt
der **zuerst gepostete Save den Session-Anker** (aktueller Einstiegspunkt mit
`episode`, `mission`, `mode`, `rift_seeds[]`, `px`). Weitere Saves liefern
zusätzlich persönliche Wahrheit pro `characters[].id` und Kontinuitäts-Echos.
Abweichende Kampagnenwerte außerhalb des Session-Ankers landen weiterhin in
`logs.flags.continuity_conflicts[]`. Der HQ-Pool (`economy.hq_pool`) bleibt
ankergeführt; Wallets/Loadouts/History der Rückkehrer werden pro Charakter
aktualisiert (neuester Stand gewinnt persönliche Felder).

#### OpenWebUI-Lobbybetrieb (Hopper/Leaver)

Für private OpenWebUI-Instanzen mit häufigen Gruppenwechseln gilt ein
Session-Anker-Modell ohne Sonderpfad:

1. **Pro Chat genau ein Session-Anker:** Der zuerst gepostete Save setzt
   den Einstieg (`campaign` mit `episode`, `mission`, `px`, Seeds).
   Das gilt auch, wenn mehrere Save-JSONs direkt in der ersten Nachricht ohne
   `Spiel laden` gepostet werden.
2. **Joiner mit persönlicher Wahrheit:** Nachrücker/Hopper bringen `characters[]`,
   Wallet, Loadouts und persönliche History mit; pro `characters[].id` zählt der
   neueste persönliche Stand.
3. **Leaver-Regel:** Rückkehrer steigen am aktuellen Session-Anker ein, behalten
   aber ihren neuesten persönlichen Charakterstand.
4. **Kein impliziter Episodenwechsel:** Episode wechselt weiterhin nur über
   regulären Debrief-/Kampagnenfluss der laufenden Runde.
5. **Empfohlener Hinweistext der Spielleitung:** _"Kontinuitäts-Import erkannt:
   Session-Anker gesetzt, Rückkehrerstände und Echos wurden integriert."_
6. **Nach Debrief im HQ (Koop):** Kurz Split-Option anbieten
   (zusammen bleiben / speichern+splitten / solo weiter), damit Gruppenwechsel
   als geordneter HQ-Schritt statt als stiller Chatbruch laufen.

## Kontinuitätsmodell (Session-Anker statt Host-SSOT)

ZEITRISS behandelt Mehrfach-Loads nicht mehr als reinen Host-Import, sondern als **Kontinuitätssynthese**.

### Goldregel

- **Erster geposteter Save = Session-Anker.** Er setzt den Einstiegspunkt der laufenden Runde (HQ, Briefing, Mission, Kampagnenrahmen).
- **Neuester Charakterstand pro `characters[].id` = persönliche Wahrheit.** Level, XP, Wallet, Gear, Carry, Artefakte, Ruf und persönliche Geschichte werden nicht auf den Anker zurückgedrückt.
- **Importierte Kontinuität = Weltmaterial.** Rückblicke, Gerüchte, offene Fäden, Branch-Ergebnisse und Rejoin-Kontext werden erzählerisch mitgeführt.

### `continuity`-Kapsel (v7)

- `last_seen`: letzter bekannter Einsatzkontext.
- `split`: `{family_id, thread_id, expected_threads[], resolved_threads[], convergence_ready}` für kanonische Core-Splits.
- `roster_echoes[]` (max 5), `shared_echoes[]` (max 6), `convergence_tags[]` (max 4).
- **Pflichtformat `shared_echoes[]`:** Jedes Item MUSS Objekt mit mindestens `tag` sein, empfohlen vollständig `{ "tag": "<slug>", "scope": "shared|rumor|campaign|personal", "text": "<kurz>" }`. Bindung: **Ereignis/Erkenntnis**, nicht Figur.
- **Pflichtformat `roster_echoes[]` (andere Struktur!):** Jedes Item MUSS Objekt mit mindestens `char_id` sein, empfohlen vollständig `{ "char_id": "<CHR-ID>", "tone": "<stimmung>", "text": "<1-Satz-Recap>" }`. Bindung: **eine Figur**, nicht ein Ereignis. Niemals mit `shared_echoes`-Format vermischen.
- **Gemeinsam**: Rohstrings (`["Lagerhaus gesichert"]`) oder Fremdkeys (`[{"echo": "..."}]`) sind in beiden Arrays Schema-Verletzung und werden von `test_v7_schema_consistency.js` + `test_continuity_output_contract.js` abgelehnt. Siehe Masterprompt §D.
- **Persistente NPC-Chrononauten:**
  - `npc_roster[]` (max 6) mit kompakten Feldern
    `id,name,callsign,role,trait,scope,owner_id,bond,status,last_seen,offscreen,hook`
  - ITI-Kernrollen nutzen feste IDs als Wiedererkennungsanker:
    `ITI-RENIER`, `ITI-MIRA`, `ITI-LORIAN`, `ITI-VARGAS`, `ITI-NARELLA`
    (optional Service-Anker: `ITI-HALDEN`, `ITI-NOX`, `ITI-JUNO`, `ITI-CASS`).
  - Diese Kernrollen gelten bereits ohne Save-Eintrag als Hauskanon; Einträge in
    `npc_roster[]` oder Echos nur bei echter offener Bindung/Schuld/Aufgabe.
  - `active_npc_ids[]` (max 4) als aktive Feldbegleitung
  - `scope`: `personal|session|iti`
  - `status`: `attached|hq|assigned|recovering|missing|rival`
  - `offscreen`: max 1 Satz pro NPC und Rückkehrfenster
- Bei HQ-`!save` werden ältere Echos verdichtet (Prune), nicht unkontrolliert gestapelt.

### Slot-Regel für Mensch/NPC-Mischgruppen

- Menschen belegen Feldplätze zuerst (Teamcap 5).
- NPCs füllen nur freie Plätze.
- Jeder geladene Save darf NPC-Kontinuität mitbringen; Auswahl dedupliziert über `npc.id`.
- Priorität: `session+attached` → `personal+attached` → `session+hq` → `personal+hq` → `iti`.
- Tie-Break: Rollenfit → Bond → Recency (`last_seen`).
- Nicht aktive bekannte NPCs bleiben als HQ-/Funk-/Offscreen-Präsenz sichtbar.

### Pflichtausgabe beim Mehrfach-Load

Vor HQ/Briefing liefert die KI-SL immer einen **Kontinuitätsrückblick** mit fünf Blöcken:

1. Session-Anker,
2. Rückkehrer/Joiner,
3. NPC-Lagebild (anwesend, offscreen, verändert, fehlend),
4. gemeinsame Nachwirkungen,
5. Konvergenz-Folge (falls `convergence_ready=true`).

### Pflichtbeats für Split/Rejoin

- **Split-Beat:** Vor Branch-Wechsel kurze Inworld-Übergabe (wer wohin geht,
  welcher Auftrag/Hinweis auf welchem Thread liegt).
- **Rejoin-HQ-Beat:** Beim Zusammenführen kurze Rückkehrszene im HQ (wer
  ankommt, wer reagiert, welche Spur sofort sichtbar wird).
- **Echo-Fortwirkung:** Mindestens ein importierter Eintrag aus
  `continuity.roster_echoes[]` oder `continuity.shared_echoes[]` muss in den
  nächsten zwei Sitzungsblöcken konkret wieder auftauchen (z. B.
  Briefing-Hinweis, NPC-Reaktion, Boss-Tell, Alt-Route oder Hook).
- **ITI-Echo-Format:** Für feste ITI-Kontakte bevorzugt kompakt als
  `ITI-ID :: Status/Hook` (z. B. `ITI-MIRA :: hält Petrow-Akte zurück, bis der
Datenkristall geprüft ist.`).
- **NPC-Departure-Beat:** Wenn ein bekannter NPC das Feld verlässt, immer 1–2
  Sätze Inworld-Übergabe statt stiller Entfernung.
- **NPC-Recognition-Beat:** Wiederkehrende NPCs erinnern mindestens eine
  konkrete gemeinsame Szene; Rückkehr nutzt genau eine kompakte
  Offscreen-Fortschreibung (Auftrag + Veränderung + Hook).
- **NPC-Cross-Pollination:** Offscreen-Rückkehr darf punktuell ein Gerücht,
  eine Wunde, einen Gegenstand, einen Boss-Tell oder einen
  Haltungswechsel aus anderer Linie mitbringen (max. 1 Hook).

**Mid-Session-Merge:** Für laufende Einsätze nutzt die KI-SL statt `load_deep()` einen
leichten Merge-Pfad: Die Save-Blöcke werden ohne Location-Reset nach
`characters[]` kopiert, Wallets normalisiert und HUD/Timer beibehalten.
So können neue Agenten aufschlagen, während `state.location` auf Mission
steht; gespeichert wird trotzdem erst wieder im HQ.

### Kompatibilität & Guards

- Semver-Toleranz: Lädt, wenn `major.minor` der gespeicherten `zr` dem
  aktuellen `ZR_VERSION` entspricht (Legacy-Importe mit `zr_version` werden vorher normalisiert); Patch-Level sind egal.
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
  1. **Start:** `arenaStart()` merkt `arena.previous_mode = campaign.mode`,
     setzt `campaign.mode = 'pvp'`.
  2. **Exit:** `arenaEnd()` stellt `campaign.mode = arena.previous_mode` wieder her,
     leert `arena.previous_mode = null`.
  3. **Load während Arena:** `reset_arena_after_load()` nutzt
     `arena.previous_mode` / `resume_token.previous_mode`, setzt
     `campaign.mode` auf den Ursprungswert zurück. Fehlt `previous_mode`,
     fällt der Restore **immer** auf `mixed` zurück (nie `preserve`).
     Arena ist **kein** dauerhaft eigener Kampagnenmodus - PvP gilt nur temporär.
- **Arena-Reset nach Load.** `load_deep()` setzt `location='HQ'`,
  deaktiviert aktive Arena-Flags und kippt die Phase auf `completed` (falls ein
  Run lief) oder `idle`. Der Reset wird explizit genannt ("Arena-Zustand auf HQ
  zurückgesetzt."); die letzte Runde bleibt über `arena.previous_mode`
  nachvollziehbar. Lief die Serie noch, erzeugt die Runtime ein
  `arena.resume_token` (Tier, Teamgröße, Modus, `match_policy`, Szenario, `previous_mode`),
  das `!arena resume` im HQ ohne erneute Gebühr reaktiviert.
- **Arena-Persistenzvertrag (Karriere + HQ-safe Checkpoint).**
  Persistiert werden Arena-Karriere und HQ-sichere Sentinel-/Checkpoint-Felder:
  `arena.active=false`, `arena.phase=idle|completed`,
  `arena.queue_state=idle|completed`, `arena.mode`, `arena.tier`,
  `arena.previous_mode`, `arena.resume_token`, `arena.contract_id`,
  `arena.streak`, `arena.pending_rewards`, `arena.banked_rewards`,
  `arena.rewarded_runs_this_contract`, `arena.first_wins`,
  `arena.defeated_types`, `arena.last_reward_episode`,
  `arena.wins_player`, `arena.wins_opponent` und `arena.match_policy`.
  Runtime-only bleiben Live-Queue-/Matchzustände wie
  `searching|matched|staging|active`, Gegnerzustände, Rundentimer,
  Zonen, temporäre Budgets und laufende Matchphysik. Der HQ-Save schreibt
  niemals ein aktives Match, aber immer den vollständigen
  Default-/Checkpoint-Block.
- **Wallets.** `initialize_wallets_from_roster()` stellt sicher, dass jeder
  Eintrag in `characters[]` ein numerisches `wallet`-Feld trägt
  (Toast "Wallets initialisiert (n×)"). Beim Laden bleiben Session-Anker-Wallets
  maßgeblich; Import-Wallets werden per Charakter-ID auf fehlende Einträge
  übertragen. Abweichende Beträge landen in `logs.flags.continuity_conflicts[]`
  und im Trace `merge_conflicts`, während die Anker-Balance Vorrang behält.
- **Self-Reflection.** `logs.flags` ergänzt Gate- und Reset-Felder
  (`foreshadow_gate_m5_seen`, `self_reflection_auto_reset_at`,
  `self_reflection_last_change_reason` usw.) für nachvollziehbare Debrief-Logs.

## HQ-Loop-Contract (Debrief → Freeplay)

Nach jedem Einsatz folgt ein deterministischer HQ-Loop. Diese Reihenfolge ist
**verpflichtend** und wird im Debrief sichtbar dokumentiert. Der Debrief darf
nicht übersprungen werden (siehe Masterprompt §C, Mission-Transition-Pflichtgate):

1. **Score-Screen / Missions-Bewertung** (Erfolg/Teilerfolg/Fehlschlag, Px-Stand).
2. **Auto-Loot** (Loot/Artefakte/Relikte automatisch zählen & loggen).
3. **CU & Wallet-Split** (HQ-Pool aktualisieren, Wallets verteilen).
4. **XP/Skills** (Level-Up/Skill-Picks aktiv abfragen — **genau eine** Wahl pro Stufe; Anti-Stacking-Gate gegen `character.level_history[<lvl>]`).
5. **ITI-Ruf-Update** (formaler Institutsruf, Lizenz-Tier).
6. **`!save`-Angebot** — erst **nach** abgeschlossener Level-Up-Wahl. Ein `!save` **vor** der Wahl wird mit `` `Kodex: Level-Up ausstehend — Save nach Wahl.` `` angehalten.
7. **Freeplay-Anker** — explizites Menü mit **Bar**, **Werkstatt**, **Archiv**
   plus **1 Gerücht** (kurzer Hook) anbieten.

Der Freeplay-Anker wird sichtbar ausgespielt und als normaler HQ-Fortschritt im
Debrief dokumentiert. Nach `!save` kann der Spieler nahtlos weiterspielen oder den Chat schließen und in einem neuen Chat per JSON-paste in die Nullzeit zurückkehren.

### Gruppenregel bei Todesfällen (Core/Rift/Chronopolis)

Im Modus `gruppe` wird bei einem Spieler-Tod die Szene sofort gestoppt. Kodex
stellt dann verbindlich eine Gruppenentscheidung:

1. **Tod bleibt Kanon.** Die Geschichte läuft mit dem Verlust weiter; Debrief
   und Logs markieren den Tod als narrative Konsequenz.
2. **Neu laden.** Die Gruppe öffnet ein neues Chatfenster, lädt den letzten
   **Gruppen-DeepSave** und startet den Einsatz erneut.

Diese Abfrage gilt identisch in Core-, Rift- und Chronopolis-Einsätzen.
Chronopolis besitzt dabei **keinen** Sonder-Respawn und keinen Traum-Reset.

## Team-Split & Team-Merge {#team-split-merge}

### Kanonischer Split-Standard

Split/Merge ist kanonisch für **Core-Parallelpfade** und **separate Rift-Ops**,
sofern pro Branch ein eigenständiger Save geführt wird. Bei
Core-Parallelpfaden ist `continuity.split.family_id` Pflicht. Die SL erstellt
pro Teilgruppe einen eigenen Save:

1. **Characters aufteilen:** Jede Teilgruppe bekommt ihre `characters[]`.
   Session-Anker des neuen Saves = erster Character im Array.
2. **HQ-Pool aufteilen:** `economy.hq_pool` gleichmäßig verteilen
   (oder nach Absprache). Persönliche `wallet`-Werte bleiben beim Character.
3. **Seeds zuweisen:** Jede Teilgruppe bekommt den/die Seeds, die sie spielen
   will. Seed-Status wechselt auf `"active"`. Seeds, die niemand nimmt, bleiben
   `"open"` und kommen in beide Saves.
4. **Trace loggen:** `{"event": "team_split", "note": "..."}` in beiden Saves.
5. **arc-Block kopieren:** Beide Teams tragen das gemeinsame Story-Wissen mit.
6. **campaign.px + px_state:** Px und `px_state` werden in beide Saves kopiert (nicht aufgeteilt).

### Kanonischer Merge (Core + Rift)

Beim Rejoin im HQ werden die Branch-Saves wieder zusammengeführt:

1. **Characters mergen:** Alle `characters[]` in ein Array.
   Session-Anker-Charakter = Index 0 (aus dem Save des ursprünglichen
   Session-Ankers).
2. **HQ-Pool summieren:** `economy.hq_pool` aus beiden Saves addieren.
3. **Seeds: Union:** Alle Seeds beider Saves zusammenführen (closed + open).
4. **Px-State zuerst, dann Wert:** Priorität `consumed > pending_reset > stable`.
   Daraus folgt: `consumed => px=0`, `pending_reset => px=5`,
   `stable => max(px aus stable-Branches, Bereich 0-4)`.
5. **Logs mergen:** Trace-Events, Artifact-Logs und Notes zusammenführen.
6. **arc mergen:** Factions, Questions, Hooks vereinigen. Bei Konflikten: beide behalten.
7. **Transparentes Protokoll:** Die SL zeigt eine Merge-Tabelle, die jede
   Entscheidung nachvollziehbar macht.

### Branch-Importe ohne Split-Protokoll

Parallele Core-Missions-Branches innerhalb derselben Episode bleiben
**kanonisch**, wenn sie dieselbe `continuity.split.family_id` tragen.
Gemischte Split-Pfade ohne gemeinsames Split-Protokoll (z. B. Rift + PvP +
Chronopolis + Abort) laufen als Branch-Import. Es gilt folgender
Präzedenzgraph (deterministisch, Session-Anker):

1. **Globale Kampagne:** Session-Anker bleibt führend für `campaign`, `arc` und globale
   `logs.flags`.
2. **Branch-lokale Progression:** Import nur über Allowlist-Felder
   `wallet`, `rift_merge`, `arena_resume`, `chronopolis_log`, `abort_marker`.
3. **Charakterdaten:** `characters[]` wird über `id` dedupliziert; pro ID
   gewinnt der neueste persönliche Stand. Divergenzen werden als
   `logs.flags.continuity_conflicts[]` protokolliert.
4. **Arena/Resume-Zustand:** Vor HQ-Save immer auf HQ-safe normalisieren
   (`arena.active=false`, `queue_state=idle|completed`, `previous_mode` bereinigt).
5. **Chronopolis-Markt/City-Logs:** bleiben als Nachweis in `logs.market[]`
   und `logs.trace[]`, ohne den Session-Anker-Kampagnenfortschritt zu überschreiben.
6. **Debrief-Outputs:** Konsolidierung in `logs.notes[]` mit Merge-Hinweis.

Zusatzregeln:

- `campaign.px_state` wird beim Import strikt beibehalten; ein bereits
  verbrauchter Px-5-Stand (`consumed`) darf durch Alt-Branches nicht
  wieder als offener Px-5-Cluster erscheinen.
- Die SL muss den Hinweistext ausgeben: _"Nicht-kanonischer Branch-Import:
  Kampagnenfortschritt bleibt beim Session-Anker; persönliche Rückkehrerstände wurden
  übernommen."_
- `logs.flags.imported_saves[]` muss pro Branch den `status` und `reason`
  (`non_canonical_branch`) dokumentieren.

#### Mischpfad-Beispiele (Dokustandard)

- **Rift + PvP → Merge:** Session-Anker-Kampagne bleibt, Rift-Seeds/Wallets werden
  importiert, Arena wird auf `idle|completed` normalisiert.
- **Abort + HQ-Rückkehr → Save → Merge:** Abort-Branch liefert nur
  `abort_marker` + Charakterzustand; kein Episoden-/Missionssprung.
- **Chronopolis-Run + HQ-Branch → Merge:** Chronopolis-Ausgaben/Markt bleiben
  als Log-Nachweis, Kampagnenfortschritt folgt weiterhin dem Session-Anker.

#### Klarstellung: Mid-Episode-Trennung (5er → 3/2)

Wenn sich ein Team nach Mission 1-2 innerhalb derselben Episode trennt und die
2er-Gruppe in einem neuen Chat weiterläuft, gilt ohne Branch-Protokoll:

1. **Beide Pfade sind spielbar:** 3er- und 2er-Gruppe können jeweils normal
   weiterspielen.
2. **Kanon pro aktiver Runde:** In jedem Chat ist der dort aktive Session-Anker
   der Einstiegspunkt.
3. **Rejoin/Merge:** Treffen die Gruppen später wieder zusammen (HQ), bleibt der
   Kampagnenrahmen am Session-Anker; persönliche Rückkehrerstände und
   Kontinuitäts-Echos werden übernommen.
4. **Kein verdeckter Episoden-Sprung:** Solisten starten nicht automatisch
   eine neue Episode; sie folgen dem aktiven Session-Anker ihres Chats.
5. **Mission-zu-Mission-Hopper:** Häufige Anker-Wechsel sind erlaubt; pro Chat
   gilt ein Session-Anker plus Import persönlicher Wahrheit.

## Koop-Debrief & Wallet-Split {#koop-wallet-split}

Nach jeder Mission folgt auf den Belohnungsblock automatisch der Koop-Abschnitt.
`apply_wallet_split()` spiegelt das Ergebnis in `characters[].wallet` und erzeugt
die Debrief-Zeilen.

### Hazard-Pay & HQ-Pool

- Enthält `outcome` ein `hazard_pay`-Feld (oder `economy.hazard_pay`), bucht die
  Runtime den Betrag zuerst auf `economy.hq_pool` und loggt `Hazard-Pay: … CU
priorisiert`.
- Anschließend meldet `apply_wallet_split()` den HQ-Stand als
  `HQ-Pool: <Betrag> CU verfügbar`. Restbeträge erscheinen in Klammern
  (`Rest 150 CU im HQ-Pool`).
- Reihenfolge und Restsummen bleiben deterministisch: Die Debrief-Zeile
  `Wallet-Split (n×)` listet IDs in Roster-Reihenfolge, verteilt Rundungsreste
  gleichmäßig von oben nach unten und schließt mit einem einzigen Hinweis auf
  den verbleibenden HQ-Pool (`Rest … CU im HQ-Pool`).

### Standard- und Sonderaufteilungen

1. **Standardaufteilung.** Ohne Vorgaben verteilt die KI-SL die Auszahlung
   gleichmäßig (`Wallet-Split (n×): Ghost +200 CU | …`).
2. **Solo→Koop.** Beim Moduswechsel initialisiert
   `initialize_wallets_from_roster()` leere Wallets für alle `characters[]`
   und verschiebt Solo-Guthaben in den HQ-Pool.
3. **Spezialschemata.** Sonderregeln kommen über `economy.split`/`wallet_split`.
   Prozentwerte (`percent`, `percent_share`) nutzt die KI-SL als 0-1 bzw. 0-100 %.
   Verhältnisangaben (`ratio`, `weight`, `share_ratio`, `portion`) bleiben
   relative Anteile. Nicht zugewiesene CU verbleiben im HQ-Pool.
4. **Dialogführung.** Kodex nennt Standard und Alternativen (_"Standardaufteilung
   je 200 CU …"_) und dokumentiert Entscheidungen in Debrief oder
   Einsatzprotokoll.

### Persistenz & IDs

- `characters[].wallet` speichert Balances pro Agenten-ID. Fehlt eine ID,
  erzeugt die KI-SL einen Slug (`agent-nova`).
- Änderungen an Callsigns aktualisieren nur den Anzeigenamen; das Guthaben bleibt
  über die ID erhalten.
- Ohne lokale Runtime müssen KI-Spielleitungen dieselben Schritte manuell
  beschreiben und die Werte in den Saveblock übertragen, damit Koop-Teams ihre
  CU-Historie nachvollziehen können.

**Legacy-Normalisierung (ohne runtime.js)**

- Encounter mit Alt-Saves laufen vollständig im KI-SL - es gibt keine
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
  Agenten zur Grundausstattung. Fehlt `psi_buffer` in `character{}`, `team{}`
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
  "ui": { "suggest_mode": true, "gm_style": "verbose", "action_mode": "uncut" },
  "character": { "modes": ["klassik", "mission_focus", "covert_ops_technoir", "suggest"] },
  "logs": { "hud": ["· SUG", "Mission-Fokus"] }
}
```

Der Save hält sowohl die aktivierten Erzählmodi (`modes[]`) als auch den UI-Flag
`suggest_mode` und den Action-Contract. Beim Laden setzt die KI-SL `modus suggest`
und spiegelt das HUD-Tag `· SUG` samt Mission-Fokus-Badge.

Das UI speichert außerdem `dice.debug_rolls` (Default `true` für offene Würfel).
Neue Sessions starten dadurch automatisch mit sichtbaren Würfen, bis ihr per
`/roll hidden|manual` umschaltet.

## Charakterbogen-Ansicht (`!bogen`) {#charakterbogen-ansicht}

`!bogen` (Alias `!charakterbogen`) erzeugt eine **lesbare Pen-&-Paper-Übersicht**
mit Team-/Charakterwerten statt JSON. Der Befehl ist für den Live-Chat gedacht,
wenn die Gruppe während einer Mission den aktuellen Stand als Bogen sehen will.

**Inhalt der Ausgabe**

- Kampagnenkopf (Episode/Mission)
- Team-Ökonomie (`economy.hq_pool`)
- pro Charakter: Name, Lvl, Rolle/Klasse, LP, Stress, Psi-Heat, Attribute, Wallet, Ausrüstung

> **Wichtig für OpenWebUI / reinen Chatbetrieb:** Der kanonische Pfad ist
> `!save` im HQ (JSON-Export) und Laden über JSON-Copy-Paste. `Spiel laden` ist
> optional und dient nur als Startsignal für den Load-Dialog.

## Makros im Überblick {#makros-im-ueberblick}

- `StartMission(total=12|14, type="core"|"rift")` - initiiert den Missionsfluss nach dem Load.
- `DelayConflict(4)` - verschiebt Konfliktszenen bis zur vierten Szene.
- `ShowComplianceOnce()` - bleibt als leerer Kompatibilitäts-Hook bestehen und
  setzt keine Flags mehr. `SkipEntryChoice()` markiert parallel
  `flags.runtime.skip_entry_choice=true`; die Runtime übernimmt das Flag
  unverändert in den Einsatz.
- `Chronopolis-Warnung` - `start_chronopolis()` erzeugt einmalig einen
  In-World-Warnhinweis und setzt `logs.flags.chronopolis_warn_seen=true`, damit
  der Hinweis nach dem ersten Besuch stumm bleibt.
- `ClusterCreate()` - legt bei Paradoxon 5 neue Rift-Seeds an.
- `ClusterDashboard()` - zeigt aktive Seeds mit Schweregrad und optionaler Deadline.
- `launch_rift(id)` - startet eine Rift-Mission aus einem Seed (nur nach Episodenende).
- `resolve_rifts(ids)` - markiert Seeds als geschlossen und passt Belohnungen an.
- `seed_to_hook(id)` - liefert drei Kurz-Hooks als Einsprungpunkte für die nächste Sitzung.

### Paradoxon-Index & Rift-Seeds (Kernlogik) {#paradoxon-index}

- Der Paradoxon-Index misst die temporale Resonanz der Zelle — ein
  **Belohnungssystem** mit deterministischer Progression.

**Px-Anstieg (fix gekoppelt an TEMP):**

|  TEMP | Px-Zuwachs             |
| ----: | :--------------------- |
|   1–2 | +1 Px alle 2 Missionen |
|   3–5 | +1 Px pro Mission      |
|   6–8 | +2 Px pro Mission      |
|  9–11 | +2 Px pro Mission      |
| 12–14 | +3 Px pro Mission      |

Der Scope ist modusabhängig und nutzt immer `campaign.px` als Quelle:

- **solo / npc-team:** Der Px-Wert gehört zum jeweiligen Run.
- **gruppe:** Der Px-Wert ist kampagnenweit gemeinsam und folgt dem
  Session-Anker-Save.

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
- Ambige Saves: "Kodex-Archiv: Profilpluralität erkannt. Sollen _Einzelprofil_
  oder _Teamprofil_ geladen werden?"

### Kanonisches Save-Exportformat (v7, einziges Format)

Das **einzige** kopierfähige `!save`-Template steht im Masterprompt §F (`meta/masterprompt_v6.md`).
Diese Datei dokumentiert Feldbedeutung, SaveGuard, Import/Migration, Split/Merge und Budgets.

> **IMPORT-ONLY / NICHT KOPIEREN / KEIN `!save`-BEISPIEL:**
> JSON-Blöcke in dieser Datei sind Legacy-/Migrationsbeispiele oder Teilbeispiele für Spezialfälle.
> Sie dürfen **nicht** als alternatives Exportmuster für neue v7-`!save`-Ausgaben verwendet werden.

Arena-Persistenzvertrag (HQ-safe):

Vertragsanker (rein deklarativ, **kein** kopierfähiges JSON):

- `"v": 7`
- `"characters": []` als einziger Charaktercontainer
- `"wallet": 0` liegt je Charakter unter `characters[]`
- `"economy": { "hq_pool": 0 }`
- `"arc": { "factions": {}, "questions": [], "hooks": [] }`
- `"history": { "background": "", "milestones": [] }`
- `"carry": []`
- `"quarters_stash": []`
- `"vehicles": { "epoch_vehicle": { "id": "VEH-XXXX" } }`
- Feldanker `"epoch_vehicle"` bleibt Pflicht im Fahrzeugcontainer
- Wallet pro Charakter: `characters[].wallet`
- HQ-Pool: `economy.hq_pool`
- Story-Hub: `arc`
- Charakterpersistenz umfasst `history`, `carry`, `quarters_stash`, `vehicles`, `vehicles.epoch_vehicle`


- Persistiert werden **ausschließlich** HQ-sichere Sentinel- und Karrierefelder:
  `active`, `phase`, `queue_state`, `mode`, `tier`, `previous_mode`, `resume_token`,
  `contract_id`, `streak`, `pending_rewards`, `banked_rewards`,
  `rewarded_runs_this_contract`, `first_wins`, `defeated_types`,
  `last_reward_episode`, `wins_player`, `wins_opponent`, `match_policy`.
- **Nicht** persistiert wird laufende Matchphysik (laufender Run, Zonen-/Staging-Daten,
  temporäre Kampfzustände, Tick/Frame-nahe Matchdaten).
- SaveGuard bleibt strikt: Während Queue/Match/Run sind Save-Versuche gesperrt.
  Erst nach Rückkehr in die HQ-Arena-Lounge wird der Arena-Block auf Sentinelzustand
  normalisiert (`active=false`, `phase/queue_state=idle|completed`) und exportiert.

#### Arc-Objekt (`arc`)

`arc` sammelt Story-Hub-Einträge und bleibt im v7-Kanon der einzige Arc-Pfad:

- **`factions{}`** – Fraktionsstatus inkl. optionaler Interventionsmetadaten.
- **`questions[]`** – offene Forschungs-/Storyfragen.
- **`hooks[]`** – aktive Story-Hooks für kommende HQ-/Missionsübergänge.

### Legacy-Importpfade (kein Runtime-Standard)

- Historische Felder wie `save_version`, `party.characters[]`, `team.members[]`,
  `economy.cu`, `economy.wallets`, `zr_version`, `campaign.mission_in_episode`,
  `characters[].attributes`, `arc.open_seeds`, `arc.open_questions`,
  `arc.timeline` oder `arc_dashboard` gelten nur als
  **Import-Bridge**.
- `load_save()` migriert Legacy-Daten in das v7-Zielmodell (`v`, `characters[]`,
  `economy.hq_pool`, `arc.*`).
- `save_game()` exportiert ausschließlich das v7-Schema.
- V6-Beispiele in diesem Dokument dienen ausschließlich der Migrationserklärung
  und sind **kein** alternatives Speicherformat.
