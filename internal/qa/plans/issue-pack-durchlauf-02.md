---
title: "Issue-Pack Fahrplan – Durchlauf 02"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 02

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Nächsten P0-Block mit direktem Runtime-Effekt schließen: **Px/Arena-Entkopplung**,
inklusive klarer Übergabe für den folgenden Save-/Wallet-SSOT-Durchlauf.

## Scope dieses Durchlaufs

- C3 Px/Arena-Entkopplung (P0)
  - Arena darf `campaign.px` nicht verändern.
  - PvP-Rückkehrpfad beschreibt nur Arena-spezifische Rewards (CU/Ruf/Training).
  - Formulierungen in Runtime-Modulen auf denselben Pfad angleichen.

## Nicht im Scope (bewusst verschoben)

- C1 Save-SSOT + Wallet (größter Block, folgt als Durchlauf 03).
- C4 Drift-Härtung (`tools/lint_runtime.py` Legacy-Token-Guards).

## Exit-Kriterium für Durchlauf 02

- Kein aktiver Runtime-Text koppelt Arena-Belohnungen an Px.
- PvP-Exit ist als modusbezogene Rückkehr dokumentiert, ohne Progressionssprung in Px.
- Pflichtcheck `bash scripts/smoke.sh` ist grün.
