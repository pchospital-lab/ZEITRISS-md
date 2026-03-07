---
title: "Issue-Pack Fahrplan – Durchlauf 33"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 33

Quelle: Fortsetzung ZR-016 mit Fokus auf Issue 5 (Compliance-Reste) und
Issue 6 (Drift-Guard gegen Rückfall) aus `uploads/ZEITRISS_codex_issue_pack.md`.

## Ziel

Den Runtime-Startflow endgültig ohne sichtbaren Compliance-Hinweis führen und
einen automatischen Guard ergänzen, der einen Rückfall in `runtime.js`
(früherer Hinweistext/Toast) sofort im Pflicht-Smoke meldet.

## Scope dieses Durchlaufs

- `runtime.js`
- `tools/lint_runtime.py`
- QA-Nachführung: Log + Known-Issues-Update

## Nicht im Scope

- Vollständige Entfernung alter Kompatibilitätsfelder aus Legacy-Saves.
- Änderungen am Save-Importpfad für `compliance_shown_today`.
- Umbau von Missions-/Debrief-Logik.

## Exit-Kriterium für Durchlauf 33

- `show_compliance_once()` bleibt leerer Kompatibilitäts-Hook ohne Ausgabe.
- Runtime-Flag-Übersicht zeigt keinen offenen/gesetzten Compliance-Zustand mehr,
  sondern den inaktiven Hook-Status.
- Lint enthält einen Guard, der Compliance-Hinweis/Toast in `runtime.js`
  erkennt und blockiert.
- `bash scripts/smoke.sh` läuft vollständig grün.
