---
title: "QA-Log – Issue-Pack Durchlauf 32"
date: 2026-03-07
scope: "Save-Modul Restdrift in Load-/Koop-Ablauftexten"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), verbleibende aktive Legacy-Wortlaute in
  `systems/gameflow/speicher-fortsetzung.md`.

## Umsetzung in diesem Durchlauf

1. **Load-/Merge-Flow auf v7-Wording gezogen (`systems/gameflow/speicher-fortsetzung.md`)**
   - `load_deep()` beschreibt nun die Migration in die **v7-Zielstruktur**.
   - Multi-Save-Import referenziert den Host-Pool als `economy.hq_pool`.
   - Mid-Session-Merge nennt `characters[]` als aktiven Roster-Pfad.

2. **Koop-/Wallet-Abschnitte konsolidiert (`systems/gameflow/speicher-fortsetzung.md`)**
   - Wallet-Initialisierung nutzt `characters[].wallet` als SSOT.
   - `apply_wallet_split()` spiegelt Ergebnisse in `characters[].wallet`.
   - Hazard-Pay bucht auf `economy.hq_pool` statt Legacy-Pool.
   - Solo→Koop- und Persistenztext auf `characters[]`/`wallet` aktualisiert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
