---
title: "Issue-Pack Fahrplan – Durchlauf 30"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 30

Quelle: Fortsetzung ZR-016 mit Fokus auf verbleibende Wallet-/Roster-Drifts in Runtime-Leittexten.

## Ziel

Die Runtime-Leitplanken (SL-Referenz + Toolkit) sollen das v7-Zielmodell ohne
aktive Legacy-Pfade beschreiben:
- Koop-Auszahlungen über `characters[].wallet` statt `economy.wallets{}`,
- Team-Roster über `characters[]` statt `party.characters[]` als Standard,
- SaveGuard-Kompaktbaum auf `v/.../characters[]/.../arc` statt v6-Pfaden,
- kanonischer HQ-Kontostand als `economy.hq_pool`.

## Scope dieses Durchlaufs

- `core/sl-referenz.md`
- `systems/toolkit-gpt-spielleiter.md`
- `tools/lint_runtime.py` (Guard gegen erneute v6-Wallet-/Roster-Drifts in den beiden Leitmodulen)
- QA-Nachführung: Log + Known-Issues-Update

## Nicht im Scope

- Laufzeit-Umbau in `runtime.js`.
- Migration alter Schema-Dateien oder Legacy-Importpfade.
- Rebalancing von Rewards/CU-Werten.

## Exit-Kriterium für Durchlauf 30

- SL-Referenz und Toolkit beschreiben den aktiven Koop-Standard mit
  `characters[].wallet` + `economy.hq_pool`.
- SaveGuard-Kompaktbaum in der SL-Referenz zeigt v7-Zielpfade (`v`, `characters[]`, `arc`).
- Neuer Lint-Guard schlägt bei Rückfall auf `economy.wallets{}`,
  `economy.credits` oder `party.characters[]` in den Leitmodulen fehl.
- `bash scripts/smoke.sh` läuft grün.
