---
title: "ZEITRISS-md Zeitreise RPG"
version: 4.2.2
tags: [meta]
---

# ZEITRISS®-md Zeitreise RPG

[![LLM-Ready ✅][llm-ready-badge]][llm-ready-link]

> **Kurzfassung:** ZEITRISS® schickt euch als operative Chrononauten in ein Tech-Noir-Zeitreise-RPG mit KI-Spielleitung, explodierenden Würfeln und JSON-Charakterbögen.
> **Markenhinweis:** ZEITRISS® ist eine eingetragene Marke von Florian Michler.
> **DPMA-Dossier:** Der vollständige Registerauszug liegt im [Markenbriefing](docs/trademark.md); haltet das Aktenzeichen 30 2025 215 671.9 bereit.

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
1. [Abnahme-Smoketest (Dispatcher)](#abnahme-smoketest)
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
1. [QA-Artefakte & Nachverfolgung](#qa-artefakte--nachverfolgung)
1. [Wie du beitragen kannst](#wie-du-beitragen-kannst)

<!-- Macro: StoreCompliance -->
{% macro StoreCompliance() -%}
Compliance-Hinweis: ZEITRISS ist ein Science-Fiction-Rollenspiel. Alle Ereignisse sind fiktiv.
{%- endmacro %}

## Überblick

**ZEITRISS-md** bietet ein schlankes Regelwerk im Zeitriss-Technoir-Stil.
Ihr spielt operative Chrononauten – Agenten des ITI – in taktisch optimierten Biohüllen.
Bereits zu Beginn entscheidet ihr euch für eine genetische Grundform:
Entweder Homo sapiens oder ein abgeleiteter Hominin-Typ wie Neandertaler, Denisova oder Atlanter-Vorläufer.
Diese Wahl prägt eure Physiologie, euer Sozialprofil und den Zugriff auf bestimmte Talente.
Eure Hülle ist keine Tarnung – sie ist euer Körper.
Ihr erkundet historische Epochen und beseitigt Anomalien.
Das System verwendet explodierende Würfel und protokolliert Zustände im JSON-Charakterbogen.
Texte und Illustrationen stehen unter [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/),
der Programmcode unter der [MIT-Lizenz](https://opensource.org/licenses/MIT).
Details findest du in [LICENSE](LICENSE).

## TL;DR – ZEITRISS in 6 Punkten

1. **Agents.** Chrononauten decken Zeitverschwörungen auf.
2. **Mission Phases.** Core-Ops verlaufen wie Episoden:
   Briefing → Infiltration → Intel/Konflikt → Exfiltration → Debrief –
   insgesamt zwölf Szenen. Rift-Ops sind eigenständige Filme in drei
   Akten mit vierzehn Szenen.
3. **Exploding Dice.** W6, ab Attribut 11 W10; Heldenwürfel erst ab 14.
4. **Paradoxon-Index (Px)** belohnt bewahrte Kausalketten.
   Schlampiges Vorgehen stagniert, destruktive Ausreißer senken Px.
   Bei Px 5 enthüllt `ClusterCreate()` 1–2 Rift-Seeds – spielbar nach Episodenende.
5. **Hard Sci-Fi.** Keine Magie, Psi kostet Power-Punkte.
6. **Boss-Rhythmus.** In Mission 5 einer Episode erscheint ein Mini-Boss, in Mission 10 der Episoden-Boss.
   Rift-Operationen platzieren ihren Boss in Szene 10. Das Toolkit löst
   `generate_boss()` an diesen Punkten automatisch aus.

Siehe den [Schnellstart-Spickzettel](#schnellstart-spickzettel) für eine kompakte Einstiegshilfe.

## Wissensspeicher & Plattform-Setup {#wissensspeicher--plattform-setup}

Die komplette Operator-Checkliste liegt in [docs/maintainer-ops.md](docs/maintainer-ops.md). Dort findet ihr die
Plattform-Workflows, QA-Notizen sowie die Rollenaufteilung zwischen Custom-GPT, Repo-Agent und Ingame-Kodex. Dieses README
listet nur die Laufzeitreferenz – bei Fragen zum Hochladen, Synchronisieren oder Testen führt euch das Maintainer-Dokument.

## Repo-Map {#repo-map}

```
ZEITRISS-md/
├─ README.md                # Laufzeit-Referenz & Plattform-Hinweise
├─ core/                    # Grundregeln & Zeitriss-Mechaniken (Runtime)
├─ characters/              # Charaktererschaffung, Ausrüstung, Zustände (Runtime)
├─ gameplay/                # Kampagnenstruktur, Generatoren, Missionsbau (Runtime)
├─ systems/                 # Gameflow, Währungen, Toolkit für die KI-Spielleitung (Runtime, ohne `runtime-stub-routing-layer.md`)
├─ meta/                    # Masterprompts, Hintergrundbriefe, Dev-only Inhalte
├─ docs/                    # Maintainer-Ops, Smoke-Tests, Starttranskripte (tags: [meta]; inkl. QA-Fahrplan & QA-Protokoll)
├─ scripts/, tools/         # Hilfsprogramme & Linter (Dev-only)
└─ master-index.json        # Übersicht aller Module und Slugs
```

### Dokumenten-Landkarte {#dokumenten-landkarte}

- **`README.md`** – Einstieg für alle Rollen. Führt Runtime-Referenzen, Kurzbefehle sowie die
  Dokumenten-Landkarte und verweist auf weiterführende Leitfäden.
- **`AGENTS.md`** – Arbeitsgrundlage für den Repo-Agenten (Programmier-KI). Verbindliche Stil-,
  Struktur- und Testpflichten inklusive Nutzung der gespiegelten Runtimes und Tools im Repo.
- **`CONTRIBUTING.md`** – Richtlinien für Beitragende. Beschreibt Workflow, Formatierung und
  Mindest-Checks; verweist auf QA- und Maintainer-Prozesse.
- **`docs/maintainer-ops.md`** – Operatives Handbuch für Plattformpflege und QA-Spiegelungen der
  Maintainer:innen.
- **`docs/qa/tester-playtest-briefing.md`** sowie QA-Logs unter `internal/qa/` – Briefing,
  Checklisten und Protokolle für Tester:innen und Maintainer:innen.
- **`meta/masterprompt_*.md`** – Laufzeit-Briefings für MyGPT. Werden im Repo aktiv gepflegt,
  dienen der Spielleitung als Grundlage und enthalten keine Dev-Vorgaben wie `AGENTS.md`.

## Schnellstart-Spickzettel {#schnellstart-spickzettel}
> **ZEITRISS**: Eine Elite‑Zelle des ITI springt durch die Jahrhunderte, um kritische Linienbrüche zu stoppen.
> Kein Schicksal, kein Mysterien‑Blabla – nur harte Einsätze, High‑Tech und Sekunden­entscheidungen.
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
7. **Self-Reflection Off** – `!sf off` setzt das globale Flag (`self_reflection: false`) für rein externe Handlung; `!sf on` stellt es zurück und das HUD zeigt `SF-OFF`, solange der Schutz aktiv ist.
8. **TK-Nahkampf-Cooldown** – `!tk melee` markiert telekinetische Nahkampfangriffe, blendet `TK🌀` im HUD ein und sperrt eine Runde; `!tk ready` hebt die Sperre nach dem Cooldown auf.
9. **Chrono-Units** – Belohnungen folgen dem CU-Multiplikator des Rifts.
   Formel: `Belohnung = Basiswert × (Szenenanzahl / 12)`.
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

- `Spiel starten (solo)` – Erschaffung → HQ-Intro → Briefing → Szene 1 · _schnell_: Rolle + Defaults → Briefing
- `Spiel starten (npc-team [0–4])` – PC bauen + Teamgröße · _schnell_: Rolle + Teamgröße
- `Spiel starten (gruppe)` – alle bauen · _schnell_: Saves posten oder Rolle nennen
- `Spiel laden` – Deepsave → Kodex-Recap → HQ/Briefing

**Klammern sind Pflicht.** Beispiel: `Spiel starten (solo)` wird erkannt; `Spiel starten solo` nicht.
**Rollen-Kurzformen erlaubt:** `infil`, `tech`, `face`, `cqb`, `psi`.

**Regeln:**

- **Nur-HQ-Save** – Speichern ist nur im HQ möglich; Missionszustände sind flüchtig.
- **Ausstieg in Mission** – Möglich, aber ohne Speichern. Gear darf übergeben werden. Nächster Save im HQ.
- **Paradoxon & Rifts** – Px 5 ⇒ `ClusterCreate()` (1–2 Rift-Seeds; spielbar nach Episodenende; danach Reset).
- **Semver-Toleranz** – Laden klappt, solange `major.minor` = `ZR_VERSION`; Patch wird ignoriert.

[Start-Transkripte ↗](internal/qa/transcripts/start-transcripts.md) ·
[Abnahme-Smoketest ↗](docs/qa/tester-playtest-briefing.md#acceptance-smoke-checkliste)

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

## Abnahme-Smoketest (Dispatcher) {#abnahme-smoketest}

### Dispatcher-Starts & Speicherpfade
1. `Spiel starten (solo klassisch)` → Erschaffung → HQ-Intro → Briefing → SC 1
2. `Spiel starten (solo schnell)` → Rolle → Defaults → Briefing/SC 1
3. `Spiel starten (npc-team 3 schnell)` → Autogen-NSCs (3) → Briefing
4. `Spiel starten (npc-team 5)` → Fehlermeldung „Teamgröße 0–4 …“
5. `Spiel starten (gruppe schnell)` → 2 Saves + 1 Rolle → Briefing
6. `Spiel starten (gruppe 3)` → Fehlermeldung „Bei *gruppe* keine Zahl …“
7. `Spiel laden` + kompatibler Save → **kein** klassisch/schnell; **Kodex-Recap-Overlay** → HQ/Briefing
8. `Speichern` während Mission → Blocker „Speichern nur im HQ …“
9. Gear-Alias: „Multi-Tool-Armband ausrüsten“ → still → „Multi-Tool-Handschuh“
10. „Px 5“ triggern → Hinweis: Seeds erzeugt, **spielbar nach Episodenende**, danach Reset

### Boss-Gates & HUD-Badges
11. `!helper boss` nach Mission 4 → Foreshadow-Liste zeigt Szene 5/10,
    HUD-Toast `Boss blockiert – Foreshadow 0/2` bis Hinweise erfüllt.
12. Mission 5 starten → HUD blendet Mini-Boss-DR (`Boss-Encounter in Szene 10`)
    und Badge `SF-OFF` ein; Foreshadow-Schritte zählen im HUD hoch.

### Psi-Heat & Ressourcen-Reset
13. Psi-Charakter in Konflikt schicken, Psi-Aktion nutzen → HUD meldet
    `Psi-Heat +1`; nach Konflikt springt Psi-Heat automatisch auf 0,
    HQ-Transfer setzt SYS/Stress/Psi-Heat zurück.


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
> Bei **TTL 0** folgt **Hot-Exfil**; scheitert der, droht **Px–1**.
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
6. **Regel-Transparenz** – Overlay und JSON-Log laufen standardmäßig; `/debug_rolls` blendet das Log bei Bedarf aus.

### Wahrscheinlichkeits-Übersicht {#wahrscheinlichkeits-uebersicht}

| SG | W6 expl. | W10 expl. | Δ (W10–W6) |
|---:|---------:|----------:|-----------:|
| 5  | 83 %     | 90 %      | +7 %       |
| 7  | 67 %     | 77 %      | +10 %      |
| 8  | 50 %     | 65 %      | +15 %      |
| 10 | 33 %     | 53 %      | +20 %      |

### Chat-Kurzbefehle {#chat-kurzbefehle}

Im Live-Chat kann nicht gescrollt werden. Diese Befehle rufen sofort Regeln ab:

### Start & Load – LLM-Dispatcher (ohne externe Runtime)

Siehe das [Mini-Einsatzhandbuch](#mini-einsatzhandbuch) für Startbefehle.

**Akzeptierte Zusätze:**
- Nach `solo`/`npc-team`/`gruppe` darf optional `klassisch` oder `schnell` folgen (auch `classic|fast`).
- `npc-team` akzeptiert nur Größen `0–4`; `gruppe` nimmt keine Zahl.
- Erlaubte Rollen-Kurzformen: `infil`, `tech`, `face`, `cqb`, `psi`.

**Fehlertexte:**
- `npc-team 5` → „Teamgröße erlaubt: 0–4. Bitte erneut eingeben (z. B. `npc-team 3`).“
- `gruppe 3` → „Bei *gruppe* keine Zahl angeben. (klassisch/schnell sind erlaubt)“

**Semver (Save-Laden):**
- Save lädt, wenn `major.minor` mit `ZR_VERSION` übereinstimmt; Patch-Level wird ignoriert.
- Mismatch → „Kodex-Archiv: Datensatz vX.Y nicht kompatibel mit vA.B. Bitte HQ-Migration veranlassen.“

**Quick-Hilfe:** `!help start` – listet alle vier Befehle mit Kurzbeschreibung.
Ein manuelles 10-Schritte-Smoke-Set steht im Abschnitt
[Acceptance-Smoke](docs/qa/tester-playtest-briefing.md#acceptance-smoke-checkliste).

- `!rules stealth` – zitiert die Passage zu Schleichen.
- `!gear cyberware` – zeigt Ausrüstung oder Implantate.
- `!save` – speichert einen Deepsave (nur im HQ).
- `!load` – lädt den letzten Deepsave.
- `!suspend` – legt einen flüchtigen Szenen-Snapshot für eine Pause an.
- `!resume` – setzt den letzten Suspend-Snapshot exakt einmal fort.
- `!autosave hq` – schaltet Auto-Save im HQ.

- `!gear shop` – zeigt Shop-Tier-Liste.
- `!psi heat` – erklärt Psi-Heat und Burn.

- `!hud status` – listet alle Zustände.
- `!reveal artifact` – zeigt Artefakt-Infos im HUD.
- `!regelcheck modul` – zwingt die KI, Regeln aus dem genannten Modul zu laden.
- `!regelreset` – setzt den Regelkontext nach Warnhinweis zurück und lädt alle Module neu.
- `modus verbose` – Filmisch an; Toast `GM_STYLE → verbose (persistiert)`.
- `modus precision` – Kurzprotokoll an (nur taktische Abschnitte); Toast `GM_STYLE → precision (persistiert)`.
- `!px` – zeigt aktuellen Paradoxon-Stand.
- `!fr help` – zeigt den aktuellen FR-Status.
- `!boss status` – listet Foreshadow-Zähler.

## Mini-FAQ

**Warum nur HQ-Saves?**
Speichern ist im HQ erlaubt, damit Einsätze spannend bleiben und Verläufe nicht festgeschrieben werden.

**Was bedeutet Px?**
Der Paradoxon-Index (Px) belohnt saubere Kausalketten.
Schlampige, laute Aktionen lassen ihn stagnieren.
–Px gibt es nur bei zivilen Opfern oder zerstörten Kern-Ankern.
Bei Px 5 erzeugt `ClusterCreate()` 1–2 Rift-Seeds, danach setzt der Zähler auf 0.

**Warum Klammern Pflicht?**
Der Dispatcher erkennt Befehle nur mit `(…)`; ohne Klammern kein Start.

#### Runtime Helper – Kurzreferenz

- **DelayConflict(threshold=4, allow=[])** – Verzögert Konfliktszenen bis zur Szene
  `threshold`. Missions-Tags `heist`/`street` senken den Schwellenwert je um eins
  (Minimum: Szene 2). `allow` kann frühe `ambush`/`vehicle_chase` freigeben.
- **comms_check(device, range)** – Pflicht vor `radio_tx/rx`: validiert Funkgerät,
  Leitung, Relais/Jammer-Override und Reichweite.
  Tipp: Terminal suchen / Comlink koppeln / Kabel/Relais nutzen / Jammer-Override aktivieren; Reichweite anpassen.
- **assert_foreshadow(count=2)** – (nur PRECISION) warnt, wenn vor Boss
  (Core: M5/M10 · Rift: Szene 10) weniger als `count` Hinweise gesetzt wurden;
  Szene 10 bleibt gesperrt, bis vier (Core) bzw. zwei (Rift) Foreshadows registriert sind.
- **ForeshadowHint(text, tag='Foreshadow')** – legt einen Foreshadow-Hinweis samt HUD-Toast an
  und erhöht den Gate-Zähler. Nutzt das Makro für manuelle Andeutungen vor dem Boss.

**Chat-Kurzbefehle**

- `!helper delay` – erklärt `DelayConflict` kurz.
- `!helper comms` – erklärt `comms_check` & Gerätevoraussetzungen.
  Tipp: Terminal suchen / Comlink koppeln / Kabel/Relais nutzen / Jammer-Override aktivieren; Reichweite anpassen.
- `!helper boss` – zeigt die Boss-Foreshadow-Checkliste.

### Runtime-State (Kurzreferenz)

- `location: "HQ" | "field"`
- `campaign: { episode, mission_in_episode, paradoxon_index:0..5, fr_bias:"normal"|"easy"|"hard" }`
- `character: { name, level, attributes:{STR,GES,INT,CHA,TEMP,SYS_max,SYS_used}, talents:[], ... }`
- `team: { name, members:[...] }`
- `loadout: { primary, secondary, cqb, armor:[], tools:[], support:[] }`
- `economy: { cu }`
- `logs: { missions:[], blacklab:[], hud:[] }`
- `ui: { gm_style:"verbose"|"precision" }`
- `exfil: { sweeps, stress, ttl_min, ttl_sec, active, armed, anchor, alt_anchor }`
- `fr_intervention: "ruhig"|"beobachter"|"aktiv"`
- `comms: { jammed:boolean, relays:number, rangeMod:number }`

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
Misslingt dieser deutlich, droht **Resonanzverlust (Px–1)**.
**0–2 Sweeps empfohlen:** 1 = Low-Risk Bonus, 2 = spürbares Tikken,
3+ = Hot-Exfil-Gefahr. [Details](gameplay/kampagnenstruktur.md#post-op-sweep)
**Ziel:** Freiraum für Erkundung – unter spürbarem Zeit- und Nerven-Druck.
**HUD** zeigt ab Zielerfüllung `ANCR Ort · RW mm:ss` und `Stress`. (Speichern weiterhin ausschließlich im **HQ**.)

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

Alle Quick-Cards halten die Toasts auf sechs Wörter begrenzt und liefern filmische Callouts für das HUD.

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
Makros siehe [speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md#makros-im-ueberblick), den Abschnitt zum
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
  beeinflussbar), ebenfalls energieautark (Kinetik + Körperwärme) mit eigener Mikro-CPU. Übernimmt die
  Kodex-Synchronisation; fällt die Verbindung aus, bleibt das HUD lokal aktiv.
- Riss-Tracker (temporaler Resonator) – warnt vor Resonanz, siehe
  [Temporale Tools](characters/ausruestung-cyberware.md#temporale-tools)
- Basiswaffe nach Einsatzprofil
- Universelles Werkzeug oder Scanner

*Details zur Hardware siehe* [HUD & Comms – Spezifikation](characters/zustaende-hud-system.md#hud-comms-spec).
*HUD-Zustände & optionale Event-Icons:* [HUD-Icons](characters/zustaende-hud-system.md#hud-icons).

> **Hardwareprinzip:** Alle Signalinteraktionen erfordern reale Geräte
> (Kontaktlinse/Comlink/Kabel/Relais). Es gibt **kein** Armband und **keine**
> externen Projektoren. **Keine Batterien oder Ladezyklen** – die Geräte
> speisen sich aus Bewegung und Körperwärme.

#### Mini-FAQ
- _Muss ich laden?_ → Nein, **keine Batterien**; autark.
- _Geht HUD ohne Kodex?_ → Ja, **lokal** (Edge-Compute). [HUD-Spec](characters/zustaende-hud-system.md#hud-comms-spec)
- _Wie weit reicht Funk?_ → **≈ 2 km**, Gelände/Jammer wirken.
  [Toolkit](systems/toolkit-gpt-spielleiter.md#funk-signale)
- _Relais/Kabel?_ → heben Reichweiten- oder Jammer-Beschränkungen auf; `comms_check()` zählt sie als `relays=true`.

HUD-Zustände erscheinen als Backticks; Event-Icons sind optional
(Feature-Flag). ☆ und 💀 dienen als Regelnotation und gehören nicht zum HUD.

## Grundidee
**ZEITRISS 4.2.2** ist in erster Linie ein historisch inspirierter Agenten-Thriller.
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
| [gameplay/massenkonflikte.md](gameplay/massenkonflikte.md) | Regeln für Massenkonflikte |
| [gameplay/kampagnenuebersicht.md](gameplay/kampagnenuebersicht.md) | Kampagnenübersicht |
| [systems/kp-kraefte-psi.md](systems/kp-kraefte-psi.md) | Details zu Psi-Kräften |
| [systems/gameflow/speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md) | Speicher-/Fortsetzungssystem |
| [systems/gameflow/cinematic-start.md](systems/gameflow/cinematic-start.md) | Cinematic-Gruppenstart |
| [systems/currency/cu-waehrungssystem.md](systems/currency/cu-waehrungssystem.md) | CU-Währungssystem |
| [systems/toolkit-gpt-spielleiter.md](systems/toolkit-gpt-spielleiter.md) | Toolkit für die KI-Spielleitung |
| [kampagnenstruktur.md](gameplay/kampagnenstruktur.md#beispiel-episoden) | Beispiel-Episoden & Rift-Op |

Die Modulnummern spiegeln die Veröffentlichungshistorie wider. Nach Modul 6 folgt das nun veröffentlichte Modul 7, anschließend 8A und 8B.

Die Dateien können als Trainingsgrundlage für ein LLM dienen, um ZEITRISS autonom zu leiten.

**Hinweis:** Das Spiel besteht aus **25** Regelmodulen. Sie verteilen sich auf 18 Markdown-Dateien;
mehrere Module sind Abschnitte anderer Dateien. Zusammen mit `README.md` und `master-index.json`
umfasst das Regelwerk **20** Dateien. `meta/masterprompt_v6.md` wird separat per Copy-Paste
genutzt. Im `master-index.json` erscheinen **25** Slugs, weil manche Einträge Kurz- und
Langfassungen desselben Moduls auflisten.
Eine kompakte [HUD-Übersicht zu Health, Stress und Zuständen](characters/zustaende-hud-system.md#hud-quickref)
fasst die wichtigsten Effekte zusammen.
Ausführliche Hintergründe liefert das Modul
[Cinematisches HUD-Overlay](characters/zustaende-hud-system.md#cinematisches-hud-overlay).

| Konflikt   | Spannung        | Exploding 6 nutzen    |
| Auswertung | Konsequenzen    | Rufpunkte, Ressourcen |

## Beispielworkflow

1. Öffnet `meta/masterprompt_v6.md`, kopiert den vollständigen Text in das Anweisungsfenster eurer Zielplattform und sichert den
   Upload im QA-Log.
2. Ladet anschließend die **25 Regelmodule** gemäß Tabelle in den Wissensspeicher. Laufzeitrelevante Dateien liegen in
   `core/`, `characters/`, `gameplay/` und `systems/`; `README.md` sowie `master-index.json` dienen als Navigationsanker.
3. Kontrolliert jeden YAML-Header auf `title`, `version` und konsistente `tags`. Nur Module mit gültigem Header werden vom GPT
   sicher erkannt.
4. Führt den Abnahme-Smoketest (Abschnitt [Abnahme-Smoketest](#abnahme-smoketest)) durch und protokolliert Autoload,
   Save/Load und Fehlermeldungen pro Plattform.
5. Für Mission Seeds, Encounter- oder Arc-Generatoren verweist ihr den GPT auf
   [gameplay/kreative-generatoren-missionen.md](gameplay/kreative-generatoren-missionen.md) sowie die dort verlinkten
   Unterkapitel. Diese Module enthalten sämtliche Tabellen, YAML-Beispiele und Briefing-Vorlagen.

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

- **`Spiel starten (solo)`** – Einzelner Chrononaut; GPT führt die NSCs.
- **`Spiel starten (npc-team)`** – GPT stellt ein temporäres Begleitteam bereit.
- **`Spiel starten (gruppe)`** – Mehrere reale Spieler laden ihre eigenen Speicherstände
  oder erstellen gemeinsam neue Charaktere; GPT koordiniert die Szene.
- **`Spiel laden`** – Lädt einen vorhandenen Gruppen- oder Solo-Spielstand.
  GPT fordert den Speicher-Code an und führt dich oder die Gruppe nach einem
  Rückblick nahtlos weiter.

Vor dem ersten Befehl blendet GPT kurz den Hinweis ein:
{{ StoreCompliance() }}
Danach fragt die Spielleitung nach gewünschter Ansprache und Spielerzahl.
Sie merkt sich beides, nutzt im Solo-Modus `Du` und im Gruppenmodus `Ihr`.
Das anschließende Startbanner übernimmt automatisch die passende Form.
Beispiel: `🟢 ZEITRISS 4.2.2 – Einsatz für {{dich|euch}} gestartet`.

- `Spiel starten (...)` → Charaktererschaffung → HQ-Phase → Mission
  ([Cinematic Start](systems/gameflow/cinematic-start.md)).
- `Spiel laden` → Save einlesen → Rückblick → Mission fortsetzen
  ([speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md)).

Wird `Spiel laden` ohne JSON-Block eingegeben, fordert GPT den Spielstand an
und setzt nicht aus dem Nichts fort.

Details zum Speichersystem findest du in [speicher-fortsetzung.md](systems/gameflow/speicher-fortsetzung.md).

Der Befehl `Speichern` erzeugt immer einen vollständigen **Deep Save** als
JSON-Block, der alle Fortschrittsdaten enthält. Tippe `Film ab!`, um eine
optionale Film-Zusammenfassung zu erhalten, die sich für Video-Generatoren
kopieren lässt. Alle Spielstände werden intern im Charakterbogen geführt –
separate Sicherungen sind nicht erforderlich.

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
- **Chronopolis** ist ein optionaler City-Anbau ab Level 10 und wird über
  den "Chronopolis‑Schlüssel" freigeschaltet. `campaign.loc` wechselt auf
  `CITY`, Speichern bleibt blockiert.
- In Chronopolis sind FR-Kontakte untersagt und Rifts lassen sich dort
  nicht starten; Seeds und Board-Infos erscheinen weiterhin.
- HQ-Zutritt ist ITI-Agenten vorbehalten; Gäste benötigen
  `guest_custody`.
- Chronopolis-Services sind Wrapper um die HQ-Module mit eigenen
  Preisfaktoren.
- Das Tagesangebot folgt einem Daily-Roll: `!chrono stock` zeigt Rang- und Research-gated Slots, `!chrono tick` steuert den Missionsrhythmus der Rotation.

## Spielmodi {#spielmodi}

Das HUD bietet mehrere Erzählstile, die sich jederzeit über den Befehl `modus`
umschalten lassen. **Hard Sci-Fi** bildet den nüchternen Grundton;
alle weiteren Modi sind optionale Zusätze:
| Modus           | Kurzbeschreibung |

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

`noir_soft()` ist ein optionales HUD-Filter. Es zählt nicht als eigener Modus und lässt sich
mit jedem Stil kombinieren; aktiv wird es nur, wenn der Spielleiter den Macro aufruft.

Mission-Fokus wird beim Spielstart automatisch aktiviert;
Gefechte richten sich gegen NSCs, nicht gegeneinander.
Core-Ops involvieren meist Rivalen aus externen Machtblöcken,
während Rift-Ops primär das jeweilige Pararift untersuchen.
```yaml
phase: Core
year: 1960
place: Karibik
objective: Black Saturday – Huminen-Söldner kapern B-59
```
Rift-Seeds nutzen `phase: Rift`.

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
  [Charaktererschaffung](characters/charaktererschaffung.md#zugang-zu-ausruestung--cyberware-hq-phase)).
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
[psi-pp-regeneration]: systems/kp-kraefte-psi.md#psi-pp-regeneration
[psi-heat-track]: systems/kp-kraefte-psi.md#psi-heat-track
[llm-ready-badge]: https://img.shields.io/badge/LLM--Ready-%E2%9C%85-success
[llm-ready-link]: systems/gameflow/speicher-fortsetzung.md#paradoxon-index


## Playtest Feedback

Wir freuen uns über Rückmeldungen zu Flow und Regelfragen.
Scanne den QR-Code oder besuche
[www.zeitriss.org](https://www.zeitriss.org/), um uns deine Eindrücke zu schicken.

## QA-Artefakte & Nachverfolgung {#qa-artefakte--nachverfolgung}

- [QA-Fahrplan 2025](internal/qa/plans/ZEITRISS-qa-fahrplan-2025.md) – priorisierte Maßnahmenliste mit Status-Tracking und Verweisen auf Commits.
- [QA-Audit 2025](internal/qa/audits/ZEITRISS-qa-audit-2025.md) – Zusammenfassung der Testläufe inklusive Bewertungsmatrix.
- [Beta-QA-Log 2025](internal/qa/logs/2025-beta-qa-log.md) – vollständige Copy-&-Paste-Protokolle aus Beta-GPT/MyGPT inklusive Nachverfolgung.
- [Maintainer-Ops](docs/maintainer-ops.md) – Plattform- und Upload-Checklisten, inklusive QA-spezifischer Routinen.

Verknüpfe jede QA-Maßnahme in PR-Beschreibungen mit dem passenden Log-Abschnitt und aktualisiere Audit wie Fahrplan nach dem Merge.
Aktuelle QA-Läufe finden ausschließlich im OpenAI-MyGPT-Beta statt.
Der Standardprompt aus `docs/qa/tester-playtest-briefing.md` lässt den GPT den gesamten QA-Lauf autonom
simulieren und liefert strukturierte `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und `Nächste Schritte`-
Blöcke für Codex.
Store-GPT, Proton LUMO und lokale Instanzen spiegeln erst nach erfolgreicher MyGPT-Abnahme denselben Stand ohne zusätzliche Plattformoptimierung.

## Wie du beitragen kannst

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Hinweise zum
Einreichen von Änderungen; beachte insbesondere die
[Umlaut-Richtlinie](CONTRIBUTING.md#schreibweise-umlaute).
Für lokale Checks nutze die dort beschriebene `pre-commit`-Integration.

Die Inhalte stehen für private kreative Nutzung bereit.
ZEITRISS® ist eine beim DPMA eingetragene Wortmarke (Reg.-Nr. 30 2025 215 671).
Eine 1:1-Kopie oder kommerzielle Veröffentlichung ist nur mit Zustimmung erlaubt (siehe [LICENSE](LICENSE)).
Gemäß Lizenz richten sich diese Regeln ausschließlich an Erwachsene (18+).

© 2025 pchospital – ZEITRISS® – private use only. See LICENSE.
