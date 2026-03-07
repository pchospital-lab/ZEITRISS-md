---
title: "Issue-Pack Fahrplan – Durchlauf 19"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 19

Quelle: `uploads/ZEITRISS_codex_issue_pack.md` + Maintainer-Feedback nach Durchlauf 18.

## Ziel
Durchlauf 18 auf den gewünschten Spielkanon zurückziehen, ohne Core-Flow zu
verschieben: Core-Ops bleiben wie bisher bodenständig; Rift-Ops werden als
mystische, eigenständige Casefile-"Filme" präzisiert.

## Scope dieses Durchlaufs

- Runtime-Textkorrektur:
  - `core/spieler-handbuch.md`
  - `gameplay/kampagnenuebersicht.md`
  - `gameplay/kreative-generatoren-missionen.md`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-19.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Änderung von Szenenanzahl, Boss-Timing oder Px-Formel.
- Umbau von Save-Schema, Ökonomie oder Runtime-Codepfaden.

## Exit-Kriterium für Durchlauf 19

- Das 3-Ebenen-Modell aus Durchlauf 18 ist aus Runtime-Texten entfernt.
- Rift-Ops sind als eigenständige Casefiles ohne Arc-Pflichtbezug verankert.
- Kampf- und PvP-Hinweise sind mit Filmstandard konsistent (PvP nicht-tödlich).
- `bash scripts/smoke.sh` ist grün.
