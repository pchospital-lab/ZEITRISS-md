---
title: "QA-Log – Issue-Pack Durchlauf 06"
version: 0.1.0
tags: [qa, log]
---

# QA-Log – Issue-Pack Durchlauf 06

## Kontext
- Input: `uploads/ZEITRISS_codex_issue_pack.md`
- Fokus: Issue 6 (Drift-Tests gegen SSOT-Drift, Teil 1).

## Umgesetzter Scope

1. **SSOT-Drift-Guard für verbotene Begriffe ergänzt**
   - In `tools/lint_runtime.py` wurde der neue Check
     `check_forbidden_terms_in_ssot()` ergänzt.
   - Der Check validiert die drei SSOT-Dateien
     `core/spieler-handbuch.md`, `core/sl-referenz.md` und
     `meta/masterprompt_v6.md`.

2. **CI-Fail bei Rückfall auf Legacy-Begriffe verankert**
   - Die Muster `\bGPT\b` und `\bRecruit\b` werden in den SSOT-Dateien
     explizit als verbotene Begriffe geprüft.
   - Der Check ist in `main()` eingebunden und läuft damit automatisch im
     Pflichtpfad `bash scripts/smoke.sh`.

## QA-Checks
- Pflichtcheck: `bash scripts/smoke.sh`.

## Offene Restpunkte (nächster Durchlauf)
1. Zusätzliche Drift-Regeln für weitere Legacy-Tokens evaluieren
   (z. B. `arc_dashboard`, `economy.cu`) und nur dort scharf schalten,
   wo sie im Zielabschnitt tatsächlich verboten sind.
2. Compliance-Reste in `runtime.js` separat als kompatibilitätsbewussten
   Umbau planen (inkl. Migrations-/Load-Absicherung).

## Status
- Durchlauf 06: **abgeschlossen**.
