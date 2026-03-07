---
title: "QA-Log – Issue-Pack Durchlauf 23"
date: 2026-03-07
scope: "Maintainer-Feedback: Gender-Syntax entfernen + PP/HQ-Kleinigkeit"
status: abgeschlossen
tags: [qa, log]
---

## Quelle
- Direktes Maintainer-Feedback auf den vorherigen Durchlauf:
  - keine Gender-Syntax im Datensatz,
  - kleine Präzisierung zum Debrief-Recap (`PP` im HQ-Kontext nicht nötig).

## Umsetzung in diesem Durchlauf

1. **Runtime-Text nachgezogen (`systems/gameflow/cinematic-start.md`)**
   - Gender-Syntaxformen ersetzt (`Spieler\*innen`, `Spielleiter\*innen`,
     `Agent*in`, `der/die`, `jede/r` → klare einfache Formen).
   - Debrief-Recap bei Belastung von `LP/SYS/PP-Zustand` auf
     `LP/SYS-Zustand` präzisiert.

2. **Drift-Guard ergänzt (`tools/lint_runtime.py`)**
   - Neue Prüfung `check_forbidden_gender_syntax_in_runtime()` scannt
     Runtime-Markdown auf `\w\*innen`, `\w:in(nen)`, `der/die`, `jede/r`.
   - Check in `main()` eingebunden, damit die Guardrails im Pflicht-Smoke
     automatisch mitlaufen.

3. **QA-Nachführung**
   - Fahrplan/Log für Durchlauf 23 ergänzt.
   - `internal/qa/process/known-issues.md` (ZR-016) um Durchlauf 23 erweitert.

## Checks
- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
