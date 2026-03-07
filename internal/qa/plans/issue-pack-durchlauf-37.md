---
title: "Issue-Pack Fahrplan – Durchlauf 37"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 37

Quelle: Fortsetzung ZR-016 mit Fokus auf Prozesshygiene und anschlussfähige
Übersicht nach den inhaltlichen SSOT-Durchläufen.

## Ziel

Die Meta-Ebene so aufräumen, dass der nächste Durchlauf ohne Sucharbeit starten
kann: kompakte Statussicht auf Issue 1–13, klare Referenz in `known-issues.md`,
keine unlesbaren Monster-Listen mehr.

## Scope dieses Durchlaufs

- `internal/qa/process/issue-pack-statusmatrix.md` (neu)
- `internal/qa/process/known-issues.md` (Refactoring der ZR-016-Notiz)
- QA-Nachführung: Plan + Log

## Nicht im Scope

- Neue Runtime-Regeländerungen in WS-Modulen.
- Erweiterung von Lint-Checks in `tools/lint_runtime.py`.
- Umstellung des Status ZR-016 auf `abgeschlossen` ohne separaten Closure-
  Entscheid.

## Exit-Kriterium für Durchlauf 37

- ZR-016 hat eine kompakte, gepflegte Referenz auf die neue Statusmatrix.
- Matrix deckt alle 13 Issues mit Status + Evidenzpfaden ab.
- `bash scripts/smoke.sh` läuft vollständig grün.
