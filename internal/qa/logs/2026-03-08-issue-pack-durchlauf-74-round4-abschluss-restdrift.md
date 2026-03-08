---
title: "QA-Log 2026-03-08 – Durchlauf 74 (Round4 Abschluss-Restdrift)"
status: "abgeschlossen"
run_id: "zr-018-d74"
---

# Kontext

Anschlusslauf nach Durchlauf 73, um zwei verbleibende Inkonsistenzen aus dem
Round-4-Cluster zu schließen (Voice-Default im Core-Beispiel und
Semver-Wording im Toolkit-Dispatcher).

# Umgesetzte Änderungen (Kern)

1. **Voice-SSOT im Kernmodul nachgezogen**
   - `core/zeitriss-core.md`: v7-Beispiel-`ui.voice_profile` von
     `gm_third_person` auf `gm_second_person` gesetzt.

2. **Save-Semver-Wording im Toolkit harmonisiert**
   - `systems/toolkit-gpt-spielleiter.md`: Dispatcher-Hinweis von
     `zr_version` auf kanonisches `zr` umgestellt und Legacy-Normalisierung
     (`zr_version` vorab normalisieren) explizit ergänzt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py core characters gameplay systems meta/masterprompt_v6.md README.md`
   - Ergebnis: **grün**

# Bewertung

- Kein verbleibender Voice-Default-Drift im v7-Kernbeispiel.
- Save-Dispatcher-Formulierung verweist jetzt auf denselben Semver-Pfad wie
  Masterprompt/SL-Referenz/Speicherdoku.
