---
title: "Issue-Pack Durchlauf 138 – Archetypen/Pregens als Fallback im Runtime-Pfad verankern"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_start_mmo_onboarding_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-137-onboarding-watchguard-automation.md"
---

# Ziel

Den verbliebenen Restpunkt aus dem Start/MMO-Review schließen: Archetypen und
Pregens bleiben als hilfreiches Material verfügbar, sollen aber im
Runtime-Standardstart nicht mehr wie ein gleichrangiger Primärpfad wirken.

# Checkliste

- [x] `characters/charaktererschaffung-optionen.md` als Inspirations-/Fallback-Modul geschärft.
- [x] Runtime-Hinweis bei Pregens auf optionales Fallback und Kampagnenstandard (`generate/custom generate/manuell`) präzisiert.
- [x] `master-index.json`-Eintrag für `chars-options` auf Inspirations-/Fallback-Charakter umbenannt und Priorität als `soll` markiert.
- [x] Onboarding-Watchguard um Archetypen-/Fallback-Anker erweitert.
- [x] Prozessspur in `internal/qa/process/known-issues.md` um Durchlauf 138 ergänzt.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) erfolgreich.

# Abschluss

Durchlauf 138 reduziert den verbleibenden Oldschool-Druck im Startpfad ohne
Regelverlust: Archetypen/Pregens bleiben vorhanden, sind aber klar als
sekundärer Einstiegspfad markiert; der Kampagnenstandard bleibt
`klassisch + generate/custom generate/manuell`.
