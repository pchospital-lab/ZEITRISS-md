---
title: "Issue-Pack Durchlauf 135 – Setup-Script/Guide auf kanonischen Onboarding-Vertrag ziehen"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_start_mmo_onboarding_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-134-masterprompt-bereit-startvertrag-restfix.md"
---

# Ziel

Den verbliebenen Onboarding-Drift zwischen Setup-Guide und Setup-Script
abschließen: Sonnet 4.6 als Script-Default konsistent zeigen und den
Start-Hinweis auf `solo klassisch` + natürliche Sprache harmonisieren
(statt Fast-Lane-first).

# Checkliste

- [x] Setup-Guide-Text zum Script-Default auf Sonnet 4.6 harmonisiert.
- [x] Vorschlags-Prompts im Setup-Script auf kanonischen Startpfad ausgerichtet.
- [x] Script-Abschlusshinweis auf `Spiel starten (solo klassisch)` umgestellt.
- [x] Prozessspur in `known-issues.md` um Durchlauf 135 ergänzt.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) erfolgreich.

# Abschluss

Durchlauf 135 entfernt den verbliebenen Einstiegskonflikt im Operator-Pfad:
Script, Setup-Guide und Runtime-Contract zeigen jetzt denselben Startstandard
(`klassisch` zuerst, natürliche Sprache erlaubt, Fast-Lane nicht mehr
hervorgehoben).
