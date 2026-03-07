---
title: "QA-Log – Issue-Pack Durchlauf 31"
date: 2026-03-07
scope: "Save-Modul Restdrift (v6-Exportformulierungen) + Guard"
status: abgeschlossen
tags: [qa, log]
---

## Quelle

- ZR-016 (externer Codex-Issue-Pack), Restdrift nach Durchlauf 30:
  - `speicher-fortsetzung.md` enthielt weiterhin widersprüchliche Formulierungen,
    die v6 als aktiven Save-Standard erscheinen ließen.

## Umsetzung in diesem Durchlauf

1. **Save-Wording konsolidiert (`systems/gameflow/speicher-fortsetzung.md`)**
   - Accessibility-Hinweis von „Aktuelle Saves (v6)" auf v7 korrigiert.
   - Abschnitt „Single Source" auf „Save v7" umgestellt und Legacy-Felder
     explizit als Importpfad markiert.
   - E2E-Trace-Ökonomiereferenz auf `economy{hq_pool}` + Wallet-Summen gezogen.
   - Timeline-Hinweis auf `arc.timeline[]` als kanonischen Pfad umgestellt;
     `arc_dashboard.timeline[]` nur noch als Legacy-Mapping benannt.

2. **Drift-Guard ergänzt (`tools/lint_runtime.py`)**
   - Neue Prüfung `check_no_v6_export_claims_in_save_module()` eingeführt.
   - Check validiert, dass im Save-Modul keine v6-Exportbehauptungen mehr stehen
     (`Aktuelle Saves (v6)`, `Single Source "Save v6"`,
     `neue Saves entstehen ausschließlich im v6-Format`).
   - Check in `main()` eingebunden (läuft automatisch im Pflicht-Smoke).

## Checks

- Pflichtcheck ausgeführt: `bash scripts/smoke.sh`.
- Ergebnis: **grün**.
