---
title: "Issue-Pack Durchlauf 124 – ITI-HQ-Ausbau-Restdrift in Currency bereinigen"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_ITI_mmo_konsistenz_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-123-iti-kernrollen-id-echo-konvention.md"
---

# Ziel

Den verbliebenen HQ-Ausbau-Begriff in einem aktiven Wissensspeicher-Modul
entfernen und auf die etablierte Zugangs-/Lizenzlogik umstellen, damit der
ITI-Hauskanon in allen Runtime-Slots konsistent bleibt.

# Checkliste

- [x] Restfund per Repo-Scan validiert (`HQ-Ausbau` in Runtime-Modulen).
- [x] `systems/currency/cu-waehrungssystem.md` auf HQ-Zugangsfreigaben/Lizenzen umgestellt.
- [x] QA-Log für Durchlauf 124 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 124 beseitigt den letzten aktiven HQ-Ausbau-Begriff im geladenen
Runtime-Kanon und schließt damit eine verbliebene ITI/MMO-Driftkante ohne neue
Mechanik ein.
