---
title: "Issue-Pack Fahrplan – Durchlauf 39"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 39

Quelle: `uploads/ZEITRISS_v7_save_load_issue_pack.md` + Maintainer-Hinweis zum
Chat-only-Betrieb (OpenWebUI) mit Save/Load über explizites `!save` und JSON-Paste.

## Ziel

Save/Load-Pfad auf Chatbetrieb schärfen: Runtime-Snapshot-Komfort entkoppeln,
`!bogen` als lesbare Übersicht etablieren und QA-Anschluss für den nächsten
Durchlauf dokumentieren.

## Scope dieses Durchlaufs

- Wissensspeicher-/Prompt-Flow für Chatbetrieb (kein Runtime-only Pfad als Spielstandard)
- `systems/gameflow/speicher-fortsetzung.md` (Betriebsstandard + Bogen-Doku)
- `core/sl-referenz.md` (Command-Referenz synchronisieren)
- `README.md` (OpenWebUI-Warntext + `!bogen` Hinweis)
- Pflicht-Smoke unverändert als Regression-Check
- QA-Nachführung: Plan + Log + Known-Issues

## Nicht im Scope

- Vollständiger Branch-Protokoll-Umbau für parallele Core-Missionen.
- Tiefenrefactor der Save-Migration für alle Legacy-Fixtures.
- Neue UI-/Frontend-Komponenten.

## Exit-Kriterium für Durchlauf 39

- Save/Load-Standard ist klar als Chatpfad (`!save`, JSON-Paste; `Spiel laden` optional) dokumentiert.
- `!bogen` ist als lesbare Charakterbogen-Ansicht dokumentiert.
- Pflichtcheck `bash scripts/smoke.sh` ist grün.
- Prozessdoku ist auf den neuen Durchlauf referenziert.
