---
title: "Issue-Pack Durchlauf 134 – Masterprompt BEREIT-Block auf Startvertrag harmonisieren"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_start_mmo_onboarding_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-133-hq-menu-autobriefing-restfix.md"
---

# Ziel

Den letzten sichtbaren Onboarding-Restdrift im Masterprompt schließen: Der
Abschlussblock `## BEREIT` soll nicht mehr primär `solo/gruppe schnell`
aufrufen, sondern den bereits etablierten Vertrag abbilden
(natürliche Sprache akzeptieren, `solo klassisch` als Standard,
`generate/custom generate/manuell` als erste Charakterentscheidung,
`solo schnell` nur als Fast-Lane).

# Checkliste

- [x] Restdrift im `## BEREIT`-Block von `meta/masterprompt_v6.md` identifiziert.
- [x] Abschlussblock auf den kanonischen Start-/Load-Vertrag umgestellt.
- [x] Fast-Lane (`solo schnell`) als optionaler, expliziter Wunsch markiert.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) erfolgreich.

# Abschluss

Durchlauf 134 schließt den letzten prominenten Startvertrag-Widerspruch im
Masterprompt-Endblock. Die Spielerführung am Prompt-Ende ist jetzt konsistent
zum Dispatcher-/Toolkit-/Handbuch-Pfad aus den Durchläufen 131–133.
