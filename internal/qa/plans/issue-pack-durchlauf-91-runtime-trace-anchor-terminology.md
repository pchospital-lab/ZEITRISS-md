---
title: "Issue-Pack Durchlauf 91 – Runtime-Trace Anchor-Terminologie"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-90-merge-conflict-contract-alignment.md"
---

# Ziel

Restdrift in Runtime-Trace-/Audit-Terminologie (Host-Wording) auf
Session-Anker-Semantik harmonisieren, damit Laufzeitmeldungen, SL-Referenz und
Testtexte denselben Kontinuitätsvertrag sprechen.

1. Runtime-Trace-Labels und Merge-Notizen auf Session-Anker umstellen.
2. SL-Referenz und betroffene Testtexte nachziehen.
3. Pflichtchecks erneut ausführen und Anschlusslauf dokumentieren.

# Checkliste

- [x] `runtime.js` nutzt Session-Anker-Wording in Merge-Notizen (`Session-Anker-Vorrang`) und UI-Override-Trace (`ui_session_anchor_override`).
- [x] Economy-Audit-Bandgrund nutzt `session_anchor_level` statt `host_level`.
- [x] `core/sl-referenz.md` referenziert den neuen Trace-Namen.
- [x] `tools/test_economy_merge.js` verwendet Session-Anker-Fehltexte.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 91 schließt Terminologie-Restdrift in der Runtime-Schicht. Damit sind
Logs/Trace-Events, Referenzdoku und Tests konsistent zur Session-Anker-
Semantik des Kontinuitäts-Redesigns.
