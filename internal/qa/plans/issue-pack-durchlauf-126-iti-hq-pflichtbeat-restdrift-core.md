---
title: "Issue-Pack Durchlauf 126 – ITI-HQ-Pflichtbeat-Restdrift im Core-Modul bereinigen"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_ITI_mmo_konsistenz_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-125-iti-hq-ausbau-restdrift-core.md"
---

# Ziel

Den verbliebenen Optionalpfad "Direkt weiterspringen (ohne HQ-Stop)" im aktiven
Core-Modul entfernen und den verpflichtenden HQ-Heimkehr-Beat eindeutig als
SSOT formulieren.

# Checkliste

- [x] Restfund per Repo-Scan validiert (`Direkt weiterspringen (ohne HQ-Stop)` in `core/zeitriss-core.md`).
- [x] `core/zeitriss-core.md` auf verpflichtenden HQ-Beat ohne Skip-Option umgestellt.
- [x] QA-Log für Durchlauf 126 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 126 schließt den letzten gefundenen Heimkehr-Rhythmus-Drift im
aktiven Core-Slot und hält damit den ITI-Hardcanon (Rückkehr als verpflichtender
Heimkehr-Beat) konsistent über Runtime-Module und Prozessartefakte.
