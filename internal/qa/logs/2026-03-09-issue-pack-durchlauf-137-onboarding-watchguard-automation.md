---
title: "QA-Log 2026-03-09 – Durchlauf 137 (Onboarding Watchguard Automation)"
status: "abgeschlossen"
run_id: "zr-021-d137"
---

# Kontext

Die Durchläufe 131-136 haben den Start-/Load-/HQ-Vertrag bereits in den
Runtime-Texten harmonisiert. Bisher fehlte dafür jedoch ein dedizierter
Regression-Guard im Smoke, der den Kontrakt bei späteren Textanpassungen
maschinell absichert.

# Umgesetzte Änderungen

1. **Neuer Start/HQ-Onboarding-Watchguard**
   - `tools/test_onboarding_start_save_watchguard.js` prüft den
     Startvertrag über `meta/masterprompt_v6.md`,
     `systems/toolkit-gpt-spielleiter.md`, `core/sl-referenz.md` und
     `core/spieler-handbuch.md` (Anker: natürliche Sprache,
     `klassisch` als Default, `generate/custom generate/manuell`).
   - Der gleiche Guard prüft HQ-Save-Disziplin über
     `meta/masterprompt_v6.md`, `systems/toolkit-gpt-spielleiter.md`,
     `core/sl-referenz.md`, `systems/gameflow/speicher-fortsetzung.md`
     (Anker: Deepsave-Hinweis, kein Auto-Briefing-Druck,
     Chatwechsel-Empfehlung).

2. **Pflicht-Smoke erweitert**
   - `scripts/smoke.sh` führt den neuen Guard aus und erwartet den
     Erfolgstoken `onboarding-start-save-watchguard-ok`.

3. **Prozessspur fortgeführt**
   - `internal/qa/process/known-issues.md` ergänzt Durchlauf 137 als
     Anschlusslauf in der ZR-020-Kette.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
2. `python3 tools/lint_links.py internal/qa/plans/issue-pack-durchlauf-137-onboarding-watchguard-automation.md internal/qa/logs/2026-03-09-issue-pack-durchlauf-137-onboarding-watchguard-automation.md internal/qa/process/known-issues.md`

# Bewertung

Der Onboarding-Vertrag ist nun nicht nur inhaltlich harmonisiert, sondern auch
automatisiert überwacht. Das reduziert Rückfallrisiken bei künftigen
Text-Refactorings und macht Folge-Durchläufe besser anschlussfähig.
