---
title: "QA-Log 2026-03-09 – Durchlauf 121 (Kausalabfang Kodex-Blocksatz Watchguard-Hardening)"
status: "abgeschlossen"
run_id: "zr-019-d121"
---

# Kontext

Der Upload "Never happened" führt einen kompakten Kodex-Satzbau mit festen
Defaults. Nach Durchlauf 120 war der Kern schon breit verankert, aber im
Masterprompt stand bei der Zulässigkeitsmeldung noch die kurze Variante
(`Kodex: Ziel nicht zulässig.`) statt des vollen Blocksatzes aus dem Toolkit.

# Umgesetzte Änderungen

1. **Masterprompt auf Toolkit-Blocksatz gehoben**
   - Datei: `meta/masterprompt_v6.md`
   - Kodex-Default harmonisiert zu:
     `Kodex: Ziel nicht zulässig. Boss-/ITI-/Zivilstatus blockiert.`

2. **Watchguard um Kodex-Feinanker gehärtet**
   - Datei: `tools/test_kausalabfang_watchguard.js`
   - `hardeningRegex` erweitert um Pflichtchecks für:
     - `Kodex: ITI-Abfangfenster steht.`
     - `Kodex: Ziel nicht zulässig ...` (inkl. Blocksatz)
     - `Kodex: Uplink fehlt. Marker bleibt ohne Vollzug.`

3. **Prozessartefakte synchronisiert**
   - Neuer Fahrplan: `internal/qa/plans/issue-pack-durchlauf-121-kausalabfang-kodex-blocksatz-watchguard-hardening.md`
   - Prozessseiten aktualisiert: `internal/qa/process/known-issues.md` und
     `internal/qa/process/continuity-redesign-statusmatrix.md`.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün** (inkl. `kausalabfang-watchguard-ok`)
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Der Kodex-Satzbau ist nun zwischen Toolkit und Masterprompt vollständig
synchron, und die verbliebenen Defaults sind als strikte Hardening-Guards im
Pflicht-Smoke abgesichert.
