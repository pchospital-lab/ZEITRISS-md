---
title: "Issue-Pack Durchlauf 129 – ITI-Hardcanon-Watchguard automatisieren"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_ITI_mmo_konsistenz_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-128-iti-alias-drift-runtime-stub.md"
---

# Ziel

Den ITI-Hauskanon nach den inhaltlichen Harmonisierungsläufen mit einem
Pflicht-Watchguard im Smoke absichern, damit Ortsatlas, Kernpersonal und
bekannte Driftbegriffe automatisch auf Regression geprüft werden.

# Checkliste

- [x] Guard-Scope auf aktive Runtime-Slots aus `master-index.json` ausgerichtet.
- [x] Neuer Tool-Check `tools/test_iti_hardcanon_watchguard.js` erstellt.
- [x] Pflichtanker geprüft: 8 Hauptorte in SSOT-Kerntexten.
- [x] Pflichtanker geprüft: Kernpersonal (Renier, Mira, Lorian, Vargas, Narella) in Runtime-SSOT-Dokumenten.
- [x] Driftbegriffe in Slot-Dateien geblockt (`Institut ... Interventionen`, `HQ-Ausbau`, `HQ-Ausbaustufen`, `Direkt weiterspringen (ohne HQ-Stop)`).
- [x] Legacy-Aliase (`Gatehall`, `Research-Wing`, `Mission-Briefing-Pod`) außerhalb der expliziten Alias-Bridge verhindert.
- [x] `scripts/smoke.sh` um den neuen Watchguard ergänzt.
- [x] QA-Log für Durchlauf 129 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 129 überführt den ITI-Hauskanon von rein dokumentarischer Evidenz in
verbindliche Guard-Automation im Pflicht-Smoke. Damit wird Restdrift künftig
früh erkannt, bevor Parallelkanon erneut in aktive Slots gelangt.
