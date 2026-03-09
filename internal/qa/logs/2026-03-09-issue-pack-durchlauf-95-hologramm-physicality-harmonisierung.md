---
title: "QA-Log 2026-03-09 – Durchlauf 95 (Hologramm/Physicality-Harmonisierung)"
status: "abgeschlossen"
run_id: "zr-019-d95"
---

# Kontext

Reviewer-Feedback zu Durchlauf 94: Das Entfernen von Hologramm-Wording war im
Kern richtig (kein Handgelenk-/disembodied HUD), wirkte aber stellenweise zu
hart und schwächte HQ-Tech-Noir-Flair. Ziel war die Präzisierung statt Verbot.

# Umgesetzte Änderungen

1. **Toolkit-Physicality präzisiert**
   - `systems/toolkit-gpt-spielleiter.md`
   - Feste HQ-Projektionen (Wand/Tisch/Briefing-Glas) als erlaubt markiert,
     wenn das Gerät benannt wird.
   - Verbot auf den eigentlichen Problemfall fokussiert:
     keine losgelösten VR-Räume und kein Handgelenk-Projektor-Default.

2. **SL-Referenz harmonisiert**
   - `core/sl-referenz.md`
   - Hardwareprinzip von „externe Projektoren gibt es nicht“ zu
     „mobile Handgelenk-Projektoren sind kein HUD-Default; feste Inworld-
     Projektoren im HQ sind erlaubt“ umgestellt.

3. **Cinematic-Wording nachgezogen**
   - `systems/gameflow/cinematic-start.md`
   - Solo-/HQ-Begriffe auf „Lichtbilder/HUD-Hologramme“ bzw.
     „Lichtbilder/Hologramm-Projektionen“ harmonisiert.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

# Bewertung

Der Flavour bleibt futuristisch-technoir, ohne den Physicality-Gate zu brechen:
Chrononauten sehen MR-HUD über Linse, und HQ-Projektionen bleiben als
sichtbare, gerätegebundene Weltinszenierung verfügbar.
