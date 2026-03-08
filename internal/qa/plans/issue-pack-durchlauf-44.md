---
title: "Issue-Pack Fahrplan – Durchlauf 44"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 44

Quelle: Verständlichkeits-Follow-up zum Hopper/Leaver-Modell ("Kanon pro aktiver Runde").

## Ziel

Die Regeln so formulieren, dass Spieler ohne Branch-Denken direkt verstehen:
- Der eigene aktive Host-Save ist immer der aktuelle Hauptfortschritt.
- Erst beim späteren Merge werden fremde Kampagnenpfade als Import behandelt.

## Scope dieses Durchlaufs

- Vereinfachte Formulierungen in `README.md`, `meta/masterprompt_v6.md`,
  `core/sl-referenz.md`, `systems/gameflow/speicher-fortsetzung.md`.
- Mid-Episode-3/2-Abschnitt auf "beide Pfade spielbar" + "Kanon pro Chat" umstellen.
- Pflicht-Smoke als Regression-Gate.

## Exit-Kriterium

- Side-Run-Sprache ist für den Standardfall nicht mehr missverständlich.
- Host-SSOT bleibt technisch unverändert und klar benannt.
- Pflicht-Smoke bleibt grün.
