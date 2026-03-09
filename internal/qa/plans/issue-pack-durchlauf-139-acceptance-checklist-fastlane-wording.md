---
title: "Issue-Pack Durchlauf 139 – Acceptance-Checklist Fast-Lane/Wording Restfix"
version: 1.0.0
status: abgeschlossen
tags: [qa, onboarding, startvertrag]
---

# Ziel

Verbleibenden Onboarding-Restdrift in Referenztexten schließen: `solo schnell` in der Toolkit-Acceptance-Checkliste explizit als optionale Fast-Lane markieren und die Modulbenennung in der SL-Referenz auf den bereits demoteten Archetypen-Status harmonisieren.

## Scope

- `systems/toolkit-gpt-spielleiter.md`
- `core/sl-referenz.md`
- Prozessspur (`internal/qa/logs/`, `internal/qa/process/known-issues.md`)

## Checkliste

- [x] Toolkit-Checklisteneintrag `Spiel starten (solo schnell)` mit Fast-Lane-Optionalität präzisieren.
- [x] SL-Referenz-Modultabelle auf `Inspiration/Fallback-Archetypen` angleichen.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) ausführen.
- [x] Link-Lint für geänderte QA-/Referenzdateien ausführen.
- [x] Lauf in `known-issues.md` dokumentieren.
