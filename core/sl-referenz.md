---
title: "ZEITRISS 4.2.6 – SL-Referenz: Dispatcher, Regeln & Systemtabellen"
version: 4.2.6
tags: [core, reference, gm]
---

# ZEITRISS 4.2.6 – SL-Referenz

> Dieses Modul enthält alle Tabellen, Befehle und Systemreferenzen die
> die KI-Spielleitung zur Laufzeit braucht. Es wird in den Wissensspeicher
> geladen und ergänzt die Module aus `core/`, `gameplay/` und `systems/`.

## Dispatcher-Kurzreferenz

### Dispatcher-Starts & Speicherpfade

- **Spielstart-Varianten.** `Spiel starten` akzeptiert `solo`, `npc-team` und
  `gruppe` plus die Zusätze `klassisch` oder `schnell`. `npc-team` verlangt eine
  Zahl `0-4` (NPC-Begleiter; Team gesamt 1-5), `gruppe` ignoriert Zahlen.
  Ungültige Kombinationen liefern die passenden Fehltexte.
- **Zentrale Strings.** Start-/Fehlertexte liegen in
  `dispatcher_strings` (Runtime-Export).
- **Syntax-Hinweis.** Startbefehle ohne Klammern oder mit fehlerhaftem Muster
  antworten mit "Startsyntax: Spiel starten (solo|npc-team [0-4]|gruppe
  [klassisch|schnell]). Klammern sind Pflicht." und schreiben höchstens einmal
  pro Session einen Trace-Eintrag `dispatch_hint`.
- **Briefing & Schnellstart.** Ohne Modus fragt der Dispatcher einmalig nach
  "klassisch oder schnell?". `klassisch` blendet Auswahlmenüs ein, `schnell`
  überspringt sie. Solo übernimmt Ansprache **Du** ohne Nachfrage nach der
  Spielerzahl; Gruppen zählen sich während der Erschaffung. NPC-Teams werden bei
  Bedarf automatisch erzeugt und skaliert.
- **HQ-Intro (Runtime).** Volles HQ-Intro 1:1 ausspielen - keine Kürzungen, die
  Schlusszeile gehört dazu.
- **Spiel laden.** `Spiel laden` springt ohne Moduswahl in das HQ-Recap,
  aktiviert das Kodex-Overlay, überspringt Einstiegsprompts/EntryChoice und
  übernimmt alle Save-Flags. Der Persistenzanker liegt auf
  `campaign.entry_choice_skipped=true` plus `ui.intro_seen=true`; das
  Laufzeit-Flag `flags.runtime.skip_entry_choice` bleibt transient, wird nicht
  serialisiert und dient nur dem aktiven Run. UI-/Accessibility-Overrides aus
  dem Host bleiben erwartetes Verhalten und werden als Trace
  `ui_host_override` protokolliert.
- **Speichern.** *(Die folgenden SaveGuard-Strings sind KI-Spielleiter-Referenz.)*
  Einsätze lassen kein Speichern zu; der Dispatcher meldet
  "SaveGuard: Speichern nur im HQ - HQ-Save gesperrt." und hält die Mission
  aktiv. Beim Laden bleibt der HQ-Pool des Hosts maßgeblich; Import-Wallets
  werden union-by-id angehängt, fehlende Labels aus dem Import ergänzt, und
  Konflikte landen in `logs.flags.merge_conflicts` (Allowlist:
  `wallet|rift_merge|arena_resume|campaign_mode|phase_bridge|location_bridge`)
  plus dem Trace `merge_conflicts`.
  Jeder HQ-Save schreibt ein `economy_audit`-Trace mit Level-Band
  (120/512/900+), `band_reason`, `wallet_avg_scope`, `target_range` (HQ-Pool +
  Wallet-Richtwert), Delta-Flags (`delta`, `out_of_range`),
  `chronopolis_sinks` (Liste der angesetzten Sinks) sowie dem berechneten
  Wallet-Durchschnitt. Die Band-Auswahl nutzt den Host-Level; fehlt dieser,
  greift der Median der Party/Team-Roster. Weichen HQ-Pool oder Wallet
  vom Ziel ab, erscheint der Toast "Economy-Audit: HQ-Pool/Wallets außerhalb
  Richtwerten (Lvl 120|512|900+).".
  SaveGuards loggen `save_blocked` mit Grund, Standort (`location`) und Phase
  (`phase`), damit die Reihenfolge und der Auslöser nachvollziehbar bleiben.
  Arena-Resumes schreiben `resume_token.previous_mode` und einen
  `merge_conflicts`-Eintrag (`field='arena_resume'`) deterministisch, wenn ein
  Save zwischen PvP/Arena und HQ wechselt; Guard-Strings bleiben identisch zu
  den Dispatcher-/SaveGuard-Fehlertexten.
- **Gear & Px.** Gear-Bezeichnungen werden nicht automatisch normalisiert;
  Armbänder sind zulässig (keine Handgelenk-Projektionen). Normalisierer lassen
  die Labels unangetastet. Erreicht der
  Paradoxon-Index Px 5, informiert der Kodex, dass neue Seeds erst nach
  Episodenende spielbar sind; der Px-Reset wird im Debrief/HQ mit dem HUD-Toast
  "Px Reset → 0" bestätigt (`px_reset_pending/confirm`). `ClusterCreate()`
  schreibt ein `cluster_create`-Trace (px_before/after, Seeds,
  Episode/Mission/Scene/Loc + campaign_type, `open_seeds_count`) und
  normalisiert `campaign.rift_seeds` beim Lauf und beim Laden als
  Objekt-Liste. Solo-/Px-5-Runs stapeln Seeds ohne Hard-Limit; das Cap 12
  greift ausschließlich beim HQ-Merge. Der Merge schreibt neben
  `rift_seed_merge_cap_applied` (kept/overflow/handoff) auch einen
  `merge_conflicts`-Eintrag (`field='rift_merge'`) mit denselben Feldern plus
  `selection_rule`, damit Trace und Flags synchron bleiben.
  HUD-Toasts folgen einem Budget von 2 pro Szene; Überschreitungen suppressen
  Low-Priority-Texte, während Critical-Tags (u. a. OFFLINE/SAVE/SCHEMA/ARENA/
  GATE/FS/BOSS/ENTRY) vorrangig bleiben und kein Budget verbrauchen. Jede
  Unterdrückung schreibt einen
  `toast_suppressed`-Trace inkl. Snapshot von `logs.flags.hud_scene_usage` und
  `qa_mode`-Flag. Unterdrückte Einträge landen zusätzlich in `logs.hud[]` mit
  `suppressed:true` und `reason:"budget"`.

### Boss-Gates & HUD-Badges

`!helper boss` listet die Foreshadow-Hinweise für Szene 4 und Szene 9 (Core;
Rift nutzt Szene 9 als Pflichthinweisszene) und spiegelt die Gate-Logik als
Golden-String: `GATE 2/2 · FS x/y` (Foreshadow-Hinweise zählen nur den `FS`-
Block hoch). Gate 2/2 ist ab Missionsstart gesetzt; Szene 10 öffnet erst, wenn
der Foreshadow-Zähler erfüllt ist (Core 4/4, Rift 2/2). Der Boss-Trace hält
Teamgröße und DR skaliert nach Boss-Typ (geklammert auf 1-5) fest. In Szene 10
erscheint automatisch der Toast mit dem aktiven Schadensreduktionswert
([Boss-DR-Skala](../gameplay/kampagnenstruktur.md#boss-rhythmus-pro-episode)); nach
dem Debrief setzt die Runtime Self-Reflection auf `SF-ON` zurück - unabhängig
davon, ob die Mission abgeschlossen oder abgebrochen wurde. Mission 10 nutzt
denselben Auto-Reset.

### Psi-Heat & Ressourcen-Reset

Psi-Aktionen erhöhen `Psi-Heat` pro Konflikt. Nach jedem Konflikt springt der
Wert auf 0. Transfers zurück ins HQ setzen zusätzlich SYS-Auslastung, Stress und
Psi-Heat auf die gespeicherten Grundwerte zurück. Arena-Niederlagen setzen
keinen Paradoxon-Reset; `campaign.px` bleibt unverändert bis zum Debrief/HQ.

### Accessibility & UI-Persistenz

Der Befehl `!accessibility` öffnet das UI-Panel (Kontrast, Badge-Dichte,
Ausgabetempo). Jede Bestätigung erzeugt den Toast "Accessibility aktualisiert …"
und schreibt die Auswahl in den Save. Der Serializer legt den kompletten UI-
Block ab (`gm_style`, `suggest_mode`, `action_mode`, `contrast`, `badge_density`,
`output_pace`, `voice_profile`), füllt fehlende Felder automatisch mit
`standard|normal|gm_second_person` plus `action_mode=uncut` und stellt sie beim
Laden sofort wieder her (z. B. `contrast: high`, `badge_density: dense`,
`output_pace: slow`). `voice_profile` akzeptiert `gm_second_person` (Default,
Du/Ihr), `gm_third_person` oder `gm_observer`; alle anderen Eingaben werden
auf das Default gehoben.
Legacy-Mappings: `full|minimal` → `standard|compact`, `rapid|quick` → `fast`,
`default|steady` → `normal`.

**HQ → Transfer-Out → Mission → Exfil/Transfer-Back → HQ**
Vor jeder Mission zeigt das HUD den Transfer-Countdown
(`Nullzeit-Puffer · Transfer 3…2…1 · Redirect: +6h`).
Nach dem Primärziel öffnet sich das Exfil-Fenster (TTL/Stress).
Beim Abzug zeigt das HUD den Rückkehr-Frame
(`Fenster stabil · <TTL> · Return 3…2…1`), danach Schnitt ins HQ,
Debrief und Save (HQ-only).

> **Transfer:** Jede Mission startet mit `Nullzeit-Puffer · Transfer 3…2…1`.
> Beim Abzug folgt `Fenster stabil · <TTL> · Return 3…2…1`.
> **Nach dem Primärziel:** Exfil-Fenster mit **TTL**.
> Jede zusätzliche Szene reduziert die TTL und **erhöht Stress**.
> Bei **TTL 0** folgt **Hot-Exfil**; scheitert der, droht nur mit aktivierter
> Px-Verlust-Regel ein **Px-1**.
> **HUD** nach Zielerfüllung: `TTL` & `Stress`. **Speichern** nur im **HQ**.

Der HUD-Header zeigt `EP · MS · SC/total · MODE · Objective` plus
klassenabhängige Ressourcen:

Im HUD bedeutet `EP` immer **Episode**. Erfahrungspunkte werden als **XP** geführt.

- **PSI:** `PP 6/8 · Psi-Heat 2 · SYS 2/6 (free 4) · Stress 1 · Px █░░░░ (1/5)` -
  Psi-Heat baut sich pro aktiver Psi-Aktion in Konflikten auf und springt
  nach jedem Konflikt auf 0.
- **Non-PSI:** `Ammo 12 · SYS 1/4 (free 3) · Stress 1 · Px █░░░░ (1/5)` -
  führt keinen Psi-Heat-Track.
  In der Exfil-Phase kommen `ANCR Ort · RW mm:ss` hinzu.
  In Szene 1 hängt `FR:Status` an.
  `ui.mode_display` wechselt zwischen `label`, `emoji` oder `both`;
  auf schmalen Zeilen blendet das System den Rank automatisch aus.

Mission-Fokus ist der Standard (oft "Operator-Stil" genannt).
Kämpfe richten sich gegen Fremdfraktionen, nicht gegeneinander.
In Core-Ops treten Rivalen aus externen Machtblöcken auf,
während Rift-Ops sich ganz auf die jeweilige Anomalie konzentrieren.

Core-Ops dauern durchschnittlich **60-75 Minuten** und umfassen **12 Szenen**.
Rift-Ops strecken sich über etwa **90-120 Minuten** mit **14 Szenen**.
Siehe [Missionsdauer-Tabelle](../gameplay/kampagnenstruktur.md#missionsdauer).

### Agenda für Session 0 {#agenda-session-0}

1. **Ton & Modus** - Thriller vs. Stealth-Heist, Mission-Fokus an/aus.
2. **Lines/Veils bestätigen** - siehe Safety Sheet.
3. **Historische Epochen-Wishlist** - Top 3 der Gruppe sammeln.
4. **Teamrollen wählen** - Infiltration, Tech, Face, Sniper …
5. **Paradoxon-Toleranz** - Legt fest, ab welcher Resonanz ihr neue Rifts erspüren möchtet.
6. **Regel-Transparenz** - Overlay und JSON-Log laufen standardmäßig;
   `/debug_rolls` blendet das Log bei Bedarf aus.

### Wahrscheinlichkeits-Übersicht {#wahrscheinlichkeits-uebersicht}

|  SG | W6 expl. | W10 expl. | Δ (W10-W6) |
| --: | -------: | --------: | ---------: |
|   5 |     83 % |      90 % |       +7 % |
|   7 |     67 % |      77 % |      +10 % |
|   8 |     50 % |      65 % |      +15 % |
|  10 |     33 % |      53 % |      +20 % |

### Chat-Kurzbefehle {#chat-kurzbefehle}

Im Live-Chat kann nicht gescrollt werden. Diese Befehle rufen sofort Regeln ab:

### Comms-Core - Funkcheck in Kurzform {#comms-core}

- **Hardwarepflicht:** Funk funktioniert nur mit Comlink (≈ 2 km), Kabel oder
  Relais. Jammer-Overrides müssen explizit gesetzt werden (`device='jammer_override'`).
- **Reichweitenprüfung:** `comms_check()` akzeptiert Meter (`range_m`) oder
  Kilometer (`range_km`) und normalisiert Werte automatisch. Jammer ohne Kabel/
  Relais blockieren den Kontakt.
- **Fallback:** Scheitert der Check, meldet der Kodex `CommsCheck failed …` und
  verweist auf das Offline-FAQ. Details siehe [Runtime-Helfer](../doc.md#comms-check).
- **Offline-Fallback:** `!offline` gibt höchstens einmal pro Minute das Kodex Offline-FAQ aus.
  Es erinnert Schritt für Schritt daran, wie die Crew den Uplink erneut herstellt:
  - Terminal oder Hardline suchen, Relay koppeln und Jammer-Override prüfen - bis
    dahin bleibt der Kodex stumm.
  - Mission normal fortsetzen: HUD liefert lokale Logs. HQ-Deepsaves/Cloud-Sync
    laufen erst nach der Rückkehr ins HQ (HQ-only, keine Save-Sperre).
  - Ask→Suggest-Fallback nutzen: Aktionen als "Vorschlag:" kennzeichnen und auf
    Bestätigung warten.

### Start & Load - LLM-Dispatcher (ohne externe Runtime)

Siehe das [Mini-Einsatzhandbuch](spieler-handbuch.md#mini-einsatzhandbuch) für Startbefehle.

**Akzeptierte Zusätze:**

- Nach `solo`/`npc-team`/`gruppe` darf optional `klassisch` oder `schnell` folgen
  (auch `classic|fast`).
- `npc-team` akzeptiert `0-4` NPC-Begleiter (Team gesamt 1-5); Arena nutzt dieselbe Obergrenze.
- Erlaubte Rollen-Kurzformen: `infil`, `tech`, `face`, `cqb`, `psi`.
- Vor jedem Einsatz ruft der Dispatcher `!radio clear` und `!alias clear` auf,
  damit Funk- und Alias-Logs ohne Altlasten starten.
- Alias- und Funkbefehle akzeptieren beliebige Groß-/Kleinschreibung (`!alias`,
  `!ALIAS`, `!Radio Log` usw.).

**Fehlertexte:**

- `npc-team 5` → "NPC-Begleiter: 0-4 (Team gesamt 1-5). Bitte erneut eingeben (z. B. npc-team 3)."
- `gruppe 3` → "Bei gruppe keine Zahl angeben. (klassisch/schnell sind erlaubt)"

**Semver (Save-Laden):**

- Save lädt, wenn `major.minor` aus `zr_version` mit `ZR_VERSION` übereinstimmt;
  Patch-Level wird ignoriert.
- Mismatch → "Kodex-Archiv: Datensatz vX.Y nicht kompatibel mit vA.B. Bitte
  HQ-Migration veranlassen."

**Save v6 – Pflichtfelder & Kompatibilität**

- _Referenz-Fixture:_ Ein vollständig ausgefüllter v6-Teststand (inkl.
  Cross-Mode-Pfaden, `logs.psi[]`, Arena-Trace) liegt unter
  [`internal/qa/fixtures/savegame_v6_test.json`](../internal/qa/fixtures/savegame_v6_test.json).
- _Single Source:_ Das vollständige Schema steht in
  `systems/gameflow/speicher-fortsetzung.md`. README und Toolkit zitieren nur
  Auszüge; neue Saves benutzen ausschließlich die v6-Struktur mit
  `party.characters[]` als kanonischem Roster (Legacy-Mirror
  `team.members[]` bleibt nur für Import/Export erhalten).
- Loader akzeptiert Wrapper-Felder wie `Charaktere`/`characters` und hebt sie
  beim Import auf `party.characters[]`/`team.members[]`; der Serializer gibt
  ausschließlich das kanonische Roster aus und erzeugt keine Wrapper-Struktur
  in Saves oder HQ-Exports.
- `character.id`, `character.attributes.SYS_max`,
  `character.attributes.SYS_installed`, `character.attributes.SYS_runtime`,
  `character.attributes.SYS_used`, `character.stress`, `character.psi_heat`,
  `character.cooldowns` sind immer Teil des HQ-Deepsaves.
- `campaign.px`, `economy` (inklusive `wallets{}`), `logs` (inklusive `hud`,
  `trace`, `artifact_log`, `market`, `offline`, `kodex`, `alias_trace`,
  `squad_radio`, `foreshadow`, `fr_interventions`, `psi`, `arena_psi`,
  `flags`, `flags.merge_conflicts`) sowie `ui` und `arena` werden vom
  Serializer garantiert. `logs.field_notes[]` ist optional; fehlt der Block,
  legt der Serializer ein leeres Array an. `character.quarters` wird für HQ/
  Profil-Infos mitgespeichert; `arc_dashboard.timeline` hält Kampagnenereignisse
  fest. Der Arena-Block kennt `queue_state=idle|searching|matched|staging|active|completed`,
  `zone=safe|combat`, `match_policy=sim|lore` und klemmt Teamgrößen hart auf 1-5.
  Der SaveGuard wertet `queue_state` mit und blockiert HQ-Deepsaves, solange der State nicht
  `idle` ist; Matchmaking-States zählen als aktiv. Saves aus Chronopolis/CITY
  werden mit "SaveGuard: Chronopolis ist kein HQ-Savepunkt" verworfen. Der
  Load-Merge
  schreibt ein Trace-Event `merge_conflicts` (Queue-State/Zone, Reset-/Resume-
  Marker, `conflict_fields`, `conflicts_added`, Gesamttally) und dedupliziert
  identische Konflikt-Records, damit Cross-Mode-Imports einheitliche Belege
  liefern. Solo-/Px-5-Runs stapeln offene `campaign.rift_seeds[]` ohne Hard-
  Limit; beim HQ-Merge deckelt die Runtime den offenen Pool auf 12, schiebt
  Überschüsse an ITI-NPC-Teams und schreibt sowohl ein
  `rift_seed_merge_cap_applied`-Trace (kept/overflow) als auch einen
  `merge_conflicts`-Eintrag (`field='rift_merge'`). Arena-Resets setzen immer einen
  HUD-Toast "Merge-Konflikt: Arena-Status verworfen" und hinterlegen den
  Konflikt im Trace; `reset_arena_after_load()` priorisiert `arena.previous_mode`
  und `resume_token.previous_mode`, damit der Kampagnenmodus nach aktiven Läufen
  auf den Ursprungswert zurückspringt.
- `ui` enthält neben `gm_style`/`intro_seen`/`suggest_mode`/`action_mode` die
  Accessibility-Felder `contrast`, `badge_density` und `output_pace` sowie das
  optionale `voice_profile`. Migration und Serializer ergänzen fehlende Felder
  mit Defaults (`standard|normal|gm_second_person`, `action_mode=uncut`),
  sodass der SaveGuard den normalisierten UI-Block prüft.
  `normalize_save_v6()` synchronisiert `ui.suggest_mode` und
  `character.modes`: Sobald eine Seite `suggest` gesetzt hat, aktiviert der
  Save beide Flags und rendert das HUD-Tag `· SUG` deterministisch.
- Direkt nach dem Laden spiegelt `ensure_economy()` fehlende
  Credits-Fallbacks (`economy.credits`) auf den HQ-Pool `economy.cu`, bevor
  Wallets oder Arena-Guards greifen.
- Serializer und Migration erzwingen `save_version: 6` - auch Legacy-Saves
  landen nach `migrate_save()` auf dieser Version und ergänzen `ui.intro_seen`
  als boolesches Feld.
- Wallets sind Maps `wallets{id → {name,balance}}`; Arrays oder namenlose
  Guthaben gelten als fehlerhaft und wandern in `logs.flags.merge_conflicts[]`
  (`field='wallet'`).
  Host-Vorrang bleibt erhalten, die Rest-Verteilung wird im
  `merge_conflicts`-Trace gespiegelt (`source`/`target`/`kept`/`handoff`), damit
  Wallet-Splits in Solo→Koop→PvP-Runs nachvollziehbar bleiben.
- **Legacy-Spiegel für GPT (ohne runtime.js):** Falls ein älterer Save noch
  Wurzel-Schlüssel wie `sys`, `sys_used`, `sys_installed`, `sys_runtime`,
  `stress`, `psi_heat` oder `cooldowns` besitzt, legt die Spielleitung beim
  Laden vorab den Block `character{}` an:
  1. `character.id`, `character.name`, `character.rank`, `character.callsign`
     aus gleichnamigen Root-Feldern übernehmen (falls belegt).
  2. `character.stress`, `character.psi_heat` und `character.cooldowns`
     aus den alten Root-Feldern kopieren und die Wurzelvarianten danach
     verwerfen.
  3. `character.attributes{SYS_max,SYS_installed,SYS_runtime,SYS_used}` aus
     `sys`/`sys_max`, `sys_installed`, `sys_runtime` bzw. `sys_used` bilden;
     weitere Werte aus `attributes{}` nur ergänzen, niemals überschreiben.
  4. Optionale Felder wie `modes[]`, `self_reflection` oder `lvl` ebenfalls in
     `character{}` verschieben, sofern sie vorher an der Wurzel lagen.
     Auf diese Weise steht dem GPT immer das vollständige Save-v6-Schema zur
     Verfügung, auch ohne die lokale `runtime.js`.

**Quick-Hilfe:** `!help start` - listet alle vier Befehle mit Kurzbeschreibung.

### Dispatcher- und HUD-Befehle

- `!rules stealth` - zitiert die Passage zu Schleichen.
- `!gear cyberware` - zeigt Ausrüstung oder Implantate.
- `!save` - speichert einen Deepsave (nur im HQ; SaveGuard blockt bei Offline-
  Ende mit "SaveGuard: Offline - HQ-Deepsave erst nach Re-Sync - HQ-Save
  gesperrt.").
- `!load` - lädt den letzten Deepsave.
- `!suspend` - legt einen flüchtigen Szenen-Snapshot für eine Pause an.
- `!resume` - setzt den letzten Suspend-Snapshot exakt einmal fort und stellt
  Initiative-Leiste sowie HUD-Timer wieder her.
- `!autosave hq` - schaltet Auto-Save im HQ.
- `!accessibility` - öffnet den Accessibility-Dialog (Kontrast, Badge-Dichte, Output-Takt).
  Optionen landen als `contrast=standard|high`, `badge_density=standard|dense|compact`,
  `output_pace=normal|fast|slow` im Save; der Toast "Accessibility aktualisiert …"
  bestätigt jede Änderung.

- `!gear shop` - zeigt Shop-Tier-Liste.
- `!psi heat` - erklärt Psi-Heat und Burn.

- `!hud status` - listet alle Zustände.
- `!reveal artifact` - zeigt Artefakt-Infos im HUD.
- `!regelcheck modul` - zwingt die KI, Regeln aus dem genannten Modul zu laden.
- `!regelreset` - setzt den Regelkontext nach Warnhinweis zurück und lädt alle Module neu.
- `modus verbose` - Filmisch an; Toast `GM_STYLE → verbose (persistiert)`.
- `modus precision` - Kurzprotokoll an (nur taktische Abschnitte); Toast
  `GM_STYLE → precision (persistiert)`.
- `modus action|gewalt konform|frei` - Action-Contract umschalten; Alias:
  `uncut` → `frei`. `modus action` zeigt den aktuellen Wert, Legacy-Werte wie
  `fsk12` oder `standard` werden auf `konform` normalisiert.
- `!px` - zeigt aktuellen Paradoxon-Stand inklusive ETA (Heuristik) aus `px_tracker()`.
- `!fr help` - zeigt den aktuellen FR-Status.
- `!dashboard status` - fasst das Arc-Dashboard (Seeds, Fraktionsmeldungen,
  offene Fragen) als Report zusammen.
- `!help dashboard` - Spickzettel für `!dashboard status` und
  Arc-Dashboard-Evidenzen.
- `!boss status` - meldet `Gate x/2 · Mission FS y/4` (Core) bzw. `y/2`
  (Rift) und zeigt Gate-Fortschritt vs. Saisonstand.

### Boss-Gates, Suggest-Modus & Arena (Kurzinfo)

- **Boss-Gates.** Ab Mission 5/10 setzt die Runtime `GATE 2/2` plus `FS 0/4`
  (Rift: `FS 0/2`) als Badge und Toast. `ForeshadowHint()` erhöht nur den
  `FS`-Zähler, das Gate bleibt fest. In Szene 10 erscheint der Boss-Toast mit
  der Schadensreduktion (skaliert nach Teamgröße und Boss-Typ). Nach dem
  Missionsende feuert der Auto-Reset für Self-Reflection (Mission 5 **und**
  Mission 10) und setzt den Status per Helper wieder auf `SF-ON`.
- **Suggest-Modus.** `modus suggest` aktiviert beratende Vorschläge (`SUG-ON`),
  `modus ask` schaltet zurück (`SUG-OFF`). Das SUG-Badge bleibt unabhängig von
  Self-Reflection aktiv.
- **Self-Reflection.** Quelle bleibt stets `character.self_reflection`;
  `logs.flags.self_reflection` spiegelt den Wert nur. **Einzige
  Schreib-Schnittstelle ist `set_self_reflection()`**, das sowohl Charakter-
  als auch Flag-Wert setzt. Automatische Resets nach Mission 5 **und** 10
  laufen über denselben Helper, schreiben `self_reflection_auto_reset_*`
  (inkl. History-Eintrag pro Mission) und bleiben damit deterministisch.
- **PvP-Arena.** `arenaStart()` setzt `location='ARENA'`, blockiert HQ-Saves bis
  zum Exit, markiert Px-Boni pro Episode und hält die PvP-Policy im Save
  (`arena.match_policy=sim|lore`). `sim` steht für Sim/Range-Training,
  `lore` erlaubt Cross-Alignment als Lore-Kampf; der HUD-Toast nennt die
  aktive Policy. PvP ist optionales Endgame-Modul; Standardkampagnen laufen
  ohne Arena-Fokus weiter.
- **Phase-Strike Arena.** `arenaStart(options)` zieht die Arena-Gebühr aus
  `economy`, setzt `phase_strike_tax = 1`, blockiert HQ-Saves und meldet Tier,
  Szenario, Policy sowie Px-Status per HUD-Toast. Die Gebühr wird parallel im HQ-Pool
  (`economy.cu`) und im Credits-Fallback (`economy.credits`) geführt;
  `sync_primary_currency()` hält beide Felder deckungsgleich und protokolliert
  bei Arena-Gebühren, Wallet-Splits und Markt-Käufen `currency_sync`-Traces
  mit Delta und Grund.

## Exfil-Fenster & Sweeps {#exfil-fenster--sweeps}

Sobald das **Primärziel** erreicht ist, öffnet sich ein
**Exfil-Fenster** mit einer **Ablaufzeit (RW)**.
Spielende können nun **optionale Sweep-Szenen** spielen
(z. B. Räume nachlooten, Keycards nutzen, Spuren sichern).
Jede Sweep-Szene **kostet RW** und **erhöht den Stress** des
ausführenden Agenten. Sweep und Rücksprung laufen **nie parallel** -
das RW muss am **IA** oder einem Alt-Anchor **bewusst armiert** werden.
Sinkt der RW-Timer auf **0**, erzwingt das System einen
**Hot-Exfil** (kurzer, riskanter Abzug).
Misslingt dieser deutlich, kann bei aktivierter Px-Verlust-Regel ein
**Resonanzverlust (Px-1)** greifen.
Standardmäßig bleibt der Paradoxon-Index stabil; die Strafe ist als Opt-in-Schalter verfügbar.
**0-2 Sweeps empfohlen:** 1 = Low-Risk Bonus, 2 = spürbares Tikken,
3+ = Hot-Exfil-Gefahr. [Details](../gameplay/kampagnenstruktur.md#post-op-sweep-optional)
**Ziel:** Freiraum für Erkundung - unter spürbarem Zeit- und Nerven-Druck.
**HUD** zeigt ab Zielerfüllung `ANCR Ort · RW mm:ss` und `Stress`. (Speichern
weiterhin ausschließlich im **HQ**.)

*(Die folgenden SaveGuard-Strings sind KI-Spielleiter-Referenz und nicht für Spieler gedacht.)*

Die Runtime spiegelt das Fenster parallel nach
`campaign.exfil{active, armed, hot, ttl, sweeps, stress, anchor, alt_anchor}`.
Solange `campaign.exfil.active` wahr ist, verweigert der HQ-Serializer den Deepsave mit
"SaveGuard: Exfil aktiv - HQ-Save gesperrt.". Nach der Rückkehr ins HQ setzt `campaign.exfil`
alle Werte (inkl. Anchor und Stress) zurück; das Save-Schema führt dieselben Felder als Referenz.
HQ-Saves akzeptieren ausschließlich vollständig installierte Systeme:
`character.attributes.SYS_installed` muss `SYS_max` entsprechen, die Runtime-Last darf den
installierten Wert nicht überschreiten. Weicht die Installation ab, bricht `save_deep()` mit
"SaveGuard: SYS nicht voll installiert - HQ-Save gesperrt." ab; eine Runtime-Last über den
installierten Slots führt zu "SaveGuard: SYS runtime overflow - HQ-Save gesperrt.". Stress
und Psi-Heat tragen denselben SaveGuard-Suffix, um HQ-Sperren klar zu markieren.
Speichern außerhalb des HQs meldet "SaveGuard: Speichern nur im HQ - HQ-Save gesperrt.".

### HUD-Shortcuts für Exfiltration

- `!exfil arm [ANCR]` - armiert den Rückweg am aktuellen Anchor und erzeugt einen HUD-Toast.
- `!exfil alt [ALT-ANCR]` - setzt oder löscht (ohne Parameter) den Alt-Anchor mit sofortigem Toast.
- `!exfil tick mm:ss` - aktualisiert den RW-Timer und loggt die Restzeit im HUD-Protokoll.
- `!exfil status` - fasst Anchor, RW und Armierung als Text zusammen.

Alle Befehle füllen das HUD-Log (`logs.hud`) automatisch und halten die Szene-
Overlays synchron. Sonder-Overlays für Verfolgungen und Massenkonflikte nutzen
den Helper `hud_event(event, details)`: Er akzeptiert ausschließlich
`vehicle_clash` oder `mass_conflict`, normalisiert numerische Felder
(`tempo`, `stress`, `damage`, `chaos`, `break_sg`), setzt fehlende Szenenindizes
auf den aktuellen Szenencounter und ergänzt fehlende ISO-Zeitstempel. Jede
Erzeugung legt parallel einen Trace `hud_event` ab. Strukturierte HUD-Events
folgen der Form `{event, scene?, details{…}, at?}`.

### HUD-Schnellhilfe (`/help`)

- `!help start` / `/help start` - Start- und Ladebefehle als knapper Spickzettel.
- `!help urban` / `/help urban` - Urban Quick-Card: Deckungsgrade, Verfolgungsdistanzen, Toast-Tags.
- `!help sg` / `/help sg` - SG- & Exploding-Benchmark: Würfelgrößen, Zielwerte, Phasenrichtwerte.

Alle Quick-Cards halten die Toasts auf sechs Wörter begrenzt und liefern
filmische Callouts für das HUD.

## Level & XP-Kurve {#level--ep-kurve}

Das Progressionssystem gliedert sich in zwei Phasen:

- **Phase 1 (Lvl 1–10):** Jede abgeschlossene Mission = sofort +1 Level.
  Schneller Einstieg, maximale Motivation.
- **Phase 2 (ab Lvl 11):** Gestaffelte XP-Kurve:

| Level | XP pro Level | Kumulativ |
|-------|-------------|-----------|
| 1–10 | 1 XP (= 1 Mission) | 10 XP |
| 11–20 | 2 XP | 30 XP |
| 21–30 | 3 XP | 60 XP |
| 31–50 | 4 XP | 140 XP |
| 51–100 | 5 XP | 390 XP |

**Level-10-Gate (Chronopolis):** Mit Erreichen von Level 10 schaltet Kodex den
**digitalen Chronopolis-Schlüssel** frei — eine kryptographische Signatur,
die bei jedem Schleusendurchgang live dechiffriert wird. Erst danach ist der
optionale City-Zugang freigeschaltet.

**Prestige-Meilensteine** bei Level 25 (*Bewährter Agent*), 50 (*Veteran*),
75 (*Koryphäe*) und 100 (*Legende*) — kosmetisch + Titel.
Kanonische Details: [Progressionssystem](zeitriss-core.md#levelaufstieg-fortschritt).

Pro Aufstieg genau eines: `+1 Attribut` oder `Talent/Upgrade` oder `+1 SYS`.
Doppelte Gratis-Upgrades im selben Level sind im Standard ausgeschlossen;
Ausnahmen nur als explizite Sonderregel der Kampagne.
Ab Attribut 11 wechselt das Würfelsystem auf W10, ab 14 kommt der Heldenwürfel.
Siehe [Core-Ops CU-Belohnungen](../systems/currency/cu-waehrungssystem.md#core-ops-belohnungen)
für wirtschaftliche Details.

## Save-Taktung (verbindlich)

Kodex setzt Save-Prompts im HQ an festen Checkpoints:

1. vor jedem Briefing/Absprung,
2. nach jedem Debriefing,
3. nach längeren HQ-Freerun-Phasen (Shop/Clinic/Werkstatt),
4. vor Chronopolis-Schleuseneintritt,
5. nach Chronopolis-Rückkehr ins HQ.

Für Stabilität gilt: pro HQ→Einsatz→HQ-Zyklus ein frischer Chat mit DeepSave-Import.

## Gruppen-Todesentscheid (Core/Rift/Chronopolis)

Im Modus `gruppe` stoppt Kodex bei einem Spieler-Tod die Szene und fordert eine
verbindliche Entscheidung:

- **Tod bleibt Kanon der Geschichte**, oder
- **Neuladen vom letzten Gruppen-DeepSave** (neues Chatfenster, Save posten,
  Einsatz neu starten).

Ohne diese Gruppenentscheidung wird die Geschichte nicht fortgesetzt.

## Regelreferenz

### Proben & Schwierigkeitsgrad

Bei ungewissen Aktionen legt die Spielleitung einen **Schwierigkeitsgrad (SG)** fest. Faustregeln:
SG 5 = leicht, SG 8-9 = mittel, SG 12 = schwierig, SG 15+ = sehr schwer.
Ausführliche Tabellen stehen in
[core/zeitriss-core.md](zeitriss-core.md) und
[core/wuerfelmechanik.md](wuerfelmechanik.md).

Die **Riftstufe** entspricht der Anzahl offener Seeds. Erst nach der Episode
erhöht jeder Seed den Schwierigkeitsgrad um +1 und steigert die CU-Belohnung (1
Seed = ×1.2, 2 Seeds = ×1.4 usw.). Details findet ihr unter
[Offene Rifts](../gameplay/kampagnenstruktur.md#offene-rifts).
Rift-Missionen verwenden weiße Stern-Symbole (☆), die den SG-Bonus ab Episodenende anzeigen.
Ein Seed entspricht einem Stern und erhöht die Schwelle um +1.
Mehr als fünf Seeds können als `☆☆☆☆☆+` notiert werden.
[Kreative Generatoren](../gameplay/kreative-generatoren-missionen.md).

### Difficulty-Konverter

| ☆-Symbole | SG-Zuschlag |
| --------- | ----------- |
| ☆         | +1          |
| ☆☆        | +2          |
| ☆☆☆       | +3          |
| ☆☆☆☆      | +4          |
| ☆☆☆☆☆     | +5          |
| ☆☆☆☆☆+    | +6 und mehr |

Paramonster und Bosse verwenden Totenkopf-Icons (💀) als eigenen
Schwierigkeitswert. Das HUD blendet 💀 **kontextsensitiv bei Boss-Encounters**
ein (Szene 10 Core/Rift). Diese Angabe hilft bei der Einschätzung des
Kampfpotenzials und verändert **nicht** den SG einer Mission.

### Wichtige Makros

Makros siehe
[speicher-fortsetzung.md](../systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick),
den Abschnitt zum
[Paradoxon-Index](../systems/gameflow/speicher-fortsetzung.md#paradoxon-index) und zum
[Immersiven Laden](../systems/gameflow/speicher-fortsetzung.md#immersives-laden):

- `ClusterCreate()`
- `ClusterDashboard()`
- `launch_rift(id)` - startet nach der Episode eine eigenständige
  Rift-Mission
- `scan_artifact()`
- `seed_to_hook(id)`
- `resolve_rifts(ids)`
  - lässt ein ITI-Team Seeds nach einer Mission beseitigen (50/50 Bericht)

### KPI-Cheat-Sheet pro Phase

| Phase      | Fokus           | Beispiel-KPI          |
| ---------- | --------------- | --------------------- |
| Briefing   | Klarheit & Hook | 5 Kerninfos, 1 Bild   |
| Aufklärung | Hinweise finden | Foreshadow-Hinweis    |
| Konflikt   | Spannung        | Exploding 6 nutzen    |
| Auswertung | Konsequenzen    | Rufpunkte, Ressourcen |

### Modulübersicht

| Regelmodul                                             | Muss | Soll | Kann | Kurzinfo / Link                            |
| ------------------------------------------------------ | :--: | :--: | :--: | ------------------------------------------ |
| [Grundwürfelsystem (W6)](wuerfelmechanik.md)      |  ✅  |      |      | Kernmechanik - explodierende Würfel        |
| [Paradoxon-Index](zeitriss-core.md)               |  ✅  |      |      | Kampagnen-Fortschritt                      |
| [Boss-Rhythmus 5/10](../gameplay/kampagnenstruktur.md)    |  ✅  |      |      | Mini- & Episoden-Boss nach Missionsnummern |
| [Stress-System](../characters/zustaende.md)               |      |  ✅  |      | Für psychische Belastung und Druck         |
| [W10-Variante ab Attribut 11](wuerfelmechanik.md) |      |  ✅  |      | Breitere Würfelspanne für große Missionen  |
| [Psi-Kräfte / Psi-Heat](../systems/kp-kraefte-psi.md)     |      |  ✅  |      | Standardmodul, wissenschaftlich erklärbar  |

### Standardausrüstung {#standardausruestung}

Chrononauten starten mit einer einheitlichen Grundausrüstung:

- **AR-Kontaktlinse (Retina-HUD):** Energieautark (Kinetik + Körperwärme),
  integrierte Mikro-CPU für lokales HUD & Logging. Projiziert Informationen
  direkt ins Sichtfeld und funktioniert auch ohne aktive Kodex-Verbindung.
- **Comlink (Ohrstöpsel, ≈ 2 km):** Kurzstreckenfunk (durch Gelände/Jammer
  beeinflussbar), ebenfalls energieautark (Kinetik + Körperwärme) mit eigener
  Mikro-CPU. Übernimmt die
  Kodex-Synchronisation; fällt die Verbindung aus, bleibt das HUD lokal aktiv.
- Riss-Tracker (temporaler Resonator) - warnt vor Resonanz, siehe
  [Temporale Tools](../characters/ausruestung-cyberware.md#temporale-tools)
- Basiswaffe nach Einsatzprofil
- Universelles Werkzeug oder Scanner

_Details zur Hardware siehe_
[HUD & Comms - Spezifikation](../characters/hud-system.md#hud-comms-spec).
_HUD-Zustände & kontextsensitive Icons:_ [HUD-Icons](../characters/hud-system.md#hud-icons).

> **Hardwareprinzip:** Alle Signalinteraktionen erfordern reale Geräte
> (Kontaktlinse/Comlink/Kabel/Relais). Armbänder sind erlaubt, projizieren aber
> kein HUD; externe Projektoren gibt es nicht. **Keine Batterien oder
> Ladezyklen** - die Geräte speisen sich aus Bewegung und Körperwärme.
> **Kein Handgelenk-Default:** HUD bleibt Retina-Linse/Comlink/Terminal, keine
> Projektionen vom Handgelenk.

> **Mixed-Reality-HUD:** Das Interface erscheint als Retina-Holo direkt im
> Sichtfeld (Terminator-/AR-Stil) und begleitet jede Epoche. **HQ = immer
> Kodex-Uplink**; im Feld stellt das Comlink/Kodex-Light die Verbindung. Bei
> Funkstille bleibt das lokale HUD aktiv (Scans/Logs laufen weiter, Kodex
> antwortet erst nach Re-Link).

#### Mini-FAQ

- _Muss ich laden?_ → Nein, **keine Batterien**; autark.
- _Geht HUD ohne Kodex?_ → Ja, **lokal** (Edge-Compute).
  [HUD-Spec](../characters/hud-system.md#hud-comms-spec)
- _Wie weit reicht Funk?_ → **≈ 2 km**, Gelände/Jammer wirken.
  [Toolkit](../systems/toolkit-gpt-spielleiter.md#funk-signale)
- _Relais/Kabel?_ → heben Reichweiten- oder Jammer-Beschränkungen auf;
  `comms_check()` zählt sie als `relays=true`.
- _Wann spricht der Kodex?_ → Nur mit aktivem Comlink-Uplink. **HQ/ITI = Vollzugriff**
  (Offline gilt nur im Einsatz). In Funkepochen gilt eine **ca. 2 km Bubble ab
  Einstiegspunkt**, erweiterbar per Relais/Kabel; Jammer oder funklose Ären
  (z.B. Mittelalter) schalten den Kodex stumm → nur HUD/Logs laufen. `!offline`
  höchstens **1×/Minute** triggert das Offline-FAQ, bis der Hardware-Link wieder
  steht. Endet eine Mission offline, blockt der SaveGuard jeden HQ-Deepsave,
  bis der Re-Sync erfolgt.

HUD-Zustände erscheinen als Backticks. Alle Icons sind **kontextsensitiv** und
werden automatisch eingeblendet, wenn der jeweilige Zustand eintritt:
- **Dauer-Anzeige** (immer sichtbar): Lvl, ❤️‍🩹 Vital, 🧠 Stress, 👁️ Tarnung
- **Zustands-Icons** (bei Eintritt → bei Ende weg): 🌀 Paradoxon (Px-relevant),
  🩸 Blutung, ☠️ Vergiftung, ⏱️ Countdown, 🛡️ Abwehr, ✋ TK-Cooldown
- **Situations-Icons**: 💀 bei Boss-Encounters (Szene 10 Core/Rift),
  ☆ nach Episodenabschluss (SG-Bonus/Loot-Multi durch offene Rifts)

Das HUD bleibt clean — nie alle Icons gleichzeitig, nur was gerade relevant ist.

## Loot-Matrix

| Mission  | Standard-Loot                                       | Boss-Loot               | Artefakt      |
| -------- | --------------------------------------------------- | ----------------------- | ------------- |
| **Core** | Forschungsergebnisse · Datenchips · Cash · Upgrades | Spezialwaffe / Gear-Mod | ✘             |
| **Rift** | Relikte · Ermittlungsakten · experimentelle Gear    | Artefakt-Wurf bei Boss  | ✔ (nur hier) |

## Loot-Quickref

| Mission-Typ | Roll-Macro / Tabelle     | Ergebnis-Typen         |
| ----------- | ------------------------ | ---------------------- |
| Core-Op     | `roll_from("ItemTable")` | ITEM · UPGRADE · CASH  |
| Rift-Op†    | `roll_legendary()`       | ARTEFAKT (bei 1W6 = 6) |

† Das Artefakt-Wurfskript greift ausschließlich in Szene 10 (Rift-Boss)
  automatisch und bleibt bei **max. 1 Artefakt pro Mission**. Relikte zählen
  als Story-Items und nutzen den normalen Generator.

**Artefakt-Sink:** Artefakte bleiben handelbar wie Gear (Tausch, Schenkung oder
Verkauf zulässig), aber die Abrechnung läuft über Research-/Archivwerte statt
Marktpreis. Archivieren zieht sie endgültig aus der Wirtschaft, CUs fließen nur
über den HQ-Pool und nie als automatischer Sellout.

## Kampagnenhierarchie

Kurzfassung — kanonische Details: [Kampagnenstruktur](../gameplay/kampagnenstruktur.md#kampagnenhierarchie).

- **Mission** — einzelner Einsatz von etwa 12 Szenen.
- **Episode/Fall** — sammelt rund zehn Missionen im gleichen Setting.
- **Arc** — mehrere Episoden bilden einen Handlungsbogen.
- **Kampagne** — verknüpft mehrere Arcs zur Gesamtgeschichte.

## Struktur

Die folgende Tabelle listet die zentralen Regelmodule und Schnellzugriffe.
Quickrefs und Unterabschnitte sind zur schnellen Orientierung mit aufgeführt.

| Datei                                                                                           | Inhalt                                        |
| ----------------------------------------------------------------------------------------------- | --------------------------------------------- |
| [core/spieler-handbuch.md](spieler-handbuch.md)                                                    | Spieler-Handbuch (Slot 1, Regeln & Einstieg)  |
| [core/zeitriss-core.md](zeitriss-core.md)                                                  | Grundregeln und Setting                       |
| [core/wuerfelmechanik.md](wuerfelmechanik.md)                                              | Würfelsystem & Proben                         |
| [Quickref](wuerfelmechanik.md#schwierigkeits-benchmark-tabelle)                            | Psi- & Konflikt-Quickref                      |
| [characters/charaktererschaffung-grundlagen.md](../characters/charaktererschaffung-grundlagen.md)  | Charaktererschaffung (Grundlagen)             |
| [characters/charaktererschaffung-optionen.md](../characters/charaktererschaffung-optionen.md)      | Optionen, Archetypen & Teamrollen             |
| [characters/ausruestung-cyberware.md](../characters/ausruestung-cyberware.md)                      | Ausrüstung, Waffen & Implantate               |
| [characters/zustaende.md](../characters/zustaende.md)                                              | Zustände, Paradoxon & Statusregeln            |
| [characters/hud-system.md](../characters/hud-system.md)                                            | HUD-Interface & Anzeige-Logik                 |
| [gameplay/kampagnenstruktur.md](../gameplay/kampagnenstruktur.md)                                  | Kampagnenaufbau, Preserve vs Trigger & ITI-HQ |
| [gameplay/fahrzeuge-konflikte.md](../gameplay/fahrzeuge-konflikte.md)                              | Fahrzeuge & Konfliktsystem                    |
| [kreative-generatoren-missionen.md](../gameplay/kreative-generatoren-missionen.md)                 | Mission & Kampagnen-Generatoren               |
| [gen-begegnungen.md](../gameplay/kreative-generatoren-begegnungen.md)                              | NPC & Encounter-Gen                           |
| [Para-Creature-Generator](../gameplay/kreative-generatoren-begegnungen.md#para-creature-generator) | Urban Myth Edition                            |
| [Boss-Generator](../gameplay/kreative-generatoren-begegnungen.md#boss-generator)                   | Mini-, Arc- und Rift-Bosse                    |
| [gameplay/massenkonflikte.md](../gameplay/massenkonflikte.md)                                      | Verfolgungsjagden & Massenkonflikte           |
| [gameplay/kampagnenuebersicht.md](../gameplay/kampagnenuebersicht.md)                              | Kampagnenübersicht                            |
| [systems/kp-kraefte-psi.md](../systems/kp-kraefte-psi.md)                                          | Psi-Kräfte, Talente & Regeln                  |
| [systems/gameflow/speicher-fortsetzung.md](../systems/gameflow/speicher-fortsetzung.md)            | Speicher-/Fortsetzungssystem                  |
| [systems/gameflow/cinematic-start.md](../systems/gameflow/cinematic-start.md)                      | Cinematic-Gruppenstart                        |
| [systems/currency/cu-waehrungssystem.md](../systems/currency/cu-waehrungssystem.md)                | CU-Währungssystem                             |
| [systems/toolkit-gpt-spielleiter.md](../systems/toolkit-gpt-spielleiter.md)                        | Toolkit für die KI-Spielleitung               |
| [kampagnenstruktur.md](../gameplay/kampagnenstruktur.md#beispiel-episoden)                         | Beispiel-Episoden & Rift-Op                   |

Die Modulnummern spiegeln die Veröffentlichungshistorie wider. Nach Modul 6
folgt das nun veröffentlichte Modul 7, anschließend 8A und 8B.

Diese Referenz bündelt die wichtigsten Regelpfade, damit die Spielleitung
während der Session schnell zwischen Core-, Gameplay- und Systems-Regeln
wechseln kann.
Eine kompakte
[HUD-Übersicht zu Health, Stress und Zuständen](../characters/hud-system.md#hud-quickref)
fasst die wichtigsten Effekte zusammen.
Ausführliche Hintergründe liefert das Modul
[Cinematisches HUD-Overlay](../characters/hud-system.md#cinematisches-hud-overlay).

| Konflikt | Spannung | Exploding 6 nutzen |
| Auswertung | Konsequenzen | Rufpunkte, Ressourcen |

### Lines & Veils (optional) {#lines--veils-optional}

Gruppen können vor Spielbeginn gemeinsame Grenzen festlegen. **Lines** sind
Inhalte, die komplett ausgespart werden. **Veils** lassen Szenen bei Bedarf
ausblenden oder "fade to black" laufen. Notiert eure Vereinbarungen im Kodex,
damit alle denselben Rahmen kennen. Wer keine speziellen Grenzen setzen
möchte, kann den Abschnitt einfach überspringen.

#### Safety Sheet

| Thema                | Line (Tabu) | Veil (Off-Screen) |
| -------------------- | ----------- | ----------------- |
| Sexualisierte Gewalt | ✔          | -                 |
| Kindesgefährdung     | -           | ✔                |
| Body Horror          | -           | ✔                |

Der SL kann Szenen jederzeit _cutten_. Als Ingame-Begründung dient eine
Index-Senke im Kodex.

### ZEITRISS - Einleitung

> Die vollständige Einleitung (Setting, ITI-Hintergrund, Einstiegsoptionen) steht im [Spieler-Handbuch](spieler-handbuch.md#zeitriss-einleitung). Dieses Modul konzentriert sich auf SL-Regeln und Systemtabellen.

## Spielstart

Kanonische Spielertexte und Startbeispiele stehen im
[Spieler-Handbuch](spieler-handbuch.md#mini-einsatzhandbuch). Diese Referenz
führt nur die Dispatcher-/Runtime-Invarianten für die Spielleitung.

- Akzeptierte Startmuster: `Spiel starten (solo|npc-team [0-4]|gruppe
  [klassisch|schnell])` sowie `Spiel laden`.
- `Spiel laden` fordert ohne JSON-Block den Save an und setzt nicht aus dem
  Nichts fort.
- Legacy-Starts mit `preserve|trigger` in Klammern brechen mit Hinweis ab;
  Kampagnenmodus wird im HQ per `!kampagnenmodus` gesetzt.

`mixed|preserve|trigger` wählst du im HQ via `!kampagnenmodus`. Standard ist `mixed`
(alle Chrononauten starten beim Ordo Mnemonika im Mischpool). Der fokussierte Modus
(`preserve` oder `trigger`) ist erst nach einem **Fraktionsübertritt** relevant —
vorher bleibt `mixed` aktiv. Der Modus wird in `campaign.mode` und
`campaign.seed_source` hinterlegt, bevor Starts oder Arena-Abzweigungen laufen.
Legacy-Starts mit `preserve|trigger` in den Klammern werden mit einem Hinweis
abgebrochen.

Der Compliance-Hinweis entfällt; die Spielleitung fragt direkt nach gewünschter
Ansprache und Spielerzahl oder übernimmt beides aus dem Startbefehl.
Sie merkt sich beides, nutzt im Solo-Modus `Du` und im Gruppenmodus `Ihr`.
Das anschließende Startbanner übernimmt automatisch die passende Form.
Beispiel: `🟢 ZEITRISS 4.2.6 - Einsatz für dich gestartet` (Solo) bzw. `... für euch gestartet` (Gruppe).

- `Spiel starten (...)` → Charaktererschaffung → HQ-Phase → Mission
  ([Cinematic Start](../systems/gameflow/cinematic-start.md)).
- `Spiel laden` → Save einlesen → Rückblick → Mission fortsetzen
  ([speicher-fortsetzung.md](../systems/gameflow/speicher-fortsetzung.md)).

Wird `Spiel laden` ohne JSON-Block eingegeben, fordert GPT den Spielstand an
und setzt nicht aus dem Nichts fort.

Details zum Speichersystem findest du in
[speicher-fortsetzung.md](../systems/gameflow/speicher-fortsetzung.md).

Der Befehl `Speichern` erzeugt immer einen vollständigen **Deep Save** als
JSON-Block, der alle Fortschrittsdaten enthält. Tippe `Film ab!`, um eine
optionale Film-Zusammenfassung zu erhalten, die sich für Video-Generatoren
kopieren lässt. Alle Spielstände werden intern im Charakterbogen geführt -
separate Sicherungen sind nicht erforderlich. Jeder Save führt zusätzlich
`logs.trace[]` als E2E-Protokoll: Mission-Start, Rift-Launch und Arena-Init
landen dort mit Szene, Modus, Foreshadow-/FR-/Economy-Zusammenfassung und
HUD-Overlay, sodass der Run nachvollziehbar bleibt.
Beim HQ-Save ergänzt die Runtime außerdem ein `economy_audit`-Trace mit Level,
HQ-Pool, Wallet-Summe, Zielband (120/512/900+), Delta-Feldern und
Chronopolis-Sinks (Toast nur bei Abweichungen).
Das kanonische JSON-Schema `systems/gameflow/saveGame.v6.schema.json` bildet
alle Pflichtcontainer ab; `load_deep()` prüft Saves dagegen und bricht mit
`Save-Schema (saveGame.v6)` ab, wenn Felder fehlen oder Typen nicht passen.
Für MyGPT ist das Schema zusätzlich als **Kompakt-Profil** hinterlegt, das
ohne Binäranhang in den Wissensspeicher passt: Nutze die SaveGuard-Liste als
Pflichtset und den Baum `save_version/zr_version/location/phase → character
→ campaign/campaign.rift_seeds → team/party/loadout/economy.wallets → logs.*
→ arc_dashboard/ui/arena`, um den Speicherstand zu rekonstruieren. Die
Schema-Datei selbst wird nicht in den Wissensspeicher geladen und dient primär
der Validierung in Tools. `arc_dashboard` ist ein Pflichtcontainer im Schema;
der SaveGuard initialisiert den Block vor dem HQ-Save automatisch und bricht
mit Pflichtpfad-Fehlern ab, falls Dashboard-Felder fehlen oder verworfen
wurden.

```json
{
  "id": "CHR-1234",
  "modes": ["mission", "transparenz"]
}
```

Das Feld `modes` speichert alle aktiven Erzählstile und wird beim Laden mit
`modus <name>` reaktiviert.

Diese Befehle können frei eingegeben werden.
Sie dienen dazu, zwischen Einzel- und Gruppenspiel sowie Neu- oder Fortsetzung zu wählen.
Der Befehl `menü` (engl. `menu`, alternativ `optionen`) öffnet jederzeit das taktische HUD-Menü.
Clients ohne Unicode setzen `settings.ascii_only = true`, um eine ASCII-Version zu erhalten.
Im Menü lässt sich über `modus` der Erzählstil wechseln,
z.B. auf **Covert-Ops Technoir** oder den neuen **Suggest**-Modus.
Nach jeder Mission zeigt die Spielleitung **automatisch** einen
**Missions-Abschlussbildschirm** (Score-Screen):
Bewertung → Loot-Recap → CU-Auszahlung → XP/Level-Up → Ruf-Update.
Dieser Screen erscheint immer — der Spieler muss nicht danach fragen.

Erst danach öffnet sich das **HQ-Menü** mit drei Optionen:

1. **Schnell-HQ** - Heilen + Shoppen in wenigen Klicks, schnell wieder
   einsatzbereit.
2. **HQ manuell erkunden** - volle HQ-Szenen mit Shopbesuchen, Kodex-Begleitung,
   Fraktions-RP, Feilschen und ausführlichem Briefing/Quartierausbau.
3. **Auto-HQ & Save** - automatische Abwicklung der HQ-Pflichtschritte,
   danach folgt das nächste Briefing.

Anschließend kann die Gruppe den aktuellen Pfad fortsetzen oder einen
neuen Missionspfad wählen. Nach der Auswahl führt das HUD die
Kampagne fort - der Sprung gilt damit als abgeschlossen.

## ITI-HQ & Chronopolis {#hq-chronopolis}

- **ITI-HQ** bleibt das zentrale Hub mit Shop, Clinic, Workshop,
  Briefing und Fraktionskontakten; hier darf gespeichert werden.
- **HQ-Definition:** Zum HQ zählen das ITI-Nullzeit-Hub, alle ITI-Decks und der
  Pre-City-Hub. Chronopolis gehört **nicht** dazu (eigener Status `CITY`).
- **Pre-City-Hub** dient als gesicherte Übergangszone zwischen HQ und Chronopolis.
  - Zugang erfolgt nach dem ersten HQ-Briefing: Kodex bietet den "Transitpfad" an,
    sobald `campaign.loc` erneut auf `HQ` gesetzt wurde und die Crew mindestens
    Mission 2 erreicht hat.
  - Der Bereich liefert atmosphärische Brückenbeschreibungen (Landeplattform,
    Transitlifte, Sicherheitschecks) und einen täglichen Vorschau-Feed mit zwei
    Händlerangeboten (`Chronopolis-Vorschau`). Einkäufe bleiben deaktiviert, bis
    der eigentliche Stadtschlüssel vorliegt.
  - Nutzt den Transit, um Fraktionspräsenz zu teasen: kurze NPC-Begegnungen,
    Radiodurchsagen oder HUD-Einblendungen werden als "Briefing-Snippets"
    markiert. Die erste Warnung wird dabei intern vermerkt, damit das Banner beim
    späteren Stadteintritt nur einmal erscheint.
    Ab Level 10 schaltet die Runtime automatisch den digitalen Chronopolis-Schlüssel frei,
    setzt `logs.flags.chronopolis_unlocked=true` plus
    `chronopolis_unlock_level=10`, schreibt ein `chronopolis_unlock`-Trace-Event
    (Level/Quelle) und blendet den HUD-Toast
    `Chronopolis-Schlüssel aktiv - Level 10+ erreicht.` ein. Fehlende Flags werden
    beim Laden nachgezogen, falls Level oder Key-Item bereits vorliegen; Trace
    und Toast werden dann einmalig nachgereicht.
- **Chronopolis** ist ein optionaler City-Anbau ab Level 10. Der Zugang läuft
  über einen **digitalen Schlüssel**, den Kodex bei jedem Schleusendurchgang
  live dechiffriert — ab Level 10 hat der Chrononaut genug Verbindung mit der
  Nullzeit aufgebaut, damit Kodex die nötige Signatur berechnen kann.
  `campaign.loc` wechselt auf `CITY`, Speichern bleibt blockiert.
- **Stimmungswechsel:** Chronopolis hat immer die gleiche Stadtstruktur, aber
  Bevölkerung, Atmosphäre und Angebot wechseln in die Epoche der aktiven
  Episode. Zeitlich spielt die Stadt ein Szenario *nach der aktuellen Episode,
  als wäre sie gescheitert* — die Charaktere sehen, was mit der Welt passiert,
  wenn sie ihren Auftrag nicht schaffen. Das erzeugt Motivation und erlaubt
  gleichzeitig, ohne Missionsdruck in die jeweilige Epoche einzutauchen.
- **Kodex-Lore:** ITI-Forscher vermuten, dass Kodex durch das riesige Archiv
  ein Verständnis des Zeitstroms erlangt hat und temporäre Parallelrealitäten
  erschaffen kann, die "noch nicht fixiert" sind. Chronopolis existiert in
  diesem instabilen Zustand — real genug zum Handeln, aber ohne permanente
  Auswirkungen auf die Hauptzeitlinie.
- **Funktion:** Epochen-passende Ausrüstung beschaffen, Informationen über die
  aktive Epoche sammeln, NSCs aus der Zielzeit treffen — alles ohne den Druck
  einer laufenden Mission.
- **Maintainer-Blueprint:** Map-Layout, Performance-Ziele und Build-Roadmap
  liegen repo-intern für Art/Tech-Abgleiche bereit.
- In Chronopolis sind **offizielle** FR-Kontakte untersagt - keine direkten
  Fraktionsmeetings, keine diplomatischen Übergaben. Fraktionen wirken dort nur
  indirekt über Gerüchte, Auftragsgeräusche und HUD-Briefings. Rifts lassen sich
  in der Stadt nicht starten; Seeds und Board-Infos erscheinen weiterhin.
- HQ-Zutritt ist ITI-Agenten vorbehalten; Begleitpersonen bleiben unter strikter
  Aufsicht und erhalten keinen freien Zugang.
- Chronopolis-Services sind Wrapper um die HQ-Module mit eigenen
  Preisfaktoren.
- Das Tagesangebot folgt einem Daily-Roll: `!chrono stock` zeigt Rang- und Research-
  gated Slots, `!chrono tick` steuert den Missionsrhythmus der Rotation.
- Slot-Matrix pro Tag: 1 Temporal Ship, 3 Never-Was Gadgets und 4 Era-Skins
  rollen gleichzeitig; die Runtime spiegelt exakt diese Verteilung im Save.
- Warnbanner quittieren: `!chronopolis ack` bzw. `!chronopolis warn ack` setzt
  `logs.flags.chronopolis_warn_seen = true`, signalisiert per HUD-Toast die
  freigeschaltete Stadt und hält den Status im Save.
- Pre-City-Warncut: Der kurze Warnschnitt zwischen HQ und City setzt das Flag
  ebenfalls und verhindert doppelte Banner beim nächsten Laden oder nach HQ-
  Rückkehr. Erst `chronopolis_reset()` öffnet den Warnhinweis erneut.
- Chronopolis-Käufe landen im Kampagnen-Save: `logs.market[]` protokolliert
  Timestamp, Artikel, Kosten und Px-Klausel (Paradoxon-Hinweis); Toolkit- und Runtime-Hooks nutzen
  `log_market_purchase()` für Debrief-Traces. Der Debrief fasst die jüngsten
  Einkäufe über die Zeile `Chronopolis-Trace (n×): …` zusammen - inklusive
  Timestamp, Item, Kosten, Px-Hinweis sowie optionaler Notiz oder Quelle; ältere
  Einträge werden oberhalb von 24 automatisch abgeschnitten.
- Offline-Fallbacks landen ebenfalls im Save: `logs.offline[]` hält bis zu 12
  Protokollzeilen mit Trigger, Gerät, Jammer-Status, Reichweite, Relais und
  Szenenmarker fest; `offline_audit()` speist HUD und Debrief. Die
  Zusammenfassung `Offline-Protokoll (n×): …` nennt Trigger, Jammer-Status,
  Reichweite sowie Episoden-/Missionsmarker.
- Alias-Debriefs landen in `logs.alias_trace[]`: `!alias log Persona|Cover|Status|Notiz`
  (oder Key-Value wie `mission=M5|scene=3`) erzeugt einen Eintrag mit Timestamp,
  Persona, Cover, Status, Szene/Mission und optionaler Notiz. Der Debrief fasst
  die letzten Einträge in `Alias-Trace (n×): …` zusammen - Grundlage für
  spätere Follow-ups zu Alias-Läufen in Solo- und Großteam-Szenarien.
- Die Alias-Befehle sind case-insensitive; `!ALIAS LOG` und `!alias log`
  verhalten sich identisch.
- Squad-Funk landet in `logs.squad_radio[]`: `!radio log Sprecher|Channel|Meldung|Status`
  bzw. `speaker=Nova|channel=med|…` protokolliert Kanal, Meldung, Status, Szene
  und Ort. Die Debrief-Zeile `Squad-Radio (n×): …` dient als Persistenz-
  Nachweis für Funkprotokolle (S/M/XL-Konflikte).
- Auch die Funkbefehle tolerieren jede Groß-/Kleinschreibung (`!RADIO STATUS`,
  `!radio status` usw.).
- Foreshadow-Hinweise werden dedupliziert gespeichert; `Foreshadow-Log (n×): …`
  im Debrief listet Tag, Szene und Kurztext der jüngsten Hinweise für spätere
  Belege.
- Die Zeile `Runtime-Flags: …` dokumentiert Persistenzstatus
  (`runtime_version`, Compliance-Check, Chronopolis-Warnung, Action-Contract)
  sowie Offline-Hilfe-Zähler mit Timestamp des letzten Abrufs; bei
  protokollierten Cuts erscheint zusätzlich `How-to-Guard n×`.
- Koop-Teams erhalten nach jeder Mission `Wallet-Split (n×): …` für persönliche
  Auszahlungen (`economy.wallets{}`) und `HQ-Pool: … CU verfügbar` für den
  Restbestand (`economy.cu`). Beim Umstieg von Solo auf Koop erzeugt die Runtime
  sofort (`Wallets initialisiert (n×)`-Toast) Einträge für alle Figuren aus
  `party.characters[]`; die Fallback-Struktur `team.members[]` bleibt
  ausschließlich für Legacy-Migrationen reserviert.
  `initialize_wallets_from_roster()` verschiebt alte Solo-Guthaben vollständig
  in den HQ-Pool und öffnet anschließend die Wallets aller aktiven IDs. Ohne
  Spezialvorgaben teilt der GPT die Prämie gleichmäßig und holt eine
  Bestätigung ein, bevor Sonderwünsche umgesetzt werden. Alle Anpassungen am HQ-
  Pool spiegeln `economy.credits` automatisch, damit Arena- und Tool-Fallbacks
  denselben Kontostand sehen.
- **Hazard-Pay** wird vor dem Split verbucht: `hazard_pay`-Angaben im Debrief
  landen direkt im HQ-Pool (`Hazard-Pay: … CU priorisiert`), erst danach läuft
  die Wallet-Verteilung.
- **Deterministische Verteilung.** `Wallet-Split (n×)` listet alle IDs in
  Roster-Reihenfolge, verteilt Rundungsreste von oben nach unten und schließt
  mit einem einzigen Hinweis auf den verbleibenden HQ-Pool (`Rest … CU im
HQ-Pool`).
- **String-Eingaben für CU** bleiben erhalten: HQ-Pool (`economy.cu`) und
  Wallets (`economy.wallets{}`) akzeptieren numerische Strings wie `"1500"` und
  wandeln sie automatisch in ganzzahlige Chrono-Units um; nur nichtnumerische
  Werte fallen auf `0` zurück.
- **High-Level-Ökonomie:** Modul 15 enthält eine Tabelle für Level 100/400/1000
  (Belohnung vs. Sink). Hazard-Pay und `seed_multi` folgen der gleichen Formel,
  Wallet-Split und Rundungslogik bleiben unverändert.

## Spielmodi {#spielmodi}

Das HUD bietet mehrere Erzählstile, die sich jederzeit über den Befehl `modus`
umschalten lassen. **Klassik** läuft standardmäßig (filmisch mit mehr Taktik und
Realismus), der Kodex bleibt immer als Assistenz aktiv. Film bleibt als
optionale Cineastik-Schicht verfügbar. Die GPT-Spielleitung verkörpert alle
Rollen (NSCs, Umwelt, Kodex-HUD); der Kodex ist nur eine ihrer Stimmen - nicht
die Spielleitung selbst. Alle weiteren Modi sind optionale Zusätze:
| Modus | Kurzbeschreibung |
| --- | --- |
| **Klassik (Standard)** | Mischung aus filmischen und taktischen Regeln; realistischere, langsamere Variante. |
| **Film** | Schnelle Regeneration und cineastische Initiative für flüssige Action. |
| **Hard Sci-Fi** | Bodennaher Stil ohne Visionen, nüchterne Technik als Alternative zum Film-Look. |
| **Covert-Ops** | Minimale Paradoxon-Effekte; Risse nur als Sensorrauschen, keine Kreaturen. |
| **Transparenz** | Offene Würfe für volle Nachvollziehbarkeit. |
| **Suggest** | Einsteigerhilfe: Ergänzt die normalen 3+frei-Szenenvorschläge um nummerierte Tipps auf Abruf. |
| **Precision** | Extrem knappe Beschreibungen, Fokus auf Fakten. |
| **Verbose** | Blumige und ausführliche Darstellung, mehr Atmosphäre. |
| **Mission-Fokus** | Strikte Einsätze ohne Visionen, konzentriert auf klare Ziele. |

Mehrere Modi können parallel aktiv sein, etwa `precision` plus `transparenz`.

Beim Start aktiviert die Runtime **Klassik** plus die Missions- und Covert-Ops-
Filter (`mission_focus`, `covert_ops_technoir`). Film wird nur auf Wunsch
zugeschaltet.

Der Suggest-Modus wird mit `modus suggest` aktiviert und mit `modus ask` wieder deaktiviert.
Er ist als Noob-/Einsteigerhilfe gedacht; der normale Kodex bleibt davon
unabhängig aktiv (Regelhinweise, HUD, Logs).
Vorschläge markiert der Kodex sichtbar als `Vorschlag:` (Toolkit-Makro `suggest_actions()`)
und wartet auf ein bestätigendes oder korrigierendes Spieler-Feedback, bevor er fortfährt.
Die üblichen 3 + frei-Ideen nach einer Szene bleiben dabei bestehen; Suggest ergänzt sie nur
um spontane, nummerierte Mikro-Vorschläge auf Zuruf.

**Würfel-Ausgabe & Manual Mode.** Standard sind offene Würfel - die Runtime
startet neue Sessions direkt mit sichtbaren Würfen. Die Anzeige lässt
sich per `/roll open|hidden|manual` steuern: `hidden` blendet Ergebnisse aus
(nur Erfolgsabstand), `manual` nennt nur den benötigten Würfel samt Exploding-
Hinweis; ihr würfelt analog/digital und gebt das Ergebnis zurück. `/roll open`
schaltet die sichtbare Ausgabe wieder ein.

**Action-Contract.** ZEITRISS ist ein 18+ Tech-Noir-RPG. `action_mode` ist
immer `uncut`. Kämpfe, Hacking und Gewalt bleiben **filmisch**: Beschreibe
Beats, Dynamik, Geräusche, Licht, Impact und Risiko, aber abstrahiere die
Technik. Keine Schritt-für-Schritt-Gewaltanleitungen, keine sexuelle Gewalt.
Konsequenzen laufen über Noise, Stress, Heat oder enge Zeitfenster.
Loot-Blöcke sind regulär Teil des Gameplays (Waffen/Tools, Keys/Daten,
Wert/CU, Hinweise, "heißes Loot" markieren). Cleanup beschreibt nur Risiko und
Protokoll (Zeit, Stress, Noise/Heat) statt Schrittlisten; Exfil-Fenster bleiben
sichtbar und werden als Optionen geführt.

`noir_soft()` ist ein optionales HUD-Filter. Es zählt nicht als eigener Modus und lässt sich
mit jedem Stil kombinieren; aktiv wird es nur, wenn der Spielleiter den Macro aufruft.

Mission-Fokus wird beim Spielstart automatisch aktiviert;
Gefechte richten sich gegen NSCs, nicht gegeneinander.
Core-Ops involvieren meist Rivalen aus externen Machtblöcken,
während Rift-Ops primär das jeweilige Pararift untersuchen.

```yaml
phase: core
year: 1962
place: Karibik
objective: Black Saturday - Funkspruch der B-59 unterdrücken (kein Torpedoabschuss)
```

Rift-Seeds nutzen `phase: rift`.

`phase` markiert die Missionsphase: `core` für den Einsatz vor Ort,
`transfer` für An- und Abreise sowie `rift` für Paradoxon-Sprünge.

Die Paradoxon-Mechanik ist standardmäßig aktiv. Über `modus paradoxon off` lässt
sich das Feature jedoch jederzeit deaktivieren und mit `modus paradoxon on`
wieder einschalten. Siehe auch
[Charaktererschaffung](../characters/charaktererschaffung-grundlagen.md) und
[Zeitriss-Core](zeitriss-core.md) für weitere Hinweise.

## Technical Reference {#technical-reference}

> Dieser Abschnitt enthält Runtime-Interna, die **nur für die SL/KI-Spielleitung**
> relevant sind. Spieler brauchen diese Details nicht.

### Runtime Helper — Kurzreferenz

- **DelayConflict(threshold=4, allow=[])** — Verzögert Konfliktszenen bis zur Szene
  `threshold`. Missions-Tags `heist`/`street` senken den Schwellenwert je um eins
  (Minimum: Szene 2). `allow` bleibt standardmäßig leer.
- **comms_check(device, range_m, …)** — Pflicht vor `radio_tx/rx`:
  akzeptiert `device` (`comlink|cable|relay|jammer_override`) und eine
  Reichweite in Metern. `must_comms()` normalisiert die Eingaben.
- **scene_overlay(total?, pressure?, env?)** — erzeugt das HUD-Banner `EP·MS·SC`
  mit Missionsziel, Px/SYS/Lvl, Exfil-Daten und `FS count/required`.
- **assert_foreshadow(count=2)** — (nur PRECISION) warnt, wenn vor Boss
  weniger als `count` Hinweise gesetzt wurden.
- **ForeshadowHint(text, tag='Foreshadow')** — legt einen Foreshadow-Hinweis an
  und erhöht den Gate-Zähler.
- **arenaStart(options)** — Schaltet den Kampagnenmodus auf PvP, zieht die
  Arena-Gebühr, setzt `phase_strike_tax = 1`, aktiviert SaveGuards.

### Runtime-State (Schema)

```text
location: "HQ" | "FIELD" | "ARENA"
campaign: { episode, mission_in_episode, scene, px:0..5,
  fr_bias:"normal"|"easy"|"hard" }
phase: "core"|"transfer"|"rift"|"pvp"
character: { name, level, stress, psi_heat, cooldowns:{},
  attributes:{STR,GES,INT,CHA,TEMP,SYS_max,SYS_installed,SYS_runtime,SYS_used},
  talents:[], ... }
team: { name, members:[...] }, party: { characters:[...] }
loadout: { primary, secondary, cqb, armor:[], tools:[], support:[] }
economy: { cu, wallets:{} }
logs: { artifact_log:[], market:[], offline:[], kodex:[],
  alias_trace:[], squad_radio:[], hud:[], foreshadow:[],
  fr_interventions:[], arena_psi:[], psi:[], flags:{} }
arc_dashboard: { offene_seeds:[], fraktionen:{}, fragen:[], timeline:[] }
ui: { gm_style, intro_seen, suggest_mode, contrast, badge_density,
  output_pace, voice_profile }
arena: { active, phase, mode, previous_mode, wins_player,
  wins_opponent, tier, proc_budget, artifact_limit,
  loadout_budget, phase_strike_tax, team_size, fee,
  scenario, started_episode, last_reward_episode,
  policy_players:[], audit:[] }
exfil: { sweeps, stress, ttl_min, ttl_sec, active, armed, anchor, alt_anchor }
fr_intervention: "ruhig"|"beobachter"|"aktiv"
comms: { jammed:boolean, relays:number, rangeMod:number }
```

### Px-Policy (Runtime)

`campaign.px` bleibt die einzige Quelle für Paradoxon-Stand und Progression.
Rifts führen kein separates `rift_px`; Importpfade verwerfen abweichende Felder.
Px 0–4 erzeugt keine Maluswerte, Px 5 triggert `ClusterCreate()` und setzt
nach der Rift-Op auf 0 zurück.

## Generator-Utilities

Neuer Eintrag? Prüfe kurz, ob der Text bereits in einer anderen Liste steht.
`objective` und `twist` sollten sich nicht doppeln. Falls du denselben Satz in
beiden Feldern findest, wähle eine Variante oder streiche ihn.
