---
title: "Issue-Pack Durchlauf 81 – Kontinuitäts-Redesign (Session-Anker + Multi-Load)"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "uploads/ZEITRISS_continuity_save_redesign.md"
  statusmatrix: "internal/qa/process/known-issues.md"
---

# Ziel

Das Kontinuitäts-Redesign aus dem Upload-Paket in die SSOT-Dokumente
überführen, ohne die mechanische Stabilität des HQ-DeepSave aufzugeben.

1. Host-SSOT-Sprache auf Session-Anker-Semantik umstellen.
2. `continuity`-Kapsel und Pflicht-Recap (`Kontinuitätsrückblick`) in den
   kanonischen Save-/Load-Texten verankern.
3. Core-Split-Kanon über `continuity.split.family_id` dokumentieren.
4. Charakter-Dedupe als Rejoin-/Kontinuitätskonflikt statt Hard-Blocker
   nachziehen.
5. Pflicht-Smoke laufen lassen und QA-Anschluss dokumentieren.

# Checkliste

- [x] README auf Session-Anker-/Kontinuitätslogik gehoben.
- [x] Masterprompt-Schema um `continuity`-Block ergänzt.
- [x] Save-/Load-SSOT (`speicher-fortsetzung.md`) auf neue Goldregel umgestellt.
- [x] SL-Referenz (`core/sl-referenz.md`) auf Rejoin-/Konvergenzregeln harmonisiert.
- [x] Pflicht-Smoke ausgeführt.

# Abschluss

Durchlauf 81 verschiebt die Load-Philosophie auf Kontinuitätssynthese
(Session-Anker + persönliche Wahrheit + Echo-Fortwirkung), behält aber die
mechanische Stabilität (HQ-Save-Invariante, Px-Guard, Allowlist-Imports) bei.
