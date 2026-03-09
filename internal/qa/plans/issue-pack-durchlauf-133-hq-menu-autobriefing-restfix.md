---
title: "Issue-Pack Durchlauf 133 – HQ-Menü Restfix ohne Auto-Briefing"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-09"
links:
  issue: "uploads/ZEITRISS_start_mmo_onboarding_review.md"
  previous_run: "internal/qa/plans/issue-pack-durchlauf-132-host-anchor-json-first-split-offer.md"
---

# Ziel

Den verbliebenen Drift in der SL-Referenz schließen: Die HQ-Menü-Option 3 darf
kein automatisches Weiterleiten ins nächste Briefing mehr suggerieren, sondern
muss den Save-Contract (`!save`, neuer Chat empfohlen) widerspruchsfrei abbilden.

# Checkliste

- [x] Restdrift in `core/sl-referenz.md` identifiziert (`Auto-HQ & Save` mit Auto-Briefing).
- [x] HQ-Menü-Option 3 auf `Auto-HQ -> Save anbieten` ohne Auto-Briefing umgestellt.
- [x] Nachsatz im HQ-Abschnitt auf explizite Folgeentscheidung (HQ bleiben/speichern/weiter) gehärtet.
- [x] Pflicht-Smoke (`bash scripts/smoke.sh`) erfolgreich.

# Abschluss

Durchlauf 133 harmonisiert den letzten sichtbaren HQ-Menü-Widerspruch im
Start/MMO-Onboarding-Strang: Auto-HQ endet jetzt konsistent mit Save-Angebot
und bewusstem Folgeschritt statt implizitem Briefing-Autoband.
