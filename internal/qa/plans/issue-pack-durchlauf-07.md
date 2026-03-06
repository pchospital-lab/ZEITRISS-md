---
title: "Issue-Pack Fahrplan – Durchlauf 07"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 07

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Den offenen Pacing-Block (Issue 11) als offiziellen Runtime-Standard verankern,
damit Core-/Rift-Missionen auch im Chatbetrieb kompakt spielbar bleiben.

## Scope dieses Durchlaufs

- C7 Pacing-/Token-Budget (P1, Teil 1)
  - `meta/masterprompt_v6.md`: `output_pace` als verbindliche Presets
    `compact|normal|cinematic` ausformulieren.
  - Ausgabevertrag auf Presets abbilden (Absatzdichte je Modus) bei gleichzeitiger
    Sicherung von Boss-/Debrief-/Save-Pflichten.
  - `core/spieler-handbuch.md`: Kompaktmodus als offizielles Preset im
    Schnellstart/Cheatsheet sichtbar machen.

## Nicht im Scope (bewusst verschoben)

- Toolkit-Feinschliff in `systems/toolkit-gpt-spielleiter.md`.
- Weitere Ton-/Lore-Themen (Issue 8/9/10).
- Zusätzliche Lint-Checks für `output_pace`-Werte.

## Exit-Kriterium für Durchlauf 07

- Masterprompt enthält klaren Preset-Vertrag für `compact|normal|cinematic`.
- Spieler-Handbuch beschreibt den Kompaktmodus als offiziellen Runtime-Modus.
- Pflichtcheck `bash scripts/smoke.sh` ist grün.
