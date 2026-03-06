---
title: "Issue-Pack Fahrplan – Durchlauf 15"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 15

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Restdrift im Ökonomie-Wording weiter reduzieren: Arena-/Debrief-Texte in
Runtime-Modulen sollen den HQ-Pool konsistent als `economy.hq_pool` referenzieren
und `economy.cu` nur noch als Legacy-Importpfad nennen.

## Scope dieses Durchlaufs

- Wording-Abgleich in geladenen Runtime-Modulen:
  - `systems/toolkit-gpt-spielleiter.md`
  - `core/sl-referenz.md`
  - `gameplay/kampagnenstruktur.md`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-06-issue-pack-durchlauf-15.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Vollständige Migration historischer Save-Beispiele in
  `systems/gameflow/speicher-fortsetzung.md`.
- Neue Lint-Regeln gegen jedes Vorkommen von `economy.cu` (würde aktuell noch
  legitime Legacy-Migrationspassagen treffen).

## Exit-Kriterium für Durchlauf 15

- Die betroffenen Arena-/Debrief-Abschnitte nutzen `economy.hq_pool` als
  primäre SSOT-Referenz.
- Legacy-Credits-/CU-Fallback bleibt explizit als Importpfad markiert.
- `bash scripts/smoke.sh` ist grün.
