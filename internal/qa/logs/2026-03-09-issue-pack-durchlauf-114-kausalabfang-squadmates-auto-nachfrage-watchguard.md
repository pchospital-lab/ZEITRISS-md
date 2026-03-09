---
title: "QA-Log 2026-03-09 – Durchlauf 114 (Kausalabfang Squadmates/Auto-Nachfrage-Watchguard)"
status: "abgeschlossen"
run_id: "zr-019-d114"
---

# Kontext

Die Läufe 108–113 haben den Kausalabfang bereits in SSOT + Smoke verankert.
Beim Nachcheck gegen das Upload-Paket blieb offen, dass zwei bestehende
Leitplanken im Guard noch nicht explizit erzwungen waren:

1. harte **Squadmates-Sperre** als separater Pflichtanker,
2. KI-Flow **unbenannt automatisch / benannt nachfragen** als strikter
   Ablaufanker in Toolkit + Masterprompt.

# Umgesetzte Änderungen

1. **Watchguard erweitert (Sperren + Ablauf)**
   - Datei: `tools/test_kausalabfang_watchguard.js`
   - Ergänzt:
     - `Squadmates` in den globalen Pflichtregexen über alle fünf Kernmodule.
     - zusätzlicher strikter Regex für den KI-Ablauf
       „Unbenannte Hostiles automatisch, benannte Ziele nachfragen".

2. **Prozessdoku synchronisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Evidenzlauf 114 dokumentiert und neuer Watchpoint für den
     Auto-/Nachfrage-Anker ergänzt.

3. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-114-kausalabfang-squadmates-auto-nachfrage-watchguard.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün** (inkl. `kausalabfang-watchguard-ok`)
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Die Kausalabfang-Automation deckt jetzt auch die letzten operativen Upload-
Leitplanken explizit ab. Damit sinkt das Risiko, dass Folgeedits die
Squadmates-Sperre oder den named-vs-unnamed-Flow stillschweigend aufweichen.
