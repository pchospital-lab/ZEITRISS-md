---
title: "QA-Harness — automatisierte Persona-Playtests"
version: 1.0.0
tags: [meta, qa]
---

# QA-Harness

> Seit 2026-06-18 im Repo (vorher nur im privaten Agent-Workspace).
> Diese Scripts gehören **nicht** zum Spielinhalt und werden **nicht** in den
> Wissensspeicher geladen.

Hier liegen die Harness-Scripts, die einen Persona-Sub-Agent (Spieler) gegen
das ZEITRISS-SL-Preset spielen lassen — die automatisierte Seite der QA.
Die menschliche Seite steht in [`docs/qa/tester-playtest-briefing.md`](../../../docs/qa/tester-playtest-briefing.md),
der Methoden-Guide in [`docs/testing.md`](../../../docs/testing.md).

Run-Artefakte dieser Läufe liegen unter
[`../evidence/2026-playtests/`](../evidence/2026-playtests/).

## Inhalt

| Datei | Zweck |
|---|---|
| `coreops_split_merge.py` | Core-Ops Split/Merge-Zyklus (aktuellster Harness, gehärtet) |
| `group-harness.py` | Gruppen-Canary / organischer 5er-Lauf (Phasen 2/3) |
| `solo_journey.py` | Solo-Durchstich über Browser-Pfad (local:-Temp-Chat) |
| `split_merge.py` | Split/Merge-Matrix (4-1/3-2/resplit/konflikt) |
| `merge_assert.py` | Validator (v7-Schema als SSOT, Σ-Konservierung) |
| `coreops-harness.py` | Regel-Mechanik-Deep-Dive + PSI-Tracking |
| `episode1-mini.py` | Solo-Smoke (Noob-Persona) |
| `pflichtgate-verify.py` | Pflichtgate-Regression (Concealment-Start u.a.) |
| `solo-canary.py` | Kurzer Solo-Sanity-Run |
| `w10-schwelle-probe.py` | W10-Schwellen-Regel-Regression |
| `g3_token_probe.py` | Token-Last-Messung (usage.prompt_tokens) |
| `build_5er_anchor.py` | Baut vollständigen 5er-HQ-Save-Anker (strict) |
| `owui_client.py` | OpenWebUI-Client, fährt exakt den Browser-Chat-Pfad nach |
| `persona-driven/` | Zwei-KI-Setup (OWUI-SL + OR-Persona), `persona-player.py` + `personas.yaml` |
| `personas/` | Persona-Profile (noob.md, end-tier-vet.md) |
| `fixtures/` | Save-Anker (save-after-hq, save-group-initial, save-lvl950-marek) |
| `scenarios/` | Placeholder — Scenarios aktuell inline in den Harness-PHASES-Dicts |
| `owui-patches/` | OpenWebUI-Container-Hotfixes (socket-main-chatid-none) |
| `zeitriss-sysprompt.txt` | **Eingefrorene MP-Kopie v4.2.6** (Harness-Input-Snapshot, NICHT SSOT) |

## Secrets / Keys

Alle Scripts laden Zugangsdaten **zur Laufzeit aus lokalen Dateien**, nie
hardcoded:

- `OPENWEBUI_API_KEY` aus `~/.openwebui_env` (`source` vor dem Lauf)
- OpenRouter-Key (`sk-or-*`) aus `auth-profiles.json` (nur `persona-driven`)

Endpoints sind localhost (`127.0.0.1:8080` OWUI, `:4000` LiteLLM) — keine
Secrets. **Vor jedem Commit:** Run-Logs auf Token-Muster prüfen (ZEITRISS ist
public). Der Initial-Import 2026-06-18 wurde vollständig gegen
`sk-`/`Bearer`/`ghp_`/Authorization-Muster gescannt — sauber.

## Aufruf-Pattern

```bash
source ~/.openwebui_env
cd internal/qa/harness
python3 group-harness.py --phase 2       # Gruppen-Canary
python3 coreops_split_merge.py           # Core-Ops Split/Merge
python3 episode1-mini.py                 # Solo-Smoke
```

## Hinweise / offene Punkte

- **KB-ID wechselt bei jedem Rebuild** — aktuelle ID steht im Header des
  jeweiligen Harness. Bei Mismatch: Preflight-Kritiker schlägt an, nicht starten.
- **Masterprompt-MD5** gegen `meta/masterprompt_v6.md` prüfen, nie gegen die
  eingefrorene `zeitriss-sysprompt.txt` (die ist nur historischer Input).
- `episode1-mini.py` / `w10-schwelle-probe.py` haben teils Port-3000-Reste aus
  der OWUI-Pre-0.9.1-Zeit — vor Einsatz Env/Port prüfen.
- **Scenarios extrahieren** (offen): Scenarios aus den PHASES-Dicts in
  `scenarios/`-Files lösen, Harness lädt per `--scenario`.

## Arbeitskopie

Die lebende Arbeitskopie spiegelt der Agent-Workspace unter
`~/.openclaw/workspace-cloud/playtests/zeitriss/` — dort entstehen neue Runs,
die kuratiert hierher committet werden.
