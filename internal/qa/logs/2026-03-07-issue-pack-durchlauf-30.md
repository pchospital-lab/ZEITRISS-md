---
title: "QA-Log – Issue-Pack Durchlauf 30"
date: 2026-03-07
scope: "Wallet-/Roster-SSOT in Leitmodulen + Guard"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), Restdrift nach Durchlauf 29:
  - aktive Koop-/Save-Leittexte enthielten noch v6-Formulierungen
    (`economy.wallets{}`, `party.characters[]`, v6-Pfadbaum).

## Umsetzung in diesem Durchlauf

1. **SL-Referenz konsolidiert (`core/sl-referenz.md`)**
   - SaveGuard-Kompaktbaum auf v7-Zielpfade umgestellt (`v`, `characters[]`, `economy.hq_pool`, `arc`).
   - Koop-Auszahlungsblock auf `characters[].wallet` + `economy.hq_pool` vereinheitlicht.
   - Roster-Standard für TEMP/Koop auf `characters[]` gezogen; Legacy-Aliase nur noch als Importpfad markiert.

2. **Toolkit präzisiert (`systems/toolkit-gpt-spielleiter.md`)**
   - Koop-Auszahlungszeile auf `characters[].wallet` umgestellt.
   - Load-Standardflags von `party.characters[].psi_buffer` auf `characters[].psi_buffer` angepasst.

3. **Guard ergänzt (`tools/lint_runtime.py`)**
   - Neuer Check `check_wallet_roster_ssot_in_runtime_guides()` prüft
     `core/sl-referenz.md` und `systems/toolkit-gpt-spielleiter.md` auf
     verbotene Rückfall-Tokens (`economy.wallets{}`, `economy.credits`, `party.characters[]`).
   - Check in `main()` eingebunden (läuft damit im Pflicht-Smoke automatisch mit).

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
