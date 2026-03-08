---
title: "Issue-Pack Durchlauf 86 – WS-Session-Anker-Restdrift"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-85-continuity-fixture-wording-anchor.md"
---

# Ziel

Verbliebene Host-Semantik in WS-Kerndokumenten auf Session-Anker-/Kontinuitäts-
Semantik nachziehen, damit Spieler-Handbuch und Core-Modul dieselbe Sprache wie
Masterprompt und Save/Load-SSOT sprechen.

1. Host-Formulierungen in `core/spieler-handbuch.md` ersetzen.
2. Host-Formulierungen in `core/zeitriss-core.md` ersetzen.
3. Pflichtchecks erneut laufen lassen und Anschlusslauf dokumentieren.

# Checkliste

- [x] `core/spieler-handbuch.md` auf Session-Anker-Semantik harmonisiert.
- [x] `core/zeitriss-core.md` auf Session-Anker-Semantik harmonisiert.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 86 schließt die Restdrift in den WS-Kerndokumenten: Gruppenspiel,
Merge-Lesart und Save-Erläuterung verwenden jetzt konsistent Session-Anker +
persönliche Charakter-Autorität statt Host-SSOT-Wording.
