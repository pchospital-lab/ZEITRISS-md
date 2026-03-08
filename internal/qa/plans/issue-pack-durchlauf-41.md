---
title: "Issue-Pack Fahrplan – Durchlauf 41"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 41

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Fokus: Issue 3, kanonische Branch-Grenzen).

## Ziel

Den Kanon für Split/Merge ohne Branch-Protokoll eindeutig festziehen:
- Split/Merge standardmäßig nur nach Episodenende für Rift-Ops.
- Parallele Core-Branches innerhalb derselben Episode explizit als nicht-kanonisch markieren.
- Gemischte Split-Pfade ohne Branch-Protokoll klar als Hausregel kennzeichnen.

## Scope dieses Durchlaufs

- Kanon-Hinweise in `meta/masterprompt_v6.md`, `systems/gameflow/speicher-fortsetzung.md`, `core/sl-referenz.md`, `README.md` synchronisieren.
- Hinweistext für nicht-kanonische Branch-Imports in der Save/Load-Doku verankern.
- Pflicht-Smoke als Regression-Gate.

## Exit-Kriterium

- Alle vier Leitquellen benennen denselben kanonischen Split/Merge-Pfad.
- Keine Quelle verkauft Core-Parallel-Branches mehr als Standard-Kampagnenpfad.
- Pflicht-Smoke bleibt grün.
