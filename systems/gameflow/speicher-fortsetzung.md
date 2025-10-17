---
title: "ZEITRISS 4.2.2 – Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)"
version: 4.2.2
tags: [system]
---

# ZEITRISS 4.2.2 – Modul 12: Speicher- und Fortsetzungssystem (überarbeitet)

## HQ-JSON-Save {#json-schluesselfelder}
> **Guard:** Speichern nur in der HQ-Phase; Pflichtwerte sind deterministisch.
> Chat-Befehle: `!save`, `!load`, optional `!autosave hq`, `!suspend`, `!resume`.
> Einziger Save-Typ: Deepsave (HQ-only).

**SaveGuard (Pseudocode)**
{# LINT:HQ_ONLY_SAVE #}
```pseudo
assert state.location == "HQ", "Speichern nur im HQ. Missionszustände sind flüchtig und werden nicht persistiert."
assert state.character.attributes.SYS_used == state.character.attributes.SYS_max
assert state.character.stress == 0 und state.character.psi_heat == 0
assert not state.get('timer') und not state.get('exfil_active') und not campaign.exfil.active
required = [
  "character.id",
  "character.attributes.SYS_max",
  "character.attributes.SYS_used",
  "character.stress",
  "character.psi_heat",
  "character.cooldowns",
  "campaign.px",
  "economy",
  "economy.wallets",
  "logs",
  "logs.hud",
  "logs.artifact_log",
  "logs.market",
  "logs.offline",
  "logs.kodex",
  "logs.alias_trace",
  "logs.squad_radio",
  "logs.fr_interventions",
  "logs.psi",
  "logs.flags",
  "ui",
  "arena"
]
assert serializer_bereit(required)
```

Speichern ist ausschließlich in der HQ-Phase zulässig. Alle Ressourcen sind
dort deterministisch gesetzt:

`campaign.exfil{active, armed, hot, ttl, sweeps, stress, anchor, alt_anchor}`
spiegelt den Zustand des Exfil-Fensters. Solange `campaign.exfil.active`
oder `state.exfil.active` wahr ist, blockiert der Serializer den HQ-Save mit
„SaveGuard: Exfil aktiv – HQ-Save gesperrt.“. Sobald die Crew ins HQ
zurückkehrt, setzt die Runtime alle Exfil-Felder automatisch zurück.

In-Mission-Ausstieg ist erlaubt, aber es erfolgt kein Save; Ausrüstung darf
übergeben werden, nächster Save erst im HQ.

```json
{
  "save_version": 6,
  "zr_version": "4.2.2",
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
    "foreshadow": [],
    "fr_interventions": [],
    "flags": {
      "runtime_version": "4.2.2",
      "compliance_shown_today": false,
      "chronopolis_warn_seen": false
    }
  },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {}
  },
  "ui": {
    "gm_style": "verbose",
    "intro_seen": false,
    "suggest_mode": false,
    "contrast": "standard",
    "badge_density": "full",
    "output_pace": "normal"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
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

- Pflichtfelder: `character.id`, `character.attributes.SYS_max`,
  `character.attributes.SYS_used`, `character.stress`, `character.psi_heat`,
  `character.cooldowns`, `campaign.px`, `economy` (inklusive `wallets{}`),
  `logs` (inklusive `hud`, `artifact_log`, `market`, `offline`, `kodex`,
  `alias_trace`, `squad_radio`, `foreshadow`, `fr_interventions`, `psi`,
  `flags`), `ui` und `arena`.
- Optionales Feld: `modes` – Liste aktivierter Erzählmodi.
- Im HQ sind `character.attributes.SYS_used`, `character.stress` und
  `character.psi_heat` deterministisch: `SYS_used == SYS_max`, `stress = 0`,
  `psi_heat = 0`. Das Speichern erfasst diese Werte, damit GPT den
  Basiszustand prüfen kann.
- GPT darf keine dieser Angaben ableiten oder weglassen. Der Serializer setzt
  fehlende Pflichtblöcke automatisch auf sichere Defaults (`economy.cu = 0`,
  leere Logs mit `logs.flags`, `ui.gm_style = "verbose"`).
- `party.characters[]` ist die kanonische Gruppenstruktur. Legacy-Saves mit
  `Charaktere` (DE) oder reinen Arrays werden beim Import auf diese Form
  normalisiert; Exporte und Debriefs verwenden ausschließlich die EN-Schreibweise.

### Cross-Mode Import – Solo → Koop/Arena {#cross-mode-import}

1. **Solo-Save laden.** `economy.wallets{}` ist zunächst leer; `party.characters[]`
   enthält nur den Protagonisten. Nach dem Laden läuft `initialize_wallets()`
   automatisch und legt leere Wallets für alle aktiven Agent:innen an.
2. **Koop- oder Gruppeneinsatz starten.** Im Debrief erzeugt `apply_wallet_split()`
   für jedes Teammitglied eine Auszahlung und protokolliert den Vorgang als
   `Wallet-Split` in den HUD-Logs. `logs.psi[]` dokumentiert parallel den zuvor
   aktiven Modus (`mode_previous`) für die Cross-Mode-Evidenz.
3. **Arena aktivieren.** `arenaStart()` setzt `arena.policy_players[]`,
   `arena.previous_mode` und `arena.phase='active'`. Während der Serie blockiert
   der HQ-Save-Guard (`SaveGuard: Arena aktiv`). Beim Exit schreibt die Runtime
   `arena.phase='completed'`, synchronisiert Px (+1 bei Sieg) und erlaubt wieder
   HQ-Saves.

### Accessibility-Preset (zweites Muster) {#accessibility-save}

```json
{
  "save_version": 6,
  "zr_version": "4.2.2",
  "location": "HQ",
  "phase": "core",
  "character": {
    "id": "CHR-7777",
    "name": "Jade",
    "rank": "Specialist",
    "stress": 0,
    "psi_heat": 0,
    "cooldowns": {},
    "attributes": {"SYS_max": 6, "SYS_used": 6}
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
      "runtime_version": "4.2.2",
      "compliance_shown_today": true,
      "chronopolis_warn_seen": true,
      "offline_help_count": 1,
      "offline_help_last": "2025-10-28T19:42:00Z"
    }
  },
  "arc_dashboard": {"offene_seeds": [], "fraktionen": {}},
  "ui": {
    "gm_style": "verbose",
    "intro_seen": true,
    "suggest_mode": false,
    "contrast": "high",
    "badge_density": "compact",
    "output_pace": "slow"
  },
  "arena": {
    "active": false,
    "phase": "idle",
    "mode": "single",
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
läuft im `slow`-Takt. Diese Werte bleiben erhalten, bis Nutzer:innen sie im HQ
zurücksetzen.

## Laden & HQ-Rückkehr {#load-flow}

### Ablauf nach `!load`

1. **Save posten.** `!load` erwartet den HQ-Deepsave als JSON und quittiert die
   Eingabe mit „Kodex: Poste Speicherstand als JSON.“
2. **Deserializer starten.** `load_deep()` in `runtime.js` migriert Legacy-Felder
   in die v6-Struktur, prüft Pflichtblöcke und setzt `state.location='HQ'`.
3. **Rückblende & HUD.** `scene_overlay()` rendert nach dem Laden den HUD-Block
   „EP·MS·SC/Total·Px·SYS“. Die Runde springt ohne Nachfrage direkt zum HQ-
   beziehungsweise Briefing-Einstieg.
4. **Compliance-Spiegel.** `show_compliance_once()` ruft das Toolkit-Makro
   `ShowComplianceOnce()` (Alias `StoreCompliance()`) auf und synchronisiert
   `campaign.compliance_shown_today` mit `logs.flags.compliance_shown_today`.

{# LINT:FS_RESET_OK #}

> **Laufzeitabgleich:** Guard-Texte und HUD-Ausgabe entsprechen den Routinen
> `load_deep()` und `scene_overlay()` in `runtime.js` (ZR_VERSION 4.2.2).

### Kompatibilität & Guards

- Semver-Toleranz: Lädt, wenn `major.minor` der gespeicherten `zr_version` dem
  aktuellen `ZR_VERSION` entspricht; Patch-Level sind egal.
- Version-Mismatch liefert `Kodex-Archiv: Datensatz vX.Y nicht kompatibel mit
  vA.B. Bitte HQ-Migration veranlassen.`
- `campaign.exfil.active` oder `state.exfil.active` blockieren den HQ-Save mit
  „SaveGuard: Exfil aktiv – HQ-Save gesperrt.“
- Pflichtblöcke dürfen nicht geschätzt werden; der Serializer ersetzt fehlende
  Strukturen mit sicheren Defaults (Wallets `{}`, Logs als leere Arrays,
  `ui.gm_style="verbose"`).

### Persistente Debrief-Spiegel

- **Runtime-Flags.** `logs.flags.runtime_version` hält die erzeugende Version
  fest. Der Debrief bündelt sie unter `Runtime-Flags: …` inklusive
  Compliance-Status, Chronopolis-Warnung sowie Offline-Hilfe-Zähler plus
  Timestamp.
- **Chronopolis & Markt.** `log_market_purchase()` schreibt Einkäufe nach
  `logs.market[]` (ISO-Timestamp, Artikel, Kosten, Px-Klausel).
  `render_market_trace()` erzeugt `Chronopolis-Trace (n×): …`.
- **Offline & Foreshadow.** `sanitize_offline_entries()` begrenzt
  `logs.offline[]` auf zwölf Einträge (Trigger, Gerät, Jammer, Reichweite,
  Relais, Szene/Episode). `render_offline_protocol()` fasst sie als
  `Offline-Protokoll (n×): …` zusammen. `normalize_save_v6()` dedupliziert
  `logs.foreshadow[]` (Tag, Kurztext, Szene, First/Last-Seen);
  Debriefs spiegeln `Foreshadow-Log (n×): …`.
- **Fraktionen & Funk.** `log_intervention()` protokolliert bis zu 16
  `logs.fr_interventions[]` (Ergebnis, Fraktion, Szene, Mission, Zusatzfelder)
  und spiegelt sie ins Arc-Dashboard; `render_alias_trace_summary()` fasst
  `logs.alias_trace[]` zu `Alias-Trace (n×): …` zusammen. Funkmeldungen landen
  via `log_squad_radio()` in `logs.squad_radio[]`; der Debrief liefert
  `Squad-Radio (n×): …`.
- **HQ-Rituale.** `campaign.hq_moments_used: string[]` dokumentiert Buffs
  (FOCUS/BASTION/SPARK/CALM/PULSE). Fehlt das Feld, setzt der Serializer `[]`;
  Debriefs nennen „HQ-Moments (n×)“ entsprechend.
- **Arena & Psi.** `ensure_arena()` konserviert PvP-Status, Phasen,
  Serienstände, Budget-Limits sowie `phase_strike_tax`. Parallel hält
  `logs.psi[]` `phase_strike_tax` und `mode_previous` fest, damit
  `render_psi_summary()` den Cross-Mode-Kontext liefert.
- **Wallets.** `initialize_wallets_from_roster()` erzeugt fehlende Einträge in
  `economy.wallets{}` (Toast „Wallets initialisiert (n×)“). Saves führen immer
  ein Objekt – ggf. `{}`.
- **Self-Reflection.** `logs.flags` ergänzt Gate- und Reset-Felder
  (`foreshadow_gate_m5_seen`, `self_reflection_auto_reset_at`,
  `self_reflection_last_change_reason` usw.) für nachvollziehbare Debrief-Logs.

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

### Standard- und Sonderaufteilungen

1. **Standardaufteilung.** Ohne Vorgaben verteilt der GPT die Auszahlung
   gleichmäßig (`Wallet-Split (n×): Ghost +200 CU | …`).
2. **Solo→Koop.** Beim Moduswechsel initialisiert
   `initialize_wallets_from_roster()` leere Wallets für alle `party.characters[]`
   und verschiebt Solo-Guthaben in den HQ-Pool.
3. **Spezialschemata.** Sonderregeln kommen über `economy.split`/`wallet_split`.
   Prozentwerte (`percent`, `percent_share`) nutzt GPT als 0–1 bzw. 0–100 %.
   Verhältnisangaben (`ratio`, `weight`, `share_ratio`, `portion`) bleiben
   relative Anteile. Nicht zugewiesene CU verbleiben im HQ-Pool.
4. **Dialogführung.** Kodex nennt Standard und Alternativen (_„Standardaufteilung
   je 200 CU …“_) und dokumentiert Entscheidungen in Debrief oder
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

- Encounter mit Alt-Saves laufen vollständig im LLM – es gibt keine
  JavaScript-Hooks im Produktivbetrieb. Deshalb erstellt die Spielleitung bei
  Legacy-Daten den `character{}`-Block manuell, bevor irgendetwas geladen oder
  geprüft wird:
  1. Alle vorhandenen Stammdaten (`id`, `name`, `rank`, `callsign`, `lvl`, `xp`)
     aus Root-Feldern in `character{}` kopieren und anschließend die
     Wurzelkopien löschen.
  2. `stress`, `psi_heat`, `psi_heat_max` und `cooldowns{}` ebenso in den
     `character`-Block übernehmen; `cooldowns{}` immer als Objekt führen.
  3. `character.attributes{SYS_max,SYS_used}` aus `sys`/`sys_max` bzw.
     `sys_used` bilden und dabei bestehende Werte aus `attributes{}` nur
     ergänzen – niemals überschreiben.
  4. Wenn ein Legacy-Save `modes[]` oder `self_reflection` direkt an der
     Wurzel notiert hatte, landen sie jetzt ebenfalls in `character{}`.
- Abschließend kontrollierst du die Standard-Flags: **Psi-Puffer** gehören bei allen Agent:innen zur Grundausstattung. Fehlt `psi_buffer` in `character{}`, `team{}` oder `party.characters[]`, ergänze `true`.
- Danach verhält sich der Save wie ein natives v6-Dokument. Guards wie der
  HQ-Serializer, Log-Sanitizer und das Semver-Gate operieren erst auf dieser
  bereinigten Struktur.

Beim Laden liest die Spielleitung `modes` aus und ruft für jeden
Eintrag `modus <name>` auf. So bleiben etwa Mission-Fokus oder
Transparenz-Modus nach einem Neustart erhalten.

## Session-Suspend (Temporärer Snapshot) {#session-suspend}

> **Ziel:** Ihr könnt eine laufende Sitzung pausieren, ohne den HQ-Deepsave zu verletzen.
> `!suspend` schreibt einen flüchtigen Snapshot, `!resume` setzt ihn exakt einmal fort.

Der Suspend-Snapshot friert den laufenden Einsatz für eine Pause ein.
Er lebt außerhalb der regulären Save-Pipeline und verfällt nach 24 Stunden.
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
- Nach der Rückkehr ins HQ erwartet Euch weiterhin `!save`, damit Episoden-Belohnungen gesichert bleiben.
- Bei Ablauf des Snapshots informiert das HUD: „Suspend-Fenster verstrichen. Bitte HQ-Deepsave laden.“
- Der Snapshot konserviert Initiative-Reihenfolge und HUD-Timer, damit Konfliktszenen nach `!resume`
  lückenlos weiterlaufen.

**HUD-Feedback**

- Nach `!suspend`: Toast `HUD → Session eingefroren · Ablauf <24h`.
- Nach `!resume`: Overlay `Session fortgesetzt · Szene X/Y`.
- Nach Ablauf: Benachrichtigung `Suspend verworfen · HQ-Save nötig`.

**Best Practices**

- Nutzt `!suspend`, wenn Ihr mitten im Konflikt aufhören müsst, aber den Flow bewahren wollt.
- Legt direkt vor einer Pause eine Mini-Rekap an, damit `!resume` den Einstieg filmisch anschließen kann.
- Verlasst Euch nicht dauerhaft darauf: Der Snapshot ersetzt keinen Story-Fortschritts-Save im HQ.
## Makros im Überblick {#makros-im-ueberblick}

- `StartMission(total=12|14, type="core"|"rift")` – initiiert den Missionsfluss nach dem Load.
- `DelayConflict(4)` – verschiebt Konfliktszenen bis zur vierten Szene.
- `ShowComplianceOnce()` – blendet den täglichen Compliance-Hinweis ein und soll
  `logs.flags.compliance_shown_today=true` setzen. Das automatische Markieren von
  `flags.runtime.skip_entry_choice=true` muss noch in den verfügbaren Toolkit-
  bzw. Makro-Pfaden implementiert werden, da `runtime.js` nicht geladen wird.
- `Chronopolis-Warnung` – `start_chronopolis()` blendet das einmalige Warn-Popup
  ein und setzt `logs.flags.chronopolis_warn_seen=true`, damit die Sequenz nach
  dem ersten Besuch stumm bleibt.
- `ClusterCreate()` – legt bei Paradoxon 5 neue Rift-Seeds an.
- `ClusterDashboard()` – zeigt aktive Seeds mit Schweregrad und optionaler Deadline.
- `launch_rift(id)` – startet eine Rift-Mission aus einem Seed (nur nach Episodenende).
- `resolve_rifts(ids)` – markiert Seeds als geschlossen und passt Belohnungen an.
- `seed_to_hook(id)` – liefert drei Kurz-Hooks als Einsprungpunkte für die nächste Sitzung.

### Paradoxon-Index & Rift-Seeds (Kernlogik) {#paradoxon-index}

- Der Paradoxon-Index misst die Resonanz der Zelle mit dem Zeitstrom.
- Bei Stufe 5 löst `ClusterCreate()` 1–2 neue Rift-Seeds aus und markiert den
  Px-Reset als „anhängig“.
- Rift-Seeds sind erst nach Episodenende spielbar.
- Nach der Rift-Phase setzen Index und Resonanz auf 0. Der Serializer spiegelt
  dies im Debrief (`px_reset_confirm=true`) und das HUD bestätigt den Reset zu
  Beginn der nächsten Mission.

### Legacy-Kompatibilität (Gear-Alias)

> Hinweis für die Spielleitung: Beim Laden interpretiert ihr alte oder abweichende Gear-Bezeichnungen still
> auf die neuen Namen. Speichern nutzt stets die kanonischen Begriffe.

**Alias-Beispiele (erweiterbar):**
- "Kodex-Armbandverstärker" → **Comlink-Boostermodul (Ear-Clip)**
- "Multi-Tool-Armband" → **Multi-Tool-Handschuh**

### Immersiver Ladevorgang (In-World-Protokoll) {#immersives-laden}

- Kollektive Ansprache im Gruppenmodus („Rückkehrprotokoll für Agententeam …“).
- Synchronisierungs-Hinweis („Kodex synchronisiert Einsatzdaten aller Teammitglieder …“).
- Kurze Rückblende der letzten Ereignisse aus Sicht der Beteiligten.
- Individuelle Logbucheinträge sind erlaubt (ein Satz pro Char).

> **Kodex-Archiv** – Rückkehrprotokoll aktiviert.
> Synchronisiere Einsatzdaten: **Alex** (Lvl 3), **Mia** (Lvl 2).
> Letzte Einsätze konsolidiert. Paradoxon-Index: █░░░░ (1/5).
> Willkommen im HQ. Befehle? (Briefing, Shop, Training, Speichern)

### Abweichende oder fehlerhafte Stände (In-World-Behandlung)

- Leichte Formatfehler: als Kodex-Anomalie melden und in-world nachfragen.
- Inkonsistenzen: als Anomalie melden und einen Vorschlag zur Bereinigung anbieten.
- Unbekannte oder veraltete Felder: still ignorieren oder als Archivnotiz kennzeichnen.
- Semver-Mismatch: „Kodex-Archiv: Datensatz vX.Y nicht kompatibel mit vA.B. Bitte HQ-Migration veranlassen.“
- Ambige Saves: „Kodex-Archiv: Profilpluralität erkannt. Sollen *Einzelprofil* oder *Teamprofil* geladen werden?“

### Kanonisches DeepSave-Schema (Kurzfassung)

```json
{
  "zr_version": "4.2.2",
  "save_version": 6,
  "location": "HQ",
  "phase": "core",
  "campaign": { "episode": 1, "mission_in_episode": 2, "scene": 0, "px": 1 },
  "character": {
    "id": "CHR-XXXX",
    "name": "Agent Name",
    "level": 3,
    "attributes": { "STR": 5, "GES": 10, "INT": 4, "CHA": 4, "TEMP": 2, "SYS_max": 4, "SYS_used": 4 },
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
  "economy": { "cu": 0 },
  "logs": { "missions": [], "blacklab": [] },
  "ui": { "gm_style": "verbose" },
  "arc_dashboard": {
    "offene_seeds": [],
    "fraktionen": {},
    "fragen": []
  }
}
```

> Gruppen-Save analog mit `party.characters[]`. Kein zweites Schema mit anderen Feldnamen.

#### Arc-Dashboard-Objekt

`arc_dashboard` sammelt alle Story-Hub-Einträge aus dem HQ-Dashboard. Das Feld ist optional, wird
aber vom Serializer automatisch nachgezogen und strukturiert:

- **`offene_seeds[]`** – Liste aktiver Missionsansätze. Jedes Element ist ein Objekt (z. B. mit
  `id`, `titel`, `status`, `deadline`).
- **`fraktionen{}`** – Wörterbuch mit Fraktionsschlüsseln; Werte sind Objekte für Ruf, Haltung oder
  letzte Aktionen. Die Runtime ergänzt `last_intervention`, `last_result`, `last_updated` sowie
  `interventions[]` (max. sechs Snapshots aus `logs.fr_interventions[]` inklusive Wirkung/Notiz),
  sodass HQ-Dashboard, Kampagnenlog und Runtime denselben Stand anzeigen.
- **`fragen[]`** – Offene Forschungs- oder Storyfragen als kurze Strings oder Objekte.

Beim Laden normalisiert `load_deep()` das Objekt, entfernt Nullwerte und stellt sicher, dass alle
Listen echte Arrays sind. Unbekannte Zusatzfelder bleiben erhalten.

### Legacy-Aliase & Normalisierung

- `party.characters[]` ist die verbindliche Quelle für Gruppenroster. Laufzeit und Serializer lesen
  ausschließlich daraus.
- Historische Felder (`team.members[]`, `team.roster[]`, `group.characters[]`, `party.members[]`,
  `npc_team[]`) werden beim Laden automatisch nach `party.characters[]` gespiegelt. Doppelte Einträge
  erkennt `load_deep()` anhand von IDs, Callsigns oder Namen und entfernt sie.
- Beim Speichern repliziert der Serializer den bereinigten Cast zusätzlich nach `team.members[]`, um
  Kompatibilität mit älteren Tools zu bewahren – ohne voneinander abweichende Arrays. `team.members[]`
  ist somit immer eine 1:1-Kopie des kanonischen `party.characters[]`. GPT ergänzt neue Koop-Mitglieder
  ausschließlich im `party`-Block; `team.members[]` wird nur vom Serializer gespiegelt, damit Saves
  aus Solo- und Koop-Läufen keine widersprüchlichen Listen mehr besitzen.

- Einführung und Zielsetzung
- Einzelspieler-Speicherstände – Bewährte Logik beibehalten
- Gruppen-Spielstände – Neue Unterstützung für Teams
- Zeitlinien-Tracker und Paradoxon-Index
- Immersiver Ladevorgang: Rückblenden und Anschluss in der Erzählung
- Umgang mit fehlerhaften oder abweichenden Speicherständen
- Spielleitung bleibt in-world (Immersion der Spielleitung)
- Praxis-Beispiele für Speicherblöcke (Solo & Gruppe)
- Fazit

## Einführung und Zielsetzung

Das Speicherstand- und Fortsetzungssystem von **ZEITRISS 4.2.2** wird in Modul 12 vollständig
überarbeitet. Ziel ist es, eine klare, GPT-kompatible Speicher- und Fortsetzungsmechanik zu
gewährleisten, die langfristiges Spielen mit einer hohen Spielerzahl unterstützt – **ohne die
Immersion zu beeinträchtigen**. Die grundlegende **Save/Load-Logik** bleibt erhalten, wird aber
durch neue Funktionen erweitert. Entwickler:innen erhalten damit ein robustes, transparentes und
flexibles Speichersystem für Einzel- und Gruppenspiele mit GPT als Spielleitung.

**Wichtige Schwerpunkte der Überarbeitung sind unter anderem:**

- **Integration eines Zeitlinien-Trackers & Paradoxon-Index:** Jede Stabilisierung eines
  historischen Ereignisses wird im Speicher protokolliert (ID, Epoche,
  Kurzbeschreibung und ein Stabilitätswert von 3 bis 0). Erreicht ein Eintrag den
  Wert 3, steigt der Paradoxon-Index um +1.
- **Trennung von Einzelspieler- und Gruppen-Spielständen:** Klare Definition, wie Einzelcharakter-
  Speicherstände vs. Gruppenspielstände aufgebaut und gehandhabt werden.
- **Standardisiertes, maschinenlesbares Format (JSON) mit narrativer Einbettung:** Einführung eines
  einheitlichen Formats mit allen notwendigen Feldern (Name, Attribute, EP, Talente, Inventar, Kodex-
  Wissen etc.), damit der KI-Spielleiter (GPT) die Daten fehlerfrei einlesen kann. Das Format wird
  **In-World** präsentiert (etwa als Kodex-Archiv), sodass die Technik für Spieler unsichtbar bleibt.
- **Integration des Gruppen-Spielsystems:** Mechaniken zum Import vorhandener Einzelcharaktere in
  eine Gruppe, Export einzelner Gruppenmitglieder sowie nahtloses Hinzufügen oder Entfernen von
  Spielern aus laufenden Gruppen.
- **Fortsetzungs-Logik für GPT:** Formatregeln sorgen dafür, dass GPT den Speicherblock bei jedem
  Laden sicher erkennt, korrekt interpretiert und die Geschichte konsistent fortsetzt.
- **Automatische Rückblenden & Anschluss an vorherige Mission:** Ingame-Mechanismen (Logbuch, Déjà-
  vu, Kodex-Archiv) ermöglichen eine kurze Zusammenfassung der letzten Ereignisse – jetzt auch aus
  Sicht aller Gruppenmitglieder – beim Laden eines Spielstands, um den Übergang in die neue Mission
  atmosphärisch zu gestalten.
- **Umgang mit fehlerhaften Speicherständen:** Richtlinien dafür, wie die KI-Spielleitung auf
  abweichende oder beschädigte Savegames reagieren kann (etwa durch korrigierende Vorschläge oder
  Ingame-Nachfragen) – ohne die Immersion zu brechen.
- **In-World-Spielleitung:** Die Spielleitung durch GPT bleibt vollständig in der Spielwelt
  verankert. Sämtliche Erklärungen zum Laden/Speichern erfolgen durch Ingame-Elemente (z.B. den Kodex,
  NSCs oder ein „Nullzeit-Log“) und nicht als außenstehende Systemkommentare.
- **Beispiel-Speicherblöcke:** Bereitstellung von kommentierten Beispielen für typische
  Speicherstände (sowohl Solo- als auch Gruppen-Spielstände) im standardisierten Format, die als
  Vorlage dienen können.
- **Token-Lite-Modus:** Missionslog mit max. 15 Einträgen. Archivierte Rifts lassen sich auslagern, um Token zu sparen.
- **Archiv-ZIP:** Erledigte Missions-JSON lassen sich gebündelt zippen, um Langzeitkampagnen schlank zu halten.

Im Folgenden werden diese Punkte im Detail ausgeführt und das neue System erläutert.
Um Speicherplatz zu sparen, darf die SL erledigte Missionslogs gebündelt als ZIP-Archiv auslagern.
Beim Laden ladet ihr zuerst euren aktuellen Speicherstand.
Danach folgt, falls nötig, die ZIP-Datei. GPT erkennt so den bisherigen Missionsverlauf.
- Nach dem Laden zwingend `StartMission()` ausführen; Details siehe Abschnitt „Load-Pipeline“.

Speichern ist ausschließlich im **HQ** erlaubt. `cmdSave()` setzt dabei das
Exfil-Fenster zurück, leert Stress und schreibt Level, Rank, Würfelmodus,
offene Seeds sowie den ☆-Bonus in den JSON-Block.

### Deep Save {#deep-save}

`speichern` gibt stets einen vollständigen JSON-Block mit allen relevanten
Feldern aus. Wird das Kontextlimit überschritten, teile den Block in mehrere
Codefelder und sende sie nacheinander.

**DeepSave(state)**

1. Wandle den gesamten Zustand in einen JSON-Snapshot um.
2. Gib diesen Snapshot vollständig aus und ersetze damit jeden vorherigen Stand.

Incrementelle oder partielle Saves sind nicht vorgesehen; jeder Speichervorgang
überschreibt den gesamten vorherigen Zustand.

```javascript
function select_state_for_save(state) {
  return {
    zr_version: "4.2.2",
    save_version: 6,
    created_at: new Date().toISOString(),
    location: state.location,
    phase: state.phase,
    campaign: state.campaign,
    character: state.character,
    team: state.team,
    loadout: state.loadout,
    economy: state.economy,
    logs: state.logs,
    ui: { gm_style: state.ui?.gm_style ?? "verbose" }
  };
}

function save_deep(state) {
  if (state.location !== "HQ") {
    throw new Error("Save denied: HQ-only.");
  }
  const payload = select_state_for_save(state);
  payload.checksum = sha256(JSON.stringify(payload)); // optional
  return JSON.stringify(payload);
}

function load_deep(json) {
  const data = JSON.parse(json);
  return hydrate_state(migrate_save(data));
}

function migrate_save(data) {
  if (!data.save_version) data.save_version = 1;
  if (data.save_version === 1) {
    data.campaign ||= {};
    data.save_version = 2;
  }
  if (data.save_version === 2) {
    data.ui ||= { gm_style: "verbose" };
    data.save_version = 3;
  }
  if (data.save_version === 3) {
    data.phase ||= "core";
    data.save_version = 4;
  }
  if (data.save_version === 4) {
    const character = data.character ||= {};
    const carryHeat = character.psi_heat ?? character.heat ?? 0;
    character.psi_heat = Number.isFinite(carryHeat) ? carryHeat : 0;
    if (character.psi_heat_max === undefined && character.heat_max !== undefined) {
      character.psi_heat_max = character.heat_max;
    }
    delete character.heat;
    delete character.heat_max;
    data.save_version = 5;
  }
  if (data.save_version === 5) {
    data.ui ||= { gm_style: "verbose" };
    data.ui.intro_seen = !!data.ui.intro_seen;
    data.save_version = 6;
  }
  return data;
}
```

`sha256()` dient lediglich der Entwicklungsprüfung; im regulären Spielbetrieb darf die Checksumme entfallen.

## Einzelspieler-Speicherstände – Bewährte Logik beibehalten

Für **Einzelspieler-Runden** (ein Chrononaut als Spielercharakter) bleibt die bisherige
Speichermechanik im Kern bestehen. Am Ende jeder Mission erzeugt das Spiel einen maschinell lesbaren
**Speicherblock** – idealerweise als strukturierten JSON-Code im Chat (z.B. in einem Code-Feld).
Entscheidend ist, dass das Format einheitlich und klar lesbar ist, sowohl für
Menschen als auch für das KI-Modell. Dadurch erkennt GPT zuverlässig, dass es sich um einen
Spielstand handelt, und kann alle relevanten Daten übernehmen, sobald der Speicherstand in eine neue
Spielsitzung geladen wird.

**Struktur und Inhalt eines Einzel-Speicherstands:** Der Speicherstand wird als zusammenhängender
Datenblock (z.B. in einem Code-Feld) dargestellt. Er enthält die wichtigsten Charakterdaten in
**beschreibender, narrativ eingebetteter Form**, aber **keine versteckten Befehle** oder unklare
Formulierungen. Alles ist neutral in der dritten Person gehalten, damit GPT es problemlos
interpretieren kann. Typische Felder eines Speicherstands sind unter anderem:

- **Grunddaten:** Name des Charakters, Herkunftsepoche (Zeit/Hintergrund), Level und
  Erfahrungspunkte (EP) bzw. Fortschritt.
- **Attribute:** Werte für Stärke, Geschicklichkeit, Intelligenz, Charisma etc. (inklusive
  Spezialattribute wie _Temporale Affinität_ oder _Systemlast_ für Chrononauten).
- **Fähigkeiten und Talente:** Eine Liste besonderer Talente, Fertigkeiten oder Ausbildungen der
  Figur.
- **Ausrüstung:** Inventarlisten, ggf. inklusive besonderer Gegenstände, Implantate, psionischer
  Fähigkeiten etc.
- **Charakterprofil:** Besondere Merkmale wie moralische Ausrichtung, Ruf oder Zugehörigkeiten (z.B.
  _„altruistisch“_, Rang im ITI, Beziehungen zu Fraktionen).
- **Errungenschaften:** Wichtige Erfolge aus vergangenen Missionen.
- **Kodex-Wissen:** Relevantes Wissen, das der Charakter im Kodex gespeichert hat – z.B.
  Erkenntnisse aus vergangenen Missionen, enthüllte Geheimnisse, bekannte NPCs oder historische
  Fakten, an die er sich erinnert.
- **Statistiken (optional):** Dinge wie absolvierte Missionen, gelöste Rätsel, besiegte Gegner usw.,
  falls für den Spielfortschritt von Belang.
- **Zeitlinien-Veränderungen (optional):** Wichtige Abweichungen im historischen Verlauf, die durch
  die Aktionen des Charakters verursacht wurden, inklusive Angabe eines Stabilitätsgrads der Änderung
  (siehe _Zeitlinien-Tracker_ weiter unten).

Nicht im Speicherstand enthalten sind in der Regel detailreiche Situationsbeschreibungen oder
komplette Dialogverläufe vergangener Missionen. Der Speicherstand soll **kompakt** bleiben –
ausreichend, um den Charakter konsistent weiterzuspielen, aber ohne den neuen Missionskontext mit
irrelevanten Altlasten zu überfrachten. Jede neue Mission beginnt erzählerisch „frisch“, und der
Spielstand liefert nur die nötigsten Zusammenfassungen der Vorgeschichte. So bleibt der Chat-Kontext
schlank, und GPT kann die Fortsetzung konsistent gestalten, ohne durch Rauschen alter Dialoge
verwirrt zu werden.

**Beispiel: JSON-Speicherstand für einen einzelnen Charakter.** Angenommen, Agent Alex hat Mission 1
abgeschlossen. Sein Speicherstand könnte folgendermaßen aussehen:

_{
  "Name": "Alex",
  "Epoche": "Gegenwart (2025)",
  "Level": 2,
  "Erfahrung": 15,
  "zr_version": "4.1.5",
  "version_hash": "4.1",
  "arc_dashboard": {"offene_seeds": [], "fraktionen": {}, "fragen": []},  # optional
  "Attribute": {"Stärke": 4, "Geschicklichkeit": 5, "Intelligenz": 5, "Charisma": 3},
  "Talente": ["Pistolenschütze", "Kryptographie"],
  "Inventar": ["Dietrich-Set", "Heiltrank", "Zeitscanner-Tablet"],
  "Kodex": ["Schlacht von Aquitanien 1356", "Chronomant Moros"],
  "Errungenschaften": ["Retter von Aquitanien"]
_}

_Erläuterung:_ In diesem Speicherblock sind alle zentralen Daten von Alex nach seiner ersten Mission enthalten.
Zum Beispiel hat er das Talent _Kryptographie_, besitzt ein Neuro-Link-Implantat,
ein Inventar mit

Gegenständen (Dietrich-Set, Heiltrank, Zeitscanner-Tablet)
und im **Kodex** stehen Einträge, die an
seine Erlebnisse aus einer Anfangsmission erinnern (Schlacht von Aquitanien 1356 etc.). Diese Informationen
reichen aus, um Alex in einer zukünftigen Mission konsistent weiterzuspielen. GPT kann daraus
entnehmen, **wer Alex ist, was er kann und was er erlebt hat**, ohne dass jedes Detail der ersten
Mission erneut im Prompt geladen werden muss.

```json
"field_notes": [
  {
    "agent_id": "ZE-A12",
    "mission": "Operation Cold Swap",
    "timestamp": "1958-06-02T14:07Z",
    "note": "Funkraum mit Ventil-Schalter entdeckt. PZ-2.5 aktiv."
  }
]
```

_Beispiel:_ Dieses optionale Feld sammelt kurze Einsatzmemos und hat keinerlei
Regelwirkung. Es erleichtert jedoch die Nachverfolgung einzelner
Entdeckungen.

Bestehende Einzelspieler-Spielstände aus früheren Versionen behalten dieses Format bei und
funktionieren weiterhin unverändert. Wer also bisher Solo-Abenteuer mit ZEITRISS gespielt hat, muss
nichts an alten Savegames ändern – sie können in ZEITRISS 4.2.2 direkt weitergenutzt werden.

## Gruppen-Spielstände – Neue Unterstützung für Teams

**Neu** im aktualisierten System ist die offizielle Unterstützung von **Gruppen-Spielständen**. Ein
einzelner Speicherblock kann nun mehrere Spielercharaktere umfassen. Dadurch lassen sich Gruppen von
Chrononauten gemeinsam speichern und laden, ohne die etablierte Einzelspieler-Mechanik zu stören.
Die bereits bekannte Datenstruktur eines Charakter-Datensatzes bleibt dabei erhalten und wird
lediglich erweitert: Statt eines einzelnen Charakter-Objekts können nun mehrere solcher Objekte im
Speicher vorhanden sein.

### Struktur eines Gruppen-Speicherstands

Um mehrere Charaktere in einem Savegame abzubilden, gibt es zwei naheliegende Ansätze im JSON-
Format:

- **Array von Charakterobjekten:** Der Speicherblock besteht aus einer Liste _\[...\]_, in der jedes
  Element ein vollständiges Charakter-Datenobjekt (wie oben beschrieben) ist.
- **Wrapper-Objekt mit Charakterliste:** Der Speicherblock ist ein JSON-Objekt mit einem Feld (z.B.
  _"Charaktere"_ oder _"Gruppe"_), das eine Liste aller Charakterobjekte enthält. Optional kann dieses
  Objekt zusätzliche gruppenweite Felder wie einen Gruppennamen enthalten.

Beide Varianten sind technisch handhabbar. Wichtig ist vor allem, dass GPT zuverlässig erkennt, dass
mehrere Charaktere vorliegen. Aus Gründen der Klarheit verwenden wir im Folgenden einen Wrapper-
Ansatz: ein JSON-Objekt mit dem Feld _"Charaktere"_, das eine Liste von Charakteren enthält, sowie
optional ein Feld für den **Gruppennamen**.

**Beispiel: JSON-Gruppenspielstand mit zwei Charakteren.** Angenommen, zwei Spieler (oder ein
Spieler mit zwei aktiven Charakteren) möchten ihre Figuren Alex und Mia gemeinsam als Team
speichern. Ein Gruppen-Spielstand im JSON-Format könnte so aussehen:

_{_

{
  "Gruppe": "Team Chronos",
  "zr_version": "4.1.5",
  "version_hash": "4.1",
  "arc_dashboard": {"offene_seeds": [], "fraktionen": {}, "fragen": []},  # optional
  "Charaktere": [
    { "Name": "Alex", "Epoche": "Gegenwart (2025)", "Level": 2 },
    { "Name": "Mia", "Epoche": "Victorianisches Zeitalter (1888)", "Level": 1 }
  ]
}

Hier besteht das Agenten-Team **“Team Chronos”** aus zwei Mitgliedern: Alex und Mia. Jeder Charakter
wird als separates Objekt mit all seinen Datenfeldern aufgeführt (der Übersicht halber sind oben
nicht alle Felder ausgeschrieben, aber in einem echten Save würden analog zu Alex auch Mias
Attribute, Talente, Inventar etc. vollständig aufgeführt sein). Das optionale Feld _"Gruppe"_ dient
als Teamname oder Identifikator der Gruppe. Es ist _nicht zwingend erforderlich_ – die Präsenz
mehrerer Objekte in _"Charaktere"_ signalisiert GPT bereits, dass es sich um einen Gruppen-
Spielstand handelt. Dennoch kann ein Gruppenname atmosphärisch hilfreich sein und vom Spielleiter in
Dialogen verwendet werden (z.B. _„Agententeam Chronos...“_).

Entscheidend ist: Die **Struktur pro Charakter bleibt identisch** zu einem Einzelspieler-
Speicherstand. Es gehen also keine Datenfelder verloren und es werden keine neuen speziellen Formate
pro Charakter erfunden – wir haben lediglich eine zusätzliche Ebene drumherum gesetzt, um mehrere
Datensätze zusammenzuhalten. Somit ist auch die **Abwärtskompatibilität** gegeben: Ein Einzel-
Charakter-Save sieht für GPT praktisch genauso aus wie ein Gruppen-Save, nur ohne die äußere Liste.

### Erkennung von Einzel- vs. Gruppen-Spielständen

Der KI-Spielleiter (GPT) muss sofort erkennen können, ob ein geladener Speicherblock einen einzelnen
Charakter enthält oder eine Gruppe. Diese Unterscheidung erfolgt **allein durch die JSON-Struktur**:

- **Einzelspieler-Speicherstand:** Besteht typischerweise aus **einem einzigen JSON-Objekt** mit
  Charakterdaten – kein äußerer Array und kein _"Charaktere"_-Feld. Auf oberster Ebene steht z.B.
  direkt _"Name": "Alex"_. GPT liest diese Struktur und sieht nur einen Charaktereintrag – damit ist
  klar, dass es sich um einen Solo-Spielstand handelt. _Beispiel:_ _{ "Name": "Alex", "Level": 2, ...
  }_ – kein Array, keine weiteren Objekte auf Top-Level außer diesem einen Charakter →
  **Einzelcharakter-Save**.
- **Gruppen-Speicherstand:** Erkennbar an **mehreren Charakterdatensätzen** in einem Container. Das
  kann eine JSON-Liste _\[ {...}, {...} \]_ sein oder ein Objekt mit einem Feld _"Charaktere"_ (bzw.
  analog), welches ein Array enthält. Sobald GPT mehr als ein Charakterobjekt findet, ist klar: Dieser
  Spielstand umfasst mehrere Figuren. Ein optionales Feld _"Gruppe"_/_"Team"_ kann die Gruppennatur
  untermauern, wird aber zur reinen Erkennung nicht benötigt. _Beispiel:_ _{ "Charaktere": \[
  {Char1-Daten}, {Char2-Daten} \] }_ – mehrere Objekte im Array → **Gruppen-Save**.

Im Klartext prüft GPT beim Laden eines Spielstands einfach die oberste Struktur: Ein einzelnes
Datenobjekt bedeutet Solo-Spiel; eine Liste oder ein _"Charaktere"_-Feld mit mehreren Objekten
bedeutet Gruppe. Diese Prüfung ist trivial und benötigt keine extra Kennzeichnung, solange wir das
Format konsequent einhalten.

### Eindeutige Identifikation von Charakteren (Metadaten)

Wenn mehrere Charaktere in einem Savegame enthalten sind, kann es hilfreich sein, jeden Eintrag mit
einer eindeutigen **ID** oder ähnlichen Metadaten zu versehen. Dies dient der robusten
Identifikation, insbesondere falls Charaktere ähnliche Namen haben oder sich über die Zeit ändern.
Ein optionales Feld wie _"ID"_ pro Charakter kann z.B. eine eindeutige Kennung (UUID oder ein
anderer einmaliger Code) enthalten.

_Beispiel eines Charakters mit ID:_

_{_

_"Name": "Alex",_

_"ID": "CHR-7f3a9b2e",_

_"Epoche": "Gegenwart (2025)",_

_..._

_}_

In einem Gruppenstand hätte dann jeder Charaktereintrag seine eigene ID. **Wozu das?** Bei der
Zusammenführung mehrerer Speicherstände oder dem späteren Aktualisieren einzelner Charaktere
innerhalb einer Gruppe kann GPT anhand der ID erkennen, ob ein Charakter bereits existiert oder neu
hinzukommt. So werden Duplikate vermieden:

- **Mit ID:** Lädt man einen neuen Speicherstand von Alex in eine bestehende Gruppe, in der Alex mit
  gleicher ID schon existiert, weiß das System, dass es **denselben Charakter** updaten soll (anstatt
  einen zweiten „Alex“ hinzuzufügen). Gleiches gilt beim erneuten Laden eines fortgeschrittenen
  Savegames: Die ID signalisiert GPT, welcher bestehende Gruppencharakter aktualisiert werden muss.
- **Ohne ID:** Versucht GPT, Charaktere anhand von Name + Epoche o. ä. zu unterscheiden. Das kann in
  vielen Fällen funktionieren, ist aber fehleranfälliger (z.B. könnten zwei Spieler zufällig beide
einen Charakter namens „Alex“ spielen, oder ein Charakter ändert seinen Decknamen zwischenzeitlich).

#### Konfliktfall ohne ID

Treffen zwei Einträge ohne ID aufeinander und stimmen **Name** sowie
**Epoche** überein, fragt das System nach. Entweder wird eine neue ID vergeben
oder der vorhandene Datensatz bewusst überschrieben. Auf diese Weise lassen sich
Duplikate vermeiden, ohne dass IDs zwingend erforderlich sind.

Eine technische UUID als ID ist daher **empfehlenswert** für langfristige, große Kampagnen, aber das
Feld bleibt optional. Das System funktioniert auch ohne – es verlässt sich dann ganz auf die
eindeutigen Namen oder Konstellationen. (In unseren obigen Beispielen haben wir der Einfachheit
halber keine IDs angegeben, um die Darstellung nicht zu verkomplizieren; in der Praxis könnte man
sie jedoch hinzufügen, um maximale Eindeutigkeit zu erzielen.)

### Laden und Zusammenführen von Speicherständen

Beim Laden eines Speicherstands in den Chat-Kontext – sei es zu Beginn einer neuen Spielsession oder
mitten im Spiel – folgt GPT je nach Art des Savegames unterschiedlichen Pfaden. Wichtig ist, dass
dieser Übergang reibungslos und narrativ sauber abläuft. **Je nach Situation passiert Folgendes:**

- **Solo-Spielstand laden (ein Charakter):** Wird ein einzelner Charakter-Speicherstand geladen
  (Format wie Alex im Beispiel oben), verfährt die Spielleitung wie gewohnt: GPT liest die
  Charakterdaten ein und setzt die Geschichte nahtlos mit **diesem einen Chrononauten** fort. Für den
  Spieler fühlt es sich an, als würde er genau dort weitermachen, wo er mit seinem Charakter aufgehört
  hat. Alle Werte, Inventargegenstände und Kodex-Einträge aus dem Save stehen zur Verfügung, und die
  neue Mission kann mit dem bekannten Helden beginnen. _(Dieser Ablauf entspricht dem bisherigen
  Fortsetzungsprozess in ZEITRISS.)_
- **Von Solo zu Gruppe (Charaktere hinzufügen):** Neu ist die Möglichkeit, aus einem laufenden
  Einzelspiel eine Gruppe zu bilden, indem man einen weiteren Charakter hinzulädt. Das geht so: Man
  startet wie üblich mit dem bisherigen Solo-Charakter A (lädt also dessen Save). Anschließend fügt
  man zusätzlich den Speicherblock eines zweiten Charakters B in den Chat ein. GPT erkennt nun, dass
  zwei getrennte Datensätze vorliegen. Daraus resultiert automatisch ein **Gruppen-Spielstand**.
  Charakter B wird als neues Gruppenmitglied hinzugefügt, ohne Charakter A zu entfernen oder zu
  überschreiben. In der laufenden Geschichte taucht B dann z.B. als weiterer Agent auf, der sich dem
  Team anschließt. Charakter A behält all seine Daten und bleibt aktiv; Charakter B bringt seine
  eigenen Daten mit. Fortan führt GPT beide Charaktere gemeinsam in einem Gruppenstand weiter.
  _(Wichtig: Die Reihenfolge, in der man zusätzliche Charakter-Saves einfügt, spielt keine große Rolle
  – ob B gleich zu Anfang oder mitten in einer Mission dazukommt: GPT erkennt den neuen Datensatz und
  integriert B entsprechend ins Team.)_
- **Gruppenstart (mehrere Charaktere gemeinsam laden):** Es ist ebenso möglich, **von Anfang an**
  mehrere Speicherstände gleichzeitig zu laden – zum Beispiel wenn mehrere Spieler, die zuvor einzeln
  gespielt haben, nun zusammen eine Mission starten wollen. In diesem Fall werden die Savegame-Blöcke
  aller beteiligten Charaktere nacheinander (oder gesammelt) in den neuen Chat eingefügt. GPT
  konsolidiert diese Informationen automatisch zu **einem einzigen Gruppenstand**: Alle Charakterdaten
  bleiben jeweils separat vorhanden, bilden aber in der Spielwelt nun ein gemeinsames Team. GPT
  behandelt den zusammengeführten Speicherblock als eine Einheit, die alle nötigen Infos für die
  Gruppe enthält. Es ist also, als hätte GPT intern eine Liste aller aktiven Charaktere. Kein
  Charakter überschreibt einen anderen: Selbst wenn man mehrere JSON-Objekte unmittelbar
  hintereinander einfügt, werden sie nicht vermischt. GPT sieht mehrere Top-Level- Objekte bzw. Array-
  Elemente und erstellt intern eine Sammlung aller Charaktere. _(Reihenfolge egal: Ob man zuerst Alex,
  dann Mia lädt oder umgekehrt, spielt inhaltlich keine Rolle – am Ende zählt, dass GPT beide Einträge
  sieht. Sollte ein Charakter doppelt geladen werden (z.B. jemand fügt versehentlich denselben Save
  zweimal ein), würde GPT dank identischer Daten/ID erkennen, dass es sich um die gleiche Figur
  handelt, und keinen Klon erzeugen.)_
  Nach dem Zusammenführen der Spielstände setzt GPT den Paradoxon-Index sowie die Liste offener
  Rifts auf **0**, damit das Team mit einem sauberen Stand beginnen kann. Ein optionales
  `startGroupMode()`-Snippet im Entwickler-Stubs `systems/runtime-stub-routing-layer.md`
  illustriert diesen Reset – das Dokument selbst wird nicht ins Spiel eingebunden.

**Zusammengefasst:** Ein einzelner Savegame-Block ergibt einen einzelnen Charakter; mehrere
Savegame-Blöcke (gleichzeitig oder sukzessive) ergeben die Bildung bzw. Erweiterung einer Gruppe.
GPT erkennt das automatisch anhand der Formatstruktur und passt sein Vorgehen entsprechend an –
**ohne** dass der Spielleiter außerhalb der Welt eingreifen muss.

### Hinzufügen, Aktualisieren und Entfernen von Gruppenmitgliedern

Sobald ein Spiel im Gruppenmodus läuft, gelten einfache **Regeln für den Umgang mit Gruppen-
Spielständen**, damit GPT als Spielleiter nichts durcheinanderbringt:

- **Neuen Charakter hinzufügen:** Jeder zusätzliche Charakter-Datensatz, der in der aktuellen Gruppe
  noch nicht vorhanden war, wird als neues Gruppenmitglied ergänzt. GPT erzeugt intern einen neuen
  Charaktereintrag und übernimmt alle Werte aus dessen Savegame. _Beispiel:_ Die Gruppe bestand bisher
  nur aus Alex. Nun wird Mias Speicherstand hinzugefügt. Mia (neuer Name/ID) wird von GPT als neues
  Mitglied erkannt. Ergebnis: Gruppe = \[Alex, Mia\]. Beide stehen mit ihren vollen Daten zur
  Verfügung.
- **Bestehenden Charakter aktualisieren:** Wird ein Speicherstand geladen, der zu einem Charakter
  gehört, der bereits in der Gruppe existiert, so werden dessen Daten **aktualisiert**, nicht
  dupliziert. Hier kommt das Metadaten-Feld (ID) ins Spiel: GPT vergleicht die IDs (falls vorhanden)
  oder ersatzweise Name/Epoche. Stimmen diese überein, nimmt es an, dass es derselbe Charakter ist.
  _Beispiel:_ In einer laufenden Gruppe aus Alex und Mia werden zu Beginn der nächsten Mission beide
  aktualisierten Savegames neu geladen. GPT erkennt an Alex’ ID oder Namen, dass Alex schon Teil der
  Gruppe ist – also wird **kein zweiter Alex** hinzugefügt, sondern Alex’ bestehender Eintrag mit den
  aktuellen Werten versehen (die ohnehin dem Save entsprechen). Genauso für Mia. Die Gruppe \[Alex,
  Mia\] bleibt bestehen, nur dass nun beide auf dem neuesten Stand sind.
- **Keine Konflikte durch unterschiedliche Felder:** Charaktere können unterschiedliche Felder oder
  Listen in ihren Daten haben, ohne Probleme zu verursachen. Hat Charakter A z.B. ein Feld _"Psionik":
  \[\]_ (weil er keine psionischen Fähigkeiten hat) und Charakter B gar kein Feld _"Psionik"_ (weil es
  für sie nie relevant war), führt das zu keinerlei Konflikt. GPT interpretiert einfach jeden
  Charakterblock für sich. Fehlt ein Feld bei einer Figur, bedeutet das nur, dass diese Figur dazu
  keine Angaben hat – es ist kein globales Problem. Es gibt also keine Fehlermeldung oder Störung,
  sondern jeder Charakterdatensatz wird individuell vollständig gelesen.
- **Optionale gemeinsame Elemente:** Das System ist primär so ausgelegt, dass jede Figur **getrennte
  Daten** hat. Falls gewünscht, kann man aber auch gruppenweite Felder definieren – etwa ein
  gemeinsames _"Gruppeninventar"_ oder einen aktuellen _"Missionsstatus"_, die außerhalb der einzelnen
  Charakterobjekte im JSON stehen. Solche Felder gelten dann für die **gesamte Gruppe**. GPT würde sie
  als von allen geteilt interpretieren. _Beispiel:_ Man könnte dem Gruppen-JSON ein Feld _"Mission":
  "Paris 1943 – Einsatzbeginn"_ auf oberster Ebene hinzufügen. GPT weiß dann, dass alle Charaktere
  sich zu Beginn von Mission X (hier Paris 1943) befinden. Solche globalen Felder sind optional und
  sollten sparsam verwendet werden, um die Trennung der Charakterdaten klar zu halten.
- **Charaktere entfernen:** Wenn ein Charakter die Gruppe dauerhaft verlassen soll, kann dies
  einfach dadurch geschehen, dass sein Datenblock im nächsten Speicherstand **weggelassen** wird. GPT
  wird beim Laden merken, dass ein zuvor vorhandener Charaktereintrag nicht mehr vorhanden ist. Die
  Konsequenz in der Spielwelt wäre, dass diese Figur nicht mehr Teil der aktiven Gruppe ist.
  Idealerweise wird dies narrativ untermauert – etwa indem zuvor in der Geschichte erklärt wird,
  **warum** der Charakter die Gruppe verlässt (Ruhestand, eigene Mission, Tod etc.). Beim nächsten
  Laden fehlen seine Daten; GPT interpretiert das so, dass nur die verbleibenden Charaktere
  weitermachen. _(Hinweis: Der letzte gespeicherte Stand des entfernten Charakters kann
  selbstverständlich als Einzel-Save separat archiviert werden, falls er später wiederkommt oder solo
  weiterspielt – die Formatkompatibilität macht’s möglich.)_

Durch diese Regeln können Gruppen dynamisch **wachsen oder schrumpfen**, ohne Chaos im Speicherstand
zu verursachen.

**Beispiel – Zusammenführung Schritt für Schritt:** Spieler 1 und Spieler 2 haben jeweils einen
Chrononauten (Charakter A und B) in Solo-Missionen gespielt und Savegames erstellt. Für ein
gemeinsames Abenteuer laden sie beide Speicherblöcke in den neuen Chat. GPT sieht Charakter A und
Charakter B – unterschiedliche Namen/IDs, keine Überschneidungen – und formt intern ein Team
**\[A, B\]**. Anschließend begrüßt der Spielleiter diese neue Gruppe im Spiel (dazu mehr im
Abschnitt _Immersiver Ladevorgang_). Kommt später Spieler 3 mit Charakter C dazu, fügt man einfach
dessen Speicherstand hinzu: GPT erkennt C als neu → Gruppe wächst zu **\[A, B, C\]**. Falls hingegen
Spieler 2 vor der nächsten Mission seinen **aktualisierten** B-Speicher einfügt (z.B. nach einem
Level-Up), erkennt GPT an B’s ID/Name, dass dieser schon in \[A, B, C\] existiert, und
**aktualisiert nur B’s Werte**, anstatt einen zweiten B hinzuzufügen. Die Gruppe bleibt konsistent,
niemand wird dupliziert.

## Load-Pipeline (Autoload, Multi-JSON, Gruppen-Merge)

**Ziel:** Saves laden (Solo oder Gruppe), migrieren, im **HQ** fortsetzen und
`StartMission()` automatisch initialisieren.

### Autoload & Intents
- Erkennt *automatisch* gepostete JSON-Saves (Heuristik: `zr_version` plus Felder wie
  `character`, `Charaktere`, `team` oder `campaign`).
- Befehle: `!load`, „Spiel laden“, „Spielstand laden“, „Load“. Ohne JSON → Prompt:
  `Kodex: Load-Modus aktiv. Poste 1–N Speicherstände (Solo oder Gruppe). "Fertig" startet den Merge.`

### Multi-JSON Collector
- Akzeptiert mehrere JSON-Blöcke in **einer** oder **mehreren** Nachrichten.
- Sammelphase endet auf **„Fertig“** – oder bei Autoload sofort, wenn genau **ein** Save erkannt
  wurde.

### Validierung & Migration
- Wende `migrate_save()` auf jeden Block an (`save_version` hochsetzen, Defaults ergänzen).
- **Fortsetzung** erzwingen: `location = "HQ"` (Load-Guard; Speichern bleibt HQ-only).

### Merge-Regeln (Gruppe)
- Primärschlüssel: `character.id` → Update statt Duplikat.
- Fallback: `(name, epoche)` → Kollision: `Kodex: Doppelter Agent erkannt. Überschreiben [Ja/Nein]?`
- **CU**-Konten bleiben **pro Agent** separat; die Summe darf im Recap erscheinen.
- Team-NSCs werden additiv zusammengeführt (Duplikate pro Name max. 1×).

### Recap & Start
- **StartMission()** direkt nach dem Load auslösen (Transfer ggf. temporär unterdrücken).
- **Compliance-Hinweis:** `ShowComplianceOnce()` vor dem Rückblick anzeigen; erscheint pro Tag nur
  1×. Der gesetzte Status liegt in `logs.flags.compliance_shown_today`; `SkipEntryChoice()`
  setzt parallel `flags.runtime.skip_entry_choice=true`, damit der übersprungene Einstieg
  dokumentiert ist.
- **Kurzrückblick**: letzte Missionslogs, Paradoxon, offene Seeds, CU pro Agent und Summe,
  aktive Modi.
- **Einstieg** gemäß README: _„klassischer Einstieg“_ oder _„Schnelleinstieg“_.
  - HQ-Interlude nur als Text; kein `NextScene("HQ")`.
  - Danach Transfer-HUD einblenden und direkt `NextScene(loc=<Ziel>, role="Ankunft")`.

```mermaid
flowchart TD
  A[JSON erkannt ODER !load] -->|Multi-JSON| B[Migration]
  B --> C[Merge (ID, sonst Name+Epoche)]
  C --> D[Fortsetzung im HQ]
  D --> E[StartMission() (Transfer-Defer)]
  E --> F[ShowComplianceOnce() + Recap]
  F --> G{Einstieg wählen}
  G -->|Klassisch| H[Transfer-HUD → NextScene]
  G -->|Schnell| I[Transfer-HUD → NextScene]

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
