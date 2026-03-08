---
title: "QA-Log 2026-03-08 – Durchlauf 86 (WS-Session-Anker-Restdrift)"
status: "abgeschlossen"
run_id: "zr-018-d86"
---

# Kontext

Nach den Durchläufen 81–85 waren SSOT, Fixtures und Guards auf Session-Anker
umgestellt. In `core/spieler-handbuch.md` und `core/zeitriss-core.md` standen
jedoch noch mehrere Host-Formulierungen, die beim Lesen eine alte Merge-
Philosophie suggerierten.

# Umgesetzte Änderungen

1. **WS-Konsolidierung im Spieler-Handbuch**
   - `core/spieler-handbuch.md`
   - Gruppen-Px-Text auf Session-Anker + persönliche Charakterfortschritte
     umgestellt.
   - Multi-Load-Regelblock von Host-Regel auf Session-Anker-Regel
     umformuliert.
   - Fahrzeug-/Gruppen- und Rift-Seed-Passagen von Host auf Session-Anker
     harmonisiert.

2. **WS-Konsolidierung im Core-Modul**
   - `core/zeitriss-core.md`
   - Save-Erläuterung: `characters[]`-Index 0 von Host auf Session-Anker
     umgestellt.
   - Gruppen-Spielstände als Session-Anker-Einstieg + persönliche Wahrheit pro
     Charakter-ID beschrieben.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core systems meta/masterprompt_v6.md README.md internal/qa/plans internal/qa/logs`
   - Ergebnis: **grün**

# Bewertung

Die WS-Spielertexte sind jetzt terminologisch und semantisch konsistent mit dem
Kontinuitäts-Redesign: Session-Anker setzt den Einstiegspunkt, persönliche
Charakterstände bleiben führend, und Mehrfach-Load wird als Kontinuitäts-
Synthese verstanden.
