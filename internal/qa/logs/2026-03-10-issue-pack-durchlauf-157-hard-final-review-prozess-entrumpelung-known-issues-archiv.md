---
title: "Log – Durchlauf 157 (Hard-Final-Review Prozess-Entrümpelung / Known-Issues-Archiv)"
date: 2026-03-10
status: abgeschlossen
owner: codex
scope: Meta/Prozess
issue: ZR-021
---

## Kontext

Anschluss auf den offenen Task "QA-Übersicht weiter entrümpeln" aus
`internal/qa/process/hard-final-review-next-steps.md`.

## Umsetzung

- Die historische Durchlaufchronik 73–156 wurde aus
  `internal/qa/process/known-issues.md` ausgelagert.
- Neue Archivdatei angelegt:
  `internal/qa/process/archive/known-issues-durchlaufhistorie-73-156.md`.
- In `known-issues.md` wurde stattdessen ein kompakter Archiv-Verweis ergänzt,
  damit die operative Triage-Seite kurz und anschlussfähig bleibt.
- `internal/qa/process/hard-final-review-next-steps.md` wurde synchronisiert
  (Task 1 als umgesetzt markiert, Follow-up präzisiert).

## Ergebnis

- Prozessübersicht ist entrümpelt, Historie bleibt vollständig referenzierbar.
- Keine Runtime-Regeländerung, nur Meta-/Prozesspflege.

## Checks

- `bash scripts/smoke.sh` erfolgreich.
