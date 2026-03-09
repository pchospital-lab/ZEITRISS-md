---
title: "QA-Log 2026-03-09 – Durchlauf 120 (Kausalabfang Festnahme-statt-Löschung Hardening)"
status: "abgeschlossen"
run_id: "zr-019-d120"
---

# Kontext

Der Upload-Thread „Never happened" fordert den Marker als ITI-Cleanup-Routine
mit klarer Haltung **Festnahme statt Löschung**. Nach den Läufen 108–118 waren
Regelanker und Guarding bereits breit vorhanden, aber das Leitmotiv war noch
nicht in allen Kernmodulen als expliziter Satz gesetzt.

# Umgesetzte Änderungen

1. **Leitmotiv in den fünf Kernmodulen nachgezogen**
   - Dateien:
     - `core/spieler-handbuch.md`
     - `core/sl-referenz.md`
     - `systems/toolkit-gpt-spielleiter.md`
     - `meta/masterprompt_v6.md`
     - `characters/ausruestung-cyberware.md`
   - Ergänzt wurde je ein expliziter Anker mit der Formulierung
     **„Festnahme statt Löschung"**, parallel zum bereits vorhandenen
     Anti-Retcon-/Anti-Kampf-Wording.

2. **Watchguard gehärtet**
   - Datei: `tools/test_kausalabfang_watchguard.js`
   - `mustHaveRegex` erweitert um positiven Pflichtcheck
     `/Festnahme\s+statt\s+Löschung/i` über alle fünf Kernmodule.

3. **Prozessartefakte synchronisiert**
   - Neuer Fahrplan: `internal/qa/plans/issue-pack-durchlauf-120-kausalabfang-festnahme-statt-loeschung-hardening.md`
   - Prozessseiten aktualisiert: `internal/qa/process/known-issues.md` und
     `internal/qa/process/continuity-redesign-statusmatrix.md`.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün** (inkl. `kausalabfang-watchguard-ok`)
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Der Kausalabfang bleibt weiterhin streng als ITI-Cleanup begrenzt; zusätzlich
ist die gewünschte Leitmotiv-Sprache nun SSOT-weit explizit und CI-seitig
hart abgesichert.
