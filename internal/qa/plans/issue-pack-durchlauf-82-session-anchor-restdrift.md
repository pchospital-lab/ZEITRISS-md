---
title: "Issue-Pack Durchlauf 82 – Session-Anker Restdrift (Host-Begriffe)"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-81-continuity-redesign.md"
---

# Ziel

Restdrift nach Durchlauf 81 abbauen: verbliebene Host-SSOT-Formulierungen in
Save-/Load- und SL-Referenztexten auf Session-Anker-Semantik harmonisieren,
ohne an Invarianten oder Runtime-Verhalten zu drehen.

1. Host-Begriffe in SSOT-nahen Merge-/Audit-/Roster-Beschreibungen ersetzen.
2. Cross-Mode-Beispielpayload auf `anchor_value`/`anchor_wins` umstellen.
3. QA-Anschluss dokumentieren und Pflicht-Smoke erneut validieren.

# Checkliste

- [x] `systems/gameflow/speicher-fortsetzung.md` auf Session-Anker-Wording nachgezogen.
- [x] `meta/masterprompt_v6.md` Roster-Regel auf Session-Anker harmonisiert.
- [x] `core/sl-referenz.md` Save-/Wallet-/Roster-Texte auf Session-Anker umgestellt.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint für betroffene Dokumente ausgeführt.

# Abschluss

Durchlauf 82 schließt einen Sprach-/Semantikrest nach dem Kontinuitäts-Redesign:
Session-Anker ist jetzt konsistenter über Profile, Merge-Beispiele, Economy-Audit
und Referenz-Checklisten hinweg beschrieben.
