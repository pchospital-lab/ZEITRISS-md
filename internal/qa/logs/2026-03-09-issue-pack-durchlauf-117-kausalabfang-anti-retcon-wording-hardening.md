---
title: "QA-Log 2026-03-09 – Durchlauf 117 (Kausalabfang Anti-Retcon-Wording-Hardening)"
status: "abgeschlossen"
run_id: "zr-019-d117"
---

# Kontext

Nach den Läufen 108–116 war die Kausalabfang-Regel technisch weitgehend dicht,
die Upload-Leitplanke „kein universeller Retcon“ war aber nicht in allen fünf
Kernmodulen als expliziter Wortlautanker präsent.

# Umgesetzte Änderungen

1. **SSOT-Wording (Anti-Retcon) parallelisiert**
   - Dateien:
     - `core/spieler-handbuch.md`
     - `core/sl-referenz.md`
     - `systems/toolkit-gpt-spielleiter.md`
     - `meta/masterprompt_v6.md`
     - `characters/ausruestung-cyberware.md`
   - Kausalabfang führt nun konsistent den expliziten Anker
     **„kein universelles Retcon-Werkzeug“** (bzw. äquivalente Formulierung)
     zusätzlich zu den bestehenden Kampf-/Infra-/Sperrenregeln.

2. **Watchguard auf positiven Anti-Retcon-Check umgestellt**
   - Datei: `tools/test_kausalabfang_watchguard.js`
   - Neuer Pflichtregex erzwingt Anti-Retcon-Wording in allen Kernmodulen;
     der frühere rein negative Driftcheck wurde entfernt.

3. **Prozessdoku synchronisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Evidenzlauf 117 ergänzt; neuer Watchpoint zum expliziten Anti-Retcon-Anker
     ergänzt.

4. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-117-kausalabfang-anti-retcon-wording-hardening.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün** (inkl. `kausalabfang-watchguard-ok`)
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Die Upload-Kernaussage „Cleanup statt universeller Retcon“ ist jetzt in allen
relevanten SSOT-Texten explizit und wird im Pflicht-Smoke aktiv erzwungen.
