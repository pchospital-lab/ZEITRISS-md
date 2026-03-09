---
title: "QA-Log 2026-03-09 – Durchlauf 113 (Kausalabfang Kodex-Archivanker-Watchguard)"
status: "abgeschlossen"
run_id: "zr-019-d113"
---

# Kontext

Die Läufe 108–112 haben Kausalabfang als Cleanup-Protokoll inkl. Sperren,
Echo-/Kodex-Hardening, Infra-Guards und Abfangfenster stabilisiert. Aus dem
Upload-Paket blieb als konkrete Satzleitplanke noch der Kodex-Call
`Lokale Erinnerung driftet. Archivanker aktiv.`

# Umgesetzte Änderungen

1. **Kodex-Default in SSOT synchronisiert**
   - Dateien:
     - `systems/toolkit-gpt-spielleiter.md`
     - `meta/masterprompt_v6.md`
   - In beiden Modulen ergänzt: kurzer Kodex-Satz zum Memory-Drift-Fall
     (`Lokale Erinnerung driftet. Archivanker aktiv.`).

2. **Watchguard erweitert**
   - Datei: `tools/test_kausalabfang_watchguard.js`
   - Neuer Hardening-Regex verlangt den Archivanker-Satz in den strikten
     Kausalabfang-Dateien.

3. **Prozessdoku synchronisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Evidenzlauf 113 dokumentiert; Watchpoint für den Archivanker ergänzt.

4. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-113-kausalabfang-kodex-archivanker-watchguard.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün** (inkl. `kausalabfang-watchguard-ok`)
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Kausalabfang bleibt weiterhin als nüchterne ITI-Infra statt Zeitspektakel
lesbar. Der Memory-Drift/Archivanker-Satz ist jetzt explizit in SSOT und
Smoke-Guard verankert, wodurch Textdrift in Folgeläufen früher auffällt.
