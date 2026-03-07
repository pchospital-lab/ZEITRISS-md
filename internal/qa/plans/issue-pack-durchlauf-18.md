---
title: "Issue-Pack Fahrplan – Durchlauf 18"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 18

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Issue 8 (Ton-Kanon) mit einem kleinen, anschlussfähigen Schritt stabilisieren:
Core/Rift als Default schärfen und Mythic-Inhalte als explizit optionalen
Layer markieren.

## Scope dieses Durchlaufs

- Runtime-Textschärfung:
  - `core/spieler-handbuch.md`
  - `gameplay/kampagnenuebersicht.md`
  - `gameplay/kreative-generatoren-missionen.md`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-18.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Umbau einzelner Generator-Tabellen oder neue Subsysteme.
- Änderungen an Save-Schema, Ökonomie oder Runtime-Code.

## Exit-Kriterium für Durchlauf 18

- Ton-Ebenen Core/Rift/Mythic sind in Handbuch + Kampagnenübersicht konsistent.
- Generator-Modul enthält eine klare Ton-Gewichtung passend zum Ebenenmodell.
- `bash scripts/smoke.sh` ist grün.
