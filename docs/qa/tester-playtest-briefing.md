---
title: "Tester-Playtest-Briefing"
version: 2.0.0
tags: [meta]
---

# Tester-Playtest-Briefing

> Pflicht vor jedem externen Testlauf: den
> `internal/qa/process/playtest-readiness-gate.md` vollständig als
> Go/No-Go-Gate abarbeiten.

## Plattform

- **OpenWebUI + OpenRouter** (empfohlen)
- Modell: `anthropic/claude-sonnet-4.6` (einziges Modell mit voller Regeltreue)
- Setup: `./scripts/setup-openwebui.sh` → Preset + 19 WS-Module + Masterprompt

## Testmatrix

### Solo-Tests

| Test | Eingabe | Prüfpunkte |
|------|---------|------------|
| Quickstart | `Spiel starten (solo schnell)` | Summe 18, Cap 6, v7-Save, Ruf im Bogen |
| Klassisch | `Spiel starten (solo klassisch)` | Chargen-Dialog, Attributverteilung, HQ-Intro |
| Save/Load | `!save` → neuer Chat → `Spiel laden` + JSON | Alle Werte erhalten, v7-Schema |
| Mission durchspielen | 12 Szenen, Debrief | Px-Staffel korrekt, Ruf + Lizenz-Tier im Debrief |
| Level-Up | Nach Mission 1 | Genau 1 Wahl: +1 Attr ODER Talent ODER +1 SYS |

### Gruppen-Tests

| Test | Eingabe | Prüfpunkte |
|------|---------|------------|
| Gruppe erstellen | `Spiel starten (gruppe schnell)` + 2-5 Saves | characters[] Array, Host = Index 0 |
| Team-Split | Nach Episode: Gruppe aufteilen | Seeds korrekt zugewiesen, HQ-Pool aufgeteilt |
| Separate Rifts | Jedes Teilteam spielt Rift in eigenem Chat | Unabhängige Saves, Artefakte, Level-Ups |
| Team-Merge | 2 Saves zusammenführen | Transparentes Merge-Protokoll, alle Chars intakt |

### Mechanik-Tests

| Test | Prüfpunkte |
|------|------------|
| Würfelproben | `1W6 + ⌊Attr/2⌋ + Talent + Gear`, Exploding bei 6 (W6) / 10 (W10) |
| Burst-Cap | Max 1 Zusatzwurf pro Würfel, kein Ketten-Exploding |
| Heldenwürfel | Ab Attribut 14: W10 + Heldenwürfel (Reroll) |
| Px-Staffel | TEMP 1-2: alle 2 Miss. +1 / 3-5: +1 / 6-8: +2 / 9-11: +2 / 12-14: +3 |
| Psi-Kosten | Jede Kraft nennt PP UND SYS |
| Artefakte | Gate 1W6 (bei 6) → 1W14. TEMP ≥ 14: +2 → Mythic bei 15-16 |
| Ruf/Tier | Debrief zeigt Ruf + Lizenz-Tier. Ruf +X = Tier X |

### Save-Schema v7

Prüfe bei jedem Save:
- `v: 7` (nicht `save_version: 6`)
- `characters[]` (nicht `character{}` + `party{}`)
- `attr` (nicht `attributes` mit SYS_max/runtime/used)
- `reputation` mit Fraktionswerten
- `economy.hq_pool` (nicht `economy.cu`)
- Keine Laufzeit-Daten (exfil, cooldowns, scene)
- Logs: 4 Arrays (trace, market, artifact_log, notes)

## Evidence dokumentieren

Playtest-Ergebnisse als Markdown unter `internal/qa/evidence/playtest-YYYY-MM-DD/`.
Pro Test eine Datei mit Modell, Szenario, Ergebnis und ggf. JSON-Save.

Vor dem ersten Testfall eines neuen Laufs immer zusätzlich den
Playtest-Readiness-Gate ausführen:

- `internal/qa/process/playtest-readiness-gate.md`

## CI-Smoke

```bash
bash scripts/smoke.sh
```

Muss vor jedem Push grün sein.
