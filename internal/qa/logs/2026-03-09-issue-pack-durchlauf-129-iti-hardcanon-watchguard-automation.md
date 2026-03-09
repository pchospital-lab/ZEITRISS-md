---
title: "QA-Log 2026-03-09 – Durchlauf 129 (ITI-Hardcanon-Watchguard-Automation)"
status: "abgeschlossen"
run_id: "zr-020-d129"
---

# Kontext

Die inhaltliche Harmonisierung des ITI-Hauskanons (Durchläufe 122-128) ist
abgeschlossen, wurde bislang aber überwiegend über Text-Reviews und
Prozessartefakte abgesichert. Für anschlussfähige QA fehlte noch ein eigener,
automatisierter Driftguard im Pflicht-Smoke.

# Umgesetzte Änderungen

1. **Neuen ITI-Watchguard angelegt**
   - Datei: `tools/test_iti_hardcanon_watchguard.js`
   - Prüft die 8 kanonischen ITI-Hauptorte in den SSOT-Dokumenten
     (`meta/masterprompt_v6.md`, `systems/toolkit-gpt-spielleiter.md`,
     `core/sl-referenz.md`, `gameplay/kampagnenstruktur.md`,
     `gameplay/kampagnenuebersicht.md`).
   - Prüft Kernpersonal-Anker (`Renier`, `Mira`, `Lorian`, `Vargas`,
     `Narella`) in Runtime-SSOT-Dokumenten.
   - Liest aktive Slot-Dateien aus `master-index.json` und blockt bekannte
     Driftbegriffe (`Institut ... Interventionen`, `HQ-Ausbau`,
     `HQ-Ausbaustufen`, `Direkt weiterspringen (ohne HQ-Stop)`).
   - Erzwingt, dass Legacy-Aliase (`Gatehall`, `Research-Wing`,
     `Mission-Briefing-Pod`) nur in den erlaubten Alias-Bridge-Dokumenten
     auftauchen.

2. **Pflicht-Smoke erweitert**
   - Datei: `scripts/smoke.sh`
   - `node tools/test_iti_hardcanon_watchguard.js` + Token-Grep
     `iti-hardcanon-watchguard-ok` als fester Schritt aufgenommen.

3. **Prozessnachführung aktualisiert**
   - Fahrplan ergänzt:
     `internal/qa/plans/issue-pack-durchlauf-129-iti-hardcanon-watchguard-automation.md`.
   - Known-Issue/Statusmatrix für ZR-020 evidenzseitig nachgezogen.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process`

# Bewertung

Der ITI-Hauskanon ist jetzt nicht nur textlich harmonisiert, sondern als
Smoke-Pflichtguard automatisiert. Das reduziert das Risiko, dass Ortsatlas,
Kernpersonal oder alte HQ-/Alias-Begriffe in aktiven Runtime-Slots unbemerkt
zurückdriften.
