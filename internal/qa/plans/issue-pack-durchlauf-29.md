---
title: "Issue-Pack Fahrplan – Durchlauf 29"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 29

Quelle: Fortsetzung ZR-016 nach Maintainer-Feedback zu Charakterbogen-/Fahrzeug-Konsistenz.

## Ziel

Den v7-Charakterbogen minimal, aber merge-fest vervollständigen:
- Story-History pro Charakter,
- persönlicher Carry + Quartier-Stash mit festen Obergrenzen,
- persistentes Epochenfahrzeug und optionales legendäres temporales Schiff,
- identische SSOT-Definition in Masterprompt, Save-Doku und SL-Referenz.

## Scope dieses Durchlaufs

- `meta/masterprompt_v6.md`
- `systems/gameflow/speicher-fortsetzung.md`
- `core/sl-referenz.md`
- `gameplay/kampagnenstruktur.md` (Quartier-Text ohne Regelwiderspruch)
- `tools/lint_runtime.py` (Guard auf neue Save-v7-Felder)
- QA-Nachführung: Log + Known-Issues-Update

## Nicht im Scope

- runtime.js-Umbau oder neue Serializer-Funktionen.
- Rebalancing von CU-/Loot-Tabellen.
- Vollständige Fahrzeug-Subsystem-Neuentwicklung.

## Exit-Kriterium für Durchlauf 29

- Save-v7-SSOT enthält in allen drei SSOT-Quellen dieselben neuen Charakterfelder.
- Epochenfahrzeug + optionales temporales Schiff sind als persistente Felder beschrieben.
- Carry/Quartier-Grenzen sind dokumentiert und split/merge-fest formuliert.
- `bash scripts/smoke.sh` läuft grün.
