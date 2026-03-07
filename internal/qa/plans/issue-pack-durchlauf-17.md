---
title: "Issue-Pack Fahrplan – Durchlauf 17"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 17

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Die Item-Regeln so nachziehen, dass der generative Kern von ZEITRISS klar
bleibt: freie, plausible Item-Erstellung durch Spielleitung ja; Save-Schema-
Konsistenz über `{name,type,tier}` bleibt strikt.

## Scope dieses Durchlaufs

- Korrektur in Runtime-Modulen:
  - `characters/ausruestung-cyberware.md`
  - `meta/masterprompt_v6.md`
  - `core/sl-referenz.md`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-06-issue-pack-durchlauf-17.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Ausbau einer festen Item-Datenbank oder Pflicht-Item-IDs.
- Änderungen an Mission-Loops, Shop-Ökonomie oder Save-Version.

## Exit-Kriterium für Durchlauf 17

- WS-Texte betonen freie, plausible Item-Erstellung durch Spielleitung.
- Save-Format bleibt überall konsistent bei `equipment[{name,type,tier}]`.
- Keine neuen optionalen Save-Felder als Pseudo-Standard im v7-Kanon.
- `bash scripts/smoke.sh` ist grün.
