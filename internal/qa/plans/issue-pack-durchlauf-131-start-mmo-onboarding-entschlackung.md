---
title: "Issue-Pack Durchlauf 131 – Start/MMO-Onboarding-Entschlackung"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_start_mmo_onboarding_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-130-abschluss-vor-deepscan.md"
---

# Ziel

Die im DeepSearch-Nachcheck benannten Start-/Onboarding-Bremsen in den
Runtime-SSOT-Modulen entschlacken: natürliche Sprache am Einstieg akzeptieren,
`klassisch + generate` als Standard verankern, HQ-Flow stärker auf
`Save -> neuer Chat` ausrichten und README/Setup auf denselben Erstpfad
harmonisieren.

# Checkliste

- [x] Startvertrag in Masterprompt, SL-Referenz, Toolkit und Spieler-Handbuch auf natürliche Sprache + kanonische Kurzform harmonisiert.
- [x] Klassisch-Default + `generate/custom generate/manuell` als primäre Startfrage im SSOT-Startpfad verankert.
- [x] Schnellstart als Fast-Lane (expliziter Wunsch) sprachlich zurückgestuft.
- [x] HQ-Workflow im Toolkit um expliziten Save-Hinweis + „kein Auto-Weiter ins Briefing“-Regel ergänzt.
- [x] Archetypen/Pregens in `characters/charaktererschaffung-optionen.md` als Inspirations-/One-Shot-Material klar markiert.
- [x] README + Setup-Guide auf denselben kanonischen Erstpfad (`solo klassisch` oder klarer natürlicher Neustartwunsch) nachgezogen.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) erfolgreich.
- [x] Linklint für geänderte Doku-/QA-Pfade erfolgreich.

# Abschluss

Durchlauf 131 zieht die Onboarding-Hierarchie auf KI-first: weniger
Command-Pflicht, klarerer Standardpfad, konsistenter HQ-Save-Rhythmus und
synchronisierte Einstiegstexte. Der Anschlusslauf kann direkt auf inhaltliche
Feinpolitur (z. B. verbleibende Modell-/Script-Drifts) aufsetzen.
