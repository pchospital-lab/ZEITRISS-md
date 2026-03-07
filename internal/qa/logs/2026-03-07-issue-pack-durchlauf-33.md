---
title: "QA-Log – Issue-Pack Durchlauf 33"
date: 2026-03-07
scope: "Compliance-Reste in Runtime-Startflow + Drift-Guard"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), Restpunkt aus Issue 5/6:
  Compliance-Hinweis war trotz SSOT-Hinweis auf „entfällt" noch als aktiver
  Runtime-Pfad/Statusformulierung sichtbar.

## Umsetzung in diesem Durchlauf

1. **Compliance-Hook stillgelegt (`runtime.js`)**
   - `show_compliance_once()` liefert jetzt nur noch `false` und erzeugt keine
     Runtime-Ausgabe (kein Hinweistext, kein HUD-Toast).
   - `sync_compliance_flags()` ist als no-op Kompatibilitätshook belassen
     (`return false`).
   - Runtime-Flag-Zusammenfassung benennt den Zustand nun als
     `Compliance-Hook inaktiv` statt „gezeigt/offen".

2. **Drift-Guard ergänzt (`tools/lint_runtime.py`)**
   - Neue Prüfung `check_runtime_compliance_hook_inactive()` liest `runtime.js`
     und schlägt fehl, falls wieder ein Hinweistext (`Compliance-Hinweis:`)
     oder direkte Ausgabe (`writeLine(...Compliance...)`,
     `hud_toast(...Compliance...)`) eingebaut wird.
   - Check ist in `main()` eingebunden und läuft automatisch im
     Pflicht-Smoke mit.

3. **Prozessnachführung (`internal/qa/process/known-issues.md`)**
   - ZR-016 um Durchlauf 33 (Plan + QA-Log) erweitert.

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
