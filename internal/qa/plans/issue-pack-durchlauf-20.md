---
title: "Issue-Pack Fahrplan – Durchlauf 20"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 20

Quelle: Maintainer-Feedback nach Durchlauf 19.

## Ziel
Boss-Endzustände filmischer und spielverträglicher präzisieren: Bei 0 LP sollen
Boss-/Mini-Boss-Gegner primär besiegt, schwer verletzt und festgesetzt werden
(ITI-Richterpfad), statt standardmäßig zu sterben.

## Scope dieses Durchlaufs

- Runtime-Textkorrektur:
  - `core/spieler-handbuch.md`
  - `gameplay/kreative-generatoren-begegnungen.md`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-20.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Änderungen an Save-Schema, Ökonomie, Boss-Timing oder Szenenanzahl.
- Umbau von PvP-/Arena-Mechanik über die bestehende Nicht-Tod-Policy hinaus.

## Exit-Kriterium für Durchlauf 20

- Boss-/Mini-Boss-Endzustand bei 0 LP ist als Festsetzungspfad dokumentiert.
- Todesfälle bleiben explizit als Ausnahme-/Dramatikpfad markiert.
- Markennamen in den neuen Formulierungen vermieden.
- `bash scripts/smoke.sh` ist grün.
