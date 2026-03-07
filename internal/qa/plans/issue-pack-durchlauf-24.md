---
title: "Issue-Pack Fahrplan – Durchlauf 24"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 24

Quelle: Fortsetzung ZR-016 (Save-SSOT/Cross-Mode-Drift im Save-Modul).

## Ziel
Den v7-Kanon im Save-Modul `systems/gameflow/speicher-fortsetzung.md` in den
Cross-Mode- und Accessibility-Abschnitten nachziehen, damit dort keine
widersprüchlichen Standardpfade (`economy.cu`, `party.characters[]`,
`save_version`) mehr als aktiver Runtime-Default stehen.

## Scope dieses Durchlaufs

- Runtime-Textkonsolidierung:
  - `systems/gameflow/speicher-fortsetzung.md`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-24.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Änderungen an Kampfregeln, Boss-Timing, Szenenzahl oder Tonalität.
- Umbau von `runtime.js`-Datenstrukturen.
- Entfernen von Legacy-Importhinweisen außerhalb des konkret überarbeiteten
  Abschnitts.

## Exit-Kriterium für Durchlauf 24

- Der überarbeitete Save-Abschnitt nennt `v: 7`, `economy.hq_pool`,
  `characters[]` und `arc` als Standard.
- Cross-Mode-Transferregeln referenzieren kein aktives
  `economy.wallets`/`economy.cu`-Standardmodell.
- `bash scripts/smoke.sh` ist grün.
