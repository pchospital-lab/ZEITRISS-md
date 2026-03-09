---
title: "QA-Log 2026-03-09 – Durchlauf 112 (Kausalabfang Abfangfenster-Hardening)"
status: "abgeschlossen"
run_id: "zr-019-d112"
---

# Kontext

Die Läufe 108–111 haben Kausalabfang als Cleanup-Protokoll inkl. Sperren,
Echo-/Kodex-Hardening und Infra-Guards abgesichert. Im Upload-Paket blieb als
präziser Leitplankenpunkt noch das **enge ITI-Abfangfenster**
("Sekunden bis wenige Minuten").

# Umgesetzte Änderungen

1. **SSOT-Zeitfenster verankert**
   - Dateien:
     - `core/spieler-handbuch.md`
     - `systems/toolkit-gpt-spielleiter.md`
     - `meta/masterprompt_v6.md`
   - Ergänzt wurde in allen drei Modulen: Kausalabfang nur im engen
     ITI-Zeitfenster **Sekunden bis wenige Minuten** vor Einsatzkontakt.

2. **Watchguard erweitert**
   - Datei: `tools/test_kausalabfang_watchguard.js`
   - Neuer Pflichtanker-Regex prüft das Zeitfenster-Wording
     (`Sekunden bis wenige Minuten` bzw. `wenige Minuten`).

3. **Prozessdoku synchronisiert**
   - Dateien:
     - `internal/qa/process/known-issues.md`
     - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Evidenzlauf 112 + Watchpoint für das enge Abfangfenster ergänzt.

4. **Fahrplanlauf dokumentiert**
   - Datei:
     `internal/qa/plans/issue-pack-durchlauf-112-kausalabfang-abfangfenster-hardening.md`

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün** (inkl. `kausalabfang-watchguard-ok`)
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Kausalabfang ist nun nicht nur als Reihenfolge-/Sperrlogik stabilisiert,
sondern auch in seiner zeitlichen Reichweite hart begrenzt. Dadurch sinkt das
Risiko, dass spätere Formulierungen ungewollt universelle Retcon-Lesarten
öffnen.
