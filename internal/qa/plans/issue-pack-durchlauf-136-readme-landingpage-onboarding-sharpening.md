---
title: "Issue-Pack Durchlauf 136 – README-Landingpage auf MMO/Save-Promise schärfen"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_start_mmo_onboarding_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-135-setup-script-onboarding-alignment.md"
---

# Ziel

Den verbleibenden Produkt-UX-Drift in der GitHub-Landingpage schließen:
README-Topblock stärker auf das Kernversprechen (MMO ohne Server, Save =
Charakter, direkt mit KI-SL sprechen) ausrichten und verbleibende
Operator-Altformulierung zum Modell-Default harmonisieren.

# Checkliste

- [x] README-Topblock auf Produktversprechen statt Ops-Reihenfolge geschärft.
- [x] Startstandard im Topblock konsistent als `solo klassisch` + natürliche Sprache geführt.
- [x] Quickstart-Abschnitt auf "In 3-5 Minuten" harmonisiert.
- [x] Hosting-Modell-Abschnitt ohne DeepSeek-Default-Restdrift (Referenzmodell Sonnet 4.6).
- [x] Prozessspur in `known-issues.md` um Durchlauf 136 ergänzt.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) erfolgreich.

# Abschluss

Durchlauf 136 schärft die erste Bildschirmhöhe der README als
Produkt-Landingpage und beseitigt den verbleibenden Modell-/Onboarding-Drift.
Die zentrale Erwartung ist jetzt konsistent: MMO ohne Server, Save als
Charakter, klassischer Kampagnenstart als Default, natürliche Sprache als
player-facing Oberfläche.
