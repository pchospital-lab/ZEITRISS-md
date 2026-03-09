---
title: "QA-Log 2026-03-09 – Durchlauf 125 (ITI-HQ-Ausbau-Restdrift Core)"
status: "abgeschlossen"
run_id: "zr-020-d125"
---

# Kontext

Nach den Durchläufen 122–124 blieb im aktiven Runtime-Slot
`core/zeitriss-core.md` ein einzelner Altbegriff zur HQ-Ausbau-/Stufenlogik
stehen (`Ausbauten des HQ ... Zugangs-Stufen`).

# Umgesetzte Änderungen

1. **Core-Modul von Ausbau- auf Freigabelogik umgestellt**
   - Datei: `core/zeitriss-core.md`
   - HQ-Abschnitt auf den kanonischen Pfad umgestellt: kein Ausbau-System,
     stattdessen Fortschritt über Zugangsfreigaben, Lizenzen und Vertrauen in
     bestehender ITI-Infrastruktur.

2. **Prozessartefakte ergänzt/aktualisiert**
   - Fahrplan ergänzt:
     `internal/qa/plans/issue-pack-durchlauf-125-iti-hq-ausbau-restdrift-core.md`.
   - Known-Issue und Statusmatrix um Durchlauf 125/Evidenz erweitert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

# Bewertung

Der verbliebene Ausbau-/Stufenrest im aktiven Core-Slot ist bereinigt. Damit
ist der ITI-Hardcanon (feste Nullzeit-Anlage, Fortschritt über Freigaben/
Lizenzen statt Basisbau) jetzt auch im Lore-Kerntext konsistent.
