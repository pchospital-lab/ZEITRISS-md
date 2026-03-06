---
title: "Issue-Pack Fahrplan – Durchlauf 08"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 08

Quelle: `uploads/ZEITRISS_codex_issue_pack.md`

## Ziel
Durchlauf 07 fachlich zurücknehmen, damit der bestehende Spiel-Flow unverändert
bleibt und keine zweite, konkurrierende Pacing-Logik neben dem laufenden Modus-Set
(`precision|klassik|verbose`) entsteht.

## Scope dieses Durchlaufs

- Rückbau der in Durchlauf 07 eingeführten `output_pace`-Regeln in den
  Runtime-Quellen (`meta/masterprompt_v6.md`, `core/spieler-handbuch.md`).
- Dokumentation der Verwerfungsentscheidung im QA-Log.
- Fortschreibung von ZR-016 mit Verweis auf Durchlauf 08.

## Nicht im Scope (bewusst verschoben)

- Neue Pacing-Features oder zusätzliche Presets.
- Änderungen am bestehenden Gameflow (Szenenrhythmus, Debrief-Pflichten,
  Kodex-Rollenverhalten).

## Exit-Kriterium für Durchlauf 08

- Keine neue `compact|normal|cinematic`-Pacing-SSOT in den Runtime-Quellen.
- Bestehender Flow/Modusbetrieb bleibt unverändert.
- Pflichtcheck `bash scripts/smoke.sh` ist grün.
