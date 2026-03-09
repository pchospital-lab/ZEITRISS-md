---
title: "Issue-Pack Durchlauf 123 – ITI-Kernrollen-ID & Echo-Konvention nachziehen"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_ITI_mmo_konsistenz_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-122-iti-mmo-hardcanon-ssot-harmonisierung.md"
---

# Ziel

Den offenen Kontinuitäts-Feinschliff aus dem ITI/MMO-Review nachziehen: feste
ITI-Kernrollen-IDs und Echo-Kurzform in Runtime-Modulen explizit als
Standard verankern, ohne neues Save-Subsystem.

# Checkliste

- [x] ITI-Kernrollen-IDs in `systems/gameflow/speicher-fortsetzung.md` ergänzt.
- [x] Echo-Kurzformat `ITI-ID :: Status/Hook` im Kontinuitätsmodell ergänzt.
- [x] Toolkit-Abschnitt zu NPC-Kontinuität um feste ITI-ID-Konvention erweitert.
- [x] QA-Log für Durchlauf 123 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 123 ergänzt den ITI-Hardcanon um einen schlanken
Kontinuitäts-Anker: feste ITI-IDs + Echo-Kurzform auf bestehendem
`continuity`-Schema, ohne Save-Aufblähung oder neue Runtime-Mechanik.
