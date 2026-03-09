---
title: "Issue-Pack Durchlauf 128 – ITI-Alias-Drift im Runtime-Stub bereinigen"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_ITI_mmo_konsistenz_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-127-iti-ssot-verankerung-referenz-uebersicht.md"
---

# Ziel

Die verbliebene ITI-Ortsdrift im Entwickler-Stub (`internal/runtime`) entfernen,
damit auch Dev-Routerbeispiele denselben Hauskanon verwenden wie die aktiven
Runtime-Slots (8 Hauptorte + Alias-Bridge als Unterzonen).

# Checkliste

- [x] Restdrift per Repo-Scan validiert (Alt-Hauptorte `Gatehall`, `Research-Wing`, `Mission-Briefing-Pod` in `internal/runtime/runtime-stub-routing-layer.md`).
- [x] Router-Map auf kanonische ITI-Hauptorte (`Quarzatrium`, `Kodex-Archiv`, `Med-Lab`, `Operations-Deck`, `Quartiere`, `Hangar-Axis`, `Zero Time Lounge`, `Pre-City-Hub`) umgestellt.
- [x] Alias-Bridge im Stub erhalten (z. B. `gatehall`, `research-wing`, `mission-briefing-pod` als Alias statt Hauptort).
- [x] Router-Beispiel/Types (`room_id`) auf kanonischen Zielraum angepasst.
- [x] QA-Log für Durchlauf 128 angelegt.
- [x] `bash scripts/smoke.sh` erfolgreich ausgeführt.
- [x] `python3 tools/lint_links.py internal/qa/plans internal/qa/logs internal/qa/process` erfolgreich ausgeführt.

# Abschluss

Durchlauf 128 schließt die letzte gefundene ITI-Ortsdrift im Dev-Stubscope.
Dadurch erzeugen auch interne Routing-Snippets künftig keine konkurrierenden
HQ-Hauptorte mehr und stützen den etablierten Runtime-SSOT.
