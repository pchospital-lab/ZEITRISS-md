---
title: "ZEITRISS — Testing-Guide (Persona-Playtest)"
version: 1.2.0
tags: [meta]
---

# ZEITRISS — Testing-Guide

> **Zielgruppe:** KI-Agenten, die an ZEITRISS arbeiten und automatisierte
> Playtest-Runs starten, auswerten oder Regressionen finden. Für
> menschliche Tester bleibt [docs/qa/tester-playtest-briefing.md](qa/tester-playtest-briefing.md)
> das primäre Briefing.

## Worum es hier geht

Dieses Repo hat **zwei komplementäre Test-Workflows**:

| Workflow                               | Zielgruppe          | Doku                                                                  |
| -------------------------------------- | ------------------- | --------------------------------------------------------------------- |
| Menschlicher Tester spielt manuell     | Flo, externe Tester | [docs/qa/tester-playtest-briefing.md](qa/tester-playtest-briefing.md) |
| Persona-Sub-Agent spielt automatisiert | Repo-Agenten        | Diese Datei.                                                          |

**Scope-Hinweis (wichtig für externe Contributor:innen):** Dieser Guide
dokumentiert den **agent-internen Automatisierungs-Workflow**. Die
Harness-Scripts, die einen Persona-Sub-Agent gegen das SL-Preset spielen
lassen, liegen seit 2026-06-18 unter `internal/qa/harness/` **in diesem
Repo** (zuvor nur im privaten Agent-Workspace). Die Run-Artefakte dieser
Läufe liegen unter `internal/qa/evidence/2026-playtests/`.
Externe Tester:innen, die manuell gegen ZEITRISS spielen, finden im
[Tester-Briefing](qa/tester-playtest-briefing.md) alles Nötige — dieser
Guide hier ist für dich nur als Referenz interessant (welche Regeln
werden geprüft, welche Stolperfallen es gab).

Für automatisierte Runs durch einen Repo-Agenten beschreibt dieser Guide
ZEITRISS-spezifisch die konkreten Checks: Preset-Konsistenz, Regressions-
Matrix, Preflight-Regeln, Cross-Findings-Mechanik.

---

## ZEITRISS-Spezifika

### Preset + KB

- **Preset:** `zeitriss-v426-uncut` in OpenWebUI (läuft über LiteLLM-Proxy
  mit Prompt-Cache). `base_model: zeitriss-sonnet` (LiteLLM-Modell-Alias auf
  `127.0.0.1:4000` → OpenRouter → Anthropic Sonnet 4.6).
- **KB-ID wechselt bei jedem Rebuild** — aktuelle ID steht im Harness-Header
  (`KB_ID`-Konstante). Live-ID am Preset holen:
  `curl -s "$OPENWEBUI_URL/api/models" -H "Authorization: Bearer $OPENWEBUI_API_KEY" | jq -r '.data[]|select(.id=="zeitriss-v426-uncut").info.meta.knowledge[].id'`.
  Bei Mismatch: Harness-`KB_ID` nachziehen, nicht starten.
  **0.11.x-Quirk:** `knowledge.files` / `data.file_ids` sind über die API leer,
  obwohl die KB gefüllt ist — nicht als „leere KB" fehldeuten. Ground-Truth ist
  die File↔Collection-Verknüpfung (`file.meta.collection_name`) bzw. die
  Vektor-Collection (ChromaDB, Dimension 384 = MiniLM). Stand 2026-09-14:
  KB `9ad88aff` = 19 Files / 1313 Embeddings / 384-dim.
- **Masterprompt-MD5** gegen Repo-Version prüfen (`meta/masterprompt_v6.md`),
  nie gegen eine Preset-Kopie vertrauen.

### Harness-Location

Seit 2026-06-18 liegen die Harnesses **im Repo** unter `internal/qa/harness/`:

```text
internal/qa/harness/
├── *.py                  # coreops_split_merge.py, group-harness.py,
│                         # solo_journey.py, split_merge.py, merge_assert.py,
│                         # episode1-mini.py, w10-schwelle-probe.py u.a.
├── persona-driven/       # persona-player.py + personas.yaml (Zwei-KI-Setup)
├── personas/             # noob.md, end-tier-vet.md
├── scenarios/            # Placeholder (aktuell inline in PHASES-Dicts)
├── fixtures/             # save-lvl950-marek.json, save-group-initial.json,
│                         # save-after-hq.json
├── owui-patches/         # OpenWebUI-Hotfixes (socket-main-chatid-none)
└── zeitriss-sysprompt.txt  # eingefrorene MP-Kopie v4.2.6 (Harness-Input,
                            # NICHT SSOT — SSOT ist meta/masterprompt_v6.md)
```

Run-Artefakte (Berichte + rohe Transkripte) liegen unter
`internal/qa/evidence/2026-playtests/<YYYY-MM-DD-kurzname>/`.

Aufruf-Pattern:

```bash
source ~/.openwebui_env
cd <repo>/internal/qa/harness
python3 group-harness.py --phase 2       # Gruppen-Canary
python3 coreops_split_merge.py           # Core-Ops Split/Merge
python3 episode1-mini.py                 # Solo-Smoke
```

**Harness-Übersicht:**

| Script                  | Zweck                                 | Dauer (ca.) | Env erforderlich                     |
| ----------------------- | ------------------------------------- | ----------- | ------------------------------------ |
| `group-harness.py`      | Gruppen-Canary (3 Personas gegen SL)  | ~15 Min     | `OPENWEBUI_URL`, `OPENWEBUI_API_KEY` |
| `coreops-harness.py`    | Regel-Mechanik-Deep-Dive + PSI-Track  | ~25 Min     | dito                                 |
| `episode1-mini.py`      | Solo-Smoke (Noob-Persona)             | ~10 Min     | dito (Hinweis: Port 3000 hardcoded)  |
| `w10-schwelle-probe.py` | W10-Schwellen-Regel-Regression        | ~5 Min      | dito (Hinweis: Port 3000 hardcoded)  |

*Port-Hinweis: `episode1-mini.py` nutzt `OPENWEBUI_URL` (Default 8080),
`w10-schwelle-probe.py` wurde 2026-09-14 von hardcoded Port 3000 auf 8080
gezogen. Der frühere Port-3000-Drift (Migration 0.9.1) ist damit erledigt.*

**Begriffe im Guide:**

- **Smoke** — kurzer (< 60 s) CI-Test, `bash scripts/smoke.sh`
- **Canary** — kurzer Sanity-Playtest-Run, oft als Ph.1 vor dem vollen Run
- **Befund** — QA-Erkenntnis, als `docs/qa/playtest-befund-*.md` ins Repo
- **Verifikation** — Regel-/Schema-Bestätigung, als `docs/qa/<thema>-verifikation.md`
- **Regression** — gegenüber vorheriger Run-Matrix verändertes Verhalten
  (typischerweise P0-Kandidat)

### Personas

Zwei zentrale Profile unter `personas/`, weitere inline in den Harnesses
(Sarah/SPLINTER, Jonas/ANVIL, Kim/GHOST, Mara/VOSS im `group-harness.py`).

**ZEITRISS-Persona-Eigenheiten:**

- Personas sind **Spieler-Charaktere mit Attributen + Ausrüstung + Callsign**,
  nicht nur Nutzer-Archetypen
- Jede Persona kennt die Würfelformel (`1W6 + ⌊Attr/2⌋ + Talent + Gear`) in
  ihrer Stufe und nutzt sie turn-intern
- Gruppen-Runs haben **geteiltes SL-Kontext** — alle Personas sehen dieselbe
  Szene, antworten in abgestimmter Reihenfolge
- Level-Stufen-Persona: Noob (Lvl 1, kennt nur Basics) vs. End-Tier-Vet (Lvl
  800–1000, High-Save-Load, Endgame-Mechanik)

### Regressions-Matrix (ZEITRISS-spezifisch)

Jeder Run muss mindestens die folgenden Punkte **explizit** prüfen:

- **v7-Save-Schema:** `v: 7`, `characters[]`, `attr{}`, `reputation{}`,
  `characters[].wallet` (kein `economy`-Geldfeld), `level_history[]`, `last_seen.mode:"hq"`
- **Würfel-Mechanik:** `⌊Attribut/2⌋`-Formel (nicht `/2` ohne floor!),
  Exploding 6 bei W6, Exploding 10 bei W10, Burst-Cap 1
- **HUD-Disziplin:** HUD nur bei Gate-Triggern (LP/Stress/PP/SYS-Änderung,
  Phasenwechsel, Schwellenmeldung) — nicht pro Turn
- **Chargen-Save-Gate:** Erst-Save **muss** `mode:"hq"` haben, nicht `"char-gen"`
- **Mira-vor-Renier:** Erstkontakt beim HQ-Preamble ist Mira, nicht Renier

Bei jeder neuen MP- oder Schema-Änderung die Matrix erweitern, nicht nur
nachträgliche Checks in `_summary.md` ergänzen.

### Erweiterter Testflow P1/P2 (Stand 2026-04-30)

Nach Abschluss der P0-Tasks wird die Playtest-Matrix um vier Pflichtblöcke
erweitert. Reihenfolge ist verbindlich: erst P1 vollständig, danach P2.

#### P1-1: 5er Split/Merge-Matrix

Pflichtfälle:

- **4/1-Split im HQ** (kanonischer Split mit `continuity.split.family_id`)
- **3/2-Split mit Rejoin**
- **Resplit** (z. B. `3 -> 2/1`)
- **Konfliktfall / non-canonical Import**

Mindest-Checks je Fall:

- `family_id`, `thread_id`, `expected_threads`, `resolved_threads`,
  `convergence_ready`
- deterministische Merge-Ergebnisse (`characters[]`, `characters[].wallet`
  (Wallets reisen mit, kein Pool-Merge), `campaign.px`/`px_state`)
- Konfliktprotokoll in `logs.flags.continuity_conflicts[]` bzw.
  `merge_conflicts`
- Trace-Nachweise `team_split`/`team_merge`

#### P1-2: Seed-Cap & Overflow-Nachweis

Pflichtfälle:

- `8 + 7` offene Seeds (Overflow erwartet)
- `12` offene Seeds (kein Overflow)
- `11 + 1` offene Seeds (kein Overflow)
- `10 + 3` offene Seeds (Overflow erwartet)

Mindest-Checks:

- Merge-Ergebnis hält max. **12 offene Seeds**
- Trace-Event `rift_seed_merge_cap_applied` mit `kept[]`/`overflow[]`
- `merge_conflicts` enthält `rift_merge`
- Handoff-Nachweis (`handoff_to`, Auswahlregel) + Debrief-Hinweis im
  Inworld-Text

#### P1-3: Arena-/Rift-Transferhygiene (Negativtests)

Pflichtfälle:

- PvP-Run -> HQ-Save
- Import eines Arena-aktiven Saves
- Rift-Transfer zurück HQ
- Mixed-Import (Rift + PvP + Chronopolis ohne gemeinsames Split-Protokoll)

Mindest-Checks:

- Keine persistenten Arena-Runtime-Reste (`resume_token`, aktive Queue/Match-
  States)
- `campaign.mode` bleibt Persistenzstrategie (`mixed|preserve|trigger`)
- Runtime läuft über `runtime_phase` und wird HQ-safe normalisiert
- Branch-lokale Daten werden nur über den definierten Importpfad übernommen

#### P2-1: Chronopolis-Qualitätspass

Pflichtfälle:

- Reaktions-Beat nach signifikanter Aktion
- Exit-Druck bei großem Gewinn
- sauberer Exit Richtung HQ
- Negativfälle (Stuck, fehlende Optionen, Persistenzdrift)
- Cross-Mode-Flow: `Core -> Arena -> Rift -> Chronopolis -> Save/Load`

Mindest-Checks:

- Beat-Loop bleibt konsistent (kein stummer Dead-End)
- Persistenzvertrag eingehalten (keine Runtime-Felder als Save-Quelle)
- Logs/Trace dokumentieren Unlock- und Rückkehrpfade nachvollziehbar

#### Artefaktpflicht pro Testfall

Für jeden Fall im Run-Artefakt dokumentieren:

- Testfall-ID (z. B. `P1-1-T03`)
- Setup/Inputs (inkl. Session-Anker)
- Erwartung vs. Ist-Ergebnis
- Status (`PASS`/`FAIL`/`SOFT-FAIL`)
- Evidenz (Trace-Auszug, Save-Diff, betroffene Felder)

Diese Verdichtung ist der Standard für die spätere Repo-Übernahme in
`docs/qa/*` und für die Fortschreibung des Abarbeitungs-Reports.


### Pflicht-Gate: Datensatz-vs-Dev-Trennlinie (ab 2026-05-06)

Jeder neue QA-Befund (Playtest, Verifikation, Regression) muss **vor** der
fachlichen Bewertung einen kurzen Trennlinien-Check enthalten. Hintergrund:
ZEITRISS-Laufzeit kennt nur Masterprompt + 19 Wissensdateien; alles andere ist
Dev-/Testkontext.

**Pflichtblock pro Befund:**

- **Datensatz-Relevanz:** Betrifft der Befund die Laufzeit (Masterprompt/WS)?
- **Nur Dev/QA?:** Wenn ja, klar als Dev-Hinweis markieren (kein Runtime-Bug).
- **WS-Spiegelpflicht:** Bei Regelwirkung angeben, in **welches** WS-Modul die
  Änderung muss (oder warum keine WS-Änderung nötig ist).
- **Invarianten-Check:** Kurz vermerken, dass Save-Schema v7/Boss-Timing/Szenen-
  counts etc. nicht verletzt werden.

**Template (copy/paste):**

```md
## Datensatz-vs-Dev-Check

- Datensatz-Relevanz: <ja/nein + Grund>
- Nur Dev/QA: <ja/nein + Datei/Tool>
- WS-Spiegelpflicht: <ja/nein + Zielmodul(e)>
- Invarianten betroffen: <nein/ja + welche>
```

### Weiche Checks (beobachten, nicht enforcen — Stand 2026-04-27)

Diese Punkte sind **thematisch erwünscht**, aber bewusst **nicht als
Regressions-FAIL** gewertet (per Flo-Entscheid vom 2026-04-27 nach
Runde 3b). Bei Abweichung nur im Friction-Log notieren, nicht als Bug
reporten:

- **Cinematic-Start:** Kaffee-Tablett + Hologramm-Vorab-Gruß bei v7-Opener.
- **Mira-Monolog:** "Klingt bequem. Ist es nicht. …" thematisch aktiv,
  nicht wörtlich-Pflicht.

### Preflight-Checkliste (Pflicht vor teuren Runs)

Vor jedem Playtest **> $5 Kosten oder > 40 Turns**:

1. **Preset-Anzahl** in OpenWebUI — Abfrage (ab OWUI 0.11.x; der alte
   `/api/chat/preset`-Endpoint existiert nicht mehr, CustomAI-Presets liegen
   unter `/api/models` mit gesetztem `info.base_model_id`):

   ```bash
   curl -s "$OPENWEBUI_URL/api/models" \
     -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
     | jq '[.data[] | select(.info.base_model_id)] | length'
   ```

   Soll (Stand 2026-09-14): **7 aktive CustomAI-Presets** — 5 Bausätze als
   Mistral-Variante (ARXION, Privacy Odyssey, ACCILOG, SEKRA, ZEITRISS) plus
   ZEITRISS zusätzlich als `zeitriss-v426-uncut` (Sonnet) und
   `zeitriss-v426-deepseek` (Budget). Unerwartete Extras = Drift-Kandidat
   (historisch: `-cached`-Kopie vom 2026-04-23, aufgelöst am 2026-04-27).

2. **MP-MD5** gegen frischen `main`-Pull:

   ```bash
   git fetch origin main && md5sum meta/masterprompt_v6.md
   ```

   Mit dem MD5 aus dem Preset-`system`-Feld abgleichen. Mismatch =
   Preset veraltet oder KB-Rebuild ausstehend.

3. **Preset-`base_model`** ist `zeitriss-sonnet` (LiteLLM-Alias), nicht
   direkt `anthropic/claude-sonnet-4.6` — sonst geht der Cache über
   OpenRouter verloren. Prüfung im Preset-Payload (`/api/models`, Feld `info.base_model_id`).

4. **Single-Turn-Cache-Check** über LiteLLM: Einen Test-Call absetzen,
   dann im Response-JSON `.usage.prompt_tokens_details.cached_tokens`
   prüfen (OpenAI-Schema durch LiteLLM-Normalisierung, **nicht**
   Anthropic-`cache_read_input_tokens` direkt). Erwartung: ab Turn 2
   > 0; bei stabilem Langlauf > 80 % Hit-Rate.

5. **Golden-Setup-Check** (`zeitriss-v426-uncut`, Capabilities +
   Params im Preset-Payload):

   ```bash
   curl -s "$OPENWEBUI_URL/api/models" \
     -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
     | jq '.data[] | select(.id=="zeitriss-v426-uncut") | {capabilities: .info.meta.capabilities, params: .info.params}'
   ```

   Soll: `capabilities` = `{vision:true, file_upload:true,
   image_generation:false, code_interpreter:false, web_search:false,
   citations:false, usage:false}`; `params.temperature` = `0.8`,
   `params.max_tokens` = `64000`, `params.reasoning_effort` = `"low"`
   (nur bei Anthropic-Varianten — `zeitriss-v426-deepseek` hat **keinen**
   `reasoning_effort`-Key). `top_p`/`frequency_penalty` dürfen **nicht**
   mehr im Payload stehen. Drift = veraltetes Preset, Fix über
   `python scripts/setup.py` (ohne `--sync` — siehe
   [setup-guide.md](setup-guide.md#golden-setup-preset-params--capabilities)).

Fängt Drift-Probleme, die einen $14-Run ruinieren können.

---

## Schema F: Manuell nachvollziehbare Szenariomatrix (OWUI-Chat, ohne Harness)

> **Zielgruppe dieses Abschnitts:** ein Agent (oder Mensch) mit **nur
> Repo-Zugriff**, ohne Altair-Runtime, ohne `internal/qa/harness/`
> (Python-Orchestrierung, `agent_mp`) — die liegt außerhalb dieses Repos
> und ist hier bewusst nicht beschrieben. Jedes Szenario unten ist
> stattdessen **manuell im OWUI-Chat gegen das Preset `zeitriss-v426-uncut`
> reproduzierbar**: Chat öffnen, Prompts wie beschrieben eintippen, Antwort
> und `!save`-Output prüfen. Kein Script nötig.

**Vorbedingung für alle Szenarien** (einmalig prüfen, dann für jedes
Szenario voraussetzen):

- Preset `zeitriss-v426-uncut` existiert und ist per
  [Preflight-Checkliste](#preflight-checkliste-pflicht-vor-teuren-runs)
  oben Golden-Setup-konform (Capabilities, Params, `reasoning_effort:
  low`, KB verlinkt).
- **Ein Preset für alle Szenarien** — `reasoning_effort: low` ist global
  am Preset gesetzt, es gibt **keine** Szenario-spezifische Preset-Variante
  (kein "Low für Solo, High für Gruppe"). Wer testet, wechselt nur den
  Chat-Inhalt, nie das Preset.
- Frischer Chat pro Abschnittswechsel (Chargen/HQ/Mission/Debrief), wie im
  [Gameflow](../core/spieler-handbuch.md#gameflow-chat-wechsel) beschrieben
  — das ist Spielregel, kein Test-Artefakt.

**Save-Modell (gilt für alle Szenarien unten):** ZEITRISS speichert **pro
Figur einen eigenständigen, vollständigen v7-Save-Block** (`!save` /
`!speichern`). Der Leader-Save ist der Anker beim Laden (bestimmt, welche
Kampagne der neue Chat fortsetzt); alle weiteren Figuren-Saves werden als
**Join-Import** in denselben Chat eingefügt und spielen dort als Gäste
weiter, mit pausiertem eigenem Kampagnenstand. Es gibt **keinen**
Sammel-Merge, der aus 5 Einzel-Saves einen einzigen Gruppen-Save macht —
im HQ erzeugt `!save` automatisch **je anwesender Figur einen eigenen,
getrennten JSON-Block**.

### F1 — Solo-Journey (1 Charakter: Chargen → HQ → Mission → Save)

**Vorbedingung:** frischer Chat, keine Vorab-Saves.

**Schritte:**

1. Prompt: `Spiel starten (solo klassisch)`.
2. Charaktererschaffung bis zum Ende durchspielen (Origin, Attribute,
   Echo-Talent, Ausrüstung).
3. Nach Heimkehrbeat: Chargen-Save-Gate abwarten, `!save` eintippen.
4. **Neuen Chat öffnen**, den JSON-Block aus Schritt 3 einfügen (lädt).
5. HQ-Briefing abwarten, eine Mission annehmen und bis zum Debrief
   durchspielen.
6. Im HQ nach Debrief: `!save`.

**Pass-Kriterien:**

- Schritt 3: Save hat `last_seen.mode: "hq"` (**nicht** `"char-gen"`) —
  Chargen-Save-Gate-Invariante.
- Schritt 3 + 6: Save ist valides v7-JSON: `v: 7`, `characters[]` (genau 1
  Eintrag), `attr{}`, `reputation{}`, `characters[0].wallet` (kein
  Top-Level-`economy`-Geldfeld), `level_history[]`.
- Schritt 5: Erstkontakt im HQ-Preamble ist **Mira**, nicht Renier
  (Mira-vor-Renier-Invariante).
- Würfelwürfe in der Mission folgen `1W6 + ⌊Attribut/2⌋ + Talent + Gear`
  (Floor-Division, nicht `/2` ohne Abrundung); Exploding 6 bei W6.
- HUD erscheint nur bei Gate-Triggern (LP/Stress/PP/SYS-Änderung,
  Phasenwechsel, Schwellenmeldung), nicht pro Turn.

**Save-Crossing-Check:** Save aus Schritt 3 in einen **komplett neuen**
Chat einfügen (nicht denselben Chat weiterspielen) — muss ohne
Nachfragen laden und beim HQ-Briefing fortsetzen. Save aus Schritt 6
ebenso in einem dritten Chat gegenprüfen.

### F2 — HQ-Runde (Einkauf/Wallet/Ausrüstung)

**Vorbedingung:** ein valider Save aus F1 (Schritt 3 oder 6), frischer Chat.

**Schritte:**

1. Save einfügen (lädt im HQ).
2. Ausrüstung kaufen/wechseln (Werkstatt-Upgrade oder Cyberware laut
   Spieler-Handbuch-Abschnitt HQ-Runde).
3. `!save`.

**Pass-Kriterien:**

- `characters[0].wallet` sinkt um exakt den Kaufpreis, kein negativer
  Wallet-Wert.
- Equipment-Einträge im Save folgen dem einheitlichen Format
  `{name, type, tier}`.
- Kein `economy`-Geldfeld auf Top-Level — Wallet lebt ausschließlich unter
  `characters[].wallet`.

**Save-Crossing-Check:** Save aus Schritt 3 in neuem Chat laden — neuer
Ausrüstungsstand muss übernommen sein, alter Stand aus F1 darf nicht mehr
auftauchen.

### F3 — Einzelmission (Briefing → Konflikt → Debrief)

**Vorbedingung:** valider HQ-Save (aus F1 oder F2), frischer Chat.

**Schritte:**

1. Save einfügen, Mission annehmen.
2. Briefing → Infiltration → Konflikt → Exfiltration → Debrief
   durchspielen (12 Szenen bei Core-Ops).
3. `!save` im HQ nach Debrief.

**Pass-Kriterien:**

- Core-Mission hat **12 Szenen**, Mini-Boss bei Szene 5, Boss bei Szene 10
  (Boss-Timing-Invariante).
- Px-Fortschritt folgt der Px-Tabelle (TEMP-Stufe-abhängige Increments,
  siehe [AGENTS.md](../AGENTS.md#pflicht-invarianten-nicht-brechen)).
- Psi-Einsätze zeigen immer **beide** Kosten (PP **und** SYS), nie nur
  eine.
- `level_history[]` hat einen neuen Eintrag für die abgeschlossene
  Mission.

**Save-Crossing-Check:** wie F1/F2 — Save in neuem Chat laden, HQ-Zustand
muss dem Debrief-Endstand entsprechen.

### F4 — Faithful 5er (Gruppe, getrennte Saves, autonome Mission)

**Vorbedingung:** 5 valide Solo-Saves (aus je einem eigenen F1-Durchlauf,
oder aus vorhandenen `internal/qa/harness/fixtures/`-Beispielen als
Referenzformat — nicht als Testdaten dieses Szenarios selbst
verwenden, sondern nur um das erwartete v7-Schema zu vergleichen).

**Schritte:**

1. Prompt: `Spiel starten (gruppe klassisch)` **oder**: Leader fügt seinen
   Single-Char-JSON-Save direkt ein (bestimmt die Kampagne).
2. Die 4 weiteren Spieler fügen nacheinander ihre eigenen Saves als
   **Join-Import** in denselben Chat ein — sie spielen ab jetzt als Gäste
   in der Leader-Kampagne, ihr eigener Kampagnenstand pausiert.
3. SL führt den Merge der 5 Figuren **selbst** durch (kein manueller
   Merge-Schritt, keine externe Zusammenführung) — Gruppe befindet sich
   danach gemeinsam im HQ.
4. Autonome Mission durchspielen (Gruppe agiert gemeinsam durch Briefing →
   Konflikt → Debrief).
5. Zurück im HQ: `!save`.

**Pass-Kriterien:**

- Schritt 3: alle 5 Figuren sind in derselben Szene/demselben
  HQ-Zustand, keine Figur bleibt in ihrem alten Solo-Kontext hängen.
- Schritt 5: `!save` erzeugt **5 getrennte v7-JSON-Blöcke**, einen pro
  anwesender Figur — **kein** einzelner "5-in-1"-Sammel-Save.
- Jeder der 5 Blöcke ist für sich ein vollständiges v7-Save (`v: 7`,
  `characters[]` mit genau **1** Eintrag — der jeweils eigenen Figur —,
  `attr{}`, `reputation{}`, `wallet`, `level_history[]`).
- Persönliche Fortschritte/Erinnerungen reisen je Figur mit; fremde
  Kampagnenstände, Auszahlungen und einzigartige Beute anderer Figuren
  werden **nicht** in die eigenen Saves kopiert.
- Mira-vor-Renier und HUD-Disziplin gelten unverändert wie in F1.

**Save-Crossing-Check:** einen der 5 Einzel-Saves in einem **neuen, leeren**
Chat laden (ohne die anderen 4) — muss als eigenständiger Solo-Fortsetzung
funktionieren, mit dem persönlichen Fortschritt aus der Gruppensession,
aber ohne Abhängigkeit von den anderen 4 Saves.

### F5 — Split/Merge (nur Legacy-Import-Kompatibilität, KEINE Gruppen-Mechanik)

> **Einordnung, wichtig:** Split/Merge (`family_id`, `thread_id`,
> `team_split`/`team_merge`-Traces, siehe Regressions-Matrix oben) ist
> **kein** aktiver Gruppen-Spielweg für neue Sessions. Es ist
> **Kompatibilität für den Import bestehender/älterer Split/Merge-Saves**
> (z. B. aus vor-F4-Kampagnen oder externen Quellen). Der aktive,
> empfohlene Gruppen-Weg für neue Sessions ist **F4 (Faithful 5er)** mit
> getrennten Saves, nicht Split/Merge.

**Vorbedingung:** ein vorhandener Split/Merge-Legacy-Save (`family_id`
gesetzt) — z. B. aus einer älteren Kampagne oder aus den Referenzformaten
unter `internal/qa/harness/fixtures/` (nur als Formatreferenz, nicht als
lebendiger Testweg).

**Schritte:**

1. Legacy-Split-Save in einen Chat importieren.
2. Prüfen, ob die SL den Import als Legacy-Kontinuität erkennt
   (`continuity.split.family_id` im geladenen Save wird respektiert, nicht
   überschrieben).
3. Weiterspielen bis zu einem Convergence-Punkt (Rejoin), `!save`.

**Pass-Kriterien:**

- Import wird als Legacy-Fall behandelt, nicht als aktiver neuer Split —
  die SL bietet keinen neuen Split über diesen Mechanismus als
  Standard-Gruppenweg an.
- `family_id`/`thread_id`/`expected_threads`/`resolved_threads` bleiben
  aus dem importierten Save konsistent, kein stiller Reset.
- Merge-Ergebnis (falls Rejoin gespielt wird): `characters[]`,
  `characters[].wallet` (Wallets reisen mit, kein Pool-Merge).

**Save-Crossing-Check:** entfällt für reine Import-Prüfung (Legacy-Save
wird nicht durch dieses Szenario neu erzeugt, nur gelesen/fortgesetzt).

### DEFERRED (noch nicht getestet, nicht Teil dieser Matrix)

Folgende Modi sind **nicht** Teil der oben abgedeckten Szenarien und
wurden im Rahmen dieser Doku-Erweiterung **nicht** verifiziert:

- **PvP** (Arena-Match-Mechanik als kompetitiver Modus)
- **Rift-2/3** (Rift-Ops Stage 2 und 3, jenseits der in F1-F5 geprüften
  Core-Ops)
- **Chronopolis-Raid**
- **Arena** (allgemein, über den in F5 genannten Legacy-Kontext hinaus)

Wer diese Modi testet, sollte einen eigenen Schema-F-Nachtrag mit
derselben Struktur (Vorbedingung · Schritte · Pass-Kriterien ·
Save-Crossing-Check) ergänzen, statt Annahmen aus F1-F5 zu übertragen —
die Timing-/Save-Invarianten dieser Modi sind an anderer Stelle in der
Regressions-Matrix (P1-2, P1-3, P2-1 oben) nur teilweise abgedeckt und
nicht Gegenstand dieses Abschnitts.

---

## Cross-Findings: ZEITRISS als Leitmotiv

Wenn bei einem ZEITRISS-Playtest etwas auffällt, das **strukturell oder
technisch** auch andere CustomAIs betreffen könnte, wird das explizit als
Cross-Finding festgehalten:

1. In Daily-Note mit Prefix `Cross-Finding:` notieren
2. Analog-Check in den anderen Repos (grep, Preset-Inspection, Watchguard-
   Scan)
3. Pro betroffenem Repo eigener PR mit Fix
4. Langlebige Lessons in `~/.openclaw/workspace-cloud/LEARNINGS.md`

**Historische Cross-Findings aus ZEITRISS** (Kurz-Kontext; für Details
siehe Daily-Notes April 2026 im Agent-Workspace):

- **`lp-terminology`-Watchguard** (ein CI-Check, der die Benennung der
  Lebenspunkte in Erzähltext prüft) prüfte nur Prosa, nicht JSON-
  Schema-Felder (2026-04-26) — betrifft jeden Watchguard in jedem CustomAI.
- **Token-Watcher-Regex** (ein Log-Parser, der LiteLLM-Responses
  für Cache-Hit-Rate auswertet) brach an verschachteltem
  `prompt_tokens_details` (2026-04-27) — betrifft jeden Harness, der
  gegen LiteLLM läuft.
- **Preset-Kopien driften still** (2026-04-27) — betrifft jedes
  OpenWebUI-Deploy mit mehreren CustomAIs; manuelle Geschwister-Presets
  sind Altlasten-Magnete.

---

## Auswertung: Run-Artefakte zu Repo-Doku

**Run-Artefakte liegen seit 2026-06-18 im Repo** unter
`internal/qa/evidence/2026-playtests/` (vorher nur im Workspace). Was
zusätzlich als kuratierte Doku ins Repo wandert:

- **Strukturelle Findings** → `docs/qa/<finding-name>.md` (siehe bestehende:
  `playtest-befund-chargen-save-gate.md`, `playtest-befund-w10-schwelle-halluzination.md`)
- **Regressions-Referenzen** → in die Regressions-Matrix hier oben integrieren
- **Schema-/Mechanik-Bestätigungen** → `docs/qa/<thema>-verifikation.md`
- **MP-Änderungsvorschläge** → eigener PR gegen `meta/masterprompt_v6.md`,
  mit Watchguard-Erweiterung in `runtime.js` und `scripts/smoke.sh`

### Aktueller Fokus-Tracker (PvP/Bio, Stand 2026-04-28)

Für den laufenden Nachcheck-Block ist der Umsetzungs- und QA-Stand separat
gepflegt in:

- [`docs/qa/pvp-bio-nachcheck-status.md`](qa/pvp-bio-nachcheck-status.md)

Diese Datei dient als Abhakliste zwischen Implementierung und nächstem
Playtest-Zyklus (PvP-only → Save-Export → Cross-Mode).

Für den konkreten Lauf liegt bereits eine Befundvorlage bereit:

- [`docs/qa/playtest-befund-pvp-only-cashout.md`](qa/playtest-befund-pvp-only-cashout.md)

**Konvention für `docs/qa/`-PRs aus Playtest-Findings** (Default, kein
Dogma — bei Sonderfällen wie `buff-schwelle-critic-selbstreview.md`
Abweichung erlaubt):

- Commit-Subject: `qa: <kurze-erkenntnis>` oder `fix(runtime): <regelbruch>`
- Im `## Warum`: Link auf den konkreten Run-Artefakt-Pfad unter
  `internal/qa/evidence/2026-playtests/<run>/` (im Repo, für alle nachvollziehbar)
- `## Verifikation`: CI-Smoke (`bash scripts/smoke.sh`) + ggf. Verweis auf
  erneuten Playtest-Run, der den Fix prüft

---

## CI-Smoke

Jede Regel-/Schema-Änderung muss durch:

```bash
bash scripts/smoke.sh
```

Muss grün sein **bevor** ein Playtest-Run startet, der die Änderung prüft.
Sonst landet ein Bug im Playtest, der eigentlich schon in der CI auffällt.

---

## Verweise

- Menschliches Tester-Briefing: [docs/qa/tester-playtest-briefing.md](qa/tester-playtest-briefing.md)
- Playtest-Readiness-Gate: `internal/qa/process/playtest-readiness-gate.md`
- Harness im Repo: `internal/qa/harness/README.md`
- Run-Evidenz im Repo: `internal/qa/evidence/2026-playtests/README.md`
- Agent-interner Workspace (Arbeitskopie, Spiegel):
  `~/.openclaw/workspace-cloud/playtests/zeitriss/`

---

## Historie

- **2026-04-27** — Erstversion. Entstanden nach Playtest-Runde 3b, als klar
  wurde, dass der Persona-basierte Workflow wiederholt genug läuft, um eine
  kanonische Anleitung zu rechtfertigen. Ergänzt den manuellen Tester-Briefing
  um den Agent-automatisierten Pfad.
- **2026-09-16** — Abschnitt "Schema F" ergänzt: manuell im OWUI-Chat
  nachvollziehbare Szenariomatrix (Solo-Journey, HQ-Runde, Einzelmission,
  Faithful 5er, Split/Merge als Legacy-Import-Kompatibilität, DEFERRED-Liste)
  für Agenten mit reinem Repo-Zugriff, ohne den privaten
  `internal/qa/harness/`-Python-Orchestrator vorauszusetzen.
