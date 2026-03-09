---
title: "QA-Log 2026-03-09 – Durchlauf 138 (Archetypen/Pregens Runtime-Demotion)"
status: "abgeschlossen"
run_id: "zr-021-d138"
---

# Kontext

Nach den Durchläufen 131-137 war der Start-/Load-/HQ-Vertrag harmonisiert und
über einen Smoke-Watchguard abgesichert. Ein Restpunkt aus dem Onboarding-
Review blieb offen: Archetypen/Pregens waren zwar bereits relativiert, standen
im Index und im Modul aber noch nicht deutlich genug als sekundärer
Fallback-Pfad.

# Umgesetzte Änderungen

1. **Charaktermodul stärker als Fallback markiert**
   - `characters/charaktererschaffung-optionen.md`
     - Titel auf Inspirations-/Fallback-Fokus geschärft.
     - Prioritätsabschnitt explizit auf "nicht bevorzugter Runtime-Pfad" präzisiert.
     - Pregens-Block um klaren Runtime-Hinweis ergänzt
       (`generate/custom generate/manuell` zuerst; Pregens optionales Fallback).

2. **Index-Priorisierung nachgezogen**
   - `master-index.json`
     - `chars-options` Titel auf "Inspiration & Fallback-Archetypen" umgestellt.
     - `level: "soll"` ergänzt, um den nicht-primären Einstiegspfad auch im
       Steuerungsindex sichtbar zu machen.

3. **Regression-Guard erweitert**
   - `tools/test_onboarding_start_save_watchguard.js` prüft jetzt zusätzlich:
     - Fallback-Formulierung im Archetypenmodul.
     - Kampagnenstandard `generate/custom generate/manuell` im Archetypenmodul.
     - Inspirations-/Fallback-Charakter des `chars-options`-Titels im `master-index.json`.

4. **Prozessspur fortgeführt**
   - `internal/qa/process/known-issues.md` um Durchlauf 138 ergänzt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans/issue-pack-durchlauf-138-archetypen-runtime-prioritaet-demotion.md internal/qa/logs/2026-03-09-issue-pack-durchlauf-138-archetypen-runtime-prioritaet-demotion.md internal/qa/process/known-issues.md`

# Bewertung

Der offene Restpunkt ist geschlossen: Archetypen/Pregens bleiben verfügbar,
werden im Runtime-Onboarding aber eindeutig als Inspiration/Fallback statt als
Default-Startbahn geführt. Gleichzeitig schützt der erweiterte Watchguard den
Status gegen Regressionen.
