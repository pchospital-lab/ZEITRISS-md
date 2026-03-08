---
title: "Issue-Pack Fahrplan – Durchlauf 43"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 43

Quelle: Praxisszenario „Hopper/Leaver in privaten OpenWebUI-Instanzen“ als Follow-up zu Durchlauf 42.

## Ziel

Die Betriebsrealität mit häufigem Host-Wechsel (nach nahezu jeder Core-Op-Mission)
sauber als Side-Run/Lobbymodell beschreiben, ohne den kanonischen Host-SSOT zu verwässern.

## Scope dieses Durchlaufs

- Klarstellung in `systems/gameflow/speicher-fortsetzung.md` (OpenWebUI-Lobbybetrieb).
- Konsistenzhinweise in `meta/masterprompt_v6.md`, `core/sl-referenz.md`, `README.md`.
- Pflicht-Smoke als Regression-Gate.

## Exit-Kriterium

- Host-Hopping, Leaver-Rejoin und Episodenfortschritt sind ohne Interpretationslücke dokumentiert.
- Es bleibt eindeutig: Kampagnenkanon kommt pro Chat nur vom aktiven Host-Save.
- Pflicht-Smoke bleibt grün.
