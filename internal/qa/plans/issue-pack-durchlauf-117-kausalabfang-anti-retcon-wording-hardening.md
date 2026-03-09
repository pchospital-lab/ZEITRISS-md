---
title: "Issue-Pack Durchlauf 117 – Kausalabfang Anti-Retcon-Wording-Hardening"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-116-kausalabfang-roster-echo-anchor-hardening.md"
---

# Ziel

Das Upload-Paket fordert klar, dass Kausalabfang **kein universeller Retcon**
sein darf. Diese Leitplanke war bereits sinngemäß enthalten, aber noch nicht in
allen Kernmodulen explizit genug als eigener Wortlautanker geführt.

1. Anti-Retcon-Leitplanke in den fünf Kausalabfang-Kernmodulen explizit und
   parallel verankern.
2. Watchguard so anpassen, dass künftig ein positiver Anti-Retcon-Anker geprüft
   wird (statt nur eines driftigen Negativchecks).
3. QA-/Prozessartefakte für Anschlusslauf 117 fortschreiben.

# Checkliste

- [x] `core/spieler-handbuch.md` enthält beim Kausalabfang explizit „kein universelles Retcon-Werkzeug“.
- [x] `core/sl-referenz.md` enthält denselben Anti-Retcon-Anker im Standardmodul.
- [x] `systems/toolkit-gpt-spielleiter.md` führt „universelles Retcon-Werkzeug“ in den Guard-Bullets.
- [x] `meta/masterprompt_v6.md` trägt denselben Anti-Retcon-Anker im Cleanup-Block.
- [x] `characters/ausruestung-cyberware.md` führt den Anti-Retcon-Anker im Gadget-Flavor.
- [x] `tools/test_kausalabfang_watchguard.js` prüft Anti-Retcon als positiven Pflichtanker.
- [x] `internal/qa/process/known-issues.md` um Evidenzlauf 117 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 117 + Watchpoint ergänzt.
- [x] QA-Log für Durchlauf 117 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 117 macht die Anti-Retcon-Leitplanke explizit und maschinenprüfbar:
Kausalabfang bleibt als enges ITI-Cleanup-Protokoll sichtbar von jeder Form
universeller Zeit-Rücknahme getrennt.
