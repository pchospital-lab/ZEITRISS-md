---
title: "Issue-Pack Durchlauf 88 – Anchor-Template + Toolkit-Restdrift"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-87-continuity-conflict-structure.md"
---

# Ziel

Verbliebene Host-Terminologie in Save-Template-Beispielen und Runtime-Spiegeltexten
auf die Session-Anker-Semantik nachziehen, damit SSOT, Masterprompt und Toolkit
im Anschluss an das Kontinuitäts-Redesign dieselbe Sprache sprechen.

1. `HOST-main` in den kanonischen Save-Beispielen auf `ANCHOR-main` harmonisieren.
2. Toolkit-Hinweise zu Wallet-/Gruppenimporten von Host- auf Session-Anker-Wording umstellen.
3. Pflichtchecks erneut laufen lassen und Anschlusslauf dokumentieren.

# Checkliste

- [x] `meta/masterprompt_v6.md` nutzt im v7-Template `branch_id: ANCHOR-main`.
- [x] `systems/gameflow/speicher-fortsetzung.md` nutzt im v7-Exportbeispiel `branch_id: ANCHOR-main`.
- [x] `systems/toolkit-gpt-spielleiter.md` auf Session-Anker-Wording harmonisiert (Wallet-/Gruppenimport).
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.

# Abschluss

Durchlauf 88 schließt verbleibende Begriffsdrift in den letzten
Template-/Toolkit-Stellen: kanonische Save-Beispiele und Runtime-Spiegel nutzen
jetzt konsistent die Session-Anker-Semantik.
