---
title: "Issue-Pack Durchlauf 137 – Onboarding-Start/HQ-Contract als Watchguard absichern"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_start_mmo_onboarding_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-136-readme-landingpage-onboarding-sharpening.md"
---

# Ziel

Die in Durchlauf 131-136 harmonisierten Start-/HQ-Onboarding-Regeln gegen
Regression absichern: natürliche Sprache als Startoberfläche, `klassisch` als
Default, `generate/custom generate/manuell` als primäre Charakterentscheidung
sowie `HQ -> !save -> neuer Chat empfohlen` ohne Auto-Briefing-Druck.

# Checkliste

- [x] Neuer Smoke-Watchguard für Start-/HQ-Onboarding-Kontrakt ergänzt.
- [x] Guard prüft Startanker in `masterprompt`, `toolkit`, `sl-referenz`, `spieler-handbuch`.
- [x] Guard prüft Save-/Chatwechsel-Anker in `masterprompt`, `toolkit`, `sl-referenz`, `speicher-fortsetzung`.
- [x] Guard in `scripts/smoke.sh` als Pflichtcheck eingebunden.
- [x] Prozessspur in `internal/qa/process/known-issues.md` um Durchlauf 137 ergänzt.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) erfolgreich.

# Abschluss

Durchlauf 137 ergänzt die fehlende Automationsschicht über dem bereits
korrigierten Onboarding-Vertrag. Künftige Driftfälle (z. B. Rückfall auf
command-first Start oder Auto-Briefing nach HQ) werden jetzt früh im Pflicht-
Smoke abgefangen.
