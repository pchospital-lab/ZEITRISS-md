---
title: "QA-Log 2026-03-09 – Durchlauf 124 (ITI-HQ-Ausbau-Restdrift Currency)"
status: "abgeschlossen"
run_id: "zr-020-d124"
---

# Kontext

Die ITI/MMO-Harmonisierung (Durchläufe 122/123) war weitgehend abgeschlossen,
aber im Runtime-Slot `systems/currency/cu-waehrungssystem.md` blieb ein
formulierter Kosten-Sink mit `HQ-Ausbau` stehen.

# Umgesetzte Änderungen

1. **Currency-Modul von Ausbau- auf Freigabelogik umgestellt**
   - Datei: `systems/currency/cu-waehrungssystem.md`
   - In der High-Level-Ökonomie-Tabelle den Sink-Eintrag von `HQ-Ausbau` auf
     `HQ-Zugangsfreigaben/Lizenzen` aktualisiert.
   - Dadurch bleibt die Endgame-Ökonomie konsistent mit dem ITI-Hauskanon:
     Fortschritt im HQ über Rechte/Freigaben statt Basisbau.

2. **Prozessartefakte ergänzt**
   - Fahrplan ergänzt:
     `internal/qa/plans/issue-pack-durchlauf-124-iti-hq-ausbau-restdrift-currency.md`.
   - Known-Issue-Zeile und Statusmatrix-Evidenz auf Durchlauf 124 erweitert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

# Bewertung

Der letzte bekannte HQ-Ausbau-String in den aktiven Wissensspeicher-Modulen ist
bereinigt. Damit ist der ITI-Hardcanon (feste Nullzeit-Anlage, Fortschritt über
Freigaben/Lizenzen) nun auch im Currency-Slot durchgehend konsistent.
