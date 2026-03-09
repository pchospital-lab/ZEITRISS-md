---
title: "Issue-Pack Durchlauf 107 – Physicality Watchguard Automation"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_npc_mmo_immersion_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-106-cinematic-physicality-wording-final-pass.md"
---

# Ziel

Die Physicality-Trennung (Linse/HUD vs. sichtbare HQ-Infrastruktur) als
Pflicht-Guard in den Smoke aufnehmen, damit Restdrift nicht nur manuell,
sondern automatisiert blockiert wird.

1. Einen gezielten Guard-Test für Toolkit, Cinematic-Start und Lore-Core
   ergänzen.
2. Smoke-Pipeline um den neuen Guard erweitern.
3. Prozessdoku um Evidenzlauf 107 + Anschluss-Watchpoint aktualisieren.

# Checkliste

- [x] `tools/test_physicality_watchguard.js` angelegt (Pflichtanker +
      Driftmuster-Blocker).
- [x] `scripts/smoke.sh` um den neuen Physicality-Guard ergänzt.
- [x] `internal/qa/process/known-issues.md` um Durchlauf 107 ergänzt.
- [x] `internal/qa/process/continuity-redesign-statusmatrix.md` um Evidenzlauf 107 ergänzt.
- [x] QA-Log für Durchlauf 107 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 107 verankert den Physicality-Guard jetzt dauerhaft im Pflicht-Smoke
und reduziert das Risiko, dass Hologramm-Default-Drift in Toolkit,
Cinematic-Start oder Lore-Core unbemerkt zurückkehrt.
