---
title: "Issue-Pack Fahrplan – Durchlauf 01"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 01

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Den externen Issue-Pack in priorisierte, nachvollziehbare Arbeitspakete überführen,
mit klarer Anschlussfähigkeit für weitere Durchläufe.

## Backlog-Cluster

| Cluster | Scope | Priorität | Status | Nächster Schritt |
| --- | --- | --- | --- | --- |
| C1 Save-SSOT + Wallet | Save v7, Feldnamen, Merge/Load-Flow | P0 | offen | Schema- und Runtime-Texte gegen `characters[]`, `economy.hq_pool`, `arc` konsolidieren |
| C2 Würfel-SSOT | W10-Schwelle, Burst-Cap, Heldenwürfel | P0 | in Umsetzung | Widersprüche in Runtime-Modulen entfernen + Guard-Lint ergänzen |
| C3 Px/Arena-Entkopplung | deterministischer Px-Flow, Arena-Reward | P0 | offen | Reset-Zeitpunkt auf Debrief/HQ-Flow festziehen |
| C4 Drift-Härtung | Terminologie-/Legacy-Lints | P1 | offen | `tools/lint_runtime.py` um verbotene Tokens ergänzen |
| C5 Ton/Essay-Schichtung | Runtime vs. Essay | P1 | offen | schwere Essay-Blöcke in Dev-Doku auslagern |

## Durchlauf 01 (aktuell)

- Fokus: **C2 Würfel-SSOT**.
- Zielbild: W6 Standard, W10 ab Attribut 11, Heldenwürfel ab 14, Burst-Cap 1 ohne Ketten-Exploding.
- Lieferobjekte:
  1. Regeltext in `core/wuerfelmechanik.md` konsolidieren.
  2. Smoke-Check laufen lassen.
  3. QA-Logeintrag mit Delta + Restpunkten schreiben.

## Exit-Kriterium für Durchlauf 01

- Keine aktive Formulierung mehr, die W10 zugleich als Standard **und** als rein optionale Hausregel im gleichen Modul führt.
- Smoke-Check grün.
- Folgearbeiten für C1/C3/C4 im QA-Log vorgemerkt.
