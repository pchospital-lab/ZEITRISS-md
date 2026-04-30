---
title: "ZEITRISS — Testing-Guide (Persona-Playtest)"
version: 1.1.0
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
lassen, liegen im privaten Agent-Workspace, nicht in diesem Repo.
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
  des `group-harness.py`. Bei Mismatch: Preflight-Kritiker schlägt an,
  Harness nicht starten.
- **Masterprompt-MD5** gegen Repo-Version prüfen (`meta/masterprompt_v6.md`),
  nie gegen eine Preset-Kopie vertrauen.

### Harness-Location

Alle Harnesses liegen workspace-lokal unter:

```text
~/.openclaw/workspace-cloud/playtests/zeitriss/
├── harness/              # group-harness.py, coreops-harness.py,
│                         # episode1-mini.py, w10-schwelle-probe.py
├── personas/             # noob.md, end-tier-vet.md
├── scenarios/            # Placeholder (aktuell inline in PHASES-Dicts)
├── fixtures/             # save-lvl950-marek.json, save-group-initial.json,
│                         # save-after-hq.json
└── runs/                 # YYYY-MM-DD-<kurzname>/ pro Run
```

Aufruf-Pattern:

```bash
source ~/.openwebui_env
cd ~/.openclaw/workspace-cloud/playtests/zeitriss
python3 harness/group-harness.py --phase 2       # Gruppen-Canary
python3 harness/coreops-harness.py               # Regel-Mechanik, PSI-Tracking
python3 harness/episode1-mini.py                 # Solo-Smoke
```

**Harness-Übersicht:**

| Script                  | Zweck                                 | Dauer (ca.) | Env erforderlich                     |
| ----------------------- | ------------------------------------- | ----------- | ------------------------------------ |
| `group-harness.py`      | Gruppen-Canary (3 Personas gegen SL)  | ~15 Min     | `OPENWEBUI_URL`, `OPENWEBUI_API_KEY` |
| `coreops-harness.py`    | Regel-Mechanik-Deep-Dive + PSI-Track  | ~25 Min     | dito                                 |
| `episode1-mini.py`      | Solo-Smoke (Noob-Persona)             | ~10 Min     | dito (Hinweis: Port 3000 hardcoded)  |
| `w10-schwelle-probe.py` | W10-Schwellen-Regel-Regression        | ~5 Min      | dito (Hinweis: Port 3000 hardcoded)  |

*Die zwei Port-3000-Scripts sind ein offener Fix, seit OpenWebUI auf 8080
migriert wurde (0.9.1). Für den Einsatz entsprechend Env anpassen oder
vorher Script patchen.*

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
  `economy.hq_pool`, `level_history[]`, `last_seen.mode:"hq"`
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
- deterministische Merge-Ergebnisse (`characters[]`, `economy.hq_pool`,
  `campaign.px`/`px_state`)
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

1. **Preset-Anzahl** in OpenWebUI — Abfrage:

   ```bash
   curl -s "$OPENWEBUI_URL/api/chat/preset" \
     -H "Authorization: Bearer $OPENWEBUI_API_KEY" | jq 'length'
   ```

   Soll: **5 aktive CustomAI-Presets**. Mehr = Drift-Kandidat
   (Beispiel: `-cached`-Kopie vom 2026-04-23, aufgelöst am 2026-04-27).

2. **MP-MD5** gegen frischen `main`-Pull:

   ```bash
   git fetch origin main && md5sum meta/masterprompt_v6.md
   ```

   Mit dem MD5 aus dem Preset-`system`-Feld abgleichen. Mismatch =
   Preset veraltet oder KB-Rebuild ausstehend.

3. **Preset-`base_model`** ist `zeitriss-sonnet` (LiteLLM-Alias), nicht
   direkt `anthropic/claude-sonnet-4.6` — sonst geht der Cache über
   OpenRouter verloren. Prüfung im Preset-Payload (`/api/chat/preset`).

4. **Single-Turn-Cache-Check** über LiteLLM: Einen Test-Call absetzen,
   dann im Response-JSON `.usage.prompt_tokens_details.cached_tokens`
   prüfen (OpenAI-Schema durch LiteLLM-Normalisierung, **nicht**
   Anthropic-`cache_read_input_tokens` direkt). Erwartung: ab Turn 2
   > 0; bei stabilem Langlauf > 80 % Hit-Rate.

Fängt Drift-Probleme, die einen $14-Run ruinieren können.

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

**Run-Artefakte bleiben im Workspace.** Was ins Repo wandert:

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
- Im `## Warum`: Link auf den konkreten Run-Artefakt-Pfad im Workspace
  (auch wenn Repo-Leser nicht drauf zugreifen — Paper-Trail für den
  Repo-Agenten im Workspace)
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
- Agent-interner Workspace (nicht Teil des Repos): `~/.openclaw/workspace-cloud/playtests/zeitriss/README.md`

---

## Historie

- **2026-04-27** — Erstversion. Entstanden nach Playtest-Runde 3b, als klar
  wurde, dass der Persona-basierte Workflow wiederholt genug läuft, um eine
  kanonische Anleitung zu rechtfertigen. Ergänzt den manuellen Tester-Briefing
  um den Agent-automatisierten Pfad.
