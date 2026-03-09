---
title: "Issue-Pack Durchlauf 125 – ITI-HQ-Ausbau-Restdrift im Core-Modul bereinigen"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_ITI_mmo_konsistenz_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-124-iti-hq-ausbau-restdrift-currency.md"
---

# Ziel

Den verbliebenen HQ-Ausbau-/Stufenbegriff im aktiven Core-Modul entfernen und
auf die etablierte ITI-Freigabe-/Lizenzlogik umstellen, damit der Hauskanon in
allen Runtime-Slots konsistent bleibt.

# Checkliste

- [x] Restfund per Repo-Scan validiert (`Ausbauten des HQ ... Zugangs-Stufen` in `core/zeitriss-core.md`).
- [x] `core/zeitriss-core.md` auf Freigaben-/Lizenzsprache ohne Ausbau-Mechanik umgestellt.
- [x] QA-Log für Durchlauf 125 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 125 schließt den letzten gefundenen HQ-Ausbau-/Stufenrest im Core-
Slot und hält damit den ITI-Hardcanon (feste Nullzeit-Anlage, Fortschritt über
Zugang/Lizenz/Freigabe statt Basisbau) durchgehend konsistent.
