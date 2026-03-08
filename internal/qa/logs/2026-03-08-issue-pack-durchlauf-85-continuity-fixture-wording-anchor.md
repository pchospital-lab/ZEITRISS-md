---
title: "QA-Log 2026-03-08 – Durchlauf 85 (Continuity-Fixture-Wording Session-Anker)"
status: "abgeschlossen"
run_id: "zr-018-d85"
---

# Kontext

Nach Durchlauf 84 war die technische Kontinuitätskapsel in Schema/Guards sauber,
aber einzelne Fixture-Texte und Branch-IDs nutzten noch Host-Formulierungen.
Das erzeugte semantische Drift zwischen SSOT-Regeln und QA-Beispielen.

# Umgesetzte Änderungen

1. **Branch-ID-Wording harmonisiert**
   - `internal/qa/fixtures/savegame_v7_split_3_2_merge.json`
   - `branch_id` von `HOST-HQ-ALPHA` auf `ANCHOR-HQ-ALPHA` umgestellt.

2. **Hinweistexte auf Session-Anker nachgezogen**
   - `internal/qa/fixtures/savegame_v7_merge_rift_pvp.json`
     - Notiztext: "Host-Save" → "Session-Anker" und "nur Charakterdaten" →
       "nur Allowlist-Felder".
   - `internal/qa/fixtures/savegame_v7_abort_resume.json`
     - Notiztext: "Host-geführt" → "Session-Anker-geführt".

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core systems meta/masterprompt_v6.md README.md internal/qa/plans internal/qa/logs`
   - Ergebnis: **grün**

# Bewertung

Die Fixture-Ebene reflektiert jetzt dieselbe Semantik wie Masterprompt,
Save/Load-SSOT und Guard-Tests: Session-Anker als Einstieg, Import über
Allowlist/Continuity statt Host-Totalüberschreibung.
