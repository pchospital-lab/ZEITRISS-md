---
title: "ZEITRISS-md Zeitreise RPG"
version: 4.2.6
tags: [meta]
---

# ZEITRISS®-md Zeitreise RPG

[![LLM-Ready ✅][llm-ready-badge]][llm-ready-link]

> **Kurzfassung:** ZEITRISS® schickt euch als operative Chrononauten in ein
> Tech-Noir-Zeitreise-RPG mit KI-Spielleitung, explodierenden Würfeln und
> JSON-Charakterbögen.
> **Hinweis (18+):** Die Inhalte richten sich ausschließlich an Erwachsene.
> **Markenhinweis:** ZEITRISS® ist eine eingetragene Marke von Florian Michler.
> **DPMA-Dossier:** Der vollständige Registerauszug liegt repo-intern vor;
> haltet das Aktenzeichen 30 2025 215 671.9 bereit.

→ [Schnellstart-Spickzettel](#schnellstart-spickzettel)
→ [Paradoxon-Index](systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
→ [Immersives Laden](systems/gameflow/speicher-fortsetzung.md#immersives-laden)
→ [Makros im Überblick](systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick)

## Inhaltsverzeichnis

1. [Schnellstart-Spickzettel](#schnellstart-spickzettel)
   1. [Agenda für Session 0](#agenda-session-0)
   1. [Wahrscheinlichkeits-Übersicht](#wahrscheinlichkeits-uebersicht)
1. [Wissensspeicher & Plattform-Setup](#wissensspeicher--plattform-setup)
1. [Repo-Map](#repo-map)
   1. [Dokumenten-Landkarte](#dokumenten-landkarte)
1. [Mini-Einsatzhandbuch](#mini-einsatzhandbuch)
1. [Start-Transkripte (Kurz)](#start-transkripte)
1. [Chat-Kurzbefehle](#chat-kurzbefehle)
1. [Exfil-Fenster & Sweeps](#exfil-fenster--sweeps)
1. [Level & EP-Kurve](#level--ep-kurve)
1. [Regelreferenz](#regelreferenz)
   1. [Proben & Schwierigkeitsgrad](#proben--schwierigkeitsgrad)
   1. [Difficulty-Konverter](#difficulty-konverter)
   1. [Wichtige Makros](#wichtige-makros)
   1. [KPI-Cheat-Sheet pro Phase](#kpi-cheat-sheet-pro-phase)
   1. [Modulübersicht](#modulübersicht)
1. [Standardausrüstung](#standardausruestung)
1. [Grundidee](#grundidee)
1. [Loot-Matrix](#loot-matrix)
1. [Loot-Quickref](#loot-quickref)
1. [Kampagnenhierarchie](#kampagnenhierarchie)
1. [Struktur](#struktur)
1. [Spielstart](#spielstart)
1. [Spielmodi](#spielmodi)
1. [Generator-Utilities](#generator-utilities)
1. [Glossar](#glossar)
   1. [Huminen](#huminen)
   1. [Begriffsklärung](#begriffsklärung)
   1. [Zeiteinheiten](#zeiteinheiten)
   1. [Zeitgebundene Effekte](#zeitgebundene-effekte)
1. [Wie du beitragen kannst](#wie-du-beitragen-kannst)

<!-- Macro: ShowComplianceOnce -->

{% macro ShowComplianceOnce() -%}
{# Compliance-Hinweis neutralisiert; Hook bleibt für Legacy-Prompts bestehen. #}
{%- endmacro %}

<!-- Macro: StoreCompliance (Alias) -->

{% macro StoreCompliance() -%}
{# Alias bleibt leer; Compliance-Hinweis entfällt. #}
{%- endmacro %}

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
Details findest du in [LICENSE](LICENSE).

## Lizenz & Nutzung (Kurzfassung)

- **Privatnutzung:** Kostenlos für private Einzelspiel- oder Gruppenrunden.
  Anpassungen sind erlaubt, solange die CC BY-NC 4.0 eingehalten und
  "ZEITRISS® - pchospital" genannt wird.
- **Kommerzielle Nutzung:** Jede Nutzung in kommerziellen Produkten,
  Plattformen oder Services erfordert eine schriftliche Lizenzvereinbarung.
  Details und Anfragen laufen über die im Repository genannten
  Maintainer-Kanäle (siehe [LICENSE](LICENSE)).
- **Marke & Altersfreigabe:** ZEITRISS® ist markenrechtlich geschützt, die
  Inhalte richten sich ausschließlich an Erwachsene (18+).

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
Jobs zu erledigen. Denkt an Shadowrun meets James Bond meets X-Files.

**Core-Ops (Standard-Missionen):**
- Historische Heists, Sabotage, Infiltration.
- Ihr springt in eine Epoche, erledigt den Auftrag, springt zurück.
- Keine Zeitschwurbelei - Zeit ist euer Setting, nicht euer Puzzle.
- Beispiel: Bankjob während eines echten historischen Überfalls.

**Rift-Ops (Bonus-Missionen):**
- Freigeschaltet durch Px 5 (gutes Spielen → Belohnung).
- Paramonster jagen, Artefakte looten.
- X-Files-Atmosphäre in historischem Setting.

**HQ (Zwischen den Missionen):**
- Sicherer Hafen in der Nullzeit.
- Ausrüsten, Feilschen, Upgrades kaufen.
- Nach jeder Mission: Zurück ins HQ, durchatmen, wieder raus.

**Kodex (Eure KI):**
- Immer dabei als AR-Overlay (denkt an Jarvis).
- Gibt Infos, zeigt HUD, protokolliert alles.
- Fällt nur bei Jammer/Störung aus.

## Wissensspeicher & Plattform-Setup {#wissensspeicher--plattform-setup}

Die komplette Operator-Checkliste liegt repo-intern vor. Dort findet ihr die
Plattform-Workflows, Upload-Notizen sowie die Rollenaufteilung zwischen
Custom-GPT, Repo-Agent und Ingame-Kodex. Dieses README listet nur die
Laufzeitreferenz - bei Fragen zum Hochladen, Synchronisieren oder Testen führt
euch das Maintainer-Dokument.

### Wissensspeicher laden

1. **Dateien importieren:** Lade `README.md`, `master-index.json` (alternativ
   `master-index.md` als Markdown-Spiegel) sowie alle unten aufgeführten 18
   Runtime-Module in den Wissensspeicher deiner Zielplattform. Diese 20 Slots
   sind exklusiv für die Runtime-Dokumentation reserviert; andere Repo-Dateien
   dürfen nicht in den Wissensspeicher wandern.
2. **Masterprompt spiegeln:** Kopiere `meta/masterprompt_v6.md` (Local-Uncut
   4.2.6) als Systemprompt (MyGPT: Masterprompt-Feld, Proton LUMO: erste
   Chatnachricht, OpenWebUI: Instruktionsfeld). Der Masterprompt gehört nicht
   in den Wissensspeicher; er wird ausschließlich als Systemfeld bzw. erste
   Nachricht geladen. Die vorherige Fassung liegt archiviert in
   `meta/archive/masterprompt_v6_legacy.md`.
3. **Slot-Kontrolle:** Prüfe nach jedem Speicherstand oder Plattform-Export, ob
   alle 20 Module weiterhin geladen sind. Falls ein Modul fehlt oder veraltet
   wirkt, fordere explizit das korrekte Markdown nach und lade es erneut.
4. **Index-Hygiene:** Runtime-Index strikt halten (`README`, `master-index*`,
   18 Runtime-Module). Der Index listet ausschließlich die 20
   Wissensspeicher-Module.

### Runtime-Module im Wissensspeicher

| Kategorie      | Datei                                           |
| -------------- | ----------------------------------------------- |
| **characters** | `characters/ausruestung-cyberware.md`           |
|                | `characters/charaktererschaffung-grundlagen.md` |
|                | `characters/charaktererschaffung-optionen.md`   |
|                | `characters/zustaende.md`                       |
|                | `characters/hud-system.md`                      |
| **core**       | `core/wuerfelmechanik.md`                       |
|                | `core/zeitriss-core.md`                         |
| **gameplay**   | `gameplay/fahrzeuge-konflikte.md`               |
|                | `gameplay/kampagnenstruktur.md`                 |
|                | `gameplay/kampagnenuebersicht.md`               |
|                | `gameplay/kreative-generatoren-begegnungen.md`  |
|                | `gameplay/kreative-generatoren-missionen.md`    |
|                | `gameplay/massenkonflikte.md`                   |
| **systems**    | `systems/currency/cu-waehrungssystem.md`        |
|                | `systems/gameflow/cinematic-start.md`           |
|                | `systems/gameflow/speicher-fortsetzung.md`      |
|                | `systems/kp-kraefte-psi.md`                     |
|                | `systems/toolkit-gpt-spielleiter.md`            |

**Slot-Kennzeichnung im Index:** In `master-index.json` (identische Inhalte in
`master-index.md` für Markdown-only-Plattformen) sind alle 20 Wissensmodule
(README, master-index und die 18 Runtime-Module) mit `"slot": true` markiert.
Meta- oder Varianten-Einträge tragen `"slot": false` und zählen nicht als
eigener Wissensspeicher-Slot.

### Plattform-Setup

- Installations- und Upload-Wege liegen weiterhin in den Maintainer-Ops
  (repo-intern, tags: [meta]). Laufzeitrelevante Presets sind hier gespiegelt,
  damit lokale Runs ohne Nachschlagen starten können.
- **LM-Studio-Sampling (gpt-oss-20b):**
  - **ZEITRISS-PLAY (Standard/uncut):** Temperatur 0,60; Top-p 0,92; Top-k 60;
    Penalty Alpha 0,05; Präsenz-Penalty 1,06.
  - **Noir/Interlude (ruhiger):** Temperatur 0,70; Top-p 0,94; Top-k 80;
    Penalty Alpha 0,07; Präsenz-Penalty 1,05.
  - Einsatz: Missionen → ZEITRISS-PLAY, HQ/ruhige Interludes → Noir/Interlude.
  - Antwortfenster 1 100-1 600 Tokens halten; in LM Studio "Limit Response
    Length" aktivieren.
- **Kontextprofile & Hardware:** 16 k/24 k/32 k Profile; GPU-Default mit
  Offload + Flash Attention, Batching 128-512. CPU-Profile nutzen denselben
  Kontext, Thread-Pool auf reale Kerne setzen. Empfehlung: 24 k als Standard,
  32 k für lange HQ-Zyklen; 131 k nur bei explizitem Bedarf.
- **RAG-Trim:** Big-RAG Limit 4, Affinity 0,74, Chunk 650, Overlap 96; der
  Runtime-Index enthält nur README, `master-index*` und die 18 Runtime-Module.
- **Template-Guard:** `{%`/`{{` aus Wissenssnippets ignorieren und niemals
  ausgeben, damit lokale Modelle nicht in Template-Modi kippen.

### Runtimes & Tests außerhalb des Wissensspeichers

- `internal/runtime/runtime-stub-routing-layer.md`, `runtime.js`, Hilfsskripte und
  Test-Tools bleiben lokal im Repo und werden **nicht** in produktive
  Wissensspeicher hochgeladen.
- Spiegle relevante Laufzeitlogik (z. B. Foreshadow-Persistenz, HUD-Badges) als
  Regelwerk, Prozessbeschreibung oder Pseudocode innerhalb der Wissensbasis
  (README, `kb/`-Äquivalente, Runtime-Module), damit produktive GPTs ohne
  externe Skripte denselben Funktionsumfang erhalten.
- Nutze die lokalen Runtimes weiterhin für Entwicklung und Tests. Spiegel
  Anpassungen an Runtime-Logik zeitnah in den Wissensmodulen, damit der
  produktive Wissensspeicher konsistent bleibt.

## Repo-Map {#repo-map}

```
ZEITRISS-md/
├─ README.md                # Laufzeit-Referenz & Plattform-Hinweise
├─ core/                    # Grundregeln & Zeitriss-Mechaniken (Runtime)
├─ characters/              # Charaktererschaffung, Ausrüstung, Zustände (Runtime)
├─ gameplay/                # Kampagnenstruktur, Generatoren, Missionsbau (Runtime)
├─ systems/                 # Gameflow, Währungen, Toolkit für die KI-Spielleitung (Runtime)
├─ internal/qa/             # Interne Pläne/Logs (Meta-Artefakte)
├─ internal/runtime/        # Entwickler-Stubs (`runtime-stub-routing-layer.md`) & lokale Runtimes
├─ meta/                    # Masterprompts, Hintergrundbriefe, Dev-only Inhalte
├─ docs/                    # Maintainer-Ops, Lizenznotizen, Hosting-Strategie
│                           # (tags: [meta]; inkl. Fahrplan & Protokoll)
├─ scripts/, tools/         # Hilfsprogramme & Linter (Dev-only)
├─ master-index.json        # Übersicht aller Module und Slugs
└─ master-index.md          # Markdown-Spiegel des Modul-Index für LM Studio & Co.
```

### Dokumenten-Landkarte {#dokumenten-landkarte}

- **README (Wissenspaket)** - Einstieg für alle Rollen, Runtime-Referenzen,
  Kurzbefehle und Plattform-Setup.
- **Beitrags- & Agentenrichtlinien (repo-intern)** - Arbeitsgrundlage für
  Beitragende und Repo-Agenten, inkl. Prüfpfade, Compliance und QA-Hinweise.
- **Maintainer-Handbuch (repo-intern)** - Upload-Workflows, Plattformpflege und
  Runtime-Spiegelungen.
- **Impressum (repo-intern)** - Rechtliche Pflichtangaben und Kontakt für
  Lizenzanfragen.
- **Hintergrund- & Strategie-Notizen (repo-intern)** - Lizenz-,
  Hosting- und Entwicklungsnotizen, nicht für den Wissensspeicher gedacht.
- **Masterprompts (repo-intern)** - Laufzeit-Briefings für MyGPT; enthalten
  keine Dev-Vorgaben wie Agentenregeln.

## Schnellstart-Spickzettel {#schnellstart-spickzettel}

> **ZEITRISS**: Eine Elite-Zelle des ITI springt durch die Jahrhunderte, um
> kritische Linienbrüche zu stoppen.
> Kein Schicksal, kein Mysterien-Blabla - nur harte Einsätze, High-Tech und
> Sekunden­entscheidungen.
> _Die folgenden Punkte bündeln Phasenablauf und Würfelregeln für einen schnellen Einstieg._

Autoload-Hinweis siehe Abschnitt [Chat-Kurzbefehle](#chat-kurzbefehle).

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
5. **Success Table** - Erfolgsraten siehe [Würfelmechanik](core/wuerfelmechanik.md#w6-vs-w10).
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
    Überblick im [Gameflow-Spickzettel](gameplay/kampagnenstruktur.md#gameflow-spickzettel).
12. **Mini-Walkthrough** - siehe Abschnitt "Mauerbau 1961" in
    [kampagnenstruktur.md](gameplay/kampagnenstruktur.md#mini-walkthrough-mauerbau-1961).
    Die Missionsbeispiele folgen dort dem einheitlichen 12-Szenen-Ablauf.
13. **Filmischer Einstieg** - das Modul
    [Cinematic Start](systems/gameflow/cinematic-start.md)
    beschreibt einen sofort spielbaren Auftakt.
14. **Demo-Mission "Feuerkette 1410"** - 45-Min-Sabotage im 12-Szenen-Format.
    [Zum Modul](gameplay/kampagnenstruktur.md#quick-mission-feuerkette-1410).
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

- [Paradoxon-Index](systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
- [Immersives Laden](systems/gameflow/speicher-fortsetzung.md#immersives-laden)
- [Makros im Überblick](systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick)
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
[Speicher-Modul](systems/gameflow/speicher-fortsetzung.md#cross-mode-import).

</details>

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
- **Speichern.** Einsätze lassen kein Speichern zu; der Dispatcher meldet
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
([Boss-DR-Skala](gameplay/kampagnenstruktur.md#boss-rhythmus-pro-episode)); nach
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
`standard|normal|gm_third_person` plus `action_mode=uncut` und stellt sie beim
Laden sofort wieder her (z. B. `contrast: high`, `badge_density: dense`,
`output_pace: slow`). `voice_profile` akzeptiert nur `gm_third_person` (Default)
oder `gm_observer`; alle anderen Eingaben werden auf das Default gehoben.
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
Siehe [Missionsdauer-Tabelle](gameplay/kampagnenstruktur.md#missionsdauer).

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
  verweist auf das Offline-FAQ. Details siehe [Runtime-Helfer](doc.md#comms-check).
- **Offline-Fallback:** `!offline` gibt höchstens einmal pro Minute das Kodex Offline-FAQ aus.
  Es erinnert Schritt für Schritt daran, wie die Crew den Uplink erneut herstellt:
  - Terminal oder Hardline suchen, Relay koppeln und Jammer-Override prüfen - bis
    dahin bleibt der Kodex stumm.
  - Mission normal fortsetzen: HUD liefert lokale Logs. HQ-Deepsaves/Cloud-Sync
    laufen erst nach der Rückkehr ins HQ (HQ-only, keine Save-Sperre).
  - Ask→Suggest-Fallback nutzen: Aktionen als "Vorschlag:" kennzeichnen und auf
    Bestätigung warten.

### Start & Load - LLM-Dispatcher (ohne externe Runtime)

Siehe das [Mini-Einsatzhandbuch](#mini-einsatzhandbuch) für Startbefehle.

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
  [`internal/qa/fixtures/savegame_v6_test.json`](internal/qa/fixtures/savegame_v6_test.json).
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
  mit Defaults (`standard|normal|gm_third_person`, `action_mode=uncut`),
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

## Mini-FAQ

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
  `voice_profile:"gm_third_person"|"gm_observer" }`
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
[`systems/gameflow/speicher-fortsetzung.md`](systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
festgelegt: Px 0-4 erzeugt keine Maluswerte, Px 5 triggert `ClusterCreate()`
und setzt nach der Rift-Op auf 0 zurück.

## Exfil-Fenster & Sweeps

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
3+ = Hot-Exfil-Gefahr. [Details](gameplay/kampagnenstruktur.md#post-op-sweep)
**Ziel:** Freiraum für Erkundung - unter spürbarem Zeit- und Nerven-Druck.
**HUD** zeigt ab Zielerfüllung `ANCR Ort · RW mm:ss` und `Stress`. (Speichern
weiterhin ausschließlich im **HQ**.)

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

## Level & EP-Kurve

- Lvl 1-10: +1 Level pro Mission.
- Lvl 11-15: 2 Missionen/Level.
- Lvl 16+: 3 Missionen/Level.
  Pro Aufstieg genau eines: `+1 Attribut` oder `Talent/Upgrade` oder `+1 SYS`.
  Ab Attribut 11 wechselt das Würfelsystem auf W10.
  Siehe [Core-Ops CU-Belohnungen](systems/currency/cu-waehrungssystem.md#core-ops-belohnungen).

## Regelreferenz

### Proben & Schwierigkeitsgrad

Bei ungewissen Aktionen legt die Spielleitung einen **Schwierigkeitsgrad (SG)** fest. Faustregeln:
SG 5 = leicht, SG 8-9 = mittel, SG 12 = schwierig, SG 15+ = sehr schwer.
Ausführliche Tabellen stehen in
[core/zeitriss-core.md](core/zeitriss-core.md) und
[core/wuerfelmechanik.md](core/wuerfelmechanik.md).

Die **Riftstufe** entspricht der Anzahl offener Seeds. Erst nach der Episode
erhöht jeder Seed den Schwierigkeitsgrad um +1 und steigert die CU-Belohnung (1
Seed = ×1.2, 2 Seeds = ×1.4 usw.). Details findet ihr unter
[Offene Rifts](gameplay/kampagnenstruktur.md#offene-rifts).
Rift-Missionen verwenden weiße Stern-Symbole (☆), die den SG-Bonus ab Episodenende anzeigen.
Ein Seed entspricht einem Stern und erhöht die Schwelle um +1.
Mehr als fünf Seeds können als `☆☆☆☆☆+` notiert werden.
[Kreative Generatoren](gameplay/kreative-generatoren-missionen.md).

### Difficulty-Konverter

| ☆-Symbole | SG-Zuschlag |
| --------- | ----------- |
| ☆         | +1          |
| ☆☆        | +2          |
| ☆☆☆       | +3          |
| ☆☆☆☆      | +4          |
| ☆☆☆☆☆     | +5          |
| ☆☆☆☆☆+    | +6 und mehr |

Paramonster verwenden Totenkopf-Icons (💀) als eigenen
Schwierigkeitswert. Diese Angabe hilft nur bei der Einschätzung des
Kampfpotenzials und verändert **nicht** den SG einer Mission.

### Wichtige Makros

Makros siehe
[speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick),
den Abschnitt zum
[Paradoxon-Index](systems/gameflow/speicher-fortsetzung.md#paradoxon-index) und zum
[Immersiven Laden](systems/gameflow/speicher-fortsetzung.md#immersives-laden):

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
| [Grundwürfelsystem (W6)](core/wuerfelmechanik.md)      |  ✅  |      |      | Kernmechanik - explodierende Würfel        |
| [Paradoxon-Index](core/zeitriss-core.md)               |  ✅  |      |      | Kampagnen-Fortschritt                      |
| [Boss-Rhythmus 5/10](gameplay/kampagnenstruktur.md)    |  ✅  |      |      | Mini- & Episoden-Boss nach Missionsnummern |
| [Stress-System](characters/zustaende.md)               |      |  ✅  |      | Für psychische Belastung und Druck         |
| [W10-Variante ab Attribut 11](core/wuerfelmechanik.md) |      |  ✅  |      | Breitere Würfelspanne für große Missionen  |
| [Psi-Kräfte / Psi-Heat](systems/kp-kraefte-psi.md)     |      |  ✅  |      | Standardmodul, wissenschaftlich erklärbar  |

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
  [Temporale Tools](characters/ausruestung-cyberware.md#temporale-tools)
- Basiswaffe nach Einsatzprofil
- Universelles Werkzeug oder Scanner

_Details zur Hardware siehe_
[HUD & Comms - Spezifikation](characters/hud-system.md#hud-comms-spec).
_HUD-Zustände & optionale Event-Icons:_ [HUD-Icons](characters/hud-system.md#hud-icons).

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
  [HUD-Spec](characters/hud-system.md#hud-comms-spec)
- _Wie weit reicht Funk?_ → **≈ 2 km**, Gelände/Jammer wirken.
  [Toolkit](systems/toolkit-gpt-spielleiter.md#funk-signale)
- _Relais/Kabel?_ → heben Reichweiten- oder Jammer-Beschränkungen auf;
  `comms_check()` zählt sie als `relays=true`.
- _Wann spricht der Kodex?_ → Nur mit aktivem Comlink-Uplink. **HQ/ITI = Vollzugriff**
  (Offline gilt nur im Einsatz). In Funkepochen gilt eine **ca. 2 km Bubble ab
  Einstiegspunkt**, erweiterbar per Relais/Kabel; Jammer oder funklose Ären
  (z.B. Mittelalter) schalten den Kodex stumm → nur HUD/Logs laufen. `!offline`
  höchstens **1×/Minute** triggert das Offline-FAQ, bis der Hardware-Link wieder
  steht. Endet eine Mission offline, blockt der SaveGuard jeden HQ-Deepsave,
  bis der Re-Sync erfolgt.

HUD-Zustände erscheinen als Backticks; Event-Icons sind optional
(Feature-Flag). ☆ und 💀 dienen als Regelnotation und gehören nicht zum HUD.

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
- **Voice-Lock:** Erzählinstanz = dritte Person (`ui.voice_profile =
gm_third_person`). Entscheidungsprompts dürfen die Spielenden adressieren,
  Erzählsätze und Beschreibungen bleiben in 3rd Person.
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

† Das Artefakt-Wurfskript greift standardmäßig in Szene 10 (Rift-Boss) automatisch.
  Optional erlaubt `rift_artifact_variant=start_roll` einen Startwurf, bleibt aber
  bei **max. 1 Artefakt pro Mission**. Relikte zählen als Story-Items und nutzen
  den normalen Generator.

**Artefakt-Sink:** Artefakte bleiben handelbar wie Gear (Tausch, Schenkung oder
Verkauf zulässig), aber die Abrechnung läuft über Research-/Archivwerte statt
Marktpreis. Archivieren zieht sie endgültig aus der Wirtschaft, CUs fließen nur
über den HQ-Pool und nie als automatischer Sellout.

## Kampagnenhierarchie

Damit ihr den Umfang eurer Abenteuer besser einschätzen könnt, hier die Begriffe im Überblick:

- **Mission** - einzelner Einsatz von etwa 12 Szenen.
- **Episode/Fall** - sammelt rund zehn Missionen im gleichen Setting.
- **Arc** - mehrere Episoden bilden einen Handlungsbogen.
- **Kampagne** - verknüpft mehrere Arcs zur Gesamtgeschichte.

## Struktur

Alle Regeln liegen als einzelne Markdown-Dateien vor und werden einzeln in das KI-Tool geladen.
Die folgende Tabelle listet alle Regelmodule. Quickref und andere Unterabschnitte
sind der Übersicht halber aufgeführt.
`README.md` und `master-index.json` dienen nur zur Orientierung:

| Datei                                                                                           | Inhalt                                        |
| ----------------------------------------------------------------------------------------------- | --------------------------------------------- |
| [README.md](README.md)                                                                          | Überblick über Projekt und Workflow           |
| [core/zeitriss-core.md](core/zeitriss-core.md)                                                  | Grundregeln und Setting                       |
| [core/wuerfelmechanik.md](core/wuerfelmechanik.md)                                              | Würfelsystem & Proben                         |
| [Quickref](core/wuerfelmechanik.md#schwierigkeits-benchmark-tabelle)                            | Psi- & Konflikt-Quickref                      |
| [characters/charaktererschaffung-grundlagen.md](characters/charaktererschaffung-grundlagen.md)  | Charaktererschaffung (Grundlagen)             |
| [characters/charaktererschaffung-optionen.md](characters/charaktererschaffung-optionen.md)      | Optionen, Archetypen & Teamrollen             |
| [characters/ausruestung-cyberware.md](characters/ausruestung-cyberware.md)                      | Ausrüstung, Waffen & Implantate               |
| [characters/zustaende.md](characters/zustaende.md)                                              | Zustände, Paradoxon & Statusregeln            |
| [characters/hud-system.md](characters/hud-system.md)                                            | HUD-Interface & Anzeige-Logik                 |
| [gameplay/kampagnenstruktur.md](gameplay/kampagnenstruktur.md)                                  | Kampagnenaufbau, Preserve vs Trigger & ITI-HQ |
| [gameplay/fahrzeuge-konflikte.md](gameplay/fahrzeuge-konflikte.md)                              | Fahrzeuge & Konfliktsystem                    |
| [kreative-generatoren-missionen.md](gameplay/kreative-generatoren-missionen.md)                 | Mission & Kampagnen-Generatoren               |
| [gen-begegnungen.md](gameplay/kreative-generatoren-begegnungen.md)                              | NPC & Encounter-Gen                           |
| [Para-Creature-Generator](gameplay/kreative-generatoren-begegnungen.md#para-creature-generator) | Urban Myth Edition                            |
| [Boss-Generator](gameplay/kreative-generatoren-begegnungen.md#boss-generator)                   | Mini-, Arc- und Rift-Bosse                    |
| [gameplay/massenkonflikte.md](gameplay/massenkonflikte.md)                                      | Verfolgungsjagden & Massenkonflikte           |
| [gameplay/kampagnenuebersicht.md](gameplay/kampagnenuebersicht.md)                              | Kampagnenübersicht                            |
| [systems/kp-kraefte-psi.md](systems/kp-kraefte-psi.md)                                          | Psi-Kräfte, Talente & Regeln                  |
| [systems/gameflow/speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md)            | Speicher-/Fortsetzungssystem                  |
| [systems/gameflow/cinematic-start.md](systems/gameflow/cinematic-start.md)                      | Cinematic-Gruppenstart                        |
| [systems/currency/cu-waehrungssystem.md](systems/currency/cu-waehrungssystem.md)                | CU-Währungssystem                             |
| [systems/toolkit-gpt-spielleiter.md](systems/toolkit-gpt-spielleiter.md)                        | Toolkit für die KI-Spielleitung               |
| [kampagnenstruktur.md](gameplay/kampagnenstruktur.md#beispiel-episoden)                         | Beispiel-Episoden & Rift-Op                   |

Die Modulnummern spiegeln die Veröffentlichungshistorie wider. Nach Modul 6
folgt das nun veröffentlichte Modul 7, anschließend 8A und 8B.

Die Dateien können als Trainingsgrundlage für ein LLM dienen, um ZEITRISS autonom zu leiten.

**Hinweis:** Das Spiel besteht aus **25** Regelmodulen. Sie verteilen sich auf
18 Markdown-Dateien; mehrere Module sind Abschnitte anderer Dateien. Zusammen
mit `README.md` und `master-index.json` umfasst das Regelwerk **20** Dateien -
die Wissensspeicher-Slots sind damit vollständig belegt.
`meta/masterprompt_v6.md` (Local-Uncut 4.2.6) wird separat per Copy-Paste
genutzt. Die Legacy-Fassung liegt unter
`meta/archive/masterprompt_v6_legacy.md`. Im `master-index.json` erscheinen
**25** Slugs, weil manche Einträge Kurz- und Langfassungen desselben Moduls
auflisten.
Eine kompakte
[HUD-Übersicht zu Health, Stress und Zuständen](characters/hud-system.md#hud-quickref)
fasst die wichtigsten Effekte zusammen.
Ausführliche Hintergründe liefert das Modul
[Cinematisches HUD-Overlay](characters/hud-system.md#cinematisches-hud-overlay).

| Konflikt | Spannung | Exploding 6 nutzen |
| Auswertung | Konsequenzen | Rufpunkte, Ressourcen |

### Lines & Veils (optional)

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

## Spielstart

Um ein Abenteuer mit GPT zu beginnen, tippe einen der folgenden Kurzbefehle in dein Chatfenster
(Icons sind optional):

- **`Spiel starten (solo [klassisch|schnell])`** - Einzelner Chrononaut; GPT führt
  die NSCs.
- **`Spiel starten (npc-team [0-4] [klassisch|schnell])`** - GPT stellt
  NPC-Begleiter bereit (Team gesamt 1-5).
- **`Spiel starten (gruppe [klassisch|schnell])`** - Mehrere reale Spieler laden
  ihre eigenen Speicherstände oder erstellen gemeinsam neue Charaktere; GPT
  koordiniert die Szene.
- **`Spiel laden`** - Lädt einen vorhandenen Gruppen- oder Solo-Spielstand.
  GPT fordert den Speicher-Code an und führt dich oder die Gruppe nach einem
  Rückblick nahtlos weiter - ohne Auswahlmenü für `klassisch`/`schnell`.

`mixed|preserve|trigger` wählst du im HQ via `!kampagnenmodus`. Standard ist `mixed`;
der Modus wird in `campaign.mode` und `campaign.seed_source` hinterlegt, bevor Starts
oder Arena-Abzweigungen laufen. Legacy-Starts mit `preserve|trigger` in den
Klammern werden mit einem Hinweis abgebrochen.

Der Compliance-Hinweis entfällt; die Spielleitung fragt direkt nach gewünschter
Ansprache und Spielerzahl oder übernimmt beides aus dem Startbefehl.
Sie merkt sich beides, nutzt im Solo-Modus `Du` und im Gruppenmodus `Ihr`.
Das anschließende Startbanner übernimmt automatisch die passende Form.
Beispiel: `🟢 ZEITRISS 4.2.6 - Einsatz für {{dich|euch}} gestartet`.

- `Spiel starten (...)` → Charaktererschaffung → HQ-Phase → Mission
  ([Cinematic Start](systems/gameflow/cinematic-start.md)).
- `Spiel laden` → Save einlesen → Rückblick → Mission fortsetzen
  ([speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md)).

Wird `Spiel laden` ohne JSON-Block eingegeben, fordert GPT den Spielstand an
und setzt nicht aus dem Nichts fort.

Details zum Speichersystem findest du in
[speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md).

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
Nach jedem Zeitsprung und nach jeder Mission öffnet sich ein
**Nullzeit-Menü**. Hier bestimmt die Gruppe, wie ausführlich die
HQ-Phase ablaufen soll. Zur Wahl stehen drei Optionen:

1. **HQ manuell erkunden** - volle HQ-Szenen mit Shopbesuchen, Kodex-Begleitung,
   Fraktions-RP, Feilschen und ausführlichem Briefing/Quartierausbau.
2. **Schnell-HQ** - wenige Klicks für Heilung und Einkauf.
3. **Auto-HQ & Save** - automatische Abwicklung, dann direkt zur nächsten Mission.

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
    Ab Level 10 schaltet die Runtime automatisch den Chronopolis-Schlüssel frei,
    setzt `logs.flags.chronopolis_unlocked=true` plus
    `chronopolis_unlock_level=10`, schreibt ein `chronopolis_unlock`-Trace-Event
    (Level/Quelle) und blendet den HUD-Toast
    `Chronopolis-Schlüssel aktiv - Level 10+ erreicht.` ein. Fehlende Flags werden
    beim Laden nachgezogen, falls Level oder Key-Item bereits vorliegen; Trace
    und Toast werden dann einmalig nachgereicht.
- **Chronopolis** ist ein optionaler City-Anbau ab Level 10 und wird über
  den "Chronopolis-Schlüssel" freigeschaltet. `campaign.loc` wechselt auf
  `CITY`, Speichern bleibt blockiert.
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

**Action-Contract-Schalter.** Für Plattformwechsel gibt es einen Gewalt-Regler:
`modus action|gewalt konform|uncut` (Alias: `frei|open|full`). Standard ist
`uncut`; Legacy-Werte wie `fsk12|standard|off` fallen automatisch auf
`konform`. Das Platform-Contract persistiert `pattern=full_scene`,
`loot_policy=full_loot`, `body_handling=protocol`. Grundregel: keine Schritt-
für-Schritt-Gewalt, kein Body-Handling. Kämpfe, Hacking und Gewalt bleiben
**filmisch**: Beschreibe Beats, Dynamik, Geräusche, Licht, Impact und Risiko,
aber abstrahiere die Technik. Konsequenzen laufen über Noise, Stress, Heat oder
enge Zeitfenster. Optional kann `log_action_contract_guard("Notiz",
{phase, scene})` genutzt werden; der Save hält
`logs.flags.platform_action_contract` und `logs.flags.howto_guard_hits[]`.
Loot-Blöcke sind wieder regulär Teil des Gameplays (Waffen/Tools, Keys/Daten,
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
[Charaktererschaffung](characters/charaktererschaffung-grundlagen.md) und
[Zeitriss-Core](core/zeitriss-core.md) für weitere Hinweise.

## Generator-Utilities

Neuer Eintrag? Prüfe kurz, ob der Text bereits in einer anderen Liste steht.
`objective` und `twist` sollten sich nicht doppeln. Falls du denselben Satz in
beiden Feldern findest, wähle eine Variante oder streiche ihn.

## Glossar

Kurze Erklärungen wichtiger Abkürzungen:

- **CU** - Chrono-Units, universelle Missionswährung.
- **Retina-HUD (AR-Kontaktlinse)** - [Standardausrüstung](#standardausruestung) /
  [HUD-&-Comms-Spec](characters/hud-system.md#hud-comms-spec).
- **Comlink (Ohrstöpsel)** - [Standardausrüstung](#standardausruestung) /
  [HUD-&-Comms-Spec](characters/hud-system.md#hud-comms-spec) /
  [`comms_check`](systems/toolkit-gpt-spielleiter.md#comms-check).
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
  [HUD-&-Comms-Spec](characters/hud-system.md#risk-level-badges).

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
  ([Missionsdauer](gameplay/kampagnenstruktur.md#missionsdauer),
  [HUD-Macros](systems/toolkit-gpt-spielleiter.md#startscene--endscene-macros)).
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

[stim-reg]: characters/ausruestung-cyberware.md#stim-reg-cap-injector
[burst-slot]: systems/kp-kraefte-psi.md#burst-slot
[adrenalinschub]: systems/kp-kraefte-psi.md#adrenalinschub
[notfall-stimulanz]: characters/charaktererschaffung-optionen.md#notfall-stimulanz
[char-gear]: characters/charaktererschaffung-grundlagen.md#zugang-zu-ausruestung--cyberware-hq-phase
[psi-pp-regeneration]: systems/kp-kraefte-psi.md#psi-pp-regeneration
[psi-heat-track]: systems/kp-kraefte-psi.md#psi-heat-track
[llm-ready-badge]: https://img.shields.io/badge/LLM--Ready-%E2%9C%85-success
[llm-ready-link]: systems/gameflow/speicher-fortsetzung.md#paradoxon-index

## Wie du beitragen kannst

Hinweise zum Einreichen von Änderungen sowie Schreibregeln
liegen repo-intern in den Beitragsrichtlinien vor.
Für lokale Checks nutze die dort beschriebene `pre-commit`-Integration.

Die Inhalte stehen für private kreative Nutzung bereit.
ZEITRISS® ist eine beim DPMA eingetragene Wortmarke (Reg.-Nr. 30 2025 215 671).
Eine 1:1-Kopie oder kommerzielle Veröffentlichung ist nur mit Zustimmung
erlaubt (siehe [LICENSE](LICENSE)).
Gemäß Lizenz richten sich diese Regeln ausschließlich an Erwachsene (18+).

© 2025 pchospital - ZEITRISS® - private use only. See LICENSE.
