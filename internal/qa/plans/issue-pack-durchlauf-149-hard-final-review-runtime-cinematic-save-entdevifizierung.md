---
title: "Issue-Pack Durchlauf 149 – Hard Final Review: Runtime-Entdevifizierung (Cinematic + Save-Referenz)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Runtime/QA
---

# Ziel

Verbleibende Hard-Final-Review-Risiken im aktiven Runtime-Stack reduzieren:

1. `systems/gameflow/cinematic-start.md` auf klaren Runtime-Default fokussieren.
2. Optionales Stilmaterial nur noch als nicht-kanonische Inszenierungsoption führen.
3. `systems/gameflow/speicher-fortsetzung.md` von explizitem QA-Test-Wording säubern.

# Arbeitspaket

- [x] Cineastik-Modul hinter dem Defaultpfad stark kürzen (Runtime-first).
- [x] Optional-Varianten als reine Stilhinweise markieren, ohne Regelstatus.
- [x] Save-Modul: QA-Testbezug entfernen, Legacy-Referenz neutral formulieren.
- [x] Prozessspur in `known-issues.md` fortschreiben.
- [x] Pflicht-Smoke ausführen.

# QA-Checkliste

- [x] `bash scripts/smoke.sh`
- [x] Spot-Check auf Restdrift (`internal/qa`, QA-Test-Wording) in geänderten Runtime-Dateien.

# Anschluss / Watchpoints

- Director-Layer bleibt in Masterprompt/SL-Referenz/Toolkit synchron.
- Falls weitere Stilmodule produktiv geladen bleiben, dieselbe Runtime-first-Logik anwenden.
