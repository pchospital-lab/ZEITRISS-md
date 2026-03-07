---
title: "Issue-Pack Fahrplan – Durchlauf 40"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 40

Quelle: Nachschärfung zu Durchlauf 39 aus Maintainer-Feedback (Chat-only Save/Load ohne Runtime-Semantik).

## Ziel

Verifizieren, dass alle WS-/Prompt-Texte den gleichen kanonischen Load-Pfad führen:
JSON-Paste als Primärtrigger, `Spiel laden` nur optional, keine missverständlichen Runtime-Hinweise.

## Scope dieses Durchlaufs

- Konsistenzprüfung in `meta/masterprompt_v6.md`, `systems/gameflow/speicher-fortsetzung.md`, `core/sl-referenz.md`, `README.md`
- Gegenprüfung auf widersprüchliche Begrifflichkeit in QA-/Prozessdoku
- Pflicht-Smoke als Regression-Gate

## Exit-Kriterium

- Kein Spielerpfad beschreibt `Spiel laden` mehr als Pflichtkommando.
- Keine Formulierung suggeriert Runtime-Speicher als Teil des Spielbetriebs.
- Pflicht-Smoke bleibt grün.
