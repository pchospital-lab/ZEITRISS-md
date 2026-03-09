---
title: "QA-Log 2026-03-09 – Durchlauf 118 (Kausalabfang Motiv-/Lagefenster-Hardening)"
status: "abgeschlossen"
run_id: "zr-019-d118"
---

# Kontext

Nach Durchlauf 117 war der Anti-Retcon-Anker explizit, aber die Upload-Formel
"nur solange Tatmotivation und Einsatzlage gleich bleiben" war noch nicht als
maschinenprüfbarer Kernanker durchgehend verankert.

# Umgesetzte Änderungen

1. **SSOT-Wording (Motiv-/Lagegrenze) parallelisiert**
   - Dateien:
     - `core/spieler-handbuch.md`
     - `core/sl-referenz.md`
     - `systems/toolkit-gpt-spielleiter.md`
     - `meta/masterprompt_v6.md`
     - `characters/ausruestung-cyberware.md`
   - Kausalabfang führt nun konsistent den Zusatzanker, dass der Abfang nur im
     engen Zeitfenster gilt, solange **Tatmotivation und Einsatzlage** des
     Zieles erkennbar gleich bleiben.

2. **Watchguard um Motiv-/Lage-Regex erweitert**
   - Datei: `tools/test_kausalabfang_watchguard.js`
   - Neuer Pflichtregex erzwingt den Doppelanker `Tatmotivation` +
     `Einsatzlage` über alle fünf Kernmodule.

3. **Prozessdoku synchronisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Evidenzlauf 118 ergänzt; neuer Watchpoint zur Motiv-/Lage-Grenze ergänzt.

4. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-118-kausalabfang-motivlage-window-hardening.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün** (inkl. `kausalabfang-watchguard-ok`)
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Der Kausalabfang bleibt jetzt nicht nur zeitlich, sondern auch kausal eng
geführt: kein universeller Retcon, kein Motivsprung, keine Lage-Neuschreibung.
