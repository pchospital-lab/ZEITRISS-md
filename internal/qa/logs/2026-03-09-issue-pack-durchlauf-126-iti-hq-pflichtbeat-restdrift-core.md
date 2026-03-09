---
title: "QA-Log 2026-03-09 – Durchlauf 126 (ITI-HQ-Pflichtbeat-Restdrift Core)"
status: "abgeschlossen"
run_id: "zr-020-d126"
---

# Kontext

Nach den Durchläufen 122–125 blieb im aktiven Runtime-Slot
`core/zeitriss-core.md` ein Optionalpfad bestehen
(`Direkt weiterspringen (ohne HQ-Stop)`), der dem verpflichtenden HQ-Heimkehr-
Beat widerspricht.

# Umgesetzte Änderungen

1. **Core-Modul auf verpflichtenden Heimkehr-Beat konsolidiert**
   - Datei: `core/zeitriss-core.md`
   - Der Entscheidungspunkt nach Missionsende ist nun durchgehend als
     verpflichtender HQ-Beat formuliert; die direkte Skip-Option ohne HQ-Stopp
     wurde entfernt.

2. **Prozessartefakte ergänzt/aktualisiert**
   - Fahrplan ergänzt:
     `internal/qa/plans/issue-pack-durchlauf-126-iti-hq-pflichtbeat-restdrift-core.md`.
   - Known-Issue und Statusmatrix um Durchlauf 126/Evidenz erweitert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

# Bewertung

Der verbliebene Optionalpfad zum Überspringen der HQ-Rückkehr im aktiven Core-
Slot ist bereinigt. Damit bleibt der ITI-Hardcanon (verpflichtender Heimkehr-
Beat nach Mission/Load) auch im Lore-Kerntext konsistent.
