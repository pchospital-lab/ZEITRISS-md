---
title: "Issue-Pack Durchlauf 109 – Kausalabfang-Watchguard Automation"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_never_happened_gadget_pack.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-108-never-happened-kausalabfang-integration.md"
---

# Ziel

Die in Durchlauf 108 verankerte Kausalabfang-Minimalregel als automatisierten
Pflicht-Guard im Smoke absichern, damit Cleanup-Drift früh und reproduzierbar
auffällt.

1. Watchguard-Test für die fünf betroffenen SSOT-Module ergänzen.
2. Smoke-Pipeline um den neuen Check erweitern.
3. Prozessdoku um Evidenzlauf 109 + Anschluss-Watchpoint ergänzen.

# Checkliste

- [x] `tools/test_kausalabfang_watchguard.js` angelegt (Pflichtanker + Driftblocker).
- [x] `scripts/smoke.sh` um den Kausalabfang-Watchguard ergänzt.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 109 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 109 ergänzt.
- [x] QA-Log für Durchlauf 109 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 109 macht den Kausalabfang-Block resilient gegen Textdrift:
Reihenfolge, 0-LP-Gate und Verbotsmatrix werden jetzt als fester Smoke-Guard
auf WS-Kerntext-Ebene geprüft.
