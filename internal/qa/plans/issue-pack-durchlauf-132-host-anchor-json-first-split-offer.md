---
title: "Issue-Pack Durchlauf 132 – Host-Anker/JSON-First + Debrief-Split-Angebot"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_start_mmo_onboarding_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-131-start-mmo-onboarding-entschlackung.md"
---

# Ziel

Den praktischen Gruppen-Flow explizit im SSOT fixieren: Mehrfach-Load ohne
`Spiel laden` (mehrere JSONs in der ersten Nachricht), Host-/Session-Anker über
Chatreihenfolge (`first JSON wins`) und ein klares Split-Angebot nach
Debrief+HQ-Heimkehr.

# Checkliste

- [x] Toolkit-Dispatcher auf JSON-first ohne Pflichtkommando geschärft.
- [x] Session-Ankerregel für Mehrfach-JSON explizit als Reihenfolge-Regel verankert.
- [x] Debrief→HQ-Split-Angebot im Runtime-Flow ergänzt (kein Auto-Weiterdruck).
- [x] Masterprompt/SL-Referenz/Handbuch/Speichermodul parallel nachgezogen.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) erfolgreich.

# Abschluss

Durchlauf 132 schließt den Praxisdrift nach Lauf 131: Gruppen können direkt
JSON-first joinen/mergen, der Session-Anker bleibt deterministisch über
Chatreihenfolge stabil, und der Debrief endet mit einem klaren Split-/Weiterpfad
für anschlussfähige Gruppenwechsel.
