---
title: "Issue-Pack Durchlauf 92 – Runtime-Note-Wording Cleanup"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-91-runtime-trace-anchor-terminology.md"
---

# Ziel

Verbleibende Host-Formulierungen in Runtime-Konfliktnotizen entfernen, damit
Load-/Merge-Hinweise und Testfixtures durchgehend Session-Anker-Semantik
verwenden.

1. Rest-Wording in `runtime.js` auf Session-Anker harmonisieren.
2. Betroffene Testdaten/-assertions im Economy-Merge-Test nachziehen.
3. Pflichtchecks erneut ausführen und Anschlusslauf dokumentieren.

# Checkliste

- [x] `runtime.js` verwendet in Merge-Konfliktnotizen kein Host-Wording mehr (`Wallet union`, Kampagnenzähler/-modus, Rift-Seeds).
- [x] `tools/test_economy_merge.js` nutzt neutrale Session-Anker-Benennung für Wallet-Name-Assertions.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 92 schließt die verbleibende Runtime-Textdrift in Konfliktnotizen.
Damit sind Laufzeittexte, Testpfad und QA-Dokumentation konsistent auf
Session-Anker ausgerichtet.
