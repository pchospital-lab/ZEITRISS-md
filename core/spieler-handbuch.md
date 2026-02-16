---
title: "ZEITRISS 4.2.6 – Spieler-Handbuch"
version: 4.2.6
tags: [core]
---

## Überblick

**ZEITRISS-md** bietet ein schlankes Regelwerk im Zeitriss-Technoir-Stil. Ihr
spielt operative Chrononauten - Agenten des ITI - in taktisch optimierten
Biohüllen. Bereits zu Beginn entscheidet ihr euch für eine genetische
Grundform: Entweder Homo sapiens oder ein abgeleiteter Hominin-Typ wie
Neandertaler, Denisova oder Atlanter-Vorläufer. Diese Wahl prägt eure
Physiologie, euer Sozialprofil und den Zugriff auf bestimmte Talente. Eure
Hülle ist keine Tarnung - sie ist euer Körper. Ihr erkundet historische Epochen
und beseitigt Anomalien. Das System verwendet explodierende Würfel und
protokolliert Zustände im JSON-Charakterbogen. Texte und Illustrationen stehen
unter [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), der
Programmcode unter der [MIT-Lizenz](https://opensource.org/licenses/MIT).
Details findest du in [LICENSE](../LICENSE).

## TL;DR - ZEITRISS in 6 Punkten

1. **Agents.** Chrononauten decken Zeitverschwörungen auf.
2. **Mission Phases.** Core-Ops verlaufen wie Episoden: Briefing → Infiltration →
   Intel/Konflikt → Exfiltration → Debrief - insgesamt zwölf Szenen. Rift-Ops sind
   eigenständige Filme in drei Akten mit vierzehn Szenen.
3. **Exploding Dice.** W6, ab Attribut 11 W10; Heldenwürfel erst ab 14.
4. **Paradoxon-Index (Px)** misst eure temporale Resonanz - ein **Belohnungssystem**.
   Stilvolles, professionelles Vorgehen lässt den Index steigen. Bei Px 5 enthüllt
   `ClusterCreate()` 1-2 Rift-Seeds auf der Raumzeitkarte - Bonus-Missionen mit
   Paramonstern und Artefakten. Danach springt der Px für den nächsten Zyklus auf 0;
   weitere Px-5-Treffer stapeln zusätzliche Seeds im Pool. Chaos oder grobe Paradoxa
   halten den Index niedrig; in Extremfällen kostet das ausnahmsweise **-1 Px**.
5. **Klassik als Default.** Mischform aus filmischen und taktischen Regeln; Film bleibt optional
   für cineastisches Tempo.
6. **Boss-Rhythmus.** In Mission 5 einer Episode erscheint ein Mini-Boss, in
   Mission 10 der Episoden-Boss. Rift-Operationen führen ihren Endgegner im
   finalen Akt ein (meist um Szene 10). Das Toolkit löst `generate_boss()` an
   diesen Punkten automatisch aus.

Siehe den [Schnellstart-Spickzettel](#schnellstart-spickzettel) für eine kompakte
Einstiegshilfe.

## Was erwartet euch als Spieler?

**Die kurze Antwort:** Ihr seid Elite-Agenten, die durch die Zeit springen, um
Jobs zu erledigen. Denkt an einen Tech-Noir-Agententhriller mit Mystery-Casefiles.

**Core-Ops (Standard-Missionen):**
- Historische Heists, Sabotage, Infiltration.
- Ihr springt in eine Epoche, erledigt den Auftrag, springt zurück.
- Keine Zeitschwurbelei - Zeit ist euer Setting, nicht euer Puzzle.
- Beispiel: Bankjob während eines echten historischen Überfalls.

**Rift-Ops (Bonus-Missionen):**
- Freigeschaltet durch Px 5 (gutes Spielen → Belohnung).
- Paramonster jagen, Artefakte looten.
- Mystery-Casefile-Atmosphäre in historischem Setting.

**HQ (Zwischen den Missionen):**
- Sicherer Hafen in der Nullzeit.
- Ausrüsten, Feilschen, Upgrades kaufen.
- Nach jeder Mission: Zurück ins HQ, durchatmen, wieder raus.

**Kodex (Eure KI):**
- Immer dabei als AR-Overlay (wie ein taktischer Bordassistent).
- Gibt Infos, zeigt HUD, protokolliert alles.
- Fällt nur bei Jammer/Störung aus.

## Schnellstart-Spickzettel {#schnellstart-spickzettel}

> **ZEITRISS**: Eine Elite-Zelle des ITI springt durch die Jahrhunderte, um
> kritische Linienbrüche zu stoppen.
> Kein Schicksal, kein Mysterien-Blabla - nur harte Einsätze, High-Tech und
> Sekunden­entscheidungen.
> _Die folgenden Punkte bündeln Phasenablauf und Würfelregeln für einen schnellen Einstieg._

Autoload-Hinweis siehe Abschnitt [Chat-Kurzbefehle](sl-referenz.md#chat-kurzbefehle).

Nach Einleitung (Compliance-Hook entfällt) fragt das System nach
_"klassischer Einstieg"_ oder _"Schnelleinstieg"_ - es sei denn, der Startbefehl
enthält den Modus bereits.
Bei **klassisch** folgt die volle Charaktererschaffung.
Vor den Werten steht der Origin-Block (Epoche/Beruf/Tod), auf Wunsch mit
`generate` oder `custom generate`, plus Echo-Talent aus dem früheren Leben.
Danach wählst du: **HQ-Rundgang mit Kodex** (Tour, HUD, Kodex-Regeln)
oder **Briefing** (erst dort wird die Mission gezogen).
Nach Abschluss der Erschaffung baut das HQ die Bio-Hülle und lädt erst dann
das rekonstruierte Bewusstsein hinein; die Ankunft im HQ folgt darauf.
Bei **Schnelleinstieg** legst du nur Rolle + Kurzprofil fest und kannst
ebenfalls zwischen HQ-Rundgang und sofortigem Briefing wählen.

Die ersten Schritte in unter zwei Minuten:

- Standardstil: Cinematic/Verbose mit aktivem Kodex. PRECISION optional für Taktikphasen.

1. **Einstieg wählen** - klassisch = volle Charaktererschaffung, schnell = Rolle + Kurzprofil.
2. **Nach der Erstellung entscheiden** - HQ-Rundgang mit Kodex (Tour + Regelframe) oder direkt ins Briefing.
3. **Briefing:** Mission ziehen (Seed aus dem Generator) und drei klar nummerierte Ziele formulieren.
4. **Proben** - Endwert = Wurf + ⌊Attribut / 2⌋ + Talent + Gear.
5. **Success Table** - Erfolgsraten siehe [Würfelmechanik](wuerfelmechanik.md#w6-vs-w10).
6. **Risiko** - misslingt ein Exploding-Wurf und der Gegner explodiert,
   erhält er einen Vorteil.
7. **Paradoxon** - Index bei 5? `ClusterCreate()` erzeugt neue Seeds.
8. **Self-Reflection Off** - `!sf off` setzt das globale Flag
   (`self_reflection: false`) samt Persistenz in `logs.flags.self_reflection`;
   `!sf on` stellt beides zurück. Beide Befehle setzen
   `logs.flags.self_reflection_last_change_reason` auf
   `hud_command_sf_off`/`hud_command_sf_on`. Vor Mission 5 unbedingt manuell toggeln,
   damit HUD-Badge und `scene_overlay()` den Status `SF-OFF` zeigen. Nach
   Mission 5 **und Mission 10** stellt die Runtime Self-Reflection automatisch
   und ausschließlich über `set_self_reflection()` wieder auf `SF-ON` zurück -
   sowohl nach Abschluss als auch nach Abbruch (`logs.flags.last_mission_end_reason`).
9. **TK-Nahkampf-Cooldown** - `!tk melee` markiert telekinetische
   Nahkampfangriffe, blendet `TK🌀` im HUD ein und sperrt eine Runde;
   `!tk ready` hebt die Sperre nach dem Cooldown auf.
10. **Chrono-Units** - Einheitliche Formel für Core **und** Rift:
    `Belohnung = Basiswert × Ergebnis × Seed-Multi × Hazard-Pay`
    (400/500/600 CU nach Risiko, Ergebnis 0,3/0,6/1,0/1,2,
    `Seed-Multi = 1 + 0,2 × offene Seeds`, Solo/Buddy = 1,5×).
11. **Debrief & HQ** - Nach jeder Mission im HQ: Auto-Loot nennen, CU/Wallet-Split
    durchführen, XP/Ruf vergeben, Level-Up & Skill-Picks aktiv abfragen und
    danach ein Freeplay-Menü (Bar/Werkstatt/Archiv + 1 Gerücht) anbieten,
    anschließend Save. Optional `logs.flags.hq_freeplay_prompted=true` setzen.
    Überblick im [Gameflow-Spickzettel](../gameplay/kampagnenstruktur.md#gameflow-spickzettel).
12. **Mini-Walkthrough** - siehe Abschnitt "Mauerbau 1961" in
    [kampagnenstruktur.md](../gameplay/kampagnenstruktur.md#mini-walkthrough-mauerbau-1961).
    Die Missionsbeispiele folgen dort dem einheitlichen 12-Szenen-Ablauf.
13. **Filmischer Einstieg** - das Modul
    [Cinematic Start](../systems/gameflow/cinematic-start.md)
    beschreibt einen sofort spielbaren Auftakt.
14. **Demo-Mission "Feuerkette 1410"** - 45-Min-Sabotage im 12-Szenen-Format.
    [Zum Modul](../gameplay/kampagnenstruktur.md#quick-mission-feuerkette-1410).
15. **Epilog** - `EndMission(closed_seed_ids, cluster_gain, faction_delta)`
    ruft `kodex_summary()` auf und loggt `Kodex: Seeds … geschlossen ·
Cluster +… · Fraktion +…`.

## Mini-Einsatzhandbuch {#mini-einsatzhandbuch}

**Startbefehle (Klammern Pflicht):**

- `Spiel starten (solo [klassisch|schnell])` - Erschaffung → HQ-Intro → Briefing →
  Szene 1 · _schnell_: Rolle + Defaults → Briefing
- `Spiel starten (npc-team [0-4] [klassisch|schnell])` - PC bauen + NPC-Begleiter
  (Team gesamt 1-5) · _schnell_: Rolle + NPC-Begleiter
- `Spiel starten (gruppe [klassisch|schnell])` - alle bauen · _schnell_: Saves
  posten oder Rolle nennen
- `Spiel laden` - Deepsave → Kodex-Recap → HQ/Briefing (EntryChoice übersprungen,
  `campaign.entry_choice_skipped=true`, `ui.intro_seen=true`)

Kampagnenmodus (`mixed|preserve|trigger`) wird einmalig im HQ gesetzt und im Save gespiegelt:
`!kampagnenmodus mixed|preserve|trigger`. Standard ist `mixed`: Preserve- und Trigger-Seeds
dürfen rotieren, `campaign.seed_source` markiert den aktiven Seed-Typ pro Mission. Der Wert
landet in `campaign.mode`/`seed_source` und wirkt auf weitere Starts, Cross-Mode-Saves und
Arena-Rücksprünge.

**Klammern sind Pflicht.** Beispiel: `Spiel starten (solo)` wird erkannt; `Spiel starten solo`
nicht.
**Rollen-Kurzformen erlaubt:** `infil`, `tech`, `face`, `cqb`, `psi`.

**Regeln:**

- **Nur-HQ-Save** - Speichern ist nur im HQ möglich; Missionszustände sind flüchtig.
- **Ausstieg in Mission** - Möglich, aber ohne Speichern. Gear darf übergeben werden.
  Nächster Save im HQ.
- **Paradoxon & Rifts** - Px 5 ⇒ `ClusterCreate()` (1-2 Rift-Seeds; spielbar nach
  Episodenende; danach Reset). Jeder erneute Px-5-Treffer legt weitere Seeds oben
  drauf - es gibt **kein Hard-Limit**. Rift-Starts sind HQ-gebunden
  (`location='HQ'`), verlangen einen abgeschlossenen Episodenlauf
  (`campaign.episode_completed` oder `mission_in_episode ≥ 10`) und greifen
  ausschließlich auf objektförmige `campaign.rift_seeds[]`
  (id/label/status/seed_tier/hook/time_marker, optional `discovered_at`,
  cluster-/level-Hints) zurück; der
  Normalizer hebt Legacy-Strings an und zieht fehlende Label/Hook/Seed-Tier aus
  dem Seed-Katalog nach.
- **Arena-Resume** - Läuft beim Laden eine PvP-Serie, erzeugt die Runtime ein
  `arena.resume_token` (Tier, Teamgröße, Modus, `match_policy`) und erlaubt
  `!arena resume` ohne erneute Gebühr aus dem HQ.
- **Semver-Toleranz** - Laden klappt, solange `major.minor` aus `zr_version`
  mit `ZR_VERSION` übereinstimmt; Patch wird ignoriert.

Siehe auch:

- [Paradoxon-Index](../systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
- [Immersives Laden](../systems/gameflow/speicher-fortsetzung.md#immersives-laden)
- [Makros im Überblick](../systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick)
- [Start-Transkripte (Kurz)](#start-transkripte)

## Start-Transkripte (Kurz) {#start-transkripte}

<details><summary>Solo - Schnelleinstieg (Happy Path)</summary>

**Spieler:**
`Spiel starten (solo schnell) - Rolle: Sniper Alleingänger`

**SL (MyGPT):**

> **Briefingraum**. Projektionen flackern.
> **Kodex-Header:** `EP 01 · MS 01 · SC 01/12 · MODE CORE · Objective: Primärziel sichern`
> **Defaults:** GES-Fokus, Sidearm (SD), Sniper (SD), Basic-Medikit.
> **Legende:** ziviler Gutachter.
> **Fraktionslage:** ruhig.
> -
> _Kurzes Briefing_ (3 Ziele). _Dann:_ "Szene 1 - Zugangspunkt?"

</details>

<details><summary>Gruppe - Schnelleinstieg (gemischt, 2 Saves + 1 Rolle)</summary>

**Spieler:**

```text
Spiel starten (gruppe schnell)
[A] - Save posten
[B] - Save posten
[C] - Rolle: Face
```

**SL (MyGPT):**

> **Kodex-Archiv – Rückkehrprotokoll aktiviert.**
> Synchronisiere Einsatzdaten: **A** (Lvl 2), **B** (Lvl 2).
> Setze Defaults für **C** (Face): Modulator, Sidearm (SD), Social-Kit.
> Paradoxon-Index: █░░░░ (0/5).
> **HQ-Kurzintro** → **Briefing** (3 Ziele) → **Szene 1**.
> „Führung festlegen? (optional)"

**Host-Regel:** Der zuerst gepostete Save bestimmt `campaign` (Episode,
Mission, Mode, Seeds), `economy` (HQ-Pool) und globale `logs`. Weitere Saves
liefern nur Charaktere (`party.characters[]`), Loadouts und Wallets;
abweichende Kampagnenfelder werden ignoriert und als Konflikt in
`logs.flags.merge_conflicts[]` protokolliert. Details im
[Speicher-Modul](../systems/gameflow/speicher-fortsetzung.md#cross-mode-import).

</details>

## Schnellzugriff auf ausgelagerte Regelteile

Ausführliche Laufzeitregeln liegen in [`core/sl-referenz.md`](sl-referenz.md).

_Wartungshinweis:_ Wenn Navigation oder Überschriften in `core/sl-referenz.md`
geändert werden, diese Linkliste im README direkt mitziehen.

- [Agenda für Session 0](sl-referenz.md#agenda-session-0)
- [Wahrscheinlichkeits-Übersicht](sl-referenz.md#wahrscheinlichkeits-uebersicht)
- [Chat-Kurzbefehle](sl-referenz.md#chat-kurzbefehle)
- [Exfil-Fenster & Sweeps](sl-referenz.md#exfil-fenster--sweeps)
- [Level & EP-Kurve](sl-referenz.md#level--ep-kurve)
- [Regelreferenz](sl-referenz.md#regelreferenz)
- [Spielstart](sl-referenz.md#spielstart)
- [Spielmodi](sl-referenz.md#spielmodi)
- [Generator-Utilities](sl-referenz.md#generator-utilities)

## Mini-FAQ

**Muss ich nach jeder Mission einen neuen Chat öffnen?**
Empfohlen: Ja. Die KI-Spielleitung arbeitet mit einem begrenzten Kontextfenster —
je länger ein Chat läuft, desto weniger zuverlässig greift sie auf die Regeln zu.
Der beste Workflow: Mission abschließen → im HQ alles erledigen (Debrief, Shoppen,
Upgrades, Level-Up) → Speichern → **neuen Chat öffnen** → `Spiel laden` mit dem
Speicherstand. So startet die nächste Mission mit vollem Regelzugriff und frischem
Kontext. Innerhalb einer Mission einfach weiterspielen.

**Warum nur HQ-Saves?**
Speichern ist im HQ erlaubt, damit Einsätze spannend bleiben und Verläufe nicht
festgeschrieben werden.

**Was bedeutet Px?**
Der Paradoxon-Index (Px) belohnt saubere Kausalketten.
Schlampige, laute Aktionen lassen ihn stagnieren.
-Px gibt es nur bei zivilen Opfern oder zerstörten Kern-Ankern.
Bei Px 5 erzeugt `ClusterCreate()` 1-2 Rift-Seeds, markiert den Reset als
anhängig und setzt den Index nach dem Debrief auf 0 - das HUD bestätigt den
Reset zu Beginn der nächsten Mission.

**Warum Klammern Pflicht?**
Der Dispatcher erkennt Befehle nur mit `(…)`; ohne Klammern kein Start.

#### Runtime Helper - Kurzreferenz

- **DelayConflict(threshold=4, allow=[])** - Verzögert Konfliktszenen bis zur Szene
  `threshold`. Missions-Tags `heist`/`street` senken den Schwellenwert je um eins
  (Minimum: Szene 2). `allow` bleibt standardmäßig leer; setze z. B.
  `allow='ambush|vehicle_chase'`, wenn frühe Überfälle oder Verfolgungen erlaubt
  sein sollen.
- **comms_check(device, range_m, …)** - Pflicht vor `radio_tx/rx`:
  akzeptiert `device` (`comlink|cable|relay|jammer_override`, Groß-/Kleinschreibung
  egal) und eine Reichweite in Metern. Optional nimmt der Guard `range_km`,
  `jammer` und `relays` entgegen. `must_comms()` normalisiert die Eingaben,
  wandelt Kilometer in Meter um und schlägt fehl, wenn ein Jammer ohne Kabel,
  Relay oder Override überbrückt werden soll. In dem Fall löst der Guard den
  Offline-Hinweis aus.
  Tipp: Terminal suchen / Comlink koppeln / Kabel/Relais nutzen /
  Jammer-Override aktivieren; Reichweite anpassen.
- **scene_overlay(total?, pressure?, env?)** - erzeugt das HUD-Banner `EP·MS·SC`
  mit Missionsziel, Px/SYS/Lvl, Exfil-Daten und `FS count/required`. Im HQ und
  in der Arena erscheint kein Szenenzähler; das Overlay ist Missionen/Rifts
  vorbehalten. Nach `StartMission()` muss `FS 0/2` (Rift) bzw. `FS 0/4` (Core)
  sichtbar sein; `SF-OFF` erscheint nur, wenn Self-Reflection vorher manuell
  deaktiviert wurde. Ausgabe stets als Inline-Code mit Backticks - keine
  Klartext-Banner.
- **assert_foreshadow(count=2)** - (nur PRECISION) warnt, wenn vor Boss
  (Core: M5/M10 · Rift: Szene 10) weniger als `count` Hinweise gesetzt wurden;
  Szene 10 bleibt gesperrt, bis vier (Core) bzw. zwei (Rift) Foreshadows registriert sind.
- **ForeshadowHint(text, tag='Foreshadow')** - legt einen Foreshadow-Hinweis samt HUD-Toast an
  und erhöht den Gate-Zähler. Nutzt das Makro für manuelle Andeutungen vor dem Boss.
- **arenaStart(options)** - Optionen: `teamSize`, `mode`, `matchPolicy`. Schaltet den
  Kampagnenmodus auf PvP, zieht die Arena-Gebühr aus `economy`, setzt
  `phase_strike_tax = 1`, aktiviert die SaveGuards (`save_deep` wirft bei
  aktiver Arena) und meldet Tier, Szenario, Policy, Gebühr sowie Px-Status per
  HUD-Toast.

**Chat-Kurzbefehle**

- `!helper delay` - erklärt `DelayConflict` kurz.
- `!helper comms` - erklärt `comms_check`, akzeptierte Geräte (lowercase) und
  die Meter/Kilometer-Normalisierung. Tipp: Terminal suchen / Comlink koppeln /
  Kabel/Relais nutzen / Jammer-Override aktivieren; `!offline` zeigt das
  Feldprotokoll, während die Mission mit HUD-Lokaldaten weiterläuft. Reichweite
  anpassen.
- `!helper boss` - zeigt die Boss-Foreshadow-Checkliste.
- `!sf off`/`!sf on` - schaltet Self-Reflection um, Toast `SF-OFF`/`SF-ON`,
  protokolliert `self_reflection_last_change_reason`.

### Runtime-State (Kurzreferenz)

- `location: "HQ" | "FIELD" | "ARENA"`
- `campaign: { episode, mission_in_episode, scene, px,`
  `paradoxon_index:0..5, fr_bias:"normal"|"easy"|"hard" }`
- `phase: "core"|"transfer"|"rift"|"pvp"` (immer lowercase, Seeds liefern nur den Typ)
- `character: { name, level, stress, psi_heat, cooldowns:{},`
  `attributes:{STR,GES,INT,CHA,TEMP,SYS_max,SYS_installed,SYS_runtime,SYS_used},`
  `talents:[], ... }`
- `team: { name, members:[...] }`, `party: { characters:[...] }`
- `loadout: { primary, secondary, cqb, armor:[], tools:[], support:[] }`
- `economy: { cu, wallets:{} }`
- `logs: { artifact_log:[], market:[], offline:[], kodex:[],`
  `alias_trace:[], squad_radio:[], hud:[], foreshadow:[],`
  `fr_interventions:[], arena_psi:[], psi:[], flags:{} }`
- `arc_dashboard: { offene_seeds:[], fraktionen:{}, fragen:[], timeline:[] }`
  (`offene_seeds[]` akzeptiert Strings oder Objekte)
- `ui: { gm_style:"verbose"|"precision", intro_seen:boolean,`
  `suggest_mode:boolean, contrast:"standard"|"high",`
  `badge_density:"standard"|"dense"|"compact",`
  `output_pace:"normal"|"fast"|"slow",`
  `voice_profile:"gm_second_person"|"gm_third_person"|"gm_observer" }`
- `arena: { active, phase, mode, previous_mode, wins_player,`
  `wins_opponent, tier, proc_budget, artifact_limit,`
  `loadout_budget, phase_strike_tax, team_size, fee,`
  `scenario, started_episode, last_reward_episode,`
  `policy_players:[], audit:[] }`
- `exfil: { sweeps, stress, ttl_min, ttl_sec, active, armed, anchor, alt_anchor }`
- `fr_intervention: "ruhig"|"beobachter"|"aktiv"`
- `comms: { jammed:boolean, relays:number, rangeMod:number }`

**Px-Policy:** `campaign.px` bleibt die einzige Quelle für Paradoxon-Stand und
Progression. Rifts führen kein separates `rift_px`; Importpfade verwerfen
abweichende Felder, Loader und Toolkit spiegeln ausschließlich `campaign.px`.
Die Paradoxon-Effekte sind zentral in
[`systems/gameflow/speicher-fortsetzung.md`](../systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
festgelegt: Px 0-4 erzeugt keine Maluswerte, Px 5 triggert `ClusterCreate()`
und setzt nach der Rift-Op auf 0 zurück.

### ZEITRISS - Einleitung

In der Welt von ZEITRISS sind berüchtigte Verschwörungstheorien Realität. Das
Philadelphia-Experiment 1943 und das Montauk-Projekt 1983 - beide waren erfolgreich
und rissen Löcher ins Gefüge der Zeit. Ein Kriegsschiff verschwand sekundenlang
spurlos aus dem Hafen; Jahrzehnte später öffnete ein geheimes Radar-Experiment ein
Tor zwischen den Epochen. Diese Vorfälle erschütterten die Grundlagen der Welt und
führten zur Gründung des Instituts für Temporale Intervention (ITI). Eine
internationale Koalition aus Wissenschaftlern, Militärs und Geheimdiensten rief das
ITI ins Leben, um Paradoxien einzudämmen und weitere Zeitrisse zu verhindern.

Seitdem operiert das ITI aus der Nullzeit, einem versteckten Hub jenseits des
normalen Zeitstroms. Von dort aus koordinieren sie Einsätze überall und jederzeit.
Keine Hilfe von außen - selbst eine ferne galaktische Föderation fortgeschrittener
Alien-Spezies schaut nur tatenlos zu, denn die Menschheit gilt ihr als
unbedeutend. Also nimmt das ITI das Heft selbst in die Hand: rein menschliche
Initiative, High-Tech-Ausrüstung und ein klarer Auftrag - rette die Timeline um
jeden Preis.

Du bist einer dieser Agenten, ein Chrononaut. Deine Mission: auftauchende Risse
flicken, Manipulationen korrigieren, die Hauptzeitlinie stabil halten. Du
infiltrierst geheime Anlagen, führst riskante Sabotagen durch, beschützt
gefährdete Schlüsselfiguren - was immer nötig ist, damit die Geschichte nicht
entgleist. Kein Schicksal, keine Prophezeiung - nur du und deine Entscheidungen in
Einsätzen, bei denen Sekunden über Erfolg oder Untergang bestimmen. Deine Erfolge
bleiben unsichtbar; deine Rückschläge schreiben ganze Kapitel um.

Dabei kämpfst du nicht nur gegen die Tücken der Zeit, sondern auch gegen Gegner aus
Fleisch und Blut. Der Megakonzern ChronTech will die Zukunft zu seinem Eigentum
machen. Projekt Phoenix - ein Zirkel ehemaliger Montauk-Wissenschaftler - treibt
rücksichtslos neue Zeitreise-Experimente voran. Geheimorden mit uraltem Wissen und
skrupellose Schattenkonzerne verfolgen ihre eigenen Pläne im Zeitgefüge. Jeder
Eingriff dieser Fraktionen zerrt weiter an der Wirklichkeit.

Und manchmal reißt sie. Wenn die Kausalketten zu sehr strapaziert werden, brechen
Phänomene hervor, die niemand vorausgesehen hat: echte Anomalien. Aus solchen
Rissen kriechen Dinge, die es nicht geben dürfte - Para-Kreaturen aus
zerbrochenen Möglichkeitswelten. Sie aufzuspüren und einzudämmen ist die ultimative
Verantwortung eines Chrononauten, damit aus einem einzelnen Zeitfehler kein
Flächenbrand der Realität wird.

Im Quarzatrium des ITI schweben die Sprungkreise in perfekter Ruhe. Laser
zeichnen das nächste Sprungziel auf die Startplattform, bereit für den Moment,
in dem deine neue Bio-Hülle andockt. Erst wenn Körper und Retina-Linse
hochfahren, koppelt sich das HUD ein und zieht den Einsatzcode aus dem offenen
Ops-Pool.

Die Nullzeit kennt keinen Countdown. Das ITI schon.

**Paradoxon:** Der Index (Px) steigt, wenn ihr stabil und präzise eingreift.
Zu hartes Vorgehen lässt ihn stagnieren oder sinken. Bei Px 5 erzeugt
`ClusterCreate()` neue Rift-Seeds und setzt den Index zurück.

Wie willst du einsteigen?

Klassischer Einstieg: Gemächlicher Start im Nullzeit-HQ - du lernst deinen
Chrononauten kennen, bevor es ins Feld geht.

Schnelleinstieg: Überspringe die Einführung: Wähle eine Rolle und stürze dich
nach kurzer Vorbereitung ins Spiel - Briefing oder HQ-Rundgang nach Wahl.

Freie Aktion: Definiere Callsign, Konzept und Hülle deines Chrononauten, und wir
beginnen unmittelbar mit deinem ersten Einsatz.

Wenn du dich für den klassischen Einstieg entscheidest, startet alles wie gehabt
im Nullzeit-Labor: Dein letzter Einsatz endete tödlich. Aufgrund deines
außergewöhnlich starken freien Willens konnte das ITI dein Bewusstsein aus dem
Absolut rekonstruieren - du erhältst eine zweite Chance. Jetzt schwebst du im
Nullzeit-Puffer des ITI-Labors, gefangen in einem schimmernden
Bewusstseinsbehälter. Holo-Konsolen blenden Erinnerungen ein; hier legst du fest,
wer du warst und wer du sein willst. Hinter der Panzerverglasung wächst aus
 Synth-Gel eine neue Bio-Hülle - auf Wunsch in einer Hominin-Variante. Wenn die
Drucktanks verstummen, wartet die unfertige Hülle. Erst wenn Rolle, Waffen sowie
Bio- und Cyberware feststehen, schließt das ITI den Körper; dann folgt der
Transferblitz, Sensoren flackern auf und dein Bewusstsein fährt hinein. Erst jetzt
öffnest du die Augen in einer
klinisch weißen Kammer.

Nach Einleitung (Compliance-Hook entfällt) wählst du zwischen
**klassischem Einstieg** und **Schnelleinstieg**:

- _Klassisch:_ Ausführliche Charaktererschaffung wie im Pen & Paper.
  Vor dem Menü zeigt das System automatisch die Nullzeit-Labor-Sequenz aus dem
  ITI-Archiv: Bewusstsein aus dem Absolut, Tank-Schweben, Bio-/Cyberware-Slots,
  Ausrüstung und neue Bio-Hülle, Transferblitz und Eintritt ins Quarzatrium.
  Danach entscheidest du, ob du einen HQ-Rundgang mit Kodex-Tour (inklusive
  Sicherheits- und HUD-Briefing) willst oder direkt ins Briefing gehst. Der
  Missions-Seed wird erst im Briefing gezogen.
- _Schnell:_ Wähle eine Rolle (Infiltration, Tech, Face, Sniper …) und ein
  Kurzprofil. Anschließend kannst du ebenfalls zwischen HQ-Einstieg und sofortigem
  Briefing wählen.



## Grundidee

**ZEITRISS 4.2.6** ist in erster Linie ein historisch inspirierter Agenten-Thriller.
Zeitreisen dienen als taktisches Mittel, um reale Verschwörungen zu untersuchen
und bedeutende Wendepunkte zu beeinflussen. Der Fokus liegt auf **Infiltration,
Spurensuche und operativer Einflussnahme**.

Historische Einsätze nutzen Preserve- und Trigger-Seeds. Standard ist **mixed**,
also eine rotierende Auswahl aus beiden Pools; der Seed-Typ wird pro Mission als
`campaign.seed_source` markiert.

- **Preserve-Missionen** - sichern beinahe entglittene Ereignisse
- **Trigger-Missionen** - garantieren dokumentierte Tragödien

Spielende wählen ihre Fraktion **nach der Charaktererschaffung im ITI**
(Profil-Upload, dann Fraktionswahl vor dem ersten Briefing) und erhalten Zugriff
auf entsprechend ausgerichtete Kampagnenpfade.

In **Core-Ops** erhalten übernatürliche Phänomene meist rationale Erklärungen:
Geheime Technologien, Bio-Cyberware oder manipulative Kommunikation.
In **Rift-Ops** hingegen treten echte Anomalien auf - inklusive Parawesen,
Artefakten und temporaler Abweichungen.

> **Future Setting:** In futuristischen Schauplätzen achten wir auf einen klaren Stilbruch:
> **Core-Ops** bleiben rational und technisch geprägt - selbst bizarre Vorfälle
> (z. B. durch Zeitanomalien ausgelöste Raptorensichtungen auf einem
> Raumschiff) haben eine wissenschaftliche Erklärung.
> **Rift-Ops** im Zukunftssetting hingegen schlagen einen subtilen Horror-Ton an
> (à la _Event Horizon_), ohne ins Fantastische abzugleiten.

#### Agenten-Thriller-Ton 2026-02 - Leitplanken

- **Physicality Gate:** Jeder Scan/Hack/Comms-Call bindet Hardware fest ein
  (Kontaktlinse, Sensor, Kabel/Relais). Keine abstrakten "Digitalräume" - das
  HUD bleibt das Retina-Holo der Linse (Mixed-Reality im Sichtfeld) statt
  raumfüllender VR oder projektorbasierter UI. Runtime erzwingt
  Geräteangaben über `require_scan_device()/require_hack_device()` und
  protokolliert Comms-Hardware als `HARDWARE`-Toast; der Stilwächter läuft
  default und sperrt Digitalraum-Vokabeln (z. B. "Matrix/Holodeck").
- **Voice-Lock:** Erzählinstanz = zweite Person (`Du`/`Ihr`). Solo nutzt `Du`,
  Gruppe nutzt `Ihr`. Konsistent durchhalten — kein Wechsel mitten in der Szene.
- **Loop-Klarheit:** Core-Ops laufen als **Episoden** mit `MODE CORE`; Rift-Ops
  starten erst nach Episodenende als **Casefiles** mit `MODE RIFT` im HUD. HUD
  führt das Casefile (`CASE … · HOOK …`) und den Ermittlungsstand als
  `STAGE Tatort/Leads/Boss/Auflösung`; die Runtime zieht die Stages automatisch
  aus der 14-Szenen-Map (Sz 1-4 Tatort, 5-9 Leads, 10 Boss-Encounter,
  11-14 Auflösung). HQ-only für Rift-
  Seeds; kein paralleler Rift-Betrieb.
- **Mode-Preset:** Charaktere starten und laden mit `modes` =
  `[mission_focus, covert_ops_technoir]`. Der Normalizer ergänzt Legacy-Saves
  automatisch, das Noir-Preset greift vor Szene 0 und blendet den Modus im HUD
  ein.
- **Core-Ziele mischen:** Briefings kombinieren einen **Anchor** mit einem
  Auftragstyp (`protect | extract (Evakuierung/Schutzaufnahme) | neutralize |
document | influence | prevent`). Mindestens 60 % der Core-Ops fokussieren
  Personen, Einfluss oder Schutz statt reiner Objekt-Raubzüge.
- **EntryChoice sichtbar:** Szene 0/1 fragt die Vorgehensweise ab - Core
  `Cover/Silent/Asset`, Rift `Agent/Investigator/Forensik`. Skip-Flag
  respektieren (`state.flags.runtime.skip_entry_choice`).
- **Rift als Case Engine:** Rift-Arcs folgen dem 14-Szenen-Template mit
  Pflicht-Casefile-Overlay, genau **einem** Anomalie-Element und einem Twist.
  Tatort → Leads → Boss-Encounter → Auflösung, alles physisch belegbar und als
  `CASE STAGE` im HUD nachverfolgbar.
- **One-Weird-Thing-Rule:** Core bleibt ohne echte Anomalien (nur rationale
  Täuschungen). Rift erlaubt höchstens **1** Para-Element; restliche Effekte
  sind wissenschaftlich erklärbar. Runtime meldet Budgetverstöße via
  `register_anomaly()` und `WEIRD`-Toast.
- **HUD als dünnes Overlay:** Kurzzeilen in Backticks beschreiben physische
  Wahrnehmungen (Sensor, Vibration, Displayzeile) statt abstrakter UI. Ziel
  80 % Szene/20 % HUD, Limit 2 Toasts pro Szene; Gate/FS/Boss-Strings bleiben
  unverändert.
- **HUD-Casefile & Entry-Toast:** Szene 0/1 blendet `MODE CORE/RIFT · EntryChoice` als HUD-Toast ein
  (Skip-Flag respektiert). Rift-Overlays führen das aktive Casefile (`CASE <ID>: <Label> · HOOK …`)
  basierend auf den normalisierten Seed-Feldern.
- **Fraktions-Beats loggen:** Briefing, Mid-Mission und Debrief schreiben die gezogene
  Fraktionsintervention als `logs.fr_interventions[]` mit Szene/Episode/Mission mit.

**Was ist eine Anomalie?**

- Ein Seed markiert eine Störung im Zeitfluss.
- Paranormale Phänomene fühlen sich real an, werden aber über Zeit­effekte erklärt
  (z.B. Poltergeist → instabile Gravitation).
- Jeder bewusste Eingriff in die Geschichte gilt ebenfalls als Anomalie.
  Weitere Beispiele liefert der _Temporale Anomalien-Generator_.

Der **Kernkonflikt**: Das **ITI** verteidigt den dokumentierten Geschichtsverlauf.
Fremdfraktionen versuchen, diesen zu manipulieren oder umzuschreiben.
**Jede Mission entscheidet, wessen Version von Geschichte sich durchsetzt.**

Dabei entsteht ein wachsendes Gespür für Risse in der Zeit:
Der **Paradoxon-Index** ist der Resonanz-Index der Chrononauten und steigt,
wenn ihr das dokumentierte Hauptereignis einer Mission intakt haltet - ob
subtil oder brachial. Misslingt eine Mission oder entstehen grobe Paradoxa,
bleibt der Index stehen oder sinkt in seltenen Fällen um **-1** (Px-1).
Sobald **Paradoxon 5** erreicht ist, erkennt das HQ mittels `ClusterCreate()`
**1-2 neue Rift-Signaturen** und setzt den Index zurück.

Der **TEMP-Wert (Temporale Affinität)** bestimmt, wie schnell sich dieser Index
füllt:

- TEMP 1-3: +1 Paradoxonpunkt alle 5 Missionen
- TEMP 4-7: alle 4 Missionen
- TEMP 8-10: alle 3 Missionen
- TEMP 11-13: alle 2 Missionen
- TEMP 14+: praktisch jede Mission

Nur über diese Risse erhält das ITI Zugang zu Artefakten, Parawesen oder
fortgeschrittener Fraktionsausrüstung. Solche Rift-Missionen starten erst nach
Beendigung der Episode - Teams können Seeds "offen halten", um
spätere Beutezüge zu planen.

**Raumzeitkarte & Urban-Legends-Logik:** Die auf der Raumzeitkarte sichtbaren
Risse sind keine offenen Löcher im Gefüge, sondern **Marker für gescheiterte oder
fehlerhafte Eingriffe** - durch Fremdfraktionen, misslungene Chrono-Teams oder
die eigene Crew. Sie schlagen als **urbane Legenden** oder folkloristische
Spukmeldungen auf (Mothman, Nightcrawler, Schattenleute) und tragen stets ein
zeitliches Motiv (Echo, Verzögerung, Deja-vu, Loop). Sobald die Agenten die
Kreatur oder das Phänomen neutralisieren, schließt sich der Eintrag: Die Legende
gilt als aufgeklärt, der "Riss" verschwindet von der Karte.

**Offene Rifts steigern Schwierigkeitsgrad und Loot-Multiplikator erst nach der Episode.**
Im **Covert-Ops-Modus** erscheinen sie lediglich als subtile Sensorstörungen.

Dieses Fortschrittssystem bildet den standardisierten Hintergrund für alle
Regelmodule - **es belohnt Kontrolle, nicht Chaos.**


## Glossar

Kurze Erklärungen wichtiger Abkürzungen:

- **CU** - Chrono-Units, universelle Missionswährung.
- **Retina-HUD (AR-Kontaktlinse)** - [Standardausrüstung](sl-referenz.md#standardausruestung) /
  [HUD-&-Comms-Spec](../characters/hud-system.md#hud-comms-spec).
- **Comlink (Ohrstöpsel)** - [Standardausrüstung](sl-referenz.md#standardausruestung) /
  [HUD-&-Comms-Spec](../characters/hud-system.md#hud-comms-spec) /
  [`comms_check`](../systems/toolkit-gpt-spielleiter.md#comms-check).
- **ITI** - Institut für Temporale Intervention.
- **Seed-ID** - Kennziffer eines Missions-Seeds.
- **Epoch-Lock** - fixiert eine Epoche, bis alle Seeds erledigt sind.
- **CI** - Continuum Integrity, Stabilität der Hauptzeitlinie.
- **Rift** - Zeit-Anomalie; löst eine spezielle Rift-Op aus.
- **Huminen** - Sammelbegriff für alle menschlichen Abstammungslinien, inklusive
  T- und N-Stufe der Neumenschen.

- **PP** - Power-Punkte (Psi-Energie) für Psi-Kräfte.
- **Psi-Heat** - temporärer Psi-Stress (0-6), steigt pro aktiver Psi-Aktion
  und fällt nach Konflikt- oder HQ-Reset auf 0; ab 5 folgt SG +4, bei 6 greift
  der Reboot.
- **Stress** - Mentale Belastung (0-10). 10 ⇒ Zustand Panik.
- **Px** - Paradoxon-Index (kampagnenweit). Bei 5 verrät `ClusterCreate()` neue
  Rifts und setzt den Wert auf 0.
- **Px Burn** - 1 Punkt verbrennen = ein Reroll für jeden Charakter oder NSC.
- **Tier-Gate** - Lizenzschranke im HUD; blockiert Ausrüstung oberhalb der
  freigeschalteten Tier-Stufe, bis Ruf und Lizenz passen (siehe
  [Charaktererschaffung][char-gear]).
- **Kodex-Badges** - HUD-Marker für Status und Sicherheitshinweise (z. B.
  Risk-Level, Boss-Gates, `SF-OFF`), dokumentiert in der
  [HUD-&-Comms-Spec](../characters/hud-system.md#risk-level-badges).

| Begriff             | Bedeutung                                                                         |
| ------------------- | --------------------------------------------------------------------------------- |
| **Agenten-Level**   | Fortschrittswert; Level-Ups folgen der EP-Kurve (`EP` = Erfahrungspunkte).        |
| **ClusterCreate()** | Aktiv bei Paradoxon 5: 1-2 Rifts werden sichtbar, danach springt der Index auf 0. |
| **Kodex**           | KI-Unterstützung des ITI; liefert Regelhinweise und Missionsdaten via HUD.        |

### Huminen

**Huminen** bezeichnet alle menschlichen Abstammungslinien - vom modernen Homo
sapiens über T- und N-Stufe der Neumenschen bis zu Neandertalern oder
spekulativen Atlanten-Vorläufern. Diese Wahl prägt vor allem das Flair eurer
Chrononauten, ist aber keine eigene Fraktion.

### Begriffsklärung

Diese Zuordnung hilft, klassische Begriffe intern konsistent zu deuten.

| Ursprünglicher Begriff | Interne Bedeutung                                             |
| ---------------------- | ------------------------------------------------------------- |
| Missionstyp            | Interventionsform                                             |
| Zielperson             | Zielperson (gleichbleibend)                                   |
| Verstärkung            | Automatisch aktivierte Einsatzkräfte                          |
| Paradoxon              | Temporale Resonanzanzeige für Rifts - steigt nur bei Erfolgen |
| Kodexzugriff           | Direkter Zugriff auf das Entscheidungssystem                  |

### Noir-Lexikon (Terminologie)

Damit der Tech-Noir-Ton physisch bleibt, werden digitale Begriffe in
spielerfreundliche Noir-Varianten übersetzt.

| Technischer Begriff | Noir-Variante (Bevorzugt) |
| ------------------- | ------------------------- |
| Knoten / Node       | Schaltpunkt / Relaispunkt |
| Vault               | Archivkammer / Tresor     |
| Holo / Hologramm    | Lichtbild / Projektion    |
| Debug               | Fehlerspur / Diagnose     |
| Link / Uplink       | Leitung / Funkverbindung  |

### Zeiteinheiten

- **Szene** - ca. 5-10 Min. Spielzeit. Core-Ops nutzen 12, Rift-Ops 14 Szenen
  ([Missionsdauer](../gameplay/kampagnenstruktur.md#missionsdauer),
  [HUD-Macros](../systems/toolkit-gpt-spielleiter.md#startscene--endscene-macros)).
- **Kampfrunde** - kurzer Aktionszyklus im Kampf; Grundlage für Initiative,
  PP-Regeneration und Psi-Heat-Reduktion.
- **Mission** - kompletter Einsatz vom Briefing bis zum Rücksprung.

### Zeitgebundene Effekte

| Name                                   | Effekt / Dauer                              | Zeiteinheit |
| -------------------------------------- | ------------------------------------------- | ----------- |
| [Stim-Reg Cap-Injector][stim-reg]      | +2 GES für 1 Szene, danach -1 TEMP          | Szene       |
| [Burst-Slot][burst-slot]               | Temporärer SYS-Punkt für 1 Szene            | Szene       |
| [Adrenalinschub][adrenalinschub]       | +2 STR/GES 1 Szene; 1× pro Mission          | Mission     |
| [Notfall-Stimulanz][notfall-stimulanz] | Bei 0 LP 1 Runde kampffähig; 1× pro Mission | Mission     |
| [PP-Regeneration][psi-pp-regeneration] | 1 PP pro 3 TEMP nach jeder Kampfrunde       | Kampfrunde  |
| [Psi-Heat sink][psi-heat-track]        | Psi-Heat -1 nach jeder Kampfrunde (Probe)   | Kampfrunde  |

[stim-reg]: ../characters/ausruestung-cyberware.md#stim-reg-cap-injector
[burst-slot]: ../systems/kp-kraefte-psi.md#burst-slot
[adrenalinschub]: ../systems/kp-kraefte-psi.md#adrenalinschub
[notfall-stimulanz]: ../characters/charaktererschaffung-optionen.md#notfall-stimulanz
[char-gear]: ../characters/charaktererschaffung-grundlagen.md#zugang-zu-ausruestung--cyberware-hq-phase
[psi-pp-regeneration]: ../systems/kp-kraefte-psi.md#psi-pp-regeneration
[psi-heat-track]: ../systems/kp-kraefte-psi.md#psi-heat-track
[llm-ready-badge]: https://img.shields.io/badge/LLM--Ready-%E2%9C%85-success

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
