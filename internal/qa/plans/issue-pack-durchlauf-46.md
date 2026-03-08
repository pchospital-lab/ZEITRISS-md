---
title: "Issue-Pack Fahrplan – Durchlauf 46"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 46

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` (Issue 2: OpenWebUI-Realität vs. Runtime-Komfort sauber trennen).

## Ziel

Chat-nativen Save/Load-Standard für OpenWebUI klar von optionalen
Runtime-Komfortfunktionen abgrenzen, damit im Wissensspeicher-Betrieb keine
falschen Erwartungen zu lokalen Snapshot-/Dateifunktionen entstehen.

## Scope dieses Durchlaufs

- `README.md`: explizite Betriebsgrenze „chat-nativ vs. runtime-only“ ergänzen.
- `systems/gameflow/speicher-fortsetzung.md`: Runtime-Hinweis beim OpenWebUI-
  Save/Load-Standard ergänzen.
- `core/spieler-handbuch.md`: Mini-Einsatzhandbuch/Befehle um denselben
  OpenWebUI-Hinweis ergänzen.
- `characters/hud-system.md`: HUD-Befehlstabelle für `load|suspend|resume|autosave hq`
  als runtime-only markieren.
- Pflicht-Smoke als Regression-Gate ausführen.

## Exit-Kriterium

- OpenWebUI-Standardpfad bleibt überall gleich (`!save` + JSON-Paste,
  optional `Spiel laden`).
- Runtime-only Komfortbefehle sind in den betroffenen Modulen klar als
  „Host-Runtime erforderlich“ markiert.
- Pflicht-Smoke bleibt grün.
