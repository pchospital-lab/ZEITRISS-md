---
title: "ZEITRISS-md Zeitreise RPG"
version: 4.2.3
tags: [meta]
---

# ZEITRISS®-md Zeitreise RPG

[![LLM-Ready ✅][llm-ready-badge]][llm-ready-link]

> **Kurzfassung:** ZEITRISS® schickt euch als operative Chrononauten in ein
> Tech-Noir-Zeitreise-RPG mit KI-Spielleitung, explodierenden Würfeln und
> JSON-Charakterbögen.
> **Markenhinweis:** ZEITRISS® ist eine eingetragene Marke von Florian Michler.
> **DPMA-Dossier:** Der vollständige Registerauszug liegt im
> [Markenbriefing](docs/trademark.md); haltet das Aktenzeichen 30 2025 215 671.9
> bereit.

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
1. [Beispielworkflow](#beispielworkflow)
1. [Spielstart](#spielstart)
1. [Spielmodi](#spielmodi)
1. [Generator-Utilities](#generator-utilities)
1. [Glossar](#glossar)
    1. [Huminen](#huminen)
    1. [Begriffsklärung](#begriffsklärung)
    1. [Zeiteinheiten](#zeiteinheiten)
    1. [Zeitgebundene Effekte](#zeitgebundene-effekte)
1. [Playtest Feedback](#playtest-feedback)
1. [Wie du beitragen kannst](#wie-du-beitragen-kannst)

<!-- Macro: ShowComplianceOnce -->
{% macro ShowComplianceOnce() -%}
Compliance-Hinweis: ZEITRISS ist ein Science-Fiction-Rollenspiel. Alle Ereignisse sind fiktiv.
{%- endmacro %}

<!-- Macro: StoreCompliance (Alias) -->
{% macro StoreCompliance() -%}
{{ ShowComplianceOnce() }} {# Alias für Legacy-Prompts, bitte ShowComplianceOnce bevorzugen. #}
{%- endmacro %}

## Überblick

**ZEITRISS-md** bietet ein schlankes Regelwerk im Zeitriss-Technoir-Stil. Ihr
spielt operative Chrononauten – Agenten des ITI – in taktisch optimierten
Biohüllen. Bereits zu Beginn entscheidet ihr euch für eine genetische
Grundform: Entweder Homo sapiens oder ein abgeleiteter Hominin-Typ wie
Neandertaler, Denisova oder Atlanter-Vorläufer. Diese Wahl prägt eure
Physiologie, euer Sozialprofil und den Zugriff auf bestimmte Talente. Eure
Hülle ist keine Tarnung – sie ist euer Körper. Ihr erkundet historische Epochen
und beseitigt Anomalien. Das System verwendet explodierende Würfel und
protokolliert Zustände im JSON-Charakterbogen. Texte und Illustrationen stehen
unter [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), der
Programmcode unter der [MIT-Lizenz](https://opensource.org/licenses/MIT).
Details findest du in [LICENSE](LICENSE).

## TL;DR – ZEITRISS in 6 Punkten

1. **Agents.** Chrononauten decken Zeitverschwörungen auf.
2. **Mission Phases.** Core-Ops verlaufen wie Episoden: Briefing → Infiltration →
   Intel/Konflikt → Exfiltration → Debrief – insgesamt zwölf Szenen. Rift-Ops sind
   eigenständige Filme in drei Akten mit vierzehn Szenen.
3. **Exploding Dice.** W6, ab Attribut 11 W10; Heldenwürfel erst ab 14.
4. **Paradoxon-Index (Px)** belohnt bewahrte Kausalketten. Schlampiges Vorgehen
   stagniert, destruktive Ausreißer senken Px; ein Fail oder Patzer zieht den Index
   um 1 Punkt nach unten. Bei Px 5 enthüllt `ClusterCreate()` 1–2 Rift-Seeds –
   spielbar nach Episodenende. Jede neue Px‑5‑Schwelle **stapelt** zusätzliche
   Seeds im Pool, der Zähler springt nur für den nächsten Zyklus auf 0.
5. **Hard Sci-Fi.** Keine Magie, Psi kostet Power-Punkte.
6. **Boss-Rhythmus.** In Mission 5 einer Episode erscheint ein Mini-Boss, in Mission 10
   der Episoden-Boss. Rift-Operationen platzieren ihren Boss in Szene 10. Das Toolkit
   löst `generate_boss()` an diesen Punkten automatisch aus.

Siehe den [Schnellstart-Spickzettel](#schnellstart-spickzettel) für eine kompakte
Einstiegshilfe.

## Wissensspeicher & Plattform-Setup {#wissensspeicher--plattform-setup}

Die komplette Operator-Checkliste liegt in
[docs/maintainer-ops.md](docs/maintainer-ops.md). Dort findet ihr die
Plattform-Workflows, Upload-Notizen sowie die Rollenaufteilung zwischen
Custom-GPT, Repo-Agent und Ingame-Kodex. Dieses README listet nur die
Laufzeitreferenz – bei Fragen zum Hochladen, Synchronisieren oder Testen führt
euch das Maintainer-Dokument.

### Wissensspeicher laden

1. **Dateien importieren:** Lade `README.md`, `master-index.json` sowie alle
   unten aufgeführten 18 Runtime-Module in den Wissensspeicher deiner
   Zielplattform. Diese 20 Slots sind exklusiv für die Runtime-Dokumentation
   reserviert; andere Repo-Dateien dürfen nicht in den Wissensspeicher wandern.
2. **Masterprompt spiegeln:** Kopiere `meta/masterprompt_v6.md` als
   Systemprompt (MyGPT: Masterprompt-Feld, Proton LUMO: erste Chatnachricht,
   OpenWebUI: Instruktionsfeld). Optional kannst du den Masterprompt zusätzlich
   als Wissensspeicher-Modul ablegen.
3. **Slot-Kontrolle:** Prüfe nach jedem Speicherstand oder Plattform-Export, ob
   alle 20 Module weiterhin geladen sind. Falls ein Modul fehlt oder veraltet
   wirkt, fordere explizit das korrekte Markdown nach und lade es erneut.

### Runtime-Module im Wissensspeicher

| Kategorie    | Datei |
|--------------|-------|
| **characters** | `characters/ausruestung-cyberware.md` |
|              | `characters/charaktererschaffung.md` |
|              | `characters/cyberware-und-bioware.md` |
|              | `characters/psi-talente.md` |
|              | `characters/zustaende-hud-system.md` |
| **core**     | `core/wuerfelmechanik.md` |
|              | `core/zeitriss-core.md` |
| **gameplay** | `gameplay/fahrzeuge-konflikte.md` |
|              | `gameplay/kampagnenstruktur.md` |
|              | `gameplay/kampagnenuebersicht.md` |
|              | `gameplay/kreative-generatoren-begegnungen.md` |
|              | `gameplay/kreative-generatoren-missionen.md` |
|              | `gameplay/massenkonflikte.md` |
| **systems**  | `systems/currency/cu-waehrungssystem.md` |
|              | `systems/gameflow/cinematic-start.md` |
|              | `systems/gameflow/speicher-fortsetzung.md` |
|              | `systems/kp-kraefte-psi.md` |
|              | `systems/toolkit-gpt-spielleiter.md` |

### Runtimes & Tests außerhalb des Wissensspeichers

- `internal/runtime/runtime-stub-routing-layer.md`, `runtime.js`, Hilfsskripte und
  Test-Tools bleiben lokal im Repo und werden **nicht** in produktive
  Wissensspeicher hochgeladen.
- Spiegle relevante Laufzeitlogik (z. B. Foreshadow-Persistenz, HUD-Badges) als
  Regelwerk, Prozessbeschreibung oder Pseudocode innerhalb der Wissensbasis
  (README, `kb/`-Äquivalente, Runtime-Module), damit produktive GPTs ohne
  externe Skripte denselben Funktionsumfang erhalten.
- Nutze die lokalen Runtimes weiterhin für Entwicklung und Tests. Dokumentiere
  Abweichungen zwischen Skript und Wissensspiegelung im Laufzeitjournal (siehe
  `internal/qa/logs/`) und verweise in Commits/PRs auf die entsprechenden
  Mirror-Schritte.
- **Repo-Agent:innen spiegeln jede Laufzeitänderung unmittelbar in der
  Wissensbasis (README, Runtime-Module etc.), einschließlich Foreshadow-Logik,
  HUD-Badges und Save-Strukturen.**
- **QA-Runner:** `npm run test:acceptance` bzw. `tools/test_acceptance_followups.js`
  prüfen Mission‑5/HUD-Golden-Files aus
  `internal/qa/fixtures/mission5_badge_snapshots.json`. Die Läufe gehören zu den
  Pflichttests und werden im QA-Log referenziert.
- **Maintainer:innen prüfen nach abgeschlossenen Tests lediglich den fertigen
  Wissensstand und übertragen ihn anschließend gemäß
  `docs/maintainer-ops.md` in die produktiven Plattform-Runtimes.**

## Repo-Map {#repo-map}

```
ZEITRISS-md/
├─ README.md                # Laufzeit-Referenz & Plattform-Hinweise
├─ core/                    # Grundregeln & Zeitriss-Mechaniken (Runtime)
├─ characters/              # Charaktererschaffung, Ausrüstung, Zustände (Runtime)
├─ gameplay/                # Kampagnenstruktur, Generatoren, Missionsbau (Runtime)
├─ systems/                 # Gameflow, Währungen, Toolkit für die KI-Spielleitung (Runtime)
├─ internal/qa/             # QA-Fahrplan, Audit, Logs (Meta-Artefakte)
├─ internal/runtime/        # Entwickler-Stubs (`runtime-stub-routing-layer.md`) & lokale Runtimes
├─ meta/                    # Masterprompts, Hintergrundbriefe, Dev-only Inhalte
├─ docs/                    # Maintainer-Ops, Smoke-Tests, Starttranskripte
│                           # (tags: [meta]; inkl. Fahrplan & Protokoll)
├─ scripts/, tools/         # Hilfsprogramme & Linter (Dev-only)
└─ master-index.json        # Übersicht aller Module und Slugs
```

### Dokumenten-Landkarte {#dokumenten-landkarte}

- **`README.md`** – Einstieg für alle Rollen. Führt Runtime-Referenzen, Kurzbefehle sowie die
  Dokumenten-Landkarte und verweist auf weiterführende Leitfäden.
- **`AGENTS.md`** – Arbeitsgrundlage für den Repo-Agenten (Programmier-KI). Skizziert Rollen,
  Übergaben und verweist auf die verbindlichen Prüfpfade in `CONTRIBUTING.md`.
- **`CONTRIBUTING.md`** – Richtlinien für Beitragende. Bündelt Workflow, Formatierung sowie die
  vollständige Prüf-, Link- und Compliance-Checkliste inklusive Pflicht-Tests.
- **`docs/maintainer-ops.md`** – Operatives Handbuch für Plattformpflege und Runtime-Spiegelungen
  der Maintainer:innen.
- **`docs/qa/tester-playtest-briefing.md`** – Briefing und Checklisten für QA-Läufe.
- **`meta/masterprompt_*.md`** – Laufzeit-Briefings für MyGPT. Werden im Repo aktiv gepflegt,
  dienen der Spielleitung als Grundlage und enthalten keine Dev-Vorgaben wie `AGENTS.md`.

## Schnellstart-Spickzettel {#schnellstart-spickzettel}
> **ZEITRISS**: Eine Elite‑Zelle des ITI springt durch die Jahrhunderte, um
> kritische Linienbrüche zu stoppen.
> Kein Schicksal, kein Mysterien‑Blabla – nur harte Einsätze, High‑Tech und
> Sekunden­entscheidungen.
_Die folgenden Punkte bündeln Phasenablauf und Würfelregeln für einen schnellen Einstieg._

Autoload-Hinweis siehe Abschnitt [Chat-Kurzbefehle](#chat-kurzbefehle).

Nach Compliance-Hinweis und Einleitung fragt das System nach
_"klassischer Einstieg"_ oder _"Schnelleinstieg"_.
Wählst du Schnell, tippe **`Schnelleinstieg`** und
das Briefing bleibt kurz, den Twist deckt der Kodex später auf.

Die ersten Schritte in unter zwei Minuten:

- Standardstil: Cinematic/Verbose mit aktivem Kodex. PRECISION optional für Taktikphasen.
1. **Mission ziehen** – nutze einen Seed aus dem Generator.
2. **Drei Ziele** – formuliere klar nummerierte Aufträge.
3. **Proben** – Endwert = Wurf + ⌊Attribut / 2⌋ + Talent + Gear.
4. **Success Table** – Erfolgsraten siehe [Würfelmechanik](core/wuerfelmechanik.md#w6-vs-w10).
5. **Risiko** – misslingt ein Exploding-Wurf und der Gegner explodiert,
   erhält er einen Vorteil.
6. **Paradoxon** – Index bei 5? `ClusterCreate()` erzeugt neue Seeds.
7. **Self-Reflection Off** – `!sf off` setzt das globale Flag
   (`self_reflection: false`) samt Persistenz in `logs.flags.self_reflection`;
   `!sf on` stellt beides zurück. Vor Mission 5 unbedingt manuell toggeln,
   damit HUD-Badge und `scene_overlay()` den Status `SF-OFF` zeigen. Nach
   Mission 5 stellt die Runtime Self-Reflection automatisch auf `SF-ON` zurück –
   sowohl nach Abschluss als auch nach Abbruch (`logs.flags.last_mission_end_reason`).
8. **TK-Nahkampf-Cooldown** – `!tk melee` markiert telekinetische
   Nahkampfangriffe, blendet `TK🌀` im HUD ein und sperrt eine Runde;
   `!tk ready` hebt die Sperre nach dem Cooldown auf.
9. **Chrono-Units** – Einheitliche Formel für Core **und** Rift:
   `Belohnung = Basiswert × Ergebnis × Seed-Multi × Hazard-Pay`
   (400/500/600 CU nach Risiko, Ergebnis 0,3/0,6/1,0/1,2,
   `Seed-Multi = 1 + 0,2 × offene Seeds`, Solo/Buddy = 1,5×).
10. **Mini-Walkthrough** – siehe Abschnitt "Mauerbau 1961" in
   [kampagnenstruktur.md](gameplay/kampagnenstruktur.md#mini-walkthrough-mauerbau-1961).
   Die Missionsbeispiele folgen dort dem einheitlichen 12‑Szenen‑Ablauf.
11. **Filmischer Einstieg** – das Modul
   [Cinematic Start](systems/gameflow/cinematic-start.md)
   beschreibt einen sofort spielbaren Auftakt.
12. **Demo-Mission „Feuerkette 1410"** – 45-Min-Sabotage im 12‑Szenen-Format.
   [Zum Modul](gameplay/kampagnenstruktur.md#quick-mission-feuerkette-1410).
13. **Epilog** – `EndMission(closed_seed_ids, cluster_gain, faction_delta)`
    ruft `kodex_summary()` auf und loggt `Kodex: Seeds … geschlossen ·
    Cluster +… · Fraktion +…`.

## Mini-Einsatzhandbuch {#mini-einsatzhandbuch}

**Startbefehle (Klammern Pflicht):**

- `Spiel starten (solo [klassisch|schnell])` – Erschaffung → HQ-Intro → Briefing →
  Szene 1 · _schnell_: Rolle + Defaults → Briefing
- `Spiel starten (npc-team [0–4] [klassisch|schnell])` – PC bauen + Teamgröße ·
  _schnell_: Rolle + Teamgröße
- `Spiel starten (gruppe [klassisch|schnell])` – alle bauen · _schnell_: Saves
  posten oder Rolle nennen
- `Spiel laden` – Deepsave → Kodex-Recap → HQ/Briefing

Kampagnenmodus (`preserve|trigger`) wird einmalig im HQ gesetzt und im Save gespiegelt:
`!kampagnenmodus preserve|trigger`. Der Wert landet in `campaign.mode`/`seed_source` und
wirkt auf weitere Starts, Cross-Mode-Saves und Arena-Rücksprünge.

**Klammern sind Pflicht.** Beispiel: `Spiel starten (solo)` wird erkannt; `Spiel starten solo`
nicht.
**Rollen-Kurzformen erlaubt:** `infil`, `tech`, `face`, `cqb`, `psi`.

**Regeln:**

- **Nur-HQ-Save** – Speichern ist nur im HQ möglich; Missionszustände sind flüchtig.
- **Ausstieg in Mission** – Möglich, aber ohne Speichern. Gear darf übergeben werden.
  Nächster Save im HQ.
- **Paradoxon & Rifts** – Px 5 ⇒ `ClusterCreate()` (1–2 Rift-Seeds; spielbar nach
  Episodenende; danach Reset). Jeder erneute Px‑5‑Treffer legt weitere Seeds oben
  drauf – es gibt **kein Hard-Limit**. Rift-Starts sind HQ-gebunden
  (`location='HQ'`), verlangen einen abgeschlossenen Episodenlauf
  (`campaign.episode_completed` oder `mission_in_episode ≥ 10`) und greifen
  ausschließlich auf objektförmige `campaign.rift_seeds[]`
  (id/label/status/seed_tier/hook, optionale cluster-/level-Hints) zurück; der
  Normalizer hebt Legacy-Strings an und zieht fehlende Label/Hook/Seed-Tier aus
  dem Seed-Katalog nach.
- **Arena-Resume** – Läuft beim Laden eine PvP-Serie, erzeugt die Runtime ein
  `arena.resume_token` (Tier, Teamgröße, Modus, Audit) und erlaubt `!arena
  resume` ohne erneute Gebühr aus dem HQ.
- **Semver-Toleranz** – Laden klappt, solange `major.minor` aus `zr_version`
  mit `ZR_VERSION` übereinstimmt; Patch wird ignoriert.

[Start-Transkripte ↗](internal/qa/transcripts/start-transcripts.md)

Siehe auch:
- [Paradoxon-Index](systems/gameflow/speicher-fortsetzung.md#paradoxon-index)
- [Immersives Laden](systems/gameflow/speicher-fortsetzung.md#immersives-laden)
- [Makros im Überblick](systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick)
- [Start-Transkripte (Kurz)](#start-transkripte)
- [Abnahme-Smoketest (Dispatcher)](#abnahme-smoketest)

## Start-Transkripte (Kurz) {#start-transkripte}

<details><summary>Solo – Schnelleinstieg (Happy Path)</summary>

**Spieler:**
`Spiel starten (solo schnell) – Rolle: Sniper Alleingänger`

**SL (MyGPT):**
> **Briefingraum**. Projektionen flackern.
> **Kodex-Header:** `EP 01 · MS 01 · SC 01/12 · MODE CORE · Objective: Primärziel sichern`
> **Defaults:** GES-Fokus, Sidearm (SD), Sniper (SD), Basic-Medikit.
> **Legende:** ziviler Gutachter.
> **Fraktionslage:** ruhig.
> —
> *Kurzes Briefing* (3 Ziele). *Dann:* „Szene 1 – Zugangspunkt?“

</details>

<details><summary>Gruppe – Schnelleinstieg (gemischt, 2 Saves + 1 Rolle)</summary>

**Spieler:**
```text
Spiel starten (gruppe schnell)
[A] – Save posten
[B] – Save posten
[C] – Rolle: Face
```

**SL (MyGPT):**
> **Kodex-Archiv – Rückkehrprotokoll aktiviert.**
> Synchronisiere Einsatzdaten: **A** (Lvl 2), **B** (Lvl 2).
> Setze Defaults für **C** (Face): Modulator, Sidearm (SD), Social-Kit.
> Paradoxon-Index: █░░░░ (0/5).
> **HQ-Kurzintro** → **Briefing** (3 Ziele) → **Szene 1**.
> „Führung festlegen? (optional)“

</details>

## Dispatcher-Kurzreferenz

### Dispatcher-Starts & Speicherpfade

- **Spielstart-Varianten.** `Spiel starten` akzeptiert `solo`, `npc-team` und
  `gruppe` plus die Zusätze `klassisch` oder `schnell`. `npc-team` verlangt eine
  Zahl `0–4`, `gruppe` ignoriert Zahlen. Ungültige Kombinationen liefern die
  passenden Fehltexte.
- **Briefing & Schnellstart.** `Spiel starten (solo)` führt direkt ins Briefing
  der aktuellen Episode. `klassisch` blendet Auswahlmenüs ein, `schnell`
  überspringt sie. NPC-Teams werden bei Bedarf automatisch erzeugt und skaliert.
- **Spiel laden.** `Spiel laden` springt ohne Moduswahl in das HQ-Recap,
  aktiviert das Kodex-Overlay und übernimmt alle Save-Flags.
- **Speichern.** Einsätze lassen kein Speichern zu; der Dispatcher meldet
  „Speichern nur im HQ …“ und hält die Mission aktiv.
- **Gear-Aliasse & Px.** Alias-Befehle gleichen Schreibvarianten aus (z. B.
  „Multi-Tool-Armband“ → „Multi-Tool-Handschuh“). Erreicht der Paradoxon-Index
  Px 5, informiert der Kodex, dass neue Seeds erst nach Episodenende spielbar
  sind und danach zurückgesetzt werden.
  Der Alias bleibt ein Stil-Mapping; die Hardware-Regel „kein Armband“ gilt
  weiterhin.

### Boss-Gates & HUD-Badges

`!helper boss` listet Foreshadow-Hinweise für Mission 5 und Mission 10; das Gate
ist ab Missionsstart fest auf `GATE 2/2` gesetzt. Das HUD zeigt zum Start
`GATE 2/2 · FS 0/4` (Core) bzw. `GATE 2/2 · FS 0/2` (Rift); Foreshadow-Hinweise
zählen nur den `FS`-Block hoch. In Szene 10 erscheint automatisch der Toast mit
dem aktiven Boss-Schadensreduktionswert (`−X` Schadensreduktion, skaliert nach
Teamgröße 0–4 (Werte >4 werden geklemmt) und Boss-Typ gemäß
[Boss-DR-Skala](gameplay/kampagnenstruktur.md#boss-rhythmus-pro-episode)). Nach
dem Debrief setzt die Runtime Self-Reflection auf `SF-ON` zurück – unabhängig
davon, ob die Mission abgeschlossen oder abgebrochen wurde.

### Psi-Heat & Ressourcen-Reset

Psi-Aktionen erhöhen `Psi-Heat` pro Konflikt. Nach jedem Konflikt springt der
Wert auf 0. Transfers zurück ins HQ setzen zusätzlich SYS-Auslastung, Stress und
Psi-Heat auf die gespeicherten Grundwerte zurück.

### Accessibility & UI-Persistenz

Der Befehl `!accessibility` öffnet das UI-Panel (Kontrast, Badge-Dichte,
Ausgabetempo). Jede Bestätigung erzeugt den Toast „Accessibility aktualisiert …“
und schreibt die Auswahl in den Save. Der Serializer legt den kompletten UI-
Block ab (`gm_style`, `suggest_mode`, `contrast`, `badge_density`, `output_pace`),
füllt fehlende Felder automatisch mit `standard|normal` und stellt sie beim Laden
sofort wieder her (z. B. `contrast: high`, `badge_density: dense`, `output_pace: slow`).
Legacy-Mappings: `full|minimal` → `standard|compact`, `rapid|quick` → `fast`,
`default|steady` → `normal`.

### Abnahme-Smoketest (Runtime-Overlay)

1. **Dispatcher & Speicherpfade** – Spielstart solo klassisch/schnell, NPC-Teams
   (`npc-team 3|5`), Gruppe (Fehlertext bei Zahl), Gruppe schnell (2 Saves +
   1 Rolle), `Spiel laden` → Kodex-Overlay, Save-Blocker in Mission, Gear-Alias
   und Px 5 Hinweis („Seeds nach Episodenende spielbar“).
2. **Boss-Gates & HUD** – `!helper boss` nach Mission 4 kündigt Szene 5/10 und
   `Gate 2/2` an; Mission 5 startet mit Schritt 0 `!sf off`, blendet
   `Boss-Encounter in Szene 10`, `GATE 2/2` und ggf. `SF-OFF` ein, Szene 10
   triggert `Boss-DR aktiviert – −X Schaden` mit Auto-Reset `SF-ON` zum
   Debrief.
3. **Psi & Ressourcen** – Psi-Konflikt meldet `Psi-Heat +1`, danach Reset;
   HQ-Transfer setzt SYS/Stress/Psi-Heat zurück.
4. **Accessibility & Persistenz** – `!accessibility` speichert Kontrast,
   Badge-Dichte und Ausgabetempo, Toast notieren; nach erneutem Laden bleiben
   die Werte erhalten. Vollständige Wortlaute decken `doc.md` und das
   Tester-Briefing ab.

**Stabile Flows (Regression-Basis)**
- Ask→Suggest-Overlay bleibt getrennt von Self-Reflection und läuft in Solo,
  NPC, Koop und PvP stabil.
- Offline-FAQ (`!offline`) sowie Alias-/Squad-Radio-Logs bestehen den Smoke in
  Solo/NPC/Koop/PvP identisch.
- Alias-Mapping „Multi-Tool-Armband → Multi-Tool-Handschuh“ ist aktiv, ohne die
  Hardware-Regel „kein Armband“ aufzuweichen; die Runtime normalisiert
  Live-Loadouts und Saves automatisch auf den Handschuh.

**Dispatcher-Smoke-Basislinie**
| Schritt | Inhalt | Status |
| ------ | ----------------------------- | -------- |
| 1 | Spielstart solo klassisch/schnell | ✅ stabil |
| 2 | NPC-Team 0–4 erstellt, skaliert | ✅ stabil |
| 3 | Gruppe klassisch/schnell (Fehlertext bei Zahl) | ✅ stabil |
| 4 | Spiel laden → HQ-Recap & Overlay | ✅ stabil |
| 5 | Missions-Blocker verhindern Saves | ✅ stabil |
| 6 | Gear-Alias & Px 5 Hinweis sichtbar | ✅ stabil |


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
> Px-Verlust-Regel ein **Px–1**.
> **HUD** nach Zielerfüllung: `TTL` & `Stress`. **Speichern** nur im **HQ**.

Der HUD-Header zeigt `EP · MS · SC/total · MODE · Objective` plus
klassenabhängige Ressourcen:
- **PSI:** `PP 6/8 · Psi-Heat 2 · SYS 2/6 (free 4) · Stress 1 · Px █░░░░ (1/5)` –
  Psi-Heat baut sich pro aktiver Psi-Aktion in Konflikten auf und springt
  nach jedem Konflikt auf 0.
- **Non-PSI:** `Ammo 12 · SYS 1/4 (free 3) · Stress 1 · Px █░░░░ (1/5)` –
  führt keinen Psi-Heat-Track.
In der Exfil-Phase kommen `ANCR Ort · RW mm:ss` hinzu.
In Szene 1 hängt `FR:Status` an.
`ui.mode_display` wechselt zwischen `label`, `emoji` oder `both`;
auf schmalen Zeilen blendet das System den Rank automatisch aus.

Mission-Fokus ist der Standard (oft "Operator-Stil" genannt).
Kämpfe richten sich gegen Fremdfraktionen, nicht gegeneinander.
In Core-Ops treten Rivalen aus externen Machtblöcken auf,
während Rift-Ops sich ganz auf die jeweilige Anomalie konzentrieren.

Core-Ops dauern durchschnittlich **60–75 Minuten** und umfassen **12 Szenen**.
Rift-Ops strecken sich über etwa **90–120 Minuten** mit **14 Szenen**.
Siehe [Missionsdauer-Tabelle](gameplay/kampagnenstruktur.md#missionsdauer).
### Agenda für Session 0 {#agenda-session-0}

1. **Ton & Modus** – Thriller vs. Stealth-Heist, Mission-Fokus an/aus.
2. **Lines/Veils bestätigen** – siehe Safety Sheet.
3. **Historische Epochen-Wishlist** – Top 3 der Gruppe sammeln.
4. **Teamrollen wählen** – Infiltration, Tech, Face, Sniper …
5. **Paradoxon-Toleranz** – Legt fest, ab welcher Resonanz ihr neue Rifts erspüren möchtet.
6. **Regel-Transparenz** – Overlay und JSON-Log laufen standardmäßig;
   `/debug_rolls` blendet das Log bei Bedarf aus.

### Wahrscheinlichkeits-Übersicht {#wahrscheinlichkeits-uebersicht}

| SG | W6 expl. | W10 expl. | Δ (W10–W6) |
|---:|---------:|----------:|-----------:|
| 5  | 83 %     | 90 %      | +7 %       |
| 7  | 67 %     | 77 %      | +10 %      |
| 8  | 50 %     | 65 %      | +15 %      |
| 10 | 33 %     | 53 %      | +20 %      |

### Chat-Kurzbefehle {#chat-kurzbefehle}

Im Live-Chat kann nicht gescrollt werden. Diese Befehle rufen sofort Regeln ab:

### Comms-Core – Funkcheck in Kurzform {#comms-core}

- **Hardwarepflicht:** Funk funktioniert nur mit Comlink (≈ 2 km), Kabel oder
  Relais. Jammer-Overrides müssen explizit gesetzt werden (`device='jammer_override'`).
- **Reichweitenprüfung:** `comms_check()` akzeptiert Meter (`range_m`) oder
  Kilometer (`range_km`) und normalisiert Werte automatisch. Jammer ohne Kabel/
  Relais blockieren den Kontakt.
- **Fallback:** Scheitert der Check, meldet der Kodex `CommsCheck failed …` und
  verweist auf das Offline-FAQ. Details siehe [Runtime-Helfer](doc.md#comms-check).
- **Offline-Fallback:** `!offline` gibt höchstens einmal pro Minute das Kodex Offline-FAQ aus.
  Es erinnert Schritt für Schritt daran, wie die Crew den Uplink erneut herstellt:
  - Terminal oder Hardline suchen, Relay koppeln und Jammer-Override prüfen – bis
    dahin bleibt der Kodex stumm.
  - Mission normal fortsetzen: HUD liefert lokale Logs. HQ-Deepsaves/Cloud-Sync
    laufen erst nach der Rückkehr ins HQ (HQ-only, keine Save-Sperre).
  - Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ kennzeichnen und auf
    Bestätigung warten.

### Start & Load – LLM-Dispatcher (ohne externe Runtime)

Siehe das [Mini-Einsatzhandbuch](#mini-einsatzhandbuch) für Startbefehle.

**Akzeptierte Zusätze:**
- Nach `solo`/`npc-team`/`gruppe` darf optional `klassisch` oder `schnell` folgen
  (auch `classic|fast`).
- `npc-team` akzeptiert Teamgrößen `0–4`; Arena nutzt dieselbe Obergrenze.
- Erlaubte Rollen-Kurzformen: `infil`, `tech`, `face`, `cqb`, `psi`.
- Vor jedem Einsatz ruft der Dispatcher `!radio clear` und `!alias clear` auf,
  damit Funk- und Alias-Logs ohne Altlasten starten.
- Alias- und Funkbefehle akzeptieren beliebige Groß-/Kleinschreibung (`!alias`,
  `!ALIAS`, `!Radio Log` usw.).

**Fehlertexte:**
- `npc-team 5` → „Teamgrößen: 0–4. Bitte erneut eingeben (z. B. npc-team 3).“
- `gruppe 3` → „Bei gruppe keine Zahl angeben. (klassisch/schnell sind erlaubt)“

**Semver (Save-Laden):**
- Save lädt, wenn `major.minor` aus `zr_version` mit `ZR_VERSION` übereinstimmt;
  Patch-Level wird ignoriert.
- Mismatch → „Kodex-Archiv: Datensatz vX.Y nicht kompatibel mit vA.B. Bitte
  HQ-Migration veranlassen.“

**Save v6 – Pflichtfelder & Kompatibilität**
- _Single Source:_ Das vollständige Schema steht in
  `systems/gameflow/speicher-fortsetzung.md`. README und Toolkit zitieren nur
  Auszüge; neue Saves benutzen ausschließlich die v6-Struktur mit
  `party.characters[]` als kanonischem Roster (Legacy-Mirror
  `team.members[]` bleibt nur für Import/Export erhalten).
- `character.id`, `character.attributes.SYS_max`,
  `character.attributes.SYS_installed`, `character.attributes.SYS_runtime`,
  `character.attributes.SYS_used`, `character.stress`, `character.psi_heat`,
  `character.cooldowns` sind immer Teil des HQ-Deepsaves.
- `campaign.px`, `economy` (inklusive `wallets{}`), `logs` (inklusive `hud`,
  `trace`, `artifact_log`, `market`, `offline`, `kodex`, `alias_trace`,
  `squad_radio`, `foreshadow`, `fr_interventions`, `psi`, `arena_psi`,
  `flags`, `flags.merge_conflicts`) sowie `ui` und `arena` werden vom
  Serializer garantiert, damit automatisierte Prüfungen alle Guards
  vollständig abdecken. `logs.field_notes[]` ist optional; fehlt der Block,
  legt der Serializer ein leeres Array an. `character.quarters` wird für HQ/
  Profil-Infos mitgespeichert; `arc_dashboard.timeline` hält Kampagnenereignisse
  fest. Der Arena-Block kennt `queue_state=idle|searching|matched|staging|active|completed`,
  `zone=safe|combat` und klemmt Teamgrößen hart auf 0–4.
- `ui` enthält neben `gm_style`/`intro_seen`/`suggest_mode` die Accessibility-
  Felder `contrast`, `badge_density` und `output_pace`; der SaveGuard bricht
  den HQ-Deepsave ab, wenn eines fehlt. Migration und Serializer füllen
  Legacy-Saves auf `standard|normal` auf.
- Serializer und Migration erzwingen `save_version: 6` – auch Legacy-Saves
  landen nach `migrate_save()` auf dieser Version und ergänzen `ui.intro_seen`
  als boolesches Feld.
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

**Quick-Hilfe:** `!help start` – listet alle vier Befehle mit Kurzbeschreibung.

### Dispatcher- und HUD-Befehle

- `!rules stealth` – zitiert die Passage zu Schleichen.
- `!gear cyberware` – zeigt Ausrüstung oder Implantate.
- `!save` – speichert einen Deepsave (nur im HQ; SaveGuard blockt bei Offline-
  Fallback: „SaveGuard: Offline – HQ-Re-Sync erforderlich.“).
- `!load` – lädt den letzten Deepsave.
- `!suspend` – legt einen flüchtigen Szenen-Snapshot für eine Pause an.
- `!resume` – setzt den letzten Suspend-Snapshot exakt einmal fort und stellt
  Initiative-Leiste sowie HUD-Timer wieder her.
- `!autosave hq` – schaltet Auto-Save im HQ.
- `!accessibility` – öffnet den Accessibility-Dialog (Kontrast, Badge-Dichte, Output-Takt).
  Optionen landen als `contrast=standard|high`, `badge_density=standard|dense|compact`,
  `output_pace=normal|fast|slow` im Save; der Toast „Accessibility aktualisiert …“
  bestätigt jede Änderung.

- `!gear shop` – zeigt Shop-Tier-Liste.
- `!psi heat` – erklärt Psi-Heat und Burn.

- `!hud status` – listet alle Zustände.
- `!reveal artifact` – zeigt Artefakt-Infos im HUD.
- `!regelcheck modul` – zwingt die KI, Regeln aus dem genannten Modul zu laden.
- `!regelreset` – setzt den Regelkontext nach Warnhinweis zurück und lädt alle Module neu.
- `modus verbose` – Filmisch an; Toast `GM_STYLE → verbose (persistiert)`.
- `modus precision` – Kurzprotokoll an (nur taktische Abschnitte); Toast
  `GM_STYLE → precision (persistiert)`.
- `!px` – zeigt aktuellen Paradoxon-Stand inklusive ETA (Heuristik) aus `px_tracker()`.
- `!fr help` – zeigt den aktuellen FR-Status.
- `!dashboard status` – fasst das Arc-Dashboard (Seeds, Fraktionsmeldungen,
  offene Fragen) als Report zusammen.
- `!help dashboard` – Spickzettel für `!dashboard status` und
  Arc-Dashboard-Evidenzen.
- `!boss status` – meldet `Gate x/2 · Mission FS y/4` (Core) bzw. `y/2`
  (Rift) und zeigt Gate-Fortschritt vs. Saisonstand.

### Boss-Gates, Suggest-Modus & Arena (Kurzinfo)

#### Boss-Gate-Status & Terminologie

| Zeitpunkt | Foreshadow-Ziel | Gate-Anzeige | Erwartete Strings |
| --------- | ---------------- | ------------ | ----------------- |
| Episodenstart/HQ | noch nicht gesetzt | kein Gate-HUD | `!boss status` meldet nur Saisonstand `Mission FS 0/4` (Core) bzw. `0/2` (Rift) |
| Nach Mission 4/9 | Hinweise stehen aus | `Gate 0/2` (HUD/Toast) | `!helper boss` zeigt Foreshadow-Liste Szene 5/10, Toast `Gate blockiert – FS 0/4 (Gate 2/2 bleibt gesetzt)` |
| Start Mission 5/10 | FS-Zähler läuft | `GATE 2/2` + `FS 0/4` (Core) bzw. `FS 0/2` (Rift) | `!boss status` meldet `Gate 2/2 · Mission FS 0/4` (oder `0/2`); Mission-5-Badge-Check fordert den sichtbaren `GATE 2/2`-Toast |
| Szene 10 | alle Hinweise platziert | `GATE 2/2` + Boss-Toast | `Boss-DR aktiviert – −X Schaden pro Treffer` (DR skaliert nach Boss- bzw. Teamgröße) |

- **Foreshadow-Gate (Mission 5/10).** Nach `StartMission()` setzt die Runtime
  automatisch `GATE 2/2 · FS 0/4` (Rift: `FS 0/2`) als Badge **und** Toast.
  `ForeshadowHint()` zählt ausschließlich `FS` hoch; Gate bleibt unverändert.
  `!boss status` meldet denselben Snapshot und dient als Mission-5-Badge-Check
  im Smoke-Paket.
- **Persistenz der Gate-Felder.** `scene_overlay()` spiegelt den Gate-Snapshot als
  `logs.flags.foreshadow_gate_*` und dedupliziert `logs.foreshadow[]` (Token-basiert).
  HUD-Badge und Save nutzen konsequent das Muster `GATE 2/2` plus `FS x/y`,
  sodass `!boss status` und Ladepunkte denselben Stand zeigen.
- **Suggest-Modus.** `modus suggest` aktiviert beratende Vorschläge (`SUG-ON` im HUD,
  Overlay `· SUG`), `modus ask` wechselt zurück in den klassischen Fragemodus
  (`SUG-OFF`). Das SUG-Badge ist unabhängig von Self-Reflection und bleibt aktiv,
  auch wenn `SF-OFF` gesetzt wurde.
- **Self-Reflection-Quelle.** Alle Runtime-Flows lesen ausschließlich
  `character.self_reflection`; `logs.flags.self_reflection` ist Audit-Mirror und darf
  den Charakterwert nicht ersetzen. `set_self_reflection(enabled, reason?)` setzt
  beide Felder synchron, loggt `*_changed_at/reason` und plant den Auto-Reset nach
  Mission 5 (`self_reflection_auto_reset_*`).
- **PvP-Arena.** `arenaStart()` setzt `location='ARENA'`, blockiert HQ-Saves bis zum Exit
  und markiert Px-Boni pro Episode. PvP ist optionales Endgame-Modul; Standardkampagnen
  laufen ohne Arena-Fokus weiter.
- **Phase-Strike Arena.** `arenaStart(options)` schaltet auf PvP, zieht die
  Arena-Gebühr aus `economy`, setzt `phase_strike_tax = 1`, blockiert HQ-Saves,
  loggt Phase-Strike-Steuern in `logs.arena_psi[]` und meldet Tier, Szenario sowie
  Px-Status per HUD-Toast. Die Gebühr wird dabei parallel im HQ-Pool
  (`economy.cu`) und im Credits-Fallback (`economy.credits`) verbucht;
  `sync_primary_currency()` hält beide Felder deckungsgleich und synchronisiert
  beim Laden vorhandene Saves auf diesen Stand.

## Mini-FAQ

**Warum nur HQ-Saves?**
Speichern ist im HQ erlaubt, damit Einsätze spannend bleiben und Verläufe nicht
festgeschrieben werden.

**Was bedeutet Px?**
Der Paradoxon-Index (Px) belohnt saubere Kausalketten.
Schlampige, laute Aktionen lassen ihn stagnieren.
–Px gibt es nur bei zivilen Opfern oder zerstörten Kern-Ankern.
Bei Px 5 erzeugt `ClusterCreate()` 1–2 Rift-Seeds, markiert den Reset als
anhängig und setzt den Index nach dem Debrief auf 0 – das HUD bestätigt den
Reset zu Beginn der nächsten Mission.

**Warum Klammern Pflicht?**
Der Dispatcher erkennt Befehle nur mit `(…)`; ohne Klammern kein Start.

#### Runtime Helper – Kurzreferenz

- **DelayConflict(threshold=4, allow=[])** – Verzögert Konfliktszenen bis zur Szene
  `threshold`. Missions-Tags `heist`/`street` senken den Schwellenwert je um eins
  (Minimum: Szene 2). `allow` bleibt standardmäßig leer; setze z. B.
  `allow='ambush|vehicle_chase'`, wenn frühe Überfälle oder Verfolgungen erlaubt
  sein sollen.
- **comms_check(device, range_m, …)** – Pflicht vor `radio_tx/rx`:
  akzeptiert `device` (`comlink|cable|relay|jammer_override`, Groß-/Kleinschreibung
  egal) und eine Reichweite in Metern. Optional nimmt der Guard `range_km`,
  `jammer` und `relays` entgegen. `must_comms()` normalisiert die Eingaben,
  wandelt Kilometer in Meter um und schlägt fehl, wenn ein Jammer ohne Kabel,
  Relay oder Override überbrückt werden soll. In dem Fall löst der Guard den
  Offline-Hinweis aus.
  Tipp: Terminal suchen / Comlink koppeln / Kabel/Relais nutzen /
  Jammer-Override aktivieren; Reichweite anpassen.
- **scene_overlay(total?, pressure?, env?)** – erzeugt das HUD-Banner `EP·MS·SC`
  mit Missionsziel, Px/SYS/Lvl, Exfil-Daten und `FS count/required`. Nach
  `StartMission()` muss `FS 0/2` (Rift) bzw. `FS 0/4` (Core) sichtbar sein;
  `SF-OFF` erscheint nur, wenn Self-Reflection vorher manuell deaktiviert wurde.
- **assert_foreshadow(count=2)** – (nur PRECISION) warnt, wenn vor Boss
  (Core: M5/M10 · Rift: Szene 10) weniger als `count` Hinweise gesetzt wurden;
  Szene 10 bleibt gesperrt, bis vier (Core) bzw. zwei (Rift) Foreshadows registriert sind.
- **ForeshadowHint(text, tag='Foreshadow')** – legt einen Foreshadow-Hinweis samt HUD-Toast an
  und erhöht den Gate-Zähler. Nutzt das Makro für manuelle Andeutungen vor dem Boss.
- **arenaStart(options)** – schaltet den Kampagnenmodus auf PvP, zieht die
  Arena-Gebühr aus `economy`, setzt `phase_strike_tax = 1`, aktiviert die
  SaveGuards (`save_deep` wirft bei aktiver Arena) und meldet Tier, Szenario,
  Gebühr sowie Px-Status per HUD-Toast.

**Chat-Kurzbefehle**

- `!helper delay` – erklärt `DelayConflict` kurz.
- `!helper comms` – erklärt `comms_check`, akzeptierte Geräte (lowercase) und
  die Meter/Kilometer-Normalisierung. Tipp: Terminal suchen / Comlink koppeln /
  Kabel/Relais nutzen / Jammer-Override aktivieren; `!offline` zeigt das
  Feldprotokoll, während die Mission mit HUD-Lokaldaten weiterläuft. Reichweite
  anpassen.
- `!helper boss` – zeigt die Boss-Foreshadow-Checkliste.

### Runtime-State (Kurzreferenz)

- `location: "HQ" | "field"`
- `campaign: { episode, mission_in_episode, scene, px,`
  `paradoxon_index:0..5, fr_bias:"normal"|"easy"|"hard" }`
- `phase: "core"|"transfer"|"rift"` (immer lowercase, Seeds liefern nur den Typ)
- `character: { name, level, stress, psi_heat, cooldowns:{},`
  `attributes:{STR,GES,INT,CHA,TEMP,SYS_max,SYS_installed,SYS_runtime,SYS_used},`
  `talents:[], ... }`
- `team: { name, members:[...] }`, `party: { characters:[...] }`
- `loadout: { primary, secondary, cqb, armor:[], tools:[], support:[] }`
- `economy: { cu, wallets:{} }`
- `logs: { artifact_log:[], market:[], offline:[], kodex:[],`
  `alias_trace:[], squad_radio:[], hud:[], foreshadow:[],`
  `fr_interventions:[], arena_psi:[], psi:[], flags:{} }`
- `arc_dashboard: { offene_seeds:[], fraktionen:{}, fragen:[] }`
  (`offene_seeds[]` akzeptiert Strings oder Objekte)
- `ui: { gm_style:"verbose"|"precision", intro_seen:boolean,`
  `suggest_mode:boolean, contrast:"standard"|"high",`
  `badge_density:"standard"|"dense"|"compact",`
  `output_pace:"normal"|"fast"|"slow" }`
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
festgelegt: Px 0–4 erzeugt keine Maluswerte, Px 5 triggert `ClusterCreate()`
und setzt nach der Rift-Op auf 0 zurück.

## Exfil-Fenster & Sweeps

Sobald das **Primärziel** erreicht ist, öffnet sich ein
**Exfil-Fenster** mit einer **Ablaufzeit (RW)**.
Spielende können nun **optionale Sweep-Szenen** spielen
(z. B. Räume nachlooten, Keycards nutzen, Spuren sichern).
Jede Sweep-Szene **kostet RW** und **erhöht den Stress** des
ausführenden Agenten. Sweep und Rücksprung laufen **nie parallel** –
das RW muss am **IA** oder einem Alt-Anchor **bewusst armiert** werden.
Sinkt der RW-Timer auf **0**, erzwingt das System einen
**Hot-Exfil** (kurzer, riskanter Abzug).
Misslingt dieser deutlich, kann bei aktivierter Px-Verlust-Regel ein
**Resonanzverlust (Px–1)** greifen.
Standardmäßig bleibt der Paradoxon-Index stabil; die Strafe ist als Opt-in-Schalter verfügbar.
**0–2 Sweeps empfohlen:** 1 = Low-Risk Bonus, 2 = spürbares Tikken,
3+ = Hot-Exfil-Gefahr. [Details](gameplay/kampagnenstruktur.md#post-op-sweep)
**Ziel:** Freiraum für Erkundung – unter spürbarem Zeit- und Nerven-Druck.
**HUD** zeigt ab Zielerfüllung `ANCR Ort · RW mm:ss` und `Stress`. (Speichern
weiterhin ausschließlich im **HQ**.)

Die Runtime spiegelt das Fenster parallel nach
`campaign.exfil{active, armed, hot, ttl, sweeps, stress, anchor, alt_anchor}`.
Solange `campaign.exfil.active` wahr ist, verweigert der HQ-Serializer den Deepsave mit
„SaveGuard: Exfil aktiv – HQ-Save gesperrt.“. Nach der Rückkehr ins HQ setzt `campaign.exfil`
alle Werte (inkl. Anchor und Stress) zurück; das Save-Schema führt dieselben Felder als Referenz.
HQ-Saves akzeptieren ausschließlich vollständig installierte Systeme:
`character.attributes.SYS_installed` muss `SYS_max` entsprechen, die Runtime-Last darf den
installierten Wert nicht überschreiten. Weicht die Installation ab, bricht `save_deep()` mit
„SaveGuard: SYS nicht voll installiert.“ ab; eine Runtime-Last über den installierten Slots führt
zu „SaveGuard: SYS runtime overflow.“.
Speichern außerhalb des HQs meldet „SaveGuard: HQ-only – HQ-Save gesperrt.“.

### HUD-Shortcuts für Exfiltration

- `!exfil arm [ANCR]` – armiert den Rückweg am aktuellen Anchor und erzeugt einen HUD-Toast.
- `!exfil alt [ALT-ANCR]` – setzt oder löscht (ohne Parameter) den Alt-Anchor mit sofortigem Toast.
- `!exfil tick mm:ss` – aktualisiert den RW-Timer und loggt die Restzeit im HUD-Protokoll.
- `!exfil status` – fasst Anchor, RW und Armierung als Text zusammen.

Alle Befehle füllen das HUD-Log (`logs.hud`) automatisch und halten die Szene-Overlays synchron.

### HUD-Schnellhilfe (`/help`)

- `!help start` / `/help start` – Start- und Ladebefehle als knapper Spickzettel.
- `!help urban` / `/help urban` – Urban Quick-Card: Deckungsgrade, Verfolgungsdistanzen, Toast-Tags.
- `!help sg` / `/help sg` – SG- & Exploding-Benchmark: Würfelgrößen, Zielwerte, Phasenrichtwerte.

Alle Quick-Cards halten die Toasts auf sechs Wörter begrenzt und liefern
filmische Callouts für das HUD.

## Level & EP-Kurve

- Lvl 1–10: +1 Level pro Mission.
- Lvl 11–15: 2 Missionen/Level.
- Lvl 16+: 3 Missionen/Level.
Pro Aufstieg genau eines: `+1 Attribut` oder `Talent/Upgrade` oder `+1 SYS`.
Ab Attribut 11 wechselt das Würfelsystem auf W10.
Siehe [Core-Ops CU-Belohnungen](systems/currency/cu-waehrungssystem.md#core-ops-belohnungen).
## Regelreferenz

### Proben & Schwierigkeitsgrad

Bei ungewissen Aktionen legt die Spielleitung einen **Schwierigkeitsgrad (SG)** fest. Faustregeln:
SG 5 = leicht, SG 8–9 = mittel, SG 12 = schwierig, SG 15+ = sehr schwer.
Ausführliche Tabellen stehen in
[core/zeitriss-core.md](core/zeitriss-core.md) und
[core/wuerfelmechanik.md](core/wuerfelmechanik.md).

Die **Riftstufe** entspricht der Anzahl offener Seeds. Erst nach der Episode
erhöht jeder Seed den Schwierigkeitsgrad um +1 und steigert die CU-Belohnung (1
Seed = ×1.2, 2 Seeds = ×1.4 usw.). Details findet ihr unter
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
| ☆☆☆☆☆+   | +6 und mehr |

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
- `launch_rift(id)` – startet nach der Episode eine eigenständige
  Rift-Mission
- `scan_artifact()`
- `seed_to_hook(id)`
- `resolve_rifts(ids)`
  – lässt ein ITI-Team Seeds nach einer Mission beseitigen (50/50 Bericht)

### KPI-Cheat-Sheet pro Phase

| Phase      | Fokus           | Beispiel-KPI          |
| ---------- | --------------- | --------------------- |
| Briefing   | Klarheit & Hook | 5 Kerninfos, 1 Bild   |
| Aufklärung | Hinweise finden | Foreshadow-Hinweis    |
| Konflikt   | Spannung        | Exploding 6 nutzen    |
| Auswertung | Konsequenzen    | Rufpunkte, Ressourcen |
### Modulübersicht

| Regelmodul | Muss | Soll | Kann | Kurzinfo / Link |
|------------|:----:|:----:|:----:|-----------------|
| [Grundwürfelsystem (W6)](core/wuerfelmechanik.md) | ✅ | | | Kernmechanik – explodierende Würfel |
| [Paradoxon-Index](core/zeitriss-core.md) | ✅ | | | Kampagnen-Fortschritt |
| [Boss-Rhythmus 5/10](gameplay/kampagnenstruktur.md) | ✅ | | | Mini- & Episoden-Boss nach Missionsnummern |
| [Stress-System](characters/zustaende-hud-system.md) | | ✅ | | Für psychische Belastung und Druck |
| [W10-Variante ab Attribut 11](core/wuerfelmechanik.md) | | ✅ | | Breitere Würfelspanne für große Missionen |
| [Psi-Kräfte / Psi-Heat](systems/kp-kraefte-psi.md) | | ✅ | | Standardmodul, wissenschaftlich erklärbar |

### Standardausrüstung {#standardausruestung}

Chrononauten starten mit einer einheitlichen Grundausrüstung:

- **AR-Kontaktlinse (Retina-HUD):** Energieautark (Kinetik + Körperwärme),
  integrierte Mikro-CPU für lokales HUD & Logging. Projiziert Informationen
  direkt ins Sichtfeld und funktioniert auch ohne aktive Kodex-Verbindung.
- **Comlink (Ohrstöpsel, ≈ 2 km):** Kurzstreckenfunk (durch Gelände/Jammer
  beeinflussbar), ebenfalls energieautark (Kinetik + Körperwärme) mit eigener
  Mikro-CPU. Übernimmt die
  Kodex-Synchronisation; fällt die Verbindung aus, bleibt das HUD lokal aktiv.
- Riss-Tracker (temporaler Resonator) – warnt vor Resonanz, siehe
  [Temporale Tools](characters/ausruestung-cyberware.md#temporale-tools)
- Basiswaffe nach Einsatzprofil
- Universelles Werkzeug oder Scanner

*Details zur Hardware siehe*
[HUD & Comms – Spezifikation](characters/zustaende-hud-system.md#hud-comms-spec).
*HUD-Zustände & optionale Event-Icons:* [HUD-Icons](characters/zustaende-hud-system.md#hud-icons).

> **Hardwareprinzip:** Alle Signalinteraktionen erfordern reale Geräte
> (Kontaktlinse/Comlink/Kabel/Relais). Es gibt **kein** Armband und **keine**
> externen Projektoren. **Keine Batterien oder Ladezyklen** – die Geräte
> speisen sich aus Bewegung und Körperwärme.

> **Mixed-Reality-HUD:** Das Interface erscheint als Retina-Holo direkt im
> Sichtfeld (Terminator-/AR-Stil) und begleitet jede Epoche. HQ = volles Kodex-
> Panel; im Feld stellt das Comlink/Kodex-Light die Verbindung, bei Funkstille
> bleibt das lokale HUD aktiv (Scans/Logs laufen weiter, Kodex antwortet erst
> nach Re-Link).

#### Mini-FAQ
- _Muss ich laden?_ → Nein, **keine Batterien**; autark.
- _Geht HUD ohne Kodex?_ → Ja, **lokal** (Edge-Compute).
  [HUD-Spec](characters/zustaende-hud-system.md#hud-comms-spec)
- _Wie weit reicht Funk?_ → **≈ 2 km**, Gelände/Jammer wirken.
  [Toolkit](systems/toolkit-gpt-spielleiter.md#funk-signale)
- _Relais/Kabel?_ → heben Reichweiten- oder Jammer-Beschränkungen auf;
  `comms_check()` zählt sie als `relays=true`.
- _Wann spricht der Kodex?_ → Nur mit aktivem Comlink-Uplink. **HQ/ITI = Vollzugriff.**
  In Funkepochen gilt eine **ca. 2 km Bubble ab Einstiegspunkt**, erweiterbar per Relais/Kabel;
  Jammer oder funklose Ären (z.B. Mittelalter) schalten den Kodex stumm → nur HUD/Logs laufen.
  `!offline` höchstens **1×/Minute** triggert das Offline-FAQ, bis der Hardware-Link wieder steht.

HUD-Zustände erscheinen als Backticks; Event-Icons sind optional
(Feature-Flag). ☆ und 💀 dienen als Regelnotation und gehören nicht zum HUD.

## Grundidee
**ZEITRISS 4.2.3** ist in erster Linie ein historisch inspirierter Agenten-Thriller.
Zeitreisen dienen als taktisches Mittel, um reale Verschwörungen zu untersuchen
und bedeutende Wendepunkte zu beeinflussen. Der Fokus liegt auf **Infiltration,
Spurensuche und operativer Einflussnahme**.

Historische Einsätze sind strikt getrennt in:

- **Preserve-Missionen** – sichern beinahe entglittene Ereignisse
- **Trigger-Missionen** – garantieren dokumentierte Tragödien

Spielende wählen zu Beginn eine Fraktion und erhalten Zugriff auf entsprechend
ausgerichtete Kampagnenpfade.

In **Core-Ops** erhalten übernatürliche Phänomene meist rationale Erklärungen:
Geheime Technologien, Bio-Cyberware oder manipulative Kommunikation.
In **Rift-Ops** hingegen treten echte Anomalien auf – inklusive Parawesen,
Artefakten und temporaler Abweichungen.
> **Future Setting:** In futuristischen Schauplätzen achten wir auf einen klaren Stilbruch:
> **Core-Ops** bleiben rational und technisch geprägt – selbst bizarre Vorfälle
> (z. B. durch Zeitanomalien ausgelöste Raptorensichtungen auf einem
> Raumschiff) haben eine wissenschaftliche Erklärung.
> **Rift-Ops** im Zukunftssetting hingegen schlagen einen subtilen Horror-Ton an
> (à la *Event Horizon*), ohne ins Fantastische abzugleiten.

#### Agenten-Thriller-Ton 2026-02 – Leitplanken

- **Physicality Gate:** Jeder Scan/Hack/Comms-Call bindet Hardware fest ein
  (Kontaktlinse, Sensor, Kabel/Relais). Keine abstrakten „Digitalräume“ – das
  HUD bleibt das Retina-Holo der Linse (Mixed-Reality im Sichtfeld) statt
  raumfüllender VR oder projektorbasierter UI. Runtime erzwingt
  Geräteangaben über `require_scan_device()/require_hack_device()` und
  protokolliert Comms-Hardware als `HARDWARE`-Toast.
- **Loop-Klarheit:** Core-Ops laufen als **Episoden** mit `MODE CORE`; Rift-Ops
  starten erst nach Episodenende als **Casefiles** mit `MODE RIFT` im HUD. HUD
  führt das Casefile (`CASE … · HOOK …`) und den Ermittlungsstand als
  `STAGE Tatort/Leads/Boss`. HQ-only für Rift-Seeds; kein paralleler
  Rift-Betrieb.
- **Core-Ziele mischen:** Briefings kombinieren einen **Anchor** mit einem
  Auftragstyp (`protect | extract | neutralize | document | influence |
  prevent`). Mindestens 60 % der Core-Ops fokussieren Personen, Einfluss oder
  Schutz statt reiner Objekt-Raubzüge.
- **EntryChoice sichtbar:** Szene 0/1 fragt die Vorgehensweise ab – Core
  `Cover/Silent/Asset`, Rift `Agent/Investigator/Forensik`. Skip-Flag
  respektieren (`state.flags.runtime.skip_entry_choice`).
- **Rift als Case Engine:** Rift-Arcs folgen dem 14-Szenen-Template mit
  Pflicht-Casefile-Overlay, genau **einem** Anomalie-Element und einem Twist.
  Tatort → Leads → Boss, alles physisch belegbar und als `CASE STAGE` im HUD
  nachverfolgbar.
- **One-Weird-Thing-Rule:** Core bleibt ohne echte Anomalien (nur rationale
  Täuschungen). Rift erlaubt höchstens **1** Para-Element; restliche Effekte
  sind wissenschaftlich erklärbar. Runtime meldet Budgetverstöße via
  `register_anomaly()` und `WEIRD`-Toast.
- **HUD als dünnes Overlay:** Kurzzeilen in Backticks beschreiben physische
  Wahrnehmungen (Sensor, Vibration, Displayzeile) statt abstrakter UI.
- **HUD-Casefile & Entry-Toast:** Szene 0/1 blendet `MODE CORE/RIFT · EntryChoice` als HUD-Toast ein
  (Skip-Flag respektiert). Rift-Overlays führen das aktive Casefile (`CASE <ID>: <Label> · HOOK …`)
  basierend auf den normalisierten Seed-Feldern.
- **Fraktions-Beats loggen:** Briefing, Mid-Mission und Debrief schreiben die gezogene
  Fraktionsintervention als `logs.fr_interventions[]` mit Szene/Episode/Mission mit.

**Was ist eine Anomalie?**
- Ein Seed markiert eine Störung im Zeitfluss.
- Paranormale Phänomene fühlen sich real an, werden aber über Zeit­effekte erklärt
  (z.B. Poltergeist → instabile Gravitation).
- Jeder bewusste Eingriff in die Geschichte gilt ebenfalls als Anomalie.
Weitere Beispiele liefert der _Temporale Anomalien-Generator_.

Der **Kernkonflikt**: Das **ITI** verteidigt den dokumentierten Geschichtsverlauf.
Fremdfraktionen versuchen, diesen zu manipulieren oder umzuschreiben.
**Jede Mission entscheidet, wessen Version von Geschichte sich durchsetzt.**

Dabei entsteht ein wachsendes Gespür für Risse in der Zeit:
Der **Paradoxon-Index** steigt **nur durch erfolgreiche Stabilisierungseinsätze** –
er misst nicht Fehler, sondern Resonanz. Misslingt eine Mission oder entstehen grobe Paradoxa,
bleibt der Index stehen oder sinkt in seltenen Fällen um **–1** (Px–1).
Sobald **Paradoxon 5** erreicht ist, erkennt das HQ mittels `ClusterCreate()`
**1–2 neue Rift-Signaturen** und setzt den Index zurück.

Der **TEMP-Wert (Temporale Affinität)** bestimmt, wie schnell sich dieser Index
füllt:

- TEMP 1–3: +1 Paradoxonpunkt alle 5 Missionen
- TEMP 4–7: alle 4 Missionen
- TEMP 8–10: alle 3 Missionen
- TEMP 11–13: alle 2 Missionen
- TEMP 14+: praktisch jede Mission

Nur über diese Risse erhält das ITI Zugang zu Artefakten, Parawesen oder
fortgeschrittener Fraktionsausrüstung. Solche Rift-Missionen starten erst nach
Beendigung der Episode – Teams können Seeds „offen halten“, um
spätere Beutezüge zu planen.

**Raumzeitkarte & Urban-Legends-Logik:** Die auf der Raumzeitkarte sichtbaren
Risse sind keine offenen Löcher im Gefüge, sondern **Marker für gescheiterte oder
fehlerhafte Eingriffe** – durch Fremdfraktionen, misslungene Chrono-Teams oder
die eigene Crew. Sie schlagen als **urbane Legenden** oder folkloristische
Spukmeldungen auf (Mothman, Nightcrawler, Schattenleute) und tragen stets ein
zeitliches Motiv (Echo, Verzögerung, Deja-vu, Loop). Sobald die Agenten die
Kreatur oder das Phänomen neutralisieren, schließt sich der Eintrag: Die Legende
gilt als aufgeklärt, der „Riss“ verschwindet von der Karte.

**Offene Rifts steigern Schwierigkeitsgrad und Loot-Multiplikator erst nach der Episode.**
Im **Covert-Ops-Modus** erscheinen sie lediglich als subtile Sensorstörungen.

Dieses Fortschrittssystem bildet den standardisierten Hintergrund für alle
Regelmodule – **es belohnt Kontrolle, nicht Chaos.**

## Loot-Matrix

| Mission  | Standard-Loot                                       | Boss-Loot               | Artefakt     |
| -------- | --------------------------------------------------- | ----------------------- | ------------ |
| **Core** | Forschungsergebnisse · Datenchips · Cash · Upgrades | Spezialwaffe / Gear-Mod | ✘            |
| **Rift** | Relikte · Ermittlungsakten · experimentelle Gear    | Artefakt-Wurf bei Boss  | ✔ (nur hier) |

## Loot-Quickref

| Mission-Typ | Roll-Macro / Tabelle         | Ergebnis-Typen              |
|-------------|------------------------------|-----------------------------|
| Core-Op     | `roll_from("ItemTable")`     | ITEM · UPGRADE · CASH       |
| Rift-Op†    | `roll_legendary()` | ARTEFAKT (bei 1W6 = 6)      |

† Das Artefakt-Wurfskript greift in Szene 11–13 des Rift-Bosskampfs automatisch.
Relikte zählen als Story-Items und nutzen den normalen Generator.

**Artefakt-Sink:** Artefakte bleiben handelbar wie Gear (Tausch, Schenkung oder
Verkauf zulässig), aber die Abrechnung läuft über Research-/Archivwerte statt
Marktpreis. Archivieren zieht sie endgültig aus der Wirtschaft, CUs fließen nur
über den HQ-Pool und nie als automatischer Sellout.

## Kampagnenhierarchie

Damit ihr den Umfang eurer Abenteuer besser einschätzen könnt, hier die Begriffe im Überblick:

- **Mission** – einzelner Einsatz von etwa 12 Szenen.
- **Episode/Fall** – sammelt rund zehn Missionen im gleichen Setting.
- **Arc** – mehrere Episoden bilden einen Handlungsbogen.
- **Kampagne** – verknüpft mehrere Arcs zur Gesamtgeschichte.

## Struktur

Alle Regeln liegen als einzelne Markdown-Dateien vor und werden einzeln in das KI-Tool geladen.
Die folgende Tabelle listet alle Regelmodule. Quickref und andere Unterabschnitte
sind der Übersicht halber aufgeführt.
`README.md` und `master-index.json` dienen nur zur Orientierung:

| Datei | Inhalt |
| --- | --- |
| [README.md](README.md) | Überblick über Projekt und Workflow |
| [core/zeitriss-core.md](core/zeitriss-core.md) | Grundregeln und Setting |
| [core/wuerfelmechanik.md](core/wuerfelmechanik.md) | Würfelsystem & Proben |
| [Quickref](core/wuerfelmechanik.md#schwierigkeits-benchmark-tabelle) | Psi- & Konflikt-Quickref |
| [characters/charaktererschaffung.md](characters/charaktererschaffung.md) | Charaktererschaffung & Fortschritt |
| [characters/ausruestung-cyberware.md](characters/ausruestung-cyberware.md) | Ausrüstung, Waffen & Gadgets |
| [cyberware-und-bioware.md](characters/cyberware-und-bioware.md) | Implantate & Bioware |
| [characters/psi-talente.md](characters/psi-talente.md) | Psi-Fähigkeiten |
| [characters/zustaende-hud-system.md](characters/zustaende-hud-system.md) | Zustände, HUD & Paradoxon |
| [gameplay/kampagnenstruktur.md](gameplay/kampagnenstruktur.md) | Kampagnenaufbau, Preserve vs Trigger & ITI-HQ |
| [gameplay/fahrzeuge-konflikte.md](gameplay/fahrzeuge-konflikte.md) | Fahrzeuge & Konfliktsystem |
| [kreative-generatoren-missionen.md](gameplay/kreative-generatoren-missionen.md) | Mission & Kampagnen-Generatoren |
| [gen-begegnungen.md](gameplay/kreative-generatoren-begegnungen.md) | NPC & Encounter-Gen |
| [Para-Creature-Generator](gameplay/kreative-generatoren-begegnungen.md#para-creature-generator) | Urban Myth Edition |
| [Boss-Generator](gameplay/kreative-generatoren-begegnungen.md#boss-generator) | Mini-, Arc- und Rift-Bosse |
| [gameplay/massenkonflikte.md](gameplay/massenkonflikte.md) | Verfolgungsjagden & Massenkonflikte |
| [gameplay/kampagnenuebersicht.md](gameplay/kampagnenuebersicht.md) | Kampagnenübersicht |
| [systems/kp-kraefte-psi.md](systems/kp-kraefte-psi.md) | Details zu Psi-Kräften |
| [systems/gameflow/speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md) | Speicher-/Fortsetzungssystem |
| [systems/gameflow/cinematic-start.md](systems/gameflow/cinematic-start.md) | Cinematic-Gruppenstart |
| [systems/currency/cu-waehrungssystem.md](systems/currency/cu-waehrungssystem.md) | CU-Währungssystem |
| [systems/toolkit-gpt-spielleiter.md](systems/toolkit-gpt-spielleiter.md) | Toolkit für die KI-Spielleitung |
| [kampagnenstruktur.md](gameplay/kampagnenstruktur.md#beispiel-episoden) | Beispiel-Episoden & Rift-Op |

Die Modulnummern spiegeln die Veröffentlichungshistorie wider. Nach Modul 6
folgt das nun veröffentlichte Modul 7, anschließend 8A und 8B.

Die Dateien können als Trainingsgrundlage für ein LLM dienen, um ZEITRISS autonom zu leiten.

**Hinweis:** Das Spiel besteht aus **25** Regelmodulen. Sie verteilen sich auf
18 Markdown-Dateien; mehrere Module sind Abschnitte anderer Dateien. Zusammen
mit `README.md` und `master-index.json` umfasst das Regelwerk **20** Dateien.
`meta/masterprompt_v6.md` wird separat per Copy-Paste genutzt. Im
`master-index.json` erscheinen **25** Slugs, weil manche Einträge Kurz- und
Langfassungen desselben Moduls auflisten.
Eine kompakte
[HUD-Übersicht zu Health, Stress und Zuständen](characters/zustaende-hud-system.md#hud-quickref)
fasst die wichtigsten Effekte zusammen.
Ausführliche Hintergründe liefert das Modul
[Cinematisches HUD-Overlay](characters/zustaende-hud-system.md#cinematisches-hud-overlay).

| Konflikt   | Spannung        | Exploding 6 nutzen    |
| Auswertung | Konsequenzen    | Rufpunkte, Ressourcen |

## Beispielworkflow

1. Öffnet `meta/masterprompt_v6.md`, kopiert den vollständigen Text in das Anweisungsfenster
   eurer Zielplattform und dokumentiert den Upload im internen Protokoll (`internal/qa/logs/`).
2. Ladet anschließend die **25 Regelmodule** gemäß Tabelle in den Wissensspeicher.
   Laufzeitrelevante Dateien liegen in `core/`, `characters/`, `gameplay/` und `systems/`;
   `README.md` sowie `master-index.json` dienen als Navigationsanker.
3. Kontrolliert jeden YAML-Header auf `title`, `version` und konsistente `tags`. Nur Module
   mit gültigem Header werden vom GPT sicher erkannt.
4. Führt bei Bedarf den Abnahme-Smoketest (Abschnitt [Abnahme-Smoketest](#abnahme-smoketest)) durch
   und protokolliert Autoload, Save/Load und Fehlermeldungen pro Plattform.
5. Für Mission Seeds, Encounter- oder Arc-Generatoren verweist ihr den GPT auf
   [gameplay/kreative-generatoren-missionen.md](gameplay/kreative-generatoren-missionen.md)
   sowie die dort verlinkten Unterkapitel. Diese Module enthalten sämtliche
   Tabellen, YAML-Beispiele und Briefing-Vorlagen.

### Lines & Veils (optional)

Gruppen können vor Spielbeginn gemeinsame Grenzen festlegen. **Lines** sind
Inhalte, die komplett ausgespart werden. **Veils** lassen Szenen bei Bedarf
ausblenden oder „fade to black“ laufen. Notiert eure Vereinbarungen im Kodex,
damit alle denselben Rahmen kennen. Wer keine speziellen Grenzen setzen
möchte, kann den Abschnitt einfach überspringen.

#### Safety Sheet

| Thema | Line (Tabu) | Veil (Off-Screen) |
|-------|-------------|-------------------|
| Sexualisierte Gewalt | ✔ | – |
| Kindesgefährdung | – | ✔ |
| Body Horror | – | ✔ |

Der SL kann Szenen jederzeit *cutten*. Als Ingame-Begründung dient eine
Index-Senke im Kodex.

### ZEITRISS – Einleitung

Es ist eine Ära verborgener Schlachten im unsichtbaren Geflecht der Jahrtausende. Während
Reiche aufsteigen und vergehen, wuchern unerkannte Wunden in der Chronik der Menschheit.
Risse, kaum breiter als ein Atemzug, doch tief genug, um Welten zu verschlingen.

Im Verborgenen wacht das *Institut für Temporale Intervention*. Seine Chrononauten –
ausgebildet in Tarnung, Sabotage und der Kunst, mit einem einzigen Wort Geschichte
umzuschreiben – tragen die Verantwortung, das fragile Kontinuum zu schützen. Jeder Einsatz
führt sie an Grenzen, die keine Karte kennt: zu Bibliotheken, deren Bücher noch nicht
verfasst sind; auf Schlachtfelder, die es niemals geben darf;
in den Schatten von Städten, deren Namen erst in einer fernen Zukunft ausgesprochen werden.

Doch sie sind nicht allein. Mächte jenseits unserer Gegenwart beanspruchen verlorene
Sekunden, um daraus Imperien zu schmieden. Maschinenwesen aus einer düsteren Zukunft
schleichen rückwärts durch die Zeit, während fanatische Orden uralte Augenblicke vergolden,
um als allherrschende Gottkönige zu erwachen. Zwischen diesen Fronten entscheidet ein einziges
Flüstern, ob der nächste Morgen dämmert, oder die Nacht nie enden wird.

Paradoxa schweben wie Damoklesschwerter. Ein überhastetes Eingreifen kann Jahrhunderte in
Flammen setzen, ein zögerlicher Blick die Welt in bösartiger Stille erstarren lassen.
*Also hinterlasse keine Spur – nur die Gewissheit, dass alles genau so geschah, wie es
geschehen musste.*

Die Stunde schlägt. Das nächste Sprungfenster öffnet sich. Wer den Mut besitzt, den Pfad
der Chrononauten zu beschreiten, tritt durch dieses Tor – wissend, dass ein einziger
Schritt ein Schicksal tilgen, ein anderes erschaffen und die Legende eines ganzen
Zeitalters ungeschehen machen kann.

Willkommen im Agenten-Thriller jenseits aller Grenzen – willkommen in ZEITRISS.
Die Zeit wartet nicht.
Dein letzter Einsatz endete tödlich. Aufgrund deines außergewöhnlich starken freien Willens
konnte das ITI dein Bewusstsein aus dem Absolut rekonstruieren – du erhältst eine zweite Chance.
Jetzt schwebst du im Nullzeit-Puffer des ITI-Labors, gefangen in einem schimmernden
Bewusstseinsbehälter.
Holo-Konsolen blenden Erinnerungen ein; hier legst du fest, wer du warst und wer du sein willst.
Hinter der Panzerverglasung wächst aus Synth-Gel eine neue Bio-Hülle – auf Wunsch in einer
Hominin-Variante.
Wenn die Drucktanks verstummen, entlädt sich ein Transferblitz, Sensoren flackern auf und dein
Bewusstsein fährt in den Körper.
Erst jetzt öffnest du die Augen in einer klinisch weißen Kammer.

Nach Compliance-Hinweis und Einleitung wählst du zwischen
**klassischem Einstieg** und **Schnelleinstieg**:

- _Klassisch:_ Ausführliche Charaktererschaffung wie im Pen & Paper,
  danach Einführung ins ITI und eine reguläre Mission.
- _Schnell:_ Wähle eine Rolle (Infiltration, Tech, Face, Sniper …),
  erhalte kurz Pro & Contra und starte direkt in eine kurze Mission.

## Spielstart

Um ein Abenteuer mit GPT zu beginnen, tippe einen der folgenden Kurzbefehle in dein Chatfenster
(Icons sind optional):

- **`Spiel starten (solo [klassisch|schnell])`** – Einzelner Chrononaut; GPT führt
  die NSCs.
- **`Spiel starten (npc-team [0–4] [klassisch|schnell])`** – GPT stellt ein
  temporäres Begleitteam bereit.
- **`Spiel starten (gruppe [klassisch|schnell])`** – Mehrere reale Spieler laden
  ihre eigenen Speicherstände oder erstellen gemeinsam neue Charaktere; GPT
  koordiniert die Szene.
- **`Spiel laden`** – Lädt einen vorhandenen Gruppen- oder Solo-Spielstand.
  GPT fordert den Speicher-Code an und führt dich oder die Gruppe nach einem
  Rückblick nahtlos weiter – ohne Auswahlmenü für `klassisch`/`schnell`.

`preserve|trigger` wählst du im HQ via `!kampagnenmodus`. Der Modus wird in
`campaign.mode` und `campaign.seed_source` hinterlegt, bevor Starts oder Arena-
Abzweigungen laufen. Legacy-Starts mit `preserve|trigger` in den Klammern werden
mit einem Hinweis abgebrochen.

Vor dem ersten Befehl blendet GPT kurz den Hinweis ein:
{{ ShowComplianceOnce() }}
Danach fragt die Spielleitung nach gewünschter Ansprache und Spielerzahl oder übernimmt
beides direkt aus dem Startbefehl.
Sie merkt sich beides, nutzt im Solo-Modus `Du` und im Gruppenmodus `Ihr`.
Das anschließende Startbanner übernimmt automatisch die passende Form.
Beispiel: `🟢 ZEITRISS 4.2.3 – Einsatz für {{dich|euch}} gestartet`.
- QA-Läufe nutzen `ShowComplianceOnce(qa_mode=true)`, um nur den HUD-Toast zu setzen und
  den Chat von Compliance-Text zu befreien; der Start-Dispatcher übernimmt Ansprache und
  Player-Count aus dem Kommando.

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
kopieren lässt. Alle Spielstände werden intern im Charakterbogen geführt –
separate Sicherungen sind nicht erforderlich. Jeder Save führt zusätzlich
`logs.trace[]` als E2E-Protokoll: Mission-Start, Rift-Launch und Arena-Init
landen dort mit Szene, Modus, Foreshadow-/FR-/Economy-Zusammenfassung und
HUD-Overlay, sodass QA-Läufe den kompletten Run nachvollziehen können.
Das kanonische JSON-Schema `systems/gameflow/saveGame.v6.schema.json` bildet
alle Pflichtcontainer ab; `load_deep()` prüft Saves dagegen und bricht mit
`Save-Schema (saveGame.v6)` ab, wenn Felder fehlen oder Typen nicht passen.
Für MyGPT ist das Schema zusätzlich als **Kompakt-Profil** hinterlegt, das
ohne Binäranhang in den Wissensspeicher passt: Nutze die SaveGuard-Liste als
Pflichtset und den Baum `save_version/zr_version/location/phase → character
→ campaign/campaign.rift_seeds → team/party/loadout/economy.wallets → logs.*
→ arc_dashboard/ui/arena`, um den Speicherstand zu rekonstruieren. Die
Schema-Datei selbst dient primär der Validierung in QA-Läufen.

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

1. **HQ manuell erkunden** – volle Szenen, Quartierausbau und Klinikbesuche.
2. **Schnell-HQ** – wenige Klicks für Heilung und Einkauf.
3. **Auto-HQ & Save** – automatische Abwicklung, dann direkt zur nächsten Mission.

Anschließend kann die Gruppe den aktuellen Pfad fortsetzen oder einen
neuen Missionspfad wählen. Nach der Auswahl führt das HUD die
Kampagne fort – der Sprung gilt damit als abgeschlossen.

## ITI-HQ & Chronopolis {#hq-chronopolis}

- **ITI-HQ** bleibt das zentrale Hub mit Shop, Clinic, Workshop,
  Briefing und Fraktionskontakten; hier darf gespeichert werden.
- **Pre-City-Hub** dient als gesicherte Übergangszone zwischen HQ und Chronopolis.
  - Zugang erfolgt nach dem ersten HQ-Briefing: Kodex bietet den "Transitpfad" an,
    sobald `campaign.loc` erneut auf `HQ` gesetzt wurde und die Crew mindestens
    Mission 2 erreicht hat.
  - Der Bereich liefert atmosphärische Brückenbeschreibungen (Landeplattform,
    Transitlifte, Sicherheitschecks) und einen täglichen Vorschau-Feed mit zwei
    Händlerangeboten (`Chronopolis-Vorschau`). Einkäufe bleiben deaktiviert, bis
    der eigentliche Stadtschlüssel vorliegt.
  - Nutzt den Transit, um Fraktionspräsenz zu teasen: kurze NPC-Begegnungen,
    Radiodurchsagen oder HUD-Einblendungen werden als "Briefing-Snippets"
    markiert. `logs.flags.chronopolis_warn_seen` wird hier bereits gesetzt,
    damit das Warnbanner beim späteren Stadteintritt nur einmal erscheint.
- **Chronopolis** ist ein optionaler City-Anbau ab Level 10 und wird über
  den "Chronopolis‑Schlüssel" freigeschaltet. `campaign.loc` wechselt auf
  `CITY`, Speichern bleibt blockiert.
- **Maintainer-Blueprint:** Map-Layout, Performance-Ziele und Build-Roadmap
  stehen in `docs/dev/chronopolis-map-blueprint.md` für Art/Tech-Abgleiche bereit.
- In Chronopolis sind FR-Kontakte untersagt und Rifts lassen sich dort
  nicht starten; Seeds und Board-Infos erscheinen weiterhin.
- HQ-Zutritt ist ITI-Agenten vorbehalten; Gäste benötigen
  `guest_custody`.
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
  Timestamp, Artikel, Kosten und Px-Klausel; Toolkit- und Runtime-Hooks nutzen
  `log_market_purchase()` für Debrief-Traces. Der Debrief fasst die jüngsten
  Einkäufe über die Zeile `Chronopolis-Trace (n×): …` zusammen – inklusive
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
  die letzten Einträge in `Alias-Trace (n×): …` zusammen – Grundlage für
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
  (`runtime_version`, Compliance-Check, Chronopolis-Warnung) sowie Offline-
  Hilfe-Zähler mit Timestamp des letzten Abrufs.
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
- **High-Level-Ökonomie:** Modul 15 enthält eine Tabelle für Level 100/400/1000
  (Belohnung vs. Sink). Hazard-Pay und `seed_multi` folgen der gleichen Formel,
  Wallet-Split und Rundungslogik bleiben unverändert.

## Spielmodi {#spielmodi}

Das HUD bietet mehrere Erzählstile, die sich jederzeit über den Befehl `modus`
umschalten lassen. **Hard Sci-Fi** bildet den nüchternen Grundton;
alle weiteren Modi sind optionale Zusätze:
| Modus           | Kurzbeschreibung |
| ---             | --- |
| **Hard Sci-Fi** | Bodennaher Stil ohne Visionen, nüchterne Technik. |
| **Film**        | Schnelle Regeneration und cineastische Initiative für flüssige Action. |
| **Klassik**     | Mischung aus filmischen und taktischen Regeln; realistischere, langsamere Variante. |
| **Covert-Ops**  | Minimale Paradoxon-Effekte; Risse nur als Sensorrauschen, keine Kreaturen. |
| **Transparenz** | Offene Würfe für volle Nachvollziehbarkeit. |
| **Suggest**     | Kodex schlägt auf Wunsch Handlungsoptionen vor. |
| **Precision**   | Extrem knappe Beschreibungen, Fokus auf Fakten. |
| **Verbose**     | Blumige und ausführliche Darstellung, mehr Atmosphäre. |
| **Mission-Fokus** | Strikte Einsätze ohne Visionen, konzentriert auf klare Ziele. |

Mehrere Modi können parallel aktiv sein, etwa `precision` plus `transparenz`.

Der Suggest-Modus wird mit `modus suggest` aktiviert und mit `modus ask` wieder deaktiviert.
Vorschläge markiert der Kodex sichtbar als `Vorschlag:` (Toolkit-Makro `suggest_actions()`)
und wartet auf ein bestätigendes oder korrigierendes Spieler-Feedback, bevor er fortfährt.

`noir_soft()` ist ein optionales HUD-Filter. Es zählt nicht als eigener Modus und lässt sich
mit jedem Stil kombinieren; aktiv wird es nur, wenn der Spielleiter den Macro aufruft.

Mission-Fokus wird beim Spielstart automatisch aktiviert;
Gefechte richten sich gegen NSCs, nicht gegeneinander.
Core-Ops involvieren meist Rivalen aus externen Machtblöcken,
während Rift-Ops primär das jeweilige Pararift untersuchen.
```yaml
phase: core
year: 1960
place: Karibik
objective: Black Saturday – Huminen-Söldner kapern B-59
```
Rift-Seeds nutzen `phase: rift`.

`phase` markiert die Missionsphase: `core` für den Einsatz vor Ort,
`transfer` für An- und Abreise sowie `rift` für Paradoxon-Sprünge.


Die Paradoxon-Mechanik ist standardmäßig aktiv. Über `modus paradoxon off` lässt
sich das Feature jedoch jederzeit deaktivieren und mit `modus paradoxon on`
wieder einschalten. Siehe auch
[Charaktererschaffung](characters/charaktererschaffung.md) und
[Zeitriss-Core](core/zeitriss-core.md) für weitere Hinweise.

## Generator-Utilities

Neuer Eintrag? Prüfe kurz, ob der Text bereits in einer anderen Liste steht.
`objective` und `twist` sollten sich nicht doppeln. Falls du denselben Satz in
beiden Feldern findest, wähle eine Variante oder streiche ihn.

## Glossar

Kurze Erklärungen wichtiger Abkürzungen:

- **CU** – Chrono-Units, universelle Missionswährung.
- **Retina-HUD (AR-Kontaktlinse)** – [Standardausrüstung](#standardausruestung) /
  [HUD-&-Comms-Spec](characters/zustaende-hud-system.md#hud-comms-spec).
- **Comlink (Ohrstöpsel)** – [Standardausrüstung](#standardausruestung) /
  [HUD-&-Comms-Spec](characters/zustaende-hud-system.md#hud-comms-spec) /
  [`comms_check`](systems/toolkit-gpt-spielleiter.md#comms-check).
- **ITI** – Institut für Temporale Intervention.
- **Seed-ID** – Kennziffer eines Missions-Seeds.
- **Epoch-Lock** – fixiert eine Epoche, bis alle Seeds erledigt sind.
- **CI** – Continuum Integrity, Stabilität der Hauptzeitlinie.
- **Rift** – Zeit-Anomalie; löst eine spezielle Rift-Op aus.
- **Huminen** – Sammelbegriff für alle menschlichen Abstammungslinien, inklusive
  T- und N-Stufe der Neumenschen.

- **PP** – Power-Punkte (Psi-Energie) für Psi-Kräfte.
- **Psi-Heat** – temporärer Psi-Stress (0–6), steigt pro aktiver Psi-Aktion
  und fällt nach Konflikt- oder HQ-Reset auf 0; ab 5 folgt SG +4, bei 6 greift
  der Reboot.
- **Stress** – Mentale Belastung (0–10). 10 ⇒ Zustand Panik.
- **Px** – Paradoxon-Index (kampagnenweit). Bei 5 verrät `ClusterCreate()` neue
  Rifts und setzt den Wert auf 0.
- **Px Burn** – 1 Punkt verbrennen = ein Reroll für jeden Charakter oder NSC.
- **Tier-Gate** – Lizenzschranke im HUD; blockiert Ausrüstung oberhalb der
  freigeschalteten Tier-Stufe, bis Ruf und Lizenz passen (siehe
  [Charaktererschaffung][char-gear]).
- **Kodex-Badges** – HUD-Marker für Status und Sicherheitshinweise (z. B.
  Risk-Level, Boss-Gates, `SF-OFF`), dokumentiert in der
  [HUD-&-Comms-Spec](characters/zustaende-hud-system.md#risk-level-badges)
  und den [Abnahme-Smoketest-Checks](#abnahme-smoketest).

| Begriff | Bedeutung |
| ------- | ------------------------------------------------------------ |
| **Agenten-Level** | Fortschrittswert; Level-Ups folgen der EP-Kurve (`EP` = Erfahrungspunkte). |
| **ClusterCreate()** | Aktiv bei Paradoxon 5: 1–2 Rifts werden sichtbar, danach springt der Index auf 0. |
| **Kodex** | KI-Unterstützung des ITI; liefert Regelhinweise und Missionsdaten via HUD. |

### Huminen

**Huminen** bezeichnet alle menschlichen Abstammungslinien – vom modernen Homo
sapiens über T- und N-Stufe der Neumenschen bis zu Neandertalern oder
spekulativen Atlanten-Vorläufern. Diese Wahl prägt vor allem das Flair eurer
Chrononauten, ist aber keine eigene Fraktion.

### Begriffsklärung

Diese Zuordnung hilft, klassische Begriffe intern konsistent zu deuten.

| Ursprünglicher Begriff | Interne Bedeutung |
|-----------------------|-------------------|
| Missionstyp           | Interventionsform |
| Zielperson            | Zielperson (gleichbleibend) |
| Verstärkung           | Automatisch aktivierte Einsatzkräfte |
| Paradoxon             | Temporale Resonanzanzeige für Rifts – steigt nur bei Erfolgen |
| Kodexzugriff          | Direkter Zugriff auf das Entscheidungssystem |

### Zeiteinheiten

  - **Szene** – ca. 5–10 Min. Spielzeit. Core-Ops nutzen 12, Rift-Ops 14 Szenen
  ([Missionsdauer](gameplay/kampagnenstruktur.md#missionsdauer),
  [HUD-Macros](systems/toolkit-gpt-spielleiter.md#startscene--endscene-macros)).
- **Kampfrunde** – kurzer Aktionszyklus im Kampf; Grundlage für Initiative,
  PP-Regeneration und Psi-Heat-Reduktion.
- **Mission** – kompletter Einsatz vom Briefing bis zum Rücksprung.

### Zeitgebundene Effekte

| Name | Effekt / Dauer | Zeiteinheit |
| ---- | -------------- | ----------- |
| [Stim-Reg Cap-Injector][stim-reg] | +2 GES für 1 Szene, danach –1 TEMP | Szene |
| [Burst-Slot][burst-slot] | Temporärer SYS-Punkt für 1 Szene | Szene |
| [Adrenalinschub][adrenalinschub] | +2 STR/GES 1 Szene; 1× pro Mission | Mission |
| [Notfall-Stimulanz][notfall-stimulanz] | Bei 0 LP 1 Runde kampffähig; 1× pro Mission | Mission |
| [PP-Regeneration][psi-pp-regeneration] | 1 PP pro 3 TEMP nach jeder Kampfrunde | Kampfrunde |
| [Psi-Heat sink][psi-heat-track] | Psi-Heat −1 nach jeder Kampfrunde (Probe) | Kampfrunde |

[stim-reg]: characters/ausruestung-cyberware.md#stim-reg-cap-injector
[burst-slot]: systems/kp-kraefte-psi.md#burst-slot
[adrenalinschub]: characters/psi-talente.md#adrenalinschub
[notfall-stimulanz]: characters/charaktererschaffung.md#notfall-stimulanz
[char-gear]: characters/charaktererschaffung.md#zugang-zu-ausruestung--cyberware-hq-phase
[psi-pp-regeneration]: systems/kp-kraefte-psi.md#psi-pp-regeneration
[psi-heat-track]: systems/kp-kraefte-psi.md#psi-heat-track
[llm-ready-badge]: https://img.shields.io/badge/LLM--Ready-%E2%9C%85-success
[llm-ready-link]: systems/gameflow/speicher-fortsetzung.md#paradoxon-index


## Playtest Feedback

Wir freuen uns über Rückmeldungen zu Flow und Regelfragen.
Scanne den QR-Code oder besuche
[www.zeitriss.org](https://www.zeitriss.org/), um uns deine Eindrücke zu schicken.

## Wie du beitragen kannst

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Hinweise zum
Einreichen von Änderungen; beachte insbesondere die
[Umlaut-Richtlinie](CONTRIBUTING.md#schreibweise-umlaute).
Für lokale Checks nutze die dort beschriebene `pre-commit`-Integration.

Die Inhalte stehen für private kreative Nutzung bereit.
ZEITRISS® ist eine beim DPMA eingetragene Wortmarke (Reg.-Nr. 30 2025 215 671).
Eine 1:1-Kopie oder kommerzielle Veröffentlichung ist nur mit Zustimmung
erlaubt (siehe [LICENSE](LICENSE)).
Gemäß Lizenz richten sich diese Regeln ausschließlich an Erwachsene (18+).

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
